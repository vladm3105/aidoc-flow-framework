# doc-adr - Quick Reference

**Skill ID:** doc-adr
**Layer:** 5 (Architecture Decision Records)
**Purpose:** Document architectural decisions with Context-Decision-Consequences format

## Quick Start

```bash
# Invoke skill
skill: "doc-adr"

# Common requests
- "Create ADR for database technology selection"
- "Document architecture decision from BRD-001"
- "Generate Layer 5 architecture decision record"
```

## What This Skill Does

1. Document architectural decisions with rationale
2. Apply Context-Decision-Consequences format
3. Evaluate and document alternatives considered
4. Define verification approach
5. Track decision lifecycle (Proposed → Accepted → Deprecated)

## Output Location

```
docs/ADR/ADR-NNN_{descriptive_name}.md
```

## ADR Format

```markdown
# ADR-NNN: Decision Title

## Status
Proposed | Accepted | Deprecated | Superseded by ADR-XXX

## Context
What issue are we addressing? What factors are in play?

## Decision
What change are we proposing or implementing?

## Consequences
### Positive Consequences
### Negative Consequences
### Risks

## Alternatives Considered
```

## Key Considerations

- **Always check ADR-000** (Technology Stack) before proposing new technology
- **Platform ADRs first** - Create foundation decisions before feature-specific ones
- **4 lifecycle states**: Proposed → Accepted → Deprecated/Superseded

## Upstream/Downstream

```
BRD, PRD, EARS, BDD → ADR → SYS, REQ
```

## Quick Validation

- [ ] Status field completed
- [ ] Context explains problem and constraints
- [ ] Decision clearly stated
- [ ] Consequences analyzed (positive, negative, risks)
- [ ] Alternatives documented with rejection rationale
- [ ] Technology Stack (ADR-000) referenced if applicable
- [ ] Cumulative tags: @brd, @prd, @ears, @bdd (4 tags)

## Template Location

```
ai_dev_flow/05_ADR/ADR-MVP-TEMPLATE.md
```

## Related Skills

- `doc-bdd` - BDD test scenarios (upstream)
- `doc-sys` - System requirements (downstream)
- `doc-req` - Atomic requirements (downstream)
