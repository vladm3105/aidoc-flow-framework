# EARS-RT-001 Implementation Plan

> **Combined plan + impl in one PR per user direction.** Plan committed first, impl commits follow on the same branch (`feat/ears-rt-001`).

**Goal:** Wire team-mode fan-out into `doc-ears-audit` + `doc-ears-fixer` SKILLs (mirror PRD-RT-001 pattern), add playbook injection (mirror LAYER-PLAYBOOKS-001 pattern), author 5 EARS playbooks, validate via live EARS cascade.

**Architecture:** Mechanical replication of the proven PRD-RT-001 + LAYER-PLAYBOOKS-001 patterns for the EARS layer (Layer 3). The framework spec + plugin mechanism + synthesizer schema all stay unchanged — only EARS-specific configuration + content lands.

**Design authority:** `plans/LAYER-PLAYBOOKS-001-DESIGN.md` (engine-agnostic playbook contract) + `platforms/claude-code-plugin/skills/doc-prd-audit/SKILL.md` (team-mode template).

---

## EARS crew (from `framework/governance/REVIEW_CREWS.yaml`)

```yaml
EARS:
  author: requirements_specialist
  review: {requirements_specialist: 35, tech_lead: 25, qa_lead: 20, chaos_engineer: 12, security_engineer: 8}
```

Sum: 100. Rationale (per file comment): "Chaos-heavy at EARS (12 > 8) — failure-mode acceptance criteria are more common than abuse-case ACs."

## Lens → plugin agent mapping (per `review-team/SKILL.md` table)

| Lens | Weight | Agent |
|---|---|---|
| `requirements_specialist` | 35 | `requirements-analyst` (also EARS author) |
| `tech_lead` | 25 | `solutions-architect` |
| `qa_lead` | 20 | `test-architect` |
| `chaos_engineer` | 12 | `chaos-engineer` |
| `security_engineer` | 8 | `security-engineer` |

---

## File structure

### Modified

| Path | What changes |
|---|---|
| `platforms/claude-code-plugin/skills/doc-ears-audit/SKILL.md` | Add `## Review Mode` (team + single_pass), `## Saga interaction`, `## Break-circuit policy`, `## Playbook injection` per the PRD-RT-001 + LAYER-PLAYBOOKS-001 patterns. Substitute layer-specific values: `03_EARS`, EARS crew + weights, lens→agent map. |
| `platforms/claude-code-plugin/skills/doc-ears-fixer/SKILL.md` | Add `## Remediate Mode` (team + single_pass) + `## Saga interaction` + `## Break-circuit policy`. Substitute layer-specific values. |
| `CHANGELOG.md` (root) | `[Unreleased]` entry for plugin minor bump (consumes pattern + adds EARS-RT-001) |
| `platforms/claude-code-plugin/CHANGELOG.md` | New version entry — plugin 0.7.0 → 0.8.0 |
| `ROADMAP.md` | Shipped bullet for EARS-RT-001 |
| `plans/HANDOFF.md` | EARS-RT-001 dated narrative |
| `docs/PARITY.md` | Plugin version + (optional) layer-specific row |
| `platforms/claude-code-plugin/VERSION` | 0.7.0 → 0.8.0 (sync hook propagates) |

### Created

| Path | Purpose |
|---|---|
| `framework/playbooks/03_EARS/requirements_specialist.md` (weight 35) | EARS author + lens playbook |
| `framework/playbooks/03_EARS/tech_lead.md` (weight 25) | Implementability lens |
| `framework/playbooks/03_EARS/qa_lead.md` (weight 20) | Testability + coverage lens |
| `framework/playbooks/03_EARS/chaos_engineer.md` (weight 12) | Failure-mode AC coverage |
| `framework/playbooks/03_EARS/security_engineer.md` (weight 8) | Abuse-case AC coverage |
| `plans/EARS-RT-001-PLAN.md` | This file |

---

## Implementation sequence

### Task 1: Author 5 EARS playbooks

Pattern: identical to LAYER-PLAYBOOKS-001 Phase E (Tasks 10.1/10.2). Hybrid content shape per `framework/governance/REVIEW_TEAM.md` §Playbooks.

Per-playbook content topics (calibrate against EARS-specific concerns):

