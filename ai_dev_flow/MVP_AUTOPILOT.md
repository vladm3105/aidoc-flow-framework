---
title: "MVP Autopilot: Core Guide"
tags:
  - framework-core
  - mvp-workflow
  - automation
custom_fields:
  document_type: guide
  artifact_type: DOCS
  layer: 0
  priority: primary
  development_status: active
---

# MVP Autopilot: Framework Core Guide

This document is the authoritative reference for the MVP Autopilot in the AI Dev Flow framework. It explains what the autopilot does, how to use it, how it interacts with validators and templates, and how to tune it for different rigor levels (MVP speed vs. strict compliance).

The Autopilot lives at:
- `ai_dev_flow/scripts/mvp_autopilot.py`

It generates and validates the entire MVP pipeline in one command:
- BRD → PRD → EARS → BDD → ADR → SYS → REQ → SPEC → TASKS → IPLAN

---

## 1) What It Does

- MVP artifacts are single, flat files; document splitting and `DOCUMENT_SPLITTING_RULES.md` do not apply in the MVP track.

- Single-command scaffolding of all MVP artifacts using repo templates.
- Per-layer validation via existing `ai_dev_flow/scripts/validate_*.{py|sh}`.
- Auto-fix strategies to keep momentum:
  - Non-destructive patching (frontmatter, H1, required sections, traceability tags).
  
- Traceability tagging across layers, using dotted forms where required (e.g., `BRD.NN.01.01`).
- Optional reporting (markdown/json/text) for CI and run history.

---

## 2) Quick Start

- MVP speed run (warnings allowed; auto-fix; write report):
  - `python3 ai_dev_flow/scripts/mvp_autopilot.py --root ai_dev_flow --intent "My MVP" --slug my_mvp --up-to IPLAN --auto-fix --report markdown`

- Strict validation (warnings fail):
  - `python3 ai_dev_flow/scripts/mvp_autopilot.py --root ai_dev_flow --intent "My MVP" --slug my_mvp --up-to IPLAN --auto-fix --strict --report markdown`

- Lighter MVP validators for BRD (`--mvp-validators`):
- `python3 ai_dev_flow/scripts/mvp_autopilot.py --root ai_dev_flow --intent "My MVP" --slug my_mvp --up-to IPLAN --auto-fix --mvp-validators`

  - Pre‑Check (one‑liner): `python3 ai_dev_flow/scripts/validate_documentation_paths.py --root ai_dev_flow` and verify `X-00_index.md`, `X-00_required_documents_list.md`, and upstream docs exist before each layer.

---

## 2.1) Pre‑Check Routine (avoid token waste)

Run these quick checks before generating each layer (BRD → … → SPEC):

- Paths: `python3 ai_dev_flow/scripts/validate_documentation_paths.py --root ai_dev_flow`
- Planning docs: Ensure `X-00_index.md` and `X-00_required_documents_list.md` exist for the target layer.
- Upstream presence: Confirm required upstream docs exist before proceeding:
  - PRD needs BRD-01
  - EARS needs PRD-01
  - BDD needs EARS-01
  - ADR/SYS need BRD-01, PRD-01, EARS-01
  - REQ needs ADR-01, SYS-01
  - SPEC/TASKS need required REQ files

Tip: Use `--strict` with the path validator when you want failures to block generation.

---

## 2.2) Dependencies

- Python dependencies for the Autopilot live in `ai_dev_flow/scripts/requirements.txt`.
- Install (virtualenv recommended):
  - `pip install -r ai_dev_flow/scripts/requirements.txt`
- Required: PyYAML (used for config and YAML parsing).

---

## 3) Command Reference

