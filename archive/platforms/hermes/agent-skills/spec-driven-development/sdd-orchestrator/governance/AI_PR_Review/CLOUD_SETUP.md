# AI PR Review — Cloud/OIDC Setup

Project-agnostic setup reference for cloud authentication requirements used by AI PR review and related workflows.

> If your AI review uses only API-key authentication, cloud setup may be optional for review itself. Keep this guide for workflows that still require cloud auth (deploy, infra, validation).

---

## Scope

This guide covers:

- OIDC/WIF identity setup pattern
- service account/identity role scoping
- repository secret wiring for workflows
- verification and failure-mode checks

---

## Prerequisites

- Administrative access to cloud IAM and identity federation configuration
- GitHub admin access for repository/org secrets (enterprise variants supported)
- CLI tools installed (`gh`, cloud CLI)

---

## Setup Pattern (OIDC/WIF)

1. Create workload identity pool/provider (or equivalent federation setup).
2. Create dedicated automation identity for workflow usage.
3. Grant minimum runtime roles.
4. Configure repo secrets for provider and identity references.
5. Validate token exchange and permissions using a dry-run workflow.

---

## Required Secret Categories

| Secret Category | Purpose |
|:----------------|:--------|
| Identity Provider Reference | Locate workload identity provider |
| Automation Identity | Service account / principal used by workflow |
| Project/Subscription ID | Target environment selector |
| API Key (optional) | AI provider auth where applicable |

---

## Verification

```bash
# Verify GitHub auth
gh auth status

# Verify required secrets exist (names only)
gh secret list
```

Validation goals:

- workflow can acquire short-lived cloud credentials
- workflow can perform least-privilege calls
- no long-lived key files are required

---

## Failure Modes

| Symptom | Likely Cause | Action |
|:--------|:-------------|:-------|
| Auth token exchange fails | OIDC audience/issuer mismatch | Re-check provider config |
| Workflow lacks cloud access | Missing role binding | Re-check IAM policy |
| Workflow targets wrong environment | Incorrect env/project secret | Correct secret value |

---

## Related Docs

- [README.md](./README.md)
- [../GOVERNANCE_RULES.md](../GOVERNANCE_RULES.md)
- [../github/GITHUB_WORKFLOWS.md](../github/GITHUB_WORKFLOWS.md)
- [../SECURITY_CHECKLIST.md](../SECURITY_CHECKLIST.md)
