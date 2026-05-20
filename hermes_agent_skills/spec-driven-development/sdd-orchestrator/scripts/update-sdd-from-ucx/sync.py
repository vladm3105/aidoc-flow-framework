#!/usr/bin/env python3
"""
UCX -> Hermes SDD Synchronization Script

Copies canonical UCX v3.2 templates, references, root documentation,
governance rules, and guidance into the Hermes skill tree.
Computes hashes, validates YAML, and produces a structured sync report.
"""

import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Hardcoded paths ───────────────────────────────────────────────
UCX_ROOT = Path("/opt/data/ucx_framework")
UCX_FLOW = UCX_ROOT / "ucx_flow_v3"
UCX_GOV = UCX_ROOT / "governance"
HSDD = Path("/home/ya/.hermes/skills/spec-driven-development")
TPL_DST = HSDD / "sdd-orchestrator" / "templates"
REF_DST = HSDD / "sdd-orchestrator" / "references"
GOV_DST = HSDD / "sdd-orchestrator" / "governance"
ROOT_DST = HSDD / "sdd-orchestrator" / "root-docs"
BACKUP_LOG = REF_DST / ".sync-backlog.json"

# ─── Explicit mappings: ucx_flow_v3 ────────────────────────────────
TEMPLATES = {
    "01_BRD/BRD-TEMPLATE.yaml": "01_BRD-TEMPLATE.yaml",
    "02_PRD/PRD-TEMPLATE.yaml": "02_PRD-TEMPLATE.yaml",
    "03_EARS/EARS-TEMPLATE.yaml": "03_EARS-TEMPLATE.yaml",
    "04_BDD/BDD-TEMPLATE.yaml": "04_BDD-TEMPLATE.yaml",
    "05_ADR/ADR-TEMPLATE.yaml": "05_ADR-TEMPLATE.yaml",
    "06_SPEC/SPEC-TEMPLATE.yaml": "06_SPEC-TEMPLATE.yaml",
    "07_TDD/TDD-TEMPLATE.yaml": "07_TDD-TEMPLATE.yaml",
    "08_IPLAN/IPLAN-TEMPLATE.yaml": "08_IPLAN-TEMPLATE.yaml",
}

REFERENCES = {
    "README.md": "ucx-readme.md",
    "AI_ASSISTANT_RULES.md": "ai-assistant-rules.md",
    "DOC_GOVERNANCE_CORE.md": "doc-governance-core.md",
    "QUICK_REFERENCE.md": "quick-reference.md",
    "ID_NAMING_STANDARDS.md": "id-naming-standards.md",
    "THRESHOLD_NAMING_RULES.md": "threshold-naming-rules.md",
    "TRACEABILITY.md": "traceability.md",
    "DIAGRAM_STANDARDS.md": "diagram-standards.md",
    "SPEC_DRIVEN_DEVELOPMENT_GUIDE.md": "sdd-guide.md",
    "TESTING_STRATEGY_TDD.md": "testing-strategy-tdd.md",
    "LAYER_REGISTRY.yaml": "layer-registry.yaml",
    "data_consistency_report.json": "data-consistency-report.json",
}

# ─── Explicit mappings: root docs ──────────────────────────────────
ROOT_DOCS = {
    "README.md": "README.md",
    "HERMES_UCX_RUNTIME_ENVIRONMENT.md": "HERMES_UCX_RUNTIME_ENVIRONMENT.md",
    "MULTI_PROJECT_QUICK_REFERENCE.md": "MULTI_PROJECT_QUICK_REFERENCE.md",
    "MULTI_PROJECT_SETUP_GUIDE.md": "MULTI_PROJECT_SETUP_GUIDE.md",
}

# ─── Governance sync: recursive, preserve tree ─────────────────────
GOV_INCLUDE_GLOBS = ["*.md", "*.yaml", "*.yml", "*.json", "*.py", "*.sh"]
GOV_EXCLUDE_DIRS = {"__pycache__", ".git", ".github", ".mypy_cache", "node_modules"}

LEGACY_ID_RE = __import__("re").compile(
    r'\b(REQ|NFR|SYS|CTR|TSPEC|TASK)-\d+\b'
)
UNQUOTED_TAG_RE = __import__("re").compile(
    r'^\s+(@brd|@prd|@ears|@bdd|@adr|@spec|@tdd|@iplan|@depends|@discoverability|@threshold)\s*:'
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(UCX_ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True, timeout=10,
        )
        return out.stdout.strip()
    except Exception:
        return "unknown"


def _git_status() -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(UCX_ROOT), "status", "--short"],
            capture_output=True, text=True, check=True, timeout=10,
        )
        return out.stdout.strip() or "clean"
    except Exception:
        return "unknown"


