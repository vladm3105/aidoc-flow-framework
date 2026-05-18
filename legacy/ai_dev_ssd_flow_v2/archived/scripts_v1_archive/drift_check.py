#!/usr/bin/env python3
"""
drift_check.py - Detect documentation drift

Traceability: @brd: BRD-01:FR-02
SPEC Reference: SPEC-02

This script compares artifact modification dates against GitHub issue close dates
to detect when documentation becomes stale relative to completed work.
"""

import os
import sys
import re
import fnmatch
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any

import click
import yaml
from github import Github, GithubException
from rich.console import Console
from rich.table import Table
from dateutil import parser as date_parser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
console = Console()


@dataclass
class Artifact:
    """Represents an SDD artifact file."""
    path: Path
    artifact_type: str
    layer: int
    last_modified: datetime
    tasks_refs: List[str] = field(default_factory=list)


@dataclass
class DriftStatus:
    """Status of documentation drift for an artifact."""
    artifact: Artifact
    drift_days: int
    related_issues: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "current"  # current, warning, stale


class ConfigLoader:
    """Load drift check configuration."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self._find_config()
        self.config = self._load_config() if self.config_path.exists() else {}

    def _find_config(self) -> Path:
        candidates = [
            Path("ucx_flow_v3/PROJECT/config/project_model.yaml"),
            Path("PROJECT/config/project_model.yaml"),
            Path("config/project_model.yaml"),
        ]
        for path in candidates:
            if path.exists():
                return path
        return Path("project_model.yaml")

    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value


class ArtifactScanner:
    """Scan directory for SDD artifacts."""

    # Layer mapping based on directory structure
    LAYER_MAP = {
        'BRD': 1, 'PRD': 2, 'EARS': 3, 'BDD': 4,
        'ADR': 5, 'SYS': 6, 'REQ': 7, 'CTR': 8,
        'SPEC': 9, 'TSPEC': 10, 'TASKS': 11,
    }

    # File extensions to scan
    EXTENSIONS = {'.md', '.yaml', '.yml', '.feature'}

    def __init__(self, config: Optional[ConfigLoader] = None):
        self.config = config
        self.excluded_patterns = []
        if config:
            self.excluded_patterns = config.get('drift_check.excluded_patterns', [])

    def scan_directory(self, path: Path) -> List[Artifact]:
        """Scan directory for SDD artifacts."""
        artifacts = []
        for file_path in path.rglob('*'):
            if not file_path.is_file():
                continue
            if file_path.suffix not in self.EXTENSIONS:
                continue
            if self._is_excluded(file_path):
                continue

            artifact = self._parse_artifact(file_path)
            if artifact:
                artifacts.append(artifact)

        return artifacts

    def _is_excluded(self, path: Path) -> bool:
        """Check if path matches exclusion patterns."""
        path_str = str(path)
        for pattern in self.excluded_patterns:
            if fnmatch.fnmatch(path_str, pattern):
                return True
        return False

    def _parse_artifact(self, file_path: Path) -> Optional[Artifact]:
        """Parse file to create Artifact instance."""
        artifact_type = self._detect_type(file_path)
        if not artifact_type:
            return None

        layer = self.LAYER_MAP.get(artifact_type, 0)
        last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
        tasks_refs = self._extract_tasks_refs(file_path)

        return Artifact(
            path=file_path,
            artifact_type=artifact_type,
            layer=layer,
            last_modified=last_modified,
            tasks_refs=tasks_refs,
        )

    def _detect_type(self, path: Path) -> Optional[str]:
        """Detect artifact type from file path or content."""
        name = path.stem.upper()

        # Check filename prefix
        for artifact_type in self.LAYER_MAP:
            if name.startswith(artifact_type):
                return artifact_type

        # Check parent directory
        parent = path.parent.name.upper()
        for artifact_type in self.LAYER_MAP:
            if artifact_type in parent:
                return artifact_type

        return None

    def _extract_tasks_refs(self, file_path: Path) -> List[str]:
        """Extract TASKS references from file content."""
        refs = []
        try:
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read()

            # Match @tasks: TASKS-NN.TT.SS or TASKS-NN patterns
            patterns = [
                r'@tasks:\s*(TASKS-[\d.]+)',
                r'TASKS-([\d.]+)',
            ]
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if not match.startswith('TASKS-'):
                        match = f'TASKS-{match}'
                    if match not in refs:
                        refs.append(match)
        except Exception as e:
            logger.debug(f"Error reading {file_path}: {e}")

        return refs

    def get_last_modified(self, artifact: Artifact) -> datetime:
        """Get last modification time of artifact."""
        return artifact.last_modified

    def extract_tasks_refs(self, artifact: Artifact) -> List[str]:
        """Get TASKS references from artifact."""
        return artifact.tasks_refs


class GitHubIssueQuery:
    """Query GitHub for issue information."""

    def __init__(self, repo: str, token: str):
        self.gh = Github(token)
        self.repo = self.gh.get_repo(repo)

    def get_closed_issues(self, sprint: Optional[str] = None,
                          since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get closed issues, optionally filtered by sprint."""
        issues = []
        state = "closed"
        sort = "updated"
        direction = "desc"

        try:
            for issue in self.repo.get_issues(state=state, sort=sort, direction=direction):
                if since and issue.closed_at and issue.closed_at < since:
                    break

                # Filter by sprint if specified
                if sprint:
                    sprint_match = False
                    for label in issue.labels:
                        if sprint.lower() in label.name.lower():
                            sprint_match = True
                            break
                    if not sprint_match:
                        continue

                issue_data = {
                    'number': issue.number,
                    'title': issue.title,
                    'closed_at': issue.closed_at,
                    'labels': [l.name for l in issue.labels],
                    'tasks_id': self._extract_tasks_id(issue.title),
                }
                issues.append(issue_data)

        except GithubException as e:
            logger.error(f"Error querying issues: {e}")

        return issues

    def _extract_tasks_id(self, title: str) -> Optional[str]:
        """Extract TASKS ID from issue title."""
        match = re.search(r'TASKS-[\d.]+', title)
        return match.group(0) if match else None

    def get_issue_close_date(self, issue: Dict[str, Any]) -> Optional[datetime]:
        """Get close date of issue."""
        return issue.get('closed_at')


