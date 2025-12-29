# =============================================================================
# 📋 Document Authority: This is the PRIMARY STANDARD for IPLAN structure.
# All other documents (Schema, Creation Rules, Validation Rules) DERIVE from this template.
# - In case of conflict, this template is the single source of truth
# - Schema: IPLAN_SCHEMA.yaml - Machine-readable validation (derivative)
# - Creation Rules: IPLAN_CREATION_RULES.md - AI guidance for document creation (derivative)
# - Validation Rules: IPLAN_VALIDATION_RULES.md - AI checklist after document creation (derivative)
#   NOTE: VALIDATION_RULES includes all CREATION_RULES and may be extended for validation
# =============================================================================
---
title: "IPLAN-TEMPLATE: Implementation Plan"
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
  schema_reference: "IPLAN_SCHEMA.yaml"
  schema_version: "1.0"
---

> **📋 Document Authority**: This is the **PRIMARY STANDARD** for IPLAN structure.
> - **Schema**: `IPLAN_SCHEMA.yaml v1.0` - Validation rules
> - **Creation Rules**: `IPLAN_CREATION_RULES.md` - Usage guidance
> - **Validation Rules**: `IPLAN_VALIDATION_RULES.md` - Post-creation checks

# Implementation Plan - IPLAN-NN: [Descriptive Task/Feature Name]

**⚠️ CRITICAL**: Always reference [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) as the single source of truth for workflow steps, artifact definitions, and quality gates.

**Position**: Layer 12 (Implementation Work Plans) - translates TASKS into executable session plans with bash commands and verification steps.

## 1. Document Control

| Item | Details |
|------|---------|
| **ID** | IPLAN-NN |
| **Status** | Draft/Ready for Implementation/In Progress/Completed/Blocked |
| **Version** | [Semantic version, e.g., 1.0.0] |
| **Created** | YYYY-MM-DD HH:MM:SS TZ |
| **Last Updated** | YYYY-MM-DD HH:MM:SS TZ |
| **Author** | [AI Assistant/Developer Name] |
| **Estimated Effort** | [X hours or Y-Z hours range] |
| **Actual Effort** | [Actual hours - update upon completion] |
| **Complexity** | [1-5 scale: 1=minimal config, 5=architectural changes] |
| **Parent TASKS** | [TASKS-NN - code generation plan being implemented] |
| **Related Artifacts** | [SPEC-NN, REQ-NN, ADR-NN, BDD-NN] |
| **IPLAN-Ready Score** | ✅ 95% (Target: ≥90%) |

---

> **⚠️ UPSTREAM ARTIFACT REQUIREMENT**: Before completing traceability tags:
> 1. **Check existing artifacts**: List what upstream documents actually exist in `docs/`
> 2. **Reference only existing documents**: Use actual document IDs, not placeholders
> 3. **Use `null` appropriately**: Only when upstream artifact type genuinely doesn't exist for this feature
> 4. **Do NOT create phantom references**: Never reference documents that don't exist
> 5. **Do NOT create missing upstream artifacts**: If upstream artifacts are missing, skip that functionality. Only create functionality for existing upstream artifacts.



## 2. Position in Document Workflow

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

## 3. Objective

[1-2 sentence statement of what this implementation plan delivers, e.g., "Implement TASKS-01 Gateway Connection Service from scratch, creating async TCP connection management with retry logic, circuit breaker, comprehensive error handling, and 100% BDD test coverage."]

