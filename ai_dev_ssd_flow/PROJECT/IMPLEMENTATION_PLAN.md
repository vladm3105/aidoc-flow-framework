# SDD Implementation Plan for Hybrid Development Model v2.2

**Version**: 1.0
**Created**: 2026-02-16
**Source**: `/opt/data/docs_flow_framework/HYBRID_MODEL_V2.md`
**Target**: `/opt/data/docs_flow_framework/ai_project_ssd_flow/`

---

## 1. Executive Summary

This implementation plan defines the scope, architecture decisions, specifications, and tasks required to implement the automation and tooling described in `HYBRID_MODEL_V2.md`.

The Hybrid Model v2.2 bridges two existing frameworks:
- **AI Dev Flow (SDD)**: 15-layer specification-driven development at `ai_dev_ssd_flow/`
- **AI Project Flow**: AI-first project governance at `ai_project_issues_flow/`

---

## 2. BRD-01: Business Requirements Document

### 2.1 Business Context

**Project Name**: Hybrid Development Model v2.2 Automation Tooling
**Target Launch**: Sprint-based delivery over 4 weeks
**PRD-Ready Score Target**: 90/100

### 2.2 Business Objectives

| ID | Objective | Measurable Outcome |
|----|-----------|-------------------|
| BO-01 | Enable TASKS-to-GitHub Issue synchronization | 100% of TASKS elements mapped to GitHub Issues with full traceability tags |
| BO-02 | Detect documentation drift automatically | Weekly drift reports generated with <7 day artifact currency |
| BO-03 | Integrate SDD validation into CI/CD | 95%+ validator pass rate at first attempt |
| BO-04 | Support change management feedback loop | CHG documents created within 2 days for L2, 5 days for L3 changes |

### 2.3 Functional Requirements

| ID | Requirement | Priority | Complexity |
|----|-------------|----------|------------|
| FR-01 | `tasks_to_github.py` converts TASKS YAML to GitHub Issues with traceability | P0 | 3 |
| FR-02 | `drift_check.py` compares artifact modification dates vs issue close dates | P1 | 3 |
| FR-03 | `validate_artifact.py` wrapper invokes per-type validators | P1 | 2 |
| FR-04 | GitHub Issue template for SDD tasks with @brd/@prd/@spec/@tasks fields | P0 | 2 |
| FR-05 | CI workflow validates changed artifacts on PR and push | P0 | 3 |
| FR-06 | CHG templates for sprint feedback loop | P1 | 2 |
| FR-07 | Sprint 0 checklist template | P2 | 1 |
| FR-08 | RACI matrix template | P2 | 1 |
| FR-09 | Configuration file for automation scripts | P1 | 2 |

### 2.4 Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| QA-01 | Script execution time | <30s for single artifact validation |
| QA-02 | YAML parsing reliability | Handle malformed YAML gracefully |
| QA-03 | GitHub API rate limiting | Respect 5000 req/hour limit |
| QA-04 | CI workflow timeout | <10 minutes for full validation |

### 2.5 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Requirement-to-code traceability | 100% | `trace-check` script |
| Documentation currency | <7 days lag | Drift check report |
| Validator pass rate | >95% first attempt | CI metrics |
| TASKS-to-Issue automation | 100% | Manual audit per sprint |

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

**Decision**: Use YAML configuration at `config/hybrid_model.yaml` with environment variable overrides.

**Rationale**:
- YAML is human-readable and consistent with TASKS format
- Environment variables enable CI/CD flexibility
- Single config file reduces complexity

**Consequences**:
- PyYAML dependency
- Config file must be versioned
- Document all configuration options

---

## 4. SPEC: Technical Specifications

### 4.1 SPEC-01: tasks_to_github.py

**Traceability**: @brd: BRD-01:FR-01

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

**CLI Interface**:
```bash
python scripts/tasks_to_github.py \
  --tasks-file docs/11_TASKS/TASKS-01.yaml \
  --repo owner/repo-name \
  --sprint "Sprint 2.1" \
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
  --github-project 31 \
  --max-age-days 14 \
  --report tmp/drift_report.md
```

### 4.3 SPEC-03: validate_artifact.py

**Traceability**: @brd: BRD-01:FR-03

**Component Architecture**:
```
validate_artifact.py
├── ArtifactTypeDetector (class)
│   ├── detect_type(filepath) -> str
│   └── get_validator_path(type) -> str
├── ValidatorRunner (class)
│   ├── run_validator(path, artifact) -> ValidationResult
│   └── collect_results(results) -> int
└── main(args) -> int
```

