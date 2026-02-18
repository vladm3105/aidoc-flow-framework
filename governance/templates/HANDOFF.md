# Developer Handoff - AI Cost Monitoring

**Status:** Phase 1 Active | **Updated:** February 2026

---

## Executive Summary

AI Cost Monitoring is an active project entering Phase 1 implementation. Architecture v2.0 is defined (5 agents, 4 MCP servers, 20-week timeline). Sprint 0 research is complete. Phase 1 (GCP Cost Guard) has 14 tasks on the project board ready for execution.

**Current State:** Sprint 0 done, Phase 1 in progress, 8 ADRs documented, 8 technical specs complete.

---

## What's Complete

### Sprint 0: Research & Decisions (Done)
- [x] LLM strategy: Vertex AI vs LiteLLM ([#6](https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME}/issues/6))
- [x] Auth strategy: GCP Identity Platform vs Auth0 ([#7](https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME}/issues/7))
- [x] OTEL Gen-AI conventions maturity ([#8](https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME}/issues/8))
- [x] Grafana deployment model ([#9](https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME}/issues/9))
- [x] OpenCost integration approach ([#10](https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME}/issues/10))

### Architecture & Documentation
- [x] 8 Architecture Decision Records ([docs/adr/](docs/adr/))
- [x] 8 Technical specifications ([docs/core/](docs/core/))
- [x] Project governance: roadmap, project plan, branching strategy, DoD
- [x] GitHub Project Board #{PROJECT_BOARD_NUMBER} configured (19 custom fields, 63 labels, 10 milestones)
- [x] 9 GitHub Actions workflows (CI, CodeQL, release, project automation)
- [x] 8 issue templates

### Key Decisions

| Decision | Choice | ADR |
|:---------|:-------|:----|
| Home Cloud | GCP (Cloud Run, BigQuery, Firestore) | [ADR-002](docs/adr/002-gcp-only-first.md) |
| Analytics DB | BigQuery | [ADR-003](docs/adr/003-use-bigquery-not-timescaledb.md) |
| Containers | Cloud Run (serverless) | [ADR-004](docs/adr/004-cloud-run-not-kubernetes.md) |
| LLM Access | LiteLLM (vendor-neutral) | [ADR-005](docs/adr/005-use-litellm-for-llms.md) |
| Task Queues | Cloud Tasks + Cloud Scheduler | [ADR-006](docs/adr/006-cloud-native-task-queues-not-celery.md) |
| UI Approach | CopilotKit Chat MVP (Grafana deferred) | [ADR-007](docs/adr/007-grafana-plus-agui-hybrid.md) |
| Data Access | MCP Servers (data access only) | [ADR-001](docs/adr/001-use-mcp-servers.md) |
| Observability | OTEL Gen-AI semantic conventions | [ADR-008](docs/adr/008-otel-gen-ai-conventions.md) |

---

## What's In Progress

### Phase 1: GCP Cost Guard (Feb 24-28, 2026)

Standalone GCP budget protection system. 14 sub-tasks tracked on [Project Board #{PROJECT_BOARD_NUMBER}](https://{GITHUB_HOST}/orgs/{GITHUB_ORG}/projects/{PROJECT_BOARD_NUMBER}).

**Epic**: [#11](https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME}/issues/11) | **Tasks**: #19-#32 (Status: Backlog)

Key deliverables:
- `{PROJECT_PREFIX}-{SERVICE_NAME}` component repo
- Terraform module structure
- Firestore config schema
- Pub/Sub `cost-alerts` topic
- `CostGuardedLLM` wrapper class
- Cloud Function `budget-remediation`
- Cloud Function `idle-scanner`
- GCP Budget + BigQuery Billing Export
- Integration tests + release v1.0.0

**Exit Criteria**: Budget alerts fire within 1 hour. LLM spend limits enforced. Idle resources detected weekly. Infra cost < $15/month.

---

## Implementation Phases

| Phase | Duration | Dates | Focus |
|:------|:--------:|:------|:------|
| **Phase 1** | 1 week | Feb 24-28 | GCP Cost Guard (standalone) |
| **Phase 2** | 3 weeks | Mar 3-21 | Foundation: Cloud Run, FastAPI, Auth, CI/CD, Terraform |
| **Phase 3** | 2 weeks | Mar 24 - Apr 4 | 4 MCP Servers (3 native + OpenCost custom) |
| **Phase 4** | 3 weeks | Apr 7-25 | 5 AI Agents (Coordinator + 4 Domain, Google ADK) |
| **Phase 5** | 2 weeks | Apr 28 - May 9 | CopilotKit Chat MVP (AG-UI streaming) |
| **Phase 6** | 2 weeks | May 12-23 | Event Processing & Alerts |
| **Phase 7** | 4 weeks | May 26 - Jun 20 | Multi-Tenant (PostgreSQL RLS) + A2A Gateway |
| **Phase 8** | 4 weeks | Jun 23 - Jul 18 | Security Hardening & E2E Testing |

**Total**: 20 weeks. See [ROADMAP.md](governance/ROADMAP.md) and [PROJECT_PLAN.md](governance/PROJECT_PLAN.md).

---

## Key Files for Developers

### Start Here
1. [README.md](README.md) — Architecture overview, project status
2. [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) — Local setup, project structure
3. [CONTRIBUTING.md](CONTRIBUTING.md) — Code standards, git workflow
4. [governance/PROJECT_PLAN.md](governance/PROJECT_PLAN.md) — Full task list with acceptance criteria

### Architecture
5. [docs/adr/](docs/adr/) — 8 Architecture Decision Records
6. [docs/core/01-database-schema.md](docs/core/01-database-schema.md) — Database design
7. [docs/core/02-mcp-tool-contracts.md](docs/core/02-mcp-tool-contracts.md) — MCP interfaces
8. [docs/core/03-agent-routing-spec.md](docs/core/03-agent-routing-spec.md) — Agent routing
9. [docs/core/05-api-endpoint-spec.md](docs/core/05-api-endpoint-spec.md) — REST API

### Governance
10. [governance/ROADMAP.md](governance/ROADMAP.md) — Phase timeline and dependencies
11. [governance/HOME_REPO.md](governance/HOME_REPO.md) — Home repo vs component repos
12. [governance/REPOSITORY_STRATEGY.md](governance/REPOSITORY_STRATEGY.md) — Polyrepo architecture
13. [governance/GITHUB_WORKFLOWS.md](governance/GITHUB_WORKFLOWS.md) — CI/CD workflow docs

### Deployment
14. [GCP-DEPLOYMENT.md](GCP-DEPLOYMENT.md) — GCP deployment guide
15. [docs/core/07-deployment-infrastructure.md](docs/core/07-deployment-infrastructure.md) — Cloud Run architecture

---

## Technology Stack

| Layer | Technology |
|:------|:-----------|
| Frontend | Next.js, CopilotKit (AG-UI/SSE), Tailwind + shadcn/ui |
| Agents | Google ADK, LiteLLM, AG-UI protocol |
| Backend | FastAPI, FastMCP, Cloud Tasks |
| Data | BigQuery, Firestore (Phase 1-6), Cloud SQL PostgreSQL (Phase 7) |
| MCP | GCP native, AWS native, Azure native, OpenCost custom |
| Infra | Cloud Run, Terraform, GitHub Actions |
| Observability | OpenTelemetry, Cloud Trace, Cloud Logging |

---

## Project Board Workflow

**Board**: [#{PROJECT_BOARD_NUMBER}](https://{GITHUB_HOST}/orgs/{GITHUB_ORG}/projects/{PROJECT_BOARD_NUMBER})

**Status Lifecycle**:
```
Todo (default) → Backlog (nearest phase) → In Progress → In Review → Done
```

- New issues → **Todo** (automatic)
- Nearest planning phase tasks → **Backlog** (manual via Phase Transition workflow)
- Sprint work → **In Progress** (manual or via `ai:in-progress` label)
- Code review → **In Review** (via `ai:review-requested` label or PR)
- Completed → **Done** (automatic on issue close)

**AI Workflow Labels**: `ai:ready`, `ai:in-progress`, `ai:review-requested`, `ai:blocked`, `ai:human-required`

---

**Document Version:** 2.0
**Date:** February 13, 2026
**Status:** Phase 1 Active
