"""UCX persona mapping management tools.

Provides show, set, diff, and health-check operations on the project-specific
``persona_mappings.yaml`` configuration.  All write operations preserve the
YAML header comments and use flow-style lists to match the canonical format.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from mcp_server.skills.project_ucx_loader import (
    PersonaMappingError,
    _invalidate_persona_mapping_cache,
    load_persona_mapping,
    resolve_ucx_root,
    validate_project_ucx_root,
)

VALID_PHASES: tuple[str, ...] = ("creation", "review", "remediation")


# ---------------------------------------------------------------------------
# YAML write helpers — preserve header comments + flow-style persona lists
# ---------------------------------------------------------------------------

class _FlowListDumper(yaml.SafeDumper):
    """Dumper that renders lists in flow style ``[a, b, c]``."""


def _flow_list_representer(dumper: yaml.Dumper, data: list) -> Any:
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)


_FlowListDumper.add_representer(list, _flow_list_representer)


def _extract_header(raw_text: str) -> tuple[str, str]:
    """Split YAML text into (header_comments, data_portion).

    Header is all leading lines that are blank or start with ``#``.
    """
    lines = raw_text.splitlines(keepends=True)
    header_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == "" or stripped.startswith("#"):
            header_lines.append(line)
        else:
            break
    header = "".join(header_lines)
    return header, raw_text[len(header):]


def _dump_with_header(header: str, data: dict) -> str:
    """Serialize *data* as YAML, prepending the original *header* comments."""
    body = yaml.dump(data, Dumper=_FlowListDumper, default_flow_style=False, sort_keys=False)
    return header + body


# ---------------------------------------------------------------------------
# Framework default loader
# ---------------------------------------------------------------------------

def _load_framework_default() -> dict:
    """Load the framework's canonical persona_mappings.yaml."""
    path = Path(__file__).resolve().parents[3] / "skills" / "persona_mappings.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Framework default persona_mappings.yaml not found: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def show_persona_mappings(
    *,
    project_root: Path,
    phase: str | None = None,
    doc_type: str | None = None,
) -> dict[str, Any]:
    """Return structured persona mapping data, optionally filtered."""
    mapping = load_persona_mapping(project_root=project_root)

    phases_to_show = [phase] if phase else [p for p in VALID_PHASES if p in mapping]
    result: dict[str, Any] = {}

    for p in phases_to_show:
        phase_map = mapping.get(p)
        if not isinstance(phase_map, dict):
            continue
        if doc_type:
            entry = phase_map.get(doc_type)
            if entry:
                result[p] = {doc_type: copy.deepcopy(entry)}
        else:
            result[p] = copy.deepcopy(phase_map)

    return {"version": mapping.get("version", "unknown"), "mappings": result}


def set_persona_mapping(
    *,
    project_root: Path,
    phase: str,
    doc_type: str,
    personas: list[str],
) -> dict[str, Any]:
    """Update persona list for a phase+doctype, write YAML, invalidate cache."""
    if phase not in VALID_PHASES:
        raise ValueError(f"Invalid phase '{phase}'. Must be one of: {VALID_PHASES}")
    if not personas:
        raise PersonaMappingError("Persona list must not be empty")

    ucx_root = validate_project_ucx_root(project_root)
    personas_dir = ucx_root / "skills" / "personas"

    # Validate all persona .md files exist.
    for name in personas:
        persona_path = personas_dir / f"{name}.md"
        if not persona_path.exists():
            raise PersonaMappingError(
                f"Persona file not found: {persona_path}. "
                f"Available personas: {sorted(p.stem for p in personas_dir.glob('*.md'))}"
            )

    # Load current mapping and read raw file for comment preservation.
    mappings_path = ucx_root / "skills" / "persona_mappings.yaml"
    raw_text = mappings_path.read_text(encoding="utf-8")
    header, _ = _extract_header(raw_text)

    mapping = copy.deepcopy(load_persona_mapping(project_root=project_root))

    # Capture previous value for the response.
    previous_personas: list[str] = []
    phase_map = mapping.get(phase)
    if isinstance(phase_map, dict):
        existing = phase_map.get(doc_type)
        if isinstance(existing, dict):
            previous_personas = list(existing.get("personas", []))

    # Set the new value.
    if phase not in mapping:
        mapping[phase] = {}
    if doc_type not in mapping[phase]:
        mapping[phase][doc_type] = {"personas": personas, "mode": "sequential"}
    else:
        mapping[phase][doc_type]["personas"] = personas

    # Write back.
    mappings_path.write_text(_dump_with_header(header, mapping), encoding="utf-8")
    _invalidate_persona_mapping_cache(project_root)

    return {
        "updated": {"phase": phase, "doc_type": doc_type, "personas": personas},
        "previous_personas": previous_personas,
    }


