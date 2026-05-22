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
- "Document architecture decision from BRD-01"
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
docs/05_ADR/ADR-NN_{slug}/ADR-NN_{slug}.md
```

## ADR Format (11 Sections)

| # | Section | Purpose |
|---|---------|---------|
| 1 | Document Control | Metadata with SPEC-Ready Score |
| 2 | Context | Problem Statement, Technical Context |
| 3 | Decision | Chosen Solution, Key Components, Approach |
| 4 | Alternatives Considered | Options with pros/cons |
| 5 | Consequences | Positive/Negative Outcomes, Costs |
| 6 | Architecture Flow | Mermaid diagrams, Integration Points |
| 7 | Implementation Assessment | Phases, Rollback, Monitoring |
| 8 | Verification | Success Criteria, BDD Scenarios |
| 9 | Traceability | Upstream/Downstream, Tags, Cross-Links |
| 10 | Related Decisions | Dependencies, Supersessions |
| 11 | MVP Lifecycle | Iteration guidance |

## Key Considerations

- **Always check ADR-00** (Technology Stack) before proposing new technology
- **Platform ADRs first** - Create foundation decisions before feature-specific ones
- **4 lifecycle states**: Proposed → Accepted → Deprecated/Superseded

## Upstream/Downstream

```
BRD, PRD, EARS, BDD → ADR → SPEC, TDD, IPLAN
```

## Element IDs

- Document ref: `ADR-NN` (e.g. `ADR-01`)
- Element ref: `ADR.NN.SS.xxxx` (4-segment, 4-char hex hash)

## Quick Validation

- [ ] Status field completed
- [ ] Context explains problem and constraints
- [ ] Decision clearly stated
- [ ] Consequences analyzed (positive, negative, risks)
- [ ] Alternatives documented with rejection rationale
- [ ] Technology Stack (ADR-00) referenced if applicable
- [ ] Cumulative tags: @brd, @prd, @ears, @bdd (4 tags)

## Template Location

```
framework/layers/05_ADR/ADR-TEMPLATE.yaml
```

## Related Skills

- `doc-bdd` - BDD test scenarios (upstream)
- `doc-spec` - Component specifications (downstream)
