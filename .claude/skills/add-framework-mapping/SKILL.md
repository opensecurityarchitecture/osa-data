---
name: add-framework-mapping
description: Add or rebuild an OSA framework mapping to NIST SP 800-53 in osa-data. Start from a published crosswalk where one exists, otherwise map from the official text by three ratings; write the coverage file and the control files' clauses; register the framework on the website. Use when a founder asks for a new framework, or to check or rebuild an existing mapping.
---

# Add a framework mapping

A framework mapping has two sides that must agree. The coverage file, `data/framework-coverage/{slug}.json`, gives each clause its controls, coverage and rationale. Each control file carries the framework's id under `compliance_mappings`, with the clauses that name the control, or an empty list. The website also needs the framework's entry in osa-website's `content/frameworks.json`.

Work on a branch, and commit or push only when asked. Keep notes of the method and each decision as you go: `data/CLAUDE.md`, "Framework mappings", says what is recorded where.

## 1. Pin down the framework

Agree with the founder:

- the id (`^[a-z][a-z0-9_]+$`, such as `eu_ai_act`), the slug (`eu-ai-act`), the name, publisher, version and region;
- the official text, in the version in force, from the publisher. For EU law use `https://publications.europa.eu/resource/celex/<CELEX>`, because EUR-Lex refuses automated fetches;
- the clause level, which is the level at which the framework is applied: articles, paragraphs or subcategories.

## 2. Look for a published crosswalk first

Search NIST's catalogue of registered crosswalks (OLIR) and the publisher's own site.

- The catalogue as JSON: `https://csrc.nist.gov/extensions/nudp/services/json/olir/informative-reference-catalog`. One entry, with its file's address and SHA-256: `.../informative-reference-catalog/details/{id}`. Send a browser-like User-Agent. The files are `.xlsx`.
- Read the licence before taking a crosswalk as the base. CIS's own SP 800-53 mapping, for one, is CC BY-NC-ND, so OSA can use it as a base only with CIS's permission.
- Note the checksum of the file you used, and whether it matches the catalogue's.

## 3a. With a crosswalk: take it as the base

- Every pair in the crosswalk with a current base control goes into the mapping. Pairs with a withdrawn control stay out.
- Where the crosswalk pairs a clause with an enhancement such as AC-2(1), ask the founder which rule to follow. The ISO 27001 and CSF 2.0 mappings left those pairs out, and the HIPAA and NERC CIP mappings credited the base control.
- Keep OSA's own pairs, and list them in `metadata.crosswalk_check.not_in_source`. Fill in `source`, `url`, `sha256`, `checked` (the date), `scope`, `source_has_none` (controls the crosswalk maps to no clause) and `added_from_source`. `data/framework-coverage/iso-27001-2022.json` is the model.

## 3b. Without one: three ratings

- Rate every clause yourself from the official text and the control statements in `data/nist/sp800-53-rev5.json`.
- Have two independent raters do the same: two separate agents, each given the same texts and none of the other ratings.
- Take the pairs that at least two of the three name, and report the agreement between each two raters.
- Record it under `metadata.analysis`: `basis`, `checked`, `texts`, `method`, the counts of pairs named by three, by two and by one (left out), `pairs_note`, `not_mapped`, and for a law `commencement`, its dates of application by provision. `data/framework-coverage/dpdpa.json` is the model.

## 4. Write the coverage file

Fields: `framework_id`, `framework_name`, `metadata` (`source`, `version`, `disclaimer`, `jurisdictions`, `applicability_type` and the record from step 3), `weight_scale` (copy it from an existing file), `clauses` (each with `id`, `title`, `controls`, `coverage_pct`, `rationale` and `gaps`) and `summary` (`total_clauses`, `average_coverage` and the count in each coverage band).

Clause titles are OSA's short summaries. Quote no copyrighted text. Where the clauses come in named parts with an order of their own, as CSF 2.0's GV, ID, PR and so on, give that order in `metadata.clause_groups`.

## 5. Write the control side

Every control file gets the framework's id under `compliance_mappings`. Write it with a script in the session's scratchpad, never in `scripts/`, and run it from the osa-data root. It is safe to run twice, and it ends by checking that the two sides agree.

```python
import json
from collections import OrderedDict
from pathlib import Path

DATA = Path('data')
FRAMEWORK, SLUG = 'eu_ai_act', 'eu-ai-act'

coverage = json.load(open(DATA / 'framework-coverage' / f'{SLUG}.json'))
by_control = {}
for clause in coverage['clauses']:
    for cid in clause['controls']:
        by_control.setdefault(cid, []).append(clause['id'])

manifest = json.load(open(DATA / 'controls' / '_manifest.json'))
for entry in manifest['controls']:
    path = DATA / 'controls' / entry['file']
    control = json.load(open(path), object_pairs_hook=OrderedDict)
    mappings = OrderedDict((k, v) for k, v in control['compliance_mappings'].items() if k != FRAMEWORK)
    mappings[FRAMEWORK] = by_control.get(entry['id'], [])
    control['compliance_mappings'] = mappings
    with open(path, 'w') as f:
        json.dump(control, f, indent=2, ensure_ascii=False)
        f.write('\n')

known = {e['id'] for e in manifest['controls']}
print('control ids in the coverage file but not in the catalogue:', sorted(set(by_control) - known))
coverage_pairs = {(cid, cl) for cid, cls in by_control.items() for cl in cls}
control_pairs = {(e['id'], cl) for e in manifest['controls']
                 for cl in json.load(open(DATA / 'controls' / e['file']))['compliance_mappings'][FRAMEWORK]}
print('pairs on one side only:', len(coverage_pairs ^ control_pairs))
```

Both printed lines should show nothing to fix: an empty list and 0.

## 6. Register on the website

Add the entry to osa-website's `content/frameworks.json`: `id`, `slug`, `name`, `fullName`, `description`, `category`, `region`, `publisher`, `version` and `url`. The region must belong to one of the filter groups in `src/pages/frameworks/index.astro`. If it does not, the build stops and names the framework.

## 7. Validate and check

```bash
python3 scripts/validate_json.py              # ends with 0 errors
npm --prefix ~/osa/website run build          # builds the framework page, card and API answer
```

Serve the build (`npx wrangler pages dev dist --port 8788` in `~/osa/website`), read the framework page and its card at `/frameworks/{slug}.md`, and run `python3 tests/agent-surface/checks.py http://127.0.0.1:8788` in osa-website.

## 8. Report

Give the founder the clause count, the number of pairs, the average coverage, the clauses with no control, and how each figure was reached: from the crosswalk and OSA's additions, or from the ratings with their agreement. Compute every figure from the files.
