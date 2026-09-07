# Governance Load Protocol for sdd-orchestrator

## Purpose

The governance tree (~130 files, synced to `sdd-orchestrator/governance/`) is NOT reachable via `skill_view()` unless files are explicitly declared in the skill's `linked_files` or loaded with `file_path` parameter. This protocol condenses the planning-first rules from three core governance documents so agents can apply them without loading the full tree.

## When to Apply

Before ANY SDD document creation, review, or remediation — and before calling any UCX MCP tool (`sdd_init`, `sdd_validate`, `sdd_create_build`, `sdd_review`, `sdd_remediate`, `sdd_next_action`).

## Condensed Rules (from GOVERANCE_RULES.md §2b, §3)

### Plan Types and Storage (GOV §2b)

| Plan Type | Location | Retention |
|-----------|----------|-----------|
| Document-layer IPLAN | `docs/IPLAN/` or `UCX/08_IPLAN/` | Permanent |
| Permanent development plan | `plans/` or `governance/plans/` | Permanent |
| Temporary plan | `tmp/` | Disposable |

### Planning-First Sequence (GOV §3)

1. Analyze provided information, constraints, dependencies, existing context
2. Create planning roadmap for the target scope
3. Create planning document index for required plan artifacts
4. Define changelog plan for the scope
5. Review planning artifacts for gaps — resolve or explicitly defer
6. Create required execution plan artifact:
   - document-layer IPLAN (`IPLAN-NNN_{slug}.md`) for SDD layer delivery
   - permanent development plan (`PLAN-NNN_{slug}.md`, preferred) under `plans/`
7. Record explicit plan approval (human reviewer or independent LLM-as-judge)

### Hard Gates (GOV §3)

- No document creation, testing, or coding begins before the planning gate is approved
- No issue transitions to `ai:in-progress` before planning approval exists
- **No completion claim without filesystem verification** — Plan ≠ Done. A written plan authorizes work; it does not constitute delivery. Before reporting any layer/document as complete, call sdd_next_action and verify existing_artifacts on disk. Never infer completion from pattern-matching across layers.

### Definition of Done — Plan/IPLAN Review Level (DoD)

A plan is Ready when:

- [ ] Planning roadmap created for target scope
- [ ] Planning index lists required planning documents
- [ ] Changelog plan defined for target scope
- [ ] Planning package gap review complete
- [ ] Gaps resolved or explicitly deferred with rationale and owner
- [ ] Solution addresses stated problem directly
- [ ] Implementation approach practical and feasible
- [ ] Edge cases and error handling considered
- [ ] Plan reviewed (self-review for solo projects)
- [ ] Approval record exists for both planning package and IPLAN

### Layer Model (GOV §7) — single-path, no depth tiers

There are **no** Lite/Standard/Full depth tiers. The flow is a single path over the 8
layers — BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code — with **CHG** as a
governance overlay on changes. Which upstream a layer must realize is governed by the
**necessary-upstream contract** (NECESSARY-UPSTREAM-001): a layer traces only the upstream
layers that actually exist, not a fixed tier. Lifecycle: **MVP → PROD → NEW MVP**.

### Operational Steps from DEVELOPMENT_WORKFLOW_GUIDE.md §2

1. Create planning roadmap for issue scope
2. Create planning index listing required plan documents
3. Define changelog plan for issue scope
4. Run planning gap review and resolve or defer gaps with rationale
5. Create and approve IPLAN

## How to Load

When loading `sdd-orchestrator` for SDD work:

```
skill_view(name='sdd-orchestrator', file_path='references/governance-load-protocol.md')
```

This single file condenses the rules from all three governance documents.

If the full governance text is needed (rare), load individually:

```
skill_view(name='sdd-orchestrator', file_path='governance/GOVERNANCE_RULES.md')
skill_view(name='sdd-orchestrator', file_path='governance/DEFINITION_OF_DONE.md')
skill_view(name='sdd-orchestrator', file_path='governance/DEVELOPMENT_WORKFLOW_GUIDE.md')
```

## Maintenance

After every UCX sync (`update-sdd-from-ucx`), review this file against the canonical governance documents. If upstream governance rules have changed, update this condensation.
