#!/usr/bin/env python3
"""
Generate PM (Program Management) family control JSON files for osa-data.

Creates all 32 PM controls (PM-01 through PM-32) with:
- Authoritative NIST SP 800-53 Rev 5 definitions
- Compliance mappings extracted from framework-coverage JSONs
- Schema-compliant JSON matching existing control format

Usage:
    cd ~/osa-data && python3 scripts/generate_pm_controls.py
"""

import json
import os
import re
from datetime import date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")
CONTROLS_DIR = os.path.join(DATA_DIR, "controls")
COVERAGE_DIR = os.path.join(DATA_DIR, "framework-coverage")
MANIFEST_PATH = os.path.join(CONTROLS_DIR, "_manifest.json")

# All 21 compliance_mapping keys in the order used by existing controls
FRAMEWORK_KEYS = [
    "iso_27001_2022", "iso_27002_2022", "cobit_2019", "pci_dss_v4",
    "nist_csf_2", "cis_controls_v8", "soc2_tsc", "finos_ccc",
    "iso_42001_2023", "iec_62443", "asd_e8", "nis2", "apra_cps_234",
    "mas_trm", "uk_pra_fca", "bsi_grundschutz", "anssi", "osfi_b13",
    "finma_circular", "gdpr", "dora",
]


# ---------------------------------------------------------------------------
# PM control definitions from NIST SP 800-53 Rev 5
# ---------------------------------------------------------------------------

