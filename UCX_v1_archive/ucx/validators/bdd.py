"""BDD (Behavior-Driven Development) validator."""

import re
from pathlib import Path

from ucx.models.enums import DocType
from ucx.validators.base import BaseValidator
from ucx.validators.registry import register_validator


@register_validator(DocType.BDD)
class BDDValidator(BaseValidator):
    """Validator for BDD Specification Documents (Layer 4)."""

    REQUIRED_FRONTMATTER = ["title", "doc_id", "version", "status"]

    REQUIRED_SECTIONS = [
        "Feature",
        "Scenario",
    ]

    ELEMENT_ID_PATTERN = r"BDD\.\d+\.\d+\.\d+"

    TRACE_PATTERNS = [
        r"@ears:",
        r"@req:",
    ]

    # Gherkin keywords
    GHERKIN_KEYWORDS = {
        "feature": r"^\s*Feature:\s*",
        "scenario": r"^\s*Scenario:\s*",
        "scenario_outline": r"^\s*Scenario Outline:\s*",
        "given": r"^\s*Given\s+",
        "when": r"^\s*When\s+",
        "then": r"^\s*Then\s+",
        "and": r"^\s*And\s+",
        "but": r"^\s*But\s+",
        "examples": r"^\s*Examples:\s*",
        "background": r"^\s*Background:\s*",
    }

    def _validate_file(self, file_path: Path, content: str) -> None:
        """Validate a BDD file."""
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
            self.warnings.append(f"{file_name}: No BDD element IDs found")

        # Check traceability
        self.check_traceability(
            content,
            self.TRACE_PATTERNS,
            file_name,
        )

        # BDD-specific checks
        self._check_gherkin_structure(content, file_name)
        self._check_scenario_completeness(content, file_name)
        self._check_examples_table(content, file_name)

    def _check_gherkin_structure(self, content: str, file_name: str) -> None:
        """Check for Gherkin structure keywords."""
        found_keywords = {}
        for keyword, pattern in self.GHERKIN_KEYWORDS.items():
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                found_keywords[keyword] = len(matches)

        # Check required keywords
        if "feature" in found_keywords:
            self.passes.append(f"{file_name}: Contains Feature definition")
        else:
            self.errors.append(f"{file_name}: Missing Feature definition")

        if "scenario" in found_keywords or "scenario_outline" in found_keywords:
            count = found_keywords.get("scenario", 0) + found_keywords.get("scenario_outline", 0)
            self.passes.append(f"{file_name}: Contains {count} Scenario(s)")
        else:
            self.errors.append(f"{file_name}: No Scenarios defined")

        # Check for Given/When/Then
        gwt = ["given", "when", "then"]
        gwt_found = [k for k in gwt if k in found_keywords]
        if len(gwt_found) == 3:
            self.passes.append(f"{file_name}: Complete Given/When/Then structure")
        else:
            missing = [k for k in gwt if k not in found_keywords]
            self.warnings.append(f"{file_name}: Missing Gherkin steps: {', '.join(missing)}")

    def _check_scenario_completeness(self, content: str, file_name: str) -> None:
        """Check that each scenario has Given/When/Then."""
        scenarios = re.split(r"^\s*Scenario(?:\s+Outline)?:\s*", content, flags=re.MULTILINE | re.IGNORECASE)

        complete = 0
        incomplete = 0

        for i, scenario in enumerate(scenarios[1:], 1):  # Skip content before first Scenario
            # Check first section only (until next Scenario or end)
            section = scenario.split("Scenario")[0] if "Scenario" in scenario else scenario

            has_given = bool(re.search(r"^\s*Given\s+", section, re.MULTILINE | re.IGNORECASE))
            has_when = bool(re.search(r"^\s*When\s+", section, re.MULTILINE | re.IGNORECASE))
            has_then = bool(re.search(r"^\s*Then\s+", section, re.MULTILINE | re.IGNORECASE))

            if has_given and has_when and has_then:
                complete += 1
            else:
                incomplete += 1

        if complete > 0:
            self.passes.append(f"{file_name}: {complete} complete scenario(s)")
        if incomplete > 0:
            self.warnings.append(f"{file_name}: {incomplete} incomplete scenario(s)")

    def _check_examples_table(self, content: str, file_name: str) -> None:
        """Check for Examples tables in Scenario Outlines."""
        outlines = re.findall(r"Scenario Outline:", content, re.IGNORECASE)
        examples = re.findall(r"Examples:", content, re.IGNORECASE)

        if outlines and not examples:
            self.errors.append(
                f"{file_name}: Scenario Outline(s) without Examples table"
            )
        elif outlines and examples:
            self.passes.append(
                f"{file_name}: Scenario Outlines have Examples tables"
            )
