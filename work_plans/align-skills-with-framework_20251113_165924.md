# Implementation Plan - Align Skills with Framework

**Created**: 2025-11-13 16:59:24 EST
**Status**: Ready for Implementation

## Objective

Align all Claude skills in `.claude/skills/` with the current framework structure in `ai_dev_flow/`, ensuring consistency in path references, terminology, layer architecture, and documentation references.

## Context

### Review Findings

A comprehensive analysis identified inconsistencies between Claude skills and the framework:

1. **Path References**: Skills reference outdated `docs_templates/ai_dev_flow/` path instead of `ai_dev_flow/`
2. **Layer Architecture**: `trace-check/SKILL.md` shows IPLAN as Layer 9 instead of Layer 12
3. **Terminology**: Mixed usage of CONTRACTS vs CTR directory naming
4. **Documentation**: Skills missing references to new framework documentation (COMPLETE_TAGGING_EXAMPLE.md, TRACEABILITY_SETUP.md, etc.)
5. **Project Paths**: Hardcoded paths like `/opt/data/trading/` need to be made generic

### Decisions Made

- **Fix Scope**: All priorities (HIGH, MEDIUM, LOW)
- **Path Strategy**: Make generic with `{project_root}` placeholders
- **Layer Numbering**: Simplify to functional layer groupings instead of formal layer numbers

### Key Files Affected

1. `.claude/skills/generate_implementation_plan.md`
2. `.claude/skills/trace-check/SKILL.md`
3. `.claude/skills/README.md`
4. `.claude/skills/doc-flow/SKILL.md`
5. `.claude/skills/project-init/SKILL.md`
6. `.claude/skills/test-automation/SKILL.md`
7. `.claude/skills/contract-tester/SKILL.md`
8. `.claude/skills/project-mngt/SKILL.md`
9. `.claude/skills/refactor-flow/SKILL.md`

## Task List

### Phase 1: Critical Path Fixes (HIGH PRIORITY)

- [ ] Fix `generate_implementation_plan.md` path references
  - Replace all `docs_templates/ai_dev_flow/` → `{project_root}/ai_dev_flow/`
  - Replace `/opt/data/trading/` → `{project_root}/`
  - Update ~10 path references across lines 10, 32, 213, 482, 483

- [ ] Fix `trace-check/SKILL.md` layer numbering
  - Replace formal layer numbers with functional workflow stages
  - Update from "Layer 9: Implementation Plans" to functional grouping
  - Revise layer description from "11 Functional Layers" to simplified grouping

- [ ] Fix `.claude/skills/README.md` template paths
  - Replace `../../docs_templates/ai_dev_flow/` → `{project_root}/ai_dev_flow/`
  - Update ~7 template path references (lines 518-530)

### Phase 2: Terminology Standardization (MEDIUM PRIORITY)

- [ ] Review and update CONTRACTS→CTR in 7 skill files
  - `.claude/skills/doc-flow/SKILL.md`
  - `.claude/skills/project-init/SKILL.md`
  - `.claude/skills/trace-check/SKILL.md`
  - `.claude/skills/test-automation/SKILL.md`
  - `.claude/skills/contract-tester/SKILL.md`
  - `.claude/skills/project-mngt/SKILL.md`
  - `.claude/skills/refactor-flow/SKILL.md`

- [ ] Add framework documentation references
  - Add `COMPLETE_TAGGING_EXAMPLE.md` to doc-flow skill
  - Add `TRACEABILITY_SETUP.md` to trace-check skill
  - Add `MATRIX_TEMPLATE_COMPLETION_GUIDE.md` to doc-flow skill
  - Add validation script references to trace-check skill

### Phase 3: Consistency & Examples (LOW PRIORITY)

- [ ] Standardize all path references with placeholders
  - Replace `/opt/data/trading/` → `{project_root}/`
  - Replace `/opt/data/docs_flow_framework/` → `{project_root}/`
  - Use relative paths `../../ai_dev_flow/` where appropriate