PM_CONTROLS = [
    {
        "num": 1,
        "name": "Information Security Program Plan",
        "control_class": "Management",
        "description": "Develop and disseminate an organization-wide information security program plan that: a. Provides an overview of the requirements for the security program and a description of the security program management controls and common controls in place or planned for meeting those requirements; b. Includes the identification and assignment of roles, responsibilities, management commitment, coordination among organizational entities, and compliance; c. Reflects the coordination among organizational entities responsible for information security; and d. Is approved by a senior official with responsibility and accountability for the risk being incurred to organizational operations (including mission, functions, image, and reputation), organizational assets, individuals, other organizations, and the Nation.",
        "supplemental_guidance": "An information security program plan is a formal document that provides an overview of the security requirements for an organization-wide information security program and describes the program management controls and common controls in place or planned for meeting those requirements. The plan can be represented in a single document or compilations of documents. The plan documents the program management controls and organization-defined common controls. The plan provides sufficient information about the controls (including specification of parameters for assignment and selection operations, explicitly or by reference) to enable an implementation that is unambiguously compliant with the intent of the plan and a determination of the risk to be incurred if the plan is implemented as intended. Updates to information security program plans include organizational changes and problems identified during plan implementation or control assessments.",
        "related_controls": ["AC-1", "AU-1", "CA-1", "CA-7", "CM-1", "CP-1", "IA-1", "IR-1", "MA-1", "MP-1", "PE-1", "PL-1", "PL-2", "PL-7", "PM-6", "PM-8", "PM-9", "PM-10", "PM-11", "PS-1", "PT-1", "RA-1", "SA-1", "SC-1", "SI-1", "SR-1"],
        "baseline_privacy": False,
        "new_in_rev5": False,
        "rev4_id": "PM-1",
        "rev4_name": "Information Security Program Plan",
        "changes_from_rev4": "Title unchanged. Incorporates guidance from multiple sources. Discussion expanded to address program plan updates and organizational changes.",
    },
    {
        "num": 2,
        "name": "Information Security Program Leadership Role",
        "control_class": "Management",
        "description": "Appoint a senior information security official with the mission and resources to coordinate, develop, implement, and maintain an organization-wide information security program.",
        "supplemental_guidance": "The senior information security official is an organizational official. For federal agencies, this official is the senior agency information security officer (SAISO) or chief information security officer (CISO) with the mission and resources to coordinate, develop, implement, and maintain an organization-wide information security program. The security official is an inherent United States Government authority and is assigned to or created by the organization, not the information system.",
        "related_controls": ["PM-1"],
        "baseline_privacy": False,
        "new_in_rev5": False,
        "rev4_id": "PM-2",
        "rev4_name": "Senior Information Security Officer",
        "changes_from_rev4": "Title changed from 'Senior Information Security Officer' to 'Information Security Program Leadership Role'. Broadened to emphasize mission and resources.",
    },
    {
        "num": 3,
        "name": "Information Security and Privacy Resources",
        "control_class": "Management",
        "description": "a. Include the resources needed to implement the information security and privacy programs in capital planning and investment requests and document all exceptions to this requirement; b. Prepare documentation required for addressing information security and privacy programs in capital planning and investment requests in accordance with applicable laws, executive orders, directives, policies, regulations, standards; and c. Make available for expenditure, the planned information security and privacy resources.",
        "supplemental_guidance": "Organizations consider establishing champions for information security and privacy and, as part of including the necessary resources, assign specialized expertise and resources as needed. Organizations may designate and empower an Investment Review Board or similar group to manage and provide oversight for the information security and privacy aspects of the capital planning and investment control process.",
        "related_controls": ["PM-1", "SA-2"],
        "baseline_privacy": False,
        "new_in_rev5": False,
        "rev4_id": "PM-3",
        "rev4_name": "Information Security Resources",
        "changes_from_rev4": "Title changed from 'Information Security Resources' to 'Information Security and Privacy Resources'. Privacy added throughout.",
    },
    {
        "num": 4,
        "name": "Plan of Action and Milestones Process",
        "control_class": "Management",
        "description": "a. Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems are maintained and document the remedial information security, privacy, and supply chain risk management actions to adequately respond to risk to organizational operations and assets, individuals, other organizations, and the Nation; and b. Review plans of action and milestones for consistency with the organizational risk management strategy and organization-wide priorities for risk response actions.",
        "supplemental_guidance": "The plan of action and milestones is a key organizational document and is subject to reporting requirements established by OMB. Organizations develop plans of action and milestones with an organizational perspective, prioritizing risk response actions and ensuring consistency with the goals and objectives of the organization. Plan of action and milestones updates are based on findings from control assessments and continuous monitoring activities. There can be multiple plans of action and milestones corresponding to the information system level and the organization level.",
        "related_controls": ["CA-5", "CA-7", "PM-9", "SI-12"],
        "baseline_privacy": False,
        "new_in_rev5": False,
        "rev4_id": "PM-4",
        "rev4_name": "Plan of Action and Milestones Process",
        "changes_from_rev4": "Privacy and supply chain risk management added. Review of POA&M consistency with risk management strategy added.",
    },
    {
        "num": 5,
        "name": "System Inventory",
        "control_class": "Management",
        "description": "Develop and update [Assignment: organization-defined frequency] an inventory of organizational systems.",
        "supplemental_guidance": "OMB provides guidance on developing systems inventories and associated reporting requirements. System inventory refers to an organization-wide inventory of systems, not system components as described in CM-8.",
        "related_controls": ["CM-8", "PM-10"],
        "baseline_privacy": False,
        "new_in_rev5": False,
        "rev4_id": "PM-5",
        "rev4_name": "Information System Inventory",
        "changes_from_rev4": "Title changed from 'Information System Inventory' to 'System Inventory'. Simplified description.",
    },
    {
        "num": 6,
        "name": "Measures of Performance",
        "control_class": "Management",
        "description": "Develop, monitor, and report on the results of information security and privacy measures of performance.",
        "supplemental_guidance": "Measures of performance are outcome-based metrics used by an organization to measure the effectiveness or efficiency of the information security and privacy programs and the controls employed in support of the program. To facilitate security and privacy risk management, organizations consider aligning measures of performance with the organizational risk tolerance as defined in the risk management strategy.",
        "related_controls": ["CA-7", "PM-9"],
        "baseline_privacy": False,
        "new_in_rev5": False,
        "rev4_id": "PM-6",
        "rev4_name": "Information Security Measures of Performance",
        "changes_from_rev4": "Title changed from 'Information Security Measures of Performance' to 'Measures of Performance'. Privacy added.",
    },
    {
        "num": 7,
        "name": "Enterprise Architecture",
        "control_class": "Management",
        "description": "Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation.",
        "supplemental_guidance": "The integration of security and privacy requirements and associated controls into the organization's enterprise architecture helps to ensure that security and privacy considerations are addressed throughout the system development life cycle and are explicitly related to the organization's mission and business processes. The process of security and privacy requirements integration also embeds into the enterprise architecture and the organization's security and privacy architectures consistent with the organizational risk management strategy.",
        "related_controls": ["AU-6", "PL-2", "PL-7", "PM-11", "RA-2", "SA-2", "SA-17"],
        "baseline_privacy": False,
        "new_in_rev5": False,
        "rev4_id": "PM-7",
        "rev4_name": "Enterprise Architecture",
        "changes_from_rev4": "Privacy added. Risk to individuals and other organizations added.",
    },
    {
        "num": 8,
        "name": "Critical Infrastructure Plan",
        "control_class": "Management",
        "description": "Address information security and privacy issues in the development of a critical infrastructure and key resources protection plan.",
        "supplemental_guidance": "Protection strategies are based on the prioritization of critical assets and resources. The requirement and guidance for defining critical infrastructure and key resources and for preparing an associated critical infrastructure protection plan are found in applicable laws, executive orders, directives, policies, regulations, standards, and guidelines.",
        "related_controls": ["PM-1", "PM-9", "PM-11", "PM-18", "RA-3", "SI-12"],
        "baseline_privacy": False,
        "new_in_rev5": False,
        "rev4_id": "PM-8",
        "rev4_name": "Critical Infrastructure Plan",
        "changes_from_rev4": "Privacy added. Related controls updated.",
    },
    {
        "num": 9,
        "name": "Risk Management Strategy",
        "control_class": "Management",
        "description": "a. Develop a comprehensive strategy to manage: 1. Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and 2. Privacy risk to individuals resulting from the authorized processing of personally identifiable information; b. Implement the risk management strategy consistently across the organization; and c. Review and update the risk management strategy [Assignment: organization-defined frequency] or as required, to address organizational changes.",
        "supplemental_guidance": "An organization-wide risk management strategy includes an expression of the security and privacy risk tolerance for the organization, security and privacy risk mitigation strategies, acceptable risk assessment methodologies, a process for evaluating security and privacy risk across the organization with respect to the organization's risk tolerance, and approaches for monitoring risk over time. The senior accountable official for risk management (agency head or designated official) aligns information security management processes with strategic, operational, and budgetary planning processes.",
        "related_controls": ["AC-1", "AU-1", "CA-1", "CA-7", "CM-1", "CP-1", "IA-1", "IR-1", "MA-1", "MP-1", "PE-1", "PL-1", "PL-2", "PM-4", "PM-28", "PS-1", "PT-1", "RA-1", "RA-3", "SA-1", "SC-1", "SI-1", "SR-1"],
        "baseline_privacy": False,
        "new_in_rev5": False,
        "rev4_id": "PM-9",
        "rev4_name": "Risk Management Strategy",
        "changes_from_rev4": "Privacy risk added. Review and update frequency added as assignment parameter.",
    },
    {
        "num": 10,
        "name": "Authorization Process",
        "control_class": "Management",
        "description": "a. Manage the security and privacy state of organizational systems and the environments in which those systems operate through authorization processes; b. Designate individuals to fulfill specific roles and responsibilities within the organizational risk management process; and c. Integrate the authorization processes into an organization-wide risk management program.",
        "supplemental_guidance": "Authorization processes for organizational systems and environments of operation require the implementation of an organization-wide risk management process and associated security and privacy standards and guidelines. Specific roles for risk management processes include a risk executive (function) and designated authorizing officials for each organizational system and common control provider. The authorization processes for the organization are integrated with continuous monitoring processes to facilitate ongoing understanding and acceptance of security and privacy risks to organizational operations, organizational assets, individuals, other organizations, and the Nation.",
        "related_controls": ["CA-6", "CA-7"],
        "baseline_privacy": False,
        "new_in_rev5": False,
        "rev4_id": "PM-10",
        "rev4_name": "Security Authorization Process",
        "changes_from_rev4": "Title changed from 'Security Authorization Process' to 'Authorization Process'. Privacy added throughout.",
    },
    {
        "num": 11,
        "name": "Mission and Business Process Definition",
        "control_class": "Management",
        "description": "a. Define organizational mission and business processes with consideration for information security and privacy and the resulting risk to organizational operations, organizational assets, individuals, other organizations, and the Nation; and b. Determine information protection and personally identifiable information processing needs arising from the defined mission and business processes; and c. Review and revise the mission and business processes [Assignment: organization-defined frequency].",
        "supplemental_guidance": "Protection needs are technology-independent capabilities that are required to counter threats to organizations, individuals, systems, and the Nation through the compromise of information (i.e., loss of confidentiality, integrity, availability, or privacy). Information protection and personally identifiable information processing needs are derived from the mission and business needs defined by organizational stakeholders, the mission and business processes designed to meet those needs, and the organizational risk management strategy.",
        "related_controls": ["CP-2", "PL-2", "PM-7", "PM-8", "RA-2", "RA-3", "SA-2"],
        "baseline_privacy": False,
        "new_in_rev5": False,
        "rev4_id": "PM-11",
        "rev4_name": "Mission/Business Process Definition",
        "changes_from_rev4": "Title changed. Privacy and PII processing needs added. Review frequency added.",
    },
    {
        "num": 12,
        "name": "Insider Threat Program",
        "control_class": "Management",
        "description": "Implement an insider threat program that includes a cross-discipline insider threat incident handling team.",
        "supplemental_guidance": "Organizations that handle classified information are required, under Executive Order 13587 and the National Insider Threat Policy, to establish insider threat programs. The standards and guidelines that apply to insider threat programs in classified environments can also be employed effectively to improve the security of controlled unclassified information in non-national security systems. Insider threat programs include controls to detect and prevent malicious insider activity through the centralized integration and analysis of both technical and nontechnical information to identify potential insider threat concerns.",
        "related_controls": ["AC-6", "AT-2", "AU-6", "AU-7", "AU-10", "AU-12", "AU-13", "CA-7", "IA-4", "IR-1", "IR-4", "MP-7", "PE-2", "PM-16", "PS-3", "PS-4", "PS-5", "PS-7", "PS-8", "SC-7", "SC-38", "SI-4"],
        "baseline_privacy": False,
        "new_in_rev5": False,
        "rev4_id": "PM-12",
        "rev4_name": "Insider Threat Program",
        "changes_from_rev4": "No significant changes from Rev 4.",
    },
    {
        "num": 13,
        "name": "Security and Privacy Workforce",
        "control_class": "Management",
        "description": "Establish a security and privacy workforce development and improvement program.",
        "supplemental_guidance": "Security and privacy workforce development and improvement programs include the definition of the knowledge, skills, and abilities needed to perform security and privacy duties and tasks; the development, improvement, and delivery of training and education programs; and the ongoing assessment of the workforce to ensure that the knowledge, skills, and abilities are being effectively applied to protect organizational operations, organizational assets, and individuals.",
        "related_controls": ["AT-1", "AT-2", "AT-3"],
        "baseline_privacy": False,
        "new_in_rev5": False,
        "rev4_id": "PM-13",
        "rev4_name": "Information Security Workforce",
        "changes_from_rev4": "Title changed from 'Information Security Workforce' to 'Security and Privacy Workforce'. Privacy added.",
    },
    {
        "num": 14,
        "name": "Testing, Training, and Monitoring",
        "control_class": "Management",
        "description": "a. Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems are developed and maintained; and b. Review testing, training, and monitoring plans for consistency with the organizational risk management strategy and organization-wide priorities for risk response actions.",
        "supplemental_guidance": "A process for organization-wide security and privacy testing, training, and monitoring helps ensure that organizations provide oversight for the testing, training, and monitoring activities conducted organization-wide and that those activities are coordinated. With the importance of continuous monitoring programs, the implementation of information security and privacy across the three levels of the risk management hierarchy and the widespread use of common controls, organizations coordinate and consolidate the testing and monitoring activities that are routinely conducted as part of ongoing organizational assessments supporting a variety of controls.",
        "related_controls": ["AT-1", "AT-2", "AT-3", "CA-7", "CP-4", "IR-3", "PM-12", "SI-4"],
        "baseline_privacy": False,
        "new_in_rev5": False,
        "rev4_id": "PM-14",
        "rev4_name": "Testing, Training, and Monitoring",
        "changes_from_rev4": "Privacy added. Review of plans for consistency with risk management strategy added.",
    },
    {
        "num": 15,
        "name": "Security and Privacy Groups and Associations",
        "control_class": "Management",
        "description": "Establish and institutionalize contact with selected groups and associations within the security and privacy communities: a. To facilitate ongoing security and privacy education and training for organizational personnel; b. To maintain currency with recommended security and privacy practices, techniques, and technologies; and c. To share current security and privacy-related information including threats, vulnerabilities, and incidents.",
        "supplemental_guidance": "Ongoing contact with security and privacy groups and associations is important in an environment of rapidly changing technologies and threats. Groups and associations include special interest groups, professional associations, forums, news groups, users' groups, and peer groups of security and privacy professionals in similar organizations. Organizations select security and privacy groups and associations based on the mission and business functions of the organization.",
        "related_controls": ["SI-5"],
        "baseline_privacy": False,
        "new_in_rev5": False,
        "rev4_id": "PM-15",
        "rev4_name": "Contacts with Security Groups and Associations",
        "changes_from_rev4": "Title changed. Privacy added throughout.",
    },
    {
        "num": 16,
        "name": "Threat Awareness Program",
        "control_class": "Management",
        "description": "Implement a threat awareness program that includes a cross-organization information-sharing capability that can influence the development of the system and security architectures, selection of security solutions, monitoring, threat intelligence, and impact of threats on the risk to organizational operations and assets, individuals, other organizations, and the Nation.",
        "supplemental_guidance": "Because of the constantly changing and increasing sophistication of adversaries, especially the advanced persistent threat (APT), it may be more likely that adversaries can successfully breach or compromise organizational systems. One of the best techniques to address this concern is for organizations to share threat information, including threat events (i.e., tactics, techniques, and procedures) that organizations have experienced, mitigations that organizations have found are effective against certain types of threats, and threat intelligence (i.e., indications and warnings about threats). Threat information sharing may be bilateral or multilateral.",
        "related_controls": ["AT-2", "PM-12", "RA-3"],
        "baseline_privacy": False,
        "new_in_rev5": False,
        "rev4_id": "PM-16",
        "rev4_name": "Threat Awareness Program",
        "changes_from_rev4": "Cross-organization information-sharing capability added. Discussion expanded for APT awareness.",
    },
    {
        "num": 17,
        "name": "Protecting Controlled Unclassified Information on External Systems",
        "control_class": "Management",
        "description": "a. Establish policy and procedures to ensure that requirements for the protection of controlled unclassified information that is processed, stored or transmitted on external systems, are implemented in accordance with applicable laws, executive orders, directives, policies, regulations, and standards; and b. Review and update the policy and procedures [Assignment: organization-defined frequency].",
        "supplemental_guidance": "Controlled unclassified information is defined by the National Archives and Records Administration along with the safeguarding and dissemination requirements for such information. The CUI Registry identifies approved CUI categories and subcategories with associated markings, safeguarding, and dissemination requirements. External systems include the systems of contractors and other organizations.",
        "related_controls": ["AC-1", "AC-20", "CA-1", "CM-1", "IA-1", "SC-1"],
        "baseline_privacy": False,
        "new_in_rev5": True,
        "rev4_id": None,
        "rev4_name": None,
        "changes_from_rev4": "New control in Rev 5.",
    },
    {
        "num": 18,
        "name": "Privacy Program Plan",
        "control_class": "Management",
        "description": "a. Develop and disseminate an organization-wide privacy program plan that provides an overview of the agency's privacy program and: 1. Includes a description of the structure of the privacy program and the resources dedicated to the privacy program; 2. Provides an overview of the requirements for the privacy program and a description of the privacy program management controls and common controls in place or planned for meeting those requirements; 3. Includes the role of the senior agency official for privacy and the identification and assignment of roles of other privacy officials and staff and their responsibilities; 4. Describes management commitment, compliance, and the strategic goals and objectives of the privacy program; 5. Reflects coordination among organizational entities responsible for the different aspects of privacy; and 6. Is approved by a senior official with responsibility and accountability for the privacy risk being incurred to organizational operations (including mission, functions, image, and reputation), organizational assets, individuals, other organizations, and the Nation; and b. Update the plan [Assignment: organization-defined frequency] and to address changes in federal privacy laws and policy and organizational changes and problems identified during plan implementation or privacy control assessments.",
        "supplemental_guidance": "A privacy program plan is a formal document that provides an overview of an organization's privacy program, including a description of the structure of the privacy program, the resources dedicated to the privacy program, the role of the senior agency official for privacy and other privacy officials and staff, the strategic goals and objectives of the privacy program, and the program management controls and common controls in place or planned for meeting applicable privacy requirements and managing privacy risks.",
        "related_controls": ["PM-8", "PM-19", "PM-20"],
        "baseline_privacy": True,
        "new_in_rev5": True,
        "rev4_id": None,
        "rev4_name": None,
        "changes_from_rev4": "New control in Rev 5. Addresses privacy program planning requirements.",
    },
    {
        "num": 19,
        "name": "Privacy Program Leadership Role",
        "control_class": "Management",
        "description": "Appoint a senior agency official for privacy with the authority, mission, and resources to coordinate, develop, and implement applicable privacy requirements and manage privacy risks through the organization-wide privacy program.",
        "supplemental_guidance": "The privacy function can be centralized or decentralized depending upon the organizational structure and composition. In either case, adequate resources need to be allocated to ensure that the privacy function has the capability and capacity to support the organization's need for privacy.",
        "related_controls": ["PM-18", "PM-20"],
        "baseline_privacy": True,
        "new_in_rev5": True,
        "rev4_id": None,
        "rev4_name": None,
        "changes_from_rev4": "New control in Rev 5. Establishes privacy leadership role.",
    },
    {
        "num": 20,
        "name": "Dissemination of Privacy Program Information",
        "control_class": "Management",
        "description": "Maintain a central resource page on the organization's principal public website that serves as a central source of information for the organization's privacy program and that: a. Ensures that the public has access to information about the organizational privacy activities and can communicate with its senior agency official for privacy; b. Ensures that organizational privacy practices and reports are publicly available; and c. Employs publicly facing email addresses and/or other mechanisms to enable the public to provide feedback and/or direct questions to privacy offices regarding privacy practices.",
        "supplemental_guidance": "For federal agencies, the webpage is located at www.[agency].gov/privacy. Organizations employ publicly facing email addresses and/or other mechanisms to inform the public about changes to privacy practices, privacy impacts, or organizational actions.",
        "related_controls": ["PM-18", "PM-19", "PT-6", "PT-7"],
        "baseline_privacy": True,
        "new_in_rev5": True,
        "rev4_id": None,
        "rev4_name": None,
        "changes_from_rev4": "New control in Rev 5. Public transparency for privacy programs.",
    },
    {
        "num": 21,
        "name": "Accounting of Disclosures",
        "control_class": "Management",
        "description": "a. Develop and maintain an accurate accounting of disclosures of personally identifiable information, including: 1. Date, nature, and purpose of each disclosure; and 2. Name and address of the person or organization to which the disclosure was made; b. Retain the accounting of disclosures for the length of the time the personally identifiable information is maintained or five years after the disclosure is made, whichever is longer; and c. Make the accounting of disclosures available to the person named in the record upon request.",
        "supplemental_guidance": "The accounting of disclosures pertains to disclosures of personally identifiable information outside of the organization (excluding disclosures that are required by law, or disclosures that are made to officers and employees of the organization).",
        "related_controls": ["AC-3", "AU-2", "PT-2"],
        "baseline_privacy": True,
        "new_in_rev5": True,
        "rev4_id": None,
        "rev4_name": None,
        "changes_from_rev4": "New control in Rev 5. Addresses Privacy Act accounting requirements.",
    },
    {
        "num": 22,
        "name": "Personally Identifiable Information Quality Management",
        "control_class": "Management",
        "description": "Develop and implement organizational policies and procedures that address the quality of personally identifiable information. Ensure policies and procedures address the steps that the organization takes to confirm the accuracy and relevance of personally identifiable information throughout the information life cycle.",
        "supplemental_guidance": "The quality of personally identifiable information can impact the ability of organizations to make accurate determinations about individuals and can create privacy risks when inaccurate or outdated information is maintained, disseminated, or used in decision-making. Establishing policies and procedures to address the quality of PII helps organizations proactively manage data quality issues and mitigate the risk of unauthorized or inappropriate use of inaccurate PII.",
        "related_controls": ["PM-24", "SI-18"],
        "baseline_privacy": True,
        "new_in_rev5": True,
        "rev4_id": None,
        "rev4_name": None,
        "changes_from_rev4": "New control in Rev 5. PII data quality management.",
    },
    {
        "num": 23,
        "name": "Data Governance Body",
        "control_class": "Management",
        "description": "Establish a Data Governance Body consisting of [Assignment: organization-defined roles] with [Assignment: organization-defined responsibilities].",
        "supplemental_guidance": "A data governance body can help ensure that the organization has coherent policies and the ability to balance the utility of data with security and privacy requirements. The data governance body establishes policies for the governance of personal data (or data from which personal data is derived) and non-personal data across the information life cycle. The data governance body provides recommendations on data management based on the organization's mission and business needs, and privacy requirements.",
        "related_controls": ["AT-1", "AT-2", "AT-3", "PM-24", "PT-1"],
        "baseline_privacy": True,
        "new_in_rev5": True,
        "rev4_id": None,
        "rev4_name": None,
        "changes_from_rev4": "New control in Rev 5. Establishes data governance structure.",
    },
    {
        "num": 24,
        "name": "Data Integrity Board",
        "control_class": "Management",
        "description": "Establish a Data Integrity Board to: a. Review proposals to conduct or participate in a matching program; and b. Conduct an annual review of all matching programs in which the agency has participated.",
        "supplemental_guidance": "A Data Integrity Board is required for federal agencies that conduct or participate in a matching program. The board reviews and approves matching agreements and related activities. The Computer Matching and Privacy Protection Act of 1988 requires the establishment of data integrity boards within agencies.",
        "related_controls": ["PM-22", "PM-23"],
        "baseline_privacy": True,
        "new_in_rev5": True,
        "rev4_id": None,
        "rev4_name": None,
        "changes_from_rev4": "New control in Rev 5. Computer Matching Act compliance.",
    },
    {
        "num": 25,
        "name": "Minimization of Personally Identifiable Information Used in Testing, Training, and Research",
        "control_class": "Management",
        "description": "a. Develop, implement, and update policies and procedures that address the use of personally identifiable information for internal testing, training, and research; b. Take measures to minimize the use of personally identifiable information for internal testing, training, and research purposes; and c. Where possible, use techniques to minimize the risk to privacy of using personally identifiable information for internal testing, training, and research, including de-identification and synthetic data generation.",
        "supplemental_guidance": "Organizations can minimize the risk to privacy of using personally identifiable information for internal testing, training, and research by implementing privacy-protective techniques such as de-identification, anonymization, synthetic data generation, and other methods that reduce the risk of exposing PII during such activities. The use of production data containing PII for testing purposes introduces risk that the PII could be misused, improperly accessed, or disclosed.",
        "related_controls": ["PM-23", "PT-3", "SA-3", "SA-8", "SI-12", "SI-19"],
        "baseline_privacy": True,
        "new_in_rev5": True,
        "rev4_id": None,
        "rev4_name": None,
        "changes_from_rev4": "New control in Rev 5. PII minimization in testing/training.",
    },
    {
        "num": 26,
        "name": "Complaint Management",
        "control_class": "Management",
        "description": "Implement a process for receiving and responding to complaints, concerns, or questions from individuals about the organizational security and privacy practices that includes: a. Mechanisms that are easy to use and readily accessible by the public; b. All information necessary for successfully filing complaints; c. Tracking mechanisms to ensure all complaints received are reviewed and appropriately addressed in a timely manner; d. Acknowledgement of receipt of complaints, concerns, or questions from individuals within [Assignment: organization-defined time period]; and e. Response to complaints, concerns, or questions from individuals within [Assignment: organization-defined time period].",
        "supplemental_guidance": "Complaints, concerns, and questions from individuals can serve as valuable sources of input to organizations and ultimately improve operational models, uses of technology, data collection practices, and controls. Organizational complaint management processes include tracking mechanisms to ensure that all complaints received are reviewed and appropriately addressed in a timely manner.",
        "related_controls": ["IR-7", "IR-9", "PM-22", "SI-18"],
        "baseline_privacy": True,
        "new_in_rev5": True,
        "rev4_id": None,
        "rev4_name": None,
        "changes_from_rev4": "New control in Rev 5. Individual complaint management process.",
    },
    {
        "num": 27,
        "name": "Privacy Reporting",
        "control_class": "Management",
        "description": "a. Develop [Assignment: organization-defined privacy reports] and disseminate to: 1. [Assignment: organization-defined oversight bodies] to demonstrate accountability with statutory, regulatory, and policy privacy mandates; and 2. [Assignment: organization-defined officials] and other personnel with responsibility for monitoring privacy program compliance; and b. Review and update privacy reports [Assignment: organization-defined frequency].",
        "supplemental_guidance": "Through internal and external privacy reporting, organizations promote accountability and transparency in organizational privacy operations. Privacy reporting helps organizations to determine progress in meeting privacy compliance and risk mitigation requirements, to compare performance across the federal government, to identify vulnerabilities, and to identify the resources needed to implement privacy programs.",
        "related_controls": ["IR-9", "PM-18"],
        "baseline_privacy": True,
        "new_in_rev5": True,
        "rev4_id": None,
        "rev4_name": None,
        "changes_from_rev4": "New control in Rev 5. Privacy program reporting requirements.",
    },
    {
        "num": 28,
        "name": "Risk Framing",
        "control_class": "Management",
        "description": "a. Identify and document: 1. Assumptions affecting risk assessments, risk responses, and risk monitoring; 2. Constraints affecting risk assessments, risk responses, and risk monitoring; 3. Priorities and trade-offs considered by the organization for managing risk; and 4. Organizational risk tolerance; b. Distribute the results of risk framing activities to [Assignment: organization-defined personnel]; and c. Review and update risk framing considerations [Assignment: organization-defined frequency].",
        "supplemental_guidance": "Risk framing is most effective when conducted at the organization level and in consultation with stakeholders throughout the organization including mission, business, and system owners. Risk framing results are shared with organizational personnel, including mission and business owners, information owners or stewards, system owners, authorizing officials, senior agency information security officers, senior agency officials for privacy, and chief information officers.",
        "related_controls": ["CA-7", "PM-9", "RA-3", "RA-7"],
        "baseline_privacy": True,
        "new_in_rev5": True,
        "rev4_id": None,
        "rev4_name": None,
        "changes_from_rev4": "New control in Rev 5. Risk framing activities formalized.",
    },
    {
        "num": 29,
        "name": "Risk Management Program Leadership Roles",
        "control_class": "Management",
        "description": "a. Appoint a Senior Accountable Official for Risk Management to align information security and privacy management processes with strategic, operational, and budgetary planning processes; and b. Establish a Risk Executive (function) to view and analyze risk from an organization-wide perspective and ensure management of risk is consistent across the organization.",
        "supplemental_guidance": "The senior accountable official for risk management leads the risk executive (function). The risk executive (function) coordinates with senior leadership of the organization to: provide a comprehensive, organization-wide, holistic approach for addressing risk; provide oversight of all risk management-related activities across the organization; and ensure that risk-related considerations for individual systems are viewed from an organization-wide perspective.",
        "related_controls": ["PM-2", "PM-9"],
        "baseline_privacy": False,
        "new_in_rev5": True,
        "rev4_id": None,
        "rev4_name": None,
        "changes_from_rev4": "New control in Rev 5. Risk management leadership formalized.",
    },
    {
        "num": 30,
        "name": "Supply Chain Risk Management Strategy",
        "control_class": "Management",
        "description": "a. Develop an organization-wide strategy for managing supply chain risks associated with the development, acquisition, maintenance, and disposal of systems, system components, and system services; b. Implement the supply chain risk management strategy consistently across the organization; and c. Review and update the supply chain risk management strategy on [Assignment: organization-defined frequency] or as required, to address organizational changes.",
        "supplemental_guidance": "An organization-wide supply chain risk management strategy includes an unambiguous expression of the supply chain risk appetite and tolerance for the organization, acceptable supply chain risk mitigation strategies or controls, a process for consistently evaluating and monitoring supply chain risk, and approaches for implementing and communicating the supply chain risk management strategy.",
        "related_controls": ["PM-9", "SR-1", "SR-2", "SR-3"],
        "baseline_privacy": False,
        "new_in_rev5": True,
        "rev4_id": None,
        "rev4_name": None,
        "changes_from_rev4": "New control in Rev 5. Formalizes supply chain risk management strategy.",
    },
    {
        "num": 31,
        "name": "Continuous Monitoring Strategy",
        "control_class": "Management",
        "description": "Develop an organization-wide continuous monitoring strategy and implement continuous monitoring programs that include: a. Establishing the following organization-wide metrics to be monitored: [Assignment: organization-defined metrics]; b. Establishing [Assignment: organization-defined frequencies] for monitoring and [Assignment: organization-defined frequencies] for assessment of control effectiveness; c. Ongoing monitoring of organizationally-defined metrics in accordance with the continuous monitoring strategy; d. Correlation and analysis of information generated by control assessments and monitoring; e. Response actions to address results of the analysis of control assessment and monitoring information; and f. Reporting the security and privacy status of organizational systems to [Assignment: organization-defined personnel or roles] [Assignment: organization-defined frequency].",
        "supplemental_guidance": "Continuous monitoring at the organization level facilitates ongoing awareness of the security and privacy posture across the organization to support organizational risk management decisions. The terms continuous and ongoing imply that organizations assess and monitor their controls and risks at a frequency sufficient to support risk-based decisions. Different types of controls may be assessed and monitored at different frequencies.",
        "related_controls": ["CA-7", "PM-4", "PM-9", "PM-14", "SC-43", "SI-4", "SI-12"],
        "baseline_privacy": False,
        "new_in_rev5": True,
        "rev4_id": None,
        "rev4_name": None,
        "changes_from_rev4": "New control in Rev 5. Organization-wide continuous monitoring formalized.",
    },
    {
        "num": 32,
        "name": "Purposing",
        "control_class": "Management",
        "description": "Analyze [Assignment: organization-defined systems or system components] supporting the organization's missions and business functions to determine if such systems or system components are suitable for reuse.",
        "supplemental_guidance": "This is a systems engineering process that ensures the effective and efficient use of organizational systems and reduces the risk of inheriting vulnerabilities or other weaknesses from systems or components that have been repurposed without proper review. Considerations include the original purpose of the system or component, the security and privacy implications of reuse, the age and condition of the system or component, and the availability of documentation.",
        "related_controls": ["AC-3", "AT-3", "CM-12", "CM-13", "PM-25", "PT-2", "PT-3", "SC-43", "SI-12", "SI-18"],
        "baseline_privacy": True,
        "new_in_rev5": True,
        "rev4_id": None,
        "rev4_name": None,
        "changes_from_rev4": "New control in Rev 5. System reuse analysis.",
    },
]


