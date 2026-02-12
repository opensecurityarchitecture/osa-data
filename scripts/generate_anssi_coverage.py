#!/usr/bin/env python3
"""Generate ANSSI framework coverage analysis JSON.

Reads all SP 800-53 control files from the controls directory, builds reverse
mappings for ANSSI Hygiene Guide, SecNumCloud, and RGS clauses, then produces
a coverage analysis JSON file at data/framework-coverage/anssi.json.

Usage:
    python3 scripts/generate_anssi_coverage.py
"""

import json
import os
import sys
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
CONTROLS_DIR = os.path.join(DATA_DIR, 'controls')
COVERAGE_DIR = os.path.join(DATA_DIR, 'framework-coverage')
OUTPUT_FILE = os.path.join(COVERAGE_DIR, 'anssi.json')

# ─── ANSSI clause metadata ──────────────────────────────────────────────────
# Each entry: (clause_id, title, coverage_pct, rationale, gaps)
# These are expert-assessed based on the nature of each ANSSI requirement
# and how well SP 800-53 Rev 5 addresses the underlying security objective.

HYGIENE_CLAUSES = [
    (
        "Hygiene.1",
        "Sensitise and train",
        90,
        "AT-01 awareness policy; AT-02 security awareness; AT-05 contacts with security groups. SP 800-53 AT family comprehensively covers awareness and training.",
        "Minimal gap. ANSSI Hygiene Guide measure is practical and well-matched by SP 800-53 awareness controls."
    ),
    (
        "Hygiene.2",
        "Define and apply a security policy",
        90,
        "AC-01 access control policy; AU-01 audit policy; CA-01 assessment policy; CM-01 configuration management policy; CP-01 contingency planning policy; IA-01 identification and authentication policy; IR-01 incident response policy; MA-01 maintenance policy; MP-01 media protection policy; PE-01 physical protection policy; PL-01 security planning policy; PS-01 personnel security policy; PT-01 PII processing policy; RA-01 risk assessment policy; SA-01 acquisition policy; SC-01 system and communications protection policy; SI-01 system integrity policy; SR-01 supply chain policy. Broad policy family coverage.",
        "Minimal gap. SP 800-53 requires comprehensive security policies across all control families."
    ),
    (
        "Hygiene.3",
        "Carry out regular audits",
        85,
        "AT-02 security awareness; AT-04 training records; AC-08 system use notification; PL-04 rules of behavior. These controls support accountability and user responsibility.",
        "Minor: ANSSI emphasizes regular independent audits as a hygiene measure. SP 800-53 CA-02 and CA-07 cover assessment and continuous monitoring but the practical audit cadence focus is less explicit."
    ),
    (
        "Hygiene.4",
        "Identify the person responsible for information systems security",
        90,
        "AT-03 security training; AT-04 training records; AT-05 contacts; CP-03 contingency training; IR-02 incident response training. SP 800-53 training and role assignment controls comprehensively address responsibility designation.",
        "Minimal gap. SP 800-53 PM-02 designates senior information security officer role."
    ),
    (
        "Hygiene.5",
        "Establish an inventory of IT assets",
        90,
        "CM-01 configuration management policy; CM-02 baseline configuration; CM-08 system component inventory; IA-03 device identification; PL-02 system security plan; SA-05 system documentation. CM-08 directly addresses asset inventory.",
        "Minimal gap. CM-08 maps directly to asset inventory requirements."
    ),
    (
        "Hygiene.6",
        "Establish access control procedures",
        90,
        "AC-02 account management; AC-13 supervision and review; IA-04 identifier management. SP 800-53 AC and IA families comprehensively address access control procedures.",
        "Minimal gap."
    ),
    (
        "Hygiene.7",
        "Manage arrivals, departures and movements of staff",
        90,
        "AC-02 account management; IA-04 identifier management; MA-05 maintenance personnel; PS-01 personnel security policy; PS-02 position categorization; PS-03 personnel screening; PS-04 personnel termination; PS-05 personnel transfer; PS-06 access agreements; PS-07 third-party personnel; PS-08 personnel sanctions. PS family comprehensively covers personnel lifecycle.",
        "Minimal gap."
    ),
    (
        "Hygiene.8",
        "Classify information to know how to protect it",
        85,
        "AC-15 automated marking; AC-16 automated labeling; CM-08 component inventory; MP-03 media labeling; PT-07 specific categories of PII; RA-02 security categorization; SI-12 information management. RA-02 and MP-03 address classification.",
        "Minor: ANSSI emphasizes a practical classification scheme for all information. SP 800-53 RA-02 uses FIPS 199 categorization which is US-specific; French classification levels (e.g., Diffusion Restreinte) not addressed."
    ),
    (
        "Hygiene.9",
        "Control access to external services",
        85,
        "AC-20 use of external systems; CA-03 system connections; SA-09 external information system services; SR-03 supply chain controls. SP 800-53 addresses external service controls.",
        "Minor: ANSSI specifically targets cloud and SaaS service access governance. SP 800-53 covers external systems but less prescriptive on modern cloud service access patterns."
    ),
    (
        "Hygiene.10",
        "Implement strong authentication",
        90,
        "AC-01 access control policy; AC-07 unsuccessful login attempts; IA-01 identification and authentication policy; IA-02 user identification and authentication; IA-05 authenticator management; IA-06 authenticator feedback. IA family provides comprehensive authentication controls.",
        "Minimal gap. SP 800-53 IA family directly addresses strong authentication requirements."
    ),
    (
        "Hygiene.11",
        "Distinguish user, admin, and service accounts",
        90,
        "AC-02 account management; AC-14 permitted actions without identification; IA-01 identification and authentication policy; IA-02 user identification; IA-04 identifier management. Account type differentiation well covered.",
        "Minimal gap."
    ),
    (
        "Hygiene.12",
        "Protect passwords and secret keys",
        90,
        "AC-07 unsuccessful login attempts; AC-10 concurrent session control; AC-12 session termination; IA-02 user identification; IA-05 authenticator management; IA-07 cryptographic module authentication; SC-10 network disconnect; SC-12 cryptographic key management; SC-13 use of cryptography; SC-17 PKI certificates; SC-23 session authenticity. Comprehensive coverage.",
        "Minimal gap."
    ),
    (
        "Hygiene.13",
        "Regularly review authorisations",
        85,
        "AC-02 account management. SP 800-53 AC-02 includes periodic review of accounts but ANSSI emphasizes a broader authorisation review process.",
        "Minor: ANSSI measure focuses on regular, systematic review of all authorisations. AC-02 covers account review but the broader entitlement review scope is less prescriptive."
    ),
    (
        "Hygiene.14",
        "Implement least privilege",
        90,
        "AC-01 access control policy; AC-03 access enforcement; AC-06 least privilege; CM-05 access restrictions for change; MP-02 media access; PS-05 personnel transfer; SI-09 information input restrictions. AC-06 directly maps to least privilege.",
        "Minimal gap."
    ),
    (
        "Hygiene.15",
        "Implement separation of duties",
        90,
        "AC-03 access enforcement; AC-05 separation of duties; AC-06 least privilege; CM-05 access restrictions for change; MA-05 maintenance personnel; PS-02 position categorization. AC-05 directly addresses separation of duties.",
        "Minimal gap."
    ),
    (
        "Hygiene.16",
        "Control access to administration functions",
        90,
        "AC-06 least privilege; CM-05 access restrictions for change; MA-04 remote maintenance. SP 800-53 addresses privileged access control.",
        "Minimal gap."
    ),
    (
        "Hygiene.17",
        "Segment networks to limit admin access",
        85,
        "AC-03 access enforcement; AC-05 separation of duties; AC-06 least privilege; CM-05 access restrictions for change. Network segmentation for admin access addressed through multiple controls.",
        "Minor: ANSSI emphasizes dedicated administration networks. SP 800-53 covers through AC-06 and SC-07 but dedicated admin network requirement is less explicit."
    ),
    (
        "Hygiene.18",
        "Keep software up to date",
        90,
        "AC-11 session lock; AC-19 mobile devices; CM-02 baseline configuration; CM-06 configuration settings; CM-07 least functionality; PE-17 alternate work site. Configuration management and patching well covered.",
        "Minimal gap. SI-02 flaw remediation directly addresses software updates."
    ),
    (
        "Hygiene.19",
        "Protect data stored on workstations",
        90,
        "AC-19 mobile devices; MP-01 media protection policy; MP-02 media access; MP-04 media storage; MP-05 media transport; MP-06 media sanitization; SC-04 information remnance; SC-13 use of cryptography; SI-12 information management; SR-12 component disposal. Comprehensive data protection coverage.",
        "Minimal gap."
    ),
    (
        "Hygiene.20",
        "Restrict software installation",
        90,
        "CM-06 configuration settings; CM-07 least functionality; MA-03 maintenance tools; SA-06 software usage restrictions; SA-07 user installed software; SC-18 mobile code; SI-07 software and information integrity. CM-07 and SA-07 directly address software restriction.",
        "Minimal gap."
    ),
    (
        "Hygiene.21",
        "Protect against malware",
        90,
        "SI-03 malicious code protection; SI-08 spam protection. SI-03 directly addresses malware protection.",
        "Minimal gap."
    ),
    (
        "Hygiene.22",
        "Secure email usage",
        85,
        "AC-20 use of external systems; SC-05 denial of service protection; SC-07 boundary protection; SC-14 public access protections; SC-15 collaborative computing; SC-18 mobile code; SI-08 spam protection. Email security addressed through multiple controls.",
        "Minor: ANSSI provides specific email security guidance. SP 800-53 covers email through general controls but email-specific measures (e.g., SPF, DKIM, DMARC requirements) less explicit."
    ),
    (
        "Hygiene.23",
        "Segment and filter network flows",
        90,
        "AC-04 information flow enforcement; SC-01 system and communications protection policy; SC-02 application partitioning; SC-03 security function isolation; SC-06 resource priority; SC-07 boundary protection; SC-08 transmission integrity; SC-20 secure name resolution; SC-21 secure name resolution (recursive); SC-22 architecture for name resolution; SA-08 security engineering principles. SC-07 directly addresses network segmentation and filtering.",
        "Minimal gap."
    ),
    (
        "Hygiene.24",
        "Implement secure remote access",
        90,
        "AC-17 remote access; MA-04 remote maintenance; SC-08 transmission integrity; SC-09 transmission confidentiality; SC-11 trusted path; SC-16 transmission of security parameters; SC-19 VoIP; SC-23 session authenticity. AC-17 directly addresses remote access security.",
        "Minimal gap."
    ),
    (
        "Hygiene.25",
        "Secure wireless networks",
        85,
        "AC-18 wireless access restrictions; SC-19 VoIP. AC-18 addresses wireless security.",
        "Minor: ANSSI provides detailed wireless security guidance including specific protocol requirements. SP 800-53 AC-18 covers wireless access but French-specific wireless standards less detailed."
    ),
    (
        "Hygiene.26",
        "Secure interconnections with partners",
        85,
        "AC-18 wireless access restrictions; IA-03 device identification; PE-04 access control for transmission medium. Partner interconnection security addressed.",
        "Minor: ANSSI emphasizes specific interconnection security requirements with partner organisations. SP 800-53 CA-03 and SA-09 cover interconnections but the partner-specific governance aspects less prescriptive."
    ),
    (
        "Hygiene.27",
        "Use firewalls to protect internal networks",
        90,
        "AC-04 information flow enforcement; SC-05 denial of service protection; SC-07 boundary protection. SC-07 directly addresses firewall and boundary protection.",
        "Minimal gap."
    ),
    (
        "Hygiene.28",
        "Protect administration of network equipment",
        85,
        "AC-17 remote access; MA-04 remote maintenance; SC-11 trusted path. Administration network protection addressed.",
        "Minor: ANSSI emphasizes dedicated out-of-band management networks. SP 800-53 covers through AC-17 and MA-04 but dedicated management network requirements less explicit."
    ),
    (
        "Hygiene.29",
        "Implement centralised log management",
        90,
        "AC-09 previous logon notification; AU-01 audit policy; AU-02 auditable events; AU-03 audit record content; AU-04 audit storage capacity; AU-05 response to audit failures; AU-06 audit review and reporting; AU-07 audit reduction; AU-08 timestamps; AU-09 protection of audit information; AU-10 non-repudiation; AU-11 audit record retention; CA-07 continuous monitoring; IR-05 incident monitoring; SI-04 system monitoring; SI-11 error handling. AU family comprehensively addresses logging.",
        "Minimal gap."
    ),
    (
        "Hygiene.30",
        "Implement regular data backups",
        90,
        "CP-01 contingency planning policy; CP-02 contingency plan; CP-06 alternate storage site; CP-07 alternate processing site; CP-08 telecommunications services; CP-09 system backup; CP-10 system recovery. CP-09 directly addresses backup requirements.",
        "Minimal gap."
    ),
    (
        "Hygiene.31",
        "Perform vulnerability management",
        90,
        "AC-13 supervision and review; CA-02 security assessments; CA-04 security certification; CA-07 continuous monitoring; RA-05 vulnerability scanning; SA-11 developer security testing; SI-06 security functionality verification; SR-06 supplier assessments; SR-10 inspection of systems. RA-05 directly addresses vulnerability management.",
        "Minimal gap."
    ),
    (
        "Hygiene.32",
        "Manage user account lifecycle",
        90,
        "AC-02 account management; IA-04 identifier management; PS-04 personnel termination; PS-05 personnel transfer. AC-02 directly addresses account lifecycle management.",
        "Minimal gap."
    ),
    (
        "Hygiene.33",
        "Apply security patches promptly",
        90,
        "RA-05 vulnerability scanning; SA-11 developer testing; SI-01 system integrity policy; SI-02 flaw remediation; SI-05 security alerts; SI-10 information accuracy. SI-02 directly addresses patch management.",
        "Minimal gap."
    ),
    (
        "Hygiene.34",
        "Manage changes carefully",
        90,
        "CM-03 configuration change control; CM-04 monitoring configuration changes; CM-05 access restrictions for change; MA-01 maintenance policy; MA-02 controlled maintenance; MA-03 maintenance tools; MA-04 remote maintenance; MA-06 timely maintenance; SA-03 lifecycle support; SA-10 developer configuration management; SI-01 system integrity policy; SI-02 flaw remediation; SI-07 software integrity. CM-03 directly addresses change management.",
        "Minimal gap."
    ),
    (
        "Hygiene.35",
        "Define and test an incident response plan",
        90,
        "CP-02 contingency plan; CP-03 contingency training; CP-04 contingency plan testing; CP-05 contingency plan update; CP-10 system recovery; IR-01 incident response policy; IR-02 incident response training; IR-03 incident response testing; IR-04 incident handling. IR family comprehensively addresses incident response.",
        "Minimal gap."
    ),
    (
        "Hygiene.36",
        "Establish a governance and risk framework",
        85,
        "CA-01 assessment policy; CA-05 plan of action; CA-06 security accreditation; CM-03 configuration change control; CP-05 contingency plan update; PL-01 security planning policy; PL-02 system security plan; PL-03 security plan update; PL-06 security-related activity planning; RA-04 risk assessment update; SA-01 acquisition policy; SA-02 allocation of resources; SA-03 lifecycle support; SA-08 security engineering principles; SA-10 developer configuration management; SR-01 supply chain policy; SR-02 supply chain risk management plan. Broad governance coverage.",
        "Minor: ANSSI governance framework expectations include French regulatory integration. SP 800-53 provides comprehensive governance but French-specific regulatory requirements (CNIL, ANSSI regulations) not addressed."
    ),
    (
        "Hygiene.37",
        "Secure premises and physical access",
        90,
        "MP-04 media storage; PE-01 physical protection policy; PE-02 physical access authorizations; PE-03 physical access control; PE-04 access control for transmission medium; PE-05 access control for display medium; PE-06 monitoring physical access; PE-07 visitor control; PE-08 access records; PE-16 delivery and removal; PE-17 alternate work site; PE-18 location of components; PE-19 information leakage; SR-09 tamper resistance. PE family comprehensively addresses physical security.",
        "Minimal gap."
    ),
    (
        "Hygiene.38",
        "Protect environmental infrastructure",
        90,
        "PE-09 power equipment; PE-10 emergency shutoff; PE-11 emergency power; PE-12 emergency lighting; PE-13 fire protection; PE-14 temperature and humidity controls; PE-15 water damage protection; PE-18 location of components. PE family environmental controls comprehensive.",
        "Minimal gap."
    ),
    (
        "Hygiene.39",
        "Implement monitoring and detection",
        90,
        "AU-06 audit review and reporting; CA-07 continuous monitoring; IR-04 incident handling; IR-05 incident monitoring; PE-06 monitoring physical access; SI-04 system monitoring; SI-05 security alerts. SI-04 directly addresses monitoring and detection.",
        "Minimal gap."
    ),
    (
        "Hygiene.40",
        "Report and handle incidents",
        90,
        "IR-01 incident response policy; IR-04 incident handling; IR-06 incident reporting; IR-07 incident response assistance; SR-08 notification agreements. IR family comprehensively addresses incident handling.",
        "Minimal gap."
    ),
    (
        "Hygiene.41",
        "Conduct risk assessments",
        90,
        "CA-02 security assessments; CA-06 security accreditation; PL-05 privacy impact assessment; RA-01 risk assessment policy; RA-02 security categorization; RA-03 risk assessment; RA-04 risk assessment update. RA family directly addresses risk assessment.",
        "Minimal gap."
    ),
    (
        "Hygiene.42",
        "Manage third-party and supply chain security",
        85,
        "SA-04 acquisitions; SA-09 external services; SR-01 supply chain policy; SR-02 supply chain risk management plan; SR-03 supply chain controls; SR-04 provenance; SR-05 acquisition strategies; SR-06 supplier assessments; SR-07 supply chain operations security; SR-08 notification agreements; SR-09 tamper resistance; SR-10 inspection; SR-11 component authenticity; IR-07 incident response assistance. SR family comprehensive.",
        "Minor: ANSSI emphasizes French/EU supply chain sovereignty requirements. SP 800-53 SR family provides strong supply chain risk management but sovereignty and data localisation requirements not covered."
    ),
]

