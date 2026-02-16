# SDD Project Model v2.2 - Implementation Plan

**Version**: 2.0
**Created**: 2026-02-16
**Updated**: 2026-02-16
**Source**: `ai_dev_ssd_flow/PROJECT/PROJECT_MODEL.md`
**Location**: `ai_dev_ssd_flow/PROJECT/IMPLEMENTATION_PLAN.md`

---

## 1. Executive Summary

This implementation plan defines the scope, architecture decisions, specifications, and tasks required to implement the automation and tooling described in `PROJECT_MODEL.md`.

The SDD Project Model v2.2 extends the core SDD framework with:
- **Sprint Integration**: TASKS→GitHub Issue automation, drift checking, Project V2 board sync
- **CI/CD Validation**: Artifact validators integrated in workflows with 4-Gate system
- **Feedback Loop**: CHG-based change management during sprints
- **Sprint 0 Support**: Checklist automation, RACI matrix generation, decision framework

---

## 2. BRD-01: Business Requirements Document

### 2.1 Business Context

**Project Name**: SDD Project Model v2.2 Automation Tooling
**Target Launch**: Sprint-based delivery over 5 weeks
**PRD-Ready Score Target**: 90/100

### 2.2 Business Objectives

| ID | Objective | Measurable Outcome |
|----|-----------|-------------------|
| BO-01 | Enable TASKS-to-GitHub Issue synchronization | 100% of TASKS elements mapped to GitHub Issues with full traceability tags |
| BO-02 | Detect documentation drift automatically | Weekly drift reports generated with <7 day artifact currency |
| BO-03 | Integrate SDD validation into CI/CD | 95%+ validator pass rate at first attempt |
| BO-04 | Support change management feedback loop | CHG documents created within 2 days for L2, 5 days for L3 changes |
| BO-05 | Automate Sprint 0 setup | Sprint 0 checklist generated with 100% prerequisite coverage |
| BO-06 | Enable 4-Gate validation | All gate transitions validated before artifact progression |

### 2.3 Functional Requirements

| ID | Requirement | Priority | Complexity |
|----|-------------|----------|------------|
| FR-01 | `tasks_to_github.py` converts TASKS YAML to GitHub Issues with traceability | P0 | 3 |
| FR-02 | `drift_check.py` compares artifact modification dates vs issue close dates | P1 | 3 |
| FR-03 | `validate_artifact.py` wrapper invokes per-type validators | P1 | 2 |
| FR-04 | GitHub Issue template for SDD tasks with @brd/@prd/@spec/@tasks fields | P0 | 2 |
| FR-05 | CI workflow validates changed artifacts on PR and push | P0 | 3 |
| FR-06 | CHG templates with 4-Gate validation integration | P1 | 3 |
| FR-07 | Sprint 0 checklist generator with prerequisite tracking | P1 | 2 |
| FR-08 | RACI matrix generator from PROJECT_MODEL roles | P2 | 2 |
| FR-09 | Configuration file for automation scripts | P1 | 2 |
| FR-10 | GitHub Project V2 board sync with custom fields | P1 | 3 |
| FR-11 | Decision framework automation (layer selection) | P2 | 2 |
| FR-12 | Sample data and worked example fixtures | P2 | 1 |

### 2.4 Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| QA-01 | Script execution time | <30s for single artifact validation |
| QA-02 | YAML parsing reliability | Handle malformed YAML gracefully |
| QA-03 | GitHub API rate limiting | Respect 5000 req/hour limit, exponential backoff |
| QA-04 | CI workflow timeout | <10 minutes for full validation |
| QA-05 | Test coverage | 85%+ unit test coverage |
| QA-06 | Documentation coverage | 100% public API documented |

### 2.5 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Requirement-to-code traceability | 100% | `trace-check` script |
| Documentation currency | <7 days lag | Drift check report |
| Validator pass rate | >95% first attempt | CI metrics |
| TASKS-to-Issue automation | 100% | Manual audit per sprint |
| Sprint 0 completion | <1 week | Checklist completion rate |
| 4-Gate compliance | 100% | Gate validation logs |

---

## 3. ADR Decisions Required

### ADR-01: GitHub API vs GraphQL for Issue Creation

**Context**: The `tasks_to_github.py` script needs to create GitHub Issues with custom fields.

**Decision**: Use PyGithub library with REST API for issue creation; GraphQL for Project V2 board operations.

**Rationale**:
- REST API handles basic issue CRUD operations well
- Project V2 custom fields require GraphQL mutations
- PyGithub is mature and well-documented

**Consequences**:
- Dependency on `PyGithub` and `requests` libraries
- Two API styles in one script
- Must handle authentication for both

### ADR-02: Validator Orchestration Strategy

**Context**: Multiple validators exist in `ai_dev_ssd_flow/scripts/`. Need unified invocation.

**Decision**: Create `validate_artifact.py` as thin wrapper that delegates to existing validators based on artifact type.

**Rationale**:
- Avoid duplicating validation logic
- Single entry point for CI
- Existing validators are well-tested

