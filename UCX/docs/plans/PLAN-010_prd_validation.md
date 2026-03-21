# PLAN-010: PRD Validation and Remediation

**Document ID**: PLAN-010_prd_validation
**Created**: 2026-03-19
**Updated**: 2026-03-20
**Status**: Revised (v10)
**Target Version**: UCX v1.21.3
**Related Plans**: PLAN-009_prd_creation.md (creation counterpart)

---

## Objective

Extend UCX Framework unified validation approach from BRD (Layer 1) to PRD (Layer 2), maintaining architectural consistency with the proven BRD validator pattern while aligning validation rules and scripts with the implemented PRD creation pipeline.

---

## UCX Architecture Context

UCX provides three phases for SSD document lifecycle:

| Phase | Command | Purpose | Status |
|-------|---------|---------|--------|
| **UCC** | `ucx create` | Create documents from templates/upstream | Implemented |
| **UCR** | `ucx validate` | Validate structure, quality gates, scoring | **This Plan** |
| **UCRem** | `ucx remediate` | Fix issues with auto-fixer + LLM hand-off | **This Plan** |

PRD creation is already handled by UCC (`ucx create prd`). This plan implements UCR and UCRem for PRD and defines the validation baseline that must remain compliant with the implemented PRD creation workflow.

### Current Create/Validate Alignment Baseline (v1.21.3)

The PRD validator and related scripts must remain compatible with the current UCC create behavior:

| Area | Current Runtime Behavior | Validation/Script Requirement |
|------|--------------------------|-------------------------------|
| Prompt loading | Framework PRD prompt + project PRD overrides are merged | Validation guidance and docs must not assume project prompts replace framework contracts |
| Output contract | UCC injects target `doc_id`, H1, Document Control, and element-prefix requirements before generation | Validation must check the same identity fields and treat mismatches as creation/metadata drift |
| Frontmatter guardrails | UCC normalizes top-level `title`, `doc_id`, `version`, `status`, `tags` before write | Validation must require the same top-level fields |
| YAML delimiters | UCC/validators accept frontmatter delimiters with trailing spaces | Validation regex and helper scripts must allow tolerant delimiter parsing |
| Prompt history | Canonical PRD path saves `.ucx_create_session/` beside the PRD file | Scripts/docs must reference `docs/02_PRD/<slug>/.ucx_create_session/` as the canonical path |
| Validation report path | `ucx validate prd` writes `.precommit_validation_report.md` in the PRD folder | Plan and scripts must use single-file validation report naming |

### Revision History

| Revision | Date | Summary |
|----------|------|---------|
| v10 | 2026-03-20 | Updated remediation artifact model to canonical UCX report naming and single-report behavior: remediation details and fix blocks are consolidated into `{DOC_ID}.UCX_remediation_report_v{NNN}.md`; removed legacy UCRem sidecar assumptions. |
| v9 | 2026-03-20 | Added PRD UCR finding-ID lifecycle alignment with BRD approach: persona output IDs use `{PREFIX}-P{PRIORITY}-{NNN}` and assembled report IDs use canonical hash format `P{0\|1\|2}-{hex}` for scoring/traceability. |
| v8 | 2026-03-20 | Added create/validate alignment history for PRD refresh fixes: exact PRD metadata guardrails, deterministic Section 8 note injection, narrower PRD-E005 detection for document-level references, and stronger prompt contracts for score-driving element families. |
| v7 | 2026-03-20 | Aligned plan with current runtime naming, prompt merge behavior, canonical session history path, and unified PRD validation report generation. |

---

## Background

### BRD Validator (v1.19.2) - Production Ready
- Unified UCX-ACTION format for task tracking
- Tiered validation (Tier 1 blocking, Tier 2 advisory)
- 10 GATE checks (GATE-01 through GATE-10)
- Auto-fixer with LLM hand-off and protected changes
- 8 Python modules + 7 shared utilities in `common/`

### PRD Layer Requirements (From Template Analysis)

| Aspect | BRD (Layer 1) | PRD (Layer 2) |
|--------|---------------|---------------|
| Quality Gates | 10 checks | 19 corpus-level (CORPUS-01 to CORPUS-19) |
| Element Types | 17 codes | 13 codes (01-09, 11, 22, 23, 24) |
| Sections | 18 (MVP) | 21 (both MVP and Standard) |
| Diagram Level | C4-L1, DFD-L0 | C4-L2, DFD-L1 |
| Ready Scores | PRD-Ready single | SYS-Ready + EARS-Ready dual |
| MVP Threshold | N/A | ≥85% |
| Standard Threshold | ≥90% | ≥90% |
| Forward Refs | Can reference PRD | Cannot reference ADR/SYS/REQ/SPEC/TASKS |
| Mandatory Section | None | Section 10 (Customer-Facing Content) |
| Layer Separation | N/A | Section 8 requires scope note |

---

## Implementation Phases

### Phase 0: Common Module Extensions
Extend shared utilities before creating PRD validator.

**Files to Modify:**
- `/opt/data/docs_flow_framework/UCX/ucx/validators/common/error_codes.py`
  - Add PRD error codes (PRD-E001 through PRD-E030)
  - Add PRD warning codes (PRD-W001 through PRD-W025)
  - Add PRD info codes (PRD-I001, PRD-I002)
  - Add CORPUS error/warning codes (CORPUS-E001 through CORPUS-E019)

- `/opt/data/docs_flow_framework/UCX/ucx/validators/common/result.py`
  - Ensure `DocType.PRD` enum exists
  - Add PRD-specific validation context fields

**Deliverable:** PRD error codes registered in shared module

---

### Phase 1: Foundation Setup
Create directory structure and base files.

**Directory:**
```
/opt/data/docs_flow_framework/UCX/ucx/validators/prd/
├── __init__.py        # UnifiedPRDValidator class
├── schema.py          # Constants, element codes, mappings
├── structure.py       # Section validation + template detection
├── metadata.py        # Frontmatter validation
├── element_codes.py   # PRD.NN.TT.SS validation
├── quality_gate.py    # File-level checks (PRD-E/W)
├── corpus_gate.py     # Corpus-level checks (CORPUS-01 to CORPUS-19)
├── scoring.py         # SYS-Ready/EARS-Ready calculation (AUTHORITATIVE)
├── fixer.py           # Auto-fixer with UCX-ACTION
└── duplicate_fixer.py # Duplicate element handling
```

**Total:** 10 files

---

### Phase 2: Schema Definition (`schema.py`)

**Element Type Codes (13 codes):**

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

**Section Structure (21 Mandatory Sections):**

```python
REQUIRED_SECTIONS = {
    1: "Document Control",
    2: "Executive Summary",
    3: "Problem Statement",
    4: "Target Audience & User Personas",
    5: "Success Metrics (KPIs)",
    6: "Goals & Objectives",
    7: "Scope & Requirements",
    8: "User Stories & User Roles",
    9: "Functional Requirements",
    10: "Customer-Facing Content & Messaging",  # BLOCKING
    11: "Acceptance Criteria",
    12: "Constraints & Assumptions",
    13: "Risk Assessment",
    14: "Success Definition",
    15: "Stakeholders & Communication",
    16: "Implementation Approach",
    17: "Budget & Resources",
    18: "Traceability",
    19: "References",
    20: "EARS Enhancement Appendix",
    21: "Quality Assurance & Testing Strategy",
}
```

