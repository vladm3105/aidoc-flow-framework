# PLAN-009: PRD Creation Improvements

**Document ID**: PLAN-009_prd_creation
**Created**: 2026-03-19
**Updated**: 2026-03-21
**Status**: Revised (v7)
**Target Version**: UCX v1.21.0+
**Related Plans**: PLAN-010_prd_validation.md (validation counterpart), PLAN-012_prd_derived_artifact_flow.md (derived-artifact downstream flow)

---

## Objective

Enhance UCX PRD creation (UCC phase) to align with the 21-section MVP template structure, dual scoring requirements, and Section 10/Section 8 mandatory content rules. Ensure created PRDs pass validation immediately and serve as the canonical source artifact for downstream PLAN-012 processing.

---

## Architecture Clarification

UCX creation is **prompt-driven**, not code-driven. The flow is:

```
UCC_PROMPT_PRD.md
       +
Persona Skills (from ucx/skills/personas/)
       +
PRD-MVP-TEMPLATE.md
       +
Upstream BRD content
       ↓
   AI Client
       ↓
   PRD Document
```

This plan focuses on **prompt engineering**, not Python module creation.

Creation boundary:
- `ucx create prd` emits the canonical source PRD only.
- Post-create validation may score and report on that artifact, but derived `_validation` and `_remediated` copies belong to the downstream PLAN-012 flow.

---

## Current State Analysis

### Existing Components

| Component | Location | Status |
|-----------|----------|--------|
| UCC Prompt | `UCX/creation/UCC_PROMPT_PRD.md` | **Outdated - requires full rewrite** |
| Template | `ai_dev_ssd_flow/02_PRD/PRD-MVP-TEMPLATE.md` | Current (21 sections) |
| Python API | `ucx/api/creation.py` | Working |
| CLI | `ucx create prd` | Working |
| Personas | `ucx/skills/personas/` (5 configured) | Needs refinement |
| Layer Skills | `ucx/config/layer_skills.py` | Needs update |

### Critical Issues in Current UCC_PROMPT_PRD.md

| Issue | Current State | Required State |
|-------|---------------|----------------|
| Section count | 11 sections | 21 sections |
| Type codes | 5 codes (01-05) | 13 codes |
| Type 01 meaning | User Story | Functional Requirement |
| User story format | `US-{NN}` | `PRD.NN.09.SS` |
| Acceptance criteria | Given-When-Then (BDD!) | Summary only |
| Scoring | Not mentioned | Dual SYS-Ready + EARS-Ready |
| Diagrams | Not mentioned | c4-l2, dfd-l1, sequence-* |
| Section 10 | Not present | Customer-Facing (BLOCKING) |
| Section 8 | Not present | Layer separation note |
| Traceability format | `BRD.01.01.12` | `@brd: BRD.01.01.12` (4-segment) |

### Layer Separation Violation in Current Prompt

**Line 122-123 of current prompt contains BDD patterns:**
```markdown
- [ ] Given {context}, when {action}, then {result}
```

This **violates layer separation**. Given-When-Then belongs in BDD (Layer 4), not PRD (Layer 2).

---

## Implementation Phases

### Phase 1: Full UCC_PROMPT_PRD.md Rewrite

**File:** `/opt/data/docs_flow_framework/UCX/creation/UCC_PROMPT_PRD.md`

**Action:** Complete replacement (not incremental update)

**New Content:**

```markdown
# UCC Prompt: PRD Creation

You are a **Unified Context Creation (UCC)** system. Your task is to author a complete **Product Requirements Document (PRD)** using multiple expert personas collaboratively.

---

## Core Philosophy

**IMPLEMENTATION CLARITY IS NON-NEGOTIABLE.** A PRD bridges business requirements to technical implementation. Ambiguity here causes development delays.

| Error Type | Risk Level | Consequence |
|------------|------------|-------------|
| **Vague Features** | **CRITICAL** | Developers interpret differently |
| **Missing Acceptance Criteria** | HIGH | QA cannot validate |
| **Undefined User Flows** | HIGH | UX inconsistencies |
| **Section 10 Empty** | **BLOCKING** | Customer messaging undefined |
| **Layer Violation (BDD in PRD)** | **CRITICAL** | Downstream confusion |

---

## MANDATORY STRUCTURE (21 Sections)

All PRDs MUST contain exactly 21 numbered sections in this order:

| # | Section | Key Content | Element Codes |
|---|---------|-------------|---------------|
| 1 | Document Control | Metadata, dual scoring, versioning | - |
| 2 | Executive Summary | 2-3 sentence overview, business value | - |
| 3 | Problem Statement | Current state, business impact | - |
| 4 | Target Audience & User Personas | Primary/secondary users | 24 |
| 5 | Success Metrics (KPIs) | Primary/secondary KPIs, go/no-go gates | 08 |
| 6 | Goals & Objectives | Business goals, objectives, stretch goals | 23 |
| 7 | Scope & Requirements | In-scope, out-of-scope, dependencies | 05, 22 |
| 8 | User Stories & User Roles | PRD-level stories with layer note | 09 |
| 9 | Functional Requirements | Core capabilities, user journeys | 01, 11, 22 |
| 10 | **Customer-Facing Content** | **BLOCKING - substantive content required** | - |
| 11 | Acceptance Criteria | Business/technical criteria | 06 |
| 12 | Constraints & Assumptions | Business/technical constraints | 03, 04 |
| 13 | Risk Assessment | High-risk items, mitigation | 07 |
| 14 | Success Definition | Go-live criteria, validation | - |
| 15 | Stakeholders & Communication | Core team, RACI matrix | 24 |
| 16 | Implementation Approach | MVP phases, testing strategy | - |
| 17 | Budget & Resources | Development cost, ROI hypothesis | - |
| 18 | Traceability | Upstream BRD, ADR Requirements table | - |
| 19 | References | Internal/external documentation | - |
| 20 | EARS Enhancement Appendix | Timing profiles, boundary values | - |
| 21 | Quality Assurance | Quality standards, testing strategy | 02 |

---

## ELEMENT ID FORMAT

Use ONLY the unified 4-segment format:

```
PRD.{DOC}.{TYPE}.{SEQ}
```

| Code | Type | Primary Section |
|------|------|-----------------|
| 01 | Functional Requirement | 9 |
| 02 | Quality Attribute | 21 |
| 03 | Constraint | 12 |
| 04 | Assumption | 12 |
| 05 | Dependency | 7 |
| 06 | Acceptance Criteria | 11 |
| 07 | Risk | 13 |
| 08 | Metric/KPI | 5 |
| 09 | User Story | 8 |
| 11 | Use Case | 9 |
| 22 | Feature Item | 7, 9 |
| 23 | Goal | 6 |
| 24 | Stakeholder Need | 4, 15 |

**FORBIDDEN PATTERNS** (legacy - DO NOT USE):
- `FR-XXX`, `NFR-XXX`, `AC-XXX`, `US-XXX`, `F-XXX`
- `RISK-XXX`, `METRIC-XXX`, `BC-XXX`, `BA-XXX`
- `Feature-NNN-NNN`

---

## SECTION 10 REQUIREMENTS (BLOCKING)

Section 10 **MUST** contain substantive content. Placeholders will fail validation.

Required subsections:
- **10.1 Product Positioning Statement** - 2-3 sentences, unique value proposition
- **10.2 Key Messaging Themes** - 3-5 themes with target audience
- **10.3 User-Facing Content Samples** - Welcome message, onboarding text
- **10.4 Help Text Templates** - Contextual help for key features
- **10.5 Error Message Patterns** - User-friendly messages with recovery actions
- **10.6 Release Notes Template** - Structure for release communication

**Minimum Requirements:**
- Positioning statement: ≥50 characters
- Messaging themes: ≥3 themes
- Error patterns: ≥3 patterns

---

## SECTION 8 REQUIREMENTS (Layer Separation)

Section 8 **MUST** include this scope note at the beginning:

> **Layer Separation Note**: This section contains PRD-level user stories
> (role definitions, story titles, 2-3 sentence summaries, product-level
> acceptance criteria). Detailed WHEN-THE-SHALL requirements belong in
> EARS (Layer 3). Executable Given-When-Then scenarios belong in BDD (Layer 4).

**CORRECT User Story Format:**
```markdown
#### PRD.01.09.01: [Story Title]

