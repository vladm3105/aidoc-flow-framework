# CHG-01 — Fix Report (fix iteration 2)

/ aidoc-flow:doc-chg-fixer · team mode · standalone (user-invoked) ·
2026-06-12 (America/New_York)

## Summary

| Field | Value |
|-------|-------|
| Artifact | CHG-01 — Add visit-rate analytics dashboard (`docs/09_CHG/CHG-01.md`) |
| Audit consumed | `.aidoc/audit/09_CHG-audit.md` (fresh team-mode re-audit, saga iteration 2) |
| Review mode | team (gate default; no project `review_mode` override in `.aidoc/profile.yaml`) |
| Saga entry status | `BRANCH_COMPLETED` (skill expected `FANIN_REDUCED`/`BRANCH_FAILED` — warning logged, proceeded standalone) |
| Fix iteration | 2 |
| Issues in | 14 (1 P1 · 8 P2 · 5 P3) |
| Issues fixed | 14 of 14 (1 P1 + 8 P2 + 5 P3) |
| Issues remaining | 0 blocking (P0/P1) |
| Files modified | 1 (`docs/09_CHG/CHG-01.md`) |
| Files created | 2 (this report + 1 patch-validation slot `integration_lead.fix_2.json`) |
| **Gate-readiness after fix** | **`gate_ready: true`** (pending re-audit confirmation) |

The single blocking finding (IL-1, P1) was an EARS→BDD propagation-seam gap on
the hot redirect path. It and the related P2 (IL-2, owner-identity
authentication requirement) were resolved by authoring the missing §3 cascade
rows; the IL-1 patch was lens-validated for non-regression by its responsible
lens (`integration_lead`), which returned `validated: true` (score 95) with no
new P0/P1. The remaining P2/P3 advisory findings were applied deterministically.
Because the patches grew the body toward the **+50% size-promotion line**
(2 250 prose words), a compensating compression pass on §2 and §7.2 (the trims
the audit explicitly invited) kept the size finding **advisory**, not Tier-1
blocking.

## Fixes Applied

