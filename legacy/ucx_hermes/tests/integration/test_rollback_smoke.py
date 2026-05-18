from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.core import run_rollback_smoke  # noqa: E402
from mcp_server.reporting import (  # noqa: E402
    build_derived_artifact_name,
    build_source_artifact_name,
)


def test_rollback_smoke_restores_source_target_without_mutating_derived_artifacts() -> None:
    source_artifact = build_source_artifact_name(doc_id="SPEC-006", slug="rollback_contract")
    validation_artifact = build_derived_artifact_name(doc_id="SPEC-006", slug="rollback_contract", stage="validation-fixed")
    remediated_artifact = build_derived_artifact_name(doc_id="SPEC-006", slug="rollback_contract", stage="remediated")

    result = run_rollback_smoke(
        source_artifact=source_artifact,
        derived_artifacts=[validation_artifact, remediated_artifact],
    )

    assert result["status"] == "ok"
    assert result["rollback_ready"] is True
    assert result["rollback_action"] == "switch_execution_target_to_source"
    assert result["source_artifact"] == source_artifact
    assert result["active_artifact"] == remediated_artifact
    assert result["preserved_artifacts"] == [validation_artifact, remediated_artifact]
