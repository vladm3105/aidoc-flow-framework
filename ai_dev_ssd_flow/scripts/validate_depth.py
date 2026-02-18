#!/usr/bin/env python3
"""
Validate project has required SDD artifacts for configured depth.

Usage:
    python validate_depth.py [config_path] [docs_root]

Example:
    python validate_depth.py sdd_config.yaml docs/
"""

import argparse
import sys
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

LAYER_DIRS = {
    0: "00_REF",
    1: "01_BRD",
    2: "02_PRD",
    3: "03_EARS",
    4: "04_BDD",
    5: "05_ADR",
    6: "06_SYS",
    7: "07_REQ",
    8: "08_CTR",
    9: "09_SPEC",
    10: "10_TSPEC",
    11: "11_TASKS",
}

LAYER_NAMES = {
    0: "REF (Reference)",
    1: "BRD (Business Requirements)",
    2: "PRD (Product Requirements)",
    3: "EARS (Formal Requirements)",
    4: "BDD (Behavior Tests)",
    5: "ADR (Architecture Decisions)",
    6: "SYS (System Requirements)",
    7: "REQ (Atomic Requirements)",
    8: "CTR (Contracts)",
    9: "SPEC (Technical Specifications)",
    10: "TSPEC (Test Specifications)",
    11: "TASKS (Implementation Tasks)",
}


def load_config(config_path: Path) -> dict:
    """Load SDD configuration."""
    if not YAML_AVAILABLE:
        print("Error: PyYAML not installed. Run: pip install pyyaml")
        sys.exit(1)
    with open(config_path) as f:
        return yaml.safe_load(f)


def validate_depth(config: dict, docs_root: Path) -> tuple:
    """
    Check required layers exist for configured depth.

    Returns:
        (is_valid, present_layers, missing_layers)
    """
    depth = config.get("sdd_depth", "standard")
    required = config.get("required_layers", {}).get(depth, [])

    present = []
    missing = []

    for layer in required:
        layer_dir = docs_root / LAYER_DIRS.get(layer, f"{layer:02d}_UNKNOWN")
        if layer_dir.exists() and any(layer_dir.iterdir()):
            present.append(f"Layer {layer}: {LAYER_NAMES.get(layer, 'Unknown')}")
        else:
            missing.append(f"Layer {layer}: {LAYER_NAMES.get(layer, 'Unknown')}")

    return len(missing) == 0, present, missing


def main():
    parser = argparse.ArgumentParser(description="Validate SDD depth configuration")
    parser.add_argument("config", nargs="?", default="sdd_config.yaml",
                        help="Path to sdd_config.yaml")
    parser.add_argument("docs", nargs="?", default="docs",
                        help="Path to docs directory")
    parser.add_argument("--strict", action="store_true",
                        help="Exit with error if validation fails")
    args = parser.parse_args()

    config_path = Path(args.config)
    docs_root = Path(args.docs)

    if not config_path.exists():
        print(f"Config file not found: {config_path}")
        print("Create from template: governance/templates/sdd_config.yaml")
        sys.exit(1 if args.strict else 0)

    config = load_config(config_path)
    depth = config.get("sdd_depth", "standard")

    print(f"SDD Depth: {depth.upper()}")
    print(f"Docs Root: {docs_root}")
    print()

    is_valid, present, missing = validate_depth(config, docs_root)

    if present:
        print("Present Layers:")
        for layer in present:
            print(f"  + {layer}")

    if missing:
        print("\nMissing Layers:")
        for layer in missing:
            print(f"  - {layer}")

    print()
    if is_valid:
        print(f"All required layers present for {depth} depth")
        sys.exit(0)
    else:
        print(f"Missing {len(missing)} required layer(s) for {depth} depth")
        block = config.get("validation", {}).get("block_on_missing_layers", True)
        sys.exit(1 if (args.strict or block) else 0)


if __name__ == "__main__":
    main()
