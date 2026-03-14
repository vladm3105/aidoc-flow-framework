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
| BRD (L1) | `UCR_PROMPT_BRD.md` | 11 required + 2 optional |
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

## Review Modes: Unified vs Persona

UCX supports two review modes with different trade-offs. Understanding when to use each mode is critical for optimal review quality.

### Quick Comparison

| Aspect | Unified Prompt | Persona Prompts |
|--------|----------------|-----------------|
| **CLI Flag** | (default) or `--unified` | `--persona` / `-p` |
| **API Calls** | 1 | 12 (one per persona) |
| **Document Context** | Full document to all personas | Filtered per persona |
| **Prior Findings** | N/A | Summarized to prevent repetition |
| **Context Engineering** | None | Hierarchical 4-level |
| **Attention Steering** | Yes (v1.14.7+) | Yes (format at END) |
| **Resume Support** | No | Yes |
| **Cost** | Lower | Higher |
| **Best For** | Small/medium docs (<50K tokens) | Large docs (>50K tokens) |

### Unified Prompt Review

```bash
ucx review brd docs/01_BRD/BRD-01/              # Default mode
ucx review brd docs/01_BRD/BRD-01/ --unified   # Force unified (skip auto-detect)
```

**How it works:**
- Single LLM API call
- All 12 personas review simultaneously in one prompt
- All findings returned in one response

```
┌─────────────────────────────────────────────────────┐
│                   SINGLE PROMPT                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ architect│ │ auditor  │ │tech_lead │  ... x12   │
│  └──────────┘ └──────────┘ └──────────┘            │
│                                                      │
│  Document Content + All Persona Instructions         │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌─────────────────┐
              │  Single Response │
              │  All Findings    │
              └─────────────────┘
```

**Advantages:**
- **Full document visibility**: Every persona sees the ENTIRE document
- **Cross-domain detection**: Architect might catch compliance issue, auditor might catch architecture issue
- **No filtering risk**: No chance of relevant content being filtered out
- **Speed**: Single API call, faster completion
- **Cost**: Lower token usage overall

**Disadvantages:**
- **Attention dilution**: 12 personas compete for LLM attention
- **Large document risk**: May truncate if document exceeds context limit
- **No resume**: Must restart from beginning if interrupted

### Persona Prompts Review

```bash
ucx review brd docs/01_BRD/BRD-01/ --persona    # Enable persona prompts
ucx review brd docs/01_BRD/BRD-01/ -p           # Shorthand
```

**How it works:**
- Sequential API calls (one per persona)
- Each persona reviews with full attention
- Prior findings summarized for later personas (anti-repetition)

```
┌────────────┐     ┌────────────┐     ┌────────────┐
│  Call 1    │     │  Call 2    │     │  Call 3    │
│ architect  │ ──► │  auditor   │ ──► │ tech_lead  │  ... x12
│            │     │ + prior    │     │ + prior    │
│            │     │  summary   │     │  summaries │
└────────────┘     └────────────┘     └────────────┘
      │                  │                  │
      ▼                  ▼                  ▼
┌──────────┐       ┌──────────┐       ┌──────────┐
│ Findings │       │ Findings │       │ Findings │
│   ARCH-  │       │   AUD-   │       │   TL-    │
└──────────┘       └──────────┘       └──────────┘
```

**Advantages:**
- **Full attention per persona**: No competition with other personas
- **Persona-specific context**: Filtered to domain-relevant sections
- **Prior findings deduplication**: Prevents same issue reported multiple times
- **Attention steering**: Format instructions at END improve compliance
- **Large document handling**: Auto-splits documents >100K chars
- **Resume capability**: Can continue from last completed persona

**Disadvantages:**
- **Filtering risk**: Persona may miss issue in filtered-out section
- **Higher cost**: 12 API calls vs 1
- **Slower**: Sequential processing

### Prompt Structure Differences

