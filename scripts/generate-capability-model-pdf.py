#!/usr/bin/env python3
"""
OSA Security Capability Model — PDF generator (v3).
Converts osa-capability-model.md → osa-capability-model.pdf with two
graphical capability-map visualisations injected after the title block.

Hierarchy: CA area → 2–4 L1 capabilities → 2–4 L2 sub-capabilities each.

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

# Left-border accent per group
GRP_BORDER = {"xc": C_DARK, "zt": C_MID, "ops": C_LIGHT}


# ── Capability data ───────────────────────────────────────────────────────────
# Each CA has 2–4 L1 capabilities; each L1 has 2–4 L2 sub-capabilities.
# grp:  xc = governance/cross-cutting (dark navy border)
#        zt = ZTA protect pillars    (mid-blue border)
#       ops = detect/respond          (cyan border)

CAPABILITIES = [
    {
        "id": "CA-01", "area": "Governance, Risk & Compliance",
        "zta": "Cross-cutting", "csf": "Govern · Identify", "grp": "xc",
        "l1s": [
            {"name": "Policy & Standards Management", "l2": [
                "Security Policy Hierarchy",
                "Standards & Procedures Lifecycle",
                "Exception & Waiver Management",
                "Regulatory Requirements Translation",
            ]},
            {"name": "Risk Management", "l2": [
                "Enterprise Risk Taxonomy & Register",
                "Risk Treatment & Acceptance",
                "Risk Appetite & Tolerance Definition",
                "Control Effectiveness Assessment",
            ]},
            {"name": "Compliance & Assurance", "l2": [
                "Multi-Framework Control Traceability (SP-026)",
                "Compliance Evidence Repository (SP-018)",
                "Internal Audit Programme",
                "Regulatory Change Management",
            ]},
            {"name": "Governance Reporting & Measurement", "l2": [
                "Security KRI/KPI Framework (SP-043)",
                "Board & Executive Reporting (SP-022)",
                "Security Investment Tracking",
                "Security Assurance Dashboard",
            ]},
        ],
    },
    {
        "id": "CA-02", "area": "Identity & Access Management",
        "zta": "Identity", "csf": "Protect", "grp": "zt",
        "l1s": [
            {"name": "Authentication", "l2": [
                "Multi-Factor Authentication",
                "Phishing-Resistant / Passkey Authentication (SP-033)",
                "Adaptive & Risk-Based Authentication",
                "Enterprise Federation & SSO (SP-032)",
            ]},
            {"name": "Identity Lifecycle & Governance", "l2": [
                "Joiner-Mover-Leaver Automation (SP-010)",
                "Access Certification & Entitlement Review",
                "SaaS Identity Provisioning & SCIM (SP-044)",
                "Role & Attribute-Based Access Control",
            ]},
            {"name": "Privileged Access", "l2": [
                "Privileged Credential Vault (SP-037)",
                "Just-in-Time & Just-Enough Access",
                "Privileged Session Recording & Monitoring",
                "Standing Privilege Elimination",
            ]},
            {"name": "Machine & Workload Identity", "l2": [
                "Service Account Governance",
                "PKI & Certificate Lifecycle Management",
                "Workload Identity Federation (SPIFFE/SPIRE)",
                "Secrets & Dynamic Credential Management",
            ]},
        ],
    },
    {
        "id": "CA-03", "area": "Device & Endpoint Trust",
        "zta": "Devices", "csf": "Protect", "grp": "zt",
        "l1s": [
            {"name": "Endpoint Management", "l2": [
                "Unified Endpoint Management (MDM/UEM) (SP-001)",
                "Configuration Baseline & Hardening",
                "Software Inventory & Application Control",
                "Patch Lifecycle Management (SP-038)",
            ]},
            {"name": "Endpoint Protection", "l2": [
                "Endpoint Detection & Response (EDR/XDR)",
                "Anti-Malware & Behavioural Detection",
                "Application Allowlisting",
                "Full-Disk Encryption & Hardware Security (TPM)",
            ]},
            {"name": "Mobile & BYOD", "l2": [
                "Corporate Mobile Management (SP-024)",
                "BYOD Containerisation (SP-003)",
                "Mobile Threat Defence (MTD)",
                "Wireless Access Security (SP-006, SP-007)",
            ]},
            {"name": "Device Trust Assessment", "l2": [
                "Device Posture Evaluation",
                "Compliance-Gated Access (ZTNA Integration)",
                "Hardware Root of Trust",
                "Continuous Compliance Monitoring",
            ]},
        ],
    },
    {
        "id": "CA-04", "area": "Network & Infrastructure Security",
        "zta": "Networks", "csf": "Protect", "grp": "zt",
        "l1s": [
            {"name": "Zero Trust Network Access", "l2": [
                "ZTNA Platform & Policy Engine (SP-029)",
                "Secure Remote Access / VPN Replacement (SP-015)",
                "SASE Architecture & Convergence",
                "Context-Aware Access Brokering",
            ]},
            {"name": "Network Segmentation", "l2": [
                "Network Security Zone Model (SP-017)",
                "Micro-Segmentation (Workload-to-Workload)",
                "DMZ Architecture & Isolation (SP-016)",
                "East-West Traffic Control",
            ]},
            {"name": "Network Security Controls", "l2": [
                "Next-Generation Firewall & IPS",
                "Network Detection & Response (NDR)",
                "DNS Security (Protective DNS, DNSSEC)",
                "DDoS Protection",
            ]},
            {"name": "Operational Technology (OT/ICS)", "l2": [
                "OT Network Isolation (SP-023)",
                "Purdue Model Segmentation",
                "Unidirectional Gateway Architecture",
                "OT Asset Visibility & Inventory",
            ]},
        ],
    },
    {
        "id": "CA-05", "area": "Application & API Security",
        "zta": "Applications", "csf": "Protect", "grp": "zt",
        "l1s": [
            {"name": "Secure Development", "l2": [
                "Secure SDLC Policy & Phase Gates (SP-012)",
                "Threat Modelling",
                "Security Architecture Review",
                "Developer Security Enablement",
            ]},
            {"name": "Application Security Testing", "l2": [
                "Static Analysis (SAST)",
                "Dynamic Analysis (DAST)",
                "Software Composition Analysis (SCA) (SP-028)",
                "Penetration Testing (SP-035)",
            ]},
            {"name": "API Security", "l2": [
                "API Gateway & Traffic Management (SP-030)",
                "Authentication & Authorisation (OAuth 2.0 / OIDC)",
                "Input Validation & Schema Enforcement",
                "SOA & Microservice Security (SP-004, SP-005)",
            ]},
            {"name": "Runtime Application Protection", "l2": [
                "Web Application Firewall (WAF) (SP-008)",
                "Runtime Application Self-Protection (RASP)",
                "Secrets Detection & Vault Integration",
                "Secure Application Baseline (SP-041)",
            ]},
        ],
    },
    {
        "id": "CA-06", "area": "Data & Information Protection",
        "zta": "Data", "csf": "Protect", "grp": "zt",
        "l1s": [
            {"name": "Data Classification & Governance", "l2": [
                "Data Classification Framework (SP-013)",
                "Data Discovery & Inventory",
                "Retention, Archival & Disposal Policy",
                "Privacy by Design",
            ]},
            {"name": "Data Loss Prevention", "l2": [
                "Endpoint DLP",
                "Network DLP",
                "Cloud DLP",
                "Information Rights Management (IRM/DRM)",
            ]},
            {"name": "Cryptography & Key Management", "l2": [
                "Encryption at Rest & in Transit",
                "Client-Side Encryption (SP-039)",
                "Key Management Service (KMS/HSM)",
                "Post-Quantum Cryptography Migration (SP-040)",
            ]},
            {"name": "Secure Data Exchange", "l2": [
                "Secure File Transfer (SP-019)",
                "Email Transport Security — DMARC/DKIM/SPF (SP-020)",
                "Data Sharing Agreements & Controls",
                "Tokenisation & Data Masking",
            ]},
        ],
    },
    {
        "id": "CA-07", "area": "Cloud & Platform Security",
        "zta": "Infrastructure", "csf": "Protect", "grp": "zt",
        "l1s": [
            {"name": "Cloud Posture Management", "l2": [
                "Cloud Security Posture Management (CSPM)",
                "Infrastructure-as-Code Security Scanning (SP-028)",
                "Compliance Benchmark Enforcement (CIS, NIST)",
                "Cloud Drift Detection & Automated Remediation",
            ]},
            {"name": "Workload Protection", "l2": [
                "Cloud Workload Protection (CWPP)",
                "Container & Kubernetes Security",
                "Serverless Security",
                "Server Hardening & Baseline (SP-002, SP-011)",
            ]},
            {"name": "Cloud Identity & Entitlements", "l2": [
                "Cloud IAM Governance",
                "Cloud Infrastructure Entitlement Management (CIEM)",
                "SaaS Security Posture Management (SSPM)",
                "Cross-Cloud Identity Federation",
            ]},
            {"name": "Cloud Architecture Security", "l2": [
                "VPC Design & Private Endpoints",
                "Cloud-Native Firewall & Security Groups",
                "Cloud Key Management & Encryption",
                "Cloud Storage Security Controls",
            ]},
        ],
    },
    {
        "id": "CA-08", "area": "Threat Detection & Security Operations",
        "zta": "Visibility & Analytics", "csf": "Detect · Identify", "grp": "ops",
        "l1s": [
            {"name": "Security Monitoring", "l2": [
                "SIEM: Log Aggregation & Correlation (SP-031)",
                "User & Entity Behaviour Analytics (UEBA)",
                "Cloud & Identity Telemetry Integration",
                "Advanced Detection Engineering (SP-025)",
            ]},
            {"name": "Threat Intelligence", "l2": [
                "Threat Intelligence Platform (TIP)",
                "Strategic & Tactical Intelligence Consumption",
                "Indicator of Compromise (IOC) Management",
                "ATT&CK-Aligned TTP Tracking",
            ]},
            {"name": "Detection & Adversarial Validation", "l2": [
                "Detection-as-Code & Rule Development",
                "MITRE ATT&CK Coverage Mapping",
                "Threat Hunting",
                "Breach & Attack Simulation (BAS)",
                "Offensive Security Testing (SP-035)",
            ]},
            {"name": "Exposure Management", "l2": [
                "Vulnerability Management & Prioritisation (SP-038)",
                "External Attack Surface Management (SP-046)",
                "Security Configuration Assessment",
                "Deception & Honeypots",
            ]},
        ],
    },
    {
        "id": "CA-09", "area": "Incident Response & Resilience",
        "zta": "Automation & Orchestration", "csf": "Respond · Recover", "grp": "ops",
        "l1s": [
            {"name": "Incident Management", "l2": [
                "IR Plan & Playbook Library (SP-036)",
                "Incident Detection, Triage & Classification",
                "Containment & Eradication Procedures",
                "Digital Forensics & Evidence Preservation (DFIR)",
            ]},
            {"name": "Crisis & Communications", "l2": [
                "Crisis Management & War-Room Coordination",
                "Regulatory Notification & Reporting",
                "Internal Stakeholder Communication",
                "External & Media Management",
            ]},
            {"name": "Business Continuity", "l2": [
                "Business Impact Analysis (BIA)",
                "Business Continuity Planning & Failover",
                "RTO/RPO Definition & Testing",
                "Tabletop Exercises & Simulations (SP-034)",
            ]},
            {"name": "Recovery & Learning", "l2": [
                "Immutable Backup & Offline Storage",
                "Disaster Recovery Orchestration",
                "Post-Incident Review (PIR)",
                "Lessons-Learned Integration & Control Improvement",
            ]},
        ],
    },
    {
        "id": "CA-10", "area": "Supply Chain & Third-Party Risk",
        "zta": "Cross-cutting", "csf": "Govern · Identify", "grp": "xc",
        "l1s": [
            {"name": "Vendor Risk Management", "l2": [
                "Vendor Risk Tiering & Assessment (SP-042)",
                "Continuous Vendor Security Monitoring",
                "Contractual Security Requirements & Baseline",
                "Right-to-Audit & Evidence Collection",
            ]},
            {"name": "Software Supply Chain", "l2": [
                "Software Bill of Materials (SBOM)",
                "Open-Source Dependency Governance",
                "Dependency Vulnerability Tracking (SCA)",
                "Artefact Signing & Approved Registry",
            ]},
            {"name": "Third-Party Access", "l2": [
                "Vendor Access Provisioning & Governance",
                "Time-Limited & JIT Third-Party Access",
                "Third-Party Session Recording",
                "Segregated Network Access for Vendors",
            ]},
            {"name": "Concentration & Resilience", "l2": [
                "Critical Supplier Identification & Mapping",
                "Concentration Risk Assessment",
                "Alternative Supplier Planning",
                "Supply Chain Incident Response",
            ]},
        ],
    },
    {
        "id": "CA-11", "area": "Human & Organisational Security",
        "zta": "Cross-cutting", "csf": "Govern · Protect", "grp": "xc",
        "l1s": [
            {"name": "Awareness & Training", "l2": [
                "Role-Based Security Awareness (SP-014)",
                "Phishing Simulation Programme",
                "Executive & Board Security Education (SP-022)",
                "Just-in-Time Coaching & Nudging",
            ]},
            {"name": "Security Culture", "l2": [
                "Security Champion Network",
                "Security Culture Maturity Measurement",
                "Developer Security Enablement",
                "Security Feedback & Recognition",
            ]},
            {"name": "Insider Threat", "l2": [
                "Insider Threat Policy & Programme",
                "Behavioural Analytics (UEBA)",
                "DLP-UEBA Correlation",
                "Investigation & Response Procedures",
            ]},
            {"name": "Collaboration Security", "l2": [
                "Secure Collaboration Platform Controls (SP-021)",
                "External Sharing Governance",
                "Information Barrier Enforcement",
                "Meeting & Channel Security",
            ]},
        ],
    },
    {
        "id": "CA-12", "area": "AI & Agentic Security",
        "zta": "Cross-cutting (emerging)", "csf": "Govern · Protect", "grp": "xc",
        "l1s": [
            {"name": "AI Governance", "l2": [
                "AI Model Inventory & Risk Classification (SP-045)",
                "AI Use Case Assessment & Approval",
                "Responsible AI — Bias, Fairness, Explainability",
                "AI Regulatory Compliance (EU AI Act, NIST AI RMF)",
            ]},
            {"name": "AI Security Controls", "l2": [
                "Prompt Injection Detection & Filtering (SP-027)",
                "AI Input/Output Monitoring",
                "Model Access Controls & Authorisation",
                "AI Audit Logging & Traceability",
            ]},
            {"name": "Agentic Security", "l2": [
                "Minimal Tool Authority / Agent Least Privilege (SP-047)",
                "Human-in-the-Loop Oversight Gates (SP-047)",
                "Agent Blast Radius Containment (SP-047)",
                "Agentic Orchestration Security (SP-047)",
            ]},
            {"name": "AI Supply Chain & Integrity", "l2": [
                "Model Provenance & Signing",
                "Approved Model Registry",
                "Training Data Governance",
                "AI Red Teaming & Adversarial Testing",
            ]},
        ],
    },
]


# ── HTML helpers ──────────────────────────────────────────────────────────────
def e(s: str) -> str:
    return _html.escape(str(s))


def _header(cap: dict) -> str:
    """Dark-navy strip with CA badge and area name."""
    return (
        f'<div style="background:{C_DARK};padding:5pt 7pt;">'
        f'<span style="display:inline-block;background:{C_MID};color:{C_WHITE};'
        f'font-size:6.5pt;font-weight:700;padding:1.5pt 5pt;border-radius:2pt;'
        f'letter-spacing:0.4pt;margin-bottom:3pt;">{e(cap["id"])}</span>'
        f'<span style="display:block;color:{C_WHITE};font-size:8pt;'
        f'font-weight:600;line-height:1.3;">{e(cap["area"])}</span>'
        f'</div>'
    )


def card_l1(cap: dict) -> str:
    """Diagram 1: header + all L1 capability names listed."""
    bc = GRP_BORDER[cap["grp"]]
    rows = "".join(
        f'<div style="font-size:7.5pt;color:{C_DARK};font-weight:500;'
        f'padding:2.5pt 0;border-bottom:0.25pt solid {C_BORDER};line-height:1.3;">'
        f'<span style="color:{C_MID};margin-right:5pt;font-weight:700;">›</span>'
        f'{e(l1["name"])}</div>'
        for l1 in cap["l1s"]
    )
    tag = (
        f'<div style="font-size:6.5pt;color:{C_MUTED};margin-top:5pt;'
        f'padding-top:3pt;border-top:0.5pt solid {C_BORDER};">'
        f'{e(cap["zta"])} &nbsp;·&nbsp; CSF: {e(cap["csf"])}</div>'
    )
    return (
        f'<div style="border:0.5pt solid {C_BORDER};border-radius:3pt;">'
        + _header(cap)
        + f'<div style="padding:5pt 7pt 6pt;border-left:3pt solid {bc};">'
        + rows + tag
        + f'</div></div>'
    )


def card_l1_l2(cap: dict) -> str:
    """Diagram 2: header + each L1 with its L2 sub-capability list."""
    bc = GRP_BORDER[cap["grp"]]
    blocks = ""
    for l1 in cap["l1s"]:
        l2_rows = "".join(
            f'<div style="font-size:6.5pt;color:{C_TEXT};padding:1.5pt 0 1.5pt 8pt;'
            f'border-bottom:0.2pt solid {C_BORDER};line-height:1.3;">{e(item)}</div>'
            for item in l1["l2"]
        )
        blocks += (
            f'<div style="margin-bottom:5pt;">'
            f'<div style="font-size:7.5pt;color:{C_MID};font-weight:600;'
            f'padding:2pt 0;border-bottom:0.5pt solid {C_BORDER};margin-bottom:1pt;">'
            f'<span style="margin-right:4pt;">›</span>{e(l1["name"])}</div>'
            + l2_rows
            + f'</div>'
        )
    return (
        f'<div style="border:0.5pt solid {C_BORDER};border-radius:3pt;">'
        + _header(cap)
        + f'<div style="padding:5pt 7pt 6pt;border-left:3pt solid {bc};">'
        + blocks
        + f'</div></div>'
    )


# ── Grid builder ──────────────────────────────────────────────────────────────
def grid(caps: list, card_fn, cols: int = 3) -> str:
    col_w = f"{100 / cols:.1f}%"
    rows = []
    for i in range(0, len(caps), cols):
        batch = caps[i : i + cols]
        cells = "".join(
            f'<td style="width:{col_w};padding:3pt;vertical-align:top;">{card_fn(c)}</td>'
            for c in batch
        )
        for _ in range(cols - len(batch)):
            cells += f'<td style="width:{col_w};padding:3pt;"></td>'
        rows.append(f'<tr style="break-inside:avoid;">{cells}</tr>')
    return (
        f'<table style="width:100%;border-collapse:separate;border-spacing:0;'
        f'table-layout:fixed;page-break-inside:auto;margin:0;">'
        + "".join(rows) + "</table>"
    )


# ── Legend ────────────────────────────────────────────────────────────────────
def legend() -> str:
    items = [
        (C_DARK,  "Governance & Cross-cutting", "CA-01, CA-10, CA-11, CA-12"),
        (C_MID,   "ZTA Protect pillars",         "CA-02 – CA-07"),
        (C_LIGHT, "Operations — Detect/Respond", "CA-08, CA-09"),
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


# ── Diagram sections ──────────────────────────────────────────────────────────
def diagram_1() -> str:
    return (
        f'<h2>Diagram 1 — Capability Areas &amp; L1 Strategic Capabilities</h2>'
        f'<p style="font-size:9pt;color:{C_MUTED};margin:-4pt 0 6pt;">'
        f'Each of the 12 capability areas contains 4 named L1 business capabilities. '
        f'Left-border colour indicates group.</p>'
        + legend()
        + grid(CAPABILITIES, card_l1, cols=3)
    )


def diagram_2() -> str:
    return (
        f'<h2>Diagram 2 — L1 Capabilities with L2 Architectural Sub-Capabilities</h2>'
        f'<p style="font-size:9pt;color:{C_MUTED};margin:-4pt 0 6pt;">'
        f'Each L1 capability is decomposed into 3–5 named L2 architectural sub-capabilities.</p>'
        + legend()
        + grid(CAPABILITIES, card_l1_l2, cols=3)
    )


def page_break() -> str:
    return '<div style="page-break-after:always;"></div>'


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
ul > li > strong {{ color: {C_DARK}; font-size: 10pt; }}
ul > li > ul {{ margin-top: 3pt; margin-bottom: 5pt; padding-left: 14pt; }}
ul > li > ul > li {{ color: {C_TEXT}; margin-bottom: 2pt; font-size: 9pt; }}
em {{ color: {C_MID}; font-style: normal; font-size: 8.5pt; }}
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
code {{ font-family: 'Courier New', monospace; font-size: 8pt; background: {C_OFFWHT}; border: 0.5pt solid {C_BORDER}; padding: 1pt 3pt; border-radius: 2pt; color: {C_DARK}; }}
h3 + blockquote {{ page-break-before: avoid; }}
"""


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    if not SRC_MD.exists():
        print(f"ERROR: source not found: {SRC_MD}", file=sys.stderr)
        sys.exit(1)

    md_text = SRC_MD.read_text(encoding="utf-8")
    md_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
    )

    # Inject diagrams immediately after the first <hr /> (after title block)
    for split_tag in ("<hr />", "<hr>"):
        idx = md_body.find(split_tag)
        if idx != -1:
            break

    if idx == -1:
        body = diagram_1() + page_break() + diagram_2() + page_break() + md_body
    else:
        before = md_body[:idx]
        after  = md_body[idx + len(split_tag):]
        body = (
            before + split_tag
            + diagram_1() + page_break()
            + diagram_2() + page_break()
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
