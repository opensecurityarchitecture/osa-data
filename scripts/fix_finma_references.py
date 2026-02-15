#!/usr/bin/env python3
"""
Fix FINMA Circular 2023/1 control references.

1. Remove invalid margin numbers > 114 (document only has 114 margins)
2. Replace FC2023/1.{mn} format with {chapter}({mn}) format

Usage:
    python3 scripts/fix_finma_references.py
"""

import json
import os
import re
import sys

# FINMA Circular 2023/1 margin-to-chapter mapping
MARGIN_TO_CHAPTER = {}

def _set_range(start, end, chapter):
    for mn in range(start, end + 1):
        MARGIN_TO_CHAPTER[mn] = chapter

_set_range(1, 2, "I")
_set_range(3, 18, "II")
_set_range(19, 21, "III")
_set_range(22, 46, "IV.A")
_set_range(47, 49, "IV.B.a")
_set_range(50, 52, "IV.B.b")
_set_range(53, 57, "IV.B.c")
_set_range(58, 60, "IV.B.d")
_set_range(61, 70, "IV.C")
_set_range(71, 82, "IV.D")
_set_range(83, 96, "IV.E")
_set_range(97, 100, "IV.F")
_set_range(101, 111, "V")
_set_range(112, 112, "VI")
_set_range(113, 113, "VII.A")
_set_range(114, 114, "VII.B")

MAX_MARGIN = 114

CONTROLS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "controls")
FC_PATTERN = re.compile(r"^FC2023/1\.(\d+)$")


def process_file(filepath):
    """Process a single control JSON file. Returns (changed, removed_count, converted_count)."""
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    data = json.loads(raw)

    mappings = data.get("compliance_mappings", {})
    finma_refs = mappings.get("finma_circular")

    if finma_refs is None:
        return False, 0, 0

    new_refs = []
    removed = 0
    converted = 0

    for ref in finma_refs:
        match = FC_PATTERN.match(ref)
        if not match:
            # Keep non-matching refs as-is
            new_refs.append(ref)
            continue

        mn = int(match.group(1))

        if mn > MAX_MARGIN:
            removed += 1
            continue

        chapter = MARGIN_TO_CHAPTER.get(mn)
        if chapter is None:
            print(f"  WARNING: No chapter mapping for margin {mn} in {os.path.basename(filepath)}")
            new_refs.append(ref)
            continue

        new_ref = f"{chapter}({mn})"
        new_refs.append(new_ref)
        converted += 1

    if removed == 0 and converted == 0:
        return False, 0, 0

    # Replace only the finma_circular value using string manipulation
    # to preserve the rest of the file exactly as-is
    mappings["finma_circular"] = new_refs
    data["compliance_mappings"] = mappings

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return True, removed, converted


def main():
    if not os.path.isdir(CONTROLS_DIR):
        print(f"ERROR: Controls directory not found: {CONTROLS_DIR}")
        sys.exit(1)

    json_files = sorted(
        f for f in os.listdir(CONTROLS_DIR)
        if f.endswith(".json") and not f.startswith("_")
    )

    total_changed = 0
    total_removed = 0
    total_converted = 0

    for filename in json_files:
        filepath = os.path.join(CONTROLS_DIR, filename)
        changed, removed, converted = process_file(filepath)

        if changed:
            total_changed += 1
            total_removed += removed
            total_converted += converted
            parts = []
            if converted:
                parts.append(f"{converted} converted")
            if removed:
                parts.append(f"{removed} removed")
            print(f"  {filename}: {', '.join(parts)}")

    print(f"\nDone: {total_changed} files modified, {total_converted} refs converted, {total_removed} refs removed")


if __name__ == "__main__":
    main()
