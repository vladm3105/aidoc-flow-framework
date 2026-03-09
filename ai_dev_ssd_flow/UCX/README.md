# UCX - Unified Context Framework

## Overview

The **UCX Framework** (Unified Context) is an advanced document lifecycle management system built into `docs_flow_framework/ai_dev_ssd_flow`. It uses a **Unified Context** approach where multiple expert personas collaborate within a single context window, maintaining full document coherence.

The system consists of three phases:
1. **UCC (Creation)** - Multi-persona document authoring with skill injection
2. **UCR (Review)** - Multi-persona document validation identifying gaps and issues
3. **UCRem (Remediation)** - Multi-persona fix proposal generation with executable fixes

**Plus**: A full **Autopilot** mode that orchestrates all phases automatically.

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

## Quick Start: Autopilot (Recommended)

The autopilot orchestrates the complete UCC → UCR → UCRem cycle with:
- **Smart Document Detection**: Auto-selects create vs review based on document existence
- **Drift Monitoring**: Tracks upstream changes via `.drift_cache.json`
- **Iterative Fix Cycles**: Max 3 iterations until score >= 90%
- **Batch Processing**: Handles multiple documents in chunks of 3

```bash
# Generate new BRD from reference docs
./run_ucx_autopilot.sh brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/

# Review existing BRD (auto-detected)
./run_ucx_autopilot.sh brd docs/01_BRD/BRD-01

# Generate from upstream artifact
./run_ucx_autopilot.sh prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01

# Generate from IPLAN
./run_ucx_autopilot.sh brd docs/01_BRD/BRD-02 --from-iplan IPLAN-001

# Batch process multiple documents
./run_ucx_autopilot.sh brd docs/01_BRD/BRD-01 docs/01_BRD/BRD-02 --batch

# Dry run (show what would happen)
./run_ucx_autopilot.sh brd docs/01_BRD/BRD-01 --dry-run
```

### Autopilot Options

| Option | Description |
|--------|-------------|
| `--from-ref <dir>` | Generate from reference documents |
| `--from-upstream <file>` | Generate from upstream artifact |
| `--from-iplan <file>` | Generate from implementation plan |
| `--batch` | Process multiple targets |
| `--max-iterations <n>` | Max review/fix cycles (default: 3) |
| `--min-score <n>` | Minimum PRD-Ready score (default: 90) |
| `--skip-drift` | Skip drift monitoring |
| `--dry-run` | Show actions without executing |

### Autopilot Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `UCX_MODEL` | `opus` | Claude model for all phases |
| `UCX_MAX_ITER` | `3` | Maximum iteration cycles |
| `UCX_MIN_SCORE` | `90` | Minimum passing score |
| `UCX_SKIP_DRIFT` | `false` | Skip drift cache generation |

---

## Manual Runner Scripts

For granular control, you can run each phase independently:

### Step 1: Run UCC Creation

```bash
# Generate a new document
./creation/run_ucc.sh <doc_type> <output_path> [options]

# Examples
./creation/run_ucc.sh brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/
./creation/run_ucc.sh prd docs/02_PRD/PRD-01.md --from-upstream docs/01_BRD/BRD-01
```

### Step 2: Run UCR Validation

```bash
# Run UCR review on a document
./review/run_ucr.sh <doc_type> <document_path> [output_file]

# Examples
./run_ucr.sh brd docs/01_BRD/BRD-01_platform_architecture
./run_ucr.sh prd docs/02_PRD/PRD-01.md
./run_ucr.sh ears docs/03_EARS/*.md
```

The script:
- Auto-selects the correct UCR prompt for the document type
- Loads layer-specific persona skills dynamically
- Outputs to `{DOC_TYPE}_UCR_REVIEW.md` in the document directory

### Step 2: Run UCRem Remediation

```bash
# Generate fix proposals from UCR review
./run_ucrem.sh <ucr_report> <document_path> [output_file]

# Examples
./run_ucrem.sh docs/01_BRD/BRD-01/BRD_UCR_REVIEW.md docs/01_BRD/BRD-01
./run_ucrem.sh prd_review.md docs/02_PRD/PRD-01.md
```

The script:
- Auto-detects document type from UCR report filename
- Loads 5 fixer persona skills for validation
- Outputs to `{DOC_TYPE}_UCRem_REPORT.md`

### Step 3: Apply Fixes

```bash
# Use the doc-brd-fixer skill (or appropriate layer fixer)
/doc-brd-fixer BRD-01 --from-ucrem BRD_UCRem_REPORT.md
```

### Step 4: Verify

```bash
# Re-run UCR to verify P0/P1 counts reduced
./run_ucr.sh brd docs/01_BRD/BRD-01_platform_architecture
```

