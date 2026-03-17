"""BRD Duplicate Element ID Fixer.

Provides automatic renumbering of duplicate element IDs across BRD documents.

Algorithm:
1. Scan all markdown files in BRD directory
2. Identify element ID definitions (not references)
3. Track first occurrence of each ID
4. Renumber duplicates by incrementing sequence number
5. Update references to renamed IDs across all files

Guardrails (v1.16.2):
- Circular rename prevention: IDs being renamed FROM are excluded from target pool
- Backtick-wrapped element IDs are treated as references (never renamed as duplicates)
- Reference context detection synced with element_codes.py

Usage:
    from ucx.validators.brd.duplicate_fixer import DuplicateElementFixer

    fixer = DuplicateElementFixer(brd_path)
    result = fixer.fix_duplicates()
    print(f"Renamed {len(result.renames)} duplicate IDs")

Note:
    The _is_reference_context() method should stay in sync with
    ucx.validators.brd.element_codes._is_reference_context().
    TODO: Consider refactoring to share this logic via a common module.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Element ID pattern: BRD.NN.TT.SS or BRD.NN.TT.SS.XX (3 or 4 part)
ELEMENT_ID_PATTERN = re.compile(r"\bBRD\.(\d{2,})\.(\d{2})\.(\d{2,})(?:\.(\d{2,}))?\b")

# Section heading pattern for tracking current section
SECTION_HEADING_PATTERN = re.compile(r"^#{2,3}\s+(\d+(?:\.\d+)*)\.")


@dataclass
class ElementLocation:
    """Location of an element ID in the codebase."""

    file_path: Path
    line_number: int
    full_id: str
    doc_num: str
    type_code: str
    seq_num: str
    is_definition: bool  # True if definition, False if reference
    context: str  # Line content for debugging


@dataclass
class RenameOperation:
    """A rename operation for a duplicate ID."""

    old_id: str
    new_id: str
    file_path: Path
    line_number: int
    reason: str


@dataclass
class DuplicateFixResult:
    """Result of duplicate fixing operation."""

    files_scanned: int = 0
    duplicates_found: int = 0
    renames: List[RenameOperation] = field(default_factory=list)
    references_updated: int = 0
    errors: List[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Check if operation completed successfully."""
        return len(self.errors) == 0


