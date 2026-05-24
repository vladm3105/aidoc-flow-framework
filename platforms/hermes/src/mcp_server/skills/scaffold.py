from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

CANONICAL_SCAFFOLD_MAPPINGS: tuple[tuple[Path, Path], ...] = (
    (Path("skills/personas"), Path("UCX/skills/personas")),
    (Path("skills/persona_mappings.yaml"), Path("UCX/skills/persona_mappings.yaml")),
    (Path("skills/layer_aliases"), Path("UCX/skills/layer_aliases")),
    (Path("prompts/templates/creation"), Path("UCX/prompts/templates/creation")),
    (Path("prompts/templates/review"), Path("UCX/prompts/templates/review")),
    (Path("prompts/templates/remediation"), Path("UCX/prompts/templates/remediation")),
)

# Files that are project-owned after initial scaffold.
# --update will NOT overwrite these; use --update-mappings explicitly.
PROTECTED_PROJECT_FILES: frozenset[str] = frozenset(
    {
        "persona_mappings.yaml",
    }
)


LAYER_DIR_PATTERN = re.compile(r"^\d{2}_[A-Z]+$")


def _migrate_legacy_ucx(project_root: Path) -> bool:
    """If docs/UCX exists and UCX/ doesn't, move it."""
    legacy = project_root / "docs" / "UCX"
    new = project_root / "UCX"
    if legacy.exists() and not new.exists():
        shutil.move(str(legacy), str(new))
        return True
    return False


@dataclass(frozen=True)
class InitScaffoldResult:
    project_root: Path
    created_paths: tuple[str, ...]
    skipped_paths: tuple[str, ...]
    updated_paths: tuple[str, ...] = ()
    protected_paths: tuple[str, ...] = ()

    @property
    def created_count(self) -> int:
        return len(self.created_paths)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped_paths)

    @property
    def updated_count(self) -> int:
        return len(self.updated_paths)

    @property
    def protected_count(self) -> int:
        return len(self.protected_paths)


def _default_canonical_root() -> Path:
    # Platform root: <repo>/platforms/hermes/ — from
    # platforms/hermes/src/mcp_server/skills/scaffold.py via parents[3].
    return Path(__file__).resolve().parents[3]


def _default_repo_root() -> Path:
    # Repo root: <repo>/ — one level above the platform root.
    return Path(__file__).resolve().parents[5]


def _default_ssd_root() -> Path:
    return _default_repo_root() / "framework" / "layers"


def _is_content_identical(source: Path, target: Path) -> bool:
    """Return True if two files have identical byte content."""
    return source.read_bytes() == target.read_bytes()


def _is_protected(file_path: Path) -> bool:
    """Return True if file name is in the protected set."""
    return file_path.name in PROTECTED_PROJECT_FILES


