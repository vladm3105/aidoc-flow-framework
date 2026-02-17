# AI Issue Lifecycle

**Framework**: AI Project Issues Flow
**Project**: {PROJECT_NAME} (`{PROJECT_PREFIX}`)
**Related**: See `plans/` for implementation plans (IPLAN documents)

> **Note**: This document is for **AI Project Issues Flow** - the lightweight, issue-based framework for small-medium AI-first projects. For formal specification-driven development (15-layer architecture), see [`../sdd_flow/`](../sdd_flow/).

This document describes how GitHub issues flow through the AI-first development workflow, from creation to deployment.

## How Issues Are Created in Issues Flow

Unlike SDD Flow where issues are derived from formal TASKS documents, **Issues Flow creates issues directly from the project description**:

```
00_REF/ (Project Description)
    ↓
Human reviews requirements
    ↓
Human creates GitHub issue with:
    - Clear title: [Phase-Sprint] Task description
    - Labels: phase:N, ai:development, component:X
    - Acceptance criteria in body
    ↓
AI agent picks up issue when ai:ready label is added
```

This approach is faster but less formal than SDD Flow's 15-layer documentation chain.

---

## Overview

This workflow uses a **4-stage iterative quality loop** with four issue types:

```

                     4-STAGE ITERATIVE QUALITY LOOP                              
                                                                                 
  DEVELOPMENT (ai:development)                                                   
  Created by human → AI develops → PR merged → Issue CLOSED                     
                                                                                
                                               
                                                                               
  DEPLOYMENT (ai:deployment)              QA TESTING (ai:qa-testing)            
  Auto-created → AI reviews →             Auto-created (if functional) →        
  Staging deploy → CLOSED                 Dormant until deploy complete         
                                                                               
                                               
                                                                                
                          QA EXECUTION (on staging)                              
                                                                                
                                                     
                                                                               
                       PASS                      FAIL                            
                                                                               
                                                                               
                    Close QA              BUG FIX (ai:development + bug)        
                    Issue                 Auto-created → Loops back to          
                                         Development (max 3 iterations)        
                                                                               
                    PRODUCTION                             
                                                                                 

```

### Benefits of 4-Stage Loop

| Benefit | How It's Achieved |
|:--------|:------------------|
| **Independent lifecycle** | Each issue type has separate labels and workflow |
| **Specialized instructions** | Each issue type has tailored body template |
| **Saves LLM context** | AI reads only relevant issue type per stage |
| **Automated iteration** | Bug fixes automatically loop back through stages |
| **Human visibility** | GitHub Project board shows all 4 stages clearly |
| **Quality gates** | Max 3 iterations before human intervention |
| **Consolidated review** | Review all issues of same type together |
| **Audit trail** | Clear link: Dev → PR → Deploy → QA → Bug (if any) |

---

## Issue Types

| Type | Label | Purpose | Created By | Closed When |
|:-----|:------|:--------|:-----------|:------------|
| **Development** | `ai:development` | Code changes, feature implementation | Human | PR merged |
| **Deployment** | `ai:deployment` | Deployment instructions, consolidation | `create-deployment-issue.yml` | Staging deployed |
| **QA Testing** | `ai:qa-testing` | Comprehensive testing after deployment | `create-qa-testing-issue.yml` | Tests pass |
| **Bug Fix** | `ai:development` + `bug` | Fixes for QA failures | `create-bug-issue.yml` | PR merged (loops back) |

---

## Development Issue Flow

### Stage 1: Issue Creation (Human)

```
HUMAN CREATES DEVELOPMENT ISSUE
       
       

  Issue #100: [P1-1.1] Implement cost alerts                                    
  Labels: phase:1, ai:development                                               
  Board Status: Backlog                                                         

         
           Human adds label `ai:ready` when issue is ready for AI
         

 Label: ai:ready   TRIGGER: agent-dispatch.yml

```

**Human Responsibilities**:
1. Create issue with clear description and acceptance criteria
2. Assign `phase:N` label (1-8)
3. Assign `ai:development` label
4. Add dependencies: `Depends on #X`, `Blocks #Y`
5. When ready for AI, add `ai:ready` label

