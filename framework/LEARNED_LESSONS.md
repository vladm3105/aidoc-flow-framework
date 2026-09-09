---
title: Learned Lessons & Project Knowledge
version: 1.0
source: trading project sessions (tradegent_hermes, b-local-privy)
last_updated: 2026-10-06
---

# Learned Lessons & Project Knowledge

Institutional knowledge extracted from live project sessions. Every rule in this file was
earned the hard way — through bugs, broken governance, or SDD chain failures. Reference this
document when writing governance rules, lint checks, or templates.

---

## 1. TDD ↔ IPLAN Status Sync

### The Problem

When an IPLAN is marked `Completed`, the corresponding TDD `test_mapping.status` fields remain
`pending`. This creates a systemic gap: IPLAN claims work is complete, but TDD records show
no tests implemented.

### Scope

- All 9 TDDs, 177 test cases across the tradegent_hermes project.
- 62 status mismatches, 53 missing Go unit tests, 13 missing Python tests.

### Root Cause

1. **No template-level rule** enforced status propagation from IPLAN → TDD.
2. Agents implement tests from IPLAN file manifests but never update TDD documents.
3. TDD `test_mapping.status` had no lifecycle rules — no enum validation, no gate check.

### Recommended Fix (Already Applied)

- **Lint rules TDD-SYNC-001 through TDD-SYNC-007** enforce cross-layer consistency.
- **IPLAN completion gate (§3.7)** includes 8 mandatory checks, including TDD sync.
- **verify_iplan_status.sh** script runs 6 automated checks before Completed status is allowed.
- **Source of truth**: IPLAN-00_index.yaml is authoritative for IPLAN status; TDD-00_index.md
  is a convenience mirror. Never treat the index as authoritative for IPLAN.

### Key Rule

> When implementing tests from an IPLAN, the TDD `test_mapping.tests[].status` MUST be
> updated from `pending` to `implemented` when the test function exists and passes. Never
> mark IPLAN `Completed` while TDD test cases in its scope remain `pending`.

### Evidence

- Commits: `f5ca3de`, `a76a53f`
- All 176 TDD test cases across 9 TDDs now `implemented` (0 pending) after fix.

---

## 2. Language Consistency

### The Problem

After a language pivot (e.g., Python → Go), both TDD and IPLAN documents reference test
files in different languages. TDD references `tests/unit/test_old_language.py` while IPLAN
`file_manifest` lists `.go` files.

### Root Cause

- TDD documents are generated before the language pivot decision.
- IPLAN documents are updated post-pivot, but TDD is not updated to match.
- No cross-layer check verifies file path language consistency.

### Rule

> TDD-SYNC-006: Language consistency. TDD `test_mapping[].file` must reference the same
> language as IPLAN `file_manifest[].path`. If a language pivot occurs, both documents
> MUST be updated in the same change.

### Evidence

- 53 Go unit tests + 13 Python tests had mismatched file paths across IPLAN/TDD.
- All corrected in the governance merge commit.

---

## 3. Governance Patterns

### 3.1 What Makes Governance Rules Effective

**Rules that worked:**

- **Single entry point**: CHG as the only initiator for SDD chain. Eliminates confusion
  about whether to create a new BRD or a CHG when modifying existing work.
- **Completion gates with scripted enforcement**: The 8 mandatory checks in §3.7 are
  only effective because `verify_iplan_status.sh` automates them. Manual gate checks are
  aspirational; automated ones are enforcement.
- **Lint rules for cross-layer consistency**: TDD-SYNC-001 through TDD-SYNC-007 turned
  "should" into "must" — lint failures block the build, not just warn.
- **Seed gap review gate at BRD level**: Moving the gate from post-IPLAN (where 91 stale
  references were found) to post-BRD catches gaps before they propagate to 6+ downstream
  documents.

**Rules that failed:**

- **Status enums without enforcement**: TDD `test_mapping.status: pending` existed as a
  field but had no lifecycle rules. The field was decorative until lint rules were added.
