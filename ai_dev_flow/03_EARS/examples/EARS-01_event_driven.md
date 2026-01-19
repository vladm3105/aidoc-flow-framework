---
title: "EARS-01: Event-Driven Example"
tags:
  - ears-example
  - layer-3-artifact
  - example-document
custom_fields:
  document_type: example
  artifact_type: EARS
  layer: 3
  development_status: example
---

# =============================================================================
# EARS-01: Event-Driven Requirements Example
# =============================================================================
# Example EARS document demonstrating event-driven requirements using
# WHEN-THE-SHALL-WITHIN syntax pattern
# =============================================================================
---
title: "EARS-01: Order Processing Event-Driven Requirements"
tags:
  - ears
  - layer-3-artifact
  - shared-architecture
  - event-driven
  - example
custom_fields:
  document_type: ears
  artifact_type: EARS
  layer: 3
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  schema_reference: "EARS_MVP_SCHEMA.yaml"
  schema_version: "1.0"
---

@brd: BRD.01.01.10
@prd: PRD.01.07.01
@threshold: PRD.035

# EARS-01: Order Processing Event-Driven Requirements

## Document Control

| Item | Details |
|------|---------|
| **Status** | Approved |
| **Version** | 1.0.0 |
| **Date Created** | 2025-12-29 |
| **Last Updated** | 2025-12-29 |
| **Author** | Platform Engineering Team |
| **Priority** | High |
| **Source Document** | @prd: PRD.01.07.01 |
| **BDD-Ready Score** | 95% (Target: >= 90%) |

## 1. Purpose and Context

### 1.1 Document Purpose

This EARS document translates PRD-01 (Order Management System) high-level product requirements into precise, atomic, testable engineering requirements using the WHEN-THE-SHALL-WITHIN syntax pattern for event-driven behaviors.

### 1.2 Scope

This document covers order lifecycle event-driven requirements:
- Order creation and validation events
- Payment processing events
- Fulfillment trigger events
- Cancellation and refund events

### 1.3 Intended Audience

- Solution Architects designing order management architecture
- Engineering teams implementing order processing services
- QA engineers creating BDD test scenarios
- AI code generation tools consuming structured requirements

---

## 2. EARS in Development Workflow

```
BRD-01 (Business Requirements)
        |
PRD-01 (Product Requirements)
        |
EARS-01 (Engineering Requirements) <- You are here
        |
BDD-01 (Behavior-Driven Development)
        |
ADR-01 (Architecture Decisions)
        |
REQ-01 (Atomic Requirements)
        |
SPEC-01 (Technical Specifications)
        |
Code Implementation
```

---

## 3. Event-Driven Requirements

### 3.1 Order Creation Events

**EARS-01-001: Order Creation from Cart**
```
WHEN a customer submits a valid shopping cart for checkout,
THE Order Service SHALL create a new order with DRAFT status,
validate all cart items against current inventory,
reserve inventory for each line item,
and return the order ID with estimated delivery date
WITHIN @threshold: PRD.035.perf.api.p95_latency (500ms).
```
**Traceability**: @brd: BRD.01.01.10 | @prd: PRD.01.07.01 | @threshold: PRD.035.perf.api.p95_latency | @entity: PRD.004.Order

**EARS-01-002: Order Validation Failure**
```
WHEN a customer submits a cart containing invalid or unavailable items,
THE Order Service SHALL reject the order request,
return detailed validation errors with item-level codes,
and preserve the original cart state unchanged
WITHIN @threshold: PRD.035.perf.api.p95_latency (500ms).
```
**Traceability**: @brd: BRD.01.01.10 | @prd: PRD.01.07.02 | @threshold: PRD.035.perf.api.p95_latency

**EARS-01-003: Inventory Reservation**
```
WHEN an order is created with DRAFT status,
THE Inventory Service SHALL reserve the requested quantity for each line item,
decrement available inventory counts,
and record reservation references on the order
WITHIN @threshold: PRD.035.perf.api.sync_timeout (2000ms).
```
**Traceability**: @brd: BRD.01.01.15 | @prd: PRD.01.07.03 | @threshold: PRD.035.perf.api.sync_timeout | @entity: PRD.004.InventoryReservation

### 3.2 Payment Processing Events

**EARS-01-004: Payment Authorization Request**
```
WHEN a customer submits payment for a DRAFT order,
THE Order Service SHALL transition the order to PENDING_PAYMENT status,
forward the payment authorization to Payment Service,
and await payment result callback
WITHIN @threshold: PRD.035.timeout.payment.authorization (30000ms).
```
**Traceability**: @brd: BRD.01.01.20 | @prd: PRD.01.08.01 | @threshold: PRD.035.timeout.payment.authorization | @entity: PRD.004.PaymentTransaction

**EARS-01-005: Payment Authorization Success**
```
WHEN Payment Service returns a successful authorization,
THE Order Service SHALL transition the order to PAID status,
record the authorization code and transaction ID,
publish order.paid event to the message queue,
and trigger fulfillment processing
WITHIN @threshold: PRD.035.perf.api.p95_latency (500ms).
```
**Traceability**: @brd: BRD.01.01.20 | @prd: PRD.01.08.02 | @threshold: PRD.035.perf.api.p95_latency

