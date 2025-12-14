# Implementation Plan - Fix Forward References in SDD Layer Templates

**Created**: 2025-12-13 19:12:50 EST
**Status**: ✅ COMPLETED (2025-12-13 19:35 EST)

## Objective

Fix SDD layer dependency violations by replacing forward references (to non-existent downstream documents) with context-specific `**[TYPE] Requirements**` guidance fields.

## Context

### SDD Layer Dependency Principle

Documents can only reference **upstream** (higher layer) documents, never **downstream** (lower layer) documents that don't exist yet:

```
Layer 1: BRD   →  Created FIRST   →  Cannot reference PRD or ADR
Layer 2: PRD   →  Created SECOND  →  Can reference BRD, cannot reference ADR
Layer 5: ADR   →  Created LATER   →  Can reference BRD and PRD
```

### Key Decisions

1. **Replace forward references with Requirements fields**:
   - `**PRD Elaboration**: PRD-NNN §18.X` → `**PRD Requirements**: [guidance text]`
   - `**ADR Reference**: ADR-NNN (pending)` → `**ADR Requirements**: [guidance text]`

2. **Requirements fields provide context-specific guidance**:
   - Describe what downstream document must elaborate for THIS specific topic
   - No document IDs - just guidance text

3. **General principle**: A higher layer document may include `**[TYPE] Requirements**` fields for ANY lower layer documents when needed.

## Task List

### Completed
- [x] Identify all files with forward reference violations
- [x] Define correct format for BRD Section 7.2
- [x] Define correct format for PRD Section 18
- [x] Document general principle for TYPE Requirements pattern

### Completed (Implementation Session)
- [x] Update `ai_dev_flow/ID_NAMING_STANDARDS.md` (line 516) - Replaced with `**PRD Requirements**`
- [x] Update `ai_dev_flow/BRD/BRD-TEMPLATE.md` (line 711) - Replaced with `**PRD Requirements**`
- [x] Update `.claude/skills/doc-brd/SKILL.md` (line 216) - Replaced with `**PRD Requirements**`
- [x] Update `ai_dev_flow/PRD/PRD-TEMPLATE.md` (lines 857, 879, 918) - Replaced `ADR Reference` with `**ADR Requirements**`
- [x] Update `.claude/skills/doc-prd/SKILL.md` (line 159) - Replaced `ADR Reference` with `**ADR Requirements**`
- [x] Update `ai_dev_flow/BRD/BRD_CREATION_RULES.md` (lines 1437, 1486) - Replaced with `**PRD Requirements**`
- [x] Update `ai_dev_flow/PRD/PRD_CREATION_RULES.md` (line 386) - Replaced with `**ADR Requirements**`

## Implementation Guide

### Prerequisites
- Read the current plan file: `/home/ya/.claude/plans/generic-snacking-backus.md`
- Understand the layer dependency principle

### Execution Steps

#### Step 1: Fix BRD-related files (Layer 1)

**File 1**: `ai_dev_flow/ID_NAMING_STANDARDS.md` (lines 516-517)

Replace:
```markdown
**ADR Reference**: ADR-NNN (pending)
**PRD Elaboration**: PRD-NNN §18.X
```

With:
```markdown
**PRD Requirements**: [What PRD must elaborate for THIS topic - technical options, evaluation criteria, performance benchmarks]
```

**File 2**: `ai_dev_flow/BRD/BRD-TEMPLATE.md` (lines 711-712)

Replace:
```markdown
**ADR Reference**: ADR-003 (pending)
**PRD Elaboration**: PRD-001 §18.3
```

With:
```markdown
**PRD Requirements**: [What PRD must elaborate for THIS topic - e.g., "Evaluate technical options for data persistence. Include scalability analysis."]
```

**File 3**: `.claude/skills/doc-brd/SKILL.md` (lines 216-217)

Replace:
```markdown
**ADR Reference**: ADR-001 (pending)
**PRD Elaboration**: PRD-001 §18.1
```

With:
```markdown
**PRD Requirements**: [What PRD must elaborate for THIS topic]
```

#### Step 2: Fix PRD-related files (Layer 2)

**File 4**: `ai_dev_flow/PRD/PRD-TEMPLATE.md` (~lines 857, 879)

Replace all instances of:
```markdown
**ADR Reference**: ADR-NNN (pending)
```

With:
```markdown
**ADR Requirements**: [What ADR must decide for THIS topic - e.g., "Select one option based on evaluation. Document trade-offs and rollback strategy."]
```

**File 5**: `.claude/skills/doc-prd/SKILL.md` (~line 159)

Replace:
```markdown
**ADR Reference**: ADR-001 (pending)
```

With:
```markdown
**ADR Requirements**: [What ADR must decide for THIS topic]
```

### Verification

1. Search for remaining forward references:
   ```bash
   grep -r "PRD-[0-9]" ai_dev_flow/BRD/ .claude/skills/doc-brd/
   grep -r "ADR-[0-9]" ai_dev_flow/BRD/ ai_dev_flow/PRD/ .claude/skills/doc-brd/ .claude/skills/doc-prd/
   ```

2. Verify new pattern exists:
   ```bash
   grep -r "PRD Requirements" ai_dev_flow/BRD/ ai_dev_flow/ID_NAMING_STANDARDS.md .claude/skills/doc-brd/
   grep -r "ADR Requirements" ai_dev_flow/PRD/ .claude/skills/doc-prd/
   ```

## References

- Plan file: `/home/ya/.claude/plans/generic-snacking-backus.md`
- Related files:
  - `ai_dev_flow/ID_NAMING_STANDARDS.md`
  - `ai_dev_flow/BRD/BRD-TEMPLATE.md`
  - `ai_dev_flow/PRD/PRD-TEMPLATE.md`
  - `.claude/skills/doc-brd/SKILL.md`
  - `.claude/skills/doc-prd/SKILL.md`
- Previous work: `work_plans/arch-decision-layer-separation_20251213_163827.md`

## General Principle Reference

| Source Layer | Target Layer | Field Name | Purpose |
|--------------|--------------|------------|---------|
| BRD (Layer 1) | PRD (Layer 2) | `**PRD Requirements**` | Technical elaboration needed |
| BRD (Layer 1) | ADR (Layer 5) | `**ADR Requirements**` | Direct architectural guidance |
| BRD (Layer 1) | SPEC (Layer 10) | `**SPEC Requirements**` | Implementation constraints |
| PRD (Layer 2) | ADR (Layer 5) | `**ADR Requirements**` | Decision criteria from technical analysis |
| PRD (Layer 2) | TASKS (Layer 11) | `**TASKS Requirements**` | Implementation task guidance |
