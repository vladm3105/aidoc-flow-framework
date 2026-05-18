# IPLAN-001: Fix ai_dev_ssd_flow and governance Integration Gaps

**Status**: Complete
**Created**: 2026-02-18
**Updated**: 2026-02-18
**Implemented**: 2026-02-18
**Phase**: Cross-phase
**Priority**: High

---

## Summary

Fix 10 integration gaps between `ai_dev_ssd_flow` (15-layer SDD framework) and `governance` (GitHub project governance). The systems are conceptually aligned but have broken references, duplicated functionality, and missing bridges.

---

## Gap Analysis Summary

| Gap | Description | Priority |
|-----|-------------|----------|
| 1 | Broken cross-references (`governance/sdd/governance/` path) | Critical |
| 2 | TASKS vs IPLAN disconnect | High |
| 3 | Dual workflow systems | High |
| 4 | CHG-to-governance mismatch | Medium |
| 5 | Validation script fragmentation | Medium |
| 6 | TASKS→Issue not in governance docs | High |
| 7 | Label system overlap (incomplete registry) | Medium |
| 8 | Traceability ends at issue creation | Medium |
| 9 | TSPEC/BDD not connected to QA | Medium |
| 10 | SDD depth not enforced | Low |
| 11 | Duplicate IPLAN templates | Medium |
| 12 | Missing README updates | Low |
| 13 | Testing model undocumented in SDD/governance | High |

---

## Testing Model: TSPEC vs BDD Execution

### Test Pyramid Mapping

```
           /\
          /  \  BDD Acceptance Tests (Staging)
         /    \
        /------\
       / FTEST  \ Functional Tests (Staging)
      /----------\
     /   STEST    \ System Tests (Staging)
    /--------------\
   /     ITEST      \ Integration Tests (CI)
  /------------------\
 /       UTEST        \ Unit Tests (CI)
/______________________\
```

### Execution Timeline

| Test Type | Source | Execution Point | Environment | Coverage Target |
|-----------|--------|-----------------|-------------|-----------------|
| **TSPEC-UTEST** | Layer 10 | After code generation | CI Pipeline | ≥80% |
| **TSPEC-ITEST** | Layer 10 | After component integration | CI Pipeline | ≥60% |
| **TSPEC-STEST** | Layer 10 | After staging deploy | QA Staging | Critical paths |
| **TSPEC-FTEST** | Layer 10 | After staging deploy | QA Staging | Feature coverage |
| **BDD** | Layer 4 | After staging deploy | QA Staging | User acceptance |

### Workflow Integration

```
Code Generation (Layer 12)
    ↓
UTEST + ITEST run in CI (pr-check)
    ↓
PR Merge → Deploy to Dev
    ↓
Phase Complete → Deploy to Staging
    ↓
QA Testing Issue Created (ai:qa-testing)
    ↓
STEST + FTEST + BDD run on Staging
    ↓
Pass → Production Ready
Fail → Bug Issue Created (iteration:N)
```

---

## Phase 1: Fix Broken Cross-References (Critical)

**Problem**: 57 occurrences of non-existent `governance/sdd/governance/` path across 4 files.

**Files to Update**:

| File | Occurrences | Changes |
|------|-------------|---------|
| `ai_dev_ssd_flow/PROJECT/PROJECT_MODEL.md` | 20 | Replace `governance/sdd/governance/` → `governance/` |
| `README.md` | 10 | Replace `governance/sdd/` → `governance/` |
| `MULTI_PROJECT_SETUP_GUIDE.md` | 19 | Replace paths |
| `MULTI_PROJECT_QUICK_REFERENCE.md` | 8 | Replace paths |

**Execution Commands**:
```bash
cd /opt/data/ucx_framework

# Verify current state
grep -rn "governance/sdd" *.md ai_dev_ssd_flow/PROJECT/*.md | wc -l
# Expected: 57

# Fix governance/sdd/governance/ first (more specific)
sed -i 's|governance/sdd/governance/|governance/|g' \
  README.md \
  MULTI_PROJECT_SETUP_GUIDE.md \
  MULTI_PROJECT_QUICK_REFERENCE.md \
  ai_dev_ssd_flow/PROJECT/PROJECT_MODEL.md

# Fix remaining governance/sdd/
sed -i 's|governance/sdd/|governance/|g' \
  README.md \
  MULTI_PROJECT_SETUP_GUIDE.md \
  MULTI_PROJECT_QUICK_REFERENCE.md \
  ai_dev_ssd_flow/PROJECT/PROJECT_MODEL.md

# Verify fix
grep -rn "governance/sdd" *.md ai_dev_ssd_flow/PROJECT/*.md | wc -l
# Expected: 0
```

**Verification**:
```bash
grep -r "governance/ssd" /opt/data/ucx_framework/*.md && echo "FAIL" || echo "PASS"
```

---

## Phase 2: Consolidate IPLAN Templates + Create TASKS-IPLAN Bridge

**Problem 1**: Duplicate IPLAN templates exist:
- `governance/templates/IPLAN-TEMPLATE.md`
- `governance/plans/IPLAN-TEMPLATE.md`

**Problem 2**: SDD generates TASKS (Layer 11), governance requires IPLAN per-issue. No documented bridge.

### Step 2.1: Consolidate IPLAN Templates

**Action**: Keep `governance/plans/IPLAN-TEMPLATE.md` as canonical, symlink from templates.

```bash
cd /opt/data/ucx_framework/governance

# Remove duplicate, create symlink
rm templates/IPLAN-TEMPLATE.md
ln -s ../plans/IPLAN-TEMPLATE.md templates/IPLAN-TEMPLATE.md

# Verify
ls -la templates/IPLAN-TEMPLATE.md
```

### Step 2.2: Update IPLAN-TEMPLATE.md with SDD Traceability

**File**: `governance/plans/IPLAN-TEMPLATE.md`

Add after frontmatter:
```markdown
## SDD Traceability (if source:sdd)

<!-- Complete if issue has source:sdd label -->
| Tag | Reference | Description |
|-----|-----------|-------------|
| @tasks | TASKS-NN.MM.PP | Source task element |
| @spec | SPEC-NN | Technical specification |
| @req | REQ-NN:REQ.NN.MM | Atomic requirement |
| @sys | SYS-NN:SYS.NN.MM | System requirement |
| @adr | ADR-NN | Architecture decision |
| @ears | EARS-NN:EARS.NN.MM | Formal requirement |
| @brd | BRD-NN:BRD.NN.MM | Business requirement |

**TASKS Source File**: `docs/11_TASKS/TASKS-NN_{slug}.yaml`
```

### Step 2.3: Create TASKS-IPLAN Bridge Document

**New File**: `governance/TASKS_IPLAN_BRIDGE.md`

```markdown
# TASKS to IPLAN Bridge

## Overview

This document bridges SDD Layer 11 (TASKS) artifacts with governance IPLAN documents, clarifying when and how each is used.

---

## Artifact Comparison

| Aspect | TASKS (SDD Layer 11) | IPLAN (Governance) |
|--------|---------------------|-------------------|
| **Created** | During SDD specification | Before implementing each issue |
| **Format** | YAML with traceability | Markdown with checklist |
| **Scope** | Full feature breakdown | Single issue execution |
| **Purpose** | Work decomposition from SPEC | Execution plan with corrections |
| **Contains** | Tasks, dependencies, acceptance criteria | Steps, risks, findings |

---

## Workflow Integration

### When Using SDD + Governance

```
SPEC-NN (Layer 9)
    ↓
TASKS-NN generated (Layer 11)
    ↓
tasks_to_github.py creates issues
    ↓
Issue #X created with source:sdd label
    ↓
AI agent picks up issue (ai:ready)
    ↓
Agent creates IPLAN-X_{slug}.md BEFORE coding
    ↓
Implementation proceeds per IPLAN
    ↓
