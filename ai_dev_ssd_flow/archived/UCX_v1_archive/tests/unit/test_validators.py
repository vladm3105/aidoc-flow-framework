"""Unit tests for validators module."""

import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile

from ucx.models.enums import DocType
from ucx.validators.registry import get_validator
from ucx.validators.base import BaseValidator


class TestValidatorRegistry:
    """Tests for validator registry."""

    def test_get_validator_brd(self):
        """Test getting BRD validator."""
        validator = get_validator(DocType.BRD)
        assert validator is not None
        assert isinstance(validator, BaseValidator)

    def test_get_validator_prd(self):
        """Test getting PRD validator."""
        validator = get_validator(DocType.PRD)
        assert validator is not None

    def test_get_validator_ears(self):
        """Test getting EARS validator."""
        validator = get_validator(DocType.EARS)
        assert validator is not None

    def test_get_validator_bdd(self):
        """Test getting BDD validator."""
        validator = get_validator(DocType.BDD)
        assert validator is not None

    def test_get_validator_adr(self):
        """Test getting ADR validator."""
        validator = get_validator(DocType.ADR)
        assert validator is not None

    def test_get_validator_sys(self):
        """Test getting SYS validator."""
        validator = get_validator(DocType.SYS)
        assert validator is not None

    def test_get_validator_req(self):
        """Test getting REQ validator."""
        validator = get_validator(DocType.REQ)
        assert validator is not None

    def test_get_validator_ctr(self):
        """Test getting CTR validator."""
        validator = get_validator(DocType.CTR)
        assert validator is not None

    def test_get_validator_spec(self):
        """Test getting SPEC validator."""
        validator = get_validator(DocType.SPEC)
        assert validator is not None

    def test_get_validator_tspec(self):
        """Test getting TSPEC validator."""
        validator = get_validator(DocType.TSPEC)
        assert validator is not None


class TestBRDValidator:
    """Tests for BRD validator."""

    def test_validate_valid_brd(self, tmp_path: Path):
        """Test validating a valid BRD document."""
        content = """# BRD-01: Test Document

## Executive Summary
Test summary content.

## BRD.01 Business Goals
### BRD.01.01 Primary Goal
Test goal description.

## BRD.02 Stakeholders
Test stakeholder content.
"""
        doc_path = tmp_path / "BRD-01.md"
        doc_path.write_text(content)

        validator = get_validator(DocType.BRD)
        result = validator.validate(doc_path)

        # Should have minimal errors for basic structure
        assert result is not None
        assert hasattr(result, "errors")

    def test_validate_empty_document(self, tmp_path: Path):
        """Test validating an empty document."""
        doc_path = tmp_path / "BRD-02.md"
        doc_path.write_text("")

        validator = get_validator(DocType.BRD)
        result = validator.validate(doc_path)

        # Should have errors for missing content
        assert len(result.errors) > 0


class TestEARSValidator:
    """Tests for EARS validator."""

    def test_validate_ears_requirements(self, tmp_path: Path):
        """Test validating EARS requirements."""
        content = """# EARS Requirements

## EARS.01 Ubiquitous Requirements

### EARS.01.01
The system shall provide user authentication.

### EARS.01.02
The system should log all access attempts.

## EARS.02 Event-Driven Requirements

### EARS.02.01
When the user logs in, the system shall create a session.
"""
        doc_path = tmp_path / "EARS-01.md"
        doc_path.write_text(content)

        validator = get_validator(DocType.EARS)
        result = validator.validate(doc_path)

        assert result is not None


class TestBDDValidator:
    """Tests for BDD validator."""

    def test_validate_gherkin_feature(self, tmp_path: Path):
        """Test validating a Gherkin feature file."""
        content = """Feature: User Authentication
  As a user
  I want to log in
  So that I can access my account

  Scenario: Successful login
    Given I am on the login page
    When I enter valid credentials
    Then I should be logged in
"""
        doc_path = tmp_path / "login.feature"
        doc_path.write_text(content)

        validator = get_validator(DocType.BDD)
        result = validator.validate(doc_path)

        assert result is not None
