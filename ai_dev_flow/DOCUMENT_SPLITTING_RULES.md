---
title: "Document Splitting Rules"
tags:
  - planning
  - split-standard
  - framework-wide
custom_fields:
  document_type: split-core
  priority: core
  development_status: active
  version: 1.0
  last_updated: 2025-12-28
---

# Document Splitting Rules

Purpose: Define the minimal, stable rules for splitting long documents into indexed sections while preserving IDs, readability, and traceability. This supersedes ad‑hoc guidance and serves as the single source of truth for split standards.

Scope: Applies to narrative Markdown types (e.g., BRD, PRD) and test/spec artifacts where applicable (e.g., BDD). For SPEC, split applies to Markdown narrative only; SPEC YAML remains monolithic per component for code generation.

## Monolithic vs Section-Based Structure

**Choose the appropriate structure based on document size and complexity:**

| Structure | File Pattern | Use When |
|-----------|--------------|----------|
| **Monolithic (Flat)** | `TYPE-DOC_NUM_{slug}.md` | Single-file documents <25KB, MVP templates |
| **Section-Based (Nested)** | `TYPE-DOC_NUM_{slug}/TYPE-DOC_NUM.S_{section}.md` | Documents >25KB, complex multi-section artifacts |

### Monolithic Documents (Flat Structure)

- **Location**: Directly in type directory (e.g., `docs/BRD/BRD-01_platform.md`)
- **No nested folder**: File lives at type root, not inside a subfolder
- **No section suffix**: Filename uses `TYPE-DOC_NUM_{slug}.md` pattern
- **H1 Title**: `# TYPE-DOC_NUM: Title` (no `.S` suffix)
- **Use for**: MVP templates, streamlined documents, single-file artifacts under 25KB

### Section-Based Documents (Nested Structure)

- **Location**: Inside nested folder (e.g., `docs/BRD/BRD-03_complex/BRD-03.0_index.md`)
- **Folder required**: Create `TYPE-DOC_NUM_{slug}/` folder containing all section files
- **Section suffix required**: All files use `TYPE-DOC_NUM.S_{section}.md` pattern
- **H1 Title**: `# TYPE-DOC_NUM.S: Section Title` (includes `.S` suffix)
- **Use for**: Large documents, complex multi-section artifacts, documents requiring splitting

## When To Split

- Trigger: Size linter warnings/errors or poor readability during review.
- Readability: If sequential reading becomes hard (> ~25–50KB or > ~500 lines), split.
- Traceability: If section‑level linking improves mapping to REQ/TEST/SPEC, split.
- Exceptions: SPEC YAML typically stays monolithic per component; split only when necessary.

## Canonical IDs And Structure

- Canonical ID: Keep `{TYPE}-{NN}` as the document’s canonical ID after splitting.
- Index file: Create `{TYPE}-{NN}.0_index.md` as the authoritative table of contents and navigation.
- Section files: Create `{TYPE}-{NN}.{S}_{slug}.md` where `{S}` is a contiguous integer starting at 1.
- Navigation: Each section includes `Prev`/`Next` links; no gaps in section numbering.
- Cross‑links: Point readers to specific sections when precision helps. The index links to all sections.

Templates:
- Use `{TYPE}-SECTION-0-TEMPLATE.md` to create the index file (`{TYPE}-{NN}.0_index.md`).
- Use `{TYPE}-SECTION-TEMPLATE.md` to create each section file (`{TYPE}-{NN}.{S}_{slug}.md`).
- For BDD, scaffold using the suite templates or `./scripts/scaffold_split_suite.sh` which applies the equivalent templates for aggregator and scenario files.

## Required Front‑Matter For Sections

Every section file must include the following fields (extend as needed per type):

```yaml
---
doc_id: TYPE-NN            # Canonical document ID (e.g., BRD-03)
section: S                 # Integer section number (e.g., 1)
title: "Section Title"
split_type: section
reading_order: sequential  # or reference
traceability_scope: inherited
index_role: false
parent_doc: "TYPE-NN.0_index.md"
prev_section: null         # or filename of previous section
next_section: "TYPE-NN.(S+1)_{slug}.md"
---
```

## Size Limits And Validation

- Markdown targets: 300–500 lines; warn > 500; error > 600.
- YAML targets: prefer monolithic per component; warn > 1000; error > 2000.
- Always run validations after splitting:
  - File size lint: `./scripts/lint_file_sizes.sh`
  - Link check: `python3 ./scripts/validate_links.py`
  - Cross‑doc: `python3 ./scripts/validate_cross_document.py`
  - Traceability updates: `python3 ./scripts/update_traceability_matrix.py`

## Migration Checklist

- Backup: Copy the original monolith before splitting.
- Index: Create `{TYPE}-{NN}.0_index.md` with section map and status.
- Sections: Create `{TYPE}-{NN}.{S}_{slug}.md` for each logical section.
- Navigation: Wire `Prev`/`Next` and add links from the index to all sections.
- Links: Update inbound/outbound links to use section files where it helps clarity.
- Traceability: Re‑run traceability scripts for affected docs.
- Validate: Run size lint, link checks, and any type‑specific validators.

---

# Generalized Rules By Type

- Narrative product docs (BRD/PRD):
  - Lead with overview/context, then move into specifications/stories; place appendices and traceability at the end.
  - Keep acceptance criteria adjacent to the relevant stories/features for clarity.
  - Avoid splitting a single coherent unit (e.g., one feature spec) across multiple files unless it exceeds limits; if split, keep numbering contiguous and cross‑link precisely.

- Test artifacts (BDD):
  - Organize as a suite directory with an aggregator index feature and individual scenario feature files.
  - Use an aggregator file with `@redirect` lines to scenarios; do not use headings in `.feature` files.
  - Prefix scenario files with the numeric suite/section for ordering (e.g., `07.01_...`, `07.02_...`). Optional companion Markdown files may hold narrative context.

- Structured specs (YAML‑heavy / SPEC):
  - SPEC YAML: Keep monolithic per component for deterministic code generation (do not split YAML).
  - SPEC Markdown: Split narrative when needed (index + section files) to improve readability for reviewers and different audiences.
  - If your tooling explicitly supports YAML includes and you document it, treat it as an advanced exception; otherwise keep YAML in a single file and move narrative to Markdown.

---

# FAQ

- Why keep an index file? It is the authoritative map of sections and the stable entry point for links.
- Can I skip numbers? No. Use contiguous integers to avoid broken navigation and confusion.
- How do I deprecate a section? Keep the number reserved in the index and mark it as deprecated; do not reuse numbers.
