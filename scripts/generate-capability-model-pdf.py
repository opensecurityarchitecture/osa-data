#!/usr/bin/env python3
"""
OSA Security Capability Model — PDF generator (v4).
Converts the front-matter of osa-capability-model.md (up to '## Capability
Breakdown') and appends programmatically generated:
  • Diagram 1 — L1 overview grid with phase headers
  • Detail sections — each CA with L1 labels/notes and L2 KPI/maturity table

Hierarchy: Phase → CA area → L1 (business label) → L2 (KPI + 3 maturity levels)

Dependencies (install once):
    pip3 install markdown weasyprint
    brew install pango
"""

import html as _html
import sys
from pathlib import Path

import markdown
from weasyprint import HTML, CSS

WORKSPACE = Path(__file__).resolve().parent.parent
SRC_MD    = WORKSPACE.parent / "osa-strategy" / "docs" / "osa-capability-model.md"
OUT_PDF   = WORKSPACE.parent / "osa-strategy" / "docs" / "osa-capability-model.pdf"

# ── OSA brand palette ─────────────────────────────────────────────────────────
C_DARK   = "#003459"
C_MID    = "#007EA7"
C_LIGHT  = "#00A8E8"
C_WHITE  = "#FFFFFF"
C_OFFWHT = "#F4F7FA"
C_BORDER = "#D0DDE8"
C_TEXT   = "#1A2E3B"
C_MUTED  = "#5A7A8A"
C_PHASE  = {"xc": C_DARK, "zt": C_MID, "ops": C_LIGHT}
PHASE_NAME = {"xc": "Foundation", "zt": "Protect", "ops": "Operate"}


# ── Capability data ───────────────────────────────────────────────────────────
# Option C ordering: Foundation → Protect → Operate
# Each L1 has: name (technical), label (business), note (sub-note)
# Each L2 has: name, kpi, maturity {initial, established, leading}

