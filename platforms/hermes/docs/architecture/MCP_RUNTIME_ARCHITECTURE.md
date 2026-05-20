# UCX Runtime Architecture

> **UCX** (Unified Context eXcelerator) — also known as `mcp_ucx` (legacy) or `sdd-lifecycle`. See [README](../README.md) for naming context.

| Field | Value |
| --- | --- |
| Canonical Name | UCX (Unified Context eXcelerator) |
| Status | Active |
| Version | 2.1 |
| Date | 2026-05-04 |
| Scope | Implemented runtime architecture for create, review, validation, fix, remediation, and diagnostics operations. Agent-agnostic context assembly for any AI agent via MCP and CLI. |

---

## 1. Purpose

Document implemented runtime architecture boundaries, component responsibilities, and execution flow. UCX provides agent-agnostic context assembly — any AI agent (Claude, Gemini, Copilot, Codex, OpenRouter) calls UCX via MCP or CLI to get project-specific personas, prompts, and templates.

Implementation complexity: 4/5.

---

## 2. Runtime Boundaries

In scope:

- CLI command entrypoint behavior
- Prompt assembly pipeline for creation and review
- Script-based structural validation pipeline for document checks
- Source-protected fix artifact generation (`validate-fix`, `remediate --fix`)
- Deterministic remediation planning (`remediate`)
- Diagnostics command group (`prescreen`, `scan`, `scoring`)
- Project UCX loading behavior
- Output artifact generation behavior

Out of scope:

- Future ingestion modes not implemented in runtime
- External skill implementations in project-local skill systems

---

## 3. Core Components

| Component | Path | Responsibility |
| --- | --- | --- |
| CLI entrypoint | ucx_hermes/src/mcp_server/cli/main.py | Parse command arguments and dispatch command handlers |
| Prompt assembly | ucx_hermes/src/mcp_server/prompts/context_builder.py | Build prompt bundles, metadata sidecars, and context contracts |
| Review and creation runner | ucx_hermes/src/mcp_server/review/runner.py | Execute assembly and optionally write prompt, sidecar, and inspection artifacts |
| Validation runner | ucx_hermes/src/mcp_server/validation/runner.py | Execute schema-guided structural validation and write JSON/TXT validation reports |
| Remediation runner | ucx_hermes/src/mcp_server/remediation/runner.py | Build remediation findings and generate derived fix artifacts |
| Prescreen runner | ucx_hermes/src/mcp_server/prescreening/runner.py | Detect high-priority remediation candidates |
| Scan runner | ucx_hermes/src/mcp_server/scan/runner.py | Aggregate finding categories from JSON reports |
| Scoring runner | ucx_hermes/src/mcp_server/scoring/runner.py | Compute, validate, and compare deterministic report scores |
| Project UCX loader | ucx_hermes/src/mcp_server/skills/project_ucx_loader.py | Resolve project-local personas/templates/layer assets; raise ProjectSkillsNotFound on missing paths (no fallback) |
| UCX scaffold | ucx_hermes/src/mcp_server/skills/scaffold.py | Copy framework assets to project UCX directory during init (no-overwrite semantics) |

---

## 4. Implemented Runtime Flows

### 4.1 init flow

1. CLI parses init command with project argument.
2. Runtime resolves project root path.
3. Scaffold service copies all framework assets into `{project}/UCX/` using `CANONICAL_SCAFFOLD_MAPPINGS`:
   - `skills/personas/` — 15 persona definition files
   - `skills/persona_mappings.yaml` — per-doctype, per-phase persona sequence configuration
   - `skills/layer_aliases/` — layer alias mappings
   - `prompts/templates/creation/` — UCC creation prompt templates
   - `prompts/templates/review/` — UCR review prompt templates
   - `prompts/templates/remediation/` — UCRem remediation prompt templates
   - `templates/` — document templates and layer-specific schemas (sourced from `framework/`)
4. Existing files are never overwritten (no-overwrite semantics; idempotent).
5. CLI reports created and skipped counts.

