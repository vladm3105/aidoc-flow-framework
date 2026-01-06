# Implementation Plan - Enhance ADR Corpus Validation

**Created**: 2026-01-04 18:15:42 EST
**Completed**: 2026-01-04 18:25 EST
**Status**: Completed

## Objective

Add missing sections from Trading Nexus ADR validation rules to the framework's generic ADR corpus validation document.

## Context

- **Source**: `/opt/data/trading_nexus/docs/ADR/ADR_CORPUS_VALIDATION_RULES.md` (463 lines)
- **Target**: `/opt/data/docs_flow_framework/ai_dev_flow/ADR/ADR_CORPUS_VALIDATION.md` (489 lines)
- Trading Nexus has practical patterns developed during actual ADR creation (ADR-01 to ADR-22)
- Framework file needs enhancement with error tracking, structure requirements, complete validation script, and remediation steps
- This follows the same pattern as the BDD corpus validation enhancement just completed

## Task List

### Completed
- [x] Add Section 0: Errors Found During Validation (~40 lines)
- [x] Add numbered check comments to existing CORPUS validation logic (~25 lines)
- [x] Add Section 3: ADR Structure Requirements (~70 lines)
- [x] Add Section 4: Cumulative Tagging Requirements (~35 lines)
- [x] Replace script usage examples with complete validation script (~150 lines)
- [x] Add Section 6: Post-Validation Actions (~40 lines)
- [x] Add Section 7: ADR-Specific Validation Rules (~45 lines)
- [x] Add Section 8: Baseline Metrics (~30 lines)
- [x] Update Document History with version 1.1
- [x] Verify file renders correctly and stays under 1000 lines (945 lines)

## Implementation Guide

### Prerequisites
- Read both source and target files (completed during analysis)
- Understand section placement for proper renumbering

### Execution Steps

1. **Insert Section 0** after line 46 (after ADR Document Categories table):
   - 0.1 Critical Errors (MUST FIX) table - E01-E06
   - 0.2 Warnings (SHOULD FIX) table - W01-W03
   - 0.3 Issues Fixed (Reference) table

2. **Add numbered check comments** to existing CORPUS validation logic blocks in Section 1

3. **Insert Section 3: ADR Structure Requirements** after current Section 2 (Error Codes):
   - 3.1 Pattern A vs Pattern B (Historical Context) table
   - 3.2 Required Document Structure (16 sections)
   - 3.3 SYS-Ready Score Calculation table

4. **Insert Section 4: Cumulative Tagging Requirements**:
   - 4.1 ADR Layer Position table (Layer 5, 4 upstream tags)
   - 4.2 Tag Format Convention (dash vs dot notation)

5. **Replace Section 3 (Automated Script Usage)** with complete validation script (~150 lines bash)

6. **Add Section 6: Post-Validation Actions**:
   - 6.1 For Critical Errors remediation table
   - 6.2 For Warnings remediation table

7. **Add Section 7: ADR-Specific Validation Rules**:
   - 7.1 Reserved ID Exemption
   - 7.2 ADR-REF Documents
   - 7.3 Mermaid Diagram Requirements

8. **Add Section 8: Baseline Metrics** template table with validation command

9. **Renumber existing sections**:
   - Current Section 4 (Validation Checklist) → Section 9
   - Current Section 5 (CI/CD Integration) → Section 10

10. **Update Document History** with version 1.1 entry

### Final Section Order
1. Section 0: Errors Found During Validation (NEW)
2. Section 1: Corpus Validation Checks (enhanced)
3. Section 2: Error Codes (existing)
4. Section 3: ADR Structure Requirements (NEW)
5. Section 4: Cumulative Tagging Requirements (NEW)
6. Section 5: Automated Validation Script (enhanced)
7. Section 6: Post-Validation Actions (NEW)
8. Section 7: ADR-Specific Validation Rules (NEW)
9. Section 8: Baseline Metrics (NEW)
10. Section 9: Validation Checklist (renumbered)
11. Section 10: CI/CD Integration (renumbered)
12. Section 11: Document History (NEW)
13. References (existing)

### Verification
- [x] File line count < 1000 lines (945 lines)
- [x] All markdown renders correctly
- [x] Code blocks have proper syntax highlighting
- [x] Section numbers are sequential (0-11 + References)
- [x] No broken internal references

## References

- Source file: `/opt/data/trading_nexus/docs/ADR/ADR_CORPUS_VALIDATION_RULES.md`
- Target file: `/opt/data/docs_flow_framework/ai_dev_flow/ADR/ADR_CORPUS_VALIDATION.md`
- Detailed plan: `/home/ya/.claude/plans/magical-conjuring-planet.md`
- Similar completed work: BDD corpus validation enhancement (same session)
