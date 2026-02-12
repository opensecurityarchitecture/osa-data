#!/usr/bin/env python3
"""Generate EU DORA (Regulation (EU) 2022/2554) coverage analysis JSON.

Reads all SP 800-53 Rev 5 control files via _manifest.json,
builds reverse mappings from DORA clauses to SP 800-53 controls,
and produces a framework-coverage JSON with expert analysis.

Output: data/framework-coverage/dora.json
"""

import json
import os
import sys
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
CONTROLS_DIR = os.path.join(DATA_DIR, 'controls')
COVERAGE_DIR = os.path.join(DATA_DIR, 'framework-coverage')
OUTPUT_FILE = os.path.join(COVERAGE_DIR, 'dora.json')

# ---------------------------------------------------------------------------
# DORA clause metadata: title, coverage_pct, rationale, gaps
# Regulation (EU) 2022/2554 — Digital Operational Resilience Act
#
# Chapter II: ICT Risk Management (Art. 5-16)
# Chapter III: ICT-related Incident Management (Art. 17-23)
# Chapter IV: Digital Operational Resilience Testing (Art. 24-27)
# Chapter V: Managing ICT Third-Party Risk (Art. 28-44)
# Chapter VI: Information-sharing arrangements (Art. 45)
# ---------------------------------------------------------------------------

