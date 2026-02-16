# IPLAN-003: Phase-Gated Deployment Setup

**Phase**: Cross-phase
**Status**: Template
**Created**: {DATE}
**Issues**: #{DEPLOYMENT_SETUP_ISSUE}
**Epic**: #{INFRASTRUCTURE_EPIC}
**Applies Before**: First deployment to any environment

---

## Purpose

Configure the phase-gated deployment model where code progresses through environments based on phase completion and QA approval. This ensures only validated code reaches production.

---

## Findings

| # | Finding | Severity | Impact |
|---|---------|----------|--------|
| 1 | Cloud infrastructure must be provisioned first | HIGH | No deployment target |
| 2 | Environment secrets must be configured per-env | HIGH | Deployment auth fails |
| 3 | Phase completion checks depend on label state | MEDIUM | Premature deployments |

---

## Analysis

### Current State

- Deployment workflows exist but environments not configured
- No connection between phase labels and deployment gates
- Manual deployment without approval workflow

### Target State

Deployment flow:
```
PR Merged → Dev (auto) → Phase Complete → Staging (auto) → QA Pass → Prod (manual)
```

Gates:
- **Dev**: Automatic on merge to main
- **Staging**: Automatic when phase issues all closed
- **Prod**: Manual trigger + QA testing passed

### Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| Cloud infrastructure provisioned | Blocks | See IPLAN-00X |
| GitHub environments configured | Blocks | Configure |
| Deployment secrets set | Blocks | Configure |
| Phase labels configured | Blocks | Verify |

---

## Deployment Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        PR Workflow                               │
│  Feature Branch → PR → AI Review → Human Review → Merge to Main │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Dev Environment                              │
│  Trigger: Push to main                                          │
│  Gate: CI passes                                                │
│  Action: Auto-deploy to {GCP_PROJECT_DEV}                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Staging Environment                            │
│  Trigger: All phase:N issues closed                             │
│  Gate: Dev smoke tests pass                                     │
│  Action: Auto-deploy to {GCP_PROJECT_STAGING}                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   QA Testing                                     │
│  Trigger: Staging deployment complete                           │
│  Gate: QA test suite passes                                     │
│  Action: Create QA testing issue, await approval                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Production Environment                           │
│  Trigger: Manual (workflow_dispatch)                            │
│  Gate: QA passed + deployment window + approvals                │
│  Action: Deploy to {GCP_PROJECT_PROD} with rollback ready       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Change Execution Checklist

### Pre-Implementation
- [ ] Verify cloud infrastructure is provisioned
- [ ] Review deploy-*.yml workflow files
- [ ] Confirm CI workflow is functional

### Implementation

#### Step 1: Configure GitHub Environments
```bash
# Create environments (via GitHub UI or API)
# Settings → Environments → New environment

# Dev: No protection rules (auto-deploy)
# Staging: Require deployment branches (main only)
# Prod: Require reviewers + deployment window
```

#### Step 2: Set Environment Secrets

**For GCP:**
```bash
# Set per-environment secrets
GH_HOST={GITHUB_HOST} gh secret set GCP_PROJECT_DEV --env dev --body "{GCP_PROJECT_DEV}"
GH_HOST={GITHUB_HOST} gh secret set GCP_PROJECT_STAGING --env staging --body "{GCP_PROJECT_STAGING}"
GH_HOST={GITHUB_HOST} gh secret set GCP_PROJECT_PROD --env prod --body "{GCP_PROJECT_PROD}"
```

#### Step 3: Configure Phase Completion Check
- [ ] Verify `check-phase-completion.yml` workflow exists
- [ ] Update phase label count: `{PHASE_COUNT}` phases
- [ ] Test by closing all issues with `phase:1` label

#### Step 4: Configure Production Protections
- [ ] Add required reviewers for prod environment
- [ ] Set deployment window: {DEPLOY_WINDOW_START}:00 - {DEPLOY_WINDOW_END}:00 {TIMEZONE}
- [ ] Enable "Prevent self-review"

#### Step 5: Test End-to-End
- [ ] Merge PR to main → verify dev deployment
- [ ] Close phase issues → verify staging trigger
- [ ] Manually trigger prod → verify approval required

### Post-Implementation
- [ ] Document deployment procedures in RELEASE_PROCESS.md
- [ ] Add deployment status badges to README.md
- [ ] Configure monitoring/alerting for deployments
- [ ] Mark this plan as Complete

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Deployment fails mid-process | MEDIUM | HIGH | Rollback workflow ready |
| Phase check false positive | LOW | MEDIUM | Manual override available |
| Production incident during deploy | LOW | HIGH | Deployment window + monitoring |

---

## Rollback Procedure

1. **Automatic**: If error rate > {ERROR_RATE_THRESHOLD}%, rollback triggers
2. **Manual**: Run `rollback-prod.yml` workflow with previous version tag
3. **Emergency**: Scale to 0 and redeploy known-good revision

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {DATE} | {AUTHOR} | Initial template |
