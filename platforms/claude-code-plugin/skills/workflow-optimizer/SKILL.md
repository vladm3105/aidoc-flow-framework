---
title: "workflow-optimizer: Workflow navigation assistant for SDD documentation"
name: workflow-optimizer
description: Workflow navigation assistant that recommends next steps and optimizes documentation sequence through the SDD workflow
tags:
  - sdd-workflow
  - ai-assistant
  - utility
  - shared-architecture
custom_fields:
  layer: null
  artifact_type: null
  architecture_approaches: [ai-agent-based]
  priority: primary
  development_status: active
  skill_category: utility
  upstream_artifacts: [PRD-00, ADR-00]
  downstream_artifacts: []
---

# workflow-optimizer

## Purpose

Guide users through the SDD workflow by determining current position, recommending next steps, identifying parallel work opportunities, and tracking progress.

**Problem Solved**: Users must manually determine next steps in the 8-layer SDD workflow, leading to workflow friction, missed dependencies, and inefficient sequencing.

**Solution**: Analyze completed artifacts, determine workflow position, and provide prioritized recommendations for next steps with clear rationale.

## When to Use This Skill

**Use workflow-optimizer when**:
- Completed an artifact and need guidance on next steps
- Starting documentation and need workflow overview
- Want to identify parallel work opportunities
- Need progress report on documentation completion
- Unsure which artifacts to create next

**Do NOT use when**:
- Need skill recommendation for specific task (use skill-recommender)
- Need project context (use context-analyzer)
- Validating artifacts (use trace-check or quality-advisor)

## Skill Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| project_root | string | Yes | Root path of project to analyze |
| completed_artifact | string | No | ID of just-completed artifact (e.g., PRD-00) |
| focus_area | string | No | Optional filter: "core-workflow", "quality", "planning" |

## Skill Workflow

### Step 1: Analyze Project State

Scan project to determine documentation status:

**Artifact Discovery**:
```bash
# Discover all artifacts
find {project_root}/docs -name "*.md" -o -name "*.yaml" -o -name "*.feature"
```

**Status Extraction**:
Extract status from Document Control section:
- Draft
- In Review
- Approved
- Superseded
- Deprecated

**Project State Model**:
```yaml
project_state:
  scan_timestamp: 2025-11-29T14:30:00Z
  artifacts_by_type:
    BRD:
      total: 3
      approved: 2
      draft: 1
      latest: BRD-03
    PRD:
      total: 2
      approved: 1
      draft: 1
      latest: PRD-00
    EARS:
      total: 0
    # ... etc
  total_artifacts: 25
  approved_artifacts: 18
  draft_artifacts: 7
```

### Step 2: Determine Workflow Position

Map artifacts to SDD workflow layers:

**Layer Definition**:
```yaml
workflow_layers:
  layer_1:
    type: BRD
    name: Business Requirements
    prerequisite: null
    description: "Business objectives and stakeholder needs"

  layer_2:
    type: PRD
    name: Product Requirements
    prerequisite: BRD
    description: "Product features and user needs"

  layer_3:
    type: EARS
    name: Formal Requirements
    prerequisite: PRD
    description: "WHEN-THE-SHALL formal requirements"

  layer_4:
    type: BDD
    name: Behavior Tests
    prerequisite: EARS
    description: "Gherkin acceptance scenarios"

  layer_5:
    type: ADR
    name: Architecture Decisions
    prerequisite: BDD
    description: "Technical decision records"

  layer_6:
    type: SPEC
    name: Technical Specification
    prerequisite: ADR
    description: "Implementation-ready interfaces, data models, behavior contracts"

  layer_7:
    type: TDD
    name: Test-Driven Development Guide
    prerequisite: SPEC
    description: "Test case definitions, BDD-to-test mapping, quality thresholds"

  layer_8:
    type: IPLAN
    name: Implementation Plan
    prerequisite: TDD
    description: "Execution bridge: file manifest, commands, code audit trail - flows to Code layer"
```

**Position Calculation**:
```yaml
workflow_position:
  completed_layers: [1, 2]  # BRD, PRD done
  in_progress_layers: [3]   # EARS in progress
  blocked_layers: [4, 5, 6, 7, 8]  # Waiting on prerequisites
  ready_layers: [3]         # Can start now

  current_position:
    layer: 3
    type: EARS
    status: in_progress

  progress_percentage: 25%  # 2 of 8 layers complete
```

