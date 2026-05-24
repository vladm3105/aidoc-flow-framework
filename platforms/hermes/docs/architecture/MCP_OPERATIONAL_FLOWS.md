# MCP Operational Flows

| Field | Value |
| --- | --- |
| Status | Active |
| Version | 2.3 |
| Date | 2026-05-06 |
| Scope | End-to-end command execution flows for implemented MCP CLI operations |

---

## 1. Flow Set

- planning-first governance flow: analyze sources -> roadmap -> planning-index and changelog plan -> gap review and closure -> per-document IPLAN -> plan approval
- project initialization flow: `venv-bootstrap` -> `runtime-start` -> `init` -> `create-build`
- document lifecycle flow (5 stages): `create` -> `validate` -> `review` -> `remediate` -> `remediate --fix`
- pull-request governance flow (up to 2 rounds): `validate` -> `review` -> `remediate` -> post-remediation `validate` -> Hermes final blocker-gap check
- review prompt flow: `review-build` and `review`
- readiness and lineage flow: `preflight`, `consistency`
- diagnostics flow: `prescreen`, `scan`, `scoring`

---

## 2. Planning-First Governance Flow

This flow runs before project initialization and before any document creation stage.

### Stage 0A - Analyze Provided Information

Required inputs:

- user-provided source artifacts
- project constraints and scope boundaries
- upstream layer dependencies

Required outputs:

- documented assumptions
- dependency inventory
- candidate document inventory for the target layer

### Stage 0B - Create Layer Roadmap Package

Required roadmap package artifacts:

| Artifact | Purpose |
| --- | --- |
| Layer roadmap | Define sequencing, dependencies, milestones, and entry criteria for the target layer |
| Layer planning index | Enumerate required planning documents for the layer |
| Layer changelog plan | Define how changes for this layer are tracked and released |

### Stage 0C - Review Roadmap and Planning Index for Gaps

Required checks:

- missing planning artifacts
- missing dependency coverage
- missing traceability tags and references
- missing acceptance criteria for planned outputs

Resolution rules:

- fix identified gaps before proceeding
- if gap closure is deferred, record explicit rationale, owner, and follow-up trigger

### Stage 0D - Create and Review Per-Document Implementation Plans

Required for each planned target document:

1. Create an implementation plan (IPLAN).
2. Review the plan for structural and dependency gaps.
3. Resolve or defer gaps with documented rationale.
4. Record explicit plan approval.

Approval rule:

- Approval authority is a human reviewer or an independent LLM-as-judge session started from a fresh context.

Hard gate:

- No document creation, test implementation, or source-code implementation starts before plan approval.

---

## 3. Project Initialization Flow

This flow runs once per project to create the project-specific UCX scaffold that all subsequent document lifecycle commands depend on.

### Stage A.0 — Runtime Environment Bootstrap (`venv-bootstrap`)

Required bootstrap commands:

```bash
cd /opt/data/ucx_framework
scripts/bootstrap_ucx_venv.sh
```

Optional when `project-knowledge` MCP server is enabled:

```bash
cd /opt/data/ucx_framework
scripts/bootstrap_ucx_venv.sh --with-kb
```

Validation checks:

```bash
/opt/data/ucx_framework/.venv/bin/python --version
/opt/data/ucx_framework/.venv/bin/python -c "import mcp_server; print('ucx_hermes ok')"
PYTHONPATH=/opt/data/ucx_framework /opt/data/ucx_framework/.venv/bin/python -c "import ucx_kb; print('ucx_kb ok')"
```

Rules:

- Shared virtual environment path is fixed at `/opt/data/ucx_framework/.venv` for all framework MCP runtimes.
- `ucx_hermes[api]` install is required before any LLM-enabled review/remediation stage.
- KB import validation is required only when KB MCP tools are part of the project runtime.

---

### Stage A.1 — Scaffold (`init`)

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
| `templates/layers/NN_TYPE/` | Layer-specific templates and schemas (from `framework/`) |

**Rules**:

- Existing files are never overwritten (idempotent) in default mode.
- Source assets come from the framework canonical scaffold and `framework/` layer directories.
- Templates matching `*-TEMPLATE.*` are copied from layer directories.
- Active layer model is v3.2 8-layer flow (BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN). Deprecated layers (SYS, REQ, CTR, TSPEC, TASKS) remain archive-only and are not active outputs.

**Update mode** (`--update`):

- Overwrites stale templates and prompts with latest framework versions.
- `persona_mappings.yaml` is protected (project-owned after init). Use `--update --update-mappings` to explicitly reset it.
- `--update-mappings` without `--update` is invalid and fails command validation.
- Content-identical files are skipped (no unnecessary writes).
- Result reports `created_paths`, `skipped_paths`, `updated_paths`, `protected_paths`.

