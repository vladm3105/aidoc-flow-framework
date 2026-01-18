#!/usr/bin/env python3
"""
Schema-Template Version Synchronization Validator

Validates that template schema_version fields match corresponding schema schema_version fields
for all artifact types in the SDD framework.

Usage:
    python scripts/validate_schema_sync.py [--verbose] [--fix]

Options:
    --verbose    Show detailed output for each artifact type
    --fix        Attempt to update mismatched versions (updates templates to match schemas)
"""

import sys
import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SyncResult:
    """Result of schema-template sync check."""
    artifact_type: str
    template_path: Path
    schema_path: Optional[Path]
    template_version: Optional[str]
    schema_version: Optional[str]
    is_synced: bool
    error: Optional[str] = None


# Artifact types and their expected files
ARTIFACT_TYPES = {
    "ADR": {"template": "ADR-MVP-TEMPLATE.md", "schema": "ADR_SCHEMA.yaml", "layer": 5},
    "BDD": {"template": "BDD-MVP-TEMPLATE.feature", "schema": "BDD_SCHEMA.yaml", "layer": 4},
    "BRD": {"template": "BRD-MVP-TEMPLATE.md", "schema": "BRD_SCHEMA.yaml", "layer": 1},
    "CTR": {"template": "CTR-MVP-TEMPLATE.md", "schema": "CTR_SCHEMA.yaml", "layer": 9},
    "EARS": {"template": "EARS-MVP-TEMPLATE.md", "schema": "EARS_SCHEMA.yaml", "layer": 3},
    "IMPL": {"template": "IMPL-MVP-TEMPLATE.md", "schema": "IMPL_SCHEMA.yaml", "layer": 8},
    "PRD": {"template": "PRD-MVP-TEMPLATE.md", "schema": "PRD_SCHEMA.yaml", "layer": 2},
    "REQ": {"template": "REQ-MVP-TEMPLATE.md", "schema": "REQ_SCHEMA.yaml", "layer": 7},
    "SPEC": {"template": "SPEC-MVP-TEMPLATE.yaml", "schema": "SPEC_SCHEMA.yaml", "layer": 10},
    "SYS": {"template": "SYS-MVP-TEMPLATE.md", "schema": "SYS_SCHEMA.yaml", "layer": 6},
    "TASKS": {"template": "TASKS-MVP-TEMPLATE.md", "schema": "TASKS_SCHEMA.yaml", "layer": 11},
}


def find_ai_dev_flow_dir() -> Path:
    """Locate the framework root flexibly without hardcoding repository names.

    Resolution order:
    1) Environment variable AI_DEV_FLOW_ROOT, if set and valid
    2) Walk up from this script's directory to find a directory containing key artifact folders
    3) Current working directory (and its parents)
    """
    # 1) Environment override
    env = Path(os.environ.get("AI_DEV_FLOW_ROOT", "")) if "AI_DEV_FLOW_ROOT" in os.environ else None
    if env and env.exists() and (env / "PRD").exists():
        return env.resolve()

    sentinels = {"BRD", "PRD", "EARS", "BDD", "ADR", "SYS", "REQ", "CTR", "SPEC", "TASKS"}

    def has_sentinels(p: Path) -> bool:
        try:
            return all((p / s).exists() for s in sentinels)
        except Exception:
            return False

    # 2) Walk up from script directory
    here = Path(__file__).resolve()
    for candidate in [here.parent, here.parent.parent, here.parent.parent.parent]:
        if has_sentinels(candidate):
            return candidate

    # 3) Walk up from CWD
    cwd = Path.cwd().resolve()
    for candidate in [cwd, cwd.parent, cwd.parent.parent]:
        if has_sentinels(candidate):
            return candidate

    raise FileNotFoundError(
        "Could not locate framework root. Set AI_DEV_FLOW_ROOT or run from within the repository.")


def extract_yaml_frontmatter(content: str) -> Optional[Dict]:
    """Extract YAML frontmatter from markdown file."""
    # Use search instead of match to handle files with comment headers before frontmatter
    match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return None
    return None


def extract_schema_version_from_template(template_path: Path) -> Optional[str]:
    """Extract schema_version from template file."""
    try:
        content = template_path.read_text(encoding='utf-8')

        # For .feature files, look for comment-based schema version
        if template_path.suffix == '.feature':
            match = re.search(r'#\s*SCHEMA_VERSION:\s*(\d+\.\d+)', content)
            if match:
                return match.group(1)
            return None

        # For .yaml files (like SPEC-MVP-TEMPLATE.yaml), look for comment or field
        if template_path.suffix == '.yaml':
            match = re.search(r'#\s*SCHEMA_VERSION:\s*(\d+\.\d+)', content)
            if match:
                return match.group(1)
            # Also try parsing as YAML
            try:
                data = yaml.safe_load(content)
                if isinstance(data, dict) and 'metadata' in data:
                    return data.get('metadata', {}).get('schema_version')
            except yaml.YAMLError:
                pass
            return None

        # For .md files, extract from YAML frontmatter
        frontmatter = extract_yaml_frontmatter(content)
        if frontmatter:
            custom_fields = frontmatter.get('custom_fields', {})
            return custom_fields.get('schema_version')

        return None
    except Exception as e:
        return None


