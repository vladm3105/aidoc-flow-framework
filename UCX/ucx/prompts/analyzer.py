"""Token analysis for prompt inspection toolset.

This module provides the TokenAnalyzer class for analyzing
token usage across personas and generating budget reports.

Version: 1.14.0
"""

from pathlib import Path
from typing import Optional

from ucx.prompts.document import DocumentLoader
from ucx.prompts.exceptions import (
    InvalidDocumentTypeError,
    validate_doc_type,
)
from ucx.prompts.models import (
    PersonaTokens,
    TokenAnalysis,
)

# Import context engine mappings for section filtering
from ucx.core.context_engine import (
    DynamicSectionMapper,
    PERSONA_SECTION_MAP,
    PERSONA_CATEGORY_MAP,
)


# Default token budgets per persona (tokens)
DEFAULT_TOKEN_BUDGET = 60000

# Per-persona budget adjustments (some need more context)
PERSONA_BUDGET_OVERRIDES = {
    "fact_checker": 100000,   # Needs ALL sections
    "chairperson": 100000,    # Needs ALL sections
    "architect": 70000,       # Complex technical analysis
    "tech_lead": 70000,       # Complex technical analysis
    "devils_advocate": 80000, # Edge case exploration
}

# Estimated instruction tokens per persona (system prompt + format)
PERSONA_INSTRUCTION_TOKENS = {
    "architect": 3500,
    "auditor": 4000,
    "tech_lead": 3000,
    "strategist": 3000,
    "devils_advocate": 3500,
    "operator": 3500,
    "integration_lead": 3500,
    "product_owner": 3000,
    "business_analyst": 3000,
    "fact_checker": 4000,
    "chairperson": 5000,
}

# All valid personas
VALID_PERSONAS = list(PERSONA_INSTRUCTION_TOKENS.keys())


