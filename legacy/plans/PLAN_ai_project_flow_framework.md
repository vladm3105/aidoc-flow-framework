# Plan: AI-First Project Governance Framework

## Objective
Create a complete, reusable project management framework for small AI-first projects based on the working implementation at `/opt/data/techtrend/AI-cost-monitoring`. The framework includes:
- Project governance documentation
- CI/CD pipelines (GitHub Actions)
- AI-powered code review
- Issue/PR templates
- Setup automation scripts

## Source & Target
- **Source**: `/opt/data/techtrend/AI-cost-monitoring` (keep intact)
- **Target**: `/opt/data/ucx_framework/ai_project_flow/`
- **Method**: Copy files from source, then genericize

## User Decisions
- **Framework location**: New folder `ai_project_flow/`
- **Source handling**: Copy files (keep source project intact)
- **Placeholder syntax**: Use `{VARIABLE_NAME}` format
- **Cloud strategy**: Full templates for ALL THREE clouds (GCP/AWS/Azure)
- **Phase structure**: Configurable with `{PHASE_COUNT}` (4-12 phases)
- **IPLAN examples**: Remove project-specific IPLANs, keep structure

---

## Framework Components

### Component 1: Governance Documentation (37 files)
**Source**: `governance/`
**Status**: Already copied to `project_governance/`

| Category | Files | Action |
|----------|-------|--------|
| Core Governance | 17 root files | Genericize placeholders |
| AI PR Review | 6 files | Genericize, multi-AI provider |
| IPLAN Structure | README only | Delete 11 project-specific IPLANs |
| CI/CD Config | 1 JSON | Replace with template |
| GHES Runner | 1 file | Keep as optional |

### Component 2: GitHub Workflows (22 files, 20 active)
**Source**: `.github/workflows/`
**Status**: NOT YET COPIED

| Category | Workflows | Framework Action |
|----------|-----------|------------------|
| **CI Pipeline** | ci.yml | Template (reusable pattern) |
| **AI Review** | ai-review.yml | Template (reusable workflow) |
| **Release** | release.yml | Template (generic) |
| **Deployment** | deploy-dev.yml, deploy-staging.yml, deploy-prod.yml | Full templates for GCP/AWS/Azure |
| **Issue Automation** | auto-add-to-project.yml, phase-transition.yml | Template with placeholders |
| **QA Pipeline** | execute-qa-testing.yml, create-qa-testing-issue.yml | Template |
| **Monitoring** | check-phase-completion.yml, check-all-phases-dev.yml | Template |
| **Utilities** | pr-merge-cleanup.yml, issue-label-sync.yml, rollback-prod.yml | Template |
| **Agent Dispatch** | agent-dispatch.yml | Template |
| **Bug/Deploy Issues** | create-bug-issue.yml, create-deployment-issue.yml | Template |

**Disabled Workflows (Excluded from Framework)**:
- `cleanup-pr-env.yml.disabled`
- `deploy-dev-pr.yml.disabled`

### Component 3: Issue Templates (11 files)
**Source**: `.github/ISSUE_TEMPLATE/`
**Status**: NOT YET COPIED

| Template | Purpose | Framework Action |
|----------|---------|------------------|
| architecture_proposal.md | ADR proposals | Template |
| bug_report.md | Bug reports | Template (generic) |
| config.yml | Template registry | Template |
| cost_analysis.md | Cost analysis tasks | Template |
| development_issue.md | 4-stage QA workflow | Template |
| feature_request.md | Feature requests | Template (generic) |
| infra_task.md | Infrastructure tasks | Template |
| mcp_server.md | MCP server issues | Template |
| research_task.md | Research items | Template |
| security_report.md | Security reports | Template |

**Note**: `deployment_issue.md` and `qa_testing.md` are created dynamically by workflows, not templates.

### Component 4: GitHub Config Files
**Source**: `.github/`
**Status**: NOT YET COPIED

| File | Purpose | Framework Action |
|------|---------|------------------|
| CODEOWNERS | Auto-assign reviewers | Template with placeholders |
| labeler.yml | PR auto-labeling | Template |
| dependabot.yml | Dependency updates | Template |
| PULL_REQUEST_TEMPLATE.md | PR checklist | Template |

