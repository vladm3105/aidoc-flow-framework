# TDD-01.F — Fix Report v001

**Artifact:** TDD-01 — Link Store
**Layer:** 07_TDD
**Fix date:** 2026-06-10
**Mode:** team (`review_mode` unset → framework default `team`)
**Saga iteration:** 1 · fixer fix-iteration: 1
**Input audit:** `.aidoc/audit/07_TDD-audit.md` + per-persona slots `.aidoc/review/07_TDD/TDD-01/` (combined_status **FAIL**, content_score **84**, structural **PASS**, **0 blocking** P0/P1; 12 P2 + 8 P3)

---

## Summary

| Metric | Value |
|--------|-------|
| Findings in (blocking) | 0 (two chaos P1s reclassified out_of_scope by the audit — Redirect Handler scope) |
| Findings in (advisory) | 12 P2 + 8 P3 = 20 |
| Findings fixed | 20 / 20 |
| Findings remaining | 0 (one P3, SE-TDD01-002, is an IPLAN-deferred binding, documented in §4) |
| Test cases | 21 → 30 (3 split into 7; 6 new coverage cases) |
| Files created | 1 (`TDD-01.F_fix_report_v001.md`) |
| Files modified | 1 (`docs/07_TDD/TDD-01.md`, → v1.0.1) |
| Structural lint | `sdd-doc-lint` exit 0 — no errors; 2 STY02 **warnings** (§4, §5 — non-blocking, see queue) |
| Document body | 2245 words (TDD STY03 ceiling ≤ 2250) |
| §3 ↔ §4 ID parity | 30 / 30, no orphans, no duplicates |

Because the audit carried **zero blocking findings** (the two chaos P1s were
reclassified out_of_scope to the Redirect Handler), team mode applied all 12 P2

+ 8 P3 **deterministically without lens-validation dispatch** — per skill policy
only P0/P1 enter the patch-validation loop. No saga compensation branches were
opened. The dominant remediation was test-case granularity (splitting three
multi-behavior unit cases) plus additive coverage for SPEC-named contracts the
draft never exercised (set_status-unavailable, load/overload, shed-order,
set_status fuzzing, deploy-gate smoke), and instantiation of SPEC §6 numeric
gates (per-op latency, throughput, runtime, flake).

The additions pushed the body to ~2402 words (over the STY03 blocking ceiling of
2250); it was condensed back to 2245 by trimming narrative prose across §1–§7
and the Glossary while preserving every remediation assertion.

---

## Fixes Applied

| Code | Sev | Issue | Fix | Location | Confidence |
|------|-----|-------|-----|----------|------------|
| QL-001 | P2 | `96d3` conflated visit-count success (BDD.1664) + fault-isolation (BDD.5f58) | Split into `74e8` (success: `visit_count += delta`, partial-field, never blocks get) and `9528` (fault: returns None, logs reconciliation `delta_id`); §3 1664/5f58 rows re-pointed | §3, §4 | auto-safe |
| QL-002 | P2 | `1526` bundled known/unknown/taken-down `get` paths | Split into `cf05` (known→record), `54b8` (unknown→None), `1bc0` (taken_down→record); §3 f44a unit cell re-pointed | §3, §4 | auto-safe |
| QL-003 | P2 | `5358` mixed success/idempotency + KeyError negative | Split into `dfd3` (success + idempotent re-apply) and `ee3d` (missing→KeyError, SPEC §3 named error) | §3, §4 | auto-safe |
| TL-02 | P2 | Per-test fixture scope unstated → order-dependence | Added §4 *Fixture independence* convention: fresh function-scoped in-memory KV double, no carry-over | §4 | auto-assisted |
| CHAOS-TDD01-03 | P2 | Zero load/overload cases vs SPEC §6 envelope | Added `233a`: design-load throughput floors + ≤0.1% error budget, 1.5× margin holds, beyond-1.5× fail-fast shed (BDD.b9e7 envelope) | §3, §4 | auto-assisted |
| SE-TDD01-001 | P2 | `claim` fuzz format-only; no `set_status` fuzz | Extended `8504` with encoding-edge/injection inputs (NFC/NFD, %-encoded, NUL/control, homoglyph per BDD.e8b9); added `fc47` set_status reject-before-write | §3, §4 | auto-assisted |
| OP-01 | P2 | No observability-emission assertions | Added emit-assertions: `af07` durable-commit metric + claim span; `840c` write-conflict counter; `3e85` increment-drop + reconciliation-depth; `7115` ERROR-severity log | §4 | auto-assisted |
| OP-02 | P2 | No deploy-gate smoke for one-way substrate | Added `d5d7` (type smoke, ≤30s: claim→COMMITTED, get, durable-commit metric); §5 smoke row (block deploy); §3 `@adr: ADR.01.03.f5f5` row | §3, §4, §5 | auto-assisted |
| CHAOS-TDD01-04 | P2 | Fault-injection mechanism unspecified (sleep/restart risk) | Added §4 *Fault injection* convention: controllable KV-adapter double / toxiproxy + deterministic clock; never real sleep/restart | §4 | auto-assisted |
| QL-004 | P2 | NFR latency budgets not instantiated | `7115` store-unavailable ≤ 1 s (EARS.fab2) + get p95 ≤ 10 ms probe; §5 per-operation latency-gate table | §4, §5 | auto-assisted |
| QL-005 | P2 | set_status StoreUnavailableError path untested | Added `74a4` (integration: degraded write → StoreUnavailableError, fails closed, status unchanged, retry-safe); §3 EARS.539a integration cell | §3, §4 | auto-assisted |
| CHAOS-TDD01-07 | P2 | Shed-order positive guarantee untested | Added `d5ca`: assert SPEC §6 shed ORDER — increment_visits → claim shed, get preserved last | §3, §4 | auto-assisted |
| MERGED-P3-C3-ab25 | P3 | `ab25`/`840c` concurrency: N + sync primitive unstated | `ab25` N=20 (BDD.b9e7) behind shared `asyncio.Event` barrier; `840c` same barrier, never sleep stagger | §4 | auto-assisted |
| OP-03 | P3 | No per-class runtime baselines | §5 runtime table: unit ≤10s, integration ≤60s, e2e ≤300s; >50% regression gate (`pytest --durations=0`) | §5 | auto-assisted |
| CHAOS-TDD01-05 | P3 | Recovery bound = harness timeout, not SPEC budget | `3e85` reconciliation completes ≤ 60 s budget (BDD.a7ad), not merely the 90 s timeout | §4 | auto-assisted |
| SE-TDD01-002 | P3 | Cipher-mode / KMS key-ARN not asserted | `24ff` note: cipher-mode + KMS key-ARN assertions bind at IPLAN when the provider surfaces them (SPEC §6 leaves mode provider-managed) | §4 | manual-required |
| OP-04 | P3 | No flake-rate budget | §5 flake-budget column: unit 0%, integration ≤1% (30-day), e2e ≤2%; quarantine within one business day | §5 | auto-assisted |
| QL-006 | P3 | Test function naming unspecified | §4 *Naming* convention: `test_<method>_<condition>_<expected>` + example | §4 | auto-assisted |
| CHAOS-TDD01-06 | P3 | Fault teardown unstated → cross-test contamination | §4 *Fault teardown* convention: clear fault + assert clean baseline before next test | §4 | auto-assisted |
| OP-05 | P3 | KMS/vault slowness uncovered | `24ff` extended: KMS key-unwrap delay > 200 ms → claim within budget or StoreUnavailableError, no orphan | §4 | auto-assisted |

