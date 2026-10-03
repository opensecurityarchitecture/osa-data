# Open Security Architecture (OSA) Data

Security architecture patterns, the NIST SP 800-53 Rev 5 controls they use, and mappings from those controls to compliance frameworks. This is the data behind [opensecurityarchitecture.org](https://www.opensecurityarchitecture.org).

## Overview

OSA provides **operational, ready-to-use security architecture patterns** with compliance control mappings. Unlike SABSA (strategic/business-focused) or O-ESA (policy-driven), OSA patterns are practical and implementable.

Each pattern names the controls that matter for a kind of system, says which are critical, and lists the threats each control mitigates. The framework mappings then show which clauses of ISO 27001, PCI DSS, DORA, NIS2 and 83 other frameworks those controls answer.

## What's here

- **56 pattern files** in `data/patterns/`: SP-000 to SP-054 and SP-999. SP-000 is the style reference and SP-999 is a rendering test.
- **315 controls** in `data/controls/`: NIST SP 800-53 Rev 5, across 20 families. Each control file lists its clauses in every framework under `compliance_mappings`. The 17 controls that Rev 5 withdrew are marked, with the controls they moved into.
- **87 framework coverage files** in `data/framework-coverage/`. For each clause of a framework: the controls that address it, a coverage estimate, the rationale and the gaps.
- **Schemas** in `data/schema/` for patterns, controls and coverage files.
- **A skill for AI agents** in `skills/osa-security-patterns/`. It teaches a coding agent to answer a question from OSA in a few requests. See [skills/README.md](skills/README.md).

[CLAUDE.md](CLAUDE.md) documents the data model and the conventions for patterns and diagrams.

## Where the mappings come from

The mappings to ISO/IEC 27001:2022 and NIST CSF 2.0 take NIST's published crosswalks as their base. Clauses that OSA adds beyond those crosswalks are recorded in the coverage file, under `metadata.crosswalk_check`, and marked on the site.

The other mappings are OSA's own analysis. Every coverage file gives its rationale and gaps clause by clause, so you can see the reasoning and check it against the framework's own text. Validate with a qualified assessor before relying on a mapping for compliance or audit.

## Using the data

- **Browse**: [patterns](https://www.opensecurityarchitecture.org/patterns/), [controls](https://www.opensecurityarchitecture.org/controls/), [frameworks](https://www.opensecurityarchitecture.org/frameworks/) and the [ATT&CK coverage matrix](https://www.opensecurityarchitecture.org/attack/).
- **API**: a JSON API at `https://www.opensecurityarchitecture.org/api/v1/`. It needs no key. See the [API guide](https://www.opensecurityarchitecture.org/api/), the [explorer](https://www.opensecurityarchitecture.org/api/explorer/) and the [OpenAPI description](https://www.opensecurityarchitecture.org/openapi.yaml).
- **AI agents**: start at [llms.txt](https://www.opensecurityarchitecture.org/llms.txt). Every pattern, control and framework also has a short Markdown card, for example `https://www.opensecurityarchitecture.org/patterns/sp-029.md`.
- **Files**: clone this repository and read the JSON.

## Layout

```
data/
├── patterns/             # SP-NNN-descriptive-title.json, one per pattern
│   └── _manifest.json    # index of all patterns
├── controls/             # AC-01.json and so on, one per control
│   ├── _manifest.json
│   └── _catalog.json
├── framework-coverage/   # one file per framework
├── verticals/            # industry profiles
├── templates/            # policy templates
└── schema/               # JSON schemas
scripts/                  # validation and the scripts that built the mappings
skills/                   # skill files for AI agents
```

The ATT&CK data behind the coverage matrix on the site is not in this repository.

## Validating

```bash
pip install jsonschema
python3 scripts/validate_json.py
```

The same check runs on every pull request that changes the data.

## Contributing

Corrections to patterns and mappings are welcome, and so are new framework mappings. Please open an issue first for anything large. To ask for a framework, use the framework request template. Problems with the website can be reported here too.

A new framework mapping needs three things:

1. A coverage file in `data/framework-coverage/` that passes `scripts/validate_json.py`. Use control ids from `data/controls/`, which are SP 800-53 Rev 5 base controls in the form `AC-02`.
2. The same mappings on the control side. Every control file gets the framework's key under `compliance_mappings`, holding the clauses that name that control, or an empty list. The two sides must agree.
3. An entry in the website's framework registry. The site's source is not in this repository, so we add that.

In the pull request, say what the mapping is based on: a published crosswalk, which you should name, or your own analysis.

## Licence

Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0). See [LICENSE](LICENSE).
