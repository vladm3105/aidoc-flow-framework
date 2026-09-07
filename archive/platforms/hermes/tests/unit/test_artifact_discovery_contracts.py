from __future__ import annotations

import sys
import threading
from pathlib import Path

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


def test_discover_artifacts_prefers_audit_wrapper_over_review_wrapper_on_equal_version(
    tmp_path: Path,
) -> None:
    _touch(tmp_path / build_source_artifact_name(doc_id="SPEC-004", slug="reporting_rules"))
    _touch(tmp_path / build_family_report_name(doc_id="SPEC-004", family="review", version=2))
    _touch(tmp_path / build_family_report_name(doc_id="SPEC-004", family="audit", version=2))

    discovered = discover_artifacts(folder=tmp_path, doc_id="SPEC-004", slug="reporting_rules")

    assert discovered.latest_review_report == build_family_report_name(
        doc_id="SPEC-004", family="audit", version=2
    )


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


def test_write_versioned_report_atomic_concurrent_writers_get_unique_versions(
    tmp_path: Path,
) -> None:
    """Regression for HERMES-REVIEW-001 C2 (M2).

    ``write_versioned_report_atomic`` now allocates versions via
    ``os.open(O_CREAT|O_EXCL)`` instead of the check-then-``os.replace`` TOCTOU.
    Many threads racing on the same ``report_dir`` must each win a *distinct*
    version file — none overwritten, none lost, no exceptions.
    """

    writer_count = 12

    def _factory(version: int) -> str:
        return str(build_family_report_name(doc_id="SPEC-006", family="audit", version=version))

    results: list[Path] = []
    errors: list[BaseException] = []
    guard = threading.Lock()
    start = threading.Barrier(writer_count)

    def _worker(idx: int) -> None:
        try:
            start.wait()  # release all writers together to maximize contention
            path = write_versioned_report_atomic(
                report_dir=tmp_path,
                report_name_factory=_factory,
                content=f"payload-{idx}",
                max_attempts=writer_count + 5,
            )
            with guard:
                results.append(path)
        except BaseException as exc:  # noqa: BLE001 — capture for assertion
            with guard:
                errors.append(exc)

    threads = [threading.Thread(target=_worker, args=(i,)) for i in range(writer_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=15)

    assert not any(t.is_alive() for t in threads), "a concurrent writer hung"
    assert not errors, f"concurrent versioned writes raised: {errors!r}"
    assert len(results) == writer_count
    # Every writer won a distinct path (no two allocated the same version).
    assert len({str(p) for p in results}) == writer_count
    # Every allocated file exists on disk with intact content (no lost/partial writes).
    on_disk = sorted(p for p in tmp_path.iterdir() if p.is_file())
    assert len(on_disk) == writer_count
    for path in on_disk:
        assert path.read_text(encoding="utf-8").startswith("payload-")