**Project isolation contract**: After init, all runtime operations load assets exclusively from the project's `UCX/` directory. Framework scaffold sources under `ucx_hermes/skills/` and `ucx_hermes/prompts/templates/` are never loaded at runtime. If required project assets are missing, the runtime raises `ProjectSkillsNotFound` — no fallback to framework defaults occurs.

### 4.2 create-build flow

1. CLI parses create-build arguments.
2. Runtime resolves personas using 2-tier priority:
   - Tier 1: Explicit `personas` parameter (if provided).
   - Tier 2: `persona_mappings.yaml` lookup by `(doc_type, create)` pair.
3. Runtime loads optional sections-json payload into SourceSection objects.
4. Runner invokes assemble_project_creation_prompt with the resolved persona list.
5. Project UCX loader resolves project-local persona files, templates, and layer assets for each persona.
6. Prompt bundle is validated. `PromptMetadataSidecar` includes `personas`, `persona_count`, `persona_token_estimate`, and `persona_token_warning` fields.
7. If output directory provided, creation artifacts are written.

Implemented behavior note:

- Direct markdown source ingestion as a first-class create-build mode is not implemented.
- Implemented source path is structured sections payload via sections-json or synthetic fallback behavior when omitted.

### 4.3 review-build flow

1. CLI parses review-build arguments.
2. Runtime validates `review_mode`:
   - `prompt_only` (default): canonical prompt-assembly path.
   - `saga_parallel`: bounded scheduler path with saga journal/reducer/status outputs.
3. Runtime resolves personas using 2-tier priority (explicit `personas` parameter or `persona_mappings.yaml` lookup by `(doc_type, review)`).
4. Runtime resolves one review source mode: sections-json payload or document auto-loading.
5. In document mode, runtime builds SourceSection objects from canonical main artifact plus appendix artifacts in the target folder. Document collection supports `.md`, `.yaml`, and `.yml` files. YAML-first precedence applies when both formats exist for the same canonical source. Legacy (`_LEGACY`) files are excluded from candidate lists.
6. Runner invokes assemble_project_review_prompt with the resolved persona list. Each persona receives sections mapped to its domain categories.
7. Prompt bundle is validated and inspection output generated.
8. If output directory provided, review artifacts are written.
9. In `saga_parallel`, runtime executes persona branches with bounded scheduling and retry/backoff controls, then emits deterministic saga status outputs (`review_run_id`, `saga_status`, branch/reducer summaries) in addition to prompt artifacts.
10. Branch-level LLM fan-out is enabled by `saga_branch_llm_enabled` (CLI/tool flag) or rollout environment controls (`UCX_REVIEW_SAGA_BRANCH_LLM_ENABLED`, `UCX_REVIEW_SAGA_BRANCH_LLM_PHASE`).
11. Branch outputs are parsed through strict JSON -> structured block extraction -> deterministic fallback finding emission.
12. Branch telemetry captures executor, model, latency, and token usage where provider metadata is available.
13. Raw branch output persistence is debug-only (`UCX_REVIEW_DEBUG_RAW_OUTPUTS=true`) and persisted text is redacted before artifact write.

### 4.4 validate flow

1. CLI parses validate arguments.
2. Runtime resolves document file or document directory input.
   - If input is a markdown file and parent folder has one canonical source artifact, validation redirects to that canonical source for any non-source markdown input.
   - This canonical redirection behavior applies across all document layers.
3. Validation runner loads project layer schema/template assets from UCX/templates/layers/{layer}.
4. Validation checks execute for required frontmatter custom fields, required tags, and required section regex patterns.
5. Validation runner emits validation_report.json and validation_report.txt when output path is configured.
6. CLI returns exit code 0 for pass and 1 for fail.

Document format support: The validation pipeline supports both `.md` and `.yaml` document formats. YAML documents follow the same lifecycle pipeline with YAML-specific structure validation (required keys, element ID format, empty section detection) applied during the validation and remediation stages. Frontmatter checks are skipped for `.yaml` files since YAML documents are structured data, not Markdown with frontmatter.

### 4.5 fix and remediation flow

