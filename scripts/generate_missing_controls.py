#!/usr/bin/env python3
"""
Generate missing SP 800-53 Rev 5 controls referenced by framework-coverage JSONs.

Creates 37 controls across 14 families that exist in coverage JSONs but lack
control JSON files, causing 404 links on framework pages.

Usage:
    cd ~/osa-data && python3 scripts/generate_missing_controls.py
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

FRAMEWORK_KEYS = [
    "iso_27001_2022", "iso_27002_2022", "cobit_2019", "pci_dss_v4",
    "nist_csf_2", "cis_controls_v8", "soc2_tsc", "finos_ccc",
    "iso_42001_2023", "iec_62443", "asd_e8", "nis2", "apra_cps_234",
    "mas_trm", "pra_op_resilience", "bsi_grundschutz", "anssi", "osfi_b13",
    "finma_circular", "gdpr", "dora",
]

FAMILY_NAMES = {
    "AC": "Access Control",
    "AU": "Audit and Accountability",
    "CA": "Security Assessment and Authorization",
    "CM": "Configuration Management",
    "CP": "Contingency Planning",
    "IA": "Identification and Authentication",
    "IR": "Incident Response",
    "MP": "Media Protection",
    "PE": "Physical and Environmental Protection",
    "PL": "Planning",
    "RA": "Risk Assessment",
    "SA": "System and Services Acquisition",
    "SC": "System and Communications Protection",
    "SI": "System and Information Integrity",
}

FAMILY_CLASS = {
    "AC": "Technical",
    "AU": "Technical",
    "CA": "Management",
    "CM": "Operational",
    "CP": "Operational",
    "IA": "Technical",
    "IR": "Operational",
    "MP": "Operational",
    "PE": "Operational",
    "PL": "Management",
    "RA": "Management",
    "SA": "Management",
    "SC": "Technical",
    "SI": "Operational",
}

# ---------------------------------------------------------------------------
# Control definitions from NIST SP 800-53 Rev 5
# ---------------------------------------------------------------------------

CONTROLS = [
    # ---- AC (Access Control) ----
    {
        "id": "AC-21", "name": "Information Sharing",
        "family": "AC",
        "description": "a. Enable authorized users to determine whether access authorizations assigned to a sharing partner match the information's access and use restrictions for [Assignment: organization-defined information sharing circumstances where user discretion is required]; and b. Employ [Assignment: organization-defined automated mechanisms or manual processes] to assist users in making information sharing and collaboration decisions.",
        "supplemental_guidance": "Information sharing applies to information that may be restricted in some manner based on some formal or administrative determination. Examples of such information include contract-sensitive information, classified information related to special access programs or compartments, privileged information, proprietary information, and personally identifiable information. Security and privacy risk assessments as well as applicable laws, regulations, and policies can provide useful guidance for discretionary information-sharing decisions.",
        "related_controls": ["AC-3", "AC-4", "AC-16", "AU-16", "PT-7"],
        "baseline_low": False, "baseline_moderate": True, "baseline_high": True,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "AC-21", "rev4_name": "Information Sharing",
    },
    {
        "id": "AC-22", "name": "Publicly Accessible Content",
        "family": "AC",
        "description": "a. Designate individuals authorized to make information publicly accessible; b. Train authorized individuals to ensure that publicly accessible information does not contain nonpublic information; c. Review the proposed content of information prior to posting onto the publicly accessible system to ensure that nonpublic information is not included; and d. Review the content on the publicly accessible system for nonpublic information [Assignment: organization-defined frequency] and remove such information, if discovered.",
        "supplemental_guidance": "In accordance with applicable laws, executive orders, directives, policies, regulations, standards, and guidelines, the public is not authorized to have access to nonpublic information, including information protected under the Privacy Act and proprietary information. This control addresses systems that are controlled by the organization and accessible to the public, typically without identification or authentication.",
        "related_controls": ["AC-3", "AC-4", "AT-2", "AT-3", "AU-13"],
        "baseline_low": True, "baseline_moderate": True, "baseline_high": True,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "AC-22", "rev4_name": "Publicly Accessible Content",
    },
    {
        "id": "AC-23", "name": "Data Mining Protection",
        "family": "AC",
        "description": "Employ [Assignment: organization-defined data mining prevention and detection techniques] for [Assignment: organization-defined data storage objects] to detect and protect against unauthorized data mining.",
        "supplemental_guidance": "Data storage objects include database records and database fields. Sensitive information can be extracted from data warehouses, databases, and data storage objects through data mining. Data mining prevention and detection techniques include limiting the types of responses provided to database queries, limiting the number or frequency of database queries to increase the work factor needed to determine the contents of databases, and notifying organizational personnel when atypical database queries or accesses occur.",
        "related_controls": ["PM-12", "PT-2"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "AC-23", "rev4_name": "Data Mining Protection",
    },
    {
        "id": "AC-24", "name": "Access Control Decisions",
        "family": "AC",
        "description": "Establish procedures to ensure [Assignment: organization-defined access control decisions] are applied to each access request prior to access enforcement.",
        "supplemental_guidance": "Access control decisions (also known as authorization decisions) occur when authorization information is applied to specific accesses. In contrast, access control enforcement occurs when systems enforce access control decisions. While it is common to have access control decisions and access control enforcement implemented by the same entity, it is not required, and it is not always an optimal implementation approach.",
        "related_controls": ["AC-2", "AC-3"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "AC-24", "rev4_name": "Access Control Decisions",
    },
    {
        "id": "AC-25", "name": "Reference Monitor",
        "family": "AC",
        "description": "Implement a reference monitor for [Assignment: organization-defined access control policies] that is tamperproof, always invoked, and small enough to be subject to analysis and testing, the completeness of which can be assured.",
        "supplemental_guidance": "The reference monitor concept and theory behind it can be found in Anderson, J.P., Computer Security Technology Planning Study, ESD-TR-73-51, Electronic Systems Division, Air Force Systems Command, Hanscom AFB, MA (October 1972) and in Lampson, B.W., Protection, Proceedings of the 5th Princeton Symposium on Information Sciences and Systems, Princeton University (March 1971). An abstract machine that mediates all access of subjects to objects based on an access control policy.",
        "related_controls": ["AC-3", "AC-16", "SA-8", "SA-17", "SC-3", "SC-11", "SC-39", "SI-13"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "AC-25", "rev4_name": "Reference Monitor",
    },

    # ---- AU (Audit and Accountability) ----
    {
        "id": "AU-12", "name": "Audit Record Generation",
        "family": "AU",
        "description": "a. Provide audit record generation capability for the event types the system is capable of auditing as defined in AU-2a on [Assignment: organization-defined system components]; b. Allow [Assignment: organization-defined personnel or roles] to select the event types that are to be audited by specific components of the system; and c. Generate audit records for the event types defined in AU-2c that include the audit record content defined in AU-3.",
        "supplemental_guidance": "Audit records can be generated from many different system components. The event types specified in AU-2 are the event types for which audit logs are to be generated and are a subset of all event types for which the system can generate audit records.",
        "related_controls": ["AC-6", "AC-17", "AU-2", "AU-3", "AU-4", "AU-5", "AU-6", "AU-14", "CM-5", "MA-4", "MP-4", "PM-12", "SA-8", "SC-18", "SI-3", "SI-4", "SI-7", "SI-10"],
        "baseline_low": True, "baseline_moderate": True, "baseline_high": True,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "AU-12", "rev4_name": "Audit Generation",
    },
    {
        "id": "AU-13", "name": "Monitoring for Information Disclosure",
        "family": "AU",
        "description": "Monitor [Assignment: organization-defined open-source information and/or information sites] [Assignment: organization-defined frequency] for evidence of unauthorized disclosure of organizational information.",
        "supplemental_guidance": "Unauthorized disclosure of information is a form of data leakage. Open-source information includes social networking sites, news outlets, and publicly accessible web pages. Examples of organizational information include information in press releases or information disclosed during interviews.",
        "related_controls": ["AC-22", "PE-3", "SC-7", "SC-26", "SI-4"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "AU-13", "rev4_name": "Monitoring for Information Disclosure",
    },
    {
        "id": "AU-14", "name": "Session Audit",
        "family": "AU",
        "description": "a. Provide and implement the capability for [Assignment: organization-defined users or roles] to [Selection (one or more): record; view; hear; log] the content of a user session under [Assignment: organization-defined circumstances]; and b. Develop, integrate, and use session auditing activities in consultation with legal counsel and in accordance with applicable laws, executive orders, directives, regulations, policies, standards, and guidelines.",
        "supplemental_guidance": "Session auditing activities are developed, integrated, and used in consultation with legal counsel and in accordance with applicable laws, executive orders, directives, regulations, policies, standards, and guidelines. Session auditing includes the real-time monitoring of activities in user sessions and the capture, recording, and logging of activities in user sessions.",
        "related_controls": ["AC-3", "AC-8", "AU-2", "AU-3", "AU-4", "AU-5", "AU-6", "AU-9", "AU-11"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "AU-14", "rev4_name": "Session Audit",
    },
    {
        "id": "AU-15", "name": "Alternate Audit Logging Capability",
        "family": "AU",
        "description": "Provide an alternate audit logging capability in the event of a failure in primary audit logging capability that implements [Assignment: organization-defined alternate audit logging functionality].",
        "supplemental_guidance": "Since an alternate audit logging capability may be a short-term protection measure employed until the failure in the primary audit logging capability is corrected, organizations may determine that the alternate audit logging capability need only provide a subset of the primary audit logging capability that is affected by the failure.",
        "related_controls": ["AU-5", "AU-9", "AU-11"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": True,
        "rev4_id": None, "rev4_name": None,
    },
    {
        "id": "AU-16", "name": "Cross-Organizational Audit Logging",
        "family": "AU",
        "description": "Employ [Assignment: organization-defined methods] for coordinating [Assignment: organization-defined audit information] among external organizations when audit information is transmitted across organizational boundaries.",
        "supplemental_guidance": "When organizations use systems and/or services of external organizations, the auditing capability necessitates a coordinated, cross-organization approach. Organizations coordinate with external organizations to develop methods for cross-organizational audit logging, including the events to be audited, the event-related data, and approaches for sharing audit information.",
        "related_controls": ["AU-3", "AU-6", "AU-7", "CA-3", "PT-7"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "AU-16", "rev4_name": "Cross-Organizational Auditing",
    },

    # ---- CA (Security Assessment and Authorization) ----
    {
        "id": "CA-08", "name": "Penetration Testing",
        "family": "CA",
        "description": "Conduct penetration testing [Assignment: organization-defined frequency] on [Assignment: organization-defined systems or system components].",
        "supplemental_guidance": "Penetration testing is a type of assessment that is conducted on a system or individual system components to identify vulnerabilities that could be exploited by adversaries. Penetration testing goes beyond automated vulnerability scanning and is conducted by agents and teams with demonstrable skills and experience that include technical expertise in network, operating system, and/or application level security. Penetration testing can be used to validate vulnerabilities or determine the degree of penetration resistance of systems to adversaries.",
        "related_controls": ["RA-5", "RA-10", "SA-11", "SI-2", "SI-6"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": True,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "CA-8", "rev4_name": "Penetration Testing",
    },

    # ---- CM (Configuration Management) ----
    {
        "id": "CM-09", "name": "Configuration Management Plan",
        "family": "CM",
        "description": "Develop, document, and implement a configuration management plan for the system that: a. Addresses roles, responsibilities, and configuration management processes and procedures; b. Establishes a process for identifying configuration items throughout the system development life cycle and for managing the configuration of the configuration items; c. Defines the configuration items for the system and places the configuration items under configuration management; and d. Is reviewed and approved by [Assignment: organization-defined personnel or roles].",
        "supplemental_guidance": "Configuration management activities occur throughout the system development life cycle. As such, there are developmental configuration management activities (e.g., the control of code and software libraries) and operational configuration management activities (e.g., control of installed components and how those components are configured). Configuration management plans satisfy the requirements in configuration management policies while being tailored to individual systems.",
        "related_controls": ["CM-2", "CM-3", "CM-4", "CM-5", "CM-8", "SA-10"],
        "baseline_low": False, "baseline_moderate": True, "baseline_high": True,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "CM-9", "rev4_name": "Configuration Management Plan",
    },
    {
        "id": "CM-10", "name": "Software Usage Restrictions",
        "family": "CM",
        "description": "a. Use software and associated documentation in accordance with contract agreements and copyright laws; b. Track the use of software and associated documentation protected by quantity licenses to control copying and distribution; and c. Control and document the use of peer-to-peer file sharing technology to ensure that this capability is not used for the unauthorized distribution, display, performance, or reproduction of copyrighted work.",
        "supplemental_guidance": "Software license tracking can be accomplished by manual or automated methods, depending on organizational needs. Examples of contract agreements include software license agreements and non-disclosure agreements.",
        "related_controls": ["AC-17", "AU-6", "CM-7", "CM-8", "PM-30", "SC-7"],
        "baseline_low": True, "baseline_moderate": True, "baseline_high": True,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "CM-10", "rev4_name": "Software Usage Restrictions",
    },
    {
        "id": "CM-11", "name": "User-Installed Software",
        "family": "CM",
        "description": "a. Establish [Assignment: organization-defined policies] governing the installation of software by users; b. Enforce software installation policies through [Assignment: organization-defined methods]; and c. Monitor policy compliance [Assignment: organization-defined frequency].",
        "supplemental_guidance": "If provided the necessary privileges, users can install software in organizational systems. To maintain control over the software installed, organizations identify permitted and prohibited actions regarding software installation. Permitted software installations include updates and security patches to existing software and downloading new applications from organization-approved application stores. Prohibited software installations include software with unknown or suspect pedigrees or software that organizations consider potentially malicious.",
        "related_controls": ["AC-3", "AU-6", "CM-2", "CM-3", "CM-5", "CM-6", "CM-7", "CM-8", "PL-4", "SI-4", "SI-7"],
        "baseline_low": True, "baseline_moderate": True, "baseline_high": True,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "CM-11", "rev4_name": "User-Installed Software",
    },

    # ---- CP (Contingency Planning) ----
    {
        "id": "CP-11", "name": "Alternate Communications Protocols",
        "family": "CP",
        "description": "Provide the capability to employ [Assignment: organization-defined alternative communications protocols] in support of maintaining continuity of operations.",
        "supplemental_guidance": "Contingency plans and the training associated with those plans incorporate an awareness of the existence of alternative communications protocols so that mission and business functions remain viable during the operation of alternative protocols. Alternative communications protocols include TLS.",
        "related_controls": ["CP-2", "CP-8", "CP-13"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "CP-11", "rev4_name": "Alternate Communications Protocols",
    },
    {
        "id": "CP-12", "name": "Safe Mode",
        "family": "CP",
        "description": "When [Assignment: organization-defined conditions] are detected, enter a safe mode of operation with [Assignment: organization-defined restrictions of safe mode of operation].",
        "supplemental_guidance": "For systems supporting critical missions and business functions, including military operations and weapons systems, civilian space operations, nuclear power plant operations, and air traffic control operations (and the systems that support these missions and functions), organizations may choose to identify certain conditions under which those systems revert to a predefined safe mode of operation.",
        "related_controls": ["CM-2", "SA-8", "SC-24", "SI-13", "SI-17"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "CP-12", "rev4_name": "Safe Mode",
    },
    {
        "id": "CP-13", "name": "Alternative Security Mechanisms",
        "family": "CP",
        "description": "Employ [Assignment: organization-defined alternative or supplemental security mechanisms] for satisfying [Assignment: organization-defined security functions] when the primary means of implementing the security function is unavailable or compromised.",
        "supplemental_guidance": "Use of alternative security mechanisms supports system resiliency, contingency planning, and continuity of operations. To ensure mission and business continuity, organizations can implement alternative or supplemental security mechanisms. The mechanisms may be less effective than the primary mechanisms. However, having the capability to readily employ alternative or supplemental mechanisms enhances the overall resilience of the system.",
        "related_controls": ["CP-2", "CP-11", "SI-13"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "CP-13", "rev4_name": "Alternative Security Mechanisms",
    },

    # ---- IA (Identification and Authentication) ----
    {
        "id": "IA-08", "name": "Identification and Authentication (Non-Organizational Users)",
        "family": "IA",
        "description": "Uniquely identify and authenticate non-organizational users or processes acting on behalf of non-organizational users.",
        "supplemental_guidance": "Non-organizational users include system users other than organizational users explicitly covered by IA-2. Non-organizational users are uniquely identified and authenticated for accesses other than those explicitly identified and documented in AC-14. Identification and authentication of non-organizational users accessing federal systems may be required to protect federal, proprietary, or privacy-related information.",
        "related_controls": ["AC-2", "AC-6", "AC-14", "AC-17", "AC-18", "AU-6", "IA-2", "IA-4", "IA-5", "IA-10", "IA-11", "MA-4", "RA-3", "SA-4", "SC-8"],
        "baseline_low": True, "baseline_moderate": True, "baseline_high": True,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "IA-8", "rev4_name": "Identification and Authentication (Non-Organizational Users)",
    },
    {
        "id": "IA-09", "name": "Service Identification and Authentication",
        "family": "IA",
        "description": "Uniquely identify and authenticate [Assignment: organization-defined system services and applications] before establishing communications with devices, users, or other services or applications.",
        "supplemental_guidance": "Services that may require identification and authentication include web applications using digital certificates or services or applications that query a database. Identification and authentication methods for services and applications include information from trusted third parties or use of authentication mechanisms such as tokens and digital certificates.",
        "related_controls": ["IA-3", "IA-4", "IA-5", "SC-8"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "IA-9", "rev4_name": "Service Identification and Authentication",
    },
    {
        "id": "IA-10", "name": "Adaptive Authentication",
        "family": "IA",
        "description": "Require individuals accessing the system to employ [Assignment: organization-defined supplemental authentication techniques or mechanisms] under specific [Assignment: organization-defined circumstances or situations].",
        "supplemental_guidance": "Adversaries may compromise individual authentication mechanisms employed by organizations and subsequently attempt to impersonate legitimate users. To address this threat, organizations may employ specific techniques or mechanisms and establish protocols to assess suspicious behavior. Adaptive authentication employs dynamic risk assessment to adjust authentication requirements.",
        "related_controls": ["IA-2", "IA-8"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": True,
        "rev4_id": None, "rev4_name": None,
    },
    {
        "id": "IA-11", "name": "Re-authentication",
        "family": "IA",
        "description": "Require users to re-authenticate when [Assignment: organization-defined circumstances or situations requiring re-authentication].",
        "supplemental_guidance": "In addition to the re-authentication requirements associated with device locks, organizations may require re-authentication of individuals in certain situations, including when roles, authenticators or credentials change, when security categories of systems change, when the execution of privileged functions occurs, after a fixed time period, or periodically.",
        "related_controls": ["AC-3", "AC-11", "IA-2", "IA-4", "IA-8"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": True,
        "rev4_id": None, "rev4_name": None,
    },
    {
        "id": "IA-12", "name": "Identity Proofing",
        "family": "IA",
        "description": "a. Identity proof users that require accounts for logical access to systems based on appropriate identity assurance level requirements as specified in applicable standards and guidelines; b. Resolve user identities to a unique individual; and c. Collect, validate, and verify identity evidence.",
        "supplemental_guidance": "Identity proofing is the process of collecting, validating, and verifying a claimed identity to establish that the identity belongs to a specific individual. Identity proofing is necessary to appropriately provision user accounts and to mitigate the risk of fraudulent identities accessing organizational systems.",
        "related_controls": ["AC-5", "IA-1", "IA-2", "IA-4", "IA-5", "IA-6", "IA-8"],
        "baseline_low": True, "baseline_moderate": True, "baseline_high": True,
        "baseline_privacy": False, "new_in_rev5": True,
        "rev4_id": None, "rev4_name": None,
    },

    # ---- IR (Incident Response) ----
    {
        "id": "IR-08", "name": "Incident Response Plan",
        "family": "IR",
        "description": "a. Develop an incident response plan that: 1. Provides the organization with a roadmap for implementing its incident response capability; 2. Describes the structure and organization of the incident response capability; 3. Provides a high-level approach for how the incident response capability fits into the overall organization; 4. Meets the unique requirements of the organization, which relate to mission, size, structure, and functions; 5. Defines reportable incidents; 6. Provides metrics for measuring the incident response capability within the organization; 7. Defines the resources and management support needed to effectively maintain and mature an incident response capability; 8. Addresses the sharing of incident information; 9. Is reviewed and approved by [Assignment: organization-defined personnel or roles] [Assignment: organization-defined frequency]; and 10. Explicitly designates responsibility for incident response to [Assignment: organization-defined entities, personnel, or roles]; b. Distribute copies of the incident response plan to [Assignment: organization-defined incident response personnel (identified by name and/or by role) and organizational elements]; c. Update the incident response plan to address system and organizational changes or problems encountered during plan implementation, execution, or testing; d. Communicate incident response plan changes to [Assignment: organization-defined incident response personnel (identified by name and/or by role) and organizational elements]; and e. Protect the incident response plan from unauthorized disclosure and modification.",
        "supplemental_guidance": "It is important that organizations develop and implement a coordinated approach to incident response. Organizational mission and business functions determine the structure of incident response capabilities. As part of the incident response capability, organizations consider the coordination and sharing of information with external organizations, including external service providers.",
        "related_controls": ["AC-2", "CP-2", "CP-4", "IR-4", "IR-7", "IR-9", "PE-6", "PL-2", "SA-15", "SI-12"],
        "baseline_low": True, "baseline_moderate": True, "baseline_high": True,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "IR-8", "rev4_name": "Incident Response Plan",
    },

    # ---- MP (Media Protection) ----
    {
        "id": "MP-07", "name": "Media Use",
        "family": "MP",
        "description": "a. [Selection: Restrict; Prohibit] the use of [Assignment: organization-defined types of system media] on [Assignment: organization-defined systems or system components] using [Assignment: organization-defined controls]; and b. Prohibit the use of portable storage devices in organizational systems when such devices have no identifiable owner.",
        "supplemental_guidance": "System media includes both digital and non-digital media. Digital media includes flash drives, diskettes, magnetic tapes, external and removable hard disk drives, compact discs, and digital versatile discs. Non-digital media includes paper and microfilm. Media use protections also apply to mobile devices with information storage capabilities. In contrast to MP-2, which restricts user access to media, MP-7 restricts the use of certain types of media on systems.",
        "related_controls": ["AC-19", "AC-20", "PL-4", "PM-12", "SC-34", "SC-41"],
        "baseline_low": True, "baseline_moderate": True, "baseline_high": True,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "MP-7", "rev4_name": "Media Use",
    },

    # ---- PE (Physical and Environmental Protection) ----
    {
        "id": "PE-20", "name": "Asset Monitoring and Tracking",
        "family": "PE",
        "description": "Employ [Assignment: organization-defined asset location technologies] to track and monitor the location and movement of [Assignment: organization-defined assets] within [Assignment: organization-defined controlled areas].",
        "supplemental_guidance": "Asset location technologies can help organizations ensure that critical assets—including vehicles, equipment, and system components—remain in authorized locations. Organizations consult with the Office of the General Counsel regarding the deployment and operation of asset location technologies to address potential constitutional and privacy concerns.",
        "related_controls": ["CM-8", "PE-16", "PM-8"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "PE-20", "rev4_name": "Asset Monitoring and Tracking",
    },

    # ---- PL (Planning) ----
    {
        "id": "PL-07", "name": "Concept of Operations",
        "family": "PL",
        "description": "a. Develop a Concept of Operations (CONOPS) for the system describing how the organization intends to operate the system from the perspective of information security and privacy; and b. Review and update the CONOPS [Assignment: organization-defined frequency].",
        "supplemental_guidance": "The concept of operations may be included in the security or privacy plans for the system or in other system development life cycle documents. The concept of operations is a living document that requires updating throughout the system development life cycle.",
        "related_controls": ["PL-2", "SA-2", "SI-12"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "PL-7", "rev4_name": "Security Concept of Operations",
    },
    {
        "id": "PL-08", "name": "Security and Privacy Architectures",
        "family": "PL",
        "description": "a. Develop security and privacy architectures for the system that: 1. Describe the requirements and approach to be taken for protecting the confidentiality, integrity, and availability of organizational information; 2. Describe the requirements and approach to be taken for processing personally identifiable information to minimize privacy risk to individuals; 3. Describe how the architectures are integrated into and support the enterprise architecture; and 4. Describe any assumptions about, and dependencies on, external systems and the services that those systems provide; and b. Review and update the architectures [Assignment: organization-defined frequency] to reflect changes in the enterprise architecture.",
        "supplemental_guidance": "The security and privacy architectures at the system level are consistent with the organization-wide security and privacy architectures described in PM-7, which are integral to and developed as part of the enterprise architecture. The architectures include an architectural description, the allocation of security and privacy functionality (including controls), security- and privacy-related information for external interfaces, information being exchanged across the interfaces, and the protection mechanisms associated with each interface.",
        "related_controls": ["CM-2", "CM-6", "PL-2", "PL-7", "PM-5", "PM-7", "RA-9", "SA-3", "SA-5", "SA-8", "SA-17"],
        "baseline_low": False, "baseline_moderate": True, "baseline_high": True,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "PL-8", "rev4_name": "Information Security Architecture",
    },

    # ---- RA (Risk Assessment) ----
    {
        "id": "RA-10", "name": "Threat Hunting",
        "family": "RA",
        "description": "a. Establish and maintain a cyber threat hunting capability to: 1. Search for indicators of compromise in organizational systems; and 2. Detect, track, and disrupt threats that evade existing controls; and b. Employ the threat hunting capability [Assignment: organization-defined frequency].",
        "supplemental_guidance": "Threat hunting is an active means of cyber defense in contrast to traditional protection measures, such as firewalls, intrusion detection and prevention systems, quarantining malicious code in sandboxes, and security event and incident management technologies and systems. Cyber threat hunting involves proactively searching organizational systems, networks, and infrastructure for advanced threats.",
        "related_controls": ["CA-2", "CA-7", "CA-8", "RA-3", "RA-5", "SC-36", "SI-4"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": True,
        "rev4_id": None, "rev4_name": None,
    },

    # ---- SA (System and Services Acquisition) ----
    {
        "id": "SA-15", "name": "Development Process, Standards, and Tools",
        "family": "SA",
        "description": "a. Require the developer of the system, system component, or system service to follow a documented development process that: 1. Explicitly addresses security and privacy requirements; 2. Identifies the standards and tools used in the development process; 3. Documents the specific tool options and tool configurations used in the development process; and 4. Documents, manages, and ensures the integrity of changes to the process and/or tools used in development; and b. Review the development process, standards, tools, tool options, and tool configurations [Assignment: organization-defined frequency] to determine if the process, standards, tools, tool options and tool configurations selected and employed can satisfy the following security and privacy requirements: [Assignment: organization-defined security and privacy requirements].",
        "supplemental_guidance": "Development tools include programming languages and computer-aided design systems. Reviews of development processes include the use of maturity models to determine the potential effectiveness of such processes. Maintaining the integrity of changes to tools and processes facilitates effective supply chain risk assessment and mitigation.",
        "related_controls": ["MA-6", "SA-3", "SA-4", "SA-8", "SA-10", "SA-11", "SR-9"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": True,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "SA-15", "rev4_name": "Development Process, Standards, and Tools",
    },
    {
        "id": "SA-16", "name": "Developer-Provided Training",
        "family": "SA",
        "description": "Require the developer of the system, system component, or system service to provide [Assignment: organization-defined training] on the correct use and operation of the implemented security and privacy functions, controls, and/or mechanisms.",
        "supplemental_guidance": "Developer-provided training applies to external and internal (in-house) developers. Training of personnel is essential to ensuring the effectiveness of the controls implemented within organizational systems.",
        "related_controls": ["AT-3", "AT-4", "PE-3", "SA-4", "SA-5"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "SA-16", "rev4_name": "Developer-Provided Training",
    },
    {
        "id": "SA-17", "name": "Developer Security and Privacy Architecture and Design",
        "family": "SA",
        "description": "Require the developer of the system, system component, or system service to produce a design specification and security and privacy architecture that: a. Is consistent with the organization's security and privacy architecture that is an integral part of the organization's enterprise architecture; b. Accurately and completely describes the required security and privacy functionality, and the allocation of controls among physical and logical components; and c. Expresses how individual security and privacy functions, mechanisms, and services work together to provide required security and privacy capabilities and a unified approach to protection.",
        "supplemental_guidance": "Developer security and privacy architecture and design are directed at external developers, although they could also be applied to internal (in-house) development. In contrast, PL-8 is directed at internal developers to ensure that organizations develop a security and privacy architecture that is integrated with the enterprise architecture.",
        "related_controls": ["PL-2", "PL-8", "PM-7", "SA-3", "SA-4", "SA-8", "SC-7"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": True,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "SA-17", "rev4_name": "Developer Security Architecture and Design",
    },
    {
        "id": "SA-22", "name": "Unsupported System Components",
        "family": "SA",
        "description": "a. Replace system components when support for the components is no longer available from the developer, vendor, or manufacturer; or b. Provide the following options for alternative sources for continued support for unsupported components [Selection (one or more): in-house support; [Assignment: organization-defined support from external providers]].",
        "supplemental_guidance": "Support for system components includes software patches, firmware updates, replacement parts, and maintenance contracts. An example of unsupported components includes when vendors no longer provide critical software patches or updates for their products. Unsupported components can create security vulnerabilities. Policies may be developed to eliminate the use of unsupported system components.",
        "related_controls": ["PL-2", "SA-3"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": True,
        "rev4_id": None, "rev4_name": None,
    },

    # ---- SC (System and Communications Protection) ----
    {
        "id": "SC-28", "name": "Protection of Information at Rest",
        "family": "SC",
        "description": "Protect the [Selection (one or more): confidentiality; integrity] of the following information at rest: [Assignment: organization-defined information at rest].",
        "supplemental_guidance": "Information at rest refers to the state of information when it is not in process or in transit and is located on system components. Such components include internal or external hard disk drives, storage area network devices, or databases. However, the focus of protecting information at rest is not on the type of storage device or frequency of access but rather on the state of the information. Information at rest addresses the confidentiality and integrity of information and covers user information and system information. System-related information that requires protection includes configurations or rule sets for firewalls, intrusion detection and prevention systems, filtering routers, and authentication information.",
        "related_controls": ["AC-3", "AC-4", "AC-16", "CM-3", "CM-5", "CM-6", "CP-9", "MP-4", "MP-5", "PE-3", "SC-8", "SC-12", "SC-13", "SC-34", "SI-3", "SI-7", "SI-16"],
        "baseline_low": False, "baseline_moderate": True, "baseline_high": True,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "SC-28", "rev4_name": "Protection of Information at Rest",
    },
    {
        "id": "SC-32", "name": "System Partitioning",
        "family": "SC",
        "description": "Partition the system into [Assignment: organization-defined system components] residing in separate [Selection: physical; logical] domains or environments based on [Assignment: organization-defined circumstances for physical or logical separation of components].",
        "supplemental_guidance": "System partitioning is part of a defense-in-depth protection strategy. Organizations determine the degree of physical separation of system components. Physical separation options include physically distinct components in separate racks in the same room, critical components in separate rooms, and geographical separation of critical components. Security categorization can guide the selection of candidates for domain partitioning.",
        "related_controls": ["AC-4", "AC-6", "SA-8", "SC-2", "SC-3", "SC-7", "SC-36"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "SC-32", "rev4_name": "Information System Partitioning",
    },
    {
        "id": "SC-36", "name": "Distributed Processing and Storage",
        "family": "SC",
        "description": "Distribute the following processing and storage components across multiple [Selection: physical locations; logical domains]: [Assignment: organization-defined processing and storage components].",
        "supplemental_guidance": "Distributing processing and storage across multiple physical locations or logical domains provides a degree of redundancy or overlap for an organization. The redundancy and overlap increase the work factor of adversaries to adversely impact the operations, assets, and individuals of the organization. The use of distributed processing and storage does not assume a single primary processing or storage location.",
        "related_controls": ["CP-6", "CP-7", "SC-32"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "SC-36", "rev4_name": "Distributed Processing and Storage",
    },
    {
        "id": "SC-39", "name": "Process Isolation",
        "family": "SC",
        "description": "Maintain a separate execution domain for each executing system process.",
        "supplemental_guidance": "Systems can maintain separate execution domains for each executing process by assigning each process a separate address space. Each system process has a distinct address space so that communication between processes is performed in a manner controlled through the security functions, and one process cannot modify the executing code of another process. Maintaining separate execution domains for executing processes can be achieved, for example, by implementing separate address spaces.",
        "related_controls": ["AC-3", "AC-4", "AC-6", "AC-25", "SA-8", "SC-2", "SC-3", "SI-16"],
        "baseline_low": True, "baseline_moderate": True, "baseline_high": True,
        "baseline_privacy": False, "new_in_rev5": False,
        "rev4_id": "SC-39", "rev4_name": "Process Isolation",
    },

    # ---- SI (System and Information Integrity) ----
    {
        "id": "SI-19", "name": "De-identification",
        "family": "SI",
        "description": "a. Remove the following elements of personally identifiable information from datasets: [Assignment: organization-defined elements of personally identifiable information]; and b. Evaluate [Assignment: organization-defined frequency] for effectiveness of de-identification.",
        "supplemental_guidance": "De-identification is the general term for the process of removing the association between a set of identifying data and the data subject. Many de-identification techniques are available, including but not limited to: removing identifiers, reducing the amount of detail included in data, grouping values into ranges, and adding random statistical noise. The appropriateness of the de-identification technique depends upon the context of the data and the purpose for which the data will be used.",
        "related_controls": ["MP-6", "PM-22", "PM-23", "PM-24", "PM-25", "PT-2", "PT-3", "PT-6", "PT-7", "RA-2", "SI-12"],
        "baseline_low": False, "baseline_moderate": False, "baseline_high": False,
        "baseline_privacy": True, "new_in_rev5": True,
        "rev4_id": None, "rev4_name": None,
    },
]


def extract_mappings_from_coverage():
    """Extract control -> framework clause mappings from coverage JSONs."""
    mappings = {}

    for fname in sorted(os.listdir(COVERAGE_DIR)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(COVERAGE_DIR, fname)) as f:
            data = json.load(f)

        fw_id = data.get("framework_id", "")
        if not fw_id:
            continue

        for clause in data.get("clauses", []):
            clause_id = clause.get("id", "")
            if not clause_id:
                continue
            for ctrl in clause.get("controls", []):
                # Normalize to zero-padded ID
                m = re.match(r"^([A-Z]{2})-(\d+)$", re.sub(r"\(.*\)", "", ctrl))
                if not m:
                    continue
                ctrl_id = f"{m.group(1)}-{int(m.group(2)):02d}"

                if ctrl_id not in mappings:
                    mappings[ctrl_id] = {}
                if fw_id not in mappings[ctrl_id]:
                    mappings[ctrl_id][fw_id] = []
                if clause_id not in mappings[ctrl_id][fw_id]:
                    mappings[ctrl_id][fw_id].append(clause_id)

    return mappings


def build_control_json(ctrl, compliance_mappings):
    """Build a control JSON matching existing schema."""
    family = ctrl["family"]

    cm = {}
    for key in FRAMEWORK_KEYS:
        cm[key] = sorted(compliance_mappings.get(key, []))

    rev4_block = {
        "id": ctrl.get("rev4_id"),
        "name": ctrl.get("rev4_name"),
        "withdrawn": False,
        "incorporated_into": [],
    }

    rev5_block = {
        "id": ctrl["id"],
        "name": ctrl["name"],
        "description": ctrl["description"],
        "discussion": ctrl["supplemental_guidance"],
        "related_controls": ctrl["related_controls"],
        "baseline_low": ctrl["baseline_low"],
        "baseline_moderate": ctrl["baseline_moderate"],
        "baseline_high": ctrl["baseline_high"],
        "baseline_privacy": ctrl.get("baseline_privacy", False),
        "new_in_rev5": ctrl.get("new_in_rev5", False),
        "changes_from_rev4": "New control in Rev 5." if ctrl.get("new_in_rev5") else "No significant changes from Rev 4.",
    }

    return {
        "$schema": "../schema/control.schema.json",
        "id": ctrl["id"],
        "name": ctrl["name"],
        "family": family,
        "family_name": FAMILY_NAMES[family],
        "control_class": FAMILY_CLASS[family],
        "description": ctrl["description"],
        "supplemental_guidance": ctrl["supplemental_guidance"],
        "enhancements": "",
        "baseline_low": ctrl["baseline_low"],
        "baseline_moderate": ctrl["baseline_moderate"],
        "baseline_high": ctrl["baseline_high"],
        "nist_800_53": {"rev4": rev4_block, "rev5": rev5_block},
        "iso17799": [],
        "cobit41": [],
        "pci_dss_v2": [],
        "compliance_mappings": cm,
        "metadata": {
            "last_reviewed": str(date.today()),
            "review_notes": "Generated from NIST SP 800-53 Rev 5 with compliance mappings from framework-coverage data",
            "mapping_status": "complete",
        },
    }


def update_manifest(controls_created):
    """Add new controls to manifest in correct sorted order."""
    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    existing_ids = {c["id"] for c in manifest["controls"]}
    new_entries = []

    for ctrl in controls_created:
        if ctrl["id"] in existing_ids:
            continue
        new_entries.append({
            "id": ctrl["id"],
            "name": ctrl["name"],
            "family": ctrl["family"],
            "family_name": FAMILY_NAMES[ctrl["family"]],
            "baseline_low": ctrl["baseline_low"],
            "baseline_moderate": ctrl["baseline_moderate"],
            "baseline_high": ctrl["baseline_high"],
            "file": f"{ctrl['id']}.json",
        })

    if not new_entries:
        print("  No new entries to add")
        return

    # Add all entries and re-sort the entire controls list
    manifest["controls"].extend(new_entries)
    manifest["controls"].sort(key=lambda c: (c["family"], int(c["id"].split("-")[1])))
    manifest["total_controls"] = len(manifest["controls"])

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    print(f"  Added {len(new_entries)} entries, total now {manifest['total_controls']}")


def main():
    print("=" * 60)
    print("Missing Controls Generation Script")
    print(f"Generating {len(CONTROLS)} controls across multiple families")
    print("=" * 60)

    # Step 1: Extract mappings
    print("\n[1/3] Extracting compliance mappings from coverage JSONs...")
    all_mappings = extract_mappings_from_coverage()

    # Step 2: Generate files
    print(f"\n[2/3] Generating control JSON files...")
    created = 0
    for ctrl in CONTROLS:
        ctrl_id = ctrl["id"]
        fpath = os.path.join(CONTROLS_DIR, f"{ctrl_id}.json")

        ctrl_mappings = all_mappings.get(ctrl_id, {})
        control_json = build_control_json(ctrl, ctrl_mappings)

        with open(fpath, "w") as f:
            json.dump(control_json, f, indent=2)
            f.write("\n")

        mapping_count = sum(len(v) for v in ctrl_mappings.values())
        fw_count = sum(1 for v in ctrl_mappings.values() if v)
        print(f"  {ctrl_id}: {ctrl['name']} ({mapping_count} mappings, {fw_count} frameworks)")
        created += 1

    print(f"  Created {created} files")

    # Step 3: Update manifest
    print("\n[3/3] Updating _manifest.json...")
    update_manifest(CONTROLS)

    # Verify no more broken links
    print("\n[Verify] Checking for remaining broken links...")
    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)
    valid_ids = {c["id"] for c in manifest["controls"]}

    broken = 0
    for fname in sorted(os.listdir(COVERAGE_DIR)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(COVERAGE_DIR, fname)) as f:
            data = json.load(f)
        for clause in data.get("clauses", []):
            for ctrl in clause.get("controls", []):
                base = re.sub(r"\(.*\)", "", ctrl)
                m = re.match(r"^([A-Z]{2})-(\d+)$", base)
                if not m:
                    continue
                padded = f"{m.group(1)}-{int(m.group(2)):02d}"
                if padded not in valid_ids:
                    print(f"  STILL BROKEN: {ctrl} -> {padded}")
                    broken += 1

    if broken == 0:
        print("  All framework-coverage control links now resolve!")
    else:
        print(f"  {broken} broken links remaining")

    print("\n" + "=" * 60)
    print(f"Done! {created} controls created, total now in manifest.")
    print("=" * 60)


if __name__ == "__main__":
    main()