class TokenAnalyzer:
    """Analyze token usage across all personas.

    Calculates token counts for each persona based on section mapping
    and compares against budgets.

    Example:
        loader = DocumentLoader()
        content, sections, tokens = loader.load(Path("docs/01_BRD/BRD-01/"), "brd")

        analyzer = TokenAnalyzer(sections)
        result = analyzer.analyze(Path("docs/01_BRD/BRD-01/"), "brd")

        print(f"Total tokens: {result.total_all_personas:,}")
        for p in result.budget_exceeded:
            print(f"  WARNING: {p} exceeds budget!")
    """

    def __init__(
        self,
        doc_sections: dict[str, str],
        use_dynamic_mapping: bool = True,
        token_budget: int = DEFAULT_TOKEN_BUDGET,
        doc_type: str = "brd",
    ):
        """Initialize TokenAnalyzer.

        Args:
            doc_sections: Dict of {section_id: content}
            use_dynamic_mapping: Use dynamic category-based mapping
            token_budget: Default token budget per persona
            doc_type: Document type for section categorization
        """
        self._sections = doc_sections
        self._use_dynamic_mapping = use_dynamic_mapping
        self._default_budget = token_budget
        self._doc_type = doc_type

        # Initialize dynamic mapper if enabled
        if use_dynamic_mapping and doc_sections:
            self._mapper = DynamicSectionMapper(doc_sections, doc_type)
        else:
            self._mapper = None

        # Pre-compute section token counts
        self._section_tokens = {
            section_id: self._estimate_tokens(content)
            for section_id, content in doc_sections.items()
        }

    def analyze(
        self,
        doc_path: Path,
        doc_type: str,
        personas: Optional[list[str]] = None,
    ) -> TokenAnalysis:
        """Analyze token usage across personas.

        Args:
            doc_path: Path to document (for metadata)
            doc_type: Document type (brd, prd, etc.)
            personas: List of personas to analyze (default: all)

        Returns:
            TokenAnalysis with breakdown per persona
        """
        doc_type = validate_doc_type(doc_type)

        if personas is None:
            personas = VALID_PERSONAS

        # Calculate document totals
        document_chars = sum(len(c) for c in self._sections.values())
        document_tokens = sum(self._section_tokens.values())

        # Calculate per-persona tokens
        per_persona = {}
        budget_exceeded = []
        budget_warnings = []

        for persona in personas:
            persona_tokens = self._calculate_persona_tokens(persona, doc_type)
            per_persona[persona] = persona_tokens

            if persona_tokens.budget_status == "exceeded":
                budget_exceeded.append(persona)
            elif persona_tokens.budget_status == "warning":
                budget_warnings.append(persona)

        # Calculate totals
        total_all_personas = sum(p.total_tokens for p in per_persona.values())

        # Calculate savings vs no context engineering
        # (no CE = every persona gets all sections)
        no_ce_tokens = document_tokens * len(personas)
        savings = no_ce_tokens - total_all_personas
        savings_pct = (savings / no_ce_tokens * 100) if no_ce_tokens > 0 else 0

        return TokenAnalysis(
            doc_path=doc_path,
            doc_type=doc_type,
            document_chars=document_chars,
            document_tokens=document_tokens,
            token_method="chars",  # chars/4 estimation
            per_persona=per_persona,
            total_all_personas=total_all_personas,
            savings_vs_no_ce=savings,
            savings_pct=savings_pct,
            budget=self._default_budget,
            budget_exceeded=budget_exceeded,
            budget_warnings=budget_warnings,
        )

    def _calculate_persona_tokens(
        self,
        persona: str,
        doc_type: str,
    ) -> PersonaTokens:
        """Calculate token usage for a single persona.

        Args:
            persona: Persona name
            doc_type: Document type

        Returns:
            PersonaTokens with breakdown
        """
        # Get section mapping
        if self._mapper:
            mapping = self._mapper.get_sections_for_persona(persona)
        else:
            mapping = self._get_static_mapping(persona, doc_type)

        # Calculate document tokens (required + optional sections)
        included_sections = mapping.get("required", []) + mapping.get("optional", [])
        doc_tokens = sum(
            self._section_tokens.get(s, 0)
            for s in included_sections
            if s in self._sections
        )

        # Get instruction tokens
        instruction_tokens = PERSONA_INSTRUCTION_TOKENS.get(persona, 3500)

        # Calculate total
        total_tokens = doc_tokens + instruction_tokens

        # Get budget for this persona
        budget = PERSONA_BUDGET_OVERRIDES.get(persona, self._default_budget)

        # Determine budget status
        budget_pct = (total_tokens / budget * 100) if budget > 0 else 0

        if total_tokens > budget:
            budget_status = "exceeded"
        elif budget_pct > 80:
            budget_status = "warning"
        else:
            budget_status = "ok"

        return PersonaTokens(
            persona=persona,
            section_count=len(included_sections),
            doc_tokens=doc_tokens,
            instruction_tokens=instruction_tokens,
            total_tokens=total_tokens,
            budget_status=budget_status,
            budget_pct=budget_pct,
        )

    def _get_static_mapping(self, persona: str, doc_type: str) -> dict[str, list[str]]:
        """Get static section mapping for persona.

        Args:
            persona: Persona name
            doc_type: Document type

        Returns:
            Dict with required/optional/skip section lists
        """
        # Use static mapping for BRD-01
        mapping = PERSONA_SECTION_MAP.get(persona, {})
        return {
            "required": mapping.get("required", []),
            "optional": mapping.get("optional", []),
            "skip": mapping.get("skip", []),
        }

    def _estimate_tokens(self, content: str) -> int:
        """Estimate token count from content.

        Args:
            content: Text content

        Returns:
            Estimated token count (chars/4)
        """
        return len(content) // 4

    def format_result(self, result: TokenAnalysis) -> str:
        """Format token analysis for display.

        Args:
            result: TokenAnalysis to format

        Returns:
            Formatted string
        """
        lines = []
        lines.append("TOKEN ANALYSIS")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Document: {result.doc_path}")
        lines.append(f"Type: {result.doc_type.upper()}")
        lines.append(f"Method: {result.token_method}")
        lines.append("")

        # Document summary
        lines.append("Document:")
        lines.append(f"  Characters: {result.document_chars:,}")
        lines.append(f"  Tokens: {result.document_tokens:,}")
        lines.append("")

        # Per-persona breakdown
        lines.append("Per-Persona Breakdown:")
        lines.append("-" * 60)
        lines.append(
            f"{'Persona':<20} {'Sections':>8} {'Doc':>8} "
            f"{'Instr':>6} {'Total':>8} {'Budget':>8}"
        )
        lines.append("-" * 60)

        for persona, tokens in sorted(result.per_persona.items()):
            status_marker = ""
            if tokens.budget_status == "exceeded":
                status_marker = " [!]"
            elif tokens.budget_status == "warning":
                status_marker = " [*]"

            budget = PERSONA_BUDGET_OVERRIDES.get(persona, result.budget)

            lines.append(
                f"{persona:<20} {tokens.section_count:>8} "
                f"{tokens.doc_tokens:>8,} {tokens.instruction_tokens:>6,} "
                f"{tokens.total_tokens:>8,} {budget:>8,}{status_marker}"
            )

        lines.append("-" * 60)
        lines.append(f"{'TOTAL':<20} {'':<8} {'':<8} {'':<6} "
                     f"{result.total_all_personas:>8,}")
        lines.append("")

        # Savings
        lines.append("Context Engineering Savings:")
        lines.append(f"  Without CE: {result.total_all_personas + result.savings_vs_no_ce:,} tokens")
        lines.append(f"  With CE: {result.total_all_personas:,} tokens")
        lines.append(f"  Savings: {result.savings_vs_no_ce:,} tokens ({result.savings_pct:.0f}%)")
        lines.append("")

        # Warnings
        if result.budget_exceeded:
            lines.append("Budget Exceeded:")
            for p in result.budget_exceeded:
                tokens = result.per_persona[p]
                budget = PERSONA_BUDGET_OVERRIDES.get(p, result.budget)
                overage = tokens.total_tokens - budget
                lines.append(f"  [!] {p}: +{overage:,} tokens over budget")
            lines.append("")

        if result.budget_warnings:
            lines.append("Budget Warnings (>80%):")
            for p in result.budget_warnings:
                tokens = result.per_persona[p]
                lines.append(f"  [*] {p}: {tokens.budget_pct:.0f}% of budget")
            lines.append("")

        return "\n".join(lines)
