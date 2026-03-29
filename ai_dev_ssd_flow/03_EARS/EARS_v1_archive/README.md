# EARS v1 Archive

**Archived**: 2026-03-29
**Reason**: Replaced by unified `EARS-TEMPLATE.yaml` (schema v1.0)

## Archived Files

| File | Replaced By |
|------|-------------|
| `EARS-MVP-TEMPLATE.md` | `../EARS-TEMPLATE.yaml` |
| `EARS-MVP-TEMPLATE.yaml` | `../EARS-TEMPLATE.yaml` |
| `EARS_MVP_SCHEMA.yaml` | Validation via mcp_sdd tools |
| `EARS_MVP_CREATION_RULES.md` | `_guidance` fields in `../EARS-TEMPLATE.yaml` |
| `EARS_MVP_VALIDATION_RULES.md` | Validation logic in mcp_sdd `sdd_validate` |
| `EARS_MVP_QUALITY_GATE_VALIDATION.md` | Quality gates via mcp_sdd `sdd_score_validate` |
| `EARS-MVP-TEMPLATE_FIX_PLAN.md` | Completed fix tracking (historical) |
| `EARS-00_TRACEABILITY_MATRIX-TEMPLATE.md` | Per-EARS Section 5 + AI-generated |
| `EARS_AI_VALIDATION_DECISION_GUIDE.md` | Empty scaffold |
| `EARS_VALIDATION_STRATEGY.md` | mcp_sdd tools |
| `EARS_VALIDATION_COMMANDS.md` | mcp_sdd tools |
| `FIXES_SUMMARY.md` | Historical fix report |
| `README_old.md` | New concise README |
| `examples/` | AI generates examples on demand |
| `scripts/` | Validation via mcp_sdd tools |
| `backup_2026-02-26/` | Old backup consolidated here |

## Migration Notes

- Dual-file template (MD + YAML) consolidated into single YAML
- 6 sections reduced to 5 + glossary (workflow merged into intro, refs into traceability)
- Sequential element IDs replaced by hash-based IDs (`EARS.NN.{section}.xxxx`)
- PRD EARS appendix content (timing profiles, boundary values) incorporated as `_guidance`
- Changelog: `changelog/CHANGELOG_v0.4.0.md`
