# Framework TODO — Example-Driven Discovery Backlog

> Triage queue for framework inconsistencies / bugs / improvements
> discovered while driving the examples corpus (`examples/url-shortener/`)
> end-to-end. Per [[feedback_framework_todo_list]] and
> [[feedback_seed_examples_are_acceptance_tests]]: examples are the
> system-under-test; their friction is the framework's truth.
>
> **Rules:**
>
> - Append entries inline as discovered. No "later PR" — the entry IS
>   the capture moment.
> - Each entry: tag + one-line title + Context (link to commit/PR/plan
>   that surfaced it) + Fix shape (one-line description of what would
>   resolve it). ≤ 3 lines per entry.
> - Tags: `[lint]` / `[harness]` / `[skill]` / `[template]` / `[sync]` /
>   `[plan-review]` / `[docs]` / `[hermes-parity]` / `[example-corpus]`.
> - Once an item is large enough to design, promote to a formal plan
>   and link from the TODO entry as `→ <NAME>-PLAN.md`. The TODO entry
>   stays open until the plan ships, then moves to **Closed** with the
>   merge-commit ref.
> - Don't double-track. If a plan already exists, cross-reference it
>   instead of creating a new entry.

## Open

### `[legacy]` Scan for v3.2-era anachronisms across the codebase

- *Context:* user-surfaced (2026-06-12) — the `sdd-orchestrator`
  agent-skill still carried `sdd_depth: lite | standard | full` tiers
  from the SDD v3.2 era. The current framework spec has settled on a
  single SDD path (BRD..IPLAN, all 8 required per necessary-upstream)
  with an adaptive loop (MVP → PROD → New MVP → Updated PROD). The
  legacy-sdd-depth follow-up PR removed the depth references but
  surfaced that the orchestrator's broader worldview (15-persona
  model, ucx_hermes templates, SDD v3.2 versioning) is also stale.
- *Fix shape:* dedicated v3.2-residue scan pass: grep across all
  non-`legacy-ucx-v3.2-read-only` paths for: `SDD v3`, `v3.2`,
  `sdd_depth`, `lite|standard|full` triples in SDD context, `15
  personas`, `ucx_hermes/templates`, `sdd_create` / `sdd_validate`
  CLI invocations. Hermes-side scope tracked separately in
  HERMES-BACKLOG H-11.
- *Status:* OPEN — file under `[legacy]` tag.

### `[layer-promotion]` Promote `component_decomposition` to a first-class `02b_DECOMP` layer (Option B from DECISION-GATE-D)

- *Context:* DECISION-GATE-D (2026-06-11) resolved as Option A
  (subsection in PRD). Option B (new layer between PRD and EARS) was
  deferred because most aidoc-flow consumers will have ≤ 5-component
  systems where buried decomp in PRD is sufficient. **User direction:
  "We will have complex projects in the future — keep Option B as
  further development for when Option A is not enough."**
- *When to revisit:* signs that Option A is insufficient include:
  (a) consumer PRDs growing past ~600 lines because component
  decomp is bloating PRD §7b; (b) auditor lens unable to evaluate
  decomp quality at PRD altitude because it competes with product
  concerns; (c) `@decomp:` becoming a desired @-tag form for richer
  downstream binding; (d) C4-L2 diagrams or component-level chaos
  scenarios that don't fit cleanly in PRD §7b.
- *Fix shape (when triggered):* new layer `02b_DECOMP` between PRD
  (02) and EARS (03). `DECOMP-NN.yaml` artifact with components +
  dataflow + threshold bindings. EARS pivots its `required_tags` from
  `[prd]` → `[decomp]`. ADR + SPEC gain `decomp` in their
  necessary-upstream sets. New 6-lens crew (architect, tech_lead,
  integration_lead, chaos_engineer, security_engineer, auditor).
  4 new SKILLs (doc-decomp / -audit / -fixer / -autopilot). Estimated
  framework MINOR `0.20.x → 0.21.0`; 5-6h cascade re-run required.
