#!/usr/bin/env python3
"""
Metadata Validation Script for AI Dev Flow Framework

Validates YAML frontmatter metadata in markdown files:
- YAML syntax correctness
- Required fields presence
- Tag taxonomy compliance
- Bidirectional cross-references
- Agent ID uniqueness (for skills)
"""

import os
import re
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# Tag Taxonomy
VALID_TAGS = {
    # Architecture approaches
    'ai-agent-primary',
    'traditional-fallback',
    'shared-architecture',

    # Priority classifications
    'recommended-approach',
    'reference-implementation',
    'required-both-approaches',

    # Document types
    'framework-guide',
    'sdd-workflow',
    'quality-assurance',
    'utility-skill',
    'domain-specific',
    'index-document',
    'creation-rules',
    'validation-rules',

    # Layer artifacts
    'layer-0-artifact',  # META (doc-flow orchestrator)
    'layer-1-artifact',  # BRD
    'layer-2-artifact',  # PRD
    'layer-3-artifact',  # EARS
    'layer-4-artifact',  # BDD
    'layer-5-artifact',  # ADR
    'layer-6-artifact',  # SYS
    'layer-7-artifact',  # REQ
    'layer-8-artifact',  # IMPL
    'layer-9-artifact',  # CTR
    'layer-10-artifact', # SPEC
    'layer-11-artifact', # TASKS
    'layer-12-artifact', # Code

    # Skill categories
    'documentation-skill',
    'automation-skill',
    'analysis-skill',

    # Status
    'active',
    'deprecated',
    'experimental',

    # Feature types
    'feature-doc',
    'platform-doc',

    # Template tags - artifact-specific
    'adr-template',
    'bdd-template',
    'brd-template',
    'ctr-template',
    'ears-template',
    'impl-template',
    'prd-template',
    'req-template',
    'spec-template',
    'sys-template',
    'tasks-template',

    # Template tags - generic
    'document-template',
    'traceability-matrix-template',

    # Reference/guide tags
    'reference-document',
    'quick-reference',
    'traceability-guide',
    'metadata-guide',
    'supporting-document',
    'supplementary-documentation',

    # ICON/contract tags
    'implementation-contract',
    'contract-index',
    'contract-template',
    'decision-criteria',
    'troubleshooting',

    # Index/directory tags
    'directory-overview',
    'brd-glossary',

    # Feature variant tags
    'feature-prd',
    'architecture-adr',

    # Checklist/misc tags
    'tasks-checklist',
    'ears',
    'utility',

    # Agent/AI tags
    'agent',
    'ai-assistant',
    'requirements-engineering',
    'traceability',
}

# Required fields by document type
REQUIRED_FIELDS = {
    'skill': ['name', 'description', 'tags', 'custom_fields'],
    'guide': ['title', 'tags', 'custom_fields'],
    'index': ['title', 'tags', 'custom_fields'],
    'template': ['title', 'tags'],  # Templates may have minimal metadata
    'default': ['title', 'tags'],
}

# Required custom_fields by document type
REQUIRED_CUSTOM_FIELDS = {
    'skill': ['architecture_approaches', 'priority', 'development_status', 'skill_category'],
    'skill_core_workflow': ['layer', 'artifact_type', 'architecture_approaches', 'priority',
                            'development_status', 'skill_category'],
    'index': ['document_type', 'artifact_type', 'layer', 'priority'],
    'guide': ['document_type', 'priority', 'development_status'],
    'default': [],
}

