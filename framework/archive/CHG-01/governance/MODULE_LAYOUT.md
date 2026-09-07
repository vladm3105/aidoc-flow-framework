# Module Folder Layout

Defines the project module directory structure and naming conventions.
Modules are the single source of truth for everything about a project part —
overview, refined decisions, invariants, constraints, seed references, business
rules, acceptance criteria.

## Directory Structure

```
docs/
├── modules/                          # Source material (architect → product owner)
│   ├── MODULE-00_index.md            # Master module registry
│   │
│   ├── MODULE-01_server/             # Directory form (multi-file modules)
│   │   ├── README.md                 # Overview, principles, constraints
│   │   ├── architecture.svg          # Architecture diagram
│   │   ├── decisions.md              # Design decisions + seed references
│   │   └── constraints.md            # Invariants, business rules, dependencies
│   │
│   ├── MODULE-12_observability/      # Complex module (6+ files)
│   │   ├── README.md                 # Overview, principles, invariants
│   │   ├── architecture.svg
│   │   ├── log_export.md             # Log export plugin interface
│   │   ├── metrics.md                # Business metrics catalog (40+)
│   │   ├── dashboards_alerts.md      # Dashboards, alerts, SLOs
│   │   └── agent_surface.md          # Future LLM/agent instrumentation
│   │
│   └── MODULE-03_auth.md             # Flat form (single-file modules)
│
├── seed/                             # Frozen input (architect + stakeholders)
│   ├── architecture/
│   │   ├── 00_index.md
│   │   └── ...
│   ├── agent-surface/
│   │   ├── 00_index.md
│   │   └── ...
│   └── adr/                          # Seed-level ADRs (web-specific)
│
├── sdd/                              # Formal SDD chain (dev team)
│   ├── 01_BRD/                       # Layer 1 — Business Requirements
│   ├── 02_PRD/                       # Layer 2 — Product Requirements
│   ├── 03_EARS/                      # Layer 3 — Formal Requirements
│   ├── 04_BDD/                       # Layer 4 — Acceptance Scenarios
│   ├── 05_ADR/                       # Layer 5 — Architecture Decisions
│   ├── 06_SPEC/                      # Layer 6 — Implementation Specs
│   ├── 07_TDD/                       # Layer 7 — Test Definitions
│   ├── 08_IPLAN/                     # Layer 8 — Implementation Plans
│   └── 09-CHG/                       # Change Records + archives
│
└── governance/                       # Project governance rules
    ├── DOC_GOVERNANCE_CORE.md           # All rules (canonical)
    ├── DECISION_WORKFLOW.md          # Seed vs Module vs SDD ADR
    ├── SELF_LEARNING.md             # Self-learning loop governance
    └── MODULE_LAYOUT.md             # This document
```

## Rules

### 1. Module location
All module docs live in `docs/modules/`. This is the single source of truth
for everything about a project part.

### 2. Flat file vs directory

| Form | When | Example |
|------|------|---------|
| **Flat file** | Module has ≤1 file (~800 lines or less) | `MODULE-03_auth.md` |
| **Directory** | Module has 2+ files (split by topic) | `MODULE-12_observability/` |

**Trigger to convert flat → directory:** When a single module file exceeds
~1000 lines OR when the module naturally splits into distinct subsystems
(e.g., metrics catalog, dashboards, agent surface are separate concerns).

### 3. Directory naming
```
MODULE-NN_descriptive-slug/       # Directory (multi-file)
MODULE-NN_descriptive-slug.md     # Flat file (single-file)
```
Use lowercase, hyphens for spaces. Match the slug between directory name and
all internal references.

### 4. README.md is the entry point
Every module directory has a `README.md` that contains:
- Module overview and purpose
- Design principles and invariants
- Constraints and dependencies
- References to other files in the directory

When a reader opens the module, `README.md` is always the first thing they see.

### 5. Diagrams stay with their module
SVG diagrams live inside the module directory or alongside the flat file.
No separate `diagrams/` directory.

### 6. Multi-file module structure

```
MODULE-NN_slug/
├── README.md           # Required: overview, principles, constraints
├── architecture.svg    # Optional: architecture diagram
├── <topic>.md          # Optional: specific subsystem (repeatable)
```

**File naming for topic files:** Use lowercase, hyphens. Name by subsystem:
- `decisions.md` — design decisions and seed references
- `constraints.md` — invariants, business rules
- `metrics.md` — metrics catalog
- `dashboards_alerts.md` — dashboards and alerting rules
- `agent_surface.md` — LLM/agent specific content
- `<topic>.md` — any distinct subsystem

### 7. Seed stays frozen, separate
Seed docs (`docs/seed/`) are frozen input to the BRD. They are not part of
the module. Modules reference seed docs but do not duplicate them.

### 8. SDD stays separate
SDD docs (`docs/sdd/`) are the formal chain. Modules are source material for
BRDs. The SDD chain formalizes from modules, not from scattered seed fragments.

## Migration Guide

### Existing flat modules (no migration needed unless splitting)
```
MODULE-01_server.md        → stays flat
MODULE-02_client.md        → stays flat
MODULE-03_auth.md          → stays flat
...
```

### Complex modules (split when >1000 lines or distinct subsystems)
```
MODULE-12_observability.md          → MODULE-12_observability/
  ├── README.md                     ← overview from header
  ├── metrics.md                    ← Business Metrics Catalog
  ├── dashboards_alerts.md          ← Dashboards, Alerts, SLOs
  └── agent_surface.md              ← Layer 5 (LLM/Agent)
```

### Index update
After migration, update `MODULE-00_index.md` to reflect directory form:
```markdown
| MODULE-01 | Server | Directory | Approved |
| MODULE-12 | Observability | Directory | Approved |
| MODULE-03 | Auth | Flat | Approved |
```

## Cross-References

- `DECISION_WORKFLOW.md` — Authorship boundaries
- `registry/LAYER_REGISTRY.yaml` — Layer definitions
- `layers/01_BRD/README.md` — BRD layer (consumes modules)
