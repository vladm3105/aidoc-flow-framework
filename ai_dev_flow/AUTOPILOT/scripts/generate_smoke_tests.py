#!/usr/bin/env python3
"""
Smoke Test Generator

Generates smoke tests from EARS, BDD, and REQ artifacts.
Part of Phase 3: Native TDD Support in MVP Autopilot.

Smoke tests validate:
- Critical user paths work after deployment
- Core functionality is accessible
- System is responsive and healthy
- No obvious regressions

Usage:
    python generate_smoke_tests.py --ears-dir ai_dev_flow/03_EARS/ --output tests/smoke/
    python generate_smoke_tests.py --bdd-dir ai_dev_flow/04_BDD/ --output tests/smoke/

Reference: IPLAN-001 Section 4.3.5
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class SmokeTestCase:
    """Represents a smoke test case."""
    test_id: str
    name: str
    description: str
    source_artifact: str
    source_type: str  # EARS, BDD, REQ
    priority: str = "P1"  # Critical smoke tests
    timeout: int = 30  # seconds
    rollback_on_failure: bool = True
    preconditions: list = field(default_factory=list)
    steps: list = field(default_factory=list)
    expected_outcome: str = ""


@dataclass
class GenerationResult:
    """Result of test generation."""
    files_generated: int
    tests_generated: int
    artifacts_processed: int
    errors: list


class SmokeTestGenerator:
    """
    Generates smoke tests from EARS/BDD/REQ artifacts.

    Smoke tests are quick, critical-path tests that validate
    system health after deployment.
    """

    # Test template for pytest smoke tests
    TEST_TEMPLATE = '''"""
Smoke Tests: {module_name}

Generated from: {source_artifacts}
Generated: {timestamp}

Purpose: Validate critical functionality after deployment.
Timeout: {timeout}s per test
Rollback: Enabled on failure

