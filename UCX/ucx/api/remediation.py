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
                if doc_path.is_dir():
                    output_path = doc_path / f"{doc_id}.UCRem_report.md"
                else:
                    output_path = doc_path.parent / f"{doc_id}.UCRem_report.md"

            empty_report = self._generate_empty_report(doc_id, review_report)
            output_path.write_text(empty_report, encoding="utf-8")
            return [], output_path

        # Detect document type from report name
        doc_type = self._detect_doc_type(review_report)

        # Set default output path - write to document folder, not review report folder
        if output_path is None:
            # Extract doc_id from doc_path (e.g., BRD-01 from BRD-01_platform_architecture)
            doc_id = self._extract_doc_id(doc_path, doc_type)
            if doc_path.is_dir():
                output_path = doc_path / f"{doc_id}.UCRem_report.md"
            else:
                output_path = doc_path.parent / f"{doc_id}.UCRem_report.md"

        # Build prompt with adaptive fixer selection
        prompt = self._build_remediation_prompt(
            doc_type,
            review_report,
            doc_path,
            fixers=self.last_screening.required_fixers,
        )

        # Generate fixes
        fix_content = self.ai_client.generate(prompt)

        # Inject screening metadata into report
        fix_content = self._inject_screening_metadata(fix_content)

        # Write fix report
        output_path.write_text(fix_content, encoding="utf-8")

        # Parse fix proposals and return with output path
        fixes = self._parse_fixes(fix_content, doc_path)
        return fixes, output_path

    def _generate_empty_report(self, doc_id: str, review_report: Path) -> str:
        """Generate report when no actionable findings exist."""
        return f"""---
title: "UCRem Report: {doc_id}"
doc_id: "{doc_id}.UCRem"
version: "1.0.0"
tags: [ucrem, remediation-report, no-action-required]
custom_fields:
  document_type: ucrem_report
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

# UCRem Report: {doc_id}

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
        else:
            report_path = doc_path / ".precommit_validation_report.md"

        if not report_path.exists():
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

        # Try to extract doc_id pattern (e.g., BRD-01, PRD-02)
        doc_type_upper = doc_type.value.upper()
        pattern = rf"({doc_type_upper}-\d+)"
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            return match.group(1).upper()

        # Fallback: use directory/file name up to first underscore
        if "_" in name:
            return name.split("_")[0].upper()

        return name.upper()

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
