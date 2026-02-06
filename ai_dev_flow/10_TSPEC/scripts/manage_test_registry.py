#!/usr/bin/env python3
"""
Test Registry Management Script for AI Dev Flow.

Manages the central test registry (test_registry.yaml) including:
- Adding/updating/removing tests
- Syncing from filesystem (pytest collection)
- Validating registry consistency
- Generating statistics and reports

Usage:
    python manage_test_registry.py --init              # Initialize registry
    python manage_test_registry.py --sync              # Sync from filesystem
    python manage_test_registry.py --add UTEST-001 ... # Add test
    python manage_test_registry.py --list              # List all tests
    python manage_test_registry.py --list --type UTEST # List by type
    python manage_test_registry.py --validate          # Validate registry
    python manage_test_registry.py --report            # Generate report
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml

# Paths
SCRIPT_DIR = Path(__file__).parent
TSPEC_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = TSPEC_DIR.parent.parent
REGISTRY_PATH = TSPEC_DIR / "test_registry.yaml"
SCHEMA_PATH = TSPEC_DIR / "test_registry_schema.yaml"
TESTS_DIR = PROJECT_ROOT / "tests"


@dataclass
class TestEntry:
    """Represents a single test in the registry."""

    test_id: str
    test_type: str
    name: str
    file_path: str
    status: str
    created_date: str
    upstream_refs: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    execution_time: Optional[float] = None
    last_result: Optional[str] = None
    last_run_date: Optional[str] = None
    coverage_targets: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary, excluding None values."""
        result = {}
        for k, v in asdict(self).items():
            if v is not None and v != []:
                result[k] = v
        return result