SECNUMCLOUD_CLAUSES = [
    (
        "SecNumCloud.6.1",
        "Information security policies for cloud services",
        80,
        "AC-01 access control policy; AT-01 awareness training policy; AU-01 audit policy; CA-01 assessment policy; CM-01 configuration management policy; CP-01 contingency planning policy; IA-01 identification and authentication policy; IR-01 incident response policy; MA-01 maintenance policy; MP-01 media protection policy; PE-01 physical protection policy; PL-01 security planning policy; PS-01 personnel security policy; PT-01 PII processing policy; RA-01 risk assessment policy; SA-01 acquisition policy; SC-01 system and communications protection policy; SI-01 system integrity policy; SR-01 supply chain policy. Broad policy coverage.",
        "SecNumCloud requires cloud-specific security policies aligned with ANSSI certification requirements and French regulatory framework. SP 800-53 policies are comprehensive but not aligned to ANSSI qualification process."
    ),
    (
        "SecNumCloud.6.2",
        "Review and update of information security policies",
        85,
        "PL-02 system security plan; PL-03 security plan update; PL-06 security-related activity planning. SP 800-53 addresses policy review and update.",
        "Minor: SecNumCloud requires policy review aligned with ANSSI certification renewal cycles."
    ),
    (
        "SecNumCloud.7.2",
        "Risk assessment specific to cloud services",
        80,
        "RA-03 risk assessment; RA-04 risk assessment update. SP 800-53 RA family addresses risk assessment.",
        "SecNumCloud requires cloud-specific risk assessment methodology that addresses multi-tenancy, data sovereignty, and jurisdictional risks. SP 800-53 risk assessment is general-purpose."
    ),
    (
        "SecNumCloud.8.1",
        "Human resources screening and roles",
        85,
        "MA-05 maintenance personnel; PS-01 personnel security policy; PS-02 position categorization; PS-03 personnel screening; PS-07 third-party personnel. PS family provides comprehensive personnel security.",
        "Minor: SecNumCloud requires nationality-based screening for certain roles handling sensitive data. SP 800-53 PS-03 covers screening but French/EU nationality requirements not addressed."
    ),
    (
        "SecNumCloud.8.2",
        "Terms and conditions of employment",
        85,
        "PL-04 rules of behavior; PS-06 access agreements. SP 800-53 covers employment terms and access agreements.",
        "Minor: SecNumCloud requires specific contractual clauses for cloud service personnel aligned with French labour law."
    ),
    (
        "SecNumCloud.8.3",
        "Information security awareness, education and training",
        90,
        "AT-02 security awareness; AT-03 security training; AT-04 training records. AT family comprehensively covers training.",
        "Minimal gap."
    ),
    (
        "SecNumCloud.8.4",
        "Disciplinary process and termination",
        85,
        "PS-04 personnel termination; PS-05 personnel transfer; PS-08 personnel sanctions. PS family covers disciplinary and termination processes.",
        "Minor: SecNumCloud requires specific French labour law compliance for disciplinary actions."
    ),
    (
        "SecNumCloud.9.1",
        "Asset inventory for cloud infrastructure",
        85,
        "CM-08 system component inventory; RA-02 security categorization. CM-08 directly addresses asset inventory.",
        "Minor: SecNumCloud requires cloud-specific asset inventory including virtual resources, tenant isolation boundaries, and data localisation tracking."
    ),
    (
        "SecNumCloud.9.2",
        "Media handling and disposal",
        85,
        "MP-01 media protection policy; MP-02 media access; MP-03 media labeling; MP-04 media storage; MP-05 media transport; SI-12 information management. MP family comprehensively addresses media handling.",
        "Minor: SecNumCloud requires specific media handling procedures for multi-tenant environments and certified destruction processes."
    ),
    (
        "SecNumCloud.9.3",
        "Information disposal and data remanence",
        85,
        "MP-06 media sanitization; SC-04 information remnance; SR-12 component disposal. MP-06 and SC-04 directly address data remanence.",
        "Minor: SecNumCloud has strict requirements on data erasure in multi-tenant cloud environments, including proof of deletion. SP 800-53 covers sanitization but multi-tenant cloud specifics less detailed."
    ),
    (
        "SecNumCloud.10.1",
        "Access control policy for cloud services",
        85,
        "AC-01 access control policy; AC-08 system use notification; AC-14 permitted actions without identification; IA-01 identification and authentication policy. Policy controls address access governance.",
        "Minor: SecNumCloud requires specific access control policies for cloud provider administrative access and tenant isolation."
    ),
    (
        "SecNumCloud.10.2",
        "User registration and identity management",
        90,
        "AC-02 account management; AC-13 supervision and review; IA-04 identifier management. SP 800-53 comprehensively addresses user registration.",
        "Minimal gap."
    ),
    (
        "SecNumCloud.10.3",
        "Access rights management",
        90,
        "AC-03 access enforcement; AC-06 least privilege; SI-09 information input restrictions. SP 800-53 comprehensively addresses access rights.",
        "Minimal gap."
    ),
    (
        "SecNumCloud.10.4",
        "Privileged access management",
        85,
        "AC-05 separation of duties; AC-06 least privilege. SP 800-53 covers privileged access.",
        "Minor: SecNumCloud requires specific privileged access management for cloud infrastructure administrators with French nationality requirements for certain operations."
    ),
    (
        "SecNumCloud.10.5",
        "User authentication for cloud services",
        90,
        "AC-07 unsuccessful login attempts; AC-10 concurrent session control; IA-02 user identification; IA-03 device identification; IA-05 authenticator management; SC-23 session authenticity. IA family comprehensively addresses authentication.",
        "Minimal gap."
    ),
    (
        "SecNumCloud.10.6",
        "Session management and timeout",
        90,
        "AC-11 session lock; AC-12 session termination; AC-19 mobile devices; SC-10 network disconnect. SP 800-53 comprehensively addresses session management.",
        "Minimal gap."
    ),
    (
        "SecNumCloud.10.7",
        "Remote access to cloud administration",
        80,
        "AC-17 remote access. SP 800-53 covers remote access.",
        "SecNumCloud requires administration access from within EU/France only. SP 800-53 AC-17 covers remote access security but geographic restrictions on administrative access not addressed."
    ),
    (
        "SecNumCloud.11.1",
        "Cryptographic controls and key management",
        80,
        "IA-07 cryptographic module authentication; SC-08 transmission integrity; SC-09 transmission confidentiality; SC-12 cryptographic key management; SC-13 use of cryptography; SC-17 PKI certificates. SC family provides comprehensive cryptographic controls.",
        "SecNumCloud mandates use of ANSSI-approved cryptographic algorithms and French/EU-qualified key management. SP 800-53 references FIPS standards (US) rather than ANSSI/EU cryptographic qualifications."
    ),
    (
        "SecNumCloud.12.1",
        "Physical security of cloud data centres",
        85,
        "MP-04 media storage; PE-01 physical protection policy; PE-17 alternate work site; PE-18 location of components. PE family covers physical security.",
        "Minor: SecNumCloud requires data centres to be located within EU territory with specific physical security certifications. SP 800-53 PE family covers physical security but data localisation requirements not addressed."
    ),
    (
        "SecNumCloud.12.2",
        "Physical access controls for cloud facilities",
        90,
        "PE-02 physical access authorizations; PE-03 physical access control; PE-04 access control for transmission medium; PE-05 access control for display medium; PE-06 monitoring physical access; PE-07 visitor control; PE-08 access records; PE-16 delivery and removal; PE-19 information leakage; SR-09 tamper resistance. PE family comprehensive.",
        "Minimal gap."
    ),
    (
        "SecNumCloud.12.3",
        "Environmental protection for cloud infrastructure",
        90,
        "PE-09 power equipment; PE-10 emergency shutoff; PE-11 emergency power; PE-12 emergency lighting; PE-13 fire protection; PE-14 temperature and humidity controls; PE-15 water damage protection. PE family environmental controls comprehensive.",
        "Minimal gap."
    ),
    (
        "SecNumCloud.13.1",
        "Operational procedures and hardening",
        85,
        "CM-01 configuration management policy; CM-02 baseline configuration; CM-06 configuration settings; CM-07 least functionality; SA-06 software usage restrictions; SA-07 user installed software; SC-18 mobile code; SI-03 malicious code protection; SI-08 spam protection. CM and SI families cover operational security.",
        "Minor: SecNumCloud requires specific cloud infrastructure hardening procedures and documented operational runbooks aligned with ANSSI guidelines."
    ),
    (
        "SecNumCloud.13.2",
        "Change management for cloud services",
        90,
        "CM-03 configuration change control; CM-04 monitoring configuration changes; CM-05 access restrictions for change. CM family comprehensively addresses change management.",
        "Minimal gap."
    ),
    (
        "SecNumCloud.13.3",
        "Capacity management",
        75,
        "SC-06 resource priority. SP 800-53 addresses resource priority.",
        "SecNumCloud requires specific capacity management for multi-tenant cloud environments including tenant resource isolation and guaranteed SLAs. SP 800-53 SC-06 covers resource priority but cloud-specific capacity planning less detailed."
    ),
    (
        "SecNumCloud.13.4",
        "Maintenance and support",
        90,
        "MA-01 maintenance policy; MA-02 controlled maintenance; MA-03 maintenance tools; MA-04 remote maintenance; MA-06 timely maintenance. MA family comprehensively addresses maintenance.",
        "Minimal gap."
    ),
    (
        "SecNumCloud.13.5",
        "Backup and restoration for cloud services",
        85,
        "CP-09 system backup. CP-09 directly addresses backup.",
        "Minor: SecNumCloud requires specific backup procedures for multi-tenant environments including tenant data isolation in backups and guaranteed restoration within defined SLAs."
    ),
    (
        "SecNumCloud.13.6",
        "Vulnerability and patch management",
        90,
        "RA-05 vulnerability scanning; SI-01 system integrity policy; SI-02 flaw remediation; SI-05 security alerts; SI-06 security functionality verification; SI-07 software integrity. SI-02 and RA-05 directly address vulnerability and patch management.",
        "Minimal gap."
    ),
    (
        "SecNumCloud.13.7",
        "Logging and monitoring for cloud services",
        90,
        "AC-09 previous logon notification; AU-01 audit policy; AU-02 auditable events; AU-03 audit record content; AU-04 audit storage capacity; AU-05 response to audit failures; AU-06 audit review and reporting; AU-07 audit reduction; AU-08 timestamps; AU-09 protection of audit information; AU-10 non-repudiation; AU-11 audit record retention; CA-07 continuous monitoring; SI-04 system monitoring. AU family comprehensively addresses logging.",
        "Minimal gap."
    ),
    (
        "SecNumCloud.14.1",
        "Network security for cloud infrastructure",
        85,
        "AC-04 information flow enforcement; CA-03 system connections; SC-01 system and communications protection policy; SC-02 application partitioning; SC-03 security function isolation; SC-07 boundary protection; SC-15 collaborative computing; SC-20 secure name resolution; SC-21 secure name resolution (recursive); SC-22 architecture for name resolution. SC family provides comprehensive network security.",
        "Minor: SecNumCloud requires cloud-specific network segmentation including tenant isolation at network level and network security monitoring for cloud-native architectures."
    ),
    (
        "SecNumCloud.14.2",
        "Secure communications and data in transit",
        85,
        "AC-17 remote access; SC-08 transmission integrity; SC-09 transmission confidentiality; SC-11 trusted path; SC-16 transmission of security parameters; SC-19 VoIP. SC family covers data in transit.",
        "Minor: SecNumCloud requires ANSSI-approved protocols and cipher suites for all data in transit within cloud infrastructure."
    ),
    (
        "SecNumCloud.14.3",
        "Wireless network security",
        80,
        "AC-18 wireless access restrictions. AC-18 covers wireless security.",
        "SecNumCloud restricts or prohibits wireless networks in sensitive cloud infrastructure zones. SP 800-53 AC-18 covers wireless access but the stringent restrictions for cloud data centres less explicit."
    ),
    (
        "SecNumCloud.14.4",
        "Protection against denial of service",
        85,
        "SC-05 denial of service protection; SC-07 boundary protection; SC-14 public access protections. SC-05 directly addresses DoS protection.",
        "Minor: SecNumCloud requires specific DDoS mitigation capabilities with EU-based scrubbing centres."
    ),
    (
        "SecNumCloud.15.1",
        "Security in development and acquisition",
        85,
        "SA-01 acquisition policy; SA-02 allocation of resources; SA-03 lifecycle support; SA-04 acquisitions. SA family covers development and acquisition.",
        "Minor: SecNumCloud requires secure development lifecycle aligned with ANSSI secure coding guidelines."
    ),
    (
        "SecNumCloud.15.2",
        "System documentation and change control",
        85,
        "SA-05 system documentation. SP 800-53 covers documentation.",
        "Minor: SecNumCloud requires cloud-specific technical documentation for ANSSI qualification assessment."
    ),
    (
        "SecNumCloud.15.3",
        "Technical security requirements",
        80,
        "SA-08 security engineering principles; SI-10 information accuracy; SI-11 error handling. SP 800-53 covers engineering principles.",
        "SecNumCloud defines specific technical security requirements for cloud platforms including hypervisor security, container isolation, and API security. SP 800-53 covers general engineering principles but cloud-native technical requirements less detailed."
    ),
    (
        "SecNumCloud.15.4",
        "Configuration management for cloud platforms",
        85,
        "SA-10 developer configuration management. SP 800-53 covers developer configuration management.",
        "Minor: SecNumCloud requires specific configuration management for cloud infrastructure components (hypervisors, orchestrators, container platforms)."
    ),
    (
        "SecNumCloud.15.5",
        "Security testing for cloud services",
        85,
        "SA-11 developer security testing. SP 800-53 covers security testing.",
        "Minor: SecNumCloud requires penetration testing aligned with ANSSI PASSI (security audit service provider) methodology."
    ),
    (
        "SecNumCloud.16.1",
        "Supplier and subcontractor management",
        75,
        "AC-20 use of external systems; PS-07 third-party personnel; SA-04 acquisitions; SA-09 external services; SR-01 supply chain policy; SR-02 supply chain risk management plan; SR-03 supply chain controls; SR-04 provenance; SR-05 acquisition strategies; SR-07 supply chain operations security; SR-08 notification agreements; SR-11 component authenticity. SR family provides supply chain coverage.",
        "SecNumCloud requires that all subcontractors and suppliers comply with EU data sovereignty requirements and that no non-EU entity has access to cloud data or administration. SP 800-53 SR family covers supply chain risk but EU sovereignty and extraterritorial law protection (e.g., against US CLOUD Act) not addressed."
    ),
    (
        "SecNumCloud.16.2",
        "Supplier assessment and monitoring",
        80,
        "SA-09 external services; SR-03 supply chain controls; SR-06 supplier assessments; SR-10 inspection of systems. SP 800-53 covers supplier assessment.",
        "SecNumCloud requires supplier qualification aligned with ANSSI requirements including EU sovereignty verification. SP 800-53 covers supplier assessment but ANSSI-specific qualification process not addressed."
    ),
    (
        "SecNumCloud.17.1",
        "Incident management for cloud services",
        85,
        "AU-06 audit review and reporting; IR-01 incident response policy; IR-02 incident response training; IR-04 incident handling; IR-05 incident monitoring; IR-06 incident reporting; IR-07 incident response assistance. IR family comprehensively addresses incident management.",
        "Minor: SecNumCloud requires incident reporting to ANSSI (French CERT-FR) within specific timeframes and notification of tenants according to French regulatory requirements."
    ),
    (
        "SecNumCloud.17.2",
        "Incident response testing and exercises",
        90,
        "IR-03 incident response testing; IR-04 incident handling. SP 800-53 covers incident response testing.",
        "Minimal gap."
    ),
    (
        "SecNumCloud.18.1",
        "Business continuity planning for cloud services",
        80,
        "CP-01 contingency planning policy; CP-02 contingency plan; CP-05 contingency plan update. CP family addresses business continuity.",
        "SecNumCloud requires cloud-specific business continuity plans including multi-region EU failover and tenant data portability. SP 800-53 CP family covers continuity but cloud-specific and EU-localised failover requirements less detailed."
    ),
    (
        "SecNumCloud.18.2",
        "Business continuity testing",
        85,
        "CP-03 contingency training; CP-04 contingency plan testing. SP 800-53 covers continuity testing.",
        "Minor: SecNumCloud requires testing of cloud-specific failover scenarios including tenant isolation during recovery."
    ),
    (
        "SecNumCloud.18.3",
        "Redundancy and disaster recovery",
        80,
        "CP-06 alternate storage site; CP-07 alternate processing site; CP-08 telecommunications services; CP-10 system recovery. CP family covers disaster recovery.",
        "SecNumCloud requires all redundant infrastructure to be located within EU territory. SP 800-53 covers disaster recovery but geographic constraints on alternate sites not addressed."
    ),
    (
        "SecNumCloud.19.1",
        "Compliance with legal and contractual requirements",
        65,
        "CA-01 assessment policy; CA-05 plan of action. SP 800-53 covers compliance planning.",
        "Significant: SecNumCloud compliance requires adherence to French and EU law including GDPR, French data protection law (Loi Informatique et Libertes), and protection against extraterritorial non-EU laws. SP 800-53 focuses on US federal compliance framework."
    ),
    (
        "SecNumCloud.19.2",
        "Independent security audits and ANSSI qualification",
        70,
        "CA-02 security assessments; CA-04 security certification; CA-06 security accreditation; CA-07 continuous monitoring. CA family covers security assessment.",
        "Significant: SecNumCloud requires qualification by ANSSI through accredited PASSI audit providers, following specific French certification methodology. SP 800-53 CA family covers assessment but ANSSI-specific qualification process (SecNumCloud label) has no equivalent."
    ),
    (
        "SecNumCloud.19.3",
        "Data protection and privacy compliance",
        70,
        "PT-01 policy and procedures; PT-02 authority to process PII; PT-03 PII processing purposes; PT-04 consent; PT-05 privacy notice; PT-06 system of records notice; PT-07 specific categories of PII; PT-08 computer matching requirements. PT family covers privacy.",
        "Significant: SecNumCloud data protection requirements are aligned with GDPR and French CNIL requirements, including data residency within EU, Data Protection Impact Assessments (DPIA), and specific cloud data protection obligations. SP 800-53 PT family addresses US privacy requirements but EU/French data protection framework materially different."
    ),
]

