# Governance Documentation

Governance rules, templates, and workflows for the **Docs Flow Framework**.

This repository uses **Specification-Driven Development (SDD)** with scalable depth based on project complexity.

---

## SDD Depth Selection

> **Detailed guide**: See [SDD_DEPTH_GUIDE.md](./SDD_DEPTH_GUIDE.md) for complete layer mappings and decision criteria.

| Depth | Layers | Best For | Timeline |
|:------|:-------|:---------|:---------|
| **SDD-Lite** | REF → BRD-MVP → PRD-MVP → TASKS-MVP | MVPs, prototypes, solo + AI | 1-3 months |
| **SDD-Standard** | REF → BRD → PRD → EARS → ADR → SYS → REQ → TASKS | Production apps, small teams | 3-6 months |
| **SDD-Full** | All 15 layers with 4-Gate CHG | Enterprise, regulated, multi-team | 6+ months |

### Quick Selection

- **Start with SDD-Lite** for new projects, MVPs, or when speed matters
- **Use SDD-Standard** for production applications with moderate traceability needs
- **Use SDD-Full** for enterprise projects with regulatory/audit requirements
- **Scale up** by adding layers as project complexity grows

---

## Directory Structure

```
governance/
├── SDD_DEPTH_GUIDE.md   # Lite vs Standard vs Full comparison
├── shared/              # Applies to all SDD depths
│   ├── AI_PR_Review/
│   ├── BRANCHING_STRATEGY.md
│   ├── DEFINITION_OF_DONE.md
│   ├── RELEASE_PROCESS.md
│   ├── github/
│   └── (repository patterns)
└── sdd/                 # SDD governance (all depths)
    ├── GOVERNANCE_RULES.md
    ├── AI_ISSUE_LIFECYCLE.md
    ├── templates/
    ├── scripts/
    ├── plans/
    └── (setup guides)

ai_dev_ssd_flow/         # Layer documentation and templates
├── BRD/                 # Layer 1 templates
├── PRD/                 # Layer 2 templates
├── EARS/                # Layer 3 templates
├── ...                  # Layers 4-14
└── README.md            # Full SDD methodology
```

---

## Shared Governance (All SDD Depths)

Documents that apply to **all** SDD depths (Lite, Standard, Full).

| Document | Description |
|:---------|:------------|
| [shared/AI_PR_Review/](./shared/AI_PR_Review/) | Automated PR review workflows (Claude Code CLI) |
| [shared/BRANCHING_STRATEGY.md](./shared/BRANCHING_STRATEGY.md) | Git workflow and branch conventions |
| [shared/DEFINITION_OF_DONE.md](./shared/DEFINITION_OF_DONE.md) | Completion criteria at task/sprint/phase levels |
| [shared/RELEASE_PROCESS.md](./shared/RELEASE_PROCESS.md) | SemVer versioning and deployment |
| [shared/github/GITHUB_WORKFLOWS.md](./shared/github/GITHUB_WORKFLOWS.md) | GitHub Actions workflow documentation |
| [shared/github/GITHUB_TOOLS_SETUP.md](./shared/github/GITHUB_TOOLS_SETUP.md) | gh CLI and MCP server configuration |
| [shared/github/ghes_runner/](./shared/github/ghes_runner/) | Self-hosted GHES runner setup |
| [shared/HOME_REPO.md](./shared/HOME_REPO.md) | Home repository structure |
| [shared/REPOSITORY_STRATEGY.md](./shared/REPOSITORY_STRATEGY.md) | Mono-repo architecture patterns |
| [shared/ROLES_AND_TOOLS.md](./shared/ROLES_AND_TOOLS.md) | Human vs AI task split |

---

## SDD Governance

Core governance documents for all SDD depths.

### Core Workflow

