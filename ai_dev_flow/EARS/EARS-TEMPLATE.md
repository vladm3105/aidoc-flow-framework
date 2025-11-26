---
title: "EARS-TEMPLATE: Engineering Requirements (EARS Format)"
tags:
  - ears-template
  - layer-3-artifact
  - shared-architecture
  - document-template
custom_fields:
  document_type: template
  artifact_type: EARS
  layer: 3
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  template_for: engineering-requirements-document
---

# EARS-NNN: [Short Descriptive Title]

**⚠️ CRITICAL**: Always reference [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) as the single source of truth for workflow steps, artifact definitions, and quality gates.

**[RESOURCE_INSTANCE - e.g., database connection, workflow instance]**: EARS is in Layer 3 (Formal Requirements Layer) - transforms PRD into formal WHEN/THEN requirements.

## Document Control

| Item | Details |
|------|---------|
| **Status** | Draft / In Review / Approved / Implemented |
| **Version** | [e.g., 1.0.0] |
| **Date Created** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD |
| **Author** | [Name and role] |
| **Priority** | High / Medium / Low |
| **Source Document** | [PRD-NNN, BRD-NNN, or SYS-NNN] |

## 1. Purpose and Context

### 1.1 Document Purpose
This EARS (Easy Approach to Requirements Syntax) document translates high-level business and product requirements into precise, atomic, testable engineering requirements using structured syntax patterns. EARS statements serve as the foundation for downstream specifications, architecture decisions, and BDD scenarios.

### 1.2 Scope
This document covers [specific system/component/feature] requirements derived from [source documents]. It defines behavioral requirements using WHEN-THE-SHALL-WITHIN syntax to ensure clarity, measurability, and AI-readability.

### 1.3 Intended Audience
- Solution Architects designing system architecture
- Engineering teams implementing functionality
- QA engineers creating test scenarios
- AI code generation tools consuming structured requirements
- Product managers validating requirement completeness

---

## 2. [RESOURCE_INSTANCE - e.g., database connection, workflow instance] in Development Workflow

```
BRD (Business Requirements Document): High-level business needs and objectives
        ↓
PRD (Product Requirements Document): User needs and product features
        ↓
EARS (Easy Approach to Requirements Syntax): Atomic, measurable technical requirements
        ↓
BDD (Behavior-Driven Development): Test scenarios and acceptance criteria
        ↓
ADR (Architecture Decision Records): Technical design decisions with rationales
        ↓
SYS (System Requirements): Technical interpretation of business requirements
        ↓
REQ (Atomic Requirements): Detailed, actionable implementation requirements
        ↓
SPEC (Technical Implementation): YAML specifications for code generation
        ↓
Code (src/{module_name}/): AI-generated Python implementation
        ↓
Tests (tests/{suite_name}/): AI-generated test suites
        ↓
Validation: BDD test execution
        ↓
Human Review: Architecture and business logic review
        ↓
Production-Ready Code
```

**EARS Role**: Bridge between business intent (BRD/PRD) and technical implementation (ADR/REQ/SPEC). Every EARS statement must be independently verifiable and traceable to business objectives.

---

## 3. Requirements

### 3.1 Event-Driven Requirements

**Format**: WHEN [triggering condition] THE [system/component] SHALL [response action] WITHIN [time/constraint].

**Purpose**: Define system behavior triggered by specific events, state changes, or external stimuli.

**Guidelines**:
- Specify exact triggering condition (observable, measurable)
- Define clear response action (single responsibility)
- Include performance constraint (timing, throughput, latency)
- Ensure triggering condition is deterministic

**Examples**:

#### Example 1: Real-Time Data Processing
```
WHEN a new [Data_Event: e.g., message, transaction, sensor reading] arrives from [External_System: e.g., API, queue, stream],
THE [Processing_Component: e.g., Handler, Processor, Controller] SHALL [Action: e.g., update calculations, transform data, validate input]
WITHIN [Latency_Target: e.g., 50 milliseconds] at [Percentile: e.g., p95] latency.
```

#### Example 2: Threshold Violation
```
WHEN [Metric_Name: e.g., error rate, queue depth, response time] exceeds [Threshold_Value: e.g., ±5.0, 100 requests, 2%] absolute value,
THE [Monitoring_Component: e.g., Alert Manager, Controller, Agent] SHALL trigger [Response_Action: e.g., analysis, scaling, notification] and emit alert
WITHIN [Response_Time: e.g., 5 seconds] of threshold breach detection.
```

#### Example 3: State Update Confirmation
```
WHEN a [State_Change_Event: e.g., order confirmation, completion event, status update] is received from [External_System],
THE [State_Manager: e.g., Coordinator, Manager, Controller] SHALL [Action: e.g., update records, recalculate metrics, persist state] to database
WITHIN [Response_Time: e.g., 2 seconds] of confirmation timestamp.
```

#### Example 4: System Transition
```
WHEN [Scheduled_Event: e.g., business hours start, maintenance window, batch cycle] is reached,
THE [System_Component] SHALL transition from [State_A: e.g., IDLE, STANDBY] to [State_B: e.g., ACTIVE, MONITORING] mode
WITHIN [Transition_Time: e.g., 30 seconds] of event timestamp.
```

---

### 3.2 State-Driven Requirements

**Format**: WHILE [system state] THE [system/component] SHALL [behavioral restriction/action] WITHIN [state duration/constraint].

**Purpose**: Define behavior dependent on system state, operational mode, or environmental conditions.

**Guidelines**:
- Clearly define the state condition
- Specify behavior that must hold throughout state duration
- Include exit conditions where applicable
- Avoid ambiguous state definitions

**Examples**:

