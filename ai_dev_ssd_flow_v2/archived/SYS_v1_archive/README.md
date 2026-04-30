# SYS v1 Archive

**Archived**: 2026-03-29
**Reason**: Replaced by unified `SYS-TEMPLATE.yaml` (schema v1.0)

## Archived Files

| File | Replaced By |
|------|-------------|
| `SYS-MVP-TEMPLATE.md` | `../SYS-TEMPLATE.yaml` |
| `SYS-MVP-TEMPLATE.yaml` | `../SYS-TEMPLATE.yaml` |
| `SYS_MVP_SCHEMA.yaml` | Validation via mcp_sdd tools |
| `SYS_MVP_CREATION_RULES.md` | `_guidance` fields in template |
| `SYS_MVP_VALIDATION_RULES.md` | mcp_sdd `sdd_validate` |
| `SYS_MVP_QUALITY_GATE_VALIDATION.md` | mcp_sdd `sdd_score_validate` |
| Other files | See migration notes |

## Migration Notes

- 15 sections reduced to 12 + glossary
- Compliance merged into Quality Attributes; Change History into Document Control
- Sequential IDs replaced by hash-based (`SYS.NN.{section}.xxxx`)
- C4 Component level: `c4_level.value: component`, diagrams: c4-l3, dfd-l3
- Changelog: `changelog/CHANGELOG_v0.7.0.md`
