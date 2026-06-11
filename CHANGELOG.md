# Changelog

All notable changes to the AI Doc Flow Framework (multi-platform project) are
documented here. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Scope: this is the **project-level** changelog tracking the multi-platform
> migration. Once scaffolded, each platform keeps its own changelog at
> `platforms/<name>/CHANGELOG.md`, and `framework/` versions independently.
>
> This file logs both project releases (`v1.x.y`) and framework-spec releases (`Framework Spec 0.x.y`). Per-stream details for the Claude Code plugin live in [`platforms/claude-code-plugin/CHANGELOG.md`](platforms/claude-code-plugin/CHANGELOG.md).

## [Unreleased]

### Changed — Framework Spec 0.19.0 → 0.19.1 + Claude Code plugin 0.16.0 → 0.16.1 (CLEANUP-PR-E)

Fourth child PR of FRAMEWORK-CLEANUP-001 (master plan PR #128). Closes
`plans/FRAMEWORK-TODO.md` Open item #17 — IPLAN sub-types.

- **Template** — `IPLAN-TEMPLATE.yaml` gains a `subtype` field
  (`code_build | deploy | combined`, default `combined`) in
  `document_control`. Existing 4 sections (file_manifest,
  execution_commands, implementation_contracts, session_handoff) gain
  `_required_when_subtype: [code_build, combined]` markers. 5 new
  deploy-only sections (rollback_procedure, smoke_tests,
  canary_metrics, observability_hooks, runbook_reference) marked
  `_required_when_subtype: [deploy, combined]`.
- **doc-iplan author SKILL** — new "Select subtype" step (4) in the
  Creation Process; default `combined` if unsure.
- **doc-iplan-audit SKILL** — Structural Checklist gains
  subtype-aware dispatch; reads `document_control.subtype` and
  selects the required-section set; missing field defaults to
  `combined` (backward compat).
- **IPLAN playbooks** — `operator.md`, `chaos_engineer.md`,
  `integration_lead.md` gain a `### Subtype awareness` subsection
  in the Reasoning frame. At `code_build` subtype, these lenses MAY
  return `lens_score: 100` with the rationale
  `"subtype: code_build — deploy concerns out of scope"` (composes
  with CLEANUP-PR-B item 8's no-findings-rationale rule).
- **Backward compat** — IPLANs pre-dating this PR have no `subtype`
  field; auditor defaults to `combined`. url-shortener's IPLAN-01
  untouched (never-hand-edit example artifacts); a future cascade
  re-run picks up the new field via the author SKILL change.
- Framework PATCH (`0.19.0 → 0.19.1`) — template field addition is
  additive + backward-compat. Plugin PATCH (`0.16.0 → 0.16.1`).

### Changed — Framework Spec 0.18.0 → 0.19.0 + Claude Code plugin 0.15.0 → 0.16.0 (CLEANUP-PR-B)

Third child PR of FRAMEWORK-CLEANUP-001 (master plan PR #128). Closes
`plans/FRAMEWORK-TODO.md` Open items #5-10. The **heart** of the
cleanup workstream — review-quality calibration.

- **Item 5** — `CLAUDE.md` §Development workflow item 2 gains a
  "Corpus cross-check" paragraph requiring `sdd_doc_lint
  examples/<NAME>/docs/` smoke when a plan changes lint rules,
  `@`-tag semantics, registry shape, or playbook content. Catches the
  NECESSARY-UPSTREAM-001 Pass 4 gap that shipped 107 orphan `@prd:`
  tags into the cascade.
- **Item 6** — `CLAUDE.md` "Empirical pass-count baseline" paragraph
  (advisory): framework-level / cross-cutting plans typically need
  4-5 review cycles; per-layer rollouts converge in 2-3. Floor stays
  ≥ 2 cycles per CLAUDE.md.
- **Item 7** — `framework/playbooks/07_TDD/auditor.md` C4 + Reasoning
  frame + C1 updated from pre-NECESSARY-UPSTREAM-001 cumulative-trace
  references (`@brd:`/`@prd:` in required-tag set) to the actual
  necessary-upstream set (EARS/BDD/ADR/SPEC). PRD/BRD remain as
  optional decorative tags. Closes a real spec-drift bug, not a
  wontfix.
- **Item 8 — HIGH** — 13 playbook files (6 × `auditor.md` + 7 ×
  `tech_lead.md`) gain a new `## No-findings rationale` section
  between `## Beyond-checklist` and `## Scoring`. A lens returning
  `lens_score: 100 / findings: []` MUST emit a `no_findings_rationale`
  field naming a section it examined and cleared. Synthesizer caps
  the lens at 95 when rationale is missing (`STRUCTURE-RAT-001`
  advisory). Calibration nudge against "convergence theater" surfaced
  by the 2026-06-11 url-shortener review (auditor + tech_lead scored
  100 across 4-6 layers with zero findings while chaos/security found
  P2/P3 in the same sections).
- **Item 9** — 9 audit SKILLs (8 layer + CHG) gain
  `### Strip author self-claim before lens dispatch` subsection
  instructing the engine to strip `*_ready_score` / `*_score` /
  `readiness_score` / `audit_score` fields from the artifact body
  before passing to each lens (anchor-effect fix). Stripped-field
  list documented in `REVIEW_TEAM.md` §Operations.
- **Item 10** — 9 audit SKILLs gain `### Regressions` subsection in
  Combined Report Format. Synthesizer agent gains fixer-introduced
  detection logic: compares iter-N finding locations to iter-(N-1)
  Fixes Applied entries; sets `fixer_introduced: true` on matches;
  caps affected lens score at iter-(N-1) value (no improvement credit
  for a fix that regressed). New `## Regressions` audit-report section
  format documented in `REVIEW_TEAM.md` §Operations.
- Framework MINOR (`0.18.0 → 0.19.0`) — 3 new `REVIEW_TEAM.md`
  §Operations subsections + 13 playbook content additions.
- Plugin MINOR (`0.15.0 → 0.16.0`) — 9 audit SKILL extensions +
  synthesizer agent new logic.
- All sync hooks ran cleanly; vendored mirrors propagated.

### Changed — Framework Spec 0.17.1 → 0.18.0 + Claude Code plugin 0.14.1 → 0.15.0 (CLEANUP-PR-C)

Second child PR of FRAMEWORK-CLEANUP-001 (master plan PR #128, merged
`528d6f23`). Closes `plans/FRAMEWORK-TODO.md` Open items #11-14.
Spec / registry / template hygiene.

- **Item 11 — Iteration cap to spec.** `REVIEW_REMEDIATION_FLOW.md` §The
  quality loop gains a new "Iteration cap" subsection elevating the
  previously-impl-bound `MAX_ITERATIONS=3` to spec. New
  `ADAPTATION_SURFACE.yaml` knob `quality_loop_max_iterations` (range
  1-10, default 3) makes the cap project-tunable. `tools/saga_driver.py`
  gains `_resolve_max_iterations(profile_path)` that loads
  `.aidoc/profile.yaml`, reads the knob, and falls back to the default
  for missing-file / malformed / out-of-range. New `import yaml`. The
  call site at the iteration-check uses the resolved value.
- **Item 12 — `@threshold:` ID pattern in registry.**
  `LAYER_REGISTRY.yaml` `id_patterns` gains a `threshold` entry
  (`TYPE.NN.<lowercase_category>.<lowercase_key>`) that distinguishes
  threshold keys from 4-segment hex-hash element IDs. `tools/sdd_doc_lint`
  TH01 check upgraded to use the strict regex; rejects mixed-case
  categories. Verified url-shortener thresholds all match (no regression).
- **Item 13 — SPEC + IPLAN element ID exemption.** New "Element-ID
  exemptions" subsection in `ID_NAMING_STANDARDS.md` formalizing that
  SPEC §5 rules + IPLAN §4 contracts MAY but are not required to carry
  layer-local `SPEC.NN.SS.xxxx` / `IPLAN.NN.SS.xxxx` element IDs.
  Traceability surface for SPEC/IPLAN is the upstream `@<layer>:`
  citation chain plus Protocol method names / file manifest entries.
- **Item 14 — EARS `@bdd:` downstream slot formalized as optional.**
  New "Optional downstream slots" subsection in `REVIEW_TEAM.md` +
  new `optional_downstream_slots:` per-layer field in
  `LAYER_REGISTRY.yaml`. Only EARS opts in (slots toward BDD); other
  layers don't emit. Slots are non-canonical for trace (the canonical
  is the upstream `required_tags` chain) and `TRACE-RES-001`'s
  downstream-skip behavior (PR #125) means unresolved slots at
  author-time don't fail lint.
- Framework MINOR (`0.17.1 → 0.18.0`) — new spec subsection +
  registry shape changes. Plugin MINOR (`0.14.1 → 0.15.0`) — saga
  driver reads new knob; lint rule upgraded.
- Sync hooks ran (sync-version-refs, sync-plugin-framework,
  sync-vendored). Conformance 120/120 PASS; unit 43/43 PASS.

### Changed — Claude Code plugin 0.14.0 → 0.14.1 (CLEANUP-PR-A — harness + lint workflow hygiene)

First child PR of the FRAMEWORK-CLEANUP-001 workstream (master plan PR #128).
Closes `plans/FRAMEWORK-TODO.md` Open items #1-4. Plumbing fixes; no spec change.

- **`--skip-lint-smoke` flag** (item 1): added to `tests/scripts/test-acceptance.sh`
  Phase 0. When set, lint-smoke logs SKIPPED outcome and the auto-remediate
  fixer cycle is bypassed (the flag wraps BOTH the check AND the remediation —
  half-bypass would be incoherent). Documented forward-looking replacement for
  the ad-hoc `SDD_LINT_SKIP_TRACE_RES=1` env-var pattern used during the
  TRACE-RES-FIXUP-001 regen (PR #125).
- **Cleanup-then-cascade pattern docs** (item 2): new subsection in
  `tests/ACCEPTANCE.md` documenting the `rm -rf <layer-dir>` → `--force` cascade
  sequence with a worked example mirroring the IPLAN-RT-001 PR #127 cascade.
  Plus guidance on when to combine with `--skip-lint-smoke`. Pass 1 verified the
  harness error message at `test-acceptance.sh:823` already correctly suggests
  `--force`; the gap was purely docs (plan authors didn't know about the
  pattern).
- **DO-NOT-EDIT banners on vendored modules** (item 3): canonical Python
  modules (`tools/sdd_doc_lint/__init__.py`, `tools/saga_driver.py`) gain a
  top-of-docstring "CANONICAL SOURCE — vendored copies under platforms/<name>/
  are byte-identical mirrors, DO NOT EDIT" banner. Banner propagates to the
  vendored copies via the sync scripts. New `platforms/claude-code-plugin/framework/_VENDORED.md`
  README explains the byte-identity contract for the vendored framework bundle
  (markdown-friendly alternative to a per-file banner that would trip lint).
- **MD056 SKILL prompt fix** (item 4): 18 audit + fixer SKILL prompts
  (`doc-{adr,bdd,brd,chg,ears,iplan,prd,spec,tdd}-{audit,fixer}/SKILL.md`)
  each gain a `### Table-pipe escape (MD056)` subsection in their Report Format
  section, instructing the LLM author to escape `|` inside code spans within
  markdown table cells (use `\|` or move the code span out of the cell). Per
  IPLAN-RT-001 cascade evidence: cascade output tripped MD056 because shell
  pipes inside backtick code spans were parsed as column separators. The
  `examples/<*>/.aidoc/` markdownlint exclude added in PR #127 is a workaround;
  this PR fixes the root cause in the SKILL prompts. Final exclude removal
  deferred to PR-A verification cascade.
- Plugin PATCH (`0.14.0 → 0.14.1`). No framework spec change.

### Changed — Framework Spec 0.17.0 → 0.17.1 + Claude Code plugin 0.13.1 → 0.14.0 (IPLAN-RT-001)

- **IPLAN layer team-mode + playbook injection — closes the 8/8 layer rollout.**
  Mirror of the TDD-RT-001 pattern for the IPLAN layer (Layer 8). With
  this PR, all 8 layers (BRD/PRD/EARS/BDD/ADR/SPEC/TDD/IPLAN) wire the
  multi-persona review fan-out + playbook injection. LAYER-PLAYBOOKS-001
  workstream complete: **45 of 45 playbooks** across all 8 layers.
- **6 IPLAN playbooks** at `framework/playbooks/08_IPLAN/`:
  `tech_lead` 30 / `architect` 25 / `operator` 15 / `integration_lead` 12 /
  `auditor` 10 / `chaos_engineer` 8 (sum 100). **No `security_engineer`** —
  threat-model lives upstream in ADR/SPEC; IPLAN is procedural deploy/
  rollback only. **New `integration_lead` lens** (cross-system contract
  compatibility, dependency rollout order, feature-flag gating, backward-
  compatible API window) — appears only at IPLAN.
- **`doc-iplan-audit/SKILL.md`** (270 → 551 lines) gains `## Review Mode`,
  `## Saga interaction`, `## Break-circuit policy`, and playbook injection
  (step 3a + augmented step 4). Lens→agent map: tech_lead + architect +
  integration_lead → solutions-architect (3 lens-roles via 3 separate
  Task subagent invocations); operator → devops-release-engineer;
  auditor → traceability-auditor; chaos_engineer → chaos-engineer.
- **`doc-iplan-fixer/SKILL.md`** (112 → 310 lines) gains
  `## Remediate Mode`, `## Saga interaction`, `## Break-circuit policy`.
- **`@unittest.skip` removed** from
  `tests/conformance/test_playbook_coverage.py:35` (task #258 closing
  cleanup). The conformance suite gains its 121st active test:
  `test_every_crew_lens_has_a_playbook_file` (now enforces all 45
  playbooks).
- **`docs/PARITY.md`** Layer Playbooks row title corrected from stale
  `(BRD/PRD/EARS)` to `(all 8 layers)` — row went stale across 5 prior
  per-layer PRs (EARS/BDD/ADR/SPEC/TDD-RT-001).
- Framework spec PATCH (`0.17.0 → 0.17.1`) — IPLAN playbooks added under
  the existing §Playbooks artifact class.
- Plugin MINOR (`0.13.1 → 0.14.0`) — new layer wiring (8/8).
- All 45 playbook frontmatter files re-synced to `framework_spec_version: "0.17.1"`
  via the `scripts/sync-version-refs.sh` hook (LAYER-PLAYBOOKS-001 Phase F
  Task 11 extension).

### Changed — Claude Code plugin 0.13.0 → 0.13.1 (TRACE-RES-FIXUP-001)

- **Lint rule semantic fix (Fix 1).** `_check_trace_resolution` in
  `tools/sdd_doc_lint/__init__.py` now skips downstream tags (tags whose
  layer-number is greater than the artifact's own layer-number).
  Downstream pointers are informational forward references (e.g. SPEC-01
  emitting `@tdd: TDD-01` before TDD-01 exists); they are not part of
  the necessary-upstream lineage being enforced. Self-tags resolve
  naturally via `doc_index`; sibling references (same layer, different
  doc_id) still resolve. Synced to both vendored copies
  (`platforms/claude-code-plugin/sdd_doc_lint/` + `platforms/hermes/sdd_doc_lint/`).
- **url-shortener example corpus regenerated (Fix 2).** Six layers
  re-authored under the post-NECESSARY-UPSTREAM-001 contract via cascade
  `--from-layer=prd --to-layer=tdd --force` (5h 1m wall clock,
  18,072s). Final scores all PASS: PRD-01 92, EARS-01 94, BDD-01 91
  (iter-3), ADR-01 96, SPEC-01 97 (iter-3 lifted from 89), TDD-01 90
  (iter-1). The regenerated corpus passes
  `python3 -m sdd_doc_lint examples/url-shortener/docs/` with zero
  `TRACE-RES-001` findings (4 pre-existing STY02 size warnings remain
  but are non-blocking).
- **Temporary `SDD_LINT_SKIP_TRACE_RES=1` bypass removed (Fix 3).** The
  env-var early-return added during TDD-RT-001 to unblock live cascade
  verification is gone. The new lint-rule semantics (Fix 1) + the
  regenerated corpus (Fix 2) together eliminate the need for the
  bypass.
- New `plans/FRAMEWORK-TODO.md` (seeded as Tier 2 of the
  example-driven feedback pipeline introduced by FRAMEWORK-FEEDBACK-LOG-001
  / PR #124): captures 8 framework-improvement items discovered during
  the NECESSARY-UPSTREAM-001 → TDD-RT-001 → TRACE-RES-FIXUP-001 sequence.
- Plugin PATCH (`0.13.0 → 0.13.1`) — lint-rule semantic fix.
- No `framework/**` change — the example corpus regeneration is data,
  not spec; no GATE-SPEC trigger.

### Changed — Framework Spec 0.16.1 → 0.17.0 (FRAMEWORK-FEEDBACK-LOG-001)

- **New governance Principle 9** in `DOC_GOVERNANCE_CORE.md`:
  example-driven / project-driven framework improvement. Friction
  discovered while applying the framework is captured immediately via
  a two-tier feedback pipeline; learning no longer evaporates between
  sessions.
- **New dedicated governance doc** `framework/governance/FRAMEWORK_FEEDBACK_LOG.md`
  codifies the two-tier pipeline:
  - **Tier 1 — Consumer project:** every project applying the framework
    keeps `framework-feedback-log.md` at its root. Records lint-rule
    misfires, harness flag absences, SKILL prose contradicting the
    spec, sync-script gotchas, missing convenience features. Inline as
    discovered. Periodically surfaced upstream via PR/issue.
  - **Tier 2 — Framework repo:** the framework's own
    `plans/FRAMEWORK-TODO.md` aggregates entries from the framework
    team's example-driven testing AND from consumer-project logs.
    Triage queue: entries → plans → PRs.
- **New consumer-project template** `framework/templates/framework-feedback-log.template.md`
  scaffolds the Tier-1 log (Open / Surfaced / Closed sections; entry
  format guidance; tag taxonomy).
- Framework spec MINOR (`0.16.1 → 0.17.0`) — adds a new governance
  principle + new governance doc + new template directory; consumer
  projects gain a documented capture path that didn't exist before.

### Changed — Framework Spec 0.16.0 → 0.16.1 + Claude Code plugin 0.12.0 → 0.13.0 (TDD-RT-001)

- **TDD layer team-mode + playbook injection.** Mirror of the SPEC-RT-001
  pattern applied to TDD (Layer 7).
- **Framework**: 6 TDD playbooks added to `framework/playbooks/07_TDD/`
  (`qa_lead` 35 / `tech_lead` 25 / `chaos_engineer` 10 / `security_engineer` 10 /
  `operator` 10 / `auditor` 10 = 100). Six-lens crew (largest TDD-altitude
  crew shape). Authored under the new necessary-upstream contract from
  NECESSARY-UPSTREAM-001.
- **Plugin**: `doc-tdd-audit/SKILL.md` (268 → 499 lines) gains `## Review Mode`
  - `## Saga interaction` + `## Break-circuit policy` + playbook injection.
  `doc-tdd-fixer/SKILL.md` (112 → 298 lines) gains `## Remediate Mode` +
  `## Saga interaction` + `## Break-circuit policy`. Both SKILLs carry zero
  cumulative-tag references (verified during NECESSARY-UPSTREAM-001 Pass 2,
  confirmed on rebase).
- **Live cascade verification**: `content_score 89` (threshold 90 — 1 point
  short of CLOSED), 0 P0/P1, 6 P2 + 2 P3 content-refinement findings.
  Saga ended `PARTIAL_TIMEOUT` in iter-2 (4273s of 5400s budget). Massive
  improvement vs the pre-NECESSARY-UPSTREAM-001 cascade (76 score, 2× P1
  trace fabrications) — the new contract eliminates trace fabrication.
- **Migration bypass** `SDD_LINT_SKIP_TRACE_RES=1` added temporarily so the
  TDD cascade can proceed past Phase 0 lint-smoke against the
  pre-NECESSARY-UPSTREAM-001 url-shortener corpus (orphan `@prd:` tags from
  the old cumulative-trace contract). Default behavior unchanged.
- **Follow-up filed** in [`plans/TRACE-RES-FIXUP-001-PLAN.md`](plans/TRACE-RES-FIXUP-001-PLAN.md):
  (1) TRACE-RES-001 downstream-tag skip (lint rule bug — fires on forward
  pointers like `@tdd: TDD-01`), (2) url-shortener corpus regeneration,
  (3) `doc-tdd/SKILL.md` still emits 1 decorative `@brd:` tag, (4) removal
  of the temporary bypass.

### Changed — Framework Spec 0.15.2 → 0.16.0 + Claude Code plugin 0.11.0 → 0.12.0 (NECESSARY-UPSTREAM-001)

- **Replaced cumulative-trace contract with necessary-upstream + transitive
  reachability.** Each layer declares only what its own evaluation reads;
  lineage to layers further upstream is discoverable transitively through
  the @-tag chain (one hop per layer) and via the new `tools/trace_walk.py`.
  Per-layer `required_tags` shrunk: EARS `[brd, prd]` → `[prd]`, BDD
  `[brd, prd, ears]` → `[ears]`, ADR `[brd, prd, ears, bdd]` → `[ears, bdd]`,
  SPEC `[brd, prd, ears, bdd, adr]` → `[ears, bdd, adr]`, TDD
  `[brd, prd, ears, bdd, adr, spec]` → `[ears, bdd, adr, spec]`, IPLAN
  `[brd, prd, ears, bdd, adr, spec, tdd]` → `[spec, tdd]`. BRD `[]` and
  PRD `[brd]` unchanged.
- **Framework**: `LAYER_REGISTRY.yaml` updated; 7 layer templates' §7
  Traceability `upstream:` blocks aligned with the new minimal set; ADR
  auditor C1 wording rewritten to validate the new required set + reference
  the `TRACE-RES-001` lint floor; `REVIEW_TEAM.md` gains §"Necessary
  upstream + transitive trace"; `ADAPTATION_SURFACE.yaml` `cascade_rule`
  restates the new default baseline explicitly.
- **Plugin**: 15 SKILLs aligned with the new contract (7 layer-author SKILLs
  drop "cumulative upstream tags" instructions; 8 audit/fixer SKILLs reword
  cumulative-tag references). Acceptance harness `tests/scripts/test-acceptance.sh`
  validator probe drops "cumulative" prompt and lowers expected-count
  threshold 20 → 10. `doc-tdd-audit`/`doc-tdd-fixer` deferred to TDD-RT-001
  rebase.
- **New tooling**:
  - `sdd_doc_lint TRACE-RES-001` corpus-level rule — every emitted
    `@<layer>: <ID>` tag must resolve (host doc exists + element id declared
    in host); element-index uses host-doc derivation so citations cannot
    resolve themselves; index docs excluded. Runs at every layer regardless
    of crew shape, providing deterministic structural-floor enforcement.
  - `tools/trace_walk.py` (158 LOC, stdlib-only) — BFS DAG-closure walker;
    `--to <LAYER>` filter; returns non-zero on any unresolvable tag.
- **Conformance**: `test_required_tags_are_cumulative` renamed → `test_required_tags_match_necessary_upstream_table`;
  new conformance file `test_layer_registry_necessary_upstream.py` (2 tests);
  new unit tests `test_sdd_doc_lint_trace_resolution.py` (4 cases) +
  `test_trace_walk.py` (4 cases). Total: 120/120 conformance + 40/40 unit.
- **Backwards compatibility**: existing url-shortener artifacts remain valid
  (declared tags still resolve). The contract change is a relaxation —
  declaring extra upstream tags isn't forbidden by `TRACE-RES-001`, only
  declaring upstream that doesn't resolve is.
- **Origin**: TDD-RT-001 live cascade (2026-06-09) produced TDD-01 with
  `@prd: PRD.01.13.7760` referencing a non-existent `docs/02_PRD/PRD-01.md`.
  Saga ended at PARTIAL_TIMEOUT in iter-3; fixer reached fixed point at
  iter-2 because the only blocking findings required either authoring
  PRD-01.md or removing trace claims the doc itself asserted as required.

### Changed — Framework Spec 0.15.1 → 0.15.2 (docs)

- **`framework/README.md` Layout section corrected.** The `framework/`
  directory listing had drifted: it omitted the `playbooks/` artifact class
  (vendored; the review-team audit checklists), the `docs/` directory (whose
  `AIDOC.md` this README already links), and the root guide docs
  (`SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`, `QUICK_REFERENCE.md`,
  `TESTING_STRATEGY_TDD.md`, `AI_ASSISTANT_RULES.md`). Layout now lists all
  top-level entries; the intro line names the playbooks artifact class. PATCH
  (doc clarification; any `framework/**` change trips GATE-SPEC-E005, forcing
  the `framework/VERSION` bump + both `FRAMEWORK_SPEC_VERSION` pointers).
  Plugin + Hermes product versions unchanged.

- **Root `README.md` Status section refreshed** (project doc, no spec impact).
  Corrected stale versions (framework spec `0.13.0` → `0.15.2`, plugin
  `v0.6.2` → `v0.11.0`); replaced the drift-prone hand-maintained feature
  catalog with a concise snapshot pointing to `ROADMAP.md` / `CHANGELOG.md`.
  The framework-spec reference now uses an inline phrase the version-sync hook
  already maintains (it had drifted because the prior table cell was unreachable
  by the hook), and the redundant plugin/Hermes version copies were dropped
  (those live, auto-synced, in the Platforms table).

- **`scripts/sync-version-refs.sh` closes two framework-spec propagation gaps**
  (tooling; no spec/product version change of its own). On a `framework/VERSION`
  bump the hook now also rewrites the plugin `README.md` (both the prose
  framework-spec lines and the `$ cat FRAMEWORK_SPEC_VERSION` example block) and
  the conformance test's hardcoded spec-version literal
  (`test_plugin_release_metadata.py`). Both previously required a hand-edit every
  bump — caught only after the fact by a conformance failure (e.g. PLANSTD-001
  and the 0.15.2 doc PATCH both hit this). Verified end-to-end by a simulated
  bump.

### Added — Framework Spec 0.15.0 → 0.15.1 + Plugin 0.10.2 → 0.11.0 (SPEC-RT-001)

- **Framework Spec 0.15.0 → 0.15.1 — 5 SPEC-layer playbooks.**
  `framework/playbooks/06_SPEC/{architect,tech_lead,integration_lead,chaos_engineer,security_engineer}.md`
  added per the §Playbooks contract from 0.14.0. Hybrid content shape
  (reasoning frame + Cn deterministic checks + beyond-checklist
  escape hatch + 0-100 scoring rubric). Crew weights 30/30/20/10/10
  = 100 per `REVIEW_CREWS.yaml`.

  **Smallest crew of any layer** (5 lenses) — no operator (deployment
  is IPLAN's altitude) and no auditor (no per-element tag-trace audit
  at SPEC). **Equal chaos/security split** (10/10) — SPEC specifies
  both performance/resilience and security controls at equal weight.
  **`integration_lead` first appears at SPEC** — binds to
  `solutions-architect` (third lens sharing this agent alongside
  architect + tech_lead; brief specifies the lens at Task dispatch
  time). PATCH bump (new content within existing artifact class).

- **Claude Code plugin 0.10.2 → 0.11.0 — SPEC layer team-mode + playbook injection.**
  `doc-spec-audit/SKILL.md` (267 → 502 lines) gains `## Review Mode`
  (team mode default at gates) + `## Saga interaction` +
  `## Break-circuit policy` + playbook injection (step 3a loads
  `framework/playbooks/06_SPEC/<lens>.md`; step 4 inlines into
  per-lens Task brief).
  `doc-spec-fixer/SKILL.md` (115 → 305 lines) gains
  `## Remediate Mode` (team-mode patch-validation for P0/P1;
  deterministic for P2/P3) + `## Saga interaction` +
  `## Break-circuit policy`. Mirrors EARS-RT-001 / BDD-RT-001 /
  ADR-RT-001 wiring pattern.

  **Live SPEC acceptance: PASS at score 97/100** (cascade-4
  `verdict.json` `combined_status: PASS`, saga `CLOSED` cleanly).
  Score trajectory across 2 audit cycles: **79 → 97 in one fixer
  cycle** (+18 points). Per-lens scores at iter 2: architect 100
  (perfect) / tech_lead 95 / integration_lead 96 / chaos_engineer 93 /
  security_engineer 100 (perfect). 5/5 lens coverage quorum on every
  audit. Wall-clock 3042s (50:42) — well within SAGA-BUDGET-001
  5400s ceiling.

  **Three infrastructure PRs surfaced and resolved during the
  SPEC-RT-001 rollout** (all merged before this PR landed):
  - PR #110 (STY03 fence-fix) — `sdd_doc_lint` STY03 now excludes
    code-fenced blocks
  - PR #111 (SAGA-BUDGET-001) — saga budget 60 → 90 min
  - PR #115 (synthesizer schema + saga events) — `findings[*].check`
    required + `saga.events[]` orchestration journal
  - PR #117 (SAGA-DETERMINISM-001) — `reconcile_post_audit` walks
    saga.status deterministically when SKILL skips per-branch
    transition stamping

  All four together resulted in the cleanest cascade evidence yet:
  100% finding-check preservation (4/4 in final verdict + 19/19 in
  iter 1), 10 reconciled transitions auto-backfilled, 8 saga.events
  with full lifecycle, fix report v001 + `chaos_engineer.fix_1.json`
  team-mode patch-validation slot (the P1 from iter 1 was a
  chaos_engineer finding).

  Implementation artifacts: `plans/SPEC-RT-001-PLAN.md` (2-cycle gap
  review: 11 Pass-1 clarifications folded + Pass-2 verdict clean).
  Test evidence: `examples/url-shortener/docs/06_SPEC/SPEC-01.md`
  (lint-clean), `examples/url-shortener/.aidoc/review/06_SPEC/SPEC-01/`
  (5 per-lens slots + 1 fix-validation slot + verdict.json +
  report.md + saga.json with 17 transitions including 10 reconciled
  - F_fix_report_v001),
  `examples/url-shortener/.aidoc/audit/06_SPEC-audit.md`.

### Fixed — SAGA-DETERMINISM-001 (Plugin 0.10.1 → 0.10.2)

Saga driver now deterministically reconciles `saga.transitions[]` and
walks `saga.status` after every audit subprocess returns, instead of
trusting the audit SKILL's LLM to do the bookkeeping consistently.

**Origin:** SPEC-RT-001 worktree cascade (2026-06-09) reached
`verdict.json` `combined_status: PASS` at score 95 with 12 clean
`saga.events[]` entries (PR #115 instrumentation) — but the harness
B2 check reported `FAIL` because `saga.status` was stuck at
`FANOUT_STARTED`. Investigation: the audit SKILL's prompt asks the
LLM to do two writes per branch event — update `branches[<lens>]`
dict + append a transition entry to `transitions[]`. The LLM
stochastically does the first while skipping the second. On ADR's
run the LLM stamped all 35 transitions; on SPEC's run (byte-identical
prompt) it stamped 0 of the 15 expected per-branch transitions across
3 audit cycles. After audit completed, the driver hit
`FANOUT_STARTED → FANIN_REDUCED` which isn't in
`_ALLOWED_TRANSITIONS`, raised, and `saga.status` stayed at
`FANOUT_STARTED`.

**Fix (`tools/saga_driver.py` + vendored copy):** new
`reconcile_post_audit(ctx, saga)` helper called at the start of
`_advance_after_phase`'s review/re-review branch. It:

1. Iterates `saga.branches[<lens>]`; for each branch whose `status`
   is terminal (`BRANCH_COMPLETED` / `BRANCH_FAILED`) but whose
   matching `branch:<lens>` `BRANCH_RUNNING` / `<terminal>`
   transition is absent from `transitions[]`, appends the missing
   entries (marked `reconciled: true`) using the branch's
   `started_at` / `ended_at` timestamps.
2. If `saga.status == FANOUT_STARTED` and every branch is terminal,
   walks `saga.status` `FANOUT_STARTED → BRANCH_RUNNING →
   BRANCH_COMPLETED` at run scope through the allowed-transition
   graph. The existing PASS code path
   (`BRANCH_COMPLETED → FANIN_REDUCED → SYNTHESIZED → CLOSED`) then
   fires correctly.

**Idempotent:** when the audit SKILL stamps transitions completely
(the ADR case), `reconcile_post_audit` is a no-op. Partial-stamp
cases (SKILL stamps some lenses, skips others) are handled — only
missing transitions are backfilled.

**Architecturally:** completes the cooperative→preemptive migration
started by SAGA-PARITY-001 Phase 2 Amendment 1. Saga-state-machine
bookkeeping is now deterministic at the driver, not LLM-delegated.
The audit SKILL's saga-interaction prompt is preserved as a
fast-path but no longer load-bearing for correctness.

**Tests:** 6 new unit tests at
`tests/unit/test_saga_reconcile_post_audit.py`. Includes a
regression test on the verbatim captured SPEC-RT-001 saga.json
fixture (`tests/unit/fixtures/saga-reconcile/saga-skill-skipped-transitions.json`).

No SKILL changes. No framework/VERSION bump. Plugin VERSION 0.10.1
→ 0.10.2 (PATCH). Byte-parity holds across canonical and vendored
`saga_driver.py` via `tools/sync-plugin-framework.sh`.

### Added — Framework Spec 0.14.3 → 0.15.0 (PLANSTD-001)

- **Unified development/work plan standard.** New normative spec doc
  `framework/layers/08_IPLAN/PLAN_STANDARD.md` defines a single,
  flexible plan structure that scales from a one-commit bugfix to a
  multi-phase feature. An execution agent reads an **applicability
  matrix** for its work type (`feature` / `bugfix` / `documentation` /
  `refactor` / `chore`) and keeps only the applicable chapters, via
  inline `[REQUIRED]` / `[CODE]` / `[IF APPLICABLE]` section tags and a
  "delete non-applicable chapters" rule. The standard is engine- and
  repo-agnostic; the copy-paste working instance is
  `plans/PLAN-TEMPLATE.md`, rewritten to conform.

  The doc is a **third, orthogonal** concept distinct from BOTH formal
  IPLAN artifacts: the Permanent per-SPEC `IPLAN-NN_{slug}.yaml` and the
  Temporary `tmp/TMP-IPLAN-*.yaml`. `framework/layers/08_IPLAN/README.md`
  gains a cross-link + scope note stating the distinction; neither YAML
  artifact changes.

  **MINOR bump (0.14.3 → 0.15.0):** a new spec doc under `framework/`
  forces a `framework/VERSION` bump via GATE-SPEC-E005. Both
  `FRAMEWORK_SPEC_VERSION` pointers re-matched; plugin and Hermes
  **product** versions unchanged (independent streams per
  `docs/PROJECT.md` §2). Plugin framework bundle re-vendored
  byte-identically (D-0022).

### Changed — Plugin 0.10.0 → 0.10.1 (synthesizer schema + saga observability)

Two infrastructure tightenings surfaced by the SPEC-RT-001 live cascade
(2026-06-09). Both are layer-agnostic; both ship as a single plugin
PATCH bump.

- **Synthesizer agent contract: `findings[*].check` is now required.**
  `platforms/claude-code-plugin/agents/synthesizer.md` `findings[]`
  Field semantics tightened: every finding in `verdict.json` MUST
  carry the `check` field (canonical `C\d+` from the per-(layer, lens)
  playbook OR `beyond-checklist:<principle-tag>` form), preserved
  byte-identically from the lens slot's finding.

  **Origin:** SPEC verdict.json findings array dropped the `check`
  field on every finding while lens slot JSONs correctly carried it.
  ADR + BDD verdicts happened to preserve `check` — that was
  LLM-stochastic luck, not contract compliance. The previous schema
  listed `id, priority, location, message, recommendation, personas`
  but not `check`, so both preserving and dropping the field were
  "valid" per the loose contract. Downstream consumers (fixers,
  traceability matrices, observability dashboards) read
  `findings[*].check` to roll up by playbook check; on SPEC they got
  nothing.

  **Test:** new conformance test
  `tests/conformance/platforms/test_synthesizer_verdict_schema.py`
  (3 tests) enforces the contract:
  1. `agents/synthesizer.md` must list `check` in the findings[]
     example JSON
  2. Every committed `verdict.json` under
     `examples/<name>/.aidoc/review/**/` finding must carry a
     syntactically valid `check` value
  3. The example JSON in the contract itself uses a canonical check
     id

  Synthetic verdicts (hand-rolled by the harness's AUTO-REMEDIATE-001
  path; marked `synthetic: true`) are exempt — they bypass the
  synthesizer agent entirely.

- **Saga driver observability: `saga.events[]` populated on every
  subprocess dispatch.** `tools/saga_driver.py` gains an
  `append_event(saga, kind, **extra)` helper and a new `events: []`
  field on saga.json. `dispatch_phase` now stamps `dispatch:<phase>`
  before each `claude -p` subprocess invocation and `complete:<phase>`
  after the subprocess returns, with `iteration`, `slash`, and
  `exit_code` recorded.

  **Origin:** SPEC saga claimed `iteration: 3` but the `transitions[]`
  array recorded only ONE audit cycle's per-branch transitions. The
  iter counter advanced silently inside fixer cycles because the
  state machine doesn't have a "fixer-dispatched" state and the
  driver wasn't appending non-state-changing events to the journal.
  A journal reader couldn't answer "how many fixer cycles ran and
  what was the outcome of each" without guessing from elapsed-time
  math.

  Strictly additive to the saga schema (existing consumers ignore
  unknown fields); byte-parity holds across canonical and vendored
  saga_driver.py via `tools/sync-plugin-framework.sh`.

No SKILL changes, no framework/VERSION bump, no agent file behavior
change beyond the contract tightening. `tests/unit` (26) + `tests/conformance` (118
including the 3 new tests; was 115) all PASS.

### Changed — SAGA-BUDGET-001 (saga driver wall-clock budget 60 → 90 min)

- **Cascade-harness saga wall-clock budget bumped from 60 min to 90 min**
  to accommodate larger / more iteration-prone layers. Three coordinated
  constants updated in lockstep so the existing graceful-exit invariant
  (300s margin between `SOFT_DEADLINE_SECONDS` and the wrapping
  `ORCHESTRATOR_TIMEOUT`) holds:

  | Variable | Was | Now | Where |
  |---|---:|---:|---|
  | `ORCHESTRATOR_TIMEOUT` | 3600 | **5400** | `tests/scripts/test-acceptance.sh` |
  | `SOFT_DEADLINE_SECONDS` | 3300 | **5100** | `platforms/claude-code-plugin/tools/saga_driver.py` |
  | `MAX_LAYER_SEC` | 3600 | **5400** | `tests/scripts/test-acceptance.sh` |

  Origin: BDD-RT-001 live cascade run #2 converged to PASS at score 95
  (verdict.json `combined_status: PASS`) in **58:38 of wall-clock** —
  within 1:22 of the 3600s saga ceiling. The wrapper SIGTERM killed the
  saga driver before its terminal output could flush, so summary.json
  recorded `doc-bdd-autopilot: FAIL` despite verdict.json reading PASS.
  The 5400s budget gives ~50% headroom over the BDD case and the same
  margin over expected ADR / SPEC / TDD / IPLAN cascade durations
  (those layers carry larger per-artifact content than BDD).

  No SKILL changes. Per-claude-subprocess timeout
  (`SUBPROCESS_TIMEOUT_SECONDS=1800` in saga_driver.py) and per-skill
  leaf timeout (`SKILL_TIMEOUT=600` in test-acceptance.sh) unchanged —
  no individual subprocess came close to those caps. Cost-cap
  (`--cost-cap`, ~$22) remains the dollar guard.

### Fixed — sdd_doc_lint STY03 counted code-fenced content

- **STY03 word-count now excludes code-fenced blocks**, mirroring STY02
  and AS3 (`tools/sdd_doc_lint/__init__.py`, plus byte-identical
  vendored copies under `platforms/{claude-code-plugin,hermes}/sdd_doc_lint/`).
  Before this fix the whole-document body-size check counted every word
  inside ``` … ``` blocks, which made any non-trivial BDD body trip the
  blocking threshold: the `doc-bdd` SKILL allows ~50k tokens of fenced
  Gherkin per artifact, while STY03's BDD target is 1500 words (blocking
  at 2250). A prose-light, scenario-heavy BDD-01.md hit STY03 at 2977
  words despite only ~1013 prose words.

  Regression test at `tests/unit/test_sdd_doc_lint_sty03_fences.py`
  (two cases: fenced-heavy doc must not trip STY03; prose-only doc over
  the blocking threshold must still trip STY03). Surfaced during
  BDD-RT-001 live cascade; the `doc-bdd-autopilot` orchestrator
  correctly diagnosed the framework workflow gap and refused to
  hand-edit the artifact. No SKILL changes, no VERSION bump (matches
  precedent commit `b777c08f` for the BRD-INDEX STRUCT01 fix).

### Added — AUTO-REMEDIATE-001 (cascade bootstrap auto-remediation)

- **Cascade bootstrap auto-remediation for STY03 lint failures.** When
  `tests/scripts/test-acceptance.sh` `phase_0_bootstrap` lint-smoke
  fails with STY03 (doc-body word-count) errors only, the harness now
  auto-dispatches `doc-<layer>-fixer` in `single_pass` mode with a
  synthetic audit verdict (P1 STY03 finding) to remediate before
  proceeding. Other lint failures still abort. Single-attempt; if STY03
  persists after the fixer cycle, the harness restores the doc to its
  pre-remediation state and aborts with a clear diagnostic.

  Closes the workflow gap that blocked BDD-RT-001 (EARS-01.md after
  EARS-RT-001 iter-2 fixer pushed it over the 2250-word blocking
  threshold). Framework-driven remediation only — no hand-edits per
  the durable convention *Never hand-edit example artifacts* (codified
  in CLAUDE.md in this same PR).

  Live cascade validation: EARS-01.md auto-remediated from 2457 → 2250
  body words by doc-ears-fixer single_pass; 44/44 element IDs and
  114/114 trace tags preserved; doc-brd-autopilot subsequently ran
  clean.

  Implementation: 7 new helper bash functions (~80 lines) in
  test-acceptance.sh + paired unit test suite at
  tests/scripts/test-auto-remediate-helpers.sh (13 tests, all passing).
  No SKILL changes, no framework/VERSION bump, no plugin/VERSION bump.

### Added — Framework Spec 0.14.3 + Plugin 0.9.0 → 0.10.0 (ADR-RT-001)

- **Framework Spec 0.14.2 → 0.14.3 — 6 ADR-layer playbooks.**
  `framework/playbooks/05_ADR/{architect,tech_lead,security_engineer,operator,auditor,chaos_engineer}.md`
  added per the §Playbooks contract from 0.14.0. Hybrid content shape
  (reasoning frame + Cn deterministic checks + beyond-checklist
  escape hatch + 0-100 scoring rubric). Crew weights
  35/25/12/10/10/8 = 100 per `REVIEW_CREWS.yaml`.

  **First layer where security dominates over chaos** (12 > 8) —
  ADRs encode trust boundaries, authn/authz choices, and crypto
  decisions. PATCH bump (new content within existing artifact
  class, no contract changes).

- **Claude Code plugin 0.9.0 → 0.10.0 — ADR layer team-mode + playbook injection.**
  `doc-adr-audit/SKILL.md` (268 → 500 lines) gains `## Review Mode`
  (team mode default at gates) + `## Saga interaction` +
  `## Break-circuit policy` + playbook injection (step 3a +
  augmented step 4).
  `doc-adr-fixer/SKILL.md` (113 → 299 lines) gains
  `## Remediate Mode` (team-mode patch-validation for P0/P1;
  deterministic for P2/P3) + `## Saga interaction` +
  `## Break-circuit policy`. Mirrors EARS-RT-001 / BDD-RT-001
  wiring pattern.

  **Live ADR acceptance: PASS at score 90/100** (cascade-1
  `verdict.json` `combined_status: PASS`). Score trajectory across
  2 audit cycles: iter 1 → **90 at iter 2** with 1 fixer cycle.
  Per-lens scores at iter 2: architect 95, tech_lead 85,
  chaos_engineer 82, security_engineer 91, operator 82, auditor 100.
  6/6 lens coverage quorum on every audit. Wall-clock **43:48**
  (well within the SAGA-BUDGET-001 5400s ceiling — saga reached
  `CLOSED` cleanly, no SIGTERM at the wire). Parallel lens
  fan-out confirmed in every audit cycle by saga journal (all 6
  `BRANCH_RUNNING` + `BRANCH_COMPLETED` transitions stamped
  same-second × 2 iters = 12 same-second pairs).

  **First observation of team-mode patch-validation firing.**
  The iter 1 fixer dispatched `security_engineer` as a Task
  subagent in patch-validation mode (per the SKILL's
  `BRANCH_COMPENSATING` contract), producing
  `security_engineer.fix_1.json` — the first such slot across
  all per-layer rollouts. BDD-RT-001 had no P0/P1s so the fixer
  ran fully deterministic; ADR-RT-001 surfaced at least one
  P0/P1 and exercised the team-mode validation cycle end-to-end.

  Implementation artifacts: `plans/ADR-RT-001-PLAN.md` (2-cycle
  gap review, 9 Pass-1 findings folded inline + Pass-2 verdict
  clean). Test evidence: `examples/url-shortener/docs/05_ADR/ADR-01.md`
  (365 lines, lint-clean); `examples/url-shortener/.aidoc/review/05_ADR/ADR-01/`
  (6 per-lens slots + 1 fix-validation slot + verdict.json +
  report.md + saga.json with 35 transitions across 2 audit + 1
  fixer cycles + F_fix_report_v001);
  `examples/url-shortener/.aidoc/audit/05_ADR-audit.md` (combined
  unified audit).

### Added — Framework Spec 0.14.2 + Plugin 0.8.0 → 0.9.0 (BDD-RT-001)

- **Framework Spec 0.14.1 → 0.14.2 — 6 BDD-layer playbooks.**
  `framework/playbooks/04_BDD/{qa_lead,tech_lead,chaos_engineer,security_engineer,operator,auditor}.md`
  added per the §Playbooks contract from 0.14.0. Hybrid content shape
  (reasoning frame + Cn deterministic checks + beyond-checklist escape
  hatch + 0-100 scoring rubric). Crew weights 35/25/14/6/10/10 = 100
  per `REVIEW_CREWS.yaml` (chaos-heavy split — failure-scenario ACs
  dominate over abuse-case ACs at BDD layer; +`operator` lens for
  SLO/observability concerns at the gherkin/Then-step level). PATCH
  bump (new content within existing artifact class, no contract
  changes).

- **Claude Code plugin 0.8.0 → 0.9.0 — BDD layer team-mode + playbook injection.**
  `doc-bdd-audit/SKILL.md` gains `## Review Mode` (team mode default
  at gates) + `## Saga interaction` + `## Break-circuit policy` +
  playbook injection (step 3a loads `framework/playbooks/04_BDD/<lens>.md`;
  step 4 inlines into per-lens Task brief).
  `doc-bdd-fixer/SKILL.md` gains `## Remediate Mode` (team-mode
  patch-validation cycle for P0/P1; deterministic application for
  P2/P3) + `## Saga interaction` + `## Break-circuit policy`. Mirrors
  the EARS-RT-001 / PRD-RT-001 wiring pattern.

  **Live BDD acceptance: PASS at score 95/100** (cascade-2,
  `verdict.json` `combined_status: PASS`). Score trajectory across 3
  audits: **80 → 88 → 95** with 2 clean fixer cycles (no regression
  P1 introduced). Per-lens scores at iter 3: qa_lead 95, tech_lead
  100, chaos_engineer 86, security_engineer 92, operator 95, auditor
  100. 6/6 coverage quorum on every audit cycle. Wall-clock 58:38
  (within 1:22 of the 3600s ceiling — triggered SAGA-BUDGET-001 bump
  in the same PR series). Parallel lens fan-out confirmed in every
  audit cycle by saga journal (all 6 `BRANCH_RUNNING` + `BRANCH_COMPLETED`
  transitions stamped same-second).

  Implementation artifacts: `plans/BDD-RT-001-PLAN.md` (2-cycle gap
  review, 8 Pass-1 findings folded inline + Pass-2 verdict clean).
  Test evidence: `examples/url-shortener/docs/04_BDD/BDD-01.md` (32
  scenarios, 5 EARS categories covered, bidirectional `@ears:` matrix);
  `examples/url-shortener/.aidoc/{review/04_BDD/BDD-01/,audit/04_BDD-audit.md}`
  (6 per-lens slots + verdict.json + report.md + saga.json showing 44
  transitions across 3 audit + 2 fixer cycles + combined unified
  audit report).

### Added — Framework Spec 0.14.1 + Plugin 0.7.0 → 0.8.0 (EARS-RT-001)

- **Framework Spec 0.14.0 → 0.14.1 — 5 EARS-layer playbooks.**
  `framework/playbooks/03_EARS/{requirements_specialist,tech_lead,qa_lead,chaos_engineer,security_engineer}.md`
  added per the §Playbooks contract from 0.14.0. Each playbook has the
  hybrid content shape (reasoning frame + Cn deterministic checks +
  beyond-checklist escape hatch + 0-100 scoring rubric). Crew weights
  35/25/20/12/8 = 100 (chaos-heavy split per REVIEW_CREWS.yaml).
  Engine-agnostic; consumed by any platform implementing the team-mode
  spec. PATCH bump (new content within existing artifact class, no
  contract changes).

- **Claude Code plugin 0.7.0 → 0.8.0 — EARS layer team-mode + playbook injection.**
  doc-ears-audit/SKILL.md (267 → 498 lines) gains `## Review Mode` (team
  mode default at gates) + `## Saga interaction` + `## Break-circuit
  policy` plus playbook injection (step 3a + augmented step 4);
  doc-ears-fixer/SKILL.md (113 → 298 lines) gains `## Remediate Mode` +
  `## Saga interaction` + `## Break-circuit policy` (mirrors PRD-RT-001
  fixer pattern). 5 EARS playbook files: requirements_specialist 35 /
  tech_lead 25 / qa_lead 20 / chaos_engineer 12 / security_engineer 8
  = 100 (chaos-heavy split per REVIEW_CREWS.yaml — failure-mode ACs
  dominate over abuse-case ACs at EARS layer). Live EARS acceptance:
  FAIL terminal at iter=5 with score 84/100, blocking=0, all P1s
  resolved (SE-001 abuse-case pair + STRUCT-001 ID format both
  fixed by hand-edits between cascade iterations); security_engineer
  perfect 100/100.

### Added — Framework Spec 0.14.0 + Plugin 0.7.0 (LAYER-PLAYBOOKS-001)

- **Framework Spec 0.13.1 → 0.14.0 — Layer Playbooks artifact class.**
  Per-layer per-lens playbooks at `framework/playbooks/<NN>_<LAYER>/<lens>.md`
  calibrate the review-team's content-quality findings against each
  layer's specific failure modes. Each playbook has a hybrid content
  shape: principle frame + deterministic checklist (Cn checks) +
  beyond-checklist escape hatch. Synthesizer enforces a new required
  `findings[].check` field; uncited findings are discarded. Verdict
  schema gains `playbook_coverage`. See REVIEW_TEAM.md §Playbooks
  and `plans/LAYER-PLAYBOOKS-001-{DESIGN,PLAN}.md`.

- **Claude Code plugin 0.6.5 → 0.7.0 — Playbook injection (BRD + PRD).**
  doc-brd-audit + doc-prd-audit SKILLs load the (layer, lens) playbook
  before fan-out and inline its content into the per-lens Task brief.
  Synthesizer agent + new `finding_filter.py` + `playbook_loader.py`
  helpers (stdlib-only) deliver the schema-enforcement + coverage
  emission. Live BRD acceptance: PASS @ 93/100 with 71% findings
  citing playbook checks.

### Deferred

- 5 audit SKILLs (doc-{bdd,adr,spec,tdd,iplan}-audit) lack team-mode
  wiring; playbook injection for those layers ships as part of per-layer
  follow-up PRs (BDD-RT-001 through IPLAN-RT-001). Trackers: see
  the project's task list.

### Changed — Framework Spec 0.13.0 → 0.13.1 (CHG-gated)

- **DOC_GOVERNANCE_CORE.md — new Principle 8: change-of-record discipline.**
  - Edit: `framework/governance/DOC_GOVERNANCE_CORE.md` adds an 8th
    principle requiring every change to keep its documents-of-record
    in sync within the same PR. No catch-up "doc-refresh" PR may
    follow a change.
  - The principle is engine-agnostic: both platforms must honor it.
  - Enforcement lives outside `framework/` (in
    `scripts/sync-version-refs.sh` + `scripts/check-docs-updated.sh`,
    wired via `.pre-commit-config.yaml`), so the framework spec
    states the rule but doesn't ship the implementation — consistent
    with `framework/` being engine-agnostic.
  - SemVer: PATCH (`0.13.0 → 0.13.1`). Editorial / additive — no
    template, schema, or transition-table changes; no behavior
    contract changes for either platform's existing implementation.

### Changed — Claude Code plugin (plugin-only; no spec change)

Plugin-side post-spec-0.13.0 work. The entries below describe how the
plugin implements (and iterates on the implementation of) the
saga-lifecycle contract codified in SAGA-PARITY-001 Phase 1. See
[`platforms/claude-code-plugin/CHANGELOG.md`](platforms/claude-code-plugin/CHANGELOG.md)
for the per-release plugin detail.

- **Plugin v0.6.0 — BRD-layer saga via cooperative enforcement
  (SAGA-PARITY-001 Phase 2).** First plugin implementation of the
  framework saga lifecycle; SKILL-prompt-driven cooperative
  enforcement of state-machine transitions. Empirically failed
  end-to-end verification (invalid transitions, non-terminal final
  status, no actual subprocess dispatch); fixed in Amendment 1
  (below).
- **Plugin v0.6.1 — preemptive saga driver
  (SAGA-PARITY-001 Phase 2 Amendment 1).** New `tools/saga_driver.py`
  (Python stdlib-only) replaces cooperative enforcement with
  deterministic script-driven enforcement; vendored alongside the
  framework bundle. 7 in-flight bugs (B1-B7) fixed on the same branch
  per the submit-only-finalized-work principle. Verified end-to-end on
  the 4th live BRD cascade: `status: CLOSED`, score 96/100, 10/10
  pass criteria. PRD..IPLAN saga driver propagation deferred to
  Phase 4.
- **Plugin v0.6.2 — 5 content sub-checks across 8 audit SKILLs
  (REVIEW-CALIBRATION-001).** Adds A1 cell-actionability + A2
  assumption-capture + A3 cross-section pointer-validity (auditor
  lens), BA1 acceptance-criterion testability (business_analyst
  lens), SE1 deferred-decision safety (security_engineer lens) —
  uniformly applied across all 8 layer audit SKILLs. Catches 5
  substantive content-quality issues that v0.6.1's review missed
  (visit-count AC untestable; sync-response content unspecified;
  qualitative budget non-actionable; assumption-shaped prose buried
  in FRs; Med/High risks with deferred mitigation). Verified
  before/after on the saved BRD-01: all 5 issues remediated. No
  spec touch, no new lens, no weight changes.

### Added — Project-level conventions

- **"Submit only finalized work" durable convention**
  (CLAUDE.md, [#90](https://github.com/vladm3105/aidoc-flow-framework/pull/90)) —
  every PR (plan or impl) must already have completed its
  review-and-fix cycles locally; post-merge amendment PRs to recently-
  merged work are forbidden.
- **"Minimal-and-realistic plans" durable convention**
  (CLAUDE.md, [#93](https://github.com/vladm3105/aidoc-flow-framework/pull/93)) —
  a plan should be sized to the problem it addresses, not "a perfect
  plan to do everything"; speculative scope gets parked as one-line
  backlog enumeration, not drafted.
- **Two-cycle plan review (mandatory)**
  (CLAUDE.md, [#86](https://github.com/vladm3105/aidoc-flow-framework/pull/86) + [#90](https://github.com/vladm3105/aidoc-flow-framework/pull/90)) —
  every plan must complete ≥2 full review→patch→re-review cycles
  BEFORE the plan PR opens.
- **Plugin-first development sequencing**
  (ROADMAP.md, [#97](https://github.com/vladm3105/aidoc-flow-framework/pull/97)) —
  features land on the plugin first; Hermes follow-on batches per
  `plans/HERMES-BACKLOG.md`.
- **"Update docs of record per PR" durable convention + 2-tier hooks**
  (CLAUDE.md / CONTRIBUTING.md / DOC_GOVERNANCE_CORE.md Principle 8 / PR #99) —
  every PR keeps its docs-of-record in sync inline (no catch-up
  doc-refresh PR). Enforcement: `scripts/sync-version-refs.sh`
  (mechanical, auto-propagates VERSION changes) +
  `scripts/check-docs-updated.sh` (semantic warning when code/spec
  changes don't touch any doc-of-record). Both wired via
  `.pre-commit-config.yaml`.

### Changed — Framework Spec 0.12.0 → 0.13.0 (CHG-gated)

- **Review-saga lifecycle promoted to framework spec
  (SAGA-PARITY-001-PHASE-1, D-0031).**
  - New: `framework/governance/REVIEW_SAGA.md` — engine-agnostic saga
    lifecycle contract (state machine, transitions, journal schema,
    break-circuit policy, FRAMEWORK_SPEC_VERSION semantics,
    enforcement-asymmetry caveat).
  - New: `framework/governance/saga.schema.json` — formal JSON Schema
    for the per-run saga journal.
  - Edit: `REVIEW_TEAM.md` adds two one-line `> See also`
    cross-references to REVIEW_SAGA.md (no content duplication).
  - D-0031 supersedes D-0005's scope-narrowing premise. D-0005's
    blackboard-for-crew-state reasoning remains authoritative.
  - `framework/VERSION`: `0.12.0 → 0.13.0`.
  - Both platforms declare `FRAMEWORK_SPEC_VERSION = 0.13.0` (intent
    to conform; implementation arrives in Phases 2 and 3 of
    SAGA-PARITY-001).

### Changed — Framework Spec 0.11.3 → 0.12.0 (CHG-gated)

- **Adversary review-lens partitioned into `chaos_engineer` + `security_engineer`
  (CHAOS-SEC-SPLIT-001, D-0030; plan in #78, impl in #79).**
  - `framework/governance/REVIEW_CREWS.yaml`: removed `adversary` from the
    personas registry; added `chaos_engineer` (internal stability) and
    `security_engineer` (external threats). All 8 crews rewritten with new
    per-layer weights (all sums = 100) and `# rationale:` comments per crew.
    Bias: BRD/EARS chaos-heavy (12:8), BDD chaos-heavy (14:6), ADR
    security-heavy (8:12), PRD/SPEC/TDD equal split, IPLAN chaos-only.
  - `framework/governance/REVIEW_TEAM.md`: prose mention of `adversary`
    updated to reference both new lenses; new `## Weight allocation rules`
    subsection codifies the four-category allocation protocol
    (chaos-heavy / security-heavy / equal / chaos-only).
  - `framework/VERSION`: 0.11.3 → 0.12.0.
  - Per-platform impact: Claude Code plugin bumped to v0.5.0 (BREAKING —
    blackboard slot filenames change: `adversary.json` →
    `chaos_engineer.json` + new `security_engineer.json`). Hermes
    FRAMEWORK_SPEC_VERSION bumped to 0.12.0; Hermes' runtime persona was
    already `chaos_engineer` so the migration was minimal (translation
    layer removed, new persona file added). Per-platform changelogs
    document the breaking-surface details.

### Fixed

- Closed a confabulation hole in the Claude Code plugin's read-time/audit
  skills: `doc-flow` and every `doc-<layer>-audit` skill now explicitly require
  the auditor to load the corresponding `*-TEMPLATE.yaml` and enumerate the
  required sections from it before running the structural check, with a
  written ban on rationalising drift as a "compact" / "walkthrough" / "lint-
  pinned" variant. The audit Structure cells now defer to that enumeration
  instead of hard-coding "all N template sections", which was a brittle parallel
  source of truth. Also realigned three creation skills with their templates:
  `doc-brd` (replaced an 18-section list containing phantom sections — User
  Stories, Implementation Approach, Support & Maintenance, Cost-Benefit, Quality
  Assurance — with the template's actual 15 numbered sections plus the diagrams
  registry and appendix backmatter; remapped `§7.2 ADR Requirements` → `§8
  adr_topics` everywhere it was cross-referenced; dropped stale `§3.6/§3.7`
  Platform-vs-Feature cross-refs that never existed in the template), `doc-ears`
  and `doc-adr` (renumbered to count `document_control` as Section 1, matching
  the template's own `# Section N:` numbering and the PRD-style convention).
  New conformance test `tests/conformance/platforms/test_skill_template_alignment.py`
  prevents the drift class from recurring: audit skills must carry the explicit
  enumeration block and no hard-coded count; creation skills' `Required structure
  (N sections)` heading must match the template's numbered count; and creation
  skill section lists must use only template-derived vocabulary (no phantoms).
  Template is the single source of truth (D-0013).
- Purged the pre-migration legacy taxonomy from the Hermes prompt templates so
  the creation/review/remediation agents follow the v3.2 source-of-truth naming
  convention (`ucx_flow_v3`). Removed the 10/12-layer `SYS / REQ / CTR / TSPEC /
  TASKS` model (the framework is the 8 layers BRD→PRD→EARS→BDD→ADR→SPEC→TDD→IPLAN)
  from `UCC_OUTPUT_SCHEMA.md`, `UCC_PERSONAS.md`, and the `UCC_/UCR_/UCRem_`
  prompts; corrected `SPEC` from Layer 9 → 6 and the upstream/downstream chains;
  and converted legacy element-ID forms to the canonical 4-segment
  `{TYPE}.{doc}.{section}.{hash}` (`TYPE.NN.SS.xxxx`) — dropping the type-code +
  sequence variant (`NN.TT.SS`) and 3-segment forms (`ADR.{doc}.{seq}`). Renamed
  PRD's legacy `SYS-Ready` score to `SPEC-Ready`. Platform-only; no framework
  spec change.

### Changed

- Framework spec **0.11.2 → 0.11.3** (patch, additive) — new
  `framework/governance/PROFILE-TEMPLATE.yaml` skeleton ships as the
  bootstrap source for project profiles. Operationalises the precedence
  chain (`framework defaults < user-global seed < project profile`)
  documented in `framework/governance/ADAPTATION.md` since v0.11.0:
  bootstrapped `.aidoc/profile.yaml` now carries no hardcoded overrides
  — every adaptation knob is commented out, falling through to
  framework defaults. Frees the framework to evolve crew/persona
  defaults without breaking existing projects (which was foreclosed by
  the previous bootstrap-as-byte-copy behaviour). No schema or rule
  change; no existing key removed; every existing profile continues to
  parse. Plugin v0.4.1 → v0.4.2 binds the new mechanism. New
  conformance test
  `tests/conformance/platforms/test_profile_schema.py` validates the
  closed-surface contract for project profiles. Both
  `FRAMEWORK_SPEC_VERSION` files (Hermes + plugin) and the 52 plugin
  skills' `framework_spec_version` re-synced to 0.11.3. See
  `plans/PROFILE-DELTA-OVERRIDE-PLAN.md` and DECISIONS.md D-0025.
- **Acceptance suite: `--dry-run` and `--no-live` consolidated into a
  single behaviour.** The two modes overlapped on Phase 0 preflight
  (manifest validate, profile check, fixtures presence) — running
  both back-to-back wasted a Phase 0 pass. `--no-live` now prints the
  planned-execution summary (phases, cost cap, timeouts, live status)
  at the top of every run, *then* continues into the full
  deterministic suite (negative fixtures + hook). `--dry-run` is kept
  as a clean alias of `--no-live` (the conventional name is widely
  expected). One mode is now sufficient for both "preview before
  spending" and "verify deterministic infrastructure" — strictly more
  coverage than the old `--dry-run` (which exited after Phase 0).
- **Acceptance methodology consolidated into permanent docs.** The
  example-scoped `examples/url-shortener/ACCEPTANCE_TEST_PLAN.md`
  (733 lines) was split into framework-wide permanent locations so
  future examples (`payment-gateway`, etc.) reuse a single source of
  methodology truth: [`tests/ACCEPTANCE.md`](tests/ACCEPTANCE.md) —
  the engine-agnostic methodology (driver, log layout, schema,
  `--promote` algorithm, phase definitions, design decisions, cost
  ballpark, CI integration); [`plans/ACCEPTANCE-SUITE-HISTORY.md`](plans/ACCEPTANCE-SUITE-HISTORY.md)
  — per-PR implementation timeline + v1→v4 plan evolution + lessons
  learned; and a thin
  [`examples/url-shortener/README.md`](examples/url-shortener/README.md)
  (~120 lines) covering only what is unique about that seed. Adding a
  sibling example is now just `seed/` + `chg/` + a ~50-line README
  pointing at the methodology — no duplication of phase definitions,
  schema docs, or design decisions. Framework spec **0.11.1 → 0.11.2**
  (patch) covers the engine-agnostic doc-link relocations (see
  immediately below).
- Framework spec **0.11.1 → 0.11.2** (patch) — doc-only refs in
  `framework/README.md` and `framework/docs/AIDOC.md` updated to
  point at `tests/ACCEPTANCE.md` (relocated from
  `framework/docs/ACCEPTANCE_TESTING.md` so the framework spec stays
  engine-agnostic). No schema or rule change. Both
  `FRAMEWORK_SPEC_VERSION` files (Hermes + plugin) and the 52 plugin
  skills' `framework_spec_version` re-synced to 0.11.2.
- Framework spec **0.11.0 → 0.11.1** (patch) — doc-only addition of
  `framework/docs/AIDOC.md` formalising the `.aidoc/` provenance tier
  as part of the engine-agnostic spec. No schema or rule change. Both
  `FRAMEWORK_SPEC_VERSION` files (Hermes + plugin) and the 52 plugin
  skills' `framework_spec_version` re-synced to 0.11.1.
- **Test runners co-located under `tests/scripts/`.** Moved `test-plugin.sh`,
  `test-layer.sh`, and `test-fullpath.sh` from the parent repo's `scripts/`
  into `framework/tests/scripts/`. The framework is now fully self-testable
  with no parent-repo dependency; `tests/` becomes the single boundary for
  everything related to verifying the spec. Run-log layout reorganised into
  per-run directories keyed by ISO timestamp:
  - Example-driven default suite (Phase 3 `sdd_doc_lint` + Phase 4 live
    probe target a specific example) → `examples/<NAME>/logs/<TS>/`
    (`plugin-test.log` + `probe-doc-flow.txt`).
  - Fixture-driven suites (unit / layer / fullpath / pre-deploy / packaging /
    release / smoke / review — none touch `examples/`) →
    `tests/logs/<TS>/plugin-test.log`.

  `.gitignore` updated to cover both. Default-suite Phase 3 now SKIPs cleanly
  when the targeted example's `docs/` is missing or empty (post-demo-reset
  state) instead of silently passing on zero files. Internal doc references
  (`tests/README.md`, `tests/HOWTO.md`, `tests/TROUBLESHOOTING.md`,
  `tests/smoke/COMMANDS.md`, `examples/url-shortener/README.md`) updated to
  the new path. Companion parent-repo PR drops the obsolete copies and
  updates `release.yml` to call `framework/tests/scripts/test-plugin.sh`.
- Framework spec **0.9.1 → 0.10.0** (minor) — AUTHORING-STYLE follow-up
  AS2: every section in every layer template (8 × ~10 sections = 76
  sections) gains a `_size_target` key with an explicit per-section word
  count drawn from AUTHORING_STYLE.md tiers (100 / 200 / 300 / 500 / 800
  per section purpose). `sdd_doc_lint` STY02 now reads this per-section
  target via heading-to-key normalisation (with `_BLOCKING_FACTOR = 1.5`
  applied) instead of the flat 200-word default; behaviour identical for
  sections without a `_size_target` key. Both `FRAMEWORK_SPEC_VERSION`
  files (Hermes + plugin) and the 50 plugin skills' `framework_spec_version`
  re-synced to 0.10.0.
- Framework spec **0.9.0 → 0.9.1** (patch) — AUTHORING-STYLE follow-up AS6:
  PRD-TEMPLATE.yaml `_guidance` blocks normalised to imperative voice
  ("Specify" replaces "Elaborate" in three places). No spec semantics
  change. Both `FRAMEWORK_SPEC_VERSION` files (Hermes + plugin) and the 50
  plugin skills' `framework_spec_version` re-synced to 0.9.1.
- Framework spec **0.8.1 → 0.9.0** (minor) — additive governance change:
  adds principle 7 ("token-efficient authoring") to `DOC_GOVERNANCE_CORE.md`
  and the new `AUTHORING_STYLE.md` governance doc. Both
  `FRAMEWORK_SPEC_VERSION` files (Hermes + plugin) and the 50 plugin skills'
  `framework_spec_version` re-synced to 0.9.0.
- Framework spec **0.8.0 → 0.8.1** (patch) — AUDIT-FIXUPS WS-A: the ADR (L5)
  template now **requires** a decision/interaction `sequenceDiagram` (carrying its
  intent header + `@diagram: sequence-*` tag), with `flowchart` demoted to an
  optional supplement — matching `DIAGRAM_STANDARDS.md` ("Required decision
  sequence"). Previously `ADR-TEMPLATE.yaml` offered sequence/flowchart as equals
  and never required the sequence. Both `FRAMEWORK_SPEC_VERSION` files + the 54
  plugin skills' `framework_spec_version` re-synced to 0.8.1.
- Platform agents now apply the framework's **C4 + DFD + sequence** diagram model
  (`framework/governance/DIAGRAM_STANDARDS.md`) in review and creation.
  Hermes review personas (`architect`, `integration_lead`, `auditor`) gained
  per-layer diagram-review lenses (injected into every crew); the SPEC review
  prompt now verifies the C4-L3/DFD-L3 diagram contract; the orchestrator's
  `references/diagram-standards.md` was de-contaminated of plugin-only tokens
  (`mermaid-gen`, `.claude/skills/…`) and now points to the framework as
  authority. Plugin agents (`solutions-architect`, `traceability-auditor`,
  `code-reviewer`) make the C4/DFD/sequence + `@diagram:` tag + C4-L4 ownership
  checks explicit. Also corrected a residual legacy layer number (SPEC
  **L9 → L6**) in the `tech_lead`/`integration_lead` personas and the SPEC
  review/remediation prompts. Platform-only — no framework spec change.
- Framework spec **0.7.1 → 0.8.0** (minor) — AGENT-TEAM Phase 0: the
  engine-agnostic **review-team** model. New `framework/governance/REVIEW_TEAM.md`
  (multi-persona crews + a hub blackboard + the persona-output contract + a
  deterministic weighted/capped scoring & conflict policy with the structural gate
  as the reproducible floor + create/review/remediate shapes + resilience/security)
  and `framework/governance/REVIEW_CREWS.yaml` (per-layer crews + scoring weights +
  default mode). Adds a `review_mode` (`team`|`single_pass`) knob to
  `ADAPTATION_SURFACE.yaml`. New `tests/conformance/test_review_team.py` validates
  the crews (layers ⊆ 8, personas ⊆ the closed set, weights sum to 100); both new
  governance files registered in the README + `test_governance` (suite now 54).
  Engine-agnostic — each platform binds the personas to its own agent runtime
  (Phase 1 Hermes conform, Phase 2 plugin build). Both `FRAMEWORK_SPEC_VERSION`
  files + the 54 plugin skills' `framework_spec_version` re-synced.
- Framework spec **0.7.0 → 0.7.1** (patch) — documentation consistency pass
  (post-EARS-changes review). Corrected three 3-segment element-ID examples in
  `EARS-TEMPLATE.yaml` to the canonical 4-segment form (`TYPE.NN.SS.xxxx`): the
  `id_standard` example (`EARS.01.c4d8` → `EARS.01.03.c4d8`, which had contradicted
  its own stated format) and two `_antipatterns` (`PRD.01.1dbc`/`BRD.02.f1de` →
  4-segment, so each shows only its named flaw). Added `SECURITY_REVIEW.md` and
  `REVIEW_REMEDIATION_FLOW.md` to the `QUICK_REFERENCE.md` Key Files table (they
  were missing since their introduction). Both `FRAMEWORK_SPEC_VERSION` files and
  the plugin skills' `framework_spec_version` re-synced. No schema/rule change.

- Framework spec **0.6.0 → 0.7.0** (minor) — DOC-CHECK Phase 0: model the
  **review→remediation→gate quality loop** and its **trigger points** in the spec
  (new `framework/governance/REVIEW_REMEDIATION_FLOW.md`). Previously review and
  remediation existed only as platform capabilities; the spec now names the loop
  (`Draft → Review → Remediate → Gate → Approved`) and four engine-agnostic
  trigger points — `on_author`, `on_gate_fail`, `pre_promotion`, `pre_merge` —
  with a **light conformance contract**: at each point an engine supports, it
  surfaces findings, the readiness score vs the gate, and the remediation path;
  *how* (deterministic vs LLM, hook vs CI) is the engine's choice, and each engine
  documents its own trigger-point → capability mapping. Does not change the
  readiness-gate threshold or the CHG gates. Additive/backward-compatible.
  Registered in the governance README + `test_governance` `EXPECTED_FILES`; both
  `FRAMEWORK_SPEC_VERSION` files and the 54 plugin skills' `framework_spec_version`
  re-synced. *(Platform triggers — the write-time hook (#1) and PR-time CI (#2) —
  follow as a separate platform/tooling change.)*
- Framework spec **0.5.0 → 0.6.0** (minor) — FRWK-REVIEW finding **#4b**: EARS
  statement-model reconciliation. The EARS layer described its own model four
  different ways (template/README: 4 patterns in `THE…SHALL` form; index: 5 types
  in a non-EARS `…THEN…` form; plugin `requirements-analyst`: 5 patterns dropping
  Unwanted; Hermes personas: 6). Standardized on **canonical EARS** (decision
  D1=A): the five patterns **Ubiquitous, Event-driven (WHEN), State-driven
  (WHILE), Optional (WHERE), Unwanted (IF)**, all using the canonical response
  clause `THE [component] SHALL …` — the non-EARS `THEN` connective is removed.
  Added the missing **Optional / `WHERE`** pattern (guidance + structured
  `optional_feature` block) to `EARS-TEMPLATE.yaml`; added the Optional row to the
  README and corrected the index table to the `SHALL` form; documented "complex"
  as *composition* of the base patterns (not a sixth type) and `WITHIN` as a
  framework timing extension. Aligned the first-class plugin docs (`doc-ears`,
  `requirements-analyst`). New `tests/conformance/test_ears_model.py` locks the
  five-pattern set + `SHALL` grammar so the files can't re-diverge (suite now 49).
  Backward-compatible (existing documents stay valid). Both `FRAMEWORK_SPEC_VERSION`
  files and the plugin skills' `framework_spec_version` re-synced. *Deferred:*
  aligning the Hermes vendored `agent-skills`/`prompts` EARS tables (platform
  follow-up, not a framework-spec change).
- Framework spec **0.4.0 → 0.5.0** (minor) — FRWK-REVIEW pre-production audit,
  batch 3 (THRESHOLD de-bloat, #12). Trimmed `framework/governance/THRESHOLD_NAMING_RULES.md`
  to its engine-agnostic naming/tag/boundary core: **genericized** the
  domain-specific financial examples (KYC verification tiers, B2B/B2C scaling,
  AML/CTR/SAR abbreviations, USD framing) to neutral `quota`/tier placeholders in
  place, and **removed** the runtime/operational machinery that is out-of-charter
  for a spec that ships no runtime — the §8 *Environment Override Rules*
  (override permission matrix, prod override workflow, environment scaling), the
  §12 governance *configuration-propagation* SLAs ("within 60 seconds") and the
  *approver-role* matrix. Condensed the duplicated per-layer usage examples (§1.3.3
  now points to §6). Replaced the stale "UCX Flow Team" / 2025-12-16 document
  history with a neutral provenance note. No programmatic consumer parses the
  file (verified across both platforms); references to it are documentation
  links, which still resolve.

  > **Deprecation note.** Threshold *runtime/override/operational* policy is no
  > longer specified by the framework. A consuming project that relied on the
  > removed §8/§12 operational guidance should define environment-override and
  > rollout policy in its own configuration governance; the framework standard
  > now covers only naming, `@threshold:` referencing, and boundary semantics.

- Framework spec **0.3.2 → 0.4.0** (minor) — FRWK-REVIEW pre-production audit,
  batches 1 (correctness) + 2 (security). **Correctness:** corrected malformed
  trace-tag examples in the SPEC/TDD templates to the registry's element form
  (`TYPE.NN.SS.xxxx`, never a `TYPE-NN.SS.xxxx` hybrid) and added an `id_standard`
  note to the SPEC/TDD/IPLAN templates documenting where document-level refs are
  the intentional per-component bridge; reframed the BDD template's downstream
  guidance; closed a numbering gap in the BRD template's extra-small requirement
  IDs; renamed the PRD index status "Review" → "In Review" with a
  doc-status-vs-lifecycle note; documented the index-template extension split in
  the layer registry; retired stale "5-Gate" branding now that GATE-SPEC is the
  sixth gate, unified the emergency post-mortem SLA to 48h, and surfaced GATE-SPEC
  on the change-approval form + post-mortem template. **Security:** new
  `framework/governance/SECURITY_REVIEW.md` (engine-agnostic safety checks for
  agent-authored artifacts — secret leakage, prompt-injection, provenance,
  active-content sanitization), referenced from `DOC_GOVERNANCE_CORE.md` and the
  gates; a new blocking `GATE-03-E008` requiring external-source changes to cite a
  CVE/advisory or an explicit `no advisory applies: <reason>` escape (W001 kept as
  the softer nudge); a `DIAGRAM_STANDARDS.md` sanitization rule for mermaid click
  handlers + inline HTML; and a `GATE-SPEC-W003` security/abuse-review check for
  agent-facing spec changes. New `tests/conformance/test_framework_review_guards.py`
  locks the correctness fixes in (suite now 46 tests); `test_governance.py`
  `EXPECTED_FILES` gains `SECURITY_REVIEW.md`. Both `FRAMEWORK_SPEC_VERSION` files
  and the plugin skills' `framework_spec_version` re-synced.
- Framework spec **0.3.1 → 0.3.2** (patch) — `framework/README.md` governance
  section now documents GATE-SPEC, the project adaptation overlay
  (`ADAPTATION.md` + `ADAPTATION_SURFACE.yaml`), and `DECISIONS.md` (the
  spec-level decision register). Doc-only; both `FRAMEWORK_SPEC_VERSION` files
  and the plugin skills' `framework_spec_version` re-synced.

### Added

- **Acceptance suite: resume + partial-execution support.** The driver
  (`tests/scripts/test-acceptance.sh`) now survives long-running
  interruptions and supports targeted re-runs without re-spending the
  full $15–25 of a cascade. **Resume** (R1–R6): SIGINT/TERM trap saves
  an incremental `summary.json` and marks in-flight elements
  `INTERRUPTED`; `RUNNING` stubs distinguish in-progress from
  PASS/FAIL/SKIP; `--skip-completed=<path>` resumes against a prior
  run's summary, replaying only `FAIL` / `INTERRUPTED` / `RUNNING`
  elements; schema bumped v1.1 → v1.2 to add the `RUNNING` and
  `INTERRUPTED` outcomes. **Partial execution** (P1–P5): `--element=<name>`
  runs a single named element (skill, agent, command, or hook);
  `--from-layer=<N>` / `--to-layer=<N>` constrain the cascade range
  (e.g. *"generate only the PRD against the existing BRD"*); `--dry-run`
  previews which elements would invoke without spending tokens;
  `--cost-cap=<USD>` halts the run when the running token estimate
  reaches the cap. The companion `summary.json` is the single source of
  truth — `_should_invoke()` consults it before every skill call, so a
  resumed or partial run re-uses prior-PASS outputs as upstream inputs
  for downstream layers.
- **`.aidoc/` — third committed documentation tier formalized.** Per
  every project, four tiers now: inputs (`seed/`, `chg/`, committed),
  outputs (`docs/`, committed), provenance (`.aidoc/`, committed),
  tool internals (`logs/<TS>/`, gitignored). `.aidoc/` holds the audit
  reports, review consensus, remediation logs, validation reports,
  security reviews, and quality suggestions that AI personas produced
  while authoring the project's chain — answering "how did the AI
  arrive at the output in `docs/`?" without needing to re-run the
  suite. New `framework/docs/AIDOC.md` is the canonical reference.
  Acceptance suite (`tests/scripts/test-acceptance.sh`) restructured
  to route skill outputs accordingly: `doc-<layer>-autopilot` → `docs/`,
  `doc-<layer>-audit` → `.aidoc/audit/`, `doc-<layer>-fixer` →
  `.aidoc/remediation/`, `review-team` → `.aidoc/review/`,
  `doc-validator`/`doc-ref`/`gate-check` → `.aidoc/validation/`,
  `security-audit` → `.aidoc/security/`, `quality-advisor` →
  `.aidoc/quality/`. Log layout flattened into single
  `logs/<TS>/elements/<name>.log` per element with YAML front-matter
  plus raw stdout. `.gitignore` rule for `.aidoc/review/` split: only
  `.aidoc/review/.blackboard/` (per-persona scratch) stays ignored;
  consensus reports under `.aidoc/review/<layer>-consensus.md` are
  committed. Acceptance suite includes per-skill timeout (`B4`),
  fixer `tmp/backup/` cleanup (`B5`), token estimation + cost cap
  (`B6` + `A8`), `--skip-completed` (`A6`), `--from-layer=<N>`
  resume (`A7`), retry-on-transient-HTTP-error (`A9`), and per-layer
  runtime cap (`B2`). Schema bumped to v1.1
  (`tests/scripts/test-acceptance.schema.json`).

- **Pre-deployment acceptance test suite** — new
  `tests/scripts/test-acceptance.sh` (~1500 lines) drives every active
  plugin surface element (50 skills + 11 agents + 1 command + 1 hook =
  63 total) against a named example's seed; the produced chain is the
  release-gate evidence that the plugin works end-to-end.

  Driver structure (per
  [`examples/url-shortener/ACCEPTANCE_TEST_PLAN.md`](examples/url-shortener/ACCEPTANCE_TEST_PLAN.md)):
  Phase 0 (bootstrap + preflight: manifest validate, lint smoke, state
  detection, API auth) → Phase 1.1 (happy-path BRD→IPLAN cascade with
  autopilot + audit + optional fixer + lint per layer) → Phase 1.2
  (6-fixture negative validation at
  `tests/acceptance/fixtures/negative/`) → Phase 2 (CHG cycle driven by
  per-example `chg/test-change.md`) → Phase 3 (14 utility probes with
  minimum-coverage thresholds preventing empty-output false-PASS) →
  Phase 4 (11 agents + `/aidoc-flow:save-plan` command + deterministic
  `hooks/sdd-doc-review.sh` test).

  Per-run log layout under `examples/<NAME>/logs/<TS>/` with
  human-readable `summary.txt`, machine-readable `summary.json`
  validating against
  `tests/scripts/test-acceptance.schema.json` (v1.0), and per-element
  `.log` + `.meta.json` under `bootstrap/`, `skills/`, `agents/`,
  `command/`, `hook/`, `cascade/`, `negative/`, `sandbox/`.

  `--mock=<run-dir>` replays a prior recorded run without LLM cost for
  script-development iteration. `--promote` archives the previous
  `examples/<NAME>/docs/` to `docs-archive/v<X.Y.Z>/` and replaces it
  with the freshly-produced cascade output; `--push` pushes the promote
  commit. 45-minute hard wall-clock cap. Token cost per `--live` run:
  ~$11–20.

  First example: `examples/url-shortener/` with seed at
  `seed/initial-requirements.md` and CHG change-set at
  `chg/test-change.md` (visit-rate analytics dashboard).

  Six shared negative fixtures at `tests/acceptance/fixtures/negative/`
  exercise structural-defect detection: missing required sections
  (STRUCT01), malformed trace-tags (ID01), non-existent upstream refs,
  low audit-score content, missing required diagrams, broken chain
  traces. 4 of 6 verifiable deterministically; 2 require live LLM.

  Companion parent-repo PR wires `release.yml` to invoke the acceptance
  suite on tag push with `actions/upload-artifact@v4` and raises the
  `T4L` token-ledger ceiling from 500K to 1M.

- **Token-efficient authoring governance** — new
  `framework/governance/AUTHORING_STYLE.md` canonicalises the writing voice
  the SDD corpus expects: elimination list (benefit statements, efficiency
  claims, ease-of-use claims, future-oriented promises, superlatives, filler
  phrases, verbose introductions, redundant restatement), form enforcement
  (imperative verbs for procedures, conditional statements for error
  handling, tables for parameter specs, bullets for options, one-sentence
  element descriptions, ≤ 3-sentence rationale, `@threshold:` keys for
  quantitative values, precise data types), form-preference order
  (table → bullet → diagram → prose), per-section size defaults (≤ 200 words
  or one table/diagram; ≤ 3 000 words for BRD/PRD bodies; ≤ 1 500 for the
  other layers + CHG), and an audit hook (Tier 2 advisory by default,
  promoted to Tier 1 blocking when ≥ 3 banned phrases occur in one section
  or the document exceeds its size target by > 50%). Promoted to canonical
  governance via `DOC_GOVERNANCE_CORE.md` principle 7. Wired into every
  `doc-<layer>` (creation) and `doc-<layer>-audit` skill as an authority
  reference, and into the audit Structural Checklist as the new
  Authoring-style check block. New conformance test
  `tests/conformance/platforms/test_authoring_style_referenced.py` (5
  checks) guarantees the rule cannot be forgotten when new skills land.
  Follow-up TODOs (linter, CHG-family extension, per-section
  `_size_target`, `_guidance` tightening, fixer auto-fix, skill-body
  retrofit) are tracked in `plans/AUTHORING-STYLE-FOLLOWUP.md`.
- **gitleaks** secret-scanning wired into `.pre-commit-config.yaml` (with
  `.gitleaks.toml` allowlisting the `.secrets.baseline`) — a git-aware scan
  alongside the existing `detect-secrets` baseline check. Added a project
  `.yamllint.yaml` config (line-length 120 as a *warning*; tolerate missing
  document-start and non-bool truthy keys common in our templates) and pointed
  the yamllint hook at it (dropping `--strict` so the configured warnings stay
  non-blocking). Tooling-only; no framework spec change.
- **Pre-commit hooks** (`.pre-commit-config.yaml` + a `pre-commit` CI workflow,
  D-0021): hygiene (whitespace/EOF/check-yaml·json·toml/merge/large-files/
  private-key), **ruff** + ruff-format, **bandit** (gated medium+), **markdownlint**,
  **yamllint**, **detect-secrets** (baseline), **pip-audit** (manual/CI stage), and
  a local hook running the conformance suite. Pragmatic rule sets (stylistic
  noise disabled); `legacy/` + Hermes vendored/parsed content excluded. A repo-wide
  autofix + cleanup pass was applied (markdownlint/ruff over ~450 files, plus
  hand-fixed genuine findings) so `pre-commit run --all-files` is green; the stale
  `ucx_hermes` placeholder config was replaced.

## [0.11.0] — Framework Spec — 2026-05-31

### Added

- Tiered test suite for the plugin (`tests/unit`, `tests/acceptance`,
  `tests/packaging`, `tests/release`, `tests/smoke`, `tests/review`).
- `STRUCT01` lint check (missing required template section).
- `sdd_doc_lint --format=json` structured output mode.
- Per-layer + full-path test runners (`scripts/test-layer.sh`, `scripts/test-fullpath.sh`).
- GitHub Actions: PR gate, release gate, nightly live tier, post-deploy smoke.
- Suite documentation: `tests/README.md`, `SCENARIOS.md`, `HOWTO.md`,
  `ENVIRONMENT.md`, `TROUBLESHOOTING.md`, `CONTRIBUTING.md`, per-tier READMEs.
- `tools/bump_version.py` portable VERSION bumper.

### Changed

- 5 stale skills bumped to align with framework spec.
- Plugin (`claude-code-plugin/v0.4.0`) ships a consolidated canonical skill set: **52 skills = 50 active + 2 deprecated stubs**. Hard-deleted 3 redundant skills (`context-analyzer`, `skill-recommender`, `workflow-optimizer`) — folded into `doc-flow`. Deprecated 2 skills (`doc-review`, `trace-check`) — retained as redirect stubs until v0.5.0, folded into `doc-validator`.
- Plugin marketplace + manifest metadata updated for pre-1.0 preview posture (see `platforms/claude-code-plugin/CHANGELOG.md`).
- IPLAN ↔ iplanic integration explicitly deferred — see [`plans/IPLAN-IPLANIC-DEFERRED.md`](plans/IPLAN-IPLANIC-DEFERRED.md).

## [1.1.0] — 2026-05-24

First post-cutover feature release. Tagged `v1.1.0` at the PR #2 merge; bundles
the canonical plugin skill-set revision, the project adaptation overlay (ADAPT),
and the return of change management as the GATE-SPEC framework-spec gate
(CHG-D1) plus its formal governance record (CHG-D2). Framework spec **0.1.0 →
0.3.1**.

### Changed

- **Plugin layer-model migration (PLM).** Migrated the entire Claude Code
  plugin skill corpus (125 skills) from the legacy **12-layer** SDD model to the
  framework's **8-layer** model (BRD·PRD·EARS·BDD·ADR·SPEC·TDD·IPLAN), closing
  the layer-model gap noted under [1.0.0] and in `docs/PARITY.md` (the gap was
  far larger than that note implied — 116/142 skills carried legacy
  fingerprints). Renamed `doc-tspec*`→`doc-tdd*` and `doc-tasks*`→`doc-iplan*`;
  retired the legacy SYS/REQ/CTR families (142→125 skills); kept the SPEC- and
  test-subtype families as L6/L7 specialization helpers (decision D-0015);
  realigned every layer number, element ID (now 4-segment `TYPE.NN.SS.xxxx`),
  `framework/layers/` path, downstream/traceability chain, and skill
  cross-reference; removed dead validation-script references. Delivered in
  staged, conformance-gated batches B0–B7 (`plans/PLM-PLAN.md`).

### Added

- **Framework governance decision register (CHG-D2).** New
  `framework/governance/DECISIONS.md` — the spec's own durable home for
  decisions about the spec and its governance. Records the CHG implementation
  model (CHG-D1) as **GD-01**, engine-agnostic; lists D-0013 + D-0019 as pending
  graduation from the migration log. Recording it was itself a GATE-SPEC change
  (framework spec **0.3.0 → 0.3.1**, the first real exercise of the gate).
- **GATE-SPEC — the framework-spec change gate (CHG-D1, D-0020).** Implements
  ROADMAP CHG-D1 — change management as skills + CI/CD, both platforms. Adds the
  *meta* gate that governs changes to the `framework/` spec itself (templates,
  governance, registry, VERSION), orthogonal to the artifact-cascade gates: a new
  `GATE-SPEC_FRAMEWORK.md` definition, a `spec` `change_source` + `semver_impact`
  field, error-catalog/interaction-diagram/CHG-template/README wiring. Wired
  through the plugin CHG skills (`gate-check` runs it; `doc-chg` family routes to
  it) and the Hermes server-side validator (`validation/chg_rules.py`). The
  diff-aware checks (E005 VERSION bump, E008 CHANGELOG) ship as
  `tests/chg/spec_gate.py` + a staged CI workflow; the human-approval half is
  documented as protected-branch review. This **unblocks** `knowledge-extractor`'s
  spec-promotion path. Framework spec **0.2.0 → 0.3.0**.
- **Project adaptation overlay (ADAPT, D-0019).** `framework/governance/ADAPTATION.md`
  - machine-readable `ADAPTATION_SURFACE.yaml` (a closed 4-knob surface:
  `active_layers`, `section_toggles`, `audit_threshold` raise-only, `glossary`),
  the `adapts:` consult-clause across the 35-skill adapting set, and two new
  utility skills — `project-profile` (maintains `.aidoc/profile.yaml`) and
  `knowledge-extractor` (promotes proven local adaptations upward). Framework spec
  **0.1.0 → 0.2.0**.
- Conformance check `tests/conformance/platforms/test_plm_lint.py` (suite now
  **32** tests) — fails if any plugin skill reintroduces a legacy 12-layer
  fingerprint, locking the migration in against regression. *(Suite has since
  grown to 43 with the adaptation-surface and GATE-SPEC guards.)*

## [1.0.0] — 2026-05-21

**Phase 5 — Cutover.** The multi-platform project replaces `main`.
The migration from the pre-migration `ucx_framework` (v0.20.4) is
complete: one engine-agnostic specification (`framework/`) plus two
independent platforms (Hermes MCP server, Claude Code plugin), both
green on the shared conformance suite. The pristine pre-migration
project is preserved on the protected, read-only archive branch
`legacy-ucx-v3.2-read-only`.

> Version scope (P5-T1 Q4): `v1.0.0` is the **project-milestone**
> tag for the cutover — *not* a claim that every component is
> 1.0-stable. `framework/` stays `0.1.0` (no spec change; earns
> `1.0.0` later under the returning CHG governance). The plugin
> stays `0.1.0` (documented layer-model gap, see below). The Hermes
> api_runner fix below ships as the optional `hermes/v0.1.1` patch.

### Removed

- In-tree `legacy/` directory (2276 tracked files, ~645k lines) —
  the pre-migration `ucx_framework` working copy. **Lossless:** the
  full content is preserved byte-for-byte on the protected
  `legacy-ucx-v3.2-read-only` branch (`491e8db`) and in git history.
  (P5-T2)
- Dev-time root `.claude/` loader (240 tracked files) — the
  migration-era Claude Code skills/agents/commands/hooks used to run
  the migration itself. The shipped Claude Code delivery is now the
  **plugin** (`platforms/claude-code-plugin/`), not a root loader.
  **Lossless:** skills/agents/commands are productized in the
  plugin; the pre-migration `.claude/` is on the archive branch; the
  migration-era `.claude/` (incl. the 3 hooks) remains in git
  history. (P5-T3)

### Fixed

- `platforms/hermes/src/mcp_server/executor/api_runner.py` — the
  litellm-missing error told users to `pip install 'ucx_hermes[api]'`;
  corrected to `pip install 'hermes-server[api]'` to match the
  distribution rename in P2-T1 Q1. Resolves the carried known issue
  surfaced at P4-T5 verify. Ships as the optional `hermes/v0.1.1`
  patch (see `platforms/hermes/CHANGELOG.md`).

### Changed

- Project docs finalized for the as-built, post-migration state
  (P5-T4): `README.md` (dropped migration framing + `legacy/` from
  the structure diagram; platform matrix → release tags; added
  archive-branch + PARITY/TAGGING pointers); `docs/REPO_STRUCTURE.md`
  (PLANNED → as-built; legacy mapping reframed as history);
  `docs/PROJECT.md` (§3/§4 cutover reconciled to the archive
  branch); `CLAUDE.md` (rewritten from migration-in-progress memory
  to slim post-migration project memory; root file, survived the
  `.claude/` removal).

### Known carried issues (post-v1.0)

- **Plugin SDD layer-model gap** — the plugin reflects the legacy
  11-layer model and lacks `doc-tdd` + `doc-iplan` (`docs/PARITY.md`
  "Known parity gap"). Content depth, not a correctness issue;
  per-skill content migration tracked as post-v1.0 work. This is why
  the plugin honestly stays `0.1.0`.
- **~150 Class D stale `framework/<X>` references** in plugin skill
  content (P3-T2 G18) — same root cause as the layer-model gap.
- **CI workflows** at `plans/workflows-pending/` await user `git mv`
  into `.github/workflows/` from a local clone (in-container GitHub
  App lacks `workflows` permission).

## [0.5.0] — 2026-05-21

Phase 4 — Conformance & Independence. Platform-conformance tests
(PC1 + PC4) added to the shared suite; greenfield CI workflows
authored; per-platform CHANGELOG retrofits; expanded Hermes README;
repo-root LICENSE; parity report.

### Added

- `tests/conformance/platforms/` sub-package with PC1 (version
  declaration: VERSION + FRAMEWORK_SPEC_VERSION files exist, are
  bare SemVer, match `framework/VERSION`) and PC4 (engine isolation:
  forbidden-token scan scoped to runtime-significant directories
  per platform) test modules. Suite grows **25 → 31 tests**.
- Three greenfield GitHub Actions workflows authored, staged at
  `plans/workflows-pending/` pending user `git mv` to
  `.github/workflows/` (in-container GitHub App lacks `workflows`
  permission — see `docs/TAGGING.md` "In-container push
  restrictions"):
  - `conformance.yml` — runs the 31-test conformance suite on
    every push/PR.
  - `hermes.yml` — runs Hermes' pytest suite (Python 3.12 via
    `actions/setup-python@v5`) on push/PR touching
    `platforms/hermes/**` or `framework/**`.
  - `plugin.yml` — smoke-checks the plugin: manifest valid +
    coupling sweep + structural sanity on push/PR touching
    `platforms/claude-code-plugin/**`.
  All `ubuntu-latest`; concurrency cancel-in-progress; minimal
  `contents: read` permissions. No carry-over from
  `legacy/github-workflows-disabled/` (28 workflows, all
  self-hosted-coupled).
- `platforms/hermes/CHANGELOG.md` — Hermes `[0.1.0]` mirroring
  project `[0.3.0]` scoped content. Cross-references project-level
  CHANGELOG and `plans/P2-T*-PLAN.md` for the full audit trail.
- `platforms/claude-code-plugin/CHANGELOG.md` — plugin `[0.1.0]`
  mirroring project `[0.4.0]` scoped content, with a "Known
  limitations" section flagging the legacy-vs-new SDD layer model
  gap.
- `LICENSE` at repo root — MIT, copyright `vladm3105` (matches
  plugin manifest's `"license": "MIT"` placeholder).
- `docs/PARITY.md` — 5-section capability comparison between
  Hermes and the Claude Code plugin: capability matrix (8 SDD
  layers × 2 platforms); workflow operations; platform-specific
  extras; known parity gap (plugin reflects the legacy 11-layer
  model; lacks `doc-tdd` + `doc-iplan`); user-facing
  "choosing between" decision table.
- `docs/STARTUP_HANDOFF.md` — distills business / startup ideas
  from the migration session (IPLAN-as-product, corpus, domain
  profiles, CHG governance-as-code, etc.) for a future strategy
  session. Separate from the technical migration scope.
- Per-task plans `plans/P4-T0..T5-PLAN.md`, the design doc
  `plans/P4-T1-DESIGN.md`, the audit `plans/P4-AUDIT-conformance.md`,
  and the verify record `plans/P4-T5-VERIFY.md`.

### Changed

- `tests/conformance/_spec.py` — extended **additively** with
  platform helpers (`PLATFORMS_ROOT`, `platform_dirs`,
  `platform_version_file`, `platform_framework_spec_version_file`,
  `framework_version`). Existing helpers + imports untouched.
- `platforms/hermes/README.md` — expanded from 27-line Phase-0
  placeholder to 113-line user-facing doc. Full mirror of P3-T3's
  populated plugin README structure: inventory table, install +
  `.mcp.json` snippet, MCP tool list, framework spec conformance
  section, platform info table, relationship-to-plugin section.
- `docs/TAGGING.md` — appended "In-container push restrictions"
  section documenting the two operation classes that need the
  local-clone workaround (`refs/tags/*` — 4 occurrences after
  P4-T5; `.github/workflows/**` — 1 occurrence). Symmetric with
  the existing tag-push reference.

### Known carried issues (deferred)

- **CI workflow files** at `plans/workflows-pending/` — user
  `git mv`'s them into `.github/workflows/` from a local clone.
  Phase 4 closed without that user action; the relocation is a
  transit detail, not a content gap.
- **Plugin legacy-vs-new SDD layer model gap** (P3-T1 §Deferred
  R2 / `docs/PARITY.md` "Known parity gap"). Plugin lacks
  `doc-tdd` + `doc-iplan`; has `doc-sys` / `doc-req` / `doc-ctr` /
  `doc-tspec` / `doc-tasks` from the legacy 11-layer model.
  Hermes covers all 8 new-model layers via its generic `sdd_*`
  tools. Resolution is a per-skill content-migration task tracked
  as post-v1.0 cleanup.
- **`platforms/hermes/src/mcp_server/executor/api_runner.py:115`**
  carries a stale install instruction
  (`pip install 'ucx_hermes[api]'`); current distribution is
  `hermes-server` (P2-T1 Q1). 1-line fix; deferred to Phase 5
  housekeeping or a `hermes/v0.1.1` patch.
- **~150 Class D stale `framework/<X>` references** in plugin
  skill content (P3-T2 G18) — same root cause as the layer model
  gap; resolution post-v1.0.

## [0.4.0] — 2026-05-20

Phase 3 — Platform B: Claude Code plugin. `platforms/claude-code-plugin/`
ships the 142-skill SDD engine as a native Claude Code plugin (no MCP
backend), consumes `framework/` at `v0.1.0`, and is released as
`claude-code-plugin/v0.1.0`. The plugin uses Claude Code's
auto-discovery from `skills/`, `agents/`, `commands/` at plugin root —
no explicit registration in the manifest.

### Added

- `platforms/claude-code-plugin/` — the Claude Code plugin platform.
  171 net files (post-cleanup): 142 skill directories (129 `doc-*`
  - 13 SDD-adjacent non-doc), 19 skill-root files (quickrefs +
  set-overview READMEs + `REVIEW_DOCUMENT_STANDARDS.md`), 1 agent
  (`requirements-analyst`), 1 command (`save-plan`), plus 4 new
  top-level files (manifest + 2 VERSION files + populated README).
- `platforms/claude-code-plugin/.claude-plugin/plugin.json` —
  minimal 7-field manifest (`name`, `description`, `version`,
  `license`, `repository`, `homepage`, `keywords`). Plugin name
  `aidoc-flow`; slash-prefix `/aidoc-flow:doc-...`. Author block
  omitted (the in-container `git config user.name` returns the
  session's identity, not the repo owner; the `repository` URL
  handles ownership signaling — matches Hermes pyproject precedent).
- `platforms/claude-code-plugin/VERSION` (`0.1.0`, 6 bytes) and
  `platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION` (`0.1.0`,
  byte-identical to `framework/VERSION`) — declares the plugin's
  own SemVer + framework-spec conformance per D-0009 / P2-T1 Q2.
- `platforms/claude-code-plugin/README.md` — populated user-facing
  doc (82 lines, from 27-line Phase 0 placeholder): inventory table,
  install pointer, slash-prefix use examples, framework spec
  conformance with VERSION cat output, platform info table,
  Hermes-platform relationship section.
- `plans/P3-T0-PLAN.md` + `plans/P3-AUDIT-claude-code-plugin.md` —
  Phase 3 audit (191-file `.claude/` inventory; copy-with-divergence
  relationship resolved) and task breakdown.
- Per-task plans `plans/P3-T1..T5-PLAN.md`, each with the two-pass
  review log mandated by D-0007.
- `plans/P3-T1-DESIGN.md` — 7 plugin design decisions resolved
  before any content moved (manifest schema verified via the
  `claude-code-guide` agent — Claude Code auto-discovers,
  no explicit registration block; plugin name `aidoc-flow`; copy
  strategy is the 3-stage `cp -r` + `rm -rf` recipe; no lifecycle
  hooks in `v0.1.0`).
- `plans/P3-T4-VERIFY.md` — formal Phase 3 verify record covering
  22 gates (conformance 25/25, plugin structure, coupling sweep,
  manifest validity, integration checks).

### Changed

- Rewrote all `ai_dev_flow` placeholder paths in the ported skill
  content to point at `framework/` — 211 line hits across 30 files
  cleared via word-boundary regex sed (P2-T7 G12). Class B (5 layer
  dirs → `framework/layers/0X_TYPE/`) and Class C
  (`ID_NAMING_STANDARDS.md` → `framework/governance/`) sub-path
  corrections applied. 2 illustration `/opt/data/...` paths
  preserved per the P2-T7 G13 historical-vs-current rule.
- `project-mngt/SKILL.md` — the one current-behavior
  `/opt/data/ucx_framework/...` reference rewired to repo-relative
  `framework/governance/ID_NAMING_STANDARDS.md`.

### Removed

- 7 non-SDD-adjacent skill directories excluded from the plugin
  port: `code-review`, `refactor-flow`, `analytics-flow`,
  `devops-flow`, `ai-pr-review`, `google-adk`, `n8n` (P3-T1 Q2 —
  general-purpose, not coupled to any SDD artifact). Source
  `.claude/skills/` retains them; they remain available in dev-time
  use until Phase 5 cutover.
- 3 `.claude/skills/` root files excluded from the plugin port:
  `README.md` (referenced an obsolete multi-project symlink pattern
  and the legacy `ucx_framework/.claude/skills/` canonical path),
  `google-adk_quickref.md`, `n8n_quickref.md` (parent skills out).
- **47 broken symlinks** the source `.claude/skills/` carried via
  `cp -r` into the plugin — self-referencing pointers at
  `/opt/data/docs_flow_framework/.claude/skills/<name>`, leftovers
  from the old multi-project symlink consumption pattern. Removed
  in-flight during P3-T4 verify (G18 finding) via `xargs git rm`
  on the 47 symlink entries.

### Carried known issue (deferred)

- The ~150 Class D stale `framework/<X>` references in the ported
  skills point at concepts not in the current 8-layer framework
  (`framework/scripts/`, legacy 11-layer numbering,
  legacy alpha-named dirs, legacy top-level guides). Resolution is
  a per-skill content-migration task outside Phase 3 scope (P3-T1
  §Deferred R2). The plugin works as a Claude Code artifact
  regardless — the references are documentation hygiene, not
  runtime correctness.

## [0.3.0] — 2026-05-20

Phase 2 — Platform A: Hermes Re-homing. `platforms/hermes/` is fully
assembled, consumes `framework/` at `v0.1.0`, and ships its own first
release as `hermes/v0.1.0`. The MCP server's scaffold + validation
runtime now reads layer templates from `framework/layers/<NN>_<X>/`
per D-0013, closing the platform-template duplication.

### Added

- `docs/TAGGING.md` — the full git-tag policy: release tags (`vX.Y.Z`,
  `framework/vX.Y.Z`, `<platform>/vX.Y.Z`) and `mark/<slug>` bookmark tags,
  with create / push / find commands (D-0011). `docs/PROJECT.md` §3 slimmed
  to a summary that links it.
- `ROADMAP.md` "Post-v1.0 — Planned Capabilities" — the domain-profile
  mechanism for generalizing the IPLAN beyond software (D-0012).
- `platforms/hermes/` — the Hermes MCP server platform. 437 net files
  ported and rewired across four sub-tasks: 64 verbatim (P2-T2 —
  `examples/`, `prompts/`, `skills/layer_aliases/`, `skills/personas/`,
  `skills/persona_mappings.yaml`); 200 port-with-repoint (P2-T3 —
  `pyproject.toml`, `src/`, `tests/`, `docs/` less `migration/`,
  `skills/README.md`, `skills/hermes/`); 181 agent-skills from `main`
  (P2-T7 — `agent-skills/spec-driven-development/{sdd-orchestrator,
  sdd-review-personas}/`); minus 8 dropped (P2-T8 — drifted layer
  templates that D-0013 obsoleted).
- `platforms/hermes/VERSION` (`0.1.0`) and
  `platforms/hermes/FRAMEWORK_SPEC_VERSION` (`0.1.0`, matching
  `framework/VERSION`) — declares Hermes' own SemVer + the framework
  spec version it conforms to (D-0009 mechanism, P2-T1 Q2).
- `platforms/hermes/pyproject.toml` keys: `name = "hermes-server"`
  (P2-T1 Q1) at `version = "0.1.0"`; `[project.scripts]
  hermes-mcp = "mcp_server.server:main_sync"` (P2-T1 Q4). Distribution
  name distinguishes the project; the `mcp_server` import path is
  preserved (no Platform B Python collision; P2-T1 Q1 rationale).
- `plans/P2-T0-PLAN.md` + `plans/P2-AUDIT-hermes.md` — the Phase 2
  audit (280-file Hermes tree classified port-verbatim / port-with-
  repoint / drop) and the per-task breakdown (T0..T9).
- Per-task plans `plans/P2-T1..T9-PLAN.md`, each with the two-pass
  review log mandated by D-0007.
- `plans/P2-T5-VERIFY.md` — the formal Phase 2 verify record covering
  14 gates (conformance 25/25, Hermes own suite 447/447, coupling
  sweep, version files, smoke test, structure, file inventory).
- `plans/DECISIONS.md` D-0013 — single-source-of-truth for layer
  templates: platforms consume `framework/layers/`, never duplicate.

### Changed

- Recorded the framework's purpose — the IPLAN as the terminal product;
  code/deploy out of scope; v1 scope is software/devops (D-0012).
- Refined D-0012: the IPLAN has a planned and an executed state with
  criticality-scaled audit depth (R1); the curated corpus of proven IPLANs —
  with composition and freshness — is the unit of value and the post-v1.0
  strategic destination (R2).
- Rewrote all `ucx_flow_v3` runtime coupling to point at `framework/`:
  18 files in the edit set (4 code + 3 tests + 5 skills + 6 architecture/
  spec docs), with sub-path repoints to `framework/registry/` and
  `framework/layers/<NN>_<X>/` (P2-T3). 11 historical-context docs
  (CHANGELOGs, ROADMAP retrospective, completed PLAN-* checklists)
  preserved verbatim per the G13 lesson — rewriting them would falsify
  history.
- Rewired the MCP server's scaffold runtime to consume the framework's
  per-layer layout (P2-T9). Five spots across three files closed the
  D-0013 architectural gap that P2-T3 first surfaced: removed the
  `templates/` row from `CANONICAL_SCAFFOLD_MAPPINGS`, rewrote
  `_default_ssd_root` to return `framework/layers`, corrected
  `_default_repo_root` parents count (`[4]→[5]` — layout shifted in
  P2-T3), and rewrote `validation/runner.py:_resolve_canonical_template_root`
  as a 3-stage precedence chain (project framework override → scaffold
  output → canonical). Hermes' own test suite went 397/447 → **447/447**.
- Rewrote the skill's template-loading prose (P2-T8): 25 references in
  `agent-skills/.../sdd-orchestrator/SKILL.md` +
  `references/sdd-workflow-quickstart.md` rewired from skill-relative
  `templates/0N_TYPE-TEMPLATE.yaml` to framework-relative
  `framework/layers/0N_TYPE/TYPE-TEMPLATE.yaml`; the `skill_view` API
  example was rewritten as a direct-read instruction since templates
  now live outside the skill.
- `.mcp.json` cwd repointed from `legacy/ucx_hermes/src` to
  `platforms/hermes/src` (P2-T3).
- `plans/P2-AUDIT-hermes.md` refreshed with §3a extension (3 test
  files added to the code-level coupling list) and §3c (new section —
  "Documentation cluster — historical vs current") to record audit
  gaps discovered during P2-T3 planning.

### Removed

- The 8 drifted layer template YAMLs at `platforms/hermes/agent-skills/
  spec-driven-development/sdd-orchestrator/templates/` (P2-T8). They
  carried engine hardcodes (`server: ucx_hermes`, `tool: sdd_validate`,
  `SDD v3` labels, vendor-named agent placeholders) that D-0013
  excluded from documents. The framework `framework/layers/<NN>_<X>/
  <X>-TEMPLATE.yaml` set is the single source of truth.
- 6 D-0013-obsolete sync files from the agent-skills package (P2-T7):
  `sync-ucx-templates.sh`, `sync.py`, `.sync-backlog.json`,
  `template-sync-procedure.md`, `template-v3-alignment-checklist.md`,
  `ucx-framework-quirks.md`. There is no longer anything to sync —
  Hermes consumes `framework/layers/` directly.
- The `templates/` row from `CANONICAL_SCAFFOLD_MAPPINGS` (P2-T9) and
  the no-op `exists()` branch in `_default_ssd_root` — both dead code
  after D-0013.
- `legacy/ucx_hermes/docs/migration/MIGRATION_FROM_MCP_UCX.md` from the
  port set (P2-T3) — `mcp_ucx/` is the deprecated predecessor, archived
  in `legacy/` and slated for full removal at Phase 5 cutover.

## [0.2.0] — 2026-05-19

Phase 1 — Framework Spec Extraction. `framework/` is fully assembled and
guarded by a 25-test conformance suite. Framework spec released as
`framework/v0.1.0`.

### Added

- Plan-review gate (D-0007): plans require a `## Review log` of ≥2 passes;
  `plans/PLAN-TEMPLATE.md` added; non-blocking `PreToolUse(git commit)` hook
  warns when a staged plan file falls short.
- `plans/P1-AUDIT-ucx_flow_v3.md` — Phase 1 audit (P1-T1) classifying the
  49-file legacy SDD tree as engine-agnostic, mixed, instance, or drop, with
  the target `framework/` layout for the Phase 1 extraction steps.
- `framework/layers/` (P1-T2) — the 8 engine-agnostic SDD layer specs
  extracted from `legacy/ucx_flow_v3/`: per layer a `*-TEMPLATE.yaml`, a
  `README.md`, and a `*-00_index.TEMPLATE.*` index template (24 files). All
  Hermes/MCP- and Claude-Code-specific content removed; legacy version
  strings neutralized.
- `framework/registry/` (P1-T3) — `LAYER_REGISTRY.yaml`, the authoritative
  machine-readable layer model (layer order, traceability graph, C4 mapping,
  ID patterns), plus a `README.md`. Standalone version field and legacy
  changelog dropped; layer `folder` paths repointed under `layers/`.
- `framework/governance/` (P1-T4) — 5 governance docs (`DOC_GOVERNANCE_CORE`,
  `ID_NAMING_STANDARDS`, `TRACEABILITY`, `DIAGRAM_STANDARDS`,
  `THRESHOLD_NAMING_RULES`) and the CHG overlay (`chg/` — README, template,
  index template, 7 gates, 2 companion templates), 18 files. Engine-specific
  skill references and `MCP` mentions neutralized; CHG extracted spec-only
  (not enforced until post-Phase 5).
- `tests/conformance/` (P1-T5) — the shared conformance suite: stdlib
  `unittest` tests covering registry self-consistency, layer templates,
  governance files, the framework root, `VERSION`, and spec hygiene (no engine
  tokens in `framework/`), plus the documented platform-conformance contract
  for Phase 4. No `pytest` dependency (D-0008).
- `framework/README.md` — the engine-agnostic spec overview (8-layer flow, C4
  alignment, layout, conformance, versioning), replacing the scaffolding
  placeholder.
- `framework/VERSION` (P1-T6) — the framework spec's independent version
  stream, at `0.1.0`.
- `docs/PROJECT.md` §3 — tag-namespace convention: project milestones
  `vX.Y.Z`, framework spec `framework/vX.Y.Z`, platforms `<platform>/vX.Y.Z`
  (D-0009).
- `framework/` root methodology docs (P1-T7) — `SPEC_DRIVEN_DEVELOPMENT_GUIDE`,
  `QUICK_REFERENCE`, `AI_ASSISTANT_RULES`, `TESTING_STRATEGY_TDD`, extracted
  engine-neutral (version strings neutralized, links repointed, legacy
  version-lineage content dropped per D-0010).

### Changed

- **Legacy isolation (P1-T0):** all pre-migration content moved into `legacy/`
  (frozen) — `ucx_flow_v3`, `ucx_hermes`, `mcp_ucx`, `ai_dev_ssd_flow_v2`,
  `governance`, and supporting trees. Repo root now holds only the new
  project (`framework/`, `platforms/`, `docs/`) plus infrastructure.
- Legacy GitHub Actions workflows disabled (parked in
  `legacy/github-workflows-disabled/`).
- Root `README.md` rewritten for the multi-platform project.
- `.mcp.json` Hermes server path repointed to `legacy/ucx_hermes/`.

## [0.1.0] — 2026-05-18

Phase 0 — Planning & Scaffolding. The migration baseline.

### Added

- Planning baseline for the multi-platform restructure:
  - `ROADMAP.md` — phased delivery plan (Phase 0 → cutover v1.0.0).
  - `docs/REPO_STRUCTURE.md` — target repository layout and legacy mapping.
  - `docs/PROJECT.md` — versioning, branching, milestones, conformance, and
    interim change-management policy.
  - `platforms/hermes/` and `platforms/claude-code-plugin/` directories.
  - `framework/` directory placeholder for the shared engine-agnostic spec.
- CHG implementation decision recorded as tracked TODO (ROADMAP CHG-D1/D2,
  `docs/PROJECT.md` § CHG implementation model): CHG to be built as
  skills + CI/CD post-Phase 5.
- `CLAUDE.md` — auto-loaded project memory: development workflow
  (plan → review → harden → implement → verify → land), definition of done,
  and session-handoff practice.
- `plans/` workspace — `README.md`, `MIGRATION_TODO.md` (live task tracker),
  `HANDOFF.md` (session continuity), `DECISIONS.md` (decision log).
- `.claude/` automation hooks: `PreCompact` (auto-commit + push a WIP
  snapshot before compaction) and `SessionStart` (inject `plans/HANDOFF.md`
  into context), with scripts under `.claude/hooks/`.

### Notes

- Forked from `ucx_framework` v0.20.4 (`main`).
- The gated CHG change-management process is intentionally not applied during
  the migration; it is re-introduced post-cutover (see `docs/PROJECT.md`).

[Unreleased]: https://github.com/vladm3105/aidoc-flow-framework/tree/claude/multi-platform-migration-AamWB
[0.2.0]: https://github.com/vladm3105/aidoc-flow-framework/releases/tag/v0.2.0
[0.1.0]: https://github.com/vladm3105/aidoc-flow-framework/releases/tag/v0.1.0
