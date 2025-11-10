# SYS Index (System Requirements Specification)

Purpose

- Central index for System Requirements Specification (SRS) documents.
- Tracks allocation and sequencing for `SYS-NNN_{slug}.md` files.

Allocation Rules

- Numbering: allocate sequentially starting at `001`; keep numbers stable.
- One system area per file; cross-link to PRD/EARS/REQ and downstream SPEC/BDD.
- Slugs: short, descriptive, lower_snake_case.
- Each SYS document consolidates upstream requirements and guides downstream implementation.

Documents

- Template
  - Descriptor: [SYS-TEMPLATE.md](./SYS-TEMPLATE.md)
