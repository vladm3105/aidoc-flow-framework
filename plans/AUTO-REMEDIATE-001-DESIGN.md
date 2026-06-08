# AUTO-REMEDIATE-001 — Cascade Bootstrap Auto-Remediation (Design)

**Status:** design approved by user during brainstorming session (2026-06-08)
**Next:** implementation plan via `writing-plans` skill → `plans/AUTO-REMEDIATE-001-PLAN.md`
**Authority:** `tests/scripts/test-acceptance.sh` (the test harness this design extends)
**Origin:** BDD-RT-001 cascade blocked at `lint-smoke` bootstrap on a STY03-violating EARS-01.md. The user clarified: framework agents (not hand-edits) must remediate example artifacts. Codified in CLAUDE.md durable convention `Never hand-edit example artifacts` and memory `feedback_never_hand_edit_example_artifacts.md`.

## Problem statement

The cascade harness's `phase_0_bootstrap` runs `sdd_doc_lint` as a one-shot smoke test on the existing `examples/<NAME>/docs/` tree. If lint fails on any pre-existing doc (e.g., EARS-01.md after EARS-RT-001 iter-2 fixer's patches pushed it to 2457 words, over the STY03 blocking threshold of 2250), the cascade exits before any audit/fixer cycle can run. The doc can ONLY be repaired by:

1. Hand-editing the doc (forbidden per `Never hand-edit example artifacts`)
2. Running a separate manual remediation step (out-of-band, fragile)

Neither path is framework-driven. The framework's own remediation surface (`doc-<layer>-fixer` SKILLs) is unreachable from a blocked cascade.

## Decisions (design surface)

| # | Decision | Choice |
|---|---|---|
| 1 | Trigger scope | **STY03 only** (doc-body word-count over blocking threshold). Other lint failures (STRUCT*, AS*, CSC*, STY01, STY02) still abort the cascade. |
| 2 | Layer dispatch | **Parse failing file path** → match `docs/<NN>_<LAYER>/<ART>-NN_*` → dispatch `doc-<lower-layer>-fixer` |
| 3 | Failure handling | **Single attempt**. If STY03 persists after the fixer cycle → restore backup, abort with diagnostic message |
| 4 | Fixer input | **Synthesize a minimal audit verdict** containing STY03 as a P1 finding. Fixer consumes it via its existing Input Contract — no SKILL changes needed |
| 5 | Saga journal | **single_pass mode**. Skips saga interaction entirely. Works for ALL 8 layers (BRD/PRD/EARS/BDD/ADR/SPEC/TDD/IPLAN) regardless of team-mode wiring state |

## Architecture

```
phase_0_bootstrap step 0.5 (lint-smoke):
  lint_out, lint_rc = sdd_doc_lint($EXAMPLE_DOCS)

  if lint_rc == 0:
    record_outcome("lint-smoke" PASS); return 0

  ──── NEW: auto-remediate path ────
  if has_STY03_only(lint_out):                       # filter check
    failing_path = extract_path(lint_out)             # e.g. docs/03_EARS/EARS-01.md
    layer_dir = extract_layer_dir(failing_path)       # e.g. 03_EARS
    layer_short = lower(layer_dir.split("_")[1])      # "ears"
    artifact_id = extract_artifact_id(failing_path)   # "EARS-01"

    backup_doc($failing_path)                         # safety net
    write_synthetic_audit_report(layer_dir, artifact_id, STY03_finding)
    write_synthetic_verdict(layer_dir, artifact_id, STY03_finding, priority=P1)

    record_outcome("lint-smoke-auto-remediate" "RUNNING" 0)
    invoke claude -p /aidoc-flow:doc-${layer_short}-fixer \
      with: REVIEW_MODE=single_pass + verdict path + budget

    re-run sdd_doc_lint($EXAMPLE_DOCS) → lint_rc2

    if lint_rc2 == 0:
      record_outcome("lint-smoke" PASS-AFTER-AUTO-REMEDIATE)
      return 0
    else:
      restore_backup($failing_path)                   # leave artifact unchanged on failure
      log_err: "doc-${layer_short}-fixer cycle did not resolve STY03; check the fixer SKILL"
      record_outcome("lint-smoke" FAIL)
      return 1

  ──── existing (non-STY03 failure) ────
  log_err "sdd_doc_lint smoke FAILED on existing docs/:"
  record_outcome("lint-smoke" FAIL)
  return 1
```

## Helper functions to add

All inside `tests/scripts/test-acceptance.sh` as bash functions. Single-purpose, testable.

