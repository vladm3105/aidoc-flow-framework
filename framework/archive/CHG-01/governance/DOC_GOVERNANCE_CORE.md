# Document Governance — SDD

## Principles

1. **Single source of truth** — Each layer has one template. No duplicate representations.
2. **YAML is the mandatory format and the source of truth** — for **templates and for the instance artifacts authored from them**. Every layer template is `{TYPE}-TEMPLATE.yaml`, and every artifact a layer produces is authored as `.yaml`. **Markdown is optional and descriptive**: a rendering of the YAML, or additional explanatory material around it. Markdown never carries a fact the YAML does not, and a fact that exists only in markdown is a defect of the same class as two records of one count. Where a `.md` file restates YAML content it is **generated, not authored** — hand-editing it is destroyed by the next generation run, and a stale rendering is a drift defect. Scope note: this principle governs the artifacts of layers 1-8 and their templates; it does not govern repository prose (`README`, `CHANGELOG`, governance surfaces such as this file) or a layer's `<X>-00_index.TEMPLATE.*`, whose extension is fixed per layer by `LAYER_REGISTRY.yaml`. **Authority:** the per-layer value is `LAYER_REGISTRY.yaml` `extensions` — the single normative source (GD-17). This principle states the rule; it does not re-specify the per-layer extensions. **Effective condition:** GD-17 states, once, when the instance-format mandate takes normative effect.
3. **Necessary-upstream traceability** — Each layer cites only its `required_tags` (`LAYER_REGISTRY.yaml`), not the cumulative closure of every upstream layer; deeper lineage is transitive.
4. **Readiness gates** — Each layer must score >=90/100 before downstream generation.
5. **No circular dependencies** — Downstream artifacts reference upstream, never the reverse.
6. **Separation of development and deployment** — Development plans produce source code, Terraform modules, Helm charts, CI/CD workflow files, schema DDL, scripts — anything authored, committed, and shipped through version control. Deployment plans handle operator-only execution of those artifacts. A development plan is complete when its artifacts are authored, committed, and green — it does NOT wait for deployment.
7. **Token-efficient authoring** — Documents must be **precise and complete**, not **detailed and exhaustive**. Completeness comes from covering every required template section, not from prose volume. Authoring voice, form preferences, and size targets are defined in [`AUTHORING_STYLE.md`](AUTHORING_STYLE.md); every creation and audit engine loads it alongside the layer template.
8. **Change-of-record discipline** — Every change must keep its documents-of-record in sync within the same PR. A doc-of-record is any document whose content is the durable answer to "what state is the project in" — `CHANGELOG`, `ROADMAP`, `README`, `PARITY`, `TAGGING`, `DECISIONS`, the handoff log, and the project memory (`CLAUDE.md`). No catch-up "doc-refresh" PR may follow a change; the doc updates ship in the change's own PR. Enforcement is two-tier: (a) **mechanical** — version-reference propagation runs automatically on commit (`scripts/sync-version-refs.sh` re-syncs every doc that quotes a `VERSION` file when that file changes); (b) **semantic** — a warning hook (`scripts/check-docs-updated.sh`) flags likely-stale docs when a commit touches code/spec/skills without touching a doc-of-record. The contributor authors the semantic content (changelog entry text, roadmap bullet, decision rationale, handoff narrative); the hook decides whether to remind. See [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md#documentation-discipline--update-docs-of-record-per-pr) §Documentation discipline for the per-change-category matrix.
9. **Example-driven / project-driven framework improvement** — Examples are the system-under-test, and every consumer project applying the framework is an additional empirical test. Friction discovered during use (lint-rule misfires, harness flag absences, engine prose contradicting the spec, sync-script gotchas, missing convenience features) is **NEW knowledge about the framework itself** and is captured immediately, not held in personal memory. The capture mechanism is a two-tier feedback pipeline defined in [`FRAMEWORK_FEEDBACK_LOG.md`](FRAMEWORK_FEEDBACK_LOG.md): (a) **Tier 1 — consumer project** keeps a `framework-feedback-log.md` at project root recording every framework friction it hits; (b) **Tier 2 — framework repo** aggregates onto the framework repo's issue tracker. Without the pipeline, learning evaporates between sessions and the next project rediscovers the same pain. **Issues are the capture and publication surface:** an entry that is actionable by someone other than its finder, reproducible at `file:line` with a fix shape, or user-visible gets an issue on the framework's tracker, linked both ways and closed on the merge SHA.

### Development vs Deployment Plans

Adopted 2026-04-29. Permanent plans split into two roles:

