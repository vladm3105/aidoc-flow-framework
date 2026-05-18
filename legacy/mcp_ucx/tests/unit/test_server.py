"""Tests for MCP transport layer: tool registry, handlers, executor registry, pipeline."""

from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_server.tool_registry import TOOLS, handle_tool, _inspect_document_folder
from mcp_server.executor.registry import (
    ExecutorConfig,
    ExecutorType,
    get_executor,
    list_executors,
    register_executor,
    remove_executor,
)
from mcp_server.executor.cli_runner import ExecutorResult


# ── Tool registry tests ─────────────────────────────────────────────────────


class TestToolRegistry:
    def test_tool_count(self):
        assert len(TOOLS) == 26  # +3 persona, +1 env_show, +2 project mgmt, +1 chg validate

    def test_tool_names_unique(self):
        names = [t.name for t in TOOLS]
        assert len(names) == len(set(names)), f"Duplicate tool names: {[n for n in names if names.count(n) > 1]}"

    def test_all_tools_have_input_schema(self):
        for tool in TOOLS:
            assert tool.inputSchema is not None, f"Tool {tool.name} missing inputSchema"
            assert "type" in tool.inputSchema, f"Tool {tool.name} schema missing 'type'"
            assert tool.inputSchema["type"] == "object"

    def test_all_tools_have_required_field(self):
        for tool in TOOLS:
            assert "required" in tool.inputSchema, f"Tool {tool.name} schema missing 'required'"

    def test_deterministic_tool_names(self):
        deterministic = {
            "sdd_init", "sdd_validate", "sdd_consistency", "sdd_validate_links", "sdd_preflight",
            "sdd_prescreen", "sdd_scan", "sdd_score_show", "sdd_score_validate",
            "sdd_score_compare", "sdd_list_executors", "sdd_register_executor", "sdd_validate_chg",
        }
        tool_names = {t.name for t in TOOLS}
        assert deterministic.issubset(tool_names)

    def test_orchestration_tool_names(self):
        orchestration = {"sdd_next_action", "sdd_run_lifecycle"}
        tool_names = {t.name for t in TOOLS}
        assert orchestration.issubset(tool_names)

    def test_llm_dependent_tool_names(self):
        llm_dependent = {
            "sdd_create_build", "sdd_create", "sdd_review",
            "sdd_remediate",
        }
        tool_names = {t.name for t in TOOLS}
        assert llm_dependent.issubset(tool_names)
        assert "sdd_validate_fix" not in tool_names
        assert "sdd_remediate_fix" not in tool_names  # Absorbed into sdd_remediate

    def test_maintenance_tool_names(self):
        tool_names = {t.name for t in TOOLS}
        assert "sdd_clean" in tool_names

    def test_llm_tools_have_executor_param(self):
        llm_tools = ["sdd_create_build", "sdd_create", "sdd_review",
                      "sdd_validate", "sdd_remediate"]
        for tool in TOOLS:
            if tool.name in llm_tools:
                props = tool.inputSchema.get("properties", {})
                assert "executor" in props, f"Tool {tool.name} missing 'executor' param"

    def test_sdd_validate_has_control_params(self):
        validate_tool = next(t for t in TOOLS if t.name == "sdd_validate")
        props = validate_tool.inputSchema["properties"]
        assert "tier1_only" in props
        assert "strict" in props
        assert "format" in props
        assert "executor" in props
        assert "timeout" in props
        assert "validation_report" in props

    def test_sdd_create_has_target_param(self):
        create_tool = next(t for t in TOOLS if t.name == "sdd_create")
        assert "target" in create_tool.inputSchema["required"]


# ── Executor registry tests ─────────────────────────────────────────────────


