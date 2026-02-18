# Governance Documentation

Governance rules, templates, and workflows for the **Docs Flow Framework**.

This repository uses **Specification-Driven Development (SDD)** with scalable depth based on project complexity.

---

## SDD Depth Selection

> **Detailed guide**: See [SDD_DEPTH_GUIDE.md](./SDD_DEPTH_GUIDE.md) for complete layer mappings and decision criteria.

| Depth | Layers | Best For | Timeline |
|:------|:-------|:---------|:---------|
| **SDD-Lite** | REF → BRD-MVP → PRD-MVP → TASKS-MVP | MVPs, prototypes, solo + AI | 1-3 months |
| **SDD-Standard** | + EARS, ADR, SYS, REQ | Production apps, small teams | 3-6 months |
| **SDD-Full** | All 15 layers + 4-Gate CHG | Enterprise, regulated, multi-team | 6+ months |

---

## Directory Structure

```
governance/
├── README.md                      # This index
├── SDD_DEPTH_GUIDE.md             # Lite vs Standard vs Full
│
├── # === CORE DOCUMENTATION ===
├── GOVERNANCE_RULES.md            # Operational policies
├── AI_ISSUE_LIFECYCLE.md          # Issue workflow (4-stage loop)
├── BRANCHING_STRATEGY.md          # Git workflow
├── DEFINITION_OF_DONE.md          # Completion criteria
├── RELEASE_PROCESS.md             # Versioning and releases
├── REPOSITORY_STRATEGY.md         # Monorepo architecture
├── ROLES_AND_TOOLS.md             # Human vs AI responsibilities
├── HOME_REPO.md                   # Home repository structure
│
├── github/                        # GitHub documentation
│   ├── GITHUB_PROJECT_SETUP.md    # Project board setup
│   ├── GITHUB_TOOLS_SETUP.md      # gh CLI and MCP config
│   └── GITHUB_WORKFLOWS.md        # GitHub Actions docs
│
├── AI_PR_Review/                  # AI PR review
│   ├── README.md                  # Overview
│   ├── AI_AGENT_REVIEW_WORKFLOW.md
│   ├── LOCAL_SETUP.md
│   ├── MANUAL_REVIEW_GUIDE.md
│   └── ONBOARDING.md
│
├── setup/                         # Setup guides
│   ├── SETUP_GUIDE.md             # Step-by-step customization
│   ├── CONFIG.md                  # 50+ placeholder variables
│   └── CLOUD_GUIDE.md             # GCP/AWS/Azure setup
│
├── templates/                     # Project templates
│   ├── CLAUDE.md                  # AI agent config
│   ├── CONTRIBUTING.md            # Contributing guide
│   ├── README.md                  # Project README
│   ├── PROJECT_PLAN-TEMPLATE.md   # Project plan
│   ├── IPLAN-TEMPLATE.md          # Implementation plan
│   ├── deployment/                # Cloud deployment guides
│   └── qa/                        # QA documentation templates
│
└── scripts/                       # Automation scripts
    ├── project_setup/             # Project setup scripts
    │   └── cloud/                 # GCP/AWS/Azure scripts
    ├── ghes-runner/               # GHES runner setup + docs
    ├── workflows/                 # CI/CD helper scripts
    └── cicd/                      # CI/CD configuration
```

---

## Core Documentation

| Document | Description |
|:---------|:------------|
| [GOVERNANCE_RULES.md](./GOVERNANCE_RULES.md) | Operational policies and mandatory rules |
| [AI_ISSUE_LIFECYCLE.md](./AI_ISSUE_LIFECYCLE.md) | 4-stage iterative loop (Dev → Deploy → QA → Bug Fix) |
| [BRANCHING_STRATEGY.md](./BRANCHING_STRATEGY.md) | Git workflow and branch conventions |
| [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md) | Completion criteria at task/sprint/phase levels |
| [RELEASE_PROCESS.md](./RELEASE_PROCESS.md) | SemVer versioning and deployment |
| [REPOSITORY_STRATEGY.md](./REPOSITORY_STRATEGY.md) | Monorepo architecture patterns |
| [ROLES_AND_TOOLS.md](./ROLES_AND_TOOLS.md) | Human vs AI task split |
| [HOME_REPO.md](./HOME_REPO.md) | Home repository structure |

