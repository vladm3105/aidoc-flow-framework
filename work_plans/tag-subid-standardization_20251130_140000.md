# Implementation Plan - Standardize ALL Traceability Tag Sub-IDs to Numeric Format

**Created**: 2025-11-30 14:00:00 EST
**Status**: Ready for Implementation

## Objective

Standardize ALL traceability tag sub-IDs to simple numeric format (`DOC-NNN:NNN`) across the entire ai_dev_flow framework for consistency.

## Context

### Problem
The framework currently uses inconsistent sub-ID formats across different tag types:
- Some use descriptive prefixes: `BRD-001:FR-030`, `PRD-003:FEATURE-002`
- Some use scenario names: `BDD-015:scenario-send-notification`
- Some use category prefixes: `SYS-008:PERF-001`, `REQ-003:interface-spec`

### User Decisions
- All tags with sub-IDs should be standardized to `DOC-NNN:NNN` format
- BDD scenarios should use numeric only (`BDD-015:001`), not descriptive names
- EARS already standardized (completed in prior session)

### Scope

**Tags WITH Sub-IDs (Standardize to `DOC-NNN:NNN`)**:

| Tag | Current Format | Target Format |
|-----|----------------|---------------|
| @brd | `BRD-NNN:FR-NNN`, `BRD-NNN:NFR-NNN` | `BRD-NNN:NNN` |
| @prd | `PRD-NNN:FEATURE-NNN`, `PRD-NNN:REQ-NNN` | `PRD-NNN:NNN` |
| @ears | `EARS-NNN:NNN` | Already done |
| @bdd | `BDD-NNN:scenario-name`, `BDD-NNN:SCENARIO-ID` | `BDD-NNN:NNN` |
| @sys | `SYS-NNN:PERF-001`, `SYS-NNN:FUNC-001` | `SYS-NNN:NNN` |
| @req | `REQ-NNN:interface-spec`, `REQ-NNN:validation-logic` | `REQ-NNN:NNN` |
| @impl | `IMPL-NNN:phase1` | `IMPL-NNN:NNN` |
| @tasks | `TASKS-NNN:task-3` | `TASKS-NNN:NNN` |

**Tags WITHOUT Sub-IDs (No Changes)**:
- `@adr: ADR-NNN` - Document-level only
- `@ctr: CTR-NNN` - Document-level only
- `@spec: SPEC-NNN` - Document-level only
- `@iplan: IPLAN-NNN` - Document-level only

**Special Tags EXCLUDED from Standardization**:
- `@icon: TASKS-NNN:ContractName` - Keep descriptive (contract names)
- `@threshold: PRD-NNN:category.key` - Keep dotted path (registry keys)

## Task List

### Completed
- [x] EARS tag standardization (completed in prior session)
- [x] Create implementation plan

### Pending

#### Phase 1: Low-Impact Artifacts (Test Process)
- [ ] IMPL - Update schema, template, validation, creation rules
- [ ] TASKS - Update schema, template, validation, creation rules

#### Phase 2: Testing Layer
- [ ] BDD - Update schema, template, validation, creation rules (Gherkin format)

#### Phase 3: Requirements Chain
- [ ] SYS - Update schema, template, validation, creation rules
- [ ] REQ - Update schema, template, validation, creation rules

#### Phase 4: Business Layer
- [ ] PRD - Update schema, template, validation, creation rules
- [ ] BRD - Update schema, template, validation, creation rules

#### Phase 5: Central Documentation (LAST)
- [ ] TRACEABILITY.md - Master reference
- [ ] COMPLETE_TAGGING_EXAMPLE.md - Training document (50+ instances)

#### Verification
- [ ] Run grep commands to verify no old formats remain
- [ ] Run grep commands to verify new formats present

## Implementation Guide

### Prerequisites
- Read current ai_dev_flow/ files before editing
- Understand YAML schema structure for regex patterns

### Target Regex Patterns

```yaml
# Tags with numeric sub-ID
brd:   "^BRD-\\d{3}:\\d{3}$"
prd:   "^PRD-\\d{3}:\\d{3}$"
ears:  "^EARS-\\d{3}:\\d{3}$"  # Already compliant
bdd:   "^BDD-\\d{3}:\\d{3}$"
sys:   "^SYS-\\d{3}:\\d{3}$"
req:   "^REQ-\\d{3}:\\d{3}$"
impl:  "^IMPL-\\d{3}:\\d{3}$"
tasks: "^TASKS-\\d{3}:\\d{3}$"

# Tags without sub-ID (no change)
adr:   "^ADR-\\d{3}$"
ctr:   "^CTR-\\d{3}$"
spec:  "^SPEC-\\d{3}$"
iplan: "^IPLAN-\\d{3}$"
```

### Per-Artifact File Updates

For each artifact type, update these 4 file categories:

| Category | File Pattern | Changes |
|----------|--------------|---------|
| Schema | `*_SCHEMA.yaml` | Regex patterns |
| Template | `*-TEMPLATE.*` | Example tags |
| Validation | `*_VALIDATION_RULES.md` | Format specs |
| Creation | `*_CREATION_RULES.md` | Guidance text |

### Example Transformations

```markdown
# BEFORE
@brd: BRD-001:FR-030, BRD-001:NFR-006
@prd: PRD-003:FEATURE-002
@bdd: BDD-015:scenario-send-notification
@sys: SYS-008:PERF-001
@req: REQ-003:interface-spec, REQ-004:validation-logic
@impl: IMPL-001:phase1
@tasks: TASKS-001:task-3

# AFTER
@brd: BRD-001:030, BRD-001:006
@prd: PRD-003:002
@bdd: BDD-015:001
@sys: SYS-008:001
@req: REQ-003:001, REQ-004:001
@impl: IMPL-001:001
@tasks: TASKS-001:003
```

### Verification Commands

```bash
# Check for remaining old formats
grep -rn "BRD-[0-9]\{3\}:FR-\|BRD-[0-9]\{3\}:NFR-" ai_dev_flow/
grep -rn "PRD-[0-9]\{3\}:FEATURE" ai_dev_flow/
grep -rn "@bdd:.*scenario-" ai_dev_flow/
grep -rn "SYS-[0-9]\{3\}:[A-Z]" ai_dev_flow/
grep -rn "@req:.*interface-spec\|validation-logic" ai_dev_flow/
grep -rn "@impl:.*phase" ai_dev_flow/
grep -rn "@tasks:.*task-[0-9]" ai_dev_flow/

# Verify new format present
grep -rn "@brd: BRD-[0-9]\{3\}:[0-9]\{3\}" ai_dev_flow/
```

## References

### Critical Files
| File | Purpose |
|------|---------|
| `TRACEABILITY.md` | Master format specification |
| `COMPLETE_TAGGING_EXAMPLE.md` | End-to-end training (50+ tags) |
| `SPEC/SPEC_SCHEMA.yaml` | Reference for cumulative tag patterns |
| `TASKS/TASKS_SCHEMA.yaml` | Highest pattern count |
| `BDD/BDD_SCHEMA.yaml` | Gherkin-specific patterns |

### Related Work
- EARS standardization completed: `work_plans/ears-tag-format-standardization_20251130_132030.md`
- BDD consistency fix: `work_plans/bdd-consistency-fix_20251130_130901.md`
