#!/usr/bin/env python3
"""
Enrich detection catalog with descriptions from ATT&CK STIX data.

Source: ATT&CK Enterprise STIX bundle via stix_utils.py
Fields added: description

Detection strategies in ATT&CK v18 don't carry descriptions directly.
Descriptions are built from the linked analytic objects (x_mitre_analytic_refs).

Idempotent: safe to run multiple times.
"""

import json
from pathlib import Path
from stix_utils import download_stix_bundle, build_detection_lookup, clean_description

DATA_DIR = Path(__file__).parent.parent / "data"
CATALOG_PATH = DATA_DIR / "attack" / "detection-catalog.json"


def build_analytic_lookup(bundle: dict) -> dict:
    """Build {analytic_stix_id: description} from x-mitre-analytic objects."""
    lookup = {}
    for obj in bundle.get("objects", []):
        if obj.get("type") == "x-mitre-analytic":
            if obj.get("revoked") or obj.get("x_mitre_deprecated"):
                continue
            desc = obj.get("description", "")
            if desc:
                lookup[obj["id"]] = desc
    return lookup


def main():
    # Load current detection catalog
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    # Download and parse STIX
    bundle = download_stix_bundle()
    det_lookup = build_detection_lookup(bundle)
    analytic_lookup = build_analytic_lookup(bundle)
    print(f"  STIX detection lookup: {len(det_lookup)} entries")
    print(f"  STIX analytic lookup: {len(analytic_lookup)} entries")

    enriched = 0
    missing = 0

    for det_id, entry in catalog.items():
        stix_obj = det_lookup.get(det_id)
        if not stix_obj:
            missing += 1
            if "description" not in entry:
                entry["description"] = ""
            continue

        # Try direct description first
        desc = stix_obj.get("description", "")

        # If no direct description, build from linked analytics
        if not desc:
            analytic_refs = stix_obj.get("x_mitre_analytic_refs", [])
            analytic_descs = []
            for ref_id in analytic_refs:
                adesc = analytic_lookup.get(ref_id, "")
                if adesc:
                    analytic_descs.append(adesc)

            if analytic_descs:
                # Use the first analytic description (they're usually similar)
                desc = analytic_descs[0]

        entry["description"] = clean_description(desc)
        if entry["description"]:
            enriched += 1

    # Write back
    with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        f.write('\n')

    with_desc = sum(1 for v in catalog.values() if v.get("description"))

    print(f"\nDetection Catalog Enrichment Complete")
    print(f"  Enriched with descriptions: {enriched}/{len(catalog)}")
    print(f"  Total with description: {with_desc}")
    if missing:
        print(f"  Missing STIX data: {missing}")


if __name__ == "__main__":
    main()
