#!/usr/bin/env python3
"""Generate comprehensive compliance report for Claude skills."""
import glob
import json
import sys
from pathlib import Path
from datetime import datetime

def analyze_skill(skill_file):
    """Analyze a single skill file for compliance."""
    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')

    word_count = len(content.split())
    token_estimate = word_count * 4  # Rough estimate (1 token ~= 0.75 words, conservative)

    # Check for version information
    has_version = any(
        re_match in content.lower()
        for re_match in ['version', '## document control', 'revision history']
    )

    # Check for document control section
    has_document_control = '## document control' in content.lower()

    # Count path references
    relative_paths = content.count('../../ai_dev_flow')
    project_root_refs = content.count('{project_root}')

    # Check for deprecated terminology
    deprecated_terms = 0
    if '12 documentation artifacts' in content:
        deprecated_terms += content.count('12 documentation artifacts')
    if '12-layer' in content and '12-layer' not in content.lower():  # Avoid false positives
        deprecated_terms += 1

    return {
        'file': str(skill_file),
        'name': Path(skill_file).parent.name,
        'word_count': word_count,
        'token_estimate': token_estimate,
        'has_version': has_version,
        'has_document_control': has_document_control,
        'relative_paths': relative_paths,
        'project_root_refs': project_root_refs,
        'deprecated_terms': deprecated_terms,
        'line_count': len(lines)
    }

def calculate_compliance_score(skill):
    """Calculate compliance score for a skill (0-100)."""
    score = 100

    # Token limit check (50K standard, 100K maximum)
    if skill['token_estimate'] > 100000:
        score -= 30  # Over maximum limit (critical)
    elif skill['token_estimate'] > 50000:
        score -= 10  # Over standard limit (warning)

    # Path reference check
    if skill['relative_paths'] > 0:
        score -= 20  # Has relative paths (major issue)

    # Terminology check
    if skill['deprecated_terms'] > 0:
        score -= 15  # Has deprecated terminology (major issue)

    # Documentation completeness (minor factors)
    if not skill['has_version']:
        score -= 5  # Missing version info (minor)

    # Bonus for using best practices
    if skill['has_document_control']:
        score = min(100, score + 5)  # Has document control (bonus)

    return max(0, score)  # Ensure score doesn't go negative

def generate_report():
    """Generate full compliance report."""
    skills = []
    skills_dir = '.claude/skills/'

    print("="*80)
    print("CLAUDE SKILLS COMPREHENSIVE COMPLIANCE REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}")
    print("="*80)
    print()

    # Analyze all skills
    for skill_file in sorted(glob.glob(f'{skills_dir}*/SKILL.md')):
        skill_data = analyze_skill(skill_file)
        skill_data['compliance_score'] = calculate_compliance_score(skill_data)
        skills.append(skill_data)

    if not skills:
        print("❌ No skills found in .claude/skills/ directory")
        return False

    # Calculate aggregate statistics
    total_score = sum(s['compliance_score'] for s in skills)
    avg_score = total_score / len(skills)
    total_tokens = sum(s['token_estimate'] for s in skills)
    avg_tokens = total_tokens / len(skills)

    # Count issues
    skills_with_issues = sum(1 for s in skills if s['compliance_score'] < 100)
    skills_with_path_issues = sum(1 for s in skills if s['relative_paths'] > 0)
    skills_with_term_issues = sum(1 for s in skills if s['deprecated_terms'] > 0)
    skills_over_limit = sum(1 for s in skills if s['token_estimate'] > 50000)

    # Print summary
    print("EXECUTIVE SUMMARY")
    print("-" * 80)
    print(f"Total Skills Analyzed: {len(skills)}")
    print(f"Average Compliance Score: {avg_score:.1f}/100")
    print(f"Skills Fully Compliant: {len(skills) - skills_with_issues}/{len(skills)} ({((len(skills) - skills_with_issues) / len(skills) * 100):.1f}%)")
    print(f"Average Token Count: {avg_tokens:,.0f}")
    print(f"Total Token Count: {total_tokens:,.0f}")
    print()

    # Print issue summary
    print("ISSUES SUMMARY")
    print("-" * 80)
    print(f"Skills with path issues: {skills_with_path_issues}")
    print(f"Skills with terminology issues: {skills_with_term_issues}")
    print(f"Skills over token limit (50K): {skills_over_limit}")
    print()

    # Print detailed scores
    print("DETAILED COMPLIANCE SCORES")
    print("-" * 80)
    print(f"{'Skill Name':<25} {'Score':<8} {'Tokens':<10} {'Paths':<8} {'Terms':<8} {'Doc Ctrl'}")
    print("-" * 80)

    for skill in sorted(skills, key=lambda x: x['compliance_score']):
        status = "✓" if skill['compliance_score'] >= 95 else "⚠" if skill['compliance_score'] >= 85 else "❌"
        doc_ctrl = "Yes" if skill['has_document_control'] else "No"
        print(
            f"{status} {skill['name']:<23} "
            f"{skill['compliance_score']:>3}/100  "
            f"{skill['token_estimate']:>8,}  "
            f"{skill['relative_paths']:>7}  "
            f"{skill['deprecated_terms']:>7}  "
            f"{doc_ctrl}"
        )

    print()
    print("="*80)

    # Determine pass/fail status
    if avg_score >= 90 and skills_with_path_issues == 0 and skills_with_term_issues == 0:
        print("STATUS: ✓ PASS - All skills meet compliance standards")
        status = "PASS"
    elif avg_score >= 85:
        print("STATUS: ⚠ WARNING - Minor compliance issues found")
        status = "WARNING"
    else:
        print("STATUS: ❌ FAIL - Significant compliance issues require remediation")
        status = "FAIL"

    print("="*80)
    print()

    # Save JSON report
    report_data = {
        'generated': datetime.now().isoformat(),
        'total_skills': len(skills),
        'average_score': round(avg_score, 2),
        'status': status,
        'summary': {
            'fully_compliant': len(skills) - skills_with_issues,
            'path_issues': skills_with_path_issues,
            'terminology_issues': skills_with_term_issues,
            'over_token_limit': skills_over_limit,
            'total_tokens': total_tokens,
            'average_tokens': round(avg_tokens, 0)
        },
        'skills': skills
    }

    report_path = 'tmp/skills_compliance_report.json'
    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2)

    print(f"Detailed JSON report saved to: {report_path}")
    print()

    return status == "PASS"

if __name__ == '__main__':
    import re  # Import here for use in analyze_skill
    success = generate_report()
    sys.exit(0 if success else 1)
