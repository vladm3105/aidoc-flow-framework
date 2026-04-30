"""MCP Tool definitions and handler dispatch for SDD lifecycle.

25 tools total:
  - 2 session management (set/get project)
  - 13 deterministic (execute directly)
  - 2 orchestration (pipeline + advisor)
  - 6 LLM-dependent (optional executor param)
"""

from __future__ import annotations

import dataclasses
import json
import re
from pathlib import Path

from mcp.types import TextContent, Tool

from mcp_server.logging_config import (
    configure_logging,
    log_tool_call,
    log_tool_result,
)

from mcp_server.executor import (
    ExecutorConfig,
    ExecutorType,
    get_executor,
    list_executors,
    register_executor,
    run_executor,
)
from mcp_server.executor.cli_runner import ExecutorResult

# ── Tool definitions ────────────────────────────────────────────────────────

TOOLS: list[Tool] = [
    # ── Session management tools ─────────────────────────────────────────
    Tool(
        name="sdd_set_project",
        description="Set default project for this session. Subsequent tool calls can omit project. Pass empty string to clear session default.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path, or empty string to clear"},
            },
            "required": ["project"],
        },
    ),
    Tool(
        name="sdd_get_project",
        description="Show current default project (session override, config default, or none).",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    # ── Deterministic tools ──────────────────────────────────────────────
    Tool(
        name="sdd_init",
        description="Scaffold project-specific UCX assets (personas, templates, schemas, prompts) under UCX/",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path. Resolved from session/config default when omitted."},
                "update": {"type": "boolean", "description": "Overwrite stale files with latest framework versions. Protects project-owned files like persona_mappings.yaml (default: false)", "default": False},
                "update_mappings": {"type": "boolean", "description": "Also reset persona_mappings.yaml to framework defaults. Requires update=true (default: false)", "default": False},
            },
            "required": ["project"],
        },
    ),
    Tool(
        name="sdd_validate",
        description="Run structural validation against layer schema/template assets. When errors are found, creates a source-protected derived copy with fix instructions. If executor specified, spawns agent to apply fixes.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path. Resolved from session/config default when omitted."},
                "doc_type": {"type": "string", "description": "Document type (e.g. brd, prd, ears)"},
                "layer": {"type": "string", "description": "SDD layer directory (e.g. 01_BRD)"},
                "document": {"type": "string", "description": "Path to document file or directory"},
                "tier1_only": {"type": "boolean", "description": "Evaluate only tier1 blocking checks", "default": False},
                "strict": {"type": "boolean", "description": "Treat warnings as failures", "default": False},
                "format": {"type": "string", "enum": ["text", "json"], "description": "Output format", "default": "json"},
                "out": {"type": "string", "description": "Output directory for reports"},
                "validation_report": {"type": "string", "description": "Path to existing validation report. Skips re-validation, generates fix artifacts from this report."},
                "executor": {"type": "string", "description": "Executor name. Omit to return fix report text."},
                "timeout": {"type": "integer", "description": "Executor timeout in seconds", "default": 300},
            },
            "required": ["project", "doc_type", "layer", "document"],
        },
    ),
    Tool(
        name="sdd_validate_chg",
        description="Run CHG governance validation for change records (SDD v3 governance overlay).",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path. Resolved from session/config default when omitted."},
                "layer": {"type": "string", "description": "Layer directory for CHG template assets (typically CHG)"},
                "document": {"type": "string", "description": "Path to CHG document file or directory"},
                "out": {"type": "string", "description": "Output directory for reports"},
            },
            "required": ["project", "layer", "document"],
        },
    ),
    Tool(
        name="sdd_consistency",
        description="Run lightweight artifact lineage and stage consistency checks on a document folder.",
        inputSchema={
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Path to source document file or directory"},
                "format": {"type": "string", "enum": ["text", "json"], "default": "json"},
                "out": {"type": "string", "description": "Output directory"},
            },
            "required": ["target"],
        },
    ),
    Tool(
        name="sdd_validate_links",
        description="Validate markdown links in documentation files. Checks relative file links exist and anchor references resolve. Returns broken links with file, line number, and target. Scans .md files only (YAML files with embedded links are not scanned).",
        inputSchema={
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Path to a markdown file or directory to scan"},
                "workspace_root": {"type": "string", "description": "Workspace root for resolving absolute paths (defaults to target or its parent)"},
                "format": {"type": "string", "enum": ["text", "json"], "default": "json", "description": "Output format (used by CLI only)"},
                "out": {"type": "string", "description": "Output directory for reports"},
            },
            "required": ["target"],
        },
    ),
    Tool(
        name="sdd_preflight",
        description="Runtime and environment readiness check before create, review, or remediation stages.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path. Resolved from session/config default when omitted."},
                "context": {"type": "string", "enum": ["create", "review", "remediate", "any"], "default": "any"},
                "document": {"type": "string", "description": "Optional document path to verify"},
                "format": {"type": "string", "enum": ["text", "json"], "default": "json"},
                "out": {"type": "string", "description": "Output directory"},
            },
            "required": ["project"],
        },
    ),
    Tool(
        name="sdd_personas_show",
        description="Show persona assignments for a project. Displays phase-doctype-persona mappings.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path. Resolved from session/config default when omitted."},
                "phase": {"type": "string", "enum": ["creation", "review", "remediation"], "description": "Filter by phase (optional)"},
                "doc_type": {"type": "string", "description": "Filter by document type (optional)"},
            },
            "required": ["project"],
        },
    ),
    Tool(
        name="sdd_personas_set",
        description="Update persona list for a specific phase and document type. Validates persona files exist and writes back to YAML.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path. Resolved from session/config default when omitted."},
                "phase": {"type": "string", "enum": ["creation", "review", "remediation"], "description": "Lifecycle phase"},
                "doc_type": {"type": "string", "description": "Document type (e.g. brd, prd, _default)"},
                "personas": {"type": "array", "items": {"type": "string"}, "description": "Ordered list of persona names"},
            },
            "required": ["project", "phase", "doc_type", "personas"],
        },
    ),
    Tool(
        name="sdd_personas_diff",
        description="Compare project persona mappings against framework defaults. Shows added, removed, and changed entries.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path. Resolved from session/config default when omitted."},
            },
            "required": ["project"],
        },
    ),
    Tool(
        name="sdd_env_show",
        description="Show project .env keys without exposing values. Reports key count, blocked system variables, and file status.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path. Resolved from session/config default when omitted."},
            },
            "required": ["project"],
        },
    ),
    Tool(
        name="sdd_prescreen",
        description="Identify high-priority remediation candidate documents.",
        inputSchema={
            "type": "object",
            "properties": {
                "document": {"type": "string", "description": "Path to document file or directory"},
                "out": {"type": "string", "description": "Output directory"},
            },
            "required": ["document"],
        },
    ),
    Tool(
        name="sdd_scan",
        description="Extract finding category counts from a JSON validation or remediation report.",
        inputSchema={
            "type": "object",
            "properties": {
                "report_file": {"type": "string", "description": "Path to JSON report file"},
                "out": {"type": "string", "description": "Output directory"},
            },
            "required": ["report_file"],
        },
    ),
    Tool(
        name="sdd_score_show",
        description="Compute and display quality score from a validation report.",
        inputSchema={
            "type": "object",
            "properties": {
                "report_file": {"type": "string", "description": "Path to JSON report file"},
            },
            "required": ["report_file"],
        },
    ),
    Tool(
        name="sdd_score_validate",
        description="Check if a report's quality score meets a threshold. Returns pass/fail.",
        inputSchema={
            "type": "object",
            "properties": {
                "report_file": {"type": "string", "description": "Path to JSON report file"},
                "threshold": {"type": "integer", "description": "Minimum required score"},
            },
            "required": ["report_file", "threshold"],
        },
    ),
    Tool(
        name="sdd_score_compare",
        description="Compare quality scores between a baseline and candidate report. Returns delta.",
        inputSchema={
            "type": "object",
            "properties": {
                "baseline_report_file": {"type": "string", "description": "Path to baseline JSON report"},
                "candidate_report_file": {"type": "string", "description": "Path to candidate JSON report"},
            },
            "required": ["baseline_report_file", "candidate_report_file"],
        },
    ),
    Tool(
        name="sdd_list_executors",
        description="List all registered CLI and API executors with their type, status, and configuration. When project is provided, includes project-specific executor overrides.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {
                    "type": "string",
                    "description": "Optional project root. When provided, includes project-specific executor overrides.",
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="sdd_register_executor",
        description="Register a new CLI or API executor at runtime. Use executor_type='cli' for CLI agents, 'api' for LLM API providers.",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Unique executor name (e.g. 'aider', 'api/mistral')"},
                "executor_type": {"type": "string", "enum": ["cli", "api"], "description": "Executor type"},
                "command": {"type": "string", "description": "CLI binary name or path (for cli type)"},
                "args": {"type": "array", "items": {"type": "string"}, "description": "Base CLI arguments"},
                "prompt_mode": {"type": "string", "enum": ["file", "positional"], "description": "How to deliver prompt to CLI"},
                "model": {"type": "string", "description": "LiteLLM model string (for api type)"},
                "api_base": {"type": "string", "description": "Custom API base URL (for api type)"},
                "api_key_env": {"type": "string", "description": "Env var name for API key (for api type)"},
                "timeout": {"type": "integer", "description": "Default timeout in seconds", "default": 300},
            },
            "required": ["name", "executor_type"],
        },
    ),
    # ── Maintenance tools ──────────────────────────────────────────────
    Tool(
        name="sdd_clean",
        description="Remove obsolete stage artifacts from document folder, keeping only the latest report and derived copy per stage.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path. Resolved from session/config default when omitted."},
                "document": {"type": "string", "description": "Path to document file or directory to clean."},
                "stages": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["validate", "review", "remediate", "creation", "all"]},
                    "description": "Stages to clean. Default: ['all'].",
                    "default": ["all"],
                },
                "keep": {"type": "integer", "description": "Number of latest versions to keep per artifact type. Default: 1.", "default": 1, "minimum": 0},
                "dry_run": {"type": "boolean", "description": "List files that would be deleted without deleting. Default: true.", "default": True},
            },
            "required": ["document"],
        },
    ),
    # ── Orchestration tools ──────────────────────────────────────────────
    Tool(
        name="sdd_next_action",
        description="Inspect a document folder and recommend the next lifecycle stage based on existing artifacts.",
        inputSchema={
            "type": "object",
            "properties": {
                "document": {"type": "string", "description": "Path to document folder"},
            },
            "required": ["document"],
        },
    ),
    Tool(
        name="sdd_run_lifecycle",
        description="Run multiple SDD lifecycle stages in sequence on a document. Stages feed output to the next. Stops on failure.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path. Resolved from session/config default when omitted."},
                "doc_type": {"type": "string", "description": "Document type (e.g. brd, prd)"},
                "layer": {"type": "string", "description": "SDD layer directory (e.g. 01_BRD)"},
                "document": {"type": "string", "description": "Path to document file or directory"},
                "stages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lifecycle stages to run in order (e.g. validate, review, remediate, prescreen, score_validate)",
                },
                "executor": {"type": "string", "description": "Executor for LLM-dependent stages. Use sdd_list_executors to see options."},
                "personas": {"type": "array", "items": {"type": "string"}, "description": "Persona list override for review/create stages. If omitted, loaded from persona_mappings.yaml."},
                "template": {"type": "string", "description": "Template for review/create stages"},
                "out": {"type": "string", "description": "Output directory"},
                "threshold": {"type": "integer", "description": "Score threshold for score_validate stage", "default": 80},
                "clean_before": {"type": "boolean", "description": "Run sdd_clean (keep=0) before starting pipeline. Default: false.", "default": False},
            },
            "required": ["project", "doc_type", "layer", "document", "stages"],
        },
    ),
    # ── LLM-dependent tools ──────────────────────────────────────────────
    Tool(
        name="sdd_create_build",
        description="Assemble LLM creation prompt with personas, template, and layer assets. If executor specified, spawns agent to generate content.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path. Resolved from session/config default when omitted."},
                "personas": {"type": "array", "items": {"type": "string"}, "description": "Persona list override. If omitted, loaded from persona_mappings.yaml."},
                "doc_type": {"type": "string", "description": "Document type (e.g. brd, prd)"},
                "layer": {"type": "string", "description": "SDD layer directory (e.g. 01_BRD)"},
                "template": {"type": "string", "description": "Template file in UCX/prompts/templates/creation"},
                "sections": {"type": "array", "items": {"type": "object"}, "description": "Optional sections JSON array [{section_id, title, content, included?}]"},
                "out": {"type": "string", "description": "Output directory"},
                "executor": {"type": "string", "description": "Executor name. Omit to return prompt text."},
                "timeout": {"type": "integer", "description": "Executor timeout in seconds", "default": 300},
            },
            "required": ["project", "doc_type", "layer", "template"],
        },
    ),
    Tool(
        name="sdd_create",
        description="Create final document artifact at target path. If executor specified, spawns agent to generate content from template.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path. Resolved from session/config default when omitted."},
                "personas": {"type": "array", "items": {"type": "string"}, "description": "Persona list override. If omitted, loaded from persona_mappings.yaml."},
                "doc_type": {"type": "string", "description": "Document type (e.g. brd, prd)"},
                "layer": {"type": "string", "description": "SDD layer directory (e.g. 01_BRD)"},
                "template": {"type": "string", "description": "Template file name"},
                "target": {"type": "string", "description": "Final target document path to create"},
                "overwrite": {"type": "boolean", "description": "Overwrite target if exists", "default": False},
                "sections": {"type": "array", "items": {"type": "object"}, "description": "Optional sections JSON array"},
                "out": {"type": "string", "description": "Output directory for diagnostics"},
                "executor": {"type": "string", "description": "Executor name. Omit for template-only creation."},
                "timeout": {"type": "integer", "description": "Executor timeout in seconds", "default": 300},
            },
            "required": ["project", "doc_type", "layer", "template", "target"],
        },
    ),
    Tool(
        name="sdd_review",
        description="Assemble multi-persona LLM review prompt. If executor specified, spawns agent to perform review.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path. Resolved from session/config default when omitted."},
                "personas": {"type": "array", "items": {"type": "string"}, "description": "Persona list override. If omitted, loaded from persona_mappings.yaml."},
                "doc_type": {"type": "string", "description": "Document type"},
                "template": {"type": "string", "description": "Review template file name"},
                "document": {"type": "string", "description": "Path to document file or directory for auto section loading"},
                "sections": {"type": "array", "items": {"type": "object"}, "description": "Optional explicit sections JSON array"},
                "layer": {"type": "string", "description": "SDD layer directory"},
                "unified": {"type": "boolean", "description": "Enable unified context mode", "default": False},
                "one_turn": {"type": "boolean", "description": "Enable one-turn review mode", "default": False},
                "out": {"type": "string", "description": "Output directory"},
                "executor": {"type": "string", "description": "Executor name. Omit to return prompt text."},
                "timeout": {"type": "integer", "description": "Executor timeout in seconds", "default": 300},
            },
            "required": ["project", "doc_type", "template"],
        },
    ),
    Tool(
        name="sdd_remediate",
        description="Generate deterministic remediation findings and report. With fix=true, generates source-protected derived copy. If executor specified, spawns agent.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path. Resolved from session/config default when omitted."},
                "doc_type": {"type": "string", "description": "Document type"},
                "layer": {"type": "string", "description": "SDD layer directory"},
                "document": {"type": "string", "description": "Path to document file or directory"},
                "review_report": {"type": "string", "description": "Optional path to review report"},
                "remediation_report": {"type": "string", "description": "Path to existing remediation report. With fix=true, skips findings generation and applies fix from this report directly."},
                "out": {"type": "string", "description": "Output directory"},
                "executor": {"type": "string", "description": "Executor name. Omit to return findings/fix report."},
                "timeout": {"type": "integer", "description": "Executor timeout in seconds", "default": 300},
                "fix": {"type": "boolean", "description": "Generate source-protected remediated derived copy after findings.", "default": False},
            },
            "required": ["project", "doc_type", "layer", "document"],
        },
    ),
]

