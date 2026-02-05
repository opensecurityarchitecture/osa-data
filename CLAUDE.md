# CLAUDE.md - Open Security Architecture Workspace

This workspace is for the modernisation of opensecurityarchitecture.org (OSA).

## Project Context

**OSA** has been running since ~2008, developed actively for 4-5 years, then dormant. Despite minimal maintenance, it continues to receive traffic (~1,700 daily visitors). Pattern content was published in O'Reilly (Cloud Pattern).

**Current platform**: Modern Astro site with Tailwind CSS, deployed via Cloudflare Pages from GitHub. Cut over from legacy Joomla on 2026-02-05.

**Goal**: Modernise OSA as a weekend side project, with realistic targets to grow traffic and value.

## GitHub Repositories

**osa-data**: https://github.com/opensecurityarchitecture/osa-data
- Structured JSON data for patterns and controls with compliance mappings

**osa-website**: https://github.com/opensecurityarchitecture/osa-website
- Astro site source, deployed to Cloudflare Pages
- Live at: https://www.opensecurityarchitecture.org

## Founder Context

**Russ** — OSA founder.

- 20+ years in technology for financial services
- Security specialist background
- Hands-on coder, deeply technical
- Values: direct communication, quality over speed, long-term thinking

**Communication style:** Direct, technical, no fluff.

## Role Definition

**Claude** — Technical partner for OSA modernisation.

Working pattern: Weekend sessions, incremental progress, realistic scope.

## Vision

Transform OSA from a static Joomla site into a modern, AI-powered security architecture resource:

1. **Structured pattern library** - Extract patterns to structured data (JSON/YAML)
2. **API-driven** - Patterns accessible via API for tooling integration
3. **AI-powered** - Claude integration for pattern recommendation, threat modelling assistance
4. **NIST/compliance mapping** - Link patterns to control frameworks
5. **Modern UX** - Whether Joomla refresh or full replatform TBD

## Phased Approach

| Phase | Focus | Status |
|-------|-------|--------|
| 0 | Discovery - traffic analysis, content audit, security posture | Complete |
| 1 | Data extraction - patterns to structured format | Complete |
| 1.5 | Content modernisation - NIST Rev 5, compliance mappings | Complete |
| 1.6 | Website replatform - Astro/Tailwind, Cloudflare Pages | **Complete** |
| 2 | API layer - expose patterns via API | Not started |
| 3 | AI integration - Claude-powered features | Not started |

## Current Data

| Asset | Count | Status |
|-------|-------|--------|
| Security patterns | 27 | Extracted to JSON |
| NIST 800-53 controls | 191 | Rev 5 updated |
| ISO 27001:2022 mappings | 701 | Complete |
| ISO 27002:2022 mappings | 411 | Complete |
| COBIT 2019 mappings | 633 | Complete |
| CIS Controls v8 mappings | 373 | Complete |
| NIST CSF 2.0 mappings | 692 | Complete |
| SOC 2 TSC mappings | 1,397 | Complete |

## Workspace Structure

```
osa-workspace/
├── CLAUDE.md                    # This file
├── README.md                    # Project documentation
├── LICENSE                      # CC BY-SA 4.0
├── data/
│   ├── patterns/                # 27 security patterns (JSON)
│   │   └── _manifest.json
│   ├── controls/                # 191 NIST 800-53 controls (JSON)
│   │   ├── _manifest.json
│   │   └── _catalog.json
│   └── schema/
│       ├── pattern.schema.json
│       └── control.schema.json
├── docs/
│   ├── DISCOVERY.md             # Phase 0 findings
│   └── ROADMAP.md               # Detailed roadmap
├── scripts/
│   ├── extract_patterns.py
│   ├── extract_controls_db.py
│   ├── update_controls_schema.py
│   ├── update_rev5_data.py
│   ├── add_rev5_families.py
│   ├── extract_compliance_mappings.py
│   └── validate_json.py
└── .github/
    └── workflows/
        └── validate.yml         # CI validation
```

## Commands

```bash
# Open workspace
cd /Users/russellwing/osa-workspace

# Validate all JSON
python3 scripts/validate_json.py

# Push to GitHub
git push origin main
```

## Session Log

### 2026-01-23 - Project Kickoff
- Discussed modernisation potential with Russ
- Agreed weekend side hustle approach
- Created this workspace
- Completed Phase 0 discovery (traffic, content audit)
- Extracted 27 patterns and 171 controls to JSON

### 2026-01-23 - Content Modernisation (Evening Session)
- Created GitHub org: opensecurityarchitecture
- Created repo: osa-data
- Updated all controls to NIST 800-53 Rev 5
  - Added Rev 5 baselines and change details
  - 95 controls with significant changes identified
- Added new Rev 5 control families
  - PT (Privacy): 8 controls
  - SR (Supply Chain): 12 controls
  - Total controls: 191
- Added modern compliance mappings via SCF 2025.4
  - ISO 27001:2022, ISO 27002:2022
  - COBIT 2019, CIS Controls v8
  - NIST CSF 2.0, SOC 2 TSC
- Set up Cloudflare redirect rules for legacy paths
  - /BB3/* -> /community/discussionforum
  - /cms/* -> /
  - /jcms/* -> /

### 2026-02-05 - Website Launch
- **Site replatform complete**: Astro + Tailwind CSS on Cloudflare Pages
- **Design system**: 5-color OSA palette (#FFFFFF, #00171F, #003459, #007EA7, #00A8E8)
- **Full content migration**: Patterns, controls, frameworks, foundations, about, blog
- **Framework mappings section**: ISO 27001, ISO 27002, COBIT 2019, CIS v8, NIST CSF 2.0, SOC 2
- **SEO**: Sitemap generation, meta descriptions, 301 redirects for legacy URLs
- **Mobile**: Responsive design with working hamburger menu
- **Personas page**: Who Uses OSA with SVG avatars
- **Cut over**: opensecurityarchitecture.org now serving new site
- **Repos**:
  - osa-data: Structured JSON data
  - osa-website: Astro site source

### Next Session
- PCI-DSS v4.0 mappings
- API layer (Phase 2)
- Pattern-level compliance enrichment
- Consider Google Search Console submission
- Social/community building (see docs/SOCIAL-STRATEGY.md)

## Backlog

### Icon Set Modernisation (Validate First)
- Old icons drove significant traffic - check if still valuable niche
- Modern icon sets (Heroicons etc) don't cover security-specific symbols
- If demand exists: modernise to SVG, consistent grid, OSA palette
- Would enable dynamic diagram generation
- **Action**: Check old analytics, validate demand before investing

### Graph-Based Architecture Vision (Phase 3+)
- Security architecture as graph: nodes (assets), edges (relationships)
- Controls applied to both nodes and edges
- Dynamic pattern generation based on system description
- AI-powered conversational threat modelling
- See detailed vision: docs/VISION-GRAPH-ARCHITECTURE.md
