# TDD-01 Review Report — Iteration 2

**Artifact:** TDD-01 (SDD Layer 7 — Link Store)
**Iteration:** 2
**Date:** 2026-06-10
**Synthesizer:** Chairperson reduce over 6 lens slots

---

## Executive Summary

Combined status: **FAIL** — borderline, 1 point below threshold.

The artifact passes all deterministic structural checks (lint floor, 30
conformant IDs, metadata valid) and carries zero blocking findings (no P0,
no P1). The content score is **89/100** against a gate threshold of 90.
All 6 lenses returned results; quorum is met. The FAIL is score-only: the
residual 6 P2 findings (each a fresh, fine-grained gap surfaced after the
iteration-1 clusters cleared) collectively suppress the weighted average by
1 point. There are no contested (either/or) items across the crew — all
findings are additive to distinct locations.

No findings were discarded by the check-citation filter. Beyond-checklist
drift is 0%.

---

## Gate Decision

| Dimension | Result |
|---|---|
| Combined status | **FAIL** |
| Structural floor | PASS |
| Blocking findings (P0 + P1) | 0 |
| Content score | 89 / 100 |
| Gate threshold | 90 |
| Score cap applied | No (no unresolved P0 or P1) |
| Quorum | Met (6/6 lenses returned) |

The gate is deterministic: structural PASS + no blocking + content score >=
threshold = PASS. Here content score 89 < 90; combined_status = FAIL.

---

## Coverage

| Lens | Score | Findings |
|---|---|---|
| qa_lead | 84 | 2 (QL-001, QL-002) |
| tech_lead | 100 | 0 — clean |
| chaos_engineer | 88 | 1 (CHAOS-001) |
| security_engineer | 86 | 1 (SE-001) |
| operator | 90 | 3 (OP-001, OP-002, OP-003) |
| auditor | 85 | 1 (AUD-001) |

Weighted average: (84×35 + 100×25 + 88×10 + 86×10 + 90×10 + 85×10) / 100 = 89.3
→ content_score 89 (integer floor).

Lenses requested: 6. Lenses returned: 6. Quorum threshold: ceil(6 × 0.5) = 3.
Quorum met: yes. Confidence: full.

---

## Findings — P2 (6 findings, non-blocking)

### QL-001 | P2 | C2 | qa_lead

**Location:** §4 Integration — TDD.01.04.af07

Case TDD.01.04.af07 bundles two structurally distinct AAA flows under one
case ID: a success-path assertion (healthy KV adapter, RPO=0) and a
failure-path assertion (faulting KV adapter, StoreUnavailableError, no orphan).
These two flows cannot share a single Arrange block. A third concern is
embedded (observability metric + trace span). Combining two fixture states
under one case ID makes a failure non-diagnosable at the case-ID level.

**Recommendation:** Split TDD.01.04.af07 into two cases: (a) success-path
(healthy adapter, RPO=0, metric + span); (b) failure-path (faulting adapter,
StoreUnavailableError, no orphan). Update §3 Test Mapping to list both new
case IDs against @bdd: BDD.01.03.8b97.

---

### QL-002 | P2 | C3 | qa_lead

**Location:** §4 Integration — TDD.01.04.24ff

Case TDD.01.04.24ff asserts a 200 ms KMS key-unwrap sub-budget threshold but
no upstream source (EARS, PRD, or SPEC) is cited for this specific value.
SPEC §6 anchors the claim operation to EARS.01.03.f909 but does not decompose
that budget into a KMS-unwrap allocation. The 200 ms figure is unanchored and
untraceable.

**Recommendation:** Either cite the upstream source for the 200 ms sub-budget
(annotate as author assumption if so), or express the threshold in terms of
the traceable budget and defer the concrete ms ceiling to IPLAN, consistent
with the cipher-mode and KMS key-ARN IPLAN-defer pattern already established
in the same case.

---

### CHAOS-001 | P2 | C1 | chaos_engineer

**Location:** TDD §3 row @bdd: BDD.01.03.f44a; case TDD.01.04.7115

The get-path degradation scenario is encoded detection-only. Case 7115 asserts
StoreUnavailableError is raised within 1 s, but no case asserts recovery after
the read path is restored. SPEC-01 §5 requires both failure detection AND
'recovers when the store returns'. Detection-only encoding permits a
permanently-failing read state (stuck circuit breaker, cached unavailability)
to pass the suite silently.

**Recommendation:** Add a paired recovery case: inject read-path fault, assert
detection (as 7115), clear fault via controllable adapter/toxiproxy, assert
get resolves the known record within p95 budget. Mirrors the ec06/4e51
detection+recovery pairs already present for the write paths.

---

### SE-001 | P2 | C2 | security_engineer

**Location:** §4 Unit/Integration; cases cf05/54b8/1bc0 (get), 74e8/9528/ab25 (increment_visits)

Input-fuzzing covers claim (8504) and set_status (fc47) but two public
Protocol boundary inputs remain unfuzzed. (1) get(code): exercised only on
known/unknown/taken_down classes — no encoding-edge/homoglyph fuzz, which is
the key-confusion surface at the trust boundary. (2) increment_visits(code,
delta): no fuzz on delta (negative/zero/overflow can silently break SPEC §4
monotonic visit_count contract) or code (encoding-edge classes).

