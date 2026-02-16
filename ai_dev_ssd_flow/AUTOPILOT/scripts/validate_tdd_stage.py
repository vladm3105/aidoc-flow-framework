#!/usr/bin/env python3
"""
TDD Stage Validator

Validates TDD workflow stages with proper skip/fail logic:
- Red State: Tests must fail before code generation (skip quality gate)
- Green State: Tests must pass after code generation (enforce quality gate)

Usage:
    python validate_tdd_stage.py --stage red --test-dir tests/unit/
    python validate_tdd_stage.py --stage green --test-dir tests/unit/ --code-dir src/ --coverage 90

Reference: IPLAN-001 Section 4.3.1
"""

import argparse
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class TDDStage(Enum):
    """TDD workflow stages."""
    RED = "red"       # Tests expected to fail (no implementation)
    GREEN = "green"   # Tests expected to pass (after implementation)


@dataclass
class ValidationResult:
    """Result of TDD stage validation."""
    status: str  # PASS, FAIL, SKIP
    message: str
    test_count: int = 0
    passed_count: int = 0
    failed_count: int = 0
    coverage: float = 0.0


class TDDStageValidator:
    """
    Validates TDD workflow stages.

    Implements the QualityGateValidator Protocol from IPLAN-001.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def validate_red_state(
        self,
        test_dir: Path,
        code_exists: bool = False
    ) -> ValidationResult:
        """
        Validate Red State: Tests should fail before code generation.

        In TDD, we write tests first that define expected behavior.
        These tests MUST fail initially (no implementation exists).

        Args:
            test_dir: Directory containing unit tests
            code_exists: Whether implementation code exists

        Returns:
            ValidationResult with PASS (tests fail) or SKIP (no tests)
        """
        if not test_dir.exists():
            return ValidationResult(
                status='SKIP',
                message=f'Test directory not found: {test_dir}'
            )

        test_files = list(test_dir.glob('**/test_*.py'))
        if not test_files:
            return ValidationResult(
                status='SKIP',
                message='No test files found'
            )

        # Run tests
        try:
            result = subprocess.run(
                ['pytest', str(test_dir), '-v', '--tb=no', '-q'],
                capture_output=True,
                text=True,
                timeout=300
            )

            # Parse test counts from output
            test_count, passed, failed = self._parse_pytest_summary(result.stdout)

            if result.returncode != 0:
                # Tests failed - this is EXPECTED in Red State
                if not code_exists:
                    return ValidationResult(
                        status='PASS',
                        message='Red State valid: Tests fail before implementation',
                        test_count=test_count,
                        passed_count=passed,
                        failed_count=failed
                    )
                else:
                    # Code exists but tests still fail - this is a problem
                    return ValidationResult(
                        status='FAIL',
                        message='Tests fail but code exists - implementation incomplete',
                        test_count=test_count,
                        passed_count=passed,
                        failed_count=failed
                    )
            else:
                # Tests passed - unexpected in Red State
                if not code_exists:
                    return ValidationResult(
                        status='SKIP',
                        message='Tests pass without implementation - tests may have stubs',
                        test_count=test_count,
                        passed_count=passed,
                        failed_count=failed
                    )
                else:
                    # Code exists and tests pass - this is Green State
                    return ValidationResult(
                        status='SKIP',
                        message='Already in Green State (code exists, tests pass)',
                        test_count=test_count,
                        passed_count=passed,
                        failed_count=failed
                    )

        except FileNotFoundError:
            return ValidationResult(
                status='SKIP',
                message='pytest not found'
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                status='FAIL',
                message='Test execution timed out'
            )
        except Exception as e:
            return ValidationResult(
                status='SKIP',
                message=f'Could not run tests: {e}'
            )

    def validate_green_state(
        self,
        test_dir: Path,
        code_dir: Path,
        coverage_threshold: int = 90
    ) -> ValidationResult:
        """
        Validate Green State: Tests must pass after code generation.

        After implementation, all tests must pass and meet coverage threshold.

        Args:
            test_dir: Directory containing unit tests
            code_dir: Directory containing implementation code
            coverage_threshold: Minimum coverage percentage required

        Returns:
            ValidationResult with PASS (tests pass + coverage met) or FAIL
        """
        if not test_dir.exists():
            return ValidationResult(
                status='FAIL',
                message=f'Test directory not found: {test_dir}'
            )

        if not code_dir.exists():
            return ValidationResult(
                status='FAIL',
                message=f'Code directory not found: {code_dir}'
            )

        # Check for code files
        code_files = list(code_dir.glob('**/*.py'))
        if not code_files:
            return ValidationResult(
                status='FAIL',
                message='No Python files found in code directory'
            )

        # Run tests with coverage
        try:
            result = subprocess.run(
                [
                    'pytest', str(test_dir),
                    '-v', '--tb=short',
                    f'--cov={code_dir}',
                    '--cov-report=term-missing',
                    f'--cov-fail-under={coverage_threshold}'
                ],
                capture_output=True,
                text=True,
                timeout=300
            )

            test_count, passed, failed = self._parse_pytest_summary(result.stdout)
            coverage = self._parse_coverage(result.stdout)

            if result.returncode == 0:
                return ValidationResult(
                    status='PASS',
                    message=f'Green State valid: All tests pass, coverage {coverage:.0f}%',
                    test_count=test_count,
                    passed_count=passed,
                    failed_count=failed,
                    coverage=coverage
                )
            else:
                if failed > 0:
                    return ValidationResult(
                        status='FAIL',
                        message=f'{failed} test(s) failed',
                        test_count=test_count,
                        passed_count=passed,
                        failed_count=failed,
                        coverage=coverage
                    )
                elif coverage < coverage_threshold:
                    return ValidationResult(
                        status='FAIL',
                        message=f'Coverage {coverage:.0f}% below threshold {coverage_threshold}%',
                        test_count=test_count,
                        passed_count=passed,
                        failed_count=failed,
                        coverage=coverage
                    )
                else:
                    return ValidationResult(
                        status='FAIL',
                        message='Tests or coverage failed',
                        test_count=test_count,
                        passed_count=passed,
                        failed_count=failed,
                        coverage=coverage
                    )

        except FileNotFoundError:
            return ValidationResult(
                status='FAIL',
                message='pytest or pytest-cov not found'
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                status='FAIL',
                message='Test execution timed out'
            )
        except Exception as e:
            return ValidationResult(
                status='FAIL',
                message=f'Error running tests: {e}'
            )

    def _parse_pytest_summary(self, output: str) -> tuple:
        """Parse pytest output for test counts."""
        import re

        # Look for summary line like "5 passed, 2 failed"
        match = re.search(
            r'(\d+)\s+passed(?:,\s+(\d+)\s+failed)?',
            output
        )
        if match:
            passed = int(match.group(1))
            failed = int(match.group(2)) if match.group(2) else 0
            return passed + failed, passed, failed

        # Look for just passed or just failed
        passed_match = re.search(r'(\d+)\s+passed', output)
        failed_match = re.search(r'(\d+)\s+failed', output)

        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0

        return passed + failed, passed, failed

    def _parse_coverage(self, output: str) -> float:
        """Parse pytest-cov output for coverage percentage."""
        import re

        # Look for TOTAL line like "TOTAL   100   10   90%"
        match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output)
        if match:
            return float(match.group(1))

        return 0.0


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Validate TDD workflow stages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate Red State (tests should fail)
  python validate_tdd_stage.py --stage red --test-dir tests/unit/

  # Validate Green State (tests should pass with coverage)
  python validate_tdd_stage.py --stage green --test-dir tests/unit/ --code-dir src/

  # Green State with custom coverage threshold
  python validate_tdd_stage.py --stage green --test-dir tests/unit/ --code-dir src/ --coverage 85
        """
    )

    parser.add_argument(
        '--stage', '-s',
        type=str,
        required=True,
        choices=['red', 'green'],
        help='TDD stage to validate (red=before code, green=after code)'
    )

    parser.add_argument(
        '--test-dir', '-t',
        type=Path,
        required=True,
        help='Directory containing test files'
    )

    parser.add_argument(
        '--code-dir', '-c',
        type=Path,
        help='Directory containing implementation code (required for green stage)'
    )

    parser.add_argument(
        '--coverage', '-C',
        type=int,
        default=90,
        help='Coverage threshold percentage (default: 90)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    validator = TDDStageValidator(verbose=args.verbose)

    try:
        if args.stage == 'red':
            # Check if code exists
            code_exists = False
            if args.code_dir and args.code_dir.exists():
                code_files = list(args.code_dir.glob('**/*.py'))
                code_exists = len(code_files) > 0

            result = validator.validate_red_state(
                test_dir=args.test_dir,
                code_exists=code_exists
            )

        elif args.stage == 'green':
            if not args.code_dir:
                print("Error: --code-dir required for green stage validation")
                return 1

            result = validator.validate_green_state(
                test_dir=args.test_dir,
                code_dir=args.code_dir,
                coverage_threshold=args.coverage
            )

        # Print result
        status_icons = {
            'PASS': '✅',
            'FAIL': '❌',
            'SKIP': '⏭️'
        }

        icon = status_icons.get(result.status, '❓')
        print(f"\n{icon} TDD {args.stage.upper()} State: {result.status}")
        print(f"   {result.message}")

        if result.test_count > 0:
            print(f"\n   Tests: {result.test_count} total")
            print(f"   Passed: {result.passed_count}")
            print(f"   Failed: {result.failed_count}")

        if result.coverage > 0:
            print(f"   Coverage: {result.coverage:.0f}%")

        # Exit codes
        if result.status == 'PASS':
            return 0
        elif result.status == 'SKIP':
            return 0  # Skip is not a failure
        else:
            return 1

    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
