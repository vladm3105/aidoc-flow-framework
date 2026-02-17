# GitHub Project Setup Guide - AI-First

Complete setup guide for GitHub Projects V2 optimized for AI-assisted development workflows.

---

## Quick Start Checklist

```
Phase 0: Prerequisites [PASS] COMPLETED
[x] GitHub CLI installed and authenticated
[x] gh-projects extension installed
[x] Project scope added to token

Phase 1: Repository Setup [PASS] COMPLETED
[x] Create repository
[x] Create labels (76 labels - exceeds 42 requirement)
[x] Create milestones (10 milestones)
[x] Add issue templates (9 templates)
[ ] Configure branch protection

Phase 2: Project Board Setup [PASS] COMPLETED
[x] Create GitHub Project V2 (#{PROJECT_BOARD_NUMBER}: {PROJECT_NAME})
[x] Add custom fields (19 fields - exceeds 7 requirement)
[x] Create views (11 views)
[x] Enable built-in workflows

Phase 3: Automation Setup [PASS] COMPLETED
[x] Create PROJECT_TOKEN secret
[x] Create ELEVATED_PAT secret (for phase-gated workflows)
[x] Add GitHub Actions workflows (18 workflows)
[x] Configure .github directory structure

Phase 4: AI Tool Configuration [PASS] COMPLETED
[x] Configure MCP servers (6 servers with -tt-{PROJECT_PREFIX} suffix)
[ ] Set up IDE integration (optional)
[ ] Create AI context directory

Phase 5: Issue Population & Kickoff [PASS] COMPLETED (Phase 1)
[x] Create Phase 1 sub-task issues (14 issues: #19-#32)
[x] Add issues to Project Board #{PROJECT_BOARD_NUMBER}
[x] Verify compliance with PROJECT_PLAN.md
[x] Update epic titles to v2.0 architecture
[x] Fix phase label descriptions with dates
[x] Update board README to v2.0 architecture
[x] Fix epic dates to 20-week timeline
[x] Recreate Phase/Component/Roadmap Phase fields with current options
[x] Set Phase 1 tasks: Status=Backlog, Phase=P1, Component=GCP Cost Guard, Sprint=2
[x] Set Roadmap Phase for all epics and research items
[ ] Add Sprints 5-10 (via UI — API limitation)
[ ] Fix Sprint 4 typo "Sprints 4" → "Sprint 4" (via UI)
[ ] Create missing views (via UI — API limitation)
[ ] Create Phase 2+ sub-tasks (just-in-time)
```

### Current Implementation Summary

| Component | Documented | Actual | Status |
|:----------|:-----------|:-------|:------:|
| Labels | 42 | 76 | [PASS] Exceeds (incl. phase-gated labels) |
| Milestones | 9 | 10 | [PASS] Exceeds |
| Custom Fields | 7 | 19 | [PASS] Exceeds |
| Workflows | 4 | 18 | [PASS] Exceeds (incl. phase-gated workflows) |
| Issue Templates | 2 | 9 | [PASS] Exceeds |
| MCP Servers | — | 6 | [PASS] Active |
| Open Issues | — | varies | [PASS] 8 epics + phase tasks |

---

## Phase 0: Prerequisites

### Required Tools

```bash
# Install GitHub CLI (if not installed)
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# Verify installation
gh --version
```

### Authentication

```bash
# Authenticate with GitHub Enterprise
gh auth login --hostname {GITHUB_HOST}

# Add required scopes
gh auth refresh --hostname {GITHUB_HOST} \
  --scopes project,repo,workflow,read:org,gist

# Verify authentication
gh auth status --hostname {GITHUB_HOST}
```

### Install gh-projects Extension

```bash
# Install extension
gh extension install github/gh-projects

# Verify
gh projects --help
```

### Set Environment Variables

```bash
# Add to ~/.bashrc or ~/.zshrc
export GH_HOST={GITHUB_HOST}
export GH_ORG="{GITHUB_ORG}"
export GH_REPO="{REPO_NAME}"
```

---

## Phase 1: Repository Setup

### 1.1 Create Repository (if new)

```bash
# Create new repository
gh repo create $GH_ORG/$GH_REPO \
  --private \
  --description "AI-agent-first cloud cost monitoring platform"

# Or clone existing
git clone https://{GITHUB_HOST}/$GH_ORG/$GH_REPO.git
cd $GH_REPO
```

### 1.2 Create Labels

Run these commands to create all required labels:

