# Recommended Platform Technology Stack: Authoritative Reference Architecture & SDD Layer Mapping

## Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-10-10 |
| Author | Framework Maintainer |
| Framework Version | 0.91.3 |
| Authority | [Decision D-0013 / GD-13](DECISIONS.md) & [CHG-83](../archive/CHG-83/CHG-83.yaml) |

---

## 1. Purpose & Relationship to Framework Core

The **`aidoc-flow-framework`** establishes a 10-layer Specification-Driven Development (SDD) contract
(BRD $\rightarrow$ PRD $\rightarrow$ EARS $\rightarrow$ BDD $\rightarrow$ ADR $\rightarrow$ SPEC $\rightarrow$ TDD $\rightarrow$ IPLAN $\rightarrow$ Code $\rightarrow$ EVAL $\rightarrow$ Verified).
Per **[Decision D-0013 / GD-13](DECISIONS.md)**, the core framework specifications (`framework/layers/` and `framework/governance/`)
are **strictly engine-agnostic and vendor-neutral**: they define life-cycles, interface schemas, declarative workflow graphs (`.sw.yaml`),
quality gates, and review crews without tying projects to any proprietary software or commercial SaaS.

This document serves as the **authoritative platform governance guidance**. It defines our ecosystem's
**recommended reference architecture**, mapping the vendor-agnostic framework contracts directly to our
production technology stack. Projects adopting this stack use the operational blueprints in
[`framework/governance/aidoc/`](aidoc/) to instantiate runtimes with zero architectural drift.

---

