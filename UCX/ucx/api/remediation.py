"""UCX Remediation (UCRem) Phase API.

Implements adaptive remediation with pre-screening to load only
the fixer personas needed based on actual UCR findings.

Features (v1.16.0+):
- Auto-detection of latest review report
- Adaptive fixer persona loading based on pre-screening
- Session data saved to .ucx_remediate_session/ folder

Features (v1.17.0+):
- Fixer-to-LLM hand-off via FixerContext
- Reads fixer context from validation report Section 7
- Injects fixer hand-off section into remediation prompts
"""

from pathlib import Path
from typing import Optional, Union
import json
import logging
import re

from ucx.config.settings import UCXConfig

logger = logging.getLogger(__name__)

# Pattern to extract fixer context JSON from validation report
FIXER_CONTEXT_PATTERN = re.compile(
    r'<!-- FIXER_CONTEXT_START\n(.*?)\nFIXER_CONTEXT_END -->',
    re.DOTALL
)
from ucx.validators.common.file_utils import is_companion_report, sort_section_files
from ucx.config.layer_skills import (
    FIXER_SKILLS,
    DOMAIN_FIXER_SKILLS,
    MANDATORY_FIXER_SKILLS,
)
from ucx.models.enums import DocType, Confidence
from ucx.models.fix import FixProposal
from ucx.exceptions import PromptError
from ucx.prescreening import analyze_ucr_report, ScreeningResult
from ucx.utils.file_ops import find_latest_review_report
from ucx.utils.reporting import (
    ensure_report_schema,
    next_report_version,
    report_filename,
    resolve_doc_id_strict,
)


