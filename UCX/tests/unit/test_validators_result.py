"""Unit tests for ucx.validators.result."""

from __future__ import annotations

from ucx.validators.result import Finding, Severity, ValidationResult


class TestSeverity:
    def test_values_are_lowercase_strings(self) -> None:
        assert Severity.ERROR == "error"
        assert Severity.WARNING == "warning"
        assert Severity.INFO == "info"

    def test_severity_is_string_enum(self) -> None:
        assert isinstance(Severity.ERROR, str)


class TestFinding:
    def test_required_fields(self) -> None:
        f = Finding(code="GATE-01", message="Placeholder found", severity=Severity.ERROR)
        assert f.code == "GATE-01"
        assert f.message == "Placeholder found"
        assert f.severity == Severity.ERROR
        assert f.line is None
        assert f.context is None

    def test_optional_fields(self) -> None:
        f = Finding(
            code="GATE-02",
            message="Missing ref",
            severity=Severity.WARNING,
            line=42,
            context="## Section without ref",
        )
        assert f.line == 42
        assert f.context == "## Section without ref"

    def test_to_dict_shape(self) -> None:
        f = Finding(code="GATE-01", message="msg", severity=Severity.ERROR, line=5)
        d = f.to_dict()
        assert d["code"] == "GATE-01"
        assert d["message"] == "msg"
        assert d["severity"] == "error"
        assert d["line"] == 5
        assert "context" in d


class TestValidationResult:
    def _make_result(self, valid: bool = True, findings=None) -> ValidationResult:
        return ValidationResult(valid=valid, path="/doc.md", findings=findings or [])

    def test_valid_result_no_findings(self) -> None:
        r = self._make_result(valid=True)
        assert r.valid is True
        assert r.error_count == 0
        assert r.warning_count == 0

    def test_errors_property_filters_by_severity(self) -> None:
        findings = [
            Finding("G1", "err", Severity.ERROR),
            Finding("G2", "warn", Severity.WARNING),
            Finding("G3", "info", Severity.INFO),
        ]
        r = self._make_result(findings=findings)
        assert len(r.errors) == 1
        assert r.errors[0].code == "G1"
        assert len(r.warnings) == 1
        assert r.warnings[0].code == "G2"

    def test_error_count_and_warning_count(self) -> None:
        findings = [
            Finding("G1", "e1", Severity.ERROR),
            Finding("G2", "e2", Severity.ERROR),
            Finding("G3", "w1", Severity.WARNING),
        ]
        r = self._make_result(findings=findings)
        assert r.error_count == 2
        assert r.warning_count == 1

    def test_to_dict_shape(self) -> None:
        r = ValidationResult(
            valid=False,
            path="/some/doc.md",
            findings=[Finding("G1", "err", Severity.ERROR)],
            score=0.4,
        )
        d = r.to_dict()
        assert d["valid"] is False
        assert d["path"] == "/some/doc.md"
        assert d["score"] == 0.4
        assert d["error_count"] == 1
        assert d["warning_count"] == 0
        assert len(d["findings"]) == 1
        assert d["findings"][0]["code"] == "G1"

    def test_score_defaults_to_none(self) -> None:
        r = self._make_result()
        assert r.score is None

    def test_findings_defaults_to_empty_list(self) -> None:
        r = ValidationResult(valid=True, path="/doc.md")
        assert r.findings == []
