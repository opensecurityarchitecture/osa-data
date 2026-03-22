#!/usr/bin/env python3
"""SP-045 AI Governance and Responsible AI - SVG generator."""

OUTPUT = "/Users/tobias.christen/osa-workspace/website/public/images/sp-045-ai-governance.svg"
FONT = "GillSans, 'Gill Sans MT', Calibri, sans-serif"
Q = chr(34)

svg_lines = []
def L(s): svg_lines.append(s)

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

CTRL_TIER = {
    "AU-02": "critical",  "AU-03": "critical",  "CA-07": "critical",
    "CM-02": "critical",  "PM-09": "critical",  "PT-04": "critical",
    "RA-03": "critical",  "RA-08": "critical",  "SA-11": "critical",
    "SI-10": "critical",
    "AC-05": "important", "AC-06": "important", "AT-02": "important",
    "AT-03": "important", "AU-06": "important", "CA-02": "important",
    "CM-03": "important", "CM-04": "important", "PM-14": "important",
    "PM-25": "important", "PM-28": "important", "PM-32": "important",
    "PT-02": "important", "PT-03": "important", "PT-05": "important",
    "RA-07": "important", "RA-09": "important", "SA-03": "important",
    "SA-08": "important", "SA-10": "important", "SI-04": "important",
    "PL-02": "standard",  "PS-06": "standard",
}

# Build badge rect/text attribute strings using Q=chr(34) for safety
def _attr(k, v): return k + Q + v + Q
def _badge_rect(color, opacity, stroke, sopacity):
    return (_attr("fill=", color) + " " + _attr("fill-opacity=", opacity) +
            " " + _attr("stroke=", stroke) + " " + _attr("stroke-opacity=", sopacity) +
            " stroke-width=" + Q + "1" + Q)

BADGE_RECT = {
    "critical":  _badge_rect("#00171F", "0.10", "#003459", "0.6"),
    "important": _badge_rect("#007EA7", "0.12", "#007EA7", "0.4"),
    "standard":  _badge_rect("#F0F0F0", "1",    "#999999", "0.6"),
}
BADGE_TEXT = {
    "critical":  "fill=" + Q + "#003459" + Q,
    "important": "fill=" + Q + "#005F7F" + Q,
    "standard":  "fill=" + Q + "#666666" + Q,
}

def badge(x, y, ctrl_id):
    tier = CTRL_TIER.get(ctrl_id, "standard")
    rs = BADGE_RECT[tier]
    ts = BADGE_TEXT[tier]
    w = max(32, int(len(ctrl_id) * 6.2 + 10))
    h, r = 16, 8
    slug = ctrl_id.lower()
    cx, cy = x + w / 2, y + h / 2
    href = f"/controls/{slug}"
    rect_attrs = f"{rs}"
    text_attrs = f"{ts}"
    return (f'    <a xlink:href="{href}">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" {rect_attrs}/>'
            f'<text x="{cx:.1f}" y="{cy+3.5:.1f}" text-anchor="middle" font-family="{FONT}" font-size="8" {text_attrs}>{ctrl_id}</text></a>')

def badge_row(x, y, ctrl_ids, row_w=290):
    cx = x
    result = []
    for ctrl_id in ctrl_ids:
        w = max(32, int(len(ctrl_id) * 6.2 + 10))
        if cx + w > x + row_w and cx > x: cx = x; y += 20
        result.append(badge(cx, y, ctrl_id))
        cx += w + 4
    return chr(10).join(result), y + 20

def add_col_bg(x, y, w, h, color, opacity=0.06):
    L(f'    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{color}" fill-opacity="{opacity}" stroke="{color}" stroke-opacity="0.2" stroke-width="1"/>')

def add_section_header(x, y, w, color, label):
    L(f'    <rect x="{x}" y="{y}" width="{w}" height="16" rx="3" fill="{color}" fill-opacity="0.35"/>')
    L(f'    <text x="{x+8}" y="{y+11.5}" font-family="{FONT}" font-size="10" font-weight="700" letter-spacing="1.5" fill="white">{esc(label)}</text>')

def add_bullet(x, y, text, color="#334155", size=8.5):
    L(f'    <circle cx="{x+5}" cy="{y-2}" r="2" fill="{color}" opacity="0.5"/>')
    L(f'    <text x="{x+12}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{color}">{esc(text)}</text>')

def add_text(x, y, text, color="#334155", size=8.5, weight="normal", anchor="start"):
    L(f'    <text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')

def add_badges(x, y, ctrl_ids, row_w=290):
    blines, ny = badge_row(x, y, ctrl_ids, row_w)
    L(blines)
    return ny


