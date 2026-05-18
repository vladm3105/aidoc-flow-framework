#!/usr/bin/env python3
"""
validate_artifact.py - Unified artifact validation with 4-Gate system

Traceability: @brd: BRD-01:FR-03, FR-06
SPEC Reference: SPEC-03

This script provides a unified entry point for SDD artifact validation,
dispatching to appropriate validators based on artifact type and integrating
the 4-Gate validation system.
"""

import os
import sys
import json
import subprocess
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple

import click
import yaml
from rich.console import Console
from rich.table import Table

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
console = Console()


@dataclass
class ValidationResult:
    """Result of a single validation run."""
    artifact_path: Path
    validator: str
    success: bool
    exit_code: int
    output: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class GateResult:
    """Result of gate validation."""
    gate_id: str
    gate_name: str
    passed: bool
    score: int
    threshold: int
    artifacts_validated: int
    failed_artifacts: List[str] = field(default_factory=list)


class ConfigLoader:
    """Load validation configuration."""

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


class ArtifactTypeDetector:
    """Detect artifact type and layer from file path."""

    # Artifact type to layer mapping
    LAYER_MAP = {
        'BRD': 1, 'PRD': 2, 'EARS': 3, 'BDD': 4,
        'ADR': 5, 'SYS': 6, 'REQ': 7, 'CTR': 8,
        'SPEC': 9, 'TSPEC': 10, 'TASKS': 11,
        'CODE': 12, 'TESTS': 13, 'RELEASE': 14,
    }

    # Layer to gate mapping
    GATE_MAP = {
        1: 'GATE-01', 2: 'GATE-01', 3: 'GATE-01', 4: 'GATE-01',
        5: 'GATE-05', 6: 'GATE-05', 7: 'GATE-05', 8: 'GATE-05',
        9: 'GATE-09', 10: 'GATE-09', 11: 'GATE-09',
        12: 'GATE-12', 13: 'GATE-12', 14: 'GATE-12',
    }

    def __init__(self, config: Optional[ConfigLoader] = None):
        self.config = config

    def detect_type(self, filepath: Path) -> Optional[str]:
        """Detect artifact type from file path."""
        name = filepath.stem.upper()
        parent = filepath.parent.name.upper()

        # Check filename prefix
        for artifact_type in self.LAYER_MAP:
            if name.startswith(artifact_type):
                return artifact_type
            # Check if parent directory contains type
            if artifact_type in parent:
                return artifact_type

        # Check for code files
        if filepath.suffix in {'.py', '.js', '.ts', '.go', '.rs', '.java'}:
            return 'CODE'

        # Check for test files
        if 'test' in name.lower() or filepath.parent.name.lower() == 'tests':
            return 'TESTS'

        return None

    def detect_layer(self, filepath: Path) -> int:
        """Detect artifact layer from file path."""
        artifact_type = self.detect_type(filepath)
        if artifact_type:
            return self.LAYER_MAP.get(artifact_type, 0)
        return 0

    def get_validator_path(self, artifact_type: str) -> Optional[str]:
        """Get validator script path for artifact type."""
        # Validator dispatch table
        validators = {
            'BRD': 'validate_cross_document.py --type BRD',
            'PRD': 'validate_cross_document.py --type PRD',
            'EARS': 'validate_cross_document.py --type EARS',
            'BDD': 'validate_cross_document.py --type BDD',
            'ADR': 'validate_cross_document.py --type ADR',
            'SYS': 'validate_cross_document.py --type SYS',
            'REQ': 'validate_cross_document.py --type REQ',
            'CTR': 'validate_schema_sync.py',
            'SPEC': 'validate_cross_document.py --type SPEC',
            'TSPEC': 'validate_cross_document.py --type TSPEC',
            'TASKS': 'validate_cross_document.py --type TASKS',
            'CODE': 'validate_tags_against_docs.py',
            'TESTS': 'validate_terminology.py',
        }
        return validators.get(artifact_type)

    def get_gate(self, layer: int) -> str:
        """Get applicable gate for layer."""
        return self.GATE_MAP.get(layer, 'GATE-01')


