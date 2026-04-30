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

This guide provides onboarding steps to consume framework pre-commit hooks.

## One-step Setup

Run from target repository root:

```bash
ln -sfn /opt/data/docs_flow_framework/ai_dev_flow_v3 ai_dev_flow_v3
cp /opt/data/docs_flow_framework/governance/templates/pre-commit-config.framework-library.yaml .pre-commit-config.yaml
pre-commit install --hook-type pre-commit
pre-commit run --all-files
```

## Inputs and Outputs

| Item | Value |
| --- | --- |
| Required dependency | `pre-commit` executable |
| Framework script path | `ai_dev_flow_v3/01_BRD/scripts/` |

## Failure Modes

| Failure | Cause | Resolution |
| --- | --- | --- |
| Script path not found | Missing `ai_dev_flow_v3` link | Recreate symlink |