```bash
# === Type Labels (9) ===
gh label create "type:epic" --color "6e40aa" --description "Epic / parent tracking issue"
gh label create "type:feature" --color "a2eeef" --description "New feature or capability"
gh label create "type:infra" --color "d4c5f9" --description "Infrastructure / Terraform / deployment"
gh label create "type:sdk" --color "0e8a16" --description "SDK development work"
gh label create "type:adr" --color "c5def5" --description "Architecture decision record"
gh label create "type:docs" --color "0075ca" --description "Documentation updates"
gh label create "type:research" --color "fbca04" --description "Spike / investigation / analysis"
gh label create "type:tech-debt" --color "e6e6e6" --description "Technical debt cleanup"
gh label create "type:test" --color "bfd4f2" --description "Test coverage"

# === Priority Labels (4) ===
gh label create "P0-critical" --color "b60205" --description "Blocker - must resolve immediately"
gh label create "P1-high" --color "d93f0b" --description "High priority - current sprint"
gh label create "P2-medium" --color "fbca04" --description "Medium priority - next sprint"
gh label create "P3-low" --color "0e8a16" --description "Low priority - backlog"

# === AI Issue Lifecycle Labels (5) ===
gh label create "ai:ready" --color "0e8a16" --description "Task well-specified and ready for AI to implement"
gh label create "ai:in-progress" --color "fbca04" --description "AI actively working on this task"
gh label create "ai:blocked" --color "b60205" --description "AI stuck - needs human input or clarification"
gh label create "ai:review-requested" --color "6f42c1" --description "AI work complete - PR ready for human review"
gh label create "ai:human-required" --color "c5def5" --description "Task requires human implementation - not suitable for AI"

# === AI Phase-Gated Labels (7) ===
gh label create "ai:development" --color "0e8a16" --description "Development issue (phase-gated QA)"
gh label create "ai:deployment" --color "1d76db" --description "Deployment issue (auto-created on PR merge)"
gh label create "ai:qa-testing" --color "fbca04" --description "QA testing issue (auto-created for functional changes)"
gh label create "ai:qa-passed" --color "0e8a16" --description "QA tests passed"
gh label create "ai:qa-failed" --color "b60205" --description "QA tests failed"
gh label create "iteration:1" --color "fbca04" --description "Bug fix iteration 1"
gh label create "iteration:2" --color "d93f0b" --description "Bug fix iteration 2"
gh label create "iteration:3" --color "b60205" --description "Bug fix iteration 3"
gh label create "needs-human" --color "b60205" --description "Max iterations exceeded - needs human intervention"

# === AI PR Review Labels (3) ===
gh label create "ai:review-passed" --color "0e8a16" --description "AI PR review passed"
gh label create "ai:review-failed" --color "b60205" --description "AI PR review failed"
gh label create "skip-ai-review" --color "c5def5" --description "Skip AI PR review"

# === Component Labels (7) ===
gh label create "component:agents" --color "f9d0c4" --description "AI Agents (ADK)"
gh label create "component:mcp" --color "d4c5f9" --description "MCP Servers"
gh label create "component:monitoring" --color "bfd4f2" --description "Observability"
gh label create "component:ui" --color "fef2c0" --description "Frontend / Grafana / CopilotKit"
gh label create "component:auth" --color "e99695" --description "Authentication / Identity"
gh label create "component:data" --color "c5def5" --description "Database / BigQuery / data layer"
gh label create "component:sdk" --color "c2e0c6" --description "AI Telemetry SDK"

# === Status Labels (8) ===
gh label create "status:blocked" --color "b60205" --description "Blocked by dependency"
gh label create "status:needs-info" --color "fbca04" --description "Needs more information"
gh label create "status:ready" --color "0e8a16" --description "Ready for development"
gh label create "status:in-progress" --color "1d76db" --description "Work in progress"
gh label create "status:review" --color "6f42c1" --description "In review"
gh label create "status:planning" --color "d4c5f9" --description "In planning stage - may be implemented in the future"
gh label create "status:implementing" --color "fbca04" --description "Active phase - currently being implemented"
gh label create "status:suspended" --color "c5def5" --description "Work temporarily paused - will resume later"

# === Scope Labels (2) ===
gh label create "scope:mandatory" --color "b60205" --description "Required for release - must be implemented"
gh label create "scope:optional" --color "0e8a16" --description "Nice to have - not required for release"

# === Cloud Provider Labels (3) ===
gh label create "cloud:gcp" --color "4285f4" --description "Google Cloud Platform"
gh label create "cloud:aws" --color "ff9900" --description "Amazon Web Services"
gh label create "cloud:azure" --color "0078d4" --description "Microsoft Azure"

# === Cost Labels (2) ===
gh label create "cost:high-impact" --color "b60205" --description "High cost impact"
gh label create "cost:optimization" --color "0e8a16" --description "Cost optimization opportunity"

# === CI Labels (1) ===
gh label create "ci:skip" --color "c5def5" --description "Skip CI runs"

# === Phase Labels (8) ===
gh label create "phase:1" --color "1d76db" --description "Phase 1: GCP Cost Guard (Feb 24-28)"
gh label create "phase:2" --color "5319e7" --description "Phase 2: Foundation Infrastructure (Mar 3-21)"
gh label create "phase:3" --color "b4a8d1" --description "Phase 3: MCP Servers - 4 servers (Mar 24-Apr 4)"
gh label create "phase:4" --color "7057ff" --description "Phase 4: AI Agents - 5 agents (Apr 7-25)"
gh label create "phase:5" --color "d876e3" --description "Phase 5: CopilotKit Chat MVP (Apr 28-May 9)"
gh label create "phase:6" --color "0052cc" --description "Phase 6: Event Processing (May 12-23)"
gh label create "phase:7" --color "006b75" --description "Phase 7: Multi-Tenant & A2A (Conditional, May 26-Jun 20)"
gh label create "phase:8" --color "b60205" --description "Phase 8: Security & Testing (Conditional, Jun 23-Jul 18)"

# === Standard GitHub Labels (15) ===
gh label create "bug" --color "d73a4a" --description "Defect fix"
gh label create "enhancement" --color "a2eeef" --description "New feature or enhancement"
gh label create "documentation" --color "0075ca" --description "Documentation improvements"
gh label create "blocker" --color "b60205" --description "Blocking issue"
gh label create "breaking-change" --color "d93f0b" --description "Breaking change"
gh label create "security" --color "b60205" --description "Security issue"
gh label create "needs-tests" --color "fbca04" --description "Missing test coverage"
gh label create "dependencies" --color "0366d6" --description "Dependencies update"
gh label create "duplicate" --color "cfd3d7" --description "Duplicate issue"
gh label create "invalid" --color "e4e669" --description "Invalid issue"
gh label create "wontfix" --color "ffffff" --description "Will not fix"
gh label create "question" --color "d876e3" --description "Question"
gh label create "cross-repo" --color "006b75" --description "Spans multiple repositories"
gh label create "good first issue" --color "7057ff" --description "Good for newcomers"
gh label create "help wanted" --color "008672" --description "Extra attention is needed"
```

### 1.3 Create Milestones

```bash
# Sprint 0
gh api repos/$GH_ORG/$GH_REPO/milestones -f title="AIOCTO - Sprint 0: Research & Decisions" \
  -f description="Resolve blocking decisions: LLM, Auth, OTEL, Grafana, OpenCost" \
  -f due_on="{DATE}T00:00:00Z"

# Phase 1-8 (AI-optimized timeline)
gh api repos/$GH_ORG/$GH_REPO/milestones -f title="AIOCTO - Phase 1: GCP Cost Guard" \
  -f description="Standalone budget alerts + auto-remediation (AI-optimized: 1 week)" \
  -f due_on="{DATE}T00:00:00Z"

gh api repos/$GH_ORG/$GH_REPO/milestones -f title="AIOCTO - Phase 2: Foundation Infrastructure" \
  -f description="Cloud Run + FastAPI + Auth + CI/CD (3 weeks)" \
  -f due_on="2026-03-21T00:00:00Z"

gh api repos/$GH_ORG/$GH_REPO/milestones -f title="AIOCTO - Phase 3: MCP Servers" \
  -f description="4 MCP servers (3 native + OpenCost custom)" \
  -f due_on="2026-04-04T00:00:00Z"

gh api repos/$GH_ORG/$GH_REPO/milestones -f title="AIOCTO - Phase 4: AI Agents" \
  -f description="5 agents (Coordinator + 4 Domain)" \
  -f due_on="2026-04-25T00:00:00Z"

gh api repos/$GH_ORG/$GH_REPO/milestones -f title="AIOCTO - Phase 5: CopilotKit Chat" \
  -f description="AI chat interface (Grafana deferred)" \
  -f due_on="2026-05-09T00:00:00Z"

gh api repos/$GH_ORG/$GH_REPO/milestones -f title="AIOCTO - Phase 6: Event Processing" \
  -f description="Event alerts (ETL deferred)" \
  -f due_on="2026-05-23T00:00:00Z"

gh api repos/$GH_ORG/$GH_REPO/milestones -f title="AIOCTO - Phase 7: Multi-Tenant & A2A" \
  -f description="Conditional: PostgreSQL, A2A gateway" \
  -f due_on="2026-06-20T00:00:00Z"

gh api repos/$GH_ORG/$GH_REPO/milestones -f title="AIOCTO - Phase 8: Security & Testing" \
  -f description="Conditional: hardening, E2E tests" \
  -f due_on="2026-07-18T00:00:00Z"
```