## 2. The Six Architectural Pillars

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     THE SIX PILLARS OF OUR STACK                                 │
├───────────────────────────────┬──────────────────────────────────┬───────────────────────────────┤
│ 1. Strictly Open Source       │ 2. Zero-Trust Defense in Depth   │ 3. AI-First & Model Context Native      │
│ 100% open-source software     │ gVisor syscall isolation, eBPF   │ Laya + LiteLLM smart router,  │
│ (MIT / Apache 2.0 / BSD); no  │ Falco EDR, CrowdSec IPS,         │ Langfuse Prompt CMS, Bytebase │
│ commercial SaaS traps.        │ Tailscale VPN, socket proxy.     │ native AI schema migration engine.  │
├───────────────────────────────┼──────────────────────────────────┼───────────────────────────────┤
│ 4. Unified OLAP Telemetry     │ 5. Multi-Tenant Consolidation    │ 6. Polyglot High Performance  │
│ ClickHouse single store for   │ 3-node HA PostgreSQL 18 cluster, │ Python 3.15 default (uv),     │
│ HyperDX (APM), Langfuse (AI), │ shared Temporal server, and      │ Rust, Go, Node.js 22 LTS / TS.│
│ and Coroot (eBPF metrics).    │ shared NATS JetStream broker.    │ Containerized via Docker CE.  │
└───────────────────────────────┴──────────────────────────────────┴───────────────────────────────┘
```

1. **Strictly Open Source**: Every runtime dependency is permissively licensed and self-hostable without commercial licensing or proprietary cloud lock-in.
2. **Zero-Trust Defense in Depth**: Dynamic code execution and autonomous coding agents operate under strict user-space kernel virtualization (**gVisor `runsc`**), modern eBPF threat monitoring (**Falco**), ingress intrusion prevention (**CrowdSec**), and machine identity secrets injection (**Infisical**).
3. **AI-First & Model Context Native**: Models are unified behind **LiteLLM** and dynamically routed by **Laya**; prompts and evaluation datasets are governed in **Langfuse**; database schemas are inspected and migrated via **Bytebase Model Context Protocol**.
4. **Unified OLAP Telemetry**: Telemetry storage is consolidated into a single columnar **ClickHouse** cluster powering full-stack APM (**HyperDX**), LLM observability (**Langfuse**), and kernel network profilers (**Coroot**).
5. **Multi-Tenant Infrastructure Consolidation**: Core platform state is centralized into shared, resilient clusters partitioned cleanly by namespace or account: a 3-node HA **PostgreSQL 18** cluster, a shared **Temporal Server**, and clustered **NATS JetStream**.
6. **Polyglot High Performance**: Standardized build toolchains across Python 3.15 default (via Astral `uv`), Rust (`cargo`), Go, and TypeScript (`pnpm`).

---

## 3. Master Platform Technology Matrix

| Layer | Platform Component | Version / Runtime | Core Role & Rationale | SDD Framework Contract |
|---|---|---|---|---|
| **Host Hypervisor** | **Debian 13 (Trixie)** | Linux Kernel 6.12+ LTS | Minimal footprint (~90 MB idle RAM), native BTF (`/sys/kernel/btf/vmlinux`), cgroups v2 PSI. | Host OS foundation for CI runners and workers. |
| **Container Engine** | **Docker CE** | Latest Upstream Engine | Containerization backed by `docker-socket-proxy` to prevent daemon compromise. | Runtime container executor. |
| **Agent Syscall Sandbox** | **gVisor (`runsc`)** | User-Space Linux Kernel | Virtualizes Linux syscalls for coding agents and shell activities with `--network=none` and dropped caps. | [`WORKTREE_FLOW.md`](WORKTREE_FLOW.md) §2.3 Sandboxed Agent Profile. |
| **Edge Ingress & Gateway**| **Traefik v3** | v3.1+ | Automatic Let's Encrypt TLS, native HTTP/3, and dynamic discovery via socket proxy. | Platform boundary ingress. |
| **Perimeter Defense** | **Tailscale + CrowdSec** | Mesh VPN + IPS | Tailscale hides admin UIs; CrowdSec blocks malicious traffic dynamically in `nftables`. | Perimeter security. |
| **Identity & SSO** | **Authentik** | Go / Python Core | Open-source IdP with reverse-proxy Outposts for forward-auth SSO across web consoles. | Actor authentication & gate enforcement. |
| **Secret Management** | **Infisical** | In-Memory Vault | Injects encrypted secrets directly into process RAM (`infisical run -- <cmd>`); machine identities. | Worktree and agent runner credential boundary. |
| **AI Model Gateway** | **Laya + LiteLLM** | OpenAI-Compatible Proxy | Laya routes intent/complexity; LiteLLM manages spend caps, fallbacks, and standardizes `gen_ai.*` OTel spans. | [`ENGINE_TELEMETRY.md`](ENGINE_TELEMETRY.md) & Model Proxy Socket. |
| **Workflow Engine** | **Temporal Server** | Shared Multi-Tenant Cluster | Durable execution engine for SDD lifecycles, SAGA compensations, retries, and crash recovery. | [`DURABLE_EXECUTION_STANDARD.md`](DURABLE_EXECUTION_STANDARD.md) Tier 1 Durable Workflow. |
| **Agent Reasoning** | **LangGraph Core** | Standard Python Callables | Cyclical agent reasoning loops executed inside plain Temporal Activities (`@activity.defn`) with heartbeating. | [`DURABLE_EXECUTION_STANDARD.md`](DURABLE_EXECUTION_STANDARD.md) Tier 2 Cognitive Flows. |
| **Database Migrations** | **Bytebase** | AI Schema Migration Engine | Manages DDL migrations for PostgreSQL 18 and ClickHouse; exposes native Model Context Protocol to coding agents. | Layer 06 SPEC / Layer 07 TDD Schema Contracts. |
| **Primary Relational DB** | **PostgreSQL 18** | `postgres:18-alpine` | Application state, native UUIDv7, async direct I/O, `pgvector`, and `xp.ledger` partitioned audit tables. | Layer 06 SPEC Database Contracts. |
| **Analytical OLAP Store** | **ClickHouse** | Columnar Engine | Unified storage for HyperDX, Langfuse, and Coroot with 85–90% disk compression. | Out-of-band audit and telemetry data plane. |
| **Observability (APM)** | **HyperDX** | Full-Stack APM | Replaces Grafana/Loki/Tempo; ClickHouse telemetry + PostgreSQL UI/alert metadata. UI on `:8080`. | System-wide trace correlation & session replay. |
| **LLM Observability** | **Langfuse** | Self-Hosted v3 | Authoritative Prompt CMS with immutable versions; evaluation datasets and LLM-as-a-judge scoring. UI on `:3000`. | Layer 10 EVAL & [`ENGINE_TELEMETRY.md`](ENGINE_TELEMETRY.md). |
| **Zero-Code Profiler** | **Coroot** | Modern-eBPF Probe | Maps TCP service calls, latency histograms, and OOM kills without SDKs into ClickHouse. UI on `:8085`. | System health monitoring. |
| **Runtime Security** | **Falco** | Modern-eBPF Probe | Sub-1% CPU syscall monitoring; flags container breakouts, shell escapes, and unauthorized network calls. | Deterministic runtime verification. |
| **Telemetry Pipeline** | **OTel Collector Contrib**| `otelcol-contrib` | Central hub (`:4317`/`:4318`), scrubs secrets/PII, tails host `.interlog/private.log` via `filelogreceiver`. | [`ENGINE_TELEMETRY.md`](ENGINE_TELEMETRY.md) Standard Spans. |
| **Asynchronous Messaging**| **NATS JetStream** | v2.12+ Clustered | Durable inter-project messaging with multi-account isolation (`nsc`), CloudEvents v1.0, and Protobuf contracts. | Layer 06 SPEC Event Contracts. |
| **Object Storage** | **MinIO / S3** | S3-Compatible Storage | Stores large artifacts, diffs, plans, conversation blobs, and prompt text exceeding 256 KB. | Out-of-band artifact plane. |

---

## 4. SDD 10-Layer Execution Mapping

The following table details how each phase of the SDD lifecycle maps to the recommended platform technology stack:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             SDD LAYER TO PLATFORM RUNTIME MAPPING                                │
├───────┬──────────────────────────┬─────────────────────────────┬─────────────────────────────────┤
│ Layer │ SDD Artifact             │ Platform Runtime Role       │ Concrete Tooling Implementation │
├───────┼──────────────────────────┼─────────────────────────────┼─────────────────────────────────┤
│ 01    │ BRD (Business Context)   │ Tier 2 Cognitive Crew       │ LangGraph review in Temporal Act│
│ 02    │ PRD (Product Scope)      │ Tier 2 Cognitive Crew       │ LangGraph review in Temporal Act│
│ 03    │ EARS (Requirements)      │ Tier 2 Cognitive Crew       │ LangGraph decompose in Activity │
│ 04    │ BDD (Scenarios)          │ Tier 2 Cognitive Crew       │ LangGraph scenario generation   │
│ 05    │ ADR (Decisions)          │ Tier 2 Cognitive Crew       │ LangGraph trade-off evaluation  │
│ 06    │ SPEC (Contracts)         │ Tier 3 Schema & Interface   │ Bytebase Schema Engine + Protobuf/NATS    │
│ 07    │ TDD (Test Cases)         │ Tier 3 Test Verification    │ Pytest + Testcontainers (PG 18) │
│ 08    │ IPLAN (Plan & Manifest)  │ Tier 1 Durable State Machine│ Temporal Workflow Orchestration │
│ 09    │ Code (Source & Diffs)    │ Tier 3 Sandboxed Execution  │ gVisor runsc + Infisical + uv   │
│ 10    │ EVAL (Quality Gate)      │ Tier 2/3 Evaluation Gate    │ Langfuse Datasets + sdd_doc_lint│
└───────┴──────────────────────────┴─────────────────────────────┴─────────────────────────────────┘
```

