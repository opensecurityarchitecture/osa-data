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

- **48 security patterns** (SP-001 to SP-047) + SP-000 reference/style guide + SP-999 test
- **315 NIST 800-53 Rev 5 controls** across 20 families
- **36 compliance frameworks** (1,840 clauses) with cross-references
- **472 MITRE ATT&CK techniques** mapped to 108 controls via CTID (ATT&CK v16.1)
- **163 ATT&CK threat groups** with 2,921 technique USES edges
- **44 ATT&CK mitigations** (M-series, v18.1) with 1,445 technique COUNTERS edges
- **691 ATT&CK detection strategies** (DET-series, v18.1) with technique DETECTS edges
- **171 CIS v8 safeguards** reverse-indexed to controls (IMPLEMENTED_BY edges)
- **135 CWE weakness classes** mapped to 132 techniques via CAPEC bridge (EXPLOITS edges)
- **30 TPCE process capabilities** across 19 NIST families (CLASSIFIED_BY edges)
- **28 TTCE technology classes** with 86 D3FEND-aligned capabilities (PROVIDES_CAPABILITY edges)
- **5 TACM adversary tiers** classifying all 469 techniques by minimum sophistication (TIER_CONTAINS edges)
- **24 THFM cognitive vulnerability classes** across 6 categories with 31 EXPLOITS_HUMAN edges
- **35 TIDM identity entities** (10 IDPs, 12 policies, 8 principals, 5 federation patterns) with 171 edges
- **22 cloud services** with shared responsibility splits (PROVIDER_IMPLEMENTS + CUSTOMER_IMPLEMENTS edges)
- **37 protocols** across 11 categories (TARGETS_PROTOCOL + UPGRADES_TO edges)
- **14 data types** with classification tiers (REQUIRES_PROTECTION + PROTECTS_DATA edges)
- **5 insider stages** with progression model (TRANSITIONS_TO + INDICATED_BY + STAGE_DETECTED_BY edges)
- **274 CPE reference entries** across 4 layers (major platforms, enterprise apps, infrastructure, FS applications) with 24 PARENT_OF hierarchy edges. 205 NVD-sourced, 69 OSA-minted for FS platforms.
- **20,584 TRIDENT graph edges** across 29 relationship types, 20 entity types

## Directory Structure

```
data/
├── patterns/           # SP-NNN-descriptive-title.json
│   └── _manifest.json  # Index of all patterns
├── controls/           # NIST 800-53 Rev 5 (AC-01.json, etc.)
│   ├── _manifest.json
│   └── _catalog.json
├── attack/             # TRIDENT attack/weakness/control graph
│   ├── technique-catalog.json           # 472 techniques with mitigations[], detection_strategies[], weaknesses[], minTier
│   ├── mitigation-catalog.json          # 44 ATT&CK mitigations with techniques[], controls[], cis_safeguards[]
│   ├── detection-catalog.json           # 691 ATT&CK v18 detection strategies
│   ├── cis-safeguard-index.json         # 171 CIS v8 safeguards -> controls reverse index
│   ├── weakness-catalog.json            # 135 CWE weakness classes -> techniques via CAPEC
│   ├── actor-catalog.json               # 163 ATT&CK threat groups -> techniques (USES)
│   ├── process-capability-catalog.json  # 30 TPCE process capabilities -> controls (CLASSIFIED_BY)
│   ├── technology-capability-catalog.json # 28 TTCE technology classes + 86 capabilities (PROVIDES_CAPABILITY)
│   ├── adversary-tier-catalog.json      # 5 TACM tiers -> techniques (TIER_CONTAINS)
│   ├── human-factors-catalog.json       # 24 THFM cognitive vulnerability classes (EXPLOITS_HUMAN)
│   ├── cloud-service-catalog.json       # 22 cloud services with shared responsibility splits
│   ├── data-classification-catalog.json # 14 TDCE data types with protection requirements
│   ├── protocol-catalog.json            # 37 TPE protocols with technique attack surface
│   ├── insider-stage-catalog.json       # 5 THFM insider threat progression stages
│   ├── cpe-catalog.json                 # 274 CPE reference entries (L1-L4, 205 NVD + 69 OSA-minted)
│   ├── cpe-parent-of-edges.json         # 24 CPE PARENT_OF hierarchy edges
│   ├── graph-edges.json                 # 20,454 explicit TRIDENT graph edges
│   └── metadata.json                    # Provenance, version info, graph summary
├── verticals/
│   └── financial-services.json          # FS vertical profile with threat profiles
└── schema/
    ├── pattern.schema.json
    ├── control.schema.json
    └── trident.schema.json              # 40 $defs, 17+ entity types
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
| ProcessCapability→Control | TPCE (Vinylwasp design) | OSA first-party | No (reference enumeration) | 30 capabilities, 140 CLASSIFIED_BY edges |
| TechnologyClass→Control | TTCE (Vinylwasp design) | OSA first-party | No (reference enumeration) | 28 classes, 123 PROVIDES_CAPABILITY edges |
| AdversaryTier→Technique | TACM (Vinylwasp design) | OSA first-party | No (capability classification) | 5 tiers, 469 TIER_CONTAINS edges |
| Technique→HumanFactor | THFM (Vinylwasp design) | OSA first-party | Yes (rationale per exploitedBy) | 24 classes, 31 EXPLOITS_HUMAN edges |
| Technique→Technique | ATT&CK hierarchy | MITRE first-party | No (canonical sub-technique hierarchy) | 301 PARENT_OF edges |
| Capability→CIS/Mitigation | TPCE/TTCE cross-ref | OSA first-party | No (capability alignment) | 246 CAPABILITY_SUPPORTS_CIS + 88 CAPABILITY_SUPPORTS_MITIGATION edges |
| CloudService→Control | TCSE (Vinylwasp design) | OSA first-party | No (shared responsibility) | 22 services, 291 PROVIDER_IMPLEMENTS + 270 CUSTOMER_IMPLEMENTS edges |
| DataType→Control | TDCE (Vinylwasp design) | OSA first-party | No (data classification) | 14 types, 140 REQUIRES_PROTECTION + 140 PROTECTS_DATA edges |
| Technique→Protocol | TPE (Vinylwasp design) | OSA first-party | No (protocol attack surface) | 37 protocols, 54 TARGETS_PROTOCOL + 4 UPGRADES_TO edges |
| InsiderStage→HumanFactor | THFM (Vinylwasp design) | OSA first-party | No (CERT CPIR progression) | 5 stages, 4 TRANSITIONS_TO + 16 INDICATED_BY + 26 STAGE_DETECTED_BY edges |
| CPE Reference Catalog | NVD CPE Dictionary + OSA | NVD (205) + OSA (69) | No (reference catalog) | 274 CPE entries across 4 layers, 24 PARENT_OF edges. L4 FS apps: 10 TFSP categories. |

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
