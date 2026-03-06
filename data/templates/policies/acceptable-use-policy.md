# Acceptable Use Policy

**Template Version:** 1.0
**Classification:** Internal
**Owner:** [CISO / Head of Information Security]
**Review Cycle:** Annual
**NIST 800-53 Alignment:** This policy maps to NIST SP 800-53 Rev 5 controls throughout. Control references are shown as `[XX-NN]`.

> **Usage:** This is a template. Replace all `[PLACEHOLDER]` values with your organisation's details. Remove sections that don't apply. Adapt language to your regulatory context.

---

## 1. Purpose

This policy defines what constitutes acceptable use of `[ORGANISATION NAME]`'s information systems, networks, data, and technology resources. It exists to protect `[ORGANISATION NAME]`, its employees, its customers, and its partners from harm caused by misuse — whether intentional or accidental.

All users are expected to exercise good judgement. This policy sets boundaries, not an exhaustive list of rules. If you're unsure whether something is acceptable, ask your manager or the IT Security team before proceeding. `[PL-04]`

## 2. Scope

This policy applies to:

- All employees, contractors, consultants, and temporary staff
- All third parties granted access to `[ORGANISATION NAME]` systems
- All technology resources: laptops, desktops, mobile devices, phones, networks, cloud services, applications, email, messaging, internet access, and any other systems provided or managed by `[ORGANISATION NAME]`
- Personal devices used to access `[ORGANISATION NAME]` data or systems (BYOD)

## 3. General Principles

- `[ORGANISATION NAME]` technology resources are provided primarily for business purposes. Limited personal use is permitted provided it does not interfere with work duties, consume excessive resources, or violate this policy. `[AC-08]`
- You are responsible for all activity conducted under your accounts and credentials. Never share your passwords, tokens, or access credentials. `[IA-05]`
- You have no expectation of privacy when using `[ORGANISATION NAME]` systems. The organisation reserves the right to monitor, log, audit, and review all activity on its systems in accordance with applicable law. `[AU-02]` `[AC-08]`

## 4. Acceptable Use

### 4.1 Email and Messaging

- Use your `[ORGANISATION NAME]` email and messaging accounts for business communications. `[AC-08]`
- Do not send Confidential or Restricted information via unencrypted email. Use approved secure channels. `[SC-08]`
- Do not auto-forward `[ORGANISATION NAME]` email to personal accounts. `[AC-08]`
- Be alert to phishing, business email compromise, and social engineering. Verify unexpected requests for payments, credentials, or sensitive data through a separate channel. Report suspicious messages to `[phishing@organisation.com / IT Security]`. `[AT-02]` `[IR-06]`
- Email and messaging may be monitored for security threats including malware, data exfiltration, and policy violations. `[SI-04]`

### 4.2 Internet Use

- Internet access is provided for business purposes. Reasonable personal use during breaks is permitted. `[AC-08]`
- Do not access, download, or distribute material that is:
  - Illegal under applicable law
  - Offensive, discriminatory, or harassing
  - Pornographic or sexually explicit
  - Malicious (malware, exploit kits, hacking tools) unless authorised for security testing `[AC-08]`
- Web traffic may be filtered, logged, and monitored. `[SI-04]` `[SC-07]`
- Circumventing web filters, firewalls, or other security controls without authorisation is prohibited. `[AC-03]`

### 4.3 Devices and Endpoints

- Lock your device when unattended — even briefly. `[AC-11]`
- Enable full disk encryption on all devices that access `[ORGANISATION NAME]` data. `[SC-28]`
- Keep your device's operating system, applications, and security software up to date. Accept automatic updates where available. `[SI-02]`
- Do not install unauthorised software on `[ORGANISATION NAME]` devices. Software requests should go through `[IT / approved procurement process]`. `[CM-11]`
- Do not connect `[ORGANISATION NAME]` devices to untrusted networks without VPN or equivalent protection. `[AC-17]`
- Do not connect personal USB drives or storage devices to `[ORGANISATION NAME]` systems without authorisation. `[MP-07]`
- Report lost or stolen devices immediately to `[IT Security / helpdesk]`. `[IR-06]`

### 4.4 Personal Devices (BYOD)

- Personal devices may only access `[ORGANISATION NAME]` data through approved applications and services (e.g., managed mobile apps, virtual desktop, web portal). `[AC-19]`
- `[ORGANISATION NAME]` reserves the right to remotely wipe corporate data from personal devices in the event of loss, theft, or termination. `[AC-19]` `[MP-06]`
- Personal devices used for work must meet minimum security standards:
  - Current operating system with security updates applied
  - Device encryption enabled
  - Screen lock with PIN, password, or biometric
  - No jailbreaking or rooting `[AC-19]`

### 4.5 Passwords and Authentication

- Use strong, unique passwords for all `[ORGANISATION NAME]` accounts. `[IA-05]`
- Never share your password with anyone — including IT staff, your manager, or helpdesk. IT will never ask for your password. `[IA-05]`
- Use the approved password manager for storing credentials. `[IA-05(13)]`
- Enable multi-factor authentication (MFA) on all accounts where available. MFA is mandatory for remote access, privileged accounts, and access to Confidential/Restricted data. `[IA-02(1)]`
- If you suspect your credentials have been compromised, change your password immediately and report to IT Security. `[IR-06]`

### 4.6 Cloud Services and SaaS

