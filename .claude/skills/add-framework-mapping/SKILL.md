---
name: add-framework-mapping
description: Add a new compliance framework mapping to NIST 800-53 controls — replaces per-framework scripts
---

# Add Framework Mapping

Add a new compliance framework's clause-to-control mappings into the `compliance_mappings` object of every NIST 800-53 Rev 5 control file. This skill replaces the single-purpose Python scripts (e.g. `add_ccm_mappings.py`, `add_gdpr_mappings.py`) with a repeatable, interactive process.

## Arguments

The user should provide:
- **Framework name** (required) — human-readable name, e.g. "EU AI Act", "NIST CSF 2.0"
- **framework_key** (required) — snake_case identifier used as the JSON key inside `compliance_mappings`, e.g. `eu_ai_act`, `nist_csf_2`. Must match the pattern `^[a-z][a-z0-9_]+$` (schema-enforced).
- **Source document or URL** (optional) — authoritative reference for the framework specification. Used to derive or verify mappings.

## Instructions

### Step 1 — Define the mappings

The goal is to produce a MAPPINGS dict: a mapping from NIST 800-53 control IDs to arrays of framework clause references (strings).

**The dict shape is:**
```
{
  "AC-01": ["Clause-1", "Clause-2"],
  "SC-07": ["Sec.4.1", "Sec.4.3"],
  ...
}
```

Keys are NIST control IDs (e.g. `AC-01`, `SC-13`). Values are arrays of framework-specific clause/section/article references as strings.

**How to populate the mappings — three paths:**

1. **User provides raw mappings** — use them directly after validation (Step 2).
2. **User provides a framework specification or document** — analyse the framework's requirements and propose mappings to NIST 800-53 controls. Present the proposed mappings to the user for review before proceeding.
3. **User provides a forward-mapping coverage file** (from `data/framework-coverage/`) — invert it. The coverage files map framework clauses to NIST controls. Read the file, then invert to produce NIST-control-to-clause-references. Example: if clause `"DSP-01"` maps to controls `["AC-01", "PT-01"]`, then `AC-01` gets `"DSP-01"` and `PT-01` gets `"DSP-01"`.

**Important:** Controls NOT in the mappings dict will receive an empty array `[]` for this framework_key. This is the established convention — every control file gets the key, even if the array is empty.

### Step 2 — Validate inputs

**2a. Load valid control IDs:**
Read `data/controls/_manifest.json`. Parse `data.controls[]` and extract every `id` field. There are 315 controls across 20 families (AC, AT, AU, CA, CM, CP, IA, IR, MA, MP, PE, PL, PM, PS, PT, RA, SA, SC, SI, SR).

**2b. Check every control ID in the mappings exists:**
Compare every key in the MAPPINGS dict against the manifest control IDs. Flag any unknown control IDs and ask the user to correct them before proceeding. Common mistakes:
- Missing zero-padding: `AC-1` should be `AC-01`
- Using enhancement notation: `AC-02(1)` — the base control files don't have enhancement suffixes; use the base ID `AC-02`
- Typos in family prefix: `AS-01` instead of `SA-01`

**2c. Check the framework_key is not already present:**
Read 2-3 control files (e.g. `AC-01.json`, `SC-07.json`, `SI-04.json`) and check whether `compliance_mappings` already contains the `framework_key`. If it does, warn the user that this will OVERWRITE existing mappings and confirm they want to proceed.

### Step 3 — Apply mappings

**If fewer than ~50 control files need the framework_key added (typical case):**

For EVERY control in the manifest (all 315), use the Edit tool:
1. Read the control JSON file from `data/controls/{entry.file}`
2. Locate the `compliance_mappings` object
3. Add `"framework_key": [...]` at the END of the `compliance_mappings` object (after the last existing key)
4. The value is the clause references array from the MAPPINGS dict, or `[]` if this control has no mappings for this framework

**CRITICAL — use the Edit tool correctly:**
- The `old_string` must match the last key-value pair in `compliance_mappings` plus the closing brace, so you can insert the new key before the closing brace
- Preserve all existing keys — you are only ADDING one new key
- Maintain `indent=2` formatting and ensure the file ends with a trailing newline
- Each array value is a JSON array of strings: `["Clause-1", "Clause-2"]` or `[]`

**If more than ~50 control files need updating (almost always the case for a new framework):**

Write a temporary Python script to `/tmp/apply_framework_mapping.py` and execute it via Bash. This avoids token-limit issues from 315 individual Edit calls.

The script pattern (derived from the existing mapping scripts):

