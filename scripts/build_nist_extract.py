#!/usr/bin/env python3
"""
Build data/nist/sp800-53-rev5.json: NIST SP 800-53 Rev 5 as OSA uses it.

One file holds what NIST says about every control and enhancement: name,
statement, discussion, related controls, baselines, and whether it was
withdrawn and into what. The control files, the control manifest and the
control names inside the patterns are kept in step with it by sync_nist.py,
so each of those facts has one source.

It is built from three things NIST publishes, all for the same release:

  1. the CPRT export, which carries the text as NIST renders it, with
     assignments and selections written out;
  2. the OSCAL catalogue, which carries the titles in title case;
  3. the four OSCAL baseline profiles (low, moderate, high, privacy).

Where two of them state the same fact they are compared, and the build stops
if they disagree on a baseline. Differences in text are counted and listed in
the extract under "checks".

Usage:
    python3 scripts/build_nist_extract.py --fetch   # download NIST's files, then build
    python3 scripts/build_nist_extract.py           # build from the copies already downloaded

The downloads are kept in .nist-sources/ at the top of the repository, which
git ignores. They are about 25 MB.
"""

import hashlib
import html
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "data" / "nist" / "sp800-53-rev5.json"
CACHE = REPO / ".nist-sources"
RELEASE = "5.2.0"
OSCAL_BASE = "https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/"
BASELINES = ("low", "moderate", "high", "privacy")
# name of the local copy: where NIST publishes it
SOURCES = {
    "cprt.json": "https://csrc.nist.gov/extensions/nudp/services/json/nudp/framework/version/sp_800_53_5_2_0/export/json?element=all",
    "catalog.json": OSCAL_BASE + "NIST_SP-800-53_rev5_catalog.json",
    "baseline-low.json": OSCAL_BASE + "NIST_SP-800-53_rev5_LOW-baseline_profile.json",
    "baseline-moderate.json": OSCAL_BASE + "NIST_SP-800-53_rev5_MODERATE-baseline_profile.json",
    "baseline-high.json": OSCAL_BASE + "NIST_SP-800-53_rev5_HIGH-baseline_profile.json",
    "baseline-privacy.json": OSCAL_BASE + "NIST_SP-800-53_rev5_PRIVACY-baseline_profile.json",
}
CPRT_BASELINE = {"SB-Low": "low", "SB-Moderate": "moderate", "SB-High": "high", "PB-Yes": "privacy"}


def fetch():
    CACHE.mkdir(exist_ok=True)
    for name, url in SOURCES.items():
        request = urllib.request.Request(url, headers={"User-Agent": "osa-data build_nist_extract"})
        with urllib.request.urlopen(request, timeout=180) as response:
            (CACHE / name).write_bytes(response.read())
        print(f"fetched {name}: {(CACHE / name).stat().st_size // 1024} KB")


def source(name):
    path = CACHE / name
    if not path.is_file():
        raise SystemExit(f"{path.relative_to(REPO)} is not there. Run with --fetch, or download it from {SOURCES[name]}")
    return path


def read(name):
    return json.loads(source(name).read_text(encoding="utf-8"))


def sha256(name):
    return hashlib.sha256(source(name).read_bytes()).hexdigest()


def one_line(text):
    return " ".join((text or "").split())


def link_text(match):
    """A link to an outside document is one of NIST's reference keys, which the
    publication prints in square brackets: [PRIVACT]. A link to another
    control is left as its text."""
    return "[%s]" % match.group(2) if 'href="http' in match.group(1) else match.group(2)


def plain(text):
    """Discussion text in the export is HTML."""
    text = (text or "").replace("</p>", " ")
    text = re.sub(r"<a\b([^>]*)>([^<]*)</a>", link_text, text)
    text = re.sub(r"</?q>", '"', text)
    text = re.sub(r"<[^>]*>", "", text)
    return one_line(html.unescape(text))


def osa_id(oscal_id):
    """ac-2 to AC-02, ac-2.1 to AC-02(01)."""
    m = re.match(r"^([a-z]{2})-(\d+)(?:\.(\d+))?$", oscal_id)
    if not m:
        return None
    base = "%s-%02d" % (m.group(1).upper(), int(m.group(2)))
    return base if m.group(3) is None else "%s(%02d)" % (base, int(m.group(3)))


# ---- the CPRT export -------------------------------------------------------

def item_label(depth, title):
    """The publication labels statement items a. then 1. then (a) then (1)."""
    return "%s." % title if depth <= 2 else "(%s)" % title


def item_order(path):
    return [(0, int(p)) if p.isdigit() else (1, p) for p in path]


def statement_items(elements, ids):
    """The export holds each item of a statement as its own element:
    CST-PT-01, CST-PT-01-a, CST-PT-01-a-1."""
    items = {}
    for e in elements:
        if e["element_type"] != "control_statement":
            continue
        m = re.match(r"^CST-([A-Z]{2}-\d{2}(?:\(\d{2}\))?)((?:-[a-z0-9]+)*)$", e["element_identifier"])
        if m and m.group(1) in ids:
            items.setdefault(m.group(1), {})[tuple(p for p in m.group(2).split("-") if p)] = e
    return items


