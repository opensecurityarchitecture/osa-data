#!/usr/bin/env python3
"""
Generate MiCA (EU Markets in Crypto-Assets Regulation) framework coverage JSON.

Regulation (EU) 2023/1114 — Markets in Crypto-Assets (MiCA)
Published in OJ L 150, 9 June 2023. Application date: 30 December 2024 (CASPs),
30 June 2024 (ARTs/EMTs).

MiCA is a broad market regulation. Security/ICT/operational requirements are concentrated in:

  Title III: Asset-referenced tokens (Art. 16-47)
    Art.34  — Governance arrangements (management body, key functions, remuneration)
    Art.35  — Risk management (operational/legal/counterparty/liquidity risk)
    Art.36  — Conflicts of interest
    Art.40  — Reserve of assets — custody and safeguarding
    Art.41  — Investments of reserve assets

  Title IV: E-money tokens (Art. 48-58)
    Art.54  — Governance of e-money token issuers
    Art.55  — Reserve of assets (EMTs)

  Title V: Crypto-asset services (Art. 59-76)
    Art.59  — Authorisation of CASPs — application and conditions
    Art.62  — Ongoing requirements for CASPs — prudential
    Art.63  — Safeguarding of clients' crypto-assets and funds
    Art.64  — Complaints-handling
    Art.65  — Conflicts of interest
    Art.66  — Outsourcing
    Art.67  — Custody/administration of crypto-assets on behalf of clients
    Art.68  — Operation of a trading platform
    Art.69  — Exchange of crypto-assets for funds or other crypto-assets
    Art.70  — Execution of orders on behalf of clients
    Art.71  — Placing of crypto-assets
    Art.72  — Reception and transmission of orders
    Art.73  — Providing advice / portfolio management
    Art.76  — Transfer services for crypto-assets

  Title VI: Prohibition of market abuse (Art. 86-92)
    Art.86  — Prohibition of insider dealing
    Art.87  — Unlawful disclosure of inside information
    Art.88  — Market manipulation prohibition
    Art.92  — Detection and prevention of market abuse by CASPs

  Title VII: Competent authorities (Art. 93-111)
    Art.94  — Powers of competent authorities (supervisory, investigatory)
    Art.97  — Professional secrecy
    Art.98  — Data protection
    Art.107 — Cooperation with ESMA/EBA
    Art.111 — EBA/ESMA guidelines

Key security-relevant recitals: 72, 73, 74, 75, 76, 77, 80, 81, 90

Reference format: "Art.{N}({P})" or "Art.{N}({P})({sub})"
where N=article, P=paragraph, sub=sub-paragraph letter.

Focus: Titles III and V (heaviest operational/security requirements).
MiCA's regulatory authorisation, market conduct, disclosure, and stablecoin
reserve management do NOT map to NIST 800-53 — gaps are acknowledged clearly.
"""

import json
import os
import sys
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "framework-coverage" / "mica.json"

# ============================================================
# MiCA clause definitions: id, title, controls, coverage_pct,
# rationale, gaps
# ============================================================
# Coverage philosophy:
#  - MiCA governance/authorisation: 15-35% (no NIST equivalent for regulatory licence)
#  - MiCA operational risk/ICT: 55-80% (partial NIST overlap)
#  - MiCA custody/safeguarding (crypto-native): 30-50% (no DLT/key mgmt equivalents)
#  - MiCA complaints/conflicts: 20-40% (procedural/legal, not security controls)
#  - MiCA market abuse detection: 50-70% (monitoring controls apply partially)
#  - MiCA outsourcing: 55-75% (good SR/SA overlap)

