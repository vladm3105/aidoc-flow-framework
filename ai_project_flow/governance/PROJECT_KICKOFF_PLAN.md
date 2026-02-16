# Project Kickoff Plan: {PROJECT_NAME}

**Project Prefix**: `{PROJECT_PREFIX}`
**Date**: {DATE}
**Status**: APPROVED
**Version**: 3.0

## 1. Executive Summary

**AI Cloud Cost Monitoring** is an AI-agent-powered FinOps platform that provides intelligent cloud cost analysis, optimization recommendations, and automated remediation across AWS, Azure, GCP, and Kubernetes.

**Core Differentiator**: The platform uses **AI agents with MCP (Model Context Protocol) servers** as the primary integration pattern—not traditional REST APIs. Users interact through natural language, and AI agents orchestrate all cloud operations.

> [!NOTE]
> This is the governance executive summary. For the full project spec, see [PROJECT_DEFINITION.md](../docs/PROJECT_DEFINITION.md).

## 2. Architecture Summary

### 2-Layer Hierarchy (Simplified)
```
Layer 1: Coordinator Agent (intent classification, routing to MCP)
Layer 2: 4 Domain Agents (Cost, Remediation, Cross-Cloud, Tenant*)
Layer 3: 4 MCP Servers (AWS, Azure, GCP, OpenCost) — data access only

* Tenant Agent deferred to Phase 7 (multi-tenancy)
Note: Cloud Agents removed — Coordinator routes directly to MCP servers
```

### Home Cloud vs Monitored Clouds
| Concept | Choice |
|:---|:---|
| **Home Cloud** (where infrastructure runs) | GCP |
| **Monitored Clouds** (what the platform analyzes) | AWS, Azure, GCP, Kubernetes |

> **Full Details**: See [Architecture README](../docs/architecture/README.md) and [Deployment Spec](../docs/core/07-deployment-infrastructure.md)

## 3. Technology Stack (Locked Decisions)

| Layer | Technology | ADR |
|:---|:---|:---|
| Integration | MCP Servers (FastMCP) | ADR-001 |
| Home Cloud | GCP | ADR-002 |
| Analytics DB | BigQuery | ADR-003 |
| Compute | Cloud Run (serverless containers) | ADR-004 |
| LLM Abstraction | LiteLLM | ADR-005 |
| Task Queues | Cloud Tasks (cloud-native) | ADR-006 |
| Dashboards | CopilotKit (MVP), Grafana (post-MVP) | ADR-007 |
| Observability | OTEL Gen-AI Conventions | ADR-008 |
| MVP Database | Firestore (no PostgreSQL until multi-tenant) | — |
| Agent Framework | Google ADK | — |
| Frontend | Next.js + CopilotKit | — |
| Backend | FastAPI on Cloud Run | — |
| Auth | Auth0 or GCP Identity Platform (TBD) | — |

> **Full Details**: See [ADR Index](../docs/adr/README.md)

## 4. Repository Strategy
**Monorepo**: All documentation, governance, and component source code live in a single repository. Components are organized under `components/` ({SERVICE_NAME}, mcp-servers, agents, frontend, infrastructure).

The **home repo** ([`{REPO_NAME}`](https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME})) is the single source of truth — all issues, documentation, source code, and project coordination happen here.

> **Full Details**: See [HOME_REPO.md](./HOME_REPO.md) and [REPOSITORY_STRATEGY.md](./REPOSITORY_STRATEGY.md)

## 5. Governance & Workflow
Sprint-based iterations using GitHub Projects with Kanban, Backlog, and Roadmap views.

> **Full Details**: See [GITHUB_PROJECT_SETUP_AI_FIRST.md](./GITHUB_PROJECT_SETUP_AI_FIRST.md)

## 6. Phased Roadmap (Summary)

