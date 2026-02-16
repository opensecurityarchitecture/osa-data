#!/usr/bin/env python3
"""
Validate JSON files against their schemas.
"""

import json
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

    # Validate ATT&CK data
    attack_dir = DATA_DIR / "attack"
    if attack_dir.exists():
        print("\nATT&CK:")
        attack_catalog_schema_path = DATA_DIR / "schema" / "attack-technique-catalog.schema.json"
        attack_metadata_schema_path = DATA_DIR / "schema" / "attack-metadata.schema.json"

        attack_catalog_schema = load_schema(attack_catalog_schema_path) if attack_catalog_schema_path.exists() else None
        attack_metadata_schema = load_schema(attack_metadata_schema_path) if attack_metadata_schema_path.exists() else None

        catalog_path = attack_dir / "technique-catalog.json"
        if catalog_path.exists():
            if not validate_json_syntax(catalog_path):
                errors += 1
            else:
                with open(catalog_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if attack_catalog_schema and HAS_JSONSCHEMA:
                    if not validate_against_schema(data, attack_catalog_schema, catalog_path):
                        errors += 1
                    else:
                        validated += 1
                        print(f"  OK: {catalog_path.name} ({len(data)} techniques)")
                else:
                    validated += 1
                    print(f"  OK: {catalog_path.name}")

        metadata_path = attack_dir / "metadata.json"
        if metadata_path.exists():
            if not validate_json_syntax(metadata_path):
                errors += 1
            else:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if attack_metadata_schema and HAS_JSONSCHEMA:
                    if not validate_against_schema(data, attack_metadata_schema, metadata_path):
                        errors += 1
                    else:
                        validated += 1
                        print(f"  OK: {metadata_path.name}")
                else:
                    validated += 1
                    print(f"  OK: {metadata_path.name}")

        actor_catalog_schema_path = DATA_DIR / "schema" / "attack-actor-catalog.schema.json"
        actor_catalog_schema = load_schema(actor_catalog_schema_path) if actor_catalog_schema_path.exists() else None

        actor_path = attack_dir / "actor-catalog.json"
        if actor_path.exists():
            if not validate_json_syntax(actor_path):
                errors += 1
            else:
                with open(actor_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if actor_catalog_schema and HAS_JSONSCHEMA:
                    if not validate_against_schema(data, actor_catalog_schema, actor_path):
                        errors += 1
                    else:
                        validated += 1
                        print(f"  OK: {actor_path.name} ({len(data)} actors)")
                else:
                    validated += 1
                    print(f"  OK: {actor_path.name}")

    # Validate TPCE process capability catalog
    tpce_path = attack_dir / "process-capability-catalog.json"
    if tpce_path.exists():
        print("\nTPCE Process Capabilities:")
        if not validate_json_syntax(tpce_path):
            errors += 1
        else:
            with open(tpce_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            tpce_errors = 0
            for cap_id, cap in data.items():
                required = ['id', 'name', 'family', 'family_name', 'description', 'controlRefs', 'cisSafeguards', 'attackMitigations']
                missing = [r for r in required if r not in cap]
                if missing:
                    print(f"  FAIL: {cap_id} missing fields: {missing}")
                    tpce_errors += 1
                if cap.get('id') != cap_id:
                    print(f"  FAIL: {cap_id} id mismatch: {cap.get('id')}")
                    tpce_errors += 1
            if tpce_errors:
                errors += tpce_errors
            else:
                validated += 1
                print(f"  OK: {tpce_path.name} ({len(data)} process capabilities)")

    # Validate TTCE technology capability catalog
    ttce_path = attack_dir / "technology-capability-catalog.json"
    if ttce_path.exists():
        print("\nTTCE Technology Capabilities:")
        if not validate_json_syntax(ttce_path):
            errors += 1
        else:
            with open(ttce_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            ttce_errors = 0
            total_caps = 0
            for cls_id, cls in data.items():
                required = ['id', 'name', 'category', 'category_name', 'description', 'controlRefs', 'cisSafeguards', 'attackMitigations', 'capabilities']
                missing = [r for r in required if r not in cls]
                if missing:
                    print(f"  FAIL: {cls_id} missing fields: {missing}")
                    ttce_errors += 1
                if cls.get('id') != cls_id:
                    print(f"  FAIL: {cls_id} id mismatch: {cls.get('id')}")
                    ttce_errors += 1
                for cap in cls.get('capabilities', []):
                    cap_required = ['id', 'name', 'd3fendTechnique', 'tier']
                    cap_missing = [r for r in cap_required if r not in cap]
                    if cap_missing:
                        print(f"  FAIL: {cap.get('id', '?')} missing fields: {cap_missing}")
                        ttce_errors += 1
                    if cap.get('tier') not in ('core', 'extended'):
                        print(f"  FAIL: {cap.get('id', '?')} invalid tier: {cap.get('tier')}")
                        ttce_errors += 1
                    total_caps += 1
            if ttce_errors:
                errors += ttce_errors
            else:
                validated += 1
                print(f"  OK: {ttce_path.name} ({len(data)} classes, {total_caps} capabilities)")

    # Validate THFM human factors catalog
    thfm_path = attack_dir / "human-factors-catalog.json"
    if thfm_path.exists():
        print("\nTHFM Human Factors:")
        if not validate_json_syntax(thfm_path):
            errors += 1
        else:
            with open(thfm_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            thfm_errors = 0
            cialdini_count = 0
            insider_count = 0
            total_edges = 0
            for hf_id, hf in data.items():
                required = ['id', 'name', 'category', 'category_name', 'description', 'cialdiniPrinciple', 'exploitedBy', 'controlRefs', 'insiderStage']
                missing = [r for r in required if r not in hf]
                if missing:
                    print(f"  FAIL: {hf_id} missing fields: {missing}")
                    thfm_errors += 1
                if hf.get('id') != hf_id:
                    print(f"  FAIL: {hf_id} id mismatch: {hf.get('id')}")
                    thfm_errors += 1
                for eb in hf.get('exploitedBy', []):
                    eb_required = ['technique', 'rationale']
                    eb_missing = [r for r in eb_required if r not in eb]
                    if eb_missing:
                        print(f"  FAIL: {hf_id} exploitedBy entry missing fields: {eb_missing}")
                        thfm_errors += 1
                    total_edges += 1
                if hf.get('cialdiniPrinciple'):
                    cialdini_count += 1
                if hf.get('category') == 'IN':
                    insider_count += 1
            if thfm_errors:
                errors += thfm_errors
            else:
                validated += 1
                print(f"  OK: {thfm_path.name} ({len(data)} classes, {cialdini_count} Cialdini-mapped, {insider_count} insider, {total_edges} technique edges)")

    # Summary
    print(f"\nValidation complete: {validated} files OK, {errors} errors")

    if errors > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
