# Acceptance test plan — url-shortener

This plan describes the pre-deployment acceptance test that exercises every
plugin surface element against the `url-shortener` seed. The chain it
produces is the release-gate evidence that the plugin works end-to-end
across its full surface.

**Status**: approved for implementation. Driver script lands in a follow-up
PR; this document is the design reference.

**Revision history**:

- v1 — initial plan (50 skills only, happy path).
- v2 — gap-closure pass. Added agents/command/hook coverage, negative-fixture
  validation, schema definitions, `--promote` algorithm, bootstrap path,
  API-layer retry policy, run-duration cap, CI artifact upload.
- **v3 — current**: closes the 5 open questions from v2. Decisions:
  archive-first `docs/` policy with retention rule; first-arg
  `<example-name>` (no auto-discover); raise `T4L` ledger 500K → 1M;
  hand-curated CHG change-sets per example with a documented file
  format; negative fixtures shared under `tests/acceptance/fixtures/negative/`.

## 1. Purpose

Drive every active element of the Claude Code plugin against the seed at
[`seed/initial-requirements.md`](seed/initial-requirements.md) and verify
the resulting output meets release criteria.

This is **not** a demo regeneration workflow — it is the pre-deployment
gate. The seed is the test input; the produced chain is the proof that
the release passes acceptance.

A second example (`payment-gateway`, `multi-tenant`, etc.) added later
will follow the same plan with its own seed.

## 2. Scope — what gets exercised

All active plugin surface elements (63 total), grouped into four phases,
plus a negative-fixture validation pass.

| Phase | Surface elements | Count |
|------:|--------|------:|
| 0 — Bootstrap & preflight | manifest validate (`--strict`) + `sdd_doc_lint` smoke + state detection | (infrastructure) |
| 1 — Layer cascade | `doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}-{base,autopilot,audit,fixer}` × negative-fixture validation | 32 |
| 2 — Change management | `doc-chg`, `doc-chg-{autopilot,audit,fixer}` | 4 |
| 3 — Cross-cutting utilities | `doc-flow`, `doc-validator`, `doc-ref`, `doc-naming`, `gate-check`, `quality-advisor`, `security-audit`, `review-team`, `knowledge-extractor`, `charts-flow`, `adr-roadmap`, `project-init`, `project-adopt`, `project-profile` | 14 |
| 4 — Agents, command, hook | 11 agents + `/aidoc-flow:save-plan` + `hooks/sdd-doc-review.sh` | 13 |
| **Total surface elements** | | **63** |

The 2 deprecated stubs (`doc-review`, `trace-check`) are not exercised —
they exist only to redirect users to their replacements.

## 3. Architecture

### Driver: `tests/scripts/test-acceptance.sh`

A new sibling to the existing `test-plugin.sh`, `test-layer.sh`, and
`test-fullpath.sh` scripts. Independent of the tier-based dispatcher
because the acceptance run has a fundamentally different shape (63
individual invocations, per-element logging, real seed→chain cascade).

### Usage

First positional argument is always the example name. To run multiple
examples, invoke the script once per example (a future `--all` flag is
tracked as Phase B work).

```bash
# Full run against url-shortener (release-candidate gate)
bash tests/scripts/test-acceptance.sh url-shortener

# Skip live LLM calls (cheap structural-only mode, ~30 seconds)
bash tests/scripts/test-acceptance.sh url-shortener --no-live

# Exercise one element only
bash tests/scripts/test-acceptance.sh url-shortener --element=doc-flow
bash tests/scripts/test-acceptance.sh url-shortener --element=agent:requirements-analyst

# Exercise one phase only
bash tests/scripts/test-acceptance.sh url-shortener --phase=cascade

# Re-use prior run's results for already-passed elements (iteration mode)
bash tests/scripts/test-acceptance.sh url-shortener --skip-completed

# Replay a recorded run instead of calling Claude (dev-iteration mode, free)
bash tests/scripts/test-acceptance.sh url-shortener --mock=logs/2026-06-01T120000

# Promote run's chain output to examples/<NAME>/docs/ (release tagging)
bash tests/scripts/test-acceptance.sh url-shortener --live --promote
```

