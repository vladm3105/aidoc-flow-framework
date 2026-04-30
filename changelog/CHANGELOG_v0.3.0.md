# CHANGELOG v0.3.0

**Release Date**: 2026-03-29
**Type**: Minor (PRD Template Unification + C4 Model Mapping)

## Summary

Unified the PRD (Layer 2) artifact into a single YAML template, following the same approach as BRD (v0.2.0). Added C4 architecture model mapping to both BRD and PRD templates.

## Changes

### PRD Layer Unification

**New**: `ucx_flow_v3/02_PRD/PRD-TEMPLATE.yaml` (605 lines, schema v1.0)

**Replaced** (6 files, 4,616 lines → 605 lines):

| File | Lines | Disposition |
|------|-------|-------------|
| `PRD-MVP-TEMPLATE.md` | 731 | Archived |
| `PRD-MVP-TEMPLATE.yaml` | 240 | Archived |
| `PRD_MVP_SCHEMA.yaml` | 380 | Archived |
| `PRD_MVP_CREATION_RULES.md` | 1,268 | Guidance embedded as `_guidance` fields |
| `PRD_MVP_VALIDATION_RULES.md` | 1,024 | Validation via mcp_ucx tools |
| `PRD_MVP_QUALITY_GATE_VALIDATION.md` | 973 | Quality gates via mcp_ucx tools |

**Archived** (8 additional files + scripts/ + examples/): 16 total files in `PRD_v1_archive/`

### Section Structure (21 + 3 appendices → 15 sections)

Removed/merged sections:

| Removed | Action | Owner |
|---------|--------|-------|
| Section 14 (Success Definition) | Merged into Section 5 (KPIs) + Section 11 (Acceptance Criteria) | — |
| Section 15 (Stakeholders) | Deferred to project management artifacts | PM |
| Section 16 (Implementation) | Deferred to IPLAN/TASKS (Layer 11-12) | IPLAN |
| Section 17 (Budget) | Covered by BRD Section 4 (cost_benefit) | BRD |
| Section 19 (References) | Merged into Section 14 (Traceability) | — |
| Section 20 (EARS Appendix) | Moved to EARS layer; content preserved in `tmp/EARS_APPENDIX_FROM_PRD.md` | EARS |
| Section 21 (QA & Testing) | Deferred to TSPEC (Layer 10) | TSPEC |
| Appendix A (Roadmap) | Duplicate of BRD lifecycle | BRD |
| Appendix C (Lifecycle) | Duplicate of BRD lifecycle | BRD |

### Hash-Based Element IDs

Format: `PRD.{doc_id}.{section_id}.{hash}` — hash derived from PRD content, not BRD.
Section numbers match new 15-section template (not old 21-section).

### C4 Architecture Model Mapping

Added `metadata.c4_level` to both BRD and PRD templates:

| C4 Level | SDD Layer | Value |
|----------|-----------|-------|
| Context | BRD (Layer 1) | `context` |
| Container | PRD (Layer 2) | `container` |
| Component | SYS (Layer 6) | `component` (future) |
| Code | SPEC (Layer 9) | `code` (future) |

ADR (Layer 5) serves as decision bridge between Container→Component.

### Embedded Authoring Guidance

| Guidance | Template Location |
|----------|-------------------|
| MVP hypothesis pattern | `executive_summary.mvp_hypothesis._guidance` |
| User story layer separation | `user_stories._guidance` + `_antipatterns` |
| FR structure + threshold conventions | `functional_requirements._guidance` |
| Customer-facing content requirements | `customer_facing_content._guidance` |
| ADR topic elaboration | `traceability._guidance` |
| EARS-Ready scoring criteria | `metadata.validation._guidance` |
| Diagram contract tags | `functional_requirements.diagram_contract._guidance` |

### mcp_ucx Updates

- Copied `PRD-TEMPLATE.yaml` to `mcp_ucx/templates/`
- Removed `mcp_ucx/templates/PRD-MVP-TEMPLATE.md`
- Updated `prompts/templates/creation/UCC_PROMPT_PRD.md`: 21→15 sections, template refs
- No source code changes (PLAN-002 naming migration already in place)

### Pre-commit Hooks

All hooks disabled (`.pre-commit-config.yaml` set to `repos: []`). Validation runs through mcp_ucx MCP tools only.

## Backward Compatibility

- Existing PRD instances created from old templates remain valid
- mcp_ucx test suite: 173 passed, 1 pre-existing failure, 0 regressions
- Framework-wide stale references (README.md, LAYER_REGISTRY.yaml, etc.) documented for future cleanup

## Validation Evidence

- YAML syntax: `yaml.safe_load()` passes
- Template resolution: `resolve_template_path()` finds `PRD-TEMPLATE.yaml`
- mcp_ucx tests: 173 passed, 0 regressions
- No `PRD-MVP-TEMPLATE` in mcp_ucx source (grep verified)
