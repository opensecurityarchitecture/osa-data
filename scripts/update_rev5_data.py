#!/usr/bin/env python3
"""
Update control JSON files with NIST 800-53 Rev 5 data from the official comparison workbook.
"""

import json
import re
from pathlib import Path
import pandas as pd

CONTROLS_DIR = Path(__file__).parent.parent / "data" / "controls"
WORKBOOK_PATH = Path("/tmp/nist-rev4-to-rev5.xlsx")


def load_rev5_data() -> dict:
    """Load and parse the NIST Rev 4 to Rev 5 comparison workbook."""

    df = pd.read_excel(WORKBOOK_PATH, sheet_name='Rev4 Rev5 Compared', skiprows=1)
    df.columns = ['id', 'title', 'baseline_privacy', 'baseline_low', 'baseline_moderate',
                  'baseline_high', 'significant_change', 'changed_elements',
                  'change_details', 'sort_as', 'extra']

    rev5_data = {}

    for _, row in df.iterrows():
        control_id = str(row['id']).strip() if pd.notna(row['id']) else None
        if not control_id or control_id == 'ID':
            continue

        # Normalize ID format: AC-1 -> AC-01, but keep AC-2(1) as AC-02(1)
        match = re.match(r'^([A-Z]{2})-(\d+)(\(\d+\))?$', control_id)
        if match:
            family, num, enhancement = match.groups()
            normalized_id = f"{family}-{int(num):02d}"
            if enhancement:
                normalized_id += enhancement
        else:
            normalized_id = control_id

        # Clean up title (remove family prefix like "(Access Control)\n")
        title = str(row['title']) if pd.notna(row['title']) else ''
        title = re.sub(r'^\([^)]+\)\n?', '', title).strip()

        # Parse baselines
        baseline_privacy = row['baseline_privacy'] == 'X' if pd.notna(row['baseline_privacy']) else False
        baseline_low = row['baseline_low'] == 'X' if pd.notna(row['baseline_low']) else False
        baseline_moderate = row['baseline_moderate'] == 'X' if pd.notna(row['baseline_moderate']) else False
        baseline_high = row['baseline_high'] == 'X' if pd.notna(row['baseline_high']) else False

        # Parse change info
        significant_change = row['significant_change'] == 'Y' if pd.notna(row['significant_change']) else False
        changed_elements = str(row['changed_elements']).strip() if pd.notna(row['changed_elements']) else ''
        change_details = str(row['change_details']).strip() if pd.notna(row['change_details']) else ''

        # Clean up change details
        changed_elements = changed_elements.replace('\n', '; ').strip('; ')
        change_details = change_details.replace('\n', ' ').strip()

        rev5_data[normalized_id] = {
            'id': normalized_id,
            'name': title,
            'baseline_privacy': baseline_privacy,
            'baseline_low': baseline_low,
            'baseline_moderate': baseline_moderate,
            'baseline_high': baseline_high,
            'significant_change': significant_change,
            'changed_elements': changed_elements,
            'change_details': change_details
        }

    return rev5_data


def update_control_file(filepath: Path, rev5_data: dict) -> tuple[bool, str]:
    """Update a single control file with Rev 5 data."""

    with open(filepath, 'r', encoding='utf-8') as f:
        control = json.load(f)

    control_id = control['id']

    if control_id not in rev5_data:
        return False, f"No Rev 5 data found for {control_id}"

    r5 = rev5_data[control_id]

    # Update the nist_800_53.rev5 section
    if 'nist_800_53' not in control:
        control['nist_800_53'] = {'rev4': {}, 'rev5': {}}

    control['nist_800_53']['rev5'] = {
        'id': r5['id'],
        'name': r5['name'],
        'description': '',  # Would need to fetch from full Rev 5 document
        'discussion': '',   # Would need to fetch from full Rev 5 document
        'related_controls': [],
        'baseline_low': r5['baseline_low'],
        'baseline_moderate': r5['baseline_moderate'],
        'baseline_high': r5['baseline_high'],
        'baseline_privacy': r5['baseline_privacy'],
        'new_in_rev5': False,
        'changes_from_rev4': r5['change_details'] if r5['significant_change'] else ''
    }

    # Update metadata
    if 'metadata' not in control:
        control['metadata'] = {}
    control['metadata']['mapping_status'] = 'partial'  # Rev 5 baselines done, descriptions pending

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(control, f, indent=2, ensure_ascii=False)

    status = "significant changes" if r5['significant_change'] else "minor/no changes"
    return True, status


def main():
    """Update all control files with Rev 5 data."""

    print("Loading NIST Rev 4 to Rev 5 comparison workbook...")
    rev5_data = load_rev5_data()
    print(f"Loaded {len(rev5_data)} Rev 5 control entries")
    print()

    print(f"Updating control files in {CONTROLS_DIR}")

    updated = 0
    not_found = 0
    significant_changes = 0

    for filepath in sorted(CONTROLS_DIR.glob("*.json")):
        if filepath.name.startswith('_'):
            continue

        success, status = update_control_file(filepath, rev5_data)

        if success:
            updated += 1
            if "significant" in status:
                significant_changes += 1
            print(f"  Updated {filepath.name}: {status}")
        else:
            not_found += 1
            print(f"  SKIP {filepath.name}: {status}")

    print()
    print(f"Done. Updated: {updated}, Not found in Rev 5: {not_found}")
    print(f"Controls with significant changes: {significant_changes}")

    # List new Rev 5 families not in our data
    print()
    print("New Rev 5 control families (not in current OSA data):")
    new_families = {'PT': 'PII Processing and Transparency', 'SR': 'Supply Chain Risk Management'}
    for family, name in new_families.items():
        count = len([k for k in rev5_data.keys() if k.startswith(f"{family}-") and '(' not in k])
        print(f"  {family}: {name} ({count} base controls)")


if __name__ == '__main__':
    main()
