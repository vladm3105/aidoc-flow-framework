# Acceptance suite — architectural restructure plan

Plan to fix the script bugs, calibration issues, and output-routing/log-layout
design issues surfaced by the first live cascade run on 2026-06-01
(suspended ~110 min in, partial Phase 3).

**Status**: proposed, not yet started.
**Approach**: Single architectural restructure (no incremental Plan-A
phase) — the harness gets a coordinated re-design rather than two
sequential PRs.
**Branch base**: `main` (after `fix/auth-check-interactive-login` merges,
  which carries the already-shipped Phase 0 auth-probe fix).

## 1. What the first run validated

The first live cascade run (`logs/2026-06-01T231324/`) successfully
exercised:

- ✅ Phase 0 — Bootstrap & preflight (4/4)
- ✅ Phase 1.1 — Cascade layers 1-5 (audit scores 95–98 each;
  runtime-aborted before SPEC/TDD/IPLAN)
- ✅ Phase 1.2 — Negative validation (6/6 fixtures detected)
- ✅ Phase 2 — CHG (correctly skipped, bootstrap mode)
- ⚠️ Phase 3 — Utilities (7/14 done before suspend: 5 PASS, 3 FAIL on
  threshold/script-bug, 1 in flight)
- ⏸️ Phase 4 — Agents + command + hook (not reached)

The skills themselves all worked. Issues are entirely in the test
harness (`tests/scripts/test-acceptance.sh`), output routing, and log
layout. No plugin element needs changes.

## 2. Three-tier output separation (the architectural change)

The current design mixes "AI working notes" into `logs/<TS>/cascade/`,
treats `docs/` as a post-run promote target, and conflates execution
metadata with documentation. The restructure splits outputs into three
explicit tiers:

| Tier | Location | Lifecycle | Purpose |
|---|---|---|---|
| **Inputs** | `examples/<NAME>/{seed,chg}/` | Committed | Human-authored test inputs |
| **AI outputs (chain)** | `examples/<NAME>/docs/` | Committed | Produced 8-layer chain; the artifact |
| **AI working notes** | `examples/<NAME>/.aidoc/` | Committed | Audit, review, remediation reports — provenance documentation |
| **Tool internals** | `examples/<NAME>/logs/<TS>/` | Gitignored | Execution metadata, stdout buffers, timing, exit codes |

The first three answer "what did the AI do and what proof do we have?"
The last answers "how did the harness behave at runtime?"

### Mapping skill outputs to tiers

| Skill | Tier | Path |
|---|---|---|
| `doc-<layer>-autopilot` | docs | `docs/<NN>_<LAYER>/<TYPE>-01.md` |
| `doc-<layer>-audit` | .aidoc | `.aidoc/audit/<NN>_<LAYER>-audit.md` |
| `doc-<layer>-fixer` | .aidoc | `.aidoc/remediation/<NN>_<LAYER>-fix.md` |
| `doc-<layer>` (base/reference) | logs | `logs/<TS>/elements/doc-<layer>.log` |
| `review-team` | .aidoc | `.aidoc/review/<layer>-consensus.md` |
| `doc-validator`, `doc-ref`, `gate-check` | .aidoc | `.aidoc/validation/<report>.md` |
| `security-audit` | .aidoc | `.aidoc/security/review.md` |
| `quality-advisor` | .aidoc | `.aidoc/quality/suggestions.md` |
| Utility probes (`doc-flow`, `doc-naming`, etc.) | logs | `logs/<TS>/elements/<name>.log` |
| Agents (Phase 4) | logs | `logs/<TS>/elements/<name>.log` |
| Hook test, command test | logs | `logs/<TS>/elements/<name>.log` |

### `.gitignore` adjustment for `.aidoc/`

Current rule (line 33-35): `.aidoc/review/` is fully gitignored as
"transient blackboard". New split:

- `.aidoc/review/.blackboard/` — stays gitignored (per-persona scratch)
- `.aidoc/review/<layer>-consensus.md` — committed (final consensus)

Other `.aidoc/` subdirs (audit/, remediation/, validation/, security/,
quality/) are committed by default.

## 3. Issues catalogued

### Architectural (output routing & log layout)

