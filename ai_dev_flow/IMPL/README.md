---
title: "Implementation Plans (IMPL): Project Management Layer"
tags:
  - index-document
  - layer-8-artifact
  - shared-architecture
custom_fields:
  document_type: readme
  artifact_type: IMPL
  layer: 8
  priority: shared
---

# Implementation Plans (IMPL): Project Management Layer

## Purpose

Implementation Plans (IMPL) are **project management documents** that organize and coordinate development work between requirements and technical specifications. They answer **WHO does WHAT and WHEN**, not HOW to build it.

**Key Role**: IMPL Plans bridge the gap between business requirements (REQ) and technical implementation by organizing work into phases, assigning teams, and scheduling deliverables.

## Position in Document Workflow

**⚠️ See [../index.md](../index.md#traceability-flow) for the authoritative workflow visualization.**


**⚠️ See for the full document flow: [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)**


> **Note on Diagram Labels**: The above flowchart shows the sequential workflow. For formal layer numbers used in cumulative tagging, always reference the 16-layer architecture (Layers 0-15) defined in README.md. Diagram groupings are for visual clarity only.

## What IMPL Plans Are

IMPL Plans are **project management documents** that:

✅ **Break down requirements** into work packages and phases
✅ **Assign responsibilities** to teams, agents, or individuals
✅ **Set timelines** and milestones
✅ **Define deliverables** (which CTRs, SPECs, TASKS to create)
✅ **Identify dependencies** between work packages
✅ **Track project risks** (resource availability, timeline risks)
✅ **Organize work sequence** for efficient execution

**Analogy**: IMPL Plan = **Project Manager's Timeline**

## What IMPL Plans Are NOT

IMPL Plans do **NOT** define:

❌ **Technical architecture** (that's ADR)
❌ **Data structures or algorithms** (that's SPEC)
❌ **API contracts** (that's CTR)
❌ **Code implementation steps** (that's TASKS)
❌ **Class hierarchies or state machines** (that's SPEC)
❌ **Integration patterns** (that's ADR/SPEC)

**IMPL Plans organize work; they don't design systems.**

## IMPL vs Other Document Types

| Document Type | Purpose | Analogy | Focus |
|--------------|---------|---------|-------|
| **REQ** | Business requirements | Product Owner's vision | WHAT to build |
| **IMPL** | Project management | Project Manager's timeline | WHO does WHAT, WHEN |
| **CTR** | API contracts | Service agreement | Interface definitions |
| **SPEC** | Technical blueprint | Architect's design | HOW to build (YAML) |
| **TASKS** | Code generation plan | Developer's TODO list | SPEC → Code steps |
| **ADR** | Architecture decisions | Design rationale | WHY we chose this approach |

### IMPL vs TASKS: Key Distinction

This is the most critical distinction:

| Aspect | IMPL Plans | TASKS |
|--------|-----------|-------|
| **Level** | High-level (multi-component) | Low-level (single SPEC) |
| **Scope** | Entire system or feature | One YAML specification |
| **Audience** | Project managers, architects | AI code generators, developers |
| **Content** | Phases, teams, deliverables | Exact code generation steps |
| **Granularity** | "Phase 1: Build Resource Management (Week 1-2)" | "Step 3: Generate ResourceLimitService class from SPEC-03.yaml" |
| **Timeline** | Weeks or months | Hours or days |
| **Deliverables** | List of CTR/SPEC/TASKS to create | Source code files |
| **Traceability** | IMPL → CTR, SPEC, TASKS | TASKS → Code |

**Example Flow**:
1. **REQ-NN**: "System must enforce resource limits"
2. **IMPL-NN**: "Resource Management System" - Phase 1: Build resource limits (Week 1-2, Agent Team) → Deliverables: CTR-NN, SPEC-NN, TASKS-NN
3. **SPEC-NN.yaml**: Technical spec with ResourceLimitService class, methods, algorithms
4. **TASKS-NN**: Step-by-step TODOs to generate code from SPEC-NN.yaml
5. **Code**: `resource_limit_service.py` generated following TASKS-NN

## When to Create IMPL Plans

Create an IMPL Plan when:

✅ **Multi-component systems**: Feature requires multiple CTRs/SPECs
✅ **Phased rollout**: Work must be done in stages
✅ **Multiple teams**: Different teams working on related components
✅ **Complex dependencies**: Components must be built in specific order
✅ **Large scope**: Project spans multiple sprints or weeks
✅ **Resource coordination**: Need to allocate people/teams to work packages

**Rule of Thumb**: If implementing a requirement requires creating 3+ SPEC files or coordinating 2+ teams, create an IMPL Plan.

## IMPL Plan Structure

IMPL Plans follow a **4-part structure** (adapted from ADR-TEMPLATE.md):

### PART 1: Project Context and Strategy
- **Overview**: What system/feature is being built (from REQ)
- **Business Objectives**: References to REQ-IDs
- **Scope**: Work packages included/excluded
- **Document Flow**: Position in development workflow

### PART 2: Phased Implementation
- **Phase 1, 2, ... N**: Work breakdown
  - Deliverables: CTR-NN, SPEC-NN, TASKS-NN to create
  - Teams/agents responsible
  - Timeline estimates
  - Dependencies

### PART 3: Project Management and Risk
- **Resource Allocation**: Teams, people, agents
- **Timeline and Milestones**: When things happen
- **Dependencies and Blockers**: What must complete first
- **Risk Register**: Project risks (timeline, resources, scope)
- **Communication Plan**: Status updates, stakeholders

### PART 4: Tracking and Completion
- **Deliverables Checklist**: All CTR/SPEC/TASKS to create
- **Acceptance Criteria**: Project completion definition
- **Sign-off Process**: Who approves completion

## File Naming Convention

**Pattern**: `IMPL-NN_{system_name}.md`

**Examples**:
- `IMPL-01_risk_management_system.md`
- `IMPL-02_external_data_integration.md`
- `IMPL-03_service_orchestrator_agent.md`

**ID Format**: `IMPL-NN` where NN is the sequence number (01, 02, ...)

## Traceability Requirements

### Upstream (What IMPL Plans Reference)

IMPL Plans trace to:
- **REQ-NN**: Business requirements being implemented
- **ADR-NN**: Architecture decisions affecting work organization
- **SYS-NN**: System requirements driving implementation

### Downstream (What IMPL Plans Produce)

IMPL Plans identify deliverables:
- **CTR-NN**: API contracts to be created
- **SPEC-NN**: Technical specifications to be written
- **TASKS-NN**: Code generation plans to be developed

**Note**: IMPL Plans do NOT directly produce code. They organize the creation of technical documents (CTR/SPEC/TASKS) which eventually lead to code.

## Directory Organization

```
ai_dev_flow/IMPL/
├── README.md                          # This file
├── IMPL-000_index.md                  # Master index of all IMPL plans
├── IMPL-TEMPLATE.md                   # Template for new IMPL plans
├── IMPL_IMPLEMENTATION_PLAN.md        # Example: Plan for creating IMPL/ system
└── examples/                          # Reference examples
    └── IMPL-01_risk_management_system.md
```

## Quality Gates

Before completing an IMPL Plan, verify:

- [ ] **Scope Clear**: All work packages identified
- [ ] **Phases Defined**: Work broken into logical phases
- [ ] **Teams Assigned**: Responsibilities clear
- [ ] **Timeline Realistic**: Estimates based on capacity
- [ ] **Dependencies Mapped**: Blockers identified
- [ ] **Deliverables Listed**: All CTR/SPEC/TASKS enumerated
- [ ] **Risks Assessed**: Project risks identified with mitigations
- [ ] **Traceability Complete**: Links to REQ/ADR/SYS
- [ ] **Token Limit**: See [AI_TOOL_OPTIMIZATION_GUIDE.md](../AI_TOOL_OPTIMIZATION_GUIDE.md) for assistant-specific token guidance and file handling.

## Writing Guidelines

### Focus on Organization, Not Implementation

**Good** (Project Management):
```markdown
## Phase 1: Resource Limit Service (Week 1-2)

**Team**: Agent Development Team (3 developers)

**Deliverables**:
- CTR-NN: API Contract
- SPEC-NN: Service Specification
- TASKS-NN: Code Generation Plan for SPEC-NN

**Dependencies**:
- Database schema approved (ADR-NN)
- Parameter configuration complete (REQ-NN)

**Timeline**: Sprint 1 (2 weeks)
```

**Bad** (Technical Implementation - belongs in SPEC):
```markdown
## Phase 1: Resource Limit Service

The ResourceLimitService class will implement a Redis-backed cache with
TTL of 60 seconds. The calculate_resource_limit() method uses the formula:
limit = base_limit * (1 - risk_factor * 0.1)
```

### Organize by Work Packages, Not Technical Layers

**Good** (Business Value):
```markdown
## Phase 1: Core Resource Management (Sprint 1-2)
- Resource limits (CTR-NN, SPEC-NN)
- Risk calculator (CTR-NN, SPEC-NN)

## Phase 2: Advanced Features (Sprint 3)
- Circuit breakers (CTR-NN, SPEC-NN)
- Correlation analysis (CTR-NN, SPEC-NN)
```

**Bad** (Technical Layers):
```markdown
## Phase 1: Data Layer
- All database models

## Phase 2: Service Layer
- All business logic

## Phase 3: API Layer
- All endpoints
```

## Common Patterns

### Pattern 1: Sequential Phases

When components must be built in order:

```markdown
## Phase 1: Foundation (Week 1-2)
- Core data models (SPEC-NN, SPEC-NN)
- Database setup (SPEC-NN)

## Phase 2: Services (Week 3-4)
- Business logic (SPEC-NN, SPEC-NN)
- Depends on: Phase 1 complete

## Phase 3: Integration (Week 5)
- API layer (SPEC-NN)
- Depends on: Phase 2 complete
```

### Pattern 2: Parallel Development

When teams can work independently:

```markdown
## Phase 1 (Parallel): Core Services (Week 1-2)

**Team A**: Resource Limits
- CTR-NN, SPEC-NN, TASKS-NN

**Team B**: Risk Calculator
- CTR-NN, SPEC-NN, TASKS-NN

**Team C**: Circuit Breakers
- CTR-NN, SPEC-NN, TASKS-NN

No dependencies between teams.
```

### Pattern 3: Iterative Delivery

When delivering incremental value:

```markdown
## Phase 1: MVP (Sprint 1)
- Basic resource limits (SPEC-NN)
- Manual override capability (SPEC-NN)
- **Release**: V1.0 to production

## Phase 2: Enhancements (Sprint 2)
- Automated calculation (SPEC-NN)
- Real-time monitoring (SPEC-NN)
- **Release**: V1.1 to production

## Phase 3: Advanced Features (Sprint 3)
- ML-based recommendations (SPEC-NN)
- **Release**: V2.0 to production
```

## Integration with Workflow

### From Requirements to IMPL

After requirements (REQ) are approved:

1. **Review Requirements**: Understand WHAT needs to be built
2. **Create IMPL Plan**: Organize WHO will build WHAT and WHEN
3. **Identify Deliverables**: List all CTR/SPEC/TASKS needed
4. **Assign Teams**: Allocate resources to work packages
5. **Set Timeline**: Estimate phase durations
6. **Get Approval**: Review IMPL Plan with stakeholders

### From IMPL to Technical Specs

IMPL Plan guides creation of:

1. **CTR Documents**: API contracts for component interfaces
2. **SPEC Documents**: YAML specifications for component implementation
3. **TASKS Documents**: Code generation plans for each SPEC

### IMPL as Progress Tracker

Throughout implementation:

- **Update Status**: Mark phases as complete
- **Track Deliverables**: Link to created CTR/SPEC/TASKS
- **Adjust Timeline**: Update estimates based on actuals
- **Manage Risks**: Update risk register as issues arise

## Benefits

### For Project Managers
- **Clear Timeline**: Know when deliverables are due
- **Resource Visibility**: See who's working on what
- **Dependency Management**: Identify blockers early
- **Progress Tracking**: Monitor completion against plan

### For Architects
- **Phased Design**: Break complex systems into manageable pieces
- **Team Coordination**: Ensure teams don't duplicate work
- **Integration Planning**: Identify integration points early

### For Developers
- **Work Organization**: Understand where their work fits
- **Dependency Clarity**: Know what they're waiting for
- **Deliverable Focus**: Clear goals (create SPEC-NN, TASKS-NN)

### For AI Assistants
- **Structured Guidance**: Clear roadmap for feature implementation
- **Deliverable Checklist**: Know what documents to create
- **Phase Context**: Understand current implementation stage

## Avoiding Pitfalls

### Pitfall 1: IMPL Becomes Technical Spec

**Problem**: IMPL Plan includes data structures, algorithms, class hierarchies

**Solution**: Move technical details to SPEC. IMPL only says "create SPEC-NN for the service"

### Pitfall 2: IMPL Duplicates TASKS

**Problem**: IMPL Plan lists exact code generation steps

**Solution**: IMPL references TASKS documents. Only TASKS contains code generation TODOs.

### Pitfall 3: IMPL Too Granular

**Problem**: IMPL Plan has 50 phases, each 2 hours long

**Solution**: Group related work into logical phases (1-2 weeks each). Save granularity for TASKS.

### Pitfall 4: IMPL Missing Deliverables

**Problem**: Phase says "Build resource management" but doesn't list which CTR/SPEC/TASKS

**Solution**: Always enumerate deliverables: "CTR-NN, SPEC-NN, TASKS-NN"

### Pitfall 5: No Team [ALLOCATION - e.g., task assignment, resource allocation]

**Problem**: Phases don't specify who does the work

**Solution**: Assign teams/people: "Agent Development Team" or "AI Code Generator"

## Tools

### Template Usage

Start with `IMPL-TEMPLATE.md`:

```bash
cp ai_dev_flow/IMPL/IMPL-TEMPLATE.md \
   docs/IMPL/IMPL-NN_my_feature.md
```

### Validation

Check IMPL Plan quality:

- **Traceability**: All REQ-NN references valid?
- **Deliverables**: All CTR/SPEC/TASKS enumerated?
- **Timeline**: Realistic estimates?
- **Dependencies**: Blockers identified?
- **Token Limit**: See [AI_TOOL_OPTIMIZATION_GUIDE.md](../AI_TOOL_OPTIMIZATION_GUIDE.md) for assistant-specific token guidance.

## Examples

### Example 1: Simple IMPL (Single Team)

```markdown
# IMPL-NN: Authentication System

## PART 1: Project Context
**Overview**: Implement OAuth2 authentication for API access

**Business Objectives**: REQ-NN (Secure access)

**Scope**:
- OAuth2 provider integration
- Token management
- User session handling

## PART 2: Phased Implementation

### Phase 1: Core Auth (Week 1)
**Deliverables**:
- CTR-NN: Authentication API Contract
- SPEC-NN: Service Specification
- TASKS-NN: Code Generation Plan

**Team**: security Team (2 developers)
**Dependencies**: None

### Phase 2: Session Management (Week 2)
**Deliverables**:
- SPEC-NN: Session Service Specification
- TASKS-NN: Code Generation Plan

**Team**: security Team
**Dependencies**: Phase 1 complete

## PART 3: Project Management
**Timeline**: 2 weeks total
**Risk**: OAuth2 provider downtime → Mitigation: Local testing mode

## PART 4: Completion
**Acceptance**: All auth flows tested, security review passed
```

### Example 2: Complex IMPL (Multiple Teams)

See: `examples/IMPL-01_risk_management_system.md`

## Related Documents

- **IMPL-000_index.md**: Master index of all IMPL plans
- **IMPL-TEMPLATE.md**: Template for new IMPL plans
- **TASKS README**: Understanding code generation plans (TASKS/README.md)
- **SPEC_DRIVEN_DEVELOPMENT_GUIDE.md**: Full workflow including IMPL
- **TRACEABILITY.md**: How IMPL fits in traceability chain

## Quick Reference

| Question | Answer |
|----------|--------|
| When to create IMPL? | Multi-component features, phased rollout, multiple teams |
| What goes in IMPL? | Phases, teams, timeline, deliverables (CTR/SPEC/TASKS) |
| What NOT in IMPL? | Data structures, algorithms, code generation steps |
| IMPL vs TASKS? | IMPL = project plan (WHO/WHEN), TASKS = code plan (HOW) |
| Upstream? | REQ, ADR, SYS |
| Downstream? | CTR, SPEC, TASKS (as deliverables) |

---

**Template Version**: 1.0
**Last Reviewed**: 2025-11-02
**Next Review**: 2026-02-02 (quarterly)