# Tools that accept a "project" parameter — used by handle_tool injection.
_PROJECT_TOOLS: frozenset[str] = frozenset(
    tool.name
    for tool in TOOLS
    if "project" in (tool.inputSchema.get("properties") or {})
)


# ── Helper functions ────────────────────────────────────────────────────────

def _path(arguments: dict, key: str) -> Path:
    return Path(arguments[key]).expanduser().resolve()


def _opt_path(arguments: dict, key: str) -> Path | None:
    val = arguments.get(key)
    return Path(val).expanduser().resolve() if val else None


def _serialize_result(result: object) -> dict:
    """Convert a frozen dataclass result to a JSON-serializable dict."""
    if hasattr(result, "report_json"):
        return json.loads(result.report_json)
    if hasattr(result, "payload") and isinstance(result.payload, dict):
        return result.payload
    if dataclasses.is_dataclass(result) and not isinstance(result, type):
        data = {}
        for f in dataclasses.fields(result):
            val = getattr(result, f.name)
            if isinstance(val, Path):
                data[f.name] = str(val)
            elif isinstance(val, (list, tuple)):
                data[f.name] = [str(v) if isinstance(v, Path) else v for v in val]
            else:
                data[f.name] = val
        return data
    return {"result": str(result)}


def _build_sections(arguments: dict):
    """Reconstruct SourceSection list from JSON array in arguments."""
    from mcp_server.prompts import SourceSection
    sections_raw = arguments.get("sections")
    if not sections_raw:
        return None
    return [
        SourceSection(
            section_id=item["section_id"],
            title=item["title"],
            content=item["content"],
            included=item.get("included", True),
        )
        for item in sections_raw
    ]


