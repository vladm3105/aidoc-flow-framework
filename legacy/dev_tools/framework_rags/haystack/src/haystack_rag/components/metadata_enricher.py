"""Metadata enricher component for Haystack."""

import re
from pathlib import Path
from typing import Any

import yaml
from haystack import Document, component


@component
class MetadataEnricher:
    """Extract and enrich document metadata from content and file paths.

    Extracts metadata from:
    - YAML frontmatter
    - File path patterns (e.g., PRD-001_auth_service.md)
    - Content patterns
    """

    def __init__(self, extract_fields: list[str] | None = None):
        """Initialize metadata enricher.

        Args:
            extract_fields: List of fields to extract.
        """
        self.extract_fields = extract_fields or [
            "doc_type",
            "project_name",
            "version",
            "date",
            "author",
            "layer",
            "status",
        ]

        # Mapping of document type prefixes to SDD layers
        # Layer 0 = Reference documents (initial project docs, business requirements)
        self.layer_mapping = {
            "REF": 0,
            "BRD": 1,
            "PRD": 2,
            "EARS": 3,
            "BDD": 4,
            "ADR": 5,
            "SYS": 6,
            "REQ": 7,
            "CTR": 8,
            "SPEC": 9,
            "TSPEC": 10,
            "TASKS": 11,
            "IPLAN": 12,
        }

    @component.output_types(documents=list[Document])
    def run(self, documents: list[Document]) -> dict[str, list[Document]]:
        """Enrich documents with metadata.

        Args:
            documents: Input documents to enrich.

        Returns:
            Dictionary with enriched documents.
        """
        enriched = []
        for doc in documents:
            meta = dict(doc.meta) if doc.meta else {}

            # Extract from frontmatter
            frontmatter_meta = self._extract_frontmatter(doc.content)
            meta.update(frontmatter_meta)

            # Extract from file path
            if "file_path" in meta:
                path_meta = self._extract_from_path(meta["file_path"])
                # Don't override frontmatter values
                for key, value in path_meta.items():
                    if key not in meta or meta[key] is None:
                        meta[key] = value

            # Infer layer from doc_type
            if "doc_type" in meta and "layer" not in meta:
                doc_type = meta["doc_type"].upper()
                if doc_type in self.layer_mapping:
                    meta["layer"] = self.layer_mapping[doc_type]

            enriched.append(Document(content=doc.content, meta=meta))

        return {"documents": enriched}

    def _extract_frontmatter(self, content: str) -> dict[str, Any]:
        """Extract metadata from YAML frontmatter.

        Args:
            content: Document content.

        Returns:
            Extracted metadata dictionary.
        """
        meta = {}

        # Match YAML frontmatter
        frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if frontmatter_match:
            try:
                frontmatter = yaml.safe_load(frontmatter_match.group(1))
                if isinstance(frontmatter, dict):
                    # Extract relevant fields
                    for field in self.extract_fields:
                        if field in frontmatter:
                            meta[field] = frontmatter[field]

                    # Also check custom_fields
                    custom_fields = frontmatter.get("custom_fields", {})
                    if isinstance(custom_fields, dict):
                        for field in self.extract_fields:
                            if field in custom_fields and field not in meta:
                                meta[field] = custom_fields[field]
            except yaml.YAMLError:
                pass

        return meta

    def _extract_from_path(self, file_path: str) -> dict[str, Any]:
        """Extract metadata from file path.

        Handles patterns like:
        - PRD-001_auth_service.md → doc_type=PRD
        - 02_PRD/PRD-001.md → layer=2, doc_type=PRD
        - projects/beelocal/docs/SPEC-001.md → project_name=beelocal

        Args:
            file_path: Path to the document.

        Returns:
            Extracted metadata dictionary.
        """
        meta = {}
        path = Path(file_path)

        # Extract doc_type from filename
        filename = path.stem
        doc_type_match = re.match(r"^([A-Z]+)-?\d*", filename)
        if doc_type_match:
            meta["doc_type"] = doc_type_match.group(1)

        # Extract layer from directory name (e.g., 02_PRD)
        for part in path.parts:
            layer_match = re.match(r"^(\d+)_([A-Z]+)", part)
            if layer_match:
                meta["layer"] = int(layer_match.group(1))
                if "doc_type" not in meta:
                    meta["doc_type"] = layer_match.group(2)
                break

        # Try to extract project name from path
        parts = path.parts
        for i, part in enumerate(parts):
            if part in ("docs", "ucx_flow_v3", "ucx_flow_v3", "documentation") and i > 0:
                meta["project_name"] = parts[i - 1]
                break

        return meta
