# OSA Modernisation Roadmap

## Executive Summary

OSA is uniquely positioned in the security architecture space. Unlike SABSA (strategic/business-focused) or O-ESA (policy-driven), **OSA provides operational, ready-to-use patterns** with control mappings. This is referenced in O'Reilly publications and has no direct open-source competitor.

**Current state:** 27 patterns, 171 NIST 800-53 Rev 4 controls with ISO 17799/COBIT 4.1/PCI-DSS v2 mappings. ~1,700 daily visitors despite minimal maintenance.

**Key opportunity:** The structured data we've extracted is the foundation for API-driven, AI-enhanced security architecture tooling.

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

### 3.1 Pattern Recommendation Engine

Given a system description or architecture diagram, recommend applicable patterns.

**Example:**
```
Input: "Cloud-hosted healthcare application with patient data"
Output:
  - SP-011 Cloud Computing (54 controls)
  - SP-013 Data Security (33 controls)
  - Relevant HIPAA control overlay
```

### 3.2 Control Selection Assistant

"I'm building a cloud-hosted healthcare application" -> Relevant controls from multiple frameworks with justification.

### 3.3 Threat Modelling Integration

Link patterns to threat models. Given a pattern, enumerate threats and mitigations.

### 3.4 Compliance Gap Analysis

"Show me gaps between my current controls and PCI-DSS v4.0 requirements"

---

## Phase 4: Platform Evolution

### 4.1 Decision: Joomla Refresh vs Replatform

**Keep Joomla if:**
- Weekend maintenance cadence is acceptable
- No need for complex user interactions
- Content is primary value (not features)

**Replatform if:**
- Want modern developer experience
- Need user accounts/submissions
- Want to integrate AI features deeply

**Replatform options:**
- Headless CMS (Strapi, Directus) + Next.js/Astro frontend
- Static site generator (Hugo, Astro) from JSON data
- Full custom (overkill for content site)

### 4.2 Community Features

- Pattern submission workflow
- Discussion/comments on patterns
- Usage analytics (which patterns are most viewed)

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

## Remaining Questions

1. **AI features:** Build into site, or separate tool/CLI that consumes the API?
2. **Monetisation:** Keep fully free, or freemium model for AI features?
3. **Community governance:** Open to external contributors, or maintain control?

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
| `data/controls/*.json` | 171 extracted controls |
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

*Last updated: 2026-01-23*
