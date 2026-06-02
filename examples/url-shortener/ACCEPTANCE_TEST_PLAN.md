# Acceptance test plan — url-shortener

This plan describes the pre-deployment acceptance test that exercises every
plugin surface element against the `url-shortener` seed. The chain it
produces is the release-gate evidence that the plugin works end-to-end
across its full surface.

**Status**: **implemented and ready for live execution.** The driver script,
schemas, fixtures, profile bootstrap, output routing, and CI wiring are
all in place. The first `--live` cascade run is the only outstanding
operational step — the suite itself is production-ready.

**Quick start** (post-PR-A/B):

```bash
cd framework
bash tests/scripts/test-acceptance.sh url-shortener --no-live   # smoke
bash tests/scripts/test-acceptance.sh url-shortener --live      # full run
bash tests/scripts/test-acceptance.sh url-shortener --live --promote --skip-completed
```

**Revision history**:

- v1 — initial plan (50 skills only, happy path).
- v2 — gap-closure pass: agents/command/hook coverage, negative-fixture
  validation, schema definitions, `--promote` algorithm, bootstrap path,
  API-layer retry policy, run-duration cap, CI artifact upload.
- v3 — closed the 5 open questions: archive-first `docs/` policy;
  first-arg `<example-name>`; raise `T4L` ledger 500K → 1M; hand-curated
  CHG change-sets per example; negative fixtures shared under
  `tests/acceptance/fixtures/negative/`.
- **v4 — current (post-implementation, 2026-06-02)**: three-tier output
  separation landed (`docs/` + `.aidoc/` + `logs/`); cascade writes
  directly to `docs/` (no intermediate); audit/review/remediation/
  validation/security/quality route to `.aidoc/<category>/`; logs
  collapsed to flat `logs/<TS>/elements/<name>.log` with YAML
  front-matter; profile bootstrap; `--force` safety belt; per-skill
  timeout; cost cap; retry on transient errors; `--from-layer` resume;
  `--skip-completed` iteration; framework spec bumped 0.11.0 → 0.11.1
  for the `framework/docs/AIDOC.md` addition. Schema bumped to v1.1.

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
# Full run against url-shortener (release-candidate gate; --live is the default)
bash tests/scripts/test-acceptance.sh url-shortener

# Skip live LLM calls (cheap structural-only mode, ~5 seconds)
bash tests/scripts/test-acceptance.sh url-shortener --no-live

# Exercise one element only
bash tests/scripts/test-acceptance.sh url-shortener --element=doc-flow

# Exercise one phase only
bash tests/scripts/test-acceptance.sh url-shortener --phase=cascade

# Resume cascade from a specific layer (e.g. after partial run)
bash tests/scripts/test-acceptance.sh url-shortener --from-layer=spec

# Re-use prior run's PASS outcomes (iteration mode; reads prior summary.json)
bash tests/scripts/test-acceptance.sh url-shortener --skip-completed

# Replay a recorded run (dev-iteration; no Claude calls)
bash tests/scripts/test-acceptance.sh url-shortener --mock=logs/2026-06-01T120000

# Bypass --force safety belt (allow overwrite when docs/ has unstaged changes)
bash tests/scripts/test-acceptance.sh url-shortener --live --force

# Promote: git add docs/ .aidoc/ + commit (release tagging)
bash tests/scripts/test-acceptance.sh url-shortener --live --promote

# CI-style: promote and push back to origin
bash tests/scripts/test-acceptance.sh url-shortener --live --promote --push
```

### Three-tier output layout (as implemented)

The acceptance suite writes outputs to three explicit tiers, plus
ephemeral logs:

```text
examples/<NAME>/
├── seed/, chg/                  # human inputs (committed)
├── docs/                        # AI outputs — the produced chain
│   ├── 01_BRD/BRD-01.md         (cascade autopilot writes here directly)
│   ├── 02_PRD/PRD-01.md
│   ├── …
│   └── .version                 (records the plugin version of this chain)
├── .aidoc/                      # AI provenance (committed; see framework/docs/AIDOC.md)
│   ├── profile.yaml             (project profile — bootstrapped from framework default)
│   ├── audit/<NN>_<LAYER>-audit.md      (doc-<layer>-audit outputs)
│   ├── remediation/<NN>_<LAYER>-fix.md  (doc-<layer>-fixer outputs)
│   ├── review/<layer>-consensus.md      (review-team consensus per layer)
│   ├── review/.blackboard/              (transient per-persona scratch; gitignored)
│   ├── validation/<report>.md           (doc-validator / doc-ref / gate-check)
│   ├── security/review.md               (security-audit)
│   └── quality/suggestions.md           (quality-advisor)
└── logs/<TS>/                   # tool internals (gitignored, ephemeral)
    ├── plugin-test.log          # driver flow trace only
    ├── summary.txt              # human-readable per-element table
    ├── summary.json             # machine-readable (validates against schema v1.1)
    ├── elements/                # one file per element (skills, agents, command,
    │   ├── <name>.log           # hook, fixtures, negatives): YAML front-matter
    │   └── …                    # + raw skill/agent stdout
    └── sandbox/                 # tmp work for project-init, save-plan, hook test
