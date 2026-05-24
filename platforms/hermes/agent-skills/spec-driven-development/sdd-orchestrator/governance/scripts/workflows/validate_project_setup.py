#!/usr/bin/env python3
"""
Validate Project Setup and Configuration

Validates project has required configuration:
- Required secrets exist (ANTHROPIC_API_KEY, etc.)
- Branch protection on main
- CLAUDE.md configuration is valid

Usage:
    python validate_project_setup.py --repo owner/repo

Environment:
    GH_TOKEN: GitHub token with repo admin access

References:
    - work_plans/ai_governance_automation.md (Item #13)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime


def run_gh(args: list[str], check: bool = True) -> str:
    """Run gh CLI command and return output."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
        check=check,
        env={**os.environ, "GH_TOKEN": os.environ.get("GH_TOKEN", "")},
    )
    return result.stdout.strip()


def check_required_secrets(repo: str) -> list[str]:
    """Check if required secrets are configured."""
    warnings = []

    # Note: We can't actually verify secrets exist via API for security reasons
    # This checks if they're referenced in workflows

    required_secrets = [
        "ANTHROPIC_API_KEY",
        "GITHUB_TOKEN",  # This is always available
    ]

    optional_secrets = [
        "ELEVATED_PAT",
        "TEAMS_WEBHOOK",
    ]

    # Check workflow files for secret references
    workflow_dir = ".github/workflows"
    if not os.path.exists(workflow_dir):
        warnings.append("No .github/workflows directory found")
        return warnings

    referenced_secrets = set()
    for filename in os.listdir(workflow_dir):
        if filename.endswith((".yml", ".yaml")):
            filepath = os.path.join(workflow_dir, filename)
            with open(filepath) as f:
                content = f.read()
            for match in re.finditer(r"\$\{\{\s*secrets\.([A-Z_]+)\s*\}\}", content):
                referenced_secrets.add(match.group(1))

    for secret in required_secrets:
        if secret != "GITHUB_TOKEN" and secret not in referenced_secrets:
            warnings.append(
                f"Required secret {secret} not referenced in any workflow. "
                f"Ensure it is configured in repository settings."
            )

    return warnings


def check_branch_protection(repo: str) -> list[str]:
    """Check branch protection on main."""
    warnings = []

    try:
        output = run_gh(["api", f"/repos/{repo}/branches/main/protection"], check=False)

        if not output or "Not Found" in output:
            warnings.append(
                "Branch protection not configured on 'main'. "
                "Consider enabling required reviews and status checks."
            )
            return warnings

        protection = json.loads(output)

        # Check required reviews
        if not protection.get("required_pull_request_reviews"):
            warnings.append("Branch protection: Required pull request reviews not enabled")

        # Check required status checks
        if not protection.get("required_status_checks"):
            warnings.append("Branch protection: Required status checks not enabled")

    except (subprocess.CalledProcessError, json.JSONDecodeError):
        warnings.append("Unable to check branch protection (may require admin access)")

    return warnings


def check_claude_md() -> list[str]:
    """Validate CLAUDE.md configuration."""
    warnings = []

    claude_md_paths = ["CLAUDE.md", "governance/templates/CLAUDE.md"]
    claude_md_content = None

    for path in claude_md_paths:
        if os.path.exists(path):
            with open(path) as f:
                claude_md_content = f.read()
            break

    if not claude_md_content:
        warnings.append("No CLAUDE.md file found")
        return warnings

    # Check for required placeholders
    required_placeholders = [
        "{PROJECT_NAME}",
        "{GITHUB_ORG}",
        "{REPO_NAME}",
    ]

    # If this is the template, placeholders should exist
    if "templates" in str(claude_md_paths):
        for placeholder in required_placeholders:
            if placeholder not in claude_md_content:
                warnings.append(f"CLAUDE.md template missing placeholder: {placeholder}")
    else:
        # If this is an instantiated file, placeholders should be replaced
        for placeholder in required_placeholders:
            if placeholder in claude_md_content:
                warnings.append(f"CLAUDE.md has unreplaced placeholder: {placeholder}")

    # Check for required sections
    required_sections = [
        "## Session Start Protocol",
        "## AI Operating Rules",
        "## GitHub Workflow",
    ]

    for section in required_sections:
        if section not in claude_md_content:
            warnings.append(f"CLAUDE.md missing required section: {section}")

    return warnings


def check_mcp_config() -> list[str]:
    """Validate .mcp.json configuration."""
    warnings = []

    if not os.path.exists(".mcp.json"):
        warnings.append("No .mcp.json file found")
        return warnings

    try:
        with open(".mcp.json") as f:
            mcp_config = json.load(f)

        # Check for required MCP servers
        servers = mcp_config.get("mcpServers", {})

        recommended_servers = ["filesystem", "git"]
        for server in recommended_servers:
            if not any(server in s.lower() for s in servers.keys()):
                warnings.append(f"Recommended MCP server not configured: {server}")

    except json.JSONDecodeError as e:
        warnings.append(f".mcp.json is not valid JSON: {e}")

    return warnings


def generate_report(all_warnings: list[str]) -> str:
    """Generate validation report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "## Project Setup Validation Report",
        "",
        f"**Generated**: {timestamp}",
        f"**Status**: {'PASS' if not all_warnings else 'WARNINGS'}",
        f"**Issues Found**: {len(all_warnings)}",
        "",
    ]

    if all_warnings:
        lines.extend(
            [
                "### Issues",
                "",
            ]
        )
        for warning in all_warnings:
            lines.append(f"- {warning}")
        lines.append("")

        lines.extend(
            [
                "### Recommended Actions",
                "",
                "1. Review and address warnings above",
                "2. Configure missing secrets in repository settings",
                "3. Enable branch protection rules",
                "4. Update CLAUDE.md with project-specific values",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "Project setup validated successfully.",
                "",
            ]
        )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Validate project setup")
    parser.add_argument("--repo", required=True, help="Repository (owner/repo)")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on warnings")
    args = parser.parse_args()

    all_warnings = []

    # Run all validations
    all_warnings.extend(check_required_secrets(args.repo))
    all_warnings.extend(check_branch_protection(args.repo))
    all_warnings.extend(check_claude_md())
    all_warnings.extend(check_mcp_config())

    # Generate report
    report = generate_report(all_warnings)
    print(report)

    # Exit code
    if args.strict and all_warnings:
        sys.exit(1)


if __name__ == "__main__":
    main()
