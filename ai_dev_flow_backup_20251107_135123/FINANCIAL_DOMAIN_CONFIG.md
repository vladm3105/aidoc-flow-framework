# Financial Services Domain Configuration

**Version**: 1.0
**Purpose**: Default domain configuration for financial services projects
**Domain**: Trading, Banking, Insurance, Portfolio Management, Risk Management
**Status**: Production
**Regulatory Scope**: SEC, FINRA, SOX, Basel III, PCI-DSS, GDPR/CCPA

---

## Overview

This configuration file provides complete customization for financial services projects within the AI Dev Flow framework. Use this as the **default domain** when no other domain is specified.

### Financial Services Scope

- **Trading Platforms**: Equities, options, futures, forex, cryptocurrency
- **Banking**: Retail banking, commercial banking, investment banking
- **Insurance**: Underwriting, claims processing, actuarial systems
- **Portfolio Management**: Asset allocation, rebalancing, performance attribution
- **Risk Management**: VaR, stress testing, position limits, P&L attribution
- **Compliance**: Regulatory reporting, audit trails, trade surveillance

---

## Placeholder Replacement Dictionary

### Core Terminology Mappings

| Placeholder | Financial Services Term | Context |
|-------------|-------------------------|---------|
| `[RESOURCE_COLLECTION]` | **Portfolio** | Collection of positions or assets |
| `[RESOURCE_ITEM]` | **Position** | Individual holding or trade |
| `[RESOURCE_ACTION]` | **Trade Execution** | Action performed on positions |
| `[EXTERNAL_DATA_PROVIDER]` | **Market Data Feed** | Bloomberg, Reuters, IEX, crypto exchanges |
| `[CALCULATION_ENGINE]` | **Greeks Calculator** | Option pricing, risk metrics, P&L |
| `[USER_ROLE]` | **Trader / Portfolio Manager** | Primary system users |
| `[TRANSACTION]` | **Trade** | Financial transaction |
| `[CONSTRAINT]` | **Position Limit** | Risk constraint or regulatory limit |
| `[REGULATORY_REQUIREMENT]` | **SEC Rule 15c3-5** | Specific regulation or control |
| `[DATA_STORE]` | **Trade Database** | Persistent storage system |
| `[EVENT]` | **Market Event** | Price update, order fill, market close |
| `[WORKFLOW]` | **Order Workflow** | Business process |
| `[METRIC]` | **P&L (Profit & Loss)** | Key performance indicator |
| `[ALERT]` | **Limit Breach Alert** | System notification |
| `[REPORT]` | **Risk Report** | Generated output |

### Extended Terminology

| Domain Concept | Financial Term | Alternative Terms |
|----------------|----------------|-------------------|
| Entity Identifier | **Symbol / Ticker** | CUSIP, ISIN, Bloomberg Ticker |
| Quantity | **Shares / Contracts / Notional** | Size, Volume, Exposure |
| Price | **Market Price / Fair Value** | Mid Price, Last Price, Mark |
| Timestamp | **Trade Timestamp** | Execution Time, Value Date |
| Status | **Order Status** | New, Filled, Canceled, Rejected |
| Category | **Asset Class** | Equity, Fixed Income, Derivative, Commodity |
| Organization Unit | **Desk / Strategy** | Trading desk, fund, account |
| Configuration | **Risk Parameters** | Limits, thresholds, tolerances |
| Validation | **Pre-Trade Check** | Risk check, compliance check |
| Approval | **Trade Approval** | Manager approval, compliance approval |

---

## AI Assistant Placeholder Replacement

### Automated Replacement Commands

When AI Assistant copies templates to project, execute these replacements:

```bash
# Core replacements
find docs/ -type f -name "*.md" -exec sed -i \
  -e 's/\[RESOURCE_COLLECTION\]/Portfolio/g' \
  -e 's/\[RESOURCE_ITEM\]/Position/g' \
  -e 's/\[RESOURCE_ACTION\]/Trade Execution/g' \
  -e 's/\[EXTERNAL_DATA_PROVIDER\]/Market Data Feed/g' \
  -e 's/\[CALCULATION_ENGINE\]/Greeks Calculator/g' \
  -e 's/\[USER_ROLE\]/Trader\/Portfolio Manager/g' \
  -e 's/\[TRANSACTION\]/Trade/g' \
  -e 's/\[CONSTRAINT\]/Position Limit/g' \
  -e 's/\[REGULATORY_REQUIREMENT\]/SEC Rule 15c3-5/g' \
  -e 's/\[DATA_STORE\]/Trade Database/g' \
  -e 's/\[EVENT\]/Market Event/g' \
  -e 's/\[WORKFLOW\]/Order Workflow/g' \
  -e 's/\[METRIC\]/P&L (Profit & Loss)/g' \
  -e 's/\[ALERT\]/Limit Breach Alert/g' \
  -e 's/\[REPORT\]/Risk Report/g' \
  {} +

# Extended replacements
find docs/ -type f -name "*.md" -exec sed -i \
  -e 's/\[ENTITY_ID\]/Symbol/g' \
  -e 's/\[QUANTITY\]/Shares/g' \
  -e 's/\[PRICE\]/Market Price/g' \
  -e 's/\[TIMESTAMP\]/Trade Timestamp/g' \
  -e 's/\[STATUS\]/Order Status/g' \
  -e 's/\[CATEGORY\]/Asset Class/g' \
  -e 's/\[ORG_UNIT\]/Trading Desk/g' \
  {} +
```

### YAML Specification Replacements

```bash
# Apply to YAML specs
find docs/specs/ -type f -name "*.yaml" -exec sed -i \
  -e 's/resource_collection/portfolio/g' \
  -e 's/resource_item/position/g' \
  -e 's/ResourceCollection/Portfolio/g' \
  -e 's/ResourceItem/Position/g' \
  {} +
```

---

## Regulatory Framework Mappings

### SEC (Securities and Exchange Commission)

| Regulation | Financial Services Application | Requirements Category |
|------------|--------------------------------|----------------------|
| **SEC Rule 15c3-5** | Market Access Risk Management | Pre-trade risk checks, position limits |
| **SEC Rule 606** | Order Routing Disclosure | Execution quality, routing transparency |
| **SEC Regulation SHO** | Short Sale Rules | Locate requirements, close-out obligations |
| **SEC Rule 17a-4** | Recordkeeping | Trade archive, WORM storage, audit trail |
| **Regulation Best Execution** | Execution Quality | Best price, speed, likelihood of execution |

**Traceability in Documents**:
```markdown
**Regulatory Requirement**: SEC Rule 15c3-5 (Market Access)
**Compliance Control**: REG-SEC-15c3-5-001
```

### FINRA (Financial Industry Regulatory Authority)

| Rule | Application | Requirements |
|------|-------------|--------------|
| **FINRA Rule 3110** | Supervision | Trade review, exception monitoring |
| **FINRA Rule 5210** | Publication of Transactions | Trade reporting to FINRA facilities |
| **FINRA Rule 4511** | Books and Records | Audit trail, trade blotters |
| **FINRA Rule 3310** | Anti-Money Laundering | Customer due diligence, suspicious activity |

### SOX (Sarbanes-Oxley Act)

| Section | Application | Requirements |
|---------|-------------|--------------|
| **SOX 404** | Internal Controls | IT general controls, segregation of duties |
| **SOX 302** | Financial Disclosures | Certification of financial data accuracy |
| **SOX 409** | Real-Time Disclosure | Material event reporting |

### Basel III (Banking)

| Requirement | Application | Implementation |
|-------------|-------------|----------------|
| **Capital Adequacy** | Risk-weighted assets | Capital calculation engines |
| **Liquidity Coverage Ratio (LCR)** | Liquidity risk | Cash flow projections |
| **Leverage Ratio** | Balance sheet limits | Exposure aggregation |

### PCI-DSS (Payment Card Industry)

| Requirement | Application | Implementation |
|-------------|-------------|----------------|
| **Requirement 3** | Protect Stored Cardholder Data | Encryption, tokenization |
| **Requirement 8** | Identify and Authenticate Access | MFA, access controls |
| **Requirement 10** | Track and Monitor Access | Audit logs, SIEM integration |

### GDPR/CCPA (Privacy)

| Requirement | Application | Implementation |
|-------------|-------------|----------------|
| **Right to Erasure** | Delete customer PII | Data deletion workflows |
| **Data Portability** | Export customer data | Data export APIs |
| **Breach Notification** | 72-hour notification | Incident response procedures |

---

## Financial Terminology Dictionary

### Asset Classes

