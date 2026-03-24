# MCP_SDD Migration Inventory

| Field | Value |
| --- | --- |
| Document | Migration Inventory |
| Date | 2026-03-23 |
| Source | UCX_v1_archive |
| Target | mcp_ssd |
| Copied Python Files | 93 |
| Keep Now | 79 |
| Defer or Remove | 14 |

## Purpose

This inventory lists every Python file already copied from UCX_v1_archive into mcp_ssd.
It also records whether each file is required for the MCP_SDD baseline migration.
No additional files should be copied until the Keep Now set is rewired and validated.

## Decision Rules

Keep Now:
- required for MCP server startup
- required for the PLAN-012 PRD six-stage flow
- required by shared validation utilities, config, or minimal runtime support

Defer or Remove:
- outside current MCP_SDD scope
- not required for current layer families
- observability or ancillary logic not needed for first runnable baseline
- legacy wrappers superseded by narrower layer-specific modules

## Copied Python Files

| Path | Decision | Rationale |
| --- | --- | --- |
| mcp_ssd/__init__.py | Keep Now | Minimal package compatibility anchor |
| mcp_ssd/exceptions.py | Keep Now | Shared exception definitions |
| mcp_ssd/version.py | Keep Now | Version surface for server/runtime |
| mcp_ssd/mcp/__init__.py | Keep Now | MCP package anchor |
| mcp_ssd/mcp/resources.py | Keep Now | Server resources currently part of archive MCP layer |
| mcp_ssd/mcp/server.py | Keep Now | Migrated FastMCP server baseline |
| mcp_ssd/mcp/tools.py | Keep Now | Core MCP tool registration baseline |
| mcp_ssd/mcp/tools_prd.py | Keep Now | Existing PRD MCP tool implementation |
| mcp_ssd/config/__init__.py | Keep Now | Config package anchor |
| mcp_ssd/config/defaults.py | Keep Now | Default runtime settings |
| mcp_ssd/config/schema.py | Keep Now | Config schema support |
| mcp_ssd/config/settings.py | Keep Now | Server configuration object |
| mcp_ssd/config/layer_skills.py | Keep Now | Required by creation, review, and remediation phase loading |
| mcp_ssd/api/__init__.py | Keep Now | API package anchor |
| mcp_ssd/api/creation.py | Keep Now | UCCPhase runtime for PRD create |
| mcp_ssd/api/review.py | Keep Now | UCRPhase runtime for PRD review |
| mcp_ssd/api/remediation.py | Keep Now | UCRemPhase runtime for PRD remediate |
| mcp_ssd/models/__init__.py | Keep Now | Models package anchor |
| mcp_ssd/models/document.py | Keep Now | Document model used by PRD creation |
| mcp_ssd/models/drift_cache.py | Keep Now | Package completeness for migrated models namespace |
| mcp_ssd/models/enums.py | Keep Now | DocType and status enums used by API phases |
| mcp_ssd/models/fix.py | Keep Now | FixProposal model used by remediation |
| mcp_ssd/models/review.py | Keep Now | Review and validation result models |
| mcp_ssd/core/__init__.py | Keep Now | Core package anchor |
| mcp_ssd/core/context_engine.py | Keep Now | Prompt context construction support |
| mcp_ssd/core/persona_prompts.py | Keep Now | Persona prompt selection and rendering |
| mcp_ssd/core/review_memory.py | Keep Now | Review state and scoring support |
| mcp_ssd/prescreening/__init__.py | Keep Now | Prescreening package anchor |
| mcp_ssd/prescreening/ucr_analyzer.py | Keep Now | Required by PRD remediation pre-screening |
| mcp_ssd/scoring/__init__.py | Keep Now | Scoring package anchor |
| mcp_ssd/scoring/calculator.py | Keep Now | Review scoring calculation support |
| mcp_ssd/scoring/categories.py | Keep Now | Review scoring category registry |
| mcp_ssd/scoring/conflicts.py | Keep Now | Review scoring conflict resolution |
| mcp_ssd/scoring/weights.py | Keep Now | Review scoring weights |
| mcp_ssd/skills/__init__.py | Keep Now | Skills package anchor |
| mcp_ssd/skills/loader.py | Keep Now | Skill loading for create/review/remediate |
| mcp_ssd/prompts/__init__.py | Keep Now | Prompts package anchor |
| mcp_ssd/prompts/loader.py | Keep Now | Prompt loading for review phase |
| mcp_ssd/utils/__init__.py | Keep Now | Utils package anchor |
| mcp_ssd/utils/file_ops.py | Keep Now | Shared file operations |
| mcp_ssd/utils/finding_hash.py | Keep Now | Finding identity support |
| mcp_ssd/utils/reporting.py | Keep Now | Structured report output support |
| mcp_ssd/utils/logging.py | Keep Now | Runtime logging helper |
| mcp_ssd/utils/hash.py | Keep Now | Shared hashing utility |
| mcp_ssd/observability/__init__.py | Keep Now | Package anchor; imported by migrated runtime |
| mcp_ssd/observability/logging.py | Keep Now | Imported by migrated MCP server |
| mcp_ssd/observability/context.py | Defer or Remove | Not required for first runnable baseline |
| mcp_ssd/observability/metrics.py | Defer or Remove | Metrics are not required for initial migration |
| mcp_ssd/observability/tracing.py | Defer or Remove | Tracing is not required for initial migration |
| mcp_ssd/observability/llm_instrumentation.py | Defer or Remove | AI instrumentation is outside initial MCP-only baseline |
| mcp_ssd/validators/__init__.py | Keep Now | Validator package anchor |
| mcp_ssd/validators/base.py | Keep Now | Core validator protocol |
| mcp_ssd/validators/registry.py | Keep Now | Validator lookup/registration |
| mcp_ssd/validators/adr.py | Keep Now | ADR layer validator |
| mcp_ssd/validators/ears.py | Keep Now | EARS layer validator |
| mcp_ssd/validators/prd.py | Keep Now | PRD layer validator entry |
| mcp_ssd/validators/req.py | Keep Now | REQ layer validator |
| mcp_ssd/validators/sys.py | Keep Now | SYS layer validator |
| mcp_ssd/validators/ctr.py | Keep Now | CTR layer validator |
| mcp_ssd/validators/brd_validator.py | Defer or Remove | Wrapper kept out of the current PRD-first scope |
| mcp_ssd/validators/generic.py | Defer or Remove | Generic validator is not required for current scoped layers |
| mcp_ssd/validators/bdd.py | Defer or Remove | BDD layer not in current MCP_SDD baseline scope |
| mcp_ssd/validators/spec.py | Defer or Remove | SPEC layer not in current MCP_SDD baseline scope |
| mcp_ssd/validators/tspec.py | Defer or Remove | TSPEC layer not in current MCP_SDD baseline scope |
| mcp_ssd/validators/common/__init__.py | Keep Now | Common validator package anchor |
| mcp_ssd/validators/common/file_utils.py | Keep Now | Shared file utilities for validators |
| mcp_ssd/validators/common/error_codes.py | Keep Now | Machine-parseable error code support |
| mcp_ssd/validators/common/patterns.py | Keep Now | Shared regex/pattern helpers |
| mcp_ssd/validators/common/result.py | Keep Now | Shared validation result model |
| mcp_ssd/validators/common/references.py | Keep Now | Shared reference validation |
| mcp_ssd/validators/common/frontmatter.py | Keep Now | Shared frontmatter validation |
| mcp_ssd/validators/common/links.py | Keep Now | Shared link validation |
| mcp_ssd/validators/common/diagrams.py | Keep Now | Shared diagram validation |
| mcp_ssd/validators/brd/__init__.py | Keep Now | BRD validator package anchor |
| mcp_ssd/validators/brd/element_codes.py | Keep Now | BRD code validation |
| mcp_ssd/validators/brd/metadata.py | Keep Now | BRD metadata validation |
| mcp_ssd/validators/brd/duplicate_fixer.py | Keep Now | BRD duplicate remediation support |
| mcp_ssd/validators/brd/schema.py | Keep Now | BRD schema validation |
| mcp_ssd/validators/brd/structure.py | Keep Now | BRD structure validation |
| mcp_ssd/validators/brd/fixer.py | Keep Now | BRD remediation logic |
| mcp_ssd/validators/brd/quality_gate.py | Keep Now | BRD quality gate logic |
| mcp_ssd/validators/prd/__init__.py | Keep Now | PRD validator package anchor |
| mcp_ssd/validators/prd/element_codes.py | Keep Now | PRD code validation |
| mcp_ssd/validators/prd/metadata.py | Keep Now | PRD metadata validation |
| mcp_ssd/validators/prd/duplicate_fixer.py | Keep Now | PRD duplicate remediation support |
| mcp_ssd/validators/prd/schema.py | Keep Now | PRD schema validation |
| mcp_ssd/validators/prd/corpus_gate.py | Keep Now | PRD corpus/content gate |
| mcp_ssd/validators/prd/structure.py | Keep Now | PRD structure validation |
| mcp_ssd/validators/prd/artifact_ops.py | Keep Now | PRD artifact operations |
| mcp_ssd/validators/prd/lineage_checker.py | Keep Now | PRD lineage validation |
| mcp_ssd/validators/prd/fixer.py | Keep Now | PRD remediation logic |
| mcp_ssd/validators/prd/scoring.py | Keep Now | PRD scoring support |
| mcp_ssd/validators/prd/quality_gate.py | Keep Now | PRD quality gate logic |

