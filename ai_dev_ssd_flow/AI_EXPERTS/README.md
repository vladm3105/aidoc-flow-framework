# AI Expert Board - Unified Context Review (UCR)

## Overview

The **AI Expert Board** is an advanced QA and validation methodology built into `docs_flow_framework/ai_dev_ssd_flow`. It uses a **Unified Context Review (UCR)** approach where multiple expert personas review documents within a single context window, maintaining full document coherence.

### Core Philosophy

**FALSE NEGATIVES ARE UNACCEPTABLE.** Missing a real issue is far worse than flagging something that turns out to be present.

| Error Type | Risk Level | Consequence |
|------------|------------|-------------|
| **False Positive** | LOW | Extra verification during remediation - easily corrected |
| **False Negative** | **CRITICAL** | Missing requirements propagate downstream - expensive rework |

**Rule: When in doubt, FLAG IT.** It is better to flag 10 items and have 2 be false positives than to miss 1 critical gap.

### UCR Method Metrics

| Metric | Value |
|--------|-------|
| **False Negatives** | 0 (primary goal) |
| **Quality Score** | 95/100 |
| **Cost Efficiency** | 1 API call per review |
| **Context Coherence** | Full document maintained |

---

## Complete Layer-Persona Matrix

UCR applies layer-specific persona sets (5-10 personas depending on document type):

| Persona | L1 BRD | L2 PRD | L3 EARS | L4 BDD | L5 ADR | L6 SYS | L7 REQ | L8 CTR | L9 SPEC | L10 TSPEC |
|---------|:------:|:------:|:-------:|:------:|:------:|:------:|:------:|:------:|:-------:|:---------:|
| **Architect** | ✓ | ✓ | - | - | ✓ | ✓ | - | ✓ | ✓ | - |
| **Auditor** | ✓ | ✓ | - | ✓* | ✓ | - | - | ✓ | - | - |
| **Tech Lead** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Strategist** | ✓ | ✓ | - | - | ✓ | - | - | - | - | - |
| **Devil's Advocate** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Operator** | ✓ | ✓ | - | ✓ | ✓ | ✓ | - | - | ✓ | ✓ |
| **Integration Lead** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Product Owner** | ✓ | ✓ | - | - | - | - | - | - | - | - |
| **Business Analyst** | ✓ | - | - | - | - | - | - | - | - | - |
| **QA Lead** | - | ✓ | ✓ | ✓ | - | ✓ | ✓ | - | - | ✓ |
| **Requirements Specialist** | - | - | ✓ | - | - | - | ✓ | - | - | - |
| **UX Strategist** | - | ✓ | - | - | - | - | - | - | - | - |
| **Count** | **9** | **10** | **5** | **6** | **7** | **6** | **5** | **5** | **5** | **5** |

*Auditor for BDD only when compliance scenarios exist

---

## Quick Start

### Step 1: Select Layer Prompt

```bash
# Copy the appropriate UCR prompt for your document type
cp AI_EXPERTS/UCR_PROMPT_BRD.md /tmp/review_prompt.md
```

### Step 2: Append Your Document

```bash
# Append your document content to the prompt
cat path/to/your/BRD-01.md >> /tmp/review_prompt.md
```

### Step 3: Run the Review

```bash
# Run with Claude Opus 4.5 (recommended)
claude -p --model opus < /tmp/review_prompt.md > audit_report.md

# Alternative: pipe method
cat AI_EXPERTS/UCR_PROMPT_BRD.md docs/01_BRD/*.md | claude -p --model opus > audit_report.md
```

### CLI Examples by Layer

