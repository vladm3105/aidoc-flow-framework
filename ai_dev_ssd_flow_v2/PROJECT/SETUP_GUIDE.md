---
title: "SDD Project Model v2.2 - Setup Guide"
tags:
  - framework-guide
  - shared-architecture
  - project-management
  - sdd-workflow
  - setup-guide
custom_fields:
  document_type: guide
  artifact_type: REF
  layer: 0
  priority: shared
  development_status: active
  location: ucx_flow_v3/PROJECT/SETUP_GUIDE.md
  created: 2026-02-16
  updated: 2026-02-16
---

# SDD Project Model v2.2 - Setup Guide

**Version**: 1.0
**Location**: `ucx_flow_v3/PROJECT/SETUP_GUIDE.md`

---

## 1. Prerequisites

### 1.1 Python Environment

```bash
# Python 3.11+ required
python3 --version

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

### 1.2 Install Dependencies

```bash
pip install -r ucx_flow_v3/scripts/requirements-project.txt
```

### 1.3 GitHub Token

Set up a GitHub Personal Access Token with these scopes:
- `repo` (full repository access)
- `project` (for Project V2 boards)

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

---

## 2. Configuration

### 2.1 Project Configuration

Edit `ucx_flow_v3/PROJECT/config/project_model.yaml`:

```yaml
project:
  name: "Your Project Name"
  repo: "owner/repo-name"
  board_number: 31  # GitHub Project V2 number
```

### 2.2 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Yes | GitHub Personal Access Token |
| `SDD_CONFIG` | No | Path to project_model.yaml (default: auto-detect) |

---

## 3. Quick Start

### 3.1 Sprint 0 Setup

```bash
# Generate Sprint 0 checklist
python ucx_flow_v3/scripts/sprint0_setup.py \
  --check-readiness \
  --docs-root docs/

# Create Sprint 0 GitHub issues
python ucx_flow_v3/scripts/sprint0_setup.py \
  --repo owner/repo-name \
  --create-issues
```

### 3.2 Generate Artifacts (Tier 1)

Use Claude Code skills for artifact generation:

```bash
/doc-brd-autopilot           # Generate BRD from reference docs
/doc-prd-autopilot BRD-01    # Generate PRD from BRD
/doc-ears-autopilot PRD-01   # Generate EARS from PRD
/doc-bdd-autopilot EARS-01   # Generate BDD from EARS
```

### 3.3 Sync TASKS to GitHub

```bash
python ucx_flow_v3/scripts/tasks_to_github.py \
  --tasks-file docs/11_TASKS/TASKS-01.yaml \
  --repo owner/repo-name \
  --project-number 31 \
  --dry-run  # Remove to create actual issues
```

---

## 4. Script Reference

### 4.1 tasks_to_github.py

Converts TASKS YAML to GitHub Issues with Project V2 integration.

```bash
python scripts/tasks_to_github.py \
  --tasks-file docs/11_TASKS/TASKS-01.yaml \
  --repo owner/repo-name \
  --sprint "Sprint 2.1" \
  --project-number 31 \
  --dry-run
```

**Options**:
| Option | Description |
|--------|-------------|
| `--tasks-file` | Path to TASKS YAML file |
| `--repo` | GitHub repository (owner/repo) |
| `--sprint` | Sprint name override |
| `--project-number` | Project V2 board number |
| `--dry-run` | Preview without creating issues |

### 4.2 drift_check.py

Detects documentation drift by comparing artifact dates with issue closes.

```bash
python scripts/drift_check.py \
  --sdd-root docs/ \
  --repo owner/repo-name \
  --max-age-days 14 \
  --report tmp/drift_report.md
```

**Options**:
| Option | Description |
|--------|-------------|
| `--sdd-root` | Root documentation directory |
| `--repo` | GitHub repository |
| `--max-age-days` | Stale threshold (default: 14) |
| `--report` | Output markdown report path |

### 4.3 validate_artifact.py

Unified artifact validation with 4-Gate system.

```bash
# Validate single artifact
python scripts/validate_artifact.py \
  --path docs/BRD/BRD-01.md \
  --strict

# Validate with gate check
python scripts/validate_artifact.py \
  --path docs/BRD/BRD-01.md \
  --gate GATE-01

# Detect affected gates
python scripts/validate_artifact.py \
  --path docs/ \
  --detect-gates \
  --output tmp/gate_analysis.json
```

### 4.4 chg_generator.py

Generate CHG documents with 4-Gate integration.

```bash
python scripts/chg_generator.py \
  --description "Add email localization support" \
  --affected-layers 2,9,11 \
  --output docs/CHG/
```

### 4.5 sprint0_setup.py

Sprint 0 checklist generation and readiness validation.

```bash
# Check readiness
python scripts/sprint0_setup.py \
  --docs-root docs/ \
  --check-readiness

# Create issues
python scripts/sprint0_setup.py \
  --repo owner/repo-name \
  --create-issues
```

### 4.6 raci_generator.py

Generate RACI matrix from configuration.

```bash
python scripts/raci_generator.py \
  --output docs/RACI_MATRIX.md \
  --format markdown \
  --validate
```

### 4.7 layer_selector.py

Decision framework for layer selection.

```bash
# Interactive mode
python scripts/layer_selector.py --interactive

# Automated classification
python scripts/layer_selector.py \
  --work-type "bug fix" \
  --description "Fix null pointer in auth"

# Show decision matrix
python scripts/layer_selector.py --show-matrix
```

---

## 5. CI/CD Integration

### 5.1 GitHub Actions Workflow

Copy the workflow template to your repository:

```bash
mkdir -p .github/workflows
cp ucx_flow_v3/PROJECT/.github/workflows/sdd-validation.yml \
   .github/workflows/
```

### 5.2 Issue Template

Copy the issue template:

```bash
mkdir -p .github/ISSUE_TEMPLATE
cp ucx_flow_v3/PROJECT/.github/ISSUE_TEMPLATE/sdd-task.yml \
   .github/ISSUE_TEMPLATE/
```

---

## 6. 4-Gate System

### 6.1 Gate Overview

| Gate | Layers | Purpose |
|------|--------|---------|
| GATE-01 | L1-L4 | Business Requirements |
| GATE-05 | L5-L8 | Architecture |
| GATE-09 | L9-L11 | Implementation Specification |
| GATE-12 | L12-L14 | Code Implementation |

### 6.2 Gate Validation

```bash
# Validate artifact against specific gate
python scripts/validate_artifact.py \
  --path docs/BRD/BRD-01.md \
  --gate GATE-01

# Detect gates affected by changes
python scripts/validate_artifact.py \
  --path docs/ \
  --detect-gates
```

---

## 7. Troubleshooting

### Common Issues

**Issue**: "GITHUB_TOKEN environment variable required"
**Solution**: Export your GitHub token: `export GITHUB_TOKEN="ghp_..."`

**Issue**: "Cannot find project_model.yaml"
**Solution**: Ensure config file exists at `ucx_flow_v3/PROJECT/config/project_model.yaml`

**Issue**: "Validator script not found"
**Solution**: Verify scripts are in `ucx_flow_v3/scripts/`

### Getting Help

- Review `PROJECT_MODEL.md` for methodology details
- Check `IMPLEMENTATION_PLAN.md` for specifications
- Run scripts with `--verbose` for debug output

---

## 8. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-16 | Initial setup guide |
