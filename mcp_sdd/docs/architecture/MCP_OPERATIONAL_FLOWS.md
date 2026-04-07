# MCP Operational Flows

| Field | Value |
| --- | --- |
| Status | Active |
| Version | 1.9 |
| Date | 2026-04-06 |
| Scope | End-to-end command execution flows for implemented MCP CLI operations |

---

## 1. Flow Set

- project initialization flow: `init` → `create-build`
- document lifecycle flow (5 stages): `create` → `validate` → `review` → `remediate` → `remediate --fix`
- review prompt flow: `review-build` and `review`
- readiness and lineage flow: `preflight`, `consistency`
- diagnostics flow: `prescreen`, `scan`, `scoring`

---

## 2. Project Initialization Flow

This flow runs once per project to create the project-specific UCX scaffold that all subsequent document lifecycle commands depend on.

### Stage A — Scaffold (`init`)

**Command**: `init`

**Input**: `--project <project_root>`

**Output** (written to `<project_root>/UCX/`):

| Destination folder | Contents |
| --- | --- |
| `skills/personas/` | 15 persona definition files |
| `skills/persona_mappings.yaml` | Per-doctype, per-phase persona sequence configuration |
| `skills/layer_aliases/` | Layer alias mappings |
| `prompts/templates/creation/` | Creation prompt templates |
| `prompts/templates/review/` | Review prompt templates |
| `prompts/templates/remediation/` | Remediation prompt templates |
| `templates/` | Document templates (unified and project-tuned) |
| `templates/layers/NN_TYPE/` | Layer-specific templates and schemas (from `ai_dev_ssd_flow/`) |

**Rules**:
- Existing files are never overwritten (idempotent) in default mode.
- Source assets come from the framework canonical scaffold and `ai_dev_ssd_flow/` layer directories.
- Templates matching `*-TEMPLATE.*` are copied from layer directories.
- All 11 layers (BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC, TSPEC, TASKS) use unified YAML naming (`{TYPE}-TEMPLATE.yaml`). No legacy `*-MVP-TEMPLATE.*` files remain.

**Update mode** (`--update`):
- Overwrites stale templates and prompts with latest framework versions.
- `persona_mappings.yaml` is protected (project-owned after init). Use `--update-mappings` to explicitly reset it.
- Content-identical files are skipped (no unnecessary writes).
- Result reports `created_paths`, `skipped_paths`, `updated_paths`, `protected_paths`.

---

### Stage A.2 — Persona Management (`personas-show`, `personas-set`, `personas-diff`)

Three commands for inspecting and modifying project-specific persona-to-layer mappings after initialization.

**`personas-show`**: Display current persona assignments.

```
Input:  --project, optional --phase, --doc-type, --format
Output: Phase → doctype → persona list table (text or JSON)
```

**`personas-set`**: Update persona list for a specific phase+doctype.

```
Input:  --project, --phase, --doc-type, --personas (space-separated names)
Output: Confirmation with previous and new persona lists
Rules:  Validates persona .md files exist. Supports _default as doc_type.
        Preserves YAML header comments. Invalidates persona mapping cache.
```

**`personas-diff`**: Compare project mappings against framework defaults.

```
Input:  --project, optional --format
Output: Added, removed, changed entries with summary counts
```

---

### Stage A.3 — Default Project (`set-project`, `get-project`)

Set a session-level default project to avoid repeating `--project` on every MCP tool call.

```
MCP: sdd_set_project(project="/path/to/project")  → session default set
MCP: sdd_get_project()                             → show resolved project + source
CLI: export SDD_DEFAULT_PROJECT=/path/to/project   → env var default for CLI
CLI: mcp get-project                               → show env var value
```

Resolution order: explicit `--project` > session override > `SDD_DEFAULT_PROJECT` env var > `executors.json` config default. `handle_tool()` injects the resolved project before `configure_logging` and dispatch for all project-dependent tools.

---

### Stage A.4 — Environment Inspection (`env-show`)

Show project `.env` keys without exposing values.

