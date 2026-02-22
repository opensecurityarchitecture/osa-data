#!/usr/bin/env python3
"""
Add ANSSI compliance mappings to NIST 800-53 Rev 5 control files.

Maps three ANSSI frameworks:
  - Hygiene Guide v2 (42 measures in 9 sections) - "Hygiene.N"
  - RGS v2.0 (Référentiel Général de Sécurité) - "RGS.X.Y"
  - SecNumCloud 3.2 (cloud security qualification) - "SecNumCloud.X.Y"

ANSSI Hygiene Guide v2 - 42 measures:
  I.   Awareness & Training (1-4)
       1: Inform and raise awareness
       2: Develop an information security policy
       3: Conduct awareness sessions for users
       4: Train IT teams on security specifics

  II.  Know the Information System (5-10)
       5: Have a precise map of the IT installation
       6: Have an exhaustive inventory of privileged accounts
       7: Draft procedures for arrival/departure of users
       8: Identify the most sensitive information and servers
       9: Have an inventory of all interconnection points
       10: Define and enforce a password policy

  III. Authentication & Access Control (11-17)
       11: Use unique and personal accounts
       12: Implement adequate authentication for each account
       13: Prohibit shared/generic service accounts
       14: Grant access rights according to the need-to-know principle
       15: Limit the number of administrator accounts
       16: Use dedicated admin workstations
       17: Ensure separation of administrator and user roles

  IV.  Security of Workstations and Mobile Devices (18-22)
       18: Implement a basic security level for all workstations
       19: Encrypt data on mobile devices (laptops, USB, etc.)
       20: Control software installed on workstations
       21: Use antivirus and keep it up to date
       22: Implement a secure gateway for Internet access

  V.   Security of the Network (23-27)
       23: Segment the network and isolate sensitive systems
       24: Use encrypted protocols for remote access (VPN)
       25: Protect the internal Wi-Fi network
       26: Control access to the physical network
       27: Supervise and filter Internet access flows

  VI.  Secure System Administration (28-31)
       28: Limit remote administration to dedicated, secured networks
       29: Implement a centralised log collection and analysis system
       30: Define and apply a backup policy
       31: Conduct periodic IT security audits

  VII. Managing the IS Security Lifecycle (32-36)
       32: Define a procedure for creating and deleting user accounts
       33: Implement a vulnerability management procedure
       34: Maintain up-to-date systems and applications
       35: Define and practice an incident response plan
       36: Plan and monitor security projects

  VIII. Physical and Environmental Security (37-38)
       37: Restrict physical access to premises and server rooms
       38: Protect against environmental threats (fire, flood, power loss)

  IX.  Managing Security Incidents (39-42)
       39: Implement a security incident detection capability
       40: Define an incident response and crisis management procedure
       41: Conduct a formal risk analysis
       42: Use ANSSI-qualified products and services

RGS v2.0 sections:
  1: General provisions
  2: Crypto functions (signature, authentication, confidentiality, timestamping)
  3: Implementation rules
  4: Audit and certification

SecNumCloud 3.2 chapters:
  6: Information security policies
  7: Organisation of information security
  8: Human resource security
  9: Asset management
  10: Access control
  11: Cryptography
  12: Physical and environmental security
  13: Operations security
  14: Communications security
  15: System acquisition, development and maintenance
  16: Supplier relationships
  17: Information security incident management
  18: Business continuity management
  19: Compliance
"""

import json
import os
import sys
from collections import OrderedDict

CONTROLS_DIR = "/Users/russellwing/osa-workspace/data/controls"

# ============================================================
# ANSSI MAPPINGS per NIST 800-53 control
# ============================================================
# Each control ID maps to a list of ANSSI references.
# Format: "Hygiene.N", "RGS.X.Y", "SecNumCloud.X.Y"

