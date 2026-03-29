from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import re


CANONICAL_SCAFFOLD_MAPPINGS: tuple[tuple[Path, Path], ...] = (
    (Path("skills/personas"), Path("docs/UCX/skills/personas")),
    (Path("skills/layer_aliases"), Path("docs/UCX/skills/layer_aliases")),
    (Path("prompts/templates/creation"), Path("docs/UCX/prompts/templates/creation")),
    (Path("prompts/templates/review"), Path("docs/UCX/prompts/templates/review")),
    (Path("prompts/templates/remediation"), Path("docs/UCX/prompts/templates/remediation")),
    (Path("templates"), Path("docs/UCX/templates")),
)


LAYER_DIR_PATTERN = re.compile(r"^\d{2}_[A-Z]+$")


@dataclass(frozen=True)
class InitScaffoldResult:
    project_root: Path
    created_paths: tuple[str, ...]
    skipped_paths: tuple[str, ...]

    @property
    def created_count(self) -> int:
        return len(self.created_paths)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped_paths)


def _default_canonical_root() -> Path:
    # Resolve repository root from mcp/src/mcp_server/skills/scaffold.py
    return Path(__file__).resolve().parents[3]


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _default_ssd_root() -> Path:
    return _default_repo_root() / "ai_dev_ssd_flow"


def _copy_tree_no_overwrite(source_root: Path, destination_root: Path) -> tuple[list[str], list[str]]:
    created: list[str] = []
    skipped: list[str] = []

    for source_file in sorted(path for path in source_root.rglob("*") if path.is_file()):
        relative = source_file.relative_to(source_root)
        target_file = destination_root / relative
        if target_file.exists():
            skipped.append(str(target_file))
            continue

        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target_file)
        created.append(str(target_file))

    return created, skipped


def _copy_ssd_layer_assets_no_overwrite(*, ssd_root: Path, destination_root: Path) -> tuple[list[str], list[str]]:
    created: list[str] = []
    skipped: list[str] = []

    for layer_dir in sorted(path for path in ssd_root.iterdir() if path.is_dir() and LAYER_DIR_PATTERN.match(path.name)):
        layer_destination = destination_root / layer_dir.name
        layer_destination.mkdir(parents=True, exist_ok=True)

        for source_file in sorted(path for path in layer_dir.iterdir() if path.is_file()):
            if "-TEMPLATE" not in source_file.name and not source_file.name.endswith("_MVP_SCHEMA.yaml"):
                continue

            target_file = layer_destination / source_file.name
            if target_file.exists():
                skipped.append(str(target_file))
                continue

            shutil.copy2(source_file, target_file)
            created.append(str(target_file))

    return created, skipped


def scaffold_project_ucx(
    *,
    project_root: Path,
    canonical_root: Path | None = None,
    ssd_root: Path | None = None,
) -> InitScaffoldResult:
    source_root = canonical_root or _default_canonical_root()
    authoritative_ssd_root = ssd_root or _default_ssd_root()
    created_paths: list[str] = []
    skipped_paths: list[str] = []

    for source_relative, destination_relative in CANONICAL_SCAFFOLD_MAPPINGS:
        source_dir = source_root / source_relative
        if not source_dir.exists():
            raise FileNotFoundError(f"Missing canonical scaffold source: {source_dir}")

        destination_dir = project_root / destination_relative
        destination_dir.mkdir(parents=True, exist_ok=True)
        created, skipped = _copy_tree_no_overwrite(source_dir, destination_dir)
        created_paths.extend(created)
        skipped_paths.extend(skipped)

    if not authoritative_ssd_root.exists():
        raise FileNotFoundError(f"Missing authoritative SSD source: {authoritative_ssd_root}")

    ssd_created, ssd_skipped = _copy_ssd_layer_assets_no_overwrite(
        ssd_root=authoritative_ssd_root,
        destination_root=project_root / "docs/UCX/templates/layers",
    )
    created_paths.extend(ssd_created)
    skipped_paths.extend(ssd_skipped)

    return InitScaffoldResult(
        project_root=project_root,
        created_paths=tuple(created_paths),
        skipped_paths=tuple(skipped_paths),
    )
