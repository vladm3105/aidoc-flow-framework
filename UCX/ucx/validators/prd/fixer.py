"""PRD Auto-Fixer Module with UCX-ACTION Output.

Provides automated fixes for common PRD validation issues:
- GATE-E001: Placeholder removal
- GATE-E002: Element ID format correction
- GATE-W008: Section-type mismatch fixing
- Missing frontmatter fields
- Legacy pattern migration

Output format follows unified UCX-ACTION standard:
```markdown
<!-- UCX-ACTION[GATE-XXXX]: description
     status: pending|applied|manual
     file: filename.md
     line: N
     suggested_fix: |
       replacement content
-->
```
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from datetime import datetime, timezone

from ucx.validators.common.result import ValidationIssue, Tier
from ucx.validators.prd.schema import (
    VALID_TYPE_CODES,
    TYPE_CODE_PRIMARY_SECTION,
    PLACEHOLDER_PATTERNS,
    LEGACY_PATTERNS,
    REQUIRED_FRONTMATTER_FIELDS,
    REQUIRED_TAGS,
)


@dataclass
class FixAction:
    """Represents a single fix action."""

    gate_code: str
    description: str
    file: str
    line: Optional[int]
    status: str  # pending, applied, manual
    old_content: Optional[str]
    new_content: Optional[str]
    context: str = ""

    def to_ucx_action(self) -> str:
        """Format as UCX-ACTION block."""
        lines = [f"<!-- UCX-ACTION[{self.gate_code}]: {self.description}"]
        lines.append(f"     status: {self.status}")
        lines.append(f"     file: {self.file}")
        if self.line:
            lines.append(f"     line: {self.line}")
        if self.new_content:
            # Indent multiline content
            indented = "\n".join(f"       {l}" for l in self.new_content.split('\n'))
            lines.append(f"     suggested_fix: |")
            lines.append(indented)
        lines.append("-->")
        return "\n".join(lines)


@dataclass
class FixerResult:
    """Result of PRD auto-fixer execution."""

    actions: List[FixAction] = field(default_factory=list)
    applied_count: int = 0
    pending_count: int = 0
    manual_count: int = 0
    modified_files: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def add_action(self, action: FixAction) -> None:
        """Add a fix action and update counts."""
        self.actions.append(action)
        if action.status == "applied":
            self.applied_count += 1
        elif action.status == "pending":
            self.pending_count += 1
        else:
            self.manual_count += 1

    def format_report(self) -> str:
        """Format as UCX-ACTION report."""
        lines = ["# UCX PRD Fixer Report", ""]
        lines.append(f"**Timestamp**: {self.timestamp}")
        lines.append(f"**Applied**: {self.applied_count}")
        lines.append(f"**Pending**: {self.pending_count}")
        lines.append(f"**Manual**: {self.manual_count}")
        lines.append("")

        if self.actions:
            lines.append("## Actions")
            lines.append("")
            for action in self.actions:
                lines.append(action.to_ucx_action())
                lines.append("")

        return "\n".join(lines)


class PRDFixer:
    """Auto-fixer for PRD validation issues."""

    def __init__(
        self,
        dry_run: bool = True,
        verbose: bool = False,
    ):
        """Initialize fixer.

        Args:
            dry_run: If True, don't apply changes (report only)
            verbose: Enable verbose output
        """
        self.dry_run = dry_run
        self.verbose = verbose

    def fix(
        self,
        file_path: Path,
        issues: List[ValidationIssue],
    ) -> FixerResult:
        """Apply fixes for validation issues.

        Args:
            file_path: Path to PRD file
            issues: List of validation issues to fix

        Returns:
            FixerResult with all actions taken
        """
        result = FixerResult()
        content = file_path.read_text(encoding='utf-8')
        modified_content = content
        file_name = file_path.name

        # Group issues by code for batch processing
        issues_by_code: Dict[str, List[ValidationIssue]] = {}
        for issue in issues:
            if issue.code not in issues_by_code:
                issues_by_code[issue.code] = []
            issues_by_code[issue.code].append(issue)

        # Apply fixers in order
        fixers: List[tuple[str, Callable]] = [
            ("CORPUS-E001", self._fix_placeholders),
            ("PRD-E005", self._fix_element_format),
            ("PRD-W003", self._fix_legacy_patterns),
            ("PRD-W008", self._fix_section_alignment),
            ("CORPUS-W018", self._fix_frontmatter),
            ("PRD-E003", self._fix_missing_tags),
            ("PRD-E004", self._fix_missing_tags),
        ]

        for code, fixer in fixers:
            if code in issues_by_code:
                for issue in issues_by_code[code]:
                    action, modified_content = fixer(
                        file_name, modified_content, issue
                    )
                    if action:
                        result.add_action(action)

        # Apply changes if not dry run
        if not self.dry_run and modified_content != content:
            file_path.write_text(modified_content, encoding='utf-8')
            result.modified_files.append(str(file_path))

        return result

    def _fix_placeholders(
        self,
        file_name: str,
        content: str,
        issue: ValidationIssue,
    ) -> tuple[Optional[FixAction], str]:
        """Fix placeholder text by removing or commenting."""
        # Find the placeholder
        for pattern in PLACEHOLDER_PATTERNS:
            matches = list(pattern.finditer(content))
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                if issue.line and line_num != issue.line:
                    continue

                placeholder = match.group()

                # Determine fix based on context
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                if line_end == -1:
                    line_end = len(content)
                full_line = content[line_start:line_end]

                # Remove placeholder but keep line structure
                fixed_line = full_line.replace(placeholder, "[Content required]")

                action = FixAction(
                    gate_code="CORPUS-E001",
                    description=f"Replace placeholder '{placeholder}'",
                    file=file_name,
                    line=line_num,
                    status="pending",
                    old_content=full_line,
                    new_content=fixed_line,
                )

                # Apply fix
                new_content = content[:line_start] + fixed_line + content[line_end:]
                return action, new_content

        return None, content

    def _fix_element_format(
        self,
        file_name: str,
        content: str,
        issue: ValidationIssue,
    ) -> tuple[Optional[FixAction], str]:
        """Fix invalid element ID format."""
        # Find invalid format (PRD-NN instead of PRD.NN.TT.SS)
        invalid_pattern = re.compile(r"\bPRD[-_](\d+)\b(?!\.)")

        for match in invalid_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            if issue.line and line_num != issue.line:
                continue

            old_id = match.group()
            doc_num = match.group(1).zfill(2)

            # Suggest corrected format
            suggested_id = f"PRD.{doc_num}.01.01"

            action = FixAction(
                gate_code="PRD-E005",
                description=f"Convert '{old_id}' to 4-segment format",
                file=file_name,
                line=line_num,
                status="manual",  # Requires user to determine type code
                old_content=old_id,
                new_content=suggested_id,
                context="Determine correct type code (TT) and sequence (SS)",
            )

            return action, content  # Don't auto-apply, needs review

        return None, content

    def _fix_legacy_patterns(
        self,
        file_name: str,
        content: str,
        issue: ValidationIssue,
    ) -> tuple[Optional[FixAction], str]:
        """Migrate legacy ID patterns to PRD.NN.TT.SS format."""
        for pattern_str, suggestion in LEGACY_PATTERNS.items():
            pattern = re.compile(pattern_str)
            matches = list(pattern.finditer(content))

            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                if issue.line and line_num != issue.line:
                    continue

                old_id = match.group()

                action = FixAction(
                    gate_code="PRD-W003",
                    description=f"Migrate legacy ID '{old_id}'",
                    file=file_name,
                    line=line_num,
                    status="manual",
                    old_content=old_id,
                    new_content=suggestion,
                    context="Replace with appropriate PRD.NN.TT.SS ID",
                )

                return action, content

        return None, content

    def _fix_section_alignment(
        self,
        file_name: str,
        content: str,
        issue: ValidationIssue,
    ) -> tuple[Optional[FixAction], str]:
        """Suggest moving element to correct section."""
        # Parse issue message for element ID
        match = re.search(r"(PRD\.\d{2}\.(\d{2})\.\d{2})", issue.message)
        if not match:
            return None, content

        element_id = match.group(1)
        type_code = match.group(2)
        primary_section = TYPE_CODE_PRIMARY_SECTION.get(type_code, 0)

        action = FixAction(
            gate_code="PRD-W008",
            description=f"Move {element_id} to Section {primary_section}",
            file=file_name,
            line=issue.line,
            status="manual",
            old_content=None,
            new_content=None,
            context=f"Element type {type_code} should be in Section {primary_section}",
        )

        return action, content

    def _fix_frontmatter(
        self,
        file_name: str,
        content: str,
        issue: ValidationIssue,
    ) -> tuple[Optional[FixAction], str]:
        """Fix missing frontmatter fields."""
        # Check if frontmatter exists
        if not content.startswith('---'):
            # Add basic frontmatter
            frontmatter = """---
