# 09_CHG — Change Record (Governance Overlay)

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-07 |
| Author | Framework Maintainer |
| Framework Version | 0.53.0 |


## Overview

CHG is a **governance overlay** for managing changes to existing SDD artifacts. It is **NOT** a lifecycle layer in the BRD→IPLAN→Code workflow — it triggers on-demand when modifying any artifact across the SDD chain.

**Position**: 09 (operational namespace, reserved between IPLAN L8 and EVAL L10)

**Scope**: Gate definitions, the CHG template, approval and post-mortem companions, and the 14-point creation checklist. CHG uses gate approval instead of readiness scores.

**Workflow**: Any artifact change → Classify (C1/C2/C3/Emergency) → Route to entry gate → Assess impact → Update artifacts → Verify → Record in CHG document

## What CHG Is and Is Not

| CHG **IS** | CHG **IS NOT** |
|------------|----------------|
| A governance overlay triggered on-demand | Part of the BRD→IPLAN→Code workflow |
| An approval and audit trail for changes | A lifecycle layer with readiness scores |
| A record of what changed, why, and the impact | An implementation plan (that's IPLAN's job) |
| An archive mechanism for superseded SDD versions | A template in the YAML chain |

## Design Decisions

- **Overlay, not lifecycle layer** — CHG triggers on-demand when modifying existing artifacts; it does not participate in the readiness score chain or the BRD→IPLAN authoring workflow. This is recorded as GD-01 in `framework/governance/DECISIONS.md`.
- **Gate approval replaces readiness scores** — Lifecycle layers use readiness gates (≥90/100); CHG uses explicit gate approval (GATE-01/03/06/08/CODE/SPEC) with human sign-off.
- **SDD-first implementation order** — When a CHG modifies SDD documents, the SDD updates ship BEFORE any code changes: CHG → SDD docs → IPLAN → code.
- **No circular dependencies** — CHG references upstream artifacts to record what changed, but no lifecycle layer references CHG.
- **Archive-not-append** — Superseded SDD versions are archived to `docs/sdd/09-CHG/archive/{CHG-ID}/{layer}/`, never appended. The current docs directory always reflects the latest truth.

## Change Levels

| Level | Scope | Gate Required | Process |
|-------|-------|---------------|---------|
| C1 | Typo, formatting, clarification | None — direct commit | Fix → commit → completed |
| C2 | Section update, requirement refinement | Peer review | Assess impact → update → verify |
| C3 | Cross-layer change, new requirements | Formal gate | Full CHG process |
| Emergency | Critical production issue | Post-hoc approval + post-mortem | Fix → deploy → document within 48h |

**Note**: For `change_source: spec` (GATE-SPEC), change_level must be >= C2 (never C1 per GATE-SPEC-E003). Major `semver_impact` requires C3.

## Change Source Routing

| Source | Entry Gate | Cascade Direction |
|--------|-----------|-------------------|
| Upstream | GATE-01 | BRD/PRD change cascading down |
| Midstream | GATE-03 | EARS/BDD/ADR change affecting neighbors |
| Design | GATE-06 | SPEC/TDD change |
| Execution | GATE-08 | IPLAN change |
| External (business) | GATE-01 | Regulatory, compliance, partner demands |
| External (technical) | GATE-03 | Security CVE, dependency update, 3rd-party API |
| Feedback | GATE-CODE | Production feedback, user issues (bubble-up) |
| Spec | GATE-SPEC | Change to the `framework/` spec itself (meta — orthogonal) |

## Cascade Chain

```
BRD(L1) → PRD(L2) → EARS(L3) → BDD(L4) → ADR(L5) → SPEC(L6) → TDD(L7) → IPLAN(L8) → Code
```

CHG sits **outside** this chain. It triggers on-demand to authorize and record changes to any artifact within it.

## CHG Status Lifecycle (Mandatory)

Every CHG document **MUST** track its status through the full lifecycle. Status changes are the mechanism that allows stopping and resuming implementation without rescanning the codebase.

**Required status transitions:**

| Status | When | What to update |
|--------|------|----------------|
| `Proposed` | CHG created | `date_proposed`, all issues `status: Proposed` |
| `Approved` | Gate passed | `date_approved`, `change_control.status: Approved` |
| `In-Progress` | Implementation started | `change_control.status: In-Progress`, issues transition to `In-Progress` |
| `Implemented` | All issues implemented and merged | `date_implemented`, `change_control.status: Implemented` |
| `Completed` | SDD docs updated, verification passed | `change_control.status: Completed` |

