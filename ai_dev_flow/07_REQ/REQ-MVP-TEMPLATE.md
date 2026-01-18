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
  artifact_type: REQ
  layer: 7
  template_variant: mvp
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
---

<!--
AI_CONTEXT_START
Role: AI Requirements Engineer
Objective: Create a streamlined MVP Atomic Requirement.
Constraints:
- Define exactly ONE atomic requirement per document.
- 12 sections required (aligned with MVP requirements template).
- All 6 upstream traceability tags required (@brd, @prd, @ears, @bdd, @adr, @sys).
- Use @threshold tags for all quantitative values.
- SPEC-Ready/IMPL-Ready thresholds: ≥70% for MVP profile.
- Ensure SPEC-ready clarity (Inputs, Processing, Outputs).
- Use distinct P1/P2/P3 priorities.
- Do not create external references to non-existent files.
- Maintain single-file structure (no document splitting in MVP).
AI_CONTEXT_END
-->

**MVP Template** — Single-file, streamlined REQ for rapid MVP development.
 Use this template for MVP atomic requirements (10-20 core requirements).

**Validation Note**: MVP templates are intentionally streamlined and will show validation errors when run against full template validators (e.g., `validate_req_template.sh`). This is expected behavior. See `scripts/README.md` → "MVP Template Validation" for guidance.

  References: Schema `REQ_SCHEMA.yaml` | Rules `REQ_MVP_CREATION_RULES.md`, `REQ_MVP_VALIDATION_RULES.md` | Matrix `REQ-00_TRACEABILITY_MATRIX-TEMPLATE.md`


# REQ-NN: [RESOURCE_TYPE] [Requirement Title]

**MVP Scope**: This requirement document focuses on essential, SPEC-ready requirements for MVP delivery.

> **Resource Tags**: Replace `[RESOURCE_TYPE]` with project-specific resource classification (e.g., `[EXTERNAL_SERVICE_GATEWAY]`, `[HEALTH_CHECK_SERVICE]`, `[DATA_VALIDATION]`). See project ADR for resource taxonomy.

## 1. Document Control

| Item | Details |
|------|---------|
| **Status** | Draft / Review / Approved / Implemented |
| **Version** | 0.1.0 |
| **Date Created** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD |
| **Author** | [Author name] |
| **Priority** | P1 (Critical) / P2 (High) / P3 (Medium) |
| **Category** | Functional / Security / Performance |
| **Source Document** | [SYS-NN section X.Y.Z] |
| **Verification Method** | BDD / Unit Test / Integration Test |
| **Assigned Team** | [Team name] |
| **SPEC-Ready Score** | ✅ [XX]% (Target: ≥70%) |
| **IMPL-Ready Score** | ✅ [XX]% (Target: ≥70%) |
| **Template Version** | 1.0 |

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

---

## 8. Testing Requirements

### 8.1 Unit Tests

| Test Case | Input | Expected Output | Coverage |
|-----------|-------|-----------------|----------|
| [Happy path] | [valid input] | [expected result] | Core logic |
| [Edge case] | [boundary input] | [expected behavior] | Boundary |
| [Error case] | [invalid input] | [error response] | Error handling |

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

## 10. Traceability

### 10.1 Upstream References

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
```

> **Note**: Document references use dash notation (`ADR-NN`). Element references within documents use 4-segment dot notation (`BRD.NN.TT.SS`). Layer 7 (REQ) requires ALL 6 upstream tags.

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

## 12. Change History

| Date | Version | Change | Author |
|------|---------|--------|--------|
| YYYY-MM-DD | 0.1.0 | Initial draft | [Author] |

---

## Migration to Full REQ Template

### When to Migrate

- [ ] Requirement complexity requires 12-section format
- [ ] Need comprehensive interface protocols (Python)
- [ ] Full error catalog with state machines required
- [ ] SPEC generation requires maximum detail
- [ ] Compliance requires comprehensive test coverage

### Migration Steps

2. **Transfer core content**: Map MVP sections to full template
3. **Expand detailed sections**:
   - Full interface protocols (Python classes)
   - Complete data schemas (JSON, Pydantic, SQLAlchemy)
   - Comprehensive error catalogs with circuit breakers
   - Detailed configuration specifications
4. **Add missing sections**: EARS statements, verification matrix
5. **Update traceability**: Ensure SPEC documents reference new REQ
6. **Archive MVP version**: Move to archive with "superseded" note
7. **Run validation**: Execute `./scripts/validate_req_template.sh` on new document

### Section Mapping (MVP → Full)

| MVP Section | Full Template Section | Migration Notes |
|-------------|----------------------|-----------------|
| 1. Document Control | 1. Document Control | Add all 12 required fields |
| 2. Requirement Description | 1. Description | Expand EARS statements |
| 3. Functional Specification | 2. Functional Requirements | Add business rules |
| 4. Interface Definition | 3. Interface Specifications | Full Protocol/ABC classes |
| 5. Error Handling | 5. Error Handling Specifications | Full catalog + state machine |
| 6. Quality Attributes | 7. Quality Attributes | Add p50/p99 metrics |
| 7. Configuration | 6. Configuration Specifications | Full YAML schema |
| 8. Testing Requirements | 10. Verification Methods | Full test matrix |
| 9. Acceptance Criteria | 9. Acceptance Criteria | Expand to ≥15 criteria |
| 10. Traceability | 11. Traceability | Add matrix if complex |
| 11. Implementation Notes | 8. Implementation Guidance | Add patterns/DI |
| 12. Change History | 12. Change History | — |

---

**Document Version**: 0.1.0
**Template Version**: 1.0 (MVP)
**Last Updated**: 2026-01-13

---

> **MVP Template Notes**:
> - 12 sections aligned with full REQ template structure
> - Single file - no document splitting required
> - Focus on SPEC-ready, atomic requirements
> - All 6 upstream traceability tags required (Layer 7)
> - SPEC-Ready/IMPL-Ready thresholds: ≥70% (vs ≥90% for full template)
> - Uses `@threshold` tags for quantitative values