RGS_CLAUSES = [
    (
        "RGS.1.2",
        "Security awareness and competence",
        85,
        "AT-01 awareness training policy. SP 800-53 covers awareness requirements.",
        "Minor: RGS requires awareness programmes aligned with French government security classification framework."
    ),
    (
        "RGS.1.3",
        "Security policy framework",
        80,
        "AC-01 access control policy; AU-01 audit policy; CA-01 assessment policy; PL-01 security planning policy; RA-01 risk assessment policy; SC-01 system and communications protection policy. Broad policy coverage.",
        "RGS requires security policies aligned with French General Security Framework (RGS v2.0) and ANSSI requirements. SP 800-53 provides comprehensive policies but French-specific RGS alignment not addressed."
    ),
    (
        "RGS.2.1",
        "Non-repudiation and electronic signatures",
        75,
        "AU-10 non-repudiation. SP 800-53 covers non-repudiation.",
        "RGS mandates compliance with eIDAS regulation and French electronic signature standards. SP 800-53 AU-10 covers non-repudiation but EU eIDAS-qualified electronic signatures and French trust services not addressed."
    ),
    (
        "RGS.2.2",
        "Authentication mechanisms",
        80,
        "IA-01 identification and authentication policy; IA-02 user identification; IA-05 authenticator management; SC-16 transmission of security parameters. IA family covers authentication.",
        "RGS mandates specific authentication levels (one-factor, two-factor, qualified) aligned with French government trust framework. SP 800-53 IA family covers authentication but RGS-specific trust levels and French qualification requirements not addressed."
    ),
    (
        "RGS.2.3",
        "Cryptographic requirements",
        75,
        "IA-07 cryptographic module authentication; SC-08 transmission integrity; SC-09 transmission confidentiality; SC-12 cryptographic key management; SC-13 use of cryptography; SC-17 PKI certificates. SC family covers cryptography.",
        "RGS mandates ANSSI-approved cryptographic algorithms and key sizes (Annexe B of RGS). SP 800-53 references FIPS 140-2/3 (US standards). French/ANSSI cryptographic requirements differ from US NIST standards."
    ),
    (
        "RGS.3.1",
        "Risk assessment methodology",
        80,
        "RA-03 risk assessment. SP 800-53 covers risk assessment.",
        "RGS recommends EBIOS RM methodology (French risk assessment framework developed by ANSSI). SP 800-53 RA-03 covers risk assessment but EBIOS RM methodology not addressed."
    ),
    (
        "RGS.4.1",
        "Security qualification and compliance assessment",
        65,
        "CA-02 security assessments; CA-04 security certification; CA-06 security accreditation. CA family covers security assessment.",
        "Significant: RGS qualification requires assessment by ANSSI-accredited bodies following French government audit methodology. SP 800-53 CA family covers assessment but RGS-specific qualification (visa de securite) has no equivalent."
    ),
]