PR created, IPLAN marked complete
```

### Traceability Chain

```
BRD → PRD → EARS → ADR → SYS → REQ → SPEC → TASKS → Issue → IPLAN → Code
```

Each IPLAN includes:
- `@tasks: TASKS-NN.MM.PP` reference (links to source task)
- Full upstream traceability (inherited from TASKS)
- Issue-specific execution details

---

## When to Use Which

| Scenario | Use TASKS | Use IPLAN |
|----------|-----------|-----------|
| SDD-generated feature | ✓ Generated from SPEC | ✓ Created per issue |
| Manual issue (no SDD) | ✗ Not applicable | ✓ Required before coding |
| Bug fix | ✗ Not applicable | ✓ Required (simplified) |
| Hotfix | ✗ Not applicable | ✗ Code-only, 72h retroactive docs |

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `ai_dev_ssd_flow/11_TASKS/TASKS-TEMPLATE.md` | TASKS format specification |
| `ai_dev_ssd_flow/11_TASKS/IMPLEMENTATION_PLAN_TEMPLATE.md` | SDD implementation tracking |
| `governance/plans/IPLAN-TEMPLATE.md` | Governance IPLAN format |
| `governance/GOVERNANCE_RULES.md` Section 3 | Issue processing workflow |

---

## Implementation Plan Templates Clarification

Multiple implementation plan templates exist for different purposes:

| Template | Location | Purpose |
|----------|----------|---------|
| **IPLAN-TEMPLATE.md** | `governance/plans/` | Per-issue execution plan (governance) |
| **IMPLEMENTATION_PLAN_TEMPLATE.md** | `ai_dev_ssd_flow/11_TASKS/` | TASKS execution tracking (SDD) |
| **IMPLEMENTATION_PLAN_TEMPLATE.yaml** | `ai_dev_ssd_flow/11_TASKS/` | Machine-readable version |

**Key Difference**:
- **IPLAN**: Governance artifact, created per GitHub issue, focuses on execution steps and corrections
- **IMPLEMENTATION_PLAN**: SDD artifact, tracks overall TASKS completion across multiple issues
```

### Step 2.4: Update governance/README.md

**File**: `governance/README.md`

Add after "Core Documentation" section:
```markdown
---

## SDD Integration

| Document | Description |
|:---------|:------------|
| [TASKS_IPLAN_BRIDGE.md](./TASKS_IPLAN_BRIDGE.md) | How TASKS (Layer 11) connects to IPLAN |
| [CHG_GOVERNANCE_BRIDGE.md](./CHG_GOVERNANCE_BRIDGE.md) | 4-Gate CHG to governance phases |
| [TSPEC_BDD_QA_BRIDGE.md](./TSPEC_BDD_QA_BRIDGE.md) | Test execution (TSPEC/BDD) to QA workflow |

> **Full SDD Documentation**: See [`../ai_dev_ssd_flow/`](../ai_dev_ssd_flow/) for layer templates and specifications.
```

### Step 2.5: Update AI_ISSUE_LIFECYCLE.md

**File**: `governance/AI_ISSUE_LIFECYCLE.md`

Add new section after overview:
```markdown
---

## Issue Sources

Issues can be created through three channels:

### 1. TASKS-Generated (SDD Workflow)

**Script**: `ai_dev_ssd_flow/scripts/tasks_to_github.py`
**Source**: TASKS YAML files from SDD Layer 11
**Labels**: `source:sdd`, `ai:ready`, `phase:N`
**Includes**: Full traceability tags (@brd, @prd, @spec, @tasks)

```bash
python ai_dev_ssd_flow/scripts/tasks_to_github.py \
  --tasks-file docs/11_TASKS/TASKS-01.yaml \
  --repo owner/repo
```

### 2. Human-Created (Manual)

**Method**: Direct issue creation in GitHub
**Labels**: `ai:development`, `phase:N`
**Template**: `.github/ISSUE_TEMPLATE/development-task.yml`

### 3. Automation-Generated

| Workflow | Creates | Trigger |
|----------|---------|---------|
| `create-bug-issue.yml` | Bug issues from QA failures | Test failure |
| `create-deployment-issue.yml` | Deployment issues | PR merge |
| `create-qa-testing-issue.yml` | QA testing issues | Deploy complete |
```

### Step 2.6: Update GOVERNANCE_RULES.md

**File**: `governance/GOVERNANCE_RULES.md`

Add to Section 3 (AI Workflow), after "Label Lifecycle":
```markdown
### Issue Sources and TASKS Integration

Issues may originate from SDD TASKS artifacts. When an issue has the `source:sdd` label:

1. **Traceability tags** are present in the issue body (@brd, @prd, @spec, @tasks)
2. **TASKS element ID** links to the source specification
3. **IPLAN** must reference the TASKS element ID for traceability

**TASKS to Issue Script**:
```bash
python ai_dev_ssd_flow/scripts/tasks_to_github.py --tasks-file <path> --repo <owner/repo>
```

See: [TASKS_IPLAN_BRIDGE.md](./TASKS_IPLAN_BRIDGE.md) for full workflow.
```

---

## Phase 3: Integrate SDD Validation Workflow

**Problem**: Dual workflow systems - SDD has `sdd-validation.yml`, governance has 22 separate workflows.

### Step 3.1: Copy and Update Workflow

**Source**: `ai_dev_ssd_flow/PROJECT/.github/workflows/sdd-validation.yml`
**Target**: `.github/workflows/sdd-artifact-validation.yml`

```bash
cp ai_dev_ssd_flow/PROJECT/.github/workflows/sdd-validation.yml \
   .github/workflows/sdd-artifact-validation.yml
```

### Step 3.2: Remove Marketplace Actions

Update `.github/workflows/sdd-artifact-validation.yml` per `GOVERNANCE_RULES.md` Section 2a:

| Replace | With |
|---------|------|
| `actions/checkout@v4` | Inline git clone pattern |
| `actions/setup-python@v5` | System Python (`python3`) |
| `tj-actions/changed-files@v42` | `git diff --name-only` |
| `stefanzweifel/git-auto-commit-action@v5` | `git add && git commit && git push` |

**Checkout replacement**:
```yaml
- name: Checkout
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    rm -rf "${GITHUB_WORKSPACE}"/* "${GITHUB_WORKSPACE}"/.[!.]* 2>/dev/null || true
    CLONE_BRANCH="${GITHUB_HEAD_REF:-$GITHUB_REF_NAME}"
    git clone "https://x-access-token:${GH_TOKEN}@${GITHUB_SERVER_URL#https://}/${GITHUB_REPOSITORY}.git" \
      "${GITHUB_WORKSPACE}" --depth 1 --branch "${CLONE_BRANCH}"
```

**Changed files replacement**:
```yaml
- name: Get changed files
  id: changed
  run: |
    if [ "${{ github.event_name }}" = "pull_request" ]; then
      FILES=$(git diff --name-only origin/${{ github.base_ref }}...HEAD | grep -E '^docs/.*\.(md|yaml|feature)$' | tr '\n' ' ')
    else
      FILES=$(git diff --name-only HEAD~1 | grep -E '^docs/.*\.(md|yaml|feature)$' | tr '\n' ' ')
    fi
    echo "files=$FILES" >> $GITHUB_OUTPUT
```

### Step 3.3: Create Workflow Integration Document

**New File**: `governance/github/WORKFLOW_INTEGRATION.md`

