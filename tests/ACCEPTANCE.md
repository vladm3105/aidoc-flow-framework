# Acceptance Testing — methodology

The framework's pre-deployment acceptance test exercises every active
plugin surface element against a named example's seed. The chain it
produces is the release-gate evidence that the plugin works
end-to-end across its full surface.

This document defines the methodology. Each example under
`examples/<NAME>/` instantiates it with its own seed, change request,
and (optionally) per-example fixtures. Both `framework/docs/AIDOC.md`
(the provenance tier) and this doc are permanent reference material;
example-level READMEs are thin pointers to them.

## 1. Purpose

Drive every active element of the Claude Code plugin against the seed
at `examples/<NAME>/seed/initial-requirements.md` and verify the
produced output meets release criteria.

This is **not** a demo regeneration workflow — it is the pre-deployment
gate. The seed is the test input; the produced chain is the proof that
the release passes acceptance.

## 2. Scope — what gets exercised

All active plugin surface elements (63 total, plus a negative-fixture
validation pass):

| Phase | Surface elements | Count |
|------:|--------|------:|
| 0 — Bootstrap & preflight | manifest validate (`--strict`) + `sdd_doc_lint` smoke + profile bootstrap + `--force` safety belt + state detection + API auth | (infrastructure) |
| 1 — Layer cascade | `doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}-{base,autopilot,audit,fixer}` × negative-fixture validation | 32 |
| 2 — Change management | `doc-chg`, `doc-chg-{autopilot,audit,fixer}` | 4 |
| 3 — Cross-cutting utilities | `doc-flow`, `doc-validator`, `doc-ref`, `doc-naming`, `gate-check`, `quality-advisor`, `security-audit`, `review-team`, `knowledge-extractor`, `charts-flow`, `adr-roadmap`, `project-init`, `project-adopt`, `project-profile` | 14 |
| 4 — Agents, command, hook | 11 agents + `/aidoc-flow:save-plan` + `hooks/sdd-doc-review.sh` | 13 |
| **Total surface elements** | | **63** |

The 2 deprecated stubs (`doc-review`, `trace-check`) are not exercised
— they exist only to redirect users to their replacements.

## 3. Architecture

### Driver: `tests/scripts/test-acceptance.sh`

Sibling to the existing `test-plugin.sh`, `test-layer.sh`, and
`test-fullpath.sh` scripts. Independent of the tier-based dispatcher
because the acceptance run has a fundamentally different shape (63
individual invocations, per-element logging, real seed→chain cascade).

### Usage

First positional argument is the example name. To run multiple
examples, invoke the script once per example (a future `--all` flag is
tracked as Phase B work).

```bash
# Full live run against a named example
bash tests/scripts/test-acceptance.sh <example> --live

# Cheap deterministic smoke (~9s, no LLM). Prints the planned execution
# at the top, then runs the deterministic phases (Phase 0 preflight,
# negative fixtures, hook). LLM-dependent elements record SKIP.
# `--dry-run` is a clean alias.
bash tests/scripts/test-acceptance.sh <example> --no-live

# Generate a single element only (e.g. only the PRD against existing BRD)
bash tests/scripts/test-acceptance.sh <example> --live --element=doc-prd-autopilot

# Run a single layer's full skill set
bash tests/scripts/test-acceptance.sh <example> --live --from-layer=prd --to-layer=prd

# Resume cascade from a specific layer after a partial run
bash tests/scripts/test-acceptance.sh <example> --live --from-layer=spec

# Re-use prior PASS outcomes (iteration mode)
bash tests/scripts/test-acceptance.sh <example> --live --skip-completed

# Replay a recorded run (free, dev-iteration mode)
bash tests/scripts/test-acceptance.sh <example> --mock=examples/<example>/logs/<TS>

# Bypass `--force` safety belt when intentionally overwriting in-progress work
bash tests/scripts/test-acceptance.sh <example> --live --force

# Promote: git commit docs/ + .aidoc/ changes
bash tests/scripts/test-acceptance.sh <example> --live --promote

# CI-style: promote and push back to origin
bash tests/scripts/test-acceptance.sh <example> --live --promote --push
```