class TestRegistry:
    """Manages the test registry file."""

    def __init__(self, registry_path: Path = REGISTRY_PATH):
        self.registry_path = registry_path
        self.data = self._load()

    def _load(self) -> Dict:
        """Load registry from YAML file."""
        if self.registry_path.exists():
            return yaml.safe_load(self.registry_path.read_text())
        return self._empty_registry()

    def _empty_registry(self) -> Dict:
        """Create empty registry structure."""
        return {
            "version": "1.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "statistics": {
                "total_tests": 0,
                "by_type": {"UTEST": 0, "ITEST": 0, "STEST": 0, "FTEST": 0},
                "by_status": {"active": 0, "deprecated": 0, "skipped": 0},
            },
            "tests": [],
        }

    def save(self) -> None:
        """Save registry to YAML file."""
        self._update_statistics()
        self.data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        self.registry_path.write_text(
            yaml.dump(self.data, default_flow_style=False, sort_keys=False)
        )
        print(f"Registry saved to: {self.registry_path}")

    def _update_statistics(self) -> None:
        """Update statistics based on current tests."""
        tests = self.data.get("tests", [])
        stats = self.data["statistics"]

        stats["total_tests"] = len(tests)

        # Reset counts
        for key in stats["by_type"]:
            stats["by_type"][key] = 0
        for key in stats["by_status"]:
            stats["by_status"][key] = 0

        # Count by type and status
        for test in tests:
            test_type = test.get("test_type", "UTEST")
            status = test.get("status", "active")
            if test_type in stats["by_type"]:
                stats["by_type"][test_type] += 1
            if status in stats["by_status"]:
                stats["by_status"][status] += 1

    def get_test(self, test_id: str) -> Optional[Dict]:
        """Get test by ID."""
        for test in self.data.get("tests", []):
            if test.get("test_id") == test_id:
                return test
        return None

    def add_test(self, entry: TestEntry) -> bool:
        """Add new test to registry."""
        if self.get_test(entry.test_id):
            print(f"Error: Test {entry.test_id} already exists")
            return False

        self.data["tests"].append(entry.to_dict())
        print(f"Added: {entry.test_id} - {entry.name}")
        return True

    def update_test(self, test_id: str, updates: Dict) -> bool:
        """Update existing test."""
        for i, test in enumerate(self.data.get("tests", [])):
            if test.get("test_id") == test_id:
                self.data["tests"][i].update(updates)
                print(f"Updated: {test_id}")
                return True
        print(f"Error: Test {test_id} not found")
        return False

    def remove_test(self, test_id: str, hard_delete: bool = False) -> bool:
        """Remove test (mark deprecated or hard delete)."""
        for i, test in enumerate(self.data.get("tests", [])):
            if test.get("test_id") == test_id:
                if hard_delete:
                    del self.data["tests"][i]
                    print(f"Deleted: {test_id}")
                else:
                    self.data["tests"][i]["status"] = "deprecated"
                    print(f"Deprecated: {test_id}")
                return True
        print(f"Error: Test {test_id} not found")
        return False

    def list_tests(
        self,
        test_type: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict]:
        """List tests with optional filters."""
        tests = self.data.get("tests", [])

        if test_type:
            tests = [t for t in tests if t.get("test_type") == test_type]

        if status:
            tests = [t for t in tests if t.get("status") == status]

        if tags:
            tests = [
                t
                for t in tests
                if any(tag in t.get("tags", []) for tag in tags)
            ]

        return tests

    def sync_from_filesystem(self) -> Dict[str, int]:
        """Discover tests from filesystem using pytest collection."""
        stats = {"discovered": 0, "added": 0, "updated": 0, "errors": 0}

        if not TESTS_DIR.exists():
            print(f"Warning: Tests directory not found: {TESTS_DIR}")
            return stats

        # Use pytest to collect tests
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--collect-only", "-q", str(TESTS_DIR)],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )
            output = result.stdout
        except FileNotFoundError:
            print("Warning: pytest not installed, skipping collection")
            return stats

        # Parse pytest output
        test_type_map = {
            "unit": "UTEST",
            "integration": "ITEST",
            "smoke": "STEST",
            "functional": "FTEST",
        }

        next_ids = {"UTEST": 1, "ITEST": 1, "STEST": 1, "FTEST": 1}

        # Find highest existing IDs
        for test in self.data.get("tests", []):
            test_id = test.get("test_id", "")
            for prefix in next_ids:
                if test_id.startswith(prefix):
                    try:
                        num = int(test_id.split("-")[1])
                        next_ids[prefix] = max(next_ids[prefix], num + 1)
                    except (IndexError, ValueError):
                        pass

        for line in output.split("\n"):
            line = line.strip()
            if "::" not in line or line.startswith("="):
                continue

            stats["discovered"] += 1
            file_path = line.split("::")[0]

            # Determine test type from directory
            test_type = "UTEST"  # default
            for dir_name, type_code in test_type_map.items():
                if f"/{dir_name}/" in file_path or f"\\{dir_name}\\" in file_path:
                    test_type = type_code
                    break

            # Check if test already exists
            existing = None
            for test in self.data.get("tests", []):
                if test.get("file_path") == line:
                    existing = test
                    break

            if existing:
                stats["updated"] += 1
            else:
                # Generate new test ID
                test_id = f"{test_type}-{next_ids[test_type]:03d}"
                next_ids[test_type] += 1

                # Extract test name from nodeid
                parts = line.split("::")
                name = parts[-1] if len(parts) > 1 else parts[0]

                entry = TestEntry(
                    test_id=test_id,
                    test_type=test_type,
                    name=name,
                    file_path=line,
                    status="active",
                    created_date=datetime.now().strftime("%Y-%m-%d"),
                )
                self.add_test(entry)
                stats["added"] += 1

        return stats

    def validate(self) -> List[str]:
        """Validate registry consistency."""
        errors = []

        # Check for duplicate IDs
        ids = [t.get("test_id") for t in self.data.get("tests", [])]
        duplicates = set([x for x in ids if ids.count(x) > 1])
        if duplicates:
            errors.append(f"Duplicate test IDs: {duplicates}")

        # Check for required fields
        required = ["test_id", "test_type", "name", "file_path", "status", "created_date"]
        for i, test in enumerate(self.data.get("tests", [])):
            for field in required:
                if field not in test:
                    errors.append(f"Test at index {i}: missing required field '{field}'")

        # Check for valid test types
        valid_types = ["UTEST", "ITEST", "STEST", "FTEST"]
        for test in self.data.get("tests", []):
            if test.get("test_type") not in valid_types:
                errors.append(
                    f"Test {test.get('test_id')}: invalid test_type '{test.get('test_type')}'"
                )

        # Check for valid statuses
        valid_statuses = ["active", "deprecated", "skipped"]
        for test in self.data.get("tests", []):
            if test.get("status") not in valid_statuses:
                errors.append(
                    f"Test {test.get('test_id')}: invalid status '{test.get('status')}'"
                )

        # Check ID format
        import re

        pattern = r"^(UTEST|ITEST|STEST|FTEST)-[0-9]{3}$"
        for test in self.data.get("tests", []):
            test_id = test.get("test_id", "")
            if not re.match(pattern, test_id):
                errors.append(f"Test {test_id}: ID does not match pattern {pattern}")

        return errors

    def generate_report(self) -> str:
        """Generate markdown report of registry status."""
        stats = self.data["statistics"]
        tests = self.data.get("tests", [])

        lines = [
            "# Test Registry Report",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Registry Version**: {self.data.get('version', '1.0')}",
            "",
            "## Summary",
            "",
            f"| Metric | Count |",
            f"|--------|-------|",
            f"| Total Tests | {stats['total_tests']} |",
            f"| Unit Tests (UTEST) | {stats['by_type']['UTEST']} |",
            f"| Integration Tests (ITEST) | {stats['by_type']['ITEST']} |",
            f"| Smoke Tests (STEST) | {stats['by_type']['STEST']} |",
            f"| Functional Tests (FTEST) | {stats['by_type']['FTEST']} |",
            "",
            "## Status Breakdown",
            "",
            f"| Status | Count |",
            f"|--------|-------|",
            f"| Active | {stats['by_status']['active']} |",
            f"| Deprecated | {stats['by_status']['deprecated']} |",
            f"| Skipped | {stats['by_status']['skipped']} |",
            "",
        ]

        if tests:
            lines.extend(
                [
                    "## Test Catalog",
                    "",
                    "| ID | Type | Name | Status | Last Result |",
                    "|----|------|------|--------|-------------|",
                ]
            )
            for test in tests:
                lines.append(
                    f"| {test.get('test_id')} | {test.get('test_type')} | "
                    f"{test.get('name', '')[:40]} | {test.get('status')} | "
                    f"{test.get('last_result', '-')} |"
                )

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Manage test registry")
    parser.add_argument("--init", action="store_true", help="Initialize registry")
    parser.add_argument("--sync", action="store_true", help="Sync from filesystem")
    parser.add_argument("--add", nargs="+", help="Add test: ID TYPE NAME FILE_PATH")
    parser.add_argument("--update", nargs="+", help="Update test: ID key=value ...")
    parser.add_argument("--remove", type=str, help="Remove test by ID")
    parser.add_argument("--hard-delete", action="store_true", help="Hard delete instead of deprecate")
    parser.add_argument("--list", action="store_true", help="List tests")
    parser.add_argument("--type", type=str, choices=["UTEST", "ITEST", "STEST", "FTEST"])
    parser.add_argument("--status", type=str, choices=["active", "deprecated", "skipped"])
    parser.add_argument("--validate", action="store_true", help="Validate registry")
    parser.add_argument("--report", action="store_true", help="Generate report")
    parser.add_argument("--output", type=str, help="Output file for report")

    args = parser.parse_args()

    registry = TestRegistry()

    if args.init:
        registry.data = registry._empty_registry()
        registry.save()
        print("Registry initialized")
        return 0

    if args.sync:
        stats = registry.sync_from_filesystem()
        registry.save()
        print(f"\nSync complete:")
        print(f"  Discovered: {stats['discovered']}")
        print(f"  Added: {stats['added']}")
        print(f"  Updated: {stats['updated']}")
        return 0

    if args.add:
        if len(args.add) < 4:
            print("Error: --add requires ID TYPE NAME FILE_PATH")
            return 1
        entry = TestEntry(
            test_id=args.add[0],
            test_type=args.add[1],
            name=args.add[2],
            file_path=args.add[3],
            status="active",
            created_date=datetime.now().strftime("%Y-%m-%d"),
        )
        if registry.add_test(entry):
            registry.save()
        return 0

    if args.update:
        if len(args.update) < 2:
            print("Error: --update requires ID and at least one key=value pair")
            return 1
        test_id = args.update[0]
        updates = {}
        for kv in args.update[1:]:
            if "=" in kv:
                key, value = kv.split("=", 1)
                updates[key] = value
        if registry.update_test(test_id, updates):
            registry.save()
        return 0

    if args.remove:
        if registry.remove_test(args.remove, args.hard_delete):
            registry.save()
        return 0

    if args.list:
        tests = registry.list_tests(test_type=args.type, status=args.status)
        if not tests:
            print("No tests found")
        else:
            print(f"\n{'ID':<12} {'Type':<6} {'Status':<10} {'Name'}")
            print("-" * 60)
            for test in tests:
                print(
                    f"{test.get('test_id', ''):<12} "
                    f"{test.get('test_type', ''):<6} "
                    f"{test.get('status', ''):<10} "
                    f"{test.get('name', '')[:35]}"
                )
            print(f"\nTotal: {len(tests)} tests")
        return 0

    if args.validate:
        errors = registry.validate()
        if errors:
            print("Validation errors:")
            for error in errors:
                print(f"  - {error}")
            return 1
        print("Registry is valid")
        return 0

    if args.report:
        report = registry.generate_report()
        if args.output:
            Path(args.output).write_text(report)
            print(f"Report saved to: {args.output}")
        else:
            print(report)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
