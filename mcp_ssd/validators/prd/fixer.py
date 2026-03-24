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

from ucx.validators.common.result import ValidationIssue
from ucx.validators.prd.schema import (
    VALID_TYPE_CODES,
    TYPE_CODE_PRIMARY_SECTION,
    PLACEHOLDER_PATTERNS,
    LEGACY_PATTERNS,
    REQUIRED_FRONTMATTER_FIELDS,
    REQUIRED_TAGS,
)

# ---------------------------------------------------------------------------
# LLM handoff classification tables
# ---------------------------------------------------------------------------

# Codes that CANNOT be auto-fixed — LLM remediation required
LLM_ONLY_CODES: Dict[str, str] = {
    "PRD-W004": "BRD traceability gaps require cross-document semantic analysis",
    "PRD-W009": "Acceptance criteria structure requires domain-aware content generation",
    "PRD-W013": "User story format normalization requires reading comprehension",
    "PRD-W014": "Priority notation standardization requires document-wide semantic judgment",
}

# Codes where script does partial structural work and LLM completes content
LLM_COMPLETION_CODES: Dict[str, Dict[str, str]] = {
    "PRD-W006": {
        "script_action": "Inserts skeleton Section 10.x subsection(s)",
        "llm_task": "Fill skeleton placeholders with domain-specific product copy",
    },
    "PRD-W021": {
        "script_action": "Inserts skeleton Section 14.x Release/Launch Criteria checklist",
        "llm_task": "Customize checklist items for this product's specific launch requirements",
    },
}


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
            ("PRD-E017", self._fix_duplicate_ids),
            ("PRD-W003", self._fix_legacy_patterns),
            ("PRD-W006", self._fix_missing_section_10_subsections),
            ("PRD-W008", self._fix_section_alignment),
            ("PRD-W011", self._fix_missing_feature_ids),
            ("PRD-W012", self._fix_missing_story_ids),
            ("PRD-W019", self._fix_missing_quality_ids),
            ("PRD-W021", self._fix_missing_launch_criteria),
            ("CORPUS-W018", self._fix_frontmatter),
            ("PRD-E003", self._fix_missing_tags),
            ("PRD-E004", self._fix_missing_tags),
            # LLM-only handoff actions (generate manual FixAction, no content change)
            ("PRD-W004", self._handoff_brd_traceability),
            ("PRD-W009", self._handoff_acceptance_criteria),
            ("PRD-W013", self._handoff_user_story_format),
            ("PRD-W014", self._handoff_priority_notation),
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

    def _fix_duplicate_ids(
        self,
        file_name: str,
        content: str,
        issue: ValidationIssue,
    ) -> tuple[Optional[FixAction], str]:
        """Fix duplicate element ID by renumbering to next available sequence.

        Parses the element ID from the issue message, locates the duplicate
        occurrence at issue.line, computes the next unused sequence number
        for that (doc_num, type_code) pair in the current content, and
        replaces the ID on that line only.
        """
        # Message format: "Duplicate element ID PRD.NN.TT.SS (first at line N)"
        id_match = re.search(r"(PRD\.(\d{2})\.(\d{2})\.(\d{2}))", issue.message)
        if not id_match or not issue.line:
            return None, content

        element_id = id_match.group(1)
        doc_num = id_match.group(2)
        type_code = id_match.group(3)

        lines = content.split('\n')
        if issue.line > len(lines):
            return None, content

        target_line = lines[issue.line - 1]
        if element_id not in target_line:
            return None, content

        # Collect all sequence numbers already used for this (doc_num, type_code)
        existing_pattern = re.compile(rf"PRD\.{doc_num}\.{type_code}\.(\d{{2}})")
        existing_seqs = {int(m.group(1)) for m in existing_pattern.finditer(content)}
        next_seq = max(existing_seqs) + 1 if existing_seqs else 1
        new_id = f"PRD.{doc_num}.{type_code}.{next_seq:02d}"

        new_line = target_line.replace(element_id, new_id, 1)
        lines[issue.line - 1] = new_line
        new_content = '\n'.join(lines)

        status = "applied" if not self.dry_run else "pending"
        action = FixAction(
            gate_code="PRD-E017",
            description=f"Renumber duplicate {element_id} \u2192 {new_id}",
            file=file_name,
            line=issue.line,
            status=status,
            old_content=element_id,
            new_content=new_id,
        )
        return action, new_content

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

    def _fix_missing_section_10_subsections(
        self,
        file_name: str,
        content: str,
        issue: ValidationIssue,
    ) -> tuple[Optional[FixAction], str]:
        """Fix PRD-W006: Add missing Section 10 subsections (10.1–10.5).

        Detects which subsections are missing from the issue message and
        appends skeleton subsections at the end of Section 10, before
        the next top-level section.
        """
        # Parse which subsections are missing from issue message
        # e.g. "Section 10 missing subsections: 10.5"
        missing_match = re.search(r"missing subsections?:\s*([\d.,\s]+)", issue.message)
        if not missing_match:
            return None, content

        missing_labels = [s.strip() for s in missing_match.group(1).split(',') if s.strip()]

        # Subsection skeleton templates
        subsection_templates = {
            "10.1": "### 10.1 Product Positioning\n\n"
                    "Value Proposition: [CONTENT REQUIRED]\n\n"
                    "Target Positioning: [CONTENT REQUIRED]\n",
            "10.2": "### 10.2 Key Messaging Themes\n\n"
                    "| Theme | Message | Target Audience | Channel |\n"
                    "|-------|---------|-----------------|--------|\n"
                    "| [Theme] | [Message] | [Audience] | [Channel] |\n",
            "10.3": "### 10.3 User-Facing Content Requirements\n\n"
                    "| Content Type | Description | Owner | Status |\n"
                    "|--------------|-------------|-------|-------|\n"
                    "| Help text | [CONTENT REQUIRED] | PM/UX | Draft |\n"
                    "| Error messages | [CONTENT REQUIRED] | PM/Dev | Draft |\n",
            "10.4": "### 10.4 Release Notes Template\n\n"
                    "Version: X.Y.Z\n"
                    "Release Date: YYYY-MM-DD\n\n"
                    "New Features:\n- [CONTENT REQUIRED]\n\n"
                    "Known Issues:\n- [CONTENT REQUIRED]\n",
            "10.5": "### 10.5 Localization & Multilingual Support\n\n"
                    "Support Materials:\n"
                    "- Notification templates (SMS/Email/Push) in supported languages\n"
                    "- Help center articles covering: limits, KYC process, troubleshooting\n\n"
                    "Localization Checklist:\n"
                    "- [ ] SMS notifications support target character encodings\n"
                    "- [ ] In-app help text translated and reviewed by native speakers\n"
                    "- [ ] Error messages culturally appropriate and actionable\n\n"
                    "Accessibility Standards:\n"
                    "- All customer-facing text meets WCAG 2.1 AA for readability\n",
        }

        # Find end of Section 10 (start of ## 11.)
        section_10_end = re.search(r"(?=^## 11\.)", content, re.MULTILINE)
        if not section_10_end:
            return None, content

        insert_pos = section_10_end.start()
        new_blocks = "\n".join(
            subsection_templates[label]
            for label in missing_labels
            if label in subsection_templates
        )
        if not new_blocks:
            return None, content

        new_content = content[:insert_pos] + new_blocks + "\n" + content[insert_pos:]
        status = "applied" if not self.dry_run else "pending"
        action = FixAction(
            gate_code="PRD-W006",
            description=f"Add missing Section 10 subsections: {', '.join(missing_labels)}",
            file=file_name,
            line=None,
            status=status,
            old_content=None,
            new_content=new_blocks[:120] + "...",
        )
        return action, new_content

    def _fix_missing_feature_ids(
        self,
        file_name: str,
        content: str,
        issue: ValidationIssue,
    ) -> tuple[Optional[FixAction], str]:
        """Fix PRD-W011: Add PRD.NN.22.xx element IDs to Section 7 feature table.

        Detects the doc number from existing element IDs, then rewrites the
        first table in Section 7.1 to prepend an ID column with sequential
        PRD.NN.22.01, .02, ... IDs.
        """
        section_7 = re.search(
            r"(^## 7\..+?)(?=^## \d+\.)",
            content,
            re.MULTILINE | re.DOTALL,
        )
        if not section_7:
            return None, content

        section_content = section_7.group(1)

        # Already has feature IDs → nothing to do
        if re.search(r"PRD\.\d{2}\.22\.\d{2}", section_content):
            return None, content

        # Infer doc number from any existing PRD.NN.xx.xx ID in the file
        doc_num_match = re.search(r"PRD\.(\d{2})\.\d{2}\.\d{2}", content)
        doc_num = doc_num_match.group(1) if doc_num_match else "01"

        # Find the first markdown table in Section 7.1
        table_pattern = re.compile(
            r"(### 7\.1[^\n]*\n+)"  # subsection heading
            r"(\|[^\n]+\|\n\|[-| :]+\|\n)"  # header + separator rows
            r"((?:\|[^\n]+\|\n)+)",  # data rows
        )
        table_match = table_pattern.search(section_content)
        if not table_match:
            return None, content

        heading = table_match.group(1)
        header_row = table_match.group(2).split('\n')
        data_rows = table_match.group(3).strip().split('\n')

        # Build new table with ID column prepended
        new_header = "| ID | " + header_row[0].lstrip('| ')
        new_separator = "|----|" + header_row[1].lstrip('|-')

        new_data_rows = []
        for idx, row in enumerate(data_rows, start=1):
            element_id = f"PRD.{doc_num}.22.{idx:02d}"
            new_data_rows.append(f"| {element_id} | " + row.lstrip('| '))

        new_table = (
            heading
            + new_header + "\n"
            + new_separator + "\n"
            + "\n".join(new_data_rows) + "\n"
        )

        old_table = table_match.group(0)
        section_start = section_7.start()
        new_section = section_content.replace(old_table, new_table, 1)
        new_content = content[:section_start] + new_section + content[section_7.end():]

        status = "applied" if not self.dry_run else "pending"
        action = FixAction(
            gate_code="PRD-W011",
            description=f"Add PRD.{doc_num}.22.xx element IDs to Section 7.1 feature table",
            file=file_name,
            line=None,
            status=status,
            old_content=old_table[:80],
            new_content=new_header,
        )
        return action, new_content

    def _fix_missing_story_ids(
        self,
        file_name: str,
        content: str,
        issue: ValidationIssue,
    ) -> tuple[Optional[FixAction], str]:
        """Fix PRD-W012: Add PRD.NN.09.xx element IDs to Section 8 user story table.

        Locates the first markdown table in Section 8.1, prepends an ID column
        with sequential PRD.NN.09.01, .02, ... IDs, and also fixes any existing
        single-digit suffixes (e.g. PRD.01.09.3 → PRD.01.09.03).
        """
        section_8 = re.search(
            r"(^## 8\..+?)(?=^## \d+\.)",
            content,
            re.MULTILINE | re.DOTALL,
        )
        if not section_8:
            return None, content

        section_content = section_8.group(1)

        # Already has user story IDs → only fix formatting
        if re.search(r"PRD\.\d{2}\.09\.\d{2}", section_content):
            # Fix single-digit suffixes: PRD.01.09.3 → PRD.01.09.03
            fixed = re.sub(
                r"(PRD\.(\d{2})\.09\.)(\d)(?!\d)",
                lambda m: f"{m.group(1)}{int(m.group(3)):02d}",
                section_content,
            )
            if fixed == section_content:
                return None, content
            new_content = content[: section_8.start()] + fixed + content[section_8.end() :]
            status = "applied" if not self.dry_run else "pending"
            action = FixAction(
                gate_code="PRD-W012",
                description="Normalize user story IDs to zero-padded 4-segment format",
                file=file_name,
                line=None,
                status=status,
                old_content="PRD.NN.09.N",
                new_content="PRD.NN.09.0N",
            )
            return action, new_content

        # Infer doc number
        doc_num_match = re.search(r"PRD\.(\d{2})\.\d{2}\.\d{2}", content)
        doc_num = doc_num_match.group(1) if doc_num_match else "01"

        # Find first table in Section 8.1
        table_pattern = re.compile(
            r"(### 8\.1[^\n]*\n+)"
            r"(\|[^\n]+\|\n\|[-| :]+\|\n)"
            r"((?:\|[^\n]+\|\n)+)",
        )
        table_match = table_pattern.search(section_content)
        if not table_match:
            return None, content

        heading = table_match.group(1)
        header_row = table_match.group(2).split('\n')
        data_rows = table_match.group(3).strip().split('\n')

        new_header = "| ID | " + header_row[0].lstrip('| ')
        new_separator = "|----|" + header_row[1].lstrip('|-')

        new_data_rows = []
        for idx, row in enumerate(data_rows, start=1):
            element_id = f"PRD.{doc_num}.09.{idx:02d}"
            new_data_rows.append(f"| {element_id} | " + row.lstrip('| '))

        new_table = (
            heading
            + new_header + "\n"
            + new_separator + "\n"
            + "\n".join(new_data_rows) + "\n"
        )

        old_table = table_match.group(0)
        section_start = section_8.start()
        new_section = section_content.replace(old_table, new_table, 1)
        new_content = content[:section_start] + new_section + content[section_8.end():]

        status = "applied" if not self.dry_run else "pending"
        action = FixAction(
            gate_code="PRD-W012",
            description=f"Add PRD.{doc_num}.09.xx element IDs to Section 8.1 user story table",
            file=file_name,
            line=None,
            status=status,
            old_content=old_table[:80],
            new_content=new_header,
        )
        return action, new_content

    def _fix_missing_quality_ids(
        self,
        file_name: str,
        content: str,
        issue: ValidationIssue,
    ) -> tuple[Optional[FixAction], str]:
        """Fix PRD-W019: Add PRD.NN.02.xx element IDs to Section 21.1 quality table.

        Locates the first markdown table in Section 21.1 and prepends an ID
        column with sequential PRD.NN.02.01, .02, ... IDs.
        """
        section_21 = re.search(
            r"(^## 21\..+?)(?=^## \d+\.|\Z)",
            content,
            re.MULTILINE | re.DOTALL,
        )
        if not section_21:
            return None, content

        section_content = section_21.group(1)

        # Already has quality attribute IDs → nothing to do
        if re.search(r"PRD\.\d{2}\.02\.\d{2}", section_content):
            return None, content

        # Infer doc number
        doc_num_match = re.search(r"PRD\.(\d{2})\.\d{2}\.\d{2}", content)
        doc_num = doc_num_match.group(1) if doc_num_match else "01"

        # Find first table in Section 21.1
        table_pattern = re.compile(
            r"(### 21\.1[^\n]*\n+)"
            r"(\|[^\n]+\|\n\|[-| :]+\|\n)"
            r"((?:\|[^\n]+\|\n)+)",
        )
        table_match = table_pattern.search(section_content)
        if not table_match:
            return None, content

        heading = table_match.group(1)
        header_row = table_match.group(2).split('\n')
        data_rows = table_match.group(3).strip().split('\n')

        new_header = "| ID | " + header_row[0].lstrip('| ')
        new_separator = "|----|" + header_row[1].lstrip('|-')

        new_data_rows = []
        for idx, row in enumerate(data_rows, start=1):
            element_id = f"PRD.{doc_num}.02.{idx:02d}"
            new_data_rows.append(f"| {element_id} | " + row.lstrip('| '))

        new_table = (
            heading
            + new_header + "\n"
            + new_separator + "\n"
            + "\n".join(new_data_rows) + "\n"
        )

        old_table = table_match.group(0)
        section_start = section_21.start()
        new_section = section_content.replace(old_table, new_table, 1)
        new_content = content[:section_start] + new_section + content[section_21.end():]

        status = "applied" if not self.dry_run else "pending"
        action = FixAction(
            gate_code="PRD-W019",
            description=f"Add PRD.{doc_num}.02.xx element IDs to Section 21.1 quality table",
            file=file_name,
            line=None,
            status=status,
            old_content=old_table[:80],
            new_content=new_header,
        )
        return action, new_content

    def _fix_missing_launch_criteria(
        self,
        file_name: str,
        content: str,
        issue: ValidationIssue,
    ) -> tuple[Optional[FixAction], str]:
        """Fix PRD-W021: Add Section 14.4 Release/Launch Criteria subsection.

        Appends a go/no-go decision checklist skeleton at the end of Section 14
        (before ## 15.) when no release/launch criteria subsection is found.
        """
        section_14 = re.search(
            r"(^## 14\..+?)(?=^## 15\.)",
            content,
            re.MULTILINE | re.DOTALL,
        )
        if not section_14:
            return None, content

        section_content = section_14.group(1)

        # Already has a dedicated launch/release criteria subsection → nothing to do
        if re.search(r"###\s+14\.\d+\s+.*(?:release|launch).*criteria", section_content, re.IGNORECASE):
            return None, content

        # Infer doc number
        doc_num_match = re.search(r"PRD\.(\d{2})\.\d{2}\.\d{2}", content)
        doc_num = doc_num_match.group(1) if doc_num_match else "01"

        # Find the highest existing 14.x subsection number
        existing_subs = re.findall(r"### 14\.(\d+)", section_content)
        next_sub = max((int(n) for n in existing_subs), default=3) + 1

        # Section 14 has no valid element type codes (SECTION_CODE_MAP["14"] = [])
        # so no PRD.NN.TT.SS IDs are generated here.
        launch_criteria_block = (
            f"\n### 14.{next_sub} Release/Launch Criteria\n\n"
            "**Go/No-Go Decision Checklist:**\n\n"
            "| Criterion | Status | Owner |\n"
            "|-----------|--------|-------|\n"
            "| All P1 functional tests pass | ☐ | Dev |\n"
            "| Performance baseline met | ☐ | QA |\n"
            "| Security review passed | ☐ | Security |\n"
            "| Compliance audit cleared | ☐ | Legal/Ops |\n"
            "| Monitoring & alerting configured | ☐ | Ops |\n"
            "| Rollback plan documented & tested | ☐ | Ops/Dev |\n\n"
            "**Launch Approval**: PO + CTO sign-off required before go-live.\n"
        )

        insert_pos = section_14.end()
        new_content = content[:insert_pos] + launch_criteria_block + content[insert_pos:]

        status = "applied" if not self.dry_run else "pending"
        action = FixAction(
            gate_code="PRD-W021",
            description=f"Add Section 14.{next_sub} Release/Launch Criteria checklist",
            file=file_name,
            line=None,
            status=status,
            old_content=None,
            new_content=launch_criteria_block[:120] + "...",
        )
        return action, new_content

    # -----------------------------------------------------------------------
    # LLM-only handoff methods
    # These generate a manual FixAction but do NOT modify document content.
    # The action appears in the fixer report as input for LLM remediation.
    # -----------------------------------------------------------------------

    def _handoff_brd_traceability(
        self,
        file_name: str,
        content: str,
        issue: ValidationIssue,
    ) -> tuple[Optional[FixAction], str]:
        """Generate LLM handoff for PRD-W004: systemic BRD traceability gap."""
        action = FixAction(
            gate_code="PRD-W004",
            description="LLM REQUIRED: Add @brd: traceability tags to PRD elements in §4, §7, §8, §9",
            file=file_name,
            line=issue.line,
            status="manual",
            old_content=None,
            new_content=None,
            context=(
                "Sections 4, 7, 8, 9 contain PRD elements with no @brd: tags.\n"
                "Required: Add `@brd: BRD.NN.TT.SS` reference to each PRD element.\n"
                "Format per element: `PRD.01.22.01 @brd: BRD.01.01.06`\n"
                "Reference §18 and §11 for BRD IDs already traced.\n"
                "LLM COMPLETION CODE: PRD-W004"
            ),
        )
        return action, content

    def _handoff_acceptance_criteria(
        self,
        file_name: str,
        content: str,
        issue: ValidationIssue,
    ) -> tuple[Optional[FixAction], str]:
        """Generate LLM handoff for PRD-W009: acceptance criteria insufficient."""
        action = FixAction(
            gate_code="PRD-W009",
            description="LLM REQUIRED: Restructure §11 acceptance criteria with PRD.NN.06.SS element IDs",
            file=file_name,
            line=issue.line,
            status="manual",
            old_content=None,
            new_content=None,
            context=(
                f"Validator detected {issue.message}.\n"
                "Required: Each AC on its own line as `- PRD.NN.06.SS: <measurable criterion>`.\n"
                "Example: `- PRD.01.06.01: ≥98% transaction success over 7-day launch window.`\n"
                "Minimum 3 ACs required; ≥5 recommended for MVP.\n"
                "LLM COMPLETION CODE: PRD-W009"
            ),
        )
        return action, content

    def _handoff_user_story_format(
        self,
        file_name: str,
        content: str,
        issue: ValidationIssue,
    ) -> tuple[Optional[FixAction], str]:
        """Generate LLM handoff for PRD-W013: non-standard user story format."""
        action = FixAction(
            gate_code="PRD-W013",
            description="LLM REQUIRED: Normalize §8 user stories to 'As a... I want... So that...' format",
            file=file_name,
            line=issue.line,
            status="manual",
            old_content=None,
            new_content=None,
            context=(
                "Section 8 user stories are missing required 'As a...' format.\n"
                "Required format: `As a [role], I want [feature], so that [benefit].`\n"
                "Each story must retain its PRD.NN.09.SS element ID.\n"
                "Example row: `| PRD.01.09.01 | As a sender, I want to lock an FX rate, "
                "so that I know the exact amount delivered. |`\n"
                "LLM COMPLETION CODE: PRD-W013"
            ),
        )
        return action, content

    def _handoff_priority_notation(
        self,
        file_name: str,
        content: str,
        issue: ValidationIssue,
    ) -> tuple[Optional[FixAction], str]:
        """Generate LLM handoff for PRD-W014: mixed priority notation."""
        action = FixAction(
            gate_code="PRD-W014",
            description="LLM REQUIRED: Standardize priority notation to MoSCoW throughout document",
            file=file_name,
            line=issue.line,
            status="manual",
            old_content=None,
            new_content=None,
            context=(
                "Document mixes P0-P4 numeric and MoSCoW (Must/Should/Could/Won't) notation.\n"
                "Required: Use MoSCoW labels as primary notation in all tables and lists.\n"
                "P-levels kept only in §1.2 legend row as parenthetical reference.\n"
                "Remove all 'P1-Must' compound forms; replace with 'Must'.\n"
                "Replace bare 'P2' in §6.2 with 'Should', 'P1' in §7.1 with 'Must'.\n"
                "LLM COMPLETION CODE: PRD-W014"
            ),
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
