# Project Governance Rules

**Status:** Approved · **Date:** 2026-10-23 (updated)
**Scope:** Hard constraints that every session must respect

---

## 1. Infrastructure Rules

### 1.1 Debian-based Docker images
User specified Docker containers should run on Debian, not Alpine. All Dockerfiles must use `debian:bookworm-slim` (runtime) and `golang:1.25-bookworm` (builder).

### 1.2 Atlas for database migrations
Use Atlas (ariga.io/atlas) for database schema migrations, not raw SQL scripts. Supersedes any prior plan referencing `scripts/migrations/*.sql`.

### 1.3 Atlas declarative mode
Use `atlas schema apply --to "file:///migrations/schema.hcl"` (declarative), NOT `atlas migrate apply` (versioned SQL). The project uses `schema.hcl` only, no numbered SQL files.

### 1.4 Docker environment variable binding
When updating docker-compose.yml to bind services to a specific host IP (e.g., LAN IP `192.168.86.174`), environment variables for bind addresses (e.g., `ADMIN_BIND`) must remain `0.0.0.0` inside the container. The host-side port mapping (e.g., `192.168.86.174:18081:8081`) handles the IP restriction. Setting bind addresses to the host IP inside the container causes `bind: cannot assign requested address` because that IP doesn't exist inside the container network namespace.

Added after backend crash caused by setting `ADMIN_BIND: "192.168.86.174"` (2026-09-06).

### 1.5 Multi-port Nginx reverse proxy configuration
When a Docker container serves both HTTP and HTTPS (e.g., ports 8080 and 443), reverse proxy blocks (such as `location /v1/ { proxy_pass http://backend:8080; ... }`) must be explicitly declared in both the plain HTTP and the SSL `server` blocks. Omitting proxy definitions from the SSL block causes HTTPS clients to fall through to `try_files` and receive 404 HTML responses for API calls.

Added after cabinet SSL proxy gap resolved (2026-09-14, CHG-21).

---

