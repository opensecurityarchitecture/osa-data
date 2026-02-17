#!/usr/bin/env python3
"""
Enrich actor catalog with descriptions and URLs from ATT&CK STIX data.

Source: ATT&CK Enterprise STIX bundle via stix_utils.py
Fields added: description, url

Idempotent: safe to run multiple times.
"""

import json
from pathlib import Path
from stix_utils import download_stix_bundle, build_actor_lookup, clean_description

DATA_DIR = Path(__file__).parent.parent / "data"
CATALOG_PATH = DATA_DIR / "attack" / "actor-catalog.json"


def main():
    # Load current actor catalog
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    # Download and parse STIX
    bundle = download_stix_bundle()
    actor_lookup = build_actor_lookup(bundle)
    print(f"  STIX actor lookup: {len(actor_lookup)} entries")

    enriched = 0
    missing = 0

    for group_id, entry in catalog.items():
        stix_obj = actor_lookup.get(group_id)
        if not stix_obj:
            print(f"  WARNING: No STIX data for {group_id} ({entry.get('name')})")
            missing += 1
            entry["description"] = ""
            entry["url"] = f"https://attack.mitre.org/groups/{group_id}"
        else:
            entry["description"] = clean_description(stix_obj.get("description", ""))
            entry["url"] = f"https://attack.mitre.org/groups/{group_id}"
            enriched += 1

    # Write back
    with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        f.write('\n')

    with_desc = sum(1 for v in catalog.values() if v.get("description"))

    print(f"\nActor Catalog Enrichment Complete")
    print(f"  Enriched from STIX: {enriched}/{len(catalog)}")
    print(f"  With description: {with_desc}")
    if missing:
        print(f"  Missing STIX data: {missing}")


if __name__ == "__main__":
    main()
