#!/usr/bin/env python3
"""
Generate SOC 2 Trust Services Criteria (TSC) coverage analysis JSON.

Reads all SP 800-53 Rev 5 control JSON files, builds reverse mappings
from SOC 2 TSC clauses to SP 800-53 controls, and produces a coverage
analysis file at data/framework-coverage/soc2-tsc.json.

The coverage percentages, rationale, and gap analysis represent expert
assessments of how well SP 800-53 Rev 5 addresses each SOC 2 TSC 2017
criterion and its Points of Focus (POF).
"""

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
CONTROLS_DIR = DATA_DIR / "controls"
MANIFEST_PATH = CONTROLS_DIR / "_manifest.json"
OUTPUT_PATH = DATA_DIR / "framework-coverage" / "soc2-tsc.json"

# ---------------------------------------------------------------------------
# SOC 2 TSC 2017 — Official Criteria Titles and Points of Focus
# ---------------------------------------------------------------------------
# Each entry: (clause_id, title, coverage_pct, rationale, gaps)
# POF sub-items included where they appear in the control mappings.
# Coverage percentages are expert assessments comparing SP 800-53 Rev 5
# scope against SOC 2 TSC requirements.
# ---------------------------------------------------------------------------

SOC2_TSC_CLAUSES = [
    # =========================================================================
    # CC1: Control Environment (COSO Principle 1-5)
    # =========================================================================
    (
        "CC1.1",
        "COSO Principle 1: The entity demonstrates a commitment to integrity and ethical values",
        35,
        "SP 800-53 PS-8 addresses personnel sanctions and PL-4 covers rules of behavior, which partially address integrity expectations. However, SP 800-53 is a technical/operational control catalog and does not directly address organizational commitment to integrity, ethical values, or tone at the top.",
        "SOC 2 CC1.1 requires demonstration of commitment to integrity and ethical values including codes of conduct, board oversight of ethics, and deviation remediation. SP 800-53 lacks controls for ethical culture establishment, codes of conduct, and governance-level integrity commitments."
    ),
    (
        "CC1.1-POF1",
        "CC1.1 POF1: Sets the tone at the top — The board of directors and management demonstrate commitment to integrity and ethical values",
        20,
        "SP 800-53 PM-1 and PM-2 establish security program leadership but do not address tone-at-the-top for integrity and ethics.",
        "No SP 800-53 equivalent for board/management setting ethical tone. SP 800-53 focuses on security program management, not organizational ethics and integrity culture."
    ),
    (
        "CC1.1-POF2",
        "CC1.1 POF2: Establishes standards of conduct — Expectations of the board and senior management concerning integrity and ethical values are defined",
        25,
        "PL-4 (Rules of Behavior) partially covers acceptable conduct standards but is focused on system use rather than broad ethical standards.",
        "SP 800-53 PL-4 covers system use rules but not enterprise-wide standards of conduct, codes of ethics, or integrity expectations for all personnel."
    ),
    (
        "CC1.1-POF3",
        "CC1.1 POF3: Evaluates adherence to standards of conduct — Processes are in place to evaluate performance against standards of conduct",
        20,
        "PS-8 (Personnel Sanctions) addresses consequences for violations but does not cover systematic evaluation of adherence.",
        "No SP 800-53 control for systematic evaluation of adherence to conduct standards. PS-8 is reactive (sanctions) rather than proactive (evaluation)."
    ),
    (
        "CC1.1-POF4",
        "CC1.1 POF4: Addresses deviations in a timely manner — Deviations from standards of conduct are identified and remedied in a timely manner",
        30,
        "PS-8 (Personnel Sanctions) and IR-4 (Incident Handling) partially address deviation handling for security matters.",
        "SP 800-53 addresses security-specific deviations but not general conduct deviations. No control for non-security behavioral deviation remediation."
    ),
    (
        "CC1.2",
        "COSO Principle 2: The board of directors demonstrates independence from management and exercises oversight of the development and performance of internal control",
        25,
        "PM-1 and PM-2 establish security program governance roles. CA-2 and CA-7 provide assessment and monitoring. However, board independence and oversight of internal control broadly are governance matters outside SP 800-53 scope.",
        "SOC 2 CC1.2 requires board independence, competence, and oversight of internal control. SP 800-53 does not address board governance, independence requirements, or board-level oversight of the control system."
    ),
    (
        "CC1.2-POF1",
        "CC1.2 POF1: Establishes oversight responsibilities — The board identifies and accepts its oversight responsibilities in relation to established requirements and expectations",
        20,
        "PM-2 assigns security roles but does not address board-level oversight responsibilities.",
        "SP 800-53 focuses on operational security roles, not board governance responsibilities. No control for board oversight establishment or acceptance of fiduciary duties."
    ),
    (
        "CC1.3",
        "COSO Principle 3: Management establishes, with board oversight, structures, reporting lines, and appropriate authorities and responsibilities in the pursuit of objectives",
        45,
        "PM-1 (Security Program Plan), PM-2 (Information Security Program Leadership Role), and PM-10 (Authorization Process) establish organizational structures and responsibilities for security. Partially addresses this criterion within security scope.",
        "SOC 2 CC1.3 requires organizational structure design with clear reporting lines and authority for all objectives. SP 800-53 covers security-specific organizational structure but not enterprise-wide organizational design, authority delegation, or non-security reporting lines."
    ),
    (
        "CC1.3-POF1",
        "CC1.3 POF1: Considers all structures of the entity — Management and the board consider the multiple structures used to support the achievement of objectives",
        30,
        "PM-7 (Enterprise Architecture) and PM-1 consider security program structure but not all organizational structures.",
        "SP 800-53 addresses security program structure only. SOC 2 requires consideration of all organizational structures including business units, legal entities, and geographic locations."
    ),
    (
        "CC1.4",
        "COSO Principle 4: The entity demonstrates a commitment to attract, develop, and retain competent individuals in alignment with objectives",
        55,
        "PM-13 (Information Security Workforce), AT-1/AT-2/AT-3 (Training), and PS-2 (Position Categorization) address workforce competence for security roles. Good coverage within security scope.",
        "SOC 2 CC1.4 extends to all personnel, not just security staff. SP 800-53 focuses on security workforce competence. General HR competency management, career development, and succession planning are not covered."
    ),
    (
        "CC1.4-POF1",
        "CC1.4 POF1: Establishes policies and practices — Policies and practices reflect expectations of competence necessary to support the achievement of objectives",
        50,
        "AT-1 establishes training policy; PM-13 addresses security workforce competence requirements.",
        "Covers security competence policies. Gaps in broader organizational competence requirements, non-security role expectations, and enterprise-wide competency frameworks."
    ),
    (
        "CC1.4-POF2",
        "CC1.4 POF2: Evaluates competence and addresses shortcomings — The board and management evaluate competence and address shortcomings",
        40,
        "PM-13 includes workforce planning and AT-4 tracks training records, enabling some competence evaluation.",
        "SP 800-53 supports competence tracking for security roles. Does not cover board-level competence evaluation, executive competence assessment, or enterprise-wide competency gap remediation."
    ),
    (
        "CC1.4-POF3",
        "CC1.4 POF3: Attracts, develops, and retains individuals — The entity provides mentoring and training to attract, develop, and retain sufficient and competent personnel",
        45,
        "AT-2, AT-3 provide training; PM-13 addresses workforce development.",
        "Good security training coverage. Gaps in general talent acquisition, mentoring programs, retention strategies, and non-security professional development."
    ),
    (
        "CC1.4-POF4",
        "CC1.4 POF4: Plans and prepares for succession — Senior management and the board develop succession plans for key roles",
        15,
        "No direct SP 800-53 control for succession planning.",
        "Significant gap. SP 800-53 does not address succession planning. PM-2 identifies key security roles but no succession or continuity of leadership requirements."
    ),
    (
        "CC1.5",
        "COSO Principle 5: The entity holds individuals accountable for their internal control responsibilities in the pursuit of objectives",
        50,
        "PS-1 (Personnel Security Policy), PS-8 (Personnel Sanctions), PM-2 (Role Assignment), and PL-4 (Rules of Behavior) establish accountability mechanisms for security responsibilities.",
        "SOC 2 CC1.5 requires accountability for all internal control responsibilities. SP 800-53 covers security accountability through sanctions and role assignment but lacks broader accountability structures, performance metrics tied to controls, and incentive alignment."
    ),
    (
        "CC1.5-POF1",
        "CC1.5 POF1: Enforces accountability through structures, authorities, and responsibilities — Management and the board establish mechanisms to communicate and hold individuals accountable",
        45,
        "PM-2 assigns authority; PS-8 enforces through sanctions; PL-4 communicates expectations.",
        "Covers security-specific accountability. Gaps in enterprise-wide accountability structures, performance measurement for control responsibilities, and board-level accountability mechanisms."
    ),

    # =========================================================================
    # CC2: Communication and Information (COSO Principle 13-15)
    # =========================================================================
    (
        "CC2.1",
        "COSO Principle 13: The entity obtains or generates and uses relevant, quality information to support the functioning of internal control",
        55,
        "AU-2/AU-3/AU-6 (Audit Events/Content/Review), SI-4 (System Monitoring), and RA-3 (Risk Assessment) generate and use security-relevant information. CA-7 (Continuous Monitoring) uses control information systematically.",
        "Good coverage for security information quality. SOC 2 CC2.1 extends to all information supporting internal control, including financial, operational, and compliance information. SP 800-53 focuses on security/audit information only."
    ),
    (
        "CC2.1-POF1",
        "CC2.1 POF1: Identifies information requirements — A process is in place to identify information required to support internal control",
        45,
        "AU-2 identifies auditable events; RA-3 identifies risk information needs.",
        "Covers security information requirements. Gaps in identifying information requirements for non-security internal controls, financial reporting, and operational effectiveness."
    ),
    (
        "CC2.2",
        "COSO Principle 14: The entity internally communicates information, including objectives and responsibilities for internal control, necessary to support the functioning of internal control",
        50,
        "AT-2 (Security Awareness), PM-1 (Program Plan), PL-4 (Rules of Behavior), and IR-7 (Incident Response Assistance) support internal communication of security-related information and responsibilities.",
        "SOC 2 CC2.2 requires communication of all internal control objectives and responsibilities. SP 800-53 covers security communication well but does not address enterprise-wide internal control communication, financial control communication, or management reporting on control effectiveness."
    ),
    (
        "CC2.2-POF1",
        "CC2.2 POF1: Communicates internal control information — A process is in place to communicate required information to enable all personnel to understand and carry out their responsibilities",
        50,
        "AT-2 communicates security awareness; PL-4 communicates rules of behavior; PM-1 disseminates security program plan.",
        "Security communication well addressed. Gaps in communicating non-security internal control responsibilities, financial control procedures, and operational control expectations to all personnel."
    ),
    (
        "CC2.2-POF3",
        "CC2.2 POF3: Communicates with the board of directors — Information necessary for the board to oversee internal control is communicated",
        25,
        "PM-6 (Measures of Performance) and CA-2 (Security Assessments) produce reports that could inform board communication.",
        "SP 800-53 does not require board-level reporting. PM-6 produces performance data but no control specifies board communication cadence, format, or content requirements."
    ),
    (
        "CC2.2-POF7",
        "CC2.2 POF7: Communicates objectives and changes to objectives — The entity communicates its objectives and changes to those objectives",
        40,
        "PM-1 includes security program objectives; CM-3 communicates configuration changes.",
        "Security objectives communicated via PM-1. Gaps in communicating enterprise-wide control objectives and changes to all internal control objectives beyond security."
    ),
    (
        "CC2.2-POF10",
        "CC2.2 POF10: Provides separate communication lines — Separate communication channels such as whistle-blower hotlines are in place and serve as fail-safe mechanisms",
        10,
        "No SP 800-53 control addresses separate communication lines or whistle-blower mechanisms.",
        "Significant gap. SP 800-53 does not address anonymous reporting channels, whistle-blower hotlines, or alternative communication paths for control concerns."
    ),
    (
        "CC2.3",
        "COSO Principle 15: The entity communicates with external parties regarding matters affecting the functioning of internal control",
        45,
        "IR-6 (Incident Reporting) covers external incident communication; PM-15 (Security Groups/Associations) addresses external security community communication; SA-9 (External System Services) addresses service provider communication.",
        "SOC 2 CC2.3 requires communication with external parties (regulators, customers, suppliers, auditors) about internal control matters. SP 800-53 covers security-specific external communication but not broader stakeholder communication about control effectiveness."
    ),
    (
        "CC2.3-POF1",
        "CC2.3 POF1: Communicates to external parties — Processes are in place to communicate relevant information to external parties",
        45,
        "IR-6 covers incident reporting to authorities; PM-15 covers security community engagement; CA-3 manages information exchange agreements.",
        "Security-specific external communication covered. Gaps in customer communication about controls, regulatory reporting beyond incidents, and supplier communication about control expectations."
    ),
    (
        "CC2.3-POF12",
        "CC2.3 POF12: Provides information on notification agreements — The entity notifies external parties of system changes affecting their operation",
        40,
        "SR-8 (Notification Agreements) directly addresses notification requirements in supply chain. CA-3 covers information exchange agreements.",
        "SR-8 covers supply chain notification. Gaps in broader customer notification about system changes, service-level change communication, and proactive stakeholder notification beyond supply chain."
    ),

    # =========================================================================
    # CC3: Risk Assessment (COSO Principle 6-9)
    # =========================================================================
    (
        "CC3.1",
        "COSO Principle 6: The entity specifies objectives with sufficient clarity to enable the identification and assessment of risks relating to objectives",
        50,
        "PM-1 (Security Program Plan) and PM-9 (Risk Management Strategy) define security objectives. RA-3 (Risk Assessment) requires clear risk context.",
        "SOC 2 CC3.1 requires clear specification of all objectives (operational, reporting, compliance). SP 800-53 covers security objective specification but not enterprise-wide objective setting for risk assessment purposes."
    ),
    (
        "CC3.2",
        "COSO Principle 7: The entity identifies risks to the achievement of its objectives across the entity and analyzes risks as a basis for determining how the risks should be managed",
        75,
        "RA-1/RA-2/RA-3/RA-5 (Risk Assessment family) comprehensively cover risk identification and analysis. PM-9 (Risk Management Strategy) and PM-28 (Risk Framing) provide risk management framework.",
        "Strong coverage for security risk identification and analysis. Minor gaps: SOC 2 CC3.2 includes operational and compliance risks beyond information security. Enterprise-wide risk identification across all objective categories is broader than SP 800-53 scope."
    ),
    (
        "CC3.2-POF1",
        "CC3.2 POF1: Includes entity, subsidiary, division, operating unit, and functional levels",
        60,
        "RA-3 covers risk assessment at system and organizational levels. PM-9 addresses organization-wide risk strategy.",
        "SP 800-53 addresses risk at system and organizational levels. Gaps in structured risk assessment across subsidiary/division/functional levels as distinct entities."
    ),
    (
        "CC3.3",
        "COSO Principle 8: The entity considers the potential for fraud in assessing risks to the achievement of objectives",
        30,
        "AC-5 (Separation of Duties) and AU-6 (Audit Review) support fraud detection. SI-4 (System Monitoring) can detect anomalous behavior.",
        "SP 800-53 provides controls useful for fraud prevention/detection but does not explicitly require fraud risk assessment. SOC 2 CC3.3 requires specific consideration of fraud risk including incentives/pressures, opportunities, attitudes/rationalizations."
    ),
    (
        "CC3.3-POF1",
        "CC3.3 POF1: Considers various types of fraud — The entity considers fraudulent reporting, possible loss of assets, and corruption",
        20,
        "AU-6 and SI-4 provide monitoring that could detect fraud indicators.",
        "Significant gap. SP 800-53 does not require specific fraud risk assessment. No controls for analyzing fraud triangle factors (incentive, opportunity, rationalization) or assessing fraudulent reporting risk."
    ),
    (
        "CC3.4",
        "COSO Principle 9: The entity identifies and assesses changes that could significantly impact the system of internal control",
        65,
        "CM-3/CM-4 (Change Control/Impact Analysis) address change assessment. RA-3 includes reassessment triggers. CA-7 (Continuous Monitoring) detects control-impacting changes.",
        "Good coverage for security-impacting changes. SOC 2 CC3.4 extends to all changes affecting internal control including regulatory, technology, business model, and personnel changes. SP 800-53 focuses on IT configuration and security-relevant changes."
    ),
    (
        "CC3.4-POF1",
        "CC3.4 POF1: Assesses changes in the external environment — The entity considers changes in regulatory, economic, and physical environments",
        35,
        "SI-5 (Security Alerts/Advisories) and PM-16 (Threat Awareness) address external security environment changes.",
        "SP 800-53 covers external security threat landscape. Gaps in assessing regulatory environment changes, economic condition changes, and broader external factor impacts on internal control."
    ),
    (
        "CC3.4-POF2",
        "CC3.4 POF2: Assesses changes in the business model — The entity considers the impact of new business lines, altered compositions of existing business lines, and acquired or divested business operations",
        15,
        "PM-7 (Enterprise Architecture) touches on business alignment but not business model change assessment.",
        "Significant gap. SP 800-53 does not address business model change impact on controls, M&A integration risks, or new business line control requirements."
    ),
    (
        "CC3.4-POF3",
        "CC3.4 POF3: Assesses changes in leadership — The entity considers changes in management and other personnel",
        25,
        "PS-4 (Personnel Termination) and PS-5 (Personnel Transfer) address personnel changes from a security perspective.",
        "SP 800-53 covers access changes due to personnel transitions. Does not address leadership change impact assessment on internal control effectiveness or organizational risk profile."
    ),

    # =========================================================================
    # CC4: Monitoring Activities (COSO Principle 16-17)
    # =========================================================================
    (
        "CC4.1",
        "COSO Principle 16: The entity selects, develops, and performs ongoing and/or separate evaluations to ascertain whether the components of internal control are present and functioning",
        70,
        "CA-2 (Security Assessments), CA-7 (Continuous Monitoring), PM-6 (Measures of Performance), and AU-6 (Audit Review) provide strong evaluation capabilities for security controls.",
        "Good coverage for security control evaluation. SOC 2 CC4.1 extends to all internal control components. Gaps in evaluating non-security controls, financial controls, and entity-level governance controls."
    ),
    (
        "CC4.1-POF1",
        "CC4.1 POF1: Considers a mix of ongoing and separate evaluations — Management includes a balance of ongoing evaluations built into processes and separate evaluations",
        70,
        "CA-7 provides ongoing monitoring; CA-2 provides separate assessments. Good balance for security controls.",
        "Well-addressed for security. Gaps in ongoing/separate evaluation methodology for non-security internal controls."
    ),
    (
        "CC4.2",
        "COSO Principle 17: The entity evaluates and communicates internal control deficiencies in a timely manner to those parties responsible for taking corrective action, including senior management and the board of directors, as appropriate",
        65,
        "CA-5 (POA&M) tracks deficiencies; CA-2 reports assessment results; PM-6 reports performance metrics. IR-6 covers incident reporting.",
        "Good deficiency tracking and reporting for security. SOC 2 CC4.2 requires communication to senior management and board. SP 800-53 tracks deficiencies through POA&M but board-level reporting is not explicitly required."
    ),
    (
        "CC4.2-POF1",
        "CC4.2 POF1: Assesses results — Management and the board assess results of ongoing and separate evaluations",
        55,
        "CA-2 results feed into authorization decisions; PM-6 provides performance measures; CA-5 tracks remediation.",
        "Security assessment results well-managed. Gaps in board-level assessment of results and management review of non-security control evaluations."
    ),
    (
        "CC4.2-POF2",
        "CC4.2 POF2: Communicates deficiencies — Deficiencies are communicated to parties responsible for taking corrective action and to senior management and the board as appropriate",
        55,
        "CA-5 communicates deficiencies through POA&M; IR-6 reports incidents; PM-6 provides metrics.",
        "Security deficiency communication via POA&M is well-established. Gaps in board-level deficiency communication, non-security control deficiency reporting, and formal escalation paths for significant deficiencies."
    ),

    # =========================================================================
    # CC5: Control Activities (COSO Principle 10-12)
    # =========================================================================
    (
        "CC5.1",
        "COSO Principle 10: The entity selects and develops control activities that contribute to the mitigation of risks to the achievement of objectives to acceptable levels",
        70,
        "The entire SP 800-53 catalog is designed to provide control activities mitigating security risks. PM-9 (Risk Management Strategy) guides control selection. CA-2 validates control effectiveness.",
        "Strong coverage for security control selection. SOC 2 CC5.1 extends to all risk mitigation activities including operational and compliance controls. SP 800-53 is specifically a security control catalog."
    ),
    (
        "CC5.2",
        "COSO Principle 11: The entity also selects and develops general control activities over technology to support the achievement of objectives",
        85,
        "SP 800-53 comprehensively covers technology general controls across access control (AC), change management (CM), system protection (SC), and monitoring (AU/SI). This is the core strength of SP 800-53.",
        "Excellent coverage for technology general controls. SP 800-53 is specifically designed as an IT control catalog. Minor gap: SOC 2 frames these as supporting all objectives; SP 800-53 frames them as security controls."
    ),
    (
        "CC5.2-POF1",
        "CC5.2 POF1: Determines dependency between the use of technology in business processes and technology general controls",
        60,
        "PM-7 (Enterprise Architecture) and SA-3 (System Development Life Cycle) address technology-business alignment.",
        "SP 800-53 addresses technology controls but the explicit dependency mapping between business processes and IT general controls is not directly required."
    ),
    (
        "CC5.3",
        "COSO Principle 12: The entity deploys control activities through policies that establish what is expected and in procedures that put policies into action",
        80,
        "SP 800-53 consistently requires policies and procedures across all control families (every -1 control). PL-1 (Planning Policy), PM-1 (Program Plan), and the policy/procedure pattern is a fundamental SP 800-53 design principle.",
        "Strong coverage. Every SP 800-53 family starts with a policy and procedure control. Minor gap: SOC 2 expects policies and procedures for all control activities, not just security."
    ),
    (
        "CC5.3-POF1",
        "CC5.3 POF1: Establishes policies and procedures to support deployment of management's directives",
        80,
        "Every SP 800-53 control family includes a -1 control requiring policy and procedures. Consistent pattern across all families.",
        "Excellent for security policies and procedures. Minor gap in non-security management directive deployment."
    ),
    (
        "CC5.3-POF6",
        "CC5.3 POF6: Reassesses policies and procedures — Management periodically reassesses policies and procedures for continued relevance and effectiveness",
        75,
        "All -1 controls require periodic review and update of policies and procedures. PM-1 requires program plan updates.",
        "SP 800-53 requires periodic review of all security policies. Minor gap in linking policy reassessment to changing business conditions and non-security requirements."
    ),

    # =========================================================================
    # CC6: Logical and Physical Access Controls
    # =========================================================================
    (
        "CC6.1",
        "Logical and Physical Access Controls — The entity implements logical access security software, infrastructure, and architectures over protected information assets to protect them from security events to meet the entity's objectives",
        90,
        "AC family (AC-1 through AC-20), IA family (IA-1 through IA-7), PE family (PE-1 through PE-19), and SC-7 (Boundary Protection) provide comprehensive logical and physical access controls.",
        "Excellent coverage. SP 800-53 access control is among its strongest areas. Minor gap: SOC 2 frames this in terms of protecting against events to meet entity objectives; SP 800-53 is more technically prescriptive."
    ),
    (
        "CC6.1-POF1",
        "CC6.1 POF1: Identifies and manages the inventory of information assets — The entity identifies and manages information assets",
        85,
        "CM-8 (System Component Inventory) and PM-5 (System Inventory) cover asset identification and management.",
        "Good asset inventory coverage. Minor gap in non-IT information asset inventory (paper records, intellectual property catalogs)."
    ),
    (
        "CC6.1-POF2",
        "CC6.1 POF2: Restricts logical access — Access to information assets is restricted through logical access security measures",
        95,
        "AC-3 (Access Enforcement), AC-6 (Least Privilege), AC-2 (Account Management), and AC-17 (Remote Access) comprehensively cover logical access restriction.",
        "Minimal gap. SP 800-53 logical access controls are comprehensive."
    ),
    (
        "CC6.1-POF3",
        "CC6.1 POF3: Considers network segmentation — Network segmentation is implemented to restrict access",
        95,
        "SC-7 (Boundary Protection) directly addresses network segmentation. AC-4 (Information Flow Enforcement) controls data flow between segments.",
        "Minimal gap. SC-7 is comprehensive for network segmentation."
    ),
    (
        "CC6.1-POF4",
        "CC6.1 POF4: Manages points of access — Points of access to information assets are managed and protected",
        90,
        "SC-7 (Boundary Protection) manages network access points; AC-17 (Remote Access) manages remote entry points; PE-3 (Physical Access Control) manages physical access points.",
        "Strong coverage across logical and physical access points. Minor gap in comprehensive access point inventory as a unified concept."
    ),
    (
        "CC6.1-POF5",
        "CC6.1 POF5: Restricts access to information assets — Access to information assets is restricted through identity management",
        95,
        "IA-2 (User Identification/Authentication), IA-4 (Identifier Management), IA-5 (Authenticator Management), and AC-2 (Account Management) provide comprehensive identity-based access restriction.",
        "Minimal gap. SP 800-53 identity and access management is thorough."
    ),
    (
        "CC6.1-POF6",
        "CC6.1 POF6: Manages identification and authentication — User identification and authentication is managed",
        95,
        "IA family comprehensively covers identification and authentication management including MFA, authenticator lifecycle, and identity proofing.",
        "Minimal gap."
    ),
    (
        "CC6.1-POF7",
        "CC6.1 POF7: Manages credentials for infrastructure and software — System and application credentials are managed",
        90,
        "IA-5 (Authenticator Management) covers credential management; CM-6 (Configuration Settings) includes credential configuration; SA-4 requires security capabilities in acquisitions.",
        "Strong coverage. Minor gap in specific application-level credential management and service account lifecycle."
    ),
    (
        "CC6.1-POF8",
        "CC6.1 POF8: Uses encryption to protect data — Encryption is used to protect data at rest and in transit",
        90,
        "SC-12 (Cryptographic Key Management), SC-13 (Cryptographic Protection), SC-8 (Transmission Confidentiality/Integrity), SC-28 (Protection at Rest) provide comprehensive encryption coverage.",
        "Excellent encryption coverage. Minor gap: SOC 2 frames encryption in access control context; SP 800-53 treats it as system/communications protection."
    ),
    (
        "CC6.1-POF9",
        "CC6.1 POF9: Protects encryption keys — Encryption keys are managed to protect data",
        90,
        "SC-12 (Cryptographic Key Establishment and Management) directly addresses key management including generation, distribution, storage, and destruction.",
        "Strong coverage. SC-12 comprehensively addresses key management lifecycle."
    ),
    (
        "CC6.2",
        "Prior to issuing system credentials and granting system access, the entity registers and authorizes new internal and external users whose access is administered by the entity",
        90,
        "AC-2 (Account Management) covers user registration, authorization, and provisioning. PS-3 (Personnel Screening) covers pre-access screening. IA-4 (Identifier Management) covers credential issuance.",
        "Excellent coverage. AC-2 directly addresses user registration and authorization prior to access. Minor gap in external user lifecycle management specifics."
    ),
    (
        "CC6.2-POF1",
        "CC6.2 POF1: Controls access credentials to protected assets — New internal and external users are registered and authorized prior to being issued credentials and granted access",
        90,
        "AC-2 requires authorization before account creation; PS-3 requires screening; IA-4 manages identifiers.",
        "Minimal gap. Pre-access authorization well covered."
    ),
    (
        "CC6.3",
        "The entity authorizes, modifies, or removes access to data, software, functions, and other protected information assets based on roles, responsibilities, or the system design and changes, giving consideration to the concepts of least privilege and segregation of duties",
        95,
        "AC-2 (Account Management), AC-3 (Access Enforcement), AC-5 (Separation of Duties), AC-6 (Least Privilege), PS-4 (Termination), and PS-5 (Transfer) directly address access lifecycle management with least privilege and SoD.",
        "Minimal gap. SP 800-53 comprehensively covers access authorization, modification, and removal with least privilege and separation of duties."
    ),
    (
        "CC6.3-POF1",
        "CC6.3 POF1: Creates or modifies access — Processes are in place to create or modify access to protected assets",
        95,
        "AC-2 covers account creation, modification, and lifecycle management. AC-6 enforces least privilege in access grants.",
        "Minimal gap."
    ),
    (
        "CC6.4",
        "The entity restricts physical access to facilities and protected information assets to authorized personnel to meet the entity's objectives",
        90,
        "PE-2 (Physical Access Authorizations), PE-3 (Physical Access Control), PE-6 (Monitoring Physical Access), and PE-8 (Access Records) provide comprehensive physical access control.",
        "Excellent coverage. PE family directly addresses physical access restriction. Minor gap: SOC 2 frames in entity objective context."
    ),
    (
        "CC6.5",
        "The entity discontinues logical and physical access to protected information assets when that access is no longer required",
        90,
        "PS-4 (Personnel Termination), PS-5 (Personnel Transfer), AC-2 (Account Management including disable/remove), and PE-2 (Physical Access Revocation) address access discontinuation.",
        "Excellent coverage. Access revocation on termination and transfer well-addressed across logical and physical access."
    ),
    (
        "CC6.6",
        "The entity implements logical access security measures to protect against threats from sources outside its system boundaries",
        90,
        "SC-7 (Boundary Protection), AC-4 (Information Flow Enforcement), SI-3 (Malicious Code Protection), SI-4 (System Monitoring), SC-8 (Transmission Integrity), and AC-17 (Remote Access) provide defense against external threats.",
        "Excellent coverage. SP 800-53 boundary protection and external threat mitigation are comprehensive."
    ),
    (
        "CC6.6-POF1",
        "CC6.6 POF1: Restricts access — The entity restricts access through network security and entry points",
        90,
        "SC-7 provides boundary protection; AC-17 manages remote access; SC-8 protects transmissions.",
        "Minimal gap. Network access restriction from external sources well-covered."
    ),
    (
        "CC6.6-POF2",
        "CC6.6 POF2: Protects identification and authentication credentials — Identification and authentication credentials are protected during transmission outside system boundaries",
        90,
        "SC-8 (Transmission Integrity), SC-13 (Cryptographic Protection), and IA-5 (Authenticator Management) protect credentials in transit.",
        "Strong coverage for credential protection during external transmission."
    ),
    (
        "CC6.6-POF3",
        "CC6.6 POF3: Requires additional authentication or credentials — Additional authentication measures are required for access from outside system boundaries",
        85,
        "AC-17 (Remote Access) and IA-2 (Multi-factor Authentication for remote) address additional authentication for external access.",
        "Good coverage. IA-2 enhancements address multi-factor for remote access. Minor gap in adaptive authentication requirements."
    ),
    (
        "CC6.7",
        "The entity restricts the transmission, movement, and removal of information to authorized internal and external users and processes, and protects it during transmission, movement, or removal to meet the entity's objectives",
        85,
        "AC-4 (Information Flow Enforcement), MP-5 (Media Transport), SC-7 (Boundary Protection), SC-8 (Transmission Integrity), SC-28 (Protection at Rest), and PE-16 (Delivery and Removal) cover information movement controls.",
        "Strong coverage for data-in-motion and media transport protection. Minor gap in comprehensive data loss prevention as an integrated concept."
    ),
    (
        "CC6.7-POF1",
        "CC6.7 POF1: Restricts the ability to perform transmission — Data loss prevention processes are in place to detect and prevent unauthorized transmission",
        75,
        "AC-4 (Information Flow), SC-7 (Boundary Protection), SI-4 (Monitoring), and PE-19 (Information Leakage) partially address DLP.",
        "SP 800-53 provides building blocks for DLP but no single integrated DLP control. Gaps in comprehensive DLP program requirements covering all transmission vectors."
    ),
    (
        "CC6.8",
        "The entity implements controls to prevent or detect and act upon the introduction of unauthorized or malicious software to meet the entity's objectives",
        90,
        "SI-3 (Malicious Code Protection), SI-7 (Software Integrity), CM-7 (Least Functionality), CM-11 (User-Installed Software), and SI-4 (Monitoring) comprehensively address malware prevention and detection.",
        "Excellent coverage. SI-3 directly addresses malicious code protection. SI-7 adds integrity verification. CM controls prevent unauthorized software installation."
    ),

    # =========================================================================
    # CC7: System Operations
    # =========================================================================
    (
        "CC7.1",
        "To meet its objectives, the entity uses detection and monitoring procedures to identify changes to configurations that result in the introduction of new vulnerabilities, and susceptibilities to newly discovered vulnerabilities",
        90,
        "CM-3/CM-4 (Change Control/Monitoring), RA-5 (Vulnerability Scanning), SI-4 (System Monitoring), SI-5 (Security Alerts), and CA-7 (Continuous Monitoring) provide comprehensive detection and monitoring.",
        "Excellent coverage. SP 800-53 vulnerability and configuration monitoring is comprehensive."
    ),
    (
        "CC7.1-POF1",
        "CC7.1 POF1: Uses defined configuration standards — The entity uses defined configuration standards to assess newly deployed or changed IT assets",
        90,
        "CM-2 (Baseline Configuration), CM-6 (Configuration Settings), and CM-3 (Change Control) directly address configuration standards.",
        "Minimal gap. Configuration baseline and standard management well-covered."
    ),
    (
        "CC7.2",
        "The entity monitors system components and the operation of those components for anomalies that are indicative of malicious acts, natural disasters, and errors affecting the entity's ability to meet its objectives; anomalies are analyzed to determine whether they represent security events",
        90,
        "SI-4 (System Monitoring), AU-6 (Audit Review), IR-4 (Incident Handling), IR-5 (Incident Monitoring), and CA-7 (Continuous Monitoring) provide comprehensive anomaly detection and analysis.",
        "Excellent coverage. SP 800-53 monitoring, detection, and analysis capabilities are comprehensive."
    ),
    (
        "CC7.2-POF1",
        "CC7.2 POF1: Implements detection policies, procedures, and tools — The entity implements and maintains detection policies, procedures, and tools",
        90,
        "SI-4 (Monitoring), AU-2 (Auditable Events), AU-6 (Audit Review), and IR-1 (IR Policy) cover detection policies, procedures, and tools.",
        "Minimal gap. Detection capability well-addressed."
    ),
    (
        "CC7.2-POF2",
        "CC7.2 POF2: Designs detection measures — Detection measures are designed to identify anomalies including known and unknown threats",
        85,
        "SI-4 monitors for anomalies; PM-16 (Threat Awareness) covers threat intelligence; RA-5 identifies vulnerabilities.",
        "Good coverage for known threats. Minor gap in explicit requirements for detecting unknown/zero-day threats and behavioral analytics."
    ),
    (
        "CC7.3",
        "The entity evaluates security events to determine whether they could or have resulted in a failure of the entity to meet its objectives (security incidents) and, if so, takes actions to prevent or address such failures",
        90,
        "IR-4 (Incident Handling), IR-5 (Incident Monitoring), IR-6 (Incident Reporting), and AU-6 (Audit Review/Analysis) provide comprehensive event evaluation and incident determination.",
        "Excellent coverage. IR family directly addresses event evaluation, incident determination, and corrective action."
    ),
    (
        "CC7.3-POF1",
        "CC7.3 POF1: Responds to security incidents — Procedures are in place to respond to security incidents",
        90,
        "IR-1 (Policy), IR-4 (Handling), IR-8 (Response Plan) directly cover incident response procedures.",
        "Minimal gap."
    ),
    (
        "CC7.4",
        "The entity responds to identified security incidents by executing a defined incident response program to understand, contain, remediate, and communicate security incidents, as appropriate",
        90,
        "IR-1 (Policy), IR-2 (Training), IR-3 (Testing), IR-4 (Handling), IR-6 (Reporting), IR-7 (Assistance), and IR-8 (Response Plan) provide a complete incident response program.",
        "Excellent coverage. SP 800-53 IR family is comprehensive for incident response programs."
    ),
    (
        "CC7.4-POF1",
        "CC7.4 POF1: Assigns roles and responsibilities — Roles and responsibilities for responding to incidents are assigned",
        90,
        "IR-1 and IR-8 define incident response roles; PM-2 assigns security roles.",
        "Minimal gap."
    ),
    (
        "CC7.4-POF2",
        "CC7.4 POF2: Contains security incidents — Processes are in place to contain security incidents",
        90,
        "IR-4 (Incident Handling) directly addresses containment activities.",
        "Minimal gap."
    ),
    (
        "CC7.4-POF3",
        "CC7.4 POF3: Mitigates ongoing security incidents — Procedures are in place to mitigate the effects of ongoing incidents",
        85,
        "IR-4 covers mitigation; SI-2 (Flaw Remediation) supports remediation activities.",
        "Good coverage. Minor gap in explicit ongoing mitigation versus containment distinction."
    ),
    (
        "CC7.4-POF4",
        "CC7.4 POF4: Ends threats posed by security incidents — Steps are taken to end the threats posed by security incidents",
        85,
        "IR-4 (Incident Handling) includes eradication; CP-10 (Recovery) addresses reconstitution.",
        "Good coverage. Minor gap in explicit threat elimination verification requirements."
    ),
    (
        "CC7.4-POF5",
        "CC7.4 POF5: Restores operations — Procedures are in place to restore normal operations",
        85,
        "CP-10 (Recovery and Reconstitution), CP-2 (Contingency Plan), and IR-4 include recovery activities.",
        "Good coverage. CP family addresses recovery. Minor gap in linking incident recovery to business objectives explicitly."
    ),
    (
        "CC7.4-POF6",
        "CC7.4 POF6: Develops and implements communication protocols for security incidents",
        80,
        "IR-6 (Incident Reporting), IR-7 (Incident Response Assistance), and IR-8 (Response Plan) include communication elements.",
        "Good coverage for internal security communication. Minor gap in structured external communication protocols for incidents affecting customers and stakeholders."
    ),
    (
        "CC7.4-POF10",
        "CC7.4 POF10: Meets regulatory notification requirements — The entity meets notification requirements for security incidents",
        75,
        "IR-6 (Incident Reporting) addresses reporting to authorities.",
        "IR-6 covers reporting to designated authorities. Gaps in comprehensive regulatory notification tracking, multi-jurisdiction notification requirements, and notification timeline management."
    ),
    (
        "CC7.4-POF11",
        "CC7.4 POF11: Obtains understanding of nature of incident — The entity obtains understanding of the incident nature and scope",
        85,
        "IR-4 (Incident Handling) includes analysis and scoping; AU-6 (Audit Review) supports forensic analysis.",
        "Good coverage. Incident analysis and scoping well-addressed."
    ),
    (
        "CC7.4-POF12",
        "CC7.4 POF12: Remediates identified vulnerabilities — The entity remediates identified vulnerabilities following incidents",
        85,
        "SI-2 (Flaw Remediation), CA-5 (POA&M), and IR-3 (Lessons Learned) address post-incident vulnerability remediation.",
        "Good coverage. Remediation well-addressed through SI-2 and CA-5. Minor gap in formal post-incident remediation verification."
    ),
    (
        "CC7.4-POF13",
        "CC7.4 POF13: Evaluates the effectiveness of incident response — The entity evaluates incident response effectiveness",
        80,
        "IR-3 (Incident Response Testing) includes lessons learned and effectiveness evaluation. CA-2 provides broader assessment.",
        "Good coverage. IR-3 directly addresses response effectiveness evaluation. Minor gap in formal metrics-based incident response program improvement."
    ),
    (
        "CC7.5",
        "The entity identifies, develops, and implements activities to recover from identified security incidents",
        85,
        "CP-2 (Contingency Plan), CP-10 (Recovery and Reconstitution), IR-4 (Incident Handling), and IR-3 (Lessons Learned) address incident recovery.",
        "Good coverage. CP family provides recovery framework; IR family covers incident-specific recovery. Minor gap in explicit post-incident business recovery planning."
    ),

    # =========================================================================
    # CC8: Change Management
    # =========================================================================
    (
        "CC8.1",
        "The entity authorizes, designs, develops or acquires, configures, documents, tests, approves, and implements changes to infrastructure, data, software, and procedures required to meet its objectives",
        85,
        "CM-3 (Configuration Change Control), CM-4 (Impact Analysis), CM-5 (Access Restrictions for Change), SA-10 (Developer Configuration Management), SA-11 (Developer Testing), and SA-4 (Acquisitions) comprehensively cover change management.",
        "Strong coverage. SP 800-53 CM and SA families provide comprehensive change management. Minor gap: SOC 2 includes changes to procedures and data explicitly; SP 800-53 focuses primarily on IT configuration changes."
    ),
    (
        "CC8.1-POF1",
        "CC8.1 POF1: Manages changes throughout the system life cycle — Processes are in place to manage changes to system components through the life cycle",
        85,
        "SA-3 (System Development Life Cycle), CM-3 (Change Control), and SA-10 (Developer Configuration Management) cover lifecycle change management.",
        "Good coverage. Minor gap in managing changes to business processes and procedures beyond IT systems."
    ),

    # =========================================================================
    # CC9: Risk Mitigation
    # =========================================================================
    (
        "CC9.1",
        "The entity identifies, selects, and develops risk mitigation activities for risks arising from potential business disruptions",
        75,
        "CP-1/CP-2/CP-4 (Contingency Policy/Plan/Testing), RA-3 (Risk Assessment), and PM-9 (Risk Management Strategy) address risk mitigation for disruptions.",
        "Good coverage for IT disruption risk mitigation. SOC 2 CC9.1 extends to all business disruptions including non-IT disruptions, supply chain disruptions, and market disruptions."
    ),
    (
        "CC9.1-POF1",
        "CC9.1 POF1: Considers mitigation through business continuity — The entity considers mitigation through contingency planning",
        80,
        "CP family (CP-1 through CP-10) provides comprehensive contingency planning and business continuity for IT systems.",
        "Strong coverage for IT continuity. Minor gap in non-IT business continuity and crisis management beyond IT."
    ),
    (
        "CC9.2",
        "The entity assesses and manages risks associated with vendors and business partners",
        80,
        "SA-4 (Acquisitions), SA-9 (External System Services), SR-1/SR-2/SR-3 (Supply Chain Risk Management), SR-5 (Acquisition Strategies), and SR-6 (Supplier Assessments) provide vendor risk management.",
        "Good coverage for technology vendor risk management. SOC 2 CC9.2 extends to all vendors and business partners, not just IT suppliers. Gaps in non-technology vendor risk assessment."
    ),
    (
        "CC9.2-POF1",
        "CC9.2 POF1: Creates policies for vendor and business partner risk management — Vendor risk management processes are established",
        80,
        "SR-1 (Supply Chain Policy) and SA-4 (Acquisition Requirements) establish vendor management policies.",
        "Good coverage for IT vendor policies. Minor gap in non-technology vendor and business partner risk policies."
    ),
    (
        "CC9.2-POF13",
        "CC9.2 POF13: Assesses vendor and business partner risks — The entity periodically assesses vendor and business partner risks",
        75,
        "SR-6 (Supplier Assessments and Reviews) directly addresses periodic vendor assessment.",
        "Good coverage. SR-6 covers supplier assessment. Gaps in business partner (non-supplier) risk assessment and comprehensive vendor risk scoring."
    ),

    # =========================================================================
    # A1: Availability
    # =========================================================================
    (
        "A1.1",
        "The entity maintains, monitors, and evaluates current processing capacity and use of system components (infrastructure, data, and software) to manage capacity demand and to enable the implementation of additional capacity to help meet its objectives",
        65,
        "AU-4 (Audit Storage Capacity), SC-5 (Denial of Service Protection), CP-2 (Contingency Plan), and CA-7 (Continuous Monitoring) partially address capacity management.",
        "SP 800-53 addresses capacity in specific contexts (audit storage, DoS protection) but lacks a comprehensive capacity management control. SOC 2 A1.1 requires proactive capacity planning across all system components."
    ),
    (
        "A1.1-POF1",
        "A1.1 POF1: Manages capacity to meet objectives — Processing capacity and use of system components are managed",
        60,
        "AU-4 manages audit storage capacity; SC-5 protects against capacity exhaustion through DoS.",
        "SP 800-53 addresses specific capacity scenarios. Gaps in comprehensive capacity planning, trending, threshold alerting, and proactive capacity management across all infrastructure components."
    ),
    (
        "A1.2",
        "The entity authorizes, designs, develops or acquires, implements, operates, approves, maintains, and monitors environmental protections, software, data backup processes, and recovery infrastructure to meet its objectives",
        85,
        "PE family (environmental protections), CP-9 (Backup), CP-6/CP-7/CP-8 (Alternate Sites/Telecommunications), and CP-10 (Recovery) provide comprehensive availability infrastructure.",
        "Strong coverage. SP 800-53 environmental and recovery controls are comprehensive."
    ),
    (
        "A1.2-POF1",
        "A1.2 POF1: Implements recovery infrastructure and software — Recovery infrastructure is implemented and maintained",
        85,
        "CP-6 (Alternate Storage), CP-7 (Alternate Processing), CP-9 (Backup), and CP-10 (Recovery) provide recovery infrastructure.",
        "Minimal gap. Recovery infrastructure well-addressed."
    ),
    (
        "A1.2-POF2",
        "A1.2 POF2: Implements environmental protections — Environmental protections for data centers and facilities are implemented",
        90,
        "PE-9 through PE-15 (Power, Emergency Shutoff, Emergency Power, Emergency Lighting, Fire, Temperature/Humidity, Water Damage) provide comprehensive environmental protections.",
        "Excellent coverage. PE family is comprehensive for environmental protections."
    ),
    (
        "A1.2-POF3",
        "A1.2 POF3: Implements data backup processes — Data backup and recovery processes are implemented and maintained",
        90,
        "CP-9 (Information System Backup) directly addresses data backup processes including scheduling, testing, and offsite storage.",
        "Minimal gap. CP-9 comprehensively covers data backup."
    ),
    (
        "A1.3",
        "The entity tests recovery plan procedures supporting system recovery to meet its objectives",
        90,
        "CP-4 (Contingency Plan Testing), CP-3 (Contingency Training), and IR-3 (Incident Response Testing) directly address recovery plan testing.",
        "Excellent coverage. CP-4 directly requires recovery plan testing. Well-aligned with SOC 2 testing requirements."
    ),

    # =========================================================================
    # C1: Confidentiality
    # =========================================================================
    (
        "C1.1",
        "The entity identifies and maintains confidential information to meet the entity's objectives related to confidentiality",
        80,
        "RA-2 (Security Categorization), AC-4 (Information Flow Enforcement), MP-3 (Media Labeling), and SC-28 (Protection at Rest) address confidential information identification and protection.",
        "Good coverage for information classification and protection. Minor gap: SOC 2 C1.1 requires identifying confidential information based on business commitments; SP 800-53 uses FIPS 199 categorization methodology."
    ),
    (
        "C1.1-POF1",
        "C1.1 POF1: Identifies confidential information — The entity has procedures to identify confidential information",
        75,
        "RA-2 covers security categorization; MP-3 covers media labeling.",
        "Good coverage through categorization. Minor gap in business-context confidentiality classification beyond security categorization."
    ),
    (
        "C1.2",
        "The entity disposes of confidential information to meet the entity's objectives related to confidentiality",
        85,
        "MP-6 (Media Sanitization), SI-12 (Information Management and Retention), and SR-12 (Component Disposal) address secure disposal of confidential information.",
        "Strong coverage. MP-6 provides comprehensive media sanitization. SI-12 covers retention and disposal policies."
    ),

    # =========================================================================
    # PI1: Processing Integrity
    # =========================================================================
    (
        "PI1.1",
        "The entity obtains or generates, uses, and communicates relevant, quality information regarding the objectives related to processing, including definitions of data processed and product and service specifications, to support the use of products and services",
        50,
        "SA-5 (System Documentation), SI-10 (Information Input Validation), and SI-12 (Information Handling) partially address processing information quality.",
        "SOC 2 PI1.1 focuses on processing integrity including data definitions, specifications, and quality information for products/services. SP 800-53 addresses data validation and system documentation but not business-level processing specifications."
    ),
    (
        "PI1.2",
        "The entity implements policies and procedures over system inputs, including controls over completeness and accuracy, to result in products, services, and reporting to meet the entity's objectives",
        60,
        "SI-9 (Information Input Restrictions), SI-10 (Information Accuracy/Completeness/Validity), and AU-10 (Non-Repudiation) address input controls.",
        "SP 800-53 provides input validation and accuracy controls. Gaps in comprehensive input completeness verification, business-rule validation, and end-to-end processing integrity assurance."
    ),
    (
        "PI1.3",
        "The entity implements policies and procedures over system processing to result in products, services, and reporting to meet the entity's objectives",
        55,
        "SI-7 (Software and Information Integrity), SI-10 (Information Accuracy), and AU-2/AU-3 (Auditable Events/Content) address processing controls.",
        "SP 800-53 provides integrity verification and audit capabilities. Gaps in business process validation, transaction processing integrity, and output reconciliation requirements."
    ),
    (
        "PI1.4",
        "The entity implements policies and procedures to make available or deliver output completely, accurately, and timely in accordance with specifications to meet the entity's objectives",
        50,
        "SI-12 (Information Output Handling), AU-3 (Content of Audit Records), and PE-5 (Access Control for Output Devices) partially address output controls.",
        "SP 800-53 addresses output handling and audit trails. Gaps in output completeness verification, accuracy validation, timeliness requirements, and delivery confirmation."
    ),
    (
        "PI1.5",
        "The entity implements policies and procedures to store inputs, items in processing, and outputs completely, accurately, and timely in accordance with system specifications to meet the entity's objectives",
        55,
        "SC-28 (Protection at Rest), MP-4 (Media Storage), CP-9 (Backup), and SI-12 (Information Handling) address storage of processing data.",
        "SP 800-53 covers data storage protection and backup. Gaps in storage integrity verification for processing items, temporal accuracy of stored data, and specification-based storage validation."
    ),

    # =========================================================================
    # P1: Privacy
    # =========================================================================
    (
        "P1.0",
        "Privacy Criteria Introduction — The entity's privacy practices meet its objectives",
        45,
        "PT family (PT-1 through PT-8) added in Rev 5 provides privacy controls. PM-25/PM-26/PM-27 address privacy program management.",
        "SP 800-53 Rev 5 significantly improved privacy coverage with the PT family. However, SOC 2 privacy criteria are based on Generally Accepted Privacy Principles (GAPP) which are broader than federal privacy requirements addressed by SP 800-53."
    ),
    (
        "P1.1",
        "The entity provides notice to data subjects about its privacy practices to meet the entity's objectives related to privacy",
        55,
        "PT-5 (Privacy Notice) directly addresses privacy notice requirements. PT-3 (Processing Purposes) requires purpose specification.",
        "PT-5 covers privacy notice. Gaps in comprehensive notice requirements including notice timing (at or before collection), notice content specifics (data types, purposes, third-party sharing, rights), and notice accessibility across all channels."
    ),
    (
        "P1.1-POF1",
        "P1.1 POF1: Communicates to data subjects — Privacy notices are provided to data subjects",
        55,
        "PT-5 (Privacy Notice) addresses notice provision.",
        "PT-5 covers privacy notice delivery. Gaps in specific notice content requirements, multi-language support, and channel-specific notice formats."
    ),
    (
        "P1.1-POF5",
        "P1.1 POF5: Provides notice of changes — Data subjects are notified of changes to the entity's privacy practices",
        40,
        "PT-5 may require notice updates. No specific control for change notification to data subjects.",
        "SP 800-53 does not explicitly require notification to data subjects when privacy practices change. Gap in change notification timing, method, and opt-out requirements."
    ),
    (
        "P1.2",
        "The entity communicates choices available regarding the collection, use, retention, disclosure, and disposal of personal information to data subjects and obtains consent",
        40,
        "PT-4 (Consent) addresses consent requirements. PT-2 (Authority to Process) covers legal basis.",
        "PT-4 covers consent. Gaps in comprehensive choice mechanisms (opt-in, opt-out, granular consent), choice presentation at point of collection, and ongoing consent management including withdrawal."
    ),
    (
        "P1.3",
        "The entity collects personal information only for the purposes identified in the notice to the data subject",
        50,
        "PT-3 (Processing Purposes) requires purpose specification. PT-2 (Authority to Process) limits processing to authorized purposes.",
        "SP 800-53 addresses purpose limitation. Gaps in purpose enforcement at collection point, preventing scope creep in data collection, and linking collection practices directly to notice content."
    ),
    (
        "P1.4",
        "The entity limits the use of personal information to the purposes identified in the notice and for which the data subject has provided explicit consent",
        50,
        "PT-3 (Processing Purposes) and PT-2 (Authority to Process) address use limitation.",
        "SP 800-53 covers purpose limitation conceptually. Gaps in enforcement mechanisms for use limitation, secondary use prevention, and audit of actual data use against stated purposes."
    ),
    (
        "P1.5",
        "The entity retains personal information consistent with the entity's objectives related to privacy",
        55,
        "SI-12 (Information Handling and Retention) and PT-3 (Processing Purposes) address retention. MP-6 (Media Sanitization) supports disposal.",
        "SP 800-53 covers retention and disposal. Gaps in retention schedule alignment with privacy notice, automated retention enforcement, and retention minimization based on purpose completion."
    ),
    (
        "P1.6",
        "The entity disposes of personal information to meet the entity's privacy objectives",
        65,
        "MP-6 (Media Sanitization), SI-12 (Information Handling), and SR-12 (Component Disposal) address secure disposal.",
        "Good technical disposal coverage. Minor gaps in privacy-specific disposal triggers (purpose completion, consent withdrawal), comprehensive disposal verification across all copies, and third-party disposal enforcement."
    ),
    (
        "P1.7",
        "The entity discloses personal information to third parties with the consent of the data subject or as authorized under applicable law or regulation",
        40,
        "PT-4 (Consent) and SA-9 (External System Services) partially address third-party disclosure.",
        "SP 800-53 covers consent and external service agreements. Gaps in third-party disclosure tracking, consent verification before sharing, third-party use limitation agreements, and cross-border transfer requirements."
    ),
    (
        "P1.8",
        "The entity provides data subjects with access to their personal information for review and correction",
        30,
        "PT-6 (System of Records Notice) addresses individual access in the federal context (Privacy Act).",
        "PT-6 is specific to federal Privacy Act requirements. Gaps in general data subject access rights, correction mechanisms, access request processing, identity verification for access requests, and response time requirements."
    ),
    (
        "P1.9",
        "The entity provides data subjects the ability to update and correct personal information",
        25,
        "PT-6 addresses correction in federal Privacy Act context.",
        "Significant gap for commercial context. SP 800-53 PT-6 is Privacy Act-specific. No general control for data correction mechanisms, correction verification, propagation of corrections to third parties, or correction request management."
    ),
]


