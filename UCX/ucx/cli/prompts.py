"""CLI commands for UCX prompt inspection toolset.

This module provides CLI commands for prompt inspection,
token analysis, and section mapping.

Version: 1.14.0
"""

import json
import click
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ucx.prompts import UCPromptPhase
from ucx.prompts.exceptions import (
    DocumentNotFoundError,
    PromptFileNotFoundError,
    InvalidDocumentTypeError,
    PersonaNotFoundError,
)

console = Console()


@click.group()
def prompt():
    """Prompt inspection and analysis commands.

    \b
    Commands:
      tokens    Analyze token usage per persona
      sections  Show section inclusion matrix
      inspect   Inspect a generated prompt file
      check     Validate document for prompt generation
      generate  Generate prompts for personas

    \b
    Examples:
      ucx prompt tokens brd docs/01_BRD/BRD-01/
      ucx prompt sections brd docs/01_BRD/BRD-01/ --csv
      ucx prompt inspect tmp/prompts/prompt_architect.txt
      ucx prompt check brd docs/01_BRD/BRD-01/ --strict
      ucx prompt generate brd docs/01_BRD/BRD-01/ -o tmp/prompts/
    """
    pass


@prompt.command()
@click.argument("doc_type")
@click.argument("doc_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--personas", "-p",
    multiple=True,
    help="Specific personas to analyze (can be repeated)",
)
@click.option(
    "--budget", "-b",
    type=int,
    default=60000,
    help="Token budget per persona (default: 60000)",
)
@click.option(
    "--json", "output_json",
    is_flag=True,
    help="Output as JSON",
)
@click.option(
    "--no-dynamic",
    is_flag=True,
    help="Use static section mapping instead of dynamic",
)
def tokens(
    doc_type: str,
    doc_path: Path,
    personas: tuple,
    budget: int,
    output_json: bool,
    no_dynamic: bool,
):
    """Analyze token usage per persona.

    \b
    Examples:
      ucx prompt tokens brd docs/01_BRD/BRD-01/
      ucx prompt tokens brd docs/01_BRD/BRD-01/ -p architect -p auditor
      ucx prompt tokens brd docs/01_BRD/BRD-01/ --budget 50000
      ucx prompt tokens brd docs/01_BRD/BRD-01/ --json
    """
    try:
        api = UCPromptPhase(
            default_budget=budget,
            use_dynamic_mapping=not no_dynamic,
        )

        personas_list = list(personas) if personas else None

        if output_json:
            result = api.tokens(doc_path, doc_type, personas_list, output_format="json")
            console.print_json(json.dumps(result, indent=2))
        else:
            result = api.tokens(doc_path, doc_type, personas_list, output_format="text")
            console.print(result)

    except (DocumentNotFoundError, InvalidDocumentTypeError, PersonaNotFoundError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@prompt.command()
@click.argument("doc_type")
@click.argument("doc_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--personas", "-p",
    multiple=True,
    help="Specific personas to include (can be repeated)",
)
@click.option(
    "--json", "output_json",
    is_flag=True,
    help="Output as JSON",
)
@click.option(
    "--csv", "output_csv",
    is_flag=True,
    help="Output as CSV",
)
@click.option(
    "--no-dynamic",
    is_flag=True,
    help="Use static section mapping instead of dynamic",
)
@click.option(
    "--no-categories",
    is_flag=True,
    help="Hide category column in output",
)
def sections(
    doc_type: str,
    doc_path: Path,
    personas: tuple,
    output_json: bool,
    output_csv: bool,
    no_dynamic: bool,
    no_categories: bool,
):
    """Show section inclusion matrix.

    Shows which sections are included (FULL/OPT/IDX) or skipped (-)
    for each persona.

    \b
    Legend:
      FULL - Required section (full content included)
      OPT  - Optional section (included if space allows)
      IDX  - Index-only (title/summary only)
      -    - Skipped (not included)

    \b
    Examples:
      ucx prompt sections brd docs/01_BRD/BRD-01/
      ucx prompt sections brd docs/01_BRD/BRD-01/ --csv > matrix.csv
      ucx prompt sections brd docs/01_BRD/BRD-01/ --json
    """
    try:
        api = UCPromptPhase(use_dynamic_mapping=not no_dynamic)

        personas_list = list(personas) if personas else None

        if output_json:
            result = api.sections(doc_path, doc_type, personas_list, output_format="json")
            console.print_json(json.dumps(result, indent=2))
        elif output_csv:
            result = api.sections(doc_path, doc_type, personas_list, output_format="csv")
            console.print(result)
        else:
            from ucx.prompts.mapper import SectionMapper
            from ucx.prompts.document import DocumentLoader

            loader = DocumentLoader()
            _, doc_sections, _ = loader.load(doc_path, doc_type)

            mapper = SectionMapper(doc_sections, use_dynamic_mapping=not no_dynamic)
            matrix = mapper.build_matrix(doc_path, doc_type, personas_list)
            result = mapper.format_matrix(matrix, show_categories=not no_categories)
            console.print(result)

    except (DocumentNotFoundError, InvalidDocumentTypeError, PersonaNotFoundError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@prompt.command()
@click.argument("prompt_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--json", "output_json",
    is_flag=True,
    help="Output as JSON",
)
def inspect(prompt_path: Path, output_json: bool):
    """Inspect a generated prompt file.

    Analyzes prompt structure, token counts, section inclusion,
    and potential issues.

    \b
    Examples:
      ucx prompt inspect tmp/prompts/prompt_architect.txt
      ucx prompt inspect tmp/prompts/prompt_architect.txt --json
    """
    try:
        api = UCPromptPhase()

        if output_json:
            result = api.inspect(prompt_path, output_format="json")
            console.print_json(json.dumps(result, indent=2))
        else:
            result = api.inspect(prompt_path, output_format="text")
            console.print(result)

    except PromptFileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@prompt.command()
@click.argument("doc_type")
@click.argument("doc_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--personas", "-p",
    multiple=True,
    help="Specific personas to check (can be repeated)",
)
@click.option(
    "--strict", "-s",
    is_flag=True,
    help="Exit with error if any persona exceeds budget",
)
@click.option(
    "--budget", "-b",
    type=int,
    default=60000,
    help="Token budget per persona (default: 60000)",
)
@click.option(
    "--json", "output_json",
    is_flag=True,
    help="Output as JSON",
)
@click.option(
    "--no-dynamic",
    is_flag=True,
    help="Use static section mapping instead of dynamic",
)
def check(
    doc_type: str,
    doc_path: Path,
    personas: tuple,
    strict: bool,
    budget: int,
    output_json: bool,
    no_dynamic: bool,
):
    """Validate document for prompt generation.

    Checks document structure, section count, and token budgets
    for all personas.

    \b
    Exit codes:
      0 - All checks passed
      1 - Errors detected (missing sections, strict budget violations)

    \b
    Examples:
      ucx prompt check brd docs/01_BRD/BRD-01/
      ucx prompt check brd docs/01_BRD/BRD-01/ --strict
      ucx prompt check brd docs/01_BRD/BRD-01/ --budget 50000
      ucx prompt check brd docs/01_BRD/BRD-01/ --json
    """
    try:
        api = UCPromptPhase(
            default_budget=budget,
            use_dynamic_mapping=not no_dynamic,
        )

        personas_list = list(personas) if personas else None
        result = api.check(doc_path, doc_type, strict=strict, personas=personas_list)

        if output_json:
            console.print_json(json.dumps(result.to_json(), indent=2))
        else:
            # Format as rich output
            status = "[green]PASSED[/green]" if result.passed else "[red]FAILED[/red]"

            console.print(Panel(
                f"Status: {status}\n"
                f"Document: {result.doc_path}\n"
                f"Type: {result.doc_type.upper()}\n"
                f"Sections: {result.section_count}\n"
                f"Characters: {result.document_chars:,}\n"
                f"Personas in budget: {result.personas_in_budget}/{result.personas_total}",
                title="PROMPT CHECK RESULT",
            ))

            if result.warnings:
                console.print("\n[yellow]Warnings:[/yellow]")
                for warning in result.warnings:
                    console.print(f"  [yellow]![/yellow] {warning}")

            if result.errors:
                console.print("\n[red]Errors:[/red]")
                for error in result.errors:
                    console.print(f"  [red]X[/red] {error}")

        # Exit with appropriate code
        if not result.passed:
            raise SystemExit(result.exit_code)

    except (DocumentNotFoundError, InvalidDocumentTypeError, PersonaNotFoundError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@prompt.command()
@click.argument("doc_type")
@click.argument("doc_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    help="Output directory (default: doc_path/.ucx_review_session)",
)
@click.option(
    "--personas", "-p",
    multiple=True,
    help="Specific personas to generate (can be repeated)",
)
@click.option(
    "--no-metadata",
    is_flag=True,
    help="Don't generate .meta.json files",
)
@click.option(
    "--no-dynamic",
    is_flag=True,
    help="Use static section mapping instead of dynamic",
)
@click.option(
    "--json", "output_json",
    is_flag=True,
    help="Output result as JSON",
)
def generate(
    doc_type: str,
    doc_path: Path,
    output: Optional[Path],
    personas: tuple,
    no_metadata: bool,
    no_dynamic: bool,
    output_json: bool,
):
    """Generate prompts for personas.

    Creates prompt files for each persona with filtered document
    sections based on persona relevance mapping.

    \b
    Output files:
      prompt_{persona}.txt      - Prompt content
      prompt_{persona}.meta.json - Metadata (unless --no-metadata)

    \b
    Examples:
      ucx prompt generate brd docs/01_BRD/BRD-01/
      ucx prompt generate brd docs/01_BRD/BRD-01/ -o tmp/prompts/
      ucx prompt generate brd docs/01_BRD/BRD-01/ -p architect -p auditor
    """
    try:
        api = UCPromptPhase(use_dynamic_mapping=not no_dynamic)

        personas_list = list(personas) if personas else None

        result = api.generate(
            doc_path=doc_path,
            doc_type=doc_type,
            personas=personas_list,
            output_dir=output,
            include_metadata=not no_metadata,
        )

        if output_json:
            console.print_json(json.dumps(result.to_json(), indent=2))
        else:
            # Format as rich output
            console.print(Panel(
                f"Document: {result.doc_path}\n"
                f"Type: {result.doc_type.upper()}\n"
                f"Output: {result.output_dir}\n"
                f"Prompts: {len(result.prompts)}\n"
                f"Total tokens: {result.total_tokens:,}",
                title="PROMPT GENERATION RESULT",
            ))

            # Show per-persona summary
            table = Table(title="Generated Prompts")
            table.add_column("Persona", style="cyan")
            table.add_column("Tokens", justify="right")
            table.add_column("Sections", justify="right")
            table.add_column("Index-only", justify="right")
            table.add_column("Warnings", justify="right")

            for p in result.prompts:
                warnings = str(len(p.warnings)) if p.warnings else "-"
                table.add_row(
                    p.persona,
                    f"{p.token_estimate:,}",
                    str(len(p.sections_included)),
                    str(len(p.sections_index_only)),
                    warnings,
                )

            console.print(table)

            # Show errors if any
            if result.errors:
                console.print("\n[red]Errors:[/red]")
                for error in result.errors:
                    console.print(f"  [red]X[/red] {error}")

    except (DocumentNotFoundError, InvalidDocumentTypeError, PersonaNotFoundError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


# Alias for backwards compatibility
@prompt.command(name="info")
@click.argument("doc_type")
@click.argument("doc_path", type=click.Path(exists=True, path_type=Path))
def info(doc_type: str, doc_path: Path):
    """Get basic document information.

    \b
    Examples:
      ucx prompt info brd docs/01_BRD/BRD-01/
    """
    try:
        api = UCPromptPhase()
        result = api.get_document_info(doc_path, doc_type)

        console.print(Panel(
            f"Path: {result['path']}\n"
            f"Type: {result['type'].upper()}\n"
            f"Directory: {result['is_directory']}\n"
            f"Sections: {result['section_count']}\n"
            f"Characters: {result['total_chars']:,}\n"
            f"Tokens: {result['total_tokens']:,}",
            title="DOCUMENT INFO",
        ))

        if result['sections']:
            console.print("\nSections:")
            for section in result['sections']:
                console.print(f"  - {section}")

    except (DocumentNotFoundError, InvalidDocumentTypeError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()
