---
title: "REQ-MVP-TEMPLATE: Requirements Document (MVP)"
tags:
  - req-template
  - mvp-template
  - layer-7-artifact
  - document-template
  - shared-architecture
custom_fields:
  document_type: template
  instance_document_type: req-document
  deliverable_type: code  # Options: code, document, ux, risk, process - determines SPEC subtype
  artifact_type: REQ
  layer: 7
  template_profile: mvp
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  schema_version: "1.1"
  complexity: 1 # 1-5 scale
---
> ** Dual-Format Note**: 
> 
> This MD template is the **primary source** for human workflow. 
> - **For Autopilot**: See `REQ-MVP-TEMPLATE.yaml` (YAML template) 
> - **Shared Validation**: Both formats are validated by `REQ_MVP_SCHEMA.yaml` 
> - **Complete Explanation**: See [DUAL_MVP_TEMPLATES_ARCHITECTURE.md](../DUAL_MVP_TEMPLATES_ARCHITECTURE.md) for full comparison of formats, authority hierarchy, and when to use each. 
> - **Consistency Requirement**: `REQ-MVP-TEMPLATE.md` and `REQ-MVP-TEMPLATE.yaml` MUST remain consistent; keep changes synchronized.
> 
---

<!--
AI_CONTEXT_START
Role: AI Requirements Engineer
Objective: Create a streamlined MVP Atomic Requirement.
Constraints:
- Define exactly ONE atomic requirement per document.
- 11 sections required (aligned with MVP requirements template).
- All 6 upstream traceability tags required (@brd, @prd, @ears, @bdd, @adr, @sys).
- Use @threshold tags for all quantitative values.
- SPEC-Ready thresholds: ≥90% for MVP profile.
- Ensure SPEC-ready clarity (Inputs, Processing, Outputs).
- Use distinct P1/P2/P3 priorities.
- Do not create external references to non-existent files.
- Maintain single-file structure (no document splitting in MVP).
AI_CONTEXT_END
-->

**MVP Template** — Single-file, streamlined REQ for rapid MVP development.
 Use this template for MVP atomic requirements (10-20 core requirements).

**Validation Note**: This is the standard REQ template. Some legacy validators may report warnings - this is expected behavior. See `scripts/README.md` → "MVP Template Validation" for guidance.

  References: Schema `REQ_MVP_SCHEMA.yaml` | Rules `REQ_MVP_CREATION_RULES.md`, `REQ_MVP_VALIDATION_RULES.md` | Matrix `REQ-00_TRACEABILITY_MATRIX-TEMPLATE.md`


# REQ-NN: [RESOURCE_TYPE] [Requirement Title]

**MVP Scope**: This requirement document focuses on essential, SPEC-ready requirements for MVP delivery.

> **Resource Tags**: Replace `[RESOURCE_TYPE]` with project-specific resource classification (e.g., `[EXTERNAL_SERVICE_GATEWAY]`, `[HEALTH_CHECK_SERVICE]`, `[DATA_VALIDATION]`). See project ADR for resource taxonomy.

## 1. Document Control

| Item | Details |
|------|---------|
| **Status** | Draft / Review / Approved / Implemented |
| **Version** | 0.1.0 |
| **Date Created** | YYYY-MM-DDTHH:MM:SS |
| **Last Updated** | YYYY-MM-DDTHH:MM:SS |
| **Author** | [Author name] |
| **Priority** | P1 (Critical) / P2 (High) / P3 (Medium) |
| **Category** | Functional / Logic / API / UI / UX / Database / Config / Infra / FinOps / Security / Performance / Reliability / Scalability / Compliance |
| **Infrastructure Type** | Compute / Database / Storage / Network / Cache / Messaging / Deployment_Automation / Observability / Security / Cost / None |
| **Source Document** | [SYS-NN section X.Y.Z] |
| **Verification Method** | BDD / Unit Test / Integration Test |
| **Assigned Team** | [Team name] |
| **SPEC-Ready Score** | [PASS] [XX]% (Target: ≥90%) |
| **CTR-Ready Score** | [PASS] [XX]% (Target: ≥90%) |
| **Template Version** | 1.1 |

---

## 2. Requirement Description

### 2.1 Statement

**The system SHALL** [precise, atomic requirement statement that defines exactly one specific behavior].

### 2.2 Context

[1-2 paragraphs: Why this requirement exists and what problem it solves]

### 2.3 Use Case

**Primary Flow**:
1. [Actor] initiates [action/trigger]
2. System validates [precondition]
3. System executes [core behavior]
4. System returns [outcome]

