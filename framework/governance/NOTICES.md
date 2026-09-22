# SDD Document Generation — Root Cause Analysis & Prevention

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-07 |
| Author | Framework Maintainer |
| Framework Version | 0.57.0 |


Tracks issues encountered during SDD document generation, their root causes,
prevention rules, and verification checklists. This document is the canonical
reference for known failure modes and their mitigations.

## Issue Registry

All issues encountered during SDD generation, ordered by severity.

### Issue 1: Hallucinated cross-references in downstream documents (HIGH)

**What happened:** SPEC-09 contained 18 fake EARS IDs (`EARS.09.00.*`,
`EARS.09.01.*`), 11 fake BDD IDs (`BDD.09.00.*`, `BDD.09.01.*`), a typo
(`ERS.09.09` missing 'A'), and a wrong ADR reference.

**Root cause:** Delegation prompts provided format references but did NOT
include the actual upstream element IDs. Subagents invented plausible-looking
IDs that followed the general pattern but didn't match real source documents.

**Why it propagated:** After subagent completion, indexes were updated without
validating output references against upstream files.

**Prevention:**
- Rule 1: Pass source IDs to subagents (see §Prevention Rules)
- Rule 2: Validate references after delegation

### Issue 2: Duplicate BDD scenario ID (MEDIUM)

**What happened:** BDD-09 scenario `BDD.09.03.i3j4` was assigned to two
different scenarios.

**Root cause:** Created 29 BDD scenarios manually in sequence, generating IDs
mentally without maintaining a running set of used IDs.

**Prevention:**
- Rule 3: Track assigned IDs during manual creation

### Issue 3: Wrong EARS pattern for liveness (LOW)

**What happened:** EARS-09 requirement used `IF the Go service process is
alive` (unwanted behavior) instead of `WHILE the Go service process is alive`
(state-driven).

**Root cause:** Misclassified "process is alive" as an error condition.

**Prevention:**
- Rule 4: Verify EARS pattern semantics

### Issue 4: Old file conflict (MEDIUM)

**What happened:** An old `TDD-09_go_unit_tests_addendum.yaml` from a prior
session existed alongside the new `TDD-09_observability_logging.yaml`.

**Root cause:** Old file was not archived when TDD-09 was reassigned.

**Prevention:**
- Rule 5: Archive old documents before reusing IDs

### Issue 5: TDD↔IPLAN cross-layer consistency bugs (HIGH)

**Date:** 2026-10-05

**What happened:** Five independent governance bugs caused TDDs and IPLANs to
drift out of sync:

- **Bug A:** IPLAN tracks file creation, not test implementation. 106 test
  cases show `pending` while all IPLAN entries claim `DONE`.
- **Bug B:** Cross-IPLAN file ownership gap. Test files referenced by TDDs
  but not listed in owning IPLANs.
- **Bug C:** Function name divergence. Only 50 of 176 TDD-specified names
  exist with exact names (28% match rate).
- **Bug D:** Language mismatch. TDDs reference Go files but IPLANs list Python.
- **Bug E:** Stale TDD-00 index showing wrong IPLAN statuses.

**Prevention:**
- Rule 6: TDD↔IPLAN cross-layer consistency (5 rules)

## Prevention Rules

### Rule 1: Pass source IDs to subagents (prevents Issue 1)

When delegating SDD document creation, the delegation prompt MUST include the
actual upstream element IDs. Copy the ID lists from the source files into the
prompt.

**Example prompt addition:**
```
Actual EARS-09 IDs to reference: EARS.09.03.a1b2, EARS.09.03.c3d4, ...
Actual BDD-09 IDs to reference: BDD.09.03.f1a2, BDD.09.03.b3c4, ...
Actual ADR-09 decision ID: ADR.09.03.a3f1
```

**Never:** Ask a subagent to "reference the upstream EARS/BDD documents"
without providing the actual IDs. Subagents cannot read files the parent
hasn't provided.

**Post-delegation grep validation (Rule 1–2 harden):** after a delegated
document lands, re-run the reference checks against the REAL tag namespaces —
`@prd:`, `@brd:`, `@adr:` — not just the EARS/BDD tags in Rule 2:

```bash
# Every cited upstream ID must exist in its source file; each grep must return ≥1 line
grep -F '<cited-PRD-ID>' <prd-source-file>
grep -F '<cited-BRD-ID>' <brd-source-file>
grep -F '<cited-ADR-ID>' <adr-source-file>
# Duplicate detection across the delegated file
grep -oP 'id: "\K[^"]+' <file> | sort | uniq -d  # Should return nothing
```

### Rule 2: Validate references after delegation (prevents Issue 1)

After a subagent completes an SDD document, run these checks before
integrating:

```bash
# Check for fake EARS IDs (section 00/01 don't exist)
grep -P '@ears: EARS\.\d+\.0[01]\.' <file>  # Should return nothing

# Check for fake BDD IDs
grep -P '@bdd: BDD\.\d+\.0[01]\.' <file>    # Should return nothing

# Check for EARS typos
grep -i 'ers\.' <file>                         # Should return nothing

# Check for duplicate IDs
grep -oP 'id: "\K[^"]+' <file> | sort | uniq -d  # Should return nothing
```

### Rule 3: Track assigned IDs during manual creation (prevents Issue 2)

When creating documents directly (not delegated), maintain a running set:

1. Before assigning each new ID, check all previously assigned IDs in the
   current file
2. After completing the file, run `sort | uniq -d` on the ID list
3. For BDD: verify 1:1 mapping between EARS requirements and BDD scenarios

### Rule 4: Verify EARS pattern semantics (prevents Issue 3)

When authoring EARS requirements, apply this decision tree:

