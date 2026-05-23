---
name: skill-recommender
description: Intelligent skill suggestion engine that analyzes user intent and project context to recommend appropriate documentation skills
metadata:
  tags:
    - sdd-workflow
    - ai-assistant
    - utility
    - shared-architecture
  custom_fields:
    layer: null
    artifact_type: null
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: utility
    upstream_artifacts: [PRD-01, ADR-01]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-05-23"
    versioning_policy: "tracks skill behavior"
---

# skill-recommender

## Purpose

Analyze user requests and recommend appropriate documentation skills from the AI Dev Flow framework catalog.

**Problem Solved**: Users must know which of 25+ skills to invoke for their documentation task, requiring deep framework knowledge.

**Solution**: Parse user intent, match against skill catalog, and provide ranked recommendations with confidence scores and rationale.

## When to Use This Skill

**Use skill-recommender when**:
- User is unsure which skill to use for a documentation task
- Starting a new documentation workflow and need guidance
- Want to discover available skills for a specific intent
- Need help navigating the skill catalog

**Do NOT use when**:
- User explicitly requests a specific skill (e.g., "/skill doc-prd")
- Performing non-documentation tasks
- User is experienced and knows the target skill

## Skill Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| user_request | string | Yes | Natural language description of what user wants to do |
| project_context | object | No | Project structure and existing artifacts (from context-analyzer) |
| max_recommendations | number | No | Maximum recommendations to return (default: 3) |

## Skill Workflow

### Step 1: Parse User Intent

Extract action verbs and targets from the user request:

**Intent Categories**:
| Category | Signal Keywords | Example Request |
|----------|-----------------|-----------------|
| `create` | create, write, draft, new, add | "Create a new PRD for user authentication" |
| `update` | update, modify, edit, change, revise | "Update the traceability section of SPEC-01" |
| `validate` | validate, check, verify, audit, review | "Check if my artifacts have proper traceability" |
| `analyze` | analyze, review, examine, inspect | "Analyze the project documentation structure" |
| `plan` | plan, roadmap, schedule, organize | "Create an implementation roadmap from ADRs" |

**Target Extraction**:
| Target | Signal Keywords | Maps To |
|--------|-----------------|---------|
| business requirements | business, brd, objectives | doc-brd |
| product requirements | product, prd, features, user stories | doc-prd |
| formal requirements | ears, formal, when-the-shall | doc-ears |
| test scenarios | bdd, scenarios, gherkin | doc-bdd |
| architecture decisions | adr, architecture, decision | doc-adr |
| technical specification | spec, specification, interfaces, contracts, data models, yaml | doc-spec |
| test definitions | tdd, test cases, test plan, quality thresholds | doc-tdd |
| implementation plan | iplan, implementation plan, file manifest, execution | doc-iplan |
| traceability | trace, traceability, links | trace-check |
| validation | validate, quality, compliance | doc-validator |
| diagrams | diagram, mermaid, chart, flow | charts-flow, mermaid-gen |
| roadmap | roadmap, adr implementation | adr-roadmap |

### Step 2: Match Skills

Match parsed intent against skill catalog:

**Skill Catalog** (Core Documentation Skills):

| Skill ID | Category | Layer | Description |
|----------|----------|-------|-------------|
| doc-brd | core-workflow | 1 | Business Requirements Documents |
| doc-prd | core-workflow | 2 | Product Requirements Documents |
| doc-ears | core-workflow | 3 | EARS Formal Requirements |
| doc-bdd | core-workflow | 4 | BDD Test Scenarios |
| doc-adr | core-workflow | 5 | Architecture Decision Records |
| doc-spec | core-workflow | 6 | Technical Specifications |
| doc-tdd | core-workflow | 7 | Test-Driven Development guides |
| doc-iplan | core-workflow | 8 | Implementation Plans |

**Quality Assurance Skills**:

| Skill ID | Category | Description |
|----------|----------|-------------|
| trace-check | quality-assurance | Validate bidirectional traceability |
| doc-validator | quality-assurance | Validate documentation standards |
| code-review | quality-assurance | Code quality review |
| contract-tester | quality-assurance | Test API contracts |

**Utility Skills**:

| Skill ID | Category | Description |
|----------|----------|-------------|
| charts-flow | utility | Mermaid architecture diagrams |
| mermaid-gen | utility | Generate Mermaid diagrams |
| analytics-flow | utility | Analytics and data analysis |
| project-init | utility | Initialize project structure |

**Planning Skills**:

| Skill ID | Category | Description |
|----------|----------|-------------|
| adr-roadmap | planning | ADR implementation roadmaps |
| doc-flow | planning | SDD workflow orchestration |

### Step 3: Score and Rank

