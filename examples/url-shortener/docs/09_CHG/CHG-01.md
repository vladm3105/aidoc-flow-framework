---
title: "CHG: Add visit-rate analytics dashboard"
doc_id: "CHG-01"
artifact_type: CHG
layer: governance-overlay
status: Proposed
version: "1.0.0"
author: doc-chg
created: "2026-06-12"
last_updated: "2026-06-12"
custom_fields:
  document_type: chg-document
  artifact_type: CHG
  purpose: governance
  change_level: C3
  change_source: upstream
  entry_gate: GATE-01
  semver_impact: null
  affected_layers: [BRD-01, PRD-01, EARS-01, BDD-01, ADR-01, ADR-02, SPEC-01, SPEC-02, TDD-02, IPLAN-02, Code]
---

# CHG-01: Add visit-rate analytics dashboard

> **Governance overlay — NOT a lifecycle layer.** No layer number, no readiness
> score; the quality bar is **gate approval**. Authored against
> `chg/CHG-TEMPLATE.yaml`; source request `chg/test-change.md`.

## 1. Change Control

| Field | Value |
|-------|-------|
| Change ID | CHG-01 |
| Title | Add visit-rate analytics dashboard |
| Status | Proposed |
| Change Level | **C3** — cross-layer, new requirements + new persistence concern |
| Change Source | **upstream** — a BRD scope change cascading down the chain |
| Entry Gate | **GATE-01** — upstream source → business/product gate |
| SemVer Impact | N/A — not a `framework/` spec change |
| Author | doc-chg (CHG-RT-001) |
| Date Proposed | 2026-06-12 |
| Date Approved | — |
| Date Implemented | — |
| Supersedes | — |

## 2. Change Description

**What.** Move "visit-rate analytics dashboard" into scope: a per-short-link
visit-rate metric (rolling 1h / 24h / 7d windows), a per-owner dashboard
endpoint, and 30-day retention of visit timestamps for the 7d window. Cross-link
aggregations, alerting, and third-party integrations stay **out of scope**.

**Why.** Stakeholders need per-short-link traffic visibility (high-value links,
abuse spikes, capacity planning). BRD-01 excludes analytics dashboards (§7 scope,
lines 146–148, 260); this change reverses that exclusion for the visit-rate
capability only.

**Trigger.** Stakeholder change request
(`examples/url-shortener/chg/test-change.md`) — business demand for traffic
visibility on existing short links.

**Backward-compatibility & existing-contract posture.** Additive: net-new
dashboard API + visit-timestamp store, no Shorten/Redirect/Mapping-Store contract
broken; storage ships as a forward-only migration (§7 rollback consequence).
SPEC-01 §3 `increment_visit(code, event_id)` and `VisitCountRecord` are
**preserved unchanged** — per-visit timestamps ride a **separate additive path**
written async off the redirect hot path so the EARS "count never blocks redirect"
obligation holds (SPEC-01 §4 additive policy); no MAJOR bump.

**Security-impact (new authorization boundary).** This introduces the **first
authn/authz boundary** into a service whose shorten/redirect paths are
intentionally anonymous (BRD-01). "Role-restricted to link owner" presupposes an
owner-identity model that does **not** exist today — ADR-01 maps only an app-tier
principal to a least-privilege DB role, no authenticated end-user owner. That
ADR-altitude decision routes to **ADR-02** (§3); ADR-01's anonymity /
least-privilege posture is touched, and the §3 ADR-01 row records the delta.

**Retained-data sensitivity & retention rationale.** The visit-timestamp +
per-link-owner linkage is a **new retained-data path**, classified
**may-contain-PII** (as ADR-01 classifies the original URL); 30-day retention is
the minimum to serve the 7d window with headroom. At-rest protection and
least-privilege access route to SPEC-02 / ADR-02, **mirroring ADR-01's interim
compensating control for the same data class — least-privilege DB grant +
managed-tier volume encryption at rest** — so the new path is not protected to a
weaker standard than the original-URL path.

## 3. Impact Assessment — Cross-Layer Cascade (Propagation Report)

**Cascade direction:** upstream → downstream — a BRD scope change ripples the
full chain `BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code`.
**Risk level:** **High** — new persistence concern + 30-day retention + 8-layer
reach.