# === SVG BODY ===
L('<?xml version="1.0" encoding="UTF-8"?>')
L('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"')
L('     viewBox="0 0 960 720" width="960" height="720">')
L('  <!-- SP-045 AI Governance and Responsible AI -->')
L('  <!-- 34 NIST 800-53 Rev 5 controls | ISO/IEC 42001:2023 | EU AI Act | NIST AI RMF -->')
L('  <defs>')
L('    <pattern id="grid" x="0" y="0" width="30" height="30" patternUnits="userSpaceOnUse">')
L('      <circle cx="15" cy="15" r="0.7" fill="#003459" opacity="0.05"/>')
L('    </pattern>')
L('  </defs>')
L('  <rect width="960" height="720" fill="#F8FAFC"/>')
L('  <rect y="62" width="960" height="658" fill="url(#grid)"/>')
L('  <g id="sp-045">')
L('    <rect x="0" y="0" width="960" height="62" fill="#003459"/>')
L(f'    <text x="16" y="34" font-family="{FONT}" font-size="22" font-weight="bold" fill="#FFFFFF">AI GOVERNANCE AND RESPONSIBLE AI</text>')
L(f'    <text x="944" y="22" text-anchor="end" font-family="{FONT}" font-size="8.5" fill="#00A8E8" opacity="0.7">PATTERN SP-045</text>')
L(f'    <text x="944" y="35" text-anchor="end" font-family="{FONT}" font-size="8" fill="white" opacity="0.5">Open Security Architecture</text>')
L('    <rect x="862" y="42" width="82" height="14" rx="7" fill="#007EA7" fill-opacity="0.25" stroke="#007EA7" stroke-width="1"/>')
L(f'    <text x="903" y="52.5" text-anchor="middle" font-family="{FONT}" font-size="8.5" fill="#00A8E8">34 NIST controls</text>')
L('    <rect x="16" y="43" width="52" height="14" rx="7" fill="#00A8E8" fill-opacity="0.25" stroke="#00A8E8" stroke-width="1"/>')
L(f'    <text x="42" y="53.5" text-anchor="middle" font-family="{FONT}" font-size="9" font-weight="700" fill="#00A8E8">SP-045</text>')
L(f'    <text x="76" y="53" font-family="{FONT}" font-size="10" fill="white" opacity="0.75">NIST 800-53 REV5 · ISO/IEC 42001:2023 · EU AI ACT · NIST AI RMF</text>')

# THREE COLUMNS y=70-388
L('    <!-- THREE COLUMNS -->')
COL_Y, COL_H, COL_W = 70, 318, 310
COL_XS = [10, 330, 650]
COL_COLORS = ['#003459', '#007EA7', '#00A8E8']
COL_LABELS = ['AIMS ESTABLISHMENT', 'TRAINING DATA GOVERNANCE', 'MODEL LIFECYCLE MANAGEMENT']
for i in range(3):
    add_col_bg(COL_XS[i], COL_Y, COL_W, COL_H, COL_COLORS[i])
    add_section_header(COL_XS[i]+6, COL_Y+6, COL_W-12, COL_COLORS[i], COL_LABELS[i])

# === COLUMN 1: AIMS ESTABLISHMENT ===
cx1, cy1 = COL_XS[0], COL_Y+32
L(f'    <rect x="{cx1+6}" y="{cy1-11}" width="{COL_W-12}" height="10" rx="2" fill="#003459" fill-opacity="0.12"/>')
L(f'    <text x="{cx1+10}" y="{cy1-3}" font-family="{FONT}" font-size="7.5" font-weight="600" fill="#003459">POLICY & STRATEGY</text>')
cy1 += 4
add_bullet(cx1+8, cy1, 'AI Governance Policy (Board-Approved)', '#003459', 8.5); cy1 += 14
add_bullet(cx1+8, cy1, 'AI Risk Appetite Statement', '#003459', 8.5); cy1 += 14
add_text(cx1+14, cy1, 'Defines tolerance for bias, drift, and autonomy', '#64748B', 7.5); cy1 += 12
add_bullet(cx1+8, cy1, 'Model Inventory & Asset Register', '#003459', 8.5); cy1 += 14