### Step 3: Identify Required Next Steps

Determine mandatory next artifacts:

**Dependency Analysis**:
```yaml
dependency_graph:
  PRD-00:
    completed: true
    downstream_required:
      - EARS (Layer 3) - formal requirements
      - BDD (Layer 4) - test scenarios
    downstream_later:
      - IPLAN (Layer 8) - execution planning

  EARS (to be created):
    upstream_required:
      - PRD-00 ✓ (completed)
    will_enable:
      - BDD (Layer 4)
      - ADR (Layer 5)
```

**Next Steps Priority**:
| Priority | Artifact | Rationale |
|----------|----------|-----------|
| P0 | EARS | Required downstream from PRD, blocks BDD and ADR |
| P1 | BDD | Can start once EARS begun, enables ADR |
| P2 | ADR | Requires BDD completion |

### Step 4: Identify Parallel Opportunities

Find work that can proceed in parallel:

**Parallelization Rules**:
```yaml
parallel_opportunities:
  rule_1:
    name: "EARS and BDD overlap"
    condition: "EARS in progress"
    parallel_work: "BDD scenarios for completed EARS"
    benefit: "Faster progress through testing layer"

  rule_2:
    name: "Multiple feature tracks"
    condition: "Multiple BRDs exist"
    parallel_work: "PRD for each BRD"
    benefit: "Parallel feature development"

  rule_3:
    name: "ADR independence"
    condition: "Technical decisions needed"
    parallel_work: "ADRs can be written in parallel"
    benefit: "Architecture decisions don't block each other"
```

**Parallel Work Output**:
```yaml
parallel_opportunities:
  can_parallelize:
    - track: "Feature A"
      current: EARS-01
      parallel: "Start BDD-01 scenarios for EARS-01 requirements"

    - track: "Feature B"
      current: PRD-00 complete
      parallel: "Start EARS-02 while Feature A progresses"

  blocked_parallelization:
    - item: "SPEC creation"
      blocker: "ADR layer incomplete"
      unblock_by: "Complete ADR-01 through ADR-05"
```

### Step 5: Calculate Progress Metrics

Generate progress report:

**Progress Metrics**:
```yaml
progress_report:
  overall:
    layers_complete: 2
    total_layers: 8
    percentage: 25%

  by_layer:
    - layer: 1 (BRD)
      status: complete
      artifacts: 3
      approved: 2

    - layer: 2 (PRD)
      status: complete
      artifacts: 2
      approved: 1

    - layer: 3 (EARS)
      status: in_progress
      artifacts: 0
      target: 3 (based on PRD features)

    - layer: 4 (BDD)
      status: blocked
      blocker: "EARS incomplete"

  estimated_remaining:
    artifacts: 25
    layers: 6

  critical_path:
    - EARS (blocks BDD)
    - BDD (blocks ADR)
    - ADR (blocks SPEC)
    - SPEC (blocks TDD)
    - TDD (blocks IPLAN)
```

### Step 6: Generate Recommendations

Provide actionable next-step guidance:

**Recommendation Format**:
```yaml
recommendations:
  context:
    completed_artifact: PRD-00
    workflow_position: Layer 2 complete
    progress: 17%

  next_steps:
    - priority: P0
      action: "Create EARS document"
      artifact_type: EARS
      skill: doc-ears
      rationale: "Required downstream from PRD-00. EARS formalizes product features into WHEN-THE-SHALL requirements."
      estimated_effort: "Medium (2-4 hours)"
      blocks: [BDD, ADR]

    - priority: P1
      action: "Start BDD scenarios"
      artifact_type: BDD
      skill: doc-bdd
      rationale: "Can begin once EARS started. Write scenarios for completed requirements."
      estimated_effort: "Medium (2-4 hours)"
      parallel_with: EARS

    - priority: P2
      action: "Consider ADR for key decisions"
      artifact_type: ADR
      skill: doc-adr
      rationale: "If architectural decisions needed, document early. Requires BDD completion."
      estimated_effort: "Low-Medium (1-3 hours)"
      condition: "After BDD progress"

  parallel_opportunities:
    - "Feature B: Start PRD-03 while Feature A progresses through EARS/BDD"
    - "Technical: Draft ADRs for known architecture decisions"

  blocked_items:
    - item: "SPEC creation"
      reason: "Requires ADR completion (Layer 5)"
      unblock_path: "Complete layers 3-5 first"

  workflow_guidance:
    current_focus: "EARS creation for PRD-00 features"
    short_term: "Complete EARS → BDD → ADR sequence"
    medium_term: "Progress through SPEC → TDD → IPLAN"

  progress_summary:
    completed: "BRD-01, BRD-02, BRD-03, PRD-01, PRD-00"
    in_progress: "None"
    next_milestone: "Complete Layer 3 (EARS)"
    overall: "25% complete (2/8 layers)"
```

