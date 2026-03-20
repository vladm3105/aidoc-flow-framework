"""UCX Creation (UCC) Phase API."""

import datetime
import re
from pathlib import Path
from typing import Optional, Union
import yaml

from ucx.config.settings import UCXConfig
from ucx.config.layer_skills import get_skills_for_phase
from ucx.models.document import Document
from ucx.models.enums import DocType
from ucx.exceptions import UCXError, PromptError, SkillError
from ucx.validators.common.file_utils import sort_section_files

CREATE_SESSION_DIR = ".ucx_create_session"


class UCCPhase:
    """
    UCC (Unified Context Creation) phase.

    Multi-persona document authoring with skill injection.

    Example:
        >>> from ucx import UCCPhase, UCXConfig
        >>>
        >>> ucc = UCCPhase(UCXConfig())
        >>> doc = ucc.create(
        ...     doc_type="brd",
        ...     output_path="docs/01_BRD/BRD-01",
        ...     from_ref="docs/00_REF/"
        ... )
        >>> print(f"Created: {doc.path}")
    """

    def __init__(self, config: Optional[UCXConfig] = None):
        """
        Initialize UCC phase.

        Args:
            config: UCXConfig instance
        """
        self.config = config or UCXConfig()
        self._ai_client = None

    @property
    def ai_client(self):
        """Get AI client instance based on config (CLI or API mode)."""
        if self._ai_client is None:
            self._ai_client = self.config.get_ai_client()
        return self._ai_client

    def create(
        self,
        doc_type: Union[str, DocType],
        output_path: Union[str, Path],
        *,
        from_ref: Optional[Path] = None,
        from_upstream: Optional[Path] = None,
        from_iplan: Optional[Path] = None,
        template: Optional[Path] = None,
        multi_file: bool = False,
        validate_after: bool = True,
        save_prompt: bool = True,
    ) -> Document:
        """
        Create a new document with optional post-creation validation.

        Args:
            doc_type: Document type (brd, prd, ears, etc.)
            output_path: Path to output file or directory
            from_ref: Reference documents directory
            from_upstream: Upstream artifact path
            from_iplan: Implementation plan path
            template: Custom template path
            multi_file: Generate multi-file output
            validate_after: Run post-creation validation (default: True)
            save_prompt: Save assembled prompt to .ucx_create_session/ for
                history tracking and inspection (default: True)

        Returns:
            Created Document instance

        Raises:
            UCXError: On creation failure
            PromptError: If prompt not found
        """
        # Normalize inputs
        if isinstance(doc_type, str):
            doc_type = DocType.from_string(doc_type)
        output_path = Path(output_path)
        output_path = self._normalize_output_path(doc_type, output_path, from_upstream)

        # Build prompt
        prompt = self.get_prompt(
            doc_type=doc_type,
            include_skills=self.config.load_skills,
            include_template=True,
            template_path=template,
        )

        # Add reference content
        if from_ref:
            prompt += self._load_reference_content(from_ref)

        # Add upstream content
        if from_upstream:
            prompt += self._load_upstream_content(from_upstream)

        # Add IPLAN content
        if from_iplan:
            prompt += self._load_iplan_content(from_iplan)

        # Add deterministic output contract to reduce LLM drift
        prompt += self._build_output_contract(doc_type, output_path)

        # Save assembled prompt for history tracking
        if save_prompt:
            prompt_path = self._save_prompt_to_session(
                prompt=prompt,
                doc_type=doc_type,
                output_path=output_path,
                from_upstream=from_upstream,
                from_ref=from_ref,
                from_iplan=from_iplan,
            )
        else:
            prompt_path = None

        # Create output directory if needed
        if multi_file:
            output_path.mkdir(parents=True, exist_ok=True)
            actual_output = output_path / f"{doc_type.value.upper()}_CREATED.md"
        else:
            # For single-file output, check if this is a sectioned document
            # (file stem matches {DOC_ID}_{slug} pattern)
            stem = output_path.stem
            parent_already_is_slug = output_path.parent.name == stem
            if (
                output_path.suffix == ".md"
                and "_" in stem
                and re.match(rf"^[A-Z]+-\d+_", stem, re.IGNORECASE)
                and not parent_already_is_slug
            ):
                # Bare slug filename (e.g. PRD-01_platform_architecture.md with
                # no matching parent dir): create the slug directory and place
                # the file inside it.
                doc_folder = output_path.parent / stem
                doc_folder.mkdir(parents=True, exist_ok=True)
                actual_output = doc_folder / output_path.name
            else:
                # Caller already specified the full canonical path, or a simple
                # single-file document: write to the specified path directly.
                output_path.parent.mkdir(parents=True, exist_ok=True)
                actual_output = output_path

        # Generate document
        content = self.ai_client.generate(prompt)

        # Apply deterministic PRD guardrails before writing output
        if doc_type == DocType.PRD:
            content = self._apply_prd_output_guardrails(content, output_path)

        # Write output
        actual_output.write_text(content, encoding="utf-8")
        document = Document.from_path(actual_output)

        # Keep PRD traceability matrix in sync with created artifacts.
        if doc_type == DocType.PRD:
            matrix_path = self._update_prd_traceability_matrix(document.path)
            if matrix_path:
                document.metadata["traceability_matrix_path"] = str(matrix_path)

        # Store prompt path in metadata so CLI can surface it
        if prompt_path:
            document.metadata["prompt_saved_path"] = str(prompt_path)

        # Post-creation validation and scoring for PRD
        if validate_after and doc_type == DocType.PRD:
            self._validate_and_score_prd(document)

        return document

    def _update_prd_traceability_matrix(self, document_path: Path) -> Optional[Path]:
        """Create or update PRD-00_TRACEABILITY_MATRIX.md with the current PRD entry."""
        prd_root = self._find_prd_root(document_path)
        if prd_root is None:
            return None

        doc_id = self._extract_prd_doc_id(document_path)
        if not doc_id:
            return None

        matrix_path = prd_root / "PRD-00_TRACEABILITY_MATRIX.md"
        if not matrix_path.exists():
            matrix_path.write_text(
                "# PRD Traceability Matrix\n\n"
                "| PRD ID | File | Upstream BRD | Status | Last Updated |\n"
                "|---|---|---|---|---|\n",
                encoding="utf-8",
            )

        content = matrix_path.read_text(encoding="utf-8")
        if doc_id in content:
            return matrix_path

        rel_path = self._to_matrix_relative_path(document_path, prd_root)
        upstream = self._extract_first_brd_ref(document_path)
        updated = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        row = f"| {doc_id} | {rel_path} | {upstream or 'TBD'} | Draft | {updated} |\n"

        content += row
        matrix_path.write_text(content, encoding="utf-8")
        return matrix_path

    def _find_prd_root(self, document_path: Path) -> Optional[Path]:
        """Find nearest 02_PRD directory for a generated PRD document."""
        for path in [document_path.parent, *document_path.parents]:
            if path.name == "02_PRD":
                return path
        return None

    def _extract_prd_doc_id(self, document_path: Path) -> Optional[str]:
        """Extract PRD-NN from frontmatter doc_id, fallback to filename prefix."""
        try:
            text = document_path.read_text(encoding="utf-8")
        except Exception:
            text = ""

        match = re.search(r"(?im)^doc_id:\s*(PRD-\d{2,9})\s*$", text)
        if match:
            return match.group(1)

        stem_match = re.match(r"^(PRD-\d{2,9})", document_path.stem)
        return stem_match.group(1) if stem_match else None

    def _extract_first_brd_ref(self, document_path: Path) -> Optional[str]:
        """Extract first @brd reference from document content."""
        try:
            text = document_path.read_text(encoding="utf-8")
        except Exception:
            return None

        match = re.search(r"@brd:\s*(BRD\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9})", text)
        return match.group(1) if match else None

    def _to_matrix_relative_path(self, document_path: Path, prd_root: Path) -> str:
        """Compute path for matrix row, relative to 02_PRD directory."""
        try:
            return str(document_path.relative_to(prd_root))
        except Exception:
            return str(document_path)

    def _normalize_output_path(
        self,
        doc_type: DocType,
        output_path: Path,
        from_upstream: Optional[Path],
    ) -> Path:
        """Normalize output path for created documents.

        If the caller supplies a plain doc ID path such as ``PRD-01`` or
        ``PRD-01.md`` and an upstream artifact provides a reliable slug source,
        convert it to ``PRD-01_{slug}.md``.

        Explicit custom filenames that already include a slug are preserved.
        """
        # If the caller passes the canonical slug folder itself
        # (e.g. docs/02_PRD/PRD-01_platform_architecture), normalize it to the
        # canonical file path inside that folder before any prompt-session or
        # write-path logic runs.
        slug_dir_pattern = rf"^{doc_type.value.upper()}-\d+_[a-z0-9][a-z0-9_\-]*$"
        if output_path.suffix == "" and re.fullmatch(slug_dir_pattern, output_path.name, re.IGNORECASE):
            return output_path / f"{output_path.name}.md"

        # Directories are otherwise left unchanged; callers using multi-file
        # output manage naming at the directory level.
        if output_path.suffix == "" and not re.search(rf"^{doc_type.value.upper()}-\d+$", output_path.name, re.IGNORECASE):
            return output_path
        if output_path.suffix and output_path.suffix.lower() != ".md":
            return output_path

        doc_id_pattern = rf"^{doc_type.value.upper()}-\d+$"
        stem = output_path.stem if output_path.suffix else output_path.name

        # Already slugged or custom-named.
        if not re.fullmatch(doc_id_pattern, stem, re.IGNORECASE):
            return output_path

        slug = self._infer_slug_from_upstream(from_upstream)
        if not slug:
            return output_path.with_suffix(".md") if not output_path.suffix else output_path

        filename = f"{stem.upper()}_{slug}.md"
        return output_path.parent / filename

    def _infer_slug_from_upstream(self, from_upstream: Optional[Path]) -> Optional[str]:
        """Infer a slug from the upstream artifact path.

        Examples:
        - ``BRD-01_platform_architecture`` -> ``platform_architecture``
        - ``.../BRD-01_platform_architecture/BRD-01.0_index.md`` -> ``platform_architecture``
        """
        if not from_upstream:
            return None

        # Use path shape instead of filesystem existence so relative API paths
        # work the same way as CLI-provided existing paths.
        candidate = from_upstream.parent if from_upstream.suffix.lower() == ".md" else from_upstream
        match = re.match(r"^[A-Z]+-\d+_(.+)$", candidate.name)
        if not match:
            return None

        slug = match.group(1).strip().lower()
        slug = re.sub(r"[^a-z0-9_\-]+", "_", slug)
        slug = re.sub(r"_+", "_", slug).strip("_")
        return slug or None

    def _save_prompt_to_session(
        self,
        prompt: str,
        doc_type: DocType,
        output_path: Path,
        from_upstream: Optional[Path],
        from_ref: Optional[Path],
        from_iplan: Optional[Path],
    ) -> Path:
        """Save the assembled creation prompt to .ucx_create_session/ directory.

        Filename includes doc type and UTC timestamp so multiple runs don't
        overwrite each other: ``prompt_prd_20260319T142301Z.txt``.

        Args:
            prompt: Fully assembled prompt string.
            doc_type: Document type being created.
            output_path: Output path (used to determine session dir location).
            from_upstream: Upstream artifact path (for metadata header).
            from_ref: Reference documents path (for metadata header).
            from_iplan: IPLAN path (for metadata header).

        Returns:
            Path to the saved prompt file.
        """
        # Determine session directory location:
        # - For sectioned documents (e.g., BRD-01_platform_architecture.md), 
        #   session dir lives inside {parent}/{stem}/.ucx_create_session/
        # - For simple single-file docs (e.g., README.md), session dir is beside the file
        # - For multi-file/directory output, session dir is inside the output directory
        
        if output_path.suffix == ".md":
            # Check if filename follows the pattern {DOC_ID}_{slug} (e.g., PRD-01_platform_architecture)
            # If so, treat as a sectioned document and put session dir inside a matching directory
            stem = output_path.stem  # e.g., "PRD-01_platform_architecture"
            parent_already_is_slug = output_path.parent.name == stem
            if (
                "_" in stem
                and re.match(rf"^[A-Z]+-\d+_", stem, re.IGNORECASE)
                and not parent_already_is_slug
            ):
                # Sectioned document: session dir inside {parent}/{stem}/
                doc_folder = output_path.parent / stem
                session_dir = doc_folder / CREATE_SESSION_DIR
            else:
                # Simple single-file document: session dir beside the file
                session_dir = output_path.parent / CREATE_SESSION_DIR
        else:
            # Multi-file/directory mode: session dir is inside the output directory
            session_dir = output_path / CREATE_SESSION_DIR
        session_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        prompt_file = session_dir / f"prompt_{doc_type.value}_{timestamp}.txt"

        # Prepend a metadata header so the file is self-documenting
        header_lines = [
            f"# UCX Creation Prompt — {doc_type.value.upper()}",
            f"# Saved: {timestamp}",
            f"# Output: {output_path}",
        ]
        if from_upstream:
            header_lines.append(f"# From upstream: {from_upstream}")
        if from_ref:
            header_lines.append(f"# From ref: {from_ref}")
        if from_iplan:
            header_lines.append(f"# From iplan: {from_iplan}")
        header_lines.append(f"# Prompt size: {len(prompt):,} chars")
        header_lines.append("#" + "-" * 78)
        header_lines.append("")

        full_content = "\n".join(header_lines) + prompt
        prompt_file.write_text(full_content, encoding="utf-8")
        return prompt_file

    def _build_output_contract(self, doc_type: DocType, output_path: Path) -> str:
        """Build strict output constraints derived from target path.

        This reduces identity and metadata drift in generated documents.
        """
        target_doc_id = self._extract_target_doc_id(doc_type, output_path)
        if not target_doc_id:
            return ""

        contract = [
            "\n---\n\n## OUTPUT CONTRACT (MUST FOLLOW EXACTLY)\n",
            f"- Target document ID: `{target_doc_id}`\n",
            "- YAML frontmatter MUST be valid and closed with `---`\n",
            f"- Frontmatter `doc_id` MUST equal `{target_doc_id}`\n",
            "- Frontmatter MUST include: `title`, `doc_id`, `version`, `status`, `tags`\n",
            f"- H1 title MUST start with `# {target_doc_id}:`\n",
            f"- Document Control table `Document ID` value MUST be `{target_doc_id}`\n",
        ]

        if doc_type == DocType.PRD:
            doc_num = target_doc_id.split("-", 1)[1]
            contract.append(f"- All PRD element IDs MUST use `PRD.{doc_num}.TT.SS`\n")

        return "".join(contract)

    def _extract_target_doc_id(self, doc_type: DocType, output_path: Path) -> Optional[str]:
        """Extract target DOC-NN from output path context."""
        pattern = re.compile(rf"({doc_type.value.upper()}-\d{{2,9}})", re.IGNORECASE)
        candidates = [
            output_path.stem,
            output_path.name,
            output_path.parent.name,
        ]
        for text in candidates:
            match = pattern.search(text)
            if match:
                return match.group(1).upper()
        return None

    def _apply_prd_output_guardrails(self, content: str, output_path: Path) -> str:
        """Normalize PRD output to satisfy required metadata and identity contracts."""
        target_doc_id = self._extract_target_doc_id(DocType.PRD, output_path)

        # Split frontmatter/body (tolerant to minor delimiter spacing).
        fm_match = re.match(r"^---[ \t]*\n(.*?)\n---[ \t]*\n?", content, re.DOTALL)
        body = content
        frontmatter = {}
        if fm_match:
            raw_fm = fm_match.group(1)
            body = content[fm_match.end():]
            try:
                parsed = yaml.safe_load(raw_fm)
                if isinstance(parsed, dict):
                    frontmatter = parsed
            except Exception:
                frontmatter = {}

        # Ensure required top-level frontmatter fields.
        title = str(frontmatter.get("title", "")).strip()
        if not title:
            title = f"{target_doc_id or 'PRD-XX'}: Product Requirements Document"
        if target_doc_id and not title.startswith(f"{target_doc_id}:"):
            title = re.sub(r"^PRD-\d{2,9}:", f"{target_doc_id}:", title)

        frontmatter["title"] = title
        if target_doc_id:
            frontmatter["doc_id"] = target_doc_id
        else:
            frontmatter.setdefault("doc_id", "PRD-XX")

        frontmatter.setdefault("version", "1.0.0")
        status = str(frontmatter.get("status", "Draft")).strip().lower()
        frontmatter["status"] = {
            "draft": "Draft",
            "review": "Review",
            "approved": "Approved",
        }.get(status, "Draft")

        tags = frontmatter.get("tags", [])
        if not isinstance(tags, list):
            tags = [str(tags)] if tags else []
        if "prd" not in tags:
            tags.append("prd")
        if "layer-2-artifact" not in tags:
            tags.append("layer-2-artifact")
        frontmatter["tags"] = tags

        custom_fields = frontmatter.get("custom_fields", {})
        if not isinstance(custom_fields, dict):
            custom_fields = {}
        custom_fields.setdefault("document_type", "prd")
        custom_fields.setdefault("artifact_type", "PRD")
        custom_fields.setdefault("layer", 2)
        frontmatter["custom_fields"] = custom_fields

        # Enforce ID consistency in common PRD locations.
        if target_doc_id:
            doc_num = target_doc_id.split("-", 1)[1]

            # H1 normalization
            body = re.sub(
                r"(?m)^#\s+PRD-\d{2,9}:",
                f"# {target_doc_id}:",
                body,
                count=1,
            )

            # Document Control row normalization
            body = re.sub(
                r"(?mi)^(\|\s*Document\s+ID\s*\|\s*)PRD-\d{2,9}(\s*\|)",
                rf"\1{target_doc_id}\2",
                body,
            )

            # Element ID doc-number normalization (PRD.NN.TT.SS)
            body = re.sub(
                rf"\bPRD\.(?!{re.escape(doc_num)}\b)(\d{{2,9}})\.(\d{{2}})\.(\d{{2,9}})\b",
                lambda m: f"PRD.{doc_num}.{m.group(2)}.{m.group(3)}",
                body,
            )

        fm_text = yaml.safe_dump(frontmatter, sort_keys=False).strip()
        return f"---\n{fm_text}\n---\n\n{body.lstrip()}"

    def _validate_and_score_prd(self, document: Document) -> None:
        """Run Tier 1 validation and compute readiness scores on created PRD.

        Validation is routed through the same UCR/registry path used by the
        standalone `ucx validate prd` command so creation-time results stay
        consistent with explicit validation runs.
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            from ucx.api.review import UCRPhase
            from ucx.models.enums import DocType
            from ucx.utils.reporting import (
                ensure_report_schema,
                next_report_version,
                report_filename,
                resolve_doc_id_strict,
            )

            ucr = UCRPhase(self.config)
            result = ucr.validate(DocType.PRD, document.path)
            validator = ucr._get_validator(DocType.PRD)
            unified_result = getattr(validator, "unified_result", None)

            # Write validation report alongside created document (same behavior as `ucx validate`)
            doc_dir = document.path if document.path.is_dir() else document.path.parent
            doc_id = resolve_doc_id_strict(document.path, DocType.PRD)
            version = next_report_version(doc_dir, doc_id, "validation")
            report_path = doc_dir / report_filename(doc_id, "validation", version)

            if unified_result and hasattr(unified_result, "format_report"):
                report_content = unified_result.format_report(doc_id=doc_id, doc_type="PRD", version=version)
            else:
                report_content = (
                    f"Status: {result.status.value if hasattr(result.status, 'value') else result.status}\n"
                    f"Errors: {len(result.errors)}\n"
                    f"Warnings: {len(result.warnings)}\n"
                )

            report_content = ensure_report_schema(
                report_content,
                report_type="validation",
                source_artifact_type=DocType.PRD.value,
                source_artifact_id=doc_id,
                report_version=version,
                validator_or_reviewer="UCX UCCPhase",
            )
            report_path.write_text(report_content, encoding="utf-8")
            document.metadata["validation_report_path"] = str(report_path)

            if result.errors:
                logger.warning(
                    f"Created PRD has {len(result.errors)} validation issues. "
                    f"Run 'ucx validate prd {document.path}' for details."
                )
                document.metadata["validation_status"] = "needs_review"
                document.metadata["tier1_errors"] = len(result.errors)
            else:
                document.metadata["validation_status"] = "passed"

        except Exception as e:
            logger.warning(f"Validation failed: {e}")
            return

        if unified_result is None:
            return

        document.metadata["sys_ready_score"] = unified_result.sys_ready_score
        document.metadata["ears_ready_score"] = unified_result.ears_ready_score
        document.metadata["template_profile"] = unified_result.template_profile
        document.metadata["readiness_status"] = (
            "PASS" if unified_result.both_passed else "REVIEW"
        )

        logger.info(
            f"PRD scores computed: SYS-Ready={unified_result.sys_ready_score:.1f}%, "
            f"EARS-Ready={unified_result.ears_ready_score:.1f}%, "
            f"Status={document.metadata['readiness_status']}"
        )

    def get_prompt(
        self,
        doc_type: Union[str, DocType],
        *,
        include_skills: bool = True,
        include_template: bool = True,
        template_path: Optional[Path] = None,
    ) -> str:
        """
        Get assembled prompt without execution.

        Args:
            doc_type: Document type
            include_skills: Include persona skills
            include_template: Include document template

        Returns:
            Assembled prompt string
        """
        if isinstance(doc_type, str):
            doc_type = DocType.from_string(doc_type)

        prompt_parts = []

        # Load base prompt
        base_prompt = self._load_prompt(doc_type)
        prompt_parts.append(base_prompt)

        # Add skills
        if include_skills:
            skills = get_skills_for_phase(doc_type, "ucc")
            skills_content = self._load_skills(skills)
            if skills_content:
                prompt_parts.append("\n---\n\n## AUTHOR PERSONA SKILL DEFINITIONS\n")
                prompt_parts.append(skills_content)

        # Add template
        if include_template:
            template_content = self._load_template(doc_type, template_path)
            if template_content:
                prompt_parts.append("\n---\n\n# DOCUMENT TEMPLATE\n\n")
                prompt_parts.append("Follow this template structure exactly:\n\n")
                prompt_parts.append(template_content)

        return "\n".join(prompt_parts)

    def _load_prompt(self, doc_type: DocType) -> str:
        """Load project-specific UCC prompt for document type."""
        project_dir = self._resolve_project_dir(required_subdir="creation")
        project_prompt_dir = project_dir / "docs" / "UCX" / "creation"
        candidates = [
            project_prompt_dir / f"UCC_PROMPT_{doc_type.value.upper()}_PROJECT.md",
            project_prompt_dir / f"UCC_PROMPT_{doc_type.value.upper()}.md",
        ]

        for path in candidates:
            if path.exists() and not path.is_symlink():
                return path.read_text(encoding="utf-8")

        searched = "\n  - ".join(str(path) for path in candidates)
        raise PromptError(
            f"Project-specific UCC prompt not found for {doc_type.value}.\n\n"
            f"Searched:\n  - {searched}\n\n"
            "UCX creation uses project-specific prompts only. Create the prompt in docs/UCX/creation/ using the framework prompt as a reference.",
            prompt_name=f"UCC_PROMPT_{doc_type.value.upper()}_PROJECT.md",
        )

    def _load_skills(self, skill_names: list[str]) -> str:
        """Load project-specific skill content for personas."""
        project_dir = self._resolve_project_dir(required_subdir="skills")
        skill_dir = project_dir / "docs" / "UCX" / "skills"
        parts = []

        for name in skill_names:
            skill_path = skill_dir / f"{name}.md"
            if not skill_path.exists() or skill_path.is_symlink():
                raise SkillError(
                    f"Project-specific skill not found: {skill_path}. UCX creation uses project-specific personas only. Create the skill file before running create.",
                    skill_name=name,
                )

            title = name.replace("_", " ").title()
            parts.append(f"### Skill: {title}\n\n")
            parts.append(skill_path.read_text(encoding="utf-8"))
            parts.append("\n\n")

        return "".join(parts)

    def _load_template(
        self,
        doc_type: DocType,
        custom_path: Optional[Path] = None,
    ) -> str:
        """Load project-specific document template."""
        if custom_path:
            if custom_path.exists():
                return custom_path.read_text(encoding="utf-8")
            raise PromptError(
                f"Custom template path not found: {custom_path}",
                prompt_name=str(custom_path),
            )

        project_dir = self._resolve_project_dir(required_subdir="templates")
        template_dir = project_dir / "docs" / "UCX" / "templates"

        candidates = [
            template_dir / f"{doc_type.value.upper()}-MVP-TEMPLATE.md",
            template_dir / f"{doc_type.value.upper()}-MVP-TEMPLATE.feature",
            template_dir / f"{doc_type.value.upper()}-TEMPLATE.md",
        ]

        for path in candidates:
            if path.exists() and not path.is_symlink():
                return path.read_text(encoding="utf-8")

        searched = "\n  - ".join(str(path) for path in candidates)
        raise PromptError(
            f"Project-specific template not found for {doc_type.value}.\n\n"
            f"Searched:\n  - {searched}\n\n"
            "UCX creation uses project-specific templates only. Create the template in docs/UCX/templates/ using the framework template as a reference.",
            prompt_name=f"{doc_type.value.upper()}-MVP-TEMPLATE.md",
        )

    def _resolve_project_dir(self, *, required_subdir: str) -> Path:
        """Resolve project root and require docs/UCX/<subdir>/ to exist."""
        project_dir = self.config.get_project_dir()
        if project_dir is None:
            cwd = Path.cwd().resolve()
            for path in [cwd, *cwd.parents]:
                if (path / "docs" / "UCX" / required_subdir).exists():
                    project_dir = path
                    break

        if project_dir is None:
            raise PromptError(
                "Project directory not configured and no docs/UCX/ directory was found from the current working directory upward. Set UCX_PROJECT_DIR or run UCX from a project that contains docs/UCX/.",
                prompt_name=f"docs/UCX/{required_subdir}",
            )

        required_dir = project_dir / "docs" / "UCX" / required_subdir
        if not required_dir.exists():
            raise PromptError(
                f"Required project-specific UCX directory not found: {required_dir}. Create the project-specific assets before running UCX.",
                prompt_name=str(required_dir),
            )

        return project_dir

    def _load_reference_content(self, ref_path: Path) -> str:
        """Load reference documents."""
        parts = ["\n---\n\n# REFERENCE DOCUMENTS\n\n"]

        if ref_path.is_dir():
            for f in sorted(ref_path.glob("*")):
                if f.is_file() and f.suffix in (".md", ".txt"):
                    parts.append(f"## Reference: {f.name}\n\n")
                    parts.append(f.read_text(encoding="utf-8"))
                    parts.append("\n\n")
        elif ref_path.is_file():
            parts.append(f"## Reference: {ref_path.name}\n\n")
            parts.append(ref_path.read_text(encoding="utf-8"))
            parts.append("\n\n")

        return "".join(parts)

    def _load_upstream_content(self, upstream_path: Path) -> str:
        """Load upstream artifact content.

        For sectioned documents (directories), uses the index file
        (``*.[doc_id].0_index.md``) to determine canonical section files and
        their order. Falls back to numeric glob sort if no index is found.

        Programmatically strips YAML frontmatter and HTML comment blocks from
        each file before merging, then prunes low-signal sections/subsections
        without an LLM call.
        """
        parts = ["\n---\n\n# UPSTREAM ARTIFACT\n\n"]

        if upstream_path.is_dir():
            section_files = self._resolve_section_files(upstream_path)
            for f in section_files:
                cleaned = self._prepare_upstream_section_content(f)
                if not cleaned:
                    continue
                parts.append(f"## File: {f.name}\n\n")
                parts.append(cleaned)
                parts.append("\n\n")
        elif upstream_path.is_file():
            cleaned = self._prepare_upstream_section_content(upstream_path)
            if not cleaned:
                return ""
            parts.append(f"## File: {upstream_path.name}\n\n")
            parts.append(cleaned)
            parts.append("\n\n")

        return "".join(parts)

    def _resolve_section_files(self, doc_dir: Path) -> list[Path]:
        """Return the canonical ordered list of section files for a BRD/PRD directory.

        Strategy:
        1. Find index file: any ``*.0_index.md`` or file with ``section: 0`` frontmatter.
        2. Parse markdown links in table rows that point to sibling ``.md`` files.
        3. Return those files in index-declared order (index itself first).
        4. Fall back to ``sort_section_files(glob)`` if no index found.
        """
        # Find index file
        index_candidates = list(doc_dir.glob("*.0_index.md"))
        if not index_candidates:
            # Fallback: first file whose frontmatter has section: 0
            for f in sorted(doc_dir.glob("*.md")):
                content = f.read_text(encoding="utf-8")
                if re.search(r"^section:\s*0\b", content, re.MULTILINE):
                    index_candidates = [f]
                    break

        if not index_candidates:
            # No index: fall back to numeric sort of all section-like files
            all_files = [
                f for f in doc_dir.glob("*.md")
                if not any(skip in f.name for skip in [
                    ".UCR_", ".UCRem_", ".V_", ".UCX_", ".precommit_"
                ])
            ]
            return sort_section_files(all_files)

        index_file = index_candidates[0]
        index_text = index_file.read_text(encoding="utf-8")

        # Extract markdown link targets from table rows — same-directory files only
        # (exclude links with path separators like ../BRD-02/... cross-document refs)
        link_pattern = re.compile(r'\[.*?\]\(([^)/\\]+\.md)\)')
        referenced = []
        for match in link_pattern.finditer(index_text):
            target = doc_dir / match.group(1)
            if target.exists() and target not in referenced:
                referenced.append(target)

        # Section files only — exclude the index file itself (metadata/nav only,
        # no content value for downstream creation)
        section_files = [f for f in referenced if f != index_file]

        # Warn (via no-op) if nothing parsed — fall back
        if len(section_files) < 1:
            all_files = [
                f for f in doc_dir.glob("*.md")
                if not any(skip in f.name for skip in [
                    ".UCR_", ".UCRem_", ".V_", ".UCX_", ".precommit_"
                ])
            ]
            return sort_section_files(all_files)

        return section_files

    def _strip_file_boilerplate(self, file_path: Path) -> str:
        """Return file content with YAML frontmatter and HTML comment blocks removed.

        Eliminates:
        - YAML frontmatter (``---`` ... ``---`` at top of file)
        - HTML comment blocks (``<!-- ... -->``)
        - Navigation breadcrumb lines (``> **Navigation**:``)

        Does NOT call an LLM — purely deterministic regex/string processing.
        """
        text = file_path.read_text(encoding="utf-8")

        # Strip YAML frontmatter (only at start of file)
        text = re.sub(r"\A---\n.*?\n---\n?", "", text, flags=re.DOTALL)

        # Strip HTML comment blocks (single and multi-line)
        text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

        # Strip navigation breadcrumb lines
        text = re.sub(r"^> \*\*Navigation\*\*:.*$\n?", "", text, flags=re.MULTILINE)

        # Collapse 3+ consecutive blank lines to 2
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def _prepare_upstream_section_content(self, file_path: Path) -> str:
        """Prepare upstream section content for prompt inclusion.

        Steps:
        1. Strip generic boilerplate.
        2. Apply section-aware pruning for BRD-style section files.
        3. Return empty string for sections that should be omitted entirely.
        """
        text = self._strip_file_boilerplate(file_path)
        if not text:
            return ""

        return self._prune_low_signal_upstream_content(file_path, text)

    def _prune_low_signal_upstream_content(self, file_path: Path, text: str) -> str:
        """Remove low-signal content from merged upstream artifacts.

        Current rules for sectioned BRD inputs:
        - Remove standalone horizontal rules.
        - Drop Section 17 (Glossary) entirely.
        - Compact subsection 16.2 Cross-BRD Dependencies.
        - Compact Mermaid blocks globally.
        - Compact References subsections.
        """
        match = re.search(r"\.(\d+)_", file_path.name)
        section_number = int(match.group(1)) if match else None

        # Glossary is low-value for downstream PRD generation.
        if section_number == 17:
            return ""

        # Remove Markdown horizontal rules that add tokens but no semantics.
        text = re.sub(r"^---\s*$\n?", "", text, flags=re.MULTILINE)

        # Keep reference context, but compress long tables to a short list.
        text = self._compact_references_subsections(text)

        # Preserve diagram presence and type without keeping the full block.
        text = self._compact_mermaid_blocks(text)

        if section_number == 16:
            # Keep dependency context, but compress tables into a short list.
            text = self._compact_cross_brd_dependencies(text)

        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _compact_references_subsections(self, text: str) -> str:
        """Compact verbose references subsections into a short bullet list."""

        def replacer(match: re.Match[str]) -> str:
            heading = match.group(1)
            body = match.group(2)
            docs = []

            for line in body.splitlines():
                stripped = line.strip()
                if not stripped.startswith("|"):
                    continue
                cells = [cell.strip() for cell in stripped.strip("|").split("|")]
                if (
                    not cells
                    or cells[0] in {"Document Name", ""}
                    or re.fullmatch(r"[-: ]+", cells[0] or "")
                ):
                    continue
                name = cells[0]
                version = cells[1] if len(cells) > 1 else ""
                doc = f"- {name}"
                if version and version != "-":
                    doc += f" ({version})"
                docs.append(doc)

            if not docs:
                return "\n"

            summary = [f"\n{heading}", "", "Compressed source references:"]
            summary.extend(docs[:8])
            return "\n".join(summary) + "\n"

        return re.sub(
            r"\n(## [^\n]*References[^\n]*)\n(.*?)(?=\n## [^\n]*\n|\n# Section |\Z)",
            replacer,
            text,
            flags=re.DOTALL,
        )

    def _compact_mermaid_blocks(self, text: str) -> str:
        """Replace Mermaid blocks with short placeholders preserving type/context."""

        def replacer(match: re.Match[str]) -> str:
            block = match.group(1)
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            diagram_type = lines[0] if lines else "diagram"
            return f"\n[Diagram omitted for token efficiency: Mermaid {diagram_type}]\n"

        return re.sub(r"```mermaid\n(.*?)```\n?", replacer, text, flags=re.DOTALL)

    def _compact_cross_brd_dependencies(self, text: str) -> str:
        """Compact Cross-BRD dependency tables into a short bullet list."""

        def replacer(match: re.Match[str]) -> str:
            body = match.group(1)
            deps = []

            for dep in sorted(set(re.findall(r"\bBRD-\d+\b", body))):
                if dep != "BRD-01":
                    deps.append(f"- {dep}")

            if not deps:
                return "\n"

            summary = [
                "\n## 16.2 Cross-BRD Dependencies",
                "",
                "Compressed downstream/upstream BRD dependency context:",
            ]
            summary.extend(deps)
            return "\n".join(summary) + "\n"

        return re.sub(
            r"\n## 16\.2 Cross-BRD Dependencies\n(.*?)(?=\n## 16\.[3-9]\b|\Z)",
            replacer,
            text,
            flags=re.DOTALL,
        )

    def _load_iplan_content(self, iplan_path: Path) -> str:
        """Load implementation plan content."""
        # Resolve IPLAN-NNN pattern
        resolved = self._resolve_iplan(iplan_path)
        if not resolved:
            return ""

        parts = ["\n---\n\n# IMPLEMENTATION PLAN\n\n"]
        parts.append(resolved.read_text(encoding="utf-8"))
        return "".join(parts)

    def _resolve_iplan(self, iplan_input: Path) -> Optional[Path]:
        """Resolve IPLAN path from input."""
        if iplan_input.exists():
            return iplan_input

        # Try IPLAN-NNN pattern
        iplan_name = iplan_input.stem
        search_dirs = [
            Path("work_plans"),
            Path("governance/plans"),
            Path("docs/IPLAN"),
        ]

        for search_dir in search_dirs:
            if search_dir.exists():
                matches = list(search_dir.glob(f"{iplan_name}*.md"))
                if matches:
                    return matches[0]

        return None
