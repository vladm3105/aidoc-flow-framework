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
            output_dir: Output directory (default: doc_path/.ucx_review_session)
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
            # Default to .ucx_review_session (consistent with UCX review session storage)
            if doc_path.is_dir():
                output_dir = doc_path / ".ucx_review_session"
            else:
                output_dir = doc_path.parent / ".ucx_review_session"

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
        1. {project_dir}/.ucx/skills/{persona}.md (hidden config)
        2. {project_dir}/docs/UCX/skills/{persona}.md (standard project docs)
        3. UCX/skills/{persona}.md (framework default)

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

        # Project-specific locations (check both .ucx/ and docs/UCX/)
        if project_dir:
            skill_paths.append(project_dir / ".ucx" / "skills" / f"{persona}.md")
            skill_paths.append(project_dir / "docs" / "UCX" / "skills" / f"{persona}.md")

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

        # Extract Role section (v1.14.4: fixed to include nested ### sections)
        role_match = re.search(r'^## Role\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if role_match:
            instructions_parts.append(f"**Role**: {role_match.group(1).strip()}")

        # Extract Core Principles (if exists) - includes nested ### sections like CAP Theorem, Scalability
        principles_match = re.search(r'^## Core.*?Principles\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if principles_match:
            instructions_parts.append(f"\n**Principles**:\n{principles_match.group(1).strip()}")

        # Extract Review Focus (v1.14.4: fixed pattern)
        focus_match = re.search(r'^## Review Focus\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if focus_match:
            instructions_parts.append(f"\n**Review Focus**:\n{focus_match.group(1).strip()}")

        # Extract Quality Criteria (v1.14.4: fixed pattern)
        quality_match = re.search(r'^## Quality Criteria\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if quality_match:
            instructions_parts.append(f"\n**Quality Criteria**:\n{quality_match.group(1).strip()}")

        # Extract Category Tagging
        category_match = re.search(r'^## Category Tagging.*?\n([\s\S]*?)(?=\n## Scoring|\Z)', skill_content, re.MULTILINE)
        if category_match:
            instructions_parts.append(f"\n**Finding Categories**:\n{category_match.group(1).strip()}")

        # Extract Anti-Patterns (if exists) - matches various naming patterns
        # Use (?=\n## [^#]|\Z) to stop at next H2 but not H3/H4 subsections
        antipattern_match = re.search(r'^##\s+.*Anti-Patterns.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if antipattern_match:
            instructions_parts.append(f"\n**Anti-Patterns to Flag**:\n{antipattern_match.group(1).strip()}")

        # Extract Business Processes (domain-specific workflows)
        process_match = re.search(r'^##\s+.*Business Process.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if process_match:
            instructions_parts.append(f"\n**Business Processes**:\n{process_match.group(1).strip()}")

        # Extract Stakeholders (domain context)
        stakeholder_match = re.search(r'^##\s+.*Stakeholders.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if stakeholder_match:
            instructions_parts.append(f"\n**Key Stakeholders**:\n{stakeholder_match.group(1).strip()}")

        # Extract Corridor/Domain-Specific Requirements
        corridor_match = re.search(r'^##\s+.*(?:Corridor|Domain).*?Requirements.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if corridor_match:
            instructions_parts.append(f"\n**Domain Requirements**:\n{corridor_match.group(1).strip()}")

        # Extract Review Questions (actionable checklist)
        questions_match = re.search(r'^##\s+Review Questions.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if questions_match:
            instructions_parts.append(f"\n**Review Questions**:\n{questions_match.group(1).strip()}")

        # Extract Analysis Checklist
        checklist_match = re.search(r'^##\s+Analysis Checklist.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if checklist_match:
            instructions_parts.append(f"\n**Analysis Checklist**:\n{checklist_match.group(1).strip()}")

        # Extract The 5 'C's or similar frameworks
        framework_match = re.search(r"^##\s+The 5\s*['\"]?C['\"]?s.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)", skill_content, re.MULTILINE)
        if framework_match:
            instructions_parts.append(f"\n**Quality Framework (5 C's)**:\n{framework_match.group(1).strip()}")

        # Extract Core Mission (chairperson synthesis goal)
        mission_match = re.search(r'^##\s+Core Mission.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if mission_match:
            instructions_parts.append(f"\n**Core Mission**:\n{mission_match.group(1).strip()}")

        # Extract Prioritization Weights (severity/priority rules)
        weights_match = re.search(r'^##\s+.*Prioritization.*?Weights.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if weights_match:
            instructions_parts.append(f"\n**Prioritization Weights**:\n{weights_match.group(1).strip()}")

        # Extract Score Calculation (scoring formula and rules)
        scoring_match = re.search(r'^##\s+Score Calculation.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if scoring_match:
            instructions_parts.append(f"\n**Score Calculation**:\n{scoring_match.group(1).strip()}")

        # Extract Synthesis Process (step-by-step process)
        synthesis_match = re.search(r'^##\s+Synthesis Process.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if synthesis_match:
            instructions_parts.append(f"\n**Synthesis Process**:\n{synthesis_match.group(1).strip()}")

        # Extract Output Requirements (format specifications)
        output_match = re.search(r'^##\s+Output Requirements.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if output_match:
            instructions_parts.append(f"\n**Output Requirements**:\n{output_match.group(1).strip()}")

        # Extract CRITICAL sections (manifest requirements, etc.)
        critical_match = re.search(r'^##\s+.*CRITICAL.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if critical_match:
            instructions_parts.append(f"\n**CRITICAL REQUIREMENTS**:\n{critical_match.group(1).strip()}")

        # Extract Failure Scenarios (devil's advocate domain-specific failures)
        failure_match = re.search(r'^##\s+.*Failure.*?Scenarios.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if failure_match:
            instructions_parts.append(f"\n**Failure Scenarios**:\n{failure_match.group(1).strip()}")

        # Extract Edge Case Framework (boundary conditions, temporal issues)
        edge_match = re.search(r'^##\s+.*Edge Case.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if edge_match:
            instructions_parts.append(f"\n**Edge Case Framework**:\n{edge_match.group(1).strip()}")

        # Extract Critical Rule (essential constraints)
        rule_match = re.search(r'^##\s+Critical Rule.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if rule_match:
            instructions_parts.append(f"\n**Critical Rule**:\n{rule_match.group(1).strip()}")

        # Extract Verification Areas (fact checker domain-specific)
        verify_areas_match = re.search(r'^##\s+.*Verification.*?Areas.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if verify_areas_match:
            instructions_parts.append(f"\n**Verification Areas**:\n{verify_areas_match.group(1).strip()}")

        # Extract Verification Process (fact checker step-by-step)
        verify_process_match = re.search(r'^##\s+Verification Process.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if verify_process_match:
            instructions_parts.append(f"\n**Verification Process**:\n{verify_process_match.group(1).strip()}")

        # Extract Partner Ecosystem (integration lead partner details)
        partner_match = re.search(r'^##\s+Partner Ecosystem.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if partner_match:
            instructions_parts.append(f"\n**Partner Ecosystem**:\n{partner_match.group(1).strip()}")

        # Extract Integration Requirements Checklist
        integ_checklist_match = re.search(r'^##\s+Integration.*?(?:Requirements|Checklist).*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if integ_checklist_match:
            instructions_parts.append(f"\n**Integration Requirements Checklist**:\n{integ_checklist_match.group(1).strip()}")

        # Extract Assessment Templates (partner assessment, compliance assessment)
        template_match = re.search(r'^##\s+.*Assessment.*?Template.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if template_match:
            instructions_parts.append(f"\n**Assessment Template**:\n{template_match.group(1).strip()}")

        # Extract Operational Requirements (SLIs, infrastructure, DR targets)
        ops_req_match = re.search(r'^##\s+Operational Requirements.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if ops_req_match:
            instructions_parts.append(f"\n**Operational Requirements**:\n{ops_req_match.group(1).strip()}")

        # Extract Operational Checklist (deployment, observability, alerting, runbooks)
        ops_checklist_match = re.search(r'^##\s+Operational Checklist.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if ops_checklist_match:
            instructions_parts.append(f"\n**Operational Checklist**:\n{ops_checklist_match.group(1).strip()}")

        # Extract MVP Definition (product owner scope, features, out-of-scope)
        mvp_match = re.search(r'^##\s+.*MVP.*?Definition.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if mvp_match:
            instructions_parts.append(f"\n**MVP Definition**:\n{mvp_match.group(1).strip()}")

        # Extract Acceptance Criteria Format (user story template, Given/When/Then)
        acceptance_match = re.search(r'^##\s+Acceptance Criteria.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if acceptance_match:
            instructions_parts.append(f"\n**Acceptance Criteria Format**:\n{acceptance_match.group(1).strip()}")

        # Extract Business Model (strategist corridor economics, unit economics)
        business_model_match = re.search(r'^##\s+.*Business Model.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if business_model_match:
            instructions_parts.append(f"\n**Business Model**:\n{business_model_match.group(1).strip()}")

        # Extract Competitive Landscape (direct competitors, differentiators)
        competitive_match = re.search(r'^##\s+Competitive Landscape.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if competitive_match:
            instructions_parts.append(f"\n**Competitive Landscape**:\n{competitive_match.group(1).strip()}")

        # Extract Financial Projections (key assumptions, break-even)
        financial_match = re.search(r'^##\s+Financial Projections.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if financial_match:
            instructions_parts.append(f"\n**Financial Projections**:\n{financial_match.group(1).strip()}")

        # Extract Scoring Weight (persona weight per doc type)
        scoring_weight_match = re.search(r'^##\s+Scoring Weight.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if scoring_weight_match:
            instructions_parts.append(f"\n**Scoring Weight**:\n{scoring_weight_match.group(1).strip()}")

        # Extract Technology Stack (tech lead core stack and domain-specific concerns)
        tech_stack_match = re.search(r'^##\s+Technology Stack.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if tech_stack_match:
            instructions_parts.append(f"\n**Technology Stack**:\n{tech_stack_match.group(1).strip()}")

        # Extract Technical Assessment (checklist for technical review)
        tech_assessment_match = re.search(r'^##\s+Technical Assessment.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if tech_assessment_match:
            instructions_parts.append(f"\n**Technical Assessment Checklist**:\n{tech_assessment_match.group(1).strip()}")

        # Extract BDD & Gherkin Standards (qa_lead syntax rules)
        bdd_match = re.search(r'^##\s+BDD.*?(?:Gherkin|Standards).*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if bdd_match:
            instructions_parts.append(f"\n**BDD & Gherkin Standards**:\n{bdd_match.group(1).strip()}")

        # Extract Test Coverage Requirements (qa_lead pyramid targets)
        coverage_match = re.search(r'^##\s+Test Coverage.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if coverage_match:
            instructions_parts.append(f"\n**Test Coverage Requirements**:\n{coverage_match.group(1).strip()}")

        # Extract Critical Test Scenarios (qa_lead priority scenarios)
        scenarios_match = re.search(r'^##\s+.*(?:Critical|Test).*?Scenarios.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if scenarios_match:
            instructions_parts.append(f"\n**Critical Test Scenarios**:\n{scenarios_match.group(1).strip()}")

        # Extract Layer-Specific Focus (qa_lead document focus)
        layer_focus_match = re.search(r'^##\s+Layer-Specific Focus.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if layer_focus_match:
            instructions_parts.append(f"\n**Layer-Specific Focus**:\n{layer_focus_match.group(1).strip()}")

        # Extract Testability Checklist (qa_lead verification items)
        testability_match = re.search(r'^##\s+Testability Checklist.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if testability_match:
            instructions_parts.append(f"\n**Testability Checklist**:\n{testability_match.group(1).strip()}")

        # Extract Quality Metrics (qa_lead SLIs and targets)
        quality_metrics_match = re.search(r'^##\s+Quality Metrics.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if quality_metrics_match:
            instructions_parts.append(f"\n**Quality Metrics**:\n{quality_metrics_match.group(1).strip()}")

        # Extract Scenario Anti-Patterns (qa_lead BDD anti-patterns)
        scenario_antipattern_match = re.search(r'^##\s+Scenario Anti-Patterns.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if scenario_antipattern_match:
            instructions_parts.append(f"\n**Scenario Anti-Patterns**:\n{scenario_antipattern_match.group(1).strip()}")

        # Extract EARS Testability Assessment (qa_lead requirements verification)
        ears_testability_match = re.search(r'^##\s+EARS Testability.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if ears_testability_match:
            instructions_parts.append(f"\n**EARS Testability Assessment**:\n{ears_testability_match.group(1).strip()}")

        # Extract TSPEC Quality Metrics (qa_lead test spec standards)
        tspec_metrics_match = re.search(r'^##\s+TSPEC Quality Metrics.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if tspec_metrics_match:
            instructions_parts.append(f"\n**TSPEC Quality Metrics**:\n{tspec_metrics_match.group(1).strip()}")

        # ============================================================
        # v1.14.4: Below-target persona extraction patterns
        # ============================================================

        # Extract Regulatory Framework Coverage (auditor compliance details)
        regulatory_match = re.search(r'^##\s+Regulatory Framework.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if regulatory_match:
            instructions_parts.append(f"\n**Regulatory Framework**:\n{regulatory_match.group(1).strip()}")

        # Extract Validation Checks (auditor explicit checklist)
        validation_checks_match = re.search(r'^##\s+Validation Checks.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if validation_checks_match:
            instructions_parts.append(f"\n**Validation Checks**:\n{validation_checks_match.group(1).strip()}")

        # Extract Common False Positive Patterns (fact_checker verification)
        false_positive_match = re.search(r'^##\s+Common False Positive.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if false_positive_match:
            instructions_parts.append(f"\n**Common False Positive Patterns**:\n{false_positive_match.group(1).strip()}")

        # Extract Synonym Mapping (fact_checker term lookup)
        synonym_match = re.search(r'^##\s+Synonym Mapping.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if synonym_match:
            instructions_parts.append(f"\n**Synonym Mapping**:\n{synonym_match.group(1).strip()}")

        # Extract Target Users (product_owner personas)
        target_users_match = re.search(r'^##\s+Target Users.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if target_users_match:
            instructions_parts.append(f"\n**Target Users**:\n{target_users_match.group(1).strip()}")

        # Extract Out of Scope (product_owner boundaries)
        out_of_scope_match = re.search(r'^##\s+.*(?:Out of Scope|Explicitly Out).*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if out_of_scope_match:
            instructions_parts.append(f"\n**Out of Scope**:\n{out_of_scope_match.group(1).strip()}")

        # Extract Core Mission (fact_checker, chairperson primary directive)
        core_mission_match = re.search(r'^##\s+Core Mission.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if core_mission_match:
            instructions_parts.append(f"\n**Core Mission**:\n{core_mission_match.group(1).strip()}")

        # Extract Where to Look (fact_checker reference locations)
        where_to_look_match = re.search(r'^##\s+Where to Look.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if where_to_look_match:
            instructions_parts.append(f"\n**Where to Look**:\n{where_to_look_match.group(1).strip()}")

        # Extract MVP Scope (product_owner corridor and features)
        mvp_scope_match = re.search(r'^##\s+MVP Scope.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if mvp_scope_match:
            instructions_parts.append(f"\n**MVP Scope**:\n{mvp_scope_match.group(1).strip()}")

        # ============================================================
        # v1.14.4b: Additional high-value extraction patterns
        # ============================================================

        # Extract Critical Compliance Gaps (auditor priority findings)
        critical_compliance_match = re.search(r'^##\s+Critical Compliance.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if critical_compliance_match:
            instructions_parts.append(f"\n**Critical Compliance Gaps**:\n{critical_compliance_match.group(1).strip()}")

        # Extract Corridor-Specific Requirements (auditor multi-jurisdiction)
        corridor_req_match = re.search(r'^##\s+Corridor-Specific Requirements.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if corridor_req_match:
            instructions_parts.append(f"\n**Corridor-Specific Requirements**:\n{corridor_req_match.group(1).strip()}")

        # Extract Critical MVP Boundaries (product_owner scope clarity)
        mvp_boundaries_match = re.search(r'^##\s+Critical MVP Boundaries.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if mvp_boundaries_match:
            instructions_parts.append(f"\n**Critical MVP Boundaries**:\n{mvp_boundaries_match.group(1).strip()}")

        # Extract User Journey Checkpoints (product_owner touchpoints)
        journey_match = re.search(r'^##\s+User Journey.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if journey_match:
            instructions_parts.append(f"\n**User Journey Checkpoints**:\n{journey_match.group(1).strip()}")

        # Extract High False Positive Categories (fact_checker common errors)
        false_pos_categories_match = re.search(r'^##\s+High False Positive.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if false_pos_categories_match:
            instructions_parts.append(f"\n**High False Positive Categories**:\n{false_pos_categories_match.group(1).strip()}")

        # Extract Verification Verdicts (fact_checker decision framework)
        verdicts_match = re.search(r'^##\s+Verification Verdicts.*?\n([\s\S]*?)(?=\n## [A-Z]|\Z)', skill_content, re.MULTILINE)
        if verdicts_match:
            instructions_parts.append(f"\n**Verification Verdicts**:\n{verdicts_match.group(1).strip()}")

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
