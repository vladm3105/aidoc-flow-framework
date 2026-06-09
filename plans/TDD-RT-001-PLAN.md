# TDD-RT-001 Implementation Plan

> Combined plan + impl PR per established per-layer rollout pattern (mirrors EARS-RT-001 + BDD-RT-001 + ADR-RT-001 + SPEC-RT-001).

**Goal:** Wire team-mode fan-out into `doc-tdd-audit` + `doc-tdd-fixer` SKILLs, add playbook injection, author 6 TDD playbooks, validate via live TDD cascade.

**Architecture:** Mechanical replication of the SPEC-RT-001 pattern for the TDD layer (Layer 7). Framework spec contract from LAYER-PLAYBOOKS-001 unchanged; only TDD-specific configuration + content lands. **All four infrastructure defects discovered during SPEC-RT-001 are now fixed on main** (STY03 fence-fix PR #110, SAGA-BUDGET-001 PR #111, synthesizer-schema + saga-events PR #115, SAGA-DETERMINISM-001 PR #117), so this rollout should be the cleanest per-layer landing yet.

**Design authority:** `plans/LAYER-PLAYBOOKS-001-DESIGN.md` + `platforms/claude-code-plugin/skills/doc-spec-audit/SKILL.md` (SPEC-RT-001 template — freshest reference).

---

## TDD crew (from `framework/governance/REVIEW_CREWS.yaml`)

```yaml
TDD:
  author: qa_lead
  review: {qa_lead: 35, tech_lead: 25, chaos_engineer: 10, security_engineer: 10, operator: 10, auditor: 10}
```

Sum: 100. Rationale (per file comment): "Equal split (10 / 10) — security_engineer co-owns SECTEST per its agent brief; failure-test cases balance security-test cases."

6 lenses — same headcount as BDD/ADR but with the equal chaos/security split (vs BDD's chaos-heavy 14/6 and ADR's security-heavy 12/8).

## Lens → plugin agent mapping

| Lens | Weight | Agent | Note |
|---|---|---|---|
| `qa_lead` | 35 | `test-architect` | TDD author + lens |
| `tech_lead` | 25 | `solutions-architect` | |
| `chaos_engineer` | 10 | `chaos-engineer` | equal-weight split |
| `security_engineer` | 10 | `security-engineer` | equal-weight split; co-owns SECTEST |
| `operator` | 10 | `devops-release-engineer` | |
| `auditor` | 10 | `traceability-auditor` | |

---

## File structure

### Modified

| Path | Change |
|---|---|
| `platforms/claude-code-plugin/skills/doc-tdd-audit/SKILL.md` (268 → ~500 lines) | Add §Review Mode (team + single_pass), §Saga interaction, §Break-circuit policy, playbook injection step 3a + augmented step 4 |
| `platforms/claude-code-plugin/skills/doc-tdd-fixer/SKILL.md` (112 → ~300 lines) | Add §Remediate Mode (team + single_pass), §Saga interaction, §Break-circuit policy |
| `CHANGELOG.md` (root) | `[Unreleased]` entry for framework 0.15.1 → 0.15.2 + plugin 0.11.0 → 0.12.0 |
| `ROADMAP.md` | Shipped bullet (if applicable) |
| `plans/HANDOFF.md` | Dated narrative |
| `docs/PARITY.md` | Layer Playbooks row extended to BRD/PRD/EARS/BDD/ADR/SPEC/TDD |
| `docs/TAGGING.md` | New row for `claude-code-plugin/v0.12.0` |
| `framework/VERSION` | 0.15.1 → 0.15.2 (PATCH — TDD playbooks under framework/) |
| `platforms/claude-code-plugin/VERSION` | 0.11.0 → 0.12.0 (MINOR — new layer wiring) |
| `tests/conformance/platforms/test_plugin_release_metadata.py` | Hardcoded "0.15.1" → "0.15.2" |

### Created

| Path | Lens / Weight |
|---|---|
| `framework/playbooks/07_TDD/qa_lead.md` | 35 |
| `framework/playbooks/07_TDD/tech_lead.md` | 25 |
| `framework/playbooks/07_TDD/chaos_engineer.md` | 10 |
| `framework/playbooks/07_TDD/security_engineer.md` | 10 |
| `framework/playbooks/07_TDD/operator.md` | 10 |
| `framework/playbooks/07_TDD/auditor.md` | 10 |

---

## Implementation sequence

### Task 1: Author 6 TDD playbooks

Hybrid content shape per `framework/governance/REVIEW_TEAM.md` §Playbooks. ~95-110 lines each. Per-lens content topics (derived from TDD-layer concerns: test-case coverage, assertion specificity, fixture independence, failure-mode test parity, security-test parity, observability hooks, traceability):

**qa_lead (35, test-architect)** — Test-suite integrity lens (TDD author).

- C1: Every BDD scenario has at least one paired test case. Missing → P1 citing C1.
- C2: Each test case carries (name, AAA structure, deterministic seed/clock, one assertion-cluster). Missing → P2 citing C2.
- C3: Test parameters use explicit bounds, not "small" / "large". Missing → P2 citing C3.
- C4: Negative tests cover documented error paths. Missing → P2 citing C4.
- C5: Test names self-describe (read like a sentence). Missing → P3 citing C5.

**tech_lead (25, solutions-architect)** — Implementability + drift lens.

- C1: Tests bind to interface contracts from SPEC (not to internal class names). Drift → P1 citing C1.
- C2: Fixture setup/teardown idempotent + isolated (no shared mutable state). Missing → P2 citing C2.
- C3: Concurrency tests use deterministic primitives (no `sleep(2)`). Flaky → P2 citing C3.
- C4: External-dependency tests marked + use a single mocking strategy (per project convention). Mixed → P3 citing C4.
- C5: Tests for retry semantics actually exercise idempotency, not just retry count. Missing → P3 citing C5.

**chaos_engineer (10, chaos-engineer)** — Failure-mode test lens.

- C1: Every BDD chaos scenario has a paired TDD test asserting the recovery condition. Missing → P1 citing C1.
- C2: Saturation / load / overload tests target SPEC's NFR bounds (not arbitrary numbers). Missing → P2 citing C2.
- C3: Network-partition / timeout / dependency-failure tests use injectable fault primitives. Missing → P2 citing C3.
- C4: Recovery-time assertions reference SPEC's MTTR bound. Missing → P3 citing C4.
- C5: Failure-test isolation prevents cross-test contamination. Missing → P3 citing C5.

**security_engineer (10, security-engineer)** — Security-test lens (co-owns SECTEST).

- C1: Every BDD authn/authz scenario has a paired TDD security test. Missing → P1 citing C1.
- C2: Input-fuzzing tests cover every SPEC-named public interface. Missing → P2 citing C2.
- C3: Audit-event tests verify field set, not just emission. Missing → P2 citing C3.
- C4: Crypto tests assert algorithm + mode + key handling, not just call success. Missing → P3 citing C4.
- C5: Failure-closed default tests fire under control unavailability. Missing → P3 citing C5.

**operator (10, devops-release-engineer)** — Observability + test-flow lens.

- C1: Tests for SLO-relevant operations emit the SPEC-named metric/log/trace. Missing → P2 citing C1.
- C2: Smoke / canary / rollback tests exist for each ADR-named one-way decision. Missing → P2 citing C2.
- C3: Test-suite runtime characterized (`pytest --durations=N` benchmarks per suite). Missing → P3 citing C3.
- C4: Flake-rate budget declared per test class. Missing → P3 citing C4.
- C5: CI failure-mode tests (network outage, registry timeout) covered. Missing → P3 citing C5.

**auditor (10, traceability-auditor)** — Upstream-trace + ID-conformance lens.

- C1: Every `@bdd: BDD.NN…` / `@spec: SPEC.NN…` / `@ears: EARS.NN…` tag in the TDD resolves to an existing upstream element. Broken → P1 citing C1.
- C2: Test-case IDs conform to `TDD.NN.SS.xxxx` 4-hex content-hash pattern. Non-conformant → P1 citing C2.
- C3: Each row in the test-coverage matrix has a paired body test case. Orphan → P2 citing C3.
- C4: Cumulative `@bdd: / @spec: / @ears:` header at the doc level resolves cleanly. Missing → P2 citing C4.
- C5: Cross-TDD `@tdd:` references use correct form (dash for doc-level, dotted for element-level). Wrong form → P3 citing C5.

Beyond-checklist escape per playbook (template): one paragraph naming the kinds of issues that fall outside the Cn checks.

### Task 2: Wire team-mode into `doc-tdd-audit/SKILL.md`

Adopt the SPEC-RT-001 audit-wiring pattern (PR #118 commit `a59cc5d7`). Add four new sections + extend Frontmatter `adapts`:

- `## Review Mode` (team default at gates; single_pass fallback)
- `## Saga interaction` (entry / fan-out / break-circuit / reduce / standalone / single_pass)
- `## Break-circuit policy` (1500s SOFT_DEADLINE)
- Step 3a — playbook resolution: `framework/playbooks/07_TDD/<lens>.md` → `BRANCH_FAILED` if missing
- Step 4 — playbook inlined into per-lens Task brief; uncited findings discarded by synthesizer
- Frontmatter `adapts: [section_toggles, active_layers, audit_threshold]` → append `review_mode`

### Task 3: Wire team-mode into `doc-tdd-fixer/SKILL.md`

Adopt the SPEC-RT-001 fixer-wiring pattern (PR #118 commit `c49fc448`):

- `## Remediate Mode` (team-mode patch-validation for P0/P1; deterministic for P2/P3; single_pass fallback unchanged)
- `## Saga interaction` (FANIN_REDUCED → BRANCH_COMPENSATING for P0/P1 → CLOSED or ESCALATED)
- `## Break-circuit policy` (1500s SOFT_DEADLINE)
- Frontmatter `adapts: [section_toggles]` → `[section_toggles, review_mode]`

### Task 4: Bump versions UPFRONT

EARS-RT-001 lesson applied:

- `framework/VERSION` 0.15.1 → 0.15.2 (PATCH)
- `platforms/claude-code-plugin/VERSION` 0.11.0 → 0.12.0 (MINOR)
- `tests/conformance/platforms/test_plugin_release_metadata.py` "0.15.1" → "0.15.2"
- `bash scripts/sync-version-refs.sh` propagates
- `bash tools/sync-plugin-framework.sh` mirrors canonical → vendored
- New row in `docs/TAGGING.md` for `claude-code-plugin/v0.12.0`

### Task 5: Live TDD cascade

`bash tests/scripts/test-acceptance.sh url-shortener --live --phase=cascade --from-layer=tdd --to-layer=tdd`

Expected: TDD-01.md drafted from upstream BRD/PRD/EARS/BDD/ADR/SPEC; 6-lens fan-out per audit; convergence to PASS within 2-3 iter cycles. Wall-clock budget: 5400s (SAGA-BUDGET-001). Score gate: ≥ 90. **Run from the worktree at `/opt/data/aidoc-flow/framework-tdd-rt-001/`** (worktree-isolation pattern from SPEC-RT-001).

Acceptance criteria per the established pass-criteria pattern:

1. All 6 TDD slot files at `.aidoc/review/07_TDD/<TDD-id>/{qa_lead,tech_lead,chaos_engineer,security_engineer,operator,auditor}.json` present
2. `verdict.json` `combined_status: PASS` with `content_score >= 90` and `coverage.quorum_met: true`
3. `report.md` + `07_TDD-audit.md` present
4. **`saga.json` `status: CLOSED`** (clean terminal; PR #117 reconcile_post_audit will backfill if SKILL skips per-branch stamping)
5. **`saga.events[]` records full lifecycle** (PR #115 instrumentation)
6. **Every committed finding cites a Cn check or `beyond-checklist:` tag** (PR #115 contract)
7. `sdd_doc_lint` on `docs/07_TDD/TDD-01.md` exits 0

### Task 6: Doc-of-record + open PR

Update + commit CHANGELOG, HANDOFF, docs/PARITY.md, docs/TAGGING.md, cascade evidence (`docs/07_TDD/`, `.aidoc/review/07_TDD/`, `.aidoc/audit/07_TDD-audit.md`), `.secrets.baseline` if saga.json fingerprint triggers detect-secrets. Push branch + open PR citing verdict.json + cascade evidence.

---

## Out of scope (deferred)

- IPLAN-RT-001 (task #268)
- Final `@unittest.skip` removal from `test_playbook_coverage.py` (task #258 — happens with the IPLAN-RT-001 PR or a separate cleanup PR)
- Hermes mirror (deferred per `plans/HERMES-BACKLOG.md`)
- CLAUDE.md "Current state" plugin-version sync (pre-existing doc-of-record gap)

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| TDD draft fails because no upstream SPEC-01.md on the example | Verify `examples/url-shortener/docs/06_SPEC/SPEC-01.md` is present on main (it is, post-PR #118). Cascade upstream-check (phase 0) catches anyway. |
| Audit SKILL stochastically skips per-branch transition stamping (same bug as SPEC) | PR #117's `reconcile_post_audit` backfills missing transitions and walks `saga.status` deterministically — bug class is now closed. |
| Synthesizer drops `findings[*].check` (same bug as SPEC) | PR #115's `agents/synthesizer.md` contract is explicit; `test_synthesizer_verdict_schema.py` conformance test enforces. |
| Saga timeout | PR #111's 5400s budget is comfortable headroom (SPEC used 50:42; ADR used 43:48; TDD likely similar). |
| Branch-confusion from concurrent session | Worktree-isolation pattern: cascade runs from `/opt/data/aidoc-flow/framework-tdd-rt-001/` pinned to `feat/tdd-rt-001`; git enforces one-branch-one-worktree. |
| `qa_lead` lens binds to `test-architect` agent (also serves BDD) | Established pattern at BDD layer; works fine. |

## Review log

### Pass 1 — 2026-06-09 — self-review

1. **REVIEW_CREWS.yaml TDD row unchanged** — TDD crew was declared at 0.12.0 (CHAOS-SEC-SPLIT-001). Plan does NOT modify. ✓
2. **saga_driver.py already declares `07_TDD` crew** (qa_lead/tech_lead/chaos_engineer/security_engineer/operator/auditor). ✓
3. **6-lens crew same shape as BDD/ADR** — different weights (TDD: equal chaos/security 10/10 vs BDD: chaos-heavy 14/6 vs ADR: security-heavy 12/8). ✓
4. **qa_lead also authors BDD** — established cross-layer pattern; brief specifies which lens at dispatch time. ✓
5. **operator lens checks observability hooks** at TDD altitude — measures that SPEC-named metrics/logs/traces are actually emitted by the tested code paths. Distinct from BDD's operator which checks scenario assertion observability. ✓
6. **security_engineer C1 says "every BDD authn/authz scenario has a paired TDD security test"** — TDD lives downstream of BDD; cross-layer trace expected. ✓
7. **Auditor C2 says `TDD.NN.SS.xxxx`** — confirmed conformant to ID_NAMING_STANDARDS. ✓
8. **Plan VERSION bump** — framework PATCH 0.15.1→0.15.2 + plugin MINOR 0.11.0→0.12.0. Mirrors precedent. ✓
9. **Worktree at `/opt/data/aidoc-flow/framework-tdd-rt-001/`** — already set up; pinned to feat/tdd-rt-001. ✓
10. **Four infrastructure PRs from SPEC-RT-001 already merged** — TDD rollout starts with a clean infrastructure foundation. ✓
11. **6 playbooks vs 5 SPEC playbooks** — one extra file but each layer's content is independent; no cross-layer integration concerns. ✓

Pass 1: 11 confirmations / clarifications. No substantive gaps.

### Pass 2 — 2026-06-09 — re-review

1. **Pass 1 finding 5 (operator vs BDD operator)** — verified by re-reading BDD operator playbook on main. BDD operator C1 was about scenario-level observability assertions; TDD operator C1 is about test-time emission verification. Distinct concerns, no overlap. ✓
2. **chaos_engineer C1 cross-layer link** — TDD chaos test pairs with BDD chaos scenario. Same pattern as security_engineer C1. ✓
3. **TDD upstream chain: BRD/PRD/EARS/BDD/ADR/SPEC** — TDD inherits all 6 upstream layers, longest chain. ✓
4. **References to recent PRs** — STY03 #110, SAGA-BUDGET #111, BDD-RT #112, ADR-RT #113, synth-schema #115, SAGA-DETERMINISM #117, SPEC-RT #118 — all merged. ✓
5. **6-lens crew + 6 playbook files** — match. ✓

Pass 2 verdict: zero new substantive gaps. Plan ready.
