---
title: "quality-advisor: Proactive quality guidance for artifact creation"
name: quality-advisor
description: Proactive quality guidance system that monitors artifact creation and provides real-time feedback on documentation quality
tags:
  - sdd-workflow
  - ai-assistant
  - quality-assurance
  - shared-architecture
custom_fields:
  layer: null
  artifact_type: null
  architecture_approaches: [ai-agent-based]
  priority: primary
  development_status: active
  skill_category: quality-assurance
  upstream_artifacts: [PRD-00, ADR-000]
  downstream_artifacts: []
---

# quality-advisor

## Purpose

Provide proactive quality guidance during artifact creation by monitoring section completion, detecting anti-patterns, and validating compliance with SDD standards.

**Problem Solved**: Documentation quality varies based on user expertise. Issues are typically found after artifact creation during validation, causing rework.

**Solution**: Real-time quality monitoring that identifies issues during creation, suggests improvements, and validates compliance before the artifact is complete.

## When to Use This Skill

**Use quality-advisor when**:
- Creating a new documentation artifact
- Reviewing an artifact before submission
- Want to check compliance with template requirements
- Need guidance on common mistakes to avoid
- Validating cumulative tagging compliance

**Do NOT use when**:
- Full traceability validation needed (use trace-check)
- Validating entire project (use doc-validator)
- Non-SDD documentation

## Skill Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| artifact_content | string | Yes | Current content of artifact being created |
| artifact_type | string | Yes | Type of artifact (BRD, PRD, SPEC, etc.) |
| artifact_id | string | No | Document ID if assigned (e.g., PRD-00) |
| check_level | string | No | Level of checks: "quick", "standard" (default), "strict" |

## Skill Workflow

### Step 1: Identify Template Requirements

Load requirements for the specified artifact type:

**Template Requirements by Type** (per LAYER_REGISTRY v1.6):

| Layer | Artifact | Required Sections | Min Tags | Special Requirements |
|-------|----------|-------------------|----------|----------------------|
| 1 | BRD | Document Control, Purpose, Stakeholders, Objectives, Requirements, Traceability | 0 | None |
| 2 | PRD | Document Control, Problem, Goals, Non-Goals, User Needs, Features, KPIs, Traceability | 1 (@brd) | KPIs must be quantitative |
| 3 | EARS | Document Control, Requirements (WHEN-THE-SHALL), Traceability | 2 (@brd, @prd) | EARS syntax validation |
| 4 | BDD | Feature, Scenarios, Tags | 3 (@brd, @prd, @ears) | Gherkin syntax |
| 5 | ADR | Document Control, Context, Decision, Rationale, Consequences, Traceability | 4 (@brd, @prd, @ears, @bdd) | Decision must be explicit |
| 6 | SYS | Document Control, System Requirements, Traceability | 5 | Technical specifications |
| 7 | REQ | Document Control, Requirement, Acceptance Criteria, Traceability | 6 | Atomic requirement |
| 8 | CTR | Document Control, Interfaces, Data Models, Contract Clauses, Traceability | 7 | Dual-file format (md+yaml) |
| 9 | SPEC | id, description, methods, traceability | 7 | YAML format |
| 10 | TSPEC | Document Control, Test Cases, Coverage, Traceability | 8 | UTEST/ITEST/STEST/FTEST types |
| 11 | TASKS | Document Control, Tasks, Dependencies, Traceability | 9 | Actionable TODOs |

**Note**: Layers 12-14 (CODE, TESTS, VALIDATION) are execution layers, not documentation artifacts.

### Step 2: Check Section Completion

Verify all required sections are present and populated:

**Section Detection**:
```python
# Section patterns by type
SECTION_PATTERNS = {
    "document_control": r"## Document Control",
    "problem_statement": r"## \d+\. Problem",
    "goals": r"## \d+\. Goals",
    "non_goals": r"## \d+\. Non-Goals",
    "traceability": r"## \d+\. Traceability|## 7\. Traceability",
    "kpis": r"## \d+\. KPIs|## KPIs",
    "acceptance_criteria": r"### Acceptance Criteria|## Acceptance",
}
```

