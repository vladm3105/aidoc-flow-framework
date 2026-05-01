# Plan: Make project_governance Framework Project-Agnostic

## Objective
Transform the `/opt/data/ucx_framework/project_governance` folder from a project-specific implementation to a reusable framework template for AI-first small projects.

## User Decisions
- **IPLAN files**: Remove all IPLAN files (keep only `plans/README.md` structure)
- **Placeholder syntax**: Use `{VARIABLE_NAME}` format (simple braces)
- **Cloud strategy**: Multi-cloud templates (parallel sections for GCP/AWS/Azure)
- **Phase structure**: Configurable with `{PHASE_COUNT}` placeholder (allow 4-12 phases)

## Gap Analysis Applied
- **Date**: 2026-02-16
- **Gaps identified**: 12 (all addressed in this revision)
- **Reference**: `GAP_ANALYSIS_project_governance.md`

---

## Current State Analysis

### Project-Specific References Found (Must Replace)

**Core Identifiers:**
| Type | Current Value | Generic Placeholder |
|------|---------------|---------------------|
| Project Prefix | `aiocto` | `{PROJECT_PREFIX}` |
| Full Project Name | `AI Ops Monitoring - Cost Module` | `{PROJECT_NAME}` |
| Repository Name | `AI-Cloud-Cost-Monitoring` | `{REPO_NAME}` |
| Organization | `USDA-AI-Innovation-Hub` | `{GITHUB_ORG}` |
| GH Enterprise Host | `github.techtrend.us` | `{GITHUB_HOST}` |
| Project Board | `#31` | `{PROJECT_BOARD_NUMBER}` |
| Local Paths | `/opt/data/techtrend/AI-cost-monitoring` | `{PROJECT_ROOT}` |

**Cloud Infrastructure:**
| Type | Current Value | Generic Placeholder |
|------|---------------|---------------------|
| GCP Dev Project | `aiocto-dev` | `{GCP_PROJECT_DEV}` |
| GCP Staging Project | `aiocto-staging` | `{GCP_PROJECT_STAGING}` |
| GCP Prod Project | `aiocto-prod` | `{GCP_PROJECT_PROD}` |
| WIF Pool Name | `github-actions-pool` | `{WIF_POOL_NAME}` |
| WIF Provider Name | `ghes-provider` | `{WIF_PROVIDER_NAME}` |
| Cloud Run URL | `aiocto-cost-guard-staging.run.app` | `{CLOUD_RUN_URL}` |
| Artifact Registry | `us-east4-docker.pkg.dev/{PROJECT}` | `{ARTIFACT_REGISTRY}` |
| Service Accounts | `aiocto-ai-reviewer@...` | `{SA_PREFIX}-{ROLE}@{GCP_PROJECT}` |

**Component & Timeline:**
| Type | Current Value | Generic Placeholder |
|------|---------------|---------------------|
| Component Names | `gcp-cost-guard`, `mcp-servers` | `{COMPONENT_NAME}` (examples) |
| Sprint Dates | `Feb 17, 2026` - `Jul 18, 2026` | Relative: `Week 1` - `Week 20` |
| Issue Numbers | `#11-#18`, `#19-#32`, etc. | Remove or use `#N` |

**Reference Count**: ~1200 total substitutions across 644 lines

### Files to Process (by Priority)

**HIGH PRIORITY (Core Governance):**
1. `GOVERNANCE_RULES.md` - 36KB, heavily project-specific
2. `PROJECT_PLAN.md` - 46KB, contains full roadmap/timeline
3. `GITHUB_PROJECT_SETUP_AI_FIRST.md` - 51KB, setup instructions
4. `GITHUB_WORKFLOWS.md` - 36KB, workflow definitions
5. `HOME_REPO.md` - 15KB, directory structure
6. `ROLES_AND_TOOLS.md` - 23KB, team/tool config

