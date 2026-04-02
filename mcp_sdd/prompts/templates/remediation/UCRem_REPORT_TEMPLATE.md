---
title: "UCRem Report: {TARGET_DOC_ID}"
doc_id: "{TARGET_DOC_ID}.UCRem"
version: "1.0.0"
tags:
  - ucrem
  - remediation-report
  - fix-proposal
custom_fields:
  document_type: ucrem_report
  artifact_type: REMEDIATION_REPORT
  layer: "{LAYER_NUMBER}"
  target_artifact_id: "{TARGET_DOC_ID}"
  target_artifact_version: "{TARGET_DOC_VERSION}"
  source_review: "{UCR_REVIEW_FILE}"
  review_date: "{UCR_REVIEW_DATE}"
  remediation_date: "{CURRENT_DATE}"
  method: UCRem
  personas_applied: [Architect Fixer, Auditor Fixer, QA Fixer, Integration Fixer, Chaos Engineer, Chairperson]
  statistics:
    total_findings: "{TOTAL_FINDINGS}"
    auto_safe_fixes: "{AUTO_SAFE_COUNT}"
    auto_assisted_fixes: "{AUTO_ASSISTED_COUNT}"
    manual_required: "{MANUAL_COUNT}"
    cross_validation_conflicts: "{CONFLICT_COUNT}"
---

# UCRem Remediation Report: {TARGET_DOC_ID}

> **Target Document**: {TARGET_DOC_ID} (Version {TARGET_DOC_VERSION})
> **Source Review**: {UCR_REVIEW_FILE}
> **Remediation Date**: {CURRENT_DATE}
> **Method**: UCRem (Unified Context Remediation)
> **Personas Applied**: {PERSONA_COUNT} ({PERSONA_LIST})

---

## 1. Remediation Summary

| Metric | Value |
|--------|-------|
| Source Review | {UCR_REVIEW_FILE} |
| Total Findings | {TOTAL_FINDINGS} |
| Auto-Safe Fixes | {AUTO_SAFE_COUNT} |
| Auto-Assisted Fixes | {AUTO_ASSISTED_COUNT} |
| Manual Required | {MANUAL_COUNT} |
| Cross-Validation Conflicts | {CONFLICT_COUNT} |

### 1.1 Blocking Items (P0 Manual-Required)

| Fix ID | Finding | Reason for Manual Review |
|--------|---------|-------------------------|
| FIX-P0-XX | {Finding description} | {Why manual review needed} |

### 1.2 Execution Phases

| Phase | Type | Fix Count | Action |
|-------|------|-----------|--------|
| 1 | Auto-Safe | {N} | Execute automatically |
| 2 | Auto-Assisted | {N} | Execute with [TODO] prompts |
| 3 | Manual | {N} | Create tasks for review |

---

## 2. Auto-Safe Fixes

These fixes can be applied automatically without human review.

### 2.1 FIX-P0-01: {Short Description}

```yaml
fix_id: FIX-P0-01
source_finding: P0-1
priority: P0
confidence: auto-safe
target_file: "{exact_filename.md}"
target_section: "{X.X.X}"
fix_type: add_text
fix_action:
  position: after
  anchor: "{exact text to find in document}"
  text: |
    {Exact text to insert. Complete and ready to apply.
    No placeholders or vague instructions.}
rationale: |
  {Explain why this specific fix addresses the finding.
  Reference the original finding and what was missing.}
validated_by:
  - Architect Fixer
  - Auditor Fixer
verification: |
  {How to verify fix was applied correctly.
  Include searchable text or checklist.}
```

---

## 3. Auto-Assisted Fixes

These fixes provide templates with [TODO] items requiring completion.

### 3.1 FIX-P0-02: {Short Description}

```yaml
fix_id: FIX-P0-02
source_finding: P0-2
priority: P0
confidence: auto-assisted
target_file: "{exact_filename.md}"
target_section: "{X.X}"
fix_type: add_section
fix_action:
  parent_section: "{X.X}"
  section_number: "{X.X.X}"
  heading: "{Section Title}"
  content: |
    #### {X.X.X Section Title}

    {Template content with [TODO] placeholders clearly marked.}

    | Column 1 | Column 2 |
    |----------|----------|
    | Value | [TODO: Complete] |
rationale: |
  {Explain why this fix addresses the finding.
  Note which [TODO] items need domain expert input.}
validated_by:
  - {Persona 1}
  - {Persona 2}
todo_items:
  - "[TODO: Description of what needs completion]"
  - "[TODO: Another item]"
verification: |
  {Verify section exists. Count [TODO] items remaining.
  All must be resolved before marking complete.}
```

---

## 4. Manual-Required Fixes