async def _maybe_run_executor(
    arguments: dict,
    prompt_text: str,
    deterministic_result: dict,
    working_dir: Path | None = None,
    system_prompt: str | None = None,
    ctx: "ProjectContext | None" = None,
) -> dict:
    """If executor specified, run it with the prompt. Otherwise return prompt text.

    Derives working_dir from the 'document' argument when not explicitly
    provided, so executor output lands in the document's folder.
    """
    executor_name = arguments.get("executor")
    if not executor_name:
        return {
            **deterministic_result,
            "prompt_text": prompt_text,
            "executor": None,
        }

    # Default working_dir to document folder
    if working_dir is None:
        doc_arg = arguments.get("document")
        if doc_arg:
            doc_path = Path(doc_arg).expanduser().resolve()
            working_dir = doc_path if doc_path.is_dir() else doc_path.parent

    # Use context instead of loading env/overrides independently.
    # Empty dict ({}) coerced to None so downstream treats "no env" uniformly.
    project_env = ctx.project_env if ctx and ctx.project_env else None
    project_overrides = ctx.executor_overrides if ctx and ctx.executor_overrides else None

    timeout = arguments.get("timeout", 300)
    exec_result: ExecutorResult = await run_executor(
        name=executor_name,
        prompt=prompt_text,
        working_dir=working_dir,
        timeout=timeout,
        project_env=project_env,
        system_prompt=system_prompt,
        project_overrides=project_overrides,
    )

    return {
        "executor": executor_name,
        "exit_code": exec_result.exit_code,
        "output": exec_result.stdout,
        "stderr": exec_result.stderr if exec_result.stderr else None,
        "prompt_file": None,
        "deterministic_result": deterministic_result,
    }