```

The flat `elements/` directory replaces the old phase-subdir layout
(`bootstrap/skills/agents/command/hook/negative/`). Element metadata
(name, kind, phase, outcome, duration, audit_score, tokens_out, …) is
encoded as YAML front-matter at the top of each `<name>.log` file.

`logs/<TS>/` is ephemeral (`.gitignored`); `docs/` and `.aidoc/` are
committed and become the release evidence. `--promote` runs `git add` +
`git commit` to record them; see §3.2.

### 3.1 `summary.json` schema (v1.1)

Committed at `tests/scripts/test-acceptance.schema.json`. Top-level
shape:

```json
{
  "schema_version": "1.1",
  "run_id": "2026-06-02T180052",
  "example": "url-shortener",
  "plugin_version": "0.4.0",
  "framework_spec_version": "0.11.1",
  "outcome": "PASS",
  "counts": { "PASS": 51, "FAIL": 0, "SKIP": 0 },
  "elements": [
    {
      "schema_version": "1.1",
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
    },
    ...
  ]
}
```

Per-element metadata is the same shape, embedded as YAML front-matter
at the top of `logs/<TS>/elements/<name>.log`:

```text
---
schema_version: "1.1"
name: doc-brd-autopilot
kind: skill
phase: cascade
duration_sec: 84
outcome: PASS
audit_score: 94
audit_score_after_fixer: null
fixer_invoked: false
output_path: docs/01_BRD/BRD-01.md
tokens_in: null
tokens_out: 9821
error: null
---

<captured skill stdout follows here>
```

Field semantics:

- `audit_score` — initial audit score
- `audit_score_after_fixer` — non-null only when the fixer was
  invoked; the final gating value is whichever is non-null and later
- `tokens_in` — exact input-token count (deferred; populated once
  `--output-format=json` wiring lands in a follow-up)
- `tokens_out` — estimated output-token count (bytes / 4 approximation
  during PR B; exact deferred)
- `output_path` — relative path under `examples/<NAME>/` (typically
  under `docs/`, `.aidoc/<category>/`, or `logs/<TS>/sandbox/`)

### 3.2 `--promote` algorithm

When `--promote` is set (or the script is invoked from `release.yml` on a
tag push) and **all phases passed**:

1. Resolve plugin version from
   `framework/platforms/claude-code-plugin/VERSION` (e.g. `0.4.0`).
2. `git add examples/<NAME>/docs examples/<NAME>/.aidoc` —
   cascade already wrote there directly (no copy step).
3. If `git diff --cached --quiet` (no staged changes), no-op exit 0
   (a re-run produced byte-identical content).
4. `git commit -m "chore(examples): promote <NAME> cascade for v<X.Y.Z>
   release"` with the run timestamp in the body.
5. If `--push` was also passed, `git push`.

The cascade writes to `docs/` directly during the run, so promote is a
single git transaction rather than a copy operation. The legacy
"archive previous to docs-archive/" step is deferred — for now, git
history serves as the archive. If formal per-release archiving is
needed later, add a separate `--archive` flag (Phase B item).

⚠️ Pre-cascade safety belt (the `--force` flag, §A12 in the
implementation plan): the suite refuses to start a live cascade if
`docs/` or `.aidoc/` have unstaged changes, unless `--force` is
passed. Prevents accidental overwrite of in-progress human edits.

---

#### Legacy promote algorithm (pre-PR-A — superseded)

The original design used a two-stage model: cascade wrote to
`logs/<TS>/cascade/`, then `--promote` did `rsync -a --delete` from
there into `examples/<NAME>/docs/`, archiving the previous `docs/` to
`docs-archive/v<previous-version>/`. PR A eliminated the intermediate
— cascade writes directly to `docs/`, so promote is just `git
add` + `git commit` (above).

Archive-to-`docs-archive/` is deferred as Phase B work; git history
serves as the regression baseline. If formal per-release archiving
becomes important (e.g. post-1.0 with longer release cadence), add a
separate `--archive` flag that tars `docs/` into
`docs-archive/v<X.Y.Z>.tar.gz` before next run overwrites.

