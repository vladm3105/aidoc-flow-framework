# Governance Documentation

Governance rules and templates for the **AI Project Flow** framework (issue-based, phase-gated development for small-medium AI-first projects).

> **Note**: For **AI Dev Flow (SDD)** documentation (15-layer formal specification), see [`ai_dev_ssd_flow/`](../ai_dev_ssd_flow/).

---

## Project Templates

Templates for initializing new AI Project Flow projects.

| Template | Description |
|:---------|:------------|
| [templates/README.md](./templates/README.md) | Project README template |
| [templates/CONTRIBUTING.md](./templates/CONTRIBUTING.md) | Contributing guidelines template |
| [templates/README_AIAGENT.md](./templates/README_AIAGENT.md) | AI agent rules template |
| [templates/CLAUDE.md](./templates/CLAUDE.md) | Claude Code settings template |
| [templates/DEVELOPER_GUIDE.md](./templates/DEVELOPER_GUIDE.md) | Developer setup guide template |
| [templates/HANDOFF.md](./templates/HANDOFF.md) | AI session handoff template |
| [templates/GCP-DEPLOYMENT.md](./templates/GCP-DEPLOYMENT.md) | GCP deployment guide |
| [templates/AWS-DEPLOYMENT.md](./templates/AWS-DEPLOYMENT.md) | AWS deployment guide |
| [templates/AZURE-DEPLOYMENT.md](./templates/AZURE-DEPLOYMENT.md) | Azure deployment guide |
| [templates/.env.example](./templates/.env.example) | Environment variables template |
| [templates/.mcp.json](./templates/.mcp.json) | MCP server configuration template |

---

## Framework Setup

Getting started guides for configuring and customizing the framework.

| Document | Description |
|:---------|:------------|
| [SETUP_GUIDE.md](./SETUP_GUIDE.md) | Step-by-step framework customization guide |
| [CONFIG.md](./CONFIG.md) | All 50 placeholder variables reference |
| [CLOUD_GUIDE.md](./CLOUD_GUIDE.md) | Multi-cloud setup (GCP, AWS, Azure) with OIDC/WIF |

---

## Core Governance

| Document | Description |
|:---------|:------------|
| [GOVERNANCE_RULES.md](./GOVERNANCE_RULES.md) | Operational policies and mandatory rules |
| [BRANCHING_STRATEGY.md](./BRANCHING_STRATEGY.md) | Git workflow and branch conventions |
| [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md) | Completion criteria at task/sprint/phase levels |
| [RELEASE_PROCESS.md](./RELEASE_PROCESS.md) | SemVer versioning and phase-gated deployment |
| [REPOSITORY_STRATEGY.md](./REPOSITORY_STRATEGY.md) | Mono-repo architecture patterns |
| [REPO_STRUCTURE_DECISION_MATRIX.md](./REPO_STRUCTURE_DECISION_MATRIX.md) | Repository structure decision guide |
| [ROLES_AND_TOOLS.md](./ROLES_AND_TOOLS.md) | Human vs AI task split and tool requirements |
| [HOME_REPO.md](./HOME_REPO.md) | Home repository structure and purpose |

---

## AI Development Workflow

| Document | Description |
|:---------|:------------|
| [AI_ISSUE_LIFECYCLE.md](./AI_ISSUE_LIFECYCLE.md) | 4-stage iterative quality loop (Development → Deployment → QA → Bug Fix) |
| [AI_TIME_ESTIMATION.md](./AI_TIME_ESTIMATION.md) | AI-assisted time estimation methodology with speedup factors |

---

## AI PR Review

Automated and on-demand AI-powered pull request review workflows.

| Document | Description |
|:---------|:------------|
| [AI_PR_Review/README.md](./AI_PR_Review/README.md) | System overview and architecture |
| [AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md](./AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md) | On-demand agent review with fix-and-verify loop |
| [AI_PR_Review/LOCAL_SETUP.md](./AI_PR_Review/LOCAL_SETUP.md) | Developer environment configuration |
| [AI_PR_Review/MANUAL_REVIEW_GUIDE.md](./AI_PR_Review/MANUAL_REVIEW_GUIDE.md) | Human-facing guide for local AI assistants |
| [AI_PR_Review/ONBOARDING.md](./AI_PR_Review/ONBOARDING.md) | Adding AI review to new repositories |

---

## GitHub Setup

GitHub tools, workflows, and project configuration guides.

| Document | Description |
|:---------|:------------|
| [github/GITHUB_TOOLS_SETUP.md](./github/GITHUB_TOOLS_SETUP.md) | gh CLI and MCP server configuration |
| [github/GITHUB_WORKFLOWS.md](./github/GITHUB_WORKFLOWS.md) | GitHub Actions workflow documentation |
| [github/GITHUB_PROJECT_SETUP.md](./github/GITHUB_PROJECT_SETUP.md) | GitHub Project board setup for AI workflow |
| [github/ghes_runner/GHES_RUNNER_GUIDE.md](./github/ghes_runner/GHES_RUNNER_GUIDE.md) | Self-hosted GHES runner setup |

---

## CI/CD

Phase-gated deployment tracking and configuration.

| File | Description |
|:-----|:------------|
| [cicd/phase-deployments.json](./cicd/phase-deployments.json) | Phase tracking file for deployment workflows |

---

## Project Planning Templates

Templates for project kickoff, planning, and roadmap documentation.

| Document | Description |
|:---------|:------------|
| [PROJECT_KICKOFF_PLAN-TEMPLATE.md](./PROJECT_KICKOFF_PLAN-TEMPLATE.md) | Project kickoff template with executive summary, architecture, and risks |
| [PROJECT_PLAN-TEMPLATE.md](./PROJECT_PLAN-TEMPLATE.md) | Full project plan template with phases, sprints, and task specifications |
| [ROADMAP-TEMPLATE.md](./ROADMAP-TEMPLATE.md) | Phase timeline template with dependency graphs and deployment strategy |

---

## Implementation Plan Templates

Implementation plan (IPLAN) templates and guidance.

| Document | Description |
|:---------|:------------|
| [plans/README.md](./plans/README.md) | Plan management guide and conventions |
| [plans/IPLAN-TEMPLATE.md](./plans/IPLAN-TEMPLATE.md) | Blank IPLAN template |
| [plans/IPLAN-001_phase-issue-review.md](./plans/IPLAN-001_phase-issue-review.md) | Pre-sprint phase issue audit template |
| [plans/IPLAN-002_ai-pr-review-workflow.md](./plans/IPLAN-002_ai-pr-review-workflow.md) | AI PR review setup template |
| [plans/IPLAN-003_phase-gated-deployment.md](./plans/IPLAN-003_phase-gated-deployment.md) | Phase-gated deployment configuration template |

---

## Setup Scripts

Automation scripts for project setup and GitHub Actions workflows.

| Directory | Description |
|:----------|:------------|
| [scripts/project_setup/](./scripts/project_setup/) | Cloud setup scripts (GCP, AWS, Azure) and validation |
| [scripts/workflows/](./scripts/workflows/) | GitHub Actions helper scripts (phase checks, QA, deployment) |
| [scripts/ghes-runner/](./scripts/ghes-runner/) | GitHub Enterprise Server self-hosted runner setup |

---

## Related Root Files

| File | Description |
|:-----|:------------|
| [/CONTRIBUTING.md](/CONTRIBUTING.md) | Contributing guidelines (symlink to templates/) |
| [/README_AIAGENT.md](/README_AIAGENT.md) | AI agent rules (symlink to templates/) |
| [/.github/CODEOWNERS](/.github/CODEOWNERS) | PR reviewer auto-assignment |
