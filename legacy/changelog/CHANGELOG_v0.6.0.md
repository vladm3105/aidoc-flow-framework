# CHANGELOG v0.6.0

**Release Date**: 2026-03-29
**Type**: Minor (ADR Template Unification)

## Summary

Unified the ADR (Layer 5) artifact into a single YAML template, completing the first five layers of the SDD workflow. ADR serves as the decision bridge between Container (PRD) and Component (SYS) in the C4 model.

## Changes

### ADR Layer Unification

**New**: `ucx_flow_v3/05_ADR/ADR-TEMPLATE.yaml` (466 lines, schema v1.0)

**Replaced** (6 files, 3,118 lines → 466 lines):

| File | Lines | Disposition |
|------|-------|-------------|
| `ADR-MVP-TEMPLATE.md` | 406 | Archived |
| `ADR-MVP-TEMPLATE.yaml` | 363 | Archived |
| `ADR_MVP_SCHEMA.yaml` | 460 | Archived |
| `ADR_MVP_CREATION_RULES.md` | 500 | Guidance embedded as `_guidance` fields |
| `ADR_MVP_VALIDATION_RULES.md` | 422 | Validation via mcp_ucx tools |
| `ADR_MVP_QUALITY_GATE_VALIDATION.md` | 967 | Quality gates via mcp_ucx tools |

**Archived**: 15+ files + scripts/ + examples/ + backup → `ADR_v1_archive/`

**Active instances kept** (NOT archived):
- `ADR-00_ai_powered_documentation_assistant_architecture.md`
- `ADR-CTR_SEPARATE_FILES_POLICY.md`

### Section Structure (11 → 10 + glossary + lifecycle appendix)

Old Section 11 (MVP Lifecycle) moved to appendix, consistent with BRD/EARS pattern.

### Key ADR-Specific Features

- **Status lifecycle**: Proposed → Accepted → Deprecated → Superseded (different from other layers)
- **Originating topic**: Points to PRD Section 14 (`@prd: PRD.NN.14.xxxx`), not BRD directly
- **Decision bridge**: Synthesizes PRD (topics), EARS (constraints), BDD (scenarios)
- **Alternatives format**: 2-3 options with pros/cons/cost/fit + rejection reasons
- **Context-Decision-Consequences**: Core ADR pattern preserved and embedded as `_guidance`

### Hash-Based Element IDs

| Old Code | Old Format | New Format |
|----------|-----------|------------|
| 10 (Decision) | `ADR.NN.10.SS` | `ADR.NN.03.xxxx` |
| 12 (Alternative) | `ADR.NN.12.SS` | `ADR.NN.04.xxxx` |
| 13 (Consequence) | `ADR.NN.13.SS` | `ADR.NN.05.xxxx` |

### Upstream BRD References Updated

Old: `BRD.NN.32.SS` (type code 32 = ADR topic)
New: `BRD.NN.08.xxxx` (BRD Section 8, hash-based)

### Downstream Expanded

ADR downstream now includes SYS (layer 6) + REQ (layer 7) + SPEC (layer 9).

### mcp_ucx Updates

- Copied `ADR-TEMPLATE.yaml` to `mcp_ucx/templates/`
- Removed `mcp_ucx/templates/ADR-MVP-TEMPLATE.md`
- ADR prompts: no old references found, no changes needed
- No source code changes

## Five Layers Unified

| Layer | C4 Position | Template | Readiness Score | Version |
|-------|-------------|----------|-----------------|---------|
| BRD (Layer 1) | Context | `BRD-TEMPLATE.yaml` | PRD-Ready | v0.2.0 |
| PRD (Layer 2) | Container | `PRD-TEMPLATE.yaml` | EARS-Ready | v0.3.0 |
| EARS (Layer 3) | Transition | `EARS-TEMPLATE.yaml` | BDD-Ready | v0.4.0 |
| BDD (Layer 4) | Transition | `BDD-TEMPLATE.yaml` | ADR-Ready | v0.5.0 |
| ADR (Layer 5) | Decision bridge | `ADR-TEMPLATE.yaml` | SYS-Ready | v0.6.0 |

## Validation Evidence

- YAML syntax: `yaml.safe_load()` passes
- Template resolution: `resolve_template_path()` finds `ADR-TEMPLATE.yaml`
- mcp_ucx full suite: 173 passed, 0 regressions
- No stale `ADR-MVP-TEMPLATE` references outside archives