CLAUSE_METADATA = {
    # ── Chapter II: ICT Risk Management ──────────────────────────────────

    # Art. 5 — Governance and organisation
    "Art.5(1)": {
        "title": "Governance and organisation — management body responsibility",
        "coverage_pct": 60,
        "rationale": "AC-01, CA-01, PL-01 establish policies and planning but address organisational policy structures rather than board-level governance accountability. SP 800-53 does not mandate management body ultimate responsibility for ICT risk.",
        "gaps": "DORA requires the management body to define, approve, oversee, and be ultimately responsible for ICT risk management. SP 800-53 establishes policy ownership but lacks the specific board/management body accountability, personal liability, and fiduciary duty requirements of DORA Art. 5."
    },
    "Art.5(2)": {
        "title": "Governance and organisation — management body approval of digital operational resilience strategy",
        "coverage_pct": 50,
        "rationale": "CA-06 provides security authorisation but does not address a specific digital operational resilience strategy requiring board approval.",
        "gaps": "DORA mandates explicit board approval of a digital operational resilience strategy. SP 800-53 has no equivalent concept of a board-approved resilience strategy document. The authorisation concept in CA-06 is system-level, not enterprise resilience-level."
    },
    "Art.5(4)": {
        "title": "Governance and organisation — ICT risk management training for management body",
        "coverage_pct": 65,
        "rationale": "AT-01 through AT-03 provide security awareness and training. PS-01 through PS-08 cover personnel security. PL-04 rules of behaviour. These address general training but not specifically board-level ICT risk competence.",
        "gaps": "DORA requires management body members to maintain sufficient knowledge and skills to understand and assess ICT risk, including regular specific training. SP 800-53 training controls are aimed at general personnel, not specifically at board-level competence requirements."
    },

    # Art. 6 — ICT risk management framework
    "Art.6(1)": {
        "title": "ICT risk management framework — establishment and maintenance",
        "coverage_pct": 80,
        "rationale": "AC-01, CA-01, CA-06, PL-01, PL-02, PL-06, RA-01, SA-02 provide comprehensive policy, planning, risk assessment, and authorisation frameworks.",
        "gaps": "DORA requires an ICT risk management framework that is documented, reviewed annually, and improved based on lessons learned and audit findings. SP 800-53 covers most elements but does not require the specific annual review cycle or the explicit link to digital operational resilience strategy."
    },
    "Art.6(2)": {
        "title": "ICT risk management framework — risk assessment and documentation",
        "coverage_pct": 80,
        "rationale": "PL-02, PL-05, PT-06, RA-01, RA-03 address system security plans, privacy impact assessments, and risk assessments comprehensively.",
        "gaps": "Minor gap: DORA requires ICT risk management to support the digital operational resilience strategy with continuous evolution. SP 800-53 risk assessment is strong but the explicit link to operational resilience strategy is not present."
    },
    "Art.6(4)": {
        "title": "ICT risk management framework — review and audit",
        "coverage_pct": 75,
        "rationale": "AC-13 supervision and review; CA-05 plan of action and milestones; PL-03 system security plan update; RA-04 risk assessment update.",
        "gaps": "DORA requires periodic audits of the ICT risk management framework by internal auditors or external firms. SP 800-53 provides review mechanisms but does not mandate formal internal audit of the risk management framework itself."
    },
    "Art.6(5)": {
        "title": "ICT risk management framework — formal reporting to management body",
        "coverage_pct": 55,
        "rationale": "AU-01 audit policies; PL-05 privacy assessment; RA-03 and RA-04 risk assessment and update. These produce reports but do not mandate reporting to the management body.",
        "gaps": "DORA mandates formal reporting to the management body on ICT risk at least annually, including ICT risk findings and recommendations. SP 800-53 has no specific requirement for management body reporting on ICT risk."
    },
    "Art.6(8)": {
        "title": "ICT risk management framework — documentation and review availability",
        "coverage_pct": 55,
        "rationale": "AU-01 audit policy documentation; PT-01 PII processing policies provide documentation requirements.",
        "gaps": "DORA requires the ICT risk management framework documentation to be available to competent authorities on request. SP 800-53 does not address regulatory reporting obligations or making frameworks available to financial supervisors."
    },

    # Art. 7 — ICT systems, protocols and tools
    "Art.7(1)": {
        "title": "ICT systems, protocols and tools — reliability and capacity",
        "coverage_pct": 85,
        "rationale": "CM-01, CM-02, CM-06, CM-07 configuration management; MA-01 through MA-06 maintenance; SA-01, SA-03, SA-08 system acquisition and engineering; SI-01 system integrity. Comprehensive coverage of ICT system management.",
        "gaps": "Minor: DORA specifically requires systems to be resilient, have sufficient capacity, and be technologically up to date. SP 800-53 addresses these through configuration and maintenance controls but does not use DORA's specific language around technological currency and capacity adequacy for financial services."
    },
    "Art.7(2)": {
        "title": "ICT systems, protocols and tools — keep systems up to date",
        "coverage_pct": 85,
        "rationale": "SI-02 flaw remediation directly addresses keeping systems current through patching and updates.",
        "gaps": "Minimal gap. DORA's requirement to keep ICT systems up to date is well covered by SI-02 flaw remediation."
    },

    # Art. 8 — Identification
    "Art.8(1)": {
        "title": "Identification — ICT asset identification and classification",
        "coverage_pct": 85,
        "rationale": "AC-15, AC-16 automated marking and labelling; CM-08 component inventory; MP-03 media labelling; RA-02 security categorisation; SA-05 documentation; SI-12 information handling. Comprehensive asset identification and classification.",
        "gaps": "Minor: DORA requires identification of all ICT-supported business functions, roles, and information/ICT assets. SP 800-53 provides strong asset inventory and classification but does not explicitly link to business function mapping required by DORA."
    },
    "Art.8(4)": {
        "title": "Identification — ICT asset register and classification",
        "coverage_pct": 80,
        "rationale": "AC-16 automated labelling; CM-08 component inventory; RA-02 security categorisation; SA-05 documentation.",
        "gaps": "DORA requires maintaining an up-to-date register of all ICT assets and their classification. SP 800-53 CM-08 and RA-02 cover most of this but DORA specifically requires the register to include all ICT assets supporting critical or important functions."
    },
    "Art.8(5)": {
        "title": "Identification — ICT risk assessment on legacy systems",
        "coverage_pct": 60,
        "rationale": "SA-03 life cycle support and SA-10 developer configuration management address system lifecycle but not specifically legacy system risk.",
        "gaps": "DORA specifically requires risk assessment of legacy ICT systems and their interactions with other systems. SP 800-53 has no specific legacy system risk assessment requirement. SA-03 addresses lifecycle generally but not the specific DORA focus on identifying and managing risks from outdated/legacy ICT systems."
    },

    # Art. 9 — Protection and prevention
    "Art.9(1)": {
        "title": "Protection and prevention — ICT security policies",
        "coverage_pct": 85,
        "rationale": "CM-01, CM-02, CM-06, CM-07 configuration management; MA-01 maintenance; PE-01 through PE-03 physical protection; SA-01, SA-08 system acquisition; SC-01 system protection; SI-01 integrity. Comprehensive protection policy coverage.",
        "gaps": "Minor: DORA requires protection and prevention measures to ensure resilience, continuity, and availability of ICT systems. SP 800-53 covers the technical controls well but does not frame them in the specific context of digital operational resilience for financial entities."
    },
    "Art.9(2)": {
        "title": "Protection and prevention — ICT system resilience and availability",
        "coverage_pct": 75,
        "rationale": "SC-05 denial of service protection; SC-06 resource priority; SC-14 public access protections address availability and resilience.",
        "gaps": "DORA requires specific measures to minimise the impact of ICT risk and ensure availability including performance and capacity management. SP 800-53 provides DoS protection and resource management but does not address DORA's specific requirements for financial entity ICT availability targets."
    },
    "Art.9(3)": {
        "title": "Protection and prevention — data integrity, confidentiality, and availability safeguards",
        "coverage_pct": 90,
        "rationale": "IA-05, IA-07 authenticator and cryptographic module management; RA-05 vulnerability scanning; SC-08, SC-09 transmission integrity and confidentiality; SC-11 through SC-17 cryptographic protections and PKI; SC-23 session authenticity. Comprehensive cryptographic and data protection coverage.",
        "gaps": "Minimal gap. SP 800-53 provides comprehensive data protection controls that align well with DORA's requirements for data integrity, confidentiality, and availability."
    },
    "Art.9(4)(a)": {
        "title": "Protection and prevention — network security management",
        "coverage_pct": 90,
        "rationale": "AC-04 information flow; AC-17 through AC-19 remote, wireless, and mobile access; CA-03 system connections; MA-04 remote maintenance; MP-01, MP-04, MP-05 media protection; SC-01 through SC-03 system protection and isolation; SC-07 boundary protection; SC-08 transmission integrity; SC-15, SC-19 through SC-22 collaborative computing and DNS protections. Extensive network security controls.",
        "gaps": "Minimal gap. SP 800-53 provides comprehensive network security controls that address DORA's network security management requirements."
    },
    "Art.9(4)(b)": {
        "title": "Protection and prevention — data leakage, malware, and media protection",
        "coverage_pct": 90,
        "rationale": "MP-01, MP-02, MP-04 through MP-06 media protection; SC-04 information remnance; SI-03 malicious code protection; SI-07 software integrity; SI-08 spam protection. Comprehensive data and malware protection.",
        "gaps": "Minimal gap. SP 800-53 comprehensively covers malware protection and data leakage prevention."
    },
    "Art.9(4)(c)": {
        "title": "Protection and prevention — access control and authentication",
        "coverage_pct": 95,
        "rationale": "AC-01 through AC-14, AC-17, AC-19 comprehensive access control; CM-05 change access restrictions; IA-01 through IA-06 identification and authentication; MA-04 remote maintenance; PS-04, PS-05 personnel termination and transfer; SC-10 network disconnect; SI-09 input restrictions. Extremely comprehensive access control and authentication coverage.",
        "gaps": "Negligible. SP 800-53 access control and identification families provide thorough coverage of DORA's access control and authentication requirements."
    },
    "Art.9(4)(d)": {
        "title": "Protection and prevention — strong authentication and identity management",
        "coverage_pct": 90,
        "rationale": "AC-02 account management; AC-05, AC-06 separation of duties and least privilege; IA-01 through IA-05 identification and authentication policies, user/device authentication, identifier and authenticator management.",
        "gaps": "Minor: DORA emphasises strong authentication mechanisms and robust identity management. SP 800-53 IA family provides strong coverage but DORA's specific requirements for financial entity authentication standards may require supplementary financial sector guidance."
    },
    "Art.9(4)(e)": {
        "title": "Protection and prevention — change management and software security",
        "coverage_pct": 85,
        "rationale": "CM-03 through CM-05 change control and access restrictions; MA-03 maintenance tools; SA-06, SA-07 software usage restrictions; SA-10 developer configuration management; SC-18 mobile code; SI-02 flaw remediation; SI-07 software integrity; SI-10, SI-11 input validation and error handling.",
        "gaps": "Minor: DORA requires robust ICT change management including testing in separate environments. SP 800-53 change management is comprehensive but does not specifically mandate separation of test and production environments as DORA does."
    },

    # Art. 10 — Detection
    "Art.10(1)": {
        "title": "Detection — anomalous activities and ICT-related incidents",
        "coverage_pct": 90,
        "rationale": "AC-09 previous logon notification; AU-02 through AU-11 comprehensive audit and accountability; CA-07 continuous monitoring; SI-04 information system monitoring; SI-05 security alerts; SI-06 security functionality verification. Extensive detection capabilities.",
        "gaps": "Minor: DORA requires detection of anomalous activities specifically in the context of ICT-related incidents and digital operational resilience. SP 800-53 audit and monitoring controls are comprehensive but do not use DORA's specific financial services context."
    },
    "Art.10(2)": {
        "title": "Detection — multiple layers of control and alert thresholds",
        "coverage_pct": 85,
        "rationale": "AU-02 auditable events; AU-05 response to audit failures; AU-06 audit monitoring and analysis; CA-07 continuous monitoring; SI-04 system monitoring; SI-06 security functionality verification.",
        "gaps": "Minor: DORA requires multiple layers of control including defined alert thresholds and criteria to trigger detection and response. SP 800-53 provides layered monitoring but does not prescribe DORA's specific multi-layer approach with defined thresholds."
    },

    # Art. 11 — Response and recovery
    "Art.11(1)": {
        "title": "Response and recovery — ICT business continuity policy",
        "coverage_pct": 80,
        "rationale": "CP-01 contingency planning policy; CP-02 contingency plan; CP-10 system recovery. Good coverage of continuity planning and recovery.",
        "gaps": "DORA requires a comprehensive ICT business continuity policy as part of the overall business continuity policy. SP 800-53 CP family addresses IT contingency but DORA requires explicit integration with broader business continuity and operational resilience."
    },
    "Art.11(2)": {
        "title": "Response and recovery — recovery time and point objectives",
        "coverage_pct": 70,
        "rationale": "CP-10 system recovery addresses recovery and reconstitution.",
        "gaps": "DORA requires entities to set specific recovery time objectives (RTOs) and recovery point objectives (RPOs) for each critical function. SP 800-53 CP-10 addresses recovery generally but does not mandate specific RTO/RPO definition for each function as DORA does."
    },
    "Art.11(3)": {
        "title": "Response and recovery — impact analysis of ICT disruption scenarios",
        "coverage_pct": 75,
        "rationale": "CP-01, CP-02 contingency policy and planning; CP-07 alternate processing site; CP-08 telecommunications services address disruption scenarios.",
        "gaps": "DORA requires business impact analysis (BIA) specifically assessing the impact of severe ICT disruption scenarios. SP 800-53 CP-02 includes BIA concepts but DORA specifically requires scenario-based impact analysis for severe ICT disruptions."
    },
    "Art.11(4)": {
        "title": "Response and recovery — ICT response and recovery plans",
        "coverage_pct": 80,
        "rationale": "CP-02 contingency plan and CP-10 system recovery and reconstitution directly address response and recovery planning.",
        "gaps": "Minor: DORA requires dedicated ICT response and recovery plans including for scenarios of severe operational disruption. SP 800-53 contingency planning covers this well but DORA requires these plans to be specifically tested for ICT scenarios."
    },
    "Art.11(6)": {
        "title": "Response and recovery — testing of ICT business continuity plans",
        "coverage_pct": 85,
        "rationale": "CP-03 contingency training; CP-04 contingency plan testing; CP-05 contingency plan update. Comprehensive testing and maintenance of continuity plans.",
        "gaps": "Minor: DORA requires testing of ICT business continuity plans at least annually and after substantive changes. SP 800-53 CP-04 addresses testing but does not mandate the specific annual minimum or post-change testing frequency."
    },
    "Art.11(7)": {
        "title": "Response and recovery — crisis communication plans",
        "coverage_pct": 55,
        "rationale": "CP-04 contingency plan testing provides a testing framework but does not specifically address crisis communication plans.",
        "gaps": "DORA requires financial entities to have crisis communication plans covering responsible staff disclosure, communication with clients, and internal escalation. SP 800-53 does not specifically address crisis communications as required by DORA."
    },

    # Art. 12 — Backup policies and recovery
    "Art.12(1)": {
        "title": "Backup policies and recovery — backup policy development",
        "coverage_pct": 85,
        "rationale": "CP-01 contingency planning policy; CP-02 contingency plan; CP-09 system backup. Comprehensive backup policy coverage.",
        "gaps": "Minor: DORA requires the backup policy to specify the scope of data subject to backup and the minimum frequency. SP 800-53 CP-09 covers backup comprehensively but DORA requires specific scope and frequency documentation."
    },
    "Art.12(2)": {
        "title": "Backup policies and recovery — restoration and recovery from backups",
        "coverage_pct": 85,
        "rationale": "CP-06 alternate storage; CP-07 alternate processing; CP-08 telecommunications; CP-09 system backup. Strong coverage of backup restoration capabilities.",
        "gaps": "Minor: DORA requires testing backup restoration at least annually. SP 800-53 CP-09 addresses backup but the specific annual restoration testing requirement is a DORA-specific mandate."
    },
    "Art.12(3)": {
        "title": "Backup policies and recovery — backup data integrity and confidentiality",
        "coverage_pct": 85,
        "rationale": "CP-09 system backup with integrity protections; SI-12 information output handling and retention.",
        "gaps": "Minor: DORA specifically requires integrity, confidentiality, and recoverability of backed-up data. SP 800-53 CP-09 addresses backup protection but DORA specifically requires verification of backup data integrity."
    },
    "Art.12(5)": {
        "title": "Backup policies and recovery — geographically separated backup site",
        "coverage_pct": 70,
        "rationale": "CP-09 system backup addresses backup requirements.",
        "gaps": "DORA requires secondary processing sites with a geographic distance ensuring immediate takeover. SP 800-53 CP-09 does not mandate geographic separation. CP-06 (alternate storage) could be relevant but is not mapped here, and DORA's specific requirement for geographic distance based on risk profile of the financial entity is not in SP 800-53."
    },

    # Art. 13 — Learning and evolving
    "Art.13(1)": {
        "title": "Learning and evolving — gathering information on vulnerabilities and cyber threats",
        "coverage_pct": 65,
        "rationale": "SI-05 security alerts and advisories provides threat intelligence capability.",
        "gaps": "DORA requires financial entities to gather information on vulnerabilities, cyber threats, and ICT-related incidents from multiple sources and integrate lessons learned. SP 800-53 SI-05 covers security advisories but does not require the systematic gathering and integration of threat intelligence as comprehensively as DORA Art. 13."
    },
    "Art.13(6)": {
        "title": "Learning and evolving — ICT security awareness and training programmes",
        "coverage_pct": 85,
        "rationale": "AT-01 through AT-05 security awareness and training; CP-03 contingency training; IR-02 incident response training. Comprehensive security training coverage.",
        "gaps": "Minor: DORA requires compulsory ICT security awareness programmes and digital operational resilience training for all staff. SP 800-53 training controls are comprehensive but DORA specifically mandates training tailored to the entity's ICT risk profile and including digital operational resilience concepts."
    },

    # Art. 14 — Communication (no mappings found, so we note zero coverage)
    # Art. 15 — Simplified framework (proportionality — no SP 800-53 analog)
    # Art. 16 — Further harmonisation (regulatory, no SP 800-53 analog)

    # ── Chapter III: ICT-related Incident Management ──────────────────────

    # Art. 17 — ICT-related incident management process
    "Art.17(1)": {
        "title": "ICT-related incident management process — establishment",
        "coverage_pct": 85,
        "rationale": "IR-01 incident response policy; IR-04 incident handling. Comprehensive incident management process.",
        "gaps": "Minor: DORA requires an ICT-related incident management process that includes early warning indicators, procedures to identify, track, log, categorise, and report incidents. SP 800-53 IR family covers incident handling well but DORA requires specific integration with regulatory reporting and early warning."
    },
    "Art.17(2)": {
        "title": "ICT-related incident management process — indicators and procedures",
        "coverage_pct": 80,
        "rationale": "IR-01 incident response policy and procedures; IR-03 incident response testing.",
        "gaps": "DORA requires early warning indicators and procedures to identify and respond to ICT-related incidents. SP 800-53 provides policy and testing frameworks but DORA's specific early warning indicator requirements are more prescriptive."
    },
    "Art.17(3)": {
        "title": "ICT-related incident management process — response procedures",
        "coverage_pct": 85,
        "rationale": "IR-01 incident response policy; IR-04 incident handling directly address response procedures.",
        "gaps": "Minor: DORA requires procedures including containment, appropriate response, communication, and reporting. SP 800-53 IR-04 is comprehensive for incident handling procedures."
    },
    "Art.17(3)(c)": {
        "title": "ICT-related incident management process — incident monitoring",
        "coverage_pct": 85,
        "rationale": "IR-05 incident monitoring directly addresses continuous monitoring of ICT-related incidents.",
        "gaps": "Minimal gap. SP 800-53 IR-05 provides good coverage of incident monitoring as required by DORA."
    },
    "Art.17(3)(d)": {
        "title": "ICT-related incident management process — training and communication",
        "coverage_pct": 80,
        "rationale": "IR-02 incident response training; IR-07 incident response assistance.",
        "gaps": "Minor: DORA requires staff training on incident detection and response plus communication protocols. SP 800-53 covers training and assistance but DORA requires specific communication procedures to clients and counterparts during incidents."
    },

    # Art. 18 — Classification of ICT-related incidents
    "Art.18(1)": {
        "title": "Classification of ICT-related incidents — classification criteria",
        "coverage_pct": 70,
        "rationale": "IR-04 incident handling; IR-05 incident monitoring provide frameworks for incident handling.",
        "gaps": "DORA requires classification of ICT-related incidents based on specific criteria including number of clients affected, duration, geographic spread, data losses, criticality of services affected, and economic impact. SP 800-53 does not prescribe these specific classification criteria."
    },
    "Art.18(2)": {
        "title": "Classification of ICT-related incidents — major incident determination",
        "coverage_pct": 60,
        "rationale": "IR-04 incident handling provides incident categorisation capability.",
        "gaps": "DORA requires specific criteria for determining when an ICT-related incident is 'major' with mandatory reporting. SP 800-53 does not define 'major incident' thresholds or link incident classification to regulatory reporting obligations."
    },

    # Art. 19 — Reporting of major ICT-related incidents
    "Art.19(1)": {
        "title": "Reporting of major ICT-related incidents — notification to competent authority",
        "coverage_pct": 45,
        "rationale": "IR-06 incident reporting; SR-08 notification agreements. These provide general incident reporting frameworks.",
        "gaps": "DORA requires specific reporting to competent financial authorities using prescribed forms and timelines (initial notification, intermediate report, final report). SP 800-53 IR-06 covers reporting but not DORA's specific financial regulatory reporting timelines, formats, and authorities."
    },
    "Art.19(4)": {
        "title": "Reporting of major ICT-related incidents — incident report content and timelines",
        "coverage_pct": 40,
        "rationale": "AU-11 audit record retention; IR-06 incident reporting. Basic reporting capabilities exist.",
        "gaps": "DORA mandates specific reporting timelines (initial notification within 4 hours, intermediate report within 72 hours, final report within one month) and specific content requirements. SP 800-53 does not prescribe EU financial regulatory reporting timelines or content formats."
    },

    # Art. 20 — Harmonisation of reporting content
    "Art.20(1)": {
        "title": "Harmonisation of reporting content and templates",
        "coverage_pct": 35,
        "rationale": "IR-06 incident reporting provides a general reporting framework.",
        "gaps": "DORA Art. 20 requires harmonised reporting templates and procedures defined by ESAs. SP 800-53 has no concept of standardised EU regulatory incident report templates. This is fundamentally a regulatory harmonisation requirement outside SP 800-53 scope."
    },

    # Art. 22 — Feedback from competent authorities
    "Art.22(1)": {
        "title": "Supervisory feedback on incident reports",
        "coverage_pct": 30,
        "rationale": "IR-07 incident response assistance provides some feedback mechanism.",
        "gaps": "DORA Art. 22 requires competent authorities to provide feedback and guidance on reported incidents. SP 800-53 does not address the regulatory feedback loop between supervised entities and financial authorities. This is a regulatory relationship requirement."
    },

    # ── Chapter IV: Digital Operational Resilience Testing ────────────────

    # Art. 24 — General requirements for testing
    "Art.24(1)": {
        "title": "Digital operational resilience testing — programme establishment",
        "coverage_pct": 70,
        "rationale": "CA-01 assessment policy; CA-02 security assessments; CA-04 security certification; CA-07 continuous monitoring; IR-03 incident response testing. Good testing framework coverage.",
        "gaps": "DORA requires a comprehensive digital operational resilience testing programme with specific scope and frequency requirements. SP 800-53 provides assessment and testing controls but does not frame them as a unified operational resilience testing programme as DORA requires."
    },
    "Art.24(2)": {
        "title": "Digital operational resilience testing — proportionality and risk-based approach",
        "coverage_pct": 55,
        "rationale": "CA-02 security assessments provide risk-based assessment capability.",
        "gaps": "DORA's proportionality principle allows smaller entities a simplified testing regime while requiring comprehensive testing for significant entities. SP 800-53 applies uniformly based on system categorisation (low/moderate/high) but has no concept of proportionality based on entity size, risk profile, or systemic importance as DORA does."
    },

    # Art. 25 — Testing of ICT tools and systems
    "Art.25(1)": {
        "title": "Testing of ICT tools and systems — scope and methods",
        "coverage_pct": 75,
        "rationale": "CA-02 security assessments; CA-04 security certification; CM-04 monitoring configuration changes; RA-05 vulnerability scanning; SA-11 developer security testing. Good coverage of testing methodologies.",
        "gaps": "DORA requires testing to include vulnerability assessments, open-source analyses, network security assessments, gap analyses, physical security reviews, software composition analysis, and source code reviews. SP 800-53 covers many of these but DORA's specific list of required testing methodologies is more prescriptive."
    },
    "Art.25(2)": {
        "title": "Testing of ICT tools and systems — developer testing",
        "coverage_pct": 70,
        "rationale": "SA-11 developer security testing directly addresses testing by developers.",
        "gaps": "DORA requires that critical ICT systems and applications are tested before and after deployment, during changes, and regularly. SP 800-53 SA-11 covers developer testing but DORA's specific testing lifecycle requirements (pre-deployment, post-deployment, change-driven, periodic) are more prescriptive."
    },

    # Art. 26 and Art. 27 have no SP 800-53 mappings — handled in UNMAPPED_CLAUSES

    # ── Chapter V: Managing ICT Third-Party Risk ──────────────────────────

    # Art. 28 — General principles
    "Art.28(1)(a)": {
        "title": "ICT third-party risk management — general principles and responsibility",
        "coverage_pct": 65,
        "rationale": "AC-20 use of external systems; SA-04 acquisitions; SA-09 external services; SR-01 supply chain policy. Good foundation for third-party risk.",
        "gaps": "DORA requires financial entities to remain fully responsible for compliance even when using ICT third-party services. SP 800-53 provides supply chain controls but does not establish the specific non-delegable responsibility for third-party ICT risk as DORA does."
    },
    "Art.28(2)": {
        "title": "ICT third-party risk management — proportionate risk management strategy",
        "coverage_pct": 65,
        "rationale": "SA-09 external services; SR-01 supply chain policy; SR-03 supply chain controls and processes.",
        "gaps": "DORA requires a proportionate strategy for ICT third-party risk management accounting for the nature, scale, complexity, and importance of ICT dependencies. SP 800-53 provides supply chain controls but does not address DORA's proportionality or the specific focus on ICT dependencies for financial entities."
    },
    "Art.28(4)": {
        "title": "ICT third-party risk management — register of ICT third-party arrangements",
        "coverage_pct": 45,
        "rationale": "SR-01 supply chain policy; SR-02 supply chain risk management plan; SR-09 tamper resistance.",
        "gaps": "DORA requires a complete register of all contractual arrangements with ICT third-party service providers, distinguishing those supporting critical or important functions. SP 800-53 does not require a specific register of ICT third-party arrangements. SR-02 provides a plan but not the detailed register DORA mandates."
    },
    "Art.28(5)": {
        "title": "ICT third-party risk management — due diligence and risk assessment before contracting",
        "coverage_pct": 70,
        "rationale": "AC-20 use of external systems; MA-05 maintenance personnel; PS-07 third-party personnel; SA-09 external services; SR-02 supply chain plan; SR-04 provenance; SR-05 acquisition strategies; SR-07 supply chain operations security; SR-11 component authenticity. Broad supply chain coverage.",
        "gaps": "DORA requires specific pre-contractual due diligence including assessing whether contracting would increase concentration risk, whether the provider is established in a third country, and information security considerations. SP 800-53 supply chain controls are comprehensive but do not address DORA's specific financial sector due diligence criteria."
    },
    "Art.28(6)": {
        "title": "ICT third-party risk management — monitoring and audit rights",
        "coverage_pct": 65,
        "rationale": "SR-06 supplier assessments and reviews; SR-10 inspection of systems or components.",
        "gaps": "DORA requires contractual audit and access rights over ICT third-party providers, including on-site inspections. SP 800-53 SR-06 and SR-10 cover assessments and inspections but DORA requires specific contractual guarantees of these rights."
    },
    "Art.28(7)": {
        "title": "ICT third-party risk management — incident notification by providers",
        "coverage_pct": 55,
        "rationale": "SR-08 notification agreements addresses notification requirements between supply chain partners.",
        "gaps": "DORA requires ICT third-party providers to notify the financial entity of ICT security incidents. SP 800-53 SR-08 provides notification agreements but DORA requires specific contractual obligations for incident notification within defined timescales."
    },
    "Art.28(8)": {
        "title": "ICT third-party risk management — exit strategies",
        "coverage_pct": 30,
        "rationale": "SR-12 component disposal addresses component end-of-life.",
        "gaps": "DORA requires financial entities to have exit strategies for ICT third-party arrangements, including transition plans and data migration. SP 800-53 SR-12 covers disposal but not the comprehensive exit strategy, data portability, and transition planning that DORA mandates."
    },

    # Art. 29 — Preliminary assessment of ICT concentration risk
    "Art.29(1)": {
        "title": "ICT concentration risk — preliminary assessment",
        "coverage_pct": 35,
        "rationale": "SR-03 supply chain controls and processes; SR-09 tamper resistance provide some supply chain risk assessment.",
        "gaps": "DORA Art. 29 requires specific assessment of ICT concentration risk — whether too many critical functions depend on the same provider or a small number of providers. SP 800-53 has no concept of ICT concentration risk assessment. This is unique to financial regulation."
    },

    # Art. 30 — Key contractual provisions
    "Art.30(2)": {
        "title": "Key contractual provisions — minimum requirements for ICT service contracts",
        "coverage_pct": 55,
        "rationale": "SA-04 acquisitions; SA-09 external services; SR-03 supply chain controls. General acquisition and contractual controls.",
        "gaps": "DORA Art. 30 mandates specific contractual provisions including service levels, data locations, access rights, security measures, subcontracting conditions, and cooperation with authorities. SP 800-53 SA-04 and SA-09 address acquisitions and external services generally but do not prescribe DORA's specific contractual requirements for financial entities."
    },
    "Art.30(2)(a)": {
        "title": "Key contractual provisions — service descriptions and SLAs",
        "coverage_pct": 55,
        "rationale": "PS-07 third-party personnel security; SR-04 provenance; SR-05 acquisition strategies; SR-07 supply chain operations security; SR-11 component authenticity.",
        "gaps": "DORA requires detailed contractual service descriptions, quantitative and qualitative SLAs, and binding performance targets. SP 800-53 supply chain controls cover vetting and assessment but do not mandate specific SLA structures or performance metrics in contracts."
    },
    "Art.30(2)(g)": {
        "title": "Key contractual provisions — termination and data return",
        "coverage_pct": 30,
        "rationale": "SR-12 component disposal addresses end-of-life considerations.",
        "gaps": "DORA requires contractual provisions for termination, including transition periods, data return, secure deletion, and transfer assistance. SP 800-53 SR-12 covers disposal but not the comprehensive termination, data return, and transition provisions DORA mandates."
    },
    "Art.30(3)": {
        "title": "Key contractual provisions — critical or important functions",
        "coverage_pct": 55,
        "rationale": "SA-04 acquisitions; SA-09 external services; SR-06 supplier assessments and reviews.",
        "gaps": "DORA requires enhanced contractual provisions when ICT third-party services support critical or important functions, including full service level descriptions, notice periods, reporting obligations, and exit plans. SP 800-53 does not differentiate contractual requirements based on function criticality as DORA does."
    },

    # ── Chapter VI: Information-sharing arrangements ──────────────────────

    "Art.45(1)": {
        "title": "Information-sharing arrangements — voluntary sharing of cyber threat intelligence",
        "coverage_pct": 50,
        "rationale": "AT-05 contacts with security groups and associations provides information sharing capability.",
        "gaps": "DORA encourages voluntary sharing of cyber threat information among financial entities within trusted communities. SP 800-53 AT-05 covers security group contacts but does not address DORA's specific framework for trusted information-sharing arrangements within the financial sector."
    },
}