Traceability:
@ears: {ears_ref}
@bdd: {bdd_ref}
@req: {req_ref}
"""

import pytest
from typing import Any

# Smoke test markers
pytestmark = [
    pytest.mark.smoke,
    pytest.mark.critical,
    pytest.mark.timeout({timeout}),
]


class Test{class_name}Smoke:
    """Smoke tests for {description}."""

    @pytest.fixture(autouse=True)
    def setup_smoke_test(self):
        """Setup for smoke tests - minimal, fast initialization."""
        # TODO: Add minimal test setup
        yield
        # Cleanup if needed

{test_methods}


def run_smoke_tests_with_rollback(deployment_id: str = None):
    """
    Run smoke tests with automatic rollback on failure.

    This function can be called from deployment scripts.
    Returns True if all smoke tests pass, False otherwise.
    """
    import subprocess

    result = subprocess.run(
        ['pytest', __file__, '-v', '--tb=short', '-x'],  # -x stops on first failure
        capture_output=True,
        text=True,
        timeout=300  # 5 minute total timeout
    )

    if result.returncode != 0:
        print("SMOKE TESTS FAILED - Triggering rollback")
        if deployment_id:
            # TODO: Implement rollback logic
            print(f"Rolling back deployment: {{deployment_id}}")
        return False

    print("SMOKE TESTS PASSED")
    return True


if __name__ == '__main__':
    import sys
    success = run_smoke_tests_with_rollback()
    sys.exit(0 if success else 1)
'''

    TEST_METHOD_TEMPLATE = '''
    def test_{method_name}(self):
        """
        Smoke Test: {description}

        Source: {source}
        Priority: {priority}
        Timeout: {timeout}s

        Steps:
{steps}

        Expected: {expected}
        """
        # Arrange
        # TODO: Minimal setup for smoke test

        # Act
        # TODO: Execute critical path

        # Assert
        # TODO: Verify system is responsive
        raise NotImplementedError("Smoke test not yet implemented")
'''

    def __init__(self, verbose: bool = False, timeout: int = 30):
        self.verbose = verbose
        self.default_timeout = timeout

    def generate_from_ears(
        self,
        ears_dir: Path,
        output_dir: Path
    ) -> GenerationResult:
        """
        Generate smoke tests from EARS (Requirements) files.

        EARS requirements with WHEN-THE-SHALL syntax map to smoke tests.
        """
        result = GenerationResult(
            files_generated=0,
            tests_generated=0,
            artifacts_processed=0,
            errors=[]
        )

        if not ears_dir.exists():
            result.errors.append(f"EARS directory not found: {ears_dir}")
            return result

        output_dir.mkdir(parents=True, exist_ok=True)

        # Find EARS markdown files
        ears_files = list(ears_dir.glob('**/*.md'))

        for ears_file in ears_files:
            try:
                test_cases = self._parse_ears_file(ears_file)
                if test_cases:
                    test_file = self._generate_test_file(
                        test_cases,
                        output_dir,
                        source_type='EARS'
                    )
                    if test_file:
                        result.files_generated += 1
                        result.tests_generated += len(test_cases)
                result.artifacts_processed += 1
            except Exception as e:
                result.errors.append(f"Error processing {ears_file}: {e}")

        return result

    def generate_from_bdd(
        self,
        bdd_dir: Path,
        output_dir: Path
    ) -> GenerationResult:
        """
        Generate smoke tests from BDD (Gherkin) feature files.

        Critical scenarios become smoke tests.
        """
        result = GenerationResult(
            files_generated=0,
            tests_generated=0,
            artifacts_processed=0,
            errors=[]
        )

        if not bdd_dir.exists():
            result.errors.append(f"BDD directory not found: {bdd_dir}")
            return result

        output_dir.mkdir(parents=True, exist_ok=True)

        # Find BDD feature files
        bdd_files = list(bdd_dir.glob('**/*.feature'))

        for bdd_file in bdd_files:
            try:
                test_cases = self._parse_bdd_file(bdd_file)
                if test_cases:
                    test_file = self._generate_test_file(
                        test_cases,
                        output_dir,
                        source_type='BDD'
                    )
                    if test_file:
                        result.files_generated += 1
                        result.tests_generated += len(test_cases)
                result.artifacts_processed += 1
            except Exception as e:
                result.errors.append(f"Error processing {bdd_file}: {e}")

        return result

    def generate_from_req(
        self,
        req_dir: Path,
        output_dir: Path
    ) -> GenerationResult:
        """
        Generate smoke tests from REQ (Requirements) files.

        P0/P1 requirements become smoke tests.
        """
        result = GenerationResult(
            files_generated=0,
            tests_generated=0,
            artifacts_processed=0,
            errors=[]
        )

        if not req_dir.exists():
            result.errors.append(f"REQ directory not found: {req_dir}")
            return result

        output_dir.mkdir(parents=True, exist_ok=True)

        # Find REQ markdown files
        req_files = list(req_dir.glob('**/*.md'))

        for req_file in req_files:
            try:
                test_cases = self._parse_req_file(req_file)
                if test_cases:
                    test_file = self._generate_test_file(
                        test_cases,
                        output_dir,
                        source_type='REQ'
                    )
                    if test_file:
                        result.files_generated += 1
                        result.tests_generated += len(test_cases)
                result.artifacts_processed += 1
            except Exception as e:
                result.errors.append(f"Error processing {req_file}: {e}")

        return result

    def _parse_ears_file(self, ears_file: Path) -> list[SmokeTestCase]:
        """Parse EARS file to extract smoke test cases."""
        content = ears_file.read_text(encoding='utf-8')
        test_cases = []

        ears_id = ears_file.stem

        # Find EARS requirements with WHEN-THE-SHALL pattern
        # Pattern: WHEN <trigger> THE <system> SHALL <action> [WITHIN <time>]
        ears_pattern = re.compile(
            r'(?:####?\s*)?(EARS[.\d-]+).*?\n.*?'
            r'WHEN\s+(.+?)\s+'
            r'THE\s+(.+?)\s+'
            r'SHALL\s+(.+?)(?:\s+WITHIN\s+(.+?))?(?:\n|$)',
            re.IGNORECASE | re.DOTALL
        )

        for match in ears_pattern.finditer(content):
            req_id = match.group(1)
            trigger = match.group(2).strip()
            system = match.group(3).strip()
            action = match.group(4).strip()
            timeout_str = match.group(5)

            # Parse timeout if specified
            timeout = self.default_timeout
            if timeout_str:
                timeout_match = re.search(r'(\d+)\s*(s|sec|second|ms|minute|min)', timeout_str, re.I)
                if timeout_match:
                    val = int(timeout_match.group(1))
                    unit = timeout_match.group(2).lower()
                    if 'min' in unit:
                        timeout = val * 60
                    elif 'ms' in unit:
                        timeout = max(1, val // 1000)
                    else:
                        timeout = val

            test_cases.append(SmokeTestCase(
                test_id=f"STEST-{req_id}",
                name=self._slugify(f"{req_id}_{action[:30]}"),
                description=f"When {trigger}, the system shall {action}",
                source_artifact=str(ears_file),
                source_type='EARS',
                timeout=timeout,
                steps=[
                    f"1. Trigger: {trigger}",
                    f"2. System: {system}",
                    f"3. Action: {action}"
                ],
                expected_outcome=action
            ))

        return test_cases

    def _parse_bdd_file(self, bdd_file: Path) -> list[SmokeTestCase]:
        """Parse BDD feature file to extract smoke test cases."""
        content = bdd_file.read_text(encoding='utf-8')
        test_cases = []

        bdd_id = bdd_file.stem

        # Find scenarios (prioritize @critical or @smoke tagged)
        scenario_pattern = re.compile(
            r'(?:@(\w+)\s+)*'
            r'Scenario(?:\s+Outline)?:\s*(.+?)\n'
            r'(.*?)(?=\n\s*(?:Scenario|@|$))',
            re.IGNORECASE | re.DOTALL
        )

        scenario_num = 0
        for match in scenario_pattern.finditer(content):
            tags = match.group(1) or ''
            scenario_name = match.group(2).strip()
            scenario_body = match.group(3).strip()
            scenario_num += 1

            # Only include scenarios tagged @smoke or @critical, or first few scenarios
            is_critical = any(tag in tags.lower() for tag in ['smoke', 'critical', 'p0', 'p1'])
            if not is_critical and scenario_num > 3:
                continue

            # Extract Given-When-Then steps
            steps = []
            for line in scenario_body.split('\n'):
                line = line.strip()
                if line.startswith(('Given', 'When', 'Then', 'And', 'But')):
                    steps.append(line)

            # Extract expected outcome from Then clauses
            then_steps = [s for s in steps if s.startswith(('Then', 'And')) and 'Then' in scenario_body[:scenario_body.find(s) if s in scenario_body else 0]]
            expected = '; '.join(then_steps) if then_steps else 'System responds correctly'

            test_cases.append(SmokeTestCase(
                test_id=f"STEST-{bdd_id}-{scenario_num:02d}",
                name=self._slugify(scenario_name),
                description=scenario_name,
                source_artifact=str(bdd_file),
                source_type='BDD',
                priority='P0' if is_critical else 'P1',
                steps=[f"{i+1}. {s}" for i, s in enumerate(steps)],
                expected_outcome=expected
            ))

        return test_cases

    def _parse_req_file(self, req_file: Path) -> list[SmokeTestCase]:
        """Parse REQ file to extract smoke test cases."""
        content = req_file.read_text(encoding='utf-8')
        test_cases = []

        req_id = req_file.stem

        # Find P0 or P1 priority requirements
        # Look for Priority: P0 or Priority: P1 sections
        req_pattern = re.compile(
            r'(?:####?\s*)?(REQ[.\d-]+).*?\n'
            r'(?:.*?Priority:\s*(P[01]))?'
            r'.*?(?:shall|must|will)\s+(.+?)(?:\n|$)',
            re.IGNORECASE | re.DOTALL
        )

        for match in req_pattern.finditer(content):
            rid = match.group(1)
            priority = match.group(2) or 'P1'
            requirement = match.group(3).strip()

            # Only include P0 and P1 requirements for smoke tests
            if priority not in ['P0', 'P1']:
                continue

            test_cases.append(SmokeTestCase(
                test_id=f"STEST-{rid}",
                name=self._slugify(f"{rid}_{requirement[:30]}"),
                description=f"Verify: {requirement}",
                source_artifact=str(req_file),
                source_type='REQ',
                priority=priority,
                expected_outcome=requirement
            ))

        return test_cases

    def _generate_test_file(
        self,
        test_cases: list[SmokeTestCase],
        output_dir: Path,
        source_type: str
    ) -> Optional[Path]:
        """Generate pytest smoke test file from test cases."""
        if not test_cases:
            return None

        from datetime import datetime

        # Determine module name from first test case
        first_case = test_cases[0]
        source_path = Path(first_case.source_artifact)
        module_name = self._slugify(source_path.stem)

        # Generate test methods
        test_methods = []
        for tc in test_cases:
            steps_formatted = '\n'.join(f"        #   {s}" for s in tc.steps) if tc.steps else "        #   1. Execute test"
            method = self.TEST_METHOD_TEMPLATE.format(
                method_name=tc.name.replace('test_', ''),
                description=tc.description,
                source=tc.source_artifact,
                priority=tc.priority,
                timeout=tc.timeout,
                steps=steps_formatted,
                expected=tc.expected_outcome or 'System responds correctly'
            )
            test_methods.append(method)

        # Determine traceability refs
        ears_ref = source_path.stem if source_type == 'EARS' else 'PENDING'
        bdd_ref = source_path.stem if source_type == 'BDD' else 'PENDING'
        req_ref = source_path.stem if source_type == 'REQ' else 'PENDING'

        # Calculate timeout (max of all test timeouts)
        max_timeout = max(tc.timeout for tc in test_cases)

        # Generate full test file
        class_name = ''.join(word.title() for word in module_name.split('_'))
        test_content = self.TEST_TEMPLATE.format(
            module_name=module_name,
            source_artifacts=first_case.source_artifact,
            timestamp=datetime.now().isoformat(),
            timeout=max_timeout,
            ears_ref=ears_ref,
            bdd_ref=bdd_ref,
            req_ref=req_ref,
            class_name=class_name,
            description=first_case.description,
            test_methods=''.join(test_methods)
        )

        # Write file
        output_file = output_dir / f"test_{module_name}_smoke.py"
        output_file.write_text(test_content, encoding='utf-8')

        if self.verbose:
            print(f"Generated: {output_file} ({len(test_cases)} tests)")

        return output_file

    def _slugify(self, text: str) -> str:
        """Convert text to valid Python identifier."""
        if not text:
            return 'unknown'
        slug = re.sub(r'[^a-z0-9]+', '_', text.lower())
        slug = slug.strip('_')
        # Ensure it doesn't start with a number
        if slug and slug[0].isdigit():
            slug = 'n_' + slug
        # Truncate if too long
        if len(slug) > 50:
            slug = slug[:50].rstrip('_')
        return slug or 'unknown'


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate smoke tests from EARS/BDD/REQ artifacts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from EARS files
  python generate_smoke_tests.py --ears-dir ai_dev_flow/03_EARS/ --output tests/smoke/

  # Generate from BDD feature files
  python generate_smoke_tests.py --bdd-dir ai_dev_flow/04_BDD/ --output tests/smoke/

  # Generate from all sources
  python generate_smoke_tests.py \\
    --ears-dir ai_dev_flow/03_EARS/ \\
    --bdd-dir ai_dev_flow/04_BDD/ \\
    --req-dir ai_dev_flow/07_REQ/ \\
    --output tests/smoke/

  # With custom timeout
  python generate_smoke_tests.py --bdd-dir ai_dev_flow/04_BDD/ --output tests/smoke/ --timeout 60
        """
    )

    parser.add_argument(
        '--ears-dir',
        type=Path,
        help='Directory containing EARS files'
    )

    parser.add_argument(
        '--bdd-dir',
        type=Path,
        help='Directory containing BDD feature files'
    )

    parser.add_argument(
        '--req-dir',
        type=Path,
        help='Directory containing REQ files'
    )

    parser.add_argument(
        '--output', '-o',
        type=Path,
        required=True,
        help='Output directory for generated tests'
    )

    parser.add_argument(
        '--timeout', '-t',
        type=int,
        default=30,
        help='Default timeout per test in seconds (default: 30)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    if not any([args.ears_dir, args.bdd_dir, args.req_dir]):
        print("Error: At least one source directory required (--ears-dir, --bdd-dir, or --req-dir)")
        return 1

    generator = SmokeTestGenerator(verbose=args.verbose, timeout=args.timeout)

    total_files = 0
    total_tests = 0
    total_artifacts = 0
    all_errors = []

    # Generate from EARS
    if args.ears_dir:
        result = generator.generate_from_ears(args.ears_dir, args.output)
        total_files += result.files_generated
        total_tests += result.tests_generated
        total_artifacts += result.artifacts_processed
        all_errors.extend(result.errors)
        if args.verbose:
            print(f"EARS: {result.files_generated} files, {result.tests_generated} tests")

    # Generate from BDD
    if args.bdd_dir:
        result = generator.generate_from_bdd(args.bdd_dir, args.output)
        total_files += result.files_generated
        total_tests += result.tests_generated
        total_artifacts += result.artifacts_processed
        all_errors.extend(result.errors)
        if args.verbose:
            print(f"BDD: {result.files_generated} files, {result.tests_generated} tests")

    # Generate from REQ
    if args.req_dir:
        result = generator.generate_from_req(args.req_dir, args.output)
        total_files += result.files_generated
        total_tests += result.tests_generated
        total_artifacts += result.artifacts_processed
        all_errors.extend(result.errors)
        if args.verbose:
            print(f"REQ: {result.files_generated} files, {result.tests_generated} tests")

    # Summary
    print(f"\nSmoke Test Generation Summary:")
    print(f"  Artifacts processed: {total_artifacts}")
    print(f"  Files generated: {total_files}")
    print(f"  Tests generated: {total_tests}")
    print(f"  Default timeout: {args.timeout}s")

    if all_errors:
        print(f"\nErrors ({len(all_errors)}):")
        for error in all_errors[:5]:
            print(f"  - {error}")
        if len(all_errors) > 5:
            print(f"  ... and {len(all_errors) - 5} more")

    return 0 if not all_errors else 1


if __name__ == '__main__':
    sys.exit(main())
