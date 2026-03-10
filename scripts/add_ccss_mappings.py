#!/usr/bin/env python3
"""
Generate CCSS v9.0 framework coverage mapping file.

CryptoCurrency Security Standard (CCSS) v9.0
Published: December 17, 2024
Issuer: CryptoCurrency Certification Consortium (C4)
Standard type: Market-driven (industry voluntary certification for crypto custodians/exchanges)

Structure:
  10 security aspects across 2 domains:
  Domain 1: Cryptographic Asset Management (Aspects 1.01-1.06)
  Domain 2: Operations (Aspects 2.01-2.04)

  41 control objectives distributed across 10 aspects at 3 maturity levels.
  Each clause in this mapping represents a discrete control objective (aspect at a
  specific level), mirroring how CCSS auditors score each requirement independently.

Aspect breakdown:
  1.01 Key Material Generation     (L1: 5 COs, L2: 1 CO, L3: 1 CO)
  1.02 Wallet Creation             (L1: 4 COs, L2: 2 COs, L3: 2 COs)
  1.03 Key Material Storage        (L1: 3 COs, L2: 2 COs, L3: 2 COs)
  1.04 Key Material Access         (L1: 2 COs, L2: 2 COs, L3: 1 CO)
  1.05 Key Usage                   (L1: 2 COs, L2: 2 COs, L3: 1 CO)
  1.06 Key Compromise Protocol     (L1: 2 COs, L2: 1 CO, L3: 1 CO)
  2.01 Security Audits & Pentests  (L1: 1 CO, L2: 1 CO, L3: 1 CO)
  2.02 Data Sanitization Policy    (L1: 1 CO, L2: 1 CO, L3: 1 CO)
  2.03 Proof of Reserve            (L1: 1 CO, L2: 1 CO, L3: 0 COs)  [2 COs]
  2.04 Audit Logs                  (L1: 1 CO, L2: 1 CO, L3: 1 CO)
  Total: 41 control objectives

References:
  https://cryptoconsortium.org/cryptocurrency-security-standard-documentation/ccss-details-v9/
  https://cryptoconsortium.org/ccss-table-v9/
  https://github.com/CryptoConsortium/CCSS (deprecated; v9 at official site)
"""

import json
import os

OUTPUT_PATH = "/Users/russellwing/osa-workspace/data/framework-coverage/ccss-v9.json"

# ============================================================
# CLAUSE DEFINITIONS
# Each clause is a discrete CCSS v9.0 control objective.
# IDs follow the CCSS convention: <aspect>.<CO-sequence>
# e.g. 1.01.1 = Aspect 1.01, Level-1 control objective 1
#      1.01.2 = Aspect 1.01, Level-1 control objective 2
#      1.01.L2 = Aspect 1.01, Level-2 control objective
# ============================================================

