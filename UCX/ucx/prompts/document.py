"""Document loading for prompt inspection toolset.

This module provides the DocumentLoader class for loading
multi-file and single-file documents for prompt generation
and analysis.

Version: 1.14.1
"""

import re
from pathlib import Path
from typing import Any, Optional

from ucx.prompts.exceptions import DocumentNotFoundError


# Content preprocessing patterns
FRONTMATTER_PATTERN = re.compile(r'^---\n.*?\n---\n', re.DOTALL)
HTML_COMMENT_PATTERN = re.compile(r'<!--.*?-->', re.DOTALL)
NAVIGATION_PATTERN = re.compile(r'^>\s*\*\*Navigation\*\*:.*$', re.MULTILINE)

# Document metadata patterns (low-value for review)
METADATA_PATTERNS = [
    # Revision history tables
    re.compile(
        r'###?\s*Document Revision History\s*\n.*?(?=\n---|\n##[^#]|\Z)',
        re.DOTALL | re.IGNORECASE
    ),
    # Document control sections
    re.compile(
        r'##\s*Document Control\s*\n.*?(?=\n---|\n##[^#]|\Z)',
        re.DOTALL | re.IGNORECASE
    ),
    # Version/Date/Author tables (standalone)
    re.compile(
        r'\|\s*Version\s*\|\s*Date\s*\|\s*Author\s*\|.*?(?=\n\n|\n---|\n##|\Z)',
        re.DOTALL
    ),
    # Quick Statistics sections
    re.compile(
        r'##\s*Quick Statistics\s*\n.*?(?=\n---|\n##[^#]|\Z)',
        re.DOTALL | re.IGNORECASE
    ),
    # Section Index tables (LLM sees actual sections)
    re.compile(
        r'##\s*Section Index\s*\n.*?(?=\n---|\n##[^#]|\Z)',
        re.DOTALL | re.IGNORECASE
    ),
]


def preprocess_content(content: str, strip_frontmatter: bool = True,
                       strip_comments: bool = True,
                       strip_navigation: bool = True,
                       strip_metadata: bool = True) -> str:
    """Preprocess section content by removing non-essential artifacts.

    Args:
        content: Raw section content
        strip_frontmatter: Remove YAML frontmatter blocks
        strip_comments: Remove HTML comments (diagram requests, etc.)
        strip_navigation: Remove navigation breadcrumbs
        strip_metadata: Remove document metadata (revision history, etc.)

    Returns:
        Cleaned content with artifacts removed
    """
    result = content

    if strip_frontmatter:
        result = FRONTMATTER_PATTERN.sub('', result)

    if strip_comments:
        result = HTML_COMMENT_PATTERN.sub('', result)

    if strip_navigation:
        result = NAVIGATION_PATTERN.sub('', result)

    if strip_metadata:
        for pattern in METADATA_PATTERNS:
            result = pattern.sub('', result)

    # Clean up multiple blank lines (from removed content)
    result = re.sub(r'\n{3,}', '\n\n', result)

    # Clean up multiple --- separators (from removed sections)
    result = re.sub(r'(\n---\s*){2,}', '\n---\n', result)

    # Strip leading/trailing whitespace
    result = result.strip()

    return result


