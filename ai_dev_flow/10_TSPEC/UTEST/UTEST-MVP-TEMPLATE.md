---
title: "UTEST-MVP-TEMPLATE: Unit Test Specification (MVP)"
tags:
  - utest-template
  - mvp-template
  - layer-10-artifact
  - document-template
  - shared-architecture
custom_fields:
  document_type: template
  artifact_type: UTEST
  layer: 10
  test_type_code: 40
  template_profile: mvp
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  schema_version: "1.0"
  complexity: 1
---

> **Dual-Format Note**:
>
> This MD template is the **primary source** for human workflow.
> - **For Autopilot**: See `UTEST-MVP-TEMPLATE.yaml` (YAML template)
> - **Shared Validation**: Both formats are validated by `UTEST_MVP_SCHEMA.yaml`
> - **Consistency Requirement**: MD and YAML templates MUST remain consistent.

---

<!--
AI_CONTEXT_START
Role: AI Test Engineer
Objective: Create unit test specifications for TDD workflow.
Constraints:
- Define test cases for ONE component/module per document.
- 6 sections required (aligned with MVP requirements).
- Required traceability tags: @req, @spec.
- TASKS-Ready threshold: ≥90%.
- Use I/O tables for all test cases.
- Include pseudocode for complex test logic.
- Categorize tests: [Logic], [State], [Validation], [Edge].
AI_CONTEXT_END
-->

**MVP Template** — Single-file, streamlined UTEST for rapid MVP development.
Use this template for unit test specifications covering single components.

**Validation Note**: MVP templates are intentionally streamlined.

References: Schema `UTEST_MVP_SCHEMA.yaml` | Rules `UTEST_MVP_CREATION_RULES.md`, `UTEST_MVP_VALIDATION_RULES.md` | Matrix `TSPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md`

# UTEST-NN: [Component Name] Unit Test Specification

**MVP Scope**: Unit test specifications for [Component Name] targeting ≥90% REQ coverage.

## 1. Document Control

| Item | Details |
|------|---------|
| **Status** | Draft / Review / Approved / Implemented |
| **Version** | 0.1.0 |
| **Date Created** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD |
| **Author** | [Author name] |
| **Component** | [Component/module name] |
| **SPEC Reference** | SPEC-NN |
| **Coverage Target** | ≥90% |
| **TASKS-Ready Score** | [XX]% (Target: ≥90%) |
| **Template Version** | 1.0 |

---

## 2. Test Scope

### 2.1 Component Under Test

| Attribute | Value |
|-----------|-------|
| **Component** | [Component name] |
| **Module Path** | `src/[path]/[module].py` |
| **SPEC Reference** | @spec: SPEC-NN |
| **REQ Coverage** | @req: REQ.NN.10.01, REQ.NN.10.02 |

### 2.2 Test Categories

| Category | Count | Description |
|----------|-------|-------------|
| [Logic] | [N] | Business logic validation |
| [State] | [N] | State transition tests |
| [Validation] | [N] | Input validation tests |
| [Edge] | [N] | Boundary condition tests |
| **Total** | [N] | |

### 2.3 Dependencies

| Dependency | Mock Strategy |
|------------|---------------|
| [Database] | In-memory SQLite |
| [External API] | Mock responses |
| [Cache] | Fake cache implementation |

---

## 3. Test Case Index

| ID | Name | Category | REQ Coverage | Priority |
|----|------|----------|--------------|----------|
| TSPEC.NN.40.01 | [Test name] | [Logic] | REQ.NN.10.01 | P1 |
| TSPEC.NN.40.02 | [Test name] | [Validation] | REQ.NN.10.02 | P1 |
| TSPEC.NN.40.03 | [Test name] | [Edge] | REQ.NN.10.01 | P2 |
| TSPEC.NN.40.04 | [Test name] | [State] | REQ.NN.10.03 | P2 |

---

## 4. Test Case Details

### TSPEC.NN.40.01: [Test Name]

**Category**: [Logic]

**Traceability**:
- @req: REQ.NN.10.01
- @spec: SPEC-NN (Section X.Y)

**Input/Output Table**:

| Input | Expected Output | Notes |
|-------|-----------------|-------|
| `param1="valid"` | `True` | Happy path |
| `param1=""` | `ValidationError` | Empty input |
| `param1=None` | `TypeError` | Null input |

