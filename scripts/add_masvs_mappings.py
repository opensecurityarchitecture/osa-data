#!/usr/bin/env python3
"""
Add OWASP MASVS v2.1 compliance mappings to NIST 800-53 Rev 5 control files.

OWASP Mobile Application Security Verification Standard v2.1
Published: 2024
Standard type: Voluntary community standard

8 requirement groups, 24 requirements:
  MASVS-STORAGE   (2) - Sensitive data storage and leakage prevention
  MASVS-CRYPTO    (2) - Cryptographic algorithm and key management
  MASVS-AUTH      (3) - Authentication and authorization
  MASVS-NETWORK   (2) - Network communication security
  MASVS-PLATFORM  (3) - Platform interaction security (IPC, WebView, UI)
  MASVS-CODE      (4) - Code quality, updates, dependencies, input validation
  MASVS-RESILIENCE(4) - Platform integrity, anti-tampering, anti-analysis
  MASVS-PRIVACY   (4) - Data minimisation, identification, transparency, control

Reference format: "MASVS-GROUP-N" (e.g., "MASVS-STORAGE-1")
"""

import json
import os
from collections import OrderedDict

CONTROLS_DIR = "/Users/russellwing/osa-workspace/data/controls"

# ============================================================
# MASVS v2.1 MAPPINGS per NIST 800-53 control
# ============================================================
# Derived from data/framework-coverage/owasp-masvs-v2.json (forward mapping).
# Each NIST control ID maps to the MASVS requirements it addresses.

MASVS_MAPPINGS = {
    # ---- AC: Access Control ----
    "AC-03": [
        "MASVS-STORAGE-1", "MASVS-AUTH-1", "MASVS-AUTH-3",
        "MASVS-PLATFORM-1", "MASVS-PRIVACY-1", "MASVS-PRIVACY-4"
    ],
    "AC-04": [
        "MASVS-STORAGE-2", "MASVS-PLATFORM-1", "MASVS-PLATFORM-2",
        "MASVS-PLATFORM-3"
    ],
    "AC-06": [
        "MASVS-PRIVACY-1"
    ],
    "AC-07": [
        "MASVS-AUTH-2"
    ],
    "AC-17": [
        "MASVS-NETWORK-1"
    ],

    # ---- AU: Audit and Accountability ----
    "AU-02": [
        "MASVS-STORAGE-2"
    ],

    # ---- CM: Configuration Management ----
    "CM-02": [
        "MASVS-CODE-1", "MASVS-CODE-2"
    ],
    "CM-03": [
        "MASVS-CODE-2"
    ],
    "CM-06": [
        "MASVS-CRYPTO-1", "MASVS-CRYPTO-2", "MASVS-CODE-1"
    ],
    "CM-07": [
        "MASVS-PLATFORM-1", "MASVS-PLATFORM-2"
    ],
    "CM-08": [
        "MASVS-CODE-3"
    ],
    "CM-14": [
        "MASVS-RESILIENCE-1", "MASVS-RESILIENCE-2"
    ],

    # ---- IA: Identification and Authentication ----
    "IA-02": [
        "MASVS-AUTH-1", "MASVS-AUTH-2", "MASVS-AUTH-3"
    ],
    "IA-05": [
        "MASVS-AUTH-1", "MASVS-AUTH-2", "MASVS-NETWORK-2"
    ],
    "IA-07": [
        "MASVS-AUTH-2"
    ],
    "IA-08": [
        "MASVS-AUTH-1"
    ],
    "IA-10": [
        "MASVS-AUTH-3"
    ],
    "IA-11": [
        "MASVS-AUTH-3"
    ],

    # ---- MP: Media Protection ----
    "MP-06": [
        "MASVS-STORAGE-1"
    ],

    # ---- PE: Physical and Environmental Protection ----
    "PE-18": [
        "MASVS-PLATFORM-3"
    ],

    # ---- PL: Planning ----
    "PL-04": [
        "MASVS-PRIVACY-3"
    ],

    # ---- PM: Program Management ----
    "PM-25": [
        "MASVS-PRIVACY-1", "MASVS-PRIVACY-2"
    ],

    # ---- PT: PII Processing and Transparency ----
    "PT-02": [
        "MASVS-PRIVACY-1", "MASVS-PRIVACY-2"
    ],
    "PT-03": [
        "MASVS-PRIVACY-1", "MASVS-PRIVACY-3", "MASVS-PRIVACY-4"
    ],
    "PT-04": [
        "MASVS-PRIVACY-3", "MASVS-PRIVACY-4"
    ],
    "PT-05": [
        "MASVS-PRIVACY-3", "MASVS-PRIVACY-4"
    ],
    "PT-06": [
        "MASVS-PRIVACY-2", "MASVS-PRIVACY-4"
    ],

    # ---- RA: Risk Assessment ----
    "RA-05": [
        "MASVS-CODE-3"
    ],

    # ---- SA: System and Services Acquisition ----
    "SA-08": [
        "MASVS-CRYPTO-1", "MASVS-CRYPTO-2", "MASVS-PRIVACY-2",
        "MASVS-RESILIENCE-2", "MASVS-RESILIENCE-3", "MASVS-RESILIENCE-4"
    ],
    "SA-11": [
        "MASVS-PLATFORM-2", "MASVS-CODE-3", "MASVS-CODE-4",
        "MASVS-RESILIENCE-1"
    ],
    "SA-22": [
        "MASVS-CODE-1", "MASVS-CODE-2"
    ],

    # ---- SC: System and Communications Protection ----
    "SC-04": [
        "MASVS-STORAGE-2", "MASVS-PLATFORM-3"
    ],
    "SC-07": [
        "MASVS-NETWORK-1", "MASVS-PLATFORM-1", "MASVS-PLATFORM-2"
    ],
    "SC-08": [
        "MASVS-NETWORK-1", "MASVS-NETWORK-2"
    ],
    "SC-12": [
        "MASVS-STORAGE-1", "MASVS-CRYPTO-2"
    ],
    "SC-13": [
        "MASVS-CRYPTO-1", "MASVS-NETWORK-1", "MASVS-AUTH-2",
        "MASVS-RESILIENCE-2", "MASVS-RESILIENCE-3", "MASVS-RESILIENCE-4"
    ],
    "SC-17": [
        "MASVS-CRYPTO-2", "MASVS-NETWORK-2"
    ],
    "SC-18": [
        "MASVS-CODE-4"
    ],
    "SC-23": [
        "MASVS-AUTH-1", "MASVS-AUTH-3", "MASVS-NETWORK-1",
        "MASVS-NETWORK-2"
    ],
    "SC-28": [
        "MASVS-STORAGE-1", "MASVS-STORAGE-2"
    ],

    # ---- SI: System and Information Integrity ----
    "SI-02": [
        "MASVS-CODE-1", "MASVS-CODE-2", "MASVS-CODE-3"
    ],
    "SI-04": [
        "MASVS-RESILIENCE-4"
    ],
    "SI-06": [
        "MASVS-RESILIENCE-1"
    ],
    "SI-07": [
        "MASVS-RESILIENCE-1", "MASVS-RESILIENCE-2",
        "MASVS-RESILIENCE-3", "MASVS-RESILIENCE-4"
    ],
    "SI-10": [
        "MASVS-PLATFORM-1", "MASVS-CODE-4"
    ],
    "SI-11": [
        "MASVS-STORAGE-2", "MASVS-PLATFORM-3"
    ],
    "SI-16": [
        "MASVS-CODE-4"
    ],

    # ---- SR: Supply Chain Risk Management ----
    "SR-03": [
        "MASVS-CODE-3"
    ],
}


