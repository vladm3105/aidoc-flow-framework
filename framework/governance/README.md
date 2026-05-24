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
| `ADAPTATION.md` | The project-adaptation surface — how a consuming project adapts the flow without forking. |
| `ADAPTATION_SURFACE.yaml` | Machine-readable closed knob registry behind `ADAPTATION.md`. |
| `DECISIONS.md` | Durable register of decisions about the spec and its governance (spec-affecting decisions graduate here). |

## CHG Overlay (`chg/`)

The `chg/` directory holds the Change Management overlay — a governance overlay
for managing changes to existing artifacts (gate definitions, the CHG template,
approval and post-mortem companions). It also carries **GATE-SPEC**, the *meta*
gate that governs changes to the `framework/` spec itself (CHG-D1).

CHG is **spec-only** in the framework: the spec defines the gates and their
checks; each consuming platform implements the enforcement against this shared
contract (a record validator for the record-level checks, continuous
integration for the diff-aware and suite checks, protected-branch review for the
human approval). This model is recorded formally as **GD-01** in `DECISIONS.md`.
