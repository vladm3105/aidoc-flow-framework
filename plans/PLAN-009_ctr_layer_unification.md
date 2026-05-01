# PLAN-009: CTR Layer Unification

**Status**: Complete
**Created**: 2026-03-29
**Scope**: Unify CTR (Layer 8) into single YAML template, same approach as Layers 1-7
**Depends on**: BRD-REQ unification (v0.2.0-v0.8.0) — all complete
**Risk**: Low — follows proven pattern

---

## Problem

CTR layer has the same dual-file pattern plus a unique characteristic — dual-file
contracts (`.md` narrative + `.yaml` OpenAPI spec):

| File | Lines | Role |
|------|-------|------|
| `CTR-MVP-TEMPLATE.md` | 629 | Human narrative template (14 sections + 2 appendices) |
| `CTR-MVP-TEMPLATE.yaml` | 393 | YAML/OpenAPI structure for autopilot |
| `CTR_MVP_SCHEMA.yaml` | 527 | OpenAPI 3.x validation schema |
| `CTR_MVP_CREATION_RULES.md` | 499 | Authoring guidance |
| `CTR_MVP_VALIDATION_RULES.md` | 500 | Post-creation validation |
| `CTR_MVP_QUALITY_GATE_VALIDATION.md` | 501 | Quality gates |
| **Total** | **3,049** | 6 files to consolidate |

Additionally to archive:

| File | Lines | Reason |
|------|-------|--------|
| `CTR-MVP-TEMPLATE_FIX_PLAN.md` | 1,165 | Completed fix tracking |
| `CTR-00_TRACEABILITY_MATRIX-TEMPLATE.md` | 369 | Redundant |
| `CTR_AI_VALIDATION_DECISION_GUIDE.md` | 65 | Empty scaffold |
| `CTR_VALIDATION_STRATEGY.md` | 121 | References scripts |
| `CTR_VALIDATION_COMMANDS.md` | 59 | References scripts |
| `REVIEW_REPORT.md` | 244 | Historical |
| `FIXES_SUMMARY.md` | 106 | Historical |
| `examples/` (4 files) | 1,499 | Old format examples |
| `scripts/` (12 files) | ~2,277 | Validation via mcp_ucx |
| `.backup_*` | — | Historical |
| `README.md` | 844 | Old version |

---

## Design Decision: Single YAML Template for CTR

CTR **instances** are dual-file (`.md` narrative + `.yaml` OpenAPI contract).
But the **template** is a single YAML, same as all other layers. The template
defines structure and guidance; AI generates dual-file instances from it.

This is the same approach as BDD: BDD instances are `.feature` files but the
template is YAML. CTR instances are `.md` + `.yaml` pairs but the template is YAML.

**No mcp_ucx code changes** — `resolve_template_path` finds `.yaml` natively.
Note: No CTR template existed in `mcp_ucx/templates/` — this migration adds one.

---

## C4 Model Position

CTR (like REQ) decomposes Component (SYS) into atomic units for Code (SPEC).
It is NOT a C4 level — it is a decomposition step.

```text
Component (SYS)  — system structure, interfaces, quality attributes
  └─ REQ/CTR     — decompose Component→Code into atomic units        ← this layer
Code (SPEC)      — implementation-ready specifications
```

No `c4_level.value` — use `_guidance` only.

---

## Target State

```text
08_CTR/
├── CTR-TEMPLATE.yaml      ← single source of truth
├── CTR-00_index.md          ← CTR registry
├── README.md                ← new, concise (~90 lines)
└── CTR_v1_archive/          ← all deprecated files
```

---

## Phase 1: Section Analysis

CTR has 14 sections + 2 appendices. Evaluate for the unified template.

### Keep (CTR-layer concerns)

| # | Section | Rationale |
|---|---------|-----------|
| 1 | Document Control | Metadata, contract status, SPEC-Ready score |
| 2 | Context | Problem statement, driving forces |
| 3 | Contract Definition | Overview, parties, communication pattern |
| 4 | Requirements Satisfied | Source REQ, business logic, thresholds |
| 5 | Interface Definition | Schema reference, endpoints/functions |
| 6 | Error Handling | Error codes, failure modes, recovery |
| 7 | Quality Attributes | Performance, reliability, security, observability |
| 8 | Versioning Strategy | Version policy, compatibility, deprecation |
| 9 | Examples | Success/failure/error response examples |
| 10 | Verification | Contract testing, BDD scenarios |
| 11 | Traceability | Upstream REQ/SYS, downstream SPEC |

