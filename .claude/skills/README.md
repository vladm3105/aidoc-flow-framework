# Claude Skills Index

**Purpose**: Catalog of reusable Claude skills for the Options Trading System project

## Available Skills

### 1. generate_implementation_plan

**Skill ID**: `generate_implementation_plan`
**File**: [generate_implementation_plan.md](./generate_implementation_plan.md)
**Quick Reference**: [generate_implementation_plan_quickref.md](./generate_implementation_plan_quickref.md)

**Purpose**: Generate IMPL (Implementation Plan) documents from BRD analysis following SDD workflow

**Use Cases**:
- Starting new project with multiple BRD documents
- Creating phased implementation roadmap
- Analyzing BRD dependencies and sequencing
- Generating atomic phases with exit criteria
- Calculating project timeline and resources

**Complexity**: High (multi-step workflow with dependency analysis)
**Version**: 1.0
**Created**: 2025-11-02

**Quick Start**:
```bash
/skill generate_implementation_plan
```

**Inputs**:
- `brd_directory`: Path to BRD files (required)
- `output_file`: Path for generated IMPL (required)
- `force_phase_1_brd`: BRD ID to prioritize (optional)
- `max_phase_duration_weeks`: Maximum phase duration (default: 4)

**Outputs**:
- Complete IMPL document following IMPL-TEMPLATE.md structure
- Dependency graph (Mermaid diagram)
- Requirements mapping table
- Timeline with milestones
- Resource allocation table

**Key Features**:
- Atomic phase decomposition (≤4 weeks per phase)
- Dependency analysis (Data-First, Read-Before-Write principles)
- Parallel execution identification
- Critical path calculation
- Exit criteria generation
- Traceability validation

---

### 2. doc-flow

**Skill ID**: `doc-flow`
**Directory**: [doc-flow/](./doc-flow/)
**File**: [doc-flow/SKILL.md](./doc-flow/SKILL.md)

**Purpose**: AI-Driven Specification-Driven Development workflow transformation (business requirements → production code)

**Key Features**:
- Complete 16-layer SDD workflow (Strategy → BRD → PRD → EARS → BDD → ADR → SYS → REQ → IMPL → CTR → SPEC → TASKS → IPLAN → Code → Tests → Validation)
- **Cumulative Tagging Hierarchy**: Each artifact includes traceability tags from ALL upstream layers
- Automated traceability validation and matrix generation
- Tag-based audit trail for regulatory compliance (SEC, FINRA, FDA, ISO)
- Impact analysis: instantly identify all downstream artifacts affected by upstream changes
- Template-driven artifact creation with built-in quality gates

**Use Cases**:
- Creating formal requirements and architecture artifacts with complete traceability
- Implementing cumulative tagging for audit trails and regulatory compliance
- Managing complex multi-artifact development workflows
- Validating traceability across entire codebase (business → code → tests)
- Generating automated traceability matrices for documentation

**Complexity**: Complete SDD methodology with cumulative tagging enforcement
**Status**: Managed skill (framework-level)
**Version**: 2.0 (with cumulative tagging hierarchy)
**Documentation**: [doc-flow/SKILL.md](./doc-flow/SKILL.md) - Section 2.5: Cumulative Tagging Hierarchy

---

### 3. google-adk

**Skill ID**: `google-adk`
**Directory**: [google-adk/](./google-adk/)
**File**: [google-adk/SKILL.md](./google-adk/SKILL.md)
**Quick Reference**: [google-adk_quickref.md](./google-adk_quickref.md)

**Purpose**: Develop agentic software and multi-agent systems using Google ADK in Python

**Use Cases**:
- Build conversational AI agents with tool integration
- Create multi-agent orchestration systems (coordinator, pipeline, hierarchical)
- Develop workflow agents (sequential, parallel, iterative/loop)
- Implement custom tools for agents (functions, OpenAPI, MCP)
- Design agent architectures for complex task decomposition
- Deploy agent applications (Agent Engine, Cloud Run, Docker)
- Evaluate agent performance with criteria-based testing
- Implement human-in-the-loop patterns for critical decisions

**Complexity**: 3 (Moderate - requires agent architecture knowledge)
**Version**: 1.0.0
**Created**: 2025-11-13

**Quick Start**:
```bash
# Install
pip install google-adk

# Invoke skill
/skill google-adk
```