- **CHG scope creep**: Allowing code implementation steps inside CHG led to CHG-04 having
  12 code steps that belonged in IPLAN. Fix: CHG = governance record (SDD doc lifecycle +
  IPLAN creation), not implementation plan.
- **Dual-maintenance templates**: A pointer file approach for CHG-TEMPLATE.yaml created
  canonical source contradictions. The full 336-line template must be the single source.

### 3.2 Three-Tier Decision Model

| Tier | Role | Authority |
|------|------|-----------|
| Seed | Architect suggestions | Recommendation only |
| Module | Product owner | Source of truth for requirements |
| ADR | Dev team | Selects ONE approach per decision |

### 3.3 Status Lifecycle Rules

- **IPLAN**: `Draft → Approved → In Progress → Completed → Verified` (Verified = FINAL/INMUTABLE)
- **CHG**: `Proposed → Approved → In-Progress → Implemented → Completed`
- **ADR**: `Proposed → Accepted` (NOT Draft/In Review/Approved)
- Status **never regresses**. Verified IPLANs are immutable — CHG + new IPLAN required for changes.

### 3.4 Authoring Quality Rules

- Fabricated traceability IDs are the #1 LLM bug class. Always cross-reference against
  actual ADR traceability sections. Found 15 fabricated IDs across SPEC-01/03/05/09.
- EARS must use ONE flat list per category (not re-declare keys per FR section). Duplicate
  YAML keys silently drop requirements — 16 requirements were lost in EARS-10.
- TDD `spec_trace` uses component names, not fabricated element IDs.
  Format: `@spec: SPEC-10 (ClassName.method)`.
- TDD coverage table arithmetic is error-prone. TOTAL rows are hand-computed by LLMs
  and consistently wrong across all 9 TDDs. Should be machine-generated or checksummed.
- YAML literal block scalar pitfall: `|` strips leading indentation during parsing.
  SHA256 element IDs MUST be computed from YAML-parsed content, not raw source text.
- **"Write before read" is the root cause of repeated CHG governance failures.** The
  14-point creation checklist is a blocking gate, not post-hoc validation. Reading it
  AFTER writing the CHG/IPLAN defeats its purpose. The agent MUST read and complete
  every checklist item BEFORE writing any CHG document. This pattern caused 16 gaps in
  CHG-04 and 3 bugs in CHG-06 (violated items 11-14 — the exact items added after
  CHG-04 to prevent these failures). Prevention: read §CHG creation checklist BEFORE
  any CHG work, treat each item as a blocking gate.

---

## 4. File Reference Rules

### 4.1 TDD Cannot Reference Files Not in Its Owning IPLAN

- TDD `test_mapping[].file` must resolve to a file listed in the IPLAN `file_manifest`.
- Cross-IPLAN file ownership must be explicit — if a test file is shared, both IPLANs
  must declare it.
- Lint rule: TDD-SYNC-005 (cross-IPLAN file ownership).

### 4.2 IPLAN-00 Index Requires Full Registration

When adding a new IPLAN via CHG, must update ALL of:
1. `registry.plans`
2. `dependency_graph`
3. Parent IPLAN's `blocks` list
4. `execution_path.tiers`

Registry-only updates leave the IPLAN invisible to dependency resolution.

### 4.3 Archive Before ID Reuse

Before assigning an SDD ID that may have been used in a prior session:
1. Check if a file with that ID already exists.
2. If it exists from a different scope, archive it to `docs/sdd/09-CHG/archive/CHG-ID/`
   before creating the new document.
3. Never overwrite an existing SDD document without archiving first.

### 4.4 Rewrite, Never Append

When modifying existing SDD documents via CHG:
1. Archive old version to `docs/sdd/09-CHG/archive/{CHG-ID}/{layer}/`.
2. Rewrite as a clean new version.
3. CHG `supersedes` lists archived docs with full archive paths (never date-based).

---

## 5. Additional Learnings

### 5.1 EARS Structure

