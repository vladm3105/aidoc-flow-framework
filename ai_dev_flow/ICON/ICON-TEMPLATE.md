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
  development_status: active
  contract_type: [protocol|exception|state-machine|data-model|di-interface]
  providers: []
  consumers: []
---

# ICON-NNN: [Contract Name]

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

## Executive Summary

[2-3 sentence overview of what this contract defines, why it exists as a standalone file, and its role in coordinating parallel development]

### Scope

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

def test_market_data_service_with_mock(mock_connector):
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

## Document Metadata

**Version**: 1.0.0
**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD
**Contract Type**: [Protocol/Exception/State Machine/Data Model/DI Interface]
**Providers**: [Count]
**Consumers**: [Count]
**Complexity**: [1-5]/5
**Token Count**: [Estimate]
