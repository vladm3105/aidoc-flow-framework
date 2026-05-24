# Roles and Tools Guide

**Project**: {PROJECT_NAME} (`{PROJECT_PREFIX}`)
**Document Type**: Governance
**Last Updated**: {DATE}

---

## Overview

This document defines the roles, responsibilities, and tools used by **humans** and **AI assistants** in the project. Understanding these boundaries ensures efficient collaboration and clear accountability.

Control-plane and execution-plane model:

- Hermes is the human-in-loop control plane for issue triage, planning governance, and post-deployment validation decisions.
- Claude Code, Codex, OpenCode, or equivalent agents are execution-plane workers for implementation and delivery of issues in `ai:ready`.

---

## Quick Reference Matrix

| Capability | Human | AI ({AI_TOOL_NAME} Code) |
|:-----------|:-----:|:----------------:|
| **GitHub Repository** |
| Create/read issues | [PASS] | [PASS] (MCP) |
| Update issue labels | [PASS] | [PASS] (MCP) |
| Create branches | [PASS] | [PASS] (MCP) |
| Push code | [PASS] | [PASS] (MCP) |
| Create/merge PRs | [PASS] | [PASS] Create / [FAIL] Merge |
| Approve PRs | [PASS] | [FAIL] |
| **GitHub Project Board** |
| View project board (UI) | [PASS] | [FAIL] |
| Update board status (GraphQL) | [PASS] | [PASS] (gh CLI) |
| Update custom fields (UI) | [PASS] | [FAIL] |
| Create/edit views | [PASS] | [FAIL] |
| Move cards (UI) | [PASS] | [FAIL] |
| **GCP Console** |
| Create budgets | [PASS] | [FAIL] |
| Enable billing export | [PASS] | [FAIL] |
| IAM permissions | [PASS] | [FAIL] |
| **Code & Infrastructure** |
| Write application code | [PASS] | [PASS] |
| Write Terraform | [PASS] | [PASS] |
| Write tests | [PASS] | [PASS] |
| Review code | [PASS] | [PASS] (advisory/policy-gated) |
| Deploy to production | [PASS] | [FAIL] |
| **Decision Making** |
| Architecture decisions | [PASS] | [FAIL] (research only) |
| Technology selection | [PASS] | [FAIL] (research only) |
| Release approval | [PASS] | [FAIL] |

---

## Human Roles

### Project Manager / Tech Lead

**Responsibilities**:

- Sprint planning and prioritization
- Architecture decisions (ADRs)
- Release approval and deployment
- Stakeholder communication
- Risk management

**Tools**:

| Tool | Purpose |
|:-----|:--------|
| GitHub Project Board | Sprint planning, roadmap views, progress tracking |
| GitHub Issues | Create epics, review AI work |
| GCP Console | Budget setup, IAM, billing configuration |
| Microsoft Teams | Team communication |

**Key Actions**:

- Mark issues as `ai:ready` when specifications are complete
- Review AI-generated PRs and approve/reject
- Update project board custom fields (Size, Priority, Component)
- Make go/no-go decisions for releases

---

### Developer (Human)

**Responsibilities**:

- Implement tasks marked `ai:human-required`
- Review AI-generated code
- Handle security-sensitive implementations
- GCP console configuration
- Production deployments

**Tools**:

| Tool | Purpose |
|:-----|:--------|
| IDE (VS Code, etc.) | Code development |
| GitHub CLI (`gh`) | Issues, PRs, project management |
| Terraform CLI | Infrastructure provisioning |
| GCP Console | Manual cloud configuration |
| Docker | Local development and testing |

**Key Actions**:

- Implement tasks AI cannot do (console work, approvals)
- Code review all AI PRs before merge
- Run `terraform apply` for infrastructure changes
- Configure GCP budgets, billing export, IAM

---

### Reviewer

**Responsibilities**:

- Code quality assurance
- Security review
- Validate AI-generated implementations
- Ensure acceptance criteria are met

**Tools**:

| Tool | Purpose |
|:-----|:--------|
| GitHub PR interface | Review diffs, add comments |
| GitHub Project Board | Track review queue |