CAPABILITIES = [
    # ── FOUNDATION ────────────────────────────────────────────────────────────
    {
        "id": "CA-01", "area": "Governance, Risk & Compliance",
        "zta": "Cross-cutting", "csf": "Govern · Identify", "grp": "xc",
        "desc": "Define, govern, measure and continuously improve the organisation's security posture in alignment with business strategy and regulatory obligations.",
        "l1s": [
            {
                "name": "Policy & Standards Management",
                "label": "Clear Security Rules That Everyone Knows How to Follow",
                "note": "Security policies and standards are maintained and translated into actionable guidance for each team (policy management); when regulations change, requirements are tracked and incorporated without a scramble (regulatory requirements management).",
                "l2": [
                    {"name": "Security Policy Hierarchy",
                     "kpi": "% of policies reviewed and approved within the last 12 months",
                     "maturity": {"initial": "Policies undated and not version-controlled", "established": "Full hierarchy maintained with annual review cycle", "leading": "Auto-triggered review on regulatory change; real-time compliance tracking"}},
                    {"name": "Standards & Procedures Lifecycle",
                     "kpi": "Average age of standards documents (target <24 months)",
                     "maturity": {"initial": "Standards drafted ad hoc; no lifecycle", "established": "Published with defined owners and review dates", "leading": "Gap analysis automated; review triggered by change events"}},
                    {"name": "Exception & Waiver Management",
                     "kpi": "% of exceptions with expiry dates and compensating controls",
                     "maturity": {"initial": "Exceptions granted informally; no tracking", "established": "Formal waiver process with approval workflow and register", "leading": "Exception trends drive policy improvement; auto-expiry enforced"}},
                    {"name": "Regulatory Requirements Translation",
                     "kpi": "% of applicable regulations mapped to internal controls",
                     "maturity": {"initial": "Regulatory requirements interpreted ad hoc", "established": "Regulations mapped to controls; ownership assigned", "leading": "Regulatory change feed integrated; impact assessed automatically"}},
                ],
            },
            {
                "name": "Risk Management",
                "label": "Risk Decisions Grounded in Evidence, Not Gut Feel",
                "note": "Every significant security risk is recorded, assessed, and assigned an owner (risk register); the board's appetite for risk is documented so decisions are consistent (risk appetite definition); controls are tested to confirm they work as expected (control effectiveness assessment).",
                "l2": [
                    {"name": "Enterprise Risk Taxonomy & Register",
                     "kpi": "% of risks with assigned owner, rating, and treatment plan",
                     "maturity": {"initial": "Risks in spreadsheets; no consistent taxonomy", "established": "Centralised register with agreed taxonomy and ownership", "leading": "Register integrated with control data; ratings updated dynamically"}},
                    {"name": "Risk Treatment & Acceptance",
                     "kpi": "% of high/critical risks with treatment plans in progress or complete",
                     "maturity": {"initial": "Treatment decisions informal; no tracking", "established": "Treatment plans documented and reviewed quarterly", "leading": "Treatment effectiveness measured; residual risk validated against controls"}},
                    {"name": "Risk Appetite & Tolerance Definition",
                     "kpi": "Risk appetite statement board-approved (yes/no + date)",
                     "maturity": {"initial": "No formal risk appetite documented", "established": "Appetite defined by category; tolerance thresholds set", "leading": "Appetite cascaded to operational thresholds; breaches trigger escalation"}},
                    {"name": "Control Effectiveness Assessment",
                     "kpi": "% of key controls tested in the last 12 months",
                     "maturity": {"initial": "Control effectiveness assumed rather than tested", "established": "Periodic testing programme with documented results", "leading": "Continuous monitoring with automated evidence collection"}},
                ],
            },
            {
                "name": "Compliance & Assurance",
                "label": "Audit Readiness Built In, Not Bolted On",
                "note": "Controls are mapped across multiple regulatory frameworks so a single piece of evidence satisfies multiple requirements (multi-framework traceability); compliance evidence is collected continuously (compliance evidence repository) — so audits draw on existing records rather than urgent evidence-gathering.",
                "l2": [
                    {"name": "Multi-Framework Control Traceability",
                     "kpi": "% of controls mapped across at least 2 regulatory frameworks",
                     "maturity": {"initial": "Framework mappings done manually for each audit", "established": "Cross-framework mapping maintained in a GRC tool", "leading": "Single control satisfies multiple frameworks; gap analysis automated"}},
                    {"name": "Compliance Evidence Repository",
                     "kpi": "% of control evidence collected automatically rather than manually",
                     "maturity": {"initial": "Evidence gathered on request; stored inconsistently", "established": "Centralised repository with defined retention", "leading": "Continuous evidence collection; linked to controls automatically"}},
                    {"name": "Internal Audit Programme",
                     "kpi": "% of planned audit engagements completed on schedule",
                     "maturity": {"initial": "Audits reactive; no annual plan", "established": "Risk-based annual plan with agreed scope and resource", "leading": "Findings tracked to closure; repeat findings drive systemic improvement"}},
                    {"name": "Regulatory Change Management",
                     "kpi": "Average days from regulatory publication to impact assessment",
                     "maturity": {"initial": "Regulatory changes identified reactively", "established": "Monitoring in place; changes assessed for impact", "leading": "Regulatory feed integrated with GRC; gaps identified automatically"}},
                ],
            },
            {
                "name": "Governance Reporting & Measurement",
                "label": "Security Performance Visible to the Board and Leadership",
                "note": "Key security metrics are tracked and reported in business terms (security KPIs/KRIs); investment decisions are supported by evidence of what is and isn't working (security investment tracking) — so leadership can hold the organisation accountable.",
                "l2": [
                    {"name": "Security KRI/KPI Framework",
                     "kpi": "% of defined KRIs/KPIs reported with current data",
                     "maturity": {"initial": "No defined metrics; reporting ad hoc", "established": "KRI/KPI set owned and reported monthly", "leading": "Benchmarked externally; thresholds trigger automatic escalation"}},
                    {"name": "Board & Executive Reporting",
                     "kpi": "% of board reports delivered on schedule with agreed format",
                     "maturity": {"initial": "Security updates to board ad hoc and inconsistent", "established": "Regular reporting cycle with defined format and audience", "leading": "Reporting tailored by audience; linked to risk appetite"}},
                    {"name": "Security Investment Tracking",
                     "kpi": "% of security budget tracked against approved initiatives",
                     "maturity": {"initial": "Spend tracked at cost-centre level only", "established": "Investment tracked by programme with benefit indicators", "leading": "ROI of security investments measured and reported"}},
                    {"name": "Security Assurance Dashboard",
                     "kpi": "Dashboard refresh frequency (target: daily or near real-time)",
                     "maturity": {"initial": "No consolidated view; assembled manually for meetings", "established": "Dashboard operational with agreed data sources", "leading": "Self-service dashboard with drill-down to evidence for stakeholders"}},
                ],
            },
        ],
    },
    {
        "id": "CA-02", "area": "Human & Organisational Security",
        "zta": "Cross-cutting", "csf": "Govern · Protect", "grp": "xc",
        "desc": "Reduce the human-layer attack surface through awareness, cultural embedding, and insider threat management — recognising that people are simultaneously the greatest risk and the most important security asset.",
        "l1s": [
            {
                "name": "Awareness & Training",
                "label": "Staff Who Know How to Spot and Respond to Threats",
                "note": "Security training is tailored to each role rather than delivered as a one-size-fits-all exercise (role-based awareness); staff are regularly tested with realistic simulated attacks (phishing simulation); guidance is offered in the moment when staff are about to do something risky (just-in-time coaching) — so awareness translates into safe habits, not quiz scores.",
                "l2": [
                    {"name": "Role-Based Security Awareness",
                     "kpi": "% of staff completing role-appropriate security training annually",
                     "maturity": {"initial": "Generic annual training with no role differentiation", "established": "Role-specific curriculum; completion tracked", "leading": "Effectiveness measured by behaviour change; curriculum updated on threat trends"}},
                    {"name": "Phishing Simulation Programme",
                     "kpi": "Phishing click rate (target <5%); % of clickers completing remedial training",
                     "maturity": {"initial": "No simulation; awareness based on incidents alone", "established": "Quarterly simulations with results tracked by department", "leading": "Simulations adaptive to individual risk profiles; results feed training priorities"}},
                    {"name": "Executive & Board Security Education",
                     "kpi": "% of executives completing security briefing in the last 12 months",
                     "maturity": {"initial": "Executives receive same generic training as general staff", "established": "Dedicated executive briefings on cyber risk and obligations", "leading": "Board education tied to risk appetite; scenario-based exercises"}},
                    {"name": "Just-in-Time Coaching & Nudging",
                     "kpi": "% of high-risk actions intercepted with a coaching nudge",
                     "maturity": {"initial": "No in-context guidance; awareness relies on memory", "established": "Browser/email nudges deployed for common high-risk actions", "leading": "Nudge effectiveness measured; high-risk users receive targeted interventions"}},
                ],
            },
            {
                "name": "Security Culture",
                "label": "Security as a Shared Habit, Not Just a Team's Responsibility",
                "note": "Employees in every function are trained and empowered to champion security within their teams (security champion network); security culture is measured so improvements can be tracked and recognised (culture maturity measurement) — so security becomes how the organisation operates, not a set of rules imposed from outside.",
                "l2": [
                    {"name": "Security Champion Network",
                     "kpi": "% of business units with an active security champion",
                     "maturity": {"initial": "No champion network; security team acts alone", "established": "Champions identified and trained in key units", "leading": "Champions in agile teams; measurable uplift tracked per unit"}},
                    {"name": "Security Culture Maturity Measurement",
                     "kpi": "Annual culture survey score (target: improving year-on-year)",
                     "maturity": {"initial": "Culture assessed by anecdote only", "established": "Annual survey with benchmarked results and action plan", "leading": "Metrics correlated with incident data; improvement initiatives tracked"}},
                    {"name": "Developer Security Enablement",
                     "kpi": "% of developers with security tooling in their IDE; mean time to fix security findings",
                     "maturity": {"initial": "Security training not part of developer onboarding", "established": "Secure coding training mandated; security champions in engineering", "leading": "Security embedded in tooling; fix rates and vulnerability trends tracked"}},
                    {"name": "Security Feedback & Recognition",
                     "kpi": "Number of security concerns reported by staff per quarter",
                     "maturity": {"initial": "No channel for staff to report security concerns", "established": "Reporting channel exists; submissions acknowledged and acted on", "leading": "Recognition programme active; reporting volume tracked as culture indicator"}},
                ],
            },
            {
                "name": "Insider Threat",
                "label": "Detecting When Trusted People Become a Risk",
                "note": "Patterns in employee behaviour are monitored to identify unusual activity that might indicate compromise or misuse (behavioural analytics); data movement is correlated with behaviour signals to distinguish accidental from deliberate harm (DLP correlation); response procedures balance investigation with employee rights — so risks are addressed early without creating a culture of suspicion.",
                "l2": [
                    {"name": "Insider Threat Policy & Programme",
                     "kpi": "% of high-risk joiner/mover/leaver events reviewed within defined SLA",
                     "maturity": {"initial": "No policy; incidents handled reactively", "established": "Policy and programme defined; risk indicators documented", "leading": "Programme integrated with HR lifecycle; cases tracked and reported"}},
                    {"name": "Behavioural Analytics (UEBA)",
                     "kpi": "Mean time from anomaly detection to investigation initiation",
                     "maturity": {"initial": "No behavioural monitoring; insider events identified after the fact", "established": "UEBA deployed; baseline established and alerts configured", "leading": "Alert fidelity tuned; high-risk user monitoring automated"}},
                    {"name": "DLP-UEBA Correlation",
                     "kpi": "% of DLP alerts enriched with behaviour context before analyst review",
                     "maturity": {"initial": "DLP and UEBA operate as independent tools", "established": "Alerts correlated manually; joint investigation process defined", "leading": "Automated correlation surfaces high-confidence cases; false positive rate tracked"}},
                    {"name": "Investigation & Response Procedures",
                     "kpi": "% of insider threat cases closed within defined timeframe",
                     "maturity": {"initial": "No defined investigation procedure; handled case-by-case", "established": "Playbook documented; legal, HR, and security roles defined", "leading": "Cases tracked end-to-end; outcomes feed policy and control improvements"}},
                ],
            },
            {
                "name": "Collaboration Security",
                "label": "Collaboration Tools That Don't Become a Leakage Channel",
                "note": "Collaboration platforms are configured to prevent accidental or unauthorised sharing of sensitive information (platform controls); external sharing is governed so only appropriate content reaches outside parties (external sharing governance); information barriers prevent sensitive data crossing between teams that should not share it — so productivity tools don't undermine information controls.",
                "l2": [
                    {"name": "Secure Collaboration Platform Controls",
                     "kpi": "% of collaboration platforms assessed against security baseline",
                     "maturity": {"initial": "Collaboration tools adopted without security review", "established": "Security baseline defined and applied to approved platforms", "leading": "Continuous configuration monitoring; drift detected and remediated automatically"}},
                    {"name": "External Sharing Governance",
                     "kpi": "% of external shares reviewed or expiry-controlled",
                     "maturity": {"initial": "No controls on external sharing; users share freely", "established": "Sharing policies enforced by platform; reports reviewed periodically", "leading": "External sharing audited continuously; oversharing detected and remediated"}},
                    {"name": "Information Barrier Enforcement",
                     "kpi": "% of required information barriers configured and verified",
                     "maturity": {"initial": "No barriers; all users can communicate across all teams", "established": "Barriers configured for regulated or sensitive team combinations", "leading": "Barrier effectiveness tested regularly; violations alerted in real time"}},
                    {"name": "Meeting & Channel Security",
                     "kpi": "% of external-facing meetings requiring authenticated join",
                     "maturity": {"initial": "No controls on meeting access; external attendees unverified", "established": "Meeting security policies defined; external access requires lobby admission", "leading": "Recordings governed and classified; channel membership audited automatically"}},
                ],
            },
        ],
    },
    {
        "id": "CA-03", "area": "Supply Chain & Third-Party Risk",
        "zta": "Cross-cutting", "csf": "Govern · Identify", "grp": "xc",
        "desc": "Identify, assess, and continuously monitor the security posture of third parties, vendors, and software dependencies — preventing the extended enterprise from becoming an uncontrolled attack surface.",
        "l1s": [
            {
                "name": "Vendor Risk Management",
                "label": "Suppliers Assessed for Security Before and After Onboarding",
                "note": "Every vendor is assessed against a security baseline before access is granted, with higher scrutiny for those handling sensitive systems (vendor risk tiering); security performance is monitored continuously rather than at annual review — so a supplier that deteriorates triggers action before it becomes an incident.",
                "l2": [
                    {"name": "Vendor Risk Tiering & Assessment",
                     "kpi": "% of active vendors with a current risk tier and assessment on file",
                     "maturity": {"initial": "No vendor classification; all suppliers treated equally", "established": "Tiering model applied; higher-risk vendors assessed before onboarding", "leading": "Continuous risk scoring integrated with vendor management system"}},
                    {"name": "Continuous Vendor Security Monitoring",
                     "kpi": "% of Tier-1 vendors with active security monitoring in place",
                     "maturity": {"initial": "Vendor security reviewed at contract renewal only", "established": "Annual reassessment for critical vendors; alerts for major incidents", "leading": "Real-time threat intelligence per vendor; rating deterioration triggers review"}},
                    {"name": "Contractual Security Requirements & Baseline",
                     "kpi": "% of new vendor contracts including security clauses aligned to baseline",
                     "maturity": {"initial": "Security requirements absent or inconsistent in contracts", "established": "Standard security clauses included in all new agreements", "leading": "Baseline reviewed annually; compliance evidence requested routinely"}},
                    {"name": "Right-to-Audit & Evidence Collection",
                     "kpi": "% of critical vendors with right-to-audit clause and evidence in last 24 months",
                     "maturity": {"initial": "No audit rights; assurance based on self-attestation only", "established": "Right-to-audit included for critical vendors; evidence collected at assessment", "leading": "Evidence collected via vendor portals; continuous assurance replaces point-in-time audits"}},
                ],
            },
            {
                "name": "Software Supply Chain",
                "label": "Every Software Component Tracked and Checked for Known Weaknesses",
                "note": "A complete inventory of all software components and libraries is maintained (software bill of materials); open-source dependencies are continuously monitored for newly discovered vulnerabilities (software composition analysis); only signed components from approved registries are permitted in the build pipeline (artefact signing) — so a compromised library cannot silently enter the codebase.",
                "l2": [
                    {"name": "Software Bill of Materials (SBOM)",
                     "kpi": "% of production systems with a current, machine-readable SBOM",
                     "maturity": {"initial": "No SBOM capability; component inventory unknown", "established": "SBOM generated for new applications; process defined", "leading": "SBOM auto-generated at build; queryable for vulnerability impact in minutes"}},
                    {"name": "Open-Source Dependency Governance",
                     "kpi": "% of open-source components approved via policy before use",
                     "maturity": {"initial": "Developers use libraries without review or approval", "established": "Approved library list maintained; new additions require review", "leading": "Policy enforced at build pipeline; unapproved dependencies blocked automatically"}},
                    {"name": "Dependency Vulnerability Tracking (SCA)",
                     "kpi": "Mean time to remediate critical dependency vulnerabilities (target <14 days)",
                     "maturity": {"initial": "Dependency vulnerabilities discovered reactively", "established": "SCA integrated into CI/CD; vulnerabilities surfaced to developers", "leading": "Risk-scored remediation prioritisation; SLAs enforced by pipeline gates"}},
                    {"name": "Artefact Signing & Approved Registry",
                     "kpi": "% of production build artefacts cryptographically signed",
                     "maturity": {"initial": "No signing; artefacts pulled from public registries without verification", "established": "Internal registry established; signing adopted for critical components", "leading": "All artefacts signed and verified at deployment; unsigned artefacts blocked"}},
                ],
            },
            {
                "name": "Third-Party Access",
                "label": "External Access That Expires and Leaves a Full Record",
                "note": "Vendors and contractors are granted access only for specific tasks, with permissions withdrawn automatically when the work is complete (just-in-time access); sessions are recorded so activity can be reviewed if questions arise (third-party session recording); vendor network access is isolated from internal systems — so a compromised supplier cannot move freely.",
                "l2": [
                    {"name": "Vendor Access Provisioning & Governance",
                     "kpi": "% of vendor accounts with defined scope, owner, and expiry date",
                     "maturity": {"initial": "Vendor accounts created on request with no standard process", "established": "Provisioning process documented; access scoped and time-bounded", "leading": "Automated provisioning/deprovisioning triggered by contract lifecycle"}},
                    {"name": "Time-Limited & JIT Third-Party Access",
                     "kpi": "% of vendor sessions using time-limited or just-in-time access vs. standing accounts",
                     "maturity": {"initial": "Standing vendor accounts with persistent access", "established": "Time-limited accounts standard; JIT adopted for critical systems", "leading": "All vendor access JIT by default; standing accounts eliminated"}},
                    {"name": "Third-Party Session Recording",
                     "kpi": "% of privileged vendor sessions recorded and stored per retention policy",
                     "maturity": {"initial": "No recording; vendor activity unverifiable after the fact", "established": "Session recording enabled for critical system access", "leading": "Recordings searchable and linked to tickets; anomalies flagged automatically"}},
                    {"name": "Segregated Network Access for Vendors",
                     "kpi": "% of vendor connections traversing a dedicated, isolated network segment",
                     "maturity": {"initial": "Vendors access internal network directly alongside staff", "established": "Vendor VLAN or jump host in place for critical access", "leading": "Vendor network fully isolated; lateral movement blocked by design"}},
                ],
            },
            {
                "name": "Concentration & Resilience",
                "label": "Understanding Which Suppliers You Cannot Afford to Lose",
                "note": "Suppliers that underpin critical operations are identified and mapped (critical supplier mapping); over-reliance on single providers is assessed and challenged (concentration risk) — so the organisation has a plan when a critical supplier suffers an outage, breach, or failure, rather than discovering the dependency in the moment.",
                "l2": [
                    {"name": "Critical Supplier Identification & Mapping",
                     "kpi": "% of critical business services with documented supplier dependencies",
                     "maturity": {"initial": "Critical supplier dependencies unknown until failure", "established": "Critical suppliers identified; single points of dependency mapped", "leading": "Dependency map updated quarterly; integrated with business continuity planning"}},
                    {"name": "Concentration Risk Assessment",
                     "kpi": "Number of critical services dependent on a single supplier (target: minimised)",
                     "maturity": {"initial": "Concentration risk not assessed", "established": "Concentration risks identified and documented; remediation planned", "leading": "Concentration thresholds defined; breaches trigger procurement review"}},
                    {"name": "Alternative Supplier Planning",
                     "kpi": "% of critical suppliers with a documented and tested alternative",
                     "maturity": {"initial": "No alternatives identified; full dependency on incumbent", "established": "Alternative suppliers identified for critical categories", "leading": "Alternative supply tested annually in resilience exercises"}},
                    {"name": "Supply Chain Incident Response",
                     "kpi": "Mean time to detect and contain a third-party security incident",
                     "maturity": {"initial": "No supply chain incident playbook; response improvised", "established": "Playbook defined; notification contacts maintained for critical vendors", "leading": "Supply chain incidents tracked separately; lessons feed vendor risk assessments"}},
                ],
            },
        ],
    },
    # ── PROTECT ───────────────────────────────────────────────────────────────
    {
        "id": "CA-04", "area": "Identity & Access Management",
        "zta": "Identity", "csf": "Protect", "grp": "zt",
        "desc": "Establish, govern, and continuously verify the identity of every user, service, and machine — enforcing least-privilege access across all resources.",
        "l1s": [
            {
                "name": "Authentication",
                "label": "Secure Sign-In That Needs No IT Support",
                "note": "One login works across all systems (SSO); even if a password is stolen through a fake website, it cannot be used alone to break in (phishing-resistant authentication) — so staff spend time working, not resetting accounts.",
                "l2": [
                    {"name": "Multi-Factor Authentication",
                     "kpi": "% of user accounts with MFA enrolled (target: 100%)",
                     "maturity": {"initial": "MFA optional or applied to privileged accounts only", "established": "MFA mandatory for all staff; exemptions tracked and time-limited", "leading": "Phishing-resistant methods (passkeys/FIDO2) adopted; SMS/OTP phased out"}},
                    {"name": "Phishing-Resistant / Passkey Authentication",
                     "kpi": "% of users on phishing-resistant authentication methods (FIDO2/passkeys)",
                     "maturity": {"initial": "Phishing-resistant methods not deployed", "established": "Passkeys or hardware tokens available for high-risk users and admins", "leading": "Phishing-resistant authentication default for all; legacy methods removed"}},
                    {"name": "Adaptive & Risk-Based Authentication",
                     "kpi": "% of authentication events assessed with risk signal (device, location, behaviour)",
                     "maturity": {"initial": "Static authentication policy with no risk context", "established": "Risk signals integrated; step-up authentication triggered for anomalies", "leading": "Continuous session risk re-assessed throughout the day"}},
                    {"name": "Enterprise Federation & SSO",
                     "kpi": "% of applications integrated with the central identity provider (SSO coverage)",
                     "maturity": {"initial": "Each application has its own credentials; no central identity", "established": "SSO deployed for major applications; identity provider centralised", "leading": "All applications federated; orphaned credentials monitored and eliminated"}},
                ],
            },
            {
                "name": "Identity Lifecycle & Governance",
                "label": "The Right Access for the Right Job",
                "note": "Access rights are shaped by where someone sits in the organisation (role-based access) and what their job actually requires day-to-day (attribute-based access); when people join, change roles, or leave, their access adjusts automatically (joiner-mover-leaver automation) — with no manual requests needed.",
                "l2": [
                    {"name": "Joiner-Mover-Leaver Automation",
                     "kpi": "Mean time to provision/deprovision on HR trigger (target <4h joiners, <1h leavers)",
                     "maturity": {"initial": "Access managed manually via IT tickets; delays common", "established": "Automated provisioning integrated with HR system for most applications", "leading": "Full lifecycle automation across all systems; deprovisioning verified automatically"}},
                    {"name": "Access Certification & Entitlement Review",
                     "kpi": "% of access reviews completed on schedule; % of access revoked as a result",
                     "maturity": {"initial": "No formal access review; access accumulates over time", "established": "Periodic access certification campaigns", "leading": "Continuous review with risk-prioritised focus; AI-assisted anomaly flagging"}},
                    {"name": "SaaS Identity Provisioning & SCIM",
                     "kpi": "% of SaaS applications provisioned via SCIM or equivalent automated method",
                     "maturity": {"initial": "SaaS accounts provisioned manually; deprovisioning unreliable", "established": "SCIM adopted for major SaaS; integrated with IdP", "leading": "All SaaS provisioned automatically; orphaned account detection automated"}},
                    {"name": "Role & Attribute-Based Access Control",
                     "kpi": "% of access assignments derived from roles/attributes vs. individual grants",
                     "maturity": {"initial": "Access granted individually on request; no role model", "established": "Role definitions aligned to job functions; RBAC applied for major systems", "leading": "Attribute-based policies enforce fine-grained access; role explosion monitored"}},
                ],
            },
            {
                "name": "Privileged Access",
                "label": "Admin Access That Expires When the Task Is Done",
                "note": "Powerful system access is granted only for a specific task and withdrawn automatically when finished (just-in-time access); every session is recorded (privileged session recording) — so compliance evidence exists by default, not by scramble.",
                "l2": [
                    {"name": "Privileged Credential Vault",
                     "kpi": "% of privileged accounts with credentials managed in a vault",
                     "maturity": {"initial": "Admin passwords shared in spreadsheets or messaging tools", "established": "PAM vault deployed for critical systems; credentials checked out per session", "leading": "All privileged accounts vaulted; check-out automated and audited"}},
                    {"name": "Just-in-Time & Just-Enough Access",
                     "kpi": "% of privileged access granted via JIT vs. standing privilege",
                     "maturity": {"initial": "Permanent admin accounts in widespread use", "established": "JIT access available for critical systems; standing privilege being reduced", "leading": "Standing privilege eliminated for all administrative access; JIT enforced by policy"}},
                    {"name": "Privileged Session Recording & Monitoring",
                     "kpi": "% of privileged sessions recorded; % of recordings reviewed or alerted on",
                     "maturity": {"initial": "No session recording; privileged activity unverifiable", "established": "Session recording enabled for critical systems", "leading": "Recordings analysed for anomalies automatically; unusual commands trigger alerts"}},
                    {"name": "Standing Privilege Elimination",
                     "kpi": "Number of accounts with permanent admin rights (target: zero)",
                     "maturity": {"initial": "Numerous permanent admin accounts; no review programme", "established": "Admin accounts audited; reduction programme under way", "leading": "Zero standing privilege achieved and continuously verified"}},
                ],
            },
            {
                "name": "Machine & Workload Identity",
                "label": "Every System Has Its Own Secure Identity",
                "note": "Automated processes, APIs and scripts each get their own verifiable identity rather than sharing passwords (service account governance); digital certificates renew automatically (PKI); API keys and passwords rotate without anyone having to intervene (secrets management) — so there are no long-lived shared credentials to steal.",
                "l2": [
                    {"name": "Service Account Governance",
                     "kpi": "% of service accounts with defined owner, purpose, and last-used date",
                     "maturity": {"initial": "Service accounts created ad hoc; no inventory or owner", "established": "Service account register maintained; owners assigned and reviewed", "leading": "Continuously monitored; unused accounts auto-disabled"}},
                    {"name": "PKI & Certificate Lifecycle Management",
                     "kpi": "% of certificates managed by automated lifecycle tooling; expired certs in production (target: 0)",
                     "maturity": {"initial": "Certificates managed manually; expiry causes unexpected outages", "established": "Certificate inventory maintained; renewal tracked and alerted", "leading": "Automated issuance and renewal; expiry incidents eliminated"}},
                    {"name": "Workload Identity Federation (SPIFFE/SPIRE)",
                     "kpi": "% of workload-to-workload communications using short-lived cryptographic identity",
                     "maturity": {"initial": "Workloads authenticate using shared secrets or API keys", "established": "Workload identity federation adopted for key microservice communications", "leading": "All workloads use cryptographic identity; static secrets fully replaced"}},
                    {"name": "Secrets & Dynamic Credential Management",
                     "kpi": "% of application secrets stored in a secrets manager (vs. config files)",
                     "maturity": {"initial": "Secrets hard-coded or stored in configuration files", "established": "Secrets vault deployed; developers guided to dynamic credentials", "leading": "All secrets dynamic and short-lived; secrets scanning in CI/CD blocks hard-coding"}},
                ],
            },
        ],
    },
    {
        "id": "CA-05", "area": "Device & Endpoint Trust",
        "zta": "Devices", "csf": "Protect", "grp": "zt",
        "desc": "Assess, enforce, and continuously verify the security posture of every endpoint — managed and unmanaged — as a prerequisite for resource access.",
        "l1s": [
            {
                "name": "Endpoint Management",
                "label": "Every Device Configured Correctly and Kept Up to Date",
                "note": "Every company device is set up to an approved standard and kept that way (endpoint management); software is inventoried so unapproved applications cannot run (application control); security updates are applied automatically (patch management) — so the attack surface shrinks without relying on individuals to keep up.",
                "l2": [
                    {"name": "Unified Endpoint Management (MDM/UEM)",
                     "kpi": "% of managed devices enrolled in UEM",
                     "maturity": {"initial": "Devices managed manually; no central inventory", "established": "MDM/UEM deployed; policy enforcement centralised", "leading": "Full fleet visibility; non-compliant devices automatically quarantined"}},
                    {"name": "Configuration Baseline & Hardening",
                     "kpi": "% of devices compliant with approved configuration baseline",
                     "maturity": {"initial": "No defined baseline; devices configured per individual preference", "established": "CIS benchmark or equivalent applied; compliance assessed periodically", "leading": "Continuous compliance monitoring; drift remediated automatically"}},
                    {"name": "Software Inventory & Application Control",
                     "kpi": "% of devices with software inventory current and unapproved applications blocked",
                     "maturity": {"initial": "No software inventory; users install freely", "established": "Software inventory maintained; unapproved applications flagged", "leading": "Application control enforced by allowlist; unapproved installs blocked in real time"}},
                    {"name": "Patch Lifecycle Management",
                     "kpi": "% of critical vulnerabilities patched within 14 days on managed devices",
                     "maturity": {"initial": "Patching manual and inconsistent; significant lag", "established": "Patch management tooling deployed; monthly cycle enforced", "leading": "Risk-prioritised patching; critical vulnerabilities patched within SLA automatically"}},
                ],
            },
            {
                "name": "Endpoint Protection",
                "label": "Active Defences on Every Device That Catch What Antivirus Misses",
                "note": "Each device runs monitoring that detects suspicious behaviour beyond known malware signatures (endpoint detection and response); only approved applications are permitted to run (application allowlisting); data on the device is encrypted so a stolen laptop cannot be read (full-disk encryption) — protection that works even when a threat has already landed.",
                "l2": [
                    {"name": "Endpoint Detection & Response (EDR/XDR)",
                     "kpi": "% of managed devices with EDR agent deployed; mean detection-to-alert time",
                     "maturity": {"initial": "Traditional antivirus only; no behavioural detection", "established": "EDR deployed across managed fleet; alerts investigated by SOC", "leading": "XDR correlating endpoint, identity, and network signals; automated response active"}},
                    {"name": "Anti-Malware & Behavioural Detection",
                     "kpi": "% of devices with up-to-date anti-malware signatures and behavioural engine",
                     "maturity": {"initial": "Anti-malware deployed but not consistently updated or monitored", "established": "Centralised management; definition freshness enforced", "leading": "Behavioural detection tuned to environment; false positives tracked and reduced"}},
                    {"name": "Application Allowlisting",
                     "kpi": "% of high-risk endpoints enforcing application allowlist",
                     "maturity": {"initial": "No allowlisting; all applications permitted to execute", "established": "Allowlisting applied to servers and privileged workstations", "leading": "Enforced across all endpoints; policy exceptions tracked and reviewed"}},
                    {"name": "Full-Disk Encryption & Hardware Security (TPM)",
                     "kpi": "% of laptops and mobile devices with full-disk encryption verified",
                     "maturity": {"initial": "Encryption applied inconsistently or not at all", "established": "Full-disk encryption mandated for all laptops; compliance monitored", "leading": "TPM-backed encryption verified at boot; hardware security modules integrated"}},
                ],
            },
            {
                "name": "Mobile & BYOD",
                "label": "Personal Devices That Can Safely Access Company Tools",
                "note": "Employees can use personal phones and tablets for work without the company controlling their private data (BYOD containerisation); company information sits in a separate, managed space on the device; wireless connections are secured to prevent eavesdropping (wireless security) — staff get flexibility without creating a security gap.",
                "l2": [
                    {"name": "Corporate Mobile Management",
                     "kpi": "% of corporate mobile devices enrolled and policy-compliant",
                     "maturity": {"initial": "Mobile devices managed manually with no MDM", "established": "MDM deployed for corporate mobiles; policy enforced (PIN, encryption, remote wipe)", "leading": "Automated compliance gating; non-compliant devices blocked from corporate resources"}},
                    {"name": "BYOD Containerisation",
                     "kpi": "% of BYOD users accessing corporate data through a managed container or MAM policy",
                     "maturity": {"initial": "BYOD users access corporate data without separation", "established": "MAM or container solution deployed; corporate data protected on personal devices", "leading": "Container policy tuned to data sensitivity; personal data never touched by corporate controls"}},
                    {"name": "Mobile Threat Defence (MTD)",
                     "kpi": "% of corporate and BYOD devices with MTD deployed",
                     "maturity": {"initial": "No mobile-specific threat detection", "established": "MTD deployed on corporate devices; risks scored and reported", "leading": "MTD integrated with access control; compromised devices blocked automatically"}},
                    {"name": "Wireless Access Security",
                     "kpi": "% of corporate Wi-Fi networks using certificate-based authentication (WPA2/3 Enterprise)",
                     "maturity": {"initial": "Shared-key wireless access; no device authentication", "established": "Certificate-based wireless authentication deployed for corporate networks", "leading": "Rogue access point detection active; posture integrated with network access control"}},
                ],
            },
            {
                "name": "Device Trust Assessment",
                "label": "Only Healthy Devices Are Allowed to Connect",
                "note": "Before any device connects to company systems, it is checked against security requirements — is it patched, encrypted, and uncompromised? (device posture evaluation); devices that fail are blocked automatically (compliance-gated access); checks continue while connected, not just at login — so a device that becomes unhealthy mid-session loses access.",
                "l2": [
                    {"name": "Device Posture Evaluation",
                     "kpi": "% of access requests evaluated against device posture",
                     "maturity": {"initial": "Device health not assessed as part of access decisions", "established": "Device posture checked at authentication for key systems", "leading": "Real-time posture signals feed continuous access decisions; degraded devices stepped down"}},
                    {"name": "Compliance-Gated Access (ZTNA Integration)",
                     "kpi": "% of critical systems requiring device compliance check before granting access",
                     "maturity": {"initial": "Network-based access control with no device health check", "established": "ZTNA or NAC enforces compliance gate for sensitive applications", "leading": "Dynamic access policy adjusts on real-time posture; non-compliant devices auto-quarantined"}},
                    {"name": "Hardware Root of Trust",
                     "kpi": "% of managed devices with TPM 2.0 enabled and measured boot configured",
                     "maturity": {"initial": "Hardware security features not utilised", "established": "TPM leveraged for device attestation on managed fleet", "leading": "Secure boot and measured boot enforced; tampered devices rejected at attestation"}},
                    {"name": "Continuous Compliance Monitoring",
                     "kpi": "Time between compliance drift detection and remediation (target <4h for critical)",
                     "maturity": {"initial": "Compliance checked at deployment only; drift undetected", "established": "Periodic compliance scans; non-compliance reported to administrators", "leading": "Continuous monitoring; drift triggers automated remediation or access restriction"}},
                ],
            },
        ],
    },
    {
        "id": "CA-06", "area": "Network & Infrastructure Security",
        "zta": "Networks", "csf": "Protect", "grp": "zt",
        "desc": "Segment, protect, and monitor network infrastructure — replacing perimeter-centric models with dynamic, policy-driven access based on identity and context.",
        "l1s": [
            {
                "name": "Zero Trust Network Access",
                "label": "Access That Checks Who You Are, Not Where You Are",
                "note": "Remote staff and systems connect securely without a traditional VPN (zero trust network access); access is granted based on identity and device health rather than which building or network someone is on (SASE) — so the security boundary travels with the user.",
                "l2": [
                    {"name": "ZTNA Platform & Policy Engine",
                     "kpi": "% of remote access sessions routed through ZTNA (vs. legacy VPN)",
                     "maturity": {"initial": "Perimeter VPN only; once inside, full trust assumed", "established": "ZTNA deployed alongside VPN; migration under way", "leading": "VPN fully replaced by ZTNA; policy engine enforces identity and context per request"}},
                    {"name": "Secure Remote Access / VPN Replacement",
                     "kpi": "% of users on ZTNA-based access vs. traditional VPN (migration progress)",
                     "maturity": {"initial": "Legacy VPN with broad network access; no per-application segmentation", "established": "Application-level access replacing broad VPN tunnels for key use cases", "leading": "Zero standing VPN tunnels; all remote access via identity-aware proxy"}},
                    {"name": "SASE Architecture & Convergence",
                     "kpi": "% of security functions (SWG, CASB, FWaaS) delivered through SASE vs. on-premises",
                     "maturity": {"initial": "Security enforced at perimeter only; remote users bypass controls", "established": "SASE components deployed; traffic routed through cloud security", "leading": "Full SASE operational; consistent policy regardless of user location"}},
                    {"name": "Context-Aware Access Brokering",
                     "kpi": "% of access decisions incorporating device, user role, and location context",
                     "maturity": {"initial": "Binary access decisions based on network location alone", "established": "Context signals (device posture, time, location) inform access policy", "leading": "Continuous contextual evaluation; access granted at least-privilege per session"}},
                ],
            },
            {
                "name": "Network Segmentation",
                "label": "Walls Inside the Network That Contain a Breach",
                "note": "The network is divided into separate zones (network segmentation) so that if one system is compromised, an attacker cannot move freely to others (micro-segmentation); critical systems sit behind additional barriers that filter traffic in both directions — limiting how far a breach can reach.",
                "l2": [
                    {"name": "Network Security Zone Model",
                     "kpi": "% of systems assigned to a defined security zone with documented data flows",
                     "maturity": {"initial": "Flat network; no formal zone model", "established": "Security zones defined (internet, DMZ, internal, restricted); firewalls between zones", "leading": "Zone model reviewed annually; policy violations detected and alerted automatically"}},
                    {"name": "Micro-Segmentation (Workload-to-Workload)",
                     "kpi": "% of production workloads with explicit east-west traffic policy (deny-by-default)",
                     "maturity": {"initial": "Flat east-west traffic; workloads communicate freely", "established": "Micro-segmentation applied to critical application tiers", "leading": "All workloads covered; unused paths automatically closed; policy defined as code"}},
                    {"name": "DMZ Architecture & Isolation",
                     "kpi": "% of internet-facing services sitting in a properly isolated DMZ",
                     "maturity": {"initial": "Internet-facing services on the same network as internal systems", "established": "DMZ defined and enforced for all internet-facing services", "leading": "DMZ continuously validated; internet-facing surface minimised and monitored"}},
                    {"name": "East-West Traffic Control",
                     "kpi": "Ratio of monitored to unmonitored east-west traffic paths",
                     "maturity": {"initial": "No visibility or control of internal lateral traffic", "established": "East-west traffic logged; suspicious lateral movement alerted", "leading": "All east-west paths explicitly permitted; anomalous communication blocked automatically"}},
                ],
            },
            {
                "name": "Network Security Controls",
                "label": "Filters and Guards That Block Harmful Traffic",
                "note": "All network traffic passes through filters that identify and block malicious content (next-generation firewall / intrusion prevention); patterns in traffic are analysed to catch threats that slip through (network detection and response); domain lookups are screened to prevent connections to harmful sites (DNS security).",
                "l2": [
                    {"name": "Next-Generation Firewall & IPS",
                     "kpi": "% of network perimeter covered by NGFW with IPS signatures updated within 24h",
                     "maturity": {"initial": "Basic stateful firewall; no IPS or application-layer inspection", "established": "NGFW deployed at perimeter; IPS rules maintained and tested", "leading": "NGFW policy managed as code; rule reviews automated; IPS effectiveness tracked"}},
                    {"name": "Network Detection & Response (NDR)",
                     "kpi": "% of network segments with NDR coverage; mean time to detect lateral movement",
                     "maturity": {"initial": "Network traffic not analysed for threats; detection relies on endpoint alone", "established": "NDR deployed on key segments; alerts integrated into SOC workflow", "leading": "Full network visibility including encrypted traffic analysis; integrated with SIEM/XDR"}},
                    {"name": "DNS Security (Protective DNS, DNSSEC)",
                     "kpi": "% of outbound DNS queries routed through protective DNS; DNSSEC validation rate",
                     "maturity": {"initial": "Standard DNS with no filtering or validation", "established": "Protective DNS deployed; known malicious domains blocked", "leading": "DNS over HTTPS enforced; DNSSEC validation active; DNS anomalies alerted"}},
                    {"name": "DDoS Protection",
                     "kpi": "Time to activate DDoS mitigation; % of internet-facing services with DDoS protection",
                     "maturity": {"initial": "No DDoS mitigation; relies on ISP best-effort", "established": "DDoS protection service in place for critical internet-facing assets", "leading": "Automated detection and scrubbing; capacity and effectiveness tested annually"}},
                ],
            },
            {
                "name": "Operational Technology (OT/ICS)",
                "label": "Industrial Systems Kept Separate From Office Networks",
                "note": "Systems that run physical operations — factories, utilities, building controls — are isolated from standard office networks (OT/ICS segmentation) so a breach on either side cannot cross to the other; data flows one way only where required (unidirectional gateway) and every industrial device is tracked and monitored.",
                "l2": [
                    {"name": "OT Network Isolation",
                     "kpi": "% of OT/ICS networks with documented and verified isolation from corporate IT",
                     "maturity": {"initial": "OT and IT networks interconnected; no defined boundary", "established": "OT network isolated with defined interconnection points and controls", "leading": "OT/IT boundary continuously monitored; any connection attempt logged and alerted"}},
                    {"name": "Purdue Model Segmentation",
                     "kpi": "% of OT assets assigned to correct Purdue level with enforced inter-level controls",
                     "maturity": {"initial": "No segmentation model applied; flat OT network", "established": "Purdue levels defined; inter-level firewalls in place", "leading": "Zone-to-zone traffic continuously validated against approved flows"}},
                    {"name": "Unidirectional Gateway Architecture",
                     "kpi": "% of OT-to-IT data flows enforced via unidirectional (data diode) architecture",
                     "maturity": {"initial": "Bidirectional connections between OT and IT; attack paths in both directions", "established": "Unidirectional gateways deployed for highest-risk OT-IT connections", "leading": "All OT-to-IT data flows one-directional by design; no return path possible"}},
                    {"name": "OT Asset Visibility & Inventory",
                     "kpi": "% of OT/ICS devices in a current, accurate asset inventory",
                     "maturity": {"initial": "No OT asset inventory; devices unknown until failure", "established": "Passive OT asset discovery deployed; inventory maintained", "leading": "Real-time OT asset inventory with vulnerability and firmware tracking"}},
                ],
            },
        ],
    },
    {
        "id": "CA-07", "area": "Application & API Security",
        "zta": "Applications", "csf": "Protect", "grp": "zt",
        "desc": "Design, build, and operate applications and APIs with security embedded throughout the software delivery lifecycle — treating code, dependencies, and runtime as the attack surface.",
        "l1s": [
            {
                "name": "Secure Development",
                "label": "Security Built Into Software Before It Ships",
                "note": "Security requirements and potential attack scenarios are considered at the design stage (threat modelling); developers are equipped with guidance and tooling (developer security enablement); checks are embedded at each stage of the build pipeline (secure SDLC) — so problems are caught early when they are cheap to fix.",
                "l2": [
                    {"name": "Secure SDLC Policy & Phase Gates",
                     "kpi": "% of projects completing required security gates before release",
                     "maturity": {"initial": "Security reviewed ad hoc or only after incidents", "established": "Secure SDLC defined; checkpoints at design, build, and release", "leading": "Security gates automated in CI/CD; release blocked on critical findings"}},
                    {"name": "Threat Modelling",
                     "kpi": "% of new significant projects completing a threat model before development",
                     "maturity": {"initial": "No formal threat modelling; design without adversarial thinking", "established": "Threat modelling conducted for major projects; findings tracked", "leading": "Embedded in sprint planning; automated tooling assists coverage"}},
                    {"name": "Security Architecture Review",
                     "kpi": "% of architecturally significant changes reviewed for security before approval",
                     "maturity": {"initial": "Security architecture review optional and infrequent", "established": "Review mandated for new systems and significant changes", "leading": "Integrated with enterprise architecture governance; findings drive standards"}},
                    {"name": "Developer Security Enablement",
                     "kpi": "% of developers with security tooling in their IDE; mean time to fix findings",
                     "maturity": {"initial": "Developers lack security tools in their daily workflow", "established": "Security tooling (SAST, secrets scanning) available in developer environments", "leading": "Security findings surface in IDE; fix rates tracked by team; champions drive adoption"}},
                ],
            },
            {
                "name": "Application Security Testing",
                "label": "Applications Tested for Weaknesses Before They Reach Customers",
                "note": "Code is automatically scanned for common vulnerabilities as it is written (static analysis); running applications are probed for exploitable flaws (dynamic analysis); third-party libraries are checked for known weaknesses (software composition analysis) — so vulnerabilities are found by the team, not by attackers.",
                "l2": [
                    {"name": "Static Analysis (SAST)",
                     "kpi": "% of code repositories with SAST enabled; % of critical findings resolved before release",
                     "maturity": {"initial": "No automated code scanning; manual review only", "established": "SAST integrated into CI/CD; high-severity findings block merge", "leading": "SAST tuned to reduce false positives; fix rate and time tracked by team"}},
                    {"name": "Dynamic Analysis (DAST)",
                     "kpi": "% of web applications scanned by DAST in the last quarter",
                     "maturity": {"initial": "No dynamic testing; production is the test environment", "established": "DAST run against staging environments before major releases", "leading": "DAST automated in CI/CD; findings risk-scored and routed to owning team"}},
                    {"name": "Software Composition Analysis (SCA)",
                     "kpi": "% of repositories with SCA enabled; % of critical dependency CVEs remediated within SLA",
                     "maturity": {"initial": "Third-party dependencies used without review", "established": "SCA integrated into build pipeline; vulnerable dependencies flagged", "leading": "SCA results feed into SBOM; critical CVE remediation enforced by pipeline gate"}},
                    {"name": "Penetration Testing",
                     "kpi": "% of business-critical applications tested by external pen test in the last 12 months",
                     "maturity": {"initial": "No penetration testing programme; testing only after incidents", "established": "Annual penetration testing for critical applications; findings tracked to closure", "leading": "Risk-based testing calendar; findings feed threat model updates; retests confirm remediation"}},
                ],
            },
            {
                "name": "API Security",
                "label": "APIs That Only Do What They Are Supposed To Do",
                "note": "All API traffic passes through a central gateway that enforces rate limits and access controls (API gateway); callers must prove who they are using a standard protocol (OAuth/OIDC); inputs are validated so malformed or malicious requests are rejected — limiting what an attacker can do even if they reach the API.",
                "l2": [
                    {"name": "API Gateway & Traffic Management",
                     "kpi": "% of external APIs routed through a managed gateway with rate limiting and auth enforcement",
                     "maturity": {"initial": "APIs exposed directly without gateway; no centralised control", "established": "API gateway deployed; authentication and rate limiting enforced", "leading": "API gateway policy managed as code; traffic anomalies alerted in real time"}},
                    {"name": "Authentication & Authorisation (OAuth 2.0 / OIDC)",
                     "kpi": "% of APIs requiring authentication using a standards-based protocol",
                     "maturity": {"initial": "Bespoke or no authentication on internal APIs", "established": "OAuth 2.0/OIDC adopted for customer-facing APIs", "leading": "All APIs require authentication; least-privilege scopes enforced; token lifetimes minimised"}},
                    {"name": "Input Validation & Schema Enforcement",
                     "kpi": "% of APIs with schema validation enforced at gateway or application layer",
                     "maturity": {"initial": "No input validation; APIs accept arbitrary payloads", "established": "Schema validation applied to critical API endpoints", "leading": "Schema validation at gateway for all APIs; malformed requests blocked and alerted"}},
                    {"name": "SOA & Microservice Security",
                     "kpi": "% of service-to-service calls authenticated using mTLS or equivalent",
                     "maturity": {"initial": "Internal microservices communicate without authentication", "established": "Service mesh or mTLS adopted for critical service interactions", "leading": "All service-to-service calls authenticated and authorised; zero-trust within the mesh"}},
                ],
            },
            {
                "name": "Runtime Application Protection",
                "label": "Active Protection for Applications Running in Production",
                "note": "Malicious web requests are blocked before they reach the application (web application firewall); secrets and credentials are stored and rotated securely rather than hard-coded (secrets management) — so an application that has a vulnerability is harder to exploit, and credentials cannot be extracted from code.",
                "l2": [
                    {"name": "Web Application Firewall (WAF)",
                     "kpi": "% of internet-facing applications protected by a WAF with up-to-date rule sets",
                     "maturity": {"initial": "No WAF; applications directly exposed to internet", "established": "WAF deployed for customer-facing applications; OWASP Top 10 rules active", "leading": "WAF in blocking mode for all apps; custom rules tuned; false positive rate <1%"}},
                    {"name": "Runtime Application Self-Protection (RASP)",
                     "kpi": "% of high-risk applications instrumented with RASP",
                     "maturity": {"initial": "No runtime protection; attacks detected only at network layer", "established": "RASP deployed on highest-risk applications", "leading": "RASP integrated with SOC alerting; attack telemetry feeds threat intelligence"}},
                    {"name": "Secrets Detection & Vault Integration",
                     "kpi": "% of repositories scanned for secrets; secrets found in code (target: zero)",
                     "maturity": {"initial": "Secrets embedded in code and repositories; no detection", "established": "Secrets scanning in CI/CD; findings alerted to developers", "leading": "Pre-commit hooks block secret introduction; vault integration mandated for new applications"}},
                    {"name": "Secure Application Baseline",
                     "kpi": "% of production applications compliant with the defined security baseline",
                     "maturity": {"initial": "No security baseline for applications; configuration varies widely", "established": "Baseline defined and communicated; compliance assessed at release", "leading": "Baseline compliance validated continuously; non-compliant applications flagged"}},
                ],
            },
        ],
    },
    {
        "id": "CA-08", "area": "Data & Information Protection",
        "zta": "Data", "csf": "Protect", "grp": "zt",
        "desc": "Classify, protect, and govern data throughout its entire lifecycle — at rest, in transit, in use, and in shared contexts — including future-proof cryptographic resilience.",
        "l1s": [
            {
                "name": "Data Classification & Governance",
                "label": "Knowing What Data You Hold and How Sensitive It Is",
                "note": "Data is labelled by sensitivity so the right controls are applied automatically (data classification); all data stores are discovered and inventoried (data discovery); retention periods are defined so data is deleted when no longer needed (retention policy) — reducing both risk and regulatory exposure.",
                "l2": [
                    {"name": "Data Classification Framework",
                     "kpi": "% of data stores with a current, verified classification label",
                     "maturity": {"initial": "No classification framework; all data treated equally", "established": "Classification scheme defined; training completed", "leading": "Auto-classification active on new data; label accuracy validated quarterly"}},
                    {"name": "Data Discovery & Inventory",
                     "kpi": "% of cloud and on-premises data stores discovered and catalogued",
                     "maturity": {"initial": "No data inventory; data location unknown", "established": "Data discovery tooling deployed; key data stores catalogued", "leading": "Continuous discovery; new data stores detected and classified automatically"}},
                    {"name": "Retention, Archival & Disposal Policy",
                     "kpi": "% of data categories with defined and enforced retention schedules",
                     "maturity": {"initial": "Data retained indefinitely by default; no disposal process", "established": "Retention policy defined; scheduled disposal processes in place", "leading": "Automated retention enforcement; disposal verified and audited"}},
                    {"name": "Privacy by Design",
                     "kpi": "% of new processing activities completing a Privacy Impact Assessment (PIA)",
                     "maturity": {"initial": "Privacy considered only when a regulator enquires", "established": "PIA process mandated for new systems handling personal data", "leading": "Privacy controls embedded in development standards; PIAs integrated into project approval"}},
                ],
            },
            {
                "name": "Data Loss Prevention",
                "label": "Sensitive Data Cannot Leave Without Authorisation",
                "note": "Attempts to copy or send sensitive data through email, USB drives, or cloud services are detected and blocked (data loss prevention); where data must be shared externally, access rights travel with the document (information rights management) — so sensitive information stays under control even after it is shared.",
                "l2": [
                    {"name": "Endpoint DLP",
                     "kpi": "% of managed endpoints with DLP agent deployed and policy active",
                     "maturity": {"initial": "No endpoint DLP; data exfiltration via USB/email undetected", "established": "Endpoint DLP deployed; high-risk actions alerted and logged", "leading": "DLP policy tuned to data classification; block actions enforced for critical data"}},
                    {"name": "Network DLP",
                     "kpi": "% of egress traffic inspected by network DLP",
                     "maturity": {"initial": "No inspection of outbound traffic for sensitive content", "established": "Network DLP deployed at key egress points; sensitive patterns defined", "leading": "Encrypted traffic inspected (TLS inspection); DLP alerts integrated with SIEM"}},
                    {"name": "Cloud DLP",
                     "kpi": "% of cloud storage and collaboration platforms covered by DLP policy",
                     "maturity": {"initial": "Cloud data movement not monitored", "established": "Cloud DLP deployed for primary SaaS platforms; alerts configured", "leading": "CASB-integrated cloud DLP; real-time blocking of sensitive data upload/share"}},
                    {"name": "Information Rights Management (IRM/DRM)",
                     "kpi": "% of highly sensitive documents protected with IRM controls",
                     "maturity": {"initial": "No IRM; files freely shared and copied after leaving organisation", "established": "IRM available and mandated for classified documents", "leading": "IRM applied automatically by classification label; access revocable post-distribution"}},
                ],
            },
            {
                "name": "Cryptography & Key Management",
                "label": "Data Protected by Encryption Throughout Its Lifecycle",
                "note": "Sensitive data is encrypted whether stored on a server or moving across a network; encryption keys are managed in a dedicated secure service rather than left in application code (key management service); where regulations require it, encryption is applied before data leaves the user's device (client-side encryption) — so a breach yields ciphertext, not readable records.",
                "l2": [
                    {"name": "Encryption at Rest & in Transit",
                     "kpi": "% of data stores encrypted at rest; % of network traffic using TLS 1.2+",
                     "maturity": {"initial": "Encryption applied inconsistently; legacy protocols in use", "established": "Encryption mandated for all data stores and transit; TLS version enforced", "leading": "Compliance continuously monitored; deprecated algorithms auto-detected"}},
                    {"name": "Client-Side Encryption",
                     "kpi": "% of applicable systems where data is encrypted before leaving user control",
                     "maturity": {"initial": "Encryption handled by server; provider can access plaintext", "established": "Client-side encryption available for highest-sensitivity use cases", "leading": "Client-side encryption default for regulated data; key management client-controlled"}},
                    {"name": "Key Management Service (KMS/HSM)",
                     "kpi": "% of encryption keys managed via a dedicated KMS (not embedded in application code)",
                     "maturity": {"initial": "Keys stored alongside encrypted data or hard-coded in applications", "established": "KMS deployed; keys separated from data; rotation enforced", "leading": "HSM used for critical keys; automated rotation; key usage audited"}},
                    {"name": "Post-Quantum Cryptography Migration",
                     "kpi": "% of cryptographic inventory assessed for quantum vulnerability; migration plan in place",
                     "maturity": {"initial": "No awareness of quantum risk; no cryptographic inventory", "established": "Cryptographic inventory complete; quantum-vulnerable algorithms identified", "leading": "PQC migration plan approved and in progress; timelines aligned to NIST PQC standards"}},
                ],
            },
            {
                "name": "Secure Data Exchange",
                "label": "Data Shared Externally Arrives Intact and Unread by Others",
                "note": "Files transferred to external parties travel through secured channels (secure file transfer); email domains are protected so messages cannot be forged to impersonate the organisation (DMARC/DKIM/SPF); where possible, sensitive values are replaced with tokens so the real data never leaves the secure environment (tokenisation).",
                "l2": [
                    {"name": "Secure File Transfer",
                     "kpi": "% of regulated external file transfers using approved secure transfer methods",
                     "maturity": {"initial": "Files shared via email or consumer services without controls", "established": "Managed file transfer (MFT) deployed for regulated data", "leading": "All external transfers logged and auditable; encryption enforced end-to-end"}},
                    {"name": "Email Transport Security (DMARC/DKIM/SPF)",
                     "kpi": "DMARC policy at reject/quarantine (yes/no); % of domains with full SPF/DKIM/DMARC",
                     "maturity": {"initial": "No DMARC/DKIM/SPF; domain can be spoofed freely", "established": "SPF and DKIM configured; DMARC in monitoring mode", "leading": "DMARC at reject policy; all domains covered; spoofing attempts reported"}},
                    {"name": "Data Sharing Agreements & Controls",
                     "kpi": "% of third-party data sharing relationships covered by a signed agreement",
                     "maturity": {"initial": "Data shared with third parties without formal agreements", "established": "Data sharing agreements in place for known relationships", "leading": "Agreements tied to data classification; controls verified before transfer"}},
                    {"name": "Tokenisation & Data Masking",
                     "kpi": "% of systems storing payment or regulated personal data using tokenisation or masking",
                     "maturity": {"initial": "Real data used in all environments including development and testing", "established": "Tokenisation applied to payment data; masking used in non-production", "leading": "Tokenisation extended to all regulated categories; masking automated in data pipelines"}},
                ],
            },
        ],
    },
    {
        "id": "CA-09", "area": "Cloud & Platform Security",
        "zta": "Infrastructure", "csf": "Protect", "grp": "zt",
        "desc": "Secure cloud infrastructure, workloads, and platform services across multi-cloud and hybrid environments — enforcing the shared responsibility model and preventing cloud-native misconfiguration.",
        "l1s": [
            {
                "name": "Cloud Posture Management",
                "label": "Cloud Settings Checked Continuously for Dangerous Misconfigurations",
                "note": "Every cloud account is scanned against security benchmarks to catch misconfigured storage, open firewall rules, and missing controls (cloud security posture management); infrastructure templates are validated before deployment (infrastructure-as-code scanning) — so misconfigurations are caught before they become incidents.",
                "l2": [
                    {"name": "Cloud Security Posture Management (CSPM)",
                     "kpi": "% of cloud accounts covered by CSPM; mean time to remediate critical misconfigurations",
                     "maturity": {"initial": "Cloud accounts not monitored for misconfigurations", "established": "CSPM deployed across primary cloud platforms; critical findings alerted", "leading": "All cloud accounts covered; auto-remediation active; MTTR tracked"}},
                    {"name": "Infrastructure-as-Code Security Scanning",
                     "kpi": "% of IaC repositories with security scanning enabled in CI/CD pipeline",
                     "maturity": {"initial": "Infrastructure deployed manually; no security review of templates", "established": "IaC scanning integrated into pipeline; critical misconfigurations block deployment", "leading": "Policy-as-code enforces security standards; drift between IaC and deployed state detected"}},
                    {"name": "Compliance Benchmark Enforcement (CIS, NIST)",
                     "kpi": "% of cloud resources compliant with organisation's chosen benchmark (e.g. CIS Level 2)",
                     "maturity": {"initial": "No benchmark applied; cloud configured to defaults", "established": "Benchmark selected and assessed; compliance score tracked", "leading": "Continuous compliance monitoring; benchmark updates automatically assessed for impact"}},
                    {"name": "Cloud Drift Detection & Automated Remediation",
                     "kpi": "Mean time between configuration drift detection and remediation (target <2h for critical)",
                     "maturity": {"initial": "No drift detection; configuration changes untracked", "established": "Drift detection alerts generated; manual remediation initiated", "leading": "Automated remediation for approved finding types; human approval for destructive changes"}},
                ],
            },
            {
                "name": "Workload Protection",
                "label": "Servers and Containers Protected While They Run",
                "note": "Cloud workloads — servers, containers, and serverless functions — are hardened to a known baseline and monitored for threats (cloud workload protection); container images are scanned for vulnerabilities before deployment (container security) — so threats inside a workload are detected and contained rather than left to spread.",
                "l2": [
                    {"name": "Cloud Workload Protection (CWPP)",
                     "kpi": "% of cloud workloads with CWPP agent or equivalent runtime protection",
                     "maturity": {"initial": "No runtime protection in cloud; endpoint security model does not extend", "established": "CWPP deployed for critical workloads; runtime threats alerted", "leading": "Full workload coverage; CWPP integrated with SIEM; automated response playbooks active"}},
                    {"name": "Container & Kubernetes Security",
                     "kpi": "% of container images passing security scan before deployment; % of clusters with runtime policy",
                     "maturity": {"initial": "Containers deployed from unscanned images; no runtime policies", "established": "Image scanning in CI/CD; Kubernetes RBAC enforced; privileged containers reviewed", "leading": "Admission controller blocks non-compliant images; runtime behaviour monitored and alerted"}},
                    {"name": "Serverless Security",
                     "kpi": "% of serverless functions with least-privilege execution role and dependency scanning",
                     "maturity": {"initial": "Serverless functions deployed with broad permissions and unscanned dependencies", "established": "Function permissions reviewed at deployment; dependency scanning in CI/CD", "leading": "Serverless security integrated with CSPM; overpermissioned functions auto-flagged"}},
                    {"name": "Server Hardening & Baseline",
                     "kpi": "% of servers compliant with approved hardening baseline (CIS benchmark or equivalent)",
                     "maturity": {"initial": "Server configuration varies by administrator; no baseline", "established": "Hardening standard defined and applied at provisioning", "leading": "Configuration compliance continuously verified; non-compliant servers auto-remediated"}},
                ],
            },
            {
                "name": "Cloud Identity & Entitlements",
                "label": "Cloud Access Rights That Don't Accumulate Unchecked",
                "note": "Every permission granted in cloud platforms is reviewed and minimised so accounts hold only what they need (cloud entitlement management); SaaS applications are checked for overly permissive configurations (SaaS security posture management) — so excessive cloud permissions cannot be exploited by attackers or abused by insiders.",
                "l2": [
                    {"name": "Cloud IAM Governance",
                     "kpi": "% of cloud IAM policies reviewed in the last 90 days; number of root/admin accounts in active use",
                     "maturity": {"initial": "Cloud IAM managed ad hoc; root credentials used routinely", "established": "Cloud IAM reviewed periodically; least-privilege enforced for new roles", "leading": "Continuous IAM analysis; unused roles and permissions auto-flagged for removal"}},
                    {"name": "Cloud Infrastructure Entitlement Management (CIEM)",
                     "kpi": "% of cloud entitlements with more permissions than used in the last 30 days",
                     "maturity": {"initial": "No visibility of effective cloud permissions; entitlement sprawl undetected", "established": "CIEM tool deployed; over-provisioned accounts identified", "leading": "Automated right-sizing of cloud permissions; entitlement drift alerted within 24h"}},
                    {"name": "SaaS Security Posture Management (SSPM)",
                     "kpi": "% of business-critical SaaS applications assessed by SSPM",
                     "maturity": {"initial": "SaaS application configuration not reviewed; vendor defaults accepted", "established": "SSPM deployed for major SaaS; critical misconfigurations remediated", "leading": "All SaaS applications in SSPM scope; configuration drift alerted and tracked"}},
                    {"name": "Cross-Cloud Identity Federation",
                     "kpi": "% of cloud workload identities using centralised federation (vs. per-cloud local accounts)",
                     "maturity": {"initial": "Separate identity stores per cloud provider; no central governance", "established": "Federation established between primary IdP and main cloud platforms", "leading": "All clouds federated; JIT cloud access from central IdP; no persistent cloud admin accounts"}},
                ],
            },
            {
                "name": "Cloud Architecture Security",
                "label": "Cloud Infrastructure Designed to Be Secure by Default",
                "note": "Cloud networks are segmented and traffic routed through private endpoints where possible (VPC design); storage, databases, and backups are encrypted and access-controlled by default (cloud storage security); firewalls and security groups are defined in code and version-controlled — so the architecture itself enforces security rather than relying on manual checks.",
                "l2": [
                    {"name": "VPC Design & Private Endpoints",
                     "kpi": "% of cloud services accessed via private endpoints (vs. public internet exposure)",
                     "maturity": {"initial": "Cloud resources exposed via public endpoints by default", "established": "Private endpoints adopted for key services (databases, storage); public access restricted", "leading": "Private-by-default architecture enforced in IaC; public exposure continuously audited"}},
                    {"name": "Cloud-Native Firewall & Security Groups",
                     "kpi": "% of security group rules reviewed and justified in last 90 days; 0.0.0.0/0 inbound rules (target: zero)",
                     "maturity": {"initial": "Security groups overly permissive; no review process", "established": "Security group review process in place; open rules flagged and remediated", "leading": "Security groups managed as code; no permissive rules in production"}},
                    {"name": "Cloud Key Management & Encryption",
                     "kpi": "% of data stores encrypted with customer-managed keys (CMK)",
                     "maturity": {"initial": "Provider-managed encryption with no customer control over keys", "established": "CMK adopted for sensitive data stores; key rotation enabled", "leading": "Key usage audited; access to CMK limited by condition-based IAM; HSM-backed for critical data"}},
                    {"name": "Cloud Storage Security Controls",
                     "kpi": "% of storage buckets/blobs with public access blocked; % with versioning and MFA-delete",
                     "maturity": {"initial": "Storage buckets publicly accessible by default; no lifecycle controls", "established": "Public access blocked; access logging enabled; bucket policies reviewed", "leading": "Continuous storage posture monitoring; public access auto-remediated; object-level logging"}},
                ],
            },
        ],
    },
    {
        "id": "CA-10", "area": "AI & Agentic Security",
        "zta": "Cross-cutting (emerging)", "csf": "Govern · Protect", "grp": "zt",
        "desc": "Govern, secure, and assure AI systems and autonomous agents — addressing AI-specific attack surfaces, model integrity, and the novel trust and control challenges introduced by agentic architectures.",
        "l1s": [
            {
                "name": "AI Governance",
                "label": "Every AI System Assessed and Approved Before It Goes Live",
                "note": "All AI models in use are inventoried and classified by the risk they carry (AI model inventory); each use case is assessed for bias, fairness, and explainability before approval (responsible AI); regulatory requirements such as the EU AI Act are tracked and mapped to each system (AI regulatory compliance) — so AI is adopted with eyes open, not discovered after the fact.",
                "l2": [
                    {"name": "AI Model Inventory & Risk Classification",
                     "kpi": "% of AI systems in production recorded with a current risk classification",
                     "maturity": {"initial": "No inventory of AI systems; shadow AI undetected", "established": "AI inventory maintained; models classified by risk category", "leading": "Continuous AI system discovery; risk classification updated on model change"}},
                    {"name": "AI Use Case Assessment & Approval",
                     "kpi": "% of new AI use cases completing formal risk assessment before deployment",
                     "maturity": {"initial": "AI deployed without review; use cases approved informally", "established": "Assessment process defined; new AI use cases reviewed for risk and compliance", "leading": "Assessment integrated into project governance; approvals tracked and auditable"}},
                    {"name": "Responsible AI (Bias, Fairness, Explainability)",
                     "kpi": "% of AI models in high-risk use cases assessed for bias and explainability",
                     "maturity": {"initial": "No responsible AI process; model behaviour not validated", "established": "Bias and fairness assessments conducted for high-risk decisions", "leading": "Continuous monitoring for model drift and bias; explainability tooling embedded in development"}},
                    {"name": "AI Regulatory Compliance (EU AI Act, NIST AI RMF)",
                     "kpi": "% of AI systems categorised under EU AI Act; compliance status of high-risk systems",
                     "maturity": {"initial": "No mapping of AI systems to regulatory requirements", "established": "AI systems mapped to EU AI Act risk tiers; obligations identified", "leading": "Compliance tracked per system; documentation maintained for regulatory inspection"}},
                ],
            },
            {
                "name": "AI Security Controls",
                "label": "Protecting AI Systems From Being Manipulated or Misused",
                "note": "Inputs to AI systems are monitored and filtered to prevent attackers from hijacking the model's behaviour through crafted prompts (prompt injection detection); outputs are also monitored for unexpected or harmful responses; all interactions are logged so misuse can be investigated — so AI systems remain under the organisation's control even when exposed to adversarial users.",
                "l2": [
                    {"name": "Prompt Injection Detection & Filtering",
                     "kpi": "% of AI system inputs scanned for prompt injection; blocked injection attempts per month",
                     "maturity": {"initial": "No controls on AI inputs; prompt injection risk unaddressed", "established": "Input filtering deployed for customer-facing AI; known patterns blocked", "leading": "Adaptive detection tuned to model behaviour; injection attempts feed threat intelligence"}},
                    {"name": "AI Input/Output Monitoring",
                     "kpi": "% of AI interactions logged with input and output captured for review",
                     "maturity": {"initial": "AI inputs and outputs not logged; misuse undetectable", "established": "Logging enabled; anomalous outputs flagged for review", "leading": "Real-time monitoring of AI outputs; policy violations trigger automated response"}},
                    {"name": "Model Access Controls & Authorisation",
                     "kpi": "% of AI models accessible only through authenticated and authorised interfaces",
                     "maturity": {"initial": "Model APIs publicly accessible without authentication", "established": "Authentication required for all model access; access scoped by use case", "leading": "Attribute-based access to models; usage quotas and abuse detection active"}},
                    {"name": "AI Audit Logging & Traceability",
                     "kpi": "% of AI decisions in regulated use cases with a complete, auditable log",
                     "maturity": {"initial": "No audit trail for AI decisions; accountability impossible", "established": "Decision logging implemented for high-risk AI use cases", "leading": "Full chain of custody; logs tamper-evident; linked to specific model version"}},
                ],
            },
            {
                "name": "Agentic Security",
                "label": "Keeping Autonomous AI Within Strict Boundaries",
                "note": "AI agents are given the minimum permissions needed for each task and no more (agent least privilege); consequential actions require a human to confirm before the agent proceeds (human-in-the-loop oversight); the scope of what an agent can affect is limited so a compromised or misbehaving agent cannot cause widespread damage (blast radius containment).",
                "l2": [
                    {"name": "Minimal Tool Authority (Agent Least Privilege)",
                     "kpi": "% of AI agents operating under defined, minimal tool permission sets",
                     "maturity": {"initial": "AI agents granted broad permissions for convenience; blast radius not considered", "established": "Agent permissions scoped to task requirements; review process in place", "leading": "Tool permissions granted just-in-time per task; usage audited and anomalies alerted"}},
                    {"name": "Human-in-the-Loop Oversight Gates",
                     "kpi": "% of consequential agent actions requiring human confirmation before execution",
                     "maturity": {"initial": "Agents execute all actions autonomously without oversight", "established": "Human confirmation gates defined for high-impact action categories", "leading": "Risk-scored action classification; confirmation thresholds tuned and tested regularly"}},
                    {"name": "Agent Blast Radius Containment",
                     "kpi": "Maximum scope of impact achievable by a single compromised agent (documented and bounded)",
                     "maturity": {"initial": "No blast radius analysis; agent failure has unbounded impact", "established": "Blast radius documented per agent; isolation boundaries defined", "leading": "Technical containment enforced by sandboxing; lateral movement by compromised agents blocked"}},
                    {"name": "Agentic Orchestration Security",
                     "kpi": "% of multi-agent workflows with defined trust boundaries and inter-agent authentication",
                     "maturity": {"initial": "Multi-agent pipelines operate without trust controls", "established": "Inter-agent authentication implemented; orchestration flow documented", "leading": "Zero-trust applied within agent networks; orchestration anomalies detected and alerted"}},
                ],
            },
            {
                "name": "AI Supply Chain & Integrity",
                "label": "AI Models From Trusted Sources, Tested Before Deployment",
                "note": "Every model in use is traced to its origin and verified as unmodified (model provenance); only models from an approved registry are permitted in production; training data is governed to prevent poisoning; models are tested against adversarial scenarios before going live (AI red teaming) — so the organisation is not unknowingly running a compromised or biased model.",
                "l2": [
                    {"name": "Model Provenance & Signing",
                     "kpi": "% of models in production with verified provenance and cryptographic signature",
                     "maturity": {"initial": "Models downloaded from public sources without verification", "established": "Model signatures verified before deployment; source documented", "leading": "Signature verification automated in deployment pipeline; unsigned models blocked"}},
                    {"name": "Approved Model Registry",
                     "kpi": "% of production AI systems running only from the approved model registry",
                     "maturity": {"initial": "Teams source models independently from any available repository", "established": "Approved registry established; model sourcing policy defined", "leading": "Unapproved model usage detected and blocked; registry updated through governed process"}},
                    {"name": "Training Data Governance",
                     "kpi": "% of models trained on internally developed or privacy-reviewed data sources",
                     "maturity": {"initial": "Training data sourced without review; provenance unknown", "established": "Data sources documented; PII and licensed content removed before training", "leading": "Training data lineage tracked end-to-end; data poisoning detection active"}},
                    {"name": "AI Red Teaming & Adversarial Testing",
                     "kpi": "% of high-risk AI systems tested by red team or adversarial evaluation before production",
                     "maturity": {"initial": "No adversarial testing; model robustness assumed", "established": "Red teaming conducted for high-risk AI systems before deployment", "leading": "Continuous adversarial evaluation; findings feed model hardening and detection rules"}},
                ],
            },
        ],
    },
    # ── OPERATE ───────────────────────────────────────────────────────────────
    {
        "id": "CA-11", "area": "Threat Detection & Security Operations",
        "zta": "Visibility & Analytics", "csf": "Detect · Identify", "grp": "ops",
        "desc": "Continuously monitor the entire attack surface, detect adversarial activity early, and operate a coordinated security operations function — intelligence-led and MITRE ATT&CK-aligned.",
        "l1s": [
            {
                "name": "Security Monitoring",
                "label": "Suspicious Activity Spotted Early Across Every System",
                "note": "Logs and events from every system are collected and correlated to surface threats that no single source would reveal (SIEM); unusual patterns in user and system behaviour trigger alerts (behavioural analytics) — giving the security team visibility before damage spreads.",
                "l2": [
                    {"name": "SIEM: Log Aggregation & Correlation",
                     "kpi": "% of critical systems with logs ingested into SIEM; mean time to detect (MTTD)",
                     "maturity": {"initial": "Logs collected but not centralised or analysed", "established": "SIEM deployed; log sources prioritised and normalised; correlation rules active", "leading": "Full log coverage; detection engineering practice; MTTD tracked and improving"}},
                    {"name": "User & Entity Behaviour Analytics (UEBA)",
                     "kpi": "Mean time from anomaly detection to analyst investigation",
                     "maturity": {"initial": "SIEM rules only; no behavioural baseline", "established": "UEBA deployed; user and entity baselines established", "leading": "Behavioural models tuned; high-fidelity alerts routed directly to response; false positives tracked"}},
                    {"name": "Cloud & Identity Telemetry Integration",
                     "kpi": "% of cloud platforms and identity providers with telemetry feeding SIEM",
                     "maturity": {"initial": "SIEM covers on-premises only; cloud and identity events not ingested", "established": "Primary cloud and IdP logs integrated; identity events correlated with endpoint", "leading": "Complete cloud-native telemetry; unified XDR view across endpoint, identity, network, and cloud"}},
                    {"name": "Advanced Detection Engineering",
                     "kpi": "% of ATT&CK techniques with at least one active detection rule; rule false-positive rate",
                     "maturity": {"initial": "Default SIEM rules only; no custom detection development", "established": "Custom detection rules developed for priority threat techniques", "leading": "Detection-as-code pipeline; rules tested against simulated attacks; coverage metrics drive roadmap"}},
                ],
            },
            {
                "name": "Threat Intelligence",
                "label": "Knowing Which Threats Are Headed Your Way and How They Work",
                "note": "External intelligence about active threat actors, campaigns, and attack techniques is collected and acted on (threat intelligence platform); knowledge of how real attackers operate is used to prioritise defences (ATT&CK-aligned tracking) — so the team focuses on realistic threats, not theoretical ones.",
                "l2": [
                    {"name": "Threat Intelligence Platform (TIP)",
                     "kpi": "% of threat intelligence feeds operationalised into SIEM/SOAR detections",
                     "maturity": {"initial": "Threat intelligence consumed informally; no structured ingestion", "established": "TIP deployed; priority feeds integrated; IOCs actioned in SIEM", "leading": "Intelligence automatically converted to detections; TTPs mapped to defensive gaps"}},
                    {"name": "Strategic & Tactical Intelligence Consumption",
                     "kpi": "Number of sector-relevant intelligence reports consumed or produced per quarter",
                     "maturity": {"initial": "No structured intelligence consumption; team unaware of adversary trends", "established": "Sector-relevant intelligence sources subscribed and reviewed regularly", "leading": "Intelligence informs security roadmap and board reporting; threat-led priorities"}},
                    {"name": "Indicator of Compromise (IOC) Management",
                     "kpi": "Mean time from IOC receipt to activation in detection tooling",
                     "maturity": {"initial": "IOCs shared informally; activation manual and delayed", "established": "IOC ingestion workflow defined; indicators activated within agreed SLA", "leading": "Automated IOC enrichment and activation; false-positive rate monitored"}},
                    {"name": "ATT&CK-Aligned TTP Tracking",
                     "kpi": "% of known priority adversary TTPs with an active detective or preventive control mapped",
                     "maturity": {"initial": "No structured TTP tracking; response to techniques reactive", "established": "ATT&CK framework used to map known adversary behaviours; coverage gaps identified", "leading": "Continuous ATT&CK heatmap maintained; gaps drive detection engineering backlog"}},
                ],
            },
            {
                "name": "Detection & Adversarial Validation",
                "label": "Continuously Testing Whether Defences Actually Detect Attacks",
                "note": "Detection rules are written, tested, and version-controlled like software (detection-as-code); coverage is measured against a common framework of attacker techniques (MITRE ATT&CK mapping); the environment is probed with simulated attacks to confirm defences respond (breach and attack simulation) — so gaps are found by the team, not by an attacker.",
                "l2": [
                    {"name": "Detection-as-Code & Rule Development",
                     "kpi": "% of detection rules stored in version control; mean time to deploy a new detection rule",
                     "maturity": {"initial": "Detection rules manually created and undocumented", "established": "Rule development process defined; rules stored and version-controlled", "leading": "CI/CD pipeline for detection rules; automated testing before production deployment"}},
                    {"name": "MITRE ATT&CK Coverage Mapping",
                     "kpi": "% of ATT&CK techniques with detective coverage (measured by automated coverage tool)",
                     "maturity": {"initial": "No ATT&CK mapping; coverage unknown", "established": "ATT&CK coverage assessed; priority techniques identified for improvement", "leading": "Coverage heatmap published to leadership; monthly improvement target tracked"}},
                    {"name": "Threat Hunting",
                     "kpi": "Number of proactive hunts completed per quarter; % resulting in a confirmed finding",
                     "maturity": {"initial": "No hunting programme; investigation only follows alerts", "established": "Structured hunting programme; priority hypotheses defined and tracked", "leading": "Intelligence-led hunting calendar; findings drive detection rule creation"}},
                    {"name": "Breach & Attack Simulation (BAS)",
                     "kpi": "% of detection rules validated by BAS in the last 90 days; detection coverage score",
                     "maturity": {"initial": "No simulation; detection effectiveness unknown", "established": "BAS platform deployed; periodic simulation campaigns run", "leading": "Continuous simulation; results automatically mapped to ATT&CK coverage gaps"}},
                ],
            },
            {
                "name": "Exposure Management",
                "label": "Vulnerabilities Found and Fixed Before Attackers Use Them",
                "note": "All known vulnerabilities are tracked and ranked by how likely they are to be exploited rather than by severity score alone (vulnerability management); the organisation's externally visible attack surface is continuously mapped and monitored (external attack surface management) — so remediation effort goes to the risks that matter most.",
                "l2": [
                    {"name": "Vulnerability Management & Prioritisation",
                     "kpi": "% of critical vulnerabilities remediated within 14 days (SLA compliance rate)",
                     "maturity": {"initial": "Scanning run ad hoc; all findings treated with equal priority", "established": "Regular scanning; risk-based prioritisation applied (CVSS + exploitability)", "leading": "Threat-intelligence-enriched prioritisation; SLA tracking automated; patch rates improving"}},
                    {"name": "External Attack Surface Management (EASM)",
                     "kpi": "Mean time to detect a new internet-facing asset; % of assets with known owner",
                     "maturity": {"initial": "External attack surface unknown; no discovery capability", "established": "EASM tool deployed; internet-facing assets catalogued and reviewed", "leading": "Continuous discovery; unrecognised assets trigger immediate investigation"}},
                    {"name": "Security Configuration Assessment",
                     "kpi": "% of in-scope systems assessed against security configuration benchmark in the last 90 days",
                     "maturity": {"initial": "Configuration assessment run manually; infrequent", "established": "Regular configuration scanning; results tracked by system owner", "leading": "Continuous monitoring; policy violations auto-remediated where safe"}},
                    {"name": "Deception & Honeypots",
                     "kpi": "Number of deception assets deployed; mean time to alert on deception asset interaction",
                     "maturity": {"initial": "No deception capability", "established": "Honeypots deployed in key network segments; alerts integrated into SOC workflow", "leading": "Distributed deception fabric; interaction intelligence feeds threat intelligence and ATT&CK mapping"}},
                ],
            },
        ],
    },
    {
        "id": "CA-12", "area": "Incident Response & Resilience",
        "zta": "Automation & Orchestration", "csf": "Respond · Recover", "grp": "ops",
        "desc": "Prepare for, detect, contain, eradicate, and recover from security incidents — maintaining business continuity under adversarial conditions and enabling organisational learning.",
        "l1s": [
            {
                "name": "Incident Management",
                "label": "A Practised Plan for When Things Go Wrong",
                "note": "Documented playbooks exist for every major incident type so the team responds consistently under pressure (incident response plan); evidence is preserved correctly from the start so investigations and legal proceedings are not compromised (digital forensics) — response is rehearsed, not improvised.",
                "l2": [
                    {"name": "IR Plan & Playbook Library",
                     "kpi": "% of playbooks tested in the last 12 months; average time from trigger to containment",
                     "maturity": {"initial": "No documented IR plan; response improvised each time", "established": "IR plan documented; playbooks exist for top 5 incident types", "leading": "Full playbook library; playbooks tested quarterly; SOAR automation reduces MTTR"}},
                    {"name": "Incident Detection, Triage & Classification",
                     "kpi": "Mean time to triage (MTTT); % of incidents correctly classified within 1 hour",
                     "maturity": {"initial": "No defined triage process; all alerts handled equally", "established": "Triage criteria defined; incidents classified by severity with SLA targets", "leading": "Automated triage for common incident types; classification accuracy tracked and improving"}},
                    {"name": "Containment & Eradication Procedures",
                     "kpi": "Mean time to contain (MTTC) by incident severity",
                     "maturity": {"initial": "Containment improvised; incomplete eradication leads to reinfection", "established": "Containment playbooks defined for major incident types; eradication checklist used", "leading": "Automated containment for defined scenarios; eradication verified before recovery"}},
                    {"name": "Digital Forensics & Evidence Preservation (DFIR)",
                     "kpi": "% of major incidents with forensic evidence collected per evidence handling policy",
                     "maturity": {"initial": "No forensic process; evidence contaminated during response", "established": "Evidence handling procedures defined; forensic toolkit available", "leading": "Forensic capability tested in exercises; chain of custody documented; legal admissibility validated"}},
                ],
            },
            {
                "name": "Crisis & Communications",
                "label": "The Right Message Reaches the Right People During a Crisis",
                "note": "A clear chain of command activates when an incident escalates (crisis management); regulatory bodies are notified within required timeframes (regulatory notification); internal teams and external stakeholders receive consistent, accurate updates — so the incident does not create a second crisis through miscommunication.",
                "l2": [
                    {"name": "Crisis Management & War-Room Coordination",
                     "kpi": "Time from incident escalation to crisis team activation (target <1h for P1)",
                     "maturity": {"initial": "No crisis management process; escalation ad hoc", "established": "Crisis team defined; activation criteria and comms channel established", "leading": "Crisis coordination tested in tabletop exercises; activation time tracked and improving"}},
                    {"name": "Regulatory Notification & Reporting",
                     "kpi": "% of notifiable incidents reported to regulator within required timeframe (e.g. 72h GDPR)",
                     "maturity": {"initial": "Notification obligations not understood; reporting missed or late", "established": "Obligations mapped; responsible contacts identified; notification drafted in response", "leading": "Notification timeline tracked from detection; pre-approved templates reduce drafting time"}},
                    {"name": "Internal Stakeholder Communication",
                     "kpi": "Time from incident declaration to first internal leadership update",
                     "maturity": {"initial": "Internal communication reactive and inconsistent", "established": "Template and distribution list prepared; regular cadence defined", "leading": "Stakeholder communication integrated into incident platform; updates automated"}},
                    {"name": "External & Media Management",
                     "kpi": "% of P1 incidents with pre-approved external communication template ready within 4 hours",
                     "maturity": {"initial": "No external communication plan; statements improvised under pressure", "established": "PR and legal engaged in incident process; initial statement templates prepared", "leading": "External communication playbooks exercised; spokesperson trained; dark site prepared"}},
                ],
            },
            {
                "name": "Business Continuity",
                "label": "Critical Operations Keep Running When Systems Are Disrupted",
                "note": "The impact of losing each system is assessed so recovery priorities are set in advance (business impact analysis); failover procedures and recovery time targets are defined, tested, and confirmed to work (business continuity planning) — so the organisation knows exactly what it can withstand and recovers to a known timetable.",
                "l2": [
                    {"name": "Business Impact Analysis (BIA)",
                     "kpi": "% of business-critical systems with a current BIA (reviewed in last 24 months)",
                     "maturity": {"initial": "No BIA; recovery priorities unclear", "established": "BIA completed for critical systems; RTOs and RPOs defined", "leading": "BIA reviewed after significant changes; drives DR prioritisation and investment decisions"}},
                    {"name": "Business Continuity Planning & Failover",
                     "kpi": "% of critical systems with a tested business continuity plan",
                     "maturity": {"initial": "No BCP; continuity assumed until failure", "established": "BCP documented for critical functions; failover procedures defined", "leading": "BCP tested annually; failover validated under realistic conditions; gaps drive improvement"}},
                    {"name": "RTO/RPO Definition & Testing",
                     "kpi": "% of critical systems meeting defined RTO/RPO in the most recent DR test",
                     "maturity": {"initial": "RTOs/RPOs defined in contracts only; never validated", "established": "RTOs/RPOs defined for all critical systems; annual DR test run", "leading": "RTO/RPO achievement tracked; tests increasing in realism; gaps drive infrastructure investment"}},
                    {"name": "Tabletop Exercises & Simulations",
                     "kpi": "Number of exercises run per year; % of exercise findings resulting in plan updates",
                     "maturity": {"initial": "No exercises; response tested only under real incidents", "established": "Annual tabletop exercise for key scenarios; findings documented", "leading": "Quarterly exercises with increasing complexity; findings tracked to closure; scenarios threat-led"}},
                ],
            },
            {
                "name": "Recovery & Learning",
                "label": "Full Recovery From Incidents and Better Controls Afterwards",
                "note": "Backups are stored offline and in an immutable state so ransomware cannot reach them (immutable backup); a structured review after every significant incident captures what happened and why (post-incident review); lessons are fed back into controls and playbooks — so each incident makes the organisation more resilient, not just recovered.",
                "l2": [
                    {"name": "Immutable Backup & Offline Storage",
                     "kpi": "% of critical systems with backups that are immutable and tested (not reachable from production)",
                     "maturity": {"initial": "Backups stored online and accessible from production; susceptible to ransomware", "established": "Immutable backups configured; offline copy maintained for critical systems", "leading": "Backup restore tested quarterly; air-gapped storage for highest-sensitivity systems"}},
                    {"name": "Disaster Recovery Orchestration",
                     "kpi": "Automated DR failover coverage (% of critical systems with automated orchestration)",
                     "maturity": {"initial": "DR recovery is manual and untested; dependent on individual knowledge", "established": "DR runbooks documented; failover steps scripted", "leading": "DR orchestration automated; failover triggered and validated without manual intervention"}},
                    {"name": "Post-Incident Review (PIR)",
                     "kpi": "% of P1/P2 incidents with PIR completed within 5 business days; % of findings actioned within 30 days",
                     "maturity": {"initial": "No formal PIR; same mistakes repeated", "established": "PIR process defined; completed for significant incidents; findings documented", "leading": "PIR findings tracked to closure; recurring themes escalated to risk register"}},
                    {"name": "Lessons-Learned Integration & Control Improvement",
                     "kpi": "% of PIR findings resulting in a documented control improvement within 60 days",
                     "maturity": {"initial": "Lessons not captured systematically; knowledge stays with individuals", "established": "Findings assigned to owners; improvements tracked", "leading": "Lessons-learned database maintained; feeds control testing and training programme"}},
                ],
            },
        ],
    },
]


