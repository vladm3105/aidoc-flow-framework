#!/usr/bin/env python3
"""Validate path references in Claude skills."""
import re
import glob
import sys
from pathlib import Path

def validate_paths():
    """Validate all path references in skill files."""
    issues = []
    skills_dir = '.claude/skills/'

    print("="*80)
    print("CLAUDE SKILLS PATH VALIDATION")
    print("="*80)
    print()

    for skill_file in sorted(glob.glob(f'{skills_dir}*/SKILL.md')):
        skill_name = Path(skill_file).parent.name

        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        # Check for relative paths (../../)
        relative_paths = []
        for i, line in enumerate(lines, 1):
            if '../../' in line and 'ai_dev_flow' in line:
                relative_paths.append(f"  Line {i}: {line.strip()[:80]}")

        if relative_paths:
            issues.append(f"\n❌ {skill_name}:")
            issues.extend(relative_paths)
        else:
            # Check if it uses {project_root}
            if '{project_root}' in content:
                print(f"✓ {skill_name}: Uses {'{project_root}'} placeholder")
            else:
                print(f"○ {skill_name}: No path references")

    if issues:
        print("\n" + "="*80)
        print("❌ PATH VALIDATION FAILED")
        print("="*80)
        for issue in issues:
            print(issue)
        print("\nAction required: Replace relative paths (../../) with {project_root}/")
        print("="*80)
        return False
    else:
        print("\n" + "="*80)
        print("✓ ALL PATH REFERENCES VALID")
        print("="*80)
        return True

if __name__ == '__main__':
    success = validate_paths()
    sys.exit(0 if success else 1)
