# Implementation Plan: Standardize Internal Feature Headings to Unified TYPE.NNN.NNN Format

**Created**: 2025-12-10 14:32:39 EST
**Status**: ✅ Completed
**Completed**: 2025-12-10 EST
**Source Plan**: `/home/ya/.claude/plans/squishy-hugging-sphinx.md`

---

## Objective

Standardize all internal document feature/requirement headings to use the unified `TYPE.NNN.NNN` format (e.g., `BRD.017.001`) for:
1. Direct searchability across all documents
2. Consistency between internal headings and external references
3. Elimination of ambiguity

## Current State

| Layer | Document Type | Current Pattern | Example |
|-------|---------------|-----------------|---------|
| 1 | BRD | `FR-XXX` | `#### FR-001: Feature Name` |
| 2 | PRD | `Feature F-XXX` | `### Feature F-001: Name` |
| 3 | EARS | `EARS.NNN.XXX` ✅ | `### EARS.012.001` |
| 4 | BDD | `BDD.NNN.XXX` ✅ | `### BDD.015.001` |
| 6 | SYS | `SYS.NNN.XXX` ✅ | `### SYS.012.001` |

**EARS, SYS, BDD already use unified format. BRD and PRD need migration.**

## Target State

All internal headings use: `### TYPE.NNN.NNN: Feature Name`

**Format Breakdown**:

| Component | Description | Example |
|-----------|-------------|---------|
| `TYPE` | Document type in SDD framework (BRD, PRD, EARS, SYS, etc.) | `BRD` |
| First `.NNN` | Document ID (the document number) | `.017` = BRD-017 |
| Second `.NNN` | Sequential feature numbering inside the document | `.001` = first feature |

**Example**: `BRD.017.003` = BRD document 017, feature 003

| Layer | Document Type | New Pattern | Example |
|-------|---------------|-------------|---------|
| 1 | BRD | `BRD.NNN.NNN` | `### BRD.017.001: Market Data Feed` |
| 2 | PRD | `PRD.NNN.NNN` | `### PRD.022.001: User Dashboard` |
| 3 | EARS | `EARS.NNN.NNN` | `### EARS.006.001: Data Validation` |
| 4 | BDD | `BDD.NNN.NNN` | `### BDD.015.001: Login Scenario` |
| 6 | SYS | `SYS.NNN.NNN` | `### SYS.008.001: API Gateway` |

## Files to Update

### 1. ID_NAMING_STANDARDS.md
- Add section documenting unified internal heading format
- Mark `FR-XXX` and `Feature F-XXX` as REMOVED (no backward compatibility)

### 2. BRD Templates & Rules
- `ai_dev_flow/BRD/BRD-TEMPLATE.md` - Update feature heading examples
- `ai_dev_flow/BRD/BRD_CREATION_RULES.md` - Update heading format rules
- `ai_dev_flow/BRD/FR_EXAMPLES_GUIDE.md` - Update all `FR-XXX` to `BRD.NNN.NNN`

### 3. PRD Templates & Rules
- `ai_dev_flow/PRD/PRD-TEMPLATE.md` - Update feature heading examples
- `ai_dev_flow/PRD/PRD_CREATION_RULES.md` - Update heading format rules
- `ai_dev_flow/PRD/PRD-000_ai_assisted_documentation_features.md` - Update `Feature F-XXX` to `PRD.NNN.NNN`

### 4. Validation Rules
- `ai_dev_flow/BRD/BRD_VALIDATION_RULES.md` - Update validation patterns
- `ai_dev_flow/PRD/PRD_VALIDATION_RULES.md` - Update validation patterns

### 5. Skills/Quickrefs
- `.claude/skills/doc-brd/SKILL.md` - Update heading format guidance
- `.claude/skills/doc-prd/SKILL.md` - Update heading format guidance
- `.claude/skills/doc-brd_quickref.md` - Update examples
- `.claude/skills/doc-prd_quickref.md` - Update examples

## Implementation Steps

1. **Update ID_NAMING_STANDARDS.md** - Add unified internal heading section
2. **Update BRD templates** - Migrate `FR-XXX` → `BRD.NNN.NNN`
3. **Update PRD templates** - Migrate `Feature F-XXX` → `PRD.NNN.NNN`
4. **Update validation rules** - Add regex patterns for new format
5. **Update skills** - Ensure guidance matches new standard
6. **Verify EARS/SYS/BDD** - Confirm already compliant (no changes needed)

## Validation Regex

```python
# Internal heading pattern
INTERNAL_HEADING_PATTERN = r'^###\s+[A-Z]{2,5}\.\d{3}\.\d{3}:\s+.+'
# Matches: ### BRD.017.001: Feature Name
```

## Removed Patterns (No Backward Compatibility)

**REMOVED in v2.0** - Do NOT use:
- `FR-XXX`, `FR-XXXA` (old BRD format)
- `Feature F-XXX` (old PRD format)
- `### 001:` (simple sequential)

**MANDATORY Format**:
- `### TYPE.NNN.NNN: Feature Name`

---

## Instructions for New Context Window

To continue implementation, provide this prompt:

```
Continue implementing the unified feature ID headings plan from:
/opt/data/docs_flow_framework/work_plans/unified-feature-id-headings_20251210_143239.md

The plan standardizes internal document headings to TYPE.NNN.NNN format.
EARS, SYS, BDD are already compliant. Focus on BRD and PRD migration.
```