def assemble(items):
    parts = []
    for key in sorted(items, key=item_order):
        text = one_line(items[key]["text"])
        if key:
            parts.append(("%s %s" % (item_label(len(key), items[key]["title"]), text)).strip())
        elif text:
            parts.append(text)
    return " ".join(parts)


def relationships(rows, ids):
    related, baselines = {}, {}
    for r in rows:
        src, dst, kind = r["source_element_identifier"], r["dest_element_identifier"], r["relationship_identifier"]
        if src not in ids:
            continue
        if kind == "related" and dst in ids:
            related.setdefault(src, set()).add(dst)
        elif kind == "projection" and dst in CPRT_BASELINE:
            baselines.setdefault(src, set()).add(CPRT_BASELINE[dst])
    return related, baselines


def load_cprt():
    data = read("cprt.json")["response"]["elements"]
    elements = data["elements"]
    ids = {e["element_identifier"] for e in elements if e["element_type"] in ("control", "control_enhancement")}
    items = statement_items(elements, ids)
    discussion = {e["element_identifier"][2:]: plain(e["text"]) for e in elements if e["element_type"] == "discussion"}
    related, baselines = relationships(data["relationships"], ids)
    controls = {cid: {
        "statement": assemble(items.get(cid, {})),
        "discussion": discussion.get(cid, ""),
        "related": related.get(cid, set()),
        "baselines": baselines.get(cid, set()),
    } for cid in ids}
    return data["documents"][0], controls


# ---- the OSCAL catalogue and profiles --------------------------------------

def render_params(prose, params):
    def one(match):
        p = params.get(match.group(1))
        if p is None:
            return match.group(0)
        if "select" in p:
            head = "Selection (one or more)" if p["select"].get("how-many") == "one-or-more" else "Selection"
            return "[%s: %s]" % (head, "; ".join(render_params(c, params) for c in p["select"].get("choice", [])))
        return "[Assignment: %s]" % render_params(p.get("label", ""), params)
    return re.sub(r"\{\{\s*insert:\s*param,\s*([^}\s]+)\s*\}\}", one, prose or "")


def oscal_statement(part, params):
    out = []
    label = next((p["value"] for p in part.get("props", []) if p.get("name") == "label" and p.get("class") != "sp800-53a"), None)
    prose = render_params(part.get("prose", ""), params)
    if label and part.get("name") == "item":
        out.append(("%s %s" % (label, prose)).strip())
    elif prose:
        out.append(prose)
    out.extend(oscal_statement(child, params) for child in part.get("parts", []) if child.get("name") == "item")
    return one_line(" ".join(out))


def successors(links):
    """A withdrawn control points at a control, an enhancement, a statement
    item (#ac-2_smt.k) or a whole family (#sr). An item is read as its control."""
    targets = [l["href"][1:].split("_")[0] for l in links
               if l.get("rel") in ("incorporated-into", "moved-to") and l.get("href", "").startswith("#")]
    return sorted({osa_id(t) or t.upper() for t in targets})


def catalog_entry(control, params):
    parts = {p["name"]: p for p in control.get("parts", [])}
    links = control.get("links", [])
    status = next((p["value"] for p in control.get("props", []) if p.get("name") == "status"), None)
    return {
        "name": control["title"].strip(),
        "withdrawn": status == "withdrawn",
        "into": successors(links),
        "statement": oscal_statement(parts["statement"], params) if "statement" in parts else "",
        "discussion": one_line(render_params(parts.get("guidance", {}).get("prose", ""), params)),
        "related": {osa_id(l["href"][1:]) for l in links if l.get("rel") == "related" and osa_id(l.get("href", "")[1:])},
    }


def load_catalog():
    doc = read("catalog.json")["catalog"]
    families, out = {}, {}

    def take(control, parent_params):
        params = dict(parent_params, **{p["id"]: p for p in control.get("params", [])})
        out[osa_id(control["id"])] = catalog_entry(control, params)
        for enhancement in control.get("controls", []):
            take(enhancement, params)

    for group in doc["groups"]:
        families[group["id"].upper()] = group["title"]
        for control in group.get("controls", []):
            take(control, {})
    return doc["metadata"], families, out


def load_profiles():
    out = {}
    for name in BASELINES:
        doc = read(f"baseline-{name}.json")["profile"]
        if doc["metadata"]["version"] != RELEASE:
            raise SystemExit(f"the {name} baseline profile is release {doc['metadata']['version']}, not {RELEASE}")
        out[name] = {osa_id(i) for imp in doc["imports"] for inc in imp.get("include-controls", []) for i in inc.get("with-ids", [])}
    return out


