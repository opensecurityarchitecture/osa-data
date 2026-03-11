# OSA Skills Catalogue

**Purpose:** Define reusable Claude Code skills (slash commands) that encode OSA's conventions, workflows, and institutional knowledge. Skills reduce errors, enforce quality, and make the multi-repo workflow accessible to all founders.

**Status:** Draft for founder discussion — 2026-03-11

---

## What Are Skills?

Skills are project-level slash commands (e.g., `/new-pattern`, `/pattern-audit`) that expand into full prompts with all the context, conventions, and multi-step instructions needed for a task. They live in `.claude/skills/` in each repo and are available to anyone working in that codebase.

**Why skills matter for OSA:**
- The pattern schema has non-obvious requirements (controls need `name` + `family`, not `title`; relatedPatterns must be strings, not objects)
- The multi-repo workflow (osa-data vs osa-website) means knowing which repo to commit to
- Framework mappings require 3 coordinated updates (coverage file + registry + reverse mappings)
- SVG diagrams have detailed conventions (palette, badge styles, viewBox) that are easy to get wrong
- Quality is our differentiator — skills encode our quality bar

---

## Implemented Skills

### `/new-pattern` (osa-data)
**Scaffold a new security pattern with all required sections.**

What it does:
1. Auto-assigns next SP number (or accepts user-specified)
2. Creates pattern JSON with all required sections: content (7 fields), examples (including Developing Areas), controls, threats, context, references, related patterns
3. Updates `_manifest.json` with correct count
4. Validates against schema
5. Reports summary (control/threat count, families, related patterns)

What it prevents:
- Missing sections (we caught missing Developing Areas on 3 patterns today)
- Schema format errors (controls format, relatedPatterns format)
- Manifest count mismatches
- Inconsistent depth (enforces minimum 25 controls, 8 threats, 5 Developing Areas)

**Owner:** Any founder creating patterns

---

### `/pattern-audit` (osa-data)
**Comprehensive quality audit of one or more patterns.**

What it does:
1. Checks 16 structure requirements (FAIL if missing)
2. Checks 10 quality indicators (WARN if missing)
3. Checks 3 cross-reference validations (manifest, SVG, related patterns)
4. Reports depth metrics (control count, threat count, example categories)
5. For `all` mode: ranks patterns by quality, lists those needing enrichment

What it prevents:
- Publishing incomplete patterns
- Broken cross-references
- Quality drift between patterns (some rich, some stubs)

**Owner:** Any founder reviewing quality

---

## Proposed Skills (Not Yet Built)

### `/new-framework` (osa-data)
**Create a framework coverage mapping with reverse mappings.**

Would handle the full 3-layer process:
1. Create `data/framework-coverage/{id}.json` with clauses, controls, coverage percentages
2. Add entry to `website/content/frameworks.json` registry
3. Run reverse mapping script to update all 315 control files
4. Validate everything

**Priority:** HIGH — we do this frequently and the 3-layer model is the most common source of "it's not showing up" bugs.

---

### `/svg-diagram` (osa-website)
**Generate SVG diagram following SP-000 conventions.**

Would enforce:
- 960x720/750 viewBox, #F8FAFC background, system-ui font
- Palette compliance (#003459, #007EA7, #00A8E8, #00171F)
- Correct badge styles (dark-bar vs inline, critical vs standard)
- Clickable control links with lowercase IDs and `target="_top"`
- Legend, reference bar, opensecurityarchitecture.org branding

**Priority:** MEDIUM — we always need layout tweaks anyway, but getting the conventions right first time saves rework.

---

### `/osa-push` (osa-data or osa-website)
**Smart commit and push with CI verification.**

Would handle:
1. Detect which repo has changes (data, website, or both)
2. Stage relevant files (not secrets, not .env)
3. Generate commit message from diff analysis
4. Push and monitor CI
5. Report status with links

**Priority:** MEDIUM — convenience skill, reduces ceremony.

---

### `/osa-release` (osa-data)
**Draft release notes and update project stats.**

Would handle:
1. Diff since last tag or specified date
2. Summarize: new patterns, new frameworks, control changes, enrichments
3. Update homepage stats if stale (pattern count, framework count)
4. Update MEMORY.md counts
5. Draft changelog entry

**Priority:** LOW — useful for monthly releases, not daily work.

---

### `/blog-post` (osa-website)
**Create a blog post entry in the correct JSON format.**

Would handle:
1. Accept title, author (default: "OSA Core Team"), and topic
2. Generate blog content in the established OSA voice (substantive, practitioner-focused, not marketing)
3. Add to `website/content/blogs.json` in correct position (newest first)
4. Include pattern links, reference links, and sign-off

**Priority:** LOW — we write blog posts infrequently but the JSON format is fiddly.

---

### `/trident-sync` (osa-trident → osa-data)
**Sync TRIDENT metadata from osa-trident to osa-data.**

Would handle:
1. Run `sync_metadata.py --apply` in osa-trident
2. Verify metadata.json validates against schema
3. Report graph summary changes (new node types, edge counts, entity counts)
4. Check website build-time validation passes

**Priority:** LOW — Chris does this when TRIDENT data changes.

---

## Skill Design Principles

1. **Read before write.** Every skill that modifies files must read the current state first.
2. **Validate after change.** Every skill that creates data must run schema validation.
3. **Don't commit.** Skills prepare changes; the founder decides when to commit.
4. **Encode conventions, not opinions.** Skills enforce the schema, naming, and structure rules — not subjective quality judgements.
5. **Report clearly.** Always show what was created/changed and what the founder needs to do next (SVG, commit, review).
6. **Fail loudly.** If validation fails, stop and report — don't silently produce invalid data.

---

## Repo Placement

| Skill | Repo | Path |
|-------|------|------|
| `/new-pattern` | osa-data | `.claude/skills/new-pattern/SKILL.md` |
| `/pattern-audit` | osa-data | `.claude/skills/pattern-audit/SKILL.md` |
| `/new-framework` | osa-data | `.claude/skills/new-framework/SKILL.md` |
| `/svg-diagram` | osa-website | `.claude/skills/svg-diagram/SKILL.md` |
| `/osa-push` | both repos | `.claude/skills/osa-push/SKILL.md` |
| `/osa-release` | osa-data | `.claude/skills/osa-release/SKILL.md` |
| `/blog-post` | osa-website | `.claude/skills/blog-post/SKILL.md` |
| `/trident-sync` | osa-trident | `.claude/skills/trident-sync/SKILL.md` |

---

## Open Questions for Founders

1. **Which proposed skills should we build next?** Recommendation: `/new-framework` (highest ROI).
2. **Should skills be committed to the repos?** They'd be available to all founders. Currently in `.claude/skills/` which is gitignored — we'd need to un-ignore or move them.
3. **Are there workflows we're missing?** Chris's TRIDENT ingestion? Tobias's pattern review process?
4. **Should we add skills for osa-engine?** Assessment creation, test running, canvas operations?
5. **Naming conventions?** Currently using `/verb-noun`. Alternatives: `/osa:verb-noun` namespace prefix.

---

*Prepared by Vitruvius for founder review — 2026-03-11*
