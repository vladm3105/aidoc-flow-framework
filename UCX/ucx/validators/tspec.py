"""TSPEC (Test Specification) validator."""

import re
from pathlib import Path

from ucx.models.enums import DocType
from ucx.validators.base import BaseValidator
from ucx.validators.registry import register_validator


@register_validator(DocType.TSPEC)
class TSPECValidator(BaseValidator):
    """Validator for Test Specification Documents (Layer 10)."""

    REQUIRED_FRONTMATTER = ["title", "doc_id", "version", "status", "test_type"]

    REQUIRED_SECTIONS = [
        "Test Cases",
        "Test Data",
    ]

    OPTIONAL_SECTIONS = [
        "Test Environment",
        "Prerequisites",
        "Setup",
        "Teardown",
        "Coverage",
        "Automation",
    ]

    ELEMENT_ID_PATTERN = r"TSPEC\.\d+\.\d+\.\d+"

    TRACE_PATTERNS = [
        r"@spec:",
        r"@req:",
        r"@bdd:",
    ]

    # Valid test types
    VALID_TEST_TYPES = [
        "unit",
        "integration",
        "e2e",
        "end-to-end",
        "functional",
        "performance",
        "security",
        "smoke",
        "regression",
        "acceptance",
    ]

    def _validate_file(self, file_path: Path, content: str) -> None:
        """Validate a TSPEC file."""
        file_name = file_path.name

        # Check YAML frontmatter
        self.check_yaml_frontmatter(
            content,
            self.REQUIRED_FRONTMATTER,
            file_name,
        )

        # Check element IDs
        id_count = self.check_element_ids(
            content,
            self.ELEMENT_ID_PATTERN,
            file_name,
        )
        if id_count == 0:
            self.warnings.append(f"{file_name}: No TSPEC element IDs found")

        # Check required sections
        self.check_required_sections(
            content,
            self.REQUIRED_SECTIONS,
            file_name,
        )

        # Check traceability
        self.check_traceability(
            content,
            self.TRACE_PATTERNS,
            file_name,
        )

        # TSPEC-specific checks
        self._check_test_type(content, file_name)
        self._check_test_cases(content, file_name)
        self._check_test_data(content, file_name)
        self._check_coverage_info(content, file_name)
        self._check_automation_status(content, file_name)

    def _check_test_type(self, content: str, file_name: str) -> None:
        """Check for valid test type."""
        match = re.search(r"test_type:\s*(\S+)", content, re.IGNORECASE)
        if match:
            test_type = match.group(1).lower().strip('"\'')
            if test_type in self.VALID_TEST_TYPES:
                self.passes.append(f"{file_name}: Valid test type: {test_type}")
            else:
                self.warnings.append(
                    f"{file_name}: Unusual test type: {test_type}. "
                    f"Common types: {', '.join(self.VALID_TEST_TYPES[:5])}..."
                )

    def _check_test_cases(self, content: str, file_name: str) -> None:
        """Check for test case definitions."""
        # Various test case identifier patterns
        tc_patterns = [
            r"TC[-._]?\d+",
            r"test\s+case\s*\d+",
            r"TSPEC\.\d+\.\d+\.\d+",
            r"^\s*[-*]\s*Test:",
        ]

        total_cases = 0
        for pattern in tc_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            total_cases += len(matches)

        if total_cases > 0:
            self.passes.append(f"{file_name}: Contains {total_cases} test case references")
        else:
            self.errors.append(f"{file_name}: No test cases defined")

        # Check test case structure (Given/When/Then or Arrange/Act/Assert)
        has_gwt = bool(re.search(r"\b(Given|When|Then)\b", content))
        has_aaa = bool(re.search(r"\b(Arrange|Act|Assert)\b", content))

        if has_gwt or has_aaa:
            pattern_name = "Given/When/Then" if has_gwt else "Arrange/Act/Assert"
            self.passes.append(f"{file_name}: Uses {pattern_name} structure")

    def _check_test_data(self, content: str, file_name: str) -> None:
        """Check for test data definitions."""
        test_data_indicators = [
            r"\btest\s+data\b",
            r"\bfixture(s)?\b",
            r"\bmock(s)?\b",
            r"\bstub(s)?\b",
            r"\bsample\s+data\b",
            r"\btest\s+input(s)?\b",
            r"\bexpected\s+(output|result)",
        ]

        found = []
        for pattern in test_data_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                found.append(pattern.replace(r"\b", "").replace("(s)?", ""))

        if found:
            self.passes.append(f"{file_name}: Test data specified")
        else:
            self.warnings.append(f"{file_name}: No test data defined")

    def _check_coverage_info(self, content: str, file_name: str) -> None:
        """Check for coverage information."""
        coverage_patterns = [
            r"\bcoverage\b",
            r"\bcovered\s+by\b",
            r"\bcovers\b",
            r"\d+%\s*(coverage|covered)",
            r"requirement\s+coverage",
        ]

        for pattern in coverage_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.passes.append(f"{file_name}: Coverage information present")
                return

        self.warnings.append(f"{file_name}: No coverage information")

    def _check_automation_status(self, content: str, file_name: str) -> None:
        """Check for automation status or indicators."""
        automation_patterns = [
            r"\bautomated?\b",
            r"\bmanual\b",
            r"\bscript(ed)?\b",
            r"\bpytest\b|\bjest\b|\bmocha\b",
            r"\bselenium\b|\bplaywright\b|\bcypress\b",
        ]

        automated = False
        manual = False

        for pattern in automation_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                if "manual" in pattern:
                    manual = True
                else:
                    automated = True

        if automated and manual:
            self.passes.append(f"{file_name}: Mixed automation (automated + manual)")
        elif automated:
            self.passes.append(f"{file_name}: Automated test specification")
        elif manual:
            self.passes.append(f"{file_name}: Manual test specification")
        else:
            self.warnings.append(
                f"{file_name}: Automation status not specified"
            )