- `--root`: Docs root. In this repo: `ai_dev_flow`.
- `--intent`: Short description used to seed names/titles.
- `--slug`: Lowercase underscore slug used in filenames (e.g., `trading_bot`).
- `--nn`: Numeric ID (default `01`) used in document IDs.
- `--up-to`: Last layer to generate/validate. One of: `BRD|PRD|EARS|BDD|ADR|SYS|REQ|SPEC|TASKS|IPLAN`.
- `--from-layer`: Start from this layer (e.g., `BDD`) instead of BRD.
- `--auto-fix`: Enables deterministic auto-fixers (safe rewriting of frontmatter, titles, required sections, tags).
- `--strict`: Treat warnings as errors (validator must exit code 0).
- `--no-precheck`: Skip pre-checks (path validator and upstream existence checks).
- `--precheck-strict`: Fail fast when pre-checks report issues or missing upstreams.
- `--mvp-validators`: Prefer lighter MVP validators when available (currently uses Python validator for BRD).
- `--skip-validate`: Generate artifacts only; skip all validators.
- `--report`: `none|markdown|json|text`. Writes a summary report.
- `--report-path`: Custom path. If omitted, report is written to `work_plans/mvp_autopilot_report_<timestamp>.(md|json|txt)`.

---

## 4) Generated Artifacts

- Files (examples for `--nn 01`, `--slug trading_bot`):
  - `ai_dev_flow/BRD/BRD-01_trading_bot.md`
  - `ai_dev_flow/PRD/PRD-01_trading_bot.md`
  - `ai_dev_flow/EARS/EARS-01_trading_bot.md`
  - `ai_dev_flow/BDD/BDD-01_trading_bot.feature`
  - `ai_dev_flow/ADR/ADR-01_trading_bot.md`
  - `ai_dev_flow/SYS/SYS-01_trading_bot.md`
  - `ai_dev_flow/REQ/REQ-01_trading_bot.md`
  - `ai_dev_flow/SPEC/SPEC-01_trading_bot.yaml`
  - `ai_dev_flow/TASKS/TASKS-01_trading_bot.md`
  - `ai_dev_flow/IPLAN/IPLAN-01_trading_bot.md`

- Planning stubs:
  - `X-00_required_documents_list.md` created per layer, listing the generated file.

---

## 5) Layer-by-Layer Behavior

- BRD:
  - Fixes: frontmatter (tags, custom_fields), `# BRD-NN: Title`, required early sections, Document Control stub.
  - MVP-aware validation: use `--mvp-validators` to switch to the Python validator per file.
  - Generation: Create from `BRD-MVP-TEMPLATE.md` with required early sections.

- PRD:
  - Fixes: frontmatter, H1, Document Control with `@brd: BRD.NN.01.01`, sections 1–3.
  - Generation: Create from `PRD-MVP-TEMPLATE.md` with functional requirements stub.

- EARS:
  - Fixes: frontmatter, H1, `## Document Control`, `## Purpose`, `## Traceability` (`@brd`, `@prd`), one EARS requirement with SHALL.

- BDD:
  - Fixes: header cumulative tags (`@brd @prd @ears`), Feature line, one GWT scenario.

- ADR:
  - Generation: Create from `ADR-MVP-TEMPLATE.md` with required sections + subsections.

- SYS:
  - Fixes: frontmatter, H1, insert Sections 1–15; `## 13. Traceability` with `@brd/@prd/@ears/@bdd/@adr`.
  - Generation: Create from `SYS-MVP-TEMPLATE.md` with stubs for all sections.

- REQ:
  - Generation: Create from `REQ-MVP-TEMPLATE.md` with Document Control (semver, ISO dates, P-level, SPEC-Ready Score), upstream chain, and cumulative tags.

- SPEC:
  - Generation: Create from `SPEC-TEMPLATE.yaml` with required top-level keys; `traceability.cumulative_tags` and `upstream_sources`; `interfaces.classes`; `performance.latency_targets`; `security` (auth/authz/input_validation); `observability` (metrics/logging/health); `verification` stubs.

- TASKS:
  - Generated from template; validated.

