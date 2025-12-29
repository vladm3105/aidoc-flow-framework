#!/usr/bin/env python3
"""
sync_layer_config.py - Validate layer configuration consistency across SDD framework

Compares LAYER_REGISTRY.yaml against hardcoded definitions in Python scripts
and reports discrepancies.

Usage:
    python scripts/sync_layer_config.py --check    # Validate consistency
    python scripts/sync_layer_config.py --report   # Generate markdown report
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml")
    sys.exit(1)


def load_registry(registry_path: Path) -> Dict:
    """Load and validate LAYER_REGISTRY.yaml"""
    if not registry_path.exists():
        print(f"ERROR: Registry file not found: {registry_path}")
        sys.exit(1)

    with open(registry_path, 'r') as f:
        return yaml.safe_load(f)


def extract_artifacts_from_registry(registry: Dict) -> Set[str]:
    """Extract all artifact types from registry"""
    artifacts = set()
    for layer in registry.get('layers', []):
        artifacts.add(layer['artifact'])
    for artifact in registry.get('additional_artifacts', []):
        artifacts.add(artifact['artifact'])
    return artifacts


def extract_layer_numbers_from_registry(registry: Dict) -> Dict[str, int]:
    """Extract artifact to layer number mapping"""
    mapping = {}
    for layer in registry.get('layers', []):
        mapping[layer['artifact']] = layer['number']
    return mapping


def check_file_for_artifacts(file_path: Path, expected_artifacts: Set[str]) -> List[str]:
    """Check a file for hardcoded layer/artifact references"""
    issues = []

    if not file_path.exists():
        return [f"File not found: {file_path}"]

    content = file_path.read_text()

    # Check for LAYER_CONFIG or similar dict definitions
    layer_config_match = re.search(r'LAYER_CONFIG\s*=\s*\{([^}]+)\}', content, re.DOTALL)
    if layer_config_match:
        config_content = layer_config_match.group(1)
        # Extract artifact names from the config
        found_artifacts = set(re.findall(r"'([A-Z]+)'", config_content))

        missing_in_file = expected_artifacts - found_artifacts
        extra_in_file = found_artifacts - expected_artifacts

        if missing_in_file:
            issues.append(f"Missing artifacts in {file_path.name}: {missing_in_file}")
        if extra_in_file:
            issues.append(f"Extra artifacts in {file_path.name}: {extra_in_file}")

    return issues


def check_layer_numbers(file_path: Path, expected_numbers: Dict[str, int]) -> List[str]:
    """Check if layer numbers match registry"""
    issues = []

    if not file_path.exists():
        return []

    content = file_path.read_text()

    # Look for layer number assignments like 'layer': 1 or 'number': 1
    for artifact, expected_num in expected_numbers.items():
        # Pattern: 'ARTIFACT': {'layer': N, ...} or similar
        pattern = rf"'{artifact}'[^}}]*'(?:layer|number)':\s*(\d+)"
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            found_num = int(match)
            if found_num != expected_num:
                issues.append(
                    f"{file_path.name}: {artifact} layer={found_num}, "
                    f"expected {expected_num}"
                )

    return issues


def generate_report(registry: Dict, issues: List[str]) -> str:
    """Generate markdown consistency report"""
    lines = [
        "# Layer Configuration Consistency Report",
        "",
        f"**Generated**: {__import__('datetime').datetime.now().isoformat()}",
        f"**Registry Version**: {registry.get('version', 'unknown')}",
        "",
        "## Registry Summary",
        "",
        "| Layer | Artifact | Name |",
        "|-------|----------|------|",
    ]

    for layer in registry.get('layers', []):
        lines.append(f"| {layer['number']} | {layer['artifact']} | {layer['name']} |")

    lines.extend([
        "",
        "## Additional Artifacts",
        "",
    ])

    for artifact in registry.get('additional_artifacts', []):
        lines.append(f"- **{artifact['artifact']}**: {artifact['name']}")

    lines.extend([
        "",
        "## Consistency Check Results",
        "",
    ])

    if issues:
        lines.append(f"**Issues Found**: {len(issues)}")
        lines.append("")
        for issue in issues:
            lines.append(f"- {issue}")
    else:
        lines.append("**Status**: All files consistent with registry")

    lines.extend([
        "",
        "## Files Checked",
        "",
        "- `scripts/validate_cross_document.py`",
        "- `scripts/validate_all.py`",
        "",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Validate layer configuration consistency'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check files for consistency with registry'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate markdown consistency report'
    )
    parser.add_argument(
        '--root',
        default='.',
        help='Root directory of the project'
    )

    args = parser.parse_args()

    if not args.check and not args.report:
        parser.error("Must specify --check or --report")

    root = Path(args.root).resolve()
    registry_path = root / 'LAYER_REGISTRY.yaml'

    # Load registry
    registry = load_registry(registry_path)
    expected_artifacts = extract_artifacts_from_registry(registry)
    expected_numbers = extract_layer_numbers_from_registry(registry)

    print(f"Loaded registry v{registry.get('version', 'unknown')}")
    print(f"Found {len(registry.get('layers', []))} layers, "
          f"{len(registry.get('additional_artifacts', []))} additional artifacts")

    # Check files
    files_to_check = [
        root / 'scripts' / 'validate_cross_document.py',
        root / 'scripts' / 'validate_all.py',
    ]

    all_issues = []

    for file_path in files_to_check:
        issues = check_file_for_artifacts(file_path, expected_artifacts)
        all_issues.extend(issues)

        number_issues = check_layer_numbers(file_path, expected_numbers)
        all_issues.extend(number_issues)

    if args.check:
        if all_issues:
            print(f"\nFound {len(all_issues)} issue(s):")
            for issue in all_issues:
                print(f"  - {issue}")
            return 1
        else:
            print("\nAll files consistent with registry")
            return 0

    if args.report:
        report = generate_report(registry, all_issues)
        output_path = root / 'tmp' / 'layer_consistency_report.md'
        output_path.parent.mkdir(exist_ok=True)
        output_path.write_text(report)
        print(f"\nReport written to: {output_path}")

        # Also print to stdout
        print("\n" + "=" * 60)
        print(report)
        return 0


if __name__ == '__main__':
    sys.exit(main() or 0)