### Component 5: Root Documentation (12 files)
**Source**: Project root
**Status**: NOT YET COPIED

| File | Size | Framework Action |
|------|------|------------------|
| README.md | 14.7KB | Template |
| README_AIAGENT.md | 14.7KB | Template (AI agent rules) |
| CLAUDE.md | 9.6KB | Template (Claude config) - **See extracted rules section** |
| DEVELOPER_GUIDE.md | 9.6KB | Template |
| CONTRIBUTING.md | 9.3KB | Template |
| HANDOFF.md | 6.8KB | Template |
| AWS-DEPLOYMENT.md | 7.3KB | Template (AWS guide) |
| AZURE-DEPLOYMENT.md | 8.8KB | Template (Azure guide) |
| GCP-DEPLOYMENT.md | 11KB | Template (GCP guide) |
| docker-compose.test.yml | 1.5KB | Template (local test env) |
| .mcp.json | 1KB | Template (MCP servers) |
| .env.example | 5.7KB | Template |

### Component 6: Setup Scripts (33 files)
**Source**: `scripts/`
**Status**: NOT YET COPIED

| Category | Count | Scripts | Framework Action |
|----------|-------|---------|------------------|
| project_setup/ | 7 | setup_github_environments.sh, gcp/*.sh (6) | Full templates for GCP |
| workflows/ | 16 | Python helpers + smoke_test.sh | Template |
| ghes-runner/ | 10 | Docker setup, config, runner scripts | Optional (GHES only) |

**Essential Scripts (23)**: project_setup/* + workflows/*
**Optional Scripts (10)**: ghes-runner/* (GHES-specific)

**Note**: Only GCP setup scripts exist. AWS/Azure scripts need to be created during implementation.

### Component 7: Architecture Docs (70 files total, ~30 for framework)
**Source**: `docs/`
**Status**: NOT YET COPIED

| Category | Count | Framework Action |
|----------|-------|------------------|
| docs/adr/ | 10 | Template (3-5 examples + README) |
| docs/qa/ | 9 | Template (all) |
| docs/core/ | 10 | Template (5-7 essential specs) |
| docs/architecture/ | 1 | Template (README) |
| docs/ (root) | 7 | Template (key docs like PROJECT_DEFINITION.md) |
| docs/UX/ | 2 | Exclude (project-specific) |
| docs/UX/legacy/ | 21 | Exclude (project-specific iterations) |
| docs/core/legacy/ | 10 | Exclude (project-specific iterations) |

**Key Root Docs to Include**:
- `PROJECT_DEFINITION.md` (30KB) - Project definition template
- `github-collaboration.md` - GitHub workflow guide
- `documentation-best-practices.md` - Doc standards
- `GCP-COST-GUARD.md`, `AWS-COST-GUARD.md`, `AZURE-COST-GUARD.md` - Cloud cost guides
- `MINIMAL-COST-GUARD.md` - Minimal setup guide

### Component 8: Component Templates (NEW)
**Source**: `components/`
**Status**: NOT YET COPIED

| Item | Purpose | Framework Action |
|------|---------|------------------|
| components/README.md | Component overview | Template |
| components/agents/README.md | Agents component | Template |
| components/frontend/README.md | Frontend component | Template |
| components/infrastructure/README.md | Infrastructure component | Template |

**Framework Component Template Structure**:
```
components/
├── README.md                  # Component overview template
└── {component-name}/
    ├── README.md             # Component README template
    ├── CHANGELOG.md          # Changelog template
    ├── src/                  # Source structure
    └── tests/                # Test structure
```

### Component 9: Claude Configuration (NEW)
**Source**: `.claude/`
**Status**: NOT YET COPIED

| File | Size | Framework Action |
|------|------|------------------|
| settings.local.json | 12KB | Template with placeholders |

**Contents**: Claude Code project-specific settings including MCP server configurations, project rules, session settings.

---

## Framework Directory Structure

```
ai_project_flow/
├── README.md                        # Framework overview & quick start
├── CONFIG.md                        # All placeholder variables
├── SETUP_GUIDE.md                   # Step-by-step customization
│
├── governance/                      # Project governance docs
│   ├── [17 root governance files]
│   ├── AI_PR_Review/               # AI review documentation
│   ├── plans/                      # IPLAN structure (README only)
│   ├── cicd/                       # CI/CD config templates
│   └── ghes_runner/                # Optional GHES guide
│
├── .github/                         # GitHub automation
│   ├── workflows/                  # 20 workflow templates (active only)
│   │   ├── ci.yml
│   │   ├── ai-review.yml
│   │   ├── deploy-{env}.yml
│   │   ├── agent-dispatch.yml
│   │   └── ...
│   ├── ISSUE_TEMPLATE/             # 11 issue templates
│   ├── CODEOWNERS
│   ├── labeler.yml
│   ├── dependabot.yml
│   └── PULL_REQUEST_TEMPLATE.md
│
├── templates/                       # Root doc templates
│   ├── README.md
│   ├── README_AIAGENT.md
│   ├── CLAUDE.md
│   ├── DEVELOPER_GUIDE.md
│   ├── CONTRIBUTING.md
│   ├── HANDOFF.md
│   ├── AWS-DEPLOYMENT.md           # NEW
│   ├── AZURE-DEPLOYMENT.md         # NEW
│   ├── GCP-DEPLOYMENT.md           # NEW
│   ├── docker-compose.test.yml     # NEW
│   ├── .mcp.json
│   └── .env.example
│
├── scripts/                         # Setup automation
│   ├── project_setup/
│   │   ├── setup_github.sh
│   │   └── cloud/
│   │       ├── gcp/               # 6 existing scripts
│   │       ├── aws/               # Placeholder - to be created
│   │       └── azure/             # Placeholder - to be created
│   ├── workflows/                  # CI/CD helper scripts (16)
│   └── ghes-runner/                # Optional GHES runner (10)
│
├── components/                      # Component templates (NEW)
│   ├── README.md
│   └── {component}/
│       ├── README.md
│       ├── CHANGELOG.md
│       └── ...
│
├── .claude/                         # Claude configuration (NEW)
│   └── settings.local.json.template
│
└── docs/                            # Technical documentation
    ├── adr/                        # ADR templates (10 files)
    ├── qa/                         # QA documentation (9 files)
    ├── core/                       # Technical specs (NEW - 10 files)
    ├── architecture/               # Architecture docs (NEW - 1 file)
    └── *.md                        # Root docs (7 files)
```

---

## Placeholder Variables (47 total)

### Required - Core
| Variable | Description | Example |
|----------|-------------|---------|
| `{PROJECT_PREFIX}` | Short identifier | `myproj` |
| `{PROJECT_NAME}` | Full name | `My Project` |
| `{REPO_NAME}` | Repository name | `my-project` |
| `{GITHUB_ORG}` | Organization | `my-org` |
| `{GITHUB_HOST}` | GitHub hostname | `github.com` |
| `{PROJECT_BOARD_NUMBER}` | Board number | `1` |

### Required - Team
| Variable | Description | Example |
|----------|-------------|---------|
| `{CODEOWNER_1}` | Primary reviewer | `@username1` |
| `{CODEOWNER_2}` | Secondary reviewer | `@username2` |
| `{TEAM_SLUG}` | Team identifier | `dev-team` |

### Required - AI Agent Configuration (NEW)
| Variable | Description | Example |
|----------|-------------|---------|
| `{TIMEZONE}` | Project timezone | `America/New_York` |
| `{AI_TOOL_NAME}` | AI tool for co-author | `Claude` |
| `{AI_TOOL_EMAIL}` | AI tool email | `noreply@anthropic.com` |
| `{COMMUNICATION_TOOL}` | Primary comms tool | `Teams` or `Slack` |
| `{BOARD_OPTION_IN_PROGRESS}` | Board "In Progress" option ID | `47fc9ee4` |
| `{BOARD_OPTION_IN_REVIEW}` | Board "In Review" option ID | `de81af01` |
| `{BOARD_OPTION_DONE}` | Board "Done" option ID | `98236657` |
| `{BOARD_STATUS_FIELD_ID}` | Board Status field ID | `PVTSSF_...` |
| `{BOARD_PROJECT_ID}` | Board Project node ID | `PVT_...` |

### Required - Cloud (select one or more)

**GCP:**
| Variable | Description | Example |
|----------|-------------|---------|
| `{GCP_PROJECT_DEV}` | Dev project | `myproj-dev` |
| `{GCP_PROJECT_STAGING}` | Staging project | `myproj-staging` |
| `{GCP_PROJECT_PROD}` | Prod project | `myproj-prod` |
| `{GCP_REGION}` | GCP region | `us-east4` |
| `{WIF_POOL_NAME}` | WIF pool | `github-actions-pool` |
| `{WIF_PROVIDER_NAME}` | WIF provider | `github-provider` |
| `{GCP_ARTIFACT_REGISTRY}` | Registry path | `us-east4-docker.pkg.dev` |

**AWS:**
| Variable | Description | Example |
|----------|-------------|---------|
| `{AWS_ACCOUNT_ID}` | AWS account | `123456789012` |
| `{AWS_REGION}` | AWS region | `us-east-1` |
| `{AWS_ROLE_ARN}` | IAM role ARN | `arn:aws:iam::123456789012:role/github-actions` |
| `{ECR_REGISTRY}` | ECR registry | `123456789012.dkr.ecr.us-east-1.amazonaws.com` |

**Azure:**
| Variable | Description | Example |
|----------|-------------|---------|
| `{AZURE_SUBSCRIPTION_ID}` | Subscription | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `{AZURE_TENANT_ID}` | Tenant ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `{AZURE_CLIENT_ID}` | App client ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `{ACR_REGISTRY}` | ACR registry | `myregistry.azurecr.io` |
| `{AZURE_RESOURCE_GROUP}` | Resource group | `myproj-rg` |

### Required - Infrastructure (NEW)
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

### Optional - Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `{PHASE_COUNT}` | Number of phases | `8` |
| `{COVERAGE_THRESHOLD}` | Test coverage % | `80` |
| `{AI_REVIEW_MODEL}` | Claude model | `sonnet` |
| `{AI_REVIEW_BUDGET}` | Max cost/review | `1` |
| `{DEPLOY_WINDOW_START}` | Deploy start hour | `10` |
| `{DEPLOY_WINDOW_END}` | Deploy end hour | `16` |
| `{ERROR_RATE_THRESHOLD}` | Rollback threshold | `1` |
| `{NOTIFICATION_WEBHOOK}` | Teams/Slack URL | (optional) |

---

## Implementation Plan

### Phase 1: Create Framework Structure
1. Create `/opt/data/ucx_framework/ai_project_flow/`
2. Move existing `project_governance/` → `ai_project_flow/governance/`
3. Create directory structure for `.github/`, `templates/`, `scripts/`, `docs/`, `components/`, `.claude/`

### Phase 2: Copy & Organize Source Files
1. Copy `.github/workflows/` (20 active files, exclude disabled)
2. Copy `.github/ISSUE_TEMPLATE/` (11 files)
3. Copy `.github/` config files (CODEOWNERS, labeler.yml, etc.)
4. Copy root templates (12 files including deployment docs)
5. Copy `scripts/` (selective - setup and helper scripts)
6. Copy `docs/` (adr, qa, core, architecture, root docs)
7. Copy `components/` structure (README templates)
8. Copy `.claude/` configuration

### Phase 3: Genericize Governance (Already Planned)
Apply gap analysis updates:
- Delete 14 project-specific files (11 IPLANs + 2 deprecated + 1 JSON)
- Replace ~1200 project-specific references
- Add 47 placeholder variables
- Keep standard labels and secret names

### Phase 4: Genericize Workflows
For each workflow:
1. Replace hardcoded org/repo/project references
2. Replace GCP-specific values with placeholders
3. Add cloud provider conditionals (GCP/AWS/Azure)
4. Document required secrets

### Phase 5: Genericize Templates
1. Issue templates - replace project references
2. PR template - make generic
3. Root docs - replace all project-specific content
4. MCP config - create template with placeholder servers

### Phase 6: Genericize Scripts
1. Setup scripts - parameterize cloud/org values
2. Workflow helpers - make cloud-agnostic where possible
3. Document which scripts are optional
4. Create placeholder AWS/Azure setup scripts

### Phase 7: Create Framework Documentation
1. `README.md` - Framework overview, quick start
2. `CONFIG.md` - All 47 placeholders with examples
3. `SETUP_GUIDE.md` - Step-by-step customization
4. `CLOUD_GUIDE.md` - GCP vs AWS vs Azure guidance

### Phase 8: Verification
```bash
# Check for remaining project-specific strings
grep -r "aiocto\|USDA\|techtrend\|AI-Cloud-Cost\|gcp-cost-guard\|github\.techtrend\.us\|vmyakota\|jvalenzano\|#31\|ai-cost-team" \
  ai_project_flow/ --include="*.md" --include="*.yml" --include="*.sh" --include="*.py" --include="*.json"

# Validate placeholder consistency
grep -roh '{[A-Z_]*}' ai_project_flow/ | sort -u

# Check workflow syntax
for f in ai_project_flow/.github/workflows/*.yml; do
  yamllint "$f"
done

# Check for broken internal links
find ai_project_flow/ -name "*.md" -exec grep -l '\[.*\](\.\/' {} \; | \
  xargs -I {} sh -c 'echo "Checking {}"; grep -oh "\[.*\](\./[^)]*)" {}'
```

---

## Files Summary

| Category | Source Count | Framework Count | Notes |
|----------|--------------|-----------------|-------|
| Governance docs | 37 | 23 | Remove 14 project-specific |
| Workflows | **22** | 20 | Exclude 2 disabled |
| Issue templates | **11** | 11 | All needed |
| GitHub config | 4 | 4 | All templated |
| Root templates | **12** | 12 | Add 4 deployment docs |
| Scripts | **33** | ~25 | Exclude some ghes-runner |
| ADRs | **10** | 3-5 | Sample + README |
| QA docs | **9** | 9 | All template |
| Core docs | **10** | 5-7 | Select essential specs |
| Component templates | **5** | 3-4 | README patterns |
| .claude config | **1** | 1 | Template |
| **Total** | **~154** | **~96** | Reduced + templated |

---

## Execution Order

**Step 1: Create Structure**
```bash
mkdir -p /opt/data/ucx_framework/ai_project_flow/{governance,.github,templates,scripts,docs,components,.claude}
mkdir -p /opt/data/ucx_framework/ai_project_flow/scripts/project_setup/cloud/{gcp,aws,azure}
mkdir -p /opt/data/ucx_framework/ai_project_flow/docs/{adr,qa,core,architecture}
```

**Step 2: Copy Governance** (from already-copied folder)
```bash
cp -r /opt/data/ucx_framework/project_governance/* \
  /opt/data/ucx_framework/ai_project_flow/governance/
```

**Step 3: Copy GitHub Config** (from source)
```bash
cp -r /opt/data/techtrend/AI-cost-monitoring/.github/* \
  /opt/data/ucx_framework/ai_project_flow/.github/
# Remove disabled workflows
rm -f /opt/data/ucx_framework/ai_project_flow/.github/workflows/*.disabled
```

**Step 4: Copy Root Templates** (from source - 12 files)
```bash
cp /opt/data/techtrend/AI-cost-monitoring/{README.md,README_AIAGENT.md,CLAUDE.md,DEVELOPER_GUIDE.md,CONTRIBUTING.md,HANDOFF.md,AWS-DEPLOYMENT.md,AZURE-DEPLOYMENT.md,GCP-DEPLOYMENT.md,docker-compose.test.yml,.mcp.json,.env.example} \
  /opt/data/ucx_framework/ai_project_flow/templates/
```

**Step 5: Copy Scripts** (from source)
```bash
cp -r /opt/data/techtrend/AI-cost-monitoring/scripts/{project_setup,workflows} \
  /opt/data/ucx_framework/ai_project_flow/scripts/
```

**Step 6: Copy Docs** (from source - expanded)
```bash
cp -r /opt/data/techtrend/AI-cost-monitoring/docs/{adr,qa,core,architecture} \
  /opt/data/ucx_framework/ai_project_flow/docs/
cp /opt/data/techtrend/AI-cost-monitoring/docs/*.md \
  /opt/data/ucx_framework/ai_project_flow/docs/
# Exclude legacy folders
rm -rf /opt/data/ucx_framework/ai_project_flow/docs/core/legacy
```

**Step 7: Copy Components** (from source)
```bash
cp /opt/data/techtrend/AI-cost-monitoring/components/README.md \
  /opt/data/ucx_framework/ai_project_flow/components/
cp /opt/data/techtrend/AI-cost-monitoring/components/*/README.md \
  /opt/data/ucx_framework/ai_project_flow/components/ 2>/dev/null || true
