# =============================================================================
# 📋 Document Authority: This is the PRIMARY STANDARD for ICON structure.
# All other documents (Schema, Creation Rules, Validation Rules) DERIVE from this template.
# - In case of conflict, this template is the single source of truth
# - Schema: ICON_SCHEMA.yaml - Machine-readable validation (derivative)
# - Creation Rules: ICON_CREATION_RULES.md - AI guidance for document creation (derivative)
# - Validation Rules: ICON_VALIDATION_RULES.md - AI checklist after document creation (derivative)
#   NOTE: VALIDATION_RULES includes all CREATION_RULES and may be extended for validation
# =============================================================================
---
title: "ICON-NNN: [Contract Name]"
tags:
  - implementation-contract
  - layer-11-artifact
  - shared-architecture
  - contract-template
custom_fields:
  document_type: implementation_contract
  artifact_type: ICON
  layer: 11
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: draft
  contract_type: [protocol|exception|state-machine|data-model|di-interface]
  provider_tasks: TASKS-XXX
  consumer_count: N
  providers: []
  consumers: []
---

<!-- ⚠️ CRITICAL WARNINGS - READ BEFORE CREATION ⚠️ -->
<!--
ICON creation is an 8-file atomic operation:
1. Create ICON-XXX.md (this file)
2. Update provider TASKS-XXX.md section 8.1 with @icon tag
3. Update N consumer TASKS-YYY.md section 8.2 with @icon tags
4. Update docs/ICON/README.md active contracts table
5. Update consumer_count in this file's frontmatter (must match grep)
6. Run scripts/preflight_icon_creation.sh
7. Run scripts/validate_icon_complete.sh
8. Only then mark development_status: active

FAILURE TO COMPLETE ALL 8 STEPS = ORPHANED CONTRACT
See ICON_INTEGRATION_WORKFLOW.md for detailed procedure.
-->

# ICON-NNN: [Contract Name]

## 1. Pre-Creation Checklist

Before creating this ICON, verify:

- [ ] Provider TASKS file exists with complete section 8.1
- [ ] All N consumer TASKS identified with grep verification
- [ ] Consumer count calculated: `grep -r "@icon: ICON-XXX" docs/TASKS/ | wc -l`
- [ ] No self-reference (provider TASKS not in consumer list)
- [ ] Contract type selected (Protocol/Exception/State/Model/DI)
- [ ] Performance requirements defined (if applicable)
- [ ] Exception hierarchy designed (if applicable)
- [ ] Mock implementation template ready

**If any item fails, STOP. Fix TASKS files first.**

**⚠️ NOTE**: Most implementation contracts should be embedded in TASKS files. Use standalone ICON files only when:
- 5+ consumer TASKS files
- Contract definition >500 lines
- Platform-level shared interfaces
- Contracts used across multiple projects

## Document Control

| Item | Details |
|------|---------|
| **Status** | Draft/Active/Deprecated |
| **Version** | [Semantic version, e.g., 1.0.0] |
| **Date Created** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD |
| **Author** | [Developer/AI Assistant/Team Name] |
| **Contract Type** | Protocol/Exception/State Machine/Data Model/DI Interface |
| **Providers** | [TASKS-IDs implementing this contract] |
| **Consumers** | [TASKS-IDs depending on this contract] |

## 2. Integration Workflow

See [ICON_INTEGRATION_WORKFLOW.md](./ICON_INTEGRATION_WORKFLOW.md) for:
- Pre-creation validation procedure
- 8-file atomic operation steps
- Post-creation validation gates
- Error recovery procedures

**Required Phases**:
1. Pre-Flight Validation (script-based)
2. Contract Creation (this file)
3. Provider TASKS Update (section 8.1)
4. Consumer TASKS Updates (section 8.2 × N)
5. README Update (active contracts table)
6. Post-Flight Validation (script-based)

---