def normalize_control_id(raw_id: str) -> str:
    """Convert control IDs like 'AC-01' to 'AC-1' (drop leading zeros in number part)."""
    parts = raw_id.split("-", 1)
    if len(parts) == 2:
        family = parts[0]
        try:
            number = str(int(parts[1]))
            return f"{family}-{number}"
        except ValueError:
            return raw_id
    return raw_id


def natural_sort_key(clause_id: str):
    """
    Generate a sort key for natural ordering.
    E.g. CC1.1 < CC1.2 < CC2.1 < CC10.1; POF1 < POF2 < POF10
    """
    # Split on category prefix and number parts
    parts = []
    current = ""
    for char in clause_id:
        if char.isdigit():
            if current and not current[-1].isdigit():
                parts.append(current)
                current = ""
            current += char
        else:
            if current and current[-1].isdigit():
                parts.append(int(current))
                current = ""
            current += char
    if current:
        if current.isdigit():
            parts.append(int(current))
        else:
            parts.append(current)
    return parts


def build_reverse_mappings(controls_dir: Path, manifest_path: Path):
    """
    Read all control files and build a mapping from SOC 2 TSC clause ID
    to a set of SP 800-53 control IDs (normalized, e.g. 'AC-1').
    """
    with open(manifest_path) as f:
        manifest = json.load(f)

    reverse_map = defaultdict(set)
    for ctrl_entry in manifest["controls"]:
        ctrl_file = controls_dir / ctrl_entry["file"]
        with open(ctrl_file) as f:
            ctrl_data = json.load(f)

        control_id = normalize_control_id(ctrl_data["id"])
        soc2_refs = ctrl_data.get("compliance_mappings", {}).get("soc2_tsc", [])
        for ref in soc2_refs:
            reverse_map[ref].add(control_id)

    return reverse_map


