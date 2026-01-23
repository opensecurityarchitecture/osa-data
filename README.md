# Open Security Architecture (OSA) Data

Structured security architecture patterns and NIST 800-53 controls from [opensecurityarchitecture.org](https://www.opensecurityarchitecture.org).

## Overview

OSA provides **operational, ready-to-use security architecture patterns** with compliance control mappings. Unlike SABSA (strategic/business-focused) or O-ESA (policy-driven), OSA patterns are practical and implementable.

**Key differentiator:** Each pattern includes specific NIST 800-53 controls mapped to ISO 27001, COBIT, PCI-DSS, and other frameworks.

## What's Here

```
osa-workspace/
├── data/
│   ├── patterns/           # 27 security architecture patterns (JSON)
│   ├── controls/           # 191 NIST 800-53 Rev 5 controls (JSON)
│   └── schema/             # JSON schemas for validation
│       ├── pattern.schema.json
│       └── control.schema.json
├── docs/
│   ├── DISCOVERY.md        # Site analysis and findings
│   └── ROADMAP.md          # Modernisation roadmap
└── scripts/                # Extraction scripts
```

## Data Structure

### Patterns

Each pattern includes:
- **Metadata**: ID, title, authors, status, dates
- **Diagram**: SVG/PNG architecture diagram paths
- **Content**: Description, assumptions, challenges, indications, contra-indications, threat resistance
- **Controls**: List of applicable NIST 800-53 controls
- **Compliance mappings**: Cross-references to ISO 27001, PCI-DSS, COBIT, NIST CSF, CIS Controls

Example pattern (SP-011 Cloud Computing):
```json
{
  "id": "SP-011",
  "title": "Cloud Computing Pattern",
  "metadata": {
    "status": "published",
    "authors": ["Phaedrus"]
  },
  "controls": [
    {"id": "AC-01", "name": "Access Control Policies and Procedures", "family": "AC"},
    {"id": "SC-07", "name": "Boundary Protection", "family": "SC"}
  ],
  "controlFamilySummary": {"AC": 5, "SC": 12, "SA": 8}
}
```

### Controls

Each control includes:
- **NIST 800-53 Rev 4 data**: ID, name, family, description, guidance
- **Baseline indicators**: Low/Moderate/High
- **Compliance mappings**: ISO 17799, COBIT 4.1, PCI-DSS v2 (legacy)
- **Rev 5 fields**: Structure ready for NIST 800-53 Rev 5 update

Example control (AC-04 Information Flow Enforcement):
```json
{
  "id": "AC-04",
  "name": "Information Flow Enforcement",
  "family": "AC",
  "family_name": "Access Control",
  "control_class": "Technical",
  "baseline_low": true,
  "baseline_moderate": true,
  "baseline_high": true,
  "iso17799": ["10.6.2", "11.4.5"],
  "cobit41": ["DS5.10"],
  "pci_dss_v2": ["4.1"]
}
```

## Pattern Catalogue

| ID | Pattern | Controls | Status |
|----|---------|----------|--------|
| SP-001 | Client Module | 80 | Published |
| SP-002 | Server Module | 90 | Published |
| SP-003 | Privacy Mobile Device Pattern | - | Published |
| SP-004 | SOA Publication and Location | 10 | Published |
| SP-005 | SOA Internal Service Usage | 14 | Published |
| SP-006 | Wireless Private Network | 19 | Published |
| SP-007 | Wireless Public Hotspot | 17 | Published |
| SP-008 | Public Web Server | 38 | Published |
| SP-009 | Generic Pattern | - | Published |
| SP-010 | Identity Management | - | Published |
| SP-011 | Cloud Computing | 54 | Published |
| SP-012 | Secure SDLC | - | Reserved |
| SP-013 | Data Security | 33 | Published |
| SP-014 | Awareness and Training | 11 | Draft |
| SP-015 | Consumer Devices for Enterprise | - | Reserved |
| SP-016 | DMZ Module | 31 | Published |
| SP-017 | Secure Network Zone Module | - | Reserved |
| SP-018 | ISMS Module | 29 | Published |
| SP-019 | Secure Ad-Hoc File Exchange | 25 | Published |
| SP-020 | Email TLS | 8 | Published |
| SP-021 | Realtime Collaboration | 19 | Draft |
| SP-022 | Board Room | 17 | Published |
| SP-023 | Industrial Control Systems | 34 | Published |
| SP-024 | iPhone Pattern | 8 | Published |
| SP-025 | Advanced Monitoring & Detection | 33 | Published |
| SP-026 | PCI Full Environment | 32 | Published |

## Roadmap

### Phase 1: Content Modernisation (Current)
- [ ] Update NIST 800-53 Rev 4 to Rev 5
- [ ] Update ISO 17799 to ISO 27001:2022
- [ ] Update COBIT 4.1 to COBIT 2019
- [ ] Update PCI-DSS v2 to v4.0
- [ ] Add NIST CSF 2.0 mappings
- [ ] Add CIS Controls v8 mappings

### Phase 2: API Layer
- [ ] REST API for patterns and controls
- [ ] OpenAPI documentation
- [ ] GitHub Pages hosting (zero cost)

### Phase 3: AI Integration
- [ ] Pattern recommendation engine
- [ ] Control selection assistant
- [ ] Threat modelling integration

See [docs/ROADMAP.md](docs/ROADMAP.md) for full details.

## Usage

### Validate JSON files
```bash
# Using ajv-cli
npm install -g ajv-cli
ajv validate -s data/schema/pattern.schema.json -d "data/patterns/*.json"
ajv validate -s data/schema/control.schema.json -d "data/controls/*.json"
```

### Query patterns by control family
```bash
# Find patterns with significant Access Control requirements
jq -r 'select(.controlFamilySummary.AC > 5) | "\(.id): \(.title) (AC: \(.controlFamilySummary.AC))"' data/patterns/*.json
```

### Find all controls for a pattern
```bash
jq '.controls[].id' data/patterns/SP-011-pattern-cloud-computing.json
```

## Contributing

Contributions welcome, especially:
- NIST 800-53 Rev 5 mapping updates
- Modern compliance framework mappings (ISO 27001:2022, PCI-DSS v4, etc.)
- Pattern content updates and corrections
- New patterns (following schema)

Please open an issue to discuss significant changes before submitting a PR.

## License

Content is licensed under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**.

See [LICENSE](LICENSE) for details.

Original content from [opensecurityarchitecture.org](https://www.opensecurityarchitecture.org).

## Background

Open Security Architecture has been running since ~2008, with active development for 4-5 years before going dormant. Despite minimal maintenance, it continues receiving ~1,700 daily visitors. Pattern content was referenced in O'Reilly publications (Cloud Pattern).

This repository represents the modernisation effort to:
1. Extract patterns to structured, version-controlled data
2. Update compliance mappings to current framework versions
3. Make patterns accessible via API
4. Enable AI-powered security architecture tooling

## Links

- **Website**: [opensecurityarchitecture.org](https://www.opensecurityarchitecture.org)
- **Pattern Library**: [Pattern Landscape](https://www.opensecurityarchitecture.org/library/patternlandscape)
- **Control Catalogue**: [Control Catalogue](https://www.opensecurityarchitecture.org/library/0802control-catalogue)
