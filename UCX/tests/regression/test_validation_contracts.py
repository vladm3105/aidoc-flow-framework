"""Regression tests — validation model contract stability.

These tests lock the public ValidationResult / Finding API so that
implementing PLAN-001 through PLAN-004 cannot inadvertently break
the structured return shape that MCP tools serialize.
"""

from __future__ import annotations

import pytest

from ucx.validators.result import Finding, Severity, ValidationResult


EXPECTED_FINDING_DICT_KEYS = {"code", "message", "severity", "line", "context"}
EXPECTED_RESULT_DICT_KEYS = {
    "valid", "path", "findings", "score", "error_count", "warning_count"
}


class TestFindingDictContract:
    def test_to_dict_has_all_required_keys(self) -> None:
        f = Finding(code="G1", message="msg", severity=Severity.ERROR)
        d = f.to_dict()
        assert EXPECTED_FINDING_DICT_KEYS.issubset(d.keys()), (
            f"Finding.to_dict() missing keys: {EXPECTED_FINDING_DICT_KEYS - d.keys()}"
        )

    def test_severity_serializes_to_string(self) -> None:
        for sev in Severity:
            f = Finding("G", "m", sev)
            assert isinstance(f.to_dict()["severity"], str)

    def test_code_is_string(self) -> None:
        f = Finding(code="BRD-001", message="x", severity=Severity.INFO)
        assert isinstance(f.to_dict()["code"], str)


class TestValidationResultDictContract:
    def test_to_dict_has_all_required_keys(self) -> None:
        r = ValidationResult(valid=True, path="/doc.md")
        d = r.to_dict()
        assert EXPECTED_RESULT_DICT_KEYS.issubset(d.keys()), (
            f"ValidationResult.to_dict() missing keys: {EXPECTED_RESULT_DICT_KEYS - d.keys()}"
        )

    def test_valid_is_bool(self) -> None:
        r = ValidationResult(valid=True, path="/doc.md")
        assert isinstance(r.to_dict()["valid"], bool)

    def test_findings_is_list(self) -> None:
        r = ValidationResult(valid=True, path="/doc.md")
        assert isinstance(r.to_dict()["findings"], list)

    def test_error_count_is_int(self) -> None:
        r = ValidationResult(valid=False, path="/doc.md")
        assert isinstance(r.to_dict()["error_count"], int)

    def test_path_is_string(self) -> None:
        r = ValidationResult(valid=True, path="/some/path.md")
        assert r.to_dict()["path"] == "/some/path.md"


class TestValidationResultInvariant:
    """Verify invariants that downstream tools rely on."""

    def test_invalid_result_has_at_least_one_error(self) -> None:
        """If valid=False, there should be at least one error finding."""
        r = ValidationResult(
            valid=False,
            path="/doc.md",
            findings=[Finding("G1", "err", Severity.ERROR)],
        )
        assert r.error_count >= 1

    def test_valid_result_has_zero_errors(self) -> None:
        r = ValidationResult(
            valid=True,
            path="/doc.md",
            findings=[Finding("G1", "warn", Severity.WARNING)],
        )
        assert r.error_count == 0

    def test_findings_nested_in_to_dict(self) -> None:
        findings = [
            Finding("G1", "e1", Severity.ERROR),
            Finding("G2", "w1", Severity.WARNING),
        ]
        r = ValidationResult(valid=False, path="/doc.md", findings=findings)
        d = r.to_dict()
        assert len(d["findings"]) == 2
        assert all(
            EXPECTED_FINDING_DICT_KEYS.issubset(f.keys())
            for f in d["findings"]
        )
