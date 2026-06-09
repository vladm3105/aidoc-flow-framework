# SPEC-01.F — Fix Report v001

**Artifact:** SPEC-01 — Link Store
**Layer:** 06_SPEC
**Fix date:** 2026-06-09
**Mode:** team (`review_mode` unset → framework default `team`)
**Saga iteration:** 1 · fixer fix-iteration: 1
**Input audit:** `.aidoc/audit/06_SPEC-audit.md` + per-persona slots `.aidoc/review/06_SPEC/SPEC-01/` (combined_status **FAIL**, content_score **79**, 1 P1 + 9 P2 + 9 P3)

---

## Summary

| Metric | Value |
|--------|-------|
| Findings in (blocking) | 1 P1 (CHAOS-002) |
| Findings in (advisory) | 9 P2 + 9 P3 |
| Findings fixed | 19 / 19 |
| Findings remaining | 0 (2 new P3 advisories surfaced in validation — deferred, see queue) |
| Files created | 1 (`chaos_engineer.fix_1.json`) |
| Files modified | 1 (`docs/06_SPEC/SPEC-01.md`, → v1.0.1) |
| Structural lint | clean (`sdd-doc-lint` exit 0; STY03/STY02/TH01/ID03 all resolved) |
| Document body | 2249 words (SPEC ceiling ≤ 2250) |

The single blocking **P1 (CHAOS-002, chaos_engineer C1)** was patched in §6 (NFR
targets + measurement methodology + resilience envelope) and §3 (boundary
failure semantics) and **lens-validated** by the `chaos-engineer` subagent:
`resolved=true, regression=false`, **lens_score 74 → 89**. The 9 P2 and 9 P3
advisory findings were applied deterministically (no lens validation per
team-mode policy). Adding the remediation content pushed the body well past the
STY03 blocking length (peaked at 2615 words); it was condensed back to 2249 by
trimming verbose prose across §1–§6 while preserving every remediation.

---

## Fixes Applied

| Code | Sev | Issue | Fix | Location | Confidence |
|------|-----|-------|-----|----------|------------|
| CHAOS-002 | P1 | NFRs only partially concrete; `get` allocation within 50 ms budget undefined | Added per-operation **NFR targets** table (latency allocation + throughput + error budget), **measurement methodology** (server-side, rolling 5-min window, design load), and **resilience envelope** (overload margin, shed order, bounded `CODE_TAKEN` retry, bounded reconciliation log) | §6 | auto-assisted |
| ARCH-002 | P2 | `ClaimResult.record` undefined for `CODE_TAKEN`; triple not total | `record` = `None` on `CODE_TAKEN`; `replay=false` on `CODE_TAKEN`; stated the `(outcome, record, replay)` triple is total | §4 | auto-safe |
| MERGED-P2-C3-CLAIM-ERRORS | P2 | `claim` retry-safety with `idempotency_key=None` unspecified; no timeout/retry/breaker per boundary | `claim` idempotent (retry-safe) only with a non-None key (submitter or ADR.01.03.3315 content-derived fallback); added §3 **Boundary failure semantics** table (timeout/retry/circuit-break per boundary) | §3 | auto-assisted |
| TL-001 | P2 | Concurrency primitive for `visit_count` unnamed | `increment_visits` is a native atomic field-increment (KV ADD/INCR); RMW forbidden; capability matrix row | §3, §2 | auto-assisted |
| INT-002 | P2 | No schema-evolution policy | Added §4 evolution policy: backward-compatible within MAJOR, `LinkStatus` append-only, breaking change bumps SPEC MAJOR + contract version + ADR-01 §7 migration | §4 | auto-assisted |
| INT-003 | P2 | No contract version on `LinkStore` port / KV boundary | Stamped `LinkStore` **contract v1** (tracks SPEC MAJOR) on the port and the KV dependency row | §2, §3 | auto-safe |
| INT-004 | P2 | No KV minimum-capability matrix | Added **KV substrate minimum-capability matrix**; adapters lacking native conditional-write marked non-conformant (ADR.01.05.3afa) | §2 | auto-assisted |
| CHAOS-001 | P2 | Resilience envelope uncharacterized; unbounded `CODE_TAKEN` retry | Folded into §6 resilience envelope (design load / 1.5× margin / fail-fast shed; bounded `CODE_TAKEN` retry, default 5) | §6 | auto-assisted |
| SEC-001 | P2 | Crypto regression vs ADR.01.03.0db1 | Restated AES-256 envelope + provider-managed KMS key + provider-default rotation; CMK deferred; TDD contract row | §6, §7 | auto-assisted |
| SEC-002 | P2 | No `short_code` validation; `original_url` delegation unscoped | Added §5 `short_code` base62 allowlist + length rule (before conditional-put); scoped `original_url` screening to the Shortening API ingress (ADR.01.03.1050) | §5 | auto-assisted |
| TL-004 | P3 | `increment_visits` fault branch signal ambiguous | Defined the fault branch as absorbed into the reconciliation log; log-write failure mode = silent drop + drop metric (§6) | §5 | auto-assisted |
| CHAOS-005 | P3 | Degradation order get vs claim unspecified | Shed order: `increment_visits` → `claim` → `get` preserved last | §6 | auto-assisted |
| CHAOS-004 | P3 | Reconciliation log growth unbounded | Bounded log (max retention), `reconciliation_overflow` alert, rate-bounded drain | §6 | auto-assisted |
| ARCH-001 | P3 | Increment transition mis-cites BDD.01.03.6d94 | Re-cited to BDD.01.03.1664 (visit-count increment scenario) | §5 | auto-safe |
| ARCH-003 | P3 | §8 `@bdd` roll-up omits bcfb, f44a | Added bcfb, f44a (+ 1664 for the new inline anchor) to §8 cumulative `@bdd` | §8 | auto-safe |
| TL-003 | P3 | Reconciliation log owner undeclared | Declared Link Store owns the reconciliation log (durable off-path sink); write synchrony stated | §2, §5 | auto-safe |
| INT-005 | P3 | Per-boundary observability unspecified | Added §6 **Observability** line naming emitters per boundary (Link Store vs caller; trace-span propagation) | §6 | auto-assisted |
| CHAOS-003 | P3 | `set_status` retry semantics + reconciliation dedup key absent | `set_status` idempotent (last-writer-wins); reconciliation per-delta `delta_id` dedup marker | §3, §5 | auto-assisted |
| SEC-003 | P3 | No audit-event emission/schema | Added §6 **Audit events** (`{event_type, actor_principal, target_code, outcome, ts_utc}` for claim/takedown/authn) + §7 TDD contract row | §6, §7 | auto-assisted |

