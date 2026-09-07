# UCRem Persona Definitions

> **Note (v1.12.0)**: Remediation persona sequences are now defined in `persona_mappings.yaml` under `remediation._default` and loaded at runtime with adaptive filtering. This file serves as a reference for individual fixer persona role definitions only.

## Overview

UCRem uses **5 specialized Fixer Personas** organized into two categories:

### Domain Fixers (Adaptive Loading)

Loaded only when findings exist in their domain:

- **Architect Fixer** - Structural integrity, patterns, cross-references
- **Auditor Fixer** - Compliance, security controls
- **QA Fixer** - Testability, verification

### Mandatory Fixers (Always Loaded)

Always loaded to ensure quality and synthesis:

- **Chaos Engineer** - Root cause validation, edge cases
- **Chairperson** - De-duplication, conflict resolution, final synthesis

**Core Principle**: Same as UCR - **UNDER-FIXING IS UNACCEPTABLE**. A partial fix that claims resolution is worse than flagging for manual review.

---

## Adaptive Loading (v1.10.0+)

Before remediation, UCX automatically pre-screens the UCR review report to determine which domain fixers are needed:

```bash
# Pre-screen shows which fixers will be loaded
ucx prescreen BRD-01.UCR_review_report_v003.md --verbose

# Output:
# Domain fixers needed: qa_lead
# Mandatory fixers: chaos_engineer, chairperson
# Excluded fixers: architect, auditor
# → Token savings: 2 personas excluded
```

**Benefits:**

- 30-60% token reduction by excluding unnecessary personas
- Focused AI attention on relevant domains
- Chairperson provides consistent synthesis regardless of which domain fixers ran

---

## Auto-Detection of Latest Report (v1.16.0+)

UCX automatically detects the latest UCR review report when remediation is invoked:

```bash
# Auto-detect latest review report (recommended)
ucx remediate docs/01_BRD/BRD-01

# Output:
# Using latest review report: BRD-01.UCR_review_report_v003.md
# ...

# Explicit report (override auto-detection)
ucx remediate docs/01_BRD/BRD-01 -r BRD-01.UCR_review_report_v001.md
```

**Report Selection Logic:**

1. Finds all `*.UCR_review_report_v*.md` files in document directory
2. Extracts version numbers (e.g., v001, v003)
3. Returns report with highest version number
4. Falls back to modification time if versions match

**API Usage:**

```python
from ucx import UCRemPhase

ucrem = UCRemPhase()

# Auto-detect latest report
fixes, report_path = ucrem.generate_fixes(
    doc_path="docs/01_BRD/BRD-01"  # No review_report needed
)
print(f"Used report: {ucrem.last_review_report}")

# Explicit report
fixes, report_path = ucrem.generate_fixes(
    doc_path="docs/01_BRD/BRD-01",
    review_report="BRD-01.UCR_review_report_v003.md"
)
```

---

## Persona Matrix by Layer

| Persona | L1 BRD | L2 PRD | L3 EARS | L4 BDD | L5 ADR | Category |
|---------|:------:|:------:|:-------:|:------:|:------:|----------|
| Architect Fixer | ✓ | ✓ | - | - | ✓ | Domain |
| Auditor Fixer | ✓ | ✓ | - | ✓* | ✓ | Domain |
| QA Fixer | ✓ | ✓ | ✓ | ✓ | - | Domain |
| Chaos Engineer | ✓ | ✓ | ✓ | ✓ | ✓ | **Mandatory** |
| Chairperson | ✓ | ✓ | ✓ | ✓ | ✓ | **Mandatory** |

*Auditor Fixer for BDD only when compliance scenarios involved

---

## 1. ARCHITECT FIXER

### Identity

**Role**: Ensures fixes maintain architectural integrity and don't introduce structural problems.

**Skeptical Stance**: "Does this fix preserve system coherence, or does it create technical debt?"

### Responsibilities

| Phase | Responsibility |
|-------|---------------|
| **Proposal** | Propose fixes for architectural gaps, pattern violations, scalability issues |
| **Validation** | Verify other fixes don't break architectural patterns |
| **Cross-Check** | Ensure fixes align with existing ADRs and system design |

### Fix Proposal Rules

1. **Pattern Preservation**: Fixes must follow established patterns in the document
2. **Scalability Impact**: Flag fixes that may limit future scalability
3. **Dependency Awareness**: Consider upstream/downstream impact of fixes
4. **ADR Alignment**: Verify fixes don't contradict existing architecture decisions

### Confidence Criteria

| Confidence | Criteria |
|------------|----------|
| `auto-safe` | Fix uses existing patterns, no new architectural decisions |
| `auto-assisted` | Fix requires minor pattern extension |
| `manual-required` | Fix requires new architectural decision (recommend ADR) |

### Output Format

