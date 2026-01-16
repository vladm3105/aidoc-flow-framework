---
title: "Development Plan README"
tags:
  - tasks-guide
  - layer-11-artifact
  - shared-architecture
custom_fields:
  document_type: readme
  artifact_type: TASKS
  layer: 11
  priority: shared
  development_status: active
---

# Development Plan & Implementation Tracker - User Guide

**Schema Version**: 2.0
**Last Updated**: 2026-01-15

## Purpose

The Development Plan serves as the **central command center** for tracking TASKS (Layer 11) implementation across all development phases. It organizes work into priority-ordered phases with built-in quality gates and workflow enforcement.

**Workflow**: `SPEC (Layer 10) → TASKS (Layer 11) → Code → Tests`

**Key Functions:**
- **Implementation Roadmap**: Organize TASKS by phase and priority
- **Workflow Enforcement**: Embed pre/post-execution verification checklists
- **Status Tracking**: Track progress through YAML-based structured data
- **Audit Trail**: Maintain session log for continuity and regulatory compliance
- **Machine-Parsable**: YAML blocks enable automation and tooling integration

---

## Quick Start

### 1. Create Your Development Plan

```bash
# Copy template to your project
cp ai_dev_flow/11_TASKS/DEVELOPMENT_PLAN_TEMPLATE.md docs/DEVELOPMENT_PLAN.md
```

### 2. Customize Implementation Strategy

Update Section 1 with your project's phased approach:
- Foundation (Security & Observability)
- Data Layer (Persistence & Storage)
- Core Logic (Domain & Connectivity)
- Engines (Strategy & Analysis)
- UI (Reporting & Visualization)

### 3. Populate Phase Tracker

For each phase, add TASKS entries in the YAML blocks following the template structure.

---

## YAML-Based TASKS Structure (v2.0)

Each TASKS entry uses this structure (matching the YAML block in TASKS-TEMPLATE.md v2.0):

```yaml
# Machine-parsable tracking for DEVELOPMENT_PLAN.md integration
tasks_tracking:
  id: TASKS-NN                        # Unique TASKS identifier
  service_name: "[Service/Component Name]"  # Human-readable description
  priority: P0                        # P0 (critical), P1, P2
  dependents: "[Components that depend on this]"  # What depends on this
  
  workflow:
    # PRE-EXECUTION VERIFICATION (Rule 3)
    pre_check:
      status: NOT_STARTED             # NOT_STARTED → COMPLETED
      checklist:
        - verified_req: false         # Verified against REQ-NN
        - verified_spec: false        # Verified against SPEC-NN
        - confirmed_arch: false       # Confirmed architecture pattern
        - checked_deps: false         # All dependencies available
    
    # MAIN IMPLEMENTATION
    implementation:
      status: NOT_STARTED             # NOT_STARTED → IN_PROGRESS → COMPLETED
      started: null                   # YYYY-MM-DD
      completed: null                 # YYYY-MM-DD
    
    # POST-EXECUTION UPDATES (Rules 1 & 2)
    post_check:
      status: NOT_STARTED
      checklist:
        - tests_passing: false        # All tests pass
        - coverage_met: false         # Coverage thresholds met
        - docs_updated: false         # Documentation updated
        - session_logged: false       # Session log entry added
```

> **Note**: This structure is embedded in each TASKS document's "Development Plan Tracking" section. The DEVELOPMENT_PLAN.md aggregates these into phase groups.

---

## Mandatory Workflow Rules

### Rule 3: Pre-Execution Verification (BEFORE Implementation)

**When**: Before starting ANY TASKS implementation

**Complete These Checks:**
```yaml
pre_check:
  checklist:
    - verified_req: true          # Read and understood REQ-NN
    - verified_spec: true         # Reviewed SPEC-NN technical spec
    - confirmed_arch: true        # Validated architecture pattern
    - checked_deps: true          # All dependencies available
```