## Scripts Already Copied

These are not counted in the Python-file inventory above because the request is specific to copied Python files under legacy runtime migration, but they are part of the current staged migration:

- mcp_ssd/scripts/extract_actions.py
- mcp_ssd/scripts/fix_duplicate_ids.py
- mcp_ssd/scripts/generate_prompts.py
- mcp_ssd/scripts/update_ucr_templates.py
- mcp_ssd/scripts/validate_actions.py

## Minimal Migration Set for PLAN-002

Retain and actively rewire only these areas first for the PLAN-012 PRD flow:
- mcp_ssd/mcp
- mcp_ssd/config
- mcp_ssd/api
- mcp_ssd/models
- mcp_ssd/core/context_engine.py
- mcp_ssd/core/persona_prompts.py
- mcp_ssd/core/review_memory.py
- mcp_ssd/prescreening
- mcp_ssd/scoring
- mcp_ssd/skills/__init__.py
- mcp_ssd/skills/loader.py
- mcp_ssd/prompts/__init__.py
- mcp_ssd/prompts/loader.py
- mcp_ssd/utils
- mcp_ssd/exceptions.py
- mcp_ssd/version.py
- mcp_ssd/validators/base.py
- mcp_ssd/validators/registry.py
- mcp_ssd/validators/common
- mcp_ssd/validators/brd
- mcp_ssd/validators/prd
- mcp_ssd/validators/adr.py
- mcp_ssd/validators/ears.py
- mcp_ssd/validators/req.py
- mcp_ssd/validators/sys.py
- mcp_ssd/validators/ctr.py
- mcp_ssd/observability/logging.py

## Deferred Set

Do not rewire these in PLAN-002 unless a dependency analysis forces it:
- mcp_ssd/observability/context.py
- mcp_ssd/observability/metrics.py
- mcp_ssd/observability/tracing.py
- mcp_ssd/observability/llm_instrumentation.py
- mcp_ssd/validators/brd_validator.py
- mcp_ssd/validators/generic.py
- mcp_ssd/validators/bdd.py
- mcp_ssd/validators/spec.py
- mcp_ssd/validators/tspec.py

## Recommended Next Action

Use this inventory as the source of truth for selective namespace rewiring.
Do not copy additional UCX_v1_archive Python modules beyond the PLAN-012 PRD flow unless a verified dependency gap appears during PLAN-002 implementation.