```
Input:  --project, optional --format {text,json}
Output: env_keys list, env_key_count, blocked_vars, env_file_exists
```

Environment variables from `.env` are auto-loaded when executors run. Merge order: `os.environ` (base) < `config.env` (executor static) < `project_env` (.env file). System variables (`PATH`, `HOME`, `PYTHONPATH`, `LD_LIBRARY_PATH`, `LD_PRELOAD`, `SHELL`, `USER`, `IFS`) are blocked. Loading uses mtime-based caching.

---

### Stage B — Create Prompt (`create-build`)

**Command**: `create-build`

**Input**: `--project`, `--doc-type`, `--layer`, `--template` + optional `--personas`, `--sections-json`

**Output** (written to the document folder or `--out`):

| Artifact | Purpose |
| --- | --- |
| `creation_prompt.md` | Assembled prompt ready for LLM input |
| `creation_sidecar.json` | Metadata: personas (list), doc type, layer assets used, template source, persona token estimates |
| Layer asset files | Unified YAML template, schema, and any project-tuned template bundled into the prompt |

**Rules**:
- Loads project-tuned template: tries `TYPE-TEMPLATE.yaml`, then `TYPE-TEMPLATE.md`, then `TYPE-MVP-TEMPLATE.md` from `UCX/templates/`. Falls back to layer template from `UCX/templates/layers/NN_TYPE/`.
- Does not write the final document artifact; use `create` for that.
- `--sections-json` injects existing document sections into the prompt for guided creation (incremental authoring).

---

### Initialization Flow Summary

```
init
  └─ writes UCX/ scaffold (personas, persona_mappings.yaml, templates, schemas, prompts)
        ↓
create-build
  └─ assembles LLM creation prompt + sidecar
        ↓
  [LLM generates document content]
        ↓
create
  └─ writes TYPE-NN_{slug}.md  ← stage 1 of document lifecycle
```

The `init` command must be run before any `create-build` or `create` command. It is safe to re-run; it will skip files that already exist.

---

## 3. Document Lifecycle Flow

This flow applies uniformly to all SSD document layers (BRD, PRD, EARS, SYS, REQ, CTR, and others).

Each stage reads from the previous stage's output artifact. The source document is never modified after stage 1.

### Stage 1 — Create

**Command**: `create`

**Input**: none (template only)

**Output**: `TYPE-NN_{slug}.md`

**Rules**:
- Source document is the canonical authored artifact.
- Filename contains no stage suffix.
- `processing_stage: source` in metadata.

---

### Stage 2 — Validate

**Command**: `validate`

**Input**: `TYPE-NN_{slug}.md` (source)

**Output**:

| Artifact | Condition |
| --- | --- |
| `validate_report.json`, `validate_report.txt` | Always produced |
| `TYPE-NN_{slug}_validated.md` | Produced when validation errors are found (source-protected derived copy with fix instructions) |
| `validate_fix_report.json`, `validate_fix_report.txt` | Produced when validation errors are found |

**Rules**:
- Validation reads the source document; it does not modify it.
- Deterministic, script-based checks only (no LLM).
- When validation errors are found, `validate` automatically creates a source-protected derived copy (`_validated`) containing fix instructions. The source document is never modified.
- `processing_stage: validation-fixed` in derived copy metadata.
- `derived_from: TYPE-NN_{slug}.md` in derived copy metadata.
- When `--document` points to a folder, MCP resolves the canonical source artifact automatically (see Source Artifact Resolution).
- New response fields: `is_valid` (bool), `fix_generated` (bool), `passed` always True (for pipeline compatibility).

> **Deprecation note**: `sdd_validate_fix` is deprecated and merged into `sdd_validate`. Calling `validate-fix` as a separate command is no longer required. The alias still works but emits a deprecation warning.

---

### Stage 3 — Review

**Command**: `review-build` / `review`

**Input**: `TYPE-NN_{slug}_validated.md` (validated copy)

**Output**: `TYPE-NN.UCX_review_report_vNNN.md`

