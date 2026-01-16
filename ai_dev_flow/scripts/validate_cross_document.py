#!/usr/bin/env python3
"""
Cross-Document Validation System for AI Dev Flow Framework

Validates upstream document content consistency across the 16-layer SDD workflow.
Auto-fixes issues without user confirmation following strict hierarchy rules.

Usage:
    # Per-document validation
    python validate_cross_document.py --document docs/REQ/REQ-01.md --auto-fix

    # Per-layer validation
    python validate_cross_document.py --layer REQ --auto-fix

    # Full validation
    python validate_cross_document.py --all --auto-fix --strict

Validation Rules (XDOC-001 to XDOC-010):
    XDOC-001: Referenced requirement ID not found in upstream
    XDOC-002: Missing cumulative tag for layer
    XDOC-003: Upstream document file not found
    XDOC-004: Title mismatch with upstream
    XDOC-005: Referencing deprecated requirement
    XDOC-006: Tag format invalid
    XDOC-007: Gap in cumulative tag chain
    XDOC-008: Broken internal link/anchor
    XDOC-009: Missing traceability section
    XDOC-010: Orphan requirement (no downstream)

Author: AI Dev Flow Framework
Version: 1.0.0
"""

import argparse
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
import json


class Severity(Enum):
    """Issue severity levels"""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class IssueCode(Enum):
    """Cross-document validation issue codes"""
    XDOC_001 = "XDOC-001"  # Referenced requirement ID not found in upstream
    XDOC_002 = "XDOC-002"  # Missing cumulative tag for layer
    XDOC_003 = "XDOC-003"  # Upstream document file not found
    XDOC_004 = "XDOC-004"  # Title mismatch with upstream
    XDOC_005 = "XDOC-005"  # Referencing deprecated requirement
    XDOC_006 = "XDOC-006"  # Tag format invalid
    XDOC_007 = "XDOC-007"  # Gap in cumulative tag chain
    XDOC_008 = "XDOC-008"  # Broken internal link/anchor
    XDOC_009 = "XDOC-009"  # Missing traceability section
    XDOC_010 = "XDOC-010"  # Orphan requirement (no downstream)


@dataclass
class ValidationIssue:
    """Represents a validation issue found during cross-document validation"""
    code: IssueCode
    severity: Severity
    message: str
    location: str
    fix_action: Optional[str] = None
    fixed: bool = False

    def __repr__(self):
        status = "[FIXED]" if self.fixed else ""
        return f"[{self.code.value}] {self.severity.value}: {self.message} @ {self.location} {status}"


# Layer configuration: defines cumulative tagging requirements
LAYER_CONFIG = {
    "BRD": {"layer": 1, "required_tags": [], "extensions": [".md"]},
    "PRD": {"layer": 2, "required_tags": ["brd"], "extensions": [".md"]},
    "EARS": {"layer": 3, "required_tags": ["brd", "prd"], "extensions": [".md"]},
    "BDD": {"layer": 4, "required_tags": ["brd", "prd", "ears"], "extensions": [".md", ".feature"]},
    "ADR": {"layer": 5, "required_tags": ["brd", "prd", "ears", "bdd"], "extensions": [".md"]},
    "SYS": {"layer": 6, "required_tags": ["brd", "prd", "ears", "bdd", "adr"], "extensions": [".md"]},
    "REQ": {"layer": 7, "required_tags": ["brd", "prd", "ears", "bdd", "adr", "sys"], "extensions": [".md"]},
    "IMPL": {"layer": 8, "required_tags": ["brd", "prd", "ears", "bdd", "adr", "sys", "req"], "extensions": [".md"]},
    "CTR": {"layer": 9, "required_tags": ["brd", "prd", "ears", "bdd", "adr", "sys", "req", "impl"], "extensions": [".md", ".yaml"]},
    "SPEC": {"layer": 10, "required_tags": ["brd", "prd", "ears", "bdd", "adr", "sys", "req"], "extensions": [".yaml"]},
    "TASKS": {"layer": 11, "required_tags": ["brd", "prd", "ears", "bdd", "adr", "sys", "req", "spec"], "extensions": [".md"]},
}

# Tag format patterns
TAG_PATTERN = re.compile(r'^@(\w+):\s*(.+)$', re.MULTILINE)

# Document-level IDs (TYPE-NN format for filenames)
# Examples: ADR-001, SPEC-01, BRD-03.1 (section files)
DOC_FILE_PATTERN = re.compile(r'^([A-Z]{2,5})-(\d{2,})(?:\.(\d+))?$')

# Element-level IDs (TYPE.NN.TT.SS format for content)
# Format: {DOC_TYPE}.{DOC_NUM}.{ELEM_TYPE}.{SEQ}
# Examples: BRD.01.01.03, PRD.17.07.15, REQ.01.01.01
# NOTE: Old formats (TYPE-NN-YY, TYPE-NN.YY) are DEPRECATED
ELEMENT_ID_PATTERN = re.compile(r'^([A-Z]{2,5})\.(\d{2,9})\.(\d{2,9})\.(\d{2,9})$')

# Combined pattern for backward compatibility during transition
# Accepts both document-level and element-level formats
DOC_ID_PATTERN = re.compile(r'([A-Z]{2,5})(?:-(\d{2,})(?:\.(\d+))?|\.(\d{2,9})\.(\d{2,9})\.(\d{2,9}))')
TRACEABILITY_SECTION_PATTERN = re.compile(r'^##\s+(?:\d+\.\s+)?Traceability', re.MULTILINE | re.IGNORECASE)