Calculate confidence scores based on:

| Factor | Weight | Description |
|--------|--------|-------------|
| Intent match | 40% | How well request matches skill intent signals |
| Target match | 30% | Explicit skill/artifact type mentioned |
| Context fit | 20% | Project state and workflow position |
| Usage patterns | 10% | Common skill sequences |

**Confidence Levels**:
- **High** (≥80%): Strong match, recommend with confidence
- **Medium** (50-79%): Good match, include alternative options
- **Low** (<50%): Weak match, suggest clarification

### Step 4: Generate Recommendations

Format recommendations with rationale:

**Output Format**:
```yaml
recommendations:
  - skill: doc-prd
    confidence: 92%
    rationale: "Request mentions 'product requirements' and 'features' - direct match for PRD creation"
    next_steps: "Run /skill doc-prd to create Product Requirements Document"

  - skill: doc-brd
    confidence: 65%
    rationale: "May need BRD first if business requirements not yet documented"
    condition: "Use if no BRD exists for this feature"

  - skill: doc-ears
    confidence: 45%
    rationale: "EARS follows PRD in workflow - consider after PRD completion"
    condition: "Use after PRD is complete"

clarification_needed: false
clarification_question: null
```

## Example Usage

### Example 1: Clear Intent

**User Request**: "I need to create a product requirements document for a new authentication feature"

**Skill Analysis**:
```
Intent: create (keywords: create, need)
Target: product requirements (keywords: product requirements document)
Domain: authentication feature
```

**Recommendations**:
```yaml
recommendations:
  - skill: doc-prd
    confidence: 95%
    rationale: "Explicit request for Product Requirements Document"
    next_steps: "Run /skill doc-prd to create PRD for authentication feature"

  - skill: doc-brd
    confidence: 40%
    rationale: "BRD may be needed upstream if not already created"
    condition: "Check if BRD exists for authentication feature"
```

### Example 2: Ambiguous Intent

**User Request**: "Help me document the system architecture"

**Skill Analysis**:
```
Intent: create (keywords: document)
Target: ambiguous - could be ADR, SPEC, or diagrams
```

**Recommendations**:
```yaml
recommendations:
  - skill: doc-adr
    confidence: 60%
    rationale: "Architecture decisions typically documented in ADRs"

  - skill: doc-spec
    confidence: 55%
    rationale: "Technical specifications capture component interfaces and architecture contracts"

  - skill: charts-flow
    confidence: 50%
    rationale: "Architecture diagrams visualize system structure"

clarification_needed: true
clarification_question: "What aspect of architecture? (1) Decisions/rationale (ADR), (2) Technical specs (SPEC), (3) Visual diagrams?"
```

### Example 3: Validation Request

**User Request**: "Check if my documentation has proper links between artifacts"

**Skill Analysis**:
```
Intent: validate (keywords: check)
Target: traceability (keywords: links between artifacts)
```

**Recommendations**:
```yaml
recommendations:
  - skill: trace-check
    confidence: 98%
    rationale: "Direct request for traceability validation"
    next_steps: "Run /skill trace-check to validate bidirectional links"
```

## Integration with Other Skills

| Integration | Description |
|-------------|-------------|
| context-analyzer | Receives project context for better recommendations |
| doc-flow | Can be invoked by doc-flow for skill discovery |
| workflow-optimizer | Shares workflow position awareness |

## Quality Gates

### Definition of Done

- [ ] User request parsed successfully
- [ ] At least one skill recommendation provided
- [ ] Confidence scores calculated for all recommendations
- [ ] Rationale included for each recommendation
- [ ] Clarification question generated when ambiguous

### Performance Targets

| Metric | Target |
|--------|--------|
| Response latency | <500ms |
| Recommendation accuracy | ≥85% |
| User acceptance rate | ≥70% |

## Traceability

**Required Tags**:
```
@prd: PRD.01.01.1dbc
@adr: ADR-01
```

### Upstream Sources

| Source | Type | Reference |
|--------|------|-----------|
| PRD-01 | Product Requirements | [PRD-01]({project_root}/framework/layers/02_PRD/PRD-01_ai_assisted_documentation_features.yaml#PRD-01) |
| ADR-01 | Architecture Decision | [ADR-01]({project_root}/framework/layers/05_ADR/ADR-01_ai_powered_documentation_assistant_architecture.yaml#ADR-01) |

### Downstream Artifacts

| Artifact | Type | Reference |
|----------|------|-----------|
| Selected doc-* skill | Skill Execution | Invoked based on recommendation |

---

## Version Information

**Version**: 1.0.0
**Created**: 2025-11-29
**Status**: Active
**Author**: AI Dev Flow Framework Team