# ── HTML helpers ───────────────────────────────────────────────────────────────
def e(s: str) -> str:
    return _html.escape(str(s))


def _header(cap: dict) -> str:
    phase_col = C_PHASE[cap["grp"]]
    phase_lbl = PHASE_NAME[cap["grp"]]
    return (
        f'<div style="background:{C_DARK};padding:5pt 7pt;">'
        f'<span style="display:inline-block;background:{phase_col};color:{C_WHITE};'
        f'font-size:5.5pt;font-weight:700;padding:1pt 4pt;border-radius:2pt;'
        f'letter-spacing:0.4pt;margin-right:4pt;">{e(phase_lbl).upper()}</span>'
        f'<span style="display:inline-block;background:{C_MID};color:{C_WHITE};'
        f'font-size:6.5pt;font-weight:700;padding:1.5pt 5pt;border-radius:2pt;'
        f'letter-spacing:0.4pt;">{e(cap["id"])}</span>'
        f'<span style="display:block;color:{C_WHITE};font-size:8pt;'
        f'font-weight:600;line-height:1.3;margin-top:3pt;">{e(cap["area"])}</span>'
        f'</div>'
    )


def card_l1(cap: dict) -> str:
    """Overview card: header + business labels for each L1."""
    bc = C_PHASE[cap["grp"]]
    rows = "".join(
        f'<div style="font-size:7pt;color:{C_DARK};font-weight:500;'
        f'padding:3pt 0;border-bottom:0.25pt solid {C_BORDER};line-height:1.3;">'
        f'<span style="color:{bc};margin-right:5pt;font-weight:700;">›</span>'
        f'{e(l1["label"])}</div>'
        for l1 in cap["l1s"]
    )
    tag = (
        f'<div style="font-size:5.5pt;color:{C_MUTED};margin-top:4pt;'
        f'padding-top:2pt;border-top:0.5pt solid {C_BORDER};">'
        f'{e(cap["zta"])} &nbsp;·&nbsp; CSF: {e(cap["csf"])}</div>'
    )
    return (
        f'<div style="border:0.5pt solid {C_BORDER};border-radius:3pt;height:100%;">'
        + _header(cap)
        + f'<div style="padding:5pt 7pt 6pt;border-left:3pt solid {bc};">'
        + rows + tag
        + f'</div></div>'
    )


