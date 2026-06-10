# EARS-01 Fix Report — v001 (saga iteration 1)

**Artifact:** EARS-01 (URL Shortener — EARS Requirements)
**Layer:** 03_EARS · **Mode:** team (lens-validated remediation)
**Date:** 2026-06-10 · **Audit input:** report.md (gate FAIL, content score 84)

---

## Summary

| Metric | Value |
|--------|-------|
| Findings in (audit) | 16 — 1 P1, 6 P2, 9 P3 |
| Fixed | 16 |
| Remaining (blocking) | 0 |
| Files created | 3 — this report; `security_engineer.fix_1.json`; `chaos_engineer.fix_1.json` |
| Files modified | 1 — `docs/03_EARS/EARS-01.md` |
| New EARS §3 lines | 8 (`fa0b`, `eca5`, `6811`, `4400`, `f62a`, `ac68`, `9903`, `4ebf`) |
| §3 lines retired (split) | 2 (`e8a5` → `ac68`+`9903`; `8650` → `6811`+`4400`) |

The one blocking finding (MERGED-P1-001) was patched and **non-regression
validated by both responsible lenses** (security_engineer, chaos_engineer) —
each returned `resolved: true`, no new P0/P1, lens_score 91. P2/P3 findings were
applied deterministically per the remediate contract (advisory findings take no
lens validation).

---

## Fixes Applied

| Code | Pri | Issue | Fix | Confidence |
|------|-----|-------|-----|------------|
| MERGED-P1-001 | P1 | PRD abuse case `PRD.01.13.e661` (automated repeat-visit metric inflation) had no EARS line pair | Added IF line `EARS.01.03.fa0b` (Visit Counter applies adoption-integrity treatment, mitigation deferred to `BRD.01.08.c478`); added §5 PRD-§13 risk-coverage matrix mapping e661 → .fa0b | auto-assisted |
| RS-001 | P2 | `EARS.01.03.e8a5` conjoined two independent defense layers | Split into `EARS.01.03.ac68` (non-walkable keyspace) + `EARS.01.03.9903` (per-source rate-limiting), each `@prd: PRD.01.09.dd8d` | auto-safe |
| RS-002 | P2 | `EARS.01.03.8650` conjoined screen-at-create + non-issuance | Split into `EARS.01.03.6811` (screen at create) + `EARS.01.03.4400` (withhold code), each WHERE-gated `@prd: PRD.01.09.b6cb` | auto-safe |
| QL-001 | P2 | No per-line downstream BDD slot on any requirement | Added inline `@bdd: BDD-01` slot to all 20 §3 requirement lines (downstream-tag form; lint-clean) | auto-safe |
| SE-002 | P2 | No access-control rule for confidential/PII original-URL in Mapping Store | Added ubiquitous line `EARS.01.03.4ebf` (least-privilege read access per classification; access/erasure parameters deferred to `BRD.01.08.daeb`) | auto-assisted |
| CE-001 | P2 | No post-issue takedown removal obligation (risk 011a reactive half) | Added IF line `EARS.01.03.f62a` (flagged/taken-down code returns not-found within takedown SLA, deferred to `BRD.01.08.daeb`) | auto-assisted |
| CE-002 | P2 | Capacity recovery (`.5442`) had no paired detection rule | Added state-driven line `EARS.01.03.eca5` (capacity-utilization alert; threshold deferred); cross-linked to `.5442` | auto-assisted |
| TL-001 | P3 | `.5442` carried no `@threshold` deferral marker | Added `@threshold: PRD.01.quota.codespacecapacity` to `.5442` and `.eca5` | auto-safe |
| TL-002 | P3 | `.50d1`/`.5442` capacity-error wording ambiguous; no precedence | `.50d1` → retryable §10 "Shortening unavailable"; `.5442` → non-retryable §10 "at capacity"; added precedence note for simultaneous conditions | auto-safe |
| RS-003 | P3 | `.5442` §13 provenance indirect | Annotated `.5442` with capacity-guard origin `PRD.01.13.385e` | auto-safe |
| QL-002 | P3 | §5 matrix unidirectional (EARS→PRD only) | Added downstream column to the §5 rollup matrix (bidirectional) | auto-safe |
| QL-003 | P3 | `.4425` no idempotency declaration | Added exactly-once / no-double-increment clause, dedup deferred to `BRD.01.08.c478` | auto-assisted |
| QL-004 | P3 | `.f766` no dedup semantic | Added exactly-once-under-concurrency clause, consistent with `.4425` | auto-assisted |
| QL-005 | P3 | `.5066` no safe-retry/idempotency clause | Added duplicate-submission clause tied to uniqueness invariant `.bca8`; generation strategy deferred to `BRD.01.08.9665` | auto-assisted |
| CE-004 | P3 | `.5e5b` RTO had no paired detection obligation | Noted store-loss detection deferred to availability ADR topic `BRD.01.08.5b91` | auto-assisted |
| SE-003 | P3 | `.aa59` privileged owner-access had no audit-log obligation | Noted owner-access audit-logging deferred to ops/observability ADR topic `BRD.01.08.c478` | auto-assisted |

