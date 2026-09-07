# TDD Review Prompt

# Document Type: TDD (Test-Driven Development)

# Layer: 7

You are conducting a multi-persona review of a TDD document.
Review against the TDD-TEMPLATE.yaml requirements and TDD best practices.

## Review Objectives

1. **Test Coverage Completeness**: Verify all SPEC interfaces have
   corresponding test cases (unit, integration, e2e)

2. **Test Pyramid Balance**: Check 70/20/10 distribution is reasonable
   for the component complexity

3. **BDD Traceability**: Ensure all BDD scenarios are mapped to at least
   one test type

4. **Threshold Feasibility**: Verify coverage targets and pass criteria
   are achievable and measurable

5. **TDD Order Compliance**: Confirm Red-Green-Refactor sequence is
   properly declared for AI implementation

## Persona Roles

**(Architect)**: Review overall test strategy alignment with architecture
**(Tech Lead)**: Review technical feasibility of test approach
**(QA Lead)**: Review test coverage completeness and threshold targets
**(Chaos Engineer)**: Review error handling and edge case coverage
**(Auditor)**: Review traceability and compliance with TDD principles

## Validation Checklist

- [ ] All 7 template sections present
- [ ] Test mapping exists for every BDD scenario
- [ ] Unit tests target >=90% coverage threshold
- [ ] Integration tests validate component contracts from SPEC
- [ ] E2E tests cover happy paths mapped from BDD
- [ ] Security tests included ONLY if mandated by SPEC or ADR
- [ ] Threshold pass criteria are concrete and enforceable
- [ ] TDD execution order declares tests-first generation
- [ ] Traceability links to SPEC, ADR, and BDD references
- [ ] Readiness score >=90/100 indicates IPLAN readiness

## Actions

1. Identify missing or incomplete sections
2. Flag edge cases not covered by tests
3. Verify test file paths are plausible
4. Check threshold metrics are measurable
5. Confirm TDD order enables test-first implementation
6. Suggest specific improvements for each finding

## Output Format

Report findings with severity (P0/P1/P2) and recommended actions.
Include exact text for fixes where applicable.
