#!/usr/bin/env python3
"""TASKS Implementation Contracts AST Parser v1.0 (2026-03-06)

AST-based validation for Implementation Contracts (Section 7-8).
Validates Python code blocks embedded in TASKS markdown documents.

Contract Types Validated:
1. Protocol interfaces (typing.Protocol)
2. TypedDict schemas (typing.TypedDict)
3. Pydantic models (pydantic.BaseModel)
4. Dataclasses (@dataclass)
5. Exception hierarchies (Exception subclasses)
6. State machines (Enum with VALID_TRANSITIONS)

Usage:
    from tasks_ast_parser import ContractValidator

    validator = ContractValidator(markdown_content)
    issues = validator.validate_all_contracts()

Author: Claude (TSPEC v2.0 team)
Based on: Phase 0 analysis design
"""

import ast
import re
from typing import List, Dict, Tuple, Optional

# Import error code helpers
try:
    from tasks_error_code_helpers import (
        format_error,
        format_warning,
        format_info,
    )
    HAS_ERROR_CODES = True
except ImportError:
    HAS_ERROR_CODES = False

    def format_error(code, msg=""):
        return f"[{code}] {msg}"

    def format_warning(code, msg=""):
        return f"[{code}] {msg}"

    def format_info(code, msg=""):
        return f"[{code}] {msg}"


# ============================================================================
# CONTRACT VALIDATOR CLASS
# ============================================================================