### Detailed Layer Blueprints
1. **Layers 01–05 (Specification & Deliberation):** Executed as cyclical multi-persona review crews ([`REVIEW_CREWS.yaml`](REVIEW_CREWS.yaml)) implemented via LangGraph StateGraphs inside plain Temporal activities. Prompts are resolved from the Langfuse Prompt CMS via `prompt_manifest_id`.
2. **Layer 06 (SPEC):** Specifications define:
   - Synchronous public APIs via typed contracts.
   - Asynchronous messaging interfaces via **CloudEvents v1.0** and **Protobuf** schemas (routed over NATS JetStream).
   - Relational and vector database contracts via **PostgreSQL 18** idioms (UUIDv7 monotonic keys, `pgvector`, and `xp.ledger` partitioned tables) and **Bytebase Schema Engine** schema definitions.
3. **Layer 07 (TDD):** Test suites validate component contracts using:
   - Fast unit tests with deterministic mocks.
   - Ephemeral integration test containers running true PostgreSQL 18 instances for schema and migration idempotency testing.
   - Asynchronous message contract validation tests over NATS JetStream test fixtures.
4. **Layer 08 (IPLAN):** Translated 1:1 into a Temporal Workflow Definition where each task state maps to a governed activity, carrying SAGA compensation handlers in reverse LIFO order.
5. **Layer 09 (Code):** Autonomous coding agents execute within isolated Git worktrees running inside **gVisor (`runsc`)** containers:
   - Network egress is blocked (`--network=none`).
   - LLM access is restricted to the host UNIX domain socket `/var/run/litellm.sock` (`:rw`).
   - Secrets are loaded into process RAM only via `infisical run`.
   - Tool operations evaluate the deterministic quality floor (`sdd_doc_lint` + `swf_lint` + `pytest`).
