"""Custom document cleaner component for Haystack."""

import re
from typing import Any

from haystack import Document, component


@component
class CustomDocumentCleaner:
    """Clean and normalize documents for better indexing.

    Performs:
    - Whitespace normalization
    - Empty line removal
    - Page number removal
    - Unicode normalization
    - Optional header/footer removal
    """

    def __init__(
        self,
        remove_empty_lines: bool = True,
        remove_extra_whitespace: bool = True,
        remove_page_numbers: bool = True,
        normalize_unicode: bool = True,
        remove_headers_footers: bool = False,
        min_line_length: int = 3,
    ):
        """Initialize document cleaner.

        Args:
            remove_empty_lines: Remove blank lines.
            remove_extra_whitespace: Collapse multiple spaces.
            remove_page_numbers: Remove page number patterns.
            normalize_unicode: Normalize unicode characters.
            remove_headers_footers: Remove repeated headers/footers.
            min_line_length: Minimum line length to keep.
        """
        self.remove_empty_lines = remove_empty_lines
        self.remove_extra_whitespace = remove_extra_whitespace
        self.remove_page_numbers = remove_page_numbers
        self.normalize_unicode = normalize_unicode
        self.remove_headers_footers = remove_headers_footers
        self.min_line_length = min_line_length

    @component.output_types(documents=list[Document])
    def run(self, documents: list[Document]) -> dict[str, list[Document]]:
        """Clean documents.

        Args:
            documents: Input documents to clean.

        Returns:
            Dictionary with cleaned documents.
        """
        cleaned = []
        for doc in documents:
            content = self._clean_content(doc.content)
            cleaned.append(Document(content=content, meta=doc.meta))
        return {"documents": cleaned}

    def _clean_content(self, content: str) -> str:
        """Clean document content.

        Args:
            content: Raw document content.

        Returns:
            Cleaned content.
        """
        if not content:
            return content

        # Normalize unicode
        if self.normalize_unicode:
            import unicodedata
            content = unicodedata.normalize("NFKC", content)

        # Remove page numbers (various formats)
        if self.remove_page_numbers:
            # Page N, Page N of M, - N -, etc.
            content = re.sub(r"(?i)page\s+\d+(\s+of\s+\d+)?", "", content)
            content = re.sub(r"^\s*-\s*\d+\s*-\s*$", "", content, flags=re.MULTILINE)
            content = re.sub(r"^\s*\d+\s*$", "", content, flags=re.MULTILINE)

        # Process line by line
        lines = content.split("\n")
        processed_lines = []

        for line in lines:
            # Remove extra whitespace within line
            if self.remove_extra_whitespace:
                line = re.sub(r"[ \t]+", " ", line)
                line = line.strip()

            # Skip empty lines
            if self.remove_empty_lines and not line:
                continue

            # Skip very short lines (likely noise)
            if len(line) < self.min_line_length:
                continue

            processed_lines.append(line)

        # Join lines
        content = "\n".join(processed_lines)

        # Remove repeated patterns (headers/footers)
        if self.remove_headers_footers:
            content = self._remove_repeated_patterns(content)

        return content

    def _remove_repeated_patterns(self, content: str) -> str:
        """Remove patterns that appear too frequently (likely headers/footers).

        Args:
            content: Document content.

        Returns:
            Content with repeated patterns removed.
        """
        lines = content.split("\n")

        # Count line occurrences
        line_counts: dict[str, int] = {}
        for line in lines:
            normalized = line.strip().lower()
            if len(normalized) > 10:  # Only consider substantial lines
                line_counts[normalized] = line_counts.get(normalized, 0) + 1

        # Remove lines that appear more than 3 times (likely headers/footers)
        threshold = 3
        filtered_lines = []
        for line in lines:
            normalized = line.strip().lower()
            if line_counts.get(normalized, 0) <= threshold:
                filtered_lines.append(line)

        return "\n".join(filtered_lines)
