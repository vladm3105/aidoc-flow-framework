#!/usr/bin/env python3
"""
layer_selector.py - Decision framework for layer selection

Traceability: @brd: BRD-01:FR-11
SPEC Reference: SPEC-10

This script helps determine which SDD layers and artifacts are needed
based on the type of work being performed.
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, List, Any
from enum import Enum

import click
import yaml
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

# Configure console
console = Console()


class WorkType(Enum):
    """Types of work that determine layer requirements."""
    NEW_FEATURE = "new_feature"
    ENHANCEMENT = "enhancement"
    BUG_FIX = "bug_fix"
    HOTFIX = "hotfix"
    CONFIG_CHANGE = "config_change"
    REFACTORING = "refactoring"


@dataclass
class LayerRecommendation:
    """Recommendation for layers and artifacts."""
    work_type: WorkType
    layers: List[int]
    artifacts: List[str]
    description: str
    effort_level: str  # Low, Medium, High


class ConfigLoader:
    """Load layer selection configuration."""

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

    def get_work_types(self) -> Dict[str, Dict[str, Any]]:
        """Get work type configurations."""
        return self.config.get('work_types', self._default_work_types())

    def _default_work_types(self) -> Dict[str, Dict[str, Any]]:
        """Default work type configurations."""
        return {
            'new_feature': {
                'layers': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                'description': 'Full SDD flow',
            },
            'enhancement': {
                'layers': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                'description': 'PRD→TASKS',
            },
            'bug_fix': {
                'layers': [11],
                'description': 'TASKS only',
            },
            'hotfix': {
                'layers': [],
                'description': 'Code only + 72h retroactive docs',
            },
            'config_change': {
                'layers': [5, 11],
                'description': 'ADR + TASKS',
            },
            'refactoring': {
                'layers': [5, 9, 10, 11],
                'description': 'ADR + SPEC + TSPEC + TASKS',
            },
        }


class WorkItemClassifier:
    """Classify work items by type."""

    # Keywords for automatic classification
    KEYWORDS = {
        WorkType.NEW_FEATURE: ['new feature', 'add feature', 'implement', 'create new', 'introduce'],
        WorkType.ENHANCEMENT: ['enhance', 'improve', 'update', 'extend', 'add support'],
        WorkType.BUG_FIX: ['bug', 'fix', 'issue', 'error', 'crash', 'broken'],
        WorkType.HOTFIX: ['hotfix', 'urgent', 'critical fix', 'production issue'],
        WorkType.CONFIG_CHANGE: ['config', 'configuration', 'setting', 'parameter', 'environment'],
        WorkType.REFACTORING: ['refactor', 'restructure', 'rewrite', 'clean up', 'modernize'],
    }

    def classify_work_type(self, description: str) -> WorkType:
        """Classify work type based on description."""
        desc_lower = description.lower()

        # Check each work type's keywords
        for work_type, keywords in self.KEYWORDS.items():
            if any(kw in desc_lower for kw in keywords):
                return work_type

        # Default to enhancement for unclear cases
        return WorkType.ENHANCEMENT

    def is_new_capability(self, description: str) -> bool:
        """Check if work adds new capability."""
        indicators = ['new', 'add', 'create', 'introduce', 'implement']
        desc_lower = description.lower()
        return any(ind in desc_lower for ind in indicators)

    def is_scope_change(self, description: str) -> bool:
        """Check if work changes existing scope."""
        indicators = ['change', 'modify', 'update', 'extend', 'expand']
        desc_lower = description.lower()
        return any(ind in desc_lower for ind in indicators)

    def is_bug_fix(self, description: str) -> bool:
        """Check if work is a bug fix."""
        return self.classify_work_type(description) == WorkType.BUG_FIX

    def is_hotfix(self, description: str) -> bool:
        """Check if work is a hotfix."""
        return self.classify_work_type(description) == WorkType.HOTFIX


class LayerRecommender:
    """Recommend layers based on work type."""

    # Layer to artifact mapping
    LAYER_ARTIFACTS = {
        1: 'BRD', 2: 'PRD', 3: 'EARS', 4: 'BDD',
        5: 'ADR', 6: 'SYS', 7: 'REQ', 8: 'CTR',
        9: 'SPEC', 10: 'TSPEC', 11: 'TASKS',
        12: 'CODE', 13: 'TESTS', 14: 'RELEASE',
    }

    def __init__(self, config: Optional[ConfigLoader] = None):
        self.config = config or ConfigLoader()

    def recommend_layers(self, work_type: WorkType) -> List[int]:
        """Recommend layers for work type."""
        work_types = self.config.get_work_types()
        type_config = work_types.get(work_type.value, {})
        return type_config.get('layers', [11])

    def recommend_artifacts(self, layers: List[int]) -> List[str]:
        """Get artifact names for layers."""
        return [self.LAYER_ARTIFACTS.get(l, f'L{l}') for l in layers if l in self.LAYER_ARTIFACTS]

    def estimate_effort(self, layers: List[int]) -> str:
        """Estimate effort level based on layers."""
        if not layers:
            return "Minimal"
        if len(layers) >= 8:
            return "High"
        if len(layers) >= 4:
            return "Medium"
        return "Low"

    def get_recommendation(self, work_type: WorkType, description: str = "") -> LayerRecommendation:
        """Get full recommendation for work type."""
        work_types = self.config.get_work_types()
        type_config = work_types.get(work_type.value, {})

        layers = type_config.get('layers', [11])
        artifacts = self.recommend_artifacts(layers)
        effort = self.estimate_effort(layers)

        return LayerRecommendation(
            work_type=work_type,
            layers=layers,
            artifacts=artifacts,
            description=type_config.get('description', ''),
            effort_level=effort,
        )


class DecisionTreeRunner:
    """Run interactive decision tree for layer selection."""

    def __init__(self, config: Optional[ConfigLoader] = None):
        self.classifier = WorkItemClassifier()
        self.recommender = LayerRecommender(config)

    def run_interactive(self) -> LayerRecommendation:
        """Run interactive decision tree."""
        console.print("[bold]SDD Layer Selection Decision Tree[/bold]\n")

        # Question 1: Is this new functionality?
        is_new = Confirm.ask("Is this adding new functionality (not changing existing)?")

        if is_new:
            # Question 2: Is it a complete new feature or enhancement?
            feature_type = Prompt.ask(
                "What type of new functionality?",
                choices=["new_feature", "enhancement"],
                default="new_feature"
            )
            work_type = WorkType.NEW_FEATURE if feature_type == "new_feature" else WorkType.ENHANCEMENT
        else:
            # Question 3: What kind of change?
            change_type = Prompt.ask(
                "What type of change?",
                choices=["bug_fix", "hotfix", "config_change", "refactoring"],
                default="bug_fix"
            )
            work_type = WorkType(change_type)

        return self.recommender.get_recommendation(work_type)

    def run_automated(self, work_type: str, description: str = "") -> LayerRecommendation:
        """Run automated classification."""
        # Try to match work_type string to enum
        try:
            wt = WorkType(work_type.lower().replace(' ', '_').replace('-', '_'))
        except ValueError:
            # Fall back to classification from description
            wt = self.classifier.classify_work_type(description or work_type)

        return self.recommender.get_recommendation(wt, description)


def display_recommendation(rec: LayerRecommendation):
    """Display recommendation as rich table."""
    console.print("\n[bold]Layer Recommendation[/bold]\n")

    table = Table()
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Work Type", rec.work_type.value.replace('_', ' ').title())
    table.add_row("Layers", ', '.join(f'L{l}' for l in rec.layers) if rec.layers else 'None')
    table.add_row("Artifacts", ', '.join(rec.artifacts) if rec.artifacts else 'Code only')
    table.add_row("Description", rec.description)
    table.add_row("Effort Level", rec.effort_level)

    console.print(table)

    # Show artifact flow
    if rec.artifacts:
        console.print("\n[bold]Artifact Flow[/bold]")
        console.print(" → ".join(rec.artifacts))


def display_decision_matrix():
    """Display the full decision matrix."""
    config = ConfigLoader()
    work_types = config.get_work_types()

    table = Table(title="SDD Layer Decision Matrix")
    table.add_column("Work Type", style="cyan")
    table.add_column("Layers", style="yellow")
    table.add_column("Artifacts", style="white")
    table.add_column("Description", style="dim")

    layer_artifacts = {
        1: 'BRD', 2: 'PRD', 3: 'EARS', 4: 'BDD',
        5: 'ADR', 6: 'SYS', 7: 'REQ', 8: 'CTR',
        9: 'SPEC', 10: 'TSPEC', 11: 'TASKS',
    }

    for wt_name, wt_config in work_types.items():
        layers = wt_config.get('layers', [])
        artifacts = [layer_artifacts.get(l, '') for l in layers if l in layer_artifacts]
        table.add_row(
            wt_name.replace('_', ' ').title(),
            ', '.join(f'L{l}' for l in layers) if layers else 'None',
            ', '.join(artifacts) if artifacts else 'Code only',
            wt_config.get('description', ''),
        )

    console.print(table)


@click.command()
@click.option('--interactive', '-i', is_flag=True, help='Run interactive decision tree')
@click.option('--work-type', '-t', default=None,
              help='Work type (new_feature, enhancement, bug_fix, hotfix, config_change, refactoring)')
@click.option('--description', '-d', default='', help='Work description for classification')
@click.option('--show-matrix', is_flag=True, help='Show full decision matrix')
@click.option('--config', '-c', type=click.Path(exists=True), default=None,
              help='Path to project_model.yaml')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(interactive: bool, work_type: Optional[str], description: str,
         show_matrix: bool, config: Optional[str], verbose: bool):
    """Determine which SDD layers are needed for your work."""
    # Load config
    config_loader = None
    if config:
        config_loader = ConfigLoader(Path(config))
    else:
        try:
            config_loader = ConfigLoader()
        except Exception:
            pass

    # Show matrix if requested
    if show_matrix:
        display_decision_matrix()
        return

    runner = DecisionTreeRunner(config_loader)

    if interactive:
        recommendation = runner.run_interactive()
    elif work_type:
        recommendation = runner.run_automated(work_type, description)
    elif description:
        recommendation = runner.run_automated('', description)
    else:
        # Default to showing matrix and prompting
        display_decision_matrix()
        console.print("\n[dim]Use --interactive for guided selection or --work-type for direct selection[/dim]")
        return

    display_recommendation(recommendation)


if __name__ == "__main__":
    main()