**As a** [role],
**I want** [capability],
**So that** [business value].

**Summary**: [2-3 sentence description of the story scope]

**Product-Level Acceptance**:
- [High-level criterion 1]
- [High-level criterion 2]

**EARS Reference**: To be detailed in EARS-NN (Layer 3)
**BDD Reference**: To be specified in BDD-NN (Layer 4)
```

**FORBIDDEN in Section 8:**
- `Given ... When ... Then ...` (BDD - Layer 4)
- `WHEN ... THE ... SHALL ...` (EARS - Layer 3)
- `@given`, `@when`, `@then` decorators
- Technical implementation details
- System-level specifications

---

## SECTION 18 REQUIREMENTS (Traceability)

### 18.1 Upstream Traceability

Use 4-segment format with `@brd:` prefix:
- **CORRECT**: `@brd: BRD.01.01.05`
- **WRONG**: `@brd: BRD-01` (document-level only)

### 18.2 Architecture Decision Requirements Table

PRD must include topics for ADR (do NOT reference specific ADR-NN numbers):

| Topic | BRD Source | Technical Options | Evaluation Criteria | Decision Timeline |
|-------|------------|-------------------|---------------------|-------------------|
| [Topic 1] | BRD-01 §7.2.3 | Option A, B, C | Performance, Cost | Sprint 3 |

**FORBIDDEN**: References to `ADR-01`, `ADR-02`, etc. (ADR doesn't exist yet at PRD layer)

---

## SECTION 20 REQUIREMENTS (EARS Enhancement Appendix)

Required content for EARS translation readiness:

### 20.1 Timing Profiles
| Operation | p50 | p95 | p99 | Timeout |
|-----------|-----|-----|-----|---------|
| [Operation 1] | Xms | Xms | Xms | Xs |

### 20.2 Boundary Values
| Parameter | Min | Max | Default | Units |
|-----------|-----|-----|---------|-------|
| [Param 1] | X | Y | Z | units |

### 20.3 State Transition Diagram
Reference or description of state machine (link to @diagram: sequence-*)

### 20.4 Fallback Paths
| Failure Mode | Fallback Behavior | Recovery Action |
|--------------|-------------------|-----------------|
| [Failure 1] | [Behavior] | [Action] |

---

## DIAGRAM REQUIREMENTS

PRD **MUST** include these diagram references:

| Diagram Type | Tag | Purpose |
|--------------|-----|---------|
| Container | `@diagram: c4-l2` | System context at container level |
| Data Flow | `@diagram: dfd-l1` | Level 1 data flow |
| Sequence | `@diagram: sequence-*` | Key interaction flows |

Sequence diagrams **MUST** include `alt/else` branches for exception paths.

---

## DUAL SCORING (Document Control)

Section 1 **MUST** include dual readiness scores:

| Field | Format |
|-------|--------|
| SYS-Ready Score | `[DRAFT] NN% (Target: ≥90%)` |
| EARS-Ready Score | `[DRAFT] NN% (Target: ≥90%)` |

Initial creation should estimate scores based on content completeness.

**Score Thresholds:**
- ≥90%: Approved (both scores required)
- 70-89%: Review
- <70%: Draft

---

## YAML FRONTMATTER

```yaml
---
title: "PRD-NN: [Product/Feature Name]"
doc_id: "PRD-NN"
version: "1.0.0"
status: draft
tags:
  - prd
  - layer-2-artifact
  - shared-architecture
custom_fields:
  document_type: prd
  artifact_type: PRD
  layer: 2
  schema_version: "1.1"
  upstream_artifacts: ["BRD-NN"]
  downstream_artifacts: ["EARS-NN"]
---
```

---

## AUTHOR PERSONAS

Apply these 7 expert personas during PRD creation:

| Persona | Focus | Sections |
|---------|-------|----------|
| **PRODUCT_OWNER** | Feature definition, MVP scope, priorities | 1-7, 14-17 |
| **UX_STRATEGIST** | User experience, accessibility | 4, 8, 9 |
| **CONTENT_STRATEGIST** | Customer messaging, content design | **10** (PRIMARY) |
| **TECH_LEAD** | Technical feasibility, constraints | 9, 12, 16, 18, 21 |
| **QA_LEAD** | Testability, acceptance criteria | 11, 20, 21 |
| **ARCHITECT** | System integration, diagrams | 9, 18, 20 |
| **REQUIREMENTS_SPECIALIST** | Layer separation, story scoping | **8** (PRIMARY) |

---

## QUALITY CHECKLIST

Before completing PRD creation, verify:

- [ ] All 21 sections present with correct numbering
- [ ] Section 10 has substantive content (not placeholders)
- [ ] Section 8 includes layer separation note
- [ ] Section 8 has NO Given-When-Then or WHEN-THE-SHALL patterns
- [ ] All element IDs use PRD.NN.TT.SS format
- [ ] All @brd: references use 4-segment format
- [ ] No ADR-NN forward references (use topic table instead)
- [ ] Dual scores included in Document Control
- [ ] Required diagram tags present (c4-l2, dfd-l1, sequence-*)
- [ ] Section 20 has timing profiles and boundary values

---

## BEGIN CREATION

Create a complete PRD from the upstream BRD artifact.

**CRITICAL REMINDERS**:
1. Use 21-section structure exactly
2. Section 10 is BLOCKING - no placeholders
3. Section 8 must have layer separation note
4. NO Given-When-Then patterns (that's BDD, Layer 4)
5. Use PRD.NN.TT.SS element IDs only
6. Include dual scoring in Document Control

---

## DOCUMENT CONTENT FOLLOWS

[Template, BRD upstream, and reference documents will be appended here]
```

**Estimated Size:** ~450 lines (vs current 172 lines)

---

### Phase 2: Persona Updates

**Files to Modify:**

#### 2a. Update `ucx/skills/personas/requirements_specialist.md`

Current file focuses on UCR (review) phase. Add PRD creation context:

