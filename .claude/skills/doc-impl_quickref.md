# doc-impl - Quick Reference

**Skill ID:** doc-impl
**Layer:** 8 (Implementation Approach) - **OPTIONAL**
**Purpose:** Document WHO-WHEN-WHAT implementation strategy

## Quick Start

```bash
# Invoke skill
skill: "doc-impl"

# Common requests
- "Create implementation approach from REQ-001"
- "Document team assignments and timeline"
- "Generate Layer 8 implementation strategy"
```

## What This Skill Does

1. Document WHO (team/developer assignments)
2. Define WHEN (timeline and milestones)
3. Specify WHAT (implementation scope)
4. Identify dependencies and blockers
5. Assess risks with mitigation strategies

## Output Location

```
ai_dev_flow/IMPL/IMPL-NNN_{descriptive_name}.md
```

## WHO-WHEN-WHAT Format

```markdown
### WHO: Team Assignment
**Primary Developer**: @john.doe
**Code Reviewer**: @jane.smith

### WHEN: Timeline
**Start Date**: 2025-01-15
**Target Completion**: 2025-01-29

### WHAT: Scope
**Requirements**: REQ-data-validation-001
**Deliverables**: Service, tests, documentation
```

## 4-PART Structure

1. **Project Context and Strategy** (Overview, Objectives, Scope)
2. **Implementation Strategy** (WHO-WHEN-WHAT, Phases, Dependencies)
3. **Risk Management** (Assessment, Contingency)
4. **Traceability** (Upstream, Downstream, Tags)

## Upstream/Downstream

```
BRD, PRD, EARS, BDD, ADR, SYS, REQ → IMPL → CTR, SPEC
```

## Quick Validation

- [ ] WHO-WHEN-WHAT framework completed
- [ ] Team assignments documented
- [ ] Timeline and milestones defined
- [ ] Technical approach specified
- [ ] Dependencies identified
- [ ] Risk assessment completed
- [ ] Cumulative tags: @brd through @req (7 tags)

## Template Location

```
ai_dev_flow/IMPL/IMPL-TEMPLATE.md
```

## Related Skills

- `doc-req` - Atomic requirements (upstream)
- `doc-ctr` - Data contracts (downstream, optional)
- `doc-spec` - Technical specifications (downstream)

## Note

**This layer is OPTIONAL** - Skip if implementation approach is straightforward
