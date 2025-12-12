# Plan: Update Framework for REF Document Ready-Score Exemption

**Plan Name**: ref-document-exemption
**Created**: 2025-12-12 12:04:39 EST
**Status**: Ready for Implementation

---

## Understanding

**User Request**: Update framework documents and doc-* skills to clarify that REF type documents do not need ready-scores for downstream documents.

**Scope Decision**: REF documents are LIMITED to **BRD and ADR only**.

## Current State Analysis

### Already Implemented
- `BRD_VALIDATION_RULES.md`: ✅ BRD-REF fully implemented (commit 5c911b0)
  - BRD Document Categories table
  - BRD-REF Reduced Validation section
  - PRD-Ready Score exemption for BRD-REF
- `REF-TEMPLATE.md`: States "Exempted: Cumulative tags, full traceability chain, quality gates"
- `doc-ref` skill: Shows "SPEC-Ready Score | Not applicable"

### Gap Analysis - Files That Need Updates

**Validation Rules** (1 file):
1. `ai_dev_flow/ADR/ADR_VALIDATION_RULES.md` - needs ADR-REF support (mirroring BRD pattern)

**Doc-* Skills** (2 files):
1. `.claude/skills/doc-brd/SKILL.md` - clarify BRD-REF no PRD-Ready Score
2. `.claude/skills/doc-adr/SKILL.md` - clarify ADR-REF no SYS-Ready Score

**Framework Guide**:
- `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` - add REF exemption section (BRD/ADR only)

## Design Decisions

1. **REF Variants Scope**: Limited to **BRD and ADR only** (user decision)
2. **REF Purpose**: Reference documents that **other documents link to** (reference targets)
   - Provides supporting information, context, or external references
   - Other BRD/ADR documents can cite REF documents as sources
3. **REF Format**: Free format, business-oriented description - **NO SCORES AT ALL**
   - No PRD-Ready Score (for BRD-REF)
   - No SYS-Ready Score (for ADR-REF)
   - No quality gates or downstream readiness metrics
4. **BRD-REF**: Already implemented - no changes needed
5. **ADR-REF**: Needs full implementation mirroring BRD pattern
6. **REF-TEMPLATE.md**: Update to clarify BRD/ADR scope, reference purpose, and no-score policy

## Implementation Plan

### Phase 1: ADR_VALIDATION_RULES.md Updates (1 file)

**Gap Analysis**: ADR_VALIDATION_RULES.md (version 1.0, only 221 lines) completely lacks REF document support.
- Has SYS-Ready Score (CHECK 3) requiring ≥90% - needs exemption for ADR-REF
- Has cumulative traceability tags (CHECK 4: @brd, @prd, @ears, @bdd) - needs exemption for ADR-REF
- No ADR Document Categories table
- No ADR-REF Reduced Validation section

1. **Add ADR Document Categories table** after Overview section:
```markdown
### ADR Document Categories

| Category | Filename Pattern | Validation Level | Description |
|----------|------------------|------------------|-------------|
| **Standard ADR** | `ADR-NNN_{decision_topic}` | Full (7 checks) | Architecture decision records |
| **ADR-REF** | `ADR-REF-NNN_{slug}.md` | Reduced (4 checks) | Supplementary reference documents |
```

2. **Add ADR-REF Reduced Validation section**:
```markdown
### ADR-REF Reduced Validation

**Purpose**: ADR-REF documents are reference targets that other documents link to. They provide supporting information, context, or external references in free format with business-oriented descriptions. They do not define formal architecture decisions.

**Applicable Checks** (4 total):
- CHECK 1 (partial): Document Control Fields (required)
- Document Revision History (required)
- Status/Context sections only (required)
- H1 ID match with filename (required)

**Exempted Checks** (NO SCORES):
- SYS-Ready Score: NOT APPLICABLE (REF documents use free format, no scores)
- CHECK 4: Cumulative traceability tags NOT REQUIRED (@brd, @prd, @ears, @bdd)
- CHECK 5-7: Decision quality, architecture documentation, implementation readiness (exempt)
- All quality gates and downstream readiness metrics: EXEMPT
```

3. **Update CHECK validation** to detect ADR-REF and apply reduced validation

### Phase 2: Doc-* Skills Updates (2 files)

| File | REF Exemption Clarification |
|------|----------------------------|
| `doc-brd/SKILL.md` | BRD-REF: Free format, no scores (no PRD-Ready Score) |
| `doc-adr/SKILL.md` | ADR-REF: Free format, no scores (no SYS-Ready Score) |

### Phase 3: Framework Guide Update (1 file)

- `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`: Add REF Document Exemptions section (BRD/ADR only)

### Phase 4: REF Template Clarification (1 file)

- `REF-TEMPLATE.md`: Clarify BRD/ADR scope, add explicit ready-score exemption statement

## Files to Modify

**Total: 5 files**

### Validation Rules (1 file)
1. `ai_dev_flow/ADR/ADR_VALIDATION_RULES.md` - Add ADR-REF support (mirroring BRD pattern)

### Doc-* Skills (2 files)
2. `.claude/skills/doc-brd/SKILL.md` - Add BRD-REF ready-score exemption
3. `.claude/skills/doc-adr/SKILL.md` - Add ADR-REF ready-score exemption

### Framework Documents (2 files)
4. `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` - Add REF exemption section
5. `ai_dev_flow/REF-TEMPLATE.md` - Clarify BRD/ADR scope

---

## Implementation Commands

To continue implementation in a new context:

```bash
# Resume this plan
claude --resume ref-document-exemption

# Or reference the plan file directly
cat /opt/data/docs_flow_framework/work_plans/ref-document-exemption_20251212_120439.md
```
