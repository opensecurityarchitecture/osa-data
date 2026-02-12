#!/usr/bin/env python3
"""Extract reverse mappings (clause → controls) for frameworks missing coverage data."""

import json
import os
from collections import defaultdict

CONTROLS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'controls')
COVERAGE_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'framework-coverage')

# The 7 frameworks that need coverage JSONs
MISSING_FRAMEWORKS = [
    'soc2_tsc',
    'iso_42001_2023',
    'anssi',
    'finma_circular',
    'osfi_b13',
    'gdpr',
    'dora',
]

def load_manifest():
    with open(os.path.join(CONTROLS_DIR, '_manifest.json')) as f:
        return json.load(f)

def extract_reverse_mappings():
    manifest = load_manifest()
    # framework_id -> { clause_id -> [control_ids] }
    reverse = {fw: defaultdict(list) for fw in MISSING_FRAMEWORKS}

    for ctrl_entry in manifest['controls']:
        ctrl_file = os.path.join(CONTROLS_DIR, ctrl_entry['file'])
        with open(ctrl_file) as f:
            ctrl = json.load(f)

        mappings = ctrl.get('compliance_mappings', {})
        for fw_id in MISSING_FRAMEWORKS:
            clauses = mappings.get(fw_id, [])
            for clause_id in clauses:
                reverse[fw_id][clause_id].append(ctrl['id'])

    # Print results
    for fw_id in MISSING_FRAMEWORKS:
        clauses = reverse[fw_id]
        sorted_clauses = sorted(clauses.keys())
        print(f"\n{'='*60}")
        print(f"Framework: {fw_id}")
        print(f"Unique clauses: {len(sorted_clauses)}")
        print(f"{'='*60}")
        for clause_id in sorted_clauses:
            controls = sorted(clauses[clause_id])
            print(f"  {clause_id}: {', '.join(controls)}")

    return reverse

if __name__ == '__main__':
    extract_reverse_mappings()
