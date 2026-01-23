# CLAUDE.md - Open Security Architecture Workspace

This workspace is for the modernisation of opensecurityarchitecture.org (OSA).

## Project Context

**OSA** has been running since ~2008, developed actively for 4-5 years, then dormant. Despite minimal maintenance, it continues to receive traffic. Pattern content was published in O'Reilly (Cloud Pattern). The site runs on Joomla, hosted via Cloudflare.

**Goal**: Modernise OSA as a weekend side project, with realistic targets to grow traffic and value.

## Founder Context

**Russ** — OSA founder, also founder of ADAvault.

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
| 0 | Discovery - traffic analysis, content audit, security posture | Not started |
| 1 | Data extraction - patterns to structured format | Not started |
| 2 | API layer - expose patterns via API | Not started |
| 3 | AI integration - Claude-powered features | Not started |
| 4 | Platform decision - Joomla refresh vs replatform | Not started |

## Workspace Structure

```
osa-workspace/
├── CLAUDE.md              # This file
├── docs/
│   ├── DISCOVERY.md       # Phase 0 findings
│   ├── PATTERNS.md        # Pattern catalogue analysis
│   └── ROADMAP.md         # Detailed roadmap
└── data/                  # Extracted pattern data (future)
```

## Key Questions to Answer (Phase 0)

1. What's the actual traffic profile? (Cloudflare analytics)
2. Which content is most valuable? (top pages, search queries)
3. What's the current security posture? (Joomla version, vulnerabilities)
4. How much pattern content exists? (catalogue size, formats)
5. What would a minimal viable modernisation look like?

## Relationship to AdaVault

This project is **separate** from AdaVault work:
- Different Cloudflare account
- Weekend cadence (not weekday AdaVault time)
- Hosted on AdaVault infrastructure but operationally independent

## Commands

```bash
# Open workspace
cd /Users/russellwing/osa-workspace

# (Future) Cloudflare API commands will go here once API key configured
```

## Session Log

### 2025-01-23 - Project Kickoff
- Discussed modernisation potential with Russ
- Agreed weekend side hustle approach
- Created this workspace
- Next: Get Cloudflare API access, analyse traffic data
