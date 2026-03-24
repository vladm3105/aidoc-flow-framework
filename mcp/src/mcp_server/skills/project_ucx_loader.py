from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REQUIRED_UCX_PATHS = (
    Path("docs/UCX/skills/personas"),
    Path("docs/UCX/skills/layer_aliases"),
    Path("docs/UCX/prompts/templates/creation"),
    Path("docs/UCX/prompts/templates/review"),
    Path("docs/UCX/prompts/templates/remediation"),
    Path("docs/UCX/templates"),
    Path("docs/UCX/templates/layers"),
)


@dataclass(frozen=True)
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



def _raise_missing(project_root: Path, missing_paths: list[Path]) -> None:
    raise ProjectSkillsNotFound(
        project_root=project_root,
        missing_paths=tuple(str(path) for path in missing_paths),
        resolution=f"Run mcp init --project {project_root} to create project-specific files.",
    )



def validate_project_ucx_root(project_root: Path) -> Path:
    missing_paths = [project_root / relative for relative in REQUIRED_UCX_PATHS if not (project_root / relative).exists()]
    if missing_paths:
        _raise_missing(project_root, missing_paths)
    return project_root / "docs/UCX"



def load_project_persona_file(*, project_root: Path, persona: str) -> str:
    validate_project_ucx_root(project_root)
    path = project_root / "docs/UCX/skills/personas" / f"{persona}.md"
    if not path.exists():
        _raise_missing(project_root, [path])
    return path.read_text(encoding="utf-8")



def load_project_prompt_template(*, project_root: Path, phase: str, template_name: str) -> str:
    validate_project_ucx_root(project_root)
    path = project_root / "docs/UCX/prompts/templates" / phase / template_name
    if not path.exists():
        _raise_missing(project_root, [path])
    return path.read_text(encoding="utf-8")


def load_project_document_template(*, project_root: Path, template_name: str) -> str:
    validate_project_ucx_root(project_root)
    path = project_root / "docs/UCX/templates" / template_name
    if not path.exists():
        _raise_missing(project_root, [path])
    return path.read_text(encoding="utf-8")


def load_project_layer_assets(*, project_root: Path, layer: str) -> dict[str, str]:
    validate_project_ucx_root(project_root)
    layer_root = project_root / "docs/UCX/templates/layers" / layer
    if not layer_root.exists():
        _raise_missing(project_root, [layer_root])

    assets: dict[str, str] = {}
    for file_path in sorted(path for path in layer_root.iterdir() if path.is_file()):
        if file_path.name == "README.md" or "-MVP-TEMPLATE" in file_path.name:
            assets[file_path.name] = file_path.read_text(encoding="utf-8")

    if not assets:
        _raise_missing(project_root, [layer_root])
    return assets
