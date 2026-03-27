# MCP Operational Flows

| Field | Value |
| --- | --- |
| Status | Active |
| Version | 1.3 |
| Date | 2026-03-27 |
| Scope | End-to-end command execution flows for implemented MCP CLI operations |

---

## 1. Flow Set

- project initialization flow: `init` → `create-build`
- document lifecycle flow (6 stages): `create` → `validate` → `validate-fix` → `review` → `remediate` → `remediate-fix`
- review prompt flow: `review-build` and `review`
- readiness and lineage flow: `preflight`, `consistency`
- diagnostics flow: `prescreen`, `scan`, `scoring`

---

## 2. Project Initialization Flow

This flow runs once per project to create the project-specific UCX scaffold that all subsequent document lifecycle commands depend on.

### Stage A — Scaffold (`init`)

**Command**: `init`

**Input**: `--project <project_root>`

**Output** (written to `<project_root>/docs/UCX/`):

| Destination folder | Contents |
| --- | --- |
| `skills/personas/` | Persona definition files |
| `skills/layer_aliases/` | Layer alias mappings |
| `prompts/templates/creation/` | Creation prompt templates |
| `prompts/templates/review/` | Review prompt templates |
| `prompts/templates/remediation/` | Remediation prompt templates |
| `templates/` | Document MVP and project-tuned templates |
| `templates/layers/NN_TYPE/` | Layer-specific MVP templates and schemas (from `ai_dev_ssd_flow/`) |

**Rules**:
- Existing files are never overwritten (idempotent).
- Source assets come from the framework canonical scaffold and `ai_dev_ssd_flow/` layer directories.
- Only MVP templates (`*-MVP-TEMPLATE.md`) and MVP schemas (`*_MVP_SCHEMA.yaml`) are copied from layer directories.

---

### Stage B — Create Prompt (`create-build`)

**Command**: `create-build`

**Input**: `--project`, `--persona`, `--doc-type`, `--layer`, `--template` + optional `--sections-json`

**Output** (written to the document folder or `--out`):

| Artifact | Purpose |
| --- | --- |
| `creation_prompt.md` | Assembled prompt ready for LLM input |
| `creation_sidecar.json` | Metadata: persona, doc type, layer assets used, template source |
| Layer asset files | MVP template, schema, and any project-tuned template bundled into the prompt |

**Rules**:
- Loads project-tuned template from `docs/UCX/templates/TYPE-MVP-TEMPLATE.md` if present; falls back to layer MVP template from `docs/UCX/templates/layers/NN_TYPE/`.
- Does not write the final document artifact; use `create` for that.
- `--sections-json` injects existing document sections into the prompt for guided creation (incremental authoring).

---

### Initialization Flow Summary

```
init
  └─ writes docs/UCX/ scaffold (personas, templates, schemas, prompts)
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

**Output**: `validation_report.json`, `validation_report.txt`

**Rules**:
- Validation reads the source document; it does not modify it.
- Deterministic, script-based checks only (no LLM).
- When `--document` points to a folder, MCP resolves the canonical source artifact automatically (see Source Artifact Resolution).

---

### Stage 3 — Validate-Fix

**Command**: `validate-fix`

**Input**: `TYPE-NN_{slug}.md` (source) + optional `validation_report.json`

**Output**: `TYPE-NN_{slug}_validation.md` (derived copy, written alongside source)

**Rules**:
- Source document is not modified.
- Derived copy is named `{slug}_validation.md`.
- When `--document` points to a folder, MCP resolves the canonical source artifact automatically.
- `processing_stage: validation-fixed` in derived copy metadata.
- `derived_from: TYPE-NN_{slug}.md` in derived copy metadata.

---

### Stage 4 — Review

**Command**: `review-build` / `review`

**Input**: `TYPE-NN_{slug}_validation.md` (validation copy)

**Output**: `TYPE-NN.UCX_review_report_vNNN.md`

**Rules**:
- Review runs against the `_validation` copy, not the source.
- LLM-based content and cross-layer compliance review.
- Report is versioned; repeated runs do not overwrite prior results.

---

### Stage 5 — Remediate

**Command**: `remediate`

**Input**: `TYPE-NN_{slug}_validation.md` + optional `review_report`

**Output**: `TYPE-NN.UCX_remediation_report_vNNN.md`

**Rules**:
- Remediation runs against the `_validation` copy, not the source.
- Report is versioned.
- When `--document` points to a folder, MCP resolves the canonical source artifact (the `_validation` copy) automatically.

---

### Stage 6 — Remediate-Fix

**Command**: `remediate-fix`

**Input**: `TYPE-NN_{slug}_validation.md` + optional `remediation_report`

**Output**: `TYPE-NN_{slug}_remediated.md` (derived copy, written alongside source)

**Rules**:
- Input is the `_validation` copy, not the source.
- Output uses the canonical base name (`{slug}_remediated.md`), not `{slug}_validation_remediated.md`.
- When `--document` points to a folder, MCP resolves the `_validation` copy automatically.
- Source and `_validation` copy are not modified.
- `processing_stage: remediated` in derived copy metadata.
- `derived_from: TYPE-NN_{slug}_validation.md` in derived copy metadata.

---

## 4. Artifact Lineage and Naming

### Canonical Artifact Set (per document folder)

| Stage | Artifact | Filename Pattern | Mutates Prior Artifact |
| --- | --- | --- | --- |
| 1 | Source document | `TYPE-NN_{slug}.md` | No |
| 2 | Validation report | `validation_report.json/.txt` | No |
| 3 | Validation copy | `TYPE-NN_{slug}_validation.md` | No |
| 4 | Review report | `TYPE-NN.UCX_review_report_vNNN.md` | No |
| 5 | Remediation report | `TYPE-NN.UCX_remediation_report_vNNN.md` | No |
| 6 | Remediated copy | `TYPE-NN_{slug}_remediated.md` | No |

### Lineage Chain

```
TYPE-NN_{slug}.md
  └─ validate ──→ validation_report.json
  └─ validate-fix   ──→ TYPE-NN_{slug}_validation.md
                              └─ review       ──→ UCX_review_report_vNNN.md
                              └─ remediate    ──→ UCX_remediation_report_vNNN.md
                              └─ remediate-fix ──→ TYPE-NN_{slug}_remediated.md
```

### Reserved Suffixes

- `_validation` — UCX-derived copy from `validate-fix` only
- `_remediated` — UCX-derived copy from `remediate-fix` only
- These suffixes must not appear in canonical source document filenames.

### Source Artifact Resolution

When `--document` points to a folder, MCP applies the following resolution rules at each stage:

| Stage | Resolution rule |
| --- | --- |
| validate, validate-fix, remediate | Locate single file matching `^[A-Z]+-\d+_.+\.md$` with no `_validation` or `_remediated` stem suffix; use it as the source. Fall back to full folder set if no unique match. |
| remediate-fix | Locate single file matching `^[A-Z]+-\d+_.+_validation\.md$`; use it as the `_validation` copy input. Fall back to full folder set if no unique match. |

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

- `--persona`, `--unified`, `--one-turn`, `--no-resume`, `--session-ttl`
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

- `pytest mcp/tests/unit/test_cli_main.py`
- `pytest mcp/tests/unit/test_validation_runner.py`
- `pytest mcp/tests/unit/test_remediation_runner.py`
- `pytest mcp/tests/unit/test_prescreening.py`
- `pytest mcp/tests/unit/test_scoring_cli.py`
- `pytest mcp/tests/integration/test_migration_flows.py`
- `pytest mcp/tests/integration/test_lifecycle_pipeline_integration.py`
