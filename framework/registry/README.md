# Framework Registry

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-07 |
| Author | Framework Maintainer |
| Framework Version | 0.57.0 |


`LAYER_REGISTRY.yaml` is the **authoritative, machine-readable definition** of
the SDD layer model: the 10 layers and their order, the traceability dependency
graph (`required_tags`, `can_reference`, `downstream`), the `layer_groups`, the
C4 mapping, and the document/element `id_patterns`.

It is the single source of truth. The layer templates, the layer READMEs, and
the conformance suite all **defer to this file** — where prose and the registry
disagree, the registry wins.

## Conventions

- Each layer's `folder` is a path relative to the **`framework/` root**
  (e.g. `layers/01_BRD/`); `template` is a filename within that folder.
- The spec version is **not** stored here — it lives in `framework/VERSION`.
- `derived_from` records the legacy lineage (`SDD v3.2`); see `plans/DECISIONS.md`
  D-0006.

## Registering a new layer

Register the layer in `LAYER_REGISTRY.yaml` **before** authoring any of its
documents. The entry must carry `number`, `artifact`, `name`, `folder`,
`extensions`, `required_tags`, `can_reference`, `error_prefix`, `optional`,
`description`, `template`, and `downstream`. Then: bump
`metadata.total_layers` (numbers stay dense 1..N), add the layer to exactly one
`layer_groups` entry, extend `realizing_layers` when the layer realizes upstream
elements, extend `c4_mapping` when applicable, update upstream layers'
`downstream` fields, and document any new lint rule IDs in
`governance/LINT_RULES.md`. The header comment in `LAYER_REGISTRY.yaml` is the
checklist of record (lint rule REG01, advisory).