6. **Layer 10 (EVAL):** Completed implementations are evaluated against benchmark datasets pulled from Langfuse. Quality scores (`relevance`, `faithfulness`, `task_completion`) are logged back to Langfuse and correlated with HyperDX traces via W3C `traceparent`.

---

## 5. Adoption & Operational Blueprints

To adapt a consumer project to this recommended platform stack, adopt the corresponding templates from [`framework/governance/aidoc/`](aidoc/):

1. **Orchestration & Cognitive Flows:** Copy [`AIDOC-TEMPORAL-LANGGRAPH-RUNTIME-TEMPLATE.md`](aidoc/AIDOC-TEMPORAL-LANGGRAPH-RUNTIME-TEMPLATE.md) into `.aidoc/project/runtime/temporal_langgraph.py`.
2. **Database & Schema Governance:** Copy [`AIDOC-BYTEBASE-POSTGRES-SCHEMA-TEMPLATE.md`](aidoc/AIDOC-BYTEBASE-POSTGRES-SCHEMA-TEMPLATE.md) into `.aidoc/project/database/bytebase_postgres.md`.
3. **Asynchronous Messaging:** Copy [`AIDOC-NATS-CLOUDEVENTS-PROTOBUF-TEMPLATE.md`](aidoc/AIDOC-NATS-CLOUDEVENTS-PROTOBUF-TEMPLATE.md) into `.aidoc/project/layers/06_SPEC/contracts/nats_cloudevents.proto`.
4. **Agent Sandbox Profile:** Copy [`AIDOC-GVISOR-SANDBOX-EXECUTION-PROFILE.md`](aidoc/AIDOC-GVISOR-SANDBOX-EXECUTION-PROFILE.md) into `.aidoc/project/security/gvisor_profile.yaml`.
5. **Observability & Evaluation:** Copy [`AIDOC-LANGFUSE-HYPERDX-OBSERVABILITY-TEMPLATE.md`](aidoc/AIDOC-LANGFUSE-HYPERDX-OBSERVABILITY-TEMPLATE.md) into `.aidoc/project/observability/telemetry_pipeline.yaml`.