class DriftAnalyzer:
    """Analyze documentation drift."""

    def __init__(self, max_age_days: int = 14, warning_threshold: int = 7):
        self.max_age_days = max_age_days
        self.warning_threshold = warning_threshold

    def compare_timestamps(self, artifact: Artifact,
                           issues: List[Dict[str, Any]]) -> DriftStatus:
        """Compare artifact timestamp with related issues."""
        related = []

        # Find issues related to this artifact
        for issue in issues:
            tasks_id = issue.get('tasks_id')
            if tasks_id and tasks_id in artifact.tasks_refs:
                related.append(issue)

        # Calculate drift
        drift_days = self.calculate_drift_days(artifact, related)

        # Determine status
        if drift_days > self.max_age_days:
            status = "stale"
        elif drift_days > self.warning_threshold:
            status = "warning"
        else:
            status = "current"

        return DriftStatus(
            artifact=artifact,
            drift_days=drift_days,
            related_issues=related,
            status=status,
        )

    def calculate_drift_days(self, artifact: Artifact,
                             related_issues: List[Dict[str, Any]]) -> int:
        """Calculate days of drift."""
        now = datetime.now()

        # If no related issues, check artifact age
        if not related_issues:
            delta = now - artifact.last_modified
            return delta.days

        # Find most recent related issue close date
        latest_close = None
        for issue in related_issues:
            close_date = issue.get('closed_at')
            if close_date:
                if not latest_close or close_date > latest_close:
                    latest_close = close_date

        if not latest_close:
            return 0

        # Drift = issue closed after artifact was last modified
        if latest_close > artifact.last_modified:
            delta = latest_close - artifact.last_modified
            return delta.days

        return 0

    def generate_report(self, drifts: List[DriftStatus]) -> str:
        """Generate markdown drift report."""
        lines = [
            "# Documentation Drift Report",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Threshold**: {self.max_age_days} days",
            "",
        ]

        # Summary
        stale = sum(1 for d in drifts if d.status == "stale")
        warning = sum(1 for d in drifts if d.status == "warning")
        current = sum(1 for d in drifts if d.status == "current")

        lines.extend([
            "## Summary",
            "",
            f"- **Stale**: {stale}",
            f"- **Warning**: {warning}",
            f"- **Current**: {current}",
            f"- **Total**: {len(drifts)}",
            "",
        ])

        # Stale artifacts
        if stale > 0:
            lines.extend([
                "## Stale Artifacts",
                "",
                "| Artifact | Type | Drift (days) | Related Issues |",
                "|----------|------|--------------|----------------|",
            ])
            for d in drifts:
                if d.status == "stale":
                    issues = ", ".join(f"#{i['number']}" for i in d.related_issues[:3])
                    lines.append(f"| {d.artifact.path.name} | {d.artifact.artifact_type} | {d.drift_days} | {issues} |")
            lines.append("")

        # Warning artifacts
        if warning > 0:
            lines.extend([
                "## Warning Artifacts",
                "",
                "| Artifact | Type | Drift (days) | Last Modified |",
                "|----------|------|--------------|---------------|",
            ])
            for d in drifts:
                if d.status == "warning":
                    modified = d.artifact.last_modified.strftime('%Y-%m-%d')
                    lines.append(f"| {d.artifact.path.name} | {d.artifact.artifact_type} | {d.drift_days} | {modified} |")
            lines.append("")

        # Recommendations
        lines.extend([
            "## Recommendations",
            "",
            "1. Review stale artifacts and update to reflect completed work",
            "2. Check warning artifacts for potential updates needed",
            "3. Ensure TASKS references are properly linked to artifacts",
            "",
        ])

        return "\n".join(lines)