**EARS-01-006: Payment Authorization Failure**
```
WHEN Payment Service returns a declined authorization,
THE Order Service SHALL retain the order in PENDING_PAYMENT status,
record the decline reason and error code,
notify the customer of payment failure with retry options,
and preserve inventory reservations for @threshold: PRD.035.reservation.hold_duration (15 minutes)
WITHIN @threshold: PRD.035.perf.api.p95_latency (500ms).
```
**Traceability**: @brd: BRD.01.01.20 | @prd: PRD.01.08.03 | @threshold: PRD.035.reservation.hold_duration

**EARS-01-007: Payment Capture on Fulfillment**
```
WHEN an order transitions to SHIPPED status,
THE Payment Service SHALL capture the authorized payment amount,
record the capture transaction,
and update the order with capture confirmation
WITHIN @threshold: PRD.035.timeout.payment.capture (10000ms).
```
**Traceability**: @brd: BRD.01.01.20 | @prd: PRD.01.08.04 | @threshold: PRD.035.timeout.payment.capture

### 3.3 Fulfillment Events

**EARS-01-008: Fulfillment Initiation**
```
WHEN an order reaches PAID status,
THE Order Service SHALL create a fulfillment request,
assign to the optimal fulfillment center based on inventory location,
publish order.fulfillment_requested event,
and transition order to PROCESSING status
WITHIN @threshold: PRD.035.perf.api.p95_latency (500ms).
```
**Traceability**: @brd: BRD.01.02.01 | @prd: PRD.01.09.01 | @threshold: PRD.035.perf.api.p95_latency | @entity: PRD.004.FulfillmentRequest

**EARS-01-009: Shipment Confirmation**
```
WHEN Fulfillment Service confirms shipment dispatch,
THE Order Service SHALL transition the order to SHIPPED status,
record tracking number and carrier information,
initiate payment capture,
and notify customer with tracking details
WITHIN @threshold: PRD.035.perf.api.p95_latency (500ms).
```
**Traceability**: @brd: BRD.01.02.02 | @prd: PRD.01.09.02 | @threshold: PRD.035.perf.api.p95_latency

**EARS-01-010: Delivery Confirmation**
```
WHEN carrier confirms package delivery,
THE Order Service SHALL transition the order to DELIVERED status,
record delivery timestamp and confirmation signature,
release inventory reservation permanently,
and trigger customer satisfaction survey
WITHIN @threshold: PRD.035.perf.api.p95_latency (500ms).
```
**Traceability**: @brd: BRD.01.02.03 | @prd: PRD.01.09.03 | @threshold: PRD.035.perf.api.p95_latency

### 3.4 Cancellation Events

**EARS-01-011: Order Cancellation Request**
```
WHEN a customer requests cancellation of a non-shipped order,
THE Order Service SHALL validate cancellation eligibility based on current status,
release all inventory reservations,
initiate refund if payment was captured,
and transition order to CANCELLED status
WITHIN @threshold: PRD.035.perf.api.p95_latency (500ms).
```
**Traceability**: @brd: BRD.01.03.01 | @prd: PRD.01.10.01 | @threshold: PRD.035.perf.api.p95_latency

**EARS-01-012: Automatic Cancellation on Payment Timeout**
```
WHEN a PENDING_PAYMENT order exceeds @threshold: PRD.035.reservation.hold_duration,
THE Order Service SHALL automatically cancel the order,
release all inventory reservations,
notify the customer of timeout cancellation,
and log cancellation reason for analytics
WITHIN @threshold: PRD.035.perf.batch.p95_latency (1000ms).
```
**Traceability**: @brd: BRD.01.03.02 | @prd: PRD.01.10.02 | @threshold: PRD.035.reservation.hold_duration

**EARS-01-013: Refund Processing**
```
WHEN an order is cancelled with captured payment,
THE Payment Service SHALL initiate refund for the captured amount,
record refund transaction with reference to original capture,
and notify Order Service of refund completion
WITHIN @threshold: PRD.035.timeout.payment.refund (5000ms).
```
**Traceability**: @brd: BRD.01.03.03 | @prd: PRD.01.10.03 | @threshold: PRD.035.timeout.payment.refund | @entity: PRD.004.RefundTransaction

### 3.5 Notification Events

**EARS-01-014: Order Confirmation Notification**
```
WHEN an order reaches PAID status,
THE Notification Service SHALL send order confirmation email to customer,
include order summary, estimated delivery, and tracking information,
and record notification delivery status
WITHIN @threshold: PRD.035.timeout.notification.email (30000ms).
```
**Traceability**: @brd: BRD.01.04.01 | @prd: PRD.01.11.01 | @threshold: PRD.035.timeout.notification.email

**EARS-01-015: Shipping Notification**
```
WHEN an order transitions to SHIPPED status,
THE Notification Service SHALL send shipping confirmation with tracking link,
include carrier name, tracking number, and estimated arrival,
and schedule delivery day reminder notification
WITHIN @threshold: PRD.035.timeout.notification.email (30000ms).
```
**Traceability**: @brd: BRD.01.04.02 | @prd: PRD.01.11.02 | @threshold: PRD.035.timeout.notification.email