**Consequences**:
- Wrapper maintains compatibility with existing validators
- Must handle exit codes from child scripts
- Configuration for validator paths

### ADR-03: Configuration File Format

**Context**: Scripts need configurable settings (repo name, project board, thresholds).

**Decision**: Use YAML configuration at `ai_dev_ssd_flow/PROJECT/config/project_model.yaml` with environment variable overrides.

**Rationale**:
- YAML is human-readable and consistent with TASKS format
- Environment variables enable CI/CD flexibility
- Single config file reduces complexity

**Consequences**:
- PyYAML dependency
- Config file must be versioned
- Document all configuration options

### ADR-04: 4-Gate Validation Architecture

**Context**: PROJECT_MODEL.md defines 4 gates (GATE-01, GATE-05, GATE-09, GATE-12) for layer transitions.

**Decision**: Implement gate validation as part of `validate_artifact.py` with gate-specific rule sets.

**Rationale**:
- Gates map to layer ranges (L1-4, L5-8, L9-11, L12-14)
- Reuse existing validators with gate-aware orchestration
- Single validation entry point

**Consequences**:
- Gate rules must be configurable
- CHG documents trigger appropriate gate validation
- CI workflow must support gate-level checks

### ADR-05: Sprint 0 Automation Strategy

**Context**: Sprint 0 requires completing Tier 1 artifacts (BRD→BDD) and ADRs before Sprint 1.

**Decision**: Create `sprint0_setup.py` that generates checklist and tracks completion.

**Rationale**:
- Checklist ensures nothing is missed
- Integrates with GitHub Issues for tracking
- Validates Tier 1 artifacts are complete

**Consequences**:
- Dependency on PROJECT_MODEL.md Section 4.5 checklist
- Must validate artifact readiness scores
- Creates blocking issues for Sprint 1

---

## 4. SPEC: Technical Specifications

### 4.1 SPEC-01: tasks_to_github.py

**Traceability**: @brd: BRD-01:FR-01, FR-10

**Component Architecture**:
```
tasks_to_github.py
├── TasksParser (class)
│   ├── load_yaml(filepath) -> Dict
│   ├── extract_tasks(yaml_data) -> List[TaskElement]
│   └── validate_traceability(task) -> bool
├── GitHubIssueCreator (class)
│   ├── __init__(repo, token)
│   ├── find_existing_issue(tasks_id) -> Optional[Issue]
│   ├── create_issue(task) -> Issue
│   └── update_issue(issue, task) -> Issue
├── ProjectV2Sync (class)
│   ├── __init__(repo, project_number, token)
│   ├── add_issue_to_project(issue) -> ProjectItem
│   ├── set_custom_fields(item, task) -> None
│   └── update_status(item, status) -> None
├── IssueFormatter (class)
│   ├── format_title(task, phase) -> str
│   ├── format_body(task) -> str
│   └── format_labels(task) -> List[str]
└── main(args) -> int
```

**Input Format** (from TASKS YAML):
```yaml
metadata:
  spec_reference: SPEC-NN
  sprint: "Sprint X.Y"
  phase: "PN"

tasks:
  - id: TASKS-NN.TT.SS
    title: "Task title"
    traceability:
      brd: "BRD-NN:BRD.NN.TT.SS"
      prd: "PRD-NN:PRD.NN.TT.SS"
      spec: "SPEC-NN"
    acceptance_criteria: [...]
    size: "S|M|L|XL"
    priority: "P0|P1|P2"
    dependencies: []
```

**Output**: GitHub Issues with:
- Title: `[{PHASE}-{TASK_ID}] {TITLE}`
- Labels: `ai:ready`, `source:sdd`, `size:{SIZE}`, `priority:{PRIORITY}`
- Body: Formatted markdown with traceability section
- Project V2: Added to board with custom fields (Phase, Size, Priority, Sprint)

**CLI Interface**:
```bash
python scripts/tasks_to_github.py \
  --tasks-file docs/11_TASKS/TASKS-01.yaml \
  --repo owner/repo-name \
  --sprint "Sprint 2.1" \
  --project-number 31 \
  --dry-run
```

### 4.2 SPEC-02: drift_check.py

**Traceability**: @brd: BRD-01:FR-02

**Component Architecture**:
```
drift_check.py
├── ArtifactScanner (class)
│   ├── scan_directory(path) -> List[Artifact]
│   ├── get_last_modified(artifact) -> datetime
│   └── extract_tasks_refs(artifact) -> List[str]
├── GitHubIssueQuery (class)
│   ├── get_closed_issues(repo, sprint) -> List[Issue]
│   └── get_issue_close_date(issue) -> datetime
├── DriftAnalyzer (class)
│   ├── compare_timestamps(artifact, issues) -> DriftStatus
│   ├── calculate_drift_days(artifact) -> int
│   └── generate_report(drifts) -> str
└── main(args) -> int
```

