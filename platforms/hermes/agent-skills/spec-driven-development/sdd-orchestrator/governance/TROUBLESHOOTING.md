# Troubleshooting Guide

Project-agnostic troubleshooting reference for governance workflows, GitHub automation, and deployment pipelines.

---

## Quick Reference

| Category | Section |
|:---------|:--------|
| Git operations | [§1 Git Issues](#1-git-issues) |
| GitHub CLI/API | [§2 GitHub Issues](#2-github-issues) |
| CI/CD workflows | [§3 Workflow Issues](#3-workflow-issues) |
| Cloud auth/deploy | [§4 Cloud Issues](#4-cloud-issues) |
| Python/dependencies | [§5 Python Issues](#5-python-issues) |

---

## 1. Git Issues

### Detached HEAD

**Symptom**: `HEAD detached at <commit>`

**Diagnosis**:

```bash
git status
git branch -v
```

**Recovery**:

```bash
git checkout -b recovery/<topic>
# or
git checkout <expected-branch>
```

### Non-fast-forward Push Rejected

**Diagnosis**:

```bash
git fetch origin
git log HEAD..origin/$(git branch --show-current) --oneline
```

**Recovery**:

```bash
git pull --rebase origin $(git branch --show-current)
git push
```

---

## 2. GitHub Issues

### CLI Authentication Failure

**Diagnosis**:

```bash
gh auth status
```

**Recovery**:

```bash
gh auth login
# optionally refresh scopes
gh auth refresh --scopes repo,workflow,read:org,project
```

### Project Board GraphQL Update Failure

**Diagnosis**:

```bash
gh api graphql -f query='query { viewer { login } }'
```

**Recovery**:

- Confirm token has `project` scope.
- Verify project ID, field ID, and option IDs are current.
- Re-run mutation with explicit `GH_HOST` when using an enterprise GitHub host.

---

## 3. Workflow Issues

### Workflow Not Triggering

**Diagnosis**:

```bash
gh workflow list
gh run list --limit 20
```

**Recovery**:

- Verify trigger event and branch filters in workflow YAML.
- Confirm required labels/secrets/environment variables are set.
- Check branch protection and required checks configuration.

### Label/Board Sync Drift

**Diagnosis**:

- Compare issue labels with board status.
- Inspect last run of label sync workflow.

**Recovery**:

- Reapply workflow label (`ai:in-progress` or `ai:review-requested`) to retrigger sync.
- If automation is unavailable, apply board status manually via GraphQL.

---

## 4. Cloud Issues

### OIDC/WIF Authentication Failure

**Diagnosis**:

- Confirm provider and service account identity values.
- Verify workflow runtime has required secrets.

**Recovery**:

- Re-validate provider audience/issuer settings.
- Re-validate IAM binding for workload identity user.
- Re-run setup from [AI_PR_Review/CLOUD_SETUP.md](./AI_PR_Review/CLOUD_SETUP.md).

### Deployment Failure

**Diagnosis**:

- Check workflow logs for failed step.
- Check service revision/log health in target cloud.

**Recovery**:

- Roll back to known-good revision/image.
- Re-run smoke tests.
- Re-deploy after root-cause fix.

---

## 5. Python Issues

### Dependency Resolution Failures

**Diagnosis**:

```bash
python3 -m pip check
python3 -m pip freeze | wc -l
```

**Recovery**:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### Import/Runtime Errors in CI Only

**Diagnosis**:

- Compare local and CI Python version.
- Compare local and CI dependency sets.

**Recovery**:

- Pin required versions.
- Align local execution to CI runtime.

---

## Escalation

Escalate to human owner when:

- Security exposure is suspected.
- Deployment rollback fails.
- 3+ automated retries fail for the same root cause.

Document escalation context in issue/PR comments with:

- Symptom
- Root-cause hypothesis
- Logs/commands used
- Next decision needed

---

## Related Governance Docs

- [GOVERNANCE_RULES.md](./GOVERNANCE_RULES.md)
- [SECURITY_CHECKLIST.md](./SECURITY_CHECKLIST.md)
- [github/GITHUB_WORKFLOWS.md](./github/GITHUB_WORKFLOWS.md)
- [AI_PR_Review/README.md](./AI_PR_Review/README.md)