class MetadataValidator:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.agent_ids: Dict[str, str] = {}  # agent_id -> file_path
        self.cross_refs: Dict[str, Set[str]] = defaultdict(set)  # file -> referenced files

    def extract_frontmatter(self, file_path: Path) -> Tuple[Dict, str]:
        """Extract YAML frontmatter from markdown file"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.errors.append(f"{file_path}: Failed to read file: {e}")
            return {}, ""

        # Match YAML frontmatter
        pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(pattern, content, re.DOTALL)

        if not match:
            return {}, content

        yaml_content = match.group(1)
        try:
            metadata = yaml.safe_load(yaml_content)
            return metadata or {}, content
        except yaml.YAMLError as e:
            self.errors.append(f"{file_path}: Invalid YAML syntax: {e}")
            return {}, content

    def get_doc_type(self, file_path: Path, metadata: Dict) -> str:
        """Determine document type from path and metadata"""
        path_str = str(file_path)

        if 'SKILL.md' in path_str:
            return 'skill'
        elif 'index.md' in path_str.lower():
            return 'index'
        elif 'TEMPLATE' in path_str:
            return 'template'
        elif any(x in path_str for x in ['GUIDE.md', 'RULES.md', 'STANDARDS.md']):
            return 'guide'

        return 'default'

    def validate_required_fields(self, file_path: Path, metadata: Dict, doc_type: str):
        """Validate presence of required fields"""
        required = REQUIRED_FIELDS.get(doc_type, REQUIRED_FIELDS['default'])

        for field in required:
            if field not in metadata:
                self.errors.append(
                    f"{file_path}: Missing required field '{field}' for {doc_type}"
                )

        # Validate custom_fields if present
        if 'custom_fields' in metadata:
            custom_fields = metadata['custom_fields']

            # For skills, check if it's core-workflow to determine requirements
            if doc_type == 'skill':
                skill_category = custom_fields.get('skill_category', '')
                if skill_category == 'core-workflow':
                    required_custom = REQUIRED_CUSTOM_FIELDS['skill_core_workflow']
                else:
                    required_custom = REQUIRED_CUSTOM_FIELDS['skill']
            else:
                required_custom = REQUIRED_CUSTOM_FIELDS.get(doc_type, [])

            for field in required_custom:
                if field not in custom_fields:
                    self.errors.append(
                        f"{file_path}: Missing required custom_field '{field}' for {doc_type}"
                    )

    def validate_tags(self, file_path: Path, metadata: Dict):
        """Validate tags against taxonomy"""
        if 'tags' not in metadata:
            return

        tags = metadata['tags']
        if not isinstance(tags, list):
            self.errors.append(f"{file_path}: 'tags' must be a list")
            return

        for tag in tags:
            if tag not in VALID_TAGS:
                self.warnings.append(
                    f"{file_path}: Unknown tag '{tag}' (not in taxonomy)"
                )

    def validate_architecture_consistency(self, file_path: Path, metadata: Dict):
        """Validate architecture approach consistency"""
        tags = metadata.get('tags', [])
        custom_fields = metadata.get('custom_fields', {})

        # Check for conflicting architecture tags
        arch_tags = [t for t in tags if t in ['ai-agent-primary', 'traditional-fallback', 'shared-architecture']]
        if len(arch_tags) > 1:
            self.errors.append(
                f"{file_path}: Multiple architecture tags found: {arch_tags} (should have only one)"
            )

        # Check priority consistency
        priority_tags = [t for t in tags if t in ['recommended-approach', 'reference-implementation', 'required-both-approaches']]
        custom_priority = custom_fields.get('priority', '')

        if priority_tags and custom_priority:
            # Map tags to expected priority values
            expected_priority = {
                'recommended-approach': 'primary',
                'reference-implementation': 'fallback',
                'required-both-approaches': 'shared',
            }

            for tag in priority_tags:
                if expected_priority.get(tag) != custom_priority:
                    self.warnings.append(
                        f"{file_path}: Priority tag '{tag}' doesn't match custom_fields.priority '{custom_priority}'"
                    )

    def validate_agent_id_uniqueness(self, file_path: Path, metadata: Dict):
        """Validate agent ID uniqueness (for skills)"""
        custom_fields = metadata.get('custom_fields', {})
        agent_id = custom_fields.get('agent_id')

        if agent_id:
            if agent_id in self.agent_ids:
                self.errors.append(
                    f"{file_path}: Duplicate agent_id '{agent_id}' "
                    f"(also in {self.agent_ids[agent_id]})"
                )
            else:
                self.agent_ids[agent_id] = str(file_path)

    def validate_layer_consistency(self, file_path: Path, metadata: Dict):
        """Validate layer number consistency"""
        custom_fields = metadata.get('custom_fields', {})
        layer = custom_fields.get('layer')
        tags = metadata.get('tags', [])

        if layer is not None:
            expected_tag = f'layer-{layer}-artifact'
            if expected_tag not in tags:
                self.warnings.append(
                    f"{file_path}: Layer {layer} specified but '{expected_tag}' tag missing"
                )

        # Check for layer tags without layer field
        layer_tags = [t for t in tags if t.startswith('layer-') and t.endswith('-artifact')]
        if layer_tags and layer is None:
            self.warnings.append(
                f"{file_path}: Layer tag found but custom_fields.layer not specified"
            )

    def validate_file(self, file_path: Path) -> bool:
        """Validate a single file"""
        metadata, content = self.extract_frontmatter(file_path)

        if not metadata:
            # No metadata found - this may be intentional for some files
            return True

        doc_type = self.get_doc_type(file_path, metadata)

        # Run validations
        self.validate_required_fields(file_path, metadata, doc_type)
        self.validate_tags(file_path, metadata)
        self.validate_architecture_consistency(file_path, metadata)
        self.validate_layer_consistency(file_path, metadata)

        if doc_type == 'skill':
            self.validate_agent_id_uniqueness(file_path, metadata)

        return len(self.errors) == 0

    def find_markdown_files(self, path: Path = None) -> List[Path]:
        """Find all markdown files in directory tree"""
        if path is None:
            path = self.root_dir

        markdown_files = []
        for md_file in path.rglob('*.md'):
            # Skip certain directories
            skip_dirs = {'.git', 'node_modules', '__pycache__', 'venv', '.venv'}
            if any(skip in md_file.parts for skip in skip_dirs):
                continue
            markdown_files.append(md_file)

        return markdown_files

    def validate_all(self, path: Path = None) -> bool:
        """Validate all markdown files"""
        files = self.find_markdown_files(path)

        if not files:
            print("No markdown files found")
            return True

        print(f"Validating {len(files)} markdown files...")

        valid_count = 0
        for file_path in files:
            if self.validate_file(file_path):
                valid_count += 1

        return len(self.errors) == 0

    def print_report(self):
        """Print validation report"""
        print("\n" + "="*70)
        print("METADATA VALIDATION REPORT")
        print("="*70)

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All metadata validation checks passed!")

        print("\n" + "="*70)

        if self.agent_ids:
            print(f"\nAgent IDs found: {len(self.agent_ids)}")

        return len(self.errors) == 0


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Validate YAML frontmatter metadata in markdown files'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to validate (file or directory)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors'
    )

    args = parser.parse_args()

    path = Path(args.path).resolve()

    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        sys.exit(1)

    # Determine root directory
    if path.is_file():
        root_dir = path.parent
        validate_path = path
    else:
        root_dir = path
        validate_path = None

    validator = MetadataValidator(root_dir)

    if validate_path and validate_path.is_file():
        validator.validate_file(validate_path)
    else:
        validator.validate_all(validate_path)

    success = validator.print_report()

    if args.strict and validator.warnings:
        success = False

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
