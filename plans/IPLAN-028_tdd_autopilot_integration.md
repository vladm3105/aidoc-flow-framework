---
title: "TDD Autopilot Integration Implementation Plan"
tags:
  - implementation-plan
  - tdd-integration
  - autopilot
  - automation
custom_fields:
  document_type: iplan
  artifact_type: IPLAN
  layer: 12
  priority: high
  development_status: in_progress
  version: "1.0"
  session_id: "tdd-autopilot-001"
  last_updated: "2026-01-21"
---

# IPLAN-001: TDD Autopilot Integration Implementation Plan

**Purpose**: Plan and track implementation of Test-Driven Development (TDD) integration with Autopilot automated workflow.

**Version**: 1.0
**Session ID**: tdd-autopilot-001
**Last Updated**: 2026-01-21

---

## Document Control

| Item | Details |
|------|---------|
| **Plan ID** | IPLAN-001 |
| **Project** | AI Dev Flow Framework |
| **Start Date** | 2026-01-21 |
| **Target Completion** | 2026-02-18 (4 weeks) |
| **Actual Completion** | 2026-02-06 |
| **Status** | ✅ Complete |
| **Owner** | AI Dev Flow Working Group |

---

## Session Log

| Session | Date | Activities | Notes |
|---------|-------|------------|--------|
| 1 | 2026-01-21 | Created framework guide and IPLAN | Initial planning complete |
| 2 | 2026-02-06 | Phase 2 & 3 Implementation | All scripts created and documented |
| 3 | 2026-02-06 | E2E Validation & Completion | validate_tdd_e2e.py created, IPLAN complete |
| 4 | 2026-02-06 | Test Suite Implementation | Full test suite: smoke, unit, regression, BDD |

---

## 1. Executive Summary

### Objective

Integrate Test-Driven Development (TDD) methodology into Autopilot workflow to:
1. Generate unit tests BEFORE specifications
2. Use tests to guide SPEC contract design
3. Reduce code refactoring cycles
4. Improve code quality and testability

### Approach

Three-phase implementation:
- **Phase 1**: Manual TDD validation (Week 1-2)
- **Phase 2**: TDD awareness (Week 3-4)
- **Phase 3**: Native TDD support (Week 5-6)

### Success Criteria

- Unit tests generated before SPEC creation
- SPEC contracts designed to satisfy test expectations
- Code generation pass rate ≥90% on first attempt
- Unit test coverage ≥90%
- Reduced refactoring cycles (≤1 per component)

---

## 2. Scope

### In Scope

**Framework Modifications**:
1. TDD unit test generation stage in Autopilot
2. SPEC generation enhancement (test-aware)
3. TASKS template updates
4. Traceability automation (two-phase tagging)
5. Quality gate modifications (TDD-aware)

**Documentation**:
1. Autopilot TDD Integration Guide
2. Testing Strategy with TDD
3. Implementation templates and examples

**Automation Scripts**:
1. Test requirement analyzer
2. Traceability tag updater
3. Quality gate validation (TDD mode)

**Test Suite** (Added v1.3):
1. Smoke tests - Quick script validation
2. Unit tests - Function-level testing
3. Regression tests - Baseline comparisons
4. BDD acceptance tests - Gherkin scenarios
5. Shared fixtures and pytest configuration

### Out of Scope

- Major Autopilot refactoring (keep incremental)
- Changes to test frameworks (pytest, pytest-bdd)
- Backend framework changes (FastAPI, etc.)
- Legacy project migration

---

## 3. Prerequisites

### System Requirements
- Python 3.9+
- Autopilot v2.0 or higher
- test-automation skill available
- Git repository with SDD structure

### Knowledge Requirements
- Understanding of SDD framework layers
- Familiarity with TDD methodology
- Autopilot workflow knowledge

### Dependencies
- Framework guide: [AUTOPILOT_TDD_INTEGRATION_GUIDE.md](../AUTOPILOT_TDD_INTEGRATION_GUIDE.md)
- Testing strategy: [TESTING_STRATEGY_TDD.md](../TESTING_STRATEGY_TDD.md)
- Autopilot workflow: [AUTOPILOT/AUTOPILOT_WORKFLOW_GUIDE.md](../ai_dev_flow/AUTOPILOT/AUTOPILOT_WORKFLOW_GUIDE.md)

---

## 4. Implementation Phases

### Phase 1: Manual TDD Validation (Week 1-2)