class TestExecutorRegistry:
    def test_builtin_executors_registered(self):
        executors = list_executors()
        names = {e.name for e in executors}
        assert "claude" in names
        assert "codex" in names
        assert "gemini" in names
        assert "opencode" in names

    def test_builtin_api_stubs_registered(self):
        executors = list_executors()
        names = {e.name for e in executors}
        assert "api/gpt-4o" in names
        assert "api/claude-sonnet" in names
        assert "api/gemini-pro" in names

    def test_get_known_executor(self):
        config = get_executor("claude")
        assert config.name == "claude"
        assert config.executor_type == ExecutorType.CLI
        assert config.command == "claude"

    def test_get_unknown_executor_raises(self):
        with pytest.raises(KeyError, match="Unknown executor"):
            get_executor("nonexistent-agent")

    def test_register_custom_executor(self):
        config = ExecutorConfig(
            name="test-agent",
            executor_type=ExecutorType.CLI,
            command="test-agent",
            args=["--run"],
            prompt_mode="positional",
        )
        register_executor(config)
        retrieved = get_executor("test-agent")
        assert retrieved.command == "test-agent"
        # Cleanup
        remove_executor("test-agent")

    def test_remove_executor(self):
        config = ExecutorConfig(
            name="temp-agent",
            executor_type=ExecutorType.CLI,
            command="temp",
        )
        register_executor(config)
        remove_executor("temp-agent")
        with pytest.raises(KeyError):
            get_executor("temp-agent")

    def test_remove_nonexistent_raises(self):
        with pytest.raises(KeyError):
            remove_executor("ghost-agent")

    def test_api_executor_has_active_status(self):
        config = get_executor("api/gpt-4o")
        assert config.executor_type == ExecutorType.API
        assert config.status == "active"
        assert config.model == "gpt-4o"

    def test_openrouter_executor_registered(self):
        config = get_executor("api/openrouter")
        assert config.executor_type == ExecutorType.API
        assert config.model == "openrouter/auto"
        assert config.api_key_env == "OPENROUTER_API_KEY"

    def test_copilot_experimental_status(self):
        config = get_executor("copilot-cli")
        assert config.status == "experimental"

    def test_load_config_file_old_array_format(self, tmp_path):
        from mcp_server.executor.registry import load_config_file
        config_file = tmp_path / "executors.json"
        config_file.write_text(
            json.dumps([{"name": "test-old", "executor_type": "cli", "command": "echo"}]),
            encoding="utf-8",
        )
        count = load_config_file(config_file)
        assert count == 1
        cfg = get_executor("test-old")
        assert cfg.command == "echo"
        remove_executor("test-old")

    def test_load_config_file_new_object_format(self, tmp_path):
        from mcp_server.executor.registry import load_config_file
        import mcp_server.project_context as pc
        old_config = pc._config_default_project
        config_file = tmp_path / "executors.json"
        config_file.write_text(
            json.dumps({
                "default_project": str(tmp_path),
                "executors": [{"name": "test-new", "executor_type": "cli", "command": "echo"}],
            }),
            encoding="utf-8",
        )
        count = load_config_file(config_file)
        assert count == 1
        assert pc._config_default_project == tmp_path
        cfg = get_executor("test-new")
        assert cfg.command == "echo"
        remove_executor("test-new")
        pc._config_default_project = old_config

    def test_load_config_file_object_without_executors(self, tmp_path):
        from mcp_server.executor.registry import load_config_file
        import mcp_server.project_context as pc
        old_config = pc._config_default_project
        config_file = tmp_path / "executors.json"
        config_file.write_text(
            json.dumps({"default_project": str(tmp_path)}),
            encoding="utf-8",
        )
        count = load_config_file(config_file)
        assert count == 0
        assert pc._config_default_project == tmp_path
        pc._config_default_project = old_config


# ── Handler tests ────────────────────────────────────────────────────────────