**Completion Scoring**:
```yaml
section_completion:
  document_control:
    present: true
    complete: true
    score: 100%
  problem_statement:
    present: true
    complete: true
    score: 100%
  goals:
    present: true
    complete: partial
    score: 60%
    issues:
      - "Goal G-003 missing success metric"
      - "Goals not prioritized (P0, P1, P2)"
  kpis:
    present: true
    complete: false
    score: 30%
    issues:
      - "KPI 'user adoption' lacks quantitative target"
      - "No performance metrics defined"
  traceability:
    present: true
    complete: partial
    score: 70%
    issues:
      - "Missing @brd tag (required for Layer 2)"
      - "Downstream artifacts section empty"
  overall_score: 72%
```

### Step 3: Detect Anti-Patterns

Identify common documentation mistakes:

**Anti-Pattern Catalog**:

| ID | Name | Description | Severity | Detection |
|----|------|-------------|----------|-----------|
| AP-001 | Missing Document Control | No version/status metadata | Error | Section not found |
| AP-002 | Placeholder Text | `[TBD]`, `TODO`, `XXX` in content | Warning | Regex match |
| AP-003 | Vague Acceptance Criteria | No measurable outcomes | Warning | Missing numbers/percentages |
| AP-004 | Missing Traceability Tags | Required upstream tags absent | Error | Tag count check |
| AP-005 | Broken Internal Links | `[ID](path)` links with invalid paths | Error | Link validation |
| AP-006 | ID Format Violation | Non-standard document ID | Error | Regex match |
| AP-007 | Empty Required Section | Section header present but no content | Warning | Content length check |
| AP-008 | Orphan Artifact | No upstream references | Warning | Traceability check |
| AP-009 | Missing Anchor | Document lacks primary anchor ID | Warning | Anchor detection |
| AP-010 | Duplicate ID Reference | Same ID referenced multiple times | Info | Duplicate check |
| AP-011 | Section Count Mismatch | `total_sections` metadata differs from actual section files | Error | SEC-E001 validation |
| AP-012 | Cross-Reference Title Mismatch | Link text differs from target section heading | Error | XREF-E001/E002 validation |
| AP-013 | Mixed ID Notation | Document uses both hyphen (TYPE-NN) and dot (TYPE.NN) formats | Error | IDPAT-E003 validation |
| AP-014 | Diagram-Text Inconsistency | Mermaid diagram components don't match prose claims | Warning | DIAG-E001/W001 validation |
| AP-015 | Undefined Acronym | Acronym used without first-use definition | Error | TERM-E002 validation |
| AP-016 | Count Mismatch | Stated count (e.g., "18 requirements") differs from itemized total | Error | COUNT-E001 validation |
| AP-017 | Forward Reference to Non-Existent Document | Upstream doc references specific downstream IDs (e.g., PRD→ADR-01) | Error | FWDREF-E001 validation |

**Anti-Pattern Detection Output**:
```yaml
anti_patterns_detected:
  - id: AP-004
    name: Missing Traceability Tags
    severity: error
    location: "Section 7: Traceability"
    details: "PRD requires @brd tag (Layer 2 cumulative requirement)"
    suggestion: "Add '@brd: BRD.NN.EE.SS' to Traceability section"

  - id: AP-003
    name: Vague Acceptance Criteria
    severity: warning
    location: "Section 6: KPIs"
    details: "KPI 'improve user experience' has no measurable target"
    suggestion: "Add quantitative metric: 'User satisfaction ≥4.0/5.0'"

  - id: AP-002
    name: Placeholder Text
    severity: warning
    location: "Section 4: User Needs, line 45"
    details: "Found placeholder '[TBD]'"
    suggestion: "Replace with actual user need or remove section"
```

### Step 4: Validate Cumulative Tagging

Check tag hierarchy compliance:

**Tag Hierarchy by Layer** (per LAYER_REGISTRY v1.6):

