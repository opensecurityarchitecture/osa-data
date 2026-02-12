#!/usr/bin/env python3
"""Generate FINMA Circular 2023/1 coverage analysis JSON.

FINMA Circular 2023/1 covers Operational Risks and Resilience for Swiss
financial institutions. Reads all SP 800-53 Rev 5 control files via
_manifest.json, builds reverse mappings from finma_circular clause IDs to
controls, then produces a framework-coverage JSON with expert assessments.

Output: data/framework-coverage/finma-circular.json
"""

import json
import os
import re
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONTROLS_DIR = os.path.join(SCRIPT_DIR, '..', 'data', 'controls')
COVERAGE_DIR = os.path.join(SCRIPT_DIR, '..', 'data', 'framework-coverage')
OUTPUT_FILE = os.path.join(COVERAGE_DIR, 'finma-circular.json')

FRAMEWORK_KEY = "finma_circular"


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


# ---- Expert clause definitions grouped by FINMA Circular domains ----
# Clauses are grouped into logical requirement areas. Individual marginal
# numbers (Randziffern) are clustered where they form coherent requirements.

CLAUSE_DEFINITIONS = [
    # --- Governance and strategy (FC2023/1.23-1.25) ---
    {
        "id": "FC2023/1.23",
        "title": "ICT governance framework and policies",
        "coverage_pct": 80,
        "rationale": "Comprehensive coverage via policy controls across all families (AC-01, AT-01, AU-01, CA-01, CM-01, CP-01, IA-01, IR-01, MA-01, MP-01, PE-01, PL-01, PL-02, PL-06, PS-01, RA-01, SA-01, SA-02, SC-01, SI-01, SR-01) plus CA-06 authorization and PL-03 plan update.",
        "gaps": "FINMA requires Swiss-specific governance with board-level accountability for ICT strategy. SP 800-53 covers comprehensive policy framework but not Swiss regulatory board oversight requirements or FINMA-specific governance reporting."
    },
    {
        "id": "FC2023/1.24",
        "title": "ICT strategy alignment with business strategy",
        "coverage_pct": 65,
        "rationale": "AC-01 and CA-01 policy; CA-06 authorization; PL-01/PL-02/PL-06 planning; SA-02 resource allocation.",
        "gaps": "FINMA requires ICT strategy to be approved by senior management and aligned with business strategy. SP 800-53 covers security planning and resource allocation but not Swiss-specific ICT strategy alignment with business objectives."
    },
    {
        "id": "FC2023/1.25",
        "title": "ICT strategy documentation and updates",
        "coverage_pct": 70,
        "rationale": "PL-02 system security plan; PL-03 plan update; SA-02 resource allocation.",
        "gaps": "FINMA requires regular ICT strategy review and update cycles with documented approval. SP 800-53 covers plan documentation and updates but not FINMA-specific strategy review cadence."
    },
    # --- ICT infrastructure and operations (FC2023/1.28-1.31) ---
    {
        "id": "FC2023/1.28",
        "title": "ICT infrastructure management and operations",
        "coverage_pct": 85,
        "rationale": "Extensive coverage via AU-04/AU-08 audit infrastructure; CM-01/CM-02/CM-06/CM-07/CM-08 configuration management; CP-08 telecommunications; MA family maintenance; PE family physical protection; SA-03/SA-05/SA-06/SA-08 system acquisition; SC-06/SC-20/SC-21/SC-22 network services.",
        "gaps": "Minor: FINMA-specific requirements for Swiss financial institution ICT infrastructure standards. SP 800-53 provides comprehensive technical infrastructure controls."
    },
    {
        "id": "FC2023/1.29",
        "title": "ICT capacity and performance management",
        "coverage_pct": 75,
        "rationale": "AU-04 audit storage capacity; CM-02/CM-06/CM-08 configuration management; MA-02/MA-03/MA-06 maintenance; SA-08 security engineering; SC-06 resource priority.",
        "gaps": "FINMA requires specific capacity planning and performance monitoring for financial services. SP 800-53 covers capacity and performance through multiple controls but not financial sector-specific SLA requirements."
    },
    {
        "id": "FC2023/1.30",
        "title": "ICT asset inventory",
        "coverage_pct": 85,
        "rationale": "CM-02 baseline configuration; CM-08 component inventory. Strong asset inventory coverage.",
        "gaps": "Minor: FINMA requires comprehensive ICT asset inventory. SP 800-53 CM-08 provides thorough component inventory capability."
    },
    {
        "id": "FC2023/1.31",
        "title": "ICT architecture documentation",
        "coverage_pct": 70,
        "rationale": "CM-02 baseline configuration. Covers system baseline documentation.",
        "gaps": "FINMA requires documented ICT architecture including network diagrams and system interconnections. SP 800-53 CM-02 covers baseline configuration but FINMA expects more comprehensive architectural documentation."
    },
    # --- ICT change management (FC2023/1.36-1.40) ---
    {
        "id": "FC2023/1.36",
        "title": "ICT change management framework",
        "coverage_pct": 85,
        "rationale": "CM-01 configuration management policy; CM-03/CM-04/CM-05 change control; MA-01/MA-02 maintenance policy; SA-01/SA-03/SA-05/SA-06/SA-07/SA-10/SA-11 acquisition and development lifecycle; SI-02 flaw remediation.",
        "gaps": "Minor: SP 800-53 provides comprehensive change management through CM and SA families."
    },
    {
        "id": "FC2023/1.37",
        "title": "Change control process and testing",
        "coverage_pct": 85,
        "rationale": "CM-03/CM-04/CM-05 change control and monitoring; SA-03 lifecycle support; SA-10 developer configuration management; SA-11 developer security testing.",
        "gaps": "Minor: FINMA requires formal testing and approval processes for changes. SP 800-53 CM and SA families cover this comprehensively."
    },
    {
        "id": "FC2023/1.38",
        "title": "Change impact analysis",
        "coverage_pct": 80,
        "rationale": "CM-03 configuration change control; CM-04 monitoring configuration changes; SA-10 developer configuration management.",
        "gaps": "Minor: FINMA requires documented change impact analysis. SP 800-53 CM-03 and CM-04 cover change analysis and monitoring."
    },
    {
        "id": "FC2023/1.39",
        "title": "Change approval and documentation",
        "coverage_pct": 80,
        "rationale": "CM-03 configuration change control; SA-10 developer configuration management.",
        "gaps": "Minor: FINMA requires formal change approval with documentation. SP 800-53 CM-03 provides change control with approval mechanisms."
    },
    {
        "id": "FC2023/1.40",
        "title": "Emergency change procedures",
        "coverage_pct": 75,
        "rationale": "CM-03 configuration change control including emergency changes.",
        "gaps": "FINMA requires specific emergency change procedures with retrospective approval. SP 800-53 CM-03 covers emergency changes but FINMA-specific financial sector urgency protocols need supplementation."
    },
    # --- Incident management (FC2023/1.41-1.47) ---
    {
        "id": "FC2023/1.41",
        "title": "Incident management framework",
        "coverage_pct": 80,
        "rationale": "AU-05 audit processing failures; IR-01 through IR-05/IR-07 incident response family; SI-11 error handling.",
        "gaps": "FINMA requires Swiss financial sector incident management aligned with FINMA reporting requirements. SP 800-53 IR family provides strong incident management but not FINMA-specific escalation and reporting timelines."
    },
    {
        "id": "FC2023/1.42",
        "title": "Incident classification and prioritisation",
        "coverage_pct": 75,
        "rationale": "IR-02 incident response training; IR-04 incident handling with classification.",
        "gaps": "FINMA requires specific incident classification for financial services including severity levels aligned with regulatory thresholds. SP 800-53 covers incident handling but not FINMA-specific classification criteria."
    },
    {
        "id": "FC2023/1.43",
        "title": "Incident response and escalation",
        "coverage_pct": 75,
        "rationale": "IR-04 incident handling including containment, eradication, and recovery.",
        "gaps": "FINMA requires specific escalation paths to senior management and board. SP 800-53 IR-04 covers incident handling but FINMA-specific escalation to Swiss governance structures needs supplementation."
    },
    {
        "id": "FC2023/1.44",
        "title": "Incident monitoring and tracking",
        "coverage_pct": 80,
        "rationale": "IR-05 incident monitoring; IR-06 incident reporting.",
        "gaps": "Minor: SP 800-53 IR-05 and IR-06 cover incident monitoring and reporting well."
    },
    {
        "id": "FC2023/1.45",
        "title": "Incident reporting to FINMA",
        "coverage_pct": 55,
        "rationale": "IR-06 incident reporting. General reporting framework applies.",
        "gaps": "FINMA requires specific incident reporting to FINMA within defined timeframes for material ICT incidents. SP 800-53 IR-06 covers incident reporting but FINMA-specific reporting timelines, formats, and thresholds are regulatory requirements not addressed."
    },
    {
        "id": "FC2023/1.46",
        "title": "Incident notification to affected parties",
        "coverage_pct": 60,
        "rationale": "IR-06 incident reporting.",
        "gaps": "FINMA requires notification of affected clients and counterparties. SP 800-53 IR-06 covers reporting but not Swiss financial sector client notification requirements."
    },
    {
        "id": "FC2023/1.47",
        "title": "Incident lessons learned",
        "coverage_pct": 60,
        "rationale": "IR-06 incident reporting. Post-incident review covered implicitly.",
        "gaps": "FINMA requires formal lessons learned process and documented improvements. SP 800-53 IR-06 covers reporting but post-incident review and improvement processes are less explicitly defined."
    },
    # --- Personnel and training (FC2023/1.48-1.53) ---
    {
        "id": "FC2023/1.48",
        "title": "ICT personnel and security awareness framework",
        "coverage_pct": 80,
        "rationale": "AT-01 through AT-05 awareness and training family; PL-01/PL-02/PL-04/PL-06 planning; PS-01/PS-02/PS-03/PS-06/PS-08 personnel security; RA-01 risk assessment policy.",
        "gaps": "Minor: FINMA requires Swiss financial sector-specific personnel security. SP 800-53 provides comprehensive personnel and training controls."
    },
    {
        "id": "FC2023/1.49",
        "title": "ICT security training programme",
        "coverage_pct": 80,
        "rationale": "AT-01 training policy; AT-02 security awareness; AT-03 security training; AT-04 training records; PL-04 rules of behaviour.",
        "gaps": "Minor: FINMA requires role-based training specific to financial services. SP 800-53 AT family covers training comprehensively."
    },
    {
        "id": "FC2023/1.50",
        "title": "Security awareness for all staff",
        "coverage_pct": 85,
        "rationale": "AT-02 security awareness; AT-03 security training. Strong awareness coverage.",
        "gaps": "Minor: SP 800-53 AT-02 and AT-03 provide comprehensive security awareness and training."
    },
    {
        "id": "FC2023/1.51",
        "title": "Ongoing security awareness updates",
        "coverage_pct": 80,
        "rationale": "AT-02 security awareness with ongoing updates.",
        "gaps": "Minor: SP 800-53 AT-02 covers ongoing awareness. FINMA expects regular refresh aligned with evolving threats to financial sector."
    },
    {
        "id": "FC2023/1.52",
        "title": "Threat intelligence and information sharing",
        "coverage_pct": 70,
        "rationale": "AT-05 contacts with security groups and associations; SI-05 security alerts and advisories.",
        "gaps": "FINMA encourages participation in financial sector threat intelligence sharing. SP 800-53 AT-05 and SI-05 cover external contacts and alerts but not Swiss-specific financial sector ISAC participation."
    },
    {
        "id": "FC2023/1.53",
        "title": "External threat intelligence sources",
        "coverage_pct": 70,
        "rationale": "AT-05 contacts with security groups; SI-05 security alerts and advisories.",
        "gaps": "FINMA expects use of financial sector-specific threat intelligence. SP 800-53 covers external threat sources but not Swiss financial sector-specific intelligence feeds."
    },
    # --- Risk assessment (FC2023/1.54-1.58) ---
    {
        "id": "FC2023/1.54",
        "title": "ICT risk assessment framework",
        "coverage_pct": 80,
        "rationale": "CA-05 POA&M; CM-08 component inventory; PS-02 position categorisation; RA-01 through RA-05 risk assessment family.",
        "gaps": "FINMA requires ICT risk assessment aligned with Swiss financial regulatory expectations. SP 800-53 RA family provides comprehensive risk assessment; gap in FINMA-specific risk categories and financial materiality thresholds."
    },
    {
        "id": "FC2023/1.55",
        "title": "ICT risk identification and analysis",
        "coverage_pct": 80,
        "rationale": "CA-05 POA&M; CM-08 inventory; RA-02 categorisation; RA-03 risk assessment; RA-04 risk assessment update.",
        "gaps": "Minor: SP 800-53 RA family covers risk identification and analysis. FINMA-specific financial risk categories may require supplementation."
    },
    {
        "id": "FC2023/1.56",
        "title": "Vulnerability management",
        "coverage_pct": 85,
        "rationale": "RA-03 risk assessment; RA-05 vulnerability scanning; SI-02 flaw remediation; SI-05 security alerts.",
        "gaps": "Minor: SP 800-53 provides comprehensive vulnerability management through RA-05 and SI-02."
    },
    {
        "id": "FC2023/1.57",
        "title": "Vulnerability scanning and assessment",
        "coverage_pct": 85,
        "rationale": "RA-03 risk assessment; RA-05 vulnerability scanning.",
        "gaps": "Minor: SP 800-53 RA-05 provides strong vulnerability scanning capability."
    },
    {
        "id": "FC2023/1.58",
        "title": "Risk assessment documentation and review",
        "coverage_pct": 80,
        "rationale": "RA-03 risk assessment with documentation requirements.",
        "gaps": "Minor: SP 800-53 RA-03 covers risk assessment documentation. FINMA expects regular review cycles aligned with regulatory calendar."
    },
    # --- Access control and security (FC2023/1.59-1.65) ---
    {
        "id": "FC2023/1.59",
        "title": "Access control and security controls framework",
        "coverage_pct": 90,
        "rationale": "Extensive coverage via AC family (AC-01 through AC-20); AU-09 audit protection; CM-05 change access restrictions; IA family (IA-01 through IA-07) identification and authentication; MA-04 remote maintenance; MP-02 media access; PE-02/PE-03 physical access; PS-04/PS-05/PS-06 personnel termination/transfer/agreements; SA-08 security engineering; SC family (SC-01/SC-05/SC-07/SC-10/SC-11/SC-14/SC-15/SC-18/SC-23) communications protection; SI family (SI-01/SI-02/SI-03/SI-07/SI-08) system integrity.",
        "gaps": "Minor: SP 800-53 provides comprehensive access control and security. Very strong alignment with FINMA requirements."
    },
    {
        "id": "FC2023/1.60",
        "title": "Identity and access management",
        "coverage_pct": 90,
        "rationale": "AC-01/AC-02/AC-03/AC-05/AC-06/AC-13 access control; IA-01/IA-02/IA-04/IA-05 identification and authentication; PS-04/PS-05 personnel termination and transfer.",
        "gaps": "Minor: SP 800-53 provides comprehensive identity and access management controls."
    },
    {
        "id": "FC2023/1.61",
        "title": "Authentication and session management",
        "coverage_pct": 90,
        "rationale": "AC-02/AC-03/AC-06/AC-07/AC-10/AC-11/AC-12 access control; IA-02/IA-05 authentication; SC-10 network disconnect.",
        "gaps": "Minor: SP 800-53 provides strong authentication and session management."
    },
    {
        "id": "FC2023/1.62",
        "title": "Network security and segmentation",
        "coverage_pct": 85,
        "rationale": "AC-04/AC-17/AC-18 information flow and remote/wireless access; CA-03 system connections; IA-03 device authentication; MA-04 remote maintenance; PE-04 transmission medium; SC-02/SC-03/SC-05/SC-07/SC-14/SC-15/SC-19/SC-20/SC-21/SC-22 network protection.",
        "gaps": "Minor: SP 800-53 provides comprehensive network security controls. FINMA-specific Swiss financial network segmentation standards well addressed."
    },
    {
        "id": "FC2023/1.63",
        "title": "Cryptography and data protection in transit",
        "coverage_pct": 90,
        "rationale": "AC-04/AC-17 information flow; IA-07 cryptographic module authentication; MP-05 media transport; PE-19 information leakage; SC-02/SC-03/SC-07/SC-08/SC-09/SC-11/SC-12/SC-13/SC-16/SC-17/SC-19/SC-23 comprehensive cryptographic and communications protection.",
        "gaps": "Minor: SP 800-53 provides comprehensive cryptographic controls. Very strong alignment with FINMA cryptography requirements."
    },
    {
        "id": "FC2023/1.64",
        "title": "Endpoint and software security",
        "coverage_pct": 85,
        "rationale": "AC-19 mobile device access; CM-06/CM-07 configuration and least functionality; SA-07 user-installed software; SC-12/SC-13/SC-17/SC-18 cryptographic and mobile code; SI-02/SI-03/SI-07/SI-08 flaw remediation, malware protection, software integrity.",
        "gaps": "Minor: SP 800-53 provides comprehensive endpoint protection. FINMA-specific endpoint standards well addressed."
    },
    {
        "id": "FC2023/1.65",
        "title": "Malware protection",
        "coverage_pct": 85,
        "rationale": "CM-07 least functionality; SC-05 denial of service protection; SI-03 malicious code protection.",
        "gaps": "Minor: SP 800-53 SI-03 provides comprehensive malware protection."
    },
    # --- Logging and monitoring (FC2023/1.66-1.69) ---
    {
        "id": "FC2023/1.66",
        "title": "Logging and monitoring framework",
        "coverage_pct": 85,
        "rationale": "AU-01 through AU-11 audit family; CA-07 continuous monitoring; CM-04 monitoring; IR-05 incident monitoring; PE-06/PE-08 physical monitoring; SI-01/SI-04/SI-11 system monitoring and error handling.",
        "gaps": "Minor: SP 800-53 AU and SI families provide comprehensive logging and monitoring. Very strong alignment."
    },
    {
        "id": "FC2023/1.67",
        "title": "Security event logging",
        "coverage_pct": 85,
        "rationale": "AU-01/AU-02/AU-03/AU-05/AU-06/AU-07/AU-09/AU-10 audit family; CA-07 continuous monitoring; IR-05 incident monitoring; SI-04 system monitoring.",
        "gaps": "Minor: SP 800-53 AU family provides comprehensive security event logging."
    },
    {
        "id": "FC2023/1.68",
        "title": "Log analysis and correlation",
        "coverage_pct": 80,
        "rationale": "AU-02 auditable events; AU-06 audit review and analysis; CA-07 continuous monitoring; SI-04 system monitoring.",
        "gaps": "Minor: SP 800-53 AU-06 and SI-04 cover log analysis and correlation. FINMA expects financial sector-specific SIEM requirements."
    },
    {
        "id": "FC2023/1.69",
        "title": "Automated monitoring and alerting",
        "coverage_pct": 80,
        "rationale": "AU-06 audit monitoring, analysis, and reporting; SI-04 system monitoring tools and techniques.",
        "gaps": "Minor: SP 800-53 AU-06 and SI-04 provide automated monitoring and alerting capabilities."
    },
    # --- Incident response and recovery (FC2023/1.70-1.74) ---
    {
        "id": "FC2023/1.70",
        "title": "Cyber incident response framework",
        "coverage_pct": 75,
        "rationale": "CP-10 system recovery; IR-01/IR-02 incident response policy and training; IR-04 incident handling; IR-07 incident response assistance.",
        "gaps": "FINMA requires Swiss financial sector cyber incident response aligned with FINMA reporting obligations. SP 800-53 IR family provides strong incident response but not FINMA-specific cyber response requirements."
    },
    {
        "id": "FC2023/1.71",
        "title": "Cyber incident containment and recovery",
        "coverage_pct": 75,
        "rationale": "CP-10 system recovery; IR-02 training; IR-04 incident handling; IR-07 assistance.",
        "gaps": "FINMA requires specific containment and recovery procedures for financial system cyber incidents. SP 800-53 covers containment and recovery but FINMA-specific financial service continuity requirements need supplementation."
    },
    {
        "id": "FC2023/1.72",
        "title": "Cyber incident eradication",
        "coverage_pct": 75,
        "rationale": "CP-10 system recovery; IR-04 incident handling including eradication.",
        "gaps": "FINMA requires thorough eradication verification before system restoration. SP 800-53 covers eradication but FINMA-specific verification requirements for financial systems need supplementation."
    },
    {
        "id": "FC2023/1.73",
        "title": "Cyber incident reporting to FINMA",
        "coverage_pct": 55,
        "rationale": "IR-06 incident reporting.",
        "gaps": "FINMA requires specific cyber incident reporting to FINMA within defined timeframes. SP 800-53 IR-06 covers incident reporting but FINMA-specific timelines and reporting formats are Swiss regulatory requirements not addressed."
    },
    {
        "id": "FC2023/1.74",
        "title": "Cyber incident notification to clients",
        "coverage_pct": 55,
        "rationale": "IR-06 incident reporting.",
        "gaps": "FINMA requires client notification for material cyber incidents affecting financial services. SP 800-53 IR-06 covers reporting but not Swiss financial sector client notification requirements."
    },
    # --- Security testing (FC2023/1.75-1.77) ---
    {
        "id": "FC2023/1.75",
        "title": "Security testing framework",
        "coverage_pct": 85,
        "rationale": "CA-01 assessment policy; CA-02 security assessments; CA-04 security certification; CA-05 POA&M; CA-06 authorization; CA-07 continuous monitoring; IR-03 incident response testing; RA-05 vulnerability scanning; SA-11 developer security testing; SI-06 security functionality verification.",
        "gaps": "Minor: SP 800-53 provides comprehensive security testing through CA, RA, and SA families."
    },
    {
        "id": "FC2023/1.76",
        "title": "Penetration testing and vulnerability assessment",
        "coverage_pct": 85,
        "rationale": "CA-02 security assessments; CA-04 certification; CA-07 continuous monitoring; IR-03 incident response testing; RA-05 vulnerability scanning; SA-11 developer testing; SI-06 security verification.",
        "gaps": "Minor: FINMA requires regular penetration testing. SP 800-53 RA-05 and CA-02 provide strong vulnerability assessment and testing. FINMA-specific TLPT (threat-led penetration testing) requirements may need supplementation."
    },
    {
        "id": "FC2023/1.77",
        "title": "Independent security testing",
        "coverage_pct": 75,
        "rationale": "CA-02 security assessments; IR-03 incident response testing.",
        "gaps": "FINMA requires periodic independent security testing by qualified third parties. SP 800-53 CA-02 supports independent assessment but FINMA-specific independent testing cadence and qualifications require supplementation."
    },
    # --- Data protection and classification (FC2023/1.78-1.84) ---
    {
        "id": "FC2023/1.78",
        "title": "Data classification and protection framework",
        "coverage_pct": 80,
        "rationale": "AC-15/AC-16 automated marking and labelling; MP-01 through MP-06 media protection; PE-19 information leakage; PL-05 privacy impact; PT-01 through PT-07 PII processing; RA-02 security categorisation; SC-01/SC-04/SC-08/SC-09 communications protection; SI-07/SI-09/SI-10/SI-12 system integrity.",
        "gaps": "Minor: SP 800-53 provides comprehensive data classification and protection. FINMA Swiss banking secrecy and client data protection requirements may need supplementation."
    },
    {
        "id": "FC2023/1.79",
        "title": "Data classification scheme",
        "coverage_pct": 75,
        "rationale": "AC-15/AC-16 automated marking/labelling; MP-01/MP-03 media protection and labelling; PL-05 privacy impact; PT-01/PT-02/PT-03/PT-07 PII processing.",
        "gaps": "FINMA requires data classification aligned with Swiss banking secrecy requirements. SP 800-53 covers security classification but Swiss-specific banking data classification needs supplementation."
    },
    {
        "id": "FC2023/1.80",
        "title": "Data handling and processing controls",
        "coverage_pct": 75,
        "rationale": "AC-16 automated labelling; MP-02/MP-03 media access and labelling; PT-03/PT-07 PII processing purposes and categories; SI-09/SI-10 input restrictions and accuracy.",
        "gaps": "FINMA requires specific data handling procedures for Swiss financial data. SP 800-53 covers data handling but Swiss banking secrecy and data locality requirements need supplementation."
    },
    {
        "id": "FC2023/1.81",
        "title": "Data protection in storage and transit",
        "coverage_pct": 85,
        "rationale": "MP-04/MP-05 media storage and transport; PE-18 component location; SC-08/SC-09 transmission integrity and confidentiality.",
        "gaps": "Minor: SP 800-53 provides strong data protection in storage and transit."
    },
    {
        "id": "FC2023/1.82",
        "title": "Data retention and archiving",
        "coverage_pct": 70,
        "rationale": "AU-11 audit record retention; CP-09 backup; MP-04 media storage; PT-06 system of records; SI-12 information output handling and retention.",
        "gaps": "FINMA requires data retention aligned with Swiss financial regulatory requirements (typically 10 years). SP 800-53 covers retention but Swiss-specific financial regulatory retention periods need supplementation."
    },
    {
        "id": "FC2023/1.83",
        "title": "Secure data disposal",
        "coverage_pct": 85,
        "rationale": "AU-11 audit retention; MP-06 media sanitisation; SC-04 information remnance; SI-12 information output handling; SR-12 component disposal.",
        "gaps": "Minor: SP 800-53 provides comprehensive data disposal through MP-06, SC-04, and SR-12."
    },
    {
        "id": "FC2023/1.84",
        "title": "Data quality and accuracy",
        "coverage_pct": 65,
        "rationale": "MP-06 media sanitisation; SI-10 information accuracy, completeness, validity.",
        "gaps": "FINMA requires data quality controls for financial data accuracy. SP 800-53 SI-10 covers input validation but FINMA-specific financial data quality requirements need supplementation."
    },
    # --- Business continuity (FC2023/1.87-1.99) ---
    {
        "id": "FC2023/1.87",
        "title": "ICT business continuity management framework",
        "coverage_pct": 75,
        "rationale": "CP-01 contingency planning policy; CP-02 contingency plan; CP-05 contingency plan update.",
        "gaps": "FINMA requires comprehensive ICT BCM aligned with Swiss financial sector operational resilience requirements. SP 800-53 CP family covers contingency planning but FINMA-specific BCM framework and Swiss financial sector resilience requirements need supplementation."
    },
    {
        "id": "FC2023/1.88",
        "title": "Business impact analysis for ICT",
        "coverage_pct": 70,
        "rationale": "CP-01 contingency planning policy; CP-02 contingency plan with business impact analysis.",
        "gaps": "FINMA requires BIA specific to financial services with recovery time and recovery point objectives. SP 800-53 CP-02 includes BIA but FINMA-specific financial sector impact criteria need supplementation."
    },
    {
        "id": "FC2023/1.89",
        "title": "ICT recovery capabilities",
        "coverage_pct": 80,
        "rationale": "CP-02 contingency plan; CP-06 alternate storage; CP-07 alternate processing; CP-08 telecommunications; CP-09 backup; CP-10 recovery; MA-06 timely maintenance; PE-09 through PE-15 physical environmental protection; PE-17 alternate work site.",
        "gaps": "Minor: SP 800-53 provides comprehensive recovery capabilities through the CP and PE families."
    },
    {
        "id": "FC2023/1.90",
        "title": "ICT disaster recovery planning",
        "coverage_pct": 80,
        "rationale": "CP-02 contingency plan; CP-06/CP-07/CP-08/CP-09/CP-10 recovery infrastructure; PE-17 alternate work site.",
        "gaps": "Minor: SP 800-53 covers disaster recovery planning. FINMA-specific Swiss financial sector DR requirements largely addressed."
    },
    {
        "id": "FC2023/1.91",
        "title": "Recovery site and backup requirements",
        "coverage_pct": 80,
        "rationale": "CP-02 contingency plan; CP-06 alternate storage; CP-07 alternate processing; CP-09 backup.",
        "gaps": "Minor: SP 800-53 covers alternate sites and backup. FINMA may have Swiss data residency requirements for recovery sites."
    },
    {
        "id": "FC2023/1.92",
        "title": "Business continuity training",
        "coverage_pct": 80,
        "rationale": "CP-03 contingency training.",
        "gaps": "Minor: SP 800-53 CP-03 covers contingency training."
    },
    {
        "id": "FC2023/1.93",
        "title": "Business continuity awareness",
        "coverage_pct": 80,
        "rationale": "CP-03 contingency training.",
        "gaps": "Minor: SP 800-53 CP-03 covers contingency awareness and training."
    },
    {
        "id": "FC2023/1.94",
        "title": "Business continuity testing framework",
        "coverage_pct": 80,
        "rationale": "CP-04 contingency plan testing and exercises.",
        "gaps": "Minor: SP 800-53 CP-04 provides comprehensive BC testing. FINMA may require specific financial sector scenario testing."
    },
    {
        "id": "FC2023/1.95",
        "title": "Disaster recovery testing",
        "coverage_pct": 80,
        "rationale": "CP-04 contingency plan testing and exercises.",
        "gaps": "Minor: SP 800-53 CP-04 covers DR testing."
    },
    {
        "id": "FC2023/1.96",
        "title": "Business continuity testing scenarios",
        "coverage_pct": 75,
        "rationale": "CP-04 contingency plan testing including realistic scenarios.",
        "gaps": "FINMA requires severe but plausible scenario testing for financial services. SP 800-53 CP-04 covers testing but FINMA-specific financial sector scenario requirements need supplementation."
    },
    {
        "id": "FC2023/1.97",
        "title": "Business continuity test results and improvements",
        "coverage_pct": 75,
        "rationale": "CP-04 contingency plan testing with lessons learned.",
        "gaps": "FINMA requires documented test results and improvement actions. SP 800-53 CP-04 covers testing results but FINMA-specific improvement documentation requirements need supplementation."
    },
    {
        "id": "FC2023/1.98",
        "title": "Business continuity plan maintenance",
        "coverage_pct": 80,
        "rationale": "CP-05 contingency plan update.",
        "gaps": "Minor: SP 800-53 CP-05 covers contingency plan maintenance and updates."
    },
    {
        "id": "FC2023/1.99",
        "title": "Business continuity plan distribution",
        "coverage_pct": 75,
        "rationale": "CP-05 contingency plan update including distribution.",
        "gaps": "FINMA requires plan distribution to key personnel. SP 800-53 CP-05 covers plan updates but specific distribution requirements less detailed."
    },
    # --- Outsourcing and third-party risk (FC2023/1.100-1.128) ---
    {
        "id": "FC2023/1.100",
        "title": "Outsourcing governance framework",
        "coverage_pct": 70,
        "rationale": "AC-20 external systems; CA-03 system connections; MA-05 maintenance personnel; PS-03/PS-07 personnel screening and third-party security; SA-01/SA-04 acquisition policy and requirements; SA-09 external services; SR-01/SR-02/SR-05 supply chain management.",
        "gaps": "FINMA requires comprehensive outsourcing governance including Swiss-specific regulatory approval requirements for material outsourcing. SP 800-53 covers vendor management but FINMA-specific outsourcing governance and FINMA notification requirements not addressed."
    },
    {
        "id": "FC2023/1.101",
        "title": "Outsourcing risk assessment",
        "coverage_pct": 70,
        "rationale": "AC-20 external systems; CA-03 system connections; MA-05 maintenance personnel; PS-07 third-party personnel; SA-04 acquisitions; SA-09 external services; SR-01/SR-02/SR-05 supply chain.",
        "gaps": "FINMA requires specific risk assessment for outsourcing arrangements including concentration risk and Swiss-specific regulatory considerations. SP 800-53 covers third-party risk assessment but FINMA-specific outsourcing risk criteria need supplementation."
    },
    {
        "id": "FC2023/1.102",
        "title": "Outsourcing contractual requirements",
        "coverage_pct": 65,
        "rationale": "PS-07 third-party personnel security; SA-04 acquisitions; SA-09 external services; SR-02 supply chain risk management plan.",
        "gaps": "FINMA requires specific contractual clauses including FINMA audit rights, sub-outsourcing restrictions, and data location requirements. SP 800-53 covers vendor contracts but FINMA-specific contractual requirements need supplementation."
    },
    {
        "id": "FC2023/1.103",
        "title": "Outsourcing due diligence",
        "coverage_pct": 65,
        "rationale": "SA-04 acquisitions; SA-09 external services; SR-02 supply chain plan.",
        "gaps": "FINMA requires specific due diligence for outsourcing partners including financial stability and Swiss regulatory compliance. SP 800-53 covers vendor assessment but FINMA-specific due diligence requirements need supplementation."
    },
    {
        "id": "FC2023/1.104",
        "title": "Outsourcing ongoing monitoring",
        "coverage_pct": 60,
        "rationale": "SA-09 external services; SR-03 supply chain controls.",
        "gaps": "FINMA requires ongoing monitoring of outsourcing providers including SLA monitoring and Swiss regulatory compliance tracking. SP 800-53 covers external service monitoring but FINMA-specific ongoing monitoring requirements need supplementation."
    },
    {
        "id": "FC2023/1.105",
        "title": "Sub-outsourcing controls",
        "coverage_pct": 55,
        "rationale": "SR-03 supply chain controls and processes.",
        "gaps": "FINMA requires specific controls for sub-outsourcing including approval requirements and chain monitoring. SP 800-53 SR-03 covers supply chain processes but FINMA-specific sub-outsourcing governance not addressed."
    },
    {
        "id": "FC2023/1.106",
        "title": "Sub-outsourcing notification and approval",
        "coverage_pct": 50,
        "rationale": "SR-03 supply chain controls.",
        "gaps": "FINMA requires notification and approval for material sub-outsourcing arrangements. SP 800-53 covers supply chain processes but not FINMA-specific sub-outsourcing approval requirements."
    },
    {
        "id": "FC2023/1.107",
        "title": "Sub-outsourcing risk management",
        "coverage_pct": 50,
        "rationale": "SR-03 supply chain controls.",
        "gaps": "FINMA requires risk management for the entire outsourcing chain. SP 800-53 SR-03 covers supply chain controls but FINMA-specific multi-tier outsourcing risk management needs supplementation."
    },
    {
        "id": "FC2023/1.108",
        "title": "Sub-outsourcing audit rights",
        "coverage_pct": 45,
        "rationale": "SR-03 supply chain controls.",
        "gaps": "FINMA requires audit rights over sub-outsourcing arrangements. SP 800-53 covers supply chain verification but FINMA-specific audit rights for outsourcing chains not explicitly addressed."
    },
    {
        "id": "FC2023/1.109",
        "title": "Supply chain provenance",
        "coverage_pct": 60,
        "rationale": "SR-04 provenance.",
        "gaps": "FINMA requires understanding of ICT supply chain provenance. SP 800-53 SR-04 covers provenance but FINMA-specific financial sector supply chain traceability may need supplementation."
    },
    {
        "id": "FC2023/1.110",
        "title": "Supply chain provenance verification",
        "coverage_pct": 60,
        "rationale": "SR-04 provenance.",
        "gaps": "FINMA requires verification of supply chain components. SP 800-53 SR-04 covers provenance verification."
    },
    {
        "id": "FC2023/1.111",
        "title": "Acquisition strategy for ICT services",
        "coverage_pct": 70,
        "rationale": "SR-05 acquisition strategies, tools, and methods.",
        "gaps": "FINMA requires structured acquisition approach for ICT services. SP 800-53 SR-05 covers acquisition strategies."
    },
    {
        "id": "FC2023/1.112",
        "title": "Acquisition methods and tools",
        "coverage_pct": 70,
        "rationale": "SR-05 acquisition strategies, tools, and methods.",
        "gaps": "FINMA requires specific acquisition methods for financial sector ICT. SP 800-53 SR-05 covers acquisition methods."
    },
    {
        "id": "FC2023/1.113",
        "title": "Supplier assessment and review",
        "coverage_pct": 70,
        "rationale": "SR-06 supplier assessments and reviews; SR-10 inspection.",
        "gaps": "FINMA requires regular supplier assessment aligned with Swiss financial regulatory expectations. SP 800-53 SR-06 covers supplier assessment; FINMA-specific assessment criteria may need supplementation."
    },
    {
        "id": "FC2023/1.114",
        "title": "Supplier assessment frequency",
        "coverage_pct": 70,
        "rationale": "SR-06 supplier assessments; SR-10 inspection of systems or components.",
        "gaps": "FINMA requires periodic supplier assessment cycles. SP 800-53 SR-06 covers ongoing supplier review."
    },
    {
        "id": "FC2023/1.115",
        "title": "Supplier risk rating",
        "coverage_pct": 65,
        "rationale": "SR-06 supplier assessments and reviews.",
        "gaps": "FINMA requires supplier risk rating and classification. SP 800-53 SR-06 covers supplier assessment but not FINMA-specific risk rating methodology."
    },
    {
        "id": "FC2023/1.116",
        "title": "Supplier performance monitoring",
        "coverage_pct": 60,
        "rationale": "SR-06 supplier assessments and reviews.",
        "gaps": "FINMA requires ongoing supplier performance monitoring. SP 800-53 SR-06 covers supplier review but FINMA-specific SLA monitoring and performance benchmarking need supplementation."
    },
    {
        "id": "FC2023/1.117",
        "title": "Supply chain operations security",
        "coverage_pct": 60,
        "rationale": "SR-07 supply chain operations security.",
        "gaps": "FINMA requires operations security in supply chain. SP 800-53 SR-07 covers supply chain OpSec."
    },
    {
        "id": "FC2023/1.118",
        "title": "Supply chain security measures",
        "coverage_pct": 60,
        "rationale": "SR-07 supply chain operations security.",
        "gaps": "FINMA requires specific security measures in supply chain operations. SP 800-53 SR-07 covers supply chain security measures."
    },
    {
        "id": "FC2023/1.119",
        "title": "Supplier notification agreements",
        "coverage_pct": 70,
        "rationale": "SR-08 notification agreements.",
        "gaps": "FINMA requires notification agreements with ICT suppliers. SP 800-53 SR-08 covers notification agreements."
    },
    {
        "id": "FC2023/1.120",
        "title": "Supplier incident notification",
        "coverage_pct": 70,
        "rationale": "SR-08 notification agreements.",
        "gaps": "FINMA requires timely incident notification from suppliers. SP 800-53 SR-08 covers notification requirements."
    },
    {
        "id": "FC2023/1.121",
        "title": "Supplier change notification",
        "coverage_pct": 65,
        "rationale": "SR-08 notification agreements.",
        "gaps": "FINMA requires notification for material changes by suppliers. SP 800-53 SR-08 covers notification but FINMA-specific material change criteria need supplementation."
    },
    {
        "id": "FC2023/1.122",
        "title": "Tamper resistance requirements",
        "coverage_pct": 65,
        "rationale": "SR-09 tamper resistance and detection; SR-11 component authenticity.",
        "gaps": "FINMA requires tamper resistance for critical financial systems. SP 800-53 SR-09 and SR-11 cover tamper resistance and authenticity."
    },
    {
        "id": "FC2023/1.123",
        "title": "Tamper detection mechanisms",
        "coverage_pct": 60,
        "rationale": "SR-09 tamper resistance and detection.",
        "gaps": "FINMA requires tamper detection capabilities. SP 800-53 SR-09 covers tamper detection."
    },
    {
        "id": "FC2023/1.124",
        "title": "System and component inspection",
        "coverage_pct": 65,
        "rationale": "SR-10 inspection of systems or components.",
        "gaps": "FINMA requires inspection of ICT systems and components. SP 800-53 SR-10 covers component inspection."
    },
    {
        "id": "FC2023/1.125",
        "title": "Component authenticity verification",
        "coverage_pct": 70,
        "rationale": "SR-11 component authenticity.",
        "gaps": "FINMA requires verification of component authenticity. SP 800-53 SR-11 covers component authenticity."
    },
    {
        "id": "FC2023/1.126",
        "title": "Component authenticity controls",
        "coverage_pct": 70,
        "rationale": "SR-11 component authenticity.",
        "gaps": "FINMA requires controls ensuring component authenticity. SP 800-53 SR-11 covers component authenticity controls."
    },
    {
        "id": "FC2023/1.127",
        "title": "Secure component disposal",
        "coverage_pct": 75,
        "rationale": "SR-12 component disposal.",
        "gaps": "FINMA requires secure disposal of ICT components. SP 800-53 SR-12 covers component disposal."
    },
    {
        "id": "FC2023/1.128",
        "title": "Component disposal verification",
        "coverage_pct": 75,
        "rationale": "SR-12 component disposal with verification.",
        "gaps": "FINMA requires verification of secure component disposal. SP 800-53 SR-12 covers disposal with verification."
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
        "framework_id": "finma_circular",
        "framework_name": "FINMA Circular 2023/1",
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
