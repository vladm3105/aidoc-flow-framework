#!/usr/bin/env python3
"""Validate terminology consistency in Claude skills."""
import re
import glob
import sys
from pathlib import Path

# Deprecated terms that should not appear
DEPRECATED_TERMS = [
    (r'12 documentation artifacts', '11 functional layers (15 artifact types)'),
    (r'12-layer(?! artifact)', '16-layer (or "11 functional layers")'),
]

# Canonical terms (for reference)
CANONICAL_TERMS = [
    '11 functional layers',
    '15 artifact types',
    '16 layers',  # When referring to Layer 0 + Layers 1-15
    '12 artifact directories',  # This is correct - refers to docs/ subdirectories
]

def validate_terminology():
    """Validate terminology consistency across skills."""
    issues = []
    skills_dir = '.claude/skills/'

    print("="*80)
    print("CLAUDE SKILLS TERMINOLOGY VALIDATION")
    print("="*80)
    print()

    for skill_file in sorted(glob.glob(f'{skills_dir}*/SKILL.md')):
        skill_name = Path(skill_file).parent.name
        skill_issues = []

        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        # Check for deprecated terms
        for pattern, replacement in DEPRECATED_TERMS:
            for i, line in enumerate(lines, 1):
                # Skip if it's part of a changelog/revision history
                if re.search(r'revision|history|changelog|deprecated', line, re.IGNORECASE):
                    continue

                if re.search(pattern, line, re.IGNORECASE):
                    skill_issues.append(
                        f"  Line {i}: Found '{pattern}' - should use '{replacement}'\n"
                        f"    Context: {line.strip()[:80]}"
                    )

        if skill_issues:
            issues.append(f"\n❌ {skill_name}:")
            issues.extend(skill_issues)
        else:
            # Check for canonical term usage (informational)
            canonical_count = sum(1 for term in CANONICAL_TERMS if term in content)
            if canonical_count > 0:
                print(f"✓ {skill_name}: Uses {canonical_count} canonical term(s)")
            else:
                print(f"○ {skill_name}: No framework terminology")

    if issues:
        print("\n" + "="*80)
        print("❌ TERMINOLOGY VALIDATION FAILED")
        print("="*80)
        for issue in issues:
            print(issue)
        print("\nAction required: Replace deprecated terminology with canonical terms")
        print("="*80)
        return False
    else:
        print("\n" + "="*80)
        print("✓ ALL TERMINOLOGY CONSISTENT")
        print("="*80)
        print("\nCanonical terms (for reference):")
        for term in CANONICAL_TERMS:
            print(f"  • {term}")
        print("="*80)
        return True

if __name__ == '__main__':
    success = validate_terminology()
    sys.exit(0 if success else 1)
