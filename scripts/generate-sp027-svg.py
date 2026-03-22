#!/usr/bin/env python3
"""Generate SVG diagram for SP-027 Secure LLM Usage."""

OUTPUT = "/Users/tobias.christen/osa-workspace/website/public/images/sp-027-secure-ai-integration.svg"

# ─── Helper builders ────────────────────────────────────────────────────────

def header_badge(cx, y_top, label):
    """Pill badge for header/footer bar (opacity 0.35, sky stroke, white text)."""
    half_w = 15
    x1, x2 = cx - half_w, cx + half_w
    r = 9
    # pill path: left semicircle centre at (x1+r, cy), right at (x2-r, cy)
    cy = y_top + 9
    def pill(x1, x2, cy, r):
        return (f"M{x1+r},{cy-r} L{x2-r},{cy-r} "
                f"C{x2-r+r*.552:.3f},{cy-r} {x2},{cy-r+r*.448:.3f} {x2},{cy} "
                f"L{x2},{cy} "
                f"C{x2},{cy+r*.448:.3f} {x2-r+r*.552:.3f},{cy+r} {x2-r},{cy+r} "
                f"L{x1+r},{cy+r} "
                f"C{x1+r-r*.552:.3f},{cy+r} {x1},{cy+r*.448:.3f} {x1},{cy} "
                f"C{x1},{cy-r*.448:.3f} {x1+r-r*.552:.3f},{cy-r} {x1+r},{cy-r} z")
    p = pill(x1, x2, cy, r)
    return f"""    <g>
      <g opacity="0.35">
        <path d="{p}" fill="#007EA7"/>
        <path d="{p}" fill-opacity="0" stroke="#00A8E8" stroke-width="0.5"/>
      </g>
      <text transform="matrix(1, 0, 0, 1, {cx}, {cy})">
        <tspan x="-{len(label)*3.3:.3f}" y="2" font-family="GillSans" font-size="8" fill="#00A8E8">{label}</tspan>
      </text>
    </g>"""

def separator(cx, cy):
    """Vertical pipe separator in header/footer."""
    return f"""    <text transform="matrix(1, 0, 0, 1, {cx+1.539:.3f}, {cy})">
      <tspan x="-1.539" y="2" font-family="GillSans" font-size="8" fill="#94A3B8">|</tspan>
    </text>"""

def inline_badge(x, y, label, link=None):
    """Small teal rounded-rect inline badge (opacity 0.12)."""
    w = max(26, len(label) * 5 + 8)
    h = 16
    r = 4
    x2, y2 = x + w, y + h
    p = (f"M{x+r},{y} L{x2-r},{y} C{x2-r+r*.552:.3f},{y} {x2},{y+r*.448:.3f} {x2},{y+r} "
         f"L{x2},{y2-r} C{x2},{y2-r+r*.552:.3f} {x2-r+r*.552:.3f},{y2} {x2-r},{y2} "
         f"L{x+r},{y2} C{x+r-r*.552:.3f},{y2} {x},{y2-r*.448:.3f} {x},{y2-r} "
         f"L{x},{y+r} C{x},{y+r*.448:.3f} {x+r-r*.552:.3f},{y} {x+r},{y} z")
    cx = x + w / 2
    cy = y + h / 2
    inner = f"""      <path d="{p}" fill="#007EA7" opacity="0.12"/>
      <text transform="matrix(1, 0, 0, 1, {cx:.1f}, {cy:.1f})">
        <tspan x="-{len(label)*3.0:.1f}" y="2" font-family="GillSans" font-size="7.5" fill="#007EA7">{label}</tspan>
      </text>"""
    if link:
        return f"""    <a xlink:href="{link}">
      <g>
{inner}
      </g>
    </a>"""
    return f"""    <g>
{inner}
    </g>"""