| Term | Definition | Examples |
|------|------------|----------|
| **Equity** | Ownership stake in company | Common stock, preferred stock, ADR |
| **Fixed Income** | Debt instruments | Corporate bonds, government bonds, municipal bonds |
| **Derivative** | Contracts based on underlying | Options, futures, swaps, forwards |
| **Commodity** | Physical goods | Gold, oil, agricultural products |
| **Cryptocurrency** | Digital assets | Bitcoin, Ethereum, stablecoins |
| **Forex** | Foreign exchange | Currency pairs (EUR/USD, GBP/JPY) |

### Trading Terminology

| Term | Definition | Usage Context |
|------|------------|---------------|
| **Symbol/Ticker** | Unique identifier for security | AAPL, MSFT, SPY |
| **Position** | Holding in portfolio | Long 1000 shares AAPL @ $150.00 |
| **Order** | Instruction to trade | Buy 500 shares TSLA at market |
| **Execution** | Completion of trade | Filled 500 @ $245.30 |
| **Fill** | Portion of order executed | Partial fill: 300 of 500 shares |
| **Slippage** | Difference between expected and actual price | Ordered @ $100, filled @ $100.05 |
| **Side** | Buy or Sell | Long (buy), Short (sell) |
| **Quantity** | Number of shares/contracts | 1000 shares, 10 contracts |
| **Price** | Execution price or market price | Bid, Ask, Last, Mid |

### Risk Terminology

| Term | Definition | Formula/Context |
|------|------------|-----------------|
| **P&L (Profit & Loss)** | Gain or loss on positions | Realized P&L, Unrealized P&L |
| **Greeks** | Option sensitivities | Delta, Gamma, Vega, Theta, Rho |
| **VaR (Value at Risk)** | Maximum expected loss | 1-day 99% VaR = $1M |
| **Stress Test** | Scenario-based risk | Market crash scenario: -20% equities |
| **Position Limit** | Maximum allowed position | Hard limit: 10,000 shares per symbol |
| **Exposure** | Market risk amount | Gross exposure, net exposure |
| **Notional** | Contract value | Notional = Contracts × Multiplier × Price |
| **Duration** | Interest rate sensitivity | Modified duration, effective duration |
| **Beta** | Market correlation | Portfolio beta = 1.2 (20% more volatile than market) |

### Portfolio Management

| Term | Definition | Context |
|------|------------|---------|
| **Asset Allocation** | Distribution across asset classes | 60% equity, 30% bonds, 10% cash |
| **Rebalancing** | Restoring target allocation | Quarterly rebalancing to policy targets |
| **Benchmark** | Performance comparison | S&P 500, Russell 2000, Custom benchmark |
| **Alpha** | Excess return vs benchmark | Portfolio return - Benchmark return |
| **Tracking Error** | Deviation from benchmark | Standard deviation of excess returns |
| **Sharpe Ratio** | Risk-adjusted return | (Return - Risk-free rate) / Volatility |
| **Drawdown** | Peak-to-trough decline | Maximum drawdown: -15% from peak |

### Market Data

| Term | Definition | Source Examples |
|------|------------|-----------------|
| **Bid** | Highest buy price | Level 1 market data |
| **Ask** | Lowest sell price | Level 1 market data |
| **Last** | Most recent trade price | Ticker plant, exchange feed |
| **Volume** | Trading activity | Daily volume, average volume |
| **OHLC** | Open, High, Low, Close | Bar data, candlestick charts |
| **Tick** | Individual trade | Time & Sales data |
| **Level 2** | Order book depth | Bid/Ask sizes at multiple price levels |
| **Implied Volatility** | Market-implied volatility | Option chain data |

---

## Requirements Subdirectory Structure

### Financial-Specific Subdirectories

AI Assistant **MUST** create these subdirectories under `docs/reqs/`:

```bash
mkdir -p docs/reqs/risk/          # Risk management requirements
mkdir -p docs/reqs/risk/lim/      # Position limits
mkdir -p docs/reqs/risk/var/      # VaR calculations
mkdir -p docs/reqs/risk/stress/   # Stress testing

mkdir -p docs/reqs/trading/       # Trade execution requirements
mkdir -p docs/reqs/trading/ord/   # Order management
mkdir -p docs/reqs/trading/exec/  # Execution algorithms
mkdir -p docs/reqs/trading/rou/   # Order routing

mkdir -p docs/reqs/portfolio/     # Portfolio management
mkdir -p docs/reqs/portfolio/alloc/   # Asset allocation
mkdir -p docs/reqs/portfolio/rebal/   # Rebalancing
mkdir -p docs/reqs/portfolio/perf/    # Performance attribution

mkdir -p docs/reqs/compliance/    # Regulatory compliance
mkdir -p docs/reqs/compliance/sec/    # SEC rules
mkdir -p docs/reqs/compliance/finra/  # FINRA rules
mkdir -p docs/reqs/compliance/audit/  # Audit trails

mkdir -p docs/reqs/ml/            # ML model requirements
mkdir -p docs/reqs/ml/pricing/    # Pricing models
mkdir -p docs/reqs/ml/sentiment/  # Sentiment analysis
mkdir -p docs/reqs/ml/regime/     # Market regime detection
```