CLAUSES = [
    # ----------------------------------------------------------------
    # ASPECT 1.01 — KEY MATERIAL GENERATION
    # Covers generation of cryptographic keys and seeds used within
    # digital asset and blockchain protocols.
    # ----------------------------------------------------------------
    {
        "id": "1.01.1",
        "title": "Key Material Generation — Confidentiality of Key Generation Environment",
        "controls": ["SC-28", "PE-02", "PE-03", "PE-06", "SC-12"],
        "coverage_pct": 55,
        "rationale": "SC-28 addresses protection of information at rest and SC-12 covers cryptographic key establishment; PE controls address physical protection of the generation environment. These provide the foundational confidentiality controls CCSS requires for preventing key exfiltration during generation. However, NIST does not prescribe crypto-specific generation ceremony procedures such as air-gapped systems, Faraday shielding, or witness requirements.",
        "gaps": "CCSS mandates that key generation occurs in an isolated, physically controlled environment with no network connectivity, often with multiple witnesses. NIST PE and SC controls are generic and do not prescribe air-gapped generation environments, ceremony documentation, or observer verification unique to cryptocurrency key ceremonies."
    },
    {
        "id": "1.01.2",
        "title": "Key Material Generation — Entropy and Randomness Sources",
        "controls": ["SC-12", "SC-13"],
        "coverage_pct": 60,
        "rationale": "SC-12 covers cryptographic key management including generation procedures, and SC-13 requires use of FIPS-validated or approved cryptographic mechanisms. NIST SP 800-90A (referenced by SC-13) addresses DRBG requirements for random number generation. These controls partially address CCSS entropy requirements for key material generation.",
        "gaps": "CCSS specifically requires either a NIST SP 800-90A-compliant DRBG seeded with two independent cryptographically secure entropy sources, or a true hardware RNG (TRNG) validated against industry statistical tests. NIST controls reference approved algorithms but do not mandate multi-source entropy combination or specific TRNG validation procedures for custodial cryptocurrency contexts."
    },
    {
        "id": "1.01.3",
        "title": "Key Material Generation — Software Validation and Integrity",
        "controls": ["SI-03", "SI-07", "CM-03", "CM-05"],
        "coverage_pct": 65,
        "rationale": "SI-07 requires software integrity verification through cryptographic mechanisms; CM-03 and CM-05 control changes to software configurations and enforce least-privilege access. Together these address the requirement to validate that generation software has not been tampered with and does not contain backdoors or value-restricting features.",
        "gaps": "CCSS requires generating a digital signature for key creation software and validating it before each execution, and that software must not contain features that restrict key value ranges or covertly transmit data. NIST SI controls address integrity broadly but do not specify the per-execution signature validation workflow required by CCSS."
    },
    {
        "id": "1.01.4",
        "title": "Key Material Generation — Automated Signing Agent Key Transfer",
        "controls": ["SC-12", "SC-28", "MP-05", "SC-08"],
        "coverage_pct": 45,
        "rationale": "SC-12 covers key establishment and management; SC-28 protects information at rest during transfer; MP-05 controls media transport; SC-08 addresses transmission confidentiality. These partially address the requirement to securely transfer key material from a generation environment to an automated signing agent.",
        "gaps": "CCSS 1.01.1.2 requires specific procedural controls: key material generated offline, transferred securely to the automated agent, and then securely deleted from the generation device using CCSS-compliant sanitization. NIST does not define the end-to-end workflow for cryptocurrency automated signing agent provisioning, including the mandatory secure deletion step post-transfer."
    },
    {
        "id": "1.01.5",
        "title": "Key Material Generation — Level 1 Documentation and Procedural Controls",
        "controls": ["SC-12", "PL-01", "CA-09"],
        "coverage_pct": 50,
        "rationale": "SC-12 requires cryptographic key management planning and documentation; PL-01 establishes security planning policies; CA-09 addresses internal connections. These support documented procedures for key generation environments. NIST provides a policy framework but lacks cryptocurrency-specific procedural prescriptions.",
        "gaps": "CCSS Level 1 requires documented key generation procedures, including specific criteria for secure environments (no external interfaces, verified entropy), custodian roles during generation, and records of each generation event. NIST controls do not require generation event logs or multi-party observation records for cryptographic key generation ceremonies."
    },
    {
        "id": "1.01.6",
        "title": "Key Material Generation — Level 2 Generation Methodology Validation",
        "controls": ["CA-02", "SC-12", "SC-13"],
        "coverage_pct": 50,
        "rationale": "CA-02 requires security control assessments; SC-12 and SC-13 mandate approved cryptographic practices. At Level 2, CCSS requires formal validation that the generation methodology meets the standard, which these controls partially support through assessment and cryptographic governance requirements.",
        "gaps": "CCSS Level 2 mandates that the key generation methodology be formally validated prior to use, including verification that software does not restrict key value ranges or transmit data covertly. NIST assessments are general-purpose and do not validate cryptocurrency-specific key generation algorithmic properties or blockchain-protocol-specific seed derivation correctness."
    },
    {
        "id": "1.01.7",
        "title": "Key Material Generation — Level 3 Advanced Ceremony Controls",
        "controls": ["SC-12", "PE-02", "PE-03", "AU-10"],
        "coverage_pct": 30,
        "rationale": "SC-12 covers key management planning; PE controls address physical access; AU-10 provides non-repudiation through audit. These partially address Level 3 requirements for witnessed, formally recorded key generation ceremonies. However, the cryptocurrency-specific ceremony requirements are substantially beyond NIST scope.",
        "gaps": "CCSS Level 3 requires formal key generation ceremonies with multiple independent witnesses, ceremony scripts, recorded video evidence, hardware security module integration or equivalent air-gapped device controls, and tamper-evident logging of the entire event. These cryptocurrency custody ceremony requirements have no equivalent in NIST 800-53."
    },

    # ----------------------------------------------------------------
    # ASPECT 1.02 — WALLET CREATION
    # Covers creation of wallets/addresses capable of receiving digital
    # assets, including single-signer and multi-signer mechanisms.
    # ----------------------------------------------------------------
    {
        "id": "1.02.1",
        "title": "Wallet Creation — Single-Signer Wallet Architecture",
        "controls": ["SC-12", "SC-13", "CM-07"],
        "coverage_pct": 45,
        "rationale": "SC-12 addresses cryptographic key management that underlies wallet creation; SC-13 requires FIPS-approved algorithms for cryptographic operations; CM-07 restricts software to approved functions. These controls partially address security of single-signer wallet creation but do not address blockchain-specific address derivation.",
        "gaps": "CCSS requires documented procedures for single-signer wallet creation specific to the blockchain protocol (e.g., BIP-32/39/44 for HD wallets, JBOK wallets), including controls for address uniqueness, derivation path management, and address verification. NIST has no controls addressing blockchain address derivation or wallet architecture patterns."
    },
    {
        "id": "1.02.2",
        "title": "Wallet Creation — Multi-Signer Wallet Architecture",
        "controls": ["SC-12", "SC-13", "AC-05"],
        "coverage_pct": 40,
        "rationale": "AC-05 requires separation of duties, which aligns with multi-signer requirements ensuring no single party can unilaterally move funds; SC-12 covers key management; SC-13 mandates approved cryptographic mechanisms for multi-party cryptography. These partially address the policy intent of multi-signer wallet controls.",
        "gaps": "CCSS specifically addresses multi-signature (m-of-n) schemes, threshold signature schemes (TSS/MPC), and smart contract-based multisig with requirements for signing quorum documentation, key shard distribution, and quorum testing. NIST 800-53 has no controls for blockchain multisig schemes, MPC/TSS wallet architectures, or distributed key custody arrangements."
    },
    {
        "id": "1.02.3",
        "title": "Wallet Creation — Wallet Inventory and Address Management",
        "controls": ["CM-08", "SC-12", "PM-05"],
        "coverage_pct": 50,
        "rationale": "CM-08 requires system component inventory tracking; PM-05 addresses information system inventory; SC-12 covers key management documentation. These controls support wallet address inventory requirements at a general level. NIST inventory controls apply to systems and components but can be adapted to wallet management practices.",
        "gaps": "CCSS requires a comprehensive wallet inventory that tracks all active addresses, their associated key material references, signing quorum configurations, and fund balances. Blockchain-specific address lifecycle management (creation, rotation, archival) and on-chain verification of address control are not addressed by NIST component inventory controls."
    },
    {
        "id": "1.02.4",
        "title": "Wallet Creation — Address Verification and Integrity",
        "controls": ["SI-07", "SC-12", "SC-17"],
        "coverage_pct": 45,
        "rationale": "SI-07 addresses software and firmware integrity verification; SC-17 covers public key infrastructure for certificate management; SC-12 addresses key management. These partially support the requirement to verify wallet addresses are correctly derived and have not been substituted by malware or clipboard hijackers.",
        "gaps": "CCSS requires specific controls to verify wallet addresses during creation and before use, addressing clipboard hijacking attacks and address substitution malware. Blockchain-specific address checksum verification, visual inspection protocols, and out-of-band address confirmation procedures are not addressed in NIST controls."
    },
    {
        "id": "1.02.5",
        "title": "Wallet Creation — Level 2 Documented Custody Policy for Wallet Creation",
        "controls": ["PL-01", "SC-12", "PM-09"],
        "coverage_pct": 55,
        "rationale": "PL-01 establishes security planning and policy documentation requirements; PM-09 addresses risk management strategy; SC-12 requires cryptographic key management planning. These provide a policy framework that partially satisfies CCSS Level 2 requirements for a documented custody policy covering wallet creation procedures.",
        "gaps": "CCSS Level 2 requires a formal documented custody policy that covers wallet creation specifically, including wallet types approved for use, signing configurations, fund segregation requirements, and wallet lifecycle management. NIST policy controls are general-purpose and do not address cryptocurrency custody policy elements."
    },
    {
        "id": "1.02.6",
        "title": "Wallet Creation — Level 2 Deterministic Wallet Controls",
        "controls": ["SC-12", "CM-03", "CM-06"],
        "coverage_pct": 35,
        "rationale": "SC-12 covers cryptographic key establishment procedures; CM-03 and CM-06 address configuration management and baseline controls. These partially address the need to manage and document deterministic wallet generation parameters (master seeds, derivation paths). However, HD wallet-specific controls are absent from NIST.",
        "gaps": "CCSS Level 2 addresses hierarchical deterministic (HD) wallet controls including BIP-32/39/44 derivation path management, master seed protection, and derivation from a single master secret. NIST has no controls covering blockchain-specific HD wallet architectures, seed phrase management, or derivation path governance."
    },
    {
        "id": "1.02.7",
        "title": "Wallet Creation — Level 3 Smart Contract Wallet Auditing",
        "controls": ["CA-08", "SA-11", "SA-15"],
        "coverage_pct": 30,
        "rationale": "CA-08 requires penetration testing; SA-11 mandates developer security testing including code review; SA-15 addresses development process and security requirements. These partially map to smart contract security audit requirements introduced in CCSS v9.0, but the blockchain execution environment is fundamentally different from traditional software.",
        "gaps": "CCSS v9.0 requires all deployed smart contracts to undergo third-party security audits by specialists in Ethereum/EVM smart contract security, covering reentrancy, integer overflow, access control flaws, and upgrade proxy patterns. NIST SA controls do not address smart contract-specific vulnerabilities, on-chain immutability constraints, or DeFi protocol security patterns."
    },
    {
        "id": "1.02.8",
        "title": "Wallet Creation — Level 3 Smart Contract State Monitoring",
        "controls": ["SI-04", "AU-06", "IR-05"],
        "coverage_pct": 30,
        "rationale": "SI-04 requires continuous monitoring of information systems; AU-06 addresses audit review and analysis; IR-05 addresses incident tracking. These partially map to CCSS Level 3 requirements to monitor smart contract state changes and wallet address activity on-chain for anomalies.",
        "gaps": "CCSS Level 3 requires blockchain-native monitoring of smart contract state changes, on-chain transaction patterns, and wallet address activity using blockchain analytics tools. NIST monitoring controls address traditional network and system monitoring but have no provisions for blockchain mempool monitoring, on-chain event log analysis, or DeFi protocol state surveillance."
    },

    # ----------------------------------------------------------------
    # ASPECT 1.03 — KEY MATERIAL STORAGE
    # Covers secure storage and backup of key material to ensure
    # protection, recoverability, and access restriction.
    # ----------------------------------------------------------------
    {
        "id": "1.03.1",
        "title": "Key Storage — Encryption of Keys at Rest",
        "controls": ["SC-28", "SC-12", "SC-13"],
        "coverage_pct": 75,
        "rationale": "SC-28 explicitly requires protection of information at rest using cryptographic mechanisms; SC-12 governs cryptographic key establishment and management; SC-13 mandates FIPS-validated cryptographic algorithms such as AES-256. These controls directly address the CCSS requirement that cryptographic keys and seeds be encrypted at rest with strong encryption (AES-256 or equivalent).",
        "gaps": "CCSS specifies that the encryption protecting stored keys must be at least as strong as the keys being protected (e.g., 256-bit keys protected by AES-256), and for Level 3 requires that backups use equivalent encryption strength to production keys. NIST controls do not establish this proportionality requirement or mandate specific key hierarchy depth for custodial crypto systems."
    },
    {
        "id": "1.03.2",
        "title": "Key Storage — Backup Existence and Accessibility",
        "controls": ["CP-09", "CP-10", "SC-12"],
        "coverage_pct": 70,
        "rationale": "CP-09 requires information system backups including backup testing; CP-10 addresses information system recovery; SC-12 covers key management including recovery procedures. Together these address the CCSS requirement that backups exist for sufficient keys to recover spending capability and that backup restoration is periodically tested.",
        "gaps": "CCSS specifies that backups must exist for at least the number of keys required to spend funds (not just all keys), and must be tested for recoverability. The standard requires documentation of quorum requirements and backup verification specific to multi-sig or threshold signing schemes. NIST backup controls are general-purpose and do not address cryptocurrency-specific key quorum recoverability."
    },
    {
        "id": "1.03.3",
        "title": "Key Storage — Environmental Protection of Key Backups",
        "controls": ["PE-09", "PE-10", "PE-13", "PE-14", "CP-09"],
        "coverage_pct": 70,
        "rationale": "PE-09 through PE-14 address physical and environmental protection including fire suppression, temperature/humidity controls, and water damage prevention; CP-09 requires backups be stored and protected appropriately. These controls map well to the CCSS requirement that key backups be protected against environmental risks including fire, flood, and other physical threats.",
        "gaps": "CCSS Level 3 requires that backups be resistant to electromagnetic pulses (EMP), which implies Faraday cage storage or equivalent shielding. NIST PE controls do not address EMP hardening or the use of EMP-resistant storage media (e.g., steel containers, granite vaults) that CCSS Level 3 requires for key backup environmental resilience."
    },
    {
        "id": "1.03.4",
        "title": "Key Storage — Level 2 Geographic Separation of Key Backups",
        "controls": ["CP-06", "CP-09", "PE-18"],
        "coverage_pct": 65,
        "rationale": "CP-06 requires alternate storage sites for backup information; CP-09 mandates backup procedures; PE-18 addresses location of information system components. These controls support the CCSS Level 2 requirement that backup key material be stored in geographically separate locations to prevent single-site loss.",
        "gaps": "CCSS Level 2 requires that backups be stored in physically distinct locations (different buildings or cities) with equivalent physical security to the primary location, and that transport of backup material follows documented secure courier procedures. NIST does not specify minimum geographic separation distances or secure custody-of-custody requirements for cryptographic key material transport."
    },
    {
        "id": "1.03.5",
        "title": "Key Storage — Level 2 Access Control for Key Material",
        "controls": ["AC-03", "AC-06", "AC-17", "IA-02", "IA-12"],
        "coverage_pct": 70,
        "rationale": "AC-03 enforces access control policies; AC-06 implements least privilege; AC-17 controls remote access; IA-02 and IA-12 require strong authentication. These controls directly address the CCSS Level 2 requirement that access to both production key material and backups be tightly controlled with strong authentication and least-privilege principles.",
        "gaps": "CCSS requires authentication controls specifically for key material access, including quorum-based access (m-of-n people required) for production key usage and separate authentication for backup access. Multi-party authorization requirements for cryptocurrency key access are not addressed by NIST access control controls, which focus on system access rather than cryptographic key custody protocols."
    },
    {
        "id": "1.03.6",
        "title": "Key Storage — Level 3 Cold Storage and Hardware Security Controls",
        "controls": ["SC-12", "SC-28", "PE-02", "PE-03"],
        "coverage_pct": 35,
        "rationale": "SC-12 covers cryptographic key management; SC-28 protects information at rest; PE-02 and PE-03 control physical access to facilities. These partially support cold storage security requirements. However, cold storage in cryptocurrency contexts involves hardware security modules or dedicated offline signing devices with no general NIST equivalent.",
        "gaps": "CCSS Level 3 requires cold storage key material be stored on hardware wallets, HSMs, or air-gapped computers with verified firmware, and backups must be encrypted at rest with encryption strength equal to the production keys. The entire cold storage paradigm — offline signing devices, hardware wallet attestation, and ceremony-based key retrieval — has no equivalent in NIST 800-53."
    },
    {
        "id": "1.03.7",
        "title": "Key Storage — Level 3 EMP-Resistant Backup Storage",
        "controls": ["PE-09", "PE-14", "CP-09"],
        "coverage_pct": 20,
        "rationale": "PE-09 addresses power equipment protection; PE-14 controls temperature and humidity; CP-09 covers backup procedures. These provide baseline physical environmental protection. However, NIST has no controls addressing EMP hardening, which is a specific Level 3 CCSS requirement.",
        "gaps": "CCSS Level 3 explicitly requires that backups of key material be resistant to electromagnetic pulses (requirement 1.03.3.3), implying storage in Faraday cages, steel safes, or granite vaults. This is a cryptocurrency-specific physical security requirement with no analogue in NIST 800-53, which does not address EMP threats to cryptographic key material backup media."
    },

    # ----------------------------------------------------------------
    # ASPECT 1.04 — KEY MATERIAL ACCESS (KEYHOLDER GRANT/REVOKE)
    # Covers policies and procedures surrounding granting and revoking
    # access to key material, including personnel onboarding/offboarding.
    # ----------------------------------------------------------------
    {
        "id": "1.04.1",
        "title": "Key Material Access — Keyholder Onboarding and Access Grant Procedures",
        "controls": ["PS-04", "AC-02", "IA-02", "IA-05"],
        "coverage_pct": 65,
        "rationale": "PS-04 covers personnel termination and transfer; AC-02 addresses account management including provisioning; IA-02 requires authentication; IA-05 manages authenticator provisioning. Together these address formal procedures for granting access to key material upon keyholder onboarding, including background verification and credential provisioning.",
        "gaps": "CCSS requires documented keyholder grant procedures specific to cryptographic signing authority, including co-signing of access grant by multiple existing keyholders, formal training requirements for new keyholders, and recording of keyholder identity with their associated key material. NIST account management controls do not address multi-party authorization of keyholder access or blockchain-specific signing authority provisioning."
    },
    {
        "id": "1.04.2",
        "title": "Key Material Access — Keyholder Offboarding and Access Revocation",
        "controls": ["PS-04", "PS-05", "AC-02", "IA-05"],
        "coverage_pct": 70,
        "rationale": "PS-04 requires immediate account termination upon personnel departure; PS-05 addresses personnel transfers; AC-02 requires timely account disabling; IA-05 covers authenticator revocation. These controls directly address the CCSS requirement to revoke keyholder access upon departure or role change, including revoking signing authority.",
        "gaps": "CCSS requires that upon keyholder departure or compromise, associated key material (not just system access) must be rotated or the keyholder's signing key revoked from the multisig quorum. Rotating cryptocurrency keys after personnel departure is a blockchain-specific operational requirement — NIST account termination controls address system access revocation but not cryptographic key rotation upon keyholder departure."
    },
    {
        "id": "1.04.3",
        "title": "Key Material Access — Level 2 Quorum-Based Keyholder Authorization",
        "controls": ["AC-05", "AC-06", "IA-02"],
        "coverage_pct": 45,
        "rationale": "AC-05 requires separation of duties; AC-06 enforces least privilege; IA-02 requires multi-factor authentication. These partially address Level 2 requirements that no single individual can unilaterally access production key material, requiring a defined quorum of keyholders (m-of-n) to authorize access.",
        "gaps": "CCSS Level 2 requires that key material access require multiple keyholders (quorum) to be present simultaneously, with documented m-of-n threshold requirements for each key type. Quorum-based physical key ceremonies and Shamir Secret Sharing arrangements are cryptocurrency custody constructs with no direct mapping in NIST, which addresses separation of duties conceptually but not multi-party physical key access protocols."
    },
    {
        "id": "1.04.4",
        "title": "Key Material Access — Level 2 Keyholder Identity Verification and Training",
        "controls": ["PS-03", "AT-03", "IA-12"],
        "coverage_pct": 65,
        "rationale": "PS-03 requires personnel screening before granting access; AT-03 mandates role-based security training; IA-12 establishes identity proofing requirements. These controls support CCSS Level 2 requirements for verifying keyholder identity and ensuring they receive training before being granted cryptographic signing authority.",
        "gaps": "CCSS specifies training requirements specific to cryptocurrency key custody responsibilities and requires formal acknowledgement of keyholder duties. Cryptocurrency-specific training on key handling procedures, cold storage protocols, and key ceremony participation is not addressed by NIST training controls, which focus on general security awareness."
    },
    {
        "id": "1.04.5",
        "title": "Key Material Access — Level 3 Formal Keyholder Registry and Audit Trail",
        "controls": ["AU-09", "AU-10", "AU-12", "CM-08"],
        "coverage_pct": 50,
        "rationale": "AU-09 protects audit information; AU-10 provides non-repudiation for audit events; AU-12 requires audit record generation; CM-08 maintains component inventories. These partially address Level 3 requirements for maintaining an auditable registry of all keyholders and their associated cryptographic signing authorities.",
        "gaps": "CCSS Level 3 requires a formally maintained keyholder registry linking individuals to specific key shards or signing keys, with tamper-evident records of all grant/revoke events signed by authorized administrators. This blockchain-custody-specific keyholder provenance chain is substantially more rigorous than NIST audit record requirements, which do not address cryptographic signing authority registries."
    },

    # ----------------------------------------------------------------
    # ASPECT 1.05 — KEY USAGE
    # Covers secure use of key material to protect confidentiality
    # and ensure integrity of funds during transaction signing.
    # ----------------------------------------------------------------
    {
        "id": "1.05.1",
        "title": "Key Usage — Transaction Authorization and Signing Controls",
        "controls": ["AC-03", "AC-06", "IA-02", "AU-10"],
        "coverage_pct": 55,
        "rationale": "AC-03 enforces information access restrictions; AC-06 implements least privilege; IA-02 requires authentication before use; AU-10 provides non-repudiation for signed actions. These controls partially address the requirement that key usage for transaction signing requires proper authentication and authorization, with a non-repudiable audit trail.",
        "gaps": "CCSS requires that each use of key material for signing cryptocurrency transactions be authenticated via multi-factor methods, with destination address and amount verification by the signing party before signing. Blockchain transaction signing workflows, including the requirement for the signer to visually verify destination addresses on a trusted display (address poisoning prevention), are not addressed by NIST controls."
    },
    {
        "id": "1.05.2",
        "title": "Key Usage — Key Usage Logging and Non-Repudiation",
        "controls": ["AU-02", "AU-03", "AU-09", "AU-10", "AU-12"],
        "coverage_pct": 75,
        "rationale": "AU-02 defines auditable events; AU-03 specifies audit record content; AU-09 protects audit information integrity; AU-10 provides non-repudiation; AU-12 generates audit records. These controls map well to the CCSS requirement to maintain a tamper-evident log of every key usage event including transaction details, signing identity, and timestamp.",
        "gaps": "CCSS requires that key usage logs capture blockchain-specific transaction details (transaction ID, amount, destination address, fee) and link each signing event to the keyholder identity and the signing mechanism used. NIST audit controls address system-level audit records but do not specify cryptocurrency transaction-level logging requirements or on-chain cross-referencing of audit logs."
    },
    {
        "id": "1.05.3",
        "title": "Key Usage — Level 2 Multi-Party Authorization for High-Value Transactions",
        "controls": ["AC-05", "AC-06", "IA-02"],
        "coverage_pct": 45,
        "rationale": "AC-05 enforces separation of duties; AC-06 requires least privilege; IA-02 mandates authentication. These partially address Level 2 requirements for multi-party authorization of cryptocurrency transactions, particularly for high-value or cold storage transactions requiring multiple keyholders to co-sign.",
        "gaps": "CCSS Level 2 requires that transactions above defined thresholds require multiple keyholders to co-authorize using cryptographic multi-signature or threshold signature schemes. The technical implementation of m-of-n transaction signing, including quorum assembly, signing coordination protocols, and transaction finalization procedures are cryptocurrency-specific and not addressed in NIST controls."
    },
    {
        "id": "1.05.4",
        "title": "Key Usage — Level 2 Destination Address Whitelisting and Verification",
        "controls": ["CM-07", "AC-04", "SI-03"],
        "coverage_pct": 40,
        "rationale": "CM-07 restricts software to authorized functions; AC-04 enforces information flow policies; SI-03 provides malware protection. These partially support destination address controls by restricting transaction flows. However, blockchain-specific address whitelisting and visual verification requirements are not covered.",
        "gaps": "CCSS Level 2 requires that cryptocurrency transactions only be sent to pre-approved, whitelisted addresses or undergo a manual out-of-band verification step before signing. Blockchain address whitelist management, change approval workflows for whitelist modifications, and visual address verification procedures (to prevent clipboard malware) are not addressed in NIST 800-53."
    },
    {
        "id": "1.05.5",
        "title": "Key Usage — Level 3 Hardware-Enforced Signing and Trusted Display",
        "controls": ["SC-12", "SC-28", "PE-03"],
        "coverage_pct": 25,
        "rationale": "SC-12 covers cryptographic key management; SC-28 protects data at rest on signing devices; PE-03 controls physical access to signing systems. These minimally address Level 3 requirements for hardware-enforced key signing using dedicated hardware wallets or HSMs with trusted display screens.",
        "gaps": "CCSS Level 3 requires transaction signing to occur on dedicated hardware devices (hardware wallets, HSMs) with built-in trusted displays showing transaction details before signing, preventing host computer compromise from affecting signing decisions. This hardware wallet attestation model, including device firmware verification and trusted display requirements, has no equivalent in NIST 800-53."
    },

    # ----------------------------------------------------------------
    # ASPECT 1.06 — KEY COMPROMISE PROTOCOL
    # Covers documented and tested procedures for responding to
    # suspected or confirmed compromise of key material or keyholders.
    # ----------------------------------------------------------------
    {
        "id": "1.06.1",
        "title": "Key Compromise Protocol — Documented Key Compromise Response Procedures",
        "controls": ["IR-01", "IR-08", "CP-02", "SC-12"],
        "coverage_pct": 60,
        "rationale": "IR-01 establishes incident response policy; IR-08 requires an incident response plan; CP-02 addresses contingency planning; SC-12 covers cryptographic key management including compromise recovery. Together these support the CCSS requirement for a documented Key Compromise Protocol (KCP) defining actions for each compromise classification.",
        "gaps": "CCSS requires the KCP to address each specific classification of key (hot, warm, cold, backup), define cryptocurrency fund transfer procedures to new keys upon compromise, specify communication channels for compromise notification (approved out-of-band channels), and name primary and secondary responders by role. Cryptocurrency-specific key compromise triage and fund-sweeping procedures are not addressed in NIST incident response or contingency planning controls."
    },
    {
        "id": "1.06.2",
        "title": "Key Compromise Protocol — Compromised Keyholder Response and Access Revocation",
        "controls": ["IR-06", "PS-04", "AC-02", "IA-05"],
        "coverage_pct": 60,
        "rationale": "IR-06 requires incident reporting and response; PS-04 addresses personnel termination including access revocation; AC-02 and IA-05 cover account and authenticator management. These controls support the requirement to revoke a compromised keyholder's access and credentials upon suspicion of compromise.",
        "gaps": "CCSS requires that upon keyholder compromise, the keyholder's cryptographic signing key be immediately revoked from all multisig quorums, remaining keyholders be notified via approved communication channels (not potentially compromised email), and funds be moved to new wallets with non-compromised key material. Cryptocurrency-specific fund-sweeping after keyholder compromise is outside NIST's scope."
    },
    {
        "id": "1.06.3",
        "title": "Key Compromise Protocol — Level 2 Tested and Rehearsed Response Procedures",
        "controls": ["IR-03", "CP-04", "IR-08"],
        "coverage_pct": 60,
        "rationale": "IR-03 requires incident response testing through exercises; CP-04 requires contingency plan testing and exercises; IR-08 mandates an up-to-date incident response plan. These controls directly support the CCSS Level 2 requirement that the Key Compromise Protocol be tested regularly to verify it works as intended.",
        "gaps": "CCSS Level 2 requires that the KCP be rehearsed in a simulated environment to verify all steps function correctly, including test fund transfers using the compromise response procedures. Cryptocurrency-specific KCP drills — including simulated key revocation, test transaction signing with backup keys, and fund transfer rehearsals — are more operationally specific than NIST exercise requirements."
    },
    {
        "id": "1.06.4",
        "title": "Key Compromise Protocol — Level 3 Out-of-Band Communication and Advanced Compromise Controls",
        "controls": ["IR-08", "CP-02", "SC-08"],
        "coverage_pct": 40,
        "rationale": "IR-08 covers incident response plan maintenance; CP-02 addresses contingency plan maintenance; SC-08 covers transmission confidentiality and integrity. These partially address the requirement for secure, out-of-band communication channels during key compromise response, but lack cryptocurrency-specific requirements.",
        "gaps": "CCSS Level 3 requires specific approved communication channels (e.g., pre-established encrypted messaging, in-person meetings) for compromise notification that are independent of potentially compromised infrastructure. The standard also requires Level 3 entities to maintain pre-positioned replacement wallets and signed transaction templates ready for immediate fund sweeps. These cryptocurrency-specific operational preparedness requirements have no NIST equivalent."
    },

    # ----------------------------------------------------------------
    # ASPECT 2.01 — SECURITY AUDITS AND PENETRATION TESTS
    # Covers independent third-party reviews of people, process, and
    # technology protecting the CCSS Trusted Environment.
    # ----------------------------------------------------------------
    {
        "id": "2.01.1",
        "title": "Security Audits — Level 1 Vulnerability Scans and Annual Security Review",
        "controls": ["CA-02", "CA-07", "RA-05", "SI-02"],
        "coverage_pct": 80,
        "rationale": "CA-02 requires security control assessments; CA-07 mandates continuous monitoring; RA-05 addresses vulnerability scanning; SI-02 requires flaw remediation. These controls map well to CCSS Level 1 requirements for regular vulnerability scanning and an annual independent security review of the CCSS Trusted Environment.",
        "gaps": "CCSS requires that vulnerability scans explicitly cover the cryptocurrency infrastructure including signing systems, wallet management platforms, and key storage environments. NIST controls address general scanning and assessment but do not specify cryptocurrency-custodian-specific scope definitions or require scans to address blockchain node configurations and DeFi protocol interfaces."
    },
    {
        "id": "2.01.2",
        "title": "Security Audits — Level 2 Independent Penetration Testing",
        "controls": ["CA-08", "RA-05", "CA-02"],
        "coverage_pct": 80,
        "rationale": "CA-08 explicitly requires penetration testing; RA-05 addresses vulnerability identification; CA-02 covers security assessments. These controls directly address CCSS Level 2 requirements for independent penetration testing of the CCSS Trusted Environment to identify exploitable paths to key material.",
        "gaps": "CCSS Level 2 requires penetration tests to specifically target cryptocurrency-specific attack vectors including key exfiltration paths, cold storage bypass scenarios, wallet address substitution, and multi-sig quorum compromise. NIST penetration testing requirements are general-purpose and do not specify blockchain or cryptocurrency-custody-specific test scenarios."
    },
    {
        "id": "2.01.3",
        "title": "Security Audits — Level 3 Full Independent CCSS Compliance Audit",
        "controls": ["CA-02", "CA-07", "CA-08", "AU-06"],
        "coverage_pct": 65,
        "rationale": "CA-02 requires comprehensive security control assessments; CA-07 covers continuous monitoring; CA-08 mandates penetration testing; AU-06 requires audit review and analysis. These support CCSS Level 3 requirements for a comprehensive independent audit covering all 41 CCSS control objectives by a qualified CCSS auditor (CCSSA credential).",
        "gaps": "CCSS Level 3 requires a full CCSS compliance audit performed by a credentialed CCSS Security Auditor (CCSSA) covering all aspects including key ceremony observation and smart contract review. NIST does not define cryptocurrency-specific auditor credentials, audit scope definitions for digital asset custodians, or the blockchain-native audit evidence requirements (e.g., on-chain proof of reserve verification)."
    },

    # ----------------------------------------------------------------
    # ASPECT 2.02 — DATA SANITIZATION POLICY
    # Covers secure removal of key material from digital media upon
    # decommissioning or reassignment of devices.
    # ----------------------------------------------------------------
    {
        "id": "2.02.1",
        "title": "Data Sanitization — Level 1 Documented Sanitization Policy for Key Material",
        "controls": ["MP-06", "MP-07", "SI-12"],
        "coverage_pct": 80,
        "rationale": "MP-06 explicitly requires media sanitization using approved techniques prior to disposal or reuse; MP-07 restricts use of media in facilities without authorization; SI-12 addresses information handling and retention. These controls closely match the CCSS Level 1 requirement for a documented data sanitization policy covering all media containing key material.",
        "gaps": "CCSS specifies that sanitization procedures must account for all media types that could hold key material including HSMs, hardware wallets, paper backups, and cloud storage. NIST MP controls address general media sanitization but do not specifically address cryptocurrency hardware wallet factory-reset procedures, paper wallet destruction protocols, or cloud-based key store deletion verification."
    },
    {
        "id": "2.02.2",
        "title": "Data Sanitization — Level 2 Verified Destruction with Evidence",
        "controls": ["MP-06", "AU-10", "CA-09"],
        "coverage_pct": 70,
        "rationale": "MP-06 requires media sanitization and can include documentation of sanitization events; AU-10 provides non-repudiation for destruction activities; CA-09 covers internal connections and decommissioning procedures. These partially address Level 2 requirements for verified destruction with evidence.",
        "gaps": "CCSS Level 2 requires documented evidence of key material sanitization including witness signatures, device serial numbers, sanitization method used, and date/time of destruction. For hardware devices, CCSS may require physical destruction (degaussing, shredding) with third-party certification. NIST MP-06 does not require witnessed destruction certificates or hardware destruction verification records at the individual device level."
    },
    {
        "id": "2.02.3",
        "title": "Data Sanitization — Level 3 Third-Party Verified Destruction",
        "controls": ["MP-06", "CA-02", "AU-10"],
        "coverage_pct": 55,
        "rationale": "MP-06 addresses media sanitization; CA-02 requires assessments including verification of controls; AU-10 covers non-repudiation. These partially support Level 3 requirements for independent third-party verification of key material destruction, which provides the highest assurance level for data sanitization.",
        "gaps": "CCSS Level 3 requires physical destruction of key material storage media to be witnessed and certified by an independent third party, with formal chain-of-custody documentation. This is substantially beyond NIST MP-06, which does not require third-party witness or certification for media sanitization events, nor does it address cryptocurrency-specific hardware wallet firmware wiping verification."
    },

    # ----------------------------------------------------------------
    # ASPECT 2.03 — PROOF OF RESERVE
    # Covers demonstrating cryptographic proof that the organization
    # controls all claimed cryptocurrency reserves.
    # ----------------------------------------------------------------
    {
        "id": "2.03.1",
        "title": "Proof of Reserve — Level 1 Internal Reserve Verification and Reconciliation",
        "controls": ["CA-02", "AU-06", "AU-11"],
        "coverage_pct": 30,
        "rationale": "CA-02 requires security control assessments and can extend to financial controls; AU-06 addresses audit review and analysis; AU-11 governs audit record retention. These minimally support internal reserve reconciliation processes by providing a framework for periodic review and audit record retention. However, the cryptocurrency-specific nature of PoR is largely outside NIST scope.",
        "gaps": "CCSS Proof of Reserve requires cryptographic proof that the organization controls specific on-chain addresses holding claimed reserve assets, typically via merkle tree liability proofs or address-signing ceremonies. This is a blockchain-native cryptographic attestation mechanism with no equivalent in NIST 800-53, which has no controls addressing on-chain asset verification, merkle proof construction, or cryptocurrency reserve attestation protocols."
    },
    {
        "id": "2.03.2",
        "title": "Proof of Reserve — Level 2 Independent Third-Party Reserve Attestation",
        "controls": ["CA-02", "CA-08", "AU-06"],
        "coverage_pct": 25,
        "rationale": "CA-02 covers security assessments which can include financial controls reviews; CA-08 requires independent penetration testing and assessment; AU-06 covers audit review processes. These controls provide a minimal framework for independent assessment but do not address cryptocurrency reserve verification techniques.",
        "gaps": "CCSS Level 2 requires an independent third-party auditor to verify that the organization's on-chain reserves match or exceed stated liabilities using cryptographic proof techniques (address signing, merkle tree proofs, or zk-proof-based PoR). Blockchain-native reserve attestation, including on-chain address signing ceremonies and merkle liability tree audits, are entirely outside NIST 800-53's scope."
    },

    # ----------------------------------------------------------------
    # ASPECT 2.04 — AUDIT LOGS
    # Covers logging of events within the CCSS Trusted Environment to
    # support audit, incident response, and forensic activities.
    # ----------------------------------------------------------------
    {
        "id": "2.04.1",
        "title": "Audit Logs — Level 1 Logging Policy and Key Management Event Logging",
        "controls": ["AU-01", "AU-02", "AU-03", "AU-09", "AU-12"],
        "coverage_pct": 80,
        "rationale": "AU-01 establishes audit and accountability policy; AU-02 defines auditable events; AU-03 specifies audit record content requirements; AU-09 protects audit information integrity; AU-12 requires audit record generation. These controls closely match CCSS Level 1 requirements to define an audit logging policy and log key management events (signing, key additions/removals, privilege changes) within the Trusted Environment.",
        "gaps": "CCSS specifically requires logging of blockchain-specific key management events: use of keys for signing transactions (with transaction details), addition/removal/modification of keys in signing quorums, key rotation events, and changes to user account privileges for key access. NIST AU controls are general-purpose and do not specify cryptocurrency transaction-level audit event requirements."
    },
    {
        "id": "2.04.2",
        "title": "Audit Logs — Level 2 Tamper-Evident Log Storage and Alert Generation",
        "controls": ["AU-09", "AU-10", "AU-06", "SI-04", "IR-06"],
        "coverage_pct": 75,
        "rationale": "AU-09 requires protection of audit information and audit tools from modification; AU-10 provides non-repudiation; AU-06 requires audit review and analysis with alerts; SI-04 requires monitoring with alert generation; IR-06 covers incident reporting. Together these address CCSS Level 2 requirements for tamper-evident log storage and automated alert generation on suspicious events.",
        "gaps": "CCSS Level 2 requires that suspicious activity in the Trusted Environment (unusual transaction patterns, failed authentication attempts, off-hours access) generate real-time alerts for security personnel to triage. Cryptocurrency-specific suspicious activity patterns — such as anomalous transaction volumes, unexpected wallet address additions, or attempted cold storage access — require domain-specific detection rules not specified in NIST monitoring controls."
    },
    {
        "id": "2.04.3",
        "title": "Audit Logs — Level 3 One-Year Retention, SIEM Integration, and Blockchain Event Monitoring",
        "controls": ["AU-11", "AU-06", "SI-04", "AU-09"],
        "coverage_pct": 65,
        "rationale": "AU-11 requires audit record retention for defined periods (CCSS requires minimum one year); AU-06 mandates audit review analysis and reporting; SI-04 requires continuous monitoring; AU-09 protects audit information. These controls address the CCSS Level 3 requirements for one-year log retention and active security monitoring.",
        "gaps": "CCSS Level 3 requires SIEM integration that monitors not only system events but also blockchain wallet address activity and smart contract state changes, enabling correlation between on-chain events and internal Trusted Environment activity. Blockchain-native event monitoring and correlation with traditional SIEM logs is a cryptocurrency-specific capability not contemplated by NIST audit and monitoring controls."
    },
]