**Goal**: Validate TDD approach with existing projects manually.

#### 4.1.1 Create Test Generation Documentation

**Tasks**:
- Document manual test generation workflow
- Create test templates from REQ documents
- Validate test generation works with test-automation skill
- Document traceability patterns (PENDING tags)

**Commands**:
```bash
# Generate unit tests from REQ
test-automation generate-unit \
  --input ai_dev_flow/07_REQ/ \
  --output tests/unit/ \
  --framework pytest

# Verify tests fail initially
pytest tests/unit/ --continue-on-collection-errors
```

**Acceptance**:
- Manual test generation documented
- Test templates created
- PENDING traceability tags documented

#### 4.1.2 Test-Aware SPEC Creation

**Tasks**:
- Create SPEC manually after reviewing unit tests
- Document SPEC design process
- Validate SPEC satisfies test requirements
- Update framework guide with best practices

**Acceptance**:
- SPEC designed around test expectations
- Test requirements satisfied
- Process documented

#### 4.1.3 Validate Complete TDD Cycle

**Tasks**:
- Generate code from test-aware SPEC
- Run unit tests and validate pass rate
- Measure time and quality improvements
- Document lessons learned

**Acceptance**:
- Unit tests pass ≥90% on first generation
- Cycle time documented
- Lessons learned captured

#### 4.1.4 Update Framework Guides

**Tasks**:
- Update AUTOPILOT_TDD_INTEGRATION_GUIDE.md with findings
- Refine TESTING_STRATEGY_TDD.md
- Add examples to framework documentation
- Create migration path documentation

**Acceptance**:
- Framework guides updated
- Examples added
- Migration path documented

---

### Phase 2: TDD Awareness (Week 3-4)

**Goal**: Autopilot reads existing unit tests during SPEC generation.

#### 4.2.1 Test Requirement Analyzer

**Tasks**:
- Create `scripts/analyze_test_requirements.py`
- Parse unit test files
- Extract required classes, methods, signatures
- Generate test requirement JSON

**Script Structure**:
```python
#!/usr/bin/env python3
"""
Analyze unit test files to extract requirements for SPEC generation
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Any

def analyze_test_file(test_file: Path) -> Dict[str, Any]:
    """Analyze a single unit test file"""
    with open(test_file) as f:
        content = f.read()

    tree = ast.parse(content)

    requirements = {
        'test_file': str(test_file),
        'req_id': extract_req_id(content),
        'required_classes': [],
        'required_methods': []
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Extract method calls (e.g., validate_email())
            method_name = extract_method_name(node)
            if method_name:
                requirements['required_methods'].append({
                    'name': method_name,
                    'signature': infer_signature(node)
                })

    return requirements

def extract_req_id(content: str) -> str:
    """Extract REQ ID from traceability tags"""
    import re
    match = re.search(r'@req:\s*(REQ-\d+)', content)
    return match.group(1) if match else 'UNKNOWN'

def generate_test_requirements(test_dir: Path, output: Path):
    """Generate test requirements JSON from all test files"""
    all_requirements = {}

    for test_file in test_dir.glob('test_req_*.py'):
        req_id = analyze_test_file(test_file)['req_id']
        all_requirements[req_id] = analyze_test_file(test_file)

    with open(output, 'w') as f:
        json.dump(all_requirements, f, indent=2)

if __name__ == '__main__':
    generate_test_requirements(
        Path('tests/unit'),
        Path('tmp/test_requirements.json')
    )
```

**Acceptance**:
- Script created and tested
- Generates valid test requirement JSON
- Extracts classes, methods, signatures correctly

#### 4.2.2 SPEC Generation Enhancement

**Tasks**:
- Modify Autopilot SPEC generation script
- Read test requirements JSON before generation
- Design SPEC contracts to satisfy test requirements
- Validate SPEC against test expectations

**Modified Workflow**:
```python
# AUTOPILOT/scripts/generate_spec_tdd.py

def generate_spec_tdd(req_files, test_requirements):
    """
    Generate SPEC with TDD awareness
    """
    for req_file in req_files:
        req_id = extract_req_id(req_file)

        # Read existing test requirements
        test_req = test_requirements.get(req_id, {})

        # Generate SPEC with test awareness
        spec = {
            'spec_id': convert_to_spec_id(req_id),
            'title': derive_title(req_file),
            'test_requirements': test_req,
            'classes': design_classes_from_tests(test_req),
            'methods': design_methods_from_tests(test_req)
        }

        # Validate SPEC matches test requirements
        validate_spec_against_tests(spec, test_req)

        # Write SPEC YAML
        write_spec_yaml(spec)
```

