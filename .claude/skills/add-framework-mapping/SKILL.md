---
name: add-framework-mapping
description: Add or rebuild an OSA framework mapping to NIST SP 800-53 in osa-data. Start from a published crosswalk where one exists, otherwise map from the official text by three ratings; write the coverage file and the control files' clauses; register the framework on the website. Use when a founder asks for a new framework, or to check or rebuild an existing mapping.
---

# Add a framework mapping

A framework mapping has two sides that must agree. The coverage file, `data/framework-coverage/{slug}.json`, gives each clause its controls, coverage and rationale. Each control file carries the framework's id under `compliance_mappings`, with the clauses that name the control, or an empty list. The website also needs the framework's entry in osa-website's `content/frameworks.json`.

Work on a branch in git worktrees of your own, one per repository, since other builders may be at work in the same repositories. Commit or push only when asked. osa-data is public, and the permission system may refuse a push to it even where a similar push went through. If it does, stop and report it: a founder then pushes or says yes to a retry. Keep notes of the method and each decision as you go: `data/CLAUDE.md`, "Framework mappings", says what is recorded where.

## 1. Pin down the framework

Agree with the founder:

- the id (`^[a-z][a-z0-9_]+$`, such as `eu_ai_act`), the slug (`eu-ai-act`), the name, publisher, version and region;
- the official text, in the version in force, from the publisher. For EU law use `https://publications.europa.eu/resource/celex/<CELEX>`, because EUR-Lex refuses automated fetches. Where the publisher gives the text out only through a form or a login, a founder downloads it: leave such forms to the founders;
- the clause level, which is the level at which the framework is applied: articles, paragraphs or subcategories. CIS is applied by its safeguards. SOC 2 is applied by its criteria, each read with its points of focus. Grundschutz++ is applied by its base requirements, with their enhancements folded in, and BOT's IT risk notification by the items of its attachments plus the sections that bind in their own right;
- the licences, below.

### Licences

OSA's data is CC BY-SA 4.0. The licence of the framework's text settles what the coverage file may quote, and the licence of a mapping settles whether OSA may publish pairs taken from it. Quote a title only where the licence or the law allows it, and record the credit (step 4). Under a licence with no derivatives, or for non-commercial use only, keep the publisher's ids and facts and write everything else in OSA's own words. The cases so far:

- CIS Controls: CC BY-NC-ND 4.0. The file keeps CIS's safeguard numbers and implementation groups, with OSA's own titles and pairs. CIS's mapping to SP 800-53 carries the same licence, so without CIS's permission OSA rates the safeguards itself.
- HKMA: its terms allow its text to be reproduced unchanged and for non-commercial use, so the titles are OSA's own.
- The Secure Controls Framework: CC BY-ND 4.0 with an end-user licence agreement. Keep pairs derived from it out of OSA's data.
- BSI Grundschutz++: CC BY-SA 4.0, so the file quotes BSI's titles as `title_de`, with the credit.
- The Bank of Thailand's notification: under section 7 of Thailand's Copyright Act B.E. 2537, a state body's notification is not a copyright work, so the file quotes its Thai titles as `title_th`.
- A publisher's mapping file that states no licence: use it for a cross-check only (step 3b).

## 2. Look for a published crosswalk first

Search NIST's catalogue of registered crosswalks (OLIR) and the publisher's own site.

- The catalogue as JSON: `https://csrc.nist.gov/extensions/nudp/services/json/olir/informative-reference-catalog`. One entry, with its file's address and SHA-256: `.../informative-reference-catalog/details/{id}`. Send a User-Agent that names OSA, such as `osa-check/1.0 (+https://www.opensecurityarchitecture.org)`, and never one that poses as a browser. If the server refuses the request, ask a founder to download the file in a browser, or use another official copy. The files are `.xlsx`.
- Read the crosswalk's licence (step 1) before taking it as the base.
- Note the checksum of the file you used, and whether it matches the catalogue's.

## 3a. With a crosswalk: take it as the base

- Every pair in the crosswalk with a current base control goes into the mapping. Pairs with a withdrawn control stay out.
- Where the crosswalk pairs a clause with an enhancement such as AC-2(1), the pair counts for the base control (Russell, 1 November 2026). Report how many pairs come from enhancements only, and list them under `metadata.crosswalk_check.from_enhancements_only`, by control.
- Keep OSA's own pairs, and list them in `metadata.crosswalk_check.not_in_source`. Fill in `source`, `url`, `sha256`, `checked` (the date), `scope`, `source_has_none` (controls the crosswalk maps to no clause) and `added_from_source`. `data/framework-coverage/iso-27001-2022.json` is the model.

## 3b. Without one: three ratings

Three raters each rate every clause: three separate agents, given the same brief. You then build the mapping from their ratings.