**Rules**:
- Review runs against the `_validated` copy, not the source.
- Multiple personas are loaded per the 2-tier resolution: explicit `--personas` override or `persona_mappings.yaml` defaults for the `(doc_type, review)` pair.
- Each persona receives only the document sections mapped to its domain categories.
- LLM-based content and cross-layer compliance review.
- Report is versioned; repeated runs do not overwrite prior results.
- In `--document` folder mode, the review pipeline collects `.md`, `.yaml`, and `.yml` files. YAML-first precedence applies when both `.yaml` and `.md` canonical sources exist. Legacy (`_LEGACY`) files are excluded. Appendix files are detected by name (`appendix`/`appendices`).

---

### Stage 4 — Remediate

**Command**: `remediate`

**Input**: `TYPE-NN_{slug}_validated.md` + optional `review_report`

**Output**: `TYPE-NN.UCX_remediation_report_vNNN.md`

**Rules**:
- Remediation runs against the `_validated` copy, not the source.
- Report is versioned.
- When `--document` points to a folder, MCP resolves the canonical source artifact (the `_validated` copy) automatically.

---

### Stage 5 — Remediate-Fix

**Command**: `remediate --fix`

> **Note**: The standalone `sdd_remediate_fix` MCP tool and `remediate-fix` CLI command have been absorbed into `sdd_remediate` with `fix=true` parameter. Use `remediate --fix` instead.

**Input**: `TYPE-NN_{slug}_validated.md` + optional `--remediation-report`

**Output**: `TYPE-NN_{slug}_remediated.md` (derived copy, written alongside source)

**Rules**:
- Input is the `_validated` copy, not the source.
- Output uses the canonical base name (`{slug}_remediated.md`), not `{slug}_validated_remediated.md`.
- When `--document` points to a folder, MCP resolves the `_validated` copy automatically.
- Source and `_validated` copy are not modified.
- `processing_stage: remediated` in derived copy metadata.
- `derived_from: TYPE-NN_{slug}_validated.md` in derived copy metadata.

**Executor prompt (v1.20.0+)**:
- Findings are grouped by priority phase: Phase 1 (P0 critical), Phase 2 (P1 high), Phase 3 (P2 enhancements).
- Derived copy content is embedded in the prompt (capped at 50K chars) so the executor has full document context.
- Fix strategy includes: FWDREF placeholder handling, section ordering preservation, substantive content requirements, and verification guidance.

**Post-fix quality checks (v1.20.0+)**:
- `verify_remediation_quality()` runs automatically after executor completes: detects cosmetic FWDREF renames, stub sections (<50 words), and low content delta. Returns `quality_pass: true/false`.
- In pipeline mode (`sdd_run_lifecycle`), `sdd_validate` auto-runs on the derived copy after `remediate --fix` to catch regressions. The `clean_before` parameter on `sdd_run_lifecycle` triggers `sdd_clean` to prune obsolete stage artifacts before the pipeline starts.

---

## 4. Artifact Lineage and Naming

### Canonical Artifact Set (per document folder)

| Stage | Artifact | Filename Pattern | Mutates Prior Artifact |
| --- | --- | --- | --- |
| 1 | Source document | `TYPE-NN_{slug}.md` | No |
| 2 | Validation report | `validate_report.json/.txt` | No |
| 2 | Validated copy (when errors found) | `TYPE-NN_{slug}_validated.md` | No |
| 2 | Validate-fix report (when errors found) | `validate_fix_report.json/.txt` | No |
| 3 | Review report | `TYPE-NN.UCX_review_report_vNNN.md` | No |
| 4 | Remediation report | `TYPE-NN.UCX_remediation_report_vNNN.md` | No |
| 5 | Remediated copy (`remediate --fix`) | `TYPE-NN_{slug}_remediated.md` | No |

### Lineage Chain

