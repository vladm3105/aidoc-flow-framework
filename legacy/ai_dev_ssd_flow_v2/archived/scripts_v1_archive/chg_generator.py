#!/usr/bin/env python3
"""
chg_generator.py - Generate CHG documents with 4-Gate integration

Traceability: @brd: BRD-01:FR-06
SPEC Reference: SPEC-07

This script creates Change Request (CHG) documents with automatic
change level classification and gate validation requirements.
"""

import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
from enum import Enum

import click
import yaml
from rich.console import Console
from rich.table import Table

# Configure console
console = Console()


class ChangeLevel(Enum):
    """Change level classification."""
    L1 = "Patch"
    L2 = "Minor"
    L3 = "Major"


@dataclass
class ChangeRequest:
    """Represents a change request."""
    description: str
    affected_layers: List[int]
    change_level: ChangeLevel
    affected_gates: List[str] = field(default_factory=list)
    requestor: str = ""
    rationale: str = ""


@dataclass
class ImpactReport:
    """Impact analysis report for a change."""
    technical_impact: str = "Low"
    schedule_impact: str = "Low"
    resource_impact: str = "Low"
    risk_impact: str = "Low"
    affected_artifacts: List[str] = field(default_factory=list)


class ConfigLoader:
    """Load change management configuration."""

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


class ChangeClassifier:
    """Classify changes by level and determine affected gates."""

    # Layer to artifact mapping
    LAYER_ARTIFACTS = {
        1: 'BRD', 2: 'PRD', 3: 'EARS', 4: 'BDD',
        5: 'ADR', 6: 'SYS', 7: 'REQ', 8: 'CTR',
        9: 'SPEC', 10: 'TSPEC', 11: 'TASKS',
        12: 'CODE', 13: 'TESTS', 14: 'RELEASE',
    }

    # Layer to gate mapping
    LAYER_GATES = {
        1: 'GATE-01', 2: 'GATE-01', 3: 'GATE-01', 4: 'GATE-01',
        5: 'GATE-05', 6: 'GATE-05', 7: 'GATE-05', 8: 'GATE-05',
        9: 'GATE-09', 10: 'GATE-09', 11: 'GATE-09',
        12: 'GATE-12', 13: 'GATE-12', 14: 'GATE-12',
    }

    def __init__(self, config: Optional[ConfigLoader] = None):
        self.config = config

    def classify_change(self, description: str, affected_layers: List[int]) -> ChangeLevel:
        """Classify change level based on description and affected layers."""
        # Keywords indicating change level
        l1_keywords = ['fix', 'bug', 'typo', 'patch', 'hotfix']
        l3_keywords = ['architecture', 'redesign', 'major', 'breaking', 'refactor']

        desc_lower = description.lower()

        # Check for L3 (Major) indicators
        if any(kw in desc_lower for kw in l3_keywords):
            return ChangeLevel.L3

        # Check for L1 (Patch) indicators
        if any(kw in desc_lower for kw in l1_keywords):
            # But if it affects multiple layers beyond TASKS, escalate
            if len(affected_layers) > 1 and not all(l == 11 for l in affected_layers):
                return ChangeLevel.L2
            return ChangeLevel.L1

        # Check layer scope
        if len(affected_layers) >= 4:
            return ChangeLevel.L3
        if len(affected_layers) >= 2:
            return ChangeLevel.L2

        # Default to L2 if affects spec layers (1-4)
        if any(layer <= 4 for layer in affected_layers):
            return ChangeLevel.L2

        return ChangeLevel.L1

    def identify_affected_layers(self, change: ChangeRequest) -> List[int]:
        """Identify all layers affected by a change (including cascading)."""
        affected = set(change.affected_layers)

        # Cascade logic: changes to higher layers may affect lower layers
        min_layer = min(affected) if affected else 11

        # If BRD changes (L1), PRD, EARS, BDD may need updates
        if 1 in affected:
            affected.update([2, 3, 4])

        # If PRD changes (L2), downstream spec layers may need updates
        if 2 in affected:
            affected.update([3, 9, 10, 11])

        # If ADR changes (L5), implementation may need updates
        if 5 in affected:
            affected.update([9, 10, 11])

        return sorted(affected)

    def determine_gates(self, layers: List[int]) -> List[str]:
        """Determine which gates need validation for affected layers."""
        gates = set()
        for layer in layers:
            gate = self.LAYER_GATES.get(layer)
            if gate:
                gates.add(gate)
        return sorted(gates)

    def get_artifacts_for_layers(self, layers: List[int]) -> List[str]:
        """Get artifact types for given layers."""
        return [self.LAYER_ARTIFACTS.get(l, f"L{l}") for l in layers if l in self.LAYER_ARTIFACTS]


