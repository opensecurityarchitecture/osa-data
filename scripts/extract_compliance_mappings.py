#!/usr/bin/env python3
"""
Extract compliance framework mappings from Secure Controls Framework (SCF) spreadsheet.
Maps NIST 800-53 R5 controls to ISO 27001:2022, ISO 27002:2022, COBIT 2019, CIS v8,
NIST CSF 2.0, and SOC 2 TSC.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
import pandas as pd

SCF_PATH = Path("/tmp/scf-2025.4.xlsx")
CONTROLS_DIR = Path(__file__).parent.parent / "data" / "controls"


def normalize_nist_id(control_id: str) -> str:
    """Normalize NIST control ID to our format (e.g., AC-1 -> AC-01)."""
    match = re.match(r'^([A-Z]{2})-(\d+)(\(\d+\))?$', control_id.strip())
    if match:
        family, num, enhancement = match.groups()
        normalized = f"{family}-{int(num):02d}"
        if enhancement:
            normalized += enhancement
        return normalized
    return control_id.strip()


def parse_control_list(cell_value) -> list[str]:
    """Parse a cell containing multiple control references."""
    if pd.isna(cell_value) or not cell_value:
        return []

    # Split by newlines and clean up
    refs = str(cell_value).strip().split('\n')
    refs = [r.strip() for r in refs if r.strip()]
    return refs


def extract_mappings() -> dict:
    """Extract compliance mappings from SCF spreadsheet."""

    print("Loading SCF 2025.4 spreadsheet...")
    df = pd.read_excel(SCF_PATH, sheet_name='SCF 2025.4')

    # Column names (with newlines as in the spreadsheet)
    columns = {
        'nist_800_53_r5': 'NIST\n800-53\nR5',
        'iso_27001_2022': 'ISO\n27001\n2022',
        'iso_27002_2022': 'ISO\n27002\n2022',
        'cobit_2019': 'COBIT\n2019',
        'cis_v8': 'CIS\nCSC\n8.1',
        'nist_csf_2': 'NIST\nCSF\n2.0',
        'soc2_tsc': 'AICPA\nTSC 2017:2022 (used for SOC 2)',
    }

    # Build reverse mapping: NIST control -> other frameworks
    mappings = defaultdict(lambda: {
        'iso_27001_2022': set(),
        'iso_27002_2022': set(),
        'cobit_2019': set(),
        'cis_controls_v8': set(),
        'nist_csf_2': set(),
        'soc2_tsc': set(),
    })

    print(f"Processing {len(df)} SCF controls...")

    for _, row in df.iterrows():
        # Get NIST controls for this row
        nist_controls = parse_control_list(row.get(columns['nist_800_53_r5']))

        if not nist_controls:
            continue

        # Get other framework references
        iso_27001 = parse_control_list(row.get(columns['iso_27001_2022']))
        iso_27002 = parse_control_list(row.get(columns['iso_27002_2022']))
        cobit = parse_control_list(row.get(columns['cobit_2019']))
        cis = parse_control_list(row.get(columns['cis_v8']))
        csf = parse_control_list(row.get(columns['nist_csf_2']))
        soc2 = parse_control_list(row.get(columns['soc2_tsc']))

        # Map each NIST control to the other frameworks
        for nist_id in nist_controls:
            normalized_id = normalize_nist_id(nist_id)

            # Skip enhancements (we only have base controls)
            if '(' in normalized_id:
                continue

            mappings[normalized_id]['iso_27001_2022'].update(iso_27001)
            mappings[normalized_id]['iso_27002_2022'].update(iso_27002)
            mappings[normalized_id]['cobit_2019'].update(cobit)
            mappings[normalized_id]['cis_controls_v8'].update(cis)
            mappings[normalized_id]['nist_csf_2'].update(csf)
            mappings[normalized_id]['soc2_tsc'].update(soc2)

    # Convert sets to sorted lists
    result = {}
    for control_id, frameworks in mappings.items():
        result[control_id] = {
            k: sorted(list(v)) for k, v in frameworks.items()
        }

    return result


def update_control_files(mappings: dict) -> tuple[int, int]:
    """Update control JSON files with compliance mappings."""

    updated = 0
    not_found = 0

    for filepath in sorted(CONTROLS_DIR.glob("*.json")):
        if filepath.name.startswith('_'):
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            control = json.load(f)

        control_id = control['id']

        if control_id not in mappings:
            not_found += 1
            continue

        # Update compliance_mappings
        if 'compliance_mappings' not in control:
            control['compliance_mappings'] = {}

        control['compliance_mappings'].update(mappings[control_id])

        # Update metadata
        if 'metadata' not in control:
            control['metadata'] = {}

        # Check if we have substantial mappings
        has_mappings = any(len(v) > 0 for v in mappings[control_id].values())
        if has_mappings:
            control['metadata']['mapping_status'] = 'complete'

        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(control, f, indent=2, ensure_ascii=False)

        updated += 1

    return updated, not_found


def main():
    """Extract and apply compliance mappings."""

    mappings = extract_mappings()
    print(f"Extracted mappings for {len(mappings)} NIST controls")

    # Show sample
    print("\nSample mappings:")
    for control_id in ['AC-01', 'AC-02', 'SC-07', 'IA-02']:
        if control_id in mappings:
            m = mappings[control_id]
            print(f"\n  {control_id}:")
            print(f"    ISO 27001:2022: {len(m['iso_27001_2022'])} refs")
            print(f"    ISO 27002:2022: {len(m['iso_27002_2022'])} refs")
            print(f"    COBIT 2019: {len(m['cobit_2019'])} refs")
            print(f"    CIS v8: {len(m['cis_controls_v8'])} refs")
            print(f"    NIST CSF 2.0: {len(m['nist_csf_2'])} refs")
            print(f"    SOC 2 TSC: {len(m['soc2_tsc'])} refs")

    print("\nUpdating control files...")
    updated, not_found = update_control_files(mappings)

    print(f"\nDone. Updated: {updated}, Not in SCF: {not_found}")

    # Summary stats
    total_iso27001 = sum(len(m['iso_27001_2022']) for m in mappings.values())
    total_iso27002 = sum(len(m['iso_27002_2022']) for m in mappings.values())
    total_cobit = sum(len(m['cobit_2019']) for m in mappings.values())
    total_cis = sum(len(m['cis_controls_v8']) for m in mappings.values())
    total_csf = sum(len(m['nist_csf_2']) for m in mappings.values())
    total_soc2 = sum(len(m['soc2_tsc']) for m in mappings.values())

    print(f"\nMapping totals:")
    print(f"  ISO 27001:2022: {total_iso27001} references")
    print(f"  ISO 27002:2022: {total_iso27002} references")
    print(f"  COBIT 2019: {total_cobit} references")
    print(f"  CIS Controls v8: {total_cis} references")
    print(f"  NIST CSF 2.0: {total_csf} references")
    print(f"  SOC 2 TSC: {total_soc2} references")


if __name__ == '__main__':
    main()