```
TYPE-NN_{slug}.md
  └─ validate ──→ validate_report.json
  │            ──→ TYPE-NN_{slug}_validated.md       (when errors found)
  │            ──→ validate_fix_report.json/.txt     (when errors found)
  │
  TYPE-NN_{slug}_validated.md
                        └─ review       ──→ UCX_review_report_vNNN.md
                        └─ remediate    ──→ UCX_remediation_report_vNNN.md
                        └─ remediate --fix ──→ TYPE-NN_{slug}_remediated.md
```

### Reserved Suffixes

- `_validated` — UCX-derived copy from `validate` (when errors are found)
- `_remediated` — UCX-derived copy from `remediate --fix` only
- These suffixes must not appear in canonical source document filenames.

### Source Artifact Resolution

When `--document` points to a folder, MCP applies the following resolution rules at each stage:

| Stage | Resolution rule |
| --- | --- |
| validate | Locate single file matching `^[A-Z]+-\d+_.+\.(md\|yaml\|yml)$` with no `_validated` or `_remediated` stem suffix; use it as the source. Fall back to full folder set if no unique match. |
| review | Collect all `.md`, `.yaml`, `.yml` files (excluding `_LEGACY`, `REVIEW`, `REPORT`, `_validated`, `_remediate_copy`, `_remediate_v{N}` stems). Identify canonical source via `^[A-Z]+-\d+_.+\.(md\|yaml\|yml)$` (excluding appendix files). YAML-first precedence when both formats exist. Append appendix files (detected by `appendix`/`appendices` in filename). |
| remediate | Locate single file matching `^[A-Z]+-\d+_.+_validated\.md$`; use it as the `_validated` input. Fall back to full folder set if no unique match. |
| remediate --fix | Locate single file matching `^[A-Z]+-\d+_.+_validated\.md$`; use it as the `_validated` input. Fall back to full folder set if no unique match. |

---

## 5. Diagnostics Flow

### 5.1 Readiness and lineage checks

1. Execute `preflight` before create, review, or remediation stages when environment or provider readiness must be verified.
2. Inspect `probe_status`, `probe_fallback_used`, and `probe_fallback_reason` when a probe payload is present.
3. Execute `consistency` against a file or folder to validate artifact lineage without re-running full validation.
4. Treat `preflight` blocked output and `consistency` failed output as CI-gating conditions.

Outputs:

- preflight report: `preflight_report.json`, `preflight_report.txt`
- consistency report: `consistency_report.json`, `consistency_report.txt`

### 5.2 Prescreen, scan, and scoring

1. Execute `prescreen` to identify high-priority candidate files.
2. Execute `scan` on JSON report files to extract finding-category counts.
3. Execute `scoring` commands for numeric quality scoring and comparisons.

Outputs:

- prescreen report: `prescreen_report.json`
- scan report: `scan_report.json`
- scoring payloads: JSON printed to stdout

---

## 6. Operational Controls

Validation controls:

- `validate --tier1-only`
- `validate --strict`
- `validate --format {text,json}`

Review controls:

- `--personas`, `--unified`, `--one-turn`, `--no-resume`, `--session-ttl`
- `--clean-memory`, `--clean-reports`, `--keep-versions`

---

## 7. Exit Behavior

| Command Group | Pass | Fail |
| --- | --- | --- |
| validate | 0 | 1 |
| consistency | 0 | 1 for blocking lineage failures, 2 for runtime errors |
| preflight | 0 for ready or degraded | 1 for blocked, 2 for runtime errors |
| scoring validate | 0 | 1 |
| other implemented commands | 0 | 2 only for CLI usage/argument failures |

---

## 8. Evidence Commands

- `pytest mcp_sdd/tests/unit/test_cli_main.py`
- `pytest mcp_sdd/tests/unit/test_validation_runner.py`
- `pytest mcp_sdd/tests/unit/test_remediation_runner.py`
- `pytest mcp_sdd/tests/unit/test_prescreening.py`
- `pytest mcp_sdd/tests/unit/test_scoring_cli.py`
- `pytest mcp_sdd/tests/integration/test_migration_flows.py`
- `pytest mcp_sdd/tests/integration/test_lifecycle_pipeline_integration.py`