```markdown
# Requirements Specialist Persona

## Role
Requirements Engineer responsible for requirement quality, formalization, and layer separation.

## Creation Focus (UCC Phase - PRD)
- Maintain PRD-level abstraction in Section 8
- Enforce layer separation between PRD/EARS/BDD
- Include mandatory layer separation note
- Avoid EARS syntax (WHEN-THE-SHALL)
- Avoid BDD syntax (Given-When-Then)
- Keep user stories to 2-3 sentence summaries

## Section 8 Anti-Patterns (FORBIDDEN)
- Given {context}, when {action}, then {result}
- WHEN {trigger} THE {system} SHALL {behavior}
- @given, @when, @then decorators
- Technical implementation details
- System-level specifications
- Executable test scenarios

## Review Focus (UCR Phase)
- Requirement atomicity
- EARS syntax compliance
- Requirement clarity
- Ambiguity elimination
- Completeness verification

## Review Questions
1. Is each requirement atomic?
2. Does it follow EARS patterns?
3. Is the language unambiguous?
4. Are modal verbs used correctly?
5. Is the requirement complete?

## Quality Criteria
- Single behavior per requirement
- Correct EARS template usage
- Shall/Should/May consistency
- No ambiguous terms
- Complete requirement statement

## Scoring Weight
- EARS: 35%
- REQ: 35%
- SYS: 25%

## EARS Validation
- Ubiquitous: The [system] shall
- State-Driven: While [state]
- Event-Driven: When [event]
- Unwanted: If [condition], then
- Optional: Where [feature]

## Tags
- phase: ucc, ucr
- doc_types: [prd, ears, req, sys]
- priority: critical
```

#### 2b. Create `ucx/skills/personas/content_strategist.md` (NEW)

```markdown
# Content Strategist Persona

## Role
Content design specialist responsible for customer-facing messaging and communication.

## Creation Focus (UCC Phase - PRD Section 10)
- Draft product positioning statement (2-3 sentences)
- Define 3-5 key messaging themes with target audiences
- Create user-facing content samples (welcome, onboarding)
- Design help text templates for key features
- Establish error message patterns with recovery actions
- Prepare release notes template structure

## Section 10 Minimum Requirements
| Element | Minimum |
|---------|---------|
| Positioning statement | ≥50 characters |
| Messaging themes | ≥3 themes |
| Content samples | ≥2 samples |
| Help text templates | ≥2 templates |
| Error message patterns | ≥3 patterns |

## Quality Criteria
- No placeholder text (TBD, TODO, etc.)
- Customer-centric language (not technical jargon)
- Consistent tone and voice
- Actionable error messages (tell user what to do)
- Clear value proposition

## Error Message Pattern
| Component | Guideline |
|-----------|-----------|
| What happened | Clear, non-technical description |
| Why it happened | Brief context if helpful |
| What to do | Specific recovery action |
| Where to get help | Support contact if needed |

## Anti-Patterns (FORBIDDEN)
- "An error occurred" (vague)
- Technical error codes without explanation
- Blame language ("You failed to...")
- Missing recovery actions

## Tags
- phase: ucc
- doc_types: [prd]
- priority: critical
- sections: [10]
```

**Estimated Changes:** 1 file modified (~50 lines), 1 file created (~80 lines)

---

### Phase 3: Layer Skills Update

**File:** `/opt/data/docs_flow_framework/UCX/ucx/config/layer_skills.py`

**Change:** Add 2 new personas to PRD UCC skills

```python
# Current (line 8):
DocType.PRD: ["product_owner", "ux_strategist", "tech_lead", "qa_lead", "architect"],

# Updated:
DocType.PRD: [
    "product_owner",
    "ux_strategist",
    "content_strategist",      # NEW - Section 10
    "tech_lead",
    "qa_lead",
    "architect",
    "requirements_specialist",  # NEW - Section 8 layer separation
],
```

**Estimated Changes:** ~5 lines modified

---

### Phase 4: Post-Creation Validation and Scoring Hook

**File:** `/opt/data/docs_flow_framework/UCX/ucx/api/creation.py`

**Add validation and scoring after creation:**

> **Architecture Note**: Scoring logic is defined in `ucx/validators/prd/scoring.py` (PLAN-010).
> This phase imports the scorer module rather than duplicating scoring logic.
> Under PLAN-012, this post-create validation path remains report-only; it must not create derived PRD copies.

```python
def create(
    self,
    doc_type: Union[str, DocType],
    output_path: Union[str, Path],
    *,
    from_ref: Optional[Path] = None,
    from_upstream: Optional[Path] = None,
    from_iplan: Optional[Path] = None,
    template: Optional[Path] = None,
    multi_file: bool = False,
    validate_after: bool = True,  # NEW PARAMETER
) -> Document:
    """Create document with optional post-creation validation and scoring."""

    # ... existing creation logic ...

    # Write output
    actual_output.write_text(content, encoding="utf-8")
    document = Document.from_path(actual_output)

    # NEW: Post-creation validation and scoring for PRD
    if validate_after and doc_type == DocType.PRD:
        self._validate_and_score_prd(document)

    return document

def _validate_and_score_prd(self, document: Document) -> None:
    """Run Tier 1 validation and compute readiness scores on created PRD.

    Scoring module imported from ucx/validators/prd/scoring.py (PLAN-010).
    """
    import logging
    logger = logging.getLogger(__name__)

    # Step 1: Run Tier 1 validation
    validation_passed = False
    try:
        from ucx.validators.prd import UnifiedPRDValidator

        validator = UnifiedPRDValidator()
        result = validator.validate(document.path, tier1_only=True)

        if result.has_errors:
            logger.warning(
                f"Created PRD has {len(result.errors)} Tier 1 issues. "
                f"Run 'ucx validate prd {document.path}' for details."
            )
            document.metadata["validation_status"] = "needs_review"
            document.metadata["tier1_errors"] = len(result.errors)
        else:
            document.metadata["validation_status"] = "passed"
            validation_passed = True

    except ImportError:
        # Validator not yet implemented (PLAN-010 dependency)
        logger.debug("PRD validator not available, skipping validation")

    # Step 2: Compute and inject readiness scores
    try:
        from ucx.validators.prd.scoring import PRDScorer

        scorer = PRDScorer()
        content = document.path.read_text(encoding="utf-8")
        scores = scorer.calculate(content)

        # Update Document Control section with computed scores
        scorer.update_document_control(document.path, scores)

        # Store in metadata for CLI output
        document.metadata["sys_ready_score"] = scores.sys_ready
        document.metadata["ears_ready_score"] = scores.ears_ready
        document.metadata["readiness_status"] = scores.status
        document.metadata["template_profile"] = scores.profile

        logger.info(
            f"PRD scores computed: SYS-Ready={scores.sys_ready:.1f}%, "
            f"EARS-Ready={scores.ears_ready:.1f}%, Status={scores.status}"
        )

    except ImportError:
        # Scoring module not yet implemented (PLAN-010 Phase 7 dependency)
        logger.debug("PRD scorer not available, skipping score computation")
    except Exception as e:
        # Don't fail creation on scoring errors
        logger.warning(f"Score computation failed: {e}")
```

**Estimated Changes:** ~75 lines added

**Cross-Reference**: The `PRDScorer` class is defined in PLAN-010 Phase 7 (`ucx/validators/prd/scoring.py`). It provides:
- `calculate(content: str) -> ReadinessScores` - Computes SYS-Ready and EARS-Ready scores
- `update_document_control(path: Path, scores: ReadinessScores)` - Injects scores into Document Control section

---

### Phase 5: CLI Enhancement

**File:** `/opt/data/docs_flow_framework/UCX/ucx/cli/main.py`

**Add creation flags:**

