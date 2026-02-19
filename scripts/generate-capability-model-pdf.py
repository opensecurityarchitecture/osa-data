#!/usr/bin/env python3
"""
OSA Security Capability Model — PDF generator.
Converts osa-capability-model.md to a styled PDF using OSA brand palette.
Output: osa-strategy/docs/osa-capability-model.pdf
"""

import sys
from pathlib import Path
import markdown
from weasyprint import HTML, CSS

WORKSPACE = Path(__file__).resolve().parent.parent
SRC_MD    = WORKSPACE.parent / "osa-strategy" / "docs" / "osa-capability-model.md"
OUT_PDF   = WORKSPACE.parent / "osa-strategy" / "docs" / "osa-capability-model.pdf"

# ── OSA palette ──────────────────────────────────────────────────────────────
C_DARK   = "#003459"
C_MID    = "#007EA7"
C_LIGHT  = "#00A8E8"
C_VDARK  = "#00171F"
C_WHITE  = "#FFFFFF"
C_OFFWHT = "#F4F7FA"
C_BORDER = "#D0DDE8"
C_TEXT   = "#1A2E3B"
C_MUTED  = "#5A7A8A"

CSS_STYLES = f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

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

* {{
    box-sizing: border-box;
}}

body {{
    font-family: 'Inter', sans-serif;
    font-size: 9.5pt;
    line-height: 1.55;
    color: {C_TEXT};
    background: {C_WHITE};
    margin: 0;
    padding: 0;
}}

/* ── Cover / title block ─────────────────────────────────────── */
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

/* Subtitle (the italicised authors line) */
h1 + p em {{
    font-size: 9pt;
    color: {C_MUTED};
    font-style: normal;
}}

hr {{
    border: none;
    border-top: 0.75pt solid {C_BORDER};
    margin: 14pt 0;
}}

/* ── Section headings ────────────────────────────────────────── */
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
}}

h4 {{
    font-size: 9.5pt;
    font-weight: 600;
    color: {C_DARK};
    margin-top: 10pt;
    margin-bottom: 3pt;
    page-break-after: avoid;
}}

/* ── Capability area sections ────────────────────────────────── */
h3 {{
    border-top: 1pt solid {C_BORDER};
    padding-top: 10pt;
}}

/* ── Blockquotes (CA descriptions) ──────────────────────────── */
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

blockquote p {{
    margin: 0;
}}

/* ── Lists ───────────────────────────────────────────────────── */
ul {{
    margin: 3pt 0 6pt 0;
    padding-left: 16pt;
}}

ul li {{
    margin-bottom: 2pt;
    padding-left: 2pt;
}}

/* L1 — bold domain label */
ul > li > strong {{
    color: {C_DARK};
}}

/* L2 — sub-domain items (first-level nested) */
ul > li > ul {{
    margin-top: 2pt;
    margin-bottom: 4pt;
    padding-left: 14pt;
}}

ul > li > ul > li {{
    color: {C_TEXT};
    margin-bottom: 1.5pt;
    font-size: 9pt;
}}

/* L2 labels (bold inside nested list) */
ul > li > ul > li > strong {{
    color: {C_MID};
    font-weight: 600;
}}

/* L3 — deepest capabilities */
ul > li > ul > li > ul {{
    padding-left: 12pt;
    margin-top: 1pt;
    margin-bottom: 3pt;
}}

ul > li > ul > li > ul > li {{
    font-size: 8.5pt;
    color: {C_TEXT};
    margin-bottom: 1pt;
    list-style-type: circle;
}}

/* Inline pattern references */
em {{
    color: {C_MID};
    font-style: normal;
    font-size: 8pt;
}}

/* ── Tables ──────────────────────────────────────────────────── */
table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 8.5pt;
    margin: 10pt 0 14pt 0;
    page-break-inside: avoid;
}}

thead tr {{
    background: {C_DARK};
    color: {C_WHITE};
}}

thead th {{
    padding: 5pt 8pt;
    text-align: left;
    font-weight: 600;
    font-size: 8pt;
    letter-spacing: 0.3pt;
}}

tbody tr {{
    border-bottom: 0.5pt solid {C_BORDER};
}}

tbody tr:nth-child(even) {{
    background: {C_OFFWHT};
}}

tbody td {{
    padding: 4pt 8pt;
    vertical-align: top;
}}

/* ── Code / inline code ──────────────────────────────────────── */
code {{
    font-family: 'Courier New', monospace;
    font-size: 8pt;
    background: {C_OFFWHT};
    border: 0.5pt solid {C_BORDER};
    padding: 1pt 3pt;
    border-radius: 2pt;
    color: {C_DARK};
}}

/* ── Page-break helpers ──────────────────────────────────────── */
.page-break {{
    page-break-after: always;
}}

h2 {{
    page-break-before: auto;
}}

/* Keep CA headings with their first content block */
h3 + blockquote {{
    page-break-before: avoid;
}}
"""

def md_to_html(md_text: str) -> str:
    body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>OSA Security Capability Model</title>
</head>
<body>
{body}
</body>
</html>"""


def main() -> None:
    if not SRC_MD.exists():
        print(f"ERROR: source not found: {SRC_MD}", file=sys.stderr)
        sys.exit(1)

    md_text = SRC_MD.read_text(encoding="utf-8")
    html    = md_to_html(md_text)

    print(f"Converting {SRC_MD.name} → {OUT_PDF.name} …")
    HTML(string=html, base_url=str(SRC_MD.parent)).write_pdf(
        OUT_PDF,
        stylesheets=[CSS(string=CSS_STYLES)],
        optimize_images=True,
    )
    size_kb = OUT_PDF.stat().st_size // 1024
    print(f"Done — {OUT_PDF} ({size_kb} KB)")


if __name__ == "__main__":
    main()