### Example Requirements Organization

```
docs/reqs/
├── risk/
│   ├── REQ-001_position_limit_enforcement.md
│   ├── REQ-002_var_calculation_methodology.md
│   ├── REQ-003_stress_test_scenarios.md
│   └── lim/
│       ├── REQ-010_hard_limit_implementation.md
│       └── REQ-011_soft_limit_warnings.md
├── trading/
│   ├── REQ-020_order_validation.md
│   ├── REQ-021_execution_algorithms.md
│   └── ord/
│       ├── REQ-030_order_types.md
│       └── REQ-031_order_lifecycle.md
├── portfolio/
│   ├── REQ-040_asset_allocation_engine.md
│   └── alloc/
│       └── REQ-050_rebalancing_triggers.md
├── compliance/
│   ├── REQ-060_trade_surveillance.md
│   └── sec/
│       └── REQ-070_rule_15c3-5_compliance.md
└── ml/
    ├── REQ-080_ml_model_requirements.md
    └── pricing/
        └── REQ-090_option_pricing_model.md
```

---

## Example Use Cases

### Use Case 1: Algorithmic Trading Platform

**Domain**: Financial Services - Trading
**Subdomain**: Equities, Options, Futures

**Placeholder Replacements**:
```
[RESOURCE_COLLECTION] → Trading Strategy
[RESOURCE_ITEM] → Order
[RESOURCE_ACTION] → Algorithm Execution
[EXTERNAL_DATA_PROVIDER] → Market Data Feed (IEX, Polygon)
[CALCULATION_ENGINE] → Signal Generator
[USER_ROLE] → Algo Trader
[TRANSACTION] → Order Execution
[CONSTRAINT] → Order Rate Limit
[REGULATORY_REQUIREMENT] → SEC Rule 15c3-5 (Market Access)
```

**Key Requirements**:
- REQ-001: Pre-trade risk checks (SEC 15c3-5)
- REQ-002: Order validation and routing
- REQ-003: Real-time market data ingestion
- REQ-004: Execution algorithm (TWAP, VWAP, POV)
- REQ-005: Post-trade TCA (Transaction Cost Analysis)

### Use Case 2: Portfolio Risk Management System

**Domain**: Financial Services - Risk Management
**Subdomain**: Multi-asset Portfolio

**Placeholder Replacements**:
```
[RESOURCE_COLLECTION] → Portfolio
[RESOURCE_ITEM] → Position
[RESOURCE_ACTION] → Risk Calculation
[EXTERNAL_DATA_PROVIDER] → Market Data & Reference Data
[CALCULATION_ENGINE] → VaR Engine
[USER_ROLE] → Risk Manager
[TRANSACTION] → Position Update
[CONSTRAINT] → VaR Limit
[REGULATORY_REQUIREMENT] → Basel III Capital Adequacy
```

**Key Requirements**:
- REQ-010: VaR calculation (historical, parametric, Monte Carlo)
- REQ-011: Stress testing engine
- REQ-012: Greeks calculation for options
- REQ-013: Position limit monitoring
- REQ-014: Risk report generation

### Use Case 3: Retail Banking Platform

**Domain**: Financial Services - Banking
**Subdomain**: Retail Banking

**Placeholder Replacements**:
```
[RESOURCE_COLLECTION] → Account Portfolio
[RESOURCE_ITEM] → Bank Account
[RESOURCE_ACTION] → Transaction Processing
[EXTERNAL_DATA_PROVIDER] → ACH Network / Card Network
[CALCULATION_ENGINE] → Interest Calculator
[USER_ROLE] → Customer / Banker
[TRANSACTION] → Fund Transfer
[CONSTRAINT] → Daily Transfer Limit
[REGULATORY_REQUIREMENT] → SOX 404 Internal Controls
```

