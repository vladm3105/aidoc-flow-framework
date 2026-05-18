# Security Checklist

Project-agnostic security verification checklist for governance-driven repositories.

---

## Quick Reference

| Checklist | When to Use |
|:----------|:------------|
| [Pre-Commit](#pre-commit-checklist) | Before every commit |
| [Pre-PR](#pre-pr-checklist) | Before creating a PR |
| [Code Review](#code-review-checklist) | During review |
| [Deployment](#deployment-checklist) | Before environment deployment |

---

## Pre-Commit Checklist

### Secrets and Credentials

- [ ] No hardcoded secrets in staged changes
- [ ] No secret files committed (`.env`, `*.pem`, `*.key`, credentials files)
- [ ] No service-account key JSON usage where WIF/OIDC is required
- [ ] Sensitive values loaded from environment/secrets manager only

### Input and Shell Safety

- [ ] User input sanitized before SQL, shell, template, or path usage
- [ ] No path traversal risk in filesystem operations
- [ ] No inline `${{ }}` expressions inside GitHub Actions `run:` blocks
- [ ] Shell variables are quoted (`"$VAR"`) when user-controlled

### Quick Verification Commands

```bash
# Potential secret patterns in staged diff
git diff --cached | grep -iE "(password|secret|api[_-]?key|token|credential)" || echo "No obvious matches"

# Workflow shell-injection anti-pattern
rg -n "run:|\$\{\{" .github/workflows
```

---

## Pre-PR Checklist

### Code and Dependency Security

- [ ] Security-sensitive code paths reviewed (auth, permissions, data access)
- [ ] No sensitive data in logs or error responses
- [ ] Dependency updates reviewed for known vulnerabilities
- [ ] Workflow permissions are least-privilege

### Workflow and Auth Security

- [ ] No marketplace actions if your governance policy forbids them
- [ ] OIDC/WIF configuration uses short-lived credentials
- [ ] No plaintext credentials in workflow YAML

---

## Code Review Checklist

### Access and Authorization

- [ ] Protected operations require authentication
- [ ] Authorization checks enforce scope/tenant/resource boundaries
- [ ] Failure mode is deny-by-default

### Data Handling

- [ ] Sensitive data minimized and protected
- [ ] Logging excludes secrets and personal data
- [ ] Data retention behavior is documented where required

### Operations and Recovery

- [ ] Security-relevant events are auditable
- [ ] Rollback path does not widen permissions
- [ ] Critical exceptions are handled explicitly

---

## Deployment Checklist

### Pre-Deploy

- [ ] CI checks pass (lint/test/security)
- [ ] Required secrets are present in target environment
- [ ] IAM roles are least-privilege for runtime and deploy identities

### Post-Deploy

- [ ] Health checks pass
- [ ] Monitoring and alerts are active
- [ ] Rollback instructions are verified

---

## Recommended Tools

| Tool | Purpose |
|:-----|:--------|
| `gitleaks` | Secret detection |
| `bandit` | Python SAST |
| `pip-audit` | Dependency vulnerability checks |
| `trivy` | Container vulnerability checks |

---

## Related Governance Docs

- [GOVERNANCE_RULES.md](./GOVERNANCE_RULES.md)
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- [github/GITHUB_WORKFLOWS.md](./github/GITHUB_WORKFLOWS.md)
- [AI_PR_Review/README.md](./AI_PR_Review/README.md)
