# Changelog

All notable changes to the AI Doc Flow Framework are documented here. Format
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.53.1] — 2026-09-08

### Fixed — P0 governance, acceptance fixtures, CI repin, template alignment (#620, #637, #635, #636, #588, #393, #641, #642, #596, #565)

**Governance & test fixes:**
- Phantom-release guard now reads working tree VERSION to avoid false phantoms on staged-but-uncommitted bumps (#620)
- Ported GOV-008/GOV-009 lint rules and MANDATORY PROCESS GATE from archived governance into active DOC_GOVERNANCE_CORE.md and LINT_RULES.md (#641)
- Ported EVAL-001/002/003/EVAL-COV-001 lint rules into active LINT_RULES.md; added EVAL downstream to BDD-00_index.TEMPLATE.md (#642)
- Fixed three stale D-0084 comments in auto-merge-ai-prs.yml, ai-review/config.json, and standards-drift.yml (#596)

**Acceptance fixtures:**
- Renamed BDD.01.04.* → BDD.01.03.* (scenarios in section 3) and BDD.01.04.aaaa → BDD.01.02.aaaa (feature in section 2) across 33 files (#637)
- Added element declarations to ADR golden fixtures; re-cited doc-level @adr/@tdd as element-level in downstream goldens; removed 5 REFGRAN01 manifest entries (#635)
- Added closing frontmatter fence and doc_id to 3 broken_chain YAML golden fixtures (#636)

**Infrastructure:**
- Repinned all 12 stale CI workflow pins from ci/v2.16.0/v3.0.0 to ci/v4.0.0 (#393)
- Added doc_id: field to all 9 layer templates — the key the linter actually reads (#588)
- Added conformance test locking extensions to [.yaml] for all layers per GD-15 (#565)

### Changed — Platforms archived, framework becomes self-sufficient (2026-09-07)

### Fixed — the acceptance goldens never adopted the normative TDD acceptance-pairing form; 8 pinned findings clear (#478) (2026-09-04)

`TDD-01_golden.yaml` carried `test_mapping.coverage_table.columns` but **omitted the
`test_mapping.scenarios:` list entirely**, which `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
declares normative for GD-08 acceptance pairing. `_check_acceptance_pairing` pairs a BDD
scenario only when a TDD line carries a real `@bdd:` tag beside a test-case id or a
`bdd_scenario`/`bdd_ref` carrier, so every scenario read as unpaired — and the fixture also
wrote `bdd_ref: BDD.01.03.bbbb` without the `@bdd:` prefix the template prescribes.
Separately `EARS.01.03.cccc` (checkout) was realized by nothing: the BDD covered sign-in and
catalog search only.

**These were errors, not warnings, in `gate-code`** — so the acceptance tier's `valid/`
positive controls could not pass the framework's own code gate.

Authoring the normative `scenarios:` list clears `ACC01` ×4 and `COV02` ×3; a new
`BDD.01.03.eeee` checkout scenario citing `@ears: EARS.01.03.cccc` clears the fourth `COV02`.

```
fullpath/golden_chain  {COV02:4, ACC01:4, REFGRAN01:5} -> {REFGRAN01:5}
layer_07_tdd/valid     {ACC01:4, COV02:4, REFGRAN01:3} -> {REFGRAN01:3}
layer_08_iplan/valid   {ACC01:4, COV02:4, REFGRAN01:5} -> {REFGRAN01:5}
layer_06_spec/valid    {COV02:4, REFGRAN01:2}          -> unchanged
```

Manifests go from **39 entries / 43 warnings to 15 / 19**. `layer_06_spec/valid` is net-zero
by design, not by omission: it stages a SPEC and no TDD, and `SPEC-01_golden.yaml` cites only
`@bdd: BDD.01.02.aaaa` element-level, so `BDD.01.03.eeee` takes the departing
`EARS.01.03.cccc` slot for the same structural reason its three siblings were already pinned.

**The remaining five `REFGRAN01` are split out to #635** — they cannot be cleared by re-citing,
because `ADR-01_golden.md` declares no `ADR.01.SS.xxxx` element, and they are sequenced
behind issue #563. **The three remaining `broken_chain` fences are split out to #636.**

Two source comments that misdescribed current state were corrected in the same change:
`tests/conformance/test_forward_coverage_is_exercised.py` still attributed the per-layer
targets' invisibility to a fence defect PR #580 had already fixed (`layer_08_iplan/valid` is a
second live `COV01` target; `layer_06`/`layer_07` stage no IPLAN, so `COV01` there is
inapplicable, not blind), and `tests/acceptance/deterministic/test_doc_validator.py` claimed a
single HTML-comment marker was the whole difference between `golden_chain` and `broken_chain`
when five files differ and always have.

Tests only — no framework spec, platform or tooling surface is touched.

### Changed — Framework Spec `0.50.0` → `0.51.0`: a Draft IPLAN's §5 `session_handoff.sessions` is empty (GD-26, #621) (2026-09-04)

**Platforms archived.** Hermes MCP server and Claude Code plugin moved to
`archive/platforms/`. Any capable AI agent derives its behavior from the
framework spec, templates, and playbooks directly — no platform-specific
wrapper needed.

**Tooling reorganized.**
- `sdd_doc_lint/` — moved to repo root (structural linter, 296+ checks)
- `hooks/` — PostToolUse advisory hook + pre-commit/pre-push hooks
- `tools/` — archived (saga_driver.py, finding_filter.py, etc.)
- `plans/` — archived (migration plans)
- `legacy/` — moved to `archive/legacy/`
- `.claude-plugin/` — archived (plugin marketplace config)
- `scripts/` — hooks moved to `hooks/`, utilities archived

**Tests cleaned up.**
- Linter-specific tests moved to `sdd_doc_lint/tests/` (14 files)
- Platform-specific conformance tests archived
- Stale acceptance live harnesses archived
- All path references updated

**Docs updated.** All core docs (README, CLAUDE.md, AGENTS.md, CONTRIBUTING.md,
SECURITY.md, etc.) updated to reflect new structure.

**Framework is now ~90% self-sufficient.** Agents can author, review, and
validate artifacts from the spec alone.

### Changed — Framework Spec `0.51.0` → `0.53.0` (2026-09-07)

**GD-24: `document_control` for all framework governance documents.** All
governance docs, gate definitions, layer READMEs, root-level reference docs,
playbook READMEs, and YAML data files now carry version tracking metadata.
66 files modified, 67 originals archived to `archive/CHG-01/`. (`CHG-01`,
GATE-SPEC, C2, minor)

**GD-25: `.aidoc/` redefined as project override layer.** The `.aidoc/`
directory now holds the project profile and project-specific overrides
(`.aidoc/project/`) instead of unused AI provenance subdirectories. New
discovery rule: `.aidoc/project/` first, fall back to framework defaults.
(`CHG-02`, GATE-SPEC, C2, minor)

**10-layer model.** CHG promoted from governance overlay to Layer 9; EVAL
added as Layer 10. All layer templates, READMEs, and the layer registry updated.

## [0.53.0] — 2026-09-07

- GD-25: `.aidoc/` redefined as project override layer
- `governance/aidoc/AIDOC.md` rewritten with new purpose and discovery rule
- `README.md` four-tier model updated
- `governance/ADAPTATION.md` §10 added — project overrides contract

## [0.52.0] — 2026-09-07

- GD-24: `document_control` added to all 66 framework governance documents
- 67 original files archived to `archive/CHG-01/`
- New playbooks: `gate_spec_change.md`, `document_control.md`
- `PROFILE-TEMPLATE.yaml` duplicate metadata key fixed

## [0.51.0] — 2026-09-04

- GD-26: Draft IPLAN's §5 `session_handoff.sessions` is empty (`sessions: []`)
- Template and layer README updated with guidance

## [0.50.0] — 2026-09-04

- GD-25: IPLAN `code_inventory` seeds `planned` at Draft

## [0.49.0] — 2026-08-30

- Framework spec consolidation and cleanup

## [0.48.0] — 2026-08-28

- GD-23: Three layer templates declare no title

## [0.47.0] — 2026-08-25

- GD-19, GD-20, GD-21, GD-22 shipped as one release

## [0.46.0] — 2026-08-20

- GD-18: Derived test paths, threshold carriers, IPLAN status contract