**Key Actions**:

- Review PRs labeled `ai:review-requested`
- Approve → merge PR (no label change needed)
- Request changes → add PR comments, AI revises
- Remove `ai:review-requested` label when PR is merged

---

## AI Role ({AI_TOOL_NAME} Code)

### AI Developer

**Responsibilities**:

- Implement tasks marked `ai:ready`
- Generate code following acceptance criteria
- Write tests for implementations
- Create PRs with proper documentation
- Signal work status via labels

**Tools**:

| Tool | Access Level | Purpose |
|:-----|:-------------|:--------|
| GitHub MCP (`github-{PROJECT_PREFIX}-{PROJECT_PREFIX}`) | Full | Issues, PRs, branches, files |
| Filesystem MCP | Full | Local file operations |
| Memory MCP | Full | Session context persistence |
| Sequential Thinking MCP | Full | Complex problem decomposition |
| Context7 MCP | Full | Library documentation lookup |
| Playwright MCP | Full | Browser automation, E2E tests |

**Capabilities**:

```
[PASS] CAN DO:
- Query issues by label (find ai:ready work)
- Read issue bodies (acceptance criteria)
- Update issue labels (signal progress)
- Add comments to issues
- Create feature branches
- Push code to branches
- Create pull requests
- Read files in repository
- Write/edit code files
- Run tests locally
- Search documentation
- Update board status via gh CLI GraphQL (mandatory per GOVERNANCE_RULES.md)

[FAIL] CANNOT DO:
- Access GitHub Project board UI (view/navigate)
- Update project custom fields via MCP (use gh CLI GraphQL instead)
- Merge pull requests
- Approve code reviews
- Access GCP Console
- Deploy to production
- Make architecture decisions
- Access secrets/credentials directly
```

**Workflow**:

```
1. FIND WORK
    list_issues(labels=["ai:ready"])

2. CLAIM ISSUE
    issue_write(labels=["ai:in-progress"])

3. UNDERSTAND REQUIREMENTS
    Read issue body, linked docs

4. IMPLEMENT
    create_branch("ai/{issue}-{slug}")
    Write code, tests
    push_files(branch, files)

5. CREATE PR
    create_pull_request(head, base, title, body)

6. REQUEST REVIEW
    issue_write(labels=["ai:review-requested"])

7. WAIT FOR GOVERNANCE OUTCOME
    Hermes runs Round 1/2 gates; escalate to human on Round 2 failure or branch-protection requirement
```

### Hermes Orchestrator

**Responsibilities**:

- Consume observability alerts and incident signals
- Create and prioritize GitHub issues with severity, repro context, and traceability
- Keep issue lifecycle aligned with governance gates
- Run round-based PR governance gates (`sdd_validate`, `sdd_review`, `sdd_remediate`, post-remediation `sdd_validate`, final blocker-gap check)
- Decide merge-time escalation when Round 2 fails
- Validate post-deployment evidence before issue closure

**Tools**:

| Tool | Access Level | Purpose |
|:-----|:-------------|:--------|
| Observability dashboards/APIs | Read | Alert and incident signal intake |
| GitHub Issues/Projects | Write | Triage, prioritization, lifecycle routing |
| UCX MCP (`sdd-lifecycle`) | Full | BRD->IPLAN orchestration and governance checks |

**Handoff Contract**:

- Hermes routes eligible issues into `ai:ready` after governance conditions are satisfied.
- Execution agents process `ai:ready` issues autonomously through implementation and PR submission.
- Hermes controls round-based PR gating, escalation decisions, and post-deployment closure.

---

## Tool Access Comparison

### GitHub Tools

```

                    GITHUB ECOSYSTEM                            

                                                                
  REPOSITORY LAYER (AI + Human)                                 
   
                                                             
    Issues  Labels  Branches  PRs    
                                                         
                                 
             AI ACCESS (MCP)                            
             - list_issues                              
             - issue_write                              
             - create_branch                            
             - push_files                               
             - create_pull_req                          
                                 
                                                           
   
                                                             
                 
                                                              
  PROJECT LAYER (Human Only)                                    
    
                                                             
    Board  Views  Custom Fields  Roadmap   
                                                             
             
         HUMAN ACCESS ONLY                                
         - gh CLI (GraphQL)                               
         - GitHub Web UI                                  
         - No MCP tools available                         
             
                                                             
    
                                                                

```

