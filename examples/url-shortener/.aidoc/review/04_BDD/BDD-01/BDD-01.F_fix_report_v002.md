# BDD-01 Fix Report — Iteration 2 (v002)

**Artifact:** BDD-01 · **Layer:** 04_BDD · **Iteration:** 2
**Date:** 2026-06-10 · **Author:** doc-bdd-fixer (team mode)
**Input:** `report.md` (iter-2 re-review) + per-persona slots under `.aidoc/review/04_BDD/BDD-01/`
**Artifact version:** 1.0.1 → **1.0.2**

---

## Summary

- **Findings in:** 14 (0 P0, 0 P1, 2 P2, 12 P3).
- **Resolved:** 10 (both P2s + 8 P3s).
- **Deferred to manual queue:** 4 P3 (2 framework-deferred C4 step-catalog debt; 2 advisory C5/C2 awaiting a future EARS obligation).
- **Files modified:** 1 (`docs/04_BDD/BDD-01.md`).
- **Files created:** 0 (this report).
- **Lens-validation slots written:** 0 — no blocking findings (0 P0/P1), so the
  team-mode patch-validation loop did not fire; all P2/P3 applied
  deterministically per the skill's advisory rule.
- **Scenarios:** 29 → **31** (+2). **EARS coverage:** 26/26 (100%) maintained.
- **Structural floor (corpus scope `sdd_doc_lint docs/`):** **PASS**, exit 0, 0 error-severity findings.

---

## Fixes Applied

| Code | Pri | Issue | Fix | Location | Confidence |
|------|-----|-------|-----|----------|------------|
| QA-BDD-01-F001 | P2 | §4 had only a prose coverage count, no navigable matrix | Added §4.1 EARS→BDD (26 rows) + §4.2 BDD→EARS (31 rows) bidirectional matrices, derived from the existing `@ears` tags | §4 | auto-safe |
| TL-BDD-01 | P2 | `.9b90` asserted a non-observable RPO-zero durability point at ack | Rewrote to a crash-recovery probe: hard-kill the Mapping Store before post-ack flush, assert the code still resolves after restart | `BDD.01.03.9b90` | auto-assisted |
| QA-BDD-01-F002 | P2 | `.5645` bundled counting-correctness + idempotency (two triggers) | Split into `.5645` (increments once on redirect) and new `.1365` (duplicate re-delivery does not double-count) | §3.1 | auto-assisted |
| QA-BDD-01-F003 | P3 | `.3c70` bundled a user-response and an event-emission assertion (dual plane) | Added a documented dual-plane verification trade-off comment (the lens-sanctioned alternative to extraction) | `BDD.01.03.3c70` | auto-safe |
| TL-BDD-02 | P3 | `.c65d` left the input partition (oracle) unpinned | Pinned the fixture numerically: 10 visits → 6 automated / 4 human; assert owner count == 4 | `BDD.01.03.c65d` | auto-assisted |
| CHAOS-BDD-01 | P3 | `.1f90` collapsed all Mapping-Store losses to one `unreachable` row | Added `dns resolution failure` + `tls handshake failure` Examples rows (matches `.41c7` partition breadth) | `BDD.01.03.1f90` | auto-safe |
| CHAOS-BDD-02 | P3 | No scenario exercised the EARS concurrent-failure precedence note | Added new recovery scenario `.e61c`: reputation-unreachable AND code-space-at-capacity → asserts the retryable "can't be created right now" message wins over the non-retryable at-capacity message | §3.3 | auto-assisted |
| OP-I2-001 | P3 | `.3322` emitted no observable for the counting degraded-mode entry | Added Then asserting a `counting_path_degraded` metric / WARN log | `BDD.01.03.3322` | auto-assisted |
| OP-I2-002 | P3 | `.1f90` emitted no observable for the store-degradation event | Added Then asserting a `mapping_store_degraded` counter labelled by `<degradation>` | `BDD.01.03.1f90` | auto-assisted |
| OP-I2-003 | P3 | `.976e` emitted no observable for the recovery event | Added Then asserting a `counting_path_recovered` event / INFO log with `reconciled_count` | `BDD.01.03.976e` | auto-assisted |

**Confidence counts:** auto-safe 3 · auto-assisted 7 · manual-required 0 (of the applied set).

**Content-preservation:** no existing Given/When/Then step text or Examples-table
data was deleted or semantically altered except where a finding explicitly
required it (the F002 split and the TL-BDD-01 durability rewrite carry the
lens-provided replacement text); all other fixes are additive (new Then
observability clauses, new Examples rows, new scenarios, comments, the §4 matrix).

---