```markdown
# Workflow Integration Guide

## Overview

This document maps workflows between SDD artifact validation and governance issue/deployment lifecycle.

---

## Workflow Categories

| Category | Workflows | Trigger | Purpose |
|----------|-----------|---------|---------|
| **SDD Validation** | `sdd-artifact-validation.yml` | `docs/**` changes | Validate artifacts, update matrix |
| **CI/CD** | `ci.yml`, `test-pipeline.yml` | PR, push | Lint, test, security scan |
| **Deployment** | `deploy-dev.yml`, `deploy-staging.yml`, `deploy-prod.yml` | Phase completion, manual | Environment deployment |
| **Issue Lifecycle** | `agent-dispatch.yml`, `issue-label-sync.yml` | Issue events | AI agent coordination |
| **QA** | `execute-qa-testing.yml`, `create-qa-testing-issue.yml` | Deploy completion | Test execution |
| **Bug Management** | `create-bug-issue.yml` | Test failure | Bug issue creation |

---

## SDD Layer to Governance Phase Mapping

| SDD Layers | Governance Activity | Workflows Involved |
|------------|--------------------|--------------------|
| L1-L4 (BRD→BDD) | Requirement definition | `sdd-artifact-validation.yml` |
| L5-L8 (ADR→CTR) | Architecture & design | `sdd-artifact-validation.yml` |
| L9-L11 (SPEC→TASKS) | Sprint planning | `sdd-artifact-validation.yml`, `mvp-docs-generation.yml` |
| L12-L14 (IMPL) | Development & QA | `ci.yml`, `deploy-*.yml`, `execute-qa-testing.yml` |

---

## Test Execution Workflow

### CI Pipeline (Development)

```
PR Created
    ↓
ci.yml triggers
    ↓
├── Lint (ruff, mypy)
├── UTEST (pytest, ≥80% coverage)
├── ITEST (integration tests, ≥60% coverage)
├── Security scan (bandit, pip-audit)
└── Build validation
    ↓
PR Ready for Review
```

### QA Pipeline (Staging)

```
All Phase Issues Closed
    ↓
deploy-staging.yml triggers
    ↓
Staging deployment complete
    ↓
create-qa-testing-issue.yml creates ai:qa-testing issue
    ↓
execute-qa-testing.yml triggers (daily 06:00-08:00 EST)
    ↓
├── Smoke tests (health endpoints)
├── STEST (system tests)
├── FTEST (functional tests)
└── BDD (acceptance tests via pytest-bdd)
    ↓
Pass: ai:qa-passed → Production Ready
Fail: create-bug-issue.yml → Bug fix iteration
```

---

## Validation Triggers

| Event | SDD Validation | CI Pipeline | QA Pipeline |
|-------|----------------|-------------|-------------|
| PR to `main` | ✓ (docs changes) | ✓ (code changes) | - |
| Push to `main` | ✓ (matrix update) | - | - |
| Phase complete | - | - | ✓ |
| Schedule (weekly) | ✓ (drift check) | - | ✓ (daily) |
```

---

## Phase 4: Bridge CHG to Governance

**Problem**: SDD uses 4-Gate CHG system, governance uses phase-gated deployment. No connection.

### New File: `governance/CHG_GOVERNANCE_BRIDGE.md`

```markdown
# CHG to Governance Phase Bridge

## Overview

This document bridges SDD's 4-Gate Change Management (CHG) system with governance phase-gated deployment.

---

## When to Use CHG

| SDD Depth | Change Management Method |
|-----------|-------------------------|
| **SDD-Lite** | PR-based only |
| **SDD-Standard** | PR-based + review gates |
| **SDD-Full** | 4-Gate CHG system (formal) |

CHG documents are **required** for SDD-Full projects and **optional** for others.

---

## Gate-to-Phase Mapping

| SDD Gate | Layers Affected | Governance Equivalent | Approval Required |
|----------|-----------------|----------------------|-------------------|
| GATE-01 | L1-L4 (BRD→BDD) | Phase requirement review | Business Owner |
| GATE-05 | L5-L8 (ADR→CTR) | Architecture review | Architect |
| GATE-09 | L9-L11 (SPEC→TASKS) | Sprint planning approval | Tech Lead |
| GATE-12 | L12-L14 (IMPL→Validation) | PR merge + phase deployment | Reviewer |

---

## Integration Points

### CHG Document Triggers Governance Actions

| CHG Status | Governance Action |
|------------|-------------------|
| CHG created | Issue labeled `chg:pending` |
| CHG approved | Label changed to `chg:approved`, proceed with implementation |
| CHG rejected | Label changed to `chg:rejected`, rework required |
| GATE-12 passed | `deploy-dev.yml` triggered on phase completion |

### Governance Events Trigger CHG Updates

| Governance Event | CHG Impact |
|------------------|------------|
| Sprint retrospective | Review open CHGs, close completed |
| Phase deployment | Update CHG status to reflect deployment |
| Production incident | May trigger emergency CHG bypass |

---

## Emergency Bypass Conditions

CHG gates can be bypassed for:
- P1 production incidents
- Critical security vulnerabilities (CVSS ≥9.0)
- Regulatory compliance deadlines

Document bypass in CHG with:
- `bypass_reason: <description>`
- `bypass_approver: <name>`
- `bypass_date: <YYYY-MM-DD>`

---

## CHG Labels

| Label | Color | Description |
|-------|-------|-------------|
| `chg:pending` | Yellow (#F9A825) | CHG document awaiting approval |
| `chg:approved` | Green (#43A047) | CHG document approved |
| `chg:rejected` | Red (#D32F2F) | CHG document rejected |

---

## Reference Documents

| Document | Location |
|----------|----------|
| CHG Template | `ai_dev_ssd_flow/CHG/CHG-TEMPLATE.md` |
| Change Management Guide | `ai_dev_ssd_flow/CHG/CHANGE_MANAGEMENT_GUIDE.md` |
| 4-Gate Definitions | `ai_dev_ssd_flow/CHG/gates/` |
```

### Update: `governance/scripts/setup-ai-pr-review-labels.sh`

Add CHG labels:
```bash
# CHG labels (SDD-Full only)
gh label create "chg:pending" --color "F9A825" --description "CHG document awaiting approval" --force
gh label create "chg:approved" --color "43A047" --description "CHG document approved" --force
gh label create "chg:rejected" --color "D32F2F" --description "CHG document rejected" --force
```

---

## Phase 5: Create Complete Label Registry

**Problem**: Labels scattered across multiple files. Missing categories.

### New File: `governance/github/LABEL_REGISTRY.yaml`

```yaml
# Label Registry - Single Source of Truth
# Used by: setup-all-labels.sh, tasks_to_github.py, workflows
#
# Update this file when adding/modifying labels.
# Run setup-all-labels.sh to apply changes.

version: "2.0"
last_updated: "2026-02-18"

categories:
  # === WORKFLOW LABELS (Issue State) ===
  workflow:
    - name: "ai:ready"
      color: "0052CC"
      description: "Ready for AI agent to work on"
    - name: "ai:in-progress"
      color: "FBCA04"
      description: "AI agent actively working"
    - name: "ai:review-requested"
      color: "1D76DB"
      description: "AI work complete, human review needed"

  # === ISSUE TYPE LABELS ===
  issue_type:
    - name: "ai:development"
      color: "5319E7"
      description: "Development issue (code changes)"
    - name: "ai:deployment"
      color: "006B75"
      description: "Deployment issue"
    - name: "ai:qa-testing"
      color: "7B68EE"
      description: "QA testing issue"
    - name: "bug"
      color: "D73A4A"
      description: "Bug fix"
    - name: "enhancement"
      color: "A2EEEF"
      description: "New feature or enhancement"
    - name: "documentation"
      color: "0075CA"
      description: "Documentation only"

  # === SOURCE LABELS ===
  source:
    - name: "source:sdd"
      color: "7057FF"
      description: "Issue generated from SDD TASKS"
    - name: "source:manual"
      color: "BFD4F2"
      description: "Manually created issue"
    - name: "source:automation"
      color: "D4C5F9"
      description: "Auto-generated (QA, deployment)"

  # === PHASE LABELS ===
  phase:
    - name: "phase:0"
      color: "EEEEEE"
      description: "Phase 0 (Sprint 0 / Setup)"
    - name: "phase:1"
      color: "D93F0B"
      description: "Phase 1 work item"
    - name: "phase:2"
      color: "E99695"
      description: "Phase 2 work item"
    - name: "phase:3"
      color: "FEF2C0"
      description: "Phase 3 work item"
    - name: "phase:4"
      color: "C2E0C6"
      description: "Phase 4 work item"
    - name: "phase:5"
      color: "BFDADC"
      description: "Phase 5 work item"
    - name: "phase:6"
      color: "C5DEF5"
      description: "Phase 6 work item"
    - name: "phase:7"
      color: "BFD4F2"
      description: "Phase 7 work item"
    - name: "phase:8"
      color: "D4C5F9"
      description: "Phase 8 work item"

  # === SIZE LABELS ===
  size:
    - name: "size:XS"
      color: "C2E0C6"
      description: "Extra small (< 1 hour)"
    - name: "size:S"
      color: "C2E0C6"
      description: "Small (1-4 hours)"
    - name: "size:M"
      color: "FEF2C0"
      description: "Medium (4-8 hours)"
    - name: "size:L"
      color: "F9D0C4"
      description: "Large (1-2 days)"
    - name: "size:XL"
      color: "E99695"
      description: "Extra large (3+ days)"

  # === PRIORITY LABELS ===
  priority:
    - name: "priority:P0"
      color: "B60205"
      description: "Critical - drop everything"
    - name: "priority:P1"
      color: "D93F0B"
      description: "High - current sprint"
    - name: "priority:P2"
      color: "FBCA04"
      description: "Medium - next sprint"
    - name: "priority:P3"
      color: "0E8A16"
      description: "Low - backlog"

  # === QA STATUS LABELS ===
  qa:
    - name: "ai:qa-passed"
      color: "28A745"
      description: "QA tests passed"
    - name: "ai:qa-failed"
      color: "DC3545"
      description: "QA tests failed"
    - name: "iteration:1"
      color: "6C757D"
      description: "First bug fix attempt"
    - name: "iteration:2"
      color: "6C757D"
      description: "Second bug fix attempt"
    - name: "iteration:3"
      color: "6C757D"
      description: "Third (final) bug fix attempt"
    - name: "needs-human"
      color: "FF0000"
      description: "Max iterations exceeded, needs human"

  # === PR REVIEW LABELS ===
  review:
    - name: "ai:review-passed"
      color: "0E8A16"
      description: "AI review approved"
    - name: "ai:review-failed"
      color: "B60205"
      description: "AI review requested changes"
    - name: "skip-ai-review"
      color: "EEEEEE"
      description: "Skip AI code review for this PR"

  # === CHG LABELS (SDD-Full) ===
  chg:
    - name: "chg:pending"
      color: "F9A825"
      description: "CHG document awaiting approval"
    - name: "chg:approved"
      color: "43A047"
      description: "CHG document approved"
    - name: "chg:rejected"
      color: "D32F2F"
      description: "CHG document rejected"

  # === COMPONENT LABELS ===
  component:
    - name: "component:api"
      color: "1D76DB"
      description: "API/backend component"
    - name: "component:frontend"
      color: "5319E7"
      description: "Frontend/UI component"
    - name: "component:infrastructure"
      color: "006B75"
      description: "Infrastructure/DevOps"
    - name: "component:agents"
      color: "7057FF"
      description: "AI agents"
    - name: "component:docs"
      color: "0075CA"
      description: "Documentation"

  # === STATUS LABELS ===
  status:
    - name: "status:blocked"
      color: "D73A4A"
      description: "Blocked by dependency"
    - name: "status:wontfix"
      color: "FFFFFF"
      description: "Will not be fixed"
    - name: "status:duplicate"
      color: "CFD3D7"
      description: "Duplicate issue"
```

### New File: `governance/scripts/setup-all-labels.sh`

```bash
#!/bin/bash
# Create all labels from LABEL_REGISTRY.yaml
# Usage: ./setup-all-labels.sh <owner> <repo>
#
# Prerequisites:
# - gh CLI authenticated
# - PyYAML installed (pip install pyyaml)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY="${SCRIPT_DIR}/../github/LABEL_REGISTRY.yaml"

OWNER="${1:?Usage: $0 <owner> <repo>}"
REPO="${2:?Usage: $0 <owner> <repo>}"

echo "Creating labels for ${OWNER}/${REPO} from ${REGISTRY}"

python3 << EOF
import yaml
import subprocess
import sys

with open("${REGISTRY}") as f:
    data = yaml.safe_load(f)

total = 0
created = 0
failed = 0

for category, labels in data.get("categories", {}).items():
    print(f"\n=== {category.upper()} ===")
    for label in labels:
        total += 1
        cmd = [
            "gh", "label", "create", label["name"],
            "--color", label["color"],
            "--description", label["description"],
            "--repo", "${OWNER}/${REPO}",
            "--force"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ {label['name']}")
            created += 1
        else:
            print(f"  ✗ {label['name']}: {result.stderr.strip()}")
            failed += 1

print(f"\n=== Summary ===")
print(f"Total: {total}, Created: {created}, Failed: {failed}")
sys.exit(1 if failed > 0 else 0)
EOF
```

---

## Phase 6: Extend Traceability to GitHub

**Problem**: SDD cumulative tags (@brd, @prd, etc.) don't persist into GitHub issues/PRs.

### Step 6.1: Update Issue Template

**File**: `ai_dev_ssd_flow/PROJECT/.github/ISSUE_TEMPLATE/sdd-task.yml`

Add structured traceability section:
```yaml
  - type: textarea
    id: traceability
    attributes:
      label: "SDD Traceability"
      description: "Auto-populated from TASKS file. Do not edit manually."
      value: |
        <!-- Machine-readable traceability - DO NOT EDIT -->
        | Tag | Reference |
        |-----|-----------|
        | @tasks | TASKS-NN.MM.PP |
        | @spec | SPEC-NN |
        | @req | REQ-NN:REQ.NN.MM |
        | @sys | SYS-NN:SYS.NN.MM |
        | @adr | ADR-NN |
        | @ears | EARS-NN:EARS.NN.MM |
        | @prd | PRD-NN:PRD.NN.MM |
        | @brd | BRD-NN:BRD.NN.MM |
    validations:
      required: true
```

### Step 6.2: Create PR Template

**New File**: `.github/PULL_REQUEST_TEMPLATE.md`

```markdown
## Summary

<!-- Brief description of changes (1-2 sentences) -->

## Linked Issue

Closes #

## SDD Traceability

<!-- Copy from linked issue if source:sdd, otherwise delete this section -->

| Tag | Reference |
|-----|-----------|
| @tasks | |
| @spec | |
| @req | |
| @brd | |

## Changes

-

## Testing

- [ ] Unit tests pass (`pytest tests/unit/`)
- [ ] Integration tests pass (`pytest tests/integration/`)
- [ ] Manual testing completed

## Checklist

- [ ] Code follows project conventions
- [ ] Tests added/updated
- [ ] Documentation updated (if applicable)
- [ ] Traceability tags present (if `source:sdd`)
- [ ] Acceptance criteria verified (checked in linked issue)
```

### Step 6.3: Update tasks_to_github.py

**File**: `ai_dev_ssd_flow/scripts/tasks_to_github.py`

Add the following functionality:

1. **Read labels from registry**:
```python
def load_label_registry(registry_path: Path) -> dict:
    """Load labels from LABEL_REGISTRY.yaml."""
    if registry_path.exists():
        with open(registry_path) as f:
            data = yaml.safe_load(f)
        return {
            label["name"]
            for category in data.get("categories", {}).values()
            for label in category
        }
    return set()
```

2. **Validate labels before applying**:
```python
def validate_labels(labels: list[str], valid_labels: set[str]) -> list[str]:
    """Filter to only valid labels from registry."""
    return [l for l in labels if l in valid_labels]
```

3. **Add IPLAN guidance to issue body**:
```python
IPLAN_SECTION = """
---

## Implementation Plan

Before starting work on this issue, create an IPLAN document:

**Location**: `governance/plans/IPLAN-{issue_number}_{slug}.md`

See: [TASKS_IPLAN_BRIDGE.md](../governance/TASKS_IPLAN_BRIDGE.md) for workflow.
"""
```

---

## Phase 7: Bridge TSPEC and BDD to QA Execution

**Problem**: SDD has TSPEC (Layer 10) and BDD (Layer 4), governance has QA workflow. No connection.

### New File: `governance/TSPEC_BDD_QA_BRIDGE.md`

```markdown
# TSPEC and BDD to QA Bridge

## Overview

This document bridges SDD test specifications (TSPEC Layer 10, BDD Layer 4) with governance QA execution workflows.

---

## Test Types and Execution Environment

### Test Pyramid

```
           /\
          /  \  BDD Acceptance (Staging)
         /    \
        /------\
       / FTEST  \ Functional (Staging)
      /----------\
     /   STEST    \ System (Staging)
    /--------------\
   /     ITEST      \ Integration (CI)
  /------------------\
 /       UTEST        \ Unit (CI)
/______________________\
```

### Mapping

| Test Type | SDD Layer | Execution | Environment | Coverage Target |
|-----------|-----------|-----------|-------------|-----------------|
| **UTEST** | TSPEC (L10) | CI Pipeline | PR checks | ≥80% code coverage |
| **ITEST** | TSPEC (L10) | CI Pipeline | PR checks | ≥60% integration |
| **STEST** | TSPEC (L10) | QA Workflow | Staging | Critical paths |
| **FTEST** | TSPEC (L10) | QA Workflow | Staging | Feature coverage |
| **BDD** | BDD (L4) | QA Workflow | Staging | User acceptance |

---

## Workflow Integration

### During Development (CI)

```
Code committed to PR
    ↓
ci.yml triggers
    ↓
├── pytest tests/unit/ (UTEST)
│   └── Coverage gate: ≥80%
├── pytest tests/integration/ (ITEST)
│   └── Coverage gate: ≥60%
└── Security scan
    ↓
PR ready for review
```

### After Staging Deployment (QA)

```
All phase issues closed
    ↓
deploy-staging.yml deploys to staging
    ↓
create-qa-testing-issue.yml creates ai:qa-testing issue
    ↓
execute-qa-testing.yml triggers (daily 06:00-08:00 EST)
    ↓
├── Smoke tests (health endpoints)
├── pytest tests/system/ (STEST)
├── pytest tests/functional/ (FTEST)
└── pytest tests/bdd/ --bdd (BDD via pytest-bdd)
    ↓
Results evaluated:
    ├── Pass: ai:qa-passed label → Production Ready
    └── Fail: create-bug-issue.yml → Bug fix iteration (max 3)
```

---

## TSPEC Registry Integration

### Registry Location

`docs/10_TSPEC/test_registry.yaml`

### Registry Structure

```yaml
# test_registry.yaml
tests:
  - nodeid: "tests/unit/test_threshold.py::test_check_threshold"
    tspec_id: "TSPEC-01.UTEST.01"
    upstream_refs:
      - "@spec: SPEC-01"
      - "@req: REQ-01:REQ.01.01"
    coverage_targets:
      - "src/threshold.py::ThresholdChecker"

  - nodeid: "tests/bdd/features/budget_alerts.feature::Budget threshold exceeded"
    tspec_id: "TSPEC-01.BDD.01"
    bdd_scenario: "BDD-01:BDD.01.01"
    upstream_refs:
      - "@ears: EARS-01:EARS.01.01"
      - "@prd: PRD-01:PRD.01.01"
```

### QA Script Integration

Update `governance/scripts/workflows/execute_qa_tests.py`:

```python
def load_tspec_registry(path: Path = Path("docs/10_TSPEC/test_registry.yaml")) -> dict:
    """Load TSPEC test registry for result mapping."""
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f)
    return {"tests": []}

def map_results_to_tspec(pytest_results: dict, registry: dict) -> list[dict]:
    """Map pytest results to TSPEC entries for traceability."""
    registry_map = {t["nodeid"]: t for t in registry.get("tests", [])}
    mapped = []
    for test in pytest_results.get("tests", []):
        tspec_entry = registry_map.get(test["nodeid"])
        if tspec_entry:
            mapped.append({
                "tspec_id": tspec_entry.get("tspec_id"),
                "bdd_scenario": tspec_entry.get("bdd_scenario"),
                "outcome": test["outcome"],
                "duration": test["duration"],
                "upstream_refs": tspec_entry.get("upstream_refs", [])
            })
    return mapped

def generate_traceability_report(mapped_results: list[dict]) -> str:
    """Generate markdown traceability report for QA issue."""
    lines = ["## Test Traceability Report", "", "| TSPEC ID | Outcome | Duration | Upstream |"]
    lines.append("|----------|---------|----------|----------|")
    for r in mapped_results:
        refs = ", ".join(r.get("upstream_refs", [])[:2])
        lines.append(f"| {r['tspec_id']} | {r['outcome']} | {r['duration']:.2f}s | {refs} |")
    return "\n".join(lines)
```

---

## BDD Execution

### Feature File Location

`tests/bdd/features/*.feature`

### Pytest-BDD Configuration

```python
# tests/bdd/conftest.py
import pytest
from pytest_bdd import scenarios

# Load all scenarios from features directory
scenarios("features/")
```

### Running BDD Tests

```bash
# Run all BDD tests
pytest tests/bdd/ --bdd

# Run with verbose BDD output
pytest tests/bdd/ -v --gherkin-terminal-reporter

# Generate BDD report
pytest tests/bdd/ --bdd --html=reports/bdd_report.html
```

---

## Coverage Requirements

| Test Type | Environment | Minimum Coverage | Gate Type |
|-----------|-------------|------------------|-----------|
| UTEST | CI | ≥80% | Block PR |
| ITEST | CI | ≥60% | Warning |
| STEST | Staging | Critical paths | Block Production |
| FTEST | Staging | Feature paths | Block Production |
| BDD | Staging | Acceptance | Block Production |

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `ai_dev_ssd_flow/10_TSPEC/TSPEC-TEMPLATE.yaml` | TSPEC format |
| `ai_dev_ssd_flow/04_BDD/BDD-TEMPLATE.feature` | BDD scenario format |
| `governance/templates/qa/01-testing-strategy.md` | Testing strategy |
| `governance/templates/qa/03-ci-pipeline-spec.md` | CI pipeline config |
```

### Update: `governance/scripts/workflows/execute_qa_tests.py`

Add imports and functions from the bridge document above.

---

## Phase 8: Create SDD Depth Configuration

**Problem**: SDD depths (Lite/Standard/Full) not enforced at project level.

### New File: `governance/templates/sdd_config.yaml`

```yaml
# SDD Project Configuration
# Copy to project root and customize.
#
# This file configures which SDD depth is used and enables
# corresponding validation and change management rules.

# SDD depth: lite | standard | full
sdd_depth: "standard"

# Required layers per depth
required_layers:
  lite:
    - 0   # REF
    - 1   # BRD-MVP
    - 2   # PRD-MVP
    - 11  # TASKS-MVP
  standard:
    - 0   # REF
    - 1   # BRD
    - 2   # PRD
    - 3   # EARS
    - 5   # ADR
    - 6   # SYS
    - 7   # REQ
    - 11  # TASKS
  full:
    - 0   # REF
    - 1   # BRD
    - 2   # PRD
    - 3   # EARS
    - 4   # BDD
    - 5   # ADR
    - 6   # SYS
    - 7   # REQ
    - 8   # CTR (optional)
    - 9   # SPEC
    - 10  # TSPEC
    - 11  # TASKS

# Validation settings
validation:
  enforce_traceability: true
  require_quality_score: 90      # Auto-approve if score >= this
  block_on_missing_layers: true  # Fail CI if required layers missing

# Change management
change_management:
  method: "pr-based"             # pr-based | chg-gated
  # Note: chg-gated only valid for full depth

# Test requirements by depth
testing:
  lite:
    utest_coverage: 60
    itest_coverage: 0
    require_bdd: false
  standard:
    utest_coverage: 80
    itest_coverage: 60
    require_bdd: false
  full:
    utest_coverage: 80
    itest_coverage: 60
    require_bdd: true
```

### New File: `ai_dev_ssd_flow/scripts/validate_depth.py`

```python
#!/usr/bin/env python3
"""
Validate project has required SDD artifacts for configured depth.

Usage:
    python validate_depth.py [config_path] [docs_root]

Example:
    python validate_depth.py sdd_config.yaml docs/
"""

import yaml
from pathlib import Path
import sys
import argparse

LAYER_DIRS = {
    0: "00_REF",
    1: "01_BRD",
    2: "02_PRD",
    3: "03_EARS",
    4: "04_BDD",
    5: "05_ADR",
    6: "06_SYS",
    7: "07_REQ",
    8: "08_CTR",
    9: "09_SPEC",
    10: "10_TSPEC",
    11: "11_TASKS",
}

LAYER_NAMES = {
    0: "REF (Reference)",
    1: "BRD (Business Requirements)",
    2: "PRD (Product Requirements)",
    3: "EARS (Formal Requirements)",
    4: "BDD (Behavior Tests)",
    5: "ADR (Architecture Decisions)",
    6: "SYS (System Requirements)",
    7: "REQ (Atomic Requirements)",
    8: "CTR (Contracts)",
    9: "SPEC (Technical Specifications)",
    10: "TSPEC (Test Specifications)",
    11: "TASKS (Implementation Tasks)",
}


def load_config(config_path: Path) -> dict:
    """Load SDD configuration."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def validate_depth(config: dict, docs_root: Path) -> tuple[bool, list[str], list[str]]:
    """
    Check required layers exist for configured depth.

    Returns:
        (is_valid, present_layers, missing_layers)
    """
    depth = config.get("sdd_depth", "standard")
    required = config.get("required_layers", {}).get(depth, [])

    present = []
    missing = []

    for layer in required:
        layer_dir = docs_root / LAYER_DIRS[layer]
        if layer_dir.exists() and any(layer_dir.iterdir()):
            present.append(f"Layer {layer}: {LAYER_NAMES[layer]}")
        else:
            missing.append(f"Layer {layer}: {LAYER_NAMES[layer]}")

    return len(missing) == 0, present, missing


def main():
    parser = argparse.ArgumentParser(description="Validate SDD depth configuration")
    parser.add_argument("config", nargs="?", default="sdd_config.yaml",
                        help="Path to sdd_config.yaml")
    parser.add_argument("docs", nargs="?", default="docs",
                        help="Path to docs directory")
    parser.add_argument("--strict", action="store_true",
                        help="Exit with error if validation fails")
    args = parser.parse_args()

    config_path = Path(args.config)
    docs_root = Path(args.docs)

    if not config_path.exists():
        print(f"Config file not found: {config_path}")
        print("Create from template: governance/templates/sdd_config.yaml")
        sys.exit(1 if args.strict else 0)

    config = load_config(config_path)
    depth = config.get("sdd_depth", "standard")

    print(f"SDD Depth: {depth.upper()}")
    print(f"Docs Root: {docs_root}")
    print()

    is_valid, present, missing = validate_depth(config, docs_root)

    if present:
        print("✓ Present Layers:")
        for layer in present:
            print(f"  - {layer}")

    if missing:
        print("\n✗ Missing Layers:")
        for layer in missing:
            print(f"  - {layer}")

    print()
    if is_valid:
        print(f"✓ All required layers present for {depth} depth")
        sys.exit(0)
    else:
        print(f"✗ Missing {len(missing)} required layer(s) for {depth} depth")
        block = config.get("validation", {}).get("block_on_missing_layers", True)
        sys.exit(1 if (args.strict or block) else 0)


if __name__ == "__main__":
    main()
```

---

## Phase 9: Document Testing Model in SDD and Governance

**Problem**: The testing model (test pyramid, execution environments, TSPEC types) is not documented in the framework. Developers don't know when UTEST/ITEST run in CI vs when STEST/FTEST/BDD run on staging.

### Step 9.1: Create Test Pyramid Guide

**New File**: `ai_dev_ssd_flow/10_TSPEC/TEST_PYRAMID_GUIDE.md`

```markdown
# Test Pyramid Guide

## Overview

This guide defines the SDD testing model, explaining when and where each test type executes in the development lifecycle.

---

## Test Pyramid

```
              /\
             /  \  BDD Acceptance Tests
            /    \     (Staging - Few, Slow)
           /------\
          / FTEST  \  Functional Tests
         /----------\    (Staging)
        /   STEST    \  System Tests
       /--------------\    (Staging)
      /     ITEST      \  Integration Tests
     /------------------\    (CI - Moderate)
    /       UTEST        \  Unit Tests
   /______________________\    (CI - Many, Fast)
```

**Principle**: More tests at the bottom (fast, cheap), fewer at the top (slow, expensive).

---

## Test Types Defined

### UTEST (Unit Tests)

| Aspect | Description |
|--------|-------------|
| **Layer** | TSPEC (Layer 10) |
| **Scope** | Single function/method, isolated |
| **Mocking** | External dependencies mocked |
| **Execution** | CI Pipeline (every PR) |
| **Coverage Target** | ≥80% code coverage |
| **Speed** | Fast (<1s per test) |
| **Location** | `tests/unit/` |

**Example TSPEC Entry**:
```yaml
- id: TSPEC-01.UTEST.01
  type: UTEST
  target: src/threshold.py::ThresholdChecker::check
  upstream: "@req: REQ-01:REQ.01.01"
```

### ITEST (Integration Tests)

| Aspect | Description |
|--------|-------------|
| **Layer** | TSPEC (Layer 10) |
| **Scope** | Multiple components together |
| **Mocking** | External services mocked (DB, APIs) |
| **Execution** | CI Pipeline (every PR) |
| **Coverage Target** | ≥60% integration paths |
| **Speed** | Moderate (1-10s per test) |
| **Location** | `tests/integration/` |

**Example TSPEC Entry**:
```yaml
- id: TSPEC-01.ITEST.01
  type: ITEST
  target: src/services/budget_service.py
  dependencies: [database, pubsub]
  upstream: "@sys: SYS-01:SYS.01.01"
```

### STEST (System Tests)

| Aspect | Description |
|--------|-------------|
| **Layer** | TSPEC (Layer 10) |
| **Scope** | Full system, end-to-end paths |
| **Mocking** | None - real services |
| **Execution** | QA Workflow (staging only) |
| **Coverage Target** | Critical user paths |
| **Speed** | Slow (10s-1min per test) |
| **Location** | `tests/system/` |

**Example TSPEC Entry**:
```yaml
- id: TSPEC-01.STEST.01
  type: STEST
  target: Full budget alert flow
  environment: staging
  upstream: "@ears: EARS-01:EARS.01.01"
```

### FTEST (Functional Tests)

| Aspect | Description |
|--------|-------------|
| **Layer** | TSPEC (Layer 10) |
| **Scope** | Feature-specific functionality |
| **Mocking** | None - real services |
| **Execution** | QA Workflow (staging only) |
| **Coverage Target** | All feature requirements |
| **Speed** | Moderate-slow |
| **Location** | `tests/functional/` |

**Example TSPEC Entry**:
```yaml
- id: TSPEC-01.FTEST.01
  type: FTEST
  feature: Budget threshold notifications
  upstream: "@prd: PRD-01:PRD.01.01"
```

### BDD (Behavior-Driven Development)

| Aspect | Description |
|--------|-------------|
| **Layer** | BDD (Layer 4) |
| **Scope** | User acceptance scenarios |
| **Format** | Gherkin (Given/When/Then) |
| **Execution** | QA Workflow (staging only) |
| **Coverage Target** | All acceptance criteria |
| **Speed** | Slow (user-facing flows) |
| **Location** | `tests/bdd/features/` |

**Example BDD Scenario**:
```gherkin
@brd: BRD-01:BRD.01.01
@prd: PRD-01:PRD.01.01
Scenario: User receives email when budget exceeds 80%
  Given a budget of $10,000 for project "web-app"
  And alert threshold configured at 80%
  When current spend reaches $8,100
  Then an email alert should be sent within 5 minutes
```

---

## Execution Environments

### CI Pipeline (Development)

**Triggers**: Every PR, every push to feature branches

**Tests Run**:
- ✅ UTEST (unit tests)
- ✅ ITEST (integration tests)
- ❌ STEST (requires staging)
- ❌ FTEST (requires staging)
- ❌ BDD (requires staging)

**Workflow**: `.github/workflows/ci.yml`

```
PR Created/Updated
    ↓
├── Lint (ruff, mypy)
├── UTEST (pytest tests/unit/)
│   └── Coverage gate: ≥80% or fail
├── ITEST (pytest tests/integration/)
│   └── Coverage gate: ≥60% or warn
└── Security scan
    ↓
PR Ready for Review
```

### QA Staging (Quality Assurance)

**Triggers**: Phase completion, staging deployment

**Tests Run**:
- ❌ UTEST (already passed in CI)
- ❌ ITEST (already passed in CI)
- ✅ STEST (system tests)
- ✅ FTEST (functional tests)
- ✅ BDD (acceptance tests)

**Workflow**: `.github/workflows/execute-qa-testing.yml`

```
Staging Deployment Complete
    ↓
ai:qa-testing issue created
    ↓
├── Smoke tests (health endpoints)
├── STEST (pytest tests/system/)
├── FTEST (pytest tests/functional/)
└── BDD (pytest tests/bdd/ --bdd)
    ↓
Pass → ai:qa-passed → Production Ready
Fail → Bug issue created (iteration:N)
```

---

## Test Directory Structure

```
tests/
├── unit/                    # UTEST - Unit tests (CI)
│   ├── conftest.py
│   ├── test_threshold.py
│   └── test_calculator.py
├── integration/             # ITEST - Integration tests (CI)
│   ├── conftest.py
│   ├── test_budget_service.py
│   └── test_notification_service.py
├── system/                  # STEST - System tests (Staging)
│   ├── conftest.py
│   └── test_full_alert_flow.py
├── functional/              # FTEST - Functional tests (Staging)
│   ├── conftest.py
│   └── test_budget_features.py
└── bdd/                     # BDD - Acceptance tests (Staging)
    ├── conftest.py
    ├── features/
    │   ├── budget_alerts.feature
    │   └── user_notifications.feature
    └── step_defs/
        ├── budget_steps.py
        └── notification_steps.py
```

---

## Coverage Requirements by SDD Depth

| SDD Depth | UTEST | ITEST | STEST/FTEST | BDD |
|-----------|-------|-------|-------------|-----|
| **Lite** | ≥60% | Optional | Optional | No |
| **Standard** | ≥80% | ≥60% | Critical paths | Optional |
| **Full** | ≥80% | ≥60% | Full coverage | Required |

---

## Workflow Summary

```
Code Generation (Layer 12)
         ↓
    ┌────────────────────────────────────┐
    │         CI PIPELINE                │
    │  ┌──────────┐    ┌──────────┐     │
    │  │  UTEST   │    │  ITEST   │     │
    │  │  ≥80%    │    │  ≥60%    │     │
    │  └──────────┘    └──────────┘     │
    └────────────────────────────────────┘
         ↓
    PR Merge → Deploy to Dev
         ↓
    Phase Complete → Deploy to Staging
         ↓
    ┌────────────────────────────────────┐
    │       QA STAGING PIPELINE          │
    │  ┌────────┐ ┌────────┐ ┌────────┐ │
    │  │ STEST  │ │ FTEST  │ │  BDD   │ │
    │  │ System │ │Feature │ │Accept. │ │
    │  └────────┘ └────────┘ └────────┘ │
    └────────────────────────────────────┘
         ↓
    Pass → Production Ready
    Fail → Bug Issue (max 3 iterations)
```

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `governance/TSPEC_BDD_QA_BRIDGE.md` | QA workflow integration |
| `governance/templates/qa/01-testing-strategy.md` | Testing strategy details |
| `governance/templates/qa/03-ci-pipeline-spec.md` | CI pipeline configuration |
| `ai_dev_ssd_flow/04_BDD/BDD-TEMPLATE.feature` | BDD scenario template |
| `ai_dev_ssd_flow/10_TSPEC/TSPEC-TEMPLATE.yaml` | TSPEC format template |
```

### Step 9.2: Update TSPEC Template with Test Type Guidance

**File**: `ai_dev_ssd_flow/10_TSPEC/TSPEC-TEMPLATE.yaml`

Add header comment explaining test types:
```yaml
# TSPEC Template - Test Specifications
#
# Test Types and Execution:
# ┌─────────┬────────────────┬───────────────────┐
# │ Type    │ Environment    │ Coverage Target   │
# ├─────────┼────────────────┼───────────────────┤
# │ UTEST   │ CI Pipeline    │ ≥80% code         │
# │ ITEST   │ CI Pipeline    │ ≥60% integration  │
# │ STEST   │ QA Staging     │ Critical paths    │
# │ FTEST   │ QA Staging     │ Feature coverage  │
# └─────────┴────────────────┴───────────────────┘
#
# See: TEST_PYRAMID_GUIDE.md for full documentation
```

### Step 9.3: Update BDD Template with Execution Context

**File**: `ai_dev_ssd_flow/04_BDD/BDD-TEMPLATE.feature`

Add header comment:
```gherkin
# BDD Template - Behavior-Driven Development Scenarios
#
# Execution Environment: QA STAGING ONLY
# - BDD tests run AFTER staging deployment
# - Tests validate user acceptance criteria
# - Part of QA workflow (ai:qa-testing)
#
# DO NOT run in CI pipeline - use UTEST/ITEST for CI
#
# See: TEST_PYRAMID_GUIDE.md for test pyramid documentation
```

### Step 9.4: Update Governance QA Documentation

**File**: `governance/templates/qa/01-testing-strategy.md`

Add section referencing test pyramid:
```markdown
## Test Pyramid Model

This project follows the SDD test pyramid model. See [`ai_dev_ssd_flow/10_TSPEC/TEST_PYRAMID_GUIDE.md`](../../ai_dev_ssd_flow/10_TSPEC/TEST_PYRAMID_GUIDE.md) for the authoritative guide.

### Summary

| Test Type | Environment | When |
|-----------|-------------|------|
| UTEST, ITEST | CI Pipeline | Every PR |
| STEST, FTEST, BDD | QA Staging | After staging deploy |

### Key Principle

**CI tests** (UTEST, ITEST) verify code correctness during development.
**Staging tests** (STEST, FTEST, BDD) verify system behavior before production.
```

### Step 9.5: Update SDD Depth Guide with Testing Requirements

**File**: `governance/SDD_DEPTH_GUIDE.md`

Add testing requirements section:
```markdown
## Testing Requirements by Depth

| Depth | UTEST | ITEST | STEST/FTEST | BDD |
|-------|-------|-------|-------------|-----|
| **Lite** | ≥60% coverage | Optional | Optional | Not required |
| **Standard** | ≥80% coverage | ≥60% coverage | Critical paths | Optional |
| **Full** | ≥80% coverage | ≥60% coverage | Full coverage | Required |

### Execution Model

All depths follow the same test pyramid execution model:
- **CI Pipeline**: UTEST + ITEST (development)
- **QA Staging**: STEST + FTEST + BDD (pre-production)

See: [`ai_dev_ssd_flow/10_TSPEC/TEST_PYRAMID_GUIDE.md`](../ai_dev_ssd_flow/10_TSPEC/TEST_PYRAMID_GUIDE.md)
```

---

## Files Summary

### New Files (13)

| File | Purpose |
|------|---------|
| `governance/TASKS_IPLAN_BRIDGE.md` | Bridge TASKS to IPLAN workflow |
| `governance/CHG_GOVERNANCE_BRIDGE.md` | Bridge CHG 4-Gate to phases |
| `governance/TSPEC_BDD_QA_BRIDGE.md` | Bridge TSPEC/BDD to QA execution |
| `governance/github/LABEL_REGISTRY.yaml` | Complete unified label registry |
| `governance/github/WORKFLOW_INTEGRATION.md` | Workflow categories and triggers |
| `governance/scripts/setup-all-labels.sh` | Create labels from registry |
| `governance/templates/sdd_config.yaml` | SDD depth configuration |
| `ai_dev_ssd_flow/scripts/validate_depth.py` | Depth validation script |
| `ai_dev_ssd_flow/10_TSPEC/TEST_PYRAMID_GUIDE.md` | **Test pyramid and execution model documentation** |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR template with traceability |
| `.github/workflows/sdd-artifact-validation.yml` | Migrated SDD validation workflow |

### Files to Update (14)

| File | Change |
|------|--------|
| `ai_dev_ssd_flow/PROJECT/PROJECT_MODEL.md` | Fix 20 broken paths |
| `README.md` | Fix 10 broken paths |
| `MULTI_PROJECT_SETUP_GUIDE.md` | Fix 19 broken paths |
| `MULTI_PROJECT_QUICK_REFERENCE.md` | Fix 8 broken paths |
| `governance/README.md` | Add SDD Integration section |
| `governance/GOVERNANCE_RULES.md` | Add TASKS integration section |
| `governance/AI_ISSUE_LIFECYCLE.md` | Add Issue Sources section |
| `governance/plans/IPLAN-TEMPLATE.md` | Add SDD traceability section |
| `governance/scripts/setup-ai-pr-review-labels.sh` | Add CHG labels |
| `governance/scripts/workflows/execute_qa_tests.py` | Add TSPEC integration |
| `ai_dev_ssd_flow/10_TSPEC/TSPEC-TEMPLATE.yaml` | **Add test type execution guidance header** |
| `ai_dev_ssd_flow/04_BDD/BDD-TEMPLATE.feature` | **Add staging-only execution context header** |
| `governance/templates/qa/01-testing-strategy.md` | **Add test pyramid reference section** |
| `governance/SDD_DEPTH_GUIDE.md` | **Add testing requirements by depth** |

### Files to Remove/Consolidate (1)

| File | Action |
|------|--------|
| `governance/templates/IPLAN-TEMPLATE.md` | Replace with symlink to `governance/plans/IPLAN-TEMPLATE.md` |

---

## Verification Checklist

```bash
cd /opt/data/ucx_framework

# 1. No broken path references
echo "=== Checking broken paths ==="
count=$(grep -r "governance/sdd" *.md ai_dev_ssd_flow/**/*.md 2>/dev/null | wc -l)
[[ $count -eq 0 ]] && echo "PASS: No broken paths" || echo "FAIL: $count broken paths found"