```

**Step 8: Copy Claude Config** (from source)
```bash
cp /opt/data/techtrend/AI-cost-monitoring/.claude/settings.local.json \
  /opt/data/ucx_framework/ai_project_flow/.claude/settings.local.json.template
```

**Step 9: Delete Project-Specific Files**
- 11 IPLAN files
- 2 deprecated files (GITHUB_PROJECT_SETUP.md, AI_PR_Review/GCP_SETUP.md)
- 1 config file (cicd/phase-deployments.json)

**Step 10: Genericize All Files**
- Replace ~1200+ project-specific references
- Add cloud provider variants (AWS/Azure workflows)
- Update placeholder variables
- Create placeholder AWS/Azure setup scripts

**Step 11: Create Framework Documentation**
- README.md (overview, quick start)
- CONFIG.md (all 47 placeholder variables)
- SETUP_GUIDE.md (customization steps)
- CLOUD_GUIDE.md (GCP/AWS/Azure specifics)

**Step 12: Verification Pass**
- Search for remaining project-specific strings (expanded pattern list)
- Validate placeholder consistency
- Test YAML syntax
- Check for broken internal links

---

## CLAUDE.md Template Structure (Extracted Rules)

The CLAUDE.md template contains reusable AI agent operational rules extracted from the source project. These patterns are framework-worthy and should be genericized with placeholders.

### Section 1: Session Start Protocol
```markdown
Before starting any implementation or governance work, read these files in order:
1. `README_AIAGENT.md` — Universal AI agent rules
2. `governance/GOVERNANCE_RULES.md` — Operational rules
3. `governance/PROJECT_PLAN.md` §2 — Current state
4. `governance/plans/README.md` — Active IPLANs