**Key Features**:
- **Code-first approach**: Define agents in Python (not YAML/JSON configs)
- **Agent types**: LlmAgent (dynamic), Sequential/Parallel/Loop Workflows (deterministic), Custom
- **Multi-agent patterns**: Coordinator/dispatcher, sequential pipeline, parallel fan-out/gather, hierarchical decomposition, generator-critic, HITL
- **Tool ecosystem**: Custom functions, OpenAPI integration, MCP (Model Context Protocol), built-in (Search, Code Execution)
- **Memory & state**: Session management, conversation history, state persistence
- **Deployment options**: Agent Engine (managed), Cloud Run, GKE, Docker (self-hosted)
- **Evaluation framework**: Criteria-based testing, user simulation
- **Web UI**: Interactive testing and debugging interface

**Supported Technologies**:
- **Primary language**: Python 3.9+ (`google-adk` package)
- **Also available**: Go (`adk-go`), Java (`adk-java`)
- **LLM models**: Gemini (optimized), other LLMs (model-agnostic)
- **Deployment**: Google Cloud (Agent Engine, Cloud Run), Docker, self-hosted

**When to Use**:
- Building agentic applications requiring tool integration
- Creating multi-agent systems with specialized roles
- Implementing deterministic workflows with LLM decision-making
- Need code-first agent development (vs configuration-based)
- Deploying to Google Cloud infrastructure
- Require evaluation framework for agent testing
- Human approval needed for critical agent actions

**When NOT to Use**:
- Simple script would suffice (use Python directly)
- No agent orchestration needed (use LLM SDK directly)
- Real-time processing <100ms latency required
- Extensive custom UI needed (ADK is backend framework)
- Team prefers configuration-based frameworks (LangChain, n8n)
- Already invested in different agent framework

**Agent Complexity Ratings**:
- Simple LlmAgent with tools: **2**
- Sequential/Parallel workflow: **2-3**
- Loop workflow (iterative): **3**
- Custom agent: **3**
- Multi-agent coordinator (2-3 agents): **4**
- Sequential pipeline (3+ agents): **4**
- Hierarchical multi-agent (>5 agents): **5**

**Tool Development Complexity**:
- Custom function tool: **2**
- OpenAPI integration: **2**
- MCP integration: **3**
- Async tool development: **2**

**Deployment Complexity**:
- Agent Engine (managed): **2**
- Cloud Run deployment: **2**
- Self-hosted Docker: **3**

**Outputs**:
- Agent implementations (LlmAgent, Workflow Agents, Custom)
- Custom tool definitions (Python functions)
- Multi-agent architectures (coordinator, pipeline, hierarchical)
- Deployment configurations (Agent Engine, Docker, Cloud Run)
- Evaluation test suites (criteria-based, user simulation)
- State management implementations
- HITL (Human-in-the-Loop) patterns

---

### 4. project-mgnt

**Skill ID**: `project-mgnt`
**Directory**: [project-mgnt/](./project-mgnt/)
**File**: [project-mgnt/SKILL.md](./project-mgnt/SKILL.md)

**Purpose**: Product Owner / Project Manager skill for MVP/MMP/MMR implementation planning

**Use Cases**:
- Create initial implementation plans from requirements (BRD, PRD, user stories)
- Update existing plans when requirements change (preserves completed work)
- Define MVP/MMP/MMR release stages
- Group requirements into atomic, independently deployable units
- Identify parallel execution opportunities
- Calculate timelines with dependency analysis

**Complexity**: Product Owner-level strategic planning
**Version**: 1.0
**Created**: 2025-01-03

**Quick Start**:
```bash
/skill project-mgnt
```

**Key Features**:
- **Generalized methodology**: Works with any project, domain, or requirement format
- **Stage-based planning**: MVP (validation) → MMP (launch) → MMR (growth)
- **Atomic grouping**: 1-4 week independently deployable units
- **Preserves progress**: Updates never modify completed work (immutable)
- **Timeline continuity**: Updates start from current date, not project beginning
- **Change tracking**: Complete change logs document all modifications
- **Adaptable**: Guidelines for infrastructure, APIs, ML/AI, web apps, different team sizes

