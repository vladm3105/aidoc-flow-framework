# PLAN-013: CHG Governance Framework Simplification

**Status**: Complete
**Created**: 2026-03-30
**Scope**: Simplify CHG (Change Management) into single YAML template + gate definitions
**Risk**: Low — CHG is governance overlay, not a lifecycle layer

---

## Problem

CHG has 30+ files across 6 directories for a change management process:

| Directory | Files | Lines | Purpose |
|-----------|-------|-------|---------|
| Root | 7 | 2,279 | Templates, schema, rules, guides |
| gates/ | 6 | — | Gate definitions (GATE-01 through GATE-12) |
| scripts/ | 7 | — | Validation scripts |
| sources/ | 5 | — | Change source guides (upstream/midstream/downstream/external/feedback) |
| templates/ | 3 | — | Emergency, approval form, post-mortem templates |
| workflows/ | 5 | — | Per-source workflows + emergency |

Most content is duplicated across source guides and workflows. The core process is:
1. Classify change (L1/L2/L3)
2. Route to gate (GATE-01/05/09/12)
3. Execute workflow (assess → update → verify)
4. Record change

---

## Design Decision: NOT a Lifecycle Layer

CHG is a **governance overlay** — it triggers when changing existing SDD artifacts.
It is NOT part of the BRD→TASKS document flow. Therefore:
- NOT added to `mcp_ucx/templates/`
- NOT assigned a C4 level
- NOT part of the readiness score chain
- Gate definitions are process documents, not artifact templates

---

## Target State

```text
CHG/
├── CHG-TEMPLATE.yaml               ← single template (L1/L2/L3 via change_level field)
├── CHG-00_index.md                  ← change registry (keep, update refs)
├── README.md                        ← concise guide (~80 lines)
├── gates/                           ← KEEP (6 files — process definitions)
│   ├── GATE-01_BUSINESS_PRODUCT.md
│   ├── GATE-05_ARCHITECTURE_CONTRACT.md
│   ├── GATE-09_DESIGN_TEST.md
│   ├── GATE-12_IMPLEMENTATION.md
│   ├── GATE_ERROR_CATALOG.md
│   └── GATE_INTERACTION_DIAGRAM.md
├── templates/                       ← KEEP (companion documents used during CHG process)
│   ├── GATE_APPROVAL_FORM.md
│   └── POST_MORTEM-TEMPLATE.md
└── CHG_v1_archive/                  ← deprecated files
```

---

## Phase 1: Analysis — What to Keep vs Archive

### KEEP (active)

| File/Dir | Reason |
|----------|--------|
| `gates/` (6 files) | Process definitions — distinct from template |
| `CHG-00_index.md` | Change registry |

### ARCHIVE (embed key content as `_guidance`)

| File/Dir | Content to Embed | Archive Reason |
|----------|-----------------|----------------|
| `CHG-TEMPLATE.md` (223 lines) | L3 major change structure | Replaced by unified YAML |
| `CHG-MVP-TEMPLATE.md` (137 lines) | L2 minor change structure | Merged into unified YAML |
| `CHG_MVP_SCHEMA.yaml` (567 lines) | Validation via mcp_ucx | Schema archived |
| `CHG_MVP_CREATION_RULES.md` (244 lines) | Key rules → `_guidance` | Rules embedded |
| `CHANGE_CLASSIFICATION_GUIDE.md` (369 lines) | L1/L2/L3 criteria → `_guidance` | Guide embedded |
| `CHANGE_MANAGEMENT_GUIDE.md` (643 lines) | Process overview → `_guidance` | Guide embedded |
| `sources/` (5 files, 2,141 lines) | Routing tables + summaries → `_guidance` (detailed guides archived as reference) | Too large to embed fully |
| `workflows/` (5 files, 1,770 lines) | Step summaries → `_guidance` (DESIGN_WORKFLOW maps to GATE-09) | Too large to embed fully |
| `templates/CHG-EMERGENCY-TEMPLATE.md` (231 lines) | Emergency change → Section 8 in unified template | Merged into template |

**KEEP active** (companion documents used during CHG process):
- `templates/GATE_APPROVAL_FORM.md` (254 lines) — filled out during gate approval
- `templates/POST_MORTEM-TEMPLATE.md` (284 lines) — required after emergency changes
| `scripts/` (7 files) | Validation via mcp_ucx | Scripts archived |

---

## Phase 2: Create CHG-TEMPLATE.yaml

Single template that handles all change levels via `change_level` field:

### Metadata

- `document_type: "chg-document"`
- `change_level`: L1 (trivial) | L2 (minor) | L3 (major)
- No `c4_level` — governance overlay
- No diagram tags
- No readiness score — uses gate approval instead

### Change Level Routing (in `_guidance`)

| Level | Scope | Gate | Process |
|-------|-------|------|---------|
| L1 | Typo, formatting, clarification | None — direct commit | Fix → commit → done |
| L2 | Section update, requirement refinement | Peer review | Assess → update → verify |
| L3 | Cross-layer change, new requirements | Formal gate (GATE-01/05/09/12) | Full CHG process |

### Change Source Routing (in `_guidance`)

| Source | Description | Entry Gate |
|--------|------------|------------|
| Upstream | BRD/PRD change cascading down | GATE-01 |
| Midstream | ADR/SYS change affecting neighbors | GATE-05 |
| Downstream | SPEC/TASKS change propagating up | GATE-09 |
| External | Regulatory, vendor, market change | GATE-01 |
| Feedback | Production feedback, user issues | GATE-12 |

### Sections

| # | Section | Content |
|---|---------|---------|
| 1 | Change Control | ID, status, level, source, author, date, gate |
| 2 | Change Description | What changed, why, business justification |
| 3 | Impact Assessment | Affected layers, artifacts, downstream impact |
| 4 | Implementation | Steps taken, artifacts modified |
| 5 | Verification | How the change was validated |
| 6 | Gate Approval | Gate reference, approver, date (L3 only) |
| 7 | Rollback Plan | How to reverse if change fails (L2/L3) |
| 8 | Emergency Change | Conditional — only for emergency bypass (unique ID: CHG-EMG-{YYYYMMDD-HHMM}) |
| — | Glossary | Terms |

Section 8 (Emergency Change) is CONDITIONAL — only populated when `change_level: emergency`.
Requires mandatory post-mortem within 48 hours (use `templates/POST_MORTEM-TEMPLATE.md`).

---

## Phase 3: Archive

Move to `CHG_v1_archive/`:
- `CHG-TEMPLATE.md`
- `CHG-MVP-TEMPLATE.md`
- `CHG_MVP_SCHEMA.yaml`
- `CHG_MVP_CREATION_RULES.md`
- `CHANGE_CLASSIFICATION_GUIDE.md`
- `CHANGE_MANAGEMENT_GUIDE.md`
- `sources/`
- `workflows/`
- `templates/`
- `scripts/`
- `README.md` (old)

**DO NOT archive**:
- `gates/` (6 files — active process definitions)
- `templates/GATE_APPROVAL_FORM.md` (companion doc — used during gate approval)
- `templates/POST_MORTEM-TEMPLATE.md` (companion doc — required after emergency changes)
- `CHG-00_index.md` (active registry)

---

## Phase 4: Update CHG-00_index.md + Create README.md

- Update template reference
- Create concise README explaining CHG as governance overlay
- Include change level routing table and gate references

---

## Phase 5: Validation

- Verify YAML valid
- No mcp_ucx template copy needed (governance, not lifecycle)
- No test suite impact expected
- Changelog note (not a version bump — CHG is outside the 11-layer system)

---

## Key Differences from Layer Migrations

| Aspect | Layers 1-11 | CHG |
|--------|-----------|-----|
| Type | Lifecycle artifact | **Governance overlay** |
| In workflow chain | Yes (BRD→TASKS) | **No — triggers on-demand** |
| mcp_ucx template | Yes | **No** |
| C4 level | Various | **None** |
| Readiness score | Yes | **Gate approval instead** |
| Multiple templates | Merged into one | **Merged + gates kept separate** |
| Downstream | Next layer | **Affected artifacts across any layer** |

---

## Decisions (Resolved)

1. **NOT added to mcp_ucx**: CHG is governance, not lifecycle.
2. **Gates kept as separate files**: They define approval processes, not artifact structure.
3. **All change levels in one template**: `change_level` field determines which sections apply.
4. **Change sources embedded**: 5 source guides → `_guidance` routing table.
5. **Workflows embedded**: 5 workflows → `_guidance` steps per change level.
6. **Emergency change**: Conditional section + post-mortem requirement in `_guidance`.
7. **No version bump**: CHG is outside the 11-layer versioning system.

---

## Future Work

- Consider adding CHG validation to mcp_ucx as a governance tool (not a lifecycle tool)
- IMPLEMENTATION_PLAN modernization (from PLAN-012 note)
