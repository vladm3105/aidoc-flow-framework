#!/usr/bin/env python3
"""
Script to update template section headers to use "N. Title" format.
"""
import re
import os
from pathlib import Path

def update_section_headers(content: str) -> str:
    """Update section headers to use N. Title format."""
    lines = content.split('\n')
    result = []

    main_section_num = 0
    sub_section_nums = {}

    # Skip frontmatter
    in_frontmatter = False
    frontmatter_count = 0

    for line in lines:
        # Handle YAML frontmatter
        if line.strip() == '---':
            frontmatter_count += 1
            if frontmatter_count == 1:
                in_frontmatter = True
            elif frontmatter_count == 2:
                in_frontmatter = False
            result.append(line)
            continue

        if in_frontmatter:
            result.append(line)
            continue

        # Check for ## header without number
        match = re.match(r'^(##) ([A-Z][^0-9].*?)$', line)
        if match:
            main_section_num += 1
            sub_section_nums[main_section_num] = 0
            new_line = f"## {main_section_num}. {match.group(2)}"
            result.append(new_line)
            continue

        # Check for ### header without number
        match = re.match(r'^(###) ([A-Z][^0-9].*?)$', line)
        if match and main_section_num > 0:
            sub_section_nums[main_section_num] += 1
            sub_num = sub_section_nums[main_section_num]
            new_line = f"### {main_section_num}.{sub_num} {match.group(2)}"
            result.append(new_line)
            continue

        result.append(line)

    return '\n'.join(result)


def process_file(filepath: Path) -> bool:
    """Process a single file. Returns True if modified."""
    try:
        content = filepath.read_text(encoding='utf-8')

        # Check if already has numbered sections
        if re.search(r'^## \d+\.', content, re.MULTILINE):
            print(f"  Skipping (already numbered): {filepath.name}")
            return False

        # Check if has unnumbered sections to update
        if not re.search(r'^## [A-Z][^0-9]', content, re.MULTILINE):
            print(f"  Skipping (no sections to update): {filepath.name}")
            return False

        new_content = update_section_headers(content)

        if new_content != content:
            filepath.write_text(new_content, encoding='utf-8')
            print(f"  Updated: {filepath.name}")
            return True
        else:
            print(f"  No changes: {filepath.name}")
            return False

    except Exception as e:
        print(f"  Error processing {filepath.name}: {e}")
        return False


def main():
    base_path = Path('/opt/data/docs_flow_framework/ai_dev_flow')

    # Find all template files
    template_files = list(base_path.glob('**/*TEMPLATE*.md'))

    print(f"Found {len(template_files)} template files")
    print("=" * 50)

    updated = 0
    for filepath in sorted(template_files):
        if process_file(filepath):
            updated += 1

    print("=" * 50)
    print(f"Updated {updated} files")


if __name__ == '__main__':
    main()