cy1 += 4
L(f'    <rect x="{cx1+6}" y="{cy1-11}" width="{COL_W-12}" height="10" rx="2" fill="#003459" fill-opacity="0.12"/>')
L(f'    <text x="{cx1+10}" y="{cy1-3}" font-family="{FONT}" font-size="7.5" font-weight="600" fill="#003459">EU AI ACT RISK TIERS</text>')
cy1 += 4
L(f'    <rect x="{cx1+8}" y="{cy1-8}" width="8" height="8" rx="2" fill="#DC2626" fill-opacity="0.7"/>')
L(f'    <text x="{cx1+20}" y="{cy1}" font-family="{FONT}" font-size="8" font-weight="600" fill="#DC2626">Unacceptable</text>')
cy1 += 10
L(f'    <text x="{cx1+20}" y="{cy1}" font-family="{FONT}" font-size="7" fill="#64748B">Banned systems (social scoring, biometric mass surveillance)</text>')
cy1 += 13
L(f'    <rect x="{cx1+8}" y="{cy1-8}" width="8" height="8" rx="2" fill="#EA580C" fill-opacity="0.7"/>')
L(f'    <text x="{cx1+20}" y="{cy1}" font-family="{FONT}" font-size="8" font-weight="600" fill="#EA580C">High Risk</text>')
cy1 += 10
L(f'    <text x="{cx1+20}" y="{cy1}" font-family="{FONT}" font-size="7" fill="#64748B">Critical infra, employment, law enforcement, education</text>')
cy1 += 13
L(f'    <rect x="{cx1+8}" y="{cy1-8}" width="8" height="8" rx="2" fill="#D97706" fill-opacity="0.7"/>')
L(f'    <text x="{cx1+20}" y="{cy1}" font-family="{FONT}" font-size="8" font-weight="600" fill="#D97706">Limited Risk</text>')
cy1 += 10
L(f'    <text x="{cx1+20}" y="{cy1}" font-family="{FONT}" font-size="7" fill="#64748B">Chatbots, emotion recognition - transparency obligations</text>')
cy1 += 13
L(f'    <rect x="{cx1+8}" y="{cy1-8}" width="8" height="8" rx="2" fill="#16A34A" fill-opacity="0.7"/>')
L(f'    <text x="{cx1+20}" y="{cy1}" font-family="{FONT}" font-size="8" font-weight="600" fill="#16A34A">Minimal Risk</text>')
cy1 += 10
L(f'    <text x="{cx1+20}" y="{cy1}" font-family="{FONT}" font-size="7" fill="#64748B">Spam filters, AI games - voluntary code of conduct</text>')
cy1 += 13

cy1 += 2
L(f'    <rect x="{cx1+6}" y="{cy1-11}" width="{COL_W-12}" height="10" rx="2" fill="#003459" fill-opacity="0.12"/>')
L(f'    <text x="{cx1+10}" y="{cy1-3}" font-family="{FONT}" font-size="7.5" font-weight="600" fill="#003459">GOVERNANCE ROLES</text>')
cy1 += 4
add_bullet(cx1+8, cy1, 'AI Ethics Lead (chairs AI Ethics Committee)', '#003459', 8); cy1 += 12
add_bullet(cx1+8, cy1, 'Model Risk Owner (accountable per model)', '#003459', 8); cy1 += 12
add_bullet(cx1+8, cy1, 'Data Steward (training data quality & consent)', '#003459', 8); cy1 += 12
add_bullet(cx1+8, cy1, 'AI Auditor (independent review & attestation)', '#003459', 8); cy1 += 12

cy1 += 6
add_badges(cx1+8, cy1, ['PM-09','PM-28','PM-14','PM-32','PL-02'], COL_W-16)
# === COLUMN 2: TRAINING DATA GOVERNANCE ===
cx2, cy2 = COL_XS[1], COL_Y+32

L(f'    <rect x="{cx2+6}" y="{cy2-11}" width="{COL_W-12}" height="10" rx="2" fill="#007EA7" fill-opacity="0.12"/>')
L(f'    <text x="{cx2+10}" y="{cy2-3}" font-family="{FONT}" font-size="7.5" font-weight="600" fill="#007EA7">DATA QUALITY & REPRESENTATION</text>')
cy2 += 4
add_bullet(cx2+8, cy2, 'Representativeness Analysis', '#007EA7', 8.5); cy2 += 14
add_text(cx2+14, cy2, 'Cross-demographic coverage assessment', '#64748B', 7.5); cy2 += 12
add_bullet(cx2+8, cy2, 'Bias Assessment & Quality Metrics', '#007EA7', 8.5); cy2 += 14
add_text(cx2+14, cy2, 'Disparate impact ratio, slicing analysis', '#64748B', 7.5); cy2 += 12
add_bullet(cx2+8, cy2, 'Data Provenance Documentation', '#007EA7', 8.5); cy2 += 14
add_text(cx2+14, cy2, 'Source, license, lineage, collection date', '#64748B', 7.5); cy2 += 12
cy2 += 4
L(f'    <rect x="{cx2+6}" y="{cy2-11}" width="{COL_W-12}" height="10" rx="2" fill="#007EA7" fill-opacity="0.12"/>')
L(f'    <text x="{cx2+10}" y="{cy2-3}" font-family="{FONT}" font-size="7.5" font-weight="600" fill="#007EA7">PRIVACY IN TRAINING DATA</text>')
cy2 += 4
add_bullet(cx2+8, cy2, 'PII Minimization in Training Sets', '#007EA7', 8.5); cy2 += 14
add_text(cx2+14, cy2, 'Anonymize before train; k-anonymity checks', '#64748B', 7.5); cy2 += 12
add_bullet(cx2+8, cy2, 'Consent Basis Documented per Data Source', '#007EA7', 8.5); cy2 += 14
add_text(cx2+14, cy2, 'Legitimate interest / consent / public task', '#64748B', 7.5); cy2 += 12
cy2 += 4
L(f'    <rect x="{cx2+6}" y="{cy2-11}" width="{COL_W-12}" height="10" rx="2" fill="#007EA7" fill-opacity="0.12"/>')
L(f'    <text x="{cx2+10}" y="{cy2-3}" font-family="{FONT}" font-size="7.5" font-weight="600" fill="#007EA7">ANNOTATION & LABELLING</text>')
cy2 += 4
add_bullet(cx2+8, cy2, 'Annotation Standards (Inter-Annotator Agreement)', '#007EA7', 8.5); cy2 += 14
add_text(cx2+14, cy2, 'Cohen kappa > 0.8 target; dispute resolution', '#64748B', 7.5); cy2 += 12
add_bullet(cx2+8, cy2, 'Labeller Diversity & Cultural Competence', '#007EA7', 8.5); cy2 += 14