class UCRemPhase:
    """
    UCRem (Unified Context Remediation) phase.

    Multi-persona fix proposal generation with confidence levels.
    Uses adaptive pre-screening to load only required fixer personas.

    Features:
        - Auto-detection of latest review report (v1.16.0+)
        - Adaptive fixer loading based on pre-screening
        - Saves session data to .ucx_remediate_session/ folder

    Example (auto-detect latest report):
        >>> from ucx import UCRemPhase
        >>>
        >>> ucrem = UCRemPhase()
        >>> fixes, report_path = ucrem.generate_fixes(
        ...     doc_path="docs/01_BRD/BRD-01"  # Auto-detects latest review report
        ... )
        >>> print(f"Used report: {ucrem.last_review_report}")
        >>> print(f"Loaded fixers: {ucrem.last_screening.required_fixers}")

    Example (explicit report):
        >>> fixes, report_path = ucrem.generate_fixes(
        ...     review_report="docs/BRD-01.UCR_review_report_v003.md",
        ...     doc_path="docs/01_BRD/BRD-01"
        ... )
        >>>
        >>> for fix in fixes:
        ...     if fix.confidence == Confidence.AUTO_SAFE:
        ...         fix.apply()
    """

    def __init__(self, config: Optional[UCXConfig] = None):
        """
        Initialize UCRem phase.

        Args:
            config: UCXConfig instance
        """
        self.config = config or UCXConfig()
        self._ai_client = None
        self.last_screening: Optional[ScreeningResult] = None
        self.last_review_report: Optional[Path] = None  # Track which report was used
        self.fixer_context: Optional[dict] = None  # Fixer hand-off context (v1.17.0+)

    @property
    def ai_client(self):
        """Get AI client instance based on config (CLI or API mode)."""
        if self._ai_client is None:
            self._ai_client = self.config.get_ai_client()
        return self._ai_client

    def generate_fixes(
        self,
        doc_path: Union[str, Path],
        review_report: Optional[Union[str, Path]] = None,
        *,
        output_path: Optional[Path] = None,
        protect_source: bool = True,
    ) -> tuple[list[FixProposal], Path]:
        """
        Generate fix proposals from review report.

        Auto-detects the latest review report if not specified (v1.16.0+).
        Always runs pre-screening first to determine which fixer personas
        are needed based on actual findings in the UCR report.

        Args:
            doc_path: Path to original document
            review_report: Path to UCR review report (optional - auto-detects latest if None)
            output_path: Custom output path for fix report
            protect_source: If True, restore unexpected source document changes
                performed by external tooling during report generation.

        Returns:
            Tuple of (list of FixProposal instances, output path where report was written)

        Raises:
            FileNotFoundError: If inputs not found or no review report found
            PromptError: If prompt not found

        Note:
            After calling this method, check:
            - `self.last_review_report` - which report was used
            - `self.last_screening` - which fixers were loaded/excluded
        """
        doc_path = Path(doc_path)

        if not doc_path.exists():
            raise FileNotFoundError(f"Document not found: {doc_path}")

        # Auto-detect latest review report if not specified
        if review_report is None:
            review_report = find_latest_review_report(doc_path)
            if review_report is None:
                raise FileNotFoundError(
                    f"No review report found in: {doc_path}\n"
                    "Run 'ucx review' first or specify --report path."
                )
        else:
            review_report = Path(review_report)
            if not review_report.exists():
                raise FileNotFoundError(f"Review report not found: {review_report}")

        # Track which report was used
        self.last_review_report = review_report

        # Load fixer context from validation report (v1.17.0+)
        self.fixer_context = self._load_fixer_context(doc_path)

        # === PRE-SCREENING PHASE ===
        # Always run pre-screening to determine required fixers
        self.last_screening = analyze_ucr_report(review_report)

        # If no actionable findings, return early
        if not self.last_screening.has_actionable_findings:
            # No fixes needed - create empty report
            doc_type = self._detect_doc_type(review_report)
            doc_id = self._extract_doc_id(doc_path, doc_type)
            if output_path is None:
                output_dir = doc_path if doc_path.is_dir() else doc_path.parent
                version = next_report_version(output_dir, doc_id, "remediation")
                output_path = output_dir / report_filename(doc_id, "remediation", version)

            empty_report = self._generate_empty_report(doc_id, review_report)
            empty_report = ensure_report_schema(
                empty_report,
                report_type="remediation",
                source_artifact_type=doc_type.value,
                source_artifact_id=doc_id,
                report_version=version,
                validator_or_reviewer=f"UCX UCRemPhase ({self.config.model})",
            )
            output_path.write_text(empty_report, encoding="utf-8")
            return [], output_path

        # Detect document type from report name
        doc_type = self._detect_doc_type(review_report)

        # Set default output path - write to document folder, not review report folder
        if output_path is None:
            doc_id = self._extract_doc_id(doc_path, doc_type)
            output_dir = doc_path if doc_path.is_dir() else doc_path.parent
            version = next_report_version(output_dir, doc_id, "remediation")
            output_path = output_dir / report_filename(doc_id, "remediation", version)

        # Build prompt with adaptive fixer selection
        prompt = self._build_remediation_prompt(
            doc_type,
            review_report,
            doc_path,
            fixers=self.last_screening.required_fixers,
        )

        # Remediation generation should be report-oriented; protect source docs
        # from unintended mutations by external model/tool behavior.
        source_snapshot: dict[Path, str] = {}
        if protect_source:
            source_files = self._collect_source_files(doc_path)
            source_snapshot = self._snapshot_source_files(source_files)

        # Generate fixes
        fix_content = self.ai_client.generate(prompt)

        if protect_source and source_snapshot:
            restored_files = self._restore_unexpected_source_changes(source_snapshot)
            if restored_files:
                logger.warning(
                    "Restored unexpected source file changes during remediation generation: %s",
                    ", ".join(str(path) for path in restored_files),
                )

        # Consolidate legacy two-file outputs into canonical UCX report content.
        fix_content = self._consolidate_external_ucrem_report(
            content=fix_content,
            doc_path=doc_path,
            output_path=output_path,
        )

        # Inject screening metadata into report
        fix_content = self._inject_screening_metadata(fix_content)
        report_version = 1
        match = re.search(r"_v(\d{3})\.md$", output_path.name)
        if match:
            report_version = int(match.group(1))
        fix_content = ensure_report_schema(
            fix_content,
            report_type="remediation",
            source_artifact_type=doc_type.value,
            source_artifact_id=self._extract_doc_id(doc_path, doc_type),
            report_version=report_version,
            validator_or_reviewer=f"UCX UCRemPhase ({self.config.model})",
        )

        # Write fix report
        output_path.write_text(fix_content, encoding="utf-8")

        # Parse fix proposals and return with output path
        fixes = self._parse_fixes(fix_content, doc_path)
        return fixes, output_path

    def _collect_source_files(self, doc_path: Path) -> list[Path]:
        """Collect source documentation files that must remain unchanged.

        Excludes UCX companion reports and hidden session files.
        """
        if doc_path.is_file():
            return [doc_path]

        files: list[Path] = []
        for file_path in doc_path.rglob("*.md"):
            if any(part.startswith(".") for part in file_path.parts):
                continue
            if is_companion_report(file_path):
                continue
            files.append(file_path)
        return sorted(files)

    def _snapshot_source_files(self, source_files: list[Path]) -> dict[Path, str]:
        """Capture source file contents before remediation generation."""
        snapshot: dict[Path, str] = {}
        for file_path in source_files:
            try:
                snapshot[file_path] = file_path.read_text(encoding="utf-8")
            except OSError:
                # Skip unreadable files; protection remains best-effort.
                continue
        return snapshot

    def _restore_unexpected_source_changes(self, snapshot: dict[Path, str]) -> list[Path]:
        """Restore source files modified unexpectedly during generation."""
        restored: list[Path] = []
        for file_path, original_content in snapshot.items():
            try:
                current_content = file_path.read_text(encoding="utf-8") if file_path.exists() else None
            except OSError:
                continue

            if current_content == original_content:
                continue

            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(original_content, encoding="utf-8")
                restored.append(file_path)
            except OSError:
                continue

        return restored

    def _consolidate_external_ucrem_report(
        self,
        *,
        content: str,
        doc_path: Path,
        output_path: Path,
    ) -> str:
        """Inline legacy externally referenced UCRem report content.

        Some remediation prompt variants return a short UCX wrapper body that
        references a separate UCRem report path. This breaks auto-apply parsing
        because fix YAML blocks are not present in the canonical UCX report.
        """
        match = re.search(
            r"UCRem(?:\s+remediation)?\s+report generated at\s+`([^`]+)`",
            content,
            re.IGNORECASE,
        )
        if not match:
            return content

        raw_report_path = match.group(1).strip()
        external_report_path = self._resolve_external_report_path(
            raw_report_path=raw_report_path,
            doc_path=doc_path,
            output_path=output_path,
        )

        if external_report_path is None:
            logger.warning(
                "Could not resolve referenced UCRem remediation report: %s (output=%s)",
                raw_report_path,
                str(output_path),
            )
            return content

        try:
            external_content = external_report_path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning(
                "Failed to read referenced UCRem remediation report: %s (%s)",
                str(external_report_path),
                str(exc),
            )
            return content

        # Strip frontmatter so canonical UCX schema remains authoritative.
        fm_match = re.match(r"\A---\n(.*?)\n---\n?(.*)\Z", external_content, re.DOTALL)
        consolidated_body = fm_match.group(2) if fm_match else external_content

        # Only consolidate when detailed fix blocks exist in the external body.
        if "```yaml" not in consolidated_body:
            return content

        if self._is_same_report_version(external_report_path, output_path):
            try:
                external_report_path.unlink(missing_ok=True)
            except OSError as exc:
                logger.warning(
                    "Failed to remove duplicate UCRem report after consolidation: %s (%s)",
                    str(external_report_path),
                    str(exc),
                )

        return consolidated_body.lstrip()

    def _resolve_external_report_path(
        self,
        *,
        raw_report_path: str,
        doc_path: Path,
        output_path: Path,
    ) -> Optional[Path]:
        """Resolve referenced remediation report path to an existing file."""
        candidate = Path(raw_report_path)
        if candidate.is_absolute() and candidate.exists():
            return candidate

        doc_dir = doc_path if doc_path.is_dir() else doc_path.parent
        project_dir = self.config.get_project_dir()

        search_candidates: list[Path] = []
        if project_dir is not None:
            search_candidates.append(project_dir / candidate)
        search_candidates.extend([
            output_path.parent / candidate,
            doc_dir / candidate,
            Path.cwd() / candidate,
        ])

        seen: set[str] = set()
        for path in search_candidates:
            normalized = str(path.resolve()) if path.exists() else str(path)
            if normalized in seen:
                continue
            seen.add(normalized)
            if path.exists():
                return path

        return None

    def _is_same_report_version(self, external_report: Path, output_report: Path) -> bool:
        """Return True when both report filenames share the same _vNNN suffix."""
        external_match = re.search(r"_v(\d{3})\.md$", external_report.name)
        output_match = re.search(r"_v(\d{3})\.md$", output_report.name)
        if not external_match or not output_match:
            return False
        return external_match.group(1) == output_match.group(1)

    def _generate_empty_report(self, doc_id: str, review_report: Path) -> str:
        """Generate report when no actionable findings exist."""
        return f"""---
title: "UCX Remediation Report: {doc_id}"
doc_id: "{doc_id}.UCXRem"
version: "1.0.0"
tags: [ucx-remediation, remediation-report, no-action-required]
custom_fields:
    document_type: ucx_remediation_report
  artifact_type: REMEDIATION_REPORT
  target_artifact_id: "{doc_id}"
  source_review: "{review_report.name}"
  status: NO_ACTION_REQUIRED
  statistics:
    total_findings: {self.last_screening.total_findings}
    actionable_findings: 0
    auto_safe_fixes: 0
    auto_assisted_fixes: 0
    manual_required: 0
---

# UCX Remediation Report: {doc_id}

## Summary

**No actionable findings detected.** All P0/P1 findings in the UCR review have been
resolved, verified, or appropriately deferred.

### Pre-Screening Results

| Metric | Value |
|--------|-------|
| Total findings scanned | {self.last_screening.total_findings} |
| Actionable (P0/P1 open) | 0 |
| Fixers loaded | None (no action required) |

### Recommendation

The document is ready for downstream processing. No remediation required.
"""

    def _load_fixer_context(self, doc_path: Path) -> Optional[dict]:
        """Load fixer context from validation report (v1.17.0+).

        Args:
            doc_path: Document path (file or directory)

        Returns:
            Fixer context dict or None if not found/invalid
        """
        doc_path = Path(doc_path)

        # Normalize: if file, look for report in parent
        if doc_path.is_file():
            report_path = doc_path.parent / ".precommit_validation_report.md"
            doc_dir = doc_path.parent
        else:
            report_path = doc_path / ".precommit_validation_report.md"
            doc_dir = doc_path

        if not report_path.exists():
            # Standard mode writes versioned validation reports; use latest canonical one as fallback.
            doc_type = self._detect_doc_type(doc_path)
            doc_id = self._extract_doc_id(doc_path, doc_type)
            candidates = sorted(
                doc_dir.glob(f"{doc_id}.UCX_validation_report_v*.md"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if candidates:
                report_path = candidates[0]
            else:
                logger.debug(f"No validation report found at {report_path}")
                return None

        try:
            content = report_path.read_text(encoding="utf-8")
        except IOError as e:
            logger.warning(f"Failed to read validation report: {e}")
            return None

        match = FIXER_CONTEXT_PATTERN.search(content)
        if not match:
            logger.debug("No fixer context found in validation report")
            return None

        try:
            context = json.loads(match.group(1))

            # Schema validation
            if context.get("schema_version", "0") < "1.0":
                logger.warning("Outdated fixer context schema")

            required = ["session_id", "timestamp"]
            if not all(f in context for f in required):
                logger.warning("Fixer context missing required fields")
                return None

            logger.info(
                f"Loaded fixer context: session={context.get('session_id')}, "
                f"partial_fixes={len(context.get('llm_completion', []))}"
            )
            return context

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse fixer context JSON: {e}")
            return None

    def _format_fixer_handoff_section(self) -> str:
        """Format fixer hand-off section for remediation prompt (v1.17.0+).

        Returns:
            Markdown string with fixer context, or empty string if no context
        """
        lines = ["\n## FIXER HAND-OFF CONTEXT\n"]

        if not self.fixer_context:
            lines.extend([
                "No fixer context found in validation report.",
                "",
                "**Recommendation**: Run `ucx validate` before remediation",
                "to apply automatic fixes and identify items needing LLM attention.",
                "",
            ])
            return "\n".join(lines)

        # Session info
        lines.extend([
            f"**Fixer Session**: `{self.fixer_context.get('session_id', 'N/A')}`",
            f"**Timestamp**: {self.fixer_context.get('timestamp', 'N/A')}",
            "",
        ])

        # LLM Completion items (highest priority)
        llm_completion = self.fixer_context.get("llm_completion", [])
        if llm_completion:
            lines.extend([
                "### Partial Fixes - COMPLETE THESE FIRST",
                "",
                "Script applied partial fixes. Your task is to complete them:",
                "",
                "| Code | File | Script Action | Your Task |",
                "|------|------|---------------|-----------|",
            ])
            for item in llm_completion:
                lines.append(
                    f"| `{item.get('code', '')}` | `{item.get('file', '')}` | "
                    f"{item.get('script_action', '')} | **{item.get('llm_task', '')}** |"
                )
            lines.extend([
                "",
                "Look for `<!-- LLM_COMPLETION: CODE -->` markers in documents.",
                "After completing each task, remove the marker.",
                "",
            ])

        # LLM-only items
        llm_only = self.fixer_context.get("llm_only", [])
        if llm_only:
            lines.extend([
                "### LLM-Only Issues",
                "",
                "These require semantic understanding (no script fix possible):",
                "",
                "| Code | File | Reason |",
                "|------|------|--------|",
            ])
            for item in llm_only:
                lines.append(f"| `{item.get('code', '')}` | `{item.get('file', '')}` | {item.get('reason', '')} |")
            lines.append("")

        # Protected changes (DO NOT UNDO)
        fixer_applied = self.fixer_context.get("fixer_applied", [])
        if fixer_applied:
            lines.extend([
                "### PROTECTED - Do Not Undo These Fixes",
                "",
                "Script successfully applied these fixes. **DO NOT modify or undo**:",
                "",
            ])
            for item in fixer_applied[:10]:
                lines.append(f"- `{item.get('code', '')}` in `{item.get('file', '')}`")
            if len(fixer_applied) > 10:
                lines.append(f"- ... and {len(fixer_applied) - 10} more")
            lines.extend([
                "",
                "If you believe a fix is incorrect, note it but do not change it.",
                "",
            ])

        return "\n".join(lines)

    def _inject_screening_metadata(self, content: str) -> str:
        """Inject pre-screening metadata into the report."""
        if not self.last_screening:
            return content

        screening_section = f"""
## Pre-Screening Results

| Metric | Value |
|--------|-------|
| Total findings scanned | {self.last_screening.total_findings} |
| Actionable (P0/P1 open) | {self.last_screening.actionable_findings} |
| Domain fixers loaded | {', '.join(self.last_screening.domain_fixers_needed) or 'None'} |
| Mandatory fixers | chaos_engineer, chairperson |
| Excluded fixers | {', '.join(self.last_screening.excluded_fixers) or 'None'} |

### Findings by Fixer

"""
        for fixer, findings in self.last_screening.findings_by_fixer.items():
            screening_section += f"- **{fixer}**: {', '.join(findings)}\n"

        if not self.last_screening.findings_by_fixer:
            screening_section += "- No domain-specific findings mapped\n"

        screening_section += "\n---\n"

        # Insert after frontmatter and title
        if "# UCRem Report" in content:
            # Insert after title line
            parts = content.split("# UCRem Report", 1)
            if len(parts) == 2:
                title_end = parts[1].find("\n\n")
                if title_end > 0:
                    return (
                        parts[0]
                        + "# UCRem Report"
                        + parts[1][:title_end + 2]
                        + screening_section
                        + parts[1][title_end + 2:]
                    )

        # Fallback: append at end
        return content + "\n\n" + screening_section

    def apply_fix(
        self,
        fix: FixProposal,
        *,
        dry_run: bool = False,
    ) -> bool:
        """
        Apply a single fix.

        Args:
            fix: FixProposal to apply
            dry_run: Show what would be done without applying

        Returns:
            True if fix was applied successfully
        """
        return fix.apply(dry_run=dry_run)

    def apply_auto_safe(
        self,
        fixes: list[FixProposal],
        *,
        dry_run: bool = False,
    ) -> list[FixProposal]:
        """
        Apply all auto-safe fixes.

        Args:
            fixes: List of fix proposals
            dry_run: Show what would be done without applying

        Returns:
            List of successfully applied fixes
        """
        applied = []
        for fix in fixes:
            if fix.confidence == Confidence.AUTO_SAFE:
                if fix.apply(dry_run=dry_run):
                    applied.append(fix)
        return applied

    def _detect_doc_type(self, report_path: Path) -> DocType:
        """Detect document type from report filename."""
        name = report_path.stem.upper()

        type_patterns = [
            (r"BRD", DocType.BRD),
            (r"PRD", DocType.PRD),
            (r"EARS", DocType.EARS),
            (r"BDD", DocType.BDD),
            (r"ADR", DocType.ADR),
            (r"SYS", DocType.SYS),
            (r"REQ", DocType.REQ),
            (r"CTR", DocType.CTR),
            (r"TSPEC", DocType.TSPEC),  # Check TSPEC before SPEC
            (r"SPEC", DocType.SPEC),
        ]

        for pattern, doc_type in type_patterns:
            if re.search(pattern, name):
                return doc_type

        return DocType.BRD  # Default

    def _extract_doc_id(self, doc_path: Path, doc_type: DocType) -> str:
        """Extract document ID from path.

        Examples:
            BRD-01_platform_architecture -> BRD-01
            PRD-02.md -> PRD-02
            docs/01_BRD/BRD-01/ -> BRD-01
        """
        # Get the relevant name (directory name or file stem)
        name = doc_path.name if doc_path.is_dir() else doc_path.stem

        return resolve_doc_id_strict(doc_path, doc_type)

    def _build_remediation_prompt(
        self,
        doc_type: DocType,
        review_report: Path,
        doc_path: Path,
        *,
        fixers: Optional[list[str]] = None,
    ) -> str:
        """
        Build complete remediation prompt with adaptive fixer selection.

        Args:
            doc_type: Document type
            review_report: Path to UCR review report
            doc_path: Path to original document
            fixers: List of fixer personas to load (from pre-screening).
                   If None, loads all fixers.
        """
        parts = []

        # Load base prompt
        base_prompt = self._load_prompt(doc_type)
        parts.append(base_prompt)

        # Add adaptive context if pre-screening was used
        if fixers and self.last_screening:
            parts.append("\n---\n\n## ADAPTIVE REMEDIATION CONTEXT\n\n")
            parts.append(
                "Pre-screening identified the following fixers as relevant:\n"
                f"- **Domain fixers**: {', '.join(self.last_screening.domain_fixers_needed) or 'None'}\n"
                f"- **Mandatory fixers**: chaos_engineer, chairperson\n"
                f"- **Excluded (no findings)**: {', '.join(self.last_screening.excluded_fixers) or 'None'}\n\n"
                "Focus remediation efforts on the domains with identified findings.\n"
            )

        # Add fixer hand-off context (v1.17.0+)
        fixer_handoff = self._format_fixer_handoff_section()
        if fixer_handoff:
            parts.append("\n---\n")
            parts.append(fixer_handoff)

        # Add fixer skills (adaptive or full)
        if self.config.load_skills:
            skills_content = self._load_fixer_skills(fixers=fixers)
            if skills_content:
                parts.append("\n---\n\n## FIXER PERSONA SKILL DEFINITIONS\n\n")
                parts.append(skills_content)

        # Add UCR report
        parts.append("\n---\n\n# UCR REVIEW REPORT\n\n")
        parts.append(review_report.read_text(encoding="utf-8"))

        # Add document content
        parts.append("\n---\n\n# ORIGINAL DOCUMENT CONTENT\n\n")
        parts.append(self._load_document_content(doc_path))

        return "".join(parts)

    def _load_prompt(self, doc_type: DocType) -> str:
        """Load UCRem prompt for document type.

        Search order:
        1. Project-specific: {project_dir}/docs/UCX/remediation/UCRem_PROMPT_{TYPE}_PROJECT.md
        2. Project BEELOCAL: {project_dir}/docs/UCX/remediation/UCRem_PROMPT_{TYPE}_BEELOCAL.md
        """
        candidates = []
        doc_type_upper = doc_type.value.upper()

        # Check project-specific prompts first
        project_dir = self.config.get_project_dir()
        if project_dir:
            remediation_dir = project_dir / "docs" / "UCX" / "remediation"
            candidates.extend([
                remediation_dir / f"UCRem_PROMPT_{doc_type_upper}_PROJECT.md",
                remediation_dir / f"UCRem_PROMPT_{doc_type_upper}_BEELOCAL.md",
                remediation_dir / f"UCRem_PROMPT_{doc_type_upper}.md",
            ])

        for path in candidates:
            if path.exists() and not path.is_symlink():
                return path.read_text(encoding="utf-8")

        # Build helpful error message
        searched_paths = "\n  - ".join(str(p) for p in candidates)
        raise PromptError(
            f"Project-specific UCRem prompt not found for {doc_type.value}\n\nSearched:\n  - {searched_paths}\n\n"
            "UCX remediation uses project-specific prompts only. Create the prompt in docs/UCX/remediation/ using the framework prompt as a reference.",
            prompt_name=f"UCRem_PROMPT_{doc_type_upper}_PROJECT.md",
        )

    def _load_fixer_skills(
        self,
        *,
        fixers: Optional[list[str]] = None,
    ) -> str:
        """
        Load fixer persona skills (adaptive or full).

        Args:
            fixers: List of fixer personas to load. If None, loads all.
                   Mandatory fixers are always included.

        Uses project-specific skills only.
        """
        parts = []

        fixer_names = {
            "architect": "Architect Fixer",
            "auditor": "Auditor Fixer",
            "qa_lead": "QA Fixer",
            "integration_lead": "Integration Fixer",
            "chaos_engineer": "Chaos Engineer",
            "chairperson": "Board Chairperson",
        }

        # Determine which skills to load
        if fixers is not None:
            # Use adaptive list, ensure mandatory are included
            skills_to_load = list(fixers)
            for mandatory in MANDATORY_FIXER_SKILLS:
                if mandatory not in skills_to_load:
                    skills_to_load.append(mandatory)
        else:
            # Load all fixers
            skills_to_load = FIXER_SKILLS

        # Sort in execution order
        order = {
            "architect": 1,
            "auditor": 2,
            "integration_lead": 3,
            "qa_lead": 4,
            "chaos_engineer": 10,
            "chairperson": 20,
        }
        skills_to_load = sorted(skills_to_load, key=lambda x: order.get(x, 99))

        project_dir = self.config.get_project_dir()
        if not project_dir:
            raise PromptError(
                "Project directory not configured. Set UCX_PROJECT_DIR or use --project-dir before running remediation.",
                prompt_name="docs/UCX/skills",
            )

        skills_dir = project_dir / "docs" / "UCX" / "skills"
        if not skills_dir.exists():
            raise PromptError(
                f"Project-specific skills directory not found: {skills_dir}. Create project persona files before running remediation.",
                prompt_name=str(skills_dir),
            )

        loaded_count = 0
        for skill in skills_to_load:
            skill_path = skills_dir / f"{skill}.md"
            if not skill_path.exists() or skill_path.is_symlink():
                raise PromptError(
                    f"Project-specific skill not found: {skill_path}. Framework skills are reference-only and cannot be used during remediation.",
                    prompt_name=str(skill_path),
                )

            title = fixer_names.get(skill, skill.replace("_", " ").title())
            if skill in MANDATORY_FIXER_SKILLS:
                role_type = "(Mandatory)"
            else:
                role_type = "(Domain)"
            parts.append(f"### Skill: {title} {role_type}\n\n")
            parts.append(skill_path.read_text(encoding="utf-8"))
            parts.append("\n\n")
            loaded_count += 1

        # Add summary
        if fixers and loaded_count < len(FIXER_SKILLS):
            excluded = set(DOMAIN_FIXER_SKILLS) - set(fixers)
            if excluded:
                parts.insert(0, f"*Adaptive loading: {loaded_count} fixers loaded, "
                            f"{len(excluded)} excluded (no relevant findings)*\n\n")

        return "".join(parts)

    def _load_document_content(self, doc_path: Path) -> str:
        """Load document content.

        Excludes companion reports (audit, review, validation, remediation reports)
        using the is_companion_report() utility from file_utils.

        Section files (e.g., BRD-01.0_index.md) are sorted numerically.
        """
        parts = []

        if doc_path.is_dir():
            all_files = list(doc_path.glob("*.md"))
            for f in sort_section_files(all_files):
                # Skip hidden files and companion reports
                if f.name.startswith("."):
                    continue
                if is_companion_report(f):
                    continue
                parts.append(f"## File: {f.name}\n\n")
                parts.append(f.read_text(encoding="utf-8"))
                parts.append("\n\n")
        else:
            parts.append(f"## File: {doc_path.name}\n\n")
            parts.append(doc_path.read_text(encoding="utf-8"))
            parts.append("\n\n")

        return "".join(parts)

    def _parse_fixes(self, content: str, doc_path: Path) -> list[FixProposal]:
        """
        Parse fix proposals from UCRem output.

        Looks for YAML blocks with fix_id, confidence, etc.
        """
        fixes = []

        # Find YAML blocks
        yaml_pattern = r"```yaml\s*(fix_id:.*?)```"
        matches = re.findall(yaml_pattern, content, re.DOTALL)

        for yaml_str in matches:
            try:
                fix = FixProposal.from_yaml(yaml_str)
                # Resolve relative target paths
                if not fix.target_file.is_absolute():
                    if doc_path.is_dir():
                        fix.target_file = doc_path / fix.target_file
                    else:
                        fix.target_file = doc_path.parent / fix.target_file
                fixes.append(fix)
            except Exception:
                # Skip malformed YAML blocks
                continue

        return fixes
