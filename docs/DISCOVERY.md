# OSA Discovery - Phase 0 Findings

**Date:** 2026-01-23
**Status:** In Progress

---

## Executive Summary

OSA is in better shape than expected. The site was modernised to Joomla 4.5.x (current) with a professional YOOtheme template. Traffic is modest but consistent (~1,500 unique visitors/day). The real value lies in the structured pattern content with NIST control mappings - this is highly extractable.

---

## 1. Traffic Profile

### 30-Day Summary (Dec 24 2025 - Jan 23 2026)

| Metric | Daily Average | Daily Range |
|--------|---------------|-------------|
| Unique Visitors | ~1,700 | 1,100 - 4,800 |
| Page Views | ~2,000 | 1,300 - 3,500 |
| Requests | ~11,500 | 4,600 - 18,600 |
| Bandwidth | ~100 MB | 35 - 150 MB |
| Threats Blocked | ~3 | 0 - 9 |
| Cache Hit Rate | ~45% | Variable |

**Notable:** Jan 1 spike (4,148 uniques), Dec 28 spike (4,852 uniques) - likely bot activity or content shares.

### Top Pages (Jan 22, 2026 sample)

| Path | Requests | Notes |
|------|----------|-------|
| `/` | 3,117 | Homepage |
| `/library/patternlandscape` | 37 | Pattern catalogue |
| `/BB3/viewtopic.php` | 30 | Legacy phpBB forum |
| `/cms/index.php` | 27 | Old CMS path |
| `/definitions/security_patterns` | 24 | Pattern definitions |
| `/library` | 23 | Library landing |

**Key insight:** Most traffic is to homepage. Pattern library gets modest direct traffic. Legacy `/BB3/` and `/cms/` paths still being hit (redirects/404s to handle).

---

## 2. Platform Assessment

### Current Stack

| Component | Version | Status |
|-----------|---------|--------|
| CMS | Joomla 4.5.23 | Current (late 2024 release) |
| Template | YOOtheme | Modern, UIKit-based |
| Hosting | HostMonster (origin) | Shared hosting |
| CDN/WAF | Cloudflare Free | Active |
| SSL | Cloudflare (auto) | Valid |
| PHP | 8.x (assumed) | J4.5 requires it |

### Domains

| Domain | Zone ID | Status |
|--------|---------|--------|
| opensecurityarchitecture.org | `4bd122a2fbd76f9a093ace24677f68d1` | Primary |
| opensecurityarchitecture.com | `ecb5122867c695e6adfcccbfe665723b` | Active |
| securityarchitecture.org | `0c0ddc80b793f4756e0239fbe91658fb` | Active |

All on Cloudflare Free plan, same nameservers (chad.ns, maya.ns).

### Security Posture

**Good:**
- Joomla 4.5.x is current and actively maintained
- Cloudflare provides basic WAF and DDoS protection
- HTTPS enforced
- Cookie consent implemented
- `X-Frame-Options: SAMEORIGIN` set
- `Referrer-Policy: strict-origin-when-cross-origin` set

**Concerns:**
- No sitemap.xml (SEO impact)
- Legacy paths still accessible (`/BB3/`, `/cms/`, `/jcms/`)
- CSRF tokens visible in page source (normal for Joomla, but worth noting)
- Free Cloudflare = limited WAF rules
- HostMonster shared hosting = limited security controls at origin

**Recommendations:**
- Audit Joomla extensions for vulnerabilities
- Create sitemap.xml
- Set up redirects for legacy paths
- Consider Cloudflare Pro for better WAF rules

---

## 3. Content Inventory

### Site Structure

```
/
├── foundations/
│   ├── osa-landscape
│   ├── osa-actors
│   ├── osa-lifecycle
│   ├── design-principles
│   ├── how-to-use
│   ├── writing-a-pattern
│   ├── osa-taxonomy
│   └── links
├── definitions/
│   ├── it-architecture
│   ├── it-risk
│   ├── it-security-architecture
│   ├── security_patterns
│   ├── it_security_requirements
│   └── glossary
├── library/
│   ├── patternlandscape (27 patterns)
│   ├── 0802control-catalogue (150+ NIST controls)
│   ├── threat_catalogue
│   ├── icon-library
│   └── pattern-template
├── community/
│   ├── roadmap
│   ├── getting-involved
│   ├── blogs
│   ├── discussionforum
│   ├── case-studies
│   └── contributed
└── about/
    ├── why-have-osa
    ├── who-uses-osa
    ├── license-terms
    ├── faq
    └── privacy-policy
```

