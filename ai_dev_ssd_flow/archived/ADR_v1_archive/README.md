# ADR v1 Archive

**Archived**: 2026-03-29
**Reason**: Replaced by unified `ADR-TEMPLATE.yaml` (schema v1.0)

## Archived Files

| File | Replaced By |
|------|-------------|
| `ADR-MVP-TEMPLATE.md` | `../ADR-TEMPLATE.yaml` |
| `ADR-MVP-TEMPLATE.yaml` | `../ADR-TEMPLATE.yaml` |
| `ADR_MVP_SCHEMA.yaml` | Validation via mcp_sdd tools |
| `ADR_MVP_CREATION_RULES.md` | `_guidance` fields in `../ADR-TEMPLATE.yaml` |
| `ADR_MVP_VALIDATION_RULES.md` | Validation logic in mcp_sdd `sdd_validate` |
| `ADR_MVP_QUALITY_GATE_VALIDATION.md` | Quality gates via mcp_sdd `sdd_score_validate` |
| `ADR-MVP-TEMPLATE_FIX_PLAN.md` | Completed fix tracking (historical) |
| `ADR-00_TRACEABILITY_MATRIX-TEMPLATE.md` | Per-ADR Section 9 + AI-generated |
| `ADR_AI_VALIDATION_DECISION_GUIDE.md` | Empty scaffold |
| `ADR_VALIDATION_STRATEGY.md` | mcp_sdd tools |
| `ADR_VALIDATION_COMMANDS.md` | mcp_sdd tools |
| `REVIEW_REPORT.md` | Historical review report |
| `FIXES_SUMMARY.md` | Historical fix summary |
| `README_old.md` | New concise README |
| `examples/` | AI generates examples on demand |
| `scripts/` | Validation via mcp_sdd tools |

## Not Archived (Active Instances)

- `ADR-00_ai_powered_documentation_assistant_architecture.md` — active ADR instance
- `ADR-CTR_SEPARATE_FILES_POLICY.md` — active ADR instance
- `ADR-00_index.md` — active registry

## Migration Notes

- 11 sections reduced to 10 + glossary + lifecycle appendix
- Sequential element IDs replaced by hash-based (`ADR.NN.{section}.xxxx`)
- Old BRD refs `BRD.NN.32.SS` → `BRD.NN.08.xxxx`
- Originating topic now points to PRD Section 14 (not BRD directly)
- ADR status lifecycle: Proposed → Accepted → Deprecated → Superseded
- Changelog: `changelog/CHANGELOG_v0.6.0.md`