**Detection Logic**:
1. Scan `docs/` for artifacts with modification dates
2. Query GitHub for closed issues in sprint
3. Flag artifacts where: `artifact_modified < issue_closed - threshold`
4. Generate markdown report with drift details

**CLI Interface**:
```bash
python scripts/drift_check.py \
  --sdd-root docs/ \
  --repo owner/repo-name \
  --github-project 31 \
  --max-age-days 14 \
  --report tmp/drift_report.md
```

### 4.3 SPEC-03: validate_artifact.py

**Traceability**: @brd: BRD-01:FR-03, FR-06

**Component Architecture**:
```
validate_artifact.py
├── ArtifactTypeDetector (class)
│   ├── detect_type(filepath) -> str
│   ├── detect_layer(filepath) -> int
│   └── get_validator_path(type) -> str
├── GateValidator (class)
│   ├── get_applicable_gate(layer) -> str
│   ├── validate_gate_requirements(artifact, gate) -> GateResult
│   └── check_upstream_gates(artifact) -> bool
├── ValidatorRunner (class)
│   ├── run_validator(path, artifact) -> ValidationResult
│   └── collect_results(results) -> int
└── main(args) -> int
```

**Validation Dispatch Table**:
| Artifact Type | Layer | Gate | Validator Script |
|---------------|-------|------|-----------------|
| BRD | 1 | GATE-01 | `validate_cross_document.py --type BRD` |
| PRD | 2 | GATE-01 | `validate_cross_document.py --type PRD` |
| EARS | 3 | GATE-01 | `validate_cross_document.py --type EARS` |
| BDD | 4 | GATE-01 | `validate_cross_document.py --type BDD` |
| ADR | 5 | GATE-05 | `validate_cross_document.py --type ADR` |
| SYS | 6 | GATE-05 | `validate_cross_document.py --type SYS` |
| REQ | 7 | GATE-05 | `validate_cross_document.py --type REQ` |
| CTR | 8 | GATE-05 | `validate_schema_sync.py` |
| SPEC | 9 | GATE-09 | `validate_cross_document.py --type SPEC` |
| TSPEC | 10 | GATE-09 | `validate_cross_document.py --type TSPEC` |
| TASKS | 11 | GATE-09 | `validate_cross_document.py --type TASKS` |
| Code | 12 | GATE-12 | `validate_tags_against_docs.py` |
| Tests | 13 | GATE-12 | `validate_terminology.py` |

**CLI Interface**:
```bash
python scripts/validate_artifact.py --path docs/BRD/BRD-01.md --strict --gate GATE-01
```

### 4.4 SPEC-04: GitHub Issue Template

**Traceability**: @brd: BRD-01:FR-04

**File**: `ai_dev_ssd_flow/PROJECT/.github/ISSUE_TEMPLATE/sdd-task.yml`

**Template Structure**:
```yaml
name: SDD Task
description: Task generated from TASKS specification
title: "[${PHASE}-${TASK_ID}] ${TITLE}"
labels: ["ai:ready", "source:sdd"]
body:
  - type: markdown
    attributes:
      value: |
        ## Traceability
        Auto-populated from TASKS file

  - type: input
    id: brd_ref
    attributes:
      label: "@brd"
      description: "BRD reference"
    validations:
      required: true

  - type: input
    id: prd_ref
    attributes:
      label: "@prd"
      description: "PRD reference"

  - type: input
    id: spec_ref
    attributes:
      label: "@spec"
      description: "SPEC reference"
    validations:
      required: true

  - type: input
    id: tasks_ref
    attributes:
      label: "@tasks"
      description: "TASKS element ID"
    validations:
      required: true

  - type: dropdown
    id: size
    attributes:
      label: "Size"
      options:
        - S
        - M
        - L
        - XL

  - type: dropdown
    id: priority
    attributes:
      label: "Priority"
      options:
        - P0
        - P1
        - P2

  - type: textarea
    id: acceptance
    attributes:
      label: "Acceptance Criteria"
      description: "Imported from SPEC"
      placeholder: |
        - [ ] Criterion 1
        - [ ] Criterion 2
    validations:
      required: true

  - type: textarea
    id: implementation
    attributes:
      label: "Implementation Notes"
      description: "From TASKS guidance"
```

### 4.5 SPEC-05: CI Workflow

**Traceability**: @brd: BRD-01:FR-05

**File**: `ai_dev_ssd_flow/PROJECT/.github/workflows/sdd-validation.yml`

**Workflow Jobs**:
1. `validate-artifacts`: Run validators on changed doc files
2. `validate-gates`: Check gate requirements for layer transitions
3. `update-matrix`: Update traceability matrix on main push
4. `drift-check`: Weekly scheduled drift detection

**Trigger Conditions**:
- `pull_request` on `docs/**/*.md`, `docs/**/*.yaml`, `docs/**/*.feature`
- `push` to `main` on `docs/**/*`
- `schedule` for weekly drift check (Friday 17:00 EST)

### 4.6 SPEC-06: Configuration File

