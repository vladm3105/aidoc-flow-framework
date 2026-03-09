# UCRem Report Schema

## Overview

The **UCRem (Unified Context Remediation) Report** is the output of the multi-persona fix planning phase. It provides machine-parseable fix instructions for the execution agent.

**Core Principle**: Every fix entry must be **executable without interpretation**. The execution agent should be able to apply fixes without domain knowledge.

---

## Schema Version

```yaml
schema_version: "1.0.0"
schema_type: ucrem_report
```

---

## Report Structure

```
UCRem_REPORT.md
├── YAML Frontmatter (metadata)
├── 1. Remediation Summary (statistics)
├── 2. Fix Entries (YAML code blocks - machine-parseable)
│   ├── 2.1 Auto-Safe Fixes
│   ├── 2.2 Auto-Assisted Fixes
│   └── 2.3 Manual-Required Fixes
├── 3. Cross-Validation Results
├── 4. Post-Fix Verification Checklist
└── 5. Execution Instructions
```

---

## YAML Frontmatter

```yaml
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
  personas_applied: [Architect Fixer, Auditor Fixer, QA Fixer, Integration Fixer, Devil's Advocate]
  statistics:
    total_findings: {N}
    auto_safe_fixes: {N}
    auto_assisted_fixes: {N}
    manual_required: {N}
    cross_validation_conflicts: {N}
---
```

---

## Fix Entry Schema

Each fix is defined in a YAML code block for machine parsing:

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `fix_id` | string | Unique ID: `FIX-{priority}-{seq}` (e.g., `FIX-P0-01`) |
| `source_finding` | string | Original finding ID from UCR report (e.g., `P0-1`) |
| `priority` | enum | `P0` \| `P1` \| `P2` |
| `confidence` | enum | `auto-safe` \| `auto-assisted` \| `manual-required` |
| `target_file` | string | Exact file path relative to doc root |
| `target_section` | string | Section number or heading (e.g., `6.1.1` or `## Quality Attributes`) |
| `fix_type` | enum | See Fix Type Enum below |
| `fix_action` | object | Action-specific payload (see below) |
| `rationale` | string | Why this fix addresses the finding |
| `validated_by` | array | List of personas that validated this fix |
| `verification` | string | How to verify the fix was applied correctly |

### Confidence Levels

| Level | Criteria | Execution |
|-------|----------|-----------|
| `auto-safe` | Deterministic, no domain knowledge needed, low risk | Execute automatically |
| `auto-assisted` | Template insertion, may need minor adjustments | Execute with review prompt |
| `manual-required` | Domain knowledge needed, ambiguous, high risk | Flag for human review |

### Fix Type Enum

| Type | Description | fix_action Schema |
|------|-------------|-------------------|
| `add_text` | Add new text at location | `{ position: after|before|replace, anchor: string, text: string }` |
| `add_section` | Add new subsection | `{ parent_section: string, section_number: string, heading: string, content: string }` |
| `add_table_row` | Add row to existing table | `{ table_anchor: string, row_data: array }` |
| `modify_text` | Replace existing text | `{ old_text: string, new_text: string }` |
| `add_frontmatter` | Add YAML frontmatter field | `{ field_path: string, value: any }` |
| `add_tag` | Add traceability tag | `{ tag_type: string, tag_value: string, location: string }` |
| `create_file` | Create new file | `{ file_path: string, template: string, content: string }` |

---

## Fix Entry Examples

### Example 1: Auto-Safe Text Addition

