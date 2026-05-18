# P1-T1 Audit — `legacy/ucx_flow_v3/`

Classification of the legacy SDD v3.2 spec tree into **engine-agnostic** content
(extract into `framework/`) vs **engine-specific** content (belongs to a
platform, not the shared spec) vs **drop** (instance data / generated / history).

| Field        | Value                                      |
|--------------|--------------------------------------------|
| Task         | P1-T1                                      |
| Audited tree | `legacy/ucx_flow_v3/` — 49 files           |
| Completed    | 2026-05-18T17:45:00Z                       |
| Feeds        | P1-T2 (layers), P1-T3 (registry), P1-T4 (governance) |

## Legend

- **AGNOSTIC** — engine-neutral spec; copy into `framework/`.
- **MIXED** — mostly agnostic but contains engine-specific sections that must be
  stripped on extraction (sections noted).
- **INSTANCE** — project-instance data, not spec; do not extract.
- **DROP** — generated output or migration history; do not extract.

## Summary

| Disposition | Files | Target |
|-------------|-------|--------|
| AGNOSTIC    | 28    | `framework/` |
| MIXED       | 9     | `framework/` (after stripping) |
| INSTANCE    | 9     | not extracted |
| DROP        | 3     | not extracted |

## Root files

| File | Class | Target / Note |
|------|-------|---------------|
| `LAYER_REGISTRY.yaml` | AGNOSTIC | `framework/registry/` — authoritative layer defs, C4 map, `id_patterns`. **Core of P1-T3.** |
| `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` | AGNOSTIC | `framework/` — methodology overview |
| `DOC_GOVERNANCE_CORE.md` | AGNOSTIC | `framework/governance/` |
| `ID_NAMING_STANDARDS.md` | AGNOSTIC | `framework/governance/` |
| `TRACEABILITY.md` | AGNOSTIC | `framework/governance/` |
| `THRESHOLD_NAMING_RULES.md` | AGNOSTIC | `framework/governance/` — large (31 KB); re-review content during P1-T4 |
| `TESTING_STRATEGY_TDD.md` | AGNOSTIC | `framework/` |
| `QUICK_REFERENCE.md` | AGNOSTIC | `framework/` — fix internal links after restructure |
| `AI_ASSISTANT_RULES.md` | AGNOSTIC | `framework/` — generic agent guidance, no engine binding |
| `DIAGRAM_STANDARDS.md` | MIXED | `framework/governance/` — strip `.claude/skills/...` cross-refs (Claude-Code-specific); the Mermaid standard itself is agnostic |
| `README.md` | MIXED | `framework/README.md` — **drop** the "UCX Hermes Review/Remediation Runtime Notes" section and Hermes/Codex agent-split prose; keep layer model, C4 model, layer flow |
| `data_consistency_report.json` | DROP | generated validator output |

## Layer directories `01_BRD` … `08_IPLAN`

| File pattern | Class | Target / Note |
|--------------|-------|---------------|
| `{TYPE}-TEMPLATE.yaml` (×8) | AGNOSTIC | `framework/layers/` — the spec contracts. **Core of P1-T2.** |
| `{TYPE}-00_index.{md,yaml}` (×8) | INSTANCE | project registries ("tracks planned/active docs per project") — not spec |
| `README.md` (×8) | MIXED | `framework/layers/` — keep layer description / C4 mapping / element-ID rules; **strip** per-layer "MCP Tools (ucx_hermes)" and "Template Sync Rule → ucx_hermes/templates/" sections (Hermes-specific) |

## CHG overlay `CHG/`

Change management is **deferred** until post-Phase 5 (ROADMAP CHG-D1/D2), but the
CHG *spec* is engine-agnostic and is extracted now so `framework/` is complete.

| File | Class | Target |
|------|-------|--------|
| `CHG/README.md` | AGNOSTIC | `framework/governance/chg/` |
| `CHG/CHG-TEMPLATE.yaml` | AGNOSTIC | `framework/governance/chg/` |
| `CHG/CHG-00_index.md` | INSTANCE | not extracted |
| `CHG/gates/*.md` (×7) | AGNOSTIC | `framework/governance/chg/gates/` |
| `CHG/templates/*.md` (×2) | AGNOSTIC | `framework/governance/chg/templates/` |

## Drop

| File | Reason |
|------|--------|
| `data_consistency_report.json` | generated report |
| `plans/CHG_MIGRATION_PLAN.md` | historical v2→v3 migration record |
| all `*-00_index.*` files | project-instance registries (counted under INSTANCE) |

## Engine-specific content found (must NOT enter `framework/`)

1. `README.md` § "UCX Hermes Review/Remediation Runtime Notes" — saga modes,
   `UCX_REVIEW_*` env vars, executor defaults. → Hermes platform docs.
2. Per-layer `README.md` § "MCP Tools (ucx_hermes)" — `sdd-lifecycle` MCP
   server, `sdd_create` / `sdd_validate` / etc. → Hermes platform docs.
3. Per-layer `README.md` § "Template Sync Rule" — `ucx_hermes/templates/`
   runtime-copy rule. Obsolete: `framework/` becomes the single source; each
   platform references it directly. → drop, do not reproduce.
4. `DIAGRAM_STANDARDS.md` cross-refs to `.claude/skills/mermaid-gen` /
   `charts-flow` — Claude-Code-specific. → strip; the Mermaid rule stays.

## Open questions for P1-T2..T4 — RESOLVED

- **Index files:** ship per-layer index templates in `framework/` — resolved
  by D-0005.
- **`framework/` version:** start at `0.1.0` with `derived_from: "SDD v3.2"` —
  resolved by D-0006.
- **CHG placement:** `framework/governance/chg/`, spec-only (no enforcement)
  until post-Phase 5.

## Recommended target layout (input to P1-T2..T4)

```
framework/
├── README.md                       # from root README (Hermes notes stripped)
├── VERSION                         # P1-T6
├── SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
├── QUICK_REFERENCE.md
├── AI_ASSISTANT_RULES.md
├── TESTING_STRATEGY_TDD.md
├── registry/
│   └── LAYER_REGISTRY.yaml
├── layers/
│   ├── 01_BRD/ … 08_IPLAN/         # TEMPLATE.yaml + stripped README.md
└── governance/
    ├── DOC_GOVERNANCE_CORE.md
    ├── ID_NAMING_STANDARDS.md
    ├── TRACEABILITY.md
    ├── DIAGRAM_STANDARDS.md
    ├── THRESHOLD_NAMING_RULES.md
    └── chg/                        # CHG spec — deferred, not enforced
        ├── README.md  CHG-TEMPLATE.yaml
        ├── gates/  templates/
```