Do NOT invent process rules. If uncertain, consult governance docs.
```

### Section 2: AI Operating Rules

**Never Do (Generic Framework Rules)**:
| Rule | Rationale |
|------|-----------|
| Use service account JSON keys | Use Workload Identity Federation |
| Force-push to `main` | All changes via PR |
| Commit directly to `main` | Branch + PR workflow |
| Invent naming conventions | Check GOVERNANCE_RULES.md |
| Use non-existent labels | Check label taxonomy first |
| Use marketplace actions (GHES) | Inline shell for reliability |

**Always Do (Generic Framework Rules)**:
| Rule | Template |
|------|----------|
| Use consistent timezone | `{TIMEZONE}` for schedules |
| Include AI co-author | `Co-Authored-By: {AI_TOOL_NAME} <{AI_TOOL_EMAIL}>` |
| Assign PR reviewers | Reference CODEOWNERS roster |
| Follow label lifecycle | `ai:ready` → `ai:in-progress` → `ai:review-requested` |
| Update board with labels | Sync label + board status |
| Cross-post review summaries | Audit trail on linked issues |

### Section 3: Issue Processing Workflow (4-Phase)

**Framework Pattern** (genericized):
```
Phase 1: Issue Analysis
  ├─ Read issue body, acceptance criteria, comments
  ├─ Read linked/dependent issues
  ├─ Read related governance docs, ADRs, specs
  └─ Review existing code to be modified