**Unified Prompt:**
```
[System Instructions]
[Document Content - FULL]
[Persona 1 Skill: architect]
[Persona 2 Skill: auditor]
[Persona 3 Skill: tech_lead]
... x12 personas
[Output Format Instructions]  ← Attention steering (at END, v1.14.7+)
```

**Persona Prompt (per persona):**
```
[System Instructions]
[Hierarchical Context]
  ├── Level 1: Overview (executive summary)
  ├── Level 2: Relevant sections (persona-specific)
  ├── Level 3: Reference sections
  └── Level 4: Discovered snippets (keyword scan)
[Prior Findings Summary]  ← "Don't repeat these"
[Persona Skill: architect]
[Output Format Instructions]  ← Attention steering (at END)
```

### Context Filtering in Persona Prompts

Persona prompts mode uses `DynamicSectionMapper` to filter document sections per persona:

| Persona | Categories Included |
|---------|---------------------|
| architect | functional, quality, technical, integration, scope |
| auditor | functional, quality, compliance, risk |
| operator | functional, quality, technical, scope |
| integration_lead | functional, integration, technical |

**Example for BRD-01:**

| Persona | Sections Included |
|---------|-------------------|
| architect | BRD-01.3 (Architecture), BRD-01.5 (NFRs), BRD-01.6 (Integration) |
| auditor | BRD-01.4 (Compliance), BRD-01.7 (Risk), BRD-01.5 (NFRs) |
| operator | BRD-01.8 (Operations), BRD-01.5 (NFRs), BRD-01.9 (SLAs) |

### Token Usage Comparison

For a 170KB BRD document:

| Mode | Document Context | Skill Instructions | Total per Call |
|------|------------------|-------------------|----------------|
| One-Turn | 170KB (full) | ~15KB (all 12) | ~185KB × 1 call |
| Multi-Turn | ~60KB (filtered) | ~1.5KB (1 persona) | ~62KB × 12 calls |

### When to Use Each Mode

**Use Unified Prompt when:**
- Document is < 30K tokens
- Quick review needed
- Cost is a concern
- Cross-domain issues are suspected
- Document structure is simple

**Use Persona Prompts (`--persona`) when:**
- Document is > 50K tokens
- Deep per-persona analysis needed
- Finding deduplication is important
- Session persistence/resume required
- Reviewing complex multi-section BRDs

**For critical reviews**: Run both modes and compare. Persona prompts catch depth, unified prompt catches breadth.

### CLI Reference

```bash
# Unified prompt (default)
ucx review brd docs/01_BRD/BRD-01/

# Force unified (skip auto-detection for large docs)
ucx review brd docs/01_BRD/BRD-01/ --unified
ucx review brd docs/01_BRD/BRD-01/ -u

# Persona prompts mode
ucx review brd docs/01_BRD/BRD-01/ --persona
ucx review brd docs/01_BRD/BRD-01/ -p

# Persona prompts with options
ucx review brd docs/01_BRD/BRD-01/ -p --no-resume        # Fresh start
ucx review brd docs/01_BRD/BRD-01/ -p --session-ttl 48   # Custom TTL
```

### Feature Parity (v1.14.5+)

As of v1.14.5, both modes have feature parity for:

| Feature | Unified Prompt | Persona Prompts |
|---------|----------------|-----------------|
| Project-specific skills | YES | YES |
| Category Tagging (`[CAT:xxx]`) | YES | YES |
| Finding ID format (`PREFIX-P#-NNN`) | YES | YES |
| Domain-specific checklists | YES | YES |
| Skill loading priority (project first) | YES | YES |

Features unique to Persona Prompts (by design):

| Feature | Reason |
|---------|--------|
| Prior Findings Summarization | No previous responses in unified prompt |
| Anti-Repetition Instructions | Single call with all personas |
| Context Engineering (hierarchical) | Persona prompts optimization |
| Session Resume | Single call completes atomically |

---

## How UCR Works

### Single-Pass Architecture (Unified Prompt)

Unlike multi-model pipelines that fragment context across multiple API calls, unified prompt:

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

### Layer-Appropriate Finding Classification (v1.5.5+)

