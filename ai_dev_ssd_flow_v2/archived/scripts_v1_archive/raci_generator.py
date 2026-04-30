#!/usr/bin/env python3
"""
raci_generator.py - Generate RACI matrix from configuration

Traceability: @brd: BRD-01:FR-08
SPEC Reference: SPEC-09

This script generates RACI (Responsible, Accountable, Consulted, Informed)
matrices from PROJECT_MODEL configuration.
"""

import csv
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, List, Any

import click
import yaml
from rich.console import Console
from rich.table import Table

# Configure console
console = Console()


@dataclass
class Role:
    """Represents a RACI role."""
    name: str
    description: str = ""


@dataclass
class Activity:
    """Represents a RACI activity."""
    name: str
    category: str = ""
    layer: int = 0


@dataclass
class RACIMatrix:
    """Complete RACI matrix."""
    roles: List[Role]
    activities: List[Activity]
    assignments: Dict[str, Dict[str, str]]  # activity -> role -> RACI value
    project_name: str = ""


class RACIParser:
    """Parse RACI configuration from YAML."""

    # Default RACI matrix based on PROJECT_MODEL.md Section 5.1
    DEFAULT_ROLES = [
        Role("Project Lead", "Overall project accountability"),
        Role("Product Manager", "Product requirements and priorities"),
        Role("Architect", "Technical design and architecture"),
        Role("Developer", "Implementation and coding"),
        Role("QA Lead", "Quality assurance and testing"),
        Role("DevOps", "Infrastructure and CI/CD"),
    ]

    DEFAULT_ACTIVITIES = [
        # Tier 1
        Activity("BRD creation", "Tier 1", 1),
        Activity("PRD creation", "Tier 1", 2),
        Activity("EARS creation", "Tier 1", 3),
        Activity("BDD creation", "Tier 1", 4),
        # Tier 2
        Activity("ADR creation", "Tier 2", 5),
        Activity("SYS creation", "Tier 2", 6),
        Activity("REQ creation", "Tier 2", 7),
        Activity("CTR creation", "Tier 2", 8),
        # Tier 3
        Activity("SPEC creation", "Tier 3", 9),
        Activity("TSPEC creation", "Tier 3", 10),
        Activity("TASKS creation", "Tier 3", 11),
        # Cross-cutting
        Activity("GitHub Issue sync", "Cross-cutting", 0),
        Activity("Validator CI setup", "Cross-cutting", 0),
        Activity("CHG management", "Cross-cutting", 0),
    ]

    DEFAULT_ASSIGNMENTS = {
        "BRD creation": {"Project Lead": "A", "Product Manager": "R", "Architect": "C", "Developer": "I", "QA Lead": "I", "DevOps": "I"},
        "PRD creation": {"Project Lead": "A", "Product Manager": "R", "Architect": "C", "Developer": "I", "QA Lead": "C", "DevOps": "I"},
        "EARS creation": {"Project Lead": "A", "Product Manager": "C", "Architect": "R", "Developer": "I", "QA Lead": "C", "DevOps": "I"},
        "BDD creation": {"Project Lead": "A", "Product Manager": "C", "Architect": "C", "Developer": "I", "QA Lead": "R", "DevOps": "I"},
        "ADR creation": {"Project Lead": "A", "Product Manager": "I", "Architect": "R", "Developer": "C", "QA Lead": "I", "DevOps": "C"},
        "SYS creation": {"Project Lead": "A", "Product Manager": "I", "Architect": "R", "Developer": "C", "QA Lead": "C", "DevOps": "I"},
        "REQ creation": {"Project Lead": "A", "Product Manager": "I", "Architect": "R", "Developer": "C", "QA Lead": "C", "DevOps": "I"},
        "CTR creation": {"Project Lead": "A", "Product Manager": "I", "Architect": "R", "Developer": "C", "QA Lead": "I", "DevOps": "C"},
        "SPEC creation": {"Project Lead": "A", "Product Manager": "I", "Architect": "C", "Developer": "R", "QA Lead": "I", "DevOps": "I"},
        "TSPEC creation": {"Project Lead": "A", "Product Manager": "I", "Architect": "I", "Developer": "C", "QA Lead": "R", "DevOps": "I"},
        "TASKS creation": {"Project Lead": "A", "Product Manager": "I", "Architect": "C", "Developer": "R", "QA Lead": "C", "DevOps": "I"},
        "GitHub Issue sync": {"Project Lead": "A", "Product Manager": "I", "Architect": "I", "Developer": "R", "QA Lead": "I", "DevOps": "C"},
        "Validator CI setup": {"Project Lead": "A", "Product Manager": "I", "Architect": "I", "Developer": "C", "QA Lead": "I", "DevOps": "R"},
        "CHG management": {"Project Lead": "R", "Product Manager": "C", "Architect": "A", "Developer": "C", "QA Lead": "C", "DevOps": "I"},
    }

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path
        self.config = self._load_config() if config_path and config_path.exists() else {}

    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def load_roles(self, config: Optional[Dict] = None) -> List[Role]:
        """Load roles from configuration or use defaults."""
        cfg = config or self.config
        role_names = cfg.get('raci_roles', [])

        if role_names:
            return [Role(name) for name in role_names]
        return self.DEFAULT_ROLES.copy()

    def load_activities(self, config: Optional[Dict] = None) -> List[Activity]:
        """Load activities from configuration or use defaults."""
        cfg = config or self.config
        activities = cfg.get('raci_activities', [])

        if activities:
            return [Activity(a.get('name', ''), a.get('category', ''), a.get('layer', 0)) for a in activities]
        return self.DEFAULT_ACTIVITIES.copy()

    def load_assignments(self, config: Optional[Dict] = None) -> Dict[str, Dict[str, str]]:
        """Load RACI assignments from configuration or use defaults."""
        cfg = config or self.config
        assignments = cfg.get('raci_assignments', {})

        if assignments:
            return assignments
        return self.DEFAULT_ASSIGNMENTS.copy()


