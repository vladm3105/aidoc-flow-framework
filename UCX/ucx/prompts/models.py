"""Data models for prompt inspection toolset.

This module defines dataclasses for prompt inspection results,
token analysis, and section mapping.

Version: 1.14.0
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class PromptSection:
    """A section within a prompt structure."""

    name: str  # e.g., "system_instructions", "document_content"
    start_line: int
    end_line: int
    char_count: int
    token_estimate: int


@dataclass
class InspectionResult:
    """Result of prompt inspection."""

    persona: str
    prompt_path: Path
    total_chars: int
    total_tokens: int

    # Structure breakdown
    structure: list[PromptSection]

    # Section analysis (from metadata or heuristics)
    sections_included: list[str]
    sections_skipped: list[str]
    sections_index_only: list[str]
    largest_section: str
    largest_section_pct: float

    # Issues detected
    warnings: list[str]

    # Attention steering
    format_position: str  # "end", "start", "both", "missing"
    has_priority_markers: bool

    # Metadata availability
    has_metadata: bool


@dataclass
class PersonaTokens:
    """Token breakdown for a single persona."""

    persona: str
    section_count: int
    doc_tokens: int
    instruction_tokens: int
    total_tokens: int
    budget_status: str  # "ok", "warning", "exceeded"
    budget_pct: float  # Percentage of budget used


@dataclass
class TokenAnalysis:
    """Result of token analysis across all personas."""

    doc_path: Path
    doc_type: str
    document_chars: int
    document_tokens: int
    token_method: str  # "chars" or "tiktoken"

    per_persona: dict[str, PersonaTokens]

    total_all_personas: int
    savings_vs_no_ce: int
    savings_pct: float

    budget: int
    budget_exceeded: list[str]  # Personas exceeding budget
    budget_warnings: list[str]  # Personas >80% of budget


@dataclass
class SectionMatrix:
    """Section inclusion matrix across all personas."""

    doc_path: Path
    doc_type: str
    sections: list[str]  # Row headers (section IDs)
    personas: list[str]  # Column headers
    matrix: dict[str, dict[str, str]]  # {section: {persona: "✓"|"✗"|"IDX"|"FULL"}}
    categories: dict[str, str]  # {section: category}
    category_confidence: dict[str, float]  # {section: confidence 0.0-1.0}

    def to_table(self) -> str:
        """Render as ASCII table."""
        if not self.sections or not self.personas:
            return "No data"

        # Calculate column widths
        section_width = max(len(s) for s in self.sections) + 2
        persona_width = 6  # Short names

        # Build header
        lines = []
        header = " " * section_width
        for p in self.personas:
            short_name = p[:5]
            header += f"{short_name:^{persona_width}}"
        lines.append(header)

        # Build rows
        for section in self.sections:
            row = f"{section:<{section_width}}"
            for persona in self.personas:
                status = self.matrix.get(section, {}).get(persona, "?")
                row += f"{status:^{persona_width}}"
            lines.append(row)

        return "\n".join(lines)

    def to_json(self) -> dict:
        """Export as JSON-serializable dict."""
        return {
            "doc_path": str(self.doc_path),
            "doc_type": self.doc_type,
            "sections": self.sections,
            "personas": self.personas,
            "matrix": self.matrix,
            "categories": self.categories,
            "category_confidence": self.category_confidence,
        }

    def to_csv(self) -> str:
        """Export as CSV."""
        lines = []
        # Header
        lines.append("section," + ",".join(self.personas))
        # Rows
        for section in self.sections:
            row = [section]
            for persona in self.personas:
                status = self.matrix.get(section, {}).get(persona, "?")
                row.append(status)
            lines.append(",".join(row))
        return "\n".join(lines)


@dataclass
class CheckResult:
    """Result of prompt check validation."""

    doc_path: Path
    doc_type: str
    passed: bool

    # Stats
    section_count: int
    document_chars: int
    personas_in_budget: int
    personas_total: int

    # Issues
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    # For CI/CD
    exit_code: int = 0

    def to_json(self) -> dict:
        """Export as JSON-serializable dict."""
        return {
            "doc_path": str(self.doc_path),
            "doc_type": self.doc_type,
            "passed": self.passed,
            "exit_code": self.exit_code,
            "stats": {
                "section_count": self.section_count,
                "document_chars": self.document_chars,
                "personas_in_budget": self.personas_in_budget,
                "personas_total": self.personas_total,
            },
            "warnings": self.warnings,
            "errors": self.errors,
        }


@dataclass
class GeneratedPrompt:
    """Result of generating a single persona prompt."""

    persona: str
    content: str
    char_count: int
    token_estimate: int
    sections_included: list[str]
    sections_skipped: list[str]
    sections_index_only: list[str]
    warnings: list[str] = field(default_factory=list)


@dataclass
class GenerationResult:
    """Result of generating prompts for all personas."""

    doc_path: Path
    doc_type: str
    output_dir: Optional[Path]
    prompts: list[GeneratedPrompt]
    total_tokens: int
    document_tokens: int
    config: dict
    errors: list[str] = field(default_factory=list)

    def to_json(self) -> dict:
        """Export as JSON-serializable dict."""
        return {
            "doc_path": str(self.doc_path),
            "doc_type": self.doc_type,
            "output_dir": str(self.output_dir) if self.output_dir else None,
            "prompts": [
                {
                    "persona": p.persona,
                    "char_count": p.char_count,
                    "token_estimate": p.token_estimate,
                    "sections_included": p.sections_included,
                    "warnings": p.warnings,
                }
                for p in self.prompts
            ],
            "total_tokens": self.total_tokens,
            "document_tokens": self.document_tokens,
            "config": self.config,
            "errors": self.errors,
        }


@dataclass
class PromptMetadata:
    """Metadata stored alongside generated prompts."""

    persona: str
    generated_at: str
    doc_path: str
    doc_type: str
    config: dict
    sections: dict  # {"included": [...], "skipped": [...], "index_only": [...]}
    tokens: dict  # {"total": int, "document": int, "instructions": int}
    structure: dict  # {"section_name": {"start": int, "end": int, "tokens": int}}

    def to_json(self) -> dict:
        """Export as JSON-serializable dict."""
        return {
            "persona": self.persona,
            "generated_at": self.generated_at,
            "doc_path": self.doc_path,
            "doc_type": self.doc_type,
            "config": self.config,
            "sections": self.sections,
            "tokens": self.tokens,
            "structure": self.structure,
        }

    @classmethod
    def from_json(cls, data: dict) -> "PromptMetadata":
        """Create from JSON dict."""
        return cls(
            persona=data["persona"],
            generated_at=data["generated_at"],
            doc_path=data["doc_path"],
            doc_type=data["doc_type"],
            config=data.get("config", {}),
            sections=data.get("sections", {}),
            tokens=data.get("tokens", {}),
            structure=data.get("structure", {}),
        )
