# Open Security Architecture (OSA) Data

Security architecture patterns, the NIST SP 800-53 Rev 5 controls they use, and mappings from those controls to compliance frameworks. This is the data behind [opensecurityarchitecture.org](https://www.opensecurityarchitecture.org).

## Overview

OSA provides **operational, ready-to-use security architecture patterns** with compliance control mappings. Unlike SABSA (strategic/business-focused) or O-ESA (policy-driven), OSA patterns are practical and implementable.

Each pattern names the controls that matter for a kind of system, says which are critical, and lists the threats each control mitigates. The framework mappings then show which clauses of ISO 27001, PCI DSS, DORA, NIS2 and 86 other frameworks those controls answer.

## What's here

- **56 pattern files** in `data/patterns/`: SP-000 to SP-054 and SP-999. SP-000 is the style reference and SP-999 is a rendering test.
- **317 controls** in `data/controls/`: NIST SP 800-53 Rev 5, across 20 families. That is all 300 controls of Release 5.2.0 and the 17 withdrawn ones that OSA's older patterns still name. Each control file lists its clauses in every framework under `compliance_mappings`, and NIST's enhancements of the control under `enhancements`, each with its statement and baselines. Frameworks are mapped to the controls, not to the enhancements. The 17 controls NIST has withdrawn are marked `withdrawn`, with the controls they moved into under `incorporated_into`. NIST's Rev 4 catalogue already lists 15 of them as withdrawn, and Rev 5 withdrew AU-15 and SC-19.
- **90 framework coverage files** in `data/framework-coverage/`. For each clause of a framework: the controls that address it, a coverage estimate, the rationale and the gaps.
- **NIST's own text** in `data/nist/sp800-53-rev5.json`: every control and enhancement of SP 800-53 Release 5.2.0 with its name, statement, discussion, related controls and baselines, built from NIST's published files.
- **MITRE ATT&CK Enterprise** in `data/mitre-attack/`: tactics, techniques, groups, mitigations and detection strategies from MITRE's STIX data, and CTID's mapping of SP 800-53 Rev 5 controls to the techniques they mitigate.
- **Policy templates** in `data/templates/policies/`: an information security policy and an acceptable use policy, each statement tagged with its SP 800-53 controls.
- **ArchiMate views** in `data/archimate/`, starting with SP-030, and earlier releases of patterns in `data/patterns/archive/`.
- **An industry profile** in `data/verticals/`: financial services, with its threat profiles.
- **Schemas** in `data/schema/` for patterns, controls, coverage files and the system architecture model (SAM).
- **Two skills for AI agents** in `skills/`. `osa-security-patterns` teaches a coding agent to answer a question from OSA in a few requests. `osa-control-mapping` teaches it to map an organisation's own controls to SP 800-53 and line them up against any framework OSA maps. See [skills/README.md](skills/README.md).

[CLAUDE.md](CLAUDE.md) documents the data model and the conventions for patterns and diagrams.

## Where the mappings come from

The mappings to ISO/IEC 27001:2022, NIST CSF 2.0, the HIPAA Security Rule and NERC CIP take crosswalks registered in NIST's catalogue (OLIR) as their base. Clauses that OSA adds beyond those crosswalks are recorded in the coverage file, under `metadata.crosswalk_check`, and marked on the site.

India's DPDPA, the NIST AI RMF and the EU AI Act were mapped from their official texts by three ratings, and each file records the texts and the method under `metadata.analysis`. The other mappings are OSA's own analysis. Every coverage file gives its rationale and gaps clause by clause, so you can check the reasoning against the framework's own text. Have a qualified assessor confirm a mapping before you rely on it for compliance or audit.

## Using the data

- **Browse**: [patterns](https://www.opensecurityarchitecture.org/patterns/), [controls](https://www.opensecurityarchitecture.org/controls/), [frameworks](https://www.opensecurityarchitecture.org/frameworks/) and the [ATT&CK matrix](https://www.opensecurityarchitecture.org/attack/).
- **API**: a JSON API at `https://www.opensecurityarchitecture.org/api/v1/`. It needs no key. See the [API guide](https://www.opensecurityarchitecture.org/api/), the [explorer](https://www.opensecurityarchitecture.org/api/explorer/) and the [OpenAPI description](https://www.opensecurityarchitecture.org/openapi.yaml).
- **AI agents**: start at [llms.txt](https://www.opensecurityarchitecture.org/llms.txt). Every pattern, control and framework also has a short Markdown card, for example `https://www.opensecurityarchitecture.org/patterns/sp-029.md`.
- **Your own controls**: map them to SP 800-53 with your AI agent, then line them up against any framework OSA maps. See the [guide](https://www.opensecurityarchitecture.org/foundations/map-your-controls/).
- **Files**: clone this repository and read the JSON.

## Layout

```
data/
├── patterns/             # SP-NNN-descriptive-title.json, one per pattern
│   ├── _manifest.json    # index of all patterns
│   └── archive/          # earlier releases of patterns
├── controls/             # AC-01.json and so on, one per control
│   ├── _manifest.json
│   └── _catalog.json
├── framework-coverage/   # one file per framework
├── nist/                 # SP 800-53 as NIST publishes it, generated
├── mitre-attack/         # ATT&CK Enterprise and CTID's SP 800-53 mapping, generated
├── archimate/            # ArchiMate views of patterns
├── verticals/            # industry profiles
├── templates/            # policy templates
└── schema/               # JSON schemas
scripts/                  # validation, the NIST sync and the builders for nist/ and mitre-attack/
skills/                   # skill files for AI agents
```

The one-off scripts that built the first mappings and diagrams, from January to March 2026, left `scripts/` in October 2026. They are in the history of that folder.

`data/mitre-attack/` holds MITRE ATT&CK Enterprise v20.0 and the Center for Threat-Informed Defense's mapping of SP 800-53 Rev 5 to it, both generated from the published sources by `scripts/build_attack_extract.py`. See its README for what was changed and the licences.

## Validating

```bash
pip install jsonschema
python3 scripts/validate_json.py
```

The same check runs on every pull request that changes the data.

## What we're working on

Our focus is the patterns and their data, for usability, accuracy and coverage. New framework mappings start from a published crosswalk wherever one exists, and we add the frameworks people ask for. We're also making OSA easy for AI agents to use, through short cards, a JSON API and skills. Ideas and requests are welcome as issues.

## Contributing

Corrections to patterns and mappings are welcome, and so are new framework mappings. Please open an issue first for anything large. To ask for a framework, use the framework request template. Problems with the website can be reported here too.

A new framework mapping needs three things:

1. A coverage file in `data/framework-coverage/` that passes `scripts/validate_json.py`. Use control ids from `data/controls/`, which are SP 800-53 Rev 5 base controls in the form `AC-02`. Where a published crosswalk to SP 800-53 exists, start from it: NIST's catalogue of registered crosswalks (OLIR) lists many.
2. The same mappings on the control side. Every control file gets the framework's key under `compliance_mappings`, holding the clauses that name that control, or an empty list. The two sides must agree.
3. An entry in the website's framework registry. The site's source is not in this repository, so we add that.

In the pull request, say what the mapping is based on: a published crosswalk, which you should name, or your own analysis.

What NIST says about a control (its name, statement, discussion, related controls, baselines and enhancements) comes from `data/nist/sp800-53-rev5.json`. `scripts/sync_nist.py` writes it into the control files and the patterns, and the validator checks that every copy agrees. To correct NIST's text, rebuild the source with `scripts/build_nist_extract.py`.

## Licence

Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0). See [LICENSE](LICENSE).
