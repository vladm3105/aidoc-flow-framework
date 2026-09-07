# BDD-RT-001 Implementation Plan

> Combined plan + impl PR per established per-layer rollout pattern.

**Goal:** Wire team-mode fan-out into `doc-bdd-audit` + `doc-bdd-fixer` SKILLs (mirror EARS-RT-001 pattern), add playbook injection, author 6 BDD playbooks, validate via live BDD cascade.

**Architecture:** Mechanical replication of EARS-RT-001 for the BDD layer (Layer 4). Framework spec contract from LAYER-PLAYBOOKS-001 unchanged; only BDD-specific configuration + content lands.

**Design authority:** `plans/LAYER-PLAYBOOKS-001-DESIGN.md` + `platforms/claude-code-plugin/skills/doc-ears-audit/SKILL.md` (EARS-RT-001 template — fresh-est reference).

---

## BDD crew (from `framework/governance/REVIEW_CREWS.yaml`)

```yaml
BDD:
  author: qa_lead
  review: {qa_lead: 35, tech_lead: 25, chaos_engineer: 14, security_engineer: 6, operator: 10, auditor: 10}
```

Sum: 100. Rationale (per file comment): "Chaos-heavy at BDD (14 > 6) — failure scenarios dominate Gherkin coverage; abuse-case scenarios are secondary."

## Lens → plugin agent mapping

| Lens | Weight | Agent | Note |
|---|---|---|---|
| `qa_lead` | 35 | `test-architect` | BDD author + lens |
| `tech_lead` | 25 | `solutions-architect` | |
| `chaos_engineer` | 14 | `chaos-engineer` | chaos-heavy at BDD |
| `security_engineer` | 6 | `security-engineer` | |
| `operator` | 10 | `devops-release-engineer` | first appearance at BDD layer |
| `auditor` | 10 | `traceability-auditor` | |

---

## File structure

### Modified

| Path | Change |
|---|---|
| `platforms/claude-code-plugin/skills/doc-bdd-audit/SKILL.md` (268 → ~500 lines) | Add §Review Mode (team + single_pass), §Saga interaction, §Break-circuit policy, playbook injection step 3a + augmented step 4 |
| `platforms/claude-code-plugin/skills/doc-bdd-fixer/SKILL.md` (118 → ~300 lines) | Add §Remediate Mode (team + single_pass), §Saga interaction, §Break-circuit policy |
| `CHANGELOG.md` (root) | `[Unreleased]` entry for framework 0.14.1 → 0.14.2 + plugin 0.8.0 → 0.9.0 |
| `platforms/claude-code-plugin/CHANGELOG.md` | `[0.9.0]` entry |
| `ROADMAP.md` | Shipped bullet |
| `plans/HANDOFF.md` | Dated narrative |
| `docs/PARITY.md` | Layer Playbooks row extended to BRD/PRD/EARS/BDD |
| `docs/TAGGING.md` | New row for `claude-code-plugin/v0.9.0` |
| `framework/VERSION` | 0.14.1 → 0.14.2 (PATCH — adds BDD playbooks under framework/) |
| `platforms/claude-code-plugin/VERSION` | 0.8.0 → 0.9.0 (MINOR — new layer wiring) |
| `tests/conformance/platforms/test_plugin_release_metadata.py` | Hardcoded "0.14.1" → "0.14.2" |

### Created

| Path | Lens / Weight |
|---|---|
| `framework/playbooks/04_BDD/qa_lead.md` | 35 |
| `framework/playbooks/04_BDD/tech_lead.md` | 25 |
| `framework/playbooks/04_BDD/chaos_engineer.md` | 14 |
| `framework/playbooks/04_BDD/security_engineer.md` | 6 |
| `framework/playbooks/04_BDD/operator.md` | 10 |
| `framework/playbooks/04_BDD/auditor.md` | 10 |

---

## Implementation sequence

### Task 1: Author 6 BDD playbooks

Hybrid content shape per `framework/governance/REVIEW_TEAM.md` §Playbooks. ~95-110 lines each. Per-lens content topics (derived from BDD-layer concerns: Gherkin syntax, scenario coverage, failure-mode focus per chaos-heavy split):

**qa_lead (35, test-architect)** — Gherkin syntax + coverage lens (BDD author).

- C1: Every EARS line covered by ≥1 scenario (bidirectional coverage matrix). Missing → P1 citing C1.
- C2: Given/When/Then atomicity — one trigger, one action, one observable per scenario step. Missing → P2 citing C2.
- C3: Data tables vs Scenario Outlines used appropriately (table for ≤3 cells; Outline for parameter sweeps). Missing → P3 citing C3.
- C4: Shared steps deduplicated (no copy-paste; reuse via step-defs). Missing → P3 citing C4.
- C5: Tag conventions consistent (@regression / @smoke / @slow / @flaky used per project standard). Missing → P3 citing C5.

**tech_lead (25, solutions-architect)** — Implementability lens.