**Traceability**: @brd: BRD-01:FR-09

**File**: `ai_dev_ssd_flow/PROJECT/config/project_model.yaml`

**Configuration Schema**:
```yaml
# Project settings
project:
  name: "{PROJECT_NAME}"
  repo: "{GITHUB_ORG}/{REPO_NAME}"
  board_number: {PROJECT_BOARD_NUMBER}

# Validation settings
validation:
  strict_mode: true
  coverage_threshold: 85
  max_complexity: 10

# Drift check settings
drift_check:
  max_age_days: 14
  schedule: "0 17 * * 5"  # Friday 5pm
  excluded_patterns:
    - "docs/generated/*"
    - "docs/archive/*"

# Quality gates
quality_gates:
  GATE-01:
    layers: [1, 2, 3, 4]
    validators: ["doc-brd-validator", "doc-prd-validator", "doc-ears-validator", "doc-bdd-validator"]
    threshold: 90
  GATE-05:
    layers: [5, 6, 7, 8]
    validators: ["doc-adr-validator", "doc-sys-validator", "doc-req-validator", "doc-ctr-validator"]
    threshold: 90
  GATE-09:
    layers: [9, 10, 11]
    validators: ["doc-spec-validator", "doc-tspec-validator", "doc-tasks-validator"]
    threshold: 90
  GATE-12:
    layers: [12, 13, 14]
    validators: ["trace-check", "coverage-check"]
    threshold: 85

# Sprint settings
sprint:
  duration_days: 14
  sprint_0_max_days: 7

# Labels
labels:
  source: "source:sdd"
  ai_ready: "ai:ready"
  sizes: ["size:S", "size:M", "size:L", "size:XL"]
  priorities: ["priority:P0", "priority:P1", "priority:P2"]
```

### 4.7 SPEC-07: CHG Generator with 4-Gate Integration

**Traceability**: @brd: BRD-01:FR-06

**File**: `ai_dev_ssd_flow/scripts/chg_generator.py`

**Component Architecture**:
```
chg_generator.py
├── ChangeClassifier (class)
│   ├── classify_change(description) -> ChangeLevel  # L1, L2, L3
│   ├── identify_affected_layers(change) -> List[int]
│   └── determine_gates(layers) -> List[str]
├── CHGDocumentGenerator (class)
│   ├── create_chg_document(change, level) -> str
│   ├── generate_impact_analysis(change) -> ImpactReport
│   └── create_approval_checklist(gates) -> str
├── GateTransitionValidator (class)
│   ├── validate_gate_entry(artifact, gate) -> bool
│   ├── validate_gate_exit(artifact, gate) -> bool
│   └── generate_gate_report(results) -> str
└── main(args) -> int
```

**Change Levels**:
| Level | Description | Gates Required | Approval |
|-------|-------------|----------------|----------|
| L1 (Patch) | Bug fix, no spec change | None | Developer |
| L2 (Minor) | Scope change, spec update | Affected gates | PO |
| L3 (Major) | Architecture change | All gates | Architect |

**CLI Interface**:
```bash
python scripts/chg_generator.py \
  --description "Add email localization support" \
  --affected-layers 2,9,11 \
  --output docs/CHG/CHG-001/
```

### 4.8 SPEC-08: Sprint 0 Setup

**Traceability**: @brd: BRD-01:FR-07

**File**: `ai_dev_ssd_flow/scripts/sprint0_setup.py`

**Component Architecture**:
```
sprint0_setup.py
├── Sprint0Checklist (class)
│   ├── generate_checklist(project_config) -> Checklist
│   ├── check_tier1_artifacts() -> Dict[str, bool]
│   ├── check_adr_decisions() -> Dict[str, bool]
│   └── validate_sprint1_readiness() -> bool
├── ChecklistIssueCreator (class)
│   ├── create_sprint0_epic(checklist) -> Issue
│   ├── create_task_issues(checklist) -> List[Issue]
│   └── link_blocking_dependencies() -> None
├── ArtifactReadinessChecker (class)
│   ├── check_brd_readiness() -> ReadinessScore
│   ├── check_prd_readiness() -> ReadinessScore
│   ├── check_ears_readiness() -> ReadinessScore
│   ├── check_bdd_readiness() -> ReadinessScore
│   └── check_adr_completeness() -> ReadinessScore
└── main(args) -> int
```

**Sprint 0 Checklist** (from PROJECT_MODEL.md Section 4.5):
| # | Task | Output | Blocks |
|---|------|--------|--------|
| 0.1 | Identify blocking technical questions | Question list | All |
| 0.2 | Research each question | Research notes | 0.3 |
| 0.3 | Document decisions as ADRs | ADR-01 through ADR-NN | Sprint 1 |
| 0.4 | Validate BRD completeness | BRD validation report | 0.5 |
| 0.5 | Generate PRD from BRD | PRD-01 through PRD-NN | 0.6 |
| 0.6 | Generate EARS from PRD | EARS-01 through EARS-NN | 0.7 |
| 0.7 | Generate BDD from EARS | BDD-01 through BDD-NN | Sprint 1 |
| 0.8 | Set up GitHub Project board | Configured board | Sprint 1 |