| Layer | Affected Artifact(s) | Impact | Cascade |
|-------|----------------------|--------|---------|
| **BRD (L1)** | BRD-01 | Add a "visit-rate analytics" capability; remove "analytics dashboards" from the out-of-scope list. | downstream |
| **PRD (L2)** | PRD-01 | Add a dashboard endpoint capability; add NFRs for 30-day visit-timestamp retention and a dashboard p95 latency target. | downstream |
| **EARS (L3)** | EARS-01 | Three new requirements: (1) **visit-rate computation** (Event-driven, on redirect); (2) **dashboard query** (Ubiquitous, role-restricted to link owner); (3) **owner-identity establishment** (Ubiquitous — ownership is bound to a link at shorten time and the owner is authenticated before any dashboard query is served). | downstream |
| **BDD (L4)** | BDD-01 | Three new scenarios, one per EARS requirement: (1) **on-redirect visit capture** (critical-path) — *Given a redirect for an issued link, When served, Then a visit timestamp is captured async off the redirect path and the redirect is not blocked*; (2) **owner views visit rate** — *Given a link with recorded visits, When the owner queries the dashboard, Then 1h/24h/7d rates are returned*; (3) **owner identity established** — *Given an owner-shortened link, When the owner authenticates and requests its dashboard, Then it is served only after ownership is verified*. | downstream |
| **ADR (L5)** | ADR-01 *(existing)* | **Boundary-impact: amended-by-ADR-02.** Visit-timestamp persistence is a **net-new metrics store owned by ADR-02**, not an extension of ADR-01's Mapping Store / `VisitCountRecord` boundary. ADR-01's anonymity / least-privilege posture **is** touched by the owner-authz boundary; ADR-02 owns that delta (no ADR-01 interface change). | lateral |
| **ADR (L5)** | ADR-02 *(new)* | **New ADR REQUIRED** (the new persistence concern makes an ADR mandatory; omitting it is a cascade regression) — three coupled decisions: (a) **metrics storage choice** (dedicated time-series store vs. rolling-window aggregation in the link DB), incl. **supply-chain criteria** (provenance, pinning, SCA gating) for any new dependency; (b) the **owner-identity / authentication model + authz boundary** (how the owner is authenticated, how ownership is bound at shorten time, what authz gates the dashboard); (c) the metrics-service **trust-boundary class** (in-process / out-of-process / external), with async off-redirect capture preserving "count never blocks redirect". | downstream |
| **SPEC (L6)** | SPEC-01 *(existing)* | **Boundary-impact: none.** `increment_visit` / `VisitCountRecord` (SPEC-01 §3) preserved unchanged; timestamps on a separate additive path. No §3/§4 section mutated — an explicit no-touch decision. | lateral |
| **SPEC (L6)** | SPEC-02 *(new)* | New component: metrics service + visit-timestamp schema + dashboard API (per-owner, role-restricted). Carries the **abuse-case controls** (rate-limit, query bounds over windows, window-bound + owner-selector input validation against injection, replay rejection) and **at-rest protection + least-privilege access** for the retained path. | downstream |
| **TDD (L7)** | TDD-02 *(new)* | New test cases: on-redirect async-capture **non-blocking behavior** (redirect served regardless of timestamp-write outcome), metric correctness across 1h/24h/7d windows, 30-day retention boundary, **owner-identity establishment / authentication-binding**, dashboard authorization (owner-only), **plus abuse-case pairs** — cross-owner / IDOR enumeration, expensive-query DoS over the windows, per-link-traffic scraping, **parameter / query-string injection (window-bound + owner-selector) and request replay**. | downstream |
| **IPLAN (L8)** | IPLAN-02 *(new)* | New tasks: metrics service, visit-timestamp migration, dashboard endpoint, retention job, integration tests. | downstream |
| **Code** | url-shortener source | Implement metrics service, persistence + retention job, and the role-restricted dashboard endpoint per SPEC-02/TDD-02/IPLAN-02. | downstream |

**Failure-mode delta (new runtime branches):** four new branches — visit-timestamp
store, retention/purge job, dashboard read endpoint, on-redirect timestamp write.
CHG-altitude deltas: (1) retention job failing to prune → unbounded storage growth
past 30 days; (2) the on-redirect write adding latency/failure to the hot path;
(3) dashboard query load.

**Async-capture failure analysis (branch 2 — hot-path-adjacent).** The async
buffer is itself a new bounded sink: (a) **overflow** — under sustained spikes
the bounded buffer fills; the contract is **drop-and-count-loss, never re-couple
to or block the redirect**, so it cannot become a second unbounded sink;
(b) **non-fatal contract** — a write failure or full buffer **MUST be non-fatal
to the redirect**: the redirect is served and `VisitCountRecord` still
increments; only the rolling-window timestamp is lost. Buffer bounds, drop-rate
thresholds, and drain mechanism defer to SPEC-02 / TDD-02 / IPLAN-02.