```yaml
cumulative_tag_requirements:
  BRD:
    layer: 1
    required_tags: []
    tag_count: 0
  PRD:
    layer: 2
    required_tags: [@brd]
    tag_count: 1
  EARS:
    layer: 3
    required_tags: [@brd, @prd]
    tag_count: 2
  BDD:
    layer: 4
    required_tags: [@brd, @prd, @ears]
    tag_count: 3
  ADR:
    layer: 5
    required_tags: [@brd, @prd, @ears, @bdd]
    tag_count: 4
  SYS:
    layer: 6
    required_tags: [@brd, @prd, @ears, @bdd, @adr]
    tag_count: 5
  REQ:
    layer: 7
    required_tags: [@brd, @prd, @ears, @bdd, @adr, @sys]
    tag_count: 6
  CTR:
    layer: 8
    required_tags: [@brd, @prd, @ears, @bdd, @adr, @sys, @req]
    tag_count: 7
  SPEC:
    layer: 9
    required_tags: [@brd, @prd, @ears, @bdd, @adr, @sys, @req]
    optional_tags: [@ctr]
    tag_count: 7
  TSPEC:
    layer: 10
    required_tags: [@brd, @prd, @ears, @bdd, @adr, @sys, @req, @spec]
    optional_tags: [@ctr]
    tag_count: 8
  TASKS:
    layer: 11
    required_tags: [@brd, @prd, @ears, @bdd, @adr, @sys, @req, @spec, @tspec]
    optional_tags: [@ctr]
    tag_count: 9
```

**Tag Validation Output**:
```yaml
tag_validation:
  artifact_type: PRD
  layer: 2
  required_tags: ["@brd"]
  found_tags: []
  missing_tags: ["@brd"]
  status: fail
  message: "Layer 2 artifact requires @brd tag"
  fix_suggestion: |
    Add to Traceability section:
    ```
    @brd: BRD.001.003
    ```
```

### Step 5: Check Naming Conventions

Validate document ID, element ID, and filename conventions per `doc-naming` skill.

**Naming Rules** (see `doc-naming` skill for complete standards):

```yaml
naming_conventions:
  # Document ID format
  document_id_format: "{TYPE}-{NN}"  # e.g., PRD-01
  filename_format: "{TYPE}-{NN}_{slug}.md"  # e.g., PRD-01_authentication.md

  # Element ID format (unified)
  element_id_format: "{TYPE}.{NN}.{TT}.{SS}"  # e.g., PRD.01.09.01

  # Threshold tag format
  threshold_format: "@threshold: {TYPE}.{NN}.{key}"  # e.g., @threshold: PRD.01.perf.auth.p99

  slug_rules:
    - lowercase
    - underscores for spaces
    - no special characters
    - descriptive of content
```

**Naming Validation Output**:

```yaml
naming_validation:
  document_id: PRD-01
  id_format_valid: true
  filename: "PRD-01_authentication.md"
  filename_valid: true
  element_ids:
    total: 24
    valid: 22
    invalid: 2
    issues:
      - "PRD.01.25.01 - code 25 not valid for PRD"
      - "US-001 - deprecated pattern, use PRD.01.09.SS"
  threshold_tags:
    total: 8
    valid: 7
    invalid: 1
    issues:
      - "perf.auth.p99 - missing TYPE.NN prefix"
  legacy_patterns_detected: 1
```

**Reference**: See `doc-naming` skill for complete element type codes and validation rules.

### Step 6: Generate Quality Report

Assemble comprehensive quality assessment:

**Quality Report Format**:
```yaml
quality_report:
  artifact_id: PRD-00
  artifact_type: PRD
  check_timestamp: 2025-11-29T14:30:00Z
  check_level: standard

  overall_status: warning
  quality_score: 72%

  summary:
    errors: 1
    warnings: 3
    info: 1
    passed_checks: 12

  section_completion:
    complete: 5
    partial: 2
    missing: 0
    score: 85%

  anti_patterns:
    - severity: error
      count: 1
      details: "Missing @brd tag"
    - severity: warning
      count: 3
      details: "Vague KPIs, placeholder text, incomplete goals"

  tag_compliance:
    status: fail
    required: 1
    found: 0
    missing: ["@brd"]

  naming_compliance:
    status: pass
    all_checks_passed: true

  recommendations:
    high_priority:
      - "Add @brd tag to Traceability section (required for Layer 2)"
    medium_priority:
      - "Add quantitative targets to KPIs"
      - "Remove [TBD] placeholder from User Needs section"
      - "Prioritize goals with P0, P1, P2 labels"
    low_priority:
      - "Consider adding more downstream artifact references"

  next_steps:
    - "Fix error-level issues before submission"
    - "Address warnings for quality improvement"
    - "Run trace-check after completion for full validation"
```

