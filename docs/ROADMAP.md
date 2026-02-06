# OSA Modernisation Roadmap

## Executive Summary

OSA is uniquely positioned in the security architecture space. Unlike SABSA (strategic/business-focused) or O-ESA (policy-driven), **OSA provides operational, ready-to-use patterns** with control mappings. This is referenced in O'Reilly publications and has no direct open-source competitor.

**Current state:** Live at opensecurityarchitecture.org on Astro/Cloudflare Pages. 27 patterns, 191 NIST 800-53 Rev 5 controls mapped to 7 compliance frameworks (ISO 27001:2022, ISO 27002:2022, COBIT 2019, CIS Controls v8, NIST CSF 2.0, SOC 2 TSC, PCI DSS v4.0.1). ~1,700 daily visitors.

**Key opportunity:** OSA's structured control-to-framework graph is unique in the market. No other open-source project provides this cross-framework mapping. This is the foundation for AI-powered security architecture tooling that connects threats directly to auditable controls.

---

## Strategic Options

### Option A: Content Refresh (Low effort, foundation building)
Focus on updating existing content to current standards before building new capabilities.

### Option B: API-First (Medium effort, developer-focused)
Build API layer to make patterns/controls programmatically accessible. Enables tooling integration.

### Option C: AI-Enhanced (Higher effort, differentiation play)
Claude-powered pattern recommendation, threat modelling assistance, control selection.

**Recommendation:** Phased approach - A -> B -> C

---

## Phase 1: Content Modernisation

### 1.1 NIST 800-53 Rev 5 Update (Priority: High)

OSA currently uses Rev 4 (withdrawn Sept 2021). Rev 5 changes:
- **66 new base controls**, 202 new enhancements
- **2 new control families:** PT (Privacy), SR (Supply Chain Risk Management)
- Outcome-based language (compliance -> performance)
- Privacy integrated throughout