**Rules:**
1. Status must never regress. A CHG cannot move from `Implemented` back to `In-Progress`. If rework is needed, create a new CHG.
2. Issue-level statuses must match the CHG status. When `Implemented`, every issue must be `Implemented` or `Skipped` (with justification).
3. Status transitions ship in the same change. No stale statuses.
4. `In-Progress` enables resumption. The next agent reads the CHG and knows exactly which issue to pick up.
5. `Implemented` ≠ `Completed`. `Implemented` = code merged. `Completed` = SDD docs updated, verification passed, fully closed.

## Rules

### Mandatory SDD Sync on IPLAN Completion

When an IPLAN is marked `Completed`, the corresponding SPEC and TDD documents **MUST** be updated to reflect what was actually built. If the implementation diverged from the spec, a CHG must be created and the SPEC/TDD rewritten as a new version. The IPLAN status change and the SPEC/TDD update must ship in the same change.

### IPLAN File Manifest Accuracy

When an IPLAN is marked `Completed`, every file in its `file_manifest` with `status: Completed` must actually exist on disk and contain a real implementation (not a stub/mock).

### C3 Gate Approval for Solo Projects

For solo-maintained projects, C3 CHGs are self-approved by the project owner (technical lead). Record in `gate_approval` with `approver: "Self (C3 — Technical Lead)"`.

### SDD Document Versioning via CHG

When an SDD document needs updating, the CHG record owns the version lifecycle:

1. Archive current version to `docs/sdd/09-CHG/archive/{CHG-ID}/{layer}/`
2. Rewrite the document in place as a clean, self-contained new version
3. Bump `document_control.version` (1.0 → 2.0 → 3.0)
4. Update `document_control.last_updated` to the CHG date
5. Record archive path in the CHG's `supersedes` field
6. Keep the same document ID (e.g., SPEC-01 stays SPEC-01 across versions)
7. The rewritten document must be clean — no appendices, no "added by CHG-XX" annotations

### CHG Archive Convention

Archive path is always `docs/sdd/09-CHG/archive/{CHG-ID}/{layer}/` where layer is one of `06_SPEC`, `07_TDD`, `08_IPLAN`. The CHG's `supersedes` field lists each archived document with its full archive path. Never use date-based archive paths.

### No Stale Context in SDD Docs

Remove stale content when rewriting. Don't keep unused sections, duplicate entries, or references to retired approaches. A v2 document should read as if written from scratch.

## CHG Creation Checklist

Before writing any CHG document, complete this 14-point checklist. Each item maps to a gap class found in CHG post-creation reviews.

| # | Check | Gap it prevents |
|---|-------|-----------------|
| 1 | **Read every file you reference** — open each artifact path in `artifacts_modified` and verify it exists | Wrong filenames, wrong line numbers, wrong function signatures |
| 2 | **Verify the architectural claim** — confirm whether the problem is client-side, server-side, or both | Mischaracterized architecture |
| 3 | **Check existing struct/type signatures** — verify existing struct accepts new fields | Claims struct has no field when it does |
| 4 | **Check existing INSERT/SELECT queries** — verify existing queries that touch modified tables | Adding columns without updating existing queries |
| 5 | **Cross-reference upstream requirements** — cite specific EARS requirement IDs and BDD scenario IDs | No traceability in CHG |
| 6 | **Check for existing handlers/webhooks** — check if a webhook handler already exists for the event type | Existing handler not considered |
| 7 | **Couple dependent issues** — if two issues share a fix, implement them together | Coupled issues implemented separately |
| 8 | **Add automated test specifications** — specify test file, test name, and assertion method | No automated test specs |
| 9 | **Verify the fix location** — check whether the error is thrown in the function or the caller | Wrong fix location |
| 10 | **Add DB migration + rollback** — provide full migration SQL, rollback SQL, backfill strategy, and indexes | Migration without rollback |
| 11 | **Plan SDD document versioning** — archive → rewrite → supersedes → version bump | No SDD lifecycle steps |
| 12 | **Check traceability to SDD lifecycle rules** — verify DOC_GOVERNANCE_CORE.md rules are satisfied | Rules not enforced at creation time |
| 13 | **SDD-first implementation order** — SDD document updates MUST appear BEFORE any code steps | Wrong ordering |
| 14 | **CHG scope: governance, not implementation plan** — CHG authorizes and scopes; code steps belong in IPLAN | Detailed code steps in CHG |

## CHG Document Structure

Each CHG document contains 7 sections (8 for Emergency):

| Section | Purpose |
|---------|---------|
| 1. Change Control | ID, status, level, source, gate, author, dates, supersedes |
| 2. Change Description | What changed, why, trigger |
| 3. Impact Assessment | Affected layers, cascade direction, risk level, traceability |
| 4. Implementation | SDD lifecycle steps first, then IPLAN creation/update |
| 5. Verification | Automated tests and manual checks with methods |
| 6. Gate Approval | Gate reference, approver, date, conditions |
| 7. Rollback Plan | Strategy, steps, estimated effort |
| 8. Emergency Change | (Conditional) Emergency ID, severity, post-mortem tracking |

