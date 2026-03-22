#!/usr/bin/env python3
"""Generate SP-048 Offensive AI and Deepfake Defence SVG diagram."""

OUTPUT_PATH = "/Users/tobias.christen/osa-workspace/website/public/images/sp-048-offensive-ai-deepfake-defence.svg"

def xe(s):
    """XML-escape a string for use inside attribute values and text content."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ─────────────────────────────────────────────
# Helper: rounded-rect path string
# ─────────────────────────────────────────────
def rrect(x, y, w, h, r=6):
    x2, y2 = x + w, y + h
    k = r * 0.552
    return (
        f"M{x+r},{y} L{x2-r},{y} C{x2-r+k},{y} {x2},{y+r-k} {x2},{y+r} "
        f"L{x2},{y2-r} C{x2},{y2-r+k} {x2-r+k},{y2} {x2-r},{y2} "
        f"L{x+r},{y2} C{x+r-k},{y2} {x},{y2-r+k} {x},{y2-r} "
        f"L{x},{y+r} C{x},{y+r-k} {x+r-k},{y} {x+r},{y} z"
    )

# ─────────────────────────────────────────────
# Helper: control badge (pill)
# style="header"  → opacity 0.35, stroke #00A8E8, white text
# style="inline"  → opacity 0.12, no stroke, teal text
# ─────────────────────────────────────────────
def badge(label, cx, cy, style="inline"):
    hw = 16
    r  = 7
    x1, x2 = cx - hw, cx + hw
    k = r * 0.552
    pill = (
        f"M{x1},{cy-r} L{x2},{cy-r} C{x2+k},{cy-r} {x2+r},{cy-r+k} "
        f"{x2+r},{cy} C{x2+r},{cy+k} {x2+k},{cy+r} {x2},{cy+r} "
        f"L{x1},{cy+r} C{x1-k},{cy+r} {x1-r},{cy+k} {x1-r},{cy} "
        f"C{x1-r},{cy-r+k} {x1-k},{cy-r} {x1},{cy-r} z"
    )
    txt_offset = f"{-len(label)*2.8:.3f}"
    if style == "header":
        return f"""    <g>
      <g opacity="0.35">
        <path d="{pill}" fill="#007EA7"/>
        <path d="{pill}" fill-opacity="0" stroke="#00A8E8" stroke-width="0.5"/>
      </g>
      <text transform="matrix(1, 0, 0, 1, {cx}, {cy})">
        <tspan x="{txt_offset}" y="2" font-family="GillSans" font-size="8" fill="#00A8E8">{xe(label)}</tspan>
      </text>
    </g>"""
    else:
        return f"""    <g>
      <g opacity="0.12">
        <path d="{pill}" fill="#007EA7"/>
      </g>
      <text transform="matrix(1, 0, 0, 1, {cx}, {cy})">
        <tspan x="{txt_offset}" y="2" font-family="GillSans" font-size="7.5" fill="#007EA7">{xe(label)}</tspan>
      </text>
    </g>"""

# ─────────────────────────────────────────────
# Helper: row of badges starting at cx, given cy
# ─────────────────────────────────────────────
def badge_row(labels, start_cx, cy, gap=38, style="inline"):
    out = []
    cx = start_cx
    for lbl in labels:
        out.append(badge(lbl, cx, cy, style=style))
        cx += gap
    return "\n".join(out)

# ─────────────────────────────────────────────
# Helper: down-arrow between two y positions at given x
# ─────────────────────────────────────────────
def arrow_down(x, y1, y2, label=""):
    mid_y = (y1 + y2) / 2
    parts = [
        f"""    <g>
      <path d="M{x},{y1} L{x},{y2-5}" fill-opacity="0" stroke="#007EA7" stroke-width="1.5"/>
      <path d="M{x-4},{y2-7} L{x},{y2} L{x+4},{y2-7} z" fill="#007EA7"/>
    </g>"""
    ]
    if label:
        lw = max(len(label) * 4.5 + 10, 24)
        lh = 10
        lx = x - lw/2
        ly = mid_y - lh/2
        parts.append(f"""    <rect x="{lx:.1f}" y="{ly:.1f}" width="{lw:.1f}" height="{lh}" rx="3" fill="white" opacity="0.9"/>
    <text transform="matrix(1, 0, 0, 1, {x}, {mid_y})">
      <tspan x="{-len(label)*2.1:.1f}" y="2" font-family="GillSans" font-size="7" fill="#007EA7">{xe(label)}</tspan>
    </text>""")
    return "\n".join(parts)

# ─────────────────────────────────────────────
# Helper: zone column container (outer card + header band)
# ─────────────────────────────────────────────
def zone_column(x, y, w, h, title, header_color, r=6):
    outer = rrect(x, y, w, h, r=r)
    hdr   = rrect(x, y, w, 26, r=r)
    # solid rectangle to flatten bottom of header curve
    hdr_b = f"M{x},{y+14} L{x+w},{y+14} L{x+w},{y+26} L{x},{y+26} z"
    cx_t  = x + w / 2
    tw = len(title) * 3.2
    return f"""    <g>
      <path d="{outer}" fill="#FFFFFF"/>
      <path d="{outer}" fill-opacity="0" stroke="{header_color}" stroke-width="2" stroke-dasharray="6,3"/>
    </g>
    <path d="{hdr}" fill="{header_color}"/>
    <path d="{hdr_b}" fill="{header_color}"/>
    <text transform="matrix(1, 0, 0, 1, {cx_t}, {y+15})">
      <tspan x="-{tw:.1f}" y="3" font-family="GillSans" font-size="11" fill="#FFFFFF">{xe(title)}</tspan>
    </text>"""

# ─────────────────────────────────────────────
# Helper: content card (white box, dashed border, title + body lines + badges)
# subtitle may contain \n for multi-line
# ─────────────────────────────────────────────
def content_box(x, y, w, h, title, subtitle, badge_labels, badge_cy, accent="#007EA7"):
    p = rrect(x, y, w, h, r=4)
    out = [
        f"""    <g>
      <path d="{p}" fill="#FFFFFF"/>
      <path d="{p}" fill-opacity="0" stroke="{accent}" stroke-width="1" stroke-dasharray="5,3"/>
    </g>""",
        f"""    <text transform="matrix(1, 0, 0, 1, {x+8}, {y+14})">
      <tspan x="0" y="0" font-family="GillSans" font-size="9" font-weight="bold" fill="#003459">{xe(title)}</tspan>
    </text>"""
    ]
    lines = subtitle.split("\n")
    for i, line in enumerate(lines):
        out.append(
            f"""    <text transform="matrix(1, 0, 0, 1, {x+8}, {y+27+i*11})">
      <tspan x="0" y="0" font-family="GillSans" font-size="7.5" fill="#475569">{xe(line)}</tspan>
    </text>"""
        )
    # Badges — start at x+20 with gap 38
    bcx = x + 20
    for lbl in badge_labels:
        out.append(badge(lbl, bcx, badge_cy, style="inline"))
        bcx += 38
    return "\n".join(out)

# ─────────────────────────────────────────────
# Build SVG
# ─────────────────────────────────────────────
def build_svg():
    out = []
    out.append("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     x="0" y="0" width="960" height="720" viewBox="0, 0, 960, 720">""")

    # ── Background ────────────────────────────────────────────────
    out.append("""  <g id="Background">
    <rect x="0" y="0" width="960" height="720" fill="#FFFFFF"/>
  </g>
  <g id="Layer_1">""")
    out.append(f"""    <path d="{rrect(0,0,960,720,r=8)}" fill="#F8FAFC"/>""")

    # ── TOP HEADER BAR (y=16-76) ──────────────────────────────────
    out.append(f"""    <path d="{rrect(16,16,928,60,r=6)}" fill="#00171F"/>""")
    # Title
    out.append("""    <text transform="matrix(1, 0, 0, 1, 480, 32)">
      <tspan x="-162" y="3" font-family="GillSans" font-size="12" fill="#FFFFFF">SP-048 · OFFENSIVE AI AND DEEPFAKE DEFENCE</tspan>
    </text>""")
    # Subtitle description
    out.append("""    <text transform="matrix(1, 0, 0, 1, 480, 46)">
      <tspan x="-168" y="2" font-family="GillSans" font-size="7.5" fill="#94A3B8">Defending against AI-weaponised deepfakes, voice cloning, synthetic identity fraud and AI-accelerated attacks</tspan>
    </text>""")

    # Header badge rows — split into left group / separator / right group
    hbadges_a = ["AT-02","AT-03","IA-02","SC-23","PM-16"]
    hbadges_b = ["AU-02","AU-06","CA-07","IA-03","IR-04","IR-06"]
    hbadges_c = ["PS-06","RA-03","RA-05","SA-04","SA-08","SA-11","SI-03","SI-04","SI-05","SI-10"]
    cx = 50
    for lbl in hbadges_a:
        out.append(badge(lbl, cx, 64, style="header"))
        cx += 38
    out.append(f"""    <text transform="matrix(1, 0, 0, 1, {cx+4}, 64)">
      <tspan x="-2" y="2" font-family="GillSans" font-size="8" fill="#94A3B8">|</tspan>
    </text>""")
    cx += 14
    for lbl in hbadges_b:
        out.append(badge(lbl, cx, 64, style="header"))
        cx += 38
    out.append(f"""    <text transform="matrix(1, 0, 0, 1, {cx+4}, 64)">
      <tspan x="-2" y="2" font-family="GillSans" font-size="8" fill="#94A3B8">|</tspan>
    </text>""")
    cx += 14
    for lbl in hbadges_c:
        out.append(badge(lbl, cx, 64, style="header"))
        cx += 38

    # ── THREE ZONE COLUMNS (y=86–406) ─────────────────────────────
    COL_Y = 86
    COL_H = 322
    COL_W = 298
    LX  = 16
    MCX = 330
    RX  = 644

    out.append(zone_column(LX,  COL_Y, COL_W, COL_H, "IDENTITY & VOICE ATTACKS",   "#003459"))
    out.append(zone_column(MCX, COL_Y, COL_W, COL_H, "CONTENT & PHISHING ATTACKS",  "#007EA7"))
    out.append(zone_column(RX,  COL_Y, COL_W, COL_H, "ADVERSARIAL INTELLIGENCE",    "#00A8E8"))

    # ── LEFT COLUMN BOXES ─────────────────────────────────────────
    PAD = 8
    BW  = COL_W - 2*PAD   # box width = 282

    # L1: Executive Impersonation (y=122–192)
    out.append(content_box(
        LX+PAD, 122, BW, 66,
        "Executive Impersonation",
        "Deepfake video/audio targeting finance,\nboard approvals & HR authorisations",
        ["IA-02","SC-23","PS-06"],
        badge_cy=176, accent="#003459"
    ))
    out.append(arrow_down(LX + COL_W/2, 188, 200, "verify"))

    # L2: Voice Cloning & Vishing (y=200–272)
    out.append(content_box(
        LX+PAD, 200, BW, 68,
        "Voice Cloning & Vishing",
        "Synthetic voice targeting helpdesk,\npayment authorisation & wire fraud",
        ["IA-02","AT-02","IR-04"],
        badge_cy=255, accent="#003459"
    ))
    out.append(arrow_down(LX + COL_W/2, 268, 280, "escalate"))

    # L3: Synthetic Identity Fraud (y=280–396)
    out.append(content_box(
        LX+PAD, 280, BW, 116,
        "Synthetic Identity Fraud",
        "AI-generated IDs defeating remote\nonboarding, KYC & AML controls\nFraudulent credit, insurance & benefits\nclaims at automated scale",
        ["IA-02","SA-04","SA-11","RA-05"],
        badge_cy=382, accent="#003459"
    ))

    # ── CENTER COLUMN BOXES ────────────────────────────────────────
    # C1: AI-Generated Spear Phishing (y=122–216)
    out.append(content_box(
        MCX+PAD, 122, BW, 90,
        "AI-Generated Spear Phishing",
        "Personalised, high-quality phishing at scale\nEmail · SMS · Social media · Vishing\nContext-aware lures from OSINT harvesting",
        ["AT-02","AT-03","SI-03","SI-04"],
        badge_cy=198, accent="#007EA7"
    ))
    out.append(arrow_down(MCX + COL_W/2, 212, 224, "detect"))

    # C2: Fraudulent Documents & Claims (y=224–312)
    out.append(content_box(
        MCX+PAD, 224, BW, 84,
        "Fraudulent Documents & Claims",
        "Fake invoices, evidence, regulatory\nfilings & contracts at industrial scale\nAI-enhanced document forgery",
        ["SA-11","AU-02","SA-08"],
        badge_cy=294, accent="#007EA7"
    ))
    out.append(arrow_down(MCX + COL_W/2, 308, 320, "trace"))

    # C3: Content Provenance Gaps (y=320–396)
    out.append(content_box(
        MCX+PAD, 320, BW, 74,
        "Content Provenance Gaps",
        "Unverified origin enables injection,\ndeception & downstream trust abuse",
        ["SC-23","SA-08","AU-02"],
        badge_cy=378, accent="#007EA7"
    ))

    # ── RIGHT COLUMN BOXES ────────────────────────────────────────
    # R1: Adversarial AI Threat Intelligence (y=122–236)
    out.append(content_box(
        RX+PAD, 122, BW, 110,
        "Adversarial AI Threat Intelligence",
        "AI monitors enterprise defences to\noptimise attack timing & vectors\nAttackers use LLMs to automate recon\nand map exploitable attack paths",
        ["PM-16","RA-03","SI-05","CA-07"],
        badge_cy=218, accent="#00A8E8"
    ))
    out.append(arrow_down(RX + COL_W/2, 232, 244, "inform"))

    # R2: AI-Accelerated Exploit Development (y=244–334)
    out.append(content_box(
        RX+PAD, 244, BW, 86,
        "AI-Accelerated Exploit Development",
        "Vulnerability-to-exploit window shrinks\nfrom weeks to hours with AI assistance\nZero-day synthesis & fuzzing at scale",
        ["RA-05","SI-05","PM-16"],
        badge_cy=316, accent="#00A8E8"
    ))
    out.append(arrow_down(RX + COL_W/2, 330, 342, "mitigate"))

    # R3: Deepfake Detection & Content Auth (y=342–396)
    out.append(content_box(
        RX+PAD, 342, BW, 52,
        "Deepfake Detection",
        "C2PA manifests · hash-chain provenance · liveness",
        ["SI-10","SC-23","SA-11","SA-08"],
        badge_cy=380, accent="#00A8E8"
    ))

    # ── DETECTION & VERIFICATION LAYER (y=418–496) ─────────────────
    DY = 418
    DH = 78
    out.append(f"""    <path d="{rrect(16, DY, 928, DH, r=5)}" fill="#003459"/>""")
    out.append(f"""    <path d="{rrect(16, DY, 928, DH, r=5)}" fill-opacity="0" stroke="#007EA7" stroke-width="1.5"/>""")
    out.append(f"""    <rect x="16" y="{DY}" width="4" height="{DH}" rx="2" fill="#007EA7"/>""")
    out.append(f"""    <text transform="matrix(1, 0, 0, 1, 480, {DY+14})">
      <tspan x="-145" y="2" font-family="GillSans" font-size="11" font-weight="bold" fill="#FFFFFF">DETECTION &amp; VERIFICATION LAYER</tspan>
    </text>""")

    det_secs = [
        ("Content Authenticity",    "C2PA manifests · hash-chain",   ["SI-10","SC-23"],          28),
        ("Identity Proofing",       "Liveness + biometric MFA",       ["IA-02","IA-03"],          262),
        ("Behavioural Anomaly",     "ML baseline + deviation alerts", ["AU-02","AU-06","SI-04"],   496),
        ("AI Threat Intelligence",  "STIX/TAXII feeds · ISACs",      ["PM-16","RA-03"],           730),
    ]
    for (dtitle, dsub, dbadges, dsx) in det_secs:
        out.append(f"""    <text transform="matrix(1, 0, 0, 1, {dsx}, {DY+32})">
      <tspan x="0" y="0" font-family="GillSans" font-size="9" font-weight="bold" fill="#00A8E8">{xe(dtitle)}</tspan>
    </text>""")
        out.append(f"""    <text transform="matrix(1, 0, 0, 1, {dsx}, {DY+44})">
      <tspan x="0" y="0" font-family="GillSans" font-size="7.5" fill="#94A3B8">{xe(dsub)}</tspan>
    </text>""")
        bcx = dsx + 18
        for lbl in dbadges:
            out.append(badge(lbl, bcx, DY + 63, style="header"))
            bcx += 38

    # Dividers between detection sections
    for div_x in [248, 482, 716]:
        out.append(f"""    <path d="M{div_x},{DY+20} L{div_x},{DY+DH-8}" fill-opacity="0" stroke="#007EA7" stroke-width="0.5" opacity="0.4"/>""")

    # ── ARCHITECTURE PRINCIPLES STRIP (y=504–566) ──────────────────
    PY = 504
    PH = 62
    out.append(f"""    <path d="{rrect(16, PY, 928, PH, r=5)}" fill="#FFFFFF"/>""")
    out.append(f"""    <path d="{rrect(16, PY, 928, PH, r=5)}" fill-opacity="0" stroke="#007EA7" stroke-width="1" stroke-dasharray="6,3"/>""")
    out.append(f"""    <text transform="matrix(1, 0, 0, 1, 30, {PY+13})">
      <tspan x="0" y="0" font-family="GillSans" font-size="9" font-weight="bold" fill="#003459">KEY ARCHITECTURE PRINCIPLES</tspan>
    </text>""")

    principles = [
        ("Assume Synthetic",      "Treat all unverified media\nas potentially AI-generated"),
        ("Out-of-Band Verify",    "Confirm high-value instructions\nvia an independent channel"),
        ("C2PA Provenance",       "Mandate content credentials\nfor all external media assets"),
        ("Zero-Trust Identity",   "Continuous re-authentication\nfor privileged operations"),
    ]
    ppw = 218
    pp_xs = [30, 256, 482, 708]
    for i, (ptitle, pbody) in enumerate(principles):
        px = pp_xs[i]
        py = PY + 24
        out.append(f"""    <rect x="{px}" y="{py}" width="{ppw}" height="{PH-28}" rx="3" fill="#007EA7" opacity="0.07"/>""")
        out.append(f"""    <text transform="matrix(1, 0, 0, 1, {px+7}, {py+12})">
      <tspan x="0" y="0" font-family="GillSans" font-size="8" font-weight="bold" fill="#007EA7">{xe(ptitle)}</tspan>
    </text>""")
        for j, pline in enumerate(pbody.split("\n")):
            out.append(f"""    <text transform="matrix(1, 0, 0, 1, {px+7}, {py+24+j*11})">
      <tspan x="0" y="0" font-family="GillSans" font-size="7" fill="#475569">{xe(pline)}</tspan>
    </text>""")

    # ── FOOTER BAR (y=576–634) ─────────────────────────────────────
    FY = 576
    FH = 56
    out.append(f"""    <path d="{rrect(16, FY, 928, FH, r=6)}" fill="#00171F"/>""")
    out.append(f"""    <text transform="matrix(1, 0, 0, 1, 300, {FY+14})">
      <tspan x="-175" y="2" font-family="GillSans" font-size="11" fill="#FFFFFF">CONTINUOUS MONITORING &amp; INCIDENT RESPONSE</tspan>
    </text>""")

    fbadges_l = ["AU-02","AU-06","IR-04","IR-06","CA-07"]
    fbadges_r = ["SI-03","SI-04","SI-05","SI-10"]
    fcx = 30
    for lbl in fbadges_l:
        out.append(badge(lbl, fcx, FY + 40, style="header"))
        fcx += 38
    out.append(f"""    <text transform="matrix(1, 0, 0, 1, {fcx+4}, {FY+40})">
      <tspan x="-2" y="2" font-family="GillSans" font-size="8" fill="#94A3B8">|</tspan>
    </text>""")
    fcx += 14
    for lbl in fbadges_r:
        out.append(badge(lbl, fcx, FY + 40, style="header"))
        fcx += 38

    # Right-side severity note
    out.append(f"""    <text transform="matrix(1, 0, 0, 1, 760, {FY+28})">
      <tspan x="0" y="0" font-family="GillSans" font-size="7.5" fill="#94A3B8">CRITICAL: AT-02 · AT-03 · IA-02 · SC-23 · PM-16</tspan>
    </text>""")
    out.append(f"""    <text transform="matrix(1, 0, 0, 1, 760, {FY+42})">
      <tspan x="0" y="0" font-family="GillSans" font-size="7.5" fill="#64748B">IMPORTANT: AU-02 · AU-06 · CA-07 · IA-03 · IR-04 · IR-06 · PS-06</tspan>
    </text>""")

    # ── REFERENCES (y=642–704) ─────────────────────────────────────
    RY = 642
    out.append(f"""    <text transform="matrix(1, 0, 0, 1, 30, {RY+10})">
      <tspan x="0" y="2" font-family="GillSans" font-size="7.5" fill="#007EA7">NIST SP 800-218 · C2PA Content Credentials Specification · OWASP AI Security Top 10 · ENISA AI Threat Landscape</tspan>
    </text>""")
    out.append(f"""    <text transform="matrix(1, 0, 0, 1, 30, {RY+23})">
      <tspan x="0" y="2" font-family="GillSans" font-size="7.5" fill="#94A3B8">Coalition for Content Provenance and Authenticity (C2PA) · NIST AI RMF 1.0 · ISO/IEC 42001:2023</tspan>
    </text>""")
    out.append(f"""    <text transform="matrix(1, 0, 0, 1, 30, {RY+38})">
      <tspan x="0" y="2" font-family="GillSans" font-size="8" fill="#007EA7">opensecurityarchitecture.org/patterns/sp-048</tspan>
    </text>""")
    # version tag top-right
    out.append(f"""    <text transform="matrix(1, 0, 0, 1, 900, {RY+10})">
      <tspan x="-45" y="2" font-family="GillSans" font-size="7" fill="#94A3B8">SP-048 v0.1</tspan>
    </text>""")
    out.append(f"""    <text transform="matrix(1, 0, 0, 1, 900, {RY+22})">
      <tspan x="-28" y="2" font-family="GillSans" font-size="7" fill="#94A3B8">2026-02-22</tspan>
    </text>""")

    out.append("  </g>\n</svg>")
    return "\n".join(out)

# ─────────────────────────────────────────────
svg_content = build_svg()
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(svg_content)
print(f"Written: {OUTPUT_PATH}")
print(f"Size: {len(svg_content):,} bytes  Lines: {svg_content.count(chr(10))}")
