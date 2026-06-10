# BDD-01 Review Report — Iteration 3

**Artifact:** BDD-01 (url-shortener BDD suite)
**Layer:** 04_BDD
**Review iteration:** 3 (saga re-review after iter-2 fixer)
**Report date:** 2026-06-10

---

## Gate decision

| Field | Value |
|---|---|
| combined_status | **PASS** |
| structural_status | PASS |
| content_score | **91 / 100** |
| blocking_findings_count (P0 + P1) | 0 |
| coverage quorum met | yes (6 / 6 lenses ran) |

The deterministic gate passes: structural floor is PASS, no unresolved P0 or P1, and content_score 91 meets the ≥ 90 threshold. This is the first PASS verdict for BDD-01 across the saga.

---

## Score calculation

| Lens | Weight | Score (iter 3) | Contribution |
|---|---|---|---|
| qa_lead | 35 | 84 | 2940 |
| tech_lead | 25 | 88 | 2200 |
| chaos_engineer | 14 | 100 | 1400 |
| security_engineer | 6 | 100 | 600 |
| operator | 10 | 97 | 970 |
| auditor | 10 | 100 | 1000 |
| **Total** | **100** | — | **9110** |

content_score = round(9110 / 100) = **91**

No caps applied (0 × P0, 0 × P1).

### Movement vs iteration 2

| | Iter 2 | Iter 3 | Delta |
|---|---|---|---|
| combined_status | FAIL | PASS | +1 tier |
| content_score | 89 | 91 | +2 |
| blocking_findings_count | 0 | 0 | — |

The iter-2 fixer resolved both prior P2s (§4 traceability matrix, BDD.01.03.5645 split) and TL-BDD-01/TL-BDD-02 plus 8 P3s. The score crossed the 90 gate threshold. However the crash-recovery rewrite of BDD.01.03.9b90 and the pre-existing entropy scenario BDD.01.03.e5ec surfaced three new non-blocking P2 atomicity/timeout findings this iteration (MERGED-P2-9b90 compound When + missing timeout, QA-BDD-01-F007 compound And-step), which the qa_lead and tech_lead lenses score at 84 and 88 respectively, anchoring the content_score at 91 rather than higher.

---

## Executive summary

BDD-01 achieves its first PASS at iteration 3. The iter-2 fixer's most impactful work — restoring the §4 traceability matrix and atomically splitting BDD.01.03.5645 — eliminated all prior blocking P2s. The document now clears the gate.

Three new P2 findings emerge this iteration, all non-blocking and all traceable to the fixer's crash-recovery rewrite of BDD.01.03.9b90. That scenario now attracts two co-located C2 findings (compound When block from qa_lead; missing numeric timeout from tech_lead) that are merged into MERGED-P2-9b90 for co-resolution in a single edit pass. The entropy scenario BDD.01.03.e5ec has a compound And-step (QA-BDD-01-F007) that is the only isolated P2.

The two advisory operator findings (OP-I3-ADV-003, OP-I3-ADV-004) carry forward unchanged from iteration 2; both remain advisory with no upstream EARS obligation, and no action is required before downstream progression.

The chaos_engineer, security_engineer, and auditor lenses score 100 with zero findings — confirming that fault-partition breadth, security assertions, and structural compliance are sound at this iteration.

---

## Coverage

| Metric | Value |
|---|---|
| Lenses expected | 6 |
| Lenses ran | 6 |
| Quorum required | ≥ 3 |
| Quorum met | yes |
| Low-confidence flag | no |

No low-confidence flag. All six crew lenses returned non-failed persona-output records.

---

## Content findings

### P2 — Non-blocking (resolve before next fixer pass recommended)

#### MERGED-P2-9b90 — Compound When + missing timeout on BDD.01.03.9b90

- **Check:** C2
- **Location:** §3.1 — BDD.01.03.9b90
- **Personas:** qa_lead, tech_lead (co-owned; requires co-resolution in one edit)
- **Message:** Two distinct C2 violations co-located in BDD.01.03.9b90. (1) The When block carries two distinct system-level triggers ('When the API acknowledges' and 'And the Mapping Store is hard-killed'), violating one-action-per-When atomicity. (2) The Then 'after the Mapping Store restarts the issued short code SHALL still resolve' declares an async wait with no numeric timeout or polling ceiling, leaving step-definition authors unable to bound the assertion duration.
- **Recommendation:** Restructure in one pass: elevate the API acknowledgement and hard-kill to Given preconditions, leaving a single explicit When trigger (the restart), and attach a named threshold key to the post-restart resolution wait (e.g., @threshold referencing the RTO from EARS.01.04.5e5b or PRD.01.perf.redirectp95). The fixer should dispatch both qa_lead and tech_lead for patch validation.