def diff_persona_mappings(
    *,
    project_root: Path,
) -> dict[str, Any]:
    """Compare project persona mappings against framework defaults."""
    project_mapping = load_persona_mapping(project_root=project_root)
    default_mapping = _load_framework_default()

    added: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    changed: list[dict[str, Any]] = []
    unchanged: list[dict[str, str]] = []

    for phase in VALID_PHASES:
        project_phase = project_mapping.get(phase, {})
        default_phase = default_mapping.get(phase, {})
        if not isinstance(project_phase, dict):
            project_phase = {}
        if not isinstance(default_phase, dict):
            default_phase = {}

        all_doctypes = sorted(set(project_phase.keys()) | set(default_phase.keys()))
        for dt in all_doctypes:
            proj_entry = project_phase.get(dt)
            def_entry = default_phase.get(dt)

            proj_personas = proj_entry.get("personas", []) if isinstance(proj_entry, dict) else []
            def_personas = def_entry.get("personas", []) if isinstance(def_entry, dict) else []
            proj_mode = proj_entry.get("mode", "sequential") if isinstance(proj_entry, dict) else "sequential"
            def_mode = def_entry.get("mode", "sequential") if isinstance(def_entry, dict) else "sequential"

            if proj_entry and not def_entry:
                added.append({"phase": phase, "doc_type": dt, "personas": proj_personas})
            elif def_entry and not proj_entry:
                removed.append({"phase": phase, "doc_type": dt, "personas": def_personas})
            elif proj_personas != def_personas or proj_mode != def_mode:
                entry: dict[str, Any] = {
                    "phase": phase,
                    "doc_type": dt,
                    "project_personas": proj_personas,
                    "default_personas": def_personas,
                }
                if proj_mode != def_mode:
                    entry["project_mode"] = proj_mode
                    entry["default_mode"] = def_mode
                changed.append(entry)
            else:
                unchanged.append({"phase": phase, "doc_type": dt})

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
        "summary": {
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
            "unchanged": len(unchanged),
        },
    }


def check_persona_mapping_health(
    *,
    project_root: Path,
) -> dict[str, Any]:
    """Check mapping completeness and file integrity.

    Unlike ``load_persona_mapping``, this does NOT raise on missing persona
    files — that's exactly what we want to detect and report.
    """
    ucx_root = validate_project_ucx_root(project_root)
    mappings_path = ucx_root / "skills" / "persona_mappings.yaml"
    mapping = yaml.safe_load(mappings_path.read_text(encoding="utf-8"))
    if not isinstance(mapping, dict):
        return {"status": "error", "missing_persona_files": [], "missing_doctypes": [],
                "extra_doctypes": [], "total_entries": 0}
    default_mapping = _load_framework_default()

    personas_dir = ucx_root / "skills" / "personas"
    missing_persona_files: list[str] = []
    missing_doctypes: list[str] = []
    extra_doctypes: list[str] = []

    # Check all referenced persona .md files exist.
    referenced_personas: set[str] = set()
    for phase in VALID_PHASES:
        phase_map = mapping.get(phase, {})
        if not isinstance(phase_map, dict):
            continue
        for _dt, config in phase_map.items():
            if isinstance(config, dict):
                for name in config.get("personas", []):
                    referenced_personas.add(name)

    for name in sorted(referenced_personas):
        if not (personas_dir / f"{name}.md").exists():
            missing_persona_files.append(name)

    # Check coverage against framework defaults.
    for phase in VALID_PHASES:
        project_phase = mapping.get(phase, {})
        default_phase = default_mapping.get(phase, {})
        if not isinstance(project_phase, dict):
            project_phase = {}
        if not isinstance(default_phase, dict):
            default_phase = {}

        for dt in default_phase:
            if dt not in project_phase:
                missing_doctypes.append(f"{phase}.{dt}")
        for dt in project_phase:
            if dt not in default_phase:
                extra_doctypes.append(f"{phase}.{dt}")

    status = "ok"
    if missing_doctypes or extra_doctypes:
        status = "warning"
    if missing_persona_files:
        status = "error"

    return {
        "status": status,
        "missing_persona_files": missing_persona_files,
        "missing_doctypes": missing_doctypes,
        "extra_doctypes": extra_doctypes,
        "total_entries": sum(
            len(mapping.get(p, {})) for p in VALID_PHASES if isinstance(mapping.get(p), dict)
        ),
    }