# ── Grid with phase section headers ──────────────────────────────────────────
def grid_with_phases(caps: list, card_fn, cols: int = 3) -> str:
    # Group by phase
    phases_seen = []
    phase_groups: dict = {}
    for cap in caps:
        ph = cap["grp"]
        if ph not in phase_groups:
            phase_groups[ph] = []
            phases_seen.append(ph)
        phase_groups[ph].append(cap)

    col_w = f"{100 / cols:.1f}%"
    html_parts = [
        f'<table style="width:100%;border-collapse:separate;border-spacing:0;'
        f'table-layout:fixed;page-break-inside:auto;margin:0;">'
    ]

    for ph in phases_seen:
        group_caps = phase_groups[ph]
        ph_col = C_PHASE[ph]
        ph_name = PHASE_NAME[ph]
        # Phase header row
        html_parts.append(
            f'<tr><td colspan="{cols}" style="padding:6pt 3pt 3pt;">'
            f'<div style="background:{ph_col};color:{C_WHITE};font-size:7.5pt;'
            f'font-weight:700;letter-spacing:0.8pt;padding:3pt 8pt;border-radius:2pt;">'
            f'{e(ph_name.upper())}</div></td></tr>'
        )
        # Cards in rows of `cols`
        for i in range(0, len(group_caps), cols):
            batch = group_caps[i: i + cols]
            cells = "".join(
                f'<td style="width:{col_w};padding:3pt;vertical-align:top;">{card_fn(c)}</td>'
                for c in batch
            )
            for _ in range(cols - len(batch)):
                cells += f'<td style="width:{col_w};padding:3pt;"></td>'
            html_parts.append(f'<tr style="break-inside:avoid;">{cells}</tr>')

    html_parts.append("</table>")
    return "".join(html_parts)


