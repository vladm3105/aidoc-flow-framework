"""PRD Duplicate Element Fixer Module.

Handles resolution of duplicate element ID definitions:
- Automatic renumbering of sequence numbers
- Cross-file duplicate detection
- Reference update tracking
- UCX-ACTION output for manual review

Duplicate Resolution Strategies:
1. Keep First: Keep first occurrence, renumber subsequent
2. Merge: Combine content from duplicates (manual)
3. Remove: Delete duplicate occurrences (with reference check)
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime, timezone

from ucx.validators.prd.fixer import FixAction, FixerResult
from ucx.validators.prd.schema import PRD_ELEMENT_ID_EXTRACT


@dataclass
class ElementOccurrence:
    """Represents a single occurrence of an element ID."""

    element_id: str
    file_path: Path
    line_number: int
    is_definition: bool
    context: str


@dataclass
class DuplicateGroup:
    """Group of duplicate element occurrences."""

    element_id: str
    occurrences: List[ElementOccurrence] = field(default_factory=list)

    @property
    def definitions(self) -> List[ElementOccurrence]:
        """Get definition occurrences only."""
        return [o for o in self.occurrences if o.is_definition]

    @property
    def references(self) -> List[ElementOccurrence]:
        """Get reference occurrences only."""
        return [o for o in self.occurrences if not o.is_definition]

    @property
    def is_cross_file(self) -> bool:
        """Check if duplicates span multiple files."""
        files = set(o.file_path for o in self.definitions)
        return len(files) > 1


class DuplicateFixer:
    """Handler for duplicate element ID resolution."""

    def __init__(
        self,
        dry_run: bool = True,
        strategy: str = "keep_first",
    ):
        """Initialize duplicate fixer.

        Args:
            dry_run: If True, don't apply changes
            strategy: Resolution strategy ('keep_first', 'merge', 'remove')
        """
        self.dry_run = dry_run
        self.strategy = strategy

    def find_duplicates(
        self,
        files: List[Path],
    ) -> List[DuplicateGroup]:
        """Find all duplicate element definitions.

        Args:
            files: List of PRD files to check

        Returns:
            List of duplicate groups
        """
        # Collect all element occurrences
        all_occurrences: Dict[str, List[ElementOccurrence]] = {}

        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
                occurrences = self._extract_occurrences(file_path, content)

                for occ in occurrences:
                    if occ.element_id not in all_occurrences:
                        all_occurrences[occ.element_id] = []
                    all_occurrences[occ.element_id].append(occ)
            except Exception:
                continue

        # Filter to duplicates only
        duplicates = []
        for element_id, occurrences in all_occurrences.items():
            definitions = [o for o in occurrences if o.is_definition]
            if len(definitions) > 1:
                group = DuplicateGroup(element_id=element_id, occurrences=occurrences)
                duplicates.append(group)

        return duplicates

    def fix_duplicates(
        self,
        files: List[Path],
        duplicates: Optional[List[DuplicateGroup]] = None,
    ) -> FixerResult:
        """Fix duplicate element IDs.

        Args:
            files: List of PRD files
            duplicates: Pre-computed duplicates (optional)

        Returns:
            FixerResult with all actions
        """
        result = FixerResult()

        if duplicates is None:
            duplicates = self.find_duplicates(files)

        for group in duplicates:
            if self.strategy == "keep_first":
                actions = self._fix_keep_first(group)
            elif self.strategy == "merge":
                actions = self._fix_suggest_merge(group)
            else:  # remove
                actions = self._fix_suggest_remove(group)

            for action in actions:
                result.add_action(action)

        return result

    def _extract_occurrences(
        self,
        file_path: Path,
        content: str,
    ) -> List[ElementOccurrence]:
        """Extract element occurrences from content."""
        occurrences = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for match in PRD_ELEMENT_ID_EXTRACT.finditer(line):
                doc_num = match.group(1)
                type_code = match.group(2)
                seq_num = match.group(3)
                element_id = f"PRD.{doc_num}.{type_code}.{seq_num}"

                # Determine if definition
                prefix = line[:match.start()].strip()
                is_definition = self._is_definition_context(prefix)

                # Get context
                start = max(0, match.start() - 30)
                end = min(len(line), match.end() + 30)
                context = line[start:end]

                occurrences.append(ElementOccurrence(
                    element_id=element_id,
                    file_path=file_path,
                    line_number=line_num,
                    is_definition=is_definition,
                    context=context,
                ))

        return occurrences

    def _is_definition_context(self, prefix: str) -> bool:
        """Check if prefix indicates definition context."""
        definition_indicators = [
            prefix == "",
            prefix == "-",
            prefix == "*",
            prefix.endswith("|"),
            prefix.endswith("**"),
            re.match(r"^\s*[-*]\s*$", prefix),
        ]
        return any(definition_indicators)

    def _fix_keep_first(self, group: DuplicateGroup) -> List[FixAction]:
        """Apply keep-first strategy: renumber subsequent duplicates."""
        actions = []
        definitions = group.definitions

        if len(definitions) < 2:
            return actions

        # Keep first, renumber rest
        first = definitions[0]
        element_parts = group.element_id.split('.')
        doc_num = element_parts[1]
        type_code = element_parts[2]

        # Find next available sequence number
        existing_seqs = self._find_existing_sequences(
            first.file_path.parent, doc_num, type_code
        )
        next_seq = max(existing_seqs) + 1 if existing_seqs else 1

        for dup in definitions[1:]:
            new_seq = str(next_seq).zfill(2)
            new_id = f"PRD.{doc_num}.{type_code}.{new_seq}"

            actions.append(FixAction(
                gate_code="PRD-E017",
                description=f"Renumber duplicate {group.element_id} to {new_id}",
                file=dup.file_path.name,
                line=dup.line_number,
                status="pending",
                old_content=group.element_id,
                new_content=new_id,
                context=f"First definition at {first.file_path.name}:{first.line_number}",
            ))
            next_seq += 1

        # Track reference updates needed
        for ref in group.references:
            actions.append(FixAction(
                gate_code="PRD-W007",
                description=f"Review reference to duplicate {group.element_id}",
                file=ref.file_path.name,
                line=ref.line_number,
                status="manual",
                old_content=group.element_id,
                new_content=None,
                context="Update reference to correct element after renumbering",
            ))

        return actions

    def _fix_suggest_merge(self, group: DuplicateGroup) -> List[FixAction]:
        """Suggest merging duplicate definitions."""
        actions = []
        definitions = group.definitions

        if len(definitions) < 2:
            return actions

        # Create merge suggestion
        locations = ", ".join(
            f"{d.file_path.name}:{d.line_number}" for d in definitions
        )

        actions.append(FixAction(
            gate_code="PRD-E017",
            description=f"Merge {len(definitions)} definitions of {group.element_id}",
            file=definitions[0].file_path.name,
            line=definitions[0].line_number,
            status="manual",
            old_content=None,
            new_content=None,
            context=f"Definitions at: {locations}",
        ))

        return actions

    def _fix_suggest_remove(self, group: DuplicateGroup) -> List[FixAction]:
        """Suggest removing duplicate definitions."""
        actions = []
        definitions = group.definitions

        if len(definitions) < 2:
            return actions

        # Keep first, suggest removing rest
        first = definitions[0]

        for dup in definitions[1:]:
            actions.append(FixAction(
                gate_code="PRD-E017",
                description=f"Remove duplicate definition of {group.element_id}",
                file=dup.file_path.name,
                line=dup.line_number,
                status="manual",
                old_content=dup.context,
                new_content="[REMOVED - duplicate]",
                context=f"Keep definition at {first.file_path.name}:{first.line_number}",
            ))

        return actions

    def _find_existing_sequences(
        self,
        directory: Path,
        doc_num: str,
        type_code: str,
    ) -> Set[int]:
        """Find existing sequence numbers for a type code."""
        sequences = set()
        pattern = re.compile(rf"PRD\.{doc_num}\.{type_code}\.(\d{{2}})")

        for file_path in directory.glob("*.md"):
            try:
                content = file_path.read_text(encoding='utf-8')
                for match in pattern.finditer(content):
                    sequences.add(int(match.group(1)))
            except Exception:
                continue

        return sequences


def find_and_fix_duplicates(
    files: List[Path],
    dry_run: bool = True,
    strategy: str = "keep_first",
) -> FixerResult:
    """Convenience function to find and fix duplicates.

    Args:
        files: List of PRD files
        dry_run: If True, don't apply changes
        strategy: Resolution strategy

    Returns:
        FixerResult with all actions
    """
    fixer = DuplicateFixer(dry_run=dry_run, strategy=strategy)
    return fixer.fix_duplicates(files)


def generate_duplicate_report(files: List[Path]) -> str:
    """Generate a report of duplicate elements.

    Args:
        files: List of PRD files

    Returns:
        Markdown report of duplicates
    """
    fixer = DuplicateFixer()
    duplicates = fixer.find_duplicates(files)

    lines = ["# PRD Duplicate Element Report", ""]
    lines.append(f"**Generated**: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"**Files Scanned**: {len(files)}")
    lines.append(f"**Duplicates Found**: {len(duplicates)}")
    lines.append("")

    if not duplicates:
        lines.append("*No duplicate element definitions found.*")
        return "\n".join(lines)

    lines.append("## Duplicate Groups")
    lines.append("")

    for i, group in enumerate(duplicates, 1):
        lines.append(f"### {i}. {group.element_id}")
        lines.append("")

        if group.is_cross_file:
            lines.append("**Cross-file duplicate**")
            lines.append("")

        lines.append("| File | Line | Context |")
        lines.append("|------|------|---------|")

        for defn in group.definitions:
            context = defn.context[:50] + "..." if len(defn.context) > 50 else defn.context
            context = context.replace("|", "\\|")
            lines.append(f"| {defn.file_path.name} | {defn.line_number} | {context} |")

        lines.append("")

        if group.references:
            lines.append(f"**References**: {len(group.references)}")
            lines.append("")

    return "\n".join(lines)
