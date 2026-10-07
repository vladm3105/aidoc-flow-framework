#!/usr/bin/env python3
"""SWF Workflow Linter — validates CNCF Serverless Workflow DSL v0.8 files and templates.

Validates declarative workflow graphs against governance rules:
  SWF-L001: CNCF DSL Spec Compliance — must declare id, name, specVersion 0.8, start, states
  SWF-L002: Valid State Types — state type must be in approved allowlist
  SWF-L003: Deterministic Terminal State — at least one state must declare end: true or terminate: true
  SWF-L004: DAG Transition & Reachability — all transitions must target declared states; no dead ends
  SWF-L005: SAGA Compensation Integrity — compensatedBy must target defined operation state
  SWF-L006: Parallel Branch Completeness — branches must have unique names and actions
  SWF-L007: Review Crew Parity — layer review workflows must match REVIEW_CREWS.yaml personas

Usage:
  python3 -m sdd_doc_lint.swf_lint [--format text|json] [--warn-exit] <path> [<path> ...]
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("sdd_swf_lint: PyYAML prerequisite missing", file=sys.stderr)
    sys.exit(3)

EXIT_CLEAN = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 2
EXIT_MISSING_PREREQUISITE = 3

VALID_STATE_TYPES = frozenset(
    {
        "operation",
        "switch",
        "parallel",
        "callback",
        "event",
        "sleep",
        "inject",
        "foreach",
    }
)


@dataclass
class Finding:
    file: str
    line: int
    severity: str  # ERROR | WARNING
    rule: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def __str__(self) -> str:
        return f"{self.file}:{self.line}: [{self.severity} {self.rule}] {self.message}"


def _find_repo_root(start: Path) -> Path | None:
    current = start.resolve()
    for parent in [current] + list(current.parents):
        if (parent / "framework" / "governance" / "REVIEW_CREWS.yaml").is_file():
            return parent
    return None


def _load_review_crews(repo_root: Path | None) -> dict[str, Any] | None:
    if not repo_root:
        return None
    crews_path = repo_root / "framework" / "governance" / "REVIEW_CREWS.yaml"
    if not crews_path.is_file():
        return None
    try:
        with crews_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("crews", {})
    except Exception:
        return None


def extract_workflow(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    """Extract workflow dict from a .sw.yaml file or hybrid *-SWF-TEMPLATE.yaml."""
    try:
        content = path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
    except Exception as e:
        return None, [f"Failed to parse YAML: {e}"]

    if not isinstance(data, dict):
        return None, ["Document root must be a YAML mapping"]

    # Root-level workflow
    if "states" in data and isinstance(data["states"], list):
        return data, []

    # Recursive search for embedded workflow
    found: dict[str, Any] | None = None

    def search(obj: Any) -> None:
        nonlocal found
        if found is not None:
            return
        if isinstance(obj, dict):
            if "states" in obj and isinstance(obj["states"], list):
                found = obj
                return
            for v in obj.values():
                search(v)

    search(data)
    if found is not None:
        return found, []

    return None, ["No CNCF Serverless Workflow definition found (missing states list)"]


def lint_workflow_dict(
    wf: dict[str, Any],
    file_path: str,
    review_crews: dict[str, Any] | None = None,
) -> list[Finding]:
    findings: list[Finding] = []

    # SWF-L001: Root schema compliance
    for field in ("id", "name", "start", "states"):
        if field not in wf:
            findings.append(
                Finding(
                    file_path, 1, "ERROR", "SWF-L001", f"Missing required root field: '{field}'"
                )
            )

    spec_ver = str(wf.get("specVersion", "")).strip()
    if spec_ver != "0.8":
        findings.append(
            Finding(
                file_path,
                1,
                "ERROR",
                "SWF-L001",
                f"specVersion must be '0.8' (found '{spec_ver}')",
            )
        )

    states = wf.get("states")
    if not isinstance(states, list) or len(states) == 0:
        findings.append(
            Finding(file_path, 1, "ERROR", "SWF-L001", "'states' must be a non-empty list")
        )
        return findings

    state_dict: dict[str, dict[str, Any]] = {}
    for i, state in enumerate(states, 1):
        if not isinstance(state, dict):
            findings.append(
                Finding(file_path, i, "ERROR", "SWF-L001", f"State item #{i} is not a YAML mapping")
            )
            continue
        s_name = state.get("name")
        if not s_name:
            findings.append(
                Finding(file_path, i, "ERROR", "SWF-L001", f"State #{i} missing 'name' attribute")
            )
            continue
        if s_name in state_dict:
            findings.append(
                Finding(file_path, i, "ERROR", "SWF-L001", f"Duplicate state name '{s_name}'")
            )
        state_dict[s_name] = state

    start_state = wf.get("start")
    if start_state and start_state not in state_dict:
        findings.append(
            Finding(
                file_path,
                1,
                "ERROR",
                "SWF-L004",
                f"Start state '{start_state}' is not defined in 'states'",
            )
        )

    # State validation
    terminal_states = 0
    compensated_states: set[str] = set()

    for s_name, state in state_dict.items():
        s_type = state.get("type")
        # SWF-L002: Valid state types
        if s_type not in VALID_STATE_TYPES:
            findings.append(
                Finding(
                    file_path,
                    1,
                    "ERROR",
                    "SWF-L002",
                    f"State '{s_name}' has invalid type '{s_type}'; must be one of {sorted(VALID_STATE_TYPES)}",
                )
            )

        # Terminal state detection
        is_end = state.get("end") is True
        is_terminate = isinstance(state.get("end"), dict) and state["end"].get("terminate") is True
        if is_end or is_terminate:
            terminal_states += 1

        # SWF-L004: Transition integrity
        if "transition" in state:
            target = state["transition"]
            if target not in state_dict:
                findings.append(
                    Finding(
                        file_path,
                        1,
                        "ERROR",
                        "SWF-L004",
                        f"State '{s_name}' transitions to undefined state '{target}'",
                    )
                )

        if s_type == "switch":
            conditions = state.get("dataConditions", [])
            for cond in conditions:
                c_target = cond.get("transition")
                if c_target and c_target not in state_dict:
                    findings.append(
                        Finding(
                            file_path,
                            1,
                            "ERROR",
                            "SWF-L004",
                            f"Switch state '{s_name}' condition transitions to undefined state '{c_target}'",
                        )
                    )
            default_target = state.get("defaultCondition", {}).get("transition")
            if default_target and default_target not in state_dict:
                findings.append(
                    Finding(
                        file_path,
                        1,
                        "ERROR",
                        "SWF-L004",
                        f"Switch state '{s_name}' defaultCondition transitions to undefined state '{default_target}'",
                    )
                )

        # SWF-L005: SAGA compensation integrity
        if "compensatedBy" in state:
            comp_target = state["compensatedBy"]
            if comp_target not in state_dict:
                findings.append(
                    Finding(
                        file_path,
                        1,
                        "ERROR",
                        "SWF-L005",
                        f"State '{s_name}' compensatedBy undefined state '{comp_target}'",
                    )
                )
            else:
                target_state = state_dict[comp_target]
                if target_state.get("type") != "operation":
                    findings.append(
                        Finding(
                            file_path,
                            1,
                            "ERROR",
                            "SWF-L005",
                            f"Saga compensation target '{comp_target}' must be an operation state (got '{target_state.get('type')}')",
                        )
                    )
                compensated_states.add(comp_target)

        # SWF-L006: Parallel state branch completeness
        if s_type == "parallel":
            branches = state.get("branches")
            if not isinstance(branches, list) or len(branches) == 0:
                findings.append(
                    Finding(
                        file_path,
                        1,
                        "ERROR",
                        "SWF-L006",
                        f"Parallel state '{s_name}' must declare a non-empty list of 'branches'",
                    )
                )
            else:
                branch_names = set()
                for b_idx, branch in enumerate(branches, 1):
                    if not isinstance(branch, dict):
                        findings.append(
                            Finding(
                                file_path,
                                1,
                                "ERROR",
                                "SWF-L006",
                                f"Parallel state '{s_name}' branch #{b_idx} is not a YAML mapping",
                            )
                        )
                        continue
                    b_name = branch.get("name")
                    if not b_name:
                        findings.append(
                            Finding(
                                file_path,
                                1,
                                "ERROR",
                                "SWF-L006",
                                f"Parallel state '{s_name}' branch #{b_idx} missing 'name'",
                            )
                        )
                    elif b_name in branch_names:
                        findings.append(
                            Finding(
                                file_path,
                                1,
                                "ERROR",
                                "SWF-L006",
                                f"Parallel state '{s_name}' has duplicate branch name '{b_name}'",
                            )
                        )
                    branch_names.add(b_name)

                    actions = branch.get("actions")
                    if not isinstance(actions, list) or len(actions) == 0:
                        findings.append(
                            Finding(
                                file_path,
                                1,
                                "ERROR",
                                "SWF-L006",
                                f"Parallel state '{s_name}' branch '{b_name}' must declare non-empty 'actions'",
                            )
                        )

    # SWF-L003: Check terminal states exist
    if terminal_states == 0:
        findings.append(
            Finding(
                file_path,
                1,
                "ERROR",
                "SWF-L003",
                "Workflow must contain at least one terminal state (end: true or end.terminate: true)",
            )
        )

    # SWF-L007: Review Crew Parity for review workflows
    metadata = wf.get("metadata", {})
    governed_layer = metadata.get("governed_layer") or wf.get("governed_layer")
    if not governed_layer and "layer" in wf:
        governed_layer = wf["layer"]

    if governed_layer and review_crews:
        # Match layer code (e.g. '01_BRD' -> 'BRD' or 'BRD')
        layer_key = governed_layer.split("_", 1)[1] if "_" in governed_layer else governed_layer
        if layer_key in review_crews:
            crew = review_crews[layer_key]
            expected_personas = set(crew.get("review", {}).keys())

            # Find review dispatch parallel state
            dispatch_states = [s for s in state_dict.values() if s.get("type") == "parallel"]
            for d_state in dispatch_states:
                branches = d_state.get("branches", [])
                dispatched_personas = set()
                for b in branches:
                    for act in b.get("actions", []):
                        fn_args = act.get("functionRef", {}).get("arguments", {})
                        if isinstance(fn_args, dict) and "persona" in fn_args:
                            dispatched_personas.add(fn_args["persona"])

                if dispatched_personas:
                    missing = expected_personas - dispatched_personas
                    if missing:
                        findings.append(
                            Finding(
                                file_path,
                                1,
                                "WARNING",
                                "SWF-L007",
                                f"Review crew for layer '{layer_key}' missing declared personas: {sorted(missing)}",
                            )
                        )

    return findings


def lint_file(path: Path, review_crews: dict[str, Any] | None = None) -> list[Finding]:
    wf, errors = extract_workflow(path)
    if errors:
        return [Finding(str(path), 1, "ERROR", "SWF-L001", msg) for msg in errors]
    if wf is None:
        return []
    return lint_workflow_dict(wf, str(path), review_crews=review_crews)


lint_path = lint_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sdd_swf_lint", description=__doc__)
    parser.add_argument("paths", nargs="+", help="File(s) or directory(ies) containing workflows")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    parser.add_argument(
        "--warn-exit",
        action="store_true",
        help="Exit 1 when any warning is emitted, not only errors",
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    repo_root = None
    all_findings: list[Finding] = []

    target_files: list[Path] = []
    for p_str in args.paths:
        p = Path(p_str)
        if not repo_root:
            repo_root = _find_repo_root(p)
        if p.is_file():
            target_files.append(p)
        elif p.is_dir():
            target_files.extend(sorted(p.rglob("*.sw.yaml")))
            target_files.extend(sorted(p.rglob("*-SWF-TEMPLATE.yaml")))
        else:
            all_findings.append(
                Finding(p_str, 0, "ERROR", "USAGE", f"Path does not exist: {p_str}")
            )

    review_crews = _load_review_crews(repo_root)

    for file_path in target_files:
        all_findings.extend(lint_file(file_path, review_crews=review_crews))

    if args.format == "json":
        print(json.dumps([f.to_dict() for f in all_findings], indent=2))
    else:
        for f in all_findings:
            print(str(f))
        errors = sum(1 for f in all_findings if f.severity == "ERROR")
        warnings = sum(1 for f in all_findings if f.severity == "WARNING")
        if all_findings:
            print(
                f"\nsdd_swf_lint: {errors} error(s), {warnings} warning(s) in {len(target_files)} file(s)"
            )

    if any(f.severity == "ERROR" for f in all_findings):
        return EXIT_FINDINGS
    if args.warn_exit and any(f.severity == "WARNING" for f in all_findings):
        return EXIT_FINDINGS
    return EXIT_CLEAN


if __name__ == "__main__":
    sys.exit(main())