**Out-of-scope boundary (explicit):** cross-link aggregations, alerting, and
third-party analytics integrations are excluded — no affected layer above
carries a requirement for them.

## 4. Implementation

| # | Step | Artifact | Status |
|---|------|----------|--------|
| 1 | Update functional requirements + out-of-scope list | BRD-01 | Pending |
| 2 | Add dashboard capability + retention/latency NFRs | PRD-01 | Pending |
| 3 | Add visit-rate, dashboard-query + owner-identity requirements | EARS-01 | Pending |
| 4 | Add on-redirect-capture, dashboard-view + owner-identity scenarios | BDD-01 | Pending |
| 5 | Author ADR for metrics storage + owner-auth model | ADR-02 | Pending |
| 6 | Author SPEC for metrics service + dashboard API | SPEC-02 | Pending |
| 7 | Author TDD for metric/retention/authz tests | TDD-02 | Pending |
| 8 | Author IPLAN for metrics service + migration + dashboard | IPLAN-02 | Pending |
| 9 | Implement code per SPEC-02 / TDD-02 / IPLAN-02 | url-shortener source | Pending |

**Artifacts modified / created:**

| ID | File | Change type |
|----|------|-------------|
| BRD-01 | `docs/01_BRD/BRD-01.md` | modified |
| PRD-01 | `docs/02_PRD/PRD-01.md` | modified |
| EARS-01 | `docs/03_EARS/EARS-01.md` | modified |
| BDD-01 | `docs/04_BDD/BDD-01.md` | modified |
| ADR-01 | `docs/05_ADR/ADR-01.md` | boundary-impact (no edit) — anonymity/least-privilege delta owned by ADR-02 |
| ADR-02 | `docs/05_ADR/ADR-02.md` | created |
| SPEC-01 | `docs/06_SPEC/SPEC-01.md` | boundary-impact (no edit) — §3/§4 unmutated; timestamps on a separate additive path |
| SPEC-02 | `docs/06_SPEC/SPEC-02.md` | created |
| TDD-02 | `docs/07_TDD/TDD-02.md` | created |
| IPLAN-02 | `docs/08_IPLAN/IPLAN-02.md` | created |

### 4.1 Operational Readiness

CHG-altitude intent; thresholds and procedures delegate to the named downstream
artifact. **Each item below must be authored and linked before GATE-01 approval
is finalized** (§6 condition C1).

| Concern | Intent (CHG altitude) | Owning artifact |
|---------|------------------------|-----------------|
| **Runbook** | Runbook entries for the metrics service, dashboard endpoint, and 30-day retention job, authored and linked here — no existing runbook covers them. | IPLAN-02 |
| **Observability** | Telemetry to author: (1) health/error-rate for the metrics service, (2) latency/error-rate alert for the dashboard (vs PRD-01 p95), (3) lag/completion for the retention job, (4) an **error/drop-rate signal on the async on-redirect timestamp write** so a silent writer failure (stale/zero dashboards) alerts rather than passing unobserved. | SPEC-02 / IPLAN-02 |
| **Deployment posture** | Canary (or blue/green) rollout; the **abort decision is driven by the observability signals above** — metrics error-rate (1), dashboard p95/error-rate (2), async-write drop-rate (4); smoke checks gate promotion. The dashboard ships behind a feature flag whose **default state at deploy is OFF** (enabled after promotion), so rollback step 1 is an actionable disable, not a no-op. Rollout increment, bake time, and numeric thresholds set downstream. **A post-migration abort applies the §7.2 (irreversible) sequence.** | IPLAN-02 |
| **Cost / capacity** | Impact categories: visit-timestamp storage growth (visits/day × size × 30d, write-heavy on redirect), retention-job CPU/IO, dashboard read path, and whether a new time-series DB is required vs. reusing existing capacity. Sizing deferred. | IPLAN-02 |

## 5. Verification

| Check | Result | Method |
|-------|--------|--------|
| Every affected layer (BRD→Code) enumerated | Pass | Cascade trace vs the 8-layer chain + Code |
| New-ADR obligation recorded | Pass | Impact review vs change-request acceptance notes |
| Out-of-scope boundary recorded | Pass | `change_description.what` scope review |
| Existing-ADR/SPEC boundary-impact stated (ADR-01, SPEC-01) | Pass | §3 consistency review |
| New authz-boundary decision routed to an ADR owner | Pass | §2 + §3 ADR-02 scope |
| Rollback names a data-preservation mitigation | Pass | §7.2 mitigation review |
| Downstream artifacts updated + re-audited per layer | Pending | `doc-<layer>-audit` after GATE-01 |

## 6. Gate Approval (C3)