def generate_coverage():
    """Generate the SOC 2 TSC coverage analysis JSON."""

    # Build reverse mappings from control data
    reverse_map = build_reverse_mappings(CONTROLS_DIR, MANIFEST_PATH)

    # Build clauses list from expert definitions, enriched with actual control mappings
    clauses = []
    for clause_id, title, coverage_pct, rationale, gaps in SOC2_TSC_CLAUSES:
        # Get controls from reverse mapping (data-driven)
        data_controls = sorted(reverse_map.get(clause_id, set()), key=natural_sort_key)

        clauses.append({
            "id": clause_id,
            "title": title,
            "controls": data_controls,
            "coverage_pct": coverage_pct,
            "rationale": rationale,
            "gaps": gaps,
        })

    # Sort clauses by natural order
    clauses.sort(key=lambda c: natural_sort_key(c["id"]))

    # Calculate summary statistics
    total = len(clauses)
    pcts = [c["coverage_pct"] for c in clauses]
    avg = round(sum(pcts) / total, 1) if total > 0 else 0

    full_count = sum(1 for p in pcts if 85 <= p <= 100)
    substantial_count = sum(1 for p in pcts if 65 <= p <= 84)
    partial_count = sum(1 for p in pcts if 40 <= p <= 64)
    weak_count = sum(1 for p in pcts if 1 <= p <= 39)
    none_count = sum(1 for p in pcts if p == 0)

    output = {
        "$schema": "../schema/framework-coverage.schema.json",
        "framework_id": "soc2_tsc",
        "framework_name": "SOC 2 Trust Services Criteria (TSC) 2017",
        "metadata": {
            "source": "SP800-53v5_Control_Mappings",
            "version": "1.0",
            "disclaimer": "Based on publicly available crosswalks and expert analysis. Validate with qualified assessors for compliance/audit use."
        },
        "weight_scale": {
            "full": {
                "min": 85,
                "max": 100,
                "label": "Fully addressed"
            },
            "substantial": {
                "min": 65,
                "max": 84,
                "label": "Well addressed, notable gaps"
            },
            "partial": {
                "min": 40,
                "max": 64,
                "label": "Partially addressed"
            },
            "weak": {
                "min": 1,
                "max": 39,
                "label": "Weakly addressed"
            },
            "none": {
                "min": 0,
                "max": 0,
                "label": "No mapping"
            }
        },
        "clauses": clauses,
        "summary": {
            "total_clauses": total,
            "average_coverage": avg,
            "full_count": full_count,
            "substantial_count": substantial_count,
            "partial_count": partial_count,
            "weak_count": weak_count,
            "none_count": none_count,
        }
    }

    return output


