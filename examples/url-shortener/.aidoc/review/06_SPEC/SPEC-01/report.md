# SPEC-01 Review Report — Iteration 2

**Artifact:** SPEC-01 (URL Shortener Technical Specification v1.0.1)
**Layer:** 06_SPEC
**Review cycle:** Iteration 2 (re-audit after doc-spec-fixer pass)
**Date:** 2026-06-09

---

## Executive Summary

All five iteration-1 blocking and high-priority findings have been independently verified as resolved in SPEC-01 v1.0.1. The fixer correctly addressed every P0/P1/P2 item raised by the iteration-1 crew. The artifact passes the deterministic gate: structural floor holds, no unresolved P0 or P1, and the weighted content score (97) clears the 90-point threshold. Four residual P3 advisory findings survive — none blocking, all deferred to TDD or IPLAN for concrete value binding.

---

## Summary Table

| Field | Value |
|---|---|
| combined_status | **PASS** |
| content_score | **97** |
| structural_status | **PASS** |
| personas requested | 5 |
| personas returned | 5 |
| quorum_met | true |
| blocking findings (P0+P1) | **0** |
| advisory findings (P2+P3) | **4** (all P3) |

---

## Score Calculation

| Lens | Weight | Score | Contribution |
|---|---|---|---|
| architect | 30 | 100 | 30.0 |
| tech_lead | 30 | 95 | 28.5 |
| integration_lead | 20 | 96 | 19.2 |
| chaos_engineer | 10 | 93 | 9.3 |
| security_engineer | 10 | 100 | 10.0 |
| **Weighted blend** | **100** | — | **97.0** |

Cap applied: **none** (no unresolved P0 or P1).
content_score: **97** (rounded from 97.0).

---

## Coverage

All 5 expected lenses returned valid persona-output records. Quorum met (5/5 ≥ ceil(5 × 0.5) = 3).

| Lens | Status | Score |
|---|---|---|
| architect | ran | 100 |
| tech_lead | ran | 95 |
| integration_lead | ran | 96 |
| chaos_engineer | ran | 93 |
| security_engineer | ran | 100 |

---

## Iteration-1 Finding Resolution

The following findings from iteration 1 were independently re-verified as resolved by the crew in this pass:

| Iteration-1 ID | Priority | Resolved by | Verification |
|---|---|---|---|
| INT-001 | P1 | fixer | §3 boundary table now states per-edge timeout/retry/circuit-break |
| INT-002 | P1 | fixer | §4 names backward-compatible-within-MAJOR LinkStatus evolution policy with migration-on-break |
| INT-003 | P1 | fixer | §2/§3 stamp LinkStore contract v1 + substrate contract v1 tracking SPEC MAJOR |
| INT-004 | P2 | fixer | §2 declares KV minimum-capability matrix with non-conformance rule |
| INT-005 | P2 | fixer | §6 attributes per-boundary emitters and cross-edge span propagation |
| TL-003 | P1 | fixer | §2 declares ownership of reconciliation log |
| CHAOS-004 | P2 | fixer | §6 characterizes overflow policy: drop-oldest with reconciliation_overflow alert, post-fault drain rate-bounded |

No contested findings. No iteration-1 findings carried forward at P0/P1/P2.

---

## Findings — Iteration 2

### P3 Advisory Findings (non-blocking, deferred to TDD/IPLAN)

#### TL-005

- **Check:** C5
- **Priority:** P3
- **Lens:** tech_lead
- **Location:** §4 Data Models / §5 Error handling (reconciliation row, delta_id)
- **Message:** The reconciliation-log entry is declared an owned persistent resource (§2 'owns the reconciliation log') and §5 states each replayed delta 'carries a unique delta_id (commit marker)' so replay can skip an already-reflected delta. That entry shape is not modeled in §4: neither delta_id nor the reconciliation-entry record (short_code, delta, delta_id, ts) appears as a typed contract alongside LinkRecord/ClaimResult. The owned off-path resource therefore has its ownership declared (resolving prior TL-003) but its schema undeclared at the spec layer, leaving the no-double-count replay mechanism un-typed for TDD/IPLAN.
- **Recommendation:** Add a minimal typed contract for the reconciliation-log entry in §4 (e.g. ReconciliationEntry: short_code: str, delta: int, delta_id: str, ts_utc: datetime) so the owned resource and its delta_id commit-marker have a declared shape, consistent with the other §4 data models.