**Section-to-Code Mapping:**
```python
SECTION_CODE_MAP = {
    "1": [],                    # Document Control - no elements
    "2": [],                    # Executive Summary
    "3": [],                    # Problem Statement
    "4": ["24"],                # Target Audience (Stakeholder Need)
    "5": ["08"],                # Success Metrics (Metric/KPI)
    "6": ["23"],                # Goals & Objectives (Goal)
    "7": ["05", "22"],          # Scope & Requirements (Dependency, Feature)
    "8": ["09"],                # User Stories (User Story)
    "9": ["01", "11", "22"],    # Functional Requirements (FR, Use Case, Feature)
    "10": [],                   # Customer-Facing Content (BLOCKING - no IDs)
    "11": ["06"],               # Acceptance Criteria
    "12": ["03", "04"],         # Constraints & Assumptions
    "13": ["07"],               # Risk Assessment
    "14": [],                   # Success Definition
    "15": ["24"],               # Stakeholders (Stakeholder Need)
    "16": [],                   # Implementation Approach
    "17": [],                   # Budget & Resources
    "18": [],                   # Traceability
    "19": [],                   # References
    "20": [],                   # EARS Enhancement Appendix
    "21": ["02"],               # Quality Assurance (Quality Attribute)
}
```

**Template Profiles:**
```python
TEMPLATE_PROFILES = {
    "mvp": {
        "sections": 21,
        "sys_ready_threshold": 85,
        "ears_ready_threshold": 85,
    },
    "standard": {
        "sections": 21,
        "sys_ready_threshold": 90,
        "ears_ready_threshold": 90,
    },
}
```

**Forward Reference Blocking Patterns:**
```python
FORBIDDEN_DOWNSTREAM_PATTERNS = [
    r"ADR-\d{2,}",              # Layer 5
    r"SYS-\d{2,}",              # Layer 6
    r"REQ-\d{2,}",              # Layer 7
    r"SPEC-\d{2,}",             # Layer 9
    r"TASKS-\d{2,}",            # Layer 11
    r"@adr:\s*ADR-",
    r"@sys:\s*SYS-",
    r"@req:\s*REQ-",
    r"@spec:\s*SPEC-",
]
```

**Legacy Pattern Detection:**
```python
LEGACY_PATTERNS = {
    r"FR-\d{3}": "PRD.NN.01.SS",
    r"NFR-\d{3}": "PRD.NN.02.SS",
    r"AC-\d{3}": "PRD.NN.06.SS",
    r"BC-\d{3}": "PRD.NN.03.SS",
    r"BA-\d{3}": "PRD.NN.04.SS",
    r"QA-\d{3}": "PRD.NN.02.SS",
    r"RISK-\d{3}": "PRD.NN.07.SS",
    r"METRIC-\d{3}": "PRD.NN.08.SS",
    r"US-\d{3}": "PRD.NN.09.SS",
    r"F-\d{3}": "PRD.NN.09.SS",
    r"Feature-\d{3}-\d{3}": "PRD.NN.22.SS",
}
```

---

### Phase 3: Core Validation (`structure.py`, `metadata.py`)

**Structure Validation:**
- All 21 sections required (both MVP and Standard)
- Section numbering: `## N. Section Title` format
- Section 10 (Customer-Facing Content) is **BLOCKING** - cannot be empty/placeholder
- Section 8 requires layer separation note
- File naming: `PRD-NN_slug.md` or `PRD-NN.S_slug.md`
- PRD-00_* exempt from validation (index, templates)

**Metadata Validation:**
```yaml
# Required top-level frontmatter fields (aligned with creation guardrails)
title: "PRD-NN: ..."
doc_id: PRD-NN
version: 1.0.0
status: Draft | Review | Approved
tags: [...]
```

```yaml
# Required custom_fields
document_type: prd
artifact_type: PRD
layer: 2
schema_version: "1.1"

# Required tags
- prd
- layer-2-artifact

# Forbidden tag patterns
- ^product-prd$
- ^feature-prd$
- ^prd-\d{2,}$
```

**Document Control (11 mandatory + 4 optional fields):**

| Field | Format | Requirement |
|-------|--------|-------------|
| Status | Draft / Review / Approved | MANDATORY |
| Version | X.Y.Z (semantic) | MANDATORY |
| Date Created | YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS | MANDATORY |
| Last Updated | YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS | MANDATORY |
| Author | Name | MANDATORY |
| Reviewer | Name | MANDATORY |
| Approver | Name | MANDATORY |
| BRD Reference | `@brd: BRD.NN.TT.SS` (4-segment) | MANDATORY |
| SYS-Ready Score | `[PASS] NN% (Target: ≥90%)` | MANDATORY |
| EARS-Ready Score | `[PASS] NN% (Target: ≥90%)` | MANDATORY |
| Revision History | Table | MANDATORY (for Review/Approved) |
| Priority | High / Medium / Low | OPTIONAL |
| Target Release | Version/Quarter | OPTIONAL |
| Estimated Effort | Story Points / PM | OPTIONAL |

---

### Phase 4: Element Code Validation (`element_codes.py`)

**Format:** `PRD.NN.TT.SS` (4-segment dot notation)
- NN: Document number (01-99)
- TT: Type code (01-09, 11, 22, 23, 24)
- SS: Sequence number (01-99)

**Context Detection (port from BRD):**
```python
def _is_definition_context(line: str, match: re.Match) -> bool:
    """Detect element ID definitions (headings, bold, bullets)."""

def _is_reference_context(line: str, match: re.Match) -> bool:
    """Detect references (backticks, tables, traceability)."""
```

**Upstream Traceability Format:**
- Required: `@brd: BRD.NN.TT.SS` (4-segment with dots)
- Invalid: `@brd: BRD-NN` (document-level only, dash notation)

---

### Phase 5: Corpus-Level Quality Gates (`corpus_gate.py`)

19 checks mapped from legacy `validate_prd_quality_score.sh`:

| Code | Check | Tier | Description |
|------|-------|------|-------------|
| CORPUS-01 | Placeholder text | 1 | No `(future)`, `(TBD)`, `[TODO]`, `XXX`, `FIXME`, `HACK`, `WIP`, `???`, merge conflicts |
| CORPUS-02 | Forbidden downstream refs | 1 | No specific ADR-NN, SYS-NN, REQ-NN, SPEC-NN, TASKS-NN |
| CORPUS-03 | Internal count consistency | 2 | Stated counts match actual items |
| CORPUS-04 | Index bidirectionality | 1 | Index synced with files, no stale/dead refs |
| CORPUS-05 | Inter-PRD cross-linking | - | DEPRECATED (document names sufficient) |
| CORPUS-06 | Visualization coverage | 1 | Required: `@diagram: c4-l2`, `@diagram: dfd-l1`, `@diagram: sequence-*` with alt/else |
| CORPUS-07 | Glossary consistency | 2 | Consistent terminology |
| CORPUS-08 | Element ID uniqueness | 1 | Cross-file duplicate detection |
| CORPUS-09 | Cost estimate format | 2 | Ranges preferred ($100-$150, not $125) |
| CORPUS-10 | File size compliance | 1/2 | WARNING @ 800 lines, ERROR @ 1,200 lines |
| CORPUS-11 | BRD traceability | 1 | All PRDs have `@brd:` in 4-segment format |
| CORPUS-12 | User story coverage | 2 | BRD objectives → PRD user stories |
| CORPUS-13 | Template structure | 1 | All 21 sections required |
| CORPUS-14 | SYS-Ready score | 1 | ≥90% (Standard) or ≥85% (MVP) |
| CORPUS-15 | EARS-Ready score | 1 | ≥90% (Standard) or ≥85% (MVP) |
| CORPUS-16 | Glossary path | 2 | Standardized location |
| CORPUS-17 | Token count | 1/2 | WARNING @ 40K, ERROR @ 80K |
| CORPUS-18 | YAML frontmatter | 2 | Required fields present |
| CORPUS-19 | Date format consistency | 2 | Accept `YYYY-MM-DD` and `YYYY-MM-DDTHH:MM:SS` |