cy2 += 6
add_badges(cx2+8, cy2, ['SI-10','PT-04','PM-25','PT-02','SA-03'], COL_W-16)
# === COLUMN 3: MODEL LIFECYCLE ===
cx3, cy3 = COL_XS[2], COL_Y+30

flow_stages = ['Develop','Test','Approve','Deploy','Monitor','Retire']
fl_x, fl_y, stg_w, stg_h = cx3+8, cy3+4, 42, 14
for i, stage in enumerate(flow_stages):
    L(f'    <rect x="{fl_x}" y="{fl_y-7}" width="{stg_w}" height="{stg_h}" rx="7" fill="#00A8E8" fill-opacity="0.18" stroke="#00A8E8" stroke-opacity="0.45" stroke-width="1"/>') 
    L(f'    <text x="{fl_x+stg_w/2:.1f}" y="{fl_y+3}" text-anchor="middle" font-family="{FONT}" font-size="7.5" font-weight="600" fill="#003459">{stage}</text>')
    fl_x += stg_w
    if i < len(flow_stages)-1:
        L(f'    <line x1="{fl_x}" y1="{fl_y}" x2="{fl_x+5}" y2="{fl_y}" stroke="#007EA7" stroke-width="1.2"/>')
        L(f'    <path d="M{fl_x+3},{fl_y-3} L{fl_x+6},{fl_y} L{fl_x+3},{fl_y+3} Z" fill="#007EA7"/>')
        fl_x += 7
cy3 = fl_y + 14

L(f'    <rect x="{cx3+6}" y="{cy3-11}" width="{COL_W-12}" height="10" rx="2" fill="#00A8E8" fill-opacity="0.12"/>')
L(f'    <text x="{cx3+10}" y="{cy3-3}" font-family="{FONT}" font-size="7.5" font-weight="600" fill="#007EA7">BIAS & FAIRNESS TESTING</text>')
cy3 += 4
add_bullet(cx3+8, cy3, 'Bias Testing (9 Protected Characteristics)', '#0070A0', 8.5); cy3 += 14
add_text(cx3+14, cy3, 'Age, disability, gender, race, religion, sex...', '#64748B', 7.5); cy3 += 12
add_bullet(cx3+8, cy3, 'Fairness Validation (Dem. Parity, Equal. Odds)', '#0070A0', 8.5); cy3 += 14
add_text(cx3+14, cy3, 'Calibration fairness, counterfactual testing', '#64748B', 7.5); cy3 += 12
add_bullet(cx3+8, cy3, 'Adversarial Robustness Testing', '#0070A0', 8.5); cy3 += 14
add_text(cx3+14, cy3, 'Model inversion, membership inference attacks', '#64748B', 7.5); cy3 += 12
cy3 += 2
L(f'    <rect x="{cx3+6}" y="{cy3-11}" width="{COL_W-12}" height="10" rx="2" fill="#00A8E8" fill-opacity="0.12"/>')
L(f'    <text x="{cx3+10}" y="{cy3-3}" font-family="{FONT}" font-size="7.5" font-weight="600" fill="#007EA7">CONFIGURATION & APPROVAL</text>')
cy3 += 4
add_bullet(cx3+8, cy3, 'Model Baseline & Versioning (CM-02)', '#0070A0', 8.5); cy3 += 14
add_text(cx3+14, cy3, 'Hyperparameters, architecture, training hash', '#64748B', 7.5); cy3 += 12
add_bullet(cx3+8, cy3, 'Approval Gates (Bias+Fairness+Ethics Sign-off)', '#0070A0', 8.5); cy3 += 14
add_text(cx3+14, cy3, 'Ethics committee sign-off before production', '#64748B', 7.5); cy3 += 12

