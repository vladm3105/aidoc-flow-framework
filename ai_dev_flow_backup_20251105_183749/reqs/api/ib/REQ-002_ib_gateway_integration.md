# REQ-002: Interactive Brokers Gateway Integration
@adr:[ADR-034](../../../adrs/ADR-034_ib_gateway_integration_architecture.md#ADR-034)
@prd:[PRD-002](../../../../prd/PRD-002_ib_gateway_integration.md)
@sys:[SYS-002](../../../../sys/SYS-002_ib_gateway_integration.md)
@ears:[EARS-002](../../../../ears/EARS-002_ib_gateway_integration.md)
@spec:[ib_gateway_service](../../../../specs/services/SPEC-002_ib_gateway_service.yaml)
@bdd:[BDD-002_ib_gateway_integration_requirements.feature:scenarios](../../../../bbds/BDD-002_ib_gateway_integration_requirements.feature#scenarios)

### Description
The system MUST integrate with Interactive Brokers via IB Gateway to provide real-time market data and trade execution. Connection setup, reconnection strategy, and failover behavior MUST adhere to external API integration requirements.

### Acceptance Criteria
- Establish connection to IB Gateway within 5 seconds; maintain persistent session with exponential backoff reconnects.
- Provide real-time quotes and options-related data; publish data to cache and streaming sink per architecture.
- Trigger failover to Alpha Vantage after configured retry thresholds or sustained staleness (>60s).

### Related ADRs
- [ADR-034](../../../adrs/ADR-034_ib_gateway_integration_architecture.md#ADR-034): Example IB Gateway Integration Architecture
- [ADR-006](../../../../../adrs/adr_interactive_brokers_api_gateway.md#ADR-006): Official IB Gateway Integration
- [ADR-026](../../../../../adrs/adr_market_data_failover_strategy.md#ADR-026): Market Data Failover Strategy

### Source Requirements
- See summary and details in [External API Integration Requirements](../../../../../reqs/external_api_integration_requirements.md#20-interactive-brokers-gateway-requirements)

### Verification
- BDD: [BDD-002_ib_gateway_integration_requirements.feature](../../../../bbds/BDD-002_ib_gateway_integration_requirements.feature#scenarios)
- Spec: [SPEC-002_ib_gateway_service.yaml](../../../../specs/services/SPEC-002_ib_gateway_service.yaml)

## Traceability
- Upstream Sources: [PRD-002](../../../../prd/PRD-002_ib_gateway_integration.md), [SYS-002](../../../../sys/SYS-002_ib_gateway_integration.md), [EARS-002](../../../../ears/EARS-002_ib_gateway_integration.md)
- Downstream Artifacts: [ADR-006](../../../../../adrs/adr_interactive_brokers_api_gateway.md#ADR-006), [BDD-002_ib_gateway_integration_requirements.feature](../../../../bbds/BDD-002_ib_gateway_integration_requirements.feature#scenarios), [SPEC-002_ib_gateway_service.yaml](../../../../specs/services/SPEC-002_ib_gateway_service.yaml)
- Anchors/IDs: `# REQ-002`
- Code Path(s): `option_strategy/integrations/ib_gateway_client.py`
