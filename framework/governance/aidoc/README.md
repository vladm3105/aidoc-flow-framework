# `.aidoc/` Governance

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-07 |
| Author | Framework Maintainer |
| Framework Version | 0.53.0 |

The `.aidoc/` directory is the project customization layer for every project
that uses the framework. This directory holds the governance documents for
the `.aidoc/` contract: the canonical reference (`AIDOC.md`), the scaffold
template for bootstrapping new projects, and the profile template.

## Documents

| File | Covers |
|------|--------|
| `AIDOC.md` | Canonical reference for the `.aidoc/` project override layer — directory structure, discovery rule, symlink convention. |
| `AIDOC-SCAFFOLD-TEMPLATE.md` | Template for bootstrapping a new project's `.aidoc/` directory. |
| `PROFILE-TEMPLATE.yaml` | The bootstrap template for `.aidoc/profile.yaml` (in `governance/`). |

## How projects consume this

New projects copy the scaffold template to bootstrap their `.aidoc/`:

```bash
cp governance/aidoc/AIDOC-SCAFFOLD-TEMPLATE.md <project>/.aidoc/README.md
```

Existing projects migrate to the new structure via a CHG record
(see `ADAPTATION.md` §10 for the override contract).
