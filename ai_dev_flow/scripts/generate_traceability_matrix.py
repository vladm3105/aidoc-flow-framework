#!/usr/bin/env python3
"""
Generate Traceability Matrix from Document Directory

This script automatically generates a traceability matrix by scanning a document
directory, extracting metadata, and populating a matrix template with actual data.

Usage:
    python generate_traceability_matrix.py --type ADR --input ../ADR/ --output TRACEABILITY_MATRIX_ADR.md

Features:
- Scans document directory for all files matching TYPE-NN pattern
- Extracts document metadata (ID, title, status, date, links)
- Populates matrix template with actual document data
- Generates Mermaid dependency diagrams
- Calculates coverage metrics
- Validates document structure and traceability

Author: AI-Driven SDD Framework
Version: 1.0.0
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
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

    def __repr__(self):
        return f"DocumentMetadata({self.doc_id}, {self.title})"


class TraceabilityMatrixGenerator:
    """Generates traceability matrices from document directories"""

    SUPPORTED_TYPES = [
        'BRD', 'PRD', 'EARS', 'BDD', 'ADR', 'SYS',
        'REQ', 'CTR', 'SPEC', 'TASKS'
    ]

    def __init__(self, doc_type: str, input_dir: str, template_path: Optional[str] = None):
        """
        Initialize the generator

        Args:
            doc_type: Document type (BRD, PRD, ADR, etc.)
            input_dir: Directory containing documents to scan
            template_path: Path to matrix template (optional)
        """
        if doc_type.upper() not in self.SUPPORTED_TYPES:
            raise ValueError(f"Unsupported document type: {doc_type}. Supported: {self.SUPPORTED_TYPES}")

        self.doc_type = doc_type.upper()
        self.input_dir = Path(input_dir).resolve()
        self.template_path = Path(template_path) if template_path else None
        self.documents: List[DocumentMetadata] = []

        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {self.input_dir}")

    def scan_documents(self) -> List[DocumentMetadata]:
        """
        Scan input directory for documents matching TYPE-NN pattern

        Returns:
            List of DocumentMetadata objects
        """
        print(f"Scanning directory: {self.input_dir}")

        # Pattern: TYPE-NN_slug.ext or TYPE-NN-YY_slug.ext
        pattern = re.compile(rf'{self.doc_type}-(\d{{2,}}(?:-\d{{2,3}})?)[_-].*\.(md|feature|yaml)$')

        found_docs = []

        # Recursively search for matching files
        for filepath in self.input_dir.rglob('*'):
            if not filepath.is_file():
                continue

            match = pattern.match(filepath.name)
            if match:
                doc_id = f"{self.doc_type}-{match.group(1)}"
                metadata = DocumentMetadata(doc_id, str(filepath))
                found_docs.append(metadata)

        # Sort by document ID
        found_docs.sort(key=lambda x: x.doc_id)

        print(f"Found {len(found_docs)} {self.doc_type} documents")

        self.documents = found_docs
        return found_docs

    def extract_metadata(self, doc: DocumentMetadata) -> DocumentMetadata:
        """
        Extract metadata from a document file

        Args:
            doc: DocumentMetadata object with filepath

        Returns:
            Updated DocumentMetadata with extracted information
        """
        try:
            with open(doc.filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract title (from H1 heading)
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                doc.title = title_match.group(1).strip()
                # Remove document ID from title if present
                doc.title = re.sub(rf'^{re.escape(doc.doc_id)}:\s*', '', doc.title)

            # Extract status from document control table
            status_match = re.search(r'\|\s*Status\s*\|\s*([^\|]+)\s*\|', content, re.IGNORECASE)
            if status_match:
                doc.status = status_match.group(1).strip()

            # Extract date
            date_match = re.search(r'\|\s*Date\s*(?:Created)?\s*\|\s*(\d{4}-\d{2}-\d{2})', content, re.IGNORECASE)
            if date_match:
                doc.date = date_match.group(1)

            # Extract upstream sources from Section 7 Traceability
            upstream_section = re.search(
                r'##\s+7\.?\s+Traceability.*?###\s+Upstream\s+Sources(.*?)###\s+Downstream',
                content, re.DOTALL | re.IGNORECASE
            )
            if upstream_section:
                upstream_text = upstream_section.group(1)
                # Extract document IDs from markdown links
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

            # Extract category (domain/phase/type)
            # Try to determine from file path or document content
            relative_path = Path(doc.filepath).relative_to(self.input_dir)
            if len(relative_path.parts) > 1:
                doc.category = relative_path.parts[0]

        except Exception as e:
            print(f"Warning: Error extracting metadata from {doc.filepath}: {e}")

        return doc

    def extract_all_metadata(self):
        """Extract metadata from all scanned documents"""
        print(f"Extracting metadata from {len(self.documents)} documents...")

        for doc in self.documents:
            self.extract_metadata(doc)

        print("Metadata extraction complete")

    def calculate_coverage_metrics(self) -> Dict[str, any]:
        """
        Calculate coverage metrics for the document set

        Returns:
            Dictionary of coverage metrics
        """
        metrics = {
            'total_documents': len(self.documents),
            'status_breakdown': defaultdict(int),
            'upstream_coverage': 0,
            'downstream_coverage': 0,
            'orphaned_documents': [],
            'missing_dates': 0,
        }

        for doc in self.documents:
            # Status breakdown
            metrics['status_breakdown'][doc.status] += 1

            # Upstream coverage
            if doc.upstream_sources:
                metrics['upstream_coverage'] += 1
            else:
                metrics['orphaned_documents'].append(doc.doc_id)

            # Downstream coverage
            if doc.downstream_artifacts:
                metrics['downstream_coverage'] += 1

            # Missing dates
            if not doc.date:
                metrics['missing_dates'] += 1

        # Calculate percentages
        if metrics['total_documents'] > 0:
            metrics['upstream_coverage_pct'] = (metrics['upstream_coverage'] / metrics['total_documents']) * 100
            metrics['downstream_coverage_pct'] = (metrics['downstream_coverage'] / metrics['total_documents']) * 100
        else:
            metrics['upstream_coverage_pct'] = 0
            metrics['downstream_coverage_pct'] = 0

        return metrics

    def generate_inventory_table(self) -> str:
        """
        Generate markdown table of document inventory

        Returns:
            Markdown table string
        """
        if not self.documents:
            return "| No documents found |"

        table = f"| {self.doc_type} ID | Title | Category | Status | Date | Upstream Sources | Downstream Artifacts |\n"
        table += "|" + "---|" * 7 + "\n"

        for doc in self.documents:
            upstream = ", ".join(doc.upstream_sources[:3])  # Limit to first 3
            if len(doc.upstream_sources) > 3:
                upstream += f" (+{len(doc.upstream_sources) - 3} more)"

            downstream = ", ".join(doc.downstream_artifacts[:3])
            if len(doc.downstream_artifacts) > 3:
                downstream += f" (+{len(doc.downstream_artifacts) - 3} more)"

            table += f"| {doc.doc_id} | {doc.title or 'Untitled'} | {doc.category or 'N/A'} | {doc.status} | {doc.date or 'N/A'} | {upstream or 'None'} | {downstream or 'None'} |\n"

        return table

    def generate_mermaid_diagram(self) -> str:
        """
        Generate Mermaid dependency diagram

        Returns:
            Mermaid diagram string
        """
        # Limit to first 10 documents for readability
        limited_docs = self.documents[:10]

        diagram = "```mermaid\ngraph TD\n"

        # Add nodes
        for doc in limited_docs:
            clean_id = doc.doc_id.replace('-', '')
            title_short = doc.title[:30] if doc.title else 'Untitled'
            diagram += f"    {clean_id}[{doc.doc_id}: {title_short}]\n"

        # Add edges (upstream to current doc)
        for doc in limited_docs:
            clean_id = doc.doc_id.replace('-', '')
            for upstream in doc.upstream_sources:
                if upstream.startswith(self.doc_type):
                    clean_upstream = upstream.replace('-', '')
                    diagram += f"    {clean_upstream} --> {clean_id}\n"

        # Styling
        diagram += f"\n    style {limited_docs[0].doc_id.replace('-', '')} fill:#e8f5e9\n"

        diagram += "```\n"

        if len(self.documents) > 10:
            diagram += f"\n*Showing first 10 of {len(self.documents)} {self.doc_type} documents*\n"

        return diagram

    def generate_matrix(self, output_path: str):
        """
        Generate complete traceability matrix and write to file

        Args:
            output_path: Path where matrix file should be written
        """
        print(f"Generating traceability matrix: {output_path}")

        # Scan and extract metadata
        self.scan_documents()
        self.extract_all_metadata()

        # Calculate metrics
        metrics = self.calculate_coverage_metrics()

        # Build matrix content
        content = f"# Traceability Matrix: {self.doc_type}-001 through {self.doc_type}-NNN\n\n"
        content += "## Document Control\n\n"
        content += "| Item | Details |\n"
        content += "|------|---------|  \n"
        content += f"| Document ID | TRACEABILITY_MATRIX_{self.doc_type} |\n"
        content += f"| Title | Comprehensive {self.doc_type} Traceability Matrix |\n"
        content += "| Status | Active |\n"
        content += "| Version | 1.0.0 |\n"
        content += f"| Date Created | {datetime.now().strftime('%Y-%m-%d')} |\n"
        content += "| Author | Auto-generated |\n"
        content += f"| Purpose | Track bidirectional traceability for all {self.doc_type} documents |\n"
        content += "| Generator | generate_traceability_matrix.py |\n\n"

        content += "## 1. Overview\n\n"
        content += "### 1.1 Statistics\n\n"
        content += f"- **Total {self.doc_type} Tracked**: {metrics['total_documents']} documents\n"
        content += f"- **Upstream Coverage**: {metrics['upstream_coverage_pct']:.1f}% ({metrics['upstream_coverage']}/{metrics['total_documents']})\n"
        content += f"- **Downstream Coverage**: {metrics['downstream_coverage_pct']:.1f}% ({metrics['downstream_coverage']}/{metrics['total_documents']})\n"
        content += f"- **Orphaned Documents**: {len(metrics['orphaned_documents'])}\n"
        content += f"- **Last Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        content += "### 1.2 Status Breakdown\n\n"
        for status, count in sorted(metrics['status_breakdown'].items()):
            percentage = (count / metrics['total_documents']) * 100 if metrics['total_documents'] > 0 else 0
            content += f"- **{status}**: {count} documents ({percentage:.1f}%)\n"
        content += "\n"

        content += f"## 2. Complete {self.doc_type} Inventory\n\n"
        content += self.generate_inventory_table()
        content += "\n\n"

        content += "## 3. Dependency Visualization\n\n"
        content += self.generate_mermaid_diagram()
        content += "\n"

        if metrics['orphaned_documents']:
            content += "## 4. Gap Analysis\n\n"
            content += "### 4.1 Orphaned Documents (No Upstream Traceability)\n\n"
            for doc_id in metrics['orphaned_documents']:
                content += f"- {doc_id}: Missing upstream sources\n"
            content += "\n"

        content += "## 5. Coverage Metrics\n\n"
        content += "| Metric | Value | Target | Status |\n"
        content += "|--------|-------|--------|--------|\n"
        content += f"| Upstream Traceability | {metrics['upstream_coverage_pct']:.1f}% | 100% | {'✅' if metrics['upstream_coverage_pct'] >= 100 else '🟡' if metrics['upstream_coverage_pct'] >= 80 else '🔴'} |\n"
        content += f"| Downstream Artifacts | {metrics['downstream_coverage_pct']:.1f}% | 90% | {'✅' if metrics['downstream_coverage_pct'] >= 90 else '🟡' if metrics['downstream_coverage_pct'] >= 70 else '🔴'} |\n"
        content += f"| Orphaned Documents | {len(metrics['orphaned_documents'])} | 0 | {'✅' if len(metrics['orphaned_documents']) == 0 else '🔴'} |\n\n"

        content += "## 6. Validation Commands\n\n"
        content += "```bash\n"
        content += f"# Validate this matrix\n"
        content += f"python scripts/validate_traceability_matrix.py --matrix {output_path}\n\n"
        content += f"# Update incrementally\n"
        content += f"python scripts/update_traceability_matrix.py --matrix {output_path}\n"
        content += "```\n\n"

        content += "## 7. Revision History\n\n"
        content += "| Version | Date | Changes | Method |\n"
        content += "|---------|------|---------|--------|\n"
        content += f"| 1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | Initial auto-generated matrix | generate_traceability_matrix.py |\n\n"

        content += "---\n\n"
        content += "*This matrix was automatically generated. For template, see*\n"
        content += f"*`{self.doc_type}-00_TRACEABILITY_MATRIX-TEMPLATE.md`*\n"

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ Traceability matrix generated: {output_path}")
        print(f"📊 Statistics:")
        print(f"   - Total documents: {metrics['total_documents']}")
        print(f"   - Upstream coverage: {metrics['upstream_coverage_pct']:.1f}%")
        print(f"   - Downstream coverage: {metrics['downstream_coverage_pct']:.1f}%")
        print(f"   - Orphaned documents: {len(metrics['orphaned_documents'])}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate traceability matrix from document directory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate ADR matrix
  python generate_traceability_matrix.py --type ADR --input ../ADR/ --output TRACEABILITY_MATRIX_ADR.md

  # Generate REQ matrix from specific domain
  python generate_traceability_matrix.py --type REQ --input ../REQ/api/ --output api_matrix.md

  # Generate SPEC matrix
  python generate_traceability_matrix.py --type SPEC --input ../SPEC/ --output TRACEABILITY_MATRIX_SPEC.md
        """
    )

    parser.add_argument(
        '--type',
        required=True,
        choices=TraceabilityMatrixGenerator.SUPPORTED_TYPES,
        help='Document type to generate matrix for'
    )

    parser.add_argument(
        '--input',
        required=True,
        help='Input directory containing documents to scan'
    )

    parser.add_argument(
        '--output',
        required=True,
        help='Output file path for generated matrix'
    )

    parser.add_argument(
        '--template',
        help='Path to matrix template (optional)'
    )

    args = parser.parse_args()

    try:
        generator = TraceabilityMatrixGenerator(
            doc_type=args.type,
            input_dir=args.input,
            template_path=args.template
        )

        generator.generate_matrix(args.output)

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