def load_manifest():
    """Load the controls manifest file."""
    manifest_path = os.path.join(CONTROLS_DIR, '_manifest.json')
    with open(manifest_path) as f:
        return json.load(f)


def build_reverse_mappings(manifest):
    """Build reverse mappings: ANSSI clause -> list of SP 800-53 control IDs."""
    reverse = defaultdict(list)

    for ctrl_entry in manifest['controls']:
        ctrl_file = os.path.join(CONTROLS_DIR, ctrl_entry['file'])
        with open(ctrl_file) as f:
            ctrl = json.load(f)

        anssi_clauses = ctrl.get('compliance_mappings', {}).get('anssi', [])
        for clause_id in anssi_clauses:
            reverse[clause_id].append(ctrl['id'])

    # Sort and deduplicate control lists
    for clause_id in reverse:
        reverse[clause_id] = sorted(set(reverse[clause_id]))

    return dict(reverse)


def classify_coverage(pct):
    """Classify coverage percentage into a band."""
    if pct >= 85:
        return "full"
    elif pct >= 65:
        return "substantial"
    elif pct >= 40:
        return "partial"
    elif pct >= 1:
        return "weak"
    else:
        return "none"


def build_clause_entry(clause_tuple, reverse_mappings):
    """Build a clause entry merging expert data with actual reverse mappings."""
    clause_id, title, coverage_pct, rationale, gaps = clause_tuple

    # Use controls from actual reverse mappings if available
    controls_from_data = reverse_mappings.get(clause_id, [])

    return {
        "id": clause_id,
        "title": title,
        "controls": controls_from_data,
        "coverage_pct": coverage_pct,
        "rationale": rationale,
        "gaps": gaps
    }


