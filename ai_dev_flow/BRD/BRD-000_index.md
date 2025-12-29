---
title: "BRD-000: BRD Index"
tags:
  - index-document
  - layer-1-artifact
  - shared-architecture
custom_fields:
  document_type: index
  artifact_type: BRD
  layer: 1
  priority: shared
---

# BRD Index (Business Requirements Documents)

Note: Some examples in this document show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → “Using This Repo” for path mapping.

Purpose

- Central index for Business Requirements Documents (BRDs).
- Tracks allocation and sequencing for `BRD-NN_{descriptive}.md` descriptors.

Allocation Rules

- Numbering: allocate sequentially starting at `001`; keep numbers stable.
- BRDs define high-level business objectives, market context, and strategic goals.
- Each BRD should link to downstream PRDs that translate business requirements into product features.
- BRDs are typically created during initial project planning and major strategic initiatives.

Document Organization

- BRDs focus on the "why" and "what" from a business perspective
- Include [DATA_ANALYSIS - e.g., user behavior analysis, trend detection], stakeholder needs, success metrics, and constraints
- Avoid technical implementation details (those belong in downstream documents)

Templates

- [BRD-TEMPLATE.md](./BRD-TEMPLATE.md): Comprehensive BRD template with detailed sections
- [BRD_CREATION_RULES.md](./BRD_CREATION_RULES.md): Complete reference for creating BRD documents according to doc-flow SDD framework
- [BRD_VALIDATION_RULES.md](./BRD_VALIDATION_RULES.md): Validation rules and quality gates for BRD documents

Validation Tools

- validate_brd_template.sh (../../scripts/validate_brd_template.sh): Pre-commit validation script for BRD documents (example)

Documents

(No BRD documents created yet. Add entries here as new BRDs are created.)
