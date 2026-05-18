# TDD Creation Prompt
# Document Type: TDD (Test-Driven Development)
# Layer: 7
# Template: TDD-TEMPLATE.yaml

You are an expert in Test-Driven Development and software quality assurance.
Your task is to create a comprehensive TDD document that defines test cases, 
test thresholds, and execution order for a SPEC component.

## Context
- Upstream: SPEC (Layer 6), ADR (Layer 5), BDD (Layer 4)
- Downstream: IPLAN (Layer 8)
-Layer 7: TDD - Test case definitions from SPEC component contracts

## Instructions
Follow the TDD-TEMPLATE.yaml structure exactly. Create:

1. **Document Control**: Generate unique TDD ID, set status to "Draft", 
   calculate IPLAN-Ready score (target >=90/100)

2. **Test Pyramid**: Define 70/20/10 distribution (unit/integration/e2e)
   with flowchart visualization

3. **BDD Scenario Mapping**: Map all BDD scenarios to test types with
   file paths and status markers

4. **Test Case Definitions**: Create unit, integration, e2e, and optional
   security tests with full details per SPEC interfaces

5. **Thresholds**: Set coverage targets (unit >=90%, integration >=85%,
   e2e >=75% of happy paths)

6. **TDD Execution Order**: Declare Red-Green-Refactor sequence for AI

7. **Traceability**: Link to SPEC references, ADR references, and BDD references

## Output Requirements
- Use YAML format
- Include all required sections from template
- Add @tdd: TDD.NN tags for traceability
- Calculate readiness score based on completeness
- Do NOT include implementation code - only test specifications

## Success Criteria
- All 7 sections present and populated
- Test mapping covers all BDD scenarios
- Thresholds defined for each test type
- Execution order clearly declared
- Traceability links all upstream artifacts
