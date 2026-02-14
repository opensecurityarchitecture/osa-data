# CLAUDE.md — osa-data

Structured JSON data for Open Security Architecture (OSA) patterns, NIST 800-53 controls, and compliance framework mappings. This is the **data layer** — the website reads from this repo via a symlink.

## Repositories

| Repo | Purpose | Visibility |
|------|---------|------------|
| [osa-data](https://github.com/opensecurityarchitecture/osa-data) | Patterns, controls, frameworks (this repo) | Public |
| [osa-website](https://github.com/opensecurityarchitecture/osa-website) | Astro site, Cloudflare Pages | Public |
| [osa-strategy](https://github.com/opensecurityarchitecture/osa-strategy) | Roadmap, metrics, contacts, social | **Private** |

The website repo is checked out as a subdirectory at `./website/` and reads data via a symlink (`website/src/data -> ../..`). A push to osa-data triggers an osa-website rebuild via GitHub Actions dispatch.

## Founders

| Name | Alias | Location | Focus |
|------|-------|----------|-------|
| Tobias Christen | Aurelius | Zurich | Enterprise security architecture, pattern design, product strategy |
| Chris Lethaby | Vinylwasp | London | APT defence, CBEST, GRC, CIS Controls |
| Russell Wing | Spinoza | London | Platform, NIST mappings, compliance frameworks, assessment |
| Claude (AI) | Vitruvius | — | Pattern enrichment, new patterns, technical implementation |

## Current Data

- **48 security patterns** (SP-001 to SP-046) + SP-000 reference/style guide + SP-999 test
- **315 NIST 800-53 Rev 5 controls** across 20 families
- **26 compliance frameworks** with cross-references
- **469 MITRE ATT&CK techniques** mapped to 108 controls via CTID (ATT&CK v16.1)
- **163 ATT&CK threat groups** with 2,921 technique USES edges
- **44 ATT&CK mitigations** (M-series, v18.1) with 1,445 technique COUNTERS edges
- **691 ATT&CK detection strategies** (DET-series, v18.1) with technique DETECTS edges
- **171 CIS v8 safeguards** reverse-indexed to controls (IMPLEMENTED_BY edges)
- **135 CWE weakness classes** mapped to 132 techniques via CAPEC bridge (EXPLOITS edges)
- **18,111 TRIDENT graph edges** across 8 relationship types

## Directory Structure

```
data/
├── patterns/           # SP-NNN-descriptive-title.json
│   └── _manifest.json  # Index of all patterns
├── controls/           # NIST 800-53 Rev 5 (AC-01.json, etc.)
│   ├── _manifest.json
│   └── _catalog.json
├── attack/             # TRIDENT attack/weakness/control graph
│   ├── technique-catalog.json    # 469 techniques with mitigations[], detection_strategies[], weaknesses[]
│   ├── mitigation-catalog.json   # 44 ATT&CK mitigations with techniques[], controls[], cis_safeguards[]
│   ├── detection-catalog.json    # 691 ATT&CK v18 detection strategies
│   ├── cis-safeguard-index.json  # 171 CIS v8 safeguards -> controls reverse index
│   ├── weakness-catalog.json     # 135 CWE weakness classes -> techniques via CAPEC
│   ├── actor-catalog.json        # 163 ATT&CK threat groups -> techniques (USES)
│   ├── graph-edges.json          # 18,111 explicit TRIDENT graph edges
│   └── metadata.json             # Provenance, version info, graph summary
└── schema/
    ├── pattern.schema.json
    └── control.schema.json
```

## TRIDENT Data Layer Provenance

Each layer in the TRIDENT graph has different source authority and validation characteristics:

| Layer | Source | Authority | Has Rationale? | Notes |
|-------|--------|-----------|----------------|-------|
| Technique→Control (CTID) | CTID Mappings Explorer | Third-party interpretive | Yes — `mapping_type` + `rationale` on each of 5,246 relationships | Only layer with custom rationale (interpretive mapping needs audit trail) |
| Mitigation→Technique | ATT&CK STIX v18.1 | MITRE first-party | No (canonical MITRE relationship) | 44 mitigations, 1,445 COUNTERS edges |
| Detection→Technique | ATT&CK STIX v18.1 | MITRE first-party | No (canonical MITRE relationship) | 691 detections (1:1 with techniques) |
| Technique→Weakness | CWE via CAPEC bridge | MITRE first-party chain | No (upstream MITRE data) | 28% technique coverage is expected — CAPEC only covers software-level patterns |
| Actor→Technique | ATT&CK STIX v18.1 | MITRE first-party | No (canonical MITRE relationship) | 163 groups, 2,921 USES edges, 313 techniques with actors |
| CIS Safeguard→Control | OSA compliance_mappings | OSA first-party | Inherited from framework mapping | 171 safeguards, 468 IMPLEMENTED_BY edges |

## Naming Conventions

- **Pattern JSON**: `SP-NNN-descriptive-title.json` (e.g., `SP-029-zero-trust-architecture.json`)
- **Pattern SVGs**: `sp-NNN-descriptive-title.svg` in `website/public/images/` (e.g., `sp-029-zero-trust-architecture.svg`)
- **Control JSON**: `XX-NN.json` using NIST ID (e.g., `AC-01.json`, `SC-13.json`)
- **Slugs**: lowercase, hyphenated, no `sp-NNN-` prefix (e.g., `zero-trust-architecture`)
- **Pattern IDs**: `SP-NNN` format, zero-padded to 3 digits

## Adding a New Pattern

1. Create `data/patterns/SP-NNN-descriptive-title.json` following the schema
2. Add entry to `data/patterns/_manifest.json`
3. Create SVG diagram at `website/public/images/sp-NNN-descriptive-title.svg`
4. That's it — the website reads the manifest and renders automatically

## Pattern Schema Key Fields

- `id`, `title`, `slug`, `description` — identity
- `metadata.status` — `active`, `draft`, `published`, `reserved`, `deprecated`
- `metadata.type` — `pattern`, `module`, `reference`
- `metadata.authors` — use aliases (Aurelius, Vinylwasp, Spinoza, Vitruvius)
- `controls[]` — NIST 800-53 control mappings with `emphasis` (critical/important/standard)
- `threats[]` — threat catalogue with `mitigatedBy` control references
- `content.keyControlAreas[]` — key areas with inline NIST references
- `examples{}`, `references[]`, `relatedPatterns[]`

## SVG Diagram Conventions

- ViewBox: `960 x 720`
- Palette: `#003459`, `#007EA7`, `#00A8E8`, `#00171F`, `#FFFFFF`
- NIST badges: clickable `xlink:href` to `/controls/XX-NN`
- Reference taglines: clickable links at bottom
- White lozenge technique: `rect fill="white" opacity="0.9" rx="3"` behind arrow text
- Icons from OSA icon library (`website/public/icons/`)

## Commands

```bash
# Validate all JSON against schemas
python3 scripts/validate_json.py

# Website build (from workspace root)
npm --prefix website run build

# Website dev server
npm --prefix website run dev
```

## CI/CD

- **osa-data**: GitHub Actions validates all JSON against schemas on push
- **osa-website**: Cloudflare Pages auto-deploys on push; also triggered by osa-data dispatch
- **Cross-repo dispatch**: osa-data push → GitHub Actions → `repository_dispatch` → osa-website rebuild

## What Goes Where

- Pattern data, controls, schemas → **this repo** (osa-data)
- Site source, SVGs, icons, JS, CSS → **osa-website**
- Strategy, metrics, contacts, social plans → **osa-strategy** (private)
- Personal session notes, preferences → your private `.claude/` memory (never committed)
