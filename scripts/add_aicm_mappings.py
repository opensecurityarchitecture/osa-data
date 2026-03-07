#!/usr/bin/env python3
"""
Add CSA AICM v1.0.3 compliance mappings to NIST 800-53 Rev 5 control files.

Cloud Security Alliance AI Controls Matrix v1.0.3
Published: 2025 (v1.0.3)
Standard type: Market-driven (extends CCM for AI/ML cloud security)

18 domains, 243 control objectives:
  A&A  (6)  - Audit & Assurance
  AIS  (15) - Application & Interface Security
  BCR  (11) - Business Continuity Management & Operational Resilience
  CCC  (9)  - Change Control & Configuration Management
  CEK  (21) - Cryptography, Encryption & Key Management
  DCS  (15) - Datacenter Security
  DSP  (24) - Data Security & Privacy Lifecycle Management
  GRC  (15) - Governance, Risk Management & Compliance
  HRS  (15) - Human Resources Security
  IAM  (19) - Identity & Access Management
  I&S  (9)  - Infrastructure & Virtualization Security
  IPY  (4)  - Interoperability & Portability
  LOG  (15) - Logging & Monitoring
  MDS  (13) - Model Security (NEW - AI specific)
  SEF  (9)  - Security Incident Management, E-Discovery & Cloud Forensics
  STA  (16) - Supply Chain Management, Transparency & Accountability
  TVM  (13) - Threat & Vulnerability Management
  UEM  (14) - Universal Endpoint Management

Reference format: "A&A-01", "AIS-02", "MDS-01", etc.
"""

import json
import os
from collections import OrderedDict

CONTROLS_DIR = "/Users/russellwing/osa-workspace/data/controls"

# ============================================================
# CSA AICM v1.0.3 MAPPINGS per NIST 800-53 control
# ============================================================
# Derived from data/framework-coverage/csa-aicm.json (forward mapping).
# Each NIST control ID maps to the AICM control objectives it addresses.