```python
@app.command()
def create(
    doc_type: str = typer.Argument(..., help="Document type (brd, prd, etc.)"),
    output_path: str = typer.Argument(..., help="Output file or directory"),
    from_ref: Optional[str] = typer.Option(None, "--from-ref", help="Reference documents directory"),
    from_upstream: Optional[str] = typer.Option(None, "--from-upstream", help="Upstream artifact path"),
    from_iplan: Optional[str] = typer.Option(None, "--from-iplan", help="Implementation plan path"),
    template: Optional[str] = typer.Option(None, "--template", help="Custom template path"),
    multi_file: bool = typer.Option(False, "--multi-file", help="Generate multi-file output"),
    validate: bool = typer.Option(True, "--validate/--no-validate", help="Run validation after creation"),
    strict: bool = typer.Option(False, "--strict", help="Fail on any validation issue"),
):
    """Create a new document with optional validation."""

    ucc = UCCPhase(config=config)
    doc = ucc.create(
        doc_type=doc_type,
        output_path=output_path,
        from_ref=Path(from_ref) if from_ref else None,
        from_upstream=Path(from_upstream) if from_upstream else None,
        from_iplan=Path(from_iplan) if from_iplan else None,
        template=Path(template) if template else None,
        multi_file=multi_file,
        validate_after=validate,
    )

    console.print(f"[green]Created:[/green] {doc.path}")

    # Display readiness scores if computed (from PLAN-010 scoring module)
    if "sys_ready_score" in doc.metadata:
        sys_score = doc.metadata["sys_ready_score"]
        ears_score = doc.metadata["ears_ready_score"]
        status = doc.metadata.get("readiness_status", "Draft")
        profile = doc.metadata.get("template_profile", "mvp")
        threshold = 85 if profile == "mvp" else 90

        # Color-code based on threshold
        sys_color = "green" if sys_score >= threshold else "yellow" if sys_score >= 70 else "red"
        ears_color = "green" if ears_score >= threshold else "yellow" if ears_score >= 70 else "red"

        console.print(f"[bold]Readiness Scores ({profile.upper()} profile, threshold={threshold}%):[/bold]")
        console.print(f"  SYS-Ready:  [{sys_color}]{sys_score:.1f}%[/{sys_color}]")
        console.print(f"  EARS-Ready: [{ears_color}]{ears_score:.1f}%[/{ears_color}]")
        console.print(f"  Status:     {status}")

    # Display validation status
    if doc.metadata.get("validation_status") == "needs_review":
        console.print(f"[yellow]Warning:[/yellow] {doc.metadata.get('tier1_errors', 0)} Tier 1 issues found")
        console.print(f"Run: ucx validate prd {doc.path}")
        if strict:
            raise typer.Exit(code=1)
    elif doc.metadata.get("validation_status") == "passed":
        console.print("[green]Validation:[/green] Passed Tier 1 checks")
```

**Estimated Changes:** ~55 lines modified

---

### Phase 6: Testing

**New File:** `/opt/data/docs_flow_framework/UCX/tests/creation/test_prd_creation.py`

```python
"""Tests for PRD creation improvements."""

import pytest
from pathlib import Path
from ucx.api.creation import UCCPhase
from ucx.config.settings import UCXConfig


class TestPRDPrompt:
    """Test UCC_PROMPT_PRD.md content."""

    def test_prompt_has_21_sections(self):
        """Verify prompt defines all 21 sections."""
        prompt_path = Path("UCX/creation/UCC_PROMPT_PRD.md")
        content = prompt_path.read_text()

        for section_num in range(1, 22):
            assert f"| {section_num} |" in content or f"## {section_num}." in content

    def test_prompt_forbids_bdd_patterns(self):
        """Verify Given-When-Then is forbidden."""
        prompt_path = Path("UCX/creation/UCC_PROMPT_PRD.md")
        content = prompt_path.read_text()

        assert "FORBIDDEN" in content
        assert "Given-When-Then" in content or "Given ... When ... Then" in content

    def test_prompt_requires_section_10(self):
        """Verify Section 10 is marked as BLOCKING."""
        prompt_path = Path("UCX/creation/UCC_PROMPT_PRD.md")
        content = prompt_path.read_text()

        assert "BLOCKING" in content
        assert "Section 10" in content or "Customer-Facing" in content

    def test_prompt_has_correct_type_codes(self):
        """Verify 13 element type codes defined."""
        prompt_path = Path("UCX/creation/UCC_PROMPT_PRD.md")
        content = prompt_path.read_text()

        expected_codes = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "11", "22", "23", "24"]
        for code in expected_codes:
            assert f"| {code} |" in content


class TestPersonaLoading:
    """Test persona skill loading."""

    def test_content_strategist_exists(self):
        """Verify content_strategist persona file exists."""
        path = Path("UCX/ucx/skills/personas/content_strategist.md")
        assert path.exists()

    def test_requirements_specialist_has_ucc_phase(self):
        """Verify requirements_specialist supports UCC phase."""
        path = Path("UCX/ucx/skills/personas/requirements_specialist.md")
        content = path.read_text()
        assert "ucc" in content.lower() or "creation" in content.lower()


class TestLayerSkills:
    """Test layer skills configuration."""

    def test_prd_has_seven_personas(self):
        """Verify PRD has 7 personas configured."""
        from ucx.config.layer_skills import UCC_LAYER_SKILLS
        from ucx.models.enums import DocType

        prd_skills = UCC_LAYER_SKILLS[DocType.PRD]
        assert len(prd_skills) == 7
        assert "content_strategist" in prd_skills
        assert "requirements_specialist" in prd_skills


class TestPostCreationScoring:
    """Test scoring integration (requires PLAN-010 Phase 7)."""

    def test_scoring_module_imported(self):
        """Verify scoring module imports correctly."""
        try:
            from ucx.validators.prd.scoring import PRDScorer, ReadinessScores
            assert PRDScorer is not None
            assert ReadinessScores is not None
        except ImportError:
            pytest.skip("PLAN-010 Phase 7 not implemented yet")

    def test_scores_computed_on_creation(self, tmp_path):
        """Verify scores computed and stored in metadata after creation."""
        try:
            from ucx.validators.prd.scoring import PRDScorer
        except ImportError:
            pytest.skip("PLAN-010 Phase 7 not implemented yet")

        # Create PRD with validation enabled
        ucc = UCCPhase(UCXConfig())
        output = tmp_path / "PRD-TEST.md"

        # Mock or use minimal upstream
        doc = ucc.create(
            doc_type="prd",
            output_path=output,
            validate_after=True,
        )

        # Verify scores in metadata
        assert "sys_ready_score" in doc.metadata
        assert "ears_ready_score" in doc.metadata
        assert isinstance(doc.metadata["sys_ready_score"], (int, float))
        assert isinstance(doc.metadata["ears_ready_score"], (int, float))

    def test_document_control_updated(self, tmp_path):
        """Verify Document Control section has scores injected."""
        try:
            from ucx.validators.prd.scoring import PRDScorer
        except ImportError:
            pytest.skip("PLAN-010 Phase 7 not implemented yet")

        ucc = UCCPhase(UCXConfig())
        output = tmp_path / "PRD-TEST.md"

        doc = ucc.create(
            doc_type="prd",
            output_path=output,
            validate_after=True,
        )

        content = output.read_text()
        assert "SYS-Ready:" in content
        assert "EARS-Ready:" in content
```

**Estimated Lines:** ~120

---

## Output Reports

### Unified Report Naming Convention

UCX uses a unified naming convention for all output reports:

```
{DOC_ID}.UCX_{report_type}_report_v{NNN}.md
```

