# SDD Pipeline Cross-Document Index Sweep

## When to Run

After completing a full pipeline for a new document (any of BRD→PRD→EARS→BDD→ADR→SPEC→TDD→IPLAN), run a cross-document index sweep to register the new document across all project-level artifacts.

## Files to Update (in order)

| # | File | What to Add |
|---|------|-------------|
| 1 | `0N_TYPE/0N-00_index.md` | New document row in the Document Registry table |
| 2 | `CHANGELOG.md` | Entry under latest `[Unreleased]` section with version, lines, status |
| 3 | `plans/BRD-PLANNING-ROADMAP.md` | Update inventory table, architecture tree, status line |
| 4 | `plans/README.md` | Update planning document statuses + SDD artifact table |
| 5 | `plans/PLAN-NNN_*.md` | Mark plan status as COMPLETE when pipeline is done |
| 6 | `0N_TYPE/README.md` | Update Files table if it lists individual documents |
| 7 | Upstream documents | Update `downstream_expected` sections in all upstream docs |
| 8 | Downstream documents | Update `upstream` references in all downstream docs |

## Typical Execution Pattern

```
# After generating a full pipeline (BRD→PRD→EARS→BDD→ADR):
# 1. Update each document's downstream_expected
# 2. Batch-patch all 00_index.md files
# 3. Update CHANGELOG, roadmap, and plans/README
# 4. Verify YAML validity of all modified files
```

## Pitfalls

- **Don't assume all 00_index files have the same format.** Each layer may have a different table structure. Read each one before patching.
- **ADR numbering may not align with BRD numbering.** The project may have pre-existing ADRs with different IDs. Always check the directory for collisions.
- **The `downstream_expected` section format varies between layers.** PRD has a flat list, BRD has nested descriptions. Match the existing format.
- **plans/README.md is often stale.** It may still show old statuses. Update all related rows, not just the new document.

## ADR ID Collision Resolution

When `ADR-NN.yaml` already exists in the project with a different topic:
1. Search for next available ADR number: `grep -r "id: ADR-" 05_ADR/*.yaml`
2. Use next available number (e.g., ADR-20 if ADR-19 is last)
3. Rename the file: `ADR-10_broker...yaml` → `ADR-20_broker...yaml`
4. Replace all `ADR.10.xxx` element IDs to `ADR.20.xxx`
5. Update cross-references in ALL upstream/downstream documents
6. Add row to `ADR-00_index.md` with the new ADR number

Proven at TradeGent CC 2026-05-14: ADRs 01-19 pre-existing. Broker ADR assigned ADR-20. All 5 pipeline documents + 4 index files updated.
