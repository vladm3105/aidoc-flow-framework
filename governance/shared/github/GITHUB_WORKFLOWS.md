# GitHub Workflows Documentation

Complete reference for all GitHub Actions workflows in the {PROJECT_NAME} project.

**Runner**: All workflows use `runs-on: self-hosted` (GHES does not provide hosted runners).
**Marketplace Actions**: Zero — all workflows use inline shell commands per GOVERNANCE_RULES.md §2a (GitHub Connect unreliable on GHES v3.12.4).

---

## Workflow Summary

| Workflow | File | Trigger | Purpose |
|:---------|:-----|:--------|:--------|
| [CI](#ci-workflow) | `ci.yml` | Push/PR to main, develop | Lint, type check, test, security scan |
| [Release](#release-workflow) | `release.yml` | Tag push (`v*.*.*`) | Create GitHub releases |
| [Auto Add to Project](#auto-add-to-project-workflow) | `auto-add-to-project.yml` | Issue/PR opened | Add to Project Board #{PROJECT_BOARD_NUMBER} |
| [Issue Label Sync](#issue-label-sync-workflow) | `issue-label-sync.yml` | Issue labeled/assigned/closed | Sync labels to board status, cleanup on close |
| [PR Merge Cleanup](#pr-merge-cleanup-workflow) | `pr-merge-cleanup.yml` | PR closed | Set PR board status to Done |
| [Phase Transition](#phase-transition-workflow) | `phase-transition.yml` | Manual dispatch | Bulk phase status transitions |
| [AI PR Review](#ai-pr-review-workflow) | `ai-review.yml` | PR opened/synced/ready + workflow_call | Unified AI code review ({AI_TOOL_NAME} Code CLI) |
| [Agent Dispatch](#agent-dispatch-workflow) | `agent-dispatch.yml` | Issue labeled `ai:ready` | Dispatch issues to AI agents  |
| [Deploy to Dev](#deploy-to-dev-workflow) | `deploy-dev.yml` | Phase complete | Phase-gated dev deployment with smoke tests  |
| [Check All Phases Dev](#check-all-phases-dev-workflow) | `check-all-phases-dev.yml` | After dev deploy | Check if all phases dev_deployed, trigger staging  |
| ~~Deploy PR Environment~~ | `deploy-dev-pr.yml.disabled` | — | **DEPRECATED**  |
| ~~Cleanup PR Environment~~ | `cleanup-pr-env.yml.disabled` | — | **DEPRECATED**  |
| [Create Deployment Issue](#create-deployment-issue-workflow) | `create-deployment-issue.yml` | PR merged | Auto-create deployment issues  |
| [Create QA Testing Issue](#create-qa-testing-issue-workflow) | `create-qa-testing-issue.yml` | PR merged | Auto-create QA issues for functional changes  |
| [Check Phase Completion](#check-phase-completion-workflow) | `check-phase-completion.yml` | Schedule + manual | Hourly check for phase completion  |
| [Execute QA Testing](#execute-qa-testing-workflow) | `execute-qa-testing.yml` | Deployments complete + schedule | Run QA tests on staging  |
| [Create Bug Issue](#create-bug-issue-workflow) | `create-bug-issue.yml` | QA failure | Create bug issues from test failures  |
| [Deploy to Staging](#deploy-to-staging-workflow) | `deploy-staging.yml` | Phase complete | Phase-gated staging deployment  |
| [Deploy to Production](#deploy-to-production-workflow) | `deploy-prod.yml` | Manual dispatch | Gradual production rollout  |
| [Rollback Production](#rollback-production-workflow) | `rollback-prod.yml` | Manual dispatch | Multi-step production rollback  |

> **Note**: Per-PR deployments (`deploy-dev-pr.yml`) have been deprecated. The project now uses phase-gated deployments via `deploy-dev.yml` → `check-all-phases-dev.yml` → `deploy-staging.yml`.

---

## Workflow Dependencies

This diagram shows how workflows trigger each other and their dependencies:

```

                           DEVELOPMENT PHASE                                   

                                                                               
   Issue Created           PR Created/Updated          PR Merged               
                                                                            
                                                                            
  auto-add-to-project     ai-review.yml          create-deployment-issue       
                                                create-qa-testing-issue      
                                                                            
  issue-label-sync              CI                                            
  (labeled/assigned)                             pr-merge-cleanup             
                                                                              
                        (must pass)                                            
                                                                               



                           DEPLOYMENT PIPELINE                                 

                                                                               
  check-phase-completion (hourly)                                              
                                                                              
         (phase N issues all closed)                                          
  deploy-dev.yml (phase N)                                                     
                                                                              
         [REQUIRES] phases 1..N-1 dev_deployed                              
         Build → Push → Deploy → Smoke Test                                 
                                                                              
         (success)                                                            
  check-all-phases-dev.yml                                                     
                                                                              
         [REQUIRES] ALL 8 phases dev_deployed                               
                                                                              
         (all complete)                                                       
  deploy-staging.yml (Phase 8 image)                                           
                                                                              
         Copy image from dev → staging                                      
         Deploy → Health Check → Acceptance Tests                           
                                                                              
         (staging verified)                                                   
  deploy-prod.yml [MANUAL]                                                     
                                                                              
         [REQUIRES] staging verified, deployment window, 2 approvers        
         Gradual rollout: 10% → 50% → 100%                                  
                                                                               



                              QA PIPELINE                                      

                                                                               
  execute-qa-testing.yml (after staging deploy OR scheduled)                   
                                                                              
         [REQUIRES] deployment complete                                     
                                                                              
         PASS → Close QA issue, board status → Done                         
                                                                              
         FAIL  create-bug-issue.yml                                      
                                                                              
                            iteration < 3 → Create bug issue (ai:ready)     
                                                                              
                            iteration ≥ 3 → Create escalation (needs-human) 
                                                                               



                           RECOVERY WORKFLOWS                                  

                                                                               
  rollback-prod.yml [MANUAL]                                                   
                                                                              
         Traffic shift to previous revision → Health check                  
                                                                               
  phase-transition.yml [MANUAL]                                                
                                                                              
         Bulk move phase issues: Backlog ↔ Todo                             
                                                                               

```

### Dependency Matrix

| Workflow | Depends On | Triggers |
|:---------|:-----------|:---------|
| `auto-add-to-project` | — | — |
| `issue-label-sync` | — | — |
| `ci.yml` | — | — |
| `ai-review.yml` | CI (implicit gate) | — |
| `release.yml` | — | — |
| `pr-merge-cleanup` | — | — |
| `create-deployment-issue` | — | — |
| `create-qa-testing-issue` | — | — |
| `check-phase-completion` | — | `deploy-dev.yml` |
| `deploy-dev.yml` | Previous phases deployed | `check-all-phases-dev.yml` |
| `check-all-phases-dev.yml` | All phases dev_deployed | `deploy-staging.yml` |
| `deploy-staging.yml` | `check-all-phases-dev.yml` | — |
| `execute-qa-testing.yml` | Deployment complete | `create-bug-issue.yml` (on failure) |
| `create-bug-issue.yml` | `execute-qa-testing.yml` | — |
| `deploy-prod.yml` | Staging verified, 2 approvers | — |
| `rollback-prod.yml` | Production deployed | — |
| `agent-dispatch.yml` | Issue labeled `ai:ready` | — |
| `phase-transition.yml` | — | — |

### Critical Paths

1. **Dev Deployment**: `check-phase-completion` → `deploy-dev` (requires all previous phases)
2. **Staging Gate**: ALL 8 phases must be `dev_deployed` before `deploy-staging` runs
3. **Production Gate**: Staging must be verified + 2 human approvers + deployment window

---

## CI Workflow

**File**: `.github/workflows/ci.yml`

### Triggers

| Event | Branches |
|:------|:---------|
| `push` | `main`, `develop` |
| `pull_request` | `main`, `develop` |

### Skip CI

Add `[skip ci]` to commit message to skip all jobs (push events only; PRs always run).

### Permissions

```yaml
permissions:
  contents: read
```

### Jobs

#### 1. Lint

| Setting | Value |
|:--------|:------|
| Runner | `self-hosted` |
| Python | System Python 3 (venv) |
| Tools | `ruff` |

**Steps**:
- Inline git clone (checkout)
- Create venv, install ruff
- Ruff linter check with GitHub output format
- Ruff formatter check (no auto-fix)

#### 2. Type Check

| Setting | Value |
|:--------|:------|
| Runner | `self-hosted` |
| Python | System Python 3 (venv) |
| Tools | `mypy`, `types-requests` |

**Steps**:
- Inline git clone (checkout)
- Create venv, install mypy
- Run mypy with `--ignore-missing-imports`
- Non-blocking (`continue-on-error: true` at step level)

#### 3. Test

| Setting | Value |
|:--------|:------|
| Runner | `self-hosted` |
| Python | 3.11, 3.12 (matrix) |
| Tools | `pytest`, `pytest-cov`, `pytest-asyncio` |

**Steps**:
- Inline git clone (checkout)
- Resolve Python binary for matrix version (falls back to `python3`)
- Create venv, install test deps + requirements
- Run pytest with coverage (exit code 5 = no tests collected passes)

#### 4. Security

| Setting | Value |
|:--------|:------|
| Runner | `self-hosted` |
| Python | System Python 3 (venv) |
| Tools | `bandit`, `safety` |

**Steps**:
- Inline git clone (checkout)
- Create venv, install bandit + safety
- Bandit security scan (excludes `./tests`)
- Safety dependency vulnerability check

### Concurrency

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

Cancels previous runs on the same branch when new commits are pushed.

---

## Release Workflow

**File**: `.github/workflows/release.yml`

### Triggers

| Event | Pattern |
|:------|:--------|
| `push` (tags) | `v*.*.*` |

### Examples

- `v1.0.0` → Release
- `v2.1.0-rc.1` → Pre-release
- `v1.0.0-beta.2` → Pre-release
- `v1.0.0-alpha.1` → Pre-release

### Steps

1. Create GitHub Release via `gh release create --generate-notes`
2. Auto-detects pre-release from tag suffix (`-rc`, `-beta`, `-alpha`)

No checkout required — `gh release create` operates via the API.

### Permissions

```yaml
permissions:
  contents: write
```

---

## Auto Add to Project Workflow

**File**: `.github/workflows/auto-add-to-project.yml`

### Triggers

| Event | Types |
|:------|:------|
| `issues` | `opened` |
| `pull_request` | `opened` |

### Configuration

| Variable | Value |
|:---------|:------|
| `PROJECT_NUMBER` | `31` |
| `ORG` | `{GITHUB_ORG}` |

### Behavior

| Item Type | Added To | Status Set | Environment Set |
|:----------|:---------|:-----------|:----------------|
| Issue | Project #{PROJECT_BOARD_NUMBER} | `Todo` | `Development` (default) |
| Pull Request | Project #{PROJECT_BOARD_NUMBER} | `In Review` | Inherited from linked issue (or `Development` if none) |

**PR Environment Inheritance**: PRs automatically inherit the Environment value from their linked issue (parsed from `Closes #X`, `Fixes #Y`, `Resolves #Z` in PR body). If no linked issue is found or the issue has no Environment set, defaults to `Development`.

### Required Secrets

| Secret | Purpose |
|:-------|:--------|
| `PROJECT_TOKEN` | PAT with `project` scope for GHE |

### GraphQL Operations

1. Add item to project using `addProjectV2ItemById` mutation
2. Get Status field ID and options
3. Set Status field value using `updateProjectV2ItemFieldValue` mutation
4. **For issues**: Set Environment field to `Development` (`37fcaf5f`)
5. **For PRs**: Parse body for linked issue → query linked issue's Environment → inherit value (or default to `Development`)

### Permissions

```yaml
permissions:
  issues: write
  pull-requests: write
  repository-projects: write
```

---

## Issue Label Sync Workflow

**File**: `.github/workflows/issue-label-sync.yml`

### Triggers

| Event | Types |
|:------|:------|
| `issues` | `labeled`, `unlabeled`, `assigned`, `closed` |

### Label-to-Status Mapping

| Event | Label/Action | Board Status |
|:------|:-------------|:-------------|
| `labeled` | `ai:in-progress` or `status:in-progress` | In Progress |
| `labeled` | `ai:review-requested` or `status:review` | In Review |
| `unlabeled` | `ai:in-progress` removed (no review label present) | Backlog |
| `assigned` | Issue assigned (no `ai:*` label present) | In Progress |
| `closed` | Issue closed (any reason) | Done |

### Close Behavior

When an issue is closed:
1. Board status set to **Done**
2. Stale labels removed: `ai:ready`, `ai:in-progress`, `ai:review-requested`, `status:planning`
3. Label removal uses REST API with 404 tolerance (labels not present are silently skipped)

### Required Secrets

| Secret | Purpose |
|:-------|:--------|
| `PROJECT_TOKEN` | PAT with `project` scope for GHE |

### Permissions

```yaml
permissions:
  issues: write
  repository-projects: write
```

---

## PR Merge Cleanup Workflow

**File**: `.github/workflows/pr-merge-cleanup.yml`

### Triggers

| Event | Condition |
|:------|:----------|
| `pull_request` | `closed` (runs for both merged and closed-without-merge) |

### Behavior

When a PR is **closed** (merged or not):
1. Finds the PR's project board item via GraphQL
2. Sets board Status to **Done**
3. Skips silently if the item is not on the project board

When a PR is **merged** (additional steps):
4. Finds linked issues (`Closes #N`, `Fixes #N`, `Resolves #N`) and sets them to **Done**

**Note**: Closed-but-not-merged PRs do NOT update linked issues (the issues remain open for a new PR).

Head branches are automatically deleted by the repo setting `delete_branch_on_merge` (enabled on the repository).

### Required Secrets

| Secret | Purpose |
|:-------|:--------|
| `PROJECT_TOKEN` | PAT with `project` scope for GHE |

### Permissions

```yaml
permissions:
  issues: write
  repository-projects: write
```

---

## Phase Transition Workflow

**File**: `.github/workflows/phase-transition.yml`

### Triggers

| Event | Inputs |
|:------|:-------|
| `workflow_dispatch` | `phase_number`, `target_status` |

### Inputs

| Input | Type | Required | Default | Description |
|:------|:-----|:---------|:--------|:------------|
| `phase_number` | choice (1-8) | Yes | --- | Phase to transition |
| `target_status` | choice | Yes | `Backlog` | Target board status |

### Target Status Options

- `Todo`
- `Backlog`

### Behavior

1. Lists open issues with label `phase:N`
2. For each issue on the project board:
   - If transitioning to **Backlog**: only moves issues currently in **Todo**
   - If transitioning to **Todo**: only moves issues currently in **Backlog**
3. Skips issues in other statuses (In Progress, In Review, Done)

### Use Case

When a phase becomes the "nearest planning phase", run this workflow to move its issues from Todo to Backlog. Use the reverse direction (Backlog to Todo) when demoting a phase.

### Required Secrets

| Secret | Purpose |
|:-------|:--------|
| `PROJECT_TOKEN` | PAT with `project` scope for GHE |

### Permissions

```yaml
permissions:
  issues: read
  repository-projects: write
```

---

## AI PR Review Workflow

**File**: `.github/workflows/ai-review.yml`

Unified workflow that runs {AI_TOOL_NAME} Code CLI in non-interactive mode (`-p`) on the self-hosted runner. Triggers directly on PRs in the home repo and can also be called as a reusable workflow from component repos.

### Triggers

| Event | Types/Inputs |
|:------|:-------------|
| `pull_request` | `opened`, `synchronize`, `ready_for_review` |
| `workflow_call` | `model`, `max-budget-usd` (inputs) |

### Inputs (for workflow_call)

| Input | Type | Required | Default | Description |
|:------|:-----|:---------|:--------|:------------|
| `model` | string | No | `sonnet` | Claude model alias (sonnet, haiku, opus) |
| `max-budget-usd` | string | No | `1.00` | Maximum API spend per review in USD |

### Component Repo Usage

Component repos call this workflow with a minimal caller file:

```yaml
# .github/workflows/ai-review.yml (in component repo)
name: AI PR Review
on:
  pull_request:
    types: [opened, synchronize, ready_for_review]
jobs:
  ai-review:
    uses: {GITHUB_ORG}/{REPO_NAME}/.github/workflows/ai-review.yml@main
    secrets: inherit
```

### Required Secrets

| Secret | Purpose |
|:-------|:--------|
| `ANTHROPIC_API_KEY` | Anthropic API key for {AI_TOOL_NAME} Code CLI |

### Skip Conditions

The workflow skips automatically when:
- PR is in draft mode
- Actor is `dependabot[bot]`
- PR has label `skip-ai-review`

### Steps

1. Verify {AI_TOOL_NAME} Code CLI is installed on runner
2. Inline git clone of PR branch
3. Fetch PR diff and metadata via `gh api`
4. Write review instructions to temp file
5. Run `claude -p` with review instructions and tools (Read, Glob, Grep, Bash)
6. Claude posts a formal GitHub review via `gh api`
7. Claude posts a conclusion comment with machine-readable JSON metadata
8. Claude applies PR label (`ai:review-passed` or `ai:review-failed`)
9. Cleanup temp files

### Concurrency

```yaml
concurrency:
  group: ai-review-${{ github.event.pull_request.number }}
  cancel-in-progress: true
```

One review per PR number. New pushes cancel in-progress reviews.

### Permissions

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write          # Required for PR label operations via /issues/{pr}/labels API
```

For architecture and review policy details, see [governance/AI_PR_Review/README.md](../AI_PR_Review/README.md).

---

## Deploy to Dev Workflow

**File**: `.github/workflows/deploy-dev.yml`

Phase-gated deployment to dev environment. Each phase deploys independently when its issues complete.

### Triggers

| Event | Inputs |
|:------|:-------|
| `workflow_dispatch` | `phase` (required) |
| `workflow_call` | `phase` (required) |

Called by `check-phase-completion.yml` when a phase's issues are all closed.

### Deployment Flow

```
check-phase-completion.yml (phase N complete)
        
        
deploy-dev.yml (phase N)
        
         Verify prerequisites (phases 1..N-1 dev_deployed)
         Build and push image (phase-N-{sha})
         Deploy to Cloud Run (dev)
         Run smoke tests
         Update phase tracking (dev_deployed or dev_failed)
        
        
check-all-phases-dev.yml (triggered on success)
```

### Smoke Tests

| Test | Endpoint | Expected |
|:-----|:---------|:---------|
| Health | `GET /health` | HTTP 200 |
| Ready | `GET /ready` | HTTP 200 |
| Version | `GET /version` | JSON with `version` field |
| Config | `GET /health/config` | HTTP 200 (optional) |

Smoke tests use `governance/scripts/workflows/smoke_test.sh` with retry logic (5 attempts, 10s delay).

### Required Secrets

| Secret | Purpose |
|:-------|:--------|
| `ELEVATED_PAT` | Clone repo with elevated permissions |
| `WIF_CREDENTIALS_DEV` | WIF credentials for dev GCP project |
| `GCP_PROJECT_DEV` | Dev project ID |
| `PROJECT_TOKEN` | GitHub Projects V2 API access |
| `TEAMS_WEBHOOK` | Teams notifications |

### Permissions

```yaml
permissions:
  contents: write
  id-token: write
  issues: write
  actions: write
```

---

## Check All Phases Dev Workflow

**File**: `.github/workflows/check-all-phases-dev.yml`

Checks if all 8 phases are `dev_deployed` and triggers staging deployment when complete.

### Triggers

| Event | Condition |
|:------|:----------|
| `workflow_dispatch` | Manual trigger |
| `workflow_call` | Called by `deploy-dev.yml` on success |

### Behavior

1. Reads `governance/cicd/phase-deployments.json`
2. Checks each phase (1-8) for status `dev_deployed` with `smoke_results: passed`
3. If ALL phases complete:
   - Posts Teams notification
   - Triggers `deploy-staging.yml` with Phase 8 image tag
4. If any phase incomplete:
   - Logs which phases are waiting
   - Exits without triggering staging

### Why Phase 8 Image?

Phases are cumulative — Phase 8 includes all Phase 1-7 functionality. Staging always receives the complete application, never partial deployments.

### Required Secrets

| Secret | Purpose |
|:-------|:--------|
| `ELEVATED_PAT` | Clone repo |
| `TEAMS_WEBHOOK` | Teams notifications |

### Permissions

```yaml
permissions:
  contents: read
  actions: write
```

---

## Deploy to Staging Workflow

**File**: `.github/workflows/deploy-staging.yml`

Deploys the complete application to staging when ALL 8 phases are `dev_deployed`. Staging is never partial.

### Triggers

| Event | Inputs |
|:------|:-------|
| `workflow_dispatch` | `image_tag` (required) |
| `workflow_call` | `image_tag` (required) |

Called by `check-all-phases-dev.yml` when all phases are complete.

### Deployment Flow

```
check-all-phases-dev.yml (all phases complete)
        
        
deploy-staging.yml (Phase 8 image)
        
         Copy image from dev registry to staging registry
         Deploy to Cloud Run (staging)
         Health check with retry
         Run full acceptance tests (all phases)
         Update staging tracking (deployed or failed)
         Close deployment issues on success
        
        
Ready for production (manual dispatch)
```

### Image Reuse

Staging receives the exact same image that was validated on dev:

```
Dev Registry:  {GCP_REGION}-docker.pkg.dev/{GCP_PROJECT_DEV}/{PROJECT_PREFIX}/{PROJECT_PREFIX}-{SERVICE_NAME}:phase-8-{sha}
        
         docker pull → docker tag → docker push
        
Staging Registry: {GCP_REGION}-docker.pkg.dev/{GCP_PROJECT_STAGING}/{PROJECT_PREFIX}/{PROJECT_PREFIX}-{SERVICE_NAME}:phase-8-{sha}
```

### Acceptance Tests

Full test suite runs against staging (not cumulative per-phase):

```bash
pytest tests/acceptance --base-url=${STAGING_URL} -n auto --timeout=300
```

Test failures create regression issues with label `ai:ready` for AI agent remediation.

### Required Secrets

| Secret | Purpose |
|:-------|:--------|
| `ELEVATED_PAT` | Clone repo with elevated permissions |
| `WIF_CREDENTIALS_DEV` | Pull image from dev registry |
| `WIF_CREDENTIALS_STAGING` | Push image and deploy to staging |
| `GCP_PROJECT_DEV` | Dev project ID |
| `GCP_PROJECT_STAGING` | Staging project ID |
| `PROJECT_TOKEN` | GitHub Projects V2 API access |
| `TEAMS_WEBHOOK` | Teams notifications |

### Permissions

```yaml
permissions:
  contents: write
  id-token: write
  issues: write
```

---

## Deploy to Production Workflow

**File**: `.github/workflows/deploy-prod.yml`

### Triggers

| Event | Inputs |
|:------|:-------|
| `workflow_dispatch` | `version`, `skip_e2e`, `rollout_strategy` |

### Inputs

| Input | Type | Required | Default | Description |
|:------|:-----|:---------|:--------|:------------|
| `version` | string | Yes | --- | Git SHA or tag to deploy |
| `skip_e2e` | boolean | No | `false` | Skip E2E verification (emergency only) |
| `rollout_strategy` | choice | Yes | `gradual` | `gradual` or `immediate` |

### Environment

- **GitHub Environment**: `production`
- **GCP Project**: `{GCP_PROJECT_PROD}`
- **Required Reviewers**: 2 (configured in GitHub environment)
- **Wait Timer**: 10 minutes
- **Deployment Window**: Mon-Thu 10am-4pm EST

### Jobs

1. **verify**: Pre-deployment checks (deployment window, staging verification)
2. **approve**: Approval gate (requires 2 reviewers via GitHub environment)
3. **deploy**: Production deployment with traffic management
4. **notify**: Post-deployment status notification

### Gradual Rollout Strategy

| Phase | Traffic | Wait |
|:------|:--------|:-----|
| 1 | 10% | 60 seconds |
| 2 | 50% | 60 seconds |
| 3 | 100% | — |

### Required Secrets

| Secret | Scope | Purpose |
|:-------|:------|:--------|
| `WIF_PROVIDER` | Repository | Workload Identity Federation provider |
| `WIF_SA_EMAIL_PROD` | Environment | Prod service account email |
| `GCP_PROJECT_STAGING` | Environment | Staging project (for pulling image) |
| `GCP_PROJECT_PROD` | Environment | Production project ID |

### Permissions

```yaml
permissions:
  contents: read
  id-token: write
```

---

## Required Secrets Summary

| Secret | Used By | Purpose |
|:-------|:--------|:--------|
| `GITHUB_TOKEN` | All (auto-provided) | Repository access |
| `PROJECT_TOKEN` | `auto-add-to-project`, `issue-label-sync`, `pr-merge-cleanup`, `phase-transition` | Projects V2 access |
| `ANTHROPIC_API_KEY` | `ai-review` | {AI_TOOL_NAME} Code CLI API key |
| `ELEVATED_PAT` | `deploy-staging`, `deploy-prod`, `check-phase-completion`, `rollback-prod` | Push commits to protected branches |
| `WIF_CREDENTIALS_DEV` | `deploy-dev-pr` | WIF credentials JSON for dev |
| `WIF_CREDENTIALS_STAGING` | `deploy-staging` | WIF credentials JSON for staging |
| `WIF_CREDENTIALS_PROD` | `deploy-prod`, `rollback-prod` | WIF credentials JSON for production |
| `GCP_PROJECT_DEV` | `deploy-dev-pr` | Dev GCP project ID |
| `GCP_PROJECT_STAGING` | `deploy-staging` | Staging GCP project ID |
| `GCP_PROJECT_PROD` | `deploy-prod`, `rollback-prod` | Production GCP project ID |
| `TEAMS_WEBHOOK` | `deploy-staging`, `deploy-prod` | Microsoft Teams notification webhook |

### Creating ELEVATED_PAT

The `ELEVATED_PAT` is a Personal Access Token that can push commits to protected branches. This is required because workflows need to update tracking files (e.g., `governance/cicd/phase-deployments.json`) on `main`.

**Step 1: Create PAT on GitHub Enterprise**

1. Go to **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token (classic)**
3. Configure:
   - **Note**: `AIOCTO Elevated PAT for CI`
   - **Expiration**: 90 days (rotate regularly)
   - **Scopes**:
     - `repo` (Full control of private repositories)
     - `workflow` (Update GitHub Action workflows)
4. Click **Generate token** and copy it

**Step 2: Add as Repository Secret**

```bash
GH_HOST={GITHUB_HOST} gh secret set ELEVATED_PAT \
  --repo {GITHUB_ORG}/{REPO_NAME} \
  --body "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**Security Notes**:
- Use a service account if available (not personal account)
- Set expiration and rotate per security policy
- The PAT owner must be a repository admin or have bypass permissions

### Workload Identity Federation (WIF) Secrets

The `WIF_CREDENTIALS_*` and `GCP_PROJECT_*` secrets enable keyless authentication to GCP. This is the **only** supported authentication method per governance rules — service account JSON keys (`GCP_SA_KEY`) are prohibited.

**Authentication Flow**:

```
GitHub Actions Workflow
        
        

  1. Read WIF_CREDENTIALS_STAGING        
     (Workload Identity Federation JSON) 

        
        

  2. gcloud auth login --cred-file       
     Exchange GitHub OIDC token for      
     short-lived GCP access token        

        
        

  3. gcloud config set project           
     Target GCP_PROJECT_STAGING          

        
        

  4. docker push / gcloud run deploy     
     Authenticated to correct project    

```

**Workflow Usage** (from `deploy-staging.yml:56-61`):

```yaml
- name: Authenticate to GCP (WIF)
  run: |
    echo '${{ secrets.WIF_CREDENTIALS_STAGING }}' > /tmp/creds.json
    gcloud auth login --cred-file=/tmp/creds.json --quiet
    gcloud config set project ${{ env.GCP_PROJECT }}
    gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet
```

**Why WIF Instead of Service Account Keys**:

| Aspect | WIF | Service Account Keys |
|:-------|:----|:---------------------|
| Credential lifetime | Short-lived (1 hour) | Long-lived (no expiration) |
| Storage risk | No secrets to leak | JSON key can be exfiltrated |
| Audit trail | Links to GitHub workflow run | Generic service account |
| Rotation | Automatic | Manual rotation required |
| Governance | Compliant | Prohibited by GOVERNANCE_RULES.md |

**Failure Modes**:

| Missing Secret | Workflow Failure |
|:---------------|:-----------------|
| `GCP_PROJECT_*` | `gcloud` commands target wrong/no project |
| `WIF_CREDENTIALS_*` | Authentication fails, no GCP access |
| Both | Workflow fails at authentication step |

**Verification**:

```bash
# List configured secrets
GH_HOST={GITHUB_HOST} gh secret list \
  --repo {GITHUB_ORG}/{REPO_NAME}

# Setup script (creates secrets automatically)
governance/scripts/project_setup/cloud/gcp/setup-environments.sh
```

---

## Configuration Files

| File | Workflow | Purpose | Status |
|:-----|:---------|:--------|:-------|
| `requirements.txt` | CI | Production dependencies | As needed |
| `requirements-dev.txt` | CI | Development dependencies | As needed |

---

## Phase-Gated Deployment Workflows

The following workflows implement the AI-first phase-gated deployment model with 4-stage iterative QA loop. See [AI_ISSUE_LIFECYCLE.md](../AI_ISSUE_LIFECYCLE.md) for architecture details. Implementation plans are available in the [plans/](../plans/) directory.

### Agent Dispatch Workflow

**File**: `.github/workflows/agent-dispatch.yml`

| Setting | Value |
|:--------|:------|
| Trigger | Issue labeled `ai:ready` |
| Purpose | Transition issue to `ai:in-progress`, notify AI agents |

**Steps**: Validate issue, change label, update board status, post to Teams.

---

### Deploy PR Environment Workflow (DEPRECATED)

**File**: `.github/workflows/deploy-dev-pr.yml.disabled`

> **DEPRECATED**: Per-PR ephemeral deployments have been replaced by phase-gated dev deployments. See [Deploy to Dev Workflow](#deploy-to-dev-workflow).

| Setting | Value |
|:--------|:------|
| Status | **Disabled** |
| Reason | Per-PR deployments are wasteful in AI-first development |
| Replacement | Phase-gated `deploy-dev.yml` |

---

### Cleanup PR Environment Workflow (DEPRECATED)

**File**: `.github/workflows/cleanup-pr-env.yml.disabled`

> **DEPRECATED**: No longer needed since per-PR ephemeral deployments are removed.

| Setting | Value |
|:--------|:------|
| Status | **Disabled** |
| Reason | No per-PR environments to clean up |

---

### Create Deployment Issue Workflow

**File**: `.github/workflows/create-deployment-issue.yml`

| Setting | Value |
|:--------|:------|
| Trigger | PR merged to main |
| Purpose | Auto-create deployment issue linked to dev issue |

**Created Issue**: `[P{phase}-Deploy-{task}]` with labels `phase:N`, `ai:deployment`.

---

### Create QA Testing Issue Workflow

**File**: `.github/workflows/create-qa-testing-issue.yml`

| Setting | Value |
|:--------|:------|
| Trigger | PR merged to main |
| Purpose | Auto-create QA issue for functional changes |

**Decision Logic**: Uses `scripts/check_qa_required.py` to skip QA for docs/cosmetic changes.

**Created Issue**: `[P{phase}-QA-{task}]` with labels `phase:N`, `ai:qa-testing`. Dormant until deployments complete.

---

### Check Phase Completion Workflow

**File**: `.github/workflows/check-phase-completion.yml`

| Setting | Value |
|:--------|:------|
| Trigger | Hourly schedule, manual dispatch |
| Purpose | Detect when all development issues in a phase are closed |

**Behavior**: Triggers staging deployment when phase is complete. Rate-limited to prevent duplicate triggers.

---

### Execute QA Testing Workflow

**File**: `.github/workflows/execute-qa-testing.yml`

| Setting | Value |
|:--------|:------|
| Trigger | Deployment complete, daily 06:00-08:00 EST |
| Purpose | Run comprehensive QA tests on staging |

**Board Status**: Sets QA issues to **Testing** (option ID `cabb455e`) at start.

**Test Types**: Smoke, unit (≥90% coverage), integration (≥70% coverage), E2E, feature-specific.

**Outcomes**:
- Pass: Close QA issue with `ai:qa-passed`, board status → Done
- Fail: Add `ai:qa-failed`, trigger bug issue creation

---

### Create Bug Issue Workflow

**File**: `.github/workflows/create-bug-issue.yml`

| Setting | Value |
|:--------|:------|
| Trigger | QA test failure |
| Purpose | Create bug fix issue with iteration tracking |

**Iteration Limit**: Max 3 attempts. After 3 failures, creates `needs-human` escalation issue.

**Created Issue**: `[P{phase}-Bug-{task}]` with labels `phase:N`, `ai:development`, `bug`, `iteration:N`, `ai:ready`.

---

### Rollback Production Workflow

**File**: `.github/workflows/rollback-prod.yml`

| Setting | Value |
|:--------|:------|
| Trigger | Manual dispatch |
| Purpose | Multi-step production rollback |

**Steps**: Shift traffic to previous revision, verify health, update tracking.

---

## Deployment Requirements

### Container Build

The `deploy-staging.yml` and `deploy-prod.yml` workflows require:

| Requirement | Location | Purpose |
|:------------|:---------|:--------|
| Dockerfile | `components/{SERVICE_NAME}/Dockerfile` | Multi-stage build for Cloud Run |
| HTTP Entry Point | `components/{SERVICE_NAME}/src/cost_guard/main.py` | Flask app with `/health` endpoint |
| Dev Dependencies | `requirements-dev.txt` (root) | Testing tools for acceptance tests |

### Health Check

Cloud Run deployments verify health before shifting traffic:

```yaml
# deploy-staging.yml health check (lines 98-110)
for i in 1 2 3 4 5; do
  sleep 15
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" ${URL}/health)
  if [ "$HTTP_CODE" == "200" ]; then
    echo "Health check passed"
    exit 0
  fi
done
```

The `/health` endpoint must return HTTP 200 with JSON:
```json
{
  "status": "healthy",
  "service": "{PROJECT_PREFIX}-{SERVICE_NAME}",
  "version": "<K_REVISION>",
  "phase": "<PHASE>"
}
```

### Deployment Architecture

| Layer | Tool | Purpose |
|:------|:-----|:--------|
| Infrastructure | Terraform | One-time GCP resource setup |
| Application | gcloud CLI | Per-phase Cloud Run deployments |
| Container | Docker | Build and push to Artifact Registry |
| Target | Cloud Run | `{GCP_REGION}`, min 1 / max 5 instances |

### First-Time Setup

Before first deployment, complete these steps:

1. **GCP Projects**: Run `governance/scripts/project_setup/cloud/gcp/setup-projects.sh`
2. **Workload Identity**: Run `governance/scripts/project_setup/cloud/gcp/setup-wif.sh`
3. **Artifact Registry**: Run `governance/scripts/project_setup/cloud/gcp/setup_artifact_registry.sh`
4. **GitHub Environments**: Run `governance/scripts/project_setup/cloud/gcp/setup-environments.sh`
5. **Terraform**: Apply `components/{SERVICE_NAME}/terraform/`

---

## Troubleshooting

### CI Failures

| Issue | Solution |
|:------|:---------|
| Ruff lint errors | Run `ruff check . --fix` locally |
| Ruff format errors | Run `ruff format .` locally |
| mypy errors | Add type annotations or `# type: ignore` |
| Test failures | Check pytest output, fix failing tests |
| Security scan findings | Review bandit/safety output, update dependencies |
| Python version not found | Install the target version on the runner host |

### Project Automation Failures

| Issue | Solution |
|:------|:---------|
| "Resource not accessible" | Verify `PROJECT_TOKEN` has `project` scope |
| "Project not found" | Check `PROJECT_NUMBER` and `ORG` values |
| "Field not found" | Verify Status field exists in project |
| GraphQL errors | Check GHE host configuration |

### AI Review Failures

| Issue | Solution |
|:------|:---------|
| {AI_TOOL_NAME} Code CLI not found | Install on runner: `npm install -g @anthropic-ai/claude-code` |
| ANTHROPIC_API_KEY missing | Add secret to repo or org settings |
| Review timeout (5 min) | Increase `max-budget-usd` or reduce diff size |
| Inline comments return 422 | Claude retries with summary-only review (stale line mapping) |
| Review not posted (doc-only PR) | Expected --- non-code files are filtered out |
| Review skipped unexpectedly | Check skip conditions: draft PR, dependabot, `skip-ai-review` label |

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 5.0 | {DATE} | Phase-gated unified deployment model. Added `deploy-dev.yml` (phase-gated with smoke tests), `check-all-phases-dev.yml` (staging gate). Updated `deploy-staging.yml` to accept `image_tag` instead of `phase`. Deprecated `deploy-dev-pr.yml` and `cleanup-pr-env.yml` (per-PR deployments removed). Added `smoke_test.sh` and `update_staging_tracking.py` scripts. |
| 4.8 | {DATE} | Environment field now mandatory: PRs inherit Environment from linked issues (parsed from Closes/Fixes/Resolves #X); defaults to Development if no linked issue; updated GraphQL Operations |
| 4.7 | {DATE} | Added Environment field to auto-add-to-project.yml: new issues get Environment=Development by default; updated Behavior and GraphQL Operations sections |
| 4.6 | {DATE} | Updated Deploying/Testing status option IDs with actual values (ea04ab37, cabb455e) after statuses were added to Project Board #{PROJECT_BOARD_NUMBER} |
| 4.5 | {DATE} | Added Deploying and Testing board statuses: deploy-staging.yml sets Deploying status, execute-qa-testing.yml sets Testing status. Updated Deploy to Staging and Execute QA Testing workflow documentation. |
| 4.4 | {DATE} | Fix pr-merge-cleanup.yml to handle closed-without-merge PRs: set board status to Done for all closed PRs, only update linked issues when merged |
| 4.3 | {DATE} | Added WIF Secrets section: authentication flow diagram, workflow usage example, WIF vs service account keys comparison, failure modes, verification commands |
| 4.2 | {DATE} | Added Deployment Requirements section: container build requirements, health check specification, deployment architecture, first-time setup checklist |
| 4.1 | {DATE} | Added ELEVATED_PAT documentation: creation steps, security notes, usage summary. Updated Required Secrets Summary (ELEVATED_PAT, WIF_CREDENTIALS_*, TEAMS_WEBHOOK). Removed PagerDuty secrets. |
| 4.0 | {DATE} | Added phase-gated deployment workflows: agent-dispatch, deploy-dev-pr, cleanup-pr-env, create-deployment-issue, create-qa-testing-issue, check-phase-completion, execute-qa-testing, create-bug-issue, rollback-prod. Deprecated deploy-dev.yml (replaced by deploy-dev-pr.yml). |
| 3.3 | {DATE} | Added deployment workflows: deploy-dev.yml, deploy-staging.yml, deploy-prod.yml  |
| 3.2 | {DATE} | Consolidated ai-review-reusable.yml into ai-review.yml — single unified workflow for both direct triggers and workflow_call |
| 3.1 | {DATE} | Added `issues: write` permission and conclusion comment + PR label steps to AI PR Review  |
| 3.0 | {DATE} | Remove 5 workflows (bulk-add, codeql, pr-labeler, stale, test-runner); rewrite CI and Release to zero marketplace actions; update AI review to {AI_TOOL_NAME} Code CLI; update secrets summary |
| 2.3 | {DATE} | CI: add permissions block, fix skip-ci for PRs, remove failure suppression; AI review: add GH_HOST for GHES diff fetch, add caller permissions; fix phase-transition subshell bug; clean up unused pagination vars; fix stale schedule to EST; fix release changelog fallback; remove deprecated pr-labeler repo-token |
| 2.2 | {DATE} | Add AI PR Review and AI PR Review (Reusable) workflow sections, WIF secrets, review script config files, AI review troubleshooting |
| 2.1 | {DATE} | Add issue close to Done + stale label cleanup, add PR merge cleanup workflow, document delete_branch_on_merge repo setting |
| 2.0 | {DATE} | Fix auto-add default (Backlog to Todo), fix bulk-add options (Ready to Todo), add issue-label-sync and phase-transition workflows |
| 1.0 | {DATE} | Initial documentation |