ANSSI_MAPPINGS = {
    # ---- AC: Access Control ----
    "AC-01": [
        "Hygiene.2", "Hygiene.10", "Hygiene.14",
        "RGS.1.3", "SecNumCloud.6.1", "SecNumCloud.10.1"
    ],
    "AC-02": [
        "Hygiene.6", "Hygiene.7", "Hygiene.11", "Hygiene.13", "Hygiene.32",
        "SecNumCloud.10.2"
    ],
    "AC-03": [
        "Hygiene.14", "Hygiene.15", "Hygiene.17",
        "SecNumCloud.10.3"
    ],
    "AC-04": [
        "Hygiene.23", "Hygiene.27",
        "SecNumCloud.14.1"
    ],
    "AC-05": [
        "Hygiene.15", "Hygiene.17",
        "SecNumCloud.10.4"
    ],
    "AC-06": [
        "Hygiene.14", "Hygiene.15", "Hygiene.16", "Hygiene.17",
        "SecNumCloud.10.3", "SecNumCloud.10.4"
    ],
    "AC-07": [
        "Hygiene.10", "Hygiene.12",
        "SecNumCloud.10.5"
    ],
    "AC-08": [
        "Hygiene.3",
        "SecNumCloud.10.1"
    ],
    "AC-09": [
        "Hygiene.29",
        "SecNumCloud.13.7"
    ],
    "AC-10": [
        "Hygiene.12",
        "SecNumCloud.10.5"
    ],
    "AC-11": [
        "Hygiene.18",
        "SecNumCloud.10.6"
    ],
    "AC-12": [
        "Hygiene.12",
        "SecNumCloud.10.6"
    ],
    "AC-13": [
        "Hygiene.6", "Hygiene.31",
        "SecNumCloud.10.2"
    ],
    "AC-14": [
        "Hygiene.11",
        "SecNumCloud.10.1"
    ],
    "AC-15": [
        "Hygiene.8"
    ],
    "AC-16": [
        "Hygiene.8"
    ],
    "AC-17": [
        "Hygiene.24", "Hygiene.28",
        "SecNumCloud.10.7", "SecNumCloud.14.2"
    ],
    "AC-18": [
        "Hygiene.25", "Hygiene.26",
        "SecNumCloud.14.3"
    ],
    "AC-19": [
        "Hygiene.18", "Hygiene.19",
        "SecNumCloud.10.6"
    ],
    "AC-20": [
        "Hygiene.9", "Hygiene.22",
        "SecNumCloud.16.1"
    ],

    # ---- AT: Awareness and Training ----
    "AT-01": [
        "Hygiene.1", "Hygiene.2",
        "RGS.1.2", "SecNumCloud.6.1"
    ],
    "AT-02": [
        "Hygiene.1", "Hygiene.3",
        "SecNumCloud.8.3"
    ],
    "AT-03": [
        "Hygiene.4",
        "SecNumCloud.8.3"
    ],
    "AT-04": [
        "Hygiene.3", "Hygiene.4",
        "SecNumCloud.8.3"
    ],
    "AT-05": [
        "Hygiene.1", "Hygiene.4"
    ],

    # ---- AU: Audit and Accountability ----
    "AU-01": [
        "Hygiene.2", "Hygiene.29",
        "RGS.1.3", "SecNumCloud.6.1", "SecNumCloud.13.7"
    ],
    "AU-02": [
        "Hygiene.29",
        "SecNumCloud.13.7"
    ],
    "AU-03": [
        "Hygiene.29",
        "SecNumCloud.13.7"
    ],
    "AU-04": [
        "Hygiene.29",
        "SecNumCloud.13.7"
    ],
    "AU-05": [
        "Hygiene.29",
        "SecNumCloud.13.7"
    ],
    "AU-06": [
        "Hygiene.29", "Hygiene.39",
        "SecNumCloud.13.7", "SecNumCloud.17.1"
    ],
    "AU-07": [
        "Hygiene.29",
        "SecNumCloud.13.7"
    ],
    "AU-08": [
        "Hygiene.29",
        "SecNumCloud.13.7"
    ],
    "AU-09": [
        "Hygiene.29",
        "SecNumCloud.13.7"
    ],
    "AU-10": [
        "Hygiene.29",
        "RGS.2.1", "SecNumCloud.13.7"
    ],
    "AU-11": [
        "Hygiene.29",
        "SecNumCloud.13.7"
    ],

    # ---- CA: Security Assessment and Authorization ----
    "CA-01": [
        "Hygiene.2", "Hygiene.36",
        "RGS.1.3", "SecNumCloud.6.1", "SecNumCloud.19.1"
    ],
    "CA-02": [
        "Hygiene.31", "Hygiene.41",
        "RGS.4.1", "SecNumCloud.19.2"
    ],
    "CA-03": [
        "Hygiene.9",
        "SecNumCloud.14.1"
    ],
    "CA-04": [
        "Hygiene.31",
        "RGS.4.1", "SecNumCloud.19.2"
    ],
    "CA-05": [
        "Hygiene.36",
        "SecNumCloud.19.1"
    ],
    "CA-06": [
        "Hygiene.36", "Hygiene.41",
        "RGS.4.1", "SecNumCloud.19.2"
    ],
    "CA-07": [
        "Hygiene.29", "Hygiene.31", "Hygiene.39",
        "SecNumCloud.13.7", "SecNumCloud.19.2"
    ],

    # ---- CM: Configuration Management ----
    "CM-01": [
        "Hygiene.2", "Hygiene.5",
        "SecNumCloud.6.1", "SecNumCloud.13.1"
    ],
    "CM-02": [
        "Hygiene.5", "Hygiene.18",
        "SecNumCloud.13.1"
    ],
    "CM-03": [
        "Hygiene.34", "Hygiene.36",
        "SecNumCloud.13.2"
    ],
    "CM-04": [
        "Hygiene.34",
        "SecNumCloud.13.2"
    ],
    "CM-05": [
        "Hygiene.15", "Hygiene.16", "Hygiene.17", "Hygiene.34",
        "SecNumCloud.13.2"
    ],
    "CM-06": [
        "Hygiene.18", "Hygiene.20",
        "SecNumCloud.13.1"
    ],
    "CM-07": [
        "Hygiene.18", "Hygiene.20",
        "SecNumCloud.13.1"
    ],
    "CM-08": [
        "Hygiene.5", "Hygiene.8",
        "SecNumCloud.9.1"
    ],

    # ---- CP: Contingency Planning ----
    "CP-01": [
        "Hygiene.2", "Hygiene.30",
        "SecNumCloud.6.1", "SecNumCloud.18.1"
    ],
    "CP-02": [
        "Hygiene.30", "Hygiene.35",
        "SecNumCloud.18.1"
    ],
    "CP-03": [
        "Hygiene.4", "Hygiene.35",
        "SecNumCloud.18.2"
    ],
    "CP-04": [
        "Hygiene.35",
        "SecNumCloud.18.2"
    ],
    "CP-05": [
        "Hygiene.35", "Hygiene.36",
        "SecNumCloud.18.1"
    ],
    "CP-06": [
        "Hygiene.30",
        "SecNumCloud.18.3"
    ],
    "CP-07": [
        "Hygiene.30",
        "SecNumCloud.18.3"
    ],
    "CP-08": [
        "Hygiene.30",
        "SecNumCloud.18.3"
    ],
    "CP-09": [
        "Hygiene.30",
        "SecNumCloud.13.5"
    ],
    "CP-10": [
        "Hygiene.30", "Hygiene.35",
        "SecNumCloud.18.3"
    ],

    # ---- IA: Identification and Authentication ----
    "IA-01": [
        "Hygiene.2", "Hygiene.10", "Hygiene.11",
        "RGS.2.2", "SecNumCloud.6.1", "SecNumCloud.10.1"
    ],
    "IA-02": [
        "Hygiene.10", "Hygiene.11", "Hygiene.12",
        "RGS.2.2", "SecNumCloud.10.5"
    ],
    "IA-03": [
        "Hygiene.5", "Hygiene.26",
        "SecNumCloud.10.5"
    ],
    "IA-04": [
        "Hygiene.6", "Hygiene.7", "Hygiene.11", "Hygiene.32",
        "SecNumCloud.10.2"
    ],
    "IA-05": [
        "Hygiene.10", "Hygiene.12",
        "RGS.2.2", "SecNumCloud.10.5"
    ],
    "IA-06": [
        "Hygiene.10",
        "SecNumCloud.10.5"
    ],
    "IA-07": [
        "Hygiene.12",
        "RGS.2.3", "SecNumCloud.11.1"
    ],

    # ---- IR: Incident Response ----
    "IR-01": [
        "Hygiene.2", "Hygiene.35", "Hygiene.40",
        "SecNumCloud.6.1", "SecNumCloud.17.1"
    ],
    "IR-02": [
        "Hygiene.4", "Hygiene.35",
        "SecNumCloud.17.1"
    ],
    "IR-03": [
        "Hygiene.35",
        "SecNumCloud.17.2"
    ],
    "IR-04": [
        "Hygiene.35", "Hygiene.39", "Hygiene.40",
        "SecNumCloud.17.1", "SecNumCloud.17.2"
    ],
    "IR-05": [
        "Hygiene.29", "Hygiene.39",
        "SecNumCloud.17.1"
    ],
    "IR-06": [
        "Hygiene.40",
        "SecNumCloud.17.1"
    ],
    "IR-07": [
        "Hygiene.40", "Hygiene.42",
        "SecNumCloud.17.1"
    ],

    # ---- MA: Maintenance ----
    "MA-01": [
        "Hygiene.2", "Hygiene.34",
        "SecNumCloud.6.1", "SecNumCloud.13.4"
    ],
    "MA-02": [
        "Hygiene.34",
        "SecNumCloud.13.4"
    ],
    "MA-03": [
        "Hygiene.20", "Hygiene.34",
        "SecNumCloud.13.4"
    ],
    "MA-04": [
        "Hygiene.16", "Hygiene.24", "Hygiene.28", "Hygiene.34",
        "SecNumCloud.13.4"
    ],
    "MA-05": [
        "Hygiene.7", "Hygiene.15",
        "SecNumCloud.8.1"
    ],
    "MA-06": [
        "Hygiene.34",
        "SecNumCloud.13.4"
    ],

    # ---- MP: Media Protection ----
    "MP-01": [
        "Hygiene.2", "Hygiene.19",
        "SecNumCloud.6.1", "SecNumCloud.9.2"
    ],
    "MP-02": [
        "Hygiene.14", "Hygiene.19",
        "SecNumCloud.9.2"
    ],
    "MP-03": [
        "Hygiene.8",
        "SecNumCloud.9.2"
    ],
    "MP-04": [
        "Hygiene.19", "Hygiene.37",
        "SecNumCloud.9.2", "SecNumCloud.12.1"
    ],
    "MP-05": [
        "Hygiene.19",
        "SecNumCloud.9.2"
    ],
    "MP-06": [
        "Hygiene.19",
        "SecNumCloud.9.3"
    ],

    # ---- PE: Physical and Environmental Protection ----
    "PE-01": [
        "Hygiene.2", "Hygiene.37",
        "SecNumCloud.6.1", "SecNumCloud.12.1"
    ],
    "PE-02": [
        "Hygiene.37",
        "SecNumCloud.12.2"
    ],
    "PE-03": [
        "Hygiene.37",
        "SecNumCloud.12.2"
    ],
    "PE-04": [
        "Hygiene.26", "Hygiene.37",
        "SecNumCloud.12.2"
    ],
    "PE-05": [
        "Hygiene.37",
        "SecNumCloud.12.2"
    ],
    "PE-06": [
        "Hygiene.37", "Hygiene.39",
        "SecNumCloud.12.2"
    ],
    "PE-07": [
        "Hygiene.37",
        "SecNumCloud.12.2"
    ],
    "PE-08": [
        "Hygiene.37",
        "SecNumCloud.12.2"
    ],
    "PE-09": [
        "Hygiene.38",
        "SecNumCloud.12.3"
    ],
    "PE-10": [
        "Hygiene.38",
        "SecNumCloud.12.3"
    ],
    "PE-11": [
        "Hygiene.38",
        "SecNumCloud.12.3"
    ],
    "PE-12": [
        "Hygiene.38",
        "SecNumCloud.12.3"
    ],
    "PE-13": [
        "Hygiene.38",
        "SecNumCloud.12.3"
    ],
    "PE-14": [
        "Hygiene.38",
        "SecNumCloud.12.3"
    ],
    "PE-15": [
        "Hygiene.38",
        "SecNumCloud.12.3"
    ],
    "PE-16": [
        "Hygiene.37",
        "SecNumCloud.12.2"
    ],
    "PE-17": [
        "Hygiene.18", "Hygiene.37",
        "SecNumCloud.12.1"
    ],
    "PE-18": [
        "Hygiene.37", "Hygiene.38",
        "SecNumCloud.12.1"
    ],
    "PE-19": [
        "Hygiene.37",
        "SecNumCloud.12.2"
    ],

    # ---- PL: Planning ----
    "PL-01": [
        "Hygiene.2", "Hygiene.36",
        "RGS.1.3", "SecNumCloud.6.1"
    ],
    "PL-02": [
        "Hygiene.2", "Hygiene.5", "Hygiene.36",
        "SecNumCloud.6.2"
    ],
    "PL-03": [
        "Hygiene.36",
        "SecNumCloud.6.2"
    ],
    "PL-04": [
        "Hygiene.1", "Hygiene.3",
        "SecNumCloud.8.2"
    ],
    "PL-05": [
        "Hygiene.41"
    ],
    "PL-06": [
        "Hygiene.36",
        "SecNumCloud.6.2"
    ],

    # ---- PS: Personnel Security ----
    "PS-01": [
        "Hygiene.2", "Hygiene.7",
        "SecNumCloud.6.1", "SecNumCloud.8.1"
    ],
    "PS-02": [
        "Hygiene.7", "Hygiene.15",
        "SecNumCloud.8.1"
    ],
    "PS-03": [
        "Hygiene.7",
        "SecNumCloud.8.1"
    ],
    "PS-04": [
        "Hygiene.7", "Hygiene.32",
        "SecNumCloud.8.4"
    ],
    "PS-05": [
        "Hygiene.7", "Hygiene.14", "Hygiene.32",
        "SecNumCloud.8.4"
    ],
    "PS-06": [
        "Hygiene.7",
        "SecNumCloud.8.2"
    ],
    "PS-07": [
        "Hygiene.7",
        "SecNumCloud.8.1", "SecNumCloud.16.1"
    ],
    "PS-08": [
        "Hygiene.7",
        "SecNumCloud.8.4"
    ],

    # ---- PM: Program Management (not in Hygiene directly, but RGS governance) ----
    # PM family doesn't exist in this control set, but we handle it if present

    # ---- PT: PII Processing and Transparency ----
    "PT-01": [
        "Hygiene.2",
        "SecNumCloud.6.1", "SecNumCloud.19.3"
    ],
    "PT-02": [
        "SecNumCloud.19.3"
    ],
    "PT-03": [
        "Hygiene.8",
        "SecNumCloud.19.3"
    ],
    "PT-04": [
        "SecNumCloud.19.3"
    ],
    "PT-05": [
        "SecNumCloud.19.3"
    ],
    "PT-06": [
        "SecNumCloud.19.3"
    ],
    "PT-07": [
        "Hygiene.8",
        "SecNumCloud.19.3"
    ],
    "PT-08": [
        "SecNumCloud.19.3"
    ],

    # ---- RA: Risk Assessment ----
    "RA-01": [
        "Hygiene.2", "Hygiene.41",
        "RGS.1.3", "SecNumCloud.6.1"
    ],
    "RA-02": [
        "Hygiene.8", "Hygiene.41",
        "SecNumCloud.9.1"
    ],
    "RA-03": [
        "Hygiene.41",
        "RGS.3.1", "SecNumCloud.7.2"
    ],
    "RA-04": [
        "Hygiene.36", "Hygiene.41",
        "SecNumCloud.7.2"
    ],
    "RA-05": [
        "Hygiene.31", "Hygiene.33",
        "SecNumCloud.13.6"
    ],

    # ---- SA: System and Services Acquisition ----
    "SA-01": [
        "Hygiene.2", "Hygiene.36",
        "SecNumCloud.6.1", "SecNumCloud.15.1"
    ],
    "SA-02": [
        "Hygiene.36",
        "SecNumCloud.15.1"
    ],
    "SA-03": [
        "Hygiene.34", "Hygiene.36",
        "SecNumCloud.15.1"
    ],
    "SA-04": [
        "Hygiene.42",
        "SecNumCloud.15.1", "SecNumCloud.16.1"
    ],
    "SA-05": [
        "Hygiene.5",
        "SecNumCloud.15.2"
    ],
    "SA-06": [
        "Hygiene.20",
        "SecNumCloud.13.1"
    ],
    "SA-07": [
        "Hygiene.20",
        "SecNumCloud.13.1"
    ],
    "SA-08": [
        "Hygiene.23", "Hygiene.36",
        "SecNumCloud.15.3"
    ],
    "SA-09": [
        "Hygiene.9", "Hygiene.42",
        "SecNumCloud.16.1", "SecNumCloud.16.2"
    ],
    "SA-10": [
        "Hygiene.34", "Hygiene.36",
        "SecNumCloud.15.4"
    ],
    "SA-11": [
        "Hygiene.31", "Hygiene.33",
        "SecNumCloud.15.5"
    ],

    # ---- SC: System and Communications Protection ----
    "SC-01": [
        "Hygiene.2", "Hygiene.23",
        "RGS.1.3", "SecNumCloud.6.1", "SecNumCloud.14.1"
    ],
    "SC-02": [
        "Hygiene.23",
        "SecNumCloud.14.1"
    ],
    "SC-03": [
        "Hygiene.23",
        "SecNumCloud.14.1"
    ],
    "SC-04": [
        "Hygiene.19",
        "SecNumCloud.9.3"
    ],
    "SC-05": [
        "Hygiene.22", "Hygiene.27",
        "SecNumCloud.14.4"
    ],
    "SC-06": [
        "Hygiene.23",
        "SecNumCloud.13.3"
    ],
    "SC-07": [
        "Hygiene.22", "Hygiene.23", "Hygiene.27",
        "SecNumCloud.14.1", "SecNumCloud.14.4"
    ],
    "SC-08": [
        "Hygiene.24",
        "RGS.2.3", "SecNumCloud.11.1", "SecNumCloud.14.2"
    ],
    "SC-09": [
        "Hygiene.24",
        "RGS.2.3", "SecNumCloud.11.1", "SecNumCloud.14.2"
    ],
    "SC-10": [
        "Hygiene.12",
        "SecNumCloud.10.6"
    ],
    "SC-11": [
        "Hygiene.24", "Hygiene.28",
        "SecNumCloud.14.2"
    ],
    "SC-12": [
        "Hygiene.12",
        "RGS.2.3", "SecNumCloud.11.1"
    ],
    "SC-13": [
        "Hygiene.12", "Hygiene.19",
        "RGS.2.3", "SecNumCloud.11.1"
    ],
    "SC-14": [
        "Hygiene.22",
        "SecNumCloud.14.4"
    ],
    "SC-15": [
        "Hygiene.22",
        "SecNumCloud.14.1"
    ],
    "SC-16": [
        "Hygiene.24",
        "RGS.2.2", "SecNumCloud.14.2"
    ],
    "SC-17": [
        "Hygiene.12",
        "RGS.2.3", "SecNumCloud.11.1"
    ],
    "SC-18": [
        "Hygiene.20", "Hygiene.22",
        "SecNumCloud.13.1"
    ],
    "SC-19": [
        "Hygiene.24", "Hygiene.25",
        "SecNumCloud.14.2"
    ],
    "SC-20": [
        "Hygiene.23",
        "SecNumCloud.14.1"
    ],
    "SC-21": [
        "Hygiene.23",
        "SecNumCloud.14.1"
    ],
    "SC-22": [
        "Hygiene.23",
        "SecNumCloud.14.1"
    ],
    "SC-23": [
        "Hygiene.12", "Hygiene.24",
        "SecNumCloud.10.5"
    ],

    # ---- SI: System and Information Integrity ----
    "SI-01": [
        "Hygiene.2", "Hygiene.33", "Hygiene.34",
        "SecNumCloud.6.1", "SecNumCloud.13.6"
    ],
    "SI-02": [
        "Hygiene.33", "Hygiene.34",
        "SecNumCloud.13.6"
    ],
    "SI-03": [
        "Hygiene.21",
        "SecNumCloud.13.1"
    ],
    "SI-04": [
        "Hygiene.29", "Hygiene.39",
        "SecNumCloud.13.7"
    ],
    "SI-05": [
        "Hygiene.33", "Hygiene.39",
        "SecNumCloud.13.6"
    ],
    "SI-06": [
        "Hygiene.31",
        "SecNumCloud.13.6"
    ],
    "SI-07": [
        "Hygiene.20", "Hygiene.34",
        "SecNumCloud.13.6"
    ],
    "SI-08": [
        "Hygiene.21", "Hygiene.22",
        "SecNumCloud.13.1"
    ],
    "SI-09": [
        "Hygiene.14",
        "SecNumCloud.10.3"
    ],
    "SI-10": [
        "Hygiene.33",
        "SecNumCloud.15.3"
    ],
    "SI-11": [
        "Hygiene.29",
        "SecNumCloud.15.3"
    ],
    "SI-12": [
        "Hygiene.8", "Hygiene.19",
        "SecNumCloud.9.2"
    ],

    # ---- SR: Supply Chain Risk Management ----
    "SR-01": [
        "Hygiene.2", "Hygiene.36", "Hygiene.42",
        "SecNumCloud.6.1", "SecNumCloud.16.1"
    ],
    "SR-02": [
        "Hygiene.36", "Hygiene.42",
        "SecNumCloud.16.1"
    ],
    "SR-03": [
        "Hygiene.9", "Hygiene.42",
        "SecNumCloud.16.1", "SecNumCloud.16.2"
    ],
    "SR-04": [
        "Hygiene.42",
        "SecNumCloud.16.1"
    ],
    "SR-05": [
        "Hygiene.42",
        "SecNumCloud.16.1"
    ],
    "SR-06": [
        "Hygiene.31", "Hygiene.42",
        "SecNumCloud.16.2"
    ],
    "SR-07": [
        "Hygiene.42",
        "SecNumCloud.16.1"
    ],
    "SR-08": [
        "Hygiene.40", "Hygiene.42",
        "SecNumCloud.16.1"
    ],
    "SR-09": [
        "Hygiene.37", "Hygiene.42",
        "SecNumCloud.12.2", "SecNumCloud.16.1"
    ],
    "SR-10": [
        "Hygiene.31", "Hygiene.42",
        "SecNumCloud.16.2"
    ],
    "SR-11": [
        "Hygiene.42",
        "SecNumCloud.16.1"
    ],
    "SR-12": [
        "Hygiene.19",
        "SecNumCloud.9.3"
    ],
}