| Role | Owns | Completed when |
| ---- | ---- | --------- |
| **Development plan (IPLAN)** | Source code, Terraform modules, Helm charts, CI/CD workflow files, schema DDL, scripts — anything that gets authored, committed, and shipped through `git push`. | Source code + Terraform modules + CI/CD scripts authored, committed, and green under `pre-commit run --all-files`; tests pass. |
| **Deployment plan** | Operator-only execution of those artifacts: `terraform apply`, `atlas migrate apply`, Auth0 tenant config push, Secret Manager seeding, project provisioning, image build + deploy, environment activation, acceptance/soak runs. | Artifacts applied to the target environment; acceptance/soak gates green. |

**Rule.** A development IPLAN flips to `Completed` once its source code is authored, committed, tests pass, and lint is clean. **It does NOT wait for the artifacts to be deployed.** The deploy execution belongs to a separate deployment plan.

Practical effect:

- An IPLAN's validation_results entry like "ready for deployment provisioning before IMPLEMENTED flip" or "`terraform apply` pending" is **NOT** a gate on the IPLAN's status. Those gates belong on the deployment plan's phase markers.
- An IPLAN that has shipped source code + Terraform module declarations + integration tests **IS** complete from the development side, even if no `terraform apply` has run.
- Conversely, the deployment plan stays `In Progress` until the apply + acceptance steps actually execute against the target environment.

**Cross-plan obligation handoff.** When closing a development IPLAN whose artifacts depend on a deployment-plan apply step, register the obligation in `IPLAN-00_index.yaml` §deferred_items before flipping `Completed`. The IPLAN's status reflects authoring-completion; the registry entry tracks the deploy-side handoff.

## Immutability

- Published artifacts (status: Approved) must not be modified.
- Changes require a new document version or a new document ID.
- Superseded documents are marked as Deprecated/Superseded in document_control.status.

## Template Policy

- **Unified YAML only** — No `.md` templates, no `.feature` templates. This bullet
  governs **templates**; Principle 2 governs the instance artifacts authored from
  them. Both mandate YAML — read Principle 2 before concluding that a layer's
  instance format is unconstrained. The per-layer value is `../registry/LAYER_REGISTRY.yaml`
  `extensions` — the single normative source (GD-17); this bullet does not re-specify it.
- Each layer has exactly one `{TYPE}-TEMPLATE.yaml`.
- Template fields use `_guidance` prefix for authoring instructions (not validated).
- Metadata block (`metadata:`) defines layer, schema version, and document type.

## Validation

- Layer entries must validate against `LAYER_REGISTRY.yaml`.
- Required upstream tags must be present in traceability sections.
- Element IDs must match the 4-segment hash format: `TYPE.NN.SS.xxxx`.
- Document IDs must match the format: `TYPE-NN`.

## Security

- Artifacts are agent-authored from inputs the agent does not control. Every
  agent-authored artifact passes the `SECURITY_REVIEW.md` checks — no embedded
  secrets, no instruction obeyed from external/untrusted content, traceable
  provenance for promotions, and sanitized active content. A failed check is a
  blocking finding, not a score deduction.

## Governance Baseline

| Governance Area | Standard |
|----|------|
| Layer registry | 10-layer registry |
| Lifecycle status field | `status` |
| Template format | YAML-only templates |
| Traceability depth | 8-depth chain |
| Specification and testing | Unified SPEC (L6) + TDD with embedded test cases (L7) |
| Change governance | CHG project-level overlay |

---

## Version Bumping

When a document is rewritten via a CHG record:
1. Bump `document_control.version` (1.0 → 2.0 → 3.0, etc.)
2. Update `document_control.last_updated` to the CHG date
3. Archive the previous version to `docs/sdd/09-CHG/archive/{CHG-ID}/{layer}/`
4. Record the archive path in the CHG's `supersedes` field
5. Keep the same document ID (e.g., SPEC-01 stays SPEC-01 across versions)
6. The rewritten document must be a clean, self-contained version — no appendices, no "added by CHG-XX" annotations, no stale content from previous versions
7. Set `metadata.framework_version` to the current `framework/VERSION` — this records which spec version the document was authored against

### Framework version tracking (software versioning)

Every SDD document records the framework version it was created under via
`metadata.framework_version`. This is the document's "build dependency" — the
same pattern software uses for lock files. When the framework bumps, existing
documents are **not** retroactively updated. Instead:

| Document state | Action |
|---------------|--------|
| Created under current version | No action needed |
| Created under older version, not touched by a CHG | No action needed — the document is valid under its recorded version |
| Touched by a CHG that also bumps the framework | The CHG's `version_action` field decides: `upgrade` (rewrite metadata to new version) or `keep` (schema is compatible) |
| New document created after a framework bump | Must use the current `framework/VERSION` |