class RequirementIndex:
    """Index of all requirements across all document types"""

    def __init__(self, docs_root: Path):
        """
        Initialize the requirement index

        Args:
            docs_root: Root directory containing docs/
        """
        self.docs_root = docs_root
        self.requirements: Dict[str, Dict] = {}  # doc_id -> {path, title, type, sections, deprecated}
        self.sections: Dict[str, Set[str]] = defaultdict(set)  # doc_id -> set of section IDs
        self.deprecated_ids: Set[str] = set()

    def build_index(self) -> None:
        """Scan all documents and build requirement index"""
        docs_dir = self.docs_root / "docs"

        if not docs_dir.exists():
            print(f"Warning: docs directory not found at {docs_dir}")
            return

        for doc_type, config in LAYER_CONFIG.items():
            type_dir = docs_dir / doc_type
            if not type_dir.exists():
                continue

            for ext in config["extensions"]:
                # Recursive glob to support subdirectory-based organization (e.g., BRD-01/, PRD-07/)
                for doc_path in type_dir.glob(f"**/*{ext}"):
                    self._index_document(doc_path, doc_type)

    def _index_document(self, doc_path: Path, doc_type: str) -> None:
        """Index a single document"""
        try:
            content = doc_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Warning: Could not read {doc_path}: {e}")
            return

        # Extract document ID from filename
        doc_id_match = DOC_ID_PATTERN.search(doc_path.stem)
        if not doc_id_match:
            return

        doc_id = f"{doc_id_match.group(1)}-{doc_id_match.group(2)}"
        if doc_id_match.group(3):
            doc_id += f".{doc_id_match.group(3)}"  # Section file format: TYPE-NN.S

        # Extract title (first # heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else ""

        # Extract section IDs (numbered sections or anchors)
        section_ids = set()
        for match in re.finditer(r'^###?\s+(\d+(?:\.\d+)*)', content, re.MULTILINE):
            section_ids.add(match.group(1))
        for match in re.finditer(r'\{#([a-z0-9-]+)\}', content):
            section_ids.add(match.group(1))

        # Check for deprecated status
        is_deprecated = bool(re.search(r'status:\s*deprecated', content, re.IGNORECASE))

        self.requirements[doc_id] = {
            "path": doc_path,
            "title": title,
            "type": doc_type,
            "sections": section_ids,
            "deprecated": is_deprecated
        }
        self.sections[doc_id] = section_ids

        if is_deprecated:
            self.deprecated_ids.add(doc_id)

    def exists(self, doc_id: str) -> bool:
        """Check if a document ID exists in the index

        Supports both exact matches and parent document lookups for section-based documents.
        Examples:
        - BRD-01 → matches BRD-01, BRD-01.0, BRD-01.1, etc.
        - BRD-01.0 → exact match only
        """
        # Try exact match first
        if doc_id in self.requirements:
            return True
        # Try base ID (without section reference)
        base_id = doc_id.split(':')[0]
        if base_id in self.requirements:
            return True

        # For parent document IDs (TYPE-NN), check if any section files exist (TYPE-NN.*)
        # This handles section-based document organization where BRD-01/ contains BRD-01.0, BRD-01.1, etc.
        if '.' not in base_id:  # Only for parent IDs like BRD-01, not section IDs like BRD-01.0
            for indexed_id in self.requirements.keys():
                # Check if indexed_id starts with base_id and has section number (TYPE-NN.S pattern)
                if indexed_id.startswith(f"{base_id}.") and indexed_id.replace(f"{base_id}.", "").isdigit():
                    return True

        return False

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Get document metadata by ID

        Supports both exact matches and parent document lookups for section-based documents.
        For parent IDs (TYPE-NN), returns the first section file (TYPE-NN.0) if found.
        """
        base_id = doc_id.split(':')[0]

        # Try exact match first
        if base_id in self.requirements:
            return self.requirements.get(base_id)

        # For parent document IDs (TYPE-NN), return first section file (TYPE-NN.0)
        if '.' not in base_id:
            # Look for index file (TYPE-NN.0) first
            index_id = f"{base_id}.0"
            if index_id in self.requirements:
                return self.requirements[index_id]

            # Fallback: return any section file
            for indexed_id in sorted(self.requirements.keys()):
                if indexed_id.startswith(f"{base_id}.") and indexed_id.replace(f"{base_id}.", "").isdigit():
                    return self.requirements[indexed_id]

        return None

    def is_deprecated(self, doc_id: str) -> bool:
        """Check if a document is deprecated"""
        base_id = doc_id.split(':')[0]
        return base_id in self.deprecated_ids

    def section_exists(self, doc_id: str, section_id: str) -> bool:
        """Check if a section exists within a document

        Supports both exact matches and parent document lookups for section-based documents.
        For parent IDs (TYPE-NN), searches all section files (TYPE-NN.*) for the section.
        """
        base_id = doc_id.split(':')[0]

        # Try exact match first
        if base_id in self.sections:
            return section_id in self.sections[base_id]

        # For parent document IDs (TYPE-NN), search all section files
        if '.' not in base_id:
            for indexed_id in self.sections.keys():
                if indexed_id.startswith(f"{base_id}.") and indexed_id.replace(f"{base_id}.", "").isdigit():
                    if section_id in self.sections[indexed_id]:
                        return True

        return False

    def get_documents_by_type(self, doc_type: str) -> List[str]:
        """Get all document IDs of a specific type"""
        return [doc_id for doc_id, meta in self.requirements.items()
                if meta["type"] == doc_type]


class CrossDocumentValidator:
    """Main validator for upstream content consistency"""

    def __init__(self, docs_root: Path, index: RequirementIndex):
        """
        Initialize the validator

        Args:
            docs_root: Root directory containing docs/
            index: Pre-built requirement index
        """
        self.docs_root = docs_root
        self.index = index
        self.issues: List[ValidationIssue] = []

    def validate_document(self, doc_path: Path) -> List[ValidationIssue]:
        """
        Validate a single document for cross-document consistency

        Args:
            doc_path: Path to document to validate

        Returns:
            List of validation issues found
        """
        self.issues = []

        if not doc_path.exists():
            self.issues.append(ValidationIssue(
                code=IssueCode.XDOC_003,
                severity=Severity.ERROR,
                message=f"Document file not found: {doc_path}",
                location=str(doc_path)
            ))
            return self.issues

        try:
            content = doc_path.read_text(encoding='utf-8')
        except Exception as e:
            self.issues.append(ValidationIssue(
                code=IssueCode.XDOC_003,
                severity=Severity.ERROR,
                message=f"Cannot read document: {e}",
                location=str(doc_path)
            ))
            return self.issues

        # Determine document type
        doc_type = self._get_doc_type(doc_path)
        if not doc_type:
            return self.issues

        # Run all validation checks
        self._validate_traceability_section(content, doc_path)
        self._validate_cumulative_tags(content, doc_path, doc_type)
        self._validate_tag_format(content, doc_path)
        self._validate_upstream_references(content, doc_path)
        self._validate_internal_links(content, doc_path)

        return self.issues

    def validate_layer(self, layer_type: str) -> List[ValidationIssue]:
        """
        Validate all documents of a specific layer

        Args:
            layer_type: Document type (BRD, PRD, etc.)

        Returns:
            List of validation issues found across the layer
        """
        self.issues = []

        docs_dir = self.docs_root / "docs" / layer_type
        if not docs_dir.exists():
            return self.issues

        config = LAYER_CONFIG.get(layer_type, {})
        extensions = config.get("extensions", [".md"])

        for ext in extensions:
            for doc_path in docs_dir.glob(f"*{ext}"):
                self.issues.extend(self.validate_document(doc_path))

        # Check for orphan requirements (no downstream references)
        self._validate_orphans(layer_type)

        return self.issues

    def validate_all(self) -> List[ValidationIssue]:
        """
        Validate all documents across all layers

        Returns:
            List of all validation issues found
        """
        self.issues = []

        for layer_type in LAYER_CONFIG.keys():
            self.issues.extend(self.validate_layer(layer_type))

        return self.issues

    def _get_doc_type(self, doc_path: Path) -> Optional[str]:
        """Determine document type from path"""
        for doc_type in LAYER_CONFIG.keys():
            if f"/{doc_type}/" in str(doc_path) or f"\\{doc_type}\\" in str(doc_path):
                return doc_type
            if doc_path.name.upper().startswith(doc_type):
                return doc_type
        return None

    def _validate_traceability_section(self, content: str, doc_path: Path) -> None:
        """Check for required traceability section"""
        if not TRACEABILITY_SECTION_PATTERN.search(content):
            self.issues.append(ValidationIssue(
                code=IssueCode.XDOC_009,
                severity=Severity.ERROR,
                message="Missing traceability section (required ## Traceability heading)",
                location=str(doc_path),
                fix_action="Add template traceability section"
            ))

    def _validate_cumulative_tags(self, content: str, doc_path: Path, doc_type: str) -> None:
        """Validate cumulative tag chain is complete"""
        config = LAYER_CONFIG.get(doc_type, {})
        required_tags = config.get("required_tags", [])

        # Extract existing tags
        existing_tags = set()
        for match in TAG_PATTERN.finditer(content):
            tag_name = match.group(1).lower()
            existing_tags.add(tag_name)

        # Check for missing required tags
        for required_tag in required_tags:
            if required_tag not in existing_tags:
                self.issues.append(ValidationIssue(
                    code=IssueCode.XDOC_002,
                    severity=Severity.ERROR,
                    message=f"Missing required cumulative tag: @{required_tag}",
                    location=str(doc_path),
                    fix_action=f"Add @{required_tag} tag with valid upstream reference"
                ))

        # Check for gaps in cumulative chain
        tag_order = ["brd", "prd", "ears", "bdd", "adr", "sys", "req", "impl", "ctr", "spec", "tasks"]
        found_tags = [t for t in tag_order if t in existing_tags]

        if found_tags:
            expected_chain = tag_order[:tag_order.index(found_tags[-1]) + 1]
            expected_required = [t for t in expected_chain if t in required_tags]

            for i, tag in enumerate(expected_required[:-1]):
                if tag not in existing_tags:
                    self.issues.append(ValidationIssue(
                        code=IssueCode.XDOC_007,
                        severity=Severity.ERROR,
                        message=f"Gap in cumulative tag chain: missing @{tag}",
                        location=str(doc_path),
                        fix_action=f"Add @{tag} tag to complete chain"
                    ))

    def _validate_tag_format(self, content: str, doc_path: Path) -> None:
        """Validate tag format is correct"""
        for match in TAG_PATTERN.finditer(content):
            tag_name = match.group(1).lower()
            tag_value = match.group(2).strip()

            # Skip null values
            if tag_value.lower() == "null":
                continue

            # Check format: TYPE-NN (doc-level) or TYPE.NN.TT.SS (sub-ID)
            if not DOC_ID_PATTERN.match(tag_value):
                self.issues.append(ValidationIssue(
                    code=IssueCode.XDOC_006,
                    severity=Severity.ERROR,
                    message=f"Invalid tag format: @{tag_name}: {tag_value} (expected TYPE-NN or TYPE.NN.TT.SS)",
                    location=str(doc_path),
                    fix_action="Correct to TYPE-NN (doc-level) or TYPE.NN.TT.SS (sub-ID) format"
                ))

    def _validate_upstream_references(self, content: str, doc_path: Path) -> None:
        """Validate all upstream references exist"""
        for match in TAG_PATTERN.finditer(content):
            tag_name = match.group(1).lower()
            tag_value = match.group(2).strip()

            # Skip null values
            if tag_value.lower() == "null":
                continue

            # Extract document ID - handle both formats:
            # TYPE-NN (doc-level): groups (1=TYPE, 2=NNN, 3=optional-sub)
            # TYPE.NN.TT.SS (sub-ID): groups (1=TYPE, 4=doc-NNN, 5=sub-NNN)
            doc_id_match = DOC_ID_PATTERN.match(tag_value)
            if not doc_id_match:
                continue

            doc_type = doc_id_match.group(1)
            if doc_id_match.group(2):  # Hyphen format: TYPE-NN or TYPE-NN.S (section file)
                doc_id = f"{doc_type}-{doc_id_match.group(2)}"
                if doc_id_match.group(3):
                    doc_id += f".{doc_id_match.group(3)}"  # Section file format: TYPE-NN.S
                section_ref = None
            else:  # Dot notation format: TYPE.NN.TT.SS (element ID)
                doc_num = doc_id_match.group(4)
                doc_id = f"{doc_type}-{doc_num}"  # Convert to hyphen for index lookup
                # Element IDs reference specific requirements, not document sections
                # We only validate the parent document exists, not element-level granularity
                section_ref = None

            # Check document exists
            if not self.index.exists(doc_id):
                self.issues.append(ValidationIssue(
                    code=IssueCode.XDOC_003,
                    severity=Severity.ERROR,
                    message=f"Referenced upstream document not found: {doc_id}",
                    location=str(doc_path),
                    fix_action=f"Remove @{tag_name} tag and dependent content (strict hierarchy)"
                ))
                continue

            # Check for deprecated references
            if self.index.is_deprecated(doc_id):
                self.issues.append(ValidationIssue(
                    code=IssueCode.XDOC_005,
                    severity=Severity.WARNING,
                    message=f"Referencing deprecated document: {doc_id}",
                    location=str(doc_path),
                    fix_action="Remove or replace with active document reference"
                ))

            # Check section reference exists if specified
            if section_ref and not self.index.section_exists(doc_id, section_ref):
                upstream_doc = self.index.get_document(doc_id)
                if upstream_doc:
                    self.issues.append(ValidationIssue(
                        code=IssueCode.XDOC_001,
                        severity=Severity.ERROR,
                        message=f"Referenced section not found: {doc_id}:{section_ref}",
                        location=str(doc_path),
                        fix_action=f"Remove section reference or fix to valid section"
                    ))

    def _validate_section_title_accuracy(self, content: str, doc_path: Path) -> None:
        """Validate section cross-reference titles match actual target headings.

        Checks XREF-E001/E002 for section number/title mismatches.
        """
        # Pattern for section references: [Section N: Title](path#anchor) or [N. Title](path)
        section_ref_pattern = re.compile(
            r'\[(?:Section\s+)?(\d+(?:\.\d+)*)(?:[\.:]\s*)?([^\]]*)\]\(([^)]+)\)'
        )

        for match in section_ref_pattern.finditer(content):
            ref_section_num = match.group(1)
            ref_title = match.group(2).strip()
            link_path = match.group(3)

            # Skip external URLs and anchor-only links
            if link_path.startswith(('http://', 'https://', 'mailto:', '#')):
                continue

            # Extract anchor if present
            anchor = None
            if '#' in link_path:
                link_path, anchor = link_path.split('#', 1)

            # Resolve relative path
            if link_path.startswith('./') or link_path.startswith('../'):
                resolved_path = (doc_path.parent / link_path).resolve()
            elif link_path:
                resolved_path = (self.docs_root / link_path).resolve()
            else:
                # Anchor-only reference to current document
                resolved_path = doc_path

            if not resolved_path.exists():
                continue  # Handled by _validate_internal_links

            try:
                target_content = resolved_path.read_text(encoding='utf-8')
            except Exception:
                continue

            # Find the referenced section heading
            # Pattern: ## N. Title or ## N Title or ### N.N. Title
            heading_pattern = re.compile(
                rf'^(#{2,})\s*{re.escape(ref_section_num)}[\.\s]+(.+)$',
                re.MULTILINE
            )
            heading_match = heading_pattern.search(target_content)

            if not heading_match:
                self.issues.append(ValidationIssue(
                    code=IssueCode.XDOC_001,
                    severity=Severity.ERROR,
                    message=f"Section {ref_section_num} not found in target: {link_path}",
                    location=str(doc_path),
                    fix_action="Verify section number or fix target document"
                ))
                continue

            # Check if title matches
            actual_title = heading_match.group(2).strip()
            if ref_title and actual_title:
                # Fuzzy match: check if titles are similar
                ref_title_norm = ref_title.lower().strip()
                actual_title_norm = actual_title.lower().strip()

                if ref_title_norm != actual_title_norm:
                    # Check for minor differences
                    if ref_title_norm in actual_title_norm or actual_title_norm in ref_title_norm:
                        self.issues.append(ValidationIssue(
                            code=IssueCode.XDOC_004,  # Reusing title mismatch code
                            severity=Severity.WARNING,
                            message=f"Section title fuzzy match: '{ref_title}' vs '{actual_title}'",
                            location=str(doc_path),
                            fix_action=f"Update link text to: {actual_title}"
                        ))
                    else:
                        self.issues.append(ValidationIssue(
                            code=IssueCode.XDOC_004,
                            severity=Severity.ERROR,
                            message=f"Section title mismatch: '{ref_title}' vs actual '{actual_title}'",
                            location=str(doc_path),
                            fix_action=f"Update link text to match: {actual_title}"
                        ))

    def _validate_internal_links(self, content: str, doc_path: Path) -> None:
        """Validate internal markdown links resolve"""
        # Pattern for markdown links: [text](path)
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

        for match in link_pattern.finditer(content):
            link_text = match.group(1)
            link_path = match.group(2)

            # Skip external URLs
            if link_path.startswith(('http://', 'https://', 'mailto:')):
                continue

            # Skip anchor-only links
            if link_path.startswith('#'):
                continue

            # Resolve relative path
            if link_path.startswith('./') or link_path.startswith('../'):
                resolved_path = (doc_path.parent / link_path).resolve()
            else:
                resolved_path = (self.docs_root / link_path).resolve()

            # Remove anchor if present
            if '#' in str(resolved_path):
                resolved_path = Path(str(resolved_path).split('#')[0])

            if not resolved_path.exists():
                self.issues.append(ValidationIssue(
                    code=IssueCode.XDOC_008,
                    severity=Severity.ERROR,
                    message=f"Broken internal link: {link_path}",
                    location=str(doc_path),
                    fix_action="Fix path or remove link"
                ))

    def _validate_orphans(self, layer_type: str) -> None:
        """Check for orphan requirements (no downstream references)"""
        # Get all documents of this layer
        layer_docs = self.index.get_documents_by_type(layer_type)

        if not layer_docs:
            return

        # Get next layer type
        layer_order = list(LAYER_CONFIG.keys())
        try:
            current_idx = layer_order.index(layer_type)
            if current_idx >= len(layer_order) - 1:
                return  # Last layer, no downstream
        except ValueError:
            return

        # Check which documents are referenced by downstream layers
        referenced = set()
        for next_type in layer_order[current_idx + 1:]:
            next_docs = self.index.get_documents_by_type(next_type)
            for doc_id in next_docs:
                doc_meta = self.index.get_document(doc_id)
                if doc_meta:
                    try:
                        content = doc_meta["path"].read_text(encoding='utf-8')
                        for match in TAG_PATTERN.finditer(content):
                            tag_value = match.group(2).strip()
                            ref_match = DOC_ID_PATTERN.match(tag_value)
                            if ref_match:
                                ref_type = ref_match.group(1)
                                if ref_match.group(2):  # Hyphen format: TYPE-NN or TYPE-NN.S
                                    ref_id = f"{ref_type}-{ref_match.group(2)}"
                                    if ref_match.group(3):
                                        ref_id += f".{ref_match.group(3)}"  # Section file format
                                else:  # Dot notation format: TYPE.NN.TT.SS
                                    ref_id = f"{ref_type}-{ref_match.group(4)}"
                                referenced.add(ref_id)
                    except Exception:
                        pass

        # Report orphans
        for doc_id in layer_docs:
            if doc_id not in referenced:
                doc_meta = self.index.get_document(doc_id)
                self.issues.append(ValidationIssue(
                    code=IssueCode.XDOC_010,
                    severity=Severity.WARNING,
                    message=f"Orphan document: {doc_id} has no downstream references",
                    location=str(doc_meta["path"]) if doc_meta else doc_id,
                    fix_action="Annotate for review or create downstream references"
                ))


class AutoFixer:
    """Automatic fix engine for cross-document validation issues"""

    TRACEABILITY_TEMPLATE = """
