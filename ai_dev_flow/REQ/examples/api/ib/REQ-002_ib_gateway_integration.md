# REQ-002: Interactive Brokers Gateway Integration
@adr:[ADR-034](../../../ADR/ADR-034_ib_gateway_integration_architecture.md#ADR-034)
@PRD:[PRD-002](../../../../PRD/PRD-002_ib_gateway_integration.md)
@SYS:[SYS-002](../../../../SYS/SYS-002_ib_gateway_integration.md)
@EARS:[EARS-002](../../../../EARS/EARS-002_ib_gateway_integration.md)
@spec:[ib_gateway_service](../../../../SPEC/services/SPEC-002_ib_gateway_service.yaml)
@bdd:[BDD-002_ib_gateway_integration_requirements.feature:scenarios](../../../../BDD/BDD-002_ib_gateway_integration_requirements.feature#scenarios)

### Description
The system MUST integrate with Interactive Brokers Gateway via ib-async 2.0.1 Python library to provide real-time market data (quotes, greeks, option chains) and order execution (market, limit, stop orders). Connection setup, reconnection strategy, and failover behavior MUST adhere to external API integration requirements.

**Technical Requirements**:
- Python version: >=3.10 (ib-async 2.0.1 minimum requirement)
- IB Gateway/TWS version: >=1023 (API compatibility requirement)
- Library: `ib_async==2.0.1` (successor to ib-insync)
- Dependencies: `aeventkit>=2.1.0`, `nest_asyncio`

**Import Statement**:
```python
from ib_async import IB, Stock, Option, MarketOrder, LimitOrder
```

### Acceptance Criteria
- Establish connection to IB Gateway within 5 seconds; maintain persistent session with exponential backoff reconnects (1s, 2s, 4s, 8s, 16s, max 60s intervals).
- Provide real-time quotes and options-related data with <500ms latency; publish data to cache and streaming sink per architecture.
- Support ib-async 2.0.1 specific features:
  - `qualifyContractsAsync()` returns N results for N contracts (None for failures)
  - Custom `IBDefaults` configuration for empty price/size handling
  - Enhanced ticker data fields (timestamp, shortable, volumeRate3Min/5Min/10Min)
- Trigger failover to backup market data provider after configured retry thresholds or sustained staleness (>60s).

### Related ADRs
- [ADR-034](../../../ADR/ADR-034_ib_gateway_integration_architecture.md#ADR-034): Example [EXTERNAL_SERVICE_GATEWAY] Integration Architecture
- [ADR-006](../../../../../ADR/adr_interactive_brokers_api_gateway.md#ADR-006): Official [EXTERNAL_SERVICE_GATEWAY] Integration
- [ADR-026](../../../../../ADR/adr_market_data_failover_strategy.md#ADR-026): [EXTERNAL_DATA - e.g., customer data, sensor readings] Failover Strategy

### Source Requirements
- See summary and details in [External API Integration Requirements](../../../../../REQ/external_api_integration_requirements.md#20-interactive-brokers-gateway-requirements)

### Verification
- BDD: [BDD-002_ib_gateway_integration_requirements.feature](../../../../BDD/BDD-002_ib_gateway_integration_requirements.feature#scenarios)
- Spec: [SPEC-002_ib_gateway_service.yaml](../../../../SPEC/services/SPEC-002_ib_gateway_service.yaml)

## Traceability
- Upstream Sources: [PRD-002](../../../../PRD/PRD-002_ib_gateway_integration.md), [SYS-002](../../../../SYS/SYS-002_ib_gateway_integration.md), [EARS-002](../../../../EARS/EARS-002_ib_gateway_integration.md)
- Downstream Artifacts: [ADR-006](../../../../../ADR/adr_interactive_brokers_api_gateway.md#ADR-006), [BDD-002_ib_gateway_integration_requirements.feature](../../../../BDD/BDD-002_ib_gateway_integration_requirements.feature#scenarios), [SPEC-002_ib_gateway_service.yaml](../../../../SPEC/services/SPEC-002_ib_gateway_service.yaml)
- Anchors/IDs: `# REQ-002`
- Code Path(s): `option_strategy/integrations/ib_gateway_client.py`
