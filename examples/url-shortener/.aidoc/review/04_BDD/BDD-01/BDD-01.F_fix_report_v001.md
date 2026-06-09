# BDD-01.F Fix Report — v001

**Artifact:** BDD-01 (`docs/04_BDD/BDD-01.md`)
**Layer:** 04_BDD
**Fixer:** doc-bdd-fixer (team mode; deterministic P2/P3 pass — 0 blocking findings)
**Input audit:** BDD-01 review report (content score 81, GATE FAIL), `report.md` + `verdict.json`
**Iteration:** 1
**Report date:** 2026-06-08
**Version transition:** BDD-01 v1.0.0 → v1.0.1

---

## Summary

| Metric | Value |
|--------|-------|
| Findings in | 25 (0 P0, 0 P1, 12 P2, 13 P3) |
| Findings fixed | 22 (12 P2 + 10 P3) |
| Findings deferred (manual queue) | 3 (P3 — require upstream EARS or step-def layer) |
| Files created | 0 |
| Files modified | 1 (`docs/04_BDD/BDD-01.md`) |
| Scenarios before → after | 32 → 35 (3 recovery scenarios extracted) |
| Structural lint | PASS → PASS (0 errors) |

There were **no blocking (P0/P1) findings**, so no per-lens patch-validation
loop ran (team mode validates only blocking findings). The gate FAILed purely
on content score (81 < 90). All 12 P2 findings and 10 of 13 P3 findings were
applied deterministically. The three deferred P3s would create
upstream-untraced (orphan) scenarios or belong to the step-definition layer —
they are routed to the manual-review queue rather than fabricated here.

---

## Fixes Applied

| Finding | Location | Fix | Confidence |
|---------|----------|-----|------------|
| qa_lead-P2-001 | §3.1 / 40d7 | Split Given precondition (role) from action; moved request to `When`, grant to `Then`, audit record to `And`. | auto-safe |
| qa_lead-P2-002 | §3.2 / 842c | Split compound `Then` "deny … and return no counts" into `Then` (deny) + `And` (no counts). | auto-safe |
| qa_lead-P2-003 | §3.1 / b9e7 | Split the `while`-joined latency/availability assertion into two steps (see also tech_lead-P2-001). | auto-safe |
| qa_lead-P2-004 | §3.3 / f44a, ed21, 1a55 | Extracted each embedded `And when <restored> …` recovery trigger into its own discrete `Scenario` (new IDs 0759, bcfb, dd27) with own Given/When/Then. | auto-assisted |
| tech_lead-P2-001 | §3.1 / b9e7, §3.3 / 1a55 | Replaced the non-implementable monthly-availability pass/fail assertion inside the bounded window with a within-window success-rate observable (≥99.9% over sampled requests, no non-shed 5xx); monthly SLO noted as a separate long-horizon target. | auto-assisted |
| tech_lead-P2-002 | §3.3 / bdae | Documented the determinism seam in the `Given`: a code generator seeded to emit candidate "abc123" for both submissions, forcing the race reproducibly. | auto-assisted |
| tech_lead-P2-003 | §3.5 / fa47 | Bound the abstract high-utilization threshold to a configurable fixture value (configured 80%, utilization at 79% → crosses to 80%); flagged as author assumption pending PRD §13. | auto-assisted |
| tech_lead-P2-004 | §3.5 / fa47 | Added a numeric emission ceiling (`WITHIN the EARS.01.03.00b9 alert-emission budget (5 s) of the crossing`); flagged as author assumption. | auto-assisted |
| chaos_engineer-P2-001 | §3.3 / 5f58 | Added a `connection refused` partition row to the visit-count store fault table (true partition variant alongside the slow variant). | auto-safe |
| auditor-P2-001 | §3.3 / f44a | Replaced bare `within 1 second` with `WITHIN the EARS.01.03.fab2 store-unavailable budget (1 s)`. | auto-safe |
| auditor-P2-002 | §3.3 / a7ad | Replaced bare `60 s` with a named reconciliation budget (60 s); flagged as author assumption backing EARS.01.03.19ec. | auto-assisted |
| auditor-P2-003 | §3.3 / 1a55 | Replaced bare `within 1 second` with `WITHIN the EARS.01.03.fab2 store-unavailable budget (1 s)`. | auto-safe |
| security_engineer-P3-001 | §3.4 / e8b9 | Added an injection-class Examples row (percent-encoded script / NUL / SQL payload), exercising the existing no-disclosure clause. | auto-assisted |
| security_engineer-P3-002 | §3.2 / 842c | Added an `And` asserting the denial body contains only the contracted response and discloses no server-side error/stack trace/dependency diagnostic. | auto-safe |
| qa_lead-P3-001 | §3.4 / 5599 | Removed the unused (unreferenced) `class` Examples column; moved labels to an inline non-parameterizing comment. | auto-safe |
| tech_lead-P3-001 | §3.1 / 5887 | Added an `And` naming the ordering observable (reputation double records the call; no code committed before a "clean" verdict — call-order verification). | auto-assisted |
| chaos_engineer-P3-001 | §3.3 / f44a, ed21, 4df6, 5f58 | Broadened every integration fault table with `dns resolution failure` and `tls handshake failure` partition fixtures (distinct code paths from a refused TCP connection). | auto-safe |
| operator-P3-001 | §3.1 / cbf4 | Added an `And` asserting a takedown-applied log at AUDIT severity (short code, operator identity, timestamp). | auto-assisted |
| operator-P3-002 | §3.2 / 8604 | Added an `And` asserting an INFO log with reason `taken_down`, distinguishing it from an organic unknown-code lookup. | auto-assisted |
| operator-P3-003 | §3.2 / 6f00 | Added an `And` asserting a pool-exhausted WARN log (metric `shortcode_pool_exhaustion_total`) per rejection. | auto-assisted |
| operator-P3-004 | §3.3 / 1a55 | Added an `And` asserting a WARN load-shed log per shed request, reason `connection_pool_saturated` (metric `redirect_shed_total`). | auto-assisted |
| operator-P3-006 | §3.5 / fa47 | Extended the alert `Then` to carry current utilization %, the threshold value, and a timestamp, delivered to the Service-Owner operations channel. | auto-assisted |

