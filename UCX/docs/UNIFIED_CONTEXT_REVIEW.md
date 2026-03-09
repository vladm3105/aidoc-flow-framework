# Unified Context Review (UCR) Method Guide

## Overview

**Unified Context Review (UCR)** is the primary document validation method for the AI Expert Board framework. UCR uses a single-pass approach that maintains full document context throughout the review, applying multiple expert personas in a unified analysis.

### Core Philosophy

**FALSE NEGATIVES ARE UNACCEPTABLE.** Missing a real issue is far worse than flagging something that turns out to be present.

| Error Type | Risk Level | Consequence |
|------------|------------|-------------|
| **False Positive** | LOW | Extra verification during remediation - easily corrected |
| **False Negative** | **CRITICAL** | Missing requirements propagate downstream - expensive rework |

**Rule: When in doubt, FLAG IT.** It is better to flag 10 items and have 2 be false positives than to miss 1 critical gap.

### Key Metrics

| Metric | UCR Value |
|--------|-----------|
| **False Negatives** | 0 (primary goal) |
| **Quality Score** | 95/100 |
| **Cost Efficiency** | 1 API call per review |
| **Context Coherence** | Full document context maintained |

---

## Quick Start

### Using UCX CLI (Recommended)

```bash
# Activate venv
source /opt/data/docs_flow_framework/.venv/bin/activate

# Run UCR validation
ucx review <doc_type> <document_path>

# Examples
ucx review brd docs/01_BRD/BRD-01_platform_architecture/
ucx review prd docs/02_PRD/PRD-01.md
ucx review ears docs/03_EARS/
ucx review bdd docs/04_BDD/
```

CLI features:
- **Auto-selects prompt** based on document type
- **Loads persona skills** dynamically
- **Outputs review report** to document directory
- **LiteLLM support** for multiple providers

Environment variables:
```bash
UCX_MODEL=opus           # LLM model (opus, sonnet, haiku, or LiteLLM format)
UCX_API_BASE=            # Custom API endpoint (for proxies, Ollama, etc.)
```

### Using Python API

```python
from ucx import UCRPhase, UCXConfig
from pathlib import Path

config = UCXConfig(model="opus", min_score=90)
ucr = UCRPhase(config)

result = ucr.review(
    doc_type="brd",
    doc_path=Path("docs/01_BRD/BRD-01_platform_architecture/"),
)

print(f"Score: {result.score}")
print(f"P0 findings: {len([f for f in result.findings if f.priority == 'P0'])}")
```

### Using Other LLM Providers

```bash
# OpenAI
UCX_MODEL="openai/gpt-4o" ucx review brd docs/01_BRD/BRD-01.md

# Local Ollama (free)
UCX_MODEL="ollama/llama3" UCX_API_BASE="http://localhost:11434" ucx review brd docs/01_BRD/BRD-01.md
```

### Layer Selection Guide

| Document Type | Prompt File | Personas |
|---------------|-------------|----------|
| BRD (L1) | `UCR_PROMPT_BRD.md` | 9 personas |
| PRD (L2) | `UCR_PROMPT_PRD.md` | 10 personas |
| EARS (L3) | `UCR_PROMPT_EARS.md` | 5 personas |
| BDD (L4) | `UCR_PROMPT_BDD.md` | 6 personas |
| ADR (L5) | `UCR_PROMPT_ADR.md` | 7 personas |
| SYS (L6) | `UCR_PROMPT_SYS.md` | 6 personas |
| REQ (L7) | `UCR_PROMPT_REQ.md` | 5 personas |
| CTR (L8) | `UCR_PROMPT_CTR.md` | 5 personas |
| SPEC (L9) | `UCR_PROMPT_SPEC.md` | 5 personas |
| TSPEC (L10) | `UCR_PROMPT_TSPEC.md` | 5 personas |

---

## How UCR Works

### Single-Pass Architecture

Unlike multi-model pipelines that fragment context across multiple API calls, UCR:

1. **Loads full document** into a single conversation context
2. **Applies all personas sequentially** within that context
3. **Cross-references findings** automatically (no missed connections)
4. **Synthesizes results** with full visibility into all sections

### Verification Protocol

Before claiming an item is PRESENT, verify it meets ALL criteria:

1. **Explicitly stated** - Not implied, inferred, or "covered by" something else
2. **Specific and actionable** - Generic mentions don't count (e.g., "security" ≠ PCI-DSS scope)
3. **Complete specification** - Partial coverage is a GAP, not "present"