class ContractValidator:
    """Validates Implementation Contracts using AST parsing.

    Extracts Python code blocks from markdown and validates syntax
    and semantic structure for 6 contract types.
    """

    def __init__(self, content: str, verbose: bool = False):
        """Initialize contract validator.

        Args:
            content: Markdown document content
            verbose: Enable verbose output
        """
        self.content = content
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

        # Extract Implementation Contracts section (7-8)
        self.contracts_section = self._extract_contracts_section()

    def _extract_contracts_section(self) -> str:
        """Extract Section 7-8 (Implementation Contracts).

        Returns:
            Section content or empty string if not found
        """
        # Try multiple section patterns
        patterns = [
            r'## 7\.\s+Implementation Contracts(.*?)(?=## 8\.|## 9\.|$)',
            r'## Implementation Contracts(.*?)(?=## [0-9]|$)',
            r'##\s*7-8[:\.]?\s*Implementation Contracts(.*?)(?=##|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, self.content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1)

        return ""

    def _extract_code_blocks(self, section: str) -> List[Tuple[str, int]]:
        """Extract Python code blocks from markdown section.

        Args:
            section: Markdown section content

        Returns:
            List of (code, line_number) tuples
        """
        code_blocks = []
        pattern = r'```python\n(.*?)\n```'

        for match in re.finditer(pattern, section, re.DOTALL):
            code = match.group(1)
            # Estimate line number (rough approximation)
            line_num = section[:match.start()].count('\n') + 1
            code_blocks.append((code, line_num))

        return code_blocks

    def validate_all_contracts(self) -> Dict:
        """Validate all Implementation Contracts.

        Returns:
            Dictionary with errors, warnings, info, and statistics
        """
        if not self.contracts_section:
            if HAS_ERROR_CODES:
                self.info.append(format_info("TASKS-I001"))
            else:
                self.info.append("No embedded contracts found (may not be needed)")
            return self._generate_report()

        # Extract all code blocks
        code_blocks = self._extract_code_blocks(self.contracts_section)

        if not code_blocks:
            if HAS_ERROR_CODES:
                self.info.append(format_info("TASKS-I001"))
            else:
                self.info.append("No Python code blocks found in contracts section")
            return self._generate_report()

        # Validate each code block
        for code, line_num in code_blocks:
            self._validate_code_block(code, line_num)

        return self._generate_report()

    def _validate_code_block(self, code: str, line_num: int) -> None:
        """Validate a single Python code block.

        Args:
            code: Python code string
            line_num: Line number in document
        """
        # Try to parse code
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            if HAS_ERROR_CODES:
                self.errors.append(format_error(
                    "TASKS-E020",
                    protocol=f"Syntax error at line ~{line_num}: {e.msg}"
                ))
            else:
                self.errors.append(f"Syntax error at line ~{line_num}: {e}")
            return

        # Analyze AST nodes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._validate_class(node, line_num)

    def _validate_class(self, node: ast.ClassDef, line_num: int) -> None:
        """Validate class definition.

        Args:
            node: AST ClassDef node
            line_num: Line number in document
        """
        # Determine class type by base classes
        base_names = [
            base.id for base in node.bases
            if isinstance(base, ast.Name)
        ]

        # Check for Protocol
        if 'Protocol' in base_names:
            self._validate_protocol(node, line_num)

        # Check for TypedDict
        elif 'TypedDict' in base_names:
            self._validate_typeddict(node, line_num)

        # Check for BaseModel (Pydantic)
        elif 'BaseModel' in base_names:
            self._validate_pydantic_model(node, line_num)

        # Check for Exception
        elif any('Exception' in name for name in base_names):
            self._validate_exception(node, line_num)

        # Check for Enum
        elif 'Enum' in base_names:
            self._validate_state_machine(node, line_num)

        # Check for dataclass (decorator-based)
        elif self._has_dataclass_decorator(node):
            self._validate_dataclass(node, line_num)

    def _validate_protocol(self, node: ast.ClassDef, line_num: int) -> None:
        """Validate Protocol interface.

        Args:
            node: AST ClassDef node
            line_num: Line number in document
        """
        class_name = node.name

        # Extract methods
        methods = [
            item for item in node.body
            if isinstance(item, ast.FunctionDef)
        ]

        if not methods:
            if HAS_ERROR_CODES:
                self.errors.append(format_error(
                    "TASKS-E024",
                    protocol=class_name
                ))
            else:
                self.errors.append(f"Protocol {class_name} has no method signatures")
            return

        # Validate each method has return type
        for method in methods:
            if not method.returns:
                if HAS_ERROR_CODES:
                    self.warnings.append(format_warning(
                        "TASKS-W015",
                        f"Protocol {class_name}.{method.name}() missing return type hint"
                    ))
                else:
                    self.warnings.append(
                        f"Protocol {class_name}.{method.name}() missing return type hint"
                    )

    def _validate_typeddict(self, node: ast.ClassDef, line_num: int) -> None:
        """Validate TypedDict schema.

        Args:
            node: AST ClassDef node
            line_num: Line number in document
        """
        class_name = node.name

        # Extract field annotations
        fields_with_types = [
            item for item in node.body
            if isinstance(item, ast.AnnAssign)
        ]

        if not fields_with_types:
            if HAS_ERROR_CODES:
                self.errors.append(format_error(
                    "TASKS-E021",
                    typeddict=class_name
                ))
            else:
                self.errors.append(f"TypedDict {class_name} has no typed fields")

    def _validate_pydantic_model(self, node: ast.ClassDef, line_num: int) -> None:
        """Validate Pydantic BaseModel.

        Args:
            node: AST ClassDef node
            line_num: Line number in document
        """
        class_name = node.name

        # Check for field validators
        has_validators = any(
            isinstance(item, ast.FunctionDef) and
            any(
                isinstance(dec, ast.Name) and dec.id == 'validator'
                or isinstance(dec, ast.Call) and
                isinstance(dec.func, ast.Name) and dec.func.id == 'validator'
                for dec in item.decorator_list
            )
            for item in node.body
        )

        if not has_validators:
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning(
                    "TASKS-W024",
                    model=class_name
                ))
            else:
                self.warnings.append(
                    f"Pydantic model {class_name} missing field validators"
                )

    def _validate_exception(self, node: ast.ClassDef, line_num: int) -> None:
        """Validate Exception hierarchy.

        Args:
            node: AST ClassDef node
            line_num: Line number in document
        """
        class_name = node.name

        # Check for error_code attribute
        has_error_code = any(
            isinstance(item, ast.Assign) and
            any(
                isinstance(target, ast.Name) and target.id == 'error_code'
                for target in item.targets
            )
            for item in node.body
        )

        if not has_error_code:
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning(
                    "TASKS-W022",
                    exception=class_name
                ))
            else:
                self.warnings.append(
                    f"Exception {class_name} missing error_code attribute"
                )

    def _validate_state_machine(self, node: ast.ClassDef, line_num: int) -> None:
        """Validate State machine Enum.

        Args:
            node: AST ClassDef node
            line_num: Line number in document
        """
        class_name = node.name

        # Only validate if it looks like a state enum
        if 'State' not in class_name:
            return

        # Look for VALID_TRANSITIONS in the same code block
        # (This is a simplified check - would need parent context)
        if HAS_ERROR_CODES:
            self.warnings.append(format_warning(
                "TASKS-W023",
                enum=class_name
            ))
        else:
            self.warnings.append(
                f"State enum {class_name} - verify VALID_TRANSITIONS map exists"
            )

    def _validate_dataclass(self, node: ast.ClassDef, line_num: int) -> None:
        """Validate dataclass.

        Args:
            node: AST ClassDef node
            line_num: Line number in document
        """
        class_name = node.name

        # Check for typed fields
        fields_with_types = [
            item for item in node.body
            if isinstance(item, ast.AnnAssign)
        ]

        if not fields_with_types:
            if HAS_ERROR_CODES:
                self.errors.append(format_error(
                    "TASKS-E023",
                    dataclass=class_name
                ))
            else:
                self.errors.append(f"Dataclass {class_name} has no typed fields")

    def _has_dataclass_decorator(self, node: ast.ClassDef) -> bool:
        """Check if class has @dataclass decorator.

        Args:
            node: AST ClassDef node

        Returns:
            True if has @dataclass decorator
        """
        return any(
            isinstance(dec, ast.Name) and dec.id == 'dataclass'
            for dec in node.decorator_list
        )

    def _generate_report(self) -> Dict:
        """Generate validation report.

        Returns:
            Dictionary with errors, warnings, info, and stats
        """
        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "counts": {
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "info": len(self.info),
            },
        }


# ============================================================================
# STANDALONE TESTING
# ============================================================================

if __name__ == "__main__":
    import sys
    from pathlib import Path

    if len(sys.argv) < 2:
        print("Usage: python tasks_ast_parser.py <MARKDOWN_FILE>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        sys.exit(1)

    # Read file
    content = file_path.read_text(encoding='utf-8')

    # Validate contracts
    validator = ContractValidator(content, verbose=True)
    results = validator.validate_all_contracts()

    # Print results
    print("=" * 70)
    print("Implementation Contracts AST Validation")
    print("=" * 70)
    print(f"File: {file_path}")
    print()

    if results['errors']:
        print("ERRORS:")
        for error in results['errors']:
            print(f"  {error}")
        print()

    if results['warnings']:
        print("WARNINGS:")
        for warning in results['warnings']:
            print(f"  {warning}")
        print()

    if results['info']:
        print("INFO:")
        for info in results['info']:
            print(f"  {info}")
        print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Errors: {results['counts']['errors']}")
    print(f"Warnings: {results['counts']['warnings']}")
    print(f"Info: {results['counts']['info']}")

    # Exit code
    exit_code = 2 if results['counts']['errors'] > 0 else 0
    sys.exit(exit_code)
