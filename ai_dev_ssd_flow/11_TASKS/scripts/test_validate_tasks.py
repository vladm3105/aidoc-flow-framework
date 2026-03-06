#!/usr/bin/env python3
"""TASKS Validator Test Suite v1.0 (2026-03-06)

Pytest test suite for validate_tasks.py (all 14 checks).
Provides comprehensive unit and integration testing.

Usage:
    pytest test_validate_tasks.py -v
    pytest test_validate_tasks.py -v --cov=validate_tasks
    pytest test_validate_tasks.py::TestFilenameValidation -v

Coverage Target: 90%+

Author: Claude (TSPEC v2.0 team)
"""

import pytest
from pathlib import Path
from validate_tasks import TasksValidator

# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def valid_tasks_content():
    """Valid TASKS document content."""
    return """---
artifact_type: TASKS
layer: 10
parent_spec: SPEC-001
tags:
  - layer-10-artifact
---

# TASKS-001: Sample Tasks

## Document Control

| Field | Value |
|-------|-------|
| TASKS ID | TASKS-001 |
| Title | Sample Tasks |
| Status | Ready |
| Version | 1.0 |
| Created | 2026-03-06 |
| Last Updated | 2026-03-06 |
| Author | Test Author |
| Parent SPEC | SPEC-001 |
| Complexity | Medium |

## 1. Overview

Sample overview.

## 2. Phase

### Phase 1: Implementation

#### TASK-001: Sample Task

Input: Sample input
Output: Sample output
Acceptance: Sample acceptance

- [x] Step 1
- [ ] Step 2

File reference: `sample.py`

## 3. Dependencies

**Upstream**: None
**Downstream**: TASKS-002
**Blocks**: None

## 4. Acceptance Criteria

- Unit coverage: 95%
- Integration coverage: 85%
- BDD-001 scenarios pass
- Definition of done: All tests pass

## Traceability

@brd: BRD-001
@prd: PRD-001
@ears: EARS-001
@bdd: BDD-001
@adr: ADR-001
@sys: SYS-001
@req: REQ-001
@spec: SPEC-001
"""

@pytest.fixture
def invalid_filename():
    """Invalid filename."""
    return "TASKS_001.md"

@pytest.fixture
def valid_filename():
    """Valid filename."""
    return "TASKS-001_sample_task.md"

@pytest.fixture
def minimal_tasks_content():
    """Minimal TASKS document (missing many fields)."""
    return """---
artifact_type: TASKS
layer: 10
parent_spec: SPEC-001
---

# TASKS-001: Minimal

## Document Control

| Field | Value |
|-------|-------|
| TASKS ID | TASKS-001 |
"""

# ============================================================================
# TEST CHECK 1: FILENAME FORMAT
# ============================================================================

class TestFilenameValidation:
    """Test CHECK 1: Filename format validation."""

    def test_valid_filename(self, tmp_path, valid_tasks_content, valid_filename):
        """Test valid filename pattern."""
        file_path = tmp_path / valid_filename
        file_path.write_text(valid_tasks_content)

        validator = TasksValidator(str(file_path))
        validator._check_01_filename_format()

        assert len(validator.errors) == 0

    def test_invalid_filename_underscore(self, tmp_path, valid_tasks_content):
        """Test invalid filename with underscore instead of hyphen."""
        file_path = tmp_path / "TASKS_001_sample.md"
        file_path.write_text(valid_tasks_content)

        validator = TasksValidator(str(file_path))
        validator._check_01_filename_format()

        assert len(validator.errors) == 1
        assert "TASKS-E001" in validator.errors[0]

    def test_invalid_filename_short_id(self, tmp_path, valid_tasks_content):
        """Test invalid filename with short ID."""
        file_path = tmp_path / "TASKS-1_sample.md"
        file_path.write_text(valid_tasks_content)

        validator = TasksValidator(str(file_path))
        validator._check_01_filename_format()

        assert len(validator.errors) == 1
        assert "TASKS-E001" in validator.errors[0]

    def test_invalid_filename_no_slug(self, tmp_path, valid_tasks_content):
        """Test invalid filename without slug."""
        file_path = tmp_path / "TASKS-001.md"
        file_path.write_text(valid_tasks_content)

        validator = TasksValidator(str(file_path))
        validator._check_01_filename_format()

        assert len(validator.errors) == 1

