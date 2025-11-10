# ADR Index

Purpose

- Central index for Architecture Decision Records (ADRs).
- Tracks allocation and sequencing for `ADR-NNN_{slug}.md` files.

Allocation Rules

- Numbering: allocate sequentially starting at `001`; keep numbers stable.
- One architectural decision per file.
- Include brief description and cross-links to REQ/PRD/EARS/SPEC/BDD when applicable.
- Each ADR should follow standard format: Context, Decision, Consequences, Alternatives Considered.
- ADRs are immutable once accepted; superseded ADRs should be marked as such.

Organization

- Group ADRs by architectural domain (data, infrastructure, integration, ML, risk)
- Use consistent slug naming: `{domain}_{decision_summary}`
- Link downstream implementations (SYS, SPEC) back to relevant ADRs

Documents

- Template
  - Descriptor: [ADR-TEMPLATE.md](./ADR-TEMPLATE.md)
