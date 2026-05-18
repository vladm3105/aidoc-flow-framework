# Governance Consolidation Plan

**IPLAN-004**: Consolidate governance documentation
**Status**: Draft (Amended)
**Created**: 2026-02-17
**Last Updated**: 2026-02-17
**Author**: Claude Opus 4.5

---

## Objective

Consolidate governance documentation into a root-level `/governance/` folder that serves both framework types (SDD and AI Project Flow), while keeping project-specific planning documents separate.

---

## Gap Analysis (Amendment)

Issues identified during plan review:

| Gap | Severity | Resolution |
|:----|:---------|:-----------|
| Missing `governance/cicd/` | **HIGH** | Added Phase 1.1 to create cicd directory and tracking file |
| Skills path updates missing | **HIGH** | Added Phase 6 for skills updates |
| MANUAL_REVIEW_GUIDE.md omitted | **MEDIUM** | Added to move list explicitly |
| Multi-project guides not updated | **MEDIUM** | Added Phase 7 for documentation updates |
| Empty cicd directory cleanup | **LOW** | Added to Phase 8 cleanup |
| Workflow path verification missing | **MEDIUM** | Added comprehensive verification steps |

---

## Current State Analysis

### Problem
- CODEOWNERS references `/governance/` at root level (doesn't exist)
- Governance docs are buried in `ai_project_issues_flow/governance/`
- Both frameworks need shared governance rules
- Templates like CONTRIBUTING.md, README_AIAGENT.md are not at expected locations
- 6 workflows reference `governance/cicd/phase-deployments.json` which doesn't exist
- Skills reference old governance paths

### Current Structure
```
ai_project_issues_flow/
├── governance/           # 27 files, 496KB
│   ├── GOVERNANCE_RULES.md
│   ├── BRANCHING_STRATEGY.md
│   ├── DEFINITION_OF_DONE.md
│   ├── ... (17 more core files)
│   ├── AI_PR_Review/     # 6 files (including MANUAL_REVIEW_GUIDE.md)
│   ├── plans/            # 5 files
│   ├── ghes_runner/      # 1 file
│   └── cicd/             # EMPTY directory
└── templates/
    ├── CONTRIBUTING.md
    ├── README_AIAGENT.md
    └── CLAUDE.md
```

---

## Target Structure

```
/governance/
├── README.md                          # NEW: Index and navigation
│
├── # === SHARED GOVERNANCE (both frameworks) ===
├── GOVERNANCE_RULES.md                # MOVE from ai_project_issues_flow/governance/
├── BRANCHING_STRATEGY.md              # MOVE
├── DEFINITION_OF_DONE.md              # MOVE
├── RELEASE_PROCESS.md                 # MOVE
├── REPOSITORY_STRATEGY.md             # MOVE
├── REPO_STRUCTURE_DECISION_MATRIX.md  # MOVE
├── ROLES_AND_TOOLS.md                 # MOVE
├── HOME_REPO.md                       # MOVE (describes mono-repo pattern)
│
├── # === AI PR REVIEW (shared) ===
├── AI_PR_Review/                      # MOVE entire directory
│   ├── README.md
│   ├── AI_AGENT_REVIEW_WORKFLOW.md
│   ├── LOCAL_SETUP.md
│   ├── MANUAL_REVIEW_GUIDE.md         # EXPLICIT (was missing from original plan)
│   └── ONBOARDING.md
│
├── # === GITHUB SETUP (shared) ===
├── github/                            # NEW subdirectory
│   ├── GITHUB_TOOLS_SETUP.md          # MOVE
│   ├── GITHUB_WORKFLOWS.md            # MOVE
│   ├── GITHUB_PROJECT_SETUP.md        # MOVE (rename from AI_FIRST)
│   └── ghes_runner/                   # MOVE
│       └── GHES_RUNNER_GUIDE.md
│
├── # === CI/CD TRACKING (NEW) ===
├── cicd/                              # NEW: Required by 6 workflows
│   └── phase-deployments.json         # NEW: Phase tracking file template
│
├── # === PLAN TEMPLATES (shared) ===
└── plans/                             # MOVE template only
    ├── README.md                      # MOVE
    └── IPLAN-TEMPLATE.md              # MOVE

/ai_project_issues_flow/
├── governance/                        # KEEP project-specific items
│   ├── PROJECT_PLAN.md                # KEEP (this project's plan)
│   ├── PROJECT_KICKOFF_PLAN.md        # KEEP
│   ├── ROADMAP.md                     # KEEP
│   ├── AI_ISSUE_LIFECYCLE.md          # KEEP (project-specific workflow)
│   ├── AI_TIME_ESTIMATION.md          # KEEP
│   └── plans/                         # KEEP specific IPLANs
│       ├── IPLAN-001_phase-issue-review.md
│       ├── IPLAN-002_ai-pr-review-workflow.md
│       └── IPLAN-003_phase-gated-deployment.md
└── templates/                         # KEEP as templates source
    └── (unchanged)

# Root-level files (elevate from templates)
/CONTRIBUTING.md                       # SYMLINK to ai_project_issues_flow/templates/
/README_AIAGENT.md                     # SYMLINK to ai_project_issues_flow/templates/
```

---

## Implementation Steps

### Phase 1: Create Root Governance Structure

```bash
# Step 1.1: Create all directories (including cicd)
mkdir -p /opt/data/ucx_framework/governance/AI_PR_Review
mkdir -p /opt/data/ucx_framework/governance/github/ghes_runner
mkdir -p /opt/data/ucx_framework/governance/plans
mkdir -p /opt/data/ucx_framework/governance/cicd
```

### Phase 2: Create CI/CD Tracking Infrastructure

```bash
# Step 2.1: Create phase-deployments.json template (required by 6 workflows)
cat > governance/cicd/phase-deployments.json << 'EOF'
{
  "schema_version": "1.0",
  "description": "Phase-gated deployment tracking file",
  "phases": {
    "phase-1": {
      "name": "Foundation",
      "status": "not_started",
      "environments": {
        "dev": { "deployed": false, "version": null, "timestamp": null },
        "staging": { "deployed": false, "version": null, "timestamp": null },
        "prod": { "deployed": false, "version": null, "timestamp": null }
      }
    }
  },
  "last_updated": null,
  "updated_by": null
}
EOF
```

### Phase 3: Move Shared Governance Files

```bash
# Step 3.1: Core governance files
mv ai_project_issues_flow/governance/GOVERNANCE_RULES.md governance/
mv ai_project_issues_flow/governance/BRANCHING_STRATEGY.md governance/
mv ai_project_issues_flow/governance/DEFINITION_OF_DONE.md governance/
mv ai_project_issues_flow/governance/RELEASE_PROCESS.md governance/
mv ai_project_issues_flow/governance/REPOSITORY_STRATEGY.md governance/
mv ai_project_issues_flow/governance/REPO_STRUCTURE_DECISION_MATRIX.md governance/
mv ai_project_issues_flow/governance/ROLES_AND_TOOLS.md governance/
mv ai_project_issues_flow/governance/HOME_REPO.md governance/

# Step 3.2: AI PR Review (all 6 files explicitly)
mv ai_project_issues_flow/governance/AI_PR_Review/README.md governance/AI_PR_Review/
mv ai_project_issues_flow/governance/AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md governance/AI_PR_Review/
mv ai_project_issues_flow/governance/AI_PR_Review/LOCAL_SETUP.md governance/AI_PR_Review/
mv ai_project_issues_flow/governance/AI_PR_Review/MANUAL_REVIEW_GUIDE.md governance/AI_PR_Review/
mv ai_project_issues_flow/governance/AI_PR_Review/ONBOARDING.md governance/AI_PR_Review/

# Step 3.3: GitHub setup docs
mv ai_project_issues_flow/governance/GITHUB_TOOLS_SETUP.md governance/github/
mv ai_project_issues_flow/governance/GITHUB_WORKFLOWS.md governance/github/
mv ai_project_issues_flow/governance/GITHUB_PROJECT_SETUP_AI_FIRST.md governance/github/GITHUB_PROJECT_SETUP.md
mv ai_project_issues_flow/governance/ghes_runner/GHES_RUNNER_GUIDE.md governance/github/ghes_runner/

# Step 3.4: Plan templates only
mv ai_project_issues_flow/governance/plans/README.md governance/plans/
mv ai_project_issues_flow/governance/plans/IPLAN-TEMPLATE.md governance/plans/
```

### Phase 4: Create Symlinks for Root-Level Files

```bash
# Step 4.1: Create symlinks for commonly referenced files
ln -sf ai_project_issues_flow/templates/CONTRIBUTING.md CONTRIBUTING.md
ln -sf ai_project_issues_flow/templates/README_AIAGENT.md README_AIAGENT.md
```

### Phase 5: Create Governance README Index

Create `/governance/README.md` with navigation:

```markdown
# Governance Documentation

Unified governance rules for both SDD and AI Project Flow frameworks.

## Core Governance
- [GOVERNANCE_RULES.md](./GOVERNANCE_RULES.md) - Operational policies and mandatory rules
- [BRANCHING_STRATEGY.md](./BRANCHING_STRATEGY.md) - Git workflow and branch conventions
- [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md) - Completion criteria
- [RELEASE_PROCESS.md](./RELEASE_PROCESS.md) - Versioning and deployment
- [REPOSITORY_STRATEGY.md](./REPOSITORY_STRATEGY.md) - Mono-repo patterns
- [ROLES_AND_TOOLS.md](./ROLES_AND_TOOLS.md) - Human vs AI task split

## AI PR Review
- [AI_PR_Review/](./AI_PR_Review/) - Automated and on-demand PR review workflows

## GitHub Setup
- [github/](./github/) - GitHub tools, workflows, and project setup guides

## CI/CD
- [cicd/](./cicd/) - Phase-gated deployment tracking

## Plan Templates
- [plans/](./plans/) - IPLAN templates and guidance
```

### Phase 6: Update Skills References

```bash
# Step 6.1: Update ai-pr-review skill paths
sed -i 's|ai_project_issues_flow/governance/AI_PR_Review|governance/AI_PR_Review|g' \
  .claude/skills/ai-pr-review/SKILL.md

sed -i 's|ai_project_issues_flow/governance/AI_PR_Review|governance/AI_PR_Review|g' \
  .claude/skills/ai-pr-review_quickref.md

# Step 6.2: Verify changes
grep -n "governance/AI_PR_Review" .claude/skills/ai-pr-review/SKILL.md
grep -n "governance/AI_PR_Review" .claude/skills/ai-pr-review_quickref.md
```

### Phase 7: Update Documentation Cross-References

Files requiring path updates:

```bash
# Step 7.1: Update workflow comment references
sed -i 's|ai_project_issues_flow/governance/AI_PR_Review/README.md|governance/AI_PR_Review/README.md|g' \
  .github/workflows/ai-pr-review.yml

# Step 7.2: Update multi-project guides (manual review recommended)
# Files to review and update selectively:
# - MULTI_PROJECT_SETUP_GUIDE.md
# - MULTI_PROJECT_QUICK_REFERENCE.md
# - ai_dev_ssd_flow/PROJECT/PROJECT_MODEL.md

# Step 7.3: Update internal links in moved governance docs
# Review and update relative paths in:
# - governance/GOVERNANCE_RULES.md
# - governance/AI_PR_Review/README.md
# - governance/github/GITHUB_WORKFLOWS.md
```

### Phase 8: Clean Up Empty Directories

```bash
# Step 8.1: Remove now-empty directories
rmdir ai_project_issues_flow/governance/AI_PR_Review
rmdir ai_project_issues_flow/governance/ghes_runner
rmdir ai_project_issues_flow/governance/cicd

# Keep ai_project_issues_flow/governance/plans/ (has specific IPLANs)
# Keep ai_project_issues_flow/governance/ (has project-specific files)
```

### Phase 9: Verify CODEOWNERS Paths

Confirm `.github/CODEOWNERS` paths now resolve correctly:
- `/governance/` ✓ (now exists)
- `/CONTRIBUTING.md` ✓ (symlink)
- `/README_AIAGENT.md` ✓ (symlink)

---

## Files to Modify

### Move (source → destination)

| Source | Destination |
|:-------|:------------|
| `ai_project_issues_flow/governance/GOVERNANCE_RULES.md` | `governance/GOVERNANCE_RULES.md` |
| `ai_project_issues_flow/governance/BRANCHING_STRATEGY.md` | `governance/BRANCHING_STRATEGY.md` |
| `ai_project_issues_flow/governance/DEFINITION_OF_DONE.md` | `governance/DEFINITION_OF_DONE.md` |
| `ai_project_issues_flow/governance/RELEASE_PROCESS.md` | `governance/RELEASE_PROCESS.md` |
| `ai_project_issues_flow/governance/REPOSITORY_STRATEGY.md` | `governance/REPOSITORY_STRATEGY.md` |
| `ai_project_issues_flow/governance/REPO_STRUCTURE_DECISION_MATRIX.md` | `governance/REPO_STRUCTURE_DECISION_MATRIX.md` |
| `ai_project_issues_flow/governance/ROLES_AND_TOOLS.md` | `governance/ROLES_AND_TOOLS.md` |
| `ai_project_issues_flow/governance/HOME_REPO.md` | `governance/HOME_REPO.md` |
| `ai_project_issues_flow/governance/AI_PR_Review/README.md` | `governance/AI_PR_Review/README.md` |
| `ai_project_issues_flow/governance/AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md` | `governance/AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md` |
| `ai_project_issues_flow/governance/AI_PR_Review/LOCAL_SETUP.md` | `governance/AI_PR_Review/LOCAL_SETUP.md` |
| `ai_project_issues_flow/governance/AI_PR_Review/MANUAL_REVIEW_GUIDE.md` | `governance/AI_PR_Review/MANUAL_REVIEW_GUIDE.md` |
| `ai_project_issues_flow/governance/AI_PR_Review/ONBOARDING.md` | `governance/AI_PR_Review/ONBOARDING.md` |
| `ai_project_issues_flow/governance/GITHUB_TOOLS_SETUP.md` | `governance/github/GITHUB_TOOLS_SETUP.md` |
| `ai_project_issues_flow/governance/GITHUB_WORKFLOWS.md` | `governance/github/GITHUB_WORKFLOWS.md` |
| `ai_project_issues_flow/governance/GITHUB_PROJECT_SETUP_AI_FIRST.md` | `governance/github/GITHUB_PROJECT_SETUP.md` |
| `ai_project_issues_flow/governance/ghes_runner/GHES_RUNNER_GUIDE.md` | `governance/github/ghes_runner/GHES_RUNNER_GUIDE.md` |
| `ai_project_issues_flow/governance/plans/README.md` | `governance/plans/README.md` |
| `ai_project_issues_flow/governance/plans/IPLAN-TEMPLATE.md` | `governance/plans/IPLAN-TEMPLATE.md` |

### Keep in Place (project-specific)

| File | Reason |
|:-----|:-------|
| `ai_project_issues_flow/governance/PROJECT_PLAN.md` | Project-specific |
| `ai_project_issues_flow/governance/PROJECT_KICKOFF_PLAN.md` | Project-specific |
| `ai_project_issues_flow/governance/ROADMAP.md` | Project-specific |
| `ai_project_issues_flow/governance/AI_ISSUE_LIFECYCLE.md` | Project-specific workflow |
| `ai_project_issues_flow/governance/AI_TIME_ESTIMATION.md` | Project-specific |
| `ai_project_issues_flow/governance/plans/IPLAN-001_phase-issue-review.md` | Project-specific plan |
| `ai_project_issues_flow/governance/plans/IPLAN-002_ai-pr-review-workflow.md` | Project-specific plan |
| `ai_project_issues_flow/governance/plans/IPLAN-003_phase-gated-deployment.md` | Project-specific plan |

### Create New

| File | Purpose |
|:-----|:--------|
| `governance/README.md` | Index and navigation for governance docs |
| `governance/cicd/phase-deployments.json` | Phase tracking file (required by 6 workflows) |
| `CONTRIBUTING.md` (symlink) | Points to templates version |
| `README_AIAGENT.md` (symlink) | Points to templates version |

### Update References

| File | Change Required |
|:-----|:----------------|
| `.claude/skills/ai-pr-review/SKILL.md` | Update governance paths |
| `.claude/skills/ai-pr-review_quickref.md` | Update governance paths |
| `.github/workflows/ai-pr-review.yml` | Update comment reference |
| `MULTI_PROJECT_SETUP_GUIDE.md` | Review and update selectively |
| `MULTI_PROJECT_QUICK_REFERENCE.md` | Review and update selectively |

---

## Verification

### Pre-Implementation Verification

```bash
# Verify all source files exist before moving
for f in GOVERNANCE_RULES.md BRANCHING_STRATEGY.md DEFINITION_OF_DONE.md \
         RELEASE_PROCESS.md REPOSITORY_STRATEGY.md REPO_STRUCTURE_DECISION_MATRIX.md \
         ROLES_AND_TOOLS.md HOME_REPO.md; do
  test -f "ai_project_issues_flow/governance/$f" || echo "MISSING: $f"
done

# Verify AI_PR_Review files
for f in README.md AI_AGENT_REVIEW_WORKFLOW.md LOCAL_SETUP.md \
         MANUAL_REVIEW_GUIDE.md ONBOARDING.md; do
  test -f "ai_project_issues_flow/governance/AI_PR_Review/$f" || echo "MISSING: $f"
done
```

### Post-Implementation Verification

```bash
# 1. Directory structure
tree governance/

# 2. Symlinks work
cat CONTRIBUTING.md | head -5
cat README_AIAGENT.md | head -5

# 3. CODEOWNERS paths exist
test -d governance && echo "✓ /governance/ exists"
test -f CONTRIBUTING.md && echo "✓ /CONTRIBUTING.md exists"
test -f README_AIAGENT.md && echo "✓ /README_AIAGENT.md exists"

# 4. CI/CD tracking file exists
test -f governance/cicd/phase-deployments.json && echo "✓ phase-deployments.json exists"

# 5. No broken links in governance docs
grep -r "ai_project_issues_flow/governance" governance/ && echo "WARN: Old paths found" || echo "✓ No old paths"

# 6. Workflow governance paths resolve
for path in $(grep -ohE "governance/[a-zA-Z0-9_/.-]+" .github/workflows/*.yml | sort -u); do
  test -e "$path" || echo "MISSING: $path"
done

# 7. Skills relative paths work
test -f governance/AI_PR_Review/README.md && echo "✓ AI_PR_Review accessible"

# 8. Git status shows clean moves
git status --short
```

---

## Rollback

If issues arise:
```bash
git checkout -- ai_project_issues_flow/governance/
git checkout -- .claude/skills/ai-pr-review/
git checkout -- .github/workflows/ai-pr-review.yml
rm -rf governance/
rm -f CONTRIBUTING.md README_AIAGENT.md
```

---

## Summary

| Metric | Value |
|:-------|:------|
| Files to move | 19 |
| Files to keep in place | 8 |
| New files to create | 4 |
| Symlinks to create | 2 |
| Directories to create | 5 |
| Directories to remove | 3 |
| Files requiring path updates | 5 |

---

## Approval

- [x] Plan reviewed
- [x] Gap analysis completed
- [x] Amendments incorporated
- [x] Ready for implementation
- [x] **Implementation complete** (2026-02-17)
