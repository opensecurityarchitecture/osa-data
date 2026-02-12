#!/usr/bin/env python3
"""Generate OSFI B-13 coverage analysis JSON.

OSFI B-13 is the Canadian Office of the Superintendent of Financial
Institutions guideline on Technology and Cyber Risk Management. Reads all
SP 800-53 Rev 5 control files via _manifest.json, builds reverse mappings
from osfi_b13 clause IDs to controls, then produces a framework-coverage
JSON with expert assessments.

Output: data/framework-coverage/osfi-b13.json
"""

import json
import os
import re
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONTROLS_DIR = os.path.join(SCRIPT_DIR, '..', 'data', 'controls')
COVERAGE_DIR = os.path.join(SCRIPT_DIR, '..', 'data', 'framework-coverage')
OUTPUT_FILE = os.path.join(COVERAGE_DIR, 'osfi-b13.json')

FRAMEWORK_KEY = "osfi_b13"


def natural_sort_key(s):
    """Sort key that handles mixed alpha-numeric clause IDs naturally."""
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r'(\d+)', s)
    ]


def load_manifest():
    with open(os.path.join(CONTROLS_DIR, '_manifest.json')) as f:
        return json.load(f)


def build_reverse_mappings():
    """Read every control JSON and build clause -> [control_ids] mapping."""
    manifest = load_manifest()
    reverse = defaultdict(list)

    for ctrl_entry in manifest['controls']:
        ctrl_file = os.path.join(CONTROLS_DIR, ctrl_entry['file'])
        with open(ctrl_file) as f:
            ctrl = json.load(f)
        clauses = ctrl.get('compliance_mappings', {}).get(FRAMEWORK_KEY, [])
        for clause_id in clauses:
            reverse[clause_id].append(ctrl['id'])

    for clause_id in reverse:
        reverse[clause_id] = sorted(reverse[clause_id])

    return reverse


# ---- Expert clause definitions for OSFI B-13 ----
# B-13 is structured in four domains:
#   1. Governance and risk management
#   2. Technology operations and resilience
#   3. Cyber security
#   4. Third-party provider technology risk

