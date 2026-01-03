# adr-roadmap - Quick Reference

**Skill**: `adr-roadmap`
**Version**: 1.0.0
**Purpose**: Generate comprehensive phased implementation roadmaps from Architecture Decision Records for any project

---

## Quick Start

**Invocation**:
```bash
/skill adr-roadmap
```

**Minimal Example**:
```
Use adr-roadmap skill to create implementation roadmap.

Inputs:
- ADR directory: {project_root}/docs/ADR/
- Project context: Web application, 3 developers, 6-month timeline

Generate roadmap in {project_root}/docs/ADR/ADR-00_IMPLEMENTATION-ROADMAP.md
```

---

## What This Skill Does

1. **Reads all ADR files** from specified directory
2. **Extracts metadata**: complexity ratings, effort estimates, dependencies
3. **Builds dependency graph**: identifies critical path and parallel opportunities
4. **Calculates complexity scores**: aggregates effort from ADR assessments
5. **Creates phase structure**: groups ADRs into logical implementation phases
6. **Generates timeline**: estimates duration based on team size and complexity
7. **Produces comprehensive roadmap**: executive summary, phase breakdown, risks, testing strategy

---

## Key Principles

### Dependency-First Sequencing
- Upstream ADRs must be in earlier phases
- Critical path determines minimum timeline
- Independent ADRs can execute in parallel

### Phase Decomposition Models

**POC-MVP-Prod** (default):
```
Phase 1: POC → Validate technical feasibility (2-3 weeks)
Phase 2: MVP → Multi-user capable (4-6 weeks)
Phase 3: Production → Cloud deployment, security (6-8 weeks)
Phase 4: Scale → Performance optimization (4-6 weeks)
Phase 5: Advanced → Extended features (ongoing)
```

**Iterative**:
```
Fixed-duration iterations (2-4 weeks each)
Each iteration: implement ADR cluster → test → deploy
```

**Waterfall**:
```
Phase by ADR category: Infrastructure → Core → Integration → Optimization
```

### Complexity Scoring
```
1-2: Simple (1-2 days)
3: Moderate (3-5 days)
4: Complex (1-2 weeks)
5: Architectural (3-4 weeks)
```

### Technical Debt Management
- **POC**: Hardcoded credentials, no tests, local deployment (acceptable)
- **MVP**: Basic error handling, simple caching (acceptable)
- **Production**: Zero tolerance for security/compliance shortcuts
- **Scale**: Partial optimization (acceptable)

---

## Output Example

**Generated File**: `{project}/docs/ADR/ADR-00_IMPLEMENTATION-ROADMAP.md`

**Structure** (~1,400 lines):
```markdown
# ADR Implementation Roadmap

## Executive Summary
- Total: 27 ADRs across 5 phases, 16-23 weeks, 3 FTE

## Phase 1: POC (2-3 weeks)
### Objectives: Validate TWS API integration
### ADRs: ADR-000, 001, 002, 003 (partial)
### Deliverables: Working local MCP server
### Success Criteria: Claude Desktop queries TWS data

## Phase 2: MVP (4-6 weeks)
[Similar structure]

## ADR Dependency Matrix
[Mermaid flowchart showing relationships]

## Technical Debt Management
[Acceptable shortcuts per phase]

## Risk Assessment
[Risks and mitigation per phase]

## Testing Strategy
[Test approach per phase]

## Traceability
[ADR → Phase → Timeline mapping]
```

---

## Common User Requests

### Request 1: "Create POC-focused roadmap"
**Skill interprets**:
- Prioritize Phase 1 with minimal ADRs
- Identify POC-critical ADRs only
- Defer all non-essential ADRs
- Target 2-3 week timeline

### Request 2: "Migration project roadmap with rollback plans"
**Skill applies**:
- Brownfield adaptation pattern
- Phase by risk level (low-risk first)
- Include rollback procedures per phase
- Add dual-run validation

### Request 3: "Tight deadline, 10 engineers"
**Skill calculates**:
- Identify parallelizable ADRs
- Create concurrent work streams
- Allocate engineers across tracks
- Optimize timeline with resource scaling

### Request 4: "Hardware-constrained IoT project"
**Skill phases**:
- Phase 1: Software simulation (before hardware)
- Phase 2: Hardware integration (after prototype ready)
- Gate phases on hardware availability

---

## Decision Flowchart

```
User Request
    ↓
Read ADRs from directory
    ↓
Parse dependencies → Build graph
    ↓
Calculate complexity → Sum effort
    ↓
Select phase model → POC-MVP-Prod / Iterative / Waterfall
    ↓
Apply phasing algorithm
    ↓
    ├─→ Respect dependencies (upstream first)
    ├─→ Balance phase size (<8 weeks)
    ├─→ Isolate high-risk ADRs
    └─→ Align with milestones
    ↓
Calculate timeline → Effort / Team Size
    ↓
Generate roadmap document
    ↓
Validate quality gates
    ↓
Output: ADR-00_IMPLEMENTATION-ROADMAP.md
```

