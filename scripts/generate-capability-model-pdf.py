#!/usr/bin/env python3
"""
OSA Security Capability Model — PDF generator.
Converts osa-capability-model.md → osa-capability-model.pdf with two
graphical capability-map visualisations injected after the title block.

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

# ── Capability data ───────────────────────────────────────────────────────────
CAPABILITIES = [
    {"id": "CA-01", "area": "Governance, Risk & Compliance",
     "l1": "Security Governance & Assurance",
     "l2": ["Policy & Standards Management", "Risk Management",
             "Compliance & Audit", "Governance Reporting & Measurement"],
     "zta": "Cross-cutting", "csf": "Govern · Identify", "grp": "xc"},

    {"id": "CA-02", "area": "Identity & Access Management",
     "l1": "Identity Trust & Access Control",
     "l2": ["Authentication", "Identity Lifecycle & Governance",
             "Privileged Access", "Machine & Workload Identity"],
     "zta": "Identity", "csf": "Protect", "grp": "zt"},

    {"id": "CA-03", "area": "Device & Endpoint Trust",
     "l1": "Device Posture & Endpoint Protection",
     "l2": ["Endpoint Management", "Endpoint Protection",
             "Mobile & BYOD", "Device Trust Assessment"],
     "zta": "Devices", "csf": "Protect", "grp": "zt"},

    {"id": "CA-04", "area": "Network & Infrastructure Security",
     "l1": "Network Segmentation & Controlled Access",
     "l2": ["Zero Trust Network Access", "Network Segmentation",
             "Network Security Controls", "Operational Technology (OT/ICS)"],
     "zta": "Networks", "csf": "Protect", "grp": "zt"},

    {"id": "CA-05", "area": "Application & API Security",
     "l1": "Secure Application Delivery",
     "l2": ["Secure Development", "Application Security Testing",
             "API Security", "Runtime Application Protection"],
     "zta": "Applications", "csf": "Protect", "grp": "zt"},

    {"id": "CA-06", "area": "Data & Information Protection",
     "l1": "Data Lifecycle Protection",
     "l2": ["Data Classification & Governance", "Data Loss Prevention",
             "Cryptography & Key Management", "Secure Data Exchange"],
     "zta": "Data", "csf": "Protect", "grp": "zt"},

    {"id": "CA-07", "area": "Cloud & Platform Security",
     "l1": "Cloud Security Posture & Workload Protection",
     "l2": ["Cloud Posture Management", "Workload Protection",
             "Cloud Identity & Entitlements", "Cloud Network & Data Security"],
     "zta": "Infrastructure", "csf": "Protect", "grp": "zt"},

    {"id": "CA-08", "area": "Threat Detection & Security Operations",
     "l1": "Intelligence-Led Detection & Security Operations",
     "l2": ["Security Monitoring", "Threat Intelligence",
             "Detection & Adversarial Validation", "Exposure Management"],
     "zta": "Visibility & Analytics", "csf": "Detect · Identify", "grp": "ops"},

    {"id": "CA-09", "area": "Incident Response & Resilience",
     "l1": "Cyber Resilience & Recovery",
     "l2": ["Incident Management", "Crisis & Communications",
             "Business Continuity", "Recovery & Learning"],
     "zta": "Automation & Orchestration", "csf": "Respond · Recover", "grp": "ops"},

    {"id": "CA-10", "area": "Supply Chain & Third-Party Risk",
     "l1": "Extended Enterprise Trust",
     "l2": ["Vendor Risk Management", "Software Supply Chain",
             "Third-Party Access", "Concentration & Resilience"],
     "zta": "Cross-cutting", "csf": "Govern · Identify", "grp": "xc"},

    {"id": "CA-11", "area": "Human & Organisational Security",
     "l1": "Human Risk & Security Culture",
     "l2": ["Awareness & Training", "Security Culture",
             "Insider Threat", "Collaboration Security"],
     "zta": "Cross-cutting", "csf": "Govern · Protect", "grp": "xc"},

    {"id": "CA-12", "area": "AI & Agentic Security",
     "l1": "Trustworthy AI & Agentic Security",
     "l2": ["AI Governance", "AI Security Controls",
             "Agentic Security", "AI Supply Chain & Integrity"],
     "zta": "Cross-cutting", "csf": "Govern · Protect", "grp": "xc"},
]

# Left-border accent colour per group
GRP_BORDER = {"xc": C_DARK, "zt": C_MID, "ops": C_LIGHT}


# ── Card builders ─────────────────────────────────────────────────────────────
def e(s: str) -> str:
    return _html.escape(str(s))


def _header(cap: dict) -> str:
    """Dark-navy strip: CA badge + area name."""
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
    """Diagram 1 card: header + L1 name + ZTA/CSF tag line."""
    bc = GRP_BORDER[cap["grp"]]
    return (
        f'<div style="border:0.5pt solid {C_BORDER};border-radius:3pt;">'
        + _header(cap)
        + f'<div style="padding:5pt 7pt 6pt;border-left:3pt solid {bc};">'
        + f'<div style="font-size:7.5pt;color:{C_MID};font-style:italic;'
        + f'line-height:1.35;margin-bottom:5pt;">{e(cap["l1"])}</div>'
        + f'<div style="font-size:6.5pt;color:{C_MUTED};border-top:0.5pt solid {C_BORDER};padding-top:3pt;">'
        + f'{e(cap["zta"])} &nbsp;·&nbsp; CSF: {e(cap["csf"])}</div>'
        + f'</div></div>'
    )


def card_l1_l2(cap: dict) -> str:
    """Diagram 2 card: header + L1 name + L2 sub-domain list."""
    bc = GRP_BORDER[cap["grp"]]
    l2_items = "".join(
        f'<div style="font-size:7pt;color:{C_TEXT};padding:2pt 0;'
        f'border-bottom:0.25pt solid {C_BORDER};line-height:1.35;">'
        f'<span style="color:{C_MID};font-weight:700;margin-right:4pt;">—</span>'
        f'{e(item)}</div>'
        for item in cap["l2"]
    )
    return (
        f'<div style="border:0.5pt solid {C_BORDER};border-radius:3pt;">'
        + _header(cap)
        + f'<div style="padding:5pt 7pt 6pt;border-left:3pt solid {bc};">'
        + f'<div style="font-size:7.5pt;color:{C_MID};font-style:italic;'
        + f'line-height:1.35;margin-bottom:5pt;border-bottom:0.5pt solid {C_BORDER};'
        + f'padding-bottom:4pt;">{e(cap["l1"])}</div>'
        + l2_items
        + f'</div></div>'
    )


# ── Grid builder ──────────────────────────────────────────────────────────────
def grid(caps: list, card_fn, cols: int = 3) -> str:
    """Fixed-layout HTML table grid. Each row has break-inside:avoid."""
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
        + "".join(rows)
        + "</table>"
    )


# ── Legend ────────────────────────────────────────────────────────────────────
def legend() -> str:
    items = [
        (C_DARK,  "Governance &amp; Cross-cutting",   "CA-01, CA-10, CA-11, CA-12"),
        (C_MID,   "ZTA Protect pillars",               "CA-02 – CA-07"),
        (C_LIGHT, "Operations — Detect / Respond",     "CA-08, CA-09"),
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
        f'<h2>Diagram 1 — Capability Areas &amp; Strategic Domains (L1)</h2>'
        f'<p style="font-size:9pt;color:{C_MUTED};margin:-4pt 0 6pt;">'
        f'12 capability areas, each anchored to a named L1 strategic domain. '
        f'Left-border colour indicates group.</p>'
        + legend()
        + grid(CAPABILITIES, card_l1, cols=3)
    )


def diagram_2() -> str:
    return (
        f'<h2>Diagram 2 — Capability Areas with Architectural Sub-Domains (L1 + L2)</h2>'
        f'<p style="font-size:9pt;color:{C_MUTED};margin:-4pt 0 6pt;">'
        f'Each capability area decomposed into four named L2 architectural sub-domains.</p>'
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
ul > li > strong {{ color: {C_DARK}; }}
ul > li > ul {{ margin-top: 2pt; margin-bottom: 4pt; padding-left: 14pt; }}
ul > li > ul > li {{ color: {C_TEXT}; margin-bottom: 1.5pt; font-size: 9pt; }}
ul > li > ul > li > strong {{ color: {C_MID}; font-weight: 600; }}
ul > li > ul > li > ul {{ padding-left: 12pt; margin-top: 1pt; margin-bottom: 3pt; }}
ul > li > ul > li > ul > li {{ font-size: 8.5pt; color: {C_TEXT}; margin-bottom: 1pt; list-style-type: circle; }}
em {{ color: {C_MID}; font-style: normal; font-size: 8pt; }}
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
    SPLIT = "<hr />"
    idx = md_body.find(SPLIT)
    if idx == -1:
        SPLIT = "<hr>"
        idx = md_body.find(SPLIT)

    if idx == -1:
        body = diagram_1() + page_break() + diagram_2() + page_break() + md_body
    else:
        before = md_body[:idx]
        after  = md_body[idx + len(SPLIT):]
        body = (
            before
            + SPLIT
            + diagram_1()
            + page_break()
            + diagram_2()
            + page_break()
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