**Key Requirements**:
- REQ-020: Account opening and KYC
- REQ-021: Fund transfer (ACH, wire, internal)
- REQ-022: Bill payment processing
- REQ-023: Interest calculation and accrual
- REQ-024: Overdraft management

---

## Document Examples

### Example REQ Document (Financial Services)

```markdown
# REQ-003: Position Limit Enforcement

<a id="REQ-003"></a>

## Document Control

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-003 |
| **Title** | Position Limit Enforcement |
| **Status** | Approved |
| **Priority** | Critical |
| **Version** | 1.2 |
| **Created** | 2024-12-15 |
| **Last Modified** | 2025-01-10 |

---

## 1. Context

### Purpose
Enforce position limits to manage market risk and comply with SEC Rule 15c3-5 (Market Access Risk Management).

### Background
Trading desks require real-time enforcement of position limits to prevent excessive risk exposure. Both hard limits (block trades) and soft limits (warnings) are needed.

### Use Case Scenarios
- **Scenario 1**: Trader attempts to buy 10,000 shares AAPL, current position is 9,500 shares, hard limit is 10,000 shares → Order rejected
- **Scenario 2**: Portfolio exposure reaches 90% of VaR limit → Soft limit warning sent to risk manager
- **Scenario 3**: End-of-day position exceeds limit due to mark-to-market → Limit breach alert generated

---

## 2. Functional Requirements

### Core Functionality

**REQ-003-F1**: System SHALL enforce hard position limits in real-time before order execution.

**REQ-003-F2**: System SHALL generate soft limit warnings when position approaches threshold (configurable, default 80% of limit).

**REQ-003-F3**: System SHALL support multiple limit types:
- Per-symbol position limits (shares/contracts)
- Per-asset-class notional limits (USD exposure)
- Per-strategy VaR limits (99% 1-day VaR)
- Sector exposure limits (percentage of NAV)

**REQ-003-F4**: System SHALL allow authorized users (Risk Manager, Compliance Officer) to override limits with justification and audit trail.

---

## 3. Acceptance Criteria

### Functional Acceptance Criteria

**AC-F1**: Hard Limit Enforcement
- Given position at hard limit
- When order would increase position
- Then order SHALL be rejected with reason "Position limit exceeded"
- And rejection SHALL be logged to audit trail

**AC-F2**: Soft Limit Warning
- Given position at 80% of limit (configurable)
- When position crosses soft threshold
- Then warning SHALL be sent to trader and risk manager
- And warning SHALL include current exposure and remaining capacity

**AC-F3**: Limit Types Support
- Given configured limits (symbol, asset class, strategy, sector)
- When pre-trade check executes
- Then all applicable limits SHALL be evaluated
- And most restrictive limit SHALL be enforced

**AC-F4**: Limit Override
- Given authorized user (Risk Manager role)
- When limit override requested with justification
- Then override SHALL be allowed with approval workflow
- And override SHALL be logged with user ID, timestamp, justification

### Error/Edge Case Criteria

**AC-E1**: Limit Configuration Error
- Given invalid limit configuration (negative value, missing symbol)
- Then configuration SHALL be rejected at setup
- And validation error SHALL be returned

**AC-E2**: Concurrent Order Race Condition
- Given two orders submitted simultaneously
- When both orders together exceed limit
- Then first order processed SHALL be accepted
- And second order SHALL be rejected if limit exceeded

**AC-E3**: Market Data Stale
- Given market data older than 60 seconds
- When limit check requires current price
- Then check SHALL use last known price with staleness flag
- And warning SHALL be logged

### Quality Acceptance Criteria

**AC-Q1**: Performance
- Limit check latency SHALL NOT exceed 10 milliseconds (P99)
- System SHALL support 10,000 limit checks per second

**AC-Q2**: Availability
- Limit enforcement SHALL have 99.99% uptime
- Degraded mode: Allow orders with warning if limit service unavailable

**AC-Q3**: Accuracy
- Limit calculations SHALL match risk system within 0.01% tolerance
- Position aggregation SHALL be real-time (sub-second latency)

### Data Validation Criteria

**AC-D1**: Limit Configuration Validation
- Limit values SHALL be positive numbers
- Percentage limits SHALL be between 0 and 100
- Symbol limits SHALL reference valid symbols from reference data

**AC-D2**: Position Calculation Validation
- Position aggregation SHALL include all orders (filled, pending)
- Position notional SHALL use real-time market prices
- Greeks calculation SHALL use current volatility surface

### Integration Criteria

**AC-I1**: Order Management System Integration
- Limit check SHALL be synchronous (blocking) in order workflow
- Order rejection SHALL include specific limit violated

**AC-I2**: Risk System Integration
- Position data SHALL sync from risk system every 5 seconds
- VaR limits SHALL be updated daily after risk run

**AC-I3**: Audit Trail Integration
- All limit events SHALL be logged to central audit system
- Log entries SHALL include: timestamp, user, symbol, limit type, breach/warning details

---

## 4. Business Value

### Primary Benefits
- **Risk Reduction**: Prevent excessive exposure and potential losses
- **Regulatory Compliance**: Meet SEC Rule 15c3-5 requirements
- **Operational Efficiency**: Automated limit enforcement reduces manual review

### Quantitative Impact
- Estimated risk reduction: 30% decrease in limit breaches
- Compliance cost avoidance: $500K annual fine risk mitigation
- Operational efficiency: 10 hours/week saved in manual limit review

---

## 5. Dependencies

### Upstream Dependencies
- [REQ-001](./REQ-001_real_time_position_aggregation.md#REQ-001): Real-time position aggregation
- [REQ-002](./REQ-002_market_data_integration.md#REQ-002): Market data integration for notional calculations
- [ADR-005](../adrs/ADR-005_risk_architecture.md#ADR-005): Real-time risk architecture decision

### Downstream Dependencies
- [SPEC-003](../specs/SPEC-003_position_limiter.yaml#SPEC-003): Position limiter technical specification
- [BDD-003](../bbds/BDD-003_position_limits.feature#BDD-003): Position limit acceptance tests

---

## 6. Constraints and Assumptions

### Technical Constraints
- Limit check must complete in <10ms to avoid order latency
- Position data must be consistent across distributed services
- Failover to degraded mode if limit service unavailable

### Business Constraints
- Risk managers must approve limit configuration changes
- Limit overrides require manager approval
- Audit trail required for all limit events (SOX compliance)

### Assumptions
- Market data availability: Real-time prices available for all symbols
- Position accuracy: OMS provides accurate position data
- User roles: RBAC system provides role information for authorization

---

## 7. Traceability

### Upstream Sources
| Source | Type | Reference |
|--------|------|-----------|
| [BRD-001](../brds/BRD-001_trading_platform.md#BRD-001) | Business Requirements | Risk management objectives |
| [PRD-002](../prd/PRD-002_risk_controls.md#PRD-002) | Product Requirements | Position limit feature |
| [ADR-005](../adrs/ADR-005_risk_architecture.md#ADR-005) | Architecture Decision | Real-time limit enforcement |
| **SEC Rule 15c3-5** | Regulatory | Market Access Risk Management |

### Downstream Artifacts
| Artifact | Type | Reference |
|----------|------|-----------|
| [SPEC-003](../specs/SPEC-003_position_limiter.yaml#SPEC-003) | Technical Specification | Implementation spec |
| [TASKS-003](../ai_tasks/TASKS-003_position_limiter.md#TASKS-003) | Implementation Tasks | AI generation tasks |
| [BDD-003](../bbds/BDD-003_position_limits.feature#BDD-003) | BDD Scenarios | Acceptance tests |
| `src/risk/position_limiter.py` | Code | Implementation |
| `tests/risk/test_position_limits.py` | Tests | Unit tests |

### Primary Anchor/ID
- **REQ-003**: Position limit enforcement requirement

### Regulatory References
- **SEC Rule 15c3-5(c)(1)(i)**: Pre-trade risk controls for order size and value
- **FINRA Rule 3110**: Supervision of trading activities
- **SOX 404**: Internal controls over financial reporting (audit trail)

### Code Paths
- `src/risk/position_limiter.py::PositionLimiter.enforce_limit()`
- `src/risk/limit_config.py::LimitConfiguration`
- `tests/risk/test_position_limits.py::test_hard_limit_enforcement()`

---

## 8. Risk Areas

### Implementation Risks
- **Race Conditions**: Concurrent orders may breach limits
  - Mitigation: Use database transactions with row-level locking

- **Performance Degradation**: High order volume may exceed latency SLA
  - Mitigation: Cache limit configurations, optimize position lookup

- **Data Consistency**: Distributed position data may be stale
  - Mitigation: Event sourcing for position updates, eventual consistency with conflict resolution

### Operational Risks
- **False Rejections**: Market data issues may cause incorrect limit calculations
  - Mitigation: Degraded mode with manual override option

- **Configuration Errors**: Incorrect limits may block legitimate trades
  - Mitigation: Limit configuration approval workflow, dry-run testing

---

## 9. Verification Methods

### BDD Scenarios
- [BDD-003](../bbds/BDD-003_position_limits.feature#BDD-003): Comprehensive limit enforcement scenarios

### Unit Tests
- `test_hard_limit_blocks_order()`
- `test_soft_limit_generates_warning()`
- `test_limit_override_with_authorization()`
- `test_multiple_limit_types_evaluated()`
- `test_concurrent_orders_race_condition()`

### Integration Tests
- Position aggregation integration
- Market data integration
- Audit trail integration

### Manual Testing
- Risk manager limit override workflow
- Configuration UI validation
- Stress test with high order volume

---

## 10. Implementation Notes

### Design Considerations
- Use in-memory cache (Redis) for limit configurations
- Implement circuit breaker for market data service calls
- Event-driven architecture for position updates

### Testing Guidance
- Mock market data service for unit tests
- Use test doubles for OMS integration
- Load testing: 10,000 limit checks/second

### Monitoring Requirements
- Metric: `limit_check_latency_ms` (P50, P99, P999)
- Alert: Latency >10ms (P99)
- Alert: Limit breach rate >5% of orders
- Dashboards: Grafana dashboard for limit metrics

### Migration Strategy
- Phase 1: Deploy limit service (read-only, monitoring mode)
- Phase 2: Enable soft limits (warnings only)
- Phase 3: Enable hard limits (blocking mode)
- Rollback: Feature flag to disable limit enforcement

---

## 11. Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-12-15 | Risk Team | Initial requirement |
| 1.1 | 2025-01-05 | Risk Team | Added soft limit support per trader feedback |
| 1.2 | 2025-01-10 | Compliance Team | Added SEC 15c3-5 traceability |

---

**End of REQ-003**
```

