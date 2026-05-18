"""UCX CLI main entry point."""

import click
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from ucx.version import __version__
from ucx.config.settings import UCXConfig
from ucx.exceptions import AIClientError
from ucx.utils.logging import setup_logging, get_logger

console = Console()


@click.group()
@click.version_option(__version__, prog_name="ucx")
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path",
)
@click.option(
    "--mode", "-m",
    type=click.Choice(["cli", "api"]),
    default="cli",
    help="AI client mode: 'cli' for CLI agents, 'api' for LiteLLM API calls",
)
@click.option(
    "--cli-tool",
    type=click.Choice(["claude", "codex", "gemini", "ollama", "aider"]),
    default="claude",
    help="CLI tool to use in cli mode",
)
@click.option(
    "--model",
    default=None,
    envvar="UCX_MODEL",
    help="AI model: opus (best quality), sonnet (balanced), haiku (fast/cheap). Default: opus. Env: UCX_MODEL",
)
@click.option(
    "--project-dir", "-P",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    envvar="UCX_PROJECT_DIR",
    help="Project root directory containing docs/UCX/ (REQUIRED for analysis)",
)
@click.option(
    "--project-prompts", "-p",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    hidden=True,  # Deprecated
    help="DEPRECATED: use --project-dir instead",
)
@click.option(
    "--log-level", "-l",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default=None,
    help="Log level (default: INFO, or UCX_LOG_LEVEL env var)",
)
@click.option(
    "--log-format",
    type=click.Choice(["console", "verbose", "json"]),
    default="console",
    help="Log format",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output (sets log level to DEBUG)")
@click.option("--quiet", "-q", is_flag=True, help="Minimal output (sets log level to WARNING)")
@click.option(
    "--enable-web-search", "-W",
    is_flag=True,
    envvar="UCX_ENABLE_WEB_SEARCH",
    help="Enable web search for deeper analysis (fact-checking, best practices, solutions)",
)
@click.pass_context
def cli(
    ctx,
    config: Optional[Path],
    mode: str,
    cli_tool: str,
    model: Optional[str],
    project_dir: Optional[Path],
    project_prompts: Optional[Path],
    log_level: Optional[str],
    log_format: str,
    verbose: bool,
    quiet: bool,
    enable_web_search: bool,
):
    """UCX - Unified Context Framework for AI-driven document lifecycle management.

    \b
    MODES:
            --mode cli   Execute CLI agents (claude, codex, gemini, ollama) via shell [default]
      --mode api   Direct API calls via LiteLLM (requires API key)

    \b
    MODELS (--model or UCX_MODEL env var):
      opus    - Best quality, highest cost, 200K context (default)
      sonnet  - Balanced quality/cost, 200K context (recommended for most tasks)
      haiku   - Fastest, lowest cost, 200K context (good for validation)

    \b
    KEY OPTIONS:
      -P, --project-dir   Project root with docs/UCX/ for custom prompts/skills
      -W, --enable-web-search   Enable internet search for fact-checking
      -v, --verbose       Debug output
      -q, --quiet         Minimal output

    \b
    ENVIRONMENT VARIABLES:
      UCX_MODEL              Default model (opus/sonnet/haiku)
      UCX_PROJECT_DIR        Project root directory
      UCX_LOG_LEVEL          Log level (DEBUG/INFO/WARNING/ERROR)
      UCX_ENABLE_WEB_SEARCH  Enable web search (true/false)

    \b
    EXAMPLES:
      ucx review brd docs/01_BRD/BRD-01/                    # Review with opus
      ucx --model sonnet review brd docs/01_BRD/BRD-01/    # Use sonnet model
      ucx -W review brd docs/01_BRD/BRD-01/                # With web search
      ucx validate brd docs/01_BRD/BRD-01/ --fix           # Validate and fix
      UCX_MODEL=sonnet ucx review brd docs/01_BRD/BRD-01/  # Via env var
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet

    # Determine log level
    if verbose:
        effective_log_level = "DEBUG"
    elif quiet:
        effective_log_level = "WARNING"
    elif log_level:
        effective_log_level = log_level
    else:
        effective_log_level = "INFO"

    # Initialize logging
    setup_logging(level=effective_log_level, format=log_format)
    logger = get_logger("ucx.cli")

    logger.debug(f"UCX v{__version__} starting")
    logger.debug(f"Log level: {effective_log_level}, format: {log_format}")

    if config:
        base_config = UCXConfig.from_yaml(config)
        logger.debug(f"Loaded config from {config}")
    else:
        base_config = UCXConfig()

    # Override with CLI options
    config_overrides = {"ai_mode": mode, "cli_tool": cli_tool}
    if model:
        config_overrides["model"] = model
    if enable_web_search:
        config_overrides["enable_web_search"] = True
        logger.info("Web search enabled for deeper analysis")

    # Handle project directory (REQUIRED for analysis operations)
    effective_project_dir = project_dir
    if effective_project_dir is None and project_prompts:
        # Legacy: infer from project_prompts
        logger.warning("--project-prompts is deprecated, use --project-dir instead")
        # Try to infer project root from project_prompts path
        p = project_prompts
        while p.parent != p:
            if (p / "docs" / "UCX").exists():
                effective_project_dir = p
                break
            p = p.parent

    if effective_project_dir:
        config_overrides["project_dir"] = effective_project_dir
        logger.info(f"Using project directory: {effective_project_dir}")
    else:
        logger.debug("No project directory set. Use --project-dir or UCX_PROJECT_DIR for analysis.")

    ctx.obj["config"] = base_config.model_copy(update=config_overrides)
    ctx.obj["project_dir"] = effective_project_dir  # For subcommands to use

    logger.debug(
        f"Config: ai_mode={mode} cli_tool={cli_tool} model={model or base_config.model}"
    )


@cli.command()
@click.argument("doc_type")
@click.argument("target", type=click.Path())
@click.option("--from-ref", type=click.Path(exists=True, path_type=Path), help="Reference docs")
@click.option("--from-upstream", type=click.Path(exists=True, path_type=Path), help="Upstream artifact")
@click.option("--from-iplan", type=click.Path(path_type=Path), help="Implementation plan")
@click.option("--max-iterations", default=3, help="Max review/fix cycles")
@click.option("--min-score", default=90, help="Minimum passing score")
@click.option("--skip-drift", is_flag=True, help="Skip drift monitoring")
@click.option("--dry-run", is_flag=True, help="Show actions without executing")
@click.pass_context
def autopilot(ctx, doc_type, target, **kwargs):
    """
    Run full autopilot cycle (UCC → UCR → UCRem).

    \b
    Examples:
      ucx autopilot brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/
      ucx autopilot prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01
    """
    from ucx import UCXAutopilot
    from ucx.models.enums import Status
    from rich.progress import Progress, SpinnerColumn, TextColumn

    config = ctx.obj["config"]
    pilot = UCXAutopilot(
        config,
        max_iterations=kwargs.get("max_iterations", 3),
        min_score=kwargs.get("min_score", 90),
        skip_drift=kwargs.get("skip_drift", False),
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Running autopilot...", total=None)

        def update_progress(phase: str, iteration: int):
            progress.update(task, description=f"{phase}")

        result = pilot.run(
            doc_type=doc_type,
            target=Path(target),
            from_ref=kwargs.get("from_ref"),
            from_upstream=kwargs.get("from_upstream"),
            from_iplan=kwargs.get("from_iplan"),
            dry_run=kwargs.get("dry_run", False),
            progress_callback=update_progress,
        )

    # Display results
    _display_result(result)


@cli.command()
@click.argument("doc_type")
@click.argument("output_path", type=click.Path(path_type=Path))
@click.option("--from-ref", type=click.Path(exists=True, path_type=Path))
@click.option("--from-upstream", type=click.Path(exists=True, path_type=Path))
@click.option("--from-iplan", type=click.Path(path_type=Path))
@click.option("--template", type=click.Path(exists=True, path_type=Path))
@click.option("--multi-file", is_flag=True)
@click.option("--validate/--no-validate", default=True, help="Run validation after creation (default: enabled)")
@click.option("--strict", is_flag=True, help="Fail on any validation issue")
@click.option("--save-prompt/--no-save-prompt", default=True, help="Save assembled prompt to .ucx_create_session/ (default: enabled)")
@click.pass_context
def create(ctx, doc_type, output_path, validate, strict, save_prompt, **kwargs):
    """
    Create a new document (UCC phase) with optional validation.

    \b
    Post-creation validation (PRD only, v1.20.0+):
      - Runs Tier 1 validation automatically
      - Computes SYS-Ready and EARS-Ready scores
      - Injects scores into Document Control section

    \b
    Prompt history (v1.21.0+):
      Prompt is saved by default to
      .ucx_create_session/prompt_<type>_<timestamp>.txt alongside the output
      file. Useful for debugging, auditing, or re-running with a different model.
      Use --no-save-prompt to disable.

        \b
        Environment options (PRD):
            - UCX_UPSTREAM_SECTION_CHARS / UCX_UPSTREAM_TOTAL_CHARS:
                Optional upstream clipping controls (default: unlimited)
            - UCX_PRD_LLM_AUDIT_COPY=true:
                Optional Appendix D capture with raw LLM attempts (default: disabled)

        \b
        Creation audit report (always):
            Every create run writes a versioned creation report
            (`<DOC_ID>.UCX_creation_report_vNNN.md`) in the output directory.

    \b
    Examples:
      ucx create brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/
            ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01_platform_architecture
            ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01_platform_architecture --no-validate
            ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01_platform_architecture --strict
            ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01_platform_architecture --no-save-prompt
            UCX_PRD_LLM_AUDIT_COPY=true ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01_platform_architecture

        If `output_path` is a plain document ID like `PRD-01` or `PRD-01.md`, UCX
        derives a slug from the upstream artifact and writes `PRD-01_{slug}.md`.
        Example: `BRD-01_platform_architecture` -> `PRD-01_platform_architecture.md`.
    """
    from ucx import UCCPhase
    from ucx.exceptions import AIClientError
    from ucx.models.enums import DocType
    from ucx.utils.reporting import ensure_report_schema, extract_doc_id, next_report_version, report_filename

    config = ctx.obj["config"]
    ucc = UCCPhase(config)

    output_path_obj = Path(output_path)
    retry_attempted = False

    def write_creation_failure_report(error: Exception, *, retry_attempted: bool = False) -> None:
        try:
            doc_type_enum = DocType.from_string(doc_type)
            normalized_output = ucc._normalize_output_path(doc_type_enum, output_path_obj, kwargs.get("from_upstream"))
            report_dir = normalized_output if normalized_output.suffix == "" else normalized_output.parent
            report_dir.mkdir(parents=True, exist_ok=True)

            doc_id = extract_doc_id(normalized_output, doc_type_enum)
            version = next_report_version(report_dir, doc_id, "creation")
            report_path = report_dir / report_filename(doc_id, "creation", version)

            error_name = error.__class__.__name__.upper()
            failure_code = f"UCC-E-{error_name}"
            body = (
                f"# UCX Creation Failure Report: {doc_id}\n\n"
                f"## Summary\n\n"
                f"- Status: FAILED\n"
                f"- Failure Code: {failure_code}\n"
                f"- Error Type: {error.__class__.__name__}\n"
                f"- Error Message: {str(error)}\n"
                f"- Timestamp: {datetime.now(timezone.utc).isoformat()}\n\n"
                f"## Invocation\n\n"
                f"- Command: ucx create {doc_type} {output_path_obj}\n"
                f"- validate_after: {validate}\n"
                f"- save_prompt: {save_prompt}\n"
                f"- from_upstream: {kwargs.get('from_upstream')}\n"
                f"- from_ref: {kwargs.get('from_ref')}\n"
                f"- from_iplan: {kwargs.get('from_iplan')}\n"
                f"- template: {kwargs.get('template')}\n\n"
                f"## Investigation Hints\n\n"
                f"1. Inspect prompt history in .ucx_create_session/.\n"
                f"2. Re-run with an alternate model/backend.\n"
                f"3. Validate project prompt/template assets under docs/UCX/.\n"
            )
            content = ensure_report_schema(
                body,
                report_type="creation",
                source_artifact_type=doc_type_enum.value,
                source_artifact_id=doc_id,
                report_version=version,
                validator_or_reviewer="UCX create",
            )
            # Fill creation-specific fields that schema helper initializes.
            content = content.replace("failure_code: UCC-E-CREATE", f"failure_code: {failure_code}")
            content = content.replace("error_type: unknown", f"error_type: {error.__class__.__name__}")
            content = content.replace("retry_attempted: false", f"retry_attempted: {str(retry_attempted).lower()}")
            report_path.write_text(content, encoding="utf-8")
            console.print(f"[red]Creation failure report:[/red] {report_path}")
        except Exception as report_error:
            console.print(f"[yellow]Unable to write creation failure report:[/yellow] {report_error}")

    def write_creation_success_report(doc_obj, *, retry_attempted: bool = False) -> None:
        try:
            doc_type_enum = DocType.from_string(doc_type)
            normalized_output = ucc._normalize_output_path(doc_type_enum, output_path_obj, kwargs.get("from_upstream"))
            report_dir = normalized_output if normalized_output.suffix == "" else normalized_output.parent
            report_dir.mkdir(parents=True, exist_ok=True)

            doc_id = extract_doc_id(normalized_output, doc_type_enum)
            version = next_report_version(report_dir, doc_id, "creation")
            report_path = report_dir / report_filename(doc_id, "creation", version)

            body = (
                f"# UCX Creation Report: {doc_id}\n\n"
                f"## Summary\n\n"
                f"- Status: SUCCEEDED\n"
                f"- Timestamp: {datetime.now(timezone.utc).isoformat()}\n"
                f"- Output Path: {doc_obj.path}\n\n"
                f"## Invocation\n\n"
                f"- Command: ucx create {doc_type} {output_path_obj}\n"
                f"- validate_after: {validate}\n"
                f"- save_prompt: {save_prompt}\n"
                f"- from_upstream: {kwargs.get('from_upstream')}\n"
                f"- from_ref: {kwargs.get('from_ref')}\n"
                f"- from_iplan: {kwargs.get('from_iplan')}\n"
                f"- template: {kwargs.get('template')}\n\n"
                f"## Outputs\n\n"
                f"- Created document: {doc_obj.path}\n"
                f"- Prompt saved: {doc_obj.metadata.get('prompt_saved_path', 'N/A')}\n"
                f"- Validation report: {doc_obj.metadata.get('validation_report_path', 'N/A')}\n"
                f"- Validation status: {doc_obj.metadata.get('validation_status', 'unknown')}\n"
                f"- Retry attempted: {str(retry_attempted).lower()}\n"
            )

            content = ensure_report_schema(
                body,
                report_type="creation",
                source_artifact_type=doc_type_enum.value,
                source_artifact_id=doc_id,
                report_version=version,
                validator_or_reviewer="UCX create",
            )
            content = content.replace("creation_status: FAILED", "creation_status: SUCCEEDED")
            content = content.replace("failure_code: UCC-E-CREATE", "failure_code: NONE")
            content = content.replace("error_type: unknown", "error_type: none")
            content = content.replace("retry_attempted: false", f"retry_attempted: {str(retry_attempted).lower()}")

            report_path.write_text(content, encoding="utf-8")
            doc_obj.metadata["creation_report_path"] = str(report_path)
        except Exception as report_error:
            console.print(f"[yellow]Unable to write creation success report:[/yellow] {report_error}")

    try:
        doc = ucc.create(doc_type, output_path_obj, validate_after=validate, save_prompt=save_prompt, **kwargs)
    except AIClientError as e:
        message = str(e)
        lowered = message.lower()
        is_quota_issue = any(
            token in lowered for token in ["out of extra usage", "quota", "rate limit", "usage limit", "too many requests"]
        )

        if not is_quota_issue:
            write_creation_failure_report(e)
            raise

        console.print("[yellow]AI generation failed due to quota/rate limits.[/yellow]")
        console.print(f"[dim]{message}[/dim]")

        # Interactive recovery path: ask user for next backend/model and retry once.
        if not click.get_text_stream("stdin").isatty():
            console.print(
                "[yellow]Non-interactive mode detected.[/yellow] "
                "Re-run with a different backend/model, for example: "
                "ucx --cli-tool gemini --model gemini-2.5-pro create ..."
            )
            write_creation_failure_report(e)
            raise click.exceptions.Exit(code=2)

        next_tool = click.prompt(
            "Choose CLI backend to retry",
            type=click.Choice(["claude", "codex", "gemini", "ollama", "aider"], case_sensitive=False),
            default="gemini",
            show_choices=True,
        )
        next_model = click.prompt(
            "Enter model to use for retry",
            default=(
                "gemini-2.5-pro"
                if next_tool == "gemini"
                else "gpt-5-codex"
                if next_tool == "codex"
                else "sonnet"
            ),
        )

        retry_config = config.model_copy(update={"cli_tool": next_tool, "model": next_model})
        retry_attempted = True
        console.print(f"[cyan]Retrying with backend={next_tool}, model={next_model}...[/cyan]")
        try:
            doc = UCCPhase(retry_config).create(
                doc_type,
                output_path_obj,
                validate_after=validate,
                save_prompt=save_prompt,
                **kwargs,
            )
        except Exception as retry_error:
            write_creation_failure_report(retry_error, retry_attempted=True)
            raise
    except Exception as e:
        write_creation_failure_report(e)
        raise

    write_creation_success_report(doc, retry_attempted=retry_attempted)

    console.print(f"[green]Created:[/green] {doc.path}")

    if "creation_report_path" in doc.metadata:
        console.print(f"[dim]Creation report:[/dim] {doc.metadata['creation_report_path']}")

    # Display saved prompt path if applicable
    if "prompt_saved_path" in doc.metadata:
        console.print(f"[dim]Prompt saved:[/dim] {doc.metadata['prompt_saved_path']}")
    if "validation_report_path" in doc.metadata:
        console.print(f"[dim]Validation report:[/dim] {doc.metadata['validation_report_path']}")

    # Display readiness scores if computed (PRD only, requires PLAN-010 scoring module)
    if "sys_ready_score" in doc.metadata:
        sys_score = doc.metadata["sys_ready_score"]
        ears_score = doc.metadata["ears_ready_score"]
        status = doc.metadata.get("readiness_status", "Draft")
        profile = doc.metadata.get("template_profile", "mvp")
        threshold = 85 if profile == "mvp" else 90

        # Color-code based on threshold
        sys_color = "green" if sys_score >= threshold else "yellow" if sys_score >= 70 else "red"
        ears_color = "green" if ears_score >= threshold else "yellow" if ears_score >= 70 else "red"

        console.print(f"\n[bold]Readiness Scores ({profile.upper()} profile, threshold={threshold}%):[/bold]")
        console.print(f"  SYS-Ready:  [{sys_color}]{sys_score:.1f}%[/{sys_color}]")
        console.print(f"  EARS-Ready: [{ears_color}]{ears_score:.1f}%[/{ears_color}]")
        console.print(f"  Status:     {status}")

    # Display validation status
    if doc.metadata.get("validation_status") == "needs_review":
        console.print(f"\n[yellow]Warning:[/yellow] {doc.metadata.get('tier1_errors', 0)} Tier 1 issues found")
        console.print(f"Run: ucx validate prd {doc.path}")
        if strict:
            raise click.exceptions.Exit(code=1)
    elif doc.metadata.get("validation_status") == "passed":
        console.print("[green]Validation:[/green] Passed Tier 1 checks")


@cli.command()
@click.argument("doc_type")
@click.argument("doc_path", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path))
@click.option("--skip-validation", is_flag=True)
@click.option("--persona", "-p", is_flag=True, help="Use persona prompts mode (now default, flag kept for compatibility)")
@click.option("--no-resume", is_flag=True, help="Start fresh (don't resume from previous session)")
@click.option("--session-ttl", type=int, default=24, help="Session TTL in hours (default: 24)")
@click.option("--clean-memory", is_flag=True, help="Clean up stale session memory and exit")
@click.option("--clean-reports", is_flag=True, help="Clean up old review reports, keep only latest (or --keep-versions)")
@click.option("--keep-versions", type=int, default=1, help="Number of report versions to keep (default: 1)")
@click.option("--clean-all", is_flag=True, help="Clean up both session memory and old reports")
@click.option("--model", default=None, envvar="UCX_MODEL", help="Model: opus (best), sonnet (balanced), haiku (fast). Env: UCX_MODEL")
@click.option("--unified", "-u", is_flag=True, help="Force unified prompt mode (bypass auto persona prompts for large docs)")
@click.option("--scoring", type=click.Choice(["weighted"]), default="weighted", hidden=True, help="Scoring method (deprecated flag, only weighted supported)")
@click.pass_context
def review(ctx, doc_type, doc_path, output, skip_validation, persona, no_resume, session_ttl, clean_memory, clean_reports, keep_versions, clean_all, model, unified, scoring):
    """
    Review a document (UCR phase).

    \b
    MODES:
      Default:   Persona prompts (sequential API calls, filtered context, ~290K tokens)
      --unified: Unified prompt (single API call, all personas, ~60K tokens)

    \b
    Examples:
      ucx review brd docs/01_BRD/BRD-01              # Persona prompts (default)
      ucx review brd docs/01_BRD/BRD-01 --unified    # Force unified prompt mode
      ucx review brd docs/01_BRD/BRD-01 -u           # Short form for --unified
      ucx review brd docs/01_BRD/BRD-01 --session-ttl 48
      ucx review prd docs/02_PRD/PRD-01/PRD-01_platform_architecture_validation.md
      ucx review brd docs/01_BRD/BRD-01 --clean-memory
      ucx review brd docs/01_BRD/BRD-01 --clean-all
    """
    import shutil
    import os
    from ucx import UCRPhase
    from ucx.validators.prd.artifact_ops import resolve_prd_review_target

    doc_path = Path(doc_path)

    # PLAN-012: PRD review must run against the validation-fixed artifact.
    if doc_type.lower() == "prd":
        review_target = resolve_prd_review_target(doc_path)
        if review_target != doc_path:
            if review_target.exists() and review_target.is_file():
                console.print(f"[dim]PLAN-012: using validation-fixed PRD for review: {review_target.name}[/dim]")
                doc_path = review_target
            else:
                raise click.ClickException(
                    "PLAN-012 requires PRD review on the _validation copy. "
                    f"Expected '{review_target.name}'. "
                    "Run 'ucx validate-fix prd <source-prd>' first."
                )
        elif doc_path.is_dir():
            raise click.ClickException(
                "PLAN-012 requires an explicit PRD _validation file for review. "
                "Provide a path like 'PRD-01_platform_architecture_validation.md'."
            )

    # Handle --clean-all flag (combines --clean-memory and --clean-reports)
    if clean_all:
        clean_memory = True
        clean_reports = True

    # Handle --clean-memory flag
    if clean_memory:
        memory_dir = doc_path / ".ucx_review_session"
        if memory_dir.exists() and memory_dir.is_dir():
            file_count = len(list(memory_dir.iterdir()))
            total_size = sum(f.stat().st_size for f in memory_dir.iterdir() if f.is_file())
            shutil.rmtree(memory_dir)
            console.print(f"[green]Cleaned up session memory:[/green] {memory_dir}")
            console.print(f"  Removed: {file_count} files ({total_size / 1024:.1f} KB)")
        else:
            console.print(f"[yellow]No session memory found:[/yellow] {memory_dir}")

    # Handle --clean-reports flag
    if clean_reports:
        # Find all UCR/UCRem report files
        report_patterns = [
            "*.UCX_review_report_v*.md",
            "*.UCX_remediation_report_v*.md",
            "*.UCR_review_report_v*.md",
            "*_UCR_REVIEW*.md",
            "*UCR_REVIEW*.md",
            "*_UCRem_*.md",
            "*PERSONA_REVIEW*.md",
        ]
        all_reports = []

        for pattern in report_patterns:
            all_reports.extend(doc_path.glob(pattern))

        # Remove duplicates and sort by modification time (newest first)
        all_reports = list(set(all_reports))
        all_reports.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        if len(all_reports) > keep_versions:
            # Keep N latest versions, remove the rest
            to_keep = all_reports[:keep_versions]
            to_remove = all_reports[keep_versions:]

            removed_count = 0
            removed_size = 0
            for report in to_remove:
                removed_size += report.stat().st_size
                report.unlink()
                removed_count += 1
                console.print(f"  [dim]Removed:[/dim] {report.name}")

            console.print(f"[green]Cleaned up old reports:[/green] {doc_path}")
            for kept in to_keep:
                console.print(f"  [green]Kept:[/green] {kept.name}")
            console.print(f"  Removed: {removed_count} files ({removed_size / 1024:.1f} KB)")
        elif len(all_reports) >= 1:
            console.print(f"[yellow]Found {len(all_reports)} report(s), keeping all (--keep-versions={keep_versions})[/yellow]")
            for report in all_reports:
                console.print(f"  {report.name}")
        else:
            console.print(f"[yellow]No review reports found in:[/yellow] {doc_path}")

        if clean_memory or clean_all:
            return  # Exit after cleanup
        if clean_reports and not clean_all:
            return  # Exit after cleanup

    # Override model if specified on command line
    config = ctx.obj["config"]
    if model:
        config = config.model_copy(update={"model": model})

    # Auto-detect project directory from doc_path if not set
    if config.get_project_dir() is None:
        # Try to find project root by looking for docs/UCX/
        # Resolve to absolute path to handle relative paths correctly
        search_path = (doc_path if doc_path.is_dir() else doc_path.parent).resolve()
        project_dir = None
        while True:
            if (search_path / "docs" / "UCX").exists():
                project_dir = search_path
                break
            if search_path.parent == search_path:
                break  # Reached filesystem root
            search_path = search_path.parent

        if project_dir:
            config = config.model_copy(update={"project_dir": project_dir})
            console.print(f"[dim]Auto-detected project directory: {project_dir}[/dim]")
        else:
            console.print(
                "[red]Error: Project directory not found.[/red]\n"
                "Project-specific prompts are REQUIRED for review.\n"
                "Either:\n"
                "  1. Set UCX_PROJECT_DIR environment variable\n"
                "  2. Use --project-dir flag\n"
                "  3. Ensure docs/UCX/ exists in project root\n"
            )
            raise click.Abort()

    ucr = UCRPhase(config)

    # Scoring method: only weighted supported (v1.12.0+)
    # Legacy scoring removed - all reviews use category-weighted scoring
    config.scoring_method = "weighted"

    # Default to persona prompts mode (v1.15.5+) unless --unified is specified
    # Persona prompts provide better quality for all document sizes
    use_persona = not unified  # Default: persona mode; --unified overrides to unified mode

    if unified:
        console.print("[dim]Using unified prompt mode (single API call).[/dim]")

    if use_persona:
        result = ucr.review_multi_turn(
            doc_type, doc_path,
            output_path=output,
            skip_validation=skip_validation,
            resume=not no_resume,
            session_ttl_hours=session_ttl,
        )
    else:
        result = ucr.review(doc_type, doc_path, output_path=output, skip_validation=skip_validation)

    console.print(f"Score: {result.score}")
    console.print(f"Findings: P0={result.findings['P0']}, P1={result.findings['P1']}, P2={result.findings['P2']}")
    console.print(f"Report: {result.report_path}")


@cli.command()
@click.argument("review_report", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output JSON path")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed findings")
def prescreen(review_report, output, verbose):
    """
    Pre-screen UCR report for adaptive remediation.

    Analyzes the review report to identify which fixer personas are needed
    based on actual P0/P1 findings. Run this before remediation to preview
    which fixers will be loaded.

    \b
    Examples:
      ucx prescreen BRD-01.UCR_review_report_v003.md
      ucx prescreen BRD-01.UCR_review_report_v003.md --verbose
      ucx prescreen BRD-01.UCR_review_report_v003.md -o screening.json
    """
    from ucx.prescreening import analyze_ucr_report
    import json

    result = analyze_ucr_report(Path(review_report))

    # Summary table (unique findings only - deduplicated across personas)
    table = Table(title="Pre-Screening Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    unique_actionable = len(result.get_unique_actionable_ids())
    table.add_row("Unique findings", str(result.unique_findings))
    table.add_row("  ✅ Resolved", f"[green]{result.resolved_findings}[/green]")
    table.add_row("  ⏳ Open", f"[yellow]{result.open_findings}[/yellow]")
    if result.deferred_findings > 0:
        table.add_row("  ⏸️  Deferred", f"[blue]{result.deferred_findings}[/blue]")
    table.add_row("Actionable (P0/P1 open)", f"[bold]{unique_actionable}[/bold]")

    console.print(table)

    # Priority breakdown (unique findings)
    by_priority = result.get_unique_findings_by_priority()
    if by_priority:
        priority_table = Table(title="Findings by Priority")
        priority_table.add_column("Priority", style="cyan")
        priority_table.add_column("Open", style="yellow")
        priority_table.add_column("Deferred", style="blue")
        priority_table.add_column("Resolved", style="green")
        priority_table.add_column("Total", style="dim")

        for priority in ["P0", "P1", "P2"]:
            if priority in by_priority:
                stats = by_priority[priority]
                open_count = stats.get("OPEN", 0)
                deferred_count = stats.get("DEFERRED", 0)
                resolved_count = stats.get("RESOLVED", 0)
                total = sum(stats.values())
                priority_table.add_row(
                    priority,
                    str(open_count) if open_count else "-",
                    str(deferred_count) if deferred_count else "-",
                    str(resolved_count) if resolved_count else "-",
                    str(total)
                )
        console.print(priority_table)

    # Fixer loading table
    fixer_table = Table(title="Fixer Loading")
    fixer_table.add_column("Category", style="cyan")
    fixer_table.add_column("Fixers", style="green")

    fixer_table.add_row("Domain (loaded)", ", ".join(result.domain_fixers_needed) or "[dim]None[/dim]")
    fixer_table.add_row("Mandatory (always)", "chaos_engineer, chairperson")
    fixer_table.add_row("Excluded (no findings)", ", ".join(result.excluded_fixers) or "[dim]None[/dim]")

    console.print(fixer_table)

    if verbose and result.findings_by_fixer:
        console.print("\n[bold]Open Findings by Domain Fixer:[/bold]")
        for fixer, findings in result.findings_by_fixer.items():
            console.print(f"  [cyan]{fixer}[/cyan] ({len(findings)}): {', '.join(findings[:10])}"
                         f"{'...' if len(findings) > 10 else ''}")

    if not result.has_actionable_findings:
        console.print("\n[green]✓ No actionable findings - remediation would be skipped[/green]")
    else:
        console.print(f"\n[yellow]→ Remediation will load {len(result.required_fixers)} fixers "
                     f"(saved {len(result.excluded_fixers)} from loading)[/yellow]")

    if output:
        Path(output).write_text(json.dumps(result.to_dict(), indent=2))
        console.print(f"\n[dim]Screening results saved to: {output}[/dim]")


@cli.command()
@click.argument("review_report", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output JSON path")
@click.option("--format", "-f", "output_format", type=click.Choice(["table", "json"]), default="table")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed findings")
def scan(review_report, output, output_format, verbose):
    """
    Unified UCR report scanner (v1.11.0+).

    Analyzes UCR review reports using two extraction methods:
    1. Manifest extraction: Parses Chairperson's Remediation Findings Manifest (authoritative)
    2. Persona extraction: Extracts from individual persona sections (fixer routing)

    The Chairperson manifest (if present) is the authoritative source for
    finding counts and PRD-Ready score.

    \b
    Examples:
      ucx scan BRD-01.UCR_review_report_v001.md
      ucx scan BRD-01.UCR_review_report_v001.md --verbose
      ucx scan BRD-01.UCR_review_report_v001.md -f json -o scan_results.json
    """
    from ucx.prescreening import scan_ucr_report
    import json

    result = scan_ucr_report(Path(review_report))

    if output_format == "json":
        json_output = json.dumps(result.to_dict(), indent=2)
        if output:
            Path(output).write_text(json_output)
            console.print(f"[dim]Scan results saved to: {output}[/dim]")
        else:
            console.print(json_output)
        return

    # Header with manifest status
    if result.has_manifest:
        console.print("[green]✓ Chairperson Manifest detected (authoritative)[/green]\n")
    else:
        console.print("[yellow]⚠ No manifest found - using persona extraction[/yellow]\n")

    counts = result.authoritative_counts

    # Summary table (authoritative counts)
    table = Table(title="UCX Scan Results" + (" [green](Manifest)[/green]" if result.has_manifest else " [yellow](Persona)[/yellow]"))
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total findings", str(counts["total"]))
    table.add_row("  P0 (Critical)", f"[red]{counts['p0']}[/red]" if counts["p0"] else "-")
    table.add_row("  P1 (High)", f"[yellow]{counts['p1']}[/yellow]" if counts["p1"] else "-")
    table.add_row("  P2 (Medium)", str(counts["p2"]) if counts["p2"] else "-")
    table.add_row("  ✅ Resolved", f"[green]{counts['resolved']}[/green]" if counts["resolved"] else "-")
    table.add_row("  ⏸️  Deferred", f"[blue]{counts['deferred']}[/blue]" if counts["deferred"] else "-")
    table.add_row("Actionable", f"[bold]{counts['actionable']}[/bold]")

    if result.prd_ready_score is not None:
        score = result.prd_ready_score
        if score >= 85:
            score_style = "green"
        elif score >= 60:
            score_style = "yellow"
        else:
            score_style = "red"
        table.add_row("PRD-Ready Score", f"[{score_style}]{score}/100[/{score_style}]")

    console.print(table)

    # Fixer loading table
    fixer_table = Table(title="Fixer Routing")
    fixer_table.add_column("Category", style="cyan")
    fixer_table.add_column("Fixers", style="green")

    required = result.required_fixers
    domain_fixers = [f for f in required if f not in ["chaos_engineer", "chairperson"]]
    excluded = [f for f in ["architect", "auditor", "integration_lead", "qa_lead"] if f not in domain_fixers]

    fixer_table.add_row("Domain (loaded)", ", ".join(domain_fixers) or "[dim]None[/dim]")
    fixer_table.add_row("Mandatory (always)", "chaos_engineer, chairperson")
    fixer_table.add_row("Excluded (no findings)", ", ".join(excluded) or "[dim]None[/dim]")

    console.print(fixer_table)

    # Verbose: Show findings by fixer
    if verbose:
        if result.has_manifest and result.manifest.findings_by_fixer:
            console.print("\n[bold]Findings by Fixer (from Manifest):[/bold]")
            for fixer, findings in result.manifest.findings_by_fixer.items():
                console.print(f"  [cyan]{fixer}[/cyan] ({len(findings)}): {', '.join(findings[:10])}"
                             f"{'...' if len(findings) > 10 else ''}")
        elif result.persona_extraction.findings_by_fixer:
            console.print("\n[bold]Findings by Fixer (from Persona Extraction):[/bold]")
            for fixer, findings in result.persona_extraction.findings_by_fixer.items():
                console.print(f"  [cyan]{fixer}[/cyan] ({len(findings)}): {', '.join(findings[:10])}"
                             f"{'...' if len(findings) > 10 else ''}")

        # Show manifest findings if present
        if result.has_manifest and result.manifest.findings:
            console.print("\n[bold]Manifest Findings (first 10):[/bold]")
            for i, f in enumerate(result.manifest.findings[:10]):
                status_color = {"OPEN": "yellow", "RESOLVED": "green", "DEFERRED": "blue"}.get(f.status, "white")
                console.print(f"  {f.id}: [{status_color}]{f.status}[/{status_color}] → {f.fixer or '-'} | {f.description[:60]}...")
            if len(result.manifest.findings) > 10:
                console.print(f"  ... and {len(result.manifest.findings) - 10} more")

    # Comparison if both methods available
    if result.has_manifest and verbose:
        console.print("\n[dim]─── Extraction Comparison ───[/dim]")
        persona_counts = result.persona_extraction.get_unique_findings_by_priority()
        p0_persona = sum(persona_counts.get("P0", {}).values())
        p1_persona = sum(persona_counts.get("P1", {}).values())
        p2_persona = sum(persona_counts.get("P2", {}).values())

        console.print(f"  Manifest:  P0={counts['p0']}, P1={counts['p1']}, P2={counts['p2']}")
        console.print(f"  Persona:   P0={p0_persona}, P1={p1_persona}, P2={p2_persona}")

        if counts["p0"] != p0_persona or counts["p1"] != p1_persona:
            console.print("  [green]→ Manifest provides deduplicated authoritative counts[/green]")

    # Summary
    if counts["actionable"] == 0:
        console.print("\n[green]✓ No actionable findings - remediation would be skipped[/green]")
    else:
        console.print(f"\n[yellow]→ Remediation will load {len(required)} fixers[/yellow]")

    if output:
        Path(output).write_text(json.dumps(result.to_dict(), indent=2))
        console.print(f"[dim]Scan results saved to: {output}[/dim]")


@cli.command()
@click.argument("doc_path", type=click.Path(exists=True, path_type=Path))
@click.option("--report", "-r", type=click.Path(exists=True, path_type=Path), help="Specific review report (auto-detects latest if not provided)")
@click.option("--output", "-o", type=click.Path(path_type=Path))
@click.option("--apply-auto-safe", is_flag=True, help="Apply auto-safe fixes")
@click.pass_context
def remediate(ctx, doc_path, report, output, apply_auto_safe):
    """
    Generate fixes from review report (UCRem phase).

    Automatically finds the latest UCR review report if not specified.
    Runs pre-screening to load only the fixer personas needed based on
    actual findings in the review report.

    \b
    Examples:
      ucx remediate docs/01_BRD/BRD-01                    # Auto-detect latest report
      ucx remediate docs/01_BRD/BRD-01 --apply-auto-safe  # Auto-detect + apply fixes
      ucx remediate docs/01_BRD/BRD-01 -r BRD-01.UCR_review_report_v003.md  # Specific report
    """
    from ucx import UCRemPhase
    from ucx.models.enums import Confidence
    from ucx.utils.file_ops import find_latest_review_report
    from ucx.validators.prd.artifact_ops import identify_prd_artifact_stage

    config = ctx.obj["config"]

    # Auto-detect project directory from doc_path if not set
    if config.get_project_dir() is None:
        # Try to find project root by looking for docs/UCX/
        # Resolve to absolute path to handle relative paths correctly
        search_path = (doc_path if doc_path.is_dir() else doc_path.parent).resolve()
        project_dir = None
        while True:
            if (search_path / "docs" / "UCX").exists():
                project_dir = search_path
                break
            if search_path.parent == search_path:
                break  # Reached filesystem root
            search_path = search_path.parent

        if project_dir:
            config = config.model_copy(update={"project_dir": project_dir})
            console.print(f"[dim]Auto-detected project directory: {project_dir}[/dim]")
        else:
            console.print(
                "[red]Error: Project directory not found.[/red]\n"
                "Project-specific prompts are REQUIRED for remediation.\n"
                "Either:\n"
                "  1. Set UCX_PROJECT_DIR environment variable\n"
                "  2. Use --project-dir flag\n"
                "  3. Ensure docs/UCX/ exists in project root\n"
            )
            raise click.Abort()

    # PLAN-012 guardrail: PRD remediation must run on a _validation copy.
    is_prd_file = doc_path.is_file() and doc_path.suffix.lower() == ".md" and doc_path.name.startswith("PRD-")
    if is_prd_file:
        stage = identify_prd_artifact_stage(doc_path)
        if stage != "validation-fixed":
            console.print(
                "[red]Error: PRD remediation must use a _validation PRD copy (processing_stage: validation-fixed).[/red]\n"
                f"Received: {doc_path.name} (stage: {stage})\n"
                "Use `ucx validate-fix prd <source-prd> --report <validation-report>` first."
            )
            raise click.Abort()

    # Auto-detect latest review report if not specified
    review_report = report
    if review_report is None:
        review_report = find_latest_review_report(doc_path)
        if review_report is None:
            console.print(
                "[red]Error: No review report found.[/red]\n"
                f"No UCR review reports found in: {doc_path}\n\n"
                "Either:\n"
                "  1. Run 'ucx review' first to generate a report\n"
                "  2. Use --report to specify a specific report path\n"
            )
            raise click.Abort()
        console.print(f"[green]Using latest review report:[/green] {review_report.name}")
    else:
        console.print(f"[dim]Using specified review report: {review_report.name}[/dim]")

    # PLAN-012 guardrail: PRD remediation must consume a UCX review report.
    if is_prd_file and ".UCX_review_report_" not in review_report.name:
        console.print(
            "[red]Error: PRD remediation requires a UCX review report (*.UCX_review_report_vNNN.md).[/red]\n"
            f"Received: {review_report.name}"
        )
        raise click.Abort()

    ucrem = UCRemPhase(config)
    fixes, report_path = ucrem.generate_fixes(doc_path, review_report=review_report, output_path=output)

    # Display pre-screening results
    if ucrem.last_screening:
        screening = ucrem.last_screening
        console.print("\n[bold]Pre-Screening:[/bold]")
        console.print(f"  Findings: {screening.total_findings} total, {screening.actionable_findings} actionable")
        if screening.domain_fixers_needed:
            console.print(f"  Domain fixers: [green]{', '.join(screening.domain_fixers_needed)}[/green]")
        else:
            console.print(f"  Domain fixers: [dim]None needed[/dim]")
        if screening.excluded_fixers:
            console.print(f"  Excluded: [dim]{', '.join(screening.excluded_fixers)}[/dim]")

    auto_safe = [f for f in fixes if f.confidence == Confidence.AUTO_SAFE]
    auto_assisted = [f for f in fixes if f.confidence == Confidence.AUTO_ASSISTED]
    manual = [f for f in fixes if f.confidence == Confidence.MANUAL_REQUIRED]

    console.print(f"\n[bold]Remediation report:[/bold] {report_path}")
    console.print(f"Fixes: auto-safe={len(auto_safe)}, auto-assisted={len(auto_assisted)}, manual={len(manual)}")

    if apply_auto_safe and auto_safe:
        applied = ucrem.apply_auto_safe(fixes)
        console.print(f"[green]Applied {len(applied)} auto-safe fixes[/green]")


@cli.command()
@click.argument("doc_type")
@click.argument("doc_path", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Write validation report to file")
@click.option("--precommit", is_flag=True, help="Emit .precommit_validation_report.md (hook mode only)")
@click.option("--tier1-only", is_flag=True, help="Run only Tier 1 (core) checks for pre-commit")
@click.option("--strict", is_flag=True, help="Treat warnings as errors")
@click.option("--format", "output_format", type=click.Choice(["text", "json"]), default="text", help="Output format")
@click.option("--fix", is_flag=True, hidden=True, help="DEPRECATED: Validation now always fixes. Use --no-fix to skip.")
@click.option("--no-fix", is_flag=True, help="Skip auto-fixing (validation always fixes by default)")
@click.option("--report/--no-report", default=True, help="Generate validation report to document directory (default: enabled)")
@click.option("--clean-reports", is_flag=True, help="Clean up old validation reports, keep only latest (or --keep-versions)")
@click.option("--keep-versions", type=int, default=1, help="Number of report versions to keep (default: 1)")
@click.pass_context
def validate(ctx, doc_type, doc_path, output, precommit, tier1_only, strict, output_format, fix, no_fix, report, clean_reports, keep_versions):
    """
    Validate a document (no AI review).

    \b
    As of v1.17.0, validation ALWAYS fixes structural issues automatically.
    Use --no-fix to skip fixing (e.g., for pre-commit hooks).

    \b
    Source Protection (v1.21.6+):
    Validation now uses source protection: fix recommendations are analyzed and
    documented in the validation report, but the source PRD/BRD file remains
    untouched. This ensures validation is a safe, read-only operation that
    produces a report artifact only.

    \b
    By default, writes validation report to document directory (like review).
    Use --no-report for console-only output.

    \b
    Tiered validation:
      Tier 1 (Core, blocking): Element codes, structure, metadata, quality gates
      Tier 2 (Advisory): Links, references, diagrams, glossary

    \b
    Auto-fix analysis (default behavior):
    Validates what fixes could be applied, documents them in the report:
      - Missing metadata fields (custom_fields.document_type, artifact_type, layer)
      - Missing tags (brd, layer-1-artifact)
      - Missing Document Control fields
      - Legacy status values
      - Partial fixes requiring LLM completion

    Source files remain unchanged; apply fixes manually or use ucx remediate.

    \b
    Examples:
      ucx validate brd docs/01_BRD/BRD-01                    # Validate + analyze fixes + report (source protected)
      ucx validate brd docs/01_BRD/BRD-01 --no-fix          # Validate only, no fix analysis
      ucx validate brd docs/01_BRD/BRD-01 --no-report       # Analyze but no report file
      ucx validate brd docs/01_BRD/BRD-01 --tier1-only      # Tier 1 + fix analysis + report
      ucx validate brd docs/01_BRD/BRD-01 --strict --format json
      ucx validate brd docs/01_BRD/BRD-01 -o custom_report.md
      ucx validate brd docs/01_BRD/BRD-01 --clean-reports --keep-versions 3
    """
    import json
    import sys
    from ucx.models.enums import DocType
    from ucx.utils.reporting import (
        ensure_report_schema,
        next_report_version,
        report_filename,
        resolve_doc_id_strict,
    )

    doc_path = Path(doc_path)

    # Handle deprecated --fix flag (v1.17.0+)
    if fix:
        console.print(
            "[yellow]⚠ --fix is deprecated. Validation now always fixes by default. "
            "Use --no-fix to skip fixing.[/yellow]\n"
        )

    def _clean_old_reports(target_path: Path, keep: int) -> None:
        """Clean up legacy versioned validation reports.

        Note: As of UCX v1.16.1, validation uses a single 'precommit_validation_report.md'
        file that overwrites on each run. This function cleans up legacy versioned reports.
        """
        # Legacy patterns (pre-v1.16.1) - versioned validation reports
        legacy_patterns = ["*.V_validation_report_v*.md", "*_validation_report_v*.md"]
        all_reports = []

        for pattern in legacy_patterns:
            all_reports.extend(target_path.glob(pattern))

        # Remove duplicates
        all_reports = list(set(all_reports))

        if all_reports:
            removed_count = 0
            removed_size = 0
            for rpt in all_reports:
                removed_size += rpt.stat().st_size
                rpt.unlink()
                removed_count += 1
                console.print(f"  [dim]Removed legacy report:[/dim] {rpt.name}")

            console.print(f"[green]Cleaned up legacy validation reports:[/green] {target_path}")
            console.print(f"  Removed: {removed_count} files ({removed_size / 1024:.1f} KB)")
        else:
            console.print(f"[yellow]No legacy validation reports found in:[/yellow] {target_path}")

    # Handle --clean-reports flag (standalone mode - cleanup only)
    if clean_reports and not fix:
        _clean_old_reports(doc_path, keep_versions)
        return  # Exit after cleanup

    doc_type_lower = doc_type.lower()

    # Use unified validator for BRD
    if doc_type_lower == "brd":
        from ucx.validators.brd import UnifiedBRDValidator

        validator = UnifiedBRDValidator(strict=strict, verbose=ctx.obj.get("verbose", False))
        result = validator.validate(Path(doc_path), tier1_only=tier1_only)

        # Auto-fix structural issues (v1.17.0: always fix unless --no-fix)
        fix_summary = None
        fixer_error = None

        if not no_fix:
            from ucx.validators.brd.fixer import BRDFixer, FIXABLE_CODES

            # Collect all fixable issues
            all_issues = result.tier1_issues + result.tier2_issues
            fixable_issues = [i for i in all_issues if i.code in FIXABLE_CODES]

            # Always run fixer for DEFERRED→UCX-ACTION migration (v1.19.2+)
            # Even if no fixable issues, we may have legacy DEFERRED comments to migrate
            if fixable_issues:
                console.print(f"\n[cyan]Auto-fixing {len(fixable_issues)} structural issue(s)...[/cyan]")

            # === VALIDATION SOURCE PROTECTION (v1.21.6+) ===
            # Snapshot source files before running fixer to ensure validation
            # creates reports only, without modifying the source PRD/BRD document.
            source_snapshot: dict[Path, str] = {}
            try:
                # Get list of markdown sources in the document directory
                doc_path_obj = Path(doc_path)
                search_dir = doc_path_obj if doc_path_obj.is_dir() else doc_path_obj.parent
                source_files = list(search_dir.glob("*.md"))
                # Exclude reports (validation, review, remediation, creation reports)
                source_files = [
                    f for f in source_files 
                    if not any(keyword in f.name for keyword in [
                        "validation_report", "V_validation", "REVIEW", "REPORT", 
                        "remediation_report", "creation_report"
                    ])
                ]
                
                # Snapshot before fixer runs
                for file_path in source_files:
                    try:
                        source_snapshot[file_path] = file_path.read_text(encoding="utf-8")
                    except OSError:
                        continue
                
                # Run fixer (will write changes to files)
                try:
                    fixer = BRDFixer(doc_path, verbose=ctx.obj.get("verbose", False))
                    fix_summary = fixer.fix_all(fixable_issues)

                    # Display fix results with partial fix indicators (v1.17.0+)
                    for fix_result in fix_summary.results:
                        if fix_result.fixed:
                            if fix_result.partial_fix:
                                console.print(f"  [cyan]◐[/cyan] {fix_result.code}: {fix_result.message}")
                                console.print(f"    [dim]LLM Task: {fix_result.llm_task}[/dim]")
                            else:
                                console.print(f"  [green]✓[/green] {fix_result.code}: {fix_result.message}")
                            for change in fix_result.changes:
                                console.print(f"    [dim]→ {change}[/dim]")
                        else:
                            console.print(f"  [yellow]⊘[/yellow] {fix_result.code}: {fix_result.message}")

                    # Summary with partial fix count (v1.17.0+)
                    if fix_summary.results:  # Only show summary if there were any fixes attempted
                        console.print(
                            f"\n[green]Fixed: {fix_summary.fully_fixed_count}[/green] | "
                            f"[cyan]Partial: {fix_summary.partial_fix_count}[/cyan] | "
                            f"[yellow]Skipped: {fix_summary.skipped_count}[/yellow] | "
                            f"[red]Failed: {fix_summary.failed_count}[/red]"
                        )

                    if fix_summary.partial_fix_count > 0:
                        console.print(f"\n[cyan]LLM Completion Required: {fix_summary.partial_fix_count}[/cyan]")
                        console.print("[dim]Run `ucx remediate` to complete partial fixes with AI.[/dim]")

                    # Re-run validation to show updated results
                    if fix_summary.fixed_count > 0:
                        console.print("\n[cyan]Re-validating after fixes...[/cyan]\n")
                        result = validator.validate(Path(doc_path), tier1_only=tier1_only)

                except Exception as e:
                    fixer_error = str(e)
                    console.print(f"[red]Fixer error: {e}[/red]")
                    import logging
                    logging.getLogger(__name__).exception("Fixer failed")
                
                # === RESTORE SOURCE FILES ===
                # Restore source documents to original state (validation report-only protection)
                if source_snapshot:
                    restored_files = []
                    for file_path, original_content in source_snapshot.items():
                        try:
                            current_content = file_path.read_text(encoding="utf-8") if file_path.exists() else None
                        except OSError:
                            continue
                        
                        # Only restore if file was modified
                        if current_content != original_content:
                            try:
                                file_path.write_text(original_content, encoding="utf-8")
                                restored_files.append(file_path)
                            except OSError:
                                continue
                    
                    if restored_files:
                        console.print(
                            f"\n[yellow]⚠ Restored source files (validation report-only):[/yellow]"
                        )
                        for f in restored_files:
                            console.print(f"  [dim]→ {f.name}[/dim]")
                        console.print(
                            "[dim]Source documents unchanged. "
                            "Fix recommendations documented in validation report only.[/dim]"
                        )
                
            except Exception as e:
                console.print(f"[red]Source protection error: {e}[/red]")
                import logging
                logging.getLogger(__name__).exception("Source protection failed")


        # Attach fixer context to result (v1.17.0+)
        if fix_summary:
            result.fixer_context = fix_summary.to_fixer_context(doc_path)
        elif fixer_error:
            # Create error context so remediation knows fixer attempted but failed
            from datetime import datetime, timezone
            from ucx.validators.common.result import FixerContext
            result.fixer_context = FixerContext(
                session_id="error",
                timestamp=datetime.now(timezone.utc).isoformat(),
                llm_only=[{
                    "code": "FIXER-ERROR",
                    "file": str(doc_path),
                    "reason": f"Fixer failed: {fixer_error}. Manual fixes required."
                }]
            )

        # Resolve doc_id from path with strict checks
        doc_path_obj = Path(doc_path)
        doc_id = resolve_doc_id_strict(doc_path_obj, DocType.BRD)

        # Handle --report flag: auto-generate report to document directory
        if report and not output:
            # Set output to document directory for auto-report
            output = doc_path_obj if doc_path_obj.is_dir() else doc_path_obj.parent

        # Write to file if output specified
        if output:
            output_path = Path(output)

            # If output path is a directory or ends with /, auto-generate filename
            if str(output).endswith("/") or (output_path.exists() and output_path.is_dir()):
                output_path.mkdir(parents=True, exist_ok=True)
                if precommit:
                    output_path = output_path / ".precommit_validation_report.md"
                    version = 1
                else:
                    doc_id = resolve_doc_id_strict(doc_path_obj, DocType.BRD)
                    version = next_report_version(output_path, doc_id, "validation")
                    output_path = output_path / report_filename(doc_id, "validation", version)
            else:
                # Output to specified file
                output_path.parent.mkdir(parents=True, exist_ok=True)
                # Extract version from filename if present, else use 1
                version_match = re.search(r"v(\d+)", str(output_path))
                version = int(version_match.group(1)) if version_match else 1

            if output_format == "json":
                import json as json_module
                output_content = json_module.dumps(result.to_dict(), indent=2)
            else:
                # Use SDD-compliant report format for file output
                output_content = result.format_report(doc_id=doc_id, doc_type="BRD", version=version)
                if not precommit:
                    output_content = ensure_report_schema(
                        output_content,
                        report_type="validation",
                        source_artifact_type=DocType.BRD.value,
                        source_artifact_id=doc_id,
                        report_version=version,
                        validator_or_reviewer="UCX validate (brd)",
                    )

            output_path.write_text(output_content)
            console.print(f"[green]Validation report written to:[/green] {output_path}")

            # Clean up old reports if --clean-reports was used with --fix
            if clean_reports:
                console.print()  # Blank line before cleanup output
                _clean_old_reports(doc_path_obj if doc_path_obj.is_dir() else doc_path_obj.parent, keep_versions)
        else:
            # Console output uses simple text format
            if output_format == "json":
                console.print_json(data=result.to_dict())
            else:
                console.print(result.format_text(verbose=ctx.obj.get("verbose", False)))

        # Exit with appropriate code
        sys.exit(result.exit_code(strict=strict))
    elif doc_type_lower == "prd":
        # PRD-specific validator path (PLAN-012, v1.22.0)
        # Emits fixed report name PRD-01_validation_report.md (no versioning)
        from ucx.validators.prd import UnifiedPRDValidator
        from ucx.validators.prd.fixer import PRDFixer
        from ucx.validators.prd.artifact_ops import prd_validation_report_name

        validator = UnifiedPRDValidator(strict=strict, verbose=ctx.obj.get("verbose", False))
        result = validator.validate(Path(doc_path), tier1_only=tier1_only)

        # --- Source Protection (v1.21.6+, PRD path) ---
        doc_path_obj = Path(doc_path)
        search_dir = doc_path_obj if doc_path_obj.is_dir() else doc_path_obj.parent
        source_snapshot: dict[Path, str] = {}
        prd_fix_result = None
        prd_fixer_error = None

        if not no_fix:
            # Snapshot source files — exclude reports and derived copies
            for f in search_dir.glob("*.md"):
                if any(kw in f.name for kw in [
                    "_validation_report", "_validation.", "_remediated.",
                    "review_report", "remediation_report", "creation_report",
                ]):
                    continue
                try:
                    source_snapshot[f] = f.read_text(encoding="utf-8")
                except OSError:
                    continue

            # Collect all issues and run PRD fixer on source files (dry_run=True in validation)
            all_issues = result.tier1_issues + result.tier2_issues
            if all_issues:
                try:
                    prd_fixer = PRDFixer(dry_run=True, verbose=ctx.obj.get("verbose", False))
                    # Get the primary PRD source file (not derived copies)
                    prd_source_files = [
                        f for f in search_dir.glob("*.md")
                        if not any(kw in f.name for kw in [
                            "_validation", "_remediated", "report"
                        ])
                    ]
                    for prd_file in prd_source_files:
                        prd_fix_result = prd_fixer.fix(prd_file, all_issues)
                        if prd_fix_result.actions:
                            console.print(
                                f"\n[cyan]Fix analysis: {len(prd_fix_result.actions)} action(s) "
                                f"identified (report-only, source unchanged)[/cyan]"
                            )
                except Exception as e:
                    prd_fixer_error = str(e)
                    console.print(f"[yellow]PRD fix analysis error: {e}[/yellow]")

            # Restore source files if fixer modified them
            for file_path, original in source_snapshot.items():
                try:
                    current = file_path.read_text(encoding="utf-8") if file_path.exists() else None
                except OSError:
                    continue
                if current != original:
                    try:
                        file_path.write_text(original, encoding="utf-8")
                    except OSError:
                        continue

        # Resolve doc_id
        try:
            doc_id = resolve_doc_id_strict(doc_path_obj, DocType.PRD)
        except (ValueError, Exception):
            doc_id = "PRD-XX"

        # Auto-report: PRD emits fixed report name (PLAN-012)
        if report and not output:
            output = doc_path_obj if doc_path_obj.is_dir() else doc_path_obj.parent

        if output:
            output_path = Path(output)
            if str(output).endswith("/") or (output_path.exists() and output_path.is_dir()):
                output_path.mkdir(parents=True, exist_ok=True)
                # Fixed PRD validation report name (no versioning per PLAN-012)
                output_path = output_path / prd_validation_report_name(doc_id)
            else:
                output_path.parent.mkdir(parents=True, exist_ok=True)

            if output_format == "json":
                import json as json_module
                output_content = json_module.dumps(result.to_dict() if hasattr(result, "to_dict") else {}, indent=2)
            else:
                unified_result = result  # UnifiedPRDValidator returns PRDValidationResult directly
                if hasattr(unified_result, "format_report"):
                    output_content = unified_result.format_report(
                        doc_id=doc_id, doc_type="PRD", version=1
                    )
                else:
                    output_content = f"# PRD Validation Report: {doc_id}\n\nStatus: {getattr(result, 'status', 'unknown')}\n"

                from ucx.validators.prd.artifact_ops import is_source_prd
                # Determine source PRD filename for lineage metadata
                source_prd_file = None
                for f in search_dir.glob("*.md"):
                    if is_source_prd(f) and not any(kw in f.name for kw in ["report"]):
                        source_prd_file = f.name
                        break

                output_content = ensure_report_schema(
                    output_content,
                    report_type="validation",
                    source_artifact_type=DocType.PRD.value,
                    source_artifact_id=doc_id,
                    report_version=1,
                    validator_or_reviewer="UCX validate (prd)",
                )
                # Inject PLAN-012 lineage metadata into the report frontmatter
                if source_prd_file:
                    output_content = _inject_prd_validation_lineage(output_content, doc_id, source_prd_file)

            output_path.write_text(output_content, encoding="utf-8")
            console.print(f"[green]Validation report:[/green] {output_path}")
        else:
            if hasattr(result, "format_text"):
                console.print(result.format_text(verbose=ctx.obj.get("verbose", False)))
            else:
                console.print(f"Status: {getattr(result, 'status', 'unknown')}")

        # Exit based on tier1 issues
        if result.tier1_issues:
            sys.exit(2)
        elif strict and result.tier2_issues:
            sys.exit(2)
        else:
            sys.exit(0)
    else:
        # Fallback validator path for non-BRD types
        from ucx import UCRPhase

        ucr = UCRPhase(ctx.obj["config"])
        result = ucr.validate(doc_type, Path(doc_path))

        # Resolve doc_id for report metadata with strict checks
        # Auto-report behavior: mirror BRD path (default enabled via --report)
        if report and not output:
            output = doc_path_obj if doc_path_obj.is_dir() else doc_path_obj.parent

        console.print(f"Status: {result.status.value}")
        console.print(f"Errors: {result.error_count}")
        console.print(f"Warnings: {result.warning_count}")

        if result.errors:
            console.print("\n[red]Errors:[/red]")
            for error in result.errors:
                console.print(f"  - {error}")

        if result.warnings:
            console.print("\n[yellow]Warnings:[/yellow]")
            for warning in result.warnings:
                console.print(f"  - {warning}")

        # Write report file when output is specified (explicitly or via --report default)
        if output:
            output_path = Path(output)

            # If output is a directory, write canonical report file (or precommit in precommit mode)
            if str(output).endswith("/") or (output_path.exists() and output_path.is_dir()):
                output_path.mkdir(parents=True, exist_ok=True)
                if precommit:
                    output_path = output_path / ".precommit_validation_report.md"
                    version = 1
                else:
                    version = next_report_version(output_path, doc_id, "validation")
                    output_path = output_path / report_filename(doc_id, "validation", version)
            else:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                version_match = re.search(r"v(\d+)", str(output_path))
                version = int(version_match.group(1)) if version_match else 1

            if output_format == "json":
                if hasattr(result, "to_dict"):
                    output_content = json.dumps(result.to_dict(), indent=2)
                else:
                    output_content = json.dumps(
                        {
                            "doc_path": str(doc_path_obj),
                            "status": result.status.value if hasattr(result.status, "value") else str(result.status),
                            "errors": result.errors,
                            "warnings": result.warnings,
                            "passes": getattr(result, "passes", []),
                        },
                        indent=2,
                    )
            else:
                if unified_result is not None and hasattr(unified_result, "format_report"):
                    output_content = unified_result.format_report(
                        doc_id=doc_id,
                        doc_type=doc_type.upper(),
                        version=version,
                    )
                    if not precommit:
                        output_content = ensure_report_schema(
                            output_content,
                            report_type="validation",
                            source_artifact_type=doc_enum.value,
                            source_artifact_id=doc_id,
                            report_version=version,
                            validator_or_reviewer=f"UCX validate ({doc_enum.value})",
                        )
                elif hasattr(result, "format_report"):
                    output_content = result.format_report(
                        doc_id=doc_id,
                        doc_type=doc_type.upper(),
                        version=version,
                    )
                    if not precommit:
                        output_content = ensure_report_schema(
                            output_content,
                            report_type="validation",
                            source_artifact_type=doc_enum.value,
                            source_artifact_id=doc_id,
                            report_version=version,
                            validator_or_reviewer=f"UCX validate ({doc_enum.value})",
                        )
                elif hasattr(result, "format_text"):
                    output_content = result.format_text(verbose=ctx.obj.get("verbose", False))
                else:
                    output_content = (
                        f"Status: {result.status.value if hasattr(result.status, 'value') else result.status}\n"
                        f"Errors: {len(result.errors)}\n"
                        f"Warnings: {len(result.warnings)}\n"
                    )

            output_path.write_text(output_content, encoding="utf-8")
            console.print(f"[green]Validation report written to:[/green] {output_path}")

        # Exit with appropriate code
        if result.errors:
            sys.exit(2)
        elif result.warnings and strict:
            sys.exit(2)
        elif result.warnings:
            sys.exit(1)
        else:
            sys.exit(0)


@cli.command("validate-fix")
@click.argument("doc_type")
@click.argument("doc_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--report", "-r",
    type=click.Path(exists=True, path_type=Path),
    help="Validation report to use for fix guidance (auto-detects PRD-01_validation_report.md if not given)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be created without writing files",
)
@click.option(
    "--max-iterations",
    type=int,
    default=3,
    show_default=True,
    help="Maximum validate/fix passes to run before stopping",
)
@click.pass_context
def validate_fix(ctx, doc_type, doc_path, report, dry_run, max_iterations):
    """
    Create a _validation copy with validation fixes applied (PLAN-012 Stage 3).

    Reads the canonical source PRD, applies deterministic validation fixes,
    injects processing-stage lineage metadata, and writes the result as a
    new ``_validation`` copy. The source PRD is never modified.

    \b
    Only 'prd' is supported as doc_type for this command.

    \b
    Examples:
      ucx validate-fix prd docs/02_PRD/PRD-01/PRD-01_platform_architecture.md
      ucx validate-fix prd docs/02_PRD/PRD-01/PRD-01_platform_architecture.md --dry-run
      ucx validate-fix prd docs/02_PRD/PRD-01/PRD-01_platform_architecture.md \\
          --report docs/02_PRD/PRD-01/PRD-01_validation_report.md
        ucx validate-fix prd docs/02_PRD/PRD-01/PRD-01_platform_architecture.md --max-iterations 5
    """
    import sys
    from collections import Counter
    from ucx.validators.prd import UnifiedPRDValidator
    from ucx.validators.prd.fixer import PRDFixer
    from ucx.validators.prd.artifact_ops import (
        create_validation_copy,
        identify_prd_artifact_stage,
        prd_validation_report_name,
    )
    from ucx.models.enums import DocType

    doc_path = Path(doc_path)

    if doc_type.lower() != "prd":
        console.print("[red]Error: validate-fix currently only supports 'prd'.[/red]")
        sys.exit(1)

    # Must be a source PRD (no _validation or _remediated suffix)
    stage = identify_prd_artifact_stage(doc_path)
    if stage != "source":
        console.print(
            f"[red]Error: Input must be a canonical source PRD (no stage suffix). "
            f"Got stage: '{stage}' for '{doc_path.name}'[/red]"
        )
        sys.exit(1)

    # Resolve doc_id
    try:
        from ucx.utils.reporting import resolve_doc_id_strict
        doc_id = resolve_doc_id_strict(doc_path, DocType.PRD)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

    # Auto-detect validation report if not given
    validation_report = report
    if validation_report is None:
        auto_report = doc_path.parent / prd_validation_report_name(doc_id)
        if auto_report.exists():
            validation_report = auto_report
            console.print(f"[dim]Using validation report: {auto_report.name}[/dim]")
        else:
            console.print(
                f"[yellow]No validation report found ({auto_report.name}). "
                f"Run 'ucx validate prd' first, or use --report.[/yellow]"
            )

    # Read source content and extract version
    source_content = doc_path.read_text(encoding="utf-8")
    from ucx.validators.prd.artifact_ops import extract_prd_identity_fields
    fields = extract_prd_identity_fields(source_content)
    source_version = fields.get("version") or "0.0.0"

    console.print(f"[cyan]Source PRD:[/cyan] {doc_path.name}")
    console.print(f"[cyan]Doc ID:[/cyan] {doc_id}, [cyan]Version:[/cyan] {source_version}")

    if max_iterations < 1:
        console.print("[red]Error: --max-iterations must be >= 1[/red]")
        sys.exit(1)

    # Run iterative validate/fix loop on a temporary source copy
    import tempfile
    import shutil
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_file = Path(tmpdir) / doc_path.name
        shutil.copy2(doc_path, tmp_file)

        validator = UnifiedPRDValidator(strict=False, verbose=ctx.obj.get("verbose", False))
        all_actions = []
        total_iterations = 0

        console.print(f"\n[cyan]Running validate/fix loop (max iterations: {max_iterations})...[/cyan]")

        for iteration in range(1, max_iterations + 1):
            total_iterations = iteration
            val_result = validator.validate(tmp_file.parent)
            issues = val_result.tier1_issues + val_result.tier2_issues

            console.print(
                f"  Iteration {iteration}: "
                f"{len(val_result.tier1_issues)} Tier 1, {len(val_result.tier2_issues)} Tier 2 issues"
            )

            if not issues:
                console.print("  [green]Converged: no remaining issues[/green]")
                break

            # Apply deterministic fixers to temp copy
            prd_fixer = PRDFixer(dry_run=False, verbose=ctx.obj.get("verbose", False))
            fix_result = prd_fixer.fix(tmp_file, issues)
            all_actions.extend(fix_result.actions)

            applied_now = sum(1 for a in fix_result.actions if a.status == "applied")
            if not fix_result.actions:
                console.print("  [yellow]Stopped: no fix actions generated for remaining issues[/yellow]")
                break

            if applied_now == 0:
                console.print("  [yellow]Stopped: no additional auto-fixes applied this iteration[/yellow]")
                break

        # Final validation pass for residual issue reporting
        final_val_result = validator.validate(tmp_file.parent)
        remaining_issues = final_val_result.tier1_issues + final_val_result.tier2_issues
        fixed_content = tmp_file.read_text(encoding="utf-8")

    fixed_count = sum(1 for a in all_actions if a.status == "applied")
    pending_count = sum(1 for a in all_actions if a.status == "pending")
    manual_count = sum(1 for a in all_actions if a.status == "manual")
    console.print(
        f"  Total actions: {len(all_actions)} "
        f"(applied={fixed_count}, pending={pending_count}, manual={manual_count})"
    )
    console.print(f"  Iterations run: {total_iterations}")

    # Classify remaining issues: manual-handoff vs unsupported-by-fixer
    action_codes = {a.gate_code for a in all_actions}
    manual_codes = {a.gate_code for a in all_actions if a.status == "manual"}
    remaining_manual = [issue for issue in remaining_issues if issue.code in manual_codes]
    remaining_unsupported = [issue for issue in remaining_issues if issue.code not in action_codes]

    # Build validation copy with lineage metadata
    output_path, output_content = create_validation_copy(
        # Pass the source path but override content with fixed content
        doc_path,
        source_doc_id=doc_id,
        source_version=source_version,
    )
    # Merge the fixer's changes into the content before metadata injection
    # (create_validation_copy uses source_path.read_text, so we need to re-apply fixes)
    # Re-do: use fixed_content as base for metadata injection
    from ucx.validators.prd.artifact_ops import (
        inject_processing_stage_metadata,
        append_derivation_history_row,
        prd_validation_copy_name,
    )
    from datetime import datetime, timezone
    derivation_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")

    output_content = inject_processing_stage_metadata(
        fixed_content,
        processing_stage="validation-fixed",
        source_doc_id=doc_id,
        source_version=source_version,
        derived_from=doc_path.name,
    )
    output_content = append_derivation_history_row(
        output_content,
        version=source_version,
        date=derivation_date,
        author="UCX Validation Fixer",
        description=f"Derived validation-fixed copy from `{doc_path.name}` using `{prd_validation_report_name(doc_id)}`",
    )
    output_stem = prd_validation_copy_name(doc_path.stem)
    output_path = doc_path.parent / f"{output_stem}.md"

    if dry_run:
        console.print(f"\n[yellow]Dry run:[/yellow] Would create {output_path.name}")
        console.print(f"  processing_stage: validation-fixed")
        console.print(f"  derived_from: {doc_path.name}")
        console.print(f"  Fixes applied: {fixed_count}")
    else:
        output_path.write_text(output_content, encoding="utf-8")
        console.print(f"\n[green]Created:[/green] {output_path}")
        console.print(f"  processing_stage: validation-fixed")
        console.print(f"  derived_from: {doc_path.name}")
        console.print(f"  Fixes applied: {fixed_count}")
        console.print(f"\n[dim]Next: ucx review prd {output_path}[/dim]")

    if remaining_issues:
        console.print(f"\n[yellow]Remaining validation issues after loop: {len(remaining_issues)}[/yellow]")

        if remaining_manual:
            manual_counts = Counter(issue.code for issue in remaining_manual)
            summary = ", ".join(f"{code} ({count})" for code, count in sorted(manual_counts.items()))
            console.print(f"  [cyan]Manual handoff:[/cyan] {summary}")

        if remaining_unsupported:
            unsupported_counts = Counter(issue.code for issue in remaining_unsupported)
            summary = ", ".join(f"{code} ({count})" for code, count in sorted(unsupported_counts.items()))
            console.print(f"  [magenta]Unsupported by deterministic fixer:[/magenta] {summary}")
    else:
        console.print("\n[green]No remaining validation issues after loop.[/green]")


@cli.command("remediate-apply")
@click.argument("doc_type")
@click.argument("doc_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--report", "-r",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Remediation report path (required)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be created without writing files",
)
@click.pass_context
def remediate_apply(ctx, doc_type, doc_path, report, dry_run):
    """
    Create a _remediated copy from a _validation PRD (PLAN-012 Stage 6).

    Reads the ``_validation`` PRD, applies auto-safe fixes, injects
    processing-stage lineage metadata, and writes the result as a
    new ``_remediated`` copy. The ``_validation`` PRD is never modified.

    \b
    Only 'prd' is supported as doc_type for this command.

    \b
    Examples:
      ucx remediate-apply prd docs/02_PRD/PRD-01/PRD-01_platform_architecture_validation.md \\
          --report docs/02_PRD/PRD-01/PRD-01_validation_remediation_report_v001.md
      ucx remediate-apply prd ... --dry-run
    """
    import sys
    from ucx.validators.prd.artifact_ops import (
        identify_prd_artifact_stage,
        create_remediated_copy,
        inject_processing_stage_metadata,
        append_derivation_history_row,
        prd_remediated_copy_name,
        extract_prd_identity_fields,
    )
    from ucx.models.enums import DocType

    doc_path = Path(doc_path)
    report_path = Path(report)

    if doc_type.lower() != "prd":
        console.print("[red]Error: remediate-apply currently only supports 'prd'.[/red]")
        sys.exit(1)

    # Must be a _validation PRD
    stage = identify_prd_artifact_stage(doc_path)
    if stage != "validation-fixed":
        console.print(
            f"[red]Error: Input must be a _validation PRD (suffix '_validation'). "
            f"Got stage: '{stage}' for '{doc_path.name}'[/red]"
        )
        sys.exit(1)

    # Resolve doc_id from validation PRD  
    try:
        from ucx.utils.reporting import resolve_doc_id_strict
        doc_id = resolve_doc_id_strict(doc_path, DocType.PRD)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

    # Read _validation PRD content and extract version
    validation_content = doc_path.read_text(encoding="utf-8")
    fields = extract_prd_identity_fields(validation_content)
    source_version = fields.get("version") or "0.0.0"
    source_doc_id = fields.get("source_doc_id") or doc_id

    console.print(f"[cyan]Validation PRD:[/cyan] {doc_path.name}")
    console.print(f"[cyan]Doc ID:[/cyan] {source_doc_id}, [cyan]Version:[/cyan] {source_version}")

    # Parse remediation report for auto-safe UCX-ACTION blocks
    report_content = report_path.read_text(encoding="utf-8")
    applied_fixes = _apply_ucx_action_fixes(validation_content, report_content)
    fixed_count = applied_fixes["count"]
    fixed_content = applied_fixes["content"]

    if fixed_count > 0:
        console.print(f"  Applied {fixed_count} fix(es) from remediation report")
    else:
        console.print(f"  [dim]No auto-applicable fixes found in report (manual review required)[/dim]")
        fixed_content = validation_content  # Use as-is

    # Build remediated copy with lineage metadata
    from datetime import datetime, timezone
    derivation_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")

    output_content = inject_processing_stage_metadata(
        fixed_content,
        processing_stage="remediated",
        source_doc_id=source_doc_id,
        source_version=source_version,
        derived_from=doc_path.name,
    )
    output_content = append_derivation_history_row(
        output_content,
        version=source_version,
        date=derivation_date,
        author="UCX Remediation Apply",
        description=f"Derived remediated copy from `{doc_path.name}` using `{report_path.name}`",
    )
    output_stem = prd_remediated_copy_name(doc_path.stem)
    output_path = doc_path.parent / f"{output_stem}.md"

    if dry_run:
        console.print(f"\n[yellow]Dry run:[/yellow] Would create {output_path.name}")
        console.print(f"  processing_stage: remediated")
        console.print(f"  derived_from: {doc_path.name}")
        console.print(f"  Fixes applied: {fixed_count}")
    else:
        output_path.write_text(output_content, encoding="utf-8")
        console.print(f"\n[green]Created:[/green] {output_path}")
        console.print(f"  processing_stage: remediated")
        console.print(f"  derived_from: {doc_path.name}")
        console.print(f"  Fixes applied: {fixed_count}")
        console.print(f"\n[dim]Review and promote `{output_path.name}` as the final PRD version.[/dim]")


def _apply_ucx_action_fixes(content: str, report_content: str) -> dict:
    """Thin wrapper — delegates to the shared implementation in artifact_ops."""
    from ucx.validators.prd.artifact_ops import apply_ucx_action_fixes
    return apply_ucx_action_fixes(content, report_content)




@cli.command("clean-markers")
@click.argument("doc_path", type=click.Path(exists=True, path_type=Path))
def clean_markers(doc_path):
    """
    Remove LLM_COMPLETION markers from documents (v1.17.0+).

    After remediation completes semantic fixes, run this command
    to clean up the temporary markers inserted by the fixer.

    \b
    Examples:
      ucx clean-markers docs/01_BRD/BRD-01
      ucx clean-markers docs/01_BRD/
    """
    import re

    doc_path = Path(doc_path)

    # Handle file vs directory
    if doc_path.is_file():
        doc_path = doc_path.parent

    # Pattern to match marker blocks (all three lines)
    marker_pattern = re.compile(
        r'<!-- LLM_COMPLETION:[^>]+-->\n?'
        r'(?:<!-- Script:[^>]+-->\n?)?'
        r'(?:<!-- Task:[^>]+-->\n?)?',
        re.MULTILINE
    )

    cleaned_count = 0
    for md_file in doc_path.glob("**/*.md"):
        # Skip hidden directories and review reports
        if any(part.startswith('.') for part in md_file.parts):
            continue
        if "_review_report" in md_file.name.lower():
            continue

        try:
            content = md_file.read_text(encoding="utf-8")
            new_content = marker_pattern.sub('', content)

            if content != new_content:
                md_file.write_text(new_content, encoding="utf-8")
                cleaned_count += 1
                console.print(f"  [green]✓[/green] Cleaned: {md_file.name}")
        except Exception as e:
            console.print(f"  [red]✗[/red] Error in {md_file.name}: {e}")

    if cleaned_count > 0:
        console.print(f"\n[green]Cleaned markers from {cleaned_count} file(s)[/green]")
    else:
        console.print("[yellow]No markers found to clean[/yellow]")


@cli.command()
@click.option("--project-name", default="myproject", help="Project name")
@click.option("--output-dir", type=click.Path(path_type=Path), default="docs/UCX")
def init(project_name, output_dir):
    """
    Initialize UCX in a project.

    Creates UCX directory structure with symlinks to framework.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (output_dir / "creation").mkdir(exist_ok=True)
    (output_dir / "review").mkdir(exist_ok=True)
    (output_dir / "remediation").mkdir(exist_ok=True)

    # Create README
    readme = output_dir / "README.md"
    readme.write_text(f"""# UCX Configuration for {project_name}

## Quick Start

```bash
# Review a document
ucx review brd docs/01_BRD/BRD-01

# Full autopilot
ucx autopilot brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/
```

## Project-Specific Prompts

Add project-specific prompts here:
- `creation/UCC_PROMPT_BRD_PROJECT.md`
- `review/UCR_PROMPT_BRD_PROJECT.md`
- `remediation/UCRem_PROMPT_BRD_PROJECT.md`
""")

    console.print(f"[green]Initialized UCX in {output_dir}[/green]")


@cli.group()
def ai():
    """AI utility commands."""


@ai.command("probe")
@click.option(
    "--cli-tool",
    type=click.Choice(["claude", "codex", "gemini", "ollama", "aider"]),
    default=None,
    help="Override CLI tool for this probe run",
)
@click.option(
    "--model",
    default=None,
    help="Override model for this probe run",
)
@click.option(
    "--full-output",
    is_flag=True,
    help="Print raw LLM output used by the probe",
)
@click.pass_context
def ai_probe(ctx, cli_tool: Optional[str], model: Optional[str], full_output: bool):
    """Run the configured AI client's shared preflight probe."""
    base_config = ctx.obj["config"]

    # Allow probe-specific model/provider overrides without affecting other commands.
    config_updates = {}
    if cli_tool:
        config_updates["ai_mode"] = "cli"
        config_updates["cli_tool"] = cli_tool
    if model:
        config_updates["model"] = model

    config = base_config.model_copy(update=config_updates) if config_updates else base_config

    client = config.get_ai_client()
    preflight = getattr(client, "_run_availability_preflight", None)

    if preflight is None:
        raise click.ClickException(
            "Configured AI client does not support preflight probing."
        )

    provider = config.cli_tool if config.ai_mode == "cli" else "litellm"
    model_name = getattr(client, "model_id", None) or getattr(client, "model", config.model)
    console.print(
        f"[cyan]AI probe[/cyan]: mode={config.ai_mode} provider={provider} model={model_name}"
    )

    try:
        if full_output:
            details = preflight(return_details=True)
        else:
            details = preflight()
    except AIClientError as exc:
        raise click.ClickException(str(exc)) from exc

    console.print("[green]AI probe passed[/green]")

    if full_output and isinstance(details, dict):
        raw_response = details.get("phase3_response")
        if raw_response:
            console.print("[cyan]Raw LLM probe output:[/cyan]")
            console.print(raw_response)


@cli.command("config")
@click.option("--show", is_flag=True, help="Show current configuration")
@click.pass_context
def config_cmd(ctx, show):
    """Show or edit configuration."""
    if show:
        config = ctx.obj["config"]
        table = Table(title="UCX Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Model", config.model)
        table.add_row("Max Iterations", str(config.max_iterations))
        table.add_row("Min Score", str(config.min_score))
        table.add_row("Skip Drift", str(config.skip_drift))
        table.add_row("Load Skills", str(config.load_skills))
        table.add_row("Log Level", config.log_level)
        table.add_row("Web Search", str(config.enable_web_search))

        console.print(table)


def _inject_prd_validation_lineage(content: str, doc_id: str, source_prd_file: str) -> str:
    """Inject PLAN-012 lineage metadata into a PRD validation report frontmatter."""
    import re
    import yaml

    match = re.match(r"\A(---\n)(.*?)(\n---\n?)(.*)\Z", content, re.DOTALL)
    if not match:
        return content

    before, raw_fm, after_delim, body = match.groups()
    try:
        fm = yaml.safe_load(raw_fm) or {}
        if not isinstance(fm, dict):
            fm = {}
    except Exception:
        return content

    custom = fm.get("custom_fields")
    if not isinstance(custom, dict):
        custom = {}

    custom["source_artifact_file"] = source_prd_file
    custom["source_processing_stage"] = "source"

    fm["custom_fields"] = custom
    new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return f"{before}{new_fm.rstrip()}{after_delim}{body}"


def _display_result(result):
    """Display autopilot result."""
    from ucx.models.enums import Status

    table = Table(title="Autopilot Result")
    table.add_column("Metric", style="cyan")

    if result.status == Status.PASS:
        table.add_column("Value", style="green")
    elif result.status == Status.NEEDS_MANUAL:
        table.add_column("Value", style="yellow")
    else:
        table.add_column("Value", style="red")

    table.add_row("Status", result.status.value)
    table.add_row("Score", f"{result.score}/100")
    table.add_row("Iterations", str(result.iterations))
    table.add_row("Drift Detected", "Yes" if result.drift_detected else "No")
    table.add_row("P0 Findings", str(result.findings.get("P0", 0)))
    table.add_row("P1 Findings", str(result.findings.get("P1", 0)))
    table.add_row("P2 Findings", str(result.findings.get("P2", 0)))
    table.add_row("Elapsed Time", f"{result.elapsed_time:.2f}s")

    console.print(table)
    console.print(f"\nReview Report: {result.review_report}")
    if result.fix_report:
        console.print(f"Fix Report: {result.fix_report}")


# Register scoring command group
from ucx.cli.scoring import scoring
cli.add_command(scoring)

# Register prompt command group (v1.14.0)
from ucx.cli.prompts import prompt
cli.add_command(prompt)


if __name__ == "__main__":
    cli()
