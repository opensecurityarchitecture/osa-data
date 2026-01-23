#!/usr/bin/env python3
"""
OSA Control Extractor (Database)
Extracts NIST 800-53 controls with compliance mappings from the Joomla database.

Usage:
    python extract_controls_db.py [raw_export_file]

If no file provided, reads from stdin.
"""

import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from html.parser import HTMLParser
from typing import Optional

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "controls")


class HTMLStripper(HTMLParser):
    """Strip HTML tags and extract text."""
    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def get_text(self):
        return ''.join(self.text)


def strip_html(html: str) -> str:
    """Remove HTML tags from string."""
    stripper = HTMLStripper()
    stripper.feed(html)
    return stripper.get_text().strip()


def extract_field(html: str, field_name: str) -> str:
    """Extract a field value from HTML like '<b>Field:</b> value'."""
    patterns = [
        rf"<b>{field_name}:</b>\s*(.+?)(?=<p>|<b>|\Z)",
        rf"<strong>{field_name}:</strong>\s*(.+?)(?=<p>|<strong>|\Z)",
        rf"{field_name}:\s*(.+?)(?=\n|$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        if match:
            return strip_html(match.group(1)).strip()

    return ""


def extract_mapping(html: str, framework: str) -> list[str]:
    """Extract compliance mapping values."""
    pattern = rf"{framework} mapping:</b>\s*([^<]+)"
    match = re.search(pattern, html, re.IGNORECASE)
    if match:
        raw = match.group(1).strip()
        # Split by comma and clean
        return [m.strip() for m in re.split(r"[,;]", raw) if m.strip()]
    return []


@dataclass
class Control:
    id: str
    name: str
    family: str
    family_name: str
    control_class: str
    description: str
    supplemental_guidance: str
    enhancements: str
    baseline_low: bool
    baseline_moderate: bool
    baseline_high: bool
    iso17799: list
    cobit41: list
    pci_dss_v2: list
    joomla_id: int


FAMILY_NAMES = {
    "AC": "Access Control",
    "AT": "Awareness and Training",
    "AU": "Audit and Accountability",
    "CA": "Security Assessment and Authorization",
    "CM": "Configuration Management",
    "CP": "Contingency Planning",
    "IA": "Identification and Authentication",
    "IR": "Incident Response",
    "MA": "Maintenance",
    "MP": "Media Protection",
    "PE": "Physical and Environmental Protection",
    "PL": "Planning",
    "PM": "Program Management",
    "PS": "Personnel Security",
    "RA": "Risk Assessment",
    "SA": "System and Services Acquisition",
    "SC": "System and Communications Protection",
    "SI": "System and Information Integrity",
}


def parse_control(joomla_id: int, title: str, introtext: str) -> Optional[Control]:
    """Parse a control from database record."""

    # Extract control ID from title like "AC-01 Access Control Policies..."
    match = re.match(r"([A-Z]{2}-\d{2})\s+(.+)", title)
    if not match:
        return None

    control_id = match.group(1)
    control_name = match.group(2)
    family = control_id.split("-")[0]

    # Extract fields from introtext
    description = extract_field(introtext, "Control")
    supplemental = extract_field(introtext, "Supplemental Guidance")
    enhancements = extract_field(introtext, "Control Enhancements")
    baseline_raw = extract_field(introtext, "Baseline")
    control_class = extract_field(introtext, "Class")

    # Parse baseline
    baseline_low = "LOW" in baseline_raw.upper()
    baseline_mod = "MOD" in baseline_raw.upper()
    baseline_high = "HIGH" in baseline_raw.upper()

    # Extract compliance mappings
    iso17799 = extract_mapping(introtext, "ISO 17799")
    cobit41 = extract_mapping(introtext, "COBIT 4.1")
    pci_dss = extract_mapping(introtext, "PCI-DSS v2")

    return Control(
        id=control_id,
        name=control_name,
        family=family,
        family_name=FAMILY_NAMES.get(family, family),
        control_class=control_class,
        description=description,
        supplemental_guidance=supplemental,
        enhancements=enhancements,
        baseline_low=baseline_low,
        baseline_moderate=baseline_mod,
        baseline_high=baseline_high,
        iso17799=iso17799,
        cobit41=cobit41,
        pci_dss_v2=pci_dss,
        joomla_id=joomla_id
    )


def parse_mysql_output(content: str) -> list[tuple]:
    """Parse MySQL tab-separated output."""
    lines = content.strip().split("\n")
    if not lines:
        return []

    # Skip header
    records = []
    current_record = None

    for line in lines[1:]:  # Skip header
        parts = line.split("\t")
        if len(parts) >= 3:
            try:
                joomla_id = int(parts[0])
                title = parts[1]
                introtext = parts[2] if len(parts) > 2 else ""
                records.append((joomla_id, title, introtext))
            except ValueError:
                # Continuation of previous record
                if records:
                    joomla_id, title, introtext = records[-1]
                    records[-1] = (joomla_id, title, introtext + "\n" + line)

    return records


def main():
    # Read input
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    else:
        content = sys.stdin.read()

    # Parse records
    records = parse_mysql_output(content)
    print(f"Parsed {len(records)} records from input")

    # Extract controls
    controls = []
    for joomla_id, title, introtext in records:
        control = parse_control(joomla_id, title, introtext)
        if control:
            controls.append(control)

    print(f"Extracted {len(controls)} controls")

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Save individual control files
    for control in controls:
        filename = f"{control.id}.json"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(asdict(control), f, indent=2, ensure_ascii=False)

    # Save combined catalog
    catalog = {
        "version": "NIST 800-53 Rev 4",
        "source": "opensecurityarchitecture.org",
        "families": {},
        "controls": [asdict(c) for c in controls]
    }

    # Group by family
    for control in controls:
        if control.family not in catalog["families"]:
            catalog["families"][control.family] = {
                "name": control.family_name,
                "controls": []
            }
        catalog["families"][control.family]["controls"].append(control.id)

    catalog_path = os.path.join(OUTPUT_DIR, "_catalog.json")
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to {OUTPUT_DIR}/")
    print(f"  - {len(controls)} individual control files")
    print(f"  - _catalog.json (combined)")

    # Stats
    print("\nCompliance mappings found:")
    iso_count = sum(1 for c in controls if c.iso17799)
    cobit_count = sum(1 for c in controls if c.cobit41)
    pci_count = sum(1 for c in controls if c.pci_dss_v2)
    print(f"  - ISO 17799: {iso_count} controls")
    print(f"  - COBIT 4.1: {cobit_count} controls")
    print(f"  - PCI-DSS v2: {pci_count} controls")


if __name__ == "__main__":
    main()