AICM_MAPPINGS = {
    # ---- AC ----
    "AC-01": ["DSP-01", "IAM-01"],
    "AC-02": ["IAM-03", "IAM-05", "IAM-06", "IAM-07", "IAM-08", "IAM-10", "IAM-11", "IAM-13", "IAM-17", "IAM-18", "LOG-12"],
    "AC-03": ["DSP-17", "IAM-16", "MDS-07"],
    "AC-04": ["AIS-08", "DSP-05", "DSP-10", "DSP-22", "I&S-03", "I&S-06", "UEM-11"],
    "AC-05": ["IAM-04", "IAM-09", "IAM-19"],
    "AC-06": ["IAM-04", "IAM-05", "IAM-08", "IAM-09", "IAM-10", "IAM-11", "IAM-16", "IAM-18", "IAM-19", "LOG-04", "MDS-07"],
    "AC-11": ["HRS-03", "UEM-06"],
    "AC-16": ["DSP-04", "DSP-06", "IAM-16"],
    "AC-17": ["HRS-04"],
    "AC-19": ["UEM-01", "UEM-13"],
    "AC-20": ["HRS-02", "UEM-14"],

    # ---- AT ----
    "AT-01": ["GRC-13", "HRS-11", "HRS-15"],
    "AT-02": ["HRS-11", "HRS-12", "HRS-13", "HRS-14"],
    "AT-03": ["DCS-11", "HRS-11", "HRS-12", "HRS-14"],

    # ---- AU ----
    "AU-01": ["A&A-01", "LOG-01"],
    "AU-02": ["CEK-09", "DSP-24", "LOG-01", "LOG-07", "LOG-08", "LOG-10", "LOG-11", "LOG-12", "LOG-14", "LOG-15"],
    "AU-03": ["LOG-07", "LOG-08", "LOG-11", "LOG-12", "LOG-15"],
    "AU-05": ["LOG-13"],
    "AU-06": ["A&A-05", "AIS-12", "LOG-03", "LOG-04", "LOG-05", "LOG-13", "LOG-14", "MDS-05", "SEF-06"],
    "AU-08": ["LOG-06"],
    "AU-09": ["IAM-12", "LOG-02", "LOG-04", "LOG-09"],
    "AU-10": ["IAM-12"],
    "AU-11": ["LOG-02", "LOG-09"],
    "AU-12": ["LOG-11"],

    # ---- CA ----
    "CA-01": ["A&A-01"],
    "CA-02": ["A&A-01", "A&A-02", "A&A-03", "A&A-04", "A&A-05", "A&A-06", "CEK-09", "GRC-07", "GRC-12", "STA-05", "STA-06", "STA-11", "STA-12", "STA-13"],
    "CA-05": ["A&A-04", "A&A-05", "A&A-06", "CCC-08", "GRC-04"],
    "CA-07": ["A&A-02", "AIS-03", "AIS-12", "GRC-12", "GRC-15", "LOG-03", "LOG-10", "LOG-15", "MDS-05", "SEF-05", "STA-11", "TVM-09", "TVM-10", "TVM-13"],
    "CA-08": ["A&A-02", "AIS-05", "AIS-13", "MDS-03", "TVM-06", "TVM-12"],
    "CA-09": ["A&A-04", "DSP-05", "I&S-08"],

    # ---- CM ----
    "CM-01": ["CCC-01", "I&S-01", "MDS-01", "UEM-01"],
    "CM-02": ["AIS-06", "CCC-06", "CCC-07", "I&S-04", "I&S-05", "UEM-03", "UEM-05", "UEM-07"],
    "CM-03": ["AIS-06", "AIS-09", "AIS-11", "CCC-01", "CCC-02", "CCC-03", "CCC-05", "CCC-07", "CCC-09", "CEK-05", "I&S-07", "MDS-04", "MDS-06", "MDS-11", "UEM-05"],
    "CM-04": ["CCC-02", "DSP-15", "I&S-05"],
    "CM-05": ["CCC-03", "CCC-04", "IAM-19", "MDS-04", "MDS-07"],
    "CM-06": ["CCC-06", "I&S-04", "UEM-05", "UEM-07"],
    "CM-07": ["UEM-02", "UEM-10"],
    "CM-08": ["CEK-21", "DCS-05", "DCS-06", "DCS-08", "DSP-03", "MDS-02", "STA-07", "STA-15", "UEM-04", "UEM-12"],
    "CM-09": ["CCC-01", "CCC-03", "MDS-11"],
    "CM-11": ["UEM-02"],

    # ---- CP ----
    "CP-01": ["BCR-01"],
    "CP-02": ["BCR-01", "BCR-02", "BCR-03", "BCR-04", "BCR-05", "BCR-07", "BCR-09", "I&S-02"],
    "CP-03": ["BCR-04", "BCR-06"],
    "CP-04": ["BCR-04", "BCR-06", "BCR-10"],
    "CP-06": ["BCR-08"],
    "CP-07": ["BCR-03", "BCR-11"],
    "CP-08": ["BCR-03", "BCR-07", "BCR-11"],
    "CP-09": ["BCR-08", "CCC-09", "CEK-18", "CEK-20"],
    "CP-10": ["BCR-09", "CCC-09"],

    # ---- IA ----
    "IA-01": ["IAM-01", "IAM-02"],
    "IA-02": ["IAM-10", "IAM-13", "IAM-14", "IAM-15", "IAM-17"],
    "IA-03": ["DCS-08", "IAM-18"],
    "IA-04": ["IAM-03", "IAM-06", "IAM-13"],
    "IA-05": ["IAM-02", "IAM-06", "IAM-14", "IAM-15"],
    "IA-08": ["IAM-14"],

    # ---- IR ----
    "IR-01": ["BCR-09", "CEK-19", "SEF-01", "SEF-02", "SEF-08", "SEF-09"],
    "IR-02": ["DCS-11", "SEF-03"],
    "IR-03": ["BCR-10", "SEF-04"],
    "IR-04": ["LOG-05", "SEF-02", "SEF-03", "SEF-05", "SEF-06", "SEF-09"],
    "IR-05": ["SEF-06"],
    "IR-06": ["BCR-07", "CEK-19", "DSP-18", "SEF-07", "SEF-08", "SEF-09"],
    "IR-07": ["SEF-07"],
    "IR-08": ["SEF-01", "SEF-03"],

    # ---- MP ----
    "MP-01": ["DCS-04"],
    "MP-02": ["HRS-03"],
    "MP-04": ["DCS-05"],
    "MP-05": ["DCS-02", "DCS-04"],
    "MP-06": ["CEK-14", "DCS-01", "DSP-02", "DSP-16", "UEM-13"],

    # ---- PE ----
    "PE-01": ["DCS-01", "DCS-02", "DCS-03"],
    "PE-02": ["DCS-03", "DCS-09"],
    "PE-03": ["DCS-03", "DCS-07", "DCS-09"],
    "PE-04": ["DCS-12"],
    "PE-05": ["DCS-06", "DCS-15"],
    "PE-06": ["DCS-07", "DCS-10", "DCS-11"],
    "PE-08": ["DCS-10"],
    "PE-09": ["DCS-12", "DCS-14"],
    "PE-10": ["DCS-14"],
    "PE-11": ["BCR-11", "DCS-14"],
    "PE-13": ["DCS-13"],
    "PE-14": ["DCS-13"],
    "PE-15": ["DCS-13"],
    "PE-16": ["DCS-02"],
    "PE-17": ["HRS-04"],
    "PE-18": ["DCS-15"],

    # ---- PL ----
    "PL-01": ["DSP-01", "GRC-01", "GRC-03", "MDS-01"],
    "PL-02": ["BCR-05", "CCC-08", "CEK-02", "DSP-05", "GRC-04", "GRC-06", "GRC-07", "HRS-09", "I&S-08"],
    "PL-04": ["HRS-02", "HRS-08", "HRS-13"],
    "PL-07": ["BCR-05"],

    # ---- PM ----
    "PM-01": ["GRC-01", "GRC-03", "GRC-05", "GRC-06", "GRC-07", "GRC-09", "GRC-10", "GRC-12", "GRC-14", "SEF-02", "STA-01", "STA-13"],
    "PM-02": ["GRC-01", "GRC-05", "GRC-06", "GRC-10", "GRC-13", "HRS-09", "HRS-14", "HRS-15", "STA-04"],
    "PM-03": ["GRC-05"],
    "PM-05": ["DSP-03", "DSP-06"],
    "PM-06": ["AIS-03", "SEF-05", "TVM-09", "TVM-10"],
    "PM-09": ["CCC-08", "GRC-02", "GRC-09", "GRC-10", "GRC-11", "GRC-14", "MDS-13"],
    "PM-15": ["GRC-08", "GRC-15", "SEF-08"],
    "PM-16": ["GRC-08", "GRC-15"],

    # ---- PS ----
    "PS-01": ["CEK-02", "GRC-13", "HRS-01", "HRS-07", "HRS-09", "HRS-15"],
    "PS-03": ["HRS-01"],
    "PS-04": ["HRS-05", "HRS-06", "IAM-07"],
    "PS-05": ["HRS-06", "IAM-07"],
    "PS-06": ["HRS-07", "HRS-08", "HRS-10", "HRS-13"],
    "PS-09": ["HRS-10"],

    # ---- PT ----
    "PT-01": ["DSP-01", "DSP-06", "DSP-07", "DSP-08", "DSP-09", "DSP-13", "DSP-14", "DSP-16", "DSP-18", "DSP-19", "DSP-20", "DSP-21", "DSP-22", "DSP-23", "HRS-12", "MDS-09"],
    "PT-02": ["DSP-08", "DSP-12"],
    "PT-03": ["DSP-03", "DSP-08", "DSP-12", "DSP-15", "DSP-20", "DSP-24", "MDS-09"],
    "PT-04": ["DSP-11", "DSP-23"],
    "PT-05": ["DSP-11"],
    "PT-06": ["DSP-11"],

    # ---- RA ----
    "RA-01": ["GRC-02", "GRC-09", "GRC-11", "TVM-01"],
    "RA-02": ["DCS-05", "DSP-04"],
    "RA-03": ["A&A-03", "BCR-02", "CEK-06", "CEK-07", "DSP-09", "DSP-21", "GRC-02", "GRC-11", "GRC-14", "MDS-12", "MDS-13", "STA-08", "STA-14", "TVM-08", "TVM-11"],
    "RA-05": ["AIS-05", "AIS-07", "AIS-10", "MDS-03", "MDS-08", "TVM-01", "TVM-03", "TVM-05", "TVM-06", "TVM-07", "TVM-08", "TVM-09", "TVM-10", "TVM-11", "TVM-12", "TVM-13"],
    "RA-07": ["A&A-03", "A&A-06", "CEK-07"],
    "RA-08": ["DSP-09"],
    "RA-09": ["BCR-02"],

    # ---- SA ----
    "SA-01": ["AIS-01", "I&S-01", "IPY-01", "STA-01"],
    "SA-03": ["AIS-04", "AIS-06", "AIS-11", "AIS-15", "I&S-07", "MDS-02", "MDS-04", "MDS-10", "MDS-11"],
    "SA-04": ["CCC-05", "DSP-13", "I&S-07", "IPY-01", "IPY-02", "IPY-03", "IPY-04", "MDS-12", "STA-03", "STA-09", "STA-10", "STA-15", "UEM-03"],
    "SA-08": ["AIS-01", "AIS-02", "AIS-04", "AIS-08", "AIS-10", "AIS-14", "AIS-15", "DSP-07", "DSP-20", "MDS-01", "MDS-09", "MDS-10"],
    "SA-09": ["DSP-13", "DSP-14", "DSP-19", "DSP-23", "IPY-02", "IPY-03", "MDS-12", "STA-06", "STA-09", "STA-12", "STA-16", "UEM-14"],
    "SA-11": ["AIS-02", "AIS-03", "AIS-04", "AIS-05", "AIS-07", "AIS-09", "AIS-10", "AIS-13", "AIS-15", "CCC-02", "MDS-03", "MDS-08", "TVM-05", "TVM-12"],
    "SA-15": ["AIS-02", "AIS-04", "AIS-11", "MDS-10"],

    # ---- SC ----
    "SC-01": ["CEK-01", "I&S-01"],
    "SC-03": ["I&S-06"],
    "SC-05": ["I&S-02", "I&S-09"],
    "SC-06": ["I&S-02"],
    "SC-07": ["AIS-08", "I&S-03", "I&S-05", "I&S-06", "I&S-08", "I&S-09", "IAM-17", "UEM-10", "UEM-11"],
    "SC-08": ["CEK-03", "DSP-10", "DSP-17", "I&S-03", "IPY-03"],
    "SC-12": ["CEK-01", "CEK-02", "CEK-08", "CEK-09", "CEK-10", "CEK-11", "CEK-12", "CEK-13", "CEK-14", "CEK-15", "CEK-16", "CEK-17", "CEK-18", "CEK-19", "CEK-20", "CEK-21"],
    "SC-13": ["AIS-14", "CEK-01", "CEK-03", "CEK-04", "CEK-05", "CEK-06", "CEK-07", "CEK-10", "DSP-10", "DSP-22", "LOG-10", "MDS-06", "UEM-08"],
    "SC-17": ["CEK-13"],
    "SC-28": ["CEK-03", "DSP-07", "DSP-17", "UEM-08"],
    "SC-42": ["UEM-01"],

    # ---- SI ----
    "SI-01": ["AIS-01", "MDS-13", "TVM-01", "TVM-02"],
    "SI-02": ["I&S-04", "TVM-03", "TVM-04", "UEM-07"],
    "SI-03": ["TVM-02", "TVM-04", "UEM-09"],
    "SI-04": ["AIS-12", "I&S-09", "LOG-03", "LOG-05", "LOG-13", "LOG-14", "MDS-05", "TVM-11", "TVM-13", "UEM-11"],
    "SI-05": ["TVM-07"],
    "SI-07": ["AIS-09", "AIS-13", "AIS-14", "CCC-04", "CCC-07", "MDS-06", "MDS-08"],
    "SI-12": ["DSP-02", "DSP-16", "DSP-21", "DSP-24"],

    # ---- SR ----
    "SR-01": ["STA-01", "STA-02", "STA-03", "STA-04", "STA-05", "STA-06", "STA-07", "STA-08", "STA-10", "STA-12", "STA-13", "STA-14", "STA-15", "STA-16", "UEM-14"],
    "SR-02": ["STA-02", "STA-07", "STA-08", "STA-16"],
    "SR-03": ["STA-02", "STA-08", "STA-14"],
    "SR-04": ["TVM-05"],
}


