#!/usr/bin/env python3
"""
CHG Routing Validation Script
Determines correct gate routing based on change source, scope, and level.
"""

import argparse
import re
import sys
import yaml
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# ANSI colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

# Gate routing rules
GATE_ROUTING = {
    'upstream': 'GATE-01',      # L1-L4 entry
    'midstream': 'GATE-05',     # L5-L8 entry (may bubble up to GATE-01)
    'design-optimization': 'GATE-09',  # L9-L11 entry
    'downstream': 'GATE-12',    # L12-L14 entry (may bubble up)
    'external': 'GATE-05',      # Usually enters at architecture/contract
    'feedback': 'GATE-12',      # Usually enters at implementation
    'emergency': 'BYPASS',      # Emergency bypass
}

GATE_LAYERS = {
    'GATE-01': ['L1', 'L2', 'L3', 'L4'],
    'GATE-05': ['L5', 'L6', 'L7', 'L8'],
    'GATE-09': ['L9', 'L10', 'L11'],
    'GATE-12': ['L12', 'L13', 'L14'],
}

LAYER_NAMES = {
    'L1': 'BRD', 'L2': 'PRD', 'L3': 'EARS', 'L4': 'BDD',
    'L5': 'ADR', 'L6': 'SYS', 'L7': 'REQ', 'L8': 'CTR',
    'L9': 'SPEC', 'L10': 'TSPEC', 'L11': 'TASKS',
    'L12': 'Code', 'L13': 'Tests', 'L14': 'Validation',
}


def parse_yaml_frontmatter(content: str) -> Optional[Dict]:
    """Extract YAML frontmatter from markdown."""
    if not content.startswith('---'):
        return None

    parts = content.split('---', 2)
    if len(parts) < 3:
        return None

    try:
        return yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None


