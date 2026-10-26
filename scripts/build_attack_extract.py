#!/usr/bin/env python3
"""
Build data/mitre-attack/: MITRE ATT&CK Enterprise as OSA uses it, and CTID's
mapping of NIST SP 800-53 Rev 5 to it.

Two files, each with one source:

  enterprise-attack.json   tactics, techniques and sub-techniques, groups and
                           the techniques MITRE says they use, MITRE's
                           mitigations and detection strategies, from MITRE's
                           own STIX data for ATT&CK Enterprise.
  sp800-53-to-attack.json  the Center for Threat-Informed Defense's mapping of
                           SP 800-53 Rev 5 controls to the techniques they
                           mitigate (Mappings Explorer), carried from the ATT&CK
                           version CTID mapped to the version above.

CTID's newest SP 800-53 mapping is for ATT&CK 16.1. A technique MITRE has since
revoked is replaced by its successor, following MITRE's own revoked-by
relationships, and the pair records the id CTID used. A pair whose technique was
deprecated without a successor, or is missing, is dropped and listed under
"checks". Nothing here is edited by hand: change the source or this script.

Usage:
    python3 scripts/build_attack_extract.py --fetch   # download the sources, then build
    python3 scripts/build_attack_extract.py           # build from the copies already downloaded

The downloads are kept in .attack-sources/ at the top of the repository, which
git ignores. They are about 57 MB.
"""

import collections
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "data" / "mitre-attack"
CACHE = REPO / ".attack-sources"

ATTACK_VERSION = "20.0"
SOURCES = {
    "attack": {
        "name": "MITRE ATT&CK Enterprise, STIX 2.1",
        "version": ATTACK_VERSION,
        "url": "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack-20.0.json",
        "file": "enterprise-attack-20.0.json",
    },
    "ctid": {
        "name": "Center for Threat-Informed Defense, Mappings Explorer: NIST SP 800-53 Rev 5 to ATT&CK 16.1 (Enterprise)",
        "url": "https://raw.githubusercontent.com/center-for-threat-informed-defense/mappings-explorer/main/mappings/nist_800_53/attack-16.1/nist_800_53-rev5/enterprise/nist_800_53-rev5_attack-16.1-enterprise.json",
        "file": "nist_800_53-rev5_attack-16.1-enterprise.json",
        "licence": "Apache-2.0",
        "project": "https://github.com/center-for-threat-informed-defense/mappings-explorer",
    },
}

MITRE_NOTICE = "© 2026 The MITRE Corporation. This work is reproduced and distributed with the permission of The MITRE Corporation."
MITRE_LICENCE = (
    "The MITRE Corporation (MITRE) hereby grants you a non-exclusive, royalty-free license to use ATT&CK® for research, "
    "development, and commercial purposes. Any copy you make for such purposes is authorized provided that you reproduce "
    "MITRE's copyright designation and this license in any such copy."
)
MITRE_TERMS = "https://attack.mitre.org/resources/legal-and-branding/terms-of-use/"


def fetch():
    CACHE.mkdir(exist_ok=True)
    for s in SOURCES.values():
        req = urllib.request.Request(s["url"], headers={"User-Agent": "osa-data-build/1.0"})
        with urllib.request.urlopen(req, timeout=300) as r:
            (CACHE / s["file"]).write_bytes(r.read())
        print("fetched", s["file"])


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ext(o):
    for r in o.get("external_references", []):
        if r.get("source_name") == "mitre-attack":
            return r.get("external_id"), r.get("url")
    return None, None


def first_paragraph(text):
    """MITRE's description up to the first blank line, without its citation markers."""
    p = (text or "").strip().split("\n\n")[0]
    p = re.sub(r"\s*\(Citation:[^)]*\)", "", p)
    return re.sub(r"[ \t]+", " ", p).strip()


def live(o):
    return not o.get("revoked") and not o.get("x_mitre_deprecated")


def tid_key(t):
    head, _, sub = t.partition(".")
    return (int(head[1:]), int(sub or 0))


