---
name: sdd-eval
description: >-
  Run EVAL verification (Layer 10): execute the TDD battery, record per-metric PASS/FAIL verdicts against strategy thresholds, and close out with the execution receipt.
---

# SDD EVAL Runner

> Framework skill — routes to `framework/layers/10_EVAL/EVAL-TEMPLATE.yaml`,
> `EVAL-REPORT-TEMPLATE.yaml`, and `EVAL_WORKFLOW_STANDARD.md`.
> Paths below use `<skills-root>` = this `framework/skills/` directory.
> Upstream: implemented code plus the `sdd-tdd` battery; the IPLAN's
> execution receipt (`iplan_receipt_ref`) is the evidence anchor.

## 1. Execute the suites, not a sample

Ingest the evaluation scope, execute the suites, and evaluate each metric
against the EVAL strategy's thresholds. Every metric gets a verdict: PASS
or FAIL — no partials, no "mostly passing". A verdict must mirror the
threshold, not the mood.

## 2. Report receipts, not stories

Record per-metric verdicts in the EVAL report with the `iplan_receipt_ref`
so the run traces to the exact execution. FAIL verdicts name the broken
contract and open the CODE2C loop (defect → IPLAN → code) — they never
quietly become known issues.

## 3. Close out

Deployable fixes close live; static closeout covers the rest. The EVAL
report is the audit trail: complete, receipted, and merged before the
parent IPLAN is called Verified.
