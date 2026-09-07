# FRWK-REVIEW-002 Plan — fix the 2026-07-09 plugin + core-docs review findings

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | FRWK-REVIEW-002                             |
| Type           | bugfix                                      |
| Status         | PLANNED — 2026-07-09T19:41:54Z              |
| Depends on     | 2026-07-09 five-agent review (findings embedded below; working copy at `tmp/REVIEW-2026-07-09_plugin-core-docs.md` — transient, this plan is self-contained) |
| Feeds          | SKILL-DEDUP-001 (follow-up plan: template-generation of the 36 per-layer skills); Hermes-parity arc (PR-D gives it a machine-readable rule catalog + realizing map) |
| Version impact | plugin PATCH ×2 (PR-A, PR-B); framework PATCH (PR-C → 0.35.2); framework MINOR (PR-D → 0.36.0); PR-E0 decision (framework PATCH — records GD-NN) + PR-E1–E4 founder-gated (framework PATCH each); PR-F/PR-G none |

## Objective

Resolve the 46 findings (7 high / 23 medium / 16 low) from the 2026-07-09
plugin + core-documentation review: copy-paste drift inside the 36 per-layer
skills (wrong audit-report paths, a dead governance citation, uneven
`review_mode` adaptation), a phantom tool reference, contradictions inside the
spec's adaptation/threshold/ID-naming contracts, the BDD layer README still
teaching the pre-YAML-BDD trace form, spec-normative content that exists only
in lint code, and a set of stale docs-of-record — including a sync-script
defect that actively corrupts historical version-in-prose lines. Work lands as
seven tier-scoped PRs; every framework/ edit re-runs the vendored-bundle sync
and the conformance suite.

## Scope

**In:** 43 of the 46 findings (H1–H7, M1–M23, L1–L13), grouped into PR-A…PR-G
below. Each fix is an edit to an existing surface (skills, governance docs,
docs of record, two small script changes) plus two additive spec artifacts
(rule catalog, realizing-layers registry block) whose absence was itself a
finding. Plus **L14** (folded into PR-C as C17). The remaining two low findings
are handled in Out-of-scope, named rather than dropped.

**Out of scope (deferred):**

- **L16** (quality-advisor re-implements the audits' Structural-Checklist
  checks with no shared source — a drift *seed*, not a live drift). Belongs to
  the shared-reference refactor, not a text patch → **SKILL-DEDUP-001**.
- **L15** (the two deprecated stubs `doc-review` / `trace-check`). The review
  itself concluded no action needed before v1.0.0; recorded here as
  **accepted / no-op** so it is not silently dropped. Removal happens at the
  v1.0.0 milestone, not in this plan.
- **Structural de-duplication of the 36 per-layer skills** (≈7,800 duplicated
  lines; generate SKILL.md families from templates). Own plan: SKILL-DEDUP-001.
  This plan fixes the *drift instances*, not the duplication *class*. A1's
  backports enlarge several audit files SKILL-DEDUP-001 will later regenerate;
  the corrected text becomes that plan's template baseline.
- Cutting the missing release tags (tracked in `plans/HANDOFF.md` backlog);
  PR-F only makes `docs/TAGGING.md` stop claiming uncut tags exist.
- Building the `bdd_to_gherkin.py` emitter (D-4 deliverable) — PR-A only makes
  `doc-bdd` stop claiming it exists. Building it is a feature, not a fix.
- Anything Hermes (`platforms/hermes/`), per review scope.
- Unifying the fixer checkpoint pipelines (multi-lens vs post-synthesizer) —
  PR-C *documents* the two placements in `REVIEW_REMEDIATION_FLOW.md`;
  changing either pipeline is out of scope.
- Wiring `--threshold` into `saga_driver.py` gating — the flag is removed
  instead (the real gate is the `audit_threshold` knob, raise-only).

## Approach

Seven PRs, ordered by tier and independence. Plugin PRs (A, B) and
docs-of-record PRs (F, G) are independent of the spec PRs (C → D → E,
sequential). Tier discipline:

- **Spec-tier PRs (C, D, E)** touch `framework/**` → GATE-SPEC applies, **no
  auto-merge** (excluded by the ai-review `tier=spec` check), each bumps
  `framework/VERSION` (pre-commit sync hook propagates the pin + 52
  frontmatters), and each re-runs `tools/sync-plugin-framework.sh` so the
  vendored bundle stays byte-identical (CI drift guard).
- **PR-E is founder-gated**: it needs a policy decision (GD-NN) on the
  engine-agnosticism boundary before edits are judged.
- **PR-G touches CLAUDE.md** → governance PR: ≤3 doc surfaces (it touches 1),
  adversarial self-review before push (OPS-0061 Rule 2).
- Multi-agent author-side review per OPS-0065/0067 before each push.

### PR-A — plugin: skill-content drift + phantom reference (plugin PATCH)

