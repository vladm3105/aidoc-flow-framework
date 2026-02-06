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
6. Discover and consolidate sectioned BRD documents as ONE input

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
| Quality Attributes | Performance, security, reliability |
| Success Metrics | KPIs and measurements |
| Traceability | Links to BRD and downstream |

## Upstream/Downstream

```
BRD → PRD → EARS, BDD
```

## Quick Validation

- [ ] References upstream BRD document(s)
- [ ] BRD sections read completely (all 19 files if sectioned)
- [ ] BRD treated as single logical document
- [ ] User stories follow standard format
- [ ] Acceptance criteria are testable
- [ ] Success metrics are quantifiable
- [ ] Traceability matrix complete

## BRD Input Handling

When BRD is sectioned (multiple files):
- Read ALL section files (0-18) as ONE document
- No BRD section → PRD section mapping
- Extract holistically across all sections
- Reference: See `PRD_CREATION_RULES.md` Section 22

## Template Location

```
ai_dev_flow/02_PRD/PRD-MVP-TEMPLATE.md
```

## Related Skills

- `doc-brd` - Business requirements (upstream)
- `doc-ears` - Formalize requirements (downstream)
- `doc-bdd` - BDD test scenarios (downstream)