---

## Dynamic Skill Loading

The runner scripts dynamically inject persona skill files into prompts at runtime. This provides rich domain knowledge to each persona without bloating static prompt files.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `UCR_LOAD_SKILLS` | `true` | Enable/disable skill loading for UCR |
| `UCREM_LOAD_SKILLS` | `true` | Enable/disable skill loading for UCRem |
| `UCR_MODEL` | `opus` | Claude model for UCR reviews |
| `UCREM_MODEL` | `opus` | Claude model for UCRem remediation |
| `UCR_PROMPT_DIR` | Script directory | Custom prompt directory |
| `UCREM_PROMPT_DIR` | Script directory | Custom prompt directory |

### Layer-to-Skills Mapping (UCR)

Different document types load different persona skill sets:

| Layer | Document Type | Personas Loaded |
|-------|---------------|-----------------|
| L1 | BRD | architect, auditor, tech_lead, strategist, devils_advocate, operator, integration_expert, product_owner, business_analyst |
| L2 | PRD | architect, auditor, tech_lead, strategist, devils_advocate, operator, integration_expert, product_owner, qa_lead, ux_strategist |
| L3 | EARS | tech_lead, devils_advocate, integration_expert, qa_lead, requirements_specialist |
| L4 | BDD | auditor, tech_lead, devils_advocate, operator, integration_expert, qa_lead |
| L5 | ADR | architect, auditor, tech_lead, strategist, devils_advocate, operator, integration_expert |
| L6 | SYS | architect, tech_lead, devils_advocate, operator, integration_expert, qa_lead |
| L7 | REQ | tech_lead, devils_advocate, integration_expert, qa_lead, requirements_specialist |
| L8 | CTR | architect, auditor, tech_lead, devils_advocate, integration_expert |
| L9 | SPEC | architect, tech_lead, devils_advocate, operator, integration_expert |
| L10 | TSPEC | tech_lead, devils_advocate, operator, integration_expert, qa_lead |

### Fixer Skills (UCRem)

UCRem uses 5 fixer personas for ALL document types:

```
architect, auditor, qa_lead, integration_expert, devils_advocate
```

### Disabling Skill Loading

For smaller prompts or debugging:

```bash
UCR_LOAD_SKILLS=false ./run_ucr.sh brd docs/01_BRD/BRD-01
UCREM_LOAD_SKILLS=false ./run_ucrem.sh brd_review.md docs/01_BRD/BRD-01
```

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

## UCRem (Remediation) System

UCRem generates executable fix proposals for findings identified in UCR review reports.

### The 5 Fixer Personas

| Persona | Focus | Key Question | Flag for Manual |
|---------|-------|--------------|-----------------|
| **Architect Fixer** | System design, pattern preservation | Does this fix maintain architectural coherence? | New pattern needed, conflicts with ADR |
| **Auditor Fixer** | Compliance completeness, security | Is this fix fully compliant? | Regulatory interpretation needed |
| **QA Fixer** | Testability, verification | Can this fix be verified? | Cannot verify programmatically |
| **Integration Fixer** | Cross-references, traceability | Do all references still resolve? | Cascade to multiple documents |
| **Devil's Advocate** | Root cause, edge cases, failures | Does this fix solve the problem or hide it? | Symptom-only fix, hidden assumptions |

### Confidence Levels

| Level | Criteria | Execution |
|-------|----------|-----------|
| **auto-safe** | Deterministic text, 2+ personas approve, no objections | Apply automatically |
| **auto-assisted** | Template with [TODO] placeholders, 1+ persona approves | Apply template, complete placeholders |
| **manual-required** | Architectural decision, regulatory, Devil's Advocate objection | Create task for domain expert |

### UCRem Fix Philosophy

**UNDER-FIXING IS UNACCEPTABLE.** A partial fix that claims resolution is worse than flagging for manual review.

| Error Type | Risk Level | Consequence |
|------------|------------|-------------|
| **Under-Fix** | **CRITICAL** | Issue reappears, team loses trust in automation |
| **Over-Fix** | LOW | Extra work, easily scaled back |

**Rule: When fix completeness is uncertain, FLAG FOR MANUAL REVIEW.**

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

## File Structure