---

### Stage 2: Agent Dispatch (Automated)

```

  AGENT DISPATCH (agent-dispatch.yml)                                           
  Trigger: issues.labeled event where label == 'ai:ready'                       
   
                                                                                 
  1. Workflow detects `ai:ready` label added                                    
  2. Checks if issue already has `ai:in-progress` (skip if yes)                 
  3. Removes `ai:ready`, adds `ai:in-progress`                                  
  4. Updates Project Board status → "In Progress"                               
  5. Posts notification to Teams                                                 
  6. AI Agent polls for `ai:in-progress` issues or receives webhook            
                                                                                 

```

**Label Transition**: `ai:ready` → `ai:in-progress`

**Board Status**: Backlog → In Progress

---

### Stage 3: AI Agent Local Development

```

  AI AGENT LOCAL DEVELOPMENT                                                     
  Executor: AI Agent ({AI_TOOL_NAME} Code, Gemini CLI, or similar)                      
   
                                                                                 
  STEP 1: Understand Requirements                                                
   Read issue body, acceptance criteria, comments                             
   Read linked/dependent issues                                               
   Read relevant code and documentation                                       
   Check for open PRs modifying same files (conflict check)                  
                                                                                 
  STEP 2: Setup Test Environment                                                 
   Load test secrets                                                          
   Start local services: docker-compose -f docker-compose.test.yml up -d     
   Verify connectivity to emulators                                           
                                                                                 
  STEP 3: Implement Solution                                                     
   Write code following project standards                                     
   Write/update unit tests (≥90% coverage)                                   
   Write/update integration tests (≥70% coverage)                            
   Update documentation if needed                                             
                                                                                 
  STEP 4: Local Testing (Quality Gates)                                          
   Lint & Format: ruff check . && ruff format --check .                       
   Type Check: pyright .                                                       
   Unit Tests: pytest tests/unit/ --cov --cov-fail-under=90                  
   Integration Tests: pytest tests/integration/ --cov-fail-under=70          
   Regression Tests: pytest tests/ -x                                         
   Security Scan: bandit -r src/ && pip-audit                                
   Local Smoke Test: curl -f http://localhost:8080/health                    
   Conflict Check: python3 governance/scripts/workflows/check_conflicts.py                        
                                                                                 
  STEP 5: Create PR                                                              
   Stop local services                                                        
   Create branch: ai/{issue_number}-{slug}                                   
   Commit changes with test results summary                                   
   Push branch and create PR with "Closes #N"                                
   Change label: ai:in-progress → ai:review-requested                        
   Update Project Board status → "In Review"                                 
   Post PR link as comment on issue                                          
                                                                                 

```

**Label Transition**: `ai:in-progress` → `ai:review-requested`

**Board Status**: In Progress → In Review

**PR Body Format**:
```markdown
Closes #100

## Summary
- Implemented cost alert feature
- Added unit tests (95% coverage)

## Test Results
- Unit tests: 95% coverage
- Integration tests: 78% coverage
- All quality gates passed

## Linked Issue
https://{GITHUB_HOST}/.../issues/100
```

---

### Stage 4: PR Review (CI + AI Review)

```

  PR REVIEW (ci.yml + ai-review.yml)                                            
  Trigger: PR opened, synchronized, ready_for_review                            
   
                                                                                 
  1. CI pipeline runs: lint, type check, test, security scan                   
  2. AI review runs (if not draft, dependabot, or skip-ai-review label)        
  3. AI posts review comments and applies ai:review-passed/failed label        
  4. Human reviewer approves or requests changes                                 
                                                                                 
  NOTE: Per-PR dev deployments are deprecated.                                  
  Dev deployment now occurs at phase completion, not per-PR.                    
                                                                                 

```

---

### Stage 5: PR Merge and Development Issue Close

```

  PR MERGED → DEVELOPMENT ISSUE CLOSED                                          
   
                                                                                 
  1. Human or AI approves and merges PR                                         
  2. GitHub auto-closes development issue (due to "Closes #N" in PR body)      
  3. Development issue status → "Done" on Project Board                         
                                                                                 
     
                                                                                 
  TRIGGERS: create-deployment-issue.yml                                         
                                                                                 

```

