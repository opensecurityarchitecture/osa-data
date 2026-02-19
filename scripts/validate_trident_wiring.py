#!/usr/bin/env python3
"""Validate TRIDENT wiring: ensure all entity/edge types in metadata.json
are rendered in the Explorer and ERD JavaScript files.

Catches the "new types pushed but Explorer/ERD doesn't render them" gap.

Usage:
  python3 scripts/validate_trident_wiring.py          # Normal run
  python3 scripts/validate_trident_wiring.py --json    # Machine-readable output

Authors: Spinoza, Vitruvius | OSA 2026
"""

import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(SCRIPT_DIR, '..')
DATA = os.path.join(ROOT, 'data', 'attack')
TRIDENT_MODEL = os.path.join(DATA, 'trident-model.json')
EXPLORER_JS = os.path.join(ROOT, 'website', 'public', 'js', 'trident-explorer.js')
MODEL_JS = os.path.join(ROOT, 'website', 'public', 'js', 'trident-model.js')
EXPLORER_ASTRO = os.path.join(ROOT, 'website', 'src', 'pages', 'trident', 'explorer.astro')
MODEL_ASTRO = os.path.join(ROOT, 'website', 'src', 'pages', 'trident', 'model.astro')

# Metadata node type -> Explorer COLOURS key
# Most match 1:1. Three legacy types use shortened names in the explorer.
NODE_TYPE_MAP = {
    'technique':          'technique',
    'mitigation':         'mitigation',
    'detection_strategy': 'detection',
    'control':            'control',
    'cis_safeguard':      'cis_safeguard',
    'weakness_class':     'weakness',
    'threat_actor':       'actor',
    'process_capability': 'process_capability',
    'technology_capability': 'technology_capability',
    'adversary_tier':     'adversary_tier',
    'human_factor':       'human_factor',
    'data_type':          'data_type',
    'cloud_service':      'cloud_service',
    'protocol':           'protocol',
    'insider_stage':      'insider_stage',
    'identity_provider':  'identity_provider',
    'access_policy':      'access_policy',
    'identity_principal': 'identity_principal',
    'federation_pattern': 'federation_pattern',
}

# Metadata edge type -> Explorer internal edge type name(s)
# Some metadata edges share an internal name (e.g. REQUIRES_PROTECTION and
# PROTECTS_DATA both render as 'datatype-control'). Update when adding new types.
EDGE_TYPE_MAP = {
    'COUNTERS':                       ['mitigation-technique'],
    'PRESCRIBES':                     ['control-mitigation'],
    'ALIGNS_TO':                      ['mitigation-cis'],
    'DETECTS':                        ['detection-technique'],
    'DETECTED_BY':                    ['detection-control'],
    'IMPLEMENTED_BY':                 ['cis-control'],
    'EXPLOITS':                       ['technique-weakness'],
    'USES':                           ['actor-technique'],
    'CLASSIFIED_BY':                  ['control-process-cap'],
    'PROVIDES_CAPABILITY':            ['control-tech-class'],
    'TIER_CONTAINS':                  ['tier-technique'],
    'EXPLOITS_HUMAN':                 ['technique-human-factor'],
    'PARENT_OF':                      ['technique-parent'],
    'CAPABILITY_SUPPORTS_CIS':        ['cap-cis'],
    'CAPABILITY_SUPPORTS_MITIGATION': ['cap-mitigation'],
    'REQUIRES_PROTECTION':            ['datatype-control'],
    'PROTECTS_DATA':                  ['datatype-control'],
    'PROVIDER_IMPLEMENTS':            ['cloud-provider-control'],
    'CUSTOMER_IMPLEMENTS':            ['cloud-customer-control'],
    'TARGETS_PROTOCOL':               ['technique-protocol'],
    'UPGRADES_TO':                    ['protocol-upgrade'],
    'TRANSITIONS_TO':                 ['stage-transition'],
    'INDICATED_BY':                   ['stage-indicator'],
    'STAGE_DETECTED_BY':              ['stage-detection'],
    'SATISFIES':                      ['tidm-control'],
    'MITIGATES':                      ['policy-technique'],
    'IMPLEMENTS_CLASS':               ['idp-tech-class'],
    'USES_PROTOCOL':                  ['idp-protocol'],
    'FEDERATES_TO':                   ['idp-federation'],
}


