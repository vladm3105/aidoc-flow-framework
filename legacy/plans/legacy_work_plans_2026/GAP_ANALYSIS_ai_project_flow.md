# Gap Analysis: AI Project Flow Framework Plan

**Date**: 2026-02-16
**Plan Under Review**: `PLAN_ai_project_flow_framework.md`

---

## Executive Summary

The plan has **15 significant gaps** that need to be addressed. The main issues are:
- Incorrect file counts (workflows, issue templates, scripts, docs)
- Missing root-level deployment documentation
- Missing component template structure
- Missing configuration files

| Category | Gap Count | Severity |
|----------|-----------|----------|
| Incorrect Counts | 5 | HIGH |
| Missing Files | 6 | HIGH |
| Missing Sections | 3 | MEDIUM |
| Structural Issues | 1 | LOW |

---

## GAP 1: Workflow Count Incorrect

**Severity**: HIGH

**Plan States**: 20 workflows
**Actual Count**: 22 files (20 active + 2 disabled)

**Actual Workflow List**:
```
Active (20):
- agent-dispatch.yml
- ai-review.yml
- auto-add-to-project.yml
- check-all-phases-dev.yml
- check-phase-completion.yml
- ci.yml
- create-bug-issue.yml
- create-deployment-issue.yml
- create-qa-testing-issue.yml
- deploy-dev.yml
- deploy-prod.yml
- deploy-staging.yml
- execute-qa-testing.yml
- issue-label-sync.yml
- phase-transition.yml
- pr-merge-cleanup.yml
- release.yml
- rollback-prod.yml

Disabled (2):
- cleanup-pr-env.yml.disabled
- deploy-dev-pr.yml.disabled
```

**Resolution**: Update plan to list all 22 workflows, note disabled ones separately.

---

## GAP 2: Issue Template Count Incorrect

**Severity**: HIGH

**Plan States**: 8 templates
**Actual Count**: 11 files (10 templates + 1 config.yml)

**Actual Template List**:
| Template | In Plan? |
|----------|----------|
| architecture_proposal.md | ✅ |
| bug_report.md | ✅ |
| config.yml | ✅ |
| **cost_analysis.md** | ❌ MISSING |
| development_issue.md | ✅ |
| feature_request.md | ✅ |
| **infra_task.md** | ❌ MISSING |
| **mcp_server.md** | ❌ MISSING |
| research_task.md | ✅ |
| **security_report.md** | ❌ MISSING |
| ~~deployment_issue.md~~ | ❌ Listed but doesn't exist |
| ~~qa_testing.md~~ | ❌ Listed but doesn't exist |

**Resolution**:
- Add: cost_analysis.md, infra_task.md, mcp_server.md, security_report.md
- Remove: deployment_issue.md, qa_testing.md (these are created by workflows, not templates)

---

## GAP 3: Missing Root-Level Deployment Documentation

**Severity**: HIGH

**Plan States**: Root templates list only 8 files
**Missing Files**:
| File | Size | Purpose |
|------|------|---------|
| `AWS-DEPLOYMENT.md` | 7.3KB | AWS deployment guide |
| `AZURE-DEPLOYMENT.md` | 8.8KB | Azure deployment guide |
| `GCP-DEPLOYMENT.md` | 11KB | GCP deployment guide |
| `docker-compose.test.yml` | 1.5KB | Local test environment |

**Resolution**: Add these 4 files to "Root Documentation" section.

**Updated Root Templates (12 total)**:
```
README.md
README_AIAGENT.md
CLAUDE.md
DEVELOPER_GUIDE.md
CONTRIBUTING.md
HANDOFF.md
AWS-DEPLOYMENT.md       # NEW
AZURE-DEPLOYMENT.md     # NEW
GCP-DEPLOYMENT.md       # NEW
docker-compose.test.yml # NEW
.mcp.json
.env.example
```

---

## GAP 4: Scripts Count Incorrect

**Severity**: MEDIUM

