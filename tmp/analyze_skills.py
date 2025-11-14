#!/usr/bin/env python3
"""Analyze Claude skills for compliance issues."""
import os
import re
from pathlib import Path

def analyze_skill(skill_path):
    """Analyze a single skill file."""
    skill_name = skill_path.parent.name
    print(f"\n{'='*70}")
    print(f"=== Analyzing {skill_name} ===")
    print('='*70)

    if not skill_path.exists():
        print(f"ERROR: {skill_path} not found")
        return None

    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')

    # Path References
    print("\n--- Path References ---")
    path_refs = []
    for i, line in enumerate(lines, 1):
        if '../../' in line or '{project_root}' in line:
            path_refs.append((i, line.strip()))

    if path_refs:
        for line_num, line in path_refs[:10]:
            print(f"{line_num}: {line[:100]}")
    else:
        print("No relative or project_root paths found")

    # Terminology
    print("\n--- Terminology ---")
    term_pattern = r'(layer|artifact|12.*artifact|16.*layer|11 functional|15 artifact)'
    term_refs = []
    for i, line in enumerate(lines, 1):
        if re.search(term_pattern, line, re.IGNORECASE):
            term_refs.append((i, line.strip()))

    if term_refs:
        for line_num, line in term_refs[:8]:
            print(f"{line_num}: {line[:100]}")
    else:
        print("No layer/artifact terminology")

    # Token Count
    print("\n--- Token Count ---")
    word_count = len(content.split())
    token_estimate = word_count * 4  # Rough estimate
    print(f"{word_count} words (~{token_estimate:,} tokens)")

    # Document Control
    print("\n--- Document Control ---")
    doc_control = False
    for i, line in enumerate(lines, 1):
        if re.match(r'^##\s+Document Control|^###\s+Version|^###\s+Revision History', line):
            print(f"{i}: {line.strip()}")
            doc_control = True

    if not doc_control:
        print("No Document Control section")

    return {
        'name': skill_name,
        'path_refs': len([r for r in path_refs if '../../' in r[1]]),
        'project_root_refs': len([r for r in path_refs if '{project_root}' in r[1]]),
        'term_refs': len(term_refs),
        'word_count': word_count,
        'token_estimate': token_estimate,
        'has_doc_control': doc_control
    }

def main():
    """Analyze all remaining skills."""
    skills_dir = Path('/opt/data/docs_flow_framework/.claude/skills')

    # Skills to analyze (excluding already analyzed: trace-check, adr-roadmap, project-init, project-mngt)
    skills_to_analyze = [
        'doc-flow', 'analytics-flow', 'charts_flow', 'code-review',
        'contract-tester', 'devops-flow', 'doc-validator', 'google-adk',
        'mermaid-gen', 'n8n', 'refactor-flow', 'security-audit', 'test-automation'
    ]

    results = []
    for skill_name in skills_to_analyze:
        skill_path = skills_dir / skill_name / 'SKILL.md'
        result = analyze_skill(skill_path)
        if result:
            results.append(result)

    # Summary
    print("\n" + "="*70)
    print("=== SUMMARY ===")
    print("="*70)
    print(f"\nTotal skills analyzed: {len(results)}")
    print(f"Skills with relative paths (../../): {sum(1 for r in results if r['path_refs'] > 0)}")
    print(f"Skills with {'{project_root}'} refs: {sum(1 for r in results if r['project_root_refs'] > 0)}")
    print(f"Skills with terminology refs: {sum(1 for r in results if r['term_refs'] > 0)}")
    print(f"Skills with Document Control: {sum(1 for r in results if r['has_doc_control'])}")
    print(f"Average token count: {sum(r['token_estimate'] for r in results) / len(results):,.0f}")
    print(f"Max token count: {max(r['token_estimate'] for r in results):,} ({max(results, key=lambda x: x['token_estimate'])['name']})")

    # Detailed results table
    print("\n" + "="*70)
    print("Skill Name           | Rel Paths | proj_root | Terms | Tokens  | Doc Ctrl")
    print("-"*70)
    for r in results:
        print(f"{r['name']:20} | {r['path_refs']:9} | {r['project_root_refs']:9} | {r['term_refs']:5} | {r['token_estimate']:7,} | {'Yes' if r['has_doc_control'] else 'No'}")

if __name__ == '__main__':
    main()