---

### Phase 6: File-Level Quality Gates (`quality_gate.py`)

| Code | Check | Tier | Description |
|------|-------|------|-------------|
| PRD-E001 | H1 format | 1 | Must match `# PRD-NN: Title` |
| PRD-E002 | Document Control | 1 | 11 required fields |
| PRD-E003 | Missing tag `prd` | 1 | Required tag |
| PRD-E004 | Missing tag `layer-2-artifact` | 1 | Required tag |
| PRD-E005 | BRD traceability format | 1 | 4-segment `@brd: BRD.NN.TT.SS` |
| PRD-E010 | Section 10 empty | 1 | Customer-Facing Content MANDATORY |
| PRD-E011 | Section 8 layer note | 1 | Layer separation scope note required |
| PRD-E023 | Missing `@diagram: c4-l2` | 1 | Container-level diagram |
| PRD-E024 | Missing `@diagram: dfd-l1` | 1 | Data flow level 1 |
| PRD-E025 | Missing sequence diagram | 1 | `@diagram: sequence-*` required |
| PRD-E026 | Sequence missing alt/else | 1 | Exception path required |
| PRD-W001 | Feature ID format | 2 | 3-digit NNN format |
| PRD-W002 | File name format | 2 | PRD-NN_slug.md |
| PRD-W005 | Legacy status field | 2 | Migrate `development_status` to `status` |
| PRD-W011 | Diagram intent header | 2 | Missing required fields |
| PRD-W020 | EARS Appendix structure | 2 | Section 20 completeness |
| PRD-W021 | Architecture Decision table | 2 | Section 18 elaboration |
| PRD-I001 | @depends tags | INFO | Cross-PRD dependencies |
| PRD-I002 | @discoverability tags | INFO | AI ranking hints |

---

### Phase 7: Scoring Module (`scoring.py`) - AUTHORITATIVE

This module is the **single source of truth** for PRD readiness scoring. It is used by:
1. `ucx validate prd` - Calculate scores during validation (this plan)
2. `ucx create prd` - Calculate scores after creation (PLAN-009 Phase 4, via import)
3. `ucx score prd` - Standalone scoring command (this plan)

**File:** `/opt/data/docs_flow_framework/UCX/ucx/validators/prd/scoring.py`

