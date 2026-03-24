"""Unit tests for ucx.agents.workflow."""

from __future__ import annotations

import pytest

from ucx.agents.stages import Stage
from ucx.agents.workflow import WorkflowEngine


class TestWorkflowEngineNextStep:
    def test_next_step_from_created(self) -> None:
        engine = WorkflowEngine(Stage.CREATED)
        assert engine.next_step("brd") == "brd_validate"

    def test_next_step_from_validated(self) -> None:
        engine = WorkflowEngine(Stage.VALIDATED)
        assert engine.next_step("brd") == "brd_review"

    def test_next_step_from_reviewed(self) -> None:
        engine = WorkflowEngine(Stage.REVIEWED)
        assert engine.next_step("prd") == "prd_remediate"

    def test_next_step_from_remediated(self) -> None:
        engine = WorkflowEngine(Stage.REMEDIATED)
        # re-validate after applying remediations
        assert engine.next_step("prd") == "prd_validate"

    def test_next_step_from_complete(self) -> None:
        engine = WorkflowEngine(Stage.COMPLETE)
        result = engine.next_step("brd")
        assert "complete" in result.lower()

    def test_next_step_prefix_is_injected(self) -> None:
        engine = WorkflowEngine(Stage.CREATED)
        for prefix in ["brd", "prd", "ears", "adr", "sys", "req", "ctr"]:
            assert engine.next_step(prefix).startswith(prefix)


class TestWorkflowEngineStage:
    def test_stage_property_returns_current(self) -> None:
        engine = WorkflowEngine(Stage.REVIEWED)
        assert engine.stage == Stage.REVIEWED


class TestWorkflowEngineAssertCanProceed:
    def test_valid_transition_does_not_raise(self) -> None:
        engine = WorkflowEngine(Stage.CREATED)
        engine.assert_can_proceed(Stage.VALIDATED)  # should not raise

    def test_invalid_transition_raises_value_error(self) -> None:
        engine = WorkflowEngine(Stage.CREATED)
        with pytest.raises(ValueError, match="Stage transition"):
            engine.assert_can_proceed(Stage.COMPLETE)

    def test_error_message_includes_stage_names(self) -> None:
        # COMPLETE → CREATED is always an invalid transition
        engine = WorkflowEngine(Stage.COMPLETE)
        with pytest.raises(ValueError) as exc_info:
            engine.assert_can_proceed(Stage.CREATED)
        assert "complete" in str(exc_info.value).lower()
