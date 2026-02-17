#!/usr/bin/env python3
"""
Enrich weakness catalog with CWE names and descriptions.

Source: CWE XML from https://cwe.mitre.org/data/xml/cwec_latest.xml.zip
Caches download to /tmp/osa-cwe-cache/

Idempotent: safe to run multiple times.
"""

import json
import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import urlretrieve

DATA_DIR = Path(__file__).parent.parent / "data"
WEAKNESS_PATH = DATA_DIR / "attack" / "weakness-catalog.json"
CACHE_DIR = Path("/tmp/osa-cwe-cache")
CWE_ZIP_URL = "https://cwe.mitre.org/data/xml/cwec_latest.xml.zip"


def download_cwe_xml() -> Path:
    """Download and extract CWE XML, caching locally."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Find any extracted XML in cache
    for f in CACHE_DIR.glob("cwec_*.xml"):
        print(f"  Using cached CWE XML: {f.name}")
        return f

    zip_path = CACHE_DIR / "cwec_latest.xml.zip"
    if not zip_path.exists():
        print(f"  Downloading CWE XML from {CWE_ZIP_URL}...")
        urlretrieve(CWE_ZIP_URL, zip_path)
        print(f"  Downloaded {zip_path.stat().st_size / 1024 / 1024:.1f} MB")

    print("  Extracting...")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(CACHE_DIR)

    for f in CACHE_DIR.glob("cwec_*.xml"):
        print(f"  Extracted: {f.name}")
        return f

    raise FileNotFoundError("No CWE XML found after extraction")


def parse_cwe_xml(xml_path: Path) -> dict:
    """Parse CWE XML and return {CWE-ID: {name, description}} lookup."""
    print("  Parsing CWE XML...")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # CWE XML uses a namespace
    ns = {"cwe": "http://cwe.mitre.org/cwe-7"}

    lookup = {}
    for weakness in root.findall(".//cwe:Weakness", ns):
        cwe_id = f"CWE-{weakness.get('ID')}"
        name = weakness.get("Name", "")
        desc_elem = weakness.find("cwe:Description", ns)
        description = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""

        # Truncate description to 2000 chars
        if len(description) > 2000:
            description = description[:1997] + "..."

        lookup[cwe_id] = {
            "name": name,
            "description": description,
        }

    print(f"  Parsed {len(lookup)} CWE entries")
    return lookup


def main():
    # Load current weakness catalog
    with open(WEAKNESS_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    # Download and parse CWE XML
    xml_path = download_cwe_xml()
    cwe_lookup = parse_cwe_xml(xml_path)

    enriched = 0
    missing = 0

    for cwe_id, entry in catalog.items():
        cwe_data = cwe_lookup.get(cwe_id)
        if not cwe_data:
            print(f"  WARNING: No CWE data for {cwe_id}")
            missing += 1
            continue

        entry["name"] = cwe_data["name"]
        entry["description"] = cwe_data["description"]
        enriched += 1

    # Write back
    with open(WEAKNESS_PATH, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f"\nWeakness Catalog Enrichment Complete")
    print(f"  Enriched: {enriched}/{len(catalog)}")
    if missing:
        print(f"  Missing CWE data: {missing}")


if __name__ == "__main__":
    main()