| Phase | Report Type | Naming Pattern | Example |
|-------|-------------|----------------|---------|
| **UCC (Create)** | create | `{DOC_ID}.UCX_create_report_v{NNN}.md` | `PRD-01.UCX_create_report_v001.md` |
| **UCR (Validate)** | validate | `{DOC_ID}.UCX_validate_report_v{NNN}.md` | `PRD-01.UCX_validate_report_v001.md` |
| **UCR (Review)** | review | `{DOC_ID}.UCX_review_report_v{NNN}.md` | `PRD-01.UCX_review_report_v001.md` |
| **UCRem (Remediate)** | remediate | `{DOC_ID}.UCX_remediate_report_v{NNN}.md` | `PRD-01.UCX_remediate_report_v001.md` |

### Creation Report Structure (`UCX_create_report`)

The creation report is generated after `ucx create prd` completes:

```markdown
---
title: "UCX Create Report: PRD"
tags:
  - ucx-create
  - prd-create
  - layer-2-artifact
custom_fields:
  document_type: ucx-create-report
  source_artifact_type: PRD
  create_id: "UCX-PRD-01-create-v001"
  layer: 2
  template_used: PRD-MVP-TEMPLATE.md
  upstream_artifact: BRD-01
  personas_applied: 7
  sys_ready_score: 85.2
  ears_ready_score: 78.5
  validation_status: passed
  tier1_errors: 0
  last_updated: "2026-03-19T14:30:00"
---

# UCX Create Report: PRD-01

## 0. Document Control

| Item | Details |
|------|---------|
| **Created Document** | PRD-01 |
| **Create ID** | UCX-PRD-01-create-v001 |
| **Create Date** | 2026-03-19T14:30:00 |
| **Template Used** | PRD-MVP-TEMPLATE.md |
| **Template Profile** | MVP (threshold: 85%) |
| **Upstream Artifact** | BRD-01 |
| **Personas Applied** | 7 |

## 1. Readiness Scores

| Score | Value | Target | Status |
|-------|-------|--------|--------|
| **SYS-Ready** | 85.2% | ≥85% | ✅ PASS |
| **EARS-Ready** | 78.5% | ≥85% | ⚠️ DRAFT |

### SYS-Ready Breakdown
| Component | Weight | Score | Contribution |
|-----------|--------|-------|--------------|
| Product Completeness | 40% | 90% | 36.0% |
| Technical Readiness | 30% | 80% | 24.0% |
| Business Alignment | 20% | 85% | 17.0% |
| Traceability | 10% | 82% | 8.2% |

### EARS-Ready Breakdown
| Component | Weight | Score | Contribution |
|-----------|--------|-------|--------------|
| Timing Profiles | 25% | 70% | 17.5% |
| Boundary Values | 25% | 75% | 18.75% |
| State Machine | 25% | 85% | 21.25% |
| Fallback Paths | 15% | 80% | 12.0% |
| Threshold Registry | 10% | 90% | 9.0% |

## 2. Validation Summary

| Check | Status |
|-------|--------|
| Tier 1 (Blocking) | ✅ Passed (0 errors) |
| Section 10 Content | ✅ Substantive |
| Section 8 Layer Note | ✅ Present |
| Element ID Format | ✅ Valid |
| Forward References | ✅ None |

## 3. Created Files

| File | Sections | Elements |
|------|----------|----------|
| PRD-01.0_index.md | Index | — |
| PRD-01.1_document_control.md | 1 | 0 |
| PRD-01.5_features.md | 5 | 12 |
| PRD-01.8_user_stories.md | 8 | 24 |
| PRD-01.10_customer_content.md | 10 | 8 |
| ... | ... | ... |

## 4. Next Steps

- [ ] Run `ucx validate prd PRD-01/` for full validation
- [ ] Address EARS-Ready gaps (Timing Profiles, Boundary Values)
- [ ] Run `ucx review prd PRD-01/` for AI review
```

### Report Location

Reports are saved in the same directory as the document:

```
docs/02_PRD/PRD-01/
├── PRD-01.0_index.md
├── PRD-01.1_document_control.md
├── ...
├── PRD-01.UCX_create_report_v001.md    ← Creation report
├── PRD-01.UCX_validate_report_v001.md  ← Validation report (PLAN-010)
├── PRD-01.UCX_review_report_v001.md    ← Review report (PLAN-010)
└── PRD-01.UCX_remediate_report_v001.md ← Remediation report (PLAN-010)
```

### Version Incrementing

Each report type has independent versioning:
- `ucx create prd` → finds max `UCX_create_report_v*` → increments
- `ucx validate prd` → finds max `UCX_validate_report_v*` → increments
- `ucx review prd` → finds max `UCX_review_report_v*` → increments
- `ucx remediate` → finds max `UCX_remediate_report_v*` → increments

### Backward Compatibility

> **Note**: This unified naming replaces the legacy format:
> - `UCR_review_report` → `UCX_review_report`
> - `UCRem_remediation_report` → `UCX_remediate_report`
>
> Legacy reports will still be detected for version incrementing during transition.

---

## Project-Specific Prompt Customization

### Overview

UCX supports project-specific prompt overrides that inject domain context without modifying the framework prompt. This enables projects like b-local-docs to create PRDs with domain-specific terminology, partners, and requirements.

### Prompt Resolution Order

```python
# ucx/api/creation.py:166-183
def _load_prompt(self, doc_type: DocType) -> str:
    prompt_dir = self.config.get_prompt_dir() / "ucc"

    candidates = [
        prompt_dir / f"UCC_PROMPT_{doc_type.value.upper()}_PROJECT.md",  # Priority 1
        prompt_dir / f"UCC_PROMPT_{doc_type.value.upper()}.md",          # Fallback
    ]
```

| Priority | File Pattern | Location |
|----------|--------------|----------|
| 1 | `UCC_PROMPT_PRD_PROJECT.md` | `{PROJECT}/docs/UCX/creation/` |
| 2 | `UCC_PROMPT_PRD.md` | `{FRAMEWORK}/UCX/creation/` |

### Project Directory Structure

```
{PROJECT_ROOT}/
├── docs/
│   └── UCX/
│       ├── creation/
│       │   ├── UCC_PROMPT_BRD_PROJECT.md   ← BRD customization
│       │   └── UCC_PROMPT_PRD_PROJECT.md   ← PRD customization (NEW)
│       ├── review/
│       ├── remediation/
│       └── skills/
└── .envrc                                   ← Sets UCX_PROJECT_ROOT
```

### Project-Specific PRD Prompt Template

**File**: `{PROJECT}/docs/UCX/creation/UCC_PROMPT_PRD_PROJECT.md`

```markdown
# UCC Prompt: {PROJECT_NAME} PRD Creation - Layer 2

## Instructions

You are creating a Product Requirements Document (PRD) for **{PROJECT_NAME}** -
{one-line project description}.

---

## Domain Context

| Aspect | Details |
|--------|---------|
| **Domain** | {business domain} |
| **Technology** | {tech stack} |
| **Partners** | {key integrations} |
| **Regulations** | {compliance requirements} |

---

## PRD-Specific Customizations

### Section 10: Customer-Facing Content (BLOCKING)

{Project-specific customer messaging requirements}

### Section 8: User Stories (Layer Separation)

{Project-specific user story guidance with layer separation reminder}

---

## Feature Areas

| Feature Area | PRD Element Codes | Key Features |
|--------------|-------------------|--------------|
| {Area 1} | PRD.XX.TT | {features} |
| {Area 2} | PRD.XX.TT | {features} |

---

## Partner Integration Requirements

| Partner | Function | PRD-Level Specs |
|---------|----------|-----------------|
| {Partner 1} | {function} | {requirements} |
| {Partner 2} | {function} | {requirements} |

---

## Upstream Traceability

This PRD MUST trace to BRD elements:
- @upstream: BRD-XX ({description})

---

## Creation Checklist

- [ ] All 21 sections present
- [ ] Section 10 has substantive {project} customer content
- [ ] Section 8 includes layer separation note
- [ ] Element IDs use PRD.NN.TT.SS format
- [ ] No Given-When-Then patterns (→ BDD)
- [ ] Upstream BRD references included
- [ ] Partner integrations specified at PRD level
- [ ] Dual readiness scores placeholder in Document Control
```

