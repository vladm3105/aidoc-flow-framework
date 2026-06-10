# SPEC-01 Fix Report — v002 (saga iteration 2)

**Artifact:** SPEC-01 (Layer 06_SPEC — Mapping Store Component Specification)
**Mode:** team (no blocking findings → deterministic application, no lens-validation cycle)
**Input audit:** `report.md` / `verdict.json` (gate FAIL, content score 89/100, threshold 90)
**Date:** 2026-06-10

---

## Summary

| Metric | Value |
|---|---|
| Findings in (audit) | 8 (P0=0, P1=0, P2=3, P3=5) |
| Findings fixed | 8 / 8 |
| Findings remaining | 0 |
| Blocking findings | 0 — gate failure was score-driven only (89 < 90) |
| Files created | 1 (this report) |
| Files modified | 1 (`docs/06_SPEC/SPEC-01.md`) |
| YAML blocks repaired | 0 (none malformed) |
| New trace tags added | 0 (all fixes reuse the existing EARS/BDD/ADR/threshold set; CHAO-001 reuses the already-upstream `@threshold: PRD.01.quota.codespacecapacity`) |

Because the verdict carried **zero P0/P1 findings**, every finding is advisory
(P2/P3). Per the skill contract, advisory findings are applied deterministically
without per-lens patch validation; no `*.fix_N.json` validation slots were
produced and no saga `BRANCH_COMPENSATING` cycle was entered. All fixes are
grounded in the upstream ADR-01 (the seed) and the existing EARS/BDD trace set.

A Phase-8 style pass followed the content fixes: the additions initially tripped
**STY03** (body > 2250-word blocking ceiling); verbose explanatory prose was
compressed across §1–§7 — preserving every interface signature, data-model
schema, behavior rule, trace tag, and threshold tag — to land the body back
under the ceiling. Two transient **TH01** glitches introduced during that
compression (punctuation glued to a `@threshold:` key) were corrected.

---

## Fixes Applied

| Code | Issue | Fix | File / location | Confidence |
|---|---|---|---|---|
| ARCH-001 (P2) | §3 `increment_visit` over-committed a named isolation level ("atomic upsert under a serializable transaction") that ADR-01 §5 does not make | Reframed the no-lost-update guarantee as an obligation **inherited from ADR-01 §5** (concurrent confirmed visits lose no increment, BDD.01.03.02c1); the concurrency primitive is now explicitly **deferred to TDD-01/IPLAN**, not bound to an isolation level at SPEC altitude | §3 `increment_visit` docstring | auto-assisted |
| INTG-001 (P2) | §4 schema-evolution named the multi-version straddle but gave no compatibility matrix / skew bound | Added a **producer×consumer compatibility matrix** (N-1 both directions; single-MAJOR max skew; out-of-window → dead-letter, never best-effort decode), tied to the MAJOR-bump policy | §4 Data Models — "Compatibility window" | auto-assisted |
| CHAO-001 (P2) | §6 characterized read saturation only; the create/write path had no overload characterization | Added a **create design-load** bullet: bounded by sync-commit tier capacity (PRD commits no create rate — anchored to the tier, not an invented threshold); beyond-margin **fast-fail/shed** mirroring the codespace-capacity error; `@threshold: PRD.01.perf.screeningdeadline` as the admission bound; **bounded backoff + jitter** on `DurabilityHaltError` retries to prevent a synchronized recovery-phase storm (ADR-01 §7) | §6 Performance considerations | auto-assisted |
| TECH-001 (P3) | The durable dispatch queue had no declared owner | Declared the **Visit Counter** as the single owner — provisions, persists (durable storage, not in-memory), and replays the queue + DLQ on crash; idempotent `event_id`-keyed consumer makes replay safe | §3 "Delivery channel" note | auto-assisted |
| INTG-002 (P3) | Dead-letter trip condition ambiguous (time- vs retry-count-driven) | Stated the trip is **time-driven** — unreconciled past the `@threshold: PRD.01.reliability.countstaleness` window → dead-letter; §6 reconciliation-lag metric + dead-letter counter fire on the **same** condition | §3 `increment_visit` delivery contract | auto-safe |
| CHAO-002 (P3) | Dead-lettered events had no recovery path / MTTR | Added **recovery semantics**: dead-lettered events are replayed through the idempotent (`event_id`-keyed) increment path on operator action — a bounded manual reconciliation closing the exactly-once loop for the failure tail | §3 `increment_visit` delivery contract | auto-assisted |
| SECU-001 (P3) | `mark_taken_down` (security-relevant state mutation) emitted no audit event | Added `mark_taken_down` to §5 Audit events emitting `{subject, action='mark_taken_down', resource=code, decision, timestamp, reason}` on takedown and re-mark (abuse-protection sibling BRD.01.08.daeb depends on the state) | §5 Audit events | auto-safe |
| SECU-002 (P3) | `resolve` / `mark_taken_down` lacked the store-boundary input-validation rule `put_mapping` has | Added a §5 validation rule: `resolve`/`mark_taken_down` accept only a `ShortCode` matching the code-generation charset/length allowlist (alphabet owned by BRD.01.08.9665) as a store-boundary precondition — defense-in-depth parity with `put_mapping` | §5 Validation rules | auto-safe |

**Confidence counts:** auto-safe = 3 · auto-assisted = 5 · manual-required = 0.

---

## Manual-Review Queue

None. All eight advisory findings were resolvable from the upstream ADR-01 seed
and the existing EARS/BDD/threshold trace set without inventing new domain
content. No `[TODO]`/`[TBD]` placeholders were introduced.

---

## Upstream Drift Summary

No upstream drift. All fixes are *additive clarifications* that inherit existing
ADR-01 commitments (§5 side-effect contract, §7 pool isolation / monitoring
baseline, §3 access-control identity model, §10 sibling map) — no upstream
content was contradicted, removed, or superseded. `.drift_cache.json` unchanged
(no tier-1/2/3 merge triggered).

---

## Validation After Fix

| Dimension | Before (audit iter 2) | After (this pass) |
|---|---|---|
| Structural lint (STY/TH/FM/ID, single-file) | PASS | PASS — STY03 + TH01 introduced during editing were both cleared; body ≤ 2250-word ceiling |
| Blocking findings (P0/P1) | 0 | 0 |
| Advisory findings open (P2/P3) | 8 | 0 |
| Content score (weighted) | 89 / 100 | re-measured by the next `doc-spec-audit` (binding gate) |
| Threshold tags | 6 distinct keys | 6 distinct keys preserved (codespacecapacity reused, not new) |
| Upstream trace tags | 6 EARS / 13 BDD / 7 ADR / 1 TDD | unchanged |

> Note: `TRACE-RES-001` findings reported by the single-file lint hook are a
> single-file-isolation artifact (the host documents ADR-01/EARS-01/BDD-01 are
> not loaded when one file is linted alone) and are the subject of the separate
> `TRACE-RES-FIXUP-001` branch work — they are **not** introduced or addressed by
> this content-fix pass.

---

## Cleanup Summary

- Superseded prior fix report `SPEC-01.F_fix_report_v001.md` removed (this v002
  is the current fix report of record for the SPEC-01 saga).

---

## Next Steps

Re-run `doc-spec-audit` (autopilot's next phase: `re-review`, iteration 3) to
re-score the content dimension against the gate threshold of 90. With all three
P2 score-drag findings and the five P3s resolved, the score gap (89 → ≥90) is
expected to close. Loop continues until score ≥ threshold or max iterations.
