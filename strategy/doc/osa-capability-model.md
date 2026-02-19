# OSA Security Capability Model v0.1

*Authors: Aurelius, Vitruvius — February 2026*

---

## Design Rationale

This model synthesises three frameworks into a single coherent capability architecture:

| Input | Contribution |
|-------|-------------|
| **ZTA pillars** (NIST SP 800-207 / CISA) | Defines *what* must be secured — the six pillars plus Analytics and Automation |
| **NIST CSF 2.0** (Govern → Identify → Protect → Detect → Respond → Recover) | Defines *how* security operates as a lifecycle |
| **OSA pattern landscape** (SP-001 to SP-047) | Grounds each capability in proven, implementable patterns |

---

## Layer Definitions (SABSA analogy)

The three layers mirror SABSA's top three tiers:

| Layer | SABSA Equivalent | Question answered | Character |
|-------|-----------------|-------------------|-----------|
| **L1 — Strategic** | Contextual (Business) | *Why?* | Business outcomes, risk drivers, regulatory obligations, board-level objectives |
| **L2 — Architectural** | Conceptual (Architect) | *What?* | Policies, principles, control objectives, architecture decisions |
| **L3 — Functional** | Logical (Designer) | *How?* | Specific sub-capabilities, logical services, functional building blocks |

---

## Quick Reference Grid

| # | Capability Area | ZTA Pillar | CSF Functions | Core OSA Patterns |
|---|----------------|-----------|--------------|-------------------|
| CA-01 | Governance, Risk & Compliance | Cross-cutting | Govern, Identify | SP-018, SP-043, SP-022 |
| CA-02 | Identity & Access Management | Identity | Protect | SP-010, SP-032, SP-033, SP-037, SP-044 |
| CA-03 | Device & Endpoint Trust | Devices | Protect | SP-001, SP-003, SP-024, SP-006, SP-007 |
| CA-04 | Network & Infrastructure Security | Networks | Protect | SP-015, SP-016, SP-017, SP-023, SP-029 |
| CA-05 | Application & API Security | Applications | Protect | SP-004, SP-008, SP-012, SP-028, SP-030, SP-041 |
| CA-06 | Data & Information Protection | Data | Protect | SP-013, SP-019, SP-020, SP-039, SP-040 |
| CA-07 | Cloud & Platform Security | Infrastructure | Protect | SP-002, SP-011, SP-028 |
| CA-08 | Threat Detection & Security Operations | Visibility & Analytics | Detect, Identify | SP-025, SP-031, SP-035, SP-038, SP-046 |
| CA-09 | Incident Response & Resilience | Automation & Orchestration | Respond, Recover | SP-034, SP-036 |
| CA-10 | Supply Chain & Third-Party Risk | Cross-cutting | Govern, Identify | SP-042 |
| CA-11 | Human & Organisational Security | Cross-cutting | Govern, Protect | SP-014, SP-021 |
| CA-12 | AI & Agentic Security | Cross-cutting (emerging) | Govern, Protect | SP-027, SP-045, SP-047 |

---

## Capability Breakdown

---

### CA-01 · Governance, Risk & Compliance

> *The capability to define, govern, measure and continuously improve the organisation's security posture in alignment with business strategy and regulatory obligations.*

**L1 — Strategic**
- Establish board-level accountability for information security risk, aligned to enterprise risk appetite
- Ensure demonstrable compliance with applicable regulatory regimes (GDPR, DORA, NIS2, FCA, DPDPA, etc.)
- Provide executive visibility into residual risk and security investment effectiveness
- Maintain an authoritative security policy hierarchy traceable to business objectives

**L2 — Architectural**
- Security policy and standards governance framework (ISMS — ISO/IEC 27001, NIST RMF)
- Risk management methodology: risk taxonomy, risk register, risk treatment lifecycle
- Compliance mapping architecture: controls-to-requirements traceability across multiple frameworks
- Security metrics and KRI/KPI architecture (measurement model, reporting cadence)
- Audit and assurance programme design