### 3.3 Tier placement

This is a **Tier 6 — Release gate** test in the pyramid (see
[`tests/README.md`](../../tests/README.md)). It runs only with `LIVE=1`
and is wired into `release.yml`, not into `pr-checks.yml`. CI artifact
upload step in §13.

## 4. Phase 0 — Bootstrap & preflight

Runs first; gates whether subsequent phases can run. As implemented
this is 7 sequential checks (records 6 fixtures + 1 internal):

1. **Seed presence**: `examples/<NAME>/seed/initial-requirements.md`
   must exist.
2. **Manifest validate**: `claude plugin validate <plugin-dir> --strict`
   must pass.
3. **`--force` safety belt** (A12): refuse to run live cascade if
   `examples/<NAME>/{docs,.aidoc}/` have unstaged changes, unless
   `--force` is passed. Prevents accidental overwrite of in-progress
   human edits.
4. **Project profile** (A11): if `examples/<NAME>/.aidoc/profile.yaml`
   exists, use it as-is. If missing, copy
   `framework/governance/REVIEW_CREWS.yaml` as the framework default.
   The suite never authors a non-default profile. If both are missing,
   fail-fast.
5. **`sdd_doc_lint` smoke**: lint the existing `examples/<NAME>/docs/`
   if non-empty. Must report zero findings if present. Acceptable to
   be empty (first-run bootstrap state — sets `bootstrap_mode=true`
   for downstream phases).
6. **Negative-fixture presence check**: confirm
   `tests/acceptance/fixtures/negative/` exists with the six fixtures
   in §5.2. Required for Phase 1 negative validation.
7. **API auth check** (live mode only): `claude` CLI on PATH and
   either `ANTHROPIC_API_KEY` set OR `claude -p` interactive login
   responding. Fail-fast if neither works.

Bootstrap mode (`docs/` empty): Phase 2 (CHG) is skipped; Phase 3
utilities and Phase 4 agents run against the freshly-produced `docs/`
content from Phase 1.
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
| Output routing (A1+A2) | Cascade autopilot → `docs/<NN>_<LAYER>/`. Audit → `.aidoc/audit/`. Fixer → `.aidoc/remediation/`. review-team → `.aidoc/review/`. doc-validator/doc-ref/gate-check → `.aidoc/validation/`. security-audit → `.aidoc/security/`. quality-advisor → `.aidoc/quality/`. Utility/agent/command output → `logs/<TS>/elements/` | Three-tier separation: `docs/` is the chain, `.aidoc/` is the AI provenance, `logs/` is the tool internals |
| Log layout (A3+A4) | Flat `logs/<TS>/elements/<name>.log`; YAML front-matter (meta) + raw stdout in a single file | Halves file count vs the old phase-subdir + separate `.meta.json` layout |
| Archive policy | Deferred (Phase B). Git history serves as the regression baseline | Pre-1.0 release cadence is short; formal archiving with `--archive` flag if/when post-1.0 needs it |
| Per-element failure isolation | One failure logs FAIL but doesn't halt subsequent elements within the phase | Diagnosable single-pass run; failures don't mask other failures |
| Phase gating | Phase 0 failure stops; Phase 1 failure skips Phase 2; Phase 1 failure does NOT skip Phases 3 + 4 (utilities + agents can still exercise) | Maximises diagnostic surface area |
| Fail-fast override | `--fail-fast` flag halts on first failure | Useful when debugging a single failing element |
| `--live` mode default | ON when invoked from `release.yml`; CLI default also ON | Release gate; deterministic-only is for local dev |
| `--mock=<run-dir>` mode | Replays a prior recorded run's `elements/<name>.log` files | Zero-cost iteration during script development |
| `--skip-completed` (A6) | Reads prior run's `summary.json`, reuses PASSed elements | Cheap iteration on a single failing skill |
| `--from-layer=<name>` (A7) | Resume cascade from named layer; previous layer in `docs/` becomes upstream | After partial cascade aborts, resume without re-running passed layers |
| `--force` safety belt (A12) | Refuses cascade if `docs/` or `.aidoc/` have unstaged changes; bypass with `--force` | Prevents accidental overwrite of in-progress human edits |
| Per-skill timeout (B4) | `SKILL_TIMEOUT=600` default, `REVIEW_TEAM_TIMEOUT=1800`, `AGENT_TIMEOUT=600`. Wrapped via `timeout` | Single stuck skill no longer hangs the run indefinitely (review-team observed 32 min in prior run) |
| Per-layer runtime cap (B2) | `MAX_LAYER_SEC=900` (15 min). Cascade aborts if a layer exceeds | Detects stuck-skill scenarios early without aborting healthy long cascades |
| Cost cap (A8) | `MAX_TOTAL_OUTPUT_TOKENS=1500000` (~$25). Cumulative tokens_out tracked; aborts if exceeded | Prevents runaway spend |
| Retry policy (A9) | 3× exponential backoff (5s, 10s, 20s) on transient HTTP errors: rate limit / 5xx / overloaded / temporarily | Distinguishes transient infra failures from skill instability |
| Promotion to release evidence | Manual `--promote` flag (or auto when invoked from `release.yml` on tag push); algorithm in §3.2 | Local runs don't pollute `docs/`/`.aidoc/`; tagged releases do |
| CHG phase scope | One hand-curated change committed at `examples/<NAME>/chg/test-change.md` (format defined in §6) | Realistic stakeholder-style change request; per-example tailoring |
| Negative-fixture location | Shared at `tests/acceptance/fixtures/negative/`; per-example additions optional at `examples/<NAME>/negative-fixtures/` | Fixtures are structural defects, not domain-specific; DRY across examples |
| Failure budget per layer | One auto-`fixer` attempt, then fail | Real release behavior |
| Token budget enforcement | `T4L: 1_000_000` ceiling in `release.yml` token ledger | Accommodates the 4-phase acceptance run with ~25% headroom |
| First-bootstrap behavior | Phase 0 detects empty `examples/<NAME>/docs/`; cascade writes there directly so Phases 3 + 4 have a chain to exercise | The first run populates `docs/` from scratch |
| Project profile bootstrap (A11) | If `.aidoc/profile.yaml` missing, copy `framework/governance/REVIEW_CREWS.yaml` as default; suite never authors a non-default profile | Honours `framework/governance/ADAPTATION.md` ("the single input an engine reads") |
| Advisory-skill thresholds | Per-skill minimum coverage values in §7 + §8 (calibrated against first partial-run output) | Prevents empty-output false-PASS |
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