### Three-tier output layout

The acceptance suite writes outputs to four explicit tiers:

```text
examples/<NAME>/
├── seed/, chg/                  # human inputs (committed)
├── docs/                        # AI outputs — the produced chain (committed)
│   ├── 01_BRD/BRD-01.md         (cascade autopilot writes here directly)
│   ├── 02_PRD/PRD-01.md
│   ├── …
│   └── .version                 (records the plugin version of this chain)
├── .aidoc/                      # AI provenance (committed; see ../AIDOC.md)
│   ├── profile.yaml             (project profile — bootstrap from framework default)
│   ├── audit/<NN>_<LAYER>-audit.md      (doc-<layer>-audit outputs)
│   ├── remediation/<NN>_<LAYER>-fix.md  (doc-<layer>-fixer outputs)
│   ├── review/<layer>-consensus.md      (review-team consensus per layer)
│   ├── validation/<report>.md           (doc-validator/doc-ref/gate-check)
│   ├── security/review.md               (security-audit)
│   └── quality/suggestions.md           (quality-advisor)
└── logs/<TS>/                   # tool internals (gitignored, ephemeral)
    ├── plugin-test.log          # driver flow trace only
    ├── summary.txt              # human-readable per-element table
    ├── summary.json             # machine-readable (validates against schema v1.2)
    ├── elements/                # one file per element (skills, agents, command,
    │   ├── <name>.log           # hook, fixtures, negatives): YAML front-matter
    │   └── …                    # + raw skill/agent stdout
    └── sandbox/                 # tmp work for project-init, save-plan, hook test
```

### 3.1 `summary.json` schema (v1.2)

Committed at `tests/scripts/test-acceptance.schema.json`. Top-level
shape:

```json
{
  "schema_version": "1.2",
  "run_id": "2026-06-02T180052",
  "example": "<example>",
  "plugin_version": "0.4.0",
  "framework_spec_version": "0.11.1",
  "outcome": "PASS",
  "counts": { "PASS": 51, "FAIL": 0, "SKIP": 0, "RUNNING": 0, "INTERRUPTED": 0 },
  "elements": [
    {
      "schema_version": "1.2",
      "name": "doc-brd-autopilot",
      "kind": "skill",
      "phase": "cascade",
      "duration_sec": 84,
      "outcome": "PASS",
      "audit_score": 94,
      "audit_score_after_fixer": null,
      "fixer_invoked": false,
      "output_path": "docs/01_BRD/BRD-01.md",
      "tokens_in": null,
      "tokens_out": 9821,
      "error": null
    }
  ]
}
```

Per-element metadata uses the same shape, embedded as YAML
front-matter at the top of `logs/<TS>/elements/<name>.log`. The body
below the front-matter is the skill's captured stdout.

**Outcome states**:

- `PASS` — element produced gate-meeting output
- `FAIL` — element failed (sub-threshold output, error, or `INTERRUPTED`)
- `SKIP` — element not exercised (live mode disabled, bootstrap mode, etc.)
- `RUNNING` — in-flight (written before invocation, overwritten on completion)
- `INTERRUPTED` — script was killed mid-skill (re-write of surviving RUNNING entries via EXIT trap)

The summary is rebuilt incrementally after every element completes, so
an interrupted run leaves a usable checkpoint that `--skip-completed`
can read.

### 3.2 `--promote` algorithm

When `--promote` is set (or the script is invoked from `release.yml`
on a tag push) and **all phases passed**:

1. Resolve plugin version from `platforms/claude-code-plugin/VERSION`.
2. `git add examples/<NAME>/docs examples/<NAME>/.aidoc` — cascade
   already wrote there directly (no copy step).
3. If `git diff --cached --quiet` (no staged changes), no-op exit 0.
4. `git commit -m "chore(examples): promote <NAME> cascade for v<X.Y.Z> release"`.
5. If `--push` was also passed, `git push`.

