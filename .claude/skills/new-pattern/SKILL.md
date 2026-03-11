---
name: new-pattern
description: Scaffold a new OSA security pattern with all required sections, update manifest, and validate
---

# New Pattern

Scaffold a complete OSA security pattern JSON file with all required sections, update the manifest, and validate against the schema.

## Arguments

The user should provide:
- **Topic/title** for the pattern (required)
- **SP number** (optional — if not provided, auto-assign next available)
- **Authors** (optional — defaults to Spinoza, Vitruvius)

## Instructions

### 1. Determine SP number

If not provided, read `data/patterns/_manifest.json` and find the next available SP-NNN (highest existing + 1, skip SP-999).

### 2. Read the schema and a reference pattern

- Read `data/schema/pattern.schema.json` for required fields
- Read `data/patterns/SP-051-tokenised-asset-security-architecture.json` as a modern reference for structure, depth, and tone

### 3. Generate the pattern JSON

Create `data/patterns/SP-NNN-descriptive-title.json` with ALL of these sections:

**Top-level fields:**
- `$schema`: `"../schema/pattern.schema.json"`
- `id`: `"SP-NNN"`
- `slug`: lowercase-hyphenated (no SP-NNN prefix)
- `title`: full title
- `description`: 3-5 sentence technical description mentioning control count, families, and applicability
- `url`: `"https://www.opensecurityarchitecture.org/patterns/sp-NNN"`
- `metadata`: release (YY.MM), classification, status (`"draft"`), type (`"pattern"`), datePublished, dateModified, authors (use aliases), reviewers (empty), provenance
- `diagram`: svg path at `/images/sp-NNN-descriptive-title.svg`, empty png
- `legend`: colour-coded description of diagram zones

**Content object — ALL fields required:**
- `description`: 4-6 paragraphs of substantive technical content
- `keyControlAreas`: array of 7-10 detailed paragraphs, each with inline NIST control references
- `assumptions`: 1 paragraph
- `typicalChallenges`: 1-2 paragraphs
- `indications`: when to use
- `contraIndications`: when NOT to use
- `threatResistance`: what the pattern defends against

**Examples object — ALL keys required:**
- 3-5 topic-specific example categories, each with 2-4 detailed examples
- **`Developing Areas`**: array of 5 forward-looking paragraphs (4-6 sentences each)

**Other required sections:**
- `references`: 8-12 authoritative references with title, url, note
- `relatedPatterns`: string array of SP-NNN IDs
- `relatedPatternNames`: parallel string array of pattern titles
- `controls`: array of objects with `id`, `name`, `family`, `emphasis` (critical/important/standard). Target 25-50 controls.
- `controlFamilySummary`: object mapping family codes to counts
- `threats`: array of 8-12 threat objects with `id` (T-XXX-NNN format), `title`, `description` (3-5 sentences), `mitigatedBy` (array of control IDs)
- `context`: object with `dataTypes`, `protocols`, `assetTypes`, `adversaryProfile` (minTier, relevantActorTypes), `regulatoryScope`, `humanFactors`

### 4. Common schema gotchas (MUST follow)

- `controls[].name` NOT `title` — use the NIST control name
- `controls[].family` is required — extract from control ID prefix
- `relatedPatterns` must be a STRING array (`["SP-029"]`), NOT objects
- `threats[].mitigatedBy` must reference control IDs that exist in the controls array
- All control IDs must be valid NIST 800-53 Rev 5 identifiers

### 5. Update manifest

Edit `data/patterns/_manifest.json`:
- Add entry: `{ "id": "SP-NNN", "title": "...", "status": "draft", "controls": N, "file": "SP-NNN-descriptive-title.json" }`
- Increment `total_patterns` by 1
- Maintain sorted order by SP number

### 6. Validate

Run: `python3 scripts/validate_json.py 2>&1 | grep -E "SP-NNN|error|FAIL"`

Confirm the new pattern passes. If validation fails, fix and re-validate before reporting success.

### 7. Report

Show the user:
- Pattern ID and title
- Control count and family breakdown
- Threat count
- Related patterns
- Reminder that SVG diagram is still needed at `website/public/images/sp-NNN-descriptive-title.svg`

## Important

- Do NOT commit or push. The user will decide when to commit.
- Do NOT create the SVG diagram (that's a separate step).
- Aim for the same depth and quality as SP-051/SP-052 — these are professional security architecture patterns, not summaries.