**Action:** Use [NIST's Rev 4 to Rev 5 comparison workbook](https://csrc.nist.gov/files/pubs/sp/800/53/r5/upd1/final/docs/sp800-53r4-to-r5-comparison-workbook.xlsx) to update control catalogue.

**Data structure ready:** `control.schema.json` includes `nist_800_53.rev5` fields for:
- Updated control names/descriptions
- New controls marked with `new_in_rev5: true`
- Withdrawn controls with `incorporated_into` references
- Privacy baseline indicator

### 1.2 Compliance Mapping Updates (Priority: High)

Current mappings are outdated:

| Current | Update To |
|---------|-----------|
| ISO 17799 | ISO 27001:2022 / ISO 27002:2022 |
| COBIT 4.1 | COBIT 2019 |
| PCI-DSS v2 | PCI-DSS v4.0 |

**Add new mappings:**
- NIST Cybersecurity Framework 2.0
- CIS Controls v8
- SOC 2 Trust Services Criteria

**Data structure ready:** `control.schema.json` includes `compliance_mappings` object with fields for all target frameworks.

### 1.3 Pattern Content Refresh (Priority: Medium)

Some patterns are dated (e.g., SP-024 iPhone Pattern from ~2010). Options:
- Archive clearly outdated patterns
- Update patterns that are still relevant with current tech context
- Mark patterns with "last reviewed" dates

### 1.4 Complete Reserved Patterns (Priority: Low)

- SP-012: Secure SDLC Pattern (reserved)
- SP-015: Consumer Devices Pattern (reserved)
- SP-017: Secure Network Zone Module (reserved)

---

## Phase 2: Technical Infrastructure

### 2.1 API Layer (Priority: High)

Expose patterns and controls via REST API:

```
GET /api/v1/patterns
GET /api/v1/patterns/{id}
GET /api/v1/patterns/{id}/controls
GET /api/v1/controls
GET /api/v1/controls/{id}
GET /api/v1/controls?framework=nist-csf-2.0
GET /api/v1/mappings?from=nist-800-53&to=iso-27001
```

**Implementation options:**

| Option | Pros | Cons |
|--------|------|------|
| Static JSON + GitHub Pages | Zero cost, simple, cacheable | No dynamic queries |
| Cloudflare Workers | Low cost, serverless, edge-deployed | Cloudflare lock-in |
| Dedicated API service | Full control, complex queries | Higher cost, maintenance |

**Recommendation:** Start with static JSON on GitHub Pages, add Cloudflare Workers for dynamic queries if needed.

### 2.2 Data Quality & Validation

- JSON Schema validation for all data (schemas in `data/schema/`)
- Automated extraction re-runs to catch site updates
- Version tracking for control/pattern changes
- CI/CD pipeline for validation on PR

### 2.3 Documentation

- API documentation (OpenAPI/Swagger)
- Pattern authoring guide
- Contribution guidelines (if opening to community)

---

## Phase 3: AI Integration

### Business Model: Two-Layer Architecture

OSA operates as two complementary layers:

**Layer 1 - Open Source (free, forever)**
- All patterns, controls, compliance mappings, icon library
- JSON data, schemas, and static API
- Self-hostable, forkable, community-owned
- CC BY-SA 4.0 licence unchanged

**Layer 2 - AI Platform (SaaS, tiered)**
- Authenticated access via OAuth (GitHub, Google)
- AI-powered threat modelling, control selection, gap analysis
- Tiered: Personal (free, rate-limited) -> Team -> Enterprise
- The AI layer consumes Layer 1 data but adds intelligence on top

This model preserves OSA's 17-year open-source ethos while creating a sustainable revenue path. The open layer builds trust and community; the AI layer monetises the unique value.

### 3.1 Controls-Aware Threat Modelling (Key Differentiator)

Existing tools (STRIDE-GPT, Microsoft Threat Modeling Tool) produce generic threats with generic mitigations. OSA can close the full chain:

```
System description / codebase
  -> STRIDE threat analysis
    -> Threats mapped to specific NIST 800-53 controls
      -> Controls cross-referenced to ISO 27001, PCI DSS, SOC 2, etc.
        -> Auditor-ready evidence requirements
```

**Why this matters:** A CISO doesn't just need "implement input validation." They need "SI-10 (Information Input Validation), which maps to PCI DSS 6.5.1 and ISO 27002 8.28, and here's what your auditor will ask for."

No other tool does this. OSA's structured control-to-framework graph is the moat.

### 3.2 Pattern Recommendation Engine

Given a system description or architecture diagram, recommend applicable patterns.

```
Input: "Cloud-hosted healthcare application with patient data"
Output:
  - SP-011 Cloud Computing (54 controls)
  - SP-013 Data Security (33 controls)
  - Relevant HIPAA control overlay
  - Threat model with controls mapped to compliance frameworks
```

### 3.3 Control Selection Assistant

Conversational control selection: "I'm building a cloud-hosted payments platform" -> relevant controls from multiple frameworks with justification, gap analysis against current posture, and prioritised implementation roadmap.

### 3.4 Compliance Gap Analysis

"Show me gaps between my current controls and PCI-DSS v4.0.1 requirements" -> specific missing controls, remediation guidance, and effort estimates.

### 3.5 MCP Server / API Integration

Expose OSA AI capabilities as an MCP server so they compose with other tools (GitHub, Terraform, CI/CD). This is the composability play - but with OSA's structured data underneath rather than generic LLM output.

---

## Phase 4: Platform Evolution

### 4.1 Replatform (DONE)

Migrated from Joomla to Astro + Tailwind CSS on Cloudflare Pages (Feb 2026). Static site generated from structured JSON data. Modern, fast, mobile-responsive.

### 4.2 Authentication & User Accounts

Required for AI layer (Phase 3). OAuth via GitHub/Google. Supports tiered access model:
- Anonymous: full access to open-source content (Layer 1)
- Authenticated Personal: AI features with rate limits
- Team/Enterprise: higher limits, custom integrations, audit reporting

### 4.3 Community Features

- Pattern submission workflow
- Discussion/comments on patterns
- Usage analytics (which patterns are most viewed)
- Community-contributed compliance mappings

---

## Quick Wins

| Task | Status | Notes |
|------|--------|-------|
| Create GitHub repo | Done | Local, ready to push |
| Create opensecurityarchitecture GitHub org | Pending | Next step |
| README.md | Done | Project documentation |
| LICENSE | Done | CC BY-SA 4.0 |
| JSON schemas | Done | pattern.schema.json, control.schema.json |
| Sitemap.xml | Pending | Generate and add to site |
| Legacy redirects | Pending | /BB3/, /cms/, /jcms/ -> proper pages |

---

## Success Metrics

| Metric | Current | 6-Month Target |
|--------|---------|----------------|
| Daily unique visitors | ~1,700 | 3,000 |
| GitHub stars | 0 | 100 |
| API calls/month | 0 | 10,000 |
| Patterns with current mappings | 0 | 27 |
| Control framework versions | Rev 4 | Rev 5 |

---

## Resource Requirements

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| 1.1 NIST Update | 2-3 weekends | NIST comparison workbook |
| 1.2 Mapping Updates | 3-4 weekends | Framework crosswalks |
| 2.1 API Layer | 1-2 weekends | Hosting decision |
| 3.x AI Features | Ongoing | API foundation |

---

## Decisions Made

1. **GitHub org:** Create new `opensecurityarchitecture` GitHub organisation
2. **Priority:** Content first - update NIST Rev 5 and compliance mappings before API
3. **Old team:** Reach out to Tobias, Spinoza, Phaedrus once foundation is solid
4. **License:** CC BY-SA 4.0 (matches existing site terms)

## Decisions Made (Phase 3+)

1. **Two-layer model:** Open source data layer (free forever) + AI SaaS layer (tiered)
2. **Monetisation:** Freemium - AI features tiered from personal to enterprise
3. **Threat modelling:** Controls-aware approach (OSA's differentiator vs generic STRIDE tools)
4. **Replatform:** Astro + Cloudflare Pages (done)

## Open Questions

1. **Community governance:** Open to external contributors, or maintain control?
2. **AI infrastructure:** Cloudflare Workers AI, or dedicated API service?
3. **Enterprise features:** What do enterprise buyers need beyond higher rate limits?

---

## Files Reference

### Created/Updated

| File | Purpose |
|------|---------|
| `README.md` | Project overview and documentation |
| `LICENSE` | CC BY-SA 4.0 license |
| `data/schema/pattern.schema.json` | JSON schema for patterns |
| `data/schema/control.schema.json` | JSON schema for controls with Rev 5 fields |
| `data/patterns/*.json` | 27 extracted patterns |
| `data/controls/*.json` | 191 NIST 800-53 Rev 5 controls |
| `docs/DISCOVERY.md` | Phase 0 findings |
| `docs/ROADMAP.md` | This file |

### Future

| File | Purpose |
|------|---------|
| `api/` | API implementation |
| `docs/api.md` | API documentation |
| `.github/workflows/` | CI/CD for data validation |

---

## Verification Checklist

- [ ] JSON schema validation passes for all patterns
- [ ] JSON schema validation passes for all controls
- [ ] All patterns have required fields
- [ ] Control mappings spot-checked against official sources
- [ ] README accurately describes data structure
- [ ] LICENSE matches OSA site terms

---

*Last updated: 2026-02-06*
