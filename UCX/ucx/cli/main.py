"""UCX CLI main entry point."""

import click
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from ucx.version import __version__
from ucx.config.settings import UCXConfig
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
    type=click.Choice(["claude", "gemini", "ollama", "aider"]),
    default="claude",
    help="CLI tool to use in cli mode",
)
@click.option(
    "--model",
    default=None,
    help="AI model: opus/sonnet/haiku for Claude CLI (default: opus), or provider/model for API mode",
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
    Two modes of operation:
      cli  - Execute CLI agents (claude, gemini, ollama) via shell commands
      api  - Direct API calls via LiteLLM (requires API key)

    \b
    Web Search:
      Use --enable-web-search (-W) to enable internet search for:
      - Fact-checking regulatory references (FinCEN, OFAC, PCI-DSS)
      - Verifying technology best practices and patterns
      - Finding solutions to identified issues
      - Validating partner API documentation

    \b
    Examples:
      ucx --mode cli --cli-tool claude review brd docs/01_BRD/BRD-01/
      ucx --mode api --model opus review brd docs/01_BRD/BRD-01/
      ucx -p docs/UCX/ review brd docs/01_BRD/BRD-01/  # Use project prompts
      ucx -W review brd docs/01_BRD/BRD-01/  # With web search enabled
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
@click.pass_context
def create(ctx, doc_type, output_path, **kwargs):
    """
    Create a new document (UCC phase).

    \b
    Examples:
      ucx create brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/
      ucx create prd docs/02_PRD/PRD-01.md --from-upstream docs/01_BRD/BRD-01
    """
    from ucx import UCCPhase

    ucc = UCCPhase(ctx.obj["config"])
    doc = ucc.create(doc_type, output_path, **kwargs)
    console.print(f"[green]Created:[/green] {doc.path}")


@cli.command()
@click.argument("doc_type")
@click.argument("doc_path", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path))
@click.option("--skip-validation", is_flag=True)
@click.option("--multi-turn", "-m", is_flag=True, help="Use multi-turn persona review with memory")
@click.option("--no-resume", is_flag=True, help="Start fresh (don't resume from previous session)")
@click.option("--session-ttl", type=int, default=24, help="Session TTL in hours (default: 24)")
@click.option("--clean-memory", is_flag=True, help="Clean up stale session memory and exit")
@click.option("--clean-reports", is_flag=True, help="Clean up old review reports, keep only latest (or --keep-versions)")
@click.option("--keep-versions", type=int, default=1, help="Number of report versions to keep (default: 1)")
@click.option("--clean-all", is_flag=True, help="Clean up both session memory and old reports")
@click.option("--model", default=None, help="Model to use (opus, sonnet, haiku for CLI; or full model name for API)")
@click.option("--force-single", is_flag=True, help="Force single-turn mode (bypass auto multi-turn for large docs)")
@click.pass_context
def review(ctx, doc_type, doc_path, output, skip_validation, multi_turn, no_resume, session_ttl, clean_memory, clean_reports, keep_versions, clean_all, model, force_single):
    """
    Review a document (UCR phase).

    \b
    Examples:
      ucx review brd docs/01_BRD/BRD-01
      ucx review brd docs/01_BRD/BRD-01 --multi-turn
      ucx review brd docs/01_BRD/BRD-01 --multi-turn --session-ttl 48
      ucx review prd docs/02_PRD/PRD-01.md -o review_report.md
      ucx review brd docs/01_BRD/BRD-01 --clean-memory
      ucx review brd docs/01_BRD/BRD-01 --clean-reports
      ucx review brd docs/01_BRD/BRD-01 --clean-all
    """
    import shutil
    import os
    from ucx import UCRPhase

    doc_path = Path(doc_path)

    # Handle --clean-all flag (combines --clean-memory and --clean-reports)
    if clean_all:
        clean_memory = True
        clean_reports = True

    # Handle --clean-memory flag
    if clean_memory:
        memory_dir = doc_path / ".doc_review_memory"
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
        report_patterns = ["*.UCR_review_report_v*.md", "*_UCR_REVIEW*.md", "*UCR_REVIEW*.md", "*_UCRem_*.md", "*PERSONA_REVIEW*.md"]
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
        search_path = doc_path if doc_path.is_dir() else doc_path.parent
        project_dir = None
        while search_path.parent != search_path:
            if (search_path / "docs" / "UCX").exists():
                project_dir = search_path
                break
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

    # Auto-detect large documents and recommend multi-turn (unless --force-single)
    if not multi_turn and not force_single:
        # Calculate document size
        total_chars = 0
        if doc_path.is_dir():
            for f in doc_path.glob("*.md"):
                if "REVIEW" not in f.name and "REPORT" not in f.name:
                    total_chars += f.stat().st_size
        else:
            total_chars = doc_path.stat().st_size

        # Large documents (>100K chars / ~25K tokens) should use multi-turn
        if total_chars > 100000:
            console.print(
                f"[yellow]Large document detected ({total_chars // 1000}K chars). "
                f"Auto-enabling multi-turn mode for better quality.[/yellow]"
            )
            multi_turn = True

    if multi_turn:
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
@click.argument("doc_path", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path))
@click.option("--apply-auto-safe", is_flag=True, help="Apply auto-safe fixes")
@click.pass_context
def remediate(ctx, review_report, doc_path, output, apply_auto_safe):
    """
    Generate fixes from review report (UCRem phase).

    \b
    Examples:
      ucx remediate BRD-01.UCR_review_report_v001.md docs/01_BRD/BRD-01
      ucx remediate BRD-01.UCR_review_report_v001.md docs/01_BRD/BRD-01 --apply-auto-safe
    """
    from ucx import UCRemPhase
    from ucx.models.enums import Confidence

    ucrem = UCRemPhase(ctx.obj["config"])
    fixes = ucrem.generate_fixes(review_report, doc_path, output_path=output)

    auto_safe = [f for f in fixes if f.confidence == Confidence.AUTO_SAFE]
    auto_assisted = [f for f in fixes if f.confidence == Confidence.AUTO_ASSISTED]
    manual = [f for f in fixes if f.confidence == Confidence.MANUAL_REQUIRED]

    console.print(f"Fixes: auto-safe={len(auto_safe)}, auto-assisted={len(auto_assisted)}, manual={len(manual)}")

    if apply_auto_safe and auto_safe:
        applied = ucrem.apply_auto_safe(fixes)
        console.print(f"[green]Applied {len(applied)} auto-safe fixes[/green]")