def display_drift_table(drifts: List[DriftStatus]):
    """Display drift status as rich table."""
    table = Table(title="Documentation Drift Analysis")
    table.add_column("Artifact", style="cyan")
    table.add_column("Type", style="white")
    table.add_column("Layer", style="yellow")
    table.add_column("Drift (days)", style="magenta")
    table.add_column("Status", style="bold")

    for d in sorted(drifts, key=lambda x: x.drift_days, reverse=True):
        status_style = {
            "stale": "[red]STALE[/red]",
            "warning": "[yellow]WARNING[/yellow]",
            "current": "[green]OK[/green]",
        }.get(d.status, d.status)

        table.add_row(
            d.artifact.path.name,
            d.artifact.artifact_type,
            str(d.artifact.layer),
            str(d.drift_days),
            status_style,
        )

    console.print(table)


@click.command()
@click.option('--sdd-root', '-d', required=True, type=click.Path(exists=True),
              help='Root directory of SDD documentation')
@click.option('--repo', '-r', required=True, help='GitHub repository (owner/repo)')
@click.option('--github-project', '-p', type=int, default=None,
              help='GitHub Project V2 board number')
@click.option('--max-age-days', '-m', type=int, default=14,
              help='Maximum age in days before artifact is considered stale')
@click.option('--report', '-o', type=click.Path(), default=None,
              help='Output path for markdown report')
@click.option('--config', '-c', type=click.Path(exists=True), default=None,
              help='Path to project_model.yaml')
@click.option('--sprint', '-s', default=None, help='Filter issues by sprint')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(sdd_root: str, repo: str, github_project: Optional[int], max_age_days: int,
         report: Optional[str], config: Optional[str], sprint: Optional[str], verbose: bool):
    """Detect documentation drift by comparing artifact dates with issue closes."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    config_loader = None
    if config:
        config_loader = ConfigLoader(Path(config))
    else:
        try:
            config_loader = ConfigLoader()
            max_age_days = config_loader.get('drift_check.max_age_days', max_age_days)
        except FileNotFoundError:
            pass

    # Get GitHub token
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        console.print("[red]Error: GITHUB_TOKEN environment variable required[/red]")
        sys.exit(1)

    # Scan artifacts
    console.print(f"[bold]Scanning {sdd_root} for SDD artifacts...[/bold]")
    scanner = ArtifactScanner(config_loader)
    artifacts = scanner.scan_directory(Path(sdd_root))
    console.print(f"Found {len(artifacts)} artifacts")

    # Query GitHub issues
    console.print(f"[bold]Querying GitHub issues from {repo}...[/bold]")
    issue_query = GitHubIssueQuery(repo, token)
    since = datetime.now() - timedelta(days=max_age_days * 2)
    issues = issue_query.get_closed_issues(sprint=sprint, since=since)
    console.print(f"Found {len(issues)} closed issues")

    # Analyze drift
    analyzer = DriftAnalyzer(max_age_days=max_age_days)
    drifts = []
    for artifact in artifacts:
        drift_status = analyzer.compare_timestamps(artifact, issues)
        drifts.append(drift_status)

    # Display results
    display_drift_table(drifts)

    # Generate report
    if report:
        report_content = analyzer.generate_report(drifts)
        report_path = Path(report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w') as f:
            f.write(report_content)
        console.print(f"\n[green]Report written to {report}[/green]")

    # Exit with error if stale artifacts found
    stale_count = sum(1 for d in drifts if d.status == "stale")
    if stale_count > 0:
        console.print(f"\n[red]Found {stale_count} stale artifacts[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
