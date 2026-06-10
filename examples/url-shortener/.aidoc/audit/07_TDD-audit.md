# TDD-01.A — Combined Audit Report (iteration 2 re-review)

## Summary

| Field | Value |
|-------|-------|
| Artifact | TDD-01 — Link Store (`docs/07_TDD/TDD-01.md`, v1.0.1) |
| Layer | 07_TDD |
| Seed (parent SPEC) | SPEC-01 v1.0.1 (`docs/06_SPEC/SPEC-01.md`) |
| Audit timestamp | 2026-06-10T13:49Z |
| Review mode | `team` (profile override-only → framework default `team` at gate) |
| Saga iteration | 2 (re-review after fixer iteration 1) |
| **Combined status** | **FAIL** (content score 89 < threshold 90; borderline −1) |
| Structural status | **PASS** (lint exit 0; 30 conformant IDs; metadata valid) |
| Content score | **89 / 100** (advisory; threshold 90) |
| Coverage quorum | **met** (6 / 6 lenses returned) |
| Blocking findings (P0/P1) | **0** |
| Advisory findings | 6 P2 + 2 P3 = 8 |

`combined_status` mirrors `.aidoc/review/07_TDD/TDD-01/verdict.json` (the
authoritative synthesizer verdict). The deterministic structural floor PASSES
and there are **zero blocking findings**; the FAIL is driven solely by the
advisory content score landing one point under the 90 gate — consistent with
this saga's iteration-1 methodology (content 84 with 0 blocking → FAIL).

## Score Calculation

Weighted average of per-lens scores using the TDD crew weights
(`REVIEW_CREWS.yaml`, sum = 100):

| Lens | Agent | Weight | lens_score | Contribution |
|------|-------|-------:|-----------:|-------------:|
| qa_lead | test-architect | 35 | 84 | 29.40 |
| tech_lead | solutions-architect | 25 | 100 | 25.00 |
| chaos_engineer | chaos-engineer | 10 | 88 | 8.80 |
| security_engineer | security-engineer | 10 | 86 | 8.60 |
| operator | devops-release-engineer | 10 | 90 | 9.00 |
| auditor | traceability-auditor | 10 | 85 | 8.50 |
| **Weighted total** | | **100** | | **89.30 → 89** |

Cap rule: 0 P0, 0 P1 → no cap applied; score stands at **89**. Compare to
threshold **90** → **below by 1**.

## Metadata Findings

None. `document_type: tdd-document` ✓ · `artifact_type: TDD` ✓ · `layer: 7` ✓
· `deliverable_type: code` ✓. No VALID-M001/M002/M003.

## Structural Findings

Structural floor **PASS** (`sdd-doc-lint` exit 0).

| Check | Result |
|-------|--------|
| Template-conformance (7 required sections §1–§7) | PASS — all present, non-empty |
| Element ID format `TDD.01.04.xxxx` (4-hex) | PASS — 30/30 conformant, no duplicates |
| Test types | PASS — every case carries a valid type (unit/integration/e2e/security/performance/smoke) |
| BDD mapping | PASS — 8/8 Link-Store BDD scenarios mapped in §3 |
| Necessary-upstream tags `[ears, bdd, adr, spec]` | PASS — all present (NECESSARY-UPSTREAM-001, spec 0.16.0+; PRD/BRD transitive) |
| Parent SPEC `@spec: SPEC-01` | PASS — resolves; SPEC-01 exists |
| Quality gate (score ≥ 90) | **FAIL** — content score 89 |

**Advisory (Tier 2 — non-blocking):** two STY02 size warnings — §4 Test Cases
1074 words (target ≤ 500) and §5 Thresholds 319 words (target ≤ 200). Not
promoted to blocking: the lint classifies both WARNING/exit 0, the document
stays under the binding STY03 doc-body ceiling (≈2245/2250), and the TDD
template mandates exactly seven numbered sections, so §4 cannot be split into
subsections. Documented as the accepted cost of the iteration-1 coverage
expansion (21 → 30 cases). No remediation expected at TDD scope.

## Content Findings

Reduced from the 6 per-lens slots (see Persona Slot Index). All findings cite a
playbook check; 0 discarded.

### P2 — advisory (6)

