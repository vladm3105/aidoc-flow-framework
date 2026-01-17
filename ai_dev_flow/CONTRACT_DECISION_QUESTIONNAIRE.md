---
title: "Contract Decision Questionnaire"
tags:
  - framework-guide
  - shared-architecture
custom_fields:
  document_type: guide
  priority: shared
  development_status: active
---

# Contract Decision Questionnaire

**Version**: 1.0
**Purpose**: Interactive questionnaire for AI Assistants to determine if CTR (Contracts) layer is needed
**Target**: AI coding assistants (see AI_TOOL_OPTIMIZATION_GUIDE.md for tool-specific notes)
**Status**: Production

> **Note**: The artifact type for contracts is 'CTR', not 'CONTRACTS'. Files are stored in `09_CTR/` directory using dual-file format (`.md` + `.yaml`).

---

## Purpose

This questionnaire enables AI Coding Assistants to determine whether the CTR (Contracts) layer should be included in the project workflow. Contracts are optional and should only be created when external interfaces require formal specification.

---

## When to Run This Questionnaire

AI Assistant **MUST** run this questionnaire:
- After domain selection
- After folder structure creation
- Before creating first documents
- When user mentions APIs, events, or integrations

---

## Decision Questionnaire

### Primary Question

```
═══════════════════════════════════════════════════════════
              CONTRACT DECISION QUESTIONNAIRE
═══════════════════════════════════════════════════════════

Does this project require API contracts or interface definitions?

Select all that apply:

1. ☐ REST/GraphQL APIs (External HTTP endpoints)
2. ☐ Event Schemas (Pub/Sub, message queues, webhooks)
3. ☐ Data Contracts (Shared database schemas, data models between services)
4. ☐ RPC/gRPC Interfaces (Service-to-service communication)
5. ☐ WebSocket APIs (Real-time bidirectional communication)
6. ☐ File Format Specifications (CSV, JSON, XML exchange formats)
7. ☐ None - Internal logic only
8. ☐ Unsure - Need guidance

Enter selections (comma-separated, e.g., "1,2" or single "7"):
```

---

## Decision Matrix

| Selection | Interpretation | Include CTR? | Workflow |
|-----------|----------------|--------------|----------|
| 1, 2, 3, 4, 5, 6 | External interfaces exist | **YES** | REQ → IMPL → CTR → SPEC → TASKS |
| 7 | Internal logic only | **NO** | REQ → IMPL → SPEC → TASKS |
| 8 | Unsure | **Ask follow-up questions** | See Follow-Up section |

---

## Contract Type Mapping

### 1. REST/GraphQL APIs

**When to Create CTR**:
- Exposing HTTP endpoints for external consumption
- API consumed by frontend, mobile apps, partners
- Multi-service architecture with service boundaries

**CTR Format**:
- **Markdown (.md)**: Context, traceability, business rationale
- **YAML (.yaml)**: OpenAPI 3.x specification

**Example**:
```
CTR-012_data_service_api.md
CTR-012_data_service_api.yaml (OpenAPI 3.0)
```

**Skip CTR If**:
- Internal function calls within monolith
- Private helper functions
- No external consumers

---

### 2. Event Schemas

**When to Create CTR**:
- Publishing events to message provider (Kafka, RabbitMQ, AWS SNS/SQS)
- Webhook callbacks to external systems
- Event-driven microservices
- Event sourcing architecture

**CTR Format**:
- **Markdown (.md)**: Event context, producers, consumers
- **YAML (.yaml)**: AsyncAPI 2.x specification

**Example**:
```
CTR-015_operation_execution_event.md
CTR-015_operation_execution_event.yaml (AsyncAPI 2.6)
```

**Skip CTR If**:
- Internal domain events (not crossing service boundaries)
- Function callbacks within same process
- Private event handlers

---

### 3. Data Contracts

**When to Create CTR**:
- Shared database schemas between services
- Data lake/warehouse schemas
- Data exchange formats between teams
- API request/response models

**CTR Format**:
- **Markdown (.md)**: Schema purpose, owners, consumers
- **YAML (.yaml)**: JSON Schema or database DDL

**Example**:
```
CTR-018_position_data_model.md
CTR-018_position_data_model.yaml (JSON Schema)
```

**Skip CTR If**:
- Internal database tables (single service ownership)
- Temporary tables
- Private data structures

---

### 4. RPC/gRPC Interfaces

**When to Create CTR**:
- Service-to-service RPC calls
- gRPC APIs between microservices
- Thrift interfaces

**CTR Format**:
- **Markdown (.md)**: Service context, dependencies
- **YAML (.yaml)** or **.proto**: Protocol Buffers definition

**Example**:
```
CTR-020_risk_calculation_service.md
CTR-020_risk_calculation_service.proto (gRPC)
```