| Document | Description |
|:---------|:------------|
| [sdd/GOVERNANCE_RULES.md](./sdd/GOVERNANCE_RULES.md) | Operational policies and mandatory rules |
| [sdd/AI_ISSUE_LIFECYCLE.md](./sdd/AI_ISSUE_LIFECYCLE.md) | 4-stage iterative loop (Dev → Deploy → QA → Bug Fix) |
| [sdd/AI_TIME_ESTIMATION.md](./sdd/AI_TIME_ESTIMATION.md) | AI-assisted time estimation methodology |

### Framework Setup

| Document | Description |
|:---------|:------------|
| [sdd/SETUP_GUIDE.md](./sdd/SETUP_GUIDE.md) | Step-by-step framework customization |
| [sdd/CONFIG.md](./sdd/CONFIG.md) | All 50 placeholder variables reference |
| [sdd/CLOUD_GUIDE.md](./sdd/CLOUD_GUIDE.md) | Multi-cloud setup (GCP, AWS, Azure) |

### Project Planning

| Document | Description |
|:---------|:------------|
| [sdd/PROJECT_KICKOFF_PLAN-TEMPLATE.md](./sdd/PROJECT_KICKOFF_PLAN-TEMPLATE.md) | Project kickoff template |
| [sdd/PROJECT_PLAN-TEMPLATE.md](./sdd/PROJECT_PLAN-TEMPLATE.md) | Full project plan with phases/sprints |
| [sdd/ROADMAP-TEMPLATE.md](./sdd/ROADMAP-TEMPLATE.md) | Phase timeline with dependency graphs |

### Implementation Plans

| Document | Description |
|:---------|:------------|
| [sdd/plans/README.md](./sdd/plans/README.md) | Plan management guide |
| [sdd/plans/IPLAN-TEMPLATE.md](./sdd/plans/IPLAN-TEMPLATE.md) | Blank IPLAN template |

### Project Templates

| Template | Description |
|:---------|:------------|
| [sdd/templates/README.md](./sdd/templates/README.md) | Project README template |
| [sdd/templates/CONTRIBUTING.md](./sdd/templates/CONTRIBUTING.md) | Contributing guidelines |
| [sdd/templates/CLAUDE.md](./sdd/templates/CLAUDE.md) | Claude Code settings template |
| [sdd/templates/DEVELOPER_GUIDE.md](./sdd/templates/DEVELOPER_GUIDE.md) | Developer setup guide |

### Setup Scripts

| Directory | Description |
|:----------|:------------|
| [sdd/scripts/project_setup/](./sdd/scripts/project_setup/) | Cloud setup (GCP, AWS, Azure) |
| [sdd/scripts/workflows/](./sdd/scripts/workflows/) | GitHub Actions helper scripts |
| [sdd/scripts/ghes-runner/](./sdd/scripts/ghes-runner/) | GHES runner setup |

---

## Layer Documentation

Full SDD layer documentation and templates are in [`ai_dev_ssd_flow/`](../ai_dev_ssd_flow/).

| Layer | Artifact | Description |
|:------|:---------|:------------|
| 0 | REF | Strategy and reference documents |
| 1 | BRD | Business requirements |
| 2 | PRD | Product requirements |
| 3 | EARS | Formal WHEN-THE-SHALL requirements |
| 4 | BDD | Gherkin behavior tests |
| 5 | ADR | Architecture Decision Records |
| 6 | SYS | System requirements |
| 7 | REQ | Atomic requirements |
| 8 | CTR | API contracts (optional) |
| 9 | SPEC | Technical specifications (YAML) |
| 10 | TSPEC | Test specifications |
| 11 | TASKS | Implementation task breakdown |
| 12-14 | IMPL | Code, tests, validation |

---

## Issue Creation (All Depths)

All SDD depths follow the same issue creation pattern:

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

**More specification layers = more precise issues with better traceability.**

---

## Related Root Files

| File | Description |
|:-----|:------------|
| [/CONTRIBUTING.md](/CONTRIBUTING.md) | Contributing guidelines (symlink) |
| [/README_AIAGENT.md](/README_AIAGENT.md) | AI agent rules (symlink) |
| [/.github/CODEOWNERS](/.github/CODEOWNERS) | PR reviewer auto-assignment |