#### Example 1: Maintenance Mode
```
WHILE the system is in maintenance mode,
THE Trading Engine SHALL reject all new trade requests with HTTP 503 status
and queue non-critical background tasks
WITHIN the maintenance window (no more than 4 hours).
```

#### Example 2: Degraded Service
```
WHILE the [EXTERNAL_DATA_PROVIDER - e.g., Weather API, Stock Data API] API returns HTTP 429 rate limit errors,
THE [EXTERNAL_DATA - e.g., customer data, sensor readings] Client SHALL serve cached responses if freshness is within 5 minutes
and surface [SAFETY_MECHANISM - e.g., rate limiter, error threshold] state to upstream callers.
```

#### Example 3: Defensive State
```
WHILE [System_State: e.g., a resource, component, entity] is in [Critical_State: e.g., DEFENSE, HIGH_LOAD, ALERT] state ([Condition: e.g., threshold ≥60% consumed]),
THE [Coordinator_Component: e.g., Orchestrator, Manager, Controller] SHALL [Monitoring_Action: e.g., monitor metrics, check status] every [Interval: e.g., 15 minutes] and evaluate [Decision: e.g., adjustment opportunities, scaling actions]
WITHIN each monitoring interval.
```

#### Example 4: Inactive Period
```
WHILE [Operational_Period: e.g., business hours, service window, batch period] is [State: e.g., closed, inactive, suspended] ([Time_Range: e.g., before 09:30 or after 16:00]),
THE [System_Component] SHALL [Restricted_Behavior: e.g., postpone operations, maintain read-only access, queue requests]
WITHIN the [Period_Name: e.g., closed session, inactive period].
```

---

### 3.3 Unwanted Behavior Requirements

**Format**: IF [error/problematic condition] THE [system/component] SHALL [preventative/recovery action] WITHIN [response time].

**Purpose**: Define behaviors to prevent, detect, or recover from error conditions, violations, or unwanted states.

**Guidelines**:
- Specify exact error condition triggering prevention
- Define clear mitigation or recovery action
- Include response time constraint
- Address both detection and remediation

**Examples**:

#### Example 1: Rate Limit Protection
```
IF the [EXTERNAL_INTEGRATION - e.g., third-party API, service provider] API rate limit is exceeded (HTTP 429 received),
THE API Client SHALL apply exponential backoff with token bucket throttling,
return clear error to caller with retry-after guidance,
and emit rate limit breach metric
WITHIN 100 milliseconds of error detection.
```

#### Example 2: Invalid Input Data
```
IF [Data_Source: e.g., API response, user input, file upload] contains invalid or out-of-range values ([Examples: e.g., negative values, future timestamps, missing required fields]),
THE [Validator_Component: e.g., Data Validator, Input Checker] SHALL reject the data, log validation failure with correlation ID,
and [Fallback_Action: e.g., continue processing using cached value, return error response]
WITHIN [Response_Time: e.g., 10 milliseconds] of detection.
```

#### Example 3: Deadlock Prevention
```
IF concurrent [RESOURCE_INSTANCE - e.g., database connection, workflow instance] updates would cause database deadlock (detected via lock timeout),
THE [RESOURCE_INSTANCE - e.g., database connection, workflow instance] Manager SHALL rollback transaction, apply jittered retry with exponential backoff,
and escalate to manual review after 3 failed attempts
WITHIN 30 seconds of initial deadlock detection.
```

#### Example 4: Security Breach Detection
```
IF unauthorized API access is detected (invalid token, failed authentication after 3 attempts),
THE Authentication Service SHALL terminate the session, revoke credentials,
emit security alert with client IP and request details,
and enforce 15-minute lockout
WITHIN 500 milliseconds of breach detection.
```

#### Example 5: [SAFETY_MECHANISM - e.g., rate limiter, error threshold] Activation
```
IF [Critical_Metric: e.g., error rate, resource usage, business metric] exceeds [Threshold: e.g., 2% of baseline, 100 errors/min],
THE [Protection_Component: e.g., [SAFETY_MECHANISM - e.g., rate limiter, error threshold], Safety Controller] SHALL activate protection mode,
[Emergency_Actions: e.g., halt new operations, rollback changes, isolate component],
and notify [Responsible_Party: e.g., on-call engineer, team lead] via [Notification_Channel: e.g., email, Slack, PagerDuty]
WITHIN [Response_Time: e.g., 60 seconds] of breach detection.
```

---

### 3.4 Ubiquitous Requirements

**Format**: THE [system/component] SHALL [system-wide requirement] WITHIN [architectural boundary/constraint].

**Purpose**: Define cross-cutting concerns, quality attributes, and system-wide constraints that apply regardless of specific events or states.

**Guidelines**:
- Apply to entire system or major subsystem
- Define non-negotiable quality attributes
- Specify measurable thresholds
- Include architectural constraints

**Examples**:

#### Example 1: Data Normalization
```
THE [External_Client: e.g., API Client, Adapter, Gateway] SHALL normalize all [Data_Type: e.g., API responses, messages, records] to the internal [Schema_Name: e.g., data schema, event format]
used by [Internal_System: e.g., Core Service, Processing Engine] to enable [Benefit: e.g., seamless failover, data consistency, integration flexibility].
```

#### Example 2: Performance Baseline
```
THE [System_Component: e.g., Processing Engine, Workflow Orchestrator] SHALL complete end-to-end [Operation: e.g., request processing, transaction execution] ([Operation_Steps: e.g., initiation to completion])
WITHIN [Latency_Target: e.g., 500 milliseconds] at [Percentile: e.g., p95] latency during [Operational_Period: e.g., business hours, peak load].
```