def main():
    """Main entry point."""
    # Verify paths
    if not MANIFEST_PATH.exists():
        print(f"ERROR: Manifest not found at {MANIFEST_PATH}", file=sys.stderr)
        sys.exit(1)
    if not CONTROLS_DIR.exists():
        print(f"ERROR: Controls directory not found at {CONTROLS_DIR}", file=sys.stderr)
        sys.exit(1)

    # Ensure output directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Generate coverage data
    coverage = generate_coverage()

    # Write output
    with open(OUTPUT_PATH, "w") as f:
        json.dump(coverage, f, indent=2)
        f.write("\n")

    # Print summary
    summary = coverage["summary"]
    print(f"SOC 2 TSC Coverage Analysis generated successfully")
    print(f"  Output: {OUTPUT_PATH}")
    print(f"  Total clauses: {summary['total_clauses']}")
    print(f"  Average coverage: {summary['average_coverage']}%")
    print(f"  Full (85-100%): {summary['full_count']}")
    print(f"  Substantial (65-84%): {summary['substantial_count']}")
    print(f"  Partial (40-64%): {summary['partial_count']}")
    print(f"  Weak (1-39%): {summary['weak_count']}")
    print(f"  None (0%): {summary['none_count']}")

    # Validate JSON is loadable
    with open(OUTPUT_PATH) as f:
        loaded = json.load(f)
    print(f"\n  Validation: JSON loads successfully, {len(loaded['clauses'])} clauses verified")


if __name__ == "__main__":
    main()
