---
title: "ICON-01: Validation Protocol (Example)"
tags:
  - icon-example
  - layer-11-artifact
  - shared-architecture
  - implementation-contract
custom_fields:
  document_type: example
  artifact_type: ICON
  layer: 11
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  contract_type: protocol
  provider_tasks: TASKS-NN
  consumer_count: 3
  providers: [TASKS-NN]
  consumers: [TASKS-NN, TASKS-NN, TASKS-NN]
---

# ICON-01: Validation Protocol (Example)

**Position**: Layer 11 (shared with TASKS) - Implementation Contracts for type-safe parallel development.

## Document Control

| Item | Details |
|------|---------|
| **Status** | Active |
| **Version** | 1.0.0 |
| **Date Created** | 2025-11-13 |
| **Last Updated** | 2025-11-13 |
| **Author** | Example Team |
| **Contract Type** | Protocol Interface |
| **Providers** | TASKS-NN (Validation Service) |
| **Consumers** | TASKS-NN, TASKS-NN, TASKS-NN |

## Traceability Tags

```markdown
@brd: BRD-NN
@prd: PRD-NN
@ears: EARS-NN
@bdd: BDD-NN
@adr: ADR-NN
@sys: SYS-NN
@req: REQ-NN
@spec: SPEC-NN
@tasks: TASKS-NN
@icon: ICON-01:ValidationProtocol
@icon-role: provider
```

---

## 1. Executive Summary

This ICON defines the ValidationProtocol interface for validating data records against configurable rules. It enables parallel development by allowing consumers to code against the protocol type while providers implement the concrete validation logic.

### 1.1 Scope

**Purpose**: Enable type-safe data validation across multiple services
**Boundary**: Validation rules, result structures; excludes persistence
**Complexity**: 2 (moderate interface, simple state)

---

## 2. Contract Definition

### 2.1 Contract Type

**Type**: Protocol Interface

**Rationale**: Multiple services (3+ consumers) require validation; protocol enables mock implementations for parallel testing.

### 2.2 Interface Specification

```python
from typing import Protocol, List, Optional
from dataclasses import dataclass
from enum import Enum

class ValidationResult(str, Enum):
    """Validation outcome enumeration."""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"

@dataclass(frozen=True)
class Violation:
    """Immutable validation violation record."""
    rule_id: str
    field: str
    message: str
    severity: str = "error"

@dataclass(frozen=True)
class ValidationResponse:
    """Immutable validation response."""
    request_id: str
    result: ValidationResult
    violations: tuple[Violation, ...]

    @property
    def passed(self) -> bool:
        return self.result == ValidationResult.PASS

class ValidationProtocol(Protocol):
    """Protocol for data validation services."""

    async def validate(
        self,
        request_id: str,
        record: dict,
        rules: List[str]
    ) -> ValidationResponse:
        """
        Validate a record against specified rules.

        Args:
            request_id: Unique request identifier
            record: Data record to validate
            rules: List of rule identifiers to apply

        Returns:
            ValidationResponse with result and any violations

        Raises:
            ValidationConfigError: Invalid rule specification
            ValidationTimeoutError: Validation exceeded timeout
        """
        ...

    def get_available_rules(self) -> List[str]:
        """Return list of available validation rule identifiers."""
        ...

    @property
    def rule_count(self) -> int:
        """Number of configured validation rules."""
        ...
```

---

## 3. Provider Requirements

### 3.1 Implementation Obligations

**Provider TASKS**: TASKS-NN (Validation Service Implementation)

**Requirements**:
- [ ] Implement all protocol methods with matching signatures
- [ ] Honor immutability of dataclass returns
- [ ] Raise specified exceptions with proper error codes
- [ ] Pass `mypy --strict` type checking
- [ ] Achieve 95% unit test coverage

### 3.2 Validation Criteria

```bash
# Type checking
mypy --strict src/services/validation_service.py

# Protocol compliance test
pytest tests/unit/test_validation_protocol.py -v
```

---

## 4. Consumer Requirements

### 4.1 Usage Obligations

**Consumer TASKS**: TASKS-NN, TASKS-NN, TASKS-NN

**Requirements**:
- [ ] Import protocol type, not implementation
- [ ] Type hint all ValidationProtocol references
- [ ] Handle ValidationConfigError and ValidationTimeoutError
- [ ] Pass `mypy --strict` type checking
- [ ] Include integration tests with mock implementations

### 4.2 Import Pattern

```python
# Correct: Import protocol type
from validation.protocols import ValidationProtocol, ValidationResponse

# Incorrect: Don't import implementation
# from validation.services import ValidationService  # NO
```

---

## 5. Exception Hierarchy

```python
class ValidationError(Exception):
    """Base exception for validation operations."""
    error_code: str = "VALIDATION_ERROR"

class ValidationConfigError(ValidationError):
    """Invalid validation configuration or rules."""
    error_code: str = "CONFIG_ERROR"

class ValidationTimeoutError(ValidationError):
    """Validation operation exceeded timeout."""
    error_code: str = "TIMEOUT_ERROR"
```

---

## 6. Mock Implementation Template

```python
from typing import List

class MockValidationService:
    """Mock implementation for consumer testing."""

    def __init__(self, should_pass: bool = True):
        self._should_pass = should_pass
        self._rules = ["required", "format", "range"]

    async def validate(
        self,
        request_id: str,
        record: dict,
        rules: List[str]
    ) -> ValidationResponse:
        if self._should_pass:
            return ValidationResponse(
                request_id=request_id,
                result=ValidationResult.PASS,
                violations=()
            )
        return ValidationResponse(
            request_id=request_id,
            result=ValidationResult.FAIL,
            violations=(Violation("mock", "field", "Mock failure"),)
        )

    def get_available_rules(self) -> List[str]:
        return self._rules.copy()

    @property
    def rule_count(self) -> int:
        return len(self._rules)
```

---

## 7. Integration Checklist

- [ ] Provider TASKS-NN updated with `@icon: ICON-01:ValidationProtocol` in section 8.1
- [ ] Consumer TASKS files updated with `@icon-role: consumer` in section 8.2
- [ ] ICON/README.md active contracts table updated
- [ ] `consumer_count` in frontmatter matches grep verification
- [ ] All mypy checks passing

---

**Example Usage**: This example demonstrates a Protocol Interface ICON. Replace all `NN` placeholders with actual document IDs.

---

**Document Control**:
- **Version**: 1.0
- **Last Updated**: 2025-11-13
- **Template Reference**: ICON-TEMPLATE.md