### Example: b-local-docs

**File**: `/opt/data/b-local/b-local-docs/docs/UCX/creation/UCC_PROMPT_PRD_PROJECT.md`

Key customizations for BeeLocal:

| Section | BeeLocal-Specific Content |
|---------|---------------------------|
| Domain Context | US→Uzbekistan remittance, USDC, GCP |
| Partners | Bridge/Noah, Asterium, Paynet, Okto, Nuvei, Modern Treasury |
| Regulations | FinCEN, OFAC, AML/KYC, PCI-DSS |
| Section 10 | "Send money home" messaging, fee transparency |
| Feature Areas | Onboarding, Send Flow, Compliance, Settlement |

### Interaction with Framework Prompt

| Aspect | Framework Prompt | Project Prompt |
|--------|------------------|----------------|
| 21-section structure | Defined | Inherits (not duplicated) |
| Element type codes | Defined (13 codes) | Inherits |
| Domain terminology | Generic | **Project-specific** |
| Partner details | None | **Project-specific** |
| Regulatory context | Generic | **Project-specific** |
| Section 10 content | Generic guidance | **Project-specific messaging** |

The project prompt **augments** the framework prompt. Projects should NOT duplicate structural guidance (sections, codes, formats) - only add domain-specific context.

### Environment Configuration

Projects must set `UCX_PROJECT_ROOT` for prompt resolution:

```bash
# .envrc (loaded by direnv)
export UCX_PROJECT_ROOT="$PWD"
```

Or via `ucx.yaml`:

```yaml
# {PROJECT}/ucx.yaml
project_dir: /path/to/project
```

---

## Project-Specific Skill Customization

### Overview

Projects can customize persona skills with domain-specific knowledge. For PRD creation and review, project skills should include PRD-specific focus areas in addition to generic domain context.

### Skill Resolution Order

```
1. {PROJECT}/docs/UCX/skills/{persona}.md    ← Project-specific (if exists)
2. {FRAMEWORK}/UCX/skills/{persona}.md       ← Framework fallback
```

### Current b-local-docs Skills Gap

**Location:** `/opt/data/b-local/b-local-docs/docs/UCX/skills/`

| Persona | Exists | PRD Weight | PRD-Specific Sections | Action |
|---------|--------|------------|----------------------|--------|
| auditor | ✅ | 20% | ❌ | Add PRD focus |
| architect | ✅ | 15% | ❌ | Add PRD focus |
| product_owner | ✅ | 30% | ❌ | Add PRD focus |
| tech_lead | ✅ | 25% | ❌ | Add PRD focus |
| chaos_engineer | ✅ | 25% | ❌ | Add PRD focus |
| ux_strategist | ✅ | 20% | ❌ | Add PRD focus |
| integration_lead | ✅ | 20% | ❌ | Add PRD focus |
| content_strategist | ❌ | — | — | **Create** |

### Required Updates

#### 1. Create `content_strategist.md` (Project-Specific)

**File:** `{PROJECT}/docs/UCX/skills/content_strategist.md`

```markdown
# BeeLocal Content Strategist Domain Knowledge

## Role
Content Strategist responsible for customer-facing messaging and Section 10 compliance.

## BeeLocal Customer Messaging

### Value Proposition
- "Send money home instantly" - primary messaging
- US→Uzbekistan corridor benefit messaging
- Fee transparency (FinCEN requirement)
- Speed comparison vs traditional remittance

### Section 10 Requirements (BLOCKING)

Section 10 (Customer-Facing Content) MUST include:

| Content Type | BeeLocal Requirement |
|--------------|---------------------|
| Onboarding messaging | KYC tier explanation, document requirements |
| Send flow copy | Quote display, fee breakdown, exchange rate |
| Confirmation messaging | Transaction status, expected delivery time |
| Error messaging | Clear, actionable error states |
| Compliance disclosures | FinCEN, fee disclosure requirements |

### Anti-Patterns to Flag

- **Generic placeholder**: "Add customer content here"
- **Missing fee disclosure**: Fees not clearly stated
- **Vague delivery time**: "Soon" instead of specific timeframes
- **Technical jargon**: Internal terms exposed to customers
- **Missing error states**: Only happy path messaging

### Review Focus for PRD
- Section 10 has substantive BeeLocal customer content
- Fee transparency requirements met
- Delivery time expectations clear
- Error messaging complete
- Compliance disclosures included

### Quality Criteria
- 100% of customer touchpoints have messaging defined
- Fee disclosure meets FinCEN requirements
- Delivery time expectations are realistic
- Error states have actionable messaging

## Scoring Weight
- PRD: 25% (Section 10 is BLOCKING)
- BRD: 10%

## Tags
- phase: ucc, ucr
- doc_types: [prd, brd]
- priority: high
- domain: beelocal
- category: content
```

#### 2. Add PRD-Specific Sections to Existing Skills

Each project skill should include a PRD-specific section:

**Example: `auditor.md` PRD Section**

```markdown
## PRD Review Focus

### Section Mappings
| PRD Section | Auditor Focus |
|-------------|---------------|
| 13. Quality Attributes | Compliance SLAs (SAR 30-day, CTR reporting) |
| 14. Constraints | Regulatory constraints (MTL, PCI-DSS scope) |
| 17. Upstream Traceability | BRD compliance requirements traced |

### PRD-Specific Checks
- [ ] KYC tier limits from BRD reflected in PRD features
- [ ] SAR workflow human review requirement in user stories
- [ ] OFAC screening mentioned in relevant features
- [ ] PCI-DSS scope for payment features defined
- [ ] Session timeout requirements in security features

### PRD Anti-Patterns
- Feature without compliance consideration
- User story missing regulatory constraint
- Acceptance criteria without compliance verification
```

**Example: `product_owner.md` PRD Section**

```markdown
## PRD Review Focus

### Section Mappings
| PRD Section | Product Owner Focus |
|-------------|---------------------|
| 5. High-Level Features | Feature completeness, MVP scope |
| 8. User Stories | Story format, acceptance criteria |
| 10. Customer-Facing Content | **BLOCKING** - substantive content |
| 11. Success Metrics | KPIs measurable and realistic |

### PRD-Specific Checks
- [ ] All BRD functional requirements have PRD features
- [ ] User stories follow standard format
- [ ] Section 10 has BeeLocal-specific customer content
- [ ] Success metrics are measurable (not "improve" but "increase by X%")
- [ ] MVP scope boundaries clear

### Layer Separation Enforcement
Section 8 MUST include layer separation note. Flag if:
- Given-When-Then patterns in user stories (→ BDD)
- Timing profiles in stories (→ EARS)
- State machine details in stories (→ EARS)
```

