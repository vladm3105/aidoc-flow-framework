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

## Position in Document Workflow

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
- **Input**: BRD, PRD, EARS (engineering requirements — event/state driven)
- **Output**: Gherkin feature files with executable acceptance tests
- **Consumer**: All downstream artifacts (REQ, SPEC, Code) must satisfy BDD scenarios

---

## Purpose

- Central index for Behavior-Driven Development (BDD) feature files
- Tracks allocation and sequencing for section-based files inside suite folders (`BDD-NN.SS_{slug}.feature`)
- Provides traceability from requirements to acceptance tests

## Allocation Rules

**Numbering**:
- Allocate suite numbers sequentially starting at `01` (e.g., `BDD-01`, `BDD-02`)
- Keep numbers stable once assigned (never reuse or renumber)
- Within each suite, allocate section numbers sequentially: `.1`, `.2`, `.3`, ...

**File Naming**:
- Format: `BDD-NN_{descriptive_slug}.feature`
- Slugs: short, descriptive, lower_snake_case
- Example: `BDD-042_risk_validation_service.feature`

**Content Requirements**:
- One primary feature/capability per file
- Include traceability tags: `@requirement:[REQ-NN]`, `@adr:[ADR-NN]`
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
@requirement:[REQ-NN](../07_REQ/.../REQ-NN.md)
@adr:[ADR-NN](../05_ADR/ADR-NN.md)
@spec:[SPEC-NN](../09_SPEC/.../SPEC-NN.yaml)
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

### Templates

- **[BDD-AGGREGATOR-TEMPLATE.feature](./BDD-AGGREGATOR-TEMPLATE.feature)**: Redirect stub when many subsections

## Planned

- Use this section to list BDD features planned but not yet created. Move rows to the appropriate functional area once created.

| ID | Suite/Feature | Source (03_EARS/REQ) | Priority | Notes |
|----|----------------|-------------------|----------|-------|
| BDD-XX | … | 03_EARS/REQ-YY | High/Med/Low | … |

### API Integrations

*[BDD scenarios for external service integrations will be listed here as they are created]*

<!-- EXAMPLE ENTRY FORMAT - Copy and modify for actual documents -->
<!--
- **BDD-01**: External Service Gateway Integration (./BDD-01_external_gateway_integration.feature)
  - **Requirements**: REQ.NN.EE.SS (Integration), REQ.NN.EE.SS (Gateway)
  - **ADRs**: ADR-NN (Architecture)
  - **Status**: Draft | Review | Approved
-->

### Resource Management

*[BDD scenarios for risk validation and controls will be listed here]*

<!-- EXAMPLE ENTRY FORMAT - Copy and modify for actual documents -->
<!--
- **BDD-02**: Resource Risk Limits Validation (./BDD-02_resource_risk_limits.feature)
  - **Requirements**: REQ.NN.EE.SS (Risk Limits)
  - **ADRs**: ADR-NN (Risk Parameters)
  - **Status**: Draft | Review | Approved
-->

### ML Models

*[BDD scenarios for machine learning model validation will be listed here]*

<!-- EXAMPLE ENTRY FORMAT - Copy and modify for actual documents -->
<!--
- **BDD-03**: System State Classifier Behavior (./BDD-03_system_state_classifier.feature)
  - **Requirements**: REQ.NN.EE.SS (ML Models)
  - **ADRs**: ADR-NN (ML Architecture)
  - **Status**: Draft | Review | Approved
-->

### Service Strategies

*[BDD scenarios for service strategies will be listed here]*

<!-- EXAMPLE ENTRY FORMAT - Copy and modify for actual documents -->
<!--
- **BDD-004**: [Service Strategy Execution](./BDD-004_service_strategy.feature)
  - **Requirements**: REQ.NN.EE.SS (Strategy)
  - **ADRs**: ADR-NN (Strategy Architecture)
  - **Status**: Draft | Review | Approved
-->

### Data Architecture

*[BDD scenarios for data management and analytics will be listed here]*

<!-- EXAMPLE ENTRY FORMAT - Copy and modify for actual documents -->
<!--
- **BDD-005**: [Analytics Pipeline](./BDD-005_analytics_pipeline.feature)
  - **Requirements**: REQ.NN.EE.SS (Analytics)
  - **ADRs**: ADR-NN (Data Architecture)
  - **Status**: Draft | Review | Approved
-->

### System Services

*[BDD scenarios for system-level services will be listed here]*

<!-- EXAMPLE ENTRY FORMAT - Copy and modify for actual documents -->
<!--
- **BDD-006**: [Monitoring and Alerting Service](./BDD-006_monitoring_alerting.feature)
  - **Requirements**: REQ.NN.EE.SS (Monitoring)
  - **ADRs**: ADR-NN (Monitoring Architecture)
  - **Status**: Draft | Review | Approved
-->

## Usage Guidelines

### Creating a New BDD Suite and Sections

1. **Assign Suite Number**: Choose next `BDD-NN` and suite slug (e.g., `knowledge_engine`)
2. **Create Suite Folder**: `04_BDD/BDD-NN_{suite_slug}`
3. **Create Index**: Copy `BDD-SECTION-0-TEMPLATE.md` to `04_BDD/BDD-NN_{suite_slug}/BDD-NN.0_index.md`
4. **Plan Sections**: Define `.1`, `.2`, `.3` sections and slugs
7. **Add Traceability Tags**: `@brd`, `@prd`, `@ears` at file top (Gherkin-native)
8. **Write Scenarios**: Given/When/Then; include primary, negative, edge, quality, integration, data-driven
9. **Use Thresholds**: Reference PRD threshold registry via `@threshold:` keys (no hardcoded numbers)
10. **Update Suite Index**: List sections, counts, and status in `BDD-NN.0_index.md`
11. **Update Global Index**: Add entry to this `BDD-00_index.md` under the appropriate area