```
UCX/
├── README.md                      # This file
├── run_ucx_autopilot.sh           # Full autopilot (UCC→UCR→UCRem)
│
├── creation/
│   ├── run_ucc.sh                 # UCC runner with skill injection
│   ├── UCC_PROMPT_*.md            # Creation prompts (per layer)
│   ├── UCC_PERSONAS.md            # Author persona definitions
│   └── UCC_OUTPUT_SCHEMA.md       # Output format specification
│
├── review/
│   ├── run_ucr.sh                 # UCR runner with dynamic skill loading
│   ├── UCR_PROMPT_*.md            # Review prompts (per layer)
│   ├── UCR_OUTPUT_*.md            # Output templates
│   └── validators/                # Schema validators
│       ├── validate_common.sh
│       ├── validate_brd.sh
│       ├── validate_prd.sh
│       └── validate_generic.sh
│
├── remediation/
│   ├── run_ucrem.sh               # UCRem runner with fixer skill loading
│
│   ├── UCRem_PROMPT_*.md          # Remediation prompts (per layer)
│   ├── UCRem_REPORT_SCHEMA.md     # Fix entry schema reference
│   ├── UCRem_REPORT_TEMPLATE.md   # Output template
│   └── UCRem_PERSONAS.md          # 5 fixer persona definitions
│
├── skills/                        # Persona skill definitions
│   ├── architect.md
│   ├── auditor.md
│   ├── tech_lead.md
│   ├── strategist.md
│   ├── devils_advocate.md
│   ├── operator.md
│   ├── integration_expert.md
│   ├── product_owner.md
│   ├── business_analyst.md
│   ├── qa_lead.md
│   ├── requirements_specialist.md
│   └── ux_strategist.md
│
├── docs/
│   ├── UNIFIED_CONTEXT_FRAMEWORK.md  # Framework overview
│   ├── UNIFIED_CONTEXT_REVIEW.md     # UCR method guide
│   ├── UCX_VS_SKILLS_COMPARISON.md   # Feature comparison with Claude Skills
│   ├── PERSONA_DESIGN_GUIDE.md       # 12 persona archetypes
│   └── HOW_TO_USE.md                 # Usage guide
│
├── SKILL_INDEX.md                 # Maps Claude Skills to UCX phases
├── init_ucx.sh                    # Project initialization script
│
└── examples/
    └── beelocal_fintech_board.md  # Fintech domain example
```

---

## Project Customization

Projects use symlinks to framework files and add project-specific prompts.

### Project Setup

```bash
cd /your/project/docs/AI_EXPERTS

# Create symlinks to framework
ln -s /path/to/framework/AI_EXPERTS/run_ucr.sh run_ucr.sh
ln -s /path/to/framework/AI_EXPERTS/run_ucrem.sh run_ucrem.sh
ln -s /path/to/framework/AI_EXPERTS/UCR_PROMPT_BRD.md UCR_PROMPT_BRD.md
ln -s /path/to/framework/AI_EXPERTS/UCRem_PROMPT_BRD.md UCRem_PROMPT_BRD.md
ln -s /path/to/framework/AI_EXPERTS/UCRem_REPORT_SCHEMA.md UCRem_REPORT_SCHEMA.md
ln -s /path/to/framework/AI_EXPERTS/UCRem_REPORT_TEMPLATE.md UCRem_REPORT_TEMPLATE.md
ln -s /path/to/framework/AI_EXPERTS/skills skills

# Create project-specific prompts (NOT symlinked)
# These override framework prompts when present
touch UCR_PROMPT_BRD_PROJECT.md      # or *_BEELOCAL.md for BeeLocal
touch UCRem_PROMPT_BRD_PROJECT.md
```

### Prompt Selection Priority

The runner scripts search for prompts in this order:

1. `UCR_PROMPT_{TYPE}_PROJECT.md` - Project-specific override
2. `UCR_PROMPT_{TYPE}_BEELOCAL.md` - BeeLocal-specific (legacy)
3. `UCR_PROMPT_{TYPE}.md` - Framework default

### Project-Specific Prompt Contents

Project prompts extend framework prompts with:
- Domain-specific terminology
- Partner/vendor integration context
- Industry-specific compliance requirements
- Custom P0 defaults for the domain

**Example**: BeeLocal fintech project adds:
- Partner integrations (Bridge, Asterium, Paynet)
- Regulatory focus (FinCEN/BSA, OFAC, MTL, PCI-DSS)
- Transaction saga compensation patterns
- USDC custody considerations

---

## Output Formats

### UCR Review Report

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

### UCRem Fix Entry Format (YAML)

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
  anchor: "exact text to find"
  text: |
    Exact text to insert. Complete and ready to apply.
    No vague instructions like "add more detail".
rationale: |
  Explain WHY this specific fix addresses the finding.
  Reference the original finding ID and what was missing.
validated_by:
  - Architect Fixer
  - Auditor Fixer
verification: |
  How to verify this fix was applied correctly.
  Include searchable text or checklist items.