- Use a **flat list** of requirements with a `type` field (event, continuous, state)
  instead of nesting under category keys (`event_driven:`, `continuous:`, `state_based:`).
  This eliminates duplicate YAML key risk.

### 5.2 BDD Per-Scenario EARS

- BDD uses per-scenario `ears:` element-level list, NOT doc-level `@ears` tags.
- Feature block has NO `ears` field.

### 5.3 ADR Upstream Requirements

- ADR requires BOTH `@ears` AND `@bdd` (not just one). Missing either is a governance
  lint error.

### 5.4 SUBAGENT Parallelism Pattern

- 4 parallel general subagents (each with source + tests) completed successfully for
  IPLAN implementations.
- Pattern: spawn subagents for independent component groups, collect results, run lint,
  fix lint, commit.
- Each subagent reads existing patterns from the codebase independently.

### 5.5 GD-08 Compliance

- Every BDD scenario from SPEC traceability MUST appear in TDD Section 3 test_mapping.
- Missing scenarios trigger governance lint error ACC01.

### 5.6 Self-Learning Governance

- Self-learn can update governance documents directly in solo projects.
- Constraints: only add rules (never remove safety invariants), cite learning source,
  keep updates small, log changes in report.
- CHG-mediated process adds unnecessary latency for solo projects.

### 5.7 EVAL Layer (L10)

- Two-track testing strategy: Functional (EVAL-F: EARS+BDD) and Unit/Smoke (EVAL-U:
  TDD+IPLAN).
- 156 BDD scenarios mapped to functional test cases; 104 TDD test case IDs (not 78 —
  TDD-00_index.md count is inaccurate) mapped to unit/smoke test cases.

### 5.8 Docker & Deployment

- WSL = dev/edit/test only. Docker = staging/runtime.
- Do NOT add `dns` to Docker `daemon.json` — it replaces embedded DNS and breaks Compose
  service discovery. Caused intermittent CI failures.
- Python 3.12 (not 3.13) — Debian host has 3.12 cached but not 3.13.
- Atlas declarative mode is canonical: `atlas schema apply --to "file:///migrations/schema.hcl"`.
  NOT `atlas migrate apply` (versioned SQL).

### 5.9 ID Hash Formula

```
hashlib.sha256(f"{NN}:{section_id}:{norm(title)}:{norm(desc or title)}").hexdigest()[:4]
```
Must `.encode('utf-8')` before hashing.

### 5.10 Element ID Format

- Use dots, not dashes: `SPEC.10.06.a1b2` (correct), `SPEC-10-06-a1b2` (wrong).
- PRD has two conventions: Short kebab-case for component IDs vs `PRD.NN.SS.xxxx` for
  content elements.
- Acceptance criteria IDs share parent FR section number.

### 5.11 SPEC Level

- SPEC is C4-L3 Component level: describes component interfaces, data models, behavior
  contracts. NOT C4-L4 code/class diagrams.

### 5.12 Cross-SPEC Model Ownership

- When multiple SPECs reference the same model (e.g., AnalysisRequest in SPEC-01 and
  SPEC-03), designate one as authoritative and have others reference it via
  `@ref: SPEC-NN`.

### 5.13 Seed Input Is Frozen

- Resolve findings in SDD documents, not in seed files.
- Max 5 functional requirements per BRD document.

---

## 6. IPLAN Validation Pattern

### The Pattern

- `Completed` ≠ `Verified`
- `Completed` = implementation done, tests pass
- `Verified` = validation passed, all findings resolved
- Verified IPLANs are immutable (CHG required for changes)

### IPLAN Status Lifecycle

```
Draft → Approved → In Progress → Completed → Verified
                                                   ↑
                                                   │ (Final/Finite)
                                                   │
                                          Cannot be changed
                                          (Need CHG + new IPLAN)
```

