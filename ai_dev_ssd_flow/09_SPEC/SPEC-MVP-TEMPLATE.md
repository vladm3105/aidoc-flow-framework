---
title: "SPEC-TEMPLATE: Technical Specification (MVP)"
tags:
  - spec-template
  - mvp-template
  - layer-9-artifact
  - shared-architecture
  - document-template
custom_fields:
  document_type: template
  artifact_type: SPEC
  layer: 9
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  complexity: 2
  template_for: technical-specification
  schema_reference: "SPEC_MVP_SCHEMA.yaml"
  schema_version: "1.0"
---

> **Dual-Format Note**:
>
> This MD template is the **primary source** for human workflow.
> - **For Autopilot**: See `SPEC-MVP-TEMPLATE.yaml` (YAML template)
> - **Shared Validation**: Both formats are validated by `SPEC_MVP_SCHEMA.yaml`
> - **Complete Explanation**: See [DUAL_MVP_TEMPLATES_ARCHITECTURE.md](../DUAL_MVP_TEMPLATES_ARCHITECTURE.md)

---

> **Document Authority**: This is the **PRIMARY STANDARD** for SPEC structure.
> Schema: `SPEC_MVP_SCHEMA.yaml v1.0` | Creation Rules: `SPEC_MVP_CREATION_RULES.md` | Validation Rules: `SPEC_MVP_VALIDATION_RULES.md`

<!--
AI_CONTEXT_START
Role: AI Technical Architect
Objective: Create complete technical specifications for component implementation.
Constraints:
- One SPEC per component/module.
- Define HOW to implement (not just WHAT).
- 7 required sections.
- Required traceability tags: @req, @ctr, @adr.
- TASKS-Ready threshold: >= 90%.
- Include pseudocode for complex logic.
- Explicit state machines for stateful components.
- Define all error handling and edge cases.
AI_CONTEXT_END
-->

**MVP Template** - Single-file technical specification for component implementation.

References: Schema `SPEC_MVP_SCHEMA.yaml` | Rules `SPEC_MVP_CREATION_RULES.md`, `SPEC_MVP_VALIDATION_RULES.md` | Matrix `SPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md`

# SPEC-NN: [Component Name] Technical Specification

**MVP Scope**: Technical specification for [Component Name] implementation.

## 1. Document Control

| Item | Details |
|------|---------|
| **Status** | Draft / Review / Approved / Implemented |
| **Version** | 1.0.0 |
| **Date Created** | YYYY-MM-DDTHH:MM:SS |
| **Last Updated** | YYYY-MM-DDTHH:MM:SS |
| **Author** | [Author name] |
| **Component** | [Component/module name] |
| **TASKS-Ready Score** | [XX]% (Target: >= 90%) |
| **Template Version** | 1.0 |

### 1.1 Revision History

| Version | Date | Author | Changes | Approver |
|---------|------|--------|---------|----------|
| 1.0.0 | YYYY-MM-DD | [Author] | Initial draft | |

---

## 2. Traceability

> **UPSTREAM ARTIFACT REQUIREMENT**: Reference only existing documents. Do NOT create phantom references.

### 2.1 Upstream Sources

| Type | ID | Title | Relevant Sections |
|------|-----|-------|-------------------|
| REQ | REQ-NN | [Requirements title] | [Sections] |
| CTR | CTR-NN | [Contract title] | [Sections] |
| ADR | ADR-NN | [Architecture decision] | [Sections] |

### 2.2 Downstream Consumers

| Type | ID | Purpose |
|------|-----|---------|
| TASKS | TASKS-NN | Implementation tasks |
| TSPEC | TSPEC-NN | Test specifications |

---

## 3. Component Overview

### 3.1 Summary

[Single-sentence description of component purpose, scope, and value proposition.]

### 3.2 Purpose

[What this component does and why it exists. 2-3 sentences.]

### 3.3 Scope

**In Scope**:
- [Capability 1]
- [Capability 2]

**Out of Scope**:
- [Exclusion 1]
- [Exclusion 2]

### 3.4 Key Design Decisions

| Decision | Rationale | ADR Reference |
|----------|-----------|---------------|
| [Decision 1] | [Why] | ADR-NN |

---

## 4. Technical Design

### 4.1 Architecture

```
[ASCII diagram or description of component architecture]
```

### 4.2 Dependencies

| Dependency | Type | Version | Purpose |
|------------|------|---------|---------|
| [Package] | External | ^X.Y.Z | [Purpose] |
| [Service] | Internal | N/A | [Purpose] |

### 4.3 Interfaces

#### 4.3.1 Public API

```python
# Interface definition
class ComponentInterface(Protocol):
    def method_name(self, param: Type) -> ReturnType:
        """Method description.

        Args:
            param: Parameter description.

        Returns:
            Return value description.

        Raises:
            ErrorType: When condition.
        """
        ...
```

#### 4.3.2 Internal Interfaces

[List internal interfaces with dependencies]

### 4.4 Data Models

```python
@dataclass
class EntityName:
    """Entity description."""
    field_name: Type  # Field description
```

---

## 5. Implementation Logic

### 5.1 Core Algorithm

```python
# Pseudocode for main algorithm
def core_algorithm(input: InputType) -> OutputType:
    """
    Step 1: Validate input
    Step 2: Process data
    Step 3: Return result
    """
    # Validation
    if not validate(input):
        raise ValidationError("Invalid input")

    # Processing
    result = process(input)

    # Return
    return result
```

### 5.2 State Machine (if applicable)

| Current State | Event | Next State | Side Effects |
|---------------|-------|------------|--------------|
| INITIAL | initialize | READY | Load config |
| READY | process | PROCESSING | Start work |
| PROCESSING | complete | READY | Emit result |
| * | error | ERROR | Log, notify |

### 5.3 Error Handling

| Error Code | Condition | Recovery | User Message |
|------------|-----------|----------|--------------|
| ERR_001 | Invalid input | Reject with details | "Invalid input: {reason}" |
| ERR_002 | Timeout | Retry with backoff | "Operation timed out" |

---

## 6. Configuration

### 6.1 Environment Variables

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `CONFIG_VAR` | string | Yes | N/A | Description |

### 6.2 Configuration Schema

```yaml
component:
  setting_name: value  # Description
  nested:
    sub_setting: value
```

---

## 7. Non-Functional Requirements

### 7.1 Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response time | < 100ms p95 | Load testing |
| Throughput | > 1000 req/s | Benchmark |

### 7.2 Security

| Requirement | Implementation |
|-------------|----------------|
| Authentication | [Method] |
| Authorization | [Method] |
| Data protection | [Method] |

### 7.3 Observability

| Type | Implementation |
|------|----------------|
| Logging | Structured JSON logs |
| Metrics | [Metrics system] |
| Tracing | [Tracing system] |

---

## 8. Quality Gates

### 8.1 TASKS-Ready Checklist

| Criterion | Status | Notes |
|-----------|--------|-------|
| All interfaces defined | [ ] | |
| All dependencies listed | [ ] | |
| Core logic pseudocoded | [ ] | |
| Error handling specified | [ ] | |
| Configuration documented | [ ] | |
| NFRs defined | [ ] | |
| Traceability complete | [ ] | |

### 8.2 TASKS-Ready Score Calculation

- Total criteria: 7
- Met criteria: [X]
- Score: [X/7 * 100]%
- Target: >= 90%

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| [Term] | [Definition] |

## Appendix B: References

- [Reference 1]
- [Reference 2]
