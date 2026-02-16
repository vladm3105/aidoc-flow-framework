# Roles and Tools Guide

**Project**: {PROJECT_NAME} (`{PROJECT_PREFIX}`)
**Document Type**: Governance
**Last Updated**: {DATE}

---

## Overview

This document defines the roles, responsibilities, and tools used by **humans** and **AI assistants** in the project. Understanding these boundaries ensures efficient collaboration and clear accountability.

---

## Quick Reference Matrix

| Capability | Human | AI ({AI_TOOL_NAME} Code) |
|:-----------|:-----:|:----------------:|
| **GitHub Repository** |
| Create/read issues | ✅ | ✅ (MCP) |
| Update issue labels | ✅ | ✅ (MCP) |
| Create branches | ✅ | ✅ (MCP) |
| Push code | ✅ | ✅ (MCP) |
| Create/merge PRs | ✅ | ✅ Create / ❌ Merge |
| Approve PRs | ✅ | ❌ |
| **GitHub Project Board** |
| View project board (UI) | ✅ | ❌ |
| Update board status (GraphQL) | ✅ | ✅ (gh CLI) |
| Update custom fields (UI) | ✅ | ❌ |
| Create/edit views | ✅ | ❌ |
| Move cards (UI) | ✅ | ❌ |
| **GCP Console** |
| Create budgets | ✅ | ❌ |
| Enable billing export | ✅ | ❌ |
| IAM permissions | ✅ | ❌ |
| **Code & Infrastructure** |
| Write application code | ✅ | ✅ |
| Write Terraform | ✅ | ✅ |
| Write tests | ✅ | ✅ |
| Review code | ✅ | ❌ (advisory only) |
| Deploy to production | ✅ | ❌ |
| **Decision Making** |
| Architecture decisions | ✅ | ❌ (research only) |
| Technology selection | ✅ | ❌ (research only) |
| Release approval | ✅ | ❌ |

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
✅ CAN DO:
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

❌ CANNOT DO:
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
   └─► list_issues(labels=["ai:ready"])

2. CLAIM ISSUE
   └─► issue_write(labels=["ai:in-progress"])

3. UNDERSTAND REQUIREMENTS
   └─► Read issue body, linked docs

4. IMPLEMENT
   └─► create_branch("ai/{issue}-{slug}")
   └─► Write code, tests
   └─► push_files(branch, files)

5. CREATE PR
   └─► create_pull_request(head, base, title, body)

6. REQUEST REVIEW
   └─► issue_write(labels=["ai:review-requested"])

7. WAIT FOR HUMAN
   └─► Human reviews, approves/rejects
```

---

## Tool Access Comparison

### GitHub Tools

```
┌────────────────────────────────────────────────────────────────┐
│                    GITHUB ECOSYSTEM                            │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  REPOSITORY LAYER (AI + Human)                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                                                          │ │
│  │  Issues ◄──────► Labels ◄──────► Branches ◄──────► PRs   │ │
│  │    │                │                │              │    │ │
│  │    │    ┌───────────┴───────────┐    │              │    │ │
│  │    │    │   AI ACCESS (MCP)     │    │              │    │ │
│  │    │    │   - list_issues       │    │              │    │ │
│  │    │    │   - issue_write       │    │              │    │ │
│  │    │    │   - create_branch     │    │              │    │ │
│  │    │    │   - push_files        │    │              │    │ │
│  │    │    │   - create_pull_req   │    │              │    │ │
│  │    │    └───────────────────────┘    │              │    │ │
│  │    │                                  │              │    │ │
│  └────┼──────────────────────────────────┼──────────────┼────┘ │
│       │                                  │              │      │
│       │    ┌─────────────────────────────┴──────────────┘      │
│       │    │                                                   │
│  PROJECT LAYER (Human Only)                                    │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                                                         │  │
│  │  Board ◄────► Views ◄────► Custom Fields ◄────► Roadmap │  │
│  │                                                         │  │
│  │    ┌─────────────────────────────────────────────┐     │  │
│  │    │   HUMAN ACCESS ONLY                         │     │  │
│  │    │   - gh CLI (GraphQL)                        │     │  │
│  │    │   - GitHub Web UI                           │     │  │
│  │    │   - No MCP tools available                  │     │  │
│  │    └─────────────────────────────────────────────┘     │  │
│  │                                                         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### GCP Tools

