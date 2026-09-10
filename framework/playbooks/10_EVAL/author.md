---
name: EVAL Author
description: Creates EVAL documents from IPLANs following the EVAL template and ID naming standards
agent: general
layer: 10_EVAL
trigger: IPLAN status = "Completed" and no EVAL exists for this IPLAN
---

# EVAL Author Playbook

## Purpose

Create a new EVAL document for an IPLAN that has reached "Completed" status.
The EVAL defines what to test, how to trace it, and what quality gates apply.
This playbook enforces the ID naming standard and the one-source-per-test-case rule.

## When to Use

- After an IPLAN reaches "Completed" status for the first time
- When creating a new EVAL (not updating an existing one)

## Inputs

- **IPLAN file**: `IPLAN-NN_*.yaml` (the IPLAN to evaluate)
- **Upstream sources**: TDD, BDD, EARS referenced by the IPLAN
- **Template**: `framework/layers/10_EVAL/EVAL-TEMPLATE.yaml`

## Outputs

- **EVAL document**: `docs/sdd/10_EVAL/EVAL-NN/EVAL-NN.yaml`
- **Registered in**: `EVAL-00_index.md`

## ID Naming Standard

Per `framework/governance/ID_NAMING_STANDARDS.md`:

- **Document ID**: `EVAL-NN` (dash separator, per `{TYPE}-{NN}` rule)
- **Element ID**: `EVAL.{NN}.{SS}.{hash}` (dot separator, per `{TYPE}.{doc_id}.{section_id}.{hash}` rule)

The test case ID is **independent from the source**. Source type and source document
are tracked via `source_type` and `source_id` fields only.

```
# Correct
id: "EVAL.01.04.4d64"
source_type: tdd_test_case
source_id: "TDD.01.04.4d64"

# Wrong — embeds source type in ID
id: "EVAL-01.TDD-01.4d64"
```

## One-Source-Per-Test-Case Rule

Each test case maps to exactly **one** upstream element via `source_type` + `source_id`.
Never combine multiple sources (BDD + TDD, etc.) in a single test case.

Create as many test cases as needed — one per source element.

## Workflow

### Step 1: Read the IPLAN

```
1. Read IPLAN-{NN}_*.yaml
2. Extract:
   - iplan_id (IPLAN-NN)
   - scope (components, files, features)
   - upstream_sources[] (TDD, BDD, EARS references)
   - test_mapping (TDD test cases, BDD scenarios)
3. Determine owning_iplan: IPLAN-NN
4. Determine eval_track:
   - unit_smoke → TDD/IPLAN sources (CI pipeline)
   - functional → EARS/BDD sources (staging)
```

### Step 2: Select EVAL Number

```
1. Read EVAL-00_index.md
2. Find the next-free EVAL number for this IPLAN
3. Each IPLAN owns exactly ONE EVAL (1:1 mapping)
4. EVAL-NN must not already exist
```

### Step 3: Extract Test Cases from Sources

```
For each TDD test case in IPLAN scope:
  1. Read TDD.NN.04.xxxx (section 04 = test cases)
  2. Extract each test case:
     - source_id: TDD.NN.04.xxxx (the element ID)
     - name: test case title
     - priority: from TDD
     - target: function/module under test
     - implementation: language, test_file
  3. Create ONE EVAL test case per TDD element:
     - id: EVAL.{NN}.{SS}.{hash} (new, content-derived)
     - source_type: tdd_test_case
     - source_id: TDD.NN.04.xxxx
  4. NEVER merge multiple TDD cases into one EVAL case

For each BDD scenario in IPLAN scope:
  1. Read BDD.NN.SS.xxxx
  2. Extract each scenario:
     - source_id: BDD.NN.SS.xxxx
     - name: scenario title
     - priority: from BDD
     - preconditions, assertions
  3. Create ONE EVAL test case per BDD scenario:
     - id: EVAL.{NN}.{SS}.{hash} (new, content-derived)
     - source_type: bdd_scenario
     - source_id: BDD.NN.SS.xxxx
  4. NEVER merge multiple BDD scenarios into one EVAL case
```

### Step 4: Assign Element IDs

```
For each test case:
  1. Format: EVAL.{NN}.{SS}.{hash}
     - NN: two-digit EVAL document number
     - SS: two-digit section number (04 for test_design)
     - hash: 4-char hex content hash
  2. Hash algorithm (per ID_NAMING_STANDARDS.md):
     - Input: "{doc_id}:{section_id}:{norm(title)}:{norm(name)}"
     - Normalize: NFC → casefold → strip non-[a-z0-9 ] → collapse whitespace → trim → first 100 chars
     - Compute: SHA-256 hex[:4]
  3. Ensure no hash collisions within the EVAL document
```

### Step 5: Build Coverage Matrix

```
1. Every test case must appear in coverage_matrix.entries
2. Each entry maps:
   - source_id: the upstream element ID
   - source_type: tdd_test_case | bdd_scenario
   - test_case_id: the EVAL element ID (EVAL.NN.SS.xxxx)
   - test_file: implementation file
   - status: implemented | pending | skipped
   - coverage: percentage
3. Summary must match actual entry counts
```

### Step 6: Set Quality Thresholds

```
1. p0_critical_pass_rate: target 100, gate error
2. p1_high_pass_rate: target 100, gate error
3. coverage_percent: target 100, gate error
4. Adjust thresholds only with documented justification
```

### Step 7: Write the EVAL Document

```
1. Create directory: docs/sdd/10_EVAL/EVAL-{NN}/
2. Create file: docs/sdd/10_EVAL/EVAL-{NN}/EVAL-{NN}.yaml
3. Follow EVAL-TEMPLATE.yaml structure:
   - id: EVAL-NN (document ID, dash separator)
   - metadata
   - document_control
   - evaluation_scope
   - test_design (with test_cases[])
   - coverage_matrix (with entries[] and summary)
   - quality_thresholds
   - execution_plan
   - traceability
4. All test case IDs must be EVAL.NN.SS.xxxx (dot separator)
5. All source_ids must resolve to real upstream elements
```

### Step 8: Register in EVAL-00 Index

```
1. Open docs/sdd/10_EVAL/EVAL-00_index.md
2. Add row to Document Registry table:
   | EVAL-NN | IPLAN-NN | eval_track | iplan_version | - | - | - | Draft | date |
3. Update Eval Loop Summary:
   - EVALs Created += 1
   - EVALs Pending -= 1
```

### Step 9: Validate

```
1. Run sdd_doc_lint on the new EVAL document
2. Verify:
   - No EVAL-SRC-001 findings (one source per test case)
   - No EVAL-ID-001 findings (correct ID format)
   - All source_ids resolve to upstream elements
   - Coverage matrix covers all test cases
   - Summary counts match entry counts
3. Fix any findings before marking as Approved
```

## Checklist

- [ ] IPLAN status is "Completed"
- [ ] EVAL number selected (next-free, 1:1 mapping)
- [ ] Test cases extracted from IPLAN scope sources
- [ ] One test case per source element (no mixing)
- [ ] Element IDs follow `EVAL.NN.SS.xxxx` format
- [ ] Element IDs are independent from source
- [ ] Coverage matrix covers all test cases
- [ ] Summary counts match entry counts
- [ ] Quality thresholds set
- [ ] Document follows EVAL-TEMPLATE.yaml structure
- [ ] Registered in EVAL-00_index.md
- [ ] sdd_doc_lint passes with no errors