## Gate System

CHG gates are the approval checkpoints for change management:

| Gate | Layers | Purpose |
|------|--------|---------|
| GATE-01 | L1-L2 (BRD, PRD) | Business/product gate |
| GATE-03 | L3-L5 (EARS, BDD, ADR) | Requirements & architecture gate |
| GATE-06 | L6-L7 (SPEC, TDD) | Design & test gate |
| GATE-08 | L8 (IPLAN) | Implementation plan gate |
| GATE-CODE | Code | Implementation gate |
| GATE-SPEC | meta | Framework-spec gate (changes to `framework/` itself) |

## Implementation Order (CHG → SDD → IPLAN → Code)

The correct flow when a CHG modifies SDD documents:

```
CHG (authorize)
  → Phase 0: SDD Document Updates (FIRST)
    1. Archive current versions to 09-CHG/archive/{CHG-ID}/{layer}/
    2. Rewrite each SDD document as clean v2 (upper layers first: PRD → SPEC → IPLAN)
    3. Update supersedes field with archive paths
    4. Bump document_control.version to 2.0
  → Phase 1: IPLAN Creation/Update
    5. Create or update IPLAN with ALL code implementation steps
  → Code implementation (from IPLAN)
```

CHG is a governance record, NOT an implementation plan. Code implementation steps belong in the IPLAN.

## Note on `09_CHG` Namespace

While CHG is an overlay rather than a sequential 9th SDD lifecycle layer, the `09_CHG` prefix is the reserved operational namespace across the framework for:

- **Playbook definitions** (`framework/playbooks/09_CHG/`)
- **Example artifacts and project documentation** (`docs/sdd/09-CHG/`)
- **Multi-agent saga review dispatch and schema validation** (`saga.schema.json` layer enum)

## Framework Self-Changes

When modifying `framework/` itself (templates, governance, registry, VERSION),
the change follows the same CHG process but routes through **GATE-SPEC** instead
of the artifact cascade gates. The workflow:

1. **Create CHG record** — classify as C2 or C3 (never C1 for spec changes)
2. **Archive originals** — to `archive/{CHG-ID}/` before any modification
3. **Update affected files** — with `document_control` blocks (GD-24)
4. **Bump VERSION** — `framework/VERSION` follows SemVer
5. **Update CHANGELOG.md** — document-of-record for spec changes (E008)
6. **Record decision** — add GD entry to `DECISIONS.md` if significant
7. **Both platforms re-declare** — `FRAMEWORK_SPEC_VERSION` + conformance green

CHG records for framework self-changes live in `archive/{CHG-ID}/CHG-{NN}.yaml`
alongside the archived originals. The CHG `supersedes` field lists every
modified file with its archive path.

## Glossary

| Term | Definition |
|------|-----------|
| CHG | Change Record — governance document for SDD artifact modifications |
| C1 | Trivial change — typo, formatting, clarification (no gate) |
| C2 | Minor change — section update, refinement (peer review) |
| C3 | Major change — cross-layer, new requirements (formal gate) |
| Emergency | Critical production fix — bypass normal process, post-mortem within 48h |
| Gate | Approval checkpoint — GATE-01 (business), GATE-03 (requirements/architecture), GATE-06 (design/test), GATE-08 (IPLAN), GATE-CODE (implementation), GATE-SPEC (framework-spec change — meta) |
| Layer L1-L10 | SDD layers: L1=BRD, L2=PRD, L3=EARS, L4=BDD, L5=ADR, L6=SPEC, L7=TDD, L8=IPLAN, L9=CHG, L10=EVAL |

## Files

| File | Purpose |
|------|---------|
| `README.md` | This file — layer documentation with all CHG rules |
| `CHG-TEMPLATE.yaml` | Unified CHG template — full authoring guidance with `_guidance`, `_antipatterns`, and structured `creation_checklist` |
| `CHG-00_index.TEMPLATE.md` | Change registry template — tracks all CHG documents per project |
| `gates/` | Gate definitions (GATE-01, 03, 06, 08, CODE, SPEC, error catalog, interaction diagram) |
| `templates/` | Gate approval form and emergency post-mortem companion |

## Cross-References

- `framework/governance/DOC_GOVERNANCE_CORE.md` — Core governance including CHG rules (§CHG Rules)
- `framework/governance/DECISIONS.md` — Durable governance decisions (GD-01: CHG as overlay)
- `docs/sdd/09-CHG/` — Project-level CHG instance documents and archive
