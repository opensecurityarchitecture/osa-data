#!/usr/bin/env python3
"""
Add new NIST 800-53 Rev 5 control families (PT and SR) to the control catalogue.
"""

import json
import re
from pathlib import Path
import pandas as pd

CONTROLS_DIR = Path(__file__).parent.parent / "data" / "controls"
WORKBOOK_PATH = Path("/tmp/nist-rev4-to-rev5.xlsx")

FAMILY_NAMES = {
    'PT': 'Personally Identifiable Information Processing and Transparency',
    'SR': 'Supply Chain Risk Management'
}

FAMILY_CLASSES = {
    'PT': 'Management',  # Privacy controls are typically management/policy
    'SR': 'Management'   # Supply chain controls are management/operational
}


def load_rev5_controls(families: list[str]) -> list[dict]:
    """Load Rev 5 controls for specified families from the NIST workbook."""

    df = pd.read_excel(WORKBOOK_PATH, sheet_name='Rev4 Rev5 Compared', skiprows=1)
    df.columns = ['id', 'title', 'baseline_privacy', 'baseline_low', 'baseline_moderate',
                  'baseline_high', 'significant_change', 'changed_elements',
                  'change_details', 'sort_as', 'extra']

    controls = []

    for _, row in df.iterrows():
        control_id = str(row['id']).strip() if pd.notna(row['id']) else None
        if not control_id:
            continue

        # Only base controls (not enhancements) for specified families
        match = re.match(r'^([A-Z]{2})-(\d+)$', control_id)
        if not match:
            continue

        family = match.group(1)
        if family not in families:
            continue

        num = int(match.group(2))
        normalized_id = f"{family}-{num:02d}"

        # Clean up title
        title = str(row['title']) if pd.notna(row['title']) else ''
        title = re.sub(r'^\([^)]+\)\n?', '', title).strip()

        # Parse baselines
        baseline_privacy = row['baseline_privacy'] == 'X' if pd.notna(row['baseline_privacy']) else False
        baseline_low = row['baseline_low'] == 'X' if pd.notna(row['baseline_low']) else False
        baseline_moderate = row['baseline_moderate'] == 'X' if pd.notna(row['baseline_moderate']) else False
        baseline_high = row['baseline_high'] == 'X' if pd.notna(row['baseline_high']) else False

        controls.append({
            'id': normalized_id,
            'name': title,
            'family': family,
            'family_name': FAMILY_NAMES[family],
            'control_class': FAMILY_CLASSES[family],
            'baseline_privacy': baseline_privacy,
            'baseline_low': baseline_low,
            'baseline_moderate': baseline_moderate,
            'baseline_high': baseline_high
        })

    return sorted(controls, key=lambda x: x['id'])


def create_control_file(control: dict) -> Path:
    """Create a JSON file for a new control."""

    control_data = {
        "$schema": "../schema/control.schema.json",
        "id": control['id'],
        "name": control['name'],
        "family": control['family'],
        "family_name": control['family_name'],
        "control_class": control['control_class'],
        "description": "",  # To be filled from full NIST SP 800-53 Rev 5
        "supplemental_guidance": "",
        "enhancements": "",
        "baseline_low": control['baseline_low'],
        "baseline_moderate": control['baseline_moderate'],
        "baseline_high": control['baseline_high'],
        "nist_800_53": {
            "rev4": {
                "id": None,
                "name": None,
                "withdrawn": False,
                "incorporated_into": []
            },
            "rev5": {
                "id": control['id'],
                "name": control['name'],
                "description": "",
                "discussion": "",
                "related_controls": [],
                "baseline_low": control['baseline_low'],
                "baseline_moderate": control['baseline_moderate'],
                "baseline_high": control['baseline_high'],
                "baseline_privacy": control['baseline_privacy'],
                "new_in_rev5": True,
                "changes_from_rev4": "New control family introduced in Rev 5"
            }
        },
        "iso17799": [],
        "cobit41": [],
        "pci_dss_v2": [],
        "compliance_mappings": {
            "iso_27001_2022": [],
            "iso_27002_2022": [],
            "cobit_2019": [],
            "pci_dss_v4": [],
            "nist_csf_2": [],
            "cis_controls_v8": [],
            "soc2_tsc": []
        },
        "metadata": {
            "last_reviewed": None,
            "review_notes": "",
            "mapping_status": "pending"
        }
    }

    # Generate filename
    slug = control['name'].lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    filename = f"{control['id']}-{slug}.json"
    filepath = CONTROLS_DIR / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(control_data, f, indent=2, ensure_ascii=False)

    return filepath


def update_manifest(new_controls: list[dict]):
    """Update the controls manifest with new controls."""

    manifest_path = CONTROLS_DIR / "_manifest.json"

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    for control in new_controls:
        slug = control['name'].lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
        filename = f"{control['id']}-{slug}.json"

        manifest['controls'].append({
            'id': control['id'],
            'name': control['name'],
            'family': control['family'],
            'family_name': control['family_name'],
            'baseline_low': control['baseline_low'],
            'baseline_moderate': control['baseline_moderate'],
            'baseline_high': control['baseline_high'],
            'file': filename
        })

    # Sort controls by ID
    manifest['controls'].sort(key=lambda x: x['id'])
    manifest['total_controls'] = len(manifest['controls'])

    # Update NIST version
    manifest['nist_version'] = '800-53 Rev 5'

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def main():
    """Add PT and SR control families."""

    print("Loading PT and SR controls from NIST Rev 5 workbook...")
    controls = load_rev5_controls(['PT', 'SR'])
    print(f"Found {len(controls)} base controls")
    print()

    print("Creating control files...")
    for control in controls:
        filepath = create_control_file(control)
        baselines = []
        if control['baseline_privacy']:
            baselines.append('P')
        if control['baseline_low']:
            baselines.append('L')
        if control['baseline_moderate']:
            baselines.append('M')
        if control['baseline_high']:
            baselines.append('H')
        baseline_str = ','.join(baselines) if baselines else 'none'
        print(f"  Created {filepath.name} [{baseline_str}]")

    print()
    print("Updating manifest...")
    update_manifest(controls)

    print()
    print(f"Done. Added {len(controls)} new Rev 5 controls:")
    pt_count = len([c for c in controls if c['family'] == 'PT'])
    sr_count = len([c for c in controls if c['family'] == 'SR'])
    print(f"  PT (Privacy): {pt_count} controls")
    print(f"  SR (Supply Chain): {sr_count} controls")


if __name__ == '__main__':
    main()
