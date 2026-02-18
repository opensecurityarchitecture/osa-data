#!/usr/bin/env python3
"""Generate TIDM identity domain edges and append to graph-edges.json.

Derives edges from identity-domain-catalog.json:
- SATISFIES: IDP/POL/PRI -> Control (from controlRefs[])
- MITIGATES: POL -> Technique (from techniques[])
- IMPLEMENTS_CLASS: IDP -> TechnologyClass (from technologyClass)
- USES_PROTOCOL: IDP -> Protocol (from protocols[])
- FEDERATES_TO: IDP -> IDP (10 reference federation patterns)
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'attack')

def load_json(filename):
    with open(os.path.join(DATA_DIR, filename)) as f:
        return json.load(f)

def save_json(filename, data):
    with open(os.path.join(DATA_DIR, filename), 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')

def main():
    catalog = load_json('identity-domain-catalog.json')
    graph = load_json('graph-edges.json')

    satisfies_edges = []
    mitigates_edges = []
    implements_class_edges = []
    uses_protocol_edges = []
    federates_to_edges = []

    # Process each catalog entry
    for entry_id, entry in catalog.items():
        # Determine entity type from ID prefix
        if entry_id.startswith('TIDM-IDP-'):
            from_type = 'identity_provider'
        elif entry_id.startswith('TIDM-POL-'):
            from_type = 'access_policy'
        elif entry_id.startswith('TIDM-PRI-'):
            from_type = 'identity_principal'
        elif entry_id.startswith('TIDM-FED-'):
            from_type = 'federation_pattern'
            continue  # FederationPatterns don't generate edges
        else:
            continue

        # SATISFIES edges from controlRefs[]
        for control_ref in entry.get('controlRefs', []):
            satisfies_edges.append({
                "from": entry_id,
                "from_type": from_type,
                "to": control_ref,
                "to_type": "control"
            })

        # MITIGATES edges from techniques[] (AccessPolicy only)
        for technique in entry.get('techniques', []):
            mitigates_edges.append({
                "from": entry_id,
                "from_type": from_type,
                "to": technique,
                "to_type": "technique"
            })

        # IMPLEMENTS_CLASS edges from technologyClass (IdentityProvider only)
        tech_class = entry.get('technologyClass')
        if tech_class:
            implements_class_edges.append({
                "from": entry_id,
                "from_type": from_type,
                "to": tech_class,
                "to_type": "technology_class"
            })

        # USES_PROTOCOL edges from protocols[] (IdentityProvider only)
        for protocol in entry.get('protocols', []):
            uses_protocol_edges.append({
                "from": entry_id,
                "from_type": from_type,
                "to": protocol,
                "to_type": "protocol"
            })

    # FEDERATES_TO reference edges (10 common federation patterns from TIDM §4.1)
    federation_pairs = [
        ("TIDM-IDP-01", "TIDM-IDP-02"),  # AD -> Entra ID
        ("TIDM-IDP-01", "TIDM-IDP-03"),  # AD -> Okta
        ("TIDM-IDP-03", "TIDM-IDP-02"),  # Okta -> Entra ID
        ("TIDM-IDP-04", "TIDM-IDP-02"),  # Duo -> Entra ID
        ("TIDM-IDP-04", "TIDM-IDP-03"),  # Duo -> Okta
        ("TIDM-IDP-05", "TIDM-IDP-01"),  # CyberArk -> AD
        ("TIDM-IDP-01", "TIDM-IDP-05"),  # AD -> CyberArk
        ("TIDM-IDP-09", "TIDM-IDP-02"),  # Workload Identity -> Cloud IdP
        ("TIDM-IDP-10", "TIDM-IDP-01"),  # NAC -> AD
        ("TIDM-IDP-03", "TIDM-IDP-06"),  # Federation broker -> CIAM
    ]

    for from_id, to_id in federation_pairs:
        federates_to_edges.append({
            "from": from_id,
            "from_type": "identity_provider",
            "to": to_id,
            "to_type": "identity_provider"
        })

    # Print counts
    print(f"SATISFIES edges: {len(satisfies_edges)}")
    print(f"MITIGATES edges: {len(mitigates_edges)}")
    print(f"IMPLEMENTS_CLASS edges: {len(implements_class_edges)}")
    print(f"USES_PROTOCOL edges: {len(uses_protocol_edges)}")
    print(f"FEDERATES_TO edges: {len(federates_to_edges)}")
    total_new = (len(satisfies_edges) + len(mitigates_edges) +
                 len(implements_class_edges) + len(uses_protocol_edges) +
                 len(federates_to_edges))
    print(f"Total new edges: {total_new}")

    # Append new edge arrays to graph-edges.json
    if 'SATISFIES' not in graph:
        graph['SATISFIES'] = []
    graph['SATISFIES'].extend(satisfies_edges)

    if 'MITIGATES' not in graph:
        graph['MITIGATES'] = []
    graph['MITIGATES'].extend(mitigates_edges)

    if 'IMPLEMENTS_CLASS' not in graph:
        graph['IMPLEMENTS_CLASS'] = []
    graph['IMPLEMENTS_CLASS'].extend(implements_class_edges)

    if 'USES_PROTOCOL' not in graph:
        graph['USES_PROTOCOL'] = []
    graph['USES_PROTOCOL'].extend(uses_protocol_edges)

    if 'FEDERATES_TO' not in graph:
        graph['FEDERATES_TO'] = []
    graph['FEDERATES_TO'].extend(federates_to_edges)

    # Update metadata edge counts
    graph['metadata']['edge_counts']['SATISFIES'] = len(graph['SATISFIES'])
    graph['metadata']['edge_counts']['MITIGATES'] = len(graph['MITIGATES'])
    graph['metadata']['edge_counts']['IMPLEMENTS_CLASS'] = len(graph['IMPLEMENTS_CLASS'])
    graph['metadata']['edge_counts']['USES_PROTOCOL'] = len(graph['USES_PROTOCOL'])
    graph['metadata']['edge_counts']['FEDERATES_TO'] = len(graph['FEDERATES_TO'])

    save_json('graph-edges.json', graph)
    print(f"\nUpdated graph-edges.json with {total_new} new edges across 5 edge types")

    # Print final edge counts from metadata
    total_all_edges = sum(graph['metadata']['edge_counts'].values())
    print(f"Total edges in graph: {total_all_edges}")

if __name__ == '__main__':
    main()
