---
title: MCP Persona Design Guide
tags:
  - mcp
  - architecture
  - personas
  - context-engineering
  - layer-architecture
custom_fields:
  document_type: architecture-guide
  layer: 9
  status: draft
  implementation_complexity: 4
---

# MCP Persona Design Guide

## 1. Purpose

Define MCP-native persona behavior, runtime loading rules, and context-engineering contracts for create/review/remediate toolchains.

## 2. Scope

In scope:
- Persona taxonomy and role boundaries for MCP tools.
- Runtime source resolution for project-specific personas, skills, and prompts.
- Context-engineering requirements for prompt assembly and diagnostics.
- Error conditions when project-specific assets are missing.

Out of scope:
- Canonical contract definitions (owned by SPEC-001..SPEC-004).
- UI workflow concerns.

## 3. Runtime Source Policy (Normative)

### 3.1 Source-of-truth at runtime

At runtime, MCP loads personas/skills/prompts from project scope only:
- `{project_root}/UCX/skills/personas/`
- `{project_root}/UCX/skills/layer_aliases/`
- `{project_root}/UCX/prompts/templates/creation/`
- `{project_root}/UCX/prompts/templates/review/`
- `{project_root}/UCX/prompts/templates/remediation/`

### 3.2 MCP bundled assets usage

Bundled assets under framework MCP paths are used only as scaffold input for `mcp init`.
They are not loaded by runtime execution paths.

### 3.3 Missing asset behavior

If required project-specific paths are missing, MCP must raise:
- `ProjectSkillsNotFound`

Minimum error payload fields:
- `error_code`
- `project_root`
- `missing_paths`
- `resolution`

Required resolution message:
- `Run mcp init --project {project_root} to create project-specific files.`

## 4. Persona Taxonomy

### 4.1 Required core personas

| Persona | Primary Responsibility | Applies To |
| --- | --- | --- |
| architect | Structure, boundaries, scalability | review, create |
| auditor | Compliance, policy, risk | review, remediate |
| tech_lead | Feasibility and implementation constraints | review, create, remediate |
| chaos_engineer | Failure mode and edge-case analysis | review, remediate |
| operator | Operability, rollback, diagnostics | review, remediate |
| integration_lead | Contract boundaries and dependency impacts | review, create, remediate |
| chairperson | Synthesis and final recommendation | review |

### 4.2 Optional personas

| Persona | Enable Condition |
| --- | --- |
| judge | High-stakes approvals, external audit, regulated cutover |
| chairperson_editor | Publication quality review package required |

### 4.3 Layer-specific personas

| Persona | Primary Layers |
| --- | --- |
| qa_lead | TSPEC and verification-heavy artifacts |
| requirements_specialist | EARS and REQ style artifacts |
| ux_strategist | PRD and UX-focused requirements |

## 5. Persona Output Contract

This guide consumes SPEC-002 Section 4 as normative source.

Required finding fields:
- `finding_id`
- `priority`
- `category`
- `persona`
- `message`
- `target_layer`

Priority domain:
- `P0`
- `P1`
- `P2`
- `P3`

## 6. Context Engineering Requirements

This guide consumes SPEC-002 Section 5 and Section 6 as normative source.

### 6.1 Required context behavior

Prompt assembly must implement:
- Persona-mapped section inclusion.
- Section skip list emission.
- Hybrid keyword-discovered snippets.
- Appendix index mode with optional verification tags.
- Dynamic mapping confidence output.

Required context fields:
- `sections_included`
- `sections_skipped`
- `discovered_snippets`
- `appendix_index`
- `token_estimate`

### 6.2 Required prompt diagnostics

Prompt diagnostics must emit deterministic sidecar metadata.

Required metadata fields:
- `persona`
- `doc_type`
- `structure_blocks`
- `sections.included`
- `sections.skipped`
- `tokens.total`

### 6.3 Minimum verification checks

For each persona prompt build:
- Validate required context fields exist.
- Validate required metadata sidecar fields exist.
- Validate deterministic output for repeated identical inputs.

## 7. Initialization and Runtime Sequence

1. `mcp init --project {project_root}` creates project-specific UCX files from MCP scaffold templates.
2. Team customizes project-specific personas/skills/prompts in `{project_root}/UCX/`.
3. MCP runtime resolves project-specific assets only.
4. MCP rejects runtime execution with `ProjectSkillsNotFound` when required assets are absent.

## 8. Failure Modes

| Failure Mode | Detection Point | Required Behavior |
| --- | --- | --- |
| Missing project personas dir | startup resolver | raise `ProjectSkillsNotFound` |
| Missing layer alias map | startup resolver | raise `ProjectSkillsNotFound` |
| Missing prompt template family | startup resolver | raise `ProjectSkillsNotFound` |
| Persona finding schema drift | parser stage | contract test failure |
| Missing metadata sidecar fields | diagnostics stage | contract test failure |
| Non-deterministic scoring/context output | regression stage | determinism test failure |

## 9. Implementation Status (Current Repository Snapshot)

| Capability | Status | Source |
| --- | --- | --- |
| Persona and context contracts defined | Defined | `mcp_sdd/docs/specs/SPEC-002_*` |
| Runtime policy for project-specific-only loading | Defined | `mcp_sdd/docs/plans/IPLAN-001_*` |
| `mcp init` behavior in implementation plan | Implemented | `mcp_sdd/src/mcp_server/skills/scaffold.py`, `mcp_sdd/src/mcp_server/cli/main.py` |
| Context-engineering runtime implementation | Partial implementation present | `mcp_sdd/src/mcp_server/prompts/context_builder.py` |
| Project-specific UCX runtime loader | Partial implementation present | `mcp_sdd/src/mcp_server/skills/project_ucx_loader.py` |
| Review prompt build runner and artifact emission | Implemented | `mcp_sdd/src/mcp_server/review/runner.py`, `mcp_sdd/src/mcp_server/cli/main.py` |

## 10. Implementation Gate

Implementation-ready for persona/context subsystem requires all conditions:
- Project-specific resolver implemented and tested.
- `ProjectSkillsNotFound` error contract implemented and tested.
- `mcp init` command scaffolding implemented and tested.
- Context-engineering fields and sidecar diagnostics implemented per SPEC-002 Sections 5-6.
- Determinism and schema regression tests passing.

Current status:
- Resolver and `ProjectSkillsNotFound` contract are partially implemented and tested.
- Context bundle assembly, sidecar serialization, dynamic mapping, and prompt inspection are partially implemented and tested.
- `mcp init` scaffolding command is implemented and tested with no-overwrite semantics.
- Review prompt build path emits prompt text, sidecar metadata, and inspection artifacts with tests.
