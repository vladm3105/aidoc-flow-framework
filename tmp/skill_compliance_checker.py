#!/usr/bin/env python3
"""
Skill Compliance Checker
Validates Claude skills against project standards:
- ID Naming Conventions
- Token Limits
- Path References
- Terminology Consistency
- Code Block Policy
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import json

# Approximate token counting (1 token ≈ 4 characters for English text)
def estimate_tokens(text: str) -> int:
    """Estimate token count (rough approximation)"""
    return len(text) // 4

# ID Naming patterns from ID_NAMING_STANDARDS.md
ID_PATTERNS = {
    'BRD': r'BRD-\d{3,4}(-\d{2,3})?',
    'PRD': r'PRD-\d{3,4}(-\d{2,3})?',
    'REQ': r'REQ-\d{3,4}(-\d{2,3})?',
    'ADR': r'ADR-\d{3,4}(-\d{2,3})?',
    'SPEC': r'SPEC-\d{3,4}(-\d{2,3})?',
    'CTR': r'CTR-\d{3,4}(-\d{2,3})?',
    'IMPL': r'IMPL-\d{3,4}(-\d{2,3})?',
    'TASKS': r'TASKS-\d{3,4}(-\d{2,3})?',
    'IPLAN': r'IPLAN-\d{3,4}',  # No sub-numbering for IPLAN
    'BDD': r'BDD-\d{3,4}(-\d{2,3})?',
    'EARS': r'EARS-\d{3,4}(-\d{2,3})?',
    'SYS': r'SYS-\d{3,4}(-\d{2,3})?',
}

# Deprecated terms
DEPRECATED_TERMS = {
    'docs_flow': 'ai_dev_flow',
    'TASKS_PLANS': 'IPLAN',
    'tasks_plans': 'iplan',
}

# Incorrect layer numbering (should be 0-15)
LAYER_PATTERN = r'Layer\s+(\d+)'

class ComplianceChecker:
    def __init__(self, skill_file: Path):
        self.skill_file = skill_file
        self.skill_name = skill_file.parent.name
        self.content = skill_file.read_text()
        self.lines = self.content.split('\n')
        self.issues = {
            'id_naming': [],
            'token_limit': [],
            'path_reference': [],
            'terminology': [],
            'code_block': [],
            'layer_numbering': [],
        }

    def check_all(self) -> Dict:
        """Run all compliance checks"""
        self.check_token_limit()
        self.check_id_naming()
        self.check_path_references()
        self.check_terminology()
        self.check_code_blocks()
        self.check_layer_numbering()
        return self.get_report()

    def check_token_limit(self):
        """Check if file exceeds token limits"""
        tokens = estimate_tokens(self.content)
        file_size_kb = len(self.content) / 1024

        if tokens > 100000:
            self.issues['token_limit'].append({
                'severity': 'CRITICAL',
                'line': None,
                'message': f'File exceeds 100K token maximum ({tokens:,} tokens, {file_size_kb:.1f}KB)'
            })
        elif tokens > 50000:
            self.issues['token_limit'].append({
                'severity': 'WARNING',
                'line': None,
                'message': f'File exceeds 50K token standard ({tokens:,} tokens, {file_size_kb:.1f}KB)'
            })

    def check_id_naming(self):
        """Check for ID naming convention issues"""
        # Look for incorrect ID patterns (e.g., XXX, NNN, YY placeholders)
        incorrect_patterns = [
            (r'\bXXX\b', 'Use actual numbers (001-999) not "XXX" placeholder'),
            (r'\bNNN\b', 'Use actual numbers (001-999) not "NNN" placeholder'),
            (r'\bYY\b', 'Use actual numbers (01-99) not "YY" placeholder'),
            (r'TYPE-XXX', 'Use proper ID format like REQ-001, not TYPE-XXX'),
            (r'TYPE-NNN', 'Use proper ID format like REQ-001, not TYPE-NNN'),
        ]

        for line_num, line in enumerate(self.lines, 1):
            for pattern, message in incorrect_patterns:
                if re.search(pattern, line) and 'example' not in line.lower() and 'pattern' not in line.lower():
                    self.issues['id_naming'].append({
                        'severity': 'ERROR',
                        'line': line_num,
                        'message': f'{message}: "{line.strip()[:80]}"'
                    })

    def check_path_references(self):
        """Check for incorrect path references"""
        # Common incorrect paths
        incorrect_paths = [
            (r'docs_flow/', 'Should use "ai_dev_flow/" not "docs_flow/"'),
            (r'docs/flow/', 'Should use "ai_dev_flow/" not "docs/flow/"'),
            (r'/docs/templates/', 'Templates are in ai_dev_flow/ not docs/templates/'),
        ]

        for line_num, line in enumerate(self.lines, 1):
            for pattern, message in incorrect_paths:
                if re.search(pattern, line, re.IGNORECASE):
                    self.issues['path_reference'].append({
                        'severity': 'ERROR',
                        'line': line_num,
                        'message': f'{message}: "{line.strip()[:80]}"'
                    })

    def check_terminology(self):
        """Check for deprecated terminology"""
        for line_num, line in enumerate(self.lines, 1):
            for old_term, new_term in DEPRECATED_TERMS.items():
                if old_term in line and 'deprecated' not in line.lower():
                    self.issues['terminology'].append({
                        'severity': 'WARNING',
                        'line': line_num,
                        'message': f'Use "{new_term}" instead of deprecated "{old_term}": "{line.strip()[:80]}"'
                    })

    def check_code_blocks(self):
        """Check Python code blocks for compliance with optional policy"""
        in_code_block = False
        code_block_start = 0
        code_block_lines = 0
        code_lang = None

        for line_num, line in enumerate(self.lines, 1):
            if line.strip().startswith('```'):
                if not in_code_block:
                    # Starting a code block
                    in_code_block = True
                    code_block_start = line_num
                    code_block_lines = 0
                    # Extract language
                    lang_match = re.match(r'```(\w+)', line.strip())
                    code_lang = lang_match.group(1) if lang_match else None
                else:
                    # Ending a code block
                    in_code_block = False

                    # Check if Python block exceeds 50 lines (optional policy)
                    if code_lang == 'python' and code_block_lines > 50:
                        self.issues['code_block'].append({
                            'severity': 'INFO',
                            'line': code_block_start,
                            'message': f'Python code block has {code_block_lines} lines (>50). Consider separate .py file per optional policy.'
                        })
            elif in_code_block:
                code_block_lines += 1

    def check_layer_numbering(self):
        """Check for correct layer numbering (0-15)"""
        for line_num, line in enumerate(self.lines, 1):
            matches = re.finditer(LAYER_PATTERN, line, re.IGNORECASE)
            for match in matches:
                layer_num = int(match.group(1))
                if layer_num > 15:
                    self.issues['layer_numbering'].append({
                        'severity': 'ERROR',
                        'line': line_num,
                        'message': f'Layer {layer_num} exceeds valid range (0-15): "{line.strip()[:80]}"'
                    })

    def get_report(self) -> Dict:
        """Generate compliance report"""
        total_issues = sum(len(issues) for issues in self.issues.values())
        critical_count = sum(1 for category in self.issues.values() for issue in category if issue['severity'] == 'CRITICAL')
        error_count = sum(1 for category in self.issues.values() for issue in category if issue['severity'] == 'ERROR')
        warning_count = sum(1 for category in self.issues.values() for issue in category if issue['severity'] == 'WARNING')

        # Determine overall status
        if critical_count > 0:
            status = 'FAIL (Critical)'
        elif error_count > 0:
            status = 'FAIL (Errors)'
        elif warning_count > 0:
            status = 'PASS (Warnings)'
        else:
            status = 'PASS'

        tokens = estimate_tokens(self.content)

        return {
            'skill_name': self.skill_name,
            'file_path': str(self.skill_file),
            'token_count': tokens,
            'file_size_kb': len(self.content) / 1024,
            'total_issues': total_issues,
            'critical_count': critical_count,
            'error_count': error_count,
            'warning_count': warning_count,
            'status': status,
            'issues': self.issues,
        }

def main():
    # Find all SKILL.md files
    skills_dir = Path('/opt/data/docs_flow_framework/.claude/skills')
    skill_files = list(skills_dir.glob('*/SKILL.md'))

    print(f"Found {len(skill_files)} skill files\n")

    all_reports = []

    for skill_file in sorted(skill_files):
        checker = ComplianceChecker(skill_file)
        report = checker.check_all()
        all_reports.append(report)

    # Save detailed report
    output_file = Path('/opt/data/docs_flow_framework/tmp/skill_compliance_report.json')
    with open(output_file, 'w') as f:
        json.dump(all_reports, f, indent=2)

    print(f"✓ Detailed report saved to: {output_file}\n")

    # Print summary
    print("=" * 80)
    print("SKILL COMPLIANCE SUMMARY")
    print("=" * 80)

    for report in all_reports:
        status_icon = "✓" if "PASS" in report['status'] else "✗"
        print(f"\n{status_icon} {report['skill_name']}")
        print(f"   Location: {report['file_path']}")
        print(f"   Token count: {report['token_count']:,} tokens ({report['file_size_kb']:.1f}KB)")
        print(f"   Status: {report['status']}")

        if report['total_issues'] > 0:
            print(f"   Issues: {report['critical_count']} critical, {report['error_count']} errors, {report['warning_count']} warnings")

            # Show critical and errors
            for category, issues in report['issues'].items():
                for issue in issues:
                    if issue['severity'] in ['CRITICAL', 'ERROR']:
                        line_info = f"Line {issue['line']}: " if issue['line'] else ""
                        print(f"      [{issue['severity']}] {line_info}{issue['message']}")

    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    total_skills = len(all_reports)
    passed = sum(1 for r in all_reports if 'PASS' in r['status'] and r['warning_count'] == 0)
    passed_warnings = sum(1 for r in all_reports if 'PASS' in r['status'] and r['warning_count'] > 0)
    failed = sum(1 for r in all_reports if 'FAIL' in r['status'])

    print(f"Total skills: {total_skills}")
    print(f"Passed (no issues): {passed}")
    print(f"Passed (warnings): {passed_warnings}")
    print(f"Failed: {failed}")

    total_issues = sum(r['total_issues'] for r in all_reports)
    total_critical = sum(r['critical_count'] for r in all_reports)
    total_errors = sum(r['error_count'] for r in all_reports)
    total_warnings = sum(r['warning_count'] for r in all_reports)

    print(f"\nTotal issues: {total_issues}")
    print(f"  Critical: {total_critical}")
    print(f"  Errors: {total_errors}")
    print(f"  Warnings: {total_warnings}")

if __name__ == '__main__':
    main()