**Outputs**:
- Implementation plan document (`PLAN-XXX_[project_name].md`)
- MVP/MMP/MMR stage breakdown
- Atomic groups with priorities, dependencies, status
- Gantt chart timeline visualization
- Parallel execution matrix
- Success metrics and exit criteria
- Change log (for plan updates)
- Progress summary with completion tracking

**When to Use**:
- Starting new project requiring structured implementation plan
- Requirements have changed mid-project and plan needs updating
- Need to preserve completed work while replanning future work
- Want to apply MVP/MMP/MMR methodology to release planning
- Need product owner expertise for stage definitions and priorities

---

### 5. charts_flow

**Skill ID**: `charts_flow`
**Directory**: [charts_flow/](./charts_flow/)
**File**: [charts_flow/SKILL.md](./charts_flow/SKILL.md)
**Quick Reference**: [charts_flow_quickref.md](./charts_flow_quickref.md)

**Purpose**: Create and manage Mermaid architecture diagrams with automatic SVG generation for documentation

**Use Cases**:
- Create architecture diagrams for PRD, BRD, ADR, SYS documents
- Migrate existing inline Mermaid diagrams to separate files
- Improve document rendering performance by separating diagram files
- Provide dual format: Mermaid source for AI assistants, SVG preview for humans
- Maintain traceability between parent documents and diagram files

**Complexity**: Medium (file operations + SVG conversion)
**Version**: 1.0
**Created**: 2025-01-04

**Quick Start**:
```bash
/skill charts_flow
```

**Supported Diagram Types**:
- Flowchart (process flows, component hierarchies)
- Sequence (agent interactions, API calls)
- Class (object relationships, data models)
- State (state machines, lifecycle flows)
- Component (system architecture)
- Deployment (infrastructure topology)

**Key Features**:
- **Automatic SVG generation**: Uses Mermaid CLI (`mmdc`) or Puppeteer
- **Base64 embedding**: SVG embedded inline in parent documents
- **Naming convention**: `{PARENT-ID}-diag_{description}.md` format
- **Migration mode**: Extract existing Mermaid blocks from documents
- **Document Control**: Full metadata linking back to parent documents
- **Performance**: Separate files improve documentation rendering speed

**Outputs**:
- Diagram file in `diagrams/` subfolder
- SVG preview embedded in parent document (Base64)
- Reference link from parent to diagram file
- Bidirectional cross-references

**When to Use**:
- Need to visualize architecture or workflows
- Main document slow to render due to complex diagrams
- Diagram needs to be reused across documents
- Following documentation standards for separation of concerns

**When NOT to Use**:
- Creating simple tables or lists (use markdown)
- Diagram is < 20 lines and parent renders fast
- Need data visualization (Gantt, pie charts - outside scope)

---

### 6. adr-roadmap

**Skill ID**: `adr-roadmap`
**Directory**: [adr-roadmap/](./adr-roadmap/)
**File**: [adr-roadmap/SKILL.md](./adr-roadmap/SKILL.md)

**Purpose**: Generate comprehensive phased implementation roadmaps from Architecture Decision Records for any project

**Use Cases**:
- Create implementation roadmap from existing ADRs
- Analyze ADR dependencies and critical path
- Generate phased rollout plan (POC → MVP → Production → Scale → Advanced)
- Estimate timelines from ADR complexity ratings
- Identify parallel implementation opportunities
- Plan technical debt remediation
- Assess risks per implementation phase

**Complexity**: High (dependency analysis, phase decomposition, timeline calculation)
**Version**: 1.0.0
**Created**: 2025-01-08

**Quick Start**:
```bash
/skill adr-roadmap
```

**Inputs**:
- `adr_directory`: Path to ADR markdown files (required)
- `project_context`: Project type, team size, constraints (required)
- `output_file`: Roadmap destination (default: `{adr_directory}/ADR-000_IMPLEMENTATION-ROADMAP.md`)
- `max_phase_duration`: Maximum weeks per phase (default: 8)
- `phase_model`: Phasing approach - `poc-mvp-prod`, `iterative`, `waterfall` (default: `poc-mvp-prod`)
- `team_size`: Number of FTE engineers (default: 3)

**Outputs**:
- Comprehensive roadmap document (1,000-2,000 lines)
- Executive summary with timeline
- Phase definitions with ADR assignments
- ADR dependency matrix (Mermaid flowchart)
- Timeline visualization (Gantt chart)
- Technical debt tracking per phase
- Risk assessment per phase
- Testing strategy per phase
- Acceptance criteria per phase
- Traceability matrix