---

### Stage A.1.5 — Runtime Startup Gate (`runtime-start`)

Start required MCP runtimes before BRD creation:

```bash
# UCX lifecycle runtime
/opt/data/ucx_framework/.venv/bin/python -m mcp_server.server

# UCX KB runtime (required only in KB-enabled projects)
PYTHONPATH=/opt/data/ucx_framework /opt/data/ucx_framework/.venv/bin/python -m ucx_kb.mcp.server
```

Readiness checks before first BRD prompt build:

- Hermes MCP client can connect to `sdd-lifecycle`.
- `sdd_preflight` passes with status `ready` or approved `degraded`.
- KB-enabled projects: `kb_status` and `kb_graph_status` return without contract errors.

Hard gate:

- Do not run `sdd_create_build` for BRD until runtime-start checks pass.
- Environment bootstrap and all required framework tools must be available before any document creation stage starts.

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
| `creation_prompt.txt` | Assembled prompt ready for LLM input |
| `creation_prompt_sidecar.json` | Metadata: personas (list), doc type, layer assets used, template source, persona token estimates |
| `creation_prompt_inspection.json` | Prompt-bundle inspection diagnostics |
| Layer asset files | Unified YAML template, schema, and any project-tuned template bundled into the prompt |

**Rules**:

- Loads project-tuned template: tries `TYPE-TEMPLATE.yaml`, then `TYPE-TEMPLATE.md`, then `TYPE-MVP-TEMPLATE.md` from `UCX/templates/`. Falls back to layer template from `UCX/templates/layers/NN_TYPE/`.
- Does not write the final document artifact; use `create` for that.
- `--sections-json` injects existing document sections into the prompt for guided creation (incremental authoring).

---

### Initialization Flow Summary

