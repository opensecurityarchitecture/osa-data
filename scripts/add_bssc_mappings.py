#!/usr/bin/env python3
"""
Generate BSSC (Blockchain Security Standards Council) framework coverage JSON.

BSSC was founded in May 2025 by Anchorage Digital, Coinbase, Kraken, Fireblocks,
Halborn, OpenZeppelin, and other leading blockchain security firms.

Four standards published:
  NOS  - Node Operation Standard
         Covers blockchain node security, software supply chain integrity,
         consensus client hardening, peer network protection, and operational
         resilience for validator/full-node infrastructure.

  TIS  - Token Integration Standard
         Covers digital asset integration, smart-contract governance, token
         standard compliance, bridge/oracle security, and configuration
         management for asset-facing components.

  KMS  - Key Management Standard
         Covers cryptographic key generation, storage (HSM / MPC / cold),
         block proposal signing, wallet custody, key rotation, and recovery.

  GSP  - General Security & Privacy Standard
         Covers baseline risk management, security governance, personnel
         security, supply-chain risk, incident management, and privacy
         obligations for blockchain entities.

Output: data/framework-coverage/bssc.json

Usage:
    python3 scripts/add_bssc_mappings.py
"""

import json
import math
import os

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "framework-coverage", "bssc.json"
)

# ============================================================
# CLAUSE DEFINITIONS
# Each clause maps to the BSSC standard section it represents.
# Controls are NIST 800-53 Rev 5.
# coverage_pct: honest % of the clause addressable by SP 800-53.
# Blockchain-native requirements (consensus participation, block
# proposal security, smart-contract bytecode integrity, MPC
# threshold signing, on-chain governance) have limited NIST
# equivalents and are scored conservatively.
# ============================================================