**When to set `version_action`:** Only when the CHG touches a document whose
`framework_version` is older than the current `framework/VERSION`. If all
documents in the CHG are already on the current version, leave `version_action`
null.

**Conformance stays per-platform, not per-document.** `GATE-SPEC-E006` continues
to check that both `FRAMEWORK_SPEC_VERSION` pins match `framework/VERSION`. The
per-document `framework_version` is an audit trail — it answers "which version
was this document authored against?" without branching the conformance suite.

---

## SDD Document Management Rules

### Active SDD location
Active SDD documents are in `docs/sdd/`. The `sdd_archived/` directory contains
broader-product archived docs. Always reference active SDD first.

### SDD document versioning — clean rewrites with archival
When an SDD document needs updating, archive the previous version to
`docs/sdd/09-CHG/archive/{CHG-ID}/{layer}/`, then rewrite the document in place
as a clean, self-contained new version.

Each CHG record owns its archive — the directory structure mirrors the SDD layer
hierarchy (06_SPEC, 07_TDD, 08_IPLAN). Never append to existing docs — no
"addendum" sections, no "NOTE: added by CHG-XX" annotations, no growing
appendices. The current docs directory always reflects the latest truth. CHG
records the change (via `supersedes` field pointing to archive paths), documents
record the current state.

### No stale context in SDD docs
Remove stale content when rewriting. Don't keep unused sections, duplicate
entries, or references to retired approaches. A v2 document should read as if it
were written from scratch with current knowledge.

### CHG archive convention
Archive path is always `docs/sdd/09-CHG/archive/{CHG-ID}/{layer}/` where layer
is one of `06_SPEC`, `07_TDD`, `08_IPLAN`.

The CHG's `supersedes` field lists each archived document with its full archive
path in parentheses. This makes the archive self-describing — looking at any CHG
tells you exactly what it superseded and where the previous versions live. Never
use date-based archive paths.

### IPLAN version tracking
When rewriting an IPLAN as v2, bump `document_control.version` to `2.0` and
update `last_updated`. The CHG `supersedes` field records which version was
replaced. Keep the same IPLAN ID (e.g., IPLAN-01 stays IPLAN-01 across versions).

### SPEC/TDD version tracking
Same pattern — bump `document_control.version` to `2.0`, update `last_updated`.
CHG `supersedes` records the replacement. Keep same document IDs.

---

## CHG (Change Record) Rules

### C3 gate approval for solo projects
For solo-maintained projects, C3 CHGs are self-approved by the project owner
(technical lead). The approval is recorded in the CHG's `gate_approval` section
with `approver: "Self (C3 — Technical Lead)"`. This is consistent with the
framework's human-in-the-loop tier where routine work only needs escalation on
iteration cap. The project owner is always the human approver for C3 changes.

### Mandatory SDD sync on IPLAN completion
When an IPLAN is marked `Completed`, the corresponding SPEC and TDD documents
MUST be updated to reflect what was actually built — not what was originally
planned. If the implementation diverged from the spec (e.g., stubs replaced with
real API calls, new interfaces added, test cases added), a CHG must be created
and the SPEC/TDD rewritten as a new version.

The IPLAN status change and the SPEC/TDD update must ship in the same change.
This prevents doc drift — the SDD docs must always be the current source of
truth without requiring codebase comparison. Enforced by: no IPLAN may flip to
`Completed` without a corresponding SPEC/TDD version check.

### CHG status lifecycle (mandatory)

Every CHG document MUST track its status through the full lifecycle. Status
changes are **not optional** — they are the mechanism that allows stopping and
resuming implementation without rescanning the codebase. An agent or human
picking up a CHG reads the status field to know exactly where work left off.

**Required status transitions:**

| Status | When | What to update |
|--------|------|----------------|
| `Proposed` | CHG created | `date_proposed`, all issues `status: Proposed` |
| `Approved` | Gate passed (GATE-08 or self-approval for C3) | `date_approved`, `change_control.status: Approved` |
| `In-Progress` | Implementation started | `change_control.status: In-Progress`, each issue transitions to `In-Progress` as work begins on it |
| `Implemented` | All issues implemented and merged | `date_implemented`, `change_control.status: Implemented`, all issues `status: Implemented` |
| `Completed` | SDD docs updated, verification passed | `change_control.status: Completed` |

**Rules:**
1. **Status must never regress.** A CHG cannot move from `Implemented` back to
   `In-Progress`. If rework is needed, create a new CHG or add a rework note.