# ── Legend ────────────────────────────────────────────────────────────────────
def legend() -> str:
    items = [
        (C_DARK,  "Foundation", "CA-01 · CA-02 · CA-03 — governance, people, supply chain"),
        (C_MID,   "Protect",    "CA-04 – CA-10 — ZTA pillars + AI"),
        (C_LIGHT, "Operate",    "CA-11 · CA-12 — detect, respond, recover"),
    ]
    chips = "".join(
        f'<span style="display:inline-block;margin-right:14pt;white-space:nowrap;">'
        f'<span style="display:inline-block;width:9pt;height:9pt;background:{col};'
        f'border-radius:1pt;vertical-align:middle;margin-right:4pt;"></span>'
        f'<span style="font-size:7pt;color:{C_TEXT};">'
        f'<strong>{label}</strong> — {desc}</span></span>'
        for col, label, desc in items
    )
    return (
        f'<div style="margin:4pt 0 8pt;padding:5pt 8pt;background:{C_OFFWHT};'
        f'border:0.5pt solid {C_BORDER};border-radius:3pt;">{chips}</div>'
    )


# ── Overview diagram (L1 only) ────────────────────────────────────────────────
def diagram_1() -> str:
    return (
        f'<h2>Capability Areas &amp; L1 Strategic Capabilities</h2>'
        f'<p style="font-size:9pt;color:{C_MUTED};margin:-4pt 0 6pt;">'
        f'Each of the 12 capability areas contains 4 named L1 business capabilities. '
        f'Left-border colour and phase banner indicate the three phases.</p>'
        + legend()
        + grid_with_phases(CAPABILITIES, card_l1, cols=3)
    )