- [ ] Update doc-flow/SKILL.md
  - Ensure workflow sequence matches framework
  - Update layer references to functional groupings
  - Add new documentation references

- [ ] Add clarification note on layer numbering
  - Add to `.claude/skills/README.md`
  - Explain functional layer groupings vs formal layer numbers

### Phase 4: Validation

- [ ] Verify all changes
  - Run grep to confirm no remaining `docs_templates/` references
  - Run grep to confirm no remaining `/opt/data/trading/` references
  - Verify CONTRACTS→CTR updates are complete
  - Check all `{project_root}` placeholders are correct

- [ ] Test skill documentation
  - Verify template paths resolve correctly
  - Confirm workflow sequences match framework README
  - Validate CTR dual-file format documentation

## Implementation Guide

### Prerequisites

- Access to `/opt/data/docs_flow_framework/`
- Write permissions for `.claude/skills/` directory
- Text editor or IDE
- Git for tracking changes

### Execution Steps

#### Step 1: Fix generate_implementation_plan.md

```bash
# Edit file
vi .claude/skills/generate_implementation_plan.md

# Find and replace:
# - "docs_templates/ai_dev_flow/" → "{project_root}/ai_dev_flow/"
# - "/opt/data/trading/" → "{project_root}/"
```

**Lines to update**: 10, 32, 213, 482, 483

#### Step 2: Fix trace-check/SKILL.md

```bash
vi .claude/skills/trace-check/SKILL.md
```

**Updates needed**:
- Line 22: Change "v2.0 - 11 Functional Layers" description
- Lines 23-35: Simplify layer grouping to functional stages:
  - Business Layer (BRD→PRD→EARS)
  - Testing Layer (BDD)
  - Architecture Layer (ADR→SYS)
  - Requirements Layer (REQ)
  - Implementation Strategy Layer (IMPL)
  - Interface Layer (CTR)
  - Technical Specs Layer (SPEC)
  - Execution Planning Layer (TASKS→IPLAN)
  - Code & Validation Layer (Code→Tests→Validation)

#### Step 3: Fix README.md template paths

```bash
vi .claude/skills/README.md
```

**Lines to update**: 518-530
- Replace all `../../docs_templates/ai_dev_flow/` → `{project_root}/ai_dev_flow/`

#### Step 4: Review CONTRACTS→CTR terminology

For each of the 7 files listed:
1. Search for "CONTRACTS" (uppercase)
2. Search for "contracts" (lowercase)
3. Replace directory references: `CONTRACTS/` → `CTR/`
4. Replace artifact type: "CONTRACTS" → "CTR"
5. Leave generic lowercase "contracts" unchanged (e.g., "API contracts")

```bash
# Example grep command to find references
grep -n "CONTRACTS\|contracts" .claude/skills/doc-flow/SKILL.md
```

#### Step 5: Add new documentation references

**In doc-flow/SKILL.md**, add references to:
- `{project_root}/ai_dev_flow/COMPLETE_TAGGING_EXAMPLE.md`
- `{project_root}/ai_dev_flow/MATRIX_TEMPLATE_COMPLETION_GUIDE.md`

**In trace-check/SKILL.md**, add references to:
- `{project_root}/ai_dev_flow/TRACEABILITY_SETUP.md`
- `{project_root}/ai_dev_flow/scripts/validate_iplan_naming.py`
- `{project_root}/ai_dev_flow/scripts/add_cumulative_tagging_to_matrices.py`
- `{project_root}/ai_dev_flow/scripts/batch_update_matrix_templates.py`

#### Step 6: Standardize all path references

Run comprehensive find/replace across all skill files:

```bash
cd .claude/skills/

# Find all files with path references
grep -r "/opt/data/trading/" .
grep -r "/opt/data/docs_flow_framework/" .
grep -r "docs_templates/" .

# After manual review, replace as needed
```

#### Step 7: Add layer architecture clarification

Add to `.claude/skills/README.md` in appropriate section:

```markdown
### Layer Architecture Note

The framework uses functional layer groupings for workflow clarity rather than formal layer numbers. Artifacts flow through functional stages:

**Business Layer** → BRD, PRD, EARS
**Testing Layer** → BDD
**Architecture Layer** → ADR, SYS
**Requirements Layer** → REQ
**Implementation Strategy Layer** → IMPL
**Interface Layer** → CTR (optional)
**Technical Specs Layer** → SPEC
**Execution Planning Layer** → TASKS, IPLAN
**Code & Validation Layer** → Code, Tests, Validation

This functional grouping simplifies understanding the workflow while maintaining full traceability.
```

#### Step 8: Final validation

```bash
# Verify no remaining outdated references
cd .claude/skills/
grep -r "docs_templates/" . && echo "❌ Found docs_templates references" || echo "✅ No docs_templates references"
grep -r "/opt/data/trading/" . && echo "❌ Found /opt/data/trading/ references" || echo "✅ No /opt/data/trading/ references"

# Verify CTR updates
grep -r "CONTRACTS/" . && echo "⚠️  Check CONTRACTS/ references" || echo "✅ No CONTRACTS/ directory references"

# Count {project_root} usage
grep -r "{project_root}" . | wc -l
```

### Verification

**Success Criteria**:
- ✅ Zero references to `docs_templates/` path
- ✅ All project-specific paths use `{project_root}` placeholder
- ✅ Layer numbering simplified to functional groupings
- ✅ CONTRACTS terminology replaced with CTR where appropriate
- ✅ New framework documentation referenced in relevant skills
- ✅ All template paths validated and working

**Expected Outcomes**:
1. Skills documentation is consistent with framework v2.0
2. Path references are portable across projects
3. Layer architecture is clearly explained using functional groupings
4. All artifact types use current naming conventions (CTR, IPLAN)
5. Skills reference latest framework documentation and tools

**Testing**:
1. Review each skill file to ensure paths are correct
2. Verify workflow sequences match framework README
3. Confirm all links to templates and documentation work
4. Check that layer descriptions are consistent across all skills

## References

### Framework Files
- `ai_dev_flow/README.md` - Main framework documentation
- `ai_dev_flow/ID_NAMING_STANDARDS.md` - Naming conventions including IPLAN
- `ai_dev_flow/COMPLETE_TAGGING_EXAMPLE.md` - Tagging examples
- `ai_dev_flow/TRACEABILITY_SETUP.md` - Traceability guidance
- `ai_dev_flow/MATRIX_TEMPLATE_COMPLETION_GUIDE.md` - Matrix template guide

### Validation Scripts
- `ai_dev_flow/scripts/validate_iplan_naming.py`
- `ai_dev_flow/scripts/add_cumulative_tagging_to_matrices.py`
- `ai_dev_flow/scripts/batch_update_matrix_templates.py`
- `ai_dev_flow/scripts/validate_traceability_matrix_enforcement.py`

### Skills to Update
- `.claude/skills/generate_implementation_plan.md`
- `.claude/skills/trace-check/SKILL.md`
- `.claude/skills/README.md`
- `.claude/skills/doc-flow/SKILL.md`
- `.claude/skills/project-init/SKILL.md`
- `.claude/skills/test-automation/SKILL.md`
- `.claude/skills/contract-tester/SKILL.md`
- `.claude/skills/project-mngt/SKILL.md`
- `.claude/skills/refactor-flow/SKILL.md`

### Analysis Report
Detailed inconsistency analysis from 2025-11-13 review session covering:
- Path reference issues (HIGH priority)
- Layer architecture mismatches (HIGH priority)
- Template path corrections (HIGH priority)
- Terminology standardization CONTRACTS→CTR (MEDIUM priority)
- Documentation reference additions (MEDIUM priority)
- Generic path placeholders (LOW priority)
- Layer numbering clarification (LOW priority)

## Notes

- This plan addresses ALL priority levels as requested
- Path strategy uses `{project_root}` placeholder for portability
- Layer numbering simplified to functional groupings for clarity
- Total estimated changes: 11 files, ~50-100 individual edits
- No breaking changes expected - purely documentation updates
- Skills will be more maintainable and portable after implementation
