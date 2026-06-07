---
name: security-audit
description: Validate security requirements and assess vulnerabilities across code, dependencies, infrastructure, and configuration, with OWASP/CWE compliance and STRIDE threat modeling. Use to security-review an SDD project or its implementation.
metadata:
  tags:
    - sdd-workflow
    - utility
    - quality-assurance
  custom_fields:
    skill_category: utility
    upstream_artifacts: [SPEC]
    downstream_artifacts: []
    version: "0.6.4"
    framework_spec_version: "0.13.1"
    last_updated: "2026-05-23"
---

# security-audit

## Purpose

Ensure security requirements are properly defined, implemented, and tested, and
identify vulnerabilities across code, dependencies, infrastructure, and
configuration. Validates compliance against recognized standards (OWASP Top 10,
CWE, GDPR/HIPAA/SOC 2/PCI DSS where relevant) and performs STRIDE threat
modeling. Security requirements trace from SPEC (Layer 6) and the EARS/ADR
security topics upstream of it.

## When to Use

Use `security-audit` when:

- Reviewing the security posture of an SDD project or its implementation.
- Validating that security requirements in SPEC (and upstream EARS/ADR) are
  complete and testable.
- Scanning code, dependencies, infrastructure, or configuration for
  vulnerabilities, secrets, or compliance gaps.
- Performing threat modeling on a component or system.

Do **not** use it for general (non-security) artifact quality (use
`../quality-advisor/SKILL.md`) or traceability validation (use
`../doc-validator/SKILL.md`).

## Behavior

The audit runs as a pipeline, producing a single report:

1. **Requirements validation** — check security requirements (sourced from SPEC
   and upstream EARS/ADR) for completeness: authn/authz, data protection,
   encryption, key management; flag missing or vague requirements.
2. **Code scanning** — SAST (bandit, semgrep), dependency CVEs (safety,
   pip-audit), secret detection (detect-secrets, gitleaks), and pattern checks
   for injection, XSS, and CSRF. Critical findings block deployment.
3. **Infrastructure scanning** — IaC (checkov, tfsec), containers (trivy,
   grype), Kubernetes, and cloud/network configuration.
4. **Dependency assessment** — known CVEs, CVSS scoring, outdated and transitive
   packages, and license-compliance issues.
5. **Compliance check** — OWASP Top 10 (2021) coverage and CWE mapping, plus any
   applicable regulatory frameworks.
6. **Threat modeling** — STRIDE analysis, attack-surface and trust-boundary
   mapping, with mitigation status per threat.
7. **Report** — overall security score, findings grouped by severity
   (critical/high/medium/low) with file:line, CWE/CVE, CVSS, and fix, plus
   compliance status and prioritized remediation. Critical issues are marked as
   deployment blockers.

**Targets**: zero critical vulnerabilities, no secrets in the repository, 100%
coverage of MUST security requirements, OWASP Top 10 fully covered.

**Limitations**: cannot detect all business-logic flaws, may produce false
positives requiring manual review, and depends on current tool vulnerability
databases.

## Related Resources

- SPEC layer: `${CLAUDE_PLUGIN_ROOT}/framework/layers/06_SPEC/README.md` ·
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Upstream security topics: `${CLAUDE_PLUGIN_ROOT}/framework/layers/03_EARS/README.md` ·
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/05_ADR/README.md`
- Governance: `${CLAUDE_PLUGIN_ROOT}/framework/governance/` (ID, tagging, traceability standards)
- Related skills: `../quality-advisor/SKILL.md` · `../doc-validator/SKILL.md` ·
  `../doc-spec/SKILL.md`
- References: OWASP Top 10 (2021), CWE, OWASP ASVS
