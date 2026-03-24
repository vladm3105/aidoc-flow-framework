"""EARS (Easy Approach to Requirements Syntax) validator."""

import re
from pathlib import Path

from ucx.models.enums import DocType
from ucx.validators.base import BaseValidator
from ucx.validators.registry import register_validator


@register_validator(DocType.EARS)
class EARSValidator(BaseValidator):
    """Validator for EARS Requirements Documents (Layer 3)."""

    REQUIRED_FRONTMATTER = ["title", "doc_id", "version", "status"]

    REQUIRED_SECTIONS = [
        "Requirements",
        "Traceability",
    ]

    ELEMENT_ID_PATTERN = r"EARS\.\d+\.\d+\.\d+"

    TRACE_PATTERNS = [
        r"@prd:",
        r"@bdd:",
    ]

    # EARS keyword patterns (Shall, Should, May, etc.)
    EARS_KEYWORDS = [
        r"\bshall\b",
        r"\bshould\b",
        r"\bmay\b",
        r"\bwill\b",
    ]

    # EARS requirement templates
    EARS_TEMPLATES = {
        "ubiquitous": r"The\s+\w+\s+shall\s+",
        "event_driven": r"When\s+.+,\s+the\s+\w+\s+shall\s+",
        "unwanted_behavior": r"If\s+.+,\s+then\s+the\s+\w+\s+shall\s+",
        "state_driven": r"While\s+.+,\s+the\s+\w+\s+shall\s+",
        "optional": r"Where\s+.+,\s+the\s+\w+\s+shall\s+",
    }

    def _validate_file(self, file_path: Path, content: str) -> None:
        """Validate an EARS file."""
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
            self.warnings.append(f"{file_name}: No EARS element IDs found")

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

        # EARS-specific checks
        self._check_ears_keywords(content, file_name)
        self._check_ears_templates(content, file_name)
        self._check_atomic_requirements(content, file_name)

    def _check_ears_keywords(self, content: str, file_name: str) -> None:
        """Check for EARS requirement keywords."""
        found_keywords = set()
        for pattern in self.EARS_KEYWORDS:
            if re.search(pattern, content, re.IGNORECASE):
                keyword = pattern.replace(r"\b", "").strip()
                found_keywords.add(keyword)

        if "shall" in found_keywords:
            self.passes.append(f"{file_name}: Contains 'shall' requirements (mandatory)")
        else:
            self.errors.append(f"{file_name}: No 'shall' requirements found")

        if "should" in found_keywords:
            self.passes.append(f"{file_name}: Contains 'should' requirements (recommended)")

        if "may" in found_keywords:
            self.passes.append(f"{file_name}: Contains 'may' requirements (optional)")

    def _check_ears_templates(self, content: str, file_name: str) -> None:
        """Check for EARS requirement templates."""
        found_templates = []
        for template_name, pattern in self.EARS_TEMPLATES.items():
            if re.search(pattern, content, re.IGNORECASE):
                found_templates.append(template_name)

        if found_templates:
            self.passes.append(
                f"{file_name}: Found EARS templates: {', '.join(found_templates)}"
            )
        else:
            self.warnings.append(
                f"{file_name}: No standard EARS templates found"
            )

    def _check_atomic_requirements(self, content: str, file_name: str) -> None:
        """Check that requirements appear to be atomic (one shall per requirement)."""
        # Count number of requirement IDs and number of "shall" keywords
        id_matches = re.findall(self.ELEMENT_ID_PATTERN, content)
        shall_matches = re.findall(r"\bshall\b", content, re.IGNORECASE)

        if len(id_matches) > 0 and len(shall_matches) > 0:
            ratio = len(shall_matches) / len(id_matches)
            if 0.8 <= ratio <= 1.5:
                self.passes.append(
                    f"{file_name}: Requirements appear atomic (IDs: {len(id_matches)}, shall: {len(shall_matches)})"
                )
            elif ratio > 1.5:
                self.warnings.append(
                    f"{file_name}: Requirements may not be atomic - multiple 'shall' per ID"
                )