**Pseudocode**:

```
GIVEN valid input parameters
WHEN function_under_test(param1) is called
THEN result equals expected_output
AND no side effects occur
```

**Error Cases**:

| Error Condition | Expected Behavior |
|-----------------|-------------------|
| Invalid input type | Raise `TypeError` |
| Empty string | Raise `ValidationError` |
| Null value | Raise `TypeError` |

---

### TSPEC.NN.40.02: [Test Name]

**Category**: [Validation]

**Traceability**:
- @req: REQ.NN.10.02
- @spec: SPEC-NN (Section X.Y)

**Input/Output Table**:

| Input | Expected Output | Notes |
|-------|-----------------|-------|
| `data={"key": "value"}` | `True` | Valid schema |
| `data={}` | `False` | Missing required field |
| `data={"key": 123}` | `False` | Wrong type |

**Pseudocode**:

```
GIVEN input data dictionary
WHEN validate_schema(data) is called
THEN returns True for valid schema
AND returns False for invalid schema
```

**Error Cases**:

| Error Condition | Expected Behavior |
|-----------------|-------------------|
| Missing required field | Return `False` |
| Wrong field type | Return `False` |
| Extra unknown field | Return `True` (ignored) |

---

### TSPEC.NN.40.03: [Test Name]

**Category**: [Edge]

**Traceability**:
- @req: REQ.NN.10.01
- @spec: SPEC-NN (Section X.Y)

**Input/Output Table**:

| Input | Expected Output | Notes |
|-------|-----------------|-------|
| `value=0` | `True` | Minimum boundary |
| `value=MAX_INT` | `True` | Maximum boundary |
| `value=-1` | `False` | Below minimum |
| `value=MAX_INT+1` | `False` | Above maximum |

**Pseudocode**:

```
GIVEN boundary value input
WHEN validate_range(value) is called
THEN accepts values within [0, MAX_INT]
AND rejects values outside range
```

---

### TSPEC.NN.40.04: [Test Name]

**Category**: [State]

**Traceability**:
- @req: REQ.NN.10.03
- @spec: SPEC-NN (Section X.Y)

**Input/Output Table**:

| Initial State | Action | Expected State |
|---------------|--------|----------------|
| `IDLE` | `start()` | `RUNNING` |
| `RUNNING` | `pause()` | `PAUSED` |
| `PAUSED` | `resume()` | `RUNNING` |
| `RUNNING` | `stop()` | `STOPPED` |

**Pseudocode**:

```
GIVEN object in initial_state
WHEN action() is called
THEN state transitions to expected_state
AND state_changed event is emitted
```

---

## 5. REQ Coverage Matrix

| REQ ID | REQ Title | Test IDs | Coverage |
|--------|-----------|----------|----------|
| REQ.NN.10.01 | [Title] | TSPEC.NN.40.01, TSPEC.NN.40.03 | ✅ |
| REQ.NN.10.02 | [Title] | TSPEC.NN.40.02 | ✅ |
| REQ.NN.10.03 | [Title] | TSPEC.NN.40.04 | ✅ |

**Coverage Summary**:
- Total REQ elements: [N]
- Covered: [N]
- Coverage: [XX]%

---

## 6. Traceability

### 6.1 Upstream References

| Tag | Reference | Description |
|-----|-----------|-------------|
| @req | REQ.NN.10.01 | [Requirement title] |
| @req | REQ.NN.10.02 | [Requirement title] |
| @spec | SPEC-NN | [Specification reference] |

### 6.2 Downstream References

| Tag | Reference | Description |
|-----|-----------|-------------|
| @tasks | TASKS-NN | Implementation tasks |
| @code | `tests/unit/test_[component].py` | Test implementation |

---

## Appendix: Test Infrastructure

### Required Fixtures

```python
@pytest.fixture
def component_under_test():
    """Create component instance for testing."""
    return ComponentClass()

@pytest.fixture
def mock_dependency():
    """Mock external dependency."""
    return Mock(spec=DependencyClass)
```

### Mock Configuration

| Mock Target | Return Value | Side Effects |
|-------------|--------------|--------------|
| `external_api.call()` | `{"status": "ok"}` | None |
| `database.query()` | `[row1, row2]` | None |