**Key Features**:
- **Domain-agnostic**: Works for web, mobile, data, ML, infrastructure, embedded systems
- **Automatic dependency mapping**: Parses ADR relationships
- **Critical path identification**: Highlights longest dependency chain
- **Phase decomposition**: Creates logical implementation phases
- **Timeline estimation**: Calculates effort from ADR complexity
- **Risk assessment**: Identifies high-risk ADRs and mitigation strategies
- **Adaptation guidelines**: Specific guidance for greenfield, brownfield, refactoring projects
- **Decision frameworks**: Reusable logic for phase scope, ADR sequencing, complexity scoring
- **Technical debt management**: Tracks acceptable shortcuts per phase

**When to Use**:
- Project has ≥5 ADRs requiring coordinated implementation
- Need stakeholder visibility into implementation timeline
- Planning multi-phase architectural rollout
- Managing technical debt across project lifecycle
- Require go/no-go decision criteria per phase

**When NOT to Use**:
- Single ADR with straightforward implementation
- ADRs are informational only (no implementation)
- Planning from requirements (BRD/PRD) → use `project-mngt` skill
- Generating documentation (SYS/REQ/SPEC) → use `doc-flow` skill

**Supported Phase Models**:
1. **POC-MVP-Prod** (default): POC validation → MVP launch → Production hardening → Scale optimization → Advanced features
2. **Iterative**: Fixed-duration iterations with incremental delivery
3. **Waterfall**: Sequential phases by ADR category

**Adaptation Patterns**:
- **Greenfield**: Front-load infrastructure, enable parallel development
- **Brownfield/Migration**: Phase by risk, maintain backward compatibility, include rollback plans
- **Refactoring**: Phase by module boundaries, minimize customer impact

---

### 7. trace-check

**Skill ID**: `trace-check`
**Directory**: [trace-check/](./trace-check/)
**File**: [trace-check/SKILL.md](./trace-check/SKILL.md)

**Purpose**: Validate and update bidirectional traceability across SDD artifacts (project)

**Use Cases**:
- Validate traceability before commits
- Audit documentation after artifact creation/updates
- Detect broken links and missing reverse references
- Calculate coverage metrics for quality reporting
- Auto-fix bidirectional inconsistencies
- Identify orphaned artifacts
- Verify ID format compliance

**Complexity**: Medium (requires parsing multiple file formats)
**Version**: 1.0.0
**Created**: 2025-11-11

**Quick Start**:
```bash
/skill trace-check
```

**Inputs**:
- `project_root_path`: Path to project documentation root (required)
- `artifact_types`: Specific types to validate (default: `["all"]`)
- `strictness_level`: `"strict"` (default), `"permissive"`, `"pedantic"`
- `auto_fix`: Enable auto-fix with backups (default: `false`)
- `report_format`: `"markdown"` (default), `"json"`, `"text"`

**Key Features**:
- **Bidirectional validation**: Verifies A→B implies B→A exists
- **Link resolution**: Tests all markdown links resolve to valid files
- **ID format compliance**: Validates TYPE-XXX or TYPE-XXX-YY format
- **Coverage metrics**: Calculates % artifacts with complete traceability
- **Orphan detection**: Identifies artifacts with no upstream/downstream
- **Auto-fix capabilities**: Updates documents with backup creation
- **Performance**: <30 seconds for 100 artifacts

**Outputs**:
- Validation report (markdown/JSON/text)
- Broken links with file:line references
- Bidirectional gaps with fix recommendations
- Coverage metrics by artifact type
- Auto-fix modifications log
- Backup archive before changes

**When to Use**:
- Before committing documentation changes
- After creating new artifacts (BRD, PRD, SPEC, etc.)
- During periodic audits (weekly/sprint/release)
- Validating traceability matrix completeness
- Establishing baseline quality metrics

**When NOT to Use**:
- Working on code implementation (use code review tools)
- Validating code traceability (use docstring validators)
- For non-SDD documentation projects
- During active editing sessions (wait until stable)

