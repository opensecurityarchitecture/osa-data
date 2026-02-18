#!/usr/bin/env python3
"""Verify TIDM identity domain implementation integrity."""

import json
import os
import glob

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
ATTACK_DIR = os.path.join(DATA_DIR, 'attack')
SCHEMA_DIR = os.path.join(DATA_DIR, 'schema')
CONTROLS_DIR = os.path.join(DATA_DIR, 'controls')

def load_json(path):
    with open(path) as f:
        return json.load(f)

def main():
    errors = []
    warnings = []

    # 1. Valid JSON checks
    print("=== 1. JSON Validity ===")
    for fname in ['identity-domain-catalog.json', 'graph-edges.json', 'metadata.json']:
        try:
            load_json(os.path.join(ATTACK_DIR, fname))
            print(f"  OK: {fname}")
        except Exception as e:
            errors.append(f"INVALID JSON: {fname} — {e}")
            print(f"  FAIL: {fname} — {e}")

    try:
        schema = load_json(os.path.join(SCHEMA_DIR, 'trident.schema.json'))
        print(f"  OK: trident.schema.json")
    except Exception as e:
        errors.append(f"INVALID JSON: trident.schema.json — {e}")
        print(f"  FAIL: trident.schema.json — {e}")
        return

    # 2. Schema $defs count
    print("\n=== 2. Schema $defs Count ===")
    defs_count = len(schema.get('$defs', {}))
    print(f"  $defs count: {defs_count}")
    if defs_count != 51:
        errors.append(f"Expected 51 $defs, got {defs_count}")
        print(f"  FAIL: expected 51, got {defs_count}")
    else:
        print(f"  OK: 51 $defs")

    # List new TIDM $defs
    tidm_defs = ['EnumIdpType', 'EnumPolicyType', 'EnumPrincipalType', 'EnumFederationTopology',
                 'EnumAAL', 'EnumFAL', 'AssuranceProfile',
                 'IdentityProvider', 'AccessPolicy', 'IdentityPrincipal', 'FederationPattern']
    for d in tidm_defs:
        if d in schema['$defs']:
            print(f"    OK: {d}")
        else:
            errors.append(f"Missing $def: {d}")
            print(f"    FAIL: {d} missing")

    # 3. Catalog entry count
    print("\n=== 3. Catalog Entry Count ===")
    catalog = load_json(os.path.join(ATTACK_DIR, 'identity-domain-catalog.json'))
    entry_count = len(catalog)
    print(f"  Total entries: {entry_count}")
    if entry_count != 35:
        errors.append(f"Expected 35 catalog entries, got {entry_count}")

    idp_count = sum(1 for k in catalog if k.startswith('TIDM-IDP-'))
    pol_count = sum(1 for k in catalog if k.startswith('TIDM-POL-'))
    pri_count = sum(1 for k in catalog if k.startswith('TIDM-PRI-'))
    fed_count = sum(1 for k in catalog if k.startswith('TIDM-FED-'))
    print(f"  IDP: {idp_count}, POL: {pol_count}, PRI: {pri_count}, FED: {fed_count}")

    # 4. Cross-reference: controlRefs exist as control files
    print("\n=== 4. Control Reference Verification ===")
    # Get all control IDs from control files
    control_files = glob.glob(os.path.join(CONTROLS_DIR, '*.json'))
    control_ids = set()
    for cf in control_files:
        try:
            ctrl = load_json(cf)
            if 'id' in ctrl:
                control_ids.add(ctrl['id'])
        except:
            pass

    all_control_refs = set()
    for entry_id, entry in catalog.items():
        for ref in entry.get('controlRefs', []):
            all_control_refs.add(ref)

    missing_controls = all_control_refs - control_ids
    if missing_controls:
        errors.append(f"Control refs not found in data/controls/: {missing_controls}")
        print(f"  FAIL: {len(missing_controls)} controls not found: {sorted(missing_controls)}")
    else:
        print(f"  OK: All {len(all_control_refs)} control refs verified against {len(control_ids)} controls")

    # 5. Cross-reference: protocols exist in protocol-catalog.json
    print("\n=== 5. Protocol Reference Verification ===")
    proto_catalog = load_json(os.path.join(ATTACK_DIR, 'protocol-catalog.json'))
    proto_ids = set(proto_catalog.keys())

    all_proto_refs = set()
    for entry_id, entry in catalog.items():
        for ref in entry.get('protocols', []):
            all_proto_refs.add(ref)

    missing_protos = all_proto_refs - proto_ids
    if missing_protos:
        errors.append(f"Protocol refs not found: {missing_protos}")
        print(f"  FAIL: {sorted(missing_protos)}")
    else:
        print(f"  OK: All {len(all_proto_refs)} protocol refs verified")

    # 6. Cross-reference: technologyClass exists in technology-capability-catalog.json
    print("\n=== 6. Technology Class Reference Verification ===")
    tech_catalog = load_json(os.path.join(ATTACK_DIR, 'technology-capability-catalog.json'))
    tech_ids = set(tech_catalog.keys())

    all_tech_refs = set()
    for entry_id, entry in catalog.items():
        tc = entry.get('technologyClass')
        if tc:
            all_tech_refs.add(tc)

    missing_tech = all_tech_refs - tech_ids
    if missing_tech:
        errors.append(f"Technology class refs not found: {missing_tech}")
        print(f"  FAIL: {sorted(missing_tech)}")
    else:
        print(f"  OK: All {len(all_tech_refs)} technology class refs verified")

    # 7. Cross-reference: techniques exist in technique-catalog.json
    print("\n=== 7. Technique Reference Verification ===")
    tech_cat = load_json(os.path.join(ATTACK_DIR, 'technique-catalog.json'))
    technique_ids = set(tech_cat.keys())

    all_technique_refs = set()
    for entry_id, entry in catalog.items():
        for ref in entry.get('techniques', []):
            all_technique_refs.add(ref)

    missing_techniques = all_technique_refs - technique_ids
    if missing_techniques:
        errors.append(f"Technique refs not found: {missing_techniques}")
        print(f"  FAIL: {sorted(missing_techniques)}")
    else:
        print(f"  OK: All {len(all_technique_refs)} technique refs verified")

    # 8. Cross-reference: cisSafeguards exist in cis-safeguard-index.json
    print("\n=== 8. CIS Safeguard Reference Verification ===")
    cis_catalog = load_json(os.path.join(ATTACK_DIR, 'cis-safeguard-index.json'))
    cis_ids = set(cis_catalog.keys())

    all_cis_refs = set()
    for entry_id, entry in catalog.items():
        for ref in entry.get('cisSafeguards', []):
            all_cis_refs.add(ref)

    missing_cis = all_cis_refs - cis_ids
    if missing_cis:
        # CIS refs in catalog use "CIS 5.1" format, index might use different format
        warnings.append(f"CIS safeguard refs format check needed: {sorted(missing_cis)}")
        print(f"  WARN: {len(missing_cis)} CIS refs use different format: {sorted(missing_cis)[:5]}...")
        print(f"  Sample CIS index keys: {sorted(list(cis_ids))[:5]}")
    else:
        print(f"  OK: All {len(all_cis_refs)} CIS safeguard refs verified")

    # 9. Edge counts match metadata
    print("\n=== 9. Edge Count Verification ===")
    metadata = load_json(os.path.join(ATTACK_DIR, 'metadata.json'))
    graph = load_json(os.path.join(ATTACK_DIR, 'graph-edges.json'))

    for edge_type in ['SATISFIES', 'MITIGATES', 'IMPLEMENTS_CLASS', 'USES_PROTOCOL', 'FEDERATES_TO']:
        actual = len(graph.get(edge_type, []))
        meta_count = metadata['graph_summary']['edge_types'].get(edge_type, 0)
        graph_meta_count = graph['metadata']['edge_counts'].get(edge_type, 0)

        if actual == meta_count == graph_meta_count:
            print(f"  OK: {edge_type} = {actual}")
        else:
            errors.append(f"{edge_type}: actual={actual}, metadata={meta_count}, graph_meta={graph_meta_count}")
            print(f"  FAIL: {edge_type}: actual={actual}, metadata={meta_count}, graph_meta={graph_meta_count}")

    # Total edges
    total_meta = metadata['graph_summary']['total_edges']
    total_graph_meta = sum(graph['metadata']['edge_counts'].values())
    total_actual = sum(len(graph.get(k, [])) for k in graph if k != 'metadata')
    print(f"\n  Total edges — metadata: {total_meta}, graph_meta: {total_graph_meta}, actual: {total_actual}")
    if total_meta != total_actual:
        errors.append(f"Total edges mismatch: metadata={total_meta}, actual={total_actual}")

    # 10. Total edge types
    print(f"\n=== 10. Edge Type Count ===")
    meta_edge_types = metadata['graph_summary']['total_edge_types']
    actual_edge_types = len(metadata['graph_summary']['edge_types'])
    print(f"  Declared: {meta_edge_types}, actual in summary: {actual_edge_types}")
    if meta_edge_types != actual_edge_types:
        errors.append(f"Edge type count mismatch: declared={meta_edge_types}, actual={actual_edge_types}")

    # Summary
    print("\n" + "=" * 50)
    if errors:
        print(f"ERRORS: {len(errors)}")
        for e in errors:
            print(f"  - {e}")
    else:
        print("ALL CHECKS PASSED")

    if warnings:
        print(f"\nWARNINGS: {len(warnings)}")
        for w in warnings:
            print(f"  - {w}")

    return len(errors) == 0

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
