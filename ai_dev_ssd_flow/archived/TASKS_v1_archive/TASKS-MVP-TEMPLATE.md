---
title: "TASKS-MVP-TEMPLATE: Task Breakdown (MVP)"
tags:
  - tasks-template
  - mvp-template
  - layer-11-artifact
  - document-template
  - shared-architecture
custom_fields:
  document_type: template
  instance_document_type: tasks-document
  deliverable_type: code  # Options: code, document, ux, risk, process - inherited from SPEC
  artifact_type: TASKS
  layer: 11
  template_profile: mvp
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  schema_version: "2.0"
---

> **Dual-Format Note**:
>
> This MD template is the **primary source** for human workflow.
> - **For Autopilot**: See `TASKS-MVP-TEMPLATE.yaml` (YAML template)
> - **Shared Validation**: Both formats are validated by `TASKS_MVP_SCHEMA.yaml`
> - **Consistency Requirement**: MD and YAML templates MUST remain consistent.

---

<!--
AI_CONTEXT_START
Role: AI Implementation Planner
Objective: Create task breakdown documents for SPEC implementation.
Constraints:
- Define tasks for ONE component/feature per document.
- 13 numbered sections required (plus Document Control and Development Plan Tracking).
- Required cumulative tags: @brd, @prd, @ears, @bdd, @adr, @sys, @req, @ctr (if exists), @spec, @tspec.
- Required TASKS-specific tags: @spec (primary), @tspec (test coverage).
- Execution-Ready threshold: >=90%.
- Include phased implementation plans with execution commands.
- Include acceptance criteria with measurable outcomes.
AI_CONTEXT_END
-->

**MVP Template** - Single-file, streamlined TASKS for rapid MVP development.
Use this template for task breakdown documents covering single components.

**Validation Note**: MVP templates are intentionally streamlined.

References: Schema `TASKS_MVP_SCHEMA.yaml` | Rules `TASKS_MVP_CREATION_RULES.md`, `TASKS_MVP_VALIDATION_RULES.md`

# TASKS-NN: [Component Name] Task Breakdown

**MVP Scope**: Task breakdown for [Component Name] implementation from SPEC-NN.

## Document Control

| Item | Details |
|------|---------|
| **TASKS ID** | TASKS-NN |
| **Document Name** | [Implementation Plan Document Name] |
| **Status** | Draft / Review / Approved / In Progress / Completed / Blocked |
| **Version** | 1.0.0 |
| **Date Created** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD |
| **Author** | [Primary Author] |
| **Assigned To** | [Primary Developer] |
| **Priority** | Critical (P0) / High (P1) / Medium (P2) / Low (P3) |
| **Source SPEC** | SPEC-NN |
| **Estimated Effort** | [X] hours |
| **Actual Effort** | [X] hours (after completion) |
| **Complexity** | [1-5] (1=minimal config, 5=architectural changes) |
| **Execution-Ready Score** | [XX]% (Target: >=90%) |
| **Template Version** | 2.0 |

---

## Development Plan Tracking

```yaml
workflow:
  pre_check:
    status: "NOT_STARTED"  # NOT_STARTED -> COMPLETED
    checklist:
      verified_req: false       # Verified against REQ-NN
      verified_spec: false      # Verified against SPEC-NN
      confirmed_arch: false     # Confirmed architecture pattern
      checked_deps: false       # All dependencies available

  implementation:
    status: "NOT_STARTED"  # NOT_STARTED -> IN_PROGRESS -> COMPLETED
    started: null        # YYYY-MM-DD
    completed: null      # YYYY-MM-DD

  post_check:
    status: "NOT_STARTED"
    checklist:
      tests_passing: false      # All tests pass
      coverage_met: false       # Coverage thresholds met
      docs_updated: false       # Documentation updated
      session_logged: false     # Session log entry added
```

---

## 1. Objective

### 1.1 Summary

[2-3 sentences description of what this implementation accomplishes]

### 1.2 Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | [Deliverable 1] | [e.g., Core module with business logic] |
| 2 | [Deliverable 2] | [e.g., Unit tests with 85%+ coverage] |
| 3 | [Deliverable 3] | [e.g., Integration with external service] |
| 4 | [Deliverable 4] | [e.g., API documentation] |

### 1.3 Business Value

[Single sentence on why this matters to the business/product]

---

## 2. Scope

### 2.1 Inclusions

- [In-scope item 1: Feature or component to implement]
- [In-scope item 2: Specific functionality to deliver]
- [In-scope item 3: Integration points or APIs]

### 2.2 Exclusions

