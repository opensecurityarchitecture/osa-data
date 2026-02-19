#!/usr/bin/env python3
"""Fix DETECTED_BY edge target and rename technology_class to technology_capability.

Two changes:
1. DETECTED_BY: retarget from detection_strategy → control (wrong)
   to detection_strategy → technology_capability (correct).
   Derivation: Detection -DETECTS-> Technique <-COUNTERS- Mitigation
               <-CAPABILITY_SUPPORTS_MITIGATION- TechnologyCapability (TTCE only)

2. Rename: technology_class → technology_capability in all from_type/to_type fields.
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'attack')

def load_json(path):
    with open(os.path.join(DATA_DIR, path)) as f:
        return json.load(f)

def save_json(path, data):
    with open(os.path.join(DATA_DIR, path), 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')

def main():
    graph = load_json('graph-edges.json')

    # === 1. Regenerate DETECTED_BY edges ===
    print("=== Regenerating DETECTED_BY edges ===")
    old_count = len(graph.get('DETECTED_BY', []))
    print(f"Old DETECTED_BY count: {old_count}")

    # Build mitigation -> TTCE tech classes (filter out TPCE process classes)
    mit_to_tech = {}
    for e in graph.get('CAPABILITY_SUPPORTS_MITIGATION', []):
        if e['from'].startswith('TTCE-'):
            mit = e['to']
            if mit not in mit_to_tech:
                mit_to_tech[mit] = set()
            mit_to_tech[mit].add(e['from'])

    # Build technique -> mitigations
    tech_to_mit = {}
    for e in graph['COUNTERS']:
        if e['to'] not in tech_to_mit:
            tech_to_mit[e['to']] = set()
        tech_to_mit[e['to']].add(e['from'])

    # Build detection -> technique
    det_to_tech = {}
    for e in graph['DETECTS']:
        det_to_tech[e['from']] = e['to']

    # Derive new DETECTED_BY: detection -> TTCE technology classes
    new_detected_by = []
    mapped = 0
    unmapped = 0
    for det_id in sorted(det_to_tech.keys()):
        technique_id = det_to_tech[det_id]
        mitigations = tech_to_mit.get(technique_id, set())
        tech_classes = set()
        for m in mitigations:
            tech_classes.update(mit_to_tech.get(m, set()))

        if tech_classes:
            mapped += 1
        else:
            unmapped += 1

        for tc in sorted(tech_classes):
            new_detected_by.append({
                "from": det_id,
                "from_type": "detection_strategy",
                "to": tc,
                "to_type": "technology_capability"  # already renamed
            })

    graph['DETECTED_BY'] = new_detected_by
    print(f"New DETECTED_BY count: {len(new_detected_by)}")
    print(f"Detections mapped: {mapped}/{len(det_to_tech)}")
    print(f"Detections unmapped: {unmapped}/{len(det_to_tech)}")

    # === 2. Rename technology_class → technology_capability in all edges ===
    print("\n=== Renaming technology_class → technology_capability ===")
    rename_count = 0
    for edge_type, edges in graph.items():
        if edge_type == 'metadata':
            continue
        if not isinstance(edges, list):
            continue
        for edge in edges:
            if edge.get('from_type') == 'technology_class':
                edge['from_type'] = 'technology_capability'
                rename_count += 1
            if edge.get('to_type') == 'technology_class':
                edge['to_type'] = 'technology_capability'
                rename_count += 1

    print(f"Renamed {rename_count} from_type/to_type fields")

    # === 3. Update graph metadata edge counts ===
    graph['metadata']['edge_counts']['DETECTED_BY'] = len(new_detected_by)

    # Recalculate total
    total = sum(
        len(graph[k]) for k in graph if k != 'metadata' and isinstance(graph[k], list)
    )
    graph['metadata']['edge_counts'] = {
        k: len(graph[k]) for k in graph if k != 'metadata' and isinstance(graph[k], list)
    }
    print(f"\nTotal edges: {total}")

    save_json('graph-edges.json', graph)
    print("Saved graph-edges.json")

if __name__ == '__main__':
    main()
