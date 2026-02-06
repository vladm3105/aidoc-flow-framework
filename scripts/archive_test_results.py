#!/usr/bin/env python3
"""
Archive and manage test results for AI Dev Flow.

Provides functionality to:
- Save test results with metadata
- Maintain rolling history (configurable retention)
- Tag results with git information
- Generate trend reports
- Set/update baseline files

Usage:
    python scripts/archive_test_results.py --save results.json
    python scripts/archive_test_results.py --set-baseline results.json
    python scripts/archive_test_results.py --prune --keep 10
    python scripts/archive_test_results.py --trend
    python scripts/archive_test_results.py --list

Reference: ai_dev_flow/10_TSPEC/test_result_schema.yaml
"""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RESULTS_DIR = PROJECT_ROOT / "tests" / "results"
ARCHIVE_DIR = RESULTS_DIR / "archive"

# Default retention
DEFAULT_KEEP = 10


def get_git_info() -> Dict[str, str]:
    """Get current git commit and branch information."""
    info = {
        "git_commit": "",
        "git_branch": "",
        "git_tag": "",
        "git_dirty": False,
    }

    try:
        # Get commit SHA
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode == 0:
            info["git_commit"] = result.stdout.strip()

        # Get branch name
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode == 0:
            info["git_branch"] = result.stdout.strip()

        # Get tag if on a tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--exact-match"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode == 0:
            info["git_tag"] = result.stdout.strip()

        # Check if working directory is dirty
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode == 0:
            info["git_dirty"] = bool(result.stdout.strip())

    except FileNotFoundError:
        pass

    return info


def archive_results(
    results_path: Path,
    test_type: Optional[str] = None,
    tag: Optional[str] = None,
) -> Path:
    """
    Archive test results with metadata.

    Args:
        results_path: Path to results JSON file
        test_type: Test type (utest, itest, stest, ftest)
        tag: Optional tag for this archive

    Returns:
        Path to archived file
    """
    if not results_path.exists():
        raise FileNotFoundError(f"Results file not found: {results_path}")

    # Load results
    results = json.loads(results_path.read_text())

    # Add archive metadata
    archive_meta = {
        "archived_at": datetime.now().isoformat(),
        "original_file": str(results_path),
        "tag": tag,
    }
    archive_meta.update(get_git_info())

    results["archive_metadata"] = archive_meta

    # Determine test type from results or filename
    if not test_type:
        test_type = results.get("test_type", "all").lower()

    # Create archive directory
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # Generate archive filename
    run_id = results.get("run_id", datetime.now().strftime("%Y%m%d_%H%M%S"))
    commit_short = archive_meta["git_commit"][:7] if archive_meta["git_commit"] else "unknown"
    archive_name = f"{test_type}_{run_id}_{commit_short}.json"

    if tag:
        archive_name = f"{test_type}_{run_id}_{tag}.json"

    archive_path = ARCHIVE_DIR / archive_name

    # Save archived results
    archive_path.write_text(json.dumps(results, indent=2))
    print(f"Archived: {archive_path}")

    return archive_path


def set_baseline(results_path: Path, test_type: Optional[str] = None) -> Path:
    """
    Set results file as the baseline for comparison.

    Args:
        results_path: Path to results JSON file
        test_type: Test type (utest, itest, stest, ftest)

    Returns:
        Path to baseline file
    """
    if not results_path.exists():
        raise FileNotFoundError(f"Results file not found: {results_path}")

    # Load results to get test type
    results = json.loads(results_path.read_text())
    if not test_type:
        test_type = results.get("test_type", "all").lower()

    # Create baseline file
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    baseline_path = RESULTS_DIR / f"baseline_{test_type}.json"

    shutil.copy(results_path, baseline_path)
    print(f"Baseline set: {baseline_path}")

    return baseline_path


def prune_archives(keep: int = DEFAULT_KEEP, test_type: Optional[str] = None) -> int:
    """
    Prune old archive files, keeping the most recent N.

    Args:
        keep: Number of archives to keep per test type
        test_type: Optional test type filter

    Returns:
        Number of files removed
    """
    if not ARCHIVE_DIR.exists():
        return 0

    removed = 0

    # Group files by test type
    files_by_type: Dict[str, List[Path]] = {}

    for file in ARCHIVE_DIR.glob("*.json"):
        # Extract test type from filename (first part before underscore)
        ftype = file.stem.split("_")[0]
        if test_type and ftype != test_type:
            continue

        if ftype not in files_by_type:
            files_by_type[ftype] = []
        files_by_type[ftype].append(file)

    # Prune each type
    for ftype, files in files_by_type.items():
        # Sort by modification time, newest first
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        # Remove old files
        for file in files[keep:]:
            file.unlink()
            removed += 1
            print(f"Removed: {file.name}")

    return removed


