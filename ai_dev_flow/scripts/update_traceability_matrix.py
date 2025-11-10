#!/usr/bin/env python3
"""
Incrementally Update Traceability Matrix

This script updates an existing traceability matrix by:
1. Detecting new documents added since last update
2. Detecting removed documents
3. Updating metadata for changed documents
4. Recalculating statistics and coverage metrics
5. Preserving manual edits and notes

Usage:
    python update_traceability_matrix.py --matrix TRACEABILITY_MATRIX_ADR.md --input ../ADR/

Features:
- Incremental updates (faster than full regeneration)
- Preserves manual edits outside auto-generated sections
- Detects new, modified, and deleted documents
- Updates statistics and coverage metrics
- Generates update changelog
- Backup creation before updates

Author: AI-Driven SDD Framework
Version: 1.0.0
"""

import argparse
import os
import re
import sys
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict


class DocumentMetadata:
    """Represents metadata extracted from a document"""

    def __init__(self, doc_id: str, filepath: str):
        self.doc_id = doc_id
        self.filepath = filepath
        self.title = ""
        self.status = "Unknown"
        self.date = ""
        self.upstream_sources = []
        self.downstream_artifacts = []
        self.category = ""
        self.modified_time = None

    def __repr__(self):
        return f"DocumentMetadata({self.doc_id}, {self.title})"


class MatrixUpdate:
    """Represents an update to be made to the matrix"""

    def __init__(self, update_type: str, doc_id: str, description: str):
        self.update_type = update_type  # ADD, REMOVE, MODIFY
        self.doc_id = doc_id
        self.description = description
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"[{self.update_type}] {self.doc_id}: {self.description}"


