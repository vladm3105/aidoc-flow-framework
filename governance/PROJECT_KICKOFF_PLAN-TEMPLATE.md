# Project Kickoff Plan: {PROJECT_NAME}

**Project Prefix**: `{PROJECT_PREFIX}`
**Date**: {DATE}
**Status**: {STATUS}
**Version**: 1.0

> **Template Usage**: Replace all `{PLACEHOLDER}` values with project-specific content. Remove this note when complete.

## 1. Executive Summary

**{PROJECT_NAME}** is {PROJECT_DESCRIPTION}.

**Core Differentiator**: {CORE_DIFFERENTIATOR}

> [!NOTE]
> This is the governance executive summary. For the full project spec, see [PROJECT_DEFINITION.md](../docs/PROJECT_DEFINITION.md).

## 2. Architecture Summary

### High-Level Architecture
```
{ARCHITECTURE_DIAGRAM}
```

### Infrastructure Strategy
| Concept | Choice |
|:---|:---|
| **Primary Cloud** (where infrastructure runs) | {PRIMARY_CLOUD} |
| **Target Environments** (what the platform interacts with) | {TARGET_ENVIRONMENTS} |

> **Full Details**: See [Architecture README](../docs/architecture/README.md) and [Deployment Spec](../docs/core/07-deployment-infrastructure.md)

## 3. Technology Stack

| Layer | Technology | ADR |
|:---|:---|:---|
| {LAYER_1} | {TECHNOLOGY_1} | {ADR_REF_1} |
| {LAYER_2} | {TECHNOLOGY_2} | {ADR_REF_2} |
| {LAYER_3} | {TECHNOLOGY_3} | {ADR_REF_3} |
| {LAYER_4} | {TECHNOLOGY_4} | {ADR_REF_4} |

> **Full Details**: See [ADR Index](../docs/adr/README.md)

## 4. Repository Strategy

**{REPO_STRATEGY}**: {REPO_STRATEGY_DESCRIPTION}

The **home repo** ([`{REPO_NAME}`](https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME})) is the single source of truth — all issues, documentation, source code, and project coordination happen here.

> **Full Details**: See [HOME_REPO.md](./HOME_REPO.md) and [REPOSITORY_STRATEGY.md](./REPOSITORY_STRATEGY.md)

## 5. Governance & Workflow

{WORKFLOW_DESCRIPTION}

> **Full Details**: See [GITHUB_PROJECT_SETUP.md](./github/GITHUB_PROJECT_SETUP.md)

## 6. Phased Roadmap (Summary)

| Phase | Scope | Duration | Key Deliverable |
|:---|:---|:---|:---|
| **{PHASE_0}** | {PHASE_0_SCOPE} | {PHASE_0_DURATION} | {PHASE_0_DELIVERABLE} |
| **{PHASE_1}** | {PHASE_1_SCOPE} | {PHASE_1_DURATION} | {PHASE_1_DELIVERABLE} |
| **{PHASE_2}** | {PHASE_2_SCOPE} | {PHASE_2_DURATION} | {PHASE_2_DELIVERABLE} |
| **{PHASE_3}** | {PHASE_3_SCOPE} | {PHASE_3_DURATION} | {PHASE_3_DELIVERABLE} |

> **Full Details**: See [ROADMAP.md](./ROADMAP.md)

## 7. Risks & Mitigation

| Risk | Impact | Mitigation |
|:---|:---|:---|
| {RISK_1} | {RISK_1_IMPACT} | {RISK_1_MITIGATION} |
| {RISK_2} | {RISK_2_IMPACT} | {RISK_2_MITIGATION} |
| {RISK_3} | {RISK_3_IMPACT} | {RISK_3_MITIGATION} |

## 8. Open Questions

| Question | Options | Status |
|:---|:---|:---|
| {QUESTION_1} | {OPTIONS_1} | {STATUS_1} |
| {QUESTION_2} | {OPTIONS_2} | {STATUS_2} |

## 9. Related Documents

### Planning & Execution
- [PROJECT_PLAN.md](./PROJECT_PLAN.md) — Full project plan with all phases, tasks, and sprint planning
- [ROADMAP.md](./ROADMAP.md) — Phase timeline and dependencies
- [AI_TIME_ESTIMATION.md](./AI_TIME_ESTIMATION.md) — AI-assisted time estimates for all phases
- [Implementation Plans](./plans/) — Execution adjustments and sprint corrections (IPLAN index)

### Project Specification
- [PROJECT_DEFINITION.md](../docs/PROJECT_DEFINITION.md) — Full project specification
- [Architecture README](../docs/architecture/README.md) — System architecture diagram
- [ADR Index](../docs/adr/README.md) — Architecture Decision Records

### Repository & Governance
- [Home Repository Guide](./HOME_REPO.md) — Central repo structure and usage
- [Repository Strategy](./REPOSITORY_STRATEGY.md) — Repository architecture
- [GitHub Project Setup](./github/GITHUB_PROJECT_SETUP.md)
- [GitHub Tools Setup](./github/GITHUB_TOOLS_SETUP.md) — gh CLI and MCP server configuration
- [GitHub Workflows](./github/GITHUB_WORKFLOWS.md) — CI/CD and automation workflows
- [Roles and Tools Guide](./ROLES_AND_TOOLS.md) — Human vs AI responsibilities and tool access
- [Branching Strategy](./BRANCHING_STRATEGY.md)
- [Release Process](./RELEASE_PROCESS.md)
- [Governance Rules](./GOVERNANCE_RULES.md) — Operational policies, naming conventions, security posture
- [Definition of Done](./DEFINITION_OF_DONE.md)

---

## Placeholder Reference

| Placeholder | Description | Example |
|:------------|:------------|:--------|
| `{PROJECT_NAME}` | Full project name | AI Cost Monitoring Platform |
| `{PROJECT_PREFIX}` | Short prefix for issues/labels | AIOCTO |
| `{PROJECT_DESCRIPTION}` | One-sentence description | An AI-powered FinOps platform |
| `{CORE_DIFFERENTIATOR}` | What makes this project unique | Uses AI agents with MCP servers |
| `{PRIMARY_CLOUD}` | Main cloud provider | GCP, AWS, Azure |
| `{TARGET_ENVIRONMENTS}` | Environments the project targets | AWS, Azure, GCP, Kubernetes |
| `{REPO_STRATEGY}` | Repository strategy type | Monorepo, Multi-repo |
| `{REPO_NAME}` | Repository name | ai-cost-monitor |
| `{GITHUB_HOST}` | GitHub host | github.com, github.enterprise.com |
| `{GITHUB_ORG}` | GitHub organization | my-org |
| `{PHASE_N}` | Phase identifier | Phase 1, Sprint 0 |
| `{DATE}` | Current date | 2026-02-17 |
| `{STATUS}` | Document status | DRAFT, APPROVED, FINAL |
