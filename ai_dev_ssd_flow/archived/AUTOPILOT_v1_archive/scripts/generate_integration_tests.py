#!/usr/bin/env python3
"""
Integration Test Generator

Generates integration tests from CTR (Contracts), SYS (System), and SPEC artifacts.
Part of Phase 3: Native TDD Support in MVP Autopilot.

Integration tests validate:
- Component interactions
- API contract compliance
- Database operations
- External service integrations

Usage:
    python generate_integration_tests.py --ctr-dir ai_dev_flow/08_CTR/ --output tests/integration/
    python generate_integration_tests.py --spec-dir ai_dev_flow/09_SPEC/ --sys-dir ai_dev_flow/06_SYS/ --output tests/integration/

Reference: IPLAN-001 Section 4.3.4
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class IntegrationTestCase:
    """Represents an integration test case."""
    test_id: str
    name: str
    description: str
    source_artifact: str
    source_type: str  # CTR, SYS, SPEC
    endpoint: Optional[str] = None
    method: Optional[str] = None
    request_schema: Optional[dict] = None
    response_schema: Optional[dict] = None
    dependencies: list = field(default_factory=list)
    setup_requirements: list = field(default_factory=list)


@dataclass
class GenerationResult:
    """Result of test generation."""
    files_generated: int
    tests_generated: int
    artifacts_processed: int
    errors: list


class IntegrationTestGenerator:
    """
    Generates integration tests from CTR/SYS/SPEC artifacts.

    Implements the integration test generation stage from IPLAN-001.
    """

    # Test template for pytest
    TEST_TEMPLATE = '''"""
Integration Tests: {module_name}

Generated from: {source_artifacts}
Generated: {timestamp}