**MEDIUM PRIORITY (Operational):**
7. `ROADMAP.md` - 21KB, phase timeline
8. `GITHUB_TOOLS_SETUP.md` - 32KB, MCP/CLI setup
9. `AI_ISSUE_LIFECYCLE.md` - 58KB, issue management
10. `AI_TIME_ESTIMATION.md` - 18KB, estimation guide

**LOW PRIORITY (Standard Patterns):**
11. `DEFINITION_OF_DONE.md` - 8KB, mostly generic
12. `BRANCHING_STRATEGY.md` - 2KB, 95% generic
13. `RELEASE_PROCESS.md` - 3KB, mostly generic
14. `REPOSITORY_STRATEGY.md` - 8KB, monorepo patterns
15. `REPO_STRUCTURE_DECISION_MATRIX.md` - 3KB
16. `PROJECT_KICKOFF_PLAN.md` - 7KB

**SUBDIRECTORIES:**
17. `plans/` - 11 IPLAN files (to be deleted), 1 README (to be updated)
18. `AI_PR_Review/` - 6 files (2 deprecated for deletion, 4 to modify)
19. `ghes_runner/` - 1 file (runner config)
20. `cicd/` - 1 JSON file (to be deleted and replaced with template)

**DEPRECATED FILES (to be deleted):**
21. `GITHUB_PROJECT_SETUP.md` - Deprecated, redirects to AI_FIRST version
22. `AI_PR_Review/GCP_SETUP.md` - Deprecated per IPLAN-006

---

## Implementation Plan

### Phase 1: Create Configuration Template
Create a `CONFIG_TEMPLATE.md` at the root with all placeholder variables:

```markdown
# Project Configuration Variables
Replace these placeholders throughout all governance documents:

## Required Variables
| Variable | Description | Example |
|----------|-------------|---------|
| {PROJECT_PREFIX} | Short project identifier | `myproj` |
| {PROJECT_NAME} | Full project name | `My Project Name` |
| {REPO_NAME} | GitHub repository name | `my-project-repo` |
| {GITHUB_ORG} | GitHub organization | `my-org` |
| {GITHUB_HOST} | GitHub hostname | `github.com` or `github.enterprise.com` |

## Optional Variables (Cloud)
| Variable | Description | Example |
|----------|-------------|---------|
| {GCP_PROJECT_DEV} | GCP dev project | `myproj-dev` |
| {GCP_PROJECT_STAGING} | GCP staging project | `myproj-staging` |
| {GCP_PROJECT_PROD} | GCP prod project | `myproj-prod` |
| {AWS_ACCOUNT_ID} | AWS account | `123456789012` |
| {AZURE_SUBSCRIPTION} | Azure subscription | `sub-id` |
```

### Phase 2: Process Core Governance Files

**2.1 GOVERNANCE_RULES.md**
- Replace all 200+ org/repo references
- Convert project-specific rules to generic patterns
- Add "Customization" section explaining placeholders

**2.2 PROJECT_PLAN.md**
- Remove specific sprint dates (Feb-Jul 2026)
- Convert to template with relative timeline (Week 1-20)
- Replace component names with `{COMPONENT_N}` patterns
- Keep structure as reference for planning methodology

**2.3 GITHUB_PROJECT_SETUP_AI_FIRST.md**
- Replace org/repo/host references
- Convert milestone dates to relative (`Week N`)
- Keep label taxonomy (reusable as-is)
- Add configuration section at top

**2.4 GITHUB_WORKFLOWS.md**
- Replace all GCP/infrastructure references
- Convert Docker registry paths to placeholders
- Keep workflow patterns (reusable structure)

**2.5 HOME_REPO.md**
- Replace directory structure with generic template
- Keep concept of monorepo organization
- Add "Adapt to Your Project" guidance

**2.6 ROLES_AND_TOOLS.md**
- Remove project-specific MCP server names
- Keep role definitions and tool selection matrix
- Add configuration examples

### Phase 3: Process Operational Files

**3.1 ROADMAP.md**
- Convert to template roadmap structure
- Replace dates with relative references
- Keep phase methodology (valuable pattern)