def _inspect_document_folder(document_dir: Path) -> dict:
    """Inspect a document folder and determine lifecycle state."""
    if not document_dir.is_dir():
        return {"error": f"Not a directory: {document_dir}"}

    md_files = sorted(document_dir.glob("*.md"))
    json_files = sorted(document_dir.glob("*.json"))
    yaml_files = sorted(document_dir.glob("*.yaml")) + sorted(document_dir.glob("*.yml"))
    all_names = [f.name for f in md_files] + [f.name for f in json_files] + [f.name for f in yaml_files]

    from mcp_server.utils.source_files import REPORT_PATTERN

    source_pattern = re.compile(r"^[A-Z]+-\d+_.+\.(md|yaml|yml)$")
    source_files = [f for f in md_files + yaml_files if source_pattern.match(f.name) and "_validated" not in f.stem and "_remediate_copy" not in f.stem and not re.search(r"_remediate_v\d+", f.stem)]
    has_validation_report = any(
        REPORT_PATTERN.match(f.name) and ".validate." in f.name
        for f in json_files + md_files + yaml_files
    )
    has_validation_copy = any(
        "_validated" in f.stem for f in md_files + yaml_files
    )
    has_review_report = any(
        REPORT_PATTERN.match(f.name) and ".review." in f.name
        for f in json_files + md_files
    )
    has_remediation_report = any(
        REPORT_PATTERN.match(f.name) and ".remediate." in f.name
        for f in json_files + md_files
    )
    has_remediated_copy = any(
        "_remediate_copy" in f.stem or re.search(r"_remediate_v\d+", f.stem) for f in md_files + yaml_files
    )

    if has_remediated_copy:
        current_stage = "remediated"
        next_action = "done"
        next_tool = None
    elif has_remediation_report:
        current_stage = "remediation_reported"
        next_action = "remediate --fix"
        next_tool = "sdd_remediate"
    elif has_review_report:
        current_stage = "reviewed"
        next_action = "remediate"
        next_tool = "sdd_remediate"
    elif has_validation_report or has_validation_copy:
        current_stage = "validated"
        next_action = "review"
        next_tool = "sdd_review"
    elif source_files:
        current_stage = "created"
        next_action = "validate"
        next_tool = "sdd_validate"
    else:
        current_stage = "empty"
        next_action = "create"
        next_tool = "sdd_create"

    return {
        "document": str(document_dir),
        "current_stage": current_stage,
        "existing_artifacts": all_names,
        "next_action": next_action,
        "next_tool": next_tool,
    }


# ── Handler dispatch ────────────────────────────────────────────────────────

async def handle_tool(name: str, arguments: dict) -> list[TextContent]:
    """Main tool handler — routes MCP tool calls to runner functions."""
    # Inject resolved default project if not explicitly provided (before logging)
    if name in _PROJECT_TOOLS and not arguments.get("project"):
        from mcp_server.project_context import resolve_project
        try:
            resolved = resolve_project(None)
            arguments["project"] = str(resolved)
        except ValueError:
            pass  # Let individual tool handlers raise on missing project

    # Configure logging if project root is available
    project_arg = arguments.get("project")
    if project_arg:
        configure_logging(Path(project_arg).expanduser().resolve())

    start = log_tool_call(
        tool=name,
        arguments=arguments,
        project_root=Path(project_arg) if project_arg else None,
    )
    try:
        result = await _dispatch(name, arguments)
        # Extract summary counts if available
        summary = result.get("summary", result.get("report", {}).get("summary", {}))
        if isinstance(summary, dict):
            log_tool_result(
                tool=name,
                start_time=start,
                errors=summary.get("errors", 0) if isinstance(summary.get("errors"), int) else 0,
                warnings=summary.get("warnings", 0) if isinstance(summary.get("warnings"), int) else 0,
                passes=summary.get("passes", 0) if isinstance(summary.get("passes"), int) else 0,
                is_valid=summary.get("is_valid"),
            )
        else:
            log_tool_result(tool=name, start_time=start)
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
    except Exception as e:
        log_tool_result(tool=name, start_time=start, errors=1)
        return [TextContent(type="text", text=json.dumps({"error": str(e), "tool": name}))]


