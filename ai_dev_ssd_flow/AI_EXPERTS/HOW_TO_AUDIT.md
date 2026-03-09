# How to Run an Expert Audit Workflow

The AI Expert Board operates using **Unified Context Review (UCR)** as the primary method. This SOP covers UCR execution, verification protocols, and troubleshooting.

---

## Core Philosophy

**FALSE NEGATIVES ARE UNACCEPTABLE.** Missing a real issue is far worse than flagging something that turns out to be present.

| Error Type | Risk Level | Consequence |
|------------|------------|-------------|
| **False Positive** | LOW | Extra verification during remediation - easily corrected |
| **False Negative** | **CRITICAL** | Missing requirements propagate downstream - expensive rework |

**Rule: When in doubt, FLAG IT.** It is better to flag 10 items and have 2 be false positives than to miss 1 critical gap.

---

## UCR Quick Start (Primary Method)

UCR is the recommended approach for all document validation. It applies multiple expert personas in a single context window with zero false negatives.

### Step 1: Select the Layer-Specific Prompt

| Document Type | Prompt File | Personas |
|---------------|-------------|----------|
| BRD (L1) | `UCR_PROMPT_BRD.md` | 9 |
| PRD (L2) | `UCR_PROMPT_PRD.md` | 10 |
| EARS (L3) | `UCR_PROMPT_EARS.md` | 5 |
| BDD (L4) | `UCR_PROMPT_BDD.md` | 6 |
| ADR (L5) | `UCR_PROMPT_ADR.md` | 7 |
| SYS (L6) | `UCR_PROMPT_SYS.md` | 6 |
| REQ (L7) | `UCR_PROMPT_REQ.md` | 5 |
| CTR (L8) | `UCR_PROMPT_CTR.md` | 5 |
| SPEC (L9) | `UCR_PROMPT_SPEC.md` | 5 |
| TSPEC (L10) | `UCR_PROMPT_TSPEC.md` | 5 |

### Step 2: Combine Prompt and Document

```bash
# Create combined review input
cat AI_EXPERTS/UCR_PROMPT_BRD.md > /tmp/review_input.md
echo "" >> /tmp/review_input.md
cat docs/01_BRD/BRD-01_platform_architecture/*.md >> /tmp/review_input.md
```

### Step 3: Run the Review

```bash
# Using Claude CLI (recommended: Opus 4.5)
claude -p --model opus < /tmp/review_input.md > docs/01_BRD/BRD-01_PERSONA_REVIEW_REPORT.md

# Using pipe method
cat AI_EXPERTS/UCR_PROMPT_BRD.md docs/01_BRD/*.md | claude -p --model opus > review_report.md
```

### UCR CLI Examples by Layer

```bash
# BRD Review
cat AI_EXPERTS/UCR_PROMPT_BRD.md docs/01_BRD/*.md | claude -p --model opus > brd_review.md

# PRD Review
cat AI_EXPERTS/UCR_PROMPT_PRD.md docs/02_PRD/*.md | claude -p --model opus > prd_review.md

# EARS Review
cat AI_EXPERTS/UCR_PROMPT_EARS.md docs/03_EARS/*.md | claude -p --model opus > ears_review.md

# BDD Review
cat AI_EXPERTS/UCR_PROMPT_BDD.md docs/04_BDD/*.feature | claude -p --model opus > bdd_review.md

# ADR Review
cat AI_EXPERTS/UCR_PROMPT_ADR.md docs/05_ADR/*.md | claude -p --model opus > adr_review.md
```

---

## Verification Protocol

Before claiming an item is PRESENT, the review must verify it meets ALL criteria:

1. **Explicitly stated** - Not implied, inferred, or "covered by" something else
2. **Specific and actionable** - Generic mentions don't count (e.g., "security" ≠ PCI-DSS scope)
3. **Complete specification** - Partial coverage is a GAP, not "present"

**IMPORTANT**: Even if something is mentioned, if it lacks implementation specifics, FLAG IT AS A GAP.

### Layer-Specific Verification Focus

| Layer | Verification Focus |
|-------|-------------------|
| **BRD** | Section 18 (Appendices), Section 7 (Quality), Section 8 (Constraints), Section 10 (Risk) |
| **PRD** | Section 18 (Technical), Section 8 (Acceptance Criteria), BRD refs |
| **EARS** | All EARS categories (Ubiquitous, Event, State, Optional, Unwanted) |
| **BDD** | All .feature files, Background sections, Scenario Outlines, negative scenarios |
| **ADR** | Alternatives Considered, Consequences (positive/negative/neutral), Related ADRs |
| **SYS** | Functional requirements, interface definitions, performance requirements |
| **REQ** | Atomic structure, traceability, verification criteria, INCOSE compliance |
| **CTR** | Schema definitions, versioning, backward compatibility, security |
| **SPEC** | Implementation details, error handling, dependencies, configuration |
| **TSPEC** | Test coverage, test data, automation hooks, test pyramid balance |

---

## Priority Classification (Conservative)

