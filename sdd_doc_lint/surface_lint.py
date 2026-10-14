"""surface_lint.py — Validate repository root governance surfaces and detect anti-patterns.

Enforces clean repository-level governance by detecting retired monolithic files:
- SURF-001 (ERROR): Loose DECISIONS.md (retired per CHG-80 / CHG-95 / GD-71 / GD-78)
- SURF-002 (WARNING): Loose ROADMAP.md (retired; planning lives in plans/*-PLAN.md)
- SURF-003 (WARNING): Loose CHANGELOG.md (retired per CHG-40 / CHG-94)
- SURF-004 (ERROR): Loose HANDOFF.md (retired; session state lives on issues/plans)

Tombstone exemption: files explicitly marked as retired/frozen tombstones are exempt.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SurfaceFinding:
    rule_id: str
    severity: str  # "ERROR" | "WARNING"
    path: Path
    message: str
    remediation: str

    def format(self, repo_root: Path | None = None) -> str:
        if repo_root:
            try:
                display_path = self.path.resolve().relative_to(repo_root.resolve())
            except ValueError:
                display_path = self.path
        else:
            display_path = self.path
        prefix = "❌ ERROR" if self.severity == "ERROR" else "⚠️ WARNING"
        return (
            f"{prefix} [{self.rule_id}]: {self.message}\n"
            f"  File: {display_path}\n"
            f"  Remediation: {self.remediation}"
        )


TOMBSTONE_MARKERS = (
    "TOMBSTONE",
    "RETIRED",
    "FROZEN",
)


def is_tombstone(file_path: Path) -> bool:
    """Return True if the file contains explicit tombstone markers."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")[:2048].upper()
        return any(marker in content for marker in TOMBSTONE_MARKERS)
    except OSError:
        return False


# Candidate paths relative to repository root
SURFACE_RULES = [
    (
        "SURF-001",
        "ERROR",
        [
            Path("DECISIONS.md"),
            Path("docs/DECISIONS.md"),
            Path("plans/DECISIONS.md"),
        ],
        "Monolithic DECISIONS.md detected.",
        "Monolithic decision logs are retired per GD-71 and GD-78. "
        "Move architectural decisions to docs/sdd/05_ADR/ (Layer 05) and change decisions to CHG-NN.yaml Section 1B.",
    ),
    (
        "SURF-002",
        "WARNING",
        [
            Path("ROADMAP.md"),
            Path("docs/ROADMAP.md"),
            Path("plans/ROADMAP.md"),
        ],
        "Monolithic ROADMAP.md detected.",
        "Monolithic roadmaps are retired. Feature planning lives in plans/*-PLAN.md and GitHub milestones.",
    ),
    (
        "SURF-003",
        "WARNING",
        [
            Path("CHANGELOG.md"),
            Path("docs/CHANGELOG.md"),
        ],
        "Monolithic CHANGELOG.md detected.",
        "CHANGELOG.md is retired per CHG-40 and CHG-94. Use GitHub Releases and structured change records (docs/sdd/09_CHG/archive/).",
    ),
    (
        "SURF-004",
        "ERROR",
        [
            Path("HANDOFF.md"),
            Path("docs/HANDOFF.md"),
            Path("plans/HANDOFF.md"),
        ],
        "Session HANDOFF.md file detected.",
        "Session handoff files are retired. Record active continuity on GitHub issues and verified plans (plans/*-PLAN.md).",
    ),
]


def lint_surfaces(repo_root: Path) -> list[SurfaceFinding]:
    """Inspect repository root for forbidden governance anti-pattern files."""
    findings: list[SurfaceFinding] = []
    root = repo_root.resolve()

    for rule_id, severity, candidate_rel_paths, msg, remediation in SURFACE_RULES:
        for rel_path in candidate_rel_paths:
            target = root / rel_path
            if target.is_file():
                if is_tombstone(target):
                    continue
                findings.append(
                    SurfaceFinding(
                        rule_id=rule_id,
                        severity=severity,
                        path=target,
                        message=msg,
                        remediation=remediation,
                    )
                )

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sdd_doc_lint.surface_lint",
        description="Verify repository governance surfaces and detect retired monolithic anti-patterns.",
    )
    parser.add_argument(
        "repo_root",
        type=Path,
        nargs="?",
        default=Path("."),
        help="Path to repository root (default: current directory)",
    )
    parser.add_argument(
        "--warn-exit",
        action="store_true",
        help="Exit 1 on warnings as well as errors",
    )
    args = parser.parse_args(argv)

    findings = lint_surfaces(args.repo_root)
    if not findings:
        print(f"✓ Governance surfaces in {args.repo_root} conform to framework standards.")
        return 0

    has_errors = False
    for f in findings:
        print(f.format(args.repo_root), file=sys.stderr if f.severity == "ERROR" else sys.stdout)
        if f.severity == "ERROR":
            has_errors = True

    if has_errors or (args.warn_exit and findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
