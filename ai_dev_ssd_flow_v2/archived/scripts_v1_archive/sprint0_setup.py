#!/usr/bin/env python3
"""
sprint0_setup.py - Sprint 0 setup and checklist automation

Traceability: @brd: BRD-01:FR-07
SPEC Reference: SPEC-08

This script generates Sprint 0 checklist, creates tracking issues,
and validates Tier 1 artifact readiness for Sprint 1.
"""

import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

import click
import yaml
from github import Github, GithubException
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

# Configure console
console = Console()


@dataclass
class ChecklistItem:
    """Represents a Sprint 0 checklist item."""
    id: str
    task: str
    output: str
    blocks: List[str]
    completed: bool = False
    github_issue: Optional[int] = None


@dataclass
class ReadinessScore:
    """Readiness score for an artifact type."""
    artifact_type: str
    score: int
    max_score: int = 100
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class Checklist:
    """Complete Sprint 0 checklist."""
    items: List[ChecklistItem]
    project_name: str = ""
    target_date: str = ""


class ConfigLoader:
    """Load Sprint 0 configuration."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self._find_config()
        self.config = self._load_config() if self.config_path and self.config_path.exists() else {}

    def _find_config(self) -> Optional[Path]:
        candidates = [
            Path("ucx_flow_v3/PROJECT/config/project_model.yaml"),
            Path("PROJECT/config/project_model.yaml"),
            Path("config/project_model.yaml"),
        ]
        for path in candidates:
            if path.exists():
                return path
        return None

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

    def get_sprint0_checklist(self) -> List[Dict[str, Any]]:
        """Get Sprint 0 checklist from config."""
        return self.config.get('sprint_0_checklist', self._default_checklist())

    def _default_checklist(self) -> List[Dict[str, Any]]:
        """Default Sprint 0 checklist."""
        return [
            {"id": "0.1", "task": "Identify blocking technical questions", "output": "Question list", "blocks": ["all"]},
            {"id": "0.2", "task": "Research each question", "output": "Research notes", "blocks": ["0.3"]},
            {"id": "0.3", "task": "Document decisions as ADRs", "output": "ADR-01 through ADR-NN", "blocks": ["sprint_1"]},
            {"id": "0.4", "task": "Validate BRD completeness", "output": "BRD validation report", "blocks": ["0.5"]},
            {"id": "0.5", "task": "Generate PRD from BRD", "output": "PRD-01 through PRD-NN", "blocks": ["0.6"]},
            {"id": "0.6", "task": "Generate EARS from PRD", "output": "EARS-01 through EARS-NN", "blocks": ["0.7"]},
            {"id": "0.7", "task": "Generate BDD from EARS", "output": "BDD-01 through BDD-NN", "blocks": ["sprint_1"]},
            {"id": "0.8", "task": "Set up GitHub Project board", "output": "Configured board", "blocks": ["sprint_1"]},
        ]


class Sprint0Checklist:
    """Generate and manage Sprint 0 checklist."""

    def __init__(self, config: Optional[ConfigLoader] = None):
        self.config = config or ConfigLoader()

    def generate_checklist(self, project_config: Dict[str, Any] = None) -> Checklist:
        """Generate Sprint 0 checklist from configuration."""
        checklist_data = self.config.get_sprint0_checklist()
        items = []

        for item in checklist_data:
            items.append(ChecklistItem(
                id=item.get('id', ''),
                task=item.get('task', ''),
                output=item.get('output', ''),
                blocks=item.get('blocks', []),
            ))

        project_name = (project_config or {}).get('name', self.config.get('project.name', 'Project'))

        return Checklist(
            items=items,
            project_name=project_name,
            target_date=datetime.now().strftime('%Y-%m-%d'),
        )

    def check_tier1_artifacts(self, docs_root: Path) -> Dict[str, bool]:
        """Check existence of Tier 1 artifacts."""
        tier1_types = ['BRD', 'PRD', 'EARS', 'BDD']
        results = {}

        for artifact_type in tier1_types:
            # Check for artifact directory or files
            found = False
            for pattern in [f'*{artifact_type}*', f'*{artifact_type.lower()}*']:
                if list(docs_root.rglob(pattern)):
                    found = True
                    break
            results[artifact_type] = found

        return results

    def check_adr_decisions(self, docs_root: Path) -> Dict[str, bool]:
        """Check existence of ADR documents."""
        adr_files = list(docs_root.rglob('*ADR*.md'))
        return {
            'ADR_exists': len(adr_files) > 0,
            'ADR_count': len(adr_files),
        }

    def validate_sprint1_readiness(self, docs_root: Path) -> bool:
        """Validate readiness for Sprint 1."""
        tier1 = self.check_tier1_artifacts(docs_root)
        adr = self.check_adr_decisions(docs_root)

        # All Tier 1 artifacts must exist
        tier1_complete = all(tier1.values())

        # At least one ADR should exist
        adr_complete = adr.get('ADR_exists', False)

        return tier1_complete and adr_complete


class ArtifactReadinessChecker:
    """Check readiness of individual artifact types."""

    def __init__(self, docs_root: Path):
        self.docs_root = docs_root

    def _count_files(self, pattern: str) -> int:
        """Count files matching pattern."""
        return len(list(self.docs_root.rglob(pattern)))

    def _check_file_content(self, pattern: str, required_sections: List[str]) -> tuple:
        """Check if files contain required sections."""
        files = list(self.docs_root.rglob(pattern))
        score = 0
        issues = []

        for file in files:
            try:
                content = file.read_text()
                section_count = sum(1 for section in required_sections if section.lower() in content.lower())
                score += int(section_count / len(required_sections) * 100) if required_sections else 100
            except Exception as e:
                issues.append(f"Error reading {file.name}: {e}")

        avg_score = score // len(files) if files else 0
        return avg_score, issues

    def check_brd_readiness(self) -> ReadinessScore:
        """Check BRD artifact readiness."""
        required_sections = ['business context', 'business objectives', 'functional requirements', 'success metrics']
        score, issues = self._check_file_content('*BRD*.md', required_sections)

        recommendations = []
        if score < 90:
            recommendations.append("Ensure all BRD sections are complete")
            recommendations.append("Add measurable success metrics")

        return ReadinessScore(
            artifact_type='BRD',
            score=score,
            issues=issues,
            recommendations=recommendations,
        )

    def check_prd_readiness(self) -> ReadinessScore:
        """Check PRD artifact readiness."""
        required_sections = ['product overview', 'product requirements', 'user stories']
        score, issues = self._check_file_content('*PRD*.md', required_sections)

        recommendations = []
        if score < 90:
            recommendations.append("Ensure PRD has clear user stories")
            recommendations.append("Add traceability to BRD requirements")

        return ReadinessScore(
            artifact_type='PRD',
            score=score,
            issues=issues,
            recommendations=recommendations,
        )

    def check_ears_readiness(self) -> ReadinessScore:
        """Check EARS artifact readiness."""
        required_sections = ['shall', 'when', 'if', 'where']
        score, issues = self._check_file_content('*EARS*.md', required_sections)

        recommendations = []
        if score < 90:
            recommendations.append("Ensure EARS requirements follow EARS syntax")
            recommendations.append("Add traceability to PRD")

        return ReadinessScore(
            artifact_type='EARS',
            score=score,
            issues=issues,
            recommendations=recommendations,
        )

    def check_bdd_readiness(self) -> ReadinessScore:
        """Check BDD artifact readiness."""
        required_sections = ['feature', 'scenario', 'given', 'when', 'then']
        score, issues = self._check_file_content('*.feature', required_sections)

        # Also check .md BDD files
        md_score, md_issues = self._check_file_content('*BDD*.md', required_sections)
        score = max(score, md_score)
        issues.extend(md_issues)

        recommendations = []
        if score < 90:
            recommendations.append("Ensure BDD scenarios cover all EARS requirements")
            recommendations.append("Add concrete examples to scenarios")

        return ReadinessScore(
            artifact_type='BDD',
            score=score,
            issues=issues,
            recommendations=recommendations,
        )

    def check_adr_completeness(self) -> ReadinessScore:
        """Check ADR completeness."""
        required_sections = ['context', 'decision', 'consequences']
        score, issues = self._check_file_content('*ADR*.md', required_sections)

        recommendations = []
        if score < 90:
            recommendations.append("Ensure ADRs document rationale clearly")
            recommendations.append("Add consequences (positive and negative)")

        return ReadinessScore(
            artifact_type='ADR',
            score=score,
            issues=issues,
            recommendations=recommendations,
        )


class ChecklistIssueCreator:
    """Create GitHub issues for Sprint 0 checklist."""

    def __init__(self, repo: str, token: str):
        self.gh = Github(token)
        self.repo = self.gh.get_repo(repo)

    def create_sprint0_epic(self, checklist: Checklist) -> Any:
        """Create Sprint 0 epic issue."""
        title = f"[Sprint 0] {checklist.project_name} - Setup and Preparation"

        body = f"""## Sprint 0 Epic