**Recommendation:** Add a get-fuzz unit case and an increment_visits-fuzz unit
case in tests/unit/test_link_store.py, mirroring the 8504/fc47 input matrix.

---

### OP-001 | P2 | C2 | operator

**Location:** §4 row @adr: ADR.01.03.f5f5; ADR-01 §7 Rollback plan

The forward deploy path is gated (TDD.01.04.d5d7, smoke, ≤30s). However, no
test exercises the rollback procedure in a non-prod environment. ADR §7 step 7
requires an automated RPO=0 smoke after substrate re-point; TDD.01.04.d5d7
cannot serve this role (it commits a fresh code on the live substrate; it has
no pre-imported records to verify). The post-rollback verification gate is an
untested manual step.

**Recommendation:** Add a non-prod rollback-path integration smoke test
(type: smoke, timeout ≤120s) exercising ADR §7 steps 3/5/7: export known
committed records, import into secondary KV with uniqueness-verification
assertions, then run an RPO=0 probe against the secondary instance. Tag
@adr: ADR.01.03.f5f5 and add to §5 smoke gate row alongside TDD.01.04.d5d7.

---

### AUD-001 | P2 | C4 | auditor

**Location:** §1 line 30 (cumulative upstream tags header) vs §3 lines 89-90 and §7 line 206

Cumulative upstream tags header lists @adr: ADR-01 only. The body cites six
ADR element refs: ADR.01.03.5c3c, ADR.01.03.1050, ADR.01.03.f5f5,
ADR.01.05.3afa, ADR.01.05.9107, plus the document-level ADR-01. The cumulative
header is the artifact's traceability contract and must enumerate every upstream
element tag cited in the body.

**Recommendation:** Update line 30 to: @adr: ADR-01 | @adr: ADR.01.03.5c3c |
@adr: ADR.01.03.1050 | @adr: ADR.01.03.f5f5 | @adr: ADR.01.05.3afa |
@adr: ADR.01.05.9107. Verify each tag resolves in the upstream ADR doc.

---

## Findings — P3 (2 findings, advisory)

### OP-002 | P3 | C1 | operator

**Location:** §4 integration cases TDD.01.04.af07, TDD.01.04.840c; SPEC-01 §6

SPEC §6 names 'atomic-claim outcome' as a distinct emission point. 840c verifies
the write-conflict counter on a race but does not assert a per-outcome labelled
metric ({outcome=COMMITTED} / {outcome=CODE_TAKEN}). Missing outcome labels
make the COMMITTED/CODE_TAKEN distribution dark in production.

**Recommendation:** Extend af07 to assert outcome=COMMITTED label on successful
claim; add companion assertion in 82ff or 840c for outcome=CODE_TAKEN. Cite
@spec: SPEC-01 §6 on both.

---

### OP-003 | P3 | C5 | operator

**Location:** §4 all classes; §5 Thresholds

Functional fault-injection cases cover application-adapter fault modes. The
pre-test-setup CI failure mode is uncovered: KV substrate unreachable before
any test runs (harness may silently skip/error), or KMS credential-fetch timeout
during CI bootstrap (produces a false CI timeout rather than a classified test
failure). TDD.01.04.24ff covers KMS slowness during an operation; the
setup-phase mode is distinct and unaddressed.

**Recommendation:** Add a CI pre-condition probe in integration and e2e CI job
configs asserting KV reachability and vault/KMS credential validity before the
test runner starts. Probe failure exits non-zero with structured error
distinguishing 'infrastructure unavailable' from 'test failure'. Document in
§5 or CI appendix for correct flake-budget classification.

---

## Playbook Coverage

| Check | Findings |
|---|---|
| C1 | 2 (CHAOS-001, OP-002) |
| C2 | 3 (QL-001, SE-001, OP-001) |
| C3 | 1 (QL-002) |
| C4 | 1 (AUD-001) |
| C5 | 1 (OP-003) |
| beyond_checklist | 0 |
| discarded | 0 |

Beyond-checklist ratio: 0/8 = 0%. No playbook drift.

All findings cite a valid playbook check (C1–C5). Zero findings were
discarded by the check-citation filter. No unknown check IDs were cited.

---

## Convergence Note

Iteration 1 scored 84/100 with 7 or more P2 clusters across the crew.
Iteration 2 scores 89/100 with 6 P2 + 2 P3 findings, a net improvement
of +5 points. The residual P2s are fresh, fine-grained findings surfaced
once the iteration-1 clusters cleared: the qa_lead's multi-fixture bundling
in af07 and the unanchored 200 ms threshold in 24ff; the chaos_engineer's
detection-only recovery gap in 7115; the security_engineer's two unfuzzed
public inputs (get, increment_visits); the operator's rollback-path smoke
gap; and the auditor's incomplete cumulative traceability header. None of
these were present or obscured in iteration 1; they represent genuine
new-resolution findings from a cleaner artifact, not regressions.

The suite is converging. A single fixer pass targeting all 6 P2s should
lift the score through the 90-point gate. The 2 P3s are advisory and do
not gate passage, though addressing OP-002 (outcome labels) closes a
production SLO visibility gap that is low-cost to add alongside OP-001's
af07 modifications.

---

*Synthesized by Synthesizer (Chairperson). Artifact not edited. Per-persona slots are transient.*