**L3 — Functional**
- Policy lifecycle management (authoring, approval, review, exception handling)
- Enterprise risk register and risk treatment tracking
- Compliance posture dashboard and evidence repository
- Control assurance and internal audit management
- Security metrics collection, aggregation, and board reporting
- Regulatory horizon scanning and impact assessment
- *OSA patterns: SP-018 (ISMS), SP-043 (Security Metrics), SP-022 (Board Room), SP-026 (PCI Environment)*

---

### CA-02 · Identity & Access Management

> *The capability to establish, govern, and continuously verify the identity of every user, service, and machine — and to enforce least-privilege access across all resources.*

**L1 — Strategic**
- Identity is the primary control plane in a Zero Trust architecture — the new perimeter
- Eliminate implicit trust based on network location; every access request must be authenticated and authorised
- Govern the full workforce, contractor, and machine identity lifecycle to reduce exposure from orphaned or over-privileged accounts
- Deliver frictionless, phishing-resistant authentication as a competitive and security advantage

**L2 — Architectural**
- Identity-centric Zero Trust access policy: no implicit trust, continuous verification, least privilege
- Authentication assurance levels and MFA requirements per resource sensitivity
- Privileged access governance principles: JIT access, session isolation, no standing privilege
- Federation and interoperability standards (SAML 2.0, OIDC, SCIM, FIDO2)
- Machine identity and workload identity architecture (service accounts, certificates, secrets)

**L3 — Functional**
- Directory services and identity repository (IDP)
- Multi-factor and phishing-resistant authentication (FIDO2/Passkeys)
- Modern authentication protocols and SSO
- Privileged access management: vault, session recording, JIT elevation
- Identity governance and administration (IGA): joiner-mover-leaver, access certification
- SaaS identity lifecycle management and SCIM provisioning
- Machine and workload identity: PKI, secrets management, SPIFFE/SPIRE
- *OSA patterns: SP-010 (Identity Management), SP-032 (Modern Authentication), SP-033 (Passkey Authentication), SP-037 (Privileged User Management), SP-044 (SaaS Identity Lifecycle)*

---

### CA-03 · Device & Endpoint Trust

> *The capability to assess, enforce, and continuously verify the security posture of every endpoint — managed and unmanaged — as a prerequisite for resource access.*

**L1 — Strategic**
- Device health is a required input to every access decision in a Zero Trust model
- Unmanaged and unhealthy devices represent the primary initial access vector for adversaries
- BYOD, mobile, and IoT proliferation demands scalable trust assessment that does not depend on physical perimeter controls
- Endpoint telemetry is a critical detection data source for the SOC

**L2 — Architectural**
- Device trust policy: minimum posture requirements (patch level, encryption, AV, compliance state) as access gate
- Unified endpoint management architecture: policy enforcement, configuration baseline, inventory
- Endpoint detection and response architecture: behavioural telemetry, threat hunting integration
- Hardware root of trust and secure boot requirements for managed devices
- BYOD segmentation and containerisation model

**L3 — Functional**
- Mobile device management / unified endpoint management (MDM/UEM)
- Device posture assessment and compliance enforcement (integration with ZTNA)
- Endpoint detection and response (EDR/XDR)
- Patch and vulnerability management at endpoint level
- Application control and allowlisting
- Full-disk encryption and hardware security (TPM, secure boot)
- Mobile threat defence (MTD) for BYOD and corporate mobile
- *OSA patterns: SP-001 (Client Module), SP-003 (Privacy Mobile Device), SP-006 (Wireless Private Network), SP-007 (Wireless Public Hotspot), SP-024 (iPhone Pattern)*

---

### CA-04 · Network & Infrastructure Security

> *The capability to segment, protect, and monitor network infrastructure — replacing perimeter-centric models with dynamic, policy-driven access based on identity and context.*

**L1 — Strategic**
- The network perimeter has dissolved; macro-segmentation alone cannot contain modern adversaries
- Micro-segmentation limits lateral movement and reduces blast radius of any breach
- Remote and hybrid work demands secure, performant access independent of physical location
- OT/ICS environments require network isolation as a fundamental protective control

