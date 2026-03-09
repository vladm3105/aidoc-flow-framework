"""CLI output formatters using Rich.

Provides consistent formatting for UCX CLI output.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich.text import Text
    from rich.markdown import Markdown

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


@dataclass
class Theme:
    """Color theme for CLI output."""

    success: str = "green"
    error: str = "red"
    warning: str = "yellow"
    info: str = "blue"
    muted: str = "dim"
    highlight: str = "cyan"
    score_high: str = "green"
    score_medium: str = "yellow"
    score_low: str = "red"


class CLIFormatter:
    """
    Formats CLI output using Rich library.

    Falls back to plain text if Rich is not available.
    """

    def __init__(
        self,
        console: Optional[Any] = None,
        theme: Optional[Theme] = None,
        no_color: bool = False,
    ) -> None:
        """
        Initialize the formatter.

        Args:
            console: Rich Console instance (created if not provided)
            theme: Color theme
            no_color: Disable colors
        """
        self._theme = theme or Theme()
        self._no_color = no_color

        if RICH_AVAILABLE and not no_color:
            self._console = console or Console()
            self._rich = True
        else:
            self._console = None
            self._rich = False

    def print(self, message: str, style: Optional[str] = None) -> None:
        """Print a message with optional style."""
        if self._rich:
            self._console.print(message, style=style)
        else:
            print(message)

    def success(self, message: str) -> None:
        """Print a success message."""
        if self._rich:
            self._console.print(f"✓ {message}", style=self._theme.success)
        else:
            print(f"[OK] {message}")

    def error(self, message: str) -> None:
        """Print an error message."""
        if self._rich:
            self._console.print(f"✗ {message}", style=self._theme.error)
        else:
            print(f"[ERROR] {message}")

    def warning(self, message: str) -> None:
        """Print a warning message."""
        if self._rich:
            self._console.print(f"⚠ {message}", style=self._theme.warning)
        else:
            print(f"[WARN] {message}")

    def info(self, message: str) -> None:
        """Print an info message."""
        if self._rich:
            self._console.print(f"ℹ {message}", style=self._theme.info)
        else:
            print(f"[INFO] {message}")

    def header(self, title: str, subtitle: Optional[str] = None) -> None:
        """Print a header."""
        if self._rich:
            text = f"[bold]{title}[/bold]"
            if subtitle:
                text += f"\n[dim]{subtitle}[/dim]"
            self._console.print(Panel(text, border_style=self._theme.highlight))
        else:
            print(f"\n{'='*60}")
            print(f"  {title}")
            if subtitle:
                print(f"  {subtitle}")
            print(f"{'='*60}\n")

    def score(self, value: int, label: str = "Score") -> None:
        """Print a score with color based on value."""
        if value >= 90:
            color = self._theme.score_high
        elif value >= 70:
            color = self._theme.score_medium
        else:
            color = self._theme.score_low

        if self._rich:
            self._console.print(f"{label}: [{color}]{value}[/{color}]")
        else:
            print(f"{label}: {value}")

    def table(
        self,
        headers: list[str],
        rows: list[list[str]],
        title: Optional[str] = None,
    ) -> None:
        """Print a table."""
        if self._rich:
            table = Table(title=title)
            for header in headers:
                table.add_column(header)
            for row in rows:
                table.add_row(*row)
            self._console.print(table)
        else:
            if title:
                print(f"\n{title}")
                print("-" * len(title))
            print("\t".join(headers))
            print("-" * 40)
            for row in rows:
                print("\t".join(row))
            print()

    def findings_table(
        self,
        findings: dict[str, list[str]],
        title: str = "Review Findings",
    ) -> None:
        """Print findings table with priority grouping."""
        if self._rich:
            table = Table(title=title)
            table.add_column("Priority", style="bold")
            table.add_column("Finding")

            priority_styles = {
                "P0": "red bold",
                "P1": "yellow",
                "P2": "dim",
            }

            for priority in ["P0", "P1", "P2"]:
                items = findings.get(priority, [])
                for i, finding in enumerate(items):
                    prio_text = priority if i == 0 else ""
                    style = priority_styles.get(priority, "")
                    table.add_row(
                        Text(prio_text, style=style),
                        finding,
                    )

            self._console.print(table)
        else:
            print(f"\n{title}")
            print("=" * len(title))
            for priority in ["P0", "P1", "P2"]:
                items = findings.get(priority, [])
                if items:
                    print(f"\n{priority}:")
                    for finding in items:
                        print(f"  - {finding}")

    def document_tree(
        self,
        root: Path,
        docs: list[dict[str, Any]],
    ) -> None:
        """Print document tree structure."""
        if self._rich:
            tree = Tree(f"📁 {root}")
            for doc in docs:
                status_icon = "✓" if doc.get("status") == "pass" else "✗"
                score = doc.get("score", "?")
                tree.add(f"{status_icon} {doc['name']} ({score})")
            self._console.print(tree)
        else:
            print(f"\n{root}/")
            for doc in docs:
                status = "[PASS]" if doc.get("status") == "pass" else "[FAIL]"
                print(f"  {status} {doc['name']} ({doc.get('score', '?')})")

    def progress_bar(
        self,
        description: str = "Processing",
        total: int = 100,
    ) -> Any:
        """Get a progress bar context manager."""
        if self._rich:
            return Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=self._console,
            )
        else:
            return PlainProgress(description, total)

    def code(self, content: str, language: str = "markdown") -> None:
        """Print code with syntax highlighting."""
        if self._rich:
            syntax = Syntax(content, language, theme="monokai", line_numbers=True)
            self._console.print(syntax)
        else:
            print(content)

    def markdown(self, content: str) -> None:
        """Print rendered markdown."""
        if self._rich:
            self._console.print(Markdown(content))
        else:
            print(content)

    def panel(
        self,
        content: str,
        title: Optional[str] = None,
        style: Optional[str] = None,
    ) -> None:
        """Print content in a panel."""
        if self._rich:
            self._console.print(Panel(content, title=title, border_style=style))
        else:
            if title:
                print(f"\n--- {title} ---")
            print(content)
            if title:
                print("-" * (len(title) + 8))

    def review_summary(
        self,
        doc_type: str,
        doc_id: str,
        score: int,
        status: str,
        findings: dict[str, int],
        report_path: Optional[Path] = None,
    ) -> None:
        """Print review summary."""
        self.header(f"Review Complete: {doc_id}", f"Type: {doc_type.upper()}")
        self.score(score)

        if self._rich:
            status_style = self._theme.success if status == "PASS" else self._theme.error
            self._console.print(f"Status: [{status_style}]{status}[/{status_style}]")
        else:
            print(f"Status: {status}")

        if findings:
            rows = [[p, str(c)] for p, c in findings.items()]
            self.table(["Priority", "Count"], rows, "Findings Summary")

        if report_path:
            self.info(f"Report: {report_path}")

    def autopilot_summary(
        self,
        doc_type: str,
        target: Path,
        iterations: int,
        final_score: int,
        status: str,
        drift_detected: bool,
    ) -> None:
        """Print autopilot run summary."""
        self.header(
            f"Autopilot Complete: {target.name}",
            f"Type: {doc_type.upper()} | Iterations: {iterations}",
        )
        self.score(final_score, "Final Score")

        if self._rich:
            status_style = self._theme.success if status == "PASS" else self._theme.error
            self._console.print(f"Status: [{status_style}]{status}[/{status_style}]")

            if drift_detected:
                self._console.print(
                    f"⚠ Upstream drift detected",
                    style=self._theme.warning,
                )
        else:
            print(f"Status: {status}")
            if drift_detected:
                print("[WARN] Upstream drift detected")


class PlainProgress:
    """Plain text progress indicator for non-Rich environments."""

    def __init__(self, description: str, total: int) -> None:
        self.description = description
        self.total = total
        self._current = 0

    def __enter__(self) -> "PlainProgress":
        print(f"{self.description}...", end="", flush=True)
        return self

    def __exit__(self, *args: Any) -> None:
        print(" done.")

    def add_task(self, description: str, total: int = 100) -> int:
        """Add a task (returns task ID)."""
        return 0

    def update(self, task_id: int, advance: int = 1) -> None:
        """Update progress."""
        self._current += advance
        if self._current % 10 == 0:
            print(".", end="", flush=True)


def get_formatter(no_color: bool = False) -> CLIFormatter:
    """
    Get a CLI formatter instance.

    Args:
        no_color: Disable colors

    Returns:
        CLIFormatter instance
    """
    return CLIFormatter(no_color=no_color)
