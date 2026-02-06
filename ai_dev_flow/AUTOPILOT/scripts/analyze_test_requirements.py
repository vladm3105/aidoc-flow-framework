#!/usr/bin/env python3
"""
Analyze Test Requirements Script

Parses unit test files to extract requirements for test-aware SPEC generation.
Part of Phase 2: TDD Awareness in MVP Autopilot.

Usage:
    python analyze_test_requirements.py --test-dir tests/unit/ --output tmp/test_requirements.json
    python analyze_test_requirements.py --test-file tests/unit/test_auth.py --output tmp/test_requirements.json

Reference: IPLAN-001 Section 4.2.1
"""

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional


@dataclass
class TraceabilityTags:
    """Traceability tags extracted from docstrings."""
    brd: list[str] = field(default_factory=list)
    prd: list[str] = field(default_factory=list)
    ears: list[str] = field(default_factory=list)
    bdd: list[str] = field(default_factory=list)
    adr: list[str] = field(default_factory=list)
    sys: list[str] = field(default_factory=list)
    req: list[str] = field(default_factory=list)
    ctr: list[str] = field(default_factory=list)
    spec: list[str] = field(default_factory=list)
    tspec: list[str] = field(default_factory=list)
    code: list[str] = field(default_factory=list)
    threshold: list[str] = field(default_factory=list)


@dataclass
class MethodSignature:
    """Extracted method signature from test assertions."""
    name: str
    parameters: list[dict[str, Any]] = field(default_factory=list)
    return_type: Optional[str] = None
    exceptions: list[str] = field(default_factory=list)
    source_test: str = ""


@dataclass
class TestCase:
    """Individual test case information."""
    test_id: str
    test_name: str
    test_class: Optional[str]
    docstring: Optional[str]
    traceability: TraceabilityTags
    required_methods: list[MethodSignature]
    input_output_hints: list[dict[str, Any]]
    assertions: list[str]
    parametrized_cases: list[dict[str, Any]]


@dataclass
class TestFileAnalysis:
    """Analysis result for a single test file."""
    file_path: str
    module_docstring: Optional[str]
    file_traceability: TraceabilityTags
    test_cases: list[TestCase]
    required_classes: list[str]
    required_methods: list[MethodSignature]
    coverage_targets: list[str]