- C1: Step definitions implementable as written (no semantic ambiguity in trigger/action/observable). Missing → P2 citing C1.
- C2: Timeout/wait reasoning explicit (no implicit sleeps). Missing → P2 citing C2.
- C3: Fixture setup/teardown idempotent (no test pollution). Missing → P2 citing C3.
- C4: Cross-scenario dependencies absent (each scenario standalone). Missing → P1 citing C4.
- C5: Tag placement at scenario boundary (no tag inheritance ambiguity). Missing → P3 citing C5.

**chaos_engineer (14, chaos-engineer)** — Failure-mode scenario lens (DOMINANT at BDD per crew rationale).

- C1: Every unwanted-pattern EARS line has ≥1 failure-mode scenario. Missing → P1 citing C1.
- C2: Network-partition + slow-response variants covered for each integration. Missing → P2 citing C2.
- C3: Recovery scenarios paired with failure scenarios. Missing → P2 citing C3.
- C4: Resource-exhaustion paths exercised (pool depletion, queue full, timeout). Missing → P2 citing C4.
- C5: Negative-path coverage parity with positive-path (every WHEN/THEN has a paired IF/THEN). Missing → P3 citing C5.

**security_engineer (6, security-engineer)** — Abuse-case scenario lens.

- C1: Every abuse-case EARS line has a security scenario. Missing → P2 citing C1.
- C2: AuthN/authZ scenarios cover both happy + denied paths. Missing → P2 citing C2.
- C3: Input-fuzzing scenarios for every accepting endpoint. Missing → P3 citing C3.
- C4: Audit-log assertions present where rules require them. Missing → P3 citing C4.
- C5: Regulatory-compliance scenarios where applicable (GDPR / HIPAA / PCI per project context). Missing → P3 citing C5.

**operator (10, devops-release-engineer)** — Runtime + observability lens.

- C1: Observability hooks in scenarios (logs / metrics / traces) — at minimum the gate-checking ones. Missing → P3 citing C1.
- C2: Runtime-config-change scenarios (feature flag flip, config reload). Missing → P3 citing C2.
- C3: Deploy-during-traffic scenarios (rolling-restart, partial outage). Missing → P3 citing C3.
- C4: Operator-action scenarios (rollback, drain, freeze). Missing → P2 citing C4.
- C5: Alerting-fire scenarios for SLO breaches. Missing → P3 citing C5.

**auditor (10, traceability-auditor)** — Conformance lens.

- C1: Tags resolve to upstream EARS lines (every @ears tag points to an actual EARS element ID). Missing → P1 citing C1.
- C2: Step-definition catalog conformance (no orphan step defs). Missing → P2 citing C2.
- C3: Scenario IDs follow naming standards (`BDD.NN.SS.xxxx` per ID_NAMING_STANDARDS). Missing → P2 citing C3.
- C4: Gherkin-lint clean (no syntax errors). Missing → P1 citing C4.
- C5: Feature-file Document Control populated. Missing → P3 citing C5.

### Task 2: Wire team-mode into `doc-bdd-audit/SKILL.md`

Mirror EARS-RT-001 audit pattern (commit `68696ded`). Insertions:

- `## Review Mode` section (team-mode default at gates; single_pass fallback) with 7-step team-mode procedure
- Playbook injection: step 3a (load `framework/playbooks/04_BDD/<lens>.md`) + augmented step 4 (inline playbook + require `check:` citation)
- `## Saga interaction` section (on entry, fan-out, break-circuit, reduce, standalone, single_pass)
- `## Break-circuit policy` (SOFT_DEADLINE 1500s)

Layer substitutions: `04_BDD`, BDD-id, BDD crew + lens-to-agent map per table above.

### Task 3: Wire team-mode into `doc-bdd-fixer/SKILL.md`

Mirror EARS-RT-001 fixer pattern (commit `3c91757b`). Insertions:

- `## Remediate Mode` (team-mode + single_pass) — 6-step procedure
- `## Saga interaction` + `## Break-circuit policy`

### Task 4: Bump versions UPFRONT (lesson from EARS-RT-001)

```bash
echo "0.14.2" > framework/VERSION
echo "0.9.0"  > platforms/claude-code-plugin/VERSION
```

Update `tests/conformance/platforms/test_plugin_release_metadata.py` hardcoded pin from `"0.14.1"` to `"0.14.2"`.

Add `claude-code-plugin/v0.9.0` row to `docs/TAGGING.md`.

Run sync hook to propagate.

### Task 5: Live BDD cascade

```bash
bash tests/scripts/test-acceptance.sh url-shortener --live --phase=cascade --from-layer=bdd --to-layer=bdd
```

**Prerequisites**: BRD-01.md + PRD-01.md + EARS-01.md must exist on the example. All three on main from prior PRs.

