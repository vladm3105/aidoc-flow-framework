# IPLAN Review Prompt
# Document Type: IPLAN (Implementation Plan)
# Layer: 8

You are conducting a multi-persona review of an IPLAN document.
Review against the IPLAN-TEMPLATE.yaml requirements and implementation planning best practices.

## Review Objectives

1. **File Manifest Accuracy**: Verify all files are declared with proper
   order, status, and traceability links

2. **Execution Command Completeness**: Check setup, implementation, and
   validation commands are sufficient for AI implementation

3. **Session Handoff Protocol**: Validate session markers and handoff
   structure are properly initialized

4. **TDD Traceability**: Confirm links to TDD and SPEC upstream artifacts

5. **Implementation Contract Fit**: If present, verify contracts are
   beneficial (3+ files with shared interfaces)

## Persona Roles

**(Architect)**: Review file structure and implementation contracts alignment
**(Tech Lead)**: Review execution command feasibility and validation approach
**(QA Lead)**: Review test validation commands and quality gates
**(Chaos Engineer)**: Review error handling in setup and implementation
**(Auditor)**: Review traceability and session handoff completeness

## Validation Checklist

- [ ] All 6 template sections present
- [ ] File manifest declares all files with path, order, status, session, verified
- [ ] Test files have lower order numbers than implementation files
- [ ] Setup commands prepare environment for code generation
- [ ] Implementation commands follow test-first order
- [ ] Validation commands include pytest, mypy, ruff or equivalent
- [ ] Session handoff section initialized (empty sessions array)
- [ ] Traceability links SPEC and TDD references
- [ ] Implementation contracts present ONLY if 3+ files share interfaces
- [ ] Readiness score >=90/100 indicates Code readiness

## Actions

1. Identify missing files or incorrect order in manifest
2. Flag incomplete or incorrect validation commands
3. Verify session handoff markers are understood
4. Check traceability links are valid
5. Assess if implementation contracts add value or overhead
6. Suggest missing setup or cleanup commands

## Output Format

Report findings with severity (P0/P1/P2) and recommended actions.
Include exact text for fixes where applicable.