- IPLAN:
  - Fixes: frontmatter (`artifact_type: IPLAN`, `layer: 12`, `parent_tasks: TASKS-NN`), required sections, bash code blocks + verification, 9 cumulative tags, prerequisites/tools/files.

---

## 6) Validation Semantics

- Default (non-strict): A layer passes if its validator exits 0 or 1 (warnings allowed).
- `--strict`: A layer passes only if exit code is 0 (warnings fail the layer).
- Auto-fix loop:
  - Apply targeted fixes → revalidate.
  - If still failing → halt and report errors for manual resolution.
  - Halt on persistent errors.
- End-of-run link check:
  - Runs `validate_links.py`; warnings can be addressed after initial scaffolding.

---

## 7) Traceability Rules

- Upstream tags auto-populated per layer; examples:
  - PRD: `@brd: BRD.NN.01.01`
  - EARS: `@brd`, `@prd`
  - BDD: `@brd`, `@prd`, `@ears`
  - SYS: `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`
  - REQ: `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@sys`
  - SPEC: cumulative tags include `req`
  - IPLAN: includes 9 tags (`@brd` … `@tasks`)
- Dotted vs hyphenated IDs: autopilot converts `BRD-NN` → `BRD.NN.01.01` where required by validators.

---

## 8) Reporting

- `--report`: `markdown|json|text` (default `none`).
- Default output directory: `work_plans/`.
- Contents:
  - Summary: PASS/FAIL, target layer, flags (`strict`), link-check result.
  - Layer table: layer, status (`pass|fixed|fail|generated`), file, notes.

---

## 9) Examples

- MVP speed run (recommended day-1):
  - `python3 ai_dev_flow/scripts/mvp_autopilot.py --root ai_dev_flow --intent "MVP idea" --slug idea --up-to IPLAN --auto-fix --report markdown`

- MVP + lighter validators + strict:
  - `python3 ai_dev_flow/scripts/mvp_autopilot.py --root ai_dev_flow --intent "MVP" --slug mvp --up-to IPLAN --auto-fix --mvp-validators --strict --report markdown`

  - Non-destructive strict gate:
  - `python3 ai_dev_flow/scripts/mvp_autopilot.py --root ai_dev_flow --intent "MVP" --slug mvp --up-to IPLAN --auto-fix --strict --report json`

- Partial pipeline:
  - `--from-layer BDD --up-to IPLAN` to continue from BDD.
  - Or `--up-to BDD` to stop at BDD.

### Validate Only (No Generation)

- Preferred (pure validation, zero writes):
  - Validate everything: `python3 ai_dev_flow/scripts/validate_all.py ai_dev_flow --all --report markdown`
  - Validate subset: `python3 ai_dev_flow/scripts/validate_all.py ai_dev_flow --layer BRD --layer PRD --report text`
  - Strict mode: add `--strict`

- Using Autopilot to validate existing docs (no new files):
  - `python3 ai_dev_flow/scripts/mvp_autopilot.py --root ai_dev_flow --resume --include-layers BRD PRD EARS BDD ADR SYS REQ SPEC TASKS --up-to TASKS --mvp-validators --strict`
  - Notes:
    - `--resume` reuses existing files; it will generate missing ones unless you exclude those layers or ensure they exist.
    - For guaranteed no writes, use `validate_all.py` above.

---

## 10) CI Integration

- Suggested targets:
  - `make mvp`: run autopilot with `--auto-fix --report markdown`.
  - `make validate`: `python3 ai_dev_flow/scripts/validate_all.py ai_dev_flow --all --report markdown`.
  - Policy: allow warnings (non-strict) for MVP branches; enable `--strict` for release branches.

---

## 11) Troubleshooting

- BRD fails early with full-template checks:
  - Use `--mvp-validators` to switch to the per-file Python validator.
  - Or omit `--strict` until content is filled in.