def format_control_id(num):
    """Format control number as PM-01, PM-02, etc."""
    return f"PM-{num:02d}"


def extract_pm_mappings_from_coverage():
    """
    Extract PM control -> framework clause mappings from all 21 coverage JSONs.

    Returns dict: { "PM-01": { "iso_27001_2022": ["4.3", "5.1", ...], ... }, ... }
    """
    pm_mappings = {}

    for fname in sorted(os.listdir(COVERAGE_DIR)):
        if not fname.endswith(".json"):
            continue

        fpath = os.path.join(COVERAGE_DIR, fname)
        with open(fpath) as f:
            data = json.load(f)

        framework_id = data.get("framework_id", "")
        if not framework_id:
            continue

        for clause in data.get("clauses", []):
            controls = clause.get("controls", [])
            clause_id = clause.get("id", "")
            if not clause_id:
                continue

            for ctrl in controls:
                # Normalize: coverage JSONs use PM-1, PM-2, etc. (no leading zero)
                match = re.match(r"^PM-(\d+)$", ctrl)
                if not match:
                    continue

                pm_num = int(match.group(1))
                pm_id = format_control_id(pm_num)

                if pm_id not in pm_mappings:
                    pm_mappings[pm_id] = {}
                if framework_id not in pm_mappings[pm_id]:
                    pm_mappings[pm_id][framework_id] = []
                if clause_id not in pm_mappings[pm_id][framework_id]:
                    pm_mappings[pm_id][framework_id].append(clause_id)

    return pm_mappings