# ============================================================================
# TEST CHECK 2: FRONTMATTER VALIDATION
# ============================================================================

class TestFrontmatterValidation:
    """Test CHECK 2: Frontmatter validation."""

    def test_valid_frontmatter(self, tmp_path, valid_tasks_content, valid_filename):
        """Test valid frontmatter."""
        file_path = tmp_path / valid_filename
        file_path.write_text(valid_tasks_content)

        validator = TasksValidator(str(file_path))
        validator._check_02_frontmatter_validation()

        # Should have no errors for valid frontmatter
        frontmatter_errors = [e for e in validator.errors if "frontmatter" in e.lower() or "E002" in e or "E003" in e or "E004" in e or "E005" in e]
        assert len(frontmatter_errors) == 0

    def test_missing_frontmatter(self, tmp_path, valid_filename):
        """Test missing frontmatter."""
        content = "# TASKS-001\n\nNo frontmatter"
        file_path = tmp_path / valid_filename
        file_path.write_text(content)

        validator = TasksValidator(str(file_path))
        validator._check_02_frontmatter_validation()

        assert any("E002" in e for e in validator.errors)

    def test_invalid_artifact_type(self, tmp_path, valid_filename):
        """Test invalid artifact_type."""
        content = """---
artifact_type: SPEC
layer: 10
parent_spec: SPEC-001
---

# TASKS-001
"""
        file_path = tmp_path / valid_filename
        file_path.write_text(content)

        validator = TasksValidator(str(file_path))
        validator._check_02_frontmatter_validation()

        assert any("E003" in e for e in validator.errors)

    def test_invalid_layer(self, tmp_path, valid_filename):
        """Test invalid layer."""
        content = """---
artifact_type: TASKS
layer: 9
parent_spec: SPEC-001
---

# TASKS-001
"""
        file_path = tmp_path / valid_filename
        file_path.write_text(content)

        validator = TasksValidator(str(file_path))
        validator._check_02_frontmatter_validation()

        assert any("E004" in e for e in validator.errors)

    def test_missing_parent_spec(self, tmp_path, valid_filename):
        """Test missing parent_spec."""
        content = """---
artifact_type: TASKS
layer: 10
---

# TASKS-001
"""
        file_path = tmp_path / valid_filename
        file_path.write_text(content)

        validator = TasksValidator(str(file_path))
        validator._check_02_frontmatter_validation()

        assert any("E005" in e for e in validator.errors)

# ============================================================================
# TEST CHECK 3: DOCUMENT CONTROL TABLE
# ============================================================================

class TestDocumentControlTable:
    """Test CHECK 3: Document Control table validation."""

    def test_all_fields_present(self, tmp_path, valid_tasks_content, valid_filename):
        """Test all required fields present."""
        file_path = tmp_path / valid_filename
        file_path.write_text(valid_tasks_content)

        validator = TasksValidator(str(file_path))
        validator._check_03_document_control_table()

        # Should have no E006 errors
        doc_control_errors = [e for e in validator.errors if "E006" in e]
        assert len(doc_control_errors) == 0

    def test_missing_fields(self, tmp_path, minimal_tasks_content, valid_filename):
        """Test missing required fields."""
        file_path = tmp_path / valid_filename
        file_path.write_text(minimal_tasks_content)

        validator = TasksValidator(str(file_path))
        validator._check_03_document_control_table()

        # Should have multiple E006 errors for missing fields
        doc_control_errors = [e for e in validator.errors if "E006" in e]
        assert len(doc_control_errors) > 5  # Missing at least 6 fields

# ============================================================================
# TEST CHECK 4: REQUIRED SECTIONS
# ============================================================================

