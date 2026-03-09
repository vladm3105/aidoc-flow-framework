"""UCX CLI main entry point."""

import click
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from ucx.version import __version__
from ucx.config.settings import UCXConfig

console = Console()


@click.group()
@click.version_option(__version__, prog_name="ucx")
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Minimal output")
@click.pass_context
def cli(ctx, config: Optional[Path], verbose: bool, quiet: bool):
    """UCX - Unified Context Framework for AI-driven document lifecycle management."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet

    if config:
        ctx.obj["config"] = UCXConfig.from_yaml(config)
    else:
        ctx.obj["config"] = UCXConfig()


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
@click.pass_context
def review(ctx, doc_type, doc_path, output, skip_validation):
    """
    Review a document (UCR phase).

    \b
    Examples:
      ucx review brd docs/01_BRD/BRD-01
      ucx review prd docs/02_PRD/PRD-01.md -o review_report.md
    """
    from ucx import UCRPhase

    ucr = UCRPhase(ctx.obj["config"])
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
      ucx remediate BRD_UCR_REVIEW.md docs/01_BRD/BRD-01
      ucx remediate BRD_UCR_REVIEW.md docs/01_BRD/BRD-01 --apply-auto-safe
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
@click.pass_context
def validate(ctx, doc_type, doc_path):
    """
    Validate a document (no AI review).

    \b
    Examples:
      ucx validate brd docs/01_BRD/BRD-01
    """
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