**How to Mark Complete:**
1. Open `DEVELOPMENT_PLAN.md`
2. Find your TASKS entry in the YAML block
3. Change each `false` to `true` as you verify
4. Update `status: NOT_STARTED` to `status: COMPLETED`

---

### Rule 2: Phase Tracker Update (AFTER Implementation)

**When**: Immediately after TASKS completes

**Update These Fields:**
```yaml
post_check:
  checklist:
    - tests_passing: true         # All tests pass
    - coverage_met: true          # Coverage thresholds met
    - docs_updated: true          # Documentation updated
    - session_logged: true        # Session log entry added
```

**How to Execute:**
1. In the YAML block, update:
   ```yaml
   implementation:
     status: COMPLETED            # Change from IN_PROGRESS
     completed: 2026-01-15        # Add completion date
   ```
2. Mark post_check checklist items as `true`

---

### Rule 1: Session Log Update (AFTER Implementation)

**When**: Immediately after TASKS completes

**Add Entry to Session Log:**
```yaml
post_check:
  checklist:
    - session_log_date: true           # Added date
    - session_log_task_id: true        # Added TASKS-XX
    - session_log_status: true         # Marked COMPLETED
    - session_log_summary: true        # Wrote summary
```

**How to Execute:**
1. Scroll to Section 3: Session Log
2. Add new row:
   ```markdown
   | 2026-01-08 | TASKS-XX | COMPLETED | Implemented [Service] with [Tech]. Verified [Tests]. |
   ```
3. Mark session log checklist items as `true` in YAML

---

## Status Progression

### Workflow Status Values

| Status | Meaning | When to Use |
|--------|---------|-------------|
| `NOT_STARTED` | Not yet begun | Initial state, no work done |
| `IN_PROGRESS` | Currently working | Active implementation |
| `BLOCKED` | Cannot proceed | Waiting on dependency or issue resolution |
| `COMPLETED` | Finished & verified | All work done, tests pass, documented |
| `DEFERRED` | Postponed | Moved to later phase or release |

### Typical Status Flow (v2.0)

```
pre_check:      NOT_STARTED → COMPLETED (verify all checklist items)
implementation: NOT_STARTED → IN_PROGRESS → COMPLETED
post_check:     NOT_STARTED → COMPLETED (update tracking)
```

> **Note**: The v2.0 YAML structure uses `implementation` (not `tasks`) as the main workflow block.

---

## Phase Organization

### Phase 0: Project Initialization
- **Goal**: Environment setup
- **Examples**: Poetry init, directory structure, dependency management
- **Priority**: All P0 (blocking everything else)

### Phase 1-N: Implementation Phases
- **Group by**: Logical layers or functional areas
- **Order by**: Priority within phase (P0, then P1, then P2)
- **Dependencies**: Use `dependents` field to track what needs this

### Priority Guidelines

| Priority | Definition | When to Use |
|----------|------------|-------------|
| **P0** | Critical path | Blocks other work, must complete first |
| **P1** | High priority | Important but not blocking |
| **P2** | Normal priority | Can be done in parallel or later |

---

## Session Log

**Purpose**: Audit trail and continuity between sessions

**Required Fields:**
- **Date**: YYYY-MM-DD format
- **Task ID**: TASKS-NN
- **Status**: Current status after this session
- **Notes**: Key accomplishments, technologies, blockers, verification

**Example Entry:**
```markdown
| 2026-01-08 | TASKS-42 | COMPLETED | Implemented Rate Limiter with Token Bucket algorithm. All 12 BDD scenarios pass. Performance: 50k req/s. |
```

---

## Machine-Parsable Features

The YAML-based structure enables:

### 1. Automated Status Reports
```python
import yaml

with open('DEVELOPMENT_PLAN.md') as f:
    content = f.read()
    # Extract YAML blocks
    yaml_blocks = extract_yaml_blocks(content)
    
    for block in yaml_blocks:
        data = yaml.safe_load(block)
        for task in data.values():
            print(f"{task['id']}: {task['workflow']['tasks']['status']}")
```