| Priority | Criteria | Default Stance |
|----------|----------|----------------|
| **P0** | Compliance, security, money movement, regulatory | **Flag as P0 unless explicitly complete** |
| **P1** | Integration contracts, operational gaps, architectural | Flag if specification is incomplete |
| **P2** | Enhancements, optimizations, nice-to-haves | Only for truly optional items |

### Domain-Specific P0 Defaults

For **Fintech/Compliance** documents:
- Regulatory requirements (FinCEN, OFAC, AML, KYC, SAR)
- Payment processing (PCI-DSS, card data, transaction integrity)
- Security controls (authentication, session management, encryption)
- Money movement (saga patterns, compensation, idempotency)

For **Healthcare** documents:
- HIPAA compliance requirements
- PHI handling and encryption
- Audit trail requirements

---

## Output Interpretation

### Remediation Format Requirements

Every finding MUST include:
1. **Target File**: Exact filename (e.g., `BRD-01.6_functional_requirements.md`)
2. **Target Section**: Specific section number (e.g., `Section 6.1.1`)
3. **Suggested Text**: Exact wording to add (not just "add more detail")

Example:
```markdown
| R1 | P0 | BRD-01.6_functional_requirements.md | 6.1 (BRD.01.01.07) | Add: "All SAR narratives MUST be reviewed by a licensed Compliance Officer within 24 hours" | Auditor |
```

### Handling Findings

1. **P0 Findings**: Block document progression. Create remediation tickets immediately.
2. **P1 Findings**: Schedule for current sprint. Document risk acceptance if deferred.
3. **P2 Findings**: Add to backlog. Implement during refactoring cycles.

### Verifying "Verified Present" Items

UCR reports include a "Verified Present" section listing items that were checked and confirmed in the document with exact quotes. This provides evidence that the review was thorough.

---

## Troubleshooting UCR Reviews

### Too Few Findings (Potential False Negatives)

**Symptom**: Report has very few P0/P1 findings for a complex document

**Cause**: Model being too lenient, not following conservative classification

**Fix**:
1. Verify prompt includes "FALSE NEGATIVES ARE UNACCEPTABLE" directive
2. Check that each persona has "skeptical stance" instructions
3. Use Claude Opus 4.5 (better at following conservative directives)
4. Add domain-specific P0 defaults to prompt

### High False Positive Rate (Excess Findings)

**Symptom**: Report claims items are missing that exist in the document

**Cause**: Model not following verification protocol

**Fix**:
1. Ensure prompt includes explicit verification steps
2. Add "Check Section 18 before claiming missing" directive
3. Add "Cite exact location and quote" requirement
4. Use model with larger context window

### Inconsistent Output Format

**Symptom**: Report doesn't follow template structure

**Cause**: Model not following structure directives

**Fix**:
1. Include explicit template in prompt with code block
2. Use lower temperature (0.1-0.3)
3. Add "Output MUST follow this exact format" directive

### Missing Remediation Specificity

**Symptom**: Remediations say "add more detail" instead of exact text

**Cause**: Prompt missing remediation format requirements

**Fix**:
1. Add explicit "Suggested Text: Exact wording to add" requirement
2. Include example remediation entry in prompt
3. Add "not just 'add more detail'" clarification

---

## Quality Verification Checklist

After running a UCR review, verify:

- [ ] Report has Executive Summary with recommendation
- [ ] P0/P1/P2 statistics provided
- [ ] All P0 findings have exact file path and section
- [ ] All remediations have suggested text (not just "fix it")
- [ ] "Verified Present" section has items with exact quotes
- [ ] Domain-specific items were checked (compliance, security, etc.)
- [ ] No obvious gaps in coverage (all personas represented)

---

## Domain Customization

For project-specific reviews, create domain-specific UCR prompts:

1. Copy base prompt: `cp UCR_PROMPT_BRD.md UCR_PROMPT_BRD_MYPROJECT.md`
2. Add domain-specific verification items
3. Add domain-specific P0 defaults
4. Add domain-specific terminology and partners
5. Test on sample document and verify quality

See [examples/beelocal_fintech_board.md](examples/beelocal_fintech_board.md) for fintech domain customization.

---

## Output Format: PERSONA_REVIEW_REPORT

All reviews produce reports following `PERSONA_REVIEW-MVP-TEMPLATE.md`:

```markdown
# PERSONA REVIEW REPORT: [Target Document]

> **Target Document**: DOC_ID (Version X.X)
> **Review Date**: YYYY-MM-DD
> **Method**: UCR (Unified Context Review)
> **Personas Applied**: N (Persona1, Persona2, ...)

## 1. Executive Summary
- **Recommendation**: (Proceed / Remediation Required / Fundamental Redesign)
- **Statistics**: X P0, Y P1, Z P2 findings

## 2. Critical Findings (P0)
| ID | Finding | Expert | Section | Impact |

## 3. High Priority Findings (P1)
| ID | Finding | Expert | Section | Impact |

## 4. Required Remediations
| ID | Priority | Target File | Section | Remediation Text | Source |

## 5. Enhancement Recommendations (P2)
## 6. Items Verified as Present
| Item | Location | Exact Specification |

## 7. Alternative Solutions (If Applicable)
```
