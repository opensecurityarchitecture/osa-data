#!/usr/bin/env python3
"""
Update control JSON files to include Rev 5 placeholder fields and new schema structure.
"""

import json
import os
from pathlib import Path

CONTROLS_DIR = Path(__file__).parent.parent / "data" / "controls"

def update_control_file(filepath: Path) -> bool:
    """Update a single control file with new schema fields."""

    with open(filepath, 'r', encoding='utf-8') as f:
        control = json.load(f)

    # Skip if already updated (has nist_800_53 field)
    if 'nist_800_53' in control:
        print(f"  Skipping {filepath.name} - already updated")
        return False

    # Add schema reference
    control['$schema'] = '../schema/control.schema.json'

    # Create nist_800_53 version structure
    control['nist_800_53'] = {
        'rev4': {
            'id': control['id'],
            'name': control['name'],
            'withdrawn': False,
            'incorporated_into': []
        },
        'rev5': {
            'id': control['id'],  # Same by default, update manually if changed
            'name': '',  # To be filled in from NIST Rev 5 data
            'description': '',
            'discussion': '',
            'related_controls': [],
            'baseline_low': None,
            'baseline_moderate': None,
            'baseline_high': None,
            'baseline_privacy': None,
            'new_in_rev5': False,
            'changes_from_rev4': ''
        }
    }

    # Create compliance_mappings structure
    control['compliance_mappings'] = {
        'iso_27001_2022': [],
        'iso_27002_2022': [],
        'cobit_2019': [],
        'pci_dss_v4': [],
        'nist_csf_2': [],
        'cis_controls_v8': [],
        'soc2_tsc': []
    }

    # Add metadata
    control['metadata'] = {
        'last_reviewed': None,
        'review_notes': '',
        'mapping_status': 'pending'
    }

    # Reorder keys for consistency
    ordered = {}
    key_order = [
        '$schema', 'id', 'name', 'family', 'family_name', 'control_class',
        'description', 'supplemental_guidance', 'enhancements',
        'baseline_low', 'baseline_moderate', 'baseline_high',
        'joomla_id',
        'nist_800_53',
        'iso17799', 'cobit41', 'pci_dss_v2',
        'compliance_mappings',
        'patterns',
        'metadata'
    ]

    for key in key_order:
        if key in control:
            ordered[key] = control[key]

    # Add any remaining keys not in our order
    for key in control:
        if key not in ordered:
            ordered[key] = control[key]

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(ordered, f, indent=2, ensure_ascii=False)

    print(f"  Updated {filepath.name}")
    return True


def main():
    """Update all control files."""
    print(f"Updating control files in {CONTROLS_DIR}")

    updated = 0
    skipped = 0

    for filepath in sorted(CONTROLS_DIR.glob("*.json")):
        if filepath.name.startswith('_'):
            continue

        if update_control_file(filepath):
            updated += 1
        else:
            skipped += 1

    print(f"\nDone. Updated: {updated}, Skipped: {skipped}")


if __name__ == '__main__':
    main()