def load_manifest():
    """Load _manifest.json and return list of control entries."""
    manifest_path = os.path.join(CONTROLS_DIR, "_manifest.json")
    with open(manifest_path, "r") as f:
        data = json.load(f)
    return data["controls"]


def update_control_file(filepath, control_id):
    """Add 'csa_aicm' key to compliance_mappings in a control JSON file."""
    with open(filepath, "r") as f:
        data = json.load(f, object_pairs_hook=OrderedDict)

    if "compliance_mappings" not in data:
        print(f"  WARNING: {control_id} has no compliance_mappings - skipping")
        return 0

    mappings = AICM_MAPPINGS.get(control_id, [])

    # Rebuild OrderedDict with csa_aicm added at end
    cm = data["compliance_mappings"]
    new_cm = OrderedDict()
    for key, val in cm.items():
        new_cm[key] = val
    # Remove old key if present
    new_cm.pop("csa_aicm", None)
    new_cm["csa_aicm"] = mappings
    data["compliance_mappings"] = new_cm

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return len(mappings)


def main():
    controls = load_manifest()
    total_refs = 0
    controls_with_mappings = 0
    controls_empty = 0

    # Count by AICM domain
    domain_counts = {}

    for entry in controls:
        control_id = entry["id"]
        filename = entry["file"]
        filepath = os.path.join(CONTROLS_DIR, filename)

        if not os.path.exists(filepath):
            print(f"  WARNING: File not found: {filepath}")
            continue

        ref_count = update_control_file(filepath, control_id)
        total_refs += ref_count
        if ref_count > 0:
            controls_with_mappings += 1
        else:
            controls_empty += 1

        # Count by AICM domain
        for ref in AICM_MAPPINGS.get(control_id, []):
            domain = ref.rsplit("-", 1)[0]
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

    print(f"\n{'='*60}")
    print(f"CSA AICM v1.0.3 Compliance Mapping Summary")
    print(f"{'='*60}")
    print(f"Total controls processed:          {len(controls)}")
    print(f"Controls with AICM mappings:       {controls_with_mappings}")
    print(f"Controls with empty mappings:       {controls_empty}")
    print(f"{'='*60}")
    print(f"Total AICM references:             {total_refs}")
    print(f"{'='*60}")

    # References by AICM domain
    print(f"\nReferences by AICM domain:")
    for domain, count in sorted(domain_counts.items()):
        print(f"  {domain}: {count}")

    # List mapped controls
    mapped_ids = sorted(AICM_MAPPINGS.keys())
    print(f"\nNIST controls with AICM mappings ({len(mapped_ids)}):")
    for cid in mapped_ids:
        refs = AICM_MAPPINGS[cid]
        print(f"  {cid}: {', '.join(refs)}")


if __name__ == "__main__":
    main()
