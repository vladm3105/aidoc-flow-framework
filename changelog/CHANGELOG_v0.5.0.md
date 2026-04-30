# CHANGELOG v0.5.0

**Release Date**: 2026-03-29
**Type**: Minor (BDD Template Unification)

## Summary

Unified the BDD (Layer 4) artifact into a single YAML template, completing the first four layers of the SDD workflow. BDD instances remain `.feature` (Gherkin) files — the template is YAML with Gherkin syntax embedded in `_guidance` and `_example` fields.

## Changes

### BDD Layer Unification

**New**: `ucx_flow_v3/04_BDD/BDD-TEMPLATE.yaml` (365 lines, schema v1.0)

**Replaced** (6 files, 4,108 lines → 365 lines):

| File | Lines | Disposition |
|------|-------|-------------|
| `BDD-MVP-TEMPLATE.feature` | 180 | Archived — Gherkin syntax now in `_example` fields |
| `BDD-MVP-TEMPLATE.yaml` | 259 | Archived |
| `BDD_MVP_SCHEMA.yaml` | 628 | Archived |
| `BDD_MVP_CREATION_RULES.md` | 1,270 | Guidance embedded as `_guidance` fields |
| `BDD_MVP_VALIDATION_RULES.md` | 815 | Validation via mcp_ucx tools |
| `BDD_MVP_QUALITY_GATE_VALIDATION.md` | 956 | Quality gates via mcp_ucx tools |

**Archived**: 20+ files + scripts/ + examples/ + 2 backups → `BDD_v1_archive/`

### Design Decision: Single YAML (No .feature Template)

BDD instances are `.feature` files but the template is YAML — consistent with
BRD/PRD/EARS. AI generates valid Gherkin from YAML guidance. No mcp_ucx code changes.

### Template Structure (5 sections)

| # | Section |
|---|---------|
| 1 | Document Control (ADR-Ready score, cumulative tags) |
| 2 | Feature Definition (Gherkin tags, background, splitting rules) |
| 3 | Scenario Structure (5 categories: success, error, recovery, parameterized, optional) |
| 4 | Traceability (upstream EARS/PRD/BRD, downstream ADR) |
| 5 | Glossary |

### Embedded Gherkin Reference

Complete Gherkin examples in `_example` fields:
- Feature header with cumulative tags (@brd + @prd + @ears)
- Scenario with Given-When-Then + threshold references
- Scenario Outline with Examples table
- Error and recovery scenario patterns

### Hash-Based Element IDs

Old: `BDD.NN.14.SS` (type code 14 = Scenario)
New: `BDD.NN.03.xxxx` (Section 3, hash-based)

### Execution Environment

Documented in template: QA STAGING ONLY — BDD tests run after staging deployment,
not in CI pipeline. Use UTEST/ITEST for CI.

### mcp_ucx Updates

- Copied `BDD-TEMPLATE.yaml` to `mcp_ucx/templates/`
- Removed `mcp_ucx/templates/BDD-MVP-TEMPLATE.feature`
- BDD prompts: no old references found, no changes needed
- No source code changes (resolve_template_path finds .yaml natively)

## Four Layers Unified

| Layer | C4 Level | Template | Readiness Score | Version |
|-------|----------|----------|-----------------|---------|
| BRD (Layer 1) | Context | `BRD-TEMPLATE.yaml` | PRD-Ready | v0.2.0 |
| PRD (Layer 2) | Container | `PRD-TEMPLATE.yaml` | EARS-Ready | v0.3.0 |
| EARS (Layer 3) | Transition | `EARS-TEMPLATE.yaml` | BDD-Ready | v0.4.0 |
| BDD (Layer 4) | Transition | `BDD-TEMPLATE.yaml` | ADR-Ready | v0.5.0 |

## Backward Compatibility

- mcp_ucx test suite: 173 passed, 1 pre-existing failure, 0 regressions
- BDD template resolution verified via `resolve_template_path`

## Validation Evidence

- YAML syntax: `yaml.safe_load()` passes
- Template resolution: `resolve_template_path()` finds `BDD-TEMPLATE.yaml`
- mcp_ucx full suite: 173 passed, 0 regressions
- No stale `BDD-MVP-TEMPLATE` references outside archives