## Example Usage

### Example 1: Post-PRD Guidance

**User Request**: "I just finished PRD-00, what should I do next?"

**Workflow Recommendations**:
```yaml
completed: PRD-00
position: Layer 2 complete

next_steps:
  1. Create EARS-01 (P0)
     - Formalize PRD-00 features into WHEN-THE-SHALL requirements
     - Run: /skill doc-ears

  2. Start BDD scenarios (P1)
     - Can begin once EARS requirements defined
     - Run: /skill doc-bdd

parallel_opportunity:
  "If other BRDs exist, you can create their PRDs in parallel"

progress: "17% → 25% after EARS completion"
```

### Example 2: Project Overview

**User Request**: "Where am I in the documentation workflow?"

**Workflow Status**:
```yaml
project_status:
  completed_layers:
    - Layer 1 (BRD): 3 documents ✓
    - Layer 2 (PRD): 2 documents ✓

  in_progress:
    - Layer 3 (EARS): 0 documents, target 5

  blocked:
    - Layers 4-8: Waiting on upstream completion

  progress: 25%

  critical_path:
    EARS → BDD → ADR → SPEC → TDD → IPLAN

  recommended_focus:
    "Complete EARS layer to unblock BDD and ADR"
```

### Example 3: Parallel Work Identification

**User Request**: "What can I work on in parallel?"

**Parallel Opportunities**:
```yaml
current_tracks:
  track_a:
    name: "Core Platform"
    position: EARS creation
    next: BDD scenarios

  track_b:
    name: "Partner Integration"
    position: BRD complete
    next: PRD creation (independent of Track A)

parallel_work:
  - "Track B PRD can proceed while Track A completes EARS"
  - "ADRs for known decisions can be drafted early"
  - "BDD scenarios can start once first EARS requirements defined"

sequential_requirements:
  - "SPEC requires ADR completion - no parallel path"
  - "TDD requires SPEC, IPLAN requires TDD - sequential"
```

## Integration with Other Skills

| Integration | Description |
|-------------|-------------|
| context-analyzer | Provides artifact inventory and traceability data |
| skill-recommender | Receives workflow position for better skill suggestions |
| doc-flow | Can be invoked by doc-flow for workflow orchestration |

## Quality Gates

### Definition of Done

- [ ] Project state analyzed
- [ ] Workflow position calculated
- [ ] Next steps prioritized (P0, P1, P2)
- [ ] Parallel opportunities identified
- [ ] Progress metrics calculated
- [ ] Actionable recommendations generated

### Performance Targets

| Metric | Target |
|--------|--------|
| Analysis latency | <1s for 50 artifacts |
| Recommendation generation | <500ms |
| Progress calculation | <200ms |

## Traceability

**Required Tags**:
```
@prd: PRD.00.00.004a
@adr: ADR-00
```

### Upstream Sources

| Source | Type | Reference |
|--------|------|-----------|
| PRD-00 | Product Requirements | [PRD-00]({project_root}/framework/layers/02_PRD/PRD-00_ai_assisted_documentation_features.yaml#PRD-00) |
| ADR-00 | Architecture Decision | [ADR-00]({project_root}/framework/layers/05_ADR/ADR-00_ai_powered_documentation_assistant_architecture.yaml#ADR-00) |

### Downstream Artifacts

| Artifact | Type | Reference |
|----------|------|-----------|
| doc-flow | Skill Consumer | Workflow orchestration |

---

## Version Information

**Version**: 1.0.0
**Created**: 2025-11-29
**Status**: Active
**Author**: AI Dev Flow Framework Team