#### Example 3: Security Standard
```
THE System SHALL encrypt all data at rest using AES-256 encryption
and all data in transit using TLS 1.2 or higher
WITHIN organizational security policy boundaries.
```

#### Example 4: Observability Standard
```
THE System SHALL emit structured logs with correlation IDs, timestamps (ISO-8601 UTC),
severity levels, and contextual metadata for all critical operations
WITHIN the centralized logging framework (Google Cloud Logging).
```

#### Example 5: Audit Compliance
```
THE System SHALL persist all [Audit_Events: e.g., transactions, approvals, state transitions]
to [Storage_Type: e.g., tamper-evident WORM storage, immutable log, audit database] with [Retention_Period: e.g., 7-year, 90-day] retention
WITHIN applicable [Compliance_Framework: e.g., regulatory, security, governance] requirements.
```

#### Example 6: Idempotency
```
THE API Gateway SHALL ensure all state-changing operations are idempotent
using request deduplication with 24-hour deduplication window
WITHIN the distributed transaction boundary.
```

---

## 4. Non-Functional Requirements (NFRs)

### 4.1 Performance Requirements

Define latency, throughput, response time, and resource utilization constraints.

| NFR ID | Requirement Statement | Metric | Target | Priority | Measurement Method |
|--------|----------------------|--------|--------|----------|-------------------|
| NFR-PERF-001 | THE System SHALL process [Data_Type: e.g., events, messages, requests] | End-to-end latency | p95 < [Target: e.g., 50ms] | High | Latency monitoring with percentile aggregation |
| NFR-PERF-002 | THE System SHALL support concurrent [Operations: e.g., transactions, calculations, workflows] | Throughput | [Target: e.g., 100 operations/second] | Medium | Load testing with synthetic workload |
| NFR-PERF-003 | THE Database SHALL complete [Query_Type: e.g., record queries, aggregations] | Query response time | p99 < [Target: e.g., 100ms] | High | Database performance monitoring |

**Guidelines**:
- Specify percentile targets (p50, p95, p99) not averages
- Include peak vs. sustained load requirements
- Define resource consumption limits (CPU, memory, network)
- Specify degradation behavior under load

---

### 4.2 Security Requirements

Define authentication, authorization, encryption, secrets management, and audit requirements.

| NFR ID | Requirement Statement | Standard/Framework | Priority | Validation Method |
|--------|----------------------|-------------------|----------|-------------------|
| NFR-SEC-001 | THE System SHALL authenticate all API requests | OAuth 2.0 / OpenID Connect | High | Penetration testing, auth flow validation |
| NFR-SEC-002 | THE System SHALL enforce role-based access control (RBAC) | Least privilege principle | High | Access audit logs, permission matrix review |
| NFR-SEC-003 | THE System SHALL rotate secrets and credentials | 90-day rotation cadence | Medium | Secrets management audit, rotation logs |
| NFR-SEC-004 | THE System SHALL audit all privileged operations | WORM/tamper-evident logging | High | Compliance audit, log integrity verification |

**Guidelines**:
- Reference specific security standards (OWASP, NIST)
- Define separation-of-duties (SoD) requirements
- Specify secrets management approach (e.g., Google Secret Manager)
- Include threat model references

---

### 4.3 Reliability Requirements

Define availability, fault tolerance, recovery time objectives, and failover requirements.

| NFR ID | Requirement Statement | Target | Priority | Measurement Period |
|--------|----------------------|--------|----------|-------------------|
| NFR-REL-001 | THE System SHALL maintain uptime during [Operational_Period: e.g., business hours, peak season] | [Availability_Target: e.g., 99.99%] availability | High | [Measurement_Window: e.g., Business hours, Monthly] |
| NFR-REL-002 | THE System SHALL complete failover to secondary [Location: e.g., region, datacenter] | RTO < [Target: e.g., 30 seconds] | High | Disaster recovery drills (quarterly) |
| NFR-REL-003 | THE System SHALL tolerate single [Component_Type: e.g., component, service] failure | [Recovery_Target: e.g., Zero data loss (RPO = 0)] | High | Chaos engineering tests |
| NFR-REL-004 | THE System SHALL recover from [Failure_Type: e.g., database, network] failures | Auto-recovery < [Target: e.g., 2 minutes] | Medium | Failure injection testing |

**Guidelines**:
- Define Recovery Time Objective (RTO) and Recovery Point Objective (RPO)
- Specify acceptable degradation modes
- Include health check requirements
- Define alerting thresholds and escalation paths

---

### 4.4 Scalability Requirements

Define capacity, growth projections, and scaling behavior.

| NFR ID | Requirement Statement | Current Baseline | Year 1 Target | Year 3 Target | Priority |
|--------|----------------------|-----------------|---------------|---------------|----------|
| NFR-SCALE-001 | THE System SHALL support concurrent [Entities: e.g., users, sessions, records] | [Current: e.g., 100 entities] | [Year1: e.g., 1,000 entities] | [Year3: e.g., 5,000 entities] | High |
| NFR-SCALE-002 | THE System SHALL process [Data_Type: e.g., data, events, transactions] volume | [Current: e.g., 1 TB/day] | [Year1: e.g., 5 TB/day] | [Year3: e.g., 20 TB/day] | High |
| NFR-SCALE-003 | THE System SHALL handle [Request_Type: e.g., API requests, transactions] volume | [Current: e.g., 1,000/day] | [Year1: e.g., 10,000/day] | [Year3: e.g., 50,000/day] | Medium |

**Guidelines**:
- Define horizontal vs. vertical scaling approach
- Specify auto-scaling thresholds and policies
- Include resource capacity planning
- Define performance degradation boundaries

---

### 4.5 Observability Requirements