**Deliverables**:
- [Specific deliverable #1: e.g., "6 Python modules (connector, service, models, errors, retry, circuit breaker)"]
- [Specific deliverable #2: e.g., "Complete test suite (unit 85%, integration 75%, BDD 100%)"]
- [Specific deliverable #3: e.g., "Project structure, dependencies, configuration"]
- [Specific deliverable #4: e.g., "All BDD scenarios validated"]

---

## 4. Context

### 4.1 Current State Analysis

**Documentation Status**: [✅/⚠️/❌ percentage% Complete]
- [List key documentation artifacts with status]
- SPEC-NN: [Description and status]
- REQ-NN through REQ-NN: [Requirements coverage]
- BDD-NN: [Test scenarios defined]
- ADR-NN: [Architecture decisions documented]
- SYS-NN: [System requirements specified]
- TASKS-NN: [Implementation plan status]

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

### 4.2 Key Technical Decisions

**Architecture** (from [ADR-NN]):
- [Key architectural decision #1]
- [Key architectural decision #2]
- [Pattern/framework chosen and rationale]

**Error Handling** (from [SPEC-NN]):
- [Error handling strategy]
- [Exception types and error codes]
- [Retry/fallback approach]

**Resilience Patterns** (from [SPEC-NN]):
- [Retry strategy with parameters]
- [Circuit breaker configuration]
- [Timeout values]

**Observability** (from [SPEC-NN]):
- [Logging approach]
- [Metrics collection]
- [Tracing implementation]
- [Health check endpoints]

**Performance Targets** (from [SPEC-NN]):
- [p50/p95/p99 latency targets]
- [Throughput requirements]
- [Resource constraints]

**Test Coverage Targets** (from [TASKS-NN]):
- Unit Tests: [≥X%]
- Integration Tests: [≥Y%]
- BDD Scenarios: [100% or specific count]

---

## 5. Task List

### 5.1 Phase 0: Documentation Review (COMPLETED ✅ / PENDING)
- [x/☐] Read templates and standards
- [x/☐] Analyze SPEC and upstream artifacts
- [x/☐] Review TASKS document
- [x/☐] Validate traceability matrix
- [x/☐] Verify all cross-references

### 5.2 Phase 1: Project Foundation & Setup ([X hours])
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

### 5.3 Phase 2: Core Implementation ([X hours])
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

### 5.4 Phase 3: Testing & Validation ([X hours])
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

### 5.5 Phase 4: Quality Assurance & Deployment ([X hours])
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

## 6. Implementation Guide

### 6.1 Prerequisites

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

### 6.2 Execution Steps

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
- Implements: TASKS-NN
- Satisfies: REQ-NN, REQ-NN
- Tests: BDD-NN scenarios

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 6.3 Verification Checklist

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

### 6.4 Pre-Implementation Checklist

**MANDATORY** - Complete before writing code:

#### Code Reuse Search
- [ ] Search codebase for existing utilities: `grep -r "function_name" src/`
- [ ] Check for similar implementations in related modules
- [ ] Document reusable components found: ____________
- [ ] If duplicating code, document justification: ____________

#### Interface Definition
- [ ] Define Protocol/ABC interfaces before implementation
- [ ] Document interface contracts with type hints
- [ ] Specify return types for all public methods

#### Dependency Verification
- [ ] Verify all imports exist in project dependencies
- [ ] Check import compatibility with Python version
- [ ] Run syntax check: `python -m py_compile <file>`

### 6.5 Security Checklist

**MANDATORY** for code handling external input:

#### Input Validation
- [ ] Validate all string inputs (empty, length, pattern)
- [ ] Validate numeric ranges (min, max, precision)
- [ ] Sanitize file paths (no path traversal)
- [ ] Validate identifiers (no empty strings, proper format)

#### Hash/Crypto Selection
- [ ] Document hash algorithm choice and rationale
- [ ] Use SHA-256+ for security-sensitive hashing
- [ ] MD5/SHA-1 only for non-security checksums (document why)

#### Credential Handling
- [ ] No credentials in code or logs
- [ ] Use environment variables or secrets manager
- [ ] Mask sensitive data in error messages

### 6.6 Error Handling Standard

**MANDATORY** - All exception handling must follow:

#### Exception Rules
- [ ] NEVER use bare `except:` or `except Exception:` without re-raise
- [ ] Always use exception chaining: `raise NewError() from original`
- [ ] Log exceptions before handling: `logger.error("msg", exc_info=True)`
- [ ] Document retry behavior for recoverable errors

#### Required Pattern
```python
try:
    result = operation()
except SpecificError as e:
    logger.error("Operation failed: %s", e, exc_info=True)
    raise ServiceError("Descriptive message") from e
```

#### Prohibited Patterns
```python
# PROHIBITED - Silent swallowing
except Exception:
    pass

# PROHIBITED - No chaining
except ValueError:
    raise CustomError("msg")  # Missing 'from e'

# PROHIBITED - Bare except
except:
    return default_value
```

### 6.7 Async/Concurrency Checklist

**MANDATORY** for async code:

#### Lock Selection
- [ ] Use `asyncio.Lock()` for async code (NOT `threading.Lock`)
- [ ] Use `threading.RLock()` only for sync code with reentrant needs
- [ ] Document lock scope and what it protects

#### Resource Management
- [ ] Implement `async with` context manager for resources
- [ ] Add cleanup/close methods for stateful classes
- [ ] Cancel pending tasks in cleanup: `task.cancel()`

#### Cache Patterns
- [ ] Add cache invalidation method
- [ ] Add cache clearing method
- [ ] Document TTL and eviction strategy
- [ ] Use `asyncio.Lock` for cache updates in async code

#### Required Pattern for Resources
```python
class ResourceManager:
    async def __aenter__(self):
        await self._acquire()
        return self

    async def __aexit__(self, *args):
        await self.cleanup()

    async def cleanup(self):
        """Release all resources."""
        # Cancel tasks, close connections, clear caches
```

### 6.8 Documentation Standard

**MANDATORY** for all public APIs:

#### Docstring Requirements
- [ ] All Protocol methods have docstrings with Args/Returns
- [ ] All public classes have class-level docstrings
- [ ] Complex algorithms have inline comments

#### Type Hint Quality
- [ ] NO `Any` type without documented justification
- [ ] Use specific types: `Optional[SpecificType]` not `Optional[Any]`
- [ ] Define TypeAlias for complex types
- [ ] Use Protocol for duck typing instead of Any

#### Module Documentation
- [ ] `__init__.py` has module docstring
- [ ] `__all__` exports are documented
- [ ] Usage examples in module docstring or README

---

## 7. Technical Details

### 7.1 File Structure

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

### 7.2 Module Specifications

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

### 7.3 Configuration Parameters

| Parameter | Type | Default | Description | Source |
|-----------|------|---------|-------------|--------|
| [PARAM_1] | [type] | [value] | [Description] | [SPEC-NN] |
| [PARAM_2] | [type] | [value] | [Description] | [SPEC-NN] |

### 7.4 BDD Scenario Mapping

| BDD Document | Scenario | Implementation | Verification Method |
|--------------|----------|----------------|---------------------|
| [BDD-NN] | [Scenario name] | [Module/function] | [Test file:line] |
| [BDD-NN] | [Scenario name] | [Module/function] | [Test file:line] |

---

## 8. Traceability Tags

**Layer 12 Position**: IPLAN inherits tags from all upstream artifacts (Layers 0-11)

### 8.1 Required Tags (Mandatory)

All IPLAN documents MUST include these cumulative tags from upstream artifacts:

- `@brd: BRD.NN.EE.SS` - Business Requirements Document (Layer 1)
- `@prd: PRD.NN.EE.SS` - Product Requirements Document (Layer 2)
- `@ears: EARS.NN.EE.SS` - Event-Action-Response-State (Layer 3)
- `@bdd: BDD.NN.EE.SS` - Behavior-Driven Development (Layer 4)
- `@adr: ADR-NN` - Architecture Decision Record (Layer 5)
- `@sys: SYS.NN.EE.SS` - System Requirements (Layer 6)
- `@req: REQ.NN.EE.SS` - Atomic Requirements (Layer 7)
- `@spec: SPEC-NN` - Technical Specification (Layer 10)
- `@tasks: TASKS.NN.EE.SS` - Code Generation Plan (Layer 11)

### 8.2 Optional Tags (If Present in Project)

- `@impl: IMPL.NN.EE.SS` - Implementation Plan (Layer 8) - include if project uses IMPL
- `@ctr: CTR-NN` - Interface Contract (Layer 9) - include if contracts defined

### 8.3 Tag Format

**Standard Format**: `@artifact-type: TYPE.NN.TT.SS (Unified Element ID: DOC_TYPE.DOC_NUM.ELEM_TYPE.SEQ)`

**Examples**:
```
@brd: BRD.01.01.42
@prd: PRD.01.01.15
@ears: EARS.01.24.03
@bdd: BDD.01.13.05
@adr: ADR-02
@sys: SYS.02.25.01
@req: REQ.01.26.01
@spec: SPEC-01
@tasks: TASKS.01.29.01
@impl: IMPL.01.28.01 (optional)
@ctr: CTR-01 (optional)
```

### 8.4 Tag Validation Requirements

1. **Completeness**: All 9 mandatory tags MUST be present (11 if @impl/@ctr exist in project)
2. **Chain Integrity**: Each tag MUST reference a valid upstream document
3. **Bidirectional Links**: Tagged documents MUST reference this IPLAN document in their downstream traceability
4. **Format Compliance**: Tags MUST follow `@type: DOC-ID:NN` pattern
5. **Layer Hierarchy**: Tags MUST respect the 16-layer cumulative tagging hierarchy (Layer 0-15)

### 8.5 Validation Methods

- **Automated**: Run `/opt/data/docs_flow_framework/ai_dev_flow/scripts/validate_tags_against_docs.py`
- **Manual**: Verify each tag resolves to existing document in framework
- **Traceability Matrix**: Update `IPLAN-000_TRACEABILITY_MATRIX-TEMPLATE.md`

<!-- VALIDATOR:IGNORE-LINKS-START -->
### 8.6 Same-Type References (Conditional)

**Include this section only if same-type relationships exist between IPLAN documents.**

| Relationship | Document ID | Document Title | Purpose |
|--------------|-------------|----------------|---------|
| Related | [IPLAN-NN](./IPLAN-NN_...md) | [Related IPLAN title] | Shared session context |
| Depends | [IPLAN-NN](./IPLAN-NN_...md) | [Prerequisite IPLAN title] | Must complete before this |

**Tags:**<!-- VALIDATOR:IGNORE-LINKS-END -->

```markdown
@related-iplan: IPLAN-NN
@depends-iplan: IPLAN-NN
```

### 8.7 Thresholds Referenced

**Purpose**: IPLAN documents REFERENCE thresholds defined in the PRD threshold registry. All quantitative values in verification steps, success criteria, and performance targets must use `@threshold:` tags to ensure single source of truth.

**Threshold Naming Convention**: `@threshold: PRD.NN.category.subcategory.key`

**Format Reference**: See [THRESHOLD_NAMING_RULES.md](../THRESHOLD_NAMING_RULES.md) for complete naming standards.

**Thresholds Used in This Document**:
```yaml
# Thresholds referenced from PRD threshold registry
# Format: @threshold: PRD.NN.category.subcategory.key

performance:
  # Verification targets (Section 4.2, 11.1)
  - "@threshold: PRD.NN.perf.api.p50_latency"        # p50 latency verification
  - "@threshold: PRD.NN.perf.api.p95_latency"        # p95 latency verification
  - "@threshold: PRD.NN.perf.api.p99_latency"        # p99 latency verification
  - "@threshold: PRD.NN.perf.throughput.rps"         # Throughput verification

coverage:
  # Test coverage targets (Section 11.1)
  - "@threshold: PRD.NN.quality.test.unit_coverage"        # Unit test coverage target
  - "@threshold: PRD.NN.quality.test.integration_coverage" # Integration test coverage target
  - "@threshold: PRD.NN.quality.test.bdd_coverage"         # BDD scenario coverage target

timeout:
  # Operation timeouts for verification (Section 6.2)
  - "@threshold: PRD.NN.timeout.request.sync"        # Synchronous request timeout
  - "@threshold: PRD.NN.timeout.connection.default"  # Connection timeout

resource:
  # Resource constraints for validation (Section 11.2)
  - "@threshold: PRD.NN.resource.cpu.max_utilization"   # CPU utilization limit
  - "@threshold: PRD.NN.resource.memory.max_mb"         # Memory limit
```

**Example Usage in Verification Steps**:
```bash
# Performance verification
pytest tests/performance/ -v \
  --benchmark-min-rounds=100 \
  --benchmark-autosave \
  # Verify p95 latency < @threshold: PRD.NN.perf.api.p95_latency

# Coverage verification
pytest --cov --cov-fail-under=@threshold: PRD.NN.quality.test.unit_coverage
```

**Reference**: See [THRESHOLD_NAMING_RULES.md](../THRESHOLD_NAMING_RULES.md) for naming conventions.

---

## 9. Traceability

<!-- VALIDATOR:IGNORE-LINKS-START -->
<!-- VALIDATOR:IGNORE-LINKS-START -->
### 9.1 Upstream References (→ references TO)

**Direct Parent**:
- [TASKS-NN](../TASKS/[path]/TASKS-NN.md) - Code generation plan being implemented

**Technical Specifications**:
- [SPEC-NN](../SPEC/[path]/SPEC-NN.yaml) - Technical blueprint for implementation

**Requirements**:
- [REQ-NN](../REQ/[path]/REQ-NN.md) - Atomic requirements satisfied
- [REQ-NN](../REQ/[path]/REQ-NN.md) - Additional requirements

**Architecture Decisions**:
- [ADR-NN](../ADR/ADR-NN.md) - Architecture decisions guiding implementation
- [ADR-NN](../ADR/ADR-NN.md) - Technology/pattern choices

**System Requirements**:
- [SYS-NN](../SYS/[path]/SYS-NN.md) - System-level requirements

**BDD Scenarios**:
- `BDD/BDD-NN_{suite}/BDD-NN.SS_{slug}.feature` - Behavioral tests to satisfy

**EARS Requirements**:
- [EARS-NN](../EARS/[path]/EARS-NN.md) - Event-action-response specifications

**Product Requirements**:
- [PRD-NN](../PRD/[path]/PRD-NN.md) - Product requirements driving feature

**Business Requirements**:
- [BRD-NN](../BRD/[path]/BRD-NN.md) - Business needs and objectives

**Optional (if present)**:
- [IMPL-NN](../IMPL/[path]/IMPL-NN.md) - Implementation strategies
- [CTR-NN](../CTR/[path]/CTR-NN.md) - Interface contracts to implement


<!-- VALIDATOR:IGNORE-LINKS-END -->
<!-- VALIDATOR:IGNORE-LINKS-END -->
<!-- VALIDATOR:IGNORE-LINKS-START -->
### 9.2 Downstream Impact (← referenced BY)

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

<!-- VALIDATOR:IGNORE-LINKS-END -->
<!-- VALIDATOR:IGNORE-LINKS-START -->
### 9.3 Related Documents

**Sibling Documents**:
- [IPLAN-NN](./IPLAN-NN.md) - Related implementation plans
- [IPLAN-000_index.md](./IPLAN-000_index.md) - Index of all implementation plans

**Traceability Matrix**:
- [IPLAN-000_TRACEABILITY_MATRIX.md](./IPLAN-000_TRACEABILITY_MATRIX.md) - Complete traceability matrix

<!-- VALIDATOR:IGNORE-LINKS-END -->
### 9.4 Traceability Tags

**Required Tags** (Cumulative Tagging Hierarchy - Layer 12):
```markdown
@brd: BRD.NN.EE.SS
@prd: PRD.NN.EE.SS
@ears: EARS.NN.EE.SS
@bdd: BDD.NN.EE.SS
@adr: ADR-NN
@sys: SYS.NN.EE.SS
@req: REQ.NN.EE.SS
@impl: IMPL.NN.EE.SS
@ctr: CTR-NN
@spec: SPEC-NN
@tasks: TASKS.NN.EE.SS
```

**Format**: `@artifact-type: TYPE.NN.TT.SS`

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
@brd: BRD-NN
@prd: PRD-NN
@ears: EARS.NN.24.NN
@bdd: BDD.NN.13.NN
@adr: ADR-NN
@sys: SYS-NN
@req: REQ-NN
@impl: IMPL-NN
@ctr: CTR-NN
@spec: SPEC-NN
@tasks: TASKS.NN.NN.NN
```

**Validation**: Tags must reference existing documents and requirement IDs. Complete chain validation ensures all upstream artifacts (BRD through TASKS) are properly linked.

**Purpose**: Cumulative tagging enables complete traceability chains from business requirements through implementation plans (session context). IPLAN provides execution context with bash commands to implement TASKS specifications. See [TRACEABILITY.md](../TRACEABILITY.md#cumulative-tagging-hierarchy) for complete hierarchy documentation.

---

## 10. Risk Mitigation

### 10.1 Implementation Risks

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

### 10.2 Technical Risks

**Risk 3: [Technical Risk]**
- **Description**: [Technical challenge or uncertainty]
- **Impact**: [Effect on timeline/quality]
- **Mitigation**:
  - [Technical approach to address]
  - [Proof of concept needed]
  - [Alternative approaches]

### 10.3 Dependency Risks

**Risk 4: [Dependency Risk]**
- **Description**: [External dependency issue]
- **Impact**: [Potential blocker]
- **Mitigation**:
  - [Fallback option]
  - [Early validation approach]
  - [Communication plan]

---

## 11. Success Criteria

### 11.1 Coverage Metrics

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

### 11.2 Functional Validation

**Feature Completeness**:
- [ ] All modules implemented per specification
- [ ] All interfaces fulfilled
- [ ] All error cases handled
- [ ] All edge cases covered

**Quality Attribute Validation**:
- [ ] Performance targets met (p50/p95/p99)
- [ ] Resource constraints satisfied
- [ ] Scalability verified
- [ ] security requirements met

### 11.3 Documentation Quality

**Deliverables**:
- [ ] All code documented (docstrings, comments)
- [ ] README.md complete with examples
- [ ] API documentation generated
- [ ] Deployment guide created
- [ ] Traceability matrix updated

### 11.4 Integration Validation

**System Integration**:
- [ ] Interfaces work with dependent systems
- [ ] End-to-end workflows validated
- [ ] No regressions in existing functionality
- [ ] Deployment tested in staging environment

---

## 12. References

### 12.1 Framework Documentation
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Workflow guide
- [TRACEABILITY.md](../TRACEABILITY.md) - Cumulative tagging hierarchy
- [TOOL_OPTIMIZATION_GUIDE.md](../TOOL_OPTIMIZATION_GUIDE.md) - Token efficiency guidelines

### 12.2 Artifact Templates
- [TASKS-TEMPLATE.md](../TASKS/TASKS-TEMPLATE.md) - Parent artifact template
- [SPEC-TEMPLATE.yaml](../SPEC/SPEC-TEMPLATE.yaml) - Technical specification template
- [BDD-TEMPLATE.feature](../BDD/BDD-TEMPLATE.feature) - BDD scenario template

### 12.3 Related Artifacts
<!-- VALIDATOR:IGNORE-LINKS-START -->
- [TASKS-NN](../TASKS/[path]/TASKS-NN.md) - Parent code generation plan
<!-- VALIDATOR:IGNORE-LINKS-END -->
<!-- VALIDATOR:IGNORE-LINKS-START -->
- [SPEC-NN](../SPEC/[path]/SPEC-NN.yaml) - Technical specification
<!-- VALIDATOR:IGNORE-LINKS-END -->
<!-- VALIDATOR:IGNORE-LINKS-START -->
- [REQ-NN](../REQ/[path]/REQ-NN.md) - Requirements being implemented
<!-- VALIDATOR:IGNORE-LINKS-END -->

### 12.4 External References
- [External documentation or API references]
- [Library/framework documentation]
- [Standards or compliance documents]

---

## 13. Appendix

### 13.1 Glossary

| Term | Definition |
|------|------------|
| [Technical term 1] | [Definition] |
| [Technical term 2] | [Definition] |

### 13.2 Command Reference

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

### 13.3 Troubleshooting

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
## File Size Limits

- Target: 300–500 lines per file
- Maximum: 600 lines per file (absolute)
- If this plan approaches/exceeds limits, split into multiple IPLAN files (e.g., sprint/phase) and update cross-links.

## Document Splitting Standard

- Split by sprint/phase or functional scope
- Keep links to TASKS/REQ/SPEC in sync; update any indexes
- Validate references and run size lints
