"""Generic validator for document types without specific validators."""

from pathlib import Path

from ucx.models.enums import DocType
from ucx.validators.base import BaseValidator


class GenericValidator(BaseValidator):
    """Generic validator for any document type."""

    REQUIRED_FRONTMATTER = ["title", "doc_id", "version"]

    def __init__(self, doc_type: DocType):
        """
        Initialize generic validator.

        Args:
            doc_type: Document type to validate
        """
        super().__init__()
        self.doc_type = doc_type
        self.element_id_pattern = rf"{doc_type.value.upper()}\.\d+\.[A-Z0-9]+\.\d+"

    def _validate_file(self, file_path: Path, content: str) -> None:
        """Validate a file using generic rules."""
        file_name = file_path.name

        # Check YAML frontmatter
        self.check_yaml_frontmatter(
            content,
            self.REQUIRED_FRONTMATTER,
            file_name,
        )

        # Check element IDs
        self.check_element_ids(
            content,
            self.element_id_pattern,
            file_name,
        )

        # Check for any traceability
        trace_patterns = [
            r"@brd:",
            r"@prd:",
            r"@ears:",
            r"@adr:",
            r"@sys:",
            r"@req:",
        ]
        self.check_traceability(
            content,
            trace_patterns,
            file_name,
        )
