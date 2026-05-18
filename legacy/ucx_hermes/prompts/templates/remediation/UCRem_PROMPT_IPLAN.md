# IPLAN Remediation Prompt
# Document Type: IPLAN (Implementation Plan)
# Layer: 8

You are remediating an IPLAN document that failed validation.
Apply fixes to bring the document into compliance with IPLAN-TEMPLATE.yaml.

## Remediation Approach

### Step 1: Review Validation Findings
- Read the validation report identifying missing or incorrect content
- Categorize findings by severity (P0 blocking, P1 high, P2 medium)
- Focus on P0 issues first (missing required sections, invalid IDs)

### Step 2: Apply Section-by-Section Fixes
**Document Control**:
- Generate unique IPLAN-NN ID
- Link to correct SPEC component (@spec: SPEC-NN)
- Ensure complexity estimate matches file count

**File Manifest**:
- Verify all paths exist or use plausible placeholders
- Ensure test files have lower order numbers than implementation files
- Add missing files with correct order sequence

**Execution Commands**:
- Ensure setup command prepares environment for code generation
- Verify implementation follows test-first order
- Add validation commands for pytest, mypy, ruff

**Implementation Contracts**:
- Include ONLY if 3+ files share interfaces
- State "No implementation contracts" if not applicable
- Contract types: Protocol Interface, Exception Hierarchy, State Machine, Data Model, DI Interface

**Session Handoff**:
- Initialize sessions array (empty) or populate if resuming
- Mark files as NOT_STARTED, IN_PROGRESS, DONE, or PARTIAL
- Add partial_work description if session ended mid-step

**Traceability**:
- Add @spec: SPEC-NN and @tdd: TDD.NN tags
- Verify all referenced IDs exist in document

### Step 3: Recalculate Readiness Score
- Use new validation results to update readiness score
- Target: >=90/100 for Code-Ready status

## Fix Rules
1. Do NOT generate code (only describe what will be created)
2. Preserve valid content from original document
3. Use exact text for fixes identified in validation report
4. Ensure file manifest respects test-first order
5. Recalculate score after applying all fixes

## Output Requirements
- YAML format only
- All 6 sections present
- Readiness score >=90/100
- All traceability IDs valid and present
- Session handoff initialized for stateless executor calls