**3.2 GITHUB_TOOLS_SETUP.md**
- Replace MCP server naming convention
- Keep tool setup instructions (reusable)
- Add multi-platform support notes

**3.3 AI_ISSUE_LIFECYCLE.md**
- Replace IPLAN references with generic patterns
- Keep lifecycle model (excellent reference)
- Add "Adapt Labels" section

**3.4 AI_TIME_ESTIMATION.md**
- Already mostly generic
- Minor placeholder updates

### Phase 4: Process Standard Patterns

**4.1 DEFINITION_OF_DONE.md**
- Keep as-is (80% generic)
- Add note about phase-gated deployment being optional

**4.2 BRANCHING_STRATEGY.md**
- Already 95% generic
- Add note about `ai/` branch pattern being optional

**4.3 RELEASE_PROCESS.md**
- Replace GCP-specific deployment details
- Keep SemVer and CHANGELOG patterns
- Add multi-cloud deployment notes

**4.4 REPOSITORY_STRATEGY.md**
- Replace component structure with template
- Keep monorepo rationale (valuable)

### Phase 5: Process Subdirectories

**5.1 plans/**
- **Delete all IPLAN-001 through IPLAN-011 files**
- Keep and update `README.md` (IPLAN structure reference)
- Remove Plan Index table (project-specific)
- Keep naming convention, lifecycle, and structure sections

**5.2 AI_PR_Review/**
- **Delete GCP_SETUP.md** (deprecated - Vertex AI no longer used)
- Replace Anthropic-specific references with generic AI provider
- Keep workflow patterns (reusable)
- Update LOCAL_SETUP.md for multiple AI providers
- Update ONBOARDING.md (heavy project-specific references)
- Remove/update references to deleted GCP_SETUP.md
- Add section for alternative AI providers (OpenAI, Gemini, etc.)

**5.3 ghes_runner/**
- Keep as optional GHES-specific guidance
- Add note about SaaS GitHub alternative

**5.4 cicd/**
- Delete `phase-deployments.json` (project-specific)
- Add template `phase-deployments-template.json` with placeholders

### Phase 6: Add Multi-Cloud Templates

**6.1 Create cloud-specific sections in key files:**

For `GITHUB_WORKFLOWS.md`, `RELEASE_PROCESS.md`, and infrastructure docs:

```markdown
## Cloud Provider Configuration

### GCP (Google Cloud Platform)
- Cloud Run for containers
- Workload Identity Federation for auth
- Artifact Registry for images
- Cloud Build for CI/CD

### AWS (Amazon Web Services)
- ECS/Fargate for containers
- IAM Roles for auth
- ECR for images
- CodeBuild/CodePipeline for CI/CD

### Azure
- Container Apps for containers
- Managed Identity for auth
- ACR for images
- Azure DevOps for CI/CD
```

**6.2 Create `CLOUD_PROVIDER_MATRIX.md`:**
- Mapping of generic concepts to cloud-specific services
- Authentication patterns per cloud
- Deployment workflow templates per cloud

### Phase 7: Create Framework Index

Create `README.md` at `project_governance/` root:

```markdown
# AI-First Project Governance Framework

Lightweight governance framework for small AI-driven projects.

## Quick Start
1. Copy this folder to your project
2. Edit CONFIG_TEMPLATE.md with your values
3. Run find-and-replace for all placeholders
4. Remove example files you don't need

## Structure
- Core governance rules
- GitHub project setup (AI-first workflow)
- Phase-based development with sprints
- AI PR review integration
- Definition of Done criteria

## When to Use
- Small to medium projects (1-6 month timeline)
- AI-first development approach
- GitHub-based collaboration
- Phase-gated deployment model

## Relationship to SDD Methodology

This framework is a **lightweight alternative** to the full SDD methodology
(`ai_dev_flow/`). Use this for:
- Small projects (1-6 months)
- Teams familiar with agile/sprint workflow
- Projects not requiring comprehensive documentation

For larger projects requiring formal requirements traceability (BRD → PRD → REQ →
SPEC → TASKS layered approach), use the full SDD methodology instead.
```

---

## Files to Modify (18 total)

**HIGH PRIORITY:**
| File | Changes | Complexity |
|------|---------|------------|
| `GOVERNANCE_RULES.md` | 200+ replacements, add cloud matrix | High |
| `PROJECT_PLAN.md` | 150+ replacements, make phases configurable | High |
| `GITHUB_PROJECT_SETUP_AI_FIRST.md` | 100+ replacements, `{PHASE_COUNT}` | High |
| `GITHUB_WORKFLOWS.md` | 80+ replacements, multi-cloud sections | High |

**MEDIUM PRIORITY:**
| File | Changes | Complexity |
|------|---------|------------|
| `HOME_REPO.md` | 50+ replacements | Medium |
| `ROLES_AND_TOOLS.md` | 40+ replacements | Medium |
| `ROADMAP.md` | 60+ replacements, configurable phases | Medium |
| `GITHUB_TOOLS_SETUP.md` | 30+ replacements | Medium |
| `AI_ISSUE_LIFECYCLE.md` | 50+ replacements | Medium |
| `RELEASE_PROCESS.md` | 15 replacements, multi-cloud deployment | Medium |
| `AI_PR_Review/README.md` | 20+ replacements | Medium |
| `AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md` | 15+ replacements | Medium |
| `AI_PR_Review/LOCAL_SETUP.md` | 20+ replacements, fix deprecated links | Medium |
| `AI_PR_Review/ONBOARDING.md` | 40+ replacements | Medium |

**LOW PRIORITY:**
| File | Changes | Complexity |
|------|---------|------------|
| `AI_TIME_ESTIMATION.md` | 10+ replacements | Low |
| `DEFINITION_OF_DONE.md` | 5 replacements | Low |
| `BRANCHING_STRATEGY.md` | 2 replacements | Low |
| `REPOSITORY_STRATEGY.md` | 20 replacements | Low |
| `REPO_STRUCTURE_DECISION_MATRIX.md` | 5 replacements | Low |
| `PROJECT_KICKOFF_PLAN.md` | 15 replacements | Low |
| `AI_PR_Review/MANUAL_REVIEW_GUIDE.md` | 10 replacements | Low |
| `ghes_runner/GHES_RUNNER_GUIDE.md` | 10 replacements | Low |
| `plans/README.md` | Remove Plan Index table | Low |

## Files to Delete (14 total)

**Deprecated Files:**
| File | Reason |
|------|--------|
| `GITHUB_PROJECT_SETUP.md` | Deprecated, redirects to AI_FIRST version |
| `AI_PR_Review/GCP_SETUP.md` | Deprecated per IPLAN-006 (Vertex AI no longer used) |

**Project-Specific IPLAN Files:**
| File | Reason |
|------|--------|
| `plans/IPLAN-001_phase1-issue-review.md` | Project-specific example |
| `plans/IPLAN-002_create-gcp-cost-guard-repo.md` | Project-specific example |
| `plans/IPLAN-003_ai-pr-review-workflow.md` | Project-specific example |
| `plans/IPLAN-004_ghes-runner-cloud-run.md` | Project-specific example |
| `plans/IPLAN-005_cicd-pipeline-setup.md` | Project-specific example |
| `plans/IPLAN-006_ai-review-conclusion-labels.md` | Project-specific example |
| `plans/IPLAN-007_firestore-config-schema.md` | Project-specific example |
| `plans/IPLAN-008_monorepo-migration.md` | Project-specific example |
| `plans/IPLAN-009_qa-deployment-pipelines.md` | Project-specific example |
| `plans/IPLAN-010_ai-first-phase-gated-deployment.md` | Project-specific example |
| `plans/IPLAN-011_unified-phase-gated-deployment.md` | Project-specific example |

**Project-Specific Configuration:**
| File | Reason |
|------|--------|
| `cicd/phase-deployments.json` | Project-specific configuration |

---

## New Files to Create

1. `README.md` - Framework overview and quick start
2. `CONFIG_TEMPLATE.md` - All placeholder variables with descriptions
3. `SETUP_GUIDE.md` - Step-by-step customization guide
4. `CLOUD_PROVIDER_MATRIX.md` - Mapping of generic concepts to GCP/AWS/Azure services
5. `cicd/phase-deployments-template.json` - Template with `{PHASE_COUNT}` support

---

## Verification

After implementation:

**1. Search for remaining project-specific strings:**
```bash
# Must return 0 results for each
grep -r "aiocto" project_governance/ --include="*.md"
grep -r "USDA-AI-Innovation-Hub" project_governance/ --include="*.md"
grep -r "AI-Cloud-Cost-Monitoring" project_governance/ --include="*.md"
grep -r "github.techtrend.us" project_governance/ --include="*.md"
grep -r "gcp-cost-guard" project_governance/ --include="*.md"
grep -r "techtrend" project_governance/ --include="*.md"
```

**2. Verify placeholder consistency:**
```bash
# List all placeholders used - should match Key Placeholder Variables list
grep -roh '{[A-Z_]*}' project_governance/ --include="*.md" | sort -u
```

**3. Check for broken internal links:**
```bash
# Find all internal markdown links and verify targets exist
grep -roh '\[.*\](\./[^)]*\.md)' project_governance/ --include="*.md" | \
  sed 's/.*(\.\///' | sed 's/).*//' | sort -u | \
  while read f; do
    [ ! -f "project_governance/$f" ] && echo "BROKEN: $f"
  done