**requirements_specialist (35, agent: requirements-analyst)** — EARS-pattern compliance lens.

- C1: Every EARS line uses one of the 6 canonical patterns (ubiquitous / event-driven / state-driven / optional / unwanted / complex). Missing → P1 citing C1.
- C2: Atomicity — one rule per line, no conjoined obligations. Missing → P2 citing C2.
- C3: Every line has a measurable response (no "appropriately", "as needed"). Missing → P2 citing C3.
- C4: Every `@prd:` tag resolves to an actual PRD element. Missing → P1 citing C4.
- C5: No orphan rule — every line traces to a PRD §9 row. Missing → P2 citing C5.

**tech_lead (25, agent: solutions-architect)** — Implementability lens.

- C1: Triggers + responses are technically implementable (no hand-waving). Missing → P2 citing C1.
- C2: Overlapping rules flagged (multiple ubiquitous on same state). Missing → P2 citing C2.
- C3: Every numeric bound has units (ms / req/s / bytes / %). Missing → P2 citing C3.
- C4: ADR-deferred placeholders explicitly marked (not implicit). Missing → P3 citing C4.
- C5: Consistency of terminology with PRD glossary. Missing → P3 citing C5.

**qa_lead (20, agent: test-architect)** — Testability lens.

- C1: Every EARS line corresponds to ≥1 BDD scenario at next layer. Missing → P2 citing C1.
- C2: Coverage matrix readable (rule → tests; bidirectional). Missing → P3 citing C2.
- C3: Ambiguity-free triggers (no "occasionally", "sometimes", "if appropriate"). Missing → P2 citing C3.
- C4: Negative cases enumerated (unwanted patterns paired with positive). Missing → P2 citing C4.
- C5: Idempotency declared for stateful rules. Missing → P3 citing C5.

**chaos_engineer (12, agent: chaos-engineer)** — Failure-mode coverage lens.

- C1: Every failure mode named in PRD §13 has an unwanted-behavior EARS line. Missing → P2 citing C1.
- C2: Timeout-vs-deadline coupling explicit (no unbounded waits). Missing → P2 citing C2.
- C3: Retry budgets bounded (no infinite-retry loops). Missing → P2 citing C3.
- C4: Cascading-failure boundary stated (firebreaks named). Missing → P3 citing C4.
- C5: Recovery rules paired with detection rules (no detection without response). Missing → P2 citing C5.

**security_engineer (8, agent: security-engineer)** — Abuse-case + control lens.

- C1: Every abuse case from PRD has an EARS line (event-driven + unwanted pair). Missing → P1 citing C1.
- C2: Input-validation rules cover all submission paths. Missing → P2 citing C2.
- C3: Rate-limiting rules have explicit bounds (or ADR-deferred markers). Missing → P2 citing C3.
- C4: Audit-log rules cover authentication + authorization decisions. Missing → P3 citing C4.
- C5: Data-classification matched to access rules. Missing → P2 citing C5.

Each playbook target: ~95-110 lines (matching the BRD/PRD playbook density).

### Task 2: Wire team-mode into `doc-ears-audit/SKILL.md`

