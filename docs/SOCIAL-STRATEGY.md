# OSA Social & Community Strategy

Notes for building community around the relaunched OSA site.

## Modern Channels

### Professional Networks
- **LinkedIn** - Where security professionals actually are now. Company page + personal posts from founders. Good for long-form thought leadership.
- **Twitter/X** - Still relevant for infosec community, though fragmented. Quick updates, control highlights.

### Tech-Forward Platforms
- **Bluesky** - Growing tech-savvy audience, good for open source projects
- **Mastodon** - Infosec instance (infosec.exchange) has strong security community

### Community Spaces
- **Discord** - Real-time community discussions, Q&A, pattern feedback. Replaces old forum model.
- **GitHub Discussions** - Technical community close to the code. Good for contributions, feature requests.

### Content Syndication
- **Dev.to** - Cross-post blog content, good developer reach
- **Hashnode** - Similar, good SEO
- **Medium** - Broader professional audience

## Content Strategy

### Regular Series Ideas
- **Control of the Week** - Deep dive on one NIST control with all its framework mappings
- **Pattern Spotlight** - Highlight one pattern with real-world use cases
- **Framework Friday** - Compare how different frameworks approach the same security domain
- **Mapping Monday** - Show interesting cross-framework connections

### Evergreen Content
- "ISO 27001 vs NIST 800-53: Which controls map to which?"
- "Getting started with security architecture patterns"
- "How to use OSA for compliance gap analysis"
- Framework-specific guides (e.g., "OSA for SOC 2 preparation")

### Community Engagement
- Invite guest pattern contributions
- Highlight community use cases
- Run pattern review sessions
- Security architecture AMAs

## Programmatic Content

The structured JSON data enables automated content generation:

```bash
# Example: Generate "control of the day" posts
jq -r '.[] | "Control: \(.id) - \(.name)\nFamily: \(.family_name)\nMaps to: ISO 27001, COBIT, CIS, NIST CSF, SOC 2\n#infosec #securityarchitecture"' data/controls/*.json
```

Ideas:
- Daily control tweets/posts from the catalogue
- Weekly pattern highlights
- Automated compliance mapping threads
- Framework coverage statistics

## Metrics to Track

- GitHub stars/forks
- Site traffic (Cloudflare analytics)
- Social followers/engagement
- Community contributions (PRs, issues, discussions)
- Newsletter subscribers (if we add one)

## Quick Wins

1. Create LinkedIn company page for Open Security Architecture
2. Set up GitHub Discussions on osa-data repo
3. Cross-post launch blog to Dev.to and LinkedIn
4. Create a few "control of the week" posts to test format
5. Reach out to security architecture community figures for amplification

## Notes

- Don't spread too thin - pick 2-3 channels and do them well
- Consistency beats volume - regular small posts > sporadic big efforts
- Engage, don't just broadcast - reply, share others' content, build relationships
- The structured data is a unique asset - lean into programmatic content

---

*Created: 2026-02-05*
*Status: Planning*