class CHGDocumentGenerator:
    """Generate CHG documents."""

    TEMPLATE_PATH = Path("ucx_flow_v3/PROJECT/templates/CHG-PROJECT-TEMPLATE.md")

    def __init__(self, config: Optional[ConfigLoader] = None):
        self.config = config
        self.classifier = ChangeClassifier(config)

    def create_chg_document(self, change: ChangeRequest, chg_number: int) -> str:
        """Create a CHG document from change request."""
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')

        # Get affected info
        all_layers = self.classifier.identify_affected_layers(change)
        gates = self.classifier.determine_gates(all_layers)
        artifacts = self.classifier.get_artifacts_for_layers(all_layers)

        # Generate impact analysis
        impact = self.generate_impact_analysis(change)

        # Build document
        doc = f"""# CHG-{chg_number:03d}: {change.description[:60]}

**Version**: 1.0
**Status**: Draft
**Created**: {date_str}
**Change Level**: {change.change_level.name} ({change.change_level.value})

---

## 1. Change Summary

**Requested By**: {change.requestor or 'TBD'}
**Affected Layers**: {', '.join(f'L{l}' for l in all_layers)}
**Affected Gates**: {', '.join(gates)}

### 1.1 Description

{change.description}

### 1.2 Rationale

{change.rationale or 'TBD'}

### 1.3 Impact Assessment

| Dimension | Impact | Details |
|-----------|--------|---------|
| Technical | {impact.technical_impact} | Changes to {len(artifacts)} artifact types |
| Schedule | {impact.schedule_impact} | Requires update to {', '.join(artifacts[:3])} |
| Resource | {impact.resource_impact} | Standard team capacity |
| Risk | {impact.risk_impact} | Managed through gate validation |

## 2. Affected Artifacts

| Artifact | Current Version | Action |
|----------|-----------------|--------|
"""
        for artifact in artifacts:
            doc += f"| {artifact} | - | Update |\n"

        doc += f"""
## 3. Gate Validation Requirements

"""
        # Add gate checklists based on affected gates
        for gate in gates:
            doc += self._generate_gate_checklist(gate)

        doc += f"""
## 4. Approval Workflow

| Level | Approver | Status | Date |
|-------|----------|--------|------|
"""
        if change.change_level == ChangeLevel.L1:
            doc += "| L1 (Patch) | Developer | Pending | |\n"
        elif change.change_level == ChangeLevel.L2:
            doc += "| L1 (Patch) | Developer | N/A | |\n"
            doc += "| L2 (Minor) | Product Owner | Pending | |\n"
        else:
            doc += "| L1 (Patch) | Developer | N/A | |\n"
            doc += "| L2 (Minor) | Product Owner | Required | |\n"
            doc += "| L3 (Major) | Architect | Pending | |\n"

        doc += f"""
## 5. Implementation Plan

### 5.1 Tasks

| Task ID | Description | Assignee | Status |
|---------|-------------|----------|--------|
| CHG-{chg_number:03d}-01 | Update {artifacts[0] if artifacts else 'documentation'} | TBD | Pending |
| CHG-{chg_number:03d}-02 | Validate gate requirements | TBD | Pending |
| CHG-{chg_number:03d}-03 | Review and merge | TBD | Pending |

### 5.2 Timeline

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Approval | {date_str} | Pending |
| Implementation Start | - | Pending |
| Implementation Complete | - | Pending |
| Validation Complete | - | Pending |

## 6. Rollback Plan

If changes cause issues, revert to previous artifact versions and re-run validation.

---

## Traceability

- **Related TASKS**: TBD
- **Related Issues**: TBD
- **Parent CHG**: None
"""
        return doc

    def _generate_gate_checklist(self, gate: str) -> str:
        """Generate gate-specific checklist."""
        checklists = {
            'GATE-01': """### 3.1 GATE-01 (Business Requirements)
- [ ] BRD impact assessed
- [ ] PRD updated (if required)
- [ ] EARS updated (if required)
- [ ] BDD scenarios updated (if required)

""",
            'GATE-05': """### 3.2 GATE-05 (Architecture)
- [ ] ADR created (if architectural change)
- [ ] SYS requirements updated
- [ ] REQ elements updated
- [ ] CTR contracts updated

""",
            'GATE-09': """### 3.3 GATE-09 (Implementation Specification)
- [ ] SPEC updated
- [ ] TSPEC updated
- [ ] TASKS created for implementation

""",
            'GATE-12': """### 3.4 GATE-12 (Code Implementation)
- [ ] Code changes implemented
- [ ] Tests pass
- [ ] Coverage maintained

""",
        }
        return checklists.get(gate, f"### {gate}\n- [ ] Validation complete\n\n")

    def generate_impact_analysis(self, change: ChangeRequest) -> ImpactReport:
        """Generate impact analysis for a change."""
        layers = change.affected_layers
        num_layers = len(layers)

        # Determine impacts based on scope
        if num_layers >= 4 or change.change_level == ChangeLevel.L3:
            return ImpactReport(
                technical_impact="High",
                schedule_impact="High",
                resource_impact="Medium",
                risk_impact="High",
                affected_artifacts=self.classifier.get_artifacts_for_layers(layers),
            )
        elif num_layers >= 2 or change.change_level == ChangeLevel.L2:
            return ImpactReport(
                technical_impact="Medium",
                schedule_impact="Medium",
                resource_impact="Low",
                risk_impact="Medium",
                affected_artifacts=self.classifier.get_artifacts_for_layers(layers),
            )
        else:
            return ImpactReport(
                technical_impact="Low",
                schedule_impact="Low",
                resource_impact="Low",
                risk_impact="Low",
                affected_artifacts=self.classifier.get_artifacts_for_layers(layers),
            )

    def create_approval_checklist(self, gates: List[str]) -> str:
        """Create approval checklist for gates."""
        checklist = "## Approval Checklist\n\n"
        for gate in gates:
            checklist += f"- [ ] {gate} validation passed\n"
        return checklist