## Traceability

### Upstream Sources
| Artifact | Reference | Description |
|----------|-----------|-------------|
| BRD | @brd: null | Business Requirements |
| PRD | @prd: null | Product Requirements |

### Downstream Artifacts
| Artifact | Reference | Description |
|----------|-----------|-------------|

### Document Anchors
- Primary ID: {doc_id}
"""

    def __init__(self, docs_root: Path, index: RequirementIndex, create_backup: bool = True,
                 dry_run: bool = False, force_xdoc: bool = False):
        """
        Initialize the auto-fixer

        Args:
            docs_root: Root directory containing docs/
            index: Pre-built requirement index
            create_backup: Whether to create .bak files before modifications
            dry_run: Preview changes without applying them
            force_xdoc: Skip confirmation for XDOC-003 tag removals
        """
        self.docs_root = docs_root
        self.index = index
        self.create_backup = create_backup
        self.dry_run = dry_run
        self.force_xdoc = force_xdoc
        self.changes_log: List[str] = []
        self.audit_entries: List[Dict] = []

    def fix_issues(self, doc_path: Path, issues: List[ValidationIssue]) -> List[ValidationIssue]:
        """
        Apply automatic fixes to a document

        Args:
            doc_path: Path to document to fix
            issues: List of issues to fix

        Returns:
            Updated list of issues with fixed status
        """
        if not issues or not doc_path.exists():
            return issues

        # Create backup before modifications
        if self.create_backup:
            self._backup_document(doc_path)

        try:
            content = doc_path.read_text(encoding='utf-8')
            original_content = content
        except Exception as e:
            print(f"Error reading {doc_path}: {e}")
            return issues

        modified = False

        for issue in issues:
            if issue.fixed:
                continue

            fix_result = self._apply_fix(content, issue, doc_path)
            if fix_result:
                content = fix_result
                issue.fixed = True
                modified = True
                self.changes_log.append(f"Fixed {issue.code.value} in {doc_path.name}: {issue.message}")

        # Write back if modified
        if modified:
            if self.dry_run:
                print(f"[DRY-RUN] Would modify {doc_path.name}:")
                for issue in issues:
                    if issue.fixed:
                        print(f"  - Would fix {issue.code.value}: {issue.message}")
                # Reset fixed status since we didn't actually modify
                for issue in issues:
                    issue.fixed = False
            else:
                try:
                    doc_path.write_text(content, encoding='utf-8')
                except Exception as e:
                    print(f"Error writing {doc_path}: {e}")
                    # Restore from backup
                    self._restore_backup(doc_path)
                    for issue in issues:
                        issue.fixed = False

        return issues

    def _apply_fix(self, content: str, issue: ValidationIssue, doc_path: Path) -> Optional[str]:
        """Apply a specific fix and return modified content"""

        if issue.code == IssueCode.XDOC_009:
            # Add traceability section
            return self._fix_missing_traceability(content, doc_path)

        elif issue.code == IssueCode.XDOC_002:
            # Add missing cumulative tag
            return self._fix_missing_tag(content, issue, doc_path)

        elif issue.code == IssueCode.XDOC_006:
            # Fix tag format
            return self._fix_tag_format(content, issue)

        elif issue.code == IssueCode.XDOC_003:
            # Remove functionality requiring missing upstream (strict hierarchy)
            return self._fix_missing_upstream(content, issue, doc_path)

        elif issue.code == IssueCode.XDOC_005:
            # Remove deprecated reference
            return self._fix_deprecated_reference(content, issue)

        elif issue.code == IssueCode.XDOC_008:
            # Fix broken link
            return self._fix_broken_link(content, issue)

        return None

    def _fix_missing_traceability(self, content: str, doc_path: Path) -> str:
        """Add missing traceability section"""
        # Extract document ID from filename
        doc_id_match = DOC_ID_PATTERN.search(doc_path.stem)
        doc_id = f"{doc_id_match.group(1)}-{doc_id_match.group(2)}" if doc_id_match else "UNKNOWN"

        template = self.TRACEABILITY_TEMPLATE.format(doc_id=doc_id)

        # Add before document end or after last section
        if content.rstrip().endswith('---'):
            content = content.rstrip()[:-3] + template + "\n---"
        else:
            content = content.rstrip() + "\n\n" + template

        return content

    def _fix_missing_tag(self, content: str, issue: ValidationIssue, doc_path: Path) -> str:
        """Add missing cumulative tag"""
        # Extract tag name from issue message
        tag_match = re.search(r'@(\w+)', issue.message)
        if not tag_match:
            return content

        tag_name = tag_match.group(1)

        # Find first available upstream document of that type
        upstream_type = tag_name.upper()
        upstream_docs = self.index.get_documents_by_type(upstream_type)

        if upstream_docs:
            # Use first document as reference
            ref_id = upstream_docs[0]
            new_tag = f"@{tag_name}: {ref_id}"
        else:
            new_tag = f"@{tag_name}: null"

        # Find traceability section and add tag
        trace_match = TRACEABILITY_SECTION_PATTERN.search(content)
        if trace_match:
            insert_pos = trace_match.end()
            # Find next line after traceability heading
            next_line = content.find('\n', insert_pos)
            if next_line != -1:
                content = content[:next_line + 1] + new_tag + "\n" + content[next_line + 1:]
        else:
            # Add at end
            content += f"\n{new_tag}\n"

        return content

    def _fix_tag_format(self, content: str, issue: ValidationIssue) -> str:
        """Fix invalid tag format"""
        # Extract the invalid tag from issue
        match = re.search(r'@(\w+):\s*([^\s]+)', issue.message)
        if not match:
            return content

        tag_name = match.group(1)
        bad_value = match.group(2)

        # Try to extract valid ID components
        id_parts = re.findall(r'([A-Z]+).*?(\d{2,})', bad_value.upper())
        if id_parts:
            corrected = f"{id_parts[0][0]}-{id_parts[0][1]}"
            pattern = re.compile(rf'@{tag_name}:\s*{re.escape(bad_value)}', re.IGNORECASE)
            content = pattern.sub(f'@{tag_name}: {corrected}', content)

        return content

    def _fix_missing_upstream(self, content: str, issue: ValidationIssue, doc_path: Path) -> Optional[str]:
        """Remove functionality requiring missing upstream (strict hierarchy)"""
        # Extract the missing document reference (supports TYPE-NN and TYPE-NN.S section files)
        match = re.search(r'([A-Z]+-\d{2,}(?:\.\d+)?)', issue.message)
        if not match:
            return content

        missing_id = match.group(1)
        tag_type = missing_id.split('-')[0].lower()

        # XDOC-003 confirmation requirement (unless --force-xdoc or --dry-run)
        if not self.force_xdoc and not self.dry_run:
            print(f"\nWARNING: XDOC-003 - Removing reference to missing document: {missing_id}")
            print(f"  File: {doc_path.name}")
            print(f"  Tag:  @{tag_type}: {missing_id}")
            response = input("Continue with removal? [y/N]: ")
            if response.lower() != 'y':
                print(f"  Skipped removal of @{tag_type}: {missing_id}")
                return None

        # Find the tag line being removed (for audit)
        tag_pattern = re.compile(rf'^@{tag_type}:\s*{re.escape(missing_id)}.*$', re.MULTILINE | re.IGNORECASE)
        tag_match = tag_pattern.search(content)
        removed_line = tag_match.group(0) if tag_match else f"@{tag_type}: {missing_id}"

        # Remove the tag line referencing missing upstream
        remove_pattern = re.compile(rf'^@{tag_type}:\s*{re.escape(missing_id)}.*$\n?', re.MULTILINE | re.IGNORECASE)
        content = remove_pattern.sub('', content)

        # Add comment noting removal
        removal_comment = f"<!-- Removed @{tag_type} reference: {missing_id} not found (strict hierarchy enforcement) -->\n"

        # Insert after frontmatter if present
        frontmatter_end = content.find('---', 3)
        if frontmatter_end != -1:
            insert_pos = content.find('\n', frontmatter_end) + 1
            content = content[:insert_pos] + removal_comment + content[insert_pos:]
        else:
            content = removal_comment + content

        # Create audit entry
        backup_path = doc_path.with_suffix(doc_path.suffix + '.bak') if self.create_backup else None
        self.audit_entries.append({
            "timestamp": datetime.now().isoformat(),
            "file": str(doc_path),
            "issue_code": issue.code.value,
            "action": "removed_tag",
            "removed_content": removed_line,
            "backup_path": str(backup_path) if backup_path else None
        })

        return content

    def _fix_deprecated_reference(self, content: str, issue: ValidationIssue) -> str:
        """Remove or mark deprecated reference"""
        # Supports TYPE-NN and TYPE-NN.S section files
        match = re.search(r'([A-Z]+-\d{2,}(?:\.\d+)?)', issue.message)
        if not match:
            return content

        deprecated_id = match.group(1)
        tag_type = deprecated_id.split('-')[0].lower()

        # Replace with null and add comment
        pattern = re.compile(rf'(@{tag_type}:\s*){re.escape(deprecated_id)}', re.IGNORECASE)
        replacement = f'@{tag_type}: null  <!-- Previously: {deprecated_id} (deprecated) -->'
        content = pattern.sub(replacement, content)

        return content

    def _fix_broken_link(self, content: str, issue: ValidationIssue) -> str:
        """Fix or remove broken link"""
        match = re.search(r'Broken internal link:\s*(.+)', issue.message)
        if not match:
            return content

        broken_path = match.group(1).strip()

        # Try to find correct path
        # For now, just comment out the broken link
        pattern = re.compile(rf'\[([^\]]+)\]\({re.escape(broken_path)}\)')
        content = pattern.sub(r'<!-- Broken link removed: [\1](' + broken_path + ') -->', content)

        return content

    def _backup_document(self, doc_path: Path) -> None:
        """Create backup of document before modification"""
        backup_path = doc_path.with_suffix(doc_path.suffix + '.bak')
        shutil.copy2(doc_path, backup_path)

    def _restore_backup(self, doc_path: Path) -> None:
        """Restore document from backup"""
        backup_path = doc_path.with_suffix(doc_path.suffix + '.bak')
        if backup_path.exists():
            shutil.copy2(backup_path, doc_path)

    def cleanup_backups(self, doc_path: Path) -> None:
        """Remove backup file after successful validation"""
        backup_path = doc_path.with_suffix(doc_path.suffix + '.bak')
        if backup_path.exists():
            backup_path.unlink()

    def write_audit_log(self) -> Optional[Path]:
        """
        Write audit entries to JSON log file.

        Returns:
            Path to audit log file, or None if no entries
        """
        if not self.audit_entries:
            return None

        log_path = Path('tmp/validation_audit.json')
        log_path.parent.mkdir(exist_ok=True)

        existing = []
        if log_path.exists():
            try:
                existing = json.loads(log_path.read_text())
            except json.JSONDecodeError:
                existing = []

        existing.extend(self.audit_entries)
        log_path.write_text(json.dumps(existing, indent=2))
        return log_path


def generate_report(doc_path: Optional[Path], issues: List[ValidationIssue], phase: int = 1) -> str:
    """
    Generate validation report

    Args:
        doc_path: Path to validated document (or None for layer/all validation)
        issues: List of validation issues
        phase: Validation phase (1=per-document, 2=per-layer, 3=final)

    Returns:
        Formatted markdown report
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Count by severity and fixed status
    errors_found = sum(1 for i in issues if i.severity == Severity.ERROR)
    errors_fixed = sum(1 for i in issues if i.severity == Severity.ERROR and i.fixed)
    warnings_found = sum(1 for i in issues if i.severity == Severity.WARNING)
    warnings_fixed = sum(1 for i in issues if i.severity == Severity.WARNING and i.fixed)

    remaining = [i for i in issues if not i.fixed]

    # Determine status
    if not remaining:
        status = "PASSED"
    elif any(i.severity == Severity.ERROR for i in remaining):
        status = "FAILED"
    else:
        status = "PASSED_WITH_WARNINGS"

    report = f"""# Cross-Document Validation Report

**Document**: {doc_path if doc_path else 'Multiple documents'}
**Timestamp**: {timestamp}
**Phase**: {phase}

## Fixes Applied

### ERRORS Fixed ({errors_fixed}/{errors_found})
| Code | Issue | Fix Applied |
|------|-------|-------------|
"""

    for issue in issues:
        if issue.severity == Severity.ERROR and issue.fixed:
            report += f"| {issue.code.value} | {issue.message} | {issue.fix_action or 'Fixed'} |\n"

    report += f"""
### WARNINGS Fixed ({warnings_fixed}/{warnings_found})
| Code | Issue | Fix Applied |
|------|-------|-------------|
"""

    for issue in issues:
        if issue.severity == Severity.WARNING and issue.fixed:
            report += f"| {issue.code.value} | {issue.message} | {issue.fix_action or 'Fixed'} |\n"

    if remaining:
        report += f"""
## Remaining Issues ({len(remaining)})
| Code | Severity | Issue | Action |
|------|----------|-------|--------|
"""
        for issue in remaining:
            report += f"| {issue.code.value} | {issue.severity.value} | {issue.message} | {issue.fix_action or 'Manual review'} |\n"

    report += f"""
## Summary
- Status: **{status}**
- Errors: {errors_found} found, {errors_fixed} fixed, {errors_found - errors_fixed} manual
- Warnings: {warnings_found} found, {warnings_fixed} fixed
"""

    return report


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Cross-document validation for AI Dev Flow framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Per-document validation
  python validate_cross_document.py --document docs/REQ/REQ-01.md --auto-fix

  # Per-layer validation
  python validate_cross_document.py --layer REQ --auto-fix

  # Full validation (all layers)
  python validate_cross_document.py --all --auto-fix --strict
        """
    )

    parser.add_argument(
        '--document', '-d',
        help='Path to specific document to validate'
    )

    parser.add_argument(
        '--layer', '-l',
        choices=list(LAYER_CONFIG.keys()),
        help='Validate all documents of a specific layer type'
    )

    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Validate all documents across all layers'
    )

    parser.add_argument(
        '--auto-fix', '-f',
        action='store_true',
        help='Automatically fix issues without confirmation'
    )

    parser.add_argument(
        '--strict', '-s',
        action='store_true',
        help='Treat warnings as errors'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create backup files before auto-fix'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )

    parser.add_argument(
        '--force-xdoc',
        action='store_true',
        help='Skip confirmation for XDOC-003 tag removals'
    )

    parser.add_argument(
        '--root',
        default='.',
        help='Root directory of the project (default: current directory)'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file for validation report'
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.document, args.layer, args.all]):
        parser.error("Must specify --document, --layer, or --all")

    docs_root = Path(args.root).resolve()

    # Build requirement index
    print("Building requirement index...")
    index = RequirementIndex(docs_root)
    index.build_index()
    print(f"Indexed {len(index.requirements)} documents")

    # Initialize validator
    validator = CrossDocumentValidator(docs_root, index)

    # Run validation
    issues = []
    validated_paths = []

    if args.document:
        doc_path = Path(args.document).resolve()
        print(f"\nValidating document: {doc_path}")
        issues = validator.validate_document(doc_path)
        validated_paths = [doc_path]

    elif args.layer:
        print(f"\nValidating layer: {args.layer}")
        issues = validator.validate_layer(args.layer)
        docs_dir = docs_root / "docs" / args.layer
        if docs_dir.exists():
            validated_paths = list(docs_dir.glob("*.md")) + list(docs_dir.glob("*.yaml"))

    elif args.all:
        print("\nValidating all layers...")
        issues = validator.validate_all()
        for layer_type in LAYER_CONFIG.keys():
            docs_dir = docs_root / "docs" / layer_type
            if docs_dir.exists():
                validated_paths.extend(docs_dir.glob("*.md"))
                validated_paths.extend(docs_dir.glob("*.yaml"))

    # Apply auto-fixes if requested
    if args.auto_fix and issues:
        mode_msg = "[DRY-RUN] Previewing" if args.dry_run else "Applying"
        print(f"\n{mode_msg} auto-fixes...")
        fixer = AutoFixer(docs_root, index, create_backup=not args.no_backup,
                          dry_run=args.dry_run, force_xdoc=args.force_xdoc)

        # Group issues by document
        issues_by_doc = defaultdict(list)
        for issue in issues:
            issues_by_doc[issue.location].append(issue)

        # Fix each document
        for doc_path_str, doc_issues in issues_by_doc.items():
            doc_path = Path(doc_path_str)
            if doc_path.exists():
                fixer.fix_issues(doc_path, doc_issues)

        # Print changes log
        if fixer.changes_log:
            print("\nChanges applied:")
            for change in fixer.changes_log:
                print(f"  - {change}")

        # Write audit log
        audit_path = fixer.write_audit_log()
        if audit_path:
            print(f"\nAudit log written to: {audit_path}")

        # Re-validate to check remaining issues (skip in dry-run mode)
        if args.dry_run:
            print("\n[DRY-RUN] Skipping re-validation (no changes were made)")
        else:
            print("\nRe-validating after fixes...")
            if args.document:
                issues = validator.validate_document(Path(args.document).resolve())
            elif args.layer:
                issues = validator.validate_layer(args.layer)
            else:
                issues = validator.validate_all()

            # Cleanup backups if all issues fixed
            remaining_issues = [i for i in issues if not i.fixed]
            if not remaining_issues and not args.no_backup:
                for doc_path in validated_paths:
                    fixer.cleanup_backups(doc_path)

    # Generate report
    phase = 1 if args.document else (2 if args.layer else 3)
    report = generate_report(
        Path(args.document) if args.document else None,
        issues,
        phase
    )

    # Output report
    print("\n" + "=" * 80)
    print(report)
    print("=" * 80)

    if args.output:
        Path(args.output).write_text(report, encoding='utf-8')
        print(f"\nReport saved to: {args.output}")

    # Determine exit code
    remaining_errors = sum(1 for i in issues if i.severity == Severity.ERROR and not i.fixed)
    remaining_warnings = sum(1 for i in issues if i.severity == Severity.WARNING and not i.fixed)

    if remaining_errors > 0:
        return 1
    if args.strict and remaining_warnings > 0:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