```

### Fix Type Reference

| fix_type | fix_action Schema |
|----------|-------------------|
| `add_text` | `position: after|before|replace`, `anchor: "text to find"`, `text: "text to add"` |
| `add_section` | `parent_section: "X.X"`, `section_number: "X.X.X"`, `heading: "Title"`, `content: "full content"` |
| `add_table_row` | `table_anchor: "table header text"`, `row_data: ["col1", "col2", ...]` |
| `modify_text` | `old_text: "exact old"`, `new_text: "exact new"` |
| `add_frontmatter` | `field_path: "custom_fields.key"`, `value: "value"` |
| `add_tag` | `tag_type: "@brd:"`, `tag_value: "BRD.01.01.XX"`, `location: "section"` |

---

## CLI Examples (Manual Method)

For manual execution without runner scripts:

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

**Note**: Manual method does NOT include dynamic skill loading. Use runner scripts for full persona knowledge.

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

## Documentation Reference

1. [UCR Method Guide](UNIFIED_CONTEXT_REVIEW.md) - Primary method documentation
2. [Persona Design Guide](PERSONA_DESIGN_GUIDE.md) - 12 persona archetypes
3. [How to Audit](HOW_TO_AUDIT.md) - Step-by-step audit instructions
4. [UCR Output Template](PERSONA_REVIEW-MVP-TEMPLATE.md) - UCR report format
5. [UCRem Report Schema](UCRem_REPORT_SCHEMA.md) - Fix entry YAML schema
6. [UCRem Personas](UCRem_PERSONAS.md) - 5 fixer persona definitions

---

## Model Recommendations

UCR/UCRem performs best with models that:
- Support large context windows (100K+ tokens)
- Have strong reasoning capabilities
- Maintain coherent multi-persona synthesis
- Follow conservative classification directives

**Recommended**: Claude Opus 4.5 (primary), Claude Sonnet 4 (faster), Gemini 2.5 Pro

---

## Drift Monitoring

The autopilot tracks upstream changes using `.drift_cache.json` files.

### How It Works

1. **Initial Generation**: When generating from `--from-ref`, computes SHA-256 hashes of all upstream files
2. **Cache Storage**: Stores hashes in `.drift_cache.json` in the document folder
3. **Review Detection**: On subsequent reviews, compares current hashes to cached values
4. **Drift Alert**: If hashes differ, alerts that upstream has changed since generation

### Cache Schema

```json
{
  "schema_version": "1.1",
  "document_id": "BRD-01",
  "document_version": "1.0",
  "upstream_mode": "ref",
  "last_reviewed": "2026-03-09T10:30:00-05:00",
  "reviewer_version": "UCX-1.0",
  "upstream_documents": {
    "spec.md": {
      "hash": "sha256:abc123...",
      "last_checked": "2026-03-09T10:30:00-05:00"
    }
  },
  "review_history": [
    {
      "date": "2026-03-09T10:30:00-05:00",
      "score": 92,
      "drift_detected": false,
      "status": "PASS"
    }
  ]
}
```

### Disabling Drift Monitoring

```bash
./run_ucx_autopilot.sh brd docs/01_BRD/BRD-01 --skip-drift
# Or via environment variable
UCX_SKIP_DRIFT=true ./run_ucx_autopilot.sh brd docs/01_BRD/BRD-01
```

---

## Feature Parity with Claude Skills

UCX provides feature parity with Claude Skills (`doc-brd-autopilot`, etc.):

| Feature | Claude Skills | UCX |
|---------|--------------|-----|
| Document Creation | `doc-brd`, etc. | `run_ucc.sh` |
| Document Review | `doc-brd-audit` | `run_ucr.sh` |
| Document Remediation | `doc-brd-fixer` | `run_ucrem.sh` |
| Smart Detection | Auto-detect action | `run_ucx_autopilot.sh` |
| Drift Monitoring | `.drift_cache.json` | `.drift_cache.json` |
| Full Autopilot | UCC→UCR→UCRem | `run_ucx_autopilot.sh` |
| IPLAN Input | `--iplan` | `--from-iplan` |
| Batch Processing | Chunked by 3 | `--batch` |

See [UCX_VS_SKILLS_COMPARISON.md](docs/UCX_VS_SKILLS_COMPARISON.md) for detailed comparison.

---

## Version History

| Date | Change |
|------|--------|
| 2026-03-09 | **v1.1**: Added full autopilot with drift monitoring, smart detection, IPLAN support |
| 2026-03-09 | Added UCRem (remediation) system with 5 fixer personas |
| 2026-03-09 | Implemented dynamic skill loading in runner scripts |
| 2026-03-09 | Added project customization with symlinks pattern |
| 2026-03-09 | Updated README with complete UCR+UCRem workflow |
