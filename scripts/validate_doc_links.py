#!/usr/bin/env python3
"""
Validate local markdown links across docs_flow_framework documentation.

Scans all markdown files and validates:
- Relative file links exist
- Anchor references (#heading) exist in target files
- Cross-references between SDD artifacts
- Governance documentation links

Outputs:
- JSON metrics/details report
- Plain-text broken links snapshot
- Optional Markdown summary report
"""

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import unquote
from datetime import datetime, timezone


LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")

# Directories to skip during scanning
SKIP_DIRS = {
    "node_modules",
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "env",
    ".env",
    "dist",
    "build",
    ".cache",
    "tmp",
}


@dataclass
class BrokenLink:
    source_file: str
    link: str
    target_path: str
    reason: str = "not_found"


@dataclass
class ScanResult:
    scan_timestamp: str
    root: str
    files_scanned: int
    total_links: int
    broken_occurrences: int
    broken_source_files: int
    unique_missing_targets: int
    broken_links: list


def should_skip_dir(path: Path) -> bool:
    """Check if any part of path is in skip list."""
    return any(part in SKIP_DIRS for part in path.parts)


def build_anchor_index(md_files: list[Path]) -> dict[Path, set[str]]:
    """Build index of heading anchors for all markdown files."""
    index: dict[Path, set[str]] = {}
    for file_path in md_files:
        anchors: set[str] = set()
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, IOError):
            continue

        for line in content.splitlines():
            match = HEADING_RE.match(line.strip())
            if not match:
                continue
            heading = match.group(2).strip().lower()
            # Remove markdown formatting
            heading = re.sub(r"[`*_~]", "", heading)
            # Remove special characters except hyphens
            heading = re.sub(r"[^a-z0-9\s-]", "", heading)
            # Replace spaces with hyphens
            heading = re.sub(r"\s+", "-", heading).strip("-")
            if heading:
                anchors.add(heading)
        index[file_path.resolve()] = anchors
    return index


def is_external(link: str) -> bool:
    """Check if link is external (http, mailto, etc.)."""
    return link.startswith(("http://", "https://", "mailto:", "tel:", "ftp://"))


def is_media_target(target: str) -> bool:
    """Check if target is a media file."""
    media_extensions = (
        ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
        ".ico", ".bmp", ".tiff", ".pdf"
    )
    return target.lower().endswith(media_extensions)


def resolve_target(workspace_root: Path, source_file: Path, target: str) -> Path:
    """Resolve a link target to an absolute path."""
    decoded = unquote(target)

    # Absolute path from workspace root
    if decoded.startswith("/"):
        resolved = workspace_root / decoded.lstrip("/")
    else:
        # Relative path from source file
        resolved = source_file.parent / decoded

    # Try adding .md extension if no extension present
    if not resolved.suffix:
        fallback = resolved.with_suffix(".md")
        if fallback.exists():
            return fallback

    return resolved


def scan(root: Path, workspace_root: Path) -> ScanResult:
    """Scan markdown files for broken links."""
    # Find all markdown files, excluding skip directories
    md_files = []
    for file_path in root.rglob("*.md"):
        if not should_skip_dir(file_path):
            md_files.append(file_path)
    md_files = sorted(md_files)

    # Build anchor index
    anchors = build_anchor_index(md_files)
    broken: list[BrokenLink] = []
    total_links = 0

    for file_path in md_files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, IOError):
            continue

        for raw_link in LINK_RE.findall(content):
            link = raw_link.strip()
            if not link or is_external(link):
                continue

            total_links += 1

            # Same-file anchor reference
            if link.startswith("#"):
                anchor = link[1:]
                if anchor and anchor not in anchors.get(file_path.resolve(), set()):
                    broken.append(BrokenLink(
                        str(file_path), link, str(file_path), "anchor_not_found"
                    ))
                continue

            # Split target and anchor
            target, anchor = (link.split("#", 1) + [""])[:2]

            # Skip media files
            if is_media_target(target):
                continue

            # Resolve and check target
            target_path = resolve_target(workspace_root, file_path, target)
            if not target_path.exists():
                broken.append(BrokenLink(
                    str(file_path), link, str(target_path), "file_not_found"
                ))
                continue

            # Check anchor in target file
            if anchor and target_path.suffix.lower() == ".md":
                anchor_set = anchors.get(target_path.resolve(), set())
                if anchor not in anchor_set:
                    broken.append(BrokenLink(
                        str(file_path), link, str(target_path), "anchor_not_found"
                    ))

    return ScanResult(
        scan_timestamp=datetime.now(timezone.utc).isoformat(),
        root=str(root),
        files_scanned=len(md_files),
        total_links=total_links,
        broken_occurrences=len(broken),
        broken_source_files=len({x.source_file for x in broken}),
        unique_missing_targets=len({x.target_path for x in broken}),
        broken_links=[asdict(x) for x in broken],
    )


def write_markdown_report(path: Path, result: ScanResult) -> None:
    """Write a markdown summary report."""
    lines = [
        "# Documentation Link Validation Report",
        "",
        f"**Scan timestamp**: {result.scan_timestamp}",
        f"**Root**: {result.root}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|:-------|------:|",
        f"| Files scanned | {result.files_scanned} |",
        f"| Total links checked | {result.total_links} |",
        f"| Broken occurrences | {result.broken_occurrences} |",
        f"| Files with broken links | {result.broken_source_files} |",
        f"| Unique missing targets | {result.unique_missing_targets} |",
        "",
    ]

    if not result.broken_links:
        lines.append("**Status**: All links valid.")
    else:
        lines.append("## Broken Links")
        lines.append("")
        lines.append("| Source File | Link | Target | Reason |")
        lines.append("|:------------|:-----|:-------|:-------|")
        for item in result.broken_links:
            source = Path(item['source_file']).name
            lines.append(
                f"| `{source}` | `{item['link']}` | `{item['target_path']}` | {item['reason']} |"
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_broken_links_txt(path: Path, result: ScanResult) -> None:
    """Write plain-text list of broken links."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in result.broken_links:
            handle.write(
                f"{item['source_file']} :: {item['link']} -> {item['target_path']} [{item['reason']}]\n"
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate markdown local links in docs_flow_framework"
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Root folder to scan (default: current directory)"
    )
    parser.add_argument(
        "--workspace-root",
        default=".",
        help="Workspace root for resolving absolute paths (default: current directory)"
    )
    parser.add_argument(
        "--output",
        help="Optional markdown report path"
    )
    parser.add_argument(
        "--json-output",
        help="Optional JSON report path"
    )
    parser.add_argument(
        "--broken-links-output",
        help="Optional plain-text broken links path"
    )
    parser.add_argument(
        "--fail-on-broken",
        action="store_true",
        help="Exit with code 1 if broken links found"
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    workspace_root = Path(args.workspace_root).resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Scan root not found or not a directory: {root}")

    result = scan(root, workspace_root)

    # Write outputs
    if args.json_output:
        json_path = Path(args.json_output)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")

    if args.broken_links_output:
        write_broken_links_txt(Path(args.broken_links_output), result)

    if args.output:
        write_markdown_report(Path(args.output), result)

    # Print summary
    print(json.dumps({
        "scan_timestamp": result.scan_timestamp,
        "files_scanned": result.files_scanned,
        "total_links": result.total_links,
        "broken_occurrences": result.broken_occurrences,
        "broken_source_files": result.broken_source_files,
        "unique_missing_targets": result.unique_missing_targets,
    }, indent=2))

    if args.fail_on_broken and result.broken_occurrences > 0:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
