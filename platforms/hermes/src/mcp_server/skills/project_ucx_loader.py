from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

# Mtime-based cache for persona_mappings.yaml (C-1 fix)
_persona_mapping_cache: dict[str, tuple[float, dict[str, Any]]] = {}


def resolve_ucx_root(project_root: Path) -> Path:
    """Resolve UCX directory, supporting both new and legacy locations."""
    new_path = project_root / "UCX"
    if new_path.exists():
        return new_path
    legacy_path = project_root / "docs" / "UCX"
    if legacy_path.exists():
        return legacy_path
    return new_path  # default to new location for scaffolding


_REQUIRED_SUBDIRS: tuple[Path, ...] = (
    Path("skills/personas"),
    Path("skills/layer_aliases"),
    Path("prompts/templates/creation"),
    Path("prompts/templates/review"),
    Path("prompts/templates/remediation"),
    Path("templates"),
    Path("templates/layers"),
)

_REQUIRED_FILES: tuple[Path, ...] = (Path("skills/persona_mappings.yaml"),)


@dataclass
class ProjectSkillsNotFound(FileNotFoundError):
    project_root: Path
    missing_paths: tuple[str, ...]
    resolution: str
    error_code: str = "ProjectSkillsNotFound"

    def to_payload(self) -> dict[str, object]:
        return {
            "error_code": self.error_code,
            "project_root": str(self.project_root),
            "missing_paths": list(self.missing_paths),
            "resolution": self.resolution,
        }

    def __str__(self) -> str:
        return f"{self.error_code}: {', '.join(self.missing_paths)}. {self.resolution}"


class PersonaMappingError(ValueError):
    """Raised when persona_mappings.yaml is invalid or missing required entries."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"PersonaMappingError: {self.message}"


def _raise_missing(project_root: Path, missing_paths: list[Path]) -> None:
    raise ProjectSkillsNotFound(
        project_root=project_root,
        missing_paths=tuple(str(path) for path in missing_paths),
        resolution=f"Run sdd_init (MCP) or mcp init --project {project_root} (CLI) to create project-specific files.",
    )


def validate_project_ucx_root(project_root: Path) -> Path:
    ucx_root = resolve_ucx_root(project_root)
    missing_paths = [
        ucx_root / relative for relative in _REQUIRED_SUBDIRS if not (ucx_root / relative).exists()
    ]
    missing_paths.extend(
        ucx_root / relative for relative in _REQUIRED_FILES if not (ucx_root / relative).exists()
    )
    if missing_paths:
        _raise_missing(project_root, missing_paths)
    return ucx_root


def load_project_persona_file(*, project_root: Path, persona: str) -> str:
    ucx_root = validate_project_ucx_root(project_root)
    path = ucx_root / "skills/personas" / f"{persona}.md"
    if not path.exists():
        _raise_missing(project_root, [path])
    return path.read_text(encoding="utf-8")


def load_project_prompt_template(*, project_root: Path, phase: str, template_name: str) -> str:
    ucx_root = validate_project_ucx_root(project_root)
    path = ucx_root / "prompts/templates" / phase / template_name
    if not path.exists():
        _raise_missing(project_root, [path])
    return path.read_text(encoding="utf-8")


def load_project_document_template(*, project_root: Path, template_name: str) -> str:
    ucx_root = validate_project_ucx_root(project_root)
    path = ucx_root / "templates" / template_name
    if not path.exists():
        _raise_missing(project_root, [path])
    return path.read_text(encoding="utf-8")


def load_project_layer_assets(*, project_root: Path, layer: str) -> dict[str, str]:
    ucx_root = validate_project_ucx_root(project_root)
    layer_root = ucx_root / "templates/layers" / layer
    if not layer_root.exists():
        _raise_missing(project_root, [layer_root])

    assets: dict[str, str] = {}
    for file_path in sorted(path for path in layer_root.iterdir() if path.is_file()):
        if "-TEMPLATE" in file_path.name or file_path.name.endswith("_MVP_SCHEMA.yaml"):
            assets[file_path.name] = file_path.read_text(encoding="utf-8")

    if not assets:
        _raise_missing(project_root, [layer_root])
    return assets


def _validate_persona_mapping(mapping: dict, project_root: Path) -> None:
    """Validate persona_mappings.yaml structure and persona name references."""
    if "version" not in mapping:
        raise PersonaMappingError("Missing 'version' key in persona_mappings.yaml")

    ucx_root = validate_project_ucx_root(project_root)
    for phase in ("creation", "review", "remediation"):
        phase_map = mapping.get(phase)
        if not phase_map:
            continue
        for doc_type, config in phase_map.items():
            if not isinstance(config, dict) or "personas" not in config:
                raise PersonaMappingError(f"Entry '{phase}.{doc_type}' missing 'personas' list")
            personas = config["personas"]
            if not isinstance(personas, list) or not personas:
                raise PersonaMappingError(
                    f"Entry '{phase}.{doc_type}.personas' must be a non-empty list"
                )
            for name in personas:
                persona_path = ucx_root / "skills/personas" / f"{name}.md"
                if not persona_path.exists():
                    _raise_missing(project_root, [persona_path])


def _invalidate_persona_mapping_cache(project_root: Path) -> None:
    """Clear cache entry for a project root. Useful for testing."""
    _persona_mapping_cache.pop(str(project_root), None)


def load_persona_mapping(*, project_root: Path) -> dict:
    """Load and validate persona_mappings.yaml with mtime-based caching."""
    ucx_root = validate_project_ucx_root(project_root)
    path = ucx_root / "skills" / "persona_mappings.yaml"
    if not path.exists():
        _raise_missing(project_root, [path])

    cache_key = str(project_root)
    current_mtime = path.stat().st_mtime
    cached = _persona_mapping_cache.get(cache_key)
    if cached is not None and cached[0] == current_mtime:
        return cached[1]

    mapping = yaml.safe_load(path.read_text(encoding="utf-8"))
    _validate_persona_mapping(mapping, project_root)
    _persona_mapping_cache[cache_key] = (current_mtime, mapping)
    return mapping


def load_multi_persona_files(*, project_root: Path, personas: list[str]) -> list[tuple[str, str]]:
    """Load multiple persona .md files. Returns [(name, content), ...]."""
    return [(p, load_project_persona_file(project_root=project_root, persona=p)) for p in personas]
