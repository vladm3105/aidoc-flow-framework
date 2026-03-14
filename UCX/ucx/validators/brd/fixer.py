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
from ucx.validators.brd.duplicate_fixer import DuplicateElementFixer


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
    "VAL-E002",  # Missing/invalid YAML frontmatter - add from scratch
    # Tier 1 element ID fixes
    "GATE-E008",  # Duplicate element ID - renumber automatically
    "BRD-E020",  # Invalid element type code - remap to valid code
    # Tier 1 file size fixes
    "GATE-E010",  # File exceeds 20K tokens - auto-split at section boundaries
    # Tier 2 count mismatch fixes
    "GATE-W003",  # Count mismatch (stated vs actual)
    "DIAG-W001",  # Diagram node count mismatch
    # Tier 2 diagram advisory fixes
    "BRD-W011",  # Missing C4-L1 diagram - add request notice for ADR
    "BRD-W012",  # Missing DFD-L0 diagram - add request notice for ADR
    "BRD-W013",  # Sequence diagram without tag - auto-classify
    "BRD-W014",  # Missing diagram intent header - add template
    # Tier 2 dependency and section fixes
    "BRD-W010",  # Missing @depends tags - add with auto-detected BRD refs
    "GATE-W008",  # Element in wrong section - move to correct section file
}