# Additional DORA articles that have no SP 800-53 mappings at all — included for completeness
UNMAPPED_CLAUSES = {
    "Art.14": {
        "title": "Communication — policies for internal and external communication on ICT-related incidents",
        "coverage_pct": 25,
        "rationale": "No direct SP 800-53 controls are mapped. IR-06 and IR-07 cover reporting and assistance generally but not DORA's specific communication requirements.",
        "gaps": "DORA Art. 14 requires policies for communicating ICT-related incidents to clients, counterparts, and the public, including responsible communication staff and media handling. SP 800-53 does not address external stakeholder communication policies for ICT incidents."
    },
    "Art.26": {
        "title": "Advanced testing — threat-led penetration testing (TLPT)",
        "coverage_pct": 25,
        "rationale": "No direct SP 800-53 controls are mapped to TLPT. CA-02 and CA-08 (not in current baselines) provide general penetration testing concepts.",
        "gaps": "DORA Art. 26 mandates threat-led penetration testing (TLPT) based on the TIBER-EU framework for significant financial entities. SP 800-53 has no equivalent to TLPT. CA-08 penetration testing exists but does not require threat intelligence-led testing, red team exercises, or TIBER-EU methodology. This is a major gap."
    },
    "Art.27": {
        "title": "Requirements for TLPT testers — qualifications and independence",
        "coverage_pct": 10,
        "rationale": "No SP 800-53 controls address tester qualification or independence requirements for penetration testing.",
        "gaps": "DORA Art. 27 requires TLPT testers to be certified, have professional indemnity insurance, and be accredited by financial authorities. SP 800-53 has no requirements for tester qualifications, accreditation, or independence. This is entirely outside SP 800-53 scope."
    },
    "Art.15": {
        "title": "Simplified ICT risk management framework — proportionality for smaller entities",
        "coverage_pct": 0,
        "rationale": "No SP 800-53 controls address proportionality or simplified frameworks for smaller entities.",
        "gaps": "DORA Art. 15 provides a simplified ICT risk management framework for certain smaller financial entities (e.g., small investment firms, payment institutions). SP 800-53 has no concept of entity-size-based proportionality. The low/moderate/high baseline approach is system-based, not entity-based."
    },
    "Art.16": {
        "title": "Further harmonisation of ICT risk management tools, methods, processes, and policies",
        "coverage_pct": 0,
        "rationale": "No SP 800-53 controls address EU regulatory harmonisation mandates.",
        "gaps": "DORA Art. 16 empowers ESAs to develop regulatory technical standards for further harmonisation of ICT risk management. This is a regulatory harmonisation provision with no SP 800-53 equivalent."
    },
}