### Project Skill Update Checklist

For each persona in `{PROJECT}/docs/UCX/skills/`:

- [ ] Add `## PRD Review Focus` section
- [ ] Add `### Section Mappings` table
- [ ] Add `### PRD-Specific Checks` checklist
- [ ] Add `### PRD Anti-Patterns` list
- [ ] Verify PRD in `doc_types` tag
- [ ] Set appropriate PRD scoring weight

### Files to Update (b-local-docs)

| File | Changes | Lines (est) |
|------|---------|-------------|
| `docs/UCX/skills/content_strategist.md` | **Create** | ~100 |
| `docs/UCX/skills/auditor.md` | Add PRD section | +40 |
| `docs/UCX/skills/architect.md` | Add PRD section | +35 |
| `docs/UCX/skills/product_owner.md` | Add PRD section | +40 |
| `docs/UCX/skills/tech_lead.md` | Add PRD section | +35 |
| `docs/UCX/skills/chaos_engineer.md` | Add PRD section | +35 |
| `docs/UCX/skills/ux_strategist.md` | Add PRD section | +35 |
| `docs/UCX/skills/integration_lead.md` | Add PRD section | +35 |
| `docs/UCX/skills/qa_lead.md` | Add PRD section | +35 |
| `docs/UCX/skills/strategist.md` | Add PRD section | +30 |
| `docs/UCX/skills/business_analyst.md` | Add PRD section | +30 |

**Total Project Skill Updates:** ~450 lines

---

## Critical Files Summary

### Framework Files to Rewrite (1 file)

| File | Action | Lines (est) |
|------|--------|-------------|
| `UCX/creation/UCC_PROMPT_PRD.md` | Full rewrite | ~450 |

### Framework Files to Create (2 files)

| File | Purpose | Lines (est) |
|------|---------|-------------|
| `ucx/skills/personas/content_strategist.md` | Section 10 persona | ~80 |
| `tests/creation/test_prd_creation.py` | Unit tests | ~120 |

### Framework Files to Modify (4 files)

| File | Changes | Lines (est) |
|------|---------|-------------|
| `ucx/skills/personas/requirements_specialist.md` | Add UCC/PRD context | +50 |
| `ucx/config/layer_skills.py` | Add 2 personas | +5 |
| `ucx/api/creation.py` | Post-creation validation + scoring hook | +75 |
| `ucx/cli/main.py` | --validate, --strict flags, score display | +55 |

**Framework Total:** ~915 lines

### Project-Specific Files (b-local-docs example)

| File | Changes | Lines (est) |
|------|---------|-------------|
| `docs/UCX/skills/content_strategist.md` | **Create** (BeeLocal customer messaging) | ~100 |
| `docs/UCX/skills/auditor.md` | Add PRD review focus section | +40 |
| `docs/UCX/skills/architect.md` | Add PRD review focus section | +35 |
| `docs/UCX/skills/product_owner.md` | Add PRD review focus section | +40 |
| `docs/UCX/skills/tech_lead.md` | Add PRD review focus section | +35 |
| `docs/UCX/skills/chaos_engineer.md` | Add PRD review focus section | +35 |
| `docs/UCX/skills/ux_strategist.md` | Add PRD review focus section | +35 |
| `docs/UCX/skills/integration_lead.md` | Add PRD review focus section | +35 |
| `docs/UCX/skills/qa_lead.md` | Add PRD review focus section | +35 |
| `docs/UCX/skills/strategist.md` | Add PRD review focus section | +30 |
| `docs/UCX/skills/business_analyst.md` | Add PRD review focus section | +30 |
| `docs/UCX/creation/UCC_PROMPT_PRD_PROJECT.md` | **Create** (BeeLocal PRD prompt) | ~150 |

**Project Total:** ~600 lines

**Grand Total:** ~1,515 lines (framework + project)

---

## Dependencies

| This Plan | Depends On | Type |
|-----------|------------|------|
| Phase 4 (Post-Validation) | PLAN-010 Phases 0-6 | Validator import |
| Phase 4 (Post-Scoring) | PLAN-010 Phase 7 | Scoring module import |

**Recommended Order:**
1. Implement PLAN-009 Phases 1-3, 5-6 (no validator/scorer dependency)
2. Implement PLAN-010 Phases 0-6 (validator core)
3. Implement PLAN-010 Phase 7 (scoring module - **authoritative source**)
4. Implement PLAN-009 Phase 4 (post-validation + scoring hook)
5. Implement PLAN-010 Phases 8-11 (auto-fixer, AI review prompt, integration, testing)

---

## Success Criteria

### Framework Prompt
1. UCC_PROMPT_PRD.md has complete 21-section structure
2. No Given-When-Then patterns in prompt or created PRDs
3. Section 10 guidance ensures substantive content
4. Section 8 includes layer separation note requirement
5. 13 element type codes documented correctly
6. Dual scoring guidance included (SYS-Ready, EARS-Ready)
7. Diagram requirements specified (c4-l2, dfd-l1, sequence-*)
8. 7 personas contribute to PRD creation

### Post-Creation Hooks
9. Post-creation validation runs automatically (when PLAN-010 ready)
10. Post-creation scoring runs automatically (when PLAN-010 Phase 7 ready)
11. Scores injected into Document Control section of created PRDs
12. CLI displays computed scores with color-coded pass/warn/fail

### Project-Specific Prompts
13. Project prompt resolution order documented (PROJECT → framework fallback)
14. Project prompt template provided with placeholder sections
15. UCX_PROJECT_ROOT environment variable documented
16. b-local-docs example customizations documented

### Project-Specific Skills
17. Project skill resolution order documented
18. `content_strategist.md` created for b-local-docs (Section 10 BeeLocal messaging)
19. All project personas have PRD review focus sections
20. PRD section mappings documented for each persona
21. PRD-specific anti-patterns defined per persona

### Output Reports
22. Creation generates `{DOC_ID}.UCX_create_report_v{NNN}.md`
23. Report includes dual scores (SYS-Ready, EARS-Ready)
24. Report includes validation summary and created files list
25. Version incrementing works correctly

### Testing
26. All unit tests pass
27. Project-specific prompt loading verified
28. Project-specific skill loading verified
29. Creation report generation verified

---

## Verification Plan

```bash
# Verify prompt structure
grep -c "## [0-9]" UCX/creation/UCC_PROMPT_PRD.md  # Should show section count

# Verify BDD patterns forbidden
grep -i "forbidden" UCX/creation/UCC_PROMPT_PRD.md
grep -i "given-when-then" UCX/creation/UCC_PROMPT_PRD.md

# Verify personas
ls -la UCX/ucx/skills/personas/content_strategist.md
grep -i "ucc" UCX/ucx/skills/personas/requirements_specialist.md

# Test PRD creation
ucx create prd docs/02_PRD/PRD-TEST.md \
    --from-upstream docs/01_BRD/BRD-01/ \
    --validate

# Verify created PRD
grep "Layer Separation Note" docs/02_PRD/PRD-TEST.md
grep "## 10." docs/02_PRD/PRD-TEST.md
grep -E "PRD\.\d{2}\.\d{2}\.\d{2}" docs/02_PRD/PRD-TEST.md

# Run tests
pytest tests/creation/test_prd_creation.py -v

# Verify project-specific prompt resolution
cd /opt/data/b-local/b-local-docs
ls -la docs/UCX/creation/UCC_PROMPT_PRD_PROJECT.md  # Should exist

# Test project-specific prompt loading
UCX_PROJECT_ROOT=/opt/data/b-local/b-local-docs \
ucx create prd docs/02_PRD/PRD-TEST.md \
    --from-upstream docs/01_BRD/BRD-01/ \
    --validate

# Verify BeeLocal-specific content in created PRD
grep -i "beelocal\|remittance\|usdc" docs/02_PRD/PRD-TEST.md

# Verify project-specific skills
ls -la docs/UCX/skills/content_strategist.md  # Should exist

# Verify PRD review focus in project skills
grep -l "PRD Review Focus" docs/UCX/skills/*.md  # Should list all personas

# Verify PRD section mappings in skills
grep -c "PRD Section" docs/UCX/skills/auditor.md  # Should show section table

# Test project skill loading
UCX_PROJECT_ROOT=/opt/data/b-local/b-local-docs \
ucx review prd docs/02_PRD/PRD-01/ 2>&1 | grep -i "loading.*skill"
```