**Project**: {checklist.project_name}
**Target Completion**: {checklist.target_date}

### Checklist

"""
        for item in checklist.items:
            status = "[x]" if item.completed else "[ ]"
            body += f"- {status} **{item.id}** {item.task}\n"
            body += f"  - Output: {item.output}\n"
            if item.blocks:
                body += f"  - Blocks: {', '.join(item.blocks)}\n"

        body += """
### Completion Criteria

- [ ] All Tier 1 artifacts (BRD→BDD) complete
- [ ] All ADRs documented
- [ ] GATE-01 validation passing
- [ ] GitHub board configured
- [ ] Team sign-off obtained

---
Labels: `sprint-0`, `epic`, `source:sdd`
"""

        try:
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=['sprint-0', 'epic', 'source:sdd'],
            )
            console.print(f"[green]Created Sprint 0 epic: #{issue.number}[/green]")
            return issue
        except GithubException as e:
            console.print(f"[red]Error creating epic: {e}[/red]")
            return None

    def create_task_issues(self, checklist: Checklist, epic_issue: Any = None) -> List[Any]:
        """Create individual task issues for checklist items."""
        issues = []

        for item in checklist.items:
            title = f"[Sprint 0-{item.id}] {item.task}"

            body = f"""## Task: {item.task}