# 2. Bridge documents exist
echo -e "\n=== Checking bridge documents ==="
for f in governance/TASKS_IPLAN_BRIDGE.md governance/CHG_GOVERNANCE_BRIDGE.md governance/TSPEC_BDD_QA_BRIDGE.md; do
  [[ -f "$f" ]] && echo "PASS: $f exists" || echo "FAIL: $f missing"
done

# 3. Label registry valid YAML
echo -e "\n=== Checking label registry ==="
python3 -c "import yaml; yaml.safe_load(open('governance/github/LABEL_REGISTRY.yaml'))" 2>/dev/null \
  && echo "PASS: Label registry valid" || echo "FAIL: Label registry invalid"

# 4. Workflow migrated
echo -e "\n=== Checking workflows ==="
[[ -f ".github/workflows/sdd-artifact-validation.yml" ]] \
  && echo "PASS: SDD workflow migrated" || echo "FAIL: SDD workflow missing"

# 5. No marketplace actions in SDD workflow
echo -e "\n=== Checking marketplace actions ==="
if [[ -f ".github/workflows/sdd-artifact-validation.yml" ]]; then
  grep -q "uses: actions/" .github/workflows/sdd-artifact-validation.yml \
    && echo "FAIL: Marketplace actions found" || echo "PASS: No marketplace actions"