**Acceptance**:
- SPEC generation reads test requirements
- SPEC contracts match test expectations
- Validation script works

#### 4.2.3 Configuration Updates

**Tasks**:
- Add `test_awareness` flag to Autopilot config
- Document TDD mode configuration
- Create config templates

**Config Template**:
```yaml
# AUTOPILOT/config_tdd.yml
autopilot:
  mode: tdd  # or 'standard'
  test_awareness: true
  test_directory: tests/unit/
  test_requirements_output: tmp/test_requirements.json

spec_generation:
  test_driven: true
  validate_against_tests: true

quality_gates:
  tdd_mode:
    skip_validation_on_initial_tests: true
    require_pass_after_code: true
```

**Acceptance**:
- Config template created
- Autopilot supports TDD mode
- Documentation updated

#### 4.2.4 TASKS Template Update

**Tasks**:
- Modify TASKS-MVP-TEMPLATE.md
- Add reference to existing unit tests
- Include test execution commands
- Add traceability update commands

**TASKS Template Section**:
```markdown
## TDD Integration

### Pre-existing Tests
This implementation has existing unit tests that define behavior:
- **Test File**: tests/unit/test_req_{NN}_{slug}.py
- **Test Coverage**: Validates {functionality description}

### Test Execution Commands
```bash
# Run unit tests after implementation
pytest tests/unit/test_req_{NN}_{slug}.py -v

# Verify coverage
pytest tests/unit/test_req_{NN}_{slug}.py \
  --cov=src/services/{service}.py \
  --cov-report=term-missing
```

### Traceability Update
After code generation, update PENDING tags:
```bash
python scripts/update_test_traceability.py \
  --test-file tests/unit/test_req_{NN}_{slug}.py \
  --spec-file 09_SPEC/SPEC-{NN}_{slug}.yaml \
  --code-file src/services/{service}.py
```
```

**Acceptance**:
- TASKS template updated
- TDD section added
- Execution commands documented

#### 4.2.5 Validation and Testing

**Tasks**:
- Test TDD-aware SPEC generation on sample projects
- Validate SPEC quality improves
- Measure reduction in refactoring cycles
- Document test results

**Acceptance**:
- TDD-aware SPEC generation validated
- Quality improvements measured
- Test results documented

---

### Phase 3: Native TDD Support (Week 5-6)

**Goal**: Full automation of TDD cycle in Autopilot.

#### 4.3.1 TDD Unit Test Generation Stage

**Tasks**:
- Add TDD unit test generation stage to Autopilot
- Implement `skip_quality_gate` logic
- Support PENDING traceability tags
- Integrate with existing workflow

**Autopilot Stage Configuration**:
```yaml
# AUTOPILOT/tdd_workflow.yml
stages:
  - name: tdd_unit_tests
    layer: POST-REQ
    action: generate_unit_tests
    source: ai_dev_flow/07_REQ/
    output: tests/unit/
    framework: pytest
    mode: tdd
    expected_status: fail
    skip_quality_gate: true
    traceability_mode: pending
```

**Quality Gate Logic**:
```python
# AUTOPILOT/scripts/validate_tdd_stage.py

def validate_tdd_unit_tests(stage_result):
    """
    Validate TDD unit test stage
    """
    if stage_result.mode == 'tdd':
        if not stage_result.code_exists:
            # Tests expected to fail before code
            return ValidationResult(
                status='SKIP',
                message='TDD: Tests fail before code (expected)'
            )
        else:
            # Code exists - tests must pass
            if stage_result.tests_pass:
                return ValidationResult(status='PASS')
            else:
                return ValidationResult(
                    status='FAIL',
                    message='Code exists but tests fail'
                )
    else:
        return standard_validation(stage_result)
```

**Acceptance**:
- TDD stage added to Autopilot
- Quality gate logic implemented
- PENDING traceability supported

#### 4.3.2 Traceability Tag Automation

**Tasks**:
- Create `scripts/update_test_traceability.py`
- Implement two-phase tagging (PENDING → filled)
- Update tags after code generation
- Validate all PENDING tags resolved