| Helper | Purpose | Approx LOC |
|---|---|---|
| `has_STY03_only(out)` | Detect if lint output contains STY03 errors and nothing else error-level | ~10 |
| `extract_path(out)` | Regex `^([^:]+):0:.*STY03` → path | ~5 |
| `extract_layer_dir(path)` | Match `0N_LAYER` directory in path components | ~5 |
| `extract_artifact_id(path)` | Match `<LAYER>-NN` filename prefix | ~5 |
| `write_synthetic_audit_report(layer_dir, art_id, finding)` | Create minimal `.aidoc/audit/<NN_LAYER>-audit.md` with one STY03 finding | ~25 |
| `write_synthetic_verdict(layer_dir, art_id, finding, priority)` | Create minimal `.aidoc/review/<NN_LAYER>/<art_id>/verdict.json` with one P1 finding | ~25 |
| `backup_doc(path)` / `restore_backup(path)` | Save + restore for failure recovery | ~5 each |

Total ~80 lines added to `tests/scripts/test-acceptance.sh`.

## Error handling

| Edge case | Behavior |
|---|---|
| Lint output has STY03 AND other ERROR (e.g., STY03 + STRUCT01) | Don't trigger auto-remediation (mixed failure = human investigation) |
| Fixer SKILL not found / not invokable | Abort with `"doc-<layer>-fixer SKILL missing; cannot auto-remediate"` |
| Fixer cycle times out (claude `-p` timeout) | Treat as failure; restore backup; abort |
| Fixer cycle PASSes (exit 0) but STY03 still fires | Restore backup + abort with `"fixer cycle reported success but STY03 unresolved — fixer SKILL gap"` |
| Multiple files fail lint (e.g., EARS-01 + PRD-01 both STY03) | Process them sequentially (first one fixed, re-lint, second one fixed, re-lint, ...). If any single one fails → abort |
| The synthetic verdict already exists (prior cascade) | Backup it first, write new one, restore after — preserves prior state |
| Fixer's patch shrinks doc but introduces a structural error (e.g., removed a required section) | Re-lint detects the new STRUCT failure; treated as "STY03 persisted OR new failure surfaced" → abort + restore backup |

## Testing strategy

| Test | What it verifies |
|---|---|
| Unit: `has_STY03_only` correctly classifies (new `tests/scripts/test-auto-remediate-helpers.sh`) | Various lint output samples → boolean (STY03-only? mixed? clean?) |
| Unit: `extract_path`, `extract_layer_dir`, `extract_artifact_id` | Sample lint outputs / paths → correct extractions |
| Smoke: dry-run with a deliberately STY03-violating EARS-01 fixture | Auto-remediation path triggers; backup written; synthetic verdict written; fixer would be invoked (mock the actual LLM call) |
| Live: full cascade with current EARS-01.md (which IS STY03-violating on main) | Real end-to-end: lint-smoke FAIL → auto-remediate → fixer cycle → re-lint PASS → cascade proceeds to BDD draft. Validates the design against the actual blocker that prompted this work. |

## Scope (in / out)

### In scope (this PR)

- New helper functions in `tests/scripts/test-acceptance.sh` (~80 lines)
- Modified `phase_0_bootstrap` step 0.5 to add the auto-remediation branch
- Unit tests for helpers
- Live cascade validation on the BDD-RT-001 blocked scenario (verifies the fix unblocks BDD-RT-001)
- Doc-of-record: CHANGELOG entry; HANDOFF narrative; no VERSION bump (harness change, not spec/plugin change)

### Out of scope (deferred)

- Broader workflow gap categories beyond STY03 (handled if/when other class blocks surface)
- Pre-emptive remediation (`cascade-preheat` phase) — heavier alternative not chosen
- Fixer SKILL-level prevention (each fixer checks its own STY-class output) — bigger surface; address only if STY03 keeps surfacing
- Auto-remediation for the OTHER lint check (STY02 section-budget, STY01 banned phrases, etc.) — narrow trigger keeps blast radius small

## Constraints

1. **No SKILL changes**: the design works purely at the harness level. The `doc-<layer>-fixer` SKILLs are not modified.
2. **No framework spec changes**: `framework/VERSION` does not bump.
3. **No plugin VERSION change**: this is harness work, not plugin behavior. `platforms/claude-code-plugin/VERSION` does not bump.
4. **Hand-edit forbidden**: when the live cascade tests this end-to-end, the auto-remediation is the EXCLUSIVE path. I (the operator) do NOT touch the failing doc directly.
5. **Conformance must stay green**: the new harness logic must not break any existing conformance test.

## Risk acknowledgment

The auto-remediation invokes the fixer SKILL with a synthetic verdict the fixer wasn't designed to consume in this exact way. Risk: the fixer might refuse the synthetic input, or might apply the wrong style of patch (e.g., it might try to add content because STY03 is described as "missing requirements" if our synthetic finding's wording is misleading). The minimal verdict should be unambiguous (`message: "Doc body is N words; reduce to ≤ TARGET"`). Will validate during the smoke test.

If the fixer SKILL declines to act on the synthetic verdict (e.g., because no `<layer>-NN.A_audit_report_vNNN.md` file exists in the expected location), that's a learning we'll fold into the implementation. The single-attempt-then-abort failure mode surfaces this clearly.

## Approved by user: 2026-06-08 during brainstorming session

**Next:** implementation plan via `writing-plans` skill → `plans/AUTO-REMEDIATE-001-PLAN.md`