**Validation Dispatch Table**:
| Artifact Type | Validator Script |
|---------------|-----------------|
| BRD | `validate_cross_document.py --type BRD` |
| PRD | `validate_cross_document.py --type PRD` |
| SPEC | `validate_cross_document.py --type SPEC` |
| TASKS | `validate_cross_document.py --type TASKS` |
| YAML | `validate_schema_sync.py` |
| Feature | `validate_terminology.py` |

**CLI Interface**:
```bash
python scripts/validate_artifact.py --path docs/BRD/BRD-01.md --strict
```

### 4.4 SPEC-04: GitHub Issue Template

**Traceability**: @brd: BRD-01:FR-04

**File**: `.github/ISSUE_TEMPLATE/sdd-task.yml`

### 4.5 SPEC-05: CI Workflow

**Traceability**: @brd: BRD-01:FR-05

**File**: `.github/workflows/sdd-validation.yml`

**Workflow Jobs**:
1. `validate-artifacts`: Run validators on changed doc files
2. `update-matrix`: Update traceability matrix on main push

### 4.6 SPEC-06: Configuration File

**Traceability**: @brd: BRD-01:FR-09

**File**: `config/hybrid_model.yaml`

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
  excluded_patterns:
    - "docs/generated/*"
    - "docs/archive/*"

# Quality gates
quality_gates:
  sprint_planning: ["doc-spec-validator"]
  pr_created: ["doc-tspec-validator"]
  pr_approved: ["trace-check"]
  phase_exit: ["all"]
```

---

## 5. TASKS Breakdown

### Phase 1: Core Scripts (Week 1)

| Task ID | Title | Dependencies | Size | Priority |
|---------|-------|--------------|------|----------|
| TASKS-01.01.01 | Implement TasksParser class | None | M | P0 |
| TASKS-01.01.02 | Implement GitHubIssueCreator class | TASKS-01.01.01 | L | P0 |
| TASKS-01.01.03 | Implement IssueFormatter class | TASKS-01.01.01 | M | P0 |
| TASKS-01.01.04 | Wire up tasks_to_github.py CLI | TASKS-01.01.01-03 | S | P0 |
| TASKS-01.02.01 | Implement ArtifactScanner class | None | M | P1 |
| TASKS-01.02.02 | Implement GitHubIssueQuery class | None | M | P1 |
| TASKS-01.02.03 | Implement DriftAnalyzer class | TASKS-01.02.01-02 | M | P1 |
| TASKS-01.02.04 | Wire up drift_check.py CLI | TASKS-01.02.01-03 | S | P1 |

### Phase 2: GitHub Integration (Week 2)

| Task ID | Title | Dependencies | Size | Priority |
|---------|-------|--------------|------|----------|
| TASKS-02.01.01 | Create sdd-task.yml issue template | None | S | P0 |
| TASKS-02.01.02 | Create sdd-validation.yml workflow | None | M | P0 |
| TASKS-02.02.01 | Implement validate_artifact.py wrapper | None | M | P1 |
| TASKS-02.02.02 | Create config/hybrid_model.yaml schema | None | S | P1 |
| TASKS-02.02.03 | Add config loading to all scripts | TASKS-02.02.02 | S | P1 |

### Phase 3: Templates and Documentation (Week 3)

| Task ID | Title | Dependencies | Size | Priority |
|---------|-------|--------------|------|----------|
| TASKS-03.01.01 | Copy and adapt CHG-MVP-TEMPLATE.md | None | S | P1 |
| TASKS-03.01.02 | Create Sprint 0 checklist template | None | S | P2 |
| TASKS-03.01.03 | Create RACI matrix template | None | S | P2 |
| TASKS-03.02.01 | Write SETUP_GUIDE.md for hybrid model | TASKS-02.02.02 | M | P1 |
| TASKS-03.02.02 | Write script README.md documentation | TASKS-01.01.04, TASKS-01.02.04 | M | P1 |

### Phase 4: Validation and Testing (Week 4)

| Task ID | Title | Dependencies | Size | Priority |
|---------|-------|--------------|------|----------|
| TASKS-04.01.01 | Unit tests for TasksParser | TASKS-01.01.01 | M | P0 |
| TASKS-04.01.02 | Unit tests for GitHubIssueCreator | TASKS-01.01.02 | M | P0 |
| TASKS-04.01.03 | Integration test for tasks_to_github.py | TASKS-01.01.04 | L | P0 |
| TASKS-04.02.01 | Unit tests for drift_check.py | TASKS-01.02.04 | M | P1 |
| TASKS-04.02.02 | End-to-end workflow validation | All | L | P0 |

---

## 6. Directory Structure

```
ai_project_ssd_flow/
├── config/
│   └── hybrid_model.yaml          # SPEC-06
├── docs/
│   ├── IMPLEMENTATION_PLAN.md     # This document
│   ├── SETUP_GUIDE.md             # TASKS-03.02.01
│   └── templates/
│       ├── CHG-HYBRID-TEMPLATE.md # TASKS-03.01.01
│       ├── SPRINT0_CHECKLIST.md   # TASKS-03.01.02
│       └── RACI_MATRIX.md         # TASKS-03.01.03
├── scripts/
│   ├── tasks_to_github.py         # SPEC-01
│   ├── drift_check.py             # SPEC-02
│   ├── validate_artifact.py       # SPEC-03
│   ├── requirements.txt
│   └── README.md                  # TASKS-03.02.02
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   └── sdd-task.yml           # SPEC-04
│   └── workflows/
│       └── sdd-validation.yml     # SPEC-05
└── tests/
    ├── test_tasks_parser.py       # TASKS-04.01.01
    ├── test_issue_creator.py      # TASKS-04.01.02
    └── test_drift_check.py        # TASKS-04.02.01