| Field | Value |
|-------|-------|
| Gate | **GATE-01** — business/product entry gate for upstream (BRD-originated) change |
| Approver | — *(pending human sign-off via `gate-check`)* |
| Approval Date | — |
| Conditions | C1–C4 below must hold (see list). |

**Approval conditions (verifiable):**

1. **C1 — collateral is an approval input.** The four §4.1 intents (runbook,
   observability, deployment, cost) are authored and linked **before** GATE-01
   sign-off, not deferred past it.
2. **C2 — no-ship before ADR-02.** No dashboard, owner-authz, or retained
   visit-timestamp surface ships until **ADR-02 is approved at its own ADR
   altitude**. GATE-01 (business gate) does **not** substitute for ADR-02's
   architectural approval — making explicit the bound previously only implied by
   §4.
3. **C3 — two-phase timing.** §4.1 collateral precedes GATE-01 (C1); the cascade
   (BRD→Code) is updated and **re-audited per layer after** GATE-01 grants the
   scope change (§5 final row). The two "GATE-01" references do not conflict —
   collateral precedes approval, re-audits follow it.
4. **C4 — post-implementation re-gate.** Each affected layer is re-validated via
   `doc-<layer>-audit` (§5 final row); the change closes only when that
   re-validation passes — the single formal re-gate path for this CHG.

> C3 requires a formal gate run — hand off to `../gate-check/SKILL.md` for
> GATE-01 and the `GATE_APPROVAL_FORM`.

## 7. Rollback Plan

**Strategy:** revert-commit. Rollback splits into a **fully reversible doc-only
phase** and an **irreversible state phase** — NOT symmetric, not one revert.

### 7.1 Pre-implementation revert (doc-only — fully reversible, RPO = 0)

1. Revert the BRD-01 / PRD-01 / EARS-01 / BDD-01 edits to the
   analytics-out-of-scope baseline.
2. Delete the created ADR-02 / SPEC-02 / TDD-02 / IPLAN-02 artifacts.
3. Remove the CHG-01 entry from `CHG-00_index.md` (or mark status: Rolled Back).

### 7.2 Post-implementation state rollback (irreversible without mitigation)

Once the storage migration has shipped, rollback is **not** an inverse step:
re-applying it restores the empty schema, **not** the accumulated data — so
reverting **permanently loses** all visit timestamps recorded since migration
unless the data-preservation mitigation runs first.

**Data-preservation obligation (required before any drop):** snapshot/export the
visit-timestamp table to cold storage before dropping it, **or** soft-disable
(stop writes + disable the dashboard) and retain it for an agreed window. The
down-migration script and snapshot mechanics are authored in IPLAN-02; **the CHG
records the obligation** that no drop occurs without a preceding snapshot or an
explicit accept-data-loss sign-off. **Default:** snapshot/export; the Release
Manager may substitute soft-disable + retain with sign-off in the deploy ticket.

**Abort-ordered sequence** (quiesce **both** reader and writer before removing
the store):

1. Disable the dashboard endpoint first (feature-flagged / separate deploy unit,
   disabled **independently** of the migration).
2. **Stop the on-redirect timestamp writer** — flip the capture flag off and
   confirm in-flight async-buffer writes have drained; the hot path falls back to
   count-only so the table is **quiescent** before snapshot. Without this step
   the writer fires through snapshot + drop, widening real RPO and dropping the
   store out from under a live write path.
3. Drain / confirm no in-flight dashboard queries against the store.
4. Run the data-preservation mitigation against the now-quiescent table.
5. Roll back the visit-timestamp storage migration.

**Abort note:** if any step fails, **halt and assess** — a partial rollback must
not leave the endpoint live against a half-migrated store.

**RTO / RPO posture:** pre-migration (§7.1) rollback is **RPO = 0**.
Post-migration, unmitigated rollback loses all visit timestamps since migration;
with the §7.2 mitigation, **RPO = last snapshot**, **RTO = snapshot + drop
duration**. "RPO = last snapshot" still **excludes timestamps
buffered-but-unflushed in the async layer** (lost on crash before step 2's drain)
— an acceptable-loss class (metric accuracy, not availability), called out so it
is not silently excluded. Exact numbers set in IPLAN-02.

## 8. Emergency Change

Not applicable — a planned C3 change, not a P0/P1 emergency. No
`emergency_change` block, post-mortem, or post-hoc gate required.

## Glossary

| Term | Definition |
|------|------------|
| CHG | Change Record — governance document for SDD artifact modifications |
| C3 | Major change — cross-layer, new requirements (formal gate) |
| GATE-01 | Business/product approval gate (L1–L2 entry, upstream changes) |

---

*End of CHG-01.*
