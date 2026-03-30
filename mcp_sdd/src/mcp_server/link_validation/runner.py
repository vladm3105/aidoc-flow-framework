"""Link validation runner for SDD documentation.

Validates markdown links in documentation files:
- Relative file links exist
- Anchor references (#heading) resolve in target files
- Reports broken links with file, line number, and target
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from urllib.parse import unquote


LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")

SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", "venv", ".venv",
    "env", ".env", "dist", "build", ".cache", "tmp",
}

MEDIA_EXTENSIONS = (
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
    ".ico", ".bmp", ".tiff", ".pdf",
)


@dataclass(frozen=True)
class LinkValidationRunResult:
    payload: dict[str, object]
    report_json: str
    report_text: str
    passed: bool
    report_path: Path | None
    summary_path: Path | None


def _should_skip_dir(path: Path, root: Path) -> bool:
    """Check if any directory component relative to root is in the skip list."""
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    return any(part in SKIP_DIRS for part in rel.parts)


def _heading_to_anchor(heading: str) -> str:
    """Convert heading text to GitHub-flavored markdown anchor slug."""
    slug = heading.strip().lower()
    slug = re.sub(r"[`*_~]", "", slug)
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug).strip("-")
    return slug


def _build_anchor_index(md_files: list[Path]) -> dict[Path, set[str]]:
    index: dict[Path, set[str]] = {}
    for file_path in md_files:
        anchors: set[str] = set()
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line in content.splitlines():
            match = HEADING_RE.match(line.strip())
            if match:
                anchor = _heading_to_anchor(match.group(2))
                if anchor:
                    anchors.add(anchor)
        index[file_path.resolve()] = anchors
    return index


def _is_external(link: str) -> bool:
    return link.startswith(("http://", "https://", "mailto:", "tel:", "ftp://"))


def _is_media(target: str) -> bool:
    return target.lower().endswith(MEDIA_EXTENSIONS)


def _resolve_target(workspace_root: Path, source_file: Path, target: str) -> Path:
    decoded = unquote(target)
    if decoded.startswith("/"):
        resolved = workspace_root / decoded.lstrip("/")
    else:
        resolved = source_file.parent / decoded
    if not resolved.suffix:
        fallback = resolved.with_suffix(".md")
        if fallback.exists():
            return fallback
    return resolved


def _collect_md_files(target_path: Path) -> list[Path]:
    if target_path.is_file():
        return [target_path] if target_path.suffix.lower() == ".md" else []
    return sorted(
        f for f in target_path.rglob("*.md") if not _should_skip_dir(f, target_path)
    )


def _render_text(payload: dict[str, object]) -> str:
    status = str(payload.get("status", "fail")).upper()
    lines = [
        "Link Validation Report",
        f"Target: {payload.get('target_path')}",
        f"Status: {status}",
        "",
        f"Files scanned: {payload.get('files_scanned', 0)}",
        f"Total links checked: {payload.get('total_links_checked', 0)}",
        f"Broken links: {payload.get('broken_count', 0)}",
        "",
    ]
    broken = payload.get("broken_links", [])
    if isinstance(broken, list) and broken:
        lines.append("Broken links:")
        for item in broken:
            if isinstance(item, dict):
                src = item.get("source_file", "?")
                ln = item.get("line_number", "?")
                link = item.get("link", "?")
                reason = item.get("reason", "?")
                lines.append(f"  {src}:{ln} [{link}] — {reason}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def run_link_validation(
    *,
    target_path: Path,
    workspace_root: Path | None = None,
    output_dir: Path | None = None,
) -> LinkValidationRunResult:
    """Validate markdown links in target file or directory.

    Args:
        target_path: single file or directory to scan
        workspace_root: root for resolving absolute paths (defaults to target or parent)
        output_dir: optional directory for writing report artifacts
    """
    if not target_path.exists():
        raise FileNotFoundError(f"Target path does not exist: {target_path}")

    if workspace_root is None:
        workspace_root = target_path if target_path.is_dir() else target_path.parent

    md_files = _collect_md_files(target_path)

    # Build anchor index from all md files under workspace root for cross-file resolution
    if target_path.is_file():
        all_md = sorted(
            f for f in workspace_root.rglob("*.md") if not _should_skip_dir(f, workspace_root)
        )
    else:
        all_md = md_files
    anchors = _build_anchor_index(all_md)

    broken_links: list[dict[str, object]] = []
    total_links = 0

    for file_path in md_files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for line_number, line in enumerate(content.splitlines(), 1):
            for raw_link in LINK_RE.findall(line):
                link = raw_link.strip()
                if not link or _is_external(link):
                    continue

                total_links += 1

                # Same-file anchor
                if link.startswith("#"):
                    anchor = link[1:]
                    if anchor and anchor not in anchors.get(file_path.resolve(), set()):
                        broken_links.append({
                            "source_file": str(file_path),
                            "line_number": line_number,
                            "link": link,
                            "target_path": str(file_path),
                            "reason": "anchor_not_found",
                        })
                    continue

                # Split target and anchor
                parts = link.split("#", 1)
                target = parts[0]
                anchor = parts[1] if len(parts) > 1 else ""

                if _is_media(target):
                    continue

                resolved = _resolve_target(workspace_root, file_path, target)
                if not resolved.exists():
                    broken_links.append({
                        "source_file": str(file_path),
                        "line_number": line_number,
                        "link": link,
                        "target_path": str(resolved),
                        "reason": "file_not_found",
                    })
                    continue

                if anchor and resolved.suffix.lower() == ".md":
                    anchor_set = anchors.get(resolved.resolve(), set())
                    if anchor not in anchor_set:
                        broken_links.append({
                            "source_file": str(file_path),
                            "line_number": line_number,
                            "link": link,
                            "target_path": str(resolved),
                            "reason": "anchor_not_found",
                        })

    passed = len(broken_links) == 0
    payload: dict[str, object] = {
        "status": "pass" if passed else "fail",
        "target_path": str(target_path),
        "files_scanned": len(md_files),
        "total_links_checked": total_links,
        "broken_count": len(broken_links),
        "broken_source_files": len({bl["source_file"] for bl in broken_links}),
        "unique_missing_targets": len({bl["target_path"] for bl in broken_links}),
        "broken_links": broken_links,
    }

    report_json = json.dumps(payload, sort_keys=True)
    report_text = _render_text(payload)

    report_path: Path | None = None
    summary_path: Path | None = None
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / "link_validation_report.json"
        summary_path = output_dir / "link_validation_report.txt"
        report_path.write_text(report_json, encoding="utf-8")
        summary_path.write_text(report_text, encoding="utf-8")

    return LinkValidationRunResult(
        payload=payload,
        report_json=report_json,
        report_text=report_text,
        passed=passed,
        report_path=report_path,
        summary_path=summary_path,
    )
