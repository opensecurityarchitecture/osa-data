---
name: enrich-pattern
description: Enrich an existing OSA pattern — add missing sections, deepen content, update controls and threats
---

# Enrich Pattern

Enrich an existing OSA security pattern by auditing its current state, identifying gaps, and adding/improving content to match the quality bar of SP-051 and SP-052.

## Arguments

- **Pattern ID** (required) — e.g., `SP-029`, `SP-005`
- **Sections to focus on** (optional) — e.g., `threats controls`, `developing-areas`, `content`. If provided, only enrich those sections. If omitted, enrich everything that needs it.

## Instructions

### Step 1 — Audit Current State

Read the pattern JSON from `data/patterns/`. Also read `data/patterns/SP-051-tokenised-asset-security-architecture.json` (first 100 lines) as the quality reference.

Run ALL of the following checks against the pattern. Score each as PASS / WARN / FAIL:

**Structure (FAIL if missing):**
- [ ] `$schema` field present (value: `"../schema/pattern.schema.json"`)
- [ ] `id`, `slug`, `title`, `description` present and non-empty
- [ ] `url` present and matches `https://www.opensecurityarchitecture.org/patterns/sp-NNN`
- [ ] `metadata` with `release`, `classification`, `status`, `type`, `datePublished`, `dateModified`, `authors`
- [ ] `metadata.provenance` present and substantive (not empty string)
- [ ] `content.description` present — 4+ paragraphs of substantive content (not 1-2 sentence stub)
- [ ] `content.keyControlAreas` present with 7+ entries, each with inline NIST refs in parentheses
- [ ] `content.assumptions` present and substantive
- [ ] `content.typicalChallenges` present and substantive
- [ ] `content.indications` present and substantive
- [ ] `content.contraIndications` present and substantive
- [ ] `content.threatResistance` present and substantive
- [ ] `controls` array present with 25+ entries, each having `id`, `name`, `family`, `emphasis`
- [ ] `controlFamilySummary` present and counts match actual controls array
- [ ] `threats` array present with 8+ entries
- [ ] `references` array present with 8+ entries (each with `title`, `url`, `note`)
- [ ] `relatedPatterns` array present (string format `["SP-NNN"]`, NOT objects)
- [ ] `relatedPatternNames` parallel array present, same length as `relatedPatterns`
- [ ] `diagram` object with `svg` path set
- [ ] `legend` field present

**Quality (WARN if missing/weak):**
- [ ] `examples` object with 3+ categories
- [ ] `examples["Developing Areas"]` present with 5+ entries (4-6 sentences each)
- [ ] Every `threats[].mitigatedBy` control ID exists in the `controls[]` array
- [ ] Every threat has `title` (or `name`) AND `description` (3+ sentences) — not just a name
- [ ] Every threat has a `T-XXX-NNN` format ID
- [ ] `controlFamilySummary` counts exactly match actual `controls[]` array per family
- [ ] Each keyControlArea paragraph is 4+ sentences with multiple inline NIST refs
- [ ] `content.description` is 4+ paragraphs covering scope, architecture, threats, and applicability
- [ ] `metadata.provenance` explains real-world origin (not placeholder)
- [ ] `context` object present with `dataTypes`, `protocols`, `assetTypes`, `adversaryProfile`, `regulatoryScope`, `humanFactors`

**Cross-references (WARN if broken):**
- [ ] All `relatedPatterns` IDs exist in `data/patterns/_manifest.json`
- [ ] SVG file exists at `website/public/images/{diagram.svg path}`
- [ ] Manifest entry exists and control count matches pattern

**Depth metrics:**
- Control count (target: 25-50)
- Threat count (target: 8-12)
- Number of NIST control families covered (target: 8+)
- Example categories count (target: 3-5 plus Developing Areas)
- Reference count (target: 8-12)
- Average threat description length (flag if < 100 chars or if `description` field is absent)
- Average keyControlArea length (flag if < 200 chars)
- Number of keyControlAreas (target: 7-10)

**Present the gap report to the user.** Format it clearly:

```
Enrichment Audit: SP-NNN — Pattern Title
==========================================

Structure:  14/20 PASS, 4 WARN, 2 FAIL
Quality:     6/10 PASS, 3 WARN, 1 FAIL

FAIL  Missing metadata.provenance
FAIL  Missing content.contraIndications
WARN  Only 14 controls (target: 25-50)
WARN  Threats have name but no description
WARN  Missing Developing Areas
WARN  Missing context object

Depth:
  Controls:         14 (6 families) — needs expansion
  Threats:          10 — count OK but descriptions needed
  KeyControlAreas:   5 — needs 2-5 more
  Examples:          4 categories — OK
  References:        6 — needs 2-6 more
  Developing Areas:  0 — needs adding
```

### Step 2 — Plan Enrichment

Based on the audit results, propose a concrete enrichment plan. List exactly what will be added or improved:

