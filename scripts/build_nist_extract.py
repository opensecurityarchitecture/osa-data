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
    python3 scripts/build_nist_extract.py --cprt FILE --catalog FILE --profiles DIR

    FILE and DIR are local copies. The addresses are in SOURCES below. The
    profiles are expected as baseline-LOW.json, baseline-MODERATE.json,
    baseline-HIGH.json and baseline-PRIVACY.json.
"""

import argparse
import hashlib
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "data" / "nist" / "sp800-53-rev5.json"
RELEASE = "5.2.0"
OSCAL_BASE = "https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/"
SOURCES = {
    "cprt": "https://csrc.nist.gov/extensions/nudp/services/json/nudp/framework/version/sp_800_53_5_2_0/export/json?element=all",
    "catalog": OSCAL_BASE + "NIST_SP-800-53_rev5_catalog.json",
    "profiles": {name: OSCAL_BASE + f"NIST_SP-800-53_rev5_{name}-baseline_profile.json" for name in ("LOW", "MODERATE", "HIGH", "PRIVACY")},
}
BASELINES = ("low", "moderate", "high", "privacy")
CPRT_BASELINE = {"SB-Low": "low", "SB-Moderate": "moderate", "SB-High": "high", "PB-Yes": "privacy"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def one_line(text):
    return re.sub(r"\s+", " ", text or "").strip()


def plain(text):
    """Discussion text in the export is HTML. A link to an outside document is
    one of NIST's reference keys, which the publication prints in square
    brackets: [PRIVACT]. A link to another control is left as its text."""
    text = re.sub(r"</p>\s*<p[^>]*>", " ", text or "")
    text = re.sub(r'<a\b[^>]*href="https?://[^"]*"[^>]*>(.*?)</a>', r"[\1]", text)
    text = re.sub(r"</?q>", '"', text)
    text = re.sub(r"<[^>]+>", "", text)
    return one_line(html.unescape(text))


def osa_id(oscal_id):
    """ac-2 to AC-02, ac-2.1 to AC-02(01)."""
    m = re.match(r"^([a-z]{2})-(\d+)(?:\.(\d+))?$", oscal_id)
    if not m:
        return None
    base = "%s-%02d" % (m.group(1).upper(), int(m.group(2)))
    return base if m.group(3) is None else "%s(%02d)" % (base, int(m.group(3)))


def item_label(depth, title):
    """The publication labels statement items a. then 1. then (a) then (1)."""
    return "%s." % title if depth <= 2 else "(%s)" % title


def item_order(path):
    return [(0, int(p)) if p.isdigit() else (1, p) for p in path]


def load_cprt(path):
    data = json.load(open(path, encoding="utf-8"))["response"]["elements"]
    document = data["documents"][0]
    elements = data["elements"]
    ids = {e["element_identifier"] for e in elements if e["element_type"] in ("control", "control_enhancement")}
    items = {}
    for e in elements:
        if e["element_type"] != "control_statement":
            continue
        m = re.match(r"^CST-([A-Z]{2}-\d{2}(?:\(\d{2}\))?)((?:-[a-z0-9]+)*)$", e["element_identifier"])
        if m and m.group(1) in ids:
            items.setdefault(m.group(1), {})[tuple(p for p in m.group(2).split("-") if p)] = e
    discussion = {e["element_identifier"][2:]: plain(e["text"]) for e in elements if e["element_type"] == "discussion"}
    related, baselines = {}, {}
    for r in data["relationships"]:
        src, dst, kind = r["source_element_identifier"], r["dest_element_identifier"], r["relationship_identifier"]
        if src not in ids:
            continue
        if kind == "related" and dst in ids:
            related.setdefault(src, set()).add(dst)
        elif kind == "projection" and dst in CPRT_BASELINE:
            baselines.setdefault(src, set()).add(CPRT_BASELINE[dst])
    out = {}
    for cid in ids:
        parts = []
        for key in sorted(items.get(cid, {}), key=item_order):
            e = items[cid][key]
            text = one_line(e["text"])
            if not key:
                if text:
                    parts.append(text)
            else:
                parts.append(("%s %s" % (item_label(len(key), e["title"]), text)).strip())
        out[cid] = {
            "statement": " ".join(parts),
            "discussion": discussion.get(cid, ""),
            "related": related.get(cid, set()),
            "baselines": baselines.get(cid, set()),
        }
    return document, out


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


def load_catalog(path):
    doc = json.load(open(path, encoding="utf-8"))["catalog"]
    families, out = {}, {}

    def take(control, parent_params):
        cid = osa_id(control["id"])
        params = dict(parent_params, **{p["id"]: p for p in control.get("params", [])})
        parts = {p["name"]: p for p in control.get("parts", [])}
        links = control.get("links", [])
        status = next((p["value"] for p in control.get("props", []) if p.get("name") == "status"), None)
        # A withdrawn control points at a control, an enhancement, a statement
        # item (#ac-2_smt.k) or a whole family (#sr). An item is read as its control.
        into = [l["href"][1:].split("_")[0] for l in links if l.get("rel") in ("incorporated-into", "moved-to") and l.get("href", "").startswith("#")]
        out[cid] = {
            "name": control["title"].strip(),
            "withdrawn": status == "withdrawn",
            "into": sorted({osa_id(x) or x.upper() for x in into}),
            "statement": oscal_statement(parts["statement"], params) if "statement" in parts else "",
            "discussion": one_line(render_params(parts.get("guidance", {}).get("prose", ""), params)),
            "related": {osa_id(l["href"][1:]) for l in links if l.get("rel") == "related" and osa_id(l.get("href", "")[1:])},
        }
        for enhancement in control.get("controls", []):
            take(enhancement, params)

    for group in doc["groups"]:
        families[group["id"].upper()] = group["title"]
        for control in group.get("controls", []):
            take(control, {})
    return doc["metadata"], families, out


def load_profiles(directory):
    out = {}
    for name in ("LOW", "MODERATE", "HIGH", "PRIVACY"):
        doc = json.load(open(Path(directory) / f"baseline-{name}.json", encoding="utf-8"))["profile"]
        assert doc["metadata"]["version"] == RELEASE, (name, doc["metadata"]["version"])
        out[name.lower()] = {osa_id(i) for imp in doc["imports"] for inc in imp.get("include-controls", []) for i in inc.get("with-ids", [])}
    return out


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


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--cprt", required=True)
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--profiles", required=True)
    args = parser.parse_args()

    document, cprt = load_cprt(args.cprt)
    metadata, families, oscal = load_catalog(args.catalog)
    profiles = load_profiles(args.profiles)
    assert document["version"] == RELEASE and metadata["version"] == RELEASE, (document["version"], metadata["version"])
    assert set(cprt) == set(oscal), sorted(set(cprt) ^ set(oscal))[:10]

    checks = {"statement_differs": [], "discussion_differs": [], "related_only_in_cprt": {}, "related_only_in_catalog": {}}
    entries = {}
    for cid in sorted(cprt):
        c, o = cprt[cid], oscal[cid]
        in_profiles = {b for b in BASELINES if cid in profiles[b]}
        if c["baselines"] != in_profiles:
            raise SystemExit(f"{cid}: the export has baselines {sorted(c['baselines'])} and the profiles {sorted(in_profiles)}")
        if not o["withdrawn"]:
            if comparable(c["statement"]) != comparable(o["statement"]):
                checks["statement_differs"].append(cid)
            if comparable(c["discussion"]) != comparable(o["discussion"]):
                checks["discussion_differs"].append(cid)
            if c["related"] - o["related"]:
                checks["related_only_in_cprt"][cid] = sorted(c["related"] - o["related"])
            if o["related"] - c["related"]:
                checks["related_only_in_catalog"][cid] = sorted(o["related"] - c["related"])
        entry = {"name": o["name"]}
        if o["withdrawn"]:
            entry["withdrawn"] = True
            entry["incorporated_into"] = o["into"]
        else:
            entry["statement"] = c["statement"]
            entry["discussion"] = c["discussion"]
            entry["related"] = sorted(c["related"] & o["related"])
            entry["baselines"] = [b for b in BASELINES if b in in_profiles]
        entries[cid] = entry

    controls = {}
    for cid, entry in entries.items():
        if "(" in cid:
            controls[cid.split("(")[0]].setdefault("enhancements", []).append(dict(id=cid, **entry))
        else:
            controls[cid] = dict(family=cid.split("-")[0], **entry)

    extract = {
        "title": "NIST SP 800-53 Rev 5, Release %s, as OSA uses it" % RELEASE,
        "release": RELEASE,
        "built": date.today().isoformat(),
        "note": "Generated by scripts/build_nist_extract.py. Do not edit by hand. NIST's text is in the public domain in the United States.",
        "sources": {
            "cprt": {"what": "The text as NIST renders it: statements, discussion, related controls, baselines.", "url": SOURCES["cprt"], "sha256": sha256(args.cprt)},
            "catalog": {"what": "Titles, and whether a control was withdrawn and into what.", "url": SOURCES["catalog"], "sha256": sha256(args.catalog)},
            "profiles": {name: {"url": SOURCES["profiles"][name.upper()], "sha256": sha256(Path(args.profiles) / f"baseline-{name.upper()}.json")} for name in BASELINES},
        },
        "counts": {
            "controls": sum(1 for c in controls.values() if not c.get("withdrawn")),
            "controls_withdrawn": sum(1 for c in controls.values() if c.get("withdrawn")),
            "enhancements": sum(1 for c in controls.values() for e in c.get("enhancements", []) if not e.get("withdrawn")),
            "enhancements_withdrawn": sum(1 for c in controls.values() for e in c.get("enhancements", []) if e.get("withdrawn")),
            "baselines": {b: sum(1 for c in controls.values() if b in c.get("baselines", [])) for b in BASELINES},
        },
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