async def _dispatch(name: str, arguments: dict) -> dict:
    """Dispatch to the appropriate handler."""
    from mcp_server.project_context import ProjectContext
    ctx = ProjectContext.resolve(arguments.get("project"))

    # ── Session management tools ───────────────────────────────────────

    if name == "sdd_set_project":
        from mcp_server.project_context import set_session_project, clear_session_project
        project_val = arguments.get("project", "")
        if not project_val:
            clear_session_project()
            return {"cleared": True, "session_project": None}
        project_root = _path(arguments, "project")
        return set_session_project(project_root)

    if name == "sdd_get_project":
        from mcp_server.project_context import get_session_project, resolve_project
        session = get_session_project()
        try:
            resolved = resolve_project(None)
            source = "session" if session else "config"
        except ValueError:
            resolved = None
            source = "none"
        return {
            "session_project": str(session) if session else None,
            "resolved_project": str(resolved) if resolved else None,
            "source": source,
        }

    # ── Deprecated aliases ───────────────────────────────────────────────

    if name == "sdd_validate_fix":
        import warnings
        warnings.warn("sdd_validate_fix is deprecated. Use sdd_validate.", DeprecationWarning, stacklevel=2)
        name = "sdd_validate"

    # ── Deterministic tools ──────────────────────────────────────────────

    if name == "sdd_init":
        from mcp_server.skills.scaffold import scaffold_project_ucx
        result = scaffold_project_ucx(
            project_root=ctx.project_root,
            force_update=bool(arguments.get("update", False)),
            force_update_mappings=bool(arguments.get("update_mappings", False)),
        )
        return _serialize_result(result)

    if name == "sdd_validate":
        from mcp_server.validation import run_project_validation_build
        from mcp_server.remediation import run_validate_fix_build
        from mcp_server.core.stage_output import STAGE_VALIDATE, resolve_stage_output_dir

        project_root = ctx.project_root
        document_path = _path(arguments, "document")
        output_dir = resolve_stage_output_dir(
            stage=STAGE_VALIDATE,
            project_root=project_root,
            output_dir=_opt_path(arguments, "out"),
            document_dir=document_path if document_path.is_dir() else document_path.parent,
        )

        # --- Phase 1: Validate (or load existing report) ---
        existing_report = _opt_path(arguments, "validation_report")
        if existing_report and existing_report.exists():
            report_data = json.loads(existing_report.read_text(encoding="utf-8"))
            errors = report_data.get("errors", [])
            warnings = report_data.get("warnings", [])
            report_path = existing_report
            summary_path = None
        else:
            result = run_project_validation_build(
                project_root=project_root,
                doc_type=arguments["doc_type"],
                layer=arguments["layer"],
                document_path=document_path,
                output_dir=output_dir,
            )
            payload = result.report
            errors = payload.get("errors", []) if isinstance(payload, dict) else []
            warnings = payload.get("warnings", []) if isinstance(payload, dict) else []
            report_path = result.report_path
            summary_path = result.summary_path

        if not isinstance(errors, list):
            errors = []
        if not isinstance(warnings, list):
            warnings = []

        tier1_only = arguments.get("tier1_only", False)
        strict = arguments.get("strict", False)

        if tier1_only:
            effective_errors = [
                item for item in errors
                if isinstance(item, str)
                and (item.startswith("Missing required custom field") or item.startswith("Missing required tag"))
            ]
        else:
            effective_errors = [item for item in errors if isinstance(item, str)]

        effective_warnings = [item for item in warnings if isinstance(item, str)]
        is_valid = len(effective_errors) == 0 and (not strict or len(effective_warnings) == 0)

        # --- Phase 2: Fix (conditional — only when validation fails) ---
        fix_generated = False
        fix_response: dict[str, object] = {}
        fix_result = None
        if not is_valid:
            try:
                fix_result = run_validate_fix_build(
                    project_root=project_root,
                    doc_type=arguments["doc_type"],
                    layer=arguments["layer"],
                    document_path=document_path,
                    validation_report=report_path,
                    output_dir=output_dir,
                )
                fix_response = {
                    "fix_generated": True,
                    "fix_report_path": str(fix_result.report_path) if fix_result.report_path else None,
                    "fix_summary_path": str(fix_result.summary_path) if fix_result.summary_path else None,
                    "derived_paths": [str(p) for p in fix_result.derived_paths],
                }
                fix_generated = True
            except (FileNotFoundError, ValueError) as exc:
                fix_response = {"fix_generated": False, "fix_error": str(exc)}

        response = {
            "report_path": str(report_path) if report_path else None,
            "summary_path": str(summary_path) if summary_path else None,
            "tier1_only": tier1_only,
            "strict": strict,
            "errors": effective_errors,
            "warnings": effective_warnings,
            "is_valid": is_valid,
            "passed": True,
            "fix_generated": fix_generated,
            **fix_response,
        }

        if fix_generated and arguments.get("executor") and fix_result is not None:
            exec_response = await _maybe_run_executor(
                arguments, fix_result.report_text, response, working_dir=project_root,
                ctx=ctx,
            )
            exec_response["passed"] = True
            exec_response["is_valid"] = is_valid
            exec_response["fix_generated"] = True

            return exec_response
        return response

    if name == "sdd_validate_chg":
        from mcp_server.validation import run_project_validation_build
        from mcp_server.core.stage_output import STAGE_VALIDATE, resolve_stage_output_dir

        project_root = ctx.project_root
        document_path = _path(arguments, "document")
        output_dir = resolve_stage_output_dir(
            stage=STAGE_VALIDATE,
            project_root=project_root,
            output_dir=_opt_path(arguments, "out"),
            document_dir=document_path if document_path.is_dir() else document_path.parent,
        )

        result = run_project_validation_build(
            project_root=project_root,
            doc_type="chg",
            layer=arguments["layer"],
            document_path=document_path,
            output_dir=output_dir,
        )
        payload = result.report
        return {
            "report_path": str(result.report_path) if result.report_path else None,
            "summary_path": str(result.summary_path) if result.summary_path else None,
            "errors": payload.get("errors", []) if isinstance(payload, dict) else [],
            "warnings": payload.get("warnings", []) if isinstance(payload, dict) else [],
            "passes": payload.get("passes", []) if isinstance(payload, dict) else [],
            "is_valid": result.is_valid,
            "passed": result.is_valid,
            "report": payload,
        }

    if name == "sdd_consistency":
        from mcp_server.consistency import run_consistency_check
        result = run_consistency_check(
            target_path=_path(arguments, "target"),
            output_dir=_opt_path(arguments, "out"),
        )
        return {
            "passed": result.passed,
            "report": json.loads(result.report_json),
            "report_path": str(result.report_path) if result.report_path else None,
        }

    if name == "sdd_validate_links":
        from mcp_server.link_validation import run_link_validation
        result = run_link_validation(
            target_path=_path(arguments, "target"),
            workspace_root=_opt_path(arguments, "workspace_root"),
            output_dir=_opt_path(arguments, "out"),
        )
        return {
            "passed": result.passed,
            "report": json.loads(result.report_json),
            "report_path": str(result.report_path) if result.report_path else None,
        }

    if name == "sdd_preflight":
        from mcp_server.preflight import run_preflight
        result = run_preflight(
            project_root=ctx.project_root,
            context=arguments.get("context", "any"),
            document_path=_opt_path(arguments, "document"),
            output_dir=_opt_path(arguments, "out"),
        )
        return {
            "status": result.status,
            "report": json.loads(result.report_json),
            "report_path": str(result.report_path) if result.report_path else None,
        }

    if name == "sdd_personas_show":
        from mcp_server.skills.persona_manager import show_persona_mappings
        return show_persona_mappings(
            project_root=ctx.project_root,
            phase=arguments.get("phase"),
            doc_type=arguments.get("doc_type"),
        )

    if name == "sdd_personas_set":
        from mcp_server.skills.persona_manager import set_persona_mapping
        return set_persona_mapping(
            project_root=ctx.project_root,
            phase=arguments["phase"],
            doc_type=arguments["doc_type"],
            personas=arguments["personas"],
        )

    if name == "sdd_personas_diff":
        from mcp_server.skills.persona_manager import diff_persona_mappings
        return diff_persona_mappings(
            project_root=ctx.project_root,
        )

    if name == "sdd_env_show":
        from mcp_server.env_manager import show_project_env
        return show_project_env(
            project_root=ctx.project_root,
        )

    if name == "sdd_prescreen":
        from mcp_server.prescreening import run_prescreen
        result = run_prescreen(
            document_path=_path(arguments, "document"),
            output_dir=_opt_path(arguments, "out"),
        )
        return json.loads(result.report_json)

    if name == "sdd_scan":
        from mcp_server.scan import run_scan
        result = run_scan(
            report_file=_path(arguments, "report_file"),
            output_dir=_opt_path(arguments, "out"),
        )
        return json.loads(result.report_json)

    if name == "sdd_score_show":
        from mcp_server.scoring import show_score
        result = show_score(report_file=_path(arguments, "report_file"))
        return result.payload

    if name == "sdd_score_validate":
        from mcp_server.scoring import validate_score
        result = validate_score(
            report_file=_path(arguments, "report_file"),
            threshold=int(arguments["threshold"]),
        )
        return result.payload

    if name == "sdd_score_compare":
        from mcp_server.scoring import compare_scores
        result = compare_scores(
            baseline_report_file=_path(arguments, "baseline_report_file"),
            candidate_report_file=_path(arguments, "candidate_report_file"),
        )
        return result.payload

    if name == "sdd_list_executors":
        executors = list_executors()
        exec_list = [
            {
                "name": e.name,
                "executor_type": e.executor_type.value,
                "command": e.command if e.executor_type == ExecutorType.CLI else None,
                "model": e.model if e.executor_type == ExecutorType.API else None,
                "status": e.status,
                "timeout": e.timeout,
                "source": "global",
            }
            for e in executors
        ]

        # Merge project overrides if project provided
        if ctx and ctx.executor_overrides:
            project_names: set[str] = set()
            for e in ctx.executor_overrides.values():
                project_names.add(e.name)
                exec_list.append({
                    "name": e.name,
                    "executor_type": e.executor_type.value,
                    "command": e.command if e.executor_type == ExecutorType.CLI else None,
                    "model": e.model if e.executor_type == ExecutorType.API else None,
                    "status": e.status,
                    "timeout": e.timeout,
                    "source": "project",
                })
            # Mark global entries that are overridden
            for item in exec_list:
                if item.get("source") != "project" and item["name"] in project_names:
                    item["overridden_by_project"] = True

        return {"executors": exec_list}

    if name == "sdd_register_executor":
        config = ExecutorConfig(
            name=arguments["name"],
            executor_type=ExecutorType(arguments["executor_type"]),
            command=arguments.get("command", ""),
            args=arguments.get("args", []),
            prompt_mode=arguments.get("prompt_mode", ""),
            model=arguments.get("model", ""),
            api_base=arguments.get("api_base", ""),
            api_key_env=arguments.get("api_key_env", ""),
            timeout=arguments.get("timeout", 300),
        )
        register_executor(config)
        return {"registered": config.name, "executor_type": config.executor_type.value}

    # ── Orchestration tools ──────────────────────────────────────────────

    if name == "sdd_next_action":
        document_dir = _path(arguments, "document")
        if not document_dir.is_dir():
            document_dir = document_dir.parent
        return _inspect_document_folder(document_dir)

    if name == "sdd_run_lifecycle":
        return await _handle_lifecycle_pipeline(arguments)

    # ── LLM-dependent tools ──────────────────────────────────────────────

    if name == "sdd_create_build":
        from mcp_server.review import run_project_creation_build
        from mcp_server.core.stage_output import STAGE_CREATE, resolve_stage_output_dir
        project_root = ctx.project_root
        output_dir = resolve_stage_output_dir(
            stage=STAGE_CREATE,
            project_root=project_root,
            output_dir=_opt_path(arguments, "out"),
            document_dir=None,
        )
        result = run_project_creation_build(
            project_root=project_root,
            personas=arguments.get("personas"),
            doc_type=arguments["doc_type"],
            layer=arguments["layer"],
            template_name=arguments["template"],
            sections=_build_sections(arguments),
            output_dir=output_dir,
        )
        det_result = _serialize_result(result)
        return await _maybe_run_executor(
            arguments, result.prompt_text, det_result, working_dir=project_root,
            ctx=ctx,
        )

    if name == "sdd_create":
        from mcp_server.review import run_project_creation_artifact
        from mcp_server.core.stage_output import STAGE_CREATE, resolve_stage_output_dir
        project_root = ctx.project_root
        target_path = _path(arguments, "target")
        output_dir = resolve_stage_output_dir(
            stage=STAGE_CREATE,
            project_root=project_root,
            output_dir=_opt_path(arguments, "out"),
            document_dir=target_path.parent,
        )
        result = run_project_creation_artifact(
            project_root=project_root,
            personas=arguments.get("personas"),
            doc_type=arguments["doc_type"],
            layer=arguments["layer"],
            template_name=arguments["template"],
            target_path=target_path,
            sections=_build_sections(arguments),
            output_dir=output_dir,
            overwrite=arguments.get("overwrite", False),
        )
        return _serialize_result(result)

    if name == "sdd_review":
        from mcp_server.review import run_project_review_build
        from mcp_server.core.stage_output import STAGE_REVIEW, resolve_stage_output_dir
        project_root = ctx.project_root
        document_path = _opt_path(arguments, "document")
        sections = _build_sections(arguments)

        if sections is None and document_path is not None:
            from mcp_server.cli.main import _build_review_sections_from_document
            sections, _ = _build_review_sections_from_document(document_path)

        if sections is None:
            return {"error": "Provide either 'sections' or 'document' parameter"}

        doc_dir = document_path if document_path and document_path.is_dir() else (document_path.parent if document_path else None)
        output_dir = resolve_stage_output_dir(
            stage=STAGE_REVIEW,
            project_root=project_root,
            output_dir=_opt_path(arguments, "out"),
            document_dir=doc_dir,
        )
        result = run_project_review_build(
            project_root=project_root,
            personas=arguments.get("personas"),
            doc_type=arguments["doc_type"],
            template_name=arguments["template"],
            sections=sections,
            layer=arguments.get("layer"),
            output_dir=output_dir,
        )
        det_result = _serialize_result(result)
        exec_response = await _maybe_run_executor(
            arguments, result.prompt_text, det_result, working_dir=project_root,
            system_prompt=getattr(result, "system_prompt", None),
            ctx=ctx,
        )

        # Persist executor review output to document folder (UCX_v1 parity).
        if exec_response.get("executor") and exec_response.get("exit_code") == 0:
            executor_output = exec_response.get("output", "")
            if executor_output and output_dir is not None and document_path is not None:
                from mcp_server.utils.source_files import extract_doc_id
                doc_id = extract_doc_id(document_path)
                output_dir.mkdir(parents=True, exist_ok=True)
                review_report_path = output_dir / f"{doc_id}.ucx.review.md"
                review_report_path.write_text(executor_output, encoding="utf-8")
                exec_response["review_report_path"] = str(review_report_path)

        return exec_response

    if name == "sdd_remediate":
        from mcp_server.remediation import run_remediation_build
        from mcp_server.core.stage_output import STAGE_REMEDIATE, resolve_stage_output_dir
        project_root = ctx.project_root
        document_path = _path(arguments, "document")
        output_dir = resolve_stage_output_dir(
            stage=STAGE_REMEDIATE,
            project_root=project_root,
            output_dir=_opt_path(arguments, "out"),
            document_dir=document_path if document_path.is_dir() else document_path.parent,
        )
        # Path A: Direct fix from existing remediation report (skip findings)
        if arguments.get("fix") and arguments.get("remediation_report"):
            from mcp_server.remediation import run_remediate_fix_build
            fix_result = run_remediate_fix_build(
                project_root=project_root,
                doc_type=arguments["doc_type"],
                layer=arguments["layer"],
                document_path=document_path,
                remediation_report=_opt_path(arguments, "remediation_report"),
                output_dir=output_dir,
            )
            fix_det = _serialize_result(fix_result)
            fix_response = await _maybe_run_executor(
                arguments, fix_result.report_text, fix_det, working_dir=project_root,
                ctx=ctx,
            )
            # Post-fix quality check
            derived_paths = fix_det.get("derived_paths", [])
            if derived_paths and document_path:
                from mcp_server.remediation.runner import verify_remediation_quality
                derived_p = Path(derived_paths[0])
                if derived_p.exists():
                    quality = verify_remediation_quality(
                        original_path=document_path,
                        remediated_path=derived_p,
                        finding_count=0,
                    )
                    fix_response["remediation_quality"] = quality
            return fix_response

        # Path B: Generate findings (always)
        result = run_remediation_build(
            project_root=project_root,
            doc_type=arguments["doc_type"],
            layer=arguments["layer"],
            document_path=document_path,
            review_report=_opt_path(arguments, "review_report"),
            output_dir=output_dir,
        )
        det_result = _serialize_result(result)
        remediate_response = await _maybe_run_executor(
            arguments, result.report_text, det_result, working_dir=project_root,
            system_prompt=getattr(result, "system_prompt", None),
            ctx=ctx,
        )

        # Path C: Auto-chain into fix after findings (fix=true, no existing report)
        if arguments.get("fix"):
            from mcp_server.remediation import run_remediate_fix_build as _run_fix
            try:
                fix_result = _run_fix(
                    project_root=project_root,
                    doc_type=arguments["doc_type"],
                    layer=arguments["layer"],
                    document_path=document_path,
                    remediation_report=result.report_path,
                    output_dir=output_dir,
                )
                fix_det = _serialize_result(fix_result)
                fix_response = await _maybe_run_executor(
                    arguments, fix_result.report_text, fix_det, working_dir=project_root,
                    ctx=ctx,
                )
                remediate_response["fix_result"] = fix_response
                # Post-fix quality check
                derived_paths = fix_det.get("derived_paths", [])
                if derived_paths and document_path:
                    from mcp_server.remediation.runner import verify_remediation_quality
                    derived_p = Path(derived_paths[0])
                    if derived_p.exists():
                        quality = verify_remediation_quality(
                            original_path=document_path,
                            remediated_path=derived_p,
                            finding_count=len(det_result.get("findings", [])),
                        )
                        remediate_response["fix_result"]["remediation_quality"] = quality
            except (FileNotFoundError, ValueError) as exc:
                remediate_response["fix_result"] = {"error": str(exc)}

        return remediate_response

    if name == "sdd_clean":
        from mcp_server.cleanup.runner import run_clean
        document_path = _path(arguments, "document")
        stages = arguments.get("stages", ["all"])
        keep = arguments.get("keep", 1)
        dry_run = arguments.get("dry_run", True)
        result = run_clean(
            document_path=document_path,
            stages=stages,
            keep=keep,
            dry_run=dry_run,
        )
        return {
            "dry_run": result.dry_run,
            "deleted": result.deleted,
            "deleted_count": len(result.deleted),
            "kept": result.kept,
            "kept_count": len(result.kept),
            "bytes_freed": result.total_bytes_freed,
        }

    raise ValueError(f"Unknown tool: {name}")


