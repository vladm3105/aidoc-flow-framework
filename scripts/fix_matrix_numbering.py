#!/usr/bin/env python3
"""
Fix section numbering in traceability matrix templates.

Issue: Many matrices skip section 3 (jump from ## 2 to ## 4)
Fix: Renumber sections to be sequential (1, 2, 3, 4, 5...)
"""

import re
from pathlib import Path

def fix_matrix_numbering(file_path: Path) -> bool:
    """Fix section numbering in a matrix template file."""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Track if changes were made
    original_content = content

    # Pattern: ## N. (section headers)
    # We need to renumber them sequentially

    # First, find all section numbers
    section_pattern = r'^## (\d+)\.'
    sections = []
    for match in re.finditer(section_pattern, content, re.MULTILINE):
        sections.append((match.start(), match.group(1)))

    if not sections:
        print(f"  ⚠️  No sections found in {file_path.name}")
        return False

    # Check if numbering is already correct
    expected_nums = list(range(1, len(sections) + 1))
    actual_nums = [int(s[1]) for s in sections]

    if actual_nums == expected_nums:
        print(f"  ✓ {file_path.name} - Already correct")
        return False

    print(f"  🔧 {file_path.name}")
    print(f"     Current: {actual_nums}")
    print(f"     Fixed:   {expected_nums}")

    # Build mapping of old -> new numbers
    old_to_new = {}
    for i, (_, old_num) in enumerate(sections):
        new_num = i + 1
        old_to_new[int(old_num)] = new_num

    # Replace section headers (## N.)
    def replace_section(match):
        old_num = int(match.group(1))
        new_num = old_to_new.get(old_num, old_num)
        return f"## {new_num}."

    content = re.sub(section_pattern, replace_section, content, flags=re.MULTILINE)

    # Also fix subsection references (### N.M)
    # These should match the parent section number
    subsection_pattern = r'^### (\d+)\.(\d+)'

    def replace_subsection(match):
        old_section = int(match.group(1))
        sub_num = match.group(2)
        new_section = old_to_new.get(old_section, old_section)
        return f"### {new_section}.{sub_num}"

    content = re.sub(subsection_pattern, replace_subsection, content, flags=re.MULTILINE)

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

def main():
    """Fix all matrix templates."""

    base_dir = Path('/opt/data/docs_flow_framework/ai_dev_flow')

    # Find all traceability matrix templates
    matrix_files = list(base_dir.glob('*/*_TRACEABILITY_MATRIX-TEMPLATE.md'))

    print(f"Found {len(matrix_files)} matrix templates\n")

    fixed_count = 0
    skipped_count = 0

    for matrix_file in sorted(matrix_files):
        if fix_matrix_numbering(matrix_file):
            fixed_count += 1
        else:
            skipped_count += 1

    print(f"\n✅ Summary:")
    print(f"   Fixed: {fixed_count} files")
    print(f"   Already correct: {skipped_count} files")
    print(f"   Total: {len(matrix_files)} files")

if __name__ == '__main__':
    main()