| Code | Lens | Check | Location | Issue → Recommendation |
|------|------|-------|----------|------------------------|
| QL-001 | qa_lead | C2 | §4 `TDD.01.04.af07` | Bundles a success-path flow (RPO=0, healthy adapter) and a failure-path flow (`StoreUnavailableError`, faulting adapter) under one case ID — distinct Arrange states, non-diagnosable at case-ID level. → Split into two cases; observability metric/span assertion lands in the success case; update §3 mapping. |
| QL-002 | qa_lead | C3 | §4 `TDD.01.04.24ff` | The `>200 ms` KMS key-unwrap sub-budget is unanchored — no EARS/PRD/SPEC source (SPEC §6 gives only the `EARS.01.03.f909` issuance budget, undecomposed). → Cite the source or re-express via the issuance budget and defer the concrete ms ceiling to IPLAN (same pattern already used for cipher-mode/KMS-ARN in this case). |
| CHAOS-001 | chaos_engineer | C1 | §3 `@bdd: BDD.01.03.f44a` / `TDD.01.04.7115` | `get`-path degradation is encoded **detection-only**; missing the Link-Store recovery half SPEC §5 names ("recovers when the store returns"). A latched read-failure could pass the suite. (Distinct from the out-of-scope Redirect Handler recovery `BDD.01.03.0759`.) → Add a paired recovery case: inject read fault → assert `StoreUnavailableError`; clear fault → assert `get` resolves the known record within the p95 budget. |
| SE-001 | security_engineer | C2 | §4 `cf05/54b8/1bc0` (get), `74e8/9528/ab25` (increment_visits) | Two public trust-boundary inputs unfuzzed: `get(code)` lacks encoding-edge/homoglyph fuzz (read-path key-confusion vs the claim path); `increment_visits(code, delta)` lacks `delta` fuzz (negative/zero/overflow breaks the monotonic `visit_count` contract). → Add a `get`-fuzz and an `increment_visits`-fuzz unit case mirroring the `8504/fc47` input matrix. |
| OP-001 | operator | C2 | §4 `@adr: ADR.01.03.f5f5` / ADR-01 §7 | Forward deploy-gate smoke (`d5d7`) present, but no non-prod **rollback-path** test for the one-way substrate runbook — ADR §7 step 7 requires an automated RPO=0 post-cutover probe, which `d5d7` cannot serve (it commits a fresh code on the live substrate, no pre-imported records). → Add a rollback-path smoke test (export → import-with-uniqueness → RPO=0 probe on the secondary instance); tag `@adr: ADR.01.03.f5f5`; add to the §5 smoke gate row. |
| AUD-001 | auditor | C4 | §1 line 30 (cumulative header) vs §3 / §7 | Cumulative upstream header lists only `@adr: ADR-01`, but the body/§7 cite six ADR element refs (`5c3c/1050/f5f5/3afa/9107`). The header is the traceability contract and must enumerate every cited element tag. Severity P2 (header incompleteness; all six refs **resolve** in ADR-01 — not a broken pointer). → Expand line 30 to list all element-level ADR refs. |

### P3 — advisory (2)

| Code | Lens | Check | Location | Issue → Recommendation |
|------|------|-------|----------|------------------------|
| OP-002 | operator | C1 | §4 `af07`/`840c`; SPEC §6 | SPEC §6 names "atomic-claim outcome" as a distinct emission point; `840c` asserts the write-conflict counter but no **per-outcome labelled** metric (`outcome=COMMITTED` / `outcome=CODE_TAKEN`) — the outcome distribution is dark in production. → Assert the outcome-labelled metric on `af07` (COMMITTED) and `82ff`/`840c` (CODE_TAKEN). |
| OP-003 | operator | C5 | §4 all classes; §5 | CI **pre-test-setup** failure modes uncovered (KV unreachable / KMS-vault credential-fetch timeout during bootstrap, before any test runs) — distinct from `24ff`'s in-operation KMS slowness. → Add a CI pre-condition probe that exits non-zero with a structured "infrastructure unavailable" vs "test failure" distinction, so flake-budget accounting attributes correctly. |

**No-finding lens:** tech_lead (solutions-architect) — `lens_score 100`. Confirmed
all cases bind to SPEC interface-catalog names (no implementation-private
symbols, C1), fresh function-scoped fixtures (C2), shared `asyncio.Event`
concurrency barriers with deterministic clock / no real sleep (C3), one
consistent fake-based mocking strategy (C4), and call-twice idempotency
assertions (C5).

## Coverage Findings

- **Per-type case counts:** unit 13, integration 7, security 3, e2e 4,
  performance 2, smoke 1 = 30 cases.
- **BDD → test:** 8/8 Link-Store BDD scenarios mapped (§3). Residual gap is
  *recovery-assertion depth* on the `get` path (CHAOS-001), not a missing
  scenario mapping.
- **SPEC alignment:** 4/4 `LinkStore` methods + 2/2 data models exercised;
  SPEC §6 resilience (load/overload/shed-order) and ADR.01.03.1050 security
  controls covered. Residual SPEC-§6 gaps: per-outcome claim metric (OP-002)
  and `get`/`delta` fuzz at the trust boundary (SE-001).
- **Trace resolution:** all emitted `@ears/@bdd/@adr/@spec/@brd` tags resolve
  in their upstream docs. `@threshold: PRD.01.perf.redirectp95` resolves
  transitively through SPEC §6 (PRD layer intentionally absent under the
  necessary-upstream contract); auditor raised no broken-pointer finding.

