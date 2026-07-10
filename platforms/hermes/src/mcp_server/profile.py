"""Project adaptation profile — `.aidoc/profile.yaml` runtime consumption.

The framework spec declares `.aidoc/profile.yaml` as the single adaptation input
(`framework/governance/ADAPTATION_SURFACE.yaml`). This module reads it and exposes
the closed set of 6 knobs, with the spec-mandated graceful fallback on
missing-file / missing-field / malformed-value.

PR-ADAPT (HERMES-REVIEW-001) scope — *minimum honest consumption*:
  - the profile is read and all 6 knobs are parsed + validated here;
  - `review_mode` is reconciled to Hermes's internal vocabulary (see
    ``REVIEW_MODE_ALIAS``);
  - the prompt-injectable authoring knobs (`glossary`, `section_toggles`,
    `active_layers`) are surfaced into the creation prompt via `context_builder`.

Deferred (see HERMES-BACKLOG H-16): structural *enforcement* of `active_layers`
(layer skipping) / `section_toggles` (template mutation), the `audit_threshold`
gate (its raise-only semantics need reconciling with
`profile_contracts.resolve_threshold_precedence`'s override semantics), and
`quality_loop_max_iterations` (Hermes has no outer review→remediate loop yet — H-7).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

# Spec review_mode vocabulary (ADAPTATION_SURFACE.yaml) → Hermes internal mode.
REVIEW_MODE_ALIAS: dict[str, str] = {
    "team": "saga_parallel",
    "single_pass": "prompt_only",
}

_DEFAULT_REVIEW_MODE = "team"
_DEFAULT_QUALITY_LOOP_MAX_ITERATIONS = 3
_QUALITY_LOOP_RANGE = range(1, 11)  # 1..10 inclusive


@dataclass(frozen=True)
class ProjectProfile:
    """Parsed `.aidoc/profile.yaml` knobs (defaults applied). Never weakens a gate."""

    active_layers: tuple[str, ...] | None = None  # None → all layers active
    section_toggles: dict = field(default_factory=dict)  # map[layer, map[section, bool]]
    audit_threshold: dict = field(default_factory=dict)  # map[layer, int] (raise-only)
    glossary: dict = field(default_factory=dict)  # map[str, str]
    review_mode: str = _DEFAULT_REVIEW_MODE  # "team" | "single_pass" (spec default: team)
    review_mode_declared: bool = False  # True only if the file set review_mode explicitly
    quality_loop_max_iterations: int = _DEFAULT_QUALITY_LOOP_MAX_ITERATIONS
    source_path: Path | None = None  # where it loaded from (None → all defaults)

    @property
    def hermes_review_mode(self) -> str:
        """`review_mode` mapped to Hermes's internal vocabulary (saga_parallel/prompt_only)."""
        return REVIEW_MODE_ALIAS.get(self.review_mode, "saga_parallel")


def _coerce_review_mode(value: object) -> str:
    if isinstance(value, str) and value in REVIEW_MODE_ALIAS:
        return value
    if value is not None:
        logger.warning(
            "profile.review_mode %r invalid — using default %r", value, _DEFAULT_REVIEW_MODE
        )
    return _DEFAULT_REVIEW_MODE


def _coerce_quality_loop(value: object) -> int:
    if isinstance(value, bool):  # bool is an int subclass — reject explicitly
        value = None
    if isinstance(value, int) and value in _QUALITY_LOOP_RANGE:
        return value
    if value is not None:
        logger.warning(
            "profile.quality_loop_max_iterations %r out of range 1-10 — using default %d",
            value,
            _DEFAULT_QUALITY_LOOP_MAX_ITERATIONS,
        )
    return _DEFAULT_QUALITY_LOOP_MAX_ITERATIONS


def _coerce_active_layers(value: object) -> tuple[str, ...] | None:
    if value is None:
        return None
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return tuple(value)
    logger.warning("profile.active_layers %r malformed — treating as all layers active", value)
    return None


def _coerce_str_map(name: str, value: object) -> dict:
    if isinstance(value, dict):
        return value
    if value is not None:
        logger.warning("profile.%s %r is not a mapping — ignoring", name, value)
    return {}


def load_project_profile(project_root: Path) -> ProjectProfile:
    """Load `<project_root>/.aidoc/profile.yaml`.

    Missing file / unreadable / malformed YAML / non-mapping document → all
    defaults (spec-mandated graceful fallback). Each knob falls back to its
    default independently when absent or malformed.
    """
    profile_path = project_root / ".aidoc" / "profile.yaml"
    if not profile_path.is_file():
        return ProjectProfile()

    try:
        # UnicodeDecodeError (a ValueError) is raised by read_text on a non-UTF-8
        # file BEFORE YAML sees the bytes — it must fall back, not crash the tool.
        raw = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        logger.warning("Failed to read/parse %s (%s) — using default profile", profile_path, exc)
        return ProjectProfile()

    if not isinstance(raw, dict):
        logger.warning("%s is not a YAML mapping — using default profile", profile_path)
        return ProjectProfile()

    return ProjectProfile(
        active_layers=_coerce_active_layers(raw.get("active_layers")),
        section_toggles=_coerce_str_map("section_toggles", raw.get("section_toggles")),
        audit_threshold=_coerce_str_map("audit_threshold", raw.get("audit_threshold")),
        glossary=_coerce_str_map("glossary", raw.get("glossary")),
        review_mode=_coerce_review_mode(raw.get("review_mode")),
        # "declared" only when the file set a *valid* review_mode value.
        review_mode_declared=raw.get("review_mode") in REVIEW_MODE_ALIAS,
        quality_loop_max_iterations=_coerce_quality_loop(raw.get("quality_loop_max_iterations")),
        source_path=profile_path,
    )
