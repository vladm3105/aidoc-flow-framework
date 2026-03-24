from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.reporting import (  # noqa: E402
    build_family_report_name,
    build_source_artifact_name,
    discover_artifacts,
    write_versioned_report_atomic,
)


def _touch(path: Path, content: str = "fixture") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_discover_artifacts_prefers_audit_wrapper_over_review_wrapper_on_equal_version(tmp_path: Path) -> None:
    _touch(tmp_path / build_source_artifact_name(doc_id="SPEC-004", slug="reporting_rules"))
    _touch(tmp_path / build_family_report_name(doc_id="SPEC-004", family="review", version=2))
    _touch(tmp_path / build_family_report_name(doc_id="SPEC-004", family="audit", version=2))

    discovered = discover_artifacts(folder=tmp_path, doc_id="SPEC-004", slug="reporting_rules")

    assert discovered.latest_review_report == build_family_report_name(doc_id="SPEC-004", family="audit", version=2)


def test_write_versioned_report_atomic_fails_after_bounded_retries() -> None:
    tmp_path = Path(__file__).resolve().parent / ".tmp_collision_test"
    tmp_path.mkdir(parents=True, exist_ok=True)
    try:
        def report_name_factory(version: int) -> str:
            return str(build_family_report_name(doc_id="SPEC-005", family="audit", version=version))

        def collision_hook(candidate_path: Path) -> None:
            candidate_path.write_text("occupied", encoding="utf-8")

        try:
            write_versioned_report_atomic(
                report_dir=tmp_path,
                report_name_factory=report_name_factory,
                content="payload",
                max_attempts=3,
                collision_hook=collision_hook,
            )
        except FileExistsError as exc:
            assert "bounded retries" in str(exc)
        else:
            raise AssertionError("Expected FileExistsError")
    finally:
        for path in sorted(tmp_path.glob("*")):
            path.unlink()
        tmp_path.rmdir()