```
Is this a normal operating state?
  → YES → WHILE (state-driven)
  → NO → Is this triggered by a specific event?
    → YES → WHEN (event-driven)
    → NO → Is this an error/failure condition?
      → YES → IF (unwanted behavior)
      → NO → Is this a universal invariant?
        → YES → THE-SHALL (ubiquitous)
        → NO → Is this feature-gated?
          → YES → WHERE (optional)
```

**Common traps:**
- "Process is alive" = normal state → WHILE, not IF
- "Collector is unreachable" = error → IF, not WHILE
- "All telemetry flows through Collector" = universal → THE-SHALL, not WHEN

### Rule 5: Archive old documents before reusing IDs (prevents Issue 4)

Before assigning an SDD ID that may have been used in a prior session:

1. Check if a file with that ID already exists: `ls <project>/sdd/07_TDD/TDD-NN_*`
2. If it exists and is from a different scope, archive it to
   `<project>/sdd/09-CHG/archive/<CHG-ID>/`
3. Only then create the new document with that ID

### Rule 6: TDD↔IPLAN cross-layer consistency (prevents Issue 5)

**Rule A: Status propagation.** IPLAN `DONE` + `verified: true` → update TDD
`pending` → `implemented`.

**Rule B: File ownership.** Every TDD test file MUST be in the owning IPLAN's
`file_manifest`.

**Rule C: Function names.** Code function names MUST match TDD-specified names.

**Rule D: Language consistency.** TDDs and IPLANs MUST reference the same
language (Go or Python).

**Rule E: Index synchronization.** `TDD-00_index.md` and
`IPLAN-00_index.yaml` MUST show consistent statuses. `IPLAN-00_index.yaml`
is the source of truth.

**Enforcement:** Lint rules `TDD-SYNC-A` through `TDD-SYNC-E` in
`LINT_RULES.md` (advisory).

## Concurrency traps

Three traps measured when multiple agents share one working tree. All are
process rules, not tool checks:

- **Verify-3 on subagent landings.** When a subagent reports completing a
  file write, verify at least 3 specific changes by reading the file back —
  agents can report success without modifying the file (phantom success).
  Re-verify at integration time, not just report time: concurrent siblings
  can clobber landings between report and check. Scope diffs to owned files
  (`git diff -- <owned files>`), never whole-tree stat, under concurrency.
- **No whole-tree git operations with live agents.** `git stash`,
  `git checkout -- <dirs>`, branch switches, and blanket `git add -A` on a
  tree shared with running agents destroy their uncommitted work with no
  recovery path. Use file-scoped commands only while agents run; snapshot
  irreplaceable work (copy to a scratch dir, patch export) BEFORE any
  whole-tree operation.
- **Layer detection before trusting a clean lint.** `sdd_doc_lint` prints
  "no structural findings" for paths without a layer pattern — the file is
  SKIPPED, not clean (see the `__main__.py` message). Never trust a clean
  result without confirming detection; always pass layer-pattern paths.
  Governed archive snapshots must be explicitly added and verified with
  `git ls-files` / `git check-ignore -v` (see `.gitignore` scope note).

## Verification Checklist

After completing any SDD layer, verify:

- [ ] All `@ears:` references match actual EARS IDs (format: `EARS.{NN}.03.{hash}`)
- [ ] All `@bdd:` references match actual BDD IDs (format: `BDD.{NN}.03.{hash}`)
- [ ] All `@prd:` references match actual PRD IDs (format: `PRD.{NN}.10.{hash}`)
- [ ] All `@brd:` references match actual BRD IDs (format: `BRD.{NN}.07.{hash}`)
- [ ] All `@adr:` references match actual ADR IDs (format: `ADR.{NN}.03.{hash}`)
- [ ] No duplicate IDs within the file
- [ ] No `ERS` typos (should be `EARS`)
- [ ] No section numbers `00` or `01` in EARS/BDD references
- [ ] Dates are current (not from prior sessions)
- [ ] No conflicting files with same ID from prior sessions

## Cross-References

- `DOC_GOVERNANCE_CORE.md` §6 — SDD Reference Integrity Rules
- `LINT_RULES.md` — TDD-SYNC-A through TDD-SYNC-E, EVAL-001 through EVAL-003
- `TESTING_STRATEGY_TDD.md` §Bidirectional Status Sync
- `ID_NAMING_STANDARDS.md` — Element ID format verification

### Issue 5: Index document counts drift from source YAML (MEDIUM)

**What happened:** TDD-00_index.md stated "78 TDD test cases" but actual TDD
YAML IDs total 104 (verified via `grep -c '^\s*- id: TDD\.' docs/sdd/07_TDD/TDD-0*.yaml`).

**Root cause:** Index counts were computed at generation time and never refreshed
when TDD documents grew.

**Prevention:**
- Rule: EVAL layer and any downstream doc must compute counts from source YAML, not copy from upstream index
- Rule: Add `grep -c` verification to pre-commit checklist for count-dependent docs

### Issue 6: Coverage summary contradicts entries (MEDIUM)

**What happened:** EVAL-01 and EVAL-02 had `coverage_matrix.entries` with
`status: implemented, coverage: 100` while the `summary` block said
`implemented: 0, coverage_percent: 0`.

**Root cause:** Summary was initialized to zeros and never updated after sample
entries were added.

**Prevention:**
- Rule: `coverage_matrix.summary` must be computed from `coverage_matrix.entries`
- Lint: EVAL-002 catches this contradiction
- Grep one-liners (run before landing any EVAL or downstream doc):
  - Index-count drift: `grep -c '^\s*- id: TDD\.' <tdd-files>` vs the index's stated count — recompute, never copy
  - Coverage contradiction: entries with `status: implemented, coverage: 100` alongside a zeroed `summary` — recompute `summary` from `entries`
