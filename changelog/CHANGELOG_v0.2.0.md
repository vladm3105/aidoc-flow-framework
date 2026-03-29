# CHANGELOG v0.2.0

**Release Date**: 2026-03-28
**Type**: Minor (BRD Template Unification)

## Summary

Unified the BRD (Layer 1) artifact into a single YAML template that serves as the sole source of truth for both AI/MCP tools and human review. Eliminates the dual-file template approach and absorbs creation/validation guidance directly into the template.

## Changes

### New File

- `ai_dev_ssd_flow/01_BRD/BRD-TEMPLATE.yaml`: Unified BRD template (898 lines, schema v1.5)

### Replaced Files (4 → 1)

| Replaced File | Lines | Disposition |
|---|---|---|
| `BRD-MVP-TEMPLATE.md` | 1,110 | Replaced by BRD-TEMPLATE.yaml |
| `BRD-MVP-TEMPLATE.yaml` | 366 | Replaced by BRD-TEMPLATE.yaml |
| `BRD_MVP_CREATION_RULES.md` | 2,229 | Authoring guidance embedded as `_guidance` fields |
| `BRD_MVP_VALIDATION_RULES.md` | 1,868 | Validation logic stays in `validate_brd_wrapper.sh` |

**Total reduction**: 5,573 lines → 898 lines (84% reduction)

### Template Architecture

- Single YAML file consumable by MCP tools and renderable to MD/HTML by AI on demand
- `_guidance`, `_antipatterns`, `_note`, `_example` fields provide human authoring context
- MCP tools ignore `_` prefixed keys; humans see instructions inline

### Section Structure (18 → 15 sections)

Removed sections owned by downstream artifacts:

| Removed Section | Owner |
|---|---|
| User Stories | PRD (Layer 2) |
| Quality Attributes (6 sub-sections) | SYS (Layer 6) |
| Implementation Approach | PRD/ADR (Layer 2/5) |
| Support & Maintenance | SYS/operational docs |
| Quality Assurance | PRD/TSPEC (Layer 2/10) |

Added sections:
- Section 2: Executive Summary (promoted from document control)
- Section 9: Quality Expectations (flat categorized list replacing 6 sub-sections)

Merged sections:
- Cost-Benefit Analysis → Section 4 (Business Objectives)
- Project Governance → Section 13 (Approval table only)

### ID Format: Hash-Based IDs

Replaced sequential element IDs with content-derived SHA256 hashes:

| Aspect | Old | New |
|---|---|---|
| Format | `BRD.NN.01.01` (sequential) | `BRD.NN.07.a7f3` (hash) |
| Stability | IDs shift on insert/delete | Stable regardless of order |
| Parallelism | Counter conflicts | Stateless, no conflicts |
| Algorithm | — | SHA256, 4-char hex, extend to 8 on collision |
| Section mapping | Fixed element type codes (01, 02, 03...) | Section numbers from template (04, 07, 08...) |

Reference implementation: `UCX_v1_archive/ucx/utils/finding_hash.py`

### Embedded Authoring Guidance

Creation rules content embedded as `_guidance` fields in relevant sections:

| Guidance Topic | Template Location |
|---|---|
| Executive Summary quantitative pattern | `executive_summary._guidance` |
| SMART objectives with baselines | `business_objectives._guidance` |
| Complexity rating methodology (1-5) | `functional_requirements.requirements[].complexity._guidance` |
| Business language patterns | `functional_requirements._guidance` |
| BRD vs PRD content boundaries | `functional_requirements._guidance` + `_antipatterns` |
| Platform vs Feature BRD types | `metadata.brd_type._guidance` |
| File naming conventions | `metadata.file_organization._guidance` |
| ADR relationship guidelines | `adr_topics._guidance` |
| Version control for refactoring | `document_control.revision_history._guidance` |

### ADR Topic Schema Consistency

All 7 mandatory ADR topics now share identical field structure:
`id`, `category`, `title`, `status`, `business_driver`, `budget_constraint`, `compliance_requirements`, `team_constraints`, `recommended_selection`, `prd_requirements`

Fields use `null` when not applicable to a specific topic.

### Quality Expectations Categorization

Quality expectations now include a `category` field (performance, reliability, scalability, security, observability) enabling SYS (Layer 6) to route expectations to correct subsections.

### Other Improvements

- Target users/market added to Executive Summary (Section 2)
- Goals use hash-based IDs (were plain integers)
- Deliverable type routing documented (code→CSPEC, document→DSPEC, etc.)
- Schema version: 1.3 → 1.5
- Removed all scattered `_note: "ID Format:..."` — centralized in `metadata.id_standard`

## Backward Compatibility

- Existing BRD instances created from old templates remain valid
- Validation script (`validate_brd_wrapper.sh`) unchanged
- Old template files not deleted — marked for deprecation
- Schema (`BRD_MVP_SCHEMA.yaml`) requires update to validate new structure

## Validation Evidence

- YAML syntax validated: `yaml.safe_load()` passes
- All 15 sections present with correct numbering
- No legacy sequential IDs remaining (verified via grep)
- No old `_note: "ID Format:..."` patterns remaining
- All cross-section references updated to new numbering