Phase 2: Create Implementation Plan
  ├─ Create: governance/plans/IPLAN-NNN_{slug}.md
  ├─ Document: scope, steps, acceptance criteria mapping
  └─ Include: risks, edge cases, testing approach

Phase 3: Review & Refine Plan
  ├─ Re-read plan as if seeing it first time
  ├─ Identify gaps: missing steps, unclear actions
  ├─ Verify: every acceptance criterion has mapped step
  └─ Update plan with improvements

Phase 4: Transition to Implementation
  └─ Execute Pre-Implementation Checklist
```

### Section 4: Pre-Implementation Checklist

**Framework Pattern** (with placeholders):
```markdown
1. **Change label**: `ai:ready` → `ai:in-progress`
2. **Update board status** → In Progress (option ID `{BOARD_OPTION_IN_PROGRESS}`)
3. **Create branch**: `ai/{issue}-{slug}` from `main`

Never start implementation while issue is labeled `ai:ready`.
```

### Section 5: Post-PR Checklist

**Framework Pattern** (with placeholders):
```markdown
1. **Verify** each acceptance criterion (read files, run tests)
2. **Check off** verified criteria in issue body (`- [ ]` → `- [x]`)
3. **Change label**: `ai:in-progress` → `ai:review-requested`
4. **Update board status** → In Review (option ID `{BOARD_OPTION_IN_REVIEW}`)
5. **Post PR link** as comment on linked issue
```

### Section 6: Naming Conventions Template

| Type | Pattern | Example |
|------|---------|---------|
| Repos | `{PROJECT_PREFIX}-{component}` | `myproj-api` |
| AI Branches | `ai/{issue}-{slug}` | `ai/42-add-auth` |
| Feature Branches | `feature/{name}` | `feature/user-login` |
| Bugfix Branches | `bugfix/{name}` | `bugfix/null-check` |
| Issues | `[P{phase}-{task_id}] {title}` | `[P1-003] Add OAuth` |
| Cloud Resources | `{PROJECT_PREFIX}-{env}-{resource}` | `myproj-dev-api` |
| Plans | `IPLAN-NNN_{slug}.md` | `IPLAN-001_setup.md` |

### Section 7: Tool Strategy (MCP vs CLI)

| Operation | Use MCP | Use gh CLI |
|:----------|:-------:|:----------:|
| Issue CRUD | ✅ | |
| PR CRUD | ✅ | |
| Create branch | ✅ | |
| Push files (multi-file) | ✅ | |
| Projects V2 board status | | ✅ |
| Labels CRUD | | ✅ |
| GraphQL mutations | | ✅ |

### Section 8: MCP Server Policy Template

```markdown
**Allowed MCP Servers** (customize per project):

