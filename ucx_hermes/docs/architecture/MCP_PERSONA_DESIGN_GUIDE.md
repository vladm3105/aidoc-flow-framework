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
- `{project_root}/UCX/skills/persona_mappings.yaml`
- `{project_root}/UCX/skills/layer_aliases/`
- `{project_root}/UCX/prompts/templates/creation/`
- `{project_root}/UCX/prompts/templates/review/`
- `{project_root}/UCX/prompts/templates/remediation/`

### 3.2 Persona Mapping Configuration

`persona_mappings.yaml` is the canonical source for per-doctype, per-phase persona sequences. It is located at `{project}/UCX/skills/persona_mappings.yaml` and scaffolded by `sdd_init`.

**Format**:

```yaml
mappings:
  brd:
    create:
      personas: [architect, strategist, business_analyst]
      mode: sequential
    review:
      personas: [architect, auditor, tech_lead, chaos_engineer, operator, chairperson]
      mode: parallel
    remediate:
      personas: [tech_lead, auditor]
      mode: sequential
  prd:
    create:
      personas: [product_owner, ux_strategist, tech_lead]
      mode: sequential
    review:
      personas: [architect, auditor, tech_lead, product_owner, chairperson]
      mode: parallel
```

The `mode` field (`sequential`, `parallel`, `adaptive`) is metadata-only in v1.0. It is not read by the runtime and has no effect on execution. It serves as documentation for intended execution semantics in future versions.

### 3.3 Persona Resolution Priority (2-Tier)

The runtime resolves personas using a 2-tier priority:

| Priority | Source | Behavior |
| --- | --- | --- |
| 1 (highest) | Explicit `personas` parameter on tool call or CLI | Overrides all defaults |
| 2 (default) | `persona_mappings.yaml` lookup by `(doc_type, phase)` | Used when no explicit `personas` parameter is provided |

There is no single `persona` parameter. All tools and CLI commands accept only `personas` (list/array). If neither source provides a persona list, the runtime raises `PersonaMappingError`.

### 3.4 MCP bundled assets usage

Bundled assets under framework MCP paths are used only as scaffold input for `mcp init`.
They are not loaded by runtime execution paths.

### 3.5 Missing asset behavior

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

The `PERSONA_CATEGORY_MAP` defines 15 personas. All personas are registered in the runtime and available for assignment in `persona_mappings.yaml`.

### 4.1 Complete Persona Registry (15 personas)

| Persona | Primary Responsibility | Category | Finding Prefix |
| --- | --- | --- | --- |
| `architect` | Structure, boundaries, scalability | technical | ARCH |
| `auditor` | Compliance, policy, risk | compliance | AUD |
| `tech_lead` | Feasibility and implementation constraints | technical | TL |
| `strategist` | Business strategy, unit economics | functional | STR |
| `chaos_engineer` | Failure mode and edge-case analysis | risk | CE |
| `operator` | Operability, rollback, diagnostics | operations | OP |
| `integration_lead` | Contract boundaries and dependency impacts | integration | IL |
| `product_owner` | MVP scope, user personas | functional | PO |
| `business_analyst` | Requirements, traceability | functional | BA |
| `fact_checker` | Cross-validation, accuracy, scope-mismatch detection | quality | FC |
| `chairperson` | Synthesis, scoring, final recommendation, applicability veto | quality | REM |
| `qa_lead` | Testability, BDD, verification | quality | QA |
| `requirements_specialist` | EARS and REQ formal requirements | functional | RS |
| `ux_strategist` | PRD and UX-focused requirements | functional | UX |
| `judge` | High-stakes approvals, external audit | compliance | JDG |

### 4.2 Remediation Adaptive Loading

During remediation, personas use `loading: adaptive` semantics. Domain personas are loaded only when review findings match their registered categories. This prevents loading irrelevant persona context for remediation runs where a persona's category has no findings.

### 4.3 Applicability Controls (v1.20.0+)

Three personas contribute to regulatory applicability filtering during review:

1. **Auditor** — APPLICABILITY CHECK: verifies regulation is relevant to the document's stated domain before flagging as P0. Out-of-scope regulations classified as P1 "Scope Gap".
2. **Fact Checker** — detects scope misunderstandings where findings flag requirements inapplicable to the document's domain. Added to default BRD review sequence in v1.20.0.
3. **Chairperson** — Applicability Veto (synthesis principle #4): excludes out-of-scope findings from score calculation. Vetoed findings listed separately in manifest under `out_of_scope_findings`.

This layered approach reduces false-positive P0 findings from generic regulatory frameworks being applied to documents where those regulations are not in scope.

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

Required metadata fields (`PromptMetadataSidecar`):
- `personas` — `list[str]` of persona identifiers loaded for the prompt
- `persona_count` — integer count of loaded personas
- `persona_token_estimate` — estimated token cost for all persona content
- `persona_token_warning` — boolean flag when persona token cost exceeds `TOKEN_WARNING_THRESHOLD` (15,000 tokens)
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
| Missing `persona_mappings.yaml` | startup resolver | raise `ProjectSkillsNotFound` |
| Structural YAML errors (missing version, empty personas list) | persona resolution | raise `PersonaMappingError` with doc_type, phase, and resolution guidance |
| No mapping entry for `(doc_type, phase)` | persona resolution | raise `PersonaMappingError` |
| Missing persona files referenced in mapping | `_validate_persona_mapping` | raise `ProjectSkillsNotFound` with missing_paths |
| Missing layer alias map | startup resolver | raise `ProjectSkillsNotFound` |
| Missing prompt template family | startup resolver | raise `ProjectSkillsNotFound` |
| Persona finding schema drift | parser stage | contract test failure |
| Missing metadata sidecar fields | diagnostics stage | contract test failure |
| Non-deterministic scoring/context output | regression stage | determinism test failure |

## 9. Implementation Status

| Capability | Status | Source |
| --- | --- | --- |
| Persona and context contracts defined | Implemented | `ucx_hermes/docs/specs/SPEC-002_*` |
| Runtime policy for project-specific-only loading | Implemented | `ucx_hermes/src/mcp_server/skills/project_ucx_loader.py` |
| `mcp init` scaffold with no-overwrite semantics | Implemented | `ucx_hermes/src/mcp_server/skills/scaffold.py` |
| `ProjectSkillsNotFound` error contract | Implemented | `ucx_hermes/src/mcp_server/skills/project_ucx_loader.py` |
| Context-engineering runtime (prompt assembly) | Implemented | `ucx_hermes/src/mcp_server/prompts/context_builder.py` |
| Project-specific UCX runtime loader | Implemented | `ucx_hermes/src/mcp_server/skills/project_ucx_loader.py` |
| Review prompt build runner and artifact emission | Implemented | `ucx_hermes/src/mcp_server/review/runner.py` |
| Creation prompt assembly and layer asset loading | Implemented | `ucx_hermes/src/mcp_server/prompts/context_builder.py` |
| Sidecar metadata and inspection diagnostics | Implemented | `ucx_hermes/src/mcp_server/prompts/context_builder.py` |
| Scaffold mapping for all 6 asset categories | Implemented | `ucx_hermes/src/mcp_server/skills/scaffold.py` |

## 10. Scaffold Contract

`sdd_init` copies all framework assets into `{project}/UCX/` using the mappings defined in `scaffold.py:CANONICAL_SCAFFOLD_MAPPINGS`. Seven asset categories are copied:

1. `skills/personas` — 15 persona definition files
2. `skills/persona_mappings.yaml` — per-doctype, per-phase persona sequence configuration
3. `skills/layer_aliases` — layer alias mappings
4. `prompts/templates/creation` — UCC creation prompt templates
5. `prompts/templates/review` — UCR review prompt templates
6. `prompts/templates/remediation` — UCRem remediation prompt templates
7. `templates` — document templates and layer-specific schemas (from `ucx_flow_v3/`)

No-overwrite semantics: existing files in the project UCX directory are never overwritten. Re-running `sdd_init` is safe and idempotent.

After initialization, the project owns its UCX assets. Teams customize personas, prompts, and templates in `{project}/UCX/` without affecting other projects or the framework scaffold source.