class TestHandlers:
    def test_unknown_tool_returns_error(self):
        result = asyncio.get_event_loop().run_until_complete(
            handle_tool("nonexistent_tool", {})
        )
        assert len(result) == 1
        payload = json.loads(result[0].text)
        assert "error" in payload

    def test_sdd_list_executors(self):
        result = asyncio.get_event_loop().run_until_complete(
            handle_tool("sdd_list_executors", {})
        )
        payload = json.loads(result[0].text)
        assert "executors" in payload
        names = {e["name"] for e in payload["executors"]}
        assert "claude" in names

    def test_sdd_register_executor_via_handler(self):
        result = asyncio.get_event_loop().run_until_complete(
            handle_tool("sdd_register_executor", {
                "name": "handler-test-agent",
                "executor_type": "cli",
                "command": "test",
                "args": ["--go"],
                "prompt_mode": "positional",
            })
        )
        payload = json.loads(result[0].text)
        assert payload["registered"] == "handler-test-agent"
        # Cleanup
        remove_executor("handler-test-agent")

    def test_sdd_validate_chg_dispatch(self, tmp_path):
        chg_doc = tmp_path / "docs" / "CHG" / "CHG-01_test.yaml"
        chg_doc.parent.mkdir(parents=True, exist_ok=True)
        chg_doc.write_text(
            """
metadata:
  document_type: chg-document
  tags: [chg-document]
change_control:
  change_level: C2
  change_source: design
  entry_gate: GATE-06
impact_assessment:
  affected_layers:
    - layer: SPEC
gate_approval:
  gate: null
  approver: null
rollback_plan:
  strategy: revert-commit
emergency_change:
  emergency_id: null
  fix_deployed: null
  post_hoc_gate: null
""".strip()
            + "\n",
            encoding="utf-8",
        )
        layer_dir = tmp_path / "CHG"
        layer_dir.mkdir(parents=True, exist_ok=True)
        (layer_dir / "CHG-TEMPLATE.yaml").write_text(
            """
metadata:
  required_tags:
    - chg-document
sections: []
""".strip()
            + "\n",
            encoding="utf-8",
        )

        result = asyncio.get_event_loop().run_until_complete(
            handle_tool(
                "sdd_validate_chg",
                {
                    "project": str(tmp_path),
                    "layer": "CHG",
                    "document": str(chg_doc),
                },
            )
        )
        payload = json.loads(result[0].text)
        assert "is_valid" in payload


# ── Next action advisor tests ────────────────────────────────────────────────


class TestNextAction:
    def test_empty_folder(self, tmp_path):
        result = _inspect_document_folder(tmp_path)
        assert result["current_stage"] == "empty"
        assert result["next_action"] == "create"
        assert result["next_tool"] == "sdd_create"

    def test_source_only(self, tmp_path):
        (tmp_path / "BRD-01_platform.md").write_text("# BRD")
        result = _inspect_document_folder(tmp_path)
        assert result["current_stage"] == "created"
        assert result["next_action"] == "validate"

    def test_after_validation(self, tmp_path):
        (tmp_path / "BRD-01_platform.md").write_text("# BRD")
        (tmp_path / "BRD-01.ucx.validate.json").write_text("{}")
        result = _inspect_document_folder(tmp_path)
        assert result["current_stage"] == "validated"
        assert result["next_action"] == "review"
        assert result["next_tool"] == "sdd_review"

    def test_after_validation_fix(self, tmp_path):
        (tmp_path / "BRD-01_platform.md").write_text("# BRD")
        (tmp_path / "BRD-01.ucx.validate.json").write_text("{}")
        (tmp_path / "BRD-01_platform_validated.md").write_text("# BRD fixed")
        result = _inspect_document_folder(tmp_path)
        assert result["current_stage"] == "validated"
        assert result["next_action"] == "review"
        assert result["next_tool"] == "sdd_review"

    def test_after_review(self, tmp_path):
        (tmp_path / "BRD-01_platform.md").write_text("# BRD")
        (tmp_path / "BRD-01_platform_validated.md").write_text("# fixed")
        (tmp_path / "BRD-01.ucx.review.md").write_text("# review")
        result = _inspect_document_folder(tmp_path)
        assert result["current_stage"] == "reviewed"
        assert result["next_action"] == "remediate"

    def test_after_remediation_report(self, tmp_path):
        (tmp_path / "BRD-01_platform.md").write_text("# BRD")
        (tmp_path / "BRD-01_platform_validated.md").write_text("# fixed")
        (tmp_path / "BRD-01.ucx.remediate.md").write_text("# rem")
        result = _inspect_document_folder(tmp_path)
        assert result["current_stage"] == "remediation_reported"
        assert result["next_action"] == "remediate --fix"

    def test_fully_remediated(self, tmp_path):
        (tmp_path / "BRD-01_platform.md").write_text("# BRD")
        (tmp_path / "BRD-01_platform_remediate_v1.md").write_text("# final")
        result = _inspect_document_folder(tmp_path)
        assert result["current_stage"] == "remediated"
        assert result["next_action"] == "done"
        assert result["next_tool"] is None