| ID | Issue | Resolution |
|---|---|---|
| **A1** | Cascade writes to `logs/<TS>/cascade/`; `--promote` copies to `docs/`. Two-stage design overcomplicated; documents end up in `logs/` instead of `docs/` | Write directly to `docs/`. `--promote` becomes `git commit` |
| **A2** | Audit/fix/review reports land in cascade dirs (conflated with the artifact) | Route to `.aidoc/<category>/` per §2 mapping |
| **A3** | Log layout uses phase subdirs (`bootstrap/`, `skills/`, `agents/`, `command/`, `hook/`, `negative/`) | Single `logs/<TS>/elements/` dir; phase encoded in `.meta.json` |
| **A4** | `.log` + `.meta.json` per element = 126 small files | Combine into one `.log` with YAML front-matter metadata |
| **A5** | `--promote` algorithm assumes copy-from-logs-to-docs model | Redesign: `git add docs/ .aidoc/` + commit; `--archive` separate flag |
| **A6** | `--skip-completed` exists but never validated | Validate via `--mock` regression against a recorded run |
| **A7** | No `--from-layer=<N>` resume for partial cascades | Add flag; reads previous layer from `docs/` to bootstrap |
| **A8** | No cost cap | Add `MAX_TOTAL_OUTPUT_TOKENS` budget; abort if exceeded |
| **A9** | No retry-on-transient-API-error | Wrap `claude -p` with 3× exponential backoff on HTTP 5xx |
| **A10** | Phase 4 (agents+cmd+hook) never validated live | First post-restructure run validates; capture any new issues in follow-up |
| **A11** | Project profile (`.aidoc/profile.yaml`) not honored by the suite. Per `framework/governance/ADAPTATION.md`, this is "the single input an engine reads when authoring or auditing"; absence ≠ "use built-in defaults silently" | Phase 0 step: if `examples/<NAME>/.aidoc/profile.yaml` exists, use it as-is; if missing, copy the framework-default profile and proceed. The suite never creates a fresh one (out of scope) |
| **A12** | Cascade silently overwrites `docs/` even if user has uncommitted edits | Add `--force` safety belt: refuse to write cascade if `docs/` or `.aidoc/` has unstaged changes; bypass with `--force` |

### Bugs (still required even with architectural changes)

| ID | Location | Symptom | Severity |
|---|---|---|---|
| **B1** | `phase_1_cascade()` lint check | Lints whole layer dir, picks up audit reports + `tmp/backup/`. Resolved naturally by A2 (audit reports route to `.aidoc/`) — but lint must still target `$docs_file` not `$layer_dir` | High |
| **B2** | `MAX_RUNTIME_SEC=2700` (45 min) | Cap too tight; aborts mid-cascade. Replace with per-layer `MAX_LAYER_SEC=900` (15 min) | High |
| **B3** | `phase_3_utilities()` review-team persona grep | Regex picks up adjacent YAML keys (`weight:`) as personas. Replace with Python YAML parse of `REVIEW_CREWS.yaml` | High |
| **B4** | Per-skill `claude -p` invocations | No per-call timeout. Add `timeout`-wrapped invocation; default 600s, review-team 1800s | Medium |
| **B5** | Fixer skill leaves `tmp/backup/` directories | Either skill instruction routes to `.aidoc/remediation/` (A2 handles) or explicit `rm -rf` post-fixer | Medium |
| **B6** | `output_path`/`tokens_in`/`tokens_out` in metadata always null | Populate via `claude -p --output-format=json`; powers A8 cost cap | Medium |

### Calibration (thresholds don't match actual output)

| ID | Skill | Threshold | Observed | Fix |
|---|---|---:|---:|---|
| **C1** | `doc-validator` | ≥ 50 trace tags | 28 on 5-layer chain | Scale to `n_layers × 4` |
| **C2** | `quality-advisor` | ≥ 8 suggestions | 3 matched (regex too narrow) | Broaden regex per actual log inspection |
| **C3** | `knowledge-extractor` | ≥ 20 graph nodes | 0 matched (wrong format) | Inspect log; update regex (likely Mermaid or JSON) |

## 4. Implementation plan

