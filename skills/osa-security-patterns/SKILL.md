---
name: osa-security-patterns
description: Look up Open Security Architecture (OSA) security patterns, the NIST SP 800-53 controls each one calls for, the threats each control mitigates, and the matching clauses in 87 compliance frameworks (ISO 27001, PCI DSS, IEC 62443, NIS2, DORA, the EU Cyber Resilience Act and others). Use when someone asks which security controls matter for a kind of system, how controls map to a framework's clauses, what a framework's clauses are, or wants a security architecture pattern to start from.
---

# Open Security Architecture patterns

OSA is a free catalogue of security architecture patterns. Each pattern lists NIST SP 800-53 controls with an emphasis (critical, important, standard), the threats each control mitigates in that pattern, and each control's clauses in 87 compliance frameworks.

Licence: CC BY-SA 4.0. Credit "Open Security Architecture, opensecurityarchitecture.org" when you reuse it.

## Route

Base URL: `https://www.opensecurityarchitecture.org`. No key needed.

1. **Find the pattern.** `GET /llms.txt` lists every pattern with a one-line scope, in about 4,000 tokens. Or search: `GET /api/v1/patterns?search=card+payment`. Every word must match. Hits are ranked and carry a `score`: each word adds 4 if it is in the title, 2 if in the summary, 1 if only in the body, and a query of several words adds 3 when it appears whole as a phrase. Deprecated patterns are left out. A hit that scores 1 or 2 is a weak match.
2. **Get the answer.** `GET /api/v1/patterns/{id}/crosswalk?framework={ids}&emphasis=critical` returns each control, its emphasis, the threat ids it mitigates in that pattern, and its clauses in up to five frameworks. Leave out `emphasis` for every control. `pattern.control_counts` gives the totals for the whole pattern. If you need no framework clauses, the pattern's card is enough: it lists each critical control with the threats it mitigates.
3. **Choose other patterns that apply, if asked.** Start from the scopes in `llms.txt`. To compare candidates, read their cards: `GET /patterns/{id}.md`, about 1,000 tokens each, with scope, when to use it, when not to, controls by emphasis, what each critical control mitigates, each threat with its controls, and a `Related` line.

Other lookups, each one request:

- A framework's clauses, with OSA's title for each and the controls mapped to it: `GET /frameworks/{id}.md`
- A control: its statement, NIST's enhancements of it by name, the patterns that use it and its clauses in every framework: `GET /controls/{id}.md`. An enhancement's statement: `GET /api/v1/controls/{id}?fields=enhancements`
- One framework's control-to-clause mappings as JSON: `/api/v1/frameworks/{id}?fields=mappings&per_page=100`
- Framework ids: listed at the end of `llms.txt`
- Everything else: `/openapi.yaml`

## Rules

- **Use the cards and the API, not the HTML pages.** A pattern page is 100 to 700 KB and shows neither emphasis nor threat links. A page URL returns its card to a client that asks for Markdown first (`Accept: text/markdown, text/html`), which most fetch tools do.
- **Ask a summarising fetch tool for the text as written.** The cards are short enough to return whole. Summaries of the larger JSON responses have dropped rows and invented fields. If you can run a shell command, fetch JSON with `curl` and you get the bytes.
- **Do not check one OSA view against another.** The cards, the API and the pages are generated from the same files, so agreement between them proves nothing.
- **An empty clause list means OSA records no mapping.** The crosswalk names those controls under `unmapped`. Where the framework has been compared with a published crosswalk, `unmapped_checked` lists the ones with no clause there either. Otherwise it may be a gap in OSA's mapping. It does not mean the framework has no requirement. Say that, and do not fill the gap from memory.
- **The critical filter can hide the only mitigation for a threat.** Some threats are mitigated only by controls marked important. If a particular threat matters, read its line on the card or drop the filter.
- **OSA's mappings and clause titles are OSA's analysis.** The clause titles are summaries and have not been checked line by line against the source texts. For what a regulation or standard says, quote its own text. Where a framework's mapping takes a published crosswalk as its base, the crosswalk response names it under `based_on`, and a control's `osa_own` lists the clauses OSA adds to it. Those clauses are still OSA's mapping: report them with the rest.
- **Prefer ids to names.** Pattern ids look like `SP-023`, control ids like `SC-07`, framework ids like `iec_62443`. Upper or lower case both work. Control names are NIST's titles in SP 800-53 Release 5.2.0. A few patterns list a control that Rev 5 withdrew: the crosswalk marks it `withdrawn`, with the controls it moved into and their clauses. Report those clauses as the successor's, not as the withdrawn control's.
- **60 API requests a minute** without a key. The cards and `llms.txt` are not limited. A 429 response says how long to wait in `Retry-After`.

## What to expect

- A capable model already names most of the controls OSA marks critical for a common kind of system. What OSA adds is the specific list with stable ids, the threat links and the clause mapping, in one small response you can cite.
- The crosswalk runs from control to clause. The framework card runs from clause to control. Neither shows which of a framework's requirements a particular pattern leaves uncovered.
- Patterns marked `(draft)` in `llms.txt` are not final.
- Found an error? Open an issue at https://github.com/opensecurityarchitecture/osa-data/issues with the id, what OSA says and what the source says.