### Document metadata

Version `1.0.0 → 1.0.1`; added a Document Control revision row; coverage note
updated to 30 cases (unit 13, integration 7, security 3, e2e 4, performance 2,
smoke 1). Frontmatter `version` and §1 row kept in sync (no FM01). New tagged
ref `@adr: ADR.01.03.f5f5` added to §7 cumulative `@adr` line and resolves in
ADR-01.

---

## Validation Slots index

No lens-validation slots written. The audit carried **0 blocking findings**
(P0/P1); per team-mode policy only blocking findings enter the patch-validation
loop. All 20 advisory findings (12 P2 + 8 P3) were applied deterministically. No
`fix_N.json` slot files and no saga `compensation_actions[]` entries were
produced.

---

## Manual-Review Queue

1. **SE-TDD01-002 (P3) — IPLAN-deferred, not resolvable at TDD scope.** Cipher
   mode and KMS key-identity/ARN assertions can only bind once IPLAN-01 selects
   the KV/KMS provider (SPEC §6 leaves the envelope mode provider-managed). The
   `24ff` case carries the binding note; the assertion itself lands at Layer 8.
2. **STY02 warnings on §4 (1074 w) and §5 (325 w).** Adding 9 net cases and the
   numeric-gate tables exceeds the 500-word / 200-word section targets. These
   are **warnings, not errors** (the structural floor passes, exit 0). Splitting
   §4 into `##` subsections is **not** available: the TDD template requires
   exactly seven numbered sections and the audit checks for them, so a fourth-
   and-fifth-level reshuffle would itself fail the floor. Accepted as the
   inherent cost of the granularity + coverage remediation; the document stays
   under the binding STY03 doc-body ceiling (2245 / 2250).
3. **Placeholder calibration values to confirm on first green run.** Runtime
   baselines (unit ≤10 s, integration ≤60 s) and flake budgets (≤1% / ≤2%) are
   SPEC-aligned starting points, not measured numbers — confirm via
   `pytest --durations=0` and adjust in a follow-up patch if reality differs.

---

## Upstream Drift Summary

None. SPEC-01 v1.0.1 unchanged; this is content remediation against the existing
seed, not an upstream re-merge. No `.drift_cache.json` update.

---

## Validation After Fix

| Metric | Before | After |
|--------|--------|-------|
| Structural lint (`sdd-doc-lint`) | exit 0 (floor PASS) | exit 0 (floor PASS; 2 STY02 warnings) |
| Document body words | 1595 | 2245 / 2250 |
| Test cases / §3↔§4 parity | 21 / clean | 30 / clean (no orphans, no dups) |
| Blocking findings (P0/P1) | 0 | 0 |
| Advisory findings open | 20 | 0 |
| Combined gate status | FAIL (score 84) | re-audit required to confirm PASS |

Re-audit is the binding gate — this report records the remediation, not a new
score. The combined score is recomputed by `doc-tdd-audit` on the next pass.
The 84-cap drivers (qa_lead 79, operator 74, chaos 71) are directly addressed:
all qa_lead C2 granularity finds, all operator observability/smoke/runtime/flake
finds, and all chaos load/shed/fault-determinism finds are resolved.

---

## Cleanup Summary

No prior fix reports to supersede (this is v001). TDD backup retained at
`tmp/backup/TDD-01_20260610-092924/TDD-01.md`.

---

## Next Steps

1. Re-run `doc-tdd-audit` (saga iteration 1 re-review) to recompute the combined
   gate. Expect PASS: 0 blocking findings, structural floor green, and every
   score-depressing P2 cluster resolved.
2. On PASS, the autopilot loop promotes TDD-01 toward IPLAN authoring.
3. Bind SE-TDD01-002 (cipher mode / KMS ARN) at IPLAN-01 when the provider is
   selected.
