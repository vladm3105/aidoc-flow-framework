# doc-brd - Quick Reference

**Skill ID:** doc-brd
**Layer:** 1 (Business Requirements)
**Purpose:** Create Business Requirements Documents (BRD)
**Template Version:** 1.2 (18 Sections)
**Lifecycle:** MVP → PROD → NEW MVP

## Lifecycle: MVP → PROD → NEW MVP

```
BRD-01 (MVP) → Production v1 → Feedback → BRD-02 (NEW MVP) → Production v2 → ...
```

| Principle | Rule |
|-----------|------|
| Each BRD = One Cycle | Don't expand BRDs indefinitely |
| New Features = New BRD | Create BRD-02 for next iteration |
| 5-15 Requirements | Keep focused per cycle |
| Cross-Cycle Links | Use `@depends: BRD-01` |

## Quick Start

```bash
# Invoke skill
skill: "doc-brd"

# Common requests
- "Create a BRD for our new payment system"
- "Document business requirements for feature X"
- "Generate Layer 1 business requirements"
```

## What This Skill Does

1. Analyze business context and stakeholder needs
2. Define strategic objectives and success criteria
3. Identify business constraints and assumptions
4. Document scope and out-of-scope items
5. Create traceability to downstream artifacts (PRD, EARS, BDD)

## Output Location

```
docs/BRD/BRD-NNN_{descriptive_name}.md
```

## Key Sections (18-Section Structure)

| Section | Purpose |
|---------|---------|
| Document Control | Metadata and revision history |
| 1. Introduction | Purpose, scope, audience |
| 2. Business Objectives | Measurable goals (SMART) |
| 3. Project Scope | What's in/out |
| 4. Stakeholders | Who is impacted |
| 5. User Stories | High-level user needs |
| 6. Functional Requirements | Business capabilities |
| **7. Quality Attributes** | **Performance, security, ADR topics** |
| 8. Constraints & Assumptions | Business limitations |
| 9. Acceptance Criteria | Success measures |
| 10. Risk Management | Risk register |
| 11. Implementation Approach | Phases, rollout |
| 12. Support & Maintenance | Support model |
| 13. Cost-Benefit Analysis | ROI, costs |
| **14. Project Governance** | **Decision authority, approval** |
| **15. Quality Assurance** | **QA standards, testing strategy** |
| **16. Traceability** | **Requirements matrix, health score** |
| **17. Glossary** | **Terms (6 subsections)** |
| 18. Appendices | Supporting documents |

## 7 Mandatory ADR Topic Categories (Section 7.2)

| # | Category | Element ID |
|---|----------|------------|
| 1 | Infrastructure | BRD.NN.32.01 |
| 2 | Data Architecture | BRD.NN.32.02 |
| 3 | Integration | BRD.NN.32.03 |
| 4 | Security | BRD.NN.32.04 |
| 5 | Observability | BRD.NN.32.05 |
| 6 | AI/ML | BRD.NN.32.06 |
| 7 | Technology Selection | BRD.NN.32.07 |

**Required per topic**: Status, Business Driver, Business Constraints, Alternatives Overview table, Cloud Provider Comparison table, Recommended Selection, PRD Requirements

## Upstream/Downstream

```
[No upstream] → BRD → PRD, EARS, BDD
```

## Quick Validation

- [ ] 18 numbered sections present
- [ ] Section 7.2 has ADR summary table
- [ ] Section 14.5 Approval and Sign-off exists
- [ ] Section 15 Quality Assurance exists
- [ ] Section 16.1-16.4 Traceability subsections exist
- [ ] Section 17.1-17.6 Glossary subsections exist
- [ ] PRD-Ready Score in Document Control
- [ ] No duplicate section numbers

## Template Location

```
ai_dev_ssd_flow/01_BRD/BRD-MVP-TEMPLATE.md
```

## Related Skills

- `doc-prd` - Create product requirements (downstream)
- `doc-ears` - Formalize requirements (downstream)
- `project-init` - Initialize project structure
- `doc-brd-validator` - Validate BRD structure
- `doc-brd-reviewer` - Review BRD content
- `doc-brd-fixer` - Fix BRD issues
- `doc-brd-autopilot` - Automated BRD generation