def load_json(path):
    with open(path) as f:
        return json.load(f)


def read_file(path):
    with open(path) as f:
        return f.read()


def check_key_in_js(js_content, key):
    """Check if a key appears as a JS object property."""
    patterns = [
        rf"['\"]?{re.escape(key)}['\"]?\s*:",
        rf"'{re.escape(key)}'",
        rf'"{re.escape(key)}"',
    ]
    return any(re.search(p, js_content) for p in patterns)


def main():
    json_output = '--json' in sys.argv

    metadata = load_json(os.path.join(DATA, 'metadata.json'))
    gs = metadata['graph_summary']
    node_types = sorted(gs['node_types'].keys())
    edge_types = sorted(gs['edge_types'].keys())

    # Website files may not exist in CI (osa-data repo checked out alone)
    has_website = os.path.isfile(EXPLORER_JS)
    explorer_js = read_file(EXPLORER_JS) if has_website else ''
    model_js = read_file(MODEL_JS) if has_website else ''
    explorer_astro = read_file(EXPLORER_ASTRO) if has_website else ''
    model_astro = read_file(MODEL_ASTRO) if has_website else ''

    errors = []
    warnings = []
    checks = 0

    if not has_website:
        warnings.append('Website files not found — skipping Explorer/ERD JS checks (data-only mode)')

    # ═══════════════════════════════════════════════════════════
    # Mapping completeness (catches new types before anything else)
    # ═══════════════════════════════════════════════════════════

    unmapped_nodes = set(node_types) - set(NODE_TYPE_MAP.keys())
    if unmapped_nodes:
        errors.append(f'NODE_TYPE_MAP missing: {", ".join(sorted(unmapped_nodes))}')

    unmapped_edges = set(edge_types) - set(EDGE_TYPE_MAP.keys())
    if unmapped_edges:
        errors.append(f'EDGE_TYPE_MAP missing: {", ".join(sorted(unmapped_edges))}')

    stale_nodes = set(NODE_TYPE_MAP.keys()) - set(node_types)
    if stale_nodes:
        warnings.append(f'NODE_TYPE_MAP stale entries: {", ".join(sorted(stale_nodes))}')

    stale_edges = set(EDGE_TYPE_MAP.keys()) - set(edge_types)
    if stale_edges:
        warnings.append(f'EDGE_TYPE_MAP stale entries: {", ".join(sorted(stale_edges))}')

    # ═══════════════════════════════════════════════════════════
    # Data-only checks (always run, even without website checkout)
    # ═══════════════════════════════════════════════════════════

    # Check edge config covers all metadata edge types (via graph-edges.json)
    graph_edges = load_json(os.path.join(DATA, 'graph-edges.json'))
    for et in edge_types:
        checks += 1
        if et not in graph_edges:
            errors.append(f'graph-edges.json missing edge type: {et}')

    # ═══════════════════════════════════════════════════════════
    # trident-model.json validation (always run)
    # ═══════════════════════════════════════════════════════════

    has_model = os.path.isfile(TRIDENT_MODEL)
    if has_model:
        model = load_json(TRIDENT_MODEL)
        model_domains = set(model.get('domains', {}).keys())
        model_node_types = model.get('nodeTypes', {})
        model_edge_types = model.get('edgeTypes', {})
        model_paths = model.get('analyticalPaths', {})
        all_model_nodes = set(model_node_types.keys())

        # Every hasData nodeType must exist in metadata
        for nt_id, nt in model_node_types.items():
            if nt.get('hasData'):
                checks += 1
                if nt_id not in node_types:
                    errors.append(f'Model nodeType "{nt_id}" (hasData=true) not in metadata node_types')
            # Domain must be valid
            checks += 1
            if nt.get('domain') not in model_domains:
                errors.append(f'Model nodeType "{nt_id}" references unknown domain "{nt.get("domain")}"')

        # Every hasData edgeType must exist in graph-edges
        for et_id, et in model_edge_types.items():
            if et.get('hasData'):
                checks += 1
                if et_id not in graph_edges:
                    errors.append(f'Model edgeType "{et_id}" (hasData=true) not in graph-edges.json')
            # from/to must reference valid nodeTypes
            froms = et.get('from', [])
            if isinstance(froms, str):
                froms = [froms]
            tos = et.get('to', [])
            if isinstance(tos, str):
                tos = [tos]
            for f in froms:
                checks += 1
                if f not in all_model_nodes:
                    errors.append(f'Model edgeType "{et_id}": from "{f}" not in model nodeTypes')
            for t in tos:
                checks += 1
                if t not in all_model_nodes:
                    errors.append(f'Model edgeType "{et_id}": to "{t}" not in model nodeTypes')

        # Every metadata node type must appear in model (hasData=true)
        for nt in node_types:
            checks += 1
            if nt not in model_node_types:
                errors.append(f'Metadata node type "{nt}" not in trident-model.json nodeTypes')
            elif not model_node_types[nt].get('hasData'):
                errors.append(f'Metadata node type "{nt}" in model but hasData is not true')

        # Every metadata edge type must appear in model (hasData=true)
        for et in edge_types:
            checks += 1
            if et not in model_edge_types:
                errors.append(f'Metadata edge type "{et}" not in trident-model.json edgeTypes')
            elif not model_edge_types[et].get('hasData'):
                errors.append(f'Metadata edge type "{et}" in model but hasData is not true')

        # Validate analytical path references
        for path_id, path_def in model_paths.items():
            if path_def.get('planned'):
                continue  # Skip planned-only paths
            for n in path_def.get('nodes', []):
                checks += 1
                if n not in all_model_nodes:
                    errors.append(f'Model path "{path_id}": node "{n}" not in model nodeTypes')
            for e in path_def.get('edges', []):
                checks += 1
                if e not in model_edge_types and e not in graph_edges:
                    errors.append(f'Model path "{path_id}": edge "{e}" not in model edgeTypes or graph-edges')
    else:
        warnings.append('trident-model.json not found — skipping model validation')

    # ═══════════════════════════════════════════════════════════
    # ERD checks — data-driven contract validation (requires website)
    # ═══════════════════════════════════════════════════════════

    if has_website:
        # Check ERD JS reads from modelData (data-driven, no hardcoded entity types)
        checks += 1
        if 'modelData.nodeConfig' not in model_js and 'nc[' not in model_js:
            errors.append('ERD JS does not read from modelData.nodeConfig (data-driven contract broken)')

        checks += 1
        if 'modelData.edgeConfig' not in model_js and 'ec[' not in model_js:
            errors.append('ERD JS does not read from modelData.edgeConfig (data-driven contract broken)')

        checks += 1
        if 'modelData.pathConfig' not in model_js and 'paths[' not in model_js:
            errors.append('ERD JS does not read from modelData.pathConfig (data-driven contract broken)')

        # Check model.astro has build-time validation
        checks += 1
        if 'validationErrors' not in model_astro or 'build-time validation failed' not in model_astro:
            errors.append('ERD model.astro missing build-time validation')

        checks += 1
        if 'graph-edges.json' not in model_astro:
            errors.append('ERD model.astro not loading graph-edges.json for edge derivation')

        checks += 1
        if 'entity-swatch' not in model_astro:
            errors.append('ERD model.astro missing data-driven legend swatches')

        checks += 1
        if 'metadata.graph_summary.node_types' not in model_astro:
            errors.append('ERD model.astro not reading metadata.graph_summary.node_types')

        # Check model.astro loads trident-model.json
        checks += 1
        if 'trident-model.json' not in model_astro:
            errors.append('ERD model.astro not loading trident-model.json for model-driven config')

        # Check model.astro injects domainConfig
        checks += 1
        if 'domainConfig' not in model_astro:
            errors.append('ERD model.astro not injecting domainConfig')

        # Check model.astro injects conceptualNodes
        checks += 1
        if 'conceptualNodes' not in model_astro:
            errors.append('ERD model.astro not injecting conceptualNodes')

    # ═══════════════════════════════════════════════════════════
    # Explorer checks — node types (requires website)
    # ═══════════════════════════════════════════════════════════

    if has_website:
        for nt in node_types:
            explorer_name = NODE_TYPE_MAP.get(nt, nt)

            # COLOURS entry
            checks += 1
            if not check_key_in_js(explorer_js, explorer_name):
                errors.append(f'Explorer COLOURS missing: {explorer_name} (for {nt})')

            # getNodeData handler (type === 'xxx')
            checks += 1
            if f"'{explorer_name}'" not in explorer_js and f'"{explorer_name}"' not in explorer_js:
                errors.append(f'Explorer JS not referencing node type: {explorer_name} (for {nt})')

            # showDetailPanel handler
            checks += 1
            panel_pattern = rf"type\s*===\s*'{re.escape(explorer_name)}'"
            if not re.search(panel_pattern, explorer_js):
                errors.append(f'Explorer detail panel missing: {explorer_name} (for {nt})')

        # ═══════════════════════════════════════════════════════════
        # Explorer checks — edge types (uses mapped names)
        # ═══════════════════════════════════════════════════════════

        seen_internal = set()
        for meta_name, internal_names in EDGE_TYPE_MAP.items():
            if meta_name not in edge_types:
                continue
            for iname in internal_names:
                if iname in seen_internal:
                    continue  # Skip duplicate internal names (e.g. datatype-control)
                seen_internal.add(iname)

                # Edge type referenced in explorer JS
                checks += 1
                if f"'{iname}'" not in explorer_js and f'"{iname}"' not in explorer_js:
                    errors.append(f'Explorer edge type missing: {iname} (for {meta_name})')

                # Legend data-edge attribute
                checks += 1
                if f'data-edge="{iname}"' not in explorer_astro:
                    errors.append(f'Explorer legend missing: data-edge="{iname}" (for {meta_name})')

        # ═══════════════════════════════════════════════════════════
        # Catalog loading check — explorer.astro must load each catalog
        # ═══════════════════════════════════════════════════════════

        catalog_files = [
            'technique-catalog.json',
            'mitigation-catalog.json',
            'detection-catalog.json',
            'cis-safeguard-index.json',
            'weakness-catalog.json',
            'actor-catalog.json',
            'process-capability-catalog.json',
            'technology-capability-catalog.json',
            'adversary-tier-catalog.json',
            'human-factors-catalog.json',
            'cloud-service-catalog.json',
            'data-classification-catalog.json',
            'protocol-catalog.json',
            'insider-stage-catalog.json',
            'identity-domain-catalog.json',
        ]
        for cat_file in catalog_files:
            checks += 1
            if cat_file not in explorer_astro:
                errors.append(f'Explorer build not loading: {cat_file}')

    # ═══════════════════════════════════════════════════════════
    # Output
    # ═══════════════════════════════════════════════════════════

    total_edges = gs['total_edges']
    total_node_types = len(node_types)
    total_edge_types = len(edge_types)

    if json_output:
        result = {
            'status': 'FAIL' if errors else 'PASS',
            'checks': checks,
            'errors': errors,
            'warnings': warnings,
            'summary': {
                'node_types': total_node_types,
                'edge_types': total_edge_types,
                'total_edges': total_edges,
            }
        }
        print(json.dumps(result, indent=2))
    else:
        print(f'TRIDENT Wiring Validator')
        print(f'{"=" * 50}')
        print(f'Metadata: {total_node_types} node types, {total_edge_types} edge types, {total_edges:,} edges')
        print(f'Checks:   {checks}')
        print()

        if errors:
            print(f'ERRORS ({len(errors)}):')
            for e in errors:
                print(f'  \u2717 {e}')
            print()

        if warnings:
            print(f'WARNINGS ({len(warnings)}):')
            for w in warnings:
                print(f'  \u26a0 {w}')
            print()

        if not errors:
            print(f'PASS: All {total_node_types} node types and {total_edge_types} edge types wired in Explorer and ERD')
        else:
            print(f'FAIL: {len(errors)} wiring gaps found')

    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
