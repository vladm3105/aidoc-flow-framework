"""Prompt inspection for analyzing generated prompts.

This module provides the PromptInspector class for analyzing
prompt structure, section inclusion, and potential issues.

Version: 1.14.0
"""

import json
import re
from pathlib import Path
from typing import Optional

from ucx.prompts.models import (
    InspectionResult,
    PromptMetadata,
    PromptSection,
)
from ucx.prompts.exceptions import (
    MetadataNotFoundError,
    PromptFileNotFoundError,
)


# Patterns for heuristic structure detection
STRUCTURE_PATTERNS = {
    "system_instructions": [
        r"^You are",
        r"^As an? (expert|senior|experienced)",
        r"^Your (role|task|job) is",
        r"^I need you to",
    ],
    "persona_definition": [
        r"^## \d+\. THE [A-Z]",
        r"^### (PERSONA|ROLE):",
        r"^## (Architect|Auditor|Tech Lead|Strategist|Devil|Operator|Integration|Product|Business|Fact|Chair)",
        r"^# PERSONA:",
    ],
    "prior_context": [
        r"^## PRIOR (FINDINGS|CONTEXT|REVIEWS)",
        r"^### Previous Persona",
        r"^The following personas have",
        r"^## FINDINGS FROM PREVIOUS",
    ],
    "document_content": [
        r"^# (DOCUMENT|FILE|SECTION)",
        r"^## File: ",
        r"^# Section: [A-Z]+-\d+",
        r"^# DOCUMENT CONTENT",
    ],
    "format_instructions": [
        r"^## (OUTPUT|FORMAT|RESPONSE) (FORMAT|REQUIREMENTS|STRUCTURE)",
        r"^### Required Output",
        r"^You MUST (format|structure|output)",
        r"^## CRITICAL FORMATTING",
        r"^# OUTPUT REQUIREMENTS",
    ],
}

# Patterns for detecting priority markers
PRIORITY_PATTERNS = [
    r"P0|P1|P2",
    r"\[CRITICAL\]|\[HIGH\]|\[MEDIUM\]|\[LOW\]",
    r"MUST|SHOULD|MAY",
    r"Priority:",
]