**Script Implementation**:
```python
#!/usr/bin/env python3
"""
Update PENDING traceability tags in test files
"""

import os
import re
from pathlib import Path

def update_test_traceability(test_dir, spec_dir, tasks_dir, code_dir):
    """
    Update PENDING traceability tags with actual file paths
    """
    for test_file in Path(test_dir).glob('*.py'):
        content = test_file.read_text()

        # Check if PENDING tags exist
        if '@spec: PENDING' not in content:
            continue

        # Extract REQ ID
        req_match = re.search(r'@req:\s*(REQ-\d+)', content)
        if not req_match:
            continue

        req_id = req_match.group(1)

        # Find corresponding files
        spec_file = find_file_by_id(spec_dir, req_id, 'SPEC')
        tasks_file = find_file_by_id(tasks_dir, req_id, 'TASKS')
        code_file = find_code_file(req_id, code_dir)

        # Update PENDING tags
        content = content.replace('@spec: PENDING', f'@spec: {spec_file}')
        content = content.replace('@tasks: PENDING', f'@tasks: {tasks_file}')
        content = content.replace('@code: PENDING', f'@code: {code_file}')

        # Write updated content
        test_file.write_text(content)
        print(f"✓ Updated {test_file.name}")

def find_file_by_id(directory, req_id, artifact_type):
    """Find file by ID in directory"""
    # Convert REQ-01 to SPEC-01 or TASKS-01
    artifact_id = req_id.replace('REQ', artifact_type)
    files = list(directory.glob(f'{artifact_id}*.yaml')) + \
             list(directory.glob(f'{artifact_id}*.md'))
    return str(files[0]) if files else 'NOT_FOUND'

def find_code_file(req_id, services_dir):
    """Find code file for REQ ID"""
    # Map REQ-001 to service name
    service_name = req_id_to_service_name(req_id)
    code_files = list(services_dir.rglob(f'{service_name}.py'))
    return str(code_files[0]) if code_files else 'NOT_FOUND'

def req_id_to_service_name(req_id):
    """Convert REQ ID to service name"""
    # Example: REQ-001 -> validation_service
    num = req_id.split('-')[1]
    service_map = load_service_map()
    return service_map.get(num, f'service_{num}')

def validate_no_pending_tags(test_dir):
    """Verify all PENDING tags are resolved"""
    pending_count = 0
    for test_file in Path(test_dir).glob('*.py'):
        content = test_file.read_text()
        if 'PENDING' in content:
            print(f"⚠ PENDING tag found in {test_file.name}")
            pending_count += 1

    if pending_count == 0:
        print("✓ All PENDING tags resolved")
        return True
    else:
        print(f"✗ {pending_count} PENDING tags remain")
        return False

if __name__ == '__main__':
    update_test_traceability(
        test_dir=Path('tests/unit'),
        spec_dir=Path('ai_dev_flow/09_SPEC'),
        tasks_dir=Path('ai_dev_flow/10_TASKS'),
        code_dir=Path('src')
    )

    validate_no_pending_tags(Path('tests/unit'))
```

**Acceptance**:
- Traceability update script created
- Two-phase tagging implemented
- PENDING tag validation works

#### 4.3.3 Code Generation Integration

**Tasks**:
- Modify code generation to run unit tests
- Validate test pass rate (90%+ required)
- Trigger traceability tag updates
- Handle test failures gracefully

**Code Generation Workflow**:
```python
# AUTOPILOT/scripts/generate_code_with_tdd.py

def generate_code_with_tdd(spec, tasks, test_dir):
    """
    Generate code with TDD validation
    """
    # Step 1: Generate code from SPEC/TASKS
    code_files = generate_code(spec, tasks)

    # Step 2: Run unit tests
    test_results = run_unit_tests(test_dir)

    # Step 3: Validate pass rate
    if test_results.pass_rate < 90:
        print(f"⚠ Test pass rate: {test_results.pass_rate}%")
        print("Attempting to fix code...")

        # Step 4: Auto-fix (max 3 attempts)
        for attempt in range(3):
            fix_code(test_results.failures)
            test_results = run_unit_tests(test_dir)
            if test_results.pass_rate >= 90:
                print(f"✓ Fixed in attempt {attempt + 1}")
                break

    # Step 5: Update traceability tags
    update_traceability_tags(test_dir)

    return test_results

def run_unit_tests(test_dir):
    """Run pytest and return results"""
    import subprocess
    result = subprocess.run(
        ['pytest', str(test_dir), '--cov=src', '--cov-report=json'],
        capture_output=True,
        text=True
    )

    # Parse coverage report
    with open('coverage.json') as f:
        coverage_data = json.load(f)

    pass_rate = calculate_pass_rate(coverage_data)

    return TestResults(
        passed=result.returncode == 0,
        pass_rate=pass_rate,
        failures=extract_failures(result.stdout)
    )
```

