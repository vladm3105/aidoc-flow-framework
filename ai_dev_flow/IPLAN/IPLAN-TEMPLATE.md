---
title: "IPLAN-TEMPLATE: implementation-plan"
tags:
  - iplan-template
  - layer-12-artifact
  - shared-architecture
  - document-template
custom_fields:
  document_type: template
  artifact_type: IPLAN
  layer: 12
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  template_for: implementation-plan
---

# Implementation Plan - IPLAN-NNN: [Descriptive Task/Feature Name]

**⚠️ CRITICAL**: Always reference [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) as the single source of truth for workflow steps, artifact definitions, and quality gates.

**Position**: Layer 12 (Implementation Work Plans) - translates TASKS into executable session plans with bash commands and verification steps.

## Document Control

| Item | Details |
|------|---------|
| **ID** | IPLAN-NNN |
| **Status** | Draft/Ready for Implementation/In Progress/Completed/Blocked |
| **Version** | [Semantic version, e.g., 1.0.0] |
| **Created** | YYYY-MM-DD HH:MM:SS TZ |
| **Last Updated** | YYYY-MM-DD HH:MM:SS TZ |
| **Author** | [AI Assistant/Developer Name] |
| **Estimated Effort** | [X hours or Y-Z hours range] |
| **Actual Effort** | [Actual hours - update upon completion] |
| **Complexity** | [1-5 scale: 1=minimal config, 5=architectural changes] |
| **Parent TASKS** | [TASKS-NNN - code generation plan being implemented] |
| **Related Artifacts** | [SPEC-NNN, REQ-NNN, ADR-NNN, BDD-NNN] |
| **IPLAN-Ready Score** | ✅ 95% (Target: ≥90%) |

---

## Position in Development Workflow

**IPLAN (Implementation Work Plans)** ← YOU ARE HERE