- [Out-of-scope item 1: Feature intentionally excluded]
- [Out-of-scope item 2: Technical debt not addressed]
- [Out-of-scope item 3: Future functionality]

### 2.3 Prerequisites

- [Prerequisite 1: Required infrastructure or service]
- [Prerequisite 2: Dependent component or module]
- [Prerequisite 3: External API or database availability]

---

## 3. Implementation Plan

### Phase 1: [Phase Name - e.g., Setup and Environment]

**Objective**: [Phase objective: What this phase achieves]

| Task ID | Task Name | Description | Dependencies | Est. Hours | Status |
|---------|-----------|-------------|--------------|------------|--------|
| TASK-01 | [Task Title] | [Detailed task description] | - | 2 | Not Started |
| TASK-02 | [Task Title] | [Detailed task description] | TASK-01 | 1 | Not Started |

**Acceptance Criteria**:
- [Criterion 1: Task completes when...]
- [Criterion 2: Task passes when...]

**Deliverables**: [Deliverable 1], [Deliverable 2]

**Duration**: 0.5 days

---

### Phase 2: [Phase Name - e.g., Core Implementation]

**Objective**: [Phase objective]

| Task ID | Task Name | Description | Dependencies | Est. Hours | Status |
|---------|-----------|-------------|--------------|------------|--------|
| TASK-03 | [Task Title] | [Detailed task description] | TASK-01, TASK-02 | 4 | Not Started |
| TASK-04 | [Task Title] | [Detailed task description] | TASK-03 | 2 | Not Started |

**Acceptance Criteria**:
- [Criterion: Core functionality implemented]
- [Criterion: Error handling implemented]

**Deliverables**: [Deliverable 1], [Deliverable 2]

**Duration**: 1 day

---

### Phase 3: [Phase Name - e.g., Testing and Validation]

**Objective**: [Phase objective]

| Task ID | Task Name | Description | Dependencies | Est. Hours | Status |
|---------|-----------|-------------|--------------|------------|--------|
| TASK-05 | [Task Title] | [Detailed task description] | TASK-04 | 1 | Not Started |

**Acceptance Criteria**:
- [Criterion: All tests pass]

**Deliverables**: [Deliverable 1], [Deliverable 2], [Deliverable 3]

**Duration**: 0.5 days

---

## 4. Execution Commands

### 4.1 Setup Commands

```bash
# Navigate to project directory
cd /path/to/project

# Create and activate virtual environment
python3 -m venv venv && source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4.2 Implementation Commands

```bash
# Create module directory
mkdir -p src/module

# Create implementation file
touch src/module/implementation.py

# Create test directory structure
mkdir -p tests/unit
```

### 4.3 Validation Commands

```bash
# Run unit tests
python3 -m pytest tests/ -v

# Check test coverage
python3 -m pytest --cov=src --cov-report=term-missing

# Run linting checks
python3 -m flake8 src/

