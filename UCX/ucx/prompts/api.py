"""UCX Prompt Phase API.

This module provides the UCPromptPhase class - the main API for
prompt inspection, token analysis, and section mapping.

Version: 1.14.1
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from ucx.prompts.document import DocumentLoader, preprocess_content
from ucx.prompts.inspector import PromptInspector
from ucx.prompts.analyzer import TokenAnalyzer, VALID_PERSONAS
from ucx.prompts.mapper import SectionMapper
from ucx.prompts.exceptions import (
    ConfigurationError,
    DocumentNotFoundError,
    PromptFileNotFoundError,
    PromptGenerationError,
    validate_doc_type,
    validate_persona,
    validate_personas,
)
from ucx.prompts.models import (
    CheckResult,
    GeneratedPrompt,
    GenerationResult,
    InspectionResult,
    PromptMetadata,
    SectionMatrix,
    TokenAnalysis,
)


# Valid output formats for API methods
VALID_OUTPUT_FORMATS = {"text", "json", "object", "csv"}


def _validate_output_format(output_format: str, valid_formats: set[str]) -> None:
    """Validate output format parameter.

    Args:
        output_format: Format to validate
        valid_formats: Set of valid formats for this method

    Raises:
        ConfigurationError: If format is invalid
    """
    if output_format not in valid_formats:
        raise ConfigurationError(
            f"Invalid output_format: '{output_format}'. "
            f"Valid formats: {', '.join(sorted(valid_formats))}"
        )


class UCPromptPhase:
    """Main API for UCX prompt inspection and analysis.

    Provides methods matching CLI commands:
    - generate: Generate prompts for personas
    - inspect: Inspect an existing prompt file
    - sections: Show section inclusion matrix
    - tokens: Show token analysis per persona
    - check: Validate document for prompt generation

    Example:
        from ucx.prompts import UCPromptPhase

        api = UCPromptPhase()

        # Analyze tokens
        result = api.tokens(Path("docs/01_BRD/BRD-01/"), "brd")
        print(f"Total tokens: {result.total_all_personas:,}")

        # Build section matrix
        matrix = api.sections(Path("docs/01_BRD/BRD-01/"), "brd")
        print(matrix.to_table())

        # Inspect generated prompt
        inspection = api.inspect(Path("tmp/prompts/prompt_architect.txt"))
        print(f"Tokens: {inspection.total_tokens:,}")

        # Check document validity
        check = api.check(Path("docs/01_BRD/BRD-01/"), "brd")
        print(f"Passed: {check.passed}")
    """

    def __init__(
        self,
        default_budget: int = 60000,
        use_dynamic_mapping: bool = True,
    ):
        """Initialize UCPromptPhase.

        Args:
            default_budget: Default token budget per persona
            use_dynamic_mapping: Use semantic category-based section mapping
        """
        self._default_budget = default_budget
        self._use_dynamic_mapping = use_dynamic_mapping
        self._loader = DocumentLoader()
        self._inspector = PromptInspector()

    # =========================================================================
    # Core API Methods
    # =========================================================================

    def tokens(
        self,
        doc_path: Union[str, Path],
        doc_type: str,
        personas: Optional[list[str]] = None,
        output_format: str = "text",
    ) -> Union[TokenAnalysis, str, dict]:
        """Analyze token usage per persona.

        Args:
            doc_path: Path to document file or directory
            doc_type: Document type (brd, prd, etc.)
            personas: List of personas (default: all)
            output_format: "text", "json", or "object"

        Returns:
            TokenAnalysis, formatted string, or dict based on output_format

        Raises:
            ConfigurationError: If output_format is invalid
        """
        _validate_output_format(output_format, {"text", "json", "object"})

        doc_path = Path(doc_path)
        doc_type = validate_doc_type(doc_type)

        if personas:
            personas = validate_personas(personas)

        # Load document
        _, sections, _ = self._loader.load(doc_path, doc_type)

        # Analyze tokens
        analyzer = TokenAnalyzer(
            sections,
            use_dynamic_mapping=self._use_dynamic_mapping,
            token_budget=self._default_budget,
        )
        result = analyzer.analyze(doc_path, doc_type, personas)

        # Return in requested format
        if output_format == "json":
            return self._token_analysis_to_json(result)
        elif output_format == "text":
            return analyzer.format_result(result)
        else:
            return result

    def sections(
        self,
        doc_path: Union[str, Path],
        doc_type: str,
        personas: Optional[list[str]] = None,
        output_format: str = "text",
    ) -> Union[SectionMatrix, str, dict]:
        """Build section inclusion matrix.

        Args:
            doc_path: Path to document file or directory
            doc_type: Document type (brd, prd, etc.)
            personas: List of personas (default: all)
            output_format: "text", "json", "csv", or "object"

        Returns:
            SectionMatrix, formatted string, or dict based on output_format

        Raises:
            ConfigurationError: If output_format is invalid
        """
        _validate_output_format(output_format, {"text", "json", "csv", "object"})

        doc_path = Path(doc_path)
        doc_type = validate_doc_type(doc_type)

        if personas:
            personas = validate_personas(personas)

        # Load document
        _, sections, _ = self._loader.load(doc_path, doc_type)

        # Build matrix
        mapper = SectionMapper(
            sections,
            use_dynamic_mapping=self._use_dynamic_mapping,
        )
        result = mapper.build_matrix(doc_path, doc_type, personas)

        # Return in requested format
        if output_format == "json":
            return result.to_json()
        elif output_format == "csv":
            return result.to_csv()
        elif output_format == "text":
            return mapper.format_matrix(result)
        else:
            return result

    def inspect(
        self,
        prompt_path: Union[str, Path],
        output_format: str = "text",
    ) -> Union[InspectionResult, str, dict]:
        """Inspect a generated prompt file.

        Args:
            prompt_path: Path to prompt file
            output_format: "text", "json", or "object"

        Returns:
            InspectionResult, formatted string, or dict based on output_format

        Raises:
            ConfigurationError: If output_format is invalid
        """
        _validate_output_format(output_format, {"text", "json", "object"})

        prompt_path = Path(prompt_path)
        result = self._inspector.inspect(prompt_path)

        # Return in requested format
        if output_format == "json":
            return self._inspection_result_to_json(result)
        elif output_format == "text":
            return self._inspector.format_result(result)
        else:
            return result

    def check(
        self,
        doc_path: Union[str, Path],
        doc_type: str,
        strict: bool = False,
        personas: Optional[list[str]] = None,
    ) -> CheckResult:
        """Validate document for prompt generation.

        Args:
            doc_path: Path to document file or directory
            doc_type: Document type (brd, prd, etc.)
            strict: Exit with error if any persona exceeds budget
            personas: List of personas to check (default: all)

        Returns:
            CheckResult with validation status
        """
        doc_path = Path(doc_path)
        doc_type = validate_doc_type(doc_type)

        if personas:
            personas = validate_personas(personas)
        else:
            personas = VALID_PERSONAS

        warnings = []
        errors = []

        # Load document
        try:
            content, sections, section_tokens = self._loader.load(doc_path, doc_type)
        except DocumentNotFoundError as e:
            return CheckResult(
                doc_path=doc_path,
                doc_type=doc_type,
                passed=False,
                section_count=0,
                document_chars=0,
                personas_in_budget=0,
                personas_total=len(personas),
                errors=[str(e)],
                exit_code=1,
            )

        # Check section count
        if len(sections) == 0:
            errors.append("No sections found in document")
        elif len(sections) < 3:
            warnings.append(f"Only {len(sections)} sections found (expected 5+)")

        # Check document size
        doc_chars = sum(len(c) for c in sections.values())
        if doc_chars < 1000:
            warnings.append(f"Document is very small ({doc_chars:,} chars)")
        elif doc_chars > 500000:
            warnings.append(f"Document is very large ({doc_chars:,} chars)")

        # Analyze tokens
        analyzer = TokenAnalyzer(
            sections,
            use_dynamic_mapping=self._use_dynamic_mapping,
            token_budget=self._default_budget,
        )
        token_result = analyzer.analyze(doc_path, doc_type, personas)

        # Check budget status
        personas_in_budget = len(personas) - len(token_result.budget_exceeded)

        if token_result.budget_exceeded:
            msg = f"{len(token_result.budget_exceeded)} persona(s) exceed token budget"
            if strict:
                errors.append(msg)
            else:
                warnings.append(msg)

        for persona in token_result.budget_exceeded:
            tokens = token_result.per_persona[persona]
            overage = tokens.total_tokens - self._default_budget
            detail = f"{persona}: {tokens.total_tokens:,} tokens (+{overage:,} over budget)"
            if strict:
                errors.append(detail)
            else:
                warnings.append(detail)

        # Determine pass/fail
        passed = len(errors) == 0
        exit_code = 0 if passed else 1

        return CheckResult(
            doc_path=doc_path,
            doc_type=doc_type,
            passed=passed,
            section_count=len(sections),
            document_chars=doc_chars,
            personas_in_budget=personas_in_budget,
            personas_total=len(personas),
            warnings=warnings,
            errors=errors,
            exit_code=exit_code,
        )

    def generate(
        self,
        doc_path: Union[str, Path],
        doc_type: str,
        personas: Optional[list[str]] = None,
        output_dir: Optional[Union[str, Path]] = None,
        include_metadata: bool = True,
    ) -> GenerationResult:
        """Generate prompts for personas.

        This method generates prompt files by combining:
        - System instructions from skill manifests
        - Persona-filtered document sections
        - Prior context (if available)
        - Output format requirements

        Args:
            doc_path: Path to document file or directory
            doc_type: Document type (brd, prd, etc.)
            personas: List of personas (default: all)
            output_dir: Output directory (default: doc_path/.doc_review_memory)
            include_metadata: Generate .meta.json alongside prompts

        Returns:
            GenerationResult with generated prompts
        """
        doc_path = Path(doc_path)
        doc_type = validate_doc_type(doc_type)

        if personas:
            personas = validate_personas(personas)
        else:
            personas = VALID_PERSONAS

        # Determine output directory
        if output_dir:
            output_dir = Path(output_dir)
        else:
            # Default to .doc_review_memory (consistent with UCX review session storage)
            if doc_path.is_dir():
                output_dir = doc_path / ".doc_review_memory"
            else:
                output_dir = doc_path.parent / ".doc_review_memory"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Load document with preprocessing (strip YAML, comments, navigation, metadata)
        content, sections, section_tokens = self._loader.load_preprocessed(
            doc_path, doc_type,
            strip_frontmatter=True,
            strip_comments=True,
            strip_navigation=True,
            strip_metadata=True
        )

        # Build section mapper for filtering
        mapper = SectionMapper(
            sections,
            use_dynamic_mapping=self._use_dynamic_mapping,
        )
        matrix = mapper.build_matrix(doc_path, doc_type, personas)

        # Generate prompts
        prompts = []
        errors = []
        total_tokens = 0
        document_tokens = sum(section_tokens.values())

        for persona in personas:
            try:
                generated = self._generate_persona_prompt(
                    persona=persona,
                    doc_path=doc_path,
                    doc_type=doc_type,
                    sections=sections,
                    section_tokens=section_tokens,
                    matrix=matrix,
                    output_dir=output_dir,
                    include_metadata=include_metadata,
                )
                prompts.append(generated)
                total_tokens += generated.token_estimate
            except Exception as e:
                errors.append(f"{persona}: {str(e)}")

        return GenerationResult(
            doc_path=doc_path,
            doc_type=doc_type,
            output_dir=output_dir,
            prompts=prompts,
            total_tokens=total_tokens,
            document_tokens=document_tokens,
            config={
                "use_dynamic_mapping": self._use_dynamic_mapping,
                "default_budget": self._default_budget,
                "include_metadata": include_metadata,
            },
            errors=errors,
        )

    # =========================================================================
    # Private Methods
    # =========================================================================

    def _generate_persona_prompt(
        self,
        persona: str,
        doc_path: Path,
        doc_type: str,
        sections: dict[str, str],
        section_tokens: dict[str, int],
        matrix: SectionMatrix,
        output_dir: Path,
        include_metadata: bool,
    ) -> GeneratedPrompt:
        """Generate prompt for a single persona.

        Args:
            persona: Persona name
            doc_path: Document path
            doc_type: Document type
            sections: Section content dict
            section_tokens: Section token counts
            matrix: Section inclusion matrix
            output_dir: Output directory
            include_metadata: Generate metadata file

        Returns:
            GeneratedPrompt with generated content
        """
        # Get section status for this persona
        included = []
        skipped = []
        index_only = []

        for section_id in matrix.sections:
            status = matrix.matrix.get(section_id, {}).get(persona, "-")
            if status == "FULL":
                included.append(section_id)
            elif status == "OPT":
                included.append(section_id)
            elif status == "IDX":
                index_only.append(section_id)
            else:
                skipped.append(section_id)

        # Build prompt content
        content_parts = []

        # Header
        content_parts.append(f"# UCX Review Prompt: {persona.upper()}")
        content_parts.append(f"# Document: {doc_path.name}")
        content_parts.append(f"# Type: {doc_type.upper()}")
        content_parts.append(f"# Generated: {datetime.now().isoformat()}")
        content_parts.append("")
        content_parts.append("=" * 60)
        content_parts.append("")

        # Load system instructions from skill manifest
        # Detect project directory for custom skills
        project_dir = self._find_project_root(doc_path)

        content_parts.append("## SYSTEM INSTRUCTIONS")
        content_parts.append("")
        system_instructions = self._load_system_instructions(persona, doc_type, project_dir)
        content_parts.append(system_instructions)
        content_parts.append("")

        # Document sections (sorted by numeric order, not alphabetically)
        content_parts.append("## DOCUMENT CONTENT")
        content_parts.append("")

        for section_id in sorted(included, key=self._section_sort_key):
            if section_id in sections:
                content_parts.append(f"# Section: {section_id}")
                content_parts.append("")
                content_parts.append(sections[section_id])
                content_parts.append("")
                content_parts.append("---")
                content_parts.append("")

        # Index-only sections
        if index_only:
            content_parts.append("## APPENDIX INDEX (Reference Only)")
            content_parts.append("")
            content_parts.append("The following sections are available but not included in full.")
            content_parts.append("Use [VERIFY: section-id] tags to request specific content.")
            content_parts.append("")
            for section_id in sorted(index_only, key=self._section_sort_key):
                if section_id in sections:
                    # Get first line as title
                    first_line = sections[section_id].split("\n")[0].lstrip("#").strip()
                    tokens = section_tokens.get(section_id, 0)
                    content_parts.append(f"- {section_id}: {first_line[:50]}... ({tokens:,} tokens)")
            content_parts.append("")

        # Output format
        content_parts.append("## OUTPUT REQUIREMENTS")
        content_parts.append("")
        content_parts.append("Format your findings as structured markdown with:")
        content_parts.append("- Finding IDs following the pattern: {PREFIX}-{PRIORITY}-{NUM}")
        content_parts.append("- Priority levels: P0 (Critical), P1 (High), P2 (Medium)")
        content_parts.append("- Clear recommendations with specific locations")
        content_parts.append("")

        # Build final content
        content = "\n".join(content_parts)
        char_count = len(content)
        token_estimate = char_count // 4

        # Determine warnings
        warnings = []
        if token_estimate > self._default_budget:
            overage = token_estimate - self._default_budget
            warnings.append(f"Exceeds budget by {overage:,} tokens")
        if len(index_only) > 5:
            warnings.append(f"{len(index_only)} sections in index-only mode")

        # Write prompt file
        prompt_path = output_dir / f"prompt_{persona}.txt"
        prompt_path.write_text(content, encoding="utf-8")

        # Write metadata file
        if include_metadata:
            metadata = PromptMetadata(
                persona=persona,
                generated_at=datetime.now().isoformat(),
                doc_path=str(doc_path),
                doc_type=doc_type,
                config={
                    "use_dynamic_mapping": self._use_dynamic_mapping,
                    "default_budget": self._default_budget,
                },
                sections={
                    "included": included,
                    "skipped": skipped,
                    "index_only": index_only,
                },
                tokens={
                    "total": token_estimate,
                    "document": sum(section_tokens.get(s, 0) for s in included),
                    "instructions": token_estimate - sum(
                        section_tokens.get(s, 0) for s in included
                    ),
                },
                # TODO: Calculate actual structure metrics from generated content
                # Current values are estimates for MVP implementation
                structure={
                    "system_instructions": {"start": 1, "end": 10, "tokens": 500},
                    "document_content": {
                        "start": 11,
                        "end": len(content_parts) - 10,
                        "tokens": token_estimate - 1000,
                    },
                    "format_instructions": {
                        "start": len(content_parts) - 9,
                        "end": len(content_parts),
                        "tokens": 500,
                    },
                },
            )

            meta_path = output_dir / f"prompt_{persona}.meta.json"
            meta_path.write_text(
                json.dumps(metadata.to_json(), indent=2),
                encoding="utf-8",
            )

        return GeneratedPrompt(
            persona=persona,
            content=content,
            char_count=char_count,
            token_estimate=token_estimate,
            sections_included=included,
            sections_skipped=skipped,
            sections_index_only=index_only,
            warnings=warnings,
        )

    def _token_analysis_to_json(self, result: TokenAnalysis) -> dict:
        """Convert TokenAnalysis to JSON-serializable dict.

        Args:
            result: TokenAnalysis

        Returns:
            Dict representation
        """
        return {
            "doc_path": str(result.doc_path),
            "doc_type": result.doc_type,
            "document_chars": result.document_chars,
            "document_tokens": result.document_tokens,
            "token_method": result.token_method,
            "per_persona": {
                persona: {
                    "persona": tokens.persona,
                    "section_count": tokens.section_count,
                    "doc_tokens": tokens.doc_tokens,
                    "instruction_tokens": tokens.instruction_tokens,
                    "total_tokens": tokens.total_tokens,
                    "budget_status": tokens.budget_status,
                    "budget_pct": tokens.budget_pct,
                }
                for persona, tokens in result.per_persona.items()
            },
            "total_all_personas": result.total_all_personas,
            "savings_vs_no_ce": result.savings_vs_no_ce,
            "savings_pct": result.savings_pct,
            "budget": result.budget,
            "budget_exceeded": result.budget_exceeded,
            "budget_warnings": result.budget_warnings,
        }

    def _inspection_result_to_json(self, result: InspectionResult) -> dict:
        """Convert InspectionResult to JSON-serializable dict.

        Args:
            result: InspectionResult

        Returns:
            Dict representation
        """
        return {
            "persona": result.persona,
            "prompt_path": str(result.prompt_path),
            "total_chars": result.total_chars,
            "total_tokens": result.total_tokens,
            "structure": [
                {
                    "name": s.name,
                    "start_line": s.start_line,
                    "end_line": s.end_line,
                    "char_count": s.char_count,
                    "token_estimate": s.token_estimate,
                }
                for s in result.structure
            ],
            "sections_included": result.sections_included,
            "sections_skipped": result.sections_skipped,
            "sections_index_only": result.sections_index_only,
            "largest_section": result.largest_section,
            "largest_section_pct": result.largest_section_pct,
            "warnings": result.warnings,
            "format_position": result.format_position,
            "has_priority_markers": result.has_priority_markers,
            "has_metadata": result.has_metadata,
        }

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_document_info(
        self,
        doc_path: Union[str, Path],
        doc_type: str,
    ) -> dict:
        """Get basic document information.

        Args:
            doc_path: Path to document
            doc_type: Document type

        Returns:
            Dict with document info
        """
        doc_path = Path(doc_path)
        doc_type = validate_doc_type(doc_type)

        content, sections, tokens = self._loader.load(doc_path, doc_type)

        return {
            "path": str(doc_path),
            "type": doc_type,
            "is_directory": doc_path.is_dir(),
            "section_count": len(sections),
            "total_chars": len(content),
            "total_tokens": sum(tokens.values()),
            "sections": list(sections.keys()),
        }

    def list_personas(self) -> list[str]:
        """Get list of valid personas.

        Returns:
            List of persona names
        """
        return VALID_PERSONAS.copy()

    @staticmethod
    def _section_sort_key(section_id: str) -> tuple[int, int]:
        """Sort key for section IDs by numeric order.

        Ensures BRD-01.5 comes before BRD-01.11 (numeric, not alphabetic).

        Args:
            section_id: Section ID like "BRD-01.6" or "BRD-01.10"

        Returns:
            Tuple for sorting (main_num, sub_num)
        """
        import re
        match = re.search(r'\.(\d+)(?:\.(\d+))?$', section_id)
        if match:
            main = int(match.group(1))
            sub = int(match.group(2)) if match.group(2) else 0
            return (main, sub)
        return (999, 0)

    def _load_system_instructions(
        self,
        persona: str,
        doc_type: str,
        project_dir: Optional[Path] = None,
    ) -> str:
        """Load system instructions from skill manifest.

        Looks for skill files in order:
        1. {project_dir}/.ucx/skills/{persona}.md (project-specific)
        2. UCX/skills/{persona}.md (framework default)

        Args:
            persona: Persona name
            doc_type: Document type being reviewed
            project_dir: Optional project directory for custom templates

        Returns:
            System instructions string
        """
        import re

        # Default locations to check
        skill_paths = []

        # Project-specific first
        if project_dir:
            skill_paths.append(project_dir / ".ucx" / "skills" / f"{persona}.md")

        # Framework default
        ucx_root = Path(__file__).parent.parent.parent  # UCX root
        skill_paths.append(ucx_root / "skills" / f"{persona}.md")

        # Load first available skill file
        skill_content = None
        for skill_path in skill_paths:
            if skill_path.exists():
                try:
                    skill_content = skill_path.read_text(encoding="utf-8")
                    break
                except Exception:
                    continue

        if not skill_content:
            # Fallback to basic instructions
            return self._generate_basic_instructions(persona, doc_type)

        # Extract relevant sections from skill file
        instructions_parts = []

        # Extract Role section
        role_match = re.search(r'^## Role\n(.*?)(?=\n##|\Z)', skill_content, re.MULTILINE | re.DOTALL)
        if role_match:
            instructions_parts.append(f"**Role**: {role_match.group(1).strip()}")

        # Extract Core Principles (if exists)
        principles_match = re.search(r'^## Core.*?Principles\n(.*?)(?=\n##|\Z)', skill_content, re.MULTILINE | re.DOTALL)
        if principles_match:
            instructions_parts.append(f"\n**Principles**:\n{principles_match.group(1).strip()}")

        # Extract Review Focus
        focus_match = re.search(r'^## Review Focus\n(.*?)(?=\n##|\Z)', skill_content, re.MULTILINE | re.DOTALL)
        if focus_match:
            instructions_parts.append(f"\n**Review Focus**:\n{focus_match.group(1).strip()}")

        # Extract Quality Criteria
        quality_match = re.search(r'^## Quality Criteria\n(.*?)(?=\n##|\Z)', skill_content, re.MULTILINE | re.DOTALL)
        if quality_match:
            instructions_parts.append(f"\n**Quality Criteria**:\n{quality_match.group(1).strip()}")

        # Extract Category Tagging
        category_match = re.search(r'^## Category Tagging.*?\n(.*?)(?=\n## Scoring|\Z)', skill_content, re.MULTILINE | re.DOTALL)
        if category_match:
            instructions_parts.append(f"\n**Finding Categories**:\n{category_match.group(1).strip()}")

        # Extract Anti-Patterns (if exists) - matches various naming patterns
        antipattern_match = re.search(r'^##\s+.*Anti-Patterns.*?\n([\s\S]*?)(?=\n##|\Z)', skill_content, re.MULTILINE)
        if antipattern_match:
            instructions_parts.append(f"\n**Anti-Patterns to Flag**:\n{antipattern_match.group(1).strip()}")

        if instructions_parts:
            return "\n".join(instructions_parts)

        return self._generate_basic_instructions(persona, doc_type)

    def _generate_basic_instructions(self, persona: str, doc_type: str) -> str:
        """Generate basic fallback instructions when skill file not found.

        Args:
            persona: Persona name
            doc_type: Document type

        Returns:
            Basic instruction string
        """
        persona_title = persona.replace("_", " ").title()
        return f"""**Role**: {persona_title} reviewing {doc_type.upper()} document.

**Review Focus**:
- Evaluate document against {persona_title} domain expertise
- Identify gaps, inconsistencies, and improvement opportunities
- Provide actionable recommendations with specific locations

**Finding Format**:
Use the pattern: {{PREFIX}}-{{PRIORITY}}-{{NUM}}
- P0: Critical issues blocking progress
- P1: High priority issues requiring attention
- P2: Medium priority improvements"""

    @staticmethod
    def _find_project_root(doc_path: Path) -> Optional[Path]:
        """Find project root directory by looking for project markers.

        Looks for directories containing .ucx/, CLAUDE.md, .git, etc.

        Args:
            doc_path: Document path to start search from

        Returns:
            Project root path or None if not found
        """
        markers = [".ucx", "CLAUDE.md", ".git", "pyproject.toml", ".envrc"]
        current = doc_path if doc_path.is_dir() else doc_path.parent

        # Walk up the directory tree
        for _ in range(10):  # Limit depth to avoid infinite loops
            for marker in markers:
                if (current / marker).exists():
                    return current
            parent = current.parent
            if parent == current:  # Reached filesystem root
                break
            current = parent

        return None