def page_break() -> str:
    return '<div style="page-break-after:always;"></div>'


# ── Detail section ─────────────────────────────────────────────────────────────
def _phase_badge(grp: str) -> str:
    col = C_PHASE[grp]
    name = PHASE_NAME[grp]
    return (
        f'<span style="display:inline-block;background:{col};color:{C_WHITE};'
        f'font-size:6pt;font-weight:700;padding:1.5pt 5pt;border-radius:2pt;'
        f'letter-spacing:0.5pt;margin-left:6pt;vertical-align:middle;">'
        f'{e(name.upper())}</span>'
    )


def _l2_table(l2_list: list) -> str:
    """Compact table with Sub-Capability | KPI | Initial | Established | Leading."""
    hdr_style = (
        f'background:{C_DARK};color:{C_WHITE};padding:4pt 6pt;'
        f'text-align:left;font-size:7pt;font-weight:600;letter-spacing:0.2pt;'
    )
    rows = ""
    for i, l2 in enumerate(l2_list):
        bg = C_OFFWHT if i % 2 == 0 else C_WHITE
        rows += (
            f'<tr style="background:{bg};">'
            f'<td style="padding:3.5pt 6pt;font-weight:600;font-size:7.5pt;color:{C_DARK};vertical-align:top;width:17%;">{e(l2["name"])}</td>'
            f'<td style="padding:3.5pt 6pt;font-size:7pt;color:{C_TEXT};vertical-align:top;width:20%;">{e(l2["kpi"])}</td>'
            f'<td style="padding:3.5pt 6pt;font-size:7pt;color:{C_TEXT};vertical-align:top;width:21%;">{e(l2["maturity"]["initial"])}</td>'
            f'<td style="padding:3.5pt 6pt;font-size:7pt;color:{C_TEXT};vertical-align:top;width:21%;">{e(l2["maturity"]["established"])}</td>'
            f'<td style="padding:3.5pt 6pt;font-size:7pt;color:{C_TEXT};vertical-align:top;width:21%;">{e(l2["maturity"]["leading"])}</td>'
            f'</tr>'
        )
    return (
        f'<table style="width:100%;border-collapse:collapse;margin:4pt 0 10pt;'
        f'font-size:7.5pt;page-break-inside:avoid;">'
        f'<thead><tr>'
        f'<th style="{hdr_style}width:17%;">Sub-Capability</th>'
        f'<th style="{hdr_style}width:20%;">KPI</th>'
        f'<th style="{hdr_style}width:21%;">Initial</th>'
        f'<th style="{hdr_style}width:21%;">Established</th>'
        f'<th style="{hdr_style}width:21%;">Leading</th>'
        f'</tr></thead>'
        f'<tbody>{rows}</tbody>'
        f'</table>'
    )