| Status | Meaning | Allowed Transitions |
|--------|---------|---------------------|
| `Draft` | IPLAN created, not yet approved | → Approved |
| `Approved` | IPLAN authorized to proceed | → In Progress |
| `In Progress` | Implementation underway | → Completed |
| `Completed` | Implementation done, awaiting validation | → Verified |
| `Verified` | Validation passed, **FINAL/FINITE** status | **None** (immutable) |

### Validation Workflow

1. All `file_manifest` entries reach `DONE` + `verified: true`
2. Document status flips to `Completed`
3. Run unit tests from `file_manifest` (tdd_ref cases)
4. Run integration tests from `execution_commands.validation`
5. Create validation report using `IPLAN-VERIFY-TEMPLATE`
6. If findings exist:
   a. Create IPLAN-VERIFY to fix P0/P1 issues
   b. Fix all critical findings
   c. Re-run validation
7. When all findings resolved:
   a. Mark original IPLAN as `Verified` (FINAL/FINITE)
   b. Close validation IPLAN as `Completed`

### Why It Matters

- Prevents silent changes to validated code
- Creates audit trail for all modifications
- Ensures quality before marking as done
- Verified status is immutable — requires CHG for changes

### Implementation

- Use `IPLAN-VERIFY-TEMPLATE` for validation
- Record findings with severity (P0-P3)
- Fix all P0/P1 before marking Verified
- Keep validation IPLAN as historical record

### Key Rule

> Once an IPLAN reaches `Verified` status, it becomes immutable. To modify a
> Verified IPLAN, create a CHG record documenting the need for changes, then
> create a NEW IPLAN (IPLAN-NN+1) that references the original.

### Evidence

- IPLAN-15 (backend integration fixes): 19 findings, 22 files, all verified
- Validation pattern prevents "completed but broken" syndrome

---

## Appendix A: Lint Rules Reference

| Rule | Layer | Enforcement |
|------|-------|-------------|
| TDD-SYNC-001 | TDD | Function names exist in test files |
| TDD-SYNC-002 | TDD | File paths match IPLAN manifest |
| TDD-SYNC-003 | TDD | Status propagation pending → implemented |
| TDD-SYNC-004 | TDD | Test files exist on disk |
| TDD-SYNC-005 | TDD/IPLAN | Cross-IPLAN file ownership |
| TDD-SYNC-006 | TDD/IPLAN | Language consistency |
| TDD-SYNC-007 | TDD-00/IPLAN-00 | Index sync |
| TDD-SYNC-008 | IPLAN | validation_results consistency |
| TDD-SYNC-009 | IPLAN | validation_results field presence |
| GOV-001–007 | Governance | Governance-specific rules |
| ACC01 | BDD/TDD | BDD scenario missing from TDD test_mapping |
| EVAL-COV-001 | EVAL | Coverage validation |

---

## Appendix B: IPLAN Completion Gate (8 Mandatory Checks)

1. All `file_manifest` entries `status: DONE`
2. Stub detection clean
3. Tests pass
4. Lint clean
5. SPEC/TDD sync verified
6. TDD status updated to `implemented`
7. TDD-00 and IPLAN-00 index consistent
8. `validation_results.tests_passing=true` AND `lint_clean=true`

**Enforcement**: `./scripts/verify_iplan_status.sh IPLAN-NN`
- Exit 0 = pass
- Exit 1 = errors
- Exit 2 = usage error

---

## 10. EVAL Assertion Gaps vs BDD-Derived Testing Scenarios

### The Problem

EVAL test cases derived from BDD scenarios had fewer assertions than the BDD-derived testing
scenarios document specified. The scenarios doc has richer Assertions + Boundaries columns per
test case. EVAL captured only 1-2 assertions when the scenarios doc specified 4-6.

### Scope

- b-local-privy EVAL-01: ~80 assertion gaps across 83 test cases, 12 missing test cases entirely.

### Root Cause

1. EVAL authoring focused on the BDD YAML scenarios (which have `then:` clauses) but did not
   cross-reference against the testing scenarios document (which has detailed assertions).
2. No template guidance on which source document is authoritative for assertion completeness.