def zone_header(x, y, w, h, color, darker, label):
    """Full-width zone column header with darker bottom strip."""
    r = 6
    # top-rounded rect
    p = (f"M{x+r},{y} L{x+w-r},{y} C{x+w-r+r*.552:.3f},{y} {x+w},{y+r*.448:.3f} {x+w},{y+r} "
         f"L{x+w},{y+h} L{x},{y+h} L{x},{y+r} C{x},{y+r*.448:.3f} {x+r-r*.552:.3f},{y} {x+r},{y} z")
    strip_h = 5
    sy = y + h - strip_h
    return f"""    <path d="{p}" fill="{color}"/>
    <rect x="{x}" y="{sy}" width="{w}" height="{strip_h}" fill="{darker}"/>
    <text transform="matrix(1, 0, 0, 1, {x + w/2:.1f}, {y + (h - strip_h)/2:.1f})">
      <tspan x="{-len(label)*3.4:.1f}" y="3" font-family="GillSans" font-size="10" font-weight="bold" fill="#FFFFFF">{label}</tspan>
    </text>"""

def card(x, y, w, h, border_color="#007EA7"):
    """Dashed-border card rect."""
    r = 5
    return f"""    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" ry="{r}" fill="white" fill-opacity="0.55" stroke="{border_color}" stroke-dasharray="6,3" stroke-width="1.5"/>"""

def card_title(x, y, label, color="#003459"):
    return f"""    <text transform="matrix(1, 0, 0, 1, {x}, {y})">
      <tspan x="0" y="0" font-family="GillSans" font-size="9.5" font-weight="bold" fill="{color}">{label}</tspan>
    </text>"""

def body_text(x, y, label, color="#334155", size=8.5):
    return f"""    <text transform="matrix(1, 0, 0, 1, {x}, {y})">
      <tspan x="0" y="0" font-family="GillSans" font-size="{size}" fill="{color}">{label}</tspan>
    </text>"""

def arrow_h(x1, x2, y, color="#007EA7"):
    """Horizontal arrow left→right."""
    aw = 7  # arrowhead width
    lines = f"""    <path d="M{x1},{y} L{x2-aw},{y}" fill="none" stroke="{color}" stroke-width="1.5"/>
    <path d="M{x2-aw},{y-4} L{x2},{y} L{x2-aw},{y+4} Z" fill="{color}"/>"""
    return lines

def zone_border(x, y, w, h, color, r=6):
    """Full zone outline (rounded rect, no fill)."""
    return f"""    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" ry="{r}" fill="none" stroke="{color}" stroke-width="1.5" opacity="0.4"/>"""

# ─── Badge rows ─────────────────────────────────────────────────────────────

def badge_row(badges, x_start, y, spacing=32):
    """Render a row of inline badges starting at x_start."""
    parts = []
    x = x_start
    for b in badges:
        parts.append(inline_badge(x, y, b, link=f"/controls/{b.replace('-','').lower()[:2].upper() + '-' + b.split('-')[1] if '-' in b else b}"))
        x += spacing
    return "\n".join(parts)

# ─── Build SVG ──────────────────────────────────────────────────────────────

lines = []

def L(s):
    lines.append(s)

# XML header
L('<?xml version="1.0" encoding="UTF-8"?>')
L('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">')
L('<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0" y="0" width="960" height="720" viewBox="0, 0, 960, 720">')

# Background
L('  <g id="Background">')
L('    <rect x="0" y="0" width="960" height="720" fill="#FFFFFF"/>')
L('  </g>')
L('  <g id="Layer_1">')

# Main inner rounded rect
L('    <path d="M8,0 L952,0 C956.418,0 960,3.582 960,8 L960,712 C960,716.418 956.418,720 952,720 L8,720 C3.582,720 0,716.418 0,712 L0,8 C0,3.582 3.582,0 8,0 z" fill="#F8FAFC"/>')

# ── HEADER BAR ──────────────────────────────────────────────────────────────
L('    <!-- HEADER BAR -->')
L('    <path d="M22,16 L938,16 C941.314,16 944,18.686 944,22 L944,76 C944,73.314 941.314,76 938,76 L22,76 C18.686,76 16,73.314 16,70 L16,22 C16,18.686 18.686,16 22,16 z" fill="#00171F"/>')

