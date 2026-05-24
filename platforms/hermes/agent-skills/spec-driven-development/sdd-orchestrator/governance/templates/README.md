# AI Cloud Cost Monitoring

[![GCP](https://img.shields.io/badge/cloud-GCP-4285F4?logo=google-cloud)](https://cloud.google.com)
[![Phase](https://img.shields.io/badge/phase-1%20active-brightgreen)](https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME})
[![Board](https://img.shields.io/badge/project-board%20%2331-blue)](https://{GITHUB_HOST}/orgs/{GITHUB_ORG}/projects/{PROJECT_BOARD_NUMBER})

AI-powered cost monitoring and optimization across AWS, Azure, GCP, and Kubernetes. Built on Google ADK (Agent Development Kit) with MCP (Model Context Protocol) servers for cloud data access. Natural language queries via CopilotKit streaming UI.

> **Home Repository** — This repo is the central hub for documentation, specifications, governance, issue tracking, and all component source code. Components live under `components/`. See [HOME_REPO.md](governance/HOME_REPO.md) for details.

---

## Architecture (v2.0)

### 2-Layer Agent Design

```
                     User Query (Natural Language)
                              |
                    CopilotKit (AG-UI/SSE)
                              |
                     FastAPI Backend
                              |
              +---------------+---------------+
              |                               |
   Coordinator Agent              Domain Agents (4)
   (Intent classification,        - Cost Agent
    routing, orchestration)       - Remediation Agent
              |                   - Cross-Cloud Agent
              +-------+----------+
                      |
            MCP Servers (4, data access only)
          +------+------+------+--------+
          |      |      |      |        |
        GCP    AWS    Azure  OpenCost
        MCP    MCP    MCP    MCP
          |      |      |      |
     Cloud APIs (billing, compute, storage, K8s)
```

**Architecture v2.0 Simplifications**:

- MCP Servers: 8 → 4 (data access only, using native cloud provider MCP servers)
- AI Agents: 11 → 5 (removed Cloud Agent layer, merged Domain Agents)
- UI: CopilotKit Chat MVP (Grafana deferred to post-MVP)
- ETL: Deferred (MCP servers query cloud APIs in real-time)

### Component Summary

| Component | Count | Technology |
|:----------|:-----:|:-----------|
| AI Agents | 5 | Google ADK (Coordinator + Cost + Remediation + Cross-Cloud) |
| MCP Servers | 4 | 3 native (AWS/Azure/GCP) + 1 custom (OpenCost) |
| Frontend | 1 | Next.js + CopilotKit (AG-UI protocol) |
| Backend | 1 | FastAPI on Cloud Run |
| Monitored Clouds | 4 | AWS, Azure, GCP, Kubernetes |

---

## Project Status

| Phase | Duration | Dates | Status |
|:------|:--------:|:------|:------:|
| Sprint 0: Research & Decisions | 1 week | Feb 17-21, 2026 | Done |
| Phase 1: GCP Cost Guard | 1 week | Feb 24-28 | In Progress |
| Phase 2: Foundation Infrastructure | 3 weeks | Mar 3-21 | Todo |
| Phase 3: MCP Servers (4) | 2 weeks | Mar 24 - Apr 4 | Todo |
| Phase 4: AI Agents (5) | 3 weeks | Apr 7-25 | Todo |
| Phase 5: CopilotKit Chat | 2 weeks | Apr 28 - May 9 | Todo |
| Phase 6: Event Processing | 2 weeks | May 12-23 | Todo |
| Phase 7: Multi-Tenant & A2A | 4 weeks | May 26 - Jun 20 | Conditional |
| Phase 8: Security & Testing | 4 weeks | Jun 23 - Jul 18 | Conditional |

**Total**: 20 weeks (Feb 17 - Jul 18, 2026). See [ROADMAP.md](governance/ROADMAP.md) for details.

**Project Board**: [#{PROJECT_BOARD_NUMBER}](https://{GITHUB_HOST}/orgs/{GITHUB_ORG}/projects/{PROJECT_BOARD_NUMBER}) | **Epics**: #11-#18 | **Phase 1 Tasks**: #19-#32

---

## Getting Started

### For Developers

1. [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) — Local setup, project structure, common tasks
2. [CONTRIBUTING.md](CONTRIBUTING.md) — Code standards, git workflow, testing guidelines
3. [HANDOFF.md](HANDOFF.md) — Project status, what's built, immediate next steps
4. [docs/core/](docs/core/) — Technical specifications (8 specs)
5. [docs/adr/](docs/adr/) — Architecture Decision Records (8 ADRs)

### For AI Agents

- [README_AIAGENT.md](README_AIAGENT.md) — Universal rules for any AI assistant (Copilot, Claude, Gemini, etc.)
- [CLAUDE.md](CLAUDE.md) — {AI_TOOL_NAME} Code-specific session and MCP configuration

### Home Cloud vs Monitored Clouds

- **Home Cloud (GCP)**: Where the platform runs — Cloud Run, BigQuery, Firestore, Secret Manager
- **Monitored Clouds**: What the platform analyzes — AWS, Azure, GCP, Kubernetes cost data via MCP servers

The platform is cloud-agnostic in monitoring but GCP-specific in deployment ([ADR-002](docs/adr/002-gcp-only-first.md)).

### Deployment to GCP

1. **Prerequisites**: GCP project with billing enabled, gcloud CLI installed
2. **Deploy**: Follow the [GCP Deployment Guide](GCP-DEPLOYMENT.md)
3. **Configure**: Use [.env.example](.env.example) for environment variables
4. **Infrastructure**: Terraform modules in component repo `{PROJECT_PREFIX}-infrastructure`

---

## Repository Structure

```
{REPO_NAME}/          (Home Repo - docs & governance)
|-- .github/
|   |-- ISSUE_TEMPLATE/            8 issue templates
|   |-- workflows/                 9 GitHub Actions workflows
|   |-- labeler.yml                PR labeling rules
|   |-- CODEOWNERS                 Auto-assign PR reviewers
|   +-- PULL_REQUEST_TEMPLATE.md
|
|-- governance/                    Project governance
|   |-- PROJECT_PLAN.md            Full project plan (~75 tasks)
|   |-- ROADMAP.md                 Phase timeline and dependencies
|   |-- GITHUB_PROJECT_SETUP.md       AI workflow setup
|   |-- GITHUB_WORKFLOWS.md        Workflow documentation
|   |-- REPOSITORY_STRATEGY.md     Monorepo architecture
|   |-- HOME_REPO.md               Home repo guide
|   +-- ...                        (branching, DoD, releases)
|
|-- docs/
|   |-- adr/                       8 Architecture Decision Records
|   |-- core/                      8 Technical specifications
|   |-- architecture/              System diagrams
|   +-- UX/                        Implementation guides
|
|-- components/                    Component source code
|   |-- {SERVICE_NAME}/            GCP budget alerts + auto-remediation
|   |-- mcp-servers/               MCP server specifications
|   |-- agents/                    AI agents (Phase 3-4)
|   |-- frontend/                  CopilotKit frontend (Phase 5)
|   +-- infrastructure/            Terraform modules (Phase 2)
|-- scripts/                       Utility scripts
|
|-- CLAUDE.md                      {AI_TOOL_NAME} Code-specific instructions
|-- README_AIAGENT.md              Universal AI agent rules
|-- DEVELOPER_GUIDE.md             Local setup guide
|-- CONTRIBUTING.md                Contribution guidelines
+-- HANDOFF.md                     Developer handoff notes
```

### Component Directories

| Component | Phase | Purpose |
|:----------|:-----:|:--------|
| `components/{SERVICE_NAME}` | 1 | GCP budget alerts + auto-remediation |
| `components/infrastructure` | 2 | Terraform modules (Cloud Run, BigQuery) |
| `components/mcp-servers` | 3 | 4 MCP servers (data access) |
| `components/agents` | 4 | 5 AI agents (Google ADK) |
| `components/frontend` | 5 | Next.js + CopilotKit |

---

## Technology Stack

### Frontend

- **Next.js** — React framework on Cloud Run
- **CopilotKit** — AI chat interface implementing AG-UI protocol (SSE streaming)
- **Tailwind CSS + shadcn/ui** — Styling

### Agent Layer

- **Google ADK** — Agent Development Kit
- **Google A2A Protocol** — Agent-to-Agent communication (Phase 7)
- **LiteLLM** — Vendor-neutral LLM abstraction ([ADR-005](docs/adr/005-use-litellm-for-llms.md))
- **AG-UI Protocol** — Agent-to-UI streaming via FastAPI SSE endpoint

### Backend

- **FastAPI** — AG-UI server (SSE streaming, JWT validation, tenant context)
- **FastMCP** — MCP server framework (OpenCost custom server)
- **Cloud Tasks + Cloud Scheduler** — Background jobs ([ADR-006](docs/adr/006-cloud-native-task-queues-not-celery.md))

### Data Layer

- **BigQuery** — Cost metrics and analytics ([ADR-003](docs/adr/003-use-bigquery-not-timescaledb.md))
- **Firestore** — Configuration, task progress, metadata (Phase 1-6)
- **Cloud SQL PostgreSQL** — Multi-tenant relational data (Phase 7)
- **Cloud Storage** — Reports, exports, backups

### Infrastructure

- **Cloud Run** — Serverless containers ([ADR-004](docs/adr/004-cloud-run-not-kubernetes.md))
- **Terraform** — Infrastructure as Code
- **OpenTelemetry** — Distributed tracing ([ADR-008](docs/adr/008-otel-gen-ai-conventions.md))

### MCP Servers (Data Access)

- **GCP**: `gcloud-mcp` + BigQuery MCP (native)
- **AWS**: `@awslabs/mcp-server-aws-core` (native)
- **Azure**: `Azure.Mcp.Server` (native)
- **OpenCost**: Custom FastMCP server (K8s cost allocation)

> MCP servers provide DATA ACCESS only. AI Agents handle reasoning, forecasting, and decisions. See [ADR-001](docs/adr/001-use-mcp-servers.md).

---

## Cloud Provider Integration

| Provider | MCP Server | Capabilities |
|:---------|:-----------|:-------------|
| **AWS** | `@awslabs/mcp-server-aws-core` | Cost Explorer, Compute Optimizer, Trusted Advisor, CloudWatch |
| **Azure** | `Azure.Mcp.Server` | Cost Management, Advisor, Resource Graph, Monitor |
| **GCP** | `gcloud-mcp` + BigQuery MCP | Cloud Billing, Recommender, Asset Inventory, Monitoring |
| **Kubernetes** | Custom OpenCost MCP | OpenCost, VPA/HPA, Resource Metrics |

---

## Operational Modes

| Mode | Trigger | Description |
|:-----|:--------|:------------|
| **Interactive** | User query | Natural language via CopilotKit chat with streaming responses |
| **Scheduled** | Cron | Cost sync (4h), resource inventory (6h), anomaly detection (4h), forecasts (daily) |
| **Event-Driven** | Webhooks | Cloud provider alerts — budget thresholds, anomaly detection, policy violations |
| **A2A** (Phase 7) | External agents | Google A2A Protocol gateway for external AI agent queries |

---

## Architecture Decision Records

| ADR | Decision |
|:----|:---------|
| [ADR-001](docs/adr/001-use-mcp-servers.md) | Use MCP Servers for cloud data access |
| [ADR-002](docs/adr/002-gcp-only-first.md) | Start with GCP-only deployment |
| [ADR-003](docs/adr/003-use-bigquery-not-timescaledb.md) | Use BigQuery for metrics, not TimescaleDB |
| [ADR-004](docs/adr/004-cloud-run-not-kubernetes.md) | Deploy to Cloud Run, not Kubernetes |
| [ADR-005](docs/adr/005-use-litellm-for-llms.md) | Use LiteLLM for vendor-neutral LLM access |
| [ADR-006](docs/adr/006-cloud-native-task-queues-not-celery.md) | Cloud-native task queues, not Celery |
| [ADR-007](docs/adr/007-grafana-plus-agui-hybrid.md) | Grafana + AG-UI hybrid (Grafana deferred to post-MVP) |
| [ADR-008](docs/adr/008-otel-gen-ai-conventions.md) | OTEL Gen-AI semantic conventions |
| [ADR-009](docs/adr/009-ai-pr-review-custom-workflow.md) | AI PR review via custom GitHub Actions workflow |

---

## Technical Specifications

| Spec | Topic |
|:-----|:------|
| [01-database-schema.md](docs/core/01-database-schema.md) | Data model and storage strategy |
| [02-mcp-tool-contracts.md](docs/core/02-mcp-tool-contracts.md) | MCP server tool specifications |
| [03-agent-routing-spec.md](docs/core/03-agent-routing-spec.md) | Agent orchestration and routing |
| [04-tenant-onboarding.md](docs/core/04-tenant-onboarding.md) | Multi-tenant setup (Phase 7) |
| [05-api-endpoint-spec.md](docs/core/05-api-endpoint-spec.md) | REST API specifications |
| [07-deployment-infrastructure.md](docs/core/07-deployment-infrastructure.md) | Cloud Run deployment |
| [08-cost-model.md](docs/core/08-cost-model.md) | Platform pricing and cost structure |
| [09-observability-spec.md](docs/core/09-observability-spec.md) | Observability and tracing |

---

## Governance

| Document | Purpose |
|:---------|:--------|
| [PROJECT_PLAN.md](governance/PROJECT_PLAN.md) | Full project plan (~75 tasks, sprint planning) |
| [ROADMAP.md](governance/ROADMAP.md) | Phase timeline and dependency graph |
| [GOVERNANCE_RULES.md](governance/GOVERNANCE_RULES.md) | Operational policies and conventions |
| [AI_TIME_ESTIMATION.md](governance/AI_TIME_ESTIMATION.md) | AI-optimized time estimates |
| [REPOSITORY_STRATEGY.md](governance/REPOSITORY_STRATEGY.md) | Monorepo architecture |
| [BRANCHING_STRATEGY.md](governance/BRANCHING_STRATEGY.md) | Git branching model |
| [DEFINITION_OF_DONE.md](governance/DEFINITION_OF_DONE.md) | Completion criteria |
| [RELEASE_PROCESS.md](governance/RELEASE_PROCESS.md) | Versioning and releases |
| [GITHUB_WORKFLOWS.md](governance/GITHUB_WORKFLOWS.md) | CI/CD workflow documentation |

---

## GitHub Automation

10 GitHub Actions workflows for CI/CD, project management, and quality gates:

| Workflow | Trigger | Purpose |
|:---------|:--------|:--------|
| CI | Push/PR | Lint (ruff), type check (mypy), test (pytest), security (bandit) |
| PR Labeler | PR opened | Auto-label by files changed and PR size |
| Stale | Weekly | Mark/close inactive issues and PRs |
| CodeQL | Push/PR/weekly | Security vulnerability analysis |
| Release | Tag push | Create GitHub releases with changelog |
| Auto Add to Project | Issue/PR opened | Add to Project Board #{PROJECT_BOARD_NUMBER} (Status: Todo) |
| Bulk Add to Project | Manual dispatch | Batch add issues to project |
| Issue Label Sync | Issue labeled/assigned | Sync AI/status labels to board status |
| Phase Transition | Manual dispatch | Bulk phase Todo/Backlog transitions |
| AI PR Review | PR opened/updated | Automated code review via {AI_TOOL_NAME} Code CLI ([ADR-009](docs/adr/009-ai-pr-review-custom-workflow.md)) |

See [GITHUB_WORKFLOWS.md](governance/GITHUB_WORKFLOWS.md) for configuration details.

---

## Security & Deployment

### Single-Tenant Mode (Default)

- Single organization managing cloud costs
- Firestore for config/metadata (no PostgreSQL overhead)
- All authenticated users trusted (RBAC optional)

### Multi-Tenant Mode (Phase 7)

- PostgreSQL Row-Level Security on `tenant_id`
- Per-tenant credential management (Secret Manager)
- RBAC: Super Admin, Org Admin, Operator, Analyst, Viewer

### Security Controls

- OAuth 2.0/OIDC authentication (provider per Sprint 0 decision)
- JWT with refresh tokens
- AES-256 encryption at rest, TLS 1.3 in transit
- Audit logging with 7-year retention (Phase 8)
- Trivy container scanning in CI (Phase 8)

---

**Project**: AI Cloud Cost Monitoring
**Organization**: {GITHUB_ORG}
**Repository**: [{REPO_NAME}](https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME})
**Project Board**: [#{PROJECT_BOARD_NUMBER}](https://{GITHUB_HOST}/orgs/{GITHUB_ORG}/projects/{PROJECT_BOARD_NUMBER})
