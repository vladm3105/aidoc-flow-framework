from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.validation.iplan_rules import run_iplan_validation_checks  # noqa: E402


def test_iplan_rules_pass_with_minimal_valid_payload() -> None:
    yaml_data = {
        "document_control": {"iplan_ready_score": "90/100"},
        "file_manifest": {
            "files": [
                {
                    "path": "tests/unit/test_a.py",
                    "order": 1,
                    "status": "NOT_STARTED",
                    "session": None,
                    "verified": False,
                }
            ]
        },
        "execution_commands": {
            "setup": ["python -m venv .venv"],
            "implementation": ["touch src/a.py"],
            "validation": ["pytest"],
        },
        "session_handoff": {"sessions": []},
        "traceability": {
            "upstream": {
                "spec_references": ["@spec: SPEC-01"],
                "tdd_references": ["@tdd: TDD-01"],
            }
        },
        "implementation_contracts": {"provided": {"contracts": []}},
    }
    errors: list[str] = []
    warnings: list[str] = []
    passes: list[str] = []
    run_iplan_validation_checks(yaml_data=yaml_data, errors=errors, warnings=warnings, passes=passes)
    assert not errors
    assert any(msg.startswith("IPLAN-001") for msg in passes)


def test_iplan_rules_fail_when_manifest_missing_fields() -> None:
    yaml_data = {
        "document_control": {"iplan_ready_score": "90/100"},
        "file_manifest": {"files": [{"path": "src/a.py", "order": 1}]},
        "execution_commands": {"setup": ["a"], "implementation": ["b"], "validation": ["c"]},
        "session_handoff": {"sessions": []},
        "traceability": {
            "upstream": {
                "spec_references": ["@spec: SPEC-01"],
                "tdd_references": ["@tdd: TDD-01"],
            }
        },
        "implementation_contracts": {"provided": {"contracts": []}},
    }
    errors: list[str] = []
    warnings: list[str] = []
    passes: list[str] = []
    run_iplan_validation_checks(yaml_data=yaml_data, errors=errors, warnings=warnings, passes=passes)
    assert any(msg.startswith("IPLAN-002") for msg in errors)