**Board Status**: In Review → Done

---

## Deployment Issue Flow

### Stage 6: Deployment Issue Creation (Automated)

```

  DEPLOYMENT ISSUE CREATION (create-deployment-issue.yml)                       
  Trigger: pull_request.closed (merged == true)                                 
   
                                                                                 
  1. Extract linked development issue from PR body                              
  2. Get phase label from development issue                                     
  3. Check if development issue has `ai:development` label                      
  4. Find other deployment issues in same phase (for blocking)                  
  5. Extract deployment considerations from PR:                                 
     - Database migrations detected?                                            
     - Config changes detected?                                                 
     - Infrastructure changes detected?                                         
  6. Create deployment issue:                                                   
     - Title: [P{N}-Deploy-{task}] {feature}                                   
     - Labels: phase:N, ai:deployment                                          
     - Body: Source links, changes summary, deployment checklist               
     - Blocked by: other deployment issues in same phase                       
  7. Link deployment issue to development issue (comment)                       
  8. Check if all phase development issues are closed                          
  9. If phase complete → trigger deployment review                              
                                                                                 

```

**Deployment Issue Created**:
```markdown
## Deployment Issue

**Source**
| Field | Value |
|:------|:------|
| Development Issue | #100 |
| Pull Request | #200 |
| Merged | {DATE}T18:30:00Z |

**Depends on**: #100 (development complete)
**Blocked by**: #301, #302 (deploy together)

## Changes Summary
Implement cost alerts

## Deployment Considerations
| Category | Status |
|:---------|:-------|
| Database Migrations | None detected |
| Config Changes | **Yes** - Review config changes |
| Infrastructure | None detected |

## Deployment Checklist
- [ ] Review changes summary
- [ ] Verify all dependent deployments ready
- [ ] Check for breaking changes
- [ ] Verify rollback procedure

## Deployment Notes
<!-- AI Agent: Add specific deployment instructions here -->

## Test Scenarios for Staging
- [ ] Smoke test: Health endpoint returns 200
- [ ] Feature test: {describe feature-specific test}
- [ ] Regression test: Existing functionality works
```

---

### Stage 7: Phase Development Completion Check (Automated)

```

  PHASE COMPLETION CHECK (check-phase-completion.yml)                           
  Triggers: Hourly schedule, issues.closed event, create-deployment-issue.yml  
   
                                                                                 
  For each phase 1..8:                                                          
    1. Skip if phase already deployed + tests passed                            
    2. Skip if phase status is "needs-revalidation"                             
    3. Verify all previous phases deployed + passed                             
    4. Get all issues with label `phase:N` AND `ai:development`                
    5. Check if ALL development issues are CLOSED                               
    6. Check for open blocker issues                                            
    7. If all development complete and no blockers:                             
       → Phase N development complete                                           
       → Notify AI Agent to review deployment issues                            
       → Update governance/cicd/phase-deployments.json                               
                                                                                 

```

---

### Stage 8: Deployment Review (AI Agent)

```

  DEPLOYMENT REVIEW                                                              
  Executor: AI Agent                                                             
   
                                                                                 
  1. Get all deployment issues for phase N:                                     
     gh issue list --label "phase:N" --label "ai:deployment"                   
                                                                                 
  2. Read each deployment issue:                                                
     - Changes summary                                                          
     - Deployment considerations                                                
     - Dependencies and blocking relationships                                  
                                                                                 
  3. Create consolidated deployment plan:                                       
     - Order of operations                                                      
     - Migration sequence                                                       
     - Config changes needed                                                    
     - Rollback procedures                                                      
                                                                                 
  4. Identify gaps:                                                             
     - Missing deployment notes                                                 
     - Conflicting changes                                                      
     - Incomplete checklists                                                    
                                                                                 
  5. Update deployment issues with:                                             
     - Specific deployment instructions                                         
     - Order number                                                             
     - Dependencies verified                                                    
                                                                                 
  6. Trigger staging deployment                                                 
                                                                                 

```

---

### Stage 8.5: Dev Deployment (Per-Phase)

