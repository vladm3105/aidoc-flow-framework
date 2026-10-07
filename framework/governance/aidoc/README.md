# `.aidoc/` Governance

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.3 |
| Status | Approved |
| Last Updated | 2026-10-06 |
| Author | Framework Maintainer |
| Framework Version | 0.88.4 |

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
| `AIDOC-CHG-EXECUTION-FLOW-TEMPLATE.md` | Operational execution handbook template for autonomous change processing (`.aidoc/project/governance/CHG_EXECUTION_FLOW.md`). |
| `AIDOC-CI-SMART-ROUTING-TEMPLATE.md` | Operational template for CI smart change detection and anti-deadlock status check orchestration. |
| `AIDOC-CONFLICT-RESOLUTION-TEMPLATE.md` | Operational standard and runbook for autonomous forward merge PR conflict resolution. |
| `AIDOC-SELF-REVIEW-LOOP-TEMPLATE.md` | Multi-agent dual self-review protocol, four-lens rubric, and commit audit phrases. |
| `AIDOC-QA-PROTOCOL-TEMPLATE.md` | Tripartite QA protocol, strict non-code-modifying hard block, and post-merge issue closure report contract. |
| `AIDOC-BROWSER-TESTING-TEMPLATE.md` | Headless browser testing architecture, port/container sandboxing, and artifact collection. |
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
