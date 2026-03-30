"""ADR (Architecture Decision Record) validator."""

import re
from pathlib import Path

from ucx.models.enums import DocType
from ucx.validators.base import BaseValidator
from ucx.validators.registry import register_validator


@register_validator(DocType.ADR)
class ADRValidator(BaseValidator):
    """Validator for Architecture Decision Records (Layer 5)."""

    REQUIRED_FRONTMATTER = ["title", "doc_id", "version", "status", "decision_status"]

    REQUIRED_SECTIONS = [
        "Context",
        "Decision",
        "Consequences",
    ]

    OPTIONAL_SECTIONS = [
        "Status",
        "Options Considered",
        "Pros and Cons",
        "Related Decisions",
    ]

    ELEMENT_ID_PATTERN = r"ADR\.\d+\.\d+"

    TRACE_PATTERNS = [
        r"@brd:",
        r"@sys:",
        r"@adr:",
    ]

    # Valid ADR statuses
    VALID_STATUSES = [
        "proposed",
        "accepted",
        "deprecated",
        "superseded",
        "rejected",
    ]

    def _validate_file(self, file_path: Path, content: str) -> None:
        """Validate an ADR file."""
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
            self.warnings.append(f"{file_name}: No ADR element IDs found")

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

        # ADR-specific checks
        self._check_decision_status(content, file_name)
        self._check_options_considered(content, file_name)
        self._check_consequences_balance(content, file_name)
        self._check_related_decisions(content, file_name)

    def _check_decision_status(self, content: str, file_name: str) -> None:
        """Check for valid decision status."""
        # Look in frontmatter
        match = re.search(r"decision_status:\s*(\w+)", content, re.IGNORECASE)
        if match:
            status = match.group(1).lower()
            if status in self.VALID_STATUSES:
                self.passes.append(f"{file_name}: Valid decision status: {status}")
            else:
                self.errors.append(
                    f"{file_name}: Invalid decision status: {status}. "
                    f"Valid: {', '.join(self.VALID_STATUSES)}"
                )
        else:
            self.errors.append(f"{file_name}: Missing decision_status in frontmatter")

    def _check_options_considered(self, content: str, file_name: str) -> None:
        """Check for options considered section."""
        if re.search(r"options?\s+considered", content, re.IGNORECASE):
            # Check if there are multiple options listed
            options = re.findall(r"^\s*[-*]\s*Option\s*\d*", content, re.MULTILINE | re.IGNORECASE)
            alt_options = re.findall(r"^\s*\d+\.\s+\w+", content, re.MULTILINE)

            option_count = len(options) + len(alt_options)
            if option_count >= 2:
                self.passes.append(f"{file_name}: Multiple options considered ({option_count})")
            else:
                self.warnings.append(
                    f"{file_name}: Consider documenting multiple options"
                )
        else:
            self.warnings.append(f"{file_name}: No 'Options Considered' section")

    def _check_consequences_balance(self, content: str, file_name: str) -> None:
        """Check for balanced positive and negative consequences."""
        # Look for positive indicators
        positive = len(re.findall(r"(benefit|advantage|pro|positive|improvement)", content, re.IGNORECASE))
        # Look for negative indicators
        negative = len(re.findall(r"(risk|drawback|con|negative|disadvantage|downside)", content, re.IGNORECASE))

        if positive > 0 and negative > 0:
            self.passes.append(
                f"{file_name}: Balanced consequences (positive: {positive}, negative: {negative})"
            )
        elif positive > 0 and negative == 0:
            self.warnings.append(
                f"{file_name}: Only positive consequences documented"
            )
        elif negative > 0 and positive == 0:
            self.warnings.append(
                f"{file_name}: Only negative consequences documented"
            )

    def _check_related_decisions(self, content: str, file_name: str) -> None:
        """Check for references to related ADRs."""
        related_refs = re.findall(r"ADR-\d+|@adr:\s*ADR-\d+", content, re.IGNORECASE)
        if related_refs:
            unique_refs = set(ref.upper().replace("@ADR:", "").strip() for ref in related_refs)
            self.passes.append(
                f"{file_name}: References {len(unique_refs)} related ADR(s)"
            )