**L2 — Architectural**
- Zero Trust Network Access (ZTNA) architecture: identity-and-context-based access, replace legacy VPN
- Micro-segmentation policy: workload-to-workload isolation, east-west traffic control
- Secure access service edge (SASE) convergence principles
- Network security zone model: classification, trust levels, permitted flows
- OT/ICS network isolation architecture: Purdue model adaptation, unidirectional gateways
- DNS security as a foundational control (protective DNS, DNSSEC)

**L3 — Functional**
- Zero Trust Network Access (ZTNA) / SASE platform
- Next-generation firewall and IPS
- Micro-segmentation and software-defined perimeter
- Secure remote access: ZTNA replacing VPN
- Network detection and response (NDR): east-west traffic analysis
- DMZ design and DMZ-hosted service isolation
- Secure network zone enforcement
- DNS security: protective DNS, filtering, DNSSEC
- OT/ICS network architecture and air-gap management
- *OSA patterns: SP-015 (Secure Remote Working), SP-016 (DMZ Module), SP-017 (Secure Network Zone), SP-023 (Industrial Control Systems), SP-029 (Zero Trust Architecture)*

---

### CA-05 · Application & API Security

> *The capability to design, build, and operate applications and APIs with security embedded throughout the software delivery lifecycle — treating code, dependencies, and runtime as the attack surface.*

**L1 — Strategic**
- Applications are the primary interface to business data and are the most targeted attack surface
- Security defects introduced during development are an order of magnitude cheaper to fix than post-deployment
- APIs represent the dominant integration channel and an under-secured attack surface in most organisations
- Software supply chain compromise is an existential threat requiring proactive control

**L2 — Architectural**
- Secure Software Development Lifecycle (S-SDLC) policy: security gates at every phase
- DevSecOps principles: security tooling integrated into CI/CD, developer-owned security outcomes
- API security standards: OAuth 2.0, OpenID Connect, input validation, rate limiting, schema enforcement
- OWASP Top 10 and OWASP API Top 10 alignment as minimum security baseline
- Runtime protection architecture: RASP, WAF, API gateway as last line of defence

**L3 — Functional**
- Static application security testing (SAST) in IDE and CI/CD
- Dynamic application security testing (DAST) against deployed apps and APIs
- Software composition analysis (SCA) and open-source dependency governance
- Container image scanning and registry security
- Secrets detection and secrets management (vault integration)
- API gateway with authentication, authorisation, rate limiting, and schema validation
- Web application firewall (WAF)
- Secure application baseline and hardening standards
- Secure DevOps pipeline automation
- SOA and microservice security patterns
- *OSA patterns: SP-004 (SOA Publication), SP-005 (SOA Internal Service), SP-008 (Public Web Server), SP-012 (Secure SDLC), SP-028 (Secure DevOps Pipeline), SP-030 (API Security), SP-041 (Secure Application Baseline)*

---

### CA-06 · Data & Information Protection

> *The capability to classify, protect, and govern data throughout its entire lifecycle — at rest, in transit, in use, and in shared contexts — including future-proof cryptographic resilience.*

**L1 — Strategic**
- Data is the ultimate target of every significant attack; perimeter and endpoint controls alone are insufficient
- Privacy regulations (GDPR, DPDPA, state laws) impose enforceable obligations on data handling and breach notification
- Quantum computing will render current public-key cryptography obsolete within a decade; migration must begin now
- Data shared with partners, SaaS platforms, and collaboration tools creates uncontrolled exposure if ungoverned

**L2 — Architectural**
- Data classification framework: sensitivity tiers, handling requirements, labelling standards
- Encryption policy: at-rest, in-transit, and in-use encryption requirements by data tier
- Cryptographic standards: approved algorithms, key lengths, key management requirements
- Post-quantum cryptography migration architecture: crypto-agility as a design principle
- Data minimisation and retention policy: collect only what is needed, dispose on schedule
- Privacy by design requirements for all systems processing personal data

**L3 — Functional**
- Data discovery and classification (automated labelling, DLP tagging)
- Data loss prevention (DLP): endpoint, network, cloud
- Encryption key management: HSM, KMS, key lifecycle
- Client-side encryption for high-sensitivity data
- Tokenisation and data masking for test/non-prod environments
- Information rights management (IRM/DRM) for document-level protection
- Secure file exchange and collaboration controls
- Email transport security: TLS, DMARC, DKIM, SPF
- Post-quantum cryptographic migration tooling and inventory
- *OSA patterns: SP-013 (Data Security), SP-019 (Secure File Exchange), SP-020 (Email TLS), SP-039 (Client-Side Encryption), SP-040 (Post-Quantum Cryptography)*

