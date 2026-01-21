---
title: "TASKS-TEMPLATE: Implementation Task Document"
tags:
  - tasks-template
  - layer-10-artifact
  - shared-architecture
  - document-template
custom_fields:
  document_type: template
  artifact_type: TASKS
  layer: 10
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  template_for: implementation-task-document
  schema_reference: "TASKS_MVP_SCHEMA.yaml"
  schema_version: "2.0"
---
> **🔄 Dual-Format Note**: 
> 
> This MD template is the **primary source** for human workflow. 
> - **For Autopilot**: See `TASKS-MVP-TEMPLATE.yaml` (YAML template) 
> - **Shared Validation**: Both formats are validated by `TASKS_MVP_SCHEMA.yaml` 
> - **Complete Explanation**: See [DUAL_MVP_TEMPLATES_ARCHITECTURE.md](../DUAL_MVP_TEMPLATES_ARCHITECTURE.md) for full comparison of formats, authority hierarchy, and when to use each. 
> 
---

> **Document Authority**: This is the **PRIMARY STANDARD** for TASKS structure.
> - **Schema**: `TASKS_MVP_SCHEMA.yaml v2.0` - Validation rules
> - **Creation Rules**: `TASKS_MVP_CREATION_RULES.md` - Usage guidance
> - **Validation Rules**: `TASKS_MVP_VALIDATION_RULES.md` - Post-creation checks


# TASKS-NN: [Descriptive Component/Feature Name]

**Layer**: 10 (Code Generation) - Unified implementation plan combining WHAT to build and HOW to execute.

**Workflow**: `SPEC (Layer 9) → TASKS (Layer 10) → Code (Layer 11) → Tests (Layer 12) → Validation (Layer 13)`

---

<h2>Document Control</h2>

| Field | Value |
|-------|-------|
| **TASKS ID** | TASKS-NN |
| **Status** | Draft / Ready / In Progress / Completed / Blocked |
| **Version** | 1.0.0 |
| **Created** | YYYY-MM-DD |
| **Updated** | YYYY-MM-DD |
| **Author** | [Developer/AI Assistant] |
| **Assigned To** | [Primary developer] |
| **Priority** | P0 (Critical) / P1 (High) / P2 (Normal) |
| **Estimated Effort** | [X hours] |
| **Actual Effort** | [Update on completion] |
| **Complexity** | [1-5 scale] |

---

<h2>Development Plan Tracking</h2>

```yaml
# Machine-parsable tracking for IMPLEMENTATION_PLAN.md integration
tasks_tracking:
  id: TASKS-NN
  service_name: "[Service/Component Name]"
  priority: P0
  dependents: "[Components that depend on this]"
  
  workflow:
    pre_check:
      status: NOT_STARTED  # NOT_STARTED → COMPLETED
      checklist:
        - verified_req: false       # Verified against REQ-NN
        - verified_spec: false      # Verified against SPEC-NN
        - confirmed_arch: false     # Confirmed architecture pattern
        - checked_deps: false       # All dependencies available
    
    implementation:
      status: NOT_STARTED  # NOT_STARTED → IN_PROGRESS → COMPLETED
      started: null        # YYYY-MM-DD
      completed: null      # YYYY-MM-DD
    
    post_check:
      status: NOT_STARTED
      checklist:
        - tests_passing: false      # All tests pass
        - coverage_met: false       # Coverage thresholds met
        - docs_updated: false       # Documentation updated
        - session_logged: false     # Session log entry added
```

---

<h2>TASKS.NN.18.01: Objective</h2>

[2-3 sentences: What this task accomplishes and its role in the system]

**Deliverables**:
- [ ] [Deliverable 1: e.g., "Core module with business logic"]
- [ ] [Deliverable 2: e.g., "Unit tests with 85%+ coverage"]
- [ ] [Deliverable 3: e.g., "Integration with external service"]
- [ ] [Deliverable 4: e.g., "API documentation"]

**Business Value**: [Single sentence on why this matters]

---

<h2>TASKS.NN.18.02: Scope</h2>

<h3>2.1 Included</h3>