---

## 4. Quality Attributes

### 4.1 Performance Requirements

| QA ID | Requirement Statement | Metric | Target | Priority | Measurement Method |
|-------|----------------------|--------|--------|----------|-------------------|
| EARS.01.02.01 | THE Order Service SHALL complete order creation | Latency | p95 < 500ms | High | APM tracing |
| EARS.01.02.02 | THE Order Service SHALL process concurrent orders | Throughput | 1000 TPS | High | Load testing |
| EARS.01.02.03 | THE Payment integration SHALL complete authorization | Latency | p95 < 5000ms | High | Integration monitoring |

### 4.2 Reliability Requirements

| QA ID | Requirement Statement | Target | Priority | Measurement Period |
|-------|----------------------|--------|----------|-------------------|
| EARS.01.02.04 | THE Order Service SHALL maintain availability | 99.9% | High | Monthly |
| EARS.01.02.05 | THE Order Service SHALL preserve data consistency | Zero data loss | Critical | Per transaction |
| EARS.01.02.06 | THE Event publishing SHALL guarantee delivery | At-least-once | High | Per event |

### 4.3 Security Requirements

| QA ID | Requirement Statement | Standard/Framework | Priority | Validation Method |
|-------|----------------------|-------------------|----------|-------------------|
| EARS.01.02.07 | THE Order Service SHALL encrypt PII at rest | AES-256 | Critical | Security audit |
| EARS.01.02.08 | THE Payment data SHALL comply with PCI-DSS | PCI-DSS Level 1 | Critical | Compliance audit |

---

## 5. Traceability

### 5.1 Upstream Sources

| Source Type | Document ID | Document Title | Relevant Sections | Relationship |
|-------------|-------------|----------------|-------------------|--------------|
| BRD | BRD-01 | E-Commerce Platform Business Requirements | Sections 3.1-3.4 | Business objectives |
| PRD | PRD-01 | Order Management Product Requirements | Sections 7-11 | Product features |
| Threshold Registry | PRD-035 | Platform Threshold Registry | All | Timing thresholds |
| Entity Definitions | PRD-004 | Data Model & Entity Ledger | Section 1.3 | Entity definitions |

### 5.2 Downstream Artifacts

| Target | Document ID | Status | Relationship |
|--------|-------------|--------|--------------|
| BDD | BDD-01 | Completed | Test scenarios |
| ADR | ADR-01 | Completed | Architecture decisions |
| SYS | SYS-01 | Completed | System requirements |
| REQ | REQ-01 | Planned | Atomic requirements |
| SPEC | SPEC-01 | Planned | Technical specifications |

### 5.3 Traceability Tags

```markdown
@brd: BRD.01.01.10
@prd: PRD.01.07.01
@threshold: PRD.035
@entity: PRD.004.Order
```

### 5.4 Thresholds Referenced

```yaml
timing:
  - "@threshold: PRD.035.perf.api.p95_latency"           # 500ms
  - "@threshold: PRD.035.perf.api.sync_timeout"         # 2000ms
  - "@threshold: PRD.035.timeout.payment.authorization" # 30000ms
  - "@threshold: PRD.035.timeout.payment.capture"       # 10000ms
  - "@threshold: PRD.035.timeout.payment.refund"        # 5000ms
  - "@threshold: PRD.035.timeout.notification.email"    # 30000ms

limits:
  - "@threshold: PRD.035.reservation.hold_duration"     # 15 minutes

performance:
  - "@threshold: PRD.035.perf.batch.p95_latency"        # 1000ms
```

---

## 6. References

### 6.1 Internal Documentation

- EARS Style Guide (EARS_STYLE_GUIDE.md)
- PRD-01 (../02_PRD/PRD-01_order_management.md) - Source product requirements
- PRD-035 (../02_PRD/PRD-035_platform_threshold_registry.md) - Threshold registry
- PRD-004 (../02_PRD/PRD-004_data_model_entity_ledger.md) - Entity definitions

### 6.2 External Standards

- EARS-inspired structured patterns: Mavin et al. (2009)
- ISO/IEC/IEEE 29148:2018: Requirements engineering
- RFC 2119: Requirement level keywords (SHALL, SHOULD, MAY)

---

## Requirement ID Naming Convention

| Category | ID Range | Pattern | Example |
|----------|----------|---------|---------|
| Event-Driven | 001-099 | EARS.01.25.0SS | EARS.01.25.001 |
| State-Driven | 101-199 | EARS.01.25.1SS | EARS.01.25.101 |
| Unwanted Behavior | 201-299 | EARS.01.25.2SS | EARS.01.25.201 |
| Ubiquitous | 401-499 | EARS.01.25.4SS | EARS.01.25.401 |

---

**Document Version**: 1.0.0
**Template Version**: 3.0
**Last Reviewed**: 2025-12-29
**Maintained By**: Platform Engineering Team

# =============================================================================
# END OF EARS-01: Event-Driven Requirements Example
# =============================================================================