---

### CA-07 · Cloud & Platform Security

> *The capability to secure cloud infrastructure, workloads, and platform services across multi-cloud and hybrid environments — enforcing the shared responsibility model and preventing cloud-native misconfigurations as the dominant breach vector.*

**L1 — Strategic**
- Cloud adoption has fundamentally shifted the attack surface from physical to configuration and identity
- Misconfiguration is the leading cause of cloud data breaches; security must be embedded in provisioning
- Multi-cloud and hybrid strategies require consistent policy enforcement independent of CSP
- Cloud economics demand automated, policy-as-code security to scale without linear headcount growth

**L2 — Architectural**
- Shared responsibility model clarity: CSP vs. customer obligations by service type (IaaS/PaaS/SaaS)
- Cloud security architecture principles: least-privilege IAM, private networking by default, encryption everywhere
- Infrastructure-as-Code (IaC) security standards: policy-as-code gates in CI/CD pipelines
- Cloud security posture management (CSPM) as continuous compliance enforcement
- Container and serverless security architecture: immutable images, runtime isolation, least privilege

**L3 — Functional**
- Cloud security posture management (CSPM): drift detection, compliance benchmarks (CIS, NIST)
- Cloud infrastructure entitlement management (CIEM): cloud IAM right-sizing
- Cloud workload protection platform (CWPP): runtime protection for VMs, containers, serverless
- IaC security scanning (Terraform, CloudFormation, Bicep)
- Container security: image scanning, registry governance, Kubernetes security posture
- Cloud-native network controls: VPC design, security groups, private endpoints
- SaaS security posture management (SSPM)
- Server hardening and secure baseline
- *OSA patterns: SP-002 (Server Module), SP-011 (Cloud Computing), SP-028 (Secure DevOps Pipeline)*

---

### CA-08 · Threat Detection & Security Operations

> *The capability to continuously monitor the entire attack surface, detect adversarial activity early, and operate a coordinated security operations function — intelligence-led and MITRE ATT&CK-aligned.*

**L1 — Strategic**
- Assume breach: detection capability determines the difference between a minor incident and a catastrophic event
- Dwell time — the gap between compromise and detection — is the primary driver of breach severity
- Threat intelligence converts reactive detection into proactive defence against known adversary TTPs
- External attack surface management closes the visibility gap on assets unknown to the security team

**L2 — Architectural**
- Detection-in-depth architecture: endpoint, network, identity, cloud, application telemetry correlated centrally
- Threat intelligence framework: strategic, operational, and tactical intel consumption and production
- Detection engineering principles: ATT&CK-aligned detection coverage, detection-as-code
- Adversarial validation architecture: red team, purple team, BAS integration as detection feedback loop
- Vulnerability management architecture: risk-based prioritisation, SLA-driven remediation

**L3 — Functional**
- Security information and event management (SIEM): log aggregation, correlation, alerting
- Security orchestration, automation, and response (SOAR): playbook automation
- User and entity behaviour analytics (UEBA): anomaly detection on identity and endpoint telemetry
- Threat intelligence platform (TIP): IOC/TTP ingestion, enrichment, dissemination
- Threat hunting: hypothesis-driven, ATT&CK-mapped investigation capability
- Deception and honeypot technology
- External attack surface management (EASM): continuous internet-facing asset discovery
- Vulnerability management and patch prioritisation
- Offensive security testing: penetration testing, red team, bug bounty
- *OSA patterns: SP-025 (Advanced Monitoring and Detection), SP-031 (Security Monitoring and Response), SP-035 (Offensive Security Testing), SP-038 (Vulnerability Management), SP-046 (External Attack Surface Management)*

---

### CA-09 · Incident Response & Operational Resilience

> *The capability to prepare for, detect, contain, eradicate, and recover from security incidents — maintaining business continuity under adversarial conditions and enabling organisational learning.*

