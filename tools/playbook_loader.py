"""Layer-and-lens playbook resolver for plugin audit SKILLs.

Resolves framework/playbooks/<layer>/<lens>.md, reads the content, and
raises a documented error if the file is missing.

Stdlib-only.
"""

from __future__ import annotations

from pathlib import Path


class PlaybookMissingError(FileNotFoundError):
    """Raised when a (layer, lens) pair has no playbook on disk."""


class PlaybookPathError(ValueError):
    """Raised when a (layer, lens) pair resolves outside the playbook root."""


def resolve_playbook_path(repo_root: Path | str, layer: str, lens: str) -> Path:
    """Return the absolute path where the (layer, lens) playbook should live.

    `layer` and `lens` are interpolated straight into the path, so a value
    containing `..` or a leading `/` would otherwise resolve anywhere on the
    filesystem and `load_playbook` would read it. Both are rejected: the
    resolved path must stay under `<repo_root>/framework/playbooks/`
    (PLUGIN-PREPROD-001 L3).

    Raises PlaybookPathError on escape. Does not require the file to exist —
    use load_playbook() to actually read.

    Returns the **resolved** path, which is the one that was validated.
    Returning a freshly-built unresolved path instead would leave the checked
    path and the opened path as two different objects, so a symlinked
    component swapped between the check and the read would escape a check that
    passed.
    """
    if not str(layer).strip() or not str(lens).strip():
        raise PlaybookPathError(f"layer and lens must be non-empty: layer={layer!r} lens={lens!r}")
    root = (Path(repo_root) / "framework" / "playbooks").resolve()
    try:
        candidate = (root / layer / f"{lens}.md").resolve()
    except ValueError as exc:
        # An embedded null byte makes realpath raise a bare ValueError. Since
        # PlaybookPathError subclasses ValueError, letting that through would
        # escape a caller written to catch PlaybookPathError.
        raise PlaybookPathError(
            f"playbook path is not a usable path: layer={layer!r} lens={lens!r} ({exc})"
        ) from exc
    if not candidate.is_relative_to(root):
        raise PlaybookPathError(f"playbook path escapes {root}: layer={layer!r} lens={lens!r}")
    return candidate


def load_playbook(repo_root: Path | str, layer: str, lens: str) -> str:
    """Read and return the playbook content for (layer, lens).

    Raises PlaybookMissingError with a message naming the expected path
    if the file does not exist.
    """
    path = resolve_playbook_path(repo_root, layer, lens)
    if not path.is_file():
        # resolve_playbook_path returns a resolved path, so compare against a
        # resolved root or relative_to() raises on an unresolved repo_root.
        root = Path(repo_root).resolve()
        rel = path.relative_to(root) if path.is_relative_to(root) else path
        raise PlaybookMissingError(f"playbook missing: {rel}")
    return path.read_text()
