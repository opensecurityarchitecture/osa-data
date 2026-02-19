# Open Security Architecture (OSA) Data

Structured security architecture patterns, NIST 800-53 controls, compliance framework mappings, and the TRIDENT threat-defence graph from [opensecurityarchitecture.org](https://www.opensecurityarchitecture.org).

## Overview

OSA provides **operational, ready-to-use security architecture patterns** with compliance control mappings. Unlike SABSA (strategic/business-focused) or O-ESA (policy-driven), OSA patterns are practical and implementable.

**Key differentiator:** Each pattern includes specific NIST 800-53 Rev 5 controls mapped to 53 compliance frameworks. The TRIDENT graph connects controls to ATT&CK techniques, mitigations, detections, threat actors, and more — enabling threat-led security architecture.

## Current Data

- **48 security patterns** (SP-001 to SP-047) + SP-000 reference/style guide
- **315 NIST 800-53 Rev 5 controls** across 20 families
- **53 compliance frameworks** (ISO 27001, PCI-DSS v4, NIST CSF 2.0, DORA, NIS2, SOC 2, CMMC, regional financial regulators, and more)
- **472 MITRE ATT&CK techniques** (v16.1) mapped to 108 controls via CTID
- **163 ATT&CK threat groups** with 2,921 technique USES edges
- **44 ATT&CK mitigations** (v18.1) with 1,445 technique COUNTERS edges
- **691 ATT&CK detection strategies** (v18.1)
- **171 CIS v8 safeguards** reverse-indexed to controls
- **135 CWE weakness classes** mapped to techniques via CAPEC bridge
- **17,332 TRIDENT graph edges** across 29 relationship types, 19 entity types

See [CLAUDE.md](CLAUDE.md) for full data model documentation.

## Directory Structure

```
data/
├── patterns/           # 48 security architecture patterns (JSON)
│   └── _manifest.json  # Index of all patterns
├── controls/           # 315 NIST 800-53 Rev 5 controls (JSON)
│   ├── _manifest.json
│   └── _catalog.json
├── attack/             # TRIDENT attack/weakness/control graph
│   ├── technique-catalog.json           # ATT&CK techniques
│   ├── mitigation-catalog.json          # ATT&CK mitigations
│   ├── detection-catalog.json           # ATT&CK v18 detection strategies
│   ├── actor-catalog.json               # ATT&CK threat groups
│   ├── weakness-catalog.json            # CWE weakness classes
│   ├── cis-safeguard-index.json         # CIS v8 safeguards
│   ├── process-capability-catalog.json  # TPCE process capabilities
│   ├── technology-capability-catalog.json # TTCE technology classes
│   ├── adversary-tier-catalog.json      # TACM adversary tiers
│   ├── human-factors-catalog.json       # THFM cognitive vulnerability classes
│   ├── cloud-service-catalog.json       # Cloud services with shared responsibility
│   ├── data-classification-catalog.json # Data types with protection requirements
│   ├── protocol-catalog.json            # Protocols with attack surface
│   ├── insider-stage-catalog.json       # Insider threat progression
│   ├── identity-domain-catalog.json     # Identity providers, policies, principals, federation
│   ├── graph-edges.json                 # 17,332 explicit TRIDENT graph edges
│   └── metadata.json                    # Provenance, version info, graph summary
├── verticals/
│   └── financial-services.json
└── schema/
    ├── pattern.schema.json
    ├── control.schema.json
    └── trident.schema.json              # TRIDENT entity/edge schemas
```

## TRIDENT Graph

The TRIDENT (Threat-Informed Defence) graph connects security controls to real-world attack intelligence:

```
Pattern -> Control -> Mitigation -> Technique <- Actor
                  \-> CIS Safeguard     |
                  \-> Process Cap        \-> Weakness
                  \-> Technology Cap     \-> Detection
                  \-> Cloud Service      \-> Protocol
                  \-> Identity Domain    \-> Human Factor
```

19 entity types connected by 29 edge types. Interactive explorer at [opensecurityarchitecture.org/trident/explorer](https://www.opensecurityarchitecture.org/trident/explorer).

## API

- REST API: [opensecurityarchitecture.org/api](https://www.opensecurityarchitecture.org/api)
- OpenAPI spec: [opensecurityarchitecture.org/openapi.yaml](https://www.opensecurityarchitecture.org/openapi.yaml)
- Swagger UI: [opensecurityarchitecture.org/api/explorer](https://www.opensecurityarchitecture.org/api/explorer)

## Usage

```bash
# Validate all JSON against schemas
python3 scripts/validate_json.py

# Build website (from workspace root)
npm --prefix website run build

# Dev server
npm --prefix website run dev
```

## Contributing

Contributions welcome, especially:
- Compliance framework mapping updates
- Pattern content updates and corrections
- New patterns (following schema in `data/schema/pattern.schema.json`)

Please open an issue to discuss significant changes before submitting a PR.

## License

Content is licensed under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**.

See [LICENSE](LICENSE) for details.

## Links

- **Website**: [opensecurityarchitecture.org](https://www.opensecurityarchitecture.org)
- **Pattern Library**: [Pattern Landscape](https://www.opensecurityarchitecture.org/library/patternlandscape)
- **TRIDENT Explorer**: [Graph Explorer](https://www.opensecurityarchitecture.org/trident/explorer)
- **TRIDENT Model**: [Data Model ERD](https://www.opensecurityarchitecture.org/trident/model)
- **Control Catalogue**: [Controls](https://www.opensecurityarchitecture.org/controls)
