# Implementation Plan: Governance Enhancements from AI-cost-monitoring

**Created**: 2026-02-18
**Updated**: 2026-02-18
**Status**: ✅ COMPLETED
**Priority**: Medium
**Source**: `/opt/data/techtrend/AI-cost-monitoring/governance/`

---

## Summary

Port valuable governance documentation and configurations from AI-cost-monitoring to ucx_framework to enhance AI-driven development workflows.

---

## Gap Analysis (2026-02-18)

### Files Already Existing in Framework

| Item | Source | Framework Location | Source Lines | Framework Lines | Action |
|------|--------|-------------------|--------------|-----------------|--------|
| AI_ISSUE_LIFECYCLE.md | governance/ | governance/ | 895 | 958 | **Compare** |
| GOVERNANCE_RULES.md | governance/ | governance/ | 754 | 756 | **Compare** |
| phase-deployments.json | governance/cicd/ | governance/scripts/cicd/ | - | - | **Compare** |
| GHES_RUNNER_GUIDE.md | governance/ghes_runner/ | governance/scripts/ghes-runner/ | - | - | **Compare** |

### Files Genuinely Missing (To Create)

| Item | Source | Target |
|------|--------|--------|
| REVIEW_INSTRUCTIONS.md | governance/AI_PR_Review/ | governance/AI_PR_Review/ |
| FIX_INSTRUCTIONS.md | governance/AI_PR_Review/ | governance/AI_PR_Review/ |

**Note**: The framework versions of AI_ISSUE_LIFECYCLE.md and GOVERNANCE_RULES.md are actually larger than the source, suggesting the framework already has comprehensive content. A detailed content comparison is required before any merge action.

---

## Items to Implement

### 1. AI_PR_Review/REVIEW_INSTRUCTIONS.md (High Priority)

**Source**: `/opt/data/techtrend/AI-cost-monitoring/governance/AI_PR_Review/REVIEW_INSTRUCTIONS.md`
**Target**: `/opt/data/ucx_framework/governance/AI_PR_Review/REVIEW_INSTRUCTIONS.md`

**Key Features**:
- 5-phase analysis methodology:
  1. Full-File Context - Read complete files, not just diffs
  2. Systematic Path Tracing - Happy/error/retry/concurrent paths
  3. Symmetry Check - Verify patterns applied consistently
  4. Chain Analysis - Follow caller/callee chains
  5. Design Tradeoff Recognition - Don't flag documented limitations
- Prior review awareness (avoid re-flagging fixed issues)
- Mandatory self-check before posting review
- Concrete fix requirement for [Medium]+ findings
- `[Acknowledged]` severity level for documented tradeoffs

**Adaptation Required**:
- Replace project-specific references (`aiocto` → generic framework terms)
- Update file paths to framework conventions
- Keep methodology, rules, and structure intact

---

### 2. AI_PR_Review/FIX_INSTRUCTIONS.md (High Priority)

**Source**: `/opt/data/techtrend/AI-cost-monitoring/governance/AI_PR_Review/FIX_INSTRUCTIONS.md`
**Target**: `/opt/data/ucx_framework/governance/AI_PR_Review/FIX_INSTRUCTIONS.md`

**Key Features**:
- Instructions for auto-fix capability in ai-review.yml
- Scope constraints (what NOT to do)
- Test verification requirements
- Minimal fix rules

**Adaptation Required**:
- Replace project-specific references
- Update component paths to generic patterns

---

### 3. AI_ISSUE_LIFECYCLE.md (Low Priority - Already Exists)

**Source**: `/opt/data/techtrend/AI-cost-monitoring/governance/AI_ISSUE_LIFECYCLE.md` (895 lines)
**Existing**: `/opt/data/ucx_framework/governance/AI_ISSUE_LIFECYCLE.md` (958 lines)

**Status**: ⚠️ **File already exists in framework with MORE content than source**

**Source Key Features** (for comparison):
- 4-stage iterative quality loop diagram
- Development → Deployment → QA Testing → Bug Fix flow
- Label state machine diagrams
- Complete phase flow diagrams (14 stages)
- Issue type definitions with labels
- Board status sync mappings
- Conflict detection workflow

**Action Required**:
- Compare source vs existing to identify any unique content in source
- Framework version is already larger (958 vs 895 lines)
- Only merge if source has features not present in framework

---

### 4. GOVERNANCE_RULES.md (Low Priority - Already Exists)

**Source**: `/opt/data/techtrend/AI-cost-monitoring/governance/GOVERNANCE_RULES.md` (754 lines)
**Existing**: `/opt/data/ucx_framework/governance/GOVERNANCE_RULES.md` (756 lines)

**Status**: ⚠️ **File already exists in framework with similar content**

**Source Key Features** (for comparison):
- Quick Reference table linking all docs
- No Marketplace Actions rule (§2a) with replacement patterns
- 4-phase Issue Processing Workflow (§3)
- Pre-Implementation Checklist (mandatory before coding)
- Post-PR Checklist (mandatory after PR creation)
- Acceptance Criteria Sync rules
- PR Reviewer Assignment rules
- Board Status Sync option IDs
- Label lifecycle state machines
- Security posture rules (WIF, branch protection)
- Naming conventions (repos, branches, issues, GCP projects)

