#!/usr/bin/env python3
"""
Script to update template section headers to use "N. Title" format.
Version 2: More comprehensive update.
"""
import re
import os
from pathlib import Path

# Sections that should NOT be numbered (special sections)
SKIP_SECTIONS = [
    '## Document Control',  # Usually at the beginning, special section
    '## Document Control Notes',
    '## Document Revision History',
]

# Special document handling patterns
# For Traceability Matrix templates, Appendix A should become a numbered section

def update_section_headers_v2(content: str, filepath: str) -> str:
    """Update section headers to use N. Title format."""
    lines = content.split('\n')
    result = []

    main_section_num = 0
    sub_section_nums = {}

    # Skip frontmatter
    in_frontmatter = False
    frontmatter_count = 0

    for i, line in enumerate(lines):
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

        # Skip lines that already have numbers
        if re.match(r'^##+ \d+\.', line):
            # Extract the current section number for tracking
            match = re.match(r'^## (\d+)\.', line)
            if match:
                main_section_num = int(match.group(1))
                sub_section_nums[main_section_num] = 0
            match = re.match(r'^### (\d+)\.(\d+)', line)
            if match:
                main_num = int(match.group(1))
                sub_num = int(match.group(2))
                if main_num in sub_section_nums:
                    sub_section_nums[main_num] = max(sub_section_nums[main_num], sub_num)
            result.append(line)
            continue

        # Check for ## header without number
        match = re.match(r'^(##) ([A-Z].*?)$', line)
        if match:
            section_title = match.group(2)
            full_header = f"## {section_title}"

            # Skip special sections
            if full_header in SKIP_SECTIONS:
                result.append(line)
                continue

            main_section_num += 1
            sub_section_nums[main_section_num] = 0
            new_line = f"## {main_section_num}. {section_title}"
            result.append(new_line)
            continue

        # Check for ### header without number
        match = re.match(r'^(###) ([A-Z].*?)$', line)
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
        original = content

        # Check if has unnumbered sections (except skip sections)
        has_unnumbered = False
        for line in content.split('\n'):
            if re.match(r'^## [A-Z]', line) and not re.match(r'^## \d+\.', line):
                # Check if it's a skip section
                if not any(line.startswith(skip) for skip in SKIP_SECTIONS):
                    has_unnumbered = True
                    break

        if not has_unnumbered:
            print(f"  Skipping (no unnumbered sections): {filepath.name}")
            return False

        new_content = update_section_headers_v2(content, str(filepath))

        if new_content != original:
            filepath.write_text(new_content, encoding='utf-8')
            print(f"  Updated: {filepath.name}")
            return True
        else:
            print(f"  No changes: {filepath.name}")
            return False

    except Exception as e:
        print(f"  Error processing {filepath.name}: {e}")
        import traceback
        traceback.print_exc()
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
