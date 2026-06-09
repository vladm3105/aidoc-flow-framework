# BDD-01.F Fix Report — v002

**Artifact:** BDD-01 (`docs/04_BDD/BDD-01.md`)
**Layer:** 04_BDD
**Fixer:** doc-bdd-fixer (team mode; deterministic P2/P3 pass — 0 blocking findings)
**Input audit:** BDD-01 review report iteration 2 (content score 88, GATE FAIL), `report.md` + `verdict.json`
**Iteration:** 2
**Report date:** 2026-06-09
**Version transition:** BDD-01 v1.0.1 → v1.0.2

---

## Summary

| Metric | Value |
|--------|-------|
| Findings in | 18 (0 P0, 0 P1, 8 P2, 10 P3) |
| Findings fixed | 10 (8 P2 + 2 P3) |
| Findings deferred (manual queue) | 8 (P3 — dependent on upstream EARS, step-def-layer, or retain-as-is) |
| Files created | 0 |
| Files modified | 1 (`docs/04_BDD/BDD-01.md`) |
| Scenarios before → after | 35 → 35 (no scenarios added/removed; steps split in place) |
| Structural lint | PASS → PASS (35 scenarios, 35 spec_traces, IDs/sections unchanged) |

There were **no blocking (P0/P1) findings**, so no per-lens patch-validation
loop ran (team mode validates only blocking findings; P2/P3 are applied
deterministically). The gate FAILed purely on content score (88 < 90), driven
by the qa_lead lens (weight 35, score 80 — six C2 atomicity violations) and
the tech_lead lens (weight 25, score 87 — two C2 unbounded-assertion gaps).

All 8 P2 findings were applied. Two low-risk P3s (tech_lead-P3-001 pool
cardinality, qa_lead-P3-002 coverage-matrix footnote) were applied because they
close the same lens's residual implementability/traceability concern at zero
semantic risk. The remaining 8 P3s are routed to the manual-review queue: six
require an upstream EARS amendment (adding them at the BDD layer would create
orphan, untraced scenarios — explicitly forbidden), one is a step-definition
(code-layer) extraction with no anchor in this `.md` artifact, and one is
flagged by the audit itself as acceptable to retain as-is.

---

## Fixes Applied

| Finding | Location | Check | Fix | Confidence |
|---------|----------|-------|-----|------------|
| qa_lead-P2-001 | §3.1 / 5887 | C2 | Split the compound `And` (test-double recorded one call **and** no code committed before clean verdict) into two discrete `And` steps; preserved the call-order parenthetical verbatim. | auto-safe |
| qa_lead-P2-002 | §3.2 / 842c | C2 | Split the compound `And` (body contains only contracted text **and** must not disclose internals) into a positive `And` and a negative `And`. | auto-safe |
| qa_lead-P2-005 | §3.2 / bcf8 | C2 | Split the compound `Then` (reject message **and** issue no short code) into `Then` (reject within budget) + `And` (issue no short code). | auto-safe |
| qa_lead-P2-003 | §3.4 / e8b9 | C2 | Split the compound `Then` into `Then` (reject within budget) + `And` (no short code); split the compound positive+negative body `And` into two `And` steps. | auto-safe |
| qa_lead-P2-004 | §3.4 / 5599 | C2 | Same split as e8b9 (compound `Then` → `Then`+`And`; compound body `And` → positive `And` + negative `And`). | auto-safe |
| qa_lead-P2-006 | §3.3 / ed21 | C2 | Split the compound `Then` (three bundled negatives) into three discrete steps: no acknowledged short code / no durable mapping / no orphan short code. | auto-safe |
| tech_lead-P2-002 | §3.5 / e452 | C2 | Bound the throttling scenario: configured rate expressed as a fixture (60 req / 60 s, one source) in `Given`; named throttle-response budget (100 ms) added to `Then`; author-assumption comment added (pending PRD §13). | auto-assisted |
| tech_lead-P2-001 | §3.5 / d521 | C2 | Bound the negative absence-of-throttling assertion: explicit load (120 req @ 2 rps, one source) in `When`; 60 s observation window added; split compound `Then` into default-behaviour `Then` + no-throttle `And`; author-assumption comment added (pending PRD §13). | auto-assisted |
| tech_lead-P3-001 | §3.5 / fa47 | C1 | Added fixture-configured pool cardinality (100-slot pool, 79 occupied) to `Given` so the single-allocation 79%→80% crossing is directly constructible; extended the author-assumption comment. | auto-assisted |
| qa_lead-P3-002 | §4.2 matrix | C1 | Added a coverage note under the EARS→BDD matrix clarifying that the EARS.01.04.4eec issuance-latency budget is exercised as a `WITHIN` constraint in every issuance-path scenario, not only the single binding row. | auto-safe |