```python
"""
PRD Readiness Scoring Module.

This module calculates SYS-Ready and EARS-Ready scores based on
PRD content analysis. It is the authoritative source for scoring
logic, used by both validation and creation phases.

Usage:
    from ucx.validators.prd.scoring import PRDScorer, ReadinessScores

    scorer = PRDScorer()
    scores = scorer.calculate(content, frontmatter)
    print(f"SYS-Ready: {scores.sys_ready}%")
    print(f"EARS-Ready: {scores.ears_ready}%")
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ScoreBreakdown:
    """Detailed score breakdown by criterion."""
    criterion: str
    weight: float
    earned: float
    max_points: float
    details: str = ""


@dataclass
class ReadinessScores:
    """PRD readiness scores result."""
    sys_ready: float                           # 0-100
    ears_ready: float                          # 0-100
    sys_breakdown: list[ScoreBreakdown]        # Per-criterion details
    ears_breakdown: list[ScoreBreakdown]       # Per-criterion details
    status: str                                # Draft/Review/Approved
    profile: str                               # mvp/standard
    threshold: int                             # 85 or 90

    @property
    def sys_passed(self) -> bool:
        return self.sys_ready >= self.threshold

    @property
    def ears_passed(self) -> bool:
        return self.ears_ready >= self.threshold

    @property
    def both_passed(self) -> bool:
        return self.sys_passed and self.ears_passed


class PRDScorer:
    """
    Calculate SYS-Ready and EARS-Ready scores from PRD content.

    Scoring is content-based, not finding-based. It checks for
    presence and quality of specific content elements.
    """

    # SYS-Ready criteria (40% + 30% + 20% + 10% = 100%)
    SYS_READY_WEIGHTS = {
        "product_completeness": 0.40,
        "technical_readiness": 0.30,
        "business_alignment": 0.20,
        "traceability": 0.10,
    }

    # EARS-Ready criteria (25% + 25% + 25% + 15% + 10% = 100%)
    # Based on PRD template Section 20.5
    EARS_READY_WEIGHTS = {
        "timing_profiles": 0.25,
        "boundary_values": 0.25,
        "state_machine": 0.25,
        "fallback_paths": 0.15,
        "threshold_registry": 0.10,
    }

    def __init__(self, profile: str = "standard"):
        """
        Initialize scorer.

        Args:
            profile: Template profile ("mvp" or "standard")
        """
        self.profile = profile
        self.threshold = 85 if profile == "mvp" else 90

    def calculate(
        self,
        content: str,
        frontmatter: Optional[dict] = None,
    ) -> ReadinessScores:
        """
        Calculate both readiness scores from PRD content.

        Args:
            content: Full PRD document content
            frontmatter: Parsed YAML frontmatter (optional)

        Returns:
            ReadinessScores with both scores and breakdowns
        """
        sys_score, sys_breakdown = self._calculate_sys_ready(content, frontmatter)
        ears_score, ears_breakdown = self._calculate_ears_ready(content, frontmatter)

        # Determine status based on scores
        if sys_score >= 90 and ears_score >= 90:
            status = "Approved"
        elif sys_score >= 70 or ears_score >= 70:
            status = "Review"
        else:
            status = "Draft"

        return ReadinessScores(
            sys_ready=round(sys_score, 1),
            ears_ready=round(ears_score, 1),
            sys_breakdown=sys_breakdown,
            ears_breakdown=ears_breakdown,
            status=status,
            profile=self.profile,
            threshold=self.threshold,
        )

    def _calculate_sys_ready(
        self,
        content: str,
        frontmatter: Optional[dict],
    ) -> tuple[float, list[ScoreBreakdown]]:
        """
        Calculate SYS-Ready score.

        Components:
        - Product Completeness (40%): 21 sections, KPIs, stakeholders
        - Technical Readiness (30%): Boundaries, quality attrs, ADR table
        - Business Alignment (20%): ROI, competitive, metrics, risk
        - Traceability (10%): Upstream BRD, downstream links
        """
        breakdown = []
        total = 0.0

        # Product Completeness (40%)
        pc_score = 0.0
        sections_present = len(re.findall(r"^## \d+\.", content, re.MULTILINE))
        pc_score += min(sections_present / 21, 1.0) * 0.10  # 21 sections
        pc_score += 0.10 if re.search(r"KPI|metric|measure", content, re.I) else 0
        pc_score += 0.10 if re.search(r"## 15\.|stakeholder", content, re.I) else 0
        pc_score += 0.10 if re.search(r"## 4\.|persona|audience", content, re.I) else 0
        breakdown.append(ScoreBreakdown(
            criterion="Product Completeness",
            weight=0.40,
            earned=pc_score,
            max_points=0.40,
            details=f"{sections_present}/21 sections"
        ))
        total += pc_score

        # Technical Readiness (30%)
        tr_score = 0.0
        tr_score += 0.10 if re.search(r"boundary|integration|interface", content, re.I) else 0
        tr_score += 0.10 if re.search(r"quality|NFR|non-functional", content, re.I) else 0
        tr_score += 0.10 if re.search(r"architecture.*decision|ADR.*topic", content, re.I) else 0
        breakdown.append(ScoreBreakdown(
            criterion="Technical Readiness",
            weight=0.30,
            earned=tr_score,
            max_points=0.30,
        ))
        total += tr_score

        # Business Alignment (20%)
        ba_score = 0.0
        ba_score += 0.05 if re.search(r"ROI|return on|business case", content, re.I) else 0
        ba_score += 0.05 if re.search(r"competitive|market|analysis", content, re.I) else 0
        ba_score += 0.05 if re.search(r"success.*metric|KPI", content, re.I) else 0
        ba_score += 0.05 if re.search(r"risk.*mitigation|## 13\.", content, re.I) else 0
        breakdown.append(ScoreBreakdown(
            criterion="Business Alignment",
            weight=0.20,
            earned=ba_score,
            max_points=0.20,
        ))
        total += ba_score

        # Traceability (10%)
        trace_score = 0.0
        trace_score += 0.05 if re.search(r"@brd:\s*BRD\.\d+\.\d+\.\d+", content) else 0
        trace_score += 0.05 if re.search(r"downstream|EARS|SYS", content, re.I) else 0
        breakdown.append(ScoreBreakdown(
            criterion="Traceability",
            weight=0.10,
            earned=trace_score,
            max_points=0.10,
        ))
        total += trace_score

        return total * 100, breakdown

    def _calculate_ears_ready(
        self,
        content: str,
        frontmatter: Optional[dict],
    ) -> tuple[float, list[ScoreBreakdown]]:
        """
        Calculate EARS-Ready score.

        Components (from PRD template Section 20.5):
        - Timing Profiles (25%): p50/p95/p99 for operations
        - Boundary Values (25%): Explicit operators (≥, >, <, ≤)
        - State Machine (25%): Complete with error transitions
        - Fallback Paths (15%): External dependency failures
        - Threshold Registry (10%): Centralized values referenced
        """
        breakdown = []
        total = 0.0

        # Timing Profiles (25%)
        tp_score = 0.0
        if re.search(r"p50|p95|p99|latency|timing.*profile", content, re.I):
            tp_score = 0.25
        elif re.search(r"response.*time|timeout|ms\b|millisecond", content, re.I):
            tp_score = 0.15  # Partial credit
        breakdown.append(ScoreBreakdown(
            criterion="Timing Profiles",
            weight=0.25,
            earned=tp_score,
            max_points=0.25,
            details="p50/p95/p99 specifications"
        ))
        total += tp_score

        # Boundary Values (25%)
        bv_score = 0.0
        if re.search(r"[≥≤><]\s*\d+|boundary.*value|\[\d+,\s*\d+\]", content):
            bv_score = 0.25
        elif re.search(r"min|max|threshold|limit|range", content, re.I):
            bv_score = 0.15  # Partial credit
        breakdown.append(ScoreBreakdown(
            criterion="Boundary Values",
            weight=0.25,
            earned=bv_score,
            max_points=0.25,
            details="Explicit operators (≥, >, <, ≤)"
        ))
        total += bv_score

        # State Machine (25%)
        sm_score = 0.0
        if re.search(r"state.*machine|state.*transition|entry.*exit", content, re.I):
            sm_score = 0.25
        elif re.search(r"state|status|workflow|flow", content, re.I):
            sm_score = 0.10  # Partial credit
        breakdown.append(ScoreBreakdown(
            criterion="State Machine",
            weight=0.25,
            earned=sm_score,
            max_points=0.25,
            details="Error transitions documented"
        ))
        total += sm_score

        # Fallback Paths (15%)
        fp_score = 0.0
        if re.search(r"fallback|failure.*mode|degraded|circuit.*breaker", content, re.I):
            fp_score = 0.15
        elif re.search(r"error.*handling|exception|recovery", content, re.I):
            fp_score = 0.10  # Partial credit
        breakdown.append(ScoreBreakdown(
            criterion="Fallback Paths",
            weight=0.15,
            earned=fp_score,
            max_points=0.15,
            details="External dependency failures"
        ))
        total += fp_score

        # Threshold Registry (10%)
        tr_score = 0.0
        if re.search(r"@threshold:|threshold.*registry|centralized.*value", content, re.I):
            tr_score = 0.10
        elif re.search(r"threshold|config|parameter", content, re.I):
            tr_score = 0.05  # Partial credit
        breakdown.append(ScoreBreakdown(
            criterion="Threshold Registry",
            weight=0.10,
            earned=tr_score,
            max_points=0.10,
            details="Centralized values referenced"
        ))
        total += tr_score

        return total * 100, breakdown

    def update_document_control(
        self,
        file_path: Path,
        scores: ReadinessScores,
    ) -> bool:
        """
        Update Document Control section with calculated scores.

        Args:
            file_path: Path to PRD file
            scores: Calculated readiness scores

        Returns:
            True if updated successfully
        """
        content = file_path.read_text(encoding="utf-8")

        # Format score strings
        sys_label = "[PASS]" if scores.sys_passed else "[DRAFT]"
        ears_label = "[PASS]" if scores.ears_passed else "[DRAFT]"
        sys_str = f"{sys_label} {scores.sys_ready}% (Target: ≥{scores.threshold}%)"
        ears_str = f"{ears_label} {scores.ears_ready}% (Target: ≥{scores.threshold}%)"

        # Update SYS-Ready Score
        content = re.sub(
            r"\|\s*SYS-Ready Score\s*\|[^|]+\|",
            f"| SYS-Ready Score | {sys_str} |",
            content
        )

        # Update EARS-Ready Score
        content = re.sub(
            r"\|\s*EARS-Ready Score\s*\|[^|]+\|",
            f"| EARS-Ready Score | {ears_str} |",
            content
        )

        # Write back
        file_path.write_text(content, encoding="utf-8")
        return True

    def format_score_summary(self, scores: ReadinessScores) -> str:
        """Format scores for console output."""
        sys_icon = "✓" if scores.sys_passed else "✗"
        ears_icon = "✓" if scores.ears_passed else "✗"

        return f"""
PRD Readiness Scores ({scores.profile} profile, threshold: {scores.threshold}%)
────────────────────────────────────────────────────────────
SYS-Ready:  {sys_icon} {scores.sys_ready}%
EARS-Ready: {ears_icon} {scores.ears_ready}%
Status:     {scores.status}
────────────────────────────────────────────────────────────
"""


# Export for use by other modules
__all__ = ["PRDScorer", "ReadinessScores", "ScoreBreakdown"]
```

