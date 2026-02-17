# Home Repository Guide

**Project**: {PROJECT_NAME} | **Prefix**: `{PROJECT_PREFIX}`

This document explains the role, structure, and usage of the project's **home repository**.

---

## What is the Home Repo?

The **home repo** is [`{REPO_NAME}`](https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME}) — the central hub and single source of truth for the entire AI Cost Monitoring project.

| Attribute | Value |
|:----------|:------|
| **URL** | `https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME}` |
| **Local Path** | `{LOCAL_PROJECT_PATH}/{REPO_NAME}` |
| **Project Board** | [V2 #{PROJECT_BOARD_NUMBER}](https://{GITHUB_HOST}/orgs/{GITHUB_ORG}/projects/{PROJECT_BOARD_NUMBER}) |
| **Organization** | {GITHUB_ORG} |

---

## Purpose

The home repo serves as:

1. **Documentation Hub** — All architecture docs, ADRs, specs, and guides live here
2. **Governance Center** — Project processes, workflows, and standards are defined here
3. **Issue Tracker** — All issues, milestones, and project planning happen here
4. **Component Host** — All component source code lives under `components/`
5. **CI/CD Orchestrator** — Project-level workflows and automation

> [!IMPORTANT]
> This is a **monorepo**. All documentation, governance, and component source code live in this single repository.

---

## Directory Structure

```
{REPO_NAME}/
 .github/
    ISSUE_TEMPLATE/          # Issue templates (bug, feature, etc.)
       bug_report.md
       feature_request.md
       architecture_proposal.md
       research_task.md
       infra_task.md
       security_report.md
       cost_analysis.md
       mcp_server.md
       config.yml
    workflows/               # GitHub Actions (18 workflows)
       ci.yml               # Lint, test, security scan
       release.yml          # Release automation
       auto-add-to-project.yml  # Add new issues/PRs to board
       issue-label-sync.yml # Sync labels → board status, cleanup on close
       pr-merge-cleanup.yml # Set merged PR board status to Done
       phase-transition.yml # Bulk phase status transitions
       ai-review.yml        # Unified AI PR review
       agent-dispatch.yml           # Dispatch issues to AI agents
       deploy-dev.yml               # Phase-gated dev deployment
       check-all-phases-dev.yml     # Staging gate (all phases dev_deployed)
       deploy-dev-pr.yml.disabled   # DEPRECATED: Per-PR dev environments
       cleanup-pr-env.yml.disabled  # DEPRECATED: Cleanup PR environments
       create-deployment-issue.yml  # Auto-create deployment issues
       create-qa-testing-issue.yml  # Auto-create QA issues
       check-phase-completion.yml   # Detect phase completion
       deploy-staging.yml           # Unified staging deploy (all phases)
       execute-qa-testing.yml       # Run QA test suite
       create-bug-issue.yml         # Auto-create bug issues
       deploy-prod.yml              # Production deployment
       rollback-prod.yml            # Production rollback
    labeler.yml              # PR labeling rules
    CODEOWNERS               # Auto-assign PR reviewers by file path
    dependabot.yml           # Dependency updates
    PULL_REQUEST_TEMPLATE.md

 governance/                  # Project governance (this directory)
    HOME_REPO.md             # This document
    PROJECT_PLAN.md          # Full project plan (all phases, ~75 tasks)
    ROADMAP.md               # Phase timeline and dependencies
    REPOSITORY_STRATEGY.md   # Monorepo architecture
    PROJECT_KICKOFF_PLAN.md  # Executive summary
    BRANCHING_STRATEGY.md    # Git branching model
    GOVERNANCE_RULES.md      # Operational policies and conventions
    DEFINITION_OF_DONE.md    # Completion criteria (references rules)
    RELEASE_PROCESS.md       # Versioning and releases
    GITHUB_WORKFLOWS.md      # All GitHub Actions documentation
    GITHUB_PROJECT_SETUP_AI_FIRST.md  # AI workflow setup
    GITHUB_TOOLS_SETUP.md    # CLI and MCP configuration
    AI_PR_Review/            # AI PR review operational docs
       README.md            # Overview, architecture, review policy
       LOCAL_SETUP.md       # Local developer setup ({AI_TOOL_NAME} Code CLI, gh auth)
       GCP_SETUP.md         # Deprecated — GCP prerequisites (Vertex AI, WIF, IAM)
       ONBOARDING.md        # Add AI review to new component repos
       AI_AGENT_REVIEW_WORKFLOW.md  # On-demand AI agent review + fix-verify loop
       MANUAL_REVIEW_GUIDE.md  # Human guide: use {AI_TOOL_NAME} Code CLI to review PRs
    plans/                   # Implementation plans (execution adjustments)
        README.md            # Plan management guide and index
        IPLAN-NNN_slug.md    # Individual plans (IPLAN-001, etc.)

 docs/                        # Technical documentation
    adr/                     # 9 Architecture Decision Records
       001-use-mcp-servers.md
       002-gcp-only-first.md
       003-use-bigquery-not-timescaledb.md
       004-cloud-run-not-kubernetes.md
       005-use-litellm-for-llms.md
       006-cloud-native-task-queues-not-celery.md
       007-grafana-plus-agui-hybrid.md
       008-otel-gen-ai-conventions.md
       009-ai-pr-review-custom-workflow.md
    core/                    # 8 Technical specifications
       01-database-schema.md
       02-mcp-tool-contracts.md
       03-agent-routing-spec.md
       04-tenant-onboarding.md
       05-api-endpoint-spec.md
       07-deployment-infrastructure.md
       08-cost-model.md
       09-observability-spec.md
    architecture/            # System diagrams
    UX/                      # Implementation guides
    qa/                      # 7 QA and deployment docs

 components/                  # Component source code
    {SERVICE_NAME}/          # Phase 1: GCP budget protection
    mcp-servers/             # Phase 3: 4 MCP servers (data access)
    agents/                  # Phase 4: 5 AI agents
    frontend/                # Phase 5: Next.js + CopilotKit
    infrastructure/          # Phase 2: Terraform modules

 scripts/                     # Shared scripts
    workflows/               # GitHub workflow helper scripts (14 Python)
       check_*.py           # Validation scripts (conflicts, errors, limits)
       create_*.py          # Issue creation scripts (bugs, test failures)
       execute_qa_tests.py  # QA test execution
       extract_test_plan.py # Test plan extraction from issues
       handle_issue_reopen.py  # Issue reopen handler
       update_*.py          # Tracking file update scripts
       verify_*.py          # Prerequisite verification scripts
    project_setup/           # One-time project setup scripts
       gcp/                 # GCP setup scripts
          setup-wif.sh             # Workload Identity Federation
          setup-projects.sh        # GCP project creation
          setup-environments.sh    # GCP environment config
          setup-ai-review-gcp.sh   # AI review prerequisites
          setup_artifact_registry.sh   # Artifact Registry
          configure_revision_retention.sh  # Revision cleanup
       setup_github_environments.sh # GitHub environment setup
    ghes-runner/             # Self-hosted runner setup

 .mcp.json                    # MCP server configuration for development
 CLAUDE.md                    # {AI_TOOL_NAME} Code-specific instructions
 README_AIAGENT.md            # Universal AI agent rules (all AI tools)
 README.md                    # Project overview
 CONTRIBUTING.md              # Contribution guidelines + reviewer roster
 DEVELOPER_GUIDE.md           # Local setup guide
 HANDOFF.md                   # Developer handoff notes
```

---

## What Lives Where

| Content | Location | Notes |
|:--------|:---------|:------|
| **All issues** | Home repo | Single issue tracker for entire project |
| **All milestones** | Home repo | Phase-aligned milestones |
| **All labels** | Home repo | 63 labels for categorization |
| **Project board** | Home repo | V2 Project #{PROJECT_BOARD_NUMBER} |
| **ADRs** | `docs/adr/` | Architecture decisions |
| **Technical specs** | `docs/core/` | 8 specifications |
| **QA & Deployment** | `docs/qa/` | 7 QA and deployment docs |
| **Governance** | `governance/` | Processes and standards |
| **CI/CD (project)** | `.github/workflows/` | Repo-level automation |
| **Source code** | `components/*/` | Component directories |
| **Component tests** | `components/*/tests/` | Per-component test suites |

---

## Directory Organization

| Directory | Purpose |
|:----------|:--------|
| `governance/` | Project governance, processes, standards |
| `docs/` | ADRs, technical specifications, architecture |
| `components/` | All component source code |
| `.github/` | Issue templates, workflows, CI/CD |
| `scripts/` | Shared utility scripts |

---

## Working with the Repo

### Cloning

```bash
# Standard clone — all components included
git clone https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME}.git
cd {REPO_NAME}
```

### Working with Components

All components are directories under `components/`. No submodule commands needed.

```bash
# Navigate to a component
cd components/{SERVICE_NAME}

# Install component dependencies
pip install -e ".[dev]"

# Run component tests
pytest
```

### Creating Issues

All issues should be created in the **home repo**, regardless of which component they affect:

```bash
# Create issue in home repo
GH_HOST={GITHUB_HOST} gh issue create \
  --repo {GITHUB_ORG}/{REPO_NAME} \
  --title "[MCP] Add health endpoint to GCP MCP server" \
  --label "component:mcp,P2-medium"
```

---

## GitHub Project Integration

The home repo is linked to **Project Board #{PROJECT_BOARD_NUMBER}**:

- **URL**: `https://{GITHUB_HOST}/orgs/{GITHUB_ORG}/projects/{PROJECT_BOARD_NUMBER}`
- **Auto-add**: New issues are automatically added to the project
- **Views**: Sprint Board, Roadmap, AI Queue, Components, etc.

### Custom Fields

| Field | Purpose |
|:------|:--------|
| Status | Backlog → Todo → In Progress → In Review → Done |
| Priority | P0-Critical to P3-Low |
| Size | XS, S, M, L, XL |
| Component | GCP Cost Guard, MCP Servers, Agents, etc. |
| Cloud Provider | GCP, AWS, Azure, Multi-cloud |
| Cost Impact | High, Medium, Low, Savings |
| Phase | Phase 1, 2, 3 |
| Risk Level | Critical, High, Medium, Low |

---

## Labels

The home repo has **63 labels** organized by category:

| Category | Examples |
|:---------|:---------|
| **Type** | `type:feature`, `type:bug`, `type:infra`, `type:research` |
| **Priority** | `P0-critical`, `P1-high`, `P2-medium`, `P3-low` |
| **Component** | `component:mcp`, `component:agents`, `component:ui` |
| **Status** | `status:in-progress`, `status:blocked`, `status:review` |
| **Cloud** | `cloud:gcp`, `cloud:aws`, `cloud:azure` |
| **Cost** | `cost:high-impact`, `cost:optimization` |
| **Phase** | `phase:1`, `phase:2`, `phase:3` |
| **AI Workflow (Issues)** | `ai:ready`, `ai:in-progress`, `ai:review-requested` |
| **AI Review (PRs)** | `ai:review-passed`, `ai:review-failed` |

---

## Milestones

| Milestone | Target Date | Notes |
|:----------|:------------|:------|
| Sprint 0: Research & Decisions | Feb 21, 2026 | |
| Phase 1: GCP Cost Guard | Feb 28, 2026 | AI-optimized (1 week) |
| Phase 2: Foundation Infrastructure | Mar 21, 2026 | 3 weeks |
| Phase 3: MCP Servers | Apr 4, 2026 | 4 servers (3 native + OpenCost) |
| Phase 4: AI Agents | Apr 25, 2026 | 5 agents |
| Phase 5: CopilotKit Chat | May 9, 2026 | Grafana deferred |
| Phase 6: Event Processing | May 23, 2026 | ETL deferred |
| Phase 7: Multi-Tenant & A2A | Jun 20, 2026 | Conditional |
| Phase 8: Security & Testing | Jul 18, 2026 | Conditional |

---

## Related Documents

### Planning & Execution
- [PROJECT_PLAN.md](./PROJECT_PLAN.md) — Full project plan with all phases, tasks, and sprint planning
- [ROADMAP.md](./ROADMAP.md) — Phase timeline and dependencies

### Repository & Architecture
- [REPOSITORY_STRATEGY.md](./REPOSITORY_STRATEGY.md) — Monorepo architecture details
- [BRANCHING_STRATEGY.md](./BRANCHING_STRATEGY.md) — Git workflow

### Governance
- [PROJECT_KICKOFF_PLAN.md](./PROJECT_KICKOFF_PLAN.md) — Executive summary
- [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md) — Completion criteria
- [RELEASE_PROCESS.md](./RELEASE_PROCESS.md) — Versioning and releases

### GitHub Integration
- [GITHUB_WORKFLOWS.md](./github/GITHUB_WORKFLOWS.md) — All GitHub Actions workflow documentation
- [GITHUB_PROJECT_SETUP_AI_FIRST.md](./github/GITHUB_PROJECT_SETUP.md) — Project board setup
- [GITHUB_TOOLS_SETUP.md](./github/GITHUB_TOOLS_SETUP.md) — CLI and MCP configuration

---

## Quick Reference

```bash
# Set environment
export GH_HOST={GITHUB_HOST}
export GH_ORG="{GITHUB_ORG}"
export GH_REPO="{REPO_NAME}"

# List all issues
gh issue list --repo $GH_ORG/$GH_REPO

# List labels
gh label list --repo $GH_ORG/$GH_REPO

# View project board
gh project view 31 --org $GH_ORG

# List components
ls components/
```