```
venv-bootstrap
  └─ creates /opt/data/ucx_framework/.venv and installs runtime dependencies
        ↓
runtime-start
  └─ starts sdd-lifecycle (and project-knowledge when enabled) and verifies readiness
        ↓
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

The `venv-bootstrap` stage must complete before `runtime-start` and `init`. The `runtime-start` gate must pass before BRD `create-build`. The `init` command must run before any `create-build` or `create` command. `init` is safe to re-run; it will skip files that already exist.

---

## 4. Document Lifecycle Flow

This flow applies uniformly to active SSD v3.2 layers (BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN).

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
| `{DOC_ID}.ucx.validate.json`, `{DOC_ID}.ucx.validate.txt` | Always produced |
| `TYPE-NN_{slug}_validated.md` | Produced when validation errors are found (source-protected derived copy with fix instructions) |
| `{DOC_ID}.ucx.validate_fix.json`, `{DOC_ID}.ucx.validate_fix.txt` | Produced when validation errors are found |

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

**Output**: `review_prompt.txt`, `review_prompt_sidecar.json`, `review_prompt_inspection.json`

**Rules**:

- Review runs against the `_validated` copy, not the source.
- Multiple personas are loaded per the 2-tier resolution: explicit `--personas` override or `persona_mappings.yaml` defaults for the `(doc_type, review)` pair.
- Each persona receives only the document sections mapped to its domain categories.
- Deterministic prompt assembly only; command does not persist an LLM-authored review report.
- `review_mode=prompt_only` is default and implemented.
- `review_mode=saga_parallel` is implemented with bounded branch scheduling, saga state journal, deterministic reducer summary, and escalation-aware status fields.
- `saga_branch_llm_enabled` controls branch-level LLM fan-out in saga mode.
- rollout phase environment control `UCX_REVIEW_SAGA_BRANCH_LLM_PHASE` defaults behavior when explicit flag is absent (`A/B` off, `C` on).
- raw branch outputs are persisted only when `UCX_REVIEW_DEBUG_RAW_OUTPUTS=true` and must be redacted.
- In `--document` folder mode, the review pipeline collects `.md`, `.yaml`, and `.yml` files. YAML-first precedence applies when both `.yaml` and `.md` canonical sources exist. Legacy (`_LEGACY`) files are excluded. Appendix files are detected by name (`appendix`/`appendices`).

---

### Stage 4 — Remediate

**Command**: `remediate`

**Input**: `TYPE-NN_{slug}_validated.md` + optional `review_report`

**Output**: `{DOC_ID}.ucx.remediate.json`, `{DOC_ID}.ucx.remediate.txt`

**Rules**:

- Remediation runs against the `_validated` copy, not the source.
- Report is deterministic and stage-scoped (non-versioned file names).
- When `--document` points to a folder, MCP resolves the canonical source artifact (the `_validated` copy) automatically.

---

### Stage 5 — Remediate-Fix

**Command**: `remediate --fix`

> **Note**: The standalone `sdd_remediate_fix` MCP tool and `remediate-fix` CLI command have been absorbed into `sdd_remediate` with `fix=true` parameter. Use `remediate --fix` instead.

**Input**: `TYPE-NN_{slug}_validated.md` + optional `--remediation-report`

**Output**: `TYPE-NN_{slug}_remediate_v{N}.{ext}` (derived copy, written alongside source) + `{DOC_ID}.ucx.remediate_fix.json/.txt`

**Rules**:

- Input is the `_validated` copy, not the source.
- Output uses the canonical base name plus version suffix (`{slug}_remediate_v{N}.{ext}`), not `{slug}_validated_remediate_v{N}.{ext}`.
- When `--document` points to a folder, MCP resolves the `_validated` copy automatically.
- Source and `_validated` copy are not modified.
- `processing_stage: remediated` in derived copy metadata.
- `derived_from: TYPE-NN_{slug}_validated.md` in derived copy metadata.

**Remediation guidance (UCX V3 / v2.0+)**:

- Findings are grouped by priority phase: Phase 1 (P0 critical), Phase 2 (P1 high), Phase 3 (P2 enhancements).
- `sdd_remediate` returns deterministic findings/fix artifacts and API executor apply-stage output.
- Use API executor names for remediation apply stages; legacy CLI executor names are unsupported.

**Post-fix quality checks (UCX V3 / v2.0+)**:

- Re-run `sdd_validate` after remediation to confirm deterministic compliance and prevent regression.
- In governed PR pipelines, a Hermes final blocker-gap/inconsistency check runs after post-remediation validation.

---

## 5. Artifact Lineage and Naming

### Canonical Artifact Set (per document folder)

| Stage | Artifact | Filename Pattern | Mutates Prior Artifact |
| --- | --- | --- | --- |
| 1 | Source document | `TYPE-NN_{slug}.md` | No |
| 2 | Validation report | `{DOC_ID}.ucx.validate.json/.txt` | No |
| 2 | Validated copy (when errors found) | `TYPE-NN_{slug}_validated.md` | No |
| 2 | Validate-fix report (when errors found) | `{DOC_ID}.ucx.validate_fix.json/.txt` | No |
| 3 | Review prompt artifacts | `review_prompt.txt`, `review_prompt_sidecar.json`, `review_prompt_inspection.json` | No |
| 4 | Remediation report | `{DOC_ID}.ucx.remediate.json/.txt` | No |
| 5 | Remediated copy (`remediate --fix`) | `TYPE-NN_{slug}_remediate_v{N}.{ext}` | No |
| 5 | Remediate-fix report | `{DOC_ID}.ucx.remediate_fix.json/.txt` | No |

### Lineage Chain

```
TYPE-NN_{slug}.md
  └─ validate ──→ {DOC_ID}.ucx.validate.json
  │            ──→ TYPE-NN_{slug}_validated.md       (when errors found)
  │            ──→ {DOC_ID}.ucx.validate_fix.json/.txt (when errors found)
  │
  TYPE-NN_{slug}_validated.md
                        └─ review       ──→ review_prompt.txt + sidecar + inspection
                        └─ remediate    ──→ {DOC_ID}.ucx.remediate.json/.txt
                        └─ remediate --fix ──→ TYPE-NN_{slug}_remediate_v{N}.{ext}
                                           └→ {DOC_ID}.ucx.remediate_fix.json/.txt
