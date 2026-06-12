# CHG-RT-001 — CHG layer team-mode + playbook injection + saga driver

> Per-layer rollout mirroring the 8 layer rollouts already shipped
> (EARS-RT-001 through IPLAN-RT-001). Brings CHG to feature-parity
> with the 8 SDD layers, then live-verifies against
> `examples/url-shortener/chg/test-change.md`.

| Field | Value |
|---|---|
| Task | CHG-RT-001 |
| Type | combined plan + impl + live verification |
| Worktree | `feat/chg-rt-001` at `/opt/data/aidoc-flow/framework-chg-rt-001/` |
| Depends on | LAYER-PLAYBOOKS-001 (45/45 playbooks done); FRAMEWORK-CLEANUP-001 (PR-B calibration + PR-D TH-RES-001 etc); CLEANUP-PR-F (#135 — doc-num independence + STRUCT01 regression fix) |
| Closes | (no FRAMEWORK-TODO item — this is a follow-on rollout per user direction 2026-06-12, "test CHG with the known per-layer-rollout path") |
| Version impact | Framework MINOR `0.20.1 → 0.21.0` (new CHG crew entry in REVIEW_CREWS.yaml + 6 new playbooks under existing §Playbooks artifact class — though §Playbooks did not anticipate CHG explicitly, hence MINOR not PATCH); plugin MINOR `0.17.1 → 0.18.0` (audit/fixer/autopilot full team-mode wiring + saga driver new layer entry) |
| Status | DRAFT — 2026-06-12 |

## Why this PR

CHG (Change Management overlay) is the **only governance surface that has not been exercised end-to-end against a real seed** despite the framework being otherwise mature:

- 4 SKILLs exist at `doc-chg`, `doc-chg-audit`, `doc-chg-fixer`, `doc-chg-autopilot` (all v0.17.1)
- Governance docs at `framework/governance/chg/` are comprehensive (README, CHG-TEMPLATE.yaml, 7 GATE definitions, POST_MORTEM template)
- `examples/url-shortener/chg/test-change.md` is a real CHG seed ("add visit-rate analytics dashboard") with downstream impacts enumerated as a built-in oracle
- `tests/scripts/test-acceptance.sh` Phase 2 is fully coded for the CHG cascade

But the live cascade has **never been run**. The url-shortener has no `docs/09_CHG/` directory. `doc-chg-audit` is single_pass-only (no Review Mode / Saga interaction / Break-circuit / Content Sub-Checks); 200 lines vs the 500-line layer audits post-PR-B. There are no CHG playbooks.

This PR brings CHG to per-layer parity (matching the EARS-RT-001 through IPLAN-RT-001 shape), then runs the live cascade as verification.

## Design decisions (committed for this PR)

### Crew composition

CHG is uniquely about **propagation faithfulness** + **gate routing** + **blast-radius assessment**. Lens choice + weights:

| Lens | Weight | Rationale |
|---|---|---|
| `integration_lead` | **30** | Primary CHG concern: did the impact assessment cover every affected layer? Are propagated changes consistent across BRD..IPLAN? |
| `architect` | 20 | Structural preservation: does the change preserve component boundaries + interfaces? |
| `chaos_engineer` | 15 | Rollback procedure + emergency-change paths + recovery scenarios |
| `operator` | 15 | Runbook updates + ops impact + deploy/monitor implications |
| `auditor` | 10 | Trace completeness across CHG ↔ affected-layer artifacts |
| `security_engineer` | 10 | Security impact of the proposed change + threat-model delta |
| **Total** | **100** | |

Reuses the closed persona set from REVIEW_CREWS.yaml — no new persona introduced. Equivalent crew shape to IPLAN's 6-lens composition.

### Layer key in saga driver

`"09_CHG"` — treats CHG as overlay-numbered-09 (sits after IPLAN/08). Acceptance suite already uses `09_CHG` in its dispatcher paths.

### Path under `framework/playbooks/`

`framework/playbooks/09_CHG/` — 6 new playbook files matching the layer-playbook convention.

### Spec touch

Framework MINOR (`0.20.1 → 0.21.0`):

- `REVIEW_CREWS.yaml` gains a CHG crew entry
- 6 new playbook files under `framework/playbooks/09_CHG/`
- `REVIEW_TEAM.md` §Playbooks gets a one-line note CHG is now wired

Plugin MINOR (`0.17.1 → 0.18.0`):

- 3 CHG SKILLs (`doc-chg-audit`, `doc-chg-fixer`, `doc-chg-autopilot`) gain ~300 lines each of saga + team-mode + Break-circuit + playbook injection
- `tools/saga_driver.py` `_LAYER_CREWS` gains `"09_CHG"` entry
- Conformance test count gate: 120 → 121 (new test for CHG crew presence)

## File structure

### New

| Path | Content |
|---|---|
| `framework/playbooks/09_CHG/integration_lead.md` | ~150 lines — propagation completeness, cross-layer consistency, expected-impacts enumeration check |
| `framework/playbooks/09_CHG/architect.md` | ~120 lines — structural preservation, boundary integrity, interface stability |
| `framework/playbooks/09_CHG/chaos_engineer.md` | ~100 lines — rollback plan completeness, emergency-change paths, recovery scenarios |
| `framework/playbooks/09_CHG/operator.md` | ~100 lines — runbook updates, deploy/monitor implications, observability hooks added/changed |
| `framework/playbooks/09_CHG/auditor.md` | ~80 lines — CHG ↔ affected-layer trace; gate-routing correctness; change-level classification correctness (C1/C2/C3/Emergency) |
| `framework/playbooks/09_CHG/security_engineer.md` | ~80 lines — security impact assessment of the proposed change, threat-model delta |
| `plans/CHG-RT-001-PLAN.md` | this plan |

### Modified

| Path | Change |
|---|---|
| `framework/governance/REVIEW_CREWS.yaml` | New `CHG:` entry under `crews:` (mirroring IPLAN's shape) — author + 6-lens review weights summing to 100 |
| `framework/governance/REVIEW_TEAM.md` §Playbooks | One-line note: CHG playbooks at `framework/playbooks/09_CHG/`; CHG is overlay, not lifecycle layer, but uses the same playbook contract |
| `tools/saga_driver.py` `_LAYER_CREWS` | New `"09_CHG"` key with the 6 personas |
| `platforms/claude-code-plugin/skills/doc-chg-audit/SKILL.md` | Full team-mode rewrite: 200 → ~500 lines. Adds `## Review Mode`, `## Saga interaction`, `## Break-circuit policy`, `## Content Sub-Checks` (5 sub-checks from PR-B), playbook injection. Mirrors `doc-iplan-audit` shape. |
| `platforms/claude-code-plugin/skills/doc-chg-fixer/SKILL.md` | Team-mode wiring: similar shape to `doc-iplan-fixer` |
| `platforms/claude-code-plugin/skills/doc-chg-autopilot/SKILL.md` | Saga-driven dispatch: invoke `python3 saga_driver.py --layer 09_CHG` |
| `tests/conformance/test_playbook_coverage.py` | Extend to 51 playbooks (45 + 6 CHG) |
| Versions + sync | `0.20.1 → 0.21.0` framework MINOR + `0.17.1 → 0.18.0` plugin MINOR + 2 × FRAMEWORK_SPEC_VERSION |
| `CHANGELOG.md`, `docs/TAGGING.md` (2 rows), `plans/HANDOFF.md` | Docs of record |

### Out of scope

- **CHG conformance tests beyond playbook coverage** (e.g., gate-routing correctness as a runtime check, change-level classification enforcement) — would be CHG-RT-002 if surfaced by live verification
- **Hermes mirror** — plugin-first per HERMES-CATCHUP-001 (already an entry in HERMES-BACKLOG)
- **CHG layer in `LAYER_REGISTRY.yaml`** — CHG remains an overlay, not a lifecycle layer (per `framework/governance/chg/README.md`); no `required_tags` entry needed
- **doc-chg author SKILL** — already exists and works (registers the change request); no rewrite needed at this layer

## Implementation sequence

1. **Plan iterative review** (2 cycles)
2. **REVIEW_CREWS.yaml** — add CHG crew entry
3. **6 CHG playbooks** under `framework/playbooks/09_CHG/`
4. **saga_driver.py** — add `09_CHG` entry to `_LAYER_CREWS`
5. **doc-chg-audit/SKILL.md** — full rewrite (mirror `doc-iplan-audit`)
6. **doc-chg-fixer/SKILL.md** — team-mode wiring (mirror `doc-iplan-fixer`)
7. **doc-chg-autopilot/SKILL.md** — saga-driven invocation
8. **REVIEW_TEAM.md** — one-line note about CHG playbooks
9. **Conformance test** — extend playbook coverage to 51
10. **Version + sync + docs of record**
11. **Conformance + unit cheap checks** (target 121/121 + 47/47)
12. **Live CHG cascade verification** against url-shortener — drive the seed through the 4 SKILLs end-to-end; verify CHG-01.md is produced + propagation report enumerates expected downstream impacts + audit converges to PASS
13. **Open PR** (only after Tasks 1-12 all green)

## Verification

| # | Check | Expected |
|---|---|---|
| 1 | `REVIEW_CREWS.yaml` has CHG crew; weights sum to 100 | PASS — conformance |
| 2 | 6 CHG playbooks present under `framework/playbooks/09_CHG/` | PASS — grep |
| 3 | `saga_driver.py` `_LAYER_CREWS["09_CHG"]` matches REVIEW_CREWS CHG personas | PASS — conformance |
| 4 | doc-chg-audit has `## Review Mode`, `## Saga interaction`, `## Break-circuit policy`, `## Content Sub-Checks` | PASS — grep |
| 5 | Conformance: **121/121** PASS (1 new test for CHG playbook coverage) | PASS |
| 6 | Unit: 47/47 PASS | PASS |
| 7 | url-shortener lint: still 1 TH-RES-001 (expected), 0 STRUCT01 | PASS |
| 8 | **Live cascade**: doc-chg-autopilot produces `docs/09_CHG/CHG-01.md` against url-shortener | PASS — file exists |
| 9 | **Live cascade**: propagation report enumerates ≥ 7 of 8 expected downstream impacts from test-change.md "Expected downstream impacts" section | PASS — manual review (use the seed's own oracle) |
| 10 | **Live cascade**: doc-chg-audit final score ≥ 90 (PASS gate) | PASS |

## Risks & rollback

| Risk | Mitigation |
|---|---|
| Live cascade reveals deeper CHG SKILL bugs (e.g., propagation report incomplete, audit can't grade gate routing) | This IS the verification step — surface bugs as findings; file as `CHG-RT-002` if substantial, else fix in-scope |
| 6-lens crew may be miscalibrated (weights wrong, lens missing/extra) | Live cascade is the calibration signal; weights can be tuned in CHG-RT-002 if 1-2 lenses dominate or none-of-them-spoke |
| Saga driver `09_CHG` entry could collide with the existing 8-layer enumeration | Saga schema already accepts arbitrary layer keys; conformance test `test_saga_driver_invariants` validates the dictionary shape, not the layer count |
| Plugin MINOR bump (0.17.1 → 0.18.0) is heavy for "one more layer of the same pattern" | MINOR is correct: framework MINOR (new crew + new playbooks under existing artifact class but extending CHG coverage); plugin MINOR (3 SKILLs gain ~900 cumulative lines + new saga layer) |

**Rollback:** single PR. `git revert <merge-sha>`. All changes additive to CHG which was previously cooperative-only.

## Review log

### Pass 0 — initial draft

- **Date:** 2026-06-12T01:00:00Z
- **Status:** SUPERSEDED by Pass 1.

### Pass 1 — self-review

- **Date:** 2026-06-12T01:05:00Z
- **Cross-checks:**
  - REVIEW_CREWS.yaml personas verified present in closed-set (no new persona introduced) ✓
  - Crew weights sum to 100 (30+20+15+15+10+10) ✓
  - saga driver `_LAYER_CREWS` accepts new keys (no enum, dict-based) ✓
  - doc-iplan-audit reference pattern available for mirror ✓
  - Live-verification oracle available: test-change.md enumerates expected impacts ✓
- **Findings (0 substantive):** plan sized to single layer; mirrors known-good per-layer rollout shape.

### Pass 2 — re-review

- **Date:** 2026-06-12T01:10:00Z
- **Findings:** 0 substantive. Self-converged.
- **Verdict:** user-driven review on the PR is the real convergence gate (per FRAMEWORK-CLEANUP-001 Pass 4 lesson).