cy3 += 6
add_badges(cx3+8, cy3, ['SA-11','CM-02','SA-08','CM-03','CM-04','SA-10'], COL_W-16)
# TWO-COLUMN BAND y=395-562
L('    <!-- TWO-COLUMN BAND -->')
BAND_Y, BAND_H, HALF_W = 395, 165, 470
add_col_bg(10, BAND_Y, HALF_W, BAND_H, '#003459')
add_section_header(16, BAND_Y+6, HALF_W-12, '#003459', 'TRANSPARENCY & EXPLAINABILITY')
add_col_bg(490, BAND_Y, HALF_W, BAND_H, '#007EA7')
add_section_header(496, BAND_Y+6, HALF_W-12, '#007EA7', 'AI RISK & IMPACT ASSESSMENT')
L('    <line x1="483" y1="400" x2="483" y2="558" stroke="#007EA7" stroke-opacity="0.15" stroke-width="1"/>')
lx, ly = 16, BAND_Y+30
L(f'    <rect x="{lx+4}" y="{ly-11}" width="{HALF_W-16}" height="10" rx="2" fill="#003459" fill-opacity="0.10"/>')
L(f'    <text x="{lx+8}" y="{ly-3}" font-family="{FONT}" font-size="7.5" font-weight="600" fill="#003459">DECISION TRANSPARENCY</text>')
ly += 4
add_bullet(lx+4, ly, 'AI Decision Transparency Obligations', '#003459', 8.5); ly += 14
add_text(lx+10, ly, 'Art.22 GDPR: right to explanation for automated decisions', '#64748B', 7.5); ly += 12
add_bullet(lx+4, ly, 'Affected Person Notification (GDPR Art.22)', '#003459', 8.5); ly += 14
add_bullet(lx+4, ly, 'Decision-Level Audit Trails', '#003459', 8.5); ly += 14
add_text(lx+10, ly, 'Input features, model version, timestamp, output', '#64748B', 7.5); ly += 12
ly += 4
L(f'    <rect x="{lx+4}" y="{ly-11}" width="{HALF_W-16}" height="10" rx="2" fill="#003459" fill-opacity="0.10"/>')
L(f'    <text x="{lx+8}" y="{ly-3}" font-family="{FONT}" font-size="7.5" font-weight="600" fill="#003459">EXPLAINABILITY METHODS</text>')
ly += 4
add_bullet(lx+4, ly, 'SHAP (Shapley Additive Explanations)', '#003459', 8.5); ly += 12
add_bullet(lx+4, ly, 'LIME (Local Interpretable Model Explanations)', '#003459', 8.5); ly += 12
add_bullet(lx+4, ly, 'Attention Mechanisms for NLP/Vision models', '#003459', 8.5); ly += 12
add_bullet(lx+4, ly, 'Counterfactual explanations for denials', '#003459', 8.5); ly += 12
ly += 4
add_badges(lx+4, ly, ['AU-02','AU-03','PT-05','PT-03'], HALF_W-20)
rx_, ry = 496, BAND_Y+30
L(f'    <rect x="{rx_+4}" y="{ry-11}" width="{HALF_W-16}" height="10" rx="2" fill="#007EA7" fill-opacity="0.12"/>')
L(f'    <text x="{rx_+8}" y="{ry-3}" font-family="{FONT}" font-size="7.5" font-weight="600" fill="#007EA7">AI-SPECIFIC RISK CATEGORIES</text>')
ry += 4
add_bullet(rx_+4, ry, 'Bias & Fairness Risk (disparate outcomes)', '#007EA7', 8.5); ry += 12
add_bullet(rx_+4, ry, 'Hallucination / Confabulation Risk', '#007EA7', 8.5); ry += 12
add_bullet(rx_+4, ry, 'Environmental / Carbon Footprint Risk', '#007EA7', 8.5); ry += 12
add_bullet(rx_+4, ry, 'Autonomy Creep / Human Oversight Erosion', '#007EA7', 8.5); ry += 12