class TestRequirementAnalyzer:
    """
    Analyzes unit test files to extract requirements for SPEC generation.

    Implements the TestRequirementAnalyzer Protocol from IPLAN-001.
    """

    # Pattern to match traceability tags in docstrings
    TAG_PATTERN = re.compile(r'@(\w+):\s*(.+?)(?=\n|@|\Z)', re.MULTILINE)

    # Pattern to extract REQ IDs
    REQ_ID_PATTERN = re.compile(r'REQ[-.]?\d+(?:\.\d+)*', re.IGNORECASE)

    # Pattern to extract Test IDs
    TEST_ID_PATTERN = re.compile(r'(?:UTEST|ITEST|STEST|FTEST|TSPEC)[-.]?\d+(?:\.\d+)*', re.IGNORECASE)

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def analyze_test_file(self, test_file: Path) -> TestFileAnalysis:
        """
        Analyze a single unit test file.

        Args:
            test_file: Path to the test file

        Returns:
            TestFileAnalysis with extracted requirements
        """
        if not test_file.exists():
            raise FileNotFoundError(f"Test file not found: {test_file}")

        content = test_file.read_text(encoding='utf-8')

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            raise ValueError(f"Syntax error in {test_file}: {e}")

        # Extract module-level docstring
        module_docstring = ast.get_docstring(tree)
        file_traceability = self._extract_traceability(module_docstring or "")

        # Analyze test classes and functions
        test_cases = []
        required_classes = set()
        all_required_methods = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                class_analysis = self._analyze_test_class(node, str(test_file))
                test_cases.extend(class_analysis['test_cases'])
                required_classes.update(class_analysis['required_classes'])
                all_required_methods.extend(class_analysis['required_methods'])

            elif isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                # Top-level test function (not in a class)
                if not self._is_inside_class(tree, node):
                    test_case = self._analyze_test_function(node, None, str(test_file))
                    test_cases.append(test_case)
                    all_required_methods.extend(test_case.required_methods)

        # Extract coverage targets from traceability
        coverage_targets = self._extract_coverage_targets(file_traceability, test_cases)

        return TestFileAnalysis(
            file_path=str(test_file),
            module_docstring=module_docstring,
            file_traceability=file_traceability,
            test_cases=test_cases,
            required_classes=list(required_classes),
            required_methods=self._dedupe_methods(all_required_methods),
            coverage_targets=coverage_targets
        )

    def _analyze_test_class(self, class_node: ast.ClassDef, file_path: str) -> dict:
        """Analyze a test class and its methods."""
        test_cases = []
        required_classes = set()
        required_methods = []

        class_docstring = ast.get_docstring(class_node)
        class_traceability = self._extract_traceability(class_docstring or "")

        for node in class_node.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                test_case = self._analyze_test_function(
                    node, class_node.name, file_path, class_traceability
                )
                test_cases.append(test_case)
                required_methods.extend(test_case.required_methods)

            # Look for fixture methods that might indicate class dependencies
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                classes = self._extract_class_references(node)
                required_classes.update(classes)

        return {
            'test_cases': test_cases,
            'required_classes': required_classes,
            'required_methods': required_methods
        }

    def _analyze_test_function(
        self,
        func_node: ast.FunctionDef,
        class_name: Optional[str],
        file_path: str,
        inherited_traceability: Optional[TraceabilityTags] = None
    ) -> TestCase:
        """Analyze a single test function."""
        docstring = ast.get_docstring(func_node)
        traceability = self._extract_traceability(docstring or "")

        # Merge inherited traceability
        if inherited_traceability:
            traceability = self._merge_traceability(inherited_traceability, traceability)

        # Extract method calls that look like production code
        required_methods = self._extract_required_methods(func_node, file_path)

        # Extract assertions for I/O hints
        assertions = self._extract_assertions(func_node)
        input_output_hints = self._derive_io_hints(func_node)

        # Extract parametrized cases
        parametrized = self._extract_parametrized_cases(func_node)

        # Generate test ID
        test_id = self._generate_test_id(func_node, traceability)

        return TestCase(
            test_id=test_id,
            test_name=func_node.name,
            test_class=class_name,
            docstring=docstring,
            traceability=traceability,
            required_methods=required_methods,
            input_output_hints=input_output_hints,
            assertions=assertions,
            parametrized_cases=parametrized
        )

    def _extract_traceability(self, text: str) -> TraceabilityTags:
        """Extract traceability tags from docstring or comment."""
        tags = TraceabilityTags()

        for match in self.TAG_PATTERN.finditer(text):
            tag_name = match.group(1).lower()
            tag_value = match.group(2).strip()

            # Split multiple values (e.g., "@req: REQ-01, REQ-02")
            values = [v.strip() for v in tag_value.split(',')]

            if hasattr(tags, tag_name):
                getattr(tags, tag_name).extend(values)

        return tags

    def _merge_traceability(
        self,
        parent: TraceabilityTags,
        child: TraceabilityTags
    ) -> TraceabilityTags:
        """Merge parent and child traceability tags."""
        merged = TraceabilityTags()

        for field_name in ['brd', 'prd', 'ears', 'bdd', 'adr', 'sys',
                           'req', 'ctr', 'spec', 'tspec', 'code', 'threshold']:
            parent_vals = getattr(parent, field_name)
            child_vals = getattr(child, field_name)
            # Child values take precedence, then parent
            merged_vals = list(dict.fromkeys(child_vals + parent_vals))
            setattr(merged, field_name, merged_vals)

        return merged

    def _extract_required_methods(
        self,
        func_node: ast.FunctionDef,
        file_path: str
    ) -> list[MethodSignature]:
        """Extract method signatures from test code that need implementation."""
        methods = []

        for node in ast.walk(func_node):
            # Look for method calls
            if isinstance(node, ast.Call):
                method_info = self._analyze_call(node, func_node.name)
                if method_info:
                    method_info.source_test = f"{file_path}::{func_node.name}"
                    methods.append(method_info)

            # Look for with pytest.raises() to identify expected exceptions
            if isinstance(node, ast.Call) and self._is_pytest_raises(node):
                exception_name = self._extract_exception_name(node)
                if exception_name:
                    # Find the associated method call inside the with block
                    pass  # This would require more context analysis

        return methods

    def _analyze_call(self, call_node: ast.Call, test_name: str) -> Optional[MethodSignature]:
        """Analyze a function/method call to extract signature."""
        # Skip common test framework calls
        skip_names = {'assert', 'assertEqual', 'assertTrue', 'assertFalse',
                      'assertRaises', 'pytest', 'mock', 'patch', 'fixture',
                      'parametrize', 'raises', 'mark', 'skip', 'xfail'}

        func_name = self._get_call_name(call_node)
        if not func_name or func_name.split('.')[-1] in skip_names:
            return None

        # Skip if it looks like a test utility
        if func_name.startswith('test_') or func_name.startswith('_'):
            return None

        # Extract parameters from call
        params = self._extract_call_params(call_node)

        return MethodSignature(
            name=func_name,
            parameters=params,
            return_type=None,  # Would need type hints to determine
            exceptions=[]
        )

    def _get_call_name(self, call_node: ast.Call) -> Optional[str]:
        """Get the name of a function/method call."""
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            # Handle method calls like obj.method()
            parts = []
            node = call_node.func
            while isinstance(node, ast.Attribute):
                parts.append(node.attr)
                node = node.value
            if isinstance(node, ast.Name):
                parts.append(node.id)
            return '.'.join(reversed(parts))
        return None

    def _extract_call_params(self, call_node: ast.Call) -> list[dict[str, Any]]:
        """Extract parameter information from a call."""
        params = []

        # Positional arguments
        for i, arg in enumerate(call_node.args):
            param = {'position': i, 'name': None}
            param['example_value'] = self._ast_to_value(arg)
            param['inferred_type'] = self._infer_type(arg)
            params.append(param)

        # Keyword arguments
        for kw in call_node.keywords:
            param = {
                'name': kw.arg,
                'example_value': self._ast_to_value(kw.value),
                'inferred_type': self._infer_type(kw.value)
            }
            params.append(param)

        return params

    def _ast_to_value(self, node: ast.AST) -> Any:
        """Convert AST node to Python value (for simple cases)."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.List):
            return [self._ast_to_value(elt) for elt in node.elts]
        elif isinstance(node, ast.Dict):
            return {
                self._ast_to_value(k): self._ast_to_value(v)
                for k, v in zip(node.keys, node.values) if k
            }
        elif isinstance(node, ast.Name):
            return f"<{node.id}>"
        elif isinstance(node, ast.Call):
            return f"<call:{self._get_call_name(node)}>"
        return "<complex>"

    def _infer_type(self, node: ast.AST) -> str:
        """Infer type from AST node."""
        if isinstance(node, ast.Constant):
            return type(node.value).__name__
        elif isinstance(node, ast.List):
            return 'list'
        elif isinstance(node, ast.Dict):
            return 'dict'
        elif isinstance(node, ast.Name):
            if node.id in ('True', 'False'):
                return 'bool'
            elif node.id == 'None':
                return 'NoneType'
            return 'unknown'
        elif isinstance(node, ast.Call):
            return 'object'
        return 'unknown'

    def _extract_assertions(self, func_node: ast.FunctionDef) -> list[str]:
        """Extract assertion statements as strings."""
        assertions = []

        for node in ast.walk(func_node):
            if isinstance(node, ast.Assert):
                try:
                    assertions.append(ast.unparse(node.test))
                except Exception:
                    assertions.append("<complex assertion>")
            elif isinstance(node, ast.Call):
                name = self._get_call_name(node)
                if name and 'assert' in name.lower():
                    try:
                        assertions.append(ast.unparse(node))
                    except Exception:
                        assertions.append(f"<{name}>")

        return assertions

    def _derive_io_hints(self, func_node: ast.FunctionDef) -> list[dict[str, Any]]:
        """Derive input/output hints from test structure."""
        hints = []

        # Look for patterns like: result = func(input) / assert result == expected
        for node in ast.walk(func_node):
            if isinstance(node, ast.Assign):
                # Simple assignment: result = func(...)
                if len(node.targets) == 1 and isinstance(node.value, ast.Call):
                    target_name = self._get_assign_target_name(node.targets[0])
                    call_name = self._get_call_name(node.value)
                    if target_name and call_name:
                        hints.append({
                            'call': call_name,
                            'result_variable': target_name,
                            'input_args': self._extract_call_params(node.value)
                        })

        return hints

    def _get_assign_target_name(self, target: ast.AST) -> Optional[str]:
        """Get the name of an assignment target."""
        if isinstance(target, ast.Name):
            return target.id
        return None

    def _extract_parametrized_cases(self, func_node: ast.FunctionDef) -> list[dict[str, Any]]:
        """Extract @pytest.mark.parametrize cases."""
        cases = []

        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Call):
                name = self._get_call_name(decorator)
                if name and 'parametrize' in name:
                    cases.extend(self._parse_parametrize(decorator))

        return cases

    def _parse_parametrize(self, decorator_call: ast.Call) -> list[dict[str, Any]]:
        """Parse pytest.mark.parametrize decorator."""
        cases = []

        if len(decorator_call.args) >= 2:
            # First arg is parameter names (string or tuple)
            param_names_node = decorator_call.args[0]
            if isinstance(param_names_node, ast.Constant):
                param_names = [n.strip() for n in param_names_node.value.split(',')]
            else:
                param_names = ['param']

            # Second arg is list of values
            values_node = decorator_call.args[1]
            if isinstance(values_node, ast.List):
                for elt in values_node.elts:
                    case = {}
                    if isinstance(elt, ast.Tuple):
                        for i, val in enumerate(elt.elts):
                            if i < len(param_names):
                                case[param_names[i]] = self._ast_to_value(val)
                    else:
                        case[param_names[0]] = self._ast_to_value(elt)
                    cases.append(case)

        return cases

    def _extract_class_references(self, node: ast.FunctionDef) -> set[str]:
        """Extract class names referenced in function."""
        classes = set()

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                name = self._get_call_name(child)
                if name and name[0].isupper():  # Likely a class instantiation
                    classes.add(name.split('.')[0])

        return classes

    def _is_inside_class(self, tree: ast.Module, func_node: ast.FunctionDef) -> bool:
        """Check if function is inside a class."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if child is func_node:
                        return True
        return False

    def _is_pytest_raises(self, call_node: ast.Call) -> bool:
        """Check if call is pytest.raises()."""
        name = self._get_call_name(call_node)
        return name in ('pytest.raises', 'raises')

    def _extract_exception_name(self, call_node: ast.Call) -> Optional[str]:
        """Extract exception name from pytest.raises call."""
        if call_node.args:
            arg = call_node.args[0]
            if isinstance(arg, ast.Name):
                return arg.id
        return None

    def _generate_test_id(
        self,
        func_node: ast.FunctionDef,
        traceability: TraceabilityTags
    ) -> str:
        """Generate a test ID based on traceability or function name."""
        # Use TSPEC ID if available
        if traceability.tspec:
            return traceability.tspec[0]

        # Use REQ ID to derive test ID
        if traceability.req:
            req_id = traceability.req[0]
            # Convert REQ-01 to UTEST-01
            match = re.match(r'REQ[-.]?(\d+)', req_id, re.IGNORECASE)
            if match:
                return f"UTEST-{match.group(1)}"

        # Fallback to function name
        return func_node.name

    def _extract_coverage_targets(
        self,
        file_trace: TraceabilityTags,
        test_cases: list[TestCase]
    ) -> list[str]:
        """Extract all REQ IDs that this file covers."""
        targets = set(file_trace.req)

        for tc in test_cases:
            targets.update(tc.traceability.req)

        return sorted(targets)

    def _dedupe_methods(self, methods: list[MethodSignature]) -> list[MethodSignature]:
        """Remove duplicate method signatures."""
        seen = {}
        deduped = []

        for method in methods:
            if method.name not in seen:
                seen[method.name] = method
                deduped.append(method)
            else:
                # Merge parameter info
                existing = seen[method.name]
                for param in method.parameters:
                    if param not in existing.parameters:
                        existing.parameters.append(param)

        return deduped

    def generate_test_requirements(
        self,
        test_dir: Path,
        output: Path,
        pattern: str = "test_*.py"
    ) -> dict[str, Any]:
        """
        Generate test requirements JSON from all test files.

        Args:
            test_dir: Directory containing test files
            output: Path to output JSON file
            pattern: Glob pattern for test files

        Returns:
            Dictionary of all requirements
        """
        all_requirements = {
            'metadata': {
                'generated_from': str(test_dir),
                'file_count': 0,
                'test_count': 0,
                'req_coverage': []
            },
            'files': {},
            'by_req': {},
            'required_methods': [],
            'required_classes': []
        }

        test_files = list(test_dir.glob(f"**/{pattern}"))
        all_requirements['metadata']['file_count'] = len(test_files)

        all_classes = set()
        all_methods = []

        for test_file in test_files:
            if self.verbose:
                print(f"Analyzing: {test_file}")

            try:
                analysis = self.analyze_test_file(test_file)

                # Store file analysis
                rel_path = str(test_file.relative_to(test_dir) if test_dir in test_file.parents else test_file)
                all_requirements['files'][rel_path] = self._serialize_analysis(analysis)

                # Index by REQ ID
                for target in analysis.coverage_targets:
                    if target not in all_requirements['by_req']:
                        all_requirements['by_req'][target] = []
                    all_requirements['by_req'][target].append(rel_path)

                # Collect classes and methods
                all_classes.update(analysis.required_classes)
                all_methods.extend(analysis.required_methods)

                all_requirements['metadata']['test_count'] += len(analysis.test_cases)

            except Exception as e:
                if self.verbose:
                    print(f"  Error: {e}")
                all_requirements['files'][str(test_file)] = {'error': str(e)}

        # Finalize
        all_requirements['metadata']['req_coverage'] = sorted(all_requirements['by_req'].keys())
        all_requirements['required_classes'] = sorted(all_classes)
        all_requirements['required_methods'] = [
            asdict(m) for m in self._dedupe_methods(all_methods)
        ]

        # Write output
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(all_requirements, f, indent=2, default=str)

        if self.verbose:
            print(f"\nGenerated: {output}")
            print(f"  Files analyzed: {all_requirements['metadata']['file_count']}")
            print(f"  Tests found: {all_requirements['metadata']['test_count']}")
            print(f"  REQ coverage: {len(all_requirements['metadata']['req_coverage'])}")

        return all_requirements

    def _serialize_analysis(self, analysis: TestFileAnalysis) -> dict:
        """Convert TestFileAnalysis to serializable dict."""
        return {
            'file_path': analysis.file_path,
            'module_docstring': analysis.module_docstring,
            'file_traceability': asdict(analysis.file_traceability),
            'test_cases': [
                {
                    'test_id': tc.test_id,
                    'test_name': tc.test_name,
                    'test_class': tc.test_class,
                    'docstring': tc.docstring,
                    'traceability': asdict(tc.traceability),
                    'required_methods': [asdict(m) for m in tc.required_methods],
                    'input_output_hints': tc.input_output_hints,
                    'assertions': tc.assertions,
                    'parametrized_cases': tc.parametrized_cases
                }
                for tc in analysis.test_cases
            ],
            'required_classes': analysis.required_classes,
            'required_methods': [asdict(m) for m in analysis.required_methods],
            'coverage_targets': analysis.coverage_targets
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Analyze unit test files to extract requirements for SPEC generation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze all tests in directory
  python analyze_test_requirements.py --test-dir tests/unit/ --output tmp/test_requirements.json

  # Analyze single file
  python analyze_test_requirements.py --test-file tests/unit/test_auth.py --output tmp/auth_requirements.json

  # Verbose output
  python analyze_test_requirements.py --test-dir tests/unit/ --output tmp/test_requirements.json -v
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--test-dir', '-d',
        type=Path,
        help='Directory containing test files'
    )
    group.add_argument(
        '--test-file', '-f',
        type=Path,
        help='Single test file to analyze'
    )

    parser.add_argument(
        '--output', '-o',
        type=Path,
        required=True,
        help='Output JSON file path'
    )

    parser.add_argument(
        '--pattern', '-p',
        default='test_*.py',
        help='Glob pattern for test files (default: test_*.py)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    analyzer = TestRequirementAnalyzer(verbose=args.verbose)

    try:
        if args.test_file:
            # Single file analysis
            analysis = analyzer.analyze_test_file(args.test_file)
            result = analyzer._serialize_analysis(analysis)

            args.output.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)

            if args.verbose:
                print(f"Analyzed: {args.test_file}")
                print(f"Output: {args.output}")
                print(f"Test cases: {len(analysis.test_cases)}")
        else:
            # Directory analysis
            analyzer.generate_test_requirements(
                args.test_dir,
                args.output,
                args.pattern
            )

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