2. **Issue-level statuses must match the CHG status.** When the CHG is
   `Implemented`, every issue must be `Implemented` or `Skipped` (with
   justification). No issue may remain `Proposed` when the CHG is `Implemented`.
3. **Status transitions ship in the same change.** Updating status from
   `Proposed` to `Implemented` must be in the same commit/PR as the
   implementation, or as an immediate follow-up. Stale statuses violate the
   contract.
4. **`In-Progress` enables resumption.** If work stops mid-implementation, the
   CHG stays `In-Progress` with completed issues marked `Implemented` and the
   next issue marked `In-Progress`. The next agent reads the CHG and knows
   exactly which issue to pick up.
5. **`Implemented` ≠ `Completed`.** `Implemented` means code is merged.
   `Completed` means SDD docs are updated, verification passed, and the CHG is
   fully closed. The gap between them is where doc drift happens — §3.2
   enforces the SDD sync.

Enforced by: agents MUST check `change_control.status` before starting work on
a CHG. If status is `Completed`, do not re-implement. If status is
`Implemented`, check SDD docs before declaring done.

### CHG creation checklist

Before writing any CHG document, complete this checklist. Each item maps to a
gap class found in CHG post-creation reviews. Items 11-12 were added after
CHG-04 was found missing SDD document lifecycle steps. Items 13-14 were added
after CHG-04 was found having wrong implementation ordering.

**MANDATORY PROCESS GATE**: This checklist is a **blocking prerequisite**, not
post-hoc validation. The agent MUST read and complete every item BEFORE writing
the CHG document. The "write before read" pattern (writing CHG/IPLAN from issue
descriptions without consulting governance rules) has caused repeated failures
(CHG-04: 16 gaps, CHG-06: 3 bugs). The checklist exists to prevent these
failures — reading it after writing defeats its purpose. Added after CHG-06
violated items 11-14 (the exact items added after CHG-04 to prevent these
failures).

| # | Check | Gap it prevents |
|---|-------|-----------------|
| 1 | **Read every file you reference** — open each artifact path in `artifacts_modified` and verify it exists, note the actual filename, and read the relevant code sections. Never write an implementation step referencing a file you haven't opened. | Wrong filenames, wrong line numbers, wrong function signatures |
| 2 | **Verify the architectural claim** — for each issue, confirm whether the problem is client-side, server-side, or both. | Mischaracterized architecture |
| 3 | **Check existing struct/type signatures** — if your fix requires passing new data, verify the existing struct accepts those fields. | Claims struct has no field when it does |
| 4 | **Check existing INSERT/SELECT queries** — if your fix adds columns to a table, verify existing queries that touch that table. | Adding columns without updating existing queries |
| 5 | **Cross-reference upstream requirements** — cite specific EARS requirement IDs and BDD scenario IDs that your CHG addresses. | No traceability in CHG |
| 6 | **Check for existing handlers/webhooks** — if your fix involves user creation or data population, check if a webhook handler already exists for that event type. | Existing handler not considered |
| 7 | **Couple dependent issues** — if two issues share a fix, implement them together, not as separate steps. | Coupled issues implemented separately |
| 8 | **Add automated test specifications** — for each implementation step, specify the test file, test name, and assertion method. Manual checks alone are insufficient. | No automated test specs |
| 9 | **Verify the fix location** — if error handling is needed, check whether the error is thrown in the function or in the caller. | Wrong fix location |
| 10 | **Add DB migration + rollback** — if adding columns, provide the full migration SQL, rollback SQL, backfill strategy, and indexes. | Migration without rollback |
| 11 | **Plan SDD document versioning** — if the CHG modifies any SDD document, add steps for archive → rewrite → supersedes → version bump. | No SDD lifecycle steps |
| 12 | **Check traceability to SDD lifecycle rules** — verify this document's §SDD Document Management and §CHG Rules are satisfied. | Rules not enforced at creation time |
| 13 | **SDD-first implementation order** — SDD document updates MUST appear BEFORE any code implementation steps. | Wrong ordering |
| 14 | **CHG scope: governance, not implementation plan** — the CHG authorizes and scopes the change. Code steps belong in the IPLAN. | Detailed code steps in CHG |

### IPLAN file_manifest accuracy
When an IPLAN is marked `Completed`, every file in its `file_manifest` with
`status: DONE` must actually exist on disk and contain a real implementation
(not a stub/mock). The iplan-executor agent defect (2026-08-30) proved this
gap: files were marked DONE but contained stubs.

Verification: `grep -c 'TODO\|stub\|mock\|hardcoded' <file>` should return 0
for DONE files.