#### INT-006

- **Check:** C3
- **Priority:** P3
- **Lens:** integration_lead
- **Location:** §3 claim / §4 LinkRecord.idempotency_key / §6 Patterns
- **Message:** The idempotency_key crosses the API -> Link Store boundary and drives the replay-collapse dedup contract, but the spec does not declare the key's uniqueness scope or a replay-match retention window. With the content-derived fallback (ADR.01.03.3315), two distinct submissions hashing to the same candidate could collapse onto one record, and a same-key retry is honored as replay over an unbounded horizon by spec. The replay guarantee across the boundary is thus time- and scope-unbounded.
- **Recommendation:** State the idempotency_key uniqueness scope (per-submitter vs global) and the replay-match retention window (key honored for replay within N; beyond it a same-key submission is treated as a fresh claim), plus the content-derived fallback's collision domain. Bind concrete values at TDD against the EARS.01.03.f909 issuance budget.

#### CHAOS-002-R1

- **Check:** C2
- **Priority:** P3
- **Lens:** chaos_engineer
- **Location:** §6 Resilience envelope (reconciliation log bound)
- **Message:** The reconciliation-log overflow policy is now characterized (CHAOS-004 resolved: 'at the bound oldest deltas drop with a reconciliation_overflow alert; post-fault drain rate-bounded'), but the bound itself is qualitative -- '(max retention)' with no ceiling magnitude (no entry count, byte ceiling, or time window). The drop-oldest behavior and alert are specified; what is missing is a concrete bound magnitude. A TDD fixture cannot drive the log to its bound and observe the drop + alert without knowing what the bound is. This is a testability gap, not an uncharacterized-resilience gap, hence P3.
- **Recommendation:** Quantify the reconciliation-log bound as a concrete ceiling (e.g. max N entries OR max retention window OR max bytes) so the overflow/drop-oldest path is constructable as a TDD fixture. Pin the magnitude to the design-load increment-fault rate x worst-case outage duration the §6 envelope assumes, or mark it a TDD-owned threshold with a named source.

#### CHAOS-002-R2

- **Check:** C4
- **Priority:** P3
- **Lens:** chaos_engineer
- **Location:** §3 Boundary failure semantics / §6 Resilience envelope (circuit-break)
- **Message:** Circuit-break OPEN semantics are defined on both synchronous boundaries (§3: 'open after a bounded failure count => fail closed'; 'open => fail-safe not-found'), and the contract asserts recovery ('recovers when the store returns', §5 error table). But the breaker RECLOSE / half-open reset semantics are implicit: no half-open probe interval, reset window, or success-count-to-close is stated. With no reclose mechanism specified, the time from substrate-recovered to breaker-closed is unbounded by the SPEC. Recovery is asserted at the outcome level but the mechanism that bounds it is missing.
- **Recommendation:** Specify the circuit-break reset contract: the half-open probe cadence (or cool-down window) and the success condition that recloses the breaker, so the post-fault readmission time is bounded and the reclose path is testable. Bind concrete values at TDD against a named recovery budget.

---

## Playbook Coverage

| Check | Findings |
|---|---|
| C1 | 0 |
| C2 | 1 |
| C3 | 1 |
| C4 | 1 |
| C5 | 1 |
| beyond_checklist | 0 |

beyond_checklist / total = 0/4 = 0.0 — within calibration norm (threshold 0.30).

---

## Contested Findings

None. All lenses reached independent conclusions with no either/or disagreement on any finding.

---

## Deterministic Gate Decision

```
structural_status = PASS   (sdd_doc_lint exit 0; all 8 required sections present)
blocking_findings = 0      (no P0, no P1)
content_score     = 97     (weighted blend 97.0, no cap)
gate_threshold    = 90

combined_status = PASS
```

The artifact is cleared for progression to Layer 7 (TDD). The four P3 advisories are non-blocking deferred items; the TDD author should address the concrete bound values for reconciliation-log ceiling, circuit-breaker reclose, idempotency-key retention window, and ReconciliationEntry schema as part of TDD fixture design.