async def _handle_lifecycle_pipeline(arguments: dict) -> dict:
    """Run multiple lifecycle stages in sequence."""
    stages = arguments["stages"]
    results: dict[str, dict] = {}

    # Optional pre-clean: remove all stage artifacts before pipeline starts
    if arguments.get("clean_before"):
        from mcp_server.cleanup.runner import run_clean
        doc_path = _path(arguments, "document")
        clean_result = run_clean(document_path=doc_path, stages=["all"], keep=0, dry_run=False)
        results["_clean_before"] = {
            "deleted_count": len(clean_result.deleted),
            "bytes_freed": clean_result.total_bytes_freed,
        }

    stage_handlers = {
        "validate": "sdd_validate",
        "validate_fix": "sdd_validate",  # Deprecated — absorbed into validate
        "review": "sdd_review",
        "remediate": "sdd_remediate",
        "remediate_fix": "sdd_remediate",  # Absorbed — routed as sdd_remediate with fix=true
        "prescreen": "sdd_prescreen",
        "score_validate": "sdd_score_validate",
    }

    for stage in stages:
        stage_args = {
            k: v for k, v in arguments.items()
            if k not in ("stages",) and v is not None
        }

        if stage == "score_validate":
            validate_result = results.get("validate", {})
            report_path = validate_result.get("report_path")
            if not report_path:
                results[stage] = {
                    "skipped": True,
                    "reason": "score_validate requires validate stage report_path",
                }
                continue
            score_args = {
                "report_file": report_path,
                "threshold": stage_args.get("threshold", 80),
            }
            try:
                stage_result = await _dispatch("sdd_score_validate", score_args)
                results[stage] = stage_result
                if stage_result.get("passed") is False:
                    results["_stopped_at"] = stage
                    results["_reason"] = "Stage failed"
                    break
            except Exception as e:
                results[stage] = {"error": str(e)}
                results["_stopped_at"] = stage
                results["_reason"] = str(e)
                break
            continue

        tool_name = stage_handlers.get(stage)
        if tool_name is None:
            results[stage] = {"skipped": True, "reason": f"Stage '{stage}' not supported in pipeline"}
            continue

        # Skip validate_fix if validate already produced fix output
        if stage == "validate_fix" and "validate" in results:
            results[stage] = {**results["validate"], "_absorbed": True}
            continue

        # Inject fix=true for remediate_fix stage (absorbed into sdd_remediate)
        if stage == "remediate_fix":
            stage_args["fix"] = True

        try:
            stage_result = await _dispatch(tool_name, stage_args)
            results[stage] = stage_result

            failed = stage_result.get("passed") is False
            has_error = "error" in stage_result
            exit_code = stage_result.get("exit_code", 0)
            if failed or has_error or (isinstance(exit_code, int) and exit_code != 0):
                results["_stopped_at"] = stage
                results["_reason"] = "Stage failed"
                break

            # Post-fix verification: auto-validate derived copy after remediate_fix
            if stage == "remediate_fix":
                fix_result = stage_result.get("fix_result", stage_result)
                derived_paths = fix_result.get("derived_paths", [])
                if derived_paths:
                    verify_args = {
                        k: v for k, v in stage_args.items()
                        if k in ("project", "doc_type", "layer")
                    }
                    verify_args["document"] = derived_paths[0]
                    try:
                        verify_result = await _dispatch("sdd_validate", verify_args)
                        results["post_remediation_verify"] = verify_result
                    except Exception as ve:
                        results["post_remediation_verify"] = {
                            "error": str(ve),
                            "note": "Post-fix validation failed but remediate_fix output is still available",
                        }

        except Exception as e:
            results[stage] = {"error": str(e)}
            results["_stopped_at"] = stage
            results["_reason"] = str(e)
            break

    results["_completed_stages"] = [s for s in stages if s in results and "error" not in results.get(s, {})]
    return results