class RACIMatrixGenerator:
    """Generate RACI matrix in various formats."""

    def __init__(self, parser: RACIParser):
        self.parser = parser

    def generate_matrix(self, roles: List[Role], activities: List[Activity],
                        assignments: Dict[str, Dict[str, str]]) -> RACIMatrix:
        """Generate RACI matrix from components."""
        return RACIMatrix(
            roles=roles,
            activities=activities,
            assignments=assignments,
            project_name=self.parser.config.get('project', {}).get('name', 'Project'),
        )

    def export_markdown(self, matrix: RACIMatrix) -> str:
        """Export RACI matrix as markdown."""
        lines = [
            "# RACI Matrix",
            "",
            f"**Project**: {matrix.project_name}",
            f"**Generated**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}",
            "",
            "## Legend",
            "",
            "- **R** = Responsible (does the work)",
            "- **A** = Accountable (final decision maker, only one per row)",
            "- **C** = Consulted (provides input)",
            "- **I** = Informed (kept up to date)",
            "",
            "## Activity Matrix",
            "",
        ]

        # Build header
        role_names = [r.name for r in matrix.roles]
        header = "| Activity | " + " | ".join(role_names) + " |"
        separator = "|----------|" + "|".join([":---:" for _ in role_names]) + "|"
        lines.extend([header, separator])

        # Build rows
        for activity in matrix.activities:
            row_values = []
            for role in matrix.roles:
                value = matrix.assignments.get(activity.name, {}).get(role.name, "-")
                row_values.append(value)
            row = f"| {activity.name} | " + " | ".join(row_values) + " |"
            lines.append(row)

        lines.extend([
            "",
            "## Validation Rules",
            "",
            "1. Each row has exactly one **A** (Accountable)",
            "2. Each row has at least one **R** (Responsible)",
            "3. No row is empty",
            "",
        ])

        return "\n".join(lines)

    def export_csv(self, matrix: RACIMatrix) -> str:
        """Export RACI matrix as CSV."""
        import io
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        role_names = [r.name for r in matrix.roles]
        writer.writerow(["Activity"] + role_names)

        # Rows
        for activity in matrix.activities:
            row = [activity.name]
            for role in matrix.roles:
                value = matrix.assignments.get(activity.name, {}).get(role.name, "")
                row.append(value)
            writer.writerow(row)

        return output.getvalue()