## Example Usage

### Example 1: Mid-Creation Check

**User Request**: "Check quality of my PRD in progress"

**Quality Feedback**:
```yaml
quality_status: in_progress
current_score: 65%
blocking_issues:
  - "Missing Document Control section at top"
  - "No traceability section found"
improvement_suggestions:
  - "Add Document Control table before Section 1"
  - "Create Section 7: Traceability with @brd tag"
  - "Add measurable KPIs (currently vague)"
completion_estimate: "3 sections need attention"
```

### Example 2: Pre-Submission Review

**User Request**: "Is this SPEC ready for submission?"

**Quality Assessment**:
```yaml
submission_readiness: not_ready
blocking_issues:
  - severity: error
    issue: "Missing @req tag (required for Layer 10)"
  - severity: error
    issue: "YAML syntax error at line 45"
warnings:
  - "verification section references non-existent BDD-015"
  - "id field uses camelCase instead of snake_case"
recommendation: "Fix 2 errors before submission"
```

### Example 3: Quick Compliance Check

**User Request**: "Quick check on tag compliance for this REQ"

**Tag Check Output**:
```yaml
artifact_type: REQ
layer: 7
tag_compliance: pass
required_tags:
  - "@brd: BRD.01.01.01 ✓"
  - "@prd: PRD.01.07.01 ✓"
  - "@ears: EARS.01.24.01 ✓"
  - "@bdd: BDD.01.13.01 ✓"
  - "@adr: ADR-02 ✓"
  - "@sys: SYS.01.25.01 ✓"
tag_count: "6/6 required tags present"
status: "Ready for downstream artifacts"
```

## Integration with Other Skills

| Integration | Description |
|-------------|-------------|
| `doc-naming` | Element ID format, threshold tags, legacy pattern detection |
| `doc-*-autopilot` | Invoked during Phase 3 (artifact generation) for real-time guidance |
| `doc-*-validator` | Structural validation (use quality-advisor for creation, validator for post-creation) |
| `doc-*-reviewer` | Content review (use quality-advisor for creation, reviewer for final QA) |
| `trace-check` | Shares validation logic for traceability checks |
| `context-analyzer` | Uses project context for reference validation |

## Quality Gates

### Definition of Done

- [ ] All required sections identified
- [ ] Section completion scored
- [ ] Anti-patterns detected and reported
- [ ] Cumulative tagging validated
- [ ] Naming conventions checked
- [ ] Quality report generated
- [ ] Actionable recommendations provided

### Performance Targets

| Metric | Target |
|--------|--------|
| Quick check latency | <100ms |
| Standard check latency | <500ms |
| Strict check latency | <1s |
| False positive rate | <5% |

## Traceability

**Required Tags**:

```markdown
@prd: PRD.000.003
@adr: ADR-000
```

### Upstream Sources

| Source | Type | Reference |
|--------|------|-----------|
| PRD-00 | Product Requirements | [PRD-00]({project_root}/ai_dev_flow/PRD/PRD-00_ai_assisted_documentation_features.md#PRD-00) |
| ADR-000 | Architecture Decision | [ADR-000]({project_root}/ai_dev_flow/ADR/ADR-00_ai_powered_documentation_assistant_architecture.md#ADR-000) |

### Downstream Artifacts

| Artifact | Type | Reference |
|----------|------|-----------|
| doc-* skills | Skill Consumer | Quality checks during creation |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2026-02-08 | Updated layer assignments per LAYER_REGISTRY v1.6; Added CTR (L8), TSPEC (L10); Fixed SPEC to L9, TASKS to L11; Integrated doc-naming skill for element ID validation |
| 1.0.0 | 2025-11-29 | Initial release |

**Status**: Active
**Author**: AI Dev Flow Framework Team
