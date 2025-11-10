# SPEC Index (Technical Specifications)

Purpose

- Central index for technical specification artifacts.
- Tracks allocation and sequencing for `SPEC-NNN_{descriptive}.{md|yaml}` files across service domains.

Allocation Rules

- Numbering: allocate sequentially, starting at `001`.
- Store YAML specs under the appropriate domain subdirectory (e.g., `services/`, `agents/`, `infrastructure/`).
- Maintain traceability links to upstream REQs, ADRs, PRDs, SYS, and BDDs per repository standards.
- Each specification should be implementation-ready with complete technical details.

Documents

- Template
  - Specification: [SPEC-TEMPLATE.yaml](./SPEC-TEMPLATE.yaml)