### Per-run log layout

Under `examples/<NAME>/logs/<LOG_TIMESTAMP>/`:

```text
plugin-test.log                  # overall driver flow
summary.txt                      # human-readable per-element table
summary.json                     # machine-readable per-element results
                                 # (validates against tests/scripts/test-acceptance.schema.json)
skills/
  doc-brd-autopilot.log          # captured stdout/stderr
  doc-brd-autopilot.meta.json    # see schema below
  doc-brd-audit.log
  doc-brd-audit.meta.json
  …                              # one .log + .meta.json per skill invocation
agents/
  requirements-analyst.log
  requirements-analyst.meta.json
  …                              # one .log + .meta.json per agent invocation
command/
  save-plan.log
  save-plan.meta.json
hook/
  sdd-doc-review.log
  sdd-doc-review.meta.json
cascade/
  01_BRD/BRD-01.url-shortener.md # the produced chain (sandbox copy, gitignored)
  02_PRD/PRD-01.url-shortener.md
  …
negative/
  brd-broken-sections.audit.log  # audit run against deliberately broken artifact
  brd-broken-tags.audit.log
  …                              # one per negative fixture
```

The `cascade/` and `negative/` outputs are ephemeral (`.gitignored` via
the existing `examples/*/logs/` rule). The release evidence gets promoted
to `examples/<NAME>/docs/` only when invoked with `--promote` (or when
the script is invoked from `release.yml` on a tag push). See §3.2 for
the promote algorithm.

### 3.1 `summary.json` schema (v1.0)

Committed at `tests/scripts/test-acceptance.schema.json`. Top-level shape:

```json
{
  "schema_version": "1.0",
  "run_id": "2026-06-01T120000",
  "example": "url-shortener",
  "plugin_version": "0.4.0",
  "framework_spec_version": "0.11.0",
  "started_at": "2026-06-01T12:00:00Z",
  "finished_at": "2026-06-01T12:18:42Z",
  "duration_sec": 1122,
  "live": true,
  "promoted": false,
  "outcome": "PASS",
  "tokens_in_total": 482103,
  "tokens_out_total": 318952,
  "elements": [
    {
      "kind": "skill",
      "name": "doc-brd-autopilot",
      "phase": "cascade",
      "outcome": "PASS",
      "duration_sec": 84,
      "tokens_in": 12404,
      "tokens_out": 9821,
      "output_path": "cascade/01_BRD/BRD-01.url-shortener.md",
      "audit_score": 94,
      "audit_score_after_fixer": null,
      "error": null
    },
    ...
  ]
}
```

Per-element `.meta.json` schema (v1.0):

```json
{
  "schema_version": "1.0",
  "name": "doc-brd-autopilot",
  "kind": "skill",
  "phase": "cascade",
  "started_at": "...",
  "finished_at": "...",
  "duration_sec": 84,
  "exit_code": 0,
  "outcome": "PASS",
  "tokens_in": 12404,
  "tokens_out": 9821,
  "output_path": "cascade/01_BRD/BRD-01.url-shortener.md",
  "audit_score": 94,
  "audit_score_after_fixer": null,
  "fixer_invoked": false,
  "error": null
}
```

`audit_score` is the initial audit. `audit_score_after_fixer` is non-null
only when the fixer was invoked; the final gating value is whichever is
non-null and later.

### 3.2 `--promote` algorithm

When `--promote` is set (or the script is invoked from `release.yml` on a
tag push) and **all phases passed**:

1. Resolve version from `framework/platforms/claude-code-plugin/VERSION`
   (e.g. `0.4.0`).
2. Refuse to run if the working tree has uncommitted changes (`git
   diff-index --quiet HEAD`).
3. Refuse to run if `examples/<NAME>/docs/` has uncommitted changes
   pending in the working tree (would conflict with the copy).
