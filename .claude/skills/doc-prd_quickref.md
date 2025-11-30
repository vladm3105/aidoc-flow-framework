# doc-prd - Quick Reference

**Skill ID:** doc-prd
**Layer:** 2 (Product Requirements)
**Purpose:** Create Product Requirements Documents (PRD)

## Quick Start

```bash
# Invoke skill
skill: "doc-prd"

# Common requests
- "Create a PRD from BRD-001"
- "Document product features for user authentication"
- "Generate Layer 2 product requirements"
```

## What This Skill Does

1. Transform business requirements into product features
2. Define user stories and acceptance criteria
3. Specify functional requirements with KPIs
4. Document user personas and journeys
5. Create traceability to upstream BRD and downstream EARS/BDD

## Output Location

```
docs/PRD/PRD-NNN_{descriptive_name}.md
```

## Key Sections

| Section | Purpose |
|---------|---------|
| Product Overview | What the product does |
| User Personas | Who uses the product |
| User Stories | As a... I want... So that... |
| Functional Requirements | What the system does |
| Non-Functional Requirements | Quality attributes |
| Success Metrics | KPIs and measurements |
| Traceability | Links to BRD and downstream |

## Upstream/Downstream

```
BRD → PRD → EARS, BDD
```

## Quick Validation

- [ ] References upstream BRD document(s)
- [ ] User stories follow standard format
- [ ] Acceptance criteria are testable
- [ ] Success metrics are quantifiable
- [ ] Traceability matrix complete

## Template Location

```
ai_dev_flow/PRD/PRD-TEMPLATE.md
```

## Related Skills

- `doc-brd` - Business requirements (upstream)
- `doc-ears` - Formalize requirements (downstream)
- `doc-bdd` - BDD test scenarios (downstream)