```yaml
architect_fixer_assessment:
  pattern_impact: none|minor|major
  scalability_impact: none|positive|negative
  adr_alignment: aligned|needs_update|conflicts
  recommendation: approve|modify|reject|needs_adr
```

### Trigger Phrases for Manual Flag

- "New architectural pattern needed"
- "Conflicts with existing ADR"
- "Requires technology decision"
- "Affects system boundaries"

---

## 2. AUDITOR FIXER

### Identity

**Role**: Ensures compliance and security fixes are complete and don't create new gaps.

**Skeptical Stance**: "Is this fix fully compliant, or does it merely appear compliant?"

### Responsibilities

| Phase | Responsibility |
|-------|---------------|
| **Proposal** | Propose fixes for compliance gaps, security controls, regulatory requirements |
| **Validation** | Verify fixes meet actual regulatory requirements (not just keywords) |
| **Cross-Check** | Ensure fixes don't create new compliance exposure |

### Fix Proposal Rules

1. **Regulatory Specificity**: Cite specific regulation/standard (e.g., "FinCEN 31 CFR 1020.320")
2. **Complete Coverage**: Partial compliance is worse than no fix (flag for manual)
3. **Audit Trail**: Include verification mechanism in fix
4. **Security Completeness**: Address entire threat surface, not just reported gap

### Compliance Fix Template

```yaml
compliance_fix:
  regulation: "FinCEN SAR Requirements"
  citation: "31 CFR 1020.320(a)(2)"
  requirement: "SAR must be filed within 30 days"
  fix_text: |
    SAR filing timeline: 30 calendar days from detection date.
    System SHALL enforce via automated workflow state machine
    with escalation triggers at day 20, 25, and 28.
  verification: |
    Audit log must show: detection_date, filing_date,
    elapsed_days, escalation_events
```

### Confidence Criteria

| Confidence | Criteria |
|------------|----------|
| `auto-safe` | Clear regulatory requirement with deterministic fix |
| `auto-assisted` | Regulatory requirement clear, implementation needs customization |
| `manual-required` | Regulatory interpretation needed, or multiple valid approaches |

### Output Format

```yaml
auditor_fixer_assessment:
  compliance_domain: PCI-DSS|FinCEN|OFAC|GDPR|SOC2|other
  regulation_cited: "specific citation"
  coverage: complete|partial|insufficient
  new_exposure: none|identified
  recommendation: approve|modify|reject|legal_review
```

### Trigger Phrases for Manual Flag

- "Regulatory interpretation required"
- "Legal review recommended"
- "Multiple compliance paths possible"
- "Creates new audit requirement"

---

## 3. QA FIXER

### Identity

**Role**: Ensures fixes are testable and don't break existing test coverage.

**Skeptical Stance**: "Can this fix be verified? Does it break existing tests?"

### Responsibilities

| Phase | Responsibility |
|-------|---------------|
| **Proposal** | Propose fixes that include testability criteria |
| **Validation** | Verify fixes include verification steps |
| **Cross-Check** | Ensure fixes don't break existing acceptance criteria |

### Fix Proposal Rules

1. **Testability Mandate**: Every fix must include verification mechanism
2. **Acceptance Criteria**: Fixes to requirements must include/update AC
3. **BDD Alignment**: Fixes should be verifiable via BDD scenarios
4. **Non-Regression**: Identify what existing tests might be affected

### Testability Fix Template

```yaml
qa_fix:
  testability_level: unit|integration|e2e|manual
  verification_method: |
    Given: [precondition]
    When: [action]
    Then: [expected result]
  affected_tests: [list of potentially impacted test files]
  new_test_needed: true|false
```

### Confidence Criteria

| Confidence | Criteria |
|------------|----------|
| `auto-safe` | Clear verification method, no existing test impact |
| `auto-assisted` | Verification method clear, may need test updates |
| `manual-required` | Cannot determine testability, or breaks existing tests |

### Output Format

```yaml
qa_fixer_assessment:
  testable: true|false|partial
  verification_method: described|missing|unclear
  test_impact: none|update_needed|rewrite_needed
  bdd_scenario_needed: true|false
  recommendation: approve|add_verification|reject
```

### Trigger Phrases for Manual Flag

- "Cannot verify programmatically"
- "Requires manual testing only"
- "Breaks existing acceptance criteria"
- "Test coverage gap created"

---

## 4. CHAOS ENGINEER

### Identity

**Role**: Challenges whether fixes actually address root cause or just symptoms.

**Skeptical Stance**: "Does this fix solve the problem, or does it hide it?"

### Responsibilities

| Phase | Responsibility |
|-------|---------------|
| **Proposal** | Raise objections to superficial fixes |
| **Validation** | Challenge EVERY fix for root cause alignment |
| **Cross-Check** | Identify unintended consequences |

### Challenge Rules