#### QA-BDD-01-F007 — Compound And-step on BDD.01.03.e5ec

- **Check:** C2
- **Location:** §3.1 — BDD.01.03.e5ec
- **Persona:** qa_lead
- **Message:** A single And-step bundles two independently falsifiable assertions: pairwise distinctness (uniqueness / collision property) and monobit frequency (statistical entropy property). A test failure cannot be attributed to one property without splitting the step.
- **Recommendation:** Split into two step lines — one for pairwise distinctness, one for the monobit frequency test — so each maps to one independently reportable assertion.

### P3 — Advisory / improvement (no gate impact)

#### QA-BDD-01-F003 — Dual-plane Then on BDD.01.03.3c70

- **Check:** beyond-checklist:test-isolation
- **Location:** §3.2 — BDD.01.03.3c70
- **Persona:** qa_lead
- **Recommendation:** Extract the 'link_takedown_applied' event assertion into a separate scenario, or accept the co-location with an explicit '@dual-plane-accepted' tag and decision reference.

#### QA-BDD-01-F004 — Repeated Given step across four scenarios

- **Check:** C4
- **Location:** §3.1 BDD.01.03.613b, §3.3 BDD.01.03.1f90 / .44fe / .076f
- **Persona:** qa_lead
- **Recommendation:** Extract to a parameterized step-definition catalog entry or Background block, or document the deferral explicitly.

#### QA-BDD-01-F005 — Repeated screening Given across three scenarios

- **Check:** C4
- **Location:** §3.3 BDD.01.03.41c7, §3.2 BDD.01.03.f0a5, §3.5 BDD.01.03.3708
- **Persona:** qa_lead
- **Recommendation:** Register as a named step or Background entry; document deferral alongside QA-BDD-01-F004 if deferred.

#### OP-I3-ADV-003 — No SLO-breach + alert-fire scenario (advisory)

- **Check:** C5
- **Location:** §3 overall
- **Persona:** operator
- **Status:** Carried from OP-I2-ADV-003; no upstream EARS obligation; no action required until EARS is revised.

#### OP-I3-ADV-004 — No runtime gate-toggle scenario (advisory)

- **Check:** C2
- **Location:** §3.5 — BDD.01.03.3708
- **Persona:** operator
- **Status:** Carried from OP-I2-ADV-004; no upstream EARS obligation; no action required until EARS is revised.

---

## Playbook coverage

| Check | Surviving findings |
|---|---|
| C2 | 4 |
| C4 | 2 |
| C5 | 1 |
| beyond_checklist | 1 |

beyond_checklist share: 1 / 8 = 12.5% — below the 30% drift-signal threshold. No playbook revision indicated.

---

## Discarded findings

None. All 7 surviving findings carry valid check citations (C2, C4, C5, or beyond-checklist:test-isolation). 0 findings were discarded by the citation gate.

---

## Contested findings

None. No lens disagreed on fix direction. MERGED-P2-9b90 consolidates two lenses on the same location under a unified recommendation; both lenses agree the fix is a single restructure pass.

---

## Recommended next step

BDD-01 **passes the gate**; progression to the ADR layer (05_ADR) is unblocked.

Before or during ADR authoring, a single follow-up fixer pass is recommended to address the two P2 findings:

1. **MERGED-P2-9b90** — restructure BDD.01.03.9b90 (compound When → Given preconditions; add named threshold on Then). Both qa_lead and tech_lead must validate the patch.
2. **QA-BDD-01-F007** — split BDD.01.03.e5ec compound And-step into two lines.

These are non-blocking for gate purposes but will accumulate if left unaddressed before TDD review.

The P3 step-catalog findings (QA-BDD-01-F004, QA-BDD-01-F005) may be deferred to a step-definition authoring pass at the Code/TDD layer, provided the deferral is documented in §3. The two advisory operator findings (OP-I3-ADV-003, OP-I3-ADV-004) require no action until upstream EARS adds corresponding obligations.
