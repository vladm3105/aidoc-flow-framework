"""Section mapping for prompt inspection toolset.

This module provides the SectionMapper class for building
section inclusion matrices across personas.

Version: 1.14.0
"""

from pathlib import Path
from typing import Optional

from ucx.prompts.exceptions import validate_doc_type
from ucx.prompts.models import SectionMatrix

# Import context engine mappings
from ucx.core.context_engine import (
    DynamicSectionMapper,
    PERSONA_SECTION_MAP,
    PERSONA_CATEGORY_MAP,
    SECTION_CATEGORIES,
)


# All valid personas
VALID_PERSONAS = [
    "architect",
    "auditor",
    "tech_lead",
    "strategist",
    "chaos_engineer",  # Renamed from devils_advocate (v1.14.3)
    "operator",
    "integration_lead",
    "product_owner",
    "business_analyst",
    "fact_checker",
    "chairperson",
    "qa_lead",  # Added v1.14.3
]

# Section inclusion markers
MARKERS = {
    "required": "FULL",
    "optional": "OPT",
    "index_only": "IDX",
    "skip": "-",
}


class SectionMapper:
    """Build section inclusion matrix across personas.

    Shows which sections are included (FULL/OPT/IDX) or skipped (-)
    for each persona.

    Example:
        loader = DocumentLoader()
        content, sections, tokens = loader.load(Path("docs/01_BRD/BRD-01/"), "brd")

        mapper = SectionMapper(sections)
        matrix = mapper.build_matrix(Path("docs/01_BRD/BRD-01/"), "brd")

        print(matrix.to_table())
        print(matrix.to_csv())
    """

    def __init__(
        self,
        doc_sections: dict[str, str],
        use_dynamic_mapping: bool = True,
        doc_type: str = "brd",
    ):
        """Initialize SectionMapper.

        Args:
            doc_sections: Dict of {section_id: content}
            use_dynamic_mapping: Use dynamic category-based mapping
            doc_type: Document type for section categorization
        """
        self._sections = doc_sections
        self._use_dynamic_mapping = use_dynamic_mapping
        self._doc_type = doc_type

        # Initialize dynamic mapper if enabled
        if use_dynamic_mapping and doc_sections:
            self._dynamic_mapper = DynamicSectionMapper(doc_sections, doc_type)
        else:
            self._dynamic_mapper = None

    def build_matrix(
        self,
        doc_path: Path,
        doc_type: str,
        personas: Optional[list[str]] = None,
    ) -> SectionMatrix:
        """Build section inclusion matrix.

        Args:
            doc_path: Path to document (for metadata)
            doc_type: Document type (brd, prd, etc.)
            personas: List of personas (default: all)

        Returns:
            SectionMatrix with inclusion data
        """
        doc_type = validate_doc_type(doc_type)

        if personas is None:
            personas = VALID_PERSONAS

        # Get all section IDs sorted
        section_ids = sorted(self._sections.keys())

        # Build matrix
        matrix = {}
        categories = {}
        category_confidence = {}

        for section_id in section_ids:
            matrix[section_id] = {}

            # Get category info from dynamic mapper
            if self._dynamic_mapper:
                info = self._dynamic_mapper.get_section_info(section_id)
                if info:
                    categories[section_id] = info.category
                    category_confidence[section_id] = info.confidence
                else:
                    categories[section_id] = "unknown"
                    category_confidence[section_id] = 0.0
            else:
                categories[section_id] = self._guess_category_from_id(section_id)
                category_confidence[section_id] = 0.5

            # Check each persona
            for persona in personas:
                status = self._get_section_status(section_id, persona, doc_type)
                matrix[section_id][persona] = status

        return SectionMatrix(
            doc_path=doc_path,
            doc_type=doc_type,
            sections=section_ids,
            personas=personas,
            matrix=matrix,
            categories=categories,
            category_confidence=category_confidence,
        )

    def _get_section_status(
        self,
        section_id: str,
        persona: str,
        doc_type: str,
    ) -> str:
        """Get section status for persona.

        Args:
            section_id: Section ID
            persona: Persona name
            doc_type: Document type

        Returns:
            Status marker (FULL, OPT, IDX, -)
        """
        # Get mapping for persona
        if self._dynamic_mapper:
            mapping = self._dynamic_mapper.get_sections_for_persona(persona)
        else:
            mapping = self._get_static_mapping(persona, doc_type)

        # Check which list the section is in
        if section_id in mapping.get("required", []):
            return MARKERS["required"]
        elif section_id in mapping.get("optional", []):
            return MARKERS["optional"]
        elif section_id in mapping.get("skip", []):
            return MARKERS["skip"]
        else:
            # Not explicitly mapped - check if it's an appendix
            category = self._get_section_category(section_id)
            if category == "appendix":
                return MARKERS["index_only"]
            else:
                return MARKERS["skip"]

    def _get_static_mapping(self, persona: str, doc_type: str) -> dict[str, list[str]]:
        """Get static section mapping for persona.

        Args:
            persona: Persona name
            doc_type: Document type

        Returns:
            Dict with required/optional/skip section lists
        """
        mapping = PERSONA_SECTION_MAP.get(persona, {})
        return {
            "required": mapping.get("required", []),
            "optional": mapping.get("optional", []),
            "skip": mapping.get("skip", []),
        }

    def _get_section_category(self, section_id: str) -> str:
        """Get category for section.

        Args:
            section_id: Section ID

        Returns:
            Category name
        """
        if self._dynamic_mapper:
            info = self._dynamic_mapper.get_section_info(section_id)
            return info.category if info else "unknown"
        return self._guess_category_from_id(section_id)

    def _guess_category_from_id(self, section_id: str) -> str:
        """Guess category from section ID when no dynamic mapper.

        Args:
            section_id: Section ID like BRD-01.18

        Returns:
            Guessed category
        """
        # Extract section number
        parts = section_id.split(".")
        if len(parts) >= 2:
            try:
                section_num = int(parts[-1])
                # High-numbered sections are often appendices
                if section_num >= 15:
                    return "appendix"
                elif section_num >= 12:
                    return "metadata"
            except ValueError:
                pass
        return "other"

    def format_matrix(
        self,
        matrix: SectionMatrix,
        show_categories: bool = True,
    ) -> str:
        """Format section matrix for display.

        Args:
            matrix: SectionMatrix to format
            show_categories: Include category column

        Returns:
            Formatted ASCII table
        """
        lines = []
        lines.append("SECTION MATRIX")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Document: {matrix.doc_path}")
        lines.append(f"Type: {matrix.doc_type.upper()}")
        lines.append("")
        lines.append("Legend: FULL=Required, OPT=Optional, IDX=Index-only, -=Skipped")
        lines.append("")

        # Build header
        section_width = 12
        cat_width = 12 if show_categories else 0
        persona_width = 6

        header = f"{'Section':<{section_width}}"
        if show_categories:
            header += f"{'Category':<{cat_width}}"
        for p in matrix.personas:
            # Shorten persona names
            short = p[:5].upper()
            header += f"{short:^{persona_width}}"

        lines.append(header)
        lines.append("-" * len(header))

        # Build rows
        for section in matrix.sections:
            row = f"{section:<{section_width}}"

            if show_categories:
                cat = matrix.categories.get(section, "?")[:10]
                row += f"{cat:<{cat_width}}"

            for persona in matrix.personas:
                status = matrix.matrix.get(section, {}).get(persona, "?")
                row += f"{status:^{persona_width}}"

            lines.append(row)

        lines.append("")

        # Category confidence summary
        if show_categories:
            lines.append("Category Confidence:")
            low_confidence = [
                (s, c) for s, c in matrix.category_confidence.items()
                if c < 0.5
            ]
            if low_confidence:
                for section, conf in sorted(low_confidence):
                    lines.append(f"  {section}: {conf:.0%} (low confidence)")
            else:
                lines.append("  All sections categorized with high confidence")

        return "\n".join(lines)

    def get_persona_summary(
        self,
        matrix: SectionMatrix,
        persona: str,
    ) -> dict:
        """Get summary of sections for a specific persona.

        Args:
            matrix: SectionMatrix
            persona: Persona name

        Returns:
            Dict with section lists by status
        """
        result = {
            "required": [],
            "optional": [],
            "index_only": [],
            "skipped": [],
        }

        for section in matrix.sections:
            status = matrix.matrix.get(section, {}).get(persona, "-")
            if status == MARKERS["required"]:
                result["required"].append(section)
            elif status == MARKERS["optional"]:
                result["optional"].append(section)
            elif status == MARKERS["index_only"]:
                result["index_only"].append(section)
            else:
                result["skipped"].append(section)

        return result

    def get_section_coverage(self, matrix: SectionMatrix) -> dict:
        """Get coverage statistics for all sections.

        Args:
            matrix: SectionMatrix

        Returns:
            Dict with coverage stats per section
        """
        coverage = {}

        for section in matrix.sections:
            full_count = 0
            opt_count = 0
            idx_count = 0
            skip_count = 0

            for persona in matrix.personas:
                status = matrix.matrix.get(section, {}).get(persona, "-")
                if status == MARKERS["required"]:
                    full_count += 1
                elif status == MARKERS["optional"]:
                    opt_count += 1
                elif status == MARKERS["index_only"]:
                    idx_count += 1
                else:
                    skip_count += 1

            coverage[section] = {
                "full": full_count,
                "optional": opt_count,
                "index_only": idx_count,
                "skipped": skip_count,
                "total_personas": len(matrix.personas),
                "coverage_pct": (full_count + opt_count) / len(matrix.personas) * 100,
            }

        return coverage
