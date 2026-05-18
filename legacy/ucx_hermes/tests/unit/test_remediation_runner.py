from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.cli.main import main  # noqa: E402


def test_cli_validate_fix_creates_validation_artifacts(tmp_path: Path) -> None:
    """Deprecated validate-fix delegates to merged validate; fix artifacts are produced on error."""
    main(["init", "--project", str(tmp_path)])

    document = tmp_path / "docs/01_BRD/BRD-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("# BRD-01\n", encoding="utf-8")

    out_dir = tmp_path / "tmp/validate"
    exit_code = main(
        [
            "validate-fix",
            "--project",
            str(tmp_path),
            "--doc-type",
            "brd",
            "--layer",
            "01_BRD",
            "--document",
            str(document),
            "--out",
            str(out_dir),
        ]
    )

    # Document has no frontmatter — validation fails, fix artifacts generated
    assert exit_code == 1
    assert (out_dir / "BRD-01.ucx.validate.json").exists()
    assert (out_dir / "BRD-01.ucx.validate_fix.json").exists()
    assert (out_dir / "BRD-01.ucx.validate_fix.txt").exists()
    assert (out_dir / "BRD-01_sample_validated.md").exists()


def test_cli_remediate_and_remediate_fix_create_outputs(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])

    document = tmp_path / "docs/01_BRD/BRD-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("TODO: complete section\n", encoding="utf-8")

    remediation_out = tmp_path / "tmp/remediate"
    remediate_exit = main(
        [
            "remediate",
            "--project",
            str(tmp_path),
            "--doc-type",
            "brd",
            "--layer",
            "01_BRD",
            "--document",
            str(document),
            "--out",
            str(remediation_out),
        ]
    )

    assert remediate_exit == 0
    report_path = remediation_out / "BRD-01.ucx.remediate.json"
    assert report_path.exists()

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["total_findings"] >= 1
    for finding in payload["findings"]:
        assert finding["finding_id"].startswith("P")
        assert finding["action_id"].startswith("ACT-")
        assert finding["priority"] in {"P1", "P2", "P3"}

    remediate_fix_exit = main(
        [
            "remediate-fix",
            "--project",
            str(tmp_path),
            "--doc-type",
            "brd",
            "--layer",
            "01_BRD",
            "--document",
            str(document),
            "--remediation-report",
            str(report_path),
            "--out",
            str(remediation_out),
        ]
    )

    assert remediate_fix_exit == 0
    assert (remediation_out / "BRD-01.ucx.remediate_fix.json").exists()
    assert (remediation_out / "BRD-01_sample_remediate_v1.md").exists()