For complete traceability workflow with visual diagram, see: [index.md - Traceability Flow](../index.md#traceability-flow)

**Quick Reference**:
```
... → TASKS → **IPLAN** → Code → Tests → ...
                    ↑
            Layer 12: Session Context
            (bash commands, verification steps)
```

**Purpose**: Executable implementation plans with session context, bash commands, and verification steps
- **Input**: TASKS (AI code generation plan), SPEC (technical blueprint), CTR (contracts)
- **Output**: Step-by-step execution plan with commands and validation checkpoints
- **Consumer**: AI assistants (Claude Code, Gemini, etc.) and developers executing implementation

**Distinction from TASKS**:
- **TASKS**: AI code generation instructions (WHAT code to generate)
- **IPLAN**: Implementation work plans (HOW to execute with specific commands)

---

## Objective

[1-2 sentence statement of what this implementation plan delivers, e.g., "Implement TASKS-001 Gateway Connection Service from scratch, creating async TCP connection management with retry logic, circuit breaker, comprehensive error handling, and 100% BDD test coverage."]

**Deliverables**:
- [Specific deliverable #1: e.g., "6 Python modules (connector, service, models, errors, retry, circuit breaker)"]
- [Specific deliverable #2: e.g., "Complete test suite (unit 85%, integration 75%, BDD 100%)"]
- [Specific deliverable #3: e.g., "Project structure, dependencies, configuration"]
- [Specific deliverable #4: e.g., "All BDD scenarios validated"]

---

## Context

### Current State Analysis

**Documentation Status**: [✅/⚠️/❌ percentage% Complete]
- [List key documentation artifacts with status]
- SPEC-NNN: [Description and status]
- REQ-NNN through REQ-NNN: [Requirements coverage]
- BDD-NNN: [Test scenarios defined]
- ADR-NNN: [Architecture decisions documented]
- SYS-NNN: [System requirements specified]
- TASKS-NNN: [Implementation plan status]

**Code Status**: [✅/⚠️/❌ percentage% Complete]
- [Current implementation state]
- [Existing modules/files]
- [Test infrastructure status]
- [Configuration files present/absent]
- [Dependencies installed/missing]

**Previous Work Completed**:
1. [✅/❌] [Prior task or phase completed]
2. [✅/❌] [Documentation reviewed]
3. [✅/❌] [Environment prepared]

### Key Technical Decisions

**Architecture** (from [ADR-NNN]):
- [Key architectural decision #1]
- [Key architectural decision #2]
- [Pattern/framework chosen and rationale]

**Error Handling** (from [SPEC-NNN]):
- [Error handling strategy]
- [Exception types and error codes]
- [Retry/fallback approach]

**Resilience Patterns** (from [SPEC-NNN]):
- [Retry strategy with parameters]
- [Circuit breaker configuration]
- [Timeout values]

**Observability** (from [SPEC-NNN]):
- [Logging approach]
- [Metrics collection]
- [Tracing implementation]
- [Health check endpoints]

**Performance Targets** (from [SPEC-NNN]):
- [p50/p95/p99 latency targets]
- [Throughput requirements]
- [Resource constraints]

**Test Coverage Targets** (from [TASKS-NNN]):
- Unit Tests: [≥X%]
- Integration Tests: [≥Y%]
- BDD Scenarios: [100% or specific count]

---

## Task List

### Phase 0: Documentation Review (COMPLETED ✅ / PENDING)
- [x/☐] Read templates and standards
- [x/☐] Analyze SPEC and upstream artifacts
- [x/☐] Review TASKS document
- [x/☐] Validate traceability matrix
- [x/☐] Verify all cross-references

### Phase 1: Project Foundation & Setup ([X hours])
- [ ] **TASK-1.1**: [Task name]
  - [Specific action to take]
  - [Files/directories to create]
  - [Verification step]

- [ ] **TASK-1.2**: [Task name]
  - [Specific action to take]
  - [Configuration to set]
  - [Verification step]

- [ ] **TASK-1.3**: [Task name]
  - [Specific action to take]
  - [Dependencies to install]
  - [Verification step]

### Phase 2: Core Implementation ([X hours])
- [ ] **TASK-2.1**: [Component name] ([X hours])
  - File: [path/to/file.py]
  - [Implementation details]
  - [Classes/functions to create]
  - Verify: [Acceptance criteria]

- [ ] **TASK-2.2**: [Component name] ([X hours])
  - File: [path/to/file.py]
  - [Implementation details]
  - [Interfaces to implement]
  - Verify: [Acceptance criteria]

### Phase 3: Testing & Validation ([X hours])
- [ ] **TASK-3.1**: Unit tests ([X hours])
  - File: [test file path]
  - [Test scenarios to cover]
  - Target: [≥X% coverage]

- [ ] **TASK-3.2**: Integration tests ([X hours])
  - File: [test file path]
  - [Integration scenarios]
  - Target: [≥Y% coverage]

- [ ] **TASK-3.3**: BDD scenarios ([X hours])
  - [BDD feature files to implement]
  - [Scenarios to validate]
  - Target: 100% BDD coverage

### Phase 4: Quality Assurance & Deployment ([X hours])
- [ ] **TASK-4.1**: Code quality checks
  - [Linting, type checking, security scans]
  - [Fix all issues found]

- [ ] **TASK-4.2**: Documentation
  - [Update README, docstrings, examples]
  - [Create deployment guides]

- [ ] **TASK-4.3**: Final validation
  - [Run complete test suite]
  - [Verify all acceptance criteria met]
  - [Update traceability matrix]

---

## Implementation Guide

### Prerequisites

**Required Tools**:
- [Tool #1: e.g., Python 3.11+, Poetry]
- [Tool #2: e.g., Docker, PostgreSQL]
- [Tool #3: e.g., Git, text editor]

**Required Files Access**:
- [File/directory path #1 with read/write permissions]
- [File/directory path #2 with read permissions]
- [Configuration files location]

**Knowledge Required**:
- [Technology stack knowledge needed]
- [Framework/library familiarity]
- [Domain knowledge requirements]

**Environment Setup**:
- [Environment variable requirements]
- [Service dependencies (databases, APIs)]
- [Network/firewall requirements]

### Execution Steps

**Step 1: [Phase Name]**

```bash
# [Description of what this step does]
cd [/path/to/project]
[command to execute]
[another command]
```

Verification:
```bash
# Verify step completed successfully
[verification command]
```

Expected outcome:
- [What should be present after this step]
- [Files created or modified]
- [Services started]

**Step 2: [Phase Name]**

```bash
# [Description]
[bash commands]
```

Verification:
```bash
# [Verification commands]
[test or check command]
```

Expected outcome:
- [Expected results]

**Step 3: [Implementation Phase]**

For each module:
1. Create file: `[path/to/module.py]`
2. Implement: [specific functionality]
3. Test: Run `[test command]`
4. Verify: [acceptance criteria]

Bash execution:
```bash
# Create module
touch [file path]

# Run tests
pytest [test file] -v

# Verify coverage
pytest --cov=[module] --cov-report=term
```

**Step 4: [Testing Phase]**

```bash
# Run unit tests
pytest tests/unit/ -v --cov

# Run integration tests
pytest tests/integration/ -v

# Run BDD scenarios
pytest tests/bdd/ --gherkin-terminal-reporter

# Generate coverage report
pytest --cov --cov-report=html
```

**Step 5: [Quality Assurance]**

```bash
# Linting
ruff check .
black --check .

# Type checking
mypy src/

# security scan
bandit -r src/

# Run all checks
make quality-checks  # or equivalent
```

**Step 6: [Git Commit]**

```bash
cd [/path/to/project]
git add [files]

git commit -m "$(cat <<'EOF'
[commit message following format]

[Details]
- [Change #1]
- [Change #2]

[Traceability]
- Implements: TASKS-NNN
- Satisfies: REQ-NNN, REQ-NNN
- Tests: BDD-NNN scenarios

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### Verification Checklist

**After Phase 1:**
- [ ] Project directory structure exists
- [ ] Dependencies installed and importable
- [ ] Configuration files present and valid
- [ ] Test infrastructure functional

**After Phase 2:**
- [ ] All modules created and importable
- [ ] All interfaces implemented
- [ ] Type checking passes
- [ ] No syntax or import errors

**After Phase 3:**
- [ ] Unit test coverage ≥[X]%
- [ ] Integration test coverage ≥[Y]%
- [ ] All BDD scenarios pass (100%)
- [ ] Test reports generated

**After Phase 4:**
- [ ] All linting checks pass
- [ ] security scan passes (no high/critical issues)
- [ ] Documentation complete and accurate
- [ ] Traceability matrix updated
- [ ] Git commit clean and descriptive

**Complete Verification:**
- [ ] All acceptance criteria met
- [ ] All tests passing
- [ ] Code coverage targets achieved
- [ ] Performance benchmarks met
- [ ] security requirements satisfied
- [ ] Documentation complete
- [ ] Traceability validated
- [ ] Ready for deployment/integration

---

## Technical Details

### File Structure

```
[project-root]/
├── src/
│   └── [module]/
│       ├── __init__.py
│       ├── [component1].py
│       ├── [component2].py
│       └── [component3].py
├── tests/
│   ├── unit/
│   │   └── [module]/
│   ├── integration/
│   │   └── [module]/
│   └── bdd/
│       └── features/
├── [config files]
└── [documentation]
```

### Module Specifications

**Module 1: [Name]**
- File: `[path/to/file.py]`
- Purpose: [What this module does]
- Classes: [List of classes]
- Functions: [List of key functions]
- Dependencies: [Required imports]

**Module 2: [Name]**
- File: `[path/to/file.py]`
- Purpose: [What this module does]
- Classes: [List of classes]
- Functions: [List of key functions]
- Dependencies: [Required imports]

### Configuration Parameters

| Parameter | Type | Default | Description | Source |
|-----------|------|---------|-------------|--------|
| [PARAM_1] | [type] | [value] | [Description] | [SPEC-NNN] |
| [PARAM_2] | [type] | [value] | [Description] | [SPEC-NNN] |

### BDD Scenario Mapping

| BDD Document | Scenario | Implementation | Verification Method |
|--------------|----------|----------------|---------------------|
| [BDD-NNN] | [Scenario name] | [Module/function] | [Test file:line] |
| [BDD-NNN] | [Scenario name] | [Module/function] | [Test file:line] |

---

## Traceability Tags

**Layer 12 Position**: IPLAN inherits tags from all upstream artifacts (Layers 0-11)

### Required Tags (Mandatory)

All IPLAN documents MUST include these cumulative tags from upstream artifacts:

- `@brd: BRD-NNN:REQ-NNN` - Business Requirements Document (Layer 1)
- `@prd: PRD-NNN:REQ-NNN` - Product Requirements Document (Layer 2)
- `@ears: EARS-NNN:REQ-NNN` - Event-Action-Response-State (Layer 3)
- `@bdd: BDD-NNN:SCENARIO-NNN` - Behavior-Driven Development (Layer 4)
- `@adr: ADR-NNN` - Architecture Decision Record (Layer 5)
- `@sys: SYS-NNN:REQ-NNN` - System Requirements (Layer 6)
- `@req: REQ-NNN` - Atomic Requirements (Layer 7)
- `@spec: SPEC-NNN:regulatoryTION` - Technical Specification (Layer 10)
- `@tasks: TASKS-NNN:PHASE-X.Y` - Code Generation Plan (Layer 11)

### Optional Tags (If Present in Project)

- `@impl: IMPL-NNN` - Implementation Plan (Layer 8) - include if project uses IMPL
- `@ctr: CTR-NNN:regulatoryTION` - Interface Contract (Layer 9) - include if contracts defined

### Tag Format

**Standard Format**: `@artifact-type: DOCUMENT-ID:REQUIREMENT-ID`

**Examples**:
```
@brd: BRD-001:REQ-042
@prd: PRD-001:REQ-015
@ears: EARS-001:REQ-003
@bdd: BDD-001:SCENARIO-005
@adr: ADR-002
@sys: SYS-002:REQ-001
@req: REQ-001
@spec: SPEC-001:connection_service
@tasks: TASKS-001:PHASE-2.1
@impl: IMPL-001 (optional)
@ctr: CTR-001:IBGatewayConnector (optional)
```

### Tag Validation Requirements

1. **Completeness**: All 9 mandatory tags MUST be present (11 if @impl/@ctr exist in project)
2. **Chain Integrity**: Each tag MUST reference a valid upstream document
3. **Bidirectional Links**: Tagged documents MUST reference this IPLAN document in their downstream traceability
4. **Format Compliance**: Tags MUST follow `@type: DOC-ID:REQ-ID` pattern
5. **Layer Hierarchy**: Tags MUST respect the 16-layer cumulative tagging hierarchy (Layer 0-15)

### Validation Methods

- **Automated**: Run `/opt/data/docs_flow_framework/ai_dev_flow/scripts/validate_tags_against_docs.py`
- **Manual**: Verify each tag resolves to existing document in framework
- **Traceability Matrix**: Update `IPLAN-000_TRACEABILITY_MATRIX-TEMPLATE.md`

---

## Traceability

### Upstream References (→ references TO)

**Direct Parent**:
- [TASKS-NNN](../TASKS/[path]/TASKS-NNN.md) - Code generation plan being implemented

**Technical Specifications**:
- [SPEC-NNN](../SPEC/[path]/SPEC-NNN.yaml) - Technical blueprint for implementation
- [SPEC-NNN:section] - Specific sections referenced

**Requirements**:
- [REQ-NNN](../REQ/[path]/REQ-NNN.md) - Atomic requirements satisfied
- [REQ-NNN](../REQ/[path]/REQ-NNN.md) - Additional requirements

**Architecture Decisions**:
- [ADR-NNN](../ADR/ADR-NNN.md) - Architecture decisions guiding implementation
- [ADR-NNN](../ADR/ADR-NNN.md) - Technology/pattern choices

**System Requirements**:
- [SYS-NNN](../SYS/[path]/SYS-NNN.md) - System-level requirements

**BDD Scenarios**:
- [BDD-NNN](../BDD/[path]/BDD-NNN.feature) - Behavioral tests to satisfy
- [BDD-NNN:SCENARIO-NNN] - Specific scenarios validated

**EARS Requirements**:
- [EARS-NNN](../EARS/[path]/EARS-NNN.md) - Event-action-response specifications

**Product Requirements**:
- [PRD-NNN](../PRD/[path]/PRD-NNN.md) - Product requirements driving feature

**Business Requirements**:
- [BRD-NNN](../BRD/[path]/BRD-NNN.md) - Business needs and objectives

**Optional (if present)**:
- [IMPL-NNN](../IMPL/[path]/IMPL-NNN.md) - Implementation strategies
- [CTR-NNN](../CTR/[path]/CTR-NNN.md) - Interface contracts to implement

### Downstream Impact (← referenced BY)

**Code Implementation**:
- [src/module/file.py:function] - Code implementing this plan
- [src/module/file.py:class] - Classes created per this plan

**Test Artifacts**:
- [tests/unit/test_file.py] - Unit tests validating implementation
- [tests/integration/test_file.py] - Integration tests
- [tests/bdd/features/file.feature] - BDD scenario implementations

**Deployment Artifacts**:
- [config/deployment.yaml] - Deployment configurations
- [.github/workflows/ci.yml] - CI/CD pipeline definitions

### Related Documents

**Sibling Documents**:
- [IPLAN-NNN](./IPLAN-NNN.md) - Related implementation plans
- [IPLAN-000_index.md](./IPLAN-000_index.md) - Index of all implementation plans

**Traceability Matrix**:
- [IPLAN-000_TRACEABILITY_MATRIX.md](./IPLAN-000_TRACEABILITY_MATRIX.md) - Complete traceability matrix

### Traceability Tags

**Required Tags** (Cumulative Tagging Hierarchy - Layer 12):
```markdown
@brd: BRD-NNN:REQUIREMENT-ID
@prd: PRD-NNN:REQUIREMENT-ID
@ears: EARS-NNN:STATEMENT-ID
@bdd: BDD-NNN:SCENARIO-ID
@adr: ADR-NNN
@sys: SYS-NNN:regulatoryTION-ID
@req: REQ-NNN:REQUIREMENT-ID
@impl: IMPL-NNN:PHASE-ID
@ctr: CTR-NNN
@spec: SPEC-NNN
@tasks: TASKS-NNN
```

**Format**: `@artifact-type: DOCUMENT-ID:REQUIREMENT-ID`

**Layer 12 Requirements**: IPLAN must reference ALL upstream artifacts:
- `@brd`: Business Requirements Document(s)
- `@prd`: Product Requirements Document(s)
- `@ears`: EARS Requirements
- `@bdd`: BDD Scenarios
- `@adr`: Architecture Decision Records
- `@sys`: System Requirements
- `@req`: Atomic Requirements
- `@impl`: Implementation Plans (optional - include if exists in chain)
- `@ctr`: API Contracts (optional - include if exists in chain)
- `@spec`: Technical Specifications
- `@tasks`: Code Generation Plans

**Tag Placement**: Include tags in this section or at the top of the document (after Document Control).

**Example**:
```markdown
@brd: BRD-001:FR-030
@prd: PRD-003:FEATURE-002
@ears: EARS-001:EVENT-003
@bdd: BDD-003:scenario-realtime-quote
@adr: ADR-033
@sys: SYS-008:PERF-001
@req: REQ-003:interface-spec
@impl: IMPL-001:phase1
@ctr: CTR-001
@spec: SPEC-003
@tasks: TASKS-001
```

**Validation**: Tags must reference existing documents and requirement IDs. Complete chain validation ensures all upstream artifacts (BRD through TASKS) are properly linked.

**Purpose**: Cumulative tagging enables complete traceability chains from business requirements through implementation plans (session context). IPLAN provides execution context with bash commands to implement TASKS specifications. See [TRACEABILITY.md](../TRACEABILITY.md#cumulative-tagging-hierarchy) for complete hierarchy documentation.

---

## Risk Mitigation

### Implementation Risks

**Risk 1: [Risk Title]**
- **Description**: [What could go wrong]
- **Likelihood**: [High/Medium/Low]
- **Impact**: [High/Medium/Low - effect on project]
- **Mitigation**:
  - [Action to prevent or reduce risk]
  - [Contingency plan if risk occurs]
  - [Monitoring strategy]

**Risk 2: [Risk Title]**
- **Description**: [What could go wrong]
- **Likelihood**: [High/Medium/Low]
- **Impact**: [High/Medium/Low]
- **Mitigation**:
  - [Preventive action]
  - [Detection method]
  - [Response plan]

### Technical Risks

**Risk 3: [Technical Risk]**
- **Description**: [Technical challenge or uncertainty]
- **Impact**: [Effect on timeline/quality]
- **Mitigation**:
  - [Technical approach to address]
  - [Proof of concept needed]
  - [Alternative approaches]

### Dependency Risks

**Risk 4: [Dependency Risk]**
- **Description**: [External dependency issue]
- **Impact**: [Potential blocker]
- **Mitigation**:
  - [Fallback option]
  - [Early validation approach]
  - [Communication plan]

---

## Success Criteria

### Coverage Metrics

**Requirements Coverage**:
- [X/Y] atomic requirements implemented (target: 100%)
- [X/Y] BDD scenarios passing (target: 100%)
- All acceptance criteria satisfied

**Test Coverage**:
- Unit tests: ≥[X]% (target achieved: ✅/❌)
- Integration tests: ≥[Y]% (target achieved: ✅/❌)
- BDD scenarios: 100% (target achieved: ✅/❌)

**Code Quality**:
- Linting: 0 errors (✅/❌)
- Type checking: 0 errors (✅/❌)
- security scan: 0 high/critical issues (✅/❌)

### Functional Validation

**Feature Completeness**:
- [ ] All modules implemented per specification
- [ ] All interfaces fulfilled
- [ ] All error cases handled
- [ ] All edge cases covered

**Non-Functional Validation**:
- [ ] Performance targets met (p50/p95/p99)
- [ ] Resource constraints satisfied
- [ ] Scalability verified
- [ ] security requirements met

### Documentation Quality

**Deliverables**:
- [ ] All code documented (docstrings, comments)
- [ ] README.md complete with examples
- [ ] API documentation generated
- [ ] Deployment guide created
- [ ] Traceability matrix updated

### Integration Validation

**System Integration**:
- [ ] Interfaces work with dependent systems
- [ ] End-to-end workflows validated
- [ ] No regressions in existing functionality
- [ ] Deployment tested in staging environment

---

## References

### Framework Documentation
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Workflow guide
- [TRACEABILITY.md](../TRACEABILITY.md) - Cumulative tagging hierarchy
- [TOOL_OPTIMIZATION_GUIDE.md](../TOOL_OPTIMIZATION_GUIDE.md) - Token efficiency guidelines

### Artifact Templates
- [TASKS-TEMPLATE.md](../TASKS/TASKS-TEMPLATE.md) - Parent artifact template
- [SPEC-TEMPLATE.yaml](../SPEC/SPEC-TEMPLATE.yaml) - Technical specification template
- [BDD-TEMPLATE.feature](../BDD/BDD-TEMPLATE.feature) - BDD scenario template

### Related Artifacts
- [TASKS-NNN](../TASKS/[path]/TASKS-NNN.md) - Parent code generation plan
- [SPEC-NNN](../SPEC/[path]/SPEC-NNN.yaml) - Technical specification
- [REQ-NNN](../REQ/[path]/REQ-NNN.md) - Requirements being implemented

### External References
- [External documentation or API references]
- [Library/framework documentation]
- [Standards or compliance documents]

---

## Appendix

### Glossary

| Term | Definition |
|------|------------|
| [Technical term 1] | [Definition] |
| [Technical term 2] | [Definition] |

### Command Reference

Quick reference for common commands used in this implementation:

```bash
# Setup
[setup commands]

# Testing
[test commands]

# Quality checks
[quality check commands]

# Deployment
[deployment commands]
```

### Troubleshooting

**Issue 1: [Common Problem]**
- **Symptom**: [What user sees]
- **Cause**: [Root cause]
- **Solution**: [How to fix]

**Issue 2: [Common Problem]**
- **Symptom**: [What user sees]
- **Cause**: [Root cause]
- **Solution**: [How to fix]

---

**Document End**

**Next Actions**: [What to do after completing this implementation plan]
**Follow-up**: [Related tasks or future enhancements]
