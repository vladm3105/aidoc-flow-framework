# BDD v1 Archive

**Archived**: 2026-03-29
**Reason**: Replaced by unified `BDD-TEMPLATE.yaml` (schema v1.0)

## Archived Files

| File | Replaced By |
|------|-------------|
| `BDD-MVP-TEMPLATE.feature` | `../BDD-TEMPLATE.yaml` (Gherkin in `_example` fields) |
| `BDD-MVP-TEMPLATE.yaml` | `../BDD-TEMPLATE.yaml` |
| `BDD_MVP_SCHEMA.yaml` | Validation via mcp_sdd tools |
| `BDD_MVP_CREATION_RULES.md` | `_guidance` fields in `../BDD-TEMPLATE.yaml` |
| `BDD_MVP_VALIDATION_RULES.md` | Validation logic in mcp_sdd `sdd_validate` |
| `BDD_MVP_QUALITY_GATE_VALIDATION.md` | Quality gates via mcp_sdd `sdd_score_validate` |
| `BDD-MVP-TEMPLATE_FIX_PLAN.md` | Completed fix tracking (historical) |
| `BDD-00_TRACEABILITY_MATRIX-TEMPLATE.md` | Per-BDD Section 4 + AI-generated |
| `BDD_GENERATION_CHECKLIST.md` | Key rules embedded in `_guidance` |
| `BDD_PRE_GENERATION_CHECKLIST.md` | Key rules embedded in `_guidance` |
| `BDD_AI_AGENT_EXTENSION.md` | AI-agent patterns embedded in `_guidance` |
| `BDD_AI_VALIDATION_DECISION_GUIDE.md` | Empty scaffold |
| `BDD_VALIDATION_STRATEGY.md` | mcp_sdd tools |
| `BDD_VALIDATION_COMMANDS.md` | mcp_sdd tools |
| `BDD-AGGREGATOR-TEMPLATE.feature` | Splitting rules embedded in `_guidance` |
| `REVIEW_REPORT.md` | Historical review report |
| `FIXES_SUMMARY.md` | Historical fix summary |
| `README_old.md` | New concise README |
| `examples/` | AI generates examples on demand |
| `scripts/` | Validation via mcp_sdd tools |

## Migration Notes

- Dual-file (`.feature` + `.yaml`) consolidated into single YAML template
- Gherkin syntax examples embedded in `_guidance` and `_example` fields
- BDD instances (actual test files) remain `.feature` format
- Sequential element IDs (`BDD.NN.14.SS`) replaced by hash-based (`BDD.NN.03.xxxx`)
- Changelog: `changelog/CHANGELOG_v0.5.0.md`
