---
doc_id: BRD-{NN}
section: 0
title: "{Document Title} - Index"
total_sections: {N}
original_size_kb: {SIZE}
split_date: {YYYY-MM-DD}
tags:
  - section-index
  - brd-section
  - layer-1-artifact
custom_fields:
  section_type: index
  artifact_type: BRD
  layer: 1
  folder_structure: nested
  architecture_approach: {approach-name}
  priority: {primary|fallback|shared}
  development_status: {active|reference|planned}
  split_type: section
  reading_order: sequential
  traceability_scope: inherited
  index_role: true
---

# BRD-{NN}.0: {Document Title} - Index

## Document Overview

| Field | Value |
|-------|-------|
| **Document ID** | BRD-{NN} |
| **Document Type** | Business Requirements Document |
| **Layer** | 1 - Business Requirements |
| **Title** | {Document Title} |
| **Total Sections** | {N} |
| **Original Size** | {SIZE} KB |
| **Split Date** | {YYYY-MM-DD} |
| **Status** | {status} |
| **PRD-Ready Score** | {score}/100 (Target: ≥90/100) |

### PRD-Ready Score Breakdown

| Category | Max Points | Score | Notes |
|----------|------------|-------|-------|
| Business-Level Language | 30 | {score} | No technical jargon, API specs, or code |
| Functional Requirements Structure | 25 | {score} | 4-subsection format with acceptance criteria |
| Traceability Completeness | 20 | {score} | All FRs linked to BOs, downstream refs |
| Quality Attributes Coverage | 15 | {score} | Performance, security, availability defined |
| Document Completeness | 10 | {score} | All mandatory sections present |
| **Total** | **100** | **{total}** | Target: ≥90/100 |

---

## Purpose

{Brief description of business requirements scope and why split into sections}

---

## Section Map

| Section | File | Title | Description |
|---------|------|-------|-------------|
| 0 | [BRD-{NN}.0_index.md](BRD-{NN}.0_index.md) | Index | Document overview, navigation, and traceability summary |
| 1 | [BRD-{NN}.1_{slug1}.md](BRD-{NN}.1_{slug1}.md) | {Title 1} | Purpose, scope, document control, and references |
| 2 | [BRD-{NN}.2_{slug2}.md](BRD-{NN}.2_{slug2}.md) | {Title 2} | Background, business goals, and strategic alignment |
| 3 | [BRD-{NN}.3_{slug3}.md](BRD-{NN}.3_{slug3}.md) | {Title 3} | {Meaningful description of section content} |

> **Note**: Descriptions must be meaningful (5-15 words). Avoid generic entries like "Section 1" or "Section 2". See `BRD_CREATION_RULES.md` section 8.5.3 for guidelines.

---

## Dependencies

### Upstream References
- None (BRD is Layer 1 - origin layer)

### Downstream References
- @ref: PRD-{NN} - Product Requirements derived from this BRD
- @ref: EARS-{NN} - Formal requirements derived from PRD

### Cross-Section Dependencies
- Section 2 depends on Section 1 (business context)
- Section 3 references all prior sections

---

## Reading Order

**Recommended reading sequence:**
1. **Section 1**: {Title 1} - Start here for business context
2. **Section 2**: {Title 2} - Continue with stakeholder requirements
3. **Section 3**: {Title 3} - Conclude with success criteria

**Quick reference:**
- For business objectives, see Section {N}
- For stakeholder analysis, see Section {M}
- For constraints and assumptions, see Section {O}

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {YYYY-MM-DD} | {Author} | Initial split from monolithic document |

---

## Traceability

- **Original Document**: BRD-{NN} (before split)
- **Element ID Patterns**:
    - Functional Requirements: BRD.{NN}.01.xx (Section 6)
    - Quality Attributes: BRD.{NN}.02.xx (Section 7)
    - Constraints: BRD.{NN}.03.xx (Section 8)
    - Assumptions: BRD.{NN}.04.xx (Section 8)
    - Dependencies: BRD.{NN}.05.xx (Section 8)
    - Acceptance Criteria: BRD.{NN}.06.xx (Section 9)
    - Risks: BRD.{NN}.07.xx (Section 10)
    - Business Objectives: BRD.{NN}.23.xx (Section 2)
    - User Stories:
        - Primary User Stories: PRD.{NN}.09.xx (PRD Section 5, referenced from BRD Section 5)
        - Operational User Stories: PRD.{NN}.10.xx (PRD Section 5, referenced from BRD Section 5)
- **Note**: This BRD utilizes a multi-segment ID format (`BRD.DOC_ID.TYPE_CODE.SEQUENCE`). The TYPE_CODE identifies the element category (e.g., 01=Functional Requirements, 23=Business Objectives). See `ID_NAMING_STANDARDS.md` for complete element type codes.
- **Tag Format**: @ref: BRD-{NN}.{S} (section reference)
- **Downstream Trace**: PRD -> EARS -> BDD -> ADR -> SYS -> REQ -> IMPL -> CTR -> SPEC