```

  DEV DEPLOYMENT (deploy-dev.yml)                                               
  Trigger: check-phase-completion.yml detects phase N issues all closed         
   
                                                                                 
  1. Verify previous phases (1..N-1) are dev_deployed                           
  2. Build container image with tag: phase-{N}-{sha}                            
  3. Deploy to dev Cloud Run                                                     
  4. Run smoke tests (health, ready, version, config)                           
  5. Update phase tracking (dev_deployed or dev_failed)                         
  6. Trigger check-all-phases-dev.yml                                           
                                                                                 
  check-all-phases-dev.yml:                                                      
    → Checks if ALL 8 phases are dev_deployed                                   
    → If YES: triggers deploy-staging.yml with Phase 8 image                    
    → If NO: exits (waits for more phases)                                      
                                                                                 

```

---

### Stage 9: Staging Deployment (Automated)

```

  STAGING DEPLOYMENT (deploy-staging.yml)                                       
  Trigger: check-all-phases-dev.yml (when ALL phases dev_deployed)              
   
                                                                                 
  1. Copy Phase 8 image from dev registry to staging registry                  
  2. Deploy to staging Cloud Run                                                
  3. Health check with retry                                                    
  4. Run FULL acceptance tests (all phases)                                     
  5. Update staging tracking in phase-deployments.json                          
                                                                                 
  NOTE: Staging deploys ONLY when ALL 8 phases are dev_deployed.                
  Staging is never partial — always a complete, production-like environment.   
                                                                                 
  If tests PASS:                                                                 
    → Mark staging as deployed + passed                                         
    → Close all deployment issues                                               
    → Post success notification to Teams                                        
                                                                                 
  If tests FAIL:                                                                 
    → Mark staging as failed                                                    
    → Create regression issues via create_test_failure_issues.py               
    → New regression issues get labels: regression, ai:ready                    
    → Regression issues enter the AI workflow cycle (Stage 2)                  
    → Deployment issues remain open                                             
                                                                                 

```

---

### Stage 10: Production Deployment (Human-Triggered)

```

  PRODUCTION DEPLOYMENT (deploy-prod.yml)                                       
  Trigger: workflow_dispatch by Developer or Project Manager                   
   
                                                                                 
  Prerequisites (all must pass):                                                
     Input confirmation == "DEPLOY"                                           
     Within deployment window (Mon-Fri 10:00-16:00 EST)                       
     All 8 phases deployed + tests passed                                      
     No open issues with label `blocker`                                       
                                                                                 
  Deployment:                                                                    
    1. Post deployment starting notification to Teams                           
    2. Copy staging image to production registry                                
    3. Deploy with 0% traffic                                                   
    4. Run smoke tests on new revision                                          
    5. Gradual rollout: 10% → 50% → 100%                                       
    6. Monitor error rate at each step                                          
    7. Auto-rollback if error rate > 1%                                         
    8. Update tracking file                                                     
    9. Post success/failure notification to Teams                               
                                                                                 

```

---

## QA Testing Flow

### Stage 11: QA Issue Creation (Automated)

```

  QA ISSUE CREATION (create-qa-testing-issue.yml)                               
  Trigger: PR merged to main (same as deployment issue)                         
   
                                                                                 
  1. Check if functional changes (skip docs, cosmetic)                          
     → scripts/check_qa_required.py analyzes changed files                      
                                                                                 
  2. If QA required:                                                             
     a. Extract test plan from dev issue acceptance criteria                    
     b. Create QA testing issue with:                                           
        - Labels: phase:N, ai:qa-testing                                        
        - Link to dev issue, PR, deployment issue                               
        - Test plan (automated + feature-specific)                              
        - Special testing instructions                                          
     c. QA issue is DORMANT (blocked by deployment issues)                      
                                                                                 
  3. If QA not required (docs only):                                            
     → Skip QA issue creation                                                   
     → Log reason                                                               
                                                                                 

```

**QA Required Decision**:
| Change Type | QA Required | Reason |
|:------------|:------------|:-------|
| `.py`, `.ts`, `.js` files | Yes | Functional code |
| API changes | Yes | Contract validation |
| `.md`, `README`, `docs/` | No | Documentation only |
| `.gitignore`, configs | No | Non-functional |