**Content sections:**
- `content.description` — expand to 4-6 substantive paragraphs if currently thin
- `content.keyControlAreas` — add entries to reach 7-10, each 4-8 sentences with multiple inline NIST control references in parentheses (e.g., "SC-12, SC-13")
- `content.assumptions` — add if missing, expand if stub
- `content.typicalChallenges` — add if missing, expand if stub
- `content.indications` — add if missing
- `content.contraIndications` — add if missing
- `content.threatResistance` — add if missing, expand if stub

**Metadata:**
- `metadata.provenance` — add real-world context explaining origin and experience behind the pattern
- `metadata.dateModified` — update to today's date
- `metadata.authors` — add "Vitruvius" if not present

**Controls:**
- Add controls to reach 25-50 total with proper `emphasis` levels:
  - `critical` — essential, failure = likely breach (typically 5-10 controls)
  - `important` — strongly recommended (typically 8-15 controls)
  - `standard` — good practice (the rest)
- Every control must have `id`, `name`, `family`, `emphasis`
- All IDs must be valid NIST 800-53 Rev 5 (format: `XX-NN`)
- Update `controlFamilySummary` to match

**Threats:**
- Add threats to reach 8-12 with proper structure:
  - `id`: `T-XXX-NNN` format (where XXX is a 2-3 letter domain code unique to this pattern)
  - `title`: concise threat name
  - `description`: 3-5 sentences explaining the attack vector, potential impact, and why the mapped controls mitigate it
  - `mitigatedBy`: array of control IDs that MUST exist in the pattern's `controls[]` array
- Check existing threat IDs across other patterns to avoid clashes — read the manifest or grep for the T-XXX prefix

**Examples:**
- Add categories to reach 3-5 topic-specific categories with 2-4 examples each
- Add `Developing Areas` array with 5 forward-looking paragraphs (4-6 sentences each covering emerging trends, immature technologies, and unsolved problems relevant to the pattern)

**References:**
- Add authoritative references to reach 8-12, each with `title`, `url`, `note`
- Prefer: NIST publications, OWASP, MITRE, ISO standards, vendor-neutral industry guidance, academic sources

**Related patterns:**
- Verify existing `relatedPatterns` IDs against manifest
- Add any obviously related patterns that are missing
- Ensure `relatedPatternNames` is a parallel array with correct titles

**Context object:**
- Add `context` object if missing, with relevant fields:
  - `dataTypes`: array of `{ "ref": "TDCE-XXX-NN", "state": [...], "volume": "..." }` objects
  - `protocols`: array of `{ "ref": "TPE-XXX-NN", "boundary": "...", "direction": "..." }` objects
  - `assetTypes`: array of lowercase-hyphenated asset type strings
  - `adversaryProfile`: `{ "minTier": "TACM-TN", "relevantActorTypes": [...] }`
  - `regulatoryScope`: array of framework strings (e.g., "GDPR", "PCI-DSS")
  - `humanFactors`: array of `"THFM-XXX-NN"` strings

**Other:**
- `$schema` — add `"../schema/pattern.schema.json"` if missing
- `url` — add/fix if missing
- `legend` — add if missing (describe the diagram zones/colours)
- `diagram` — leave as-is (do NOT create/modify SVGs)

**Present the plan to the user and WAIT for approval before proceeding.** Show estimated additions:
```
Enrichment Plan for SP-NNN
============================
Controls:    14 -> ~35 (+21 new across 5 additional families)
Threats:     10 -> 10 (add descriptions to all 10)
KCAs:         5 -> 8 (+3 new areas)
Examples:     4 -> 5 (+Developing Areas)
References:   6 -> 10 (+4 new)
New sections: provenance, contraIndications, context object

Proceed? (y/n)
```

### Step 3 — Enrich

After user approval, make the changes. Critical rules:

1. **PRESERVE all existing content.** Never delete, overwrite, or shorten any existing text, control, threat, example, or reference. This is ADDITIVE enrichment only.

2. **Match the tone and depth of SP-051/SP-052.** These are professional security architecture patterns used by enterprise architects, CISOs, and GRC teams. Content must be authoritative, specific, and technically precise.

3. **Ensure control validity:**
   - All control IDs must be valid NIST 800-53 Rev 5 identifiers
   - Format: two uppercase letters + hyphen + two digits (e.g., `AC-06`, `SC-12`, `IR-04`)
   - The 20 valid family prefixes are: AC, AT, AU, CA, CM, CP, IA, IR, MA, MP, PE, PL, PM, PS, PT, RA, SA, SC, SI, SR
   - Cross-check against `data/controls/` directory for valid IDs if uncertain

4. **Ensure threat ID uniqueness:**
   - Use `T-XXX-NNN` format where XXX is a 2-3 letter domain code for this pattern's subject area
   - Check existing patterns for the same prefix to avoid clashes: `grep -r '"T-XXX-' data/patterns/`
   - Number sequentially from existing highest (or 001 if new prefix)

5. **Ensure threat mitigatedBy integrity:**
   - Every control ID in any `mitigatedBy` array MUST exist in the pattern's `controls[]` array
   - If a threat needs a control that is not in the array, add the control first