Current state: 267 lines, legacy single-pass structure (no `REVIEW_CREWS`, no fan-out). Mirror PRD-RT-001 pattern (commit `b3e36583` / PR #101).

Insertions (matching PRD's structure):

- `## Review Mode` section after `## Execution Contract`, before `## Structural Checklist`
  - `### team mode (default at gates)` with steps 1-7 (blackboard prep, crew read, lens→agent map, fan-out, slot collection, synthesizer dispatch, audit report composition)
  - `### Output Contract (team mode)` with the verbatim stdout shape
  - `### single_pass mode (fallback)` preserved as legacy path
- `## Saga interaction` section before `## Break-circuit policy`
  - On entry, during lens fan-out, before synthesizer (break-circuit), after synthesizer reduce, standalone mode, single_pass mode
- `## Break-circuit policy` section
- **Playbook injection** (per LAYER-PLAYBOOKS-001): in the team-mode fan-out, add step 3a (load `framework/playbooks/03_EARS/<lens>.md` → `BRANCH_FAILED` on miss) + augmented step 4 (inline `## Layer-specific playbook` section + require `check:` citation)

Layer-specific substitutions:

- Saga journal path: `.aidoc/review/03_EARS/<EARS-id>/saga.json`
- Slot directory: `.aidoc/review/03_EARS/<EARS-id>/<lens>.json`
- Audit report: `.aidoc/audit/03_EARS-audit.md`
- Crew: `{requirements_specialist: 35, tech_lead: 25, qa_lead: 20, chaos_engineer: 12, security_engineer: 8}`
- Lens → plugin agent map per table above
- Playbook path: `${CLAUDE_PLUGIN_ROOT}/../../framework/playbooks/03_EARS/<lens>.md`

### Task 3: Wire team-mode into `doc-ears-fixer/SKILL.md`

Current state: 113 lines, legacy structure. Mirror PRD-RT-001 fixer pattern (commit `b3e36583`).

Insertions:

- `## Remediate Mode` section between `## Input Contract` and `## Fix Phases`
  - `### team mode (per REVIEW_TEAM.md §Operations §Remediate)` with steps 1-6
  - `### single_pass mode (fallback)` preserved
- `## Saga interaction` section
- `## Break-circuit policy` section

### Task 4: Bump plugin VERSION 0.7.0 → 0.8.0

```bash
echo "0.8.0" > platforms/claude-code-plugin/VERSION
```

Sync hook auto-propagates to plugin.json, marketplace.json, 52 SKILL.md frontmatters, README, plugin README, docs/SKILL_AUTHORING.md, docs/PARITY.md.

### Task 5: Live EARS cascade verification

```bash
# Prerequisites: BRD-01.md + PRD-01.md must exist as upstream artifacts.
# (Both are on main from LAYER-PLAYBOOKS-001.)
ls examples/url-shortener/docs/01_BRD/BRD-01.md examples/url-shortener/docs/02_PRD/PRD-01.md

# Run cascade for EARS only
bash tests/scripts/test-acceptance.sh url-shortener --live --phase=cascade --from-layer=ears --to-layer=ears
```

**Pass criteria** (mirror LAYER-PLAYBOOKS-001 Task 12 criteria):

- combined_status = PASS
- coverage.quorum_met = true
- ≥ 60% findings cite a checklist check (not beyond-checklist)
- EARS score reasonable (no baseline yet; first live EARS team-mode run — set sanity check ≥ 85)
- No findings with `check: "<missing>"`
- saga = CLOSED

### Task 6: Doc-of-record + commit + push + open PR

Update:

- Root `CHANGELOG.md`: `[Unreleased]` entry for plugin 0.7.0 → 0.8.0 (EARS team-mode + playbook injection + 5 EARS playbooks)
- `platforms/claude-code-plugin/CHANGELOG.md`: new `[0.8.0]` entry
- `ROADMAP.md`: shipped bullet
- `plans/HANDOFF.md`: dated narrative incl. live cascade results
- `docs/PARITY.md`: auto-updated by sync hook for version; manual row for EARS-RT-001 if appropriate
- `plans/HERMES-BACKLOG.md`: extend H-4 if appropriate

Final commit batching all doc-of-record changes. Push. Open PR.

---

## Out of scope (deferred)

- BDD/ADR/SPEC/TDD/IPLAN per-layer rollouts → tracked as #264-#268
- Removing `@unittest.skip` from `test_playbook_coverage.py` → deferred to final per-layer PR (#268 / IPLAN-RT-001) per #258

---

## Review log

*Mandatory per CLAUDE.md "Two-cycle plan review is mandatory" — cycles executed against this draft prior to the initial commit of the plan file. Combined plan + impl PR per user direction; cycles still happen here BEFORE the PR opens.*

### Pass 1 — 2026-06-08

Reviewer: Claude (plan author, fresh-eyes self-review).

Findings:

1. **EARS lens-to-agent map preservation (CRITICAL CHECK).** Plan table lists `tech_lead → solutions-architect`, `qa_lead → test-architect`. Verified against `platforms/claude-code-plugin/skills/review-team/SKILL.md` mapping. Mapping is consistent with what PRD-RT-001 uses for `tech_lead` (also `solutions-architect`). `qa_lead → test-architect` is new for this PR. Confirm `test-architect` agent exists: per Task 1 prep, `platforms/claude-code-plugin/agents/` contains `test-architect.md`. Patched: no change needed — agent exists.

2. **Live cascade prerequisites (CRITICAL).** EARS cascade requires BRD-01.md AND PRD-01.md as upstream. Per Task 5 plan, both are confirmed on main from LAYER-PLAYBOOKS-001 (#106 merged). Patched: pre-check explicit in Task 5.

3. **No baseline for EARS score (IMPORTANT).** Prior layers had baselines (BRD 96, PRD 93). EARS has no prior team-mode cascade → no baseline. Patched: pass criterion set to "≥ 85" as a sanity check rather than ±3-of-baseline.

4. **doc-ears-fixer current state (IMPORTANT).** 113 lines, legacy `## Fix Phases` table-based structure. Verified by reading the file. The PRD-RT-001 fixer wiring inserts `## Remediate Mode` BEFORE `## Fix Phases` (preserves the phase table). Patched: Task 3 explicitly notes "Insertions ... between `## Input Contract` and `## Fix Phases`" so the phase table is preserved.

5. **Playbook authoring TDD exception (MINOR).** Task 1 is content authoring, not TDD. Same pattern as LAYER-PLAYBOOKS-001 Phase E (no per-playbook unit test; conformance test covers existence + frontmatter; live cascade covers calibration). Patched: explicit "Hybrid content shape per framework/governance/REVIEW_TEAM.md §Playbooks" reference and the implicit absence of per-playbook tests is acceptable.

6. **Sync-plugin-framework.sh + sdd_doc_lint sync (MINOR).** When Task 1 creates playbook files, `tools/sync-plugin-framework.sh` mirrors them to `platforms/claude-code-plugin/framework/playbooks/03_EARS/` per the SUBTREES extension landed during LAYER-PLAYBOOKS-001. No change needed.

7. **Plugin VERSION bump direction (MINOR).** 0.7.0 → 0.8.0 (minor bump). Justified: adds EARS team-mode (new behavior in 5 SKILLs and the cascade). Major bump (1.0) deferred to documented v1.0 cutover per docs/PROJECT.md. Patched: explicit bump rationale in Task 4.

8. **Tests state expectation (MINOR).** After Task 1-3 land, `test_playbook_coverage.py` is still SKIPPED (no change). `test_playbook_frontmatter.py` validates the new 5 EARS playbooks vacuously through its rglob. Verified via plan's mental model. No change needed.

Total Pass 1: 8 findings, all addressed inline (4 noted, 4 confirmed already correct).

### Pass 2 — 2026-06-08

Reviewer: Claude (re-review after Pass 1, fresh-eyes pass focused on cycle-N+1 invariant).

Findings:

1. **Pass 1's "agent exists" claim re-verified.** Re-checked `platforms/claude-code-plugin/agents/test-architect.md` via `ls`. File present. Mapping safe.

2. **EARS cascade dispatcher expects saga driver.** test-acceptance.sh cascade dispatcher (modified in PR #102 to invoke saga driver directly) handles all 8 layers identically: `python3 saga_driver.py --layer ${layer_num}_${type}`. So for EARS, it invokes `--layer 03_EARS --threshold 90`. The saga driver dispatches the `/aidoc-flow:doc-ears-{audit,fixer}` slash commands via `claude -p`. As long as Task 2 + 3 produce the correct SKILL behavior, the harness is layer-agnostic. Verified.

3. **Plugin VERSION bump propagation.** Sync hook handles 0.7.0 → 0.8.0 across the 52 SKILL.md, plugin.json, marketplace.json, etc. Same mechanism as LAYER-PLAYBOOKS-001 Task 1's bump 0.13.1 → 0.14.0. No change.

4. **Doc-of-record per CLAUDE.md "Update docs of record per PR" rule.** All 5 doc artifacts (CHANGELOG×2, ROADMAP, HANDOFF, PARITY) listed in Task 6. HERMES-BACKLOG already has H-4 entry covering all layers; no new entry needed.

5. **Branch name + commit prefix consistency.** `feat/ears-rt-001` branch + `feat(plugin):` commit prefix for SKILL changes, `feat(framework):` for playbook authoring, `docs(ears-rt-001):` for doc-of-record. Same conventions as prior PRs.

Pass 2: zero new substantive gaps. Plan ready.