class RACIValidator:
    """Validate RACI matrix for correctness."""

    def validate_single_accountable(self, matrix: RACIMatrix) -> List[str]:
        """Ensure each activity has exactly one Accountable."""
        errors = []

        for activity in matrix.activities:
            assignments = matrix.assignments.get(activity.name, {})
            accountable_count = sum(1 for v in assignments.values() if v == "A")

            if accountable_count == 0:
                errors.append(f"'{activity.name}' has no Accountable (A)")
            elif accountable_count > 1:
                errors.append(f"'{activity.name}' has multiple Accountable (A): should be exactly one")

        return errors

    def validate_has_responsible(self, matrix: RACIMatrix) -> List[str]:
        """Ensure each activity has at least one Responsible."""
        errors = []

        for activity in matrix.activities:
            assignments = matrix.assignments.get(activity.name, {})
            responsible_count = sum(1 for v in assignments.values() if v == "R")

            if responsible_count == 0:
                errors.append(f"'{activity.name}' has no Responsible (R)")

        return errors

    def validate_no_gaps(self, matrix: RACIMatrix) -> List[str]:
        """Ensure no activity row is completely empty."""
        warnings = []

        for activity in matrix.activities:
            assignments = matrix.assignments.get(activity.name, {})
            if not assignments or all(v in ("", "-") for v in assignments.values()):
                warnings.append(f"'{activity.name}' has no RACI assignments")

        return warnings

    def generate_warnings(self, matrix: RACIMatrix) -> List[str]:
        """Generate all validation warnings."""
        warnings = []
        warnings.extend(self.validate_single_accountable(matrix))
        warnings.extend(self.validate_has_responsible(matrix))
        warnings.extend(self.validate_no_gaps(matrix))
        return warnings


def display_matrix(matrix: RACIMatrix):
    """Display RACI matrix as rich table."""
    table = Table(title=f"RACI Matrix - {matrix.project_name}")

    table.add_column("Activity", style="cyan")
    for role in matrix.roles:
        table.add_column(role.name, style="white", justify="center")

    for activity in matrix.activities:
        row = [activity.name]
        for role in matrix.roles:
            value = matrix.assignments.get(activity.name, {}).get(role.name, "-")
            row.append(value)
        table.add_row(*row)

    console.print(table)


@click.command()
@click.option('--config', '-c', type=click.Path(exists=True), default=None,
              help='Path to project_model.yaml')
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output file path')
@click.option('--format', '-f', 'output_format', type=click.Choice(['markdown', 'csv']),
              default='markdown', help='Output format')
@click.option('--validate', is_flag=True, help='Validate RACI matrix')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(config: Optional[str], output: str, output_format: str,
         validate: bool, verbose: bool):
    """Generate RACI matrix from configuration."""
    # Load parser
    config_path = Path(config) if config else None
    if not config_path:
        # Try to find config
        candidates = [
            Path("ucx_flow_v3/PROJECT/config/project_model.yaml"),
            Path("PROJECT/config/project_model.yaml"),
        ]
        for path in candidates:
            if path.exists():
                config_path = path
                break

    parser = RACIParser(config_path)

    # Load components
    roles = parser.load_roles()
    activities = parser.load_activities()
    assignments = parser.load_assignments()

    # Generate matrix
    generator = RACIMatrixGenerator(parser)
    matrix = generator.generate_matrix(roles, activities, assignments)

    # Display matrix
    console.print("[bold]RACI Matrix Generation[/bold]\n")
    display_matrix(matrix)

    # Validate if requested
    if validate:
        console.print("\n[bold]Validation Results[/bold]\n")
        validator = RACIValidator()
        warnings = validator.generate_warnings(matrix)

        if warnings:
            for warning in warnings:
                console.print(f"[yellow]Warning: {warning}[/yellow]")
        else:
            console.print("[green]Matrix validation passed[/green]")

    # Export
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_format == 'markdown':
        content = generator.export_markdown(matrix)
    else:
        content = generator.export_csv(matrix)

    with open(output_path, 'w') as f:
        f.write(content)

    console.print(f"\n[green]Matrix written to {output}[/green]")


if __name__ == "__main__":
    main()