| Document Type | Command |
|---------------|---------|
| **BRD (L1)** | `cat UCR_PROMPT_BRD.md docs/01_BRD/*.md \| claude -p --model opus > brd_review.md` |
| **PRD (L2)** | `cat UCR_PROMPT_PRD.md docs/02_PRD/*.md \| claude -p --model opus > prd_review.md` |
| **EARS (L3)** | `cat UCR_PROMPT_EARS.md docs/03_EARS/*.md \| claude -p --model opus > ears_review.md` |
| **BDD (L4)** | `cat UCR_PROMPT_BDD.md docs/04_BDD/*.feature \| claude -p --model opus > bdd_review.md` |
| **ADR (L5)** | `cat UCR_PROMPT_ADR.md docs/05_ADR/*.md \| claude -p --model opus > adr_review.md` |
| **SYS (L6)** | `cat UCR_PROMPT_SYS.md docs/06_SYS/*.md \| claude -p --model opus > sys_review.md` |
| **REQ (L7)** | `cat UCR_PROMPT_REQ.md docs/07_REQ/*.yaml \| claude -p --model opus > req_review.md` |
| **CTR (L8)** | `cat UCR_PROMPT_CTR.md docs/08_CTR/*.yaml \| claude -p --model opus > ctr_review.md` |
| **SPEC (L9)** | `cat UCR_PROMPT_SPEC.md docs/09_SPEC/*.yaml \| claude -p --model opus > spec_review.md` |
| **TSPEC (L10)** | `cat UCR_PROMPT_TSPEC.md docs/10_TSPEC/*.yaml \| claude -p --model opus > tspec_review.md` |

---

## Priority Classification (Conservative)

| Priority | Criteria | Default Stance |
|----------|----------|----------------|
| **P0** | Compliance, security, money movement, regulatory | **Flag as P0 unless explicitly complete** |
| **P1** | Integration contracts, operational gaps, architectural | Flag if specification is incomplete |
| **P2** | Enhancements, optimizations, nice-to-haves | Only for truly optional items |

### Domain-Specific P0 Defaults

For **Fintech/Compliance** documents, err heavily toward P0 for:
- Regulatory requirements (FinCEN, OFAC, AML, KYC, SAR)
- Payment processing (PCI-DSS, card data, transaction integrity)
- Security controls (authentication, session management, encryption)
- Money movement (saga patterns, compensation, idempotency)

---

## Verification Protocol

Before claiming an item is PRESENT, verify it meets ALL criteria:
1. **Explicitly stated** - Not implied, inferred, or "covered by" something else
2. **Specific and actionable** - Generic mentions don't count (e.g., "security" ≠ PCI-DSS scope)
3. **Complete specification** - Partial coverage is a GAP, not "present"

**IMPORTANT**: Even if something is mentioned, if it lacks implementation specifics, FLAG IT AS A GAP.

---

## Output Format

UCR produces reports using `PERSONA_REVIEW-MVP-TEMPLATE.md`:

```markdown
# PERSONA REVIEW REPORT: [Target Document]

## 1. Executive Summary
- Recommendation: (Proceed / Remediation Required / Fundamental Redesign)
- Statistics: X P0, Y P1, Z P2 findings

## 2. Critical Findings (P0)
| ID | Finding | Expert | Section | Impact |

## 3. High Priority Findings (P1)
| ID | Finding | Expert | Section | Impact |

## 4. Required Remediations
| ID | Priority | Target File | Section | Remediation Text | Source |
|----|----------|-------------|---------|------------------|--------|
| R1 | P0 | `exact_filename.md` | X.X | "Exact text to add" | Expert |

## 5. Enhancement Recommendations (P2)
## 6. Items Verified as Present
| Item | Location | Exact Specification |

## 7. Alternative Solutions (If Fundamental Redesign)
```

### Remediation Format Requirements

Every finding MUST include:
1. **Target File**: Exact filename (e.g., `BRD-01.6_functional_requirements.md`)
2. **Target Section**: Specific section number (e.g., `Section 6.1.1`)
3. **Suggested Text**: Exact wording to add (not just "add more detail")

---

## Prompt Files