1. `validate-fix` (deprecated alias of `validate`) generates `_validated` derived artifact(s) with source protection enabled when validation errors are present.
2. `remediate` generates deterministic findings and remediation report artifacts. Review findings are sorted by priority (P0→P1→P2) before the 50-finding cap. `recommended_action` text preserved up to 2000 chars.
3. `remediate --fix` (internally `sdd_remediate` with `fix=true`) generates versioned `_remediate_v{N}` derived artifact(s) with source protection enabled. The standalone `sdd_remediate_fix` MCP tool has been absorbed into `sdd_remediate`. An optional `remediation_report` parameter can supply a pre-existing report. Executor prompt includes phased findings (P0/P1/P2), embedded document content (50K cap), and 6-step fix strategy with FWDREF handling and section ordering rules.
4. `verify_remediation_quality()` runs post-executor: detects cosmetic FWDREF renames, stub sections (<50 words), low content delta. Returns `quality_pass` flag in tool output under `remediation_quality`.
5. In pipeline mode (`sdd_run_lifecycle`), `sdd_validate` auto-runs on the derived copy after step 3 to catch regressions. Result under `post_remediation_verify`. The `clean_before` parameter on `sdd_run_lifecycle` triggers `sdd_clean` to prune obsolete stage artifacts before the pipeline starts.

### 4.6 diagnostics flow

1. `prescreen` identifies candidate documents for remediation prioritization.
2. `scan` aggregates category counts from report JSON.
3. `scoring` computes numeric score payloads and supports validate/compare operations.

---

## 5. Error Handling Contracts

### 5.1 Missing project UCX assets

Error type:

- ProjectSkillsNotFound

Required payload fields:

- error_code
- project_root
- missing_paths
- resolution

Required resolution string:

- Run mcp init --project {project_root} to create project-specific files.

### 5.2 Persona mapping failures

**Structural YAML errors** raise `PersonaMappingError`:

- `persona_mappings.yaml` has missing `version` field or empty `personas` list.
- No mapping entry exists for the requested `(doc_type, phase)` pair and no explicit `personas` parameter was provided.

Required payload fields:

- error_code
- doc_type
- phase
- resolution

**Missing persona files** raise `ProjectSkillsNotFound`:

- A persona identifier in the mapping references a non-existent persona file. The `_validate_persona_mapping` function raises `ProjectSkillsNotFound` with `missing_paths` listing the absent files.

### 5.2.1 Persona mapping caching

`load_persona_mapping()` caches results keyed on `(project_root, mtime)`. The YAML file is re-read only when its filesystem modification time changes. This mtime-based LRU cache prevents redundant file reads during multi-stage lifecycle runs within the same project.

### 5.2.2 Early UCX root validation

`validate_project_ucx_root()` checks `_REQUIRED_FILES` including `persona_mappings.yaml` for early detection of missing project assets before persona resolution runs. This catches missing files at project load time rather than at persona resolution time.

### 5.3 Contract validation failures

Error type:

- ContractValidationError

Failure condition:

- prompt bundle fails context or metadata sidecar validation.

---

## 6. Resource Requirements and Constraints

- CPU: moderate for prompt assembly and validation
- Memory: moderate for section and metadata payloads
- Storage: required only for optional artifact outputs
- Constraint: runtime behavior documentation must map to implemented code paths

---

## 7. Failure Modes

| Failure Mode | Detection Point | Required Behavior |
| --- | --- | --- |
| Missing UCX directory set | project loader validation | raise ProjectSkillsNotFound |
| Structural persona_mappings.yaml errors (missing version, empty personas, no mapping entry) | persona resolution stage | raise PersonaMappingError with doc_type, phase, and resolution |
| Missing persona files referenced in persona_mappings.yaml | `_validate_persona_mapping` in persona resolution stage | raise ProjectSkillsNotFound with missing_paths |
| Invalid sections-json payload shape | CLI deserialization stage | command failure with parse error |
| Prompt bundle contract invalid | assembly validation stage | raise ContractValidationError |
| Missing or invalid YAML frontmatter in target document | validation runner stage | mark validation as failed and report error |
| Required schema-driven fields/tags/sections not satisfied | validation runner stage | mark validation as failed and report violations |
| Output path not writable | artifact write stage | command failure with I/O error |