| # | Fix | Findings | Files |
|---|-----|----------|-------|
| A1 | Replace the **versioned** legacy audit-report filename `<TYPE>-NN.A_audit_report_vNNN.md` with the **fixed** relocated form `.aidoc/audit/<NN>_<LAYER>-audit.md` at **all 68 instructional sites** (grep-verified count 2026-07-09): the Execution-Contract write-step of the **8 audits** that still carry it (all but brd — brd's EC step already relocated), plus the Downstream / report-cleanup-glob / "Output:" / fixer-handoff sites in **all 9 audits** (brd included — it retains the token at :32, :44, :578), plus the Upstream / consume / team-mode-read sites in **all 9 fixers** (1–3 sites each). Because the relocated form is a single fixed file, **not** a `vNNN` series, also reword the version-series semantics: the `…_v*.md` cleanup glob, "delete superseded", and "consume the latest" become "the single relocated audit-report file". Reword any surviving "legacy shape, relocated" note so it does **not** contain the `_audit_report_v` token (so the zero-token verification is achievable). | H1a | all 9 `skills/doc-*-audit/SKILL.md` + all 9 `skills/doc-*-fixer/SKILL.md` |
| A2 | Iteration-cap paragraph: correct the citation in the 2 audits that have it (`REVIEW_SAGA.md §"Iteration cap"` → `REVIEW_REMEDIATION_FLOW.md §Iteration cap`) and backport the corrected paragraph to the 7 audits missing it (engine-wide behavior). | H1b | `skills/doc-iplan-audit/SKILL.md:343`, `skills/doc-chg-audit/SKILL.md:388`, + 7 sibling audits' `## Break-circuit policy` |
| A3 | `review_mode` consistency: add `review_mode` to the `adapts:` frontmatter list of the 3 audits missing it (prd, ears, bdd — all 9 already resolve it in the body); add the short `## Adaptation` paragraph documenting the key (iplan/chg wording) to the 7 audits missing it. | H1c | `skills/doc-{prd,ears,bdd}-audit/SKILL.md:18`, 7 audits' `## Adaptation` |
| A4 | `doc-bdd` phantom emitter: reword — the `.feature` emitter is a designed-but-unshipped deliverable (YAML-BDD plan D-4); the shipped tool is the reverse-direction one-off `tools/gherkin_to_bdd_yaml.py`. New wording must not claim a `tools/bdd_to_gherkin.py` file exists. | H2 | `skills/doc-bdd/SKILL.md:29` |
| A5 | Propagate the `gate_ready` verdict clarifier from `doc-chg-audit`'s Saga-interaction section to the other 8 audits. The chg wording is CHG-specific ("For CHG, `combined_status` and `gate_ready`…") — reword per layer to the generic verdict semantics (`gate_ready: true` ⇒ proceed to gate-check; `false` ⇒ dispatch fixer). | H1d | 8 audits' `## Saga interaction` |
| A6 | Sharpen creator vs autopilot frontmatter descriptions ×9: creator gains "single-document entry point, normally invoked by the autopilot's saga loop"; autopilot keeps "end-to-end / batch". | M17 | `skills/doc-<layer>/SKILL.md` + `skills/doc-<layer>-autopilot/SKILL.md` descriptions |
| A7 | Cheap wording normalization while touching the files: MANDATORY-blockquote parity across the 9 autopilots; re-wrap the iplan/chg saga sections to the common line breaks; drop the ears-only generic example in the MD056 block. | L3, L13 | autopilot + fixer SKILL.md files above |

### PR-B — plugin: mechanics (plugin PATCH)

| # | Fix | Findings | Files |
|---|-----|----------|-------|
| B1 | Remove the dead `--threshold` flag: delete the argparse arg, the `SagaContext.threshold` field, and the pass-through; drop `--threshold 90` from the 8 layer autopilots' command blocks. PASS/FAIL stays verdict-driven (`combined_status`); the real knob is `audit_threshold` (raise-only). No conformance test references the flag (verified). | M13 | `tools/saga_driver.py:200,644,669`, 8 autopilot SKILL.md command blocks |
| B2 | Extend the advisory hook's artifact case-arm with `CHG` so writes under `docs/09_CHG/` nudge `doc-chg-audit`. | L1 | `hooks/sdd-doc-review.sh:29` |
| B3 | Wire `/aidoc-flow:save-plan` to the documented config: read `work_plans_dir` from `.claude/aidoc-flow.config.yaml` first, fall back to the legacy `.claude/CLAUDE.md` line (CONFIG.md's stated contract); modernize the stale example/timestamp text. | M14 | `commands/save-plan.md`, cross-check `docs/CONFIG.md:49-52,161-165` |
| B4 | Plugin CHANGELOG structure: promote 0.23.0 / 0.23.1 / 0.23.2 from `###` under `## [Unreleased]` to top-level `##` released sections (matching 0.22.0 and earlier); `[Unreleased]` becomes empty. | M15 | `platforms/claude-code-plugin/CHANGELOG.md:15-89` |
| B5 | `plugin.json` keywords: add `"spec"`, `"tdd"` (completes the 8 layers). | L2 | `.claude-plugin/plugin.json:13` |
| B6 | Document the CHG model-precheck exclusion where it's visible: one sentence in `doc-chg-autopilot` (CHG is a governance overlay, not a layer; no `model.per_layer.CHG` recommendation exists; the conformance test intentionally asserts 8). | M16 | `skills/doc-chg-autopilot/SKILL.md` |

### PR-C — spec: normative-text corrections (framework PATCH)

Every C-item also re-runs `tools/sync-plugin-framework.sh` (vendored bundle).

| # | Fix | Findings | Files |
|---|-----|----------|-------|
| C1 | Rewrite BDD README upstream-traceability section to the YAML-BDD contract: structured `scenarios:`/`ears:` list per scenario (TAG_SYNTAX's stated exception), correct `@ears` target layer to Layer 3, replace the raw-Gherkin quick-reference block with the `scenarios:` YAML form. | H3 | `framework/layers/04_BDD/README.md:36-67` |
| C2 | Fix `BDD-TEMPLATE.yaml` internal contradiction: drop the "Gherkin tag format (NO spaces after colon)" guidance block (pre-D-0038); keep the one-space `"@ears: EARS.NN.03.xxxx"` form used elsewhere in the file. | H3 | `framework/layers/04_BDD/BDD-TEMPLATE.yaml:293-296,305` |
| C3 | Adaptation reconciliation: ADAPTATION.md §4 documents all **6** knobs (add `review_mode`, `quality_loop_max_iterations` rationale sections; retitle "v1 — four knobs"); fix the `# Knobs (5)` comment and the `id_format … §8` pointer (→ §9) in the surface file; fix the dotted `quality_loop.max_iterations` → flat `quality_loop_max_iterations` in REVIEW_REMEDIATION_FLOW. | H4 | `framework/governance/ADAPTATION.md:72ff`, `ADAPTATION_SURFACE.yaml:33`, `REVIEW_REMEDIATION_FLOW.md:49,53` |
| C4 | Add the missing `ADR → SPEC-Ready (>=90) → SPEC` gate to the two 7-gate tables (guide + ADR README already have it). | M1 | `framework/QUICK_REFERENCE.md:36-46`, `framework/governance/TRACEABILITY.md:109-117` |
| C5 | COV02 wording: "realized by a downstream SPEC/TDD" → "realized by a doc in its realizing set (EARS → BDD/SPEC/TDD; BDD → SPEC/TDD)" — matches the SPEC-00 template prose and the implementation. Add a cross-link between the COV01 doc-level (TRACEABILITY) and element-level (SPEC-00 template) halves. | M3, L8 | `framework/governance/TRACEABILITY.md:54-59`, `framework/layers/06_SPEC/SPEC-00_index.TEMPLATE.md:78-87` |
| C6 | Threshold-key reconciliation (registry wins): relax §2.1 to the registry regex's 2-segment minimum (`{category}.{attribute}` allowed, subcategory optional) OR tighten registry+examples to 3 — **default: relax prose to registry**, since `LAYER_REGISTRY.yaml` is declared authoritative and shipped examples are 2-segment. Clarify NR-02 that underscores are allowed *within* a segment (`p95_latency`). Fix the SPEC-hosted example at :170 to an ADR-hosted one (source docs are BRD/PRD/ADR per the doc's own list). | M5 | `framework/governance/THRESHOLD_NAMING_RULES.md:187-193,719,170`, `framework/governance/ID_NAMING_STANDARDS.md:207` |
| C7 | ID-format lockstep (registry wins): ID_NAMING_STANDARDS "two-digit number" → "two-or-more digits (registry: `^[A-Z]+-\d{2,}$`)"; update REVIEW_SAGA's "(2-digit NN)… must change in lockstep" note accordingly. | M6 | `framework/governance/ID_NAMING_STANDARDS.md:5`, `framework/governance/REVIEW_SAGA.md:71`, `framework/registry/LAYER_REGISTRY.yaml:215` (unchanged, cited) |
| C8 | File-naming table: IPLAN also carries a slug (`IPLAN-NN_{slug}.yaml`). | M7 | `framework/governance/ID_NAMING_STANDARDS.md:252` |
| C9 | BRD README rehash phrasing: "Not verified end-to-end until `rehash --check` (PROVISIONAL-IDS-002)" → shipped-Phase-1 wording ("verifiable on demand via `rehash --check`, advisory `IDDRIFT01`; BRD §7 boundary only — other layers Phase 2+"). Keep the sibling-layer READEs' sentences accurate for their (still-unextracted) layers with the same clarification. **Constraint: stay inside the D-0061/D-0062 "verifiable on demand, not verified" scoping — do not imply hash-verified IDs.** | M8 | `framework/layers/01_BRD/README.md:95,102` (+ same sentence in PRD/EARS/BDD/ADR READMEs) |
| C10 | REVIEW_TEAM frontmatter example: `framework_spec_version: "0.14.0"` → placeholder `"<framework/VERSION>"` and drop the false "auto-propagated by sync hook" claim from the example comment (the hook does not touch this doc). | M10 | `framework/governance/REVIEW_TEAM.md:260` |
| C11 | AIDOC.md profile semantics: align to PROFILE-TEMPLATE.yaml (bootstrap from PROFILE-TEMPLATE, crews/weights not project-overridable; profile = knob overrides). The `claude -p` neutralization (F3) and plugin-skill table (F4) are engine-agnosticism edits → deferred to PR-E2 (founder-gated), not done here. | M9 | `framework/docs/AIDOC.md:45-59` |
| C12 | FEEDBACK_LOG: fix the mislabeled/dead link (`AIDOC.md` text → actual target; anchor `#examples` doesn't exist in framework/README — point at `framework/docs/AIDOC.md` directly); define the two `feedback_*` identifiers inline or reword to plain references. | M11 | `framework/governance/FRAMEWORK_FEEDBACK_LOG.md:9,10,41` |
| C13 | Residual "Gherkin" mentions post-YAML-BDD → "BDD scenarios (YAML)". | L4 | `framework/governance/TRACEABILITY.md:114`, `REVIEW_CREWS.yaml:64`, `DIAGRAM_STANDARDS.md:118` |
| C14 | Governance README index: add REVIEW_SAGA.md (+ saga.schema.json), FRAMEWORK_FEEDBACK_LOG.md, PROFILE-TEMPLATE.yaml rows. Framework README layout: add `templates/`, `layers/08_IPLAN/IPLAN-ECOSYSTEM.md`; note 9 playbook folders (8 layers + 09_CHG overlay). | L5, L6 | `framework/governance/README.md`, `framework/README.md:52-79` |
| C15 | Tag-table typo: `@spec: SPEC.NN` → `@spec: SPEC-NN` (document form). | L7 | `framework/governance/ID_NAMING_STANDARDS.md:204` |
| C16 | Document the fixer checkpoint placements: short REVIEW_REMEDIATION_FLOW paragraph naming both pipelines (multi-lens validation dispatches vs post-patch/pre-synthesizer) and which layer family uses which, so the canon exists outside skill copies. | H1e | `framework/governance/REVIEW_REMEDIATION_FLOW.md` |
| C17 | REVIEW_TEAM.md files PRD's 8:7 chaos/security split under an "Equal split" label — relabel to reflect the actual (self-consistent with REVIEW_CREWS.yaml) weighting. | L14 | `framework/governance/REVIEW_TEAM.md:204` |

### PR-D — spec: completeness additions (framework MINOR)

| # | Fix | Findings | Files |
|---|-----|----------|-------|
| D1 | Realizing-layers map into the spec: add a machine-readable `realizing_layers` block to `framework/registry/LAYER_REGISTRY.yaml` (BRD→PRD; EARS→BDD/SPEC/TDD; BDD→SPEC/TDD — mirror of the code constant) + a normative TRACEABILITY.md subsection referencing it. New conformance test: lint's `REALIZING_LAYERS` == registry block. (Registry loader is tolerant — `yaml.safe_load` + `assertIn` in `test_registry.py` — so the new key adds no regression.) | M2 | `framework/registry/LAYER_REGISTRY.yaml`, `framework/governance/TRACEABILITY.md`, `tests/conformance/` (new test), `tools/sdd_doc_lint/__init__.py:1933` (unchanged, guarded) |
| D2 | Lint-rule catalog: new `framework/governance/LINT_RULES.md` — one row per emitted rule ID (the 25 enumerated from code 2026-07-09: COV01-03, CSC01, DG02, EARS01, FM01, HASH01, ID01-03, IDDRIFT01, PH01, PROV01, REFGRAN01, REUSE01/02, STALE01, STRUCT01, STY01-03, TAG01, TH01/02; re-enumerate at implementation), each with one-paragraph semantics, severity tier, and defining-doc cross-ref where one exists. New conformance test: every rule ID the lint can emit appears in the catalog. Add catalog to governance README index. **Must also add `governance/LINT_RULES.md` to `EXPECTED_FILES` in `tests/conformance/test_governance.py`** — the `test_no_unexpected_files` / `test_no_orphan_governance_files` pair (:67-70,111-120) asserts `found == set(EXPECTED_FILES)` and fails on any un-registered governance file. | M4 | `framework/governance/LINT_RULES.md` (new), `tests/conformance/test_governance.py` (EXPECTED_FILES edit), `tests/conformance/` (new catalog-coverage test), `framework/governance/README.md` |

### PR-E — spec: engine-agnosticism sweep (founder-gated; split into a decision PR + scoped edit PRs)

**Blocked on a founder policy decision.** This work touches
`framework/governance/DECISIONS.md`, so per CLAUDE.md "Governance PR discipline"
it is a **governance PR** and is bound by Rule 1 (≤3 doc surfaces per PR) and
Rule 2 (adversarial self-review before push). The engine-agnosticism sweep
spans ~10 surfaces, so it **cannot** ship as one PR — it splits into a
decision-first sequence, exactly the pattern Rule 1 prescribes
("DECISIONS first → plan citing it → propagation"):

- **PR-E0 (decision only, 1 surface):** record **GD-NN** in
  `framework/governance/DECISIONS.md` — what counts as an engine-specific token
  in `framework/`, and which references are accepted documented exceptions
  (the way D-0022 excepts the vendored bundle from D-0013). Founder ratifies
  (GATE-SPEC). If the founder rejects or defers, the remaining E-PRs are
  dropped and their findings are logged as accepted exceptions in that same
  GD-NN entry. **No auto-merge (spec + governance tier).**
- **PR-E1 … PR-E4 (scoped edits, ≤3 surfaces each, each citing GD-NN):**

| PR | Fix | Findings | Files (≤3) |
|----|-----|----------|-----------|
| E1 | Playbook frontmatter contract: define `agent:` as an engine-defined executor identifier ("the engine maps lens → executor; see the platform's own docs") and remove the `platforms/claude-code-plugin/...` pointer (REVIEW_TEAM :143, :259, :283, :287); replace "SKILL"/`doc-*` plugin vocabulary with engine-neutral terms in the two other governance/layer surfaces. | H5 (incl. F4) | `framework/governance/REVIEW_TEAM.md`, `AUTHORING_STYLE.md:89`, `layers/08_IPLAN/IPLAN-TEMPLATE.yaml:58` (3) |
| E2 | ID_NAMING plugin-generator vocabulary → engine-neutral; AIDOC.md plugin-skill table → marked an explicit Platform-B illustration (or moved to plugin docs), and its `claude -p` line made engine-neutral. | H5 (F4) | `framework/governance/ID_NAMING_STANDARDS.md:67,78`, `framework/docs/AIDOC.md:75,93-102` (2) |
| E3 | Move the workspace-CI section (pins `aidoc-flow-ci@ci/v1.6.0`, OPS-refs) from REVIEW_REMEDIATION_FLOW to CONTRIBUTING.md (repo tier), leaving a one-line pointer. | H5 (F5) | `framework/governance/REVIEW_REMEDIATION_FLOW.md:172-214`, `CONTRIBUTING.md` (2) |
| E4 | Spec references to repo-root tools (`tools/trace_walk.py`, `tools/sdd_coverage.py`): describe the *capability* normatively and mark the tool path "reference implementation (outside the spec)". | M12 | `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md:28`, `TRACEABILITY.md:14,31-33`, `layers/06_SPEC/SPEC-00_index.TEMPLATE.md:88` (3) |

Each edit PR: spec-tier + governance-tier → **no auto-merge**, adversarial
self-review before push, founder merges. (`REVIEW_TEAM.md:287` — the
tools-reference in E4's scope — is edited in E1's REVIEW_TEAM surface to avoid
a second PR touching the same file; E4 covers the remaining three tool-ref
surfaces.)

### PR-F — docs of record: currency restoration + sync-corruption fix (no version bump)

| # | Fix | Findings | Files |
|---|-----|----------|-------|
| F1 | Restore the two corrupted PARITY provenance lines to their authored value (`0.13.0`) and make them sweep-proof. The sync sed matches only the exact literal ``framework spec `X.Y.Z` `` (verified: `scripts/sync-version-refs.sh:181-193` has no `framework/vX` pattern), so rephrase the provenance so it does **not** contain that literal — e.g. "introduced by SAGA-PARITY-001 (D-0031) in the **0.13.0 spec cycle**". Do **not** cite `framework/v0.13.0` as a tag — that tag was never cut (`git tag -l` verified 2026-07-09); a tag citation here would reintroduce the very "claims an uncut tag" defect F3/F4 remove. Add a comment in `sync-version-refs.sh` documenting the hazard: the global sed rewrites historical prose that matches the literal; historical version mentions must avoid it. Close the related FRAMEWORK-TODO entry (which restored them to the wrong value). | H7 | `docs/PARITY.md:26,207`, `scripts/sync-version-refs.sh:181-193`, `plans/FRAMEWORK-TODO.md:151-156` |
| F2 | DESC.md: refresh the three stale claims (hermes 0.7.3, plugin 0.23.2, spec 0.35.1) and either add DESC.md to the sync script's coverage or stamp it "snapshot as of <date>" — **default: add to sync coverage** (it quotes current-state versions). | H6 | `DESC.md:292,293,312`, `scripts/sync-version-refs.sh` |
| F3 | TAGGING.md: correct the "Current tags" table to tags that exist (verified: plugin ≤ v0.20.1, framework ≤ v0.21.0, hermes ≤ v0.1.1, project ≤ v1.1.0); move never-cut rows to a clearly-labelled "planned / backlog (not yet cut)" subsection; add the missing `hermes/v0.1.1` row; delete the obsolete local-only footnote (all five early tags are on the remote). | M19, L12 | `docs/TAGGING.md:107-149,162-172` |
| F4 | README "Release" column: label uncut versions as VERSION-file state, not release tags (or point at the planned-tags subsection). | M19 | `README.md:292-293` |
| F5 | ROADMAP: backfill "Recently shipped" (coverage engine 0.24–0.27, YAML-BDD 0.28–0.29, provisional-IDs/reuse D-0040/41, GD-05 0.33.0, COV03 0.34.0, GD-02..05 0.34.2, PROVISIONAL-IDS-002 Phase 1 0.35.0); move the Phase-1 bullet out of "Now"; fix the stale `framework 0.35.0` current-state reference. | M20, M21 | `ROADMAP.md:34,41-44,95-166` |
| F6 | Stale current-state versions: SECURITY.md supported row → `0.35.x`; HANDOFF banner → 0.35.1. | M21 | `SECURITY.md:11`, `plans/HANDOFF.md:6,11` |
| F7 | Dead section name: "Post-v1.0 — Shipped" → "Recently shipped" in the CONTRIBUTING doc-matrix and the reminder hook. | M22 | `CONTRIBUTING.md:50`, `scripts/check-docs-updated.sh:17,93` |
| F8 | conformance README refresh: platform half is implemented (17 modules) and green; update the "What is checked" table and the governance-file count. | M18 | `tests/conformance/README.md:13ff` |
| F9 | REPO_STRUCTURE: complete the workflows list (13) and add docs/SUPPORT.md to the tree. | L9 | `docs/REPO_STRUCTURE.md:31,34-39` |
| F10 | HERMES-BACKLOG "Last update" → actual last-edit date. | M23 | `plans/HERMES-BACKLOG.md:7` |

### PR-G — governance: CLAUDE.md fixes (governance PR, 1 surface)

| # | Fix | Findings | Files |
|---|-----|----------|-------|
| G1 | Fix the CONTRIBUTING anchor (em-dash heading → double-hyphen GitHub slug `#documentation-discipline--update-docs-of-record-per-pr`). | L10 | `CLAUDE.md:58` |
| G2 | Update stale descriptions: ROADMAP is a Now/Next/Later post-cutover roadmap (not "Phase 0 → cutover"); `plans/` is the active planning surface (was "the migration record"). While editing the adjacent governance table, fix the stale "Plans" row `PLAN-NNN-<slug>.md` → the convention this dir actually uses (`<NAME>-PLAN.md`). | L11, minor | `CLAUDE.md` "Where things are" + per-repo governance table |

## Implementation sequence

1. **PR-A** → 2. **PR-B** (plugin stream; each: edit → conformance +
   `plm_lint --all` → plugin VERSION PATCH bump → CHANGELOG → push → merge on
   green per OPS-0062).
2. **PR-F** → 3. **PR-G** (docs stream, parallel to plugin stream; PR-G after
   PR-F so the CONTRIBUTING matrix rename lands before CLAUDE.md links are
   re-verified; PR-G gets adversarial self-review per governance Rule 2 and is
   **not** auto-merged).
3. **PR-C** → 4. **PR-D** (spec stream; each: edit `framework/**` → bump
   `framework/VERSION` (C: PATCH → 0.35.2; D: MINOR → 0.36.0) → pre-commit
   sync hook propagates pin/frontmatters → `tools/sync-plugin-framework.sh` →
   conformance → corpus cross-check → CHANGELOG/ROADMAP → push; **spec tier:
   no auto-merge**, founder merges or explicitly OKs).
4. **PR-E0** (decision only) last, after PR-C/PR-D land; then **PR-E1→E4**
   scoped edits, each citing the ratified GD-NN, in order. If the founder
   rejects or defers GD-NN, E1–E4 are dropped and their findings recorded as
   accepted exceptions in the GD-NN entry.

**Note on PR-C/PR-D and CLAUDE.md:** each spec-tier PR mechanically edits
CLAUDE.md's framework-spec pin via the pre-commit sync hook. That is the
documented mechanical-sync exception, not an authored governance edit —
CLAUDE.md's governance-PR trigger targets *authored* changes; repo precedent
(every prior spec bump) treats the hook's pin rewrite as exempt. Called out
here to preempt the objection; no manual CLAUDE.md edit is in PR-C/PR-D scope.

## Verification

Per PR, before push:

- `python3 -m unittest discover -s tests/conformance` — 188+ tests green
  (D adds 2 new tests + the `EXPECTED_FILES` edit; count grows).
- `python3 tests/conformance/platforms/plm_lint.py --all` — clean (plugin PRs).
- **Corpus cross-check** (mandatory for PR-C/PR-D since they touch governance
  text adjacent to lint semantics): `PYTHONPATH=tools python3 -m sdd_doc_lint
  examples/url-shortener/docs/` — findings must match the known baseline (the
  example corpus is regenerated wholesale after framework changes; the check is
  for drift between plan claims and corpus reality, not for corpus
  remediation). Baseline as of 2026-07-09: 1 TH-RES-001 error + STY02 / COV02 /
  REFGRAN01 warnings.
- PR-B: `python3 platforms/claude-code-plugin/tools/saga_driver.py --help`
  no longer shows `--threshold`; grep the 8 autopilots for `--threshold` → 0.
- PR-A: grep all audits/fixers for `_audit_report_v` → 0 remaining uses
  (all 68 sites, per LB-1; the reworded "legacy shape" notes must not carry
  the token); grep for the mis-citation `REVIEW_SAGA.md` + Iteration-cap → 0.
- PR-F: `bash scripts/sync-version-refs.sh` dry-run on a scratch VERSION bump
  → PARITY historical lines untouched.
- PR-G: verify the anchor resolves on GitHub render (double-hyphen slug).
- Docs-of-record hooks run on every commit (mechanical sync + reminder).

## Docs to update (per CONTRIBUTING matrix)

- **PR-A/B:** plugin `CHANGELOG.md` (PATCH entries), root `CHANGELOG.md`
  `[Unreleased]`, `plans/HANDOFF.md` progress note.
- **PR-C/D:** `framework/VERSION`, root + relevant `CHANGELOG.md`,
  `ROADMAP.md` Recently-shipped bullet, `docs/PARITY.md` row (mechanical),
  CLAUDE.md current-state line (mechanical), `framework/governance/DECISIONS.md`
  only if a GD decision is recorded (D2 catalog is documentation of existing
  behavior — no GD needed; D1 registry block mirrors code — no GD needed).
- **PR-E:** GD-NN in `framework/governance/DECISIONS.md` (founder).
- **PR-F/G:** self-contained (they *are* the docs-of-record updates).
- Plan status updates in this file, ISO-stamped, per merge.

## Risks

| Risk | Mitigation |
|------|------------|
| A1 path unification contradicts an engine behavior that actually writes the legacy filename | The saga driver writes `report.md`/`verdict.json` under `.aidoc/review/`; the audit *skill* composes the final report — path is skill-instructed, so text is authoritative. Verified `doc-brd-audit` + both prd files already use `.aidoc/audit/` in their composition steps. |
| C6/C7 "registry wins" resolves a contradiction in the direction founder disagrees with | Both items flagged in the PR description; GATE-SPEC review is the decision point; prose-tightening alternative documented above. |
| Spec PATCH vs MINOR miscall for PR-C | PR description proposes PATCH (corrections, no new surface) and asks the founder to promote if GATE-SPEC review judges the gate-table/COV02 corrections contract-visible. |
| Sync-script edit (F1/F2) breaks the mechanical hook | Hook is idempotent and testable offline: scratch-bump VERSION, run script, `git diff`, revert. |
| PR-A/A2 backport enlarges 7 audit files that SKILL-DEDUP-001 will later regenerate | Acceptable: drift correctness now; dedup plan consumes the corrected text as its template baseline. |
| Example-corpus lint baseline shifts for unrelated reasons mid-plan | Corpus check compares against freshly captured baseline at PR time, not this plan's date. |

## Claim ledger

| #   | Claim | Symbol | Citation |
| --- | ----- | ------ | -------- |
| 1 | brd-audit already writes the relocated audit-report path | `.aidoc/audit/01_BRD-audit.md` | platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md:56 |
| 2 | prd-audit Execution Contract still instructs the legacy report name | `PRD-NN.A_audit_report_vNNN.md` | platforms/claude-code-plugin/skills/doc-prd-audit/SKILL.md:53 |
| 3 | the same prd-audit composes the final report at the relocated path (intra-file contradiction) | `.aidoc/audit/02_PRD-audit.md` | platforms/claude-code-plugin/skills/doc-prd-audit/SKILL.md:137 |
| 4 | prd-fixer consumes the legacy name in one step | `PRD-NN.A_audit_report_vNNN.md` | platforms/claude-code-plugin/skills/doc-prd-fixer/SKILL.md:41 |
| 5 | and reads the relocated path in another | `.aidoc/audit/02_PRD-audit.md` | platforms/claude-code-plugin/skills/doc-prd-fixer/SKILL.md:55 |
| 6 | brd-audit's fixer-handoff line still uses the legacy name | `BRD-NN.A_audit_report_vNNN.md` | platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md:578 |
| 7 | iplan-audit cites a REVIEW_SAGA section for the iteration cap | `REVIEW_SAGA.md` §"Iteration cap" | platforms/claude-code-plugin/skills/doc-iplan-audit/SKILL.md:343 |
| 8 | chg-audit carries the same mis-citation | `MAX_ITERATIONS=3` | platforms/claude-code-plugin/skills/doc-chg-audit/SKILL.md:388 |
| 9 | the Iteration-cap section actually lives in REVIEW_REMEDIATION_FLOW | `### Iteration cap` | framework/governance/REVIEW_REMEDIATION_FLOW.md:37 |
| 10 | REVIEW_SAGA's saga contract carries the artifact-id field the cap-citing skills quote, but no Iteration-cap section (grep `Iteration cap`/`MAX_ITERATIONS` = 0 hits, verified 2026-07-09) | `artifact_id` | framework/governance/REVIEW_SAGA.md:71 |
| 11 | prd-audit `adapts:` omits review_mode | `adapts: [section_toggles, active_layers, audit_threshold]` | platforms/claude-code-plugin/skills/doc-prd-audit/SKILL.md:18 |
| 12 | yet prd-audit's body resolves review_mode | `review_mode` | platforms/claude-code-plugin/skills/doc-prd-audit/SKILL.md:58 |
| 13 | doc-bdd claims a `.feature` emitter tool exists; `find`/git history show it was never committed | `tools/bdd_to_gherkin.py` | platforms/claude-code-plugin/skills/doc-bdd/SKILL.md:29 |
| 14 | the shipped transcoder is the reverse-direction tool | `gherkin_to_bdd_yaml` | tools/gherkin_to_bdd_yaml.py:1 |
| 15 | saga_driver parses `--threshold` | `--threshold` | platforms/claude-code-plugin/tools/saga_driver.py:644 |
| 16 | stores it on the context | `threshold: int = 90` | platforms/claude-code-plugin/tools/saga_driver.py:200 |
| 17 | and passes it through; `ctx.threshold` is read nowhere else (grep = only these 3 sites + field) | `threshold=args.threshold` | platforms/claude-code-plugin/tools/saga_driver.py:669 |
| 18 | autopilots mandate the dead flag in their exact-command block | `--threshold 90` | platforms/claude-code-plugin/skills/doc-adr-autopilot/SKILL.md:92 |
| 19 | the only `threshold` mention in tests/conformance/platforms is unrelated prose — no test couples to the flag (grep verified 2026-07-09) | `Tier 2 → Tier 1 at threshold` | tests/conformance/platforms/test_authoring_style_referenced.py:89 |
| 20 | the advisory hook's case-arm omits CHG | `BRD\|PRD\|EARS\|BDD\|ADR\|SPEC\|TDD\|IPLAN)` | platforms/claude-code-plugin/hooks/sdd-doc-review.sh:29 |
| 21 | CONFIG.md documents `work_plans_dir` as save-plan's config key; commands/save-plan.md never mentions it (grep = 0) | `work_plans_dir: work_plans/` | platforms/claude-code-plugin/docs/CONFIG.md:52 |
| 22 | plugin CHANGELOG files 0.23.2 under Unreleased | `## [Unreleased]` | platforms/claude-code-plugin/CHANGELOG.md:15 |
| 23 | as a `###` subsection | `### [0.23.2]` | platforms/claude-code-plugin/CHANGELOG.md:17 |
| 24 | plugin.json keywords omit spec/tdd | `"keywords"` | platforms/claude-code-plugin/.claude-plugin/plugin.json:13 |
| 25 | brd-autopilot has the Model precheck section | `## Model precheck` | platforms/claude-code-plugin/skills/doc-brd-autopilot/SKILL.md:66 |
| 26 | chg-autopilot goes straight from detection to Workflow — no Model-precheck section anywhere in the file (grep = 0 hits, verified 2026-07-09) | `## Workflow` | platforms/claude-code-plugin/skills/doc-chg-autopilot/SKILL.md:61 |
| 27 | BDD README teaches an @ears necessary-upstream tag and mislabels the layer | `@ears (Layer 4)` | framework/layers/04_BDD/README.md:59 |
| 28 | TAG_SYNTAX declares BDD the exception (structured YAML `ears:` list, not an @-tag) and mandates one space after the colon | `one space after the colon` | framework/governance/TAG_SYNTAX.md:15 |
| 29 | BDD-TEMPLATE still carries the no-space Gherkin-tag guidance | `Gherkin tag format (NO spaces after colon)` | framework/layers/04_BDD/BDD-TEMPLATE.yaml:293 |
| 30 | while showing the one-space form in the same file | `"@ears: EARS.NN.03.xxxx"` | framework/layers/04_BDD/BDD-TEMPLATE.yaml:305 |
| 31 | ADAPTATION prose says four knobs | `v1 — four knobs` | framework/governance/ADAPTATION.md:72 |
| 32 | the surface file's comment says five | `# Knobs (5)` | framework/governance/ADAPTATION_SURFACE.yaml:33 |
| 33 | but defines a fifth and sixth knob | `- name: review_mode` | framework/governance/ADAPTATION_SURFACE.yaml:67 |
| 34 | sixth knob is flat-named | `- name: quality_loop_max_iterations` | framework/governance/ADAPTATION_SURFACE.yaml:77 |
| 35 | REVIEW_REMEDIATION_FLOW uses the dotted name | `quality_loop.max_iterations` | framework/governance/REVIEW_REMEDIATION_FLOW.md:49 |
| 36 | the SDD guide's gate chain includes SPEC-Ready | `SPEC-Ready (>=90)` | framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md:50 |
| 37a | QUICK_REFERENCE's table jumps from ADR-Ready straight to TDD-Ready (grep `SPEC-Ready` = 0 hits, verified 2026-07-09) | `ADR-Ready` | framework/QUICK_REFERENCE.md:43 |
| 37b | TRACEABILITY's gate table does the same (grep `SPEC-Ready` = 0 hits, verified 2026-07-09) | `ADR-Ready` | framework/governance/TRACEABILITY.md:114 |
| 38 | ADR README confirms the gate exists | `SPEC-Ready Score` | framework/layers/05_ADR/README.md:41 |
| 39 | TRACEABILITY's COV02 says realized by SPEC/TDD | `downstream SPEC/TDD` | framework/governance/TRACEABILITY.md:59 |
| 40 | the SPEC-00 template (matching the code) says EARS is realized by BDD/SPEC/TDD | `an EARS requirement by **BDD/SPEC/TDD**` | framework/layers/06_SPEC/SPEC-00_index.TEMPLATE.md:81 |
| 41 | the realizing map exists only as a code constant | `REALIZING_LAYERS: dict[str, tuple[str, ...]]` | `tools/sdd_doc_lint/__init__.py:1933` |
| 42 | lint emits rule IDs never defined in framework/ (grep STALE01/STRUCT01/TAG01 in framework/ = 0) | `"STALE01"` | `tools/sdd_doc_lint/__init__.py:1141` |
| 43 | THRESHOLD key spec requires subcategory | `{category}.{subcategory}.{attribute}[.{qualifier}]` | framework/governance/THRESHOLD_NAMING_RULES.md:187 |
| 44 | but ID_NAMING's example is 2-segment | `@threshold: BRD.01.perf.p95_latency` | framework/governance/ID_NAMING_STANDARDS.md:207 |
| 45 | and the doc's own IPLAN line hosts a threshold in SPEC | `@threshold: SPEC.NN.perf.target` | framework/governance/THRESHOLD_NAMING_RULES.md:170 |
| 46 | ID_NAMING says two-digit NN | `sequential two-digit number` | framework/governance/ID_NAMING_STANDARDS.md:5 |
| 47 | the registry (authoritative) allows 2+ | `document: "^[A-Z]+-\\d{2,}$"` | framework/registry/LAYER_REGISTRY.yaml:215 |
| 48 | REVIEW_SAGA hard-codes 2-digit with a lockstep clause | `(2-digit NN)` | framework/governance/REVIEW_SAGA.md:71 |
| 49 | naming table gives the slug to BRD only | `(BRD:` | framework/governance/ID_NAMING_STANDARDS.md:252 |
| 50 | IPLAN normatively carries a slug | `IPLAN-NN_{slug}.yaml` | framework/layers/08_IPLAN/README.md:20 |
| 51 | tag-table typo (dot for dash) | `@spec: SPEC.NN` | framework/governance/ID_NAMING_STANDARDS.md:204 |
| 52 | BRD README still frames rehash as future | Not verified end-to-end | framework/layers/01_BRD/README.md:95 |
| 53 | REVIEW_TEAM's normative example quotes 0.14.0 claiming auto-sync | `framework_spec_version: "0.14.0"` | framework/governance/REVIEW_TEAM.md:260 |
| 54 | the playbook contract binds `agent:` to a plugin path | `agent: chaos-engineer` | framework/governance/REVIEW_TEAM.md:259 |
| 55 | AIDOC.md references the Claude CLI | `claude -p` | framework/docs/AIDOC.md:75 |
| 56 | AIDOC.md bootstraps profile from REVIEW_CREWS (contradicting PROFILE-TEMPLATE) | `REVIEW_CREWS.yaml` | framework/docs/AIDOC.md:59 |
| 57 | FEEDBACK_LOG link text/target mismatch, dead anchor (framework/README has no Examples heading; grep = 0) | `[`AIDOC.md`](../README.md#examples)` | framework/governance/FRAMEWORK_FEEDBACK_LOG.md:9 |
| 58 | governance README's index table (rows like REVIEW_TEAM at :20) omits REVIEW_SAGA.md / FRAMEWORK_FEEDBACK_LOG.md / PROFILE-TEMPLATE.yaml (grep = 0 hits, verified 2026-07-09) | `REVIEW_TEAM.md` | framework/governance/README.md:20 |
| 59 | DESC.md quotes spec 0.20.1 as current | `0.20.1` | DESC.md:312 |
| 60 | and plugin v0.17.1 | `claude-code-plugin/v0.17.1` | DESC.md:293 |
| 61 | PARITY provenance line now reads 0.23.0 | `via SAGA-PARITY-001, D-0031` | docs/PARITY.md:26 |
| 62 | it was authored as 0.13.0 (git show bb78dad4:docs/PARITY.md line 26, verified 2026-07-09) | `SAGA-PARITY-001` | docs/PARITY.md:26 |
| 63 | the sync script's global sed is the sweep mechanism | `"framework spec \`$fw_prev\`" "framework spec \`$fw_ver\`"` | scripts/sync-version-refs.sh:189 |
| 64 | an earlier sweep was caught but restored the wrong value | `0.23.0` | plans/FRAMEWORK-TODO.md:151 |
| 65 | TAGGING claims plugin v0.23.2 as a current tag; `git tag` max is claude-code-plugin/v0.20.1 (verified 2026-07-09) | `claude-code-plugin/v0.23.2` | docs/TAGGING.md:149 |
| 66 | SECURITY supported row is 0.11.x | `0.11.x` | SECURITY.md:11 |
| 67 | HANDOFF banner quotes spec 0.35.0 | `0.35.0` | plans/HANDOFF.md:6 |
| 68 | ROADMAP "Now" quotes 0.35.0 as the plugin's current spec surface | `0.35.0` | ROADMAP.md:34 |
| 69 | CONTRIBUTING matrix names a dead ROADMAP section | `"Post-v1.0 — Shipped"` | CONTRIBUTING.md:50 |
| 70 | the reminder hook names it too | `Post-v1.0 — Shipped` | scripts/check-docs-updated.sh:17 |
| 71 | ROADMAP's actual section | `## Recently shipped` | ROADMAP.md:95 |
| 72 | conformance README says platform checks not implemented | `Not implemented yet` | tests/conformance/README.md:13 |
| 73 | HERMES-BACKLOG header date | `2026-07-02` | plans/HERMES-BACKLOG.md:7 |
| 74 | CLAUDE.md links the single-hyphen anchor | `#documentation-discipline-update-docs-of-record-per-pr` | CLAUDE.md:58 |
| 75 | the CONTRIBUTING heading contains an em dash (GitHub slug gets a double hyphen) | `## Documentation discipline — update docs of record per PR` | CONTRIBUTING.md:33 |
| 76 | (LB-1) 8 audits still carry the legacy name in their EC write-step — here doc-iplan-audit, missed by the first A1 draft | `IPLAN-NN.A_audit_report_vNNN.md` | platforms/claude-code-plugin/skills/doc-iplan-audit/SKILL.md:59 |
| 77 | (LB-1) doc-chg-audit likewise | `CHG-NN.A_audit_report_vNNN.md` | platforms/claude-code-plugin/skills/doc-chg-audit/SKILL.md:72 |
| 78 | (LB-3) new governance files must be registered or conformance fails | `EXPECTED_FILES` | tests/conformance/test_governance.py:10 |
| 79 | (LB-3) the orphan guard asserts every governance file is expected | `test_no_orphan_governance_files` | tests/conformance/test_governance.py:113 |
| 80 | (LB-4) the sed rewrites only the backticked spec-version literal — no framework tag-form pattern exists, so tag-form prose escapes but must not be cited as a real tag (framework/v0.13.0 never cut) | `"framework spec \`$fw_prev\`" "framework spec \`$fw_ver\`"` | scripts/sync-version-refs.sh:189 |

## Review log

### Pass 1 — 2026-07-09 — self-review (draft)

- Scoped out the skill-dedup refactor, tag-cutting, emitter build, and fixer
  pipeline unification (minimal-and-realistic rule); parked as named
  follow-ups in Scope-Out.
- Corrected two review-report claims during ledger verification: (a) the
  `review_mode` gap is narrower than reported — all 9 audit bodies resolve the
  key; the drift is the `adapts:` frontmatter (3 files) and the `## Adaptation`
  section (7 files) — A3 rewritten accordingly; (b) `doc-spec-audit` and
  `doc-adr-audit` DO list review_mode in `adapts:` — only prd/ears/bdd lack it.
- Verified no conformance test couples to `--threshold` before proposing its
  removal (B1).
- Chose "registry wins" as the default resolution direction for C6/C7 per
  `framework/registry/README.md`'s own authority rule; flagged both for
  GATE-SPEC judgment.
- Chose a rewrite for F1 so the restored lines can never re-match the sync
  sed — over a marker/exclusion mechanism (which would touch CLAUDE.md and grow
  the script). *(Pass 2 corrected the specific phrasing — see LB-4.)*

**Template-compliance note (Type: bugfix):** the per-PR **Files** columns serve
as this plan's File-structure section (no new module tree is created; edits are
to existing surfaces). Test-first applies to the three code-touching items —
B1 (`saga_driver.py`), D1/D2 (new conformance tests), F1/F7 (script edits):
each lands its test/verification in the same PR, asserted in the Verification
section rather than a separate `[CODE]` step.

### Pass 2 — 2026-07-09 — independent (fresh-context subagent)

A fresh-context reviewer verified all 76 ledger rows against source (100% pass;
~35 semantically deep-verified, including every grep-zero and git-history
claim) and adversarially checked the fix tables. **Ledger clean; 6
load-bearing findings in the fix tables / scope**, all folded:

- **LB-1** — A1 under-scoped: the legacy audit-report name appears at **68
  instructional sites** (self-verified: 8 audits carry it in the EC write-step
  — all but brd; brd retains it at :32/:44/:578; 4–5 sites per audit, 1–3 per
  fixer), not the ~16 first tabulated, and the versioned→fixed filename
  semantics (cleanup glob, "latest") need rewording. A1 rewritten to all 18
  files + all 68 sites + semantic reword; verification criterion made
  achievable.
- **LB-2** — "all 46 findings" was false (L14/L15/L16 unlisted). L14 → C17;
  L16 → SKILL-DEDUP-001 (Out-of-scope); L15 → accepted/no-op (Out-of-scope).
  Scope line corrected to "43 + L14, remaining two named".
- **LB-3** — D2 would turn conformance red: new `governance/LINT_RULES.md`
  must be added to `EXPECTED_FILES` in `tests/conformance/test_governance.py`
  (`test_no_unexpected_files` / `test_no_orphan_governance_files`). Added to
  D2's Files + scope.
- **LB-4** — F1 cited `framework/v0.13.0`, a tag that was never cut
  (`git tag -l` verified) — reintroducing the exact defect F3/F4 remove. F1
  reworded to sweep-proof prose ("0.13.0 spec cycle") with no tag claim.
- **LB-5** — PR-E is a governance PR (touches DECISIONS.md) spanning ~10
  surfaces, violating Rule 1 (≤3). Split into PR-E0 (decision only) +
  PR-E1–E3 (≤3 surfaces each, each citing GD-NN) — the discipline's own
  DECISIONS-first pattern.
- **LB-6** — mandatory corpus cross-check (CLEANUP-PR-B item 5) was missing
  from the review cycle (D1 changes registry shape; C5/C6/C7/C15 touch
  threshold/tag governance text). Run in Pass 3.

Minors folded: A5 per-layer reword note; PR-C/D mechanical-CLAUDE.md exemption
note; G2 also fixes the stale `PLAN-NNN-<slug>` Plans-table row; stray backtick
in Verification removed; template-compliance note added. Reviewer's wrong-
assumption hunts all came back CLEAN (no test pins the "four knobs" wording,
BDD README, gate tables, or PARITY prose; `--threshold` truly dead; the 25
rule-ID enumeration and the STALE01/STRUCT01/TAG01 "undefined-in-spec" claims
confirmed; PR-F correctly non-governance).

### Pass 3 — 2026-07-09 — corpus cross-check + fold convergence (self)

- **Corpus cross-check (LB-6):** `PYTHONPATH=tools python3 -m sdd_doc_lint
  examples/url-shortener/docs/` → 1 ERROR (TH-RES-001, PRD-01 missing
  `component_decomposition`) + STY02/REFGRAN01/COV02 warnings. **All trace to
  the known un-regenerated baseline** (the corpus is regenerated wholesale
  after framework changes — project convention; the plugin already ships a
  "known lint baseline" note for this example). No finding traces to a claim
  in this plan. Decisive positive signal: the **COV02 output** ("BDD element …
  cited element-level by no SPEC/TDD") confirms the implementation's realizing
  set treats BDD as realized-by **SPEC/TDD** — exactly the wording C5 adopts
  for TRACEABILITY.md. Plan claims and corpus reality agree.
- All six LB folds re-read for internal consistency: scope line, Out-of-scope,
  A1, C17, D2, F1, PR-E split, implementation-sequence step 4, version-impact
  line, and verification bullets are mutually consistent.
- One more independent pass is dispatched to confirm the folds introduce no
  new inconsistencies (the folds were substantial — A1 rewrite + PR-E
  restructure).

### Pass 4 — 2026-07-09 — independent (fresh-context subagent) + fold

A second fresh-context reviewer re-ran the greps and the corpus lint itself and
confirmed **LB-1/2/3/4/6 folded correctly** (68 sites / 18 files verified;
C17→REVIEW_TEAM:204 verified; D2 EXPECTED_FILES coupling verified against
`test_governance.py`; F1 tag-absence + sed-escape rationale verified; corpus
baseline + COV02→C5 confirmation reproduced). It surfaced **one new
load-bearing finding**:

- **NF-1** — the PR-E split left **PR-E2 with 4 surfaces** (ID_NAMING + AIDOC +
  REVIEW_REMEDIATION_FLOW + CONTRIBUTING), violating the ≤3 bound the split
  exists to satisfy. **Folded:** the E-edits are regrouped into four
  ≤3-surface PRs — E1 (REVIEW_TEAM + AUTHORING_STYLE + IPLAN-TEMPLATE = 3),
  E2 (ID_NAMING + AIDOC = 2), E3 (REVIEW_REMEDIATION_FLOW + CONTRIBUTING = 2),
  E4 (SPEC-guide + TRACEABILITY + SPEC-00 = 3). Version-impact + implementation
  sequence updated E1–E3 → E1–E4. Consequential overlap caught during the
  fold: the `claude -p` neutralization (F3) was double-listed in C11 and E2;
  removed from C11 (it is an engine-agnosticism edit → belongs in founder-gated
  PR-E2). All other new-inconsistency checks came back clean (no stray "E4"
  before this fold created the real E4; ledger rows 76–80 resolve; A1
  ledger↔table consistent).

NF-1 was a pure regrouping with no source-claim change (the surfaces and their
`file:line`s are unchanged; only their PR assignment moved), so it needs no new
ledger citation and no further independent pass under the "substantive fold"
bar — the surfaces were already reviewed in Pass 4.

**Result:** ready. Ledger has zero UNVERIFIED rows; two independent
fresh-context passes (2, 4) drove the load-bearing count to zero; the mandatory
corpus cross-check ran clean against the known baseline; the final state has no
load-bearing findings.
