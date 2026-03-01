---
title: "Pre-commit Hook Library Consumer Guide"
tags:
  - setup-guide
  - pre-commit
  - shared-architecture
custom_fields:
  document_type: setup-guide
  priority: shared
  development_status: active
---

## Pre-commit Hook Library Consumer Guide

This guide provides copy/paste onboarding steps to consume framework pre-commit hooks in any repository.

## Scope

- Installs framework-backed local pre-commit validation.
- Adds optional manual Claude skill audit hook.
- Targets BRD validation with framework naming and section-element rules.

## One-step Setup (Copy/Paste)

Run from target repository root:

```bash
# 1) Link framework scripts into repository root (required by hook entry paths)
ln -sfn /opt/data/docs_flow_framework/ai_dev_ssd_flow ai_dev_ssd_flow

# 2) Copy framework hook template
cp /opt/data/docs_flow_framework/governance/templates/pre-commit-config.framework-library.yaml .pre-commit-config.yaml

# 3) Install hooks
pre-commit install --hook-type pre-commit

# 4) Validate setup
pre-commit run --all-files

# 5) Optional manual skill audit (enabled only when env var is set)
ENABLE_CLAUDE_SKILL_HOOK=1 pre-commit run brd-claude-skill-audit --all-files --hook-stage manual
```

## What Gets Installed

| Hook ID | Stage | Behavior |
| ------- | ----- | -------- |
| `brd-core-wrapper` | `pre-commit` | Blocking BRD core validation via unified wrapper (`--skip-advisory`) |
| `brd-standardized-element-codes` | `manual` | Deprecated compatibility alias for `brd-core-wrapper` |
| `brd-claude-skill-audit` | `manual` | Optional `/doc-brd-audit` run with report output |

## Inputs and Outputs

| Item | Value |
| ---- | ----- |
| Required dependency | `pre-commit` executable |
| Framework script path | `ai_dev_ssd_flow/01_BRD/scripts/` |
| Manual skill reports | `tmp/skill_hook_reports/*.doc-brd-audit.txt` |

## Failure Modes

| Failure | Cause | Resolution |
| ------- | ----- | ---------- |
| Hook command not found | `pre-commit` missing | Install `pre-commit` and rerun install |
| Script path not found | Missing `ai_dev_ssd_flow` link | Recreate symlink to framework path |
| Skill audit skipped | `ENABLE_CLAUDE_SKILL_HOOK` unset | Set `ENABLE_CLAUDE_SKILL_HOOK=1` for manual run |
| Skill audit failed | `claude` CLI unavailable or timeout | Install/authenticate `claude`, rerun manual hook |

## Verification Commands

```bash
pre-commit run brd-core-wrapper --all-files
pre-commit run brd-claude-skill-audit --all-files --hook-stage manual

# Legacy alias (deprecated, still supported)
pre-commit run brd-standardized-element-codes --all-files --hook-stage manual
```