### Document metadata

Version `1.0.0 → 1.0.1`; added a Document Control revision row; replaced the
stale `tdd_ready_score: 92` self-claim narrative with "recomputed by
doc-spec-audit". Frontmatter `version` and §1 row kept in sync (no FM01).

---

## Validation Slots index

| Slot file | Lens | Finding | Resolved | Regression | lens_score |
|-----------|------|---------|----------|------------|------------|
| `chaos_engineer.fix_1.json` | chaos_engineer | CHAOS-002 (P1) | yes | no | 74 → 89 |

Advisory findings (P2/P3) applied deterministically — no lens-validation slot
per team-mode policy (only blocking P0/P1 enter the patch-validation loop).

---

## Manual-Review Queue

No blocking items. Two **new P3 advisories** surfaced by the chaos-engineer
validator (non-blocking; deferred to a later iteration to respect the SPEC body
size ceiling — the document is at 2249/2250 words):

- **CHAOS-002-R1** — reconciliation-log retention bound is qualitative ("max
  retention"); add a placeholder ceiling magnitude (entries/bytes/age) so the
  overflow test is constructable.
- **CHAOS-002-R2** — circuit-break OPEN is defined but the reclose / half-open
  reset semantics are implicit; add a reset contract (timing bindable at TDD).

Drafted NFR magnitudes (10 ms `get` allocation, ≥ 500 read/s, ≥ 99.9% / ≤ 0.1%)
are SPEC-level allocations for **TDD load-test calibration**, not final numbers.

---

## Upstream Drift Summary

None. ADR-01 unchanged; this is content remediation against the existing seed,
not an upstream re-merge. No `.drift_cache.json` update.

---

## Validation After Fix

| Metric | Before | After (expected) |
|--------|--------|------------------|
| Structural lint (`sdd-doc-lint`) | clean (gate floor PASS) | clean (exit 0) |
| Document body words | within ceiling | 2249 / 2250 |
| chaos_engineer lens_score | 74 | 89 (patch-validated) |
| Blocking findings (P0/P1) | 1 | 0 |
| Combined gate status | FAIL (score 79) | re-audit required to confirm PASS |

Re-audit is the binding gate — this report records the remediation, not a new
score. The synthesizer's combined score is recomputed by `doc-spec-audit` on the
next pass.

---

## Cleanup Summary

No prior fix reports to supersede (this is v001). SPEC backup retained at
`tmp/backup/SPEC-01_20260609-144153/SPEC-01.md`.

---

## Next Steps

1. Re-run `doc-spec-audit` (saga iteration 1 re-review) to recompute the
   combined gate. Expect PASS: 0 blocking findings remain, the structural floor
   is green, and the chaos lens (the prior 79 cap driver) rose 74 → 89.
2. On PASS, the autopilot loop promotes SPEC-01 toward TDD authoring.
3. Optionally fold CHAOS-002-R1/R2 into a later patch if a follow-up iteration
   opens (both P3, non-blocking).