def extract_schema_version_from_schema(schema_path: Path) -> Optional[str]:
    """Extract schema_version from schema file."""
    try:
        content = schema_path.read_text(encoding='utf-8')
        data = yaml.safe_load(content)
        if isinstance(data, dict):
            return data.get('schema_version')
        return None
    except Exception:
        return None


def check_artifact_sync(artifact_type: str, base_dir: Path) -> SyncResult:
    """Check if template and schema versions are synchronized for an artifact type."""
    config = ARTIFACT_TYPES[artifact_type]
    artifact_dir = base_dir / artifact_type

    template_path = artifact_dir / config["template"]
    schema_filename = config["schema"]

    # Check if template exists
    if not template_path.exists():
        return SyncResult(
            artifact_type=artifact_type,
            template_path=template_path,
            schema_path=None,
            template_version=None,
            schema_version=None,
            is_synced=False,
            error=f"Template not found: {template_path}"
        )

    # BRD has no schema (Layer 1 entry point)
    if schema_filename is None:
        template_version = extract_schema_version_from_template(template_path)
        # For BRD, schema_reference should be "none" and that's valid
        if template_version == "n/a":
            return SyncResult(
                artifact_type=artifact_type,
                template_path=template_path,
                schema_path=None,
                template_version=template_version,
                schema_version=None,
                is_synced=True,
                error=None
            )
        return SyncResult(
            artifact_type=artifact_type,
            template_path=template_path,
            schema_path=None,
            template_version=template_version,
            schema_version=None,
            is_synced=template_version == "n/a",
            error="BRD has no schema - template should have schema_version: n/a" if template_version != "n/a" else None
        )

    schema_path = artifact_dir / schema_filename

    # Check if schema exists
    if not schema_path.exists():
        return SyncResult(
            artifact_type=artifact_type,
            template_path=template_path,
            schema_path=schema_path,
            template_version=None,
            schema_version=None,
            is_synced=False,
            error=f"Schema not found: {schema_path}"
        )

    # Extract versions
    template_version = extract_schema_version_from_template(template_path)
    schema_version = extract_schema_version_from_schema(schema_path)

    # Check synchronization
    is_synced = template_version == schema_version
    error = None

    if template_version is None:
        error = "Template missing schema_version field"
        is_synced = False
    elif schema_version is None:
        error = "Schema missing schema_version field"
        is_synced = False
    elif not is_synced:
        error = f"Version mismatch: template={template_version}, schema={schema_version}"

    return SyncResult(
        artifact_type=artifact_type,
        template_path=template_path,
        schema_path=schema_path,
        template_version=template_version,
        schema_version=schema_version,
        is_synced=is_synced,
        error=error
    )


def print_result(result: SyncResult, verbose: bool = False):
    """Print sync check result."""
    status = "✅" if result.is_synced else "❌"

    if result.is_synced:
        if verbose:
            print(f"{status} {result.artifact_type}: v{result.template_version or 'n/a'} (synced)")
        else:
            print(f"{status} {result.artifact_type}")
    else:
        print(f"{status} {result.artifact_type}: {result.error}")
        if verbose:
            print(f"   Template: {result.template_path}")
            print(f"   Template version: {result.template_version}")
            if result.schema_path:
                print(f"   Schema: {result.schema_path}")
                print(f"   Schema version: {result.schema_version}")


def main():
    """Main entry point."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    fix_mode = "--fix" in sys.argv

    try:
        base_dir = find_ai_dev_flow_dir()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Checking schema-template sync in: {base_dir}")
    print("=" * 60)

    results: List[SyncResult] = []

    for artifact_type in sorted(ARTIFACT_TYPES.keys(), key=lambda x: ARTIFACT_TYPES[x]["layer"]):
        result = check_artifact_sync(artifact_type, base_dir)
        results.append(result)
        print_result(result, verbose)

    # Summary
    print("=" * 60)
    synced_count = sum(1 for r in results if r.is_synced)
    total_count = len(results)

    if synced_count == total_count:
        print(f"✅ All {total_count} artifact types are synchronized")
        sys.exit(0)
    else:
        print(f"❌ {synced_count}/{total_count} artifact types are synchronized")
        print(f"   {total_count - synced_count} need attention")
        sys.exit(1)


if __name__ == "__main__":
    main()