CLAUSE_DEFINITIONS = [
    # --- Domain 1: Governance (B-13.1.x) ---
    {
        "id": "B-13.1.1",
        "title": "Technology and cyber risk governance, accountability, and culture",
        "coverage_pct": 70,
        "rationale": "AC-05 separation of duties; AT-01 through AT-05 awareness and training; PL-04 rules of behaviour; PS-01 through PS-08 personnel security. Covers personnel governance, training, and accountability.",
        "gaps": "OSFI B-13 requires board and senior management accountability for technology and cyber risk with a defined risk appetite. SP 800-53 covers personnel security and training comprehensively but Canadian regulatory board-level accountability, risk appetite statement, and technology risk culture requirements are not addressed."
    },
    {
        "id": "B-13.1.2",
        "title": "Technology and cyber risk strategy",
        "coverage_pct": 65,
        "rationale": "PL-01 security planning policy; PL-02 system security plan; PL-03 plan update; PL-06 security-related activity planning; SA-02 resource allocation.",
        "gaps": "OSFI B-13 requires a documented technology and cyber risk strategy aligned with business objectives and risk appetite. SP 800-53 covers security planning and resource allocation but not Canadian-specific strategic alignment with business objectives, regulatory expectations, or OSFI risk appetite framework."
    },
    {
        "id": "B-13.1.3",
        "title": "Technology and cyber risk management framework",
        "coverage_pct": 75,
        "rationale": "Extensive coverage via policy controls (AC-01, AU-01, CA-01, IA-01, PL-01, PL-02, PL-03, PT-01, RA-01, SC-01, SI-01); CA-02/CA-04/CA-05/CA-06/CA-07 security assessment and authorization; PL-05 privacy impact; PT-02/PT-03 PII processing; RA-02/RA-03/RA-04 risk assessment.",
        "gaps": "OSFI B-13 requires a comprehensive technology and cyber risk management framework with regular OSFI reporting. SP 800-53 provides strong risk management through the RA and CA families but Canadian OSFI-specific risk management framework expectations, risk appetite integration, and OSFI reporting requirements need supplementation."
    },
    {
        "id": "B-13.1.4",
        "title": "Technology and cyber risk reporting",
        "coverage_pct": 55,
        "rationale": "CA-05 POA&M; IR-06 incident reporting; RA-04 risk assessment update.",
        "gaps": "OSFI B-13 requires regular reporting to senior management and the board on technology and cyber risk posture, including OSFI self-assessment reporting. SP 800-53 covers risk tracking and incident reporting but OSFI-specific board reporting cadence, risk posture dashboards, and OSFI self-assessment reporting are regulatory requirements not addressed."
    },
    # --- Domain 2: Technology operations and resilience (B-13.2.x) ---
    {
        "id": "B-13.2.1",
        "title": "Technology asset management",
        "coverage_pct": 70,
        "rationale": "CM-08 component inventory; PE-16 delivery and removal; SA-03 lifecycle support.",
        "gaps": "OSFI B-13 requires comprehensive technology asset management including lifecycle management and end-of-life planning. SP 800-53 covers component inventory and lifecycle support but OSFI-specific asset lifecycle management and end-of-life risk management need supplementation."
    },
    {
        "id": "B-13.2.2",
        "title": "Technology architecture and standards",
        "coverage_pct": 75,
        "rationale": "CA-03 system connections; CM-01/CM-02/CM-06/CM-07 configuration management; SA-01/SA-03/SA-05/SA-06/SA-07/SA-08 system acquisition and architecture; SC-02/SC-03/SC-22 system protection.",
        "gaps": "OSFI B-13 requires documented technology architecture aligned with the institution's risk appetite. SP 800-53 covers configuration management and security engineering principles but OSFI-specific architectural standards and Canadian financial sector technology standards need supplementation."
    },
    {
        "id": "B-13.2.3",
        "title": "Technology change management",
        "coverage_pct": 85,
        "rationale": "CM-01/CM-03/CM-04/CM-05 configuration management and change control; MA-01 through MA-05 system maintenance; SA-01/SA-04/SA-10 system acquisition and developer configuration management.",
        "gaps": "Minor: SP 800-53 provides comprehensive change management through CM and MA families. OSFI B-13 change management requirements well addressed."
    },
    {
        "id": "B-13.2.4",
        "title": "Technology vulnerability and patch management",
        "coverage_pct": 85,
        "rationale": "MA-06 timely maintenance; RA-05 vulnerability scanning; SI-01 system integrity policy; SI-02 flaw remediation; SI-05 security alerts and advisories.",
        "gaps": "Minor: SP 800-53 provides comprehensive vulnerability and patch management through RA-05, SI-02, and SI-05. OSFI B-13 vulnerability management requirements well addressed."
    },
    {
        "id": "B-13.2.5",
        "title": "Technology incident management",
        "coverage_pct": 80,
        "rationale": "IR-01 through IR-07 incident response family. Comprehensive incident management coverage.",
        "gaps": "OSFI B-13 requires incident management with OSFI notification for significant technology incidents. SP 800-53 IR family provides strong incident management but OSFI-specific notification timelines and Canadian regulatory reporting requirements need supplementation."
    },
    {
        "id": "B-13.2.6",
        "title": "Technology resilience and disaster recovery",
        "coverage_pct": 85,
        "rationale": "CP-01 through CP-10 contingency planning family; PE-09 through PE-18 physical environmental protection; SC-05 denial of service protection; SC-06 resource priority.",
        "gaps": "Minor: SP 800-53 provides comprehensive resilience and disaster recovery through CP and PE families. OSFI B-13 operational resilience requirements well addressed at the technical level."
    },
    # --- Domain 3: Cyber security (B-13.3.x) ---
    {
        "id": "B-13.3.1",
        "title": "Cyber risk identification and assessment",
        "coverage_pct": 80,
        "rationale": "CM-08 component inventory; RA-02 security categorisation; RA-03 risk assessment; RA-05 vulnerability scanning.",
        "gaps": "OSFI B-13 requires cyber-specific risk identification and assessment including threat intelligence. SP 800-53 RA family covers risk assessment but OSFI-specific cyber risk assessment methodology and Canadian threat landscape considerations may need supplementation."
    },
    {
        "id": "B-13.3.2",
        "title": "Cyber security controls",
        "coverage_pct": 90,
        "rationale": "Extensive coverage via AC family (AC-01 through AC-20) access control; AU-09 audit protection; CA-03 system connections; CM-05/CM-06/CM-07 configuration management; IA family (IA-01 through IA-07) identification and authentication; MA-04 remote maintenance; MP-01 through MP-06 media protection; PE-01 through PE-19 physical protection; PS-04/PS-05 personnel; PT-01/PT-07 PII; SA-07/SA-08/SA-10/SA-11 system acquisition; SC family (SC-01 through SC-23) system and communications protection; SI family (SI-03/SI-07/SI-08/SI-09/SI-10/SI-11/SI-12) system integrity.",
        "gaps": "Minor: SP 800-53 provides comprehensive cyber security controls. Very strong alignment with OSFI B-13 cyber security control requirements across access control, network security, cryptography, endpoint protection, and data security."
    },
    {
        "id": "B-13.3.3",
        "title": "Cyber security monitoring and detection",
        "coverage_pct": 85,
        "rationale": "AC-13 supervision and review; AT-05 security contacts; AU-01 through AU-11 audit family; CA-07 continuous monitoring; CM-04 monitoring changes; IR-05 incident monitoring; PE-06/PE-08 physical monitoring; SI-03/SI-04/SI-05/SI-06/SI-07/SI-08 system integrity monitoring.",
        "gaps": "Minor: SP 800-53 provides comprehensive security monitoring through AU, SI, and CA families. OSFI B-13 monitoring requirements well addressed."
    },
    {
        "id": "B-13.3.4",
        "title": "Cyber incident response",
        "coverage_pct": 75,
        "rationale": "CP-10 system recovery; IR-01 through IR-04/IR-06/IR-07 incident response. Strong incident response coverage.",
        "gaps": "OSFI B-13 requires cyber incident response with OSFI notification for significant incidents. SP 800-53 IR family provides strong cyber incident response but OSFI-specific notification requirements, Canadian CCIRC coordination, and regulatory escalation requirements need supplementation."
    },
    {
        "id": "B-13.3.5",
        "title": "Cyber security testing",
        "coverage_pct": 80,
        "rationale": "CA-02 security assessments; CA-04 security certification; CP-04 contingency testing; IR-03 incident response testing; SA-11 developer security testing; SI-06 security functionality verification.",
        "gaps": "OSFI B-13 requires regular cyber security testing including vulnerability assessments and penetration testing. SP 800-53 covers security testing through CA and SA families. OSFI-specific testing cadence and Canadian financial sector testing requirements may need supplementation."
    },
    # --- Domain 4: Third-party provider technology risk (B-13.4.x) ---
    {
        "id": "B-13.4.1",
        "title": "Third-party technology risk management",
        "coverage_pct": 70,
        "rationale": "AC-20 external systems; MA-05 maintenance personnel; PS-07 third-party personnel; SA-04 acquisitions; SA-09 external services; SR-01 through SR-12 supply chain risk management family. Comprehensive supply chain and vendor management.",
        "gaps": "OSFI B-13 requires comprehensive third-party technology risk management including concentration risk assessment, Canadian regulatory considerations, and OSFI notification for material outsourcing. SP 800-53 SR family covers supply chain risk management but OSFI-specific third-party governance, concentration risk, and Canadian regulatory outsourcing notification requirements need supplementation."
    },
    {
        "id": "B-13.4.2",
        "title": "Third-party technology risk oversight and monitoring",
        "coverage_pct": 55,
        "rationale": "SA-09 external information system services. General third-party service monitoring.",
        "gaps": "OSFI B-13 requires ongoing oversight and monitoring of third-party technology providers including SLA monitoring, performance metrics, and regular risk reassessment. SP 800-53 SA-09 covers external service management but OSFI-specific ongoing monitoring requirements, third-party risk reassessment cadence, and Canadian regulatory third-party oversight expectations need supplementation."
    },
]


