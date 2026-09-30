# `.aidoc/` Governance

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-09-29 |
| Author | Framework Maintainer |
| Framework Version | 0.68.1 |

The `.aidoc/` directory is the project customization layer for every project
that uses the framework. This directory holds the governance documents for
the `.aidoc/` contract: the canonical reference (`AIDOC.md`), the scaffold
template for bootstrapping new projects, the profile template, and the
bootstrap (`BOOTSTRAP.md`) and upgrade (`UPGRADE-RUNBOOK.md`) runbooks.

## Documents

| File | Covers |
|------|--------|
| `AIDOC.md` | Canonical reference for the `.aidoc/` project override layer — directory structure, discovery rule, symlink convention. |
| `AIDOC-SCAFFOLD-TEMPLATE.md` | Template for bootstrapping a new project's `.aidoc/` directory. |
| `PROFILE-TEMPLATE.yaml` | The bootstrap template for `.aidoc/profile.yaml` (in `governance/`). |
| `BOOTSTRAP.md` | Step-by-step bootstrap procedure + shape validation for a new project's `.aidoc/`. |
| `UPGRADE-RUNBOOK.md` | Consumer upgrade runbook: re-adopting a new `framework/VERSION`. |

## How projects consume this

New projects bootstrap their `.aidoc/` by following `BOOTSTRAP.md`. The first
step copies the scaffold template — run from the repository root:

```bash
cp framework/governance/aidoc/AIDOC-SCAFFOLD-TEMPLATE.md <project>/.aidoc/README.md
```

Existing projects migrate to the new structure via a CHG record
(see `ADAPTATION.md` §10 for the override contract). Consumers on an older
canon re-adopt via `UPGRADE-RUNBOOK.md`.
