"""profile_lint.py — Validate .aidoc/profile.yaml against ADAPTATION_SURFACE.yaml (Schema 1.1.0).

Authority: framework/governance/ADAPTATION_SURFACE.yaml
Enforces closed adaptation knobs, raise-only audit thresholds, and schema 1.1.0 compliance.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


MANDATORY_LAYERS = {"BRD", "PRD", "EARS", "SPEC", "TDD", "IPLAN"}
KNOWN_LAYERS = {"BRD", "PRD", "EARS", "BDD", "ADR", "SPEC", "TDD", "IPLAN", "CHG", "EVAL"}

KNOB_RANGES = {
    "quality_loop_max_iterations": (1, 10),
    "exec_max_files": (1, 100),
    "exec_max_diff_lines": (1, 10000),
    "exec_test_timeout_s": (30, 3600),
    "exec_max_attempts": (1, 10),
    "exec_token_budget": (10000, 2000000),
    "exec_wall_clock_budget_s": (60, 14400),
    "exec_failure_summary_lines": (5, 200),
}


def validate_profile(path: Path) -> tuple[bool, list[str]]:
    """Validate an adaptation profile file against schema 1.1.0.

    Returns (is_valid, list_of_errors).
    """
    errors: list[str] = []

    if yaml is None:
        return False, ["PyYAML is required for profile linting (pip install pyyaml)."]

    if not path.exists():
        return False, [f"Profile file not found: {path}"]

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, [f"Failed to parse YAML from {path}: {exc}"]

    if not isinstance(data, dict):
        return False, [f"Profile root must be a YAML mapping (got {type(data).__name__})"]

    # 1. Metadata & schema version
    meta = data.get("metadata")
    if not isinstance(meta, dict):
        errors.append("Missing required top-level 'metadata' section.")
    else:
        version = str(meta.get("schema_version", ""))
        if version != "1.1.0":
            errors.append(f"metadata.schema_version must be '1.1.0' (got '{version}')")
        if not meta.get("project_name"):
            errors.append("metadata.project_name must be non-empty.")

    # 2. active_layers
    active = data.get("active_layers")
    if active is not None:
        if not isinstance(active, list):
            errors.append("active_layers must be a list of layer names.")
        else:
            active_set = {str(l).upper() for l in active}
            unknown = active_set - KNOWN_LAYERS
            if unknown:
                errors.append(
                    f"active_layers contains unknown layer(s): {', '.join(sorted(unknown))}"
                )
            missing_mandatory = MANDATORY_LAYERS - active_set
            if missing_mandatory:
                errors.append(
                    f"active_layers cannot disable mandatory layer(s): {', '.join(sorted(missing_mandatory))}"
                )

    # 3. audit_threshold (Raise-only constraint: >= 90)
    thresholds = data.get("audit_threshold")
    if thresholds is not None:
        if not isinstance(thresholds, dict):
            errors.append("audit_threshold must be a mapping of layer -> integer.")
        else:
            for layer, val in thresholds.items():
                if not isinstance(val, int) or val < 90:
                    errors.append(
                        f"audit_threshold.{layer} must be an integer >= 90 (raise-only floor; got {val})"
                    )

    # 4. review_mode
    review_mode = data.get("review_mode")
    if review_mode is not None:
        if review_mode not in ("team", "single_pass"):
            errors.append(f"review_mode must be 'team' or 'single_pass' (got '{review_mode}')")

    # 5. Numeric execution limits
    for knob, (min_v, max_v) in KNOB_RANGES.items():
        if knob in data:
            val = data[knob]
            if not isinstance(val, int) or val < min_v or val > max_v:
                errors.append(f"{knob} must be an integer between {min_v} and {max_v} (got {val})")

    # 6. exec_protected_paths
    protected = data.get("exec_protected_paths")
    if protected is not None:
        if not isinstance(protected, list) or not all(isinstance(p, str) for p in protected):
            errors.append("exec_protected_paths must be a list of relative path strings.")

    # 7. ci_bindings
    ci_bindings = data.get("ci_bindings")
    if ci_bindings is not None and not isinstance(ci_bindings, dict):
        errors.append("ci_bindings must be a mapping of platform mechanics.")

    # 8. glossary
    glossary = data.get("glossary")
    if glossary is not None and not isinstance(glossary, dict):
        errors.append("glossary must be a mapping of term -> definition.")

    return len(errors) == 0, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sdd_doc_lint.profile_lint",
        description="Validate an adaptation profile (.aidoc/profile.yaml) against schema 1.1.0.",
    )
    parser.add_argument("path", type=Path, help="Path to .aidoc/profile.yaml")
    args = parser.parse_args(argv)

    ok, errors = validate_profile(args.path)
    if ok:
        print(f"✓ Profile {args.path} conforms to schema 1.1.0 (valid adaptation knobs)")
        return 0
    print(f"✗ Profile {args.path} failed schema 1.1.0 validation:", file=sys.stderr)
    for err in errors:
        print(f"  - {err}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