- Autopilot halts at a layer:
  - Re-run with `--auto-fix` to allow fixers.
  - Re-run without `--strict` to allow warnings while filling content.

- Link integrity warnings at the end:
  - Fill in real links and re-run `python3 ai_dev_flow/scripts/validate_links.py --docs-dir ai_dev_flow` later.

- Auto-fixers brittle with major template changes:
  - The fixers use regexes and rely on current template structure. If templates are significantly refactored, fixers may need corresponding updates in `mvp_autopilot.py`. Autopilot uses `<LAYER>-MVP-TEMPLATE.*` as the default starting point (fall back to full templates where an MVP variant is not available).

---

## 12) Extensibility

- Add per-layer fixers for additional patterns (e.g., custom section names).
  - Add a config file (e.g., `ai_dev_flow/.autopilot.yaml`) to persist flags: `mvp_validators`, `strict`, `report`.
- Add `--profile <name>` to load preset flag combinations.
- Template overrides: In `.autopilot.yaml`, set `templates:<LAYER>: <filename>` to try alternate templates without changing code.

---

## 13) Best Practices

  - Start with speed: run non-strict with auto-fix to get a quick baseline.
- Iterate content quickly: replace stubs with real material in each file.
  - Tighten later: turn on `--strict` when stabilizing.
- Validate frequently: run `validate_all.py` and `validate_links.py` as you fill content.

---

## 14) Safety and Scope

- The Autopilot writes only inside the docs repo (`ai_dev_flow/`).
- It does not execute arbitrary commands; it only reads/writes files and invokes validators.
- IPLAN documents may include bash blocks; these are content only and not executed by the Autopilot.

---

## 15) Pointers & Related Docs

- Autopilot code: `ai_dev_flow/scripts/mvp_autopilot.py`
- MVP Workflow guide: `ai_dev_flow/MVP_WORKFLOW_GUIDE.md`
- Design notes: `ai_dev_flow/MVP_AUTOMATION_DESIGN.md`
- Layer templates and validator scripts: see `ai_dev_flow/<LAYER>/` and `ai_dev_flow/scripts/`

---

## 16) Configuration & Profiles

You can persist preferred defaults and named profiles in a YAML config file.

- Default path (auto-detected): `ai_dev_flow/.autopilot.yaml`
- Override: `--config /path/to/.autopilot.yaml`

Example:

```
defaults:
  auto_fix: true
  mvp_validators: true
  report: markdown

default_profile: mvp

profiles:
  mvp:
    auto_fix: true
    strict: false
    mvp_validators: true
    report: markdown
  strict:
    auto_fix: true
    strict: true
    report: markdown
```

Usage:

- `--profile mvp` or `--profile strict`
- CLI flags always win over config (only config fills in CLI defaults not explicitly set).

---

## 17) Continuing Existing Projects (Resume or Fork)

The Autopilot can be used to continue a partially created project or to fork an existing project as the base for a new one.

### Modes

- **Resume In-Place**: Discover existing artifacts, validate and fix them, generate only missing layers/files, keep IDs/links intact.
- **Fork-As-New**: Copy the existing project as a base for a new effort with a new `NN` and `slug`, update IDs/titles/traceability, and preserve a “supersedes/origin” link.

### Recommended Workflow

- **Discovery**:
  - Scan `ai_dev_flow/<LAYER>/` for existing `X-NN_{slug}.*` files (or sectioned patterns).
  - Extract IDs/tags using `ai_dev_flow/scripts/extract_tags.py` to build an upstream/downstream map.
  - Run `validate_all.py ai_dev_flow --all --report markdown` to get a baseline status.

- **Planning**:
  - Decide target layers (e.g., only `REQ`, `SPEC`, `IPLAN`) with `--up-to` and `--include-layers`/`--exclude-layers`.
  - Choose Resume vs Fork:
    - Resume: prefer non-destructive fixes; do not overwrite existing content unless `--force-overwrite` is given.
    - Fork: pick `--new-nn` and `--new-slug`; add “Supersedes {OLD-ID}” note in the new BRD/PRD and “Superseded by {NEW-ID}” note in old docs (optional).

