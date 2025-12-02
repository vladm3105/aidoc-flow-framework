---
title: "BDD-000: BDD Index"
tags:
  - index-document
  - layer-4-artifact
  - shared-architecture
custom_fields:
  document_type: index
  artifact_type: BDD
  layer: 4
  priority: shared
---

# BDD Index

## resource in Development Workflow

**BDD (Behavior-Driven Development)** ← YOU ARE HERE

For the complete traceability workflow with visual diagram, see: [index.md - Traceability Flow](../index.md#traceability-flow)

**Quick Reference**:
```
... → EARS → **BDD** → ADR → SYS → REQ → ...
              ↑
      Testing Layer
      (Acceptance criteria and test scenarios)
```

**BDD Purpose**: Define acceptance criteria through executable scenarios
- **Input**: BRD, PRD, EARS (business requirements and event-driven SPEC)
- **Output**: Gherkin feature files with executable acceptance tests
- **Consumer**: All downstream artifacts (REQ, SPEC, Code) must satisfy BDD scenarios

---

## Purpose

- Central index for Behavior-Driven Development (BDD) feature files
- Tracks allocation and sequencing for `BDD-NNN_{slug}.feature` files
- Provides traceability from requirements to acceptance tests

## Allocation Rules

**Numbering**:
- Allocate sequentially starting at `001`
- Keep numbers stable once assigned (never reuse or renumber)
- Use three-digit format: BDD-001, BDD-002, etc.

**File Naming**:
- Format: `BDD-NNN_{descriptive_slug}.feature`
- Slugs: short, descriptive, lower_snake_case
- Example: `BDD-042_risk_validation_service.feature`

**Content Requirements**:
- One primary feature/capability per file
- Include traceability tags: `@requirement:[REQ-NNN]`, `@adr:[ADR-NNN]`
- Cross-link to upstream requirements (REQ, SYS, ADR)
- Cross-link to downstream implementations (SPEC, Code, TASKS)
- Each BDD file serves as acceptance criteria for requirements

**Gherkin Format**:
- Start with `Feature:` line (no `#` prefix)
- Include `Background:` section for common preconditions
- Use `Given/When/Then` syntax for scenarios
- Group scenarios: Success Path, Error Handling, Edge Cases

## Organization

**Functional Areas**:
- **API Integrations**: External service integrations ([EXTERNAL_SERVICE_GATEWAY], [EXTERNAL_DATA_PROVIDER - e.g., Weather API, item Data API])
- **resource management**: resource limits, risk validation, circuit breakers
- **ML Models**: [SYSTEM_STATE - e.g., operating mode, environment condition] classifier, sentiment analysis, ensemble signals
- **Service Strategies**: Standard operations, batch processing, resource collection balancing
- **Data Architecture**: Data ingestion, storage, analytics, correlation
- **System Services**: Authentication, monitoring, logging, configuration

**Tagging Strategy**:
```gherkin
@requirement:[REQ-NNN](../REQ/.../REQ-NNN.md)
@adr:[ADR-NNN](../ADR/ADR-NNN.md)
@spec:[SPEC-NNN](../SPEC/.../SPEC-NNN.yaml)
@priority:high|medium|low
@component:component_name
```

**Scenario Organization**:
1. **Background**: Common setup/preconditions
2. **Success Path Scenarios**: Happy path acceptance criteria
3. **Error Handling Scenarios**: Negative tests and error conditions
4. **Edge Case Scenarios**: Boundary conditions and corner cases
5. **Integration Scenarios**: Cross-component interactions

## Documents

### Template

- **[BDD-TEMPLATE.feature](./BDD-TEMPLATE.feature)**: Comprehensive template with examples and best practices

### API Integrations

*[BDD scenarios for external service integrations will be listed here as they are created]*

Example format:
- **BDD-001**: [[EXTERNAL_SERVICE - e.g., Payment Gateway, CRM System] Gateway Integration](./BDD-001_ib_gateway_integration.feature)
  - **Requirements**: REQ-026 ([EXTERNAL_DATA_PROVIDER - e.g., Weather API, item Data API] Integration), REQ-XXX ([EXTERNAL_SERVICE_GATEWAY])
  - **ADRs**: ADR-030 ([EXTERNAL_SERVICE_GATEWAY] Architecture)
  - **Status**: Pending

### resource management

*[BDD scenarios for risk validation and controls will be listed here]*

Example format:
- **BDD-002**: [resource Risk Limits Validation](./BDD-002_position_risk_limits.feature)
  - **Requirements**: REQ-XXX (Risk Limits)
  - **ADRs**: ADR-008 (Centralized Risk Parameters)
  - **Status**: Pending

### ML Models

*[BDD scenarios for machine learning model validation will be listed here]*

Example format:
- **BDD-003**: [[SYSTEM_STATE - e.g., operating mode, environment condition] Classifier Behavior](./BDD-003_system_state_classifier.feature)
  - **Requirements**: REQ-XXX (ML Models)
  - **ADRs**: ADR-XXX (ML Architecture)
  - **Status**: Pending

### Service Strategies

*[BDD scenarios for [DOMAIN_ACTIVITY - e.g., payment processing, content moderation] strategies will be listed here]*

Example format:
- **BDD-004**: [Service Strategy Execution](./BDD-004_service_strategy.feature)
  - **Requirements**: REQ-001 through REQ-007 (Covered Calls)
  - **ADRs**: ADR-015 (Covered Calls Strategy Agent)
  - **Status**: Pending

### Data Architecture

*[BDD scenarios for data management and analytics will be listed here]*

Example format:
- **BDD-005**: [BigQuery Analytics Pipeline](./BDD-005_bigquery_analytics.feature)
  - **Requirements**: REQ-XXX (Analytics)
  - **ADRs**: ADR-004 (BigQuery Architecture)
  - **Status**: Pending

### System Services

*[BDD scenarios for system-level services will be listed here]*

Example format:
- **BDD-006**: [Monitoring and Alerting Service](./BDD-006_monitoring_alerting.feature)
  - **Requirements**: REQ-XXX (Monitoring)
  - **ADRs**: ADR-010 (Monitoring Architecture), ADR-022 (Monitoring Agent)
  - **Status**: Pending

## Usage Guidelines

### Creating a New BDD Feature File

1. **Identify Next Number**: Check this index for the next available BDD-NNN number
2. **Choose Descriptive Slug**: Use lower_snake_case matching the feature name
3. **Copy Template**: `cp BDD-TEMPLATE.feature BDD-NNN_your_slug.feature`
4. **Fill Out Header**: Add traceability tags (@requirement, @adr, @spec)
5. **Write Feature Description**: Clear, concise feature title and context
6. **Define Scenarios**: Use Given/When/Then format for acceptance criteria
7. **Update This Index**: Add entry to appropriate functional area section
8. **Link Requirements**: Ensure corresponding REQ documents reference this BDD file

### BDD File Structure

```gherkin
# REQUIREMENTS VERIFIED:
#   - REQ-NNN: [Primary requirement description]
# TRACEABILITY:
#   Upstream: [REQ-NNN], [ADR-NNN]
#   Downstream: [SPEC-NNN], Code(module.component), [TASKS-NNN]

@requirement:[REQ-NNN]
@adr:[ADR-NNN]
@priority:high
Feature: [Clear feature description]
  [Business value context]
  As a [role]
  I want [capability]
  So that [benefit]

  Background:
    Given [common precondition]

  # SUCCESS PATH SCENARIOS
  Scenario: [Happy path test]
    Given [initial state]
    When [action]
    Then [expected outcome]

  # ERROR HANDLING SCENARIOS
  Scenario: [Error condition test]
    Given [error precondition]
    When [error trigger]
    Then [error handling behavior]

  # EDGE CASE SCENARIOS
  Scenario: [Boundary condition test]
    Given [edge case setup]
    When [boundary action]
    Then [boundary behavior]
```

### Linking BDD to Requirements

In REQ documents, reference BDD scenarios:
```markdown
#### Behavioral Specifications

| BDD ID | Scenario Title | Acceptance Criteria Validated |
|--------|----------------|-------------------------------|
| [BDD-NNN](../../BDD/BDD-NNN_slug.feature) | Feature: Title | Primary functional criteria |
| [BDD-NNN](../../BDD/BDD-NNN_slug.feature#scenario-1) | Scenario: Specific | Specific acceptance criterion |
```

### Running BDD Tests

BDD feature files are executable acceptance tests:

```bash
# Run all BDD tests
pytest tests/acceptance/

# Run specific feature
pytest tests/acceptance/test_bdd_NNN_slug.py

# Run with tags
pytest -m "requirement:REQ-042"
pytest -m "priority:high"
```

## Validation

### BDD Coverage Metrics

Track acceptance test coverage for requirements:

| Metric | Target | Current |
|--------|--------|---------|
| Requirements with BDD scenarios | 100% | [TBD] |
| BDD scenarios passing | 100% | [TBD] |
| Error conditions with negative tests | 100% | [TBD] |
| Integration points with scenarios | 100% | [TBD] |

### Validation Checklist

- [ ] All BDD files follow naming convention: `BDD-NNN_{slug}.feature`
- [ ] All BDD files have traceability tags (@requirement, @adr)
- [ ] All BDD files have upstream links (REQ, SYS, ADR)
- [ ] All BDD files have downstream links (SPEC, Code, TASKS)
- [ ] All requirements have corresponding BDD scenarios
- [ ] All BDD scenarios are executable (valid Gherkin syntax)
- [ ] This index is up-to-date with all BDD files

## Traceability

### Upstream Sources

| Source Type | Document ID | Relationship |
|-------------|-------------|--------------|
| BRD | [BRD-NNN](../BRD/BRD-NNN.md) | Business requirements driving acceptance criteria |
| PRD | [PRD-NNN](../PRD/PRD-NNN.md) | Product requirements defining features |
| EARS | [EARS-NNN](../EARS/EARS-NNN.md) | Event-driven specifications for behavior |

### Downstream Consumers

| Consumer Type | Document ID | Relationship |
|---------------|-------------|--------------|
| ADR | [ADR-NNN](../ADR/ADR-NNN.md) | Architecture decisions must satisfy BDD scenarios |
| SYS | [SYS-NNN](../SYS/SYS-NNN.md) | System requirements traced from BDD scenarios |
| REQ | [REQ-NNN](../REQ/.../REQ-NNN.md) | Atomic requirements validated by BDD scenarios |
| SPEC | [SPEC-NNN](../SPEC/.../SPEC-NNN.yaml) | Technical SPEC implement BDD acceptance criteria |
| Code | `src/module/component.py` | Implementation satisfies BDD tests |

## References

### Internal Links

- [BDD README](./README.md): Comprehensive BDD documentation and guidelines
- [BDD-TEMPLATE.feature](./BDD-TEMPLATE.feature): Template for creating new BDD feature files
- [AI Dev Flow Index](../index.md): Master index with complete traceability workflow

### External Links

- [Gherkin Reference](https://cucumber.io/docs/gherkin/reference/): Official Gherkin syntax documentation
- [Cucumber Best Practices](https://cucumber.io/docs/bdd/better-gherkin/): Writing better BDD scenarios
- [Pytest-BDD](https://pytest-bdd.readthedocs.io/): Python BDD testing framework

### Related Standards

- [REQ-TEMPLATE.md](../REQ/REQ-TEMPLATE.md): Requirements template (BDD validates requirements)
- [SPEC-TEMPLATE.yaml](../SPEC/SPEC-TEMPLATE.yaml): Technical SPEC template (implements BDD scenarios)
- [TASKS-TEMPLATE.md](../TASKS/TASKS-TEMPLATE.md): Code generation template (generates BDD test code)

---

## Maintenance

**Last Updated**: 2025-11-02
**Maintained By**: AI Dev Flow Working Group
**Review Frequency**: Monthly or when new BDD files are added
**Version**: 1.0

**Update Process**:
1. When creating a new BDD file, add entry to appropriate functional area section
2. Include BDD-NNN number, title, requirements, ADRs, and status
3. Update validation metrics as BDD tests are implemented
4. Ensure all cross-references are valid and up-to-date

---

**Index Version**: 1.0
**Template Compliance**: BDD-TEMPLATE.feature v1.0
**Traceability Standard**: AI Dev Flow Traceability v1.0