---

## GitHub Documentation

| Document | Description |
|:---------|:------------|
| [github/GITHUB_PROJECT_SETUP.md](./github/GITHUB_PROJECT_SETUP.md) | Project board, labels, fields setup |
| [github/GITHUB_TOOLS_SETUP.md](./github/GITHUB_TOOLS_SETUP.md) | gh CLI and MCP server configuration |
| [github/GITHUB_WORKFLOWS.md](./github/GITHUB_WORKFLOWS.md) | GitHub Actions workflow documentation |

---

## AI PR Review

| Document | Description |
|:---------|:------------|
| [AI_PR_Review/README.md](./AI_PR_Review/README.md) | Overview and architecture |
| [AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md](./AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md) | On-demand AI review workflow |
| [AI_PR_Review/LOCAL_SETUP.md](./AI_PR_Review/LOCAL_SETUP.md) | Local developer setup |
| [AI_PR_Review/MANUAL_REVIEW_GUIDE.md](./AI_PR_Review/MANUAL_REVIEW_GUIDE.md) | Manual AI PR review guide |
| [AI_PR_Review/ONBOARDING.md](./AI_PR_Review/ONBOARDING.md) | Add AI review to new repos |

---

## Setup Guides

| Document | Description |
|:---------|:------------|
| [setup/SETUP_GUIDE.md](./setup/SETUP_GUIDE.md) | Step-by-step framework customization |
| [setup/CONFIG.md](./setup/CONFIG.md) | All 50+ placeholder variables reference |
| [setup/CLOUD_GUIDE.md](./setup/CLOUD_GUIDE.md) | Multi-cloud setup (GCP, AWS, Azure) |

---

## Templates

| Template | Description |
|:---------|:------------|
| [templates/CLAUDE.md](./templates/CLAUDE.md) | Claude Code project instructions |
| [templates/CONTRIBUTING.md](./templates/CONTRIBUTING.md) | Contributing guidelines |
| [templates/README.md](./templates/README.md) | Project README template |
| [templates/PROJECT_PLAN-TEMPLATE.md](./templates/PROJECT_PLAN-TEMPLATE.md) | Full project plan with phases |
| [templates/IPLAN-TEMPLATE.md](./templates/IPLAN-TEMPLATE.md) | Implementation plan template |
| [templates/qa/](./templates/qa/) | QA documentation templates |

---

## Scripts

| Directory | Description |
|:----------|:------------|
| [scripts/project_setup/](./scripts/project_setup/) | Cloud setup (GCP, AWS, Azure) |
| [scripts/ghes-runner/](./scripts/ghes-runner/) | GHES runner setup and documentation |
| [scripts/workflows/](./scripts/workflows/) | GitHub Actions helper scripts |
| [scripts/cicd/](./scripts/cicd/) | CI/CD configuration files |

---

## Layer Documentation

Full SDD layer documentation and templates are in [`../ai_dev_ssd_flow/`](../ai_dev_ssd_flow/).

---

## Issue Creation (All Depths)

```
Human creates REF/ (Project Description)
    ↓
AI Agent generates specification layers (depth varies)
    ↓
AI Agent generates TASKS from specifications
    ↓
AI Agent creates GitHub Issues from TASKS
    ↓
AI Agent executes issues (ai:ready → ai:in-progress → PR)
```

---

## Related Root Files

| File | Description |
|:-----|:------------|
| [/CONTRIBUTING.md](/CONTRIBUTING.md) | Contributing guidelines (symlink) |
| [/README_AIAGENT.md](/README_AIAGENT.md) | AI agent rules (symlink) |
| [/.github/CODEOWNERS](/.github/CODEOWNERS) | PR reviewer auto-assignment |