---

## AI Assistant Application Guidance

### When to Use This Configuration

AI Assistant should automatically apply FINANCIAL_DOMAIN_CONFIG.md when:

1. User selects "Financial Services" in domain questionnaire
2. User presses Enter (default) in domain questionnaire
3. User explicitly says "finance", "trading", "banking", "portfolio"
4. No domain specified (default behavior)

### Application Sequence

1. **Load configuration file**: Read FINANCIAL_DOMAIN_CONFIG.md
2. **Create financial subdirectories**: risk/, trading/, portfolio/, compliance/, ml/
3. **Apply placeholder replacements**: Run sed commands on templates
4. **Validate terminology**: Confirm financial terms used in generated documents
5. **Apply regulatory references**: Include SEC/FINRA/SOX references where applicable

### Validation Checklist

After applying financial domain configuration, verify:

- [ ] `docs/reqs/risk/` directory exists
- [ ] `docs/reqs/trading/` directory exists
- [ ] `docs/reqs/portfolio/` directory exists
- [ ] `docs/reqs/compliance/` directory exists
- [ ] `docs/reqs/ml/` directory exists
- [ ] Placeholder `[RESOURCE_COLLECTION]` replaced with "Portfolio"
- [ ] Placeholder `[RESOURCE_ITEM]` replaced with "Position"
- [ ] Regulatory requirements include SEC/FINRA references
- [ ] Financial terminology used in document examples

---

## References

- [AI_ASSISTANT_RULES.md](./AI_ASSISTANT_RULES.md#rule-3-domain-configuration-application) - Rule 3: Domain Configuration
- [DOMAIN_SELECTION_QUESTIONNAIRE.md](./DOMAIN_SELECTION_QUESTIONNAIRE.md#1-financial-services-default) - Domain selection process
- [DOMAIN_ADAPTATION_GUIDE.md](./DOMAIN_ADAPTATION_GUIDE.md) - Multi-domain adaptation guide (includes Healthcare, E-commerce, IoT)
- [SOFTWARE_DOMAIN_CONFIG.md](./SOFTWARE_DOMAIN_CONFIG.md) - Alternative domain (Software/SaaS)
- [GENERIC_DOMAIN_CONFIG.md](./GENERIC_DOMAIN_CONFIG.md) - Fallback domain (Generic/Other)

---

**End of Financial Services Domain Configuration**