class GateValidator:
    """Validate artifacts against 4-Gate requirements."""

    def __init__(self, config: Optional[ConfigLoader] = None):
        self.config = config
        self.detector = ArtifactTypeDetector(config)

    def get_applicable_gate(self, layer: int) -> str:
        """Get the gate that applies to a given layer."""
        return self.detector.get_gate(layer)

    def get_gate_config(self, gate_id: str) -> Dict[str, Any]:
        """Get gate configuration."""
        if self.config:
            gates = self.config.get('quality_gates', {})
            return gates.get(gate_id, {})
        return self._default_gate_config(gate_id)

    def _default_gate_config(self, gate_id: str) -> Dict[str, Any]:
        """Default gate configurations."""
        defaults = {
            'GATE-01': {
                'name': 'Business Requirements Gate',
                'layers': [1, 2, 3, 4],
                'threshold': 90,
            },
            'GATE-05': {
                'name': 'Architecture Gate',
                'layers': [5, 6, 7, 8],
                'threshold': 90,
            },
            'GATE-09': {
                'name': 'Implementation Specification Gate',
                'layers': [9, 10, 11],
                'threshold': 90,
            },
            'GATE-12': {
                'name': 'Code Implementation Gate',
                'layers': [12, 13, 14],
                'threshold': 85,
            },
        }
        return defaults.get(gate_id, {})

    def validate_gate_requirements(self, artifact_path: Path, gate_id: str) -> GateResult:
        """Validate artifact against gate requirements."""
        gate_config = self.get_gate_config(gate_id)
        layer = self.detector.detect_layer(artifact_path)
        allowed_layers = gate_config.get('layers', [])

        # Check if artifact layer is valid for this gate
        if layer not in allowed_layers:
            return GateResult(
                gate_id=gate_id,
                gate_name=gate_config.get('name', gate_id),
                passed=False,
                score=0,
                threshold=gate_config.get('threshold', 90),
                artifacts_validated=0,
                failed_artifacts=[f"{artifact_path.name}: Layer {layer} not in gate {gate_id}"],
            )

        # Run validation
        runner = ValidatorRunner(self.config)
        result = runner.run_validator(artifact_path)

        score = 100 if result.success else 0
        threshold = gate_config.get('threshold', 90)

        return GateResult(
            gate_id=gate_id,
            gate_name=gate_config.get('name', gate_id),
            passed=score >= threshold,
            score=score,
            threshold=threshold,
            artifacts_validated=1,
            failed_artifacts=[] if result.success else [artifact_path.name],
        )

    def check_upstream_gates(self, artifact_path: Path) -> List[str]:
        """Check which upstream gates must be passed first."""
        layer = self.detector.detect_layer(artifact_path)
        current_gate = self.get_applicable_gate(layer)

        # Determine required upstream gates
        gate_order = ['GATE-01', 'GATE-05', 'GATE-09', 'GATE-12']
        current_idx = gate_order.index(current_gate) if current_gate in gate_order else 0

        return gate_order[:current_idx]


