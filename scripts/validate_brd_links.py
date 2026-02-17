#!/usr/bin/env python3
"""
Validate local markdown links under docs/BRD.

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


@dataclass
class BrokenLink:
    source_file: str
    link: str
    target_path: str


@dataclass
class ScanResult:
    scan_timestamp: str
    root: str
    files_scanned: int
    broken_occurrences: int
    broken_source_files: int
    unique_missing_targets: int
    broken_links: list


def build_anchor_index(md_files: list[Path]) -> dict[Path, set[str]]:
    index: dict[Path, set[str]] = {}
    for file_path in md_files:
        anchors: set[str] = set()
        for line in file_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            match = HEADING_RE.match(line.strip())
            if not match:
                continue
            heading = match.group(2).strip().lower()
            heading = re.sub(r"[`*_~]", "", heading)
            heading = re.sub(r"[^a-z0-9\s-]", "", heading)
            heading = re.sub(r"\s+", "-", heading).strip("-")
            if heading:
                anchors.add(heading)
        index[file_path.resolve()] = anchors
    return index


def is_external(link: str) -> bool:
    return link.startswith(("http://", "https://", "mailto:", "tel:"))


def is_media_target(target: str) -> bool:
    return target.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"))


def resolve_target(workspace_root: Path, source_file: Path, target: str) -> Path:
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


def scan(root: Path, workspace_root: Path) -> ScanResult:
    md_files = sorted(root.rglob("*.md"))
    anchors = build_anchor_index(md_files)
    broken: list[BrokenLink] = []

    for file_path in md_files:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        for raw_link in LINK_RE.findall(content):
            link = raw_link.strip()
            if not link or is_external(link):
                continue

            if link.startswith("#"):
                anchor = link[1:]
                if anchor and anchor not in anchors.get(file_path.resolve(), set()):
                    broken.append(BrokenLink(str(file_path), link, str(file_path)))
                continue

            target, anchor = (link.split("#", 1) + [""])[:2]
            if is_media_target(target):
                continue

            target_path = resolve_target(workspace_root, file_path, target)
            if not target_path.exists():
                broken.append(BrokenLink(str(file_path), link, str(target_path)))
                continue

            if anchor and target_path.suffix.lower() == ".md":
                anchor_set = anchors.get(target_path.resolve(), set())
                if anchor not in anchor_set:
                    broken.append(BrokenLink(str(file_path), link, str(target_path)))

    return ScanResult(
        scan_timestamp=datetime.now(timezone.utc).isoformat(),
        root=str(root),
        files_scanned=len(md_files),
        broken_occurrences=len(broken),
        broken_source_files=len({x.source_file for x in broken}),
        unique_missing_targets=len({x.target_path for x in broken}),
        broken_links=[asdict(x) for x in broken],
    )


def write_markdown_report(path: Path, result: ScanResult) -> None:
    lines = [
        "# BRD Link Validation Report",
        "",
        f"- scan_timestamp: {result.scan_timestamp}",
        f"- root: {result.root}",
        f"- files_scanned: {result.files_scanned}",
        f"- broken_occurrences: {result.broken_occurrences}",
        f"- broken_source_files: {result.broken_source_files}",
        f"- unique_missing_targets: {result.unique_missing_targets}",
        "",
        "## Broken Links",
    ]

    if not result.broken_links:
        lines.append("No broken links found.")
    else:
        for item in result.broken_links:
            lines.append(
                f"- source: {item['source_file']} | link: {item['link']} | target: {item['target_path']}"
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_broken_links_txt(path: Path, result: ScanResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in result.broken_links:
            handle.write(
                f"{item['source_file']} :: {item['link']} -> {item['target_path']}\n"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate BRD markdown local links")
    parser.add_argument("--root", default="docs/BRD", help="Root folder to scan")
    parser.add_argument("--workspace-root", default=".", help="Workspace root path")
    parser.add_argument("--output", help="Optional markdown report path")
    parser.add_argument("--json-output", help="Optional JSON report path")
    parser.add_argument("--broken-links-output", help="Optional plain-text broken links path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    workspace_root = Path(args.workspace_root).resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Scan root not found or not a directory: {root}")

    result = scan(root, workspace_root)

    if args.json_output:
        json_path = Path(args.json_output)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")

    if args.broken_links_output:
        write_broken_links_txt(Path(args.broken_links_output), result)

    if args.output:
        write_markdown_report(Path(args.output), result)

    print(json.dumps({
        "scan_timestamp": result.scan_timestamp,
        "files_scanned": result.files_scanned,
        "broken_occurrences": result.broken_occurrences,
        "broken_source_files": result.broken_source_files,
        "unique_missing_targets": result.unique_missing_targets,
    }))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
