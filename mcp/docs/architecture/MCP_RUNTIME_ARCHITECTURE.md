# MCP Runtime Architecture

| Field | Value |
| --- | --- |
| Status | Active |
| Version | 1.0 |
| Date | 2026-03-24 |
| Scope | Implemented runtime architecture for init, create-build, and review-build operations |

---

## 1. Purpose

Document implemented runtime architecture boundaries, component responsibilities, and execution flow.

Implementation complexity: 4/5.

---

## 2. Runtime Boundaries

In scope:
- CLI command entrypoint behavior
- Prompt assembly pipeline for creation and review
- Project UCX loading behavior
- Output artifact generation behavior

Out of scope:
- Future ingestion modes not implemented in runtime
- External skill implementations in project-local skill systems

---

## 3. Core Components

| Component | Path | Responsibility |
| --- | --- | --- |
| CLI entrypoint | mcp/src/mcp_server/cli/main.py | Parse command arguments and dispatch command handlers |
| Prompt assembly | mcp/src/mcp_server/prompts/context_builder.py | Build prompt bundles, metadata sidecars, and context contracts |
| Review and creation runner | mcp/src/mcp_server/review/runner.py | Execute assembly and optionally write prompt, sidecar, and inspection artifacts |
| Project UCX loader | mcp/src/mcp_server/skills/project_ucx_loader.py | Resolve project-local personas/templates/layer assets and enforce missing-path errors |
| UCX scaffold | mcp/src/mcp_server/skills/scaffold.py | Initialize project-local docs/UCX file structure |

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
2. Runtime loads required sections-json payload into SourceSection objects.
3. Runner invokes assemble_project_review_prompt.
4. Prompt bundle is validated and inspection output generated.
5. If output directory provided, review artifacts are written.

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
| Output path not writable | artifact write stage | command failure with I/O error |
