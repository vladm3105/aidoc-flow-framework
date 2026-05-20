# Security Checklist — Template

> Replace placeholders and project-specific policy references before use.

## Project Context

- Project: {PROJECT_NAME}
- Repository: {REPO_NAME}
- Governance Rules: {GOVERNANCE_RULES_PATH}

---

## Pre-Commit

- [ ] No hardcoded credentials/secrets
- [ ] No secret files committed
- [ ] Input validation updated for new attack surfaces
- [ ] Workflow shell commands avoid inline `${{ }}` in `run:` blocks

## Pre-PR

- [ ] Security-sensitive changes reviewed
- [ ] Dependency vulnerabilities checked
- [ ] Workflow permissions least-privilege
- [ ] Auth/identity configuration matches policy

## Code Review

- [ ] Authentication and authorization boundaries enforced
- [ ] Sensitive data handling and logging reviewed
- [ ] Error handling does not leak internals

## Deployment

- [ ] CI security checks pass
- [ ] Secrets and IAM configured for target environment
- [ ] Rollback path verified

## Tooling

- `gitleaks`
- `bandit`
- `pip-audit`
- `trivy`