| Phase | Scope | Duration | Key Deliverable |
|:---|:---|:---|:---|
| **S0** | Research & Decisions | ~1 week | ADRs for LLM + Auth strategy |
| **1** | GCP Cost Guard | ~1 week | Standalone budget alerts + auto-remediation |
| **2** | Foundation Infrastructure | ~3 weeks | Cloud Run + FastAPI + Auth + CI/CD |
| **3** | MCP Servers | ~2 weeks | 4 MCP servers (3 native + OpenCost) |
| **4** | AI Agents | ~3 weeks | 5 agents (Coordinator + 4 Domain) |
| **5** | UI/UX (CopilotKit) | ~2 weeks | AI chat interface (Grafana deferred) |
| **6** | Events & Alerts | ~2 weeks | Event processing (ETL deferred) |
| **7** | Multi-Tenant & A2A | ~4 weeks | Conditional: PostgreSQL, A2A gateway |
| **8** | Security & Testing | ~4 weeks | Conditional: hardening, E2E tests |

> **Full Details**: See [ROADMAP.md](./ROADMAP.md)

## 7. Risks & Mitigation

| Risk | Impact | Mitigation |
|:---|:---|:---|
| MCP protocol immaturity | Breaking changes, limited tooling | Pin FastMCP version; wrap in abstraction layer |
| GCP API changes | Breaks Terraform modules | Pin provider versions; monitor changelogs |
| LLM cost overrun | AI Agent queries become expensive | Set token budgets via LiteLLM; cache frequent queries |
| Agent complexity | Agent orchestration difficult to debug | Build bottom-up (MCP → Domain Agents → Coordinator) |
| Scope creep (multi-tenant) | Delays core delivery | Phases 7-8 are explicitly **Conditional** |

## 8. Open Questions

| Question | Options | Status |
|:---|:---|:---|
| Default LLM provider | Gemini 2.0, Claude 3.5, GPT-4 | User-configurable via LiteLLM |
| Authentication provider | Auth0, GCP Identity Platform, Okta | TBD |
| Grafana deployment | Self-hosted vs Grafana Cloud | TBD |
| OpenCost integration | Prometheus vs direct API | TBD |

## 9. Related Documents

### Planning & Execution
*   [PROJECT_PLAN.md](./PROJECT_PLAN.md) — **Full project plan with all phases, tasks, and sprint planning**
*   [Roadmap](./ROADMAP.md) — Phase timeline and dependencies
*   [AI_TIME_ESTIMATION.md](./AI_TIME_ESTIMATION.md) — **AI-assisted time estimates for all phases**
*   [Implementation Plans](./plans/) — **Execution adjustments and sprint corrections (IPLAN index)**

### Project Specification
*   [PROJECT_DEFINITION.md](../docs/PROJECT_DEFINITION.md) — Full project specification
*   [Architecture README](../docs/architecture/README.md) — System architecture diagram
*   [ADR Index](../docs/adr/README.md) — 8 Architecture Decision Records

### Repository & Governance
*   [Home Repository Guide](./HOME_REPO.md) — Central repo structure and usage
*   [Repository Strategy](./REPOSITORY_STRATEGY.md) — Monorepo architecture
*   [GitHub Project Setup (AI-First)](./GITHUB_PROJECT_SETUP_AI_FIRST.md)
*   [GitHub Tools Setup](./GITHUB_TOOLS_SETUP.md) — gh CLI and MCP server configuration
*   [GitHub Workflows](./GITHUB_WORKFLOWS.md) — CI/CD and automation workflows
*   [Roles and Tools Guide](./ROLES_AND_TOOLS.md) — **Human vs AI responsibilities and tool access**
*   [Branching Strategy](./BRANCHING_STRATEGY.md)
*   [Release Process](./RELEASE_PROCESS.md)
*   [Governance Rules](./GOVERNANCE_RULES.md) — **Operational policies, naming conventions, security posture**
*   [Definition of Done](./DEFINITION_OF_DONE.md)

### Implementation References
*   [GCP Cost Guard](../docs/GCP-COST-GUARD.md) — Phase 1 implementation reference
*   [Multi-Cloud Cost Guard](../docs/MINIMAL-COST-GUARD.md) — Multi-cloud implementation reference
