#!/usr/bin/env python3
"""
Enrich controls with function classification (preventative/detective/corrective).

Based on NIST SP 800-53 control family primary functions, with individual
control overrides where a control's function differs from its family default.

Classification approach:
- Family-level default: most controls in a family share the same function
- Individual overrides: specific controls that differ from family default
  (e.g., AU-06 Audit Record Review is detective even though AU family default is detective;
   CA-07 Continuous Monitoring is detective within the mostly preventative CA family)

Idempotent: safe to run multiple times.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
CONTROLS_DIR = DATA_DIR / "controls"

# Family-level default function classification
# Based on NIST SP 800-53 control family primary purposes
FAMILY_DEFAULTS = {
    "AC": "preventative",  # Access Control — prevent unauthorized access
    "AT": "preventative",  # Awareness & Training — prevent through education
    "AU": "detective",     # Audit & Accountability — detect through logging/monitoring
    "CA": "detective",     # Assessment, Authorization & Monitoring — detect through assessment
    "CM": "preventative",  # Configuration Management — prevent through hardening
    "CP": "corrective",   # Contingency Planning — recover from incidents
    "IA": "preventative",  # Identification & Authentication — prevent unauthorized access
    "IR": "corrective",   # Incident Response — respond to and recover from incidents
    "MA": "preventative",  # Maintenance — prevent through system maintenance
    "MP": "preventative",  # Media Protection — prevent data exposure via media
    "PE": "preventative",  # Physical & Environmental — prevent physical threats
    "PL": "preventative",  # Planning — prevent through security planning
    "PM": "preventative",  # Program Management — prevent through governance
    "PS": "preventative",  # Personnel Security — prevent insider threats
    "PT": "preventative",  # PII Processing & Transparency — prevent privacy violations
    "RA": "detective",     # Risk Assessment — detect risks through assessment
    "SA": "preventative",  # System & Services Acquisition — prevent through secure acquisition
    "SC": "preventative",  # System & Communications Protection — prevent through technical controls
    "SI": "detective",     # System & Information Integrity — detect integrity issues
    "SR": "preventative",  # Supply Chain Risk Management — prevent supply chain threats
}

# Individual control overrides where a control differs from its family default
CONTROL_OVERRIDES = {
    # CA family — mostly detective, but some are preventative
    "CA-01": "preventative",  # Policy & Procedures — governance/preventative
    "CA-03": "preventative",  # Information Exchange — preventative controls on exchange
    "CA-05": "corrective",    # Plan of Action & Milestones — corrective remediation tracking
    "CA-06": "preventative",  # Authorization — preventative governance gate
    "CA-09": "preventative",  # Internal System Connections — preventative

    # SI family — mostly detective, but some are preventative or corrective
    "SI-01": "preventative",  # Policy & Procedures — governance/preventative
    "SI-02": "corrective",    # Flaw Remediation — corrective patching
    "SI-03": "detective",     # Malicious Code Protection — detection + prevention (classified detective)
    "SI-07": "detective",     # Software, Firmware & Information Integrity — detect tampering
    "SI-08": "preventative",  # Spam Protection — prevent spam delivery
    "SI-10": "preventative",  # Information Input Validation — prevent bad input
    "SI-11": "preventative",  # Error Handling — prevent information leakage
    "SI-12": "preventative",  # Information Management & Retention — prevent data loss
    "SI-13": "corrective",    # Predictable Failure Prevention — corrective/predictive
    "SI-14": "corrective",    # Non-Persistence — corrective refresh
    "SI-15": "preventative",  # Information Output Filtering — prevent data leakage
    "SI-16": "preventative",  # Memory Protection — prevent memory attacks
    "SI-17": "corrective",    # Fail-Safe Procedures — corrective fail-safe
    "SI-18": "corrective",    # Personally Identifiable Information Quality Operations — corrective data quality
    "SI-19": "preventative",  # De-identification — prevent PII exposure
    "SI-20": "preventative",  # Tainting — prevent/trace unauthorized data flow
    "SI-21": "preventative",  # Information Refresh — prevent stale data
    "SI-22": "preventative",  # Information Diversity — prevent single points of failure
    "SI-23": "preventative",  # Information Fragmentation — prevent full data compromise

    # RA family — mostly detective, but RA-01 is governance
    "RA-01": "preventative",  # Policy & Procedures — governance/preventative

    # AU family — mostly detective, but AU-01 is governance
    "AU-01": "preventative",  # Policy & Procedures — governance/preventative
    "AU-09": "preventative",  # Protection of Audit Information — prevent tampering with logs

    # CP family — mostly corrective, but CP-01/CP-02 are preventative planning
    "CP-01": "preventative",  # Policy & Procedures — governance/preventative
    "CP-02": "preventative",  # Contingency Plan — preventative planning

    # IR family — mostly corrective, but IR-01/IR-02 are preventative
    "IR-01": "preventative",  # Policy & Procedures — governance/preventative
    "IR-02": "preventative",  # Incident Response Training — preventative preparation

    # SC family — mostly preventative, but some are detective
    "SC-26": "detective",     # Decoys — detective honeypots

    # PE family — mostly preventative, but some are detective
    "PE-06": "detective",     # Monitoring Physical Access — detect physical access
    "PE-08": "detective",     # Visitor Access Records — detect/log visitor access
}


def get_function(control_id: str, family: str) -> str:
    """Get the function classification for a control."""
    if control_id in CONTROL_OVERRIDES:
        return CONTROL_OVERRIDES[control_id]
    return FAMILY_DEFAULTS.get(family, "preventative")


def main():
    enriched = 0
    errors = 0
    function_counts = {"preventative": 0, "detective": 0, "corrective": 0}

    for filepath in sorted(CONTROLS_DIR.glob("*.json")):
        if filepath.name.startswith("_"):
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        control_id = data["id"]
        family = data["family"]
        func = get_function(control_id, family)

        data["function"] = func
        function_counts[func] += 1

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')

        enriched += 1

    print(f"\nControl Function Enrichment Complete")
    print(f"  Enriched: {enriched} controls")
    print(f"  Preventative: {function_counts['preventative']}")
    print(f"  Detective: {function_counts['detective']}")
    print(f"  Corrective: {function_counts['corrective']}")


if __name__ == "__main__":
    main()
