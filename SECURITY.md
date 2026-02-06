# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in the OSA data, schemas, or tooling, please report it responsibly.

**Email:** info@opensecurityarchitecture.org

**Please include:**
- Description of the vulnerability
- Steps to reproduce
- Potential impact

We will acknowledge receipt within 48 hours and provide an initial assessment within 7 days.

## Scope

This repository contains structured JSON data (security patterns and NIST 800-53 controls) and validation scripts. The primary security concerns are:

- **Data integrity** -- unauthorised modification of pattern or control data
- **Schema validation** -- ensuring data conforms to expected structure
- **CI/CD pipeline** -- preventing supply chain compromise of the validation and dispatch workflow

## Supported Versions

| Version | Supported |
|---------|-----------|
| main    | Yes       |

## Security Practices

- All GitHub Actions are pinned to commit SHAs
- Dependencies are version-pinned
- Dependabot monitors for security updates
- Secret scanning is enabled on this repository
