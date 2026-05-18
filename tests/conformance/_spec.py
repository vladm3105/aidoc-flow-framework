"""Helpers for the framework conformance suite.

Locates the ``framework/`` spec tree and loads its machine-readable core so
the test modules can assert against a single source of truth.
"""

from __future__ import annotations

from pathlib import Path

import yaml

# tests/conformance/_spec.py  ->  parents[2] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[2]
FRAMEWORK = REPO_ROOT / "framework"
REGISTRY_PATH = FRAMEWORK / "registry" / "LAYER_REGISTRY.yaml"

# The 8 SDD document layers, in canonical order.
ARTIFACTS = ["BRD", "PRD", "EARS", "BDD", "ADR", "SPEC", "TDD", "IPLAN"]


def load_registry() -> dict:
    """Parse and return the layer registry."""
    with REGISTRY_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def registry_layers() -> list[dict]:
    """Return the registry's layer entries sorted by layer number."""
    return sorted(load_registry()["layers"], key=lambda layer: layer["number"])


def framework_files() -> list[Path]:
    """Return every file under ``framework/`` (sorted, for stable output)."""
    return sorted(p for p in FRAMEWORK.rglob("*") if p.is_file())
