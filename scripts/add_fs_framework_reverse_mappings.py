#!/usr/bin/env python3
"""Add reverse mappings for 7 financial services frameworks to all 315 control files.

Reads framework-coverage JSONs to build control -> clause mappings,
then adds them to each control's compliance_mappings object.
"""

import json
import os
from collections import defaultdict

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
CONTROLS_DIR = os.path.join(BASE_DIR, 'data', 'controls')
COVERAGE_DIR = os.path.join(BASE_DIR, 'data', 'framework-coverage')

# The 7 new frameworks (ordered by framework_id)
NEW_FRAMEWORKS = [
    ('pci_pts', 'pci-pts.json'),
    ('fips_140', 'fips-140.json'),
    ('cbest', 'cbest.json'),
    ('tiber_eu', 'tiber-eu.json'),
    ('pci_hsm', 'pci-hsm.json'),
    ('common_criteria', 'common-criteria.json'),
    ('isae_3402', 'isae-3402.json'),
]


def load_forward_mappings():
    """Extract control -> [clause_ids] from each framework-coverage file."""
    # framework_id -> { control_id -> [clause_ids] }
    reverse = {}

    for fw_id, filename in NEW_FRAMEWORKS:
        filepath = os.path.join(COVERAGE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  WARNING: {filepath} not found, skipping {fw_id}")
            reverse[fw_id] = {}
            continue

        with open(filepath) as f:
            data = json.load(f)

        ctrl_to_clauses = defaultdict(list)
        for clause in data['clauses']:
            clause_id = clause['id']
            for ctrl_id in clause['controls']:
                if clause_id not in ctrl_to_clauses[ctrl_id]:
                    ctrl_to_clauses[ctrl_id].append(clause_id)

        reverse[fw_id] = dict(ctrl_to_clauses)
        print(f"  {fw_id}: {len(ctrl_to_clauses)} controls referenced across {len(data['clauses'])} clauses")

    return reverse


def update_control_files(reverse_maps):
    """Add new framework keys to all control compliance_mappings."""
    manifest_path = os.path.join(CONTROLS_DIR, '_manifest.json')
    with open(manifest_path) as f:
        manifest = json.load(f)

    updated = 0
    for ctrl_entry in manifest['controls']:
        ctrl_file = os.path.join(CONTROLS_DIR, ctrl_entry['file'])
        with open(ctrl_file) as f:
            ctrl = json.load(f)

        mappings = ctrl.get('compliance_mappings', {})

        # Add each new framework
        changed = False
        for fw_id, _ in NEW_FRAMEWORKS:
            if fw_id not in mappings:
                clauses = sorted(reverse_maps[fw_id].get(ctrl['id'], []))
                mappings[fw_id] = clauses
                changed = True

        if changed:
            ctrl['compliance_mappings'] = mappings
            with open(ctrl_file, 'w') as f:
                json.dump(ctrl, f, indent=2, ensure_ascii=False)
                f.write('\n')
            updated += 1

    return updated


def verify_consistency(reverse_maps):
    """Cross-check: count total clauses mapped per framework."""
    print("\nReverse mapping summary:")
    for fw_id, ctrl_map in reverse_maps.items():
        total_refs = sum(len(clauses) for clauses in ctrl_map.values())
        unique_clauses = set()
        for clauses in ctrl_map.values():
            unique_clauses.update(clauses)
        print(f"  {fw_id}: {len(ctrl_map)} controls, {len(unique_clauses)} unique clauses, {total_refs} total references")


def main():
    print("Loading forward mappings from framework-coverage files...")
    reverse_maps = load_forward_mappings()

    verify_consistency(reverse_maps)

    print(f"\nUpdating {315} control files...")
    updated = update_control_files(reverse_maps)
    print(f"  Updated {updated} control files with 7 new framework keys")

    print("\nDone.")


if __name__ == '__main__':
    main()