Define logging, monitoring, tracing, alerting, and debugging requirements.

| NFR ID | Requirement Statement | Implementation | Priority | Validation Method |
|--------|----------------------|----------------|----------|-------------------|
| NFR-OBS-001 | THE System SHALL emit structured logs with correlation IDs | JSON format, trace propagation | High | Log query validation, trace sampling |
| NFR-OBS-002 | THE System SHALL expose Prometheus-compatible metrics | /metrics endpoint with SLI metrics | High | Metrics scraping validation |
| NFR-OBS-003 | THE System SHALL provide distributed tracing | OpenTelemetry with 1% sampling | Medium | Trace visualization, latency breakdown |
| NFR-OBS-004 | THE System SHALL alert on SLO violations | Threshold-based alerts with runbooks | High | Alert firing validation, on-call testing |

**Guidelines**:
- Define Service Level Indicators (SLIs) and Service Level Objectives (SLOs)
- Specify log retention and query requirements
- Include dashboard and visualization requirements
- Define alerting thresholds with business context

---

### 4.6 Compliance Requirements

Define regulatory, audit, data retention, and governance requirements.

| NFR ID | Regulation/Standard | Requirement Statement | Applicability | Priority | Validation Method |
|--------|---------------------|----------------------|---------------|----------|-------------------|
| NFR-COMP-001 | [Regulation: e.g., GDPR, HIPAA, [COMPLIANCE_STANDARD - e.g., PCI-DSS, ISO27001]] | THE System SHALL retain all [Record_Type: e.g., transactions, audit logs] for [Period: e.g., 7 years] | [Jurisdiction: e.g., EU, US, Global] | High | Compliance audit, retention policy review |
| NFR-COMP-002 | [Standard: e.g., PCI-DSS, ISO 27001] | THE System SHALL [Compliance_Action: e.g., document processes, implement controls] | [Scope: e.g., payment data, customer records] | High | [Validation: e.g., audit reports, certification review] |
| NFR-COMP-003 | [Privacy_Law: e.g., GDPR, CCPA] | THE System SHALL support [Privacy_Rights: e.g., data access, deletion requests] | [Jurisdiction: e.g., EU, California] customer data | Medium | Privacy impact assessment, request workflow testing |

**Guidelines**:
- Specify jurisdiction-specific requirements
- Define data residency and sovereignty constraints
- Include audit trail and evidence requirements
- Reference compliance frameworks (SOC 2, ISO 27001)

---

## 5. Guidelines for Writing EARS Statements

### 5.1 Precision and Measurability

**Principle**: Every EARS statement must be objectively verifiable through testing or observation.

**Good Examples**:
```
✓ WHEN [Metric: e.g., queue depth, error rate] exceeds [Threshold: e.g., ±5.0, 100 errors], THE [Component: e.g., Alert Manager, Controller] SHALL trigger [Action: e.g., analysis, scaling] WITHIN [Time: e.g., 5 seconds].
✓ THE System SHALL complete [Operation: e.g., API requests, transactions] WITHIN [Latency: e.g., 500ms] at [Percentile: e.g., p95] latency.
```

**Bad Examples**:
```
✗ The system should be fast. (Vague, not measurable)
✗ When risk is high, take action. (Undefined threshold, unclear action)
✗ The system shall perform well under load. (Subjective, no quantification)
```

**Guidelines**:
- Replace subjective terms (fast, slow, reliable) with quantitative metrics
- Define exact thresholds and boundaries
- Specify measurement method and percentile
- Include units and time frames

---

### 5.2 Atomic Requirements (One Concept Per Statement)

**Principle**: Each EARS statement represents a single, independently testable requirement.

**Good Example (Atomic)**:
```
✓ WHEN a [Event: e.g., confirmation, completion event] is received, THE [Component: e.g., Manager, Controller] SHALL [Action: e.g., update records, process data] WITHIN [Time: e.g., 2 seconds].
✓ WHEN [State_Change: e.g., records updated, data processed] occurs, THE System SHALL [Follow_Up_Action: e.g., recalculate metrics, trigger notification] WITHIN [Time: e.g., 5 seconds].
```

**Bad Example (Compound)**:
```
✗ WHEN a [Event] is received, THE System SHALL [Action1], [Action2], [Action3],
[Action4], and [Action5] WITHIN [Time].
```

**Guidelines**:
- Split compound requirements into separate statements
- Each statement should have one clear success criterion
- Maintain logical dependencies through sequencing
- Use separate EARS statements for different failure modes

---

### 5.3 Testability Criteria

**Principle**: EARS statements must enable direct translation to BDD scenarios and automated tests.

**Testable Statement Structure**:
1. **Given**: Initial state or precondition (implicit in WHEN/WHILE/IF)
2. **When**: Triggering event or condition
3. **Then**: Expected outcome (THE SHALL clause)
4. **Verify**: Measurable assertion (WITHIN clause)

**Example Mapping to BDD**:

**EARS Statement**:
```
WHEN [Metric: e.g., error rate, queue depth] exceeds [Threshold: e.g., ±5.0, 100 requests], THE [Component: e.g., Controller, Manager] SHALL trigger [Action: e.g., analysis, scaling] WITHIN [Time: e.g., 5 seconds].
```

**BDD Scenario**:
```gherkin
Scenario: [Metric] breach triggers [Action]
  Given a [System_State: e.g., system with metric at baseline value]
  When [Event: e.g., new activity] increases [Metric] to [Threshold_Value]
  Then the [Component] SHALL trigger [Action]
  And the [Action] SHALL complete within [Time] of breach detection
  And an alert SHALL be emitted with [Metric] value and timestamp
```