---

### Stage 12: QA Activation (Automated)

```

  QA ACTIVATION (execute-qa-testing.yml)                                        
  Trigger: All deployment issues in phase CLOSED                                
  Schedule: Daily 06:00-08:00 EST (QA window)                                  
   
                                                                                 
  1. Check phase readiness:                                                      
      All deployment issues closed                                             
      Staging deployment successful                                            
      QA issues exist and are not in-progress                                 
                                                                                 
  2. Activate QA issues:                                                         
     → Add label: ai:in-progress                                                
     → Update Project Board: QA Testing                                         
                                                                                 
  3. Run comprehensive tests:                                                    
     → Smoke tests (health endpoints)                                          
     → Unit tests (coverage ≥90%)                                              
     → Integration tests (coverage ≥70%)                                        
     → E2E tests                                                                 
     → Feature-specific tests (from acceptance criteria)                        
                                                                                 

```

**Environment**:
- **Target**: Staging
- **URL**: https://staging.{PROJECT_PREFIX}.{DOMAIN}
- **Timeout**: 120 minutes per phase
- **Isolation**: Uses dedicated test schemas

---

### Stage 13: QA Results Processing (Automated)

```

  QA RESULTS PROCESSING                                                         
   
                                                                                 
  IF ALL TESTS PASS:                                                            
    1. Update QA issue:                                                          
       → Remove: ai:in-progress                                                 
       → Add: ai:qa-passed                                                       
    2. Post test results summary to QA issue                                    
    3. Close QA issue (reason: completed)                                       
    4. Update phase tracking: qa_status = "passed"                              
    5. Phase ready for production                                                
                                                                                 
  IF ANY TEST FAILS:                                                             
    1. Update QA issue:                                                          
       → Remove: ai:in-progress                                                 
       → Add: ai:qa-failed                                                       
    2. Post failure details to QA issue                                         
    3. Trigger create-bug-issue.yml for each failure                            
    4. Update phase tracking: qa_status = "failed"                              
                                                                                 

```

---

### Stage 14: Bug Issue Creation (Automated)

```

  BUG ISSUE CREATION (create-bug-issue.yml)                                     
  Trigger: QA test failure                                                       
   
                                                                                 
  1. Check iteration count:                                                      
     → Current iteration = count of existing bug issues for this test           
                                                                                 
  2. IF iteration ≤ 3:                                                          
     a. Create bug issue with:                                                   
        - Labels: phase:N, ai:development, bug, iteration:N, ai:ready          
        - Link to QA issue, original dev issue                                  
        - Failure details (test file, name, error, stack trace)                 
        - Remaining iterations warning                                          
     b. Bug issue enters Development flow (Stage 2)                             
     c. → PR merge creates new Deployment + QA issues                           
     d. → Loop repeats                                                          
                                                                                 
  3. IF iteration > 3:                                                           
     a. Create escalation issue with:                                           
        - Labels: phase:N, needs-human, blocker                                 
        - History of all fix attempts                                           
        - Persistent failure details                                            
     b. Post urgent alert to Teams                                              
     c. → STOP: Human intervention required                                     
                                                                                 

```

**Iteration Safety**:
| Iteration | Action |
|:----------|:-------|
| 1 | Create bug issue, 2 remaining |
| 2 | Create bug issue, 1 remaining |
| 3 | Create bug issue, **final attempt** |
| 4+ | Create `needs-human` escalation, **STOP** |

---

## Complete Phase Flow Diagram