- *Effort estimate:* ~12-15h (vs. PR-D's ~3h). See
  `plans/CLEANUP-PR-D-DECOMP-THRESHOLD-GATES-PLAN.md` §Option B
  comparison for the full scope analysis preserved during the
  decision gate.

## Closed

### `[example-corpus]` url-shortener corpus regen → all 6 layers PASS (2026-06-10)

- *Resolution:* TRACE-RES-FIXUP-001 (PR #125, merge `90f37002`) + IPLAN-RT-001
  (PR #127, merge `c56c386f`). Cascade scores: PRD 92 / EARS 94 / BDD 91 /
  ADR 96 / SPEC 97 / TDD 90 / IPLAN 100. Post-cascade review (2026-06-11)
  surfaced 9 NEW framework-improvement items, captured above as Open
  entries for FRAMEWORK-CLEANUP-001 triage.

### `[harness]` Cascade harness lacks `--skip-lint-smoke` flag for migration scenarios

- *Context:* TRACE-RES-FIXUP-001 cascade (2026-06-10) needed
  `SDD_LINT_SKIP_TRACE_RES=1` env-var bypass to run against the legacy
  url-shortener corpus before the new contract was applied.
- *Fix shape:* add `--skip-lint-smoke` flag to `tests/scripts/test-acceptance.sh`
  Phase 0 so migration runs can defer lint until after the corpus is
  regenerated. Removes the need for per-rule env-var bypasses.
  *Resolution:* CLEANUP-PR-A (PR #TBD, merge SHA TBD) — first child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-A-HARNESS-LINT-PLAN.md` for impl details.

### `[harness]` Tree-safety check requires `--force` after pre-cleanup; plan templates don't surface this

- *Context:* TRACE-RES-FIXUP-001 first cascade attempt (2026-06-10) aborted
  in 30s at Phase 0 "tree-safety FAIL" because `rm -rf` of legacy artifacts
  created unstaged deletions. Five-pass plan review missed this. Re-run
  with `--force` succeeded.
- *Fix shape:* either (a) document the cleanup-then-`--force` pattern in
  the cascade-rebuild section of plans that touch `examples/<NAME>/`,
  or (b) auto-stage the cleanup in the harness so the safety check sees
  a clean tree.
  *Resolution:* CLEANUP-PR-A (PR #TBD, merge SHA TBD) — first child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-A-HARNESS-LINT-PLAN.md` for impl details.

### `[lint]` `sync-vendored.sh` and `sync-plugin-framework.sh` are two separate sync mechanisms; easy to confuse

- *Context:* TRACE-RES-FIXUP-001 Task 2 (2026-06-10) and earlier
  NECESSARY-UPSTREAM-001 (PR #121): I edited the vendored lint module,
  ran `sync-plugin-framework.sh`, and the edit was overwritten because
  that script syncs `tools/sdd_doc_lint/` → vendored copies (treating
  `tools/` as canonical), not the reverse. The lint module's canonical
  source is `tools/sdd_doc_lint/__init__.py`; the vendored copies under
  `platforms/<name>/sdd_doc_lint/` are byte-identical mirrors.
- *Fix shape:* either (a) consolidate to one sync script that knows the
  direction per directory, or (b) add a top-of-file comment to each
  vendored module declaring "DO NOT EDIT — synced from tools/...". A
  brief CONTRIBUTING.md note next to the existing sync-script docs
  would also help.
  *Resolution:* CLEANUP-PR-A (PR #TBD, merge SHA TBD) — first child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-A-HARNESS-LINT-PLAN.md` for impl details.

### `[skill]` Auditor + fixer SKILLs emit unescaped `|` inside backtick code spans in table cells (MD056)

- *Context:* IPLAN-RT-001 live cascade (2026-06-10) produced
  `examples/url-shortener/.aidoc/audit/08_IPLAN-audit.md:105` and
  `.aidoc/review/08_IPLAN/IPLAN-01/IPLAN-01.F_fix_report_v001.md:50`
  containing rows where a `docker compose ps | grep 'Up'` code span
  inside a table cell has its shell pipe treated by markdownlint as a
  column separator, tripping MD056 (column-count mismatch). Pre-commit
  hook blocked impl commits on cascade output.
- *Fix shape:* update audit + fixer SKILL prompts to escape `|` inside
  code spans within markdown table cells (use `\|` or move the code
  span to a paragraph reference). Until then, `examples/<name>/.aidoc/`
  is excluded from the pre-commit markdownlint hook (workflow-gap fix
  landed in IPLAN-RT-001 commit).
  *Resolution:* CLEANUP-PR-A (PR #TBD, merge SHA TBD) — first child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-A-HARNESS-LINT-PLAN.md` for impl details.

### `[governance]` Iteration cap for the quality loop is implementation-bound, not spec-bound

- *Context:* `REVIEW_REMEDIATION_FLOW.md` defines the quality loop as
  "Draft → Review → (Remediate → Re-review)* → Gate Pass" and states
  *"the loop repeats until the gate passes"* — open-ended. But the cap
  is hard-coded at `tools/saga_driver.py:125` `MAX_ITERATIONS = 3` (and
  default threshold 90). No `ADAPTATION_SURFACE.yaml` knob exposes this;
  the spec gives no guidance on default cap or how to tune it per layer
  / project.
- *Fix shape:* either (a) elevate the iteration cap to spec — declare a
  default in `REVIEW_REMEDIATION_FLOW.md` or `REVIEW_SAGA.md` and expose
  it via `ADAPTATION_SURFACE.yaml` (e.g. `quality_loop.max_iterations:
  3`, tunable per project) — or (b) leave it as a platform implementation
  detail but explicitly document that in the spec so consumers know to
  consult their platform's docs for the cap. Either way, the framework
  shouldn't have a silent implementation-bound cap that the spec is
  unaware of. Discovered while observing the TRACE-RES-FIXUP-001 corpus
  regen cascade (2026-06-10): PRD-01 converged in iter-2 (PASS 92),
  EARS-01 in iter-2 (PASS 94); both ran the loop until gate passed,
  consistent with spec — but the silent 3-iter ceiling means
  near-convergent artifacts (89/90) end up `PARTIAL_TIMEOUT` instead of
  one-more-cycle.
  *Resolution:* CLEANUP-PR-C (PR #TBD, merge SHA TBD) — second child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-C-SPEC-REGISTRY-PLAN.md` for impl details.

### `[registry]` `@threshold:` 3-segment keys vs element-ID 4-segment pattern

- *Context:* `LAYER_REGISTRY.yaml` `id_patterns.element` regex covers
  the 4-segment hash form `TYPE.NN.SS.xxxx`. But threshold keys use a
  3-segment form `PRD.01.perf.redirectp95`. The current `sdd_doc_lint`
  cannot distinguish a legitimate threshold from a malformed 3-segment
  element ID — a hand-edit introducing `PRD.01.perf.typo` would slip
  past validation.
- *Fix shape:* add a `threshold` ID pattern to `LAYER_REGISTRY.yaml`
  `id_patterns:`; extend `sdd_doc_lint` to validate the new namespace.
  Coordinate with the `[gate] Threshold-binding gate` entry above.
  *Resolution:* CLEANUP-PR-C (PR #TBD, merge SHA TBD) — second child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-C-SPEC-REGISTRY-PLAN.md` for impl details.

### `[template]` SPEC + IPLAN declare no layer-local element IDs

- *Context:* url-shortener review (2026-06-11) — `SPEC-01.md` and
  `IPLAN-01.md` carry no `SPEC.NN.SS.xxxx` or `IPLAN.NN.SS.xxxx`
  element IDs (only upstream `@adr`/`@tdd` refs + Protocol method
  names). Templates `SPEC-TEMPLATE.yaml` / `IPLAN-TEMPLATE.yaml` do
  not require any. If a downstream consumer ever needs to cite an
  individual SPEC rule (e.g. "the §5 fail-closed rule") or an
  individual IPLAN step, they have no element ID to bind to.
- *Fix shape:* either (a) require element IDs at SPEC §5 rules and
  IPLAN §4 contracts via template + auditor lens, or (b) document the
  deliberate exemption in `ID_NAMING_STANDARDS.md` so future authors
  know it's intentional.
  *Resolution:* CLEANUP-PR-C (PR #TBD, merge SHA TBD) — second child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-C-SPEC-REGISTRY-PLAN.md` for impl details.

### `[template]` EARS emits per-line `@bdd:` downstream slots — direction-of-flow violation

- *Context:* url-shortener review (2026-06-11) — `EARS-01.md:68, 73, 81 etc.`
  emit per-line `@bdd: BDD-01` slots BEFORE the downstream BDD exists.
  These work as downstream slots but bypass the necessary-upstream
  contract direction (upstream-only).
- *Fix shape:* either (a) drop per-line `@bdd:` slots from EARS and
  rely on BDD's reverse `@ears:` tags for the trace (cleaner direction),
  or (b) declare downstream-slot semantics officially in
  `LAYER_REGISTRY.yaml` so the contract names them.
  *Resolution:* CLEANUP-PR-C (PR #TBD, merge SHA TBD) — second child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-C-SPEC-REGISTRY-PLAN.md` for impl details.

### `[plan-review]` Plan reviews should cross-check claims against the example corpus, not only test fixtures

- *Context:* NECESSARY-UPSTREAM-001 (PR #121) Pass 4 verified
  TRACE-RES-001 against `tools/sdd_doc_lint/fixtures/` but **not**
  against `examples/url-shortener/docs/`. The latter carried 107 orphan
  `@prd:` tags that broke the TDD-RT-001 cascade. The plan's
  "backwards compatibility" claim was wrong because the corpus
  cross-check was missing.
- *Fix shape:* update the plan-review templates / verified-planning
  skill to require, when a plan changes lint rules or @-tag semantics,
  a `python3 -m sdd_doc_lint examples/<NAME>/docs/` smoke run as a
  mandatory Pass-N check. Catches corpus drift before merge.
  *Resolution:* CLEANUP-PR-B (PR #TBD, merge SHA TBD) — third child PR of FRAMEWORK-CLEANUP-001 (heart). See `plans/CLEANUP-PR-B-REVIEW-CALIBRATION-PLAN.md` for impl details.

### `[skill]` doc-tdd auditor C4 inter-section consistency may be over-strict (or the cascade-produced TDD-01 has a real inconsistency)

- *Context:* TDD-RT-001 live cascade (2026-06-09) finished with
  `content_score 89`; one P2 finding cited "§1 line 30 (cumulative
  upstream tags header) vs §3 lines 89-90 and §7 line 206". The §1 line
  was correctly `@ears | @bdd | @adr | @spec` per the new contract;
  inconsistency was elsewhere. Not investigated.
- *Fix shape:* run a focused diagnostic on the TDD-01.md generated by
  PR #122 + decide whether C4 is the right gate or whether the TDD
  author needs to be tighter about section-level tag consistency. May
  result in a small `doc-tdd/SKILL.md` tightening.
  *Resolution:* CLEANUP-PR-B (PR #TBD, merge SHA TBD) — third child PR of FRAMEWORK-CLEANUP-001 (heart). See `plans/CLEANUP-PR-B-REVIEW-CALIBRATION-PLAN.md` for impl details.

### `[plan-review]` 5-pass plan reviews are paying off; consider codifying minimum-pass count by plan-type

- *Context:* TRACE-RES-FIXUP-001 plan took 5 passes to converge
  (Pass 4 caught a silent-no-op `rm -rf .aidoc/saga/` that would have
  wasted a 6-9 hour cascade). NECESSARY-UPSTREAM-001 took 4 passes;
  TDD-RT-001 took 2; the 8-skill rollout plans typically took 2-3.
- *Fix shape:* not urgent, but worth noting in the verified-planning
  skill: framework-level / cross-cutting plans seem to need 4-5 cycles
  in practice; per-layer rollout plans converge in 2. CLAUDE.md's
  "minimum 2" floor is correct; an advisory upper-bound by plan-type
  would help future estimation.
  *Resolution:* CLEANUP-PR-B (PR #TBD, merge SHA TBD) — third child PR of FRAMEWORK-CLEANUP-001 (heart). See `plans/CLEANUP-PR-B-REVIEW-CALIBRATION-PLAN.md` for impl details.

### `[playbook]` `auditor` + `tech_lead` lens calibration — convergence theater

- *Context:* url-shortener cascade audit trail (2026-06-11) — `auditor`
  lens scored **100 on 4 of 5 cascaded layers** where it ran; `tech_lead`
  scored **100 on 3 of 4** even when `chaos`+`security_engineer` found
  multiple P2/P3 issues in the same sections. The synthesizer's weighted
  mean still surfaces real findings (verdicts 91-97 honest), but 2 of 6
  lenses are giving blank checks. IPLAN-01 scored 100 with 5/6 lenses
  returning zero findings — the strongest convergence-theater signal.
- *Fix shape:* refresh `framework/playbooks/<layer>/auditor.md` and
  `tech_lead.md` for each layer with more falsifiable checks. Specifically
  require tech_lead to cross-check the sections security/chaos flagged.
  Add a "no-lens-scores-100-without-falsifiable-evidence" guard to the
  synthesizer.
  *Resolution:* CLEANUP-PR-B (PR #TBD, merge SHA TBD) — third child PR of FRAMEWORK-CLEANUP-001 (heart). See `plans/CLEANUP-PR-B-REVIEW-CALIBRATION-PLAN.md` for impl details.

### `[skill]` `doc-*-audit` must strip author's self-claimed scores before lens fan-out

- *Context:* url-shortener cascade audit trail (2026-06-11) —
  `02_PRD/PRD-01/verdict.json:AUD-002` flagged that the author's
  `ears_ready_score: 92` self-claim survived into the artifact body
  the lenses see. The synthesizer's final score was **also 92**.
  Coincidence, or anchor-effect from lenses reading the author's claim?
  Either way, the framework should not let author self-assessment leak
  into the review surface.
- *Fix shape:* `doc-*-audit/SKILL.md` step that prepares the lens brief
  must strip fields like `ears_ready_score`, `prd_score`, etc. from the
  artifact text before passing to each lens subagent. Document the
  stripped-field list in `REVIEW_TEAM.md` §Operations.
  *Resolution:* CLEANUP-PR-B (PR #TBD, merge SHA TBD) — third child PR of FRAMEWORK-CLEANUP-001 (heart). See `plans/CLEANUP-PR-B-REVIEW-CALIBRATION-PLAN.md` for impl details.

### `[saga]` Saga lifecycle — no `fixer_introduced_finding` tag

- *Context:* `examples/url-shortener/.aidoc/review/04_BDD/BDD-01/saga.json`
  shows iter-2 fixer rewrote scenario `.9b90`; iter-3 audit found the
  rewrite introduced **two new P2s** at the same location (compound
  `When` + unbounded timeout). The framework has no way to flag findings
  that the fixer itself caused — they appear as "new findings" with no
  link to the change set.
- *Fix shape:* extend `REVIEW_SAGA.md` schema with a
  `fixer_introduced_finding` tag on iter-N findings whose location
  matches a iter-(N-1) "Fixes Applied" table row. Surface in the audit
  report under `## Regressions` (new section in audit report format).
  *Resolution:* CLEANUP-PR-B (PR #TBD, merge SHA TBD) — third child PR of FRAMEWORK-CLEANUP-001 (heart). See `plans/CLEANUP-PR-B-REVIEW-CALIBRATION-PLAN.md` for impl details.

### `[template]` IPLAN sub-types: code-build vs deploy

- *Context:* url-shortener review (2026-06-11) — IPLAN-01 covers Red/Green/
  Refactor with pytest gates but has **no canary, no smoke endpoint, no
  observability dashboard, no rollback procedure** (§5 explicitly defers
  runbook/dashboard to "first to-production session"). It scored 100, but
  it's a code-build plan, not a deploy plan. The crew (operator + chaos
  - integration_lead lenses) is calibrated for deploy concerns; if the
  artifact silently scopes out those concerns, the crew can't catch it.
- *Fix shape:* `IPLAN-TEMPLATE.yaml` gains a `subtype` field with values
  `code_build` | `deploy` | `combined`. Deploy IPLANs are gated on
  rollback/smoke/observability sections; code-build IPLANs are exempt.
  Audit dispatch selects the section set by subtype.
  *Resolution:* CLEANUP-PR-E (PR #TBD, merge SHA TBD) — fourth child PR. See `plans/CLEANUP-PR-E-IPLAN-SUBTYPES-PLAN.md`.

### `[gate]` Component-decomposition gate missing between PRD and ADR

- *Context:* url-shortener review (2026-06-11) — BRD/PRD scoped the **whole
  service** (shorten + redirect + counter + abuse screening); ADR-01 onward
  silently narrowed to **one component** (Mapping Store). ADR §10 mentions
  "five sibling ADRs as future work" but no scope-contraction artifact
  records the decision. Downstream layers (SPEC/TDD/IPLAN) implement only
  the Mapping Store, not the URL shortener.
- *Fix shape:* introduce a `which-containers-from-PRD-§9-get-ADRs-this-cycle`
  artifact (a CHG-like decision record) at the PRD↔ADR boundary. ADR
  authoring SKILL must reference it; auditor must verify scope matches.
  Without it, downstream layers silently shrink scope unobserved.
  *Resolution:* CLEANUP-PR-D (PR #TBD, merge SHA TBD) — fifth and final child PR. Option A chosen; Option B deferred to item #19.

### `[gate]` Threshold-binding gate missing before BDD/TDD PASS

- *Context:* url-shortener review (2026-06-11) — 7 of 11 threshold keys
  in PRD-01 are placeholders (`screeningdeadline`, `countstaleness`,
  `codespacecapacity`, `takedownsla`, `codeentropy`, `resolutionpersource`,
  `resolutionwindow`) with no numeric values bound. BDD scenarios cite
  `WITHIN @threshold:PRD.01.perf.screeningdeadline` and TDD test cases
  cite them too — neither is testable, both passed audit.
- *Fix shape:* extend `sdd_doc_lint` with a `THRESHOLD-RES-001` rule
  (mirror of TRACE-RES-001 for threshold keys): every `@threshold:KEY`
  citation must resolve to a numeric-bound value in the host doc.
  Unbound thresholds fire P1 at BDD/TDD audit.
  *Resolution:* CLEANUP-PR-D (PR #TBD, merge SHA TBD) — fifth and final child PR. Option A chosen; Option B deferred to item #19.

### `[governance]` Doc-number independence across layers not codified anywhere

- *Context:* User clarification (2026-06-11) — document numbers (the
  `NN` in `BRD-01` / `PRD-01` / `EARS-01` / ...) are **per-layer
  sequential and independent**; one BRD MAY drive multiple downstream
  PRDs (PRD-01, PRD-02, ...), one PRD MAY cite multiple BRD upstream
  docs. Framework currently has zero explicit mention of this:
  `ID_NAMING_STANDARDS.md` says *"sequential two-digit number"* (per
  layer, but doesn't say independent across); `TRACEABILITY.md` has
  no cross-layer cardinality discussion; `REVIEW_TEAM.md` +
  `REVIEW_REMEDIATION_FLOW.md` are silent on cardinality. The
  url-shortener example's 1:1 numbering alignment (BRD-01 → PRD-01 →
  ... → IPLAN-01) reinforces the wrong "numbers line up" mental model.
- *Fix shape:* (a) add "Cross-layer cardinality" subsection to
  `ID_NAMING_STANDARDS.md` (or `TRACEABILITY.md`) explicitly stating
  doc numbers are per-layer independent + one-to-many + many-to-one
  both supported; (b) update `doc-<layer>` author SKILL prompts:
  *"the upstream's number is NOT your number — pick next-free in
  YOUR layer's index"*; (c) auditor playbooks: clarify orphan-looking
  downstream docs may be siblings of the same upstream, not actual
  orphans. **Deferred to a follow-up CLEANUP-PR-F (single-item)** —
  cataloged here per Tier-2 pipeline (FRAMEWORK-FEEDBACK-LOG-001
  Principle 9); impl waits until after current cleanup PRs settle.
  *Resolution:* CLEANUP-PR-F (PR #TBD, merge SHA TBD) — single-item follow-up after FRAMEWORK-CLEANUP-001 workstream closed; codified per-layer cardinality independence in ID_NAMING_STANDARDS.md.
