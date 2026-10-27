# Plan: Retirement of Legacy MVP Template Tombstones & Conformance Anti-Resurrection Guard

## Metadata

| Field | Value |
| --- | --- |
| Author | Framework Maintainer |
| Authority | Decision GD-76, User instruction in session (2026-10-11) |
| Framework Version | 0.91.7 |
| Target Version | 0.91.8 |
| Date | 2026-10-11 |
| Status | Proposed |

## Objective

Permanently retire the eight legacy `*-MVP-TEMPLATE.yaml` tombstone pointer files across layers 01 through 08 (`01_BRD` to `08_IPLAN`).

The framework unified around single canonical templates (`*-TEMPLATE.yaml`) in CHG-08 (#666), leaving 11-line pointer tombstones. Now that all 10 SDD layers have canonical templates and canonical YAML indices, these legacy tombstones serve no active runtime or spec function. We remove them and modernize conformance tests from checking tombstone status to asserting an ironclad **Anti-Resurrection Guard** that prevents MVP templates from ever being re-introduced into the layer tree.

## Scope

In scope:

- Remove 8 legacy MVP template tombstones from `framework/layers/`:
  1. `framework/layers/01_BRD/BRD-MVP-TEMPLATE.yaml`
  2. `framework/layers/02_PRD/PRD-MVP-TEMPLATE.yaml`
  3. `framework/layers/03_EARS/EARS-MVP-TEMPLATE.yaml`
  4. `framework/layers/04_BDD/BDD-MVP-TEMPLATE.yaml`
  5. `framework/layers/05_ADR/ADR-MVP-TEMPLATE.yaml`
  6. `framework/layers/06_SPEC/SPEC-MVP-TEMPLATE.yaml`
  7. `framework/layers/07_TDD/TDD-MVP-TEMPLATE.yaml`
  8. `framework/layers/08_IPLAN/IPLAN-MVP-TEMPLATE.yaml`
- Archive historical snapshots in `framework/archive/CHG-89/templates/` for permanent auditability.
- Modernize conformance test suites:
  - `tests/conformance/test_seed_contract.py`: update `test_mvp_skeleton_is_tombstone` to `test_mvp_template_not_resurrected`, asserting `self.assertFalse(BRD_MVP_TEMPLATE.exists())`.
  - `tests/conformance/test_iplan_carrier.py`: update `test_mvp_skeleton_is_tombstone` to `test_mvp_template_not_resurrected`, asserting `self.assertFalse(path.exists())`.
  - `tests/conformance/test_layers.py`: add `test_no_mvp_templates_exist` asserting zero `*-MVP-TEMPLATE.*` files exist across any layer directory.
- Ratify Decision `GD-76` (DEC-CHG-89) in `framework/governance/DECISIONS.md`.
- Author authorizing change request `CHG-89.yaml` and implementation plan `IPLAN-89.yaml` under `framework/archive/CHG-89/`.
- Advance framework spec version to `0.91.8` via `hooks/sync-version-refs.sh`.
- Run full verification battery: `chg_lint.py`, `swf_lint`, conformance suite (536+ tests), acceptance suite.

Out of scope:

- Modifying canonical templates (`*-TEMPLATE.yaml`).
- Modifying canonical index templates (`*-00_index.TEMPLATE.yaml`).

## Anti-Resurrection Guard Architecture

Instead of weakening test coverage by simply deleting assertions, conformance tests are transformed into negative guards that forbid resurrection:

```python
# In tests/conformance/test_seed_contract.py
def test_mvp_template_not_resurrected(self):
    """MVP templates were retired in CHG-08 and tombstoned files removed in CHG-89 (GD-76).

    Asserts that legacy *-MVP-TEMPLATE.yaml files must not be resurrected.
    """
    self.assertFalse(
        BRD_MVP_TEMPLATE.exists(),
        "BRD-MVP-TEMPLATE.yaml resurrected — only canonical BRD-TEMPLATE.yaml is permitted (GD-76)",
    )

# In tests/conformance/test_iplan_carrier.py
def test_mvp_template_not_resurrected(self):
    """MVP templates were retired in CHG-08 and tombstoned files removed in CHG-89 (GD-76)."""
    path = LAYER / "IPLAN-MVP-TEMPLATE.yaml"
    self.assertFalse(
        path.exists(),
        f"{path.name} resurrected — only canonical IPLAN-TEMPLATE.yaml is permitted (GD-76)",
    )

# In tests/conformance/test_layers.py
def test_no_mvp_templates_exist(self):
    """All 8 legacy *-MVP-TEMPLATE.yaml tombstones removed in CHG-89 (GD-76)."""
    mvp_files = list(FRAMEWORK.glob("layers/*/*-MVP-TEMPLATE.*"))
    self.assertEqual(
        [],
        mvp_files,
        f"MVP templates must not exist in framework/layers/ (GD-76): {mvp_files}",
    )
```

## Review log

### Pass 1 (2026-10-11T14:48:00Z)

- **Reviewer**: Lead Architect & Conformance Auditor
- **Findings**:
  1. Identified that `test_seed_contract.py` and `test_iplan_carrier.py` hold explicit positive assertions on `tombstone: status: retired`. Removing files without updating tests would fail CI.
  2. Identified that `test_layers.py` only checked `(folder / layer["template"]).is_file()` and index templates. It did not explicitly guard against rogue MVP templates in other layers (e.g. `03_EARS`, `04_BDD`, `05_ADR`, `06_SPEC`, `07_TDD`).
- **Resolution**:
  1. Convert the two existing positive checks into explicit negative anti-resurrection guards citing Decision GD-76.
  2. Add `test_no_mvp_templates_exist` to `tests/conformance/test_layers.py` to assert that zero `*-MVP-TEMPLATE.*` files exist across all layer folders.
  3. Archive pre-change copies of all 8 files into `framework/archive/CHG-89/templates/` to preserve historical lineage.

### Pass 2 (2026-10-11T14:48:30Z)

- **Reviewer**: Governance & Spec Auditor
- **Findings**:
  1. Checked `hooks/sync-version-refs.sh` `OLD_VERSIONS`: `0.91.7` must be appended so the mechanical version sweep correctly catches any `0.91.7` pins during the `0.91.8` bump.
  2. Verified `IPLAN-89.yaml` and `CHG-89.yaml` requirements per `CHG_REQUEST_FLOWS.md` (DIR2C flow, Level C2 Spec Governance Batch, Decision block DEC-CHG-89 present).
- **Resolution**:
  1. Added `0.91.7` to `OLD_VERSIONS` in `hooks/sync-version-refs.sh`.
  2. Configured `CHG-89.yaml` and `IPLAN-89.yaml` with exhaustive `file_manifest`, complete decision block, and verified clean exit via `chg_lint.py`.