# ── Pipeline tests ───────────────────────────────────────────────────────────


class TestLifecyclePipeline:
    def test_pipeline_stops_on_failure(self):
        """Pipeline should stop when a stage returns passed=False (e.g. review)."""
        import mcp_server.tool_registry as tr
        original = tr._dispatch

        call_count = 0
        async def mock_dispatch(name, arguments):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # validate now always returns passed=True (stage completed)
                return {"passed": True, "is_valid": False, "fix_generated": True}
            return {"passed": False, "errors": ["Missing section"]}

        async def _run():
            tr._dispatch = mock_dispatch
            try:
                result = await tr._handle_lifecycle_pipeline({
                    "project": "/tmp/test",
                    "doc_type": "brd",
                    "layer": "01_BRD",
                    "document": "/tmp/test/docs/01_BRD/BRD-01/",
                    "stages": ["validate", "review"],
                })
                return result
            finally:
                tr._dispatch = original

        payload = asyncio.get_event_loop().run_until_complete(_run())
        assert payload.get("_stopped_at") == "review"
        assert call_count == 2

    def test_pipeline_completes_all_stages(self):
        """Pipeline should run all stages when none fail."""
        import mcp_server.tool_registry as tr
        original = tr._dispatch

        async def mock_dispatch(name, arguments):
            return {"passed": True, "report_text": "ok"}

        async def _run():
            tr._dispatch = mock_dispatch
            try:
                result = await tr._handle_lifecycle_pipeline({
                    "project": "/tmp/test",
                    "doc_type": "brd",
                    "layer": "01_BRD",
                    "document": "/tmp/test/docs/01_BRD/BRD-01/",
                    "stages": ["validate", "review"],
                })
                return result
            finally:
                tr._dispatch = original

        payload = asyncio.get_event_loop().run_until_complete(_run())
        assert "_stopped_at" not in payload
        assert "validate" in payload["_completed_stages"]
        assert "review" in payload["_completed_stages"]

    def test_validate_fix_stage_absorbed(self):
        """Pipeline should absorb validate_fix when validate already ran."""
        import mcp_server.tool_registry as tr
        original = tr._dispatch

        call_count = 0
        async def mock_dispatch(name, arguments):
            nonlocal call_count
            call_count += 1
            return {"passed": True, "fix_generated": True, "is_valid": False}

        async def _run():
            tr._dispatch = mock_dispatch
            try:
                result = await tr._handle_lifecycle_pipeline({
                    "project": "/tmp/test",
                    "doc_type": "brd",
                    "layer": "01_BRD",
                    "document": "/tmp/test/docs/01_BRD/BRD-01/",
                    "stages": ["validate", "validate_fix"],
                })
                return result
            finally:
                tr._dispatch = original

        payload = asyncio.get_event_loop().run_until_complete(_run())
        assert call_count == 1  # Only validate dispatched, validate_fix absorbed
        assert payload["validate_fix"].get("_absorbed") is True
        assert "validate" in payload["_completed_stages"]
        assert "validate_fix" in payload["_completed_stages"]