**Guidelines**:
- Include observable outputs (logs, metrics, state changes)
- Specify verification method (API response, database query, log entry)
- Define success and failure criteria
- Enable automation through clear assertions

---

### 5.4 Common Patterns

#### Pattern 1: Request-Response
```
WHEN [actor] requests [operation] with [parameters],
THE [system] SHALL [process request] and return [response]
WITHIN [latency constraint].
```

#### Pattern 2: Threshold-Based Trigger
```
WHEN [metric] exceeds [threshold value],
THE [system] SHALL [trigger action] and [emit notification]
WITHIN [response time].
```

#### Pattern 3: State Transition
```
WHEN [condition] is met,
THE [system] SHALL transition from [state A] to [state B]
and [perform transition actions]
WITHIN [transition time].
```

#### Pattern 4: Error Recovery
```
IF [error condition] occurs,
THE [system] SHALL [detect error], [log details],
[attempt recovery] with [retry policy],
and [escalate if unrecoverable]
WITHIN [recovery window].
```

#### Pattern 5: Periodic Operations
```
WHILE [system is in operational state],
THE [component] SHALL [perform periodic task]
every [interval] with [tolerance]
WITHIN [operational hours].
```

---

### 5.6 Business vs Technical Requirements Boundary

**Purpose**: This section defines the boundary between Business Requirements (BRD-level) and Product/Technical Requirements (PRD-level) when writing EARS statements. Use this guide to ensure EARS requirements stay appropriately abstract and implementation-agnostic.

#### ❌ EXCLUDE from EARS Statements (PRD-Level/SPEC-Level Content)

**1. UI Interaction Flows**
- "User clicks X button"
- "System displays Y screen"
- "Form shows Z fields"
- Screen layouts, button placements, UI element specifications

**2. API Endpoint Specifications**
- POST /quotes, GET /transactions
- JSON request/response payloads
- HTTP status codes (200, 400, 500)
- API versioning, rate limiting headers

**3. Technical Implementation Details**
- Debounced inputs (500ms delay)
- WebSocket connections for real-time updates
- Database transactions (BEGIN...COMMIT)
- Caching strategies, session management

**4. State Machine Transitions**
- INITIATED → FUNDED → COMPLETED with event handlers
- State management logic (on wallet_debited event, transition to FUNDED)
- Technical state coordination

**5. Specific Timeout Values**
- 90-second quote validity
- 500ms debounce delay
- 30-second API timeout

**6. Code-Level Logic**
- Idempotency key generation (UUID, SHA256 hashing)
- Retry exponential backoff algorithms
- Webhook signature verification (HMAC-SHA256)
- Feature engineering functions for ML models

**7. Technical Error Handling**
- Rollback transaction logic
- Database constraint violations
- Circuit breaker patterns
- Technical fault tolerance mechanisms

**8. Code Blocks**
- Python functions and pseudocode
- JSON schema examples
- SQL queries
- Algorithm implementations

---

#### ✅ INCLUDE in EARS Statements (Business/Functional Requirements)

**1. Business Capability Required**
```
WHEN customer initiates recipient selection,
THE System SHALL enable selection from saved recipients or creation of new recipient
WITHIN transaction initiation workflow.
```

**2. Business Rules and Policies**
```
WHEN transaction amount is determined,
THE System SHALL enforce transaction limits based on KYC verification tier
(L1: $200, L2: $1,000, L3: $10,000)
WITHIN transaction validation process.
```

**3. Regulatory/Compliance Requirements**
```
WHEN transaction is submitted,
THE System SHALL screen transaction against OFAC sanctions list
and complete screening within 3 seconds for 95% of transactions.
```

**4. Business Acceptance Criteria with Measurable Targets**
```
WHEN screening is completed,
THE System SHALL maintain false positive rate ≤3%
to minimize blocking legitimate customers.
```

**5. Business Outcomes and Metrics**
```
WHEN transaction is initiated,
THE System SHALL achieve first-attempt delivery success ≥95%
and notify customer within 60 seconds of delivery confirmation.
```

**6. Partner Dependencies (Business-Level)**
```
WHEN FX quote is requested,
THE System SHALL obtain quote from FX provider with 90-second validity window
WITHIN quote request workflow.
```

**7. Business Constraints**
```
THE System SHALL enforce minimum transaction amount of $10
and maximum transaction determined by KYC tier
WITHIN regulatory compliance boundaries.
```

---

#### Edge Case Handling Rules

**Edge Case 1: Quantitative Thresholds - Customer SLA vs Technical Metrics**

✅ **INCLUDE (Customer-Facing SLAs)**:
```
WHEN transaction is submitted,
THE System SHALL complete end-to-end processing within 15 minutes
for 95% of transactions.
```

❌ **EXCLUDE (Technical Metrics)**:
- API latency <200ms (95th percentile)
- Database query time <50ms
- WebSocket connection establishment <500ms

**Rule**: Include business outcomes affecting customer experience or regulatory compliance; exclude technical performance metrics (move to SPEC/NFRs).

**Edge Case 2: State Machines and Business Processes**

✅ **INCLUDE (Business State Names)**:
```
WHEN transaction progresses,
THE System SHALL transition through states: INITIATED, FUNDED, COMPLETED, FAILED
WITHIN business process workflow.
```

❌ **EXCLUDE (State Management Implementation)**:
- Event handlers (on wallet_debited event, transition to FUNDED)
- State machine coordination logic
- Technical state transitions with database updates

**Rule**: Document business process states and flow; exclude technical state management implementation.

**Edge Case 3: ML Model Specifications (AI Agent Requirements)**

