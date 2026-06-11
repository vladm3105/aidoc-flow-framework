# ADR-01 Fix Report — v001

**Skill:** doc-adr-fixer · **Mode:** team (per framework default; `review_mode`
unset in `.aidoc/profile.yaml`) · **Saga iteration:** 1 ·
**Generated:** 2026-06-10

## Summary

| Metric | Value |
|---|---|
| Findings in (audit v-current) | 18 (3 × P1, 8 × P2, 7 × P3) |
| Blocking (P1) resolved + lens-validated | 3 / 3 |
| P2 applied | 8 / 8 |
| P3 applied | 6 / 7 (1 deferred → manual queue) |
| Files created | 3 (this report + 2 validation slots) |
| Files modified | 1 (`docs/05_ADR/ADR-01.md`) |
| Regressions detected / reverted | 0 / 0 |

All three blocking P1 findings are resolved and confirmed by their responsible
review lenses with no new P0/P1 introduced. The gate-blocking trio
(CHAOS-ADR-01-001, SE-ADR-01-001, SE-ADR-01-002) is cleared. One P3 (cosmetic
cross-decision tag relabel) is deferred to the manual queue.

## Fixes Applied

| Code | Sev | Issue | Fix | Section | Confidence |
|---|---|---|---|---|---|
| CHAOS-ADR-01-001 | P1 | Synchronous-standby unavailability failure mode undecided | Added §3 **Failure semantics** clause: on standby loss the primary **halts** create-path writes (fail-closed on durability, RPO = 0 preserved), rejects silent async-degrade, emits a degraded-mode signal returning a bounded error tied to BDD.01.03.1f90; read path declared independent | §3 | auto-assisted (lens-validated) |
| SE-ADR-01-001 | P1 | AuthN axis never named for the PII-read principal | Added §3 **Access-control identity model**: API authenticates the caller (authN); app-tier identity maps to a per-call-path least-privilege DB role that the column/row grant is evaluated against | §3 | auto-assisted (lens-validated) |
| SE-ADR-01-002 | P1 | Identity-preservation across API→Store boundary silent | Same §3 clause: end-principal identity translated to a per-call-path DB principal (not one shared service principal) at the API→Store boundary; BDD permit/deny pair now realizable against a named mechanism | §3 | auto-assisted (lens-validated) |
| ARCH-ADR-01-001 | P2 | Reversibility described but not classified | Added §5 **Reversibility: two-way** labeled line (days-scale cost behind the Mapping Store interface; two-table migration + re-proof of RPO = 0) | §5 | auto-assisted |
| TL-ADR-01-001 | P2 | Redirect p95 criterion not satisfiable in decided scope | §8 criterion restated as PK-read within the no-cache MVP envelope; p95 < 50 ms marked jointly owned with BRD.01.08.66e2, verifiable once the cache lands | §8 | auto-assisted |
| CHAOS-ADR-01-002 | P2 | Visit-count increment semantics undeclared | Added §5 **Side-effect contract**: at-least-once with an idempotency/dedup key in the count table; dedup owned by BRD.01.08.c478 | §5 | auto-assisted |
| CHAOS-ADR-01-003 | P2 | Blast radius not classified | Added blast-radius labels (single-service / cross-service / data-loss-possible) to all §5 trade-offs + new ADR.01.05.5896 standby-loss entry (cross-service) | §5 | auto-safe |
| SE-ADR-01-003 | P2 | Encryption-at-rest of PII column unspecified | Added §5 ADR.01.05.98ff: at-rest encryption deferred to data-protection ADR (BRD.01.08.daeb) as a recorded **accepted risk** with interim compensating control (least-privilege grant + managed-tier volume encryption) | §5 | auto-assisted |
| SE-ADR-01-004 | P2 | Access-control grant failure mode (fail-closed/open) unstated | §3 clause states the read **fails closed** when the decision cannot be made; §8 adds a deny-on-grant-unavailable verification row | §3, §8 | auto-assisted |
| SE-ADR-01-005 | P2 | No explicit threat model for the PII control | Added §2 **Threat model (scope)**: mitigates over-broad principal read; at-rest encryption / backup confidentiality / erasure out of scope (owned by BRD.01.08.daeb) | §2 | auto-assisted |
| MERGED-OP-ADR-01-001-002 | P2 | PITR/backup health has no monitoring hook | Added §7 **PITR backup recency** hook (WAL > 1 h / base backup > 24 h) + periodic restore-probe signal; RTO claim (§2) tied to the chain | §7 | auto-assisted |
| CHAOS-ADR-01-004 | P3 | Detection signals lacked time bounds | §7 monitoring baseline: each signal now carries a detection-time bound (standby ≤ 30 s, commit lag ≤ 60 s, p95 over a 5-min window) as a fraction of the 30-min RTO | §7 | auto-safe |
| CHAOS-ADR-01-005 | P3 | Create-path stall retry-storm potential | §7 rollback/decision: write/read connection-pool isolation + fail-fast create-path timeout so a stalled standby cannot starve reads (cross-ref'd from §5 5896) | §5, §7 | auto-assisted |
| SE-ADR-01-006 | P3 | Rollback export of PII tables names no confidentiality control | §7 rollback: export inherits access/at-rest controls (encrypted, least-privilege, secure-deleted; params owned by BRD.01.08.daeb) | §7 | auto-assisted |
| OP-ADR-01-003 | P3 | Synchronous-mode config knob unnamed | §7 monitoring **config-drift** hook on `synchronous_commit` (named param + drift alert) — the standalone runtime-config paragraph was folded into the monitor for word-budget (see Notes) | §7 | auto-assisted |
| OP-ADR-01-004 | P3 | Rollback omits production-step ordering | §7 rollback: three-step ordered outline (drain → export+verify → re-point + confirm RPO = 0) | §7 | auto-assisted |
| OP-ADR-01-005 | P3 | No deployment-ordering constraint across siblings | §10 **Deployment ordering** note: store provisioning + health checks gate all five sibling ADR deployments | §10 | auto-assisted |

New element IDs derived (section+content hash per ID_NAMING_STANDARDS):
`ADR.01.05.5896` (standby-loss risk), `ADR.01.05.98ff` (encryption-at-rest
deferral).

## Validation Slots index

| Lens | Slot | lens_score | P1 findings validated | New P0/P1 |
|---|---|---|---|---|
| security_engineer | `security_engineer.fix_1.json` | 88 | SE-ADR-01-001 ✅, SE-ADR-01-002 ✅ | none |
| chaos_engineer | `chaos_engineer.fix_1.json` | 91 | CHAOS-ADR-01-001 ✅ | none |

Both responsible lenses returned `BRANCH_COMPLETED` with zero new P0/P1 on the
patched regions; no patch was reverted. Saga: both branches transitioned
`BRANCH_COMPLETED → BRANCH_COMPENSATING → BRANCH_COMPLETED`; run
`status: BRANCH_COMPLETED`.

## Manual-Review Queue

| Code | Sev | Why deferred |
|---|---|---|
| TL-ADR-01-002 | P3 | Replace §10 BRD refs with provisional cross-decision tag placeholders. Deferred: the sibling decisions are not yet authored, and writing a literal self-tag / doc-id placeholder token in prose trips the trace-tag linter (ID01/ID02). Revisit once the five sibling topics are assigned real decision IDs. Cosmetic, non-gate-blocking. |

## Out-of-scope (not an ADR content finding)

- **32 × `[ERROR TRACE-RES-001]`** — `@ears`/`@bdd` trace tags report host
  documents `EARS-01` / `BDD-01` as unresolvable. These tag lines were **not
  touched by this fixer** (verified byte-identical against the pre-edit backup;
  only line numbers shifted from prose inserts), and the upstream audit reported
  **structural PASS** for them. This is the active **TRACE-RES-FIXUP-001** branch
  work, not an ADR content remediation. Left for that workstream.

## Validation After Fix

| Dimension | Before | After |
|---|---|---|
| Blocking P1 (unresolved) | 3 | 0 |
| Content score (audit) | 85 / 100 (capped by P1s) | re-score pending re-audit |
| Structural gate (sdd_doc_lint) | PASS¹ | STY02/STY03 introduced during editing then resolved; document now within the ADR ≤ 2250-word body cap; 32 pre-existing TRACE-RES-001 remain (out of scope) |
| Lens scores (patched regions) | sec 74 / chaos 78 | sec 88 / chaos 91 |

¹ Per the audit report's deterministic gate (structural_status PASS). The
TRACE-RES-001 host-resolution errors are a property of the
TRACE-RES-FIXUP-001 working tree, surfaced by the post-edit lint hook, not by
the ADR audit.

### Notes on editing discipline

The first-pass patch packed every advisory finding into §3/§5/§7 and tripped
**STY02** (oversized §3 then §5) and **STY03** (document body > 2250-word ADR
cap). Per Phase 7, oversized sections were split to their natural homes
(threat-model → §2; reversibility + visit-count contract → §5) and the advisory
prose was compressed so the 3 P1 + 8 P2 fixes land within the structural budget.
No existing decision, context, or alternatives content was deleted; only new
clauses were inserted or relocated.

## Cleanup Summary

No prior `ADR-01.F_fix_report_v*.md` existed; nothing superseded. This is v001.

## Next Steps

Re-run **`/aidoc-flow:doc-adr-audit`** (saga iteration 1 → re-review phase) to
re-score the content gate and confirm the three P1 findings clear. Expected:
P1 = 0; content score back above the 90 threshold once the P1 caps lift. The
TRACE-RES-001 structural errors are tracked separately under TRACE-RES-FIXUP-001.
