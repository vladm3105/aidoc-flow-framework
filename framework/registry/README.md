# Framework Registry

`LAYER_REGISTRY.yaml` is the **authoritative, machine-readable definition** of
the SDD layer model: the 8 layers and their order, the traceability dependency
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
