# Information Security Policy

**Template Version:** 1.0
**Classification:** Internal
**Owner:** [CISO / Head of Information Security]
**Review Cycle:** Annual
**NIST 800-53 Alignment:** This policy maps to NIST SP 800-53 Rev 5 controls throughout. Control references are shown as `[XX-NN]`.

> **Usage:** This is a template. Replace all `[PLACEHOLDER]` values with your organisation's details. Remove sections that don't apply. Adapt language to your regulatory context.

---

## 1. Purpose

This policy establishes the information security requirements for `[ORGANISATION NAME]`. It defines the principles, responsibilities, and minimum standards for protecting information assets against unauthorised access, disclosure, modification, destruction, and disruption.

This policy applies to all information assets owned, operated, or managed by `[ORGANISATION NAME]`, regardless of format or location. `[PL-01]` `[PM-01]`

## 2. Scope

This policy applies to:

- All employees, contractors, consultants, and temporary staff
- All third parties with access to `[ORGANISATION NAME]` systems or data
- All information assets including systems, applications, networks, data, and infrastructure — whether on-premises, cloud-hosted, or hybrid
- All locations from which `[ORGANISATION NAME]` information is accessed, including remote and mobile working

## 3. Policy Ownership and Governance

| Role | Responsibility |
|------|---------------|
| **Board / Executive Committee** | Approve this policy. Accept residual risk. Fund the security programme. `[PM-01]` |
| **CISO / Head of Security** | Maintain this policy. Report security posture to the board. Direct the security programme. `[PM-02]` |
| **Information Asset Owners** | Classify their assets. Approve access. Accept risk for their assets. `[RA-02]` |
| **IT / Platform Engineering** | Implement technical controls. Maintain systems. Respond to incidents. `[SA-03]` |
| **All Staff** | Comply with this policy. Report security incidents. Complete security training. `[AT-02]` |

The CISO shall report to the board or executive committee at least quarterly on: security posture, material incidents, risk trends, and programme progress. `[PM-06]`

## 4. Information Classification

All information shall be classified according to the following scheme. The classification determines the minimum controls required for handling, storage, transmission, and disposal. `[RA-02]`

| Classification | Description | Examples |
|---------------|-------------|----------|
| **Public** | Approved for unrestricted distribution | Marketing materials, published reports |
| **Internal** | For internal use only; limited business impact if disclosed | Internal memos, process documents, org charts |
| **Confidential** | Significant business impact if disclosed; restricted to authorised personnel | Customer data, financial records, contracts, source code |
| **Restricted** | Severe business or regulatory impact if disclosed; strict need-to-know | Encryption keys, authentication credentials, PII subject to regulation, trade secrets |

Asset owners are responsible for classifying their information. Where classification is uncertain, apply the higher classification until resolved. `[RA-02]` `[MP-03]`

## 5. Access Control

### 5.1 Principles

- **Least privilege:** Users shall be granted the minimum access necessary to perform their role. `[AC-06]`
- **Need to know:** Access to Confidential and Restricted information requires explicit authorisation from the asset owner. `[AC-03]`
- **Separation of duties:** No single individual shall control all phases of a critical process. `[AC-05]`
- **Default deny:** Access is denied unless explicitly granted. `[AC-03]`

### 5.2 Account Management

- User accounts shall be uniquely assigned. Shared accounts are prohibited except where technically unavoidable, in which case they require documented approval and compensating controls. `[AC-02]`
- Privileged accounts (administrator, root, service accounts with elevated rights) shall be inventoried, individually assigned, subject to enhanced monitoring, and reviewed quarterly. `[AC-02(7)]` `[AC-06(5)]`
- Accounts shall be disabled within `[24 hours / same business day]` of termination or role change. `[AC-02(3)]` `[PS-04]`
- Dormant accounts (no login for `[90]` days) shall be automatically disabled. `[AC-02(3)]`
- Access reviews shall be conducted at least `[quarterly / semi-annually]` for privileged accounts and `[annually]` for standard accounts. `[AC-02(13)]`

### 5.3 Authentication

- Multi-factor authentication (MFA) is required for:
  - All remote access `[IA-02(1)]`
  - All privileged accounts `[IA-02(1)]`
  - All access to Confidential and Restricted data `[IA-02(1)]`
  - All cloud management consoles `[IA-02(1)]`
- Passwords shall meet the following minimum requirements: `[IA-05]`
  - Minimum `[14]` characters for standard accounts
  - Minimum `[16]` characters for privileged accounts
  - No reuse of the previous `[12]` passwords
  - Lockout after `[10]` consecutive failed attempts
- Password managers are recommended for all staff. `[IA-05(13)]`
- Service account credentials shall be stored in a secrets management system, never in source code or configuration files. `[IA-05(7)]`

## 6. Network Security