4. Archive existing `examples/<NAME>/docs/` (if non-empty) to
   `examples/<NAME>/docs-archive/v<previous-version>/`. If the archive
   dir already exists for that version, fail with a clear message
   (don't overwrite history).
5. `rsync -a --delete logs/<TS>/cascade/ examples/<NAME>/docs/`.
6. Commit: `chore(examples): promote url-shortener cascade for v<X.Y.Z>
   release` with the run's `LOG_TIMESTAMP` in the commit body.
7. Push only if `--push` was also passed; otherwise leave for human
   review.

First-time bootstrap (destination empty): skip step 4, proceed.

#### Retention policy

- **Pre-1.0 plugin releases**: keep every archive uncompressed. History
  is short and the comparison value is high.
- **Post-1.0**: if `docs-archive/` exceeds 5 MB, compress archives older
  than the most recent 5 releases into `docs-archive/legacy.tar.gz`.
  Never delete; the archived chains are the regression baseline.

### 3.3 Tier placement

This is a **Tier 6 — Release gate** test in the pyramid (see
[`tests/README.md`](../../tests/README.md)). It runs only with `LIVE=1`
and is wired into `release.yml`, not into `pr-checks.yml`. CI artifact
upload step in §13.

## 4. Phase 0 — Bootstrap & preflight

Runs first; gates whether subsequent phases can run.

1. **Manifest validate**: `claude plugin validate <plugin-dir> --strict`
   must pass. Same check Phase 1 of `test-plugin.sh` runs.
2. **`sdd_doc_lint` smoke**: lint the existing `examples/<NAME>/docs/` if
   non-empty. Must report zero findings if present. Acceptable to be
   empty (first-run bootstrap state).
3. **Bootstrap detection**: if `examples/<NAME>/docs/` is empty:
   - Set `bootstrap_mode=true` in run metadata.
   - Phase 2 (CHG) is **skipped** (no chain to mutate).
   - Phase 3 utilities that need a chain (`doc-validator`, `doc-ref`,
     `gate-check`, `quality-advisor`, `security-audit`, `review-team`,
     `knowledge-extractor`, `charts-flow`, `adr-roadmap`,
     `project-profile`) run against `logs/<TS>/cascade/` *after* Phase 1
     completes, not against `examples/<NAME>/docs/`.
4. **Negative-fixture presence check**: confirm
   `tests/acceptance/fixtures/negative/` exists with the six fixtures
   in §5.2. Required for Phase 1 negative validation. Per-example
   additions under `examples/<NAME>/negative-fixtures/` are optional
   and are merged on top of the shared base set when present.
5. **API auth check** (live mode only): `claude --version` returns 0
   and `ANTHROPIC_API_KEY` is non-empty. Fail-fast with clear message
   if missing.

Phase 0 failure stops the run (no subsequent phase can recover).

## 5. Phase 1 — Layer cascade (32 skills + negative validation)

Two passes: happy-path cascade (§5.1) + negative-fixture validation (§5.2).

### 5.1 Happy-path cascade

For each of the 8 layers (`brd, prd, ears, bdd, adr, spec, tdd, iplan`):

1. **Invoke `doc-<layer>-autopilot`** with the previous layer's output
   as context. For BRD, context is the seed. Output is written to
   `cascade/<NN>_<LAYER>/<TYPE>-01.url-shortener.md`.
2. **Invoke `doc-<layer>-audit`** against the produced artifact. Capture
   the readiness score (0–100). Record in `.meta.json`.
3. **If audit score < 90**, invoke `doc-<layer>-fixer` with the audit
   findings, then re-run the audit. Record both invocations.
4. **Invoke `doc-<layer>`** (the base/reference skill) against the
   artifact — serves as structural baseline. Used for cross-check, not
   gating.
5. **Run `sdd_doc_lint`** against the layer's output directory. Must
   produce zero structural findings.

Pass criteria for happy-path cascade:

- Every `-autopilot` exit 0.
- Every final `-audit` reports ≥ 90 score (after at most one fixer cycle).
- `sdd_doc_lint` reports no structural findings across all 8 layers.
- Cumulative `@brd…@tdd` traceability tags resolve.

### 5.2 Negative-fixture validation

Curated broken artifacts live at `tests/acceptance/fixtures/negative/`
(shared across all examples — these are structural defects, not
domain-specific). Per-example additions, if any, live under
`examples/<NAME>/negative-fixtures/` and are merged in at run time.

| Fixture | What's broken | Expected detection |
|---|---|---|
| `brd-broken-sections.md` | Missing required §3 (Capabilities) | `doc-brd-audit` reports STRUCT01 + score < 50 |
| `brd-broken-tags.md` | `@brd` element-IDs malformed (3-segment instead of 4) | `doc-brd-audit` reports tag-format violation |
| `prd-broken-upstream-ref.md` | References non-existent `@brd:BRD.99.x.xxxx` | `doc-validator` reports unresolved reference |
| `ears-score-7.md` | Content quality forces audit score < 50 | `doc-ears-audit` reports findings, fixer attempts repair, score improves |
| `adr-missing-sequence-diagram.md` | No required `sequenceDiagram` per ADR contract | `doc-adr-audit` reports diagram contract violation |
| `chain-trace-broken.zip` | Full chain with mid-cascade `@brd` reference to deleted upstream | `doc-validator` reports broken trace |

For each fixture: invoke the relevant audit/lint skill, **assert it
reports the expected finding**. A negative fixture that passes audit is
a regression in gating sensitivity.

Pass criteria for negative validation:

- Every fixture in the table above triggers the expected finding.
- Zero false-negatives (no broken fixture silently passes).

Cascade phase (both passes) fails the release gate if any criterion
fails.

## 6. Phase 2 — Change management (4 skills)

**Gated on Phase 1 success.** If `bootstrap_mode=true`, skipped entirely.

After the cascade completes successfully:

1. **Apply the predefined change** committed at
   `examples/<NAME>/chg/test-change.md` — e.g. for url-shortener: add a
   visit-rate analytics dashboard (a non-trivial scope expansion that
   forces re-scoping of analytics, a new ADR for storage choice, and
   downstream impacts on TDD coverage).
2. **Invoke `doc-chg`** to register the change request.
3. **Invoke `doc-chg-autopilot`** to drive the CHG-01 artifact through
   its governance flow (impact assessment, approval, propagation).
4. **Invoke `doc-chg-audit`** against the CHG-01 artifact.
5. **Invoke `doc-chg-fixer`** if audit score < 90.

Pass criteria: CHG-01 artifact passes audit, propagation surfaces the
affected downstream layers, and the propagation report enumerates each
"Expected downstream impacts" item from `chg/test-change.md` (or
explicitly flags why an item was rejected).

### `chg/test-change.md` file format

Hand-curated per example. Required structure:

```markdown
# Test change request — <one-line summary>

## Motivation
<why the change is being requested — 2–3 sentences from a stakeholder POV>

## Scope
<what's being added/removed/modified — bullet list>

## Expected downstream impacts
<which layers should propagate, predicted by the human author>

- BRD: <section/item updated>
- PRD: <section/item updated>
- EARS: <requirement updated>
- BDD: <scenario added/changed>
- ADR: ADR-NN required for <decision>
- SPEC: <component impact>
- TDD: <test coverage delta>
- IPLAN: <task delta>
```

The "Expected downstream impacts" list is what the audit phase compares
against `doc-chg-autopilot`'s actual propagation report.

## 7. Phase 3 — Cross-cutting utilities (14 skills)

Each utility gets a targeted probe against the produced chain. **Each
probe has a minimum-coverage threshold** — empty structured output is
treated as FAIL.

| Skill | Probe | Pass criteria (with coverage threshold) |
|---|---|---|
| `doc-flow` | Two modes: (a) "given chain at layer N, what's next?" routing; (b) "scan corpus, report position" | (a) returns the correct next skill; (b) reports correct current layer + ≥1 finding |
| `doc-validator` | Cumulative trace closure across BRD→IPLAN | All `@brd…@tdd` tags resolve; report enumerates ≥ 50 resolved tags (chain has ~80–120) |
| `doc-ref` | Cross-reference resolution | All inter-doc references resolve; report enumerates ≥ 8 references (one per layer) |
| `doc-naming` | Name compliance check | All artifact IDs match `ID_NAMING_STANDARDS.md`; report enumerates ≥ 8 IDs |
| `gate-check` | Aggregate readiness gate | Confirms all 8 layers ≥ 90 |
| `quality-advisor` | Improvement suggestions | Produces ≥ 1 actionable suggestion per layer (≥ 8 total) |
| `security-audit` | Security review | Produces ≥ 1 finding *and* zero high-severity (or explicit "no findings" justification block ≥ 100 words) |
| `review-team` | Multi-persona review | Produces output from **all configured personas** per `REVIEW_CREWS.yaml` (every layer's crew); no persona's output may be empty |
| `knowledge-extractor` | Extract domain knowledge | Graph has ≥ 20 nodes (chain captures ~30–50 entities) |
| `charts-flow` | Diagram contract compliance | All required diagrams present per `DIAGRAM_STANDARDS.md` (BRD c4-l1+dfd-l1, PRD c4-l2+dfd-l2+sequence, ADR sequence, SPEC c4-l3+dfd-l3) |
| `adr-roadmap` | ADR aggregation into roadmap | Roadmap references every ADR in the chain (1:1 coverage) |
| `project-init` | Scaffold new project (sandboxed tmp dir) | Produces expected directory tree (8 layer dirs + governance + registry) |
| `project-adopt` | Adopt an existing project tree (sandboxed) | Adoption report enumerates ≥ 8 layers detected |
| `project-profile` | Profile the produced chain | Profile reports plugin version + layer count + readiness |

Each utility probe runs independently. One failure logs FAIL but doesn't
halt the rest. Final exit code is non-zero if any probe failed.

## 8. Phase 4 — Agents, command, hook (13 elements)

### 8.1 Agents (11)

Per `docs/AGENTS.md`, the agents and their probes:

| Agent | Probe | Pass criteria |
|---|---|---|
| `requirements-analyst` | Run against BRD-01 from cascade | Produces structured requirements analysis ≥ 200 words |
| `pm-orchestrator` | Run against full cascade | Produces orchestration plan referencing all 8 layers |
| `solutions-architect` | Run against SPEC-01 | Produces architecture review with C4/DFD references |
| `test-architect` | Run against TDD-01 | Produces test-strategy review |
| `software-engineer` | Run against IPLAN-01 | Produces implementation review |
| `devops-release-engineer` | Run against IPLAN-01 + ADR-01 | Produces deployment plan |
| `code-reviewer` | Run against the IPLAN's code-block examples | Produces structured review |
| `security-engineer` | Run against full cascade | Produces security review |
| `traceability-auditor` | Run against full cascade | Confirms all 4-segment IDs resolve |
| `adversary` (review-team lens) | Run against any layer via review-team | Produces adversarial findings ≥ 1 |
| `synthesizer` (review-team lens) | Run against any layer via review-team | Produces synthesis combining persona outputs |

Each agent invocation captured at `logs/<TS>/agents/<NAME>.log`. Pass
criteria thresholds prevent empty-output false-PASS (same principle as
§7).

### 8.2 Command (1)

`/aidoc-flow:save-plan` invoked in a sandboxed Claude Code session.
Expected behavior: captures the current conversation plan to a
timestamped file under `plans/`.

Pass criteria: produces a non-empty plan file at the expected path with
the expected header structure.

### 8.3 Hook (1)

`hooks/sdd-doc-review.sh` is a `PostToolUse` advisory triggered on
`Write`/`Edit` of SDD instance documents.

Pass criteria:

- Hook config (`hooks/hooks.json`) is valid JSON and references the
  correct event + matcher.
- Hook script executes without error when invoked with a sample
  `Write` payload (synthetic invocation, not a real Claude session).
- Hook script finds the vendored `sdd_doc_lint` via the bundled
  `framework/registry/`.
- Hook outputs deterministic structural findings for a synthetic
  broken artifact (re-uses Phase 1 negative fixtures).
- Hook **does not block** the edit (must exit 0 regardless of
  findings — advisory only).

## 9. Design decisions

| Decision | Choice | Rationale |
|---|---|---|
| Driver location | `tests/scripts/test-acceptance.sh` | Sibling to existing test runners; tier-6 release gate, not a tier-suite |
| Output location during run | `examples/<NAME>/logs/<TS>/cascade/` | Ephemeral, gitignored; isolates the run-as-test from the curated release evidence |
| Output location after promote | `examples/<NAME>/docs/` (latest) + `examples/<NAME>/docs-archive/v<X.Y.Z>/` (per-release snapshot) | Latest doubles as discoverable example; archive is audit trail |
| Archive retention | Pre-1.0: keep every archive uncompressed. Post-1.0: compress beyond 5 most recent if `docs-archive/` exceeds 5 MB; never delete | History is the regression baseline; the cost is trivial |
| Skip strategy for non-cascade skills | Sandboxed tmp dirs with minimal corpus per skill; no element silently skipped | Every release-gate run exercises all 63 elements; coverage is the point |
| Per-element failure isolation | One failure logs FAIL but doesn't halt subsequent elements within the phase | Diagnosable single-pass run; failures don't mask other failures |
| Phase gating | Phase 0 failure stops; Phase 1 failure skips Phase 2; Phase 1 failure does NOT skip Phases 3 + 4 (utilities + agents can still exercise) | Maximises diagnostic surface area |
| Fail-fast override | `--fail-fast` flag halts on first failure | Useful when debugging a single failing element |
| `--live` mode default | ON when invoked from `release.yml`; the CLI default is also ON | This is a release gate; deterministic-only is for local development |
| `--mock=<run-dir>` mode | Replays a prior recorded run's `.log` outputs without calling Claude | Zero-cost iteration when developing the script itself |
| Re-run cost mitigation | `--skip-completed` flag reads prior run's `summary.json`, skips PASSed elements | Speeds iteration when fixing a single failing element |
| Promotion to release evidence | Manual `--promote` flag (or auto when invoked from `release.yml` on tag push); algorithm in §3.2 | Local runs don't pollute `examples/<NAME>/docs/`; tagged releases do |
| API-layer retry policy | **Retry network/HTTP errors up to 3× with exponential backoff**; **no retries on non-zero exit with structured skill output** | Distinguishes transient infra failures from skill instability |
| CHG phase scope | One hand-curated change committed at `examples/<NAME>/chg/test-change.md` (format defined in §6) | Realistic stakeholder-style change request; per-example tailoring |
| Negative-fixture location | Shared at `tests/acceptance/fixtures/negative/`; per-example additions optional at `examples/<NAME>/negative-fixtures/` | Fixtures are structural defects, not domain-specific; DRY across examples |
| Failure budget per layer | One auto-`fixer` attempt, then fail | Real release behavior |
| Token budget enforcement | `T4L: 1_000_000` ceiling in `release.yml` token ledger (raised from 500K in this revision) | Accommodates the 4-phase acceptance run with ~25% headroom |
| Max wall-clock runtime | 45 minutes (hard-fail at 45m; GHA job timeout 60m) | Prevents indefinite hangs; allows generous overhead |
| First-bootstrap behavior | Phase 0 detects empty `examples/<NAME>/docs/`; Phases 3 + 4 run against `cascade/` output instead | Bootstrap run can populate the docs/ tree from nothing |
| Advisory-skill thresholds | Per-skill minimum coverage values in §7 + §8 | Prevents empty-output false-PASS |
| Argument pattern | First positional arg is `<example-name>`; one example per invocation. `--all` deferred to Phase B | Explicit is safer than auto-discovery; multi-example invocation can be added later cheaply |

## 10. Token cost ballpark

| Phase | Estimated output tokens | Notes |
|---:|---:|---|
| 0 — Bootstrap & preflight | < 5 000 | Manifest validate + lint smoke; deterministic mostly |
| 1.1 — Happy-path cascade | 250 000 – 350 000 | 8 layers × ~3 skill invocations |
| 1.2 — Negative validation | 30 000 – 50 000 | ~6 fixtures × audit invocation |
| 2 — CHG | 50 000 – 80 000 | 4 skills × moderate output |
| 3 — Utilities (14) | 150 000 – 200 000 | Includes the new minimum-coverage probes |
| 4 — Agents + command + hook (13) | 80 000 – 120 000 | 11 agents × moderate; command + hook deterministic |
| **Total per `--live` run** | **~565 000 – 805 000** | **≈ $11 – 20** |

Acceptable as a release gate. The `T4L` token-ledger ceiling in
`release.yml` is raised from 500K to **1M** in this revision (§13)
to accommodate this run shape with ~25% headroom for skill evolution.

## 11. Implementation plan

| Step | Description | Effort |
|---|---|---|
| 1 | Add `tests/scripts/test-acceptance.sh` skeleton: arg parsing, log layout, phase dispatch, summary aggregation | 1.5 h |
| 2 | Implement Phase 0 — bootstrap detection, manifest validate, lint smoke, API auth check | 1 h |
| 3 | Implement Phase 1.1 — happy-path cascade (autopilot + audit + fixer loop, lint, score parsing) | 2 h |
| 4 | Author shared negative fixtures under `tests/acceptance/fixtures/negative/` + implement Phase 1.2 validation | 1.5 h |
| 5 | Commit `examples/url-shortener/chg/test-change.md` in §6 format; implement Phase 2 CHG cycle | 1 h |
| 6 | Implement Phase 3 — 14 utility probes with minimum-coverage thresholds | 2.5 h |
| 7 | Implement Phase 4 — 11 agents + 1 command + 1 hook | 2 h |
| 8 | Commit `test-acceptance.schema.json` for `summary.json` + per-element `.meta.json` | 0.5 h |
| 9 | Implement `--promote` algorithm with bootstrap handling | 1 h |
| 10 | Implement `--mock` mode (replay recorded run) | 1 h |
| 11 | Wire `release.yml`: invoke acceptance on tag push, upload artifact on failure, raise `T4L` to 1M | 0.5 h |
| 12 | First successful `--live` run on url-shortener; commit `examples/url-shortener/docs/` + `examples/url-shortener/docs-archive/v0.4.0/` | 1 h |
| 13 | Update `examples/url-shortener/README.md`: reframe + per-release archive index | 0.5 h |
| 14 | CHANGELOG entry under `[Unreleased] → Added` | 0.25 h |
| **Total** | | **≈ 15.75 h** |

Token cost for the first cascade run: ~$11–20.

## 12. Subsequent example additions

Adding a new example seed (e.g. `payment-gateway`) after this script
exists:

1. Create `examples/<NEW-NAME>/seed/initial-requirements.md`.
2. Create `examples/<NEW-NAME>/chg/test-change.md` in the §6 format.
3. (Optional) Create `examples/<NEW-NAME>/negative-fixtures/` for
   domain-specific failure modes; the shared base set at
   `tests/acceptance/fixtures/negative/` covers all structural defects.
4. Run `bash tests/scripts/test-acceptance.sh <NEW-NAME>` to verify the
   acceptance suite passes against the new seed.
5. Wire the new example name into `release.yml` if it should gate
   releases alongside `url-shortener`.

No script changes required.

## 13. CI integration (`release.yml`)

On tag push (`v*` or `claude-code-plugin/v*`):

```yaml
- name: Run acceptance suite (release gate)
  timeout-minutes: 60
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: bash framework/tests/scripts/test-acceptance.sh url-shortener --live --promote

- name: Upload acceptance logs
  if: always()  # upload on PASS and FAIL
  uses: actions/upload-artifact@v4
  with:
    name: acceptance-logs-${{ github.sha }}
    path: framework/examples/*/logs/
    retention-days: 30
```

Token-ledger ceiling raised in the same step's Python block:

```python
HARD = {"T3L": 50_000, "T4L": 1_000_000, "review": 200_000, "smoke": 20_000}
```

On `--promote` success, the workflow also commits the promoted chain
back to the release branch (separate job, behind a manual approval to
avoid auto-pushes from CI).

## 14. Phase B — deferred work

Not blocking initial implementation; tracked for future passes.

| ID | Description |
|---|---|
| B1 | **`--all` flag for multi-example runs**: invoke the suite across every directory under `examples/` in one command (current behavior is one example per invocation) |
| B2 | **Multi-example acceptance config**: `examples/<NAME>/acceptance-config.yaml` with per-skill weights/thresholds (relevant when 2nd example lands; uniform algorithm fits one example) |
| B3 | **Skill-version drift tracking**: archive skill-manifest hashes alongside the chain; produce a hash-diff report between consecutive release archives |
| B4 | **Variance quantification**: collect element-ID overlap (Jaccard) between consecutive runs of the same seed; flag drops below threshold (e.g. 0.6) |
| B5 | **Phase 3 parallelism**: utility probes are independent; parallelize for ~3× speedup |
| B6 | **Mid-run abort/resume**: SIGINT/SIGTERM handler; partial `.meta.json` writes use `.partial` suffix until completion |
| B7 | **Performance benchmarking**: token cost trend per release; flag regressions where the same seed costs significantly more |
| B8 | **Per-phase token budget split**: replace single `T4L` ceiling with per-phase budgets (`T4L_CASCADE`, `T4L_CHG`, `T4L_UTILITIES`, `T4L_AGENTS`) for finer-grained cost regression signal |

## 15. Gap- and question-resolution log

### v2 — gap closure

| Gap | What was added |
|---|---|
| G1 — Agents/command/hook | New Phase 4 (§8); scope table includes 13 additional elements |
| G2 — Negative fixtures | New §5.2 with 6-fixture coverage table |
| G3 — Schemas | New §3.1 with `summary.json` + `.meta.json` v1.0 schemas; commit at `tests/scripts/test-acceptance.schema.json` |
| G4 — Promote semantics | New §3.2 with the 7-step algorithm |
| G5 — Advisory thresholds | Minimum-coverage column added to §7 + §8 probes |
| G6 — API retry policy | Layered retry: 3× backoff on network/HTTP; no retry on skill instability (§9) |
| G7 — CI artifact upload | New §13 with `upload-artifact@v4` step |
| G8 — Run duration cap | Max 45m wall-clock; GHA `timeout-minutes: 60` (§9 + §13) |
| G9 — Bootstrap behavior | New Phase 0 (§4) with `bootstrap_mode` detection; Phases 2 + 3 gating |
| G10–G15 | Logged as Phase B deferred work (§14) |

### v3 — open question closure

| Question | Decision |
|---|---|
| `docs/` policy each release | **Archive-first** with retention rule (§3.2 + §9). Pre-1.0 keep all uncompressed; post-1.0 compress beyond 5 most recent if `docs-archive/` > 5 MB |
| Multi-example arg pattern | **First positional arg = `<example-name>`**, one example per invocation (§3 usage + §9). `--all` deferred to Phase B (B1) |
| `T4L` token budget | **Raise 500K → 1M** in `release.yml` token ledger (§10 + §13). Per-phase split deferred to Phase B (B8) |
| CHG change-set source | **Hand-curated per example** at `examples/<NAME>/chg/test-change.md` with documented format (§6) |
| Negative-fixtures location | **Shared base set** at `tests/acceptance/fixtures/negative/`; per-example additions optional (§5.2 + §9). Bootstrap presence check updated (§4 step 4) |
