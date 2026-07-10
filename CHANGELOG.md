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

### Added — Hermes `0.9.0 → 0.10.0` `audit_threshold` raise-only gate — HERMES-ADAPT-ENFORCE-001 (2026-07-10)

- **Enforces the `.aidoc/profile.yaml` `audit_threshold` knob** (the Hermes-native
  slice of H-16). `validate_score` honors a per-layer profile threshold only if ≥ 90
  (the framework-documented default) and raises the gate via `max()` after the
  tdd/iplan floor — never weakens. `sdd_score_validate` gains an optional `project`
  arg (+ pipeline threading) so the profile is reachable; a handler-level test guards
  the wiring. Structural `active_layers`/`section_toggles` enforcement (the cascade is
  a framework change — byte-identical vendored lint) and `quality_loop_max_iterations`
  (H-7) remain deferred. Plan: `plans/HERMES-ADAPT-ENFORCE-001-PLAN.md`. Hermes stream only.

### Added — Hermes `0.8.0 → 0.9.0` `.aidoc/profile.yaml` runtime consumption — HERMES-REVIEW-001 PR-ADAPT (2026-07-10)

- **Hermes now reads the spec's declared adaptation input at runtime** (M1/M7;
  partly closes HERMES-BACKLOG **H-16**). New `mcp_server/profile.py` loads
  `.aidoc/profile.yaml` (all 6 `ADAPTATION_SURFACE.yaml` knobs, graceful fallback),
  wired into `ProjectContext`. **A2**: `sdd_review` accepts the spec `review_mode`
  vocabulary (`team`→`saga_parallel`, `single_pass`→`prompt_only`) and honors a
  profile that explicitly declares it. **A1**: the creation prompt injects a
  `## Project Adaptation Profile` block (`glossary` + layer-scoped `section_toggles`
  - `active_layers`) via `context_builder`. Structural enforcement of
  `active_layers`/`section_toggles`, the `audit_threshold` gate, and
  `quality_loop_max_iterations` are deferred (H-16 follow-up; the last needs the outer
  review loop tracked as H-7). Hermes stream only.

### Changed — Hermes `0.7.4 → 0.8.0` native BDD authoring → YAML-BDD — HERMES-REVIEW-001 PR-BDD (2026-07-10)

- **Rewrote Hermes's private BDD prompts/persona/output-schema from Gherkin to the
  structured `scenarios:` YAML form** (D-0038, closes HERMES-BACKLOG **H-15**). The 3
  BDD prompts (creation/review/remediation), the `qa_lead` persona lens, and the
  Layer-4 output schema now teach the flat `scenarios:` list (per-scenario
  `type`/`priority`, element-level `ears:`, no Gherkin, no written `@`-tags), plus
  M6/L4/L5 stale-tag/wording cleanups in the EARS/PRD/SPEC prompts. Added a
  Hermes-side drift guard (`test_bdd_prompt_yaml_conformance.py`) keyed on
  **structural** Gherkin markers (not the bare word "Gherkin"), making a previously
  CI-invisible drift class visible. Hermes stream only.

### Fixed — Hermes `0.7.3 → 0.7.4` MCP source fixes — HERMES-REVIEW-001 PR-CODE (2026-07-10)

- **Six correctness/hygiene fixes in the Hermes MCP server** from the 2026-07-09
  review, each with a regression test where behavior changes: **C1 (H2)** the
  API-executor env lock is now a module-global `threading.Lock` (the lazily-created
  `asyncio.Lock` raised `RuntimeError: bound to a different event loop` under the
  saga's cross-thread `ThreadPoolExecutor`/`asyncio.run` contention; acquire site
  `async with` → `with`, factory collapsed) + cross-thread regression test; **C2
  (M2)** `write_versioned_report_atomic` uses `os.open(O_CREAT|O_EXCL)` instead of
  the exists()-then-`os.replace` TOCTOU + concurrent-writer test; **C3 (L1)**
  `datetime.now(UTC)` replaces deprecated `datetime.utcnow()`; **C4 (M3)** the
  blocking saga call is offloaded via `await asyncio.to_thread(...)` so it no longer
  blocks the MCP event loop; **C5 (L2)** cleanup unlinks first and records deletion
  only on success (no half-done batch / false claims); **C6 (L3)** removed dead
  scoring-runner code + annotated the TDD/IPLAN fail-closed readiness gate. Hermes
  stream only.

### Fixed — Hermes `0.7.3` docs/version drift sweep — HERMES-REVIEW-001 PR-DOCS (2026-07-10)

- **Reconciled active-facing Hermes docs to the real `0.7.3` / spec `0.36.2`
  state** (2026-07-09 Hermes review findings H3/H4/H5/M4/M5/M8, L6). `pyproject.toml`
  version `0.1.0` → `0.7.3`; `platforms/hermes/README.md` conformance block +
  platform-info table (canonical `hermes/v*` cell, complete 27-tool table, module
  count `20`, persona count `16`); `docs/HERMES_INTEGRATION.md` paths rewritten to
  `platforms/hermes` + Python `>=3.12` + retired `ucx_kb` KB sections repointed to
  engramory; `docs/README.md` `2.0.0`/`ucx_hermes` self-id + dead migration link +
  `SPEC-011`; `docs/ROADMAP.md` legacy table marked historical; `CHANGELOG.md`
  `[0.7.3]` section cut from the bundled `[Unreleased]`. `scripts/sync-version-refs.sh`
  extended to cover the Hermes `pyproject.toml` + README version blocks (closes
  FRAMEWORK-TODO `HERMES-README-VERSION-DRIFT`). Hermes-stream docs/tooling only.

### Changed — Framework Spec `0.36.1 → 0.36.2` — FRWK-REVIEW-002 PR-E engine-agnosticism neutralization (2026-07-09)

Implements the GD-06 Hybrid ruling — neutralizes the generic platform vocabulary
in the spec while keeping the two sanctioned bindings (spec PATCH, no behavior
change):