> **⚠️ UPSTREAM ARTIFACT REQUIREMENT**: Before completing traceability tags:
> 1. **Check existing artifacts**: List what upstream documents actually exist in `docs/`
> 2. **Reference only existing documents**: Use actual document IDs, not placeholders
> 3. **Use `null` appropriately**: Only when upstream artifact type genuinely doesn't exist for this feature
> 4. **Do NOT create phantom references**: Never reference documents that don't exist
> 5. **Do NOT create missing upstream artifacts**: If upstream artifacts are missing, skip that functionality. Only create functionality for existing upstream artifacts.



## 3. Executive Summary

[2-3 sentence overview of what this contract defines, why it exists as a standalone file, and its role in coordinating parallel development]

### 3.1 Scope

**Purpose**: [What this contract enables]
**Boundary**: [What is included/excluded]
**Complexity**: [1-5 scale]

---

## 1. Contract Definition

### 1.1 Contract Type

**Type**: [Protocol Interface | Exception Hierarchy | State Machine | Data Model | DI Interface]

**Rationale**: [Why this contract type was chosen]

### 1.2 Interface Specification

[Complete type-safe contract definition with code examples]

**Example**:
```python
from typing import Protocol, Optional
from enum import Enum

class ConnectionState(str, Enum):
    """Connection state enumeration."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    FAILED = "failed"

class GatewayConnector(Protocol):
    """Protocol for gateway connection services."""

    async def connect(
        self,
        host: str,
        port: int,
        client_id: int,
        timeout: float = 30.0
    ) -> None:
        """
        Establish connection to gateway.

        Args:
            host: Gateway hostname
            port: Gateway port
            client_id: Unique client identifier
            timeout: Connection timeout in seconds

        Raises:
            GatewayConnectionError: Connection failed
            ClientIDInUseError: Client ID already connected
            TimeoutError: Connection timeout exceeded
        """
        ...

    async def disconnect(self) -> None:
        """Graceful disconnection from gateway."""
        ...

    @property
    def state(self) -> ConnectionState:
        """Current connection state."""
        ...

    @property
    def is_connected(self) -> bool:
        """Connection status indicator."""
        ...
```

---

## 2. Provider Requirements

### 2.1 Implementation Obligations

**Provider TASKS**: [List of TASKS-IDs that must implement this contract]

**Requirements**:
- [ ] Implement all protocol methods
- [ ] Honor all type signatures
- [ ] Raise specified exceptions
- [ ] Pass mypy type checking
- [ ] Include unit tests for contract compliance

### 2.2 Validation Criteria

**Type Checking**:
```bash
mypy --strict src/services/gateway_connector.py
```

**Runtime Validation**:
```python
from typing import runtime_checkable

@runtime_checkable
class GatewayConnector(Protocol):
    ...

# Validate implementation
assert isinstance(implementation, GatewayConnector)
```

---

## 3. Consumer Requirements

### 3.1 Usage Obligations

**Consumer TASKS**: [List of TASKS-IDs that depend on this contract]

**Requirements**:
- [ ] Import protocol type only (not implementation)
- [ ] Type hint all protocol references
- [ ] Handle all specified exceptions
- [ ] Pass mypy type checking
- [ ] Include integration tests

### 3.2 Dependency Management

**Import Pattern**:
```python
from typing import Protocol
from contracts.gateway import GatewayConnector, ConnectionState

class MarketDataService:
    """Market data service depending on GatewayConnector."""

    def __init__(self, connector: GatewayConnector):
        self._connector = connector

    async def subscribe_quotes(self, symbol: str) -> None:
        if not self._connector.is_connected:
            await self._connector.connect("localhost", 7497, 1)
        # ... subscription logic
```

---

## 4. Change Management

### 4.1 Versioning Strategy

**Semantic Versioning**:
- **Major**: Breaking changes (remove methods, change signatures)
- **Minor**: Backward-compatible additions (new optional parameters)
- **Patch**: Documentation updates, clarifications

### 4.2 Breaking Change Protocol

