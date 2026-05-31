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


PLATFORMS_ROOT = REPO_ROOT / "platforms"


def platform_dirs() -> list[Path]:
    """Return every direct subdirectory of ``platforms/`` (sorted)."""
    return sorted(p for p in PLATFORMS_ROOT.iterdir() if p.is_dir())


def platform_version_file(platform: Path) -> Path:
    return platform / "VERSION"


def platform_framework_spec_version_file(platform: Path) -> Path:
    return platform / "FRAMEWORK_SPEC_VERSION"


def framework_version() -> str:
    """Return the bare-SemVer string from ``framework/VERSION``."""
    return (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()


LAYER_DIR_BY_NAME = {
    "BRD": FRAMEWORK / "layers" / "01_BRD",
    "PRD": FRAMEWORK / "layers" / "02_PRD",
    "EARS": FRAMEWORK / "layers" / "03_EARS",
    "BDD": FRAMEWORK / "layers" / "04_BDD",
    "ADR": FRAMEWORK / "layers" / "05_ADR",
    "SPEC": FRAMEWORK / "layers" / "06_SPEC",
    "TDD": FRAMEWORK / "layers" / "07_TDD",
    "IPLAN": FRAMEWORK / "layers" / "08_IPLAN",
}


def layer_root(name: str) -> Path:
    """Return the framework/layers/NN_<X>/ directory for an artifact name."""
    return LAYER_DIR_BY_NAME[name]


def template_path(name: str) -> Path:
    """Return the canonical TYPE-TEMPLATE.yaml for an artifact name."""
    return layer_root(name) / f"{name}-TEMPLATE.yaml"


def plugin_bundle_root() -> Path:
    """Return the claude-code-plugin bundle root."""
    return PLATFORMS_ROOT / "claude-code-plugin"


def skill_dirs() -> list[Path]:
    """Return sorted list of every SKILL.md-bearing skill directory in the plugin."""
    return sorted((plugin_bundle_root() / "skills").iterdir())