**L1 — Strategic**
- Resilience is the business objective; security incidents are unavoidable — the measure is how fast the organisation recovers
- Regulatory frameworks (DORA, NIS2) mandate defined, tested incident response and recovery capabilities with notification obligations
- OT incidents can have physical safety consequences, requiring dedicated OT response posture
- Cyber insurance and business continuity planning require evidence of tested response capability

**L2 — Architectural**
- Incident response lifecycle architecture: Prepare → Identify → Contain → Eradicate → Recover → Learn (PICERL)
- Crisis communications framework: stakeholder notification, regulatory reporting, media management
- Business continuity and disaster recovery integration: RTO/RPO targets by system criticality
- Forensic capability architecture: evidence preservation, chain of custody, tooling standards
- Playbook design: scenario-specific, automated where appropriate, regularly tested

**L3 — Functional**
- Incident response plan and playbook library
- Digital forensics and incident response (DFIR): tooling, retainer, capability
- Crisis management and war-room protocols
- Tabletop exercises and simulated incident drills
- Backup and restore: immutable backup, offline copies, tested restoration
- Disaster recovery orchestration and failover automation
- Business continuity management: BIA, continuity plans, communications trees
- Cyber resilience architecture: redundancy, diversity, graceful degradation
- Post-incident review and lessons-learned process
- *OSA patterns: SP-034 (Cyber Resilience), SP-036 (Incident Response)*

---

### CA-10 · Supply Chain & Third-Party Risk

> *The capability to identify, assess, and continuously monitor the security posture of third parties, vendors, and software dependencies — preventing the extended enterprise from becoming an uncontrolled attack surface.*

**L1 — Strategic**
- Third-party breaches are among the highest-impact attack vectors: one compromised vendor can expose hundreds of clients
- Software supply chain attacks demonstrate that open-source and commercial components are attack vectors
- Concentration risk in critical suppliers creates systemic resilience exposure
- Regulatory frameworks (DORA Article 28, NIS2 Article 21) impose explicit third-party risk obligations

**L2 — Architectural**
- Third-party risk management (TPRM) framework: risk tiering, due diligence, contractual obligations, ongoing monitoring
- Software Bill of Materials (SBOM) policy: mandatory SBOM for critical software, lifecycle tracking
- Vendor access governance architecture: JIT access, network segregation, session monitoring for third-party users
- Contractual security baseline: minimum security requirements, right-to-audit clauses, incident notification obligations
- Open-source governance policy: approved registries, licence compliance, vulnerability response SLAs

**L3 — Functional**
- Vendor risk assessment and tiering (questionnaire, audit, external rating)
- Continuous vendor security rating monitoring
- SBOM management: generation, ingestion, vulnerability correlation
- Open-source dependency governance and SCA integration
- Third-party access management: dedicated credentials, session recording, time-limited access
- Contract management: security clause library, review workflow
- Concentration risk analysis and alternative supplier planning
- *OSA patterns: SP-042 (Third-Party Risk Management)*

---

### CA-11 · Human & Organisational Security

> *The capability to reduce human-layer attack surface through awareness, cultural embedding, and insider threat management — recognising that people are simultaneously the greatest risk and the most important security asset.*

**L1 — Strategic**
- Social engineering (phishing, vishing, pretexting) remains the dominant initial access vector across all threat actor categories
- Security culture is a force multiplier: engaged employees detect and report attacks faster than technical controls alone
- Insider threats — malicious, negligent, or compromised — require behavioural controls that complement technical ones
- Secure collaboration platforms have become mission-critical infrastructure requiring dedicated security patterns

**L2 — Architectural**
- Competency-based security awareness architecture: role-differentiated content, not generic annual compliance training
- Security culture maturity model: measurement, executive sponsorship, feedback loops
- Insider threat programme framework: policy, detection (UEBA), investigation, response, privacy balance
- Security champion programme design: embedding security expertise in engineering teams
- Secure collaboration architecture: information barriers, access controls, external sharing governance