fi

# 6. Depth config template exists
echo -e "\n=== Checking depth config ==="
[[ -f "governance/templates/sdd_config.yaml" ]] \
  && echo "PASS: Depth config template exists" || echo "FAIL: Depth config missing"

# 7. PR template exists
echo -e "\n=== Checking PR template ==="
[[ -f ".github/PULL_REQUEST_TEMPLATE.md" ]] \
  && echo "PASS: PR template exists" || echo "FAIL: PR template missing"

# 8. IPLAN template consolidated
echo -e "\n=== Checking IPLAN consolidation ==="
if [[ -L "governance/templates/IPLAN-TEMPLATE.md" ]]; then
  echo "PASS: IPLAN template is symlink"
elif [[ ! -f "governance/templates/IPLAN-TEMPLATE.md" ]]; then
  echo "PASS: Duplicate IPLAN removed"
else
  echo "FAIL: Duplicate IPLAN still exists (not a symlink)"
fi

# 9. governance/README.md updated
echo -e "\n=== Checking README updates ==="
grep -q "TASKS_IPLAN_BRIDGE" governance/README.md 2>/dev/null \
  && echo "PASS: README references bridges" || echo "FAIL: README missing bridge references"

# 10. Validate depth script exists
echo -e "\n=== Checking validation script ==="
[[ -f "ai_dev_ssd_flow/scripts/validate_depth.py" ]] \
  && echo "PASS: validate_depth.py exists" || echo "FAIL: validate_depth.py missing"