# ---- putting them together -------------------------------------------------

def comparable(text):
    """Text with the differences of rendering taken out: OSCAL's links, how a
    control number is padded, and what stands inside a parameter's brackets."""
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("–", "-"), ("—", "-")):
        text = text.replace(a, b)
    text = re.sub(r"\[([^\]\[]*)\]\(#[^)]*\)", r"\1", text)
    previous = None
    while previous != text:
        previous = text
        text = re.sub(r"\[(?:Assignment|Selection)[^\[\]]*\]", "§", text)
    text = re.sub(r"\b([A-Za-z]{2})-0?(\d+)", lambda m: "%s-%d" % (m.group(1), int(m.group(2))), text)
    text = re.sub(r"\(0?(\d+)\)", r"(\1)", text)
    return re.sub(r"[^a-z0-9§]+", " ", text.lower()).strip()


def compare(cid, c, o, checks):
    """Note where the two sources word the same control differently."""
    if comparable(c["statement"]) != comparable(o["statement"]):
        checks["statement_differs"].append(cid)
    if comparable(c["discussion"]) != comparable(o["discussion"]):
        checks["discussion_differs"].append(cid)
    if c["related"] - o["related"]:
        checks["related_only_in_cprt"][cid] = sorted(c["related"] - o["related"])
    if o["related"] - c["related"]:
        checks["related_only_in_catalog"][cid] = sorted(o["related"] - c["related"])


def entry(cid, c, o, profiles, checks):
    in_profiles = {b for b in BASELINES if cid in profiles[b]}
    if c["baselines"] != in_profiles:
        raise SystemExit(f"{cid}: the export has baselines {sorted(c['baselines'])} and the profiles {sorted(in_profiles)}")
    if o["withdrawn"]:
        return {"name": o["name"], "withdrawn": True, "incorporated_into": o["into"]}
    compare(cid, c, o, checks)
    return {
        "name": o["name"],
        "statement": c["statement"],
        "discussion": c["discussion"],
        "related": sorted(c["related"] & o["related"]),
        "baselines": [b for b in BASELINES if b in in_profiles],
    }


def nest(entries):
    """Base controls by id, each with its enhancements."""
    controls = {}
    for cid, item in entries.items():
        if "(" in cid:
            controls[cid.split("(")[0]].setdefault("enhancements", []).append(dict(id=cid, **item))
        else:
            controls[cid] = dict(family=cid.split("-")[0], **item)
    return controls


def counts(controls):
    enhancements = [e for c in controls.values() for e in c.get("enhancements", [])]
    return {
        "controls": sum(1 for c in controls.values() if not c.get("withdrawn")),
        "controls_withdrawn": sum(1 for c in controls.values() if c.get("withdrawn")),
        "enhancements": sum(1 for e in enhancements if not e.get("withdrawn")),
        "enhancements_withdrawn": sum(1 for e in enhancements if e.get("withdrawn")),
        "baselines": {b: sum(1 for c in controls.values() if b in c.get("baselines", [])) for b in BASELINES},
    }


def main():
    if "--fetch" in sys.argv:
        fetch()
    document, cprt = load_cprt()
    metadata, families, oscal = load_catalog()
    profiles = load_profiles()
    if document["version"] != RELEASE or metadata["version"] != RELEASE:
        raise SystemExit(f"expected release {RELEASE}: the export is {document['version']} and the catalogue {metadata['version']}")
    if set(cprt) != set(oscal):
        raise SystemExit(f"the two sources list different controls: {sorted(set(cprt) ^ set(oscal))[:10]}")

    checks = {"statement_differs": [], "discussion_differs": [], "related_only_in_cprt": {}, "related_only_in_catalog": {}}
    controls = nest({cid: entry(cid, cprt[cid], oscal[cid], profiles, checks) for cid in sorted(cprt)})
    extract = {
        "title": "NIST SP 800-53 Rev 5, Release %s, as OSA uses it" % RELEASE,
        "release": RELEASE,
        "built": date.today().isoformat(),
        "note": "Generated by scripts/build_nist_extract.py. Do not edit by hand. NIST's text is in the public domain in the United States.",
        "sources": {name: {"url": url, "sha256": sha256(name)} for name, url in SOURCES.items()},
        "counts": counts(controls),
        "checks": {
            "what": "Where the CPRT export and the OSCAL catalogue state the same thing, they were compared, with differences of rendering set aside. The text here is the export's. Related controls are those both list. The baselines agree for every control and enhancement.",
            **checks,
        },
        "families": families,
        "controls": controls,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(extract, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)}: {OUT.stat().st_size // 1024} KB")
    print("counts:", json.dumps(extract["counts"]))
    print("statement differs between the two sources:", checks["statement_differs"])
    print("discussion differs:", len(checks["discussion_differs"]), "| related only in the export:", len(checks["related_only_in_cprt"]),
          "| only in the catalogue:", len(checks["related_only_in_catalog"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