def load_manifest():
    """Load _manifest.json and return list of control entries."""
    manifest_path = os.path.join(CONTROLS_DIR, "_manifest.json")
    with open(manifest_path, "r") as f:
        data = json.load(f)
    return data["controls"]


def update_control_file(filepath, control_id):
    """Add 'owasp_masvs' key to compliance_mappings in a control JSON file."""
    with open(filepath, "r") as f:
        data = json.load(f, object_pairs_hook=OrderedDict)

    if "compliance_mappings" not in data:
        print(f"  WARNING: {control_id} has no compliance_mappings - skipping")
        return 0

    mappings = MASVS_MAPPINGS.get(control_id, [])

    # Rebuild OrderedDict with owasp_masvs added at end
    cm = data["compliance_mappings"]
    new_cm = OrderedDict()
    for key, val in cm.items():
        new_cm[key] = val
    new_cm["owasp_masvs"] = mappings
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

    # Count by MASVS group
    group_counts = {}

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

        # Count by MASVS group
        for ref in MASVS_MAPPINGS.get(control_id, []):
            group = "-".join(ref.split("-")[:-1])  # e.g., MASVS-STORAGE
            group_counts[group] = group_counts.get(group, 0) + 1

    print(f"\n{'='*60}")
    print(f"OWASP MASVS v2.1 Compliance Mapping Summary")
    print(f"{'='*60}")
    print(f"Total controls processed:         {len(controls)}")
    print(f"Controls with MASVS mappings:     {controls_with_mappings}")
    print(f"Controls with empty mappings:     {controls_empty}")
    print(f"{'='*60}")
    print(f"Total MASVS references:           {total_refs}")
    print(f"{'='*60}")

    # References by MASVS group
    print(f"\nReferences by MASVS group:")
    for group, count in sorted(group_counts.items()):
        print(f"  {group}: {count}")

    # List mapped controls
    mapped_ids = sorted(MASVS_MAPPINGS.keys())
    print(f"\nNIST controls with MASVS mappings ({len(mapped_ids)}):")
    for cid in mapped_ids:
        refs = MASVS_MAPPINGS[cid]
        print(f"  {cid}: {', '.join(refs)}")


if __name__ == "__main__":
    main()
