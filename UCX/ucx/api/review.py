"""UCX Review (UCR) Phase API."""

import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from ucx.config.settings import UCXConfig
from ucx.config.layer_skills import get_skills_for_phase
from ucx.models.enums import DocType, ValidationStatus
from ucx.models.review import ReviewResult, ValidationResult
from ucx.exceptions import PromptError
from ucx.core.review_memory import ReviewMemory
from ucx.core.persona_prompts import (
    get_personas_for_doc_type,
    build_persona_prompt,
    get_persona_title,
    UnifiedPromptLoader,
    ProjectPromptNotFoundError,
    require_unified_prompt,
    generate_unified_prompt_template,
)
from ucx.prompts.loader import ProjectPromptNotFoundError as LoaderPromptNotFoundError
from ucx.utils.logging import (
    get_logger,
    log_phase_start,
    log_phase_end,
    log_review_result,
    log_timing,
)


class UCRPhase:
    """
    UCR (Unified Context Review) phase.

    Multi-persona document validation with integrated schema validation.

    Example:
        >>> from ucx import UCRPhase
        >>>
        >>> ucr = UCRPhase()
        >>> result = ucr.review("brd", "docs/01_BRD/BRD-01")
        >>> print(f"Score: {result.score}, Findings: {result.findings}")
    """

    def __init__(self, config: Optional[UCXConfig] = None):
        """
        Initialize UCR phase.

        Args:
            config: UCXConfig instance
        """
        self.config = config or UCXConfig()
        self._ai_client = None
        self._validators: dict[DocType, "BaseValidator"] = {}
        self.logger = get_logger("ucx.api.review")

        self.logger.debug(
            f"Initialized UCRPhase: ai_mode={self.config.ai_mode} "
            f"skip_validation={self.config.skip_validation}"
        )

    @property
    def ai_client(self):
        """Get AI client instance based on config (CLI or API mode)."""
        if self._ai_client is None:
            self._ai_client = self.config.get_ai_client()
            self.logger.debug(f"Created AI client: {type(self._ai_client).__name__}")
        return self._ai_client

    def _get_next_report_version(self, doc_path: Path, doc_type: DocType) -> int:
        """
        Get the next version number for a review report.

        Scans existing reports and returns the next available version.

        Args:
            doc_path: Path to document directory
            doc_type: Document type

        Returns:
            Next version number (1 if no existing reports)
        """
        # Extract doc_id from path (e.g., "BRD-01" from "BRD-01_platform_architecture")
        doc_id = self._extract_doc_id(doc_path, doc_type)

        # Pattern to match versioned reports: BRD-01.UCR_review_report_v001.md
        pattern = re.compile(
            rf"{re.escape(doc_id)}\.UCR_review_report_v(\d{{3}})\.md$"
        )

        max_version = 0
        search_dir = doc_path if doc_path.is_dir() else doc_path.parent

        for file in search_dir.glob(f"{doc_id}.UCR_review_report_v*.md"):
            match = pattern.match(file.name)
            if match:
                version = int(match.group(1))
                max_version = max(max_version, version)

        return max_version + 1

    def _extract_doc_id(self, doc_path: Path, doc_type: DocType) -> str:
        """
        Extract document ID from path.

        Examples:
            BRD-01_platform_architecture -> BRD-01
            PRD-02_user_features -> PRD-02

        Args:
            doc_path: Path to document
            doc_type: Document type

        Returns:
            Document ID string (e.g., "BRD-01")
        """
        doc_id_match = re.search(
            rf"({doc_type.value.upper()}-\d+)",
            str(doc_path),
            re.IGNORECASE
        )
        if doc_id_match:
            return doc_id_match.group(1).upper()
        return f"{doc_type.value.upper()}-XX"

    def _generate_review_id(self, doc_path: Path, doc_type: DocType, version: int) -> str:
        """
        Generate a unique review ID.

        Format: UCR-{DOC_ID}-v{NNN}
        Example: UCR-BRD-01-v001

        Args:
            doc_path: Path to document
            doc_type: Document type
            version: Version number

        Returns:
            Unique review ID string
        """
        doc_id = self._extract_doc_id(doc_path, doc_type)
        return f"UCR-{doc_id}-v{version:03d}"

    def _get_versioned_output_path(
        self,
        doc_path: Path,
        doc_type: DocType,
        output_path: Optional[Path] = None,
    ) -> tuple[Path, int, str]:
        """
        Get versioned output path for review report.

        Args:
            doc_path: Path to document
            doc_type: Document type
            output_path: Custom output path (if provided, version not added)

        Returns:
            Tuple of (output_path, version, review_id)
        """
        if output_path is not None:
            # Custom path provided - use version 1
            version = 1
            review_id = self._generate_review_id(doc_path, doc_type, version)
            return output_path, version, review_id

        # Generate versioned path
        version = self._get_next_report_version(doc_path, doc_type)
        review_id = self._generate_review_id(doc_path, doc_type, version)
        doc_id = self._extract_doc_id(doc_path, doc_type)

        # New naming format: {DOC_ID}.UCR_review_report_v{NNN}.md
        # Example: BRD-01.UCR_review_report_v001.md
        filename = f"{doc_id}.UCR_review_report_v{version:03d}.md"

        if doc_path.is_dir():
            versioned_path = doc_path / filename
        else:
            versioned_path = doc_path.parent / filename

        return versioned_path, version, review_id

    def review(
        self,
        doc_type: Union[str, DocType],
        doc_path: Union[str, Path],
        *,
        output_path: Optional[Path] = None,
        skip_validation: bool = False,
    ) -> ReviewResult:
        """
        Review a document.

        Args:
            doc_type: Document type (brd, prd, ears, etc.)
            doc_path: Path to document file or directory
            output_path: Custom output path for review report
            skip_validation: Skip validation phase

        Returns:
            ReviewResult with score, findings, and report path

        Raises:
            FileNotFoundError: If document not found
            PromptError: If prompt not found
        """
        start_time = time.perf_counter()

        # Normalize inputs
        if isinstance(doc_type, str):
            doc_type = DocType.from_string(doc_type)
        doc_path = Path(doc_path)

        # Log phase start
        log_phase_start("UCR", doc_type.value, str(doc_path))
        self.logger.info(f"Starting review: doc_type={doc_type.value} path={doc_path}")

        if not doc_path.exists():
            self.logger.error(f"Document not found: {doc_path}")
            raise FileNotFoundError(f"Document not found: {doc_path}")

        # Get versioned output path with review ID
        output_path, version, review_id = self._get_versioned_output_path(
            doc_path, doc_type, output_path
        )

        self.logger.debug(f"Output path: {output_path}")
        self.logger.info(f"Review ID: {review_id} (version {version})")

        # Phase 1: Validation
        validation_result = ValidationResult(status=ValidationStatus.SKIPPED)
        if not skip_validation and not self.config.skip_validation:
            self.logger.info("Running validation phase")
            with log_timing("Validation phase"):
                validation_result = self.validate(doc_type, doc_path)
            self.logger.info(
                f"Validation complete: status={validation_result.status.value} "
                f"errors={len(validation_result.errors)} warnings={len(validation_result.warnings)}"
            )
        else:
            self.logger.debug("Validation phase skipped")

        # Phase 2: Build prompt
        self.logger.debug("Building review prompt")
        with log_timing("Build prompt"):
            prompt = self._build_review_prompt(
                doc_type=doc_type,
                doc_path=doc_path,
                validation_result=validation_result,
                review_id=review_id,
                version=version,
            )
        prompt_len = len(prompt)
        self.logger.info(f"Prompt built: {prompt_len} chars (~{prompt_len // 4} tokens)")

        # Phase 3: Run AI review
        self.logger.info("Starting AI review")

        # System prompt to ensure complete structured output
        system_prompt = (
            "You are conducting a formal document review. "
            "Generate the COMPLETE structured report as specified in the prompt. "
            "Do NOT summarize or abbreviate. Follow the exact output format with all sections, "
            "tables, and findings. The output should be 5000+ words with detailed per-persona analysis."
        )

        with log_timing("AI review"):
            review_content = self.ai_client.generate(prompt, system_prompt=system_prompt)
        self.logger.info(f"AI review complete: {len(review_content)} chars")

        # Write review report
        self.logger.debug(f"Writing review report to {output_path}")
        output_path.write_text(review_content, encoding="utf-8")

        # Parse results
        self.logger.debug("Parsing review results")
        result = ReviewResult.from_report(output_path, doc_path)
        result.validation_status = validation_result.status

        # Calculate duration
        duration_s = time.perf_counter() - start_time

        # Log review result
        log_review_result(
            doc_type=doc_type.value,
            doc_path=str(doc_path),
            score=result.score,
            p0_count=result.findings.get("P0", 0),
            p1_count=result.findings.get("P1", 0),
            p2_count=result.findings.get("P2", 0),
        )

        # Log phase end
        log_phase_end("UCR", doc_type.value, success=True, duration_s=duration_s)
        self.logger.info(
            f"Review complete: score={result.score} findings={len(result.findings)} "
            f"duration={duration_s:.1f}s report={output_path}"
        )

        return result

    def validate(
        self,
        doc_type: Union[str, DocType],
        doc_path: Union[str, Path],
    ) -> ValidationResult:
        """
        Run validation only (no AI review).

        Args:
            doc_type: Document type
            doc_path: Path to document

        Returns:
            ValidationResult with errors and warnings
        """
        if isinstance(doc_type, str):
            doc_type = DocType.from_string(doc_type)
        doc_path = Path(doc_path)

        self.logger.debug(f"Validating: doc_type={doc_type.value} path={doc_path}")

        validator = self._get_validator(doc_type)
        result = validator.validate(doc_path)

        self.logger.debug(
            f"Validation result: status={result.status.value} "
            f"errors={len(result.errors)} warnings={len(result.warnings)}"
        )

        return result

    def _get_validator(self, doc_type: DocType) -> "BaseValidator":
        """Get or create validator for document type."""
        if doc_type not in self._validators:
            from ucx.validators.registry import get_validator
            self._validators[doc_type] = get_validator(doc_type)
            self.logger.debug(f"Created validator for {doc_type.value}")
        return self._validators[doc_type]

    def _build_review_prompt(
        self,
        doc_type: DocType,
        doc_path: Path,
        validation_result: ValidationResult,
        review_id: Optional[str] = None,
        version: Optional[int] = None,
    ) -> str:
        """Build complete review prompt."""
        parts = []

        # Load base prompt
        self.logger.debug("Loading base prompt")
        base_prompt = self._load_prompt(doc_type)

        # Inject review_id and version into prompt if provided
        if review_id and version:
            base_prompt = base_prompt.replace(
                "[REVIEW_ID]", review_id
            ).replace(
                "[VERSION]", f"v{version:03d}"
            )

        parts.append(base_prompt)
        self.logger.debug(f"Base prompt loaded: {len(base_prompt)} chars")

        # Add validation results
        if validation_result.status != ValidationStatus.SKIPPED:
            parts.append("\n---\n\n## PRE-VALIDATION RESULTS\n\n")
            parts.append(f"**Status**: {validation_result.status.value}\n\n")

            if validation_result.errors:
                parts.append("**Errors**:\n")
                for error in validation_result.errors:
                    parts.append(f"- {error}\n")
                parts.append("\n")

            if validation_result.warnings:
                parts.append("**Warnings**:\n")
                for warning in validation_result.warnings:
                    parts.append(f"- {warning}\n")
                parts.append("\n")

            parts.append("> **Note**: Address validation failures as P0 findings.\n")

        # Add skills
        if self.config.load_skills:
            skills = get_skills_for_phase(doc_type, "ucr")
            self.logger.debug(f"Loading {len(skills)} skills: {skills}")
            skills_content = self._load_skills(skills)
            if skills_content:
                parts.append("\n---\n\n## PERSONA SKILL DEFINITIONS\n\n")
                parts.append(skills_content)
                self.logger.debug(f"Skills content: {len(skills_content)} chars")

        # Add document content
        parts.append("\n---\n\n# DOCUMENT CONTENT\n\n")
        doc_content = self._load_document_content(doc_path)
        parts.append(doc_content)
        self.logger.debug(f"Document content: {len(doc_content)} chars")

        return "".join(parts)

    def _load_prompt(self, doc_type: DocType) -> str:
        """
        Load UCR prompt for document type.

        CRITICAL: Project-specific prompts are REQUIRED.
        Framework prompts are NEVER used for analysis.

        Search order (project-specific only):
        1. {project_dir}/docs/UCX/review/UCR_PROMPT_{TYPE}_PROJECT.md
        2. {project_dir}/docs/UCX/review/UCR_PROMPT_{TYPE}_{PROJECT_NAME}.md

        Raises:
            ProjectPromptNotFoundError: If no project-specific prompt found
        """
        candidates = []

        # Get project directory from config
        project_dir = self.config.get_project_dir()

        if project_dir is None:
            self.logger.error(
                "Project directory not configured. "
                "Set UCX_PROJECT_DIR or use --project-dir flag."
            )
            raise ProjectPromptNotFoundError(
                "ucr",
                doc_type.value,
                Path.cwd()
            )

        # Project-specific prompt directory
        project_prompt_dir = project_dir / "docs" / "UCX" / "review"

        if not project_prompt_dir.exists():
            self.logger.error(
                f"Project UCX/review directory not found: {project_prompt_dir}. "
                f"Create project-specific prompts before running review."
            )
            raise ProjectPromptNotFoundError(
                "ucr",
                doc_type.value,
                project_dir
            )

        # Search patterns for project-specific prompts (non-symlinks only)
        doc_type_upper = doc_type.value.upper()
        patterns = [
            f"UCR_PROMPT_{doc_type_upper}_PROJECT.md",
            f"UCR_PROMPT_{doc_type_upper}_*.md",
        ]

        for pattern in patterns:
            if "*" not in pattern:
                # Exact match
                path = project_prompt_dir / pattern
                if path.exists() and not path.is_symlink():
                    self.logger.info(f"Using project-specific prompt: {path}")
                    return path.read_text(encoding="utf-8")
            else:
                # Glob pattern - find non-symlink files, exclude framework base name
                base_name = f"UCR_PROMPT_{doc_type_upper}.md"
                for path in project_prompt_dir.glob(pattern):
                    if not path.is_symlink() and path.name != base_name:
                        self.logger.info(f"Using project-specific prompt: {path}")
                        return path.read_text(encoding="utf-8")

        # No project-specific prompt found - FAIL (no framework fallback)
        self.logger.error(
            f"Project-specific UCR prompt not found for {doc_type.value}. "
            f"Expected: {project_prompt_dir}/UCR_PROMPT_{doc_type_upper}_PROJECT.md "
            f"Framework prompts cannot be used for analysis."
        )
        raise ProjectPromptNotFoundError(
            "ucr",
            doc_type.value,
            project_dir
        )

    def _load_skills(self, skill_names: list[str]) -> str:
        """Load skill content for personas."""
        skill_dir = self.config.get_skill_dir()
        parts = []
        loaded = []

        for name in skill_names:
            skill_path = skill_dir / f"{name}.md"
            if skill_path.exists():
                title = name.replace("_", " ").title()
                parts.append(f"### Skill: {title}\n\n")
                parts.append(skill_path.read_text(encoding="utf-8"))
                parts.append("\n\n")
                loaded.append(name)

        self.logger.debug(f"Loaded skills: {loaded}")
        return "".join(parts)

    def _load_document_content(self, doc_path: Path) -> str:
        """Load document content for review."""
        parts = []
        files_loaded = []

        if doc_path.is_dir():
            for f in sorted(doc_path.glob("*.md")):
                # Exclude review/report files
                if "REVIEW" not in f.name and "REPORT" not in f.name:
                    parts.append(f"## File: {f.name}\n\n")
                    content = f.read_text(encoding="utf-8")
                    parts.append(content)
                    parts.append("\n\n")
                    files_loaded.append(f.name)
        else:
            parts.append(f"## File: {doc_path.name}\n\n")
            parts.append(doc_path.read_text(encoding="utf-8"))
            parts.append("\n\n")
            files_loaded.append(doc_path.name)

        self.logger.debug(f"Loaded {len(files_loaded)} files: {files_loaded[:5]}{'...' if len(files_loaded) > 5 else ''}")
        return "".join(parts)

    def review_multi_turn(
        self,
        doc_type: Union[str, DocType],
        doc_path: Union[str, Path],
        *,
        output_path: Optional[Path] = None,
        skip_validation: bool = False,
        personas: Optional[list[str]] = None,
        resume: bool = True,
        session_ttl_hours: int = 24,
    ) -> ReviewResult:
        """
        Review a document using multi-turn persona reviews with memory.

        This approach breaks the review into smaller per-persona calls,
        storing prompts and responses in .doc_review_memory/ for:
        - Resume capability (skip completed personas)
        - Debugging (inspect prompts/responses)
        - Caching (reuse if document unchanged)
        - Better output quality (no summarization)

        Args:
            doc_type: Document type (brd, prd, ears, etc.)
            doc_path: Path to document file or directory
            output_path: Custom output path for review report
            skip_validation: Skip validation phase
            personas: Custom persona list (uses default for doc_type if None)
            resume: Resume from previous incomplete session
            session_ttl_hours: Session time-to-live in hours (default: 24)

        Returns:
            ReviewResult with score, findings, and report path
        """
        start_time = time.perf_counter()

        # Normalize inputs
        if isinstance(doc_type, str):
            doc_type = DocType.from_string(doc_type)
        doc_path = Path(doc_path)

        # Log phase start
        log_phase_start("UCR-MultiTurn", doc_type.value, str(doc_path))
        self.logger.info(f"Starting multi-turn review: doc_type={doc_type.value} path={doc_path}")

        if not doc_path.exists():
            self.logger.error(f"Document not found: {doc_path}")
            raise FileNotFoundError(f"Document not found: {doc_path}")

        # Get versioned output path with review ID
        output_path, version, review_id = self._get_versioned_output_path(
            doc_path, doc_type, output_path
        )

        self.logger.debug(f"Output path: {output_path}")
        self.logger.info(f"Review ID: {review_id} (version {version})")

        # Get personas for this doc type
        if personas is None:
            personas = get_personas_for_doc_type(doc_type.value)

        self.logger.info(f"Using {len(personas)} personas: {personas}")

        # Initialize project-specific persona loader
        project_dir = self.config.get_project_dir()
        if project_dir is None:
            self.logger.error(
                "Project directory not configured for multi-turn review. "
                "Set UCX_PROJECT_DIR or use --project-dir flag."
            )
            raise ProjectPromptNotFoundError(
                "ucr",
                f"{doc_type.value}/personas",
                Path.cwd()
            )

        # Use unified prompt loader (single source of truth)
        unified_loader = UnifiedPromptLoader(project_dir, doc_type.value)

        # Check if project has unified prompt configured
        if not unified_loader.has_unified_prompt():
            self.logger.warning(
                f"No project-specific unified prompt found. "
                f"Expected: {project_dir}/docs/UCX/review/UCR_PROMPT_{doc_type.value.upper()}_PROJECT.md"
            )
            template_path = generate_unified_prompt_template(project_dir, doc_type.value)
            self.logger.info(
                f"Generated unified prompt template: {template_path}\n"
                f"Please customize it for your project domain, then re-run the review."
            )
            raise ProjectPromptNotFoundError(
                "review",
                doc_type.value,
                project_dir
            )

        # Parse personas from unified prompt
        try:
            available_personas = unified_loader.list_personas()
            if not available_personas:
                raise ProjectPromptNotFoundError(
                    "review",
                    f"{doc_type.value} (no personas found in prompt)",
                    project_dir
                )
            self.logger.info(f"Found {len(available_personas)} personas in unified prompt: {available_personas}")
        except Exception as e:
            self.logger.error(f"Failed to parse personas from unified prompt: {e}")
            raise

        # Phase 1: Validation
        validation_result = ValidationResult(status=ValidationStatus.SKIPPED)
        if not skip_validation and not self.config.skip_validation:
            self.logger.info("Running validation phase")
            with log_timing("Validation phase"):
                validation_result = self.validate(doc_type, doc_path)
            self.logger.info(
                f"Validation complete: status={validation_result.status.value} "
                f"errors={len(validation_result.errors)} warnings={len(validation_result.warnings)}"
            )

        # Phase 2: Initialize memory
        memory = ReviewMemory(doc_path, doc_type.value)

        # Load document content
        doc_content = self._load_document_content(doc_path)
        content_hash = ReviewMemory.compute_content_hash(doc_content)

        # Initialize or resume session (clear memory if not resuming)
        is_resuming = memory.initialize(
            personas, content_hash,
            clear=not resume,
            session_ttl_hours=session_ttl_hours,
        )
        if is_resuming:
            completed = memory.get_completed_personas()
            self.logger.info(f"Resuming: {len(completed)}/{len(personas)} personas already complete")

        # Save shared context
        memory.save_shared_context(doc_content)

        # Add validation results to context if present
        validation_context = ""
        if validation_result.status != ValidationStatus.SKIPPED:
            validation_context = self._format_validation_context(validation_result)

        # Phase 3: Run each persona
        previous_responses = {}

        for i, persona in enumerate(personas):
            # Check if already complete (resume)
            if memory.is_persona_complete(persona):
                self.logger.info(f"[{i+1}/{len(personas)}] {persona}: Already complete (cached)")
                response = memory.get_response(persona)
                if response:
                    previous_responses[persona] = response
                continue

            self.logger.info(f"[{i+1}/{len(personas)}] {persona}: Starting review")

            # Build persona-specific prompt from unified prompt
            try:
                prompt = unified_loader.build_persona_prompt(
                    persona=persona,
                    document_content=validation_context + doc_content,
                    previous_responses=previous_responses if i > 0 else None,
                )
            except ProjectPromptNotFoundError as e:
                self.logger.error(
                    f"Persona '{persona}' not found in unified prompt. "
                    f"Add section: ### N. THE {persona.upper().replace('_', ' ')}"
                )
                raise

            # Save prompt for debugging
            memory.save_prompt(persona, prompt)
            prompt_tokens = len(prompt) // 4
            self.logger.debug(f"Prompt for {persona}: {len(prompt)} chars (~{prompt_tokens} tokens)")

            # Call AI
            persona_start = time.perf_counter()
            try:
                with log_timing(f"AI review: {persona}"):
                    response = self.ai_client.generate(prompt)

                duration_ms = (time.perf_counter() - persona_start) * 1000

                # Save response
                memory.save_response(persona, response, duration_ms=duration_ms)
                previous_responses[persona] = response

                self.logger.info(
                    f"[{i+1}/{len(personas)}] {persona}: Complete "
                    f"({len(response)} chars, {duration_ms/1000:.1f}s)"
                )

            except Exception as e:
                self.logger.error(f"[{i+1}/{len(personas)}] {persona}: Failed - {e}")
                memory.mark_failed(str(e))
                raise

        # Phase 4: Assemble final report
        self.logger.info("Assembling final report")
        review_content = memory.assemble_report(
            include_header=True,
            review_id=review_id,
            version=version,
        )
        memory.mark_complete()

        # Write to output path
        output_path.write_text(review_content, encoding="utf-8")
        self.logger.info(f"Final report written to {output_path}")

        # Parse results
        result = ReviewResult.from_report(output_path, doc_path)
        result.validation_status = validation_result.status

        # Calculate duration
        duration_s = time.perf_counter() - start_time

        # Log review result
        log_review_result(
            doc_type=doc_type.value,
            doc_path=str(doc_path),
            score=result.score,
            p0_count=result.findings.get("P0", 0),
            p1_count=result.findings.get("P1", 0),
            p2_count=result.findings.get("P2", 0),
        )

        log_phase_end("UCR-MultiTurn", doc_type.value, success=True, duration_s=duration_s)
        self.logger.info(
            f"Multi-turn review complete: score={result.score} "
            f"personas={len(personas)} duration={duration_s:.1f}s"
        )

        return result

    def _format_validation_context(self, validation_result: ValidationResult) -> str:
        """Format validation results for inclusion in prompts."""
        parts = ["\n## PRE-VALIDATION RESULTS\n\n"]
        parts.append(f"**Status**: {validation_result.status.value}\n\n")

        if validation_result.errors:
            parts.append("**Errors**:\n")
            for error in validation_result.errors[:20]:  # Limit to avoid prompt bloat
                parts.append(f"- {error}\n")
            if len(validation_result.errors) > 20:
                parts.append(f"- ... and {len(validation_result.errors) - 20} more errors\n")
            parts.append("\n")

        if validation_result.warnings:
            parts.append("**Warnings**:\n")
            for warning in validation_result.warnings[:20]:
                parts.append(f"- {warning}\n")
            if len(validation_result.warnings) > 20:
                parts.append(f"- ... and {len(validation_result.warnings) - 20} more warnings\n")
            parts.append("\n")

        parts.append("> **Note**: Address validation failures as P0 findings.\n\n")
        return "".join(parts)