**L3 — Functional**
- Phishing simulation: frequency, targeting, role-based difficulty, just-in-time coaching
- Role-based security awareness training: technical, non-technical, executive, privileged user tracks
- Insider threat detection: UEBA-driven behavioural alerting, DLP correlation
- Security champion network: training, tooling, escalation paths
- Human risk scoring and targeted intervention
- Secure collaboration platform controls: DLP, external sharing policies, meeting security
- Executive and board security education
- *OSA patterns: SP-014 (Awareness and Training), SP-021 (Realtime Collaboration), SP-022 (Board Room)*

---

### CA-12 · AI & Agentic Security

> *The capability to govern, secure, and assure AI systems and autonomous agents — addressing AI-specific attack surfaces, model integrity, and the novel trust and control challenges introduced by agentic architectures.*

**L1 — Strategic**
- AI adoption is accelerating across every business function; ungoverned AI introduces model risk, data leakage, and reputational exposure
- Agentic AI systems — autonomous agents with tool access, memory, and multi-step reasoning — operate with a risk profile fundamentally different from traditional software
- Adversarial AI attacks (prompt injection, model poisoning, adversarial examples) represent an emerging and rapidly evolving threat class
- Regulatory AI governance obligations are crystallising globally (EU AI Act, NIST AI RMF, DORA); early capability building avoids costly retrofitting

**L2 — Architectural**
- AI governance framework: model risk management, AI inventory, lifecycle governance, ethical AI principles
- Agentic security architecture principles: minimal tool authority, human-in-the-loop gates, audit trail requirements, blast radius containment
- AI threat model: prompt injection, jailbreaking, data exfiltration via LLM, model inversion, supply chain poisoning
- AI data governance: training data provenance, RAG data access controls, output monitoring
- AI security integration standards: how AI components integrate with existing IAM, DLP, and monitoring

**L3 — Functional**
- AI model inventory and risk classification
- Prompt injection detection and input/output filtering
- AI system access controls: scoped tool permissions, identity propagation into agent actions
- AI audit logging: agent reasoning traces, tool calls, data accessed
- Human oversight gates: approval workflows for high-risk agentic actions
- AI output monitoring: content moderation, sensitive data detection in LLM outputs
- Model and supply chain integrity: provenance verification, approved model registry
- AI red teaming and adversarial testing capability
- Responsible AI assessment: bias, fairness, explainability evaluation
- *OSA patterns: SP-027 (Secure AI Integration), SP-045 (AI Governance and Responsible AI), SP-047 (Secure Agentic AI Frameworks)*

---

## Cross-Cutting Analysis

### ZTA Pillar Coverage

All seven ZTA pillars are addressed — Identity (CA-02), Devices (CA-03), Networks (CA-04), Applications (CA-05), Data (CA-06), Visibility & Analytics (CA-08), Automation & Orchestration (CA-09). CA-07 (Cloud) and CA-12 (AI) extend ZTA to infrastructure types that post-date the original pillar model.

### NIST CSF 2.0 Function Mapping

| CSF Function | Primary CAs | Secondary CAs |
|-------------|------------|---------------|
| Govern | CA-01, CA-10, CA-12 | CA-11 |
| Identify | CA-01, CA-10 | CA-08 |
| Protect | CA-02, CA-03, CA-04, CA-05, CA-06, CA-07 | CA-11, CA-12 |
| Detect | CA-08 | CA-03, CA-07 |
| Respond | CA-09 | CA-08 |
| Recover | CA-09 | CA-01 |

### OSA Pattern Coverage & Gaps

All 47 active patterns (SP-001 to SP-047) map into this model. The most pattern-dense capability areas are CA-02 (Identity), CA-05 (Application), and CA-08 (Detection), reflecting OSA's strongest current content.

**Pattern gaps worth filling:**

| Gap | CA | Proposed pattern |
|-----|----|-----------------|
| No dedicated cloud-native / CSPM pattern | CA-07 | SP-048: Cloud Security Posture Management |
| No SBOM / software supply chain pattern | CA-10 | SP-049: Software Supply Chain Security |
| No unified endpoint security pattern (current coverage is device-specific) | CA-03 | SP-050: Endpoint Security Architecture |

---

*This model is a living reference. Layer 3 functional capabilities map directly to OSA patterns, making the pattern catalogue the primary implementation evidence base for each capability. As new patterns are added, they should be cross-referenced here.*