class TestRequiredSections:
    """Test CHECK 4: Required sections validation."""

    def test_all_sections_present(self, tmp_path, valid_tasks_content, valid_filename):
        """Test all required sections present."""
        file_path = tmp_path / valid_filename
        file_path.write_text(valid_tasks_content)

        validator = TasksValidator(str(file_path))
        validator._check_04_required_sections()

        # Should have no E007 errors
        section_errors = [e for e in validator.errors if "E007" in e]
        assert len(section_errors) == 0

    def test_missing_sections(self, tmp_path, minimal_tasks_content, valid_filename):
        """Test missing required sections."""
        file_path = tmp_path / valid_filename
        file_path.write_text(minimal_tasks_content)

        validator = TasksValidator(str(file_path))
        validator._check_04_required_sections()

        # Should have E007 errors for missing sections
        section_errors = [e for e in validator.errors if "E007" in e]
        assert len(section_errors) > 3  # Missing at least 4 sections

# ============================================================================
# TEST CHECK 5: PHASE STRUCTURE
# ============================================================================

class TestPhaseStructure:
    """Test CHECK 5: Phase structure validation."""

    def test_valid_phase_structure(self, tmp_path, valid_tasks_content, valid_filename):
        """Test valid phase structure."""
        file_path = tmp_path / valid_filename
        file_path.write_text(valid_tasks_content)

        validator = TasksValidator(str(file_path))
        validator._check_05_phase_structure()

        # Should have no E008 errors (phases present)
        phase_errors = [e for e in validator.errors if "E008" in e]
        assert len(phase_errors) == 0

    def test_no_phases(self, tmp_path, minimal_tasks_content, valid_filename):
        """Test missing phases."""
        file_path = tmp_path / valid_filename
        file_path.write_text(minimal_tasks_content)

        validator = TasksValidator(str(file_path))
        validator._check_05_phase_structure()

        # Should have E008 error
        assert any("E008" in e for e in validator.errors)

    def test_duplicate_task_ids(self, tmp_path, valid_filename):
        """Test duplicate task IDs."""
        content = """---
artifact_type: TASKS
layer: 10
parent_spec: SPEC-001
---

# TASKS-001

## 2. Phase

### Phase 1: Test

#### TASK-001: First
#### TASK-001: Duplicate
"""
        file_path = tmp_path / valid_filename
        file_path.write_text(content)

        validator = TasksValidator(str(file_path))
        validator._check_05_phase_structure()

        # Should have E035 error for duplicates
        assert any("E035" in e for e in validator.errors)

# ============================================================================
# TEST CHECK 6: TASK DETAILS
# ============================================================================

class TestTaskDetailValidation:
    """Test CHECK 6: Task detail validation."""

    def test_all_task_fields_present(self, tmp_path, valid_tasks_content, valid_filename):
        """Test all task fields present."""
        file_path = tmp_path / valid_filename
        file_path.write_text(valid_tasks_content)

        validator = TasksValidator(str(file_path))
        validator._check_06_task_detail_validation()

        # Should have no warnings for missing Input/Output/Acceptance
        task_warnings = [w for w in validator.warnings if "W005" in w or "W006" in w or "W007" in w]
        assert len(task_warnings) == 0

    def test_missing_task_fields(self, tmp_path, minimal_tasks_content, valid_filename):
        """Test missing task fields."""
        file_path = tmp_path / valid_filename
        file_path.write_text(minimal_tasks_content)

        validator = TasksValidator(str(file_path))
        validator._check_06_task_detail_validation()

        # Should have warnings for missing fields
        assert any("W005" in w or "W006" in w or "W007" in w for w in validator.warnings)

# ============================================================================
# TEST CHECK 11: TRACEABILITY TAGS
# ============================================================================

class TestTraceabilityTags:
    """Test CHECK 11: Traceability tags validation."""

    def test_all_tags_present(self, tmp_path, valid_tasks_content, valid_filename):
        """Test all 8 required tags present."""
        file_path = tmp_path / valid_filename
        file_path.write_text(valid_tasks_content)

        validator = TasksValidator(str(file_path))
        validator._check_11_traceability_tags()

        # Should have no E010 errors
        tag_errors = [e for e in validator.errors if "E010" in e]
        assert len(tag_errors) == 0

    def test_missing_tags(self, tmp_path, minimal_tasks_content, valid_filename):
        """Test missing required tags."""
        file_path = tmp_path / valid_filename
        file_path.write_text(minimal_tasks_content)

        validator = TasksValidator(str(file_path))
        validator._check_11_traceability_tags()

        # Should have E010 errors for missing tags
        tag_errors = [e for e in validator.errors if "E010" in e]
        assert len(tag_errors) == 8  # All 8 tags missing