class DocumentLoader:
    """Unified document loading for prompt generation and analysis.

    Supports both multi-file documents (directory with section files)
    and single-file documents.

    Example:
        loader = DocumentLoader()
        content, sections = loader.load(Path("docs/01_BRD/BRD-01/"), "brd")
        print(f"Loaded {len(sections)} sections")
    """

    # Patterns for section file naming
    SECTION_FILE_PATTERN = re.compile(
        r"^([A-Z]+-\d+)\.(\d+(?:\.\d+)?)_(.+)\.md$", re.IGNORECASE
    )

    # Files to skip when loading
    SKIP_PATTERNS = [
        r"\.UCR_",  # Review reports
        r"\.V_",  # Validation reports
        r"\.ucx_review_session",  # Review memory
        r"\.ucx_create_session",  # Creation prompt history
        r"^\.prompt_cache",  # Generated prompts
        r"^\.",  # Hidden files
    ]

    def __init__(self):
        """Initialize DocumentLoader."""
        self._skip_patterns = [re.compile(p) for p in self.SKIP_PATTERNS]

    def load(
        self, doc_path: Path, doc_type: str
    ) -> tuple[str, dict[str, str], dict[str, int]]:
        """Load document content and parse into sections.

        Args:
            doc_path: Path to document file or directory
            doc_type: Document type (brd, prd, etc.)

        Returns:
            tuple: (full_content, section_dict, section_tokens)
                - full_content: Concatenated document text
                - section_dict: {section_id: section_content}
                - section_tokens: {section_id: token_estimate}

        Raises:
            DocumentNotFoundError: If path doesn't exist
        """
        doc_path = Path(doc_path)

        if not doc_path.exists():
            raise DocumentNotFoundError(doc_path)

        if doc_path.is_file():
            return self._load_single_file(doc_path)
        elif doc_path.is_dir():
            return self._load_directory(doc_path, doc_type)
        else:
            raise DocumentNotFoundError(doc_path)

    def _load_directory(
        self, doc_path: Path, doc_type: str
    ) -> tuple[str, dict[str, str], dict[str, int]]:
        """Load multi-file document directory.

        Args:
            doc_path: Path to document directory
            doc_type: Document type

        Returns:
            tuple: (full_content, sections, section_tokens)
        """
        sections = {}
        section_tokens = {}
        content_parts = []

        # Find and sort markdown files
        md_files = self._get_sorted_section_files(doc_path, doc_type)

        for md_file in md_files:
            # Skip if matches skip patterns
            if self._should_skip(md_file.name):
                continue

            # Extract section ID
            section_id = self._extract_section_id(md_file, doc_type)

            # Read content
            try:
                content = md_file.read_text(encoding="utf-8")
            except (IOError, UnicodeDecodeError, OSError) as e:
                # Log warning but continue with other files
                import logging
                logging.getLogger(__name__).warning(
                    f"Failed to read {md_file}: {e}"
                )
                continue

            sections[section_id] = content
            section_tokens[section_id] = len(content) // 4  # Rough estimate

            # Add to full content
            content_parts.append(f"# Section: {section_id}\n\n")
            content_parts.append(content)
            content_parts.append("\n\n---\n\n")

        full_content = "".join(content_parts)
        return full_content, sections, section_tokens

    def _load_single_file(
        self, doc_path: Path
    ) -> tuple[str, dict[str, str], dict[str, int]]:
        """Load single-file document and parse sections via headers.

        Args:
            doc_path: Path to document file

        Returns:
            tuple: (full_content, sections, section_tokens)
        """
        try:
            content = doc_path.read_text(encoding="utf-8")
        except Exception as e:
            raise DocumentNotFoundError(doc_path) from e

        sections = self._parse_sections_from_headers(content, doc_path)
        section_tokens = {
            section_id: len(section_content) // 4
            for section_id, section_content in sections.items()
        }

        return content, sections, section_tokens

    def _get_sorted_section_files(self, doc_path: Path, doc_type: str) -> list[Path]:
        """Get section files sorted by section number.

        Args:
            doc_path: Document directory
            doc_type: Document type

        Returns:
            List of paths sorted by section number
        """
        # Match files like BRD-01.0_index.md, BRD-01.10_risk.md
        pattern = f"{doc_type.upper()}-*.md"
        files = list(doc_path.glob(pattern))

        # Also try lowercase
        if not files:
            pattern = f"{doc_type.lower()}-*.md"
            files = list(doc_path.glob(pattern))

        # Sort by section number (handle 0, 1, 2, ... 10, 11 correctly)
        def sort_key(path: Path) -> tuple[int, int, str]:
            match = self.SECTION_FILE_PATTERN.match(path.name)
            if match:
                section_num = match.group(2)
                # Handle subsections like "6.1"
                parts = section_num.split(".")
                main = int(parts[0])
                sub = int(parts[1]) if len(parts) > 1 else 0
                return (main, sub, path.name)
            return (999, 0, path.name)

        return sorted(files, key=sort_key)

    def _extract_section_id(self, file_path: Path, doc_type: str) -> str:
        """Extract section ID from filename.

        Args:
            file_path: Path to section file
            doc_type: Document type

        Returns:
            Section ID (e.g., "BRD-01.6")
        """
        match = self.SECTION_FILE_PATTERN.match(file_path.name)
        if match:
            doc_id = match.group(1).upper()
            section_num = match.group(2)
            return f"{doc_id}.{section_num}"

        # Fallback: use filename without extension
        return file_path.stem

    def _should_skip(self, filename: str) -> bool:
        """Check if file should be skipped.

        Args:
            filename: Name of file

        Returns:
            True if file should be skipped
        """
        for pattern in self._skip_patterns:
            if pattern.search(filename):
                return True
        return False

    def _parse_sections_from_headers(
        self, content: str, doc_path: Path
    ) -> dict[str, str]:
        """Parse sections from markdown headers in single-file document.

        Args:
            content: Document content
            doc_path: Path to document (for generating section IDs)

        Returns:
            Dict of {section_id: section_content}
        """
        sections = {}
        current_section = None
        current_content = []

        # Extract doc ID from filename
        doc_id = doc_path.stem.upper()

        lines = content.split("\n")
        section_num = 0

        for line in lines:
            # Check for section header (## or # followed by number or text)
            if line.startswith("## ") or line.startswith("# "):
                # Save previous section
                if current_section:
                    sections[current_section] = "\n".join(current_content)

                # Start new section
                section_num += 1
                section_title = line.lstrip("#").strip()

                # Try to extract section number from title
                num_match = re.match(r"^(\d+(?:\.\d+)?)\s*[.\-:]\s*", section_title)
                if num_match:
                    current_section = f"{doc_id}.{num_match.group(1)}"
                else:
                    current_section = f"{doc_id}.{section_num}"

                current_content = [line]
            else:
                current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = "\n".join(current_content)

        return sections

    def get_section_list(self, doc_path: Path, doc_type: str) -> list[str]:
        """Get list of section IDs without loading full content.

        Args:
            doc_path: Path to document
            doc_type: Document type

        Returns:
            List of section IDs
        """
        doc_path = Path(doc_path)

        if not doc_path.exists():
            raise DocumentNotFoundError(doc_path)

        if doc_path.is_dir():
            files = self._get_sorted_section_files(doc_path, doc_type)
            return [
                self._extract_section_id(f, doc_type)
                for f in files
                if not self._should_skip(f.name)
            ]
        else:
            content = doc_path.read_text(encoding="utf-8")
            sections = self._parse_sections_from_headers(content, doc_path)
            return list(sections.keys())

    def get_section_info(
        self, doc_path: Path, doc_type: str
    ) -> list[dict[str, Any]]:
        """Get section information without loading full content.

        Args:
            doc_path: Path to document
            doc_type: Document type

        Returns:
            List of section info dicts with id, title, char_count, token_estimate
        """
        _, sections, tokens = self.load(doc_path, doc_type)

        info = []
        for section_id, content in sections.items():
            # Extract title from first line
            lines = content.strip().split("\n")
            title = lines[0].lstrip("#").strip() if lines else section_id

            info.append(
                {
                    "id": section_id,
                    "title": title[:50],  # Truncate long titles
                    "char_count": len(content),
                    "token_estimate": tokens.get(section_id, len(content) // 4),
                }
            )

        return info

    def load_preprocessed(
        self, doc_path: Path, doc_type: str,
        strip_frontmatter: bool = True,
        strip_comments: bool = True,
        strip_navigation: bool = True,
        strip_metadata: bool = True
    ) -> tuple[str, dict[str, str], dict[str, int]]:
        """Load document with content preprocessing applied.

        Args:
            doc_path: Path to document file or directory
            doc_type: Document type (brd, prd, etc.)
            strip_frontmatter: Remove YAML frontmatter blocks
            strip_comments: Remove HTML comments
            strip_navigation: Remove navigation breadcrumbs
            strip_metadata: Remove document metadata (revision history, etc.)

        Returns:
            tuple: (full_content, section_dict, section_tokens)
                - full_content: Concatenated preprocessed text
                - section_dict: {section_id: preprocessed_content}
                - section_tokens: {section_id: token_estimate}
        """
        full_content, sections, section_tokens = self.load(doc_path, doc_type)

        # Apply preprocessing to each section
        preprocessed_sections = {}
        preprocessed_tokens = {}

        for section_id, content in sections.items():
            cleaned = preprocess_content(
                content,
                strip_frontmatter=strip_frontmatter,
                strip_comments=strip_comments,
                strip_navigation=strip_navigation,
                strip_metadata=strip_metadata
            )
            preprocessed_sections[section_id] = cleaned
            preprocessed_tokens[section_id] = len(cleaned) // 4

        # Rebuild full content from preprocessed sections
        content_parts = []
        for section_id in sorted(preprocessed_sections.keys(), key=self._section_sort_key):
            content_parts.append(f"# Section: {section_id}\n\n")
            content_parts.append(preprocessed_sections[section_id])
            content_parts.append("\n\n---\n\n")

        preprocessed_full = "".join(content_parts)

        return preprocessed_full, preprocessed_sections, preprocessed_tokens

    @staticmethod
    def _section_sort_key(section_id: str) -> tuple[int, int]:
        """Sort key for section IDs by numeric order.

        Args:
            section_id: Section ID like "BRD-01.6" or "BRD-01.10"

        Returns:
            Tuple for sorting (main_num, sub_num)
        """
        match = re.search(r'\.(\d+)(?:\.(\d+))?$', section_id)
        if match:
            main = int(match.group(1))
            sub = int(match.group(2)) if match.group(2) else 0
            return (main, sub)
        return (999, 0)
