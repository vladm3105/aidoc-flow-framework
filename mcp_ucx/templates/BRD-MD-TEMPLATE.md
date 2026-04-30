# BRD-MD-TEMPLATE: YAML-to-Markdown Rendering Standard

This template defines the standard format for rendering BRD YAML documents as human-readable Markdown.

## Frontmatter

---
title: "BRD-NN: {Title}"
document_type: brd-document
layer: 1
schema_version: "1.5"
tags: [brd-document, layer-1-artifact, ...]
brd_type: platform | feature
deliverable_type: code | document | ux | risk | process
---

## Section Headings

Format: `## N. Section Title` followed by element ID on next line.

Example:
## 1. Document Control
`[BRD.NN.xxxx]`

## Diagram Index (Section 2a)

Insert after Section 2 (Executive Summary):

## 2a. Diagram Index
`[BRD.NN.xxxx]`

| # | Diagram | ID | Scope |
|---|---------|-----|-------|
| 01 | [Title](diagrams/filename.svg) | `[BRD.NN.xxxx]` | Description |

## Inline Diagram References

At the start of sections with associated diagrams:

> **Diagram**: [Chart of Accounts](diagrams/05_chart_of_accounts.svg) `[BRD.NN.xxxx]`

## Table Formats

### Stakeholders
| Role | Type | Interest | Influence |

### RACI Matrix
| Activity | CFO | CCO | Treasury | Finance | Engineering |
R = Responsible, A = Accountable, C = Consulted, I = Informed

### Risks
| ID | Risk | L | I | Score | Mitigation | Owner |

### ADT Alternatives
| Option | Function | Est. Monthly Cost | Rationale |
Selected option in **bold**.

### Cost Comparison
| Category | Option A | Option B |

### Quality Attributes
| ID | Requirement | Measurement | Rationale |

### User Stories
- **As a** {role}
- **I want** {capability}
- **So that** {benefit}
**Acceptance Criteria**: bullet list

## Business Rules

Format MUST/SHALL/MUST NOT in bold:
- **Accounts MUST have unique identifiers**
- **Closed accounts MUST NOT accept new postings**

## Cross-References

- Element-level: `[BRD.NN.xxxx]`
- Document-level: BRD-NN
- Upstream: `@depends: BRD-01`
- Downstream: `@discoverability: BRD-05`
