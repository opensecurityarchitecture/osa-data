# Skills

Skill files that teach a coding agent to use OSA in a few requests instead of working the site out page by page.

## osa-security-patterns

How to find the pattern for a kind of system, get its critical controls with their framework clauses and the threats each one mitigates, and read a framework's clause list. In a test of twelve runs on three tasks in October 2026, agents given the skill answered in a median of 12 requests and about three and a half minutes. Agents left to work the site out took 23 requests and five and a half minutes. Every answer in both groups was correct.

Install for Claude Code, for one user:

```bash
mkdir -p ~/.claude/skills/osa-security-patterns
curl -fsS https://www.opensecurityarchitecture.org/skills/osa-security-patterns/SKILL.md \
  -o ~/.claude/skills/osa-security-patterns/SKILL.md
```

For one project, put it under `.claude/skills/` in that project. Other tools that support the Agent Skills format (`SKILL.md`) can use the same file.

The skill needs no key. It makes requests to `www.opensecurityarchitecture.org` only.

## osa-control-mapping

How to map an organisation's own controls to NIST SP 800-53, and then carry them to up to five of the frameworks OSA maps in one request, with the clauses they reach and the ones they do not. The method has the agent quote the control text behind every pair, map in both directions separately, check against a published crosswalk and challenge its strongest pairs before a person reviews the table. Only SP 800-53 ids are sent to OSA; the organisation's control texts stay with the agent.

Install it the same way, with `osa-control-mapping` in place of `osa-security-patterns`. A guide for people is at https://www.opensecurityarchitecture.org/foundations/map-your-controls/.

The file is served from the site so there is one address to give an agent. A change here reaches the site on the next build.

Licence: CC BY-SA 4.0, like the rest of this repository.
