# MCP_SDD Tool Creation List

| Field | Value |
| --- | --- |
| Document | Tool Creation List |
| Date | 2026-03-23 |
| Source | mcp_ssd migrated files |
| Scope | PLAN-012 PRD flow only |
| Status | Revised against PLAN-012 |

## Objective

Define the MCP tool surface for the PRD-only workflow described in PLAN-012.
The immediate migration target is the six-stage PRD derived-artifact flow and only the support tools required to run that flow safely.

## PLAN-012 Alignment

PLAN-012 defines this PRD flow:

1. Create canonical source PRD
2. Generate validation report
3. Generate `_validation` PRD copy with deterministic fixes
4. Generate review report against `_validation` copy
5. Generate remediation report against `_validation` copy
6. Generate `_remediated` PRD copy with remediation fixes applied

The MCP_SDD tool list below maps directly to those six stages.

## Primary PRD Tools

| Stage | MCP Tool | Purpose | Legacy source |
| --- | --- | --- | --- |
| 1 | prd_create | Create canonical source PRD from upstream/reference inputs | mcp_ssd/api/creation.py |
| 2 | prd_validate | Generate deterministic validation report only | mcp_ssd/validators/prd.py, mcp_ssd/validators/prd/* |
| 3 | prd_validate_fix | Create `_validation` PRD copy from source PRD | mcp_ssd/mcp/tools_prd.py, mcp_ssd/validators/prd/fixer.py |
| 4 | prd_review | Review `_validation` PRD and write review report | mcp_ssd/api/review.py, mcp_ssd/mcp/tools_prd.py |
| 5 | prd_remediate | Generate remediation report from review report | mcp_ssd/api/remediation.py, mcp_ssd/mcp/tools_prd.py |
| 6 | prd_remediate_apply | Create `_remediated` PRD copy from remediation report | mcp_ssd/mcp/tools_prd.py |

## Support Tools

These are useful for operating the six-stage PRD flow but are not themselves workflow stages.

| Tool | Purpose | Legacy source |
| --- | --- | --- |
| prd_artifacts | Discover all PLAN-012 artifacts in a PRD directory | mcp_ssd/mcp/tools_prd.py |
| prd_status | Report current PLAN-012 stage and recommended next step | mcp_ssd/mcp/tools_prd.py |
| sdd_health | Return MCP_SDD health and version state | mcp_ssd/mcp/server.py |

## Tool Contracts

### 1. prd_create

Inputs:
- target
- from_ref optional
- from_upstream optional
- profile optional

Outputs:
- status
- path
- findings
- next_step
- data: doc_id, doc_type, created

Implementation note:
- Wrap the migrated `UCCPhase.create(..., doc_type="prd")` path.
- Output must be source PRD only, matching PLAN-012 Stage 1.

### 2. prd_validate

Inputs:
- source_prd_path
- strict optional
- profile optional
- tier1_only optional

Outputs:
- status
- path
- findings
- next_step
- data: report_path, error_count, warning_count, pass_count

Implementation note:
- This tool must be report-only for PRD, matching PLAN-012 Stage 2.
- It must not mutate the source PRD.

### 3. prd_validate_fix

Inputs:
- source_prd_path
- dry_run optional
- max_iterations optional

Outputs:
- status
- path
- findings
- next_step
- data: output_path, fixes_applied, iterations_run, remaining_issue_count, processing_stage

Implementation note:
- This is already present in migrated PRD MCP code.
- Output must be `_validation` PRD only, matching PLAN-012 Stage 3.

### 4. prd_review

Inputs:
- prd_path

Outputs:
- status
- path
- findings
- next_step
- data: report_path, score, total_findings, has_critical, validation_prd_path

Implementation note:
- Must review the `_validation` PRD copy, not the canonical source PRD.
- This matches PLAN-012 Stage 4.

### 5. prd_remediate

Inputs:
- validation_prd_path
- review_report_path optional

Outputs:
- status
- path
- findings
- next_step
- data: report_path, fix_count, auto_safe_count, manual_review_count

Implementation note:
- Must generate remediation report only.
- Must operate on the `_validation` PRD copy, matching PLAN-012 Stage 5.

### 6. prd_remediate_apply

Inputs:
- validation_prd_path
- remediation_report_path
- dry_run optional

Outputs:
- status
- path
- findings
- next_step
- data: output_path, fixes_applied, processing_stage, derived_from

Implementation note:
- This is already present in migrated PRD MCP code.
- Output must be `_remediated` PRD only, matching PLAN-012 Stage 6.

## Migration Decision

Create now:
- prd_create
- prd_validate
- prd_validate_fix
- prd_review
- prd_remediate
- prd_remediate_apply
- prd_artifacts
- prd_status
- sdd_health

Do not prioritize now:
- non-PRD layer tools
- generic legacy `ucx_*` wrappers as public MCP tools
- batch, drift, autopilot, and cross-layer status tools

## Required Runtime Dependencies For PRD Focus

The six PRD tools require these migrated packages:

- mcp_ssd/api
- mcp_ssd/models
- mcp_ssd/core/context_engine.py
- mcp_ssd/core/persona_prompts.py
- mcp_ssd/core/review_memory.py
- mcp_ssd/prescreening
- mcp_ssd/scoring
- mcp_ssd/skills/loader.py
- mcp_ssd/prompts/loader.py
- mcp_ssd/config/layer_skills.py
- mcp_ssd/validators/prd
- mcp_ssd/utils

## Registration Order

1. sdd_health
2. prd_create
3. prd_validate
4. prd_validate_fix
5. prd_review
6. prd_remediate
7. prd_remediate_apply
8. prd_artifacts
9. prd_status

## Recommended Next Action

Use this list as the implementation scope for PLAN-002, limited to the PRD six-stage flow from PLAN-012.