### 1.4 Create Issue Templates [PASS] COMPLETED

**Current Templates (9 total)**:

| Template | File | Purpose |
|:---------|:-----|:--------|
| Bug Report | `bug_report.md` | Bug tracking |
| Feature Request | `feature_request.md` | New features |
| Architecture Proposal | `architecture_proposal.md` | ADR proposals |
| Research Task | `research_task.md` | Spike/investigation |
| Infrastructure Task | `infra_task.md` | Terraform/deployment |
| Security Report | `security_report.md` | Security issues |
| Cost Analysis | `cost_analysis.md` | Cost investigations |
| MCP Server | `mcp_server.md` | MCP server development |
| Development Issue | `development_issue.md` | 4-stage QA workflow development issues |

<details>
<summary>Example: AI-Ready Feature Template (reference)</summary>

Create `.github/ISSUE_TEMPLATE/feature-ai-ready.md`:

```markdown
---
name: Feature Request (AI-Ready)
about: Feature specification optimized for AI implementation
labels: type:feature
---

## Summary
<!-- One sentence describing the feature -->

## Acceptance Criteria
<!-- Checkbox list of specific, testable requirements -->
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Specification

### Input
<!-- Data structures, API parameters, user inputs -->

### Output
<!-- Expected results, return values, side effects -->

### Constraints
<!-- Performance requirements, security considerations, compatibility -->

## Context

### Related Files
<!-- List files that need modification -->
- `src/module/file.py`

### Dependencies
<!-- Issues or components this depends on -->
- Depends on: #

### References
<!-- Documentation, examples, similar implementations -->

## Size Estimate
<!-- XS (<2h), S (2-4h), M (1-2d), L (3-5d), XL (>1wk) -->
Size:

## AI Implementation Notes
<!-- Special instructions for AI agent -->
- Follow existing patterns in `src/`
- Maintain test coverage
- Update documentation if needed
```

Create `.github/ISSUE_TEMPLATE/bug-ai-ready.md`:

```markdown
---
name: Bug Report (AI-Ready)
about: Bug specification optimized for AI diagnosis and fix
labels: type:bug
---

## Bug Summary
<!-- One sentence describing the bug -->

## Reproduction Steps
1.
2.
3.

## Expected Behavior
<!-- What should happen -->

## Actual Behavior
<!-- What happens instead -->

## Environment
- OS:
- Version:
- Configuration:

## Error Output
```
<!-- Paste error messages, stack traces -->
```

## Suspected Location
<!-- Files or functions likely involved -->
- `src/module/file.py:123`

## Acceptance Criteria
- [ ] Bug no longer reproducible
- [ ] Regression test added
- [ ] No new warnings introduced

## Size Estimate
Size:
```

</details>

### 1.4.1 PR Template

**File**: `.github/PULL_REQUEST_TEMPLATE.md`

The PR template is optimized for the 4-stage QA workflow:

| Section | Purpose |
|:--------|:--------|
| **Linked Issue** | `Closes #N` triggers auto-creation of deployment/QA issues |
| **Type of Change** | Categorize the PR |
| **Changes Made** | Bullet list of changes |
| **Pre-Merge Checks** | CI pass + coverage thresholds |
| **Checklist** | Self-review, security, cost |

**Key Integration Points**:
- `Closes #`, `Fixes #`, `Resolves #` patterns are parsed by `create-deployment-issue.yml` and `create-qa-testing-issue.yml`
- Bug fix PRs should include iteration number and original dev issue reference
- Detailed test plans belong in the development issue (extracted to QA issue)

### 1.5 Configure Branch Protection

```bash
# Via GitHub API
gh api repos/$GH_ORG/$GH_REPO/branches/main/protection -X PUT \
  -F required_status_checks='{"strict":true,"contexts":["ci/tests"]}' \
  -F enforce_admins=false \
  -F required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  -F restrictions=null \
  -F allow_force_pushes=false \
  -F allow_deletions=false
```

---

## Phase 2: Project Board Setup

### 2.1 Create GitHub Project

```bash
# Create project
gh api graphql -f query='
mutation {
  createProjectV2(input: {
    ownerId: "ORG_ID"
    title: "{PROJECT_NAME}"
  }) {
    projectV2 {
      id
      number
      url
    }
  }
}'

# Note the project number (e.g., 31) for subsequent commands
export PROJECT_NUMBER=31
```

Or create via UI: **Organization → Projects → New Project**

### 2.2 Get Project ID

```bash
# Get project ID for subsequent operations
PROJECT_ID=$(gh api graphql -f query='
  query($org: String!, $number: Int!) {
    organization(login: $org) {
      projectV2(number: $number) { id }
    }
  }' -f org="$GH_ORG" -F number=$PROJECT_NUMBER --jq '.data.organization.projectV2.id')

echo "Project ID: $PROJECT_ID"
```

### 2.3 Create Custom Fields [PASS] COMPLETED

**Current Fields (19 total)**:

| Field | Type | Purpose |
|:------|:-----|:--------|
| Title | Text | Issue/PR title |
| Assignees | People | Assigned developers |
| Status | Single Select | Workflow status |
| Labels | Labels | Issue labels |
| Linked pull requests | PR | Associated PRs |
| Reviewers | People | PR reviewers |
| Repository | Repository | Source repo |
| Milestone | Milestone | Sprint/phase milestone |
| Start Date | Date | Work start date |
| Target Date | Date | Target completion |
| Sprints | Iteration | Sprint iteration |
| Priority | Single Select | P0-P3 priority |
| Size | Single Select | XS/S/M/L/XL sizing |
| Component | Single Select | System component |
| Cloud Provider | Single Select | GCP/AWS/Azure/K8s |
| Cost Impact | Single Select | Cost implications |
| Phase | Single Select | Project phase |
| Risk Level | Single Select | Risk assessment |
| Roadmap Phase | Single Select | Roadmap alignment |

<details>
<summary>GraphQL commands to create fields (reference only)</summary>