CLAUSES = [

    # ──────────────────────────────────────────────────────────────────────────
    # TITLE III — ASSET-REFERENCED TOKENS (ARTs)
    # ──────────────────────────────────────────────────────────────────────────

    {
        "id": "Art.34(1)",
        "title": "ART governance arrangements — management body requirements",
        "controls": ["PL-01", "PM-01", "PM-02", "PS-02", "PS-08", "PS-09"],
        "coverage_pct": 30,
        "rationale": (
            "PL-01 and PM-01/02 address policy planning and senior security roles. "
            "PS-02, PS-08, PS-09 address position descriptions, rules of behaviour, and personnel "
            "screening — providing partial governance scaffolding. "
            "Together these create an organisational security governance baseline. "
            "However, MiCA Art.34(1) specifies fit-and-proper requirements for management body "
            "members, governance structures for ART issuers, and remuneration policies — concepts "
            "that are regulatory in nature and not addressed by SP 800-53."
        ),
        "gaps": (
            "MiCA requires ART issuers to have a management body whose members meet fit-and-proper "
            "criteria under CRD IV, with clear responsibility allocation, remuneration policies, and "
            "governance documents reviewable by the competent authority. SP 800-53 addresses "
            "organisational policy and senior security roles but contains no equivalent to regulatory "
            "fit-and-proper, board composition, or remuneration governance requirements. "
            "The authorisation and supervision dimensions are outside NIST scope."
        ),
    },

    {
        "id": "Art.34(5)",
        "title": "ART governance arrangements — internal controls and risk management",
        "controls": [
            "CA-01", "CA-02", "CA-07", "PL-02", "PM-09",
            "RA-01", "RA-03", "RA-07", "SA-02", "SI-01",
        ],
        "coverage_pct": 68,
        "rationale": (
            "CA-01/02/07 provide security assessment, authorisation, and continuous monitoring. "
            "PL-02 and SA-02 address system security planning and security resource allocation. "
            "PM-09 risk management strategy establishes the enterprise risk framework. "
            "RA-01, RA-03, and RA-07 provide risk assessment policy, risk assessment process, "
            "and explicit risk response documentation. "
            "SI-01 system and information integrity policy rounds out internal control requirements. "
            "These collectively address the operational risk management framework Art.34(5) requires."
        ),
        "gaps": (
            "MiCA Art.34(5) requires internal control mechanisms including risk management procedures "
            "addressing operational, legal, counterparty, and liquidity risks specific to ART issuance. "
            "SP 800-53 addresses operational/ICT risk well but does not cover legal risk, "
            "counterparty exposure, or reserve asset liquidity risk — which are financial regulatory "
            "concepts specific to stablecoin operations. The ESG and liquidity risk dimensions "
            "are outside NIST scope."
        ),
    },

    {
        "id": "Art.35(1)",
        "title": "ART risk management — identifying and managing risks",
        "controls": [
            "PM-09", "RA-01", "RA-02", "RA-03", "RA-05",
            "RA-07", "RA-09", "SA-02", "SI-05",
        ],
        "coverage_pct": 65,
        "rationale": (
            "PM-09 risk management strategy provides the enterprise risk framework. "
            "RA-01 through RA-09 provide comprehensive risk assessment policy, categorisation, "
            "process, vulnerability scanning, risk response, and criticality analysis. "
            "SI-05 security alerts and advisories support ongoing threat awareness. "
            "SA-02 ensures security is integrated into resource planning. "
            "These controls address the ICT and operational risk dimensions of Art.35(1) well."
        ),
        "gaps": (
            "MiCA Art.35(1) requires ART issuers to identify and manage risks including liquidity "
            "risk, market risk, and operational risk arising from the reserve management function. "
            "SP 800-53 addresses information system and operational risks thoroughly but does not "
            "cover financial risk categories (liquidity, market, counterparty) that arise from "
            "reserve asset portfolios. These are prudential risk categories requiring financial "
            "regulation frameworks, not SP 800-53."
        ),
    },

    {
        "id": "Art.36(1)",
        "title": "ART conflicts of interest — policies and procedures",
        "controls": ["AC-05", "AC-06", "PM-01", "PS-06", "PS-08"],
        "coverage_pct": 30,
        "rationale": (
            "AC-05 separation of duties and AC-06 least privilege provide technical control "
            "mechanisms that partially address conflicts of interest by limiting access and "
            "authority to individuals with overlapping roles. "
            "PM-01 security programme management and PS-06 agreements/PS-08 rules of behaviour "
            "create the organisational framework for behavioural policies. "
            "These provide a baseline but fall well short of MiCA's requirements."
        ),
        "gaps": (
            "MiCA Art.36 requires ART issuers to maintain, implement, and update conflicts of "
            "interest policies identifying circumstances that could harm clients or token holders, "
            "with requirements for organisational separation, disclosure, and register maintenance. "
            "SP 800-53 separation of duties and least privilege are technical access controls, "
            "not business conduct frameworks. The regulatory disclosure, register, and client "
            "protection dimensions of MiCA conflicts provisions are outside NIST scope."
        ),
    },

    {
        "id": "Art.40(1)",
        "title": "ART reserve of assets — custody and safeguarding",
        "controls": [
            "AC-03", "AC-06", "CM-08", "IA-02", "IA-05",
            "MP-02", "MP-04", "SC-12", "SC-13", "SC-28",
        ],
        "coverage_pct": 45,
        "rationale": (
            "AC-03/06 access enforcement and least privilege apply to reserve management systems. "
            "CM-08 component inventory supports custody asset tracking. "
            "IA-02/05 identification, authentication, and authenticator management protect "
            "access to custody systems. "
            "SC-12/13 and SC-28 provide cryptographic key establishment, cryptographic protection, "
            "and protection of information at rest — relevant to private key management for "
            "reserve custodians. MP-02/04 media access and storage address physical media controls."
        ),
        "gaps": (
            "MiCA Art.40 requires ART reserve assets to be held by an authorised custodian "
            "under specific legal segregation, ring-fencing, and insolvency-remote arrangements. "
            "The requirements cover prudential custody (legal title, client asset segregation, "
            "insolvency protection) and crypto-native custody (secure key management, "
            "cold/hot wallet segregation, DLT-specific safeguards) that SP 800-53 does not address. "
            "There are no NIST controls covering regulatory asset custody, legal segregation of "
            "client assets, or the specific technical requirements of DLT-based reserve management."
        ),
    },

    {
        "id": "Art.41(1)",
        "title": "ART reserve assets — investment policy and risk",
        "controls": ["PM-09", "RA-03", "SA-02"],
        "coverage_pct": 15,
        "rationale": (
            "PM-09 risk management strategy and RA-03 risk assessment provide minimal partial "
            "coverage of the risk management dimension. SA-02 security resource planning is "
            "only tangentially relevant to investment governance. "
            "SP 800-53 does not address investment policy or financial asset management."
        ),
        "gaps": (
            "MiCA Art.41 requires reserve assets to be invested only in highly liquid financial "
            "instruments with minimal market, credit, and concentration risk. This is a prudential "
            "investment regulation requirement — ESMA/EBA will issue regulatory technical standards "
            "for eligible asset categories. SP 800-53 has no controls addressing investment policy, "
            "asset quality, diversification, or financial risk limits. This article is entirely "
            "outside the NIST 800-53 scope."
        ),
    },

    {
        "id": "Art.43(1)",
        "title": "ART — independent audit of reserve",
        "controls": ["CA-02", "CA-07", "AU-01", "PM-01"],
        "coverage_pct": 28,
        "rationale": (
            "CA-02 security assessments and CA-07 continuous monitoring provide partial analogy "
            "to independent review. AU-01 audit policy and PM-01 programme management establish "
            "oversight structures. However, MiCA specifies an independent external auditor, "
            "not an internal security assessment process."
        ),
        "gaps": (
            "MiCA Art.43 requires ART issuers to commission an independent audit of the reserve "
            "at least every six months, with results disclosed. This is a financial audit "
            "requirement (reserve composition, custody arrangements, investment quality) performed "
            "by qualified external auditors. SP 800-53 security assessments are IT/operational, "
            "not financial audit mechanisms. The reserve audit, disclosure, and regulatory "
            "filing dimensions are outside NIST scope."
        ),
    },

    # ──────────────────────────────────────────────────────────────────────────
    # TITLE IV — E-MONEY TOKENS (EMTs)
    # ──────────────────────────────────────────────────────────────────────────

    {
        "id": "Art.54(1)",
        "title": "EMT governance — management body and internal controls",
        "controls": [
            "CA-01", "PM-01", "PM-02", "PM-09",
            "PS-02", "PS-09", "RA-01", "SA-02",
        ],
        "coverage_pct": 32,
        "rationale": (
            "PM-01/02 and CA-01 establish programme management and security planning. "
            "PM-09 risk management strategy provides the enterprise risk framework. "
            "PS-02/09 address position designations and security responsibilities. "
            "RA-01 and SA-02 provide risk assessment policy and security resourcing. "
            "These controls address ICT governance dimensions but not the regulatory governance "
            "requirements of EMT issuers (who must be authorised credit institutions or e-money "
            "institutions)."
        ),
        "gaps": (
            "MiCA Art.54 applies governance requirements from the Electronic Money Directive "
            "(2009/110/EC) to EMT issuers, including board composition, fit-and-proper criteria, "
            "remuneration policies, and regulatory authorisation as an e-money institution. "
            "SP 800-53 addresses ICT governance but not the regulatory licensing requirements "
            "or the EMD2 governance framework. The authorisation and sectoral fit-and-proper "
            "obligations are entirely outside NIST scope."
        ),
    },

    {
        "id": "Art.55(1)",
        "title": "EMT reserve of assets — custody and safeguarding",
        "controls": [
            "AC-03", "AC-06", "IA-02", "IA-05",
            "SC-12", "SC-13", "SC-28", "MP-02", "MP-04",
        ],
        "coverage_pct": 40,
        "rationale": (
            "AC-03/06, IA-02/05 provide access control and authentication for reserve management "
            "systems. SC-12/13 and SC-28 address cryptographic protection and data at rest — "
            "relevant to private key management. MP-02/04 address physical media handling. "
            "These controls address ICT protection aspects of reserve system operation but "
            "do not cover the legal custody and segregation requirements."
        ),
        "gaps": (
            "MiCA Art.55 requires EMT reserve assets to be held by authorised custodians under "
            "legal segregation equivalent to the Electronic Money Directive framework — ring-fenced, "
            "insolvency-remote, and invested only in secure low-risk assets. These requirements "
            "are prudential/legal custody rules outside SP 800-53 scope. "
            "Crypto-specific key management requirements for EMT reserve custody (cold storage, "
            "multi-sig, HSM requirements) are not addressed by NIST 800-53 controls."
        ),
    },

    # ──────────────────────────────────────────────────────────────────────────
    # TITLE V — CRYPTO-ASSET SERVICES (CASPs)
    # ──────────────────────────────────────────────────────────────────────────

    {
        "id": "Art.59(1)",
        "title": "CASP authorisation — application and conditions",
        "controls": ["PM-01", "PM-02", "PM-09", "PL-01", "CA-06"],
        "coverage_pct": 22,
        "rationale": (
            "PM-01 programme management, PM-02 senior officer, PM-09 risk strategy, "
            "PL-01 planning, and CA-06 authorisation provide the closest NIST analogues "
            "to organisational security governance. These controls establish that an "
            "organisation has security plans, management commitment, and authorised systems."
        ),
        "gaps": (
            "MiCA Art.59 requires CASPs to obtain regulatory authorisation from their national "
            "competent authority before providing services — a licensing requirement that involves "
            "submission of detailed governance documentation, business plans, shareholder structures, "
            "and management body information for regulatory approval. SP 800-53 has no concept "
            "equivalent to regulatory licensing or market authorisation. The CASP authorisation "
            "process is fundamentally a regulatory/legal process outside NIST scope."
        ),
    },

    {
        "id": "Art.62(1)",
        "title": "CASP ongoing requirements — prudential and ICT requirements",
        "controls": [
            "CA-01", "CA-07", "CM-01", "CM-06",
            "PM-09", "RA-01", "RA-03", "RA-07",
            "SA-01", "SA-02", "SI-01",
        ],
        "coverage_pct": 65,
        "rationale": (
            "CA-01/07 provide security policy and continuous monitoring. "
            "CM-01/06 address configuration management policy and settings. "
            "PM-09 and SA-02 establish risk management strategy and security resource allocation. "
            "RA-01/03/07 provide risk assessment policy, assessment, and risk response. "
            "SA-01 and SI-01 address systems acquisition and integrity policies. "
            "Together these address the ICT resilience and operational risk dimensions "
            "of Art.62(1) ongoing requirements for CASPs."
        ),
        "gaps": (
            "MiCA Art.62(1) requires CASPs to act honestly, fairly, and professionally in "
            "clients' best interests, with adequate ICT systems, processes, and controls — "
            "including prudential own funds requirements and professional indemnity insurance. "
            "SP 800-53 covers ICT systems and operational controls well but does not address "
            "the conduct requirements (best interest duty, fair dealing), prudential capital "
            "requirements, or insurance obligations that MiCA imposes on CASPs."
        ),
    },

    {
        "id": "Art.63(1)",
        "title": "CASP safeguarding — clients' crypto-assets and funds",
        "controls": [
            "AC-03", "AC-04", "AC-06", "IA-02", "IA-05",
            "SC-12", "SC-13", "SC-17", "SC-28", "MP-02", "MP-04",
        ],
        "coverage_pct": 48,
        "rationale": (
            "AC-03/04/06 provide access enforcement, flow enforcement, and least privilege "
            "for custody systems. IA-02/05 address authentication and authenticator management "
            "for access to client asset systems. "
            "SC-12/13 and SC-28 address cryptographic key management, cryptographic protection, "
            "and protection of data (including crypto keys) at rest — central to DLT asset custody. "
            "SC-17 handles PKI certificates relevant to client wallet operations. "
            "MP-02/04 address physical media controls for offline/cold wallet storage."
        ),
        "gaps": (
            "MiCA Art.63 requires CASPs holding client crypto-assets to maintain legal segregation, "
            "ensure assets appear in a register updated daily, use strong and secure crypto-specific "
            "custody techniques (cold storage, multi-signature schemes, HSMs), and keep client funds "
            "in separate bank accounts. These are DLT-native custody requirements — key management, "
            "cryptographic signing schemes, wallet architecture — that SP 800-53 does not address "
            "specifically. The legal segregation, insolvency protection, and daily reconciliation "
            "requirements are regulatory obligations outside NIST scope. EBA will issue RTS on "
            "custody security."
        ),
    },

    {
        "id": "Art.63(2)",
        "title": "CASP safeguarding — segregation and record-keeping",
        "controls": [
            "AC-05", "AU-01", "AU-09", "AU-11", "AU-12",
            "CM-08", "IA-04", "PM-01",
        ],
        "coverage_pct": 50,
        "rationale": (
            "AC-05 separation of duties provides technical separation between client asset "
            "and operational system functions. "
            "AU-01, AU-09, AU-11, AU-12 address audit policy, audit record protection, "
            "audit retention, and audit generation — directly applicable to the asset "
            "register and daily reconciliation requirements. "
            "CM-08 component inventory and IA-04 identifier management support registry "
            "and account tracking. PM-01 programme management provides oversight framework."
        ),
        "gaps": (
            "MiCA Art.63(2) requires CASPs to maintain a register of positions opened in the "
            "name of each client, segregated from CASP own assets, updated at least daily, "
            "reconciled against blockchain records, and auditable by the competent authority. "
            "SP 800-53 audit and accountability controls address log integrity and retention but "
            "do not address the specific requirements of DLT asset register maintenance, "
            "on-chain reconciliation, or regulatory access to position registers. "
            "The legal segregation and regulatory filing dimensions are outside NIST scope."
        ),
    },

    {
        "id": "Art.64(1)",
        "title": "CASP complaints-handling — procedures and records",
        "controls": ["IR-01", "IR-04", "IR-07", "IR-08", "PM-01"],
        "coverage_pct": 38,
        "rationale": (
            "IR-01 incident response policy, IR-04 incident handling, IR-07 incident response "
            "assistance, and IR-08 incident response plan provide the closest NIST controls to "
            "complaints-handling — establishing structured processes for receiving, tracking, "
            "and responding to reported issues. PM-01 programme management provides oversight. "
            "These overlap with complaints-handling in structure but not regulatory purpose."
        ),
        "gaps": (
            "MiCA Art.64 requires CASPs to establish complaints-handling procedures enabling "
            "clients to file complaints free of charge, receive responses within specified "
            "timescales, and have complaints investigated and resolved with reasons provided. "
            "SP 800-53 incident response is focused on security incidents, not client complaints. "
            "The regulatory consumer protection obligations — complaint register, response "
            "timelines, ADR access, regulatory reporting of complaints — are outside NIST scope."
        ),
    },

    {
        "id": "Art.65(1)",
        "title": "CASP conflicts of interest — identification and management",
        "controls": ["AC-05", "AC-06", "PM-01", "PS-06", "PS-08"],
        "coverage_pct": 28,
        "rationale": (
            "AC-05 separation of duties and AC-06 least privilege provide technical separation "
            "mechanisms that partially address conflicts by restricting authority overlap. "
            "PM-01, PS-06, PS-08 establish programme management, personnel agreements, and "
            "rules of behaviour that underpin conduct policies. "
            "These provide limited coverage of the business conduct aspects of Art.65."
        ),
        "gaps": (
            "MiCA Art.65 requires CASPs to identify, prevent, manage, and disclose conflicts "
            "of interest — including conflicts between the CASP, its shareholders, managers, "
            "employees, and clients — with a register maintained and policies reviewed annually. "
            "SP 800-53 provides IT access separation but not business conduct frameworks. "
            "The client disclosure, regulatory register, and financial conflict identification "
            "dimensions are entirely outside NIST scope."
        ),
    },

    {
        "id": "Art.66(1)",
        "title": "CASP outsourcing — conditions and ongoing oversight",
        "controls": [
            "CA-03", "PM-09", "RA-03", "SA-04", "SA-09",
            "SR-01", "SR-02", "SR-03", "SR-05", "SR-06",
        ],
        "coverage_pct": 68,
        "rationale": (
            "CA-03 system interconnection agreements establish third-party system connections. "
            "SA-04/09 address acquisition and external information system requirements. "
            "SR-01 through SR-06 provide supply chain risk management policy, strategy, "
            "third-party provider controls, provenance, acquisition strategies, and assessments — "
            "directly applicable to CASP outsourcing risk management. "
            "PM-09 and RA-03 provide the risk management framework for outsourcing decisions."
        ),
        "gaps": (
            "MiCA Art.66 permits CASPs to outsource operational functions subject to conditions: "
            "competent authority notification, contractual service descriptions, audit rights, "
            "CASP retention of full regulatory responsibility, and prohibition on outsourcing "
            "that materially impairs service quality or regulatory compliance. "
            "SP 800-53 supply chain controls cover vetting and assessment well but do not "
            "address regulatory notification requirements, MiCA-specific contractual mandatory "
            "clauses, or the rule that regulatory accountability cannot be outsourced. "
            "ESMA will issue RTS on outsourcing standards."
        ),
    },

    {
        "id": "Art.66(3)",
        "title": "CASP outsourcing — contractual provisions and audit rights",
        "controls": [
            "CA-03", "SA-04", "SA-09", "SR-04", "SR-05", "SR-06", "SR-11",
        ],
        "coverage_pct": 60,
        "rationale": (
            "SA-04 acquisition process requirements and SA-09 external service requirements "
            "establish contractual security requirements. "
            "SR-04/05/11 address supply chain provenance, acquisition strategies, and "
            "component authenticity — applicable to service provider contractual controls. "
            "SR-06 supplier assessments and reviews enable ongoing monitoring of outsourced services. "
            "CA-03 system interconnection agreements formalise third-party integration requirements."
        ),
        "gaps": (
            "MiCA Art.66(3) requires outsourcing contracts to include: full service descriptions, "
            "data access and audit rights for the CASP and competent authorities, requirements for "
            "sub-outsourcing approval, data location, business continuity provisions, and termination "
            "with transition support. SP 800-53 supply chain controls cover the technical and "
            "operational aspects but do not mandate the specific contractual structures MiCA "
            "requires, nor do they address the regulatory right of competent authorities to audit "
            "service providers directly."
        ),
    },

    {
        "id": "Art.67(1)",
        "title": "Custody and administration of crypto-assets — specific service requirements",
        "controls": [
            "AC-02", "AC-03", "AC-06", "AU-11", "AU-12",
            "IA-02", "IA-05", "SC-12", "SC-13", "SC-17", "SC-28",
        ],
        "coverage_pct": 50,
        "rationale": (
            "AC-02/03/06 provide account management, access enforcement, and least privilege "
            "for custody administration systems. "
            "AU-11/12 address audit record retention and audit generation — supporting "
            "the transaction and position audit trail requirements. "
            "IA-02/05 address authentication and authenticator management for custody systems. "
            "SC-12/13/17/28 provide cryptographic key management, cryptographic protection, "
            "PKI, and data-at-rest protection — core to DLT asset custody operations."
        ),
        "gaps": (
            "MiCA Art.67 requires CASPs providing custody/administration services to maintain "
            "a register of client positions updated daily, implement DLT-specific security "
            "measures (private key management, cold storage, multi-signature), carry liability "
            "for loss of client assets, and provide a policy document to clients before service. "
            "SP 800-53 provides strong generic cryptographic and access controls but does not "
            "address DLT-native custody architecture, private key lifecycle management, wallet "
            "security standards, or the strict liability and pre-contractual disclosure "
            "requirements of Art.67."
        ),
    },

    {
        "id": "Art.68(1)",
        "title": "Operation of a trading platform for crypto-assets — rules and systems",
        "controls": [
            "AC-04", "AU-02", "AU-03", "AU-12", "CM-07",
            "SA-08", "SC-05", "SC-07", "SI-04", "SI-10",
        ],
        "coverage_pct": 55,
        "rationale": (
            "AC-04 information flow enforcement and SC-07 boundary protection address network "
            "segmentation for trading infrastructure. "
            "AU-02/03/12 address audit event selection, content, and generation — applicable "
            "to trade surveillance and order audit trails. "
            "CM-07 and SA-08 address functionality restrictions and security engineering "
            "principles for platform systems. "
            "SC-05 denial-of-service protection addresses trading platform availability. "
            "SI-04 system monitoring and SI-10 input validation support anomaly detection "
            "and order integrity checking."
        ),
        "gaps": (
            "MiCA Art.68 requires trading platform operators to establish non-discretionary "
            "rules for matching orders, ensure fair and orderly trading, publish real-time "
            "and end-of-day price transparency, maintain trading halt mechanisms, and implement "
            "market surveillance systems. These are market microstructure and trading regulation "
            "requirements. SP 800-53 monitoring and integrity controls provide partial overlap "
            "with trade surveillance but do not address market fairness, price transparency, "
            "trading halt obligations, or market integrity frameworks specific to financial markets."
        ),
    },

    {
        "id": "Art.68(5)",
        "title": "Trading platform — system resilience and business continuity",
        "controls": [
            "CP-01", "CP-02", "CP-04", "CP-06", "CP-07",
            "CP-09", "CP-10", "SA-08", "SC-05", "SI-13",
        ],
        "coverage_pct": 72,
        "rationale": (
            "CP-01/02 address contingency policy and business continuity planning. "
            "CP-04 contingency plan testing, CP-06/07 alternate storage/processing sites, "
            "and CP-09/10 backup and system recovery address the resilience requirements. "
            "SA-08 security engineering principles and SC-05 DoS protection address "
            "system design resilience. SI-13 predictive maintenance supports availability. "
            "These controls comprehensively address the operational resilience requirements "
            "of trading platform systems under Art.68(5)."
        ),
        "gaps": (
            "MiCA Art.68(5) requires trading platforms to have business continuity arrangements "
            "and an ICT continuity policy ensuring continuity of critical services if systems "
            "fail, with ability to resume trading within set timeframes. SP 800-53 contingency "
            "planning and business continuity controls address this well. Remaining gaps: "
            "MiCA's specific RTO requirements for trading resumption and the ESMA RTS on "
            "trading platform resilience will impose sector-specific standards beyond SP 800-53."
        ),
    },

    {
        "id": "Art.69(1)",
        "title": "Exchange services — policies for determining crypto-asset prices",
        "controls": ["AU-02", "AU-12", "SA-08", "SI-10"],
        "coverage_pct": 28,
        "rationale": (
            "AU-02/12 audit event and generation requirements provide partial coverage of "
            "transparency and auditability. SA-08 security engineering and SI-10 input validation "
            "address system integrity. However, these do not address market conduct or price "
            "determination policy requirements."
        ),
        "gaps": (
            "MiCA Art.69 requires CASPs exchanging crypto-assets for funds to establish, "
            "implement, and maintain a price determination policy to ensure prices reflect "
            "market conditions and are transparent to clients. This is a market conduct and "
            "consumer protection requirement entirely outside SP 800-53 scope. "
            "Price transparency, fairness, and market reference requirements are financial "
            "regulation obligations with no NIST equivalent."
        ),
    },

    {
        "id": "Art.70(1)",
        "title": "Execution of orders — best execution and order handling",
        "controls": ["AU-02", "AU-12", "SA-08"],
        "coverage_pct": 18,
        "rationale": (
            "AU-02/12 provide minimal coverage through audit trail requirements applicable to "
            "order records. SA-08 security engineering principles apply to order management "
            "system design. Coverage is very limited as MiCA Art.70 is primarily a market "
            "conduct requirement."
        ),
        "gaps": (
            "MiCA Art.70 requires CASPs executing orders to take sufficient steps to obtain "
            "the best possible result for clients — best execution in price, cost, speed, "
            "and likelihood of execution — with documented policies and annual review. "
            "This is a market conduct obligation (analogous to MiFID II best execution) "
            "with no equivalent in SP 800-53. Order audit trails are partially addressed "
            "by AU controls but the conduct, fiduciary, and client outcome dimensions are "
            "entirely outside NIST scope."
        ),
    },

    {
        "id": "Art.72(1)",
        "title": "Reception and transmission of orders — client order handling",
        "controls": ["AU-02", "AU-12", "IA-02", "SA-08"],
        "coverage_pct": 22,
        "rationale": (
            "IA-02 authentication of users placing orders provides minimal relevant coverage. "
            "AU-02/12 provide audit trail requirements for order records. "
            "SA-08 security engineering principles apply to order routing system design. "
            "MiCA Art.72 is primarily a market conduct and client protection requirement."
        ),
        "gaps": (
            "MiCA Art.72 requires CASPs receiving and transmitting client orders to act in "
            "clients' best interests, have procedures to promptly and fairly transmit orders, "
            "not receive inducements, and maintain records of orders for five years. "
            "SP 800-53 audit retention (AU-11) partially addresses five-year record-keeping. "
            "The conduct obligations, prohibition on inducements, and order routing fairness "
            "requirements are regulatory conduct obligations outside NIST scope."
        ),
    },

    {
        "id": "Art.73(1)",
        "title": "Providing advice and portfolio management — suitability",
        "controls": ["PM-01", "PS-06"],
        "coverage_pct": 10,
        "rationale": (
            "PM-01 programme management and PS-06 personnel agreements provide very minimal "
            "coverage of the organisational governance around advisory services. "
            "SP 800-53 has no controls relevant to suitability assessment or investment advice."
        ),
        "gaps": (
            "MiCA Art.73 requires CASPs providing advice or portfolio management to obtain "
            "information about clients' knowledge, experience, financial situation, and objectives "
            "to assess suitability before making recommendations or taking investment decisions. "
            "This is a conduct-of-business and client protection obligation (analogous to MiFID II "
            "suitability) with no equivalent in SP 800-53. Client profiling, suitability assessment, "
            "and advice documentation are regulatory obligations entirely outside NIST scope."
        ),
    },

    {
        "id": "Art.76(1)",
        "title": "Transfer services — handling crypto-asset transfers",
        "controls": [
            "AC-04", "IA-02", "IA-05", "SC-08", "SC-12", "SC-13", "SI-10",
        ],
        "coverage_pct": 55,
        "rationale": (
            "AC-04 information flow enforcement addresses control over transfer routing. "
            "IA-02/05 address authentication for transfer authorisation. "
            "SC-08 transmission confidentiality/integrity and SC-12/13 cryptographic key "
            "management and protection address the cryptographic aspects of secure transfer. "
            "SI-10 input validation supports integrity checking of transfer instructions. "
            "These controls address the technical security aspects of transfer service operations."
        ),
        "gaps": (
            "MiCA Art.76 requires CASP transfer services to verify that originator and beneficiary "
            "information is included with transfers (consistent with EU Funds Transfer Regulation "
            "2023/1113 / Travel Rule), screen transactions for sanctions, and maintain records. "
            "SP 800-53 does not address the Travel Rule, sanctions screening requirements, "
            "or the data accompanying crypto-asset transfers that MiCA/TFR mandates. "
            "These are AML/CFT compliance obligations requiring a separate regulatory framework."
        ),
    },

    # ──────────────────────────────────────────────────────────────────────────
    # ICT SECURITY AND OPERATIONAL RESILIENCE — CASPs
    # Art.62 cross-references DORA for larger CASPs; MiCA Art.62(5)-(6) contain
    # standalone ICT requirements for CASPs not subject to DORA.
    # ──────────────────────────────────────────────────────────────────────────

    {
        "id": "Art.62(5)",
        "title": "CASP ICT systems — security, reliability, and adequate resources",
        "controls": [
            "CM-02", "CM-06", "CM-07", "CP-07", "CP-09",
            "SA-03", "SA-08", "SC-05", "SC-07", "SI-02",
            "SI-04", "SI-13",
        ],
        "coverage_pct": 78,
        "rationale": (
            "CM-02/06/07 address configuration management, settings, and functionality "
            "restrictions for ICT systems. CP-07/09 address alternate processing and "
            "backups for resilience. "
            "SA-03 and SA-08 address lifecycle and security engineering for CASP platforms. "
            "SC-05/07 address DoS protection and boundary protection — key for service availability. "
            "SI-02 flaw remediation, SI-04 monitoring, and SI-13 predictive maintenance "
            "provide comprehensive system reliability controls. "
            "Together these address the ICT system security, reliability, and capacity "
            "requirements of Art.62(5) for CASPs."
        ),
        "gaps": (
            "MiCA Art.62(5) requires CASPs to have adequate ICT systems, infrastructure, "
            "and procedures proportionate to the complexity and nature of their services, "
            "and sufficient resources (both financial and human) to operate their systems "
            "reliably. SP 800-53 covers system security and reliability well. "
            "The financial and human resource adequacy requirements and ESMA's forthcoming "
            "RTS on ICT requirements for CASPs will introduce sector-specific standards. "
            "Larger CASPs are also subject to DORA, which introduces additional testing, "
            "third-party risk, and reporting obligations."
        ),
    },

    {
        "id": "Art.62(6)",
        "title": "CASP business continuity — ICT continuity policy",
        "controls": [
            "CP-01", "CP-02", "CP-03", "CP-04", "CP-06",
            "CP-07", "CP-09", "CP-10", "PM-09",
        ],
        "coverage_pct": 80,
        "rationale": (
            "CP-01/02 provide contingency policy and business continuity plan. "
            "CP-03 contingency training and CP-04 contingency testing address preparedness. "
            "CP-06/07 alternate storage and processing sites address recovery infrastructure. "
            "CP-09/10 address backup and system recovery procedures. "
            "PM-09 risk management strategy provides the overarching resilience framework. "
            "These controls comprehensively address the ICT continuity policy requirements "
            "of Art.62(6) for CASPs."
        ),
        "gaps": (
            "MiCA Art.62(6) requires CASPs to have an ICT continuity policy ensuring, in the "
            "event of an ICT system interruption, the protection of data and maintenance or "
            "rapid restoration of activities and services. SP 800-53 contingency planning "
            "controls address this well. "
            "Remaining gaps: MiCA-specific requirements around restoration timescales for "
            "crypto-asset custody and trading services, and ESMA RTS on business continuity "
            "standards for CASPs, will add sector-specific detail. CASPs under DORA also "
            "face enhanced testing and reporting obligations."
        ),
    },

    {
        "id": "Art.62(7)",
        "title": "CASP security policies — ICT and cyber security",
        "controls": [
            "AC-01", "AT-01", "AT-02", "CA-01", "CM-01",
            "IA-01", "IR-01", "PL-01", "RA-01", "SA-01",
            "SC-01", "SI-01",
        ],
        "coverage_pct": 82,
        "rationale": (
            "AC-01, CA-01, CM-01, IA-01, IR-01, PL-01, RA-01, SA-01, SC-01, SI-01 form "
            "the comprehensive policy baseline across all major NIST control families — "
            "access control, assessment, configuration, authentication, incident response, "
            "planning, risk assessment, acquisition, communications, and integrity. "
            "AT-01/02 ensure security awareness and training policies are in place. "
            "Together these provide strong coverage of a CASP security policy framework."
        ),
        "gaps": (
            "MiCA Art.62(7) requires CASPs to have adequate policies and procedures to "
            "ensure ICT and cyber security, including protection of systems and data from "
            "unauthorised access, and protection of clients' crypto-assets. "
            "SP 800-53 policy controls cover this domain comprehensively. "
            "Remaining gap: MiCA-specific requirements around crypto-asset security policies "
            "(private key management policies, wallet security, DLT-specific security) are "
            "not addressed by NIST controls. ESMA will issue guidelines on CASP security policies."
        ),
    },

    {
        "id": "Art.62(8)",
        "title": "CASP incident management — detection and reporting",
        "controls": [
            "AU-06", "IR-01", "IR-04", "IR-05", "IR-06",
            "IR-07", "IR-08", "SI-04", "SI-05",
        ],
        "coverage_pct": 72,
        "rationale": (
            "IR-01/04/05/06/07/08 provide a comprehensive incident response framework — "
            "policy, incident handling, incident monitoring, reporting, assistance, and plans. "
            "AU-06 audit review and analysis supports anomaly detection. "
            "SI-04 system monitoring and SI-05 security alerts provide detection capability. "
            "Together these address the incident detection, classification, and internal "
            "response dimensions of Art.62(8)."
        ),
        "gaps": (
            "MiCA Art.62(8) requires CASPs to have processes to detect, manage, and notify "
            "major operational or security incidents to competent authorities (initially within "
            "4 hours, final report within 1 month — mirroring DORA Article 19). "
            "SP 800-53 incident response covers detection and handling well. "
            "Gaps: the specific regulatory reporting obligation to national competent authorities "
            "and ESMA/EBA (with defined timescales and report formats) is not addressed by NIST. "
            "CASPs subject to DORA additionally face the full DORA incident reporting regime."
        ),
    },

    {
        "id": "Art.62(9)",
        "title": "CASP data protection — personal data handling",
        "controls": [
            "AC-03", "AU-01", "MP-06", "PT-01", "PT-02",
            "PT-03", "PT-04", "PT-05", "PT-06", "SC-28",
        ],
        "coverage_pct": 55,
        "rationale": (
            "PT-01 through PT-06 address PII processing, authority, consent, privacy notice, "
            "processing conditions, and privacy policy — providing strong NIST coverage of "
            "data protection obligations. "
            "AC-03 access enforcement and SC-28 data-at-rest protection address technical "
            "data security measures. AU-01 and MP-06 address audit policy and media sanitisation. "
            "Together these address the technical and policy dimensions of CASP data protection."
        ),
        "gaps": (
            "MiCA Art.62(9) requires CASPs to store all data relating to crypto-asset services "
            "for five years and ensure compliance with GDPR. "
            "SP 800-53 PT controls and AU-11 (audit retention) partially address this. "
            "GDPR compliance is a full regulatory obligation requiring a comprehensive data "
            "protection programme beyond SP 800-53 scope — see the GDPR coverage file for detail. "
            "MiCA-specific data retention requirements (five-year minimum for service data, "
            "blockchain transaction records, order records) are not fully addressed by NIST."
        ),
    },

    # ──────────────────────────────────────────────────────────────────────────
    # TITLE VI — MARKET ABUSE (Art. 86-92)
    # ──────────────────────────────────────────────────────────────────────────

    {
        "id": "Art.86(1)",
        "title": "Prohibition of insider dealing — policy and access controls",
        "controls": ["AC-02", "AC-05", "AC-06", "AU-02", "AU-12", "PM-01", "PS-06"],
        "coverage_pct": 32,
        "rationale": (
            "AC-02/05/06 address account management, separation of duties, and least privilege — "
            "providing technical controls to limit access to inside information. "
            "AU-02/12 support audit trails for access to sensitive market information. "
            "PM-01 and PS-06 provide organisational governance and personnel agreements "
            "that form the foundation for insider dealing policies."
        ),
        "gaps": (
            "MiCA Art.86 prohibits insider dealing in crypto-assets — acquiring, disposing of, "
            "or recommending based on inside information. This is a market abuse prohibition "
            "requiring insider lists, information barriers, market surveillance, and regulatory "
            "enforcement. SP 800-53 access controls provide partial technical segregation but "
            "do not address the legal prohibition, insider list requirements, front-running "
            "detection, or regulatory reporting obligations. These are financial regulation "
            "requirements outside NIST scope."
        ),
    },

    {
        "id": "Art.88(1)",
        "title": "Market manipulation — prohibition and detection",
        "controls": [
            "AU-02", "AU-06", "AU-12", "SI-04", "SI-07",
        ],
        "coverage_pct": 38,
        "rationale": (
            "AU-02/06/12 address audit events, audit review, and audit generation — "
            "providing infrastructure for trade surveillance log analysis. "
            "SI-04 system monitoring and SI-07 software and firmware integrity support "
            "anomaly detection in trading systems. "
            "These controls provide a technical monitoring foundation but not market "
            "surveillance functionality."
        ),
        "gaps": (
            "MiCA Art.88 prohibits market manipulation — transactions or orders giving false "
            "signals about supply/demand, price-fixing, information dissemination intended to "
            "manipulate prices. Detection requires trade surveillance systems and pattern "
            "analysis specific to crypto-asset markets. SP 800-53 system monitoring is "
            "general-purpose IT monitoring, not trade surveillance. The legal prohibition "
            "itself, investigation powers, and enforcement dimensions are outside NIST scope."
        ),
    },

    {
        "id": "Art.92(1)",
        "title": "CASP detection and prevention of market abuse — policies and procedures",
        "controls": [
            "AC-05", "AC-06", "AU-02", "AU-06", "AU-12",
            "IR-04", "PM-01", "PS-06", "SI-04",
        ],
        "coverage_pct": 50,
        "rationale": (
            "AC-05/06 provide separation of duties and least privilege for trading functions. "
            "AU-02/06/12 support audit and monitoring for suspicious order/transaction detection. "
            "IR-04 incident handling provides the process framework for responding to suspected "
            "market abuse. SI-04 system monitoring enables anomaly detection in trading activity. "
            "PM-01 and PS-06 provide programme management and conduct policy scaffolding."
        ),
        "gaps": (
            "MiCA Art.92 requires CASPs to establish and maintain effective arrangements, "
            "systems, and procedures to detect and report suspicious orders and transactions "
            "potentially constituting market abuse, with suspicious transaction reports (STRs) "
            "filed with competent authorities. SP 800-53 provides monitoring and incident "
            "handling controls but does not address trade surveillance systems, crypto-specific "
            "manipulation pattern libraries, STR filing obligations, or the regulatory interaction "
            "with competent authorities under market abuse rules."
        ),
    },

    # ──────────────────────────────────────────────────────────────────────────
    # TITLE VII — COMPETENT AUTHORITIES
    # ──────────────────────────────────────────────────────────────────────────

    {
        "id": "Art.94(1)",
        "title": "Powers of competent authorities — supervisory and investigatory powers",
        "controls": ["CA-02", "CA-07", "AU-01", "PM-01"],
        "coverage_pct": 20,
        "rationale": (
            "CA-02 security assessments and CA-07 continuous monitoring provide internal "
            "assessment capabilities that partially overlap with regulatory examination. "
            "AU-01 and PM-01 support documentation and oversight processes. "
            "Coverage is minimal as Art.94 addresses regulatory powers, not organisational "
            "security controls."
        ),
        "gaps": (
            "MiCA Art.94 grants competent authorities supervisory powers including: access to "
            "premises and documents, powers to summon persons, impose administrative sanctions, "
            "order suspension of services, and publish public notices. These are regulatory "
            "enforcement powers that cannot be mapped to information security controls. "
            "SP 800-53 is an organisational security framework and does not address "
            "regulatory supervisory or enforcement powers."
        ),
    },

    {
        "id": "Art.97(1)",
        "title": "Professional secrecy — confidentiality of supervisory information",
        "controls": [
            "AC-03", "AC-06", "MP-02", "MP-04",
            "PT-01", "SC-08", "SC-12", "SC-28",
        ],
        "coverage_pct": 52,
        "rationale": (
            "AC-03/06 access enforcement and least privilege protect confidential supervisory "
            "information. MP-02/04 address media access restrictions and storage of sensitive "
            "information. PT-01 PII processing policy provides a framework for handling "
            "confidential regulatory information. SC-08 transmission confidentiality and "
            "SC-12/28 cryptographic and at-rest protection address technical confidentiality."
        ),
        "gaps": (
            "MiCA Art.97 imposes professional secrecy obligations on competent authority staff "
            "and experts — binding them to maintain confidentiality of information received "
            "during supervisory work, with criminal liability for breach. "
            "SP 800-53 provides technical confidentiality controls but not the legal professional "
            "secrecy obligations, criminal liability framework, or the regulatory information "
            "sharing protocols between competent authorities that Art.97 establishes."
        ),
    },

    {
        "id": "Art.98(1)",
        "title": "Data protection — processing of personal data",
        "controls": [
            "PT-01", "PT-02", "PT-03", "PT-04", "PT-05",
            "PT-06", "PT-07", "PT-08", "SC-28",
        ],
        "coverage_pct": 55,
        "rationale": (
            "PT-01 through PT-08 provide comprehensive PII processing policy, authority, "
            "consent, privacy notice, processing conditions, privacy policy, identity "
            "management, and computer matching controls. "
            "SC-28 protection at rest addresses technical data protection. "
            "These NIST controls provide strong coverage of the technical and policy "
            "dimensions of personal data protection within MiCA supervisory activities."
        ),
        "gaps": (
            "MiCA Art.98 confirms that processing of personal data under MiCA is subject to "
            "GDPR (Regulation (EU) 2016/679) and EUDPR (Regulation (EU) 2018/1725) for "
            "EU institutions. GDPR compliance is a comprehensive legal obligation beyond "
            "SP 800-53 scope — see the GDPR coverage file for full gap analysis. "
            "The legal basis for processing, data subject rights, and cross-border transfer "
            "rules are regulatory obligations outside NIST scope."
        ),
    },

    {
        "id": "Art.111(1)",
        "title": "EBA/ESMA guidelines — technical standards and regulatory cooperation",
        "controls": ["CA-01", "CA-02", "PM-01", "PM-09", "RA-01"],
        "coverage_pct": 20,
        "rationale": (
            "CA-01/02, PM-01/09, and RA-01 provide security planning, assessment, and risk "
            "management frameworks that form the basis for compliance with regulatory technical "
            "standards. Coverage is minimal as Art.111 addresses regulatory authority mandates "
            "for guidelines, not organisational security controls."
        ),
        "gaps": (
            "MiCA Art.111 mandates EBA and ESMA to develop regulatory technical standards (RTS) "
            "and implementing technical standards (ITS) covering CASPs, ART/EMT issuers, and "
            "trading platforms. Many RTS are in development (2024-2025). SP 800-53 provides "
            "a strong baseline but MiCA RTS will impose sector-specific requirements — "
            "particularly for ICT security, custody, and outsourcing — that will introduce "
            "additional obligations beyond the current NIST mapping."
        ),
    },

    # ──────────────────────────────────────────────────────────────────────────
    # CROSS-CUTTING REQUIREMENTS
    # ──────────────────────────────────────────────────────────────────────────

    {
        "id": "Art.82(1)",
        "title": "Record-keeping — transaction and order records",
        "controls": [
            "AU-01", "AU-09", "AU-11", "AU-12",
            "CM-08", "SI-12",
        ],
        "coverage_pct": 60,
        "rationale": (
            "AU-01 audit policy, AU-09 audit record protection, AU-11 audit retention (5 years "
            "required under MiCA; NIST typically requires 3 years minimum), and AU-12 audit "
            "generation address the record-keeping infrastructure. "
            "CM-08 component inventory supports asset-level records. "
            "SI-12 information management and retention provides information lifecycle controls."
        ),
        "gaps": (
            "MiCA Art.82 requires CASPs to maintain records of all services, activities, orders, "
            "and transactions for at least five years and in a format accessible to competent "
            "authorities. SP 800-53 audit and record retention controls address the technical "
            "mechanisms. Gaps: MiCA specifies transaction-level detail for crypto-asset orders, "
            "the format of records, and the obligation to make them available for regulatory "
            "review — including blockchain transaction records tied to client accounts. "
            "These crypto-specific record formats are outside NIST scope."
        ),
    },

    {
        "id": "Art.83(1)",
        "title": "Information to clients — disclosures and marketing communications",
        "controls": ["PT-05", "PM-01"],
        "coverage_pct": 15,
        "rationale": (
            "PT-05 privacy notice addresses transparency obligations for personal data processing. "
            "PM-01 programme management provides oversight governance. "
            "Coverage is minimal as Art.83 is primarily a consumer protection and "
            "marketing communications requirement."
        ),
        "gaps": (
            "MiCA Art.83 requires all information provided to clients to be fair, clear, and "
            "not misleading, with marketing communications clearly identified as such. "
            "CASPs must provide prescribed pre-contractual disclosures including white papers, "
            "fee schedules, and risk warnings. These are consumer protection and disclosure "
            "obligations entirely outside SP 800-53 scope."
        ),
    },

    {
        "id": "Art.84(1)",
        "title": "Crypto-asset white paper — publication requirements",
        "controls": ["PM-01", "SA-05"],
        "coverage_pct": 12,
        "rationale": (
            "SA-05 system documentation and PM-01 programme management provide very limited "
            "coverage of the documentation and oversight dimensions. "
            "Coverage is minimal as white paper requirements are regulatory disclosure obligations "
            "rather than information security controls."
        ),
        "gaps": (
            "MiCA Art.84 requires CASPs facilitating trading to ensure crypto-assets have a "
            "published white paper compliant with Title II requirements, with mandatory content "
            "including technology description, rights/obligations, risks, and key personnel. "
            "This is a regulatory prospectus-equivalent requirement entirely outside SP 800-53. "
            "White paper content requirements, publication obligations, and ESMA notification "
            "are market regulation obligations with no NIST equivalent."
        ),
    },

    {
        "id": "Art.47(1)",
        "title": "ART — redemption rights and liquidity management",
        "controls": ["CP-02", "CP-09", "PM-09", "RA-03"],
        "coverage_pct": 22,
        "rationale": (
            "CP-02 contingency planning and CP-09 backup/recovery provide limited coverage "
            "of business continuity in redemption scenarios. PM-09 risk management strategy "
            "and RA-03 risk assessment provide the risk framework. "
            "Coverage is low as redemption rights are primarily a financial regulation requirement."
        ),
        "gaps": (
            "MiCA Art.47 requires ART issuers to establish redemption rights allowing token "
            "holders to redeem at any time at the reserve-backed value. This requires liquidity "
            "management policies, queue management, and operational procedures for high-volume "
            "redemption scenarios that are financial regulation obligations, not ICT security "
            "controls. Redemption liquidity, orderly wind-down procedures, and the regulatory "
            "halt mechanisms (Art.47(3)) are outside SP 800-53 scope."
        ),
    },
]