### BDD File Structure (Section-Based)

```gherkin
@section: N.S
@parent_doc: BDD-NN
@index: BDD-NN.0_index.md
@brd:BRD.NN.EE.SS
@prd:PRD.NN.EE.SS
@ears:EARS.NN.EE.SS

Feature: BDD-NN.SS: [Clear feature description]
  As a [role]
  I want [capability]
  So that [business value]

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
| [BDD-NN.SS](../../04_BDD/BDD-NN_suite/BDD-NN.SS_section.feature) | Feature: Title | Primary functional criteria |
| [BDD-NN.SS](../../04_BDD/BDD-NN_suite/BDD-NN.SS_section.feature#scenario-1) | Scenario: Specific | Specific acceptance criterion |
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
| Requirements with BDD scenarios | 100% | [Pending] |
| BDD scenarios passing | 100% | [Pending] |
| Error conditions with negative tests | 100% | [Pending] |
| Integration points with scenarios | 100% | [Pending] |

### Validation Checklist

- [ ] All BDD files follow section-based naming: `04_BDD/BDD-NN_{suite}/BDD-NN.SS_{slug}.feature`
- [ ] All BDD files have traceability tags (@brd, @prd, @ears)
- [ ] All BDD files have upstream links (REQ, SYS, ADR)
- [ ] All BDD files have downstream links (SPEC, Code, TASKS)
- [ ] All requirements have corresponding BDD scenarios
- [ ] All BDD scenarios are executable (valid Gherkin syntax)
- [ ] This index is up-to-date with all BDD files

## Traceability

### Upstream Sources

| Source Type | Document ID | Relationship |
|-------------|-------------|--------------|
<!-- VALIDATOR:IGNORE-LINKS-START -->
| BRD | [BRD-NN](../01_BRD/BRD-NN.md) | Business requirements driving acceptance criteria |
<!-- VALIDATOR:IGNORE-LINKS-END -->
<!-- VALIDATOR:IGNORE-LINKS-START -->
| PRD | [PRD-NN](../02_PRD/PRD-NN.md) | Product requirements defining features |
<!-- VALIDATOR:IGNORE-LINKS-END -->
<!-- VALIDATOR:IGNORE-LINKS-START -->
| EARS | [EARS-NN](../03_EARS/EARS-NN.md) | Event-driven specifications for behavior |
<!-- VALIDATOR:IGNORE-LINKS-END -->

### Downstream Consumers

| Consumer Type | Document ID | Relationship |
|---------------|-------------|--------------|
<!-- VALIDATOR:IGNORE-LINKS-START -->
| ADR | [ADR-NN](../05_ADR/ADR-NN.md) | Architecture decisions must satisfy BDD scenarios |
<!-- VALIDATOR:IGNORE-LINKS-END -->
<!-- VALIDATOR:IGNORE-LINKS-START -->
| SYS | [SYS-NN](../06_SYS/SYS-NN.md) | System requirements traced from BDD scenarios |
<!-- VALIDATOR:IGNORE-LINKS-END -->
<!-- VALIDATOR:IGNORE-LINKS-START -->
| REQ | [REQ-NN](../07_REQ/.../REQ-NN.md) | Atomic requirements validated by BDD scenarios |
<!-- VALIDATOR:IGNORE-LINKS-END -->
<!-- VALIDATOR:IGNORE-LINKS-START -->
| SPEC | [SPEC-NN](../09_SPEC/.../SPEC-NN.yaml) | Technical SPEC implement BDD acceptance criteria |
<!-- VALIDATOR:IGNORE-LINKS-END -->
| Code | `src/module/component.py` | Implementation satisfies BDD tests |

## References

### Internal Links

- [BDD README](./README.md): Comprehensive BDD documentation and guidelines
- [BDD-MVP-TEMPLATE.feature](./BDD-MVP-TEMPLATE.feature): Template for creating new BDD feature files
- [AI Dev Flow Index](../index.md): Master index with complete traceability workflow

### External Links

- [Gherkin Reference](https://cucumber.io/docs/gherkin/reference/): Official Gherkin syntax documentation
- [Cucumber Best Practices](https://cucumber.io/docs/bdd/better-gherkin/): Writing better BDD scenarios
- [Pytest-BDD](https://pytest-bdd.readthedocs.io/): Python BDD testing framework

### Related Standards

- [REQ-MVP-TEMPLATE.md](../07_REQ/REQ-MVP-TEMPLATE.md): Requirements template (BDD validates requirements; full template archived)
- [SPEC-MVP-TEMPLATE.yaml](../09_SPEC/SPEC-MVP-TEMPLATE.yaml): Technical SPEC template (implements BDD scenarios)
- [TASKS-TEMPLATE.md](../11_TASKS/TASKS-TEMPLATE.md): Code generation template (generates BDD test code)

---

## Maintenance

**Last Updated**: 2025-11-02
**Maintained By**: AI Dev Flow Working Group
**Review Frequency**: Monthly or when new BDD files are added
**Version**: 1.0

**Update Process**:
1. When creating a new BDD file, add entry to appropriate functional area section
2. Include BDD-NN number, title, requirements, ADRs, and status
3. Update validation metrics as BDD tests are implemented
4. Ensure all cross-references are valid and up-to-date

---

**Index Version**: 1.0
**Template Compliance**: BDD-MVP-TEMPLATE.feature v1.0
**Traceability Standard**: AI Dev Flow Traceability v1.0
