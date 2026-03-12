---
name: generate-coverage
description: Generate a framework coverage analysis JSON file with reverse mappings and statistics
---

# Generate Coverage

Generate a framework coverage analysis JSON file that maps a regulatory/standards framework's clauses to SP 800-53 Rev 5 controls, with expert-assessed coverage percentages and gap analysis.

## Arguments

The user should provide:
- **Framework name** (required) — human-readable name (e.g., "FINMA Circular 2023/1", "EU GDPR")
- **framework_id** (required) — snake_case identifier matching the key used in control files' `compliance_mappings` (e.g., `finma_circular`, `gdpr`, `soc2_tsc`)
- **Jurisdiction** (required) — ISO 3166-1 alpha-2 code or region code: `EU`, `EEA`, `APAC`, `GLOBAL` (e.g., `["CH"]`, `["EU", "EEA"]`)
- **Applicability type** (optional) — one of `mandatory`, `voluntary`, `market_driven` (default: `mandatory`)
- **Source URL** (optional) — authoritative source for the framework
- **Clause definitions** (required) — either provided by the user or collaboratively developed

## Instructions

### Step 1 — Define clause definitions

Work with the user to build the CLAUSE_DEFINITIONS — an array of objects, each with:

```json
{
  "id": "Art. 5(1)(f)",
  "title": "Integrity and confidentiality",
  "coverage_pct": 85,
  "rationale": "SP 800-53 SC, SI, and AC families provide comprehensive integrity and confidentiality controls...",
  "gaps": "Minor: GDPR-specific data processing integrity beyond system-level controls."
}
```

Fields per clause:
- `id` (string, required): Clause identifier within the framework. Must be unique. Examples: `"Art. 5(1)(f)"`, `"CC6.1"`, `"Section 4.2"`, `"FC2023/1.23"`, `"CC1.1-POF1"`
- `title` (string, required): Short description of the clause requirement
- `coverage_pct` (integer 0-100, required): Expert assessment of how well SP 800-53 Rev 5 addresses this clause
- `rationale` (string, required): Explanation referencing specific SP 800-53 control IDs that provide coverage
- `gaps` (string, required): What SP 800-53 does NOT cover for this clause. Use empty string `""` only if truly no gaps.

Coverage percentage guidelines:
- **85-100% (Full)**: SP 800-53 comprehensively addresses the clause. Gaps are minor or negligible.
- **65-84% (Substantial)**: Well addressed with notable gaps in specific areas.
- **40-64% (Partial)**: Partially addressed. Significant areas require supplementation.
- **1-39% (Weak)**: Weakly addressed. The clause is primarily outside SP 800-53 scope.
- **0% (None)**: No SP 800-53 mapping exists.

### Step 2 — Build reverse mappings

This is the mechanical step. Read all SP 800-53 control files and invert the `compliance_mappings` to find which controls reference each clause.

1. Read `data/controls/_manifest.json` to get the list of all control files.
2. For each control file in `data/controls/`:
   - Open the JSON file
   - Check if `compliance_mappings.{framework_id}` exists (where `framework_id` matches the argument)
   - If it contains clause IDs, add `ctrl.id` to a reverse map: `clause_id -> [control_ids]`
3. Sort control IDs within each clause entry.
4. Deduplicate control IDs.

The reverse mapping lookup uses the `framework_id` as the key in `compliance_mappings`. For example, for GDPR the key is `gdpr`, for FINMA it is `finma_circular`. This key **must match** what is already in the control JSON files.

If no controls reference a clause from the definitions, that clause will have an empty `controls` array in the output (this is valid and expected for clauses outside SP 800-53 scope).

If controls reference clause IDs not in the definitions, warn the user — these clauses exist in control data but have no expert assessment.

### Step 3 — Compute statistics

From the merged clause list, compute:

```python
total = len(clauses)
pcts = [c["coverage_pct"] for c in clauses]
avg = round(sum(pcts) / total, 1) if total else 0

full_count = sum(1 for p in pcts if 85 <= p <= 100)
substantial_count = sum(1 for p in pcts if 65 <= p <= 84)
partial_count = sum(1 for p in pcts if 40 <= p <= 64)
weak_count = sum(1 for p in pcts if 1 <= p <= 39)
none_count = sum(1 for p in pcts if p == 0)
```

Band boundaries (must match `weight_scale` in output):
- Full: 85-100
- Substantial: 65-84
- Partial: 40-64
- Weak: 1-39
- None: 0

### Step 4 — Generate coverage JSON

Write to `data/framework-coverage/{framework_id_with_hyphens}.json`. The filename uses hyphens (e.g., `finma-circular.json` for `framework_id: "finma_circular"`).

The file must conform to `data/schema/framework-coverage.schema.json`. Required top-level fields:

```json
{
  "$schema": "../schema/framework-coverage.schema.json",
  "framework_id": "{framework_id}",
  "framework_name": "{framework_name}",
  "metadata": {
    "source": "SP800-53v5_Control_Mappings",
    "version": "1.0",
    "disclaimer": "Based on publicly available crosswalks and expert analysis. Validate with qualified assessors for compliance/audit use.",
    "jurisdictions": ["{jurisdiction_codes}"],
    "applicability_type": "{mandatory|voluntary|market_driven}"
  },
  "weight_scale": {
    "full":        { "min": 85, "max": 100, "label": "Fully addressed" },
    "substantial": { "min": 65, "max": 84,  "label": "Well addressed, notable gaps" },
    "partial":     { "min": 40, "max": 64,  "label": "Partially addressed" },
    "weak":        { "min": 1,  "max": 39,  "label": "Weakly addressed" },
    "none":        { "min": 0,  "max": 0,   "label": "No mapping" }
  },
  "clauses": [
    {
      "id": "clause_id",
      "title": "clause title",
      "controls": ["AC-01", "SC-13"],
      "coverage_pct": 85,
      "rationale": "...",
      "gaps": "..."
    }
  ],
  "summary": {
    "total_clauses": 42,
    "average_coverage": 72.3,
    "full_count": 10,
    "substantial_count": 15,
    "partial_count": 12,
    "weak_count": 3,
    "none_count": 2
  }
}
```