def load_manifest():
    """Load the controls manifest file."""
    manifest_path = os.path.join(CONTROLS_DIR, '_manifest.json')
    with open(manifest_path) as f:
        return json.load(f)


def build_reverse_mappings(manifest):
    """Build reverse mapping: DORA clause -> list of SP 800-53 control IDs."""
    reverse = defaultdict(list)

    for ctrl_entry in manifest['controls']:
        ctrl_file = os.path.join(CONTROLS_DIR, ctrl_entry['file'])
        with open(ctrl_file) as f:
            ctrl = json.load(f)

        dora_clauses = ctrl.get('compliance_mappings', {}).get('dora', [])
        for clause_id in dora_clauses:
            # Normalise control ID: convert e.g. "AC-01" manifest id to
            # human-readable "AC-1" style used in coverage JSONs
            ctrl_id = ctrl['id']
            reverse[clause_id].append(ctrl_id)

    # Sort and deduplicate controls for each clause
    for clause_id in reverse:
        reverse[clause_id] = sorted(set(reverse[clause_id]))

    return dict(reverse)


def normalise_control_id(ctrl_id):
    """Convert control IDs like AC-01 to AC-1 for the coverage output format.

    Checks the NIS2 reference file for the formatting convention used.
    In the NIS2 file, controls use formats like 'PM-1', 'RA-3', 'IR-6'.
    """
    parts = ctrl_id.split('-')
    if len(parts) == 2:
        family = parts[0]
        num = parts[1].lstrip('0') or '0'
        return f"{family}-{num}"
    return ctrl_id


