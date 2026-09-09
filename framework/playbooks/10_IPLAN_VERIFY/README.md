# 10_IPLAN_VERIFY — IPLAN Verification Playbooks

## Document Control

| Field | Value |
|-------|-------|
| Version | 2.0 |
| Status | Approved |
| Last Updated | 2026-10-27 |
| Author | Framework Maintainer |
| Framework Version | 0.53.1 |

## Purpose

Playbooks for verifying IPLAN implementation correctness through iterative EVAL cycles.
These playbooks enforce the IPLAN status lifecycle and ensure quality before marking IPLANs as Verified.

## Core Concept: The Eval Cycle

Each IPLAN owns exactly one EVAL document (1:1 mapping). The EVAL defines what to test.
Eval reports (RPT) record what happened. The cycle iterates until all findings are resolved.

```
IPLAN Completed
  └── Create EVAL document (EVAL-{NN}/EVAL-{NN}.yaml)
      └── Run eval cycle 1 (initial_eval)
          └── If FAIL: fix findings → run cycle 2 (bug_fix_verification)
              └── Repeat until PASS
                  └── IPLAN Verified
```

## Playbooks

| Playbook | Role | Purpose |
|----------|------|---------|
| `evaluator.md` | EVAL Executor | Runs eval cycles, creates RPT reports |
| `verifier.md` | IPLAN Verifier | Reviews latest RPT verdict, marks IPLAN Verified |
| `report_generator.md` | RPT Generator | Generates EVAL-RPT from test execution output |

## Workflow

### Step 1: IPLAN Reaches Completed

```
1. IPLAN status transitions to "Completed"
2. Create EVAL document:
   - Extract relevant test cases from IPLAN scope
   - Create EVAL-{NN}/EVAL-NN.yaml
   - Test case IDs: EVAL-{NN}.BDD-{NN}.TC-{NN}.{NN}
   - Register in EVAL-00 index
```

### Step 2: Initial Eval (Cycle 1)

```
1. Evaluator runs tests defined in EVAL document
2. Creates EVAL-{NN}-RPT-001.yaml (trigger: initial_eval)
3. Records all findings with severity and context
4. Sets verdict: PASS / PASS-WITH-NOTES / FAIL / BLOCKED
```

### Step 3: Iterative Fix Loop (if FAIL)

```
For each OPEN finding:
  1. Fix the code issue
  2. Commit fix
  3. Re-run tests for this IPLAN only
  4. Create new RPT (trigger: bug_fix_verification)
  5. Record resolved findings and new findings
  6. Update verdict

Repeat until verdict = PASS
```

### Step 4: IPLAN Verified

```
1. Verifier reads latest RPT for this IPLAN
2. Checks verdict = PASS
3. Checks no P0/P1 findings open
4. Marks IPLAN as "Verified" (FINAL/FINITE)
```

## Trigger Types

| Trigger | When | What Changes |
|---------|------|-------------|
| `initial_eval` | First eval after IPLAN Completed | cycle = 1, baseline = null |
| `bug_fix_verification` | After code fixes | cycle += 1, records resolved/new findings |
| `chg_verification` | After CHG modifies IPLAN | EVAL version bumps, cycle resets |
| `scheduled` | Periodic regression check | Same EVAL version, new cycle |
| `pre_deploy` | Before branch promotion | Gate check, no code changes |

## Status Lifecycle

```
Draft → Approved → In Progress → Completed → Verified
                                                   ↑
                                          Eval cycle: PASS
```

## Key Rules

- **1:1 Mapping**: Each IPLAN owns exactly one EVAL document
- **Version Coupling**: EVAL versions when IPLAN versions (via CHG)
- **Self-Contained Reports**: Each RPT has all context inline, no external deps
- **Immutability**: RPT files are never modified after creation
- **Archive on Version**: Old EVAL + reports go to CHG archive when EVAL versions
- **Verified = Immutable**: Once Verified, no changes allowed (need CHG + new IPLAN)

## Directory Structure

```
docs/sdd/10_EVAL/
  EVAL-00_index.md                          # master index
  EVAL-NN/
    EVAL-NN.yaml                            # active strategy
    reports/
      EVAL-NN-RPT-001.yaml                  # cycle 1
      EVAL-NN-RPT-002.yaml                  # cycle 2
      ...
```

## Scripts

| Script | Purpose |
|--------|---------|
| `eval-trend.sh` | Compute trend metrics from RPT files |
| `eval-trend.sh --status` | Show latest verdict for all IPLANs |