### CI gate reusables: same-repo only (added after #360/CHG-29, 2026-09-16)
- PR-gate workflows SHALL call reusable workflows exclusively from this repository (`.github/workflows/local-*.yml`, provenance-stamped copies of `vladm3105/aidoc-flow-ci` bodies). Cross-repo private reusables do not load on `pull_request`/`pull_request_target`/`push`/`dispatch` events for this user-owned consumer; only `workflow_run`/`pull_request_review` callers (composition, auto-merge) are exempt because they demonstrably work.
- Every required/registered gate MUST appear in `gate-doctor.yml`'s roll list at creation (EARS.11.03.g5h7); zero-job load failures are forensically silent and must be detected actively, never assumed healthy.
- Vendored bodies resync on canon release updates (keep the provenance header's source SHA/current); PRT-triggered flips verify on the FIRST POST-MERGE PR, not the flip PR itself.

## 2. SDD Document Management Rules

### 2.1 Active SDD location
Active SDD documents are in `docs/sdd/`. The `sdd_archived/` directory contains broader-product archived docs. Always reference active SDD first.

**Next available SDD IDs:** BRD-10, PRD-10, EARS-10, BDD-10, ADR-10, SPEC-10, TDD-10, IPLAN-21, CHG-11. (CHG-10 In-Progress: local-first user architecture refactor — had §3.3/§3.1.1 violations, remediated in-place. IPLAN-20 created.)

### 2.2 SDD document versioning — clean rewrites with archival
When an SDD document needs updating, archive the previous version to `docs/sdd/09-CHG/archive/{CHG-ID}/{layer}/` (e.g., `docs/sdd/09-CHG/archive/CHG-02/06_SPEC/SPEC-01.yaml`), then rewrite the document in place as a clean, self-contained new version.

Each CHG record owns its archive — the directory structure mirrors the SDD layer hierarchy (06_SPEC, 07_TDD, 08_IPLAN). Never append to existing docs — no "addendum" sections, no "NOTE: added by CHG-XX" annotations, no growing appendices. The current docs directory always reflects the latest truth. CHG records the change (via `supersedes` field pointing to archive paths), documents record the current state. Previous versions are recoverable from the CHG's archive directory.

### 2.3 No stale context in SDD docs
Remove stale content when rewriting. Don't keep unused sections, duplicate entries, or references to retired approaches. A v2 document should read as if it were written from scratch with current knowledge. Clean up file_manifest duplicates, remove dead references, fix naming mismatches between signatures and data models.

### 2.4 CHG archive convention
Archive path is always `docs/sdd/09-CHG/archive/{CHG-ID}/{layer}/` where layer is one of `06_SPEC`, `07_TDD`, `08_IPLAN`.

The CHG's `supersedes` field lists each archived document with its full archive path in parentheses. This makes the archive self-describing — looking at any CHG tells you exactly what it superseded and where the previous versions live. Never use date-based archive paths.

### 2.5 IPLAN version tracking
When rewriting an IPLAN as v2, bump `document_control.version` to `2.0` and update `last_updated`. The CHG `supersedes` field records which version was replaced. Keep the same IPLAN ID (e.g., IPLAN-01 stays IPLAN-01 across versions).

### 2.6 SPEC/TDD version tracking
Same pattern — bump `document_control.version` to `2.0`, update `last_updated`. CHG `supersedes` records the replacement. Keep same document IDs.

### 2.7 New layer registration (mandatory)
When creating a new framework layer, it MUST be registered in `.aidoc/framework/registry/LAYER_REGISTRY.yaml` before any layer documents are authored. The registration entry must include: `number`, `artifact`, `name`, `folder`, `extensions`, `required_tags`, `can_reference`, `error_prefix`, `optional`, `description`, `template`, `downstream`. Additionally:
- Update `total_layers` in metadata
- Add the layer to `layer_groups`
- Add to `realizing_layers` if the layer realizes upstream elements
- Add to `c4_mapping` if applicable
- Update upstream layers' `downstream` fields to include the new layer
- Update `CLAUDE.md` layer citation table
- Update `.aidoc/framework/governance/LINT_RULES.md` with any new lint rule IDs referenced by the template

Added after EVAL (L10) was found unregistered in LAYER_REGISTRY.yaml (2026-10-06).

---

## 3. CHG (Change Record) Rules

### 3.1 C3 gate approval for solo projects
For solo-maintained projects, C3 CHGs are self-approved by the project owner (technical lead). The approval is recorded in the CHG's `gate_approval` section with `approver: "Self (C3 — Technical Lead)"`. This is consistent with the framework's human-in-the-loop tier where routine work only needs escalation on iteration cap. The project owner is always the human approver for C3 changes.

### 3.1.1 MANDATORY: SDD-First Implementation Order (NON-NEGOTIABLE)

**This rule has been violated 4 times (CHG-04, CHG-06, CHG-08, CHG-10). Violations require immediate correction.**

When a CHG modifies SDD documents, the **FIRST** implementation steps **MUST** be SDD document updates. The correct flow is:

```
CHG (authorize only)
  ↓
Phase 0: SDD Document Updates (FIRST — MANDATORY)
  1. Archive current versions to docs/sdd/09-CHG/archive/{CHG-ID}/{layer}/
  2. Rewrite each SDD document as clean v2 (upper layers first: PRD → SPEC → IPLAN)
  3. Update supersedes field with archive paths
  4. Bump document_control.version to 2.0
  ↓
Phase 1: IPLAN Creation/Update (AFTER SDD docs exist)
  5. Create or update IPLAN with ALL code implementation steps
     - The IPLAN MUST reference the NEW SDD document versions
  ↓
Phase 2: Code Implementation (driven by IPLAN)
  6. Implement code per IPLAN specifications
```

**CRITICAL RULES:**
- Code implementation steps belong in IPLAN, NOT in CHG
- SDD updates MUST happen BEFORE IPLAN creation (not "deferred")
- The IPLAN MUST reference the NEW (updated) SDD versions
- If SDD updates are "deferred", the CHG is INCORRECT
- **No code may be written without an approved IPLAN (IPLAN Gate — see §3.13)**

**What Goes Where:**

| Document | Contains | Does NOT Contain |
|----------|----------|------------------|
| **CHG** | Authorization, scope, SDD lifecycle steps (archive/rewrite/version bump), IPLAN creation/update | Detailed code implementation steps |
| **IPLAN** | All code implementation steps, file manifest, execution commands, test cases | SDD document lifecycle (that's CHG's job) |
| **SDD Documents** | Current requirements, specs, test definitions | Implementation details (that's IPLAN's job) |

**Violations (for reference):**
- CHG-04: Code steps first (Steps 1-10), SDD updates last (Step 11)
- CHG-06: Skipped SDD chain audit, created IPLAN directly
- CHG-08: 18 code steps in CHG, SDD updates marked "Deferred"
- CHG-10: Code implemented before IPLAN existed, IPLAN created retroactively

### 3.1.2 Backward Propagation / Code-to-Doc Reconciliation Flow (Type-R / Reverse Engineering CHG)

**Purpose & Scope:**
When code modifications or test suites originate empirically — such as during live sandbox provider integration discovery (e.g. Privy/Bridge APIs), live interactive browser test authoring (Playwright E2E suites), critical test flakiness remediation, or emergency operational bugfixes — the codebase state temporarily precedes the written specifications.

To eliminate **code drift vs. documentation** without fabricating a fictional "design-first" chronology, the framework formalizes **Type-R (Reconciliation / Backward Propagation)** change requests.

**Type-R Workflow & Order (Mandatory):**

```
Verified Working Codebase (All Tests Pass, 0 Secret Findings, Clean Boundaries)
  ↓
Phase 0: Codebase Freeze & Manifest Extraction
  1. Freeze and verify code changes (ensure 100% test pass: go test, npm run verify:product, playwright).
  2. Extract exact modified file paths, methods, schemas, configuration keys, and test commands.
  ↓
Phase 1: Reverse-Engineered IPLAN Authoring (Ground Truth from Code)
  3. Author IPLAN reflecting the verified code reality, exact file manifests, and test suites.
  4. IPLAN documents the empirical findings and serves as the bridge between code and SDD.
  ↓
Phase 2: Upstream SDD Layer Reconciliation (Code → TDD → SPEC → BDD → EARS)
  5. Update Layer 7 TDD test suites with new assertions, test cases, and coverage standards.
  6. Update Layer 6 SPEC interface signatures, data models, and constraints.
  7. Update Layer 4 BDD feature behaviors and scenarios.
  8. Update Layer 3 EARS requirements.
  9. Refresh all layer master index ledgers (IPLAN-00, TDD-00, SPEC-00, BDD-00, EARS-00).
  ↓
Phase 3: Core Project Documentation Reconciliation
  10. Update user journey specifications (e.g. USER_JOURNEYS.md), testing strategy guidance, and agent operational rules.
  ↓
Phase 4: Bi-directional Verification Gate
  11. Execute chg_lint.py, unit tests, E2E journey tests, boundary checks, and secret scans.
```

**Guardrails for Type-R CHGs:**
1. `change_source` in CHG metadata must be `reconciliation` (or `backward_propagation`).
2. Codebase must pass all verification gates BEFORE initiating backward documentation propagation.
3. No new unverified code may be introduced during the documentation reconciliation phase.

### 3.13 IPLAN Gate (HARD BLOCK — NON-NEGOTIABLE)

**No code may be written without an IPLAN authorizing the changes.**

This is a HARD BLOCK that supersedes all other instructions. Before ANY write/edit call to code files (`*.go`, `*.py`, `*.js`, `*.ts`) or governance files (`*.yaml` SDD, `*.md` governance):

**Pre-write verification (MANDATORY):**

1. [ ] An IPLAN exists in `docs/sdd/08_IPLAN/` for this work
2. [ ] The IPLAN status is `In Progress` (not `Draft`, `Approved`, or `Completed`)
3. [ ] The IPLAN's `source_chg` references the CHG authorizing this work
4. [ ] The files you're about to modify are listed in the IPLAN's `file_manifest`
5. [ ] The CHG status is `In-Progress` or `Implemented` (not `Proposed`)

**If ANY check fails: STOP. Do not write code. Fix the governance gap first.**

**Enforcement mechanism:**
- Session-start verification in CLAUDE.md checks IPLAN status before any work
- Agents MUST NOT bypass this gate — no exceptions for "quick fixes" or "small changes"
- The only exception: bug fixes on active IPLANs may skip CHG creation but MUST verify IPLAN status

**Violation log:** CHG-10 had code implemented before IPLAN existed (2026-11-06). Code was written directly, then IPLAN-20 was created retroactively. This violates §3.1.1 Phase 2 which requires IPLAN before code. Remediated by creating IPLAN-20 and updating governance. This gate prevents recurrence.

**Automated enforcement:** Run `python scripts/chg_lint.py <chg-file.yaml>` to validate CHG governance before implementation. The linter checks:
- CHG-L001: Status lifecycle (§3.3)
- CHG-L002: Gate approval (§3.1)
- CHG-L003: CHG scope (§3.4 items 13-14)
- CHG-L004: IPLAN reference (§3.1.1)
- CHG-L005: SDD-first order (§3.1.1)

**Related rules:**
- §3.1.1: SDD-First Implementation Order
- §3.3: CHG status lifecycle
- §3.4 items 13-14: CHG scope (no code steps in CHG)
- CLAUDE.md: Session-Start Verification + IPLAN Gate

### 3.2 Mandatory SDD sync on IPLAN completion
When an IPLAN is marked `Completed`, the corresponding SPEC and TDD documents MUST be updated to reflect what was actually built — not what was originally planned. If the implementation diverged from the spec (e.g., stubs replaced with real API calls, new interfaces added, test cases added), a CHG must be created and the SPEC/TDD rewritten as a new version.

The IPLAN status change and the SPEC/TDD update must ship in the same change. This prevents doc drift — the SDD docs must always be the current source of truth without requiring codebase comparison. Enforced by: no IPLAN may flip to `Completed` without a corresponding SPEC/TDD version check.

### 3.3 CHG status lifecycle (mandatory)

Every CHG document MUST track its status through the full lifecycle. Status changes are **not optional** — they are the mechanism that allows stopping and resuming implementation without rescanning the codebase. An agent or human picking up a CHG reads the status field to know exactly where work left off.

**Required status transitions:**

| Status | When | What to update |
|--------|------|----------------|
| `Proposed` | CHG created | `date_proposed`, all issues `status: Proposed` |
| `Approved` | Gate passed (GATE-08 or self-approval for C3) | `date_approved`, `change_control.status: Approved` |
| `In-Progress` | Implementation started | `change_control.status: In-Progress`, each issue transitions to `In-Progress` as work begins on it |
| `Implemented` | All issues implemented and merged | `date_implemented`, `change_control.status: Implemented`, all issues `status: Implemented` |
| `Completed` | SDD docs updated, verification passed | `change_control.status: Completed` |

**Rules:**
1. **Status must never regress.** A CHG cannot move from `Implemented` back to `In-Progress`. If rework is needed, create a new CHG or add a rework note.
2. **Issue-level statuses must match the CHG status.** When the CHG is `Implemented`, every issue must be `Implemented` or `Skipped` (with justification). No issue may remain `Proposed` when the CHG is `Implemented`.
3. **Status transitions ship in the same change.** Updating status from `Proposed` to `Implemented` must be in the same commit/PR as the implementation, or as an immediate follow-up. Stale statuses violate the contract.
4. **`In-Progress` enables resumption.** If work stops mid-implementation, the CHG stays `In-Progress` with completed issues marked `Implemented` and the next issue marked `In-Progress`. The next agent reads the CHG and knows exactly which issue to pick up.
5. **`Implemented` ≠ `Completed`.** `Implemented` means code is merged. `Completed` means SDD docs are updated, verification passed, and the CHG is fully closed. The gap between them is where doc drift happens — §3.2 enforces the SDD sync.
6. **No skipping lifecycle stages.** A CHG MUST NOT jump from `Proposed` directly to `Implemented`. The `Approved` stage is a mandatory gate — it records that the change was authorized before implementation began. Skipping `Approved` means implementation started without authorization.

Enforced by: agents MUST check `change_control.status` before starting work on a CHG. If status is `Completed`, do not re-implement. If status is `Implemented`, check SDD docs before declaring done.

**Violation log:** CHG-10 jumped from `Proposed` to `Implemented` without `Approved` stage. Gate approval was `null`. Remediated in-place (2026-11-06).

**Automated enforcement:** Run `python scripts/chg_lint.py <chg-file.yaml>` to validate status lifecycle and other governance rules. The linter checks:
- CHG-L001 / GOV-011: Status lifecycle (§3.3)
- CHG-L002 / GOV-012: Gate approval (§3.1)
- CHG-L003 / GOV-013: CHG scope (§3.4 items 13-14)
- CHG-L004: IPLAN reference (§3.1.1)
- CHG-L005: SDD-first order (§3.1.1)

### 3.4 CHG creation checklist

**BLOCKING GATE — NOT ADVISORY.**

Before writing any CHG document, complete this checklist. Each item maps to a gap class found in CHG-04 review or post-creation gap analysis. Items 11-12 were added after CHG-04 was found missing SDD document lifecycle steps. Items 13-14 were added after CHG-04 was found having wrong implementation ordering.

**MANDATORY PROCESS GATE**: This checklist is a **blocking prerequisite**, not post-hoc validation. The agent MUST read and complete every item BEFORE writing the CHG document. The "write before read" pattern (writing CHG/IPLAN from issue descriptions without consulting governance rules) has caused gaps in CHG-04 (16 gaps) and CHG-06 (3 bugs). The checklist exists to prevent these failures — reading it after writing defeats its purpose.

**Enforcement:** The session-start verification in CLAUDE.md and the governance-gate skill enforce this gate. Violations are recorded in the self-learn system and trigger retroactive governance.

| # | Check | Gap it prevents |
|---|-------|-----------------|
| 1 | **Read every file you reference** — open each artifact path in `artifacts_modified` and verify it exists, note the actual filename, and read the relevant code sections. Never write an implementation step referencing a file you haven't opened. | Wrong filenames (bootstrap.go vs profile_bootstrap.go), wrong line numbers, wrong function signatures |
| 2 | **Verify the architectural claim** — for each issue, confirm whether the problem is client-side, server-side, or both. Check if the method/endpoint/port actually exists in the codebase before proposing a fix. | auth.signup mischaracterized as server port when it's a client contract method |
| 3 | **Check existing struct/type signatures** — if your fix requires passing new data (e.g., email, name), verify the existing struct accepts those fields. If not, add a step to extend the struct. | Claims struct has no email/name, BeeLocalProfile has no email_verified_at |
| 4 | **Check existing INSERT/SELECT queries** — if your fix adds columns to a table, verify existing queries in the codebase that touch that table. Note which queries need updating. | INSERT INTO users only has 3 columns, adding 7 more requires updating the INSERT |
| 5 | **Cross-reference upstream requirements** — cite specific EARS requirement IDs and BDD scenario IDs that your CHG addresses. If modifying PRD/SPEC, note which sections change. | No EARS/BDD traceability in CHG-04 |
| 6 | **Check for existing handlers/webhooks** — if your fix involves user creation or data population, check if a webhook handler already exists for that event type. | Privy user.creation webhook already exists but wasn't considered |
| 7 | **Couple dependent issues** — if two issues share a fix (e.g., first-time detection needs onboarded_at column), implement them together, not as separate steps. | Issue 5 (first-time detection) and Issue 10 (onboarded_at) were separate |
| 8 | **Add automated test specifications** — for each implementation step, specify the test file, test name, and assertion method. Manual checks alone are insufficient. | CHG-04 had 10 manual checks but zero automated test specs |
| 9 | **Verify the fix location** — if error handling is needed, check whether the error is thrown in the function or in the caller. Put the try/catch where the call happens, not inside the function. | Issue 9 put try/catch in auth.js instead of demo-auth.js (the caller) |
| 10 | **Add DB migration + rollback** — if adding columns, provide the full migration SQL, the rollback SQL, a backfill strategy for existing rows, and any index additions. | CHG-04 listed ALTER TABLE but no rollback, no backfill, no indexes |
| 11 | **Plan SDD document versioning** — if the CHG modifies any SDD document (PRD, SPEC, IPLAN, etc.), add implementation steps to: (a) archive current versions to `docs/sdd/09-CHG/archive/{CHG-ID}/{layer}/`, (b) rewrite each document as a clean v2, (c) update the CHG `supersedes` field with archive paths, (d) bump `document_control.version` for IPLAN/SPEC/TDD. §2.2-2.6 governs this. | CHG-04 listed PRD-02/SPEC-02/IPLAN-12 in `artifacts_modified` but had no implementation step for archiving or rewriting them |
| 12 | **Check traceability to SDD lifecycle rules** — before finalizing the CHG, verify that `docs/governance/GOVERNANCE_RULES.md` §2.2-2.6 (SDD document management) and §3.2 (mandatory SDD sync) are satisfied. Cross-reference each SDD-modifying step against the versioning, archival, and clean-rewrite requirements. | Rules exist but were not enforced at creation time because the checklist didn't reference them |
| 13 | **SDD-first implementation order** — when a CHG modifies SDD documents, the FIRST implementation steps MUST be SDD document updates (PRD → SPEC → IPLAN), appearing BEFORE any code implementation steps. The CHG is a governance record, not an implementation plan. Code steps belong in the IPLAN, not in the CHG. The correct flow: CHG → SDD docs first → create/update IPLAN with all code steps → implement from IPLAN. | CHG-04 had code steps first (Steps 1-10) and SDD updates last (Step 11), violating the SDD chain direction |
| 14 | **CHG scope: governance, not implementation plan** — the CHG's `implementation.steps` should contain: (a) SDD document lifecycle steps (archive → rewrite → supersedes → version bump), and (b) IPLAN creation/update with all code steps. The CHG should NOT contain detailed code implementation steps directly. The IPLAN is the execution artifact; the CHG authorizes and scopes the change. | CHG-04 listed 12 detailed code steps (DB migration, middleware fix, frontend changes) in the CHG itself instead of deferring to IPLAN-12 |

### 3.4.1 CHG Post-Creation Validation (MANDATORY)

After creating a CHG document, verify EVERY item before committing. This catches errors introduced during CHG authoring — even when §3.4 was followed. Added after CHG-09 contained wrong traceability references and incomplete SDD lifecycle plans despite the §3.4 checklist existing.

**Gate:** ALL checks pass → commit. ANY check fails → fix, re-validate, then commit.

| # | Check | Gap it prevents |
|---|-------|-----------------|
| A1 | `id` matches filename | Mismatched CHG ID |
| A2 | `document_control.status` is `Proposed` | Wrong initial status |
| A3 | `change_control.chg_id` matches `id` | Mismatched IDs |
| A4 | `metadata.last_updated` matches today | Stale timestamp |
| B5 | Every file in `artifacts_modified` was read (spot-check 3+) | Phantom file references |
| B6 | Every architectural claim verified against codebase | Wrong architectural claims |
| B7 | Every struct/type signature checked | Wrong field names |
| B8 | Every INSERT/SELECT query verified | Missing query updates |
| B9 | EARS IDs cited exist in actual EARS documents | Fabricated requirement IDs |
| B10 | BDD IDs cited exist in actual BDD documents | Fabricated scenario IDs |
| B11 | Existing handlers/webhooks checked | Existing handler missed |
| B12 | Issue dependencies analyzed | Coupled issues split |
| B13 | Test specifications included | No automated tests |
| B14 | Fix locations verified (caller vs function) | Wrong fix location |
| B15 | DB migration + rollback included | Migration without rollback |
| C16 | `sdd_lifecycle` lists EVERY modified SDD document | Incomplete SDD lifecycle |
| C17 | Each SDD entry has: layer, document, action, archive_path, new_version, changes | Missing SDD metadata |
| C18 | Archive paths use CHG-ID format, not date-based | Wrong archive convention |
| C19 | New versions are bumped (not same as current) | Version not bumped |
| C20 | `supersedes` lists ALL archived documents with full paths | Missing supersedes |
| D21 | Every EARS ID exists in actual EARS document | Wrong traceability |
| D22 | Every BDD ID exists in actual BDD document | Wrong traceability |
| D23 | No architecture seed docs referenced as SDD docs | Wrong document type |
| D24 | Upstream requirements cited, not architecture descriptions | Wrong reference level |
| E25 | CHG contains governance steps only (SDD lifecycle + IPLAN creation) | Scope creep |
| E26 | NO code implementation steps in CHG | Code in wrong document |
| E27 | `implementation.steps` references IPLAN, not code files | Wrong reference |

**Violation log:** Record errors in CHG revision_history for audit trail.

### 3.5 IPLAN file_manifest accuracy
When an IPLAN is marked `Completed`, every file in its `file_manifest` with `status: DONE` must actually exist on disk and contain a real implementation (not a stub/mock). The iplan-executor agent defect (2026-08-30) proved this gap: files were marked DONE but contained stubs.

Verification: `grep -c 'TODO\|stub\|mock\|hardcoded' <file>` should return 0 for DONE files.

### 3.6 Subagent file write verification
When a subagent reports completing a file write, verify at least 3 specific changes by reading the file back. Subagents can report `status: success` without actually modifying the file (phantom success). Do not trust subagent success reports for critical file modifications — spot-check before marking tasks complete. Added after general-12 subagent reported IPLAN-19 rewrite success but file was unchanged (2026-10-23). Extended 2026-09-17 (CHG-32): re-verify at integration time, not just report time — concurrent siblings in one tree can clobber landings between report and check; run a per-file census (e.g. `grep -c CHG-32`) after ALL siblings land. Scoped diffs only: use `git diff -- <owned files>`, never whole-tree stat, under concurrency.

### 3.6a No whole-tree git operations with live subagents
`git stash`, `git checkout -- <dirs>`, branch switches, and `git add -A` commits on a tree shared with running subagents destroy their uncommitted work with no git recovery path. Use file-scoped commands only while agents run. Snapshot irreplaceable work (`cp -r` to /tmp, patch export) BEFORE any whole-tree operation. Added after a mid-session `git stash` wiped 5 landed CHG-32 SDD extensions (2026-09-17; recovery via trajectory-store replay).

### 3.6b Governed archive paths must be force-added
Repo-root `.gitignore` carries a bare `archive/` rule that silently excludes `docs/sdd/09-CHG/archive/CHG-*/` snapshots. `git add -A` shows nothing wrong while the archive never commits. Force-add governed archives (`git add -f docs/sdd/09-CHG/archive/<CHG-ID>`) and verify with `git ls-files`. Added after archive/CHG-32 (20 snapshots) was invisible to git until `git check-ignore -v` revealed the rule (2026-09-17).

### 3.6c sdd_doc_lint results require layer detection
`sdd_doc_lint` prints "no structural findings" for paths without an `NN_LAYER` segment or `ARTIFACT-NN` filename prefix — the file is SKIPPED, not clean. Never trust a clean result without confirming detection (JSON format shows file entries); always pass layer-pattern paths. Added after a STEP-02 "clean baseline" proved irreproducible — the invocation had skipped the files (2026-09-17).

### 3.7 IPLAN SQL query accuracy
IPLAN endpoint details containing SQL queries must be verified against `migrations/schema.hcl` or the actual database schema before marking the IPLAN ready for implementation. Fabricated column names (e.g., `id` instead of `user_id`, `balance` instead of `balance_minor_units`) will cause runtime failures. Added after IPLAN-19 had 5 wrong admin view SQL queries that used plausible but nonexistent column names (2026-10-23).

### 3.8 IPLAN breaking change documentation
When an IPLAN step modifies an exported function or constructor signature, it MUST explicitly document: (1) the current signature, (2) the new signature, (3) that it's a breaking change, and (4) which callers must be updated. Omitting this leads to compilation errors during implementation. Added after IPLAN-19 changed NewAdminServer from 2-param to 3-param without documenting the breaking change (2026-10-23).

### 3.9 IPLAN status transitions are mandatory gates
The IPLAN status lifecycle (`Draft → Approved → In Progress → Completed → Verified`) requires explicit status updates at each phase boundary. Each transition is a blocking gate:
- `Draft → Approved`: Authorization gate. Must be set before any implementation planning.
- `Approved → In Progress`: Implementation gate. MUST be set BEFORE writing any code.
- `In Progress → Completed`: Completion gate. Set when all implementation is done and tests pass.
- `Completed → Verified`: Validation gate. Set after verification passes.

**Critical rule:** Never start work on the next phase without first updating the IPLAN status to that phase. The agent MUST check `document_control.status` AND update it to the next phase before beginning work. Violation pattern: updating to `Approved` then starting implementation without updating to `In Progress`. Added after IPLAN-19 was updated to `Approved` but implementation started without `In Progress` transition (2026-10-23).

### 3.10 IPLAN file_manifest status must be updated in real-time
After implementing each file, the IPLAN `file_manifest` entry MUST be updated from `PENDING` to `DONE` (or `SKIPPED` with `_note`). Never leave `PENDING` status after implementation is complete. The agent must track file_manifest status as work progresses, not batch-update at the end. Added after IPLAN-19 had all 18 file_manifest entries with `status: PENDING` after Groups A-D were implemented (2026-10-24).

### 3.11 CHG status must track IPLAN completion
When an IPLAN authorized by a CHG is marked `Completed`, the CHG status MUST also be updated to `Completed` (or at least `Implemented`). The CHG status should reflect the actual implementation state, not just the governance state. A CHG stuck at `In-Progress` after all its IPLANs are `Completed` violates the status lifecycle. Added after CHG-08 had `status: In-Progress` with `date_implemented: null` even after IPLAN-19 was `Completed` (2026-10-24).

### 3.12 P0-Card gate requires explicit user decision
Group E (card handlers) in IPLAN-19 was blocked by P0-Card gate until user confirmed "Bridge Cards Issuing" as the card provider. The gate is a product decision, not a technical decision. The agent cannot make this decision — it must come from the user/product owner. The gate status must be recorded in the IPLAN's `risk_and_gating` section and updated when confirmed. Added after IPLAN-19 Group E was marked SKIPPED with `_note: "P0-Card gate not confirmed"` until user confirmed (2026-10-24).

---

## 4. Status Propagation Rules

### 4.1 Upstream status propagation on downstream layer start
When a downstream SDD layer document is started, the upstream document's status MUST be updated to "Approved". Do not start the next layer if its upstream is not approved.

**Propagation chain:**
- Seed doc status → "Approved" when module doc generation starts
- Module doc status → "Approved" when its BRD layer starts
- BRD doc status → "Approved" when its PRD layer starts

This ensures the SDD chain reflects authoring progress — a Draft upstream means its downstream hasn't been started yet.

**ADR convention:** ADRs use "Accepted" (not "Approved") as their terminal status.

---

## 5. Decision Workflow Rules

See [DECISION_WORKFLOW.md](DECISION_WORKFLOW.md) for the full specification.

**Summary:**
- Seed docs (architect): suggestions, 2-3 options, principles
- Module docs (product owner): ALL source material, single source of truth
- SDD ADRs (dev team): ONE selected architecture
- No separate seed ADR files
- SDD ADR selects, doesn't re-survey

---

## 6. SDD Reference Integrity Rules

### 6.1 Source IDs must be passed to subagents

When delegating SDD document creation to subagents, the delegation prompt MUST include the actual source document IDs. Never ask a subagent to generate cross-references without the real upstream IDs.

**Required in delegation prompt:**
- The actual EARS element IDs (e.g., `EARS.09.03.a1b2`, `EARS.09.03.c3d4`, ...)
- The actual BDD scenario IDs (e.g., `BDD.09.03.f1a2`, `BDD.09.03.b3c4`, ...)
- The actual ADR decision IDs (e.g., `ADR.09.03.a3f1`)
- The actual PRD/BRD element IDs referenced

**Forbidden:** Generating IDs like `EARS.09.00.xxx` or `BDD.09.01.xxx` — these are hallucinated references that don't match any real document.

### 6.2 Post-delegation reference validation

After a subagent completes an SDD document, the parent agent MUST validate all cross-references before integrating the output:

1. `grep '@ears:' <file>` — verify each EARS ID exists in the upstream EARS document
2. `grep '@bdd:' <file>` — verify each BDD ID exists in the upstream BDD document
3. `grep '@prd:' <file>` — verify each PRD ID exists in the upstream PRD document
4. `grep '@brd:' <file>` — verify each BRD ID exists in the upstream BRD document
5. `grep '@adr:' <file>` — verify each ADR ID exists in the upstream ADR document
6. `grep -i 'ers\.' <file>` — check for `EARS` typos (missing 'A')
7. `sort | uniq -d` on ID lists — check for duplicate IDs within the file

**Never skip this step.** The cost of validating is ~2 minutes; the cost of propagating fake references through 7 SDD layers is hours of rework.

### 6.3 ID format verification

SDD element IDs follow strict formats. When reviewing any document, verify IDs match these patterns:

| Layer | ID Format | Example |
|-------|-----------|---------|
| EARS | `EARS.{NN}.03.{hash}` (requirements), `EARS.{NN}.04.{hash}` (quality) | `EARS.09.03.a1b2` |
| BDD | `BDD.{NN}.03.{hash}` | `BDD.09.03.f1a2` |
| ADR | `ADR.{NN}.03.{hash}` (decisions), `ADR.{NN}.05.{hash}` (consequences) | `ADR.09.03.a3f1` |
| SPEC | `SPEC.{NN}.{xx}.{hash}` | `SPEC.09.01.a1b7` |
| TDD | `TDD.{NN}.04.{hash}` (unit), `TDD.{NN}.05.{hash}` (integration), `TDD.{NN}.06.{hash}` (e2e) | `TDD.09.04.a1b2` |
| PRD | `PRD.{NN}.10.{hash}` | `PRD.09.10.a1b2` |
| BRD | `BRD.{NN}.07.{hash}` (FRs), `BRD.{NN}.08.{hash}` (ADRs) | `BRD.09.07.a1b2` |

**Red flags:** `EARS.09.00.*`, `EARS.09.01.*`, `BDD.09.00.*`, `BDD.09.01.*` — section numbers 00 and 01 don't exist in EARS/BDD. These are always hallucinated.

### 6.4 Manual ID generation tracking

When creating documents directly (not delegated), maintain a running set of assigned IDs to prevent duplicates:

1. Before assigning a new ID, check all previously assigned IDs in the current file
2. Use `sort | uniq -d` on the ID list to verify no duplicates
3. For BDD scenarios specifically: each EARS requirement maps to exactly one BDD scenario — verify 1:1 mapping

### 6.5 EARS pattern verification

When authoring EARS requirements, verify the pattern matches the requirement semantics:

| Pattern | Use When | Example |
|---------|----------|---------|
| `WHEN` (event-driven) | Triggered by a specific event or user action | "WHEN an inbound port API call is received" |
| `WHILE` (state-driven) | Continuous state that must be maintained | "WHILE the Go service is running" |
| `IF` (unwanted behavior) | Error condition or failure mode | "IF the OTel Collector becomes unreachable" |
| `WHERE` (optional feature) | Feature-flagged or configuration-gated | "WHERE Grafana Faro is configured" |
| `THE-SHALL` (ubiquitous) | Universal invariant or system-wide rule | "THE Go service SHALL export all telemetry through OTel" |

**Common mistake:** Using `IF` for liveness/always-on checks. "Process is alive" is a normal state (`WHILE`), not an error condition (`IF`).

### 6.6 Archive before ID reuse

Before assigning an SDD ID that may have been used in a prior session, check if a file with that ID already exists. If it exists and is from a different scope, archive it to `docs/sdd/09-CHG/archive/CHG-SDD09-fix/` before creating the new document.

### 6.7 Reference to full RCA

For the complete root cause analysis, issue registry, and prevention rules, see `docs/governance/notices.md`.

### 6.8 Self-learning governance

For the self-learning loop architecture, capture/extract/consolidate/inject phases, and verification checklist, see `docs/governance/SELF_LEARNING.md`.

### 6.9 Self-learn → governance update + feedback submission protocol

When the self-learn skill finds a governance-relevant pattern (missing rule, broken process, new constraint), it updates the target governance document directly AND submits tracking issues. This is authorized for solo projects where CHG-mediated governance updates add unnecessary latency.

**Targets:** `GOVERNANCE_RULES.md`, `DECISION_WORKFLOW.md`, `notices.md`, `SELF_LEARNING.md`, `.claude/AGENTS.md`

**Constraints:**
- Only add rules — never remove safety invariants
- Cite the learning source in the update (e.g., "Added after TDD↔IPLAN sync bug, 2026-10-05")
- Keep updates small — one rule or sentence per learning
- Log all changes in the self-learn report output

**Feedback submission (mandatory for governance/framework changes):**

| Modified files | Target repo | Purpose |
|----------------|-------------|---------|
| `.aidoc/framework/**` | `vladm3105/aidoc-flow-framework` | Framework-level bugs/improvements |
| `.aidoc/project/governance/**` | `vladm3105/b-local-privy` | Project governance audit trail |

After modifying any file under `.aidoc/framework/` or `.aidoc/project/governance/`, submit a tracking issue using the `gh issue create` command with the submit-feedback body contract. Search for duplicates first. Read back the issue to verify publication. Log issue URLs in the self-learn report.

### 6.10 TDD↔IPLAN cross-layer consistency (5 rules)

These rules prevent the 5 governance bugs found during the TDD↔IPLAN status sync investigation (2026-10-05).

**Rule A: IPLAN status propagation to TDD.** When an IPLAN `file_manifest` entry is marked `DONE` with `verified: true`, the corresponding TDD `test_mapping` entries MUST also be updated from `pending` to `implemented`. IPLAN `DONE` means "file created", not "all TDD test cases inside it implemented." Enforced by lint rules TDD-SYNC-001 through TDD-SYNC-004.

**Rule B: Cross-IPLAN file ownership.** Every test file referenced by a TDD `test_mapping` MUST be listed in the TDD's owning IPLAN's `file_manifest`. If a test file is shared across components (e.g., `internal/provider/integration_test.go`), it MUST be listed in ALL owning IPLANs, or a cross-reference note in the IPLAN must cite the shared file's location. No TDD may reference a file that its owning IPLAN doesn't list without a documented cross-reference.

**Rule C: Function name consistency.** Test function names in code MUST match the names declared in TDD `test_mapping`. If a name needs changing, update the TDD FIRST, then implement. Never write a test with a different name and leave the TDD stale.

**Rule D: Language consistency.** TDDs and their owning IPLANs MUST reference the same test file language (Python or Go). After a language pivot (e.g., Python→Go), BOTH the TDD and IPLAN must be updated in the same change. No TDD may reference Go files while its IPLAN lists Python files for the same component.

**Rule E: Index synchronization.** `TDD-00_index.md` and `IPLAN-00_index.yaml` MUST show consistent IPLAN statuses. `IPLAN-00_index.yaml` is the source of truth. When an IPLAN status changes, BOTH indexes must be updated. Any new IPLAN added to `IPLAN-00_index.yaml` MUST also be added to `TDD-00_index.md`.

---

## 7. Framework and project structure

**Status:** Active — 2026-10-06

### 7.1 Framework location

The aidoc-flow-framework is cloned directly into `.aidoc/framework/` (NOT a symlink).

**Framework source:** `https://github.com/vladm3105/aidoc-flow-framework`
**Framework location:** `.aidoc/framework/` (cloned repo, version-pinned)
**Framework spec:** `.aidoc/framework/framework/` (governance, layers, playbooks, etc.)

**Included directories** (framework development files excluded):
- `framework/` — core spec (governance, layers, playbooks, scripts, templates, registry)
- `docs/` — documentation
- `examples/` — reference examples
- `hooks/` — PostToolUse hooks
- `sdd_doc_lint/` — structural linting
- `tests/` — conformance tests

### 7.2 Project structure rule

`.aidoc/project/` MUST mirror the same directory structure as
`.aidoc/framework/framework/` — `governance/`, `layers/`, `playbooks/`,
`scripts/`, `templates/`, `registry/`. Project-specific files go in the
matching subdirectory.

### 7.3 Discovery rule

When reading a template, rule, or playbook:
1. Check `.aidoc/project/{same-path}` first (project override)
2. If the file exists there, use it
3. If not, fall back to `.aidoc/framework/framework/{same-path}` (shared framework)

### 7.4 Framework updates

```bash
cd .aidoc/framework && git pull origin main
```

After pulling, verify the version in `framework/VERSION` matches the pin in
`.aidoc/profile.yaml`. If a newer version has breaking changes, update the
project overrides in `.aidoc/project/` before adopting.

### 7.5 No symlinks

**Rule:** Do NOT create symlinks to external directories. The framework is a
real cloned copy. This allows version pinning, local patches, and clean
`git pull` updates without breaking paths.

**Enforcement:** A grep check warns when active files reference external
framework paths instead of `.aidoc/framework/`:

```bash
grep -rn "framework/" docs/ .aidoc/ CLAUDE.md --include="*.md" --include="*.yaml" \
  | grep -v ".aidoc/framework/" | grep -v "09-CHG/" | grep -v "sdd_archived/" \
  | grep -v "framework_archived/" | grep -v ".aidoc/README.md"
```

If this returns results, update those files before committing.

---

## 8. Port Boundary & Wire Contract Invariants

### 8.1 RPC request payload normalization
The client HTTP port adapter (`httpPortAdapter.js`) wraps RPC parameters in `{ args: { ... } }`. The Go `PortRouter` must unwrap `args` if present before delegating to port handlers to ensure parameter binding is transparent to handler implementations.

### 8.2 List-returning port response envelope
All collection/list endpoints (`wallet.list`, `recipient.list`, `transaction.list`, `bill.categories`, `bill.due`, `schedule.list`, `notification.list`) must wrap arrays in `map[string]interface{}{ "items": [...] }` conforming to the cabinet's contract expectation.

### 8.3 Profile schema KYC invariant
The `profile.get` endpoint must return the complete profile object including the `kyc: { tier: "L0", status: "not started" }` object to prevent frontend sidebar navigation crashes during boot.

### 8.4 Privy direct webhook signature verification
Privy has deprecated Svix delivery headers (`Svix-Id`, `Svix-Timestamp`, `Svix-Signature`). Webhook signature verification in `webhook_handler.go` must read direct Privy signature headers (`privy-signature` / `privy-webhook-signature`) with fallback to legacy headers.

---

*Created: 2026-08-30*
*Updated: 2026-09-14 — Added §8 Port Boundary & Wire Contract Invariants (RPC envelope normalization, list format, profile KYC schema, Privy direct webhooks)*
*Updated: 2026-10-23 — Added §3.1.1 MANDATORY SDD-First Implementation Order (NON-NEGOTIABLE) — violated 3 times (CHG-04, CHG-06, CHG-08), CHG-10 followed correctly*
*Updated: 2026-10-06 — Replaced §7 (symlink deprecation) with framework/project structure rules*
*Updated: 2026-10-05 — Added §6.10 TDD↔IPLAN cross-layer consistency rules (5 rules: status propagation, file ownership, function names, language consistency, index sync)*
*Updated: 2026-10-05 — Added §6.9 Self-learn → governance update protocol*
*Updated: 2026-08-31 — Added §6 SDD Reference Integrity Rules (subagent delegation, post-delegation validation, ID format verification, manual ID tracking, EARS pattern verification)*
