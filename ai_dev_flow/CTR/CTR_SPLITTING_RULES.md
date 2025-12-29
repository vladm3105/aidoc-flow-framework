---
title: "CTR Splitting Rules"
tags:
  - framework-guide
  - shared-architecture
  - layer-9-artifact
custom_fields:
  document_type: splitting-rules
  artifact_type: CTR
  priority: shared
  development_status: active
  version: 1.0
  last_updated: 2025-12-28
---

# CTR Splitting Rules

Purpose: Extend the core splitting rules for API Contracts (CTR), which use paired Markdown (.md) and YAML (.yaml) files. Read with DOCUMENT_SPLITTING_RULES.md.

## When To Split CTR

- Size/readability thresholds are met for either file or combined pair.
- Contract spans multiple endpoint groups or domains where section-level navigation improves consumption.
- Traceability benefits by mapping specific sections to REQ/ADR/SPEC.

## Structure And Naming

- Canonical ID: `CTR-{NN}` remains the canonical identifier.
- Index file: `CTR-{NN}.0_index.md` (from `CTR-SECTION-0-TEMPLATE.md`).
- Section pairs (contiguous numbering starting at 1):
  - Markdown: `CTR-{NN}.{S}_{slug}.md`
  - YAML: `CTR-{NN}.{S}_{slug}.yaml`
- The `.md` and `.yaml` for a section must share the same `{NN}`, `{S}`, and `{slug}`.
- Navigation: Each Markdown section includes Prev/Next; the index links to all sections.

## Required Front‑Matter (Markdown Sections)

```yaml
---
doc_id: CTR-NN
section: S
title: "Section Title"
split_type: section
reading_order: sequential
parent_doc: "CTR-NN.0_index.md"
prev_section: null
next_section: "CTR-NN.(S+1)_{slug}.md"
paired_yaml: "CTR-NN.S_{slug}.yaml"
---
```

## Pairing And Consistency Rules

- Both files must exist for every section; CI should fail if a pair is missing.
- Content alignment:
  - `.md`: Context, rationale, examples, traceability details.
  - `.yaml`: Schemas, enums, error catalogs, quality attributes.
- Titles/IDs:
  - `.md` H1: `# CTR-NN: [Title]`
  - `.yaml` should include a stable `contract_id` (snake_case of slug) and `ctr_id: CTR-NN`.

## Validation

- Size lint: `./scripts/lint_file_sizes.sh`
- Link check: `python3 ./scripts/validate_links.py`
- Cross-doc: `python3 ./scripts/validate_cross_document.py`
- Schema validation: `yamllint` and JSON Schema checks per `CTR_SCHEMA.yaml`
- Pair integrity: ensure `.md`/`.yaml` pairs exist and share `{NN}.{S}_{slug}`

## Migration Checklist

1) Backup original files.
2) Create `CTR-{NN}.0_index.md` from `CTR-SECTION-0-TEMPLATE.md`.
3) For each section, create paired files from `CTR-SECTION-TEMPLATE.md` (Markdown) and the YAML section template pattern.
4) Wire Prev/Next in Markdown sections; ensure index lists all pairs.
5) Update traceability and run all validations.

Notes:
- Keep endpoint groups together; avoid splitting a single coherent interface across different section numbers.
- If a contract contains multiple protocols (e.g., REST + Pub/Sub), use separate sections for clarity.