✅ **INCLUDE (Business-Level)**:
```
WHEN transaction is submitted,
THE System SHALL assess fraud risk using ML-based scoring model
and assign risk score 0-100 with decision rules:
  - Score 0-59: auto-approve
  - Score 60-79: manual review
  - Score 80-100: auto-decline
WITHIN 200ms inference latency at 95th percentile.
```

❌ **EXCLUDE (PRD-Level)**:
- Feature extraction code (transaction_amount, device_risk_score, etc.)
- Model hyperparameters (max_depth=5, learning_rate=0.1)
- Training pipeline specifications

**Rule**: Include business risk policies, scoring thresholds, and operational outcomes; exclude ML model architecture details.

---

#### Quick Self-Check Questions for EARS Writers

Before finalizing each EARS statement, ask:

1. **Could this requirement be implemented in multiple ways?** (✅ Appropriate abstraction)
   - vs. **Does this prescribe a specific implementation?** (❌ Too technical)

2. **Does this describe a business capability or outcome?** (✅ Business-level)
   - vs. **Does this describe HOW to build it technically?** (❌ Implementation-level)

3. **Would a solution architect understand the intent without implementation details?** (✅ Appropriate)
   - vs. **Does this require reading code or API docs to understand?** (❌ Too specific)

4. **Does this reference business rules, regulations, or SLAs?** (✅ Business-level)
   - vs. **Does this reference APIs, databases, or code?** (❌ Technical-level)

5. **Is this testable through BDD scenarios without knowing implementation?** (✅ Good EARS)
   - vs. **Does testing require knowing internal system architecture?** (❌ Too coupled)

---

#### Reference