```bash
# Priority field
gh api graphql -f query='
mutation($projectId: ID!) {
  createProjectV2Field(input: {
    projectId: $projectId
    dataType: SINGLE_SELECT
    name: "Priority"
    singleSelectOptions: [
      {name: "P0 - Critical", color: RED, description: "Blocker - must resolve immediately"},
      {name: "P1 - High", color: ORANGE, description: "High priority - current sprint"},
      {name: "P2 - Medium", color: YELLOW, description: "Medium priority - next sprint"},
      {name: "P3 - Low", color: GREEN, description: "Low priority - backlog"}
    ]
  }) { projectV2Field { ... on ProjectV2SingleSelectField { id name } } }
}' -f projectId="$PROJECT_ID"

# Size field
gh api graphql -f query='
mutation($projectId: ID!) {
  createProjectV2Field(input: {
    projectId: $projectId
    dataType: SINGLE_SELECT
    name: "Size"
    singleSelectOptions: [
      {name: "XS", color: GRAY, description: "< 2 hours"},
      {name: "S", color: BLUE, description: "2-4 hours"},
      {name: "M", color: GREEN, description: "1-2 days"},
      {name: "L", color: YELLOW, description: "3-5 days"},
      {name: "XL", color: RED, description: "> 1 week"}
    ]
  }) { projectV2Field { ... on ProjectV2SingleSelectField { id name } } }
}' -f projectId="$PROJECT_ID"

# Component field
gh api graphql -f query='
mutation($projectId: ID!) {
  createProjectV2Field(input: {
    projectId: $projectId
    dataType: SINGLE_SELECT
    name: "Component"
    singleSelectOptions: [
      {name: "GCP Cost Guard", color: BLUE, description: "Phase 1: Standalone budget alerts"},
      {name: "MCP Servers", color: PURPLE, description: "Phase 3: 4 MCP servers (data access)"},
      {name: "AI Agents", color: ORANGE, description: "Phase 4: 5 agents (Coordinator + 4 Domain)"},
      {name: "Frontend", color: GREEN, description: "Phase 5: CopilotKit Chat MVP"},
      {name: "Backend", color: GRAY, description: "FastAPI backend"},
      {name: "Infrastructure", color: RED, description: "Phase 2: Terraform/Cloud Run"},
      {name: "Event Processing", color: YELLOW, description: "Phase 6: Webhooks + notifications"},
      {name: "Documentation", color: BLUE, description: "Docs and guides"}
    ]
  }) { projectV2Field { ... on ProjectV2SingleSelectField { id name } } }
}' -f projectId="$PROJECT_ID"

# Complexity field
gh api graphql -f query='
mutation($projectId: ID!) {
  createProjectV2Field(input: {
    projectId: $projectId
    dataType: SINGLE_SELECT
    name: "Complexity"
    singleSelectOptions: [
      {name: "Trivial", color: GRAY, description: "AI autonomous"},
      {name: "Low", color: GREEN, description: "AI autonomous"},
      {name: "Medium", color: YELLOW, description: "AI with checkpoints"},
      {name: "High", color: ORANGE, description: "Human-led, AI-assisted"},
      {name: "Critical", color: RED, description: "Human only"}
    ]
  }) { projectV2Field { ... on ProjectV2SingleSelectField { id name } } }
}' -f projectId="$PROJECT_ID"

# Start Date field
gh api graphql -f query='
mutation($projectId: ID!) {
  createProjectV2Field(input: {
    projectId: $projectId
    dataType: DATE
    name: "Start Date"
  }) { projectV2Field { ... on ProjectV2Field { id name } } }
}' -f projectId="$PROJECT_ID"

# Target Date field
gh api graphql -f query='
mutation($projectId: ID!) {
  createProjectV2Field(input: {
    projectId: $projectId
    dataType: DATE
    name: "Target Date"
  }) { projectV2Field { ... on ProjectV2Field { id name } } }
}' -f projectId="$PROJECT_ID"
```

</details>

### 2.4 Create Views

Views must be created via the GitHub UI:

**Project → + Add View**

| # | View Name | Layout | Configuration |
|:-:|:----------|:-------|:--------------|
| 1 | Sprint Board | Board | Column: Status, Filter: `iteration:@current`, Slice by: Component |
| 2 | Issues | Table | Group by: Milestone, Sort: Priority desc |
| 3 | Roadmap | Roadmap | Date: Start → Target, Group by: Milestone |
| 4 | Sprint Roadmap | Roadmap | Date: Start → Target, Group by: Iteration |
| 5 | Sprint Planning | Table | Group by: Iteration |
| 6 | Tasks | Table | Filter: `assignee:@me`, Sort: Priority desc |
| 7 | AI Queue | Table | Filter: `label:ai:ready OR label:ai:in-progress` |
| 8 | Review | Board | Filter: `status:"In Review"` |
| 9 | Blocked | Table | Filter: `label:status:blocked`, Group by: Component |
| 10 | Components | Table | Group by: Component |
| 11 | Tech Debt | Table | Filter: `label:type:tech-debt` |

### 2.5 Enable Built-in Workflows

**Project → Settings → Workflows**

| Workflow | Enable | Action |
|:---------|:------:|:-------|
| Item added to project | [PASS] | Set Status → **Todo** (default for all new issues) |
| Item reopened | [PASS] | Set Status → Todo |
| Pull request merged | [PASS] | Set Status → Done |
| Item closed | [PASS] | Set Status → Done |
| Auto-add to project | [PASS] | Filter: `is:issue repo:ORG/REPO` |

> **Status Assignment Rules**:
> - **Todo** (default): All new issues added to the board receive Status=Todo automatically via the built-in workflow.
> - **Backlog**: Sub-tasks of the **nearest planning phase only** are manually set to Backlog. This signals they are ready for sprint pull.
> - When a phase enters execution, its epic moves to In Progress; sub-tasks move from Backlog → In Progress as work begins.
> - Future phase epics and sub-tasks remain at Todo until their phase becomes the nearest planning phase.

### 2.6 Link Repository to Project

```bash
gh api graphql -f query='
mutation($projectId: ID!, $repoId: ID!) {
  linkProjectV2ToRepository(input: {projectId: $projectId, repositoryId: $repoId}) {
    repository { id }
  }
}' -f projectId="$PROJECT_ID" -f repoId="REPO_NODE_ID"
```

---

## Phase 3: Automation Setup [PASS] COMPLETED

### 3.0 Current Workflows (18 total)

**Core CI/CD (2)**
| Workflow | File | Purpose |
|:---------|:-----|:--------|
| CI | `ci.yml` | Continuous integration tests |
| Release | `release.yml` | Release automation |

**Project Automation (4)**
| Workflow | File | Purpose |
|:---------|:-----|:--------|
| Auto-add to Project | `auto-add-to-project.yml` | Add issues to Project #{PROJECT_BOARD_NUMBER} |
| Issue Label Sync | `issue-label-sync.yml` | Label-to-status sync |
| Phase Transition | `phase-transition.yml` | Phase gate workflow |
| PR Merge Cleanup | `pr-merge-cleanup.yml` | Branch cleanup on merge |

**AI PR Review (2)**
| Workflow | File | Purpose |
|:---------|:-----|:--------|
| AI Review | `ai-review.yml` | Reusable AI PR review (Gemini) |
| Agent Dispatch | `agent-dispatch.yml` | AI agent dispatch for issue work |

