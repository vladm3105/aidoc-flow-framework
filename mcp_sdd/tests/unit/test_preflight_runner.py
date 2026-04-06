from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.cli.main import main  # noqa: E402
from mcp_server.preflight.runner import run_preflight  # noqa: E402


def test_run_preflight_uses_token_fallback_status(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    probe_file = tmp_path / "tmp/preflight_probe_response.txt"
    probe_file.parent.mkdir(parents=True, exist_ok=True)
    probe_file.write_text("Provider check result: READY at 2026-03-27", encoding="utf-8")

    result = run_preflight(project_root=tmp_path, context="any", output_dir=None)

    assert result.status in {"ready", "degraded"}
    checks = result.payload.get("checks", {})
    assert isinstance(checks, dict)
    assert checks.get("probe_fallback_used") is True
    assert checks.get("probe_fallback_reason") == "token_scan"


def test_run_preflight_uses_iso_date_fallback_when_no_status_token(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    probe_file = tmp_path / "tmp/preflight_probe_response.txt"
    probe_file.parent.mkdir(parents=True, exist_ok=True)
    probe_file.write_text("Provider check completed on 2026-03-27 without explicit status", encoding="utf-8")

    result = run_preflight(project_root=tmp_path, context="any", output_dir=None)

    assert result.status == "degraded"
    checks = result.payload.get("checks", {})
    assert isinstance(checks, dict)
    assert checks.get("probe_fallback_reason") == "iso_date_fallback"
    assert checks.get("probe_status") == "degraded"


def test_run_preflight_json_status_overrides_fallback(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    probe_file = tmp_path / "tmp/preflight_probe_response.txt"
    probe_file.parent.mkdir(parents=True, exist_ok=True)
    probe_file.write_text('{"status":"blocked","note":"provider unavailable"}', encoding="utf-8")

    result = run_preflight(project_root=tmp_path, context="any", output_dir=None)

    assert result.status == "blocked"
    checks = result.payload.get("checks", {})
    assert isinstance(checks, dict)
    assert checks.get("probe_fallback_used") is False
    assert checks.get("probe_fallback_reason") == "json_status"


def test_preflight_includes_persona_health_check(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    result = run_preflight(project_root=tmp_path, context="review", output_dir=None)
    checks = result.payload.get("checks", {})
    assert "persona_mapping_health" in checks
    assert checks["persona_mapping_health"] in {"ok", "warning", "error"}


def test_preflight_reports_env_key_count(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    env_file = tmp_path / ".env"
    env_file.write_text("API_KEY=sk-test\nMODEL=gpt-4\n", encoding="utf-8")

    result = run_preflight(project_root=tmp_path, context="any", output_dir=None)
    checks = result.payload.get("checks", {})
    assert checks.get("env_key_count") == 2
    assert sorted(checks.get("env_keys", [])) == ["API_KEY", "MODEL"]


def test_preflight_reports_blocked_env_vars(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    env_file = tmp_path / ".env"
    env_file.write_text("PATH=/evil\nAPI_KEY=safe\n", encoding="utf-8")

    result = run_preflight(project_root=tmp_path, context="any", output_dir=None)
    checks = result.payload.get("checks", {})
    assert "PATH" in checks.get("env_blocked_vars", [])
    warnings = result.payload.get("warnings", [])
    assert any("env_blocked_vars" in w for w in warnings)