```yaml
fix_id: FIX-P0-01
source_finding: P0-1
priority: P0
confidence: auto-safe
target_file: BRD-01.6_functional_requirements.md
target_section: "6.1.1"
fix_type: add_text
fix_action:
  position: after
  anchor: "SAR workflow automation"
  text: |

    **Human Review Mandate**: All SAR narratives MUST be reviewed and approved by
    a licensed Compliance Officer within 24 hours of automated generation. No SAR
    may be filed without human authorization. System SHALL enforce this gate via
    workflow state machine requiring CO_APPROVED status before BSA submission.
rationale: |
  UCR finding P0-1 identified that SAR human review mandate is not explicit.
  The document mentions "SAR workflow automation" but lacks the mandatory
  human-in-the-loop requirement for regulatory compliance. This fix adds
  explicit language per FinCEN requirements.
validated_by:
  - Auditor Fixer
  - Architect Fixer
verification: |
  Search for "Human Review Mandate" in section 6.1.1. Verify text includes
  "licensed Compliance Officer", "24 hours", and "CO_APPROVED status".
```

### Example 2: Auto-Assisted Section Addition

```yaml
fix_id: FIX-P0-02
source_finding: P0-2
priority: P0
confidence: auto-assisted
target_file: BRD-01.7_quality_attributes.md
target_section: "7.2"
fix_type: add_section
fix_action:
  parent_section: "7.2"
  section_number: "7.2.4"
  heading: "PCI-DSS Compliance Scope"
  content: |
    #### 7.2.4 PCI-DSS Compliance Scope

    **SAQ Level**: SAQ-D (Service Provider)

    **Scope Boundary**:
    | Component | In Scope | Justification |
    |-----------|----------|---------------|
    | Payment tokenization | Yes | Handles card data via Nuvei |
    | User authentication | No | No card data in auth flow |
    | Transaction logging | Yes | Contains masked PAN references |

    **Cardholder Data Flow**:
    - Card data enters system at: [TODO: Specify entry point]
    - Tokenization occurs at: Nuvei hosted fields
    - Token storage: BeeLocal database (no raw PAN)

    **Annual Assessment**: PCI-DSS assessment required by [TODO: Date]
rationale: |
  UCR finding P0-2 identified missing PCI-DSS scope definition. Document
  mentions Nuvei integration but lacks SAQ level and scope boundary. This
  fix adds structured PCI scope section. Marked auto-assisted because
  [TODO] placeholders require domain input.
validated_by:
  - Auditor Fixer
  - QA Fixer
verification: |
  Verify section 7.2.4 exists with "SAQ-D" designation and scope boundary table.
  Flag remaining [TODO] items for manual completion.
```

### Example 3: Manual-Required Fix

```yaml
fix_id: FIX-P0-03
source_finding: P0-3
priority: P0
confidence: manual-required
target_file: BRD-01.6_functional_requirements.md
target_section: "6.3"
fix_type: add_section
fix_action:
  parent_section: "6.3"
  section_number: "6.3.5"
  heading: "Transaction Saga Pattern"
  content: |
    #### 6.3.5 Transaction Saga Pattern

    **Saga Orchestration**: [MANUAL: Define choreography vs orchestration approach]

    **Compensation Actions**:
    | Step | Forward Action | Compensation Action | Timeout |
    |------|---------------|---------------------|---------|
    | 1 | [MANUAL: Step 1] | [MANUAL: Rollback 1] | [MANUAL] |
    | 2 | [MANUAL: Step 2] | [MANUAL: Rollback 2] | [MANUAL] |

    **Idempotency Keys**: [MANUAL: Define idempotency strategy]

    **Failure Scenarios**:
    - Partial completion: [MANUAL: Define handling]
    - Network timeout: [MANUAL: Define retry policy]
rationale: |
  UCR finding P0-3 identified missing transaction saga/compensation patterns.
  This is marked manual-required because:
  1. Saga choreography vs orchestration is an architectural decision
  2. Compensation actions require business logic knowledge
  3. Timeout values need SLA alignment

  Template provided as scaffold; domain expert must complete [MANUAL] sections.
validated_by:
  - Architect Fixer
  - Devil's Advocate
devil_advocate_note: |
  This fix provides structure but does NOT solve the root problem. The actual
  saga pattern requires architectural decision. Recommend ADR before completing
  this section.
verification: |
  Verify section 6.3.5 exists. Count [MANUAL] placeholders - all must be
  resolved before marking complete. Verify ADR reference exists.
```