**Phase-Gated Deployment (7)**
| Workflow | File | Purpose |
|:---------|:-----|:--------|
| Deploy Dev | `deploy-dev.yml` | Phase-gated dev deployment |
| Check All Phases | `check-all-phases-dev.yml` | Staging gate when all phases dev_deployed |
| Deploy Staging | `deploy-staging.yml` | Staging deployment (all phases complete) |
| Deploy Prod | `deploy-prod.yml` | Production deployment (manual approval) |
| Rollback Prod | `rollback-prod.yml` | Production rollback |
| Create Deployment Issue | `create-deployment-issue.yml` | Auto-create deployment issues |
| Check Phase Completion | `check-phase-completion.yml` | Phase completion checker |

**Deprecated**
| Workflow | File | Status |
|:---------|:-----|:-------|
| ~~Deploy PR~~ | `deploy-dev-pr.yml.disabled` | Deprecated — per-PR deploys removed |
| ~~Cleanup PR Env~~ | `cleanup-pr-env.yml.disabled` | Deprecated — no longer needed |

**QA Loop (3)**
| Workflow | File | Purpose |
|:---------|:-----|:--------|
| Create QA Testing Issue | `create-qa-testing-issue.yml` | Auto-create QA testing issues |
| Execute QA Testing | `execute-qa-testing.yml` | Execute QA tests in staging |
| Create Bug Issue | `create-bug-issue.yml` | Auto-create bug issues on QA failure |

### 3.1 Create PROJECT_TOKEN Secret

1. Generate Personal Access Token:
   - Go to: `https://{GITHUB_HOST}/settings/tokens`
   - Click **Generate new token**
   - Select scopes: `project`, `repo`
   - Copy the token

2. Add to repository:
   ```bash
   gh secret set PROJECT_TOKEN --body "ghp_xxxxxxxxxxxx"
   ```

### 3.2 Create ELEVATED_PAT Secret

The `ELEVATED_PAT` allows workflows to push commits to protected branches (e.g., updating `governance/cicd/phase-deployments.json`).

1. Generate Personal Access Token:
   - Go to: `https://{GITHUB_HOST}/settings/tokens`
   - Click **Generate new token (classic)**
   - Note: `AIOCTO Elevated PAT for CI`
   - Expiration: 90 days
   - Select scopes: `repo` (full), `workflow`
   - Copy the token

2. Add to repository:
   ```bash
   GH_HOST={GITHUB_HOST} gh secret set ELEVATED_PAT \
     --repo {GITHUB_ORG}/{REPO_NAME} \
     --body "ghp_xxxxxxxxxxxx"
   ```

**Used by**: `deploy-staging.yml`, `deploy-prod.yml`, `check-phase-completion.yml`, `rollback-prod.yml`

**Security**: Use a service account (not personal), set expiration, rotate regularly.

### 3.3 Create GitHub Actions Directory

```bash
mkdir -p .github/workflows
mkdir -p .github/scripts
mkdir -p .github/ai-context
```

### 3.3 Create AI-Ready Validation Workflow

Create `.github/workflows/ai-ready-validation.yml`:

```yaml
name: AI-Ready Validation

on:
  issues:
    types: [labeled]

env:
  GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

jobs:
  validate-ai-ready:
    if: github.event.label.name == 'ai:ready'
    runs-on: ubuntu-latest
    steps:
      - name: Get Issue Body
        id: issue
        run: |
          BODY=$(gh issue view ${{ github.event.issue.number }} --json body -q '.body')
          echo "body<<EOF" >> $GITHUB_OUTPUT
          echo "$BODY" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT

      - name: Validate AI-Ready Criteria
        id: validate
        run: |
          BODY="${{ steps.issue.outputs.body }}"
          ERRORS=""

          if ! echo "$BODY" | grep -qi "acceptance criteria"; then
            ERRORS="$ERRORS\n- Missing 'Acceptance Criteria' section"
          fi

          if ! echo "$BODY" | grep -qi "related files"; then
            ERRORS="$ERRORS\n- Missing 'Related Files' section"
          fi

          if ! echo "$BODY" | grep -qiE "size:\s*(xs|s|m|l|xl)"; then
            ERRORS="$ERRORS\n- Missing 'Size' estimate"
          fi

          if echo "$BODY" | grep -qiE "size:\s*(l|xl)"; then
            ERRORS="$ERRORS\n- Size L/XL requires human lead"
          fi

          if [ -n "$ERRORS" ]; then
            echo "valid=false" >> $GITHUB_OUTPUT
            echo "errors=$ERRORS" >> $GITHUB_OUTPUT
          else
            echo "valid=true" >> $GITHUB_OUTPUT
          fi

      - name: Handle Validation Result
        run: |
          if [ "${{ steps.validate.outputs.valid }}" == "false" ]; then
            gh issue comment ${{ github.event.issue.number }} \
              --body "## [WARN] AI-Ready Validation Failed

              Missing required sections:
              ${{ steps.validate.outputs.errors }}

              Please update and re-apply the label."
            gh issue edit ${{ github.event.issue.number }} --remove-label "ai:ready"
          else
            gh issue comment ${{ github.event.issue.number }} \
              --body "## [PASS] AI-Ready Validated

              This issue is now in the AI queue."
          fi
```

### 3.4 Create Label-to-Status Sync Workflow

Create `.github/workflows/ai-label-status-sync.yml`:

```yaml
name: AI Label to Status Sync

on:
  issues:
    types: [labeled]

env:
  GH_TOKEN: ${{ secrets.PROJECT_TOKEN }}
  PROJECT_ID: "YOUR_PROJECT_ID"
  STATUS_FIELD_ID: "YOUR_STATUS_FIELD_ID"
  STATUS_TODO: "YOUR_TODO_OPTION_ID"
  STATUS_IN_PROGRESS: "YOUR_IN_PROGRESS_OPTION_ID"
  STATUS_IN_REVIEW: "YOUR_IN_REVIEW_OPTION_ID"
  STATUS_DONE: "YOUR_DONE_OPTION_ID"

jobs:
  sync-status:
    runs-on: ubuntu-latest
    steps:
      - name: Get Project Item ID
        id: get-item
        run: |
          ITEM_ID=$(gh api graphql -f query='
            query($org: String!, $number: Int!) {
              organization(login: $org) {
                projectV2(number: $number) {
                  items(first: 100) {
                    nodes {
                      id
                      content { ... on Issue { number } }
                    }
                  }
                }
              }
            }' -f org="${{ github.repository_owner }}" -F number=31 \
            --jq ".data.organization.projectV2.items.nodes[] | select(.content.number == ${{ github.event.issue.number }}) | .id")
          echo "item_id=$ITEM_ID" >> $GITHUB_OUTPUT

      - name: Sync Label to Status
        run: |
          LABEL="${{ github.event.label.name }}"
          OPTION_ID=""

          case $LABEL in
            "ai:ready") OPTION_ID="$STATUS_TODO" ;;
            "ai:in-progress") OPTION_ID="$STATUS_IN_PROGRESS" ;;
            "ai:review-requested") OPTION_ID="$STATUS_IN_REVIEW" ;;
          esac

          if [ -n "$OPTION_ID" ]; then
            gh api graphql -f query='
              mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
                updateProjectV2ItemFieldValue(input: {
                  projectId: $projectId, itemId: $itemId, fieldId: $fieldId
                  value: { singleSelectOptionId: $optionId }
                }) { projectV2Item { id } }
              }' \
              -f projectId="$PROJECT_ID" \
              -f itemId="${{ steps.get-item.outputs.item_id }}" \
              -f fieldId="$STATUS_FIELD_ID" \
              -f optionId="$OPTION_ID"
          fi
```

