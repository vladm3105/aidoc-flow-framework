# doc-brd-reviewer v1.7 Implementation Plan

**Created**: 2026-02-25T10:45:00 EST
**Status**: Ready for Implementation
**Priority**: P1
**Target Files**:
- `/opt/data/docs_flow_framework/.claude/skills/doc-brd-reviewer/SKILL.md` (source)
- `/opt/data/b-local/b-local-docs/.claude/skills/doc-brd-reviewer/SKILL.md` (project copy)

---

## Overview

Implement the v1.7 changes documented in version history but never actually applied. The current implementation (v1.6) does not validate the 18-section BRD-MVP-TEMPLATE structure.

### Root Cause Analysis

The `BRD-MVP-TEMPLATE_FIX_PLAN.md` was marked "Completed" but:
1. Version history entry for v1.7 was added (line 761)
2. Actual implementation changes were **not applied**
3. Metadata still shows `version: "1.6"` (line 19)
4. Check #6 Section Completeness uses generic section names, not 18-section structure

---

## Gap Analysis

### Current Check #6 (Lines 292-322)

```markdown
| Section | Minimum Words |
|---------|---------------|
| Executive Summary | 100 |
| Problem Statement | 75 |
| Business Objectives | 150 |
| Functional Requirements | 200 |
| Non-Functional Requirements | 150 |
| ADR Topics | 300 |
| Appendices | 100 |
```

### Required Check #6 (Per BRD-MVP-TEMPLATE 18-Section Structure)

```markdown
| # | Section | Minimum Words | Required Subsections |
|---|---------|---------------|----------------------|
| 1 | Introduction | 100 | 1.1-1.5 |
| 2 | Business Objectives | 150 | 2.1 MVP Hypothesis |
| 3 | Project Scope | 200 | 3.2 MVP Core Features, 3.5.4-3.5.5 |
| 4 | Stakeholders | 75 | 4.1-4.2 |
| 5 | User Stories | 100 | 5.1-5.3 |
| 6 | Functional Requirements | 200 | 6.1-6.x per FR |
| 7 | Quality Attributes | 300 | 7.2 ADR Topics (7 mandatory categories) |
| 8 | Constraints & Assumptions | 100 | 8.1-8.2 |
| 9 | Acceptance Criteria | 100 | 9.1 MVP Launch Criteria |
| 10 | Risk Management | 150 | Risk table |
| 11 | Implementation Approach | 100 | 11.1-11.2 |
| 12 | Support & Maintenance | 75 | 12.1-12.2 |
| 13 | Cost-Benefit Analysis | 100 | 13.1-13.2 |
| 14 | Project Governance | 150 | 14.5 Approval and Sign-off |
| 15 | Quality Assurance | 100 | 15.3 Quality Gates |
| 16 | Traceability | 150 | 16.1-16.4 |
| 17 | Glossary | 50 | 17.1-17.6 (optional MVP) |
| 18 | Appendices | 100 | A-D |
```

---

## Implementation Changes

### Phase 1: Update Metadata (Lines 19-20)

**Current**:
```yaml
  version: "1.6"
  last_updated: "2026-02-24T21:30:00"
```

**Replace with**:
```yaml
  version: "1.7"
  last_updated: "2026-02-25T11:00:00"
```

---

### Phase 2: Update Check #6 Section Completeness (Lines 292-322)

**Replace entire section with**:

```markdown
### 6. Section Completeness

Verifies all 18 required sections have substantive content per BRD-MVP-TEMPLATE.

**Scope**:
- All 18 numbered sections present (plus Document Control)
- Minimum word count per section
- Required subsections for governance, traceability, glossary
- Tables have data rows (not just headers)
- Mermaid diagrams render properly

**18-Section Structure Validation**:

| # | Section | Min Words | Required Subsections |
|---|---------|-----------|----------------------|
| 1 | Introduction | 100 | 1.1-1.5 |
| 2 | Business Objectives | 150 | **2.1 MVP Hypothesis** |
| 3 | Project Scope | 200 | **3.2 MVP Core Features**, 3.5.4, 3.5.5 |
| 4 | Stakeholders | 75 | 4.1-4.2 |
| 5 | User Stories | 100 | 5.1-5.3 |
| 6 | Functional Requirements | 200 | 6.1+ per FR |
| 7 | Quality Attributes | 300 | **7.2 ADR Topics (7 categories)** |
| 8 | Constraints & Assumptions | 100 | 8.1-8.2 |
| 9 | Acceptance Criteria | 100 | **9.1 MVP Launch Criteria** |
| 10 | Risk Management | 150 | Risk table required |
| 11 | Implementation Approach | 100 | 11.1-11.2 |
| 12 | Support & Maintenance | 75 | 12.1-12.2 |
| 13 | Cost-Benefit Analysis | 100 | 13.1-13.2 |
| 14 | Project Governance | 150 | **14.5 Approval and Sign-off** |
| 15 | Quality Assurance | 100 | **15.3 Quality Gates** |
| 16 | Traceability | 150 | **16.1-16.4** (all required) |
| 17 | Glossary | 50 | **17.1-17.6** (structure required) |
| 18 | Appendices | 100 | Appendix A-D |

**MVP-Critical Subsections** (bold items above):

| Subsection | Purpose | Error if Missing |
|------------|---------|------------------|
| 2.1 MVP Hypothesis | Validates core MVP assumption | REV-MVP001 |
| 3.2 MVP Core Features | P1/P2 feature checklist | REV-MVP002 |
| 9.1 MVP Launch Criteria | Go/no-go checklist | REV-MVP003 |
| 14.5 Approval and Sign-off | Stakeholder sign-off table | REV-MVP004 |
| 15.3 Quality Gates | Quality gate checklist | REV-MVP005 |
| 16.1-16.4 | Traceability matrix subsections | REV-MVP006-009 |
| 17.1-17.6 | Glossary structure | REV-MVP010 |

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-S001 | Error | Required section missing entirely |
| REV-S002 | Warning | Section below minimum word count |
| REV-S003 | Warning | Table has no data rows |
| REV-S004 | Error | Mermaid diagram syntax error |
| REV-MVP001 | Error | Missing MVP Hypothesis (Section 2.1) |
| REV-MVP002 | Warning | Missing MVP Core Features checklist (Section 3.2) |
| REV-MVP003 | Error | Missing MVP Launch Criteria (Section 9.1) |
| REV-MVP004 | Error | Missing Approval Sign-off Table (Section 14.5) |
| REV-MVP005 | Error | Missing Quality Gates (Section 15.3) |
| REV-MVP006 | Error | Missing Requirements Traceability Matrix (Section 16.1) |
| REV-MVP007 | Warning | Missing Cross-BRD Dependencies (Section 16.2) |
| REV-MVP008 | Warning | Missing Test Coverage Traceability (Section 16.3) |
| REV-MVP009 | Warning | Missing Traceability Summary (Section 16.4) |
| REV-MVP010 | Warning | Missing Glossary subsection structure (17.1-17.6) |
```

---

### Phase 3: Add Subsection Validation Logic (After Line 322)

**Insert new subsection**:

```markdown
#### 6.1 Subsection Validation Algorithm

```
FOR each section in 18_SECTION_LIST:
  1. Verify section header exists: "## {N}. {Title}"
  2. Count words in section content
  3. IF section has required_subsections:
     FOR each subsection in required_subsections:
       - Search for header pattern: "### {N}.{M}" or "#### {N}.{M}.{X}"
       - IF not found: Add appropriate error code
       - IF found: Validate minimum content (>10 words)
  4. IF section < minimum_words: Add REV-S002 warning
```

**Section Detection Patterns**:

| Section Type | Pattern | Example |
|--------------|---------|---------|
| Main section | `## N. Title` | `## 14. Project Governance` |
| Subsection | `### N.M Title` | `### 14.5 Approval and Sign-off` |
| Sub-subsection | `#### N.M.X Title` | `#### 16.1.1 Business Objectives → FRs` |