def compute_summary(clauses):
    """Compute summary statistics from clause list."""
    total = len(clauses)
    if total == 0:
        return {
            "total_clauses": 0,
            "average_coverage": 0,
            "full_count": 0,
            "substantial_count": 0,
            "partial_count": 0,
            "weak_count": 0,
            "none_count": 0,
        }

    total_pct = sum(c["coverage_pct"] for c in clauses)
    avg = round(total_pct / total, 1)

    full = sum(1 for c in clauses if c["coverage_pct"] >= 85)
    substantial = sum(1 for c in clauses if 65 <= c["coverage_pct"] <= 84)
    partial = sum(1 for c in clauses if 40 <= c["coverage_pct"] <= 64)
    weak = sum(1 for c in clauses if 1 <= c["coverage_pct"] <= 39)
    none = sum(1 for c in clauses if c["coverage_pct"] == 0)

    return {
        "total_clauses": total,
        "average_coverage": avg,
        "full_count": full,
        "substantial_count": substantial,
        "partial_count": partial,
        "weak_count": weak,
        "none_count": none,
    }


def build_output():
    """Build the full framework coverage JSON structure."""
    summary = compute_summary(CLAUSES)

    output = {
        "$schema": "../schema/framework-coverage.schema.json",
        "framework_id": "mica",
        "framework_name": "EU Markets in Crypto-Assets Regulation (MiCA)",
        "metadata": {
            "source": "SP800-53v5_Control_Mappings",
            "version": "1.0",
            "disclaimer": (
                "Based on Regulation (EU) 2023/1114 (MiCA). MiCA has sector-specific requirements "
                "for cryptoasset service providers (CASPs) and asset-referenced token issuers that "
                "extend beyond SP 800-53 scope, particularly in regulatory authorisation, market "
                "conduct, consumer protection, and stablecoin reserve management. Many ESMA and EBA "
                "regulatory technical standards are still in development (2024-2025) and will "
                "introduce additional sector-specific obligations. Validate with qualified assessors "
                "for compliance/audit use."
            ),
            "jurisdictions": ["EU"],
            "applicability_type": "mandatory",
        },
        "weight_scale": {
            "full": {"min": 85, "max": 100, "label": "Fully addressed"},
            "substantial": {"min": 65, "max": 84, "label": "Well addressed, notable gaps"},
            "partial": {"min": 40, "max": 64, "label": "Partially addressed"},
            "weak": {"min": 1, "max": 39, "label": "Weakly addressed"},
            "none": {"min": 0, "max": 0, "label": "No mapping"},
        },
        "clauses": CLAUSES,
        "summary": summary,
    }
    return output


