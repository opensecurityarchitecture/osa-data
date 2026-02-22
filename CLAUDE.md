# CLAUDE.md — osa-data

Structured JSON data for Open Security Architecture (OSA) patterns, NIST 800-53 controls, and compliance framework mappings. This is the **data layer** — the website reads from this repo via a symlink.

## Repositories

| Repo | Purpose | Visibility |
|------|---------|------------|
| [osa-data](https://github.com/opensecurityarchitecture/osa-data) | Patterns, controls, frameworks (this repo) | Public |
| [osa-website](https://github.com/opensecurityarchitecture/osa-website) | Astro site, Cloudflare Pages | Public |
| [osa-trident](https://github.com/opensecurityarchitecture/osa-trident) | TRIDENT data, schemas, scripts, design docs | **Private** |
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
- **63 compliance framework coverage files** (79 in website registry) with cross-references
- `data/attack/metadata.json` — TRIDENT graph versioning, provenance, checksums, and changelog (90,501 edges, 43 edge types, 27 entity types)

> **Note:** TRIDENT data catalogs, schemas, and enrichment scripts have moved to [osa-trident](https://github.com/opensecurityarchitecture/osa-trident). Only `metadata.json` and `attack-metadata.schema.json` remain here. Locally, `data/attack/*.json` are symlinks to the osa-trident checkout.

### metadata.json Structure

This file is the **public contract** between osa-trident (private) and osa-website (public). It contains:

- **`graph_version`** (semver): Data version, bumped on significant graph changes
- **`graph_schema_version`**: Must match `trident-model.json` version (currently `1.1`). Website build fails on mismatch.
- **`graph_build_id`**: ISO timestamp of last build
- **`files`**: SHA-256 checksums, entity counts, and last-modified dates for all data files
- **`changelog`**: Version history with categorised change entries
- **`edge_types`**, **`entity_schemas`**: Graph structure summary for build-time validation

**CRITICAL — CI will break if this file is not kept in sync with osa-trident.** The website build validates that:

1. Every `hasData: true` nodeType in `trident-model.json` exists in `graph_summary.node_types`
2. Every edge type in `graph-edges.json` exists in `graph_summary.edge_types`

When osa-trident data changes (new entity types, edge types, or catalogs), you MUST update `metadata.json`:

- Add new node types to `graph_summary.node_types` with entity count
- Add new edge types to `graph_summary.edge_types` with edge count
- Update `total_edges` and `total_edge_types`
- Add new files to `files` section (SHA-256, entity_count, description)
- Update checksums for modified files (`graph-edges.json`, `trident-model.json`, etc.)
- Add `data_layers` entry and `changelog` entry
- Bump `graph_version`

## Directory Structure

```
data/
├── patterns/           # SP-NNN-descriptive-title.json
│   └── _manifest.json  # Index of all patterns
├── controls/           # NIST 800-53 Rev 5 (AC-01.json, etc.)
│   ├── _manifest.json
│   └── _catalog.json
├── attack/
│   └── metadata.json                    # Provenance, version info, graph summary
├── verticals/
│   └── financial-services.json          # FS vertical profile with threat profiles
└── schema/
    ├── pattern.schema.json
    ├── control.schema.json
    ├── framework-coverage.schema.json
    └── attack-metadata.schema.json      # Validates metadata.json
```

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
- TRIDENT data, schemas, scripts, design docs → **osa-trident** (private)
- Site source, SVGs, icons, JS, CSS → **osa-website**
- Strategy, metrics, contacts, social plans → **osa-strategy** (private)
- Personal session notes, preferences → your private `.claude/` memory (never committed)