def build():
    attack_path = CACHE / SOURCES["attack"]["file"]
    ctid_path = CACHE / SOURCES["ctid"]["file"]
    bundle = json.loads(attack_path.read_text())
    objs = bundle["objects"]
    by_id = {o["id"]: o for o in objs}
    rels = [o for o in objs if o["type"] == "relationship" and live(o)]
    revoked_by = {o["source_ref"]: o["target_ref"] for o in objs
                  if o["type"] == "relationship" and o.get("relationship_type") == "revoked-by"}

    # Tactics, in the order of MITRE's Enterprise matrix.
    matrix = next(o for o in objs if o["type"] == "x-mitre-matrix")
    tactics, tactic_by_short = [], {}
    for ref in matrix["tactic_refs"]:
        t = by_id[ref]
        tid, url = ext(t)
        tactic_by_short[t["x_mitre_shortname"]] = tid
        tactics.append({"id": tid, "name": t["name"], "shortname": t["x_mitre_shortname"], "url": url,
                        "description": first_paragraph(t.get("description"))})

    # Techniques and sub-techniques that MITRE has neither revoked nor deprecated.
    patterns = [o for o in objs if o["type"] == "attack-pattern"]
    by_ext = {}
    for o in patterns:
        tid, _ = ext(o)
        if tid:
            by_ext.setdefault(tid, []).append(o)
    parent = {}
    for r in rels:
        if r["relationship_type"] == "subtechnique-of":
            parent[ext(by_id[r["source_ref"]])[0]] = ext(by_id[r["target_ref"]])[0]
    techniques = []
    for o in patterns:
        if not live(o):
            continue
        tid, url = ext(o)
        phases = [p["phase_name"] for p in o.get("kill_chain_phases", []) if p.get("kill_chain_name") == "mitre-attack"]
        techniques.append({
            "id": tid, "name": o["name"],
            "tactics": [tactic_by_short[p] for p in phases],
            "subtechnique_of": parent.get(tid) if o.get("x_mitre_is_subtechnique") else None,
            "platforms": o.get("x_mitre_platforms", []),
            "url": url,
            "description": first_paragraph(o.get("description")),
        })
    techniques.sort(key=lambda t: tid_key(t["id"]))
    live_ids = {t["id"] for t in techniques}
    stix_to_live = {o["id"]: ext(o)[0] for o in patterns if live(o)}

    def targets(source_type, rel_type):
        out = collections.defaultdict(set)
        for r in rels:
            if r["relationship_type"] == rel_type and r["source_ref"].startswith(source_type + "--") and r["target_ref"] in stix_to_live:
                out[r["source_ref"]].add(stix_to_live[r["target_ref"]])
        return out

    def collection(stix_type, rel_type, id_pattern, extra=lambda o: {}):
        used = targets(stix_type, rel_type)
        out = []
        for o in objs:
            if o["type"] != stix_type or not live(o):
                continue
            oid, url = ext(o)
            if not oid or not re.match(id_pattern, oid):
                continue
            out.append({"id": oid, "name": o["name"], **extra(o), "url": url,
                        "techniques": sorted(used.get(o["id"], ()), key=tid_key)})
        return sorted(out, key=lambda x: x["id"])

    groups = collection("intrusion-set", "uses", r"^G\d{4}$", lambda o: {"aliases": [a for a in o.get("aliases", []) if a != o["name"]]})
    mitigations = collection("course-of-action", "mitigates", r"^M\d{4}$")
    detections = collection("x-mitre-detection-strategy", "detects", r"^DET\d{4}$")

    # CTID's mapping, carried to this ATT&CK version.
    ctid = json.loads(ctid_path.read_text())
    meta = ctid["metadata"]

    def resolve(tid):
        cands = by_ext.get(tid)
        if not cands:
            return None, "not in ATT&CK %s" % ATTACK_VERSION
        o = cands[0]
        seen = set()
        while o.get("revoked"):
            if o["id"] in seen or o["id"] not in revoked_by:
                return None, "revoked without a successor"
            seen.add(o["id"])
            o = by_id[revoked_by[o["id"]]]
        if o.get("x_mitre_deprecated"):
            return None, "deprecated"
        return ext(o)[0], None

    pairs, dropped, carried = {}, [], {}
    source_pairs = set()
    non_mappable = []
    for m in ctid["mapping_objects"]:
        t16 = m["attack_object_id"]
        t20, why = resolve(t16)
        if m.get("status") == "non_mappable":
            if t20:
                non_mappable.append({"technique": t20, **({"technique_in_source": t16} if t16 != t20 else {}),
                                     "comment": (m.get("comments") or "").strip()})
            continue
        if m.get("mapping_type") != "mitigates":
            continue
        ctl = m["capability_id"]
        source_pairs.add((ctl, t16))
        if not t20:
            dropped.append({"control": ctl, "technique_in_source": t16, "reason": why})
            continue
        key = (ctl, t20)
        p = pairs.setdefault(key, {"control": ctl, "technique": t20, "mapping_type": "mitigates"})
        if t16 != t20:
            p.setdefault("technique_in_source", [])
            if t16 not in p["technique_in_source"]:
                p["technique_in_source"].append(t16)
            carried[t16] = t20
    pair_list = sorted(pairs.values(), key=lambda p: (p["control"], tid_key(p["technique"])))
    dropped = sorted({json.dumps(d, sort_keys=True) for d in dropped})
    dropped = [json.loads(d) for d in dropped]
    covered = {p["technique"] for p in pair_list}
    kept_source = len(source_pairs) - len({(d["control"], d["technique_in_source"]) for d in dropped})
    nm = {}
    for n in non_mappable:
        nm.setdefault(n["technique"], n)
    non_mappable = sorted(nm.values(), key=lambda n: tid_key(n["technique"]))

    attack_src = {**{k: v for k, v in SOURCES["attack"].items() if k != "file"}, "sha256": sha256(attack_path),
                  "modified": next(o for o in objs if o["type"] == "x-mitre-collection").get("modified")}
    ctid_src = {**{k: v for k, v in SOURCES["ctid"].items() if k != "file"}, "sha256": sha256(ctid_path),
                "attack_version": meta.get("attack_version"), "last_update": meta.get("last_update")}
    marking = next(o for o in objs if o["type"] == "marking-definition").get("definition", {}).get("statement")

    enterprise = {
        "about": "MITRE ATT&CK Enterprise as OSA uses it. Generated by scripts/build_attack_extract.py from MITRE's STIX data. Do not edit.",
        "notice": MITRE_NOTICE,
        "licence": MITRE_LICENCE,
        "terms": MITRE_TERMS,
        "copyright_in_source": marking,
        "source": attack_src,
        "counts": {"tactics": len(tactics), "techniques": sum(1 for t in techniques if not t["subtechnique_of"]),
                   "subtechniques": sum(1 for t in techniques if t["subtechnique_of"]), "groups": len(groups),
                   "mitigations": len(mitigations), "detection_strategies": len(detections)},
        "tactics": tactics,
        "techniques": techniques,
        "groups": groups,
        "mitigations": mitigations,
        "detection_strategies": detections,
    }
    mapping = {
        "about": ("CTID's mapping of NIST SP 800-53 Rev 5 controls to the ATT&CK Enterprise techniques they mitigate, carried "
                  "from ATT&CK %s to %s through MITRE's revoked-by relationships. Generated by "
                  "scripts/build_attack_extract.py. Do not edit." % (meta.get("attack_version"), ATTACK_VERSION)),
        "attack_version": ATTACK_VERSION,
        "source": ctid_src,
        "attack_notice": MITRE_NOTICE,
        "pairs": pair_list,
        "non_mappable": non_mappable,
        "checks": {
            "pairs_in_source": len(source_pairs),
            "pairs_kept": kept_source,
            "share_kept": round(kept_source / len(source_pairs), 4),
            "pairs_after_carrying": len(pair_list),
            "controls": len({p["control"] for p in pair_list}),
            "techniques_carried": dict(sorted(carried.items(), key=lambda kv: tid_key(kv[0]))),
            "dropped": dropped,
            "enterprise_techniques_and_subtechniques": len(live_ids),
            "with_a_control": len(covered & live_ids),
            "share_with_a_control": round(len(covered & live_ids) / len(live_ids), 4),
            "non_mappable": len(non_mappable),
        },
    }
    assert covered <= live_ids
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "enterprise-attack.json").write_text(json.dumps(enterprise, indent=1, ensure_ascii=False) + "\n")
    (OUT / "sp800-53-to-attack.json").write_text(json.dumps(mapping, indent=1, ensure_ascii=False) + "\n")
    c = mapping["checks"]
    print("ATT&CK %s: %s" % (ATTACK_VERSION, json.dumps(enterprise["counts"])))
    print("CTID pairs: %d in source, %d kept (%.1f%%), %d dropped; %d pairs after carrying, over %d controls"
          % (c["pairs_in_source"], c["pairs_kept"], 100 * c["share_kept"], len(dropped), c["pairs_after_carrying"], c["controls"]))
    print("techniques carried: %d; techniques with a control: %d of %d (%.1f%%); non-mappable: %d"
          % (len(carried), c["with_a_control"], c["enterprise_techniques_and_subtechniques"], 100 * c["share_with_a_control"], c["non_mappable"]))
    for d in dropped[:20]:
        print("   dropped:", d)


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        fetch()
    build()
