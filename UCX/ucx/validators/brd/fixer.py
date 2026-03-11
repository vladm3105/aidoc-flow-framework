"""BRD Auto-Fixer for structural validation issues.

Provides deterministic fixes for common BRD validation errors:
- Missing metadata fields (custom_fields, tags)
- Missing Document Control fields
- Legacy status values

Usage:
    from ucx.validators.brd.fixer import BRDFixer

    fixer = BRDFixer(doc_path)
    result = fixer.fix_all(validation_result)
    # or
    result = fixer.fix_issue(issue)
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml

from ucx.validators.common.result import ValidationIssue


@dataclass
class FixResult:
    """Result of a fix operation."""

    code: str
    file_path: Path
    fixed: bool
    message: str
    changes: List[str] = field(default_factory=list)


@dataclass
class FixSummary:
    """Summary of all fix operations."""

    total_issues: int = 0
    fixed_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0
    results: List[FixResult] = field(default_factory=list)

    @property
    def all_fixed(self) -> bool:
        """Check if all issues were fixed."""
        return self.fixed_count == self.total_issues

    def add(self, result: FixResult):
        """Add a fix result."""
        self.total_issues += 1
        self.results.append(result)
        if result.fixed:
            self.fixed_count += 1
        elif "skip" in result.message.lower():
            self.skipped_count += 1
        else:
            self.failed_count += 1


# Error codes that can be auto-fixed
FIXABLE_CODES: Set[str] = {
    # Tier 1 structural fixes
    "BRD-E002",  # Missing custom_fields.document_type
    "BRD-E003",  # Missing tag 'brd'
    "BRD-E004",  # Missing tag 'layer-1-artifact'
    "BRD-E009",  # Missing Document Control fields
    "BRD-W005",  # Legacy development_status
    "VAL-W002",  # Legacy status value
    # Tier 2 count mismatch fixes
    "GATE-W003",  # Count mismatch (stated vs actual)
    "DIAG-W001",  # Diagram node count mismatch
}


class BRDFixer:
    """Auto-fixer for BRD structural issues."""

    def __init__(self, doc_path: Path, verbose: bool = False):
        """
        Initialize BRD fixer.

        Args:
            doc_path: Path to BRD document or directory
            verbose: Enable verbose output
        """
        self.doc_path = Path(doc_path)
        self.verbose = verbose
        self._file_cache: Dict[Path, str] = {}
        self._modified_files: Set[Path] = set()

    def fix_all(self, issues: List[ValidationIssue]) -> FixSummary:
        """
        Fix all fixable issues.

        Args:
            issues: List of validation issues to fix

        Returns:
            FixSummary with results
        """
        summary = FixSummary()

        # Group issues by file for efficient processing
        issues_by_file: Dict[Path, List[ValidationIssue]] = {}
        for issue in issues:
            if issue.code in FIXABLE_CODES and issue.file_path:
                file_path = issue.file_path
                if file_path not in issues_by_file:
                    issues_by_file[file_path] = []
                issues_by_file[file_path].append(issue)

        # Process each file
        for file_path, file_issues in issues_by_file.items():
            for issue in file_issues:
                result = self.fix_issue(issue)
                summary.add(result)

        # Write all modified files
        self._write_modified_files()

        return summary

    def fix_issue(self, issue: ValidationIssue) -> FixResult:
        """
        Fix a single validation issue.

        Args:
            issue: Validation issue to fix

        Returns:
            FixResult with outcome
        """
        if issue.code not in FIXABLE_CODES:
            return FixResult(
                code=issue.code,
                file_path=issue.file_path or self.doc_path,
                fixed=False,
                message=f"Not auto-fixable: {issue.code}"
            )

        if not issue.file_path:
            return FixResult(
                code=issue.code,
                file_path=self.doc_path,
                fixed=False,
                message="No file path specified"
            )

        # Dispatch to specific fixer
        fix_method = getattr(self, f"_fix_{issue.code.replace('-', '_').lower()}", None)
        if fix_method:
            return fix_method(issue)

        return FixResult(
            code=issue.code,
            file_path=issue.file_path,
            fixed=False,
            message=f"No fixer implemented for {issue.code}"
        )

    def _get_file_content(self, file_path: Path) -> str:
        """Get file content from cache or disk."""
        if file_path not in self._file_cache:
            self._file_cache[file_path] = file_path.read_text(encoding="utf-8")
        return self._file_cache[file_path]

    def _set_file_content(self, file_path: Path, content: str):
        """Set file content in cache and mark as modified."""
        self._file_cache[file_path] = content
        self._modified_files.add(file_path)

    def _write_modified_files(self):
        """Write all modified files to disk."""
        for file_path in self._modified_files:
            if file_path in self._file_cache:
                file_path.write_text(self._file_cache[file_path], encoding="utf-8")

    def _parse_frontmatter(self, content: str) -> Tuple[Optional[Dict], str, str]:
        """
        Parse YAML frontmatter from content.

        Returns:
            (frontmatter_dict, frontmatter_str, body)
        """
        if not content.startswith("---"):
            return None, "", content

        # Find closing ---
        lines = content.split("\n")
        end_idx = -1
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                end_idx = i
                break

        if end_idx == -1:
            return None, "", content

        frontmatter_str = "\n".join(lines[1:end_idx])
        body = "\n".join(lines[end_idx + 1:])

        try:
            frontmatter = yaml.safe_load(frontmatter_str)
            return frontmatter, frontmatter_str, body
        except yaml.YAMLError:
            return None, frontmatter_str, body

    def _rebuild_content(self, frontmatter: Dict, body: str) -> str:
        """Rebuild content from frontmatter dict and body."""
        # Use yaml.dump with specific formatting
        fm_str = yaml.dump(
            frontmatter,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120
        )
        return f"---\n{fm_str}---\n{body}"

    # =========================================================================
    # SPECIFIC FIXERS
    # =========================================================================

    def _fix_brd_e002(self, issue: ValidationIssue) -> FixResult:
        """Fix missing custom_fields.document_type."""
        file_path = issue.file_path
        content = self._get_file_content(file_path)
        fm, fm_str, body = self._parse_frontmatter(content)

        if fm is None:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message="Cannot parse frontmatter"
            )

        changes = []

        # Ensure custom_fields exists
        if "custom_fields" not in fm:
            fm["custom_fields"] = {}
            changes.append("Added custom_fields section")

        # Add document_type if missing
        if "document_type" not in fm["custom_fields"]:
            fm["custom_fields"]["document_type"] = "brd"
            changes.append("Added document_type: brd")

        # Add other common missing fields
        if "artifact_type" not in fm["custom_fields"]:
            fm["custom_fields"]["artifact_type"] = "BRD"
            changes.append("Added artifact_type: BRD")

        if "layer" not in fm["custom_fields"]:
            fm["custom_fields"]["layer"] = 1
            changes.append("Added layer: 1")

        if changes:
            new_content = self._rebuild_content(fm, body)
            self._set_file_content(file_path, new_content)
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=True,
                message="Fixed missing custom_fields",
                changes=changes
            )

        return FixResult(
            code=issue.code,
            file_path=file_path,
            fixed=False,
            message="No changes needed"
        )

    def _fix_brd_e003(self, issue: ValidationIssue) -> FixResult:
        """Fix missing 'brd' tag."""
        return self._add_tag(issue, "brd")

    def _fix_brd_e004(self, issue: ValidationIssue) -> FixResult:
        """Fix missing 'layer-1-artifact' tag."""
        return self._add_tag(issue, "layer-1-artifact")

    def _add_tag(self, issue: ValidationIssue, tag: str) -> FixResult:
        """Add a tag to frontmatter."""
        file_path = issue.file_path
        content = self._get_file_content(file_path)
        fm, fm_str, body = self._parse_frontmatter(content)

        if fm is None:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message="Cannot parse frontmatter"
            )

        # Ensure tags exists as list
        if "tags" not in fm:
            fm["tags"] = []
        elif isinstance(fm["tags"], str):
            fm["tags"] = [fm["tags"]]

        # Add tag if not present
        if tag not in fm["tags"]:
            fm["tags"].append(tag)
            new_content = self._rebuild_content(fm, body)
            self._set_file_content(file_path, new_content)
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=True,
                message=f"Added tag: {tag}",
                changes=[f"Added '{tag}' to tags"]
            )

        return FixResult(
            code=issue.code,
            file_path=file_path,
            fixed=False,
            message=f"Tag '{tag}' already present"
        )

    def _fix_brd_e009(self, issue: ValidationIssue) -> FixResult:
        """Fix missing Document Control fields.

        Note: This is a complex fix that may not be fully automatic.
        The validator checks for specific field names in a table format.
        If a Document Control section exists but uses different field names
        (e.g., "Project Name" vs "Project"), it may still report issues.

        This fixer only adds a Document Control section if NONE exists.
        It does NOT modify existing sections to avoid breaking content.
        """
        file_path = issue.file_path
        content = self._get_file_content(file_path)

        # Check for ANY Document Control section (various formats)
        doc_ctrl_patterns = [
            r"## 0\. Document Control",
            r"## Document Control",
            r"\| *Project Name *\|",
            r"\| *Document Version *\|",
            r"\| *Document Owner *\|",
        ]

        has_doc_control = any(re.search(p, content, re.IGNORECASE) for p in doc_ctrl_patterns)

        if has_doc_control:
            # Document Control exists - don't add duplicate
            # The issue may be about specific missing fields, but we skip auto-fix
            # to avoid creating duplicate sections or breaking existing content
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message="Document Control section exists; manual review needed for field names",
                changes=["Skipped: existing Document Control detected - verify field names match expected format"]
            )

        # No Document Control section - add one
        fm, fm_str, body = self._parse_frontmatter(content)

        required_fields = [
            ("Project Name", "[Project Name]"),
            ("Document Version", "1.0"),
            ("Date", "[YYYY-MM-DD]"),
            ("Document Owner", "[Owner Name]"),
            ("Status", "Draft"),
        ]

        doc_ctrl_section = "\n## 0. Document Control\n\n| Field | Value |\n|-------|-------|\n"
        for field_name, default in required_fields:
            doc_ctrl_section += f"| {field_name} | {default} |\n"
        doc_ctrl_section += "\n"

        # Insert after first heading or at start of body
        h1_match = re.search(r"^# .+$", body, re.MULTILINE)
        if h1_match:
            insert_pos = h1_match.end()
            body = body[:insert_pos] + "\n" + doc_ctrl_section + body[insert_pos:]
        else:
            body = doc_ctrl_section + body

        new_content = self._rebuild_content(fm, body) if fm else content
        self._set_file_content(file_path, new_content)

        return FixResult(
            code=issue.code,
            file_path=file_path,
            fixed=True,
            message="Added Document Control section",
            changes=["Added Section 0: Document Control with required fields"]
        )

    def _fix_brd_w005(self, issue: ValidationIssue) -> FixResult:
        """Fix legacy development_status → status migration."""
        file_path = issue.file_path
        content = self._get_file_content(file_path)
        fm, fm_str, body = self._parse_frontmatter(content)

        if fm is None:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message="Cannot parse frontmatter"
            )

        changes = []

        # Check custom_fields for development_status
        if "custom_fields" in fm:
            cf = fm["custom_fields"]
            if "development_status" in cf and "status" not in cf:
                cf["status"] = cf.pop("development_status")
                changes.append("Renamed development_status to status")

        if changes:
            new_content = self._rebuild_content(fm, body)
            self._set_file_content(file_path, new_content)
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=True,
                message="Migrated legacy status field",
                changes=changes
            )

        return FixResult(
            code=issue.code,
            file_path=file_path,
            fixed=False,
            message="No legacy status field found"
        )

    def _fix_val_w002(self, issue: ValidationIssue) -> FixResult:
        """Fix legacy status value (active → development or production)."""
        file_path = issue.file_path
        content = self._get_file_content(file_path)
        fm, fm_str, body = self._parse_frontmatter(content)

        if fm is None:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message="Cannot parse frontmatter"
            )

        # Status value mapping (legacy → canonical)
        status_map = {
            "active": "production",
            "draft": "development",
            "deprecated": "deprecated",  # Keep as-is
            "reference": "production",
            "planned": "development",
        }

        changes = []

        if "custom_fields" in fm and "status" in fm["custom_fields"]:
            old_status = fm["custom_fields"]["status"]
            if old_status in status_map:
                new_status = status_map[old_status]
                if old_status != new_status:
                    fm["custom_fields"]["status"] = new_status
                    changes.append(f"Updated status: {old_status} → {new_status}")

        if changes:
            new_content = self._rebuild_content(fm, body)
            self._set_file_content(file_path, new_content)
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=True,
                message="Updated legacy status value",
                changes=changes
            )

        return FixResult(
            code=issue.code,
            file_path=file_path,
            fixed=False,
            message="No legacy status value found"
        )

    def _fix_gate_w003(self, issue: ValidationIssue) -> FixResult:
        """Fix count mismatch (stated vs actual count).

        Parses the issue context to extract stated and actual counts,
        then updates the prose to match the actual count.

        IMPORTANT: Uses negative lookbehind to avoid matching:
        - Section numbers like "## 16.1" or "### 5.2"
        - Numbers in ranges like "3-10"
        - Numbers that are part of version numbers like "v1.2"
        """
        file_path = issue.file_path
        content = self._get_file_content(file_path)

        # Parse context: "Count mismatch: stated X, found Y"
        context = issue.context or ""
        match = re.search(r"stated (\d+), found (\d+)", context)
        if not match:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message="Cannot parse count mismatch from context"
            )

        stated_count = int(match.group(1))
        actual_count = int(match.group(2))

        # Find and replace count patterns in content
        # Pattern: "N requirements", "N user stories", etc.
        # Use negative lookbehind (?<![.\d#-]) to avoid matching:
        # - After "." (section numbers like 16.1)
        # - After digits (part of larger numbers)
        # - After "#" (markdown headings like ## 5)
        # - After "-" (ranges like 3-10)
        safe_prefix = r"(?<![.\d#-])"
        count_patterns = [
            (safe_prefix + r"(\b{}\b)(\s+(?:functional\s+)?requirements?\b)".format(stated_count), r"{}\2".format(actual_count)),
            (safe_prefix + r"(\b{}\b)(\s+user\s+stor(?:y|ies)\b)".format(stated_count), r"{}\2".format(actual_count)),
            (safe_prefix + r"(\b{}\b)(\s+(?:quality\s+)?attributes?\b)".format(stated_count), r"{}\2".format(actual_count)),
            (safe_prefix + r"(\b{}\b)(\s+(?:business\s+)?objectives?\b)".format(stated_count), r"{}\2".format(actual_count)),
            (safe_prefix + r"(\b{}\b)(\s+(?:acceptance\s+)?criteria\b)".format(stated_count), r"{}\2".format(actual_count)),
            (safe_prefix + r"(\b{}\b)(\s+constraints?\b)".format(stated_count), r"{}\2".format(actual_count)),
            (safe_prefix + r"(\b{}\b)(\s+assumptions?\b)".format(stated_count), r"{}\2".format(actual_count)),
            (safe_prefix + r"(\b{}\b)(\s+risks?\b)".format(stated_count), r"{}\2".format(actual_count)),
            (safe_prefix + r"(\b{}\b)(\s+dependencies?\b)".format(stated_count), r"{}\2".format(actual_count)),
            (safe_prefix + r"(\b{}\b)(\s+stakeholders?\b)".format(stated_count), r"{}\2".format(actual_count)),
            (safe_prefix + r"(\b{}\b)(\s+items?\b)".format(stated_count), r"{}\2".format(actual_count)),
        ]

        new_content = content
        changes = []

        for pattern, replacement in count_patterns:
            new_content_candidate = re.sub(pattern, replacement, new_content, flags=re.IGNORECASE)
            if new_content_candidate != new_content:
                new_content = new_content_candidate
                changes.append(f"Updated count: {stated_count} → {actual_count}")
                break  # Only fix first match

        if changes:
            self._set_file_content(file_path, new_content)
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=True,
                message=f"Fixed count mismatch: {stated_count} → {actual_count}",
                changes=changes
            )

        return FixResult(
            code=issue.code,
            file_path=file_path,
            fixed=False,
            message=f"Could not find count pattern for '{stated_count}' to replace"
        )

    def _fix_diag_w001(self, issue: ValidationIssue) -> FixResult:
        """Fix diagram node count mismatch in prose.

        Parses the issue context to extract claimed count and actual node count,
        then updates the prose to match the diagram.

        IMPORTANT: Uses negative lookbehind to avoid matching:
        - Numbers in ranges like "3-10 nodes"
        - Section numbers like "## 10.1"
        - Version numbers like "v10.2"
        """
        file_path = issue.file_path
        content = self._get_file_content(file_path)

        # Parse context: "Text claims X nodes, diagram (line Y) has Z nodes"
        context = issue.context or ""
        match = re.search(r"claims (\d+) (\w+).*has (\d+) nodes", context)
        if not match:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message="Cannot parse diagram count mismatch from context"
            )

        claimed_count = int(match.group(1))
        item_type = match.group(2)
        actual_count = int(match.group(3))

        # Build replacement pattern
        # Match: "10 nodes", "10 components", "10 services", etc.
        # Use negative lookbehind to avoid matching after ., -, #, or digits
        safe_prefix = r"(?<![.\d#-])"
        pattern = safe_prefix + r"(\b{}\b)(\s+{}\b)".format(claimed_count, item_type)
        replacement = r"{}\2".format(actual_count)

        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        if new_content != content:
            self._set_file_content(file_path, new_content)
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=True,
                message=f"Fixed diagram count: {claimed_count} → {actual_count} {item_type}",
                changes=[f"Updated prose: {claimed_count} {item_type} → {actual_count} {item_type}"]
            )

        return FixResult(
            code=issue.code,
            file_path=file_path,
            fixed=False,
            message=f"Could not find '{claimed_count} {item_type}' pattern to replace"
        )
