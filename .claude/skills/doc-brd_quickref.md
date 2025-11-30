# doc-brd - Quick Reference

**Skill ID:** doc-brd
**Layer:** 1 (Business Requirements)
**Purpose:** Create Business Requirements Documents (BRD)

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

## Key Sections

| Section | Purpose |
|---------|---------|
| Executive Summary | High-level business context |
| Business Objectives | Measurable goals (SMART) |
| Stakeholders | Who is impacted |
| Scope | What's in/out |
| Success Criteria | How success is measured |
| Constraints | Business limitations |
| Assumptions | Documented assumptions |
| Traceability | Links to downstream artifacts |

## Upstream/Downstream

```
[No upstream] → BRD → PRD, EARS, BDD
```

## Quick Validation

- [ ] Business objectives are measurable (SMART)
- [ ] Stakeholders identified with roles
- [ ] Scope clearly defined (in/out)
- [ ] Success criteria are quantifiable
- [ ] Traceability section complete

## Template Location

```
ai_dev_flow/BRD/BRD-TEMPLATE.md
```

## Related Skills

- `doc-prd` - Create product requirements (downstream)
- `doc-ears` - Formalize requirements (downstream)
- `project-init` - Initialize project structure
