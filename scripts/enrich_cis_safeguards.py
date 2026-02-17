#!/usr/bin/env python3
"""
Enrich CIS safeguard index with name, description, implementation group, and asset type.

Sources:
- Name and description from data/framework-coverage/cis-controls-v8.json (clauses[].title, rationale)
- Implementation group (IG) from embedded CIS v8 lookup table
- Asset type from embedded CIS v8 lookup table

Idempotent: safe to run multiple times.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
CIS_INDEX_PATH = DATA_DIR / "attack" / "cis-safeguard-index.json"
CIS_COVERAGE_PATH = DATA_DIR / "framework-coverage" / "cis-controls-v8.json"

# CIS v8 Implementation Group assignments (which IG a safeguard first appears in)
# Source: CIS Controls v8 (cisecurity.org)
# Parent controls (e.g., CIS 1, CIS 2) are headings — no IG assignment
IG_LOOKUP = {
    "CIS 1.1": 1, "CIS 1.2": 1, "CIS 1.3": 2, "CIS 1.4": 2, "CIS 1.5": 3,
    "CIS 2.1": 1, "CIS 2.2": 2, "CIS 2.3": 1, "CIS 2.4": 2, "CIS 2.5": 2, "CIS 2.6": 2, "CIS 2.7": 3,
    "CIS 3.1": 1, "CIS 3.2": 2, "CIS 3.3": 1, "CIS 3.4": 1, "CIS 3.5": 2, "CIS 3.6": 1, "CIS 3.7": 2,
    "CIS 3.8": 2, "CIS 3.9": 2, "CIS 3.10": 2, "CIS 3.11": 1, "CIS 3.12": 1, "CIS 3.13": 3, "CIS 3.14": 3,
    "CIS 4.1": 1, "CIS 4.2": 2, "CIS 4.3": 2, "CIS 4.4": 2, "CIS 4.5": 2, "CIS 4.6": 1, "CIS 4.7": 1,
    "CIS 4.8": 2, "CIS 4.9": 2, "CIS 4.10": 2, "CIS 4.11": 3, "CIS 4.12": 2,
    "CIS 5.1": 1, "CIS 5.2": 1, "CIS 5.3": 1, "CIS 5.4": 1, "CIS 5.5": 2, "CIS 5.6": 3,
    "CIS 6.1": 1, "CIS 6.2": 1, "CIS 6.3": 2, "CIS 6.4": 2, "CIS 6.5": 1, "CIS 6.6": 2, "CIS 6.7": 2, "CIS 6.8": 2,
    "CIS 7.1": 1, "CIS 7.2": 2, "CIS 7.3": 2, "CIS 7.4": 2, "CIS 7.5": 3, "CIS 7.6": 3, "CIS 7.7": 3,
    "CIS 8.1": 2, "CIS 8.2": 1, "CIS 8.3": 2, "CIS 8.4": 2, "CIS 8.5": 1, "CIS 8.6": 2, "CIS 8.7": 2,
    "CIS 8.8": 2, "CIS 8.9": 2, "CIS 8.10": 2, "CIS 8.11": 2, "CIS 8.12": 2,
    "CIS 9.1": 1, "CIS 9.2": 1, "CIS 9.3": 2, "CIS 9.4": 2, "CIS 9.5": 3, "CIS 9.6": 3, "CIS 9.7": 3,
    "CIS 10.1": 1, "CIS 10.2": 1, "CIS 10.3": 2, "CIS 10.4": 2, "CIS 10.5": 2, "CIS 10.6": 2, "CIS 10.7": 2,
    "CIS 11.1": 1, "CIS 11.2": 1, "CIS 11.3": 1, "CIS 11.4": 1, "CIS 11.5": 3,
    "CIS 12.1": 1, "CIS 12.2": 2, "CIS 12.3": 2, "CIS 12.4": 2, "CIS 12.5": 3, "CIS 12.6": 3, "CIS 12.7": 2, "CIS 12.8": 2,
    "CIS 13.1": 1, "CIS 13.2": 2, "CIS 13.3": 2, "CIS 13.4": 2, "CIS 13.5": 2, "CIS 13.6": 1, "CIS 13.7": 2,
    "CIS 13.8": 2, "CIS 13.9": 2, "CIS 13.10": 3, "CIS 13.11": 3,
    "CIS 14.1": 1, "CIS 14.2": 1, "CIS 14.3": 2, "CIS 14.4": 2, "CIS 14.5": 2, "CIS 14.6": 2, "CIS 14.7": 2,
    "CIS 14.8": 3, "CIS 14.9": 3,
    "CIS 15.1": 1, "CIS 15.2": 2, "CIS 15.3": 2, "CIS 15.4": 2, "CIS 15.5": 3, "CIS 15.6": 3, "CIS 15.7": 3,
    "CIS 16.1": 1, "CIS 16.2": 1, "CIS 16.3": 2, "CIS 16.4": 2, "CIS 16.5": 2, "CIS 16.6": 2, "CIS 16.7": 1,
    "CIS 16.8": 1, "CIS 16.9": 1, "CIS 16.10": 2, "CIS 16.11": 1, "CIS 16.12": 2, "CIS 16.13": 3, "CIS 16.14": 3,
    "CIS 17.1": 2, "CIS 17.2": 2, "CIS 17.3": 1, "CIS 17.4": 2, "CIS 17.5": 2, "CIS 17.6": 1, "CIS 17.7": 2,
    "CIS 17.8": 2, "CIS 17.9": 1,
    "CIS 18.1": 2, "CIS 18.2": 2, "CIS 18.3": 1, "CIS 18.4": 2, "CIS 18.5": 3,
}

# CIS v8 asset type assignments
# Parent controls are headings — no asset type
ASSET_TYPE_LOOKUP = {
    "CIS 1.1": "devices", "CIS 1.2": "devices", "CIS 1.3": "devices", "CIS 1.4": "devices", "CIS 1.5": "devices",
    "CIS 2.1": "applications", "CIS 2.2": "applications", "CIS 2.3": "applications", "CIS 2.4": "applications",
    "CIS 2.5": "applications", "CIS 2.6": "applications", "CIS 2.7": "applications",
    "CIS 3.1": "data", "CIS 3.2": "data", "CIS 3.3": "data", "CIS 3.4": "data", "CIS 3.5": "data",
    "CIS 3.6": "data", "CIS 3.7": "data", "CIS 3.8": "data", "CIS 3.9": "data", "CIS 3.10": "data",
    "CIS 3.11": "data", "CIS 3.12": "data", "CIS 3.13": "data", "CIS 3.14": "data",
    "CIS 4.1": "devices", "CIS 4.2": "devices", "CIS 4.3": "devices", "CIS 4.4": "devices",
    "CIS 4.5": "devices", "CIS 4.6": "devices", "CIS 4.7": "users", "CIS 4.8": "devices",
    "CIS 4.9": "devices", "CIS 4.10": "devices", "CIS 4.11": "devices", "CIS 4.12": "devices",
    "CIS 5.1": "users", "CIS 5.2": "users", "CIS 5.3": "users", "CIS 5.4": "users",
    "CIS 5.5": "users", "CIS 5.6": "users",
    "CIS 6.1": "users", "CIS 6.2": "users", "CIS 6.3": "users", "CIS 6.4": "users",
    "CIS 6.5": "users", "CIS 6.6": "users", "CIS 6.7": "users", "CIS 6.8": "users",
    "CIS 7.1": "applications", "CIS 7.2": "applications", "CIS 7.3": "applications", "CIS 7.4": "applications",
    "CIS 7.5": "applications", "CIS 7.6": "applications", "CIS 7.7": "applications",
    "CIS 8.1": "devices", "CIS 8.2": "devices", "CIS 8.3": "network", "CIS 8.4": "network",
    "CIS 8.5": "devices", "CIS 8.6": "devices", "CIS 8.7": "devices", "CIS 8.8": "devices",
    "CIS 8.9": "devices", "CIS 8.10": "devices", "CIS 8.11": "devices", "CIS 8.12": "network",
    "CIS 9.1": "network", "CIS 9.2": "network", "CIS 9.3": "network", "CIS 9.4": "network",
    "CIS 9.5": "network", "CIS 9.6": "network", "CIS 9.7": "network",
    "CIS 10.1": "devices", "CIS 10.2": "devices", "CIS 10.3": "devices", "CIS 10.4": "devices",
    "CIS 10.5": "devices", "CIS 10.6": "devices", "CIS 10.7": "devices",
    "CIS 11.1": "data", "CIS 11.2": "data", "CIS 11.3": "data", "CIS 11.4": "data", "CIS 11.5": "data",
    "CIS 12.1": "network", "CIS 12.2": "network", "CIS 12.3": "network", "CIS 12.4": "network",
    "CIS 12.5": "network", "CIS 12.6": "network", "CIS 12.7": "network", "CIS 12.8": "network",
    "CIS 13.1": "network", "CIS 13.2": "network", "CIS 13.3": "network", "CIS 13.4": "network",
    "CIS 13.5": "network", "CIS 13.6": "network", "CIS 13.7": "network", "CIS 13.8": "network",
    "CIS 13.9": "network", "CIS 13.10": "network", "CIS 13.11": "network",
    "CIS 14.1": "users", "CIS 14.2": "users", "CIS 14.3": "users", "CIS 14.4": "users",
    "CIS 14.5": "users", "CIS 14.6": "users", "CIS 14.7": "users", "CIS 14.8": "users", "CIS 14.9": "users",
    "CIS 15.1": "network", "CIS 15.2": "network", "CIS 15.3": "network", "CIS 15.4": "network",
    "CIS 15.5": "network", "CIS 15.6": "network", "CIS 15.7": "network",
    "CIS 16.1": "applications", "CIS 16.2": "applications", "CIS 16.3": "applications", "CIS 16.4": "applications",
    "CIS 16.5": "applications", "CIS 16.6": "applications", "CIS 16.7": "applications", "CIS 16.8": "applications",
    "CIS 16.9": "applications", "CIS 16.10": "applications", "CIS 16.11": "applications", "CIS 16.12": "applications",
    "CIS 16.13": "applications", "CIS 16.14": "applications",
    "CIS 17.1": "devices", "CIS 17.2": "devices", "CIS 17.3": "devices", "CIS 17.4": "devices",
    "CIS 17.5": "devices", "CIS 17.6": "devices", "CIS 17.7": "devices", "CIS 17.8": "devices", "CIS 17.9": "devices",
    "CIS 18.1": "applications", "CIS 18.2": "applications", "CIS 18.3": "applications",
    "CIS 18.4": "applications", "CIS 18.5": "applications",
}


def main():
    # Load current CIS safeguard index
    with open(CIS_INDEX_PATH, 'r', encoding='utf-8') as f:
        cis_index = json.load(f)

    # Load framework coverage for names and descriptions
    with open(CIS_COVERAGE_PATH, 'r', encoding='utf-8') as f:
        coverage = json.load(f)

    # Build lookup from clause ID to clause data
    clause_lookup = {c["id"]: c for c in coverage["clauses"]}

    enriched = 0
    missing = 0

    for cis_id, entry in cis_index.items():
        clause = clause_lookup.get(cis_id)
        if not clause:
            print(f"  WARNING: No coverage data for {cis_id}")
            missing += 1
            continue

        entry["name"] = clause["title"]
        entry["description"] = clause.get("rationale", "")
        entry["implementation_group"] = IG_LOOKUP.get(cis_id)
        entry["asset_type"] = ASSET_TYPE_LOOKUP.get(cis_id)
        entry["url"] = "https://www.cisecurity.org/controls/v8"
        enriched += 1

    # Write back
    with open(CIS_INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(cis_index, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f"\nCIS Safeguard Enrichment Complete")
    print(f"  Enriched: {enriched}/{len(cis_index)}")
    if missing:
        print(f"  Missing coverage data: {missing}")

    # Count stats
    with_ig = sum(1 for v in cis_index.values() if v.get("implementation_group") is not None)
    with_asset = sum(1 for v in cis_index.values() if v.get("asset_type") is not None)
    print(f"  With IG: {with_ig}")
    print(f"  With asset_type: {with_asset}")


if __name__ == "__main__":
    main()
