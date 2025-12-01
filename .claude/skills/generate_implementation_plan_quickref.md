# Implementation Plan Generator - Quick Reference

**Skill**: `generate_implementation_plan`
**Purpose**: Generate IMPL documents from BRD analysis following SDD workflow

## Quick Start

```bash
# Invoke skill
/skill generate_implementation_plan

# Required inputs (skill will prompt)
brd_directory: {project_root}/docs/BRD/
output_file: {project_root}/docs/BRD/BRD-000_implementation_plan.md

# Optional inputs
force_phase_1_brd: BRD-009
max_phase_duration_weeks: 4
```

## What This Skill Does

1. **Reads BRD Documents** → Extracts FR/NFR counts, complexity, dependencies
2. **Analyzes Dependencies** → Builds dependency matrix using Data-First, Read-Before-Write principles
3. **Creates Atomic Phases** → Splits BRDs into ≤4-week phases with clear boundaries
4. **Sequences Phases** → Orders by dependencies, identifies critical path and parallel opportunities
5. **Defines Exit Criteria** → Measurable success criteria per phase
6. **Calculates Timeline** → Resource estimates, duration calculations, milestone mapping
7. **Generates IMPL Document** → Complete IMPL-TEMPLATE.md-compliant document
8. **Validates Output** → Checks atomicity, dependencies, traceability, token limits

## Key Principles

**Atomic Phase Decomposition**:
- ≤ 4 weeks duration per phase
- Single clear purpose (one BRD or sub-component)
- Independently deployable and testable
- Clear exit criteria with measurable outcomes
- Minimal coupling (1-2 dependencies max)

**Dependency Sequencing**:
- **Data-First**: Broker/database before business logic
- **Read-Before-Write**: Validation before enforcement
- **Infrastructure-Before-Application**: Calculation engines before consumers
- **Component Decomposition**: Split large BRDs by logical boundaries

**Phase Naming**:
- Use descriptive names: "Market Data Foundation", not "Phase 1"
- Format: `[Primary Function] [Implementation Scope]`

## Output Example

**Generated Document Structure**:
```
IMPL-001: Options Trading System Implementation Plan
├── Part 1: Project Context and Strategy
│   ├── Overview, Business Objectives, Scope
│   └── Dependencies (Upstream + External)
├── Part 2: Phased Implementation (12 phases)
│   ├── Phase 1: Market Data Foundation (BRD-009: 4 weeks)
│   ├── Phase 2: Observability Foundation (BRD-010: 1 week)
│   └── ... [10 more phases]
├── Part 3: Project Management and Risk
│   ├── Resource Allocation, Timeline, Milestones
│   └── Risk Register, Communication Plan
└── Part 4: Tracking and Completion
    ├── Deliverables Checklist (CTR/SPEC/TASKS)
    ├── Project Validation, Completion Criteria
    └── Sign-off (PM, Product Owner, Tech Lead)
```

**Timeline Optimization**:
- Sequential: 52 weeks (all phases one after another)
- Optimized: 27 weeks (48% reduction via parallel execution)
- Critical Path: Phase 1 → 3 → 6 → 11 (11 weeks)

## Common User Requests

**"Set BRD-X as Phase 1"**:
- Skill reorders phases to make BRD-X critical prerequisite
- Recalculates dependencies and timeline

**"Split BRD-Y into smaller phases"**:
- Skill decomposes BRD-Y by functional boundaries (state vs execution, validation vs enforcement)
- Creates sub-phases with independent exit criteria

**"Use meaningful phase names, not Phase 1, 2, 3"**:
- Skill generates descriptive names: "Data Integration Foundation", "Core Calculation Engine"
- Format: Primary Function + Implementation Scope

## IMPL Scope (What's Included)

✅ **IMPL Contains**:
- WHO: Team assignments, resource allocation
- WHEN: Timeline, milestones, phase durations
- WHAT: Deliverables (CTR/SPEC/TASKS documents)
- WHY: Business objectives, requirements satisfied

❌ **IMPL Excludes**:
- HOW: Technical implementation (→ SPEC)
- CODE: Python code, algorithms (→ TASKS)
- TESTS: BDD scenarios, unit tests (→ BDD/TASKS)
- ARCHITECTURE: System design choices (→ ADR)

## Validation Checks

**Automated Validation**:
- ✅ All phases ≤ 4 weeks duration
- ✅ No circular dependencies
- ✅ Exit criteria defined for all phases
- ✅ Deliverables specified (CTR/SPEC/TASKS)
- ✅ Traceability complete (all BRDs → phases)
- ✅ Token limits: Claude Code (50K-100K), Gemini CLI use file read tool >10K
- ✅ Objective language (no promotional content)
- ✅ No Python code blocks

## When NOT to Use This Skill

**Skip IMPL for**:
- Single BRD, < 2 weeks implementation
- Single developer, single component
- Low-risk bug fix or config change

**Go directly**: REQ → SPEC → TASKS

**Decision Criteria**: See [WHEN_TO_CREATE_IMPL.md]({project_root}/ai_dev_flow/WHEN_TO_CREATE_IMPL.md)

## Quick Commands

**After Generation**:
```bash
# Validate traceability
python {project_root}/scripts/validation/validate_traceability.py \
    {project_root}/docs/BRD/BRD-000_implementation_plan.md

# Check phase dependencies
python {project_root}/scripts/validation/validate_phase_dependencies.py \
    {project_root}/docs/BRD/BRD-000_implementation_plan.md

# Count tokens
wc -w {project_root}/docs/BRD/BRD-000_implementation_plan.md
```

## References

- **Full Skill**: [generate_implementation_plan.md](./generate_implementation_plan.md)
- **SDD Workflow**: [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md]({project_root}/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)
- **IMPL Template**: [IMPL-TEMPLATE.md]({project_root}/ai_dev_flow/IMPL/IMPL-TEMPLATE.md)
- **When to Create IMPL**: [WHEN_TO_CREATE_IMPL.md]({project_root}/ai_dev_flow/WHEN_TO_CREATE_IMPL.md)

---

**Version**: 1.0 | **Updated**: 2025-11-02 | **Complexity**: High