**Estimated Lines:** ~350

---

### Phase 8: Auto-Fixer (`fixer.py`, `duplicate_fixer.py`)

**Fixable Error Codes:**

| Code | Fix Type | Description |
|------|----------|-------------|
| PRD-E002 | Auto | Add missing custom_fields |
| PRD-E003 | Auto | Add missing `prd` tag |
| PRD-E004 | Auto | Add missing `layer-2-artifact` tag |
| PRD-E005 | Auto | Convert `@brd: BRD-NN` to 4-segment |
| PRD-W002 | Auto | Rename file to correct format |
| PRD-W005 | Auto | Migrate `development_status` to `status` |
| CORPUS-01 | LLM | Remove placeholders (semantic) |
| CORPUS-02 | Auto | Remove forbidden downstream refs |
| CORPUS-08 | Auto | Renumber duplicate elements |
| CORPUS-19 | Auto | Fix date format to ISO |
| **SCORE-UPDATE** | Auto | Update Document Control with calculated scores |

**UCX-ACTION Output Format:**
```markdown
<!-- UCX-ACTION
TYPE: INTERNAL | HANDOFF
TARGET: fixer | llm | human
PRIORITY: P1 | P2 | P3
CONTEXT: {issue description}
REQUIREMENT: {what needs to happen}
-->
```

**Protected Changes Tracking:**
```python
@dataclass
class FixerContext:
    fixer_applied: list[str]      # Codes fixed by script
    llm_completion: list[str]     # Codes needing LLM
    protected_ranges: list[tuple[int, int]]  # Line ranges
```

---

### Phase 9: AI Review Prompt Update (`UCR_PROMPT_PRD.md`)

The AI review prompt must be updated to align with the new 21-section structure, quality gates, and dual scoring.

**File:** `/opt/data/docs_flow_framework/UCX/ucx/prompts/templates/ucr/UCR_PROMPT_PRD.md`

**Current Issues:**

| Issue | Current State | Required State |
|-------|---------------|----------------|
| Section references | Section 5, Section 18 | 21-section MVP structure |
| Scoring | `ears_ready_score` only | Dual: `sys_ready_score` + `ears_ready_score` |
| Quality gates | None referenced | GATE-E001 through GATE-E019 |
| Element codes | Generic pattern | 13 type codes with section mappings |
| Section 10 | Not mentioned | BLOCKING requirement |
| Layer separation | Not enforced | Section 8 layer note required |

**Updates Required:**

#### 1. Document Control Section Update

```markdown
## 0. Document Control

| Item | Details |
|------|---------|
| **Source Document** | [PRD-XX] (Version X.X) |
| **Review ID** | [REVIEW_ID] |
| **Review Date** | [YYYY-MM-DDTHH:MM:SS] |
| **Review Method** | UCR (Unified Context Review) |
| **Personas Applied** | 10 |
| **Reviewer** | UCX Framework v1.21.x |
| **Status** | [Draft / Review / Approved] |
| **SYS-Ready Score** | [SCORE]% (Target: ≥90%) |
| **EARS-Ready Score** | [SCORE]% (Target: ≥90%) |
| **Template Profile** | [MVP / Standard] |
```

#### 2. Section Reference Updates

Replace outdated section references with 21-section structure:

```markdown
**Sections to Cross-Reference**:
| Section | Name | Validation Focus |
|---------|------|------------------|
| 1 | Document Control | Scores populated |
| 4 | Target Audience & User Personas | Persona definitions |
| 5 | High-Level Features / Epics | Feature hierarchy |
| 8 | User Stories | Layer separation note present |
| 9 | Acceptance Criteria | Testable conditions |
| 10 | Customer-Facing Content | **BLOCKING** - substantive content required |
| 13 | Quality Attributes Summary | NFR coverage |
| 14 | Constraints | Technical/business limits |
| 17 | Upstream Traceability | BRD references |
| 18 | Downstream Artifacts | SYS/EARS/BDD references |
```

#### 3. Quality Gate Integration

Add quality gate references to persona prompts:

```markdown
### Pre-Review Validation Check

Before AI review begins, verify these quality gates passed:

| Gate | Check | Blocking |
|------|-------|----------|
| GATE-E001 | Placeholder detection | Yes |
| GATE-E002 | Element ID format (PRD.NN.TT.SS) | Yes |
| GATE-E008 | Section 10 substantive content | Yes |
| GATE-E015 | SYS-Ready ≥90% | Yes |
| GATE-E016 | EARS-Ready ≥90% | Yes |

If any blocking gate fails, flag in Document Control before proceeding.
```

#### 4. Persona Focus Updates

Update each persona to reference correct sections:

```markdown
### 1. THE ARCHITECT (Technical Feasibility)

Focus on:
- Section 13 (Quality Attributes Summary) - Are NFRs QUANTIFIED?
- Section 14 (Constraints) - Are limits EXPLICIT?
- Section 18 (Downstream Artifacts) - Are SYS references valid?
- Section 20 (Diagram Index) - Are required diagrams present?
  - c4-l2 container diagram
  - dfd-l1 data flow diagram
  - sequence-* interaction diagrams

### 8. THE PRODUCT OWNER (Feature Scope & Value)

Focus on:
- Section 5 (High-Level Features) - Feature hierarchy complete?
- Section 8 (User Stories) - Layer separation note present?
- Section 10 (Customer-Facing Content) - **BLOCKING** content exists?
- Section 11 (Success Metrics & KPIs) - Measurable targets?
```

#### 5. Dual Scoring Output

Update output template to include both scores:

```markdown
### Review Summary

| Metric | Value |
|--------|-------|
| **Recommendation** | [✅ PROCEED / ⚠️ REMEDIATION REQUIRED / 🚨 FUNDAMENTAL REDESIGN] |
| **SYS-Ready Score** | [SCORE]% ([PASS/DRAFT]) |
| **EARS-Ready Score** | [SCORE]% ([PASS/DRAFT]) |
| **P0 Critical Findings** | [COUNT] |
| **P1 High Findings** | [COUNT] |
| **P2 Medium Findings** | [COUNT] |

**Readiness Assessment:**
- SYS-Ready: [Product Completeness 40% + Technical Readiness 30% + Business Alignment 20% + Traceability 10%]
- EARS-Ready: [Timing Profiles 25% + Boundary Values 25% + State Machine 25% + Fallback Paths 15% + Threshold Registry 10%]
```

#### 6. Layer Separation Enforcement

Add explicit layer separation check:

```markdown
### CRITICAL: Layer Separation Validation

Before scoring, verify Section 8 (User Stories) includes:

> **Layer Separation Note**: This section contains high-level user stories only.
> Detailed behaviors belong in downstream artifacts:
> - Timing/boundary values → EARS (Layer 3)
> - Given-When-Then scenarios → BDD (Layer 4)
> - State machine details → EARS (Layer 3)

**Flag as P0** if:
- Given-When-Then patterns found in PRD
- Timing profiles embedded in user stories
- State machine transitions specified
```

#### 7. Forward Reference Blocking

Add forward reference detection:

```markdown
### Forward Reference Check

PRD MUST NOT reference Layer 5+ artifacts. Flag as P0:
- @adr: ADR-NN references
- @sys: SYS-NN references
- @req: REQ-NN references
- @spec: SPEC-NN references
- @tasks: TASKS-NN references

PRD MAY reference:
- @brd: BRD-NN (upstream)
- @ears: EARS-NN (downstream, planning)
- @bdd: BDD-NN (downstream, planning)
```

**Estimated Changes:** ~200 lines modified in UCR_PROMPT_PRD.md

---

### Phase 10: Integration

**Registry Update (`validators/registry.py`):**
```python
@register_validator(DocType.PRD)
class UnifiedPRDValidator:
    ...
```

**CLI Commands (`cli.py`):**
```bash
# Validation with scoring
ucx validate prd <path> [--tier1-only] [--strict] [--no-fix] [--update-scores]

# Review
ucx review prd <path>

# Remediation
ucx remediate prd <path>

# Standalone scoring (NEW)
ucx score prd <path> [--update] [--profile mvp|standard]
```

**Standalone Score Command:**
```python
@app.command()
def score(
    doc_type: str,
    path: str,
    update: bool = typer.Option(False, "--update", help="Update Document Control"),
    profile: str = typer.Option("standard", "--profile", help="Template profile"),
):
    """Calculate readiness scores for a PRD document."""
    from ucx.validators.prd.scoring import PRDScorer

    content = Path(path).read_text()
    scorer = PRDScorer(profile=profile)
    scores = scorer.calculate(content)

    console.print(scorer.format_score_summary(scores))

    if update:
        scorer.update_document_control(Path(path), scores)
        console.print(f"[green]Updated Document Control in {path}[/green]")
```

**Pre-commit Hook Update (`.pre-commit-config.yaml`):**

Update PRD hooks to match BRD pattern (script-based validation + AI review):

```yaml
# =========================================================================
# PRD - Product Requirements Document (L2) - UCX IMPLEMENTED
# =========================================================================

# Tier 1 Validation (Blocking - runs on every commit)
- id: ucx-prd-validate
  name: UCX PRD Validation (Tier 1)
  entry: bash -c 'source /opt/data/docs_flow_framework/.venv/bin/activate && ucx validate prd docs/02_PRD --tier1-only'
  language: system
  files: ^docs/02_PRD/.*\.md$
  exclude: ^docs/02_PRD/PRD-00_.*
  pass_filenames: false
  stages: [pre-commit]  # CHANGED from [manual] to [pre-commit]

# Full Validation (Manual - Tier 1 + Tier 2)
- id: ucx-prd-validate-full
  name: UCX PRD Full Validation (Tier 1 + Tier 2)
  entry: bash -c 'source /opt/data/docs_flow_framework/.venv/bin/activate && ucx validate prd docs/02_PRD'
  language: system
  pass_filenames: false
  stages: [manual]

# AI Review (Manual - Multi-persona review)
- id: ucx-prd-review
  name: UCX PRD AI Review
  entry: bash -c 'source /opt/data/docs_flow_framework/.venv/bin/activate && ucx review prd docs/02_PRD'
  language: system
  pass_filenames: false
  stages: [manual]

# Scoring Only (Manual - Calculate and update scores)
- id: ucx-prd-score
  name: UCX PRD Scoring
  entry: bash -c 'source /opt/data/docs_flow_framework/.venv/bin/activate && ucx score prd docs/02_PRD --update'
  language: system
  pass_filenames: false
  stages: [manual]
```

**Key Changes from Legacy:**

| Aspect | Legacy | UCX |
|--------|--------|-----|
| Hook ID | `ucx-prd-validate` | Same (updated entry) |
| Stage | `manual` | `pre-commit` (blocking) |
| Entry | `bash scripts/ucx-validate.sh prd` | `ucx validate prd` |
| Full validation | Not available | `ucx-prd-validate-full` |
| AI review | `prd-claude-skill-audit` | `ucx-prd-review` |
| Scoring | Manual script | `ucx-prd-score` |

**Deprecation:**

```yaml
# DEPRECATED - Remove after full UCX PRD validator migration
- id: prd-core-wrapper
  name: "[DEPRECATED] PRD Core Wrapper - Use ucx-prd-validate"
  stages: [manual]

- id: prd-quality-gate
  name: "[DEPRECATED] PRD Quality Gate - Use ucx-prd-validate-full"
  stages: [manual]
```

**Version Bump (`version.py`):**
```python
__version__ = "1.20.0"
# v1.21.3 baseline - PRD unified validator and create/validate alignment
# - 10 Python modules for PRD validation
# - 19 corpus-level + 19 file-level quality gates
# - Dual readiness scoring (SYS-Ready, EARS-Ready)
# - Standalone scoring command (ucx score prd)
# - Forward reference blocking for Layer 5+ artifacts
# - Section 10 mandatory enforcement
```

---

### Phase 11: Testing

**Unit Tests (`tests/validators/prd/`):**
```
tests/validators/prd/
├── test_schema.py
├── test_structure.py
├── test_metadata.py
├── test_element_codes.py
├── test_quality_gate.py
├── test_corpus_gate.py
├── test_scoring.py          # Comprehensive scoring tests
├── test_fixer.py
└── test_duplicate_fixer.py
```

**Scoring-Specific Tests (`test_scoring.py`):**
```python
class TestPRDScorer:
    """Test PRD scoring module."""

    def test_sys_ready_full_score(self):
        """PRD with all content should score 100%."""

    def test_sys_ready_partial_score(self):
        """PRD with missing sections should score proportionally."""

    def test_ears_ready_timing_profiles(self):
        """p50/p95/p99 presence should contribute 25%."""

    def test_ears_ready_boundary_values(self):
        """Explicit operators should contribute 25%."""

    def test_threshold_mvp_vs_standard(self):
        """MVP threshold is 85%, standard is 90%."""

    def test_update_document_control(self):
        """Scores should be written to Document Control."""

    def test_score_status_mapping(self):
        """≥90% = Approved, 70-89% = Review, <70% = Draft."""
```

**Integration Tests:**
```bash
# Validate PRD documents in b-local-docs
ucx validate prd /opt/data/b-local/b-local-docs/docs/02_PRD/ --tier1-only

# Score existing PRD
ucx score prd /opt/data/b-local/b-local-docs/docs/02_PRD/PRD-01/ --profile mvp

# Compare with legacy scripts
python3 ai_dev_ssd_flow/02_PRD/scripts/validate_prd.py docs/02_PRD/PRD-01/
```

**Validation Criteria:**
1. All 19 corpus-level gates execute
2. All 19 file-level gates execute
3. Dual scoring matches manual calculation
4. Auto-fixer produces correct UCX-ACTION blocks
5. Legacy script parity for overlapping checks
6. Scoring module is importable by creation phase

---

## Output Reports

### Current Report and Session Artifact Naming

Current UCX runtime behavior uses these artifact locations/names:

| Phase | Artifact | Current Path / Naming |
|-------|----------|-----------------------|
| **UCC (Create)** | Prompt history | `docs/02_PRD/<slug>/.ucx_create_session/prompt_prd_<timestamp>.txt` |
| **UCR (Validate)** | Validation report | `.precommit_validation_report.md` |
| **UCR (Review)** | Review report | `{DOC_ID}.UCX_review_report_v{NNN}.md` |
| **UCRem (Remediate)** | Remediation report | `{DOC_ID}.UCX_remediation_report_v{NNN}.md` |