**CLI Interface**:
```bash
python scripts/sprint0_setup.py \
  --repo owner/repo-name \
  --project-number 31 \
  --config ai_dev_ssd_flow/PROJECT/config/project_model.yaml
```

### 4.9 SPEC-09: RACI Matrix Generator

**Traceability**: @brd: BRD-01:FR-08

**File**: `ai_dev_ssd_flow/scripts/raci_generator.py`

**Component Architecture**:
```
raci_generator.py
├── RACIParser (class)
│   ├── load_roles(config) -> List[Role]
│   ├── load_activities(config) -> List[Activity]
│   └── load_assignments(config) -> Dict[Activity, Dict[Role, str]]
├── RACIMatrixGenerator (class)
│   ├── generate_matrix(roles, activities, assignments) -> str
│   ├── export_markdown(matrix) -> str
│   └── export_csv(matrix) -> str
├── RACIValidator (class)
│   ├── validate_single_accountable(matrix) -> bool
│   ├── validate_no_gaps(matrix) -> bool
│   └── generate_warnings(matrix) -> List[str]
└── main(args) -> int
```

**RACI Matrix** (from PROJECT_MODEL.md Section 5.1):
| Activity | Project Lead | Product Manager | Architect | Developer | QA Lead | DevOps |
|----------|:------------:|:---------------:|:---------:|:---------:|:-------:|:------:|
| BRD creation | A | R | C | I | I | I |
| PRD creation | A | R | C | I | C | I |
| EARS creation | A | C | R | I | C | I |
| BDD creation | A | C | C | I | R | I |
| ADR creation | A | I | R | C | I | C |
| SYS creation | A | I | R | C | C | I |
| REQ creation | A | I | R | C | C | I |
| SPEC creation | A | I | C | R | I | I |
| TSPEC creation | A | I | I | C | R | I |
| TASKS creation | A | I | C | R | C | I |
| GitHub Issue sync | A | I | I | R | I | C |
| Validator CI setup | A | I | I | C | I | R |
| CHG management | R | C | A | C | C | I |

**CLI Interface**:
```bash
python scripts/raci_generator.py \
  --config ai_dev_ssd_flow/PROJECT/config/project_model.yaml \
  --output docs/RACI_MATRIX.md \
  --format markdown
```

### 4.10 SPEC-10: Decision Framework Automation

**Traceability**: @brd: BRD-01:FR-11

**File**: `ai_dev_ssd_flow/scripts/layer_selector.py`

**Component Architecture**:
```
layer_selector.py
├── WorkItemClassifier (class)
│   ├── classify_work_type(description) -> WorkType
│   ├── is_new_capability() -> bool
│   ├── is_scope_change() -> bool
│   ├── is_bug_fix() -> bool
│   └── is_hotfix() -> bool
├── LayerRecommender (class)
│   ├── recommend_layers(work_type) -> List[int]
│   ├── recommend_artifacts(layers) -> List[str]
│   └── estimate_effort(layers) -> str
├── DecisionTreeRunner (class)
│   ├── run_interactive() -> LayerRecommendation
│   └── run_automated(work_item) -> LayerRecommendation
└── main(args) -> int
```

**Decision Matrix** (from PROJECT_MODEL.md Section 10.1):
| Work Type | Layers | Artifacts |
|-----------|--------|-----------|
| New Feature | 1-11 | BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC, TSPEC, TASKS |
| Enhancement | 2-11 | PRD→TASKS |
| Bug Fix | 11 | TASKS only |
| Hotfix | None | Code only + 72h retroactive docs |
| Config Change | 5, 11 | ADR + TASKS |
| Refactoring | 5, 9-11 | ADR + SPEC + TSPEC + TASKS |

**CLI Interface**:
```bash
python scripts/layer_selector.py --interactive
python scripts/layer_selector.py --work-type "bug fix" --description "Fix null pointer in auth"
```

---

## 5. TASKS Breakdown

### Phase 0: Project Setup (Day 1-2)

| Task ID | Title | Dependencies | Size | Priority |
|---------|-------|--------------|------|----------|
| TASKS-00.01.01 | Create PROJECT/config/ directory structure | None | S | P0 |
| TASKS-00.01.02 | Create project_model.yaml configuration | TASKS-00.01.01 | M | P0 |
| TASKS-00.01.03 | Create PROJECT/.github/ directory structure | None | S | P0 |
| TASKS-00.02.01 | Create sample TASKS YAML fixture (Budget Alert) | None | M | P1 |
| TASKS-00.02.02 | Create sample BRD/PRD/SPEC fixtures | TASKS-00.02.01 | M | P1 |

### Phase 1: Core Scripts (Week 1)

