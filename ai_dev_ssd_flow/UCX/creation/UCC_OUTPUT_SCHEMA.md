# UCC Output Schema Reference

This document defines the output format for **Unified Context Creation (UCC)** generated documents.

---

## Overview

UCC produces structured documents in Markdown with YAML frontmatter. Each document type has specific schema requirements based on its layer and artifact type.

---

## Common Output Structure

All UCC-generated documents share this structure:

```markdown
---
# YAML Frontmatter (required)
title: "{ARTIFACT_TYPE}: {Document Title}"
doc_id: "{ARTIFACT_TYPE}-{NN}"
version: "1.0.0"
status: draft
tags:
  - {artifact_type_lowercase}
  - layer-{N}
custom_fields:
  document_type: {artifact_type_lowercase}
  artifact_type: {ARTIFACT_TYPE}
  layer: {N}
  upstream_artifacts: [{LIST}]
  downstream_artifacts: [{LIST}]
  created_by: UCC
  creation_date: "{YYYY-MM-DD}"
  personas_applied: [{LIST}]
---

# {ARTIFACT_TYPE}-{NN}: {Document Title}

## Section 1: Overview
{Content per artifact type schema}

## Section 2: {Artifact-Specific}
{Content per artifact type schema}

...

## Appendix A: Traceability Matrix
{Cross-references to upstream/downstream}

## Appendix B: Revision History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | {DATE} | UCC | Initial draft |
```

---

## Layer-Specific Output Schemas

### Layer 1: BRD (Business Requirements Document)

```yaml
# Required Frontmatter
custom_fields:
  artifact_type: BRD
  layer: 1
  upstream_artifacts: [REF-XX]  # Reference documents
  downstream_artifacts: [PRD-XX]
  personas_applied: [Architect, Product Owner, Business Analyst, Strategist, Tech Lead]
```

**Required Sections**:
1. Executive Summary
2. Business Context
3. Stakeholder Analysis
4. Business Requirements (BRD.XX.XX.XX elements)
5. Constraints & Assumptions
6. Success Metrics
7. Risk Assessment

**Element ID Format**: `BRD.{doc}.{type}.{seq}`

---

### Layer 2: PRD (Product Requirements Document)

```yaml
custom_fields:
  artifact_type: PRD
  layer: 2
  upstream_artifacts: [BRD-XX]
  downstream_artifacts: [EARS-XX]
  personas_applied: [Product Owner, UX Strategist, Tech Lead, QA Lead, Architect]
```

**Required Sections**:
1. Product Overview
2. User Personas
3. User Stories
4. Feature Requirements (PRD.XX.XX.XX elements)
5. Acceptance Criteria
6. Non-Functional Requirements

**Element ID Format**: `PRD.{doc}.{type}.{seq}`

---

### Layer 3: EARS (Easy Approach to Requirements Syntax)

```yaml
custom_fields:
  artifact_type: EARS
  layer: 3
  upstream_artifacts: [PRD-XX]
  downstream_artifacts: [BDD-XX]
  personas_applied: [Requirements Specialist, Tech Lead, QA Lead]
```

**Required Sections**:
1. EARS Overview
2. Requirement Categories
3. EARS Statements (using EARS syntax patterns)
4. Traceability Matrix

**EARS Patterns**:
- Ubiquitous: "The [system] shall [action]"
- Event-Driven: "When [event], the [system] shall [action]"
- State-Driven: "While [state], the [system] shall [action]"
- Optional: "Where [feature included], the [system] shall [action]"
- Unwanted: "If [condition], then the [system] shall [action]"

---

### Layer 4: BDD (Behavior-Driven Development)

```yaml
custom_fields:
  artifact_type: BDD
  layer: 4
  upstream_artifacts: [EARS-XX]
  downstream_artifacts: [ADR-XX]
  personas_applied: [QA Lead, Tech Lead, Business Analyst]
```

**Required Format**: Gherkin syntax in `.feature` files

```gherkin
Feature: {Feature Name}
  As a {persona}
  I want {capability}
  So that {benefit}

  Background:
    Given {common precondition}

  @tag
  Scenario: {Scenario Name}
    Given {context}
    When {action}
    Then {expected outcome}
    And {additional verification}

  Scenario Outline: {Parameterized Scenario}
    Given {context with <param>}
    When {action with <param>}
    Then {expected outcome}

    Examples:
      | param | expected |
      | value1 | result1 |
      | value2 | result2 |
```

---

### Layer 5: ADR (Architecture Decision Record)

```yaml
custom_fields:
  artifact_type: ADR
  layer: 5
  upstream_artifacts: [BDD-XX, BRD-XX]
  downstream_artifacts: [SYS-XX]
  personas_applied: [Architect, Tech Lead, Integration Expert, Operator]
```

**Required Sections**:
1. Context
2. Decision
3. Consequences
4. Alternatives Considered
5. Implementation Notes

**Element ID Format**: `ADR.{doc}.{seq}`

---

