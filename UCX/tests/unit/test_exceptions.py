"""Unit tests for ucx.exceptions."""

from __future__ import annotations

import pytest

from ucx.exceptions import (
    UCXAIError,
    UCXConfigError,
    UCXDocumentNotFound,
    UCXError,
    UCXStageError,
    UCXToolError,
    UCXValidationError,
)


class TestUCXErrorHierarchy:
    def test_all_exceptions_inherit_ucx_error(self) -> None:
        for exc_class in [
            UCXConfigError,
            UCXValidationError,
            UCXDocumentNotFound,
            UCXStageError,
            UCXAIError,
            UCXToolError,
        ]:
            assert issubclass(exc_class, UCXError)

    def test_all_exceptions_inherit_base_exception(self) -> None:
        assert issubclass(UCXError, Exception)


class TestUCXValidationError:
    def test_stores_path_and_count(self) -> None:
        err = UCXValidationError("failed", path="/some/doc.md", error_count=3)
        assert err.path == "/some/doc.md"
        assert err.error_count == 3
        assert str(err) == "failed"

    def test_default_error_count_is_zero(self) -> None:
        err = UCXValidationError("failed", path="/doc.md")
        assert err.error_count == 0


class TestUCXDocumentNotFound:
    def test_message_includes_path(self) -> None:
        err = UCXDocumentNotFound("/missing/file.md")
        assert "/missing/file.md" in str(err)
        assert err.path == "/missing/file.md"


class TestUCXStageError:
    def test_stores_stage_info(self) -> None:
        err = UCXStageError(
            "invalid transition",
            required_stage="validated",
            actual_stage="created",
        )
        assert err.required_stage == "validated"
        assert err.actual_stage == "created"
        assert "invalid transition" in str(err)


class TestExceptionRaising:
    def test_ucx_validation_error_is_catchable_as_ucx_error(self) -> None:
        with pytest.raises(UCXError):
            raise UCXValidationError("bad doc", path="/doc.md")

    def test_ucx_document_not_found_is_catchable_as_ucx_error(self) -> None:
        with pytest.raises(UCXError):
            raise UCXDocumentNotFound("/nonexistent.md")