```
PHASE 1: DEVELOPMENT → DEPLOYMENT → QA TESTING → (BUG FIX if needed)


STAGE 1: DEVELOPMENT

Issue #100 [P1-1.1]                     Issue #300 [P1-Deploy]  Issue #400 [P1-QA]
Labels: phase:1,                        Labels: phase:1,        Labels: phase:1,
        ai:development,                         ai:deployment           ai:qa-testing
        ai:ready                        (auto-created)          (auto-created, DORMANT)
                                                                    
                                                                    
agent-dispatch.yml                                                   
                                                                    
                                                                    
AI Agent develops                                                    
                                                                    
                                                                    
PR #200 merged 
                create-deployment-issue.yml  create-qa-testing-issue.yml
     
Issue #100 CLOSED

       (Same flow for #101, #102...)
     
ALL DEV ISSUES CLOSED
     
     

STAGE 2: DEPLOYMENT

check-phase-completion.yml
     
     

  AI Agent reviews deployment issues #300, #301, #302             
  Creates consolidated deployment plan                             

     
     
deploy-staging.yml
     
     
Close deployment issues #300, #301, #302
     

STAGE 3: QA TESTING

      Deployment issues closed → QA issues ACTIVATED
     
execute-qa-testing.yml (06:00-08:00 EST)
     
     

  AI Agent runs tests on staging:                                  
  - Smoke tests, Unit tests, Integration tests, Feature tests    

     
      ALL PASS  Close QA issues  Phase 1 Complete  PRODUCTION
                      (ai:qa-passed)
     
      ANY FAIL  (ai:qa-failed)
                       
                       

STAGE 4: BUG FIX ITERATION

create-bug-issue.yml
     
     
Issue #500 [P1-Bug-1.1]
Labels: phase:1, ai:development, bug, iteration:1, ai:ready
     
      iteration ≤ 3?
     
      YES  BACK TO STAGE 1 (Development)
                 → AI Agent fixes bug
                 → PR merge creates new Deploy + QA issues
                 → Repeat stages 2-3
                 → If QA passes: Done
                 → If QA fails: iteration++, repeat
     
      NO  CREATE ESCALATION ISSUE
                  Labels: needs-human, blocker
                  → STOP: Human intervention required
```

---

## Label Reference

### Issue Type Labels

| Label | Color | Description |
|:------|:------|:------------|
| `ai:development` | `#5319E7` (purple) | Development issue (code changes) |
| `ai:deployment` | `#006B75` (teal) | Deployment issue (deployment instructions) |
| `ai:qa-testing` | `#7B68EE` (medium purple) | QA testing issue |
| `bug` | `#D73A4A` (red) | Bug fix issue (used with ai:development) |

### Workflow Status Labels

| Label | Meaning | Set By | Triggers |
|:------|:--------|:-------|:---------|
| `ai:ready` | Issue ready for AI pickup | Human | `agent-dispatch.yml` |
| `ai:in-progress` | AI Agent working on issue | `agent-dispatch.yml` | Conflict detection |
| `ai:review-requested` | PR created, awaiting review | AI Agent | — |
| `regression` | Test failure from staging | `deploy-staging.yml` | — |
| `blocker` | Blocks production | Human | `deploy-prod.yml` prereq check |

### QA Status Labels

| Label | Meaning | Set By | Triggers |
|:------|:--------|:-------|:---------|
| `ai:qa-passed` | QA tests passed | `execute-qa-testing.yml` | Close QA issue |
| `ai:qa-failed` | QA tests failed | `execute-qa-testing.yml` | `create-bug-issue.yml` |
| `iteration:1` | First bug fix attempt | `create-bug-issue.yml` | — |
| `iteration:2` | Second bug fix attempt | `create-bug-issue.yml` | — |
| `iteration:3` | Third (final) bug fix attempt | `create-bug-issue.yml` | — |
| `needs-human` | Max iterations exceeded | `create-bug-issue.yml` | STOP automation |

### Phase Labels

| Label | Description |
|:------|:------------|
| `phase:1` | Phase 1: GCP Cost Guard |
| `phase:2` | Phase 2: Foundation Infrastructure |
| `phase:3` | Phase 3: MCP Servers |
| `phase:4` | Phase 4: AI Agents |
| `phase:5` | Phase 5: CopilotKit Chat |
| `phase:6` | Phase 6: Event Processing |
| `phase:7` | Phase 7: Multi-Tenant & A2A |
| `phase:8` | Phase 8: Security & Testing |

---

## Label State Machine

### Development Issue Labels