def load_manifest():
    """Load _manifest.json and return list of control entries."""
    manifest_path = os.path.join(CONTROLS_DIR, "_manifest.json")
    with open(manifest_path, "r") as f:
        data = json.load(f)
    return data["controls"]


def update_control_file(filepath, control_id):
    """Add 'anssi' key to compliance_mappings in a control JSON file."""
    with open(filepath, "r") as f:
        data = json.load(f, object_pairs_hook=OrderedDict)

    if "compliance_mappings" not in data:
        print(f"  WARNING: {control_id} has no compliance_mappings - skipping")
        return 0

    mappings = ANSSI_MAPPINGS.get(control_id, [])

    # Insert 'anssi' key into compliance_mappings
    # Rebuild OrderedDict with anssi in the right position (after pra_op_resilience or at end)
    cm = data["compliance_mappings"]
    new_cm = OrderedDict()
    for key, val in cm.items():
        new_cm[key] = val
    # Add anssi at end (alphabetically after pra_op_resilience, or as new last key)
    new_cm["anssi"] = mappings
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
    hygiene_refs = 0
    rgs_refs = 0
    secnumcloud_refs = 0

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

        # Count by framework
        for ref in ANSSI_MAPPINGS.get(control_id, []):
            if ref.startswith("Hygiene."):
                hygiene_refs += 1
            elif ref.startswith("RGS."):
                rgs_refs += 1
            elif ref.startswith("SecNumCloud."):
                secnumcloud_refs += 1

    print(f"\n{'='*60}")
    print(f"ANSSI Compliance Mapping Summary")
    print(f"{'='*60}")
    print(f"Total controls processed:       {len(controls)}")
    print(f"Controls with ANSSI mappings:    {controls_with_mappings}")
    print(f"Controls with empty mappings:    {controls_empty}")
    print(f"{'='*60}")
    print(f"Total ANSSI references:          {total_refs}")
    print(f"  Hygiene Guide references:      {hygiene_refs}")
    print(f"  RGS references:                {rgs_refs}")
    print(f"  SecNumCloud references:         {secnumcloud_refs}")
    print(f"{'='*60}")

    # Hygiene measure coverage
    hygiene_used = set()
    for refs in ANSSI_MAPPINGS.values():
        for ref in refs:
            if ref.startswith("Hygiene."):
                hygiene_used.add(int(ref.split(".")[1]))
    print(f"\nHygiene measures used: {sorted(hygiene_used)}")
    print(f"Hygiene coverage: {len(hygiene_used)}/42 measures")

    # List unmapped controls
    all_ids = {e["id"] for e in controls}
    mapped_ids = set(ANSSI_MAPPINGS.keys())
    unmapped = sorted(all_ids - mapped_ids)
    if unmapped:
        print(f"\nControls with empty ANSSI mappings ({len(unmapped)}):")
        for cid in unmapped:
            print(f"  {cid}")


if __name__ == "__main__":
    main()