def build_coverage_json(reverse_mappings):
    """Build the complete coverage JSON structure."""
    clauses = []

    # Process mapped clauses from actual control data
    for clause_id, controls in sorted(reverse_mappings.items()):
        meta = CLAUSE_METADATA.get(clause_id)
        if meta is None:
            # Clause exists in data but not in our metadata — skip with warning
            print(f"  WARNING: No metadata for clause '{clause_id}' "
                  f"(mapped by: {', '.join(controls)})", file=sys.stderr)
            continue

        normalised_controls = [normalise_control_id(c) for c in controls]

        clauses.append({
            "id": clause_id,
            "title": meta["title"],
            "controls": normalised_controls,
            "coverage_pct": meta["coverage_pct"],
            "rationale": meta["rationale"],
            "gaps": meta["gaps"],
        })

    # Add unmapped clauses (DORA articles with no SP 800-53 control mappings)
    for clause_id, meta in sorted(UNMAPPED_CLAUSES.items()):
        clauses.append({
            "id": clause_id,
            "title": meta["title"],
            "controls": [],
            "coverage_pct": meta["coverage_pct"],
            "rationale": meta["rationale"],
            "gaps": meta["gaps"],
        })

    # Sort clauses by article number for readable output
    def clause_sort_key(clause):
        """Sort by article number, then sub-clause."""
        cid = clause["id"]
        # Extract "Art.X" and the rest
        if cid.startswith("Art."):
            rest = cid[4:]
            # Split on first '(' to separate article number from sub-clauses
            parts = rest.split('(', 1)
            try:
                art_num = int(parts[0])
            except ValueError:
                art_num = 999
            sub = '(' + parts[1] if len(parts) > 1 else ''
            return (art_num, sub)
        return (999, cid)

    clauses.sort(key=clause_sort_key)

    # Compute summary statistics
    total_clauses = len(clauses)
    coverage_values = [c["coverage_pct"] for c in clauses]
    avg_coverage = round(sum(coverage_values) / total_clauses, 1) if total_clauses > 0 else 0

    full_count = sum(1 for v in coverage_values if 85 <= v <= 100)
    substantial_count = sum(1 for v in coverage_values if 65 <= v <= 84)
    partial_count = sum(1 for v in coverage_values if 40 <= v <= 64)
    weak_count = sum(1 for v in coverage_values if 1 <= v <= 39)
    none_count = sum(1 for v in coverage_values if v == 0)

    return {
        "$schema": "../schema/framework-coverage.schema.json",
        "framework_id": "dora",
        "framework_name": "EU DORA (Digital Operational Resilience Act)",
        "metadata": {
            "source": "SP800-53v5_Control_Mappings",
            "version": "1.0",
            "disclaimer": "Based on publicly available crosswalks and expert analysis of Regulation (EU) 2022/2554. Validate with qualified assessors for compliance/audit use. DORA has sector-specific requirements for financial entities that extend beyond SP 800-53 scope."
        },
        "weight_scale": {
            "full": {"min": 85, "max": 100, "label": "Fully addressed"},
            "substantial": {"min": 65, "max": 84, "label": "Well addressed, notable gaps"},
            "partial": {"min": 40, "max": 64, "label": "Partially addressed"},
            "weak": {"min": 1, "max": 39, "label": "Weakly addressed"},
            "none": {"min": 0, "max": 0, "label": "No mapping"},
        },
        "clauses": clauses,
        "summary": {
            "total_clauses": total_clauses,
            "average_coverage": avg_coverage,
            "full_count": full_count,
            "substantial_count": substantial_count,
            "partial_count": partial_count,
            "weak_count": weak_count,
            "none_count": none_count,
        },
    }


def main():
    print("Loading controls manifest...")
    manifest = load_manifest()
    print(f"  Found {len(manifest['controls'])} controls")

    print("Building reverse mappings (DORA clause -> SP 800-53 controls)...")
    reverse_mappings = build_reverse_mappings(manifest)
    print(f"  Found {len(reverse_mappings)} DORA clauses with mappings")

    print("Building coverage JSON...")
    coverage = build_coverage_json(reverse_mappings)

    # Ensure output directory exists
    os.makedirs(COVERAGE_DIR, exist_ok=True)

    print(f"Writing {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(coverage, f, indent=2)
        f.write('\n')

    # Print summary
    summary = coverage['summary']
    print(f"\nDORA Coverage Summary:")
    print(f"  Total clauses:      {summary['total_clauses']}")
    print(f"  Average coverage:   {summary['average_coverage']}%")
    print(f"  Full (85-100%):     {summary['full_count']}")
    print(f"  Substantial (65-84%): {summary['substantial_count']}")
    print(f"  Partial (40-64%):   {summary['partial_count']}")
    print(f"  Weak (1-39%):       {summary['weak_count']}")
    print(f"  None (0%):          {summary['none_count']}")
    print(f"\nOutput written to: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