def build_control_json(ctrl_def, compliance_mappings):
    """Build a complete control JSON object matching the existing schema."""
    ctrl_id = format_control_id(ctrl_def["num"])

    # Build compliance_mappings with all 21 keys in canonical order
    mappings = {}
    for key in FRAMEWORK_KEYS:
        mappings[key] = sorted(compliance_mappings.get(key, []))

    # Build nist_800_53 block
    rev4_block = {
        "id": ctrl_def["rev4_id"],
        "name": ctrl_def["rev4_name"],
        "withdrawn": False,
        "incorporated_into": [],
    }

    rev5_block = {
        "id": ctrl_id,
        "name": ctrl_def["name"],
        "description": ctrl_def["description"],
        "discussion": ctrl_def["supplemental_guidance"],
        "related_controls": ctrl_def["related_controls"],
        "baseline_low": False,
        "baseline_moderate": False,
        "baseline_high": False,
        "baseline_privacy": ctrl_def["baseline_privacy"],
        "new_in_rev5": ctrl_def["new_in_rev5"],
        "changes_from_rev4": ctrl_def["changes_from_rev4"],
    }

    control = {
        "$schema": "../schema/control.schema.json",
        "id": ctrl_id,
        "name": ctrl_def["name"],
        "family": "PM",
        "family_name": "Program Management",
        "control_class": ctrl_def["control_class"],
        "description": ctrl_def["description"],
        "supplemental_guidance": ctrl_def["supplemental_guidance"],
        "enhancements": "",
        "baseline_low": False,
        "baseline_moderate": False,
        "baseline_high": False,
        "nist_800_53": {
            "rev4": rev4_block,
            "rev5": rev5_block,
        },
        "iso17799": [],
        "cobit41": [],
        "pci_dss_v2": [],
        "compliance_mappings": mappings,
        "metadata": {
            "last_reviewed": str(date.today()),
            "review_notes": "Generated from NIST SP 800-53 Rev 5 with compliance mappings extracted from framework-coverage data",
            "mapping_status": "complete",
        },
    }

    return control