Traceability:
@ctr: {ctr_ref}
@sys: {sys_ref}
@spec: {spec_ref}
"""

import pytest
from typing import Any, Dict

# Test fixtures would be imported from conftest.py
# from conftest import api_client, database, test_data


class Test{class_name}Integration:
    """Integration tests for {description}."""

{test_methods}


# Pytest markers for integration tests
pytestmark = [
    pytest.mark.integration,
    pytest.mark.slow,
]
'''

    TEST_METHOD_TEMPLATE = '''
    def test_{method_name}(self):
        """
        Test: {description}

        Source: {source}
        Endpoint: {endpoint}
        """
        # Arrange
        # TODO: Set up test data and dependencies

        # Act
        # TODO: Call the integration point
        # result = api_client.{method}("{endpoint}")

        # Assert
        # TODO: Verify integration behavior
        raise NotImplementedError("Integration test not yet implemented")
'''

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def generate_from_ctr(
        self,
        ctr_dir: Path,
        output_dir: Path
    ) -> GenerationResult:
        """
        Generate integration tests from CTR (Contract) files.

        CTR files define API contracts that should be tested.
        """
        result = GenerationResult(
            files_generated=0,
            tests_generated=0,
            artifacts_processed=0,
            errors=[]
        )

        if not ctr_dir.exists():
            result.errors.append(f"CTR directory not found: {ctr_dir}")
            return result

        output_dir.mkdir(parents=True, exist_ok=True)

        # Find CTR YAML files
        ctr_files = list(ctr_dir.glob('**/*.yaml')) + list(ctr_dir.glob('**/*.yml'))

        for ctr_file in ctr_files:
            try:
                test_cases = self._parse_ctr_file(ctr_file)
                if test_cases:
                    test_file = self._generate_test_file(
                        test_cases,
                        output_dir,
                        source_type='CTR'
                    )
                    if test_file:
                        result.files_generated += 1
                        result.tests_generated += len(test_cases)
                result.artifacts_processed += 1
            except Exception as e:
                result.errors.append(f"Error processing {ctr_file}: {e}")

        return result

    def generate_from_spec(
        self,
        spec_dir: Path,
        output_dir: Path
    ) -> GenerationResult:
        """
        Generate integration tests from SPEC files.

        SPEC files define interfaces and behavior that should be tested.
        """
        result = GenerationResult(
            files_generated=0,
            tests_generated=0,
            artifacts_processed=0,
            errors=[]
        )

        if not spec_dir.exists():
            result.errors.append(f"SPEC directory not found: {spec_dir}")
            return result

        output_dir.mkdir(parents=True, exist_ok=True)

        # Find SPEC YAML files
        spec_files = list(spec_dir.glob('**/*.yaml')) + list(spec_dir.glob('**/*.yml'))

        for spec_file in spec_files:
            try:
                test_cases = self._parse_spec_file(spec_file)
                if test_cases:
                    test_file = self._generate_test_file(
                        test_cases,
                        output_dir,
                        source_type='SPEC'
                    )
                    if test_file:
                        result.files_generated += 1
                        result.tests_generated += len(test_cases)
                result.artifacts_processed += 1
            except Exception as e:
                result.errors.append(f"Error processing {spec_file}: {e}")

        return result

    def generate_from_sys(
        self,
        sys_dir: Path,
        output_dir: Path
    ) -> GenerationResult:
        """
        Generate integration tests from SYS (System Requirements) files.

        SYS files define system-level requirements that need integration testing.
        """
        result = GenerationResult(
            files_generated=0,
            tests_generated=0,
            artifacts_processed=0,
            errors=[]
        )

        if not sys_dir.exists():
            result.errors.append(f"SYS directory not found: {sys_dir}")
            return result

        output_dir.mkdir(parents=True, exist_ok=True)

        # Find SYS markdown files
        sys_files = list(sys_dir.glob('**/*.md'))

        for sys_file in sys_files:
            try:
                test_cases = self._parse_sys_file(sys_file)
                if test_cases:
                    test_file = self._generate_test_file(
                        test_cases,
                        output_dir,
                        source_type='SYS'
                    )
                    if test_file:
                        result.files_generated += 1
                        result.tests_generated += len(test_cases)
                result.artifacts_processed += 1
            except Exception as e:
                result.errors.append(f"Error processing {sys_file}: {e}")

        return result

    def _parse_ctr_file(self, ctr_file: Path) -> list[IntegrationTestCase]:
        """Parse CTR file to extract integration test cases."""
        if not yaml:
            return []

        try:
            content = yaml.safe_load(ctr_file.read_text(encoding='utf-8'))
        except Exception:
            return []

        if not content:
            return []

        test_cases = []
        ctr_id = content.get('id', ctr_file.stem)

        # Extract endpoints from CTR
        endpoints = content.get('endpoints', [])
        for i, endpoint in enumerate(endpoints):
            test_cases.append(IntegrationTestCase(
                test_id=f"ITEST-{ctr_id}-{i+1:02d}",
                name=f"test_{endpoint.get('method', 'get').lower()}_{self._slugify(endpoint.get('path', 'unknown'))}",
                description=endpoint.get('description', f"Test {endpoint.get('path', 'endpoint')}"),
                source_artifact=str(ctr_file),
                source_type='CTR',
                endpoint=endpoint.get('path'),
                method=endpoint.get('method', 'GET'),
                request_schema=endpoint.get('request'),
                response_schema=endpoint.get('response')
            ))

        # Extract interfaces from CTR
        interfaces = content.get('interfaces', {})
        for interface_name, interface_def in interfaces.items():
            if isinstance(interface_def, dict):
                test_cases.append(IntegrationTestCase(
                    test_id=f"ITEST-{ctr_id}-{interface_name}",
                    name=f"test_{self._slugify(interface_name)}_contract",
                    description=f"Contract test for {interface_name}",
                    source_artifact=str(ctr_file),
                    source_type='CTR'
                ))

        return test_cases

    def _parse_spec_file(self, spec_file: Path) -> list[IntegrationTestCase]:
        """Parse SPEC file to extract integration test cases."""
        if not yaml:
            return []

        try:
            content = yaml.safe_load(spec_file.read_text(encoding='utf-8'))
        except Exception:
            return []

        if not content:
            return []

        test_cases = []
        spec_id = content.get('id', spec_file.stem)

        # Extract interfaces for integration testing
        interfaces = content.get('interfaces', {})

        # Internal APIs
        internal_apis = interfaces.get('internal_apis', [])
        for i, api in enumerate(internal_apis):
            if isinstance(api, dict):
                test_cases.append(IntegrationTestCase(
                    test_id=f"ITEST-{spec_id}-INT-{i+1:02d}",
                    name=f"test_{self._slugify(api.get('interface', 'api'))}",
                    description=api.get('purpose', 'Internal API integration test'),
                    source_artifact=str(spec_file),
                    source_type='SPEC'
                ))

        # External dependencies
        external_deps = interfaces.get('external_dependencies', [])
        for i, dep in enumerate(external_deps):
            if isinstance(dep, dict):
                test_cases.append(IntegrationTestCase(
                    test_id=f"ITEST-{spec_id}-EXT-{i+1:02d}",
                    name=f"test_{self._slugify(dep.get('name', 'external'))}_integration",
                    description=f"External integration: {dep.get('name', 'unknown')}",
                    source_artifact=str(spec_file),
                    source_type='SPEC',
                    dependencies=[dep.get('name', 'unknown')]
                ))

        return test_cases

    def _parse_sys_file(self, sys_file: Path) -> list[IntegrationTestCase]:
        """Parse SYS file to extract integration test cases."""
        content = sys_file.read_text(encoding='utf-8')
        test_cases = []

        sys_id = sys_file.stem

        # Extract interface requirements from SYS
        # Look for "Interface" or "Integration" sections
        interface_pattern = re.compile(
            r'###?\s+(?:Interface|Integration|External)\s+.*?(?=\n###?|\Z)',
            re.DOTALL | re.IGNORECASE
        )

        matches = interface_pattern.findall(content)
        for i, match in enumerate(matches):
            # Extract requirement IDs from the section
            req_ids = re.findall(r'(FR-\d+|NFR-\d+|IR-\d+)', match)
            for req_id in req_ids:
                test_cases.append(IntegrationTestCase(
                    test_id=f"ITEST-{sys_id}-{req_id}",
                    name=f"test_{self._slugify(req_id)}_integration",
                    description=f"System integration test for {req_id}",
                    source_artifact=str(sys_file),
                    source_type='SYS'
                ))

        return test_cases

    def _generate_test_file(
        self,
        test_cases: list[IntegrationTestCase],
        output_dir: Path,
        source_type: str
    ) -> Optional[Path]:
        """Generate pytest test file from test cases."""
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
            method = self.TEST_METHOD_TEMPLATE.format(
                method_name=tc.name.replace('test_', ''),
                description=tc.description,
                source=tc.source_artifact,
                endpoint=tc.endpoint or 'N/A',
                method=tc.method or 'call'
            )
            test_methods.append(method)

        # Determine traceability refs
        ctr_ref = 'PENDING' if source_type != 'CTR' else source_path.stem
        sys_ref = 'PENDING' if source_type != 'SYS' else source_path.stem
        spec_ref = 'PENDING' if source_type != 'SPEC' else source_path.stem

        # Generate full test file
        class_name = ''.join(word.title() for word in module_name.split('_'))
        test_content = self.TEST_TEMPLATE.format(
            module_name=module_name,
            source_artifacts=first_case.source_artifact,
            timestamp=datetime.now().isoformat(),
            ctr_ref=ctr_ref,
            sys_ref=sys_ref,
            spec_ref=spec_ref,
            class_name=class_name,
            description=first_case.description,
            test_methods=''.join(test_methods)
        )

        # Write file
        output_file = output_dir / f"test_{module_name}_integration.py"
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
        return slug or 'unknown'


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate integration tests from CTR/SYS/SPEC artifacts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from CTR files
  python generate_integration_tests.py --ctr-dir ai_dev_flow/08_CTR/ --output tests/integration/

  # Generate from SPEC files
  python generate_integration_tests.py --spec-dir ai_dev_flow/09_SPEC/ --output tests/integration/

  # Generate from all sources
  python generate_integration_tests.py \\
    --ctr-dir ai_dev_flow/08_CTR/ \\
    --spec-dir ai_dev_flow/09_SPEC/ \\
    --sys-dir ai_dev_flow/06_SYS/ \\
    --output tests/integration/
        """
    )

    parser.add_argument(
        '--ctr-dir',
        type=Path,
        help='Directory containing CTR (Contract) files'
    )

    parser.add_argument(
        '--spec-dir',
        type=Path,
        help='Directory containing SPEC files'
    )

    parser.add_argument(
        '--sys-dir',
        type=Path,
        help='Directory containing SYS (System Requirements) files'
    )

    parser.add_argument(
        '--output', '-o',
        type=Path,
        required=True,
        help='Output directory for generated tests'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    if not any([args.ctr_dir, args.spec_dir, args.sys_dir]):
        print("Error: At least one source directory required (--ctr-dir, --spec-dir, or --sys-dir)")
        return 1

    generator = IntegrationTestGenerator(verbose=args.verbose)

    total_files = 0
    total_tests = 0
    total_artifacts = 0
    all_errors = []

    # Generate from CTR
    if args.ctr_dir:
        result = generator.generate_from_ctr(args.ctr_dir, args.output)
        total_files += result.files_generated
        total_tests += result.tests_generated
        total_artifacts += result.artifacts_processed
        all_errors.extend(result.errors)
        if args.verbose:
            print(f"CTR: {result.files_generated} files, {result.tests_generated} tests")

    # Generate from SPEC
    if args.spec_dir:
        result = generator.generate_from_spec(args.spec_dir, args.output)
        total_files += result.files_generated
        total_tests += result.tests_generated
        total_artifacts += result.artifacts_processed
        all_errors.extend(result.errors)
        if args.verbose:
            print(f"SPEC: {result.files_generated} files, {result.tests_generated} tests")

    # Generate from SYS
    if args.sys_dir:
        result = generator.generate_from_sys(args.sys_dir, args.output)
        total_files += result.files_generated
        total_tests += result.tests_generated
        total_artifacts += result.artifacts_processed
        all_errors.extend(result.errors)
        if args.verbose:
            print(f"SYS: {result.files_generated} files, {result.tests_generated} tests")

    # Summary
    print(f"\nIntegration Test Generation Summary:")
    print(f"  Artifacts processed: {total_artifacts}")
    print(f"  Files generated: {total_files}")
    print(f"  Tests generated: {total_tests}")

    if all_errors:
        print(f"\nErrors ({len(all_errors)}):")
        for error in all_errors[:5]:
            print(f"  - {error}")
        if len(all_errors) > 5:
            print(f"  ... and {len(all_errors) - 5} more")

    return 0 if not all_errors else 1


if __name__ == '__main__':
    sys.exit(main())