| Task ID | Title | Dependencies | Size | Priority |
|---------|-------|--------------|------|----------|
| TASKS-01.01.01 | Implement TasksParser class | TASKS-00.01.02 | M | P0 |
| TASKS-01.01.02 | Implement GitHubIssueCreator class | TASKS-01.01.01 | L | P0 |
| TASKS-01.01.03 | Implement ProjectV2Sync class | TASKS-01.01.02 | L | P0 |
| TASKS-01.01.04 | Implement IssueFormatter class | TASKS-01.01.01 | M | P0 |
| TASKS-01.01.05 | Wire up tasks_to_github.py CLI | TASKS-01.01.01-04 | S | P0 |
| TASKS-01.02.01 | Implement ArtifactScanner class | TASKS-00.01.02 | M | P1 |
| TASKS-01.02.02 | Implement GitHubIssueQuery class | None | M | P1 |
| TASKS-01.02.03 | Implement DriftAnalyzer class | TASKS-01.02.01-02 | M | P1 |
| TASKS-01.02.04 | Wire up drift_check.py CLI | TASKS-01.02.01-03 | S | P1 |

### Phase 2: GitHub Integration (Week 2)

| Task ID | Title | Dependencies | Size | Priority |
|---------|-------|--------------|------|----------|
| TASKS-02.01.01 | Create sdd-task.yml issue template | None | S | P0 |
| TASKS-02.01.02 | Create sdd-validation.yml workflow | TASKS-02.02.01 | M | P0 |
| TASKS-02.02.01 | Implement ArtifactTypeDetector class | None | M | P1 |
| TASKS-02.02.02 | Implement GateValidator class | TASKS-02.02.01 | L | P1 |
| TASKS-02.02.03 | Implement ValidatorRunner class | TASKS-02.02.01 | M | P1 |
| TASKS-02.02.04 | Wire up validate_artifact.py CLI | TASKS-02.02.01-03 | S | P1 |
| TASKS-02.03.01 | Add config loading to all scripts | TASKS-00.01.02 | S | P1 |

### Phase 3: CHG and 4-Gate System (Week 3)

| Task ID | Title | Dependencies | Size | Priority |
|---------|-------|--------------|------|----------|
| TASKS-03.01.01 | Implement ChangeClassifier class | None | M | P1 |
| TASKS-03.01.02 | Implement CHGDocumentGenerator class | TASKS-03.01.01 | L | P1 |
| TASKS-03.01.03 | Implement GateTransitionValidator class | TASKS-02.02.02 | L | P1 |
| TASKS-03.01.04 | Wire up chg_generator.py CLI | TASKS-03.01.01-03 | S | P1 |
| TASKS-03.02.01 | Implement Sprint0Checklist class | None | M | P1 |
| TASKS-03.02.02 | Implement ChecklistIssueCreator class | TASKS-03.02.01 | M | P1 |
| TASKS-03.02.03 | Implement ArtifactReadinessChecker class | TASKS-02.02.01 | M | P1 |
| TASKS-03.02.04 | Wire up sprint0_setup.py CLI | TASKS-03.02.01-03 | S | P1 |

### Phase 4: Templates and Documentation (Week 4)

| Task ID | Title | Dependencies | Size | Priority |
|---------|-------|--------------|------|----------|
| TASKS-04.01.01 | Implement RACIParser class | None | S | P2 |
| TASKS-04.01.02 | Implement RACIMatrixGenerator class | TASKS-04.01.01 | M | P2 |
| TASKS-04.01.03 | Implement RACIValidator class | TASKS-04.01.02 | S | P2 |
| TASKS-04.01.04 | Wire up raci_generator.py CLI | TASKS-04.01.01-03 | S | P2 |
| TASKS-04.02.01 | Implement WorkItemClassifier class | None | M | P2 |
| TASKS-04.02.02 | Implement LayerRecommender class | TASKS-04.02.01 | M | P2 |
| TASKS-04.02.03 | Implement DecisionTreeRunner class | TASKS-04.02.01-02 | M | P2 |
| TASKS-04.02.04 | Wire up layer_selector.py CLI | TASKS-04.02.01-03 | S | P2 |
| TASKS-04.03.01 | Write SETUP_GUIDE.md | All scripts | M | P1 |
| TASKS-04.03.02 | Write scripts/README.md | All scripts | M | P1 |
| TASKS-04.03.03 | Document anti-patterns from PROJECT_MODEL Section 11.6 | None | S | P2 |

### Phase 5: Validation and Testing (Week 5)