The brief gives every rater:

- the same inputs: the official text with the list of clause ids, and the control statements from `data/nist/sp800-53-rev5.json`;
- a work folder of its own in the session's scratchpad. A rater works from its inputs alone, so it stays out of the other raters' folders, OSA's coverage files and patterns, the web and any publisher's mapping;
- what to list: current base controls, in the form `AC-02`, whose statements, put in place, directly meet part of what the clause asks. A control that supports the clause or shares its topic stays off the list;
- the house rules that settle common splits (`data/CLAUDE.md`, "Framework mappings"): a crosswalk pair on an enhancement counts for its base control, and customer authentication maps to IA-08, with IA-02 added where multi-factor or separate-device authentication is asked for;
- the output, one JSON file: `{"rater", "method_notes", "clauses": [{"id", "controls": [{"id", "rationale"}], "coverage_pct", "gaps"}]}`, where `coverage_pct` estimates how much of the clause an organisation would meet by putting the listed controls in place;
- a check script for the rater to write and run before it hands back. It confirms that the clause ids match the list, in order, that each control is one of the 300 current base controls (those without `withdrawn` in the extract) and is named once, that each coverage figure is a whole number from 0 to 100, and that the copy check below passes.

Rate a large framework in groups of about 120 to 150 clauses, with three raters to a group. Grundschutz++ took five groups.

A publisher's spreadsheet may store clause numbers as numbers, so that CIS 3.10 reads as 3.1. Number each clause by its position within its parent, check that the ids are unique and complete, and put the same warning in the brief.

For an official text in another language, give every rater the same working English translation, made with fixed renderings of the modal verbs (must, should, may). Say in `metadata.disclaimer` that OSA read the text through its own working translation, which is not official.

Then build the mapping:

- Keep each pair that two or more raters name. A clause's coverage is the median of the three estimates.
- Once the controls are settled, write the titles, rationale and gaps from the raters' reasons and from the gaps two or more raters named. Writer agents with a checker script do this well. Then have a reviewer read every clause against the control statements: in CIS the review caught a claim that no control statement makes.
- Check with a script, as each rater does, that no run of seven or more words in a title, rationale or gap matches the source text. Hold titles further off under a licence with no derivatives: each CIS title shares at most three words in a row with CIS's own.
- Report the agreement of each two raters as a Jaccard index, the pairs both named divided by the pairs either named. So far it has run from 0.66 to 0.87.

Record it under `metadata.analysis`: `basis`, `checked`, `texts`, `method`, `pairs_named_by_three`, `pairs_named_by_two`, `pairs_named_by_one_and_left_out`, `pairs_per_rating`, `agreement_measure`, `agreement`, `coverage_agreement`, `pairs_note`, `not_mapped`, and for a law `commencement`, its dates of application by provision. `data/framework-coverage/cis-controls-v8.json` is the model, and `bot-cyber.json` for a law.

A publisher's own mapping may follow a different method, such as listing every related control. Compare it with OSA's privately, and let a founder decide before any file or page cites it. With a founder's yes, cite the comparison in `metadata.analysis.publisher_mapping`, in OSA's own words: the mapping's title, publisher, address and SHA-256, the date compared, the pairs in each and in both, and the main reasons the two differ. End `analysis.basis` with one sentence that gives the headline figure, since the framework page shows it. `data/framework-coverage/soc2-tsc.json` is the model.

## 4. Write the coverage file

Fields: `framework_id`, `framework_name`, `metadata` (`source`, `version`, `disclaimer`, `jurisdictions`, `applicability_type` and the record from step 3), `weight_scale` (copy it from an existing file), `clauses` (each with `id`, `title`, `controls`, `coverage_pct`, `rationale` and `gaps`) and `summary` (`total_clauses`, `average_coverage` and the count in each coverage band).

Write OSA's own short title for each clause unless step 1 allows quoting the publisher's. The rationale and gaps are always OSA's own words.

- A file that quotes English titles word for word names their source, with the credit its licence asks for, in `metadata.clause_titles_from`. The site prints it as "Clause titles are the source's own wording, from …". `clause_titles_licence` and `clause_titles_url` record the licence and the address. `data/framework-coverage/ncsc-caf.json` is the model.
- For a source in another language, `title` holds OSA's English title and a field named for the language holds the publisher's: `title_de` in BSI Grundschutz++, `title_th` in BOT's notification. Credit them in `metadata`: `clause_titles_{lang}_from` and `clause_titles_{lang}_url` for the source, `_licence` and `_licence_url` for the licence, or `_rights` and `_rights_url` for a text outside copyright, and `clause_titles_note` for what OSA did with the titles. Leave `clause_titles_from` out of such a file. The site shows German and Thai titles. For another language, add it to `LANGUAGES` in osa-website's `src/lib/titles-credit.ts` and to the clause tables of `src/pages/frameworks/[slug].astro` and `[slug]/coverage.astro`.