### Pattern Catalogue (27 patterns identified)

| ID | Pattern Name | Type |
|----|--------------|------|
| SP-001 | Pattern 001 | Pattern |
| SP-002 | Pattern 002 | Pattern |
| SP-003 | Pattern 003 | Pattern |
| SP-003.1 | Pattern 003.1 | Pattern |
| SP-006 | Pattern 006 | Pattern |
| SP-007 | Pattern 007 | Pattern |
| SP-008 | Public Web Server | Pattern |
| SP-009 | Pattern 009 | Pattern |
| SP-010 | Identity Management | Pattern |
| SP-011 | Cloud Computing | Pattern |
| SP-012 | Secure SDLC | Reserved |
| SP-013 | Data Security | Pattern |
| SP-014 | Awareness and Training | Draft |
| SP-015 | Consumer Devices for Enterprise | Pattern |
| SP-016 | DMZ Module | Module |
| SP-017 | Secure Network Zone Module | Reserved |
| SP-018 | ISMS Module | Module |
| SP-019 | Secure Ad-hoc File Exchange | Pattern |
| SP-020 | Email TLS | Pattern |
| SP-021 | Realtime Collaboration | Draft |
| SP-022 | Board Room | Pattern |
| SP-023 | Industrial Control Systems | Pattern |
| SP-024 | iPhone | Pattern |
| SP-025 | Advanced Monitoring & Detection | Pattern |
| SP-026 | PCI Full | Pattern |
| - | SOA Internal Service Usage | Pattern |
| - | SVG Test | Test |

### Pattern Structure (highly extractable)

Each pattern contains:
- **Diagram**: SVG with hyperlinked NIST controls
- **Legend**: Control interpretation for context
- **Description**: Use case explanation
- **Key control areas**: Important controls highlighted
- **Assumptions**: Context assumptions
- **Typical challenges**: Implementation challenges
- **Indications**: When to use
- **Contra-indications**: When NOT to use
- **Resistance against threats**: Threat mitigation
- **References**: External resources
- **Related patterns**: Cross-references
- **Classification**: Category
- **Release**: Version (08.02)
- **Authors/Reviewers**: Attribution

### Control Catalogue

- Based on **NIST 800-53**
- Existing mappings to:
  - ISO 17799
  - COBIT 4.1
  - PCI-DSS v2
- SQL export available
- 150+ individual controls

### Icon Library

Custom security architecture icons for diagrams.

---

## 4. Modernisation Opportunities

### High Value / Low Effort

1. **Pattern extraction to JSON/YAML** - Structure is already there
2. **Sitemap.xml generation** - Joomla can do this natively
3. **Legacy path redirects** - Simple .htaccess or Cloudflare rules
4. **RSS/Atom feeds** - Already exist, could promote

### Medium Value / Medium Effort

1. **API layer** - Expose patterns via REST API
2. **Search improvement** - Current search is basic
3. **NIST 800-53 Rev5 update** - Controls are on older revision
4. **Mobile UX** - Template is responsive but could improve

### High Value / High Effort

1. **AI-powered pattern recommendation** - Claude integration
2. **Compliance mapping expansion** - NIST CSF, CIS Controls, etc.
3. **Full replatform** - Headless CMS + modern frontend
4. **Community features** - User accounts, pattern submissions

---

## 5. Next Steps

### Immediate (This Session)

- [x] Cloudflare API access confirmed
- [x] Traffic analysis complete
- [x] Site reconnaissance complete
- [ ] Pattern content extraction proof-of-concept
- [ ] Document pattern JSON schema

### Phase 1 Planning

1. Define JSON/YAML schema for patterns
2. Build extraction script (scrape or Joomla DB export)
3. Extract all patterns to structured data
4. Version control pattern data
5. Validate data completeness

---

## Appendix: API Token

Cloudflare API token configured with read permissions:
- Zone read
- Analytics read
- DNS records read
- WAF read
- Logs read

Token expires: 2026-02-28

---

*Last updated: 2026-01-23*