**Schema field types (from `framework-coverage.schema.json`):**
- `framework_id`: string
- `framework_name`: string
- `metadata.source`: string (required)
- `metadata.version`: string (required)
- `metadata.disclaimer`: string (required)
- `metadata.jurisdictions`: array of strings (optional but recommended)
- `metadata.applicability_type`: enum `mandatory|voluntary|market_driven` (optional but recommended)
- `weight_scale`: object with 5 required keys (`full`, `substantial`, `partial`, `weak`, `none`), each having `min` (integer), `max` (integer), `label` (string)
- `clauses[]`: array of objects, each requiring `id` (string), `title` (string), `controls` (string array), `coverage_pct` (integer 0-100), `rationale` (string), `gaps` (string)
- `summary`: object requiring `total_clauses` (integer), `average_coverage` (number), `full_count` (integer), `substantial_count` (integer), `partial_count` (integer), `weak_count` (integer), `none_count` (integer)

**Sorting**: Clauses should be sorted naturally by ID (using alphanumeric sort that handles mixed letters/digits correctly).

**For large frameworks (100+ clauses)**: Generate the file via a Python script at `scripts/generate_{framework_id}_coverage.py` to avoid hitting token limits. The script follows the established pattern:

```python
#!/usr/bin/env python3
"""Generate {framework_name} coverage analysis JSON."""

import json, os, re
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CONTROLS_DIR = SCRIPT_DIR.parent / "data" / "controls"
OUTPUT_PATH = SCRIPT_DIR.parent / "data" / "framework-coverage" / "{filename}.json"
FRAMEWORK_KEY = "{framework_id}"

CLAUSE_DEFINITIONS = [ ... ]  # All clause definitions

def natural_sort_key(s):
    return [int(p) if p.isdigit() else p.lower() for p in re.split(r'(\d+)', s)]

def build_reverse_mappings():
    with open(CONTROLS_DIR / "_manifest.json") as f:
        manifest = json.load(f)
    reverse = defaultdict(list)
    for ctrl_entry in manifest["controls"]:
        with open(CONTROLS_DIR / ctrl_entry["file"]) as f:
            ctrl = json.load(f)
        for clause_id in ctrl.get("compliance_mappings", {}).get(FRAMEWORK_KEY, []):
            reverse[clause_id].append(ctrl["id"])
    for cid in reverse:
        reverse[cid] = sorted(set(reverse[cid]))
    return dict(reverse)

def generate_coverage():
    reverse = build_reverse_mappings()
    # ... merge, compute stats, write JSON ...
```

### Step 5 — Validate

Run the JSON validator:

```bash
python3 scripts/validate_json.py 2>&1 | grep -E "{framework_id}|error|FAIL|passed"
```

Confirm the new file passes schema validation. If validation fails, fix the issue and re-validate.

Also verify:
- All control IDs in `clauses[].controls` exist in `data/controls/_manifest.json`
- All clause IDs are unique
- `summary` statistics are mathematically correct (counts add up to `total_clauses`, `average_coverage` matches)

### Step 6 — Register in website

Remind the user that the framework must be registered in the website's framework registry at `website/content/frameworks.json` if not already present. Each entry has:

```json
{
  "id": "{framework_id}",
  "slug": "{framework-id-with-hyphens}",
  "name": "{short name}",
  "fullName": "{full official name}",
  "description": "{1-2 sentence description}",
  "category": "{category}",
  "region": "{region}",
  "publisher": "{publisher}",
  "version": "{version}",
  "url": "{official_url}"
}
```

This is a separate manual step — do NOT modify `website/content/frameworks.json` as part of this skill unless the user explicitly asks.

### Step 7 — Report

Show the user:
- Output file path
- Total clauses and average coverage percentage
- Band distribution (full/substantial/partial/weak/none counts)
- Number of clauses with reverse-mapped controls vs. clauses with empty control arrays
- Any warnings (clause IDs in data but not in definitions, or vice versa)
- Reminder about website registration if needed

## Important

- Do NOT commit or push. The user decides when to commit.
- The `framework_id` (snake_case, used in control `compliance_mappings`) and the filename (hyphenated) are different forms of the same identifier. Example: `framework_id: "finma_circular"` -> filename: `finma-circular.json`.
- The `$schema` field must be `"../schema/framework-coverage.schema.json"` (relative path from the output file location).
- The `weight_scale` bands must use the exact boundaries: 85-100, 65-84, 40-64, 1-39, 0. These are hardcoded across all existing coverage files.
- Controls listed for each clause are populated from reverse mappings (Step 2), NOT from the expert rationale text. The rationale may mention controls for explanation, but the `controls` array comes strictly from what is recorded in control files' `compliance_mappings`.
- For frameworks not yet mapped in control files (no `compliance_mappings` entries), the reverse mapping step will produce empty arrays. The user must first add mappings to control files (via `scripts/add_{framework}_mappings.py` or manually), then regenerate.