## 11. Implementation status

All implementation work is **complete and merged**. The suite is ready
for live execution. Status table:

| # | Item | PR | Status |
|---:|---|:---:|:---:|
| 1 | Driver skeleton + Phase 0 + Phase 1.1 + schemas + `--mock` | #53 | ✅ merged |
| 2 | Phase 1.2 negative validation + shared fixtures + `chg/test-change.md` + Phase 2 CHG | #54 | ✅ merged |
| 3 | Phase 3 — 14 utility probes | #55 | ✅ merged |
| 4 | Phase 4 — 11 agents + command + hook | #56 | ✅ merged |
| 5 | `--promote` + README + CHANGELOG (Impl-5) | #57 | ✅ merged |
| 6 | Plan restructure (this doc, v3) | #59 | ✅ merged |
| 7 | Three-tier output separation + flat logs + Phase 0 + redesigned `--promote` (PR A) | #60 | ✅ merged |
| 8 | Script tightening: B4-B6 + A6-A9 + C2/C3 calibrations + doc pass + AIDOC.md + spec 0.11.1 (PR B) | #61 | ✅ merged |
| 9 | Parent `release.yml` acceptance wiring | (parent #7) | ✅ merged |

**Only outstanding step: first live cascade run** — a one-command
operational step the user kicks off when ready. Token cost ~$15-25,
wall-clock 60-120 min.

### Reproducing the smoke verification

```bash
cd framework
bash tests/scripts/test-acceptance.sh url-shortener --no-live
# Expected: PASS (8 PASS, 0 FAIL, 43 SKIP, 51 total)
#   by phase: bootstrap=6, cascade=8, negative=6, chg=4,
#             utilities=14, agents=11, command=1, hook=1
```

### Kicking off the first live cascade

```bash
cd framework

# Conservative: review output before committing
bash tests/scripts/test-acceptance.sh url-shortener --live

# Or: promote on success (commits docs/ + .aidoc/ to current branch)
bash tests/scripts/test-acceptance.sh url-shortener --live --promote

# Or: promote + push back to origin (CI-style)
bash tests/scripts/test-acceptance.sh url-shortener --live --promote --push
```

Iteration helpers (after a partial or failing run):

```bash
# Resume after the cascade aborted at layer 6
bash tests/scripts/test-acceptance.sh url-shortener --live --from-layer=spec

# Re-run only the elements that didn't PASS last time
bash tests/scripts/test-acceptance.sh url-shortener --live --skip-completed

# Override the safety belt when intentionally overwriting in-progress work
bash tests/scripts/test-acceptance.sh url-shortener --live --force
```

Token cost cap (default 1.5M output ≈ $25) and per-skill timeouts
(10 min / 30 min review-team) prevent runaway runs.

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

Already wired in the parent repo's `release.yml` (see aidoc-flow#7).
On tag push (`v*` or `claude-code-plugin/v*`):

```yaml
- name: Run acceptance suite (release gate)
  timeout-minutes: 60
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: bash framework/tests/scripts/test-acceptance.sh url-shortener --live --promote --push

- name: Upload acceptance logs
  if: always()  # upload on PASS and FAIL
  uses: actions/upload-artifact@v4
  with:
    name: acceptance-logs-${{ github.sha }}
    path: framework/examples/*/logs/
    retention-days: 30
```

⚠️ `--push` from CI requires write access to the framework repo (the
default `GITHUB_TOKEN` only has write access to the parent repo). See
PR #7's discussion — currently the workflow assumes a future PAT
secret. Until that's configured, run the cascade locally (`--promote`
without `--push`), then push manually.

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