---

## Manual-Review Queue

None blocking. Two non-fixer items noted for transparency:

- **STY02 (advisory, non-blocking):** §5 Traceability is 239 words (warning
  threshold 150; Phase-7 split threshold 300). Below the split line; left intact
  to preserve the per-source + risk-coverage rollups. No action required.
- **TRACE-RES-001 (out of fixer scope):** 21 `@prd:` host-resolution errors.
  This is the pre-existing single-file corpus-resolution condition owned by the
  `trace-res-fixup-001` branch (the pre-edit artifact already carried 20 of the
  same class; the audit's structural floor passed with them present). The `@prd`
  tags reference real PRD-01 §9 elements and are correct — **not** remediated
  here, per the "never hand-edit a correct tag to mask a framework/linter gap"
  convention.

---

## Validation After Fix

| Check | Before | After |
|-------|--------|-------|
| Structural floor (sdd_doc_lint) | PASS (20 × TRACE-RES-001 pre-existing) | PASS (21 × TRACE-RES-001 same class; **0** malformed-ID / new structural errors introduced) |
| Malformed-tag errors (ID01/ID02) | 0 | 0 (intermediate `[BDD-pending:]` placeholder + `ADR-deferred` token errors caught and reworked to lint-clean forms before completion) |
| MERGED-P1-001 (security lens) | P1 open | resolved, lens_score 91, no regression |
| MERGED-P1-001 (chaos lens) | P3→merged | resolved, lens_score 91, no regression |
| PRD §13 risk coverage | 3/4 (e661 unanchored) | 4/4 |

Authoritative content re-score is produced by the next `doc-ears-audit` pass.
Lens-region scores moved up on the patched regions (security 76→91, chaos
85→91); the P2/P3 applications target the requirements_specialist (84) and
qa_lead (83) deficits (atomicity splits, per-line BDD slots, idempotency,
precedence).

### Validation Slots index

| Slot | Lens | Finding | Result |
|------|------|---------|--------|
| `security_engineer.fix_1.json` | security_engineer | MERGED-P1-001 | resolved=true, no new P0/P1, score 91 |
| `chaos_engineer.fix_1.json` | chaos_engineer | MERGED-P1-001 | resolved=true, no new P0/P1, score 91 |

---

## Cleanup Summary

No superseded fix reports to delete (this is v001 for iteration 1).

## Next Steps

Re-run `/aidoc-flow:doc-ears-audit` on EARS-01 to confirm the gate passes
(content score ≥ 90, no unresolved P0/P1). On PASS, the autopilot advances to
the BDD layer. The TRACE-RES-001 class is tracked separately on the
`trace-res-fixup-001` branch and is not a re-audit blocker.
