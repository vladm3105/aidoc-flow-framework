#!/usr/bin/env python3
"""
Validate all markdown links in Section 7 Traceability sections.
Check that:
1. Relative paths resolve to actual files
2. Anchors exist in target files
3. No broken references
"""

import re
from pathlib import Path
from collections import defaultdict


def extract_section_7(content):
    """Extract Section 7 content."""
    pattern = r'## 7\. Traceability.*?(?=\n## |\Z)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    return match.group(0) if match else None


def extract_markdown_links(text):
    """Extract all markdown links from text."""
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    return re.findall(pattern, text)


def validate_link(source_file, link_text, link_path):
    """Validate a single link."""
    issues = []

    # Skip external URLs
    if link_path.startswith('http://') or link_path.startswith('https://'):
        return []

    # Skip mailto links
    if link_path.startswith('mailto:'):
        return []

    # Skip anchor-only links (same document)
    if link_path.startswith('#'):
        return []

    source_dir = source_file.parent

    # Split path and anchor
    if '#' in link_path:
        file_part, anchor_part = link_path.split('#', 1)
    else:
        file_part, anchor_part = link_path, None

    # Resolve relative path
    try:
        if file_part:
            target_path = (source_dir / file_part).resolve()

            # Check file exists
            if not target_path.exists():
                issues.append({
                    'type': 'broken_file',
                    'source': str(source_file),
                    'link_text': link_text,
                    'link_path': link_path,
                    'message': f"File not found: {target_path}"
                })
                return issues

            # If anchor specified, check it exists in target
            if anchor_part:
                try:
                    with open(target_path, 'r', encoding='utf-8') as f:
                        target_content = f.read()

                    # Check for various anchor formats
                    anchor_found = False

                    # Format 1: # ANCHOR (markdown header)
                    if f'#{anchor_part}' in target_content:
                        anchor_found = True

                    # Format 2: {#anchor} (pandoc style)
                    elif f'{{#{anchor_part}}}' in target_content:
                        anchor_found = True

                    # Format 3: <a name="anchor"></a>
                    elif f'<a name="{anchor_part}"' in target_content or f"<a name='{anchor_part}'" in target_content:
                        anchor_found = True

                    # Format 4: id="anchor" (YAML/frontmatter)
                    elif f'id: {anchor_part}' in target_content:
                        anchor_found = True

                    # Format 5: id="anchor" (HTML attribute in span/div tags)
                    elif f'id="{anchor_part}"' in target_content or f"id='{anchor_part}'" in target_content:
                        anchor_found = True

                    # Format 6: Generated from header (convert header to anchor)
                    # Headers like "## BRD-001" become #brd-001
                    header_pattern = f'#+ {anchor_part.replace("-", "[- ]")}'
                    if re.search(header_pattern, target_content, re.IGNORECASE):
                        anchor_found = True

                    if not anchor_found:
                        issues.append({
                            'type': 'broken_anchor',
                            'source': str(source_file),
                            'link_text': link_text,
                            'link_path': link_path,
                            'target': str(target_path),
                            'anchor': anchor_part,
                            'message': f"Anchor not found: #{anchor_part}"
                        })

                except Exception as e:
                    issues.append({
                        'type': 'read_error',
                        'source': str(source_file),
                        'link_path': link_path,
                        'message': f"Could not read target file: {e}"
                    })

    except Exception as e:
        issues.append({
            'type': 'path_error',
            'source': str(source_file),
            'link_path': link_path,
            'message': f"Path resolution error: {e}"
        })

    return issues


def check_for_placeholders(text):
    """Find TBD and placeholder references."""
    placeholders = []

    patterns = [
        (r'\[TBD\]', 'TBD'),
        (r'\(TBD\)', 'TBD'),
        (r'\(planned\)', 'Planned'),
        (r'\(to be created\)', 'To be created'),
        (r'\(coming soon\)', 'Coming soon'),
    ]

    for pattern, placeholder_type in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            placeholders.append({
                'type': placeholder_type,
                'text': match.group(0),
                'position': match.start()
            })

    return placeholders


def validate_file(file_path):
    """Validate all links in a file's Section 7."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'error': f"Could not read file: {e}"}, []

    section_7 = extract_section_7(content)

    if not section_7:
        return {}, []  # No Section 7

    # Extract links
    links = extract_markdown_links(section_7)

    # Validate each link
    all_issues = []
    for link_text, link_path in links:
        issues = validate_link(file_path, link_text, link_path)
        all_issues.extend(issues)

    # Check for placeholders
    placeholders = check_for_placeholders(section_7)

    return {
        'file': str(file_path),
        'links_found': len(links),
        'issues': all_issues,
        'placeholders': placeholders
    }, all_issues


def generate_report(results, docs_dir):
    """Generate validation report."""
    total_files = len(results)
    files_with_issues = sum(1 for r in results if r.get('issues'))
    total_issues = sum(len(r.get('issues', [])) for r in results)
    total_placeholders = sum(len(r.get('placeholders', [])) for r in results)

    print("\n" + "=" * 80)
    print("LINK VALIDATION REPORT")
    print("=" * 80)
    print(f"\nFiles scanned: {total_files}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Total link issues: {total_issues}")
    print(f"Total placeholders: {total_placeholders}")

    # Group issues by type
    issue_by_type = defaultdict(int)
    for result in results:
        for issue in result.get('issues', []):
            issue_by_type[issue['type']] += 1

    if issue_by_type:
        print("\n--- Issues by Type ---")
        for issue_type, count in sorted(issue_by_type.items()):
            print(f"  {issue_type}: {count}")

    # Show detailed issues
    if total_issues > 0:
        print("\n--- Detailed Issues ---")
        for result in results:
            if result.get('issues'):
                print(f"\n{result['file']}:")
                for issue in result['issues']:
                    print(f"  [{issue['type']}] {issue['message']}")
                    if 'link_path' in issue:
                        print(f"    Link: {issue['link_path']}")

    # Show placeholders
    if total_placeholders > 0:
        print("\n--- Files with Placeholders ---")
        for result in results:
            if result.get('placeholders'):
                print(f"{result['file']}: {len(result['placeholders'])} placeholders")

    return {
        'total_files': total_files,
        'files_with_issues': files_with_issues,
        'total_issues': total_issues,
        'total_placeholders': total_placeholders,
        'issue_by_type': dict(issue_by_type)
    }


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Validate links in Section 7')
    parser.add_argument('--docs-dir', default='/opt/data/ibmcp/docs', help='Documentation directory')
    parser.add_argument('--json', action='store_true', help='Output JSON format')

    args = parser.parse_args()
    docs_dir = Path(args.docs_dir)

    results = []
    all_issues = []

    for md_file in sorted(docs_dir.rglob('*.md')):
        result, issues = validate_file(md_file)
        if result:
            results.append(result)
            all_issues.extend(issues)

    if args.json:
        print(json.dumps({
            'results': results,
            'summary': {
                'total_files': len(results),
                'total_issues': len(all_issues)
            }
        }, indent=2))
    else:
        generate_report(results, docs_dir)


if __name__ == '__main__':
    main()
