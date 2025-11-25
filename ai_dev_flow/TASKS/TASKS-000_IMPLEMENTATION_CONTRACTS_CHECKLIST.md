---
title: "TASKS-000: Implementation Contracts Quick Reference Checklist"
tags:
  - tasks-checklist
  - layer-11-artifact
  - shared-architecture
  - quality-assurance
custom_fields:
  document_type: checklist
  artifact_type: TASKS
  layer: 11
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
---

# TASKS-000: Implementation Contracts Quick Reference Checklist

## Purpose

Quick reference guide for determining when to create integration contracts, selecting contract types, and validating contract implementations. Use this checklist before implementing any TASKS file with dependencies.

**Complexity**: 2/5 (straightforward decision process)

**Reference**: See [INTEGRATION_CONTRACTS_GUIDE.md](./INTEGRATION_CONTRACTS_GUIDE.md) for detailed documentation.

---

## 1. When to Create Implementation Contracts

### Decision Matrix

Use this matrix to determine if integration contracts are required:

| Criterion | Threshold | Your TASKS | Create Contracts? |
|-----------|-----------|------------|-------------------|
| Downstream dependencies | ≥3 TASKS | [ ] Count: ___ | Yes if ≥3 |
| Implementation sessions | ≥2 sessions | [ ] Sessions: ___ | Yes if ≥2 |
| State machine complexity | ≥4 states | [ ] States: ___ | Yes if ≥4 |
| Exception types | ≥3 types | [ ] Types: ___ | Yes if ≥3 |
| Parallel development need | Required | [ ] Yes [ ] No | Yes if checked |

**Decision**: [ ] Create contracts [ ] Skip contracts

### Triggers (Create Contracts If...)

