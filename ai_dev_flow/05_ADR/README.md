---
title: "Architecture Decision Records (ADRs)"
tags:
  - index-document
  - layer-5-artifact
  - shared-architecture
custom_fields:
  document_type: readme
  artifact_type: ADR
  layer: 5
  priority: shared
---

# Architecture Decision Records (ADRs)

## Generation Rules

- Index-only: maintain `ADR-00_index.md` as the authoritative plan and registry (mark planned items with Status: Planned).
- Templates: default to the MVP template; use the full (sectioned) template only when explicitly set in project settings or clearly requested in the prompt.
- Inputs used for generation: `ADR-00_index.md` + selected template profile; no skeletons are used.
- Example index: `ai_dev_flow/tmp/SYS-00_index.md`.

Architecture Decision Records (ADRs) document significant architectural decisions, their context, consequences, and the rationale for choosing one approach over alternatives. ADRs create a historical record of how and why architectural choices were made, enabling teams to understand design decisions years later and avoid repeating past mistakes.

## Available Templates

**ADR-MVP-TEMPLATE.md** (default) - Streamlined MVP version in a single file without sectioning (~250 lines)
- Focused on decision + rationale + 2-3 alternatives
- Maintains framework compliance while reducing documentation overhead
- Ideal for MVP architecture decisions with quick turnaround

Full template is archived; stay on MVP unless an enterprise/full template is explicitly required.

## Purpose

ADRs serve as the **architectural foundation** that:

- **Document Decisions**: Capture important architectural choices with full context and reasoning
- **Explain Rationale**: Record why alternatives were rejected and trade-offs accepted
- **Enable Traceability**: Link architectural decisions to business requirements and implementation specifications
- **Facilitate Knowledge Transfer**: Help new team members understand how systems evolved and why design choices were made
- **Support Future Changes**: Provide decision history to inform future architectural evolution

## Foundation ADRs

Foundation ADRs establish project-wide standards that all other ADRs must reference:

### ADR-000: Technology Stack
**Location**: [ADR-00_technology_stack.md](ADR-00_technology_stack.md)

**Purpose**: Single source of truth for all technology decisions across the entire options [SYSTEM_TYPE - e.g., inventory system, booking system].

**Scope**: Defines approved technologies for:
- Agent Framework (Google ADK, MCP, A2A Protocol)
- Cloud Infrastructure (GCP primary, Azure/AWS multi-cloud)
- Programming Languages (Python 3.11+, TypeScript)
- Backend/Frontend (FastAPI, React 18, Next.js 14)
- Infrastructure as Code (Terraform, Flyway, GitHub Actions)
- Monitoring, security, and Compliance standards

**When to Reference ADR-000**:
- ✅ **Before proposing new technologies**: Check if technology is already approved in ADR-000
- ✅ **When writing new ADRs**: Include "Technology Stack Compliance" section (see ADR-TEMPLATE.md)
- ✅ **When creating specifications**: Ensure SPEC technologies align with ADR-000
- ✅ **If proposing technology not in ADR-000**: Document justification and recommend updating ADR-000

**Future Foundation ADRs** (referenced but not yet created):
- **ADR-01**: Google ADK Framework - Agent orchestration and lifecycle management
- **ADR-02**: Model Context Protocol (MCP) - Tool integration standard for agent capabilities
- **ADR-03**: Google A2A Protocol - Agent-to-agent communication patterns
- **ADR-004**: Multi-Cloud Architecture - GCP primary with Azure/AWS disaster recovery

**Technology Stack Compliance**:
Every ADR proposing new technologies must include a "Technology Stack Compliance" section demonstrating:
1. Technology aligns with ADR-000 approved stack, OR
2. Justification for why existing stack cannot meet requirements
3. Evaluation against alternatives already in ADR-000
4. Integration impact and migration plan
5. Recommendation to update ADR-000 if new technology is adopted

See [ADR-TEMPLATE.md](ADR-TEMPLATE.md) for the complete compliance section template.

## Position in Document Workflow