def update_manifest(pm_controls_data):
    """Update _manifest.json with PM control entries."""
    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    existing_ids = {c["id"] for c in manifest["controls"]}

    new_entries = []
    for ctrl_def in pm_controls_data:
        ctrl_id = format_control_id(ctrl_def["num"])
        if ctrl_id in existing_ids:
            print(f"  Skipping {ctrl_id} - already in manifest")
            continue
        new_entries.append(
            {
                "id": ctrl_id,
                "name": ctrl_def["name"],
                "family": "PM",
                "family_name": "Program Management",
                "baseline_low": False,
                "baseline_moderate": False,
                "baseline_high": False,
                "file": f"{ctrl_id}.json",
            }
        )

    if not new_entries:
        print("  No new entries to add to manifest")
        return

    # Insert PM controls in correct sorted position (after PL, before PS)
    controls = manifest["controls"]
    insert_idx = len(controls)
    for i, c in enumerate(controls):
        if c["family"] > "PM" and c["family"] != "PM":
            insert_idx = i
            break

    for entry in reversed(new_entries):
        controls.insert(insert_idx, entry)

    manifest["total_controls"] = len(controls)

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    print(f"  Added {len(new_entries)} entries, total now {manifest['total_controls']}")


def main():
    print("=" * 60)
    print("PM Control Generation Script")
    print("=" * 60)

    # Step 1: Extract compliance mappings from coverage JSONs
    print("\n[1/3] Extracting PM compliance mappings from framework-coverage JSONs...")
    pm_mappings = extract_pm_mappings_from_coverage()
    mapped_count = len(pm_mappings)
    total_clauses = sum(
        sum(len(v) for v in fw.values()) for fw in pm_mappings.values()
    )
    print(f"  Found {total_clauses} clause mappings for {mapped_count} PM controls")

    # Step 2: Generate JSON files
    print(f"\n[2/3] Generating {len(PM_CONTROLS)} PM control JSON files...")
    created = 0
    for ctrl_def in PM_CONTROLS:
        ctrl_id = format_control_id(ctrl_def["num"])
        fpath = os.path.join(CONTROLS_DIR, f"{ctrl_id}.json")

        # Get compliance mappings for this control
        ctrl_mappings = pm_mappings.get(ctrl_id, {})

        control_json = build_control_json(ctrl_def, ctrl_mappings)

        with open(fpath, "w") as f:
            json.dump(control_json, f, indent=2)
            f.write("\n")

        mapping_count = sum(len(v) for v in ctrl_mappings.values())
        frameworks_with_mappings = sum(1 for v in ctrl_mappings.values() if v)
        print(f"  {ctrl_id}: {ctrl_def['name']}"
              f" ({mapping_count} mappings across {frameworks_with_mappings} frameworks)")
        created += 1

    print(f"  Created {created} control files")

    # Step 3: Update manifest
    print("\n[3/3] Updating _manifest.json...")
    update_manifest(PM_CONTROLS)

    print("\n" + "=" * 60)
    print("Done! Generated files in:", CONTROLS_DIR)
    print("=" * 60)


if __name__ == "__main__":
    main()