## Persona Slot Index

| Lens | Slot path | Score |
|------|-----------|------:|
| qa_lead | `.aidoc/review/07_TDD/TDD-01/qa_lead.json` | 84 |
| tech_lead | `.aidoc/review/07_TDD/TDD-01/tech_lead.json` | 100 |
| chaos_engineer | `.aidoc/review/07_TDD/TDD-01/chaos_engineer.json` | 88 |
| security_engineer | `.aidoc/review/07_TDD/TDD-01/security_engineer.json` | 86 |
| operator | `.aidoc/review/07_TDD/TDD-01/operator.json` | 90 |
| auditor | `.aidoc/review/07_TDD/TDD-01/auditor.json` | 85 |
| **synthesis** | `.aidoc/review/07_TDD/TDD-01/verdict.json` + `report.md` | 89 |

**Playbook coverage:** C1×2, C2×3, C3×1, C4×1, C5×1; beyond_checklist 0;
discarded 0. No >30% beyond-checklist drift.

**Coverage:** `quorum_met = true` (6/6). Verdict is full-confidence, not
low-confidence.

## Fix Queue (hand-off to doc-tdd-fixer)

All 8 findings normalized for the fixer. None blocking; all advisory but
score-depressing — a single focused fixer pass closing the 6 P2s reaches PASS
at iteration 3.

| Code | source | severity | confidence | file | section | action_hint |
|------|--------|----------|------------|------|---------|-------------|
| QL-001 | content | warning | auto-assisted | docs/07_TDD/TDD-01.md | §4 / §3 | Split `af07` into success-path + failure-path cases; re-map §3 |
| QL-002 | content | warning | auto-assisted | docs/07_TDD/TDD-01.md | §4 `24ff` | Re-express 200 ms via `EARS.01.03.f909`; defer ms ceiling to IPLAN |
| CHAOS-001 | content | warning | auto-assisted | docs/07_TDD/TDD-01.md | §4 / §3 | Add `get`-path recovery case (clear fault → resolve within p95) |
| SE-001 | content | warning | auto-assisted | docs/07_TDD/TDD-01.md | §4 | Add `get`-fuzz + `increment_visits(delta)`-fuzz unit cases |
| OP-001 | content | warning | auto-assisted | docs/07_TDD/TDD-01.md | §4 / §5 | Add non-prod rollback-path smoke (export/import/RPO=0 probe) |
| AUD-001 | content | warning | auto-safe | docs/07_TDD/TDD-01.md | §1 line 30 | Enumerate all 6 `@adr:` element refs in cumulative header |
| OP-002 | content | info | auto-assisted | docs/07_TDD/TDD-01.md | §4 | Assert per-outcome claim metric (`outcome=COMMITTED/CODE_TAKEN`) |
| OP-003 | content | info | auto-assisted | docs/07_TDD/TDD-01.md | §5 | Document CI pre-condition probe (infra-unavailable vs test-failure) |

- `auto_fixable`: AUD-001 (header enumeration — mechanical).
- `auto_assisted`: QL-001, QL-002, CHAOS-001, SE-001, OP-001, OP-002, OP-003.
- `blocked`/`manual_required`: none.

## Convergence Note

Iteration 1 (content 84; multiple stacked P2 clusters — granularity, observability,
load/shed, fault-determinism) → iteration 2 (content 89; 6 P2 + 2 P3). The
+5-point gain reflects the resolved iteration-1 clusters; tech_lead is now
clean (100). The residual P2s are **fresh fine-grained findings** visible only
once the larger clusters cleared (e.g. `af07` two-flow bundling surfaced after
the unit-layer splits; `get`-path recovery surfaced after the write-path
recovery pairs were added). This is normal convergence, not regression.

## Recommended Next Step

Hand off to **`doc-tdd-fixer`** (saga iteration 2 fix). Apply the 6 P2s (the
score-depressing set) plus the 2 P3s; expect PASS at the iteration-3 re-audit
(structural floor already green, 0 blocking, score 1 point under). Per the
no-hand-edit convention, the fixer — not a manual edit — applies these
lens-validated patches.

## Cleanup Summary

- Superseded the iteration-1 combined report in place
  (`.aidoc/audit/07_TDD-audit.md` overwritten). No stale
  `TDD-NN.A_audit_report_v*.md` copies exist to delete.
- Retained: `TDD-01.F_fix_report_v001.md`, all six lens slots (refreshed this
  iteration), `verdict.json`, `report.md`, `saga.json`.
- Saga journal advanced PREPARED → … → FANOUT_STARTED → BRANCH_COMPLETED ×6 →
  FANIN_REDUCED (iteration 2). No `PARTIAL_TIMEOUT` (elapsed 551 s < 1500 s
  soft deadline). No compensation branches.
