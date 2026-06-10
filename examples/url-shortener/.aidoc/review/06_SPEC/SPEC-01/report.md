# SPEC-01 Review — Iteration 3 Unified Report

**Artifact:** SPEC-01 (Mapping Store component spec)
**Iteration:** 3 (re-review after iteration-2 fixer)
**Date:** 2026-06-10

---

## Executive Summary

SPEC-01 passes the iteration-3 gate. Combined status: **PASS**. Content score: **97 / 100** (threshold 90). Structural status: **PASS**. All 5 requested personas returned slots (quorum met). Blocking findings (P0 + P1): **0**. The five remaining findings are all P3 (advisory); none block release.

All five lenses confirmed that the iteration-2 fixer changes resolved the prior P2 findings — no P2 issues carry forward into this iteration.

---

## Gate Decision

| Dimension | Result |
|---|---|
| Combined status | **PASS** |
| Content score | **97** (threshold 90) |
| Structural status | **PASS** |
| Blocking findings (P0 + P1) | **0** |
| Coverage quorum | **met (5 / 5)** |

---

## Per-Lens Score Table

| Lens | Weight | Score | Weighted contribution |
|---|---|---|---|
| architect | 30% | 96 | 28.80 |
| tech_lead | 30% | 100 | 30.00 |
| integration_lead | 20% | 100 | 20.00 |
| chaos_engineer | 10% | 93 | 9.30 |
| security_engineer | 10% | 93 | 9.30 |
| **Weighted total** | | | **97.40 → 97** |

---

## Coverage

- Personas requested: 5
- Personas returned: 5
- Quorum met: yes
- Missing slots: none
- Confidence: full

---

## Reduced Findings

### P3 — Advisory (5 findings; no gate impact)

**ARCH-001** (architect) — check C5
Location: Section 8 Upstream ADR tag line; Section 5 degraded→recovered state transition; Section 7 recovery contract.
Message: The RTO-bounded recovery behavior in Sections 5 and 7 traces to ADR-01 consequence ADR.01.05.cb92 (PITR + standby promotion, RTO ≤ 30 min), but that consequence is absent from the Section 8 Upstream ADR tag line. The sibling consequences (.47a1, .454a, .5896, .7dde, .2740) are all cited; only the recovery consequence is missing. No behavioral contradiction exists — the linkage gap is traceability-only.
Recommendation: Add @adr: ADR.01.05.cb92 to the Section 8 Upstream ADR list.

---

**CHAO-001** (chaos_engineer) — check C4
Location: Section 3 increment_visit delivery contract / Section 6 dead-letter recovery.
Message: Dead-letter reconciliation is operator-driven with no stated MTTR or RTO. The count-staleness window governs when an event routes to dead-letter and triggers an alert; it does not bound when a dead-lettered event is actually replayed. The RTO ≤ 30 min applies to store-loss recovery only. A backlog of dead-lettered count events can remain unreconciled indefinitely while all stated bounds are met.
Recommendation: State a reconciliation MTTR target or escalation window for the dead-letter replay path, and make that target testable at TDD-01 alongside the store-loss RTO probe.

---

**CHAO-002** (chaos_engineer) — check beyond-checklist:backpressure-policy-undefined
Location: Section 3 delivery channel (Visit-Counter-owned durable queue) / Section 6 read/create design-load.
Message: The durable async queue carrying increment_visit off the redirect path has no stated beyond-margin behavior. When the reconciler lags the producer sustainably, queue depth grows without bound or shed/backpressure policy. SPEC-01 binds the at-least-once delivery contract to this transport, so its saturation policy is in scope to reference, even though the queue is owned by the Visit Counter component.
Recommendation: Reference the queue's beyond-margin policy (max depth / age bound, and the behavior at that bound: shed-with-alert, block producer, or age-out to dead-letter). If the policy is fully specified in the Visit Counter component spec, cite that owner explicitly for traceability.

---

**SECU-003** (security_engineer) — check C3
Location: Section 5 validation rules / read_original_url.
Message: The ShortCode charset/length allowlist precondition covers resolve and mark_taken_down but not read_original_url. read_original_url accepts an attacker-influenceable ShortCode and is guarded only by the parameterized PK lookup. The SPEC's stated defense-in-depth parity principle applies to all classified-read interfaces; read_original_url is the highest-sensitivity read and currently has weaker boundary validation than the unprivileged resolve.
Recommendation: Extend the Section 5 ShortCode allowlist rule to name read_original_url alongside resolve and mark_taken_down.

---

**SECU-004** (security_engineer) — check C3
Location: Section 5 validation rules / increment_visit event_id.
Message: increment_visit accepts an EventId (the dedup/idempotency key) with no stated format or length constraint at the store boundary. An unbounded or malformed EventId is attacker-influenceable and could bloat the dedup index or attempt collisions against the idempotency gate. Risk is bounded by the off-path, idempotent consumer, but no typed-parse or length rule is specified.
Recommendation: Add a Section 5 validation rule constraining increment_visit's EventId to a typed-parsed, bounded-length format, paralleling the put_mapping OriginalUrl and resolve ShortCode allowlist rules.

---

## Contested Findings

None. All lenses converged; no either/or judgment surfaced.

---

## Iteration-2 Fixer Verification

All five lenses (architect, tech_lead, integration_lead, chaos_engineer, security_engineer) confirmed that the iteration-2 fixer changes fully resolved the prior P2 findings; no P2 issues carry forward.

---

## Playbook Coverage

| Check | Surviving findings |
|---|---|
| C3 | 2 |
| C4 | 1 |
| C5 | 1 |
| beyond-checklist | 1 |

Beyond-checklist ratio: 1 / 5 = 20% (below the 30% drift-signal threshold — no playbook revision signal).

---

## Discarded Findings

None. All findings carried valid playbook check citations (C3, C4, C5, or beyond-checklist form); zero findings were discarded.