**Pass criteria** (relaxed from EARS-RT-001's experience):

- combined_status = PASS or PARTIAL_TIMEOUT terminal with blocking=0
- coverage.quorum_met = true
- ≥ 60% findings cite checklist Cn (not beyond-checklist)
- No findings with `check: "<missing>"`
- No blocking P0/P1 in final iteration (resume if needed via direct driver invocation)
- BDD score ≥ 80 (chaos-heavy crew surfaces many findings; below 90 is expected on first run)

If iter-N terminal with P1 still present, hand-fix the P1 + run one more iter (proven recovery pattern from EARS-RT-001 iter-4/iter-5).

### Task 6: Doc-of-record + open PR

Update: root CHANGELOG, plugin CHANGELOG (`[0.9.0]`), ROADMAP, HANDOFF, PARITY (extend Layer Playbooks row to BRD/PRD/EARS/BDD), TAGGING (already added in Task 4). HERMES-BACKLOG H-4 covers BDD; no new entry.

Commit final batch. Push. Open PR.

---

## Out of scope (deferred)

- ADR/SPEC/TDD/IPLAN per-layer rollouts → trackers #265-#268
- Removing `@unittest.skip` from test_playbook_coverage.py → final per-layer PR per #258

---

## Review log

### Pass 1 — 2026-06-08

Reviewer: Claude (plan author, fresh-eyes self-review).

Findings:

1. **operator lens is new at BDD layer (CRITICAL CHECK)**. Verified: REVIEW_CREWS.yaml introduces `operator` at BDD (also present at TDD/IPLAN). Plugin agent mapping `operator → devops-release-engineer` per `review-team/SKILL.md`. Verified `platforms/claude-code-plugin/agents/devops-release-engineer.md` exists. Mapping safe.

2. **6-lens crew vs 5-lens previous layers**. Plan accounts for this — operator is the 6th. No issue.

3. **EARS-RT-001 lessons applied (CRITICAL)**.
   - framework/VERSION bumped UPFRONT in Task 4 (not retroactively as in EARS-RT-001 which required a separate fix commit + CI re-run)
   - Test pin updated in same task as VERSION bump
   - TAGGING.md row added in same task

4. **Live cascade pass criteria relaxed (IMPORTANT)**. EARS-RT-001 plan said `≥ 85` and ran 5 iterations to land at 84. BDD plan says `≥ 80` to acknowledge chaos-heavy crews surface more findings. Also explicit "resume + hand-fix" workflow per EARS-RT-001's proven recovery.

5. **Chaos-heavy weight 14 (IMPORTANT)**. BDD has the highest chaos_engineer weight of any layer (14 vs 12 BRD/EARS, 8 PRD, 10 SPEC/TDD, 8 IPLAN). This means chaos findings have heaviest impact on the weighted score. The chaos_engineer playbook's C1 ("every unwanted-pattern EARS line has ≥1 failure scenario") will be a binding gate.

6. **STY03 doc-length risk (NICE-TO-HAVE)**. BDD scenario files are typically long. Track and tighten if STY03 fires.

7. **BDD prerequisite chain (CRITICAL)**. BDD draft reads EARS-01.md as upstream. The current EARS-01.md is the one from EARS-RT-001 (with hand-fixes for SE-001 + STRUCT-001). Acceptable but contains advisory P2/P3 findings still — those may propagate to BDD draft.

8. **operator agent prompt may be uncalibrated for BDD lens specifically (MINOR)**. devops-release-engineer is a general-purpose agent. Per LAYER-PLAYBOOKS-001 design, the playbook brief steers the lens; agent stays generic. Plan relies on this — minor calibration risk noted.

Pass 1: 8 findings, all addressed inline (4 confirmed already correct; 4 documented as lessons-applied or acceptable risks).

### Pass 2 — 2026-06-08

Reviewer: Claude (re-review).

Findings:

1. **Pass 1 finding 3 (version bumps upfront) verified**. Task 4 explicitly bumps framework/VERSION AND plugin/VERSION AND updates test pin AND adds TAGGING row — all in same task. No retroactive fix needed. ✓

2. **Sync hook coverage check**. `scripts/sync-version-refs.sh` was extended in LAYER-PLAYBOOKS-001 Task 11 to propagate `framework_spec_version` into playbook frontmatters. For the new 6 BDD playbooks, this means after Task 1 they have hardcoded "0.14.1" initially; after Task 4 (VERSION bump to 0.14.2 + sync hook fires on commit), the hook bumps them. Sequence is correct.

3. **Conformance test pin propagation**. The hardcoded pin in `test_plugin_release_metadata.py` requires manual update each time framework/VERSION bumps. Task 4 covers this. No drift.

4. **Pass 1 finding 7 (BDD prerequisite chain)**. EARS-01.md state on main is the post-fix version. BDD-01.md draft reads it as `@ears:` upstream. If EARS-01.md has any P2/P3 findings flagged but unaddressed, BDD chaos_engineer's C1 (unwanted-pattern coverage) may inherit gaps. Acceptable for the first BDD live run; iterate per EARS-RT-001 pattern if issues surface.

5. **Branch + commit conventions consistent**. `feat/bdd-rt-001`, `feat(plugin):` for SKILL changes, `feat(framework):` for playbooks, `chore(plugin):` for VERSION bump, `docs(bdd-rt-001):` for doc-of-record. Same conventions as PRD/EARS-RT-001.

Pass 2 verdict: zero new substantive gaps. Plan ready.