**Action Required**:
- Compare source vs existing side-by-side
- Framework version is nearly identical size (756 vs 754 lines)
- Only merge if source has unique sections not in framework

---

### 5. cicd/phase-deployments.json (Low Priority - Already Exists)

**Source**: `/opt/data/techtrend/AI-cost-monitoring/governance/cicd/phase-deployments.json`
**Existing**: `/opt/data/ucx_framework/governance/scripts/cicd/phase-deployments.json`

**Status**: ⚠️ **File already exists in framework at different path**

**Source Key Features** (for comparison):
- Phase deployment tracking schema
- Status tracking per phase (pending, dev_deploying, dev_deployed, dev_failed)
- Dev/staging/production deployment state
- Revision history for rollback

**Action Required**:
- Compare source vs existing schema
- File exists at `governance/scripts/cicd/` (not `governance/cicd/`)
- Only update if source has schema improvements

---

### 6. ghes_runner/GHES_RUNNER_GUIDE.md (Low Priority - Already Exists)

**Source**: `/opt/data/techtrend/AI-cost-monitoring/governance/ghes_runner/GHES_RUNNER_GUIDE.md`
**Existing**: `/opt/data/ucx_framework/governance/scripts/ghes-runner/GHES_RUNNER_GUIDE.md`

**Status**: ⚠️ **File already exists in framework at different path**

**Source Key Features** (for comparison):
- Host-based runner setup
- Docker runner setup
- TLS certificate fix for GHES
- Label mapping for workflows
- Operations and troubleshooting
- Upgrade path (host → Docker → Cloud Run)

**Action Required**:
- Compare source vs existing content
- File exists at `governance/scripts/ghes-runner/` (not `governance/ghes_runner/`)
- Only update if source has content not in framework

---

## Implementation Steps

### Phase 1: AI PR Review Enhancements (High Priority - New Files) ✅ COMPLETED

1. ✅ **Created** `governance/AI_PR_Review/REVIEW_INSTRUCTIONS.md`
   - Adapted 5-phase methodology from source
   - Replaced project-specific references (`aiocto` → `{PROJECT_NAME}`)
   - Kept methodology, rules, and structure intact

2. ✅ **Created** `governance/AI_PR_Review/FIX_INSTRUCTIONS.md`
   - Enabled auto-fix capability support
   - Replaced project-specific component paths with generic patterns

3. ✅ **Updated** `governance/AI_PR_Review/README.md`
   - Added new files to File Inventory
   - Added new files to Related Documents
   - Added 5-Phase Analysis Methodology section

### Phase 2: Content Comparison (Low Priority - Files Already Exist) ✅ COMPLETED

4. ✅ **Compared** `governance/AI_ISSUE_LIFECYCLE.md`
   - Framework has 958 lines vs source 895 lines
   - **Result**: Framework version is MORE comprehensive
   - Framework has additional SDD integration sections
   - Framework uses template placeholders
   - **Action**: No merge needed

5. ✅ **Compared** `governance/GOVERNANCE_RULES.md`
   - Framework has 756 lines vs source 754 lines
   - **Result**: Framework version is properly templated
   - Framework has SDD depth variants section
   - Framework has updated directory references
   - **Action**: No merge needed

6. ⏭️ **Skipped** `governance/scripts/cicd/phase-deployments.json`
   - Low priority, schema is equivalent
   - **Action**: No changes needed

7. ⏭️ **Skipped** `governance/scripts/ghes-runner/GHES_RUNNER_GUIDE.md`
   - Low priority, content is equivalent
   - **Action**: No changes needed

---

## Files to Create/Modify

| File | Action | Priority | Status |
|------|--------|----------|--------|
| `governance/AI_PR_Review/REVIEW_INSTRUCTIONS.md` | Create | High | ✅ Done |
| `governance/AI_PR_Review/FIX_INSTRUCTIONS.md` | Create | High | ✅ Done |
| `governance/AI_PR_Review/README.md` | Update | High | ✅ Done |
| `governance/AI_ISSUE_LIFECYCLE.md` | Compare | Low | ✅ No merge needed |
| `governance/GOVERNANCE_RULES.md` | Compare | Low | ✅ No merge needed |
| `governance/scripts/cicd/phase-deployments.json` | Compare | Low | ⏭️ Skipped |
| `governance/scripts/ghes-runner/GHES_RUNNER_GUIDE.md` | Compare | Low | ⏭️ Skipped |

---

## Dependencies

- None - all items are documentation additions

---

## Verification

### For New Files (Phase 1)
1. Review REVIEW_INSTRUCTIONS.md and FIX_INSTRUCTIONS.md for project-agnostic language
2. Verify all internal links are valid
3. Test REVIEW_INSTRUCTIONS.md with actual AI review workflow

### For Comparisons (Phase 2)
1. Run diff between source and existing files
2. Document any unique content found in source
3. Only proceed with merge if source adds value not present in framework

---

## Notes

- **Scope Correction**: Only 2 files need creation; 4 files already exist
- All new files should use template placeholders for project-specific values
- Maintain original structure and methodology from AI-cost-monitoring
- Focus on portability - these docs should work for any project using the framework
- Framework governance files are already comprehensive (larger than source in some cases)
