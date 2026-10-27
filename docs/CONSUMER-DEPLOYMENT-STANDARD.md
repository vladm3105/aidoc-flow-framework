# Consumer Deployment Standard

How a consumer project deploys across environments. The authority is the
platform technology stack, not this file: spec 21 (deployment pillars and
tooling split), spec 16 (tri-environment matrix, runbooks, invariants), and
spec 11 (infrastructure provisioning phases). Where this guide and those
specs disagree, the specs win — file an issue; do not fork the standard.

## The standard

| Environment | Tool | Shape |
|---|---|---|
| Dev | Docker Compose | Lean local stack, `core` profile by default; `frontend` and `full-telemetry` on demand (spec 16 §3.1, §10.1) |
| Stage | Docker Compose for services, OpenTofu for infrastructure | Single host, production-parity single-node services + stage-only QA arsenal; Day-0 host/network via tofu (spec 16 §3.2, spec 11) |
| Prod | Per-architecture HA, OpenTofu for infrastructure | Multi-node, zero-SPOF; mechanism defined per deployment (spec 16 §3.3, spec 11) |

The split is the Goldilocks model (spec 21 §4): Compose gives sub-second
edit-refresh cycles with zero state-locking overhead for the inner loop;
OpenTofu gives declarative HCL state management with a plan-before-apply
gate for hosted tiers. Do not emulate HA topologies on dev or stage
single hosts — no multi-node datastores, no clustered brokers
(spec 16 warning, binding invariant 1).

## Dev: Compose

Run everything in containers; install nothing on the host OS beyond Docker
itself (spec 16 tenet 4, invariant 10). Baseline is `docker compose up -d`
on the `core` profile: single PostgreSQL 18, NATS JetStream, Valkey,
Temporal backed by the local database (spec 16 §3.1, §10.1). Telemetry stays
lean (OTel stdout exporter, Langfuse in PostgreSQL-only mode); bring up the
full stack only for deep analysis via the `full-telemetry` profile
(spec 16 tenet 3). Schema changes run through the Tier-1 native migration
runner against the shared `migrations/*.up.sql` directory — the identical
files Bytebase consumes on stage/prod (spec 16 §5.2, invariant 8). Keep dev
on mock/local vault materialization per the two-tier secrets design
(spec 16 §4).

## Stage: Compose services on tofu-provisioned infrastructure

Stage is one host (single OCI VM or equivalent) running the full service
set as single-node Compose services — the same Compose definitions as dev
plus the `observability` profile — with the stage-only QA arsenal (`k6`,
`nats bench`, `toxiproxy`, eBPF APM) behind the `stage-qa` profile
(spec 16 §3.2, §7, §10.2). QA/load/chaos tooling runs **only** here: banned
on dev (machine responsiveness) and forbidden in prod (synthetic-data
contamination), invariant 3. All synthetic traffic follows the four hygiene
rules (spec 16 §5.3): `X-Synthetic-QA: true` plus a unique `X-Test-Run-ID`,
the `syntheticqa: "true"` CloudEvents attribute, ephemeral sinks
(`xp.qa.v1.>`, never core subjects), and automated purging after runs
(invariant 4).

The host and network underneath come from OpenTofu **Day-0**
(`infra/tofu/bootstrap`: compute, VCN, DNS, Tailscale keys, state in OCI
Object Storage), applied non-interactively (`tofu init -input=false`,
`tofu test`, `tofu apply -input=false -auto-approve`) (spec 11 §Phase 1).
Service-level declarations (buckets, configs, identities) come from
OpenTofu **Day-2** (`infra/tofu/services`), only after host hardening and
healthy Compose services, reached over the Tailscale mesh — the two
compositions are never merged into one module (spec 11 §8 item 2).
Ingress is a dedicated `cloudflared` tunnel behind Cloudflare Access Zero
Trust; no public unauthenticated traffic (spec 16 §4).

## Prod: HA per architecture, tofu underneath

Production is multi-node with no single point of failure
(spec 16 §3.3); the serving mechanism (hardened runtimes, Kubernetes pods,
immutable appliances) is defined per deployment (spec 16 tenet 4,
invariant 10). What is uniform: tofu Day-0/Day-2 provisioning as on stage,
two-tier secrets with rotation (OCI Vault + OpenBao HA), Bytebase GitOps
migrations with approval workflow, and Cloudflare edge (WAF, DDoS, Bot
Fight) in front of the prod tunnel (spec 16 §3.3, §4). Telemetry is passive
only — zero synthetic traffic, zero chaos engines (invariant 3).

## Invariants that cross all three

- **Clean naming:** queue names, stream names, and subjects are identical
  everywhere — never environment-prefixed; isolation lives at the
  network/DNS/endpoint boundary (spec 16 tenet 1, invariant 2).
- **One migration directory:** the native runner and Bytebase consume the
  same `migrations/*.up.sql`; divergent files are prohibited (invariant 8).
- **Promotion:** feature branches squash-merge or rebase into `dev`;
  `dev` → `staging` → `main` merges are `--no-ff` only, never squash,
  protecting the merge base (spec 16 §9.1, invariant 7).
- **Daemon hygiene:** Docker daemons set `log-opts` (`max-size: 50m`,
  `max-file: 3`) with `"live-restore": true`; stateful Compose services set
  `stop_grace_period: 30s` minimum (invariants 11–12).
- **Per-project isolation:** each project gets a dedicated rootless Docker
  daemon under its own unprivileged user on shared hosts (spec 21 §2).

## Module layout (OpenTofu)

Two specs describe two axes — keep them distinct. The module *library*
(spec 21 §4.1) lives under `deploy/tofu/` with root composition files,
`modules/{network,datastore,workflows,services,observability}/`, and
per-tier bindings at `environments/staging/staging.tfvars` and
`environments/production/production.tfvars`; pin OpenTofu `>= 1.8.0` with
the Docker provider in `versions.tf`. The deployment *phasing* (spec 11)
composes from that library into two never-merged roots under `infra/tofu/`:
`bootstrap/` (Day-0: the network/hosting side) and `services/` (Day-2: the
service/data declarations). A layout with a single merged composition, or
with env bindings anywhere but the per-tier tfvars, satisfies neither spec.