- [ ] **3+ downstream TASKS** depend on this interface
- [ ] **Shared interfaces** used across 2+ implementation sessions
- [ ] **Complex state machines** with 4+ states
- [ ] **Exception hierarchies** with 3+ exception types
- [ ] **Parallel development** required (dependencies can't wait)
- [ ] **Type safety** enforcement needed at boundaries
- [ ] **External integration** with strict contract requirements

### Skip Contracts If...

- [x] **Single downstream** dependency only
- [x] **Internal details** not shared across TASKS
- [x] **Temporary** or experimental interfaces
- [x] **Simple structures** (1-2 fields, no complex logic)
- [x] **Rapid prototyping** phase (can add contracts later)

---

## 2. Contract Type Selection

### Contract Types & Use Cases

Select contract type(s) based on what you're sharing:

#### Protocol Interfaces ✓ Use When:
- [ ] Defining async/sync service interfaces
- [ ] Creating plugin architectures
- [ ] Implementing adapter patterns
- [ ] Sharing service boundaries between TASKS

**Example**: `IBGatewayConnector` protocol with `connect()`, `disconnect()` methods

#### Exception Hierarchies ✓ Use When:
- [ ] Defining service failure modes
- [ ] Implementing retry logic
- [ ] Standardizing error codes
- [ ] Sharing error handling across TASKS

**Example**: `GatewayConnectionError` hierarchy with error codes and retry flags

#### State Machine Contracts ✓ Use When:
- [ ] Managing connection lifecycles
- [ ] Tracking order/workflow states
- [ ] Validating state transitions
- [ ] Sharing state logic across TASKS

**Example**: `ConnectionState` enum with valid transition mappings

#### Data Models ✓ Use When:
- [ ] Defining API request/response schemas
- [ ] Sharing configuration structures
- [ ] Creating database models
- [ ] Validating data between TASKS

**Example**: `ConnectionConfig` Pydantic model with validation rules

#### Dependency Injection Interfaces ✓ Use When:
- [ ] Implementing service registration
- [ ] Enabling testing with mocks
- [ ] Creating plugin architectures
- [ ] Sharing abstract interfaces

**Example**: `ClientIDValidator` ABC for DI container

---

## 3. Contract Creation Process

### 5-Step Workflow

#### Step 1: Dependency Analysis ✓
- [ ] Review TASKS file for dependencies
- [ ] Count downstream TASKS (how many depend on this?)
- [ ] Identify shared interfaces
- [ ] Document in "Implementation Contracts" section

**Output**: List of upstream/downstream dependencies

#### Step 2: Contract Type Selection ✓
- [ ] Review 5 contract types above
- [ ] Select types matching your interfaces
- [ ] Combine multiple types if needed
- [ ] Document selection rationale

**Output**: Selected contract types with justification

#### Step 3: Contract Implementation ✓
- [ ] Write contract code with full type hints
- [ ] Add docstrings for all public methods
- [ ] Define exception hierarchies
- [ ] Specify validation rules
- [ ] Create state transition mappings

**Output**: Contract code ready for validation

#### Step 4: Contract Documentation ✓
- [ ] Add "Implementation Contracts" section to TASKS
- [ ] Document contract purpose and scope
- [ ] Provide usage examples
- [ ] List consuming TASKS files
- [ ] Create mock implementations

**Output**: Complete contract documentation

#### Step 5: Validation ✓
- [ ] Run `mypy --strict` on contracts
- [ ] Verify all type hints present
- [ ] Test with mock implementations
- [ ] Review with architecture team
- [ ] Notify downstream consumers

**Output**: Validated, distribution-ready contracts

---

## 4. Contract Templates

### Template 1: Protocol Interface

```python
from typing import Protocol

class YourServiceInterface(Protocol):
    """Brief description of service interface."""

    async def method_name(
        self,
        param1: str,
        param2: int,
        param3: float = 10.0
    ) -> ReturnType:
        """
        Method description.

        Args:
            param1: Description
            param2: Description
            param3: Description (default: 10.0)

        Returns:
            Description of return value

        Raises:
            ExceptionType1: When error condition occurs
            ExceptionType2: When other error occurs
        """
        ...

    @property
    def property_name(self) -> PropertyType:
        """Property description."""
        ...
```

### Template 2: Exception Hierarchy

```python
from enum import Enum
from typing import Optional

class ErrorCode(str, Enum):
    """Error codes for exception types."""
    ERROR_TYPE_1 = "E001"
    ERROR_TYPE_2 = "E002"
    ERROR_TYPE_3 = "E003"

class BaseServiceError(Exception):
    """Base exception for service failures."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        retryable: bool = False,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.error_code = error_code
        self.retryable = retryable
        self.original_error = original_error

class SpecificError(BaseServiceError):
    """Specific error condition."""

    def __init__(self, context_param: str):
        super().__init__(
            f"Error message with {context_param}",
            ErrorCode.ERROR_TYPE_1,
            retryable=True
        )
        self.context_param = context_param
```

### Template 3: State Machine

```python
from enum import Enum
from typing import Dict, Set

class ServiceState(str, Enum):
    """Service state enumeration."""
    STATE_1 = "state_1"
    STATE_2 = "state_2"
    STATE_3 = "state_3"
    STATE_4 = "state_4"

# Valid state transitions
VALID_TRANSITIONS: Dict[ServiceState, Set[ServiceState]] = {
    ServiceState.STATE_1: {ServiceState.STATE_2},
    ServiceState.STATE_2: {ServiceState.STATE_3, ServiceState.STATE_4},
    ServiceState.STATE_3: {ServiceState.STATE_1},
    ServiceState.STATE_4: {ServiceState.STATE_1}
}

def is_valid_transition(
    current: ServiceState,
    next_state: ServiceState
) -> bool:
    """Validate state transition is allowed."""
    return next_state in VALID_TRANSITIONS.get(current, set())
```

### Template 4: Data Model (Pydantic)

```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class ServiceConfig(BaseModel):
    """Service configuration model."""

    field1: str = Field(..., min_length=1, max_length=255)
    field2: int = Field(..., ge=1, le=100)
    field3: float = Field(10.0, gt=0, le=1000)
    optional_field: Optional[str] = None

    @validator("field1")
    def validate_field1(cls, v: str) -> str:
        """Validate field1 is not empty."""
        if not v.strip():
            raise ValueError("field1 cannot be empty")
        return v.strip()

    class Config:
        frozen = True  # Immutable after creation
```

---

## 5. Validation Checklist

### Pre-Distribution Validation

**Type Safety**:
- [ ] All methods have type hints for parameters
- [ ] All methods have return type hints
- [ ] All properties have type hints
- [ ] Optional types explicitly marked with `Optional[T]`
- [ ] No `Any` types used (use specific types)

**Documentation**:
- [ ] All classes have docstrings
- [ ] All methods have docstrings
- [ ] All parameters documented in docstrings
- [ ] All return values documented
- [ ] All exceptions documented
- [ ] Usage examples provided

**Exception Handling**:
- [ ] Error codes defined in enum
- [ ] Retryable flag correctly set
- [ ] Original error preserved
- [ ] Exception hierarchy complete

**State Machines**:
- [ ] All states enumerated
- [ ] Valid transitions defined
- [ ] No orphaned states
- [ ] Terminal states identified
- [ ] Transition validation function provided

**Data Models**:
- [ ] All fields have type annotations
- [ ] Constraints defined (min/max, regex)
- [ ] Validators for business rules
- [ ] Immutability specified where appropriate
- [ ] Default values provided where appropriate

**Testing**:
- [ ] `mypy --strict` passes
- [ ] Mock implementations created
- [ ] Usage examples tested
- [ ] Edge cases documented

**Distribution**:
- [ ] Contract added to TASKS "Implementation Contracts" section
- [ ] Downstream consumers notified
- [ ] Contract location documented
- [ ] Version number assigned (1.0.0)

### Post-Distribution Validation

**Integration**:
- [ ] Consuming TASKS validated contracts
- [ ] Integration tests pass with mocks
- [ ] No interface mismatches reported
- [ ] Performance acceptable

**Documentation**:
- [ ] Contract documentation reviewed
- [ ] Usage examples verified by consumers
- [ ] All questions from consumers answered
- [ ] Documentation updated based on feedback

**Versioning**:
- [ ] Semantic versioning established (MAJOR.MINOR.PATCH)
- [ ] Breaking changes process defined
- [ ] Deprecation process documented
- [ ] Change log created

---

## 6. Common Pitfalls

### Pitfall 1: Over-Specification ❌
**Problem**: Including implementation details in contracts

**Example** (incorrect):
```python
class ServiceInterface(Protocol):
    def public_method(self) -> None: ...
    def _private_helper(self) -> None: ...  # Don't include!
```

**Solution**: Contracts define public interface only ✓

### Pitfall 2: Missing Type Hints ❌
**Problem**: Incomplete type annotations

**Example** (incorrect):
```python
def connect(self, host, port):  # No type hints
    ...
```

**Solution**: Add complete type hints ✓
```python
def connect(self, host: str, port: int) -> None:
    ...
```

### Pitfall 3: Mutable Contracts ❌
**Problem**: Changing contracts frequently breaks consumers

**Solution**: Use semantic versioning and deprecation ✓
- Version contracts (v1, v2)
- Deprecate old versions gradually
- Communicate breaking changes

### Pitfall 4: No Validation ❌
**Problem**: Contracts not validated with type checkers

**Solution**: Run `mypy --strict` on all contracts ✓
```bash
mypy --strict contracts/your_contracts.py
```

### Pitfall 5: Insufficient Documentation ❌
**Problem**: Contracts lack usage examples or error conditions

**Solution**: Document thoroughly ✓
- Purpose and scope
- Usage examples
- Exception conditions
- Consumer list

---

## 7. ROI Quick Reference

### Quantified Benefits (from TASKS-001 analysis)

**Development Speed**:
- Sequential: 11.5 weeks
- Parallel with contracts: 4 weeks
- **Improvement**: 65% faster

**Integration Bugs**:
- Pre-contract: 23 bugs
- Post-contract: 2 bugs
- **Reduction**: 90% fewer bugs

**Rework**:
- Pre-contract: 48 hours
- Post-contract: 6 hours
- **Reduction**: 87% less rework

**Investment vs. Return**:
- Contract creation: 4 hours per TASKS
- Savings: 26 hours per TASKS
- **ROI**: 550% return

### When ROI Is Highest

- [ ] **High dependency count**: 5+ downstream TASKS
- [ ] **Long implementation time**: 2+ weeks per TASKS
- [ ] **Complex interfaces**: Many methods/parameters
- [ ] **High integration risk**: Historical integration bugs
- [ ] **Team distribution**: Multiple teams/locations
- [ ] **Parallel urgency**: Critical path optimization needed

---

## 8. Quick Start Guide

### Minimal Contract Creation (15 minutes)

**Step 1** (5 min): Analyze dependencies
```bash
# Count downstream TASKS
grep -r "TASKS-YOUR-ID" ../TASKS/*.md | wc -l
```

**Step 2** (2 min): Select contract type
- Service interface → Protocol
- Errors → Exception Hierarchy
- States → State Machine
- Config → Data Model

**Step 3** (5 min): Write contract
```python
# Use templates from Section 4 above
# Add type hints to all methods
# Document all parameters
```

**Step 4** (2 min): Validate
```bash
mypy --strict your_contracts.py
```

**Step 5** (1 min): Document in TASKS
```markdown
## Implementation Contracts

### Contract 1: YourInterface
**Type**: Protocol
**Consumers**: 3 TASKS
[Contract code here]
```

---

## 9. Validation Commands

### Type Checking

```bash
# Validate single contract file
mypy --strict contracts/your_contracts.py

# Validate all contracts
mypy --strict contracts/*.py

# Validate with specific Python version
mypy --strict --python-version 3.11 contracts/*.py
```

### Runtime Validation

```python
# Protocol checking (runtime)
from typing import runtime_checkable, Protocol

@runtime_checkable
class YourInterface(Protocol):
    ...

# Validate implementation
assert isinstance(implementation, YourInterface)
```

### Pydantic Validation

```python
# Data model validation
from pydantic import ValidationError

try:
    config = YourConfig(**data)
except ValidationError as e:
    print(e.json())
```

---

## 10. @icon Tag Quick Reference

### Tag Format

**Primary**:
```yaml
@icon: TASKS-XXX:ContractName
```

**With Role**:
```yaml
@icon: TASKS-001:IBGatewayConnector
@icon-role: provider
```

### Role Types
- `provider` - Implements the contract
- `consumer` - Depends on the contract
- (no role) - Reference only

### Usage Examples

**Provider** (in TASKS-001):
```markdown
## 8. Implementation Contracts
@icon: TASKS-001:IBGatewayConnector
@icon-role: provider
```

**Consumer** (in TASKS-002):
```markdown
## 3. Dependencies
@icon: TASKS-001:IBGatewayConnector
@icon-role: consumer
```

**Code Comment**:
```python
# @icon: TASKS-001:IBGatewayConnector
# @icon-role: provider
class IBGatewayConnector(Protocol):
    ...
```

### Relationship to Other Tags
- `@ctr:` - Layer 9 external API contracts
- `@icon:` - Layer 11 internal implementation contracts
- `@iplan:` - Layer 12 implementation plans

---

## 11. ICON File Decision (Optional)

**Default**: Embed contracts in TASKS files

**Use Standalone ICON Files When** (ALL must be met):
- [ ] 5+ consumer TASKS files
- [ ] Contract definition >500 lines
- [ ] Platform-level shared interface
- [ ] Cross-project usage

**ICON Resources**:
- [ICON Directory README](../ICON/README.md)
- [ICON_CREATION_RULES.md](../ICON/ICON_CREATION_RULES.md)
- [ICON-000_index.md](../ICON/ICON-000_index.md)
- [ICON-TEMPLATE.md](../ICON/ICON-TEMPLATE.md)

**Quick Decision**:
```
3 consumers, 200 lines → Embed in TASKS ✅
8 consumers, 600 lines, 3 projects → Create ICON ✅
```

---

## 12. Reference Links

### Internal Documentation
- [IMPLEMENTATION_CONTRACTS_GUIDE.md](./IMPLEMENTATION_CONTRACTS_GUIDE.md) - Comprehensive guide
- [TASKS-TEMPLATE.md](./TASKS-TEMPLATE.md) - TASKS template with contracts section
- [CLAUDE.md](/home/ya/.claude/CLAUDE.md) - Global instructions with contracts strategy

### External Resources
- [PEP 544: Protocols](https://peps.python.org/pep-0544/) - Structural subtyping
- [mypy Documentation](https://mypy.readthedocs.io/) - Type checking tool
- [Pydantic Documentation](https://docs.pydantic.dev/) - Data validation
- [Type Hints Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html) - Quick reference

---

## Document Metadata

**Version**: 1.1.0
**Created**: 2025-11-24
**Last Updated**: 2025-11-25
**Document Type**: Quick Reference Checklist
**Complexity**: 2/5
**Token Count**: ~3,500 tokens