### Evaluate for removal/merge

| # | Section | Assessment | Action |
|---|---------|-----------|--------|
| 12 | References | Merge into traceability | **MERGE** |
| App A | Alternatives Considered | ADR pattern, not CTR | **REMOVE** |
| App B | Implementation Notes | SPEC/TASKS owns this | **REMOVE** |

### Proposed structure: 11 sections + glossary

| # | Section |
|---|---------|
| 1 | Document Control |
| 2 | Context |
| 3 | Contract Definition |
| 4 | Requirements Satisfied |
| 5 | Interface Definition |
| 6 | Error Handling |
| 7 | Quality Attributes |
| 8 | Versioning Strategy |
| 9 | Examples |
| 10 | Verification |
| 11 | Traceability (absorbs old Section 12 References) |
| — | Glossary |

---

## Phase 2: Create CTR-TEMPLATE.yaml

- `metadata.c4_level`: `_guidance` only (decomposition step, no value)
- `metadata.diagram_standard`: sequence diagrams for contract interactions, no C4 tags
- `metadata.validation.tool: sdd_validate` / `server: mcp_ucx`
- `metadata.id_standard`: `{doc_type}.{doc_id}.{section_id}.{hash}`, SHA256
- `document_control.spec_ready_score` (downstream is SPEC)
- `document_control.contract_status`: Draft | Active | Deprecated | Superseded

### CTR-specific guidance to embed

| Source | Embed in | Content |
|--------|----------|---------|
| Creation Rules: Dual-file convention | `metadata._guidance` | .md narrative + .yaml OpenAPI instances |
| Creation Rules: OpenAPI 3.x structure | `interface_definition._guidance` | Schema, endpoints, components |
| Creation Rules: Versioning strategy | `versioning._guidance` | SemVer, compatibility rules, deprecation |
| Creation Rules: Contract testing | `verification._guidance` | Contract test patterns |
| Validation Rules: SPEC-Ready scoring | `metadata.validation._guidance` | 10-point rubric |

### Upstream Traceability (REQ → CTR)

```yaml
traceability:
  tags:
    - "@ctr: CTR-NN"
  upstream:
    - "@req: REQ.NN.04.xxxx"    # REQ interface definition
    - "@sys: SYS.NN.06.xxxx"    # SYS interface specification
```

### Downstream Traceability (CTR → SPEC)

```yaml
  downstream_expected:
    - type: SPEC
      layer: 9
      description: "Technical specifications implementing this contract"
```

---

## Phase 3-8: Standard Execution

- Phase 3: Archive to `CTR_v1_archive/`
- Phase 4: Update `CTR-00_index.md`
- Phase 5: Create new `README.md` (include dual-file instance convention)
- Phase 6: Copy to `mcp_ucx/templates/CTR-TEMPLATE.yaml` (NEW — no old to remove)
- Phase 7: Cross-ref updates (REQ/SYS downstream, update ADR-CTR_SEPARATE_FILES_POLICY.md refs)
- Phase 8: Tests, template resolution, changelog v0.9.0, roadmap

---

## Key Differences from Previous Migrations

| Aspect | Layers 1-7 | CTR |
|--------|-----------|-----|
| Instance format | Single file (.md or .feature) | Dual-file (.md + .yaml OpenAPI) |
| mcp_ucx template | Existed (to replace) | **NEW** (never existed) |
| Contract testing | N/A | Contract tests, BDD cross-refs |
| Versioning | Document version only | SemVer + compatibility + deprecation |
| C4 level | Various | None (decomposition step) |
| Readiness score | Various | SPEC-Ready |

---

## Decisions (Resolved)

1. **Single YAML template**: Template is YAML; instances are dual-file (.md + .yaml).
2. **Appendix A (Alternatives)**: REMOVE — ADR owns alternatives evaluation.
3. **Appendix B (Implementation Notes)**: REMOVE — SPEC/TASKS own implementation.
4. **Section 12 (References)**: MERGE into Section 11 (Traceability).
5. **Contract status**: Draft | Active | Deprecated | Superseded (similar to ADR lifecycle).
6. **mcp_ucx**: NEW template (no old file to remove).
7. **ADR-CTR_SEPARATE_FILES_POLICY.md**: Update stale SPEC/CTR template refs in Phase 7.
