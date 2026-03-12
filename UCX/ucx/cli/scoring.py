"""UCX CLI scoring commands."""

import click
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
def scoring():
    """Scoring configuration and analysis commands.

    \b
    Commands:
      show      - Show scoring weights for a document type
      validate  - Validate a scoring configuration file
      compare   - Compare weighted vs legacy scoring for a report
    """
    pass


@scoring.command()
@click.argument("doc_type")
@click.option("--format", "-f", type=click.Choice(["table", "yaml"]), default="table")
def show(doc_type: str, format: str):
    """Show scoring weights for a document type.

    \b
    Examples:
      ucx scoring show brd
      ucx scoring show prd --format yaml
    """
    from ucx.scoring import load_weights, ScoringConfigError, Category

    try:
        weights = load_weights(doc_type)
    except ScoringConfigError as e:
        console.print(f"[red]Error loading weights:[/red] {e}")
        raise SystemExit(1)

    if format == "yaml":
        import yaml
        data = {
            "doc_type": weights.doc_type,
            "categories": {},
            "thresholds": {
                "pass": weights.thresholds.pass_threshold,
                "warn": weights.thresholds.warn_threshold,
                "fail": weights.thresholds.fail_threshold,
            },
        }
        for cat_name, cat in weights.categories.items():
            data["categories"][cat_name] = {
                "weight": cat.weight,
                "weight_percent": f"{cat.weight_percent:.1f}%",
                "max_deduction": cat.max_deduction,
            }
        console.print(yaml.dump(data, default_flow_style=False))
    else:
        table = Table(title=f"Scoring Weights: {doc_type.upper()}")
        table.add_column("Category", style="cyan")
        table.add_column("Weight", justify="right")
        table.add_column("Max Deduction", justify="right")
        table.add_column("Element Codes", style="dim")

        total_weight = 0.0
        for cat_name, cat in sorted(weights.categories.items()):
            codes_str = ", ".join(str(c) for c in cat.element_codes[:5])
            if len(cat.element_codes) > 5:
                codes_str += "..."
            table.add_row(
                cat_name,
                f"{cat.weight_percent:.1f}%",
                f"-{cat.max_deduction}",
                codes_str or "(keywords)",
            )
            total_weight += cat.weight

        table.add_section()
        table.add_row(
            "[bold]Total[/bold]",
            f"[bold]{total_weight * 100:.1f}%[/bold]",
            "-100",
            "",
        )

        console.print(table)

        console.print(f"\n[dim]Thresholds: Pass >= {weights.thresholds.pass_threshold}, "
                     f"Warn >= {weights.thresholds.warn_threshold}[/dim]")


@scoring.command()
@click.argument("config_path", type=click.Path(exists=True, path_type=Path))
def validate(config_path: Path):
    """Validate a scoring configuration file.

    \b
    Examples:
      ucx scoring validate docs/UCX/scoring_weights.yaml
    """
    from ucx.scoring import validate_config_file

    errors = validate_config_file(config_path)

    if errors:
        console.print(f"[red]Validation failed:[/red] {len(errors)} error(s)")
        for error in errors:
            console.print(f"  - {error}")
        raise SystemExit(1)
    else:
        console.print(f"[green]Validation passed:[/green] {config_path}")


@scoring.command()
@click.argument("report_path", type=click.Path(exists=True, path_type=Path))
@click.option("--verbose", "-v", is_flag=True)
def compare(report_path: Path, verbose: bool):
    """Compare weighted vs legacy scoring for a report.

    Parses a review report and shows both scoring methods.

    \b
    Examples:
      ucx scoring compare docs/01_BRD/BRD-01.UCR_review_report_v002.md
    """
    import re

    # Read the report
    content = report_path.read_text()

    # Extract P0/P1/P2 counts from manifest or report
    # Look for patterns like "P0=274, P1=98, P2=9" or table format
    p0_match = re.search(r"P0[=:]\s*(\d+)", content)
    p1_match = re.search(r"P1[=:]\s*(\d+)", content)
    p2_match = re.search(r"P2[=:]\s*(\d+)", content)

    if not (p0_match and p1_match and p2_match):
        # Try table format
        table_match = re.search(
            r"\|\s*\*\*Total\*\*\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)",
            content
        )
        if table_match:
            p0_count = int(table_match.group(1))
            p1_count = int(table_match.group(2))
            p2_count = int(table_match.group(3))
        else:
            console.print("[red]Could not extract P0/P1/P2 counts from report[/red]")
            console.print("Expected format: 'P0=N, P1=N, P2=N' or category summary table")
            raise SystemExit(1)
    else:
        p0_count = int(p0_match.group(1))
        p1_count = int(p1_match.group(1))
        p2_count = int(p2_match.group(1))

    # Calculate legacy score
    from ucx.scoring import calculate_legacy_score
    legacy_score = calculate_legacy_score(p0_count, p1_count, p2_count)

    # Try to extract weighted score from report
    weighted_match = re.search(
        r"(?:Weighted Score|Score)[:\s]+(\d+(?:\.\d+)?)\s*/\s*100",
        content
    )
    weighted_score = float(weighted_match.group(1)) if weighted_match else None

    # Display comparison
    table = Table(title="Score Comparison")
    table.add_column("Method", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Status")

    table.add_row(
        "Legacy (P0*10 + P1*3 + P2*1)",
        f"{legacy_score}/100",
        _get_status_str(legacy_score) if legacy_score >= 0 else "[red]NEGATIVE[/red]",
    )

    if weighted_score is not None:
        table.add_row(
            "Weighted (category-based)",
            f"{weighted_score:.1f}/100",
            _get_status_str(weighted_score),
        )
    else:
        table.add_row(
            "Weighted (category-based)",
            "[dim]Not available[/dim]",
            "[dim]Run with UCX v1.12.0+ to get weighted score[/dim]",
        )

    console.print(table)

    console.print(f"\n[dim]Finding counts: P0={p0_count}, P1={p1_count}, P2={p2_count}[/dim]")

    if verbose:
        console.print("\n[bold]Legacy Score Formula:[/bold]")
        console.print(f"  100 - ({p0_count} * 10) - ({p1_count} * 3) - ({p2_count} * 1)")
        console.print(f"  100 - {p0_count * 10} - {p1_count * 3} - {p2_count * 1}")
        console.print(f"  = {legacy_score}")

        if legacy_score < 0:
            console.print("\n[yellow]Warning: Legacy score went negative due to no deduction caps.[/yellow]")
            console.print("Category-weighted scoring prevents this with per-category caps.")


def _get_status_str(score: float) -> str:
    """Get status string for a score."""
    if score >= 85:
        return "[green]PASS[/green]"
    elif score >= 70:
        return "[yellow]WARN[/yellow]"
    else:
        return "[red]FAIL[/red]"
