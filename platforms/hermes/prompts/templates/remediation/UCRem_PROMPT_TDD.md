# TDD Remediation Prompt

# Document Type: TDD (Test-Driven Development)

# Layer: 7

You are remediating a TDD document that failed validation.
Apply fixes to bring the document into compliance with TDD-TEMPLATE.yaml.

## Remediation Approach

### Step 1: Review Validation Findings

- Read the validation report identifying missing or incorrect content
- Categorize findings by severity (P0 blocking, P1 high, P2 medium)
- Focus on P0 issues first (missing required sections, invalid IDs)

### Step 2: Apply Section-by-Section Fixes

**Document Control**:

- Generate unique TDD.NN ID
- Calculate IPLAN-Ready score >=90/100
- Ensure all required fields present

**Test Pyramid**:

- Maintain 70/20/10 distribution unless component justifies variation
- Update flowchart to match distribution percentages

**BDD Scenario Mapping**:

- Ensure every BDD scenario has at least one test mapping
- Add missing test types (unit/integration/e2e) per scenario

**Test Case Definitions**:

- Verify all test cases reference SPEC sections
- Ensure test functions have concrete expected outputs
- Add edge case coverage for boundary/null/empty conditions

**Thresholds**:

- Verify coverage targets are achievable
- Add pass criteria if missing (e.g., "all tests pass")
- Ensure fail actions are enforceable

**TDD Execution Order**:

- Confirm Red-Green-Refactor phases are declared
- Verify phase 1 generates test files, phase 2 implements

**Traceability**:

- Add @tdd: TDD.NN tag to traceability section
- Verify all referenced IDs exist in document

### Step 3: Recalculate Readiness Score

- Use new validation results to update readiness score
- Target: >=90/100 for IPLAN-Ready status

## Fix Rules

1. Do NOT change test architecture decisions
2. Do NOT add implementation code (only test specifications)
3. Preserve valid content from original document
4. Use exact text for fixes identified in validation report
5. Recalculate score after applying all fixes

## Output Requirements

- YAML format only
- All 7 sections present
- Readiness score >=90/100
- All traceability IDs valid and present
