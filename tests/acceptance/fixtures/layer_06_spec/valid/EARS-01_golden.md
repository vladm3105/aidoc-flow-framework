---
doc_id: EARS-01
artifact_id: EARS-01
artifact_type: EARS
layer: 3
deliverable_type: code
---
# EARS-01

## Document Control

Owner, status, and revision history for this EARS document.

## Purpose and Context

Formal requirements that translate the upstream PRD into testable EARS statements for the MVP.

## Requirements

Each requirement is atomic, measurable, and uses the canonical WHEN-THE-SHALL-WITHIN form.

### EARS.01.03.aaaa Login response

WHEN a user submits valid credentials, THE authentication service SHALL return a session token WITHIN 300 milliseconds at the 95th percentile.

- @brd: BRD.01.07.aaaa
- @prd: PRD.01.09.aaaa

### EARS.01.03.bbbb Search response

WHEN a user submits a product query, THE catalog service SHALL return ranked results WITHIN 500 milliseconds at the 95th percentile.

- @brd: BRD.01.07.aaaa
- @prd: PRD.01.09.aaaa

### EARS.01.03.cccc Checkout response

WHEN a buyer confirms a cart, THE order service SHALL persist the order and emit a confirmation event WITHIN 800 milliseconds at the 95th percentile.

- @brd: BRD.01.07.aaaa
- @prd: PRD.01.09.aaaa

## Quality Attributes

Quantified performance, security, and reliability targets aligned with the requirements above.

## Traceability

Upstream BRD and PRD references for this EARS document.

- @brd: BRD.01.07.aaaa
- @prd: PRD.01.09.aaaa

## Glossary

Project-specific terms and definitions used in this EARS document.