### GCP Tools

```

                      GCP ECOSYSTEM                             

                                                                
  INFRASTRUCTURE AS CODE (AI + Human)                           
   
                                                             
    Terraform  Python Code  Config Files             
                                                             
    AI can WRITE these files, but CANNOT APPLY them          
                                                             
   
                                                               
                                                               
  GCP CONSOLE / CLI (Human Only)                                
   
                                                             
    Billing  IAM  APIs  Resources                
                                                             
    - Create budgets (Console)                               
    - Enable billing export (Console)                        
    - terraform apply (CLI)                                  
    - gcloud commands (CLI)                                  
                                                             
   
                                                                

```

---

## Workflow Integration

### Label-Based Handoff

The AI workflow uses labels to signal state transitions between AI and humans:

**AI Workflow Labels** (Minimal Practical Set):

| Label | Who Sets | Who Acts | Purpose |
|:------|:---------|:---------|:--------|
| `ai:ready` | Human | AI | Task well-specified, AI can start |
| `ai:in-progress` | AI | — | AI actively working (tracking) |
| `ai:blocked` | AI | Human | AI stuck, needs input/clarification |
| `ai:review-requested` | AI | Hermes / Human | AI done, PR ready for round-based governance review |
| `ai:human-required` | Human | Human | Not suitable for AI |

**Workflow:**

```
ai:ready → ai:in-progress → ai:review-requested → (Round 1 gates) → (Round 2 if needed) → merge
               ↓
          ai:blocked (if stuck)
```

> **Note:** `ai:approved`/`ai:rejected` labels are not used - PR approval status is sufficient.

**PR Review Labels** (AI review outcome — distinct from issue workflow labels):

| Label | Scope | Applied When | Set By |
|:------|:------|:-------------|:-------|
| `ai:review-passed` | PRs only | APPROVE or COMMENT (low-severity only) | AI review workflow |
| `ai:review-failed` | PRs only | REQUEST_CHANGES | AI review workflow |

These labels track AI code review outcomes on PRs, not issue workflow state. See [GOVERNANCE_RULES.md §3 PR Review Labels](./GOVERNANCE_RULES.md) for details.

**Status Labels** (Phase/Issue Lifecycle):

| Label | Description | Use Case |
|:------|:------------|:---------|
| `status:planning` | In planning stage | Future phases, conditional features |
| `status:implementing` | Active phase | Current sprint/phase work |
| `status:suspended` | Work temporarily paused | Will resume later, on hold |
| `status:blocked` | Blocked by dependency | Waiting on external factor |
| `status:ready` | Ready for development | Specifications complete |

**Scope Labels** (Release Requirements):

| Label | Description | Use Case |
|:------|:------------|:---------|
| `scope:mandatory` | Required for release | Must-have features |
| `scope:optional` | Nice to have | Can defer to future release |

### Typical Task Flow

```
1. SPECIFICATION
   Human/Hermes define task, acceptance criteria, and traceability
   Issue is approved into ai:ready

2. IMPLEMENTATION
   Execution agent (or human for ai:human-required) implements and opens PR

3. ROUND-BASED PR GOVERNANCE
   Round 1: sdd_validate -> sdd_review -> sdd_remediate -> post-remediation sdd_validate -> Hermes final blocker-gap check
   If Round 1 fails: Round 2 with same sequence
   If Round 2 fails: escalate to human and block merge

4. MERGE & DEPLOY
   Merge after gates pass (and human approval when required)
   CI/CD runs, Hermes verifies post-deployment signals, linked issue closes
```

---

## Task Suitability Guide

### AI-Suitable Tasks (`ai:ready`)