**Error Flow**:
- When [error condition], system SHALL [error behavior]

---

## 3. Functional Specification

### 3.1 Core Functionality

**Required Capabilities**:
- [Capability 1]: [Specific behavior with measurable outcome]
- [Capability 2]: [Specific behavior with measurable outcome]

### 3.2 Business Rules

**ID Format**: `REQ.NN.21.SS` (Validation Rule)

| Rule ID | Condition | Action |
|---------|-----------|--------|
| REQ.NN.21.01 | IF [condition] | THEN [action/outcome] |
| REQ.NN.21.02 | IF [condition] | THEN [action/outcome] |

### 3.3 Input/Output Specification

**Inputs**:

| Parameter | Type | Required | Validation | Description |
|-----------|------|----------|------------|-------------|
| [param1] | [string/int/etc] | Yes/No | [rules] | [what it is] |
| [param2] | [string/int/etc] | Yes/No | [rules] | [what it is] |

**Outputs**:

| Field | Type | Description |
|-------|------|-------------|
| [field1] | [string/int/etc] | [what it contains] |
| [field2] | [string/int/etc] | [what it contains] |

### 3.4 Interface Protocol

> **Note**: Define the interface contract as a Python `Protocol` or Abstract Base Class (ABC). This drives the SPEC generation.
> **Linting Reminder**: In Protocol/ABC examples, prefer `raise NotImplementedError("method not implemented")` over `pass` or `...` so stubs are explicit contracts and not mistaken for incomplete code.

```python
from typing import Protocol, List, Optional
from datetime import datetime

class ResourceStrategy(Protocol):
    """Interface for [Resource Name] operations."""

    def execute_operation(self, param1: str) -> bool:
        """
        Execute the main operation.
        
        Args:
            param1: Description of parameter.
            
        Returns:
            bool: True if successful.
            
        Raises:
            ResourceError: If operation fails.
        """
        ...

    async def validate_state(self) -> bool:
        """Check if resource is in valid state."""
        ...
```

---

## 4. Interface Definition

### 4.1 API Contract (if applicable)

> **Note**: This section provides JSON wire format examples. If using Section 4.2 Pydantic schemas with `.model_json_schema()`, this section is optional and may be omitted to avoid redundancy with Section 3.3 Input/Output.

**Endpoint**: `[METHOD] /api/v1/[resource]`

**Request**:
```json
{
  "field1": "value",
  "field2": 123
}
```

**Response (Success)**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "result": "value"
  }
}
```

**Response (Error)**:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Description"
  }
}
```

### 4.2 Data Schema

```python
from pydantic import BaseModel, Field
from datetime import datetime

class RequestModel(BaseModel):
    """Request data structure."""
    field1: str = Field(..., min_length=1, max_length=100)
    field2: int = Field(..., ge=0)

class ResponseModel(BaseModel):
    """Response data structure."""
    id: str
    result: str
    timestamp: datetime
```

---

## 5. Error Handling

### 5.1 Error Catalog

| Error Code | HTTP Status | Condition | User Message | System Action |
|------------|-------------|-----------|--------------|---------------|
| [ERR_001] | 400 | Invalid input | [Message] | Log, return error |
| [ERR_002] | 404 | Resource not found | [Message] | Log, return error |
| [ERR_003] | 500 | Processing failed | [Message] | Log, alert, retry |

### 5.2 Recovery Strategy

| Error Type | Retry? | Fallback | Alert |
|------------|--------|----------|-------|
| Validation error | No | Return error | No |
| Transient failure | Yes (3x) | Queue/Cache | After retries |
| Permanent failure | No | Graceful error | Yes |

### 5.3 Exception Definitions

```python
class ResourceError(Exception):
    """Base exception for [Resource Name] errors."""
    pass

class ValidationError(ResourceError):
    """Raised when input validation fails."""
    pass

class StateError(ResourceError):
    """Raised when resource is in invalid state."""
    pass

class UpstreamError(ResourceError):
    """Raised when upstream service fails."""
    pass
```

---

## 6. Quality Attributes

**ID Format**: `REQ.NN.02.SS` (Quality Attribute)

### 6.1 Performance (REQ.NN.02.01)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response time (p95) | < @threshold: PRD.NN.perf.api.p95_latency | APM traces |
| Throughput | @threshold: PRD.NN.perf.api.throughput | Load test |

> **Note**: Use `@threshold` tags for all quantitative values. Reference centralized threshold registry in PRD.

### 6.2 Security (REQ.NN.02.02)

