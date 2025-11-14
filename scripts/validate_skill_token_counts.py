#!/usr/bin/env python3
"""
Validate SKILL.md token counts against CLAUDE.md standards.

Token Count Standards (from CLAUDE.md):
- Claude Code (Primary): 50,000 tokens standard, 100,000 tokens maximum
- Warning: >50K tokens (review), >75K tokens (split recommended), >100K tokens (MUST split)

Formula: tokens ≈ words * 1.33

Exit Codes:
- 0: All files within standard limit (≤50K tokens)
- 1: Warning issues found (50K-75K tokens)
- 2: Critical issues found (>75K tokens)
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple


def count_words(file_path: Path) -> int:
    """Count words in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return len(content.split())


def estimate_tokens(word_count: int) -> int:
    """Estimate tokens from word count using 1.33 multiplier."""
    return int(word_count * 1.33)


def categorize_size(token_count: int) -> Tuple[str, str]:
    """
    Categorize token count and return status and emoji.

    Returns:
        Tuple of (status, emoji)
    """
    if token_count <= 50000:
        return ("✅ OK", "✅")
    elif token_count <= 75000:
        return ("⚠️  WARNING (review recommended)", "⚠️")
    elif token_count <= 100000:
        return ("⚠️  CRITICAL (split recommended)", "⚠️")
    else:
        return ("❌ MUST SPLIT (exceeds maximum)", "❌")


def format_number(num: int) -> str:
    """Format number with thousands separator."""
    return f"{num:,}"


def validate_skill_files(skills_dir: Path) -> Dict[str, dict]:
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
        word_count = count_words(skill_md)
        token_count = estimate_tokens(word_count)
        status, emoji = categorize_size(token_count)

        results[str(relative_path)] = {
            "word_count": word_count,
            "token_count": token_count,
            "status": status,
            "emoji": emoji,
            "file_size": skill_md.stat().st_size
        }

    return results


def print_report(results: Dict[str, dict]) -> int:
    """
    Print validation report and return exit code.

    Exit Codes:
        0: All files OK
        1: Warnings found
        2: Critical issues found
    """
    print("=" * 80)
    print("SKILL.md Token Count Validation Report")
    print("=" * 80)
    print()
    print("Standards:")
    print("  ✅ OK: ≤50,000 tokens (standard limit)")
    print("  ⚠️  WARNING: 50,001-75,000 tokens (review recommended)")
    print("  ⚠️  CRITICAL: 75,001-100,000 tokens (split recommended)")
    print("  ❌ MUST SPLIT: >100,000 tokens (exceeds maximum)")
    print()
    print("-" * 80)

    # Sort by token count (descending)
    sorted_results = sorted(
        results.items(),
        key=lambda x: x[1]["token_count"],
        reverse=True
    )

    has_warnings = False
    has_critical = False
    has_must_split = False

    for file_path, data in sorted_results:
        emoji = data["emoji"]
        words = format_number(data["word_count"])
        tokens = format_number(data["token_count"])
        status = data["status"]
        file_size_kb = data["file_size"] / 1024

        print(f"{emoji} {file_path}")
        print(f"   Words: {words} | Tokens: {tokens} | Size: {file_size_kb:.1f} KB")
        print(f"   Status: {status}")
        print()

        # Track severity
        if "MUST SPLIT" in status:
            has_must_split = True
        elif "CRITICAL" in status:
            has_critical = True
        elif "WARNING" in status:
            has_warnings = True

    print("-" * 80)
    print(f"Total files validated: {len(results)}")

    # Count by category
    ok_count = sum(1 for r in results.values() if r["token_count"] <= 50000)
    warn_count = sum(1 for r in results.values() if 50000 < r["token_count"] <= 75000)
    critical_count = sum(1 for r in results.values() if 75000 < r["token_count"] <= 100000)
    must_split_count = sum(1 for r in results.values() if r["token_count"] > 100000)

    print(f"  ✅ OK: {ok_count}")
    print(f"  ⚠️  WARNING: {warn_count}")
    print(f"  ⚠️  CRITICAL: {critical_count}")
    print(f"  ❌ MUST SPLIT: {must_split_count}")
    print()

    # Recommendations
    if has_must_split or has_critical:
        print("=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        print()
        for file_path, data in sorted_results:
            if data["token_count"] > 75000:
                print(f"📝 {file_path}")
                print(f"   Token count: {format_number(data['token_count'])}")
                print("   Actions:")
                print("   1. Extract large code blocks to separate example files")
                print("   2. Move detailed examples to skill-specific examples/ directory")
                print("   3. Replace inline code with references: [See Code Example: examples/file.py]")
                print("   4. Consider splitting into multiple focused skill files if still too large")
                print()

    print("=" * 80)

    # Determine exit code
    if has_must_split or has_critical:
        print("❌ FAILED: Critical issues found (token count >75K)")
        return 2
    elif has_warnings:
        print("⚠️  WARNING: Some files exceed standard limit (>50K tokens)")
        return 1
    else:
        print("✅ SUCCESS: All files within standard limit (≤50K tokens)")
        return 0


def main():
    """Main validation function."""
    # Detect skills directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    skills_dir = project_root / ".claude" / "skills"

    if not skills_dir.exists():
        print(f"❌ ERROR: Skills directory not found: {skills_dir}", file=sys.stderr)
        sys.exit(3)

    print(f"Scanning: {skills_dir}")
    print()

    # Validate all SKILL.md files
    results = validate_skill_files(skills_dir)

    if not results:
        print("❌ ERROR: No SKILL.md files found", file=sys.stderr)
        sys.exit(3)

    # Print report and exit with appropriate code
    exit_code = print_report(results)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
