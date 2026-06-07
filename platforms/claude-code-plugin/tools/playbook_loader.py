"""Layer-and-lens playbook resolver for plugin audit SKILLs.

Resolves framework/playbooks/<layer>/<lens>.md, reads the content, and
raises a documented error if the file is missing.

Stdlib-only.
"""

from __future__ import annotations

from pathlib import Path


class PlaybookMissingError(FileNotFoundError):
    """Raised when a (layer, lens) pair has no playbook on disk."""


def resolve_playbook_path(repo_root: Path | str, layer: str, lens: str) -> Path:
    """Return the absolute path where the (layer, lens) playbook should live.

    No I/O. Pure path resolution. Use load_playbook() to actually read.
    """
    return Path(repo_root) / "framework" / "playbooks" / layer / f"{lens}.md"


def load_playbook(repo_root: Path | str, layer: str, lens: str) -> str:
    """Read and return the playbook content for (layer, lens).

    Raises PlaybookMissingError with a message naming the expected path
    if the file does not exist.
    """
    path = resolve_playbook_path(repo_root, layer, lens)
    if not path.is_file():
        rel = path.relative_to(repo_root) if path.is_absolute() else path
        raise PlaybookMissingError(f"playbook missing: {rel}")
    return path.read_text()