These fixes require human review before application.

### 4.1 FIX-P0-03: {Short Description}

```yaml
fix_id: FIX-P0-03
source_finding: P0-3
priority: P0
confidence: manual-required
target_file: "{exact_filename.md}"
target_section: "{X.X}"
fix_type: add_section
fix_action:
  parent_section: "{X.X}"
  section_number: "{X.X.X}"
  heading: "{Section Title}"
  content: |
    > **MANUAL REVIEW REQUIRED**: {Reason}

    {Scaffold content with [MANUAL] markers}
rationale: |
  {Explain what the fix addresses.}
validated_by:
  - {Persona}
manual_review_reason: |
  {Detailed explanation of why manual review is required.
  What decisions need to be made?
  What domain knowledge is needed?}
devil_advocate_note: |
  {If Chaos Engineer flagged this, explain the concern.
  What root cause issue needs architectural/business decision?}
prerequisite_decisions:
  - "{Decision 1 needed before fix can be completed}"
  - "{Decision 2}"
verification: |
  {How to verify once manual review is complete.
  What must be true for this to be marked resolved?}
```

---

## 5. Cross-Validation Results

### 5.1 Conflicts Identified

```yaml
cross_validation:
  - conflict_id: CV-01
    fixes_involved:
      - FIX-P0-XX
      - FIX-P1-XX
    conflict_type: "{location_overlap|semantic_conflict|approach_disagreement}"
    description: |
      {What is the conflict?}
    resolution: |
      {How was it resolved, or why does it need manual review?}
    resolved_by: "{Persona name|MANUAL}"
```

### 5.2 Persona Validation Summary

| Fix ID | Architect | Auditor | QA | Integration | Chaos Engineer | Final |
|--------|-----------|---------|-----|-------------|------------------|-------|
| FIX-P0-01 | PASS | PASS | PASS | PASS | PASS | auto-safe |
| FIX-P0-02 | PASS | PASS | FLAG | PASS | PASS | auto-assisted |
| FIX-P0-03 | PASS | PASS | PASS | PASS | OBJECT | manual-required |

---

## 6. Execution Instructions

```yaml
execution_order:
  - phase: 1
    description: "Apply auto-safe fixes"
    fixes:
      - FIX-P0-01
      - FIX-P1-01
      - FIX-P1-02
    instruction: |
      Apply in listed order. No human review needed.
      Verify each fix using the verification criteria.

  - phase: 2
    description: "Apply auto-assisted fixes"
    fixes:
      - FIX-P0-02
      - FIX-P1-03
    instruction: |
      Apply template content. After application:
      1. List all [TODO] items for follow-up
      2. Create tasks for each [TODO] completion
      3. Do not mark fix as complete until [TODO]s resolved

  - phase: 3
    description: "Manual review queue"
    fixes:
      - FIX-P0-03
    instruction: |
      Do NOT auto-apply. For each fix:
      1. Create GitHub issue or task
      2. Assign to domain expert based on prerequisite_decisions
      3. Track until prerequisite decisions made
      4. Re-run UCRem after decisions to generate executable fix
```

---

## 7. Post-Remediation Checklist

After applying Phase 1 and Phase 2 fixes:

- [ ] All auto-safe fixes applied and verified
- [ ] All auto-assisted fixes applied
- [ ] [TODO] items documented for follow-up
- [ ] Manual-required fixes have tasks created
- [ ] Cross-reference integrity verified
- [ ] Run UCR review on updated document
- [ ] Compare P0/P1 counts: should be reduced

### 7.1 Expected Outcome

| Metric | Before | After (Expected) |
|--------|--------|------------------|
| P0 Findings | {N} | {N - auto_safe_P0 - auto_assisted_P0} |
| P1 Findings | {N} | {N - auto_safe_P1 - auto_assisted_P1} |
| P2 Findings | {N} | {N} (P2 usually not auto-fixed) |

---

## 8. Appendix: Fix Type Reference

| fix_type | fix_action Fields | Description |
|----------|------------------|-------------|
| `add_text` | position, anchor, text | Add text before/after anchor |
| `add_section` | parent_section, section_number, heading, content | Add new subsection |
| `add_table_row` | table_anchor, row_data | Add row to existing table |
| `modify_text` | old_text, new_text | Replace exact text |
| `add_frontmatter` | field_path, value | Add/update YAML field |
| `add_tag` | tag_type, tag_value, location | Add traceability tag |
| `create_file` | file_path, template, content | Create new file |

---

**Report Generated**: {CURRENT_DATE}
**Method**: UCRem (Unified Context Remediation)
**Generator**: Claude Opus 4.5
**Personas Applied**: {PERSONA_COUNT}