### Recommended Fix (Already Applied)

- **EVAL-TEMPLATE.yaml §test_design**: Added ASSERTION CROSS-REFERENCE mandatory guidance.
  "Each EVAL assertion list MUST include all items from the scenarios doc."
- **Lint rule EVAL-COV-002**: Smoke test commands must match CI workflow YAML.
- **Lint rule EVAL-COV-003**: TDD/BDD IDs must be verified against source documents.
- **Lint rule EVAL-COV-004**: Coverage summary counts must match parsed YAML.

### Key Rule

> When deriving EVAL assertions from BDD scenarios, always cross-reference against the
> BDD-derived testing scenarios document (docs/testing/scenarios/). That document has
> richer Assertions + Boundaries columns. Missing assertions cause shallow test coverage.

### Evidence

- b-local-privy EVAL-01 `bdd02.int01` only asserted "First login creates users row" but
  TC-02.6 also requires: email_verified_at set, privy_user_id stored, idempotent on second call.
- b-local-privy EVAL-02 had fabricated TDD ID `TDD.01.04.f19c` (doesn't exist in any TDD file).
- b-local-privy EVAL-02 smoke tests referenced non-existent scripts (`build_website.sh`).

---

## 11. EVAL Coverage Summary Counts Must Be Computed After Final Write

### The Problem

Coverage summary counts were set before the final YAML was written, resulting in wrong numbers.
EVAL-01 said "77 test cases" but actual parsed count was 95. EVAL-02 said "105 total" but
actual was 104.

### Root Cause

The agent writes the coverage summary as part of the initial draft, then adds test cases
incrementally. The summary is not recomputed after the final write.

### Recommended Fix (Already Applied)

- **EVAL-TEMPLATE.yaml §coverage_matrix.summary**: Added guidance "Computed from entries —
  total, implemented, pending, skipped, coverage %. Recompute after final YAML write."
- **Lint rule EVAL-COV-004**: Validates summary.total matches parsed test_design.test_cases count.

### Key Rule

> EVAL coverage summary MUST be recomputed after final YAML write using YAML parser:
> `python3 -c "import yaml; d=yaml.safe_load(open('file.yaml')); print(len(d['test_design']['test_cases']))"`
> Never set the summary count before writing all test cases.

### Evidence

- b-local-privy EVAL-01: summary said 77/156 (49%) but actual was 95/156 (61%).
- b-local-privy EVAL-02: summary said 105 total but parsed count was 104.

---

## 12. Migration Idempotency — IF NOT EXISTS Is Mandatory

### The Problem

Migration `004_add_audit_log.sql` used `CREATE TABLE audit_log (...)` without `IF NOT EXISTS`,
while all other migrations (001-03) used `IF NOT EXISTS`. The test runner assumes all
migrations are idempotent. Non-idempotent migrations cause integration test failures with
`relation already exists` when running against a pre-existing database.

### Scope

- b-local-privy: 12 auth integration tests skipped due to this migration bug.

### Root Cause

The migration author did not follow the established convention (all prior migrations used
IF NOT EXISTS). No lint rule enforces idempotency.

### Recommended Fix

- **Lint rule**: All migration SQL files MUST use `IF NOT EXISTS` for `CREATE TABLE`,
  `CREATE INDEX`, and `ALTER TABLE ADD COLUMN` statements.
- **Verification**: `grep -n "CREATE TABLE\|CREATE INDEX" migrations/*.sql | grep -v "IF NOT EXISTS"`

### Key Rule

> All migration SQL files MUST use IF NOT EXISTS for DDL statements. This ensures:
> 1. Migrations are idempotent (safe to re-run)
> 2. Integration tests pass against pre-existing databases
> 3. No manual intervention needed for schema convergence

### Evidence

- b-local-privy `004_add_audit_log.sql`: `CREATE TABLE audit_log (...)` → error on re-run.
- Fixed by adding `IF NOT EXISTS` to all CREATE TABLE and CREATE INDEX statements.