**Validation Checks**:
- ✅ ID format: TYPE-XXX or TYPE-XXX-YY
- ✅ Link resolution: All paths resolve to valid files
- ✅ Anchor existence: All #anchor references found
- ✅ Bidirectional consistency: Forward and reverse links match
- ✅ Coverage: All artifacts have Section 7 Traceability
- ✅ Orphan detection: No artifacts missing upstream/downstream

**Quality Gates**:
- Target: ≥95% bidirectional consistency
- Target: 100% link resolution
- Target: 100% ID format compliance
- Target: Zero orphaned root/leaf artifacts

---

### 8. n8n

**Skill ID**: `n8n`
**Directory**: [n8n/](./n8n/)
**File**: [n8n/SKILL.md](./n8n/SKILL.md)
**Quick Reference**: [n8n_quickref.md](./n8n_quickref.md)

**Purpose**: Develop workflows, custom nodes, and integrations for the n8n automation platform

**Use Cases**:
- Design automation workflows combining multiple services
- Write JavaScript/Python code within workflow nodes
- Build custom nodes in TypeScript
- Integrate APIs, databases, and cloud services (500+ pre-built connectors)
- Create AI agent workflows with LangChain
- Implement error handling and recovery patterns
- Plan self-hosted n8n deployments
- Convert manual processes to automated workflows

**Complexity**: 3 (Moderate - requires platform-specific knowledge)
**Version**: 1.0.0
**Created**: 2025-11-13

**Quick Start**:
```bash
/skill n8n
```

**Key Features**:
- **Workflow design methodology**: Planning, node selection, error handling, testing
- **Code execution**: JavaScript/Python nodes with API calls, transformations, aggregations
- **Custom node development**: Programmatic and declarative styles in TypeScript
- **Integration patterns**: HTTP Request, webhooks, database, file operations
- **AI agent workflows**: LangChain integration, gatekeeper pattern, RAG
- **Deployment guidance**: Docker, environment config, scaling with queue mode
- **Best practices**: Modularity, error resilience, performance, security
- **Pattern library**: API sync, data enrichment, event-driven processing, human-in-the-loop

**Supported Technologies**:
- **Runtime**: Node.js, TypeScript (90.7%), Vue.js frontend
- **Execution**: JavaScript, Python code nodes
- **Integrations**: 500+ services (AWS, GCP, Azure, Slack, PostgreSQL, MongoDB, OpenAI, etc.)
- **AI/ML**: LangChain, OpenAI, Anthropic, Hugging Face, Pinecone vectors
- **Deployment**: Docker, self-hosted, cloud

**When to Use**:
- Need to automate workflows across multiple services
- Building API integrations without writing full applications
- Creating scheduled data synchronization tasks
- Implementing event-driven automation
- Developing AI agent workflows with external tools
- Converting manual processes to code
- Rapid prototyping of integrations

**When NOT to Use**:
- Real-time processing required (<100ms latency)
- Complex business logic better suited to application code
- Extensive custom UI needed
- Single-purpose script (Python/Node.js script simpler)
- Advanced debugging tools required

**Workflow Complexity Ratings**:
- Use native node: **1**
- HTTP Request integration: **1**
- Code node transformation: **2**
- Error handling pattern: **2**
- Declarative custom node: **2**
- AI agent basic: **3**
- Programmatic custom node: **3**
- Gatekeeper pattern (human-in-loop): **4**
- Multi-agent orchestration: **5**

**Outputs**:
- Workflow designs with node configuration
- Code node implementations (JavaScript/Python)
- Custom node TypeScript packages
- Integration patterns and templates
- Deployment configurations (Docker Compose, environment variables)
- Error handling strategies
- AI agent workflow patterns

---

### 9. skill-recommender

**Skill ID**: `skill-recommender`
**Directory**: [skill-recommender/](./skill-recommender/)
**File**: [skill-recommender/SKILL.md](./skill-recommender/SKILL.md)

**Purpose**: Intelligent skill suggestion engine that analyzes user intent and project context to recommend appropriate documentation skills

**Use Cases**:
- User is unsure which skill to use for a documentation task
- Starting a new documentation workflow and need guidance
- Want to discover available skills for a specific intent
- Need help navigating the skill catalog

**Complexity**: Low-Medium (intent parsing and skill matching)
**Version**: 1.0.0
**Created**: 2025-11-29

**Quick Start**:
```bash
/skill skill-recommender
```