| Layer | Prompt File | Personas |
|-------|-------------|----------|
| L1 BRD | [UCR_PROMPT_BRD.md](UCR_PROMPT_BRD.md) | 9 |
| L2 PRD | [UCR_PROMPT_PRD.md](UCR_PROMPT_PRD.md) | 10 |
| L3 EARS | [UCR_PROMPT_EARS.md](UCR_PROMPT_EARS.md) | 5 |
| L4 BDD | [UCR_PROMPT_BDD.md](UCR_PROMPT_BDD.md) | 6 |
| L5 ADR | [UCR_PROMPT_ADR.md](UCR_PROMPT_ADR.md) | 7 |
| L6 SYS | [UCR_PROMPT_SYS.md](UCR_PROMPT_SYS.md) | 6 |
| L7 REQ | [UCR_PROMPT_REQ.md](UCR_PROMPT_REQ.md) | 5 |
| L8 CTR | [UCR_PROMPT_CTR.md](UCR_PROMPT_CTR.md) | 5 |
| L9 SPEC | [UCR_PROMPT_SPEC.md](UCR_PROMPT_SPEC.md) | 5 |
| L10 TSPEC | [UCR_PROMPT_TSPEC.md](UCR_PROMPT_TSPEC.md) | 5 |

---

## Persona Skills Reference

| Persona | Skill File | Focus | Stance |
|---------|------------|-------|--------|
| Architect | [skills/architect.md](skills/architect.md) | System design, scalability | Skeptical - assume gaps exist |
| Auditor | [skills/auditor.md](skills/auditor.md) | Compliance, security | Non-compliant until proven |
| Tech Lead | [skills/tech_lead.md](skills/tech_lead.md) | Implementation feasibility | Details matter |
| Strategist | [skills/strategist.md](skills/strategist.md) | Economics, trade-offs | Validate assumptions |
| Devil's Advocate | [skills/devils_advocate.md](skills/devils_advocate.md) | Edge cases, failure modes | If not documented, it will fail |
| Operator | [skills/operator.md](skills/operator.md) | Observability, deployment | Not production-ready if not observable |
| Integration Lead | [skills/integration_expert.md](skills/integration_expert.md) | Dependencies, contracts | Failures cascade |
| Product Owner | [skills/product_owner.md](skills/product_owner.md) | Business value, scope | Scope creep kills projects |
| Business Analyst | [skills/business_analyst.md](skills/business_analyst.md) | Requirements completeness | Ambiguity causes disputes |
| QA Lead | [skills/qa_lead.md](skills/qa_lead.md) | Testability, BDD syntax | Untestable = unimplementable |
| Requirements Specialist | [skills/requirements_specialist.md](skills/requirements_specialist.md) | EARS/INCOSE syntax | Strict syntax enforcement |
| UX Strategist | [skills/ux_strategist.md](skills/ux_strategist.md) | User journey, accessibility | UX gaps cause churn |

---

## Domain Customization

For project-specific reviews, create domain-specific UCR prompts:

```bash
# Example: Create BeeLocal-specific BRD prompt
cp UCR_PROMPT_BRD.md UCR_PROMPT_BRD_BEELOCAL.md
# Add domain-specific verification items (partners, regulations, terminology)
```

See [examples/beelocal_fintech_board.md](examples/beelocal_fintech_board.md) for a fintech domain example.

---

## Documentation Reference

1. [UCR Method Guide](UNIFIED_CONTEXT_REVIEW.md) - Primary method documentation
2. [Persona Design Guide](PERSONA_DESIGN_GUIDE.md) - 12 persona archetypes
3. [How to Audit](HOW_TO_AUDIT.md) - Step-by-step audit instructions
4. [Output Template](PERSONA_REVIEW-MVP-TEMPLATE.md) - Report format

---

## Model Recommendations

UCR performs best with models that:
- Support large context windows (100K+ tokens)
- Have strong reasoning capabilities
- Maintain coherent multi-persona synthesis
- Follow conservative classification directives

**Recommended**: Claude Opus 4.5 (primary), Claude Sonnet 4 (faster), Gemini 2.5 Pro