### Validation Report Structure (`.precommit_validation_report.md`)

Generated after `ucx validate prd` completes:

```markdown
---
title: "UCX Validate Report: PRD"
tags:
  - ucx-validate
  - prd-validate
  - layer-2-artifact
custom_fields:
  document_type: ucx-validate-report
  source_artifact_type: PRD
  validate_id: "UCX-PRD-01-validate-v001"
  layer: 2
  validation_mode: tier1-only | full
  total_errors: 0
  total_warnings: 5
  sys_ready_score: 85.2
  ears_ready_score: 88.5
  last_updated: "2026-03-19T15:00:00"
---

# UCX Validate Report: PRD-01

## 0. Document Control

| Item | Details |
|------|---------|
| **Validated Document** | PRD-01 |
| **Validate ID** | UCX-PRD-01-validate-v001 |
| **Validate Date** | 2026-03-19T15:00:00 |
| **Validation Mode** | Tier 1 Only |
| **Status** | ✅ PASS |

## 1. Readiness Scores

| Score | Value | Target | Status |
|-------|-------|--------|--------|
| **SYS-Ready** | 85.2% | ≥85% | ✅ PASS |
| **EARS-Ready** | 88.5% | ≥85% | ✅ PASS |

## 2. Quality Gate Results

### Tier 1 (Blocking)

| Gate | Check | Status |
|------|-------|--------|
| GATE-E001 | Placeholder detection | ✅ PASS |
| GATE-E002 | Element ID format | ✅ PASS |
| GATE-E008 | Section 10 content | ✅ PASS |
| GATE-E015 | SYS-Ready ≥85% | ✅ PASS |
| GATE-E016 | EARS-Ready ≥85% | ✅ PASS |

### Tier 2 (Advisory)

| Gate | Check | Status | Details |
|------|-------|--------|---------|
| GATE-W003 | Upstream traceability | ⚠️ WARN | 3 BRD refs missing |
| GATE-W007 | Diagram coverage | ⚠️ WARN | c4-l2 missing |

## 3. Errors (0)

*No blocking errors found.*

## 4. Warnings (5)

| Code | File | Message |
|------|------|---------|
| GATE-W003 | PRD-01.5_features.md | BRD.01.02.03 not traced |
| GATE-W003 | PRD-01.5_features.md | BRD.01.02.04 not traced |
| GATE-W003 | PRD-01.5_features.md | BRD.01.02.05 not traced |
| GATE-W007 | PRD-01.20_diagrams.md | c4-l2 diagram not found |
| GATE-W007 | PRD-01.20_diagrams.md | dfd-l1 diagram not found |

## 5. Next Steps

- [ ] Address warnings before review
- [ ] Run `ucx review prd PRD-01/` for AI review
```

### Review Report Structure (`UCR_review_report`)

Generated after `ucx review prd` completes:

```markdown
---
title: "UCR Review Report: PRD"
tags:
  - ucx-review
  - prd-review
  - layer-2-artifact
  - quality-assurance
custom_fields:
  document_type: ucx-review-report
  source_artifact_type: PRD
    review_id: "UCR-PRD-01-v001"
  layer: 2
  review_method: unified-context-review
  scoring_method: category-weighted-v1.12.0
  personas_applied: 10
  sys_ready_score: 85.2
  ears_ready_score: 88.5
  weighted_score: 84.0
  p0_findings: 5
  p1_findings: 12
  p2_findings: 8
  last_updated: "2026-03-19T16:00:00"
---

# UCR Review Report: PRD-01

## 0. Document Control

| Item | Details |
|------|---------|
| **Source Document** | PRD-01 |
| **Review ID** | UCR-PRD-01-v001 |
| **Review Date** | 2026-03-19T16:00:00 |
| **Review Method** | UCR (Unified Context Review) |
| **Personas Applied** | 10 |
| **Reviewer** | UCX Framework v1.21.x |
| **Status** | Draft |

## 1. Readiness Scores

| Score | Value | Target | Status |
|-------|-------|--------|--------|
| **SYS-Ready** | 85.2% | ≥90% | ⚠️ REVIEW |
| **EARS-Ready** | 88.5% | ≥90% | ⚠️ REVIEW |
| **Review Score** | 84.0/100 | — | ⚠️ WARN |

## 2. Category Breakdown

| Category | P0 | P1 | P2 | Raw | Capped | Weighted |
|----------|---:|---:|---:|----:|-------:|--------:|
| functional | 2 | 3 | 1 | -29 | -25 | -6.25 |
| quality | 1 | 2 | 2 | -19 | -15 | -2.25 |
| compliance | 1 | 3 | 1 | -20 | -20 | -4.00 |
| constraints | 0 | 1 | 2 | -5 | -5 | -0.50 |
| integration | 1 | 2 | 1 | -17 | -10 | -1.00 |
| acceptance | 0 | 1 | 1 | -4 | -4 | -0.40 |
| **Total** | **5** | **12** | **8** | **-94** | **-79** | **-16.00** |

## 3. Findings Summary

### P0 Critical (5)
- [ARCH-P0-001] Missing state machine for transaction lifecycle
- [AUD-P0-001] KYC verification flow incomplete
- ...

### P1 High (12)
- [TL-P1-001] Performance targets not specified
- ...

## 4. Per-Persona Analysis
[Detailed findings from each persona...]

## 5. Recommended Remediations
[UCX-ACTION blocks for auto-fixer...]
```

### Remediation Report Structure (`UCX_remediation_report`)

Generated after `ucx remediate prd` completes:

```markdown
---
title: "UCX Remediation Report: PRD-01"
tags:
  - ucx-remediate
  - prd-remediate
  - layer-2-artifact
custom_fields:
  document_type: ucx-remediate-report
  source_artifact_type: PRD
    report_type: remediation
    source_artifact_id: PRD-01
    report_version: v001
  layer: 2
    source_review: "PRD-01.UCX_review_report_v001.md"
  p0_resolved: 5
  p1_resolved: 8
  p1_deferred: 4
  estimated_score_after: 92
  last_updated: "2026-03-19T17:00:00"
---

# UCX Remediation Report: PRD-01

## 0. Document Control

| Item | Details |
|------|---------|
| **Remediated Document** | PRD-01 |
| **Report ID** | PRD-01.UCX_remediation_report_v001 |
| **Source Review** | PRD-01.UCX_review_report_v001.md |
| **Remediate Date** | 2026-03-19T17:00:00 |
| **Status** | Complete |

## 1. Remediation Summary

| Metric | Before | After |
|--------|--------|-------|
| **P0 Findings** | 5 | 0 |
| **P1 Findings** | 12 | 4 (deferred) |
| **SYS-Ready Score** | 85.2% | 92.0% |
| **EARS-Ready Score** | 88.5% | 94.0% |
| **Review Score** | 84.0 | 92.0 (estimated) |

## 2. Resolved Findings

### P0 Critical (5/5 resolved)
| Finding | Action | File Modified |
|---------|--------|---------------|
| ARCH-P0-001 | Added state machine | PRD-01.8_user_stories.md |
| AUD-P0-001 | Completed KYC flow | PRD-01.9_acceptance.md |
| ... | ... | ... |

### P1 High (8/12 resolved)
| Finding | Action | File Modified |
|---------|--------|---------------|
| TL-P1-001 | Added perf targets | PRD-01.13_quality_attrs.md |
| ... | ... | ... |

## 3. Deferred Findings

| Finding | Reason | Deferred To |
|---------|--------|-------------|
| TL-P1-005 | Requires ADR decision | ADR-03 |
| IL-P1-002 | Requires CTR definition | CTR-01 |
| ... | ... | ... |

## 4. Files Modified

| File | Changes |
|------|---------|
| PRD-01.8_user_stories.md | +45 lines (state machine) |
| PRD-01.9_acceptance.md | +28 lines (KYC criteria) |
| PRD-01.13_quality_attrs.md | +15 lines (perf targets) |

## 5. Next Steps

- [ ] Run `ucx validate prd PRD-01/` to verify fixes
- [ ] Create ADR-03 for deferred architectural decisions
- [ ] Create CTR-01 for deferred contract definitions
```