```

### Reserved Suffixes

- `_validated` — UCX-derived copy from `validate` (when errors are found)
- `_remediate_v{N}` — UCX-derived copy from `remediate --fix` only
- These suffixes must not appear in canonical source document filenames.

### Source Artifact Resolution

When `--document` points to a folder, MCP applies the following resolution rules at each stage:

| Stage | Resolution rule |
| --- | --- |
| validate | Locate single file matching `^[A-Z]+-\d+_.+\.(md\|yaml\|yml)$` with no `_validated`, `_remediate_copy`, or `_remediate_v{N}` stem suffix; use it as the source. Fall back to full folder set if no unique match. |
| review | Collect all `.md`, `.yaml`, `.yml` files (excluding `_LEGACY`, `REVIEW`, `REPORT`, `_validated`, `_remediate_copy`, `_remediate_v{N}` stems). Identify canonical source via `^[A-Z]+-\d+_.+\.(md\|yaml\|yml)$` (excluding appendix files). YAML-first precedence when both formats exist. Append appendix files (detected by `appendix`/`appendices` in filename). |
| remediate | Locate single file matching `^[A-Z]+-\d+_.+_validated\.md$`; use it as the `_validated` input. Fall back to full folder set if no unique match. |
| remediate --fix | Locate single file matching `^[A-Z]+-\d+_.+_validated\.md$`; use it as the `_validated` input. Fall back to full folder set if no unique match. |

---

## 6. Diagnostics Flow

### 6.1 Readiness and lineage checks

1. Execute `preflight` before create, review, or remediation stages when environment or provider readiness must be verified.
2. Inspect `probe_status`, `probe_fallback_used`, and `probe_fallback_reason` when a probe payload is present.
3. Execute `consistency` against a file or folder to validate artifact lineage without re-running full validation.
4. Treat `preflight` blocked output and `consistency` failed output as CI-gating conditions.

Outputs:

- preflight report: `preflight_report.json`, `preflight_report.txt`
- consistency report: `consistency_report.json`, `consistency_report.txt`

### 6.2 Prescreen, scan, and scoring

1. Execute `prescreen` to identify high-priority candidate files.
2. Execute `scan` on JSON report files to extract finding-category counts.
3. Execute `scoring` commands for numeric quality scoring and comparisons.

Outputs:

- prescreen report: `prescreen_report.json`
- scan report: `scan_report.json`
- scoring payloads: JSON printed to stdout

---

## 7. PR Governance Flow (Hermes Default)

Hermes is the default AI agent orchestrating issue-to-merge governance.

### 7.1 Lifecycle Sequence

1. Define task (human or AI-originated).
2. Complete and approve planning-first governance artifacts for the target scope.
3. Create and prioritize GitHub issue with acceptance criteria and traceability tags.
4. Perform implementation work on a feature branch.
5. Submit pull request.
6. Execute Round 1 gates:
   - `sdd_validate` (deterministic structure and ID/naming checks)
   - `sdd_review` (UCX persona content review)
   - `sdd_remediate` (UCX persona remediation findings and fixes)
   - post-remediation `sdd_validate`
   - Hermes final blocker-gap/inconsistency review (non-deep-content)
7. If any blocking check fails in Round 1, execute Round 2 with the same sequence.
8. If Round 2 also fails, escalate to human review and block merge.
9. On successful merge, close linked GitHub issue(s).

### 7.2 Merge Gate Conditions

Merge is allowed only when all conditions are true:

- Final-round `sdd_validate` status is PASS.
- Round review/remediation sequence completed.
- Hermes final review status is PASS.
- Escalation status is not `REQUIRED`.

Alert channels for escalation and merge-time notifications are implementation-defined (TBD).

---

## 8. Operational Controls

Validation controls:

- `validate --tier1-only`
- `validate --strict`
- `validate --format {text,json}`

Review controls:

- `--personas`, `--unified`, `--one-turn`, `--no-resume`, `--session-ttl`
- `--clean-memory`, `--clean-reports`, `--keep-versions`
- `--review-mode {prompt_only,saga_parallel}`
- `--max-parallel-branches`, `--branch-timeout-seconds`, `--max-branch-retries`, `--retry-backoff-seconds`, `--saga-resume`, `--saga-branch-llm-enabled`

Saga mode note:

- `saga_parallel` persists branch/journal/reducer state and status for governance integration.
- Scheduler controls drive bounded concurrency, per-branch timeout, and retry/backoff behavior.
- branch telemetry includes executor/model/latency/token usage when available.

---

## 9. Exit Behavior

| Command Group | Pass | Fail |
| --- | --- | --- |
| validate | 0 | 1 |
| consistency | 0 | 1 for blocking lineage failures, 2 for runtime errors |
| preflight | 0 for ready or degraded | 1 for blocked, 2 for runtime errors |
| scoring validate | 0 | 1 |
| other implemented commands | 0 | 2 only for CLI usage/argument failures |

---

## 10. Evidence Commands

- `pytest ucx_hermes/tests/unit/test_cli_main.py`
- `pytest ucx_hermes/tests/unit/test_validation_runner.py`
- `pytest ucx_hermes/tests/unit/test_remediation_runner.py`
- `pytest ucx_hermes/tests/unit/test_prescreening.py`
- `pytest ucx_hermes/tests/unit/test_scoring_cli.py`
- `pytest ucx_hermes/tests/integration/test_migration_flows.py`
- `pytest ucx_hermes/tests/integration/test_lifecycle_pipeline_integration.py`