def list_archives(test_type: Optional[str] = None) -> List[Dict]:
    """
    List archived result files.

    Args:
        test_type: Optional test type filter

    Returns:
        List of archive metadata
    """
    if not ARCHIVE_DIR.exists():
        return []

    archives = []

    for file in sorted(ARCHIVE_DIR.glob("*.json"), key=lambda p: -p.stat().st_mtime):
        # Filter by test type if specified
        ftype = file.stem.split("_")[0]
        if test_type and ftype != test_type:
            continue

        try:
            data = json.loads(file.read_text())
            summary = data.get("summary", {})
            archive_meta = data.get("archive_metadata", {})

            archives.append(
                {
                    "file": file.name,
                    "test_type": ftype,
                    "run_id": data.get("run_id", ""),
                    "total": summary.get("total", 0),
                    "passed": summary.get("passed", 0),
                    "failed": summary.get("failed", 0),
                    "pass_rate": (
                        summary.get("passed", 0) / summary.get("total", 1) * 100
                        if summary.get("total", 0) > 0
                        else 0
                    ),
                    "git_commit": archive_meta.get("git_commit", "")[:7],
                    "archived_at": archive_meta.get("archived_at", ""),
                }
            )
        except (json.JSONDecodeError, KeyError):
            continue

    return archives


def generate_trend_report(test_type: Optional[str] = None, limit: int = 20) -> str:
    """
    Generate trend report from archived results.

    Args:
        test_type: Optional test type filter
        limit: Maximum number of runs to include

    Returns:
        Markdown formatted trend report
    """
    archives = list_archives(test_type)[:limit]

    if not archives:
        return "No archived results found."

    lines = [
        "# Test Results Trend Report",
        "",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Runs Analyzed**: {len(archives)}",
        "",
        "## Pass Rate Trend",
        "",
        "| Run ID | Type | Total | Passed | Failed | Pass Rate | Commit |",
        "|--------|------|-------|--------|--------|-----------|--------|",
    ]

    for archive in archives:
        lines.append(
            f"| {archive['run_id']} | {archive['test_type']} | "
            f"{archive['total']} | {archive['passed']} | {archive['failed']} | "
            f"{archive['pass_rate']:.1f}% | {archive['git_commit']} |"
        )

    lines.append("")

    # Calculate statistics
    if archives:
        pass_rates = [a["pass_rate"] for a in archives]
        avg_rate = sum(pass_rates) / len(pass_rates)
        min_rate = min(pass_rates)
        max_rate = max(pass_rates)

        lines.extend(
            [
                "## Statistics",
                "",
                f"| Metric | Value |",
                f"|--------|-------|",
                f"| Average Pass Rate | {avg_rate:.1f}% |",
                f"| Minimum Pass Rate | {min_rate:.1f}% |",
                f"| Maximum Pass Rate | {max_rate:.1f}% |",
                "",
            ]
        )

        # Identify failing runs
        failing = [a for a in archives if a["failed"] > 0]
        if failing:
            lines.extend(
                [
                    "## Runs with Failures",
                    "",
                ]
            )
            for run in failing[:5]:
                lines.append(f"- {run['run_id']}: {run['failed']} failures")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Archive and manage test results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/archive_test_results.py --save tests/results/latest_utest.json
    python scripts/archive_test_results.py --set-baseline tests/results/results_utest.json
    python scripts/archive_test_results.py --prune --keep 10
    python scripts/archive_test_results.py --trend --type utest
    python scripts/archive_test_results.py --list
        """,
    )

    parser.add_argument(
        "--save",
        type=Path,
        metavar="FILE",
        help="Archive results file",
    )
    parser.add_argument(
        "--set-baseline",
        type=Path,
        metavar="FILE",
        help="Set results file as baseline",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="Prune old archives",
    )
    parser.add_argument(
        "--keep",
        type=int,
        default=DEFAULT_KEEP,
        help=f"Number of archives to keep per type (default: {DEFAULT_KEEP})",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List archived results",
    )
    parser.add_argument(
        "--trend",
        action="store_true",
        help="Generate trend report",
    )
    parser.add_argument(
        "--type",
        choices=["utest", "itest", "stest", "ftest", "all"],
        help="Filter by test type",
    )
    parser.add_argument(
        "--tag",
        type=str,
        help="Tag for archive (used with --save)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file for reports",
    )

    args = parser.parse_args()

    # Archive results
    if args.save:
        try:
            archive_results(args.save, args.type, args.tag)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return 1

    # Set baseline
    if args.set_baseline:
        try:
            set_baseline(args.set_baseline, args.type)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return 1

    # Prune archives
    if args.prune:
        removed = prune_archives(args.keep, args.type)
        print(f"Removed {removed} archive(s)")

    # List archives
    if args.list:
        archives = list_archives(args.type)
        if not archives:
            print("No archives found")
        else:
            print(f"\n{'File':<40} {'Type':<6} {'Pass Rate':<10} {'Commit'}")
            print("-" * 70)
            for archive in archives:
                print(
                    f"{archive['file']:<40} {archive['test_type']:<6} "
                    f"{archive['pass_rate']:>6.1f}%    {archive['git_commit']}"
                )
            print(f"\nTotal: {len(archives)} archives")

    # Generate trend report
    if args.trend:
        report = generate_trend_report(args.type)
        if args.output:
            args.output.write_text(report)
            print(f"Report saved to: {args.output}")
        else:
            print(report)

    # If no action specified, show help
    if not any([args.save, args.set_baseline, args.prune, args.list, args.trend]):
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