**⚠️ See [../index.md](../index.md#traceability-flow) for the authoritative workflow visualization.**

ADR is in the **Architecture Layer** within the complete SDD workflow:

**Business Layer** (BRD → PRD → EARS) → **Testing Layer** (BDD) → **Architecture Layer** (ADR → SYS) ← **YOU ARE HERE** → **Requirements Layer** (REQ) → **Project Management Layer** (IMPL) → **Interface Layer** (CTR - optional) → **Technical Specs (SPEC)** → **Code Generation Layer** (TASKS) → **Execution Layer** (Code → Tests) → **Validation Layer** (Validation → Review → Production)

**Key Points**:
- **Upstream**: BDD (Behavior-Driven Development scenarios)
- **Downstream**: SYS (System Requirements Specification)
- **Decision Point**: After IMPL, CTR is created if the requirement specifies an interface; otherwise, proceed directly to SPEC

For the complete workflow diagram with all relationships and styling, see [index.md](../index.md#traceability-flow).

## ADR File Creation Order: Prerequisites and Sequence

ADRs should be created **after** business and technical requirements are gathered but **before** detailed implementation specifications and code development begins. This ensures architectural decisions are grounded in solid requirements and address stated business goals.

### When to Create ADRs

ADRs should be created **immediately after** initial requirements and BDD scenarios are established but **before** system specifications and implementation plans:

**⚠️ See for the full document flow: [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)**

```text
Requirements (02_PRD/EARS) → BDD Scenarios ← ADR Decision → 06_SYS/10_SPEC/Implementation
                                          ↓
                                  Architectural Validation
```

#### Development Workflow Timing

1. **Before ADR**: Requirements gathering is complete; business goals and technical constraints are understood
2. **Create ADR**: Architecture team crafts ADR documenting the chosen solution, alternatives considered, and implementation approach
3. **Review ADR**: Technical leads, architects, and stakeholders review and approve the architectural approach
4. **After ADR**: System requirements, specifications, and implementation plans are based on ADR decisions

### Prerequisites for ADR Creation

#### ✅ **Must Exist Before ADR Creation**

- **Business Requirements (PRD)**: Clear understanding of business problems and goals
- **Technical Requirements (EARS)**: Atomic, measurable requirements in WHEN/THEN format
- **Behavioral Scenarios (BDD)**: Concrete scenarios defining expected system behavior
- **Constraints and Driving Forces**: Understanding of performance, cost, compliance, and operational constraints
- **Problem Context**: Clear definition of the architectural problem being solved

#### ✅ **Should Exist Before ADR Creation**

- **Existing System Architecture**: Understanding of current state and legacy systems
- **Technology Landscape**: Knowledge of available technologies and tools
- **Team Capabilities**: Understanding of team skills and available expertise
- **Risk Assessment**: Preliminary identification of key risks and concerns

#### ❌ **Should NOT Be Started Before ADR**

- **Detailed System Specifications**: ADRs focus on architectural decisions, not implementation details
- **Code Implementation**: ADRs establish constraints and direction for code, not the code itself
- **Database Schemas**: ADRs specify architecture, not data structures (saved for specifications)
- **DevOps Infrastructure**: ADRs may reference infrastructure patterns, but detailed deployment is separate

### File Dependencies and Sequence

```text
1. PRD-NN.md (Product Requirements)     ← Foundation documents
2. EARS-NN.md (Technical Requirements)  ← Prerequisite - provides atomic requirements
3. `04_BDD/BDD-NN_{suite}/BDD-NN.SS_{slug}.feature` (Behavior Scenarios)  ← Prerequisite - defines expected behaviors
4. ADR-NN.md (Architecture Decision)    ← Created from steps 1-3
5. SYS-NN.md (System Requirements)      ← Uses ADR decisions as constraints
6. REQ-NN.md (Atomic Requirements)      ← Implements ADR at granular level
7. SPEC-NN.yaml (Technical Specs)       ← Detailed implementation of ADR
8. TASKS-NN.md (Implementation Plans)   ← Based on ADR and SPEC
9. Code Implementation                   ← Validates against ADR constraints
```

### Critical Success Factors

#### Architecture Readiness

- **Architecture Team Available**: Experienced architects must be involved in ADR creation
- **Technology Knowledge**: Team must understand available technologies and trade-offs
- **Decision Authority**: Clear accountability for approving architectural decisions
- **Risk Tolerance**: Understanding of business acceptance of architectural risks

#### Business Readiness

- **Requirements Stability**: Core business requirements should be stable before major architectural commitments
- **Stakeholder Agreement**: Key stakeholders must accept the architectural approach and its trade-offs
- **Resource Commitment**: Resources must be available to implement architectural decisions

#### Technical Readiness

- **Proof of Concepts**: Complex architectural decisions should be validated with POCs
- **Technology Maturity**: Selected technologies should be evaluated for production readiness
- **Team Capability**: Team must possess or be able to acquire necessary technical skills
- **Integration Planning**: Impact on existing systems and integration points understood

## Platform vs Feature BRD Context

ADRs have different relationships with Platform BRDs versus Feature BRDs:

**Platform BRDs → Foundation ADRs**:
- Platform BRDs (e.g., BRD-01 Platform Architecture) inform Foundation ADRs
- Foundation ADR-000 documents technology stack decisions that enable platform capabilities
- Platform BRDs define "what" the platform must do; Foundation ADRs document "how" through technology choices
- Typically created together at project inception

**Feature BRDs → Feature-Specific ADRs**:
- Feature BRDs (e.g., BRD-06 B2C Identity Verification Onboarding) drive architectural decisions for specific features
- Feature ADRs build upon foundation established by Platform BRDs and Foundation ADRs
- Address feature-specific architectural concerns (e.g., API design, data models, integration patterns)
- Reference Foundation ADRs for technology stack and infrastructure decisions

**ADR File Creation Order**:
1. **Foundation ADRs** (informed by Platform BRDs)
   - ADR-000: Technology stack and infrastructure decisions
   - Cross-cutting architectural patterns and standards

2. **Feature-Specific ADRs** (driven by Feature BRDs)
   - Created as needed for each feature
   - Build upon foundation established in step 1
   - Reference both Platform BRDs and Foundation ADRs

**Reference**: See [PLATFORM_VS_FEATURE_BRD.md](../PLATFORM_VS_FEATURE_BRD.md) for BRD categorization methodology

## ADR Structure

### Header with Traceability Tags

All ADRs include mandatory traceability linking to upstream and downstream artifacts:

```markdown
# ADR-NN: Descriptive Title

@PRD:[PRD-NN](../02_PRD/PRD-NN_descriptive_title.md)
@EARS:[EARS-NN](../03_EARS/EARS-NN_descriptive_title.md)
@bdd:[BDD-NN.SS:scenarios](../04_BDD/BDD-NN_{suite}/BDD-NN.SS_{slug}.feature#scenarios)

@SYS:[SYS-NN](../06_SYS/SYS-NN_descriptive_title.md)
@requirement:[REQ-NN](../07_REQ/infrastructure/REQ-NN_descriptive_title.md#REQ-NN)
@spec:[spec-name.yaml](../10_SPEC/compute/spec-name.yaml)
```

### Four-Part Structure

ADRs follow a comprehensive four-part structure:

#### PART 1: Decision Context and Requirements

Establishes the problem, requirements, and decision made:

- **Status**: Proposed/Accepted/Deprecated/Superseded
- **Context**: Problem statement, background, driving forces, constraints
- **Decision**: Chosen solution with key components and implementation approach
- **Requirements Satisfied**: Traceability table showing how ADR addresses each requirement

#### PART 2: Impact Analysis and Architecture

Analyzes consequences and provides architectural details:

- **Consequences**: Positive outcomes, negative outcomes, trade-offs, risks, costs
- **Architecture Flow**: Detailed flow diagrams showing how components interact
- **Implementation Assessment**: Complexity, dependencies, resources, failure modes, rollback plans
- **Compatibility**: Backward/forward compatibility, breaking changes, deprecation strategy
- **Monitoring & Observability**: Success metrics, error tracking, performance baselines
- **Alternatives Considered**: Other approaches evaluated with pros/cons and rejection reasons

#### PART 3: Implementation and Operations

Provides detailed operational guidance:

- **security**: Input validation, authentication, authorization, data protection, compliance
- **Related Decisions**: Dependencies, superseded decisions, related ADRs
- **Implementation Notes**: Development phases, code locations, configuration management
- **Rollback Procedures**: Triggers, steps, impact, feature flags
- **Performance Considerations**: Optimization strategies, caching, data consistency
- **Scalability Considerations**: Horizontal scaling, connection pooling, load balancing

#### PART 4: Traceability and Documentation

Maintains comprehensive traceability:

- **Upstream Sources**: Links to PRD, EARS, BDD that justified the decision
- **Downstream Artifacts**: Links to SYS, REQ, SPEC, implementation code
- **Validation Artifacts**: Test results, security assessments, performance benchmarks
- **References**: Internal links, external documentation, research materials

## File Naming Convention

```markdown
ADR-NN_descriptive_slug.md
```

Where:

- `ADR` is the constant prefix
- `NNN` is the 2+ digit sequence number (01, 02, 003, etc.)
- `descriptive_slug` uses snake_case describing the architectural decision
- `.md` is the mandatory markdown file extension

**Naming Examples:**

- `ADR-01_gcp_cloud_run_deployment.md`: GCP Cloud Run serverless deployment architecture
- `ADR-02_multi_agent_orchestration.md`: Multi-agent system orchestration patterns
- `ADR-03_kubernetes_cluster_management.md`: Kubernetes cluster configuration and management
- `ADR-004_database_layer_design.md`: Multi-database strategy (SQL + NoSQL)
- `ADR-042_ml_model_serving_layer.md`: ML model inference and serving architecture

### Index File

An `ADR-00_index.md` file maintains a central index of all ADRs:

```markdown
# ADR Index

## Purpose
- Central index for ADR documents in this example set
- Tracks allocation and sequencing for `ADR-NN_{slug}.md` files

## Allocation Rules
- Numbering: keep ADR-NN aligned with decisions referenced by this example set
- Include a brief description and cross-links to 07_REQ/02_PRD/03_EARS/10_SPEC/BDD when applicable

## Documents (example set)
- [ADR-033_risk_limit_enforcement_architecture.md](./ADR-033_risk_limit_enforcement_architecture.md)
- [ADR-034_ib_gateway_integration_architecture.md](./ADR-034_ib_gateway_integration_architecture.md)
- [ADR-035_external_api_integration_architecture.md](./ADR-035_external_api_integration_architecture.md)
```

## Decision Status Values

### Proposed

Decision is under review and not yet approved:

```markdown
**Status**: Proposed
**Date**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD
```

- Not yet implemented
- Open for feedback and alternative suggestions
- May be revised based on stakeholder input
- Proceed with caution on implementation

### Accepted

Decision is approved and implementation is underway:

```markdown
**Status**: Accepted
**Date**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD
```

- Fully approved by decision makers
- Implementation actively in progress
- Should be followed in new development
- Establishes architectural constraint for related work

### Deprecated

Decision is no longer recommended but still in use:

```markdown
**Status**: Deprecated
**Date**: YYYY-MM-DD
**Deprecation Notice**: Deprecated in favor of ADR-NN; sunset date: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD
```

- No longer recommended for new development
- Existing implementations should migrate to replacement
- Provides transition period and migration guidance
- Superseded by newer architectural approach

### Superseded

Decision has been completely replaced by another:

```markdown
**Status**: Superseded
**Superseded By**: ADR-NN: Descriptive Title
**Date**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD
```

- Completely replaced by newer decision
- Kept for historical reference and understanding evolution
- Should not be used for new development
- Link to successor ADR for migration path

## Writing Guidelines

### 1. Problem-Focused Context

- **Start with problems**: Begin with the architectural challenge being solved
- **Quantify constraints**: Use specific metrics (performance, cost, scale targets)
- **Explain driving forces**: Why this decision matters now (business, technical, compliance)
- **Reference upstream artifacts**: Link to 02_PRD/03_EARS/BDD that motivated the decision

### 2. Comprehensive Decision Explanation

- **Chosen solution clearly stated**: Unambiguous description of what was selected
- **Key components described**: Important parts and their roles in the solution
- **Implementation approach outlined**: High-level strategy without low-level details
- **Requirements traceability**: Show how decision satisfies stated requirements

### 3. Impact Analysis Depth

- **Positive and negative outcomes**: Both benefits and trade-offs acknowledged
- **Concrete examples**: Illustrate how architecture works with specific scenarios
- **Failure mode coverage**: Identify and plan for potential failure conditions
- **Recovery strategies**: Document how to detect and recover from failures

### 4. Rigorous Alternatives Analysis

- **Multiple alternatives evaluated**: At least 2-3 serious alternatives considered
- **Pros and cons balanced**: Fair comparison showing strengths and weaknesses
- **Rejection reasoning clear**: Specific explanation for why alternatives were not chosen
- **Fit scoring**: Relative ranking (Poor/Good/Better) aids future decision makers

### 5. Maintainability Focus

- **History preserved**: Document describes decision rationale for future reference
- **Structure enables navigation**: Headings and tables support quick scanning
- **Diagram-supported**: Architecture flows shown visually with mermaid diagrams
- **Traceability complete**: Links to upstream and downstream artifacts maintained

## ADR Quality Gates

**Every ADR must include:**

- Clear problem statement with business context and driving forces
- Specific statement of chosen solution and key components
- Requirements satisfaction table showing traceability to 02_PRD/03_EARS/BDD
- At least 2 alternatives considered with rejection reasoning
- Consequences analysis covering positive and negative outcomes
- Architecture flow diagrams showing component interactions
- Implementation assessment including complexity, dependencies, and resources
- Failure modes and recovery strategies
- Rollback procedures and feature flags for safe deployment
- Complete traceability to upstream (02_PRD/03_EARS/BDD) and downstream (06_SYS/07_REQ/SPEC) artifacts

**ADR content standards:**

- Business language for problem statement and consequences
- Technical precision for architecture and implementation details
- Visual diagrams (mermaid flowcharts) for complex interactions
- Tables for comparison (requirements, alternatives, metrics)
- Links that resolve to existing artifacts
- All assumptions and constraints explicitly documented

## Common ADR Patterns

### Infrastructure Architecture ADRs

**Focus**: Deployment, scaling, networking, cloud services

```markdown
## Problem
Current infrastructure cannot scale to support projected transaction volume during peak operating hours.

## Decision
Deploy microservices on Kubernetes with auto-scaling policies based on CPU and request metrics.

## Requirements Satisfied
- Scale from 0-100 instances based on demand
- Maintain p95 latency <100ms during peak load
- Reduce infrastructure cost 40% vs. traditional approach
```

### Integration Architecture ADRs

**Focus**: System-to-system communication, data flows, API contracts

```markdown
## Problem
Manual data synchronization between [SYSTEM_TYPE - e.g., inventory system, booking system] and [EXTERNAL_DATA - e.g., customer data, sensor readings] provider creates operational friction and introduces staleness windows.

## Decision
Implement event-driven architecture with message queue for real-time data propagation.

## Requirements Satisfied
- Eliminate manual data sync operations
- Reduce data staleness from 5 minutes to <1 second
- Enable horizontal scaling of consumer services
```

### Technology Selection ADRs

**Focus**: Choosing between competing frameworks, languages, or platforms

```markdown
## Problem
Current monolithic Python application limits deployment flexibility and scales poorly.

## Decision
Migrate to microservices architecture with per-service technology selection (Python for analysis, Go for orchestration).

## Requirements Satisfied
- Support independent scaling per service type
- Reduce deployment time from 2 hours to 15 minutes
- Enable polyglot development with appropriate tools per service
```

### Data Architecture ADRs

**Focus**: Database selection, data modeling, consistency strategies

```markdown
## Problem
Single database cannot provide both strong consistency for financial records and horizontal scaling for analytics.

## Decision
Multi-database strategy: PostgreSQL for transactional data with strong ACID guarantees, BigQuery for analytics with eventual consistency.

## Requirements Satisfied
- Maintain ACID compliance for critical financial transactions
- Support unlimited scaling for analytics queries
- Reduce analytics query latency from hours to seconds
```

### security Architecture ADRs

**Focus**: Authentication, authorization, encryption, threat models

```markdown
## Problem
Current shared credentials and manual access control creates security risks and audit compliance gaps.

## Decision
Implement role-based access control (RBAC) with centralized identity management and service account tokens.

## Requirements Satisfied
- Achieve SOC 2 audit compliance
- Eliminate shared credentials
- Support fine-grained authorization policies
- Enable audit trail for all access
```

## Creating Your First ADR

### Step 1: Identify the Architectural Decision

- What significant architectural choice are we making?
- Is this important enough to document? (Rule of thumb: If multiple people ask "why did we do this?", it's worth an ADR)
- Are there alternatives we're consciously rejecting?

### Step 2: Gather Requirements Context

- Review related PRD, EARS, and BDD documents
- Understand business drivers and constraints
- Identify stakeholders and decision makers
- Document assumptions and dependencies

### Step 3: Evaluate Alternatives

- Identify at least 2-3 credible alternatives
- Analyze pros and cons for each
- Conduct proof of concept if decision is risky
- Document why each alternative was rejected

### Step 4: Document the Decision

- Write problem statement clearly
- Describe chosen solution with key components
- Create architecture flow diagrams
- Analyze consequences and trade-offs

### Step 5: Establish Traceability

- Link to upstream 02_PRD/03_EARS/BDD
- Link to downstream 06_SYS/07_REQ/SPEC
- Reference code locations
- Update ADR index

### Step 6: Review and Approve

- Technical review by architecture team
- Stakeholder review for business alignment
- Document approval and date
- Plan for communication to wider team

## ADR Evolution and Maintenance

### Initial Creation (Proposed Phase)

Focus on capturing decision with sufficient context for review:

```markdown
**Status**: Proposed
## Context
[Problem statement and driving forces]

## Decision
[Chosen approach]

## Consequences
[Expected outcomes and risks]
```

### Approval Phase (Accepted)

Add implementation details and complete traceability:

```markdown
**Status**: Accepted
## Implementation Assessment
[Complexity, dependencies, resources]

## Traceability
[Links to 06_SYS/07_REQ/SPEC as they're created]
```

### Production Phase (Active Use)

Include monitoring results and operational experience:

```markdown
**Status**: Accepted
**Last Updated**: YYYY-MM-DD

## Implementation Assessment
[Updated with actual performance data]

## Monitoring & Observability
[Actual performance metrics from production]
```

### Deprecation Phase (Deprecated/Superseded)

Document successor and migration path:

```markdown
**Status**: Deprecated
**Superseded By**: ADR-NN: [Title]
**Sunset Date**: YYYY-MM-DD
**Migration Guide**: [How to migrate from this decision]
```

## Benefits of Comprehensive ADRs

1. **Preserved Knowledge**: Decision rationale survives beyond the decision makers
2. **Faster Onboarding**: New team members understand architecture through decision history
3. **Informed Evolution**: Future architectural changes reference past decisions and trade-offs
4. **Risk Awareness**: Documented failure modes and mitigation strategies inform operations
5. **Compliance**: Complete decision record supports regulatory and audit requirements

## Avoiding Common ADR Pitfalls

1. **Implementation Details**: ADRs describe architecture, not code implementation
2. **Incomplete Alternatives**: Analyzing only weak alternatives doesn't justify decisions
3. **Missing Trade-offs**: Every decision has costs; be honest about what you're sacrificing
4. **Vague Consequences**: Quantify impacts ("reduce latency by 40%", not "improve performance")
5. **Broken Links**: Maintain traceability as related documents evolve
6. **Status Neglect**: Update status and dates as decision evolves through lifecycle
7. **Isolated Decisions**: Connect ADRs to upstream business requirements and downstream implementation

## Integration with Development Process

### Pre-Implementation Gate

- ✅ ADR is Accepted status
- ✅ All stakeholders have reviewed and approved
- ✅ Traceability established to 02_PRD/03_EARS/BDD
- ✅ Risks and mitigation strategies documented
- ✅ Rollback procedures planned

### Implementation Phase

- Implement following ADR constraints and assumptions
- Update code with references to ADR decision number
- Document deviations in PR reviews with justification
- Create 06_SYS/07_REQ/SPEC artifacts based on ADR

### Verification Phase

- Validate that implementation satisfies ADR constraints
- Compare actual performance to ADR predictions
- Document any architectural issues discovered
- Update ADR if real-world experience contradicts assumptions

### Operational Phase

- Monitor against ADR success metrics
- Track failure modes and mitigation activations
- Document lessons learned for future ADRs
- Plan deprecation when decision approaches end of life

## Traceability and References

### Why Traceability Matters in AI-First Development

In AI-first development, traceability is critical for:

- **AI Context Understanding**: LLMs and AI agents need complete context to generate accurate implementations; broken traceability chains mean missing requirements or outdated constraints
- **Requirement Validation**: Every ADR decision must connect back to business requirements (PRD) and engineering specifications (03_EARS/BDD) that justified it
- **Change Impact Analysis**: Understanding upstream dependencies helps predict how requirement changes cascade through architecture decisions to code
- **Audit & Compliance**: Complete traceability enables regulatory audits, regulatory reviews, and architectural review boards to understand decision rationale
- **Knowledge Preservation**: Future team members can understand why decisions were made by following the traceability chain
- **Automation**: CI/CD pipelines can validate that implementations satisfy ADR constraints by checking traceability links

## Traceability in ADRs

### Upstream Sources: Why This Decision Was Made

Upstream sources are the **business and technical requirements that justify the ADR decision**. They answer the question: "What drove this architectural choice?"

#### Understanding Upstream Sources

Every ADR must trace back to at least one upstream source establishing business context:

**Business Requirements (PRD-NN):**

- Product Requirements Documents define "what" the business needs
- Example: "System must support concurrent execution of 11 agents with independent scaling"
- ADR links back: This ADR (Cloud Run) specifically addresses the scaling requirement from PRD-01

**Engineering Requirements (EARS-NN):**

- EARS documents specify atomic, measurable requirements in WHEN/THEN format
- Example: "WHEN request queue depth exceeds 50 THEN system SHALL scale to additional instances WITHIN 30 seconds"
- ADR links back: This ADR (Cloud Run) implements the auto-scaling specification from EARS-01

**Behavior-Driven Tests (BDD-NN):**

- BDD scenarios define concrete behaviors the system must exhibit
- Example: "GIVEN strategy agent with min=0, max=5 instances WHEN request queue depth exceeds threshold THEN new instances scale up within 30 seconds"
- ADR links back: This ADR (Cloud Run) satisfies the scaling behavior scenarios in BDD-01

#### Traceability Header for Upstream Sources

Every ADR should include traceability tags in the header:

```markdown
# ADR-NN: Cloud Run Deployment Architecture

@PRD:[PRD-01](../02_PRD/PRD-01_serverless_deployment.md)
@EARS:[EARS-01](../03_EARS/EARS-01_infrastructure_requirements.md)
@bdd:[BDD-01.1:scenarios](../04_BDD/BDD-01_gcp_cloud_run/BDD-01.1_gcp_cloud_run_deployment.feature#scenarios)
```

#### Documenting Upstream Sources in PART 4

The "Upstream Sources" section in PART 4 details what requirements drove the decision:

```markdown
### Upstream Sources

**Business Logic**: 
- [PRD-01 - Serverless Deployment Requirements](../02_PRD/PRD-01_serverless_deployment.md): 
  Defines serverless deployment requirements for multi-agent orchestration, auto-scaling policies 
  (0-5 instances), and regional failover

**EARS Requirements**: 
- [EARS-01 - Infrastructure Engineering Requirements](../03_EARS/EARS-01_infrastructure_requirements.md): 
  Specifies formal requirements for container management (health checks every 30s), 
  performance SLOs (p95 <100ms latency), cost optimization (<$110/month per agent group)

**BDD Scenarios**: 
- [BDD-01 - GCP Cloud Run Deployment](../04_BDD/BDD-01_gcp_cloud_run/BDD-01.1_gcp_cloud_run_deployment.feature): 
  Provides behavior scenarios for container deployment, auto-scaling events, 
  multi-zone failover procedures, and scheduled scaling
```

### Downstream Artifacts: How This Decision Is Implemented

Downstream artifacts are the **technical specifications and implementation that follow from ADR decisions**. They answer the question: "What must be built to realize this architecture?"

#### Understanding Downstream Artifacts

Downstream artifacts form the implementation chain flowing from ADR decisions:

**System Requirements (SYS-NN):**

- Translates architectural decisions into system-level requirements
- Example: "SYS-01 specifies per-agent resource allocation (orchestrator: 2vCPU/4Gi RAM, strategy agents: 1vCPU/2Gi RAM)"
- Downstream from: This ADR (Cloud Run) decision to allocate resources per agent type

**Atomic Requirements (REQ-NN):**

- Breaks down system requirements into granular, independently verifiable requirements
- Example: "REQ-01: Deploy all agents as Cloud Run containers with auto-scaling (0-5 instances/agent)"
- Downstream from: ADR (Cloud Run) architectural pattern

**Technical Specifications (SPEC-NN.yaml):**

- Declarative specifications that code must implement
- Example: "SPEC-01_cloud_run_configuration.yaml: Defines per-agent resource allocation, health check endpoints, scaling policies"
- Downstream from: ADR (Cloud Run) component design and resource allocation decisions

**Implementation Code (src/{module}/):**

- Actual code implementing the architecture
- Example: "agents/orchestrator/main.py implements health checks at /ready and /health endpoints per ADR specification"
- Downstream from: All upstream specifications starting with ADR

**Tests (tests/{suite}/):**

- Test suites validating that implementation satisfies ADR constraints
- Example: "tests/integration/test_cloud_run_deployment.py validates scaling behaviors defined in ADR"
- Downstream from: ADR success metrics and acceptance criteria

#### Traceability Reference for Downstream Artifacts

Document downstream artifact relationships in PART 4:

```markdown
### Downstream Artifacts

**System Requirements**: 
- [SYS-01 - Cloud Run Compute Sizing](../06_SYS/SYS-01_cloud_run_compute.md): 
  System-level requirements for per-agent resource allocation, health check specifications, 
  and auto-scaling policy definitions

**Atomic Requirements**: 
- [REQ-01 - Serverless Container Deployment](../07_REQ/infrastructure/REQ-01_serverless_deployment.md#REQ-01)
- [REQ-02 - Auto-scaling Policy](../07_REQ/infrastructure/REQ-02_auto_scaling.md#REQ-02)
- [REQ-03 - Regional High Availability](../07_REQ/infrastructure/REQ-03_regional_ha.md#REQ-03)

**Technical Specifications**: 
- [SPEC-01 - Cloud Run Configuration](../10_SPEC/compute/cloud_run_service.yaml): 
  Declarative specification for per-agent resource allocation, health check configuration

**Implementation Code**: 
- Orchestrator Agent: `agents/orchestrator/main.py` (implements /ready and /health endpoints)
- Analysis Agents: `agents/analysis_{id}/main.py` (ML workloads with sustained CPU allocation)
- Health Check Logic: `agents/health_checks.py` (dependency validation and liveness probes)

**Test Coverage**: 
- Integration Tests: `tests/integration/test_cloud_run_deployment.py` (validates orchestrator ↔ analysis agent communication)
- Load Tests: `tests/load/locustfile_1000rps.py` (stress test with 1000 requests/second)
- Performance Tests: `tests/performance/cold_start_validation.py` (validates <1s cold start)
```

### Building Complete Traceability Chains

Effective ADRs establish complete traceability chains from business requirements through implementation:

```text
PRD-01 (Business need: scale to 11 agents)
    ↓
EARS-01 (Technical spec: scale 0-5 instances, <100ms latency)
    ↓
BDD-01 (Behavior: scale-up completes in <30 seconds)
    ↓
ADR-01 (Decision: Use Cloud Run with request-based auto-scaling)
    ↓
SYS-01 (System design: 2vCPU/4Gi RAM per agent, min/max instance config)
    ↓
REQ-01 to REQ-008 (Atomic requirements: deploy, scale, monitor, HA, etc.)
    ↓
SPEC-01 (Terraform: Cloud Run service definition, scaling policies)
    ↓
agents/orchestrator/main.py (Implementation: health checks, request handling)
    ↓
tests/integration/test_cloud_run_deployment.py (Validation: requirements met)
```

Each link in the chain is bidirectional:

- **Downstream**: "How will this ADR be implemented?"
- **Upstream**: "What requirements justified this ADR?"

### Traceability Best Practices for AI-First Development

#### 1. Include Complete Anchor References

Use specific file paths and line numbers for unambiguous linking:

```markdown
# ❌ Insufficient: Vague reference
@PRD: Product requirements somewhere

# ✅ Complete: Specific file and anchor
@PRD:[PRD-01](../02_PRD/PRD-01_serverless_deployment.md#PRD-01)
@EARS:[EARS-01](../03_EARS/EARS-01_infrastructure_requirements.md#EARS-01-scaling)
```

#### 2. Map Each Requirement to Implementation

Create explicit traceability tables showing how each requirement is satisfied:

```markdown
## Requirements Satisfied

| Requirement ID | Description | ADR Decision | Implementation |
|---|---|---|---|
| PRD-01 | Support 11 concurrent agents | Cloud Run with independent services | agents/{agent_type}/main.py |
| EARS-01 | Scale 0-5 instances | Request-based auto-scaling | infrastructure/cloud_run_policies.yaml |
| BDD-01 | Scale-up <30 seconds | Cloud Run native scaling | tests/integration/cloud_run_tests.py |
```

#### 3. Validate Traceability in CI/CD

Automated checks should verify:

- All ADR upstream sources (02_PRD/03_EARS/BDD) exist and are linked
- All ADR downstream artifacts (06_SYS/07_REQ/SPEC) exist or are planned
- No orphaned requirements (requirements not linked to any ADR)
- No broken links (references to non-existent documents)

#### 4. Update Traceability When Documents Change

When upstream documents change:

1. Update affected ADRs to reflect new requirements
2. Cascade changes to downstream 06_SYS/07_REQ/SPEC
3. Update implementation code and tests
4. Document change in ADR update log

#### 5. Enable AI Agents to Follow Chains

Structure traceability for LLMs/AI agents to understand context:

```markdown
# ✅ AI-Friendly: Clear context and relationships
## Requirements Satisfied

**From PRD-01 (section 2.1)**: "System must support concurrent execution of 11 agents"
- **How Satisfied**: Each agent deployed as separate Cloud Run service with isolated scaling
- **SYS Reference**: SYS-01 specifies per-agent resource allocation
- **Implementation**: agents/{agent_type}/*.py implements agent container

**From EARS-01 (section 3.2)**: "Achieve p95 latency <100ms"
- **How Satisfied**: Orchestrator always-on, optimized analysis agents, minimal strategy agent latency
- **Spec Reference**: SPEC-01 specifies 2vCPU/4Gi RAM allocation
- **Test Reference**: tests/performance/latency_validation.py verifies p95 <100ms
```

## References

### How to Use This Reference section

This section documents all external resources, related documentation, and supporting evidence for ADR decisions. It serves as a research foundation for future architectural work.

### Internal Links: Project Documentation

Document your ADR's relationship to other project artifacts:

```markdown
## References

### Internal Links

**Upstream Requirements Documentation:**
- [PRD-01: Product Requirements - Serverless Deployment](../02_PRD/PRD-01_serverless_deployment.md): Business requirements for multi-agent deployment
- [EARS-01: Engineering Requirements - Infrastructure](../03_EARS/EARS-01_infrastructure_requirements.md): Atomic technical requirements for container management
- [BDD-01: Behavior-Driven Tests - GCP Cloud Run](../04_BDD/BDD-01_gcp_cloud_run/BDD-01.1_gcp_cloud_run_deployment.feature): Executable scenarios for deployment behavior

**Related ADRs:**
- [ADR-NN: Networking Architecture](./ADR-NN_networking_architecture.md): VPC and Load Balancer prerequisite
- [ADR-YY: Secrets Management](./ADR-YYY_Secrets_management_strategy.md): API key management for Cloud Run
- [ADR-ZZZ: Database Layer Design](./ADR-ZZZ_cloud_sql_instance_sizing.md): Risk validator database sizing

**Downstream Implementation:**
- [SYS-01: System Requirements - Cloud Run](../06_SYS/SYS-01_cloud_run_compute.md): System-level compute specifications
- [SPEC-01: Cloud Run Configuration](../10_SPEC/compute/cloud_run_service.yaml): Terraform/declarative configuration
- [Cloud Run Deployment Runbook](../../docs/deployment_runbook.md): Operational procedures
```

### External Links: Technology Documentation

Reference official documentation for technologies chosen in the ADR:

```markdown
### External Technology References

**Google Cloud Run Documentation:**
- [Cloud Run Overview](https://cloud.google.com/run/docs): Official GCP Cloud Run documentation
- [Cloud Run Concepts](https://cloud.google.com/run/docs/concepts): Understanding services, revisions, traffic splitting
- [Configuring Cloud Run Services](https://cloud.google.com/run/docs/configuring): Resource allocation, environment variables, scaling
- [Cloud Run Best Practices](https://cloud.google.com/run/docs/best-practices): Production readiness guidelines
- [Troubleshooting Cloud Run](https://cloud.google.com/run/docs/troubleshooting): Common issues and solutions

**Python on Cloud Run:**
- [Python 3.11 Runtime](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/python): Python containerization best practices
- [Multi-stage Docker Builds](https://docs.docker.com/build/building/multi-stage/): Optimizing container images for faster startup

**Infrastructure as Code:**
- [Terraform Cloud Run Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_service): Terraform resource documentation
- [Terraform Best Practices](https://developer.hashicorp.com/terraform/best-practices): Infrastructure as Code patterns
```

### Research and Industry Benchmarks

Document research that informed the architectural decision:

```markdown
### Research and Industry Context

**Serverless vs Traditional Infrastructure:**
- [Cloud Native Computing Foundation - Serverless Whitepaper](https://www.cncf.io/): Industry trends in serverless adoption
- [Gartner's Serverless Architecture Report 2024](https://www.gartner.com/): [DATA_ANALYSIS - e.g., user behavior analysis, trend detection] and adoption patterns
- Benchmark Study: "Kubernetes vs Serverless for Service Systems" (internal document: docs/research/k8s_vs_serverless_benchmark.md)

**Cold Start Optimization:**
- [StackOverflow Analysis: Cloud Run Cold Starts](https://stackoverflow.com/questions/tagged/google-cloud-run): Community cold start experiences
- Research Paper: "Optimizing Container Image Size for Sub-second Startup" (referenced in: docs/container_optimization_report.md)
- Industry Case Study: "Fintech Platform Serverless Migration" (external source: Case_Study_Fintech_Serverless.pdf)

**Performance Benchmarks:**
- Financial Services Latency Standards: <100ms p95 latency for service decisions is industry standard (sources: various Service Systems literature)
- Actual Benchmark Results: See `docs/performance_benchmarks/cloud_run_latency_report.csv` for our measurements vs. industry standards

**Cost Analysis:**
- GCP Cost Comparison: Traditional VM ($2,400/month) vs. Cloud Run ($800-1500/month) - documented in `docs/cost_analysis/infrastructure_cost_comparison.md`
```

### Lessons Learned and Decision Context

Document insights and trade-offs that informed this decision:

```markdown
### Lessons Learned from Related Work

**From Previous ADRs:**
- [ADR-03: Kubernetes Migration Attempt](./ADR-03_kubernetes_attempt_archived.md): Why GKE was rejected in favor of serverless (30 hours/month operational burden)
- [ADR-005: Database Selection](./ADR-005_database_architecture.md): Experiences with persistent storage and stateless services

**From Production Incidents:**
- Incident Report: "March 2025 Scaling Incident" (`docs/incident_reports/2025-03_scaling_incident.md`): Revealed need for faster auto-scaling (triggered ADR creation)
- Postmortem: "Cold Start Latency Spike" (`docs/postmortems/2025-02_cold_start_postmortem.md`): Drove decision to optimize container images

**From Team Retrospectives:**
- Engineering Retrospective Notes: "Infrastructure Complexity Review" (internal Confluence doc) - team feedback on operational burden of previous approach
```

### Supporting Documentation

Include links to evidence and supporting analysis:

```markdown
### Supporting Analysis and Evidence

**Performance Validation:**
- Cold Start Benchmark Report: `docs/performance/cold_start_analysis.md` (95% of instances <950ms startup time)
- Latency Measurement Results: `docs/performance/latency_p95_measurement.csv` (p95 consistently <80ms in production)
- Cost Tracking Dashboard: `docs/cost_analysis/monthly_infrastructure_cost_dashboard.csv` (actual spend $800-1200/month vs. projected)

**Risk Assessment:**
- Risk Register: `docs/risk_management/cloud_run_risks.xlsx` (identified risks and mitigation strategies)
- Failure Mode Analysis: `docs/fmea/cloud_run_fmea.md` (detailed FMEA for critical components)

**Architecture Validation:**
- Architecture Review Board Approval: `docs/arb_reviews/ARB_2025-10-15_cloud_run_approval.md` (stakeholder sign-off)
- security Assessment: `docs/security/cloud_run_security_audit.md` (SOC 2 compliance validation)
```

### Creating Effective References

When writing an ADR, include references that:

1. **Show Research**: Evidence that alternatives were seriously considered
2. **Justify Constraints**: Explain why performance, cost, and reliability targets were chosen
3. **Enable Future Decisions**: Provide context for how to evolve the architecture
4. **Support Validation**: Allow verification that implementation satisfies ADR constraints
5. **Build Organizational Knowledge**: Capture lessons learned for future projects

### Common Reference Patterns

**For Technology Selection ADRs:**

- Link to official documentation for chosen technology
- Reference competitive analysis comparing alternatives
- Include benchmark results from POCs or proof of concepts
- Document why industry-standard tools were chosen or rejected

**For Infrastructure ADRs:**

- Link to cost calculators and cost comparison spreadsheets
- Reference performance benchmarks and SLA requirements
- Include capacity planning models and scaling analysis
- Document compliance and audit requirements

**For Integration ADRs:**

- Link to API specifications and contracts
- Reference integration testing results
- Include data format specifications and transformation rules
- Document fallback and error handling strategies

**For security Architecture ADRs:**

- Link to threat models and risk assessments
- Reference compliance standards and audit requirements
- Include security testing results and penetration test reports
- Document incident response procedures

---

## Example ADR Template

See `ADR-TEMPLATE.md` for the complete structural template with all sections and helpful prompts for each part.

See `{project_root}/docs/05_ADR/ADR-00_technology_stack.md` for a comprehensive real-world example of a fully-developed ADR demonstrating all best practices including:

- Complete upstream source traceability to 02_PRD/03_EARS/BDD
- Detailed downstream artifact mapping to 06_SYS/07_REQ/10_SPEC/code
- References to external documentation and research
- Risk assessments with mitigation strategies
- Performance benchmarks and actual production metrics

---

**README Version**: 1.0
**Last Updated**: 2025-10-28
**Template Version**: ADR-TEMPLATE.md v1.0

**Related Documentation:**

- [ID_NAMING_STANDARDS.md](../ID_NAMING_STANDARDS.md): Document ID allocation and naming conventions
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md): Complete SDD workflow overview
- [TRACEABILITY.md](../TRACEABILITY.md): Cross-document traceability standards
## File Size Limits

- Target: 300–500 lines per file
- Maximum: 600 lines per file (absolute)
- If a file approaches/exceeds limits, split into section files using `ADR-SECTION-TEMPLATE.md` and update the suite index. See `../DOCUMENT_SPLITTING_RULES.md` for core splitting standards.

## Document Splitting Standard

When ADRs become lengthy or cover multiple decisions/sub-decisions:
- Ensure `ADR-{NN}.0_index.md` exists and contains a section map
- Create `ADR-{NN}.{S}_{section_slug}.md` from `ADR-SECTION-TEMPLATE.md` (see `../DOCUMENT_SPLITTING_RULES.md` for numbering and required front‑matter)
- Keep Prev/Next navigation, update links and impacts to related artifacts
- Validate links and size; keep decision history/appendices coherent across sections