### 3.5 Create PR Review Workflow

Create `.github/workflows/ai-pr-review.yml`:

```yaml
name: AI PR Review

on:
  pull_request:
    types: [opened, synchronize]
    branches: [main]

env:
  GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Security Scan
        id: security
        run: |
          FINDINGS=""

          # Check for hardcoded secrets
          if grep -rE "(api_key|password|secret)\s*=\s*['\"][^'\"]+['\"]" --include="*.py" .; then
            FINDINGS="$FINDINGS\n- Potential hardcoded secret detected"
          fi

          # Check for SQL injection
          if grep -rE "f['\"].*SELECT.*\{" --include="*.py" .; then
            FINDINGS="$FINDINGS\n- Potential SQL injection"
          fi

          echo "findings=$FINDINGS" >> $GITHUB_OUTPUT

      - name: Post Results
        run: |
          if [ -n "${{ steps.security.outputs.findings }}" ]; then
            gh pr comment ${{ github.event.pull_request.number }} \
              --body "##  Security Findings
              ${{ steps.security.outputs.findings }}"
            gh pr edit ${{ github.event.pull_request.number }} \
              --add-label "quality:security-review"
          fi
```

### 3.6 Create Branch Cleanup Workflow

Create `.github/workflows/ai-branch-cleanup.yml`:

```yaml
name: AI Branch Cleanup

on:
  pull_request:
    types: [closed]
  schedule:
    - cron: '0 0 * * 0'

env:
  GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

jobs:
  cleanup-merged:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - name: Delete AI Branch
        if: startsWith(github.event.pull_request.head.ref, 'ai/')
        run: |
          gh api repos/${{ github.repository }}/git/refs/heads/${{ github.event.pull_request.head.ref }} -X DELETE || true
```

### 3.7 Commit Automation Files

```bash
git add .github/
git commit -m "feat: add AI-first project automation

- AI-ready validation workflow
- Label-to-status sync workflow
- PR security review workflow
- Branch cleanup workflow
- Issue templates"
git push
```

---

## Phase 4: AI Tool Configuration [PASS] COMPLETED

### 4.1 MCP Server Configuration

The project has 6 MCP servers configured in `.mcp.json` using the `-tt-{PROJECT_PREFIX}` naming convention:

| Server | Package | Purpose | Status |
|:-------|:--------|:--------|:------:|
| `github-{PROJECT_PREFIX}-{PROJECT_PREFIX}` | `ghcr.io/github/github-mcp-server` | GitHub Enterprise operations | [PASS] |
| `filesystem-tt-{PROJECT_PREFIX}` | `@modelcontextprotocol/server-filesystem` | File operations | [PASS] |
| `memory-tt-{PROJECT_PREFIX}` | `@modelcontextprotocol/server-memory` | Knowledge graph | [PASS] |
| `sequential-thinking-tt-{PROJECT_PREFIX}` | `@modelcontextprotocol/server-sequential-thinking` | Problem decomposition | [PASS] |
| `context7-tt-{PROJECT_PREFIX}` | `@upstash/context7-mcp` | Library documentation | [PASS] |
| `playwright-tt-{PROJECT_PREFIX}` | `@playwright/mcp` | Browser automation | [PASS] |

**Naming Convention**: `{function}-tt-{PROJECT_PREFIX}`
- `tt` = TechTrend (GitHub Enterprise instance)
- `{PROJECT_PREFIX}` = AI Cost Monitoring project prefix

Example configuration (`.mcp.json`):

```json
{
  "mcpServers": {
    "github-{PROJECT_PREFIX}-{PROJECT_PREFIX}": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx...",
        "ghcr.io/github/github-mcp-server",
        "--gh-host", "https://{GITHUB_HOST}",
        "stdio"
      ]
    },
    "filesystem-tt-{PROJECT_PREFIX}": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "{LOCAL_PROJECT_PATH}/{REPO_NAME}"]
    },
    "memory-tt-{PROJECT_PREFIX}": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "sequential-thinking-tt-{PROJECT_PREFIX}": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "context7-tt-{PROJECT_PREFIX}": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "playwright-tt-{PROJECT_PREFIX}": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp"]
    }
  }
}
```

> **Full Documentation**: See [GITHUB_TOOLS_SETUP.md](./GITHUB_TOOLS_SETUP.md) for tool usage patterns and troubleshooting.

### 4.2 {AI_TOOL_NAME} Code Hooks

Create `.claude/settings.json`:

```json
{
  "hooks": {
    "pre-commit": "npm run lint && npm run test:unit"
  }
}
```

### 4.3 AI Context Directory

Create `.github/ai-context/README.md`:

```markdown
# AI Context Directory

This directory contains context files for AI assistants.

## Files

- `working-state.md` - Current task state (auto-maintained by AI)
- `architecture.md` - System architecture overview
- `patterns.md` - Code patterns and conventions
```

### 4.4 VS Code Settings

Create `.vscode/settings.json`:

```json
{
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true
}
```

---

## Phase 5: Issue Population & Kickoff [PASS] COMPLETED (Phase 1)

### 5.1 Create Phase Sub-Task Issues

For each phase, create sub-task issues from [PROJECT_PLAN.md](./PROJECT_PLAN.md) task specifications.

```bash
# Example: Create Phase 1 sub-task issue
GH_HOST={GITHUB_HOST} gh issue create \
  --repo $GH_ORG/$GH_REPO \
  --title "[P1-1.0] Create {PROJECT_PREFIX}-{SERVICE_NAME} repository" \
  --label "type:infra,P0-critical,phase:1,ai:ready,scope:mandatory,status:planning" \
  --milestone "AIOCTO - Phase 1: GCP Cost Guard" \
  --body "$(cat <<'EOF'
## Summary
Create the component repository for GCP Cost Guard module.

## Acceptance Criteria
- [ ] Repository created in {GITHUB_ORG} org
- [ ] Standard Python project structure
...

## Dependencies
- None

## Blocks
- #20 (Terraform), #21 (CI/CD)

**Parent Epic**: #11
EOF
)"
```

**Naming Convention**: `[P{phase}-{task_id}] {title}`
- Example: `[P1-1.3] Implement CostGuardedLLM wrapper class`

### 5.2 Add Issues to Project Board