**Acceptance**:
- Code generation runs unit tests
- 90% pass rate enforced
- Traceability tags updated automatically

#### 4.3.4 Integration Test Automation

**Tasks**:
- Create integration test generation stage
- Generate from CTR/SYS/SPEC after all code
- Run integration tests immediately
- Validate component interactions

**Integration Test Stage**:
```yaml
stages:
  - name: integration_tests
    layer: POST-CODE
    action: generate_and_run_integration_tests
    source: [ai_dev_flow/08_CTR/, ai_dev_flow/06_SYS/, ai_dev_flow/09_SPEC/]
    output: tests/integration/
    framework: pytest
    testcontainers: true
    expected_status: pass
```

**Acceptance**:
- Integration test stage created
- Tests generated from CTR/SYS/SPEC
- Tests run automatically

#### 4.3.5 Smoke Test Automation

**Tasks**:
- Create smoke test generation stage
- Generate from EARS/BDD/REQ
- Run immediately after deployment
- Implement rollback on failure

**Smoke Test Stage**:
```yaml
stages:
  - name: smoke_tests
    layer: POST-DEPLOY
    action: generate_and_run_smoke_tests
    source: [ai_dev_flow/03_EARS/, ai_dev_flow/04_BDD/, ai_dev_flow/07_REQ/]
    output: tests/smoke/
    framework: pytest
    timeout: 300  # 5 minutes
    fail_fast: true
    rollback_on_failure: true
    environment: production
```

**Rollback Logic**:
```python
def run_smoke_tests_with_rollback(smoke_tests, environment):
    """Run smoke tests and rollback on failure"""
    results = run_tests(smoke_tests)

    if not results.all_passed:
        print(f"✗ Smoke tests failed")
        print(f"Rolling back {environment} deployment...")

        rollback_deployment(environment)

        return False
    else:
        print(f"✓ Smoke tests passed")
        return True
```

**Acceptance**:
- Smoke test stage created
- Rollback implemented
- Tests run post-deployment

#### 4.3.6 End-to-End Workflow Validation

**Tasks**:
- Test complete TDD workflow end-to-end
- Validate all stages execute correctly
- Measure pipeline performance
- Document results

**Test Scenarios**:
1. Simple service (1 REQ, 1 SPEC)
2. Medium service (3 REQS, 1 SPEC)
3. Complex service (5 REQS, 2 SPECS)
4. Multiple components with integration

**Acceptance**:
- All scenarios pass
- Pipeline performance measured
- Results documented

---

## 5. Dependencies

### External Dependencies
- test-automation skill
- Autopilot v2.0
- pytest, pytest-cov, pytest-bdd

### Internal Dependencies
- [AUTOPILOT_TDD_INTEGRATION_GUIDE.md](../AUTOPILOT_TDD_INTEGRATION_GUIDE.md)
- [TESTING_STRATEGY_TDD.md](../TESTING_STRATEGY_TDD.md)
- [10_TASKS/TASKS-MVP-TEMPLATE.md](../ai_dev_flow/10_TASKS/TASKS-MVP-TEMPLATE.md)
- [09_SPEC/SPEC-MVP-TEMPLATE.yaml](../ai_dev_flow/09_SPEC/SPEC-MVP-TEMPLATE.yaml)

### Blocked By
- None

### Blocks
- Production deployment (until validated)
- Legacy project migration (until TDD integration stable)

---

## 6. Risks and Mitigations

### Risk 1: TDD Learning Curve

**Probability**: Medium
**Impact**: Medium

**Mitigation**:
- Provide comprehensive documentation
- Start with manual validation (Phase 1)
- Use example projects for training
- Create video tutorials

### Risk 2: Breaking Autopilot Workflow

**Probability**: Low
**Impact**: High

**Mitigation**:
- Incremental implementation (3 phases)
- Maintain backward compatibility
- Extensive testing on sample projects
- Rollback plan ready

### Risk 3: SPEC Quality Degradation

**Probability**: Low
**Impact**: Medium

