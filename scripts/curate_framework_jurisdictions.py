#!/usr/bin/env python3
"""
curate_framework_jurisdictions.py — Add jurisdiction applicability to framework-coverage files.

Adds two fields to each framework-coverage JSON's metadata block:
  - jurisdictions: array of ISO 3166-1 alpha-2 + region codes
  - applicability_type: mandatory | voluntary | market_driven

Usage:
  python3 scripts/curate_framework_jurisdictions.py          # dry run
  python3 scripts/curate_framework_jurisdictions.py --apply   # write changes

Design ref: Issue #50 — Jurisdiction Applicability for Framework Coverage
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Allowed jurisdiction codes: ISO 3166-1 alpha-2 + region supranational codes
ALLOWED_JURISDICTIONS = {
    # Supranational / regional
    "EU", "EEA", "APAC", "GLOBAL",
    # Countries
    "AE", "AU", "BH", "BE", "BR", "CA", "CH", "CN", "DE", "FR",
    "GB", "GH", "HK", "IN", "IL", "JP", "MY", "NG", "NL", "QA",
    "SA", "SG", "TH", "US", "ZA",
}

ALLOWED_APPLICABILITY = {"mandatory", "voluntary", "market_driven"}

# Expert-curated jurisdiction mappings for all 79 frameworks.
# Format: framework_id -> (jurisdictions[], applicability_type)
FRAMEWORK_JURISDICTIONS = {
    # ── EU/EEA mandatory ─────────────────────────────────────────────
    "gdpr":               (["EU", "EEA"],           "mandatory"),
    "dora":               (["EU"],                   "mandatory"),
    "nis2":               (["EU"],                   "mandatory"),
    "cra":                (["EU"],                   "mandatory"),
    "eba-ict":            (["EU"],                   "mandatory"),
    "ecb-croe":           (["EU"],                   "mandatory"),
    "solvency-ii":        (["EU"],                   "mandatory"),
    "tiber-eu":           (["EU"],                   "mandatory"),
    "bio2":               (["NL"],                   "mandatory"),
    "dnb-good-practice":  (["NL"],                   "mandatory"),
    "cbe-csf":            (["BE"],                   "mandatory"),

    # ── UK mandatory ─────────────────────────────────────────────────
    "cbest":              (["GB"],                   "mandatory"),
    "fca-sysc-13":        (["GB"],                   "mandatory"),
    "pra-op-resilience":  (["GB"],                   "mandatory"),
    "pra-ss1-23":         (["GB"],                   "mandatory"),
    "nhs-dspt":           (["GB"],                   "mandatory"),

    # ── Europe country-specific mandatory ────────────────────────────
    "anssi":              (["FR"],                   "mandatory"),
    "bsi-grundschutz":    (["DE"],                   "mandatory"),
    "finma-circular":     (["CH"],                   "mandatory"),

    # ── US mandatory ─────────────────────────────────────────────────
    "nerc-cip":           (["US"],                   "mandatory"),
    "ferc-cip":           (["US"],                   "mandatory"),
    "cmmc-2":             (["US"],                   "mandatory"),
    "hipaa-sr":           (["US"],                   "mandatory"),
    "nydfs-500":          (["US"],                   "mandatory"),
    "ffiec-is":           (["US"],                   "mandatory"),
    "fda-21-cfr-11":      (["US"],                   "mandatory"),
    "fda-cyber":          (["US"],                   "mandatory"),
    "nrc-73-54":          (["US"],                   "mandatory"),
    "awia":               (["US"],                   "mandatory"),
    "tsa-psd":            (["US"],                   "mandatory"),
    "fips-140":           (["US"],                   "mandatory"),
    "doe-c2m2":           (["US"],                   "mandatory"),
    "naic-ds":            (["US"],                   "mandatory"),

    # ── Americas (non-US) mandatory ──────────────────────────────────
    "lgpd-bcb":           (["BR"],                   "mandatory"),
    "osfi-b13":           (["CA"],                   "mandatory"),

    # ── Asia-Pacific mandatory ───────────────────────────────────────
    "mas-trm":            (["SG"],                   "mandatory"),
    "hkma-tme1":          (["HK"],                   "mandatory"),
    "apra-cps-234":       (["AU"],                   "mandatory"),
    "asd-essential-eight":(["AU"],                   "mandatory"),
    "rbi-csf":            (["IN"],                   "mandatory"),
    "sebi-cscrf":         (["IN"],                   "mandatory"),
    "bot-cyber":          (["TH"],                   "mandatory"),
    "fisc":               (["JP"],                   "mandatory"),
    "mlps-2":             (["CN"],                   "mandatory"),
    "bom-ctrm":           (["MY"],                   "mandatory"),

    # ── Middle East mandatory ────────────────────────────────────────
    "nca-ecc":            (["SA"],                   "mandatory"),
    "sama-csf":           (["SA"],                   "mandatory"),
    "cbuae":              (["AE"],                   "mandatory"),
    "uae-ia":             (["AE"],                   "mandatory"),
    "qatar-nia":          (["QA"],                   "mandatory"),
    "cbb-tm":             (["BH"],                   "mandatory"),

    # ── Africa mandatory ─────────────────────────────────────────────
    "cbn-csf":            (["NG"],                   "mandatory"),
    "bog-cisd":           (["GH"],                   "mandatory"),
    "popia":              (["ZA"],                   "mandatory"),
    "sa-js2":             (["ZA"],                   "mandatory"),

    # ── Global voluntary (standards & best practices) ────────────────
    "iso-27001-2022":     (["GLOBAL"],               "voluntary"),
    "iso-27002-2022":     (["GLOBAL"],               "voluntary"),
    "iso-27799":          (["GLOBAL"],               "voluntary"),
    "iso-42001-2023":     (["GLOBAL"],               "voluntary"),
    "nist-csf-2":         (["GLOBAL"],               "voluntary"),
    "cis-controls-v8":    (["GLOBAL"],               "voluntary"),
    "cobit-2019":         (["GLOBAL"],               "voluntary"),
    "common-criteria":    (["GLOBAL"],               "voluntary"),
    "hitrust-csf":        (["GLOBAL"],               "voluntary"),
    "isae-3402":          (["GLOBAL"],               "voluntary"),
    "soc2-tsc":           (["GLOBAL"],               "voluntary"),
    "finos-ccc":          (["GLOBAL"],               "voluntary"),

    # ── Global market-driven ─────────────────────────────────────────
    "pci-dss-v4":         (["GLOBAL"],               "market_driven"),
    "pci-hsm":            (["GLOBAL"],               "market_driven"),
    "pci-pts":            (["GLOBAL"],               "market_driven"),
    "swift-cscf":         (["GLOBAL"],               "market_driven"),
    "lloyds-ms":          (["GLOBAL"],               "market_driven"),

    # ── Global sector-specific (mandatory in applicable sector) ──────
    "iaea-nss":           (["GLOBAL"],               "mandatory"),
    "iec-62443":          (["GLOBAL"],               "mandatory"),
    "ieee-1686":          (["GLOBAL"],               "mandatory"),
    "api-1164":           (["GLOBAL", "US"],          "mandatory"),

    # ── International financial standards (voluntary/advisory) ───────
    "bcbs-239":           (["GLOBAL"],               "mandatory"),
    "cpmi-pfmi":          (["GLOBAL"],               "mandatory"),
    "iosco-cyber":        (["GLOBAL"],               "voluntary"),
}


def validate_mappings():
    """Validate all mappings use allowed jurisdiction codes and applicability types."""
    errors = []
    for fid, (jurisdictions, app_type) in FRAMEWORK_JURISDICTIONS.items():
        for j in jurisdictions:
            if j not in ALLOWED_JURISDICTIONS:
                errors.append(f"{fid}: unknown jurisdiction code '{j}'")
        if app_type not in ALLOWED_APPLICABILITY:
            errors.append(f"{fid}: unknown applicability_type '{app_type}'")
    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Add jurisdiction applicability to framework-coverage files"
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Write changes to files (default: dry run)"
    )
    args = parser.parse_args()

    # Validate mappings first
    errors = validate_mappings()
    if errors:
        print("Mapping validation errors:")
        for e in errors:
            print(f"  ERROR: {e}")
        sys.exit(1)

    coverage_dir = Path(__file__).resolve().parent.parent / "data" / "framework-coverage"
    if not coverage_dir.is_dir():
        print(f"ERROR: Coverage directory not found: {coverage_dir}")
        sys.exit(1)

    # Discover all framework-coverage JSON files
    json_files = sorted(coverage_dir.glob("*.json"))
    file_ids = {f.stem: f for f in json_files}

    # Check for unmapped files
    unmapped = set(file_ids.keys()) - set(FRAMEWORK_JURISDICTIONS.keys())
    if unmapped:
        print(f"ERROR: {len(unmapped)} framework files have no mapping:")
        for u in sorted(unmapped):
            print(f"  - {u}")
        sys.exit(1)

    # Check for mappings without files
    extra = set(FRAMEWORK_JURISDICTIONS.keys()) - set(file_ids.keys())
    if extra:
        print(f"WARNING: {len(extra)} mappings have no matching file:")
        for e in sorted(extra):
            print(f"  - {e}")

    changed = 0
    unchanged = 0

    for fid in sorted(file_ids.keys()):
        filepath = file_ids[fid]
        jurisdictions, app_type = FRAMEWORK_JURISDICTIONS[fid]

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        metadata = data.get("metadata", {})
        current_j = metadata.get("jurisdictions")
        current_a = metadata.get("applicability_type")

        if current_j == jurisdictions and current_a == app_type:
            unchanged += 1
            continue

        changed += 1
        action = "UPDATE" if current_j is not None else "ADD"
        print(f"  {action}: {fid}")
        if current_j is not None and current_j != jurisdictions:
            print(f"    jurisdictions: {current_j} -> {jurisdictions}")
        elif current_j is None:
            print(f"    jurisdictions: {jurisdictions}")
        if current_a is not None and current_a != app_type:
            print(f"    applicability_type: {current_a} -> {app_type}")
        elif current_a is None:
            print(f"    applicability_type: {app_type}")

        if args.apply:
            metadata["jurisdictions"] = jurisdictions
            metadata["applicability_type"] = app_type
            data["metadata"] = metadata

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")

    print()
    print(f"Summary: {changed} changed, {unchanged} unchanged, {len(file_ids)} total")
    if not args.apply and changed > 0:
        print("Dry run — re-run with --apply to write changes.")


if __name__ == "__main__":
    main()