UCR now distinguishes between **BRD requirements** and **SPEC implementation details**:

| Finding Type | BRD Priority | Notes |
|--------------|--------------|-------|
| Regulatory compliance gaps | P0 | FinCEN, OFAC, PCI-DSS mandates |
| Security control requirements | P0 | Session timeout *requirement*, not exact values |
| Money movement safety | P0 | Saga pattern *requirement*, not algorithm details |
| Per-partner webhook algorithms | P1 (Defer to SPEC) | Implementation detail |
| Connection pool configurations | P1 (Defer to SPEC) | Implementation detail |
| State machine state names | P1 (Defer to SPEC) | Define *need* for FSM, defer states to SPEC |
| Circuit breaker thresholds | P1 (Defer to SPEC) | Implementation detail |

**Rule**: If the finding is about "what algorithm/config/threshold to use" rather than "what capability is required", mark as P1 with note "Defer to SPEC layer".

### Pre-Validation vs Content Findings (v1.5.5+)

Pre-validation errors (YAML schema, missing fields) are **infrastructure** issues, not **content** issues:

| Error Category | Classification | Report Section |
|----------------|----------------|----------------|
| YAML frontmatter missing fields | Pre-validation | Section 8 (Pre-Validation Summary) |
| Schema compliance failures | Pre-validation | Section 8 (Pre-Validation Summary) |
| Content gaps (missing requirements) | P0/P1/P2 | Section 2/3/5 (Findings) |

**Rule**: Pre-validation errors do not count toward P0/P1/P2 content findings. They are reported separately.

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

**Core Personas (Required - 11)**:

| Persona | Skeptical Stance |
|---------|------------------|
| **Architect** | Assume architectural gaps exist until proven otherwise |
| **Auditor** | Assume non-compliant until explicitly proven compliant |
| **Tech Lead** | Implementation details matter - vague specs cause bugs |
| **Strategist** | Financial assumptions must be validated |
| **Chaos Engineer** | If failure mode isn't documented, it WILL happen |
| **Operator** | If it can't be observed and rolled back, not production-ready |
| **Integration Lead** | Integration failures cascade - every dependency is a risk |
| **Product Owner** | Scope creep kills projects - MVP must be ruthlessly bounded |
| **Business Analyst** | Ambiguous requirements cause implementation disputes |
| **Fact Checker** | Trust but verify - cross-reference all findings against source |
| **Chairperson** | Synthesize consensus - calculate score with transparent formula |

**Quality Assurance Personas (Optional - 2)**:

| Persona | Purpose |
|---------|---------|
| **Judge** | Validate Chairperson's analysis for bias, accuracy, and completeness |
| **Chairperson Editor** | Final polish, consistency check, Judge feedback integration |

**Layer-Specific Personas**:

| Persona | Skeptical Stance | Layers |
|---------|------------------|--------|
| **QA Lead** | Untestable requirements are unimplementable | PRD, EARS, BDD, TSPEC |
| **Requirements Specialist** | Syntax violations are P0 - no exceptions | EARS, REQ |
| **UX Strategist** | UX gaps cause user churn - accessibility is non-negotiable | PRD |

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
ucx remediate brd docs/01_BRD/BRD-01/ --review-report docs/01_BRD/BRD-01/BRD-01.UCR_review_report_v001.md

# Step 3: Apply fixes (via Claude skill)
/doc-brd-fixer BRD-01 --from-ucrem BRD-01_UCRem_REPORT.md

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
| BRD | architect, auditor, tech_lead, strategist, chaos_engineer, operator, integration_lead, product_owner, business_analyst |
| PRD | architect, auditor, tech_lead, strategist, chaos_engineer, operator, integration_lead, product_owner, qa_lead, ux_strategist |
| EARS | tech_lead, chaos_engineer, integration_lead, qa_lead, requirements_specialist |
| BDD | auditor, tech_lead, chaos_engineer, operator, integration_lead, qa_lead |
| ADR | architect, auditor, tech_lead, strategist, chaos_engineer, operator, integration_lead |

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