**Mitigation**:
- Validate SPEC against test requirements
- Implement SPEC quality gates
- Manual review for first few cycles
- Automated SPEC validation

### Risk 4: Traceability Tag Errors

**Probability**: Medium
**Impact**: Low

**Mitigation**:
- Implement PENDING tag validation
- Automated tag update script
- Regular traceability matrix checks
- Manual review after each phase

---

## 7. Resource Requirements

### Human Resources
- 1 Developer (Framework team)
- 1 QA Engineer (Testing validation)
- 1 DevOps Engineer (CI/CD integration)

**Time Commitment**:
- Phase 1: 20 hours
- Phase 2: 40 hours
- Phase 3: 60 hours
- Total: 120 hours (6 weeks)

### Technical Resources
- Development environment with Autopilot
- Test projects for validation
- CI/CD pipeline for integration testing
- Documentation hosting (Docusaurus)

### Budget
- Development time: 120 hours
- Testing infrastructure: $500/month
- Documentation hosting: $100/month
- **Total**: $600/month (2 months) = $1,200

---

## 8. Testing Strategy

### Phase 1 Validation
- Manual TDD on 3 existing projects
- Document test generation process
- Validate SPEC quality improvements

### Phase 2 Validation
- Test-aware SPEC generation on sample projects
- Compare SPEC quality (before/after)
- Measure refactoring cycle reduction

### Phase 3 Validation
- End-to-end workflow testing
- Performance benchmarking
- CI/CD pipeline validation

### Success Criteria

| Metric | Target | Measurement |
|--------|---------|-------------|
| Unit test pass rate (first generation) | ≥90% | pytest results |
| Code coverage | ≥90% | pytest-cov |
| Refactoring cycles per component | ≤1 | Count iterations |
| SPEC testability score | ≥95% | Automated analysis |
| Integration test failures | <5% | Test run frequency |
| Smoke test duration | <5 min | Execution time |
| End-to-end pipeline time | <30 min | CI/CD timing |

---

## 9. Deployment Strategy

### Phase 1 Deployment (Manual)
- Update framework documentation
- Create training materials
- Team training sessions
- Manual validation on projects

### Phase 2 Deployment (Pilot)
- Deploy to test environment
- Enable TDD awareness flag
- Test on 3 pilot projects
- Gather feedback

### Phase 3 Deployment (Production)
- Full TDD integration enabled
- Update all Autopilot instances
- Monitor metrics and performance
- Rollback plan ready

---

## 10. Acceptance Criteria

### Phase 1 Acceptance
- Manual TDD workflow documented
- Test generation templates created
- SPEC design process validated
- Framework guides updated

### Phase 2 Acceptance
- Test requirement analyzer script created
- SPEC generation reads test requirements
- Config template supports TDD mode
- TASKS template includes TDD section
- Validation results documented

### Phase 3 Acceptance
- TDD stage integrated into Autopilot
- Traceability automation works end-to-end
- Code generation runs unit tests automatically
- Integration and smoke test stages operational
- End-to-end workflow validated
- All quality gates pass

---

## 11. Maintenance and Operations

### Ongoing Tasks
- Monitor TDD pipeline performance
- Update documentation as needed
- Refine test generation heuristics
- Address framework feedback

### Support Plan
- Documentation repository
- Issue tracking (GitHub)
- Regular review meetings
- Continuous improvement backlog

---

## 12. Appendix

### A. Test Project Setup

```bash
# Create test project
mkdir -p tdd_test_project
cd tdd_test_project

# Initialize SDD structure
python AUTOPILOT/scripts/init_project.py --name tdd_test_project

# Generate artifacts (standard mode)
python AUTOPILOT/scripts/mvp_autopilot.py \
  --intent "Simple validation service" \
  --slug validation_service \
  --up-to REQ

# Generate unit tests (TDD)
test-automation generate-unit \
  --input ai_dev_flow/07_REQ/ \
  --output tests/unit/ \
  --framework pytest

# Generate SPEC (test-aware)
python AUTOPILOT/scripts/generate_spec_tdd.py \
  --input ai_dev_flow/07_REQ/ \
  --test-requirements tmp/test_requirements.json \
  --output ai_dev_flow/09_SPEC/
```

### B. Commands Reference