**Plan States**: 23 scripts, keep ~15
**Actual Count**: 33 relevant scripts (excluding node_modules)

**Breakdown**:
| Category | Count | Files |
|----------|-------|-------|
| project_setup/ | 7 | setup_github_environments.sh, gcp/*.sh (6) |
| workflows/ | 16 | Python helpers + smoke_test.sh |
| ghes-runner/ | 10 | setup, config, runner scripts |

**Resolution**: Update scripts count to 33, clarify which are essential vs optional:
- **Essential (23)**: project_setup/* + workflows/*
- **Optional (10)**: ghes-runner/* (GHES-specific)

---

## GAP 5: Docs Count Severely Underestimated

**Severity**: HIGH

**Plan States**: "9 ADRs + 8 QA docs"
**Actual Count**: 70 total docs

**Breakdown**:
| Folder | Count | Plan Coverage |
|--------|-------|---------------|
| docs/adr/ | 10 | ✅ Mentioned (but count wrong) |
| docs/qa/ | 9 | ✅ Mentioned (but count wrong) |
| docs/core/ | 10 | ❌ NOT MENTIONED |
| docs/core/legacy/ | 10 | ❌ NOT MENTIONED |
| docs/UX/ | 2 | ❌ NOT MENTIONED |
| docs/UX/legacy/ | 21 | ❌ NOT MENTIONED |
| docs/architecture/ | 1 | ❌ NOT MENTIONED |
| docs/ (root) | 7 | ❌ NOT MENTIONED |

**Key Missing Docs**:
- `docs/PROJECT_DEFINITION.md` (30KB) - Project definition
- `docs/github-collaboration.md` - GitHub workflow guide
- `docs/documentation-best-practices.md` - Doc standards
- `docs/GCP-COST-GUARD.md`, `AWS-COST-GUARD.md`, `AZURE-COST-GUARD.md`
- `docs/MINIMAL-COST-GUARD.md`
- `docs/core/*.md` - Technical specifications (10 files)

**Resolution**:
1. Add `docs/core/` to framework (essential specs)
2. Add key root-level docs
3. Exclude `legacy/` folders (project-specific iterations)

**Updated Docs Section**:
```
docs/
├── adr/           # 10 files (3 samples + README)
├── qa/            # 9 files (all template)
├── core/          # 10 files (spec templates)  # NEW
├── architecture/  # 1 file (README)            # NEW
└── deployment/    # 3 cloud guides             # Keep as planned
```

---

## GAP 6: Missing Component Structure Templates

**Severity**: MEDIUM

**Issue**: Plan doesn't address `components/` folder structure.

**Actual Component Structure**:
```
components/
├── agents/
│   └── README.md
├── frontend/
│   └── README.md
├── gcp-cost-guard/
│   ├── README.md
│   ├── CHANGELOG.md
│   ├── src/
│   └── tests/
└── infrastructure/
    └── README.md
```

**Resolution**: Add component template section:
```
components/
├── README.md           # Component overview template
├── {component-name}/
│   ├── README.md      # Component README template
│   ├── CHANGELOG.md   # Changelog template
│   ├── src/           # Source structure
│   └── tests/         # Test structure
```

---

## GAP 7: Missing .claude Configuration

**Severity**: LOW

**Issue**: Plan doesn't mention `.claude/settings.local.json` (12KB)

**Contents**: Claude Code project-specific settings including:
- MCP server configurations
- Project-specific rules
- Session settings

**Resolution**: Add to templates section:
```
.claude/
└── settings.local.json.template
```

---

## GAP 8: Missing Placeholder Variables

**Severity**: MEDIUM

**Current Plan**: 30+ variables
**Missing Variables**:

| Variable | Description | Example |
|----------|-------------|---------|
| `{SERVICE_NAME}` | Main service name | `cost-guard` |
| `{DOCKER_IMAGE_PREFIX}` | Docker image prefix | `myproj` |
| `{SMOKE_TEST_ENDPOINTS}` | Health check URLs | `/health,/ready` |
| `{REVISION_RETENTION}` | Cloud Run revision count | `10` |
| `{MIN_INSTANCES}` | Min container instances | `0` |
| `{MAX_INSTANCES}` | Max container instances | `10` |
| `{MEMORY_LIMIT}` | Container memory | `1Gi` |
| `{CPU_LIMIT}` | Container CPU | `1` |

**Resolution**: Add infrastructure configuration variables section.

---

## GAP 9: Execution Step 4 - Missing Files

**Severity**: HIGH

**Plan Step 4**:
```bash
cp /opt/data/techtrend/AI-cost-monitoring/{README.md,README_AIAGENT.md,CLAUDE.md,DEVELOPER_GUIDE.md,CONTRIBUTING.md,HANDOFF.md,.mcp.json,.env.example} \
  /opt/data/ucx_framework/ai_project_flow/templates/
```

**Missing from command**:
- AWS-DEPLOYMENT.md
- AZURE-DEPLOYMENT.md
- GCP-DEPLOYMENT.md
- docker-compose.test.yml

**Resolution**: Update Step 4 command to include all 12 root files.

---

## GAP 10: Execution Step 6 - Incomplete Docs Copy

**Severity**: MEDIUM

**Plan Step 6**:
```bash
cp -r /opt/data/techtrend/AI-cost-monitoring/docs/{adr,qa} \
  /opt/data/ucx_framework/ai_project_flow/docs/
```

**Missing**:
- `docs/core/` (10 technical spec files)
- `docs/architecture/` (1 README)
- Root docs (7 files including PROJECT_DEFINITION.md)

**Resolution**: Update Step 6:
```bash
cp -r /opt/data/techtrend/AI-cost-monitoring/docs/{adr,qa,core,architecture} \
  /opt/data/ucx_framework/ai_project_flow/docs/
cp /opt/data/techtrend/AI-cost-monitoring/docs/*.md \
  /opt/data/ucx_framework/ai_project_flow/docs/
```

---

## GAP 11: Missing AWS/Azure Setup Scripts

**Severity**: HIGH (given "all three clouds" requirement)

**Issue**: Plan says "Full templates for GCP/AWS/Azure" but only GCP setup scripts exist.

**Current**:
```
scripts/project_setup/
├── setup_github_environments.sh
└── gcp/
    ├── setup-wif.sh
    ├── setup_artifact_registry.sh
    ├── setup-environments.sh
    ├── setup-projects.sh
    ├── setup-ai-review-gcp.sh
    └── configure_revision_retention.sh
```

**Missing for AWS**:
- setup-iam-role.sh (OIDC authentication)
- setup-ecr.sh (Container registry)
- setup-ecs.sh or setup-fargate.sh

**Missing for Azure**:
- setup-managed-identity.sh
- setup-acr.sh
- setup-container-apps.sh

**Resolution**:
1. Document that only GCP scripts exist currently
2. Add placeholder structure for AWS/Azure
3. Create basic AWS/Azure setup scripts during implementation

---

## GAP 12: Files Summary Table Incorrect

**Severity**: MEDIUM

**Plan States**:
| Category | Source Count | Framework Count |
|----------|--------------|-----------------|
| Workflows | 20 | 20 |
| Issue templates | 8 | 8 |
| Root templates | 8 | 8 |
| Scripts | 23 | ~15 |
| ADRs | 9 | 3 |
| QA docs | 8 | 8 |

**Corrected**:
| Category | Source Count | Framework Count | Notes |
|----------|--------------|-----------------|-------|
| Workflows | **22** | 20 | Exclude 2 disabled |
| Issue templates | **11** | 11 | All needed |
| Root templates | **12** | 12 | Add 4 deployment docs |
| Scripts | **33** | ~25 | Exclude some ghes-runner |
| ADRs | **10** | 3-5 | Sample + README |
| QA docs | **9** | 9 | All template |
| Core docs | **10** | 5-7 | Select essential specs |
| Component templates | **5** | 3-4 | README patterns |

---

## GAP 13: Verification Script Incomplete

**Severity**: LOW

**Plan Verification**:
```bash
grep -r "aiocto\|USDA\|techtrend\|AI-Cloud-Cost" \
  ai_project_flow/ --include="*.md" --include="*.yml"
```

**Missing Patterns**:
- `gcp-cost-guard` (component name)
- `github.techtrend.us` (GHES host)
- `vmyakota\|jvalenzano` (CODEOWNERS)
- `#31` (project board)
- `ai-cost-team` (team slug)
- Specific dates (2026-02-xx)

**Resolution**: Update verification:
```bash
grep -r "aiocto\|USDA\|techtrend\|AI-Cloud-Cost\|gcp-cost-guard\|github\.techtrend\.us\|vmyakota\|jvalenzano\|#31\|ai-cost-team" \
  ai_project_flow/ --include="*.md" --include="*.yml" --include="*.sh" --include="*.py" --include="*.json"
```

---

## GAP 14: Directory Structure Diagram Incomplete

**Severity**: LOW

**Missing from Structure**:
```
ai_project_flow/
├── ...
├── components/                    # MISSING - Component templates
│   ├── README.md
│   └── {component}/
│       ├── README.md
│       ├── CHANGELOG.md
│       └── ...
├── .claude/                       # MISSING - Claude config
│   └── settings.local.json.template
└── ...
```

---

## GAP 15: No Handling of Disabled Workflows

**Severity**: LOW

**Issue**: Plan doesn't address what to do with disabled workflows:
- `cleanup-pr-env.yml.disabled`
- `deploy-dev-pr.yml.disabled`

**Resolution Options**:
1. **Include as examples** - Rename to `.yml.example`
2. **Exclude entirely** - Don't copy disabled workflows
3. **Document only** - Reference in docs but don't include

**Recommendation**: Option 2 - Exclude disabled workflows from framework.

---

## Updated File Counts Summary

| Category | Plan | Actual | Framework |
|----------|------|--------|-----------|
| Governance docs | 37 | 37 | 23 |
| Workflows | 20 | 22 | 20 |
| Issue templates | 8 | 11 | 11 |
| GitHub config | 4 | 4 | 4 |
| Root templates | 8 | 12 | 12 |
| Scripts | 23 | 33 | ~25 |
| ADRs | 9 | 10 | 3-5 |
| QA docs | 8 | 9 | 9 |
| Core docs | 0 | 10 | 5-7 |
| Component templates | 0 | 5 | 3-4 |
| .claude config | 0 | 1 | 1 |
| **Total** | ~117 | **~144** | **~96** |

---

## Recommended Plan Updates

### 1. Update Component 2 (Workflows)
Change count from 20 to 22, note disabled workflows.

### 2. Update Component 3 (Issue Templates)
Fix template list:
- Add: cost_analysis.md, infra_task.md, mcp_server.md, security_report.md
- Remove: deployment_issue.md, qa_testing.md

### 3. Update Component 5 (Root Documentation)
Add 4 missing files: AWS-DEPLOYMENT.md, AZURE-DEPLOYMENT.md, GCP-DEPLOYMENT.md, docker-compose.test.yml

### 4. Add Component 8: Component Templates
New section for `components/` structure.

### 5. Add Component 9: Core Documentation
New section for `docs/core/` technical specs.

### 6. Update Component 6 (Scripts)
Change count from 23 to 33, clarify essential vs optional.

### 7. Update Execution Steps
- Step 4: Add 4 missing root files
- Step 6: Add docs/core/ and docs/architecture/
- Add new step for components/ structure

### 8. Add Placeholder Variables
Add 8 infrastructure configuration variables.

### 9. Update Verification Script
Add missing project-specific patterns.

### 10. Note AWS/Azure Script Gap
Document that AWS/Azure setup scripts need to be created.