| Step | Change | Cost |
|---|---|---|
| 1 | Merge `fix/auth-check-interactive-login` (auth probe — already shipped) | 0 |
| 2 | Inspect `logs/2026-06-01T231324/skills/{quality-advisor,knowledge-extractor}.log` for C2/C3 calibration | 0 |
| 3 | Inspect `framework/governance/REVIEW_CREWS.yaml` for B3 YAML parse target | 0 |
| 4 | Restructure log layout (A3+A4): single `elements/` dir, YAML front-matter combines `.log`+`.meta.json` | 0 |
| 5 | Route skill output (A1+A2): cascade → `docs/<NN>_<LAYER>/`, audit/fix/review/validation → `.aidoc/<category>/` | 0 |
| 6 | Redesign `--promote` (A5): `git add docs/ .aidoc/` + commit; `--archive` for tagged releases | 0 |
| 7 | Apply remaining bug fixes (B1-B6) and calibrations (C1-C3) | 0 |
| 8 | Add `--from-layer=<N>` resume (A7) and `MAX_TOTAL_OUTPUT_TOKENS` cap (A8) | 0 |
| 9 | Add retry wrapper for transient HTTP errors (A9) | 0 |
| 9a | Add Phase 0 profile-bootstrap (A11): check `.aidoc/profile.yaml`, copy framework default if missing, fail-fast if framework default is also missing | 0 |
| 9b | Add `--force` safety belt (A12): refuse to overwrite `docs/` / `.aidoc/` with unstaged changes unless `--force` is passed | 0 |
| 10 | Update schema (`test-acceptance.schema.json` v1.1) for new YAML front-matter format | 0 |
| 11 | Update `examples/url-shortener/README.md` with three-tier layout + `.gitignore` adjustment for `.aidoc/review/` split | 0 |
| 11b | **Framework-wide documentation pass** to introduce the `.aidoc/` concept as "AI's working notes — the documentation of provenance" — see §4a below | 0 |
| 12 | Validate `--skip-completed` via `--mock` against recorded run (A6) | 0 |
| 13 | `--no-live` smoke regression | 0 |
| 14 | `--live` re-run (no `--promote`) to validate full 8-layer cascade | ~$10-15 |
| 15 | If PASS: `--live --promote` to land the chain into `docs/` + `.aidoc/` | $0 (re-uses cached if same run) |
| 16 | Phase 4 validation findings → follow-up plan if needed (A10) | 0 |

## 4a. Framework-wide documentation pass

The three-tier output separation introduces `.aidoc/` as a first-class
concept across the framework. Several documents need to be updated to
introduce and define it consistently. Core message to land in each:

> **`.aidoc/` is "AI's working notes" — the documentation of
> provenance.** It holds the audit, review, remediation, validation,
> security, and quality reports the AI personas produced while
> authoring the chain. Committed alongside `docs/` so the question
> "how did the AI arrive at this output?" can be answered from the
> repo without re-running the suite.

### Files to update

| File | What changes |
|---|---|
| `framework/README.md` | Add a brief "Inputs / Outputs / Provenance / Logs" section describing the four-tier layout under every `examples/<NAME>/` (seed/, chg/ as inputs; docs/ as outputs; `.aidoc/` as provenance; logs/ as tool internals) |
| `framework/docs/PROJECT.md` | Define `.aidoc/` in the structural-conventions section. Cross-reference REVIEW_REMEDIATION_FLOW.md |
| `framework/docs/REPO_STRUCTURE.md` | List `examples/<NAME>/.aidoc/` in the repo-layout table with its purpose |
| `framework/governance/REVIEW_REMEDIATION_FLOW.md` | Replace any references to "review/remediation reports live in logs/" with the new `.aidoc/audit/`, `.aidoc/remediation/`, `.aidoc/review/` paths |
| `framework/CHANGELOG.md` | `[Unreleased] → Added` entry for the three-tier output separation + `.aidoc/` formalization |
| `examples/url-shortener/README.md` | Already in step 11; expand the §2 three-tier layout table to spell out the `.aidoc/` subdirs (audit/, remediation/, review/, validation/, security/, quality/) |
| `examples/url-shortener/ACCEPTANCE_TEST_PLAN.md` | Update §3 "Per-run log layout" + §3.2 `--promote` algorithm to reflect the new direct-to-`docs/` + `.aidoc/` routing |
| `.gitignore` | Split `.aidoc/review/` rule: keep `.aidoc/review/.blackboard/` ignored, allow committed consensus reports |
| `tests/README.md` | Reference the `.aidoc/` provenance tier in the test-suite navigation hub |
| `tests/scripts/test-acceptance.sh` header | Update the "Log layout" comment block to describe three tiers, not two |

### Authoring principle

Every doc that touches the example-directory layout MUST mention all
four tiers (inputs, outputs, provenance, logs) — not just `docs/` and
`logs/`. Tools or contributors reading any one of these docs in
isolation should understand where `.aidoc/` fits without cross-reading.

A short "see also" link at the end of each updated doc points at the
canonical definition (proposed: a new `framework/docs/AIDOC.md`
explaining the three-tier separation in detail, or a §2-equivalent
block in REPO_STRUCTURE.md).

## 5. Verification — pre-PR

```bash
# Should still SKIP cleanly without --live (no regressions in dry run)
bash tests/scripts/test-acceptance.sh url-shortener --no-live
```

Expected: 6 PASS (2 bootstrap + 3 lint-based negatives + 1 hook),
all others SKIP, 49 elements total.