# Run type checking
python3 -m mypy src/
```

---

## 5. Constraints

### 5.1 Technical Constraints

- [Technical constraint 1: Must use Python 3.9+]
- [Technical constraint 2: Must integrate with existing authentication system]
- [Technical constraint 3: Maximum response time 200ms]

### 5.2 Quality Constraints

- [Quality constraint 1: Code coverage must be >=85%]
- [Quality constraint 2: All tests must pass before commit]
- [Quality constraint 3: Must follow PEP 8 style guide]

### 5.3 Performance Constraints

- [Performance constraint 1: API must handle 1000 req/s]
- [Performance constraint 2: Database queries must complete in <100ms]
- [Performance constraint 3: Memory usage must remain under 512MB]

---

## 6. Acceptance Criteria

### 6.1 Functional Criteria

- [Functional criterion 1: All core features work as specified]
- [Functional criterion 2: Integration with external systems works]
- [Functional criterion 3: Error conditions handled properly]

### 6.2 Quality Criteria

- [Quality criterion 1: Code coverage >=85%]
- [Quality criterion 2: No critical linting issues]
- [Quality criterion 3: Performance benchmarks met]

### 6.3 Operational Criteria

- [Operational criterion 1: Can be deployed to production environment]
- [Operational criterion 2: Monitoring and logging in place]
- [Operational criterion 3: Rollback plan documented]

---

## 7. Implementation Contracts

### 7.1 Contracts Provided

| Contract Type | Description | Code Reference |
|---------------|-------------|----------------|
| Protocol Interface | Protocol interface definition for this service | `src/module/interfaces.py` |
| Data Model | Pydantic data models for input/output | `src/module/models.py` |

### 7.2 Contracts Consumed

| Contract Type | Description | Provided By | Interface Name |
|---------------|-------------|-------------|----------------|
| External API | External API contract this service depends on | CTR-NN | ExternalServiceInterface |
| Database | Database schema contract | SYS-NN | table1, table2 |

**Note**: If no contracts apply, state "No implementation contracts for this TASKS."

---

## 8. Traceability

### 8.1 Cumulative Tags (Layer 1-10)

| Tag | Reference | Description |
|-----|-----------|-------------|
| @brd | BRD.NN.TT.SS | Business requirement |
| @prd | PRD.NN.TT.SS | Product requirement |
| @ears | EARS.NN.25.SS | EARS statement |
| @bdd | BDD.NN.14.SS | BDD scenario |
| @adr | ADR-NN | Architecture decision |
| @sys | SYS.NN.26.SS | System requirement |
| @req | REQ.NN.27.SS | Atomic requirement |
| @ctr | CTR-NN | Data contract (if exists) |
| @spec | SPEC-NN | Technical specification |
| @tspec | TSPEC.NN.TT.SS | Test specification |

### 8.2 TASKS-Specific Tags

| Tag | Reference | Description |
|-----|-----------|-------------|
| @spec | SPEC-NN | Primary specification for task breakdown |
| @tspec | TSPEC.NN.TT.SS | Test specification reference |

### 8.3 Downstream References

| Tag | Reference | Description |
|-----|-----------|-------------|
| @impl | `src/module/implementation.py` | Implementation code |
| @code | `src/[component]/` | Source code location |
| @tests | `tests/unit/test_implementation.py` | Test implementation |

### 8.4 Cross-Links

| Link Type | Reference | Rationale |
|-----------|-----------|-----------|
| @depends | TASKS-NN | Hard prerequisite TASKS docs |
| @discoverability | TASKS-NN | Related TASKS (short rationale) |

---

## 9. Risk & Mitigation

| Risk ID | Risk Description | Probability | Impact | Mitigation Strategy | Owner |
|---------|------------------|-------------|--------|---------------------|-------|
| RISK-001 | [Risk: e.g., Third-party API may have rate limits] | High | High | [Mitigation: e.g., Implement retry logic with exponential backoff] | [Owner] |
| RISK-002 | [Risk: e.g., Database schema changes may break existing queries] | Medium | Medium | [Mitigation: e.g., Create database migration script, test in staging] | [Owner] |
| RISK-003 | [Risk: e.g., Team member may be unavailable] | Low | Medium | [Mitigation: e.g., Document code thoroughly, ensure knowledge sharing] | [Owner] |

---

## 10. Unit Test Results

| Test Suite | Function | Result | Coverage |
|------------|----------|--------|----------|
| `tests/unit/...` | [Core Logic] | Passed / Failed | XX% |
| `tests/integration/...` | [API Integration] | Passed / Failed | XX% |

**Coverage Summary**:
- Total Lines: [N]
- Covered: [N]
- Coverage: [XX]%

---

## 11. Implementation Summary

### 11.1 Summary

[Short description of the implementation execution]

### 11.2 Accomplishments

- [Completed configuration]
- [Implemented core logic]
- [Verified via tests]

### 11.3 Issues Encountered

| Issue | Description | Resolution/Workaround |
|-------|-------------|----------------------|
| [Issue 1] | [Description] | [Resolution] |

### 11.4 Remaining Work

- [Pending item 1]
- [Pending item 2]

---

## 12. Session Log

| Date | Task IDs | Progress Summary | Blockers | Next Steps |
|------|----------|------------------|----------|------------|
| YYYY-MM-DD | TASK-01, TASK-02 | [Progress: Completed setup and initial implementation] | - | [Continue with core implementation] |
| YYYY-MM-DD | TASK-03, TASK-04 | [Progress: Core features implemented] | [Blocker: External API latency] | [Implement error handling] |
| YYYY-MM-DD | TASK-05 | **Implementation Complete** - Summary: [deliverables], Tests: [N]/[N] Passed, Coverage: [X]% | - | [Ready for deployment] |

---

## 13. Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | YYYY-MM-DD | [Author Name] | Initial version |

---

## Appendix: Template Notes

**MVP Profile Notes**:
- 13 numbered sections (1-13) plus Document Control and Development Plan Tracking
- Section 4: Execution Commands added in v2.0
- Section 7: Implementation Contracts section supports parallel development
- Minimum Execution-Ready Score: 90%

**References**:
- Schema: `TASKS_MVP_SCHEMA.yaml`
- Creation Rules: `TASKS_MVP_CREATION_RULES.md`
- Validation Rules: `TASKS_MVP_VALIDATION_RULES.md`