### New scenarios (qa_lead-P2-004 extractions)

| ID | Type | Title | Inherited upstream tags |
|----|------|-------|--------------------------|
| BDD.01.03.0759 | recovery | Redirect recovers after the Link Store is restored | @ears:EARS.01.03.fab2 @prd:PRD.01.09.ce85 @brd:BRD.01.07.15e1 |
| BDD.01.03.bcfb | recovery | Issuance recovers idempotently after the Link Store write path is restored | @ears:EARS.01.03.8df7 @ears:EARS.01.04.93f7 @prd:PRD.01.13.ebf9 @brd:BRD.01.10.3407 |
| BDD.01.03.dd27 | recovery | Redirect path resumes normal latency after connection-pool pressure clears | @ears:EARS.01.03.a132 @ears:EARS.01.03.fab2 @ears:EARS.01.04.ca05 @prd:PRD.01.09.ce85 @brd:BRD.01.07.15e1 |

Each extracted scenario inherits its parent's upstream tags (no new EARS line
introduced); §4.2 EARS→BDD matrix rows and §4.3 category counts (recovery
9 → 12) were updated accordingly. EARS coverage remains 44/44 (100%).

---

## Manual-Review Queue (deferred)

| Finding | Location | Why deferred |
|---------|----------|--------------|
| qa_lead-P3-002 | §3.2–§3.3 / shared `When` step | Step-definition-layer concern (extract a canonical shared step binding), not a BDD-document edit. No scenario semantics change. Carry to the step-def layer. |
| operator-P3-005 | §3.5 / e452, d521 | A runtime rate-limit-reconfiguration-without-restart scenario asserts a requirement **no EARS line declares**. Adding it here would create an upstream-untraced (orphan) scenario. Route to an EARS-01 amendment first, then regenerate. |
| operator-P3-007 | §3.1 / b9e7, §3.3 / 1a55 | SLO-breach alerting (latency/availability) has **no upstream EARS requirement**. Adding breach-alert scenarios would orphan them against §4.2. Route to an EARS-01 amendment (declare breach-alerting), then add downstream. |

These three are P3 advisory and do not block the gate. Per the framework's
"never fabricate upstream-untraced scenarios" discipline, the two new-scenario
items are escalated to an upstream (EARS) change rather than invented at L4.

---

## Validation After Fix

| Check | Before | After |
|-------|--------|-------|
| Structural lint (sdd_doc_lint) | PASS (0 errors) | PASS (0 errors) |
| Structural warnings | 1 × STY02 (§4 Traceability, 670 w) | 1 × STY02 (§4 Traceability, 679 w — pre-existing, table-driven, non-blocking) |
| Content score | 81 / 100 (GATE FAIL) | re-audit pending — projected ≥ 90 |
| Blocking findings (P0/P1) | 0 | 0 |
| P2 findings open | 12 | 0 |
| P3 findings open | 13 | 3 (deferred to manual queue) |
| Scenarios / scenario-ids | 32 | 35 / 35 (no duplicates) |
| EARS coverage | 44/44 | 44/44 |

Score projection basis: all 12 P2 (the FAIL drivers across qa_lead/tech_lead/
chaos/auditor lenses) are resolved, and the operator-lens P3 observability gaps
(the lowest-weighted contributor's main complaints) are largely closed. The
binding score is the `doc-bdd-audit` re-run, not this report.

Mechanical post-fix checks (all clean): no malformed `@threshold:` tokens, no
residual `And when …` embedded triggers, no residual bare `within 1 second` /
`60 s` timings, no duplicate scenario IDs, no removed-tag dangling references.

---

## Cleanup Summary

No superseded fix reports to remove (this is v001).

---

## Next Steps

1. Re-run `doc-bdd-audit` against BDD-01 v1.0.1 to confirm the content gate
   clears (≥ 90).
2. If it clears, promote downstream to ADR (Layer 5).
3. Route the three deferred P3s: the shared-step item to the step-definition
   layer; the runtime-reconfig and SLO-breach-alerting items to an EARS-01
   amendment before any new L4 scenarios are added.