```

**4. Validate deleted files have no remaining references:**
```bash
# Should return 0 results
grep -r "GITHUB_PROJECT_SETUP\.md[^_]" project_governance/ --include="*.md"
grep -r "GCP_SETUP\.md" project_governance/ --include="*.md"
grep -r "IPLAN-00" project_governance/ --include="*.md"
```

**5. Manual review checklist:**
- [ ] Read README.md as if new user adopting framework
- [ ] Verify CONFIG_TEMPLATE.md has all 20 variables
- [ ] Confirm multi-cloud sections present in GITHUB_WORKFLOWS.md
- [ ] Test that `plans/README.md` no longer has Plan Index table

---

## Estimated Scope (Revised per Gap Analysis)

- **Files to modify**: 18 markdown files (was 16)
- **Files to delete**: 14 files (11 IPLANs + 2 deprecated + 1 JSON)
- **Files to create**: 5 new framework files
- **Total replacements**: ~1200 string substitutions (was 800+)
- **Placeholder variables**: 20 (was 15)
- **Approach**: Systematic find-replace with manual review for context

---

## Execution Order

1. **Create framework files first** (CONFIG_TEMPLATE.md, CLOUD_PROVIDER_MATRIX.md)
2. **Delete deprecated files** (GITHUB_PROJECT_SETUP.md, AI_PR_Review/GCP_SETUP.md)
3. **Delete project-specific files** (all 11 IPLANs, cicd/phase-deployments.json)
4. **Process high-complexity files** (GOVERNANCE_RULES, PROJECT_PLAN, GITHUB_PROJECT_SETUP_AI_FIRST, GITHUB_WORKFLOWS)
5. **Process medium-complexity files** (HOME_REPO, ROLES_AND_TOOLS, ROADMAP, AI_PR_Review/*, etc.)
6. **Process low-complexity files** (BRANCHING_STRATEGY, DEFINITION_OF_DONE, REPOSITORY_STRATEGY)
7. **Update plans/README.md** (remove Plan Index table, keep structure)
8. **Create README.md and SETUP_GUIDE.md**
9. **Create cicd/phase-deployments-template.json**
10. **Verification pass** (run all verification scripts above)

---

## Key Placeholder Variables (20 total)

**Required - Core:**
| Variable | Description | Example Value |
|----------|-------------|---------------|
| `{PROJECT_PREFIX}` | Short project identifier | `myproj` |
| `{PROJECT_NAME}` | Full project name | `My Project` |
| `{REPO_NAME}` | Repository name | `my-project-repo` |
| `{GITHUB_ORG}` | GitHub organization | `my-org` |
| `{GITHUB_HOST}` | GitHub hostname | `github.com` |
| `{PROJECT_BOARD_NUMBER}` | GitHub project board number | `1` |

**Required - Cloud (GCP):**
| Variable | Description | Example Value |
|----------|-------------|---------------|
| `{GCP_PROJECT_DEV}` | GCP dev project ID | `myproj-dev` |
| `{GCP_PROJECT_STAGING}` | GCP staging project ID | `myproj-staging` |
| `{GCP_PROJECT_PROD}` | GCP prod project ID | `myproj-prod` |
| `{WIF_POOL_NAME}` | Workload Identity pool name | `github-actions-pool` |
| `{WIF_PROVIDER_NAME}` | Workload Identity provider | `github-provider` |
| `{SA_PREFIX}` | Service account prefix | `myproj` |

**Required - Infrastructure:**
| Variable | Description | Example Value |
|----------|-------------|---------------|
| `{CLOUD_RUN_URL}` | Cloud Run deployment URL | `myproj-staging.run.app` |
| `{ARTIFACT_REGISTRY}` | Docker registry path | `us-east4-docker.pkg.dev/{PROJECT}` |

**Optional - Multi-Cloud:**
| Variable | Description | Example Value |
|----------|-------------|---------------|
| `{CLOUD_PROVIDER}` | Primary cloud (GCP/AWS/Azure) | `GCP` |
| `{AWS_ACCOUNT_ID}` | AWS account ID | `123456789012` |
| `{AZURE_SUBSCRIPTION}` | Azure subscription ID | `sub-xxx` |
| `{AI_PROVIDER}` | AI provider (Anthropic/OpenAI/Google) | `Anthropic` |

**Optional - Timeline:**
| Variable | Description | Example Value |
|----------|-------------|---------------|
| `{PHASE_COUNT}` | Number of project phases (4-12) | `8` |
| `{SPRINT_DURATION}` | Sprint length | `2 weeks` |

---

## Standard Labels (Keep As-Is)

These labels are part of the framework standard and do NOT need replacement:

**AI Workflow Labels:**
- `ai:ready`, `ai:in-progress`, `ai:blocked`, `ai:human-required`
- `ai:review-requested`, `ai:review-passed`, `ai:review-failed`
- `ai:deployment`, `ai:development`, `ai:qa-testing`
- `ai:approved`, `ai:rejected`
- `skip-ai-review`

**Phase Labels:**
- `phase:1` through `phase:{PHASE_COUNT}` (auto-generated based on config)

**Component Labels:**
- `component:*` (project defines own components)

**Cloud Labels:**
- `cloud:gcp`, `cloud:aws`, `cloud:azure`

**Iteration Labels:**
- `iteration:1`, `iteration:2`, `iteration:3`

---

## Standard Secret Names (Keep As-Is)

These GitHub secret names are framework conventions and do NOT need replacement:

**AI Provider:**
- `ANTHROPIC_API_KEY` - Claude API key (or equivalent for chosen AI_PROVIDER)

**GitHub:**
- `ELEVATED_PAT` - Personal access token with elevated permissions
- `PROJECT_TOKEN` - Token for GitHub Projects access

**GCP (when using GCP):**
- `GCP_PROJECT_ID` - Project ID (value is replaced, name is standard)
- `GCP_SERVICE_ACCOUNT` - Service account email
- `GCP_WORKLOAD_IDENTITY_PROVIDER` - WIF provider path
- `WIF_PROVIDER` - Alias for WIF provider
- `WIF_SA_EMAIL` - Service account for WIF
- `WIF_SA_EMAIL_DEV` / `_STAGING` / `_PROD` - Environment-specific SAs
- `WIF_CREDENTIALS_DEV` / `_STAGING` / `_PROD` - Environment-specific creds

**Note**: Secret *names* are standardized; secret *values* are project-specific and set during setup.