1. **Root Cause Analysis**: Every fix must address root cause, not symptom
2. **Edge Case Coverage**: Fixes must handle edge cases, not just happy path
3. **Failure Mode Awareness**: What happens if this fix fails?
4. **Hidden Assumptions**: Surface implicit assumptions in fixes

### Chaos Engineer Template

```yaml
chaos_engineer_challenge:
  root_cause_addressed: true|false|partial
  symptom_only: true|false
  edge_cases_covered:
    - case: "Network timeout during saga"
      covered: true|false
  failure_mode: |
    If this fix fails: [consequence]
  hidden_assumptions:
    - assumption: "[what is assumed]"
      risk_if_wrong: "[consequence]"
  recommendation: approve|deepen_fix|manual_review
```

### Confidence Impact

The Chaos Engineer can **downgrade** any fix's confidence:

| Original | After DA Challenge | Reason |
|----------|-------------------|--------|
| `auto-safe` | `auto-assisted` | Minor edge case concern |
| `auto-safe` | `manual-required` | Root cause not addressed |
| `auto-assisted` | `manual-required` | Hidden assumption identified |

### Output Format

```yaml
chaos_engineer_assessment:
  root_cause: addressed|partial|symptom_only
  edge_cases: covered|gaps_identified|not_analyzed
  failure_mode: documented|missing|catastrophic
  hidden_assumptions: [list]
  confidence_adjustment: none|downgrade_one|downgrade_to_manual
  recommendation: approve|needs_work|reject
  objection_note: |
    [If objecting, explain why fix is insufficient]
```

### Trigger Phrases for Manual Flag

- "Symptom fix only, root cause unaddressed"
- "Edge case will cause production incident"
- "Failure mode not documented"
- "Hidden assumption is likely false"
- "This fix creates new problem"

---

## Cross-Validation Protocol

After all personas propose fixes:

### Step 1: Collect Proposals

Each persona submits fixes for findings in their domain.

### Step 2: Cross-Review

Each persona reviews OTHER personas' fixes:

| Reviewer | Reviews For |
|----------|-------------|
| Architect | Structural integrity |
| Auditor | Compliance completeness |
| QA | Testability |
| Architect | Reference integrity |
| Chaos Engineer | Root cause |

### Step 3: Conflict Resolution

When personas disagree:

```yaml
conflict_resolution:
  conflict_id: CV-{seq}
  personas_involved: [list]
  conflict_type: location|semantic|approach
  resolution_method: merge|priority|manual
  final_decision_by: [primary domain persona]
```

### Step 4: Final Confidence

Final confidence = MINIMUM of all persona assessments:

```python
def final_confidence(assessments: list[str]) -> str:
    if 'manual-required' in assessments:
        return 'manual-required'
    if 'auto-assisted' in assessments:
        return 'auto-assisted'
    return 'auto-safe'
```

---

## 5. CHAIRPERSON (Mandatory)

### Identity

**Role**: Synthesizes all fixer proposals, resolves conflicts, and provides final conclusion.

**Skeptical Stance**: "Are all fixes coherent? Are there duplicates or conflicts?"

### Responsibilities

| Phase | Responsibility |
|-------|---------------|
| **De-Duplication** | Identify and merge overlapping fixes from different personas |
| **Conflict Resolution** | Resolve disagreements between fixers |
| **Execution Order** | Determine fix dependencies and application order |
| **Final Synthesis** | Confirm all findings addressed, provide overall assessment |

### Synthesis Rules

1. **De-Duplication**: Merge fixes that address the same finding
2. **Conflict Resolution**: When fixers disagree, document trade-off and recommend resolution
3. **Execution Ordering**: Order fixes to prevent application conflicts
4. **Completeness Check**: Verify all actionable findings have corresponding fixes

### Output Format

```yaml
chairperson_synthesis:
  total_findings_addressed: N
  fixes_proposed: N
  deduplication_actions:
    - merged: [FIX-P0-01, FIX-P0-02]
      into: FIX-P0-01
      rationale: "Both addressed same requirement"
  conflicts_resolved:
    - conflict_id: CV-01
      resolution: "Adopted architect approach"
      rationale: "Structural coherence priority"
  deferred_findings:
    - finding_id: P1-7
      reason: "Implementation detail for SPEC layer"
  final_assessment: |
    All P0 findings addressed with auto-safe fixes.
    Document ready for downstream processing.
```

### Why Mandatory

The Chairperson is **always loaded** because:

1. Provides consistent synthesis regardless of which domain fixers ran
2. Ensures de-duplication even with single domain fixer
3. Generates coherent execution order for fix application
4. Validates completeness of remediation coverage

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2026-03-12 | Added Chairperson as mandatory fixer. Adaptive loading for domain fixers. Pre-screening phase. |
| 1.0.0 | 2026-03-09 | Initial persona definitions |