| Category | Examples | Why AI Works |
|:---------|:---------|:-------------|
| **Boilerplate** | Project setup, scaffolding | Repetitive, well-defined |
| **CRUD operations** | API endpoints, models | Pattern-based |
| **Tests** | Unit tests, integration tests | Follows existing patterns |
| **Terraform** | Resource definitions | Declarative, well-documented |
| **Documentation** | README, API docs | Structured content |
| **Refactoring** | Code cleanup, formatting | Mechanical changes |

### Human-Required Tasks (`ai:human-required`)

| Category | Examples | Why Human Needed |
|:---------|:---------|:-----------------|
| **Console work** | GCP Budget setup, IAM | No API/automation |
| **Secrets** | API keys, tokens | Security-sensitive |
| **Architecture** | ADRs, design decisions | Judgment required |
| **Approvals** | PR merge, releases | Accountability |
| **Debugging** | Production issues | Context needed |
| **Security** | Penetration testing | Expertise required |

---

## Communication Patterns

### AI → Human

| Signal | Mechanism | Human Action |
|:-------|:----------|:-------------|
| "Work complete" | Label: `ai:review-requested` | Review PR |
| "Need help" | Label: `ai:blocked` + comment | Unblock issue |
| "Question" | Issue comment | Respond in comment |

### Human → AI

| Signal | Mechanism | AI Action |
|:-------|:----------|:----------|
| "Work available" | Label: `ai:ready` | Claim and implement |
| "Revision needed" | PR review with requested changes | Revise code based on comments |

---

## Security Boundaries

### AI Access Restrictions

```

                    TRUST BOUNDARY                           

                                                             
  AI CAN ACCESS:                                             
   Public repository code                                 
   Issue content (non-secret)                             
   Documentation                                          
   Test fixtures (non-production data)                    
                                                             
  AI CANNOT ACCESS:                                          
   GCP service account keys                               
   API tokens (except via environment)                    
   Production databases                                   
   Customer data                                          
   Billing account credentials                            
                                                             

```

### Human Oversight Requirements

| Action | Oversight Level |
|:-------|:----------------|
| AI writes code | Round-based governance gates before merge |
| AI creates PR | Merge allowed only after gate pass (plus branch protection requirements) |
| AI modifies config | Security review |
| Any production change | Human approves execution and validates outcome |

---

## Summary

### Division of Labor

| Aspect | Human | AI |
|:-------|:------|:---|
| **Planning** | Owns | Assists with research |
| **Specification** | Owns | Reads and follows |
| **Implementation** | Complex/sensitive tasks | Routine/boilerplate tasks |
| **Review** | Owns escalation and policy decisions | Performs advisory and policy-gated review checks |
| **Deployment** | Approves and governs | Can execute approved CI/CD workflows |
| **Monitoring** | Owns | Cannot access production |

### Key Principles

1. **AI executes within governance policy** - Hermes governs rounds/escalation; humans intervene on escalation or required approvals
2. **Labels are the interface** - AI and humans communicate via issue labels
3. **Project board is human-only** - AI works at repository level
4. **Security is human-enforced** - AI has no access to secrets or production
5. **Accountability is human** - Humans approve and own production outcomes

---

## Related Documents

- [GITHUB_PROJECT_SETUP.md](./github/GITHUB_PROJECT_SETUP.md) - Project board configuration
- [GITHUB_TOOLS_SETUP.md](./github/GITHUB_TOOLS_SETUP.md) - MCP and CLI tool setup
- [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md) - Task completion criteria
- [AI_TIME_ESTIMATION.md](./AI_TIME_ESTIMATION.md) - AI vs human time estimates

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 1.0 | {DATE} | Initial document |
| 1.1 | {DATE} | Added status labels (`status:planning`, `status:implementing`) and scope labels (`scope:mandatory`, `scope:optional`) |
| 1.2 | {DATE} | Added `status:suspended` label |
| 1.4 | {DATE} | Clarified AI can update board status via gh CLI GraphQL (not MCP); added PR Review Labels section; fixed Slack→Teams reference |
| 1.3 | {DATE} | Simplified AI workflow to 5 practical labels; removed `ai:approved`/`ai:rejected` |