6. **Update controlFamilySummary:**
   - Recount every family from the actual controls array
   - The summary must exactly match: `{ "AC": 5, "SC": 8, ... }`

7. **Update metadata.dateModified** to today's date (YYYY-MM-DD format).

8. **Add "Vitruvius" to metadata.authors** if not already present (append, do not replace existing authors).

9. **Content quality standards:**
   - `content.description`: 4-6 paragraphs. Cover: what the pattern is, why it matters, the threat landscape, architectural approach, scope/applicability, and target audience.
   - `keyControlAreas`: each entry should be 4-8 sentences with a title prefix like "Area Name (XX-NN, YY-NN, ZZ-NN):" followed by substantive explanation of WHY these controls matter for this pattern, HOW they are implemented, and WHAT happens if they fail.
   - `threats[].description`: 3-5 sentences explaining the attack vector, the potential impact (with quantified examples where possible), and a brief note on why the mapped controls provide mitigation.
   - `examples["Developing Areas"]`: 5 paragraphs of 4-6 sentences each. Cover emerging technologies, unsolved problems, regulatory evolution, industry trends, and future architectural challenges relevant to this pattern's domain.
   - `references[].note`: 1-2 sentences explaining why this reference is relevant to the pattern specifically (not generic descriptions).

10. **If the user specified sections to focus on**, only enrich those sections. Leave everything else untouched. Still update `dateModified` and add Vitruvius to authors.

### Step 4 — Validate

After making changes:

1. Run schema validation:
   ```bash
   python3 scripts/validate_json.py 2>&1 | grep -E "SP-NNN|error|FAIL|Error"
   ```
   If validation fails, fix the issue and re-validate. Common issues:
   - Control ID format mismatch (must be `XX-NN`, not `XX-NNN` or lowercase)
   - Missing required fields on control objects (`id`, `name`, `family`)
   - `relatedPatterns` containing objects instead of strings
   - Invalid enum values in `context` fields

2. Verify threat-control integrity:
   - Every `threats[].mitigatedBy` control ID must exist in `controls[].id`
   - Report any orphaned references

3. Verify relatedPatterns:
   - Read `data/patterns/_manifest.json`
   - Every ID in `relatedPatterns` must have a matching entry in the manifest
   - Report any broken references

4. Verify controlFamilySummary accuracy:
   - Count controls per family from the actual array
   - Compare against `controlFamilySummary`
   - Fix any mismatches

### Step 5 — Report

Show a before/after comparison:

```
Enrichment Complete: SP-NNN — Pattern Title
=============================================

Controls:        14 -> 36 (was 6 families, now 12)
Threats:         10 -> 10 (descriptions added to all)
KeyControlAreas:  5 ->  8
Examples:         4 categories -> 5 (+Developing Areas with 5 entries)
References:       6 -> 10
Related Patterns: 6 ->  7

Sections added/expanded:
  + metadata.provenance (new)
  + content.contraIndications (new)
  + content.keyControlAreas (3 entries added)
  ~ content.description (expanded from 2 to 5 paragraphs)
  + examples["Developing Areas"] (5 entries)
  + context object (dataTypes, assetTypes, adversaryProfile, regulatoryScope)
  + 22 new controls (AC: +3, AU: +4, CM: +2, IR: +3, PE: +2, PM: +1, RA: +2, SA: +3, SR: +2)
  ~ controlFamilySummary (updated to match)
  ~ metadata.dateModified -> 2026-03-12
  ~ metadata.authors -> added Vitruvius

Validation: PASS
Threat-control integrity: PASS (all mitigatedBy refs valid)
Related pattern cross-refs: PASS (all IDs in manifest)

Remaining gaps:
  - SVG diagram needs updating to reflect new controls (separate task)
  - Manifest control count should be updated to 36
```

## Important Rules

- **ADDITIVE ONLY** — never remove existing content. If existing text is weak, add to it; do not replace it.
- **Do NOT commit or push.** The user decides when to commit.
- **Do NOT create or modify SVG diagrams.** That is a separate task.
- **Do NOT modify _manifest.json** control counts here — just note the discrepancy in the report. The user or a separate process handles manifest updates.
- **Quality bar: match SP-051/SP-052 depth.** These patterns are used by enterprise security architects and auditors. Stubs, generic summaries, and filler content are not acceptable.
- **Threat descriptions must be substantive.** 3-5 sentences explaining: what the attacker does, how the attack works, what the impact is (with real-world examples or quantified losses where possible), and which controls mitigate it and why.
- **keyControlAreas paragraphs must be substantive.** 4-8 sentences with multiple inline NIST control references. Explain: what the control area covers, why it matters for this specific pattern, how it is typically implemented, and what happens if it is missing.
- **Control emphasis levels must be justified:**
  - `critical` — the pattern fundamentally depends on this control; without it, the primary security objective fails
  - `important` — strongly recommended; absence significantly increases risk
  - `standard` — good practice that rounds out the security posture
- **If a pattern is already at gold-standard quality** (passes all checks with good depth metrics), say so and ask the user if there are specific areas they want expanded rather than making unnecessary changes.
