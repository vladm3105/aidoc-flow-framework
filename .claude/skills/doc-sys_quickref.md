# doc-sys - Quick Reference

**Skill ID:** doc-sys
**Layer:** 6 (System Requirements)
**Purpose:** Define functional requirements and quality attributes

## Quick Start

```bash
# Invoke skill
skill: "doc-sys"

# Common requests
- "Create system requirements from ADR-001"
- "Document functional requirements for order management"
- "Generate Layer 6 system requirements"
```

## What This Skill Does

1. Translate ADR decisions into technical requirements
2. Define functional requirements (SYS.NNN.NNN)
3. Specify quality attributes (SYS.NNN.NNN with QA category)
4. Create system flows with Mermaid diagrams
5. Document technical constraints from ADR

## Output Location

```
docs/SYS/SYS-NNN_{descriptive_name}.md
```

## Requirement Formats

**Functional Requirement (FR)**:
```markdown
### SYS.NNN.001: Trade Order Validation
**Description**: System SHALL validate all trade orders
**Input**: Trade order (symbol, quantity, price, account)
**Processing**: Validation steps
**Output**: Validation result
**Source**: EARS.001.001, ADR-033
```

**Quality Attribute (QA)**:
```markdown
### SYS.NNN.015: Order Validation Performance
**Category**: Performance
**Requirement**: SHALL complete within 50ms at P95
**Measurement**: P50 <25ms, P95 <50ms, P99 <100ms
```

## QA Categories

- Performance, Reliability, Security
- Scalability, Maintainability, Observability

## Upstream/Downstream

```
BRD, PRD, EARS, BDD, ADR → SYS → REQ
```

## Quick Validation

- [ ] Functional requirements use unified format (SYS.NNN.NNN)
- [ ] Quality attributes use unified format (SYS.NNN.NNN with QA category)
- [ ] Each requirement has measurable criteria
- [ ] System flows use Mermaid diagrams (not Python code)
- [ ] Technical constraints from ADR documented
- [ ] Cumulative tags: @brd, @prd, @ears, @bdd, @adr (5 tags)

## Template Location

```
ai_dev_flow/SYS/SYS-TEMPLATE.md
```

## Related Skills

- `doc-adr` - Architecture decisions (upstream)
- `doc-req` - Atomic requirements (downstream)
