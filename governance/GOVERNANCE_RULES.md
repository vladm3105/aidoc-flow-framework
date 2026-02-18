# Governance Rules

**Framework**: Specification-Driven Development (SDD)
**Project**: {PROJECT_NAME} (`{PROJECT_PREFIX}`)

> **Depth Selection**: This document applies to all SDD depths (Lite, Standard, Full). Choose your depth based on project complexity - see [SDD_DEPTH_GUIDE.md](./SDD_DEPTH_GUIDE.md).

Operational policies and conventions that govern how this project is developed. These are **rules** (how we work), distinct from [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md) (completion checklists).

## SDD Depth Variants

| Depth | Layers | Best For | Timeline |
|:------|:-------|:---------|:---------|
| **SDD-Lite** | REF → BRD-MVP → PRD-MVP → TASKS-MVP | MVPs, prototypes, solo + AI | 1-3 months |
| **SDD-Standard** | REF → BRD → PRD → EARS → ADR → SYS → REQ → TASKS | Production apps, small teams | 3-6 months |
| **SDD-Full** | All 15 layers with 4-Gate CHG | Enterprise, regulated, multi-team | 6+ months |

**Issue Creation (all depths):** Human creates REF/ → AI generates specs → AI creates issues from TASKS → AI executes

---

## Quick Reference