**IMPORTANT**: Even if something is mentioned, if it lacks implementation specifics, FLAG IT AS A GAP.

### Cross-Reference Sections

Each layer-specific prompt includes mandatory cross-reference checks:

```
Sections to Cross-Reference:
- Section 18 (Appendices) - Technology conditions, retry patterns, integrations
- Section 7 (Quality Attributes) - Security, performance, observability specs
- Section 8 (Constraints) - Business, technical, regulatory constraints
- Section 10 (Risk Analysis) - Mitigations may contain specifications
```

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

---

## Persona Architecture

### Persona Stance

Each persona operates with a **skeptical stance**:

| Persona | Skeptical Stance |
|---------|------------------|
| **Architect** | Assume architectural gaps exist until proven otherwise |
| **Auditor** | Assume non-compliant until explicitly proven compliant |
| **Tech Lead** | Implementation details matter - vague specs cause bugs |
| **Strategist** | Financial assumptions must be validated |
| **Devil's Advocate** | If failure mode isn't documented, it WILL happen |
| **Operator** | If it can't be observed and rolled back, not production-ready |
| **Integration Lead** | Integration failures cascade - every dependency is a risk |
| **Product Owner** | Scope creep kills projects - MVP must be ruthlessly bounded |
| **QA Lead** | Untestable requirements are unimplementable |
| **Requirements Specialist** | Syntax violations are P0 - no exceptions |
| **Business Analyst** | Ambiguous requirements cause implementation disputes |
| **UX Strategist** | UX gaps cause user churn - accessibility is non-negotiable |

### Layer-Specific Personas

| Persona | Layers | Focus |
|---------|--------|-------|
| **Architect** | L1, L2, L5, L6, L8, L9 | System design, scalability, patterns |
| **Auditor** | L1, L2, L4*, L5, L8 | Compliance, security, regulatory |
| **Operator** | L1, L2, L4, L5, L6, L9, L10 | Observability, deployment, SLIs/SLOs |
| **QA Lead** | L2, L3, L4, L6, L7, L10 | Testability, coverage, BDD syntax |
| **Strategist** | L1, L2, L5 | Costs, economics, trade-offs |
| **Product Owner** | L1, L2 | Business value, scope, MVP boundaries |
| **Requirements Specialist** | L3, L7 | EARS/INCOSE syntax, atomic structure |
| **Business Analyst** | L1 | Stakeholder coverage, requirements completeness |
| **UX Strategist** | L2 | User journey, accessibility, friction points |

*Auditor for L4 (BDD) only when compliance scenarios exist

---

## Output Format

UCR reviews produce reports using the **PERSONA_REVIEW-MVP-TEMPLATE.md** format:

```markdown
# PERSONA REVIEW REPORT: [Target Document]

> **Target Document**: DOC_ID (Version X.X)
> **Review Date**: YYYY-MM-DD
> **Method**: UCR (Unified Context Review)
> **Personas Applied**: N (Persona1, Persona2, ...)

## 1. Executive Summary
- **Recommendation**: (Proceed / Remediation Required / Fundamental Redesign)
- **Statistics**: X P0, Y P1, Z P2 findings
- **Blocking Issues**: [List P0 items]

## 2. Critical Findings (P0)
| ID | Finding | Expert | Section | Impact |

## 3. High Priority Findings (P1)
| ID | Finding | Expert | Section | Impact |

## 4. Required Remediations
| ID | Priority | Target File | Section | Remediation Text | Source |

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

## Best Practices

### Before Review

1. **Complete document first** - UCR is for validation, not co-authoring
2. **Include all appendices** - Section 18 content is critical for verification
3. **Check cross-references** - Ensure all `@brd:`, `@prd:` tags are resolvable

### During Review

1. **Use full document** - Don't truncate for token limits; use capable models
2. **Trust the conservative classification** - P0 until proven otherwise
3. **Note section references** - UCR provides exact section locations for findings

### After Review

1. **Prioritize P0 findings** - Block sign-off until resolved
2. **Verify "Verified Present" items** - Use as quality check for review thoroughness
3. **Document remediation** - Update document with exact suggested text

---

## Domain Customization

For project-specific reviews, create domain-specific UCR prompts:

1. Copy base prompt: `cp UCR_PROMPT_BRD.md UCR_PROMPT_BRD_MYPROJECT.md`
2. Add domain-specific verification items (partners, regulations, terminology)
3. Add domain-specific P0 defaults
4. Add domain-specific persona focus areas
5. Test on sample document and verify quality

See [examples/beelocal_fintech_board.md](examples/beelocal_fintech_board.md) for fintech domain customization.

---

## Model Recommendations

UCR performs best with models that:

- Support large context windows (100K+ tokens)
- Have strong reasoning capabilities
- Can maintain coherent multi-persona synthesis
- Follow conservative classification directives

Recommended models (as of 2026):
- Claude Opus 4.5 (primary - best conservative classification)
- Claude Sonnet 4 (faster alternative)
- Gemini 2.5 Pro

---

## Troubleshooting

### Too Few Findings (Potential False Negatives)

**Symptom**: Report has very few P0/P1 findings for a complex document

**Cause**: Model being too lenient, not following conservative classification

**Fix**:
1. Verify prompt includes "FALSE NEGATIVES ARE UNACCEPTABLE" directive
2. Check that each persona has "skeptical stance" instructions
3. Use Claude Opus 4.5 (better at following conservative directives)
4. Add domain-specific P0 defaults to prompt

### High False Positive Rate

**Cause**: Model not following verification protocol

**Fix**:
1. Ensure prompt includes explicit verification steps
2. Add "Check Section 18 before claiming missing" directive
3. Add "Cite exact location and quote" requirement

### Missing Remediation Specificity

**Symptom**: Remediations say "add more detail" instead of exact text

**Fix**:
1. Add explicit "Suggested Text: Exact wording to add" requirement
2. Include example remediation entry in prompt

---

---

## UCRem (Remediation) Integration

After UCR validation, use **UCRem (Unified Context Remediation)** to generate executable fix proposals.

### UCRem Workflow

```bash
# Step 1: Run UCR validation (produces review report)
ucx review brd docs/01_BRD/BRD-01/

# Step 2: Run UCRem remediation (produces fix proposals)
ucx remediate brd docs/01_BRD/BRD-01/ --review-report docs/01_BRD/BRD-01/BRD_UCR_REVIEW.md

# Step 3: Apply fixes (via Claude skill)
/doc-brd-fixer BRD-01 --from-ucrem BRD_UCRem_REPORT.md

# Step 4: Re-validate
ucx review brd docs/01_BRD/BRD-01/
```

### UCRem Confidence Levels

| Level | Criteria | Execution |
|-------|----------|-----------|
| **auto-safe** | Deterministic text, 2+ personas approve | Apply automatically |
| **auto-assisted** | Template with [TODO] placeholders | Apply, complete placeholders |
| **manual-required** | Architectural/regulatory decision needed | Create task for expert |

See `UCRem_PROMPT_BRD.md` and `UCRem_REPORT_SCHEMA.md` for full documentation.

---

## Dynamic Skill Loading

UCR uses persona skill files from `skills/` directory to provide domain knowledge. Skills are loaded automatically by runner scripts based on document type.

### Layer-to-Skills Mapping

| Layer | Skills Loaded |
|-------|---------------|
| BRD | architect, auditor, tech_lead, strategist, devils_advocate, operator, integration_expert, product_owner, business_analyst |
| PRD | architect, auditor, tech_lead, strategist, devils_advocate, operator, integration_expert, product_owner, qa_lead, ux_strategist |
| EARS | tech_lead, devils_advocate, integration_expert, qa_lead, requirements_specialist |
| BDD | auditor, tech_lead, devils_advocate, operator, integration_expert, qa_lead |
| ADR | architect, auditor, tech_lead, strategist, devils_advocate, operator, integration_expert |

To disable skill loading in Python:
```python
config = UCXConfig(load_skills=False)
```

---

## Reference

- **CLI**: `ucx review`, `ucx remediate`, `ucx autopilot`
- **Python API**: `UCRPhase`, `UCRemPhase`, `UCXAutopilot`
- **Skill definitions**: `ucx/skills/personas/`
- **Output template**: `review/UCR_OUTPUT_TEMPLATE.md`
- **Layer prompts**: `review/UCR_PROMPT_*.md`
- **UCRem prompts**: `remediation/UCRem_PROMPT_*.md`
- **UCRem schema**: `remediation/UCRem_REPORT_SCHEMA.md`
- **Domain examples**: `examples/`
