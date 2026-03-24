"""Unit tests for ucx.agents.stages."""

from __future__ import annotations

import pytest

from ucx.agents.stages import Stage, TRANSITIONS, can_transition


class TestStageEnum:
    def test_all_stages_are_strings(self) -> None:
        for stage in Stage:
            assert isinstance(stage, str)

    def test_stage_values(self) -> None:
        assert Stage.CREATED == "created"
        assert Stage.VALIDATED == "validated"
        assert Stage.REVIEWED == "reviewed"
        assert Stage.REMEDIATED == "remediated"
        assert Stage.COMPLETE == "complete"

    def test_five_stages_defined(self) -> None:
        assert len(Stage) == 5


class TestTransitions:
    def test_transitions_covers_all_stages(self) -> None:
        for stage in Stage:
            assert stage in TRANSITIONS, f"{stage} missing from TRANSITIONS map"

    def test_created_can_go_to_validated(self) -> None:
        assert Stage.VALIDATED in TRANSITIONS[Stage.CREATED]

    def test_validated_can_go_to_reviewed(self) -> None:
        assert Stage.REVIEWED in TRANSITIONS[Stage.VALIDATED]

    def test_reviewed_can_go_to_remediated(self) -> None:
        assert Stage.REMEDIATED in TRANSITIONS[Stage.REVIEWED]

    def test_remediated_can_go_to_complete(self) -> None:
        assert Stage.COMPLETE in TRANSITIONS[Stage.REMEDIATED]

    def test_complete_has_no_forward_transitions(self) -> None:
        assert TRANSITIONS[Stage.COMPLETE] == []


class TestCanTransition:
    def test_valid_forward_transitions(self) -> None:
        assert can_transition(Stage.CREATED, Stage.VALIDATED)
        assert can_transition(Stage.VALIDATED, Stage.REVIEWED)
        assert can_transition(Stage.REVIEWED, Stage.REMEDIATED)
        assert can_transition(Stage.REMEDIATED, Stage.COMPLETE)

    def test_re_validate_after_fix_is_valid(self) -> None:
        # VALIDATED → CREATED means re-validate after a fix round
        assert can_transition(Stage.VALIDATED, Stage.CREATED)

    def test_re_review_after_remediation_is_valid(self) -> None:
        assert can_transition(Stage.REMEDIATED, Stage.REVIEWED)

    def test_forward_skip_is_invalid(self) -> None:
        # Cannot skip from CREATED directly to REVIEWED
        assert not can_transition(Stage.CREATED, Stage.REVIEWED)
        assert not can_transition(Stage.CREATED, Stage.REMEDIATED)
        assert not can_transition(Stage.CREATED, Stage.COMPLETE)

    def test_backward_skip_is_invalid(self) -> None:
        assert not can_transition(Stage.COMPLETE, Stage.CREATED)
        assert not can_transition(Stage.REVIEWED, Stage.CREATED)

    def test_self_transition_is_invalid(self) -> None:
        for stage in Stage:
            assert not can_transition(stage, stage)