---

### 5. WebSocket APIs

**When to Create CTR**:
- Real-time bidirectional communication
- Live data feeds (market data, notifications)
- Collaborative features (multiplayer, shared editing)

**CTR Format**:
- **Markdown (.md)**: WebSocket protocol, message types
- **YAML (.yaml)**: Message schema definitions

**Example**:
```
CTR-025_realtime_market_feed.md
CTR-025_realtime_market_feed.yaml (Message schemas)
```

---

### 6. File Format Specifications

**When to Create CTR**:
- CSV/JSON/XML file exchange between systems
- Import/export file formats
- Batch data transfer protocols

**CTR Format**:
- **Markdown (.md)**: File format purpose, structure
- **YAML (.yaml)**: Schema definition (JSON Schema, XSD)

**Example**:
```
CTR-030_trade_blotter_export.md
CTR-030_trade_blotter_export.yaml (CSV schema)
```

---

## Follow-Up Questions (If User Selects "8 - Unsure")

### AI Assistant Should Ask:

```
Let me ask a few questions to determine if contracts are needed:

Question 1: External Consumers
  Does any other system, service, or application consume data from this project?
  a) Yes - External frontend (web, mobile)
  b) Yes - Other microservices
  c) Yes - Third-party integrations
  d) No - Self-contained internal logic
  → If a, b, or c: **Include CTR layer**

Question 2: Team Boundaries
  Do multiple teams work on different parts of this system?
  a) Yes - Frontend and backend teams
  b) Yes - Multiple backend service teams
  c) No - Single team, single service
  → If a or b: **Include CTR layer**

Question 3: Parallel Development
  Do you need to develop consuming services before producing services are complete?
  a) Yes - Need contract-first development
  b) No - Sequential development is acceptable
  → If a: **Include CTR layer**

Question 4: Interface Stability
  Do interfaces need versioning and backward compatibility?
  a) Yes - Public API with external consumers
  b) No - Internal implementation can change freely
  → If a: **Include CTR layer**
```

### Decision Logic

```python
# Pseudocode for decision logic
if any_external_consumers or multiple_teams or contract_first_needed or needs_versioning:
    include_ctr = True
    workflow = "REQ → IMPL → CTR → SPEC → TASKS"
else:
    include_ctr = False
    workflow = "REQ → IMPL → SPEC → TASKS"
```

---

## Decision Examples

### Example 1: Service Platform with REST API

**Scenario**: Algorithmic Service Platform with REST API for request submission

**Questions**:
1. External interfaces? **YES** - REST API for traders
2. Event schemas? **YES** - Order execution events
3. Data contracts? **YES** - Order and position data models

**Decision**: **Include CTR layer**
**Workflow**: `REQ → IMPL → CTR → SPEC → TASKS → Code`

**Contracts to Create**:
- CTR-01: request submission API (OpenAPI 3.0)
- CTR-02: Order Execution Event (AsyncAPI 2.x)
- CTR-03: Position Data Model (JSON Schema)

---

### Example 2: Internal Risk Calculator

**Scenario**: Risk calculation engine used only within risk service

**Questions**:
1. External interfaces? **NO** - Internal functions only
2. Event schemas? **NO** - No events published
3. Data contracts? **NO** - Private data structures

**Decision**: **Skip CTR layer**
**Workflow**: `REQ → IMPL → SPEC → TASKS → Code`

**Rationale**: Internal logic with no external consumers doesn't require formal contracts. SPEC alone is sufficient for code generation.

---

### Example 3: Microservices with Internal APIs

**Scenario**: Multi-service architecture with service-to-service communication

**Questions**:
1. External interfaces? **YES** - APIs between services
2. Multiple teams? **YES** - Each service owned by different team
3. Contract-first needed? **YES** - Parallel development

**Decision**: **Include CTR layer**
**Workflow**: `REQ → IMPL → CTR → SPEC → TASKS → Code`

**Contracts to Create**:
- CTR-NN: User Service API (OpenAPI 3.0)
- CTR-NN: Payment Service API (OpenAPI 3.0)
- CTR-NN: Notification Service Events (AsyncAPI 2.x)

---

## AI Assistant Processing Logic

### Implementation