### 2. Progress Dashboards
```python
def calculate_phase_progress(phase_data):
    # v2.0: Use 'implementation' instead of 'tasks'
    completed = sum(1 for t in phase_data if t['workflow']['implementation']['status'] == 'COMPLETED')
    total = len(phase_data)
    return (completed / total) * 100
```

### 3. Validation Scripts
```python
def validate_workflow(task):
    """Ensure workflow rules are followed (v2.0 structure)"""
    pre = task['workflow']['pre_check']
    impl = task['workflow']['implementation']  # v2.0: 'implementation' not 'tasks'
    post = task['workflow']['post_check']
    
    # Rule: Can't start implementation without pre_check complete
    if impl['status'] != 'NOT_STARTED' and pre['status'] != 'COMPLETED':
        raise ValidationError(f"{task['id']}: Started without pre-check")
    
    # Rule: Can't complete implementation without post_check
    if impl['status'] == 'COMPLETED' and post['status'] != 'COMPLETED':
        raise ValidationError(f"{task['id']}: Completed without post-check")
```

### 4. Dependency Tracking
```python
def check_dependencies(plan):
    """Verify all dependencies are met before starting (v2.0 structure)"""
    for task in plan['tasks']:
        # v2.0: Use 'implementation' instead of 'tasks'
        if task['workflow']['implementation']['status'] == 'IN_PROGRESS':
            # Check all dependents are complete
            for dep_id in parse_dependents(task['dependents']):
                dep_task = find_task(plan, dep_id)
                if dep_task['workflow']['implementation']['status'] != 'COMPLETED':
                    print(f"WARNING: {task['id']} started but {dep_id} not complete")
```

---

## Best Practices

### 1. Update Immediately
- ✅ Update YAML status as soon as work completes
- ✅ Add session log entries same day
- ❌ Don't batch updates at end of week

### 2. Be Specific in Session Log
- ✅ "Implemented OAuth2 with PKCE flow. Tests: 15/15 pass. Performance: <100ms p95"
- ❌ "Worked on auth stuff"

### 3. Use Checklist Discipline
- ✅ Check every boolean flag as you complete items
- ✅ Don't mark pre_check complete until ALL items verified
- ❌ Don't skip checklist items "because you know what you're doing"

### 4. Track Blockers
- ✅ Use `BLOCKED` status with notes about what's blocking
- ✅ Update `dependents` field to track impact
- ✅ Add session log entry explaining blocker

### 5. Maintain YAML Validity
- ✅ Use YAML validators before committing
- ✅ Maintain consistent indentation (2 spaces)
- ❌ Don't break YAML syntax with missing colons or quotes

---

## Troubleshooting

### YAML Syntax Errors

**Problem**: Invalid YAML breaks parsing
**Solution**: Use online validator or:
```bash
python -c "import yaml; yaml.safe_load(open('DEVELOPMENT_PLAN.md').read())"
```

### Forgotten Updates

**Problem**: Completed TASKS but forgot to update
**Solution**: Run validation script:
```bash
python scripts/validate_development_plan.py docs/DEVELOPMENT_PLAN.md
```

### Lost Context Between Sessions

**Problem**: Don't remember what was done last session
**Solution**: Review Session Log (Section 3) - this is why it exists!

---

## Integration with Framework

### Relationship to Other Artifacts (v2.0)

```
REQ (Layer 7) → SPEC (Layer 10) → TASKS (Layer 11) → Code → Tests
                                        ↓
                                DEVELOPMENT_PLAN.md
                                (tracks TASKS execution)
```

### TASKS v2.0 Document Structure

The unified TASKS document (v2.0) has **11 sections**:

| Section | Purpose | Development Plan Relevance |
|---------|---------|---------------------------|
| 1. Objective | Deliverables and business value | What to track |
| 2. Scope | Inclusions, exclusions, prerequisites | Dependencies |
| 3. Implementation Plan | Phased steps with durations | Phase mapping |
| 4. Execution Commands | Setup, implementation, validation | Bash commands |
| 5. Constraints | Technical and quality constraints | Verification criteria |
| 6. Acceptance Criteria | Functional, quality, operational | Success measures |
| 7. Implementation Contracts | Provider/consumer contracts | Parallel dev coordination |
| 8. Traceability | Upstream refs, tags, code locations | Audit trail |
| 9. Risk & Mitigation | Risk table | Blocker prediction |
| 10. Session Log | Progress tracking | **Syncs with Dev Plan** |
| 11. Change History | Version history | Change tracking |

**Key Features:**
- **Section 4 (Execution Commands)**: Contains bash commands for implementation
- **Section 7 (Implementation Contracts)**: Type-safe interfaces for parallel development
- **YAML Tracking Block**: Embedded in each TASKS for Development Plan integration

**Development Plan Role:**
- Organizes TASKS into phases
- Tracks TASKS implementation status
- Enforces workflow rules (pre/post checks)
- Maintains audit trail via session log
- Aggregates YAML tracking blocks from individual TASKS documents

### References
- **Template**: `ai_dev_flow/11_TASKS/DEVELOPMENT_PLAN_TEMPLATE.md`
- **TASKS Template**: `ai_dev_flow/11_TASKS/TASKS-TEMPLATE.md`
- **TASKS Documentation**: `ai_dev_flow/11_TASKS/README.md`
- **Workflow Guide**: `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`

---

## Example: Complete TASKS Lifecycle

### 1. Pre-Execution (Rule 3)
```yaml
# BEFORE starting
pre_check:
  status: NOT_STARTED
  checklist:
    - verified_req: false
    - verified_spec: false
    - confirmed_arch: false
    - checked_deps: false
```

**Action**: Review REQ-NN, SPEC-NN, check architecture
```yaml
# AFTER verification
pre_check:
  status: COMPLETED          # ← Changed
  checklist:
    - verified_req: true     # ← All true
    - verified_spec: true    # v2.0: 'spec' not 'tasks'
    - confirmed_arch: true
    - checked_deps: true
```

### 2. Implementation
```yaml
implementation:
  status: IN_PROGRESS        # ← Mark when you start
  started: 2026-01-15        # ← Add start date
  completed: null
```

**Action**: Implement code using execution commands in TASKS document, write tests, verify

```yaml
implementation:
  status: COMPLETED          # ← Mark when done
  started: 2026-01-15
  completed: 2026-01-15      # ← Add completion date
```

### 3. Post-Execution (Rules 1 & 2)
```yaml
post_check:
  status: NOT_STARTED
  checklist:
    - tests_passing: false
    - coverage_met: false
    - docs_updated: false
    - session_logged: false
```

**Action**: Verify tests, update documentation, add session log entry
```yaml
post_check:
  status: COMPLETED               # ← Changed
  checklist:
    - tests_passing: true         # ← All true
    - coverage_met: true
    - docs_updated: true
    - session_logged: true
```

**Session Log Entry Added:**
```markdown
| 2026-01-08 | TASKS-42 | COMPLETED | Implemented Rate Limiter service. All tests pass. |
```

---

## Summary

The Development Plan transforms implementation tracking from "optional documentation" to "enforced workflow" by:

- Embedding quality gates (pre/post checks) directly in TASKS structure
- Using machine-parsable YAML for automation and reporting
- Maintaining complete audit trail through session log
- Enforcing discipline through detailed checklists
- Providing clear status progression and dependency tracking
**Remember**: The plan is only useful if you update it! Make updates immediately after completing work, not days later.

---

**Document Version**: 2.0
**Last Updated**: 2026-01-15
**Schema Reference**: TASKS-TEMPLATE.md v2.0