- [Feature/functionality #1]
- [Feature/functionality #2]
- [Integration point #1]

<h3>2.2 Excluded</h3>

- [Out of scope item #1 - future task]
- [Out of scope item #2 - different component]

<h3>2.3 Prerequisites</h3>

- [ ] [Infrastructure requirement]
- [ ] [Dependency requirement]
- [ ] [Access/permission requirement]

---

<h2>TASKS.NN.18.03: Implementation Plan</h2>

<h3>Phase 1: Setup & Foundation</h3>

| Step | Action | Success Criteria | Duration |
|------|--------|------------------|----------|
| 1.1 | Review SPEC-NN and REQ-NN | Requirements understood | [X min] |
| 1.2 | Create module structure | Files created, imports work | [X min] |
| 1.3 | Define interfaces/types | Type hints complete, mypy passes | [X min] |

<h3>Phase 2: Core Implementation</h3>

| Step | Action | Success Criteria | Duration |
|------|--------|------------------|----------|
| 2.1 | Implement business logic | Core functions work | [X min] |
| 2.2 | Add error handling | All error paths covered | [X min] |
| 2.3 | Implement integrations | External calls functional | [X min] |

<h3>Phase 3: Testing & Validation</h3>

| Step | Action | Success Criteria | Duration |
|------|--------|------------------|----------|
| 3.1 | Write unit tests | 85%+ coverage | [X min] |
| 3.2 | Write integration tests | All integrations verified | [X min] |
| 3.3 | Run BDD scenarios | All scenarios pass | [X min] |

<h3>Phase 4: Completion</h3>

| Step | Action | Success Criteria | Duration |
|------|--------|------------------|----------|
| 4.1 | Update documentation | Docstrings complete | [X min] |
| 4.2 | Code review | Review approved | [X min] |
| 4.3 | Update tracking | YAML status updated | [X min] |
| 4.4 | Hand-off | Tests passed & Log updated | [X min] |

---

<h2>TASKS.NN.18.04: Execution Commands</h2>

<h3>4.1 Environment Setup</h3>

```bash
# Verify environment
python --version  # Requires 3.12+
poetry --version  # Or uv

# Install dependencies
poetry install
# or: uv sync

# Verify installation
poetry run python -c "import [package]; print('OK')"
```

<h3>4.2 Implementation Commands</h3>

```bash
# Create module structure
mkdir -p src/[module]/{domain,adapters,ports}
touch src/[module]/__init__.py
touch src/[module]/domain/{models,services}.py
touch src/[module]/ports/{interfaces}.py
touch src/[module]/adapters/{repository,api_client}.py

# Run type checking during development
poetry run mypy src/[module] --strict

# Run tests continuously
poetry run pytest tests/unit/[module] -v --tb=short
```

<h3>4.3 Validation Commands</h3>

```bash
# Full test suite
poetry run pytest tests/ -v --cov=src/[module] --cov-report=term-missing

# BDD scenarios
poetry run pytest tests/bdd/ -v --gherkin-terminal-reporter

# Lint and format
poetry run black src/[module] tests/[module]
poetry run flake8 src/[module]
poetry run mypy src/[module] --strict

# Security scan
poetry run bandit -r src/[module]
```

<h3>4.4 Verification Checklist</h3>

```bash
# Run all verification steps
poetry run pytest tests/ -v                    # All tests pass
poetry run mypy src/[module] --strict          # No type errors
poetry run flake8 src/[module]                 # No lint errors
poetry run pytest --cov=src/[module] --cov-fail-under=85  # Coverage met
```

---

<h2>TASKS.NN.18.05: Constraints</h2>

<h3>5.1 Technical Constraints</h3>

| Category | Constraint |
|----------|------------|
| **Language** | Python 3.12+ with type hints |
| **Framework** | FastAPI / [specified framework] |
| **Database** | PostgreSQL / Redis |
| **Patterns** | Hexagonal architecture, Repository pattern |

<h3>5.2 Quality Constraints</h3>

| Metric | Target |
|--------|--------|
| **Unit Test Coverage** | ≥ 85% |
| **Type Coverage** | 100% (mypy strict) |
| **Lint Score** | 0 errors (Flake8) |
| **Complexity** | < 10 cyclomatic per function |

<h3>5.3 Performance Constraints</h3>

| Metric | Target |
|--------|--------|
| **Response Time** | p95 < [XXX]ms |
| **Throughput** | ≥ [XXX] req/s |
| **Memory** | < [XXX] MB |

---

<h2>TASKS.NN.18.06: Acceptance Criteria</h2>

<h3>6.1 Functional</h3>

- [ ] Implements all requirements from REQ-NN
- [ ] Business logic matches SPEC-NN specification
- [ ] All integration points functional
- [ ] Error handling covers all edge cases

<h3>6.2 Quality</h3>

- [ ] Unit test coverage ≥ 85%
- [ ] All BDD scenarios pass
- [ ] mypy --strict passes with no errors
- [ ] No high/critical security vulnerabilities

<h3>6.3 Operational</h3>

- [ ] Documentation complete (docstrings, README)
- [ ] Logging implemented with correlation IDs
- [ ] Health check endpoint functional
- [ ] Configuration externalized

---

---

<h2>TASKS.NN.18.07: Implementation Contracts</h2>

> **Mandatory Interface Compliance**: The implementation MUST adhere to these contracts.

<h3>7.1 Contracts Provided (if provider)</h3>

| Contract Name | Type | Consumers | File |
|---------------|------|-----------|------|
| [InterfaceName] | Protocol | TASKS-XX, TASKS-YY | `src/contracts/[name].py` |

<h3>7.2 Contracts Consumed (if consumer)</h3>

| Source | Contract Name | Type | Usage |
|--------|---------------|------|-------|
| TASKS-NN | [ContractName] | Protocol | [How it's used] |

---

<h2>TASKS.NN.18.08: Traceability</h2>

<h3>8.1 Upstream References</h3>

| Type | ID | Title | Relevant Sections |
|------|-----|-------|-------------------|
| SPEC | SPEC-NN | [Specification title] | Sections X, Y |
| REQ | REQ-NN | [Requirement title] | All criteria |
| ADR | ADR-NN | [Decision title] | Decision, Rationale |
| BDD | BDD-NN | [Feature file] | Scenarios 1-N |

<h3>8.2 Traceability Tags</h3>

```markdown
@spec: SPEC-NN
@req: REQ-NN.XX.YY
@adr: ADR-NN
@bdd: BDD-NN.SS
@prd: PRD-NN.XX.YY
@sys: SYS-NN.XX.YY
@related-tasks: TASKS-NN
@depends-tasks: TASKS-NN
```

<h3>8.3 Code Locations</h3>

| Component | Path | Purpose |
|-----------|------|---------|
| Core Module | `src/[module]/domain/` | Business logic |
| Interfaces | `src/[module]/ports/` | Port definitions |
| Adapters | `src/[module]/adapters/` | External integrations |
| Tests | `tests/unit/[module]/` | Unit tests |
| BDD Tests | `tests/bdd/[module]/` | Acceptance tests |

---

---

<h2>TASKS.NN.18.09: Risk & Mitigation</h2>

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| External API unavailable | Medium | High | Circuit breaker, cached fallback |
| Performance target missed | Low | High | Early profiling, caching strategy |
| Complex business logic | Medium | Medium | Property-based testing, domain expert review |

---

---

<h2>TASKS.NN.18.10: Session Log</h2>

| Date | Status | Summary |
|------|--------|---------|
| YYYY-MM-DD | IN_PROGRESS | Started implementation, completed Phase 1 |
| YYYY-MM-DD | COMPLETED | **Implementation Complete**<br><ul><li>**Summary**: [Summary of deliverables]</li><li>**Tests**: [N]/[N] Passed ([X]%), [X]% Coverage.</li><li>**Artifacts**: `src/...`, `tests/...`</li></ul> |

---

---

<h2>TASKS.NN.18.11: Change History</h2>

| Date | Version | Change | Author |
|------|---------|--------|--------|
| YYYY-MM-DD | 1.0 | Initial document | [Author] |

---

<h2>References</h2>

- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Workflow guide
- Implementation contracts guide - reference only (link intentionally omitted)
- [IMPLEMENTATION_PLAN_README.md](./IMPLEMENTATION_PLAN_README.md) - Tracking workflow

---

**Template Version**: 2.0
**File Size Target**: <15,000 tokens
**Last Updated**: 2026-01-15