class TraceabilityMatrixUpdater:
    """Incrementally updates traceability matrices"""

    SUPPORTED_TYPES = [
        'BRD', 'PRD', 'EARS', 'BDD', 'ADR', 'SYS',
        'REQ', 'IMPL', 'CTR', 'SPEC', 'TASKS'
    ]

    def __init__(self, matrix_path: str, input_dir: str, dry_run: bool = False):
        """
        Initialize the updater

        Args:
            matrix_path: Path to traceability matrix file to update
            input_dir: Directory containing actual documents
            dry_run: Preview changes without modifying files
        """
        self.matrix_path = Path(matrix_path).resolve()
        self.input_dir = Path(input_dir).resolve()
        self.dry_run = dry_run

        self.doc_type = self._detect_doc_type()

        # Current state from matrix
        self.matrix_doc_ids: Set[str] = set()
        self.matrix_metadata: Dict[str, Dict] = {}

        # Current state from filesystem
        self.actual_documents: Dict[str, DocumentMetadata] = {}

        # Detected changes
        self.updates: List[MatrixUpdate] = []

        if not self.matrix_path.exists():
            raise FileNotFoundError(f"Matrix file not found: {self.matrix_path}")

        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {self.input_dir}")

    def _detect_doc_type(self) -> str:
        """Detect document type from matrix filename"""
        filename = self.matrix_path.name

        for doc_type in self.SUPPORTED_TYPES:
            if doc_type in filename.upper():
                return doc_type

        raise ValueError(f"Cannot detect document type from matrix filename: {filename}")

    def scan_actual_documents(self):
        """Scan input directory for actual document files"""
        print(f"Scanning actual documents in: {self.input_dir}")

        pattern = re.compile(rf'{self.doc_type}-(\d{{3,4}}(?:-\d{{2,3}})?)[_-].*\.(md|feature|yaml)$')

        for filepath in self.input_dir.rglob('*'):
            if not filepath.is_file():
                continue

            match = pattern.match(filepath.name)
            if match:
                doc_id = f"{self.doc_type}-{match.group(1)}"
                metadata = DocumentMetadata(doc_id, str(filepath))
                metadata.modified_time = filepath.stat().st_mtime
                self.extract_metadata(metadata)
                self.actual_documents[doc_id] = metadata

        print(f"Found {len(self.actual_documents)} actual {self.doc_type} documents")

    def extract_metadata(self, doc: DocumentMetadata) -> DocumentMetadata:
        """Extract metadata from a document file"""
        try:
            with open(doc.filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract title (from H1 heading)
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                doc.title = title_match.group(1).strip()
                doc.title = re.sub(rf'^{re.escape(doc.doc_id)}:\s*', '', doc.title)

            # Extract status
            status_match = re.search(r'\|\s*Status\s*\|\s*([^\|]+)\s*\|', content, re.IGNORECASE)
            if status_match:
                doc.status = status_match.group(1).strip()

            # Extract date
            date_match = re.search(r'\|\s*Date\s*(?:Created)?\s*\|\s*(\d{4}-\d{2}-\d{2})', content, re.IGNORECASE)
            if date_match:
                doc.date = date_match.group(1)

            # Extract upstream sources
            upstream_section = re.search(
                r'##\s+7\.?\s+Traceability.*?###\s+Upstream\s+Sources(.*?)###\s+Downstream',
                content, re.DOTALL | re.IGNORECASE
            )
            if upstream_section:
                upstream_text = upstream_section.group(1)
                upstream_ids = re.findall(r'\[([A-Z]+-\d+(?:-\d+)?)\]', upstream_text)
                doc.upstream_sources = list(set(upstream_ids))

            # Extract downstream artifacts
            downstream_section = re.search(
                r'###\s+Downstream\s+Artifacts(.*?)(?:##|$)',
                content, re.DOTALL | re.IGNORECASE
            )
            if downstream_section:
                downstream_text = downstream_section.group(1)
                downstream_ids = re.findall(r'\[([A-Z]+-\d+(?:-\d+)?)\]', downstream_text)
                doc.downstream_artifacts = list(set(downstream_ids))

            # Extract category
            relative_path = Path(doc.filepath).relative_to(self.input_dir)
            if len(relative_path.parts) > 1:
                doc.category = relative_path.parts[0]

        except Exception as e:
            print(f"Warning: Error extracting metadata from {doc.filepath}: {e}")

        return doc

    def parse_existing_matrix(self):
        """Parse existing matrix to extract current document list"""
        print(f"Parsing existing matrix: {self.matrix_path}")

        try:
            with open(self.matrix_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find inventory table
            inventory_section = re.search(
                r'##\s+2\.\s+Complete.*?Inventory(.*?)(?:##|\Z)',
                content, re.DOTALL | re.IGNORECASE
            )

            if not inventory_section:
                print("Warning: Cannot find inventory section")
                return

            inventory_text = inventory_section.group(1)

            # Extract table rows
            table_rows = re.findall(
                rf'\|\s*({self.doc_type}-\d{{3,4}}(?:-\d{{2,3}})?)\s*\|([^\|]*)\|([^\|]*)\|([^\|]*)\|([^\|]*)\|([^\|]*)\|([^\|]*)\|',
                inventory_text
            )

            for row in table_rows:
                doc_id = row[0].strip()
                self.matrix_doc_ids.add(doc_id)

                self.matrix_metadata[doc_id] = {
                    'title': row[1].strip(),
                    'category': row[2].strip(),
                    'status': row[3].strip(),
                    'date': row[4].strip(),
                    'upstream': row[5].strip(),
                    'downstream': row[6].strip()
                }

            print(f"Found {len(self.matrix_doc_ids)} documents in existing matrix")

        except Exception as e:
            print(f"Error parsing existing matrix: {e}")

    def detect_changes(self):
        """Detect changes between matrix and actual documents"""
        print("Detecting changes...")

        actual_doc_ids = set(self.actual_documents.keys())

        # New documents (in filesystem, not in matrix)
        new_docs = actual_doc_ids - self.matrix_doc_ids
        for doc_id in new_docs:
            doc = self.actual_documents[doc_id]
            self.updates.append(MatrixUpdate(
                "ADD",
                doc_id,
                f"New document: {doc.title or 'Untitled'}"
            ))

        # Removed documents (in matrix, not in filesystem)
        removed_docs = self.matrix_doc_ids - actual_doc_ids
        for doc_id in removed_docs:
            self.updates.append(MatrixUpdate(
                "REMOVE",
                doc_id,
                "Document no longer exists"
            ))

        # Modified documents (in both, but metadata changed)
        common_docs = actual_doc_ids & self.matrix_doc_ids
        for doc_id in common_docs:
            doc = self.actual_documents[doc_id]
            matrix_meta = self.matrix_metadata.get(doc_id, {})

            # Check if metadata changed
            changes = []

            if doc.title != matrix_meta.get('title'):
                changes.append(f"title changed to '{doc.title}'")

            if doc.status != matrix_meta.get('status'):
                changes.append(f"status changed to '{doc.status}'")

            if changes:
                self.updates.append(MatrixUpdate(
                    "MODIFY",
                    doc_id,
                    ", ".join(changes)
                ))

        print(f"Detected {len(self.updates)} changes")
        for update in self.updates:
            print(f"  {update}")

    def calculate_coverage_metrics(self) -> Dict[str, any]:
        """Calculate coverage metrics from actual documents"""
        metrics = {
            'total_documents': len(self.actual_documents),
            'status_breakdown': defaultdict(int),
            'upstream_coverage': 0,
            'downstream_coverage': 0,
            'orphaned_documents': [],
            'missing_dates': 0,
        }

        for doc in self.actual_documents.values():
            metrics['status_breakdown'][doc.status] += 1

            if doc.upstream_sources:
                metrics['upstream_coverage'] += 1
            else:
                metrics['orphaned_documents'].append(doc.doc_id)

            if doc.downstream_artifacts:
                metrics['downstream_coverage'] += 1

            if not doc.date:
                metrics['missing_dates'] += 1

        if metrics['total_documents'] > 0:
            metrics['upstream_coverage_pct'] = (metrics['upstream_coverage'] / metrics['total_documents']) * 100
            metrics['downstream_coverage_pct'] = (metrics['downstream_coverage'] / metrics['total_documents']) * 100
        else:
            metrics['upstream_coverage_pct'] = 0
            metrics['downstream_coverage_pct'] = 0

        return metrics

    def generate_inventory_table(self) -> str:
        """Generate updated markdown table of document inventory"""
        if not self.actual_documents:
            return "| No documents found |\n"

        # Sort documents by ID
        sorted_docs = sorted(self.actual_documents.values(), key=lambda d: d.doc_id)

        table = f"| {self.doc_type} ID | Title | Category | Status | Date | Upstream Sources | Downstream Artifacts |\n"
        table += "|" + "---|" * 7 + "\n"

        for doc in sorted_docs:
            upstream = ", ".join(doc.upstream_sources[:3])
            if len(doc.upstream_sources) > 3:
                upstream += f" (+{len(doc.upstream_sources) - 3} more)"

            downstream = ", ".join(doc.downstream_artifacts[:3])
            if len(doc.downstream_artifacts) > 3:
                downstream += f" (+{len(doc.downstream_artifacts) - 3} more)"

            table += f"| {doc.doc_id} | {doc.title or 'Untitled'} | {doc.category or 'N/A'} | {doc.status} | {doc.date or 'N/A'} | {upstream or 'None'} | {downstream or 'None'} |\n"

        return table

    def update_matrix(self):
        """Update the matrix file with changes"""
        if not self.updates and len(self.matrix_doc_ids) == len(self.actual_documents):
            print("✅ Matrix is already up-to-date. No changes needed.")
            return

        print(f"Updating matrix file: {self.matrix_path}")

        if self.dry_run:
            print("DRY RUN: Changes preview only, file not modified")
        else:
            # Create backup
            backup_path = self.matrix_path.with_suffix('.md.backup')
            shutil.copy2(self.matrix_path, backup_path)
            print(f"Backup created: {backup_path}")

        # Read existing matrix
        with open(self.matrix_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update Document Control table (last updated date)
        content = re.sub(
            r'(\|\s*Date\s+Created\s*\|)\s*([^\|]+)\s*\|',
            rf'\1 {datetime.now().strftime("%Y-%m-%d")} |',
            content,
            flags=re.IGNORECASE
        )

        # Update statistics section
        metrics = self.calculate_coverage_metrics()

        content = re.sub(
            r'(\*\*Total\s+' + self.doc_type + r'\s+Tracked\*\*:)\s*\d+',
            rf'\1 {metrics["total_documents"]}',
            content,
            flags=re.IGNORECASE
        )

        content = re.sub(
            r'(\*\*Upstream Coverage\*\*:)\s*[\d.]+%\s*\([\d]+/[\d]+\)',
            rf'\1 {metrics["upstream_coverage_pct"]:.1f}% ({metrics["upstream_coverage"]}/{metrics["total_documents"]})',
            content,
            flags=re.IGNORECASE
        )

        content = re.sub(
            r'(\*\*Downstream Coverage\*\*:)\s*[\d.]+%\s*\([\d]+/[\d]+\)',
            rf'\1 {metrics["downstream_coverage_pct"]:.1f}% ({metrics["downstream_coverage"]}/{metrics["total_documents"]})',
            content,
            flags=re.IGNORECASE
        )

        content = re.sub(
            r'(\*\*Orphaned Documents\*\*:)\s*\d+',
            rf'\1 {len(metrics["orphaned_documents"])}',
            content,
            flags=re.IGNORECASE
        )

        content = re.sub(
            r'(\*\*Last Generated\*\*:)\s*[\d-]+\s+[\d:]+',
            rf'\1 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            content,
            flags=re.IGNORECASE
        )

        # Update status breakdown section
        status_section = "### 1.2 Status Breakdown\n\n"
        for status, count in sorted(metrics['status_breakdown'].items()):
            percentage = (count / metrics['total_documents']) * 100 if metrics['total_documents'] > 0 else 0
            status_section += f"- **{status}**: {count} documents ({percentage:.1f}%)\n"
        status_section += "\n"

        content = re.sub(
            r'###\s+1\.2\s+Status\s+Breakdown.*?(?=##)',
            status_section,
            content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Update inventory table (Section 2)
        new_table = self.generate_inventory_table()

        inventory_pattern = r'(##\s+2\.\s+Complete.*?Inventory\s*\n\n)(.*?)(?=\n\n##)'
        content = re.sub(
            inventory_pattern,
            rf'\1{new_table}',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Update coverage metrics table (Section 5)
        coverage_table = "| Metric | Value | Target | Status |\n"
        coverage_table += "|--------|-------|--------|--------|\n"
        coverage_table += f"| Upstream Traceability | {metrics['upstream_coverage_pct']:.1f}% | 100% | {'✅' if metrics['upstream_coverage_pct'] >= 100 else '🟡' if metrics['upstream_coverage_pct'] >= 80 else '🔴'} |\n"
        coverage_table += f"| Downstream Artifacts | {metrics['downstream_coverage_pct']:.1f}% | 90% | {'✅' if metrics['downstream_coverage_pct'] >= 90 else '🟡' if metrics['downstream_coverage_pct'] >= 70 else '🔴'} |\n"
        coverage_table += f"| Orphaned Documents | {len(metrics['orphaned_documents'])} | 0 | {'✅' if len(metrics['orphaned_documents']) == 0 else '🔴'} |\n\n"

        content = re.sub(
            r'(##\s+5\.\s+Coverage\s+Metrics\s*\n\n)(.*?)(?=\n\n##)',
            rf'\1{coverage_table}',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Add revision history entry
        new_revision = f"| {datetime.now().strftime('%Y-%m-%d')} | Incremental update: "
        if self.updates:
            change_summary = f"{len([u for u in self.updates if u.update_type == 'ADD'])} added, "
            change_summary += f"{len([u for u in self.updates if u.update_type == 'REMOVE'])} removed, "
            change_summary += f"{len([u for u in self.updates if u.update_type == 'MODIFY'])} modified"
            new_revision += change_summary
        else:
            new_revision += "Statistics refresh"
        new_revision += " | update_traceability_matrix.py |\n"

        # Insert before the closing revision history marker
        content = re.sub(
            r'(##\s+7\.\s+Revision\s+History.*?\n\n.*?\n\|[-|]+\|.*?\n)(.*?)(---)',
            rf'\1{new_revision}\2\3',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )

        if not self.dry_run:
            # Write updated content
            with open(self.matrix_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✅ Matrix updated successfully")
            print(f"📊 Updated statistics:")
            print(f"   - Total documents: {metrics['total_documents']}")
            print(f"   - Upstream coverage: {metrics['upstream_coverage_pct']:.1f}%")
            print(f"   - Downstream coverage: {metrics['downstream_coverage_pct']:.1f}%")
            print(f"   - Orphaned documents: {len(metrics['orphaned_documents'])}")
        else:
            print("\nDRY RUN COMPLETE - Preview of changes:")
            print(f"   - Total documents: {metrics['total_documents']}")
            print(f"   - Changes detected: {len(self.updates)}")
            print(f"   - New documents: {len([u for u in self.updates if u.update_type == 'ADD'])}")
            print(f"   - Removed documents: {len([u for u in self.updates if u.update_type == 'REMOVE'])}")
            print(f"   - Modified documents: {len([u for u in self.updates if u.update_type == 'MODIFY'])}")

    def generate_changelog(self) -> str:
        """Generate changelog of updates"""
        if not self.updates:
            return "No changes detected."

        changelog = "# Matrix Update Changelog\n\n"
        changelog += f"**Matrix**: {self.matrix_path.name}\n"
        changelog += f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        changelog += f"**Total Changes**: {len(self.updates)}\n\n"

        # Group by update type
        adds = [u for u in self.updates if u.update_type == "ADD"]
        removes = [u for u in self.updates if u.update_type == "REMOVE"]
        modifies = [u for u in self.updates if u.update_type == "MODIFY"]

        if adds:
            changelog += f"## Added ({len(adds)} documents)\n\n"
            for update in adds:
                changelog += f"- {update.doc_id}: {update.description}\n"
            changelog += "\n"

        if removes:
            changelog += f"## Removed ({len(removes)} documents)\n\n"
            for update in removes:
                changelog += f"- {update.doc_id}: {update.description}\n"
            changelog += "\n"

        if modifies:
            changelog += f"## Modified ({len(modifies)} documents)\n\n"
            for update in modifies:
                changelog += f"- {update.doc_id}: {update.description}\n"
            changelog += "\n"

        return changelog

    def update(self):
        """Run incremental update process"""
        print(f"Updating traceability matrix: {self.matrix_path.name}")
        print(f"Document type: {self.doc_type}")
        print(f"Input directory: {self.input_dir}\n")

        # Scan and detect changes
        self.parse_existing_matrix()
        self.scan_actual_documents()
        self.detect_changes()

        # Generate changelog
        changelog = self.generate_changelog()
        print("\n" + "="*80)
        print(changelog)
        print("="*80 + "\n")

        # Apply updates
        self.update_matrix()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Incrementally update traceability matrix',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update ADR matrix
  python update_traceability_matrix.py --matrix TRACEABILITY_MATRIX_ADR.md --input ../ADR/

  # Preview changes without modifying file
  python update_traceability_matrix.py --matrix matrix.md --input ../SPEC/ --dry-run

  # Update and save changelog
  python update_traceability_matrix.py --matrix matrix.md --input ../REQ/ --changelog changelog.md
        """
    )

    parser.add_argument(
        '--matrix',
        required=True,
        help='Path to traceability matrix file to update'
    )

    parser.add_argument(
        '--input',
        required=True,
        help='Input directory containing actual documents'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying matrix file'
    )

    parser.add_argument(
        '--changelog',
        help='Output file for update changelog (optional)'
    )

    args = parser.parse_args()

    try:
        updater = TraceabilityMatrixUpdater(
            matrix_path=args.matrix,
            input_dir=args.input,
            dry_run=args.dry_run
        )

        updater.update()

        # Save changelog if requested
        if args.changelog:
            changelog = updater.generate_changelog()
            with open(args.changelog, 'w', encoding='utf-8') as f:
                f.write(changelog)
            print(f"✅ Changelog saved: {args.changelog}")

        return 0

    except Exception as e:
        print(f"❌ Update failed: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