⚠️ Pre-cascade safety belt (`--force`): the suite refuses to start a
live cascade if `docs/` or `.aidoc/` have unstaged changes, unless
`--force` is passed. Prevents accidental overwrite of in-progress
human edits.

### 3.3 Tier placement

This is a **Tier 6 — Release gate** test in the pyramid (see
[`../tests/README.md`](../../tests/README.md)). It runs only with
`LIVE=1` and is wired into `release.yml`, not into `pr-checks.yml`.

## 4. Phase 0 — Bootstrap & preflight

Runs first; gates whether subsequent phases can run. 7 sequential
checks:

1. **Seed presence**: `examples/<NAME>/seed/initial-requirements.md`.
2. **Manifest validate**: `claude plugin validate <plugin-dir> --strict`.
3. **`--force` safety belt**: refuses to run live cascade if
   `examples/<NAME>/{docs,.aidoc}/` have unstaged changes, unless
   `--force` is passed.
4. **Project profile**: if `examples/<NAME>/.aidoc/profile.yaml`
   exists, use it. If missing, copy
   `framework/governance/REVIEW_CREWS.yaml` as the framework default.
   Suite never authors a non-default profile.
5. **`sdd_doc_lint` smoke** on existing `docs/`. Acceptable to be
   empty (first-run bootstrap state).
6. **Negative-fixture presence check**: confirm
   `tests/acceptance/fixtures/negative/` exists.
7. **API auth check** (live only): `claude` CLI on PATH +
   `ANTHROPIC_API_KEY` set OR `claude -p` interactive login.

Bootstrap mode (`docs/` empty): Phase 2 (CHG) is skipped; Phase 3
utilities + Phase 4 agents run against the freshly-produced `docs/`
content from Phase 1.

### Partial-execution upstream check

When `--from-layer=<name>` or `--element=<name>` implies a non-BRD
layer, Phase 0 verifies the previous layer's artifact under `docs/`
exists. Fails fast with a clear hint if missing.

### Cleanup-then-cascade pattern (`rm -rf` → `--force`)

A common migration scenario: re-run the cascade against an example
whose existing artifacts pre-date a framework contract change (e.g.
`TRACE-RES-FIXUP-001` regenerated the url-shortener corpus under the
new necessary-upstream contract; `IPLAN-RT-001` regenerated only the
IPLAN layer against post-migration upstream). The clean approach is
to remove the to-be-regenerated layer directories + their `.aidoc/`
state before re-running the cascade.

