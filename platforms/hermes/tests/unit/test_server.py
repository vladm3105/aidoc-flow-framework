"""Tests for MCP transport layer: tool registry, handlers, executor registry, pipeline."""

from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
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
from mcp_server.executor.contracts import ExecutorResult


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
                      "sdd_remediate"]
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
        assert "validation_report" in props

    def test_sdd_create_has_target_param(self):
        create_tool = next(t for t in TOOLS if t.name == "sdd_create")
        assert "target" in create_tool.inputSchema["required"]

    def test_sdd_remediate_executor_semantics(self):
        remediate_tool = next(t for t in TOOLS if t.name == "sdd_remediate")
        props = remediate_tool.inputSchema["properties"]
        assert "executor" in props
        assert props["fix"]["default"] is True


# ── Executor registry tests ─────────────────────────────────────────────────


class TestExecutorRegistry:
    def test_builtin_executors_registered(self):
        executors = list_executors()
        names = {e.name for e in executors}
        assert "api/gpt-4o" in names
        assert "api/claude-sonnet" in names
        assert "api/gemini-pro" in names
        assert "api/openrouter" in names
        assert "api/deepseek-v4-pro" in names
        assert "api/ollama-qwen-coder" in names

    def test_builtin_api_stubs_registered(self):
        executors = list_executors()
        names = {e.name for e in executors}
        assert "api/gpt-4o" in names
        assert "api/claude-sonnet" in names
        assert "api/gemini-pro" in names

    def test_get_known_executor(self):
        config = get_executor("api/gpt-4o")
        assert config.name == "api/gpt-4o"
        assert config.executor_type == ExecutorType.API
        assert config.model == "openai/openai-gpt-4o"
        assert config.api_base == "http://localhost:4001/v1"
        assert config.api_key_env == "LITELLM_MASTER_KEY"

    def test_get_unknown_executor_raises(self):
        with pytest.raises(KeyError, match="Unknown executor"):
            get_executor("nonexistent-agent")

    def test_register_custom_executor(self):
        config = ExecutorConfig(
            name="test-agent",
            executor_type=ExecutorType.API,
            model="openai/gpt-4o-mini",
        )
        register_executor(config)
        retrieved = get_executor("test-agent")
        assert retrieved.model == "openai/gpt-4o-mini"
        # Cleanup
        remove_executor("test-agent")

    def test_remove_executor(self):
        config = ExecutorConfig(
            name="temp-agent",
            executor_type=ExecutorType.API,
            model="openai/gpt-4o-mini",
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
        assert config.model == "openai/openai-gpt-4o"

    def test_openrouter_executor_registered(self):
        config = get_executor("api/openrouter")
        assert config.executor_type == ExecutorType.API
        assert config.model == "openai/openrouter-claude-3.5-sonnet"
        assert config.api_base == "http://localhost:4001/v1"
        assert config.api_key_env == "LITELLM_MASTER_KEY"

    def test_openrouter_executor_is_active(self):
        config = get_executor("api/openrouter")
        assert config.status == "active"

    def test_load_config_file_old_array_format(self, tmp_path):
        from mcp_server.executor.registry import load_config_file
        config_file = tmp_path / "executors.json"
        config_file.write_text(
            json.dumps([{"name": "test-old", "executor_type": "api", "model": "openai/gpt-4o-mini"}]),
            encoding="utf-8",
        )
        count = load_config_file(config_file)
        assert count == 1
        cfg = get_executor("test-old")
        assert cfg.model == "openai/gpt-4o-mini"
        remove_executor("test-old")

    def test_load_config_file_new_object_format(self, tmp_path):
        from mcp_server.executor.registry import load_config_file
        import mcp_server.project_context as pc
        old_config = pc._config_default_project
        config_file = tmp_path / "executors.json"
        config_file.write_text(
            json.dumps({
                "default_project": str(tmp_path),
                "executors": [{"name": "test-new", "executor_type": "api", "model": "openai/gpt-4o-mini"}],
            }),
            encoding="utf-8",
        )
        count = load_config_file(config_file)
        assert count == 1
        assert pc._config_default_project == tmp_path
        cfg = get_executor("test-new")
        assert cfg.model == "openai/gpt-4o-mini"
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

    def test_load_config_file_skips_legacy_cli_executor(self, tmp_path):
        from mcp_server.executor.registry import load_config_file

        config_file = tmp_path / "executors.json"
        config_file.write_text(
            json.dumps([{"name": "legacy-cli", "executor_type": "cli", "command": "claude"}]),
            encoding="utf-8",
        )
        count = load_config_file(config_file)
        assert count == 0
        with pytest.raises(KeyError):
            get_executor("legacy-cli")


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
        assert "api/gpt-4o" in names

    def test_sdd_register_executor_via_handler(self):
        result = asyncio.get_event_loop().run_until_complete(
            handle_tool("sdd_register_executor", {
                "name": "handler-test-agent",
                "executor_type": "api",
                "model": "openai/gpt-4o-mini",
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

    def test_sdd_init_rejects_update_mappings_without_update(self, tmp_path):
        result = asyncio.get_event_loop().run_until_complete(
            handle_tool(
                "sdd_init",
                {
                    "project": str(tmp_path),
                    "update_mappings": True,
                },
            )
        )
        payload = json.loads(result[0].text)
        assert payload.get("passed") is False
        assert payload.get("error_code") == "InvalidInitParams"


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
    """Verify review output remains deterministic without executor writes."""

    def test_review_report_not_saved_when_executor_provided(self, tmp_path):
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
            executor_name="api/gpt-4o",
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
            ) as run_executor_mock,
        ):
            result = asyncio.get_event_loop().run_until_complete(
                handle_tool("sdd_review", {
                    "project": str(tmp_path),
                    "doc_type": "brd",
                    "template": "UCR_PROMPT_BRD_PROJECT.md",
                    "document": str(doc_dir),
                    "executor": "api/gpt-4o",
                    "sections": [{"section_id": "BRD-01", "title": "BRD-01", "content": "# BRD-01"}],
                })
            )

        payload = json.loads(result[0].text)
        assert payload.get("review_report_path") is None
        assert payload.get("executor") == "api/gpt-4o"
        assert payload.get("passed") is True
        assert "REM-P0-001" in str(payload.get("output", ""))
        run_executor_mock.assert_awaited_once()

        # No .ucx.review.md created even when executor parameter is provided.
        review_files = list(doc_dir.glob("*.ucx.review.md"))
        assert len(review_files) == 0


class TestReviewSagaSchema:
    def test_saga_review_paths_preserved_without_prompt_artifacts(self, tmp_path):
        from mcp_server.review.saga_orchestrator import SagaReviewResult

        branch_summary = tmp_path / "BRD-00_validation-fixed_saga_branch_summary_v001.json"
        reducer_summary = tmp_path / "BRD-00_validation-fixed_saga_reducer_summary_v001.json"
        synthesis_summary = tmp_path / "BRD-00_validation-fixed_saga_synthesis_summary_v001.json"
        journal = tmp_path / "BRD-00_validation-fixed_saga_journal_v001.json"
        for p in (branch_summary, reducer_summary, synthesis_summary, journal):
            p.write_text("{}", encoding="utf-8")

        fake_saga = SagaReviewResult(
            review_mode="saga_parallel",
            review_run_id="run-001",
            saga_status="CLOSED",
            journal_path=journal,
            prompt_path=None,
            sidecar_path=None,
            inspection_path=None,
            branch_summary={"total": 2, "completed": 2, "failed": 0},
            branch_summary_path=branch_summary,
            compensation_summary={"count": 0},
            reducer_summary={"reduced_count": 1},
            reducer_summary_path=reducer_summary,
            synthesis_summary_path=synthesis_summary,
            passed=True,
        )

        fake_exec_result = ExecutorResult(
            stdout="saga review output",
            stderr="",
            exit_code=0,
            executor_name="api/gpt-4o",
        )

        with (
            patch(
                "mcp_server.review.run_project_review_build_saga",
                return_value=fake_saga,
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
                    "review_mode": "saga_parallel",
                    "executor": "api/gpt-4o",
                    "sections": [{"section_id": "1.0", "title": "Architecture", "content": "text"}],
                })
            )

        payload = json.loads(result[0].text)
        assert payload["review_mode"] == "saga_parallel"
        assert payload["saga_status"] == "CLOSED"
        assert payload["branch_summary_path"] == str(branch_summary)
        assert payload["reducer_summary_path"] == str(reducer_summary)
        assert payload["synthesis_summary_path"] == str(synthesis_summary)
        assert payload["prompt_path"] is None
        assert payload["sidecar_path"] is None
        assert payload["inspection_path"] is None

    def test_saga_review_passes_document_path_to_orchestrator(self, tmp_path):
        from mcp_server.review.saga_orchestrator import SagaReviewResult

        doc_dir = tmp_path / "docs" / "01_BRD" / "BRD-01_platform"
        doc_dir.mkdir(parents=True)
        (doc_dir / "BRD-01_platform.md").write_text("# BRD-01", encoding="utf-8")

        branch_summary = tmp_path / "BRD-01_validation-fixed_saga_branch_summary_v001.json"
        journal = tmp_path / "BRD-01_validation-fixed_saga_journal_v001.json"
        for p in (branch_summary, journal):
            p.write_text("{}", encoding="utf-8")

        fake_saga = SagaReviewResult(
            review_mode="saga_parallel",
            review_run_id="run-002",
            saga_status="CLOSED",
            journal_path=journal,
            prompt_path=None,
            sidecar_path=None,
            inspection_path=None,
            branch_summary={"total": 1, "completed": 1, "failed": 0},
            branch_summary_path=branch_summary,
            compensation_summary={"count": 0},
            reducer_summary={"reduced_count": 1},
            reducer_summary_path=None,
            synthesis_summary_path=None,
            passed=True,
        )

        fake_exec_result = ExecutorResult(
            stdout="saga review output",
            stderr="",
            exit_code=0,
            executor_name="api/gpt-4o",
        )

        with (
            patch(
                "mcp_server.review.run_project_review_build_saga",
                return_value=fake_saga,
            ) as saga_mock,
            patch(
                "mcp_server.tool_registry.run_executor",
                new_callable=AsyncMock,
                return_value=fake_exec_result,
            ),
        ):
            _ = asyncio.get_event_loop().run_until_complete(
                handle_tool("sdd_review", {
                    "project": str(tmp_path),
                    "doc_type": "brd",
                    "template": "UCR_PROMPT_BRD_PROJECT.md",
                    "review_mode": "saga_parallel",
                    "executor": "api/gpt-4o",
                    "document": str(doc_dir),
                    "sections": [{"section_id": "1.0", "title": "Architecture", "content": "text"}],
                })
            )

        called_kwargs = saga_mock.call_args.kwargs
        assert str(called_kwargs.get("document_path")) == str(doc_dir)

    def test_saga_review_returns_reduced_findings_without_second_executor_call(self, tmp_path):
        from mcp_server.review.saga_orchestrator import SagaReviewResult

        branch_summary = tmp_path / "BRD-00_validation-fixed_saga_branch_summary_v001.json"
        reducer_summary = tmp_path / "BRD-00_validation-fixed_saga_reducer_summary_v001.json"
        synthesis_summary = tmp_path / "BRD-00_validation-fixed_saga_synthesis_summary_v001.json"
        journal = tmp_path / "BRD-00_validation-fixed_saga_journal_v001.json"
        for p in (branch_summary, reducer_summary, synthesis_summary, journal):
            p.write_text("{}", encoding="utf-8")

        fake_saga = SagaReviewResult(
            review_mode="saga_parallel",
            review_run_id="run-003",
            saga_status="CLOSED",
            journal_path=journal,
            prompt_path=None,
            sidecar_path=None,
            inspection_path=None,
            branch_summary={"total": 2, "completed": 2, "failed": 0},
            branch_summary_path=branch_summary,
            compensation_summary={"count": 0},
            reducer_summary={"reduced_count": 1},
            reducer_summary_path=reducer_summary,
            synthesis_summary_path=synthesis_summary,
            passed=True,
            reduced_findings=[
                {
                    "finding_id": "P1-deadbeef00",
                    "action_id": "ACT-deadbeef0000",
                    "priority": "P1",
                    "category": "quality",
                    "personas": ["architect"],
                    "message": "Use deterministic IDs",
                    "target_layer": "spec",
                    "recommended_action": "Keep reducer contract",
                    "provenance": [{"branch_id": "b1", "persona": "architect"}],
                    "content_hash": "deadbeef",
                }
            ],
        )

        with (
            patch(
                "mcp_server.review.run_project_review_build_saga",
                return_value=fake_saga,
            ),
            patch(
                "mcp_server.tool_registry.run_executor",
                new_callable=AsyncMock,
            ) as run_executor_mock,
        ):
            result = asyncio.get_event_loop().run_until_complete(
                handle_tool("sdd_review", {
                    "project": str(tmp_path),
                    "doc_type": "brd",
                    "template": "UCR_PROMPT_BRD_PROJECT.md",
                    "review_mode": "saga_parallel",
                    "executor": "api/gpt-4o",
                    "sections": [{"section_id": "1.0", "title": "Architecture", "content": "text"}],
                })
            )

        payload = json.loads(result[0].text)
        assert payload.get("passed") is True
        assert payload.get("exit_code") == 0
        assert "reduced_findings" in json.loads(payload.get("output", "{}"))
        run_executor_mock.assert_not_awaited()


class TestRemediateExecutorRequired:
    def test_sdd_remediate_uses_default_executor_when_missing(self, tmp_path):
        doc_dir = tmp_path / "docs" / "01_BRD" / "BRD-01_platform"
        doc_dir.mkdir(parents=True)
        (doc_dir / "BRD-01_platform.md").write_text("# BRD-01", encoding="utf-8")

        with (
            patch("mcp_server.tool_registry.get_executor") as get_exec_mock,
            patch("mcp_server.remediation.run_remediation_build") as rem_build_mock,
            patch("mcp_server.remediation.run_remediate_fix_build") as rem_fix_mock,
        ):
            get_exec_mock.return_value = ExecutorConfig(
                name="api/claude-sonnet",
                executor_type=ExecutorType.API,
                model="claude-sonnet-4-20250514",
                api_key_env="ANTHROPIC_API_KEY",
            )
            rem_build_mock.return_value = SimpleNamespace(
                report_json="{}",
                report_path=tmp_path / "report.json",
            )
            rem_fix_mock.side_effect = ValueError("skip")

            result = asyncio.get_event_loop().run_until_complete(
                handle_tool("sdd_remediate", {
                    "project": str(tmp_path),
                    "doc_type": "brd",
                    "layer": "01_BRD",
                    "document": str(doc_dir),
                })
            )

        payload = json.loads(result[0].text)
        assert payload.get("error_code") == "RemediationBuildError"
        get_exec_mock.assert_called_once()
        called_name = get_exec_mock.call_args.args[0]
        assert called_name == "api/claude-sonnet"

    def test_sdd_remediate_rejects_cli_executor(self, tmp_path):
        doc_dir = tmp_path / "docs" / "01_BRD" / "BRD-01_platform"
        doc_dir.mkdir(parents=True)
        (doc_dir / "BRD-01_platform.md").write_text("# BRD-01", encoding="utf-8")

        result = asyncio.get_event_loop().run_until_complete(
            handle_tool("sdd_remediate", {
                "project": str(tmp_path),
                "doc_type": "brd",
                "layer": "01_BRD",
                "document": str(doc_dir),
                "executor": "claude",
            })
        )
        payload = json.loads(result[0].text)
        assert payload.get("passed") is False
        assert payload.get("error_code") == "UnknownExecutor"

    def test_sdd_review_requires_executor(self, tmp_path):
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
        assert payload.get("passed") is False
        assert payload.get("error_code") == "ExecutorRequired"

    def test_sdd_review_rejects_cli_executor(self, tmp_path):
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
                    "executor": "claude",
                    "sections": [{"section_id": "BRD-01", "title": "BRD-01", "content": "# BRD-01"}],
                })
            )

        payload = json.loads(result[0].text)
        assert payload.get("passed") is False
        assert payload.get("error_code") == "UnknownExecutor"

    def test_review_report_not_saved_with_api_executor(self, tmp_path):
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
        fake_exec_result = ExecutorResult(
            stdout="review output",
            stderr="",
            exit_code=0,
            executor_name="api/gpt-4o",
        )

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
                    "executor": "api/gpt-4o",
                    "sections": [{"section_id": "BRD-01", "title": "BRD-01", "content": "# BRD-01"}],
                })
            )

        payload = json.loads(result[0].text)
        assert payload.get("passed") is True
        assert payload.get("executor") == "api/gpt-4o"
        # No .ucx.review.md created
        review_files = list(doc_dir.glob("*.ucx.review.md"))
        assert len(review_files) == 0