---

## Status Propagation Rules

### Upstream status propagation on downstream layer start
When a downstream SDD layer document is started, the upstream document's status
MUST be updated to "Approved". Do not start the next layer if its upstream is
not approved.

**Propagation chain:**
- Seed doc status → "Approved" when module doc generation starts
- Module doc status → "Approved" when its BRD layer starts
- BRD doc status → "Approved" when its PRD layer starts

This ensures the SDD chain reflects authoring progress — a Draft upstream means
its downstream hasn't been started yet.

**ADR convention:** ADRs use "Accepted" (not "Approved") as their terminal
status.

---

## Decision Workflow Rules

See [DECISION_WORKFLOW.md](DECISION_WORKFLOW.md) for the full specification.

**Summary:**
- Seed docs (architect): suggestions, 2-3 options, principles
- Module docs (product owner): ALL source material, single source of truth
- SDD ADRs (dev team): ONE selected architecture
- No separate seed ADR files
- SDD ADR selects, doesn't re-survey

---

## Unified Flow — One SDD chain, two initiators

The SDD chain is always the execution model:

```
Seed → Module → BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code
```

The chain is initiated by one of two sources:

| Initiator | When | What it triggers |
|-----------|------|-----------------|
| **Modules/seed** | New feature, first time | Full SDD chain from seed through IPLAN |
| **CHG request** | All changes (modification, rewrite, bugfix) | Same SDD chain for affected layers (archive old → rewrite as v2) |

**CHG is the single entry point for all changes.** Every modification to existing SDD documents goes through a CHG. The CHG lists tasks (which layers need to be generated or rewritten), and the SDD chain executes them.

**CHG governs:**
- New feature: CHG lists all 8 SDD layers as tasks
- Modification: CHG lists only affected layers, archives old versions, rewrites as v2
- Seed gap: CHG lists missing seed docs + affected SDD layers for regeneration
- Bugfix: CHG lists affected layers, archives old versions, rewrites as needed

**Rule:** The SDD chain is always the execution model. For new features, modules/seed initiate the chain. For all changes, CHG is the single entry point that initiates the chain.

---

## Document Status Lifecycle

### Document Status Enum

Every SDD document has exactly one document-level status. The valid values are:

| Status | Meaning | Applies to |
|--------|---------|-----------|
| `Draft` | Document being authored or not yet approved | All layers |
| `Approved` | Document reviewed, approved for next layer or implementation | BRD, PRD, EARS, BDD, SPEC, TDD, IPLAN |
| `Accepted` | ADR architecture decision accepted (not "Approved") | ADR only |
| `Completed` | Implementation complete, tests passing, code verified | TDD, IPLAN only |

**Rules:**
- Status transitions are forward-only within a session (no reverting Approved → Draft)
- Exception: A CHG rewrite archives the old doc and creates a new Draft
- "Completed" is for TDD and IPLAN only — all other layers use "Approved" as their terminal status
- Do NOT use "Completed" for BRD, PRD, EARS, BDD, or SPEC

### Terminal Status per Layer

| Layer | Terminal Status | Trigger |
|-------|----------------|---------|
| BRD | Approved | When PRD starts |
| PRD | Approved | When EARS starts |
| EARS | Approved | When BDD starts |
| BDD | Approved | When ADR starts |
| ADR | Accepted | When SPEC starts |
| SPEC | Approved | When TDD starts |
| TDD | Approved → **Completed** | Approved when IPLAN starts; Completed when implementation verified |
| IPLAN | Approved → **Completed** | Approved when implementation starts; Completed when code green + tests pass |

**Note on TDD/IPLAN "Completed":** After implementation completes, update TDD status to "Completed" (all tests passing, coverage met) and IPLAN status to "Completed" (all files implemented, stub detection clean). This signals the SDD chain is fully consumed for that module.

---

## Status Propagation Enforcement

Before starting any downstream SDD layer, verify and update upstream status per §Status Propagation Rules:

- When PRD layer starts → all upstream BRDs MUST be "Approved" (not "Draft")
- When EARS layer starts → all upstream PRDs MUST be "Approved"
- When BDD layer starts → all upstream EARS MUST be "Approved"
- When ADR layer starts → all upstream BDD MUST be "Approved"
- When SPEC layer starts → all upstream ADR MUST be "Accepted"
- When TDD layer starts → all upstream SPEC MUST be "Approved"
- When IPLAN layer starts → all upstream TDD MUST be "Approved"
- After implementation completes → TDD and IPLAN updated to "Completed" (§Terminal Status per Layer)
- Update both the YAML `document_control.status` field AND the layer index file