**Key Features**:
- **Intent parsing**: Extract action verbs and targets from user requests
- **Skill matching**: Map parsed intent to skill catalog with confidence scores
- **Ranked recommendations**: Priority-ordered suggestions with rationale
- **Ambiguity handling**: Clarification questions when intent unclear
- **Context awareness**: Uses project state for better recommendations

**Inputs**:
- `user_request`: Natural language description of documentation task (required)
- `project_context`: Project structure and existing artifacts (optional)
- `max_recommendations`: Maximum recommendations to return (default: 3)

**Outputs**:
- Ranked skill recommendations with confidence scores
- Rationale for each recommendation
- Clarification questions when ambiguous
- Next steps guidance

**When to Use**:
- Don't know which doc-* skill to invoke
- New to the framework and need discovery
- Want to validate skill selection before starting

**When NOT to Use**:
- Already know the specific skill needed
- Non-documentation tasks
- Experienced user with clear intent

---

### 10. context-analyzer

**Skill ID**: `context-analyzer`
**Directory**: [context-analyzer/](./context-analyzer/)
**File**: [context-analyzer/SKILL.md](./context-analyzer/SKILL.md)

**Purpose**: Project context analysis engine that scans project structure and surfaces relevant information for documentation creation

**Use Cases**:
- Starting documentation work in an existing project
- Creating a new artifact that needs upstream references
- Need to understand what documentation already exists
- Want to identify gaps in documentation coverage
- Preparing context for doc-* skill invocation

**Complexity**: Medium (project scanning and context building)
**Version**: 1.0.0
**Created**: 2025-11-29

**Quick Start**:
```bash
/skill context-analyzer
```

**Key Features**:
- **Project scanning**: Enumerate artifacts by type and location
- **Metadata extraction**: Parse YAML frontmatter and Document Control sections
- **Traceability mapping**: Build artifact relationship graph
- **Workflow position**: Calculate current position in SDD layers
- **Upstream identification**: Find relevant upstream candidates for new artifacts
- **Key term extraction**: Build project vocabulary from existing docs

**Inputs**:
- `project_root`: Root path of project to analyze (required)
- `target_artifact_type`: Artifact type being created (optional)
- `depth`: Analysis depth: "quick", "standard" (default), "deep"

**Outputs**:
- Artifact inventory by type
- Traceability graph
- Workflow position analysis
- Upstream candidates with relevance scores
- Key terms and domain vocabulary
- Coverage gap identification

**When to Use**:
- Starting documentation in existing project
- Need context for new artifact creation
- Identifying documentation gaps
- Understanding project state

**When NOT to Use**:
- Project has no existing documentation
- Working on isolated single document
- Full project audit needed (use trace-check)

---

### 11. quality-advisor

**Skill ID**: `quality-advisor`
**Directory**: [quality-advisor/](./quality-advisor/)
**File**: [quality-advisor/SKILL.md](./quality-advisor/SKILL.md)

**Purpose**: Proactive quality guidance system that monitors artifact creation and provides real-time feedback on documentation quality

**Use Cases**:
- Creating a new documentation artifact
- Reviewing an artifact before submission
- Want to check compliance with template requirements
- Need guidance on common mistakes to avoid
- Validating cumulative tagging compliance

**Complexity**: Medium (template validation and anti-pattern detection)
**Version**: 1.0.0
**Created**: 2025-11-29

**Quick Start**:
```bash
/skill quality-advisor
```

**Key Features**:
- **Section monitoring**: Track completion against template requirements
- **Anti-pattern detection**: Identify 10+ common documentation mistakes
- **Tag validation**: Verify cumulative tagging compliance by layer
- **Naming compliance**: Validate ID format and filename conventions
- **Quality scoring**: Calculate overall completeness percentage
- **Actionable suggestions**: Provide specific fix recommendations

**Inputs**:
- `artifact_content`: Current content of artifact being created (required)
- `artifact_type`: Type of artifact (BRD, PRD, SPEC, etc.) (required)
- `artifact_id`: Document ID if assigned (optional)
- `check_level`: "quick", "standard" (default), "strict"

**Outputs**:
- Quality report with overall status
- Section completion scores
- Anti-pattern issues with severity levels
- Tag compliance validation
- Naming convention checks
- Prioritized recommendations (high/medium/low)