def compute_summary(clauses):
    """Compute summary statistics for all clauses."""
    total = len(clauses)
    if total == 0:
        return {
            "total_clauses": 0,
            "average_coverage": 0,
            "full_count": 0,
            "substantial_count": 0,
            "partial_count": 0,
            "weak_count": 0,
            "none_count": 0
        }

    coverages = [c["coverage_pct"] for c in clauses]
    avg = round(sum(coverages) / total, 1)

    full_count = sum(1 for c in coverages if c >= 85)
    substantial_count = sum(1 for c in coverages if 65 <= c < 85)
    partial_count = sum(1 for c in coverages if 40 <= c < 65)
    weak_count = sum(1 for c in coverages if 1 <= c < 40)
    none_count = sum(1 for c in coverages if c == 0)

    return {
        "total_clauses": total,
        "average_coverage": avg,
        "full_count": full_count,
        "substantial_count": substantial_count,
        "partial_count": partial_count,
        "weak_count": weak_count,
        "none_count": none_count
    }


def generate_coverage():
    """Generate the complete ANSSI coverage analysis JSON."""
    print("Loading manifest...")
    manifest = load_manifest()
    print(f"  Found {len(manifest['controls'])} controls")

    print("Building reverse mappings...")
    reverse_mappings = build_reverse_mappings(manifest)
    print(f"  Found {len(reverse_mappings)} unique ANSSI clause references")

    # Report any clauses in data but not in our expert list
    expert_ids = set()
    for clause_list in [HYGIENE_CLAUSES, SECNUMCLOUD_CLAUSES, RGS_CLAUSES]:
        for c in clause_list:
            expert_ids.add(c[0])

    data_ids = set(reverse_mappings.keys())
    unmapped = data_ids - expert_ids
    if unmapped:
        print(f"  WARNING: {len(unmapped)} clause(s) in control data but not in expert analysis:")
        for uid in sorted(unmapped):
            print(f"    {uid}: {reverse_mappings[uid]}")

    missing = expert_ids - data_ids
    if missing:
        print(f"  NOTE: {len(missing)} clause(s) in expert analysis but not found in control data:")
        for mid in sorted(missing):
            print(f"    {mid}")

    print("Building clause entries...")
    clauses = []

    # Hygiene Guide clauses
    for clause_tuple in HYGIENE_CLAUSES:
        clauses.append(build_clause_entry(clause_tuple, reverse_mappings))

    # SecNumCloud clauses
    for clause_tuple in SECNUMCLOUD_CLAUSES:
        clauses.append(build_clause_entry(clause_tuple, reverse_mappings))

    # RGS clauses
    for clause_tuple in RGS_CLAUSES:
        clauses.append(build_clause_entry(clause_tuple, reverse_mappings))

    print(f"  Built {len(clauses)} clause entries")

    summary = compute_summary(clauses)
    print(f"  Average coverage: {summary['average_coverage']}%")
    print(f"  Full: {summary['full_count']}, Substantial: {summary['substantial_count']}, "
          f"Partial: {summary['partial_count']}, Weak: {summary['weak_count']}, "
          f"None: {summary['none_count']}")

    output = {
        "$schema": "../schema/framework-coverage.schema.json",
        "framework_id": "anssi",
        "framework_name": "ANSSI Hygiene Guide & SecNumCloud",
        "metadata": {
            "source": "SP800-53v5_Control_Mappings",
            "version": "1.0",
            "disclaimer": "Based on publicly available crosswalks and expert analysis. ANSSI Hygiene Guide (Guide d'hygiene informatique, 42 measures), SecNumCloud (cloud security qualification), and RGS (Referentiel General de Securite). Validate with qualified assessors and ANSSI-accredited PASSI providers for compliance/audit use."
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
        "summary": summary
    }

    # Ensure output directory exists
    os.makedirs(COVERAGE_DIR, exist_ok=True)

    print(f"Writing output to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print("Done.")
    return output


def validate_output(output):
    """Perform basic validation of the generated output."""
    errors = []

    # Check required top-level keys
    for key in ["framework_id", "framework_name", "metadata", "weight_scale", "clauses", "summary"]:
        if key not in output:
            errors.append(f"Missing required key: {key}")

    # Check metadata
    meta = output.get("metadata", {})
    for key in ["source", "version", "disclaimer"]:
        if key not in meta:
            errors.append(f"Missing metadata key: {key}")

    # Check weight_scale
    ws = output.get("weight_scale", {})
    for band in ["full", "substantial", "partial", "weak", "none"]:
        if band not in ws:
            errors.append(f"Missing weight_scale band: {band}")
        else:
            for key in ["min", "max", "label"]:
                if key not in ws[band]:
                    errors.append(f"Missing weight_scale.{band}.{key}")

    # Check clauses
    clauses = output.get("clauses", [])
    for i, clause in enumerate(clauses):
        for key in ["id", "title", "controls", "coverage_pct", "rationale", "gaps"]:
            if key not in clause:
                errors.append(f"Clause {i} missing key: {key}")
        if "coverage_pct" in clause:
            pct = clause["coverage_pct"]
            if not isinstance(pct, int) or pct < 0 or pct > 100:
                errors.append(f"Clause {clause.get('id', i)}: coverage_pct must be int 0-100, got {pct}")
        if "controls" in clause:
            if not isinstance(clause["controls"], list):
                errors.append(f"Clause {clause.get('id', i)}: controls must be a list")

    # Check summary
    summary = output.get("summary", {})
    for key in ["total_clauses", "average_coverage", "full_count", "substantial_count",
                 "partial_count", "weak_count", "none_count"]:
        if key not in summary:
            errors.append(f"Missing summary key: {key}")

    # Verify summary counts add up
    if all(k in summary for k in ["total_clauses", "full_count", "substantial_count",
                                    "partial_count", "weak_count", "none_count"]):
        count_sum = (summary["full_count"] + summary["substantial_count"] +
                     summary["partial_count"] + summary["weak_count"] + summary["none_count"])
        if count_sum != summary["total_clauses"]:
            errors.append(f"Summary counts ({count_sum}) do not match total_clauses ({summary['total_clauses']})")

    # Verify total_clauses matches actual clause count
    if "total_clauses" in summary and len(clauses) != summary["total_clauses"]:
        errors.append(f"total_clauses ({summary['total_clauses']}) does not match actual clauses ({len(clauses)})")

    return errors


if __name__ == '__main__':
    output = generate_coverage()

    print("\nValidating output...")
    errors = validate_output(output)
    if errors:
        print(f"VALIDATION FAILED with {len(errors)} error(s):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("Validation passed.")

    # Verify JSON is valid by re-reading the file
    print(f"Verifying {OUTPUT_FILE} is valid JSON...")
    with open(OUTPUT_FILE) as f:
        reloaded = json.load(f)
    print(f"  Loaded successfully: {len(reloaded['clauses'])} clauses, "
          f"average coverage {reloaded['summary']['average_coverage']}%")
    print("\nAll checks passed.")