This trips Phase 0's `--force` safety belt (item 3 above) because the
`rm -rf` shows up as unstaged deletions. The fix is to add `--force`
to the cascade invocation. Worked example (mirrors the IPLAN-RT-001
PR #127 cascade):

```sh
# 1. Pre-cleanup — remove the layer(s) being regenerated + per-layer
#    saga/audit state so the cascade starts deterministic.
rm -rf examples/url-shortener/docs/08_IPLAN/
rm -rf examples/url-shortener/.aidoc/review/08_IPLAN/
rm -rf examples/url-shortener/.aidoc/audit/08_IPLAN-audit.md

# 2. Run cascade with --force to bypass the unstaged-deletions safety
#    belt. The cleanup is the explicit precondition for the re-run.
bash tests/scripts/test-acceptance.sh url-shortener --live \
     --phase=cascade --from-layer=iplan --to-layer=iplan --force
```

**When to use `--skip-lint-smoke` in addition:** if the corpus is
mid-migration and the existing `docs/` carry artifacts that won't
pass `sdd_doc_lint` until they're regenerated, add `--skip-lint-smoke`
to bypass Phase 0's lint check + its auto-remediate fixer cycle. This
replaces the deprecated `SDD_LINT_SKIP_TRACE_RES=1` env-var pattern
that was used during the TRACE-RES-FIXUP-001 regen (PR #125). Use
only for migration scenarios; never set on production CI.

**Note on `.aidoc/remediation/`:** this directory holds per-document
remediation history that is not invalidated by a layer re-run; do NOT
clear it. Only `.aidoc/review/<NN_LAYER>/` (per-saga state) and
`.aidoc/audit/<NN_LAYER>-audit.md` (per-layer audit report) need
clearing for a deterministic re-run.

## 5. Phase 1 — Layer cascade

### 5.1 Happy-path cascade

For each of the 8 layers (`brd, prd, ears, bdd, adr, spec, tdd, iplan`):

1. **`doc-<layer>-autopilot`** with the previous layer's output as
   context. For BRD, context is the seed. Output written to
   `docs/<NN>_<LAYER>/<TYPE>-01.md`.
2. **`doc-<layer>-audit`** against the produced artifact. Audit
   report written to `.aidoc/audit/<NN>_<LAYER>-audit.md`. Capture
   the readiness score (0–100).
3. **If audit score < 90**, invoke `doc-<layer>-fixer` with audit
   findings; fix report written to
   `.aidoc/remediation/<NN>_<LAYER>-fix.md`. Then re-audit.
4. **`doc-<layer>`** (base/reference) against the artifact —
   structural baseline. Output captured to
   `logs/<TS>/elements/doc-<layer>.log`.
5. **`sdd_doc_lint`** against the artifact file only. Must produce
   zero structural findings.

Pass criteria for happy-path cascade:

- Every `-autopilot` exit 0.
- Every final `-audit` reports ≥ 90 score.
- `sdd_doc_lint` reports no structural findings across all 8 layers.
- Cumulative `@brd…@tdd` traceability tags resolve.

### 5.2 Negative-fixture validation

Curated broken artifacts live at `tests/acceptance/fixtures/negative/`
(shared across all examples — structural defects, not domain-specific).
Per-example additions, if any, live under
`examples/<NAME>/negative-fixtures/`.

| Fixture | What's broken | Expected detection |
|---|---|---|
| `brd-broken-sections.md` | Missing required `Functional Requirements` section | `doc-brd-audit` / `sdd_doc_lint` reports STRUCT01 |
| `brd-broken-tags.md` | `@brd` element-IDs malformed (3-segment) | `doc-brd-audit` / `sdd_doc_lint` reports ID01 |
| `prd-broken-upstream-ref.md` | References non-existent `@brd:BRD.99.01.aaaa` | `doc-validator` reports unresolved reference |
| `ears-score-7.md` | Vague content forces audit score < 50 | `doc-ears-audit` reports findings |
| `adr-missing-sequence-diagram.md` | No required `sequenceDiagram` | `doc-adr-audit` reports diagram contract violation |
| `chain-trace-broken/` | Mid-cascade `@brd` reference to non-existent upstream | `doc-validator` reports broken trace |

For each fixture: invoke the relevant audit/lint skill, assert it
reports the expected finding. A negative fixture that passes audit
is a regression in gating sensitivity.

## 6. Phase 2 — Change management (4 skills)

**Gated on Phase 1 success.** If `bootstrap_mode=true`, skipped
entirely.

After the cascade completes successfully:

1. Apply the predefined change committed at
   `examples/<NAME>/chg/test-change.md`.
2. **`doc-chg`** to register the change request.
3. **`doc-chg-autopilot`** drives the CHG-01 artifact through impact
   assessment, approval, propagation.
4. **`doc-chg-audit`** against CHG-01.
5. **`doc-chg-fixer`** if audit score < 90.

Pass criteria: CHG-01 audit ≥ 90; the propagation report enumerates
each "Expected downstream impacts" item from the change file.

### `chg/test-change.md` file format

Hand-curated per example. Required structure:

```markdown
# Test change request — <one-line summary>

## Motivation
<why the change is being requested — 2–3 sentences from a stakeholder POV>

## Scope
<what's being added/removed/modified — bullet list>

## Expected downstream impacts
- BRD: <section/item updated>
- PRD: <section/item updated>
- EARS: <requirement updated>
- BDD: <scenario added/changed>
- ADR: ADR-NN required for <decision>
- SPEC: <component impact>
- TDD: <test coverage delta>
- IPLAN: <task delta>
```

## 7. Phase 3 — Cross-cutting utilities (14 skills)

Each utility gets a targeted probe against the produced chain. **Each
probe has a minimum-coverage threshold** — empty structured output is
treated as FAIL.

| Skill | Probe | Pass criteria |
|---|---|---|
| `doc-flow` | "Given chain at layer N, what's next?" routing | Returns the correct next skill |
| `doc-validator` | Cumulative trace closure | All `@brd…@tdd` tags resolve; ≥ `n_layers × 4` resolved tags |
| `doc-ref` | Cross-reference resolution | All inter-doc references resolve; ≥ 8 references |
| `doc-naming` | Name compliance check | All IDs match `ID_NAMING_STANDARDS.md`; ≥ 8 IDs |
| `gate-check` | Aggregate readiness gate | All 8 layers ≥ 90 |
| `quality-advisor` | Improvement suggestions | ≥ 1 actionable suggestion per layer |
| `security-audit` | Security review | ≥ 1 finding + zero high-severity, OR "no findings" justification ≥ 100 words |
| `review-team` | Multi-persona review | All configured personas per `profile.yaml` produce non-empty output |
| `knowledge-extractor` | Domain knowledge graph | ≥ `n_layers × 4` nodes; Mermaid syntax |
| `charts-flow` | Diagram contract compliance | All required diagrams per `DIAGRAM_STANDARDS.md` |
| `adr-roadmap` | ADR aggregation | Roadmap references every ADR exactly once |
| `project-init` | Scaffold (sandboxed) | Produces 8 layer dirs + governance + registry |
| `project-adopt` | Adopt existing tree | Adoption report enumerates ≥ 8 layers detected |
| `project-profile` | Profile chain | Reports plugin version + layer count + readiness |

Each utility probe runs independently. One failure logs FAIL but
doesn't halt the rest.

## 8. Phase 4 — Agents, command, hook (13 elements)

### 8.1 Agents (11)

Per `docs/AGENTS.md`, each agent invocation must produce ≥ N words
(varies per agent role; see `AGENTS` table in `test-acceptance.sh`).
Pass criteria thresholds prevent empty-output false-PASS.

### 8.2 Command (1)

`/aidoc-flow:save-plan` invoked in a sandboxed Claude Code session.
Pass criteria: produces a non-empty plan file under
`sandbox/save-plan/plans/`.

### 8.3 Hook (1) — deterministic

`hooks/sdd-doc-review.sh` synthetically invoked with a fake
PostToolUse JSON payload pointing at a staged BRD-01.md from the
`brd-broken-sections` fixture. Pass criteria:

- `hooks.json` is valid JSON; references `PostToolUse` + `Write|Edit`
  - `sdd-doc-review.sh`
- Hook exits 0 (advisory — must never block)
- Hook output is valid JSON, includes `doc-brd-audit` nudge, and
  includes `STRUCT01` / "structural findings" text

This is the only Phase-4 check that runs in `--no-live` mode.

## 9. Design decisions

| Decision | Choice | Rationale |
|---|---|---|
| Driver location | `tests/scripts/test-acceptance.sh` | Sibling to existing test runners; tier-6 release gate |
| Output routing | Cascade autopilot → `docs/`. Audit → `.aidoc/audit/`. Fixer → `.aidoc/remediation/`. review-team → `.aidoc/review/`. doc-validator/doc-ref/gate-check → `.aidoc/validation/`. security-audit → `.aidoc/security/`. quality-advisor → `.aidoc/quality/`. Other utility/agent/command → `logs/<TS>/elements/` | Three-tier separation: `docs/` is the chain, `.aidoc/` is the AI provenance, `logs/` is the tool internals |
| Log layout | Flat `logs/<TS>/elements/<name>.log`; YAML front-matter + raw stdout in a single file | Single file per element; easier enumeration |
| Per-element failure isolation | One failure logs FAIL but doesn't halt subsequent elements within the phase | Diagnosable single-pass run |
| Phase gating | Phase 0 failure stops; Phase 1 failure skips Phase 2; Phase 1 failure does NOT skip Phases 3 + 4 | Maximises diagnostic surface area |
| Fail-fast override | `--fail-fast` flag halts on first failure | Useful when debugging |
| Live mode default | ON when invoked from `release.yml`; CLI default also ON | Release gate; `--no-live` is for local dev |
| `--mock=<run-dir>` | Replays a prior recorded run's `elements/<name>.log` files | Zero-cost script-development iteration |
| `--skip-completed` | Reads prior run's `summary.json`, reuses PASSed elements | Cheap iteration on a single failing skill |
| `--from-layer=<name>` | Resume cascade from named layer; previous layer in `docs/` becomes upstream | Resume after partial cascade aborts |
| `--to-layer=<name>` | Cascade stops after the named layer | With `--from-layer` gives single-layer-only |
| `--element=<name>` | Run only the named element; infer phase; resolve upstream | "Generate just the PRD" iteration |
| `--no-live` / `--dry-run` | Prints the planned-execution summary, then runs the full deterministic suite (Phase 0 preflight + 3 of 6 negative fixtures + hook). Any element requiring LLM records SKIP. `--dry-run` is a clean alias kept for the conventional name. | Preview + infrastructure check before spending tokens |
| `--force` | Bypass docs/`.aidoc/` unstaged-changes safety belt | Allow intentional overwrites |
| Per-skill timeout | `SKILL_TIMEOUT=600` default, `REVIEW_TEAM_TIMEOUT=1800`, `AGENT_TIMEOUT=600`; wrapped via `timeout` | Single stuck skill no longer hangs the run |
| Per-layer runtime cap | `MAX_LAYER_SEC=900` (15 min). Cascade aborts if a layer exceeds | Detects stuck-skill scenarios early |
| Cost cap | `MAX_TOTAL_OUTPUT_TOKENS=1500000` (~$25). Cumulative tokens_out tracked; aborts if exceeded | Prevents runaway spend |
| Retry policy | 3× exponential backoff (5s, 10s, 20s) on transient HTTP errors: rate limit / 5xx / overloaded / temporarily | Distinguishes transient infra failures from skill instability |
| Resume on interrupt | `trap _on_exit EXIT` rewrites RUNNING → INTERRUPTED; incremental `summary.json` writes | `Ctrl-C` mid-run leaves a usable checkpoint |
| Promotion | `--promote` runs `git add docs/ .aidoc/` + commit; `--push` pushes | Local runs don't pollute `docs/` until explicitly committed |
| CHG phase scope | One hand-curated change per example at `examples/<NAME>/chg/test-change.md` | Realistic stakeholder-style change request |
| Negative-fixture location | Shared at `tests/acceptance/fixtures/negative/`; per-example additions optional | Fixtures are structural defects, not domain-specific |
| Failure budget per layer | One auto-`fixer` attempt, then fail | Real release behavior |
| Token budget enforcement | `T4L: 1_000_000` ceiling in `release.yml` token ledger | Accommodates the 4-phase acceptance run |
| First-bootstrap behavior | Phase 0 detects empty `examples/<NAME>/docs/`; cascade writes there directly | First run populates `docs/` from scratch |
| Project profile bootstrap | If `.aidoc/profile.yaml` missing, copy `framework/governance/REVIEW_CREWS.yaml` | Honours `framework/governance/ADAPTATION.md` |
| Argument pattern | First positional arg is `<example-name>`; one example per invocation. `--all` deferred to Phase B | Explicit is safer than auto-discovery |

## 10. Token cost ballpark

| Phase | Estimated output tokens | Notes |
|---:|---:|---|
| 0 — Bootstrap & preflight | < 5 000 | Manifest validate + lint smoke; mostly deterministic |
| 1.1 — Happy-path cascade | 250 000 – 350 000 | 8 layers × ~3 skill invocations |
| 1.2 — Negative validation | 30 000 – 50 000 | ~6 fixtures × audit invocation |
| 2 — CHG | 50 000 – 80 000 | 4 skills × moderate output |
| 3 — Utilities (14) | 150 000 – 200 000 | Includes minimum-coverage probes |
| 4 — Agents + command + hook (13) | 80 000 – 120 000 | 11 agents × moderate; command + hook deterministic |
| **Total per `--live` run** | **~565 000 – 805 000** | **≈ $11 – 20** |

Acceptable as a release gate. The `T4L` token-ledger ceiling in
`release.yml` is set to **1M** to accommodate this run shape with
~25% headroom.

## 11. Adding a new example

Adding a new example seed (e.g. `payment-gateway`) requires no script
changes:

1. Create `examples/<NEW-NAME>/seed/initial-requirements.md`.
2. Create `examples/<NEW-NAME>/chg/test-change.md` in the §6 format.
3. (Optional) Create `examples/<NEW-NAME>/negative-fixtures/` for
   domain-specific failure modes; the shared base set at
   `tests/acceptance/fixtures/negative/` covers all structural defects.
4. Run `bash tests/scripts/test-acceptance.sh <NEW-NAME>` to verify
   the acceptance suite passes against the new seed.
5. Wire the new example name into `release.yml` if it should gate
   releases.

## 12. CI integration (`release.yml`)

Wired in the parent repo's `release.yml`. On tag push (`v*` or
`claude-code-plugin/v*`):

```yaml
- name: Run acceptance suite (release gate)
  timeout-minutes: 60
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: bash framework/tests/scripts/test-acceptance.sh url-shortener --live --promote --push

- name: Upload acceptance logs
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: acceptance-logs-${{ github.sha }}
    path: framework/examples/*/logs/
    retention-days: 30
```

⚠️ `--push` from CI requires write access to the framework repo (the
default `GITHUB_TOKEN` only has write access to the parent repo). Until
a framework PAT is configured, the workflow's `--push` step will fail;
run the cascade locally (`--promote` without `--push`), then push
manually.

## 13. Phase B — deferred work

Not blocking the suite's release-gate use; tracked for future
iterations:

| ID | Description |
|---|---|
| B1 | `--all` flag for multi-example runs |
| B2 | Per-example acceptance config (`examples/<NAME>/acceptance-config.yaml`) — per-skill weights/thresholds when ≥2 examples exist |
| B3 | Skill-version drift tracking — archive skill-manifest hashes alongside the chain |
| B4 | Variance quantification — Jaccard overlap between consecutive runs of the same seed |
| B5 | Phase 3 parallelism — utility probes are independent; ~3× speedup |
| B6 | Performance benchmarking — token cost trend per release |
| B7 | Per-phase token budget split — replace single `T4L` ceiling |
| B8 | Exact token tracking via `claude -p --output-format=json` (current implementation is bytes/4 estimate) |
| B9 | P6 framework-side audit — exercise single-element runs in `--mock` mode; surface any skill prompts that need adjustment for partial-execution support |

## See also

- [`../framework/docs/AIDOC.md`](../framework/docs/AIDOC.md) — `.aidoc/` provenance tier definition
- [`../framework/governance/REVIEW_TEAM.md`](../framework/governance/REVIEW_TEAM.md) — multi-persona review model
- [`../framework/governance/REVIEW_REMEDIATION_FLOW.md`](../framework/governance/REVIEW_REMEDIATION_FLOW.md) — review/remediation gate flow
- [`../framework/governance/ADAPTATION.md`](../framework/governance/ADAPTATION.md) — `.aidoc/profile.yaml` semantics
- [`README.md`](README.md) — test-suite navigation hub
- [`../plans/ACCEPTANCE-SUITE-HISTORY.md`](../plans/ACCEPTANCE-SUITE-HISTORY.md) — project-level history (per-PR record + v1→v4 plan evolution)
- `../examples/<NAME>/README.md` — per-example specifics (seed summary, CHG content)