- [ ] Input validation: All inputs validated
- [ ] Authentication: [Required/Optional]
- [ ] Authorization: [Role-based check]
- [ ] Data protection: [PII handling]

### 6.3 Reliability (REQ.NN.02.03)

- Error rate: < @threshold: PRD.NN.reliability.error_rate
- Idempotency: [Required for POST/PUT operations]

---

## 7. Configuration

### 7.1 Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| [CONFIG_1] | [type] | [default] | [what it controls] |
| [CONFIG_2] | [type] | [default] | [what it controls] |

### 7.2 Feature Flags (if applicable)

| Flag | Default | Description |
|------|---------|-------------|
| [FLAG_NAME] | false | [When to enable] |

### 7.3 Configuration Schema

```yaml
resource_config:
  enabled: true
  timeout_ms: 5000  # @threshold: PRD.NN.timeout.default
  retry_policy:
    max_attempts: 3
    backoff_factor: 1.5
  feature_flags:
    enable_experimental: false
```

---

## 8. Testing Requirements

### 8.1 Unit Tests

> **Define WHAT to test before HOW.** These tests drive the SPEC interface design.
> **IMPORTANT:** Check (and recreate if needed) this list during every validation.
> **REQUIRED:** Use category prefixes: `[Logic]`, `[State]`, `[Validation]`, and `[Edge]`.

| Test Case | Input | Expected Output | Coverage |
|-----------|-------|-----------------|----------|
| **[Logic] Fee Calc** | `amount=100, tier='basic'` | `fee=1.50` | REQ.NN.21.01 |
| **[State] Circuit Trip** | `fail_count=5` | `State=OPEN` | REQ.NN.02.03 |
| **[Validation] Bad Input** | `amount=-1` | `Error: INVALID_AMOUNT` | REQ.NN.05.01 |
| **[Edge] Boundary** | `amount=MAX_INT` | `Success` | Overflow check |

### 8.2 Integration Tests

- [ ] API endpoint responds correctly
- [ ] Database operations work
- [ ] External service integration works

### 8.3 BDD Scenarios

**Feature**: [Feature name]
**File**: `04_BDD/BDD-NN_{suite}/BDD-NN.SS_{slug}.feature`

| Scenario | Priority | Status |
|----------|----------|--------|
| [Scenario 1] | P1 | [Pending/Passed] |
| [Scenario 2] | P1 | [Pending/Passed] |

---

## 9. Acceptance Criteria

**ID Format**: `REQ.NN.06.SS` (Acceptance Criteria)

### 9.1 Functional Acceptance

> **Note**: Each criterion should trace to one or more BDD scenarios in Section 8.3. Use `@bdd` tags for traceability.

| Criteria ID | Criterion | Measurable Outcome | Status |
|-------------|-----------|-------------------|--------|
| REQ.NN.06.01 | [Criterion 1] | [Measurable outcome] | [ ] |
| REQ.NN.06.02 | [Criterion 2] | [Measurable outcome] | [ ] |
| REQ.NN.06.03 | [Criterion 3] | [Measurable outcome] | [ ] |

### 9.2 Quality Acceptance

> **Note**: Reference Section 6 Quality Attributes for target values. Use `@threshold` tags to avoid duplication.

| Criteria ID | Criterion | Target | Status |
|-------------|-----------|--------|--------|
| REQ.NN.06.04 | Performance target | @threshold: REQ.NN.02.01 | [ ] |
| REQ.NN.06.05 | Security | No critical vulnerabilities | [ ] |
| REQ.NN.06.06 | Test coverage | ≥ @threshold: PRD.NN.quality.coverage | [ ] |

---

---

## 10. Traceability

### 10.1 Upstream Sources

| Source Type | Document ID | Element Reference | Relationship |
|-------------|-------------|-------------------|--------------|
| BRD | BRD-NN | BRD.NN.TT.SS | Primary business need |
| PRD | PRD-NN | PRD.NN.TT.SS | Product requirement |
| EARS | EARS-NN | EARS.NN.TT.SS | Formal requirement |
| BDD | BDD-NN | BDD.NN.TT.SS | Acceptance test |
| ADR | ADR-NN | — | Architecture decision |
| SYS | SYS-NN | SYS.NN.TT.SS | System requirement |

> **Complete Upstream Chain**: Layer 7 (REQ) requires references to all 6 upstream artifact types.

### 10.2 Downstream Artifacts

| Artifact | Status | Relationship |
|----------|--------|--------------|
| CTR-NN | TBD | API contract (if external interface) |
| SPEC-NN | TBD | Technical specification |
| TASKS-NN | TBD | Implementation tasks |

