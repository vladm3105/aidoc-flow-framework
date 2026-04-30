#!/usr/bin/env python3
"""Convert consolidated BRD markdown files to YAML scaffold with block scalars.

For each BRD folder with a consolidated MD and no existing YAML:
1. Parse frontmatter for metadata
2. Split on '# Section N:' headings
3. Map section headings to YAML top-level keys
4. Write YAML with block scalars (content preserved as-is)
5. Move MD to archive/

Usage:
    python scripts/convert_brd_md_to_yaml.py /opt/data/b-local/b-local-docs [--dry-run]
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

# Section heading → YAML key mapping (normalized heading → yaml key)
# Multiple heading variants map to the same YAML key
SECTION_KEY_MAP: dict[str, str] = {
    # Standard sections
    "introduction": "introduction",
    "executive summary": "executive_summary",
    "business objectives": "business_objectives",
    "business context & objectives": "business_objectives",
    "business context & market sizing": "business_objectives",
    "business context": "introduction",
    "business context & background": "introduction",
    "project scope": "project_scope",
    "scope": "project_scope",
    "stakeholders": "stakeholders",
    "stakeholder analysis": "stakeholders",
    "stakeholders (high-level)": "stakeholders",
    "user stories": "user_stories",
    "user stories (high-level summary)": "user_stories",
    "functional requirements": "functional_requirements",
    "business requirements": "functional_requirements",
    "data requirements": "functional_requirements",
    "quality attributes": "quality_attributes",
    "quality attributes (non-functional requirements)": "quality_attributes",
    "architecture decision topics": "adr_topics",
    "architecture decision requirements": "adr_topics",
    "architecture overview": "adr_topics",
    "constraints and assumptions": "constraints_and_assumptions",
    "constraints & assumptions": "constraints_and_assumptions",
    "constraints assumptions": "constraints_and_assumptions",
    "business constraints and assumptions": "constraints_and_assumptions",
    "key assumptions & constraints": "constraints_and_assumptions",
    "acceptance criteria": "acceptance_criteria",
    "success criteria": "acceptance_criteria",
    "risk management": "risk_management",
    "business risk management": "risk_management",
    "consolidated risk register": "risk_management",
    "risk heat maps": "risk_management",
    "implementation approach": "implementation_considerations",
    "implementation": "implementation_considerations",
    "support and maintenance": "support_maintenance",
    "support & maintenance": "support_maintenance",
    "support maintenance": "support_maintenance",
    "cost-benefit analysis": "cost_benefit_analysis",
    "cost benefit analysis": "cost_benefit_analysis",
    "project governance": "governance",
    "governance": "governance",
    "governance & approval": "governance",
    "quality assurance": "document_quality",
    "traceability": "traceability",
    "traceability matrix": "traceability",
    "glossary": "glossary",
    "index": "_index",
    "dependencies": "dependencies",
    "future considerations": "future_considerations",
    # BRD-36/37 finance-specific
    "revenue model & pricing architecture": "revenue_model",
    "cost structure (cogs & opex)": "cost_structure",
    "unit economics & margins": "unit_economics",
    "growth model & user acquisition": "growth_model",
    "p&l projections (m0–m48)": "pl_projections",
    "funding requirements & capital planning": "funding_requirements",
    "staffing & organizational plan": "staffing_plan",
    "infrastructure & technology costs": "infrastructure_costs",
    "sensitivity analysis & scenarios": "sensitivity_analysis",
    "corridor expansion economics": "corridor_expansion",
    "model architecture & traceability": "traceability",
}

# Heading pattern: # Section N: Title
SECTION_HEADING_RE = re.compile(r"^# Section (\d+):\s*(.+)$", re.MULTILINE)


def _extract_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and return (frontmatter_dict, body)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("---", 3)
    if end == -1:
        return {}, text
    fm_text = text[3:end].strip()
    body = text[end + 3:].lstrip("\n")
    try:
        fm = yaml.safe_load(fm_text)
        if not isinstance(fm, dict):
            fm = {}
    except yaml.YAMLError:
        fm = {}
    return fm, body


def _split_sections(body: str) -> list[tuple[int, str, str]]:
    """Split body on '# Section N: Title' headings.

    Returns list of (section_number, title, content).
    """
    matches = list(SECTION_HEADING_RE.finditer(body))
    if not matches:
        return [(0, "body", body.strip())]

    sections = []
    for i, m in enumerate(matches):
        sec_num = int(m.group(1))
        title = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        content = body[start:end].strip()
        sections.append((sec_num, title, content))
    return sections


def _normalize_heading(title: str) -> str:
    """Normalize heading for lookup."""
    return title.lower().strip()


def _heading_to_key(title: str) -> str:
    """Map a section heading to a YAML key."""
    normalized = _normalize_heading(title)
    if normalized in SECTION_KEY_MAP:
        return SECTION_KEY_MAP[normalized]
    # Fallback: slugify the heading
    slug = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")
    return slug


def _build_metadata(fm: dict, doc_id: str, title: str) -> dict:
    """Build metadata section from frontmatter."""
    tags = fm.get("tags", [])
    if not isinstance(tags, list):
        tags = []
    # Clean tags — keep only relevant ones
    tags = [t for t in tags if isinstance(t, str) and t not in ("brd-index", "brd-section")]
    if "brd-document" not in tags:
        tags.insert(0, "brd-document")
    if "layer-1-artifact" not in tags:
        tags.append("layer-1-artifact")

    custom = fm.get("custom_fields", {})
    if not isinstance(custom, dict):
        custom = {}

    brd_category = custom.get("brd_category", "feature")

    meta = {
        "schema_version": "1.5",
        "document_type": "brd-document",
        "layer": 1,
        "lifecycle": "mvp-prod-newmvp",
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "validation": {
            "tool": "sdd_validate",
            "server": "mcp_ucx",
        },
        "c4_level": {"value": "context"},
        "tags": tags,
        "deliverable_type": {
            "value": "code",
            "routing": {
                "code": "CSPEC",
                "document": "DSPEC",
                "ux": "UXSPEC",
                "risk": "RISKSPEC",
                "process": "PROCSPEC",
            },
        },
        "brd_type": {"value": brd_category},
    }
    return meta


def _build_document_control(fm: dict, doc_id: str, title: str) -> dict:
    """Build document_control section from frontmatter."""
    custom = fm.get("custom_fields", {})
    if not isinstance(custom, dict):
        custom = {}

    prd_ready = custom.get("prd_ready_score", "")
    status = custom.get("status", "Draft")
    depends = custom.get("depends", [])
    if not isinstance(depends, list):
        depends = []

    return {
        "project_name": title,
        "version": "1.0",
        "status": status if isinstance(status, str) else "Draft",
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "prd_ready_score": str(prd_ready) if prd_ready else "",
        "depends": depends,
    }


def _yaml_block_scalar(content: str) -> str:
    """Format content as a YAML block scalar value."""
    # Remove leading/trailing whitespace but preserve internal structure
    return content.strip()


def convert_brd_to_yaml(brd_dir: Path, dry_run: bool = False) -> dict:
    """Convert a consolidated MD BRD to YAML scaffold."""
    folder_name = brd_dir.name
    m = re.match(r"^(BRD-\d+)_(.+)$", folder_name)
    if not m:
        return {"folder": folder_name, "skipped": True, "reason": "invalid folder name"}

    doc_id = m.group(1)
    slug = m.group(2)

    # Check for existing YAML
    existing_yaml = list(brd_dir.glob("*.yaml"))
    if existing_yaml:
        return {"folder": folder_name, "skipped": True, "reason": "YAML already exists"}

    # Find consolidated MD
    md_name = f"{doc_id}_{slug}.md"
    md_path = brd_dir / md_name
    if not md_path.exists():
        return {"folder": folder_name, "skipped": True, "reason": f"{md_name} not found"}

    md_text = md_path.read_text(encoding="utf-8")
    fm, body = _extract_frontmatter(md_text)

    title = fm.get("title", slug.replace("_", " ").title())
    # Clean title — remove " - Index" suffix
    title = re.sub(r"\s*-\s*Index$", "", title)

    sections = _split_sections(body)

    # Build YAML document
    doc: dict = {}
    doc["id"] = doc_id
    doc["title"] = title
    doc["metadata"] = _build_metadata(fm, doc_id, title)
    doc["document_control"] = _build_document_control(fm, doc_id, title)

    # Track which YAML keys we've populated
    seen_keys: set[str] = set()

    for sec_num, sec_title, sec_content in sections:
        yaml_key = _heading_to_key(sec_title)
        if yaml_key == "_index":
            continue  # Skip index content (already in metadata)
        if yaml_key in seen_keys:
            # Append to existing key
            existing = doc.get(yaml_key, "")
            doc[yaml_key] = existing + "\n\n" + sec_content if existing else sec_content
        else:
            doc[yaml_key] = sec_content
            seen_keys.add(yaml_key)

    # Ensure diagrams section exists
    if "diagrams" not in doc:
        doc["diagrams"] = {"items": []}

    section_count = len(seen_keys)
    yaml_path = brd_dir / f"{doc_id}_{slug}.yaml"

    if dry_run:
        return {
            "folder": folder_name,
            "target": yaml_path.name,
            "sections": section_count,
            "yaml_keys": sorted(seen_keys),
            "dry_run": True,
        }

    # Write YAML
    # Use custom dumper to handle block scalars for long strings
    yaml_content = _render_yaml(doc)
    yaml_path.write_text(yaml_content, encoding="utf-8")

    # Move MD to archive
    archive_dir = brd_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    if md_path.exists():
        shutil.move(str(md_path), str(archive_dir / md_path.name))

    return {
        "folder": folder_name,
        "target": yaml_path.name,
        "sections": section_count,
        "yaml_keys": sorted(seen_keys),
        "lines": yaml_content.count("\n"),
    }


class _BlockScalarStr(str):
    """String subclass that serializes as YAML block scalar."""
    pass


def _block_scalar_representer(dumper: yaml.Dumper, data: _BlockScalarStr) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


def _render_yaml(doc: dict) -> str:
    """Render document dict to YAML with block scalars for long content."""
    # Convert long string values to block scalars
    processed = _process_for_yaml(doc)

    dumper = yaml.Dumper
    dumper.add_representer(_BlockScalarStr, _block_scalar_representer)

    header = (
        f"# {'=' * 77}\n"
        f"#  {doc['id']}_{doc.get('title', '').replace(' ', '_')}.yaml\n"
        f"#  Converted from consolidated markdown\n"
        f"#  Conversion date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n"
        f"#  Schema: mcp_ucx BRD-TEMPLATE.yaml v1.5\n"
        f"# {'=' * 77}\n\n"
    )

    body = yaml.dump(
        processed,
        Dumper=dumper,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )

    return header + body


def _process_for_yaml(obj: object) -> object:
    """Recursively convert long strings to block scalar markers."""
    if isinstance(obj, str):
        if "\n" in obj or len(obj) > 120:
            return _BlockScalarStr(obj)
        return obj
    if isinstance(obj, dict):
        return {k: _process_for_yaml(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_process_for_yaml(item) for item in obj]
    return obj


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert consolidated BRD MDs to YAML scaffolds")
    parser.add_argument("project_root", help="Project root (e.g., /opt/data/b-local/b-local-docs)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).expanduser().resolve()
    brd_root = project_root / "docs" / "01_BRD"

    if not brd_root.is_dir():
        print(f"Error: {brd_root} not found", file=sys.stderr)
        return 1

    # Find BRD folders with archive/ (went through Phase 1) and no YAML
    brd_folders = sorted(
        d for d in brd_root.iterdir()
        if d.is_dir()
        and d.name.startswith("BRD-")
        and (d / "archive").is_dir()
        and not list(d.glob("*.yaml"))
    )

    print(f"Found {len(brd_folders)} BRD folders to convert")
    if args.dry_run:
        print("DRY RUN — no files will be modified\n")

    converted = 0
    skipped = 0

    for brd_dir in brd_folders:
        result = convert_brd_to_yaml(brd_dir, dry_run=args.dry_run)

        if result.get("skipped"):
            print(f"  SKIP {result['folder']}: {result.get('reason')}")
            skipped += 1
            continue

        keys = result.get("yaml_keys", [])
        sections = result.get("sections", 0)

        if args.dry_run:
            print(f"  WOULD CONVERT {result['folder']}: {sections} sections → {result['target']}")
        else:
            lines = result.get("lines", 0)
            print(f"  CONVERTED {result['folder']}: {sections} sections → {result['target']} ({lines} lines)")

        converted += 1

    print(f"\nSummary: {converted} converted, {skipped} skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