def test_validate_fix_fails_for_invalid_validation_report_path(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    document = tmp_path / "docs/01_BRD/BRD-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("# BRD-01\n", encoding="utf-8")

    missing_report = tmp_path / "tmp/missing_validation_report.json"
    exit_code = main(
        [
            "validate-fix",
            "--project",
            str(tmp_path),
            "--doc-type",
            "brd",
            "--layer",
            "01_BRD",
            "--document",
            str(document),
            "--validation-report",
            str(missing_report),
        ]
    )

    assert exit_code == 1


def test_cli_validate_fix_directory_prefers_source_artifact(tmp_path: Path) -> None:
    """Deprecated validate-fix on directory input prefers canonical source for derived copy."""
    main(["init", "--project", str(tmp_path)])

    doc_dir = tmp_path / "docs/01_BRD/BRD-01_platform"
    doc_dir.mkdir(parents=True, exist_ok=True)
    source_doc = doc_dir / "BRD-01_platform.md"
    source_doc.write_text("# BRD-01\n", encoding="utf-8")
    (doc_dir / "BRD-01_platform_remediate_copy.md").write_text("# remediated copy\n", encoding="utf-8")

    out_dir = tmp_path / "tmp/validate"
    exit_code = main(
        [
            "validate-fix",
            "--project",
            str(tmp_path),
            "--doc-type",
            "brd",
            "--layer",
            "01_BRD",
            "--document",
            str(doc_dir),
            "--out",
            str(out_dir),
        ]
    )

    # Document has no frontmatter — validation fails, fix artifacts generated
    assert exit_code == 1
    assert (out_dir / "BRD-01_platform_validated.md").exists()
    assert not (out_dir / "BRD-01_platform_validated" / "BRD-01_platform.md").exists()


def test_cli_remediate_fix_directory_prefers_validation_copy(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])

    doc_dir = tmp_path / "docs/02_PRD/PRD-01_platform"
    doc_dir.mkdir(parents=True, exist_ok=True)
    (doc_dir / "PRD-01_platform.md").write_text("# source\n", encoding="utf-8")
    (doc_dir / "PRD-01_platform_validated.md").write_text("# validation copy\n", encoding="utf-8")

    out_dir = tmp_path / "tmp/remediate"
    exit_code = main(
        [
            "remediate-fix",
            "--project",
            str(tmp_path),
            "--doc-type",
            "prd",
            "--layer",
            "02_PRD",
            "--document",
            str(doc_dir),
            "--out",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    # Uses _validated as input -> _remediate_v1 output with canonical base stem
    assert (out_dir / "PRD-01_platform_remediate_v1.md").exists()
    # Must NOT create a tree copy of the whole folder
    assert not (out_dir / f"{doc_dir.name}_remediate_v1").exists()
    # Must NOT create _validated_remediate_v1 (non-canonical name)
    assert not (out_dir / "PRD-01_platform_validated_remediate_v1.md").exists()


def test_remediate_fix_fails_for_invalid_remediation_report_path(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    document = tmp_path / "docs/01_BRD/BRD-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("TODO: complete section\n", encoding="utf-8")

    missing_report = tmp_path / "tmp/missing_remediation_report.json"
    exit_code = main(
        [
            "remediate-fix",
            "--project",
            str(tmp_path),
            "--doc-type",
            "brd",
            "--layer",
            "01_BRD",
            "--document",
            str(document),
            "--remediation-report",
            str(missing_report),
        ]
    )

    assert exit_code == 1


def test_validate_fix_emits_source_protection_telemetry(tmp_path: Path) -> None:
    """Deprecated validate-fix delegates to merged validate; telemetry in fix report."""
    main(["init", "--project", str(tmp_path)])
    document = tmp_path / "docs/01_BRD/BRD-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("# BRD-01\n", encoding="utf-8")

    out_dir = tmp_path / "tmp/validate"
    exit_code = main(
        [
            "validate-fix",
            "--project",
            str(tmp_path),
            "--doc-type",
            "brd",
            "--layer",
            "01_BRD",
            "--document",
            str(document),
            "--out",
            str(out_dir),
        ]
    )

    assert exit_code == 1  # Validation fails (no frontmatter), fix artifacts generated
    payload = json.loads((out_dir / "BRD-01.ucx.validate_fix.json").read_text(encoding="utf-8"))
    telemetry = payload.get("source_protection_telemetry", {})
    assert isinstance(telemetry, dict)
    assert telemetry.get("source_protection_enabled") is True
    assert telemetry.get("restoration_events") == 0
    assert telemetry.get("guard_status") == "clean"


def test_validate_fix_restores_source_when_mutated(tmp_path: Path, monkeypatch) -> None:
    main(["init", "--project", str(tmp_path)])
    document = tmp_path / "docs/01_BRD/BRD-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    original = "# BRD-01\n"
    document.write_text(original, encoding="utf-8")

    def _mutating_copy(src: Path, suffix: str, output_dir: Path) -> Path:
        src.write_text("# MUTATED\n", encoding="utf-8")
        output_dir.mkdir(parents=True, exist_ok=True)
        target = output_dir / f"{src.stem}_{suffix}{src.suffix}"
        target.write_text("# derived\n", encoding="utf-8")
        return target

    monkeypatch.setattr("mcp_server.remediation.runner._copy_with_suffix", _mutating_copy)

    out_dir = tmp_path / "tmp/validate"
    exit_code = main(
        [
            "validate-fix",
            "--project",
            str(tmp_path),
            "--doc-type",
            "brd",
            "--layer",
            "01_BRD",
            "--document",
            str(document),
            "--out",
            str(out_dir),
        ]
    )

    assert exit_code == 1  # Validation fails, fix artifacts generated
    assert document.read_text(encoding="utf-8") == original
    payload = json.loads((out_dir / "BRD-01.ucx.validate_fix.json").read_text(encoding="utf-8"))
    telemetry = payload.get("source_protection_telemetry", {})
    assert isinstance(telemetry, dict)
    assert telemetry.get("restoration_events") == 1
    assert telemetry.get("guard_status") == "restored"


def test_validate_fix_omits_telemetry_when_source_monitoring_not_applicable(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    doc_dir = tmp_path / "docs/01_BRD/BRD-01_sections"
    doc_dir.mkdir(parents=True, exist_ok=True)
    (doc_dir / "BRD-01.1_intro.md").write_text("# Intro\n", encoding="utf-8")

    out_dir = tmp_path / "tmp/validate"
    exit_code = main(
        [
            "validate-fix",
            "--project",
            str(tmp_path),
            "--doc-type",
            "brd",
            "--layer",
            "01_BRD",
            "--document",
            str(doc_dir),
            "--out",
            str(out_dir),
        ]
    )

    assert exit_code == 1  # Validation fails, fix artifacts generated
    payload = json.loads((out_dir / "BRD-01.ucx.validate_fix.json").read_text(encoding="utf-8"))
    assert "source_protection_telemetry" not in payload


def test_remediation_findings_use_stable_hash_ids_across_reruns(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])

    document = tmp_path / "docs/01_BRD/BRD-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("TODO: complete section\n", encoding="utf-8")

    out_first = tmp_path / "tmp/remediate-first"
    out_second = tmp_path / "tmp/remediate-second"

    assert (
        main(
            [
                "remediate",
                "--project",
                str(tmp_path),
                "--doc-type",
                "brd",
                "--layer",
                "01_BRD",
                "--document",
                str(document),
                "--out",
                str(out_first),
            ]
        )
        == 0
    )
    assert (
        main(
            [
                "remediate",
                "--project",
                str(tmp_path),
                "--doc-type",
                "brd",
                "--layer",
                "01_BRD",
                "--document",
                str(document),
                "--out",
                str(out_second),
            ]
        )
        == 0
    )

    first_payload = json.loads((out_first / "BRD-01.ucx.remediate.json").read_text(encoding="utf-8"))
    second_payload = json.loads((out_second / "BRD-01.ucx.remediate.json").read_text(encoding="utf-8"))

    first_pairs = [(item["finding_id"], item["action_id"]) for item in first_payload["findings"]]
    second_pairs = [(item["finding_id"], item["action_id"]) for item in second_payload["findings"]]

    assert first_pairs == second_pairs


# ── Versioned remediation copies ────────────────────────────────────────────


def test_remediate_fix_version_incrementing(tmp_path: Path) -> None:
    """Run remediate_fix twice -> both _v1 and _v2 exist, v1 not overwritten."""
    main(["init", "--project", str(tmp_path)])
    document = tmp_path / "docs/01_BRD/BRD-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("TODO: complete section\n", encoding="utf-8")

    out_dir = tmp_path / "tmp/remediate"

    # First run
    assert main([
        "remediate-fix", "--project", str(tmp_path),
        "--doc-type", "brd", "--layer", "01_BRD",
        "--document", str(document), "--out", str(out_dir),
    ]) == 0
    v1 = out_dir / "BRD-01_sample_remediate_v1.md"
    assert v1.exists()
    v1_content = v1.read_text(encoding="utf-8")

    # Second run
    assert main([
        "remediate-fix", "--project", str(tmp_path),
        "--doc-type", "brd", "--layer", "01_BRD",
        "--document", str(document), "--out", str(out_dir),
    ]) == 0
    v2 = out_dir / "BRD-01_sample_remediate_v2.md"
    assert v2.exists()
    # v1 must not be overwritten
    assert v1.read_text(encoding="utf-8") == v1_content


def test_remediate_fix_iterative_flow(tmp_path: Path) -> None:
    """Pass _remediate_v1 as document -> produces _v2 (canonical stem properly stripped)."""
    main(["init", "--project", str(tmp_path)])
    doc_dir = tmp_path / "docs/01_BRD"
    doc_dir.mkdir(parents=True, exist_ok=True)
    source = doc_dir / "BRD-01_sample.md"
    source.write_text("# BRD-01\n", encoding="utf-8")

    out_dir = tmp_path / "tmp/remediate"

    # Create v1
    assert main([
        "remediate-fix", "--project", str(tmp_path),
        "--doc-type", "brd", "--layer", "01_BRD",
        "--document", str(source), "--out", str(out_dir),
    ]) == 0
    v1 = out_dir / "BRD-01_sample_remediate_v1.md"
    assert v1.exists()

    # Pass v1 as input document -> should create v2 with canonical stem
    assert main([
        "remediate-fix", "--project", str(tmp_path),
        "--doc-type", "brd", "--layer", "01_BRD",
        "--document", str(v1), "--out", str(out_dir),
    ]) == 0
    v2 = out_dir / "BRD-01_sample_remediate_v2.md"
    assert v2.exists()


def test_remediate_fix_directory_versioning(tmp_path: Path) -> None:
    """Run remediate_fix on directory twice -> both _v1/ and _v2/ dirs exist."""
    main(["init", "--project", str(tmp_path)])

    doc_dir = tmp_path / "docs/01_BRD/BRD-01_sections"
    doc_dir.mkdir(parents=True, exist_ok=True)
    (doc_dir / "BRD-01.1_intro.md").write_text("# Intro\n", encoding="utf-8")

    out_dir = tmp_path / "tmp/remediate"

    # First run
    assert main([
        "remediate-fix", "--project", str(tmp_path),
        "--doc-type", "brd", "--layer", "01_BRD",
        "--document", str(doc_dir), "--out", str(out_dir),
    ]) == 0
    v1_dir = out_dir / "BRD-01_sections_remediate_v1"
    assert v1_dir.exists() and v1_dir.is_dir()

    # Second run
    assert main([
        "remediate-fix", "--project", str(tmp_path),
        "--doc-type", "brd", "--layer", "01_BRD",
        "--document", str(doc_dir), "--out", str(out_dir),
    ]) == 0
    v2_dir = out_dir / "BRD-01_sections_remediate_v2"
    assert v2_dir.exists() and v2_dir.is_dir()
    # v1 must still exist
    assert v1_dir.exists()


def test_remediate_fix_backward_compat_legacy_copy(tmp_path: Path) -> None:
    """Pre-existing _remediate_copy is excluded from source discovery; fix creates _v1."""
    main(["init", "--project", str(tmp_path)])
    doc_dir = tmp_path / "docs/01_BRD"
    doc_dir.mkdir(parents=True, exist_ok=True)
    source = doc_dir / "BRD-01_sample.md"
    source.write_text("# BRD-01\n", encoding="utf-8")
    legacy = doc_dir / "BRD-01_sample_remediate_copy.md"
    legacy.write_text("# legacy\n", encoding="utf-8")

    out_dir = tmp_path / "tmp/remediate"
    assert main([
        "remediate-fix", "--project", str(tmp_path),
        "--doc-type", "brd", "--layer", "01_BRD",
        "--document", str(source), "--out", str(out_dir),
    ]) == 0
    # Creates v1, not v2 (legacy _remediate_copy doesn't count as v0)
    assert (out_dir / "BRD-01_sample_remediate_v1.md").exists()


def test_remediate_fix_prefix_safety(tmp_path: Path) -> None:
    """Two documents with shared prefix -> version numbers independent."""
    main(["init", "--project", str(tmp_path)])
    doc_dir = tmp_path / "docs/01_BRD"
    doc_dir.mkdir(parents=True, exist_ok=True)

    short = doc_dir / "BRD-01_test.md"
    short.write_text("# short\n", encoding="utf-8")
    extended = doc_dir / "BRD-01_test_extended.md"
    extended.write_text("# extended\n", encoding="utf-8")

    out_dir = tmp_path / "tmp/remediate"

    # Create v1 for extended
    assert main([
        "remediate-fix", "--project", str(tmp_path),
        "--doc-type", "brd", "--layer", "01_BRD",
        "--document", str(extended), "--out", str(out_dir),
    ]) == 0
    assert (out_dir / "BRD-01_test_extended_remediate_v1.md").exists()

    # Create v1 for short — should NOT be v2 due to extended prefix match
    assert main([
        "remediate-fix", "--project", str(tmp_path),
        "--doc-type", "brd", "--layer", "01_BRD",
        "--document", str(short), "--out", str(out_dir),
    ]) == 0
    assert (out_dir / "BRD-01_test_remediate_v1.md").exists()


def test_remediate_fix_chain_via_cli(tmp_path: Path) -> None:
    """sdd_remediate --fix produces both findings JSON and versioned copy."""
    main(["init", "--project", str(tmp_path)])
    document = tmp_path / "docs/01_BRD/BRD-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("TODO: complete section\n", encoding="utf-8")

    out_dir = tmp_path / "tmp/remediate"
    assert main([
        "remediate", "--fix", "--project", str(tmp_path),
        "--doc-type", "brd", "--layer", "01_BRD",
        "--document", str(document), "--out", str(out_dir),
    ]) == 0

    # Remediation findings report
    assert (out_dir / "BRD-01.ucx.remediate.json").exists()
    # Versioned copy from auto-chained fix
    assert (out_dir / "BRD-01_sample_remediate_v1.md").exists()