- **Neutralized:** `doc-*`/"SKILL" vocabulary → engine-neutral terms ("audit
  engine", "authoring engine") across `REVIEW_TEAM.md`, `AUTHORING_STYLE.md`,
  `ID_NAMING_STANDARDS.md`, `IPLAN-TEMPLATE.yaml`, `FRAMEWORK_FEEDBACK_LOG.md`,
  `DOC_GOVERNANCE_CORE.md`; the `claude -p` reference →
  "the engine's CLI"; the AIDOC `.aidoc/`-population table → explicitly marked a
  Platform-B illustration; repo-root tool paths (`trace_walk.py`,
  `sdd_coverage.py`) → framed as a reference implementation outside the spec
  (`TRACEABILITY.md`, `REVIEW_TEAM.md`, `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`,
  `SPEC-00_index.TEMPLATE.md`, `BRD-TEMPLATE.yaml`).
- **Kept (GD-06 sanctioned exceptions):** the playbook `agent:` executor field
  (plugin-path pointer softened to "see the platform's own docs") and the
  `REVIEW_REMEDIATION_FLOW.md` workspace-CI section (gains a GD-06 scope note).

### Added — Framework Spec `0.36.0 → 0.36.1` — GD-06 engine-agnosticism boundary (FRWK-REVIEW-002 PR-E0) (2026-07-09)

Records **GD-06** in `framework/governance/DECISIONS.md` — the founder-ratified
policy for engine-specific tokens in the spec (the FRWK-REVIEW-002 PR-E blocker).
**Hybrid ruling:** neutralize the generic platform vocabulary (`doc-*`/"SKILL"
terms, the `claude -p` reference, the AIDOC plugin-skill table, repo-root tool
paths → "reference implementation outside the spec"); **keep two load-bearing
bindings as documented exceptions** (the D-0022 pattern) — the playbook `agent:`
executor field and the workspace-CI section. Decision only (no doc edits yet);
the neutralization edits follow as a scoped PR citing GD-06. SemVer patch, C1.

### Added — Framework Spec `0.35.2 → 0.36.0` — FRWK-REVIEW-002 PR-D spec-completeness additions (2026-07-09)

Two normative surfaces that previously existed only in linter code, so an
independent engine can now implement them from `framework/` alone (spec MINOR):

- **`realizing_layers` map (D1).** Added a normative `realizing_layers` block to
  `registry/LAYER_REGISTRY.yaml` (BRD→PRD; EARS→BDD/SPEC/TDD; BDD→SPEC/TDD) — the
  element-level backward-coverage map behind `COV02` (D-0039), previously only a
  `REALIZING_LAYERS` constant in `sdd_doc_lint`. `TRACEABILITY.md` now cites it as
  the normative source. New conformance guard asserts the linter constant matches
  the registry block.
- **Lint-rule catalog (D2).** New `framework/governance/LINT_RULES.md` — one row
  per emitted rule ID (28: COV01-03, CSC01, DG02, EARS01, FM01, HASH01, ID01-03,
  IDDRIFT01, PH01, PROV01, REFGRAN01, REUSE01/02, STALE01, STRUCT01, STY01-03,
  TAG01, TH01/02, TH-RES-001, TRACE-RES-001, BDD-SCHEMA-001) with meaning,
  severity, and defining contract. New conformance guard asserts every rule ID the
  linter can emit is catalogued; added to `test_governance.py` `EXPECTED_FILES`
  and the governance README index.

### Fixed — Framework Spec `0.35.1 → 0.35.2` — FRWK-REVIEW-002 PR-C spec-text corrections (2026-07-09)

Normative-text corrections from the 2026-07-09 plugin + core-docs review
(`plans/FRWK-REVIEW-002-PLAN.md`), no behavior change (spec PATCH):

- **BDD layer README + template** rewritten to the shipped YAML-BDD contract
  (structured `scenarios:`/`ears:` per scenario, not Gherkin `@`-tags; `@ears`
  corrected to Layer 3; dropped the contradictory "NO spaces after colon"
  Gherkin block).
- **Adaptation surface reconciled** — `ADAPTATION.md` §4 now documents all **6**
  knobs (added `review_mode`, `quality_loop_max_iterations` rationale); fixed
  the `Knobs (5)` comment and the `§8 → §9` pointer; unified the dotted
  `quality_loop.max_iterations` → flat name in `REVIEW_REMEDIATION_FLOW.md`.
- **SPEC-Ready gate** added to the `QUICK_REFERENCE.md` and `TRACEABILITY.md`
  gate tables (both jumped ADR-Ready → TDD-Ready).
- **COV02 wording** corrected to the realizing-set map (EARS → BDD/SPEC/TDD;
  BDD → SPEC/TDD).
- **Threshold + document-ID specs** reconciled to the authoritative registry
  ("registry wins": threshold key min 2 segments / subcategory optional; NN is
  2+ digits).
- **Rehash phrasing** updated (BRD §7 is verifiable-on-demand, Phase 1 shipped;
  other layers Phase 2+).
- Misc: `REVIEW_TEAM.md` spec-version example → placeholder; AIDOC profile
  semantics aligned to `PROFILE-TEMPLATE.yaml`; FEEDBACK_LOG dead link +
  undefined identifiers; residual "Gherkin" mentions; governance/framework
  README indexes; `@spec` tag-form typo; "Balanced split" relabel; fixer
  break-circuit checkpoint canon documented in `REVIEW_REMEDIATION_FLOW.md`.

### Fixed — Claude Code plugin `0.23.4` — FRWK-REVIEW-002 PR-B plugin mechanics (2026-07-09)

Plugin mechanics from the 2026-07-09 review (`plans/FRWK-REVIEW-002-PLAN.md`):
removed the dead `--threshold` flag from `saga_driver.py` and all 8 autopilot
command blocks (the effective gate is the `audit_threshold` knob), added `CHG`
to the advisory-hook case-arm, wired `/aidoc-flow:save-plan` to the
`work_plans_dir` config key with a legacy-CLAUDE.md fallback, promoted the
released `0.23.x` plugin-changelog entries to `##` sections, added `spec`/`tdd`
to `plugin.json` keywords, and documented the CHG model-precheck exclusion.
Per-package detail in [`platforms/claude-code-plugin/CHANGELOG.md`](platforms/claude-code-plugin/CHANGELOG.md).

### Fixed — Claude Code plugin `0.23.3` — FRWK-REVIEW-002 PR-A skill-content drift (2026-07-09)

Plugin-side drift fixes from the 2026-07-09 plugin + core-docs review
(`plans/FRWK-REVIEW-002-PLAN.md`): unified the audit-report path across all 18
audit/fixer skills (68 sites; legacy versioned name → relocated
`.aidoc/audit/<NN>_<LAYER>-audit.md`), corrected the iteration-cap governance
citation and backported it, made `review_mode` adaptation consistent, removed
the phantom `bdd_to_gherkin.py` reference, propagated the verdict-outcome
clarifier, and disambiguated the 9 creator-vs-autopilot descriptions. Per-package
detail in [`platforms/claude-code-plugin/CHANGELOG.md`](platforms/claude-code-plugin/CHANGELOG.md).

### Added — auto-merge-ai-prs.yml caller (server-side auto-merge for AI-opened PRs) (2026-07-08)

Adopts the canonical `auto-merge-ai-prs.yml` caller from
`aidoc-flow-ci/install/templates/workflows/auto-merge-ai-prs-public.yml`
per REPO_STANDARDS §17 workspace canon. Complements OPS-0062 (AI
agent auto-merge default — in-session `--auto`) with server-side
recovery for stuck-green PRs.

- **`.github/workflows/auto-merge-ai-prs.yml`** (NEW) — thin caller
  pinning `aidoc-flow-ci@ci/v1.5.1`. ubuntu-latest runner labels.

Rollout aligned with 5 workspace-canon consumers (operations, business,
iplanic, iplan-runner, engramory) from prior IPLAN-0030 Phase B.
Requires reviewer App install + `auto_merge.repos` allowlist entry to
fully activate; falls back to GITHUB_TOKEN with downgrade warning
pre-install.

Self-review skipped per founder OK — mechanical template-clone workflow addition; ci/v1.5.1 pin matches sibling consumers

### Changed — Wave 1 adoption of aidoc-flow-ci PLAN-003 governance-file canon (2026-07-08)

Framework adopts the PLAN-003 flexible-canonical (Option B) project-governance
file canon shipped by `aidoc-flow-ci@ci/v1.6.0` (see PR-V1/V2/V3/V4 —
`aidoc-flow-ci#73`, `#74`, `aidoc-flow-operations#217`, `aidoc-flow-ci#75`
— design at `aidoc-flow-ci/plans/PLAN-003_project-governance-canon.md`).
Governance drift check (`bash ../aidoc-flow-ci/install/apply-standards.sh
--check`) now reports `CLAUDE.md#per-repo-governance: OK`.

- **`CLAUDE.md`** — `## Per-repo governance` table updated:
  - Fixed `Plans` row: cell was `plans/<NAME>-PLAN.md` (a naming pattern
    that doesn't resolve on disk) → `plans/` (the actual directory).
  - Added required `Roadmap | ROADMAP.md` row (was absent per PLAN-003
    §4.5 required-row check).
  - Added 3 repo-specific additional rows below the required 6 per
    §4.2: `Spec governance decisions | framework/governance/DECISIONS.md`
    (second DECISIONS surface — spec-governance — distinct from
    `plans/DECISIONS.md` which tracks migration decisions),
    `Hermes per-package changelog | platforms/hermes/CHANGELOG.md`, and
    `Plugin per-package changelog | platforms/claude-code-plugin/CHANGELOG.md`.

**3 surfaces** (CLAUDE.md + FRAMEWORK-TODO.md tracking entry + this
CHANGELOG entry) — at the OPS-0061 Rule 1 ≤3 boundary. Retrofit of the
workspace-standards blocks (per
PLAN-003 §5.4c framework row link-summary-format retrofit) DEFERRED to
follow-up PR — tracked in `plans/FRAMEWORK-TODO.md` § Open under
`[docs] PLAN-003 §5.4c framework link-summary retrofit`. Orthogonal to
the `--check` governance-drift gate this PR closes.

Multi-agent self-review per OPS-0065 (code-reviewer + documentation-specialist parallel dispatch): approved after 1 fold cycle addressing 2 HIGH (CHANGELOG TBD placeholder → filled; PR reference undercount PR-V1/V2 → PR-V1/V2/V3/V4 with per-PR #s) + 2 MEDIUM (deferred retrofit had no forward pointer → tracked in FRAMEWORK-TODO.md per feedback_framework_todo_list rule; scope-imprecision on plans/DECISIONS.md label wording → clarified as "migration decisions") + 5 LOW (dual-DECISIONS phrasing; italic separator note; explanatory prose deferred; PLAN-003 path cited inline; jargon reduced)

### Added — governance-doc addition triggers framework spec 0.35.0 → 0.35.1 patch bump (2026-07-08)

- **`framework/VERSION`** — patch bump `0.35.0 → 0.35.1`. Prior Wave 1
  canon-adoption PR added a new "Mechanical author-side pre-push gate
  (aidoc-flow workspace layer)" section to
  `framework/governance/REVIEW_REMEDIATION_FLOW.md` — GATE-SPEC-E005
  requires a version bump when `framework/**` changes. Patch (not
  minor) because the addition is a governance-doc cross-reference,
  not a schema/CHG change.

### Added — Wave 1 governance-tier adoption of aidoc-flow-ci canon (PLAN-002 §5.5) (2026-07-08)

Self-adopts the workspace-wide standards canon from `aidoc-flow-ci@ci/v1.6.0`
per PLAN-002 §5.5 Wave 1 (governance tier). Adds mechanical OPS-0069
audit-trail enforcement + updates `framework/governance/REVIEW_REMEDIATION_FLOW.md`
to reference the new mechanical author-side gate (M7 fix per plan §5.5 Wave 1).

Files (5 file surfaces + REVIEW_REMEDIATION_FLOW.md update + CHANGELOG):

INSTALLED (fresh canon):

- `scripts/pre_push_check.sh` (NEW) — canon self-review script.
- `.gitattributes` (NEW) — canon baseline.
- `.github/workflows/audit-trail.yml` (NEW) — caller `@ci/v1.6.0`.
- `.github/workflows/standards-drift.yml` (NEW) — weekly cron `--tier governance`.

MERGED:

- `.pre-commit-config.yaml` — canon block appended via ruamel round-trip
  (`indent(mapping=2, sequence=4, offset=2)`); `# CANON:` marker line 1.
- `.gitignore` — 15 canon lines appended.

UPDATED (M7 fix per plan §5.5):

- `framework/governance/REVIEW_REMEDIATION_FLOW.md` — new "Mechanical
  author-side pre-push gate (aidoc-flow workspace layer)" section
  documenting the OPS-0069 audit-trail gate as complementary to the
  artifact-level review loop. Content-shaped review + process-shaped
  mechanical gate are two independent layers; both must pass for merge.

PRESERVED (intentional canon-divergence):

- `.github/CODEOWNERS` — existing custom routing preserved (more granular
  than flat canon).
- `.github/PULL_REQUEST_TEMPLATE.md` — existing template preserved (repo-
  idiomatic; uppercase filename retained — GitHub accepts either case).
- `.github/dependabot.yml` — existing per-directory pip + github-actions
  config preserved (more useful than flat canon).

Server-side follow-up (F5 blast-radius; not in this PR):
`bash install/apply-standards.sh --apply --repo vladm3105/aidoc-flow-framework
--tier governance --ci-tag ci/v1.6.0 --yes`

Origin: `aidoc-flow-ci/plans/PLAN-002_workspace-standards-rollout.md` §5.5
Wave 1 (governance tier).

### Added — PROVISIONAL-IDS-002 Phase 1: formalize the hash-input contract + ship `rehash --check` (the Model-2 element-ID drift verifier, `IDDRIFT01`) (framework spec 0.34.2 → 0.35.0) (2026-07-08)

Delivers the ratified Model-2 direction (D-0061): element IDs get a real, verifiable
content-drift signal, as a deliberately minimal Phase-1 core.

- **Formalized the byte-exact hash-input contract** in `framework/governance/ID_NAMING_STANDARDS.md`
  (the authority): the **normalization transform** (NFC → casefold → strip to `[a-z0-9 ]` →
  collapse whitespace → trim → first 100 chars) and the **BRD §7 FR field-extraction boundary**
  (title between `—` and `**`; description = post-band body accumulated across wrapped
  continuation lines until a blank line / next bullet / heading / acceptance label). The
  normalization moved out of the BRD template (`id_standard` block, now a cross-ref) → one source.
  `TRACEABILITY.md` documents the new rule.
- **`rehash --check`** — `python -m sdd_doc_lint.rehash --check <docs>` recomputes each canonical
  BRD §7 FR element's hash and emits **`IDDRIFT01`** (WARNING) on a mismatch (content drifted since
  the ID was minted, or a canonical leak). **Opt-in** (NOT in the default `sdd_doc_lint` pass, so
  the default gate + example-corpus lint stay **byte-identical**), **`id_state: canonical`-gated**
  (provisional docs exempt), **BRD §7 only**. Primitives live in the canonical
  `sdd_doc_lint/__init__.py` (vendored byte-identical to both platform mirrors — the drift guard +
  `sync-vendored.sh` now cover the new `rehash.py`); the CLI is `sdd_doc_lint/rehash.py`.
- **Tests** — `tests/conformance/test_rehash_verifier.py` (16) proves transform determinism +
  documented anglocentric strip (V4), exact extraction bytes incl. multi-line / wrapped-band /
  colon-in-body (V4b), §7-only scope (V4c), clean/drift/provisional-exempt (V1/V2/V3), the 8-char
  collision form, and advisory severity. 182 conformance green.
- **Scoped, not over-claimed** — the authority says the contract is **verifiable on demand** via
  the opt-in command (Phase 1 does not run it on the corpus; corpus IDs are LLM-generated and stay
  unverified until the Phase-2 reconciliation), never "verified" — avoiding the exact over-claim
  D-0061 removed.
- **Deferred to founder-decided Phase 2+:** `rehash --fix` (canonicalize + citation cascade),
  all-8-layer extraction, corpus reconciliation, advisory→gate promotion, a Unicode-category strip.
- Framework spec **MINOR** `0.34.2 → 0.35.0` (new normative contract content trips GATE-SPEC); both
  `FRAMEWORK_SPEC_VERSION` pointers auto-re-matched; plugin + Hermes product versions unchanged.
  See `plans/DECISIONS.md` D-0062 + `plans/PROVISIONAL-IDS-002-PLAN.md`.

### Changed — FRAMEWORK-PROD-READINESS-001: scope the SHA-256 element-ID guarantee to reality across all 13 spec surfaces + ratify GD-02…05 (framework spec 0.34.1 → 0.34.2) (2026-07-07)

The 2 framework-side items from the production-readiness audit. **(1) SHA-256 over-claim
scoped.** `ID_NAMING_STANDARDS.md` — and 12 more spec surfaces (5 layer templates' `id_standard`
block + 5 layer READMEs + the PRD-00/SPEC-00 index templates, all vendored) — promised
"deterministic, byte-identical" content-hash element IDs, but the engines LLM-generate IDs that
aren't real `SHA256(content)` and nothing verifies them (D-0040 deferred `rehash --check` to
PROVISIONAL-IDS-002). Every surface now carries a scope caveat: the SHA-256 form is the
**canonicalization target**, not a currently-verified property — a produced ID is a stable
opaque string, unverified until `rehash --check` ships. The algorithm + `hash_algorithm: SHA256`
field stay verbatim (the target is unchanged; only the *guarantee* is scoped to reality).
**(2) GD-02…05 ratified.** Flipped `Status: Proposed → Accepted` for the four graduated
governance decisions that are merged + enforced (GD-05 disregard-strip, GD-04 IPLAN-ASSURANCE,
GD-03 REFGRAN01, GD-02 independent review). Doc-accuracy + governance-status only — no
rule/algorithm/structure change; deterministic `sdd_doc_lint` output byte-identical; 166
conformance green. Framework spec **PATCH**. **Forward note:** the deeper decision
(PROVISIONAL-IDS-002 — enforce the hash + use it as a content-drift identifier) is now DECIDED
as **Model 2** (stable ID + drift fingerprint) and follows in its own plan. See
`plans/FRAMEWORK-PROD-READINESS-001-PLAN.md` + `plans/DECISIONS.md` D-0061.

### Fixed — PLUGIN-PROD-READINESS-001: fix the playbook-path-escape BLOCKER + 3 SHOULD-FIX from the plugin production-readiness audit (plugin 0.23.1 → 0.23.2; no framework change) (2026-07-06)

A 4-agent production-readiness audit of the Claude Code plugin found it clean/green on
packaging, conformance, tooling, versioning, and skill structure — with one BLOCKER + three
SHOULD-FIX, all fixed here. **BLOCKER:** the 9 `doc-*-audit` skills + `agents/synthesizer.md`
resolved their vendored playbooks / `REVIEW_TEAM.md` via `${CLAUDE_PLUGIN_ROOT}/../../framework/…`
— the `/../../` escapes the plugin root, so in a distributed install every playbook/contract
load failed and the weighted-crew review collapsed to zero coverage; dropped `/../../` (11
refs). Plus: reconciled `doc-ears` + `doc-ears-audit` to the D54-F04 latency-vs-non-latency
model; bumped the deprecated-stub removal milestone `v0.7.0 → v1.0.0` (8 occurrences); added a
"known lint baseline" note to the url-shortener example README + dropped a phantom
`docs/.version` line. Plugin PATCH; no `framework/` change. 166 conformance green. D-0060.

### Removed — H-11b: delete the 5 orphaned hand-vendored `references/` framework-doc copies from the Hermes sdd-orchestrator (hermes 0.7.2 → 0.7.3; skill 2.1.1 → 2.1.2; no framework change) (2026-07-06)

Deleted `ucx-readme.md`, `doc-governance-core.md`, `id-naming-standards.md`,
`layer-registry.yaml`, `data-consistency-report.json` from
`platforms/hermes/agent-skills/.../sdd-orchestrator/references/`. Orphaned (no loader
references them) + stale drift-sources (e.g. `id-naming-standards.md` was titled "SDD v3.2",
53 vs the canonical 191 lines, describing the retired sequential-ID scheme). Per D-0013 Hermes
reads `framework/` directly, so these local copies had silently drifted; deleting removes the
drift source. No behavioral change; 166 conformance + 511 Hermes green. D-0059. Closes H-11b.

### Changed — D54-F04: broaden the EARS-Ready rubric so a non-latency quantified bound counts as "quantified" (framework spec 0.34.0 → 0.34.1) (2026-07-06)

The EARS quality-attribute rubric in `framework/layers/03_EARS/EARS-TEMPLATE.yaml` conflated
"quantified" with "has latency percentiles" — it mandated `p50/p95/p99` for *every* timing
requirement, so a genuinely quantified **non-latency** bound (`WITHIN 3 cycles`, retry
iterations, an event-window, a `*.count` threshold) was docked for "lacking percentiles."
Reworded the four percentile-mandating surfaces (`_guidance` scoring weight, the EARS-Ready
checklist, the antipattern, and the quality-attributes guidance + its illustration block) so
**latency/response-time** dimensions use percentiles while a **non-latency** dimension is
quantified by a concrete numeric value + unit (added a "Non-latency bound examples" table:
cycles / retries / count). The latency-percentile bar is **preserved**. No new syntax — the
threshold vocabulary already supports non-latency categories (`circuit.failure.count`), and
the playbook lenses (`tech_lead.md` "any other quantified" bound) already scored this way; the
template was the over-strict outlier, now reconciled to them. Prose-only `_guidance` rewording;
no validator/schema/conformance change (deterministic `sdd_doc_lint` output over the corpus is
byte-identical). The rubric is LLM-auditor scoring, so the score improvement on the example
corpus's non-latency bounds (`RTO ≤ 30 min`, `≥ 99.9% monthly`, a visit-window) lands at the
next wholesale regen. Framework spec **PATCH**; plugin + Hermes product versions unchanged.
See `plans/D54-F04-EARS-RUBRIC-PLAN.md` + `plans/DECISIONS.md` D-0057.

### Fixed — LINT-DOCID-HEADER-FALSE-POSITIVE: narrow the ID02 doc-id scan to digit-leading tokens (tooling; no spec change) (2026-07-06)

`sdd_doc_lint`'s ID02 malformed-doc-id scan (`_DOC_ID` = `\b(TYPE)-([A-Za-z0-9]+)\b`) flagged
**any** `TYPE-<token>` that wasn't `TYPE-<digits>`/`-INDEX` as malformed — so legitimate prose
(`PRD-Ready`, `BRD-TEMPLATE`, `BRD-NN`) tripped it on the BRD-00 index template and any
consumer's filled-in index. A valid doc-id's post-hyphen segment is always all-digits
(`doc_re` = `^[A-Z]+-\d{2,}$`), so ID02 now fires **only when the second segment is
digit-leading** — a letter-leading `TYPE-<word>` is a compound word, not a doc-id attempt.
Removes the false-positives; keeps real malformed ids (`BRD-2`, `BRD-007x`); generalizes
D-0043's `-INDEX` exemption. Pure `tools/sdd_doc_lint` change, vendored byte-identical to both
platform mirrors; **no `framework/` change, no version bump** (the D-0043 STRUCT01-INDEX-EXEMPTION
precedent). New unit guard; 166 conformance green. See `plans/DECISIONS.md` D-0056 +
`plans/LINT-DOCID-HEADER-FALSE-POSITIVE-PLAN.md`.

### Added — D54-F13 phase-leak: COV03 advisory when a deferred (`Future`-banded) FR is realized downstream (framework spec 0.33.1 → 0.34.0) (2026-07-06)

New `sdd_doc_lint` rule **`COV03`** — the exact inverse of `COV01`'s escape. `COV01` blocks
an in-scope (`AUTHORED`) FR that is *not* realized; `COV03` warns when a **`DEFERRED`
(`Future`-banded) FR IS realized downstream** by its realizing layer (PRD) — something scoped
for a next MVP cycle is being pulled into the current build. **Advisory (`warning`) in both
`build` and `gate-code`, never blocks** (scope pull-forward is legitimate; the fix is to
re-band the FR `P1`/`P2` or confirm the deferral). A `realized_by:` FR is a positive coverage
claim (`REALIZED_BY`), never flagged; cross-cycle leaks need no gate (later-cycle BRDs are
trace-inert). This closes the phase-leak leg of `D54-F13` (its missing-downstream leg shipped
earlier as `COV01`) with **no new phase tag** — grounding found the `Future` band + the BRD-00
`Cycle` roadmap already encode both phase axes. Implemented in the canonical
`tools/sdd_doc_lint/__init__.py` (vendored byte-identical to both platform mirrors via
`sync-vendored.sh`), documented normatively in `framework/governance/TRACEABILITY.md` §Coverage
gates + a BRD band note; 6 new `test_coverage_engine.py` cases; zero findings on the example
corpus. Framework spec **MINOR** (new normative rule); plugin + Hermes product versions
unchanged. See `plans/D54-F13-PHASE-LEAK-PLAN.md` + `plans/DECISIONS.md` D-0055.

### Changed — IPLAN-LANG-001: de-Python the IPLAN template; inherit language from SPEC (framework spec 0.33.0 → 0.33.1) (2026-07-06)

`framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` hardcoded a Python toolchain in its
example content (`pip install`, `pytest`, `mypy`, `ruff`, `src/[module]`,
`tests/unit/test_[module].py`), re-pinning a language its own `@spec: SPEC-NN` already
owns (SPEC declares `language:` + `dependencies:` at Layer 6). Made the example content
**language-neutral**: `file_manifest` paths (§2) and `execution_commands` strings (§3)
are now `<…, per the @spec language>` placeholders + a lead-comment per category, each with
a clearly labelled `# example (Python):` line, and the `_guidance` instructs the author to
derive concrete commands/paths from the `@spec` language + dependencies. Extended the same
treatment to the residual Python example paths in §5 (session_handoff) and §6 (traceability
`@code:`/`@tests:` + code_inventory) so the template is internally consistent — a
discovered-in-impl extension of the plan's §2/§3 scope, same fix. The **structural contract
is preserved exactly** (six sections; the `setup`/`implementation`/`validation` categories,
each a non-empty list), so **no validator, schema, or conformance change** — Hermes
`iplan_rules.py` still passes, `test_layers.py` metadata assertions hold, and the plugin
bundle was re-vendored via `sync-plugin-framework.sh`. Framework spec **PATCH**; plugin +
Hermes product versions unchanged. See `plans/IPLAN-LANG-001-PLAN.md` + `plans/DECISIONS.md`.

### Changed — ENG-STALE-DEPTH-DOCS: reconcile the Hermes sdd-orchestrator's published root-docs + governance docs to the single-path model (dead Lite/Standard/Full tables + a dead SDD_DEPTH_GUIDE.md link) (hermes 0.7.1 → 0.7.2; skill 2.1.0 → 2.1.1; no framework change) (2026-07-06)

Completes the behavioral legs of H-11a. The sdd-orchestrator skill's user-facing
`root-docs/` + `governance/` docs still advertised the dead v3.2 SDD-Lite/Standard/Full
depth-variant model (the 2026-06-12 legacy cleanup fixed `sdd_config.yaml` + the repo
README; D-0053 fixed the SKILL + 2 loaded governance files). Fixed the 7 remaining
published surfaces: `README.md` (a "Scalable Depth" tagline + a depth-variants table that
**contradicted the same file's** correct single-path prose), `MULTI_PROJECT_QUICK_REFERENCE.md`

- `MULTI_PROJECT_SETUP_GUIDE.md` (two depth tables + an embedded changelog line),
`CHG_GOVERNANCE_BRIDGE.md` (a rule keyed on the dead tiers), two **dead links** to a
nonexistent `SDD_DEPTH_GUIDE.md` (removed), and a dead "SDD-Full" term in CHG-label
comments (no `create_label` value changed). All reconciled to the single SDD path.
Doc-accuracy only — no engine, no `framework/` change (no GATE-SPEC), no new decision.
Closes `ENG-STALE-DEPTH-DOCS`. Deferred: the public-render leg + the cosmetic v3.2 string
sweep.

### Changed — H11-ORCHESTRATOR-CREW-MODEL: modernize the Hermes sdd-orchestrator skill from the v3.2 15-persona + depth-tier model to the weighted-crew + playbook + single-path model (hermes 0.7.0 → 0.7.1; skill 2.0.0 → 2.1.0; no framework change) (2026-07-06)

The `platforms/hermes/agent-skills/.../sdd-orchestrator` skill described the obsolete
v3.2 review + flow model the engine abandoned. `SKILL.md` corrected: persona model →
point at `framework/governance/REVIEW_CREWS.yaml` (9 weighted crews) + one illustrative
BRD crew + `framework/playbooks/`/LAYER-PLAYBOOKS-001 cross-link; the superseded
"8-category weighted-deduction" chairperson formula → the current weighted-average of
crew `lens_score`s capped by unresolved P0/P1 (per `review/review_scoring.py`); the wrong
"All 15 required BRD sections" list → point at `BRD-TEMPLATE.yaml`; the "4-persona" counts
→ 5-lens crews; stale `/opt/data/ucx_framework/.venv` MCP paths → `/path/to/python`; "SDD
v3.2" pins dropped. Two **loaded** governance files carrying the abandoned
Lite/Standard/Full depth-tier model (`governance/GOVERNANCE_RULES.md` §7 + the primary-load
`references/governance-load-protocol.md`) → the current single-path layer model
(necessary-upstream contract; MVP → PROD → NEW MVP). Doc-accuracy only — no engine change,
no `framework/` change (no GATE-SPEC, no re-vendor). D-0053. Deferred backlog: the
cosmetic v3.2 string residue, the hand-vendored `references/` copies (D-0013), and the
element-ID SHA-256 residue (PROVISIONAL-IDS-002).

### Fixed — H-14 PR 2: the plugin review lens honors the strip MUST via a disregard instruction (plugin 0.23.0 → 0.23.1; GD-05 fallback) (2026-07-06)

The plugin's agentic review lens reads the artifact directly, so it de-anchors from the
author self-assessment score by an explicit disregard instruction (GD-05's constrained
fallback — it cannot physically strip). Added across every anchored lens path: the 9
`doc-*-audit` fan-out briefs + strip sections (both modes; `doc-chg-audit` bespoke), the
9 `doc-*-fixer` inline lens briefs, `review-team`, and `traceability-auditor`. Both
platforms now satisfy the strip MUST (Hermes physical removal, plugin disregard
instruction). Plugin PATCH `0.23.1`; D-0052 (implements GD-05); closes H-14. 160
conformance green.

### Changed — GD-05: the author-self-claim strip MUST gains a disregard-instruction fallback for engines whose lens reads the artifact directly (framework spec 0.32.7 → 0.33.0) (2026-07-04)

**Framework governance decision (GD-05), ratified on merge.** `REVIEW_TEAM.md`
§"Strip author self-claim" previously named one mechanism ("the brief that goes to the
lens has the stripped body"), which presumes the engine controls the lens input — true
for Hermes (physical strip, D-0051) but not for the Claude Code plugin, an all-LLM
engine whose lens reads the artifact directly (H-14). GD-05 keeps the de-anchor
requirement unchanged and sanctions a **second, weaker compliance mechanism**, selected
by a structural fact about the engine:

- **Primary (physical removal):** an engine that **curates the lens input** MUST strip
  the fields from the body the lens receives (Hermes — unchanged).
- **Constrained fallback (disregard instruction):** where **the lens reads the artifact
  directly** (handed a path / shares the reading context), the engine MUST include a
  strong instruction in the lens brief that the lens not read, cite, or weight the
  fields when forming its `lens_score`. Permitted **only** under that reads-directly
  condition.

Additive standard clarification: SemVer **minor** `0.32.7 → 0.33.0`, change-level
**C2**. `REVIEW_TEAM.md` re-vendored to the plugin bundle; FSV pins → `0.33.0`. The
plugin's implementation of the fallback (its lens briefs) follows in the H-14 plugin PR.
See GD-05 in `framework/governance/DECISIONS.md`.

### Fixed — HERMES-REVIEW-CONTENT-DELIVERY: the review lens now receives the document body (Hermes review was content-blind) (hermes 0.6.0 → 0.7.0; no framework change) (2026-07-04)

Hermes's API-path LLM review never received the artifact body — the prompt was
persona + template + rules + metadata only, the executor a pure completion, and no
system prompt carried the body. The lens scored a document it had never read. Fixed at
the shared builder (`assemble_project_review_prompt`): inline a `## Document to Review`
block from the per-persona `included_sections`, deduping the template's own
`[PASTE … CONTENT BELOW]` placeholder, so every review path delivers the body. Folded
the author-self-claim strip into `run_project_review_build` — it was **inert** in
`0.6.0` (it mutated section content that never reached the LLM) and only now, with the
body inlined, actually removes the anchor. No new token accounting (the included body
was already counted). Discovered while implementing the single_pass strip (#242, now
superseded). Hermes MINOR `0.6.0 → 0.7.0`; D-0051 (corrects D-0049). 511 Hermes + 160
conformance tests green.

### Added — HERMES-REVIEW-CALIBRATION (H-6.1 + H-6.2): no-findings rationale cap + strip author self-claim (hermes 0.5.1 → 0.6.0; no framework change) (2026-07-04)

Two FRAMEWORK-CLEANUP-001 "PR-B heart" review-quality deltas brought to Hermes's
team-mode review path as consumer-side enforcement — both contracts already exist in
`framework/governance/REVIEW_TEAM.md` + the injected playbooks, so no framework
change.

- **No-findings rationale (H-6.1).** `persona_output_parser.py` captures a lens's
  `no_findings_rationale`; `review_scoring.score_review` caps a lens scoring 100 with
  zero findings and no rationale to 95, surfacing a `STRUCTURE-RAT-001` advisory.
  Also fixes a latent parser bug: a clean `findings: []` output previously fell to a
  `fallback` P1 with `lens_score=None`, dropping the lens from `lens_scores` (which
  lowered coverage and made the cap unreachable). The parser now returns a successful
  empty result that preserves the score.
- **Strip author self-claim (H-6.2).** `_strip_author_self_claim` redacts
  `*_ready_score` / `*_score` / `readiness_score` / `audit_score` assignment lines
  from each `SourceSection.content` once before fan-out (in-prompt only; on-disk
  artifact untouched) — the anchor-effect fix.

H-6.3 (fixer-introduced regression detection) stays deferred: Hermes's saga is
single-pass, so there is no iter-(N-1) to compare. Hermes MINOR `0.5.1 → 0.6.0`;
D-0049; 508 Hermes + 160 conformance tests green.

### Fixed — HERMES-SAGA-JOURNAL-CONFORMANCE (H-12): real Hermes saga journals conform to saga.schema.json; add `09_CHG` to the schema enum (framework spec 0.32.6 → 0.32.7; hermes 0.5.0 → 0.5.1) (2026-07-03)

Hermes's **real** saga journal (serialized from `SagaRunState` via `asdict`) was
missing 4 `saga.schema.json`-required fields — `artifact_id`, `layer`, `iteration`,
`transitions` — and never recorded `transitions` at all. The Phase-1 conformance
guard validated only hand-authored fixtures (written *with* those fields), so the
"both platforms' saga journals conform to the shared schema" parity claim (D-0031)
was aspirational for Hermes, not enforced against real output.

- **`SagaRunState`** (`saga_models.py`) gains `artifact_id`/`layer`/`iteration`/
  `transitions` (all defaulted → backward-compatible).
- **`saga_journal.py`** now records schema-shaped transitions — `create_saga_journal`
  seeds `{ts, from: null, to: PREPARED, scope: run}`; `update_run_status` appends a
  `scope: run` entry on each successful status change; `set_branch_state` appends a
  `scope: branch:<persona>` entry when a branch status changes. Each entry carries
  exactly `{ts, from, to, scope}`. `_to_run_state` roundtrips the new fields.
- **Orchestrator** derives `layer` from the **required** `doc_type` via
  `normalize_layer(layer or doc_type)` (not the optional `--layer`, whose default is
  `None`), so the default invocation still emits a schema-valid `layer` (H-12 F1).
- **Framework:** added `"09_CHG"` to the `saga.schema.json` `layer` enum so CHG
  review journals validate — a framework PATCH (GATE-SPEC applies; re-vendored to the
  plugin bundle).
- **Conformance:** new `SagaRealJournalConformance` validates a **real** Hermes
  journal (driven through the actual journal functions, for a lifecycle layer, the
  `--layer`-omitted path, and a CHG run) — the guard that would have caught H-12.

Framework spec PATCH `0.32.6 → 0.32.7`; Hermes PATCH `0.5.0 → 0.5.1`. D-0048; closes
H-12. 160 conformance + Hermes saga tests green.

### Added — HERMES-PARITY-PHASE-3: 8-layer playbook coverage (verified) + CHG crew parity (hermes 0.4.0 → 0.5.0; no framework change) (2026-07-03)

Phase 2's playbook injection is layer-agnostic, so all 8 lifecycle layers already
inject their playbooks — now locked in by a regression test over every crew lens.
Added the `chg` review crew to `persona_mappings.yaml` + removed the
`HERMES_DEFERRED_LAYERS` whitelist so the crew-coverage test enforces CHG. Crew-map
parity only; a live/sanctioned CHG saga review (schema `09_CHG` + dispatch) is a
deferred follow-on. Hermes MINOR; no framework spec change. D-0047; 497 Hermes + 157
conformance tests green.

### Added — HERMES-PARITY-PHASE-2: Hermes playbook injection for BRD+PRD (hermes 0.3.0 → 0.4.0; no framework change) (2026-07-03)

Hermes's review saga now injects the per-`(layer,lens)` playbook into each crew
lens's branch prompt (BRD+PRD), enforces the `check:` citation floor (discard
uncited on the LLM path), and emits `verdict.playbook_coverage` — closing the
load-bearing playbook-injection gap (H-4) for the first two layers. New
`playbook_loader.py` (crew-membership-keyed, so non-crew branch personas
`fact_checker`/`chairperson` are exempt, not failed) + byte-identical vendor of the
plugin's `finding_filter.py` (drift-guarded); `check` threaded parser → reducer →
verdict. Hermes MINOR bump; no framework spec change (playbooks pre-exist). Other 6
layers + CHG + `prompt_only` mode are Phase 3. D-0046; 496 Hermes + 157 conformance
tests green.

### Fixed — HERMES-PARITY-PHASE-1: Hermes saga state-machine conformance + enforced parity test (no version change) (2026-07-02)

Hermes's saga `_ALLOWED_TRANSITIONS` was missing the spec's `PARTIAL_TIMEOUT`
break-circuit state; added it so Hermes's table equals `REVIEW_SAGA.md` and the
plugin's `saga_driver.py`. New shared conformance test
`tests/conformance/test_saga_lifecycle_parity.py` (+ `fixtures/saga/`) enforces
**both** platforms' transition tables against the spec and validates a sample
journal from each runner against `saga.schema.json` — a test `docs/PARITY.md`
previously over-claimed already existed. No framework spec change and no Hermes
version bump (Phase 1 makes the state machine *accept* the transition; the
orchestrator break-circuit *exercise* + resume is Phase 1b). Corrected the stale
`HERMES-BACKLOG.md` premise (Hermes already has team-mode; the 0.32.x arc is
auto-satisfied). D-0045.

### Changed — P3 docs sweep: INDEX-UPSTREAM-RESIDUE + ENG-PLATFORM-ADR-TIMING + D54-F12-AGENTIC-ANTIPATTERNS; framework spec 0.32.5 → 0.32.6 (2026-06-30)

Three template clarifications, batched (no behavior change):

- **INDEX-UPSTREAM-RESIDUE** — corrected the 5 stale cumulative `Upstream:` lines in
  the `EARS/BDD/ADR/TDD-00` index templates to the necessary-upstream contract
  (matching the already-correct SPEC-00/PRD-00). Template-side only — the example
  corpus has no layer index, so the wholesale regen does not touch this (an earlier
  banner/runbook mischaracterized it as corpus-side; corrected).
- **ENG-PLATFORM-ADR-TIMING** — reworded the platform-BRD ADR-timing guidance
  (architectural decisions are *decided* before the PRD = provenance; the ADR
  *documents* are still authored in-sequence so they carry the full upstream chain)
  and added the platform-flow exception to `PRD-TEMPLATE` (a platform PRD MAY cite
  already-decided ADR numbers).
- **D54-F12-AGENTIC-ANTIPATTERNS** — added an agentic FAIL/PASS pair to BRD and PRD
  `_antipatterns` distinguishing business/product value from agent-pipeline
  architecture (belongs in ADR/SPEC).

PATCH 0.32.5 → 0.32.6; conformance green; bundle re-vendored.

### Added — Corpus-regeneration runbook (docs; no spec change) (2026-06-30)

`plans/CORPUS-REGEN-RUNBOOK.md` — founder-runnable procedure for the wholesale
example-corpus regeneration after framework-spec changes (needs a live plugin CLI).
Leverages `tests/ACCEPTANCE.md` (driver + `--promote`); adds the
post-framework-change trigger, a G1–G5 verification gate, and the deferred
corpus-remediation backlog it closes (16 COV02 orphans, `CORPUS-REFGRAN-RECASCADE`,
`CORPUS-PRD-TH-RES`, `INDEX-UPSTREAM-RESIDUE` corpus-side). `plans/HANDOFF.md`
updated to the session-wrap state (P3 items 2 & 3 + the STRUCT01-INDEX-EXEMPTION
bugfix shipped; regen runbook delivered).

### Added — ENG-BRD-SKETCH-ROADMAP: project-init roadmap in the BRD-00 index + trace-inert sketch sub-form; framework spec 0.32.4 → 0.32.5 (2026-06-30)

Authoring only `BRD-01` plus index one-liners left whole-project scope
under-specified before cycle 1 (Engramory #1). Made the `BRD-00` index "Planned
BRDs" table the **roadmap home**: extended it with cycle / target-PROD / `@depends:`
/ status (`Planned | Sketch`) columns and a usage preamble; added a "Project
initiation: enumerate the roadmap" subsection to `01_BRD/README.md` defining a
**Sketch** as a trace-inert planned row (carries only `BRD-NN` + `@depends:`; no
element IDs; not in the `@`-tag graph; ignored by forward coverage — and `@depends:`
is not a trace tag, so referencing a not-yet-authored planned row never trips
TRACE-RES-001); cross-referenced from `BRD-TEMPLATE.yaml`'s `document_control`
guidance. Docs-only. A *standalone* scope-only `status: Sketch` BRD **file** stays
deferred (it would fail required-section lint as an instance BRD). Builds on
STRUCT01-INDEX-EXEMPTION (D-0043) which made the BRD-00 index free of STRUCT01.
PATCH 0.32.4 → 0.32.5; conformance green; bundle re-vendored. D-0044.

### Fixed — STRUCT01-INDEX-EXEMPTION: `sdd_doc_lint` recognizes index/registry docs so they lint clean (tooling; no spec change) (2026-06-30)

`sdd_doc_lint`'s index exemption (STRUCT01 required-sections + the trace-resolution
skip) read a **top-level** `artifact_type` ending in `-INDEX`, but the 8 layer index
templates declare `artifact_type` under `custom_fields` (6 with a bare value) and the
IPLAN-00 registry is a `.yaml` with no `---` frontmatter — so the exemption never
fired and a consumer's copied index threw STRUCT01 errors (BRD-00: 17). The `-INDEX`
marker also self-tripped the ID02 doc-id scan. Fixed in the linter: a filename-based
`_is_index_doc(rel, fm)` (`<TYPE>-00_index`, reliable for all 8 incl. the `.yaml`) used
in both exemptions, plus the ID02 scan skips `-INDEX` tokens. No template/`framework/`
change → no spec bump (precedent: #198/#200). Vendored copies re-synced byte-identical;
new conformance guard `test_index_template_lint.py` (lints the 8 real templates → 0
STRUCT01 / 0 `-INDEX` ID02); 316 conformance+unit green; example-corpus lint unchanged.
D-0043.

### Changed — BL-READY-SCORE-ADVISORY: mark `*_ready_score` / `target_score` advisory in the 7 layer templates; framework spec 0.32.3 → 0.32.4 (2026-06-30)

The `<next>_ready_score` (`document_control`) and `target_score` (`health_score`)
fields shipped in every layer template (BRD…TDD) read as a **required gate**, but
the score is **advisory** — auditor-lens-computed, never hand-authored; the
deterministic `sdd_doc_lint` floor is the real gate. A blank score made a finished
artifact look half-done (BeeLocal #56). Marked the **14 score fields** advisory via
an inline `#` comment per score line plus one `_note:` per `health_score` block
(D-0042), **and reworded 15 contradicting `_guidance` prose lines** across the same
templates that still framed the score as "required before generation" / a "quality
gate" (caught by ai-review on the impl PR — Pass 3). **No rubric / no offline
scorer** (author Q4 — that would contradict D54-F03; the audit skill IS the rubric).
All 7 layer templates reconciled uniformly (IPLAN/08 carries neither field). PATCH
bump 0.32.3 → 0.32.4; conformance green; bundle re-vendored byte-identical.

### Changed — BeeLocal P3 docs-clarification sweep (BL-SIZE-UNITS, BL-BRD-SET-WORDING, BL-VENDOR-NAME-SCOPE); framework spec 0.32.2 → 0.32.3 (2026-06-29)

Three small wording clarifications from BeeLocal consumer feedback, batched (no
behavior change):

- **BL-SIZE-UNITS** — `AUTHORING_STYLE.md` now states the words-vs-tokens
  relationship: section/document targets are in **words** (style guidance); the
  50 000-**token** figure is the document **split trigger**.
- **BL-BRD-SET-WORDING** — `01_BRD/README.md` reworded "each BRD = one cycle" →
  "each BRD **set** (platform + feature BRDs, linked by `@depends:`) = one
  iteration cycle", with a parent/child tree example (the prior wording caused
  real BeeLocal planning confusion).
- **BL-VENDOR-NAME-SCOPE** — `BRD-TEMPLATE.yaml` `adr_topics` guidance clarifies
  the "no vendor names" rule applies to the topic title/`business_driver`
  (stay business-level); vendor names ARE allowed in `recommended_selection`
  (the decision record).

PATCH bump 0.32.2 → 0.32.3; 314 conformance+unit green; bundle re-vendored
byte-identical.

### Changed — ENG-IPLAN-REGISTRY-README: document the IPLAN index-registry vs document schema; framework spec 0.32.1 → 0.32.2 (2026-06-29)

The `IPLAN-00_index.yaml` (`iplan-registry`, no `document_control`) vs
`IPLAN-NN_*.yaml` (`iplan-document`) schema distinction was undocumented in the
layer README, so a naive "validate every `IPLAN-*.yaml`" glob misfired on the
registry (Engramory feedback item 3). Added an "Index registry vs document
schema" section to `08_IPLAN/README.md` noting the two schemas and that
`sdd_doc_lint` already exempts `artifact_type: *-INDEX`. Behavior unchanged —
docs-only. PATCH bump 0.32.1 → 0.32.2; 314 conformance+unit green; bundle
re-vendored byte-identical.

### Changed — ENG-SPEC-IPLAN-ID-EXEMPTION-NOTE: cross-reference the element-ID exemption in the SPEC/IPLAN templates; framework spec 0.32.0 → 0.32.1 (2026-06-29)

The element-ID exemption for SPEC (§3/§5) and IPLAN (§2/§4) was documented only
in `governance/ID_NAMING_STANDARDS.md` — an author reading just the template
might over-assign IDs (noise) or worry they're missing required ones (Engramory
feedback item 4). Added a one-line cross-reference `_guidance` note to
`SPEC-TEMPLATE.yaml` (interfaces/behavior) and `IPLAN-TEMPLATE.yaml`
(file_manifest/implementation_contracts) pointing to the standard's
"Element-ID exemptions" section. The exemption itself is unchanged (the standard
stays authoritative). PATCH bump 0.32.0 → 0.32.1; 314 conformance+unit green;
bundle re-vendored byte-identical.

### Added — REUSE-MANIFEST-001: first-class reuse / satisfied-by-reference; framework spec 0.31.0 → 0.32.0 (2026-06-29)

Lets a brownfield project **reuse an existing upstream artifact** instead of
re-authoring it (D54-F02, CONSUMER-FEEDBACK-001 PR-5 — the make-or-break
brownfield capability). Plan [`plans/REUSE-MANIFEST-PLAN.md`](plans/REUSE-MANIFEST-PLAN.md)
(3 review passes).

- **`reuse: {state: referenced, target: <doc_id|path>@<commit>}`** frontmatter
  wires the stubbed `CoveredState.SATISFIED_BY_REFERENCE`. A referenced doc's
  elements are **exempt from `COV01`/`COV02`** (reused as-is, not realized here);
  one **`REUSE01`** advisory per referenced doc keeps every reuse visible.
- **`REUSE02`** target contract — the target must be in-repo + commit-pinned
  (7–40 hex); a URL, unpinned, or unresolvable target is an error (live URLs are
  `@discoverability` hints only).
- **Full-prefix rule** — a referenced doc's upstream lineage must also be in-repo
  - `referenced`, so its outbound `@`-tags resolve with no trace-engine change;
  an absent upstream stays a (correct) `TRACE-RES-001` finding.
- Reuse contract documented in `governance/TRACEABILITY.md` (incl. the no-free-≥90
  readiness rule — skill enforcement is a follow-on). Framework MINOR
  **0.31.0 → 0.32.0**; 314 conformance+unit green; corpus baseline unchanged;
  vendored byte-identity intact.

### Added — PROVISIONAL-IDS-001: manual-mode provisional IDs + normative hash algorithm; framework spec 0.30.0 → 0.31.0 (2026-06-29)

Lets manual authors (no plugin generator) produce linter-valid element IDs and
canonicalize them by hand (D54-F01, CONSUMER-FEEDBACK-001 PR-4). Plan
[`plans/PROVISIONAL-IDS-PLAN.md`](plans/PROVISIONAL-IDS-PLAN.md) (3 review passes).

- **Normative hash algorithm** in `ID_NAMING_STANDARDS.md` — the exact input
  string `"{doc_id}:{section_id}:{title}:{description}"`, `[:4]` truncation, and
  4→8 collision rule (previously only in template `_guidance`), so a by-hand hash
  is byte-identical to the plugin's. Plus the provisional-vs-canonical convention.
- **`id_state: provisional|canonical`** frontmatter flag (default canonical;
  back-compatible) — a `provisional` doc gets one doc-level **`PROV01`** advisory
  to canonicalize before downstream layers cite its IDs. `state` governs ID
  stability, not coverage — provisional elements are still gated normally.
- **Provisional ID form** — section-ordinal hex (`0001`); templates' placeholder
  field is now `0000` (regex-valid) instead of the `ELEM_FORM`-invalid `xxxx`.
- **`PH01` lowercase fix** — `(?<!\.)\bx{3,}\b` flags a bare lowercase `xxxx`
  (the uppercase-only `\bXX+\b` blind spot) while leaving a full-element-id hash
  segment to ID03 (no double-report).
- All 8 layer templates gain `id_standard.state: canonical`. Framework MINOR
  **0.30.0 → 0.31.0**. 306 conformance+unit green; corpus baseline unchanged;
  vendored byte-identity intact.
- **Deferred to PROVISIONAL-IDS-002:** the reference-aware `rehash` subcommand
  (auto-canonicalization + `rehash --check`).

### Fixed — tooling backlog: changelog-entry test convention + SKILL_AUTHORING bump straggler (2026-06-29)

Two recurring tooling papercuts (no version impact):

- **`tests/release/test_changelog_entry.py`** (`RELEASE-CHANGELOG-TEST-CONVENTION-GAP`)
  — was asserting a top-level `## [X.Y.Z]` heading while the repo nests the
  current version under `## [Unreleased]` as a `### … framework spec X → Y`
  subsection, so it was latently RED at HEAD (invisible only because CI doesn't
  run `tests/release/`). Now accepts the version in either a released top-level
  heading or an Unreleased subsection heading.
- **`tools/bump_version.py`** (`BUMP-SKILL-AUTHORING-CHECKLIST-STRAGGLER`) — now
  sweeps the backtick-wrapped `framework_spec_version: "X"` in
  `SKILL_AUTHORING.md`'s §6 checklist that the column-anchored `bump_fsv` regex
  missed every bump (left stale at `0.27.0`, 3 bumps behind); corrected to
  `0.30.0` and auto-maintained henceforth.

### Added — ELEMENT-COVERAGE-001: element-level COV01/COV02 coverage; framework spec 0.29.1 → 0.30.0 (2026-06-29)

Upgrades the coverage lint gates from **document-level** to **element-level**
reach (the deferred payoff of the CFB-PR-2 coverage engine, unblocked by
REFGRAN01 + the YAML-BDD arc making citations element-precise). Plan
[`plans/ELEMENT-COVERAGE-PLAN.md`](plans/ELEMENT-COVERAGE-PLAN.md) (5 review
passes — 1 self + 4 independent).

- **`COV02` (backward) now binds per element** — each declared EARS/BDD element
  must be cited element-level by a doc in its **realizing set**, not merely have
  its host doc reach the layer. This catches the **16 orphaned BDD scenarios**
  in the example corpus (declared in BDD-01 but cited by no SPEC/TDD element)
  that doc-level COV02 could not see. Warnings in `build` (corpus lint exit code
  unchanged), errors in `gate-code`.
- **`COV01` (forward) now binds per element** — each AUTHORED BRD FR element must
  be cited by a PRD (then the host BRD's SPEC + IPLAN doc-reach is retained), one
  finding per FR (precedence: no-PRD → no-SPEC → no-IPLAN). 0 new findings on the
  real corpus (all 4 BRD-01 FRs are PRD-cited element-level).
- **Curated `REALIZING_LAYERS` map** (`tools/sdd_doc_lint`): BDD→{SPEC,TDD},
  EARS→{BDD,SPEC,TDD}, BRD-FR→{PRD} — deliberately NOT the registry single-hop
  `downstream` (which routes BDD→ADR); ADR excluded (decides, doesn't realize).
  The one-hop model avoids false-blocking EARS realized via BDD (D-0039).
- SPEC-00 `## Coverage` section updated to the element-level contract; conformance
  `test_coverage_engine.py` re-baselined to assert the 16 orphans; new unit cases
  (orphan-sibling, EARS-via-orphan-passes, ADR-only-not-realized, FR-uncited-by-PRD).
- Framework MINOR bump **0.29.1 → 0.30.0** (gate semantics change; GATE-SPEC).
  295 conformance+unit green; vendored byte-identity intact.

### Changed — YAML-BDD-SCHEMA PR-3b: 04_BDD playbook bodies + QUICK_REFERENCE Gherkin → YAML; framework spec 0.29.0 → 0.29.1 (2026-06-29)

Deferred governance polish completing the YAML-BDD arc. PR-3 bumped the six
`framework/playbooks/04_BDD/*.md` lens playbooks' version frontmatter but left
their bodies describing Gherkin; this PR rewrites the bodies to the structured
`scenarios:` YAML model.

- **`framework/playbooks/04_BDD/{qa_lead,auditor,chaos_engineer,security_engineer,tech_lead,operator}.md`**
  — reasoning frames + evidence checks re-expressed against the YAML model:
  Gherkin steps → `given`/`when`/`then` phase-list entries; Gherkin tags →
  element-level `ears:` lists (REFGRAN01); Gherkin-lint → `BDD-SCHEMA-001`
  structural check (required fields, `type`/`priority` enums); feature-file
  Document Control → the `document_control:` block. The auditor's
  Gherkin-lint/step-catalog checks (C2/C4) recast to `BDD-SCHEMA-001`; the
  tech_lead's Gherkin tag-placement check (C5) recast to scenario-scoped
  attribute placement (`feature:` carries no `ears`, D-3). Each scenario's
  `id:` copied verbatim on migration (downstream `@bdd:` stability).
- **`framework/QUICK_REFERENCE.md`** — ADR-Ready gate criterion "Gherkin
  quality" → "scenario quality".
- **Spec bump 0.29.0 → 0.29.1** (PATCH — `framework/**` change trips
  GATE-SPEC): `bump_version.py` propagated 104 `framework_spec_version`
  declarations, both platform FSV pins, the plugin README spec strings, the
  release-metadata hard-pin, and re-vendored the bundle byte-identical.
- **Verification:** 148 conformance + 142 unit green; vendored byte-identity
  intact; corpus baseline unchanged (1× TH-RES-001, 5× REFGRAN01, 6× STY02 —
  no new findings). Spec-tier → human sign-off.

### Changed — YAML-BDD-SCHEMA PR-5: `doc-bdd*` skills author the YAML form; plugin 0.22.0 → 0.23.0 (2026-06-28)

Completes the YAML-BDD arc on the authoring side. The four `doc-bdd*` plugin
skills (`doc-bdd`, `-audit`, `-fixer`, `-autopilot`) rewritten to author +
validate the structured YAML scenario model instead of Gherkin `@`-tags
(per-stream detail in [`platforms/claude-code-plugin/CHANGELOG.md`](platforms/claude-code-plugin/CHANGELOG.md)).
Plugin MINOR **0.22.0 → 0.23.0** (no framework change). 148 conformance +
plm_lint clean + 142 unit green; the 5-section template-alignment contract
preserved (content-only edits).

### Changed — YAML-BDD-SCHEMA PR-4: example corpus BDD-01 migrated to YAML scenarios (2026-06-28)

The corpus payoff — the framework migrates its own showcase artifact end-to-end
(machine-produced by the transcoder; never hand-edited).

- **`examples/url-shortener/docs/04_BDD/BDD-01.md`** — Gherkin → structured YAML
  `scenarios:` block via the hardened transcoder. 31 scenarios; each
  `@scenario-id` **copied verbatim** so all **16 downstream `@bdd:` citations
  still resolve** (V4 ID-stability); inline `@threshold:` preserved; `#`
  comments lifted to `spec_trace:`/`notes:`. **Drops the 2 BDD REFGRAN edges:
  corpus REFGRAN 7 → 5** (the remaining 5 are SPEC/TDD/IPLAN `@adr`/`@tdd` —
  `CORPUS-REFGRAN-RECASCADE`). New corpus baseline: 1 TH-RES, 5 REFGRAN, 6 STY02.
- **`tools/gherkin_to_bdd_yaml.py`** — hardened for the real corpus:
  fence-classified placement (feature → §2, scenarios → §3), Document Control
  reference-row strip, empty category sub-heading collapse. +1 multi-fence test
  (`tests/unit/test_gherkin_to_bdd_yaml.py`, now 7).
- Acceptance `BDD-01_golden` fixtures are already non-Gherkin → no change.
- **Verification:** 290 unit + conformance green; acceptance unchanged (the 3
  failing SPEC `@adr` REFGRAN cases are pre-existing `CORPUS-REFGRAN-RECASCADE`,
  not BDD). Not a `framework/` change → no version bump.

### Added — Framework Spec 0.27.0 → 0.28.0: GD-04 ratifies IPLAN-ASSURANCE L1 (2026-06-28)

- **`governance/DECISIONS.md` — GD-04:** ratifies **IPLAN-ASSURANCE L1** at
  `iplan/v0.4.0` as an aidoc-flow conformance requirement (the GATE-SPEC ratification
  the standard's `GOVERNANCE.md` points to). A consumer declaring `assurance ≥ L1`
  MUST verify the initiator signature over the canonical IPLAN (with `intake_control`
  excluded) against an authorized-initiator keyring before approval/execution (§2 +
  §9 R1–R3). L0 stays the default; L1 is opt-in. The §3 attestation predicate is
  **IPLAN-native** (R3, amended — SLSA provenance subject-inverts the IPLAN); first
  conformant producer is iplanic A4 / D-0109. L2 + REQUIRED witness are future tiers,
  not ratified here.
- **Bump:** `framework/VERSION` 0.27.0 → 0.28.0; both platforms'
  `FRAMEWORK_SPEC_VERSION` = `0.28.0`; 104 `framework_spec_version` declarations
  synced; plugin bundle re-vendored (byte-identity); conformance green. Recording a
  `GD` is itself a framework-spec change → GATE-SPEC (per GD-01).
- **Merge precondition:** founder tags `iplan/v0.4.0` on `aidoc-flow-iplan-standard`
  first. Tracking: `aidoc-flow-operations` `ops/iplans/IPLAN-0028`.

### Changed — Framework Spec 0.28.0 → 0.29.0: YAML-BDD-SCHEMA PR-3 (BDD template + schema) (2026-06-28)

Third implementation increment — the **framework-spec** change (GATE-SPEC: the
template restructure carries the MINOR bump). Realigns the BDD layer's normative
template + governance with the YAML-native scenario model (D-0038).

- **`framework/layers/04_BDD/BDD-TEMPLATE.yaml`** — `scenario_structure.scenarios`
  restructured from a **category-dict** (success/error/…) to a **flat list with a
  `type:` discriminator** matching the normative schema; each scenario is a
  structured mapping (id/name/type/priority/element-level `ears` list/given-when-
  then phase lists/optional spec_trace+notes+outline+examples) — no Gherkin
  `@`-tags. `feature_definition` → a `feature:` YAML block (name/description/
  background) carrying **no `ears`** (coverage = union of scenarios, D-3).
  `document_control` drops the `ears/prd/brd_reference` rows.
- **`framework/layers/04_BDD/BDD-00_index.TEMPLATE.md`** — trace convention +
  checklist + "create a BDD" steps updated from `@ears` tags / "valid Gherkin"
  to the structured `ears:` list / YAML scenario schema.
- **Governance reconciliation:** `governance/TAG_SYNTAX.md` (BDD carries `ears:`
  as structured YAML, not an `@`-tag; the no-space Gherkin note + BDD row +
  pipe-container example updated) and `governance/ID_NAMING_STANDARDS.md` GD-03
  (new "BDD carrier" clause — element-level `ears` enforced by REFGRAN01 +
  BDD-SCHEMA-001; downstream still cites `@bdd:` element tags).
- **Framework MINOR bump 0.28.0 → 0.29.0** via `bump_version.py` (both
  `FRAMEWORK_SPEC_VERSION` pins, 104 skill/playbook frontmatter declarations,
  plugin README, bundle re-vendor, version-ref fanout). 148 conformance + 141
  unit green; example corpus unchanged vs baseline.
- **Deferred to PR-3b (PATCH bump):** `QUICK_REFERENCE.md` + the `04_BDD/*.md`
  playbooks (peripheral guidance).

### Added — YAML-BDD-SCHEMA PR-2: `sdd_doc_lint` dual-mode BDD parse path (2026-06-28)

Second implementation increment. The linter now reads a migrated BDD doc's
trace from its structured ``scenarios:`` YAML block; a doc with no scenarios
block falls back to the legacy Gherkin ``@``-tag path (dual-mode), so the
still-Gherkin example corpus is byte-for-byte unaffected.

- **`build_edge_graph`** — for a BDD doc with a ``scenarios:`` block, synthesises
  one upstream edge per scenario ``ears`` token **verbatim** (doc-form included),
  with ``cited_doc = doc_id_from_token(token)``. So **REFGRAN01** fires on a
  doc-form ``ears`` while COV01/COV02 see BDD↔EARS lineage identically (Pass-2
  LB-3 / Pass-3 finding 2). Scenario ``id`` declarations self-register via the
  existing ``_ELEM_ID`` scan.
- **`_check_trace_resolution` (TRACE-RES-001)** — resolves scenario ``ears``
  tokens against the corpus (the ``ears:`` list carries no ``@`` for the legacy
  scan to see).
- **`lint_text` TAG01** — BDD ``required_tags: [ears]`` is satisfied from the
  parsed scenario ``ears``.
- **`BDD-SCHEMA-001`** (new) — structural validation only: malformed block,
  non-mapping scenario, missing required field
  (id/name/type/priority/ears/given/when/then), or invalid type/priority enum.
  Element-level ``ears`` granularity stays REFGRAN01's job — no double-report.
- Re-vendored byte-identical into both platform copies.
- **Tests:** `tests/unit/test_bdd_yaml_mode.py` (11) — REFGRAN verbatim-edge
  behaviour, TRACE-RES, TAG01, BDD-SCHEMA-001, no-double-report, and the legacy
  dual-mode fallback. Existing `test_ref_granularity.py`/`test_coverage_engine.py`
  legacy fixtures unchanged (supplemented, not replaced — Pass-3 finding 1).
- **Verification:** 141 unit + 148 conformance green; example corpus unchanged
  vs baseline; end-to-end smoke — the PR-1 transcoder converts the real BDD-01
  (31 scenarios / 50 ears tokens) and this fork reads it with IDs verbatim.

### Added — YAML-BDD-SCHEMA PR-1: `_THRESHOLD` quote-fix + Gherkin→YAML transcoder (2026-06-28)

First implementation increment of the merged YAML-BDD-SCHEMA design
(`plans/YAML-BDD-SCHEMA-PLAN.md`, PR #197 / D-0038). Migrates BDD scenarios
toward a structured YAML block; this PR ships the two self-contained pieces.

- **`tools/sdd_doc_lint` `_THRESHOLD` regex** — tightened
  `@threshold:\s*([^\s|]+)` → `([^\s|'"]+)` so an inline `@threshold:` ending a
  quoted YAML scalar (`'… @threshold:PRD.01.x'`) no longer glues the closing
  quote into the value and false-fires **TH01** (YAML-BDD-SCHEMA Pass-2 LB-1).
  All-layer + regression-free (threshold values never contain quotes; corpus
  verified). Re-vendored byte-identical to both platform copies.
- **`tools/gherkin_to_bdd_yaml.py`** — new one-time migration transcoder
  (YAML-BDD-SCHEMA D-6). Parses a BDD doc's embedded Gherkin
  (feature/background/scenario outline/examples/multi-step/inline-threshold/
  `#` comments) into the structured YAML scenario model, **copying each
  `@scenario-id:` verbatim into `id:`** so the 16 downstream `@bdd:` citations
  stay stable. `# spec_trace:` → `spec_trace:`, other `#` comments → `notes:`.
- **Tests:** `tests/unit/test_threshold_quoted_scalar.py` (3),
  `tests/unit/test_gherkin_to_bdd_yaml.py` (6). Suite green (130 unit / 148
  conformance); example corpus unchanged vs baseline.
- **Continuity:** `plans/DECISIONS.md` D-0038 (plan D-1…D-6);
  `plans/HANDOFF.md` resume banner (PR-2 = the linter dual-mode fork is next).

### Changed — CI: pin callers to @ci/v1.3.0; drop pull_request_target from composition (IPLAN-0026 P8 + IPLAN-0027 P4; 2026-06-28)

- **`.github/workflows/composition.yml`** — pin `@ci/v1.2.0` → `@ci/v1.3.0`;
  trigger set reduced to `pull_request_review` + `workflow_run` only
  (drop `pull_request_target`). Activates Phase 2's friction-relief benefit
  on framework: composition no longer early-fires on PR open, and therefore
  no longer creates the stale-red FAILURE that branch-protection's rollup
  retained until a `skip-ai-review` label-cycle. Header refreshed
  (drops Phase-1 chicken-and-egg admission; references new force-fresh path).
- **`.github/workflows/ai-review.yml`** — pin `@ci/v1.1.6` → `@ci/v1.3.0`.
  Activates the R3 early-exit step in the v1.3.0 reusable. Saves ~$0.10-
  0.20 + ~2-3 min per redundant re-fire (label-cycle-retriggered ai-review
  after the App has already APPROVED at HEAD). Consumer caller shape
  unchanged.
- **Bundled release**: ci/v1.3.0 was tagged on aidoc-flow-ci main commit
  `3dcb0e8` after PRs #41 (IPLAN-0026 P7) + #42 (IPLAN-0027 P1) merged
  earlier today. This framework PR is the public-runner activation of
  both benefits in a single pin-bump cycle (operations PR #163 is the
  self-hosted-runner activation).
- **Chicken-and-egg on THIS PR**: BASE main's composition.yml caller
  still has `pull_request_target` (Phase-1 parallel-trigger shape), so
  this PR fires under the old triggers. After merge, every subsequent
  framework PR uses the post-v1.3.0 trigger set (no `pull_request_target`
  on composition). Same pattern as every prior v1.X.X bump per
  IPLAN-0026 §3 P4/P5.
- **Plans (in `aidoc-flow-operations`):**
  `ops/iplans/IPLAN-0026_composition-workflow-run-redesign.md` P8 +
  `ops/iplans/IPLAN-0027_r3-ai-review-early-exit.md` P4.

### Added — Framework Spec 0.26.0 → 0.27.0: REFGRAN01 ref-granularity enforcement (CFB-PR-3) (2026-06-27)

Enforces GD-03 (0.26.0): the deterministic lint that makes the coverage engine
element-precise. MINOR.

- **`sdd_doc_lint` (vendored): `REFGRAN01`** — flags an `@<layer>:` trace
  citation in document-level form (`TYPE-NN`) to an element-declaring layer
  (`@brd @prd @ears @bdd @adr @tdd`); `@spec`/`@iplan` exempt (element-ID-exempt).
  Reuses `build_edge_graph`'s edges (upstream-only; self-tags + downstream
  pointers excluded), so it fires only on genuine upstream trace citations.
  Run-mode severity (warning/`build`, error/`gate-code`); per-edge finding; runs
  unconditionally (a form rule, not the corpus coverage gate). No double-fire
  with `ID01`/`TRACE-RES-001`.
- **Spec:** `governance/TAG_SYNTAX.md` (new) — the `@`-tag form reference
  (per-layer punctuation, pipe-delimited cardinality, self-tag/downstream
  carve-outs), cross-referencing GD-03 / `ID_NAMING` (granularity) and
  `TRACEABILITY.md` (chain) without duplicating them. The layer templates that
  taught the doc-form upstream ref are reconciled to element-level:
  `BDD-00_index.TEMPLATE.md` (`@ears`), `SPEC-TEMPLATE.yaml` (`@adr`),
  `IPLAN-TEMPLATE.yaml` (`@tdd`), `PRD-TEMPLATE.yaml` (`@brd`) — self-tags and
  downstream references stay document-level (exempt).
- **Deferred:** the **corpus re-cascade** of the 7 doc-level tags (5 drop +
  2 convert, incl. the BDD Feature fan-out) needs the `doc-<layer>-fixer` skills,
  which aren't invocable in a framework-dev session — flagged as
  `CORPUS-REFGRAN-RECASCADE` (`FRAMEWORK-TODO.md`). `REFGRAN01` contributes
  **warnings only** in `build` mode (it does not raise the lint exit code); the
  corpus's pre-existing non-zero exit is the separately-tracked
  `CORPUS-PRD-TH-RES` (`TH-RES-001`) error, unrelated to REFGRAN. The
  element-level `COV01`/`COV02` upgrade + `BL-STATUS-SCOPE` remain named
  follow-ons.
- **Backward compatibility:** additive; `REFGRAN01` no-ops without upstream
  edges (single-file runs); existing corpora are warned, not blocked, in
  `build` mode.
- **Validation:** 269 unit+conformance green (`test_ref_granularity.py` +
  `test_coverage_engine` REFGRAN contract + the `TAG_SYNTAX` page guard);
  framework + both `FRAMEWORK_SPEC_VERSION` = `0.27.0`; vendored byte-identity.

### Added — Framework Spec 0.25.0 → 0.26.0: ref-granularity policy GD-03 (CFB-PR-3 prep) (2026-06-27)

Settles the tag-granularity policy that the CFB-PR-3 lint (`REFGRAN01`) will
enforce — a focused standard clarification before the enforcement PR. MINOR.

- **`governance/DECISIONS.md` — GD-03:** every `@<layer>:` **trace citation** to
  an **element-declaring** layer (`@brd @prd @ears @bdd @adr @tdd`) MUST be
  **element-level** (`TYPE.NN.SS.xxxx`), in all contexts — including the
  necessary-upstream / feature-level tag, not only inline body citations. A unit
  realizing multiple upstream elements pipe-delimits them; a whole-document
  dependency is stated in prose, never as a doc-level trace tag. `@spec:`/
  `@iplan:` stay document-level (element-ID-exempt); self-tags + downstream
  forward-pointers are exempt.
- **`governance/ID_NAMING_STANDARDS.md`** gains the normative "Reference
  granularity" clause (rationale: functionality is defined in elements, the
  document is a container; a doc-level ref discards that granularity).
- **Why a standalone policy PR:** the existing Tag-Format table already showed
  element-level forms, but did not state explicitly that the
  necessary-upstream/feature tag is also element-level — the gap that let the
  url-shortener BDD-01 Feature carry a coarse doc-level `@ears: EARS-01`, keeping
  the coverage engine document-level. Settling the policy first lets CFB-PR-3's
  `REFGRAN01` enforce a consistent, unambiguous rule.
- **Deferred to CFB-PR-3:** the `REFGRAN01` enforcement, reconciling the
  doc-form necessary-upstream examples in the layer templates, and the corpus
  re-cascade (fan-out the feature tags). **Backward compatible** — a standard
  clarification; no tooling behavior changes in this PR.
- **Validation:** conformance green; framework + both `FRAMEWORK_SPEC_VERSION` =
  `0.26.0`; vendored byte-identity intact.

### Changed — `.github/workflows/composition.yml`: pin `@ci/v1.0.5` → `@ci/v1.2.0` + add `workflow_run` trigger (IPLAN-0026 P5; Phase 1 mechanism only) (2026-06-27)

- Framework composition caller pin bumped from `@ci/v1.0.5` to
  `@ci/v1.2.0` (the IPLAN-0026 Phase-1 release on aidoc-flow-ci).
- **`workflow_run` trigger added** alongside existing
  `pull_request_target` + `pull_request_review` (parallel transition
  per IPLAN-0017 §3.4 + IPLAN-0026 §2.3 D2 migration discipline).
- **Phase 1 ships MECHANISM only.** Friction relief NOT yet delivered;
  Phase 2 (ci/v1.3.0, separate small IPLAN after empirical validation)
  drops `pull_request_target` + delivers the relief.
- **Chicken-and-egg:** BASE main pins v1.0.5; new `workflow_run`
  trigger only activates AFTER merge.
- **Plan:** [IPLAN-0026](https://github.com/vladm3105/aidoc-flow-operations/blob/main/ops/iplans/IPLAN-0026_composition-workflow-run-redesign.md)
  (operations PR #156, merged 2026-06-27 commit `44f4b5b`).
- **Next:** P6 empirical validation (1+ clean routine PR with new
  triggers on EITHER operations or framework) → P7+P8 Phase 2 cleanup.

### Added — Framework Spec 0.24.0 → 0.25.0: backward coverage gate `COV02` (CFB-PR-2b) (2026-06-27)

The backward half of the coverage engine (sub-PR 2b), the dual of 2a's forward
`COV01`. MINOR.

- **Tooling (`sdd_doc_lint`, vendored):** `_check_backward_coverage` (`COV02`) —
  every EARS/BDD requirement doc must transitively reach a SPEC or TDD doc
  downstream, else its requirements/scenarios are designed/tested by nothing.
  Document-level binding (PR-3 refines to element granularity). Gated to corpora
  with a real (non-`-00`) SPEC/TDD doc (the `-00` index signal, since SPEC/IPLAN
  docs declare no canonical elements); run-mode severity (warning/`build`,
  error/`gate-code`); wired into `lint_path` behind the existing
  `--skip-coverage-gate`.
- **Spec:** `layers/06_SPEC/SPEC-00_index.TEMPLATE.md` gains a normative
  `## Coverage` section (the doc-of-record for the backward contract — `COV02`
  is a structural lint code, not a formal gate-catalog entry, symmetric with
  `COV01`), and its stale cumulative `**Upstream**: BRD, PRD, EARS, BDD, ADR`
  line is corrected to the necessary-upstream form `EARS, BDD, ADR`
  (INDEX-UPSTREAM-RESIDUE for SPEC-00).
- **Deferred to PR-3:** element-level backward coverage, the EARS/BDD deferral
  signal, and remediating the orphaned corpus BDD scenarios element-level
  analysis surfaced.
- **Backward compatibility:** additive. The gate no-ops unless the corpus has
  reached a real design/test doc, so single-file `on_author` runs and
  pre-design cascades are unaffected; the example corpus is clean (0 `COV02`).
- **Validation:** 260 unit+conformance green (incl. `test_backward_coverage.py`
  - `test_coverage_engine.py` COV02 contract + the SPEC-00 section/Upstream
  guards in canonical + vendored). Plugin/Hermes product versions unchanged
  (independent streams).

### Added — CLAUDE.md: OPS-0062 AI agent auto-merge default rule (applies to ALL AI agents) (2026-06-27)

- **`CLAUDE.md`** new top-level section **"AI agent auto-merge default
  (OPS-0062)"** placed after the existing "Governance PR discipline
  (mandatory)" section. AI agents (Claude, Codex, Gemini, GitHub
  Copilot, etc.) opening PRs in this repository default to auto-watch
  - auto-merge when green; escalate to human at 10 attempts.
- **Canonical record** lives in operations `ops/DECISIONS.md` OPS-0062
  (full reasoning, scope, exceptions, reconciliation with the
  `auto_merge.repos` allowlist, session-boundary behavior, per-PR
  cumulative counter, visibility requirement). This CLAUDE.md section
  is the short-form rule + pointer.
- **Rollout from operations OPS-0062 source PR** (#152, merged
  2026-06-27 commit `dcc4692`). 7 sibling repos getting individual
  CLAUDE.md update PRs (this is one of them — framework).
- **Exceptions list** explicitly includes this repo's existing
  governance PR list (CLAUDE.md / `plans/PLAN-*.md` /
  `.github/ai-review/` / `.github/workflows/ai-review.yml`) so AI
  never auto-merges PRs touching those — preserves existing Rule 1 +
  Rule 2 discipline.

### Added — Framework Spec 0.23.1 → 0.24.0: forward-coverage engine (CFB-PR-2 2a-core) (2026-06-27)

Adds the forward/completeness half of traceability the framework lacked
(`trace_walk.py` is backward/transitive only). Engine-agnostic tooling + a
normative BRD-template rule + a governance cross-ref; MINOR.

- **Tooling (`tools/`, vendored linter):**
  - `sdd_doc_lint/trace_graph.py` — shared `@`-tag trace primitives (relocated
    from `tools/sdd_trace_graph.py` into the package so the vendored linter
    imports them; D-0036).
  - `sdd_doc_lint` gains the heading-context FR scanner (`scan_fr_elements`), the
    net-new bidirectional element edge-graph (`build_edge_graph`), the
    `covered_state` classifier + band parser (`CoveredState` / `parse_band` /
    `covered_state_of`), and the forward-coverage gate `COV01`
    (`_check_forward_coverage`) with run-mode severity (`--mode {build|gate-code}`)
    - `--skip-coverage-gate` (DD-1/DD-2/DD-3/DD-4/DD-5/DD-6/DD-9).
  - `tools/sdd_coverage.py` — generates a deterministic, regenerable
    `TRACEABILITY_MATRIX.md` (DD-7); the forward companion to `trace_walk.py`,
    reading the same graph.
- **Spec / governance:**
  - `governance/TRACEABILITY.md` — reverse-lookup note cross-refs the generated
    forward matrix + `trace_walk.py` (DD-7).
  - `layers/01_BRD/BRD-TEMPLATE.yaml` — normative `_authored_form` rule: every FR
    bullet MUST carry a `(P1|P2|Future, …)` band; the literal `Acceptance
    criteria:` line bounds the gated FR sub-block; optional `realized_by: <LAYER>`
    escape (DD-3/DD-4/D-0037).
- **Reach is document-level** for SPEC/TDD/IPLAN binding (PR-3 refines to element
  granularity, co-lands with 2a-ref). Deferred to 2c/PR-3: the escaped-FR
  informational row + the phase-leak row (DD-6 rows 1 & 4).
- **Backward compatibility:** additive. The coverage gate no-ops unless the
  corpus has reached both the SPEC and IPLAN layers (DD-1), so single-file
  `on_author` runs and partial cascades are unaffected; the example corpus is
  clean (0 `COV01`). New `covered_state` enum member `satisfied_by_reference` is
  stubbed for PR-5.
- **Validation:** 248 unit+conformance green (incl. `test_coverage_engine.py`
  V5 matrix-determinism + `COV01` contract + the template-rule guard, and the
  vendored byte-identity drift-guard). Example matrix regenerates byte-identical.

### Changed — `.github/workflows/ai-review.yml`: pin `@ci/v1.1.5` → `@ci/v1.1.6` (auto-merge App-token fix; version-lockstep with operations) (2026-06-27)

- Framework caller pin bumped from `@ci/v1.1.5` to `@ci/v1.1.6` to
  consume the auto-merge anti-recursion fix shipped on aidoc-flow-ci
  PR #37. The reusable workflow at `@ci/v1.1.6` authenticates the
  auto-merge as the reviewer App (`APP_TOKEN`) instead of the default
  `GITHUB_TOKEN`, so the App-authored merge commit triggers downstream
  `push:` workflows on every routine auto-merged PR.
- **Why now (vs deferring):** framework currently has no `push:`
  workflows that depend on the fix (no docs-sync.yml here yet), so
  the direct functional impact on framework is minimal. Adopting
  v1.1.6 keeps framework in version-lockstep with operations (the
  consumer that DOES depend on the fix) + readies framework for any
  future push: workflows. Per IPLAN-0024 the consumer-pin-bump
  discipline is to bump both in close succession to avoid skew.
- **Graceful fallback in v1.1.6:** if the reviewer App lacks
  `contents: write`, falls back to `GITHUB_TOKEN` + emits a
  `::warning::` with exact stderr. PR still merges (no regression).
- **Backward compatibility:** identical to pre-v1.1.6 behavior on
  framework today (no push: workflows depending on it). The merge-
  author change (`github-actions[bot]` → `aidoc-reviewer[bot]`) is
  visible in `git log` of future auto-merged PRs but otherwise inert
  for framework.
- **Plan:** discovered + fixed during IPLAN-0018 docs-sync verification
  on operations PRs #149 + #150 (operations carries primary tracking).
  Operations counterpart PR #151. Deeper structural fix is a future
  AI-driven doc-maintainer IPLAN (formerly TODO matrix row 6, DEFERRED;
  being promoted to active per founder direction this session).
- **Chicken-and-egg:** this PR's ai-review fires using BASE main's
  v1.1.5 workflow (not v1.1.6 yet); its own auto-merge will be by
  `github-actions[bot]`. Expected. The fix activates for the NEXT
  auto-merged PR after this one merges (but framework has no push:
  workflow to make the change observable; verify via merge-author of
  the next auto-merged PR).

### Changed — `.github/workflows/ai-review.yml`: pin `@ci/v1.1.3` → `@ci/v1.1.5` (IPLAN-0024 P4 — CRITICAL GitHub-hosted-runner validation) (2026-06-27)

- Framework caller pin bumped from `@ci/v1.1.3` to `@ci/v1.1.5` to
  consume the curl-replaces-`actions/checkout` fix shipped on aidoc-
  flow-ci main (PR #36 merged + tag `ci/v1.1.5` pushed; operations P3
  PR #148 merged earlier this session with all 9 checks green
  including ai-review on self-hosted). The reusable workflow at
  `@ci/v1.1.5` replaces 2 cross-repo `actions/checkout` steps with
  `curl`, eliminating the v1.1.0→v1.1.3 sparse-checkout / clean-flag /
  INIT-time-content-delete bug class. Header comment block refreshed
  to reference IPLAN-0024 instead of the v1.1.x saga context.
- **Framework is the CRITICAL validation:** GitHub-hosted runners
  (`ubuntu-latest`) are the bug-class home that v1.1.0-v1.1.3 couldn't
  escape — every prior sparse-checkout iteration failed here while
  passing on operations' self-hosted runners. P3 (operations on self-
  hosted) was the KNOWN-GOOD class. THIS PR is where curl's
  effectiveness is actually proven.
- **Chicken-and-egg:** BASE main still pins v1.1.3 → ai-review on this
  PR fires using the still-buggy v1.1.3 workflow on `ubuntu-latest`.
  Expected to fail or hang the same way prior framework PRs in the
  v1.1.x lineage did; ship via `skip-ai-review` label + admin-merge.
  After merge the new pin takes effect for all subsequent PRs and
  curl's GitHub-hosted-runner behavior is the validation gate.
- **R1 + R2 bundle from operations HANDOFF — BOTH DROPPED** in P1 (R1
  would have broken `docs/troubleshooting.md §15` force-fresh-review
  path; R2's bare 1-line `workflow_dispatch:` doesn't work without
  reusable workflow inputs design). Both tracked for separate future
  small IPLANs.
- **Plan:** IPLAN-0024 (operations PR #145; approved + merged
  2026-06-26).
- **Next:** if ai-review on the next post-merge framework PR fires
  cleanly using v1.1.5 on ubuntu-latest, IPLAN-0024 closes successfully.

### Fixed — `tools/bump_version.py`: bump playbooks + plugin README; decouple plugin VERSION (#182, 2026-06-27)

- The `framework_spec_version` regex required `\s+` (indentation) so it
  silently skipped all **51 playbooks** (column-0 frontmatter) — every
  framework-spec bump left conformance red until hand-fixed. Now `\s*` matches
  both; the bump set adds canonical playbooks + `SKILL_AUTHORING.md` + the
  plugin README framework-spec strings; the plugin's own `VERSION` is **no
  longer coupled** (independent stream). A framework bump now leaves conformance
  with **1** failure (the deliberate hard-pin tripwire in
  `test_plugin_release_metadata.py`, which the tool now reminds about) instead
  of 54. Tool-only change (no `framework/**`).

### In progress — CONSUMER-FEEDBACK-001 workstream (2026-06-27)

- Triaged 3 consumer-feedback logs (D54 / Engramory / BeeLocal) → 22 items,
  orchestrated by `plans/CONSUMER-FEEDBACK-001-PLAN.md` (12 child PRs).
  **Done:** PR-1 (the 0.23.1 reconciliation below, #180/#181); the bump-tool fix
  (#182); **PR-2 coverage engine — the full arc:** design of record (#184),
  **2a-core forward gate `COV01`** (#187, spec 0.24.0), **2b backward gate
  `COV02`** (#189 plan / #190, 0.25.0), **GD-03 ref-granularity policy** (#192,
  0.26.0), **PR-3 `REFGRAN01` enforcement** (#193 plan / #194, 0.27.0). The
  coverage engine asserts both directions + enforces element-granular refs.
  **Remaining (next session):** the corpus REFGRAN re-cascade
  (`CORPUS-REFGRAN-RECASCADE`), the element-level `COV01`/`COV02` upgrade (the
  payoff catching the 15 orphaned BDD scenarios), `BL-STATUS-SCOPE` (PR-3b), and
  sub-PRs 2c (phase reconciliation) + 2d (BDD roll-up).

### Fixed — Framework Spec 0.23.1: cumulative→necessary-upstream doc reconciliation (2026-06-27)

- Completed the doc migration `NECESSARY-UPSTREAM-001` (spec 0.16.0) left
  unfinished: the obsolete **cumulative-tag model** ("each layer inherits all
  upstream tags") survived in ~20 framework-core surfaces, several making
  **false `required_tags` claims** that contradicted `LAYER_REGISTRY.yaml` +
  the lint-passing corpus (e.g. `EARS-TEMPLATE` "requires @brd and @prd" → only
  `@prd`; `BDD-TEMPLATE` "@brd+@prd+@ears" → only `@ears`; `GATE-03` "ADR needs
  4 tags" → `@ears @bdd`). All corrected to **necessary-upstream** (each layer
  cites only its `required_tags`; deeper lineage transitive). One live
  author-facing bug fixed (`AI_ASSISTANT_RULES.md` told assistants to emit the
  full cumulative chain — the exact trace fabrication 0.16.0 banned).
- Surfaces: `TRACEABILITY.md`, `GATE-08`/`GATE-03`/`GATE_ERROR_CATALOG`,
  `DOC_GOVERNANCE_CORE` (Principle 3), `AI_ASSISTANT_RULES`, `DEFINITION_OF_DONE`,
  `REVIEW_REMEDIATION_FLOW`, `SPEC_DRIVEN_DEVELOPMENT_GUIDE`, `QUICK_REFERENCE`,
  `framework/README` + `governance/README`, EARS/BDD templates + 3 layer READMEs
  - BDD-00 index + ADR template guidance + ADR auditor playbook. Structural tag
  *fields* untouched (BL-Q1) — prose/guidance/gate-doc only.
- Framework PATCH (`0.23.0 → 0.23.1`); `FRAMEWORK_SPEC_VERSION` pins + 52 skill
  - 51 playbook `framework_spec_version` synced to 0.23.1; **plugin VERSION
  stays 0.22.0** (independent stream — only its bundled spec docs changed, not
  its code). CFB-PR-1 (CONSUMER-FEEDBACK-001), bundled per founder decision.

### Fixed — bump caller pin @ci/v1.1.1 → @ci/v1.1.2 (full-clone sparse-checkout fix; 2026-06-26)

- **`.github/workflows/ai-review.yml`** caller pin bumped per
  aidoc-flow-ci PR #31 / `ci/v1.1.2`. v1.1.1's cone-mode sparse-checkout
  STILL didn't populate `./reviewer-assets/ai-review/` on GitHub-hosted
  runner fresh clones (broke framework PR #173 + operations PR #140
  ai-review). v1.1.2 removes sparse-checkout entirely + does full
  clone (reliable; a few seconds slower).
- Chicken-and-egg: this PR's ai-review uses BASE main's v1.1.1
  workflow (which has the bug) → ships via `skip-ai-review` label
  - admin-merge.

### Fixed — close 2 repo-wide CI gaps + CHANGELOG terminology (2026-06-26)

- **`.github/workflows/ai-review.yml`** caller pin bumped
  `@ci/v1.1.0` → `@ci/v1.1.1`. The prior pin had a sparse-checkout
  pattern bug (aidoc-flow-ci PR #29 / `ci/v1.1.1`) that broke
  ai-review on GitHub-hosted runners (worked on self-hosted only
  due to cached state from prior `actions/checkout` invocations
  masking the issue). Framework PR #173 ai-review failed with
  `Append system prompt file not found` — exposed the bug.
- **`CHANGELOG.md` line 27** terminology fix: "(ubuntu-latest
  runner)" → "(GitHub-hosted runner)" per
  [GitHub Actions docs](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners)
  - the canonical reference at `aidoc-flow-ci/docs/runners.md §0`
  (shipped in aidoc-flow-ci PR #30). Runners have two CLASSES
  (GitHub-hosted vs self-hosted); `ubuntu-latest` is a LABEL
  identifying a specific runner image within the GitHub-hosted
  class. Class-first framing prevents conflation bugs.
- **`.github/workflows/composition.yml`** triggers extended:
  `[synchronize, labeled, unlabeled]` →
  `[opened, synchronize, reopened, labeled, unlabeled]`.
  **Gap 2 closed:** without `opened`, freshly-opened PRs left
  composition pending (only ai-review fired on `opened`) → merge
  blocked until label-cycle / push woke composition. Root-cause fix
  per `aidoc-flow-ci/docs/troubleshooting §15` label-cycle pattern
  (label-cycle was the workaround; this is the fix). Mirrors
  operations PR #140 same-pattern fix.

### Changed — IPLAN-0022 PR-C: ai-review caller bumped @ci/v1.0.5 → @ci/v1.1.0 (2026-06-25)

- **`.github/workflows/ai-review.yml`** caller pin bumped per
  IPLAN-0022 §4 P2 (second consumer after operations PR-B; both
  consume the new asset source on aidoc-flow-ci).
- **What this changes for framework:** the reusable workflow now
  fetches `review-prompt.md` + `verdict.schema.json` from
  `aidoc-flow-ci/ai-review/@ci/v1.1.0` (via sparse-checkout) instead
  of `aidoc-flow-operations@main`. `config.json` still comes from
  operations@main via a transitional sparse-checkout step.
- **Validation:** next framework PR after this merges will fire
  the new asset-fetch path end-to-end on a PUBLIC consumer
  (GitHub-hosted runner). Pairs with operations PR #138 (PRIVATE
  consumer; self-hosted) for cross-visibility coverage.
- **What stays on operations** (until IPLAN-0022 PR-D): the legacy
  `.github/ai-review/review-prompt.md` + `verdict.schema.json` files
  remain for back-compat with consumers pinned at older `@ci/v1.0.X`
  tags.
- Source-of-truth migration plan: [`aidoc-flow-operations` IPLAN-0022](https://github.com/vladm3105/aidoc-flow-operations/blob/main/ops/iplans/IPLAN-0022_source-of-truth-migration.md).

### Added — Adopted `aidoc-flow-ci@ci/v1.0.2` shared CI library (2026-06-24)

Framework is the **first PUBLIC consumer of `aidoc-flow-ci`** per
IPLAN-0017 §4 Phase A (revised 2026-06-24 (d) to put framework
first; operations-side migration deferred). PR #168 bootstrapped:

- `.github/workflows/ai-review.yml` — thin caller pinned to
  `vladm3105/aidoc-flow-ci/.github/workflows/ai-review.yml@ci/v1.0.2`;
  reviewer set to `claude` (uses the `CLAUDE_CODE_OAUTH_TOKEN`
  subscription-auth path, not `ANTHROPIC_API_KEY` pay-per-token).
- `.github/workflows/composition.yml` — thin caller pinned to
  `...composition.yml@ci/v1.0.2`.
- `.github/ai-review/config.json` — trust allowlist (`vladm3105`
  only initially).
- 9 canonical labels added to the repo via `gh label create`
  (`ai:*` state labels + `area: *` semantic labels).

**Activation prerequisites done by founder:** `aidoc-reviewer`
GitHub App installed on `vladm3105/aidoc-flow-framework`; secrets
set (`APP_REVIEWER_1_ID`, `APP_REVIEWER_1_KEY`,
`CLAUDE_CODE_OAUTH_TOKEN`).

**Local fixes layered on top of `ci/v1.0.2` templates** (caught by
framework's pre-commit on PR #168's first run; backport to
aidoc-flow-ci templates deferred per the v1.0.4 misplacement
decision):

- `runner_labels_review:` alignment double-space removed (yamllint
  `[colons] too many spaces after colon`).
- `secrets: inherit` lines annotated with
  `# pragma: allowlist secret` (detect-secrets false-positive on
  the word "secrets").

This PR is the first verification PR after PR #168 merged —
exercises the v1.0.2 `Install codex + claude CLI` step on
`ubuntu-latest` + the `claude` reviewer end-to-end (the load-bearing
test of v1.0.2). Source runbook:
[`aidoc-flow-operations/ops/inbox/2026-06-24_cto-platform_framework-phase-a-migration.md`](https://github.com/vladm3105/aidoc-flow-operations/blob/main/ops/inbox/2026-06-24_cto-platform_framework-phase-a-migration.md).

### Added — Governance PR discipline (mandatory) section in CLAUDE.md (2026-06-23)

- **`CLAUDE.md` — new "Governance PR discipline (mandatory)" section.** Two
  rules for any PR touching `DECISIONS.md`, plan files, `CLAUDE.md`,
  `.github/ai-review/` or `.github/workflows/ai-review.yml`, or
  superseding a locked decision: (1) ≤3 doc surfaces per PR (split if
  more); (2) mandatory adversarial self-review before every push
  (dead refs / supersession completeness / internal consistency).
  Reconciliation paragraph clarifies the rule does NOT supersede the
  existing doc-currency rule — it scopes how doc-currency applies
  per-PR. Origin: operations 2026-06-23 (22+ ai-reviewer findings
  across operations PRs #107-109 in one session). Full reasoning +
  formal record in `aidoc-flow-operations` `CLAUDE.md` + `OPS-0061`.

### Added — Framework Spec `0.22.0` → `0.23.0`: security of an automated `pre_merge` gate

`REVIEW_REMEDIATION_FLOW.md` §"Independent review at `pre_merge`" gains four
engine-agnostic security properties an automated gate MUST hold: **trusted source**
(the gate's logic/rubric come from a trusted ref, not the change under review),
**read-don't-execute** (the reviewer reads the change, never runs it), **fail-closed**
(missing/unparseable verdict blocks), and **independent infrastructure** (isolated,
least-privilege). Additive (SemVer **minor**, change-level **C2**); passes GATE-SPEC.
Distilled from the operations binding's real findings (`aidoc-flow-operations`
IPLAN-0011 P2: the gate, reviewing itself with a different vendor, flagged a
runner-execution risk in the prior design).

### Added — Framework Spec `0.21.2` → `0.22.0`: AI-review governance standard (GD-02)

Engine-agnostic governance standard for an **independent automated review at
`pre_merge`** (judge ≠ generator; severity classes; iteration-capped remediation
→ escalate to a human) plus a **risk-tiered human-in-loop** (routine = gate +
escalation; spec/governance = human approval always). Additive (SemVer **minor**,
change-level **C2**); passes GATE-SPEC (VERSION + this entry + both platform
`FRAMEWORK_SPEC_VERSION` re-declared + green conformance; human approval on merge).

- `framework/governance/DECISIONS.md` — new **GD-02**.
- `framework/governance/REVIEW_REMEDIATION_FLOW.md` — new §"Independent review at `pre_merge`".
- `framework/governance/DEFINITION_OF_DONE.md` — new (completion criteria + tiered human-in-loop).
- `framework/governance/README.md` + `GOVERNANCE.md` — index updated.
- Proposed per `aidoc-flow-operations` IPLAN-0011; ratified on merge (human signs).

### Fixed — `CLAUDE.md` current-state snapshot staleness + release-tag backfill (no VERSION bump)

- `CLAUDE.md:19` "Current state (as of …)" snapshot bumped from
  `2026-06-11` / plugin `0.17.0` to `2026-06-15` / plugin `0.20.1`.
  The framework-themes paragraph below it (playbook injection, saga
  driver, review-quality calibration, etc.) remains accurate at
  `0.20.1`, so left intact per "size to the problem". The user-facing
  additions between `0.17.0 → 0.20.1` (11 slash commands per
  PLUGIN-USER-COMMANDS, prompt-driven `bug-report` / `feedback`, README
  version-cell sync fix) are tracked in
  `platforms/claude-code-plugin/CHANGELOG.md` and the release tags
  below.
- Pushed three previously-missing release tags so the
  `claude-code-plugin` namespace is gap-free `v0.18.0 → v0.20.1`:
  - `claude-code-plugin/v0.19.0` on `8f34b911` (Merge PR #143 —
    11 user-facing commands, PLUGIN-USER-COMMANDS).
  - `claude-code-plugin/v0.20.0` on `19d9f05f` (Merge PR #144 —
    bug-report/feedback draft GitHub issues from prompt + context).
  - `claude-code-plugin/v0.20.1` on `0ffa153c` (PR #145 README
    version-cell sync fix + PR #154 marketplace pre-publish
    doc-polish, cumulative).
  All annotated, immutable, pushed per `docs/TAGGING.md`. The
  intermediate `0.19.1` bump from a transient branch was never on
  main's first-parent history and so does not get a tag.

## [0.21.2] — Framework Spec — 2026-06-15

### Changed — `IPLAN-ECOSYSTEM.md`: standalone-mode clarification note (PATCH)

- `framework/layers/08_IPLAN/IPLAN-ECOSYSTEM.md` gains an emphatic
  blockquote right after the cascade diagram noting that **iplanic is
  optional** — IOPS can run an approved IPLAN straight from the
  framework with a fully local, signed, append-only ledger +
  independent gate + handover (standalone mode, including fully
  offline). iplanic dispatch (`intake --payload`) and evidence relay
  (`emit-events`) are framed as additive (with-iplanic mode). The two
  hops through iplanic in the cascade describe the with-iplanic mode;
  standalone is just `framework (author) → IOPS (execute, local
  ledger / gate / handover)`. Cross-links to iplan-runner's README
  "Operating modes".
- Clarification only — no change to layer schema, validation rules,
  conformance vectors, or any consumer-visible contract; existing
  IPLANs and integrations continue to work unchanged.
- Plugin framework bundle re-synced (`tools/sync-plugin-framework.sh`)
  so `platforms/claude-code-plugin/framework/layers/08_IPLAN/IPLAN-ECOSYSTEM.md`
  stays byte-identical (drift-guarded by
  `test_plugin_framework_bundle.py`).
- `framework/VERSION` 0.21.1 → 0.21.2 (PATCH).
  `platforms/{claude-code-plugin,hermes}/FRAMEWORK_SPEC_VERSION`
  bumped to match per `test_version_declaration.py`. Mechanical
  reference propagation handled by `scripts/sync-version-refs.sh`
  pre-commit hook.

Companion: iplan-runner PR #35.

### Fixed — plugin marketplace pre-publish doc-polish (plugin v0.20.1; no VERSION bump)

Three doc-only corrections discovered during a marketplace-readiness
review of `claude-code-plugin/v0.20.1`. Code, framework spec, skills,
agents, commands, and the vendored bundle all unchanged; conformance
suite 129/129 before and after.

- `.claude-plugin/marketplace.json` — description undercounted
  commands ("1 command" → "12 commands"). The plugin has shipped 12
  user-facing commands since plugin `v0.19.0` (PLUGIN-USER-COMMANDS).
- `platforms/claude-code-plugin/README.md` "What's inside" — added a
  dedicated row enumerating the 2 deprecated-stub skills (`doc-review`,
  `trace-check`). The 50/52 totals already reconciled; only the named
  utility list omitted them.
- `platforms/claude-code-plugin/README.md` "Framework spec conformance"
  — reworded to remove the incorrect claim that the bundle ships its
  own `framework/VERSION`. The bundle deliberately vendors only the
  subtrees the plugin consumes (`layers/`, `governance/`, `registry/`,
  `playbooks/`) plus `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` per D-0022;
  canonical `../../framework/VERSION` remains the single source of
  truth, and `tests/conformance/platforms/test_version_declaration.py`
  enforces the `FRAMEWORK_SPEC_VERSION` match.

### Changed — `docs/SUPPORT.md` go-live sync (operations IPLAN-0009 PR 3)

- `docs/SUPPORT.md` updated to reflect that the Contact-us channel is
  **live** (not "stubbed / coming in v2") with a Google Form ↔ Sheet ↔
  Drive MCP architecture.
- §"Where this is going (Phase 2)" renamed to §"Architecture (live since
  2026-06)" and rewritten to describe the simplified design: form →
  Sheet → AI Team polls via `mcp__claude_ai_Google_Drive__*`; two-stage
  classifier (Python prefilter + Haiku 4.5 LLM); no auto-acknowledgment
  email (the Google Forms confirmation page is the visitor's only ack);
  notification fan-out to internal Slack + Telegram + optional Gmail draft.
- The four-channel directory table (channel #4 row) and the "What to
  expect" table updated to drop "Phase 2 / when active" qualifiers.
- Cross-link table now references `operations/ops/iplans/IPLAN-0009`
  (Phase 2 implementation) alongside IPLAN-0008 (Phase 1 historical
  context) and the operations + business design docs.
- Trace: operations OPS-0039 + `aidoc-flow-operations#23` (plan) +
  `aidoc-flow-operations#24` (impl).

## [0.21.1] — Framework Spec — 2026-06-14

### Fixed — release gate (umbrella `PR Checks`)

- Cut this `## [0.21.1]` section from `[Unreleased]` so `tests/release`
  (`test_changelog_has_entry_for_current_version`) matches `framework/VERSION`.
- `platforms/claude-code-plugin/commands/status.md` — quoted the `description`
  frontmatter value (an unquoted `:` made the YAML parse as a nested mapping),
  so `claude plugin validate --strict` (`tests/packaging`) passes. At runtime
  the unparsed frontmatter had been silently dropped.

### Fixed — ACCEPTANCE-FIXTURES-DRIFT (no plugin VERSION change)

Closes 12 long-standing failures in
`tests/acceptance/deterministic/` that were red on the umbrella `PR
Checks` workflow since 2026-06-02 and on the umbrella nightly `Live
Tier` since 2026-06-01. Framework's own CI didn't run the suite, so the
failures stayed silent here; the umbrella CI catches them and recent
umbrella PRs merged through the red check as a known background issue.

Three coordinated fixes for three root causes:

- **`tests/acceptance/_harness.py`** — `template_sections()` gains a
  `subtype` parameter and respects `_required: false` (PRD
  `component_decomposition`) and `_required_when_subtype: [list]`
  (IPLAN sub-types per CLEANUP-PR-E item 17). New `subtype_of()`
  helper reads `document_control.subtype` from a YAML golden (tolerant
  of optional `---` frontmatter fence) and defaults to `combined` per
  the IPLAN template's backward-compat note. New `headings()` parses
  the YAML body after a `---` frontmatter fence so per-layer goldens
  that carry a `doc_id`-bearing frontmatter still expose their body
  sections. Closes 4 failures (PRD + IPLAN missing-sections + fullpath
  PRD/IPLAN subtests).
- **Fullpath upstream goldens** — `01_BRD/BRD-01_golden.md` gains the
  `### BRD.01.07.aaaa` heading downstream layers cite;
  `02_PRD/PRD-01_golden.md` gains `### PRD.01.09.aaaa`. SPEC/TDD/IPLAN
  goldens gain top-level `doc_id:` + closing `---` frontmatter fence
  so `@spec: SPEC-01`, `@tdd: TDD-01` doc-form references resolve.
  IPLAN goldens (per-layer + fullpath) gain `subtype: code_build` to
  match the existing fixture content (no deploy sections). Closes 1
  failure (fullpath chain lint).
- **Per-layer fixture sibling additions** — for each layer N ∈ {2..8},
  copied upstream goldens (layers 1..N-1) from
  `fullpath/golden_chain/` into `layer_NN_<NAME>/valid/`. 28 file
  copies total. Closes 7 failures (per-layer lint, PRD through
  IPLAN).

New unit test
`tests/acceptance/deterministic/test_harness_template_sections.py`
covers the 5 cases for `template_sections()` (PRD optional section,
IPLAN combined/code_build/None subtypes, BRD subtype-irrelevant).

Verified-planning gate: 12 cited claims; Pass 1 + Pass 2 (independent
Agent review) with 13 findings folded in; `check_plan.py: ok`. Plan
merged via [PR #147](https://github.com/vladm3105/aidoc-flow-framework/pull/147).

### Added — IPLAN-0008 framework slice (no plugin VERSION change)

- **`docs/SUPPORT.md`** — new public-facing channel directory for
  developers, evaluators, and contributors. Names the four channels
  (in-product `/aidoc-flow:bug-report` and `/feedback`, GitHub Issues
  direct, web-site `/support`), explains the AI Team intake architecture
  for Phase 2 Contact-us, and documents what channels do NOT exist by
  design (no public Slack, no public Telegram, no `mailto:`, no status
  page). Cross-links to the operations and business sibling docs.
- **`scripts/sync-version-refs.sh`** extended to propagate
  `Pre-release v<X.Y.Z>` in `../web-site/src/pages/index.astro`
  (cross-submodule write at the umbrella layer; no-op when the sibling
  is not present). Closes the version-badge drift class for the web-site
  home page — sibling fix to the plugin-README drift fixed in v0.20.1.
  Per IPLAN-0008 step 6.
- **`plans/FRAMEWORK-TODO.md`** carries the
  `WEBSITE-VERSION-BADGE-DRIFT` entry documenting the cross-repo
  coupling.

Trace: this CHANGELOG entry covers the framework slice of
`../operations/ops/iplans/IPLAN-0008_support-channels.md` (steps 3 + 6).

### Fixed — Claude Code plugin 0.20.0 → 0.20.1 (PATCH)

- Long-standing drift in `platforms/claude-code-plugin/README.md` Platform
  info table — the `Version` cell had been stuck at `0.6.3` since plugin
  v0.7.0 (~14 bumps ago) because `scripts/sync-version-refs.sh` only awk'd
  bare lines, missing inline table cells. Canonicalized the cell to the
  tag form (`claude-code-plugin/v<X.Y.Z>`) and extended the sync script
  to also propagate the tag form in platform READMEs so the bug class
  can't recur. Same drift exists in `platforms/hermes/README.md`
  (out of scope per plugin-first); tracked in `plans/FRAMEWORK-TODO.md`.
  Per-platform detail in
  [`platforms/claude-code-plugin/CHANGELOG.md`](platforms/claude-code-plugin/CHANGELOG.md).

### Changed — Claude Code plugin 0.19.0 → 0.20.0 (MINOR)

- `/aidoc-flow:bug-report` and `/aidoc-flow:feedback` now accept a user
  prompt argument and draft a structured GitHub issue from it (title +
  body) using the conversation context and the environment stamp. The
  drafted title + body are URL-encoded into `?title=&body=` and the user
  reviews on github.com before clicking Submit; the plugin never
  auto-submits. Supersedes the unreleased v0.19.1 PATCH (which used the
  same `&body=` machinery for a static four-line env block only).
  GitHub issue templates refined to match. Per-platform detail in
  [`platforms/claude-code-plugin/CHANGELOG.md`](platforms/claude-code-plugin/CHANGELOG.md).

### Added — Claude Code plugin 0.18.0 → 0.19.0 (PLUGIN-USER-COMMANDS)

- 11 user-facing commands (meta · workflow · lifecycle · config) on the Claude
  Code plugin; optional project-local `.claude/aidoc-flow.config.yaml` config
  format; `feedback.md` issue template; conformance test for the config
  schema. Per-platform detail in
  [`platforms/claude-code-plugin/CHANGELOG.md`](platforms/claude-code-plugin/CHANGELOG.md).

### Added — Framework Spec 0.21.0 → 0.21.1 (CHG-gated)

- **`framework/layers/08_IPLAN/IPLAN-ECOSYSTEM.md` — cross-repo reference note.**
  - Adds an engine-agnostic note describing how IPLAN spans three sibling
    repos: `aidoc-flow-framework` authors (Layer 8), `aidoc-flow-iplanic`
    manages (control plane + standard), `iplan-runner` executes (engineering
    codename `iops-framework`). Captures the *intended pipeline*, the
    *authoritative docs per repo*, the *contract divergence* between the
    three (template shape, schema_version, identity, signing, …) and the
    *open question / next step* (recommendation: option 2 — keep L8 as the
    authoring format, make iplanic's import the formal bridge).
  - Mirrored identically in `iplanic/docs/standards/IPLAN-ECOSYSTEM.md`
    (carries iplanic's D-0020 forward-looking resolution; propagates to
    this framework copy only when explicitly approved per iplanic D-0016)
    and `iplan-runner/docs/IPLAN-ECOSYSTEM.md`.
  - SemVer: PATCH (`0.21.0 → 0.21.1`). Content-only addition — no template,
    schema, registry, or governance-rule changes; no behavior contract
    changes for either platform.

### Changed — Framework Spec 0.20.1 → 0.21.0 + Claude Code plugin 0.17.1 → 0.18.0 (CHG-RT-001)

CHG layer (Change Management overlay) brought to per-layer parity with
the 8 SDD layers. Closes the long-standing gap that CHG was the only
governance surface never exercised end-to-end despite being structurally
mature.

- **Framework spec**:
  - New CHG crew entry in `REVIEW_CREWS.yaml`:
    `integration_lead:30 / architect:20 / chaos_engineer:15 / operator:15 /
    auditor:10 / security_engineer:10` (= 100). Rationale: CHG is
    propagation-faithfulness primary; integration_lead leads (30); operator
    and chaos_engineer get larger weight than typical because CHG sits at
    the deploy boundary.
  - 6 new playbook files under `framework/playbooks/09_CHG/` (one per
    crew lens) matching the existing per-lens playbook contract.
  - `REVIEW_TEAM.md` §Playbooks gains a CHG-RT-001 note documenting that
    CHG is an overlay (not lifecycle layer) but uses the same playbook
    contract.
- **Claude Code plugin**:
  - `doc-chg-audit/SKILL.md`: 200 → 693 lines. Adds `## Review Mode` +
    `## Saga interaction` + `## Break-circuit policy` + `## Content
    Sub-Checks` (A1/A2/A3/BA1/SE1) + playbook injection. Mirrors the
    `doc-iplan-audit` shape post-IPLAN-RT-001 + post-PR-B.
  - `doc-chg-fixer/SKILL.md`: 125 → 344 lines. Adds `## Remediate Mode`
    - `## Saga interaction` + `## Break-circuit policy`.
  - `doc-chg-autopilot/SKILL.md`: 116 → 191 lines. Adds saga-driven
    generation loop invoking `python3 saga_driver.py --layer 09_CHG`;
    existing 6-step Linear Pipeline preserved as `single_pass` fallback.
  - `tools/saga_driver.py` `_LAYER_CREWS` gains `"09_CHG"` entry with
    the 6 personas matching REVIEW_CREWS.yaml.
- **Conformance**:
  - `_spec.py`: new `OVERLAYS = ["CHG"]` constant + `ARTIFACTS_AND_OVERLAYS`
    helper (ARTIFACTS stays 8 layers — CHG is overlay, not lifecycle layer).
  - `test_playbook_coverage.py` `LAYER_PREFIX` map extended with
    `"CHG": "09_CHG"`.
  - `test_review_team.py` `test_crews_cover_exactly_the_artifacts`
    compares to `ARTIFACTS_AND_OVERLAYS` (was `eight_layers`); also
    `_parse_weight_table` extended to recognise CHG.
  - `chaos-engineer.md` + `security-engineer.md` weight tables gain CHG
    row (15 + 10 respectively).
- Framework MINOR (`0.20.1 → 0.21.0`) — new crew + 6 playbooks +
  REVIEW_TEAM §Playbooks update.
- Plugin MINOR (`0.17.1 → 0.18.0`) — 3 CHG SKILLs gain ~900 cumulative
  lines + new saga layer entry.
- **Live CHG cascade verification PENDING** — Task 11 of plan; will
  drive `examples/url-shortener/chg/test-change.md` end-to-end through
  the 4 SKILLs to verify CHG-01.md is produced + propagation report
  enumerates expected downstream impacts.

### Changed — Framework Spec 0.20.0 → 0.20.1 + Claude Code plugin 0.17.0 → 0.17.1 (CLEANUP-PR-F)

Single-item follow-up PR closing `plans/FRAMEWORK-TODO.md` item #18.
Documents doc-number independence across layers (the deferred item
from the original 2026-06-11 PR-C cataloging).

- **`ID_NAMING_STANDARDS.md`** gains new §"Cross-layer cardinality"
  subsection (~35 lines) between §Document IDs and §Element IDs.
  States explicitly: doc numbers are per-layer sequential and
  INDEPENDENT across layers; one-to-many + many-to-one cross-layer
  relationships both supported; the url-shortener example's 1:1
  alignment is coincidence not contract.
- 8 doc-<layer> author SKILLs gain one-line clarification in their
  Reserve ID step pointing to the new subsection.
- 6 auditor playbooks (BRD/PRD/BDD/ADR/TDD/IPLAN) gain an
  orphan-vs-sibling note in Beyond-checklist: validate trace by tag
  resolution, not number alignment.
- `TRACEABILITY.md` gains a cross-reference in §Cumulative Tagging.
- Framework PATCH (`0.20.0 → 0.20.1`) + plugin PATCH
  (`0.17.0 → 0.17.1`).

### Workstream — FRAMEWORK-CLEANUP-001 complete (2026-06-11, 5 child PRs)

`plans/FRAMEWORK-TODO.md` drained — 18 of 19 items closed across PR-A
through PR-D + PR-E; 2 deferred follow-ups (item #18 doc-num
independence, item #19 Option B `02b_DECOMP` layer promotion for
complex projects). Master plan PR #128 merged `528d6f23`; five child
PRs landed:

- **PR-A (#129, plugin 0.14.1)** — harness + lint workflow hygiene
- **PR-C (#130, framework 0.18.0 + plugin 0.15.0)** —
  spec/registry/template hygiene
- **PR-B (#131, framework 0.19.0 + plugin 0.16.0) — heart** —
  review-quality calibration; remediated the "convergence theater"
  pattern in the auditor + tech_lead lenses
- **PR-E (#132, framework 0.19.1 + plugin 0.16.1)** — IPLAN
  sub-types (`code_build` / `deploy` / `combined`)
- **PR-D (#133, framework 0.20.0 + plugin 0.17.0)** — decomposition
  - threshold-resolution gates

Cumulative framework `0.17.1 → 0.20.0`; plugin `0.14.1 → 0.17.0`. Per
the FRAMEWORK-FEEDBACK-LOG-001 contract (governance Principle 9), this
workstream converted accumulated example-driven feedback from the
url-shortener corpus into durable spec + SKILL improvements. Per-PR
entries below preserve the detail.

### Changed — Framework Spec 0.19.1 → 0.20.0 + Claude Code plugin 0.16.1 → 0.17.0 (CLEANUP-PR-D)

Fifth and final child PR of FRAMEWORK-CLEANUP-001 (master plan PR #128).
Closes `plans/FRAMEWORK-TODO.md` items #15-16. Opens item #19 (Option B
future). Resolves DECISION-GATE-D as Option A — subsection in PRD.

- **Item 15** — `PRD-TEMPLATE.yaml` gains new OPTIONAL section §7b
  `component_decomposition` between `scope_and_requirements` and
  `user_stories`. Each component declares responsibility + named
  thresholds (`full_id: PRD.NN.<cat>.<key>` per PR-C's threshold
  regex). Section is `_required: false` — present only when downstream
  cites `@threshold:`.
- **Item 16** — new `sdd_doc_lint` TH-RES-001 rule (corpus-level,
  citation-driven). Validates every downstream `@threshold:` citation
  resolves to a `full_id:` entry in the host PRD's
  `component_decomposition` section. P2 (missing section) and P1
  (missing key) severities. New `tests/unit/test_threshold_resolution.py`
  covers 4 cases.
- **REVIEW_TEAM.md** §Operations gains a new "Threshold-resolution
  gate" subsection documenting the rule + 4-downstream-audit-SKILL
  ingest.
- **Backward compat** — TH-RES-001 fires P2 on url-shortener PRD-01
  (which has inline threshold definitions but no formal
  `component_decomposition` section); this is **expected backward-
  compat behavior**, not a regression. A future cascade re-run
  populates the section.
- **Item #19 (NEW, OPENED, DEFERRED)** — Option B promotion to a
  first-class `02b_DECOMP` layer. Cataloged with "when to revisit"
  criteria; impl waits until complex projects show Option A is
  insufficient.
- Framework MINOR (`0.19.1 → 0.20.0`) — new lint rule + new template
  section + spec subsection. Plugin MINOR (`0.16.1 → 0.17.0`).

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
