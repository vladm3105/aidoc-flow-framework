# ADR Layer Planning & Gap Review

## When to Apply

After BDD layer completion (all docs health >= 8), before ANY ADR document is generated.
ADR generation requires a written and approved plan per governance rules.

## ADR Topic Inventory

Source topics from four streams:

1. **BDD Deferred Findings** — the HEALTH8 5-persona convergent reviews identify items
   "deferred to ADR". Read the chairperson manifest for the categorized list.
2. **PRD adr_topic_elaboration** — every PRD has `traceability.adr_topic_elaboration.topics[]`.
   Extract: topic name, brd_reference, status, business_driver.
3. **EARS Requirements** — state machine, auth, timing, calendar references.
4. **BRD Constraints & Dependencies** — execution models, broker contracts, external services.

Build the topic inventory as a table:

```markdown
| ADR ID | Topic | Source | Priority | Blocks | Consolidated From |
```

## Engine vs Cross-Cutting Categorization

### Engine-Specific ADRs (one per BDD/engine)

- 1:1 mapping: each engine gets one ADR for its execution model
- ADR-01 through ADR-09 (umbrella is ADR-01)
- ADR-01 is the benchmark — generate it first as the quality template

### Cross-Cutting ADRs (affect all engines)

- ADR-10+: Event Bus, Auth, Calendar, Idempotency, Regulatory Reporting,
  Observability, Alerting, Backpressure, Input Validation, Encryption
- These unblock BDD deferred findings that are ADR-blocked
- Consolidation allowed: merge related topics (e.g., Input Validation into Encryption)
- Generated in Phase 3 after engine ADRs are validated

## Coverage Matrix

Every BDD deferred finding must map to exactly one ADR:

```markdown
| BDD Finding | Resolved By | Notes |
```

Include SEC/REG findings from the security-auditor HEALTH8 review.
Goal: 0 remaining uncovered.

## Gap Review Methodology

After drafting the plan, run a self-review against:

1. BDD chairperson manifest — every P0/P1 deferred finding must have an ADR home
2. PRD adr_topic_elaboration — every topic from every PRD must be assigned
3. SEC/REG HEALTH8 findings — regulatory gaps are not optional
4. Template requirements — ADR-TEMPLATE.yaml mandates specific sections

## Pre-Generation Checklist (Phase 0)

Before ADR creation:

- [ ] Fix BDD hash collisions (SCH-002 style — identical hashes across docs)
- [ ] Fix PRD placeholder hashes (`xxxx` in @brd/@ears references)
- [ ] Verify all BDD validation reports exist (out/04_BDD/*.ucx.validate.json)
- [ ] Verify ADR-TEMPLATE.yaml is current (run sdd_init with update=true)
- [ ] Verify all 4 upstream layers pass structural validation

**Gate**: No ADR creation begins until this checklist is complete and approved.

## Anti-Patterns

1. **Skipping gap review**: writing a plan without cross-referencing BDD deferred findings
   means ADRs will miss the decisions they need to make → BDD stays deferred → layer stalls.
2. **Mixing numbering schemes**: engine ADRs and cross-cutting ADRs sharing the 01-09 range
   causes confusion. Use ADR-01-09 for engines, ADR-10+ for cross-cutting.
3. **Underestimating regulatory ADRs**: SEC 17a-3/17a-4 (WORM), CAT NMS Plan, FINRA TRACE/ORF
   are NOT optional. They belong in the plan or the layer is incomplete.
4. **Consolidating too aggressively**: merging 5 cross-cutting topics into one ADR saves files
   but breaks the "one decision per file" rule. Prefer separate ADRs with cross-references.
