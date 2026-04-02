# MCP Runtime Architecture

| Field | Value |
| --- | --- |
| Status | Active |
| Version | 1.2 |
| Date | 2026-03-27 |
| Scope | Implemented runtime architecture for create, review, validation, fix, remediation, and diagnostics operations |

---

## 1. Purpose

Document implemented runtime architecture boundaries, component responsibilities, and execution flow.

Implementation complexity: 4/5.

---

## 2. Runtime Boundaries

In scope:

- CLI command entrypoint behavior
- Prompt assembly pipeline for creation and review
- Script-based structural validation pipeline for document checks
- Source-protected fix artifact generation (`validate-fix`, `remediate-fix`)
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
| CLI entrypoint | mcp_sdd/src/mcp_server/cli/main.py | Parse command arguments and dispatch command handlers |
| Prompt assembly | mcp_sdd/src/mcp_server/prompts/context_builder.py | Build prompt bundles, metadata sidecars, and context contracts |
| Review and creation runner | mcp_sdd/src/mcp_server/review/runner.py | Execute assembly and optionally write prompt, sidecar, and inspection artifacts |
| Validation runner | mcp_sdd/src/mcp_server/validation/runner.py | Execute schema-guided structural validation and write JSON/TXT validation reports |
| Remediation runner | mcp_sdd/src/mcp_server/remediation/runner.py | Build remediation findings and generate derived fix artifacts |
| Prescreen runner | mcp_sdd/src/mcp_server/prescreening/runner.py | Detect high-priority remediation candidates |
| Scan runner | mcp_sdd/src/mcp_server/scan/runner.py | Aggregate finding categories from JSON reports |
| Scoring runner | mcp_sdd/src/mcp_server/scoring/runner.py | Compute, validate, and compare deterministic report scores |
| Project UCX loader | mcp_sdd/src/mcp_server/skills/project_ucx_loader.py | Resolve project-local personas/templates/layer assets and enforce missing-path errors |
| UCX scaffold | mcp_sdd/src/mcp_server/skills/scaffold.py | Initialize project-local docs/UCX file structure |

---

## 4. Implemented Runtime Flows

### 4.1 init flow

1. CLI parses init command with project argument.
2. Runtime resolves project root path.
3. Scaffold service creates project-local docs/UCX directories and files.
4. CLI reports created and skipped counts.

### 4.2 create-build flow

1. CLI parses create-build arguments.
2. Runtime loads optional sections-json payload into SourceSection objects.
3. Runner invokes assemble_project_creation_prompt.
4. Project UCX loader resolves project-local persona, template, and layer assets.
5. Prompt bundle is validated.
6. If output directory provided, creation artifacts are written.

Implemented behavior note:

- Direct markdown source ingestion as a first-class create-build mode is not implemented.
- Implemented source path is structured sections payload via sections-json or synthetic fallback behavior when omitted.

### 4.3 review-build flow

1. CLI parses review-build arguments.
2. Runtime resolves one review source mode: sections-json payload or document auto-loading.
3. In document mode, runtime builds SourceSection objects from canonical main artifact plus appendix artifacts in the target folder.
4. Runner invokes assemble_project_review_prompt.
5. Prompt bundle is validated and inspection output generated.
6. If output directory provided, review artifacts are written.

### 4.4 validate flow

1. CLI parses validate arguments.
2. Runtime resolves document file or document directory input.
   - If input is a markdown file and parent folder has one canonical source artifact, validation redirects to that canonical source for any non-source markdown input.
   - This canonical redirection behavior applies across all document layers.
3. Validation runner loads project layer schema/template assets from docs/UCX/templates/layers/{layer}.
4. Validation checks execute for required frontmatter custom fields, required tags, and required section regex patterns.
5. Validation runner emits validation_report.json and validation_report.txt when output path is configured.
6. CLI returns exit code 0 for pass and 1 for fail.

Document format support: The validation pipeline supports both `.md` and `.yaml` document formats. YAML documents follow the same lifecycle pipeline with YAML-specific structure validation (required keys, element ID format, empty section detection) applied during the validation and remediation stages. Frontmatter checks are skipped for `.yaml` files since YAML documents are structured data, not Markdown with frontmatter.

### 4.5 fix and remediation flow

1. `validate-fix` generates `_validation` derived artifact(s) with source protection enabled.
2. `remediate` generates deterministic findings and remediation report artifacts.
3. `remediate-fix` generates `_remediated` derived artifact(s) with source protection enabled.

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

### 5.2 Contract validation failures

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
| Invalid sections-json payload shape | CLI deserialization stage | command failure with parse error |
| Prompt bundle contract invalid | assembly validation stage | raise ContractValidationError |
| Missing or invalid YAML frontmatter in target document | validation runner stage | mark validation as failed and report error |
| Required schema-driven fields/tags/sections not satisfied | validation runner stage | mark validation as failed and report violations |
| Output path not writable | artifact write stage | command failure with I/O error |
