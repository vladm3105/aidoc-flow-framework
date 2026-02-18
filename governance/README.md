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
│   ├── IMPLEMENT_INSTRUCTIONS.md  # AI agent implementation guide
│   ├── LOCAL_SETUP.md
│   ├── MANUAL_REVIEW_GUIDE.md
│   └── ONBOARDING.md
│
├── AI_AGENT_MEMORY.md             # AI Agent Memory System docs
├── memory/                        # AI agent memory storage
│   ├── GLOBAL_LEARNINGS.md        # Project-wide learnings
│   ├── active/                    # Active issue memory files
│   └── archive/                   # Completed issue memory files
│
├── setup/                         # Setup guides
│   ├── SETUP_GUIDE.md             # Step-by-step customization
│   ├── CONFIG.md                  # 50+ placeholder variables
│   └── CLOUD_GUIDE.md             # GCP/AWS/Azure setup
│
├── plans/                         # Implementation plans
│   ├── README.md                  # IPLAN guide and index
│   └── IPLAN-TEMPLATE.md          # Implementation plan template
│
├── templates/                     # Project templates
│   ├── CLAUDE.md                  # AI agent config
│   ├── CONTRIBUTING.md            # Contributing guide
│   ├── README.md                  # Project README
│   ├── README_AIAGENT.md          # Universal AI agent rules
│   ├── PROJECT_PLAN-TEMPLATE.md   # Project plan template
│   ├── PROJECT_KICKOFF_PLAN-TEMPLATE.md  # Kickoff plan template
│   ├── ROADMAP-TEMPLATE.md        # Roadmap template
│   ├── DEVELOPER_GUIDE.md         # Developer onboarding guide
│   ├── HANDOFF.md                 # Project handoff template
│   ├── PROJECT_DEFINITION.md      # Project definition template
│   ├── GCP-DEPLOYMENT.md          # GCP deployment guide
│   ├── AWS-DEPLOYMENT.md          # AWS deployment guide
│   ├── AZURE-DEPLOYMENT.md        # Azure deployment guide
│   └── qa/                        # QA documentation templates
│
└── scripts/                       # Automation scripts
    ├── project_setup/             # Project setup scripts
    │   └── cloud/                 # GCP/AWS/Azure scripts
    ├── ghes-runner/               # GHES runner setup + docs
    ├── workflows/                 # Governance automation scripts
    │   ├── verify_acceptance_criteria.py
    │   ├── generate_iplan_from_issue.py
    │   ├── generate_deployment_plan.py
    │   ├── check_staging_ready.py
    │   ├── generate_phase_summary.py
    │   ├── sync_tasks_from_issues.py
    │   ├── validate_governance.py
    │   └── validate_project_setup.py
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
| [AI_AGENT_MEMORY.md](./AI_AGENT_MEMORY.md) | AI Agent Memory System for session persistence |

---

## Governance Automation

| Script | Purpose |
|:-------|:--------|
| `scripts/workflows/verify_acceptance_criteria.py` | Verify PR against issue acceptance criteria |
| `scripts/workflows/generate_iplan_from_issue.py` | Auto-generate IPLAN from GitHub issue |
| `scripts/workflows/generate_deployment_plan.py` | Generate deployment plan from phase issues |
| `scripts/workflows/check_staging_ready.py` | Evaluate staging readiness for production |
| `scripts/workflows/generate_phase_summary.py` | Generate phase completion summary |
| `scripts/workflows/sync_tasks_from_issues.py` | Bidirectional sync TASKS ↔ GitHub issues |
| `scripts/workflows/validate_governance.py` | Detect governance documentation drift |
| `scripts/workflows/validate_project_setup.py` | Validate project configuration and secrets |

---

## SDD Integration

| Document | Description |
|:---------|:------------|
| [TASKS_IPLAN_BRIDGE.md](./TASKS_IPLAN_BRIDGE.md) | How TASKS (Layer 11) connects to IPLAN |
| [CHG_GOVERNANCE_BRIDGE.md](./CHG_GOVERNANCE_BRIDGE.md) | 4-Gate CHG to governance phases |
| [TSPEC_BDD_QA_BRIDGE.md](./TSPEC_BDD_QA_BRIDGE.md) | Test execution (TSPEC/BDD) to QA workflow |

> **Full SDD Documentation**: See [`../ai_dev_ssd_flow/`](../ai_dev_ssd_flow/) for layer templates and specifications.

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

## Implementation Plans

| Document | Description |
|:---------|:------------|
| [plans/README.md](./plans/README.md) | IPLAN guide, lifecycle, and index |
| [plans/IPLAN-TEMPLATE.md](./plans/IPLAN-TEMPLATE.md) | Implementation plan template |

---

## Templates

### Core Templates

| Template | Description |
|:---------|:------------|
| [templates/CLAUDE.md](./templates/CLAUDE.md) | Claude Code project instructions |
| [templates/README_AIAGENT.md](./templates/README_AIAGENT.md) | Universal AI agent rules |
| [templates/MEMORY.md](./templates/MEMORY.md) | AI Agent memory file template |
| [templates/CONTRIBUTING.md](./templates/CONTRIBUTING.md) | Contributing guidelines |
| [templates/README.md](./templates/README.md) | Project README template |

### Planning Templates

| Template | Description |
|:---------|:------------|
| [templates/PROJECT_PLAN-TEMPLATE.md](./templates/PROJECT_PLAN-TEMPLATE.md) | Full project plan with phases |
| [templates/PROJECT_KICKOFF_PLAN-TEMPLATE.md](./templates/PROJECT_KICKOFF_PLAN-TEMPLATE.md) | Sprint kickoff planning |
| [templates/ROADMAP-TEMPLATE.md](./templates/ROADMAP-TEMPLATE.md) | Project roadmap template |
| [templates/PROJECT_DEFINITION.md](./templates/PROJECT_DEFINITION.md) | Project definition template |

### Development Templates

| Template | Description |
|:---------|:------------|
| [templates/DEVELOPER_GUIDE.md](./templates/DEVELOPER_GUIDE.md) | Developer onboarding guide |
| [templates/HANDOFF.md](./templates/HANDOFF.md) | Project handoff documentation |

### Deployment Templates

| Template | Description |
|:---------|:------------|
| [templates/GCP-DEPLOYMENT.md](./templates/GCP-DEPLOYMENT.md) | GCP Cloud Run deployment guide |
| [templates/AWS-DEPLOYMENT.md](./templates/AWS-DEPLOYMENT.md) | AWS ECS/Fargate deployment guide |
| [templates/AZURE-DEPLOYMENT.md](./templates/AZURE-DEPLOYMENT.md) | Azure Container Apps deployment guide |

### QA Templates

| Template | Description |
|:---------|:------------|
| [templates/qa/](./templates/qa/) | Testing strategy, standards, CI/CD specs |

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