---

## Backward Compatibility

**Existing PRDs created with old prompt:**
- Will fail validation with new validator (PLAN-010)
- Use `ucx remediate` to fix issues
- Migration path: old format → validate → remediate → new format

**Gradual Rollout:**
1. Update prompt (this plan)
2. New PRDs use new format
3. Existing PRDs remediated as needed
4. No forced migration required

---

## Removed from Plan (v1 → v2)

| Removed Item | Reason |
|--------------|--------|
| `ucx/creation/template_sync.py` | UCX is prompt-driven, not code-driven |
| `ucx/creation/section_generators/` | Not compatible with UCX architecture |
| `ucx/creation/scoring_generator.py` | Scoring guidance in prompt instead |
| Duplicate `requirements_specialist.md` | File already exists, update instead |

---

*Plan Version: v7 (Unified output reports, project-specific skills, upstream optimization, quota recovery)*
*Generated: 2026-03-19*

---

## Phase 7: Creation Prompt History (v1.21.0)

**Goal**: Save the assembled creation prompt to disk by default so users can audit, debug, and reuse prompts.

### Behaviour

- `ucx create` saves the full assembled prompt to `.ucx_create_session/prompt_<type>_<timestamp>.txt` **by default**.
- File includes a self-documenting header with doc type, timestamp, upstream path, ref path, IPLAN path, and prompt size in chars.
- Use `--no-save-prompt` to disable.

Session location rules:
- Sectioned single-file outputs (`PRD-01_{slug}.md`) store session files under `{doc_folder}/.ucx_create_session/`.
- Simple single-file outputs store session files under `{parent}/.ucx_create_session/`.
- Directory/multi-file outputs store session files under `{output_dir}/.ucx_create_session/`.

### Files Changed

| File | Change |
|------|--------|
| `ucx/api/creation.py` | Added `save_prompt: bool = True` param to `create()`; added `_save_prompt_to_session()` method; new module constant `CREATE_SESSION_DIR = ".ucx_create_session"` |
| `ucx/cli/main.py` | Added `--save-prompt/--no-save-prompt` flag (default enabled); displays saved path in output |
| `ucx/validators/brd/fixer.py` | Added `.ucx_create_session` to skip list |
| `ucx/validators/brd/duplicate_fixer.py` | Added `.ucx_create_session` to two skip lists |
| `ucx/prompts/document.py` | Added `.ucx_create_session` to `SKIP_PATTERNS` |

### Session Directory Layout

```
docs/02_PRD/PRD-01_platform_architecture/
├── PRD-01_platform_architecture.md
└── .ucx_create_session/
    ├── prompt_prd_20260319T142301Z.txt
    ├── prompt_prd_20260320T091500Z.txt   ← each run appends a new file
    └── ...
```

### Python API

```python
# Default: prompt is saved automatically
doc = ucc.create("prd", output_path, from_upstream=brd_path)

# Opt out
doc = ucc.create("prd", output_path, from_upstream=brd_path, save_prompt=False)

# Inspect where it was saved
print(doc.metadata.get("prompt_saved_path"))
```

---

## Phase 8: Upstream Context Optimization and Slugged Output (v1.21.0)

**Goal**: Reduce PRD creation token waste from sectioned BRD folders and improve output naming deterministically.

### Behaviour

- `--from-upstream` for sectioned BRD now resolves section files from `*.0_index.md` links, not from naive directory-wide `*.md` scanning.
- YAML frontmatter, HTML comments, and navigation boilerplate are stripped before prompt assembly.
- Low-signal heavy blocks are compacted deterministically:
    - Mermaid diagrams -> compact placeholders (`[Diagram omitted for token efficiency: Mermaid ...]`)
    - Cross-BRD dependency tables -> compact bullet summary
    - Reference-heavy subsections -> compact list summary
- If `output_path` is a plain doc ID (`PRD-01` or `PRD-01.md`) and upstream is slugged (`BRD-01_platform_architecture`), output path is normalized to `PRD-01_platform_architecture.md`.

### Files Changed

| File | Change |
|------|--------|
| `ucx/api/creation.py` | Added `_resolve_section_files()`, `_strip_file_boilerplate()`, section compaction helpers, `_normalize_output_path()`, `_infer_slug_from_upstream()` |
| `ucx/cli/main.py` | Updated `create` help text/examples for slugged output behavior |
| `README.md` | Updated PRD creation examples to sectioned BRD upstream paths |
| `docs/HOW_TO_CREATE_PRD.md` | Added auto-slug behavior documentation and updated examples |
| `docs/HOW_TO_USE.md` | Updated PRD creation examples and expected output filenames |

### Verification

```bash
# Plain doc ID + slugged upstream yields slugged output filename
ucx --project-dir . create prd docs/02_PRD/PRD-01 \
    --from-upstream docs/01_BRD/BRD-01_platform_architecture \
    --no-validate

# Expect output file path suffix: PRD-01_platform_architecture.md
```

---

## Phase 9: Quota-Aware Failure Handling and Retry Prompt (v1.21.0+)

**Goal**: Handle CLI model quota/rate-limit failures gracefully and guide user to retry with another backend/model.

### Behaviour

- `CLIClient` now captures useful error text from both `stderr` and `stdout` (some CLIs emit fatal errors to `stdout`).
- Quota/rate-limit phrases are detected and surfaced with explicit guidance.
- `ucx create` catches quota-related `AIClientError` and:
    - prints a clear, user-facing quota message;
    - in interactive TTY mode, asks user which backend/model to try next and retries once;
    - in non-interactive mode, prints exact rerun guidance and exits with non-zero code.

### Files Changed

| File | Change |
|------|--------|
| `ucx/ai/cli_client.py` | Enhanced `CalledProcessError` handling to include stdout, quota phrase detection, and actionable guidance |
| `ucx/cli/main.py` | `create` now catches quota/rate-limit `AIClientError`, prompts for backend/model in interactive mode, retries once |

### Verification

```bash
# Non-interactive sanity check should print guidance (not generic "No error output")
ucx --project-dir . --model sonnet create prd docs/02_PRD/PRD-01 \
    --from-upstream docs/01_BRD/BRD-01_platform_architecture \
    --no-validate < /dev/null

# Interactive mode should ask for backend/model when quota is hit
ucx --project-dir . --model sonnet create prd docs/02_PRD/PRD-01 \
    --from-upstream docs/01_BRD/BRD-01_platform_architecture \
    --no-validate
```