def main():
    output = build_output()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("\n")

    summary = output["summary"]
    print(f"\n{'=' * 60}")
    print(f"MiCA Framework Coverage — Generation Summary")
    print(f"{'=' * 60}")
    print(f"Output:                {OUTPUT_PATH}")
    print(f"Total clauses:         {summary['total_clauses']}")
    print(f"Average coverage:      {summary['average_coverage']}%")
    print(f"{'=' * 60}")
    print(f"Full (85-100%):        {summary['full_count']}")
    print(f"Substantial (65-84%):  {summary['substantial_count']}")
    print(f"Partial (40-64%):      {summary['partial_count']}")
    print(f"Weak (1-39%):          {summary['weak_count']}")
    print(f"None (0%):             {summary['none_count']}")
    print(f"{'=' * 60}")

    # Print clause breakdown
    print(f"\nClause breakdown:")
    for c in CLAUSES:
        band = (
            "FULL"        if c["coverage_pct"] >= 85
            else "SUBST." if c["coverage_pct"] >= 65
            else "PART."  if c["coverage_pct"] >= 40
            else "WEAK"   if c["coverage_pct"] >= 1
            else "NONE"
        )
        print(f"  {c['id']:20s}  {c['coverage_pct']:3d}%  [{band:6s}]  {c['title'][:55]}")


if __name__ == "__main__":
    main()
