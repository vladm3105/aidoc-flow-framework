#!/usr/bin/env python3
"""
tasks_to_github.py - Convert TASKS YAML to GitHub Issues

Traceability: @brd: BRD-01:FR-01, FR-10
SPEC Reference: SPEC-01

This script parses TASKS YAML files and creates/updates GitHub Issues
with full traceability tags and Project V2 board integration.
"""

import os
import sys
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, List, Any

import click
import yaml
import requests
from github import Github, GithubException
from rich.console import Console
from rich.table import Table

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
console = Console()


@dataclass
class TaskElement:
    """Represents a single task from TASKS YAML."""
    id: str
    title: str
    description: str = ""
    traceability: Dict[str, str] = field(default_factory=dict)
    acceptance_criteria: List[str] = field(default_factory=list)
    size: str = "M"
    priority: str = "P1"
    dependencies: List[str] = field(default_factory=list)
    implementation_notes: str = ""
    phase: str = "P1"
    sprint: str = ""


@dataclass
class TasksMetadata:
    """Metadata from TASKS YAML header."""
    id: str
    title: str
    version: str
    spec_reference: str
    sprint: str
    phase: str
    traceability: Dict[str, str] = field(default_factory=dict)


class ConfigLoader:
    """Load configuration from project_model.yaml."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self._find_config()
        self.config = self._load_config()

    def _find_config(self) -> Path:
        """Find project_model.yaml in standard locations."""
        candidates = [
            Path("ai_dev_ssd_flow/PROJECT/config/project_model.yaml"),
            Path("PROJECT/config/project_model.yaml"),
            Path("config/project_model.yaml"),
        ]
        for path in candidates:
            if path.exists():
                return path
        raise FileNotFoundError("Cannot find project_model.yaml configuration")

    def _load_config(self) -> Dict[str, Any]:
        """Load and return configuration."""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value


class TasksParser:
    """Parse TASKS YAML files into structured data."""

    def __init__(self, config: Optional[ConfigLoader] = None):
        self.config = config

    def load_yaml(self, filepath: Path) -> Dict[str, Any]:
        """Load YAML file and return parsed data."""
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)

    def extract_tasks(self, yaml_data: Dict[str, Any]) -> List[TaskElement]:
        """Extract task elements from parsed YAML."""
        tasks = []
        metadata = yaml_data.get('metadata', {})
        default_phase = metadata.get('phase', 'P1')
        default_sprint = metadata.get('sprint', '')

        for task_data in yaml_data.get('tasks', []):
            task = TaskElement(
                id=task_data.get('id', ''),
                title=task_data.get('title', ''),
                description=task_data.get('description', ''),
                traceability=task_data.get('traceability', {}),
                acceptance_criteria=task_data.get('acceptance_criteria', []),
                size=task_data.get('size', 'M'),
                priority=task_data.get('priority', 'P1'),
                dependencies=task_data.get('dependencies', []),
                implementation_notes=task_data.get('implementation_notes', ''),
                phase=task_data.get('phase', default_phase),
                sprint=task_data.get('sprint', default_sprint),
            )
            tasks.append(task)
        return tasks

    def extract_metadata(self, yaml_data: Dict[str, Any]) -> TasksMetadata:
        """Extract metadata from TASKS YAML header."""
        md = yaml_data.get('metadata', {})
        return TasksMetadata(
            id=md.get('id', ''),
            title=md.get('title', ''),
            version=md.get('version', '1.0'),
            spec_reference=md.get('spec_reference', ''),
            sprint=md.get('sprint', ''),
            phase=md.get('phase', 'P1'),
            traceability=md.get('traceability', {}),
        )

    def validate_traceability(self, task: TaskElement) -> bool:
        """Validate that task has required traceability tags."""
        required = ['brd', 'spec']
        for tag in required:
            if tag not in task.traceability or not task.traceability[tag]:
                logger.warning(f"Task {task.id} missing @{tag} traceability")
                return False
        return True


class IssueFormatter:
    """Format task data for GitHub issue creation."""

    def __init__(self, config: Optional[ConfigLoader] = None):
        self.config = config

    def format_title(self, task: TaskElement, phase: str = "") -> str:
        """Format issue title."""
        p = phase or task.phase
        return f"[{p}-{task.id}] {task.title}"

    def format_body(self, task: TaskElement, metadata: Optional[TasksMetadata] = None) -> str:
        """Format issue body with traceability and acceptance criteria."""
        sections = []

        # Traceability section
        trace_lines = ["## Traceability", ""]
        for tag, ref in task.traceability.items():
            trace_lines.append(f"- **@{tag}**: `{ref}`")
        if metadata and metadata.spec_reference:
            trace_lines.append(f"- **@spec**: `{metadata.spec_reference}`")
        trace_lines.append(f"- **@tasks**: `{task.id}`")
        sections.append("\n".join(trace_lines))

        # Description
        if task.description:
            sections.append(f"## Description\n\n{task.description}")

        # Acceptance Criteria
        if task.acceptance_criteria:
            criteria = ["## Acceptance Criteria", ""]
            for ac in task.acceptance_criteria:
                criteria.append(f"- [ ] {ac}")
            sections.append("\n".join(criteria))

        # Implementation Notes
        if task.implementation_notes:
            sections.append(f"## Implementation Notes\n\n{task.implementation_notes}")

        # Dependencies
        if task.dependencies:
            deps = ["## Dependencies", ""]
            for dep in task.dependencies:
                deps.append(f"- {dep}")
            sections.append("\n".join(deps))

        # Metadata footer
        footer = [
            "---",
            f"**Size**: {task.size} | **Priority**: {task.priority} | **Sprint**: {task.sprint}",
        ]
        sections.append("\n".join(footer))

        return "\n\n".join(sections)

    def format_labels(self, task: TaskElement) -> List[str]:
        """Generate labels for the issue."""
        labels = ["ai:ready", "source:sdd"]

        if task.size:
            labels.append(f"size:{task.size}")
        if task.priority:
            labels.append(f"priority:{task.priority}")
        if task.phase:
            labels.append(f"phase:{task.phase}")

        return labels


class GitHubIssueCreator:
    """Create and manage GitHub issues from tasks."""

    def __init__(self, repo: str, token: str):
        self.gh = Github(token)
        self.repo = self.gh.get_repo(repo)
        self.formatter = IssueFormatter()

    def find_existing_issue(self, tasks_id: str) -> Optional[Any]:
        """Find existing issue by TASKS ID in title."""
        query = f"repo:{self.repo.full_name} is:issue {tasks_id} in:title"
        try:
            results = self.gh.search_issues(query)
            for issue in results:
                if tasks_id in issue.title:
                    return issue
        except GithubException as e:
            logger.error(f"Error searching issues: {e}")
        return None

    def create_issue(self, task: TaskElement, metadata: Optional[TasksMetadata] = None) -> Any:
        """Create a new GitHub issue from task."""
        title = self.formatter.format_title(task)
        body = self.formatter.format_body(task, metadata)
        labels = self.formatter.format_labels(task)

        try:
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=labels,
            )
            logger.info(f"Created issue #{issue.number}: {title}")
            return issue
        except GithubException as e:
            logger.error(f"Error creating issue for {task.id}: {e}")
            raise

    def update_issue(self, issue: Any, task: TaskElement, metadata: Optional[TasksMetadata] = None) -> Any:
        """Update existing issue with new task data."""
        title = self.formatter.format_title(task)
        body = self.formatter.format_body(task, metadata)

        try:
            issue.edit(title=title, body=body)
            logger.info(f"Updated issue #{issue.number}: {title}")
            return issue
        except GithubException as e:
            logger.error(f"Error updating issue #{issue.number}: {e}")
            raise


class ProjectV2Sync:
    """Sync issues to GitHub Project V2 board using GraphQL."""

    GRAPHQL_ENDPOINT = "https://api.github.com/graphql"

    def __init__(self, repo: str, project_number: int, token: str):
        self.repo = repo
        self.project_number = project_number
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.project_id = None
        self.field_ids: Dict[str, str] = {}

    def _graphql_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute GraphQL query."""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = requests.post(
            self.GRAPHQL_ENDPOINT,
            headers=self.headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            raise Exception(f"GraphQL error: {data['errors']}")

        return data["data"]

    def _get_project_id(self) -> str:
        """Get Project V2 node ID."""
        if self.project_id:
            return self.project_id

        owner, repo_name = self.repo.split("/")
        query = """
        query($owner: String!, $repo: String!, $number: Int!) {
            repository(owner: $owner, name: $repo) {
                projectV2(number: $number) {
                    id
                    fields(first: 20) {
                        nodes {
                            ... on ProjectV2SingleSelectField {
                                id
                                name
                                options {
                                    id
                                    name
                                }
                            }
                            ... on ProjectV2Field {
                                id
                                name
                            }
                        }
                    }
                }
            }
        }
        """
        variables = {"owner": owner, "repo": repo_name, "number": self.project_number}
        data = self._graphql_query(query, variables)

        project = data["repository"]["projectV2"]
        self.project_id = project["id"]

        # Cache field IDs
        for field in project["fields"]["nodes"]:
            self.field_ids[field["name"]] = field["id"]
            if "options" in field:
                for opt in field["options"]:
                    self.field_ids[f"{field['name']}:{opt['name']}"] = opt["id"]

        return self.project_id

    def add_issue_to_project(self, issue) -> str:
        """Add issue to Project V2 board."""
        project_id = self._get_project_id()

        query = """
        mutation($projectId: ID!, $contentId: ID!) {
            addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
                item {
                    id
                }
            }
        }
        """
        variables = {"projectId": project_id, "contentId": issue.node_id}
        data = self._graphql_query(query, variables)

        item_id = data["addProjectV2ItemById"]["item"]["id"]
        logger.info(f"Added issue #{issue.number} to project board")
        return item_id

    def set_custom_fields(self, item_id: str, task: TaskElement) -> None:
        """Set custom fields on project item."""
        project_id = self._get_project_id()

        # Set single-select fields (Size, Priority, Phase)
        field_mappings = [
            ("Size", task.size),
            ("Priority", task.priority),
            ("Phase", task.phase),
        ]

        for field_name, value in field_mappings:
            field_id = self.field_ids.get(field_name)
            option_id = self.field_ids.get(f"{field_name}:{value}")

            if field_id and option_id:
                query = """
                mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
                    updateProjectV2ItemFieldValue(input: {
                        projectId: $projectId,
                        itemId: $itemId,
                        fieldId: $fieldId,
                        value: {singleSelectOptionId: $optionId}
                    }) {
                        projectV2Item {
                            id
                        }
                    }
                }
                """
                variables = {
                    "projectId": project_id,
                    "itemId": item_id,
                    "fieldId": field_id,
                    "optionId": option_id,
                }
                try:
                    self._graphql_query(query, variables)
                except Exception as e:
                    logger.warning(f"Could not set {field_name}={value}: {e}")


def display_summary(tasks: List[TaskElement], created: int, updated: int, skipped: int):
    """Display summary table of processed tasks."""
    table = Table(title="Tasks Processing Summary")
    table.add_column("Task ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Size", style="yellow")
    table.add_column("Priority", style="magenta")

    for task in tasks:
        table.add_row(task.id, task.title[:50], task.size, task.priority)

    console.print(table)
    console.print(f"\n[green]Created: {created}[/green] | [yellow]Updated: {updated}[/yellow] | [dim]Skipped: {skipped}[/dim]")


@click.command()
@click.option('--tasks-file', '-f', required=True, type=click.Path(exists=True),
              help='Path to TASKS YAML file')
@click.option('--repo', '-r', required=True, help='GitHub repository (owner/repo)')
@click.option('--sprint', '-s', default=None, help='Sprint name override')
@click.option('--project-number', '-p', type=int, default=None,
              help='GitHub Project V2 board number')
@click.option('--dry-run', is_flag=True, help='Preview without creating issues')
@click.option('--config', '-c', type=click.Path(exists=True), default=None,
              help='Path to project_model.yaml')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(tasks_file: str, repo: str, sprint: Optional[str], project_number: Optional[int],
         dry_run: bool, config: Optional[str], verbose: bool):
    """Convert TASKS YAML to GitHub Issues with Project V2 integration."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    config_loader = None
    if config:
        config_loader = ConfigLoader(Path(config))

    # Get GitHub token
    token = os.environ.get('GITHUB_TOKEN')
    if not token and not dry_run:
        console.print("[red]Error: GITHUB_TOKEN environment variable required[/red]")
        sys.exit(1)

    # Parse TASKS file
    parser = TasksParser(config_loader)
    yaml_data = parser.load_yaml(Path(tasks_file))
    metadata = parser.extract_metadata(yaml_data)
    tasks = parser.extract_tasks(yaml_data)

    # Override sprint if specified
    if sprint:
        metadata.sprint = sprint
        for task in tasks:
            task.sprint = sprint

    console.print(f"[bold]Processing {len(tasks)} tasks from {metadata.id}[/bold]")

    if dry_run:
        console.print("[yellow]DRY RUN MODE - No issues will be created[/yellow]\n")
        display_summary(tasks, 0, 0, len(tasks))
        return

    # Initialize GitHub clients
    issue_creator = GitHubIssueCreator(repo, token)
    project_sync = None
    if project_number:
        project_sync = ProjectV2Sync(repo, project_number, token)

    # Process tasks
    created, updated, skipped = 0, 0, 0
    for task in tasks:
        if not parser.validate_traceability(task):
            console.print(f"[yellow]Skipping {task.id}: missing traceability[/yellow]")
            skipped += 1
            continue

        try:
            existing = issue_creator.find_existing_issue(task.id)
            if existing:
                issue_creator.update_issue(existing, task, metadata)
                updated += 1
                issue = existing
            else:
                issue = issue_creator.create_issue(task, metadata)
                created += 1

            # Add to project board
            if project_sync:
                item_id = project_sync.add_issue_to_project(issue)
                project_sync.set_custom_fields(item_id, task)

        except Exception as e:
            console.print(f"[red]Error processing {task.id}: {e}[/red]")
            skipped += 1

    display_summary(tasks, created, updated, skipped)


if __name__ == "__main__":
    main()
