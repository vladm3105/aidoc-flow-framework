"""MCP Tool definitions and handler dispatch for SDD lifecycle.

20 tools total:
  - 12 deterministic (execute directly)
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
    # ── Deterministic tools ──────────────────────────────────────────────
    Tool(
        name="sdd_init",
        description="Scaffold project-specific UCX assets (personas, templates, schemas, prompts) under UCX/",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path"},
            },
            "required": ["project"],
        },
    ),
    Tool(
        name="sdd_validate",
        description="Run script-based structural validation against layer schema/template assets. Returns pass/fail with error details.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path"},
                "doc_type": {"type": "string", "description": "Document type (e.g. brd, prd, ears)"},
                "layer": {"type": "string", "description": "SDD layer directory (e.g. 01_BRD)"},
                "document": {"type": "string", "description": "Path to document file or directory"},
                "tier1_only": {"type": "boolean", "description": "Evaluate only tier1 blocking checks", "default": False},
                "strict": {"type": "boolean", "description": "Treat warnings as failures", "default": False},
                "format": {"type": "string", "enum": ["text", "json"], "description": "Output format", "default": "json"},
                "out": {"type": "string", "description": "Output directory for reports"},
            },
            "required": ["project", "doc_type", "layer", "document"],
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
                "project": {"type": "string", "description": "Project root path"},
                "context": {"type": "string", "enum": ["create", "review", "remediate", "any"], "default": "any"},
                "document": {"type": "string", "description": "Optional document path to verify"},
                "format": {"type": "string", "enum": ["text", "json"], "default": "json"},
                "out": {"type": "string", "description": "Output directory"},
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
        description="List all registered CLI and API executors with their type, status, and configuration.",
        inputSchema={
            "type": "object",
            "properties": {},
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
                "project": {"type": "string", "description": "Project root path"},
                "doc_type": {"type": "string", "description": "Document type (e.g. brd, prd)"},
                "layer": {"type": "string", "description": "SDD layer directory (e.g. 01_BRD)"},
                "document": {"type": "string", "description": "Path to document file or directory"},
                "stages": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["create", "validate", "validate_fix", "review", "remediate", "remediate_fix"]},
                    "description": "Lifecycle stages to run in order",
                },
                "executor": {"type": "string", "description": "Executor for LLM-dependent stages. Use sdd_list_executors to see options."},
                "persona": {"type": "string", "description": "Persona for review/create stages"},
                "template": {"type": "string", "description": "Template for review/create stages"},
                "out": {"type": "string", "description": "Output directory"},
            },
            "required": ["project", "doc_type", "layer", "document", "stages"],
        },
    ),
    # ── LLM-dependent tools ──────────────────────────────────────────────
    Tool(
        name="sdd_create_build",
        description="Assemble LLM creation prompt with persona, template, and layer assets. If executor specified, spawns agent to generate content.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path"},
                "persona": {"type": "string", "description": "Persona file name without extension"},
                "doc_type": {"type": "string", "description": "Document type (e.g. brd, prd)"},
                "layer": {"type": "string", "description": "SDD layer directory (e.g. 01_BRD)"},
                "template": {"type": "string", "description": "Template file in UCX/prompts/templates/creation"},
                "sections": {"type": "array", "items": {"type": "object"}, "description": "Optional sections JSON array [{section_id, title, content, included?}]"},
                "out": {"type": "string", "description": "Output directory"},
                "executor": {"type": "string", "description": "Executor name. Omit to return prompt text."},
                "timeout": {"type": "integer", "description": "Executor timeout in seconds", "default": 300},
            },
            "required": ["project", "persona", "doc_type", "layer", "template"],
        },
    ),
    Tool(
        name="sdd_create",
        description="Create final document artifact at target path. If executor specified, spawns agent to generate content from template.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path"},
                "persona": {"type": "string", "description": "Persona file name without extension"},
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
            "required": ["project", "persona", "doc_type", "layer", "template", "target"],
        },
    ),
    Tool(
        name="sdd_review",
        description="Assemble multi-persona LLM review prompt. If executor specified, spawns agent to perform review.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path"},
                "persona": {"type": "string", "description": "Persona file name without extension"},
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
            "required": ["project", "persona", "doc_type", "template"],
        },
    ),
    Tool(
        name="sdd_validate_fix",
        description="Generate source-protected validation derived copy. If executor specified, spawns agent to apply fixes.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path"},
                "doc_type": {"type": "string", "description": "Document type"},
                "layer": {"type": "string", "description": "SDD layer directory"},
                "document": {"type": "string", "description": "Path to document file or directory"},
                "validation_report": {"type": "string", "description": "Optional path to validation report"},
                "out": {"type": "string", "description": "Output directory"},
                "executor": {"type": "string", "description": "Executor name. Omit to return fix report."},
                "timeout": {"type": "integer", "description": "Executor timeout in seconds", "default": 300},
            },
            "required": ["project", "doc_type", "layer", "document"],
        },
    ),
    Tool(
        name="sdd_remediate",
        description="Generate deterministic remediation findings and report. If executor specified, spawns agent with remediation prompt.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path"},
                "doc_type": {"type": "string", "description": "Document type"},
                "layer": {"type": "string", "description": "SDD layer directory"},
                "document": {"type": "string", "description": "Path to document file or directory"},
                "review_report": {"type": "string", "description": "Optional path to review report"},
                "out": {"type": "string", "description": "Output directory"},
                "executor": {"type": "string", "description": "Executor name. Omit to return findings."},
                "timeout": {"type": "integer", "description": "Executor timeout in seconds", "default": 300},
            },
            "required": ["project", "doc_type", "layer", "document"],
        },
    ),
    Tool(
        name="sdd_remediate_fix",
        description="Generate source-protected remediated derived copy. If executor specified, spawns agent to apply fixes.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project root path"},
                "doc_type": {"type": "string", "description": "Document type"},
                "layer": {"type": "string", "description": "SDD layer directory"},
                "document": {"type": "string", "description": "Path to document file or directory"},
                "remediation_report": {"type": "string", "description": "Optional path to remediation report"},
                "out": {"type": "string", "description": "Output directory"},
                "executor": {"type": "string", "description": "Executor name. Omit to return fix report."},
                "timeout": {"type": "integer", "description": "Executor timeout in seconds", "default": 300},
            },
            "required": ["project", "doc_type", "layer", "document"],
        },
    ),
]


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

    timeout = arguments.get("timeout", 300)
    exec_result: ExecutorResult = await run_executor(
        name=executor_name,
        prompt=prompt_text,
        working_dir=working_dir,
        timeout=timeout,
    )

    return {
        "executor": executor_name,
        "exit_code": exec_result.exit_code,
        "output": exec_result.stdout,
        "stderr": exec_result.stderr if exec_result.stderr else None,
        "prompt_file": exec_result.prompt_file,
        "deterministic_result": deterministic_result,
    }


def _inspect_document_folder(document_dir: Path) -> dict:
    """Inspect a document folder and determine lifecycle state."""
    if not document_dir.is_dir():
        return {"error": f"Not a directory: {document_dir}"}

    md_files = sorted(document_dir.glob("*.md"))
    json_files = sorted(document_dir.glob("*.json"))
    yaml_files = sorted(document_dir.glob("*.yaml"))
    all_names = [f.name for f in md_files] + [f.name for f in json_files] + [f.name for f in yaml_files]

    from mcp_server.utils.source_files import REPORT_PATTERN

    source_pattern = re.compile(r"^[A-Z]+-\d+_.+\.(md|yaml|yml)$")
    source_files = [f for f in md_files + yaml_files if source_pattern.match(f.name) and "_validate_copy" not in f.stem and "_remediate_copy" not in f.stem]
    has_validation_report = any(
        REPORT_PATTERN.match(f.name) and ".validate." in f.name
        for f in json_files + md_files + yaml_files
    )
    has_validation_copy = any(
        "_validate_copy" in f.stem for f in md_files + yaml_files
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
        "_remediate_copy" in f.stem for f in md_files + yaml_files
    )

    if has_remediated_copy:
        current_stage = "remediated"
        next_action = "done"
        next_tool = None
    elif has_remediation_report:
        current_stage = "remediation_reported"
        next_action = "remediate_fix"
        next_tool = "sdd_remediate_fix"
    elif has_review_report:
        current_stage = "reviewed"
        next_action = "remediate"
        next_tool = "sdd_remediate"
    elif has_validation_copy:
        current_stage = "validation_fixed"
        next_action = "review"
        next_tool = "sdd_review"
    elif has_validation_report:
        current_stage = "validated"
        next_action = "validate_fix"
        next_tool = "sdd_validate_fix"
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

    # ── Deterministic tools ──────────────────────────────────────────────

    if name == "sdd_init":
        from mcp_server.skills.scaffold import scaffold_project_ucx
        result = scaffold_project_ucx(project_root=_path(arguments, "project"))
        return _serialize_result(result)

    if name == "sdd_validate":
        from mcp_server.validation import run_project_validation_build
        from mcp_server.core.stage_output import STAGE_VALIDATE, resolve_stage_output_dir
        project_root = _path(arguments, "project")
        document_path = _path(arguments, "document")
        output_dir = resolve_stage_output_dir(
            stage=STAGE_VALIDATE,
            project_root=project_root,
            output_dir=_opt_path(arguments, "out"),
            document_dir=document_path if document_path.is_dir() else document_path.parent,
        )
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
        failed = len(effective_errors) > 0 or (strict and len(effective_warnings) > 0)

        return {
            "report_path": str(result.report_path) if result.report_path else None,
            "summary_path": str(result.summary_path) if result.summary_path else None,
            "tier1_only": tier1_only,
            "strict": strict,
            "errors": effective_errors,
            "warnings": effective_warnings,
            "passed": not failed,
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
            project_root=_path(arguments, "project"),
            context=arguments.get("context", "any"),
            document_path=_opt_path(arguments, "document"),
            output_dir=_opt_path(arguments, "out"),
        )
        return {
            "status": result.status,
            "report": json.loads(result.report_json),
            "report_path": str(result.report_path) if result.report_path else None,
        }

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
        return {
            "executors": [
                {
                    "name": e.name,
                    "executor_type": e.executor_type.value,
                    "command": e.command if e.executor_type == ExecutorType.CLI else None,
                    "model": e.model if e.executor_type == ExecutorType.API else None,
                    "status": e.status,
                    "timeout": e.timeout,
                }
                for e in executors
            ]
        }

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
        project_root = _path(arguments, "project")
        output_dir = resolve_stage_output_dir(
            stage=STAGE_CREATE,
            project_root=project_root,
            output_dir=_opt_path(arguments, "out"),
            document_dir=None,
        )
        result = run_project_creation_build(
            project_root=project_root,
            persona=arguments["persona"],
            doc_type=arguments["doc_type"],
            layer=arguments["layer"],
            template_name=arguments["template"],
            sections=_build_sections(arguments),
            output_dir=output_dir,
        )
        det_result = _serialize_result(result)
        return await _maybe_run_executor(
            arguments, result.prompt_text, det_result, working_dir=project_root,
        )

    if name == "sdd_create":
        from mcp_server.review import run_project_creation_artifact
        from mcp_server.core.stage_output import STAGE_CREATE, resolve_stage_output_dir
        project_root = _path(arguments, "project")
        target_path = _path(arguments, "target")
        output_dir = resolve_stage_output_dir(
            stage=STAGE_CREATE,
            project_root=project_root,
            output_dir=_opt_path(arguments, "out"),
            document_dir=target_path.parent,
        )
        result = run_project_creation_artifact(
            project_root=project_root,
            persona=arguments["persona"],
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
        project_root = _path(arguments, "project")
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
            persona=arguments["persona"],
            doc_type=arguments["doc_type"],
            template_name=arguments["template"],
            sections=sections,
            layer=arguments.get("layer"),
            output_dir=output_dir,
        )
        det_result = _serialize_result(result)
        return await _maybe_run_executor(
            arguments, result.prompt_text, det_result, working_dir=project_root,
        )

    if name == "sdd_validate_fix":
        from mcp_server.remediation import run_validate_fix_build
        from mcp_server.core.stage_output import STAGE_VALIDATE, resolve_stage_output_dir
        project_root = _path(arguments, "project")
        document_path = _path(arguments, "document")
        output_dir = resolve_stage_output_dir(
            stage=STAGE_VALIDATE,
            project_root=project_root,
            output_dir=_opt_path(arguments, "out"),
            document_dir=document_path if document_path.is_dir() else document_path.parent,
        )
        result = run_validate_fix_build(
            project_root=project_root,
            doc_type=arguments["doc_type"],
            layer=arguments["layer"],
            document_path=document_path,
            validation_report=_opt_path(arguments, "validation_report"),
            output_dir=output_dir,
        )
        det_result = _serialize_result(result)
        return await _maybe_run_executor(
            arguments, result.report_text, det_result, working_dir=project_root,
        )

    if name == "sdd_remediate":
        from mcp_server.remediation import run_remediation_build
        from mcp_server.core.stage_output import STAGE_REMEDIATE, resolve_stage_output_dir
        project_root = _path(arguments, "project")
        document_path = _path(arguments, "document")
        output_dir = resolve_stage_output_dir(
            stage=STAGE_REMEDIATE,
            project_root=project_root,
            output_dir=_opt_path(arguments, "out"),
            document_dir=document_path if document_path.is_dir() else document_path.parent,
        )
        result = run_remediation_build(
            project_root=project_root,
            doc_type=arguments["doc_type"],
            layer=arguments["layer"],
            document_path=document_path,
            review_report=_opt_path(arguments, "review_report"),
            output_dir=output_dir,
        )
        det_result = _serialize_result(result)
        return await _maybe_run_executor(
            arguments, result.report_text, det_result, working_dir=project_root,
        )

    if name == "sdd_remediate_fix":
        from mcp_server.remediation import run_remediate_fix_build
        from mcp_server.core.stage_output import STAGE_REMEDIATE, resolve_stage_output_dir
        project_root = _path(arguments, "project")
        document_path = _path(arguments, "document")
        output_dir = resolve_stage_output_dir(
            stage=STAGE_REMEDIATE,
            project_root=project_root,
            output_dir=_opt_path(arguments, "out"),
            document_dir=document_path if document_path.is_dir() else document_path.parent,
        )
        result = run_remediate_fix_build(
            project_root=project_root,
            doc_type=arguments["doc_type"],
            layer=arguments["layer"],
            document_path=document_path,
            remediation_report=_opt_path(arguments, "remediation_report"),
            output_dir=output_dir,
        )
        det_result = _serialize_result(result)
        return await _maybe_run_executor(
            arguments, result.report_text, det_result, working_dir=project_root,
        )

    raise ValueError(f"Unknown tool: {name}")


async def _handle_lifecycle_pipeline(arguments: dict) -> dict:
    """Run multiple lifecycle stages in sequence."""
    stages = arguments["stages"]
    results: dict[str, dict] = {}
    stage_handlers = {
        "validate": "sdd_validate",
        "validate_fix": "sdd_validate_fix",
        "review": "sdd_review",
        "remediate": "sdd_remediate",
        "remediate_fix": "sdd_remediate_fix",
    }

    for stage in stages:
        tool_name = stage_handlers.get(stage)
        if tool_name is None:
            results[stage] = {"skipped": True, "reason": f"Stage '{stage}' not supported in pipeline"}
            continue

        stage_args = {
            k: v for k, v in arguments.items()
            if k not in ("stages",) and v is not None
        }

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
        except Exception as e:
            results[stage] = {"error": str(e)}
            results["_stopped_at"] = stage
            results["_reason"] = str(e)
            break

    results["_completed_stages"] = [s for s in stages if s in results and "error" not in results.get(s, {})]
    return results
