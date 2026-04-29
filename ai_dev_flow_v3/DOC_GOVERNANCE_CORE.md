# Document Governance — SDD v3

## Principles

1. **Single source of truth** — Each layer has one template. No duplicate representations.
2. **YAML-first** — All templates are `.yaml`. MD is for indexes and reference docs only.
3. **Cumulative traceability** — Each layer inherits all upstream tags; adds one.
4. **Readiness gates** — Each layer must score >=90/100 before downstream generation.
5. **No circular dependencies** — Downstream artifacts reference upstream, never the reverse.

## Immutability

- Published artifacts (status: Approved) must not be modified.
- Changes require a new document version or a new document ID.
- Superseded documents are marked as Deprecated/Superseded in document_control.status.

## Template Policy

- **Unified YAML only** — No `.md` templates, no `.feature` templates.
- Each layer has exactly one `{TYPE}-TEMPLATE.yaml`.
- Template fields use `_guidance` prefix for authoring instructions (not validated).
- Metadata block (`metadata:`) defines layer, schema version, and document type.

## Validation

- Layer entries must validate against `LAYER_REGISTRY.yaml`.
- Required upstream tags must be present in traceability sections.
- Element IDs must match the 4-segment hash format: `TYPE.NN.SS.xxxx`.
- Document IDs must match the format: `TYPE-NN`.

## What's Different from SDD v2

| v2 | v3 |
|----|----|
| 14-layer registry | 7-layer registry |
| `development_status` frontmatter | `status` field (simplified) |
| MD + YAML dual templates | YAML-only templates |
| 14-depth traceability chain | 6-depth chain |
| 5 SPEC subtypes + 6 TSPEC subtypes | Unified templates |
| CHG gate system | Project-level concern |
