---
name: new-pattern
description: Add a new OSA security pattern to osa-data, with its manifest entry, control names from NIST, threats, references that serve the documents they name, and the diagram that goes with it on the website. Use when a founder asks for a new pattern or a draft of one on a topic.
---

# New pattern

A pattern is one JSON file in `data/patterns/`, an entry in `data/patterns/_manifest.json` and a diagram in osa-website's `public/images/`. The website builds the pattern's page, Markdown card and API answer from the file.

Work on a branch, and commit or push only when asked. Write the text a person reads in plain words, by the "Words on the page" rules in osa-website's `CLAUDE.md`.

## 1. Number and file name

Read `data/patterns/_manifest.json` and take the next number after the highest SP-NNN. SP-000 is the style reference and SP-999 the rendering test, so skip both. The file is `data/patterns/SP-NNN-descriptive-title.json`. The slug is the title in lowercase with hyphens, without the `sp-nnn-` prefix.

## 2. Read before writing

- `data/schema/pattern.schema.json` for the required fields.
- `data/patterns/SP-000-reference-pattern.json`, the reference for structure and diagrams.
- A recent full pattern for depth and tone, such as `SP-051-tokenised-asset-security-architecture.json` or `SP-052-decentralised-identity-verifiable-credentials.json`.
- `data/CLAUDE.md`, "Pattern Schema Key Fields" and "SVG Diagram Conventions".

## 3. Write the pattern

Top level: `$schema` (`"../schema/pattern.schema.json"`), `id`, `slug`, `title`, `description` (three to five sentences on what it protects, its control count and main families, and when it applies), `url` (`https://www.opensecurityarchitecture.org/patterns/sp-nnn`), `metadata`, `diagram` (`/images/sp-nnn-descriptive-title.svg`) and `legend`.

`metadata`: `release` (YY.MM), `classification`, `status` `"draft"`, `type` `"pattern"`, `datePublished`, `dateModified`, `authors` by alias (Aurelius, Vinylwasp, Spinoza, Vitruvius), `reviewers` and `provenance`.

`content`: `description` (four to six paragraphs), `keyControlAreas` (seven to ten paragraphs, each naming its SP 800-53 controls inline), `assumptions`, `typicalChallenges`, `indications`, `contraIndications` and `threatResistance`.

`examples`: three to five categories of two to four examples each, and `Developing Areas` with five forward-looking paragraphs.

`controls`: 25 to 50 objects, each with `id`, `name`, `family` and `emphasis` (`critical`, `important` or `standard`). Use current base controls in the form `AC-02`. Check each against `data/controls/_manifest.json`, and pick its successor where the control is marked withdrawn. The sync in step 5 writes the names.

`controlFamilySummary`: each family code with its count.

`threats`: eight to twelve, each with `id` (`T-XXX-NNN`), `title`, `description` (three to five sentences) and `mitigatedBy`, which names controls from this pattern's list. Give every threat at least one control, and aim for every critical control to mitigate at least one threat: the pattern card lists what each critical control mitigates.

`references`: eight to twelve, each with `title`, `url` and `note`. Open every address and confirm it serves the document the title names. In October 2026 a check of all patterns found 27 addresses that returned 404, used in 24 patterns.

`relatedPatterns`: a list of ids as strings (`["SP-029"]`), with `relatedPatternNames` in the same order.

`context`: `dataTypes`, `protocols`, `assetTypes`, `adversaryProfile`, `regulatoryScope` and `humanFactors`.

## 4. Manifest

Add `{ "id": "SP-NNN", "title": "...", "status": "draft", "controls": N, "file": "SP-NNN-descriptive-title.json" }` to `data/patterns/_manifest.json` in number order, and raise `total_patterns` by one.

## 5. Names from NIST, then validate

```bash
python3 scripts/sync_nist.py        # writes each control's name as NIST has it
python3 scripts/validate_json.py    # ends with 0 errors
```

The validator compares every control name in a pattern with NIST's, so let the sync write the names.

## 6. The diagram

Draw the SVG at osa-website's `public/images/sp-nnn-descriptive-title.svg`, following SP-000 and "SVG Diagram Conventions" in `data/CLAUDE.md`: a 960 by 720 viewBox, the OSA palette, clickable control badges (`/controls/xx-nn` in lowercase, with `target="_top"`), a legend, a reference bar, and opensecurityarchitecture.org at the foot.

- End every font list with a generic family: `system-ui, -apple-system, sans-serif`. The website build runs `node scripts/svg-font-fallbacks.mjs --check` and stops on a font without one.
- The footer line prints the status and the control totals, such as "35 NIST 800-53 Rev 5 controls across 12 families · Authors: … · Draft · 2026-10-29". Keep it in step with the pattern file. The website's acceptance checks compare them.

## 7. Check it on the site

Build osa-website (`npm --prefix ~/osa/website run build`), serve it (`npx wrangler pages dev dist --port 8788` in `~/osa/website`) and read the pattern page, the card at `/patterns/sp-nnn.md` and `/api/v1/patterns/SP-NNN/crosswalk?emphasis=critical`. Then run `python3 tests/agent-surface/checks.py http://127.0.0.1:8788` in osa-website.

## 8. Report

Give the founder the id and title, the controls by emphasis and family, the threats, the related patterns and anything left to decide. The pattern stays `draft` until a founder promotes it.