# Header pattern label (left)
L('    <text transform="matrix(1, 0, 0, 1, 100, 30)">')
L('      <tspan x="0" y="3" font-family="GillSans" font-size="10" fill="#64748B">SP-027</tspan>')
L('    </text>')

# Header title (centred)
L('    <text transform="matrix(1, 0, 0, 1, 480, 31)">')
L('      <tspan x="-88" y="3.5" font-family="GillSans" font-size="13" font-weight="bold" fill="#FFFFFF">SECURE LLM USAGE</tspan>')
L('    </text>')

# Header subtitle
L('    <text transform="matrix(1, 0, 0, 1, 480, 46)">')
L('      <tspan x="-148" y="2" font-family="GillSans" font-size="8.5" fill="#94A3B8">Security architecture for integrating large language models into enterprise environments</tspan>')
L('    </text>')

# Header badges — critical controls, two groups separated by |
# Group 1: AC-03, AC-04, AU-02, AU-03, CA-07
badge_y_top = 56
bx = 108
badge_spacing = 54
critical = ["AC-03","AC-04","AU-02","AU-03","CA-07"]
for ctrl in critical:
    L(header_badge(bx, badge_y_top, ctrl))
    bx += badge_spacing

L(separator(bx - 10, badge_y_top + 9))

# Group 2: RA-08, SA-09, SC-04, SC-07, SI-10, SR-02
group2 = ["RA-08","SA-09","SC-04","SC-07","SI-10","SR-02"]
bx += 14
for ctrl in group2:
    L(header_badge(bx, badge_y_top, ctrl))
    bx += badge_spacing

L(separator(bx - 10, badge_y_top + 9))

# Group 3: PT-02, PT-03, SA-04, SA-11, SI-03
group3 = ["PT-02","PT-03","SA-04","SA-11","SI-03"]
bx += 14
for ctrl in group3:
    L(header_badge(bx, badge_y_top, ctrl))
    bx += badge_spacing

# ── THREE COLUMN ZONES ───────────────────────────────────────────────────────
L('    <!-- THREE COLUMN ZONES -->')

col_top = 88
col_bot = 492
col_h = col_bot - col_top

# Left column  x=16-308
lx, lw = 16, 292
# Center column x=320-644
cx_col, cw = 320, 308
# Right column x=656-944
rx, rw = 656, 288

# Zone outlines
L(zone_border(lx, col_top, lw, col_h, "#003459"))
L(zone_border(cx_col, col_top, cw, col_h, "#007EA7"))
L(zone_border(rx, col_top, rw, col_h, "#00A8E8"))

# Zone headers
L(zone_header(lx, col_top, lw, 32, "#003459", "#001F35", "INPUT &amp; CLASSIFICATION"))
L(zone_header(cx_col, col_top, cw, 32, "#007EA7", "#005A7A", "LLM SECURITY CONTROLS"))
L(zone_header(rx, col_top, rw, 32, "#00A8E8", "#0075A3", "LLM PROVIDER BOUNDARY"))

# ── LEFT COLUMN CARDS ────────────────────────────────────────────────────────
L('    <!-- LEFT COLUMN -->')

# Card 1: Data Classification  y=130-220
L(card(lx+8, 130, lw-16, 90, "#003459"))
L(card_title(lx+16, 144, "Data Classification", "#003459"))
L(body_text(lx+16, 158, "Classify all data before it enters the prompt", "#334155"))
L(body_text(lx+16, 171, "No data above the LLM trust boundary", "#475569", 8))

