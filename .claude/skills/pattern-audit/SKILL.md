---
name: pattern-audit
description: Audit an OSA pattern for completeness, quality, and consistency
---

# Pattern Audit

Run a comprehensive quality audit on one or more OSA security patterns.

## Arguments

- **Pattern ID(s)** — e.g., `SP-029`, `SP-051 SP-052`, or `all` for full catalogue audit
- If no argument, audit all patterns

## Instructions

### 1. Load pattern(s)

Read the pattern JSON file(s) from `data/patterns/`. If `all`, read the manifest and audit every pattern except SP-000 (reference) and SP-999 (test).

### 2. Run completeness checks

For each pattern, check ALL of the following. Score as PASS / WARN / FAIL:

**Structure (FAIL if missing):**
- [ ] `$schema` field present
- [ ] `id`, `slug`, `title`, `description` present
- [ ] `metadata` with status, type, datePublished, dateModified, authors
- [ ] `content.description` present and non-empty
- [ ] `content.keyControlAreas` present with 5+ entries
- [ ] `content.assumptions` present
- [ ] `content.typicalChallenges` present
- [ ] `content.indications` present
- [ ] `content.contraIndications` present
- [ ] `content.threatResistance` present
- [ ] `controls` array present with 15+ entries
- [ ] `controlFamilySummary` present
- [ ] `threats` array present with 5+ entries
- [ ] `references` array present with 5+ entries
- [ ] `relatedPatterns` array present (string format, not objects)
- [ ] `context` object present

**Quality (WARN if missing/weak):**
- [ ] `examples` object with 3+ categories
- [ ] `examples["Developing Areas"]` present with 3+ entries
- [ ] `legend` field present (needed for diagram)
- [ ] `diagram.svg` path set
- [ ] `relatedPatternNames` parallel array present
- [ ] Every `threats[].mitigatedBy` control ID exists in `controls[]`
- [ ] `controlFamilySummary` counts match actual controls array
- [ ] `metadata.provenance` present and substantive (not empty)
- [ ] Description is 2+ sentences (not a stub)
- [ ] Each keyControlArea references at least one NIST control ID in parentheses

**Cross-references (WARN if broken):**
- [ ] All `relatedPatterns` IDs exist in the manifest
- [ ] SVG file exists at `website/public/images/{expected-path}`
- [ ] Manifest entry exists and control count matches

**Depth indicators (INFO):**
- Number of controls, threats, examples, references, keyControlAreas
- Average threat description length (flag if < 100 chars)
- Average keyControlArea length (flag if < 200 chars)
- Number of NIST control families covered

### 3. Schema validation

Run `python3 scripts/validate_json.py` and check the pattern(s) pass.

### 4. Report

Output a summary table:

```
Pattern Audit Report
====================

SP-029 Zero Trust Architecture
  Structure: 16/16 PASS
  Quality:   10/10 PASS
  X-refs:     3/3  PASS
  Depth:     42 controls, 10 threats, 5 example categories, 12 refs

SP-052 Decentralised Identity & Verifiable Credentials
  Structure: 16/16 PASS
  Quality:    9/10 WARN — missing SVG diagram
  X-refs:     2/3  WARN — SP-044 not in manifest
  Depth:     35 controls, 10 threats, 5 example categories, 12 refs

Issues Found:
  FAIL  SP-015  Missing content.contraIndications
  WARN  SP-052  SVG diagram not found
  WARN  SP-008  Developing Areas section missing
  INFO  SP-006  Only 8 controls (consider enrichment)
```

### 5. If auditing `all`, also report:

- Total patterns audited
- Count of PASS / WARN / FAIL
- Patterns most in need of enrichment (lowest scores)
- Patterns missing Developing Areas (list them)
- Patterns without SVG diagrams (list them)

## Important

- This is a READ-ONLY audit. Do NOT modify any files.
- Be honest about quality — the founders want to know the real state.
- Flag patterns that are stubs vs fully enriched.