class DuplicateElementFixer:
    """Fixer for duplicate element IDs in BRD documents."""

    def __init__(self, brd_path: Path, verbose: bool = False, dry_run: bool = False):
        """
        Initialize duplicate fixer.

        Args:
            brd_path: Path to BRD document directory
            verbose: Enable verbose output
            dry_run: If True, only report changes without modifying files
        """
        self.brd_path = Path(brd_path)
        self.verbose = verbose
        self.dry_run = dry_run
        self._file_cache: Dict[Path, str] = {}
        self._modified_files: Set[Path] = set()

    def fix_duplicates(self) -> DuplicateFixResult:
        """
        Fix all duplicate element IDs in the BRD directory.

        Returns:
            DuplicateFixResult with details of all changes
        """
        result = DuplicateFixResult()

        # Step 1: Collect all element locations
        all_locations = self._collect_all_elements()
        result.files_scanned = len(set(loc.file_path for loc in all_locations))

        if self.verbose:
            print(f"Found {len(all_locations)} element occurrences across {result.files_scanned} files")

        # Step 2: Identify duplicates (only among definitions)
        definitions = [loc for loc in all_locations if loc.is_definition]
        duplicates = self._find_duplicates(definitions)
        result.duplicates_found = len(duplicates)

        if self.verbose:
            print(f"Found {len(duplicates)} duplicate definitions")

        # Step 3: Generate rename operations
        renames = self._generate_renames(duplicates, definitions)
        result.renames = renames

        if self.verbose:
            for rename in renames:
                print(f"  Rename: {rename.old_id} → {rename.new_id} in {rename.file_path.name}:{rename.line_number}")

        if self.dry_run:
            return result

        # Step 4: Apply renames to files
        for rename in renames:
            self._apply_rename(rename)

        # Step 5: Update references across all files
        result.references_updated = self._update_references(renames)

        # Step 6: Write modified files
        self._write_modified_files()

        return result

    def _collect_all_elements(self) -> List[ElementLocation]:
        """Collect all element ID occurrences across all markdown files."""
        locations = []

        # Find all markdown files, excluding generated/session directories
        md_files = [
            f for f in self.brd_path.glob("**/*.md")
            if not any(
                skip in f.parts
                for skip in [".ucx_review_session", ".doc_review_memory", ".backup", "__pycache__"]
            )
        ]

        for file_path in md_files:
            try:
                content = self._get_file_content(file_path)
                file_locations = self._parse_file_elements(file_path, content)
                locations.extend(file_locations)
            except Exception as e:
                if self.verbose:
                    print(f"Error processing {file_path}: {e}")

        return locations

    def _parse_file_elements(self, file_path: Path, content: str) -> List[ElementLocation]:
        """Parse a file and extract all element ID occurrences."""
        locations = []
        lines = content.splitlines()
        current_section: Optional[str] = None
        in_code_block = False

        for line_no, line in enumerate(lines, start=1):
            # Toggle code block state
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            # Skip code blocks
            if in_code_block:
                continue

            # Track current section
            section_match = SECTION_HEADING_PATTERN.match(line)
            if section_match:
                current_section = section_match.group(1)

            # Check if line is a reference context
            is_reference = self._is_reference_context(file_path, current_section, line)

            # Find all element IDs in line
            for match in ELEMENT_ID_PATTERN.finditer(line):
                full_id = match.group(0)
                doc_num = match.group(1)
                type_code = match.group(2)
                seq_num = match.group(3)

                locations.append(ElementLocation(
                    file_path=file_path,
                    line_number=line_no,
                    full_id=full_id,
                    doc_num=doc_num,
                    type_code=type_code,
                    seq_num=seq_num,
                    is_definition=not is_reference,
                    context=line.strip()[:100],
                ))

        return locations

    def _is_reference_context(
        self,
        file_path: Path,
        current_section: Optional[str],
        line: str,
    ) -> bool:
        """Determine if element ID appears in a reference context."""
        # Check filename for known reference-only files
        if "traceability" in file_path.name.lower():
            return True
        if "index" in file_path.name.lower():
            return True

        # Check if in Section 16 (Traceability section)
        if current_section and current_section.startswith("16"):
            return True

        # Check for backtick-wrapped element IDs (code-formatted references)
        # e.g., "per constraint `BRD.17.04.22`" or "(`BRD.11.03.01`: FinCEN)"
        # Backtick-wrapped IDs are always cross-references, never definitions
        if re.search(r'`BRD\.\d{2,}\.\d{2}\.\d{2,}(?:\.\d{2,})?`', line):
            return True

        # Check if this line contains a definition
        if self._is_definition_context(line):
            return False

        # Table rows are references
        stripped_line = line.strip()
        if stripped_line.startswith("|"):
            return True

        # Inline parenthetical references (supports 3 or 4 part IDs)
        # e.g., "requires intelligent orchestration (BRD.01.23.01)"
        # e.g., "supports target objective (BRD.14.23.01.02)"
        if re.search(r'\(BRD\.\d{2,}\.\d{2}\.\d{2,}(?:\.\d{2,})?\)', line):
            return True

        # "Related Requirements" style references
        # e.g., "- BRD.01.01.01 (Platform Architecture): Technology serves..."
        if re.match(r'^[-*]\s+BRD\.\d{2,}\.\d{2}\.\d{2,}\s+\(', stripped_line):
            return True

        # Constraint/driver reference patterns
        # e.g., "- Must operate within ~$2M seed runway (BRD.01.03.01)"
        if re.search(r'[-*]\s+.*\(BRD\.\d{2,}\.\d{2}\.\d{2,}\)', line):
            return True

        # Inline constraint references with colon (bullet points in Business Constraints)
        # e.g., "- BRD.02.03.02: Limited operations team capacity"
        # e.g., "BRD.02.03.01: Partner API rate limits vary by provider"
        if re.match(r'^[-*]?\s*BRD\.\d{2,}\.\d{2}\.\d{2,}:', stripped_line):
            return True

        # Business Driver/Constraint inline references
        # e.g., "**Business Driver**: BRD.02.23.01 (Reduce operational overhead)"
        if re.search(r'\*\*Business (Driver|Constraint)[s]?\*\*:.*BRD\.\d{2,}\.\d{2}\.\d{2,}', line):
            return True

        # "Related Requirements" section references
        # e.g., "- BRD.02.01.01-05 (All Partners): Webhook event sources"
        if re.match(r'^[-*]\s+BRD\.\d{2,}\.\d{2}\.\d{2,}', stripped_line):
            return True

        # Checkbox/task list items are references (summary lists)
        # e.g., "- [ ] P1 BRD.40.01.01 — Auth0 Authentication"
        # e.g., "- [x] BRD.05.01.01 — Completed item"
        if re.match(r'^[-*]\s+\[[ xX]\]', stripped_line):
            return True

        # Priority-prefixed items (P0/P1/P2 lists)
        # e.g., "- P1 BRD.40.01.01: Description"
        if re.match(r'^[-*]\s+P[0-3]\s+BRD\.\d{2,}\.\d{2}\.\d{2,}', stripped_line):
            return True

        # Em-dash separated items (common in summary lists)
        # e.g., "- BRD.40.01.01 — Auth0 Authentication"
        if re.search(r'BRD\.\d{2,}\.\d{2}\.\d{2,}\s+[—–-]\s+\w', line):
            return True

        # Category reference lists (ID followed by description in parentheses)
        # e.g., "- Compliance BRDs: BRD.03.01.01 (Audit Trail...)"
        # e.g., "- Quality Attributes: BRD.03.02.01 (Performance...)"
        if re.search(r'BRD\.\d{2,}\.\d{2}\.\d{2,}\s*\([^)]+\)', line):
            return True

        # Parenthetical references with target/constraint suffix (supports 3 or 4 part IDs)
        # e.g., "- Target operational float: ~$20k (BRD.14.23.01.02 target)"
        # e.g., "- Maximum timeout: 30s (BRD.14.09.01 constraint)"
        if re.search(r'\(BRD\.\d{2,}\.\d{2}\.\d{2,}(?:\.\d{2,})?\s+\w+\)', line):
            return True

        # @brd: cross-reference annotations
        # e.g., "per @brd: BRD.03.01.04 Section 4.1"
        if re.search(r'@brd:\s*BRD\.\d{2,}\.\d{2}\.\d{2,}', line):
            return True

        # Multiple IDs on same line (likely a reference list)
        # e.g., "BRD.03.01.01, BRD.03.01.07, BRD.03.01.09"
        ids_in_line = ELEMENT_ID_PATTERN.findall(line)
        if len(ids_in_line) > 1:
            return True

        # Range notation for element IDs
        # e.g., "BRD.03.32.01-11" or "BRD.03.01.01-05"
        if re.search(r'BRD\.\d{2,}\.\d{2}\.\d{2,}-\d+', line):
            return True

        # Review report files are references, not definitions
        if "_review_report" in str(file_path).lower():
            return True

        return False

    def _is_definition_context(self, line: str) -> bool:
        """Determine if element ID appears in a definition context."""
        stripped = line.strip()

        # Heading definition: ### BRD.01.01.01: Title
        if re.match(r'^#{2,4}\s+BRD\.\d{2,}\.\d{2}\.\d{2,}:', stripped):
            return True

        # Bold definition at start: **BRD.01.01.01**: Description
        if re.match(r'^\*\*BRD\.\d{2,}\.\d{2}\.\d{2,}\*\*:', stripped):
            return True

        # Bullet with bold definition: - **BRD.01.01.01**: Description
        if re.match(r'^[-*]\s+\*\*BRD\.\d{2,}\.\d{2}\.\d{2,}\*\*:', stripped):
            return True

        return False

    def _find_duplicates(self, definitions: List[ElementLocation]) -> List[ElementLocation]:
        """Find duplicate definitions (second and subsequent occurrences)."""
        seen: Dict[str, ElementLocation] = {}
        duplicates = []

        # Sort by file path and line number for deterministic first-occurrence
        sorted_defs = sorted(definitions, key=lambda x: (str(x.file_path), x.line_number))

        for loc in sorted_defs:
            if loc.full_id in seen:
                duplicates.append(loc)
            else:
                seen[loc.full_id] = loc

        return duplicates

    def _generate_renames(
        self,
        duplicates: List[ElementLocation],
        all_definitions: List[ElementLocation],
    ) -> List[RenameOperation]:
        """Generate rename operations for duplicates.

        Includes guardrails to prevent circular renames:
        1. Tracks all IDs being renamed FROM to prevent renaming TO those IDs
        2. Validates that new IDs don't conflict with pending renames
        """
        renames = []

        # Track all existing IDs and which have been used
        existing_ids: Set[str] = {loc.full_id for loc in all_definitions}
        pending_new_ids: Set[str] = set()

        # GUARDRAIL: Track IDs being renamed FROM to prevent circular renames
        # If we rename A->B, we must not later rename something TO A
        ids_being_renamed_from: Set[str] = {dup.full_id for dup in duplicates}

        for dup in duplicates:
            # Find next available sequence number
            # GUARDRAIL: Also exclude IDs that are sources of other renames
            excluded_ids = existing_ids | pending_new_ids | ids_being_renamed_from
            new_id = self._find_next_available_id(
                dup.doc_num,
                dup.type_code,
                excluded_ids,
            )

            if new_id:
                # GUARDRAIL: Double-check we're not creating a circular rename
                if new_id in ids_being_renamed_from:
                    if self.verbose:
                        print(f"  GUARDRAIL: Skipping rename {dup.full_id} → {new_id} (would create circular rename)")
                    continue

                pending_new_ids.add(new_id)
                renames.append(RenameOperation(
                    old_id=dup.full_id,
                    new_id=new_id,
                    file_path=dup.file_path,
                    line_number=dup.line_number,
                    reason=f"Duplicate ID at {dup.file_path.name}:{dup.line_number}",
                ))

        return renames

    def _find_next_available_id(
        self,
        doc_num: str,
        type_code: str,
        used_ids: Set[str],
    ) -> Optional[str]:
        """Find next available sequence number for an element ID."""
        # Start from 01 and find first unused
        for seq in range(1, 1000):
            seq_str = f"{seq:02d}" if seq < 100 else str(seq)
            candidate = f"BRD.{doc_num}.{type_code}.{seq_str}"
            if candidate not in used_ids:
                return candidate

        return None

    def _apply_rename(self, rename: RenameOperation) -> None:
        """Apply a single rename operation to a file."""
        content = self._get_file_content(rename.file_path)

        # Replace only at the specific line to avoid unintended changes
        lines = content.splitlines()
        if rename.line_number <= len(lines):
            old_line = lines[rename.line_number - 1]
            # Use word boundary to avoid partial matches
            new_line = re.sub(
                rf"\b{re.escape(rename.old_id)}\b",
                rename.new_id,
                old_line,
            )
            lines[rename.line_number - 1] = new_line
            new_content = "\n".join(lines)

            # Preserve trailing newline
            if content.endswith("\n"):
                new_content += "\n"

            self._set_file_content(rename.file_path, new_content)

    def _update_references(self, renames: List[RenameOperation]) -> int:
        """Update references to renamed IDs across all files.

        Note: Excludes historical/generated files to preserve audit trails:
        - .ucx_review_session/ (review session files)
        - .doc_review_memory/ (legacy session files)
        - *_review_report*.md (historical review reports)
        - *_audit_report*.md (historical audit reports)
        - *UCRem*.md (remediation reports)
        """
        if not renames:
            return 0

        # Build rename map
        rename_map = {r.old_id: r.new_id for r in renames}
        updated_count = 0

        # Get all markdown files, excluding generated/historical files
        # GUARDRAIL: Don't modify historical reports (preserve audit trail)
        md_files = [
            f for f in self.brd_path.glob("**/*.md")
            if not any(skip in f.parts for skip in [
                ".ucx_review_session", ".doc_review_memory", ".backup", "__pycache__"
            ])
            and "_review_report" not in f.name.lower()
            and "_audit_report" not in f.name.lower()
            and "ucrem" not in f.name.lower()
            and "_validation_report" not in f.name.lower()
        ]

        for file_path in md_files:
            original_content = self._get_file_content(file_path)
            new_content = original_content
            file_updated = False

            for old_id, new_id in rename_map.items():
                # Replace all occurrences (word boundary to avoid partial matches)
                pattern = rf"\b{re.escape(old_id)}\b"
                # Count in ORIGINAL content (before any modifications in this loop)
                # This ensures accurate counting even if renames overlap
                match_count = len(re.findall(pattern, original_content))
                if match_count > 0:
                    new_content = re.sub(pattern, new_id, new_content)
                    file_updated = True
                    updated_count += match_count

            if file_updated and new_content != original_content:
                self._set_file_content(file_path, new_content)

        return updated_count

    def _get_file_content(self, file_path: Path) -> str:
        """Get file content from cache or disk."""
        if file_path not in self._file_cache:
            self._file_cache[file_path] = file_path.read_text(encoding="utf-8")
        return self._file_cache[file_path]

    def _set_file_content(self, file_path: Path, content: str) -> None:
        """Set file content in cache and mark as modified."""
        self._file_cache[file_path] = content
        self._modified_files.add(file_path)

    def _write_modified_files(self) -> None:
        """Write all modified files to disk."""
        for file_path in self._modified_files:
            if file_path in self._file_cache:
                file_path.write_text(self._file_cache[file_path], encoding="utf-8")


def fix_duplicate_ids(brd_path: Path, verbose: bool = False, dry_run: bool = False) -> DuplicateFixResult:
    """
    Convenience function to fix duplicate element IDs.

    Args:
        brd_path: Path to BRD document directory
        verbose: Enable verbose output
        dry_run: If True, only report changes without modifying files

    Returns:
        DuplicateFixResult with details of all changes
    """
    fixer = DuplicateElementFixer(brd_path, verbose=verbose, dry_run=dry_run)
    return fixer.fix_duplicates()
