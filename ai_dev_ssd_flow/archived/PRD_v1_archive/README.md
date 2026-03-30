# PRD v1 Archive

**Archived**: 2026-03-29
**Reason**: Replaced by unified `PRD-TEMPLATE.yaml` (schema v1.0)

## Archived Files

| File | Replaced By |
|------|-------------|
| `PRD-MVP-TEMPLATE.md` | `../PRD-TEMPLATE.yaml` |
| `PRD-MVP-TEMPLATE.yaml` | `../PRD-TEMPLATE.yaml` |
| `PRD_MVP_SCHEMA.yaml` | Validation via mcp_sdd tools |
| `PRD_MVP_CREATION_RULES.md` | `_guidance` fields in `../PRD-TEMPLATE.yaml` |
| `PRD_MVP_VALIDATION_RULES.md` | Validation logic in mcp_sdd `sdd_validate` |
| `PRD_MVP_QUALITY_GATE_VALIDATION.md` | Quality gates in mcp_sdd `sdd_score_validate` |
| `PRD-MVP-TEMPLATE_FIX_PLAN.md` | Completed fix tracking (historical) |
| `PRD-00_threshold_registry_template.md` | Inline thresholds with `@threshold:` tags |
| `PRD-00_TRACEABILITY_MATRIX-TEMPLATE.md` | Per-PRD Section 14 + AI-generated |
| `PRD_VALIDATION_STRATEGY.md` | mcp_sdd tools |
| `PRD_VALIDATION_COMMANDS.md` | mcp_sdd tools |
| `PRD_AI_VALIDATION_DECISION_GUIDE.md` | Empty scaffold |
| `README_old.md` | New concise README |
| `examples/` | AI generates examples on demand |
| `scripts/` | All deprecated, validation via mcp_sdd |
| `backup_2026-02-26/` | Old backup consolidated here |

## Migration Notes

- Dual-file template (MD + YAML) consolidated into single YAML
- 21 sections + 3 appendices reduced to 15 sections + glossary
- Sequential element IDs replaced by hash-based IDs (`PRD.NN.{section}.xxxx`)
- EARS Enhancement Appendix preserved in `tmp/EARS_APPENDIX_FROM_PRD.md`
- Changelog: `changelog/CHANGELOG_v0.3.0.md`