def _copy_tree(
    source_root: Path,
    destination_root: Path,
    *,
    force_update: bool = False,
    force_update_mappings: bool = False,
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Copy directory tree. Returns (created, skipped, updated, protected) path lists."""
    created: list[str] = []
    skipped: list[str] = []
    updated: list[str] = []
    protected: list[str] = []

    for source_file in sorted(path for path in source_root.rglob("*") if path.is_file()):
        relative = source_file.relative_to(source_root)
        target_file = destination_root / relative
        if target_file.exists():
            is_prot = _is_protected(target_file)
            can_update = force_update_mappings if is_prot else force_update
            if can_update and not _is_content_identical(source_file, target_file):
                shutil.copy2(source_file, target_file)
                updated.append(str(target_file))
            elif force_update and is_prot and not force_update_mappings:
                protected.append(str(target_file))
            else:
                skipped.append(str(target_file))
            continue

        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target_file)
        created.append(str(target_file))

    return created, skipped, updated, protected


def _copy_ssd_layer_assets(
    *,
    ssd_root: Path,
    destination_root: Path,
    force_update: bool = False,
) -> tuple[list[str], list[str], list[str]]:
    """Copy layer template assets. Returns (created, skipped, updated) path lists.

    Layer templates are always framework-owned (no protected files).
    """
    created: list[str] = []
    skipped: list[str] = []
    updated: list[str] = []

    for layer_dir in sorted(
        path for path in ssd_root.iterdir() if path.is_dir() and LAYER_DIR_PATTERN.match(path.name)
    ):
        layer_destination = destination_root / layer_dir.name
        layer_destination.mkdir(parents=True, exist_ok=True)

        for source_file in sorted(path for path in layer_dir.iterdir() if path.is_file()):
            if "-TEMPLATE" not in source_file.name and not source_file.name.endswith(
                "_MVP_SCHEMA.yaml"
            ):
                continue

            target_file = layer_destination / source_file.name
            if target_file.exists():
                if force_update and not _is_content_identical(source_file, target_file):
                    shutil.copy2(source_file, target_file)
                    updated.append(str(target_file))
                else:
                    skipped.append(str(target_file))
                continue

            shutil.copy2(source_file, target_file)
            created.append(str(target_file))

    return created, skipped, updated


# Keep old names as aliases for backward compatibility with external callers.
def _copy_tree_no_overwrite(
    source_root: Path, destination_root: Path
) -> tuple[list[str], list[str]]:
    created, skipped, _, _ = _copy_tree(source_root, destination_root, force_update=False)
    return created, skipped


def _copy_ssd_layer_assets_no_overwrite(
    *, ssd_root: Path, destination_root: Path
) -> tuple[list[str], list[str]]:
    created, skipped, _ = _copy_ssd_layer_assets(
        ssd_root=ssd_root, destination_root=destination_root, force_update=False
    )
    return created, skipped


def scaffold_project_ucx(
    *,
    project_root: Path,
    canonical_root: Path | None = None,
    ssd_root: Path | None = None,
    force_update: bool = False,
    force_update_mappings: bool = False,
) -> InitScaffoldResult:
    _migrate_legacy_ucx(project_root)
    source_root = canonical_root or _default_canonical_root()
    authoritative_ssd_root = ssd_root or _default_ssd_root()
    created_paths: list[str] = []
    skipped_paths: list[str] = []
    updated_paths: list[str] = []
    protected_paths: list[str] = []

    for source_relative, destination_relative in CANONICAL_SCAFFOLD_MAPPINGS:
        source_path = source_root / source_relative
        if not source_path.exists():
            raise FileNotFoundError(f"Missing canonical scaffold source: {source_path}")

        destination_path = project_root / destination_relative
        if source_path.is_file():
            # Single-file scaffold mapping (e.g. persona_mappings.yaml)
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            if destination_path.exists():
                is_prot = _is_protected(destination_path)
                can_update = force_update_mappings if is_prot else force_update
                if can_update and not _is_content_identical(source_path, destination_path):
                    shutil.copy2(source_path, destination_path)
                    updated_paths.append(str(destination_path))
                elif force_update and is_prot and not force_update_mappings:
                    protected_paths.append(str(destination_path))
                else:
                    skipped_paths.append(str(destination_path))
            else:
                shutil.copy2(source_path, destination_path)
                created_paths.append(str(destination_path))
        else:
            # Directory scaffold mapping
            destination_path.mkdir(parents=True, exist_ok=True)
            created, skipped, updated, prot = _copy_tree(
                source_path,
                destination_path,
                force_update=force_update,
                force_update_mappings=force_update_mappings,
            )
            created_paths.extend(created)
            skipped_paths.extend(skipped)
            updated_paths.extend(updated)
            protected_paths.extend(prot)

    if not authoritative_ssd_root.exists():
        raise FileNotFoundError(f"Missing authoritative SSD source: {authoritative_ssd_root}")

    ssd_created, ssd_skipped, ssd_updated = _copy_ssd_layer_assets(
        ssd_root=authoritative_ssd_root,
        destination_root=project_root / "UCX/templates/layers",
        force_update=force_update,
    )
    created_paths.extend(ssd_created)
    skipped_paths.extend(ssd_skipped)
    updated_paths.extend(ssd_updated)

    return InitScaffoldResult(
        project_root=project_root,
        created_paths=tuple(created_paths),
        skipped_paths=tuple(skipped_paths),
        updated_paths=tuple(updated_paths),
        protected_paths=tuple(protected_paths),
    )