ry += 4
L(f'    <rect x="{rx_+4}" y="{ry-11}" width="{HALF_W-16}" height="10" rx="2" fill="#007EA7" fill-opacity="0.12"/>')
L(f'    <text x="{rx_+8}" y="{ry-3}" font-family="{FONT}" font-size="7.5" font-weight="600" fill="#007EA7">IMPACT ASSESSMENTS</text>')
ry += 4
add_bullet(rx_+4, ry, 'AI Impact Assessment (Fundamental Rights)', '#007EA7', 8.5); ry += 12
add_text(rx_+10, ry, 'Mandatory for EU AI Act High Risk systems', '#64748B', 7.5); ry += 12
add_bullet(rx_+4, ry, 'EU AI Act Conformity Assessment', '#007EA7', 8.5); ry += 12
add_text(rx_+10, ry, 'Third-party audit or self-assessment per tier', '#64748B', 7.5); ry += 12
add_bullet(rx_+4, ry, 'Criticality Tiers for Autonomous Systems', '#007EA7', 8.5); ry += 12
ry += 4
add_badges(rx_+4, ry, ['RA-03','RA-08','RA-07','RA-09'], HALF_W-20)
# FOUR-PANEL BOTTOM BAND y=567-650
L('    <!-- FOUR-PANEL BOTTOM BAND -->')
BOT_Y, BOT_H, PANEL_W, PANEL_G = 567, 84, 232, 8
PANEL_COLORS = ['#003459','#007EA7','#00A8E8','#003459']
PANEL_LABELS = ['HUMAN OVERSIGHT','AI LITERACY','CONCEPT DRIFT DETECTION','AIMS REVIEW']
PANEL_ITEMS = [
    [('bold','Autonomy Spectrum:'),('item','Automated / HotL / HitL / HiC'),('item','Competence + Authority + Time'),('item','Documented escalation protocol')],
    [('item','Role-Based AI Training'),('item','Recognise Hallucinations'),('item','Know When to Override'),('item','AI Ethics & Liability Awareness')],
    [('item','Fairness Metrics Dashboard'),('item','Population Stability Index (PSI)'),('item','Anomalous Pattern Escalation'),('item','Feature Drift Monitoring (KL-Div)')],
    [('item','Quarterly Governance Review'),('item','Regulatory Landscape Update'),('item','Monitoring Threshold Calibration'),('item','Annual AIMS Maturity Assessment')],
]
PANEL_BADGES = [['AC-05','AC-06'],['AT-02','AT-03','PS-06'],['CA-07','SI-04'],['CA-02','AU-06']]
for i in range(4):
    px = 10 + i*(PANEL_W+PANEL_G)
    pc = PANEL_COLORS[i]
    add_col_bg(px, BOT_Y, PANEL_W, BOT_H, pc, opacity=0.08)
    add_section_header(px+4, BOT_Y+4, PANEL_W-8, pc, PANEL_LABELS[i])
    iy = BOT_Y+28
    for kind, text in PANEL_ITEMS[i]:
        if kind=='bold': add_text(px+10, iy, text, pc, 8, weight='700')
        else: add_bullet(px+8, iy, text, '#334155', 7.5)
        iy += 12
    iy += 2
    add_badges(px+6, iy, PANEL_BADGES[i], PANEL_W-12)
for i in range(1, 4):
    dx = 10 + i*(PANEL_W+PANEL_G) - PANEL_G
    L(f'    <line x1="{dx+PANEL_G//2}" y1="{BOT_Y+4}" x2="{dx+PANEL_G//2}" y2="{BOT_Y+BOT_H-4}" stroke="#007EA7" stroke-opacity="0.1" stroke-width="1"/>')