### Report Location

Current artifacts are saved in the document directory:

```
docs/02_PRD/PRD-01/
├── PRD-01.0_index.md
├── PRD-01.1_document_control.md
├── ...
├── .ucx_create_session/
│   └── prompt_prd_<timestamp>.txt        ← UCC prompt history
├── .precommit_validation_report.md       ← This plan (single-file overwrite)
├── PRD-01.UCX_review_report_v001.md      ← UCR review output
├── PRD-01.UCX_review_report_v002.md      ← Subsequent review runs
└── PRD-01.UCX_remediation_report_v001.md ← UCRem remediation output (canonical single report)
```

### Backward Compatibility

> **Note**: Validation remains single-file (`.precommit_validation_report.md`),
> while review/remediation use versioned UCX report families
> (`UCX_review_report_vNNN`, `UCX_remediation_report_vNNN`).
> Remediation uses one canonical report artifact per run.

---

## Critical Files Summary

### New Files (Create) - 10 files

| File | Purpose | Lines (est) |
|------|---------|-------------|
| `prd/__init__.py` | UnifiedPRDValidator | 350 |
| `prd/schema.py` | Constants, 13 type codes, 21 sections | 500 |
| `prd/structure.py` | Section validation, Section 10 blocking | 400 |
| `prd/metadata.py` | Frontmatter, 11 Doc Control fields | 300 |
| `prd/element_codes.py` | PRD.NN.TT.SS, context detection | 450 |
| `prd/quality_gate.py` | 19 file-level checks | 550 |
| `prd/corpus_gate.py` | 19 corpus-level checks | 650 |
| `prd/scoring.py` | **SYS-Ready + EARS-Ready (AUTHORITATIVE)** | 350 |
| `prd/fixer.py` | Auto-fixer with UCX-ACTION | 850 |
| `prd/duplicate_fixer.py` | Duplicate handling | 400 |

**Total:** ~4,800 lines

### Existing Files (Modify) - 6 files

| File | Changes | Lines (est) |
|------|---------|-------------|
| `common/error_codes.py` | Add 60+ PRD/CORPUS codes | +150 |
| `validators/__init__.py` | Add PRD imports | +5 |
| `validators/registry.py` | Register PRD validator | +3 |
| `cli.py` | Add PRD commands + `ucx score` | +80 |
| `version.py` | Bump to current release baseline | +5 |
| `prompts/templates/ucr/UCR_PROMPT_PRD.md` | 21-section alignment, dual scoring, quality gates | +200 |

**Total Modifications:** ~443 lines

### Reference Files (Read-only)

| File | Purpose |
|------|---------|
| `validators/brd/` | Architecture pattern |
| `ai_dev_ssd_flow/02_PRD/scripts/validate_prd.py` | Legacy validation logic |
| `ai_dev_ssd_flow/02_PRD/scripts/validate_prd_wrapper.sh` | Quality gate wrapper |
| `ai_dev_ssd_flow/02_PRD/PRD-MVP-TEMPLATE.md` | 21-section template |

---

## Success Criteria

### Script-Based Validation (Phases 0-8)
1. All 21 sections validated (both MVP and Standard)
2. Section 10 (Customer-Facing Content) blocking enforcement
3. Section 8 layer separation note validation
4. 13 element type codes validated
5. **Dual scoring (SYS-Ready + EARS-Ready) calculated correctly**
6. **Scoring module importable by PLAN-009 (creation)**
7. **`ucx score prd` standalone command works**
8. Forward references to ADR/SYS/REQ/SPEC/TASKS blocked
9. Auto-fixer produces UCX-ACTION blocks
10. Legacy pattern detection with migration warnings

### AI Review Prompt (Phase 9)
11. UCR_PROMPT_PRD.md references 21-section structure
12. Dual scoring (SYS-Ready + EARS-Ready) in output template
13. Quality gate references in persona prompts
14. Layer separation enforcement in persona checks
15. Forward reference detection documented

### Integration (Phases 10-11)
16. Pre-commit hook `ucx-prd-validate` runs at `pre-commit` stage (blocking)
17. Pre-commit hook `ucx-prd-validate-full` available at `manual` stage
18. Pre-commit hook `ucx-prd-review` triggers AI review
19. Legacy hooks deprecated with clear migration message

### Output Reports
20. Validation generates `.precommit_validation_report.md`
21. Review generates `{DOC_ID}.UCX_review_report_v{NNN}.md`
22. Remediation generates `{DOC_ID}.UCX_remediation_report_v{NNN}.md`
23. Reports include dual scores (SYS-Ready, EARS-Ready)
24. Version incrementing works correctly per report type
25. Validation rules and scripts remain compliant with UCC creation guardrails and prompt-session paths

### Testing
26. All tests pass

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Legacy PRD format incompatibility | High | Migration warnings, not blocking errors |
| Scoring calculation mismatch | Medium | Port exact formulas from legacy template |
| Forward ref blocking too strict | Medium | Allow generic references ("downstream ADR") |
| Section 10 false positives | Medium | Check for substantive content, not just presence |
| PRD-00_* incorrectly validated | Low | Explicit exemption pattern |
| Scoring import fails in creation | Medium | Graceful fallback to placeholders |

---

## Migration from Legacy Scripts

| Legacy Script | UCX Module | Notes |
|---------------|------------|-------|
| `validate_prd.py` | `quality_gate.py`, `structure.py` | Core validation |
| `validate_prd_wrapper.sh` | `corpus_gate.py` | 19 corpus checks |
| `validate_prd_quality_score.sh` | `scoring.py` | Dual scoring |
| Pre-commit hooks | CLI integration | Unified entry point |
| — | `UCR_PROMPT_PRD.md` | AI review prompt (21-section alignment) |

---

## Estimated Scope

- **New code:** ~4,800 lines across 10 modules
- **Modified code:** ~443 lines across 6 files (including UCR_PROMPT_PRD.md)
- **Test code:** ~1,800 lines across 9 test files
- **Documentation:** Changelog, README updates

---

*Plan Version: v10 (Create/validate alignment, PRD review ID lifecycle alignment, and canonical UCX remediation report consolidation)*
*Generated: 2026-03-20*