| Code | Sev | Issue | Fix | Section | Confidence |
|------|-----|-------|-----|---------|------------|
| **IL-1** | P1 | EARS declared 2 new requirements but §3 BDD row named only 1 scenario — the on-redirect visit-rate-computation requirement (critical hot-path hop) had no BDD scenario; EARS→BDD broken | Added a dedicated **on-redirect visit capture** BDD scenario (*Given a redirect …, Then a visit timestamp is captured async off the redirect path and the redirect is not blocked*) to the §3 BDD row, and carried **on-redirect async-capture non-blocking behavior** into the TDD-02 row — EARS→BDD→TDD chain unbroken | §3 BDD (L4) + TDD (L7) rows | auto-assisted |
| **IL-2** | P2 | Owner-identity **authentication** requirement never propagated as EARS/BDD — only downstream authz covered; trust boundary appeared at ADR/SPEC altitude with no upstream requirement | Added a third EARS requirement (**owner-identity establishment** — ownership bound at shorten time, owner authenticated before a dashboard query) + a paired BDD scenario, carried into TDD-02 (authentication-binding tests). ADR-02 decision routing left unchanged | §3 EARS/BDD/TDD rows | auto-assisted |
| **CE-1** | P2 | Async on-redirect capture asserted as a closed mitigation but never failure-analyzed; backpressure/overflow and the "write failure non-fatal to redirect" contract stated nowhere | Added **Async-capture failure analysis**: bounded-buffer overflow → drop-and-count-loss (never re-couple/block the redirect); explicit **non-fatal contract** (`VisitCountRecord` still increments, only the rolling-window timestamp is lost) | §3 failure-mode delta | auto-assisted |
| **CE-2** | P2 | §7.2 abort sequence quiesced only the reader; the on-redirect **writer** kept firing through snapshot + drop → non-quiescent snapshot, store dropped under a live write path | Inserted a new step 2 — **stop the on-redirect timestamp writer** (flip capture flag off, drain in-flight async writes) before snapshot/drop; hot path falls back to count-only so the table is quiescent | §7.2 abort sequence | auto-assisted |
| **OP-1** | P2 | Async on-redirect write path had no named observability signal — silent writer failure leaves stale/zero dashboards with no alert | Added a 4th observability intent — **error/drop-rate on the async on-redirect write** (owner SPEC-02/IPLAN-02) | §4.1 Observability | auto-assisted |
| **OP-2** | P2 | Canary abort threshold named but the telemetry **source** the operator watches was not identified at CHG altitude | Named the abort-decision signal sources — metrics error-rate (1), dashboard p95/error-rate (2), async-write drop-rate (4); numeric thresholds defer to IPLAN-02 | §4.1 Deployment posture | auto-assisted |
| **AU-1** | P2 | §6 did not name the post-implementation **re-gate path** / cross-reference §5's per-layer re-validation | Added §6 condition **C4** — each affected layer re-validated via `doc-<layer>-audit` (§5 final row); the change closes only when that passes (single formal re-gate path) | §6 Gate Approval | auto-assisted |
| **AU-2** | P2 | §4.1 marked readiness links "before GATE-01" while §5 marked artifacts "after GATE-01" — ambiguous whether they are approval blockers or post-approval intent | Added §6 conditions **C1** (collateral is an approval input, authored before sign-off) + **C3** (two-phase timing: collateral precedes GATE-01; the 8-layer cascade re-audits after) — reconciled | §6 + §4.1 preamble | auto-assisted |
| **SE-1** | P2 | First-authz-boundary deferral to ADR-02 lacked an **explicit** "no surface ships before ADR-02 is approved" gate condition; bound only implied by §4 ordering | Added §6 condition **C2** — no dashboard/owner-authz/retained-data surface ships until **ADR-02 is approved at ADR altitude**; GATE-01 (business gate) does not substitute | §6 Gate Approval | auto-assisted |
| **IL-3** | P3 | §4 "Artifacts modified/created" table omitted ADR-01 and SPEC-01 (boundary-affected in §3/frontmatter) | Added ADR-01 + SPEC-01 rows marked **boundary-impact (no edit)** with delta-owner note — table now a complete index of affected IDs | §4 artifacts table | auto-safe |
| **CE-3** | P3 | "RPO = last snapshot" silently excluded timestamps buffered-but-unflushed in the async layer (lost on crash) | Added the exclusion note to the RTO/RPO posture — acceptable-loss class (metric accuracy, not availability), called out so it is not silently excluded | §7.2 RTO/RPO | auto-safe |
| **OP-3** | P3 | Dashboard feature-flag claimed for independent disable, but its default state at deploy was not declared | Declared **default state at deploy is OFF** (enabled after promotion), so rollback step 1 is an actionable disable, not a no-op | §4.1 Deployment posture | auto-safe |
| **SE-2** | P3 | Abuse-case enumeration was three-of-five — parameter/query-string injection and replay not named in SPEC-02/TDD-02 routing | Added **window-bound + owner-selector input validation against injection, and request replay rejection** to the SPEC-02 controls and TDD-02 abuse-case pairs | §3 SPEC-02 + TDD-02 rows | auto-safe |
| **SE-3** | P3 | At-rest protection for the new may-contain-PII path did not mirror ADR-01's named interim compensating control | Mirrored ADR-01's control for the same data class — **least-privilege DB grant + managed-tier volume encryption at rest** — so the new path is not protected to a weaker standard | §2 retained-data | auto-assisted |
| STY (size) | adv | Patches grew the body toward the +50% promotion line (2 250 prose words); audit advised trimming §2 and §7.2 | Compensating compression of §2 (six paragraphs) and §7.2 prose + table-cell tightening across §1/§3/§4.1/§5/§6 — no recorded content removed; body landed ≈ 2 232 prose words (≈ +48.8%, advisory, below the 2 250 blocking line) | §1–§8 prose | auto-safe |

