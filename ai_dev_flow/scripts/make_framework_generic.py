#!/usr/bin/env python3
"""
Make AI Dev Flow Framework Project-Agnostic

This script transforms the AI Dev Flow framework from trading-specific to generic
by replacing domain-specific references with [UPPERCASE_BRACKET] placeholders.

Usage:
    python scripts/make_framework_generic.py

Features:
    - Processes all .md and .yaml files in docs_templates/ai_dev_flow/
    - Replaces trading-specific terminology with generic placeholders
    - Preserves file structure and formatting
    - Creates backup before modification
    - Generates transformation report
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import shutil
from datetime import datetime

# Trading-specific terms and their generic replacements
REPLACEMENTS = {
    # Trading strategies
    r'\bportfolio orchestrator agent\b': '[ORCHESTRATION_COMPONENT]',
    r'\bportfolio orchestrator\b': '[ORCHESTRATION_COMPONENT]',
    r'\biron condor\b': '[STRATEGY_NAME - e.g., multi-step workflow, approval process]',
    r'\bcovered call\b': '[STRATEGY_NAME]',
    r'\bcovered put\b': '[STRATEGY_NAME]',
    r'\bcash-secured put\b': '[STRATEGY_NAME]',
    r'\bbear call spread\b': '[STRATEGY_NAME]',

    # Trading entities
    r'\bInteractive Brokers\b': '[EXTERNAL_SERVICE - e.g., Payment Gateway, CRM System]',
    r'\bIB Gateway\b': '[EXTERNAL_SERVICE_GATEWAY]',
    r'\bAlpha Vantage\b': '[EXTERNAL_DATA_PROVIDER - e.g., Weather API, Stock Data API]',
    r'\bmarket data\b': '[EXTERNAL_DATA - e.g., customer data, sensor readings]',
    r'\bmarket analysis\b': '[DATA_ANALYSIS - e.g., user behavior analysis, trend detection]',

    # Trading actions
    r'\btrade execution\b': '[OPERATION_EXECUTION - e.g., order processing, task execution]',
    r'\bposition limit\b': '[RESOURCE_LIMIT - e.g., request quota, concurrent sessions]',
    r'\bcircuit breaker\b': '[SAFETY_MECHANISM - e.g., rate limiter, error threshold]',
    r'\brisk management\b': '[RESOURCE_MANAGEMENT - e.g., capacity planning, quota management]',
    r'\brisk budget\b': '[RESOURCE_BUDGET]',

    # Greeks and financial metrics
    r'\bgreeks\b': '[METRICS - e.g., performance indicators, quality scores]',
    r'\bdelta\b(?! hedging)': '[METRIC_1 - e.g., error rate, response time]',
    r'\bdelta hedging\b': '[ADJUSTMENT_STRATEGY]',
    r'\bgamma\b': '[METRIC_2 - e.g., throughput, success rate]',
    r'\btheta\b': '[METRIC_3]',
    r'\bvega\b': '[METRIC_4]',
    r'\bVIX\b': '[VOLATILITY_INDICATOR - e.g., system load, error frequency]',

    # Financial terms
    r'\bportfolio\b': '[RESOURCE_COLLECTION - e.g., user accounts, active sessions]',
    r'\bposition\b(?! active)': '[RESOURCE_INSTANCE - e.g., database connection, workflow instance]',
    r'\bpremium\b': '[VALUE - e.g., subscription fee, processing cost]',
    r'\bstrike price\b': '[THRESHOLD_VALUE]',
    r'\bexpiration\b': '[DEADLINE - e.g., session timeout, cache expiry]',
    r'\bDTE\b': '[TIME_REMAINING - e.g., days until deadline, TTL]',
    r'\bassignment\b': '[ALLOCATION - e.g., task assignment, resource allocation]',
    r'\bbroker\b': '[EXTERNAL_INTEGRATION - e.g., third-party API, service provider]',

    # Market/trading states
    r'\bmarket scanning\b': '[DISCOVERY_MODE - e.g., resource scanning, opportunity search]',
    r'\bmarket regime\b': '[SYSTEM_STATE - e.g., operating mode, environment condition]',
    r'\bbullish\b': '[POSITIVE_CONDITION - e.g., high capacity, favorable state]',
    r'\bbearish\b': '[NEGATIVE_CONDITION - e.g., low capacity, degraded state]',
    r'\bneutral\b': '[NORMAL_CONDITION - e.g., steady state, balanced load]',
    r'\bvolatile\b': '[UNSTABLE_CONDITION - e.g., fluctuating load, variable demand]',

    # Trading platform specific
    r'\btrading platform\b': '[APPLICATION_TYPE - e.g., e-commerce platform, SaaS application]',
    r'\btrading system\b': '[SYSTEM_TYPE - e.g., inventory system, booking system]',
    r'\btrading strategy\b': '[BUSINESS_LOGIC - e.g., pricing algorithm, routing strategy]',
    r'\boptions trading\b': '[DOMAIN_ACTIVITY - e.g., payment processing, content moderation]',
    r'\bmulti-agent trading\b': '[MULTI_COMPONENT_SYSTEM - e.g., microservices architecture]',

    # Compliance
    r'\bSEC compliance\b': '[REGULATORY_COMPLIANCE - e.g., GDPR, HIPAA, SOC2]',
    r'\bFINRA\b': '[REGULATORY_BODY - e.g., FDA, FTC]',
    r'\bSOX\b': '[COMPLIANCE_STANDARD - e.g., PCI-DSS, ISO27001]',

    # Stock/ticker symbols
    r'\b[A-Z]{1,5}\s+stock\b': '[ENTITY_IDENTIFIER - e.g., customer ID, product SKU]',
    r'\bticker\b': '[IDENTIFIER - e.g., user handle, product code]',

    # Preserve these patterns (don't replace)
    # r'\[.*?\]': lambda m: m.group(0),  # Already in placeholder format
}

# Domain-specific folder names to genericize
DOMAIN_FOLDERS = {
    'risk': '[DOMAIN - e.g., auth, core, billing, analytics]',
    'ml': '[DOMAIN]',
    'api': '[DOMAIN]',
}

class FrameworkTransformer:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.backup_path = self.base_path.parent / f"ai_dev_flow_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.stats = {
            'files_processed': 0,
            'files_modified': 0,
            'replacements_made': 0,
            'errors': []
        }

    def create_backup(self):
        """Create backup of entire framework before modification"""
        print(f"Creating backup at: {self.backup_path}")
        shutil.copytree(self.base_path, self.backup_path)
        print("✓ Backup created")

    def transform_text(self, text: str) -> Tuple[str, int]:
        """Apply all replacements to text, return (transformed_text, replacement_count)"""
        replacement_count = 0
        result = text

        for pattern, replacement in REPLACEMENTS.items():
            matches = re.finditer(pattern, result, re.IGNORECASE)
            count = len(list(matches))
            if count > 0:
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
                replacement_count += count

        return result, replacement_count

    def process_file(self, file_path: Path) -> bool:
        """Process a single file, return True if modified"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            transformed_content, replacement_count = self.transform_text(original_content)

            if replacement_count > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(transformed_content)

                self.stats['files_modified'] += 1
                self.stats['replacements_made'] += replacement_count
                print(f"  ✓ {file_path.relative_to(self.base_path)}: {replacement_count} replacements")
                return True
            else:
                print(f"  - {file_path.relative_to(self.base_path)}: No changes needed")
                return False

        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            self.stats['errors'].append(error_msg)
            print(f"  ✗ {error_msg}")
            return False

    def process_directory(self, directory: Path):
        """Recursively process all .md and .yaml files in directory"""
        for item in directory.rglob('*'):
            if item.is_file() and item.suffix in ['.md', '.yaml', '.yml']:
                # Skip archived folders
                if 'archived' in str(item):
                    continue

                # Skip example files we just created
                if any(x in item.name for x in ['example', 'EXAMPLE']):
                    continue

                self.stats['files_processed'] += 1
                self.process_file(item)

    def generate_report(self):
        """Generate transformation report"""
        report = f"""
================================================================================
AI Dev Flow Framework Transformation Report
================================================================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Backup Location: {self.backup_path}

Summary:
--------
Files Processed: {self.stats['files_processed']}
Files Modified: {self.stats['files_modified']}
Total Replacements: {self.stats['replacements_made']}
Errors: {len(self.stats['errors'])}

"""
        if self.stats['errors']:
            report += "\nErrors Encountered:\n"
            for error in self.stats['errors']:
                report += f"  - {error}\n"

        report += "\n" + "="*80 + "\n"

        # Write report to file
        report_path = self.base_path / 'TRANSFORMATION_REPORT.txt'
        with open(report_path, 'w') as f:
            f.write(report)

        print(report)
        print(f"\nReport saved to: {report_path}")

    def run(self):
        """Main execution flow"""
        print("\n" + "="*80)
        print("AI Dev Flow Framework - Make Generic Transformation")
        print("="*80 + "\n")

        # Create backup
        self.create_backup()

        # Process all directories
        print("\nProcessing files...")
        print("-" * 80)

        directories = [
            'REQ', 'IMPL', 'CONTRACTS', 'SPEC', 'BDD',
            'ADR', 'PRD', 'BRD', 'EARS', 'SYS', 'TASKS'
        ]

        for dir_name in directories:
            dir_path = self.base_path / dir_name
            if dir_path.exists():
                print(f"\nProcessing {dir_name}/...")
                self.process_directory(dir_path)

        # Process root README files
        print(f"\nProcessing root documentation...")
        root_files = [
            'README.md',
            'TRACEABILITY.md',
            'ID_NAMING_STANDARDS.md',
            'SPEC_DRIVEN_DEVELOPMENT_GUIDE.md',
            'WHEN_TO_CREATE_IMPL.md',
            'index.md'
        ]

        for filename in root_files:
            file_path = self.base_path / filename
            if file_path.exists():
                self.stats['files_processed'] += 1
                self.process_file(file_path)

        # Generate report
        print("\n" + "-" * 80)
        self.generate_report()

        print("\n✓ Transformation complete!")
        print(f"  Original files backed up to: {self.backup_path}")
        print(f"  Modified {self.stats['files_modified']} files")
        print(f"  Made {self.stats['replacements_made']} replacements")

if __name__ == "__main__":
    # Get the base path (parent of scripts directory)
    script_dir = Path(__file__).parent
    base_path = script_dir.parent

    # Run transformation
    transformer = FrameworkTransformer(base_path)
    transformer.run()