# Invalid type code remapping table
# Maps invalid codes to valid BRD type codes based on likely intent
INVALID_CODE_REMAP: Dict[str, str] = {
    # Common invalid codes → most likely valid code
    "00": "01",  # Likely meant Functional Requirement
    "11": "01",  # Functional Requirement
    "12": "01",  # Functional Requirement
    "13": "01",  # Functional Requirement
    "14": "01",  # Functional Requirement
    "15": "01",  # Functional Requirement
    "16": "01",  # Functional Requirement
    "17": "01",  # Functional Requirement
    "18": "01",  # Functional Requirement
    "19": "01",  # Functional Requirement
    "20": "02",  # Quality Attribute
    "21": "01",  # Functional Requirement
    "25": "05",  # Dependency
    "26": "06",  # Acceptance Criteria
    "27": "07",  # Risk
    "28": "08",  # Metric
    "29": "09",  # User Story
    "30": "03",  # Constraint
    "31": "03",  # Constraint
    "33": "03",  # Constraint
    "34": "04",  # Assumption
    "35": "05",  # Dependency
    "36": "06",  # Acceptance Criteria
    "37": "07",  # Risk
    "38": "08",  # Metric
    "39": "09",  # User Story
    "40": "04",  # Assumption
    "41": "01",  # Functional Requirement
    "42": "02",  # Quality Attribute
    "43": "03",  # Constraint
    "44": "04",  # Assumption
    "45": "05",  # Dependency
    "46": "06",  # Acceptance Criteria
    "47": "07",  # Risk
    "48": "08",  # Metric
    "49": "09",  # User Story
    "50": "05",  # Dependency
    "51": "01",  # Functional Requirement
    "52": "02",  # Quality Attribute
    "53": "03",  # Constraint
    "54": "04",  # Assumption
    "55": "05",  # Dependency
    "56": "06",  # Acceptance Criteria
    "57": "07",  # Risk
    "58": "08",  # Metric
    "59": "09",  # User Story
    "60": "06",  # Acceptance Criteria
    "61": "01",  # Functional Requirement
    "62": "02",  # Quality Attribute
    "63": "03",  # Constraint
    "64": "04",  # Assumption
    "65": "05",  # Dependency
    "66": "06",  # Acceptance Criteria
    "67": "07",  # Risk
    "68": "08",  # Metric
    "69": "09",  # User Story
    "70": "07",  # Risk
    "71": "01",  # Functional Requirement
    "72": "02",  # Quality Attribute
    "73": "03",  # Constraint
    "74": "04",  # Assumption
    "75": "05",  # Dependency
    "76": "06",  # Acceptance Criteria
    "77": "07",  # Risk
    "78": "08",  # Metric
    "79": "09",  # User Story
    "80": "08",  # Metric
    "81": "01",  # Functional Requirement
    "82": "02",  # Quality Attribute
    "83": "03",  # Constraint
    "84": "04",  # Assumption
    "85": "05",  # Dependency
    "86": "06",  # Acceptance Criteria
    "87": "07",  # Risk
    "88": "08",  # Metric
    "89": "09",  # User Story
    "90": "91",  # Performance Requirement (closest QA code)
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
        """Fix BRD-E002 which can mean either missing custom_fields OR missing Section 0.

        Check the issue context to determine which fix to apply:
        - "Missing Section 0" → Add Document Control section
        - "Missing required field" → Add custom_fields
        """
        file_path = issue.file_path
        content = self._get_file_content(file_path)
        context = issue.context or ""

        # Check if this is a "Missing Section 0" error
        if "Section 0" in context or "Document Control" in context:
            return self._fix_brd_e009(issue)

        fm, fm_str, body = self._parse_frontmatter(content)

        changes = []

        # If no frontmatter exists, create it from scratch
        if fm is None:
            # Extract doc_id from filename (e.g., BRD-03.6-6_1_requirements → BRD-03.6-6)
            doc_id = file_path.stem.split("_")[0] if "_" in file_path.stem else file_path.stem
            fm = {
                "doc_id": doc_id,
                "title": f"{doc_id} Section",
                "tags": ["brd", "layer-1-artifact"],
                "custom_fields": {
                    "document_type": "brd",
                    "artifact_type": "BRD",
                    "layer": 1,
                }
            }
            body = content  # Entire content becomes body
            changes.append("Created frontmatter from scratch")

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

    def _fix_val_e002(self, issue: ValidationIssue) -> FixResult:
        """Fix missing or invalid YAML frontmatter by creating it from scratch."""
        file_path = issue.file_path
        content = self._get_file_content(file_path)
        fm, fm_str, body = self._parse_frontmatter(content)

        if fm is not None:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message="Frontmatter already exists"
            )

        # Extract doc_id from filename
        doc_id = file_path.stem.split("_")[0] if "_" in file_path.stem else file_path.stem

        # Create new frontmatter
        fm = {
            "doc_id": doc_id,
            "title": f"{doc_id} Section",
            "tags": ["brd", "layer-1-artifact"],
            "custom_fields": {
                "document_type": "brd",
                "artifact_type": "BRD",
                "layer": 1,
            }
        }

        new_content = self._rebuild_content(fm, content)
        self._set_file_content(file_path, new_content)

        return FixResult(
            code=issue.code,
            file_path=file_path,
            fixed=True,
            message="Created YAML frontmatter from scratch",
            changes=[
                f"Added doc_id: {doc_id}",
                "Added tags: brd, layer-1-artifact",
                "Added custom_fields with document_type, artifact_type, layer"
            ]
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

    def _fix_gate_e008(self, issue: ValidationIssue) -> FixResult:
        """Fix duplicate element ID by renumbering.

        Uses the DuplicateElementFixer to:
        1. Identify all element IDs across the BRD
        2. Find duplicates (second occurrence of same ID)
        3. Renumber duplicates with next available sequence number
        4. Update all references to renamed IDs

        Note: This fix operates on the entire BRD directory, not just one file.
        Multiple GATE-E008 issues in the same validation run will be consolidated
        into a single fix operation.
        """
        file_path = issue.file_path
        if not file_path:
            return FixResult(
                code=issue.code,
                file_path=self.doc_path,
                fixed=False,
                message="No file path specified"
            )

        # Determine the BRD directory (parent of the file)
        brd_dir = file_path.parent
        if brd_dir.name.endswith(".md"):
            brd_dir = brd_dir.parent

        # Check if we've already processed this directory in this run
        cache_key = f"_duplicate_fix_done_{brd_dir}"
        if hasattr(self, cache_key):
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=True,
                message="Already processed in batch operation",
                changes=["Duplicate fix applied in earlier batch"]
            )

        # Run duplicate fixer on the entire directory
        try:
            fixer = DuplicateElementFixer(brd_dir, verbose=self.verbose)
            result = fixer.fix_duplicates()

            # Mark directory as processed
            setattr(self, cache_key, True)

            if result.renames:
                changes = [
                    f"Renamed {len(result.renames)} duplicate IDs",
                    f"Updated {result.references_updated} references",
                ]
                for rename in result.renames[:5]:  # Show first 5 renames
                    changes.append(f"  {rename.old_id} → {rename.new_id}")
                if len(result.renames) > 5:
                    changes.append(f"  ... and {len(result.renames) - 5} more")

                return FixResult(
                    code=issue.code,
                    file_path=file_path,
                    fixed=True,
                    message=f"Renumbered {len(result.renames)} duplicate element IDs",
                    changes=changes
                )
            else:
                return FixResult(
                    code=issue.code,
                    file_path=file_path,
                    fixed=False,
                    message="No duplicates found to fix (may have been fixed already)"
                )

        except Exception as e:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message=f"Error fixing duplicates: {str(e)}"
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

    # =========================================================================
    # TIER 2 DIAGRAM ADVISORY FIXES
    # =========================================================================

    def _fix_brd_w011(self, issue: ValidationIssue) -> FixResult:
        """
        Fix missing C4-L1 architecture diagram.

        Instead of adding a false @diagram: c4-l1 tag (which would claim a
        diagram exists when it doesn't), this adds a @diagram-request notice
        that signals to downstream ADR layer that a C4 Level 1 context diagram
        should be created.

        The ADR layer agent can then decide whether to create the diagram
        based on architecture complexity.
        """
        return self._add_diagram_request(
            issue=issue,
            diagram_type="c4-l1",
            target_layer="ADR",
            rationale="BRD architecture requires C4 Level 1 context diagram for visualization",
            priority="recommended"
        )

    def _fix_brd_w012(self, issue: ValidationIssue) -> FixResult:
        """
        Fix missing DFD-L0 data flow diagram.

        Adds a @diagram-request notice for downstream ADR layer to create
        a DFD Level 0 diagram showing high-level data flows.
        """
        return self._add_diagram_request(
            issue=issue,
            diagram_type="dfd-l0",
            target_layer="ADR",
            rationale="BRD data flows require DFD Level 0 diagram for visualization",
            priority="recommended"
        )

    def _add_diagram_request(
        self,
        issue: ValidationIssue,
        diagram_type: str,
        target_layer: str,
        rationale: str,
        priority: str = "recommended"
    ) -> FixResult:
        """
        Add a diagram request notice to signal downstream layers.

        This creates honest traceability - the BRD signals that a diagram
        is needed, and downstream layers (PRD/ADR) decide whether to create it.

        Args:
            issue: The validation issue being fixed
            diagram_type: Type of diagram requested (c4-l1, dfd-l0, etc.)
            target_layer: Which layer should create the diagram (ADR, PRD)
            rationale: Why this diagram is recommended
            priority: Request priority (required, recommended, optional)

        Returns:
            FixResult indicating success or failure
        """
        file_path = issue.file_path
        content = self._get_file_content(file_path)

        # Check if request already exists
        if f"@diagram-request: {diagram_type}" in content:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message=f"Diagram request for {diagram_type} already exists"
            )

        # Build the diagram request notice
        request_notice = f"""
<!-- DIAGRAM REQUEST -->
<!-- @diagram-request: {diagram_type} -->
<!-- target_layer: {target_layer} -->
<!-- priority: {priority} -->
<!-- rationale: {rationale} -->
<!-- status: pending -->
"""

        # Find the best insertion point
        # Prefer: after frontmatter, before first heading
        fm, fm_str, body = self._parse_frontmatter(content)

        if fm is not None:
            # Insert after frontmatter
            new_body = request_notice + body
            new_content = self._rebuild_content(fm, new_body)
        else:
            # No frontmatter - insert at top
            new_content = request_notice + content

        self._set_file_content(file_path, new_content)

        return FixResult(
            code=issue.code,
            file_path=file_path,
            fixed=True,
            message=f"Added @diagram-request: {diagram_type} for {target_layer} layer",
            changes=[
                f"Added diagram request notice for {diagram_type}",
                f"Target layer: {target_layer}",
                f"Priority: {priority}"
            ]
        )

    def _fix_brd_w013(self, issue: ValidationIssue) -> FixResult:
        """
        Fix sequence diagram without classification tag.

        Detects the sequence diagram type (sync, async, error) by analyzing
        the Mermaid content and adds the appropriate @diagram: tag.
        """
        file_path = issue.file_path
        content = self._get_file_content(file_path)

        # Check if tag already exists
        if re.search(r"@diagram:\s*sequence-", content):
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message="Sequence diagram tag already exists"
            )

        # Detect sequence diagram type from content
        seq_type = self._detect_sequence_type(content)

        # Add the tag before the sequenceDiagram block
        tag_comment = f"<!-- @diagram: sequence-{seq_type} -->\n"

        # Find sequenceDiagram and insert tag before it
        new_content = re.sub(
            r"(```mermaid\s*\n\s*sequenceDiagram)",
            tag_comment + r"\1",
            content,
            count=1
        )

        if new_content != content:
            self._set_file_content(file_path, new_content)
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=True,
                message=f"Added @diagram: sequence-{seq_type} tag",
                changes=[f"Detected sequence type: {seq_type}", "Added classification tag"]
            )

        return FixResult(
            code=issue.code,
            file_path=file_path,
            fixed=False,
            message="Could not find sequenceDiagram block to tag"
        )

    def _detect_sequence_type(self, content: str) -> str:
        """
        Analyze sequence diagram content to determine type.

        Returns:
            "error" - if diagram contains error/failure handling
            "async" - if diagram contains async messaging patterns
            "sync" - default for synchronous request-response
        """
        content_lower = content.lower()

        # Check for error handling patterns
        error_indicators = [
            "error", "fail", "exception", "reject", "rollback",
            "compensat", "cancel", "timeout", "retry"
        ]
        if any(indicator in content_lower for indicator in error_indicators):
            return "error"

        # Check for async patterns
        async_indicators = [
            "async", "-->>" in content,  # Mermaid async arrow
            "event", "publish", "subscribe", "queue", "webhook",
            "callback", "notify", "broadcast"
        ]
        if any(
            indicator in content_lower if isinstance(indicator, str) else indicator
            for indicator in async_indicators
        ):
            return "async"

        # Default to sync
        return "sync"

    def _fix_brd_w014(self, issue: ValidationIssue) -> FixResult:
        """
        Fix missing diagram intent header.

        Adds a template diagram intent header with required fields that
        can be customized by the document author.
        """
        file_path = issue.file_path
        content = self._get_file_content(file_path)

        # Check what fields are already present
        required_fields = [
            "diagram_type:",
            "level:",
            "scope_boundary:",
            "upstream_refs:",
            "downstream_refs:"
        ]

        existing_fields = [f for f in required_fields if f in content]
        missing_fields = [f for f in required_fields if f not in content]

        if not missing_fields:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message="All diagram intent fields already present"
            )

        # Determine diagram type from content
        if "sequenceDiagram" in content:
            diagram_type = "sequence"
            level = "component"
        elif "flowchart" in content or "graph " in content:
            diagram_type = "flowchart"
            level = "process"
        elif "C4" in content or "Container" in content:
            diagram_type = "c4"
            level = "context"
        else:
            diagram_type = "architecture"
            level = "system"

        # Extract doc_id from file path for refs
        doc_id = file_path.stem.split("_")[0] if "_" in file_path.stem else file_path.stem

        # Build intent header
        intent_header = f"""<!-- DIAGRAM INTENT -->
<!-- diagram_type: {diagram_type} -->
<!-- level: {level} -->
<!-- scope_boundary: {doc_id}-boundary -->
<!-- upstream_refs: {doc_id} -->
<!-- downstream_refs: PRD, EARS, ADR -->
"""

        # Find first mermaid block and insert header before it
        new_content = re.sub(
            r"(```mermaid)",
            intent_header + r"\1",
            content,
            count=1
        )

        if new_content != content:
            self._set_file_content(file_path, new_content)
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=True,
                message="Added diagram intent header",
                changes=[
                    f"Added fields: {', '.join(missing_fields)}",
                    f"Detected diagram type: {diagram_type}",
                    f"Set level: {level}"
                ]
            )

        return FixResult(
            code=issue.code,
            file_path=file_path,
            fixed=False,
            message="Could not find Mermaid block for intent header"
        )

    # =========================================================================
    # TIER 2 DEPENDENCY AND SECTION FIXES
    # =========================================================================

    def _fix_brd_w010(self, issue: ValidationIssue) -> FixResult:
        """
        Fix missing @depends tags by auto-detecting BRD references in content.

        Scans the document for references to other BRDs (e.g., BRD-01, BRD.02)
        and adds them as @depends tags in the frontmatter.
        """
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

        # Extract current doc_id to exclude self-references
        current_doc_id = fm.get("doc_id", "")
        current_brd_num = ""
        if current_doc_id:
            match = re.search(r"BRD-?(\d+)", current_doc_id, re.IGNORECASE)
            if match:
                current_brd_num = match.group(1)

        # Find all BRD references in content
        # Patterns: BRD-01, BRD-02, BRD.01, BRD.02.xx.xx
        brd_patterns = [
            r"BRD-(\d{2,})",  # BRD-01, BRD-02
            r"BRD\.(\d{2,})\.\d{2}\.\d{2,}",  # BRD.01.01.01
        ]

        referenced_brds = set()
        for pattern in brd_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                brd_num = match.group(1)
                # Exclude self-references
                if brd_num != current_brd_num:
                    referenced_brds.add(f"BRD-{brd_num}")

        if not referenced_brds:
            # No BRD references found - add placeholder
            depends_value = ["BRD-01"]  # Default to platform BRD
        else:
            # Sort by BRD number
            depends_value = sorted(referenced_brds, key=lambda x: int(re.search(r"\d+", x).group()))

        # Ensure custom_fields exists
        if "custom_fields" not in fm:
            fm["custom_fields"] = {}

        # Add depends field
        fm["custom_fields"]["depends"] = depends_value

        # Also add @depends tag in body if not present
        depends_str = ", ".join(depends_value)
        depends_tag = f"<!-- @depends: {depends_str} -->"

        if "@depends:" not in body:
            # Insert after first heading
            h1_match = re.search(r"^# .+$", body, re.MULTILINE)
            if h1_match:
                insert_pos = h1_match.end()
                body = body[:insert_pos] + f"\n\n{depends_tag}\n" + body[insert_pos:]
            else:
                body = depends_tag + "\n" + body

        new_content = self._rebuild_content(fm, body)
        self._set_file_content(file_path, new_content)

        return FixResult(
            code=issue.code,
            file_path=file_path,
            fixed=True,
            message=f"Added @depends tags: {depends_str}",
            changes=[
                f"Added custom_fields.depends: {depends_value}",
                f"Added @depends comment tag",
                f"Auto-detected {len(referenced_brds)} BRD references"
            ]
        )

    def _fix_gate_w008(self, issue: ValidationIssue) -> FixResult:
        """
        Fix element in wrong section by moving it to the correct section file.

        Parses the issue context to extract:
        - Current section (where the element is)
        - Expected type code(s)
        - Actual type code (from the element)

        Then moves the element to the appropriate section file.
        """
        file_path = issue.file_path
        if not file_path:
            return FixResult(
                code=issue.code,
                file_path=self.doc_path,
                fixed=False,
                message="No file path specified"
            )

        content = self._get_file_content(file_path)

        # Parse context: "Section 6 expects '01' (...), found '32'"
        context = issue.context or ""
        match = re.search(r"Section (\d+) expects .+, found '(\d{2})'", context)
        if not match:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message="Cannot parse section mismatch from context"
            )

        current_section = match.group(1)
        element_type = match.group(2)

        # Map element type code to target section
        TYPE_TO_SECTION = {
            "01": "6",   # Functional Requirement → Section 6
            "02": "8",   # Integration Point → Section 8
            "03": "9",   # Constraint → Section 9
            "04": "10",  # Assumption → Section 10
            "05": "11",  # Risk → Section 11
            "06": "6",   # Acceptance Criteria → Section 6
            "22": "3",   # Feature Item → Section 3
            "24": "4",   # Stakeholder Need → Section 4
            "32": "5",   # Business Objective → Section 5
            "91": "7",   # Performance Requirement → Section 7
            "92": "7",   # Reliability Requirement → Section 7
            "94": "7",   # Scalability Requirement → Section 7
            "96": "7",   # Security Requirement → Section 7
            "98": "7",   # Observability Requirement → Section 7
            "99": "7",   # Maintainability Requirement → Section 7
        }

        target_section = TYPE_TO_SECTION.get(element_type)
        if not target_section:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message=f"Unknown element type code: {element_type}"
            )

        if target_section == current_section:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message="Element already in correct section"
            )

        # Find the target section file
        brd_dir = file_path.parent
        target_files = list(brd_dir.glob(f"*{target_section}_*.md"))
        if not target_files:
            target_files = list(brd_dir.glob(f"*.{target_section}_*.md"))

        if not target_files:
            # Create a TODO comment instead of failing
            line_no = issue.line or 0
            lines = content.split("\n")

            if 0 < line_no <= len(lines):
                # Find the element block (from this line to next element or section)
                element_line = lines[line_no - 1]

                # Add a TODO comment
                todo_comment = f"<!-- TODO: Move to Section {target_section} (element type {element_type}) -->"
                lines.insert(line_no - 1, todo_comment)

                new_content = "\n".join(lines)
                self._set_file_content(file_path, new_content)

                return FixResult(
                    code=issue.code,
                    file_path=file_path,
                    fixed=True,
                    message=f"Added TODO comment for move to Section {target_section}",
                    changes=[
                        f"Target section file not found, added TODO comment",
                        f"Element type {element_type} → Section {target_section}"
                    ]
                )

            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message=f"Could not find target section file for Section {target_section}"
            )

        target_file = target_files[0]

        # Extract the element block
        line_no = issue.line or 0
        if line_no <= 0:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message="No line number specified for element"
            )

        lines = content.split("\n")
        if line_no > len(lines):
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message=f"Line {line_no} out of range"
            )

        # Find element boundaries (### heading to next ### or ##)
        start_idx = line_no - 1
        end_idx = start_idx + 1

        # Look for ### element heading
        while start_idx > 0 and not lines[start_idx].startswith("### "):
            start_idx -= 1

        # Find end (next ### or ## or end of file)
        while end_idx < len(lines):
            if lines[end_idx].startswith("## ") or lines[end_idx].startswith("### "):
                break
            end_idx += 1

        # Extract element block
        element_block = "\n".join(lines[start_idx:end_idx])

        # Remove from source file
        new_source_lines = lines[:start_idx] + lines[end_idx:]
        new_source_content = "\n".join(new_source_lines)
        self._set_file_content(file_path, new_source_content)

        # Append to target file
        target_content = self._get_file_content(target_file)
        if not target_content.endswith("\n"):
            target_content += "\n"
        target_content += "\n" + element_block + "\n"
        self._set_file_content(target_file, target_content)

        return FixResult(
            code=issue.code,
            file_path=file_path,
            fixed=True,
            message=f"Moved element to Section {target_section}",
            changes=[
                f"Removed element from {file_path.name}",
                f"Appended element to {target_file.name}",
                f"Element type {element_type} → Section {target_section}"
            ]
        )

    def _fix_gate_e010(self, issue: ValidationIssue) -> FixResult:
        """
        Fix file exceeding 20K tokens by splitting at section boundaries.

        Identifies ## section headers and splits the file into multiple
        section-based files, updating the index accordingly.
        """
        file_path = issue.file_path
        if not file_path:
            return FixResult(
                code=issue.code,
                file_path=self.doc_path,
                fixed=False,
                message="No file path specified"
            )

        content = self._get_file_content(file_path)

        # Parse frontmatter
        fm, fm_str, body = self._parse_frontmatter(content)

        # Find all ## section headers
        section_pattern = re.compile(r"^(## \d+\..*?)(?=^## \d+\.|\Z)", re.MULTILINE | re.DOTALL)
        sections = section_pattern.findall(body)

        if len(sections) < 2:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message="Not enough sections to split (need at least 2)"
            )

        # Get BRD directory and doc_id
        brd_dir = file_path.parent
        doc_id = fm.get("doc_id", file_path.stem.split(".")[0]) if fm else file_path.stem.split(".")[0]

        # Estimate tokens per section (rough: 1 token ≈ 4 chars)
        section_tokens = [(s, len(s) // 4) for s in sections]
        total_tokens = sum(t for _, t in section_tokens)

        # Split strategy: combine small sections, separate large ones
        MAX_SECTION_TOKENS = 15000  # Leave room for overhead
        current_group = []
        current_tokens = 0
        groups = []

        for section_content, tokens in section_tokens:
            if current_tokens + tokens > MAX_SECTION_TOKENS and current_group:
                groups.append(current_group)
                current_group = [section_content]
                current_tokens = tokens
            else:
                current_group.append(section_content)
                current_tokens += tokens

        if current_group:
            groups.append(current_group)

        if len(groups) < 2:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message="Content cannot be split effectively (all sections fit in one file)"
            )

        # Create new section files
        created_files = []
        index_entries = []

        for i, group in enumerate(groups):
            # Extract section numbers from group
            section_nums = []
            for section_content in group:
                match = re.match(r"## (\d+)\.", section_content)
                if match:
                    section_nums.append(match.group(1))

            if not section_nums:
                continue

            # Determine filename
            if len(section_nums) == 1:
                section_id = section_nums[0]
            else:
                section_id = f"{section_nums[0]}-{section_nums[-1]}"

            # Get section title from first section
            title_match = re.match(r"## \d+\.\s*(.+)", group[0])
            title_slug = title_match.group(1).lower().replace(" ", "_")[:30] if title_match else "content"
            title_slug = re.sub(r"[^a-z0-9_]", "", title_slug)

            new_filename = f"{doc_id}.{section_id}_{title_slug}.md"
            new_path = brd_dir / new_filename

            # Create file content with complete BRD frontmatter
            new_content = f"""---
doc_id: {doc_id}.{section_id}
title: "{doc_id} Section {section_id}"
tags:
  - brd
  - layer-1-artifact
  - section-fragment
custom_fields:
  document_type: brd
  artifact_type: BRD
  layer: 1
  parent_doc: {doc_id}
  section_range: "{section_id}"
---

{"".join(group)}
"""
            new_path.write_text(new_content, encoding="utf-8")
            created_files.append(new_filename)
            index_entries.append(f"- [{doc_id}.{section_id}](./{new_filename})")

        # Update original file to be an index
        if fm is None:
            fm = {}

        fm["custom_fields"] = fm.get("custom_fields", {})
        fm["custom_fields"]["layout"] = "section-based"
        fm["custom_fields"]["sections"] = created_files

        # Create index body
        index_body = f"""
# {doc_id} Index

This document has been split into section-based files for maintainability.

## Section Files

{chr(10).join(index_entries)}

---

*Auto-split by UCX Framework v1.14.9 due to token limit (GATE-E010)*
"""

        new_content = self._rebuild_content(fm, index_body)
        self._set_file_content(file_path, new_content)

        return FixResult(
            code=issue.code,
            file_path=file_path,
            fixed=True,
            message=f"Split into {len(created_files)} section files",
            changes=[
                f"Created {len(created_files)} section files",
                f"Updated {file_path.name} as index",
                f"Original: ~{total_tokens} tokens",
            ] + [f"  → {f}" for f in created_files[:5]] + (
                [f"  ... and {len(created_files) - 5} more"] if len(created_files) > 5 else []
            )
        )

    # =========================================================================
    # TIER 1 ELEMENT TYPE CODE FIX
    # =========================================================================

    def _fix_brd_e020(self, issue: ValidationIssue) -> FixResult:
        """
        Fix invalid element type code by remapping to a valid code.

        Parses the issue context to extract the invalid type code,
        then remaps it to the most likely valid code based on:
        1. The INVALID_CODE_REMAP table
        2. Section context (if available)
        3. Default fallback to "01" (Functional Requirement)

        This fix updates all occurrences of the invalid element ID
        in the file to use the new valid type code.
        """
        file_path = issue.file_path
        if not file_path:
            return FixResult(
                code=issue.code,
                file_path=self.doc_path,
                fixed=False,
                message="No file path specified"
            )

        content = self._get_file_content(file_path)

        # Parse context: "Invalid type code 'XX' in BRD.NN.XX.SS"
        context = issue.context or ""
        match = re.search(r"Invalid type code '(\d{2})' in (BRD\.\d{2,}\.\d{2}\.\d{2,})", context)
        if not match:
            # Try alternate format
            match = re.search(r"type code '(\d{2})'.*?(BRD\.\d{2,}\.\d{2}\.\d{2,})", context)

        if not match:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message="Cannot parse invalid type code from context"
            )

        invalid_code = match.group(1)
        element_id = match.group(2)

        # Determine the new valid code
        new_code = INVALID_CODE_REMAP.get(invalid_code)

        if not new_code:
            # Try to infer from section context
            section_match = re.search(r"section (\d+)", context.lower())
            if section_match:
                section = section_match.group(1)
                # Section to preferred code mapping
                SECTION_TO_CODE = {
                    "2": "23",  # Business Objectives
                    "3": "22",  # Feature Items
                    "4": "24",  # Stakeholder Needs
                    "5": "09",  # User Stories
                    "6": "01",  # Functional Requirements
                    "7": "02",  # Quality Attributes
                    "8": "03",  # Constraints
                    "9": "06",  # Acceptance Criteria
                    "10": "07", # Risks
                    "11": "05", # Dependencies
                }
                new_code = SECTION_TO_CODE.get(section, "01")
            else:
                # Default to Functional Requirement
                new_code = "01"

        # Build the new element ID
        parts = element_id.split(".")
        if len(parts) >= 4:
            # BRD.NN.TT.SS format
            new_element_id = f"{parts[0]}.{parts[1]}.{new_code}.{parts[3]}"
        else:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message=f"Cannot parse element ID format: {element_id}"
            )

        # Replace all occurrences of the old element ID with the new one
        old_pattern = re.escape(element_id)
        new_content = re.sub(old_pattern, new_element_id, content)

        if new_content == content:
            return FixResult(
                code=issue.code,
                file_path=file_path,
                fixed=False,
                message=f"Element ID {element_id} not found in file"
            )

        # Count replacements
        replacement_count = len(re.findall(old_pattern, content))

        self._set_file_content(file_path, new_content)

        return FixResult(
            code=issue.code,
            file_path=file_path,
            fixed=True,
            message=f"Remapped type code: {invalid_code} → {new_code}",
            changes=[
                f"Old ID: {element_id}",
                f"New ID: {new_element_id}",
                f"Replaced {replacement_count} occurrence(s)",
                f"Type: {invalid_code} → {new_code}"
            ]
        )