| Server | Purpose |
|--------|---------|
| `github-{PREFIX}` | GitHub ({GITHUB_HOST}) |
| `git` | Git operations |
| `filesystem` | Project file access |
| `memory` | Session persistence |
| `sequential-thinking` | Complex reasoning |
| `fetch` | HTTP requests |
| `context7` | Documentation lookup |
| `playwright` | Browser automation |
```

---

## AWS/Azure Script Gap

**Current State**: Only GCP setup scripts exist in the source project.

**Missing for AWS**:
- `setup-iam-role.sh` (OIDC authentication)
- `setup-ecr.sh` (Container registry)
- `setup-ecs.sh` or `setup-fargate.sh` (Container service)

**Missing for Azure**:
- `setup-managed-identity.sh` (OIDC authentication)
- `setup-acr.sh` (Container registry)
- `setup-container-apps.sh` (Container service)

**Resolution**:
1. Document that only GCP scripts exist currently in CLOUD_GUIDE.md
2. Add placeholder directory structure for AWS/Azure
3. Create basic AWS/Azure setup scripts during implementation (or document as TODO)

---

## Relationship to SDD Methodology

This framework is a **lightweight alternative** to the full SDD methodology (`ai_dev_flow/`):

| Aspect | SDD (ai_dev_flow) | This Framework |
|--------|-------------------|----------------|
| Scope | Large projects | Small-medium projects |
| Layers | 12 formal layers | Agile phases/sprints |
| Docs | BRD→PRD→REQ→SPEC→TASKS | PROJECT_PLAN + IPLANs |
| Traceability | Full requirement tracing | Issue-based tracking |
| Timeline | Months-years | 1-6 months |
| Team | Multiple roles | Solo/small team + AI |