CLAUSES = [

    # ================================================================
    # NOS — Node Operation Standard
    # ================================================================
    {
        "id": "NOS-01",
        "title": "Node Infrastructure Governance and Policy",
        "controls": ["PL-01", "PL-02", "PM-01", "PM-09", "CA-01"],
        "coverage_pct": 82,
        "rationale": (
            "PL-01 and PL-02 establish security planning policy and system security plans "
            "applicable to node infrastructure. PM-01 and PM-09 provide the programmatic "
            "governance framework for managing node operations as a risk-managed programme. "
            "CA-01 covers assessment policy that supports continuous node security assurance."
        ),
        "gaps": (
            "NIST does not address blockchain-specific governance requirements such as "
            "validator set management, staking governance, or on-chain upgrade participation "
            "policies that NOS requires operators to document and enforce."
        )
    },
    {
        "id": "NOS-02",
        "title": "Node Software Integrity and Supply Chain",
        "controls": ["SA-10", "SA-11", "SR-03", "SR-04", "SI-07", "CM-14"],
        "coverage_pct": 78,
        "rationale": (
            "SA-10 addresses developer configuration management including integrity "
            "verification of software artefacts. SA-11 covers security testing in the "
            "development lifecycle. SR-03 and SR-04 address supply chain controls and "
            "provenance of components. SI-07 enforces software and firmware integrity "
            "checking at the node level."
        ),
        "gaps": (
            "NOS requires cryptographic verification of consensus client binaries against "
            "published checksums from client teams (e.g. Geth, Lighthouse, Prysm), "
            "reproducible build verification, and signing of client releases — these are "
            "blockchain-ecosystem specifics beyond NIST supply-chain controls."
        )
    },
    {
        "id": "NOS-03",
        "title": "Consensus Client Configuration Hardening",
        "controls": ["CM-02", "CM-06", "CM-07", "CM-08", "SI-02"],
        "coverage_pct": 75,
        "rationale": (
            "CM-02 mandates baseline configuration management for node software. CM-06 "
            "establishes configuration settings aligned to security requirements. CM-07 "
            "enforces least-functionality by disabling unnecessary services and ports. "
            "CM-08 provides the component inventory needed to track client versions. "
            "SI-02 ensures timely patching of consensus client vulnerabilities."
        ),
        "gaps": (
            "Blockchain-specific hardening requirements such as disabling JSON-RPC exposure, "
            "configuring attestation subnet subscriptions, rate-limiting gossip traffic, and "
            "setting appropriate fee-recipient addresses are not addressed by NIST configuration "
            "management controls."
        )
    },
    {
        "id": "NOS-04",
        "title": "Peer Network Security and Isolation",
        "controls": ["SC-07", "SC-05", "SC-08", "AC-04", "SC-20", "SC-21"],
        "coverage_pct": 70,
        "rationale": (
            "SC-07 boundary protection controls govern network segmentation for node peer "
            "connections. SC-05 addresses denial-of-service protection relevant to eclipse "
            "and flooding attacks. SC-08 covers transmission confidentiality and integrity "
            "for peer communications. AC-04 enforces information flow policies between node "
            "network segments and administrative interfaces."
        ),
        "gaps": (
            "NOS addresses blockchain-specific threats including eclipse attacks, peer "
            "discovery poisoning, and libp2p/devp2p protocol hardening. NIST network "
            "controls do not address consensus-layer peer scoring, peer whitelisting "
            "strategies, or gossip protocol security specific to blockchain networks."
        )
    },
    {
        "id": "NOS-05",
        "title": "Node Access Control and Authentication",
        "controls": ["AC-02", "AC-03", "AC-06", "IA-02", "IA-05", "AC-17"],
        "coverage_pct": 85,
        "rationale": (
            "AC-02 and AC-03 establish account management and access enforcement for node "
            "administrative interfaces. AC-06 mandates least-privilege for node operators. "
            "IA-02 requires multi-factor authentication for privileged access to node "
            "management. IA-05 governs authenticator management including SSH key controls. "
            "AC-17 addresses secure remote access to node infrastructure."
        ),
        "gaps": (
            "NOS requires role separation between validator key custodians and node operators, "
            "and restricts who can access execution-layer RPC endpoints — nuances not "
            "captured by NIST access control families which lack blockchain-specific "
            "role definitions."
        )
    },
    {
        "id": "NOS-06",
        "title": "Node Monitoring and Anomaly Detection",
        "controls": ["AU-02", "AU-06", "AU-12", "SI-04", "SI-05"],
        "coverage_pct": 80,
        "rationale": (
            "AU-02 and AU-12 establish audit event selection and generation for node "
            "operations. AU-06 covers audit review and alerting. SI-04 provides "
            "information-system monitoring including detection of anomalous node behaviour. "
            "SI-05 ensures security alerts and threat intelligence are fed into node "
            "monitoring pipelines."
        ),
        "gaps": (
            "NOS requires blockchain-specific monitoring including missed block/attestation "
            "alerts, slashing condition detection, validator client version divergence "
            "monitoring, and mempool anomaly detection — none of which are addressed by "
            "NIST audit and monitoring controls."
        )
    },
    {
        "id": "NOS-07",
        "title": "Node Resilience, Backup, and Recovery",
        "controls": ["CP-02", "CP-09", "CP-10", "CP-07", "CP-08"],
        "coverage_pct": 78,
        "rationale": (
            "CP-02 establishes the contingency plan covering node failure and recovery "
            "scenarios. CP-09 mandates backup of node state and configuration data. "
            "CP-10 covers system recovery and reconstitution following a node outage. "
            "CP-07 and CP-08 address alternate processing sites and telecommunications "
            "redundancy for node availability."
        ),
        "gaps": (
            "NOS requires specific slashing protection database backups, anti-slashing "
            "double-signing controls during failover, and blockchain state synchronisation "
            "procedures that are unique to consensus participant recovery and not covered "
            "by NIST contingency planning."
        )
    },
    {
        "id": "NOS-08",
        "title": "Validator Key Operational Security",
        "controls": ["SC-12", "SC-13", "IA-05", "AC-06", "MP-04"],
        "coverage_pct": 60,
        "rationale": (
            "SC-12 and SC-13 provide cryptographic key establishment and management "
            "requirements. IA-05 covers authenticator (credential) management applicable "
            "to validator key handling. AC-06 enforces least-privilege around key access. "
            "MP-04 addresses physical media protection of offline key material."
        ),
        "gaps": (
            "NOS requires specific EIP-2335 keystore handling, BLS12-381 key derivation "
            "procedures, slashing protection databases (EIP-3076), remote signer protocol "
            "security (e.g. web3signer), and distributed validator technology (DVT) "
            "operational controls — none of which have NIST equivalents."
        )
    },
    {
        "id": "NOS-09",
        "title": "Node Physical and Environmental Security",
        "controls": ["PE-02", "PE-03", "PE-06", "PE-11", "PE-12", "PE-14"],
        "coverage_pct": 88,
        "rationale": (
            "PE-02 through PE-14 comprehensively address physical access control, "
            "monitoring, power equipment, and environmental controls for data centre "
            "and colocation facilities hosting blockchain node infrastructure. These "
            "controls directly map to NOS physical security requirements for validator "
            "and full-node deployments."
        ),
        "gaps": (
            "NOS physical security requirements are largely well-addressed by NIST PE "
            "controls. Remaining gaps relate to blockchain-specific requirements for "
            "air-gapped signing environments and tamper-evidence for hardware security "
            "module enclosures used in validator key storage."
        )
    },
    {
        "id": "NOS-10",
        "title": "Node Vulnerability Management and Patching",
        "controls": ["RA-05", "SI-02", "CA-07", "CM-03", "CM-04"],
        "coverage_pct": 83,
        "rationale": (
            "RA-05 mandates vulnerability scanning of node infrastructure. SI-02 requires "
            "flaw remediation with defined timelines. CA-07 provides continuous monitoring "
            "including security-relevant configuration changes. CM-03 and CM-04 govern "
            "change control and impact analysis for node software updates."
        ),
        "gaps": (
            "NOS requires tracking of consensus client CVEs published by individual client "
            "teams outside standard CVE databases, coordinated upgrade windows for network "
            "upgrades (hard forks), and emergency patching procedures that must maintain "
            "network participation — operational constraints not addressed by NIST."
        )
    },

    # ================================================================
    # TIS — Token Integration Standard
    # ================================================================
    {
        "id": "TIS-01",
        "title": "Token Integration Governance and Risk Assessment",
        "controls": ["RA-01", "RA-03", "PM-09", "PL-01", "CA-01"],
        "coverage_pct": 75,
        "rationale": (
            "RA-01 and RA-03 establish risk assessment policy and procedures applicable "
            "to evaluating digital asset integration risks. PM-09 provides the enterprise "
            "risk management framework under which token integration decisions are made. "
            "PL-01 covers security planning policy that should encompass asset-facing "
            "systems. CA-01 addresses assessment and authorisation policy."
        ),
        "gaps": (
            "TIS requires blockchain-specific risk assessment covering token standard "
            "compliance (ERC-20/721/1155/4626), smart contract auditability, protocol "
            "risk (liquidity, governance attacks), and on-chain asset custody risk. "
            "NIST risk assessment frameworks do not address these digital asset-specific "
            "risk dimensions."
        )
    },
    {
        "id": "TIS-02",
        "title": "Smart Contract Security and Auditing",
        "controls": ["SA-11", "CA-02", "CA-08", "RA-05", "SR-06"],
        "coverage_pct": 55,
        "rationale": (
            "SA-11 covers developer security testing applicable to smart contract code "
            "review. CA-02 security assessments can encompass smart contract audits. "
            "CA-08 penetration testing requirements apply to contract functionality "
            "testing. RA-05 vulnerability scanning is analogous to automated contract "
            "analysis. SR-06 addresses supplier assessments relevant to third-party "
            "contract auditors."
        ),
        "gaps": (
            "TIS requires formal smart contract audits by qualified blockchain security "
            "firms, automated analysis with tools such as Slither, Mythril, and Echidna, "
            "formal verification for high-value contracts, and economic/game-theoretic "
            "security analysis. These are blockchain-specific assurance techniques "
            "absent from NIST."
        )
    },
    {
        "id": "TIS-03",
        "title": "Token Standard Compliance and Configuration",
        "controls": ["CM-06", "CM-07", "SA-04", "SA-08"],
        "coverage_pct": 35,
        "rationale": (
            "CM-06 configuration settings and CM-07 least-functionality requirements "
            "partially address token contract configuration (e.g. admin key controls, "
            "pause functions). SA-04 acquisition requirements apply to token standard "
            "specifications. SA-08 security engineering principles map to secure token "
            "design. Coverage is limited due to the blockchain-native nature of the "
            "requirement."
        ),
        "gaps": (
            "TIS compliance with ERC-20, ERC-721, ERC-1155, ERC-4626, and other token "
            "standards; proxy upgrade pattern security (UUPS vs. transparent proxy); "
            "access control role configuration (OpenZeppelin AccessControl); and "
            "timelock governance have no NIST equivalents."
        )
    },
    {
        "id": "TIS-04",
        "title": "Bridge and Cross-Chain Integration Security",
        "controls": ["SC-07", "AC-04", "RA-03", "SA-11", "IR-04"],
        "coverage_pct": 42,
        "rationale": (
            "SC-07 boundary protection applies to bridge ingress/egress points between "
            "chains. AC-04 information flow enforcement is relevant to cross-chain message "
            "validation. RA-03 risk assessment covers bridge economic risks. SA-11 "
            "security testing applies to bridge contract audits. IR-04 incident handling "
            "is essential given the history of bridge exploits."
        ),
        "gaps": (
            "Bridge security is a uniquely blockchain domain: validator set compromise, "
            "light-client proof validation, optimistic fraud proof windows, canonical "
            "message relay security, and re-entrancy across chains are not addressable "
            "with NIST controls. Bridge exploits represent the largest category of "
            "blockchain losses and require specialised controls."
        )
    },
    {
        "id": "TIS-05",
        "title": "Oracle Security and Price Feed Integrity",
        "controls": ["SI-07", "SI-04", "RA-03", "SC-08", "AU-10"],
        "coverage_pct": 38,
        "rationale": (
            "SI-07 software and firmware integrity checking partially addresses oracle "
            "data integrity. SI-04 monitoring applies to oracle deviation detection. "
            "RA-03 risk assessment covers oracle manipulation risk. SC-08 transmission "
            "integrity applies to oracle data feeds. AU-10 non-repudiation partially "
            "addresses oracle data provenance."
        ),
        "gaps": (
            "Oracle security requirements including Time-Weighted Average Price (TWAP) "
            "manipulation resistance, multi-source aggregation (e.g. Chainlink, Pyth), "
            "heartbeat and deviation thresholds, circuit breakers, and on-chain "
            "price sanity checks are entirely blockchain-native and absent from NIST."
        )
    },
    {
        "id": "TIS-06",
        "title": "DeFi Protocol Integration Controls",
        "controls": ["RA-03", "SA-04", "CA-02", "IR-01", "SR-05"],
        "coverage_pct": 32,
        "rationale": (
            "RA-03 risk assessment applies to DeFi protocol integration decisions. "
            "SA-04 acquisition requirements cover protocol selection criteria. "
            "CA-02 assessments apply to due diligence on protocol security. "
            "IR-01 incident response policy is essential given DeFi exploit risk. "
            "SR-05 supplier assessments apply to evaluating DeFi protocol audits."
        ),
        "gaps": (
            "TIS DeFi controls covering MEV exposure, flash loan attack surfaces, "
            "liquidity pool concentration risk, governance token attack vectors, "
            "sandwich attack protections, and slippage tolerance configuration "
            "are entirely outside the scope of NIST 800-53."
        )
    },
    {
        "id": "TIS-07",
        "title": "Token Custody and Asset Segregation",
        "controls": ["AC-06", "SC-12", "MP-04", "AC-03", "AU-09"],
        "coverage_pct": 62,
        "rationale": (
            "AC-06 least privilege directly applies to token custody permission models. "
            "SC-12 key management governs the cryptographic keys controlling token "
            "custody. MP-04 media protection covers offline cold storage of private keys. "
            "AC-03 access enforcement applies to custody platform authorisation. "
            "AU-09 audit protection ensures custody transaction logs are tamper-evident."
        ),
        "gaps": (
            "TIS requires specific asset segregation controls including proof-of-reserves "
            "mechanisms, multi-party approval thresholds, withdrawal allow-listing, "
            "and on-chain accounting reconciliation — blockchain-native requirements "
            "that supplement but are not covered by NIST access and key management."
        )
    },
    {
        "id": "TIS-08",
        "title": "Smart Contract Upgrade and Governance",
        "controls": ["CM-03", "CM-05", "SA-10", "CA-06", "PL-02"],
        "coverage_pct": 58,
        "rationale": (
            "CM-03 configuration change control maps to contract upgrade governance. "
            "CM-05 access restrictions for change enforce upgrade authorisation. "
            "SA-10 configuration management in development covers upgrade testing. "
            "CA-06 plan of action and milestones applies to post-upgrade assurance. "
            "PL-02 system security plan should document upgrade procedures."
        ),
        "gaps": (
            "TIS requires timelock enforcement (minimum delay before upgrade execution), "
            "on-chain multisig governance (Gnosis Safe or equivalent), transparent "
            "proxy storage collision checking, and community veto mechanisms — all "
            "blockchain-specific upgrade controls absent from NIST."
        )
    },

    # ================================================================
    # KMS — Key Management Standard
    # ================================================================
    {
        "id": "KMS-01",
        "title": "Cryptographic Key Management Policy",
        "controls": ["SC-12", "SC-13", "SC-17", "PL-01", "CA-01"],
        "coverage_pct": 88,
        "rationale": (
            "SC-12 directly requires a cryptographic key management policy including "
            "key generation, distribution, storage, access, retirement, and destruction. "
            "SC-13 mandates use of approved cryptographic algorithms. SC-17 covers PKI "
            "certificate management. PL-01 and CA-01 provide the policy framework "
            "within which key management policy sits."
        ),
        "gaps": (
            "KMS requires policy coverage for blockchain-specific key types (BLS12-381 "
            "for Ethereum validators, secp256k1 for signing, Ed25519 for Solana), "
            "derivation path standards (BIP-39/44/32 HD wallets), and threshold "
            "cryptography governance — areas where NIST key management policy "
            "provides a useful framework but lacks domain-specific guidance."
        )
    },
    {
        "id": "KMS-02",
        "title": "Key Generation and Randomness",
        "controls": ["SC-12", "SC-13", "SA-08"],
        "coverage_pct": 72,
        "rationale": (
            "SC-12 covers key generation requirements. SC-13 mandates FIPS-approved "
            "random number generation for cryptographic operations. SA-08 security "
            "engineering principles include use of approved entropy sources. Together "
            "these address the core requirement for secure, high-entropy key generation."
        ),
        "gaps": (
            "KMS requires blockchain-specific entropy hardening for key generation in "
            "cold environments, BLS key derivation from EIP-2333 seed, mnemonic phrase "
            "generation using CSPRNG with WORDLIST verification, and air-gapped ceremony "
            "procedures for genesis/bootstrap keys not covered by NIST."
        )
    },
    {
        "id": "KMS-03",
        "title": "Hardware Security Module (HSM) and Secure Enclave Usage",
        "controls": ["SC-12", "SC-13", "PE-03", "MP-04", "SA-04"],
        "coverage_pct": 80,
        "rationale": (
            "SC-12 requires key storage in hardware security modules for high-assurance "
            "environments. SC-13 mandates FIPS 140-2/3 validated cryptographic modules. "
            "PE-03 physical access controls protect HSM equipment. MP-04 covers media "
            "protection for HSM backup tokens. SA-04 acquisition requirements apply to "
            "HSM procurement and acceptance testing."
        ),
        "gaps": (
            "KMS HSM requirements specific to blockchain include support for secp256k1 "
            "and BLS12-381 curves (not all HSMs support these), MPC-CMP protocol support, "
            "cloud HSM integration for remote signing (AWS CloudHSM, Azure Dedicated HSM), "
            "and HSM cluster configuration for validator signing."
        )
    },
    {
        "id": "KMS-04",
        "title": "Multi-Party Computation (MPC) and Threshold Signing",
        "controls": ["SC-12", "AC-05", "AC-06", "IA-03"],
        "coverage_pct": 40,
        "rationale": (
            "SC-12 key management policy can encompass threshold key schemes. AC-05 "
            "separation of duties maps to MPC share distribution across parties. "
            "AC-06 least privilege applies to MPC participant authorisation. IA-03 "
            "device identification applies to MPC share holder authentication."
        ),
        "gaps": (
            "MPC/TSS (Threshold Signature Schemes) such as GG18, CGGMP21, FROST, and "
            "BLS threshold aggregation are advanced cryptographic primitives with no "
            "NIST 800-53 equivalent. Requirements for share generation ceremonies, "
            "resharing protocols, key refresh cycles, and MPC node security are "
            "entirely blockchain/digital-asset native."
        )
    },
    {
        "id": "KMS-05",
        "title": "Cold Storage and Air-Gapped Key Custody",
        "controls": ["MP-04", "MP-05", "PE-03", "AC-06", "SC-12"],
        "coverage_pct": 75,
        "rationale": (
            "MP-04 and MP-05 directly address physical media protection and transport "
            "of offline key storage media. PE-03 physical access controls apply to "
            "cold storage vaults. AC-06 least privilege limits access to cold key "
            "material. SC-12 key management policy covers offline key custody procedures."
        ),
        "gaps": (
            "KMS cold storage requirements for blockchain include hardware wallet "
            "device provisioning and verification (Ledger, Trezor, Coldcard), "
            "metal seed phrase backup media, Shamir's Secret Sharing for seed "
            "backup, and multi-jurisdiction geographic distribution of key shares — "
            "requirements not addressed by NIST media protection controls."
        )
    },
    {
        "id": "KMS-06",
        "title": "Key Access Control and Multi-Signature Authorisation",
        "controls": ["AC-02", "AC-03", "AC-05", "AC-06", "IA-02", "IA-05"],
        "coverage_pct": 82,
        "rationale": (
            "AC-02 account management, AC-03 access enforcement, and AC-05 separation "
            "of duties collectively address who can access and use cryptographic keys. "
            "AC-06 least privilege restricts key usage to authorised operations. IA-02 "
            "MFA and IA-05 authenticator management apply to key access authentication. "
            "Together these cover the authorisation layer of KMS."
        ),
        "gaps": (
            "KMS requires multi-signature (multisig) transaction policies with M-of-N "
            "approval thresholds, time-delay controls on high-value transactions, "
            "allow-listing of destination addresses, and quorum rules for key usage — "
            "controls that supplement but are not fully addressed by NIST access "
            "control families."
        )
    },
    {
        "id": "KMS-07",
        "title": "Key Rotation, Revocation, and Lifecycle Management",
        "controls": ["SC-12", "IA-05", "CM-03", "CA-05"],
        "coverage_pct": 78,
        "rationale": (
            "SC-12 covers the complete cryptographic key lifecycle including rotation and "
            "revocation requirements. IA-05 authenticator management includes credential "
            "rotation schedules. CM-03 configuration change control applies to key "
            "rotation procedures. CA-05 plans of action track key rotation completion."
        ),
        "gaps": (
            "KMS requires blockchain-specific rotation considerations: voluntary validator "
            "key exit and withdrawal credential rotation (ETH2), BLS key migration, "
            "smart contract ownership transfer procedures, and multisig signatory "
            "rotation — processes with blockchain-native dependencies not covered "
            "by NIST lifecycle controls."
        )
    },
    {
        "id": "KMS-08",
        "title": "Block Proposal and Signing Security",
        "controls": ["SC-12", "SC-13", "IA-05", "AU-10"],
        "coverage_pct": 35,
        "rationale": (
            "SC-12 and SC-13 provide the cryptographic foundation for signing operations. "
            "IA-05 authenticator management applies to signing key protection. AU-10 "
            "non-repudiation covers the integrity of signed block proposals. Coverage "
            "is limited because block proposal is a fundamentally blockchain-specific "
            "operation."
        ),
        "gaps": (
            "Block proposal security requirements — preventing double signing (equivocation), "
            "managing proposer boost and attestation timing, remote signer protocol security "
            "(web3signer EIP-3030), slashing database synchronisation, and distributed "
            "validator protocol (DVT) liveness — have no NIST 800-53 equivalents."
        )
    },
    {
        "id": "KMS-09",
        "title": "Wallet Custody Architecture and Controls",
        "controls": ["SC-12", "AC-06", "AC-03", "MP-04", "PE-03", "AU-09"],
        "coverage_pct": 68,
        "rationale": (
            "SC-12 key management encompasses wallet key protection architecture. "
            "AC-06 least privilege applies to wallet access permission models. "
            "AC-03 access enforcement covers withdrawal authorisation policies. "
            "MP-04 media protection applies to hardware wallet devices. "
            "AU-09 audit protection ensures wallet transaction audit trails are "
            "tamper-evident and non-repudiable."
        ),
        "gaps": (
            "KMS wallet custody controls require hot/warm/cold tiering with defined "
            "transaction limits per tier, allow-list management, proof-of-reserves "
            "demonstration capability, and integration with custodian certification "
            "frameworks (SOC 1 Type II for custodians) — requirements beyond NIST scope."
        )
    },
    {
        "id": "KMS-10",
        "title": "Key Backup, Recovery, and Disaster Recovery",
        "controls": ["CP-09", "CP-10", "SC-12", "MP-04", "MP-05"],
        "coverage_pct": 78,
        "rationale": (
            "CP-09 backup and CP-10 system recovery directly address key backup and "
            "recovery requirements. SC-12 key management includes key recovery procedures. "
            "MP-04 and MP-05 cover offline backup media protection and transport. "
            "Together these establish a comprehensive framework for key recovery planning."
        ),
        "gaps": (
            "KMS recovery requirements include blockchain-specific procedures for "
            "reconstructing keys from Shamir shares or BIP-39 mnemonics, re-keying "
            "smart contracts after key compromise, and validator exit and re-entry "
            "procedures following custody failure — not addressed by NIST."
        )
    },

    # ================================================================
    # GSP — General Security & Privacy Standard
    # ================================================================
    {
        "id": "GSP-01",
        "title": "Information Security Governance and Leadership",
        "controls": ["PM-01", "PM-02", "PM-09", "PL-01", "PL-02", "CA-06"],
        "coverage_pct": 88,
        "rationale": (
            "PM-01 establishes the information security programme and PM-02 defines senior "
            "information security officer responsibilities. PM-09 covers enterprise risk "
            "management frameworks. PL-01 and PL-02 establish security planning policy "
            "and system security plans. CA-06 addresses security authorisation. Together "
            "these comprehensively address GSP governance requirements."
        ),
        "gaps": (
            "GSP includes blockchain-specific governance requirements: board-level "
            "digital asset risk oversight, CISO responsibility for on-chain risk, "
            "and governance over staking and validator operations that traditional "
            "NIST governance controls do not specifically address."
        )
    },
    {
        "id": "GSP-02",
        "title": "Risk Assessment and Management Framework",
        "controls": ["RA-01", "RA-02", "RA-03", "RA-05", "RA-07", "PM-09"],
        "coverage_pct": 85,
        "rationale": (
            "RA-01 through RA-07 comprehensively cover risk assessment policy, asset "
            "identification and valuation, risk assessment methodology, vulnerability "
            "identification, and risk response. PM-09 provides the enterprise risk "
            "management framework. These controls address the majority of GSP risk "
            "management requirements."
        ),
        "gaps": (
            "GSP requires blockchain-specific threat modelling covering consensus failure, "
            "protocol-level risks, smart contract risk, key custody risk, and regulatory "
            "risk from evolving digital asset regulation. NIST risk assessment is "
            "general-purpose and does not address blockchain-native threat categories."
        )
    },
    {
        "id": "GSP-03",
        "title": "Security Awareness and Training",
        "controls": ["AT-01", "AT-02", "AT-03", "AT-04"],
        "coverage_pct": 82,
        "rationale": (
            "AT-01 establishes awareness and training policy. AT-02 covers role-based "
            "security awareness. AT-03 requires specialised training for roles with "
            "significant security responsibilities. AT-04 tracks training completion. "
            "These controls directly map to GSP workforce security training requirements."
        ),
        "gaps": (
            "GSP requires blockchain-specific security training covering social engineering "
            "targeting crypto personnel (SIM swap, phishing, physical threats to key holders), "
            "operational security for individuals holding high-value keys, and secure "
            "communications practices for distributed teams — not addressed by NIST AT controls."
        )
    },
    {
        "id": "GSP-04",
        "title": "Personnel Security and Background Screening",
        "controls": ["PS-01", "PS-02", "PS-03", "PS-06", "PS-07"],
        "coverage_pct": 85,
        "rationale": (
            "PS-01 establishes personnel security policy. PS-02 defines position "
            "categorisation based on risk. PS-03 mandates personnel screening prior "
            "to access. PS-06 addresses agreements for personnel with security "
            "responsibilities. PS-07 covers third-party personnel security. These "
            "directly address GSP personnel security screening requirements."
        ),
        "gaps": (
            "GSP requires enhanced vetting for individuals with access to private keys "
            "controlling significant digital assets, including enhanced financial "
            "background checks and ongoing monitoring of key custodians — requirements "
            "that go beyond standard NIST PS screening criteria."
        )
    },
    {
        "id": "GSP-05",
        "title": "Incident Detection, Response, and Reporting",
        "controls": ["IR-01", "IR-02", "IR-04", "IR-05", "IR-06", "IR-08"],
        "coverage_pct": 83,
        "rationale": (
            "IR-01 establishes incident response policy. IR-02 covers training. "
            "IR-04 defines incident handling procedures including containment and "
            "eradication. IR-05 tracks incident monitoring and reporting. IR-06 "
            "addresses regulatory and law enforcement reporting. IR-08 covers the "
            "incident response plan and its maintenance."
        ),
        "gaps": (
            "GSP incident response for blockchain entities requires specific procedures "
            "for key compromise response (rapid asset migration), smart contract exploit "
            "response (pause and upgrade), and coordination with blockchain security "
            "firms and chain emergency response teams — procedures not addressed by "
            "NIST incident response controls."
        )
    },
    {
        "id": "GSP-06",
        "title": "Business Continuity and Operational Resilience",
        "controls": ["CP-01", "CP-02", "CP-04", "CP-09", "CP-10", "CP-11"],
        "coverage_pct": 85,
        "rationale": (
            "CP-01 establishes contingency planning policy. CP-02 requires a contingency "
            "plan addressing service disruption. CP-04 mandates contingency plan testing. "
            "CP-09 covers backup procedures. CP-10 addresses system recovery. CP-11 covers "
            "alternate communications. Together these comprehensively address GSP "
            "operational resilience requirements."
        ),
        "gaps": (
            "GSP resilience requirements include blockchain-specific continuity scenarios: "
            "consensus protocol upgrade (hard fork) continuity, RPC provider failover, "
            "validator client diversity for network resilience, and custodian failover "
            "with key recovery — not addressed by NIST contingency planning."
        )
    },
    {
        "id": "GSP-07",
        "title": "Third-Party and Supply Chain Risk Management",
        "controls": ["SR-01", "SR-02", "SR-03", "SR-05", "SA-09", "SA-04"],
        "coverage_pct": 82,
        "rationale": (
            "SR-01 and SR-02 establish supply chain risk management policy and strategy. "
            "SR-03 covers supply chain controls and plans. SR-05 addresses acquisition "
            "strategies and tools. SA-09 covers external system services and third-party "
            "risk. SA-04 addresses acquisition requirements for security. These collectively "
            "address the majority of GSP third-party risk management requirements."
        ),
        "gaps": (
            "GSP requires blockchain-specific third-party risk covering node infrastructure "
            "providers, blockchain RPC providers (Infura, Alchemy, QuickNode), bridge "
            "protocol dependencies, DeFi protocol integrations, and oracle providers — "
            "categories of supply chain risk unique to blockchain operations."
        )
    },
    {
        "id": "GSP-08",
        "title": "Vulnerability Disclosure and Bug Bounty",
        "controls": ["RA-05", "SI-02", "CA-08", "IR-06", "SA-11"],
        "coverage_pct": 65,
        "rationale": (
            "RA-05 vulnerability scanning and SI-02 flaw remediation cover the technical "
            "identification and remediation lifecycle. CA-08 penetration testing relates "
            "to the testing that surfaces vulnerabilities subject to disclosure. IR-06 "
            "incident reporting covers responsible disclosure coordination. SA-11 "
            "developer security testing relates to pre-disclosure internal testing."
        ),
        "gaps": (
            "GSP requires blockchain-specific vulnerability disclosure programmes covering "
            "smart contract bug bounties (Immunefi, HackerOne), coordinated disclosure "
            "with blockchain security firms, emergency pause mechanism activation, and "
            "public disclosure timelines — practices not addressed by NIST controls."
        )
    },
    {
        "id": "GSP-09",
        "title": "Data Protection and Privacy",
        "controls": ["PT-01", "PT-02", "PT-03", "PT-05", "SC-28", "MP-06"],
        "coverage_pct": 75,
        "rationale": (
            "PT-01 establishes privacy policy and PT-02 covers authority and purpose "
            "specification for data processing. PT-03 addresses data actions and "
            "processing transparency. PT-05 covers privacy notice requirements. "
            "SC-28 protects data at rest. MP-06 covers media sanitisation. Together "
            "these address standard data protection requirements in GSP."
        ),
        "gaps": (
            "GSP privacy requirements must address the public-ledger nature of blockchains "
            "where on-chain transaction data is inherently public, creating unique privacy "
            "obligations around chain analytics, address clustering, and GDPR compliance "
            "for entities processing personal data on-chain. These blockchain-native "
            "privacy challenges are not addressed by NIST PT controls."
        )
    },
    {
        "id": "GSP-10",
        "title": "Regulatory Compliance and AML/CFT Controls",
        "controls": ["CA-01", "CA-02", "PM-09", "RA-01", "AU-02"],
        "coverage_pct": 48,
        "rationale": (
            "CA-01 and CA-02 cover policy and assessment frameworks relevant to regulatory "
            "compliance programmes. PM-09 enterprise risk management applies to regulatory "
            "risk. RA-01 risk assessment policy encompasses compliance risk. AU-02 covers "
            "audit events relevant to transaction monitoring. Coverage is limited as "
            "AML/CFT is a compliance domain outside NIST's scope."
        ),
        "gaps": (
            "GSP requires Travel Rule compliance (FATF), transaction monitoring and "
            "sanctions screening (OFAC, EU restrictive measures), KYC/AML programme "
            "management, suspicious activity reporting (SARs), and blockchain analytics "
            "integration — regulatory obligations entirely outside NIST 800-53 scope."
        )
    },
    {
        "id": "GSP-11",
        "title": "Access Control and Identity Management",
        "controls": ["AC-01", "AC-02", "AC-03", "AC-05", "AC-06", "IA-01", "IA-02", "IA-05"],
        "coverage_pct": 90,
        "rationale": (
            "AC-01 through AC-06 comprehensively cover access control policy, account "
            "management, access enforcement, separation of duties, and least privilege. "
            "IA-01, IA-02, and IA-05 cover identification and authentication policy, "
            "MFA requirements, and authenticator management. These NIST controls "
            "directly and fully address GSP access control baseline requirements."
        ),
        "gaps": (
            "GSP access control for blockchain operations requires privileged access "
            "management for node operators distinct from key custodians, smart contract "
            "admin key access controls, and on-chain identity management considerations "
            "for decentralised applications — nuances not fully captured by NIST."
        )
    },
    {
        "id": "GSP-12",
        "title": "Logging, Audit, and Monitoring",
        "controls": ["AU-01", "AU-02", "AU-03", "AU-06", "AU-09", "AU-11", "SI-04"],
        "coverage_pct": 87,
        "rationale": (
            "AU-01 through AU-11 comprehensively address audit and accountability policy, "
            "event selection, record content, storage capacity, response to failures, "
            "audit review and reporting, audit record retention, and protection of audit "
            "information. SI-04 information system monitoring addresses continuous "
            "monitoring requirements. These controls strongly address GSP logging requirements."
        ),
        "gaps": (
            "GSP monitoring requirements for blockchain include on-chain event monitoring "
            "(contract events, large transfers, governance proposals), integration of "
            "blockchain analytics platforms (Chainalysis, TRM Labs), and immutable "
            "on-chain audit trail verification — dimensions not covered by NIST audit controls."
        )
    },
    {
        "id": "GSP-13",
        "title": "Encryption and Data-in-Transit Protection",
        "controls": ["SC-08", "SC-12", "SC-13", "SC-23", "SC-28"],
        "coverage_pct": 88,
        "rationale": (
            "SC-08 addresses transmission confidentiality and integrity for all data "
            "in transit. SC-12 and SC-13 govern cryptographic key management and "
            "approved cryptographic algorithms. SC-23 covers session authenticity. "
            "SC-28 addresses protection of data at rest. These controls broadly address "
            "GSP encryption requirements."
        ),
        "gaps": (
            "GSP cryptographic requirements for blockchain include end-to-end encryption "
            "of node communications using TLS 1.3 minimum, encrypted key material in "
            "transit between MPC parties, and confidential computing for key operations "
            "in cloud environments — areas where NIST provides the framework but "
            "lacks blockchain-specific implementation guidance."
        )
    },
    {
        "id": "GSP-14",
        "title": "Change Management and Configuration Control",
        "controls": ["CM-01", "CM-02", "CM-03", "CM-05", "CM-06", "CM-08"],
        "coverage_pct": 87,
        "rationale": (
            "CM-01 establishes configuration management policy. CM-02 maintains baseline "
            "configurations. CM-03 controls configuration changes. CM-05 enforces access "
            "restrictions for changes. CM-06 establishes configuration settings. CM-08 "
            "maintains the system component inventory. Together these comprehensively "
            "address GSP change management requirements."
        ),
        "gaps": (
            "GSP change management for blockchain entities must address smart contract "
            "upgrade coordination with users, protocol upgrade (hard fork) change "
            "management, and multi-sig governance for on-chain parameter changes — "
            "processes not addressed by NIST configuration management controls."
        )
    },
    {
        "id": "GSP-15",
        "title": "Penetration Testing and Security Assessments",
        "controls": ["CA-02", "CA-07", "CA-08", "RA-05", "SA-11"],
        "coverage_pct": 83,
        "rationale": (
            "CA-02 security assessments and CA-08 penetration testing directly require "
            "independent security testing of systems. CA-07 continuous monitoring "
            "complements periodic assessments. RA-05 vulnerability scanning provides "
            "automated coverage between manual assessments. SA-11 developer security "
            "testing ensures pre-deployment security assurance."
        ),
        "gaps": (
            "GSP penetration testing requirements for blockchain include smart contract "
            "audit and formal verification, economic security analysis (game theory), "
            "blockchain-specific red team exercises (key compromise simulation, "
            "on-chain governance attack simulation), and DeFi protocol stress testing — "
            "specialised assessment types not addressed by NIST."
        )
    },
]