### v4 — post-implementation reconciliation (2026-06-02)

After the first partial live run (cancelled at ~110 min, 5/8 layers
done) surfaced concrete design issues, the restructure plan
(`plans/ACCEPTANCE-SUITE-FIXES-PLAN.md`) landed in two PRs.

| Change | Where addressed |
|---|---|
| Cascade output ended up in `logs/` instead of `docs/` (the two-stage promote design conflated working state with canonical state) | A1 — cascade writes to `docs/` directly. `--promote` becomes `git commit`. PR #60 |
| Audit/fix/review reports polluted cascade dirs | A2 — routed to `.aidoc/<category>/`. PR #60 |
| Log layout was phase-subdir + separate `.meta.json` per element | A3 + A4 — flat `logs/<TS>/elements/`; YAML front-matter combined with raw stdout. PR #60 |
| `.aidoc/` was treated as gitignored "blackboard"; should be the third committed tier | Three-tier separation; `.gitignore` split (`.aidoc/review/.blackboard/` only). New `framework/docs/AIDOC.md`. PR #60 + #61 |
| Project profile not honoured by the suite | A11 — Phase 0 bootstraps `.aidoc/profile.yaml` from `framework/governance/REVIEW_CREWS.yaml` if missing. PR #60 |
| Cascade silently overwrote `docs/` even with uncommitted edits | A12 — `--force` safety belt. PR #60 |
| Lint ran against whole layer dir (audit reports + tmp/backup polluted output) | B1 — lint targets `$artifact` only. PR #60 |
| Global 45-min runtime cap aborted healthy long cascades | B2 — per-layer 15-min cap. PR #60 |
| review-team persona-extraction grep picked up `weight:` lines | B3 — Python YAML parse of `profile.yaml`. PR #60 |
| No per-skill timeout — review-team ran 32 min unbounded | B4 — `timeout` wrapper (600s default / 1800s review-team / 600s agents). PR #61 |
| Fixer left `tmp/backup/` dirs tripping HASH01 lint check | B5 — `rm -rf $layer_dir/tmp` post-fixer + prompt instructs skill. PR #61 |
| `tokens_in`/`tokens_out` always null | B6 — output-bytes ÷ 4 estimation (exact via `--output-format=json` deferred). PR #61 |
| No iteration mode after partial run | A6 `--skip-completed` reads prior `summary.json` + A7 `--from-layer=<name>` resume. PR #61 |
| No cost cap | A8 `MAX_TOTAL_OUTPUT_TOKENS` (default 1.5M ≈ $25). PR #61 |
| No retry on transient HTTP errors | A9 — 3× exponential backoff on rate-limit / 5xx / overloaded patterns. PR #61 |
| `doc-validator` threshold ≥50 sized for 8-layer chain (failed on 5-layer partial) | C1 — `n_layers × 4` scale. PR #60 |
| `quality-advisor` regex `suggest\|recommend\|improve` undercounted ~5× | C2 — broader regex matching `### Layer N` + arrows + numbered/bullets. Prompt requests structured headings. PR #61 |
| `knowledge-extractor` asked for clarification instead of producing graph | C3 — directive prompt "do not ask for clarification — produce Mermaid"; regex matches Mermaid syntax. PR #61 |
| Framework spec needed bump for `framework/docs/AIDOC.md` addition | Spec **0.11.0 → 0.11.1** (patch); 52 plugin skills' `framework_spec_version` resynced. PR #61 |
| Schema bumped to reflect new combined log layout | `tests/scripts/test-acceptance.schema.json` v1.0 → v1.1. PR #60 |
