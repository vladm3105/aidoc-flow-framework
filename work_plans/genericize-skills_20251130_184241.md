# Implementation Plan - Genericize Framework Skills

**Created**: 2025-11-30 18:42:41 EST
**Status**: Ready for Implementation

## Objective

Remove project-specific content (trading/finance terminology, hardcoded paths) from skill files to make the docs_flow_framework generic and reusable for any domain.

## Context

Framework assessment showed 99.7% compliance score with the following issues identified:
- Project-specific content in 6 skill files referencing trading/finance domain
- References to `option_strategy/` directory paths
- Trading-specific examples (Greeks, delta_hedging, trading logic)
- Finance domain terminology in examples that should be generic

The framework is otherwise production-ready with all 13 templates complete, metadata validation passing, and skills compliance at high levels.

## Task List

### Completed
- [x] Framework assessment and validation
- [x] Identify all project-specific content locations
- [x] Document line numbers and fix strategies

### Pending
- [ ] Fix `.claude/skills/doc-flow/SKILL.md` (28+ changes)
- [ ] Fix `.claude/skills/doc-brd/SKILL.md` (10 changes)
- [ ] Fix `.claude/skills/charts-flow/SKILL.md` (13 changes)
- [ ] Fix `.claude/skills/project-mngt/SKILL.md` (5 changes)
- [ ] Fix `.claude/skills/generate_implementation_plan.md` (5 changes)
- [ ] Fix `.claude/skills/generate_implementation_plan_quickref.md` (1 change)
- [ ] Re-run validation scripts to confirm fixes

### Notes
- Use `{project_root}` placeholder convention for paths
- Replace trading terms with generic business logic terminology
- Maintain document structure and formatting

## Implementation Guide

### Prerequisites
- Access to `/opt/data/docs_flow_framework/.claude/skills/` directory
- Understanding of placeholder conventions (`{project_root}`, `{PROJECT_NAME}`)

### Execution Steps

#### 1. doc-flow/SKILL.md (Core Orchestrator)
**Location**: `.claude/skills/doc-flow/SKILL.md`
**Issues**: Lines 131, 184, 206, 212-222, 263
**Changes**:
- Replace `option_strategy/` with `{project_root}/docs/`
- Replace "trading logic" with "business logic"
- Replace "Greeks", "delta_hedging" with generic calculation examples
- Replace trading-specific workflow references with generic ones

#### 2. doc-brd/SKILL.md (BRD Creation)
**Location**: `.claude/skills/doc-brd/SKILL.md`
**Issues**: Lines 146-149, 179, 182-186, 241, 264, 268, 278, 297, 353
**Changes**:
- Replace `option_strategy/` path references with `{project_root}/docs/`
- Remove trading template references
- Use generic project examples

#### 3. charts-flow/SKILL.md (Diagram Generation)
**Location**: `.claude/skills/charts-flow/SKILL.md`
**Issues**: Lines 245, 248, 396-397, 415, 418, 436, 443, 472, 500
**Changes**:
- Replace "Portfolio Orchestrator" with "System Orchestrator"
- Replace "Stock Selection" with "Item Selection"
- Update paths from `option_strategy/diagrams/` to `{project_root}/docs/diagrams/`

#### 4. project-mngt/SKILL.md (Project Management)
**Location**: `.claude/skills/project-mngt/SKILL.md`
**Issues**: Lines 554, 558, 561, 583, 587
**Changes**:
- Replace trading system examples with generic project management examples

#### 5. generate_implementation_plan.md
**Location**: `.claude/skills/generate_implementation_plan.md`
**Issues**: Lines 74, 86, 87, 115, 332
**Changes**:
- Replace "Greeks" with generic calculation module names
- Replace trading logic examples with generic business logic

#### 6. generate_implementation_plan_quickref.md
**Location**: `.claude/skills/generate_implementation_plan_quickref.md`
**Issues**: Line 88
**Changes**:
- Replace "Greeks & Pricing Engine" with generic module name (e.g., "Core Calculation Engine")

### Verification
1. Run `python scripts/skills_compliance_report.py` - should maintain 99.7%+ score
2. Grep for remaining trading terms:
   ```bash
   grep -rn "option_strategy\|trading\|Greeks\|delta_hedging" .claude/skills/
   ```
3. Verify placeholders follow `{project_root}` convention
4. Check that examples remain coherent and useful

## References

- Related files:
  - `/opt/data/docs_flow_framework/tmp/skills_compliance_report.json`
  - `/opt/data/docs_flow_framework/scripts/skills_compliance_report.py`
- Documentation:
  - `/opt/data/docs_flow_framework/ai_dev_flow/README.md`
  - `/opt/data/docs_flow_framework/ai_dev_flow/PROJECT_SETUP_GUIDE.md`
- Validation scripts:
  - `scripts/validate_metadata.py`
  - `scripts/skills_compliance_report.py`