### Layer 6: SYS (System Requirements)

```yaml
custom_fields:
  artifact_type: SYS
  layer: 6
  upstream_artifacts: [ADR-XX]
  downstream_artifacts: [REQ-XX]
  personas_applied: [Architect, Tech Lead, Operator, Integration Expert]
```

**Required Sections**:
1. System Overview
2. Component Specifications
3. Interface Definitions
4. Performance Requirements
5. Operational Requirements

**Element ID Format**: `SYS.{doc}.{type}.{seq}`
- Types: CP (Component), IF (Interface), DT (Data), PF (Performance), SC (Security), OP (Operational)

---

### Layer 7: REQ (Atomic Requirements)

```yaml
custom_fields:
  artifact_type: REQ
  layer: 7
  upstream_artifacts: [SYS-XX]
  downstream_artifacts: [CTR-XX, SPEC-XX]
  personas_applied: [Requirements Specialist, Tech Lead, Integration Expert]
```

**Required Format**: YAML requirement blocks

```yaml
req_id: REQ.{doc}.{type}.{seq}
title: "{Concise title}"
statement: |
  The system shall {single atomic requirement}.
type: functional|interface|performance|security
priority: P0|P1|P2
verification:
  method: test|inspection|analysis|demonstration
  criteria: "{How to verify}"
traces:
  upstream:
    - "@sys: SYS.XX.XX.XX"
  downstream:
    - "@spec: SPEC.XX.XX.XX"
rationale: "{Why this requirement exists}"
```

---

### Layer 8: CTR (Data Contracts)

```yaml
custom_fields:
  artifact_type: CTR
  layer: 8
  upstream_artifacts: [REQ-XX]
  downstream_artifacts: [SPEC-XX]
  personas_applied: [Architect, Tech Lead, Integration Expert]
```

**Required Format**: Dual-file (YAML schema + MD documentation)

**CTR-XX.yaml**:
```yaml
contract_id: CTR-{NN}
name: "{Contract Name}"
version: "1.0.0"
status: active
owner: "{Team/Service}"

schema:
  type: object
  required: [field1]
  properties:
    field1:
      type: string
      validation:
        pattern: "^[a-z]+$"

versioning:
  strategy: semantic
  breaking_changes: []

consumers: []
producers: []
```

---

### Layer 9: SPEC (Technical Specification)

```yaml
custom_fields:
  artifact_type: SPEC
  layer: 9
  upstream_artifacts: [REQ-XX, CTR-XX]
  downstream_artifacts: [TSPEC-XX, TASKS-XX]
  personas_applied: [Tech Lead, Architect, Operator, Integration Expert]
```

**Required Format**: YAML specification

```yaml
spec_id: SPEC-{NN}
title: "{Specification Title}"
version: "1.0.0"

components:
  - name: "{Component}"
    type: service|module|function
    interfaces:
      inputs: []
      outputs: []
    algorithm: |
      1. Step 1
      2. Step 2
    error_handling: []

performance:
  latency_p99: "{target}"
  throughput: "{rps}"

monitoring:
  metrics: []
  alerts: []
```

---

### Layer 10: TSPEC (Test Specification)

```yaml
custom_fields:
  artifact_type: TSPEC
  layer: 10
  upstream_artifacts: [SPEC-XX]
  downstream_artifacts: []
  personas_applied: [QA Lead, Tech Lead, Operator]
```

**Required Format**: YAML test specification

```yaml
tspec_id: TSPEC-{NN}
title: "{Test Specification Title}"
version: "1.0.0"

coverage:
  spec_reference: "@spec: SPEC-XX"
  requirements_tested: []

test_categories:
  unit: []
  integration: []
  e2e: []

test_data:
  fixtures: []
  factories: []

metrics:
  coverage_target: 80%
```

---

## Persona Attribution

Each UCC-generated section should include attribution:

```markdown
<!-- UCC Attribution -->
<!-- Section authored by: ARCHITECT, reviewed by: TECH_LEAD, QA_LEAD -->
```

Or in YAML:

```yaml
_ucc_metadata:
  primary_author: ARCHITECT
  reviewers: [TECH_LEAD, QA_LEAD]
  validation_status: approved
```

---

## Quality Indicators

UCC outputs include quality metrics:

```yaml
custom_fields:
  quality_metrics:
    completeness_score: 95
    traceability_coverage: 100
    persona_agreement: 5/5
    validation_status: passed
```

---

## Validation Hooks

UCC outputs are ready for UCR validation:

```yaml
custom_fields:
  validation_ready: true
  ucr_checkpoints:
    - structural_integrity
    - cross_reference_validity
    - element_id_compliance
    - traceability_completeness
```

---

## Usage Notes

1. **Version Control**: All UCC outputs should be committed with meaningful messages
2. **Review Workflow**: After UCC creation, run UCR for validation
3. **Iteration**: If UCR finds issues, use UCRem for remediation
4. **Traceability**: Maintain bidirectional links to upstream/downstream artifacts
