#!/usr/bin/env python3
"""
Generate Test-Aware SPEC Script

Generates SPEC YAML files that satisfy test requirements extracted by
analyze_test_requirements.py. Part of Phase 2: TDD Awareness in MVP Autopilot.

Usage:
    python generate_spec_tdd.py --test-requirements tmp/test_requirements.json --output ai_dev_flow/09_SPEC/
    python generate_spec_tdd.py --test-requirements tmp/auth_requirements.json --req-dir ai_dev_flow/07_REQ/ --output ai_dev_flow/09_SPEC/

Reference: IPLAN-001 Section 4.2.2
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class InterfaceMethod:
    """Method to be implemented in SPEC."""
    name: str
    class_name: Optional[str] = None
    signature: str = ""
    purpose: str = ""
    parameters: list[dict] = field(default_factory=list)
    return_type: Optional[str] = None
    exceptions: list[str] = field(default_factory=list)
    source_tests: list[str] = field(default_factory=list)
    assertions: list[str] = field(default_factory=list)


@dataclass
class TestAwareSPEC:
    """SPEC document structure derived from test requirements."""
    spec_id: str
    component_name: str
    summary: str
    req_ids: list[str]
    traceability_tags: dict[str, list[str]]
    interfaces: list[InterfaceMethod]
    data_models: list[dict]
    validation_rules: list[dict]
    test_references: list[dict]


class TestAwareSPECGenerator:
    """
    Generates SPEC YAML files using test requirements as input.

    Implements the test-aware SPEC generation from IPLAN-001 Phase 2.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.today = date.today().isoformat()

    def load_test_requirements(self, path: Path) -> dict:
        """Load test requirements JSON."""
        with open(path, encoding='utf-8') as f:
            return json.load(f)

    def generate_spec_from_tests(
        self,
        test_requirements: dict,
        req_dir: Optional[Path] = None,
        output_dir: Path = Path('.')
    ) -> list[Path]:
        """
        Generate SPEC files from test requirements.

        Args:
            test_requirements: Output from analyze_test_requirements.py
            req_dir: Optional REQ documents directory for additional context
            output_dir: Output directory for SPEC files

        Returns:
            List of generated SPEC file paths
        """
        generated_files = []

        # Group test files by REQ coverage
        by_req = test_requirements.get('by_req', {})

        if not by_req:
            # If no REQ coverage, generate a single SPEC from all tests
            spec_data = self._build_spec_from_all_tests(test_requirements)
            output_path = output_dir / f"SPEC-01_{spec_data.component_name}.yaml"
            self._write_spec(spec_data, output_path)
            generated_files.append(output_path)
        else:
            # Generate SPEC per REQ group
            for req_id, test_files in by_req.items():
                spec_data = self._build_spec_for_req(
                    req_id, test_files, test_requirements, req_dir
                )
                if spec_data:
                    output_path = output_dir / f"SPEC-{spec_data.spec_id}_{spec_data.component_name}.yaml"
                    self._write_spec(spec_data, output_path)
                    generated_files.append(output_path)

        return generated_files

    def _build_spec_from_all_tests(self, test_requirements: dict) -> TestAwareSPEC:
        """Build a single SPEC from all test files."""
        all_methods = []
        all_traceability = self._empty_traceability()
        all_test_refs = []
        all_assertions = []

        for file_path, file_data in test_requirements.get('files', {}).items():
            if isinstance(file_data, dict) and 'error' not in file_data:
                # Merge traceability
                file_trace = file_data.get('file_traceability', {})
                for key in all_traceability:
                    all_traceability[key].extend(file_trace.get(key, []))

                # Collect methods
                for method in file_data.get('required_methods', []):
                    all_methods.append(self._method_to_interface(method))

                # Collect test references
                for tc in file_data.get('test_cases', []):
                    all_test_refs.append({
                        'test_id': tc.get('test_id'),
                        'test_name': tc.get('test_name'),
                        'source_file': file_path
                    })
                    all_assertions.extend(tc.get('assertions', []))

        # Deduplicate
        for key in all_traceability:
            all_traceability[key] = list(dict.fromkeys(all_traceability[key]))

        component_name = self._derive_component_name(test_requirements)

        return TestAwareSPEC(
            spec_id="01",
            component_name=component_name,
            summary=f"Test-driven specification for {component_name}",
            req_ids=test_requirements.get('metadata', {}).get('req_coverage', []),
            traceability_tags=all_traceability,
            interfaces=self._dedupe_methods(all_methods),
            data_models=self._infer_data_models(all_assertions),
            validation_rules=self._infer_validation_rules(all_assertions),
            test_references=all_test_refs
        )

    def _build_spec_for_req(
        self,
        req_id: str,
        test_files: list[str],
        test_requirements: dict,
        req_dir: Optional[Path]
    ) -> Optional[TestAwareSPEC]:
        """Build SPEC for a specific REQ ID."""
        all_methods = []
        all_traceability = self._empty_traceability()
        all_test_refs = []
        all_assertions = []

        # Add REQ to traceability
        all_traceability['req'].append(req_id)

        for file_path in test_files:
            file_data = test_requirements.get('files', {}).get(file_path, {})
            if isinstance(file_data, dict) and 'error' not in file_data:
                # Merge traceability
                file_trace = file_data.get('file_traceability', {})
                for key in all_traceability:
                    if key != 'req':  # Already added
                        all_traceability[key].extend(file_trace.get(key, []))

                # Find test cases covering this REQ
                for tc in file_data.get('test_cases', []):
                    tc_reqs = tc.get('traceability', {}).get('req', [])
                    if req_id in tc_reqs or any(req_id in r for r in tc_reqs):
                        # This test case covers our REQ
                        for method in tc.get('required_methods', []):
                            all_methods.append(self._method_to_interface(method))
                        all_test_refs.append({
                            'test_id': tc.get('test_id'),
                            'test_name': tc.get('test_name'),
                            'source_file': file_path
                        })
                        all_assertions.extend(tc.get('assertions', []))

        if not all_methods and not all_test_refs:
            return None

        # Deduplicate
        for key in all_traceability:
            all_traceability[key] = list(dict.fromkeys(all_traceability[key]))

        # Derive component name from REQ ID
        component_name = self._req_to_component_name(req_id)
        spec_id = self._req_to_spec_id(req_id)

        return TestAwareSPEC(
            spec_id=spec_id,
            component_name=component_name,
            summary=f"Test-driven specification implementing {req_id}",
            req_ids=[req_id],
            traceability_tags=all_traceability,
            interfaces=self._dedupe_methods(all_methods),
            data_models=self._infer_data_models(all_assertions),
            validation_rules=self._infer_validation_rules(all_assertions),
            test_references=all_test_refs
        )

    def _method_to_interface(self, method: dict) -> InterfaceMethod:
        """Convert method dict to InterfaceMethod."""
        name = method.get('name', 'unknown')

        # Parse class.method format
        class_name = None
        method_name = name
        if '.' in name:
            parts = name.split('.')
            if len(parts) == 2:
                class_name, method_name = parts
            else:
                method_name = parts[-1]

        # Build signature from parameters
        params = method.get('parameters', [])
        param_strs = []
        for p in params:
            pname = p.get('name') or f"arg{p.get('position', 0)}"
            ptype = p.get('inferred_type', 'Any')
            if ptype == 'unknown':
                ptype = 'Any'
            param_strs.append(f"{pname}: {ptype}")

        return_type = method.get('return_type') or 'Any'
        signature = f"def {method_name}({', '.join(param_strs)}) -> {return_type}"

        return InterfaceMethod(
            name=method_name,
            class_name=class_name,
            signature=signature,
            purpose=f"Method extracted from test: {method.get('source_test', '')}",
            parameters=params,
            return_type=return_type,
            exceptions=method.get('exceptions', []),
            source_tests=[method.get('source_test', '')]
        )

    def _dedupe_methods(self, methods: list[InterfaceMethod]) -> list[InterfaceMethod]:
        """Remove duplicate methods by name."""
        seen = {}
        for method in methods:
            key = f"{method.class_name or ''}.{method.name}"
            if key not in seen:
                seen[key] = method
            else:
                # Merge source tests
                seen[key].source_tests.extend(method.source_tests)
                seen[key].source_tests = list(dict.fromkeys(seen[key].source_tests))
        return list(seen.values())

    def _infer_data_models(self, assertions: list[str]) -> list[dict]:
        """Infer data models from assertions."""
        models = []
        seen_fields = {}

        for assertion in assertions:
            # Look for patterns like: result.field == value
            match = re.search(r'(\w+)\.(\w+)\s*(?:==|is)\s*(.+)', assertion)
            if match:
                var_name, field_name, expected = match.groups()
                if var_name not in seen_fields:
                    seen_fields[var_name] = {}
                if field_name not in seen_fields[var_name]:
                    seen_fields[var_name][field_name] = self._infer_type_from_value(expected)

        for model_name, fields in seen_fields.items():
            models.append({
                'name': model_name.title() + 'Result',
                'description': f'Data model inferred from test assertions on {model_name}',
                'fields': [
                    {'name': fname, 'type': ftype, 'constraints': 'Inferred from tests'}
                    for fname, ftype in fields.items()
                ]
            })

        return models

    def _infer_type_from_value(self, value: str) -> str:
        """Infer type from assertion value."""
        value = value.strip()
        if value in ('True', 'False'):
            return 'bool'
        if value == 'None':
            return 'Optional[Any]'
        if value.startswith('"') or value.startswith("'"):
            return 'str'
        if value.isdigit():
            return 'int'
        if re.match(r'^\d+\.\d+$', value):
            return 'float'
        if value.startswith('['):
            return 'list'
        if value.startswith('{'):
            return 'dict'
        return 'Any'

    def _infer_validation_rules(self, assertions: list[str]) -> list[dict]:
        """Infer validation rules from assertions."""
        rules = []

        for assertion in assertions:
            # Look for common validation patterns
            if 'is not None' in assertion:
                match = re.search(r'(\w+(?:\.\w+)?)\s+is\s+not\s+None', assertion)
                if match:
                    rules.append({
                        'rule': f'{match.group(1)} Required',
                        'implementation': f'assert {match.group(1)} is not None'
                    })
            elif '==' in assertion and 'error' in assertion.lower():
                rules.append({
                    'rule': 'Error Handling',
                    'implementation': assertion
                })

        return rules

    def _empty_traceability(self) -> dict[str, list[str]]:
        """Create empty traceability structure."""
        return {
            'brd': [], 'prd': [], 'ears': [], 'bdd': [],
            'adr': [], 'sys': [], 'req': [], 'ctr': [],
            'spec': [], 'tspec': [], 'code': [], 'threshold': []
        }

    def _derive_component_name(self, test_requirements: dict) -> str:
        """Derive component name from test requirements."""
        # Try to get from first file path
        files = list(test_requirements.get('files', {}).keys())
        if files:
            first_file = files[0]
            # Extract component name from test file name
            match = re.search(r'test_(\w+)', first_file)
            if match:
                return match.group(1)
        return 'component'

    def _req_to_component_name(self, req_id: str) -> str:
        """Convert REQ ID to component name."""
        # REQ.01.10.01 -> req_01_10
        parts = req_id.replace('.', '_').lower()
        return parts.replace('-', '_')

    def _req_to_spec_id(self, req_id: str) -> str:
        """Convert REQ ID to SPEC ID."""
        # Extract numeric part
        match = re.search(r'(\d+)', req_id)
        if match:
            return match.group(1).zfill(2)
        return '01'

    def _write_spec(self, spec_data: TestAwareSPEC, output_path: Path) -> None:
        """Write SPEC data to YAML file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        spec_yaml = self._build_spec_yaml(spec_data)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# =============================================================================\n")
            f.write("# Test-Driven SPEC - Generated from unit test analysis\n")
            f.write(f"# Generated: {self.today}\n")
            f.write("# Source: analyze_test_requirements.py -> generate_spec_tdd.py\n")
            f.write("# =============================================================================\n\n")
            yaml.dump(spec_yaml, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        if self.verbose:
            print(f"Generated: {output_path}")

    def _build_spec_yaml(self, spec_data: TestAwareSPEC) -> dict:
        """Build SPEC YAML structure."""
        # Build cumulative tags string
        cumulative_tags = {}
        for tag_type, values in spec_data.traceability_tags.items():
            if values:
                cumulative_tags[tag_type] = ', '.join(values)

        # Build interfaces section
        interfaces_yaml = {
            'internal_apis': [],
            'classes': []
        }

        # Group methods by class
        by_class: dict[str, list[InterfaceMethod]] = {}
        for method in spec_data.interfaces:
            class_key = method.class_name or 'ServiceClass'
            if class_key not in by_class:
                by_class[class_key] = []
            by_class[class_key].append(method)

        for class_name, methods in by_class.items():
            class_def = {
                'name': class_name,
                'description': f'Service class implementing test requirements',
                'methods': []
            }
            for method in methods:
                method_def = {
                    'name': method.name,
                    'signature': method.signature,
                    'purpose': method.purpose,
                    'test_sources': method.source_tests
                }
                class_def['methods'].append(method_def)
                interfaces_yaml['internal_apis'].append({
                    'interface': f'{class_name}.{method.name}()',
                    'signature': method.signature,
                    'purpose': method.purpose
                })
            interfaces_yaml['classes'].append(class_def)

        # Build complete SPEC structure
        spec_yaml = {
            'id': spec_data.component_name,
            'summary': spec_data.summary,
            'metadata': {
                'version': '1.0.0',
                'status': 'draft',
                'created_date': self.today,
                'last_updated': self.today,
                'task_ready_score': 'PENDING - TDD Generated',
                'generation_mode': 'test_driven',
                'source_tests': len(spec_data.test_references)
            },
            'traceability': {
                'upstream_sources': {
                    'atomic_requirements': [
                        {'id': req_id, 'relationship': 'Implements requirement'}
                        for req_id in spec_data.req_ids
                    ]
                },
                'cumulative_tags': cumulative_tags,
                'test_sources': spec_data.test_references
            },
            'req_implementations': self._build_req_implementations(spec_data),
            'interfaces': interfaces_yaml,
            'behavior': {
                'state_management': {
                    'description': 'State machine derived from test assertions',
                    'states': ['INITIAL', 'PROCESSING', 'SUCCESS', 'ERROR'],
                    'transitions': [
                        {'from': 'INITIAL', 'to': 'PROCESSING', 'trigger': 'start()'},
                        {'from': 'PROCESSING', 'to': 'SUCCESS', 'trigger': 'complete()'},
                        {'from': 'PROCESSING', 'to': 'ERROR', 'trigger': 'fail()'}
                    ]
                }
            },
            'verification': {
                'unit_tests': {
                    'source': 'TDD - Tests written before implementation',
                    'test_count': len(spec_data.test_references),
                    'tests': spec_data.test_references
                },
                'tdd_validation': {
                    'red_state_validated': False,
                    'green_state_validated': False,
                    'coverage_target': '90%'
                }
            }
        }

        # Add data models if any were inferred
        if spec_data.data_models:
            spec_yaml['data_models'] = spec_data.data_models

        # Add validation rules if any were inferred
        if spec_data.validation_rules:
            spec_yaml['validation_rules'] = spec_data.validation_rules

        return spec_yaml

    def _build_req_implementations(self, spec_data: TestAwareSPEC) -> list[dict]:
        """Build req_implementations section."""
        implementations = []

        for req_id in spec_data.req_ids:
            # Find interfaces related to this REQ
            related_interfaces = []
            for method in spec_data.interfaces:
                for source in method.source_tests:
                    if req_id in source:
                        related_interfaces.append({
                            'class': method.class_name or 'ServiceClass',
                            'method': method.name,
                            'signature': method.signature,
                            'purpose': method.purpose
                        })
                        break

            implementations.append({
                'req_id': req_id,
                'req_link': f'../07_REQ/{req_id.replace(".", "/")}.md',
                'implementation': {
                    'interfaces': related_interfaces or [
                        {'method': 'TBD', 'signature': 'TBD', 'purpose': 'Implementation pending'}
                    ],
                    'data_models': [],
                    'validation_rules': [],
                    'error_handling': [],
                    'test_approach': {
                        'unit_tests': [ref['test_name'] for ref in spec_data.test_references],
                        'integration_tests': []
                    }
                }
            })

        return implementations

    def validate_spec_against_tests(
        self,
        spec_path: Path,
        test_requirements: dict
    ) -> dict:
        """
        Validate SPEC against test requirements.

        Returns validation results with coverage analysis.
        """
        with open(spec_path, encoding='utf-8') as f:
            spec = yaml.safe_load(f)

        results = {
            'spec_path': str(spec_path),
            'valid': True,
            'coverage': {
                'methods_covered': 0,
                'methods_missing': [],
                'req_covered': 0,
                'req_missing': []
            },
            'warnings': [],
            'errors': []
        }

        # Check if all required methods from tests are in SPEC
        spec_methods = set()
        for cls in spec.get('interfaces', {}).get('classes', []):
            for method in cls.get('methods', []):
                spec_methods.add(method.get('name'))

        test_methods = set()
        for method in test_requirements.get('required_methods', []):
            name = method.get('name', '').split('.')[-1]
            if name and not self._is_builtin(name):
                test_methods.add(name)

        missing_methods = test_methods - spec_methods
        if missing_methods:
            results['coverage']['methods_missing'] = list(missing_methods)
            results['warnings'].append(
                f"Methods in tests but not in SPEC: {missing_methods}"
            )

        results['coverage']['methods_covered'] = len(test_methods - missing_methods)

        # Check REQ coverage
        spec_reqs = set()
        for impl in spec.get('req_implementations', []):
            spec_reqs.add(impl.get('req_id'))

        test_reqs = set(test_requirements.get('metadata', {}).get('req_coverage', []))

        missing_reqs = test_reqs - spec_reqs
        if missing_reqs:
            results['coverage']['req_missing'] = list(missing_reqs)
            results['warnings'].append(
                f"REQs in tests but not in SPEC: {missing_reqs}"
            )

        results['coverage']['req_covered'] = len(test_reqs - missing_reqs)

        if results['errors']:
            results['valid'] = False

        return results

    def _is_builtin(self, name: str) -> bool:
        """Check if name is a Python builtin."""
        builtins = {
            'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set',
            'tuple', 'type', 'print', 'range', 'open', 'isinstance', 'hasattr'
        }
        return name in builtins


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate test-aware SPEC files from test requirements',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate SPEC from test requirements
  python generate_spec_tdd.py --test-requirements tmp/test_requirements.json --output ai_dev_flow/09_SPEC/

  # Generate with REQ directory for additional context
  python generate_spec_tdd.py --test-requirements tmp/test_requirements.json --req-dir ai_dev_flow/07_REQ/ --output ai_dev_flow/09_SPEC/

  # Validate existing SPEC against tests
  python generate_spec_tdd.py --validate ai_dev_flow/09_SPEC/SPEC-01_auth.yaml --test-requirements tmp/test_requirements.json
        """
    )

    parser.add_argument(
        '--test-requirements', '-t',
        type=Path,
        required=True,
        help='Test requirements JSON from analyze_test_requirements.py'
    )

    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output directory for SPEC files'
    )

    parser.add_argument(
        '--req-dir', '-r',
        type=Path,
        help='REQ documents directory for additional context'
    )

    parser.add_argument(
        '--validate', '-V',
        type=Path,
        help='Validate existing SPEC against test requirements'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    generator = TestAwareSPECGenerator(verbose=args.verbose)

    try:
        test_reqs = generator.load_test_requirements(args.test_requirements)

        if args.validate:
            # Validation mode
            results = generator.validate_spec_against_tests(args.validate, test_reqs)
            print(json.dumps(results, indent=2))
            return 0 if results['valid'] else 1
        elif args.output:
            # Generation mode
            generated = generator.generate_spec_from_tests(
                test_reqs,
                args.req_dir,
                args.output
            )
            print(f"Generated {len(generated)} SPEC file(s):")
            for path in generated:
                print(f"  - {path}")
            return 0
        else:
            parser.error("Either --output or --validate is required")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