**Anti-Patterns Detected**:
- AP-001: Missing Document Control
- AP-002: Placeholder text ([TBD], TODO)
- AP-003: Vague acceptance criteria
- AP-004: Missing traceability tags
- AP-005: Broken internal links
- AP-006: ID format violations
- AP-007: Empty required sections
- AP-008: Orphan artifacts
- AP-009: Missing anchors
- AP-010: Duplicate ID references

**When to Use**:
- During artifact creation for real-time feedback
- Before submitting for review
- Validating compliance with SDD standards

**When NOT to Use**:
- Full traceability validation (use trace-check)
- Batch project validation (use doc-validator)
- Non-SDD documentation

---

### 12. workflow-optimizer

**Skill ID**: `workflow-optimizer`
**Directory**: [workflow-optimizer/](./workflow-optimizer/)
**File**: [workflow-optimizer/SKILL.md](./workflow-optimizer/SKILL.md)

**Purpose**: Workflow navigation assistant that recommends next steps and optimizes documentation sequence through the SDD workflow

**Use Cases**:
- Completed an artifact and need guidance on next steps
- Starting documentation and need workflow overview
- Want to identify parallel work opportunities
- Need progress report on documentation completion
- Unsure which artifacts to create next

**Complexity**: Medium (workflow analysis and dependency tracking)
**Version**: 1.0.0
**Created**: 2025-11-29

**Quick Start**:
```bash
/skill workflow-optimizer
```

**Key Features**:
- **Project state analysis**: Scan and categorize all existing artifacts
- **Workflow position**: Map artifacts to 12-layer SDD workflow
- **Dependency analysis**: Identify blocked and ready layers
- **Next-step recommendations**: Prioritized actions (P0, P1, P2) with rationale
- **Parallel opportunities**: Find work that can proceed simultaneously
- **Progress metrics**: Track completion percentage and milestones

**Inputs**:
- `project_root`: Root path of project to analyze (required)
- `completed_artifact`: ID of just-completed artifact (optional)
- `focus_area`: Filter: "core-workflow", "quality", "planning" (optional)

**Outputs**:
- Project state model with artifact inventory
- Workflow position (completed, in-progress, blocked layers)
- Next-step recommendations with skill invocations
- Parallel work opportunities
- Progress metrics and critical path
- Workflow guidance (short-term, medium-term)

**Workflow Layers**:
1. BRD (Business Requirements)
2. PRD (Product Requirements)
3. EARS (Formal Requirements)
4. BDD (Behavior Tests)
5. ADR (Architecture Decisions)
6. SYS (System Requirements)
7. REQ (Atomic Requirements)
8. IMPL (Implementation Plan) - optional
9. CTR (Interface Contracts) - optional
10. SPEC (Technical Specifications)
11. TASKS (Implementation Tasks)
12. IPLAN (Execution Plans)

**When to Use**:
- After completing any artifact
- Starting documentation workflow
- Planning parallel development
- Tracking overall progress

**When NOT to Use**:
- Need skill recommendation for specific task (use skill-recommender)
- Need project context (use context-analyzer)
- Validating artifacts (use trace-check or quality-advisor)

---

## Skill Development

### Creating New Skills

**Directory Structure**:
```
.claude/skills/
├── README.md (this file)
├── {skill_name}.md (full skill documentation)
├── {skill_name}_quickref.md (quick reference card)
└── {skill_name}/ (optional: external managed skill)
```

**Skill Documentation Template**:
```markdown
# {skill_name} Skill

**Skill ID**: `{skill_name}`
**Version**: 1.0
**Created**: YYYY-MM-DD
**Purpose**: [One-line description]

## Overview
[Detailed description]

## When to Use This Skill
[Use cases and decision criteria]

## Skill Inputs
[Required and optional parameters]

## Skill Workflow
[Step-by-step process]

## Example Usage
[Concrete examples]

## Skill Constraints
[What NOT to do]

## Quality Gates
[Definition of Done]

## Error Handling
[Common errors and resolutions]

## Output Format
[Generated artifacts]

## References
[Related documents and templates]
```