```
┌────────────────────────────────────────────────────────────────┐
│                      GCP ECOSYSTEM                             │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  INFRASTRUCTURE AS CODE (AI + Human)                           │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                                                          │ │
│  │  Terraform ◄──► Python Code ◄──► Config Files            │ │
│  │                                                          │ │
│  │  AI can WRITE these files, but CANNOT APPLY them         │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                           │                                    │
│                           ▼                                    │
│  GCP CONSOLE / CLI (Human Only)                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                                                          │ │
│  │  Billing ◄──► IAM ◄──► APIs ◄──► Resources               │ │
│  │                                                          │ │
│  │  - Create budgets (Console)                              │ │
│  │  - Enable billing export (Console)                       │ │
│  │  - terraform apply (CLI)                                 │ │
│  │  - gcloud commands (CLI)                                 │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
└────────────────────────────────────────────────────────────────┘
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
| `ai:review-requested` | AI | Human | AI done, PR ready for review |
| `ai:human-required` | Human | Human | Not suitable for AI |

**Workflow:**
```
ai:ready → ai:in-progress → ai:review-requested → (merge PR)
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
┌─────────────────────────────────────────────────────────────────┐
│                      TASK LIFECYCLE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. SPECIFICATION (Human)                                       │
│     └─► Create issue with acceptance criteria                   │
│     └─► Add labels: type, priority, component                   │
│     └─► Add to milestone                                        │
│     └─► Set project fields (Size, etc.) ◄── Project Board       │
│     └─► Add label: ai:ready (or ai:human-required)              │
│                         │                                       │
│                         ▼                                       │
│  2. IMPLEMENTATION                                              │
│     ┌─────────────────────────────────────────────────────┐    │
│     │  IF ai:ready          │  IF ai:human-required       │    │
│     │  ─────────────────    │  ────────────────────       │    │
│     │  AI claims issue      │  Human implements           │    │
│     │  AI writes code       │  Human writes code          │    │
│     │  AI creates PR        │  Human creates PR           │    │
│     │  AI requests review   │  Human requests review      │    │
│     └─────────────────────────────────────────────────────┘    │
│                         │                                       │
│                         ▼                                       │
│  3. REVIEW (Human)                                              │
│     └─► Review PR diff                                          │
│     └─► Check acceptance criteria                               │
│     └─► Approve or request changes                              │
│                         │                                       │
│                         ▼                                       │
│  4. MERGE & DEPLOY (Human)                                      │
│     └─► Merge PR                                                │
│     └─► CI/CD runs automatically                                │
│     └─► Human verifies deployment                               │
│     └─► Close issue                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
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
┌─────────────────────────────────────────────────────────────┐
│                    TRUST BOUNDARY                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  AI CAN ACCESS:                                             │
│  ├── Public repository code                                 │
│  ├── Issue content (non-secret)                             │
│  ├── Documentation                                          │
│  └── Test fixtures (non-production data)                    │
│                                                             │
│  AI CANNOT ACCESS:                                          │
│  ├── GCP service account keys                               │
│  ├── API tokens (except via environment)                    │
│  ├── Production databases                                   │
│  ├── Customer data                                          │
│  └── Billing account credentials                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Human Oversight Requirements

| Action | Oversight Level |
|:-------|:----------------|
| AI writes code | Review before merge |
| AI creates PR | Approval required |
| AI modifies config | Security review |
| Any production change | Human executes |

---

## Summary

### Division of Labor

| Aspect | Human | AI |
|:-------|:------|:---|
| **Planning** | Owns | Assists with research |
| **Specification** | Owns | Reads and follows |
| **Implementation** | Complex/sensitive tasks | Routine/boilerplate tasks |
| **Review** | Owns | Cannot review |
| **Deployment** | Owns | Cannot deploy |
| **Monitoring** | Owns | Cannot access production |

### Key Principles

1. **AI is a tool, not a decision-maker** - Humans approve all changes
2. **Labels are the interface** - AI and humans communicate via issue labels
3. **Project board is human-only** - AI works at repository level
4. **Security is human-enforced** - AI has no access to secrets or production
5. **Accountability is human** - Humans merge, deploy, and own outcomes

---

## Related Documents

- [GITHUB_PROJECT_SETUP_AI_FIRST.md](./GITHUB_PROJECT_SETUP_AI_FIRST.md) - Project board configuration
- [GITHUB_TOOLS_SETUP.md](./GITHUB_TOOLS_SETUP.md) - MCP and CLI tool setup
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