# ── Error handling tests ─────────────────────────────────────────────────────


class TestErrorHandling:
    def test_handler_catches_exception(self):
        """Handler should return error JSON, not raise."""
        result = asyncio.get_event_loop().run_until_complete(
            handle_tool("sdd_validate", {"project": "/nonexistent"})
        )
        payload = json.loads(result[0].text)
        assert "error" in payload

    def test_executor_result_frozen(self):
        result = ExecutorResult(
            stdout="ok",
            stderr="",
            exit_code=0,
            executor_name="test",
        )
        with pytest.raises(AttributeError):
            result.stdout = "modified"


class TestReviewReportPersistence:
    """Verify executor review output is saved to document folder."""

    def test_review_report_saved_on_executor_success(self, tmp_path):
        from mcp_server.review.runner import ReviewRunResult

        # Set up minimal document folder
        doc_dir = tmp_path / "docs" / "01_BRD" / "BRD-01_platform"
        doc_dir.mkdir(parents=True)
        (doc_dir / "BRD-01_platform.md").write_text("# BRD-01")

        fake_review_result = ReviewRunResult(
            prompt_text="review prompt text",
            sidecar_json="{}",
            inspection={},
            layer_asset_names=[],
            prompt_path=None,
            sidecar_path=None,
            inspection_path=None,
        )
        fake_exec_result = ExecutorResult(
            stdout="## Review Report\nREM-P0-001 finding",
            stderr="",
            exit_code=0,
            executor_name="claude",
        )

        # Patch the two dependencies: review build + executor
        with (
            patch(
                "mcp_server.review.run_project_review_build",
                return_value=fake_review_result,
            ),
            patch(
                "mcp_server.tool_registry.run_executor",
                new_callable=AsyncMock,
                return_value=fake_exec_result,
            ),
        ):
            result = asyncio.get_event_loop().run_until_complete(
                handle_tool("sdd_review", {
                    "project": str(tmp_path),
                    "doc_type": "brd",
                    "template": "UCR_PROMPT_BRD_PROJECT.md",
                    "document": str(doc_dir),
                    "executor": "claude",
                    "sections": [{"section_id": "BRD-01", "title": "BRD-01", "content": "# BRD-01"}],
                })
            )

        payload = json.loads(result[0].text)
        assert payload.get("review_report_path") is not None

        report_path = Path(payload["review_report_path"])
        assert report_path.exists()
        assert report_path.name == "BRD-01.ucx.review.md"
        assert "REM-P0-001" in report_path.read_text(encoding="utf-8")

    def test_review_report_not_saved_without_executor(self, tmp_path):
        from mcp_server.review.runner import ReviewRunResult

        doc_dir = tmp_path / "docs" / "01_BRD" / "BRD-01_platform"
        doc_dir.mkdir(parents=True)
        (doc_dir / "BRD-01_platform.md").write_text("# BRD-01")

        fake_review_result = ReviewRunResult(
            prompt_text="review prompt text",
            sidecar_json="{}",
            inspection={},
            layer_asset_names=[],
            prompt_path=None,
            sidecar_path=None,
            inspection_path=None,
        )

        with patch(
            "mcp_server.review.run_project_review_build",
            return_value=fake_review_result,
        ):
            result = asyncio.get_event_loop().run_until_complete(
                handle_tool("sdd_review", {
                    "project": str(tmp_path),
                    "doc_type": "brd",
                    "template": "UCR_PROMPT_BRD_PROJECT.md",
                    "document": str(doc_dir),
                    "sections": [{"section_id": "BRD-01", "title": "BRD-01", "content": "# BRD-01"}],
                })
            )

        payload = json.loads(result[0].text)
        assert payload.get("executor") is None
        assert "review_report_path" not in payload
        # No .ucx.review.md created
        review_files = list(doc_dir.glob("*.ucx.review.md"))
        assert len(review_files) == 0