def extract_change_source(content: str, frontmatter: Optional[Dict]) -> Optional[str]:
    """Extract change source from CHG document."""
    # Check frontmatter first
    if frontmatter:
        custom = frontmatter.get('custom_fields', {})
        if custom.get('change_source'):
            return custom['change_source'].lower()

    # Check document content
    patterns = [
        r'change[_\s]?source[:\s]+(\w+)',
        r'Source[:\s]+(\w+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).lower()

    return None


def extract_change_level(content: str, frontmatter: Optional[Dict]) -> Optional[str]:
    """Extract change level from CHG document."""
    # Check frontmatter first
    if frontmatter:
        custom = frontmatter.get('custom_fields', {})
        if custom.get('change_level'):
            return custom['change_level'].upper()

    # Check document content
    patterns = [
        r'change[_\s]?level[:\s]+(L[123]|EMERGENCY)',
        r'Level[:\s]+(L[123]|EMERGENCY)',
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).upper()

    return None


def extract_affected_layers(content: str) -> List[str]:
    """Extract affected layers from CHG document."""
    layers = set()

    # Look for layer patterns
    for i in range(1, 15):
        patterns = [
            rf'\bL{i}\b',
            rf'Layer\s*{i}\b',
            rf'\b{LAYER_NAMES.get(f"L{i}", "")}\b',
        ]
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                layers.add(f'L{i}')

    return sorted(layers, key=lambda x: int(x[1:]))


def check_breaking_change(content: str) -> bool:
    """Check if document indicates breaking change."""
    patterns = [
        r'breaking\s*(change|api|compatibility)',
        r'backward[s]?\s*incompatible',
        r'non-backward[s]?\s*compatible',
    ]

    for pattern in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False


def check_emergency_criteria(content: str) -> bool:
    """Check if change qualifies for emergency bypass."""
    emergency_patterns = [
        r'P1\s*incident',
        r'critical\s*security',
        r'CVSS[:\s]*(9\.[0-9]|10\.0)',
        r'production\s*down',
        r'data\s*breach',
        r'active\s*exploit',
    ]

    for pattern in emergency_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False


def determine_entry_gate(
    change_source: Optional[str],
    affected_layers: List[str],
    is_breaking: bool,
    is_emergency: bool
) -> Tuple[str, str]:
    """Determine the correct entry gate and provide reasoning."""

    # Emergency bypass
    if is_emergency:
        return 'BYPASS', 'Emergency criteria met (P1/Critical Security)'

    # Default routing based on source
    if change_source in GATE_ROUTING:
        recommended_gate = GATE_ROUTING[change_source]
    else:
        # Infer from affected layers
        if any(l in affected_layers for l in GATE_LAYERS['GATE-01']):
            recommended_gate = 'GATE-01'
        elif any(l in affected_layers for l in GATE_LAYERS['GATE-05']):
            recommended_gate = 'GATE-05'
        elif any(l in affected_layers for l in GATE_LAYERS['GATE-09']):
            recommended_gate = 'GATE-09'
        else:
            recommended_gate = 'GATE-12'

    # Determine reasoning
    if change_source:
        reason = f"Change source '{change_source}' routes to {recommended_gate}"
    else:
        reason = f"Affected layers {affected_layers} indicate {recommended_gate}"

    # Check for bubble-up requirements
    if recommended_gate in ['GATE-05', 'GATE-09', 'GATE-12']:
        if any(l in affected_layers for l in GATE_LAYERS['GATE-01']):
            return 'GATE-01', f"Layers {affected_layers} require starting at GATE-01"

    if recommended_gate in ['GATE-09', 'GATE-12']:
        if any(l in affected_layers for l in GATE_LAYERS['GATE-05']):
            return 'GATE-05', f"Layers {affected_layers} require starting at GATE-05"

    return recommended_gate, reason


def determine_cascade_path(entry_gate: str, affected_layers: List[str]) -> List[str]:
    """Determine the cascade path from entry gate to completion."""
    gate_order = ['GATE-01', 'GATE-05', 'GATE-09', 'GATE-12']

    if entry_gate == 'BYPASS':
        return ['BYPASS (Emergency)', 'Post-mortem review']

    try:
        start_idx = gate_order.index(entry_gate)
        return gate_order[start_idx:]
    except ValueError:
        return [entry_gate]


def validate_routing(chg_file: Path, verbose: bool = False) -> int:
    """Validate CHG routing and provide recommendations."""

    print("=" * 50)
    print("CHG Routing Validation")
    print("=" * 50)
    print(f"File: {chg_file}")
    print()

    # Read file
    try:
        content = chg_file.read_text()
    except Exception as e:
        print(f"{RED}ERROR: Could not read file: {e}{NC}")
        return 3

    # Parse frontmatter
    frontmatter = parse_yaml_frontmatter(content)

    # Extract information
    change_source = extract_change_source(content, frontmatter)
    change_level = extract_change_level(content, frontmatter)
    affected_layers = extract_affected_layers(content)
    is_breaking = check_breaking_change(content)
    is_emergency = check_emergency_criteria(content)

    # Display extracted information
    print("--- Extracted Information ---")
    print(f"  Change Source: {change_source or 'Not specified'}")
    print(f"  Change Level:  {change_level or 'Not specified'}")
    print(f"  Affected Layers: {', '.join(affected_layers) if affected_layers else 'None detected'}")
    print(f"  Breaking Change: {'Yes' if is_breaking else 'No'}")
    print(f"  Emergency:       {'Yes' if is_emergency else 'No'}")
    print()

    # Determine routing
    entry_gate, reason = determine_entry_gate(
        change_source, affected_layers, is_breaking, is_emergency
    )
    cascade_path = determine_cascade_path(entry_gate, affected_layers)

    # Display routing recommendation
    print("--- Routing Recommendation ---")
    print(f"  Entry Gate: {GREEN}{entry_gate}{NC}")
    print(f"  Reason: {reason}")
    print(f"  Cascade Path: {' -> '.join(cascade_path)}")
    print()

    # Validation checks
    errors = 0
    warnings = 0

    print("--- Validation Checks ---")

    # Check: Source should be specified
    if not change_source:
        print(f"  {YELLOW}WARNING: Change source not specified{NC}")
        print("    -> Add change_source to frontmatter or document body")
        warnings += 1
    else:
        print(f"  {GREEN}✓ Change source specified: {change_source}{NC}")

    # Check: Level should be specified
    if not change_level:
        print(f"  {YELLOW}WARNING: Change level not specified{NC}")
        print("    -> Add change_level to frontmatter (L1/L2/L3)")
        warnings += 1
    else:
        print(f"  {GREEN}✓ Change level specified: {change_level}{NC}")

    # Check: Breaking change should be L3
    if is_breaking and change_level and change_level != 'L3':
        print(f"  {RED}ERROR: Breaking change must be L3 (found: {change_level}){NC}")
        errors += 1
    elif is_breaking:
        print(f"  {GREEN}✓ Breaking change correctly classified{NC}")

    # Check: Emergency should have proper authorization
    if is_emergency:
        if 'authorized' not in content.lower() and 'commander' not in content.lower():
            print(f"  {YELLOW}WARNING: Emergency bypass should document authorization{NC}")
            warnings += 1
        else:
            print(f"  {GREEN}✓ Emergency authorization documented{NC}")

    # Check: Layers should be documented
    if not affected_layers:
        print(f"  {YELLOW}WARNING: No affected layers detected{NC}")
        print("    -> Document which layers are impacted")
        warnings += 1
    else:
        print(f"  {GREEN}✓ Affected layers documented: {len(affected_layers)} layers{NC}")

    print()
    print("=" * 50)
    print("Validation Summary")
    print("=" * 50)
    print(f"  Errors:   {RED}{errors}{NC}")
    print(f"  Warnings: {YELLOW}{warnings}{NC}")
    print()

    if errors > 0:
        print(f"{RED}ROUTING VALIDATION FAILED{NC}")
        return 2
    elif warnings > 0:
        print(f"{YELLOW}ROUTING VALIDATED with warnings{NC}")
        return 1
    else:
        print(f"{GREEN}ROUTING VALIDATED successfully{NC}")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description='Validate CHG routing and determine correct gate entry'
    )
    parser.add_argument('chg_file', type=Path, help='Path to CHG document')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--check-bubble-up', action='store_true',
                       help='Check if bubble-up to upstream gate is required')
    parser.add_argument('--spec-readiness', action='store_true',
                       help='Check SPEC implementation readiness')
    parser.add_argument('--validate-root-cause', action='store_true',
                       help='Validate root cause analysis for downstream changes')

    args = parser.parse_args()

    if not args.chg_file.exists():
        print(f"{RED}ERROR: File not found: {args.chg_file}{NC}")
        sys.exit(3)

    exit_code = validate_routing(args.chg_file, args.verbose)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