```bash
# Get Project V2 ID
PROJECT_ID=$(GH_HOST={GITHUB_HOST} gh api graphql -f query='
  { organization(login: "{GITHUB_ORG}") {
      projectV2(number: 31) { id }
  }}' --jq '.data.organization.projectV2.id')

# Get issue node ID
ISSUE_ID=$(GH_HOST={GITHUB_HOST} gh api graphql -f query='
  { repository(owner: "{GITHUB_ORG}", name: "{REPO_NAME}") {
      issue(number: 19) { id }
  }}' --jq '.data.repository.issue.id')

# Add issue to project board
GH_HOST={GITHUB_HOST} gh api graphql -f query="
  mutation {
    addProjectV2ItemById(input: {projectId: \"$PROJECT_ID\", contentId: \"$ISSUE_ID\"}) {
      item { id }
    }
  }"
```

### 5.3 Verify Phase Compliance

Before starting a phase, verify all issues match local documents:

```bash
# List phase issues
GH_HOST={GITHUB_HOST} gh issue list \
  --repo $GH_ORG/$GH_REPO \
  --label "phase:1" --state open

# Verify issue count matches PROJECT_PLAN.md
# Phase 1: 14 sub-tasks (#19-#32) + Epic #11
```

**Compliance Checks**:
- Title matches PROJECT_PLAN.md task name
- Priority label matches plan priority (P0→P0-critical, P1→P1-high)
- AI label matches plan (Y→ai:ready, N→ai:human-required)
- Milestone assigned with correct due date
- Issue body has: Summary, Acceptance Criteria, Dependencies, Blocks, Parent Epic
- All issues added to Project Board #{PROJECT_BOARD_NUMBER}

### 5.4 Status Lifecycle

Issues follow this status progression on the board (varies by issue type):

```
Development issues (ai:development):
  Todo → Backlog → In Progress → In Review → Done

Deployment issues (ai:deployment):
  Todo → Deploying → Done

QA issues (ai:qa-testing):
  Todo → Testing → Done
```

**Status Options**:
| Status | Color | Used For |
|:-------|:------|:---------|
| Backlog | Gray | Unprioritized items |
| Todo | Blue | Ready to start |
| In Progress | Yellow | Development work active |
| In Review | Purple | PR awaiting review |
| Deploying | Orange | Staging/prod deployment in progress |
| Testing | Pink | QA tests running |
| Done | Green | Completed |

**Rules**:
1. **New issues** get Status=**Todo** and Environment=**Development** automatically (via `issue-auto-add.yml`)
2. **Nearest planning phase sub-tasks** are set to Status=**Backlog** (manual, one phase at a time)
3. When a sprint starts, pull tasks from Backlog → **In Progress**
4. Phase epic moves to **In Progress** when execution begins
5. **Deployment issues** move to **Deploying** when `deploy-staging.yml` starts
6. **QA issues** move to **Testing** when `execute-qa-testing.yml` starts
7. Future phase sub-tasks stay at **Todo** until their phase becomes the nearest planning phase

```bash
# When a phase enters planning: move its sub-tasks from Todo → Backlog
# Example for Phase 2 (when Phase 1 completes):
for ITEM_ID in $(gh api graphql ... --jq '...phase 2 items...'); do
  GH_HOST={GITHUB_HOST} gh api graphql -f query="
    mutation {
      updateProjectV2ItemFieldValue(input: {
        projectId: \"$PROJECT_ID\", itemId: \"$ITEM_ID\",
        fieldId: \"$STATUS_FIELD_ID\",
        value: { singleSelectOptionId: \"$STATUS_BACKLOG\" }
      }) { projectV2Item { id } }
    }"
done

# When a sprint starts: update issue labels
for i in 19 20 21 22 23 24 25 26 27 28 29 30 31 32; do
  GH_HOST={GITHUB_HOST} gh issue edit $i \
    --repo $GH_ORG/$GH_REPO \
    --remove-label "status:planning" \
    --add-label "status:implementing"
done
```

### Current Status