def generate_coverage():
    """Generate the framework coverage JSON file."""
    reverse = build_reverse_mappings()

    clauses = []
    for clause_def in CLAUSE_DEFINITIONS:
        clause_id = clause_def["id"]
        controls = reverse.get(clause_id, [])

        clauses.append({
            "id": clause_id,
            "title": clause_def["title"],
            "controls": controls,
            "coverage_pct": clause_def["coverage_pct"],
            "rationale": clause_def["rationale"],
            "gaps": clause_def["gaps"]
        })

    # Sort clauses naturally
    clauses.sort(key=lambda c: natural_sort_key(c["id"]))

    # Calculate summary
    total = len(clauses)
    coverages = [c["coverage_pct"] for c in clauses]
    avg = round(sum(coverages) / total, 1) if total > 0 else 0

    full_count = sum(1 for c in coverages if 85 <= c <= 100)
    substantial_count = sum(1 for c in coverages if 65 <= c <= 84)
    partial_count = sum(1 for c in coverages if 40 <= c <= 64)
    weak_count = sum(1 for c in coverages if 1 <= c <= 39)
    none_count = sum(1 for c in coverages if c == 0)

    output = {
        "$schema": "../schema/framework-coverage.schema.json",
        "framework_id": "osfi_b13",
        "framework_name": "OSFI B-13",
        "metadata": {
            "source": "SP800-53v5_Control_Mappings",
            "version": "1.0",
            "disclaimer": "Based on publicly available crosswalks and expert analysis. Validate with qualified assessors for compliance/audit use."
        },
        "weight_scale": {
            "full": {"min": 85, "max": 100, "label": "Fully addressed"},
            "substantial": {"min": 65, "max": 84, "label": "Well addressed, notable gaps"},
            "partial": {"min": 40, "max": 64, "label": "Partially addressed"},
            "weak": {"min": 1, "max": 39, "label": "Weakly addressed"},
            "none": {"min": 0, "max": 0, "label": "No mapping"}
        },
        "clauses": clauses,
        "summary": {
            "total_clauses": total,
            "average_coverage": avg,
            "full_count": full_count,
            "substantial_count": substantial_count,
            "partial_count": partial_count,
            "weak_count": weak_count,
            "none_count": none_count
        }
    }

    os.makedirs(COVERAGE_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
        f.write('\n')

    print(f"Generated {OUTPUT_FILE}")
    print(f"  Total clauses: {total}")
    print(f"  Average coverage: {avg}%")
    print(f"  Full: {full_count}  Substantial: {substantial_count}  "
          f"Partial: {partial_count}  Weak: {weak_count}  None: {none_count}")


if __name__ == '__main__':
    generate_coverage()