# LEGEND & FRAMEWORK ALIGNMENT
L('    <!-- LEGEND & FRAMEWORK ALIGNMENT -->')
LEGEND_Y = 656
L(f'    <rect x="10" y="{LEGEND_Y-1}" width="940" height="14" rx="3" fill="#003459" fill-opacity="0.05"/>')
L(f'    <rect x="16" y="{LEGEND_Y}" width="41" height="12" rx="6" fill="#00171F" fill-opacity="0.10" stroke="#003459" stroke-opacity="0.6" stroke-width="1"/>')
L(f'    <text x="{16+20.5}" y="{LEGEND_Y+8.5}" text-anchor="middle" font-family="{FONT}" font-size="7" fill="#003459">XX-00</text>')
L(f'    <text x="62" y="{LEGEND_Y+8.5}" font-family="{FONT}" font-size="7" fill="#64748B">Critical</text>')
L(f'    <rect x="98" y="{LEGEND_Y}" width="41" height="12" rx="6" fill="#007EA7" fill-opacity="0.12" stroke="#007EA7" stroke-opacity="0.4" stroke-width="1"/>')
L(f'    <text x="{98+20.5}" y="{LEGEND_Y+8.5}" text-anchor="middle" font-family="{FONT}" font-size="7" fill="#005F7F">XX-00</text>')
L(f'    <text x="144" y="{LEGEND_Y+8.5}" font-family="{FONT}" font-size="7" fill="#64748B">Important</text>')
L(f'    <rect x="186" y="{LEGEND_Y}" width="41" height="12" rx="6" fill="#F0F0F0" stroke="#999" stroke-opacity="0.6" stroke-width="1"/>')
L(f'    <text x="{186+20.5}" y="{LEGEND_Y+8.5}" text-anchor="middle" font-family="{FONT}" font-size="7" fill="#666">XX-00</text>')
L(f'    <text x="232" y="{LEGEND_Y+8.5}" font-family="{FONT}" font-size="7" fill="#64748B">Standard  (click badge to view control)</text>')
L(f'    <text x="944" y="{LEGEND_Y+9}" text-anchor="end" font-family="{FONT}" font-size="7" fill="#64748B">Framework alignment: ISO/IEC 42001 · EU AI Act · NIST AI RMF · IEEE 7000 · OECD AI Principles</text>')
# FOOTER y=672-720
L('    <!-- FOOTER -->')
FOOT_Y = 672
L(f'    <rect x="0" y="{FOOT_Y}" width="960" height="48" fill="#00171F"/>')
L(f'    <text x="16" y="{FOOT_Y+14}" font-family="{FONT}" font-size="8.5" font-weight="700" fill="white">Related Patterns:</text>')
L(f'    <text x="16" y="{FOOT_Y+27}" font-family="{FONT}" font-size="8.5" fill="#00A8E8">SP-027 Secure LLM Usage  ·  SP-047 Secure Agentic AI Frameworks  ·  SP-042 Third Party Risk Management</text>')
L(f'    <text x="944" y="{FOOT_Y+14}" text-anchor="end" font-family="{FONT}" font-size="8" fill="#94A3B8">ISO/IEC 42001:2023  ·  EU AI Act  ·  NIST AI RMF AI-100-1  ·  OECD AI Principles</text>')
L(f'    <text x="16" y="{FOOT_Y+40}" font-family="{FONT}" font-size="7.5" fill="#64748B">SP-045  ·  AI Governance and Responsible AI  ·  34 NIST 800-53 Rev 5 controls  ·  Authors: Aurelius, Vitruvius  ·  Draft  ·  2026-02-24</text>')
L(f'    <text x="944" y="{FOOT_Y+40}" text-anchor="end" font-family="{FONT}" font-size="7.5" fill="#475569">opensecurityarchitecture.org/patterns/sp-045</text>')
# CONTROL FAMILY SUMMARY BAND y=653-672
L('    <!-- CONTROL FAMILY BAND -->')
CFAM_Y = 655
# Background
L(f'    <rect x="10" y="{CFAM_Y}" width="940" height="14" rx="3" fill="#003459" fill-opacity="0.06"/>')

# Show control families compactly
families = [
    ('AC','Access Control','2'),('AT','Awareness & Training','2'),('AU','Audit & Account.','3'),
    ('CA','Assessment','2'),('CM','Config Mgmt','3'),('PL','Planning','1'),
    ('PM','Program Mgmt','5'),('PS','Personnel Sec.','1'),('PT','PII Processing','4'),
    ('RA','Risk Assessment','4'),('SA','System Acq.','5'),('SI','System Integrity','2'),
]
fam_x = 14
fam_step = 940 // len(families)
for fam_id, fam_name, fam_count in families:
    L(f'    <text x="{fam_x}" y="{CFAM_Y+6}" font-family="{FONT}" font-size="6.5" font-weight="700" fill="#007EA7">{fam_id}</text>')
    L(f'    <text x="{fam_x+14}" y="{CFAM_Y+6}" font-family="{FONT}" font-size="6" fill="#64748B">{fam_name}</text>')
    L(f'    <text x="{fam_x+14}" y="{CFAM_Y+13}" font-family="{FONT}" font-size="6.5" fill="#003459" font-weight="600">{fam_count} ctrl</text>')
    fam_x += fam_step


# ADDITIONAL CONTENT: Column sub-labels and decorative elements

# Add vertical section dividers in each column
for col_x in COL_XS:
    L(f'    <line x1="{col_x+6}" y1="{COL_Y+24}" x2="{col_x+COL_W-6}" y2="{COL_Y+24}" stroke="{COL_COLORS[COL_XS.index(col_x)]}" stroke-opacity="0.2" stroke-width="0.5"/>')

# Add bottom border to three-column section
L(f'    <line x1="10" y1="{COL_Y+COL_H}" x2="960" y2="{COL_Y+COL_H}" stroke="#007EA7" stroke-opacity="0.1" stroke-width="1"/>')

# Add bottom border to two-column section
L(f'    <line x1="10" y1="{BAND_Y+BAND_H}" x2="950" y2="{BAND_Y+BAND_H}" stroke="#007EA7" stroke-opacity="0.1" stroke-width="1"/>')

# Watermark / branding text (subtle)
L(f'    <text x="480" y="387" text-anchor="middle" font-family="{FONT}" font-size="7" fill="#003459" opacity="0.08" font-weight="700">OPEN SECURITY ARCHITECTURE</text>')

# Add ISO 42001 and NIST RMF cross-reference annotations in header area
L(f'    <text x="480" y="57" text-anchor="middle" font-family="{FONT}" font-size="7" fill="white" opacity="0.35">AI Governance Framework · Responsible AI · Model Risk Management · Ethics & Compliance</text>')