**Sectioned BRD Handling**:

For sectioned BRDs (BRD-NN.N_*.md files):
1. Map file to section number from filename pattern
2. Validate section content within that file
3. Cross-reference section numbering consistency

| File Pattern | Section |
|--------------|---------|
| BRD-NN.14_*.md | Section 14 (Governance) |
| BRD-NN.15_*.md | Section 15 (Quality Assurance) |
| BRD-NN.16_*.md | Section 16 (Traceability) |
| BRD-NN.17_*.md | Section 17 (Glossary) |
```

---

### Phase 4: Update Review Score Calculation (Lines 624-641)

**Modify Section Completeness row**:

Current:
```markdown
| Section Completeness | 12% | (complete_sections / total_sections) × 12 |
```

Replace with:
```markdown
| Section Completeness | 12% | ((18_sections_present + mvp_subsections_valid) / (18 + 10)) × 12 |
```

**Note**: 18 main sections + 10 MVP-critical subsections = 28 validation points

---

### Phase 5: Update Version History (Line 761)

**Current v1.7 entry**:
```markdown
| 1.7 | 2026-02-25 | **Template alignment**: Updated for 18-section structure with sections 12 (Support), 14 (Governance/Approval), 15 (QA), 16 (Traceability 16.1-16.4), 17 (Glossary 17.1-17.6) |
```

**Replace with**:
```markdown
| 1.7 | 2026-02-25T11:00:00 | **Template alignment**: Check #6 updated for 18-section structure; Added MVP-critical subsection validation (2.1, 3.2, 9.1, 14.5, 15.3, 16.1-16.4, 17.1-17.6); Added REV-MVP001-MVP010 error codes; Updated scoring formula for subsection validation |
```

---

## Verification Checklist

### Pre-Implementation
- [ ] Backup current SKILL.md files
- [ ] Document current version (1.6)

### Implementation
- [ ] Phase 1: Update metadata to v1.7
- [ ] Phase 2: Replace Check #6 with 18-section validation
- [ ] Phase 3: Add subsection validation logic
- [ ] Phase 4: Update scoring formula
- [ ] Phase 5: Update version history entry

### Post-Implementation
- [ ] Apply changes to source: `/opt/data/docs_flow_framework/.claude/skills/doc-brd-reviewer/SKILL.md`
- [ ] Apply changes to project copy: `/opt/data/b-local/b-local-docs/.claude/skills/doc-brd-reviewer/SKILL.md`
- [ ] Verify syntax (no markdown errors)
- [ ] Test with BRD-01 (should still pass with 100/100)
- [ ] Test with incomplete BRD (should flag missing MVP subsections)

### Regression Testing
- [ ] Run `/doc-brd-reviewer BRD-01` - expect 100/100
- [ ] Verify review report includes 18-section structure validation
- [ ] Verify MVP subsection checks appear in detailed results

---

## Files to Update

| File | Action | Priority |
|------|--------|----------|
| `/opt/data/docs_flow_framework/.claude/skills/doc-brd-reviewer/SKILL.md` | Full v1.7 implementation | P1 |
| `/opt/data/b-local/b-local-docs/.claude/skills/doc-brd-reviewer/SKILL.md` | Sync with source | P1 |
| `/opt/data/docs_flow_framework/ai_dev_ssd_flow/01_BRD/BRD-MVP-TEMPLATE_FIX_PLAN.md` | Mark Phase 7.2 as actually completed | P2 |

---

## Rollback Plan

If issues occur:
1. Restore from backup: `cp SKILL.md.backup SKILL.md`
2. Revert version to 1.6
3. Document failure mode for debugging

---

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| BRD-MVP-TEMPLATE.md | ✅ Updated | 18-section structure in place |
| BRD-MVP-TEMPLATE.yaml | ✅ Updated | Section schema defined |
| doc-brd-validator | ✅ v2.3 | Validation rules aligned |
| doc-brd-fixer | ✅ v2.3 | Fix patterns updated |

---

**End of Implementation Plan**