```

---

## 7. Dependencies

### 7.1 External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| PyGithub | >=2.0 | GitHub REST API |
| PyYAML | >=6.0 | YAML parsing |
| Click | >=8.0 | CLI interface |
| requests | >=2.28 | HTTP requests |

### 7.2 Internal Dependencies

| Script | Depends On | Location |
|--------|-----------|----------|
| tasks_to_github.py | extract_tags.py | ai_dev_ssd_flow/scripts/ |
| validate_artifact.py | validate_cross_document.py | ai_dev_ssd_flow/scripts/ |
| validate_artifact.py | validate_tags_against_docs.py | ai_dev_ssd_flow/scripts/ |
| drift_check.py | config/hybrid_model.yaml | ai_project_ssd_flow/config/ |

---

## 8. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GitHub API rate limiting | Medium | High | Implement exponential backoff |
| YAML parsing failures | Low | Medium | Graceful error handling |
| Validator compatibility | Low | High | Test wrapper against all validators |
| CI workflow timeouts | Medium | Medium | Parallelize validation jobs |

---

## 9. Acceptance Criteria Summary

### Definition of Done for Phase 1
- [ ] `tasks_to_github.py` converts sample TASKS file to Issues (dry-run)
- [ ] `drift_check.py` generates report for test repo
- [ ] Unit tests pass with 85%+ coverage

### Definition of Done for Phase 2
- [ ] Issue template renders correctly in GitHub
- [ ] CI workflow validates changed artifacts on PR
- [ ] Config file loads without errors

### Definition of Done for Phase 3
- [ ] All templates pass doc-validator
- [ ] Setup guide enables new project onboarding
- [ ] Script documentation complete

### Definition of Done for Phase 4
- [ ] All unit tests pass
- [ ] Integration test creates real Issues (in test repo)
- [ ] End-to-end workflow validated with sample data

---

## 10. Traceability Matrix

| BRD Req | SPEC | TASKS | Test |
|---------|------|-------|------|
| FR-01 | SPEC-01 | TASKS-01.01.* | TASKS-04.01.01-03 |
| FR-02 | SPEC-02 | TASKS-01.02.* | TASKS-04.02.01 |
| FR-03 | SPEC-03 | TASKS-02.02.01 | - |
| FR-04 | SPEC-04 | TASKS-02.01.01 | - |
| FR-05 | SPEC-05 | TASKS-02.01.02 | TASKS-04.02.02 |
| FR-06 | - | TASKS-03.01.01 | - |
| FR-07 | - | TASKS-03.01.02 | - |
| FR-08 | - | TASKS-03.01.03 | - |
| FR-09 | SPEC-06 | TASKS-02.02.02-03 | - |

---

## 11. Quick Start Commands

```bash
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

# Sprint integration
python scripts/tasks_to_github.py --tasks-file docs/11_TASKS/TASKS-01.yaml --repo owner/repo

# Validation
/doc-validator docs/                    # Validate all artifacts
python scripts/trace-check.py           # Check traceability
python scripts/drift_check.py           # Check documentation drift
```

---

## 12. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-16 | AI Assistant | Initial implementation plan |
