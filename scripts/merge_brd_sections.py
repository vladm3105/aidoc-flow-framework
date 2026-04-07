#!/usr/bin/env python3
"""Merge sectioned BRD markdown files into single consolidated MD files.

For each BRD folder under docs/01_BRD/:
1. Read index file (.0_index.md) frontmatter → becomes document_control header
2. Concatenate section files (.1 through .17/.18/.19) in numeric order
3. Skip appendices file (highest section number) — kept as companion
4. Write consolidated BRD-NN_{slug}.md
5. Move section files to {brd_folder}/archive/

Usage:
    python scripts/merge_brd_sections.py /opt/data/b-local/b-local-docs [--dry-run]
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path


# Section files match: BRD-NN.S_name.md where S is a number
SECTION_FILE_PATTERN = re.compile(r"^(BRD-\d+)\.(\d+)_(.+)\.md$")

# Files to skip during merge (not section content)
SKIP_SUFFIXES = {"_validated", "_remediate_copy", ".ucx."}
SKIP_NAMES = {"review_prompt", "review_prompt_sidecar", "review_prompt_inspection"}


def _parse_section_number(filename: str) -> tuple[str, int, str] | None:
    """Extract (doc_id, section_number, slug) from filename."""
    m = SECTION_FILE_PATTERN.match(filename)
    if not m:
        return None
    return m.group(1), int(m.group(2)), m.group(3)


def _strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter (--- delimited) from markdown content."""
    if not text.startswith("---"):
        return text
    end = text.find("---", 3)
    if end == -1:
        return text
    return text[end + 3:].lstrip("\n")


def _strip_navigation(text: str) -> str:
    """Remove navigation lines (> **Navigation**: ...) from section content."""
    lines = text.split("\n")
    filtered = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("> **Navigation**:"):
            continue
        if stripped.startswith("> **Nav**:"):
            continue
        filtered.append(line)
    return "\n".join(filtered)


def _extract_frontmatter_yaml(text: str) -> str:
    """Extract raw YAML frontmatter block."""
    if not text.startswith("---"):
        return ""
    end = text.find("---", 3)
    if end == -1:
        return ""
    return text[3:end].strip()


