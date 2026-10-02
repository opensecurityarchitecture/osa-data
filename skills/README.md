# Skills

Skill files that teach a coding agent to use OSA in a few requests instead of working the site out page by page.

## osa-security-patterns

How to find the pattern for a kind of system, get its critical controls with their framework clauses and the threats each one mitigates, and read a framework's clause list. In two test runs, an agent given the skill made about half the requests of one left to work the site out.

Install for Claude Code, for one user:

```bash
mkdir -p ~/.claude/skills/osa-security-patterns
curl -fsS https://www.opensecurityarchitecture.org/skills/osa-security-patterns/SKILL.md \
  -o ~/.claude/skills/osa-security-patterns/SKILL.md
```

For one project, put it under `.claude/skills/` in that project. Other tools that support the Agent Skills format (`SKILL.md`) can use the same file.

The skill needs no key. It makes requests to `www.opensecurityarchitecture.org` only.

The file is served from the site so there is one address to give an agent. A change here reaches the site on the next build.

Licence: CC BY-SA 4.0, like the rest of this repository.