**Quick Reference Template**:
```markdown
# {skill_name} - Quick Reference

**Skill**: `{skill_name}`
**Purpose**: [One-line description]

## Quick Start
[Minimal invocation example]

## What This Skill Does
[Numbered list of steps]

## Key Principles
[Core concepts]

## Output Example
[Expected results]

## Common User Requests
[Typical scenarios]

## When NOT to Use This Skill
[Decision criteria for skipping]

## References
[Links to full skill and related docs]
```

### Skill Quality Standards

**Documentation Requirements**:
- Complete workflow documentation (≥500 words)
- Quick reference card (≤2000 words)
- Example usage with inputs/outputs
- Error handling guidance
- Quality gates (Definition of Done)

**Testing Requirements**:
- Validate skill with ≥2 example scenarios
- Document edge cases and error conditions
- Provide expected outputs for validation

**Maintenance**:
- Review skills quarterly
- Update when related templates change
- Deprecate skills if workflow changes

---

## Skill Invocation

**General Format**:
```bash
/skill {skill_name}
```

**With Parameters** (if supported by skill):
```bash
/skill {skill_name} --param1 value1 --param2 value2
```

**Getting Help**:
```bash
/skill {skill_name} --help
```

---

## Skill Categories

### Document Generation Skills
- `generate_implementation_plan` - Generate IMPL documents from BRD analysis
- `charts_flow` - Create and manage Mermaid architecture diagrams with SVG generation
- `adr-roadmap` - Generate phased implementation roadmaps from ADRs

### Project Management Skills
- `project-mgnt` - MVP/MMP/MMR implementation planning and release management
- `adr-roadmap` - ADR-driven implementation roadmap with timeline and dependencies

### Development Workflow Skills
- `doc-flow` - SDD workflow transformation (BRD → Code)

### Automation & Integration Skills
- `n8n` - Workflow automation, custom nodes, and service integrations

### Quality Assurance Skills
- `trace-check` - Validate and update bidirectional traceability across SDD artifacts

### Agent Development & AI Skills
- `google-adk` - Multi-agent systems and agentic application development with Python

### AI Assistant Skills
- `skill-recommender` - Intelligent skill suggestion based on user intent and project context
- `context-analyzer` - Project structure scanning and context building for documentation
- `quality-advisor` - Proactive quality guidance and anti-pattern detection during artifact creation
- `workflow-optimizer` - SDD workflow navigation and next-step recommendations

---

## Related Documentation

**SDD Workflow**:
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md]({project_root}/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Authoritative SDD workflow
- [index.md]({project_root}/ai_dev_flow/index.md) - Traceability flow diagram

**Templates**:
- [IMPL-TEMPLATE.md]({project_root}/ai_dev_flow/IMPL/IMPL-TEMPLATE.md) - Implementation plan template
- [CTR-TEMPLATE.md]({project_root}/ai_dev_flow/CTR/CTR-TEMPLATE.md) - API contract template
- [SPEC-TEMPLATE.yaml]({project_root}/ai_dev_flow/SPEC/SPEC-TEMPLATE.yaml) - Technical specification template
- [TASKS-TEMPLATE.md]({project_root}/ai_dev_flow/TASKS/TASKS-TEMPLATE.md) - Code generation plan template

**Decision Guides**:
- [WHEN_TO_CREATE_IMPL.md]({project_root}/ai_dev_flow/WHEN_TO_CREATE_IMPL.md) - IMPL creation criteria
- [ID_NAMING_STANDARDS.md]({project_root}/ai_dev_flow/ID_NAMING_STANDARDS.md) - Document ID conventions

---

## Framework Architecture Note

### Layer Groupings

The framework uses **functional layer groupings** for workflow clarity rather than formal layer numbers. Artifacts flow through functional stages:

- **Business Layer**: BRD → PRD → EARS
- **Testing Layer**: BDD
- **Architecture Layer**: ADR → SYS
- **Requirements Layer**: REQ
- **Implementation Strategy Layer**: IMPL (optional)
- **Interface Layer**: CTR (optional)
- **Technical Specs Layer**: SPEC
- **Execution Planning Layer**: TASKS → IPLAN
- **Code & Validation Layer**: Code → Tests → Validation → Review → Production

This functional grouping simplifies understanding the workflow while maintaining full traceability. Each artifact accumulates tags from previous functional layers as it progresses through the workflow.

---

**Index Version**: 1.7
**Last Updated**: 2025-11-29
**Next Review**: 2026-02-29 (quarterly)
