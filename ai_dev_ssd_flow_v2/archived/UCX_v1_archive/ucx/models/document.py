"""Document model."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from datetime import datetime
import re
import yaml

from ucx.models.enums import DocType


@dataclass
class Document:
    """Represents a UCX document."""

    path: Path
    doc_type: DocType
    doc_id: str
    version: str = "1.0"
    title: str = ""
    status: str = "draft"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    _content: Optional[str] = field(default=None, repr=False)

    @classmethod
    def from_path(cls, path: Path) -> "Document":
        """
        Load document from file path.

        Args:
            path: Path to document file or directory

        Returns:
            Document instance with parsed metadata
        """
        if path.is_dir():
            # Find main document file in directory
            candidates = list(path.glob("*.md"))
            candidates = [c for c in candidates if "REVIEW" not in c.name and "REPORT" not in c.name]
            if not candidates:
                raise FileNotFoundError(f"No document files found in {path}")
            path = sorted(candidates)[0]

        content = path.read_text(encoding="utf-8")

        # Parse YAML frontmatter
        frontmatter = {}
        if content.startswith("---"):
            match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            if match:
                try:
                    frontmatter = yaml.safe_load(match.group(1)) or {}
                except yaml.YAMLError:
                    pass

        # Extract doc_id from frontmatter or filename
        doc_id = frontmatter.get("doc_id", "")
        if not doc_id:
            doc_id_match = re.search(r"(BRD|PRD|EARS|BDD|ADR|SYS|REQ|CTR|SPEC|TSPEC)-\d+", path.stem)
            doc_id = doc_id_match.group(0) if doc_id_match else path.stem

        # Determine doc_type from doc_id or path
        doc_type_str = doc_id.split("-")[0].lower() if "-" in doc_id else "brd"
        try:
            doc_type = DocType.from_string(doc_type_str)
        except ValueError:
            doc_type = DocType.BRD

        return cls(
            path=path,
            doc_type=doc_type,
            doc_id=doc_id,
            version=str(frontmatter.get("version", "1.0")),
            title=frontmatter.get("title", ""),
            status=frontmatter.get("status", "draft"),
            metadata=frontmatter.get("custom_fields", {}),
            _content=content,
        )

    def read_content(self) -> str:
        """Read document content."""
        if self._content is not None:
            return self._content
        self._content = self.path.read_text(encoding="utf-8")
        return self._content

    def write_content(self, content: str) -> None:
        """Write document content."""
        self._content = content
        self.updated_at = datetime.now()
        self.path.write_text(content, encoding="utf-8")

    @property
    def exists(self) -> bool:
        """Check if document file exists."""
        return self.path.exists()

    @property
    def directory(self) -> Path:
        """Get document directory."""
        return self.path.parent if self.path.is_file() else self.path

    def get_companion_path(self, suffix: str) -> Path:
        """Get path for companion file (e.g., review report)."""
        return self.directory / f"{self.doc_id}_{suffix}"