def merge_brd_folder(brd_dir: Path, dry_run: bool = False) -> dict:
    """Merge section files in a single BRD folder.

    Returns dict with merge stats.
    """
    folder_name = brd_dir.name
    # Extract BRD-NN and slug from folder name (e.g., BRD-05_multi_agent_ai_system)
    m = re.match(r"^(BRD-\d+)_(.+)$", folder_name)
    if not m:
        return {"folder": folder_name, "skipped": True, "reason": "invalid folder name"}

    doc_id = m.group(1)
    slug = m.group(2)

    # Find all section files
    section_files: dict[int, Path] = {}
    for f in sorted(brd_dir.iterdir()):
        if not f.is_file() or f.suffix.lower() != ".md":
            continue
        parsed = _parse_section_number(f.name)
        if parsed is None:
            continue
        fid, sec_num, _ = parsed
        if fid != doc_id:
            continue
        section_files[sec_num] = f

    if not section_files:
        return {"folder": folder_name, "skipped": True, "reason": "no section files found"}

    # Determine which section is appendices (highest number, typically 18 or 19)
    max_section = max(section_files.keys())
    appendices_file = section_files.get(max_section)
    appendices_slug = ""
    if appendices_file:
        parsed = _parse_section_number(appendices_file.name)
        if parsed:
            appendices_slug = parsed[2]

    # If highest section is appendices, exclude it from merge
    is_appendices = appendices_slug in ("appendices", "appendix")

    # Build consolidated content
    parts: list[str] = []

    # Index file (section 0) — extract frontmatter as document header
    index_file = section_files.get(0)
    if index_file and index_file.exists():
        index_text = index_file.read_text(encoding="utf-8")
        fm_yaml = _extract_frontmatter_yaml(index_text)
        if fm_yaml:
            parts.append(f"---\n{fm_yaml}\n---\n")
        # Add any content after frontmatter from index
        index_body = _strip_frontmatter(index_text).strip()
        index_body = _strip_navigation(index_body).strip()
        # Remove diagram request comments from index (they'll be in sections)
        if index_body:
            parts.append(index_body)
            parts.append("")

    # Concatenate section files 1..N (excluding 0 and optionally appendices)
    for sec_num in sorted(section_files.keys()):
        if sec_num == 0:
            continue
        if is_appendices and sec_num == max_section:
            continue

        sec_file = section_files[sec_num]
        sec_text = sec_file.read_text(encoding="utf-8")
        sec_body = _strip_frontmatter(sec_text).strip()
        sec_body = _strip_navigation(sec_body).strip()

        if sec_body:
            parts.append(sec_body)
            parts.append("")

    consolidated = "\n\n".join(parts).rstrip() + "\n"

    # Target filename
    target_name = f"{doc_id}_{slug}.md"
    target_path = brd_dir / target_name

    # Collect files to archive (all section .N_ files)
    files_to_archive = [section_files[n] for n in sorted(section_files.keys())]
    # Also include SVG files
    svg_files = list(brd_dir.glob(f"{doc_id}*.svg"))

    # Don't archive appendices — it stays as companion
    if is_appendices and appendices_file in files_to_archive:
        files_to_archive.remove(appendices_file)

    if dry_run:
        return {
            "folder": folder_name,
            "target": target_name,
            "sections_merged": len([n for n in section_files if n != 0 and not (is_appendices and n == max_section)]),
            "appendices_kept": appendices_file.name if is_appendices and appendices_file else None,
            "files_to_archive": len(files_to_archive),
            "consolidated_lines": consolidated.count("\n"),
            "dry_run": True,
        }

    # Check if target already exists (skip to avoid data loss)
    if target_path.exists():
        return {"folder": folder_name, "skipped": True, "reason": f"{target_name} already exists"}

    # Write consolidated file
    target_path.write_text(consolidated, encoding="utf-8")

    # Create archive directory and move section files
    archive_dir = brd_dir / "archive"
    archive_dir.mkdir(exist_ok=True)

    archived_count = 0
    for f in files_to_archive:
        if f.exists() and f != target_path:
            dest = archive_dir / f.name
            shutil.move(str(f), str(dest))
            archived_count += 1

    # Move SVGs to archive too
    for svg in svg_files:
        if svg.exists():
            shutil.move(str(svg), str(archive_dir / svg.name))
            archived_count += 1

    return {
        "folder": folder_name,
        "target": target_name,
        "sections_merged": len([n for n in section_files if n != 0 and not (is_appendices and n == max_section)]),
        "appendices_kept": appendices_file.name if is_appendices and appendices_file else None,
        "files_archived": archived_count,
        "consolidated_lines": consolidated.count("\n"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Merge sectioned BRD files into consolidated MDs")
    parser.add_argument("project_root", help="Project root (e.g., /opt/data/b-local/b-local-docs)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).expanduser().resolve()
    brd_root = project_root / "docs" / "01_BRD"

    if not brd_root.is_dir():
        print(f"Error: {brd_root} not found", file=sys.stderr)
        return 1

    # Find BRD folders that need conversion (no YAML file present)
    brd_folders = sorted(
        d for d in brd_root.iterdir()
        if d.is_dir()
        and d.name.startswith("BRD-")
        and not list(d.glob("*.yaml"))
    )

    print(f"Found {len(brd_folders)} BRD folders to process (skipping folders with existing YAML)")
    if args.dry_run:
        print("DRY RUN — no files will be modified\n")

    total_merged = 0
    total_archived = 0
    total_skipped = 0

    for brd_dir in brd_folders:
        result = merge_brd_folder(brd_dir, dry_run=args.dry_run)

        if result.get("skipped"):
            print(f"  SKIP {result['folder']}: {result.get('reason')}")
            total_skipped += 1
            continue

        sections = result.get("sections_merged", 0)
        appendices = result.get("appendices_kept", "none")
        lines = result.get("consolidated_lines", 0)

        if args.dry_run:
            archived = result.get("files_to_archive", 0)
            print(f"  WOULD MERGE {result['folder']}: {sections} sections → {result['target']} ({lines} lines), archive {archived} files, appendices: {appendices}")
        else:
            archived = result.get("files_archived", 0)
            print(f"  MERGED {result['folder']}: {sections} sections → {result['target']} ({lines} lines), archived {archived} files, appendices: {appendices}")
            total_archived += archived

        total_merged += 1

    print(f"\nSummary: {total_merged} merged, {total_skipped} skipped, {total_archived} files archived")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