---

## Cross-Validation Results Section

When fixes conflict or require coordination:

```yaml
cross_validation:
  - conflict_id: CV-01
    fixes_involved: [FIX-P0-02, FIX-P1-05]
    conflict_type: location_overlap
    description: |
      Both fixes target section 7.2. FIX-P0-02 adds 7.2.4, FIX-P1-05 adds 7.2.4.
      Renumber FIX-P1-05 to 7.2.5.
    resolution: |
      Apply FIX-P0-02 first (P0 priority). Renumber FIX-P1-05 section to 7.2.5.
    resolved_by: Integration Fixer

  - conflict_id: CV-02
    fixes_involved: [FIX-P0-01, FIX-P1-03]
    conflict_type: semantic_conflict
    description: |
      FIX-P0-01 adds 24-hour review mandate. FIX-P1-03 references "automated
      SAR submission". These may conflict semantically.
    resolution: |
      Update FIX-P1-03 to reference "automated SAR preparation" (not submission).
      Submission requires human approval per FIX-P0-01.
    resolved_by: Auditor Fixer
```

---

## Execution Instructions Section

Ordered list for the execution agent:

```yaml
execution_order:
  - phase: 1
    description: "Apply auto-safe fixes"
    fixes: [FIX-P0-01, FIX-P1-01, FIX-P1-02]
    instruction: "Apply in order. No human review needed."

  - phase: 2
    description: "Apply auto-assisted fixes"
    fixes: [FIX-P0-02, FIX-P1-03]
    instruction: "Apply template. Flag [TODO] items for follow-up."

  - phase: 3
    description: "Manual review queue"
    fixes: [FIX-P0-03, FIX-P0-04]
    instruction: "Do not auto-apply. Create GitHub issues or manual tasks."

  - phase: 4
    description: "Post-fix verification"
    instruction: "Run UCR review on fixed document. Verify P0/P1 counts reduced."
```

---

## Validation Rules

### Required for All Fixes

1. `fix_id` must be unique within report
2. `source_finding` must reference valid finding from UCR report
3. `target_file` must be valid path (existence verified at execution)
4. `fix_action.text` or `fix_action.content` must be non-empty
5. `rationale` must explain WHY this fix addresses the finding
6. `validated_by` must have at least 1 persona

### Confidence Level Criteria

**auto-safe** requires ALL of:
- Deterministic text (no placeholders)
- Single location (no ambiguity)
- At least 2 persona validations
- No Devil's Advocate objections

**auto-assisted** requires ALL of:
- Template structure provided
- [TODO] or [MANUAL] placeholders clearly marked
- At least 1 persona validation

**manual-required** when ANY of:
- Architectural decision required
- Business logic needed
- Devil's Advocate raises objection
- Cross-validation conflict unresolved
- Domain knowledge required

---

## Machine Parsing

The execution agent MUST parse fix entries using:

1. Extract YAML code blocks between ` ```yaml ` and ` ``` `
2. Parse each block as YAML
3. Filter by `confidence` level
4. Sort by `execution_order.phase`
5. Apply `fix_action` based on `fix_type`

### Parsing Example (Python)

```python
import yaml
import re

def parse_ucrem_report(content: str) -> list[dict]:
    """Extract fix entries from UCRem report."""
    pattern = r'```yaml\n(fix_id:.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)

    fixes = []
    for match in matches:
        try:
            fix = yaml.safe_load(match)
            if 'fix_id' in fix:
                fixes.append(fix)
        except yaml.YAMLError:
            continue

    return sorted(fixes, key=lambda x: (
        0 if x['priority'] == 'P0' else 1 if x['priority'] == 'P1' else 2,
        0 if x['confidence'] == 'auto-safe' else 1 if x['confidence'] == 'auto-assisted' else 2
    ))
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-09 | Initial schema design |