# Classification tier pills (small coloured labels)
tier_colors = [("#22C55E","Public"),("#EAB308","Internal"),("#F97316","Confidential"),("#EF4444","Restricted")]
tx = lx+16
for col, lbl in tier_colors:
    tw = len(lbl)*5+10
    L(f'    <rect x="{tx}" y="178" width="{tw}" height="13" rx="3" ry="3" fill="{col}" opacity="0.15"/>')
    L(f'    <text transform="matrix(1, 0, 0, 1, {tx+tw/2:.1f}, 185.5)">'
      f'<tspan x="-{len(lbl)*2.8:.1f}" y="0" font-family="GillSans" font-size="7" fill="{col}" font-weight="bold">{lbl}</tspan></text>')
    tx += tw + 6

# Inline badges
L(inline_badge(lx+16, 197, "AC-04", "/controls/ac-04"))
L(inline_badge(lx+16+30, 197, "PT-02", "/controls/pt-02"))
L(inline_badge(lx+16+60, 197, "SC-04", "/controls/sc-04"))

# Card 2: Context Window Management  y=232-318
L(card(lx+8, 232, lw-16, 86, "#003459"))
L(card_title(lx+16, 246, "Context Window Management", "#003459"))
L(body_text(lx+16, 260, "RAG context · conversation history · tool outputs", "#334155", 8.5))
L(body_text(lx+16, 273, "Each source classified and scope-limited", "#475569", 8))
L(body_text(lx+16, 284, "Inject only what is necessary at the lowest tier", "#475569", 8))
L(inline_badge(lx+16, 296, "SC-04", "/controls/sc-04"))
L(inline_badge(lx+16+30, 296, "PT-03", "/controls/pt-03"))
L(inline_badge(lx+16+60, 296, "AC-04", "/controls/ac-04"))

# Card 3: Prompt Construction  y=330-460
L(card(lx+8, 330, lw-16, 132, "#003459"))
L(card_title(lx+16, 344, "Prompt Construction", "#003459"))
L(body_text(lx+16, 358, "System prompt separated from user input", "#334155", 8.5))

# System prompt / User input sub-boxes
L('    <rect x="28" y="366" width="120" height="28" rx="3" fill="#003459" fill-opacity="0.08" stroke="#003459" stroke-width="0.5" stroke-dasharray="3,2"/>')
L('    <text transform="matrix(1, 0, 0, 1, 38, 376)"><tspan x="0" y="0" font-family="GillSans" font-size="7.5" font-weight="bold" fill="#003459">System Prompt</tspan></text>')
L('    <text transform="matrix(1, 0, 0, 1, 38, 387)"><tspan x="0" y="0" font-family="GillSans" font-size="7" fill="#475569">Policy · Instructions · Scope</tspan></text>')

L('    <rect x="162" y="366" width="120" height="28" rx="3" fill="#EF4444" fill-opacity="0.06" stroke="#EF4444" stroke-width="0.5" stroke-dasharray="3,2"/>')
L('    <text transform="matrix(1, 0, 0, 1, 172, 376)"><tspan x="0" y="0" font-family="GillSans" font-size="7.5" font-weight="bold" fill="#EF4444">User Input</tspan></text>')
L('    <text transform="matrix(1, 0, 0, 1, 172, 387)"><tspan x="0" y="0" font-family="GillSans" font-size="7" fill="#475569">Treated as untrusted</tspan></text>')

L(body_text(lx+16, 406, '"\u201cSystem prompt = policy, not secret\u201d', "#64748B", 7.5))
L(body_text(lx+16, 418, "User input sanitised before assembly", "#475569", 8))
L(body_text(lx+16, 430, "Structural separation enforced at runtime", "#475569", 8))

L(inline_badge(lx+16, 444, "SI-10", "/controls/si-10"))
L(inline_badge(lx+16+30, 444, "SC-07", "/controls/sc-07"))
L(inline_badge(lx+16+60, 444, "SI-03", "/controls/si-03"))