## Manual-Review Queue

None blocking. Two items surfaced for human awareness (neither blocks gate-readiness):

1. **Approval / signature fields left blank by design** — `Date Approved`,
   `gate_approval.approver`, approval conditions C1–C4 sign-off are human
   decisions at `../gate-check/SKILL.md` (content-preservation rule). Not filled.
2. **Size-budget tension (advisory).** Even after compression the record sits at
   ≈ +48.8% over the 1 500-word CHG target — a genuine tension for a **C3
   cross-layer change touching 8 layers + Code** with rollback, gate conditions,
   operational readiness, and failure analysis. It is **below** the +50%
   blocking line, so the audit's size check stays advisory; if a future fix adds
   more content, the §3 ADR-02 cell and §4.1 are the next split/manual-required
   candidates per Fix Phase 7.

## Gate-Readiness After Fix

- **Before:** `gate_ready: false` — 1 unresolved P1 (**IL-1**).
- **After:** `gate_ready: true` — 0 unresolved P0/P1. Remaining blocking codes
  **{IL-1} → {}**. Structural gate floor remained **PASS** throughout (no
  schema / change-level / routing / conditional-block change; metadata
  unchanged). Size finding kept **advisory** (not promoted to Tier 1).
- No numeric score — CHG is a governance overlay, not a lifecycle layer. The bar
  is **gate approval**, not a score.

Final confirmation is a fresh `doc-chg-audit` re-run; only a re-audit returning
`gate_ready: true` authorizes the hand-off to GATE-01.

## Validation Slots index

Team-mode patch-validation outputs (one per responsible lens, fix-iteration 2).
IL-1 is a single-lens finding (`integration_lead`); IL-2 was validated in the
same dispatch. P2/P3 advisory findings were applied deterministically without
lens validation, per the skill.

| Finding | Persona | N | Slot | Lens score | Result |
|---------|---------|---|------|-----------|--------|
| IL-1 (+ IL-2) | integration_lead | 2 | `.aidoc/review/09_CHG/CHG-01/integration_lead.fix_2.json` | 95 | validated — il1_closed, il2_closed, no new P0/P1 |

Revert policy: a patch reverts only if a responsible lens returns a new P0/P1.
The IL-1 validator returned none, so no revert.

## Cleanup Summary

- CHG backup retained at `tmp/backup/CHG-01_20260612T092205/` for restore-on-error.
- Wrote this report to `.aidoc/remediation/09_CHG-fix.md` (per invocation path;
  sits alongside `01_BRD-fix.md` / `02_PRD-fix.md` / `03_EARS-fix.md`).
- Wrote validation slot `.aidoc/review/09_CHG/CHG-01/integration_lead.fix_2.json`.
- Retained prior `CHG-01.F_fix_report_v001.md` and the `*.fix_1.json` slots
  (fix-cycle history — kept per policy).
- **`saga.json` not transitioned.** This was a standalone, user-invoked fixer
  run; `saga.json` is at `BRANCH_COMPLETED` (iteration 2) and is owned by a prior
  autopilot run, not this invocation — consistent with the audit's same choice
  not to drive transitions on a non-autopilot-owned saga.

## Next Steps

1. **Re-run `../doc-chg-audit/SKILL.md`** to confirm `gate_ready: true` and that
   the patches introduced no new structural/size finding.
2. When the re-audit is clean, hand to **`../gate-check/SKILL.md`** to run
   **GATE-01** (C3) and complete the `GATE_APPROVAL_FORM` — the human C3 sign-off
   this skill never auto-grants.
3. Forward obligations to IPLAN-02 (author + link before GATE-01 is finalized):
   the §4.1 operational-readiness collateral (incl. the new async-write
   observability signal) and the §7.2 down-migration / writer-quiesce script.

---

*The `*.fix_2.json` slot is the authoritative patch-validation record; this
report is its human narrative mirror.*