- Only use cloud services that have been approved by IT Security. Do not create accounts on unapproved services using your `[ORGANISATION NAME]` email. `[SA-09]`
- Do not store Confidential or Restricted data on unapproved cloud services, personal cloud storage (Dropbox, personal Google Drive, iCloud), or file-sharing sites. `[SA-09]` `[AC-03]`
- When sharing files externally via approved cloud services, use time-limited links with the minimum permissions necessary. `[AC-03]` `[AC-06]`

### 4.7 Artificial Intelligence Tools

- Do not submit Confidential or Restricted data to external AI services (ChatGPT, Claude, Gemini, Copilot, etc.) unless the service has been approved by IT Security and data processing agreements are in place. `[SA-09]` `[PT-02]`
- Approved AI services: `[LIST APPROVED SERVICES, e.g., "[ORGANISATION NAME] GPT instance", "GitHub Copilot Business"]`
- When using approved AI tools:
  - Do not submit customer personal data, authentication credentials, encryption keys, or source code from security-critical systems
  - Review AI-generated output before using it in production, decisions, or customer-facing communications
  - Be aware that AI-generated content may be inaccurate — you remain responsible for the output you use `[PM-14]`
- Report any AI tool that unexpectedly requests or exposes sensitive data to IT Security. `[IR-06]`

### 4.8 Social Media

- Do not disclose `[ORGANISATION NAME]` Confidential or Restricted information on social media. `[AC-08]`
- Do not represent yourself as speaking on behalf of `[ORGANISATION NAME]` unless authorised. `[AC-08]`
- Be aware that publicly sharing details of your role, projects, or technology stack can assist adversary reconnaissance.

### 4.9 Remote and Mobile Working

- Apply the same security standards when working remotely as you would in the office. `[AC-17]`
- Use VPN or approved zero trust access when connecting to `[ORGANISATION NAME]` systems from outside the corporate network. `[AC-17]` `[SC-08]`
- Do not access Confidential or Restricted information in public places where screens are visible to others. Use a privacy screen where available. `[AC-11]`
- Secure physical documents when working remotely. Do not leave printouts containing Confidential or Restricted information unattended. `[MP-04]`
- Use `[ORGANISATION NAME]`-approved video conferencing and collaboration tools for business discussions. `[AC-08]`

### 4.10 Software Development

- Follow the secure development lifecycle (SDLC) defined in the Information Security Policy. `[SA-03]`
- Do not commit credentials, API keys, tokens, or private keys to source code repositories. Use secrets management. `[IA-05(7)]`
- Do not disable or bypass security controls (linters, pre-commit hooks, vulnerability scanners) without approval. `[CM-03]`
- Report vulnerabilities found in `[ORGANISATION NAME]` systems or third-party dependencies to IT Security. `[SI-02]` `[RA-05]`

## 5. Prohibited Activities

The following are strictly prohibited on `[ORGANISATION NAME]` systems and networks:

- Unauthorised access to systems, accounts, or data — including colleagues' accounts, even with their permission `[AC-03]`
- Installing or running malware, hacking tools, port scanners, or vulnerability scanners without authorisation from IT Security `[CM-11]`
- Intercepting, monitoring, or recording network traffic or communications without authorisation `[AC-08]`
- Circumventing access controls, encryption, logging, or other security mechanisms `[AC-03]`
- Using `[ORGANISATION NAME]` resources for personal commercial activities, cryptocurrency mining, or political campaigning `[AC-08]`
- Connecting unauthorised network equipment (routers, wireless access points, switches) to the corporate network `[AC-18]`
- Downloading, distributing, or storing pirated software, media, or other copyrighted material `[AC-08]`
- Harassing, threatening, or discriminating against any person via `[ORGANISATION NAME]` systems `[AC-08]`

## 6. Data Handling

- Handle data according to its classification (see Information Security Policy, Section 4). `[RA-02]`
- Do not copy Confidential or Restricted data to removable media (USB drives, external hard drives) without approval and encryption. `[MP-05]` `[MP-07]`
- Dispose of data securely — shred physical documents, use approved data wiping tools for electronic media. `[MP-06]`
- When leaving `[ORGANISATION NAME]`, return all data and equipment. Do not retain copies of `[ORGANISATION NAME]` data. `[PS-04]`

## 7. Reporting

Report the following to `[security-incidents@organisation.com / IT Security team]` immediately:

- Suspected or confirmed security incidents `[IR-06]`
- Lost or stolen devices `[IR-06]`
- Phishing emails or suspected social engineering `[IR-06]`
- Suspected malware infection `[IR-06]`
- Unauthorised access or suspicious activity on your accounts `[IR-06]`
- Suspected data breaches or data loss `[IR-06]`
- Any activity that may violate this policy

You will not face disciplinary action for reporting a genuine security concern in good faith, even if it relates to your own accidental action.

## 8. Monitoring and Enforcement

- `[ORGANISATION NAME]` monitors its systems and networks for security threats, policy compliance, and operational purposes. This includes but is not limited to: email content, internet activity, file access, authentication events, and device activity. `[AU-02]` `[SI-04]`
- Monitoring is conducted in accordance with applicable privacy and employment law.
- Violation of this policy may result in:
  - Removal of access privileges
  - Formal disciplinary action up to and including termination
  - Criminal prosecution where unlawful activity is identified
  - Contract termination for third parties

## 9. Exceptions

Exceptions to this policy must be requested in writing, approved by the CISO or delegate, documented with a risk assessment, and are time-limited (maximum `[12]` months). `[RA-03]`

## 10. Acknowledgement

All users must acknowledge they have read, understood, and agree to comply with this policy.

- New starters: within `[5]` working days of receiving system access
- Existing staff: annually, or when the policy is materially updated
- Third parties: before system access is granted

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