# Arrow from left → centre
L(arrow_h(lx+lw, 335+66, col_top+col_h//2 - 70, "#007EA7"))

# ── CENTER COLUMN CARDS ──────────────────────────────────────────────────────
L('    <!-- CENTER COLUMN -->')

# Card 1: Prompt Injection Defence  y=130-228
L(card(cx_col+8, 130, cw-16, 98, "#007EA7"))
L(card_title(cx_col+16, 144, "Prompt Injection Defence", "#007EA7"))
L(body_text(cx_col+16, 158, "Injection: attacker input overrides instructions", "#334155", 8.5))
L(body_text(cx_col+16, 170, "The SQL injection of the AI era", "#64748B", 7.5))

# Sub-items with bullet dots
for i, item in enumerate(["Input sanitisation","Structural separation","Injection detection"]):
    iy = 182 + i*13
    L(f'    <circle cx="{cx_col+18}" cy="{iy+1}" r="2.5" fill="#007EA7" opacity="0.6"/>')
    L(body_text(cx_col+25, iy, item, "#475569", 8))

L(inline_badge(cx_col+16, 212, "SI-10", "/controls/si-10"))
L(inline_badge(cx_col+16+30, 212, "SI-03", "/controls/si-03"))
L(inline_badge(cx_col+16+60, 212, "SC-07", "/controls/sc-07"))

# Card 2: Output Validation  y=240-330
L(card(cx_col+8, 240, cw-16, 90, "#007EA7"))
L(card_title(cx_col+16, 254, "Output Validation", "#007EA7"))
L(body_text(cx_col+16, 268, "Validate before acting \u2014 LLMs hallucinate", "#334155", 8.5))
L(body_text(cx_col+16, 280, "Security-critical outputs require human or", "#475569", 8))
L(body_text(cx_col+16, 291, "deterministic verification before action", "#475569", 8))
L(body_text(cx_col+16, 302, "Never act on unvalidated LLM output in pipelines", "#64748B", 7.5))

L(inline_badge(cx_col+16, 314, "SI-10", "/controls/si-10"))
L(inline_badge(cx_col+16+30, 314, "CA-07", "/controls/ca-07"))
L(inline_badge(cx_col+16+60, 314, "SA-11", "/controls/sa-11"))

# Card 3: Jailbreak Detection  y=342-420
L(card(cx_col+8, 342, cw-16, 78, "#007EA7"))
L(card_title(cx_col+16, 356, "Jailbreak Detection", "#007EA7"))
L(body_text(cx_col+16, 370, "Adversarial prompts that override alignment", "#334155", 8.5))
L(body_text(cx_col+16, 382, "Red-team test prompts quarterly", "#475569", 8))
L(body_text(cx_col+16, 393, "Monitor for adversarial input patterns", "#475569", 8))

L(inline_badge(cx_col+16, 406, "SI-10", "/controls/si-10"))
L(inline_badge(cx_col+16+30, 406, "AC-03", "/controls/ac-03"))
L(inline_badge(cx_col+16+60, 406, "SA-11", "/controls/sa-11"))

# Card 4: Model Extraction Control  y=432-470
L(card(cx_col+8, 432, cw-16, 50, "#007EA7"))
L(card_title(cx_col+16, 445, "Model Extraction Control", "#007EA7"))
L(body_text(cx_col+16, 458, "Rate limiting \u00b7 Anomaly detection \u00b7 System prompt protection", "#475569", 7.5))

L(inline_badge(cx_col+16, 468, "SR-02", "/controls/sr-02"))
L(inline_badge(cx_col+16+30, 468, "SA-09", "/controls/sa-09"))
L(inline_badge(cx_col+16+60, 468, "AU-02", "/controls/au-02"))

# Arrow from center → right
L(arrow_h(cx_col+cw, 130+50, col_top+col_h//2 - 70, "#00A8E8"))

# ── RIGHT COLUMN CARDS ───────────────────────────────────────────────────────
L('    <!-- RIGHT COLUMN -->')

# Card 1: Provider Security Assessment  y=130-218
L(card(rx+8, 130, rw-16, 88, "#00A8E8"))
L(card_title(rx+16, 144, "Provider Security Assessment", "#00A8E8"))
L(body_text(rx+16, 158, "Treat LLM provider as critical third party", "#334155", 8.5))
L(body_text(rx+16, 170, "Contractual data handling agreements required", "#475569", 8))

for i, item in enumerate(["SOC 2 Type II certification","ISO 27001 / 27017","Data Processing Agreement (DPA)"]):
    iy = 181 + i*12
    L(f'    <circle cx="{rx+18}" cy="{iy+1}" r="2.5" fill="#00A8E8" opacity="0.6"/>')
    L(body_text(rx+25, iy, item, "#475569", 8))

L(inline_badge(rx+16, 208, "SA-09", "/controls/sa-09"))
L(inline_badge(rx+16+30, 208, "SA-04", "/controls/sa-04"))

# Card 2: Data Residency & Privacy  y=230-316
L(card(rx+8, 230, rw-16, 86, "#00A8E8"))
L(card_title(rx+16, 244, "Data Residency &amp; Privacy", "#00A8E8"))
L(body_text(rx+16, 258, "Where is prompt data processed and stored?", "#334155", 8.5))
L(body_text(rx+16, 270, "GDPR, financial reg, and sector rules apply", "#475569", 8))
L(body_text(rx+16, 281, "to LLM input and conversation history", "#475569", 8))
L(body_text(rx+16, 292, "Validate residency before production deployment", "#64748B", 7.5))

L(inline_badge(rx+16, 304, "PT-02", "/controls/pt-02"))
L(inline_badge(rx+16+30, 304, "PT-03", "/controls/pt-03"))
L(inline_badge(rx+16+60, 304, "SA-09", "/controls/sa-09"))

# Card 3: Fine-Tuning Risks  y=328-416
L(card(rx+8, 328, rw-16, 88, "#00A8E8"))
L(card_title(rx+16, 342, "Fine-Tuning Risks", "#00A8E8"))
L(body_text(rx+16, 356, "Fine-tuning on PII risks training data leakage", "#334155", 8.5))
L(body_text(rx+16, 368, "Privacy inference: reconstruct training samples", "#475569", 8))

for i, item in enumerate(["Differential privacy techniques","Data minimisation before fine-tune","Sanitise / anonymise training corpus"]):
    iy = 379 + i*12
    L(f'    <circle cx="{rx+18}" cy="{iy+1}" r="2.5" fill="#00A8E8" opacity="0.6"/>')
    L(body_text(rx+25, iy, item, "#475569", 8))

L(inline_badge(rx+16, 408, "RA-08", "/controls/ra-08"))
L(inline_badge(rx+16+30, 408, "PT-02", "/controls/pt-02"))
L(inline_badge(rx+16+60, 408, "PT-03", "/controls/pt-03"))

# Card 4: Provider Tiers & Fallback  y=428-472
L(card(rx+8, 428, rw-16, 54, "#00A8E8"))
L(card_title(rx+16, 441, "Provider Tiers &amp; Fallback", "#00A8E8"))
L(body_text(rx+16, 454, "Cloud API \u00b7 Private hosted \u00b7 On-premises", "#475569", 8))
L(body_text(rx+16, 465, "Higher sensitivity \u2192 stricter residency requirement", "#64748B", 7.5))

L(inline_badge(rx+16, 473, "SA-09", "/controls/sa-09"))
L(inline_badge(rx+16+30, 473, "SA-04", "/controls/sa-04"))
L(inline_badge(rx+16+60, 473, "SC-04", "/controls/sc-04"))

# ── AUDIT & INTERACTION LOGGING PANEL ────────────────────────────────────────
L('    <!-- AUDIT PANEL -->')

audit_y = 502
audit_h = 74
audit_hdr_h = 20

# Outer rounded rect
L(f'    <rect x="16" y="{audit_y}" width="928" height="{audit_h}" rx="6" ry="6" fill="#003459" fill-opacity="0.07" stroke="#003459" stroke-width="1.5" stroke-dasharray="6,3"/>')

# Dark header strip
L(f'    <rect x="16" y="{audit_y}" width="928" height="{audit_hdr_h}" rx="6" ry="6" fill="#003459"/>')
L(f'    <rect x="16" y="{audit_y+audit_hdr_h-6}" width="928" height="6" fill="#003459"/>')
L(f'    <text transform="matrix(1, 0, 0, 1, 480, {audit_y+audit_hdr_h/2})">')
L(f'      <tspan x="-130" y="3" font-family="GillSans" font-size="10" font-weight="bold" fill="#FFFFFF">AUDIT &amp; INTERACTION LOGGING</tspan>')
L(f'    </text>')

# Four sub-sections
audit_items = [
    ("Prompt Logged", "User identity · model version · timestamp"),
    ("Response Logged", "Output hash · latency · token count"),
    ("Anomaly Detection", "Rate · patterns · jailbreak signals"),
    ("Retention &amp; Review", "SIEM integration · periodic review"),
]
sub_w = 928 // 4
for i, (title, desc) in enumerate(audit_items):
    sx = 16 + i * sub_w
    # vertical divider (except first)
    if i > 0:
        L(f'    <line x1="{sx}" y1="{audit_y+audit_hdr_h+4}" x2="{sx}" y2="{audit_y+audit_h-4}" stroke="#003459" stroke-width="0.5" opacity="0.3"/>')
    cx_sub = sx + sub_w // 2
    L(f'    <text transform="matrix(1, 0, 0, 1, {cx_sub}, {audit_y+audit_hdr_h+12})">')
    L(f'      <tspan x="-{len(title)*3.2:.1f}" y="0" font-family="GillSans" font-size="8.5" font-weight="bold" fill="#003459">{title}</tspan>')
    L(f'    </text>')
    L(f'    <text transform="matrix(1, 0, 0, 1, {cx_sub}, {audit_y+audit_hdr_h+26})">')
    L(f'      <tspan x="-{len(desc)*2.65:.1f}" y="0" font-family="GillSans" font-size="7.5" fill="#475569">{desc}</tspan>')
    L(f'    </text>')

# Audit badges
audit_badges = ["AU-02","AU-03","AU-06","CA-07"]
abx = 16+8
aby = audit_y + audit_hdr_h + 42
for b in audit_badges:
    L(inline_badge(abx, aby, b, f"/controls/{b.lower().replace('-','-')}"))
    abx += 30

# ── FOOTER BAR ───────────────────────────────────────────────────────────────
L('    <!-- FOOTER BAR -->')

footer_y = 586
footer_h = 58

# Dark footer background
L(f'    <path d="M22,{footer_y} L938,{footer_y} C941.314,{footer_y} 944,{footer_y+2.686:.3f} 944,{footer_y+6} L944,{footer_y+footer_h-6} C944,{footer_y+footer_h-2.686:.3f} 941.314,{footer_y+footer_h} 938,{footer_y+footer_h} L22,{footer_y+footer_h} C18.686,{footer_y+footer_h} 16,{footer_y+footer_h-2.686:.3f} 16,{footer_y+footer_h-6} L16,{footer_y+6} C16,{footer_y+2.686:.3f} 18.686,{footer_y} 22,{footer_y} z" fill="#00171F"/>')

L(f'    <text transform="matrix(1, 0, 0, 1, 480, {footer_y+14})">')
L(f'      <tspan x="-198" y="2" font-family="GillSans" font-size="9" font-weight="bold" fill="#FFFFFF">CONTINUOUS MONITORING  \u00b7  INCIDENT RESPONSE  \u00b7  SECURITY TESTING</tspan>')
L(f'    </text>')

# Footer badges - Group 1
footer_badge_y = footer_y + 28
fbx = 108
for ctrl in ["AC-03","AC-04","AU-02","AU-03","CA-07"]:
    L(header_badge(fbx, footer_badge_y, ctrl))
    fbx += 54
L(separator(fbx - 10, footer_badge_y + 9))
fbx += 14
for ctrl in ["SA-09","SC-04","SC-07","SI-10","SR-02"]:
    L(header_badge(fbx, footer_badge_y, ctrl))
    fbx += 54
L(separator(fbx - 10, footer_badge_y + 9))
fbx += 14
for ctrl in ["RA-08","PT-02","IR-04"]:
    L(header_badge(fbx, footer_badge_y, ctrl))
    fbx += 54

# ── REFERENCES FOOTER ────────────────────────────────────────────────────────
L('    <!-- REFERENCES -->')

ref_y = 656
L(f'    <text transform="matrix(1, 0, 0, 1, 100, {ref_y})">')
L(f'      <tspan x="0" y="2.5" font-family="GillSans" font-size="10" fill="#334155">SP-027: Secure LLM Usage</tspan>')
L(f'    </text>')
L(f'    <text transform="matrix(1, 0, 0, 1, 100, {ref_y+16})">')
L(f'      <tspan x="0" y="2" font-family="GillSans" font-size="8.5" fill="#64748B">26 NIST 800-53 Rev 5 controls across 9 families  \u00b7  Authors: Aurelius, Vitruvius  \u00b7  Draft  \u00b7  2026-02-22</tspan>')
L(f'    </text>')

# Ref links right side
L(f'    <text transform="matrix(1, 0, 0, 1, 944, {ref_y})">')
L(f'      <tspan x="-455" y="2.5" font-family="GillSans" font-size="8.5" fill="#007EA7">OWASP LLM Top 10  \u00b7  NIST AI RMF  \u00b7  SP-045 AI Governance  \u00b7  SP-047 Agentic AI  \u00b7  SP-048 Offensive AI</tspan>')
L(f'    </text>')
L(f'    <text transform="matrix(1, 0, 0, 1, 944, {ref_y+16})">')
L(f'      <tspan x="-261" y="2" font-family="GillSans" font-size="9" fill="#94A3B8">opensecurityarchitecture.org/patterns/sp-027</tspan>')
L(f'    </text>')

# Legend (bottom bar)
legend_y = ref_y + 36

# Control flow arrow
L(f'    <path d="M464,{legend_y+2} L496,{legend_y+2}" fill="none" stroke="#003459" stroke-width="1.5"/>')
L(f'    <path d="M492,{legend_y-2} L496,{legend_y+2} L492,{legend_y+6} Z" fill="#003459"/>')
L(f'    <text transform="matrix(1, 0, 0, 1, 527, {legend_y+2})"><tspan x="-23" y="2.5" font-family="GillSans" font-size="8.5" fill="#64748B">Data flow</tspan></text>')

# Data response arrow (dashed)
L(f'    <path d="M564,{legend_y+2} L596,{legend_y+2}" fill="none" stroke="#00A8E8" stroke-width="1.5" stroke-dasharray="4,3"/>')
L(f'    <path d="M592,{legend_y-2} L596,{legend_y+2} L592,{legend_y+6} Z" fill="#00A8E8"/>')
L(f'    <text transform="matrix(1, 0, 0, 1, 633, {legend_y+2})"><tspan x="-30" y="2.5" font-family="GillSans" font-size="8.5" fill="#64748B">LLM response</tspan></text>')

# Inline badge legend
L(f'    <rect x="682" y="{legend_y-6}" width="28" height="16" rx="4" ry="4" fill="#007EA7" opacity="0.12"/>')
L(f'    <text transform="matrix(1, 0, 0, 1, 696, {legend_y+2})"><tspan x="-11" y="2" font-family="GillSans" font-size="8" fill="#007EA7">XX-00</tspan></text>')
L(f'    <text transform="matrix(1, 0, 0, 1, 772, {legend_y+2})"><tspan x="-50" y="2.5" font-family="GillSans" font-size="8.5" fill="#64748B">NIST control (click to view)</tspan></text>')

L('  </g>')
L('</svg>')

# Write output
svg = "\n".join(lines)
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(svg)

print(f"Written: {OUTPUT}")
print(f"Lines:   {len(lines)}")
print(f"Bytes:   {len(svg.encode())}")