title: "[TITLE REQUIRED]"
doc_id: PRD-XX
version: "1.0"
status: Draft
tags:
  - prd
  - layer-2-artifact
custom_fields:
  document_type: prd
  artifact_type: PRD
  layer: 2
---

"""
            action = FixAction(
                gate_code="CORPUS-W018",
                description="Add missing YAML frontmatter",
                file=file_name,
                line=1,
                status="pending",
                old_content="[missing]",
                new_content=frontmatter.strip(),
            )

            new_content = frontmatter + content
            return action, new_content

        return None, content

    def _fix_missing_tags(
        self,
        file_name: str,
        content: str,
        issue: ValidationIssue,
    ) -> tuple[Optional[FixAction], str]:
        """Fix missing required tags."""
        # Find tags section in frontmatter
        frontmatter_match = re.match(r"---\n(.*?)\n---", content, re.DOTALL)
        if not frontmatter_match:
            return None, content

        frontmatter = frontmatter_match.group(1)

        # Find tags line
        tags_match = re.search(r"^tags:\s*\n((?:\s+-\s+.+\n)*)", frontmatter, re.MULTILINE)

        missing_tag = None
        if "prd" in issue.message.lower():
            missing_tag = "prd"
        elif "layer-2" in issue.message.lower():
            missing_tag = "layer-2-artifact"

        if not missing_tag:
            return None, content

        if tags_match:
            # Add missing tag to existing tags
            tags_content = tags_match.group(1)
            if missing_tag not in tags_content:
                new_tags = tags_content + f"  - {missing_tag}\n"
                new_frontmatter = frontmatter[:tags_match.start(1)] + new_tags + frontmatter[tags_match.end(1):]
                new_content = f"---\n{new_frontmatter}\n---" + content[frontmatter_match.end():]

                action = FixAction(
                    gate_code=issue.code,
                    description=f"Add missing tag '{missing_tag}'",
                    file=file_name,
                    line=1,
                    status="applied" if not self.dry_run else "pending",
                    old_content=tags_content.strip(),
                    new_content=new_tags.strip(),
                )

                return action, new_content

        return None, content


def fix_prd_file(
    file_path: Path,
    issues: List[ValidationIssue],
    dry_run: bool = True,
) -> FixerResult:
    """Convenience function to fix a PRD file.

    Args:
        file_path: Path to PRD file
        issues: Validation issues to fix
        dry_run: If True, don't apply changes

    Returns:
        FixerResult with all actions
    """
    fixer = PRDFixer(dry_run=dry_run)
    return fixer.fix(file_path, issues)