| Phase | Issues Created | On Board #{PROJECT_BOARD_NUMBER} | Board Status |
|:------|:--------------:|:------------:|:-------------|
| Sprint 0 | 5 (#6-#10) | Yes | Done (closed) |
| Phase 1 Epic | #11 | Yes | In Progress |
| Phase 1 Sub-tasks | 14 (#19-#32) | Yes | **Backlog** (nearest phase) |
| Phase 2-8 Epics | #12-#18 | Yes | Todo |
| Phase 2-8 Sub-tasks | — | — | Create just-in-time (default: Todo) |

---

## Verification Checklist

Run these commands to verify setup:

```bash
# Check labels
gh label list --limit 50

# Check milestones
gh api repos/$GH_ORG/$GH_REPO/milestones --jq '.[].title'

# Check project exists
gh projects list --org $GH_ORG

# Check workflows
ls -la .github/workflows/

# Check issue templates
ls -la .github/ISSUE_TEMPLATE/
```

---

## Field IDs Reference

Retrieve field IDs for workflow configuration:

```bash
gh projects field-list 31 --org {GITHUB_ORG}
```

**Current Field IDs (Project #{PROJECT_BOARD_NUMBER})**:

| Field | Type | ID |
|:------|:-----|:---|
| Project | — | `MDk6UHJvamVjdFYyOTg=` |
| Status | SingleSelect | `MDI2OlByb2plY3RWMlNpbmdsZVNlbGVjdEZpZWxkMTIyMA==` |
| Priority | SingleSelect | `MDI2OlByb2plY3RWMlNpbmdsZVNlbGVjdEZpZWxkMTIzMg==` |
| Size | SingleSelect | `MDI2OlByb2plY3RWMlNpbmdsZVNlbGVjdEZpZWxkMTIzMw==` |
| Component | SingleSelect | `MDI2OlByb2plY3RWMlNpbmdsZVNlbGVjdEZpZWxkMTI1NA==` |
| Sprints | Iteration | `MDIzOlByb2plY3RWMkl0ZXJhdGlvbkZpZWxkMTIzMA==` |
| Start Date | Date | `MDE0OlByb2plY3RWMkZpZWxkMTIyOA==` |
| Target Date | Date | `MDE0OlByb2plY3RWMkZpZWxkMTIyOQ==` |
| Cloud Provider | SingleSelect | `MDI2OlByb2plY3RWMlNpbmdsZVNlbGVjdEZpZWxkMTIzNw==` |
| Cost Impact | SingleSelect | `MDI2OlByb2plY3RWMlNpbmdsZVNlbGVjdEZpZWxkMTIzOA==` |
| Phase | SingleSelect | `MDI2OlByb2plY3RWMlNpbmdsZVNlbGVjdEZpZWxkMTI1Mw==` |
| Risk Level | SingleSelect | `MDI2OlByb2plY3RWMlNpbmdsZVNlbGVjdEZpZWxkMTI0MA==` |
| Roadmap Phase | SingleSelect | `MDI2OlByb2plY3RWMlNpbmdsZVNlbGVjdEZpZWxkMTI1NQ==` |
| Environment | SingleSelect | `MDI2OlByb2plY3RWMlNpbmdsZVNlbGVjdEZpZWxkMTI3OQ==` |

**Environment Options** (Deployment Pipeline view):

| Environment | Option ID | Description |
|:------------|:----------|:------------|
| Planning | `d1fd5954` | Pre-development planning |
| Development | `37fcaf5f` | In development/PR phase (default) |
| Staging | `ab95acae` | Deployed to staging environment |
| Production | `d4abfe48` | Deployed to production |

**Environment Field is Mandatory** for all issues and PRs.

**Environment Rules**:
1. **New issues** get Environment=**Development** by default (set by `auto-add-to-project.yml`)
2. **New PRs** inherit Environment from linked issue (parsed from `Closes #X`, `Fixes #Y`, `Resolves #Z` in PR body)
3. **PRs without linked issue** default to Environment=**Development**
4. **Deployment issues** move to **Staging** when `deploy-staging.yml` completes successfully
5. **Production deployment** moves items to **Production** when `deploy-prod.yml` completes
6. The **Deployment Pipeline** view groups items by Environment field

---

## AI Workflow Labels Reference (Minimal Practical Set)

| Label | Description | Who Sets → Who Acts |
|:------|:------------|:--------------------|
| `ai:ready` | Task well-specified, ready for AI | Human → AI |
| `ai:in-progress` | AI actively working | AI → (tracking) |
| `ai:blocked` | AI stuck, needs human input | AI → Human |
| `ai:review-requested` | AI work complete, PR ready | AI → Human |
| `ai:human-required` | Requires human implementation | Human → Human |

**Development Workflow:**
```
ai:ready → ai:in-progress → ai:review-requested → (PR merge)
               ↓
          ai:blocked (if stuck)
```

**4-Stage Iterative QA Loop:**
```
Development (ai:development) → PR merge
     → Deployment (ai:deployment)     → staging deploy
     → QA Testing (ai:qa-testing)     → execute tests
                                              
                                         
                                        Pass     Fail
                                                  
                                    ai:qa-passed   Create Bug Issue
                                                  (ai:development + bug)
                                                  iteration:1-3
                                                       
                                                  Loop back (max 3x)
                                                       
                                    PRODUCTION 
```

**Additional Labels for QA Loop:**
| Label | Description |
|:------|:------------|
| `ai:deployment` | Deployment issue (auto-created on PR merge) |
| `ai:qa-testing` | QA testing issue (auto-created for functional changes) |
| `ai:qa-passed` | QA tests passed |
| `ai:qa-failed` | QA tests failed |
| `bug` | Bug fix (used with `ai:development`) |
| `iteration:1-3` | Bug fix iteration count |
| `needs-human` | Max iterations exceeded |

See [AI_ISSUE_LIFECYCLE.md](./AI_ISSUE_LIFECYCLE.md) for full details.

**Note:** `ai:approved`/`ai:rejected` labels are intentionally not used - PR state already indicates approval status.

---

## Complexity Guidelines

| Level | Characteristics | Assignment |
|:------|:----------------|:-----------|
| Trivial | Config, typo fix | AI autonomous |
| Low | Single function | AI autonomous |
| Medium | Multiple files | AI with checkpoints |
| High | Architectural | Human-led, AI-assisted |
| Critical | Breaking changes | Human only |

---

## Quick Commands Reference

```bash
# List AI-ready issues
gh issue list --label "ai:ready"

# Claim issue for AI work
gh issue edit 123 --remove-label "ai:ready" --add-label "ai:in-progress"

# Mark work complete
gh issue edit 123 --remove-label "ai:in-progress" --add-label "ai:review-requested"

# Check AI queue stats
echo "Ready: $(gh issue list --label 'ai:ready' --json number | jq length)"
echo "In Progress: $(gh issue list --label 'ai:in-progress' --json number | jq length)"
echo "Blocked: $(gh issue list --label 'ai:blocked' --json number | jq length)"
```

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 1.0 | {DATE} | Initial setup |
| 2.0 | {DATE} | AI-first development edition |
| 3.0 | {DATE} | Complete setup guide with step-by-step instructions |
| 3.1 | {DATE} | Updated Phase 4 with actual 6 MCP servers using `-tt-{PROJECT_PREFIX}` naming |
| 3.2 | {DATE} | Verified against live GitHub project; updated all phases with actual counts (48 labels, 19 fields, 6 workflows, 8 templates) |
| 3.3 | {DATE} | Added status and scope labels: `status:planning`, `status:implementing`, `scope:mandatory`, `scope:optional` |
| 3.4 | {DATE} | Added `status:suspended` and phase labels 4-8 |
| 4.0 | {DATE} | Added Phase 5: Issue Population & Kickoff; fixed Phase 2 milestone date (Mar 28→Mar 21); updated phase label descriptions with dates; updated Component field for v2.0 architecture (removed Cloud Agents); updated issue counts |
| 4.2 | {DATE} | Added Board Status Rules: Todo (default for new issues), Backlog (nearest planning phase only); documented status lifecycle; updated §2.5, §5.4, Current Status table |
| 4.1 | {DATE} | Board #{PROJECT_BOARD_NUMBER} overhaul: updated README to v2.0 architecture; fixed epic dates (20-week timeline); recreated Phase field (8 options), Component field (8 options), Roadmap Phase field (9 options); set Phase/Component/Roadmap/Sprint values for all items; updated field IDs |
| 3.5 | {DATE} | Implemented minimal practical AI workflow labels (5 labels); removed unused `ai:approved`/`ai:rejected` (63 labels total) |
| 4.3 | {DATE} | Updated §3.0 workflow list from 6 to actual 18 workflows (removed non-existent pr-labeler.yml, stale.yml, codeql.yml; added all deployment and AI review workflows) |
| 4.4 | {DATE} | Updated §1.2 labels to match actual repo (76 labels): added deployment labels, AI PR review labels, cloud/cost labels, fixed status:wip→status:in-progress, removed non-existent quality:* labels |
| 4.5 | {DATE} | Added Development Issue template to §1.4 (8→9 templates); template supports 4-stage QA workflow with Test Plan section |
| 4.6 | {DATE} | Added §1.4.1 PR Template documentation; streamlined PR template with `Closes #` for workflow integration |
| 4.9 | {DATE} | Environment field now mandatory: PRs inherit from linked issues; updated Environment Rules with inheritance logic (6 rules) |
| 4.8 | {DATE} | Added Environment field for Deployment Pipeline view (Planning/Development/Staging/Production); Environment=Development set as default for new issues; added Field IDs and Environment Options tables |
| 4.7 | {DATE} | Added Deploying and Testing board statuses for CI/CD pipeline visibility; updated status progression to show different flows for development, deployment, and QA issues; added Status Options table |