**Process**:
1. Create new contract version (ICON-NNN v2.0.0)
2. Notify all consumer TASKS owners
3. Provide migration guide
4. Maintain old version until all consumers migrate
5. Deprecate old version (6-month sunset period)

### 4.3 Change History

| Version | Date | Changes | Impact |
|---------|------|---------|--------|
| 1.0.0 | YYYY-MM-DD | Initial contract definition | N/A |

---

## 5. Testing Requirements

### 5.1 Provider Tests

**Contract Compliance**:
```python
import pytest
from typing import get_type_hints
from contracts.gateway import GatewayConnector

def test_protocol_compliance():
    """Verify implementation matches protocol."""
    from services.gateway_connector import RealGatewayConnector

    # Runtime check
    assert isinstance(RealGatewayConnector(), GatewayConnector)

    # Method signature validation
    hints = get_type_hints(RealGatewayConnector.connect)
    assert 'host' in hints
    assert 'port' in hints
    assert 'client_id' in hints
```

### 5.2 Consumer Tests

**Integration Tests**:
```python
import pytest
from unittest.mock import Mock
from contracts.gateway import GatewayConnector, ConnectionState

@pytest.fixture
def mock_connector():
    """Mock connector for testing."""
    connector = Mock(spec=GatewayConnector)
    connector.is_connected = False
    connector.state = ConnectionState.DISCONNECTED
    return connector

def test_external_data_service_with_mock(mock_connector):
    """Test market data service with mocked connector."""
    service = MarketDataService(mock_connector)
    # ... test logic
```

---

## 6. Documentation

### 6.1 Usage Examples

[Comprehensive examples for providers and consumers]

### 6.2 Common Patterns

[Best practices and common usage patterns]

### 6.3 Anti-Patterns

[What NOT to do - common mistakes to avoid]

---

## 7. Traceability

### 7.1 Upstream Artifacts

**Source Requirements**:
```markdown
@spec: SPEC-NNN:interface-spec
@req: REQ-NNN:interface-requirement
@adr: ADR-NNN
```

### 7.2 Provider/Consumer Tags

**This Contract**:
```markdown
@icon: ICON-NNN:ContractName
```

**Provider TASKS**:
```markdown
@icon: ICON-NNN:ContractName
@icon-role: provider
```

**Consumer TASKS**:
```markdown
@icon: ICON-NNN:ContractName
@icon-role: consumer
```

---

## 8. References

### 8.1 Internal Documentation
- [IMPLEMENTATION_CONTRACTS_GUIDE.md](../TASKS/IMPLEMENTATION_CONTRACTS_GUIDE.md)
- [TASKS-TEMPLATE.md](../TASKS/TASKS-TEMPLATE.md)
- [TRACEABILITY.md](../TRACEABILITY.md)

### 8.2 Related Contracts
- [List related ICON files]

### 8.3 Provider TASKS
- TASKS-NNN: [Description]

### 8.4 Consumer TASKS
- TASKS-NNN: [Description]

---

## 9. Validation Gates

### 9.1 Pre-Activation Validation

**Before marking development_status: active**:

```bash
# Run validation scripts
./scripts/preflight_icon_creation.sh ICON-XXX TASKS-XXX
./scripts/validate_icon_complete.sh ICON-XXX

# Verify output shows:
# ✓ Provider TASKS has section 8.1 with @icon tag
# ✓ Consumer count matches grep results (N consumers)
# ✓ Bidirectional @icon tags present
# ✓ YAML frontmatter complete
# ✓ All 10 contract sections present
```

**If any check fails**: See ICON_ERROR_RECOVERY.md

---

## 10. Document Metadata

**Version**: 1.0.0
**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD
**Contract Type**: [Protocol/Exception/State Machine/Data Model/DI Interface]
**Providers**: [Count]
**Consumers**: [Count]
**Complexity**: [1-5]/5
**Token Count**: [Estimate]
