#!/usr/bin/env python3
"""
Update Test Traceability Script

Updates PENDING traceability tags in test files with actual file paths
after SPEC and code generation. Part of Phase 2: TDD Awareness in MVP Autopilot.

Usage:
    python update_test_traceability.py --test-dir tests/unit/ --spec-dir ai_dev_flow/09_SPEC/ --code-dir src/
    python update_test_traceability.py --test-dir tests/unit/ --validate-only

Reference: IPLAN-001 Section 4.3.2
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class TagUpdate:
    """Represents a tag update."""
    file_path: Path
    line_number: int
    tag_type: str
    old_value: str
    new_value: str


@dataclass
class UpdateResult:
    """Result of update operation."""
    files_scanned: int
    files_updated: int
    tags_updated: int
    pending_remaining: int
    updates: list[TagUpdate]
    errors: list[str]


class TraceabilityUpdater:
    """
    Updates PENDING traceability tags in test files.

    Implements the TraceabilityUpdater Protocol from IPLAN-001.
    """

    # Pattern to match PENDING tags in docstrings/comments
    PENDING_PATTERN = re.compile(
        r'@(spec|tasks|code|tspec):\s*PENDING\s*(?:#.*)?$',
        re.MULTILINE | re.IGNORECASE
    )

    # Pattern to extract REQ ID from file
    REQ_PATTERN = re.compile(
        r'@req:\s*(REQ[-.\d]+)',
        re.IGNORECASE
    )

    # Pattern to extract component hints
    COMPONENT_PATTERN = re.compile(
        r'test_(\w+)',
        re.IGNORECASE
    )

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def update_test_traceability(
        self,
        test_dir: Path,
        spec_dir: Optional[Path] = None,
        tasks_dir: Optional[Path] = None,
        code_dir: Optional[Path] = None,
        dry_run: bool = False
    ) -> UpdateResult:
        """
        Update PENDING traceability tags with actual file paths.

        Args:
            test_dir: Directory containing test files
            spec_dir: Directory containing SPEC files
            tasks_dir: Directory containing TASKS files
            code_dir: Directory containing source code
            dry_run: If True, don't modify files

        Returns:
            UpdateResult with statistics and details
        """
        result = UpdateResult(
            files_scanned=0,
            files_updated=0,
            tags_updated=0,
            pending_remaining=0,
            updates=[],
            errors=[]
        )

        test_files = list(test_dir.glob('**/*.py'))
        result.files_scanned = len(test_files)

        for test_file in test_files:
            file_updates = self._process_file(
                test_file, spec_dir, tasks_dir, code_dir
            )

            if file_updates:
                result.updates.extend(file_updates)
                result.tags_updated += len(file_updates)

                if not dry_run:
                    self._apply_updates(test_file, file_updates)
                    result.files_updated += 1
                else:
                    result.files_updated += 1  # Count as would-be-updated

        # Count remaining PENDING tags
        if not dry_run:
            result.pending_remaining = self._count_pending_tags(test_dir)
        else:
            # Estimate - don't count since files weren't updated
            result.pending_remaining = self._count_pending_tags(test_dir) - result.tags_updated

        return result

    def _process_file(
        self,
        test_file: Path,
        spec_dir: Optional[Path],
        tasks_dir: Optional[Path],
        code_dir: Optional[Path]
    ) -> list[TagUpdate]:
        """Process a single test file for PENDING tags."""
        updates = []

        try:
            content = test_file.read_text(encoding='utf-8')
        except Exception as e:
            if self.verbose:
                print(f"Error reading {test_file}: {e}")
            return updates

        # Extract context from file
        req_ids = self.REQ_PATTERN.findall(content)
        component_match = self.COMPONENT_PATTERN.search(test_file.stem)
        component_name = component_match.group(1) if component_match else None

        # Find and resolve each PENDING tag
        for match in self.PENDING_PATTERN.finditer(content):
            tag_type = match.group(1).lower()
            line_number = content[:match.start()].count('\n') + 1

            # Resolve the path
            resolved_path = self._resolve_path(
                tag_type, req_ids, component_name,
                spec_dir, tasks_dir, code_dir
            )

            if resolved_path and resolved_path != 'PENDING':
                updates.append(TagUpdate(
                    file_path=test_file,
                    line_number=line_number,
                    tag_type=tag_type,
                    old_value='PENDING',
                    new_value=resolved_path
                ))

        return updates

    def _resolve_path(
        self,
        tag_type: str,
        req_ids: list[str],
        component_name: Optional[str],
        spec_dir: Optional[Path],
        tasks_dir: Optional[Path],
        code_dir: Optional[Path]
    ) -> Optional[str]:
        """Resolve path for a specific tag type."""
        if tag_type == 'spec' and spec_dir:
            return self._find_spec_file(req_ids, component_name, spec_dir)
        elif tag_type == 'tasks' and tasks_dir:
            return self._find_tasks_file(req_ids, component_name, tasks_dir)
        elif tag_type == 'code' and code_dir:
            return self._find_code_file(req_ids, component_name, code_dir)
        elif tag_type == 'tspec':
            # TSPEC is derived from REQ
            if req_ids:
                return self._derive_tspec_id(req_ids[0])
        return None

    def _find_spec_file(
        self,
        req_ids: list[str],
        component_name: Optional[str],
        spec_dir: Path
    ) -> Optional[str]:
        """Find SPEC file matching REQ or component."""
        if not spec_dir.exists():
            return None

        # Try to find by REQ ID
        for req_id in req_ids:
            # Convert REQ.01.10.01 -> patterns
            patterns = self._req_to_patterns(req_id, 'SPEC')
            for pattern in patterns:
                matches = list(spec_dir.glob(f'**/{pattern}'))
                if matches:
                    return str(matches[0].relative_to(spec_dir.parent))

        # Try to find by component name
        if component_name:
            matches = list(spec_dir.glob(f'**/*{component_name}*.yaml'))
            if matches:
                return str(matches[0].relative_to(spec_dir.parent))

        # Return first SPEC file as fallback
        all_specs = list(spec_dir.glob('**/*.yaml'))
        if all_specs:
            return str(all_specs[0].relative_to(spec_dir.parent))

        return None

    def _find_tasks_file(
        self,
        req_ids: list[str],
        component_name: Optional[str],
        tasks_dir: Path
    ) -> Optional[str]:
        """Find TASKS file matching REQ or component."""
        if not tasks_dir.exists():
            return None

        # Try to find by REQ ID
        for req_id in req_ids:
            patterns = self._req_to_patterns(req_id, 'TASKS')
            for pattern in patterns:
                matches = list(tasks_dir.glob(f'**/{pattern}'))
                if matches:
                    return str(matches[0].relative_to(tasks_dir.parent))

        # Try to find by component name
        if component_name:
            matches = list(tasks_dir.glob(f'**/*{component_name}*.md'))
            if matches:
                return str(matches[0].relative_to(tasks_dir.parent))

        return None

    def _find_code_file(
        self,
        req_ids: list[str],
        component_name: Optional[str],
        code_dir: Path
    ) -> Optional[str]:
        """Find source code file matching component."""
        if not code_dir.exists():
            return None

        # Try to find by component name
        if component_name:
            # Look for service/module file
            patterns = [
                f'**/{component_name}.py',
                f'**/{component_name}_service.py',
                f'**/services/{component_name}.py',
                f'**/*{component_name}*.py'
            ]
            for pattern in patterns:
                matches = list(code_dir.glob(pattern))
                if matches:
                    return str(matches[0].relative_to(code_dir.parent))

        # Try to derive from REQ
        for req_id in req_ids:
            service_name = self._req_to_service_name(req_id)
            if service_name:
                matches = list(code_dir.glob(f'**/{service_name}*.py'))
                if matches:
                    return str(matches[0].relative_to(code_dir.parent))

        return None

    def _req_to_patterns(self, req_id: str, artifact_type: str) -> list[str]:
        """Convert REQ ID to file search patterns."""
        patterns = []

        # Extract numeric parts
        match = re.match(r'REQ[-.]?(\d+)(?:[-.](\d+))?(?:[-.](\d+))?', req_id, re.IGNORECASE)
        if match:
            parts = [p for p in match.groups() if p]
            num = parts[0] if parts else '01'

            patterns.extend([
                f'{artifact_type}-{num}*.yaml',
                f'{artifact_type}-{num}*.md',
                f'{artifact_type}_{num}*.yaml',
                f'{artifact_type}_{num}*.md',
            ])

        # Also try with full ID converted
        slug = req_id.replace('.', '_').replace('-', '_').lower()
        patterns.append(f'*{slug}*.yaml')
        patterns.append(f'*{slug}*.md')

        return patterns

    def _req_to_service_name(self, req_id: str) -> Optional[str]:
        """Convert REQ ID to likely service name."""
        # Map known REQ patterns to service names
        # This would typically be configured or derived from REQ file content
        mappings = {
            'REQ.01.10': 'auth',
            'REQ.01.20': 'user',
            'REQ.02': 'api',
        }

        for prefix, service in mappings.items():
            if req_id.startswith(prefix):
                return service

        return None

    def _derive_tspec_id(self, req_id: str) -> str:
        """Derive TSPEC ID from REQ ID."""
        # REQ.01.10.01 -> TSPEC.01.40.01 (40 = Unit Test)
        match = re.match(r'REQ[-.]?(\d+)', req_id, re.IGNORECASE)
        if match:
            num = match.group(1).zfill(2)
            return f'TSPEC.{num}.40.01'
        return f'TSPEC.01.40.01'

    def _apply_updates(self, test_file: Path, updates: list[TagUpdate]) -> None:
        """Apply tag updates to file."""
        content = test_file.read_text(encoding='utf-8')

        for update in updates:
            # Replace PENDING with resolved path
            old_pattern = f'@{update.tag_type}: PENDING'
            new_value = f'@{update.tag_type}: {update.new_value}'
            content = re.sub(
                rf'@{update.tag_type}:\s*PENDING',
                new_value,
                content,
                flags=re.IGNORECASE
            )

        test_file.write_text(content, encoding='utf-8')

        if self.verbose:
            print(f"Updated {test_file.name}: {len(updates)} tag(s)")

    def _count_pending_tags(self, test_dir: Path) -> int:
        """Count remaining PENDING tags in directory."""
        count = 0
        for test_file in test_dir.glob('**/*.py'):
            try:
                content = test_file.read_text(encoding='utf-8')
                count += len(self.PENDING_PATTERN.findall(content))
            except Exception:
                pass
        return count

    def validate_no_pending_tags(self, test_dir: Path) -> bool:
        """
        Verify all PENDING tags are resolved.

        Returns True if no PENDING tags remain.
        """
        pending_files = []

        for test_file in test_dir.glob('**/*.py'):
            try:
                content = test_file.read_text(encoding='utf-8')
                matches = self.PENDING_PATTERN.findall(content)
                if matches:
                    pending_files.append({
                        'file': str(test_file),
                        'pending_tags': list(set(matches))
                    })
            except Exception as e:
                if self.verbose:
                    print(f"Error reading {test_file}: {e}")

        if pending_files:
            if self.verbose:
                print(f"\n{len(pending_files)} file(s) with PENDING tags:")
                for pf in pending_files:
                    print(f"  - {pf['file']}: {pf['pending_tags']}")
            return False
        else:
            if self.verbose:
                print("All PENDING tags resolved")
            return True


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Update PENDING traceability tags in test files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update PENDING tags with resolved paths
  python update_test_traceability.py --test-dir tests/unit/ --spec-dir ai_dev_flow/09_SPEC/ --code-dir src/

  # Dry run (show what would be updated)
  python update_test_traceability.py --test-dir tests/unit/ --spec-dir ai_dev_flow/09_SPEC/ --dry-run

  # Validate no PENDING tags remain
  python update_test_traceability.py --test-dir tests/unit/ --validate-only

  # Update with all directories
  python update_test_traceability.py --test-dir tests/unit/ \\
    --spec-dir ai_dev_flow/09_SPEC/ \\
    --tasks-dir ai_dev_flow/11_TASKS/ \\
    --code-dir src/
        """
    )

    parser.add_argument(
        '--test-dir', '-t',
        type=Path,
        required=True,
        help='Directory containing test files'
    )

    parser.add_argument(
        '--spec-dir', '-s',
        type=Path,
        help='Directory containing SPEC files'
    )

    parser.add_argument(
        '--tasks-dir', '-T',
        type=Path,
        help='Directory containing TASKS files'
    )

    parser.add_argument(
        '--code-dir', '-c',
        type=Path,
        help='Directory containing source code'
    )

    parser.add_argument(
        '--validate-only', '-V',
        action='store_true',
        help='Only validate, do not update'
    )

    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be updated without modifying files'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    updater = TraceabilityUpdater(verbose=args.verbose)

    try:
        if args.validate_only:
            # Validation mode
            valid = updater.validate_no_pending_tags(args.test_dir)
            return 0 if valid else 1

        # Update mode
        result = updater.update_test_traceability(
            test_dir=args.test_dir,
            spec_dir=args.spec_dir,
            tasks_dir=args.tasks_dir,
            code_dir=args.code_dir,
            dry_run=args.dry_run
        )

        # Print summary
        print(f"\nTraceability Update Summary:")
        print(f"  Files scanned: {result.files_scanned}")
        print(f"  Files updated: {result.files_updated}")
        print(f"  Tags updated: {result.tags_updated}")
        print(f"  PENDING remaining: {result.pending_remaining}")

        if args.dry_run:
            print("\n[DRY RUN - No files were modified]")

        if args.verbose and result.updates:
            print(f"\nUpdates:")
            for update in result.updates:
                print(f"  {update.file_path.name}:{update.line_number}")
                print(f"    @{update.tag_type}: PENDING -> {update.new_value}")

        if result.errors:
            print(f"\nErrors:")
            for error in result.errors:
                print(f"  - {error}")

        # Validate after update
        if not args.dry_run and result.pending_remaining == 0:
            print("\n All PENDING tags resolved successfully")
            return 0
        elif result.pending_remaining > 0:
            print(f"\n {result.pending_remaining} PENDING tag(s) could not be resolved")
            return 1

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