- Network architecture shall implement defence in depth with segmentation between trust zones. `[SC-07]`
- All external-facing systems shall be protected by firewalls, web application firewalls, or equivalent controls. `[SC-07]`
- Internal network segmentation shall isolate systems of different classification levels. `[SC-07(5)]`
- All remote access shall use encrypted tunnels (VPN or zero trust network access). `[AC-17]` `[SC-08]`
- Wireless networks shall use WPA3 or WPA2-Enterprise with certificate-based authentication. `[AC-18]` `[SC-08]`
- Network traffic shall be monitored for anomalous activity. `[SI-04]`

## 7. System and Application Security

### 7.1 Secure Development

- Applications developed by or for `[ORGANISATION NAME]` shall follow a secure development lifecycle (SDLC) that includes threat modelling, security requirements, secure coding standards, and security testing. `[SA-03]` `[SA-08]`
- Source code shall undergo security review (automated and/or manual) before release to production. `[SA-11]`
- Production environments shall be separated from development and testing environments. `[CM-02]`
- Third-party libraries and dependencies shall be tracked and monitored for known vulnerabilities. `[SA-12]` `[RA-05]`

### 7.2 Change Management

- All changes to production systems shall follow a documented change management process including approval, testing, rollback planning, and post-implementation review. `[CM-03]`
- Emergency changes are permitted with retrospective documentation and approval within `[48]` hours. `[CM-03]`

### 7.3 Vulnerability Management

- Vulnerability scanning shall be conducted at least `[monthly]` for all internet-facing systems and `[quarterly]` for internal systems. `[RA-05]`
- Critical and high vulnerabilities on internet-facing systems shall be remediated within `[14]` days. `[RA-05]` `[SI-02]`
- Critical and high vulnerabilities on internal systems shall be remediated within `[30]` days. `[SI-02]`
- Where remediation is not feasible within the required timeframe, a risk acceptance shall be documented and approved by the asset owner and CISO. `[RA-03]`

### 7.4 Endpoint Security

- All endpoints (laptops, desktops, mobile devices) shall run approved endpoint protection (EDR/anti-malware). `[SI-03]`
- Operating systems and applications shall be kept current with vendor-supported versions. `[SI-02]`
- Device encryption shall be enabled on all endpoints that process or store Confidential or Restricted data. `[SC-28]`
- Mobile device management (MDM) shall be deployed for all devices accessing `[ORGANISATION NAME]` data. `[AC-19]`

## 8. Cryptography

- Encryption shall protect Confidential and Restricted data at rest and in transit. `[SC-08]` `[SC-28]`
- Encryption standards shall meet or exceed:
  - **Data in transit:** TLS 1.2 minimum, TLS 1.3 preferred `[SC-08]`
  - **Data at rest:** AES-256 or equivalent `[SC-28]`
  - **Hashing:** SHA-256 minimum for integrity checking `[SC-13]`
- Cryptographic key management shall include documented procedures for generation, distribution, storage, rotation, revocation, and destruction. `[SC-12]`
- Keys shall be stored in hardware security modules (HSMs) or approved key management services — never in source code, configuration files, or shared drives. `[SC-12]`

## 9. Data Protection and Privacy

- Personal data shall be processed in accordance with applicable data protection legislation (`[GDPR / CCPA / POPIA / PDPA / specify]`). `[PT-02]` `[PT-03]`
- Data processing activities involving personal data shall be recorded in a processing register. `[PT-05]`
- Data protection impact assessments (DPIAs) shall be conducted for new processing activities involving high-risk personal data. `[RA-08]`
- Data retention periods shall be defined for all information types. Data shall be securely disposed of when no longer required. `[MP-06]` `[SI-12]`
- Data loss prevention (DLP) controls shall be implemented for Confidential and Restricted data leaving the organisation's boundary. `[SC-07]` `[SI-04]`

## 10. Cloud Security

- Cloud services shall be approved by IT Security before adoption. Shadow IT is prohibited. `[SA-09]`
- Cloud provider selection shall include security assessment against `[ORGANISATION NAME]` requirements. `[SA-09]`
- Cloud environments shall be configured following CIS Benchmarks or equivalent hardening standards. `[CM-06]`
- Cloud security posture management (CSPM) tooling shall monitor configuration drift and compliance. `[CM-06]` `[CA-07]`
- Data residency requirements shall be documented and enforced for Restricted and Confidential data. `[SA-09]`

## 11. Third-Party and Supply Chain Security

- All third parties with access to `[ORGANISATION NAME]` systems or data shall be subject to security due diligence before engagement. `[SA-09]` `[SR-06]`
- Third-party contracts shall include security requirements, right-to-audit clauses, breach notification obligations, and data handling terms. `[SA-09]`
- Third-party access shall be reviewed at least annually. Access shall be revoked upon contract termination. `[PS-07]`
- Critical suppliers shall be assessed for concentration risk and business continuity capability. `[SR-02]` `[SR-03]`

## 12. Physical Security