def _l1_block(l1: dict, phase_col: str) -> str:
    """One L1 with label, note, and L2 table."""
    return (
        f'<div style="margin-top:10pt;page-break-inside:avoid;">'
        f'<div style="background:{C_OFFWHT};border-left:3pt solid {phase_col};'
        f'padding:5pt 8pt;margin-bottom:3pt;">'
        f'<span style="font-size:9.5pt;font-weight:700;color:{C_DARK};">{e(l1["label"])}</span><br>'
        f'<span style="font-size:8pt;color:{C_MUTED};font-style:italic;">{e(l1["note"])}</span>'
        f'</div>'
        + _l2_table(l1["l2"])
        + f'</div>'
    )


def ca_detail(cap: dict) -> str:
    """Full detail block for one CA."""
    phase_col = C_PHASE[cap["grp"]]
    l1_blocks = "".join(_l1_block(l1, phase_col) for l1 in cap["l1s"])
    return (
        f'<h3 style="page-break-before:always;">{e(cap["id"])} · {e(cap["area"])}'
        + _phase_badge(cap["grp"])
        + f'</h3>'
        f'<blockquote><p>{e(cap["desc"])}</p></blockquote>'
        + l1_blocks
    )


def detail_section() -> str:
    return (
        f'<h2>Capability Detail — L1 &amp; L2 with KPI and Maturity</h2>'
        f'<p style="font-size:9pt;color:{C_MUTED};margin:-4pt 0 6pt;">'
        f'Each L1 capability is shown with its business label and sub-note. '
        f'The table beneath lists L2 sub-capabilities with a measurable KPI '
        f'and three maturity levels (Initial / Established / Leading).</p>'
        + "".join(ca_detail(cap) for cap in CAPABILITIES)
    )