| Task ID | Title | Dependencies | Size | Priority |
|---------|-------|--------------|------|----------|
| TASKS-05.01.01 | Unit tests for TasksParser | TASKS-01.01.01 | M | P0 |
| TASKS-05.01.02 | Unit tests for GitHubIssueCreator | TASKS-01.01.02 | M | P0 |
| TASKS-05.01.03 | Unit tests for ProjectV2Sync | TASKS-01.01.03 | M | P0 |
| TASKS-05.01.04 | Integration test for tasks_to_github.py | TASKS-01.01.05 | L | P0 |
| TASKS-05.02.01 | Unit tests for drift_check.py | TASKS-01.02.04 | M | P1 |
| TASKS-05.02.02 | Unit tests for validate_artifact.py | TASKS-02.02.04 | M | P1 |
| TASKS-05.02.03 | Unit tests for chg_generator.py | TASKS-03.01.04 | M | P1 |
| TASKS-05.02.04 | Unit tests for sprint0_setup.py | TASKS-03.02.04 | M | P1 |
| TASKS-05.03.01 | End-to-end workflow validation | All | L | P0 |
| TASKS-05.03.02 | Validate against Budget Alert worked example | TASKS-00.02.01-02, All | L | P0 |

---

## 6. Directory Structure

```
ai_dev_ssd_flow/
├── PROJECT/                           # SDD Project Model v2.2
│   ├── PROJECT_MODEL.md               # Methodology document
│   ├── IMPLEMENTATION_PLAN.md         # This document
│   ├── SETUP_GUIDE.md                 # TASKS-04.03.01
│   ├── ANTI_PATTERNS.md               # TASKS-04.03.03
│   ├── config/
│   │   └── project_model.yaml         # SPEC-06
│   ├── templates/
│   │   ├── CHG-PROJECT-TEMPLATE.md    # CHG template
│   │   ├── SPRINT0_CHECKLIST.md       # Sprint 0 checklist
│   │   └── RACI_MATRIX.md             # RACI template
│   ├── .github/
│   │   ├── ISSUE_TEMPLATE/
│   │   │   └── sdd-task.yml           # SPEC-04
│   │   └── workflows/
│   │       └── sdd-validation.yml     # SPEC-05
│   ├── fixtures/                      # Test data
│   │   ├── budget_alert/              # Worked example
│   │   │   ├── BRD-01.md
│   │   │   ├── PRD-01.md
│   │   │   ├── SPEC-05.yaml
│   │   │   └── TASKS-05.yaml
│   │   └── README.md
│   └── tests/
│       ├── test_tasks_parser.py       # TASKS-05.01.01
│       ├── test_issue_creator.py      # TASKS-05.01.02
│       ├── test_project_v2_sync.py    # TASKS-05.01.03
│       ├── test_drift_check.py        # TASKS-05.02.01
│       ├── test_validate_artifact.py  # TASKS-05.02.02
│       ├── test_chg_generator.py      # TASKS-05.02.03
│       ├── test_sprint0_setup.py      # TASKS-05.02.04
│       └── conftest.py                # Shared fixtures
├── scripts/                           # Scripts (existing + new)
│   ├── tasks_to_github.py             # SPEC-01 (NEW)
│   ├── drift_check.py                 # SPEC-02 (NEW)
│   ├── validate_artifact.py           # SPEC-03 (NEW)
│   ├── chg_generator.py               # SPEC-07 (NEW)
│   ├── sprint0_setup.py               # SPEC-08 (NEW)
│   ├── raci_generator.py              # SPEC-09 (NEW)
│   ├── layer_selector.py              # SPEC-10 (NEW)
│   ├── requirements-project.txt       # Dependencies for PROJECT scripts
│   ├── README.md                      # TASKS-04.03.02
│   └── (existing validators...)
└── (existing template directories: 01_BRD/, 02_PRD/, etc.)
```

---

## 7. Dependencies

### 7.1 External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| PyGithub | >=2.0 | GitHub REST API |
| PyYAML | >=6.0 | YAML parsing |
| Click | >=8.0 | CLI interface |
| requests | >=2.28 | HTTP requests (GraphQL) |
| rich | >=13.0 | Terminal output formatting |
| pytest | >=7.0 | Testing framework |
| pytest-cov | >=4.0 | Coverage reporting |

### 7.2 Internal Dependencies

| Script | Depends On | Location |
|--------|-----------|----------|
| tasks_to_github.py | extract_tags.py | ai_dev_ssd_flow/scripts/ |
| validate_artifact.py | validate_cross_document.py | ai_dev_ssd_flow/scripts/ |
| validate_artifact.py | validate_tags_against_docs.py | ai_dev_ssd_flow/scripts/ |
| drift_check.py | project_model.yaml | ai_dev_ssd_flow/PROJECT/config/ |
| chg_generator.py | validate_artifact.py | ai_dev_ssd_flow/scripts/ |
| sprint0_setup.py | tasks_to_github.py | ai_dev_ssd_flow/scripts/ |

---

## 8. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GitHub API rate limiting | Medium | High | Implement exponential backoff, use GraphQL batching |
| YAML parsing failures | Low | Medium | Graceful error handling, schema validation |
| Validator compatibility | Low | High | Test wrapper against all 11 existing validators |
| CI workflow timeouts | Medium | Medium | Parallelize validation jobs, cache dependencies |
| Project V2 API changes | Medium | Medium | Abstract GraphQL queries, version pin schema |
| Gate validation complexity | Medium | High | Comprehensive test coverage, incremental rollout |

---

## 9. Acceptance Criteria Summary