- Facilities housing information systems shall implement physical access controls proportionate to the classification of information processed. `[PE-02]` `[PE-03]`
- Server rooms and network equipment areas shall be restricted to authorised personnel with access logged. `[PE-02]`
- Visitor access shall be logged and escorted in restricted areas. `[PE-03]`
- Equipment disposal shall follow secure media sanitisation procedures. `[MP-06]`

## 13. Business Continuity and Disaster Recovery

- Business continuity plans (BCPs) shall be documented for critical business processes. `[CP-02]`
- Disaster recovery plans (DRPs) shall be documented for critical information systems, including recovery time objectives (RTOs) and recovery point objectives (RPOs). `[CP-02]`
- Backups shall be performed according to a documented schedule, encrypted, and tested at least `[quarterly]`. `[CP-09]` `[CP-04]`
- BCPs and DRPs shall be tested at least annually via tabletop exercise or functional test. `[CP-04]`

## 14. Security Incident Management

- All suspected or confirmed security incidents shall be reported immediately to `[security-incidents@organisation.com / IT Security team / SOC]`. `[IR-06]`
- An incident response plan shall be maintained, tested annually, and shall define:
  - Roles and responsibilities `[IR-01]`
  - Severity classification `[IR-04]`
  - Escalation and notification procedures (including regulatory notification where required) `[IR-06]`
  - Forensic evidence preservation `[IR-04]`
  - Post-incident review and lessons learned `[IR-04]`
- All incidents shall be logged, tracked to resolution, and reviewed for root cause. `[IR-05]`

## 15. Security Awareness and Training

- All staff shall complete security awareness training within `[30]` days of joining and annually thereafter. `[AT-02]`
- Phishing simulations shall be conducted at least `[quarterly]`. `[AT-02]`
- Role-specific training shall be provided for:
  - Developers (secure coding) `[AT-03]`
  - System administrators (hardening, monitoring) `[AT-03]`
  - Executives (social engineering, business email compromise) `[AT-03]`
  - Incident responders (IR procedures, forensics) `[AT-03]`
- Training completion rates shall be tracked and reported to management. `[AT-04]`

## 16. Logging, Monitoring, and Audit

- Security-relevant events shall be logged for all systems, including: `[AU-02]`
  - Authentication events (success and failure)
  - Privilege escalation
  - Access to Confidential and Restricted data
  - Configuration changes
  - Administrative actions
- Logs shall be protected from tampering, retained for at least `[12]` months, and available for analysis for at least `[3]` months. `[AU-09]` `[AU-11]`
- Centralised log management (SIEM or equivalent) shall aggregate and correlate security events. `[AU-06]` `[SI-04]`
- Automated alerting shall be configured for high-severity events. `[SI-04]` `[AU-05]`

## 17. Artificial Intelligence and Automated Decision-Making

- AI systems that process `[ORGANISATION NAME]` data shall be approved by IT Security before deployment. `[SA-09]`
- Confidential and Restricted data shall not be submitted to external AI services (including public LLMs) unless:
  - The service has been risk-assessed and approved `[RA-03]`
  - Data processing agreements are in place `[SA-09]`
  - Data is anonymised or synthetic where feasible `[PT-02]`
- AI-generated outputs used in security, compliance, or risk decisions shall be reviewed by a qualified human before action. `[PM-14]`
- AI model training on `[ORGANISATION NAME]` data requires explicit approval from the data owner and CISO.

## 18. Compliance

- `[ORGANISATION NAME]` shall maintain compliance with applicable laws, regulations, and contractual obligations, including but not limited to: `[PM-01]`
  - `[List applicable: GDPR, PCI DSS, SOX, HIPAA, DORA, NIS2, etc.]`
- Internal security audits shall be conducted at least annually. `[CA-02]`
- External independent assessments shall be conducted at least `[annually / as required by regulation]`. `[CA-02]`
- Non-compliance with this policy may result in disciplinary action up to and including termination, and for third parties, contract termination.

## 19. Exceptions

- Exceptions to this policy require documented risk acceptance approved by:
  - The CISO for Confidential-level exceptions
  - The CISO and a board member for Restricted-level exceptions
- Exceptions shall be time-limited (maximum `[12]` months), reviewed at expiry, and recorded in the risk register. `[RA-03]`

## 20. Review

This policy shall be reviewed at least annually, or following:
- A material security incident
- Significant changes to the business, technology, or regulatory environment
- Results of security audits or assessments

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | `[DATE]` | `[AUTHOR]` | Initial release |

---

**Document Control**
- **Classification:** Internal
- **Next Review:** `[DATE + 12 months]`
- **Approved by:** `[NAME, TITLE]`
- **Approval date:** `[DATE]`

---

*This template is provided by Open Security Architecture (opensecurityarchitecture.org) under CC BY 4.0. NIST SP 800-53 Rev 5 control references are shown in square brackets. Adapt to your organisation's size, sector, and regulatory requirements. This template does not constitute legal or professional advice.*