- **Execution**:
  - Run Autopilot with `--auto-fix` for conservative passes; iterate content to resolve remaining validator errors.
  - For Forks, use the new identifiers so the Autopilot generates new files and rewrites traceability accordingly.

- **Review**:
  - Inspect the report (`--report markdown`) to see: reused vs generated vs skipped files.
  - Resolve any link warnings by updating references and re-running `validate_links.py`.

### Non-Destructive Fixing (Resume)

- **Don’t overwrite** any existing file by default; restrict to patching frontmatter, titles, required section headers, and tags.
  - Generate artifacts from MVP templates; avoid overwriting existing files unless `--force-overwrite` is explicitly requested.
- Prefer `--strict` only after you’ve closed most warnings; early runs can allow warnings to speed progress.

### Forking a Project (Copy-As-New)

- **Copy Strategy**:
  - Source selection: find `X-OLDNN_{old_slug}.*` artifacts per layer.
  - Create new files as `X-NEWNN_{new_slug}.*` and update:
    - Frontmatter: `title`, `custom_fields.layer`, `artifact_type`, etc.
    - H1/Feature lines: `# X-NEWNN: {New Title}`.
    - Traceability tags: convert `BRD-OLDNN` → `BRD.NEWNN.01.01` (and similar for all layers) where dotted forms are required.
  - Add a small “Supersedes”/“Derived from” note in the new BRD/PRD and optionally a “Superseded by” in the old documents.

- **ID and Link Consistency**:
  - Maintain a simple ID map while forking: `BRD-01→BRD-02`, `PRD-01→PRD-02`, etc., and propagate to dotted references (`BRD.01.01.01→BRD.02.01.01`).
  - After generation, run `validate_links.py` to catch residual links to old IDs; fix or leave a redirect note.

### Flags (for Resume/Fork)

- **Resume**:
  - `--resume`: enable discovery-first behavior and skip regenerating existing artifacts.
  - `--no-overwrite`: explicit safeguard to avoid replacing any existing file content.
  - `--include-layers / --exclude-layers`: limit the operation scope.
  - `--plan-only`: write a plan/report without making any changes (plan file: `work_plans/mvp_plan_<timestamp>.md`).

- **Fork**:
  - `--fork-from-nn 01 --new-nn 02 --new-slug new_product`: copy all `*-01_*` artifacts as `*-02_*` updating IDs and tags.
  - `--id-map path/to/id_map.yaml`: advanced mappings across layers. Format: simple YAML dictionary `{"OLD-ID": "NEW-ID"}` (e.g., `REQ-15: REQ-03`).
  - `--supersede`: inject “Supersedes/Derived from” blocks automatically.
  - `--copy-assets`: copy images/diagrams referenced by relative paths (preserves sectional folder layouts).

- **Safety**:
  - `--dry-run`: simulate actions, mark outputs as planned, and skip validation.
  - Always write a report (`--report markdown|json|text`) for audit trails; report includes plan actions.

### Practical Recommendations

  - **Start with Resume (non-destructive)** for teams picking up partial work; enable `--auto-fix --report markdown` to normalize and see what’s missing. Use `--plan-only` first to review intended actions.
- **Fork only when scope diverges** or IDs need to branch cleanly; pick a fresh `NN` and add “Supersedes” info to keep the lineage auditable.
- **Incremental layers**: If BRD/PRD/EARS are stable but implementation isn’t, set `--up-to IPLAN` while targeting `SYS/REQ/SPEC/TASKS/IPLAN` phases.
  - Use `--from-layer BDD` (or `ADR`/`SYS`) to skip earlier layers cleanly.
- **Reports & Plans**: Save reports and plans in `work_plans/` and attach to review PRs.