class GateTransitionValidator:
    """Validate gate transitions for changes."""

    def __init__(self, config: Optional[ConfigLoader] = None):
        self.config = config
        self.classifier = ChangeClassifier(config)

    def validate_gate_entry(self, artifact_path: Path, gate: str) -> bool:
        """Validate that prerequisites are met to enter a gate."""
        # In a full implementation, would check:
        # 1. Upstream gates are complete
        # 2. Required artifacts exist
        # 3. Artifact scores meet threshold
        return True

    def validate_gate_exit(self, artifact_path: Path, gate: str) -> bool:
        """Validate that gate requirements are met to exit."""
        # In a full implementation, would run gate validators
        return True

    def generate_gate_report(self, results: Dict[str, bool]) -> str:
        """Generate report of gate validation results."""
        report = "## Gate Validation Report\n\n"
        report += "| Gate | Status |\n"
        report += "|------|--------|\n"
        for gate, passed in results.items():
            status = "PASS" if passed else "FAIL"
            report += f"| {gate} | {status} |\n"
        return report


def get_next_chg_number(output_dir: Path) -> int:
    """Get next CHG number by scanning existing files."""
    if not output_dir.exists():
        return 1

    max_num = 0
    for file in output_dir.glob("CHG-*.md"):
        try:
            num = int(file.stem.split('-')[1])
            max_num = max(max_num, num)
        except (IndexError, ValueError):
            pass
    return max_num + 1


@click.command()
@click.option('--description', '-d', required=True, help='Change description')
@click.option('--affected-layers', '-l', required=True,
              help='Comma-separated list of affected layers (e.g., 2,9,11)')
@click.option('--rationale', '-r', default='', help='Rationale for the change')
@click.option('--requestor', default='', help='Name of change requestor')
@click.option('--output', '-o', required=True, type=click.Path(),
              help='Output directory for CHG document')
@click.option('--config', '-c', type=click.Path(exists=True), default=None,
              help='Path to project_model.yaml')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(description: str, affected_layers: str, rationale: str, requestor: str,
         output: str, config: Optional[str], verbose: bool):
    """Generate CHG document with 4-Gate integration."""
    # Parse layers
    try:
        layers = [int(l.strip()) for l in affected_layers.split(',')]
    except ValueError:
        console.print("[red]Error: affected-layers must be comma-separated integers[/red]")
        sys.exit(1)

    # Load configuration
    config_loader = None
    if config:
        config_loader = ConfigLoader(Path(config))
    else:
        try:
            config_loader = ConfigLoader()
        except Exception:
            pass

    # Classify change
    classifier = ChangeClassifier(config_loader)
    change_level = classifier.classify_change(description, layers)
    gates = classifier.determine_gates(layers)

    change = ChangeRequest(
        description=description,
        affected_layers=layers,
        change_level=change_level,
        affected_gates=gates,
        requestor=requestor,
        rationale=rationale,
    )

    # Display classification
    table = Table(title="Change Classification")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Description", description[:50] + "...")
    table.add_row("Change Level", f"{change_level.name} ({change_level.value})")
    table.add_row("Affected Layers", ', '.join(f'L{l}' for l in layers))
    table.add_row("Affected Gates", ', '.join(gates))

    console.print(table)

    # Generate document
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)

    chg_number = get_next_chg_number(output_path)
    generator = CHGDocumentGenerator(config_loader)
    document = generator.create_chg_document(change, chg_number)

    # Write document
    chg_file = output_path / f"CHG-{chg_number:03d}.md"
    with open(chg_file, 'w') as f:
        f.write(document)

    console.print(f"\n[green]Created: {chg_file}[/green]")


if __name__ == "__main__":
    main()