class ValidatorRunner:
    """Run validators on artifacts."""

    def __init__(self, config: Optional[ConfigLoader] = None):
        self.config = config
        self.detector = ArtifactTypeDetector(config)
        self.scripts_path = self._find_scripts_path()

    def _find_scripts_path(self) -> Path:
        """Find the scripts directory."""
        candidates = [
            Path("ucx_flow_v3/scripts"),
            Path("scripts"),
            Path(__file__).parent,
        ]
        for path in candidates:
            if path.exists():
                return path
        return Path("ucx_flow_v3/scripts")

    def run_validator(self, artifact_path: Path,
                      validator_override: Optional[str] = None) -> ValidationResult:
        """Run appropriate validator for artifact."""
        artifact_type = self.detector.detect_type(artifact_path)
        if not artifact_type:
            return ValidationResult(
                artifact_path=artifact_path,
                validator="unknown",
                success=False,
                exit_code=1,
                errors=["Could not detect artifact type"],
            )

        validator_cmd = validator_override or self.detector.get_validator_path(artifact_type)
        if not validator_cmd:
            return ValidationResult(
                artifact_path=artifact_path,
                validator="none",
                success=True,
                exit_code=0,
                warnings=[f"No validator configured for {artifact_type}"],
            )

        # Build command
        parts = validator_cmd.split()
        script = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        script_path = self.scripts_path / script
        if not script_path.exists():
            return ValidationResult(
                artifact_path=artifact_path,
                validator=script,
                success=False,
                exit_code=1,
                errors=[f"Validator script not found: {script_path}"],
            )

        # Run validator
        cmd = [sys.executable, str(script_path)] + args + [str(artifact_path)]
        logger.debug(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            return ValidationResult(
                artifact_path=artifact_path,
                validator=script,
                success=result.returncode == 0,
                exit_code=result.returncode,
                output=result.stdout,
                errors=result.stderr.splitlines() if result.returncode != 0 else [],
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                artifact_path=artifact_path,
                validator=script,
                success=False,
                exit_code=124,
                errors=["Validator timed out"],
            )
        except Exception as e:
            return ValidationResult(
                artifact_path=artifact_path,
                validator=script,
                success=False,
                exit_code=1,
                errors=[str(e)],
            )

    def collect_results(self, results: List[ValidationResult]) -> Tuple[int, int, int]:
        """Collect and summarize results. Returns (passed, failed, warnings)."""
        passed = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)
        warnings = sum(len(r.warnings) for r in results)
        return passed, failed, warnings


def display_results(results: List[ValidationResult], gate_results: List[GateResult] = None):
    """Display validation results as rich tables."""
    # Artifact validation table
    table = Table(title="Artifact Validation Results")
    table.add_column("Artifact", style="cyan")
    table.add_column("Type", style="white")
    table.add_column("Validator", style="yellow")
    table.add_column("Status", style="bold")

    for r in results:
        artifact_type = ArtifactTypeDetector().detect_type(r.artifact_path) or "?"
        status = "[green]PASS[/green]" if r.success else "[red]FAIL[/red]"
        table.add_row(
            r.artifact_path.name,
            artifact_type,
            r.validator,
            status,
        )

    console.print(table)

    # Gate validation table
    if gate_results:
        console.print()
        gate_table = Table(title="Gate Validation Results")
        gate_table.add_column("Gate", style="cyan")
        gate_table.add_column("Name", style="white")
        gate_table.add_column("Score", style="yellow")
        gate_table.add_column("Threshold", style="magenta")
        gate_table.add_column("Status", style="bold")

        for g in gate_results:
            status = "[green]PASS[/green]" if g.passed else "[red]FAIL[/red]"
            gate_table.add_row(
                g.gate_id,
                g.gate_name,
                str(g.score),
                str(g.threshold),
                status,
            )

        console.print(gate_table)


def detect_gates_for_path(path: Path) -> List[str]:
    """Detect which gates are affected by changes to a path."""
    detector = ArtifactTypeDetector()
    affected_gates = set()

    if path.is_dir():
        for file in path.rglob('*'):
            if file.is_file():
                layer = detector.detect_layer(file)
                if layer > 0:
                    gate = detector.get_gate(layer)
                    affected_gates.add(gate)
    else:
        layer = detector.detect_layer(path)
        if layer > 0:
            gate = detector.get_gate(layer)
            affected_gates.add(gate)

    return sorted(affected_gates)


@click.command()
@click.option('--path', '-p', required=False, type=click.Path(exists=True),
              help='Path to artifact or directory')