For complete guidance on BRD-level content boundaries, see:
- [BRD Template - Appendix B (full version)](../BRD/BRD-TEMPLATE.md#appendix-b-prd-level-content-exclusions-critical-reference)
- [FR Examples Guide](../BRD/FR_EXAMPLES_GUIDE.md) - Examples of business-level requirements

---

### 5.5 Common Pitfalls

#### Pitfall 1: Vague Language
```
✗ The system should be reliable.
✓ THE System SHALL maintain 99.99% uptime during market hours (09:30-16:00 ET).
```

#### Pitfall 2: Missing Constraints
```
✗ WHEN data arrives, THE system SHALL process it.
✓ WHEN [EXTERNAL_DATA - e.g., customer data, sensor readings] arrives, THE system SHALL process and cache it WITHIN 50ms at p95 latency.
```

#### Pitfall 3: Compound Requirements
```
✗ WHEN market opens, THE system SHALL scan stocks, calculate [METRICS - e.g., performance indicators, quality scores], evaluate strategies,
   check risk limits, and place orders.
✓ [Split into 5 separate EARS statements, one per action]
```

#### Pitfall 4: Untestable Assertions
```
✗ THE System SHALL be easy to use.
✓ THE Dashboard SHALL display [RESOURCE_INSTANCE - e.g., database connection, workflow instance] summary within 3 clicks from login.
```

#### Pitfall 5: Ambiguous Subjects
```
✗ WHEN errors occur, retry should happen.
✓ IF the [EXTERNAL_INTEGRATION - e.g., third-party API, service provider] API returns HTTP 503, THE API Client SHALL retry with exponential backoff
   (initial delay 1s, max 3 attempts) WITHIN 30 seconds.
```

---

## 6. Quality Checklist

Before finalizing an EARS document, verify:

### 6.1 Format Compliance
- [ ] All Event-Driven requirements use WHEN-THE-SHALL-WITHIN format
- [ ] All State-Driven requirements use WHILE-THE-SHALL-WITHIN format
- [ ] All Unwanted Behavior requirements use IF-THE-SHALL-WITHIN format
- [ ] All Ubiquitous requirements use THE-SHALL-WITHIN format

### 6.2 Precision and Clarity
- [ ] No subjective language (fast, slow, reliable, easy, good)
- [ ] All thresholds are quantitative with units
- [ ] All timing constraints specify percentiles (p50, p95, p99)
- [ ] All system components are clearly identified

### 6.3 Atomicity
- [ ] Each statement represents one testable concept
- [ ] Compound requirements are split into separate statements
- [ ] Dependencies between statements are explicit
- [ ] No statements contain "and" clauses combining multiple actions

### 6.4 Testability
- [ ] Each statement can be translated to BDD scenario
- [ ] Success criteria are observable and measurable
- [ ] Failure modes are defined where applicable
- [ ] Verification method is clear

### 6.5 Completeness
- [ ] All source PRD/BRD requirements are covered
- [ ] All quality attributes (performance, security, reliability) are addressed
- [ ] All error conditions and edge cases are specified
- [ ] All state transitions and modes are defined

### 6.6 Traceability
- [ ] All upstream sources are linked (PRD, BRD, SYS)
- [ ] All downstream artifacts are referenced (REQ, SPEC, ADR)
- [ ] BDD scenarios are mapped to EARS statements
- [ ] Code implementation paths are documented

### 6.7 Consistency
- [ ] Terminology is consistent throughout document
- [ ] Requirements IDs follow naming convention
- [ ] Cross-references are valid and accessible
- [ ] No conflicting or contradictory requirements

---

## 7. Traceability

### 7.1 Upstream Sources

Document the business and product requirements that drive this EARS specification.

| Source Type | Document ID | Document Title | Relevant Sections | Relationship |
|-------------|-------------|----------------|-------------------|--------------|
| BRD | [BRD-NNN](../BRD/BRD-NNN_...md) | [Business requirement title] | Sections 2.4, 4.x | Business objectives driving these requirements |
| PRD | [PRD-NNN](../PRD/PRD-NNN_...md) | [Product requirement title] | Functional Requirements 4.x | Product features and user needs |
| SYS | [SYS-NNN](../SYS/SYS-NNN_...md) | [System requirement title] | System architecture section X | Technical system constraints |

**Key Business Objectives Satisfied**:
- BO-001: [Business objective description] → Satisfied by EARS statements [list statement IDs]
- BO-002: [Business objective description] → Satisfied by EARS statements [list statement IDs]

**Product Features Enabled**:
- Feature: [Feature name] → Specified by EARS statements [list statement IDs]
- Capability: [Capability name] → Specified by EARS statements [list statement IDs]

---

### 7.2 Downstream Artifacts

Document the technical specifications and designs derived from this EARS document.

#### 7.2.1 Architecture Decisions

| ADR ID | ADR Title | Decisions Driven by EARS | Relationship |
|--------|-----------|-------------------------|--------------|
| [ADR-NNN](../ADR/ADR-NNN_...md#ADR-NNN) | [Architecture decision title] | EARS statements [IDs] drive technology choice | This EARS requirement necessitates the architectural approach |
| [ADR-NNN](../ADR/ADR-NNN_...md#ADR-NNN) | [Architecture decision title] | EARS NFR-PERF-001 requires this pattern | Performance requirement drives architectural pattern |

#### 7.2.2 Atomic Requirements

| REQ ID | Requirement Title | Source EARS Statements | Relationship |
|--------|------------------|----------------------|--------------|
| [REQ-NNN](../REQ/.../REQ-NNN_...md#REQ-NNN) | [Detailed requirement] | Derived from EARS statements [IDs] | Detailed implementation requirement |
| [REQ-NNN](../REQ/.../REQ-NNN_...md#REQ-NNN) | [Detailed requirement] | Derived from EARS statements [IDs] | Detailed implementation requirement |

#### 7.2.3 Technical Specifications

| SPEC ID | Specification Title | EARS Requirements Implemented | Relationship |
|---------|-------------------|------------------------------|--------------|
| [SPEC-NNN](../SPEC/.../SPEC-NNN_...yaml) | [YAML specification] | Implements EARS statements [IDs] | Code generation specification |
| [SPEC-NNN](../SPEC/.../SPEC-NNN_...yaml) | [YAML specification] | Implements EARS statements [IDs] | Code generation specification |

|  |  | EARS Requirements Enforced | Relationship |
|-------------|---------------|---------------------------|--------------|

---

### 7.3 BDD Scenario Mapping

Map EARS statements to BDD scenarios for validation and acceptance testing.

| EARS Statement ID | EARS Statement Summary | BDD Feature File | BDD Scenario | Test Coverage |
|-------------------|----------------------|------------------|--------------|---------------|
| Event-001 | [EXTERNAL_DATA - e.g., customer data, sensor readings] processing latency | [BDD-NNN.feature](../BDD/BDD-NNN.feature#L10) | Scenario: Process [EXTERNAL_DATA - e.g., customer data, sensor readings] within latency target | Unit + Integration |
| State-001 | Maintenance mode behavior | [BDD-NNN.feature](../BDD/BDD-NNN.feature#L25) | Scenario: Reject trades during maintenance | Integration |
| Unwanted-001 | Rate limit error handling | [BDD-NNN.feature](../BDD/BDD-NNN.feature#L40) | Scenario: Handle API rate limit gracefully | Unit + Integration |
| Ubiquitous-001 | Data normalization | [BDD-NNN.feature](../BDD/BDD-NNN.feature#L55) | Scenario: Normalize [EXTERNAL_DATA_PROVIDER - e.g., Weather API, Stock Data API] to IB schema | Unit |

**BDD Coverage Summary**:
- Total EARS statements: [count]
- Statements with BDD scenarios: [count]
- Coverage percentage: [percentage]%
- Untested statements: [list IDs requiring BDD scenarios]

---

### 7.4 Code Implementation Paths

Document where EARS requirements are implemented in the codebase.

| EARS Statement ID | Primary Implementation | Supporting Modules | Test Files | Notes |
|-------------------|----------------------|-------------------|------------|-------|
| Event-001 | `src/market_data/handler.py:MarketDataHandler.process_tick()` | `src/cache/redis_client.py` | `tests/unit/test_market_data_handler.py` | Lines 142-178 |
| State-001 | `src/engine/state_machine.py:TradingEngine.set_maintenance_mode()` | `src/api/middleware.py` | `tests/integration/test_maintenance_mode.py` | Lines 89-115 |
| Unwanted-001 | `src/integrations/api_client.py:APIClient.handle_rate_limit()` | `src/utils/retry.py` | `tests/unit/test_api_client_errors.py` | Lines 203-245 |
| Ubiquitous-001 | `src/adapters/alpha_vantage_adapter.py:normalize_response()` | `src/schemas/market_data.py` | `tests/unit/test_alpha_vantage_adapter.py` | Lines 67-102 |

**Implementation Status**:
- Fully implemented: [count] requirements
- Partially implemented: [count] requirements
- Not implemented: [count] requirements
- Implementation blockers: [list any blockers]

---

### 7.5 Document Links and Cross-References

#### 7.5.1 Internal Document Structure

- **Anchors/IDs**: `#EARS-NNN` (for referencing this document)
- **Section References**: Use `#3.1` for Event-Driven Requirements section
- **Statement References**: Use unique IDs within document (e.g., `Event-001`, `State-001`)

#### 7.5.2 External References

**Product Strategy Documents**:
- [Strategy_Document: e.g., Product Strategy, Technical Vision](../../[domain_folder]/[strategy_doc].md) - [Relevant_Sections: e.g., Sections 2.1, 4.2]
- [Business_Rules: e.g., Domain Rules, Business Logic](../../[domain_folder]/[business_rules].md) - [Topic: e.g., Key calculations, Decision logic]

**Architecture Documentation**:
- [System_Architecture: e.g., System Design, Technical Blueprint](../../docs/[system_architecture].md) - [Topic: e.g., Component hierarchy, Communication patterns]
- [Data_Architecture: e.g., Data Model, Database Design](../../docs/[data_architecture].md) - [Topic: e.g., Data warehouse design, Schema definitions]

**Business Requirements**:
- [Business Requirements Document](../BRD/BRD-NNN_[project_name].md) - Source business objectives
- [Functional Requirements](../BRD/BRD-NNN_[project_name].md#appendix-i) - Detailed functional requirements

#### 7.5.3 Cross-Reference Validation

| Reference Type | Total Count | Valid Links | Broken Links | Last Validated |
|----------------|-------------|-------------|--------------|----------------|
| Upstream (BRD/PRD/SYS) | [count] | [count] | [count] | YYYY-MM-DD |
| Downstream (REQ/SPEC/ADR) | [count] | [count] | [count] | YYYY-MM-DD |
| BDD Scenarios | [count] | [count] | [count] | YYYY-MM-DD |
| Code Paths | [count] | [count] | [count] | YYYY-MM-DD |

---

### 7.6 Validation Evidence

Document evidence that EARS requirements have been implemented and validated correctly.

| EARS Statement ID | Validation Method | Evidence Location | Result | Date Validated |
|-------------------|------------------|-------------------|--------|----------------|
| Event-001 | Unit test execution | `tests/unit/test_market_data_handler.py::test_process_tick_latency` | PASS (p95=45ms) | YYYY-MM-DD |
| State-001 | Integration test | `tests/integration/test_maintenance_mode.py::test_reject_trades` | PASS | YYYY-MM-DD |
| Unwanted-001 | Manual API testing | `test_evidence/api_rate_limit_test_2024-01-15.log` | PASS | YYYY-MM-DD |
| NFR-PERF-001 | Load test | `load_tests/results/2024-01-15-market-data-latency.html` | PASS (p95=48ms) | YYYY-MM-DD |
| NFR-SEC-001 | Security audit | `audits/security_review_2024-Q1.pdf` | PASS | YYYY-MM-DD |

**Validation Status Summary**:
- Validated requirements: [count] / [total]
- Validation coverage: [percentage]%
- Failed validations: [list IDs with failures and remediation plans]
- Pending validations: [list IDs awaiting validation]

---

### 7.7 Traceability Tags

**Required Tags** (Cumulative Tagging Hierarchy - Layer 3):
```markdown
@brd: BRD-NNN:REQUIREMENT-ID
@prd: PRD-NNN:REQUIREMENT-ID
```

**Format**: `@artifact-type: DOCUMENT-ID:REQUIREMENT-ID`

**Layer 3 Requirements**: EARS must reference ALL upstream artifacts:
- `@brd`: Business Requirements Document(s)
- `@prd`: Product Requirements Document(s)

**Tag Placement**: Include tags in this section or at the top of the document (after Document Control).

**Example**:
```markdown
@brd: BRD-001:FR-030, BRD-001:NFR-006
@prd: PRD-003:FEATURE-002
```

**Validation**: Tags must reference existing documents and requirement IDs. Complete chain validation ensures all upstream artifacts are properly linked.

**Purpose**: Cumulative tagging enables complete traceability chains from business requirements through implementation. Each EARS document must include ALL upstream tags (BRD + PRD). See [TRACEABILITY.md](../TRACEABILITY.md#cumulative-tagging-hierarchy) for complete hierarchy documentation.

---

## 8. References

### 8.1 Internal Documentation

- [EARS Overview](README.md) - Guidelines for writing EARS documents
- [BRD Template](../BRD/BRD-TEMPLATE.md) - Business requirements structure
- [ADR Template](../ADR/ADR-TEMPLATE.md) - Architecture decision record format
- [BDD Feature Template](../BDD/BDD-TEMPLATE.feature) - Behavior-driven development scenarios
- [SPEC Template](../SPEC/SPEC-TEMPLATE.yaml) - Specification format

### 8.2 External Standards

- **EARS Notation**: Mavin, A. et al. (2009). "Easy Approach to Requirements Syntax (EARS)."
- **ISO/IEC/IEEE 29148:2018**: Systems and software engineering — Life cycle processes — Requirements engineering
- **RFC 2119**: Key words for use in RFCs to Indicate Requirement Levels (SHALL, SHOULD, MAY)

### 8.3 Domain References

[Add domain-specific references relevant to your project:]

- **[Domain_Standard: e.g., Healthcare, Finance, E-commerce]**: [Industry standards, regulatory frameworks]
- **[Domain_Practice: e.g., [RESOURCE_MANAGEMENT - e.g., capacity planning, quota management], Quality Assurance]**: [Best practice guidelines, industry resources]
- **[Regulatory_Reference: e.g., Compliance Standard, Legal Requirement]**: [Regulatory body, compliance framework]

### 8.4 Technology References

[Add technology-specific references relevant to your project:]

- **[Cloud_Platform: e.g., AWS, GCP, Azure]**: [Platform documentation, architecture framework]
- **[External_API: e.g., Payment Gateway, Data Provider]**: [API documentation, integration guides]
- **[Technology_Stack: e.g., Framework, Library, Service]**: [Technical documentation, best practices]

---

**Document Version**: 1.0.0
**Template Version**: 2.0
**Last Reviewed**: YYYY-MM-DD
**Next Review**: YYYY-MM-DD (recommend quarterly review for active EARS documents)
**Maintained By**: [Team/Role responsible for EARS maintenance]