def classify(src: Path, dst: Path) -> str:
    if not src.exists():
        return "missing_src"
    if not dst.exists():
        return "NEW"
    if sha256_file(src) == sha256_file(dst):
        return "UNCHANGED"
    return "MODIFIED"


def validate_yaml(path: Path) -> tuple[bool, str | None]:
    try:
        import yaml
        yaml.safe_load(path.read_text())
        return True, None
    except Exception as exc:
        return False, str(exc)


def validate_content(path: Path) -> dict:
    text = path.read_text()
    legacy = LEGACY_ID_RE.findall(text)
    unquoted = [ln for ln in text.splitlines() if UNQUOTED_TAG_RE.match(ln)]
    return {
        "legacy_ids": legacy,
        "unquoted_tags": unquoted,
    }


def copy_atomic(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(dst.suffix + ".tmp")
    shutil.copy2(src, tmp)
    tmp.rename(dst)


def _walk_governance() -> list[tuple[Path, Path]]:
    """Return list of (src_rel, dst) for all governance files to sync."""
    results: list[tuple[Path, Path]] = []
    if not UCX_GOV.exists():
        return results
    for src in UCX_GOV.rglob("*"):
        if not src.is_file():
            continue
        # skip excluded dirs
        if any(part in GOV_EXCLUDE_DIRS for part in src.parts):
            continue
        # skip unsupported extensions
        if not any(src.match(g) for g in GOV_INCLUDE_GLOBS):
            continue
        rel = src.relative_to(UCX_GOV)
        dst = GOV_DST / rel
        results.append((src, dst))
    return results


def main() -> int:
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ucx_root": str(UCX_ROOT),
        "git_commit": _git_commit(),
        "git_status": _git_status(),
        "files": [],
        "validation": {"yaml": [], "content": []},
    }

    if not UCX_ROOT.exists():
        print(f"[ERROR] UCX root missing: {UCX_ROOT}", file=sys.stderr)
        return 1
    if not HSDD.exists():
        print(f"[ERROR] Hermes SDD root missing: {HSDD}", file=sys.stderr)
        return 1

    known_dst: set[Path] = set()

    # ── Phase 1: ucx_flow_v3 templates ──────────────────────────────
    for src_rel, dst_name in TEMPLATES.items():
        src = UCX_FLOW / src_rel
        dst = TPL_DST / dst_name
        known_dst.add(dst)
        status = classify(src, dst)
        entry = {
            "category": "template",
            "src": str(src_rel),
            "dst": str(dst.relative_to(HSDD)),
            "status": status,
            "src_hash": sha256_file(src) if src.exists() else None,
            "dst_hash": sha256_file(dst) if dst.exists() else None,
        }
        if status in ("NEW", "MODIFIED"):
            copy_atomic(src, dst)
            entry["copied"] = True
            yok, yerr = validate_yaml(dst)
            v = validate_content(dst)
            report["validation"]["yaml"].append({
                "file": str(dst.relative_to(HSDD)), "ok": yok, "error": yerr,
            })
            report["validation"]["content"].append({
                "file": str(dst.relative_to(HSDD)),
                "legacy_ids": v["legacy_ids"],
                "unquoted_tags": v["unquoted_tags"],
            })
        report["files"].append(entry)

    # ── Phase 2: ucx_flow_v3 references ─────────────────────────────
    for src_rel, dst_name in REFERENCES.items():
        src = UCX_FLOW / src_rel
        dst = REF_DST / dst_name
        known_dst.add(dst)
        status = classify(src, dst)
        entry = {
            "category": "reference",
            "src": str(src_rel),
            "dst": str(dst.relative_to(HSDD)),
            "status": status,
            "src_hash": sha256_file(src) if src.exists() else None,
            "dst_hash": sha256_file(dst) if dst.exists() else None,
        }
        if status in ("NEW", "MODIFIED"):
            copy_atomic(src, dst)
            entry["copied"] = True
            if dst.suffix in (".yaml", ".yml"):
                yok, yerr = validate_yaml(dst)
                report["validation"]["yaml"].append({
                    "file": str(dst.relative_to(HSDD)), "ok": yok, "error": yerr,
                })
        report["files"].append(entry)

    # ── Phase 3: root docs ──────────────────────────────────────────
    for src_name, dst_name in ROOT_DOCS.items():
        src = UCX_ROOT / src_name
        dst = ROOT_DST / dst_name
        known_dst.add(dst)
        status = classify(src, dst)
        entry = {
            "category": "root-doc",
            "src": str(src_name),
            "dst": str(dst.relative_to(HSDD)),
            "status": status,
            "src_hash": sha256_file(src) if src.exists() else None,
            "dst_hash": sha256_file(dst) if dst.exists() else None,
        }
        if status in ("NEW", "MODIFIED"):
            copy_atomic(src, dst)
            entry["copied"] = True
            if dst.suffix in (".yaml", ".yml"):
                yok, yerr = validate_yaml(dst)
                report["validation"]["yaml"].append({
                    "file": str(dst.relative_to(HSDD)), "ok": yok, "error": yerr,
                })
        report["files"].append(entry)

    # ── Phase 4: governance (recursive tree) ────────────────────────
    for src, dst in _walk_governance():
        known_dst.add(dst)
        status = classify(src, dst)
        entry = {
            "category": "governance",
            "src": str(src.relative_to(UCX_ROOT)),
            "dst": str(dst.relative_to(HSDD)),
            "status": status,
            "src_hash": sha256_file(src) if src.exists() else None,
            "dst_hash": sha256_file(dst) if dst.exists() else None,
        }
        if status in ("NEW", "MODIFIED"):
            copy_atomic(src, dst)
            entry["copied"] = True
            if dst.suffix in (".yaml", ".yml"):
                yok, yerr = validate_yaml(dst)
                report["validation"]["yaml"].append({
                    "file": str(dst.relative_to(HSDD)), "ok": yok, "error": yerr,
                })
        report["files"].append(entry)

    # ── Phase 5: orphan scan ────────────────────────────────────────
    # Scan known directories for files not in known_dst
    scan_dirs = [
        (TPL_DST, "template"),
        (REF_DST, "reference"),
        (ROOT_DST, "root-doc"),
        (GOV_DST, "governance"),
    ]
    for scan_dir, cat in scan_dirs:
        if not scan_dir.exists():
            continue
        for p in scan_dir.rglob("*"):
            if not p.is_file():
                continue
            if p.name == ".sync-backlog.json":
                continue
            if p not in known_dst:
                report["files"].append({
                    "category": cat,
                    "dst": str(p.relative_to(HSDD)),
                    "status": "ORPHANED",
                })

    # ── Phase 6: persist log ────────────────────────────────────────
    BACKUP_LOG.parent.mkdir(parents=True, exist_ok=True)
    logs = json.loads(BACKUP_LOG.read_text()) if BACKUP_LOG.exists() else []
    logs.append(report)
    BACKUP_LOG.write_text(json.dumps(logs, indent=2))

    # ── Phase 7: print report ───────────────────────────────────────
    counts = {"UNCHANGED": 0, "NEW": 0, "MODIFIED": 0, "ORPHANED": 0}
    for e in report["files"]:
        counts[e.get("status", "")] = counts.get(e.get("status", ""), 0) + 1

    yaml_errors = [v for v in report["validation"]["yaml"] if not v["ok"]]
    legacy_findings = [v for v in report["validation"]["content"] if v["legacy_ids"]]
    unquoted_findings = [v for v in report["validation"]["content"] if v["unquoted_tags"]]

    print("# UCX -> Hermes SDD Sync Report")
    print(f"\n**Timestamp**: {report['timestamp']}")
    print(f"**UCX root**: {report['ucx_root']}")
    print(f"**Git commit**: {report['git_commit']}")
    print(f"**Git status**: {report['git_status']}")
    print("\n## Summary")
    print(f"| Unchanged     | {counts['UNCHANGED']} |")
    print(f"| New           | {counts['NEW']} |")
    print(f"| Modified      | {counts['MODIFIED']} |")
    print(f"| Orphaned      | {counts['ORPHANED']} |")
    print(f"| YAML errors   | {len(yaml_errors)} |")
    print(f"| Legacy IDs    | {len(legacy_findings)} |")
    print(f"| Unquoted tags | {len(unquoted_findings)} |")

    def _print_section(cat: str) -> None:
        items = [e for e in report["files"] if e.get("category") == cat]
        if not items:
            return
        print(f"\n## {cat.replace('-', ' ').title()}s")
        for e in items:
            st = e.get("status", "")
            if st == "ORPHANED":
                print(f"- [{st}] {e['dst']}")
            else:
                print(f"- [{st}] {e['dst']}  (sha: {e.get('src_hash','')} -> {e.get('dst_hash','')})")

    _print_section("template")
    _print_section("reference")
    _print_section("root-doc")
    _print_section("governance")

    if yaml_errors:
        print("\n## YAML Validation Failures")
        for v in yaml_errors:
            print(f"- `{v['file']}`: {v['error']}")

    if legacy_findings:
        print("\n## Legacy ID Findings")
        for v in legacy_findings:
            print(f"- `{v['file']}`: {', '.join(v['legacy_ids'])}")

    if unquoted_findings:
        print("\n## Unquoted Tag Findings")
        for v in unquoted_findings:
            print(f"- `{v['file']}`: {len(v['unquoted_tags'])} lines")
            for ln in v["unquoted_tags"][:3]:
                print(f"  > {ln.strip()}")

    print(f"\n## Log written to: {BACKUP_LOG}")

    return 0 if not yaml_errors else 1


if __name__ == "__main__":
    sys.exit(main())
