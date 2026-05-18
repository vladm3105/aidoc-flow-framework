# Governance

Engine-agnostic governance standards for the SDD framework. These documents
define the rules that every artifact and platform must conform to, independent
of which engine executes the workflow.

## Documents

| File | Covers |
|------|--------|
| `DOC_GOVERNANCE_CORE.md` | Core governance principles — single source of truth, YAML-first templates, immutability, validation baseline. |
| `ID_NAMING_STANDARDS.md` | Document IDs, element IDs, traceability tags, and file-naming formats. |
| `TRACEABILITY.md` | The 8-layer traceability chain, cumulative tagging, and readiness gates. |
| `DIAGRAM_STANDARDS.md` | Mermaid-only diagram requirement and the C4 + DFD + sequence ownership model. |
| `THRESHOLD_NAMING_RULES.md` | Naming, boundary, and usage rules for thresholds, limits, and timing parameters. |

## CHG Overlay (`chg/`)

The `chg/` directory holds the Change Management overlay — a governance overlay
for managing changes to existing artifacts (gate definitions, the CHG template,
approval and post-mortem companions).

CHG is **spec-only** in the framework: it is extracted here for completeness but
is **not enforced**. Change-management enforcement is deferred until after the
Phase 5 cutover (see `ROADMAP.md`, CHG-D1/D2).