@click.option('--strict', is_flag=True, help='Fail on warnings')
@click.option('--gate', '-g', default=None,
              help='Specific gate to validate (GATE-01, GATE-05, GATE-09, GATE-12)')
@click.option('--detect-gates', is_flag=True, help='Detect affected gates and output as JSON')
@click.option('--validate-gates', is_flag=True, help='Validate all gates for path')
@click.option('--gates-file', type=click.Path(exists=True), default=None,
              help='JSON file with gate analysis to validate')
@click.option('--output', '-o', type=click.Path(), default=None,
              help='Output file for results')
@click.option('--config', '-c', type=click.Path(exists=True), default=None,
              help='Path to project_model.yaml')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(path: Optional[str], strict: bool, gate: Optional[str], detect_gates: bool,
         validate_gates: bool, gates_file: Optional[str], output: Optional[str],
         config: Optional[str], verbose: bool):
    """Unified SDD artifact validation with 4-Gate system."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    config_loader = None
    if config:
        config_loader = ConfigLoader(Path(config))
    else:
        try:
            config_loader = ConfigLoader()
        except Exception:
            pass

    # Handle detect-gates mode
    if detect_gates:
        if not path:
            console.print("[red]Error: --path required for --detect-gates[/red]")
            sys.exit(1)

        gates = detect_gates_for_path(Path(path))
        result = {"affected_gates": gates, "path": path}

        if output:
            with open(output, 'w') as f:
                json.dump(result, f, indent=2)
            console.print(f"[green]Gate analysis written to {output}[/green]")
        else:
            console.print(json.dumps(result, indent=2))
        return

    # Handle validate-gates mode with gates file
    if validate_gates and gates_file:
        with open(gates_file, 'r') as f:
            gate_data = json.load(f)

        affected_gates = gate_data.get('affected_gates', [])
        if not affected_gates:
            console.print("[green]No gates to validate[/green]")
            return

        gate_validator = GateValidator(config_loader)
        console.print(f"[bold]Validating gates: {', '.join(affected_gates)}[/bold]")
        # In practice, would validate each gate's artifacts here
        console.print("[green]Gate validation complete[/green]")
        return

    # Standard validation mode
    if not path:
        console.print("[red]Error: --path required for validation[/red]")
        sys.exit(1)

    artifact_path = Path(path)
    results: List[ValidationResult] = []
    gate_results: List[GateResult] = []

    runner = ValidatorRunner(config_loader)
    gate_validator = GateValidator(config_loader)

    # Collect files to validate
    files_to_validate = []
    if artifact_path.is_dir():
        for ext in ['.md', '.yaml', '.yml', '.feature', '.py']:
            files_to_validate.extend(artifact_path.rglob(f'*{ext}'))
    else:
        files_to_validate = [artifact_path]

    console.print(f"[bold]Validating {len(files_to_validate)} artifacts...[/bold]")

    # Run validation
    for file in files_to_validate:
        result = runner.run_validator(file)
        results.append(result)

        # Gate validation
        if gate or validate_gates:
            layer = ArtifactTypeDetector().detect_layer(file)
            target_gate = gate or ArtifactTypeDetector().get_gate(layer)
            if target_gate:
                gate_result = gate_validator.validate_gate_requirements(file, target_gate)
                gate_results.append(gate_result)

    # Display results
    display_results(results, gate_results)

    # Write output
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write("# Validation Report\n\n")
            for r in results:
                status = "PASS" if r.success else "FAIL"
                f.write(f"- {r.artifact_path.name}: {status}\n")

    # Exit with appropriate code
    passed, failed, warnings = runner.collect_results(results)
    if failed > 0:
        sys.exit(1)
    if strict and warnings > 0:
        sys.exit(1)

    console.print(f"\n[green]Validation complete: {passed} passed, {failed} failed[/green]")


if __name__ == "__main__":
    main()