@cli.command()
@click.argument("doc_type")
@click.argument("doc_path", type=click.Path(exists=True, path_type=Path))
@click.option("--tier1-only", is_flag=True, help="Run only Tier 1 (core) checks for pre-commit")
@click.option("--strict", is_flag=True, help="Treat warnings as errors")
@click.option("--format", "output_format", type=click.Choice(["text", "json"]), default="text", help="Output format")
@click.pass_context
def validate(ctx, doc_type, doc_path, tier1_only, strict, output_format):
    """
    Validate a document (no AI review).

    \b
    Tiered validation:
      Tier 1 (Core, blocking): Element codes, structure, metadata, quality gates
      Tier 2 (Advisory): Links, references, diagrams, glossary

    \b
    Examples:
      ucx validate brd docs/01_BRD/BRD-01
      ucx validate brd docs/01_BRD/BRD-01 --tier1-only
      ucx validate brd docs/01_BRD/BRD-01 --strict --format json
    """
    import json
    import sys

    doc_type_lower = doc_type.lower()

    # Use unified validator for BRD
    if doc_type_lower == "brd":
        from ucx.validators.brd import UnifiedBRDValidator

        validator = UnifiedBRDValidator(strict=strict, verbose=ctx.obj.get("verbose", False))
        result = validator.validate(Path(doc_path), tier1_only=tier1_only)

        if output_format == "json":
            console.print_json(data=result.to_dict())
        else:
            console.print(result.format_text(verbose=ctx.obj.get("verbose", False)))

        # Exit with appropriate code
        sys.exit(result.exit_code(strict=strict))
    else:
        # Fallback to legacy validator for other types
        from ucx import UCRPhase

        ucr = UCRPhase(ctx.obj["config"])
        result = ucr.validate(doc_type, Path(doc_path))

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

        # Exit with appropriate code
        if result.errors:
            sys.exit(2)
        elif result.warnings and strict:
            sys.exit(2)
        elif result.warnings:
            sys.exit(1)
        else:
            sys.exit(0)


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


if __name__ == "__main__":
    cli()