# ── CSS ───────────────────────────────────────────────────────────────────────
CSS_STYLES = f"""
@page {{
    size: A4;
    margin: 20mm 18mm 22mm 18mm;
    @top-center {{
        content: "OSA Security Capability Model";
        font-family: 'Inter', sans-serif;
        font-size: 8pt;
        color: {C_MUTED};
        border-bottom: 0.5pt solid {C_BORDER};
        padding-bottom: 4pt;
    }}
    @bottom-right {{
        content: counter(page) " / " counter(pages);
        font-family: 'Inter', sans-serif;
        font-size: 8pt;
        color: {C_MUTED};
    }}
    @bottom-left {{
        content: "opensecurityarchitecture.org";
        font-family: 'Inter', sans-serif;
        font-size: 8pt;
        color: {C_MUTED};
    }}
}}
@page :first {{
    @top-center {{ content: none; }}
    @bottom-right {{ content: none; }}
    @bottom-left {{ content: none; }}
    margin-top: 30mm;
}}
* {{ box-sizing: border-box; }}
body {{
    font-family: 'Inter', sans-serif;
    font-size: 9.5pt;
    line-height: 1.55;
    color: {C_TEXT};
    background: {C_WHITE};
    margin: 0;
    padding: 0;
}}
h1 {{
    font-size: 22pt;
    font-weight: 700;
    color: {C_DARK};
    border-bottom: 3pt solid {C_LIGHT};
    padding-bottom: 8pt;
    margin-top: 0;
    margin-bottom: 4pt;
    line-height: 1.2;
}}
h1 + p em {{ font-size: 9pt; color: {C_MUTED}; font-style: normal; }}
hr {{ border: none; border-top: 0.75pt solid {C_BORDER}; margin: 14pt 0; }}
h2 {{
    font-size: 13pt;
    font-weight: 600;
    color: {C_DARK};
    border-left: 3.5pt solid {C_LIGHT};
    padding-left: 8pt;
    margin-top: 22pt;
    margin-bottom: 8pt;
    page-break-after: avoid;
}}
h3 {{
    font-size: 11pt;
    font-weight: 600;
    color: {C_MID};
    margin-top: 18pt;
    margin-bottom: 5pt;
    page-break-after: avoid;
    border-top: 1pt solid {C_BORDER};
    padding-top: 10pt;
}}
h4 {{ font-size: 9.5pt; font-weight: 600; color: {C_DARK}; margin-top: 10pt; margin-bottom: 3pt; page-break-after: avoid; }}
blockquote {{
    margin: 4pt 0 10pt 0;
    padding: 7pt 12pt;
    background: {C_OFFWHT};
    border-left: 3pt solid {C_MID};
    color: {C_MUTED};
    font-size: 9pt;
    font-style: italic;
    border-radius: 2pt;
}}
blockquote p {{ margin: 0; }}
ul {{ margin: 3pt 0 6pt 0; padding-left: 16pt; }}
ul li {{ margin-bottom: 2pt; padding-left: 2pt; }}
table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 8.5pt;
    margin: 10pt 0 14pt 0;
    page-break-inside: avoid;
}}
thead tr {{ background: {C_DARK}; color: {C_WHITE}; }}
thead th {{ padding: 5pt 8pt; text-align: left; font-weight: 600; font-size: 8pt; letter-spacing: 0.3pt; }}
tbody tr {{ border-bottom: 0.5pt solid {C_BORDER}; }}
tbody tr:nth-child(even) {{ background: {C_OFFWHT}; }}
tbody td {{ padding: 4pt 8pt; vertical-align: top; }}
em {{ color: {C_MID}; font-style: normal; font-size: 8.5pt; }}
h3 + blockquote {{ page-break-before: avoid; }}
"""


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    if not SRC_MD.exists():
        print(f"ERROR: source not found: {SRC_MD}", file=sys.stderr)
        sys.exit(1)

    md_text = SRC_MD.read_text(encoding="utf-8")

    # Take only the front matter (up to "## Capability Breakdown")
    split_marker = "\n## Capability Breakdown"
    split_idx = md_text.find(split_marker)
    if split_idx != -1:
        front_matter = md_text[:split_idx]
    else:
        front_matter = md_text  # fallback: use all

    md_body = markdown.markdown(
        front_matter,
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
    )

    # Inject overview diagram after the first <hr />
    for split_tag in ("<hr />", "<hr>"):
        idx = md_body.find(split_tag)
        if idx != -1:
            break

    if idx == -1:
        body = md_body + page_break() + diagram_1() + page_break() + detail_section()
    else:
        before = md_body[:idx]
        after  = md_body[idx + len(split_tag):]
        body = (
            before + split_tag
            + page_break()
            + diagram_1()
            + page_break()
            + detail_section()
            + after
        )

    full_html = (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        '<title>OSA Security Capability Model</title></head>'
        f'<body>{body}</body></html>'
    )

    print(f"Converting {SRC_MD.name} → {OUT_PDF.name} …")
    HTML(string=full_html, base_url=str(SRC_MD.parent)).write_pdf(
        OUT_PDF,
        stylesheets=[CSS(string=CSS_STYLES)],
        optimize_images=True,
    )
    size_kb = OUT_PDF.stat().st_size // 1024
    print(f"Done — {OUT_PDF} ({size_kb} KB)")


if __name__ == "__main__":
    main()