## Manual-Review Queue (4 deferred, all P3, all non-blocking)

| Code | Pri | Why deferred |
|------|-----|--------------|
| QA-BDD-01-F004 | P3 (C4) | Step-duplication debt (shared `issued short code "/abc123"` Given × 4 scenarios). The step-definition **catalog mechanism is framework-deferred in this project scope** (auditor C2: "No step-definition catalog file in project scope; framework-deferred; check does not apply"). Resolving requires either introducing a catalog file (out of scope) or restructuring the single-file BDD into sub-feature Background blocks (heavy change to a corpus that passes structural lint). |
| QA-BDD-01-F005 | P3 (C4) | Same class: shared `destination-reputation screening is enabled` Given × 3 scenarios. Same framework-deferred rationale. |
| OP-I2-ADV-003 | P3 (C5) | Advisory; **no upstream EARS breach-alert obligation** binds. Deferred per the C5 scoping rule pending a future EARS revision declaring `WHEN p95 exceeds threshold … SHALL fire an alert`. |
| OP-I2-ADV-004 | P3 (C2) | Advisory; **no upstream EARS runtime-reconfig obligation** binds. Deferred per the C2 scoping rule pending a future EARS revision declaring a no-restart screening-gate toggle. |

---

## Validation After Fix

| Metric | Before (iter-2 audit) | After (v1.0.2) |
|--------|-----------------------|----------------|
| Scenarios | 29 | 31 (+`.1365`, +`.e61c`) |
| Categories | success 12 / error 6 / recovery 9 / param 1 / optional 1 | success 13 / error 6 / recovery 10 / param 1 / optional 1 |
| EARS coverage | 26/26 | 26/26 (no orphans either direction) |
| Scenario-ID uniqueness | 29 unique | 31 unique (new IDs hash-derived, collision-checked) |
| Structural floor (`sdd_doc_lint docs/`, CI scope) | PASS (exit 0) | **PASS (exit 0, 0 error-severity)** |
| Content score | 89 (gate 90 → FAIL by 1) | re-audit pending (both P2s + 8 P3s resolved → qa_lead/tech_lead lens scores expected to rise above the gate) |

**Validation Slots index:** none. No P0/P1 blocking findings in iteration 2, so no
`<persona>.fix_<N>.json` slots were produced (team-mode lens validation applies
only to blocking findings).

---

## Notes on advisory lint output (not artifact defects)

1. **TRACE-RES-001 single-file false positives (framework gap).** The
   `PostToolUse(Write|Edit)` hook runs `python -m sdd_doc_lint <single-file>`.
   `lint_path()` builds the corpus from the path(s) of a single `lint_path` call,
   so a single-file invocation yields a one-member corpus — `EARS-01` is absent
   from `doc_index`, and **every upstream `@ears` tag is reported unresolvable**
   (52 ERROR lines on BDD-01). These are **advisory only** (the hook always
   exits 0 and never blocks) and **do not occur at CI/audit scope**: the CI step
   (`doc-review.yml` line 60) and the audit lint the `docs` **directory** in one
   `lint_path` call, building the full corpus, where exit is **0** with no
   TRACE-RES findings. No artifact change is warranted — the `@ears` tags are
   correct and resolve corpus-wide. *Recommended framework fix (relevant to
   branch TRACE-RES-FIXUP-001):* make `_check_trace_resolution` skip cross-document
   resolution (or hydrate the sibling corpus) when invoked on a single-member
   corpus, so the advisory hook stops emitting false upstream-resolution errors.

2. **STY02 non-blocking warnings (§4 535w, §1 163w).** Both are
   `severity="warning"` (CLI exits non-zero only on `error`). §4 carries the
   F001-mandated bidirectional matrix; §1 carries the mandatory appended
   revision-history row. This mirrors the upstream **EARS-01 §5**, whose praised
   tabular matrix carries the same accepted non-blocking STY02 (239w). The
   per-section prose word cap counts table rows; required matrices/control tables
   exceed it by nature. Structural floor (error-only) remains PASS.

---

## Cleanup Summary

`BDD-01.F_fix_report_v001.md` retained — it documents the distinct iteration-1
fix pass. No superseded same-iteration report to delete.

---

## Next Steps

Re-run `/aidoc-flow:doc-bdd-audit` (iteration 3). Both P2 findings and 8 of 12
P3 findings are resolved; the qa_lead (82) and tech_lead (87) lens scores — the
two pulling the weighted average below the gate — are expected to rise, lifting
`content_score` above the 90 threshold. The 4 deferred P3s are non-blocking
(framework-deferred catalog debt + advisory EARS-pending items) and are tracked
in the Manual-Review Queue above.