```python
#!/usr/bin/env python3
"""Apply {framework_name} compliance mappings to NIST 800-53 control files."""

import json
import os
from collections import OrderedDict

CONTROLS_DIR = "/Users/russellwing/osa-workspace/data/controls"

FRAMEWORK_KEY = "{framework_key}"

# NIST control ID -> list of framework clause references
MAPPINGS = {
    "AC-01": ["..."],
    # ... all mappings ...
}


def main():
    manifest_path = os.path.join(CONTROLS_DIR, "_manifest.json")
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    total_refs = 0
    controls_updated = 0
    controls_empty = 0
    family_counts = {}

    for entry in manifest["controls"]:
        control_id = entry["id"]
        filepath = os.path.join(CONTROLS_DIR, entry["file"])

        if not os.path.exists(filepath):
            print(f"  WARNING: File not found: {filepath}")
            continue

        with open(filepath, "r") as f:
            data = json.load(f, object_pairs_hook=OrderedDict)

        if "compliance_mappings" not in data:
            print(f"  WARNING: {control_id} has no compliance_mappings — skipping")
            continue

        refs = MAPPINGS.get(control_id, [])

        # Rebuild compliance_mappings with new key at end
        cm = data["compliance_mappings"]
        new_cm = OrderedDict()
        for key, val in cm.items():
            if key != FRAMEWORK_KEY:
                new_cm[key] = val
        new_cm[FRAMEWORK_KEY] = refs
        data["compliance_mappings"] = new_cm

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

        ref_count = len(refs)
        total_refs += ref_count
        if ref_count > 0:
            controls_updated += 1
            family = control_id.split("-")[0]
            family_counts[family] = family_counts.get(family, 0) + 1
        else:
            controls_empty += 1

    print(f"\n{'='*60}")
    print(f"{FRAMEWORK_KEY} Compliance Mapping Summary")
    print(f"{'='*60}")
    print(f"Total controls processed:       {len(manifest['controls'])}")
    print(f"Controls with mappings:         {controls_updated}")
    print(f"Controls with empty mappings:   {controls_empty}")
    print(f"Total clause references:        {total_refs}")
    print(f"Coverage:                       {controls_updated}/{len(manifest['controls'])} ({100*controls_updated/len(manifest['controls']):.1f}%)")
    print(f"{'='*60}")
    print(f"\nBy NIST family:")
    for fam, count in sorted(family_counts.items()):
        print(f"  {fam}: {count}")


if __name__ == "__main__":
    main()
```

Key details for the script:
- Use `OrderedDict` with `object_pairs_hook` to preserve JSON key order
- Always pop the framework_key first (idempotent re-run) then add at end
- Write with `indent=2` and `ensure_ascii=False`
- Always append `"\n"` after `json.dump` for trailing newline
- Extract family from control ID via `control_id.split("-")[0]`

### Step 4 — Generate summary statistics

After applying, report:
- **Total controls mapped** (those with non-empty arrays)
- **Total clause references added** (sum of all array lengths)
- **Breakdown by NIST control family** (AC: N, AT: N, AU: N, etc.) — only families with mappings
- **Coverage percentage**: controls with mappings / 315 total
- **Top-referenced clauses** (optional): if useful, show which framework clauses appear most frequently

### Step 5 — Validate

Run:
```bash
python3 /Users/russellwing/osa-workspace/scripts/validate_json.py
```

Confirm zero errors. If validation fails:
1. Read the error messages carefully
2. The most common issue is invalid JSON syntax from a bad edit — check the failing file
3. The `compliance_mappings` schema enforces `patternProperties: "^[a-z][a-z0-9_]+$"` — ensure the framework_key matches
4. Fix and re-run validation until clean

### Step 6 — Report to user

Present:
- Framework name and key
- Number of controls updated (with mappings) vs total
- Coverage percentage
- Family breakdown
- Reminder: **Do NOT commit or push** — the user decides when

## Important notes

- **Do NOT commit or push.** The user will decide when to commit changes.
- **Do NOT create a separate permanent Python script** in `scripts/`. This skill IS the replacement for those scripts. If a temp script is needed for bulk application, write it to `/tmp/` and delete it after use.
- **Preserve existing compliance_mappings.** Only add or update the single new framework_key. Never remove or modify other keys.
- **Every control gets the key.** Even controls with no mappings for this framework get an empty array `[]`. This is the established convention across all 66+ existing framework mappings.
- **Control ID format:** Always `XX-NN` with zero-padded two-digit number (e.g. `AC-01` not `AC-1`). The valid families are: AC, AT, AU, CA, CM, CP, IA, IR, MA, MP, PE, PL, PM, PS, PT, RA, SA, SC, SI, SR.
- **Clause references are strings.** The array values can be any format appropriate to the framework (e.g. `"Art.32(1)(a)"` for GDPR, `"DSP-01"` for CCM, `"CIP-003-9"` for NERC CIP). Be consistent within a framework.
- **JSON formatting:** `indent=2`, trailing newline, `ensure_ascii=False`. This matches all existing control files.
- **Idempotent re-runs:** The script pattern removes the framework_key before re-adding it, so running twice produces the same result.
- **The manifest is at** `data/controls/_manifest.json` — it contains `controls[]` with `id`, `name`, `family`, `family_name`, `file` for each of the 315 controls.