Keep the publisher's facts about each clause in fields of their own, such as CIS's `implementation_group`, and say what each holds in `metadata.clause_fields`. Where the clauses come in named parts with an order of their own, as CSF 2.0's GV, ID, PR and so on, give that order in `metadata.clause_groups`.

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
    control['compliance_mappings'][FRAMEWORK] = by_control.get(entry['id'], [])
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

The script adds a new framework's key at the end of `compliance_mappings`, and the diff then shows a comma added after the key before it. On a rebuild it does the same in any control file that lacks the key. Elsewhere the key keeps its place, so the files' framework order stays as it is. Each list follows the coverage file's clause order.

Other mapping branches touch the same control files. When one lands before yours, rebase onto it and run the script again, which writes your framework's key afresh in every control file.

## 6. Register on the website

Add the entry to osa-website's `content/frameworks.json`: `id`, `slug`, `name`, `fullName`, `description`, `category`, `region`, `publisher`, `version` and `url`. The region must belong to one of the filter groups in `src/pages/frameworks/index.astro`. If it does not, the build stops and names the framework.

A new framework also raises the framework count in `README.md`, `CLAUDE.md`, `skills/osa-security-patterns/SKILL.md` and `skills/osa-control-mapping/SKILL.md`. Change them on the same branch.

## 7. Validate and check

```bash
python3 scripts/validate_json.py              # ends with 0 errors
```

The validator also checks every framework's two sides: the coverage file and the control files must name the same pairs, and every control a coverage file names must be in the catalogue.

Build and serve the site from a worktree of osa-website, on a `feature/` branch from `origin/staging`:

- Point `src/data` at the root of your data worktree, since the site reads `src/data/data/...`, and link `node_modules` from `~/osa/website`: `ln -s <data worktree> src/data` and `ln -s ~/osa/website/node_modules node_modules`. Stage website files by explicit path: `.gitignore` names `node_modules/` as a folder, so git lists the link as a new file.
- Run `npm run build` in the worktree. Load the local database's tables before serving, `npx wrangler d1 execute osa-comments --local --file=schema.sql`, then serve with `npx wrangler pages dev dist --port 8788`.
- Read the framework page and its card at `/frameworks/{slug}.md`, and run `python3 tests/agent-surface/checks.py http://127.0.0.1:8788`.

The checks read what they expect from the data, so a data change can change how many run, and a check that assumes something about the data can fail, such as which frameworks keep pairs of OSA's own. Change such a check in a website pull request that merges with the data one, and say in both pull requests why the count moved.

Look at the page sizes in `dist/frameworks/{slug}/`. The Grundschutz++ coverage page, with 652 clauses, is 1.7 MB, so raise splitting with a founder for a framework of that size.

## 8. Report

Give the founder the clause count, the number of pairs, the average coverage, the clauses with no control, and how each figure was reached: from the crosswalk and OSA's additions, or from the ratings with their agreement. Compute every figure from the files. Name each judgement call too, such as adding a clause: BOT's section 9 became one because section 10.1 relies on its criteria.

## An existing mapping: check, rebuild or retire

Check a mapping against the edition in force before you change it. A rebuild then follows steps 2 to 8.

- Record the edition the file maps in `metadata.edition`: `used`, `url`, and `replaced` where it took over from an earlier one. Record the check in `metadata.edition_check`: `checked`, `basis`, `sources`, `changes` and `titles`, with the rows that changed in `clauses_edited`, `clauses_added` and `clauses_removed`. `data/framework-coverage/cis-controls-v8.json` is the model.
- While a rebuild is under way, give the framework's entry in osa-website's `content/frameworks.json` the `status` `updating`, a `statusNote` naming the document the mapping is moving to, and `replacedBy` linking it. Keep the id and slug, so links keep working, and remove the status when the rebuild lands.
- To retire a framework, delete its coverage file and take its key out of each control file in place, so a file loses only those lines. Remove its registry entry, lower the counts (step 6), and send its pages and cards to its successor with 301s in osa-website's `public/_redirects`, as `eba_ict` went to DORA.
- When the registry gains a field or a status value, raise the API's version as osa-website's `CLAUDE.md` says.
- For a small edit, such as new titles, change the lines themselves and check that the file still parses. A re-save with `json.dump` spreads arrays that some files keep on one line, such as `crosswalk_check.added_from_source`, over many lines, and the real change gets lost in the diff. Read `git diff --stat` before committing.
- When you retitle clauses, search every coverage file for the old titles, because other files copy them: BIO2 had ISO/IEC 27002's titles with "(BIO2)" added.