```bash
# Analyze test requirements
python scripts/analyze_test_requirements.py \
  --test-dir tests/unit/ \
  --output tmp/test_requirements.json

# Generate TDD unit tests
test-automation generate-unit \
  --input ai_dev_flow/07_REQ/ \
  --output tests/unit/ \
  --framework pytest \
  --tdd-mode

# Generate test-aware SPEC
python AUTOPILOT/scripts/generate_spec_tdd.py \
  --test-requirements tmp/test_requirements.json

# Update traceability tags
python scripts/update_test_traceability.py \
  --test-dir tests/unit/ \
  --spec-dir ai_dev_flow/09_SPEC/ \
  --tasks-dir ai_dev_flow/10_TASKS/ \
  --code-dir src/

# Validate no PENDING tags
python scripts/validate_traceability.py --test-dir tests/unit/
```

### C. Contact Information

| Role | Name | Email |
|-------|-------|-------|
| Framework Lead | AI Dev Flow Working Group | framework@aidevflow.dev |
| Autopilot Lead | Autopilot Team | autopilot@aidevflow.dev |
| QA Lead | QA Team | qa@aidevflow.dev |

---

**Document Control**

| Item | Details |
|------|---------|
| **IPLAN Version** | 1.3 |
| **Session ID** | tdd-autopilot-001 |
| **Start Date** | 2026-01-21 |
| **Actual Completion** | 2026-02-06 |
| **Current Phase** | All Phases + Test Suite Complete |
| **Status** | ✅ Complete |
| **Next Milestone** | Production Deployment Ready |

**Change History**:

| Version | Date | Changes | Author |
|---------|-------|---------|---------|
| 1.0 | 2026-01-21 | Initial implementation plan for TDD Autopilot integration | Framework Team |
| 1.1 | 2026-02-06 | Phase 2 & 3 Implementation Complete: analyze_test_requirements.py, generate_spec_tdd.py, update_test_traceability.py, validate_tdd_stage.py, --tdd-mode flag | Framework Team |
| 1.2 | 2026-02-06 | Phase 3 Complete: generate_integration_tests.py, generate_smoke_tests.py, validate_tdd_e2e.py, MVP_AUTOPILOT.md updated, TASKS template verified | Framework Team |
| 1.3 | 2026-02-06 | Test Suite Complete: smoke tests, unit tests, regression tests, BDD acceptance tests, pytest configuration, shared fixtures | Framework Team |

---

**Implementation Contracts**

### 7.1 Provided Contracts

**Test Requirement Analyzer Interface**:
```python
from typing import Protocol

class TestRequirementAnalyzer(Protocol):
    def analyze_test_file(self, test_file: Path) -> Dict[str, Any]:
        """Analyze unit test file and extract requirements"""

    def generate_test_requirements(self, test_dir: Path, output: Path) -> None:
        """Generate test requirements JSON from all test files"""
```

**Traceability Updater Interface**:
```python
from typing import Protocol

class TraceabilityUpdater(Protocol):
    def update_test_traceability(
        self,
        test_dir: Path,
        spec_dir: Path,
        tasks_dir: Path,
        code_dir: Path
    ) -> None:
        """Update PENDING traceability tags with actual file paths"""

    def validate_no_pending_tags(self, test_dir: Path) -> bool:
        """Verify all PENDING tags are resolved"""
```

**Quality Gate Validator Interface**:
```python
from typing import Protocol

class QualityGateValidator(Protocol):
    def validate_tdd_unit_tests(self, stage_result: Any) -> ValidationResult:
        """Validate TDD unit test stage with skip logic"""

    def validate_standard_tests(self, stage_result: Any) -> ValidationResult:
        """Validate standard test stage without skip logic"""
```

### 7.2 Consumed Contracts

**Test-Automation Skill Contract**:
- `generate_unit_tests()`: Generate unit tests from REQ documents
- `generate_integration_tests()`: Generate integration tests from CTR/SYS/SPEC
- `generate_smoke_tests()`: Generate smoke tests from EARS/BDD/REQ
- `generate_bdd()`: Generate acceptance tests from BDD documents

**Autopilot Workflow Contract**:
- `generate_spec()`: Generate SPEC from REQ with test awareness
- `generate_tasks()`: Generate TASKS with test references
- `generate_code()`: Generate code from SPEC/TASKS with test validation
- `validate_stage()`: Validate artifact quality with TDD-aware gates

**Framework Registry Contract**:
- `Layer Registry`: TDD stage registered as POST-REQ layer
- `Template Registry`: TDD templates registered and accessible
- `Validation Registry`: TDD quality gates registered