class PromptInspector:
    """Analyze generated prompt structure and content.

    The inspector can work in two modes:
    1. With metadata: Uses .meta.json file for accurate section info
    2. Heuristic mode: Detects structure using regex patterns

    Example:
        inspector = PromptInspector()
        result = inspector.inspect(Path("tmp/prompts/prompt_architect.txt"))
        print(f"Total tokens: {result.total_tokens}")
        print(f"Warnings: {result.warnings}")
    """

    def __init__(self):
        """Initialize PromptInspector."""
        self._structure_patterns = {
            name: [re.compile(p, re.IGNORECASE) for p in patterns]
            for name, patterns in STRUCTURE_PATTERNS.items()
        }
        self._priority_patterns = [
            re.compile(p, re.IGNORECASE) for p in PRIORITY_PATTERNS
        ]

    def inspect(self, prompt_path: Path) -> InspectionResult:
        """Inspect a prompt file.

        Args:
            prompt_path: Path to prompt file

        Returns:
            InspectionResult with analysis

        Raises:
            PromptFileNotFoundError: If prompt file doesn't exist
        """
        prompt_path = Path(prompt_path)

        if not prompt_path.exists():
            raise PromptFileNotFoundError(prompt_path)

        # Read prompt content
        content = prompt_path.read_text(encoding="utf-8")

        # Try to load metadata
        metadata = self._load_metadata(prompt_path)

        if metadata:
            return self._inspect_with_metadata(prompt_path, content, metadata)
        else:
            return self._inspect_heuristic(prompt_path, content)

    def _load_metadata(self, prompt_path: Path) -> Optional[PromptMetadata]:
        """Load metadata file if it exists.

        Args:
            prompt_path: Path to prompt file

        Returns:
            PromptMetadata or None if not found
        """
        # Try .meta.json extension
        meta_path = prompt_path.with_suffix(".meta.json")
        if not meta_path.exists():
            # Try replacing .txt with .meta.json
            meta_path = prompt_path.parent / (prompt_path.stem + ".meta.json")

        if not meta_path.exists():
            return None

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return PromptMetadata.from_json(data)
        except (json.JSONDecodeError, KeyError):
            return None

    def _inspect_with_metadata(
        self, prompt_path: Path, content: str, metadata: PromptMetadata
    ) -> InspectionResult:
        """Inspect prompt using metadata file.

        Args:
            prompt_path: Path to prompt file
            content: Prompt content
            metadata: Loaded metadata

        Returns:
            InspectionResult
        """
        lines = content.split("\n")
        total_chars = len(content)
        total_tokens = metadata.tokens.get("total", total_chars // 4)

        # Build structure from metadata
        structure = []
        for section_name, section_info in metadata.structure.items():
            structure.append(
                PromptSection(
                    name=section_name,
                    start_line=section_info.get("start", 0),
                    end_line=section_info.get("end", 0),
                    char_count=0,  # Would need to calculate
                    token_estimate=section_info.get("tokens", 0),
                )
            )

        # Get sections from metadata
        sections_included = metadata.sections.get("included", [])
        sections_skipped = metadata.sections.get("skipped", [])
        sections_index_only = metadata.sections.get("index_only", [])

        # Find largest section
        largest_section, largest_pct = self._find_largest_section(
            content, sections_included
        )

        # Generate warnings
        warnings = self._generate_warnings(
            content,
            total_tokens,
            largest_section,
            largest_pct,
            sections_index_only,
        )

        # Check attention steering
        format_position = self._detect_format_position(lines)
        has_priority = self._has_priority_markers(content)

        return InspectionResult(
            persona=metadata.persona,
            prompt_path=prompt_path,
            total_chars=total_chars,
            total_tokens=total_tokens,
            structure=structure,
            sections_included=sections_included,
            sections_skipped=sections_skipped,
            sections_index_only=sections_index_only,
            largest_section=largest_section,
            largest_section_pct=largest_pct,
            warnings=warnings,
            format_position=format_position,
            has_priority_markers=has_priority,
            has_metadata=True,
        )

    def _inspect_heuristic(
        self, prompt_path: Path, content: str
    ) -> InspectionResult:
        """Inspect prompt using heuristic detection.

        Args:
            prompt_path: Path to prompt file
            content: Prompt content

        Returns:
            InspectionResult
        """
        lines = content.split("\n")
        total_chars = len(content)
        total_tokens = total_chars // 4

        # Detect structure
        structure = self._detect_structure(lines)

        # Extract persona from filename
        persona = self._extract_persona_from_path(prompt_path)

        # Find section references in content
        sections_included = self._find_section_references(content)

        # Find largest section
        largest_section, largest_pct = self._find_largest_section(
            content, sections_included
        )

        # Generate warnings
        warnings = self._generate_warnings(
            content,
            total_tokens,
            largest_section,
            largest_pct,
            [],  # Can't know index-only without metadata
        )

        # Add warning about heuristic mode
        warnings.insert(
            0, "Using heuristic detection - skipped sections not available"
        )

        # Check attention steering
        format_position = self._detect_format_position(lines)
        has_priority = self._has_priority_markers(content)

        return InspectionResult(
            persona=persona,
            prompt_path=prompt_path,
            total_chars=total_chars,
            total_tokens=total_tokens,
            structure=structure,
            sections_included=sections_included,
            sections_skipped=[],  # Can't determine without metadata
            sections_index_only=[],
            largest_section=largest_section,
            largest_section_pct=largest_pct,
            warnings=warnings,
            format_position=format_position,
            has_priority_markers=has_priority,
            has_metadata=False,
        )

    def _detect_structure(self, lines: list[str]) -> list[PromptSection]:
        """Detect prompt structure using heuristic patterns.

        Args:
            lines: Lines of prompt content

        Returns:
            List of detected PromptSections
        """
        sections = []
        current_section = None
        current_start = 0
        current_chars = 0

        for i, line in enumerate(lines):
            detected = self._detect_section_type(line)
            if detected and detected != (current_section.name if current_section else None):
                # Save previous section
                if current_section:
                    current_section.end_line = i
                    current_section.char_count = current_chars
                    current_section.token_estimate = current_chars // 4
                    sections.append(current_section)

                # Start new section
                current_section = PromptSection(
                    name=detected,
                    start_line=i + 1,  # 1-indexed
                    end_line=0,
                    char_count=0,
                    token_estimate=0,
                )
                current_start = i
                current_chars = len(line)
            else:
                current_chars += len(line) + 1  # +1 for newline

        # Save last section
        if current_section:
            current_section.end_line = len(lines)
            current_section.char_count = current_chars
            current_section.token_estimate = current_chars // 4
            sections.append(current_section)

        return sections

    def _detect_section_type(self, line: str) -> Optional[str]:
        """Detect section type from a line.

        Args:
            line: Line to check

        Returns:
            Section type name or None
        """
        for section_type, patterns in self._structure_patterns.items():
            for pattern in patterns:
                if pattern.match(line.strip()):
                    return section_type
        return None

    def _find_section_references(self, content: str) -> list[str]:
        """Find section IDs referenced in content.

        Args:
            content: Prompt content

        Returns:
            List of section IDs found
        """
        # Pattern for section IDs like BRD-01.6, PRD-02.3
        pattern = r"([A-Z]+-\d+\.\d+(?:\.\d+)?)"
        matches = re.findall(pattern, content, re.IGNORECASE)
        return sorted(set(m.upper() for m in matches))

    def _find_largest_section(
        self, content: str, sections: list[str]
    ) -> tuple[str, float]:
        """Find the largest section by content size.

        Args:
            content: Full prompt content
            sections: List of section IDs

        Returns:
            tuple: (largest_section_id, percentage_of_total)
        """
        if not sections:
            return ("unknown", 0.0)

        total_len = len(content)
        largest = ""
        largest_len = 0

        for section_id in sections:
            # Find content between section markers
            pattern = rf"# Section: {re.escape(section_id)}.*?(?=# Section:|$)"
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                section_len = len(match.group(0))
                if section_len > largest_len:
                    largest = section_id
                    largest_len = section_len

        if largest and total_len > 0:
            return (largest, (largest_len / total_len) * 100)
        elif sections:
            return (sections[0], 0.0)
        else:
            return ("unknown", 0.0)

    def _generate_warnings(
        self,
        content: str,
        total_tokens: int,
        largest_section: str,
        largest_pct: float,
        index_only_sections: list[str],
    ) -> list[str]:
        """Generate warnings based on analysis.

        Args:
            content: Prompt content
            total_tokens: Total token count
            largest_section: Largest section ID
            largest_pct: Percentage of largest section
            index_only_sections: Sections with index-only content

        Returns:
            List of warning messages
        """
        warnings = []

        # Warn if one section dominates
        if largest_pct > 25:
            warnings.append(
                f"{largest_section} is {largest_pct:.0f}% of total - may dominate attention"
            )

        # Warn about token budget
        if total_tokens > 45000:
            warnings.append(
                f"High token count ({total_tokens:,}) - approaching typical limits"
            )

        # Warn about index-only sections
        if index_only_sections:
            sections_str = ", ".join(index_only_sections[:3])
            if len(index_only_sections) > 3:
                sections_str += f" (+{len(index_only_sections) - 3} more)"
            warnings.append(
                f"Appendix in index-only mode ({sections_str}) - use [VERIFY:] tags if citing"
            )

        return warnings

    def _detect_format_position(self, lines: list[str]) -> str:
        """Detect where format instructions appear.

        Args:
            lines: Lines of content

        Returns:
            "end", "start", "both", or "missing"
        """
        format_patterns = self._structure_patterns.get("format_instructions", [])

        at_start = False
        at_end = False

        # Check first 20% of lines
        start_lines = lines[: max(1, len(lines) // 5)]
        for line in start_lines:
            for pattern in format_patterns:
                if pattern.match(line.strip()):
                    at_start = True
                    break

        # Check last 20% of lines
        end_lines = lines[max(0, len(lines) - len(lines) // 5) :]
        for line in end_lines:
            for pattern in format_patterns:
                if pattern.match(line.strip()):
                    at_end = True
                    break

        if at_start and at_end:
            return "both"
        elif at_end:
            return "end"
        elif at_start:
            return "start"
        else:
            return "missing"

    def _has_priority_markers(self, content: str) -> bool:
        """Check if content has priority markers.

        Args:
            content: Prompt content

        Returns:
            True if priority markers found
        """
        for pattern in self._priority_patterns:
            if pattern.search(content):
                return True
        return False

    def _extract_persona_from_path(self, prompt_path: Path) -> str:
        """Extract persona name from prompt file path.

        Args:
            prompt_path: Path to prompt file

        Returns:
            Persona name
        """
        # Expected format: prompt_architect.txt
        name = prompt_path.stem
        if name.startswith("prompt_"):
            return name[7:]  # Remove "prompt_" prefix
        return name

    def format_result(self, result: InspectionResult) -> str:
        """Format inspection result for display.

        Args:
            result: InspectionResult to format

        Returns:
            Formatted string
        """
        lines = []
        lines.append(f"PROMPT INSPECTION: {result.persona}")
        lines.append("=" * 60)
        lines.append("")

        # Structure
        lines.append("Structure:")
        for section in result.structure:
            tokens_str = f"({section.token_estimate:,} tokens)"
            lines.append(
                f"  [Lines {section.start_line}-{section.end_line}] "
                f"{section.name:<25} {tokens_str}"
            )
        lines.append("  " + "-" * 55)
        lines.append(f"  TOTAL: {result.total_tokens:,} tokens")
        lines.append("")

        # Sections included
        lines.append("Document Sections Included:")
        for section in result.sections_included:
            lines.append(f"  ✓ {section}")
        for section in result.sections_skipped:
            lines.append(f"  ✗ {section} (skipped)")
        for section in result.sections_index_only:
            lines.append(f"  ⊙ {section} (index only)")
        lines.append("")

        # Warnings
        if result.warnings:
            lines.append("Potential Issues:")
            for warning in result.warnings:
                lines.append(f"  ⚠ {warning}")
            lines.append("")

        # Attention steering
        lines.append("Attention Steering:")
        format_status = "✓" if result.format_position == "end" else "⚠"
        lines.append(f"  {format_status} Format instructions at {result.format_position.upper()}")
        priority_status = "✓" if result.has_priority_markers else "✗"
        lines.append(f"  {priority_status} Priority markers {'present' if result.has_priority_markers else 'missing'}")

        return "\n".join(lines)