### Definition of Done for Phase 0
- [ ] Directory structure created at `ai_dev_ssd_flow/PROJECT/`
- [ ] Configuration file validated against schema
- [ ] Sample fixtures for Budget Alert example

### Definition of Done for Phase 1
- [ ] `tasks_to_github.py` converts sample TASKS file to Issues (dry-run)
- [ ] `tasks_to_github.py` syncs issues to Project V2 board (dry-run)
- [ ] `drift_check.py` generates report for test repo
- [ ] Unit tests pass with 85%+ coverage

### Definition of Done for Phase 2
- [ ] Issue template renders correctly in GitHub
- [ ] CI workflow validates changed artifacts on PR
- [ ] Gate validation integrated in validate_artifact.py
- [ ] Config file loads without errors

### Definition of Done for Phase 3
- [ ] `chg_generator.py` creates CHG documents with gate analysis
- [ ] `sprint0_setup.py` generates checklist and creates issues
- [ ] 4-Gate validation working end-to-end
- [ ] All CHG levels (L1, L2, L3) tested

### Definition of Done for Phase 4
- [ ] `raci_generator.py` produces valid RACI matrix
- [ ] `layer_selector.py` interactive mode works
- [ ] All templates pass doc-validator
- [ ] Setup guide enables new project onboarding
- [ ] Script documentation complete
- [ ] Anti-patterns documented

### Definition of Done for Phase 5
- [ ] All unit tests pass with 85%+ coverage
- [ ] Integration test creates real Issues (in test repo)
- [ ] End-to-end workflow validated with Budget Alert example
- [ ] All 10 scripts tested and documented

---

## 10. Traceability Matrix

| BRD Req | SPEC | TASKS | Test |
|---------|------|-------|------|
| FR-01 | SPEC-01 | TASKS-01.01.* | TASKS-05.01.01-04 |
| FR-02 | SPEC-02 | TASKS-01.02.* | TASKS-05.02.01 |
| FR-03 | SPEC-03 | TASKS-02.02.* | TASKS-05.02.02 |
| FR-04 | SPEC-04 | TASKS-02.01.01 | - |
| FR-05 | SPEC-05 | TASKS-02.01.02 | TASKS-05.03.01 |
| FR-06 | SPEC-07 | TASKS-03.01.* | TASKS-05.02.03 |
| FR-07 | SPEC-08 | TASKS-03.02.* | TASKS-05.02.04 |
| FR-08 | SPEC-09 | TASKS-04.01.* | - |
| FR-09 | SPEC-06 | TASKS-00.01.02, TASKS-02.03.01 | - |
| FR-10 | SPEC-01 | TASKS-01.01.03 | TASKS-05.01.03 |
| FR-11 | SPEC-10 | TASKS-04.02.* | - |
| FR-12 | - | TASKS-00.02.* | TASKS-05.03.02 |

---

## 11. Quick Start Commands

```bash
# Phase 0: Project Setup
mkdir -p ai_dev_ssd_flow/PROJECT/{config,templates,fixtures,.github/{ISSUE_TEMPLATE,workflows},tests}

# Generate SDD artifacts (Tier 1)
/doc-brd-autopilot           # Generate BRD from reference docs
/doc-prd-autopilot BRD-01    # Generate PRD from BRD
/doc-ears-autopilot PRD-01   # Generate EARS from PRD
/doc-bdd-autopilot EARS-01   # Generate BDD from EARS
/doc-adr                     # Create ADR for decisions

# Generate SDD artifacts (Tier 2)
/doc-sys-autopilot ADR-01    # Generate SYS from ADR
/doc-req-autopilot SYS-01    # Generate REQ from SYS
/doc-spec-autopilot REQ-01   # Generate SPEC from REQ
/doc-tasks-autopilot SPEC-01 # Generate TASKS from SPEC

# Sprint integration (NEW)
python scripts/tasks_to_github.py --tasks-file docs/11_TASKS/TASKS-01.yaml --repo owner/repo --project-number 31

# Sprint 0 setup (NEW)
python scripts/sprint0_setup.py --repo owner/repo --project-number 31

# CHG generation (NEW)
python scripts/chg_generator.py --description "Add feature X" --affected-layers 2,9,11

# Layer selection (NEW)
python scripts/layer_selector.py --interactive

# Validation
/doc-validator docs/                              # Validate all artifacts
python scripts/validate_artifact.py --path docs/BRD/BRD-01.md --gate GATE-01
python scripts/drift_check.py --sdd-root docs/   # Check documentation drift

# RACI matrix (NEW)
python scripts/raci_generator.py --output docs/RACI_MATRIX.md
```

---

## 12. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-16 | AI Assistant | Initial implementation plan |
| 2.0 | 2026-02-16 | AI Assistant | Fixed all gaps: updated paths, added SPEC-07/08/09/10, Phase 0, Project V2 sync, 4-Gate system, Sprint 0 automation, RACI generator, layer selector, sample fixtures, expanded TASKS breakdown |
