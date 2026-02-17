# Governance Documentation

Governance rules, templates, and workflows for the **Docs Flow Framework**.

This repository contains **two complementary frameworks**:

| Framework | Directory | Best For |
|:----------|:----------|:---------|
| **AI Project Issues Flow** | [`issues_flow/`](./issues_flow/) | Small-medium AI-first projects (1-6 months) |
| **AI Dev SDD Flow** | [`sdd_flow/`](./sdd_flow/) → [`ai_dev_ssd_flow/`](../ai_dev_ssd_flow/) | Large/enterprise/regulated projects |

---

## Framework Selection

### Use Issues Flow when:
- Building MVPs or small-to-medium projects
- Creating issues directly from project description
- Working solo or with small team + AI
- Need rapid iteration with phase-gated deployment

### Use SDD Flow when:
- Building enterprise software with regulatory requirements
- Need complete audit trails and bidirectional traceability
- Multiple teams working on complex systems
- Formal 15-layer documentation required

---

## Directory Structure

```
governance/
├── shared/           # Both frameworks
│   ├── AI_PR_Review/
│   ├── BRANCHING_STRATEGY.md
│   ├── DEFINITION_OF_DONE.md
│   ├── RELEASE_PROCESS.md
│   ├── github/
│   └── (repository patterns)
├── issues_flow/      # AI Project Issues Flow
│   ├── GOVERNANCE_RULES.md
│   ├── AI_ISSUE_LIFECYCLE.md
│   ├── templates/
│   ├── scripts/
│   ├── plans/
│   └── (setup guides)
└── sdd_flow/         # AI Dev SDD Flow (references)
    └── README.md     # Links to ai_dev_ssd_flow/
```

---

## Shared Governance (Both Frameworks)

Documents that apply to **both** Issues Flow and SDD Flow.

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

## Issues Flow Governance

Documents specific to **AI Project Issues Flow** (issue-based, phase-gated development).

### Core Workflow

| Document | Description |
|:---------|:------------|
| [issues_flow/GOVERNANCE_RULES.md](./issues_flow/GOVERNANCE_RULES.md) | Operational policies and mandatory rules |
| [issues_flow/AI_ISSUE_LIFECYCLE.md](./issues_flow/AI_ISSUE_LIFECYCLE.md) | 4-stage iterative loop (Dev → Deploy → QA → Bug Fix) |
| [issues_flow/AI_TIME_ESTIMATION.md](./issues_flow/AI_TIME_ESTIMATION.md) | AI-assisted time estimation methodology |

### Framework Setup

| Document | Description |
|:---------|:------------|
| [issues_flow/SETUP_GUIDE.md](./issues_flow/SETUP_GUIDE.md) | Step-by-step framework customization |
| [issues_flow/CONFIG.md](./issues_flow/CONFIG.md) | All 50 placeholder variables reference |
| [issues_flow/CLOUD_GUIDE.md](./issues_flow/CLOUD_GUIDE.md) | Multi-cloud setup (GCP, AWS, Azure) |

### Project Planning

| Document | Description |
|:---------|:------------|
| [issues_flow/PROJECT_KICKOFF_PLAN-TEMPLATE.md](./issues_flow/PROJECT_KICKOFF_PLAN-TEMPLATE.md) | Project kickoff template |
| [issues_flow/PROJECT_PLAN-TEMPLATE.md](./issues_flow/PROJECT_PLAN-TEMPLATE.md) | Full project plan with phases/sprints |
| [issues_flow/ROADMAP-TEMPLATE.md](./issues_flow/ROADMAP-TEMPLATE.md) | Phase timeline with dependency graphs |

### Implementation Plans

| Document | Description |
|:---------|:------------|
| [issues_flow/plans/README.md](./issues_flow/plans/README.md) | Plan management guide |
| [issues_flow/plans/IPLAN-TEMPLATE.md](./issues_flow/plans/IPLAN-TEMPLATE.md) | Blank IPLAN template |

### Project Templates

| Template | Description |
|:---------|:------------|
| [issues_flow/templates/README.md](./issues_flow/templates/README.md) | Project README template |
| [issues_flow/templates/CONTRIBUTING.md](./issues_flow/templates/CONTRIBUTING.md) | Contributing guidelines |
| [issues_flow/templates/CLAUDE.md](./issues_flow/templates/CLAUDE.md) | Claude Code settings template |
| [issues_flow/templates/DEVELOPER_GUIDE.md](./issues_flow/templates/DEVELOPER_GUIDE.md) | Developer setup guide |

### Setup Scripts

| Directory | Description |
|:----------|:------------|
| [issues_flow/scripts/project_setup/](./issues_flow/scripts/project_setup/) | Cloud setup (GCP, AWS, Azure) |
| [issues_flow/scripts/workflows/](./issues_flow/scripts/workflows/) | GitHub Actions helper scripts |
| [issues_flow/scripts/ghes-runner/](./issues_flow/scripts/ghes-runner/) | GHES runner setup |

---

## SDD Flow Governance

Documents specific to **AI Dev SDD Flow** (15-layer formal specification).

See [sdd_flow/README.md](./sdd_flow/README.md) for links to:

- 15-layer architecture documentation
- ID naming standards
- Cumulative traceability tagging
- Change management (4-Gate CHG system)
- Domain adaptation guides
- Validation scripts

Full SDD documentation: [`ai_dev_ssd_flow/`](../ai_dev_ssd_flow/)

---

## Issue Creation Comparison

| Framework | How Issues Are Created |
|:----------|:-----------------------|
| **Issues Flow** | Human creates issue directly from `00_REF/` (project description) → AI executes |
| **SDD Flow** | Create BRD→PRD→...→TASKS documents first → Issues derived from TASKS layer |

---

## Related Root Files

| File | Description |
|:-----|:------------|
| [/CONTRIBUTING.md](/CONTRIBUTING.md) | Contributing guidelines (symlink) |
| [/README_AIAGENT.md](/README_AIAGENT.md) | AI agent rules (symlink) |
| [/.github/CODEOWNERS](/.github/CODEOWNERS) | PR reviewer auto-assignment |