**ID**: {item.id}
**Expected Output**: {item.output}

### Acceptance Criteria

- [ ] Task completed successfully
- [ ] Output artifact created/validated
- [ ] Blocking dependencies resolved

### Blocks

{', '.join(item.blocks) if item.blocks else 'None'}

"""
            if epic_issue:
                body += f"\n**Parent Epic**: #{epic_issue.number}"

            try:
                issue = self.repo.create_issue(
                    title=title,
                    body=body,
                    labels=['sprint-0', 'source:sdd'],
                )
                item.github_issue = issue.number
                issues.append(issue)
                console.print(f"  Created: #{issue.number} - {item.task[:40]}")
            except GithubException as e:
                console.print(f"  [red]Error creating issue for {item.id}: {e}[/red]")

        return issues

    def link_blocking_dependencies(self, checklist: Checklist) -> None:
        """Add blocking issue links (requires issues to exist)."""
        # This would add "Blocked by #N" comments to issues
        # based on the blocks field in checklist items
        pass


def display_checklist(checklist: Checklist):
    """Display checklist as rich table."""
    table = Table(title=f"Sprint 0 Checklist - {checklist.project_name}")
    table.add_column("ID", style="cyan")
    table.add_column("Task", style="white")
    table.add_column("Output", style="yellow")
    table.add_column("Blocks", style="magenta")
    table.add_column("Status", style="bold")

    for item in checklist.items:
        status = "[green]Done[/green]" if item.completed else "[dim]Pending[/dim]"
        blocks = ', '.join(item.blocks) if item.blocks else '-'
        table.add_row(item.id, item.task, item.output, blocks, status)

    console.print(table)


def display_readiness(scores: List[ReadinessScore]):
    """Display readiness scores as rich table."""
    table = Table(title="Artifact Readiness Scores")
    table.add_column("Artifact", style="cyan")
    table.add_column("Score", style="white")
    table.add_column("Status", style="bold")

    for score in scores:
        status_style = "[green]Ready[/green]" if score.score >= 90 else (
            "[yellow]Needs Work[/yellow]" if score.score >= 70 else "[red]Not Ready[/red]"
        )
        table.add_row(score.artifact_type, f"{score.score}/100", status_style)

    console.print(table)


@click.command()
@click.option('--repo', '-r', default=None, help='GitHub repository (owner/repo)')
@click.option('--project-number', '-p', type=int, default=None,
              help='GitHub Project V2 board number')
@click.option('--config', '-c', type=click.Path(exists=True), default=None,
              help='Path to project_model.yaml')
@click.option('--docs-root', '-d', type=click.Path(exists=True), default='docs',
              help='Root directory of documentation')
@click.option('--create-issues', is_flag=True, help='Create GitHub issues for checklist')
@click.option('--check-readiness', is_flag=True, help='Check artifact readiness')
@click.option('--output', '-o', type=click.Path(), default=None,
              help='Output path for checklist markdown')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(repo: Optional[str], project_number: Optional[int], config: Optional[str],
         docs_root: str, create_issues: bool, check_readiness: bool,
         output: Optional[str], verbose: bool):
    """Sprint 0 setup and readiness validation."""
    # Load configuration
    config_loader = None
    if config:
        config_loader = ConfigLoader(Path(config))
    else:
        try:
            config_loader = ConfigLoader()
        except Exception:
            pass

    # Generate checklist
    sprint0 = Sprint0Checklist(config_loader)
    project_config = {'name': config_loader.get('project.name', 'Project') if config_loader else 'Project'}
    checklist = sprint0.generate_checklist(project_config)

    console.print("[bold]Sprint 0 Setup[/bold]\n")

    # Display checklist
    display_checklist(checklist)

    # Check readiness if requested
    if check_readiness:
        console.print("\n[bold]Checking Artifact Readiness...[/bold]\n")
        docs_path = Path(docs_root)
        checker = ArtifactReadinessChecker(docs_path)

        scores = [
            checker.check_brd_readiness(),
            checker.check_prd_readiness(),
            checker.check_ears_readiness(),
            checker.check_bdd_readiness(),
            checker.check_adr_completeness(),
        ]

        display_readiness(scores)

        # Check overall readiness
        is_ready = sprint0.validate_sprint1_readiness(docs_path)
        if is_ready:
            console.print("\n[green]Sprint 1 Readiness: PASSED[/green]")
        else:
            console.print("\n[yellow]Sprint 1 Readiness: NOT READY[/yellow]")
            console.print("Complete Tier 1 artifacts before starting Sprint 1")

    # Create GitHub issues if requested
    if create_issues:
        if not repo:
            console.print("[red]Error: --repo required for --create-issues[/red]")
            sys.exit(1)

        token = os.environ.get('GITHUB_TOKEN')
        if not token:
            console.print("[red]Error: GITHUB_TOKEN environment variable required[/red]")
            sys.exit(1)

        console.print("\n[bold]Creating GitHub Issues...[/bold]\n")
        creator = ChecklistIssueCreator(repo, token)

        epic = creator.create_sprint0_epic(checklist)
        if epic:
            creator.create_task_issues(checklist, epic)

    # Write output
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(f"# Sprint 0 Checklist - {checklist.project_name}\n\n")
            f.write(f"**Target Completion**: {checklist.target_date}\n\n")

            for item in checklist.items:
                status = "[x]" if item.completed else "[ ]"
                f.write(f"- {status} **{item.id}** {item.task}\n")
                f.write(f"  - Output: {item.output}\n")
                if item.blocks:
                    f.write(f"  - Blocks: {', '.join(item.blocks)}\n")

        console.print(f"\n[green]Checklist written to {output}[/green]")


if __name__ == "__main__":
    main()