**Content-preservation:** every split relocates existing assertion text onto
its own atomic step line — no assertion text was invented, deleted, or
semantically altered, and no `Examples` table data was touched. The two
tech_lead bounds add fixture values explicitly flagged as author assumptions
pending a PRD §13 rate-limit element (consistent with the suite's existing
author-assumption convention).

---

## Manual-Review Queue (deferred — not fixed here)

| Finding | Location | Reason deferred | Routing |
|---------|----------|-----------------|---------|
| qa_lead-P3-001 | §3.1 / b9e7 | Audit flags the parenthetical 5xx clause as **acceptable to retain** as a single quantified success-rate definition. | Retain as-is (no action). |
| qa_lead-P3-003 | f9d6 / 40d7 / 842c | Shared-step ("When the caller requests adoption metrics") extraction belongs to the step-definition (code) layer; the `.md` suite has no step-definition anchor to extract into. | Step-definition layer (downstream). |
| security_engineer-P3-001 | §3.2 / Redirect Handler | New input-fuzzing scenario on the redirect path. Defer to a focused security-coverage pass; no upstream blocker, but out of the C2 atomicity scope this iteration targets. | Backlog (security coverage). |
| security_engineer-P3-002 | §3.1/§3.2 / Metrics Reporter | New malformed-input scenario on the metrics endpoint. Same as above. | Backlog (security coverage). |
| security_engineer-P3-003 | §3.4 / 5599 | SSRF encoding-bypass fixtures (IPv6 loopback, decimal/octal IP, DNS-rebinding) require the **EARS** denylist contract to name them first; adding Examples rows without an upstream parent fabricates coverage. | Surface to EARS owner. |
| operator-P3-001 | §3.5 | Runtime-config-change scenario for rate-limit/retry-ceiling has no EARS parent (no runtime-reconfigurability line). Adding it would orphan the scenario. | Surface to EARS owner. |
| operator-P3-002 | §4 / SLO lines | SLO-breach alert scenarios (redirect p95, monthly availability) require EARS lines declaring alert emission. | Surface to EARS owner. |
| operator-P3-003 | §3.2 / bcf8 | Harmful-destination-rejected observable signal requires EARS.01.03.9671 to declare a log/metric emission first. | Surface to EARS owner. |

**Companion EARS track:** the four operator/security findings that depend on upstream EARS
(operator-P3-001/002/003, security_engineer-P3-003) should be raised with the
EARS-01 owner as a companion remediation track. They cannot be closed at the
BDD layer without fabricating upstream-untraced scenarios.

---

## Validation After Fix

| Dimension | Before (it.2 audit) | After (expected) |
|-----------|---------------------|------------------|
| Structural status | PASS | PASS (no ID/section/scenario-count change) |
| Scenario count | 35 | 35 |
| spec_trace count | 35 | 35 |
| EARS coverage | 100% (44/44) | 100% (44/44) — matrix unchanged, note added |
| Content score | 88 (FAIL) | re-audit pending |
| Blocking findings | 0 | 0 |

No lens-validation slots were written this iteration (zero blocking findings —
team mode validates only P0/P1). The 8 C2 atomicity resolutions target the
qa_lead lens (80) and tech_lead lens (87); resolving all 8 P2s is expected to
lift the weighted average above the 90 gate floor. The binding confirmation is
the re-run of `doc-bdd-audit`.

---

## Cleanup Summary

- `BDD-01.F_fix_report_v001.md` is **retained** — it documents iteration 1's
  distinct finding set (25 findings, 32→35 scenarios) and is part of the
  remediation audit trail, not a superseded duplicate of this report.
- No scaffold/placeholder files were created this iteration.
- Backup of the pre-fix BDD: `tmp/backup/BDD-01_<ts>/BDD-01.md`.

---

## Next Steps

1. Re-run `doc-bdd-audit` (iteration 3) to confirm content score ≥ 90 and
   re-validate the qa_lead and tech_lead lens scores.
2. If the gate passes, promote BDD-01 to the ADR layer.
3. Raise the companion EARS track (4 upstream-dependent P3s) with the EARS-01
   owner; schedule the two security-coverage P3 scenarios as a focused
   follow-up once the gate is green.
