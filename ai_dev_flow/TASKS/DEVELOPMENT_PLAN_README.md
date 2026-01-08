# Development Plan & Implementation Tracker - User Guide

## Purpose

The Development Plan serves as the **central command center** for tracking TASKS (Layer 11) implementation across all development phases. It organizes work into priority-ordered phases with built-in quality gates and workflow enforcement.

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
cp ai_dev_flow/TASKS/DEVELOPMENT_PLAN_TEMPLATE.md docs/DEVELOPMENT_PLAN.md
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

## YAML-Based TASKS Structure

Each TASKS entry uses this comprehensive structure:

```yaml
phase_N_tasks:
  - id: TASKS-XX                      # Unique TASKS identifier
    service_name: "[Service Name]"    # Human-readable description
    priority: P0                      # P0 (critical), P1, P2
    dependents: "[Component Names]"   # What depends on this
    
    workflow:
      # PRE-EXECUTION VERIFICATION (Rule 3)
      pre_check:
        status: NOT_STARTED           # NOT_STARTED → COMPLETED
        checklist:
          - verified_req: false       # ✅ Verified against REQ-NN
          - verified_tasks: false     # ✅ Verified against TASKS-NN  
          - confirmed_arch: false     # ✅ Confirmed Architecture
          - checked_gaps: false       # ✅ Checked for gaps
          - reviewed_upstream: false  # ✅ Reviewed upstream docs
          - confirmed_deps: false     # ✅ Confirmed dependencies
      
      # MAIN IMPLEMENTATION
      tasks:
        status: NOT_STARTED           # Status progression tracking
        iplan_id: IPLAN-XX            # Associated implementation plan
        iplan_status: NOT_STARTED     # IPLAN execution status
      
      # POST-EXECUTION UPDATES (Rules 1 & 2)
      post_check:
        status: NOT_STARTED
        checklist:
          # Rule 2: Phase Tracker Update
          - tasks_status_updated: false    # ✅ Update TASKS status
          - iplan_status_updated: false    # ✅ Update IPLAN status
          - completion_date_added: false   # ✅ Add completion date
          # Rule 1: Session Log Update
          - session_log_date: false        # ✅ Log completion date
          - session_log_task_id: false     # ✅ Log TASKS ID
          - session_log_status: false      # ✅ Log COMPLETED status
          - session_log_summary: false     # ✅ Log work summary
```

---

## Mandatory Workflow Rules

### Rule 3: Pre-Execution Verification (BEFORE Implementation)

**When**: Before starting ANY TASKS/IPLAN implementation

**Complete These Checks:**
```yaml
pre_check:
  checklist:
    - verified_req: true          # Read and understood REQ-NN
    - verified_tasks: true        # Reviewed TASKS-NN scope
    - confirmed_arch: true        # Validated architecture pattern
    - checked_gaps: true          # No missing logic/fields
    - reviewed_upstream: true     # Consistency with upstream
    - confirmed_deps: true        # All dependencies available
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
    - tasks_status_updated: true       # Updated in YAML above
    - iplan_status_updated: true       # Updated in YAML above
    - completion_date_added: true      # Added to notes
```

**How to Execute:**
1. In the YAML block, update:
   ```yaml
   tasks:
     status: COMPLETED              # Change from IN_PROGRESS
     iplan_status: COMPLETED        # If IPLAN was used
   ```
2. Mark phase tracker checklist items as `true`

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

### Typical Status Flow

```
pre_check:   NOT_STARTED → COMPLETED (verify all checklist items)
tasks:       NOT_STARTED → IN_PROGRESS → COMPLETED
post_check:  NOT_STARTED → COMPLETED (update tracking)
```

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
- **Task ID**: TASKS-NN or IPLAN-NN
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
    completed = sum(1 for t in phase_data if t['workflow']['tasks']['status'] == 'COMPLETED')
    total = len(phase_data)
    return (completed / total) * 100
```

### 3. Validation Scripts
```python
def validate_workflow(task):
    """Ensure workflow rules are followed"""
    pre = task['workflow']['pre_check']
    main = task['workflow']['tasks']
    post = task['workflow']['post_check']
    
    # Rule: Can't start TASKS without pre_check complete
    if main['status'] != 'NOT_STARTED' and pre['status'] != 'COMPLETED':
        raise ValidationError(f"{task['id']}: Started without pre-check")
    
    # Rule: Can't complete TASKS without post_check
    if main['status'] == 'COMPLETED' and post['status'] != 'COMPLETED':
        raise ValidationError(f"{task['id']}: Completed without post-check")
```

### 4. Dependency Tracking
```python
def check_dependencies(plan):
    """Verify all dependencies are met before starting"""
    for task in plan['tasks']:
        if task['workflow']['tasks']['status'] == 'IN_PROGRESS':
            # Check all dependents are complete
            for dep_id in parse_dependents(task['dependents']):
                dep_task = find_task(plan, dep_id)
                if dep_task['workflow']['tasks']['status'] != 'COMPLETED':
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

### Relationship to Other Artifacts

```
REQ (Layer 7) → TASKS (Layer 11) → IPLAN (Layer 12) → Implementation
                     ↓
            DEVELOPMENT_PLAN.md
            (tracks TASKS execution)
```

**Development Plan Role:**
- Organizes TASKS into phases
- Tracks TASKS implementation status
- Links TASKS to IPLAN
- Enforces workflow rules
- Maintains audit trail

### References
- **Template**: `ai_dev_flow/TASKS/DEVELOPMENT_PLAN_TEMPLATE.md`
- **TASKS Documentation**: `ai_dev_flow/TASKS/README.md`
- **IPLAN Documentation**: `ai_dev_flow/IPLAN/README.md`
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
    ...
```

**Action**: Review REQ-42, TASKS-42, check architecture
```yaml
# AFTER verification
pre_check:
  status: COMPLETED          # ← Changed
  checklist:
    - verified_req: true     # ← All true
    - verified_tasks: true
    - confirmed_arch: true
    - checked_gaps: true
    - reviewed_upstream: true
    - confirmed_deps: true
```

### 2. Implementation
```yaml
tasks:
  status: IN_PROGRESS        # ← Mark when you start
  iplan_id: IPLAN-42
  iplan_status: IN_PROGRESS
```

**Action**: Implement code, write tests, verify

```yaml
tasks:
  status: COMPLETED          # ← Mark when done
  iplan_id: IPLAN-42
  iplan_status: COMPLETED
```

### 3. Post-Execution (Rules 1 & 2)
```yaml
post_check:
  status: NOT_STARTED
  checklist:
    - tasks_status_updated: false
    ...
```

**Action**: Update YAML above, add session log entry
```yaml
post_check:
  status: COMPLETED               # ← Changed
  checklist:
    - tasks_status_updated: true  # ← All true
    - iplan_status_updated: true
    - completion_date_added: true
    - session_log_date: true
    - session_log_task_id: true
    - session_log_status: true
    - session_log_summary: true
```

**Session Log Entry Added:**
```markdown
| 2026-01-08 | TASKS-42 | COMPLETED | Implemented Rate Limiter service. All tests pass. |
```

---

## Summary

The Development Plan transforms implementation tracking from "optional documentation" to "enforced workflow" by:

✅ Embedding quality gates (pre/post checks) directly in TASKS structure
✅ Using machine-parsable YAML for automation and reporting
✅ Maintaining complete audit trail through session log
✅ Enforcing discipline through detailed checklists
✅ Providing clear status progression and dependency tracking

**Remember**: The plan is only useful if you update it! Make updates immediately after completing work, not days later.