### 10.3 Traceability Tags

```markdown
@brd: BRD.NN.TT.SS
@prd: PRD.NN.TT.SS
@ears: EARS.NN.TT.SS
@bdd: BDD.NN.TT.SS
@adr: ADR-NN
@sys: SYS.NN.TT.SS
@ctr: CTR-NN          # If API contract exists
@spec: SPEC-NN         # Technical specification
@tasks: TASKS-NN       # Implementation tasks
@sys: SYS-NN          # System deployment requirements
```

> **Note**: Document references use dash notation (`ADR-NN`). Element references within documents use 4-segment dot notation (`BRD.NN.TT.SS`). Layer 7 (REQ) requires ALL 6 upstream tags. Deployment requirements are system-level concerns defined in SYS-NN documents.

**Downstream Traceability Tags** (for generated artifacts):

```markdown
@ctr: CTR-NN            # If API contract exists
@spec: SPEC-NN          # Technical specification
@tasks: TASKS-NN        # Implementation tasks
@deployment: scripts/   # Deployment scripts directory
@ansible: ansible/      # Ansible playbooks directory
@iac: terraform/        # IaC templates directory
@config_file_type: yaml # Configuration file format (yaml/json/toml)
@source_code: [URL, PATH]     # Link to generated source code repo
```

> **Note**: Downstream tags reference generated artifacts (scripts, playbooks, IaC) for bidirectional traceability.

### 10.4 Cross-Links (Same-Layer)

Use cross-links to make dependencies and discoverability AI-friendly:

```markdown
@depends: REQ-NN   # Hard prerequisite requirements (must be satisfied first)
@discoverability: REQ-NN (short rationale); REQ-NN (short rationale)
```

- `@depends` captures sequencing/blocking relationships across REQs.
- `@discoverability` lists related REQs with a one-phrase rationale to aid search/ranking.
- Avoid legacy "See also" strings; use the tags above for structured linkage.

---

## 11. Implementation Notes

### 11.1 Technical Approach

[Brief description of recommended implementation approach]

### 11.2 Code Location

- **Primary**: `src/[module]/[component].py`
- **Tests**: `tests/[module]/test_[component].py`

### 11.3 Dependencies

| Package/Service | Version | Purpose |
|-----------------|---------|---------|
| [dependency1] | [version] | [why needed] |
| [dependency2] | [version] | [why needed] |

---

<!-- Change History section is intentionally omitted for MVP to keep 11-section structure. -->

---

### 11.4 MVP Lifecycle (MVP → PROD → NEW MVP)

> **Lifecycle Principle**: Each REQ represents requirements for ONE iteration cycle. New requirements require a NEW REQ document.

#### 11.4.1 Lifecycle Phases

| Phase | Duration | Focus | REQ Output |
|-------|----------|-------|------------|
| **MVP** | 1-2 weeks | Atomic requirements (5-15) | This REQ → SPEC → Implementation |
| **PROD** | 30-90 days | Operate, validate requirements, collect feedback | Implementation outcomes |
| **NEW MVP** | 1-2 weeks | Next requirement set | Create REQ-02, REQ-03, etc. |

#### 11.4.2 When to Create a New REQ

- [ ] Current REQ requirements are implemented and validated
- [ ] New atomic requirements identified for next iteration
- [ ] Interface changes required for new features
- [ ] Business case for new requirements approved

#### 11.4.3 Cross-REQ Traceability

When creating the next REQ iteration:

1. **Link to previous cycle**: Add `@depends: REQ-01` in Traceability section
2. **Reference implementation outcomes**: Include validation data from previous cycle
3. **Supersedes pattern**: Use when replacing a previous requirement entirely
4. **Update index**: Add new REQ to REQ-00_index.md with cross-references

**Note**: There is no "full REQ" template. This MVP template IS the standard. Expansion happens through NEW REQs, not template migration.

---

**Document Version**: 0.1.0
**Template Version**: 1.0 (MVP)
**Last Updated**: 2026-02-26T00:00:00

---

> **MVP Template Notes**:
> - 11 sections - this is the standard REQ MVP template structure
> - Single file - no document splitting required
> - Focus on SPEC-ready, atomic requirements
> - All 6 upstream traceability tags required (Layer 7)
> - SPEC-Ready/CTR-Ready thresholds: ≥90%
> - Uses `@threshold` tags for quantitative values
> - **Lifecycle**: MVP → PROD → NEW MVP (no separate "full REQ" template)