Post-restructure: `logs/<TS>/elements/` (flat), no separate phase
subdirs. `docs/` empty (no cascade yet). `.aidoc/` may have leftover
content from prior runs — that's fine, it's committed.

## 6. Verification — live re-run

Expected outcomes after restructure:

| Phase | Expected |
|---|---|
| 0 — Bootstrap | 4/4 PASS |
| 1.1 — Cascade (8/8 layers) | 8/8 PASS, audit scores ≥ 90 each; artifacts in `docs/<NN>_<LAYER>/` |
| 1.2 — Negative | 6/6 detected |
| 2 — CHG | 4/4 PASS (no longer bootstrap mode if 1.1 promoted) |
| 3 — Utilities (calibrated) | 12-14/14 PASS |
| 4 — Agents (11) | 9-11/11 PASS |
| 4 — Command + Hook | 2/2 PASS |

After `--promote`:

- `examples/url-shortener/docs/` populated with 8 layer dirs
- `examples/url-shortener/.aidoc/` populated with audit, remediation,
  review, validation, security, quality reports
- Commit message: `chore(examples): promote url-shortener cascade for v0.4.0 release`

## 7. PR shape

| PR | Contents | Cost |
|---|---|---|
| **PR-1** | All architectural + bug + calibration changes in one logical PR. ~250-400 net lines across `test-acceptance.sh`, `test-acceptance.schema.json` v1.1, `examples/url-shortener/README.md`, `.gitignore` | 0 + ~$10-15 re-run |
| **PR-2** (optional parent companion) | If new CLI flags require release.yml update — likely none | 0 |
| **PR-3** (deferred, post-validation) | Promote the produced cascade + CHANGELOG entry | $0 (re-run already done) |

## 8. Open questions — resolved

| # | Question | Decision |
|---|---|---|
| Q1 | Does `claude -p --output-format=json` return token usage? | Defer to implementation step 4. Trivial probe; falls back to byte-count estimate if no `usage` object |
| Q2 | Single PR or split the restructure? | **Single PR** — coherence over reviewability. Pre-1.0 work; the design only makes sense as a whole |
| Q3 | `.aidoc/profile.yaml` — out of scope or in scope? | **In scope as A11.** The profile is "the single input an engine reads" per `framework/governance/ADAPTATION.md`. Suite must honor it. Phase 0 bootstraps from framework default if missing. Creating a *new* (non-default) profile stays out of scope |
| Q4 | Should `docs/` overwrites require `--force`? | **Yes — A12.** Refuse to overwrite `docs/`/`.aidoc/` with unstaged changes; `--force` overrides |

### Followups from these decisions

- A11 needs the framework-default profile location identified during step 9a. `framework/governance/ADAPTATION.md` mentions framework defaults but doesn't pin them to a single file path. Step 9a inspects `framework/governance/` for the canonical default (likely derived from `ADAPTATION_SURFACE.yaml` + `REVIEW_CREWS.yaml`); if no single canonical file exists, the step is to create one as a sibling change inside this PR.
- A12 reuses the same `git diff-index --quiet` check that `--promote` already does; just runs it earlier in the flow.

## 9. Done criteria

- Restructure landed: three-tier separation active.
- Cascade writes directly to `docs/`; audit/review/remediation/validation
  /security/quality skills route to `.aidoc/<category>/`; logs collapse to
  `logs/<TS>/elements/` with YAML front-matter metadata combined into a
  single file per element.
- All bugs (B1-B6) and calibrations (C1-C3) resolved.
- `--no-live` smoke regression: 6 PASS, 0 FAIL across 49 elements.
- `--live` re-run produces clean 8-layer cascade with ≥ 90% PASS across
  all 63 elements; `docs/` and `.aidoc/` populated; commit lands.

## 10. Gap-resolution log

| Gap from user feedback | Where addressed |
|---|---|
| Documents in `logs/` instead of `docs/` | A1 — write cascade directly to `docs/` |
| `.aidoc/` is part of documents (not execution logs) | §2 three-tier + A2 routing |
| Logging system needs optimization | A3 (flat `elements/`) + A4 (single file per element with YAML front-matter) + B6 (token tracking) |
| Framework docs need to introduce `.aidoc/` as "AI's working notes — documentation of provenance" | §4a documentation pass |
| `--force` safety belt for `docs/` overwrites | A12 + step 9b |
| `.aidoc/profile.yaml` honored by the suite (use existing or copy framework default) | A11 + step 9a |
| Plan gaps catalogued earlier (G1-G12) | All folded into A1-A10 / B1-B6 / C1-C3 |
