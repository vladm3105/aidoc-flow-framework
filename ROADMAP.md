# AI Doc Flow Framework — Multi-Platform Roadmap

| Field            | Value                                                        |
|------------------|--------------------------------------------------------------|
| Project          | AI Doc Flow Framework (multi-platform)                       |
| Status           | Phase 4 complete (`v0.5.0`) — Phase 5 next                    |
| Working branch   | `claude/multi-platform-migration-AamWB`                      |
| Origin           | Forked from `main` (`ucx_framework` v0.20.4)                 |
| Cutover target   | v1.0.0 — new project replaces `main`                         |
| Created          | 2026-05-18                                                   |

## Goal

Deliver the document-flow framework as **one engine-agnostic specification**
with **two independent delivery platforms**:

- **Platform A — Hermes AI**: MCP-server engine (existing `ucx_hermes`).
- **Platform B — Claude Code plugin**: native Claude Code engine — skills,
  agents, commands, hooks. No MCP backend; Claude itself replaces Hermes.

The two platforms share the `framework/` spec and nothing else. Each versions,
releases, and changes independently.

## Version Streams

Three independent SemVer streams (see `docs/PROJECT.md`):

- **Framework spec** — the shared contract.
- **Hermes AI platform** — declares the spec version it conforms to.
- **Claude Code plugin** — declares the spec version it conforms to.

The *project-level* version below tracks migration milestones only.

## Phases

### Phase 0 — Planning & Scaffolding  → `v0.1.0`
- Working branch created; planning baseline tagged.
- `ROADMAP.md`, `CHANGELOG.md`, `docs/PROJECT.md`, `docs/REPO_STRUCTURE.md`.
- `platforms/` directories established.
- Status: **complete** (`v0.1.0`).

### Phase 1 — Framework Spec Extraction  → `v0.2.0`
- **Step 0 — Legacy isolation (done):** all pre-migration content moved into
  `legacy/`; legacy GitHub Actions workflows disabled.
- Consolidate engine-agnostic content from `legacy/` into `framework/` (layers,
  registry, governance, CHG overlay).
- Define the shared conformance test suite under `tests/conformance/`.
- Tag `framework/VERSION` at its first independent release.
- Status: **complete** (`v0.2.0`) — `framework/` fully assembled, 25-test
  conformance suite green, framework spec released as `framework/v0.1.0`.

### Phase 2 — Platform A: Hermes Re-homing  → `v0.3.0`
- Copy `legacy/ucx_hermes/` + `legacy/mcp_ucx/` into `platforms/hermes/`.
- Point Hermes at `framework/`; declare `framework_spec_version`.
- Hermes passes the conformance suite.
- Status: **complete** (`v0.3.0`, `hermes/v0.1.0`).

### Phase 3 — Platform B: Claude Code Plugin  → `v0.4.0`
- Scaffold `.claude-plugin/plugin.json`.
- Port the `doc-*` skill set, commands, and agents into the plugin.
- Remove all Hermes/MCP dependency — Claude is the engine.
- Plugin passes the same conformance suite.
- Status: **complete** (`v0.4.0`, `claude-code-plugin/v0.1.0`).

### Phase 4 — Conformance & Independence  → `v0.5.0`
- Both platforms green on the shared conformance suite.
- Independent per-platform `CHANGELOG.md` and CI.
- Parity report: feature gaps between platforms documented.
- Status: **complete** (`v0.5.0`).

### Phase 5 — Cutover  → `v1.0.0`
- New project replaces `main`.
- Legacy trees archived.
- Tag `v1.0.0`; platforms tag their own first stable releases.

## Post-Migration — Tracked TODOs

Change management (the gated CHG process) is **deliberately deferred** during
migration. It is re-introduced after Phase 5. See `docs/PROJECT.md` §
Change Management for the full policy.

| TODO | Decision (recorded) | Revisit |
|------|---------------------|---------|
| **CHG-D1 — CHG implementation model** | CHG is implemented as **skills + CI/CD**, not a monolith. Skills handle authoring and the automatable gate checks (schema, upstream tags, traceability, gate report + `GATE_APPROVAL_FORM`). CI/CD enforces the gate as a required status check; the human sign-off half is enforced by GitHub branch protection / required reviewers — a skill must never self-approve. Implemented twice against the same `framework/` spec: skills + CI workflow in the Claude Code plugin, server-side in Hermes. | Post-Phase 5 |
| **CHG-D2 — CHG as a `framework/` decision** | Record CHG-D1 as a formal decision in `framework/governance/` when CHG returns, since both platforms implement it from the shared spec. | Post-Phase 5 |

## Post-v1.0 — Planned Capabilities

### Domain profiles — generalizing the IPLAN beyond software

The framework's purpose is to produce a fully-traceable, gate-approved
**IPLAN** as its terminal artifact (D-0012). v1 scopes this to **software +
devops** — the current SDD layers (EARS, BDD, ADR, TDD) are software-native
and stay that way for v1.

Post-v1.0, generalize the IPLAN to other task domains via a **domain-profile**
mechanism — additively, without reworking the core:

- **Core (domain-neutral):** the flow engine, the gate model, traceability,
  the IPLAN schema, and conformance. Already domain-independent.
- **A profile:** declares which layers apply for a domain and their schemas.
  - `profile: software` — ships in v1 (the current layer set).
  - `profile: devops` — v1 (devops-flavored layers and thresholds).
  - `profile: <non-technical>` — post-v1.0, additive: e.g. operational
    runbooks, compliance/audit planning, research plans. Each new profile is
    new layer definitions, not a change to the core.

This makes "an IPLAN for any purpose" an architectural property of the engine
while keeping every release's scope honest. Revisit after the v1.0.0 cutover.

### The IPLAN library — the corpus is the asset

A single IPLAN is reproducible and low-value. The strategic asset is a
**curated, maintained library of proven IPLANs** — codified, executable
institutional knowledge (D-0012, refinement R2). Post-v1.0, build the library
as a first-class capability:

- **Planned vs executed state** — an IPLAN is *planned* (confirmations
  pending) or *executed* (confirmations satisfied with evidence). The executed
  IPLAN is the auditable trail; audit depth scales with the work's criticality
  (D-0012, R1).
- **Proven-entry gate** — an IPLAN earns library membership only once executed
  and audited.
- **Composition** — distinguish an IPLAN *template* (the proven pattern) from
  an *instance* (a parameterised run); allow IPLANs to compose other IPLANs.
- **Freshness** — each library IPLAN records when it was last proven and
  against which versions; conformance flags stale entries for re-validation.

This is the post-v1.0 strategic destination — the framework as a system of
record for an organisation's executable process knowledge. Revisit after the
v1.0.0 cutover.
