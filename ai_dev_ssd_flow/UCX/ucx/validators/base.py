"""Base validator interface."""

from abc import ABC, abstractmethod
from pathlib import Path
import re
import yaml

from ucx.models.review import ValidationResult
from ucx.models.enums import ValidationStatus


class BaseValidator(ABC):
    """Abstract base class for document validators."""

    def __init__(self):
        """Initialize validator."""
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.passes: list[str] = []

    def validate(self, doc_path: Path) -> ValidationResult:
        """
        Validate a document.

        Args:
            doc_path: Path to document file or directory

        Returns:
            ValidationResult with errors, warnings, passes
        """
        # Reset state
        self.errors = []
        self.warnings = []
        self.passes = []

        # Get files to validate
        files = self._get_files(doc_path)

        # Run validation on each file
        for file_path in files:
            content = file_path.read_text(encoding="utf-8")
            self._validate_file(file_path, content)

        # Determine status
        if self.errors:
            status = ValidationStatus.FAILED
        else:
            status = ValidationStatus.PASSED

        return ValidationResult(
            status=status,
            errors=self.errors,
            warnings=self.warnings,
            passes=self.passes,
        )

    @abstractmethod
    def _validate_file(self, file_path: Path, content: str) -> None:
        """
        Validate a single file.

        Implementations should populate self.errors, self.warnings, self.passes.

        Args:
            file_path: Path to file
            content: File content
        """
        pass

    def _get_files(self, doc_path: Path) -> list[Path]:
        """Get list of files to validate."""
        if doc_path.is_dir():
            files = list(doc_path.glob("*.md"))
            # Exclude review/report files
            return [f for f in files if "REVIEW" not in f.name and "REPORT" not in f.name]
        return [doc_path]

    # Common validation helpers

    def check_yaml_frontmatter(
        self,
        content: str,
        required_fields: list[str],
        file_name: str = "",
    ) -> bool:
        """
        Check YAML frontmatter for required fields.

        Args:
            content: File content
            required_fields: List of required field names
            file_name: File name for error messages

        Returns:
            True if valid, False otherwise
        """
        if not content.startswith("---"):
            self.errors.append(f"{file_name}: Missing YAML frontmatter")
            return False

        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            self.errors.append(f"{file_name}: Malformed YAML frontmatter")
            return False

        try:
            frontmatter = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError as e:
            self.errors.append(f"{file_name}: Invalid YAML: {e}")
            return False

        valid = True
        for field in required_fields:
            if field not in frontmatter:
                self.errors.append(f"{file_name}: Missing required field: {field}")
                valid = False
            else:
                self.passes.append(f"{file_name}: Found {field}")

        return valid

    def check_element_ids(
        self,
        content: str,
        pattern: str,
        file_name: str = "",
    ) -> int:
        """
        Check element ID format.

        Args:
            content: File content
            pattern: Regex pattern for valid IDs
            file_name: File name for messages

        Returns:
            Count of valid element IDs found
        """
        matches = re.findall(pattern, content)
        if matches:
            self.passes.append(f"{file_name}: Found {len(matches)} valid element IDs")
        return len(matches)

    def check_required_sections(
        self,
        content: str,
        sections: list[str],
        file_name: str = "",
    ) -> bool:
        """
        Check for required sections.

        Args:
            content: File content
            sections: List of required section headings
            file_name: File name for messages

        Returns:
            True if all sections found
        """
        valid = True
        for section in sections:
            if re.search(rf"^#+\s*{re.escape(section)}", content, re.MULTILINE | re.IGNORECASE):
                self.passes.append(f"{file_name}: Found section: {section}")
            else:
                self.warnings.append(f"{file_name}: Missing section: {section}")
                valid = False
        return valid

    def check_traceability(
        self,
        content: str,
        patterns: list[str],
        file_name: str = "",
    ) -> int:
        """
        Check for traceability tags.

        Args:
            content: File content
            patterns: List of tag patterns (e.g., "@brd:", "@prd:")
            file_name: File name for messages

        Returns:
            Count of traceability tags found
        """
        total = 0
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            total += len(matches)

        if total > 0:
            self.passes.append(f"{file_name}: Found {total} traceability tags")
        else:
            self.warnings.append(f"{file_name}: No traceability tags found")

        return total
