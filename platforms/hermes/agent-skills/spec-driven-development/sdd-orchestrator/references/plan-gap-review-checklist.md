# Plan Gap Review Checklist

**Purpose**: Concrete checklist for auditing a plan (PLAN-NNN or IPLAN-NNN) against SDD governance rules (GOVERNANCE_RULES.md §3) and Definition of Done (DEFINITION_OF_DONE.md — Plan/IPLAN Review Level).

**When to use**: After writing a plan and before presenting it for approval. Run every gap item; resolve or explicitly defer each.

---

## Gap Categories (Audit Pass Order)

### G1 — Changelog Plan
- [ ] Does the plan define what changelog entries will be created?
- [ ] Are the target files named (CHANGELOG.md, plans/CHANGELOG-PLAN.md, layer README)?
- [ ] Are changelog entry formats consistent with project conventions?

**GOV reference**: §3 step 4 — "Define changelog plan for the scope"
**Common gap**: Plan has a "Changelog Plan" heading but only lists target documents, not actual entries.

### G2 — Gap Review
- [ ] Is there an explicit gap review section in the plan?
- [ ] Are unknowns/unknowns enumerated (things not yet decided)?
- [ ] Is each gap resolved or explicitly deferred with rationale?
- [ ] Are deferred gaps assigned an owner (e.g., "deferred to ADR")?

**GOV reference**: §3 step 5 — "Review planning artifacts for gaps"
**Common gap**: Plan skips the gap review entirely — assumes everything is known.

### G3 — Planning Index
- [ ] Does `plans/README.md` or equivalent index this plan?
- [ ] Is the plan's status column current?
- [ ] Are downstream artifacts (e.g., new SDD document entries) reflected?

**GOV reference**: §3 step 3 — "Create planning document index"
**Common gap**: Plan written but never registered in the index — future sessions can't find it.

### G4 — Upstream Dependencies
- [ ] Are ALL upstream SDD artifacts that this work depends on listed?
- [ ] Are cross-BRD dependencies complete (not just the obvious ones)?
- [ ] Are data consumers listed (e.g., "BRD-03 needs option chain from broker")?

**Common gap**: Feature BRD lists BRD-01 (umbrella) but misses the data-consumer BRDs that will use its output.

### G5 — Roadmap Update Timing
- [ ] Does the plan update the roadmap during planning, or defer to "after creation"?
- [ ] If deferred, is there a clear handoff so the update doesn't get lost?

**GOV reference**: §3 step 2 — "Create planning roadmap for the target scope"
**Common gap**: Plan says "update roadmap after document created" but post-creation sessions forget.

### G6 — ADR/Design Topics
- [ ] Are architecture decision topics enumerated with sufficient coverage?
- [ ] Are security, auth, credentials, isolation, and failover topics present?
- [ ] Is there at least one topic per mandatory category (infrastructure, data, integration, security, observability)?

**Common gap**: 7 ADR topics listed but auth/credentials, market data subscriptions, paper/live isolation, and order routing are missing.

### G7 — Scope Boundary
- [ ] Is there an explicit "OUT of scope" section?
- [ ] Does it prevent the new artifact from absorbing content that belongs in existing artifacts?
- [ ] Are deferred features listed with rationale?

**Common gap**: Plan defines IN scope only — no boundary to prevent scope creep into adjacent BRDs.

### G8 — Document Section Outline
- [ ] Does the plan sketch what goes in each section of the target SDD document?
- [ ] For BRDs: are all 18 sections accounted for with content expectations?
- [ ] Is the outline detailed enough that generation won't miss sections?

**Common gap**: Plan says "generate BRD-10 per template" without sketching section content.

### G9 — CHG Governance
- [ ] Is this a change to an existing layer? If so, is a CHG record included?
- [ ] Does the plan document downstream impact (new PRD/EARS/BDD/etc. required)?
- [ ] Is the change rationale documented?

**Common gap**: Adding a BRD to a "complete" layer — no CHG record, no downstream impact analysis.

### G10 — Validation Pre-Check
- [ ] Does the plan verify that the new artifact won't conflict with existing artifacts?
- [ ] Are cross-references to existing documents checked for accuracy before creation?
- [ ] Is the target artifact numbered correctly (no collision with existing IDs)?

**Common gap**: Plan doesn't check whether BRD-04 already covers the proposed BRD-10 scope.

---

## Quick Audit Commands

```bash
# G3: Check if plan is in index
grep -c "PLAN-NNN" plans/README.md

# G4: Find all upstream BRD references
grep -oP 'BRD-\d+' plans/PLAN-NNN_*.md | sort -u

# G10: Check for scope overlap with existing documents
grep -l "broker\|order execution\|position monitoring" 01_BRD/BRD-*.yaml
```

---

## TradeGent CC PLAN-009 Example (2026-05-14)

Initial audit found 10 gaps across all 10 categories:
- P0 (2): G1 (changelog plan missing), G2 (gap review missing)
- P1 (5): G3, G4 (BRD-03/BRD-06 missing), G5, G6 (ADR topics incomplete), G7
- P2 (3): G8, G9, G10

After remediation: all 10 gaps resolved, plan approved, BRD-10 created and validated 100/100.
