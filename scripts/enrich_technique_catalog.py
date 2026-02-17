#!/usr/bin/env python3
"""
Enrich technique catalog with descriptions and parent IDs from ATT&CK STIX data.

Source: ATT&CK Enterprise STIX bundle via stix_utils.py
Fields added: description, parent

Idempotent: safe to run multiple times.
"""

import json
from pathlib import Path
from stix_utils import download_stix_bundle, build_technique_lookup, clean_description

DATA_DIR = Path(__file__).parent.parent / "data"
CATALOG_PATH = DATA_DIR / "attack" / "technique-catalog.json"


def main():
    # Load current technique catalog
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    # Download and parse STIX
    bundle = download_stix_bundle()
    technique_lookup = build_technique_lookup(bundle)
    print(f"  STIX technique lookup: {len(technique_lookup)} entries")

    enriched = 0
    missing = 0

    for tech_id, entry in catalog.items():
        stix_obj = technique_lookup.get(tech_id)
        if not stix_obj:
            print(f"  WARNING: No STIX data for {tech_id}")
            missing += 1
            entry["description"] = ""
            entry["parent"] = None
        else:
            entry["description"] = clean_description(stix_obj.get("description", ""))
            enriched += 1

        # Derive parent from technique ID
        if entry.get("is_subtechnique") and "." in tech_id:
            entry["parent"] = tech_id.split(".")[0]
        else:
            entry["parent"] = None

    # Write back
    with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        f.write('\n')

    with_parent = sum(1 for v in catalog.values() if v.get("parent") is not None)
    with_desc = sum(1 for v in catalog.values() if v.get("description"))

    print(f"\nTechnique Catalog Enrichment Complete")
    print(f"  Enriched from STIX: {enriched}/{len(catalog)}")
    print(f"  With description: {with_desc}")
    print(f"  With parent: {with_parent}")
    if missing:
        print(f"  Missing STIX data: {missing}")


if __name__ == "__main__":
    main()