# Add a compact annotation showing AI risk management cycle (at col3 bottom area)
# Already have lifecycle flow at top of col3
# Add annotation for the 5 NIST AI RMF functions
rmf_x = COL_XS[2] + 8
rmf_y = COL_Y + COL_H - 24
rmf_fns = ['GOVERN','MAP','MEASURE','MANAGE']
rmf_w = (COL_W - 16) // len(rmf_fns)
for j, fn in enumerate(rmf_fns):
    fx = rmf_x + j * rmf_w
    L(f'    <rect x="{fx}" y="{rmf_y-10}" width="{rmf_w-2}" height="20" rx="3" fill="#00A8E8" fill-opacity="0.08" stroke="#00A8E8" stroke-opacity="0.2" stroke-width="0.5"/>')
    L(f'    <text x="{fx + (rmf_w-2)/2:.1f}" y="{rmf_y+4}" text-anchor="middle" font-family="{FONT}" font-size="7" font-weight="600" fill="#007EA7">NIST RMF</text>')
    L(f'    <text x="{fx + (rmf_w-2)/2:.1f}" y="{rmf_y+12}" text-anchor="middle" font-family="{FONT}" font-size="6.5" fill="#003459">{fn}</text>')

# Add tooltip-style annotations for key concepts
# Privacy notice annotation in col2
L(f'    <rect x="{COL_XS[1]+8}" y="{COL_Y+COL_H-38}" width="{COL_W-16}" height="28" rx="3" fill="#007EA7" fill-opacity="0.05" stroke="#007EA7" stroke-opacity="0.15" stroke-width="0.5"/>')
L(f'    <text x="{COL_XS[1]+14}" y="{COL_Y+COL_H-26}" font-family="{FONT}" font-size="7" font-weight="600" fill="#007EA7">Data Sheet Requirements (ISO 42001 A.7.2)</text>')
L(f'    <text x="{COL_XS[1]+14}" y="{COL_Y+COL_H-15}" font-family="{FONT}" font-size="6.5" fill="#64748B">Purpose · Sources · Preprocessing · Known Limitations · Recommended Uses</text>')

# Add annotation for col1 governance maturity
L(f'    <rect x="{COL_XS[0]+8}" y="{COL_Y+COL_H-38}" width="{COL_W-16}" height="28" rx="3" fill="#003459" fill-opacity="0.05" stroke="#003459" stroke-opacity="0.15" stroke-width="0.5"/>')
L(f'    <text x="{COL_XS[0]+14}" y="{COL_Y+COL_H-26}" font-family="{FONT}" font-size="7" font-weight="600" fill="#003459">AIMS Maturity Levels (ISO 42001)</text>')
L(f'    <text x="{COL_XS[0]+14}" y="{COL_Y+COL_H-15}" font-family="{FONT}" font-size="6.5" fill="#64748B">Ad-hoc · Managed · Defined · Quantitative · Optimising</text>')

# Key risk indicators annotation in two-col right section
L(f'    <text x="{rx_+4}" y="{BAND_Y+BAND_H-10}" font-family="{FONT}" font-size="7" fill="#64748B" opacity="0.7">KPIs: False Positive Rate · Demographic Parity Difference · Equal Opportunity Difference · Model Drift Index</text>')


L('  </g>')
L('</svg>')




# Post-process: fix any unescaped & in text elements
import re

def fix_amp_in_text(svg_text):
    # Replace & in XML text content (between > and <) that are not already &amp;
    result = []
    i = 0
    while i < len(svg_text):
        if svg_text[i] == '&':
            # Check context: are we in a text node (not an attribute, not already escaped)?
            # Simple heuristic: replace & not followed by amp; lt; gt; # apos; quot;
            rest = svg_text[i:]
            if not any(rest.startswith(e) for e in ['&amp;','&lt;','&gt;','&#','&quot;','&apos;']):
                result.append('&amp;')
            else:
                result.append('&')
        elif svg_text[i:i+4] == '<!--':
            # Skip comment content - replace & with &amp; inside comments too
            end = svg_text.find('-->', i)
            if end == -1:
                result.append(svg_text[i:])
                break
            comment = svg_text[i:end+3].replace('&', '&amp;').replace('&amp;amp;', '&amp;')
            result.append(comment)
            i = end + 3
            continue
        else:
            result.append(svg_text[i])
        i += 1
    return ''.join(result)


sep = chr(10)
svg = fix_amp_in_text(sep.join(svg_lines))
with open(OUTPUT, 'w', encoding='utf-8') as f: f.write(svg)
print(f'Written : {OUTPUT}')
print(f'Lines   : {len(svg_lines)}')
print(f'Bytes   : {len(svg.encode()):,}')