echo -e "\n=== Verification complete ==="
```

---

## Implementation Order

| Phase | Priority | Effort | Dependencies | Est. Files |
|-------|----------|--------|--------------|------------|
| 1. Fix broken paths | Critical | Low | None | 4 |
| 2. IPLAN consolidation + Bridge | High | Medium | Phase 1 | 6 |
| 3. Workflow integration | High | Medium | Phase 1 | 2 |
| 4. CHG bridge | Medium | Low | Phase 1 | 2 |
| 5. Label registry | Medium | Low | None | 2 |
| 6. Traceability | Medium | Medium | Phase 2 | 3 |
| 7. TSPEC/BDD→QA bridge | Medium | Medium | None | 2 |
| 8. Depth config | Low | Low | None | 2 |

---

## Rollback Strategy

If issues occur during implementation:

### Path Changes (Phase 1)
```bash
# Revert using git
git checkout -- README.md MULTI_PROJECT_*.md ai_dev_ssd_flow/PROJECT/PROJECT_MODEL.md
```

### New Files (Phases 2-8)
```bash
# Simply delete new files - no existing functionality affected
rm governance/TASKS_IPLAN_BRIDGE.md
rm governance/CHG_GOVERNANCE_BRIDGE.md
rm governance/TSPEC_BDD_QA_BRIDGE.md
# etc.
```

### Workflow Changes (Phase 3)
```bash
# Delete new workflow - existing workflows unaffected
rm .github/workflows/sdd-artifact-validation.yml
```

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing workflows | Low | High | New workflow added, existing unchanged |
| Path changes break links | Medium | Medium | Grep validation before/after |
| Label changes affect automation | Low | Medium | Additions only, no removals |
| Script changes introduce bugs | Low | Medium | Test in isolated branch |
| IPLAN consolidation confusion | Low | Low | Clear symlink documentation |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-18 | Initial plan |
| 2.0 | 2026-02-18 | Fixed all gaps: added complete label registry, IPLAN consolidation, README updates, TSPEC/BDD testing model, rollback strategy, verification script |
