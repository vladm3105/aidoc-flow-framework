import typer
import re
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import track
from pathlib import Path
from typing import Optional

app = typer.Typer()
console = Console()

@app.command()
def analyze(
    file_path: str = typer.Argument(..., help="Path to the log file"),
    format: str = typer.Option("text", help="Format of the log file: text or jsonl"),
    error_keywords: str = typer.Option("Error,Exception,Fail", help="Comma-separated keywords to count as errors")
):
    """
    Analyze a log file and generate a Battle Report.
    """
    path = Path(file_path)
    if not path.exists():
        console.print(f"[bold red]File not found: {file_path}[/bold red]")
        raise typer.Exit(code=1)

    console.print(f"[bold green]Analyzing {file_path}...[/bold green]")

    # Metrics
    total_lines = 0
    error_counts = {k: 0 for k in error_keywords.split(",")}
    total_tokens = 0
    token_pattern = re.compile(r"Tokens Used:?\s*(\d+)", re.IGNORECASE)
    
    # Process
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            total_lines = len(lines)
            
            for line in track(lines, description="Processing lines..."):
                # 1. Error Counting
                for kw in error_counts:
                    if kw.lower() in line.lower():
                        error_counts[kw] += 1
                
                # 2. Token Counting
                match = token_pattern.search(line)
                if match:
                    total_tokens += int(match.group(1))

    except Exception as e:
        console.print(f"[bold red]Error reading file: {e}[/bold red]")
        raise typer.Exit(code=1)

    # Report
    table = Table(title="Battle Report")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Total Events/Lines", str(total_lines))
    table.add_row("Total Tokens Detected", f"{total_tokens:,}")
    
    # Cost Estimate (Roughly $5 / 1M input tokens blend)
    est_cost = (total_tokens / 1_000_000) * 5.0
    table.add_row("Est. Cost (at $5/1M)", f"${est_cost:.4f}")

    console.print(table)

    # Errors
    err_table = Table(title="Defects Found")
    err_table.add_column("Keyword", style="red")
    err_table.add_column("Count", style="white")
    
    total_errors = 0
    for kw, count in error_counts.items():
        err_table.add_row(kw, str(count))
        total_errors += count
    
    console.print(err_table)
    
    error_rate = (total_errors / total_lines * 100) if total_lines > 0 else 0
    console.print(f"[bold]Error Rate:[/bold] {error_rate:.2f}%")

if __name__ == "__main__":
    app()