def compute_summary(clauses):
    """Compute summary statistics from clause data."""
    total = len(clauses)
    full_count = sum(1 for c in clauses if c["coverage_pct"] >= 85)
    substantial_count = sum(1 for c in clauses if 65 <= c["coverage_pct"] <= 84)
    partial_count = sum(1 for c in clauses if 40 <= c["coverage_pct"] <= 64)
    weak_count = sum(1 for c in clauses if 1 <= c["coverage_pct"] <= 39)
    none_count = sum(1 for c in clauses if c["coverage_pct"] == 0)

    avg = round(sum(c["coverage_pct"] for c in clauses) / total, 1) if total > 0 else 0.0

    return {
        "total_clauses": total,
        "average_coverage": avg,
        "full_count": full_count,
        "substantial_count": substantial_count,
        "partial_count": partial_count,
        "weak_count": weak_count,
        "none_count": none_count,
    }


def main():
    summary = compute_summary(CLAUSES)

    output = {
        "$schema": "../schema/framework-coverage.schema.json",
        "framework_id": "ccss_v9",
        "framework_name": "CryptoCurrency Security Standard (CCSS) v9.0",
        "metadata": {
            "source": "SP800-53v5_Control_Mappings",
            "version": "1.0",
            "disclaimer": (
                "Based on publicly available CCSS v9.0 documentation and expert analysis. "
                "CCSS has cryptocurrency-specific requirements that extend substantially beyond "
                "SP 800-53 scope, particularly in blockchain-native key generation ceremonies, "
                "cold storage operations, multi-signature wallet architecture, proof of reserve "
                "attestation, and smart contract security auditing. Coverage percentages reflect "
                "how well generic NIST controls address CCSS intent; most gaps require "
                "cryptocurrency-specific procedural and technical controls. "
                "Validate with qualified CCSS auditors (CCSSA credential) for compliance use."
            ),
            "jurisdictions": ["GLOBAL"],
            "applicability_type": "market_driven",
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

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Written: {OUTPUT_PATH}")
    print(f"Total clauses: {summary['total_clauses']}")
    print(f"Average coverage: {summary['average_coverage']}%")
    print(f"  Full (85-100%):         {summary['full_count']}")
    print(f"  Substantial (65-84%):   {summary['substantial_count']}")
    print(f"  Partial (40-64%):       {summary['partial_count']}")
    print(f"  Weak (1-39%):           {summary['weak_count']}")
    print(f"  None (0%):              {summary['none_count']}")


if __name__ == "__main__":
    main()
