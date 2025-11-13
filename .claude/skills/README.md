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
- Complete 16-layer SDD workflow (Strategy → BRD → PRD → EARS → BDD → ADR → SYS → REQ → IMPL → CTR → SPEC → TASKS → tasks_plans → Code → Tests → Validation)
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

**Purpose**: Agent Development Kit from Google

**Status**: Managed skill (external)
**Version**: See skill directory
**Documentation**: See skill directory for details

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

### Quality Assurance Skills
- `trace-check` - Validate and update bidirectional traceability across SDD artifacts

### External Framework Skills
- `google-adk` - Agent Development Kit integration

---

## Related Documentation

**SDD Workflow**:
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../../docs_templates/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Authoritative SDD workflow
- [index.md](../../docs_templates/ai_dev_flow/index.md) - Traceability flow diagram

**Templates**:
- [IMPL-TEMPLATE.md](../../docs_templates/ai_dev_flow/IMPL/IMPL-TEMPLATE.md) - Implementation plan template
- [CTR-TEMPLATE.md](../../docs_templates/ai_dev_flow/CONTRACTS/CTR-TEMPLATE.md) - API contract template
- [SPEC-TEMPLATE.yaml](../../docs_templates/ai_dev_flow/SPEC/SPEC-TEMPLATE.yaml) - Technical specification template
- [TASKS-TEMPLATE.md](../../docs_templates/ai_dev_flow/TASKS/TASKS-TEMPLATE.md) - Code generation plan template

**Decision Guides**:
- [WHEN_TO_CREATE_IMPL.md](../../docs_templates/ai_dev_flow/WHEN_TO_CREATE_IMPL.md) - IMPL creation criteria
- [ID_NAMING_STANDARDS.md](../../docs_templates/ai_dev_flow/ID_NAMING_STANDARDS.md) - Document ID conventions

---

**Index Version**: 1.4
**Last Updated**: 2025-11-11
**Next Review**: 2026-02-11 (quarterly)
