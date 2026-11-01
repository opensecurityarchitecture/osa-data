#!/usr/bin/env python3
"""
Validate JSON files against their schemas.
"""

import json
import re
import sys
from pathlib import Path

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("Warning: jsonschema not installed, skipping schema validation")

DATA_DIR = Path(__file__).parent.parent / "data"


def validate_json_syntax(filepath: Path) -> bool:
    """Validate JSON syntax."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except json.JSONDecodeError as e:
        print(f"  FAIL: {filepath.name} - JSON syntax error: {e}")
        return False


def validate_against_schema(data: dict, schema: dict, filepath: Path) -> bool:
    """Validate data against JSON schema."""
    if not HAS_JSONSCHEMA:
        return True

    try:
        jsonschema.validate(data, schema)
        return True
    except jsonschema.ValidationError as e:
        print(f"  FAIL: {filepath.name} - Schema validation error: {e.message}")
        return False


def load_schema(schema_path: Path) -> dict:
    """Load a JSON schema file."""
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def consistency_checks() -> list:
    """Things written in two places must agree. Each check here caught a real slip
    (1 November 2026): a pattern title that differed from the manifest's, manifest
    and description counts that no longer matched the control list, and mappings
    whose coverage file and control files gave different answers."""
    problems = []

    # Patterns against the pattern manifest, and the counts their descriptions state
    stated_count = re.compile(r'(?<![\d-])(\d+) NIST (?:SP )?800-53 controls')
    manifest = json.load(open(DATA_DIR / "patterns" / "_manifest.json", encoding="utf-8"))
    for entry in manifest.get("patterns", []):
        path = DATA_DIR / "patterns" / entry["file"]
        if not path.exists():
            problems.append(f"{entry['id']}: manifest names {entry['file']}, which does not exist")
            continue
        pattern = json.load(open(path, encoding="utf-8"))
        listed = len(pattern.get("controls", []))
        if pattern.get("title") != entry.get("title"):
            problems.append(f"{entry['id']}: title {pattern.get('title')!r} differs from the manifest's {entry.get('title')!r}")
        if entry.get("controls") != listed:
            problems.append(f"{entry['id']}: the manifest says {entry.get('controls')} controls, the pattern lists {listed}")
        for found in stated_count.finditer(pattern.get("description", "")):
            if int(found.group(1)) != listed:
                problems.append(f"{entry['id']}: the description says {found.group(0)!r}, the pattern lists {listed}")

    # relatedPatternNames are copies of the related patterns' titles, in the same order
    titles = {}
    for entry in manifest.get("patterns", []):
        path = DATA_DIR / "patterns" / entry["file"]
        if path.exists():
            titles[entry["id"]] = json.load(open(path, encoding="utf-8")).get("title")
    for entry in manifest.get("patterns", []):
        path = DATA_DIR / "patterns" / entry["file"]
        if not path.exists():
            continue
        pattern = json.load(open(path, encoding="utf-8"))
        ids, names = pattern.get("relatedPatterns", []), pattern.get("relatedPatternNames", [])
        if len(ids) != len(names):
            problems.append(f"{entry['id']}: {len(ids)} relatedPatterns but {len(names)} relatedPatternNames")
            continue
        for rid, name in zip(ids, names):
            if rid not in titles:
                problems.append(f"{entry['id']}: related pattern {rid} is not in the manifest")
            elif name != titles[rid]:
                problems.append(f"{entry['id']}: names {rid} {name!r}; its title is {titles[rid]!r}")

    # Quality fields (quality dimensions deck, November 2026): the catalogue ids, building
    # blocks and threat ids they name exist. The schema checks their form, this their targets.
    attack_ids = {t["id"] for t in json.load(open(DATA_DIR / "mitre-attack" / "enterprise-attack.json", encoding="utf-8")).get("techniques", [])}
    for entry in manifest.get("patterns", []):
        path = DATA_DIR / "patterns" / entry["file"]
        if not path.exists():
            continue
        pattern = json.load(open(path, encoding="utf-8"))
        threat_ids = {t.get("id") for t in pattern.get("threats", [])}
        for threat in pattern.get("threats", []):
            for ref in threat.get("catalogueRefs", []):
                if ref.get("catalogue") == "mitre-attack" and ref.get("id") not in attack_ids:
                    problems.append(f"{entry['id']}: threat {threat.get('id')} names ATT&CK {ref.get('id')}, which is not in enterprise-attack.json")
        for pre in pattern.get("content", {}).get("preconditions", []):
            if pre.get("pattern") and pre["pattern"] not in titles:
                problems.append(f"{entry['id']}: a precondition names building block {pre['pattern']}, which is not in the manifest")
            if pre.get("pattern") == entry["id"]:
                problems.append(f"{entry['id']}: a precondition names the pattern itself as its building block")
            for tid in pre.get("removesThreats", []):
                if tid not in threat_ids:
                    problems.append(f"{entry['id']}: a precondition removes threat {tid}, which the pattern does not list")

    # Each mapping: the coverage file's pairs and the control files' pairs are the same
    control_manifest = json.load(open(DATA_DIR / "controls" / "_manifest.json", encoding="utf-8"))
    mappings = {}
    for entry in control_manifest.get("controls", []):
        control = json.load(open(DATA_DIR / "controls" / entry["file"], encoding="utf-8"))
        mappings[entry["id"]] = control.get("compliance_mappings", {})
    for path in sorted((DATA_DIR / "framework-coverage").glob("*.json")):
        coverage = json.load(open(path, encoding="utf-8"))
        framework = coverage.get("framework_id")
        if not framework:
            problems.append(f"{path.name}: no framework_id")
            continue
        coverage_pairs = {(cid, clause["id"]) for clause in coverage.get("clauses", []) for cid in clause.get("controls", [])}
        unknown = sorted({cid for cid, _ in coverage_pairs if cid not in mappings})
        if unknown:
            problems.append(f"{path.name}: names controls that are not in the catalogue: {', '.join(unknown)}")
        control_pairs = {(cid, clause) for cid, cm in mappings.items() for clause in cm.get(framework, [])}
        only_coverage, only_controls = coverage_pairs - control_pairs, control_pairs - coverage_pairs
        if only_coverage or only_controls:
            sample = ", ".join(f"{c} {cl}" for c, cl in sorted(only_coverage | only_controls)[:4])
            problems.append(f"{path.name}: {len(only_coverage)} pairs only in the coverage file and {len(only_controls)} "
                            f"only in the control files (such as {sample}); write the control side from the coverage "
                            f"file, as the add-framework-mapping skill shows")
    return problems


def main():
    """Validate all JSON files."""
    print("Validating OSA JSON data files\n")

    errors = 0
    validated = 0

    # Load schemas
    pattern_schema = None
    control_schema = None

    pattern_schema_path = DATA_DIR / "schema" / "pattern.schema.json"
    control_schema_path = DATA_DIR / "schema" / "control.schema.json"

    if pattern_schema_path.exists():
        pattern_schema = load_schema(pattern_schema_path)
    if control_schema_path.exists():
        control_schema = load_schema(control_schema_path)

    # Validate patterns
    print("Patterns:")
    patterns_dir = DATA_DIR / "patterns"
    for filepath in sorted(patterns_dir.glob("*.json")):
        if filepath.name.startswith('_'):
            continue

        if not validate_json_syntax(filepath):
            errors += 1
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if pattern_schema and HAS_JSONSCHEMA:
            if not validate_against_schema(data, pattern_schema, filepath):
                errors += 1
                continue

        validated += 1
        print(f"  OK: {filepath.name}")

    # Validate controls
    print("\nControls:")
    controls_dir = DATA_DIR / "controls"
    for filepath in sorted(controls_dir.glob("*.json")):
        if filepath.name.startswith('_'):
            continue

        if not validate_json_syntax(filepath):
            errors += 1
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if control_schema and HAS_JSONSCHEMA:
            if not validate_against_schema(data, control_schema, filepath):
                errors += 1
                continue

        validated += 1
        print(f"  OK: {filepath.name}")

    # What NIST says about a control is written in one place, data/nist/, and
    # copied into the control files, the control manifest and the patterns.
    # sync_nist.py keeps the copies in step. Here it only reports.
    if (DATA_DIR / "nist" / "sp800-53-rev5.json").exists():
        sys.path.insert(0, str(Path(__file__).parent))
        import sync_nist
        print("\nNIST SP 800-53 (" + ", ".join(sync_nist.MANAGED) + "):")
        differences = sync_nist.sync(write=False) + sync_nist.MISSING
        for line in differences:
            print(f"  FAIL: {line}")
        if differences:
            print("  Run: python3 scripts/sync_nist.py")
        else:
            print("  OK: control files, manifest and patterns agree with data/nist/sp800-53-rev5.json")
        errors += len(differences)

    # Validate framework-coverage files
    fc_dir = DATA_DIR / "framework-coverage"
    fc_schema_path = DATA_DIR / "schema" / "framework-coverage.schema.json"
    if fc_dir.exists() and fc_schema_path.exists():
        fc_schema = load_schema(fc_schema_path)
        print("\nFramework Coverage:")
        for filepath in sorted(fc_dir.glob("*.json")):
            if not validate_json_syntax(filepath):
                errors += 1
                continue
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if HAS_JSONSCHEMA:
                if not validate_against_schema(data, fc_schema, filepath):
                    errors += 1
                    continue
            validated += 1
            print(f"  OK: {filepath.name} ({len(data.get('clauses', []))} clauses, {data.get('summary', {}).get('average_coverage', 0)}%)")

    # Patterns against their manifest, and each mapping's two sides
    if errors == 0:
        print("\nConsistency:")
        problems = consistency_checks()
        for line in problems:
            print(f"  FAIL: {line}")
        if not problems:
            print("  OK: patterns match their manifest, and every mapping's coverage file matches the control files")
        errors += len(problems)

    # Summary
    print(f"\nValidation complete: {validated} files OK, {errors} errors")

    if errors > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