| I need to... | Read |
|:-------------|:-----|
| Process a GitHub issue as AI agent | [Issue Processing Workflow](#issue-processing-workflow-mandatory) (this doc §3) |
| Check if my work is complete | [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md) |
| Know which branch to create | [BRANCHING_STRATEGY.md](./BRANCHING_STRATEGY.md) |
| Tag and release a component | [RELEASE_PROCESS.md](./RELEASE_PROCESS.md) |
| Understand human vs AI task split | [ROLES_AND_TOOLS.md](./ROLES_AND_TOOLS.md) |
| Set up gh CLI or MCP servers | [GITHUB_TOOLS_SETUP.md](./github/GITHUB_TOOLS_SETUP.md) |
| Configure GitHub Actions workflows | [GITHUB_WORKFLOWS.md](./github/GITHUB_WORKFLOWS.md) |
| Set up project board, labels, fields | [GITHUB_PROJECT_SETUP.md](./github/GITHUB_PROJECT_SETUP.md) |
| Understand the phase timeline | [ROADMAP-TEMPLATE.md](./templates/ROADMAP-TEMPLATE.md) |
| Find task specs and sprint schedules | [PROJECT_PLAN-TEMPLATE.md](./templates/PROJECT_PLAN-TEMPLATE.md) |
| Review AI time estimates | [AI_TIME_ESTIMATION.md](./AI_TIME_ESTIMATION.md) |
| See execution adjustments and corrections | [templates/IPLAN-TEMPLATE.md](./templates/IPLAN-TEMPLATE.md) |
| Understand monorepo structure | [REPOSITORY_STRATEGY.md](./REPOSITORY_STRATEGY.md) + [HOME_REPO.md](./HOME_REPO.md) |
| Read the project executive summary | [PROJECT_KICKOFF_PLAN-TEMPLATE.md](./templates/PROJECT_KICKOFF_PLAN-TEMPLATE.md) |
| Read universal AI agent rules | [README_AIAGENT.md](./templates/README_AIAGENT.md) |
| Find PR reviewers / CODEOWNERS | [CONTRIBUTING.md](./templates/CONTRIBUTING.md) |
| Set up or troubleshoot AI PR review | [AI_PR_Review/](./AI_PR_Review/) (overview, local setup, onboarding) |
| Conduct on-demand AI agent PR review | [AI_AGENT_REVIEW_WORKFLOW.md](./AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md) |
| Use local AI ({AI_TOOL_NAME} Code, Gemini CLI) to review a PR | [MANUAL_REVIEW_GUIDE.md](./AI_PR_Review/MANUAL_REVIEW_GUIDE.md) |
| Set up or manage GHES self-hosted runner | [GHES_RUNNER_GUIDE.md](./scripts/ghes-runner/GHES_RUNNER_GUIDE.md) |

> **Canonical file index**: [HOME_REPO.md](./HOME_REPO.md) (directory tree) | **Categorized links**: [PROJECT_KICKOFF_PLAN.md §9](./PROJECT_KICKOFF_PLAN.md)

---

## 1. Communication

| Rule | Detail |
|:-----|:-------|
| **Channels** | Microsoft Teams and Email only. Alternative: {COMMUNICATION_TOOL_ALT}. |
| **MCP Server** | Use `teams` MCP server for Teams integration |
| **Notifications** | Budget alerts, remediation actions, and system notifications go to Teams/Email |
| **GitHub** | Issue comments and PR reviews are the primary async communication channel |

---

## 2. Security Posture

| Rule | Detail | Reference |
|:-----|:-------|:----------|
| **Authentication** | Workload Identity Federation (WIF) for all GCP auth. No service account JSON keys. | ADR-002 |
| **CI/CD Secrets** | `GCP_PROJECT_ID`, `GCP_WORKLOAD_IDENTITY_PROVIDER`, `GCP_SERVICE_ACCOUNT`. Never `GCP_SA_KEY`. | [GITHUB_TOOLS_SETUP.md](./github/GITHUB_TOOLS_SETUP.md) |
| **Branch Protection** | `main` is protected. All changes via PR. Minimum 1 review. No force-push. | [BRANCHING_STRATEGY.md](./BRANCHING_STRATEGY.md) |
| **PR Reviewers** | Auto-assigned via CODEOWNERS; fallback: assign from reviewer roster. At least 1 reviewer per PR. | [CODEOWNERS](../.github/CODEOWNERS), [CONTRIBUTING.md](../CONTRIBUTING.md) §Reviewers |
| **AI Trust Boundary** | AI has no access to: GCP service account keys, API tokens, production databases, customer data, billing credentials. | [ROLES_AND_TOOLS.md](./ROLES_AND_TOOLS.md) |
| **Service Remediation** | Scale-to-0 only for cost guard actions. Never `services.delete` (destructive, irreversible). | GCP-COST-GUARD.md |
| **No Marketplace Actions** | All GitHub Actions workflows must be self-contained — no marketplace actions (`actions/checkout`, `actions/setup-python`, etc.). GitHub Connect is unreliable on GHES v3.12.4. Use inline shell commands instead. | §2a below |

### 2a. No Marketplace Actions (Mandatory)

GHES v3.12.4 does not have reliable GitHub Connect to `github.com`. All workflows **must** use inline shell commands instead of marketplace actions. This applies to the home repo **and** all component repos.

**Prohibited**: Any `uses:` referencing an external action (e.g., `actions/checkout@v4`, `actions/setup-python@v5`, `google-github-actions/auth@v2`, `hashicorp/setup-terraform`).

**Allowed**: `uses:` referencing a **local org reusable workflow** (e.g., `{GITHUB_ORG}/{REPO_NAME}/.github/workflows/ai-review-reusable.yml@main`).

**Replacements**:

| Marketplace Action | Self-Contained Replacement |
|:-------------------|:--------------------------|
| `actions/checkout@v4` | `git clone "https://${GITHUB_SERVER_URL#https://}/${GITHUB_REPOSITORY}.git" . --depth 1` |
| `actions/setup-python@v5` | Use runner-installed Python (`python3`); install specific version via `apt-get` or `pyenv` if needed |
| `google-github-actions/auth@v2` | Manual WIF OIDC exchange: request `$ACTIONS_ID_TOKEN_REQUEST_URL`, exchange via STS API, activate `gcloud` |
| `hashicorp/setup-terraform` | `curl -fsSL` download from releases.hashicorp.com |
| `orhun/git-cliff-action@v3` | `cargo install git-cliff` or download prebuilt binary |
| `softprops/action-gh-release@v2` | `gh release create "$TAG" --title "$TAG" --notes "$NOTES"` |
| `codecov/codecov-action@v4` | Codecov bash uploader or skip |

**Checkout pattern** (used in all workflows):

```yaml
- name: Checkout
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    rm -rf "${GITHUB_WORKSPACE}"/* "${GITHUB_WORKSPACE}"/.[!.]* 2>/dev/null || true
    CLONE_BRANCH="${GITHUB_HEAD_REF:-$GITHUB_REF_NAME}"
    git clone "https://x-access-token:${GH_TOKEN}@${GITHUB_SERVER_URL#https://}/${GITHUB_REPOSITORY}.git" \
      "${GITHUB_WORKSPACE}" --depth 1 --branch "${CLONE_BRANCH}"
```

**WIF auth pattern** (no marketplace action):

```yaml
- name: Authenticate to GCP (WIF)
  env:
    WIF_PROVIDER: ${{ secrets.WIF_PROVIDER }}
    WIF_SA_EMAIL: ${{ secrets.WIF_SA_EMAIL }}
  run: |
    # 1. Get GitHub OIDC token
    OIDC_TOKEN=$(curl -sS -H "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" \
      "${ACTIONS_ID_TOKEN_REQUEST_URL}&audience=https://iam.googleapis.com/${WIF_PROVIDER}" \
      | jq -r '.value')
    # 2. Exchange for GCP access token via STS
    ACCESS_TOKEN=$(curl -sS -X POST "https://sts.googleapis.com/v1/token" \
      -H "Content-Type: application/json" \
      -d "{
        \"grant_type\": \"urn:ietf:params:oauth:grant-type:token-exchange\",
        \"audience\": \"//iam.googleapis.com/${WIF_PROVIDER}\",
        \"scope\": \"https://www.googleapis.com/auth/cloud-platform\",
        \"requested_token_type\": \"urn:ietf:params:oauth:token-type:access_token\",
        \"subject_token\": \"${OIDC_TOKEN}\",
        \"subject_token_type\": \"urn:ietf:params:oauth:token-type:jwt\"
      }" | jq -r '.access_token')
    # 3. Impersonate service account
    SA_TOKEN=$(curl -sS -X POST \
      "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/${WIF_SA_EMAIL}:generateAccessToken" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "Content-Type: application/json" \
      -d '{"scope": ["https://www.googleapis.com/auth/cloud-platform"], "lifetime": "3600s"}' \
      | jq -r '.accessToken')
    # 4. Export token for downstream steps
    echo "::add-mask::${SA_TOKEN}"
    echo "GCP_ACCESS_TOKEN=${SA_TOKEN}" >> "$GITHUB_ENV"
    echo "CLOUDSDK_AUTH_ACCESS_TOKEN=${SA_TOKEN}" >> "$GITHUB_ENV"
```

---

## 3. AI Workflow

### Label Lifecycle (3 workflow labels)

```
ai:ready → ai:in-progress → ai:review-requested → (PR merge)
```

`ai:approved` and `ai:rejected` labels are **not used** — PR approval status is sufficient. Note: PR-scoped labels `ai:review-passed` and `ai:review-failed` serve a different purpose (AI review outcome), see **PR Review Labels** below.

| Label | Set By | Meaning |
|:------|:-------|:--------|
| `ai:ready` | Human | Task is well-specified and ready for AI implementation |
| `ai:in-progress` | AI/Automation | AI agent is actively working on the task |
| `ai:review-requested` | AI/Automation | AI work complete, human review needed |

### Issue Type Labels (4 types)

The 4-stage iterative QA loop uses these issue type labels:

| Label | Color | Purpose | Created By |
|:------|:------|:--------|:-----------|
| `ai:development` | `#5319E7` (purple) | Development issue (code changes) | Human |
| `ai:deployment` | `#006B75` (teal) | Deployment issue (deploy instructions) | `create-deployment-issue.yml` |
| `ai:qa-testing` | `#7B68EE` (medium purple) | QA testing issue | `create-qa-testing-issue.yml` |
| `bug` | `#D73A4A` (red) | Bug fix (used with `ai:development`) | `create-bug-issue.yml` |

### QA Status Labels (6 labels)

| Label | Color | Applied When | Set By |
|:------|:------|:-------------|:-------|
| `ai:qa-passed` | `#28A745` (green) | QA tests pass | `execute-qa-testing.yml` |
| `ai:qa-failed` | `#DC3545` (red) | QA tests fail | `execute-qa-testing.yml` |
| `iteration:1` | `#6C757D` (gray) | First bug fix attempt | `create-bug-issue.yml` |
| `iteration:2` | `#6C757D` (gray) | Second bug fix attempt | `create-bug-issue.yml` |
| `iteration:3` | `#6C757D` (gray) | Third (final) bug fix attempt | `create-bug-issue.yml` |
| `needs-human` | `#FF0000` (bright red) | Max iterations exceeded | `create-bug-issue.yml` |

### PR Review Labels (2 labels)

Distinct from issue-scoped `ai:ready`/`ai:in-progress`/`ai:review-requested`, these labels track **AI review outcome on PRs**:

| Label | Color | Applied When | Scope |
|:------|:------|:-------------|:------|
| `ai:review-passed` | Green (#0e8a16) | APPROVE or COMMENT (low-only) | PRs (home + component repos) |
| `ai:review-failed` | Red (#b60205) | REQUEST_CHANGES | PRs (home + component repos) |

**Rules**:
- Labels are **replaced** on each review (not accumulated). A re-review that passes replaces `ai:review-failed` with `ai:review-passed`.
- Applied by both the automated CI workflow (`ai-review-reusable.yml`) and on-demand agent reviews.
- A **conclusion comment** is also posted with a machine-readable JSON metadata block for downstream automation.

### Board Status Sync (Mandatory)

**Rule**: Labels and board status are **two separate systems**. The `issue-label-sync.yml` workflow automatically syncs board status when labels change. AI agents should update labels via MCP; the workflow handles the corresponding board status update.

> **Automation**: When AI applies `ai:in-progress` or `ai:review-requested` labels, the `issue-label-sync.yml` workflow automatically updates the board status. Manual GraphQL updates are only needed when: (1) the workflow is unavailable, (2) cross-repo operations, or (3) bulk fixes.

| Label Event | Board Status Change | Status Option ID | Automation |
|:------------|:-------------------|:-----------------|:-----------|
| `ai:in-progress` applied | → In Progress | `{BOARD_OPTION_IN_PROGRESS}` | `issue-label-sync.yml` |
| `ai:review-requested` applied | → In Review | `{BOARD_OPTION_IN_REVIEW}` | `issue-label-sync.yml` |
| `ai:deployment` issue starts deploying | → Deploying | `ea04ab37` | `deploy-staging.yml` |
| `ai:qa-testing` issue starts tests | → Testing | `cabb455e` | `execute-qa-testing.yml` |
| `ai:in-progress` removed (no review label) | → Backlog | `e7eaf9e5` | `issue-label-sync.yml` |
| Issue closed | → Done | `{BOARD_OPTION_DONE}` | `issue-label-sync.yml` (also removes stale labels) |
| PR merged/closed | → Done | `{BOARD_OPTION_DONE}` | `pr-merge-cleanup.yml` |

### Environment Field (Mandatory)

The **Environment** field tracks deployment phase independently of issue Status. This field is **mandatory** for all issues and PRs.

| Environment | Option ID | Set By |
|:------------|:----------|:-------|
| Planning | `d1fd5954` | Manual (pre-development) |
| Development | `37fcaf5f` | `auto-add-to-project.yml` (default for issues) |
| Staging | `ab95acae` | `deploy-staging.yml` (on successful deployment) |
| Production | `d4abfe48` | `deploy-prod.yml` (on successful deployment) |

**Field ID**: `MDI2OlByb2plY3RWMlNpbmdsZVNlbGVjdEZpZWxkMTI3OQ==` (verify against Project Board #{PROJECT_BOARD_NUMBER} if issues occur)

**Rules**:
1. **Issues**: Automatically get Environment=`Development` when created
2. **PRs**: Inherit Environment from linked issue (parsed from `Closes #X`, `Fixes #Y`, `Resolves #Z`)
3. **PRs without linked issue**: Default to Environment=`Development`
4. **Deployment Pipeline view**: Groups items by Environment field

**Tool Strategy**:
- **GitHub MCP** (`github-{PROJECT_PREFIX}-{PROJECT_PREFIX}`): Use for issue/PR CRUD operations (labels, comments, state)
- **gh CLI**: Use for Projects V2 board status updates (requires GraphQL)

**Update issue labels** (via GitHub MCP — Primary):

```python
# Load MCP tool first
ToolSearch(query="+github issue")

# Update issue labels
mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__issue_write(
    method="update",
    owner="{GITHUB_ORG}",
    repo="{REPO_NAME}",
    issue_number=123,
    labels=["ai:in-progress", "phase:1"]
)
```

**Update board status** (via gh CLI — Required for Projects V2):

```bash
GH_HOST={GITHUB_HOST} gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "MDk6UHJvamVjdFYyOTg="
    itemId: "<ITEM_ID>"
    fieldId: "MDI2OlByb2plY3RWMlNpbmdsZVNlbGVjdEZpZWxkMTIyMA=="
    value: { singleSelectOptionId: "<OPTION_ID>" }
  }) { projectV2Item { id } }
}'
```

To find an issue's `itemId`, query the project items and match by issue number.

**Note**: Labels and board status are **two separate systems**:
- Use MCP `issue_write` for labels → fast, direct tool call
- Use gh CLI GraphQL for board status → Projects V2 not exposed in MCP

**Automated transitions**: All board status changes in the table above are handled by GitHub Actions workflows. Manual updates are only needed when workflows are unavailable (e.g., cross-repo operations or bulk fixes).

**On issue close**: The `issue-label-sync.yml` workflow automatically removes stale labels (`ai:ready`, `ai:in-progress`, `ai:review-requested`, `status:planning`).

**On PR merge**: Head branches are automatically deleted by the repo setting `delete_branch_on_merge`.

### Issue Processing Workflow (Mandatory)

**Rule**: When an AI agent picks up a GitHub issue labeled `ai:ready`, the agent **must** follow this 4-phase workflow before writing any implementation code. Skipping phases or rushing to implementation produces lower-quality work and causes rework.

#### Phase 1: Issue Analysis

Thoroughly review the issue and its context:

| Step | Action | Tool/Method |
|:-----|:-------|:------------|
| 1.1 | Read the issue body, acceptance criteria, and comments | `gh issue view <NUMBER>` |
| 1.2 | Identify and read all linked/dependent issues | Parse `Depends on #X`, `Blocks #Y` from body |
| 1.3 | Read related governance docs referenced in the issue | `Read` tool on governance/ files |
| 1.4 | Read relevant ADRs, specs, and technical docs | `Read` tool on docs/adr/, docs/core/ |
| 1.5 | Review existing code/files that will be modified | `Glob`, `Grep`, `Read` as needed |
| 1.6 | Check PROJECT_PLAN.md for phase context and dependencies | Locate task in §2 or §3 |

**Output**: Mental model of the full scope, constraints, and dependencies.

#### Phase 2: Implementation Plan Creation

Create a detailed plan and save to file:

| Step | Action |
|:-----|:-------|
| 2.1 | Create file: `governance/plans/IPLAN-NNN_{issue-slug}.md` (next ID from plans/README.md) |
| 2.2 | Document: purpose, scope, affected files, step-by-step implementation tasks |
| 2.3 | Include: acceptance criteria mapping (which plan step satisfies which criterion) |
| 2.4 | List: risks, edge cases, testing approach |
| 2.5 | Reference: dependent issues, related ADRs/specs |

**Template** (minimum viable):

```markdown
# IPLAN-NNN: {Issue Title}

**Issue**: #{NUMBER}
**Phase**: {N}
**Status**: Draft
**Created**: {YYYY-MM-DD}

---

## Scope

{What this plan covers and explicitly excludes}

## Implementation Steps

1. {Step 1 — specific file/action}
2. {Step 2 — specific file/action}
...

## Acceptance Criteria Mapping

| AC | Plan Step | Verification |
|:---|:----------|:-------------|
| AC-1: {criterion text} | Step 2 | {how to verify} |
| AC-2: {criterion text} | Step 4 | {how to verify} |

## Risks & Edge Cases

- {Risk 1}
- {Edge case 1}

## Testing Approach

- {Test strategy}
```

#### Phase 3: Plan Review & Refinement

Review the plan from scratch and improve it:

| Step | Action |
|:-----|:-------|
| 3.1 | Re-read the plan as if seeing it for the first time |
| 3.2 | Identify gaps: missing steps, unclear actions, unaddressed acceptance criteria |
| 3.3 | Check for dependencies: are prerequisite steps in correct order? |
| 3.4 | Verify completeness: does every acceptance criterion have a mapped step? |
| 3.5 | Add missing details, clarify ambiguous steps, fix ordering issues |
| 3.6 | Update plan status: `Draft` → `Approved` (self-approval for AI agents) |

**Gap checklist**:
- [ ] All acceptance criteria mapped to implementation steps
- [ ] All files to be created/modified explicitly listed
- [ ] Testing/verification method defined for each criterion
- [ ] No implicit assumptions — all dependencies documented
- [ ] Error handling and edge cases addressed

#### Phase 4: Transition to Implementation

Only after Phases 1-3 are complete, proceed to the [Pre-Implementation Checklist](#pre-implementation-checklist-mandatory) below.

**Workflow summary**:
```
Issue (ai:ready)
    
    

 Phase 1: Issue Analysis          
 (read issue, deps, docs, code)   

    
    

 Phase 2: Create Plan             
 (IPLAN-NNN_{slug}.md)            

    
    

 Phase 3: Review & Refine Plan    
 (identify gaps, improve)         

    
    

 Phase 4: Pre-Implementation      
 (label, board, branch)           

    
    
Implementation begins
```

---

### Pre-Implementation Checklist (Mandatory)

**Rule**: After completing the [Issue Processing Workflow](#issue-processing-workflow-mandatory) above, and before writing any implementation code, the AI agent **must** execute all of the following steps in sequence, in the same turn. These are not optional — they are the gate for starting work.

1. **Change label**: `ai:ready` → `ai:in-progress` (board status auto-syncs to "In Progress" via `issue-label-sync.yml`)
2. **Create branch**: `ai/{issue}-{slug}` from `main`

**Never start implementation while the issue is still labeled `ai:ready`.** The transition to `ai:in-progress` signals to other agents and humans that work has begun.

> **Note**: Board status updates automatically when the label changes. Manual GraphQL update is only needed if the workflow fails or is unavailable.

### Post-PR Checklist (Mandatory)

**Rule**: Immediately after `gh pr create` succeeds, the AI agent **must** execute all of the following steps in sequence, in the same turn. These are not separate tasks — they are part of PR creation.

1. **Verify** each acceptance criterion in the linked issue (methods in [Acceptance Criteria Sync](#acceptance-criteria-sync-mandatory) below)
2. **Check off** verified criteria in the issue body (`- [ ]` → `- [x]`) via `gh issue edit`
3. **Change label**: `ai:in-progress` → `ai:review-requested` (board status auto-syncs to "In Review" via `issue-label-sync.yml`)
4. **Post PR link** as comment on the linked issue (PR#, URL, branch, date — format in [Issue PR Link](#issue-pr-link-mandatory) below)

**Never leave an issue in `ai:in-progress` after a PR has been created.** The transition to `ai:review-requested` is a mandatory part of PR creation, not a follow-up action.

> **Note**: Board status updates automatically when the label changes. Manual GraphQL update is only needed if the workflow fails or is unavailable.

### Acceptance Criteria Sync (Mandatory)

**Rule**: Before moving an issue to `ai:review-requested` (or any review/done status), the AI agent **must verify and then check off** acceptance criteria checkboxes (`- [ ]` → `- [x]`) in the issue body. Reviewers will reject issues with unchecked criteria.

**Verification requirement**: Do **not** blindly mark checkboxes. For each criterion, the AI agent must **actively verify** that the work is done:

| Criterion Type | Verification Method |
|:---------------|:-------------------|
| File/directory exists | Run `ls`, `gh api`, or `Glob` to confirm |
| Configuration has specific values | Read the file and confirm contents |
| Feature is implemented | Read the source code, run tests |
| CI/CD passes | Check workflow run status |
| Protection rules applied | Query the API to confirm settings |

**How to update**: After verification, use `gh issue edit <number> --body "..."` with the full body, replacing `- [ ]` with `- [x]` for each **verified** criterion. Never check an item without evidence.

**When criteria cannot be met**: If a criterion is blocked or out of scope, add a comment on the issue explaining why, and leave the checkbox unchecked.

### PR Reviewer Assignment (Mandatory)

**Primary mechanism**: [`.github/CODEOWNERS`](../.github/CODEOWNERS) auto-assigns reviewers based on file paths. No manual action needed when CODEOWNERS matches.

**Fallback**: When CODEOWNERS does not match or additional expertise is needed, AI agents **must** assign at least one reviewer from the roster in [CONTRIBUTING.md §Reviewers](../CONTRIBUTING.md#reviewer-roster).

```bash
GH_HOST={GITHUB_HOST} gh pr create --title "..." --body "..." --reviewer <username>
```

**Rules**:
- At least one reviewer per PR (enforced by branch protection)
- PR author cannot self-review — assign a **different** reviewer
- Select reviewer based on component scope (see roster for expertise areas)
- When CODEOWNERS auto-assigns, additional manual reviewers are optional

### Issue PR Link (Mandatory)

**Rule**: Immediately after creating a PR that references an issue (`Closes #N`, `Fixes #N`, `Resolves #N`), the AI agent **must** post a comment on the linked issue with the PR number and URL. This allows anyone viewing the issue on the project board (especially in "In Review" status) to navigate directly to the PR without searching.

```bash
GH_HOST={GITHUB_HOST} gh issue comment <ISSUE_NUMBER> \
  --repo {GITHUB_ORG}/<REPO> \
  --body "$(cat <<'COMMENT_EOF'
## PR Created — #<PR_NUMBER>

| Field | Value |
|:------|:------|
| **PR** | [#<PR_NUMBER>: <PR_TITLE>](<PR_URL>) |
| **Branch** | `<HEAD_BRANCH>` → `<BASE_BRANCH>` |
| **Created** | <YYYY-MM-DD HH:MM EST> |

---
_Auto-posted on PR creation._
COMMENT_EOF
)"
```

**When to post**: Once, immediately after `gh pr create` succeeds.

**When to skip**: If the PR body does not reference any issue.

### Linked Issue Verification in PR Review (Mandatory)

**Rule**: Every AI agent PR review (both automated and on-demand) **must** verify the PR against its linked issue's acceptance criteria. Code quality review alone is insufficient — the reviewer must confirm the PR delivers what the issue requires.

**Workflow**:
1. Parse the PR body for issue links (`Closes #N`, `Fixes #N`, `Resolves #N`)
2. Fetch the linked issue body and extract acceptance criteria
3. Verify each criterion against the PR diff and repo state (same methods as [Acceptance Criteria Sync](#acceptance-criteria-sync-mandatory))
4. Include a **Linked Issue Verification** section in the review summary listing each criterion and its pass/fail status
5. If criteria are not met, note the gap in the review — do not post `APPROVE`

**When no issue is linked**: Note the absence in the review comment. A missing issue link does not block the review but should be flagged.

### Issue Review History (Mandatory)

**Rule**: After every PR review (initial review and each re-review iteration), the AI agent **must** post a summary comment on the **linked issue** (`Closes #N`). This creates a review audit trail directly on the issue, allowing stakeholders to track review history without navigating to the PR.

**What to post**: A concise record containing: reviewer identity, date (EST), commit SHA, verdict (APPROVE/COMMENT/REQUEST_CHANGES), finding counts, acceptance criteria verification summary, and a link to the full PR review.

**When to post**:
- After every initial review (APPROVE, COMMENT, or REQUEST_CHANGES)
- After every re-review iteration in the fix-and-verify loop
- On escalation (3-iteration cap reached)

**When to skip**: If the PR body has no linked issue (`Closes #N`, `Fixes #N`, `Resolves #N`). The missing link is already flagged in the PR review itself.

**Format and API details**: See [AI_AGENT_REVIEW_WORKFLOW.md §7c](./AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md).

### AI PR Review (Automated)

Every PR receives an automated AI code review via the `ai-review.yml` workflow ([ADR-009](../docs/adr/009-ai-pr-review-custom-workflow.md)).

| Aspect | Detail |
|:-------|:-------|
| **Model** | {AI_TOOL_NAME} Code CLI on self-hosted runner (ANTHROPIC_API_KEY) |
| **Output** | Inline line-level comments + conclusion comment + PR labels |
| **Events** | `APPROVE`, `COMMENT`, or `REQUEST_CHANGES` (integrates with branch protection) |
| **Context** | Receives ruff/mypy output to avoid duplicate findings |
| **Skip** | Add label `skip-ai-review` to bypass on a specific PR |
| **Cost** | ~$2-5/month at 25 PRs (Claude Sonnet default) |

AI review is **advisory** — it supplements but does not replace human review. At least one human reviewer is still required per [PR Reviewer Assignment](#pr-reviewer-assignment-mandatory).

Full documentation: [AI_PR_Review/](./AI_PR_Review/) | Add to new repo: [ONBOARDING.md](./AI_PR_Review/ONBOARDING.md)

### AI Agent Review (On-Demand)

For interactive AI agent reviews using the formal GitHub Reviews API with `REQUEST_CHANGES` events, inline comments, and a fix-and-verify loop, see [AI_AGENT_REVIEW_WORKFLOW.md](./AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md). Key differences from the automated review:

- Agent uses GitHub Reviews API directly (not via GH Actions)
- Supports `REQUEST_CHANGES` event (automated review uses `APPROVE` or `COMMENT` only)
- Includes fix-and-verify feedback loop (max 3 iterations)
- Requires explicit human authorization to enter fix loop

### Co-Author Attribution

All AI-implemented commits include:
```
Co-Authored-By: {AI_TOOL_NAME} <{AI_TOOL_EMAIL}>
```

### AI Suitability

| Size | AI Role | Human Role |
|:-----|:--------|:-----------|
| XS/S | Autonomous | Review only |
| M | Autonomous with checkpoints | Review + test |
| L | AI-assisted | Leads implementation |
| XL | Human-led | AI provides research/scaffolding |

---

## 4. Naming Conventions

### Repositories

```
{PROJECT_PREFIX}-{component}
```

Examples: `{PROJECT_PREFIX}-{SERVICE_NAME}`, `{PROJECT_PREFIX}-agents`, `{PROJECT_PREFIX}-frontend`, `{PROJECT_PREFIX}-infrastructure`

### Branches

| Type | Pattern | Example |
|:-----|:--------|:--------|
| Feature | `feature/{short-name}` | `feature/budget-alerts` |
| Bugfix | `bugfix/{short-name}` | `bugfix/threshold-calc` |
| Hotfix | `hotfix/{short-name}` | `hotfix/pubsub-retry` |
| AI | `ai/{issue-number}-{short-name}` | `ai/24-costguarded-llm` |

### Issues

```
[P{phase}-{task_id}] {title}
```

Examples: `[P1-1.0] Create {PROJECT_PREFIX}-{SERVICE_NAME} repository`, `[P2-2.3] FastAPI backend skeleton`

### GCP Resources

```
{PROJECT_PREFIX}-{env}-{resource}
```

Examples: `{GCP_PROJECT_DEV}-cloud-run`, `{GCP_PROJECT_PROD}-bigquery`, `{PROJECT_PREFIX}-{SERVICE_NAME}-budget`

### Implementation Plans

```
governance/plans/IPLAN-NNN_{slug}.md
```

See [plans/README.md](./plans/README.md) for full conventions.

### MCP Servers

```
{function}-tt-{PROJECT_PREFIX}
```

`tt` = TechTrend (GitHub Enterprise instance), `{PROJECT_PREFIX}` = project prefix.

---

## 5. Sprints & Scheduling

| Rule | Detail |
|:-----|:-------|
| **Duration** | 2 weeks per sprint |
| **Naming** | `Sprint N.M` (e.g., Sprint 2.1, Sprint 2.2) |
| **Timezone** | EST ({TIMEZONE}) for all schedules |
| **Capacity** | Documented as AI hours + Human hours + 20% buffer |
| **Board Statuses** | Todo (default) → Backlog (nearest phase) → In Progress → In Review → Done |
| **Backlog rule** | Only the **next phase to execute** has sub-tasks in Backlog. All other phases stay in Todo. |

---

## 6. Document Maintenance

### Governance Doc Sync

After every sprint completion **or** any significant/breaking change, review and update:

| Document | What to Verify |
|:---------|:---------------|
| Your project's `ROADMAP.md` | Phase dates, statuses, dependencies reflect reality |
| [RELEASE_PROCESS.md](./RELEASE_PROCESS.md) | Release workflow matches current tooling and conventions |
| Your project's `PROJECT_PLAN.md` | Task statuses, schedule, gap analysis (Section 2) |

> **Note**: Create `PROJECT_PLAN.md` and `ROADMAP.md` from [templates/](./templates/).

### Sync Triggers

- Sprint boundary (mandatory)
- Dependency changes between phases
- New ADRs or technology decisions
- Scope additions or deferrals
- Schedule shifts of 1+ week

### Release Notes

When AI contributes to a release, tag in CHANGELOG:
- `[AI-implemented]` — Fully implemented by AI, human-reviewed
- `[AI-assisted]` — Human-led with AI assistance

---

## 7. Dependencies & Blocking

| Convention | Format | Example |
|:-----------|:-------|:--------|
| Blocks | `Blocks #X` in issue body | `Blocks #{PROJECT_BOARD_NUMBER}` |
| Depends on | `Depends on #Y` in issue body | `Depends on #22` |
| Closes | `Closes #Z` in PR body | `Closes #24` |

All dependency relationships must be documented in issue bodies. The PROJECT_PLAN dependency graph is the source of truth.

---

## 8. QA & Deployment

### Testing Requirements

| Test Type | Coverage Target | Enforcement |
|:----------|:----------------|:------------|
| Unit | ≥80% | CI gate (fail build) |
| Integration | ≥60% | CI gate (warning) |
| E2E | Critical paths | Pre-prod gate |

All components must have tests before merge. See [docs/qa/01-testing-strategy.md](../docs/qa/01-testing-strategy.md) for the full testing pyramid.

### CI Pipeline Stages

```
Lint → Unit Tests → Integration Tests → Security Scan → Build
```

All stages must pass before PR merge. See [docs/qa/03-ci-pipeline-spec.md](../docs/qa/03-ci-pipeline-spec.md) for stage specifications.

### Environment Promotion

| Environment | Deploy Trigger | Gate |
|:------------|:---------------|:-----|
| Development | Merge to `main` | CI passes |
| Staging | Dev deploy succeeds | Smoke tests pass |
| Production | Manual dispatch | E2E passes + 2 approvers |

See [docs/qa/04-deployment-strategy.md](../docs/qa/04-deployment-strategy.md) for rollback procedures and deployment windows.

### Security Scanning

| Tool | Purpose | Severity Threshold |
|:-----|:--------|:-------------------|
| `bandit` | Python SAST | HIGH = fail |
| `pip-audit` | Dependency vulnerabilities | HIGH = fail |
| `trivy` | Container scanning | CRITICAL = fail |
| `gitleaks` | Secret detection | Any = fail |

See [docs/qa/06-security-testing.md](../docs/qa/06-security-testing.md) for full security testing requirements.

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 2.14 | {DATE} | Clarified board status automation: labels trigger automatic sync via issue-label-sync.yml; manual GraphQL only for fallback; fixed Tool Strategy MCP name |
| 2.13 | {DATE} | Fixed MCP server naming: `github-{PROJECT_PREFIX}` → `github-{PROJECT_PREFIX}-{PROJECT_PREFIX}` to match .mcp.json config |
| 2.12 | {DATE} | Environment field now mandatory: PRs inherit from linked issues; added Rules subsection with inheritance logic |
| 2.11 | {DATE} | Added Environment Field section for Deployment Pipeline view; Environment=Development set as default for new issues via auto-add-to-project.yml |
| 2.10 | {DATE} | Updated Board Status Sync table with actual option IDs for Deploying (ea04ab37) and Testing (cabb455e) |
| 2.9 | {DATE} | Added GitHub MCP tool examples to Board Status Sync section; clarified MCP for labels vs gh CLI for Projects V2 |
| 2.8 | {DATE} | Fixed Quick Reference ADR count (8 → 9) |
| 2.7 | {DATE} | Added mandatory Issue Processing Workflow (4-phase: analyze → plan → review/refine → implement) — AI agents must create IPLAN before coding |
| 2.6 | {DATE} | Added mandatory Pre-Implementation Checklist — AI must transition `ai:ready` → `ai:in-progress` + board "In Progress" before writing any code |
| 2.5 | {DATE} | Added PR Review Labels subsection (`ai:review-passed`/`ai:review-failed`); updated AI PR Review to {AI_TOOL_NAME} Code CLI + conclusion comments |
| 2.4 | {DATE} | Added mandatory Post-PR Checklist — consolidated acceptance criteria sync, label transition, board status update, and PR link into a single atomic sequence that must execute immediately after PR creation |
| 2.3 | {DATE} | Added §2a No Marketplace Actions rule — all workflows must be self-contained, no `actions/*` or third-party marketplace actions due to unreliable GitHub Connect on GHES v3.12.4 |
| 2.2 | {DATE} | Added GHES Runner Guide to Quick Reference |
| 2.1 | {DATE} | Added mandatory Issue PR Link rule — AI agent must post PR number and URL on linked issue immediately after PR creation |
| 2.0 | {DATE} | Added mandatory Issue Review History rule — AI agent must cross-post review summary to linked issue after every review and re-review |
| 1.9 | {DATE} | Documented automated board status transitions (issue close→Done, PR merge→Done), stale label cleanup, and branch auto-delete |
| 1.8 | {DATE} | Added mandatory Linked Issue Verification rule — AI reviews must verify PR against linked issue acceptance criteria |
| 1.7 | {DATE} | Added MANUAL_REVIEW_GUIDE.md to Quick Reference — human-facing guide for local AI assistants |
| 1.6 | {DATE} | Added AI Agent Review (On-Demand) subsection — formal GitHub Reviews API with fix-and-verify loop |
| 1.5 | {DATE} | Added AI PR Review section — automated Gemini 2.5 Flash review via Vertex AI (ADR-009) |
| 1.4 | {DATE} | Added mandatory Acceptance Criteria Sync rule — AI must **verify then check off** acceptance criteria before requesting review (no blind marking) |
| 1.3 | {DATE} | Added mandatory PR Reviewer Assignment rule — AI must assign reviewer from maintainers list on every PR |
| 1.2 | {DATE} | Made Board Status Sync mandatory — AI agents must update Project Board status alongside labels; added option IDs and GraphQL example |
| 1.1 | {DATE} | Added Quick Reference table (purpose-oriented doc index) |
| 1.0 | {DATE} | Initial creation — consolidated rules from DoD, ROLES_AND_TOOLS, GITHUB_PROJECT_SETUP_AI_FIRST, GITHUB_TOOLS_SETUP, BRANCHING_STRATEGY, CLAUDE.md |