```
                    
                      phase:N              
                      ai:development       
                    
                                 Human adds ai:ready
                                
                    
                      + ai:ready             Workflow trigger
                    
                                 agent-dispatch.yml
                                
                    
                      - ai:ready           
                      + ai:in-progress       AI Agent working
                    
                                 AI Agent creates PR
                                
                    
                      - ai:in-progress     
                      + ai:review-requested  PR under review
                    
                                 PR merged
                                
                    
                      ISSUE CLOSED         
                    
```

### Deployment Issue Labels

```
                    
                      phase:N              
                      ai:deployment          Auto-created on PR merge
                    
                                 All dev issues closed
                                
                    
                      AI reviews all       
                      deployment issues    
                    
                                 Staging deployed + tests pass
                                
                    
                      ISSUE CLOSED         
                    
```

---

## Project Board Status Sync

The workflows update Project Board #{PROJECT_BOARD_NUMBER} status via GraphQL mutations.

| Board Status | Option ID | Set By |
|:-------------|:----------|:-------|
| Backlog | `e7eaf9e5` | Human (default) |
| Todo | `f75ad846` | Human (prioritized) |
| In Progress | `{BOARD_OPTION_IN_PROGRESS}` | `agent-dispatch.yml` (development issues) |
| In Review | `{BOARD_OPTION_IN_REVIEW}` | AI Agent (post-PR) |
| Deploying | `ea04ab37` | `deploy-staging.yml` (deployment issues) |
| Testing | `cabb455e` | `execute-qa-testing.yml` (QA issues) |
| Done | `{BOARD_OPTION_DONE}` | GitHub (auto on issue close) |

---

## Conflict Detection

When multiple AI Agents work in parallel, `check_conflicts.py` prevents merge conflicts:

```

  CONFLICT CHECK (before PR creation)                                           
   
                                                                                 
  1. List all open PRs with label `ai:in-progress`                              
  2. Get list of files modified in current branch                               
  3. For each open PR:                                                          
     - Get list of files modified                                               
     - Check for intersection                                                   
  4. If conflict detected:                                                      
     - Wait for conflicting PR to merge (poll every 5 min, max 30 min)         
     - Rebase on main                                                           
     - Re-run local tests                                                       
  5. Continue to PR creation                                                    
                                                                                 

```

---

## Tracking Files

### Phase Deployment Status

`governance/cicd/phase-deployments.json`:

```json
{
  "config": {
    "total_phases": 8,
    "repository": "{GITHUB_ORG}/{REPO_NAME}"
  },
  "phases": {
    "1": {
      "name": "GCP Cost Guard",
      "status": "deployed",
      "deployed_at": "{DATE}T18:30:00Z",
      "commit_sha": "abc1234",
      "staging_url": "https://{SERVICE_NAME}-staging.{CLOUD_RUN_DOMAIN}",
      "test_results": "passed",
      "test_report_url": "https://{GITHUB_HOST}/.../actions/runs/123"
    }
  },
  "production": {
    "deployed": false,
    "current_revision": null,
    "revision_history": ""
  }
}
```

---

## Workflows Summary

| Workflow | Trigger | Purpose |
|:---------|:--------|:--------|
| `agent-dispatch.yml` | `ai:ready` label added | Dispatch dev issue to AI Agent |
| `deploy-dev-pr.yml` | CI passes on PR | Deploy PR to ephemeral dev env |
| `cleanup-pr-env.yml` | PR closed | Delete PR environment |
| `create-deployment-issue.yml` | PR merged | Create deployment issue from dev issue |
| `check-phase-completion.yml` | Hourly / issue closed | Check if phase dev is complete |
| `deploy-staging.yml` | Phase dev complete | Deploy phase to staging |
| `deploy-prod.yml` | Manual trigger | Deploy to production |
| `rollback-prod.yml` | Manual trigger | Rollback production |

---

## Related Documents

- [Implementation Plans](plans/) — IPLAN documents for deployment workflows
- [GOVERNANCE_RULES.md](GOVERNANCE_RULES.md) — AI workflow rules
- [GITHUB_WORKFLOWS.md](./github/GITHUB_WORKFLOWS.md) — Workflow documentation
- [AI_AGENT_REVIEW_WORKFLOW.md](AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md) — PR review process