---

## Adaptation Quick Guide

| Project Type | Phase Strategy | Key Considerations |
|--------------|----------------|-------------------|
| **Greenfield** | Front-load infrastructure | Clean slate, enable parallelization |
| **Brownfield** | Phase by risk level | Backward compatibility, rollback plans |
| **Refactoring** | Phase by module | Minimize customer impact, heavy testing |
| **Migration** | Dual-run periods | Validate in parallel, gradual cutover |
| **Embedded** | Gate on hardware | Software first, integrate when ready |

---

## When NOT to Use This Skill

❌ **Single ADR**: Direct implementation, no roadmap needed

❌ **No ADRs yet**: Use `project-mngt` skill to plan from requirements (BRD/PRD)

❌ **Documentation generation**: Use `doc-flow` skill for SYS/REQ/SPEC creation

❌ **Architecture diagrams only**: Use `charts-flow` skill for Mermaid diagrams

❌ **Informational ADRs**: No implementation required, roadmap not applicable

---

## Troubleshooting

### Issue: "Circular dependency detected"
**Cause**: ADR-A depends on ADR-B which depends on ADR-A
**Resolution**: User must update ADRs to break cycle
**Action**: Skill reports circular chain, cannot proceed

### Issue: "Phase exceeds 8 weeks"
**Cause**: Too many ADRs in single phase
**Resolution**: Skill automatically splits into sub-phases
**Action**: Review phase breakdown, adjust if needed

### Issue: "Missing complexity ratings"
**Cause**: ADRs lack implementation assessment sections
**Resolution**: Skill estimates complexity from ADR content
**Action**: Warn user, proceed with estimates (default 3/5)

### Issue: "Timeline unrealistic for team size"
**Cause**: 100 person-weeks effort with 2 FTE team = 50 weeks
**Resolution**: Skill reports constraint conflict
**Action**: User adjusts team size or timeline expectations

---

## Quick Syntax Reference

### Required Inputs
```
ADR directory: /absolute/path/to/ADR/
Project context: "[type], [team size], [constraints]"
```

### Optional Inputs
```
Output file: /path/to/roadmap.md (default: {adr_dir}/ADR-00_IMPLEMENTATION-ROADMAP.md)
Max phase duration: 8 weeks (default)
Phase model: poc-mvp-prod | iterative | waterfall (default: poc-mvp-prod)
Team size: 3 FTE (default)
Prioritize ADR: ADR-002 (force first)
```

### Example Invocations

**Minimal**:
```
Use adr-roadmap skill.
ADR directory: {project_root}/docs/ADR/
Project context: Trading system, 3 developers
```

**Full Options**:
```
Use adr-roadmap skill.
ADR directory: {project_root}/arch/decisions/
Project context: Migration project, 8 engineers, 9 months
Phase model: iterative
Team size: 8
Max phase duration: 4 weeks
Output: {project_root}/docs/ROADMAP.md
```

---

## Expected Results

**Processing Time**: 30-60 seconds for 20-30 ADRs

**Output Size**: 1,000-2,000 lines depending on ADR count

**Artifacts Generated**:
1. Roadmap markdown file
2. Executive summary table
3. Phase breakdown (1-5+ phases)
4. Mermaid dependency graph
5. Mermaid Gantt chart
6. Risk assessment tables
7. Technical debt tracking
8. Testing strategy per phase
9. Traceability matrix

**Quality Validation**:
- All ADRs mapped to phases ✓
- Dependencies validated (no cycles) ✓
- Timeline realistic for team size ✓
- Mermaid diagrams render correctly ✓
- Language objective (CLAUDE.md compliant) ✓

---

## Related Skills

**project-mngt**: Use for requirement-based planning (BRD/PRD → MVP)
**doc-flow**: Use for generating SYS/REQ/SPEC from ADRs
**charts-flow**: Combine for enhanced Mermaid visualizations

---

## References

**Full Skill Documentation**: [SKILL.md](./adr-roadmap/SKILL.md)

**Related Documentation**:
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md]({project_root}/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)
- [ADR-TEMPLATE.md]({project_root}/ai_dev_flow/ADR-TEMPLATE.md)
- [ID_NAMING_STANDARDS.md]({project_root}/ai_dev_flow/ID_NAMING_STANDARDS.md)

**Example Output**: `{project_root}/docs/ADR/ADR-00_IMPLEMENTATION-ROADMAP.md`

---

**Version**: 1.0.0
**Last Updated**: 2025-01-08