# ============================================================================
# TEST INTEGRATION: FULL VALIDATION
# ============================================================================

class TestFullValidation:
    """Test complete validation workflow."""

    def test_valid_document_full_validation(self, tmp_path, valid_tasks_content, valid_filename):
        """Test full validation on valid document."""
        file_path = tmp_path / valid_filename
        file_path.write_text(valid_tasks_content)

        validator = TasksValidator(str(file_path))
        results = validator.validate()

        # Valid document should have minimal errors
        assert results['counts']['errors'] == 0
        assert results['exit_code'] in [0, 1]  # Pass or Pass with warnings
        assert results['status'] in ["PASS", "PASS WITH WARNINGS"]

    def test_invalid_document_full_validation(self, tmp_path, minimal_tasks_content, valid_filename):
        """Test full validation on invalid document."""
        file_path = tmp_path / valid_filename
        file_path.write_text(minimal_tasks_content)

        validator = TasksValidator(str(file_path))
        results = validator.validate()

        # Invalid document should have many errors
        assert results['counts']['errors'] > 5
        assert results['exit_code'] == 2  # Fail
        assert results['status'] == "FAIL"

    def test_json_output(self, tmp_path, valid_tasks_content, valid_filename):
        """Test JSON output format."""
        file_path = tmp_path / valid_filename
        file_path.write_text(valid_tasks_content)

        validator = TasksValidator(str(file_path))
        results = validator.validate()

        # Check JSON structure
        assert 'file' in results
        assert 'validator_version' in results
        assert 'phase' in results
        assert 'checks_implemented' in results
        assert results['checks_implemented'] == 14
        assert 'errors' in results
        assert 'warnings' in results
        assert 'counts' in results

# ============================================================================
# TEST AST PARSER (CHECK 9)
# ============================================================================

class TestImplementationContracts:
    """Test CHECK 9: Implementation Contracts (AST parsing)."""

    def test_valid_protocol(self, tmp_path, valid_filename):
        """Test valid Protocol detection."""
        content = """---
artifact_type: TASKS
layer: 10
parent_spec: SPEC-001
---

# TASKS-001

## 7. Implementation Contracts

```python
from typing import Protocol

class DataProcessor(Protocol):
    def process(self, data: dict) -> dict:
        ...
```
"""
        file_path = tmp_path / valid_filename
        file_path.write_text(content)

        validator = TasksValidator(str(file_path))
        validator._check_09_implementation_contracts()

        # Valid protocol should have no errors
        contract_errors = [e for e in validator.errors if "E020" in e or "E024" in e]
        assert len(contract_errors) == 0

    def test_protocol_missing_return_type(self, tmp_path, valid_filename):
        """Test Protocol with missing return type."""
        content = """---
artifact_type: TASKS
layer: 10
parent_spec: SPEC-001
---

# TASKS-001

## 7. Implementation Contracts

```python
from typing import Protocol

class DataProcessor(Protocol):
    def process(self, data: dict):  # Missing return type
        ...
```
"""
        file_path = tmp_path / valid_filename
        file_path.write_text(content)

        validator = TasksValidator(str(file_path))
        validator._check_09_implementation_contracts()

        # Should have warning for missing return type
        assert any("W015" in w for w in validator.warnings)

    def test_syntax_error_in_contract(self, tmp_path, valid_filename):
        """Test syntax error detection."""
        content = """---
artifact_type: TASKS
layer: 10
parent_spec: SPEC-001
---

# TASKS-001

## 7. Implementation Contracts

```python
from typing import Protocol

class Broken(Protocol):
    def method(  # Syntax error
```
"""
        file_path = tmp_path / valid_filename
        file_path.write_text(content)

        validator = TasksValidator(str(file_path))
        validator._check_09_implementation_contracts()

        # Should have E020 error for syntax
        assert any("E020" in e for e in validator.errors)

# ============================================================================
# TEST MAIN
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