```python
# Pseudocode for AI Assistant

def process_contract_decision(user_selections):
    # Parse selections
    selections = parse_selections(user_selections)

    # Decision logic
    if "7" in selections:  # None - internal only
        include_ctr = False
        message = "✓ No contracts needed. Workflow: REQ → IMPL → SPEC → TASKS"

    elif "8" in selections:  # Unsure
        run_follow_up_questions()
        return  # Wait for follow-up responses

    else:  # 1-6 selected (has external interfaces)
        include_ctr = True
        contract_types = map_selections_to_contract_types(selections)
        message = f"✓ Contracts needed. Contract types: {contract_types}"
        message += "\n✓ Workflow: REQ → IMPL → CTR → SPEC → TASKS"

    # Apply decision
    set_workflow_mode(include_ctr)
    print(message)

    # Proceed to next step
    if include_ctr:
        print("\nNext: Create IMPL (Implementation Plan) → then CTR (Contracts)")
    else:
        print("\nNext: Create IMPL (Implementation Plan) → then SPEC (Specifications)")

    return include_ctr


def map_selections_to_contract_types(selections):
    mapping = {
        "1": "REST/GraphQL APIs (OpenAPI)",
        "2": "Event Schemas (AsyncAPI)",
        "3": "Data Contracts (JSON Schema)",
        "4": "RPC/gRPC (Protocol Buffers)",
        "5": "WebSocket APIs (Message Schemas)",
        "6": "File Formats (Schema Definitions)"
    }
    return [mapping[sel] for sel in selections if sel in mapping]
```

---

## Workflow Adjustments

### With Contracts (CTR Layer Included)

```
BRD → PRD → EARS → BDD → ADR → SYS → REQ → IMPL → CTR → SPEC → TASKS → Code
                                                      ↑
                                            Contract-first design
                                            Enables parallel development
```

**Key Points**:
- IMPL identifies CTR documents to create
- CTR defines interface contracts (dual .md + .yaml files)
- SPEC implements interfaces defined in CTR
- Multiple teams can work in parallel once CTR approved

---

### Without Contracts (Skip CTR Layer)

```
BRD → PRD → EARS → BDD → ADR → SYS → REQ → IMPL → SPEC → TASKS → Code
                                                     ↑
                                          Direct to implementation SPEC
                                          Simpler workflow for internal logic
```

**Key Points**:
- IMPL directly identifies SPEC documents to create
- SPEC contains complete implementation details
- No formal interface contracts needed
- Faster workflow for internal-only features

---

## Summary Decision Table

| Project Characteristic | Include CTR? | Rationale |
|------------------------|--------------|-----------|
| Public REST API | **YES** | External consumers need stable contract |
| Internal function calls | **NO** | No external interface to document |
| Microservices (multi-team) | **YES** | Team boundaries require contracts |
| Monolith (single team) | **NO** | No team boundaries to coordinate |
| Event-driven architecture | **YES** | Event schemas shared across services |
| Batch processing | **NO** (unless file exchange) | Internal processing logic |
| Mobile/Web frontend | **YES** | Frontend consumes backend API |
| Background jobs | **NO** | Internal scheduled tasks |
| Third-party integrations | **YES** | Implementation contracts needed |
| Library/SDK | **YES** | Public API surface area |

---

## Contract-First Development Benefits

When CTR layer is included:

1. **Parallel Development**: Frontend and backend teams start simultaneously
2. **Contract Testing**: Validate implementations against schema
3. **Clear Boundaries**: Explicit service interfaces
4. **Versioning**: API version management
5. **Documentation**: Auto-generated API docs from OpenAPI/AsyncAPI
6. **Mocking**: Generate mock servers from contracts
7. **Validation**: Request/response validation against schema

---

## AI Assistant Confirmation Message

After decision, AI Assistant should confirm:

```
═══════════════════════════════════════════════════════════
              CONTRACT DECISION SUMMARY
═══════════════════════════════════════════════════════════

Decision: Contracts (CTR layer) INCLUDED ✓
  or
Decision: Contracts (CTR layer) SKIPPED ✓

Contract Types:
- REST API (OpenAPI 3.0)
- Event Schemas (AsyncAPI 2.x)

Workflow:
REQ → IMPL → CTR → SPEC → TASKS → Code
         or
REQ → IMPL → SPEC → TASKS → Code

Next Steps:
1. Create requirements (REQ documents)
2. Create implementation plan (IMPL document)
3. [If CTR included] Create contracts (CTR documents)
4. Create specifications (SPEC documents)
5. Create implementation tasks (TASKS documents)
6. Generate code from SPEC

═══════════════════════════════════════════════════════════
```

---

## References

- [AI_ASSISTANT_RULES.md](./AI_ASSISTANT_RULES.md#rule-5-contract-decision-questionnaire) - Rule 5: Contract Questionnaire
- [WHEN_TO_CREATE_IMPL.md](./WHEN_TO_CREATE_IMPL.md) - Implementation plan guidance
- [CTR-MVP-TEMPLATE.md](./09_CTR/CTR-MVP-TEMPLATE.md) - Contract template
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](./SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Complete workflow
- [DOMAIN_SELECTION_QUESTIONNAIRE.md](./DOMAIN_SELECTION_QUESTIONNAIRE.md) - Previous step

---

**End of Contract Decision Questionnaire**