def compute_summary(clauses):
    """Compute summary statistics from clause list."""
    total = len(clauses)
    if total == 0:
        return {
            "total_clauses": 0,
            "average_coverage": 0.0,
            "full_count": 0,
            "substantial_count": 0,
            "partial_count": 0,
            "weak_count": 0,
            "none_count": 0,
        }

    full = sum(1 for c in clauses if c["coverage_pct"] >= 85)
    substantial = sum(1 for c in clauses if 65 <= c["coverage_pct"] <= 84)
    partial = sum(1 for c in clauses if 40 <= c["coverage_pct"] <= 64)
    weak = sum(1 for c in clauses if 1 <= c["coverage_pct"] <= 39)
    none = sum(1 for c in clauses if c["coverage_pct"] == 0)

    avg = sum(c["coverage_pct"] for c in clauses) / total
    avg_rounded = round(avg, 1)

    return {
        "total_clauses": total,
        "average_coverage": avg_rounded,
        "full_count": full,
        "substantial_count": substantial,
        "partial_count": partial,
        "weak_count": weak,
        "none_count": none,
    }


def build_document():
    summary = compute_summary(CLAUSES)

    doc = {
        "$schema": "../schema/framework-coverage.schema.json",
        "framework_id": "bssc",
        "framework_name": "Blockchain Security Standards Council (BSSC) Standards",
        "metadata": {
            "source": "SP800-53v5_Control_Mappings",
            "version": "1.0",
            "disclaimer": (
                "Based on BSSC Node Operation Standard (NOS), Token Integration Standard "
                "(TIS), Key Management Standard (KMS), and General Security & Privacy "
                "Standard (GSP) (May 2025). BSSC standards are industry-led and cover "
                "blockchain-specific operational security requirements. Some "
                "blockchain-native requirements (consensus participation, block proposal "
                "security, token standard compliance) have limited SP 800-53 equivalents. "
                "Validate with qualified assessors for compliance/audit use."
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
    return doc


def main():
    doc = build_document()

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")

    summary = doc["summary"]
    print(f"{'='*60}")
    print(f"BSSC Framework Coverage Mapping")
    print(f"{'='*60}")
    print(f"Output: {OUTPUT_PATH}")
    print(f"{'='*60}")
    print(f"Total clauses:        {summary['total_clauses']}")
    print(f"Average coverage:     {summary['average_coverage']}%")
    print(f"{'='*60}")
    print(f"Full (85-100%):       {summary['full_count']}")
    print(f"Substantial (65-84%): {summary['substantial_count']}")
    print(f"Partial (40-64%):     {summary['partial_count']}")
    print(f"Weak (1-39%):         {summary['weak_count']}")
    print(f"None (0%):            {summary['none_count']}")
    print(f"{'='*60}")

    # Standard breakdown
    nos = [c for c in CLAUSES if c["id"].startswith("NOS")]
    tis = [c for c in CLAUSES if c["id"].startswith("TIS")]
    kms = [c for c in CLAUSES if c["id"].startswith("KMS")]
    gsp = [c for c in CLAUSES if c["id"].startswith("GSP")]

    for label, group in [("NOS", nos), ("TIS", tis), ("KMS", kms), ("GSP", gsp)]:
        avg = sum(c["coverage_pct"] for c in group) / len(group) if group else 0
        print(f"  {label} ({len(group)} clauses): avg {avg:.1f}%")


if __name__ == "__main__":
    main()
