# doc-ears - Quick Reference

**Skill ID:** doc-ears
**Layer:** 3 (Formal Requirements)
**Purpose:** Create EARS (Easy Approach to Requirements Syntax) formal requirements

## Quick Start

```bash
# Invoke skill
skill: "doc-ears"

# Common requests
- "Create EARS requirements from PRD-001"
- "Formalize feature requirements using WHEN-THE-SHALL"
- "Generate Layer 3 formal requirements"
```

## What This Skill Does

1. Transform PRD requirements into formal EARS syntax
2. Apply WHEN-THE-SHALL-WITHIN pattern
3. Ensure requirements are testable and measurable
4. Add timing constraints (WITHIN clause)
5. Create traceability to BDD and ADR

## Output Location

```
docs/EARS/EARS-NNN_{descriptive_name}.md
```

## EARS Syntax Pattern

```
WHEN <trigger_condition>
THE <system/component>
SHALL <action/behavior>
WITHIN <time_constraint>
```

## Example

```
EARS-001: WHEN a user submits login credentials
          THE authentication service
          SHALL validate credentials and return session token
          WITHIN 500ms
```

## Upstream/Downstream

```
BRD, PRD → EARS → BDD, ADR
```

## Quick Validation

- [ ] All requirements follow WHEN-THE-SHALL-WITHIN format
- [ ] Timing constraints are specified
- [ ] Requirements are atomic (single behavior)
- [ ] Requirements are testable
- [ ] Traceability to PRD complete

## Template Location

```
ai_dev_flow/EARS/EARS-TEMPLATE.md
```

## Related Skills

- `doc-prd` - Product requirements (upstream)
- `doc-bdd` - BDD test scenarios (downstream)
- `doc-adr` - Architecture decisions (downstream)
