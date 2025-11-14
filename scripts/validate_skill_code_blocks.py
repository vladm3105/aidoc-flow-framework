#!/usr/bin/env python3
"""
Validate inline code block sizes in SKILL.md files against CLAUDE.md standards.

Code Block Policy (from CLAUDE.md):
- Small examples (<50 lines): Inline Python code blocks acceptable
- Large implementations (>50 lines): Create separate .py files
- Reference format: [See Code Example: filename.py - function_name()]

Exit Codes:
- 0: All code blocks comply with standards (≤50 lines)
- 1: Warning issues found (code blocks >50 lines)
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def extract_code_blocks(content: str) -> List[Tuple[int, int, str, str]]:
    """
    Extract all code blocks from markdown content.

    Returns:
        List of tuples: (start_line, line_count, language, snippet)
    """
    blocks = []
    lines = content.split('\n')
    in_block = False
    block_start = 0
    block_lines = []
    block_lang = ""

    for i, line in enumerate(lines, start=1):
        if line.strip().startswith('```'):
            if not in_block:
                # Start of code block
                in_block = True
                block_start = i
                block_lines = []
                # Extract language identifier
                lang_match = re.match(r'```(\w+)?', line.strip())
                block_lang = lang_match.group(1) if lang_match and lang_match.group(1) else "unknown"
            else:
                # End of code block
                in_block = False
                line_count = len(block_lines)
                snippet = '\n'.join(block_lines[:5])  # First 5 lines for preview
                if len(block_lines) > 5:
                    snippet += "\n..."
                blocks.append((block_start, line_count, block_lang, snippet))
        elif in_block:
            block_lines.append(line)

    return blocks


def suggest_filename(language: str, block_index: int, skill_name: str) -> str:
    """Suggest a filename for extracted code block."""
    lang_extensions = {
        "python": "py",
        "py": "py",
        "typescript": "ts",
        "ts": "ts",
        "javascript": "js",
        "js": "js",
        "yaml": "yaml",
        "yml": "yaml",
        "json": "json",
        "bash": "sh",
        "shell": "sh",
        "unknown": "txt"
    }

    ext = lang_extensions.get(language.lower(), "txt")
    return f"{skill_name}_example_{block_index:02d}.{ext}"


def validate_skill_file(skill_md: Path) -> Dict:
    """
    Validate code blocks in a single SKILL.md file.

    Returns:
        Dict with validation results
    """
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    code_blocks = extract_code_blocks(content)

    # Extract skill name from path
    skill_name = skill_md.parent.name

    violations = []
    for start_line, line_count, language, snippet in code_blocks:
        if line_count > 50:
            suggested_file = suggest_filename(language, len(violations) + 1, skill_name)
            violations.append({
                "start_line": start_line,
                "line_count": line_count,
                "language": language,
                "snippet": snippet,
                "suggested_file": suggested_file
            })

    return {
        "total_blocks": len(code_blocks),
        "violations": violations,
        "compliant_blocks": len(code_blocks) - len(violations)
    }


def validate_all_skills(skills_dir: Path) -> Dict[str, dict]:
    """
    Validate all SKILL.md files in the skills directory.

    Returns:
        Dict mapping file path to validation results
    """
    results = {}

    for skill_md in skills_dir.rglob("SKILL.md"):
        # Skip backup directories
        if "backup" in str(skill_md).lower():
            continue

        relative_path = skill_md.relative_to(skills_dir.parent)
        results[str(relative_path)] = validate_skill_file(skill_md)

    return results


def print_report(results: Dict[str, dict]) -> int:
    """
    Print validation report and return exit code.

    Exit Codes:
        0: All files compliant
        1: Violations found
    """
    print("=" * 80)
    print("SKILL.md Code Block Size Validation Report")
    print("=" * 80)
    print()
    print("Standards:")
    print("  ✅ Compliant: Code blocks ≤50 lines (inline acceptable)")
    print("  ❌ Violation: Code blocks >50 lines (must extract to separate file)")
    print()
    print("Policy:")
    print("  - Small examples (<50 lines): Inline code blocks acceptable")
    print("  - Large implementations (>50 lines): Create separate .py files")
    print("  - Use reference format: [See Code Example: examples/filename.py - function()]")
    print()
    print("-" * 80)

    has_violations = False
    total_violations = 0
    total_blocks = 0

    for file_path, data in sorted(results.items()):
        violations = data["violations"]
        total = data["total_blocks"]
        compliant = data["compliant_blocks"]

        total_blocks += total
        total_violations += len(violations)

        if violations:
            has_violations = True
            print(f"❌ {file_path}")
            print(f"   Total code blocks: {total}")
            print(f"   Compliant: {compliant} | Violations: {len(violations)}")
            print()

            for i, violation in enumerate(violations, start=1):
                start_line = violation["start_line"]
                line_count = violation["line_count"]
                language = violation["language"]
                suggested = violation["suggested_file"]
                snippet = violation["snippet"]

                print(f"   Violation #{i}:")
                print(f"     Line: {start_line}")
                print(f"     Size: {line_count} lines (exceeds 50 line limit)")
                print(f"     Language: {language}")
                print(f"     Suggested file: examples/{suggested}")
                print(f"     Preview:")
                for line in snippet.split('\n'):
                    print(f"       {line}")
                print()
        else:
            print(f"✅ {file_path}")
            print(f"   Total code blocks: {total} | All compliant (≤50 lines)")
            print()

    print("-" * 80)
    print(f"Total files validated: {len(results)}")
    print(f"Total code blocks: {total_blocks}")
    print(f"Compliant blocks: {total_blocks - total_violations}")
    print(f"Violations: {total_violations}")
    print()

    if has_violations:
        print("=" * 80)
        print("RECOMMENDED ACTIONS")
        print("=" * 80)
        print()
        print("For each violation:")
        print("1. Extract code block to examples/ subdirectory (skill-specific)")
        print("2. Replace inline block with reference:")
        print("   [See Code Example: examples/filename.py - function_name()]")
        print("3. Add complexity rating (1-5) in documentation")
        print("4. Create examples/README.md if not exists")
        print()
        print("Example directory structure:")
        print("  .claude/skills/")
        print("    google-adk/")
        print("      SKILL.md")
        print("      examples/")
        print("        google_adk_agent_implementation.py")
        print("        google_adk_tools_example.py")
        print("        README.md")
        print()
        print("=" * 80)
        print("❌ FAILED: Code blocks exceeding 50 lines found")
        return 1
    else:
        print("=" * 80)
        print("✅ SUCCESS: All code blocks within 50 line limit")
        return 0


def main():
    """Main validation function."""
    # Detect skills directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    skills_dir = project_root / ".claude" / "skills"

    if not skills_dir.exists():
        print(f"❌ ERROR: Skills directory not found: {skills_dir}", file=sys.stderr)
        sys.exit(2)

    print(f"Scanning: {skills_dir}")
    print()

    # Validate all SKILL.md files
    results = validate_all_skills(skills_dir)

    if not results:
        print("❌ ERROR: No SKILL.md files found", file=sys.stderr)
        sys.exit(2)

    # Print report and exit with appropriate code
    exit_code = print_report(results)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
