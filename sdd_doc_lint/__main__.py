"""CLI: python -m sdd_doc_lint [--registry PATH] [--mode build|gate-code]
       [--skip-coverage-gate] [--warn-exit] <path> [<path> ...]

Exit codes:

* **0** — no error-level findings (and, under ``--warn-exit``, no findings at all)
* **1** — error findings; with ``--warn-exit``, warning findings too
* **2** — usage error, *or* the registry could not be read
* **3** — a runtime prerequisite is missing: Python is below the floor, or PyYAML
  cannot be imported. Raised at package import, before any linting. Kept distinct
  from 2 so a caller can tell "the linter declined to run" from "your document is
  wrong" — see ``sdd_doc_lint.EXIT_MISSING_PREREQUISITE``.

The framework registry is located automatically (upward search for
``framework/registry/LAYER_REGISTRY.yaml``, or ``$SDD_REGISTRY`` / ``--registry``),
so the same code runs from the canonical repo or a vendored platform copy.
Backs the ``on_author`` (advisory) and ``pre_merge`` (blocking) trigger points —
see framework/governance/REVIEW_REMEDIATION_FLOW.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import (
    compute_disabled_skippable,
    find_profile,
    lint_path,
    load_active_layers,
)


def main(argv: list[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    if raw_argv and ("--slice" in raw_argv or (raw_argv[0] == "slice")):
        from sdd_doc_lint.slice import main as slice_main

        slice_argv = [a for a in raw_argv if a not in ("--slice", "slice")]
        return slice_main(slice_argv)

    parser = argparse.ArgumentParser(prog="sdd_doc_lint")
    parser.add_argument("paths", nargs="*", default=[], help="file(s) or directory(ies) to lint")
    parser.add_argument(
        "--slice",
        nargs="*",
        metavar="TARGET",
        help="extract minimal topological context slice (delegates to sdd_doc_lint.slice)",
    )
    parser.add_argument(
        "--profile",
        type=Path,
        default=None,
        help="path to .aidoc/profile.yaml to validate against schema 1.1.0",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=None,
        help="path to LAYER_REGISTRY.yaml (else $SDD_REGISTRY or an upward search)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format (text = human-readable; json = single array of findings)",
    )
    parser.add_argument(
        "--mode",
        choices=("build", "gate-code"),
        default="build",
        help="forward-coverage severity mode (CFB-PR-2 DD-6): 'build' warns when an "
        "in-scope FR reaches a SPEC but no IPLAN; 'gate-code' blocks it",
    )
    parser.add_argument(
        "--skip-coverage-gate",
        action="store_true",
        help="suppress the forward-coverage gate entirely (CFB-PR-2 DD-9 — the "
        "transient-migration escape hatch)",
    )
    parser.add_argument(
        "--warn-exit",
        action="store_true",
        help="exit 1 when any finding is emitted, not only error-severity ones; the "
        "default contract (0 unless an error) is what CI gates on, so callers that "
        "want to see warnings — the plugin's review hook — opt in here",
    )
    parser.add_argument(
        "--active-layers",
        default=None,
        help="CSV of active layers (overrides `.aidoc/profile.yaml` discovery); a "
        "disabled skippable layer (BDD/ADR) is not demanded downstream "
        "(ACTIVE-LAYERS-CASCADE-001)",
    )
    parser.add_argument(
        "--check-surfaces",
        type=Path,
        nargs="?",
        const=Path("."),
        default=None,
        metavar="REPO_ROOT",
        help="verify repository governance surfaces and detect retired monolithic anti-patterns",
    )
    # Native SDD Graph and Observability Adapter (CHG-108, GD-95)
    parser.add_argument(
        "--graph-check",
        type=Path,
        default=None,
        metavar="PATH",
        help="verify Binary Topological Validation (BTV) on native SDD property graph",
    )
    parser.add_argument(
        "--blast-radius",
        type=str,
        default=None,
        metavar="NODE_ID",
        help="calculate downstream blast radius of a mutated graph node ID",
    )
    parser.add_argument(
        "--render-spec",
        type=Path,
        default=None,
        metavar="GRAPH_PATH",
        help="render human-readable Markdown spec sheet from SDD graph",
    )
    parser.add_argument(
        "--render-diagram",
        type=Path,
        default=None,
        metavar="GRAPH_PATH",
        help="render Mermaid architecture diagram from SDD graph",
    )
    parser.add_argument(
        "--diagram-type",
        choices=("lineage", "c4-container"),
        default="lineage",
        help="diagram type for --render-diagram (default: lineage)",
    )
    parser.add_argument(
        "--render-matrix",
        type=Path,
        default=None,
        metavar="GRAPH_PATH",
        help="render compliance and traceability matrix from SDD graph",
    )
    parser.add_argument(
        "--render-pr-impact",
        action="store_true",
        help="render PR delta impact summary comparing --base and --head graphs",
    )
    parser.add_argument(
        "--base",
        type=Path,
        default=None,
        metavar="BASE_PATH",
        help="base graph directory or file for --render-pr-impact",
    )
    parser.add_argument(
        "--head",
        type=Path,
        default=None,
        metavar="HEAD_PATH",
        help="head graph directory or file for --render-pr-impact",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        metavar="OUT_FILE",
        help="output destination file for rendered spec sheets or diagrams",
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    # 1. Native SDD Graph & Observability CLI Handlers
    if args.graph_check is not None:
        from sdd_doc_lint.graph_engine import GraphEngine

        engine = GraphEngine()
        p = args.graph_check
        graph = engine.load_graph_directory(p) if p.is_dir() else engine.load_graph_file(p)
        findings = engine.validate_btv(graph)
        errors = [f for f in findings if f.severity == "error"]
        for f in findings:
            prefix = "ERROR" if f.severity == "error" else "WARN"
            stream = sys.stderr if f.severity == "error" else sys.stdout
            print(f"[{prefix}] {f.code}: {f.message}", file=stream)
        if errors:
            print(f"\nsdd-doc-lint: ✗ BTV Graph Check failed with {len(errors)} error(s).", file=sys.stderr)
            return 1
        print(f"✓ Native SDD Graph conforms to BTV (0 cycles, 0 dangling edges, {len(graph.nodes)} nodes).")
        return 0

    if args.blast_radius is not None:
        from sdd_doc_lint.graph_engine import GraphEngine

        engine = GraphEngine()
        p = Path(args.paths[0]) if args.paths else Path("docs/sdd/graph")
        graph = engine.load_graph_directory(p) if p.is_dir() else engine.load_graph_file(p)
        radius = engine.calculate_blast_radius(graph, args.blast_radius)
        import json
        print(json.dumps(sorted(list(radius)), indent=2))
        return 0

    if args.render_spec is not None:
        from sdd_doc_lint.graph_engine import GraphEngine
        from sdd_doc_lint.observability_adapter import ObservabilityAdapter

        engine = GraphEngine()
        p = args.render_spec
        graph = engine.load_graph_directory(p) if p.is_dir() else engine.load_graph_file(p)
        adapter = ObservabilityAdapter()
        spec = adapter.render_spec_sheet(graph)
        if args.out:
            args.out.write_text(spec, encoding="utf-8")
            print(f"✓ Rendered specification sheet to {args.out}")
        else:
            sys.stdout.write(spec)
        return 0

    if args.render_diagram is not None:
        from sdd_doc_lint.graph_engine import GraphEngine
        from sdd_doc_lint.observability_adapter import ObservabilityAdapter

        engine = GraphEngine()
        p = args.render_diagram
        graph = engine.load_graph_directory(p) if p.is_dir() else engine.load_graph_file(p)
        adapter = ObservabilityAdapter()
        diag = adapter.render_mermaid(graph, diagram_type=args.diagram_type)
        if args.out:
            args.out.write_text(diag, encoding="utf-8")
            print(f"✓ Rendered {args.diagram_type} diagram to {args.out}")
        else:
            sys.stdout.write(diag)
        return 0

    if args.render_matrix is not None:
        from sdd_doc_lint.graph_engine import GraphEngine
        from sdd_doc_lint.observability_adapter import ObservabilityAdapter

        engine = GraphEngine()
        p = args.render_matrix
        graph = engine.load_graph_directory(p) if p.is_dir() else engine.load_graph_file(p)
        adapter = ObservabilityAdapter()
        matrix = adapter.render_matrix(graph)
        if args.out:
            args.out.write_text(matrix, encoding="utf-8")
            print(f"✓ Rendered compliance matrix to {args.out}")
        else:
            sys.stdout.write(matrix)
        return 0

    if args.render_pr_impact:
        from sdd_doc_lint.graph_engine import GraphEngine
        from sdd_doc_lint.observability_adapter import ObservabilityAdapter

        if not args.base or not args.head:
            print("Error: --render-pr-impact requires both --base and --head paths", file=sys.stderr)
            return 2
        engine = GraphEngine()
        g_base = engine.load_graph_directory(args.base) if args.base.is_dir() else engine.load_graph_file(args.base)
        g_head = engine.load_graph_directory(args.head) if args.head.is_dir() else engine.load_graph_file(args.head)
        adapter = ObservabilityAdapter()
        summary = adapter.render_pr_impact_summary(g_base, g_head)
        if args.out:
            args.out.write_text(summary, encoding="utf-8")
            print(f"✓ Rendered PR impact summary to {args.out}")
        else:
            sys.stdout.write(summary)
        return 0

    if args.profile is not None:
        from sdd_doc_lint.profile_lint import validate_profile

        ok, errors = validate_profile(args.profile)
        if ok:
            print(f"✓ Profile {args.profile} conforms to schema 1.1.0 (valid adaptation knobs)")
            return 0
        print(f"✗ Profile {args.profile} failed schema 1.1.0 validation:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    if args.check_surfaces is not None:
        from sdd_doc_lint.surface_lint import lint_surfaces

        findings = lint_surfaces(args.check_surfaces)
        if not findings:
            print(f"✓ Governance surfaces in {args.check_surfaces} conform to framework standards.")
            return 0
        has_errors = False
        for f in findings:
            print(
                f.format(args.check_surfaces),
                file=sys.stderr if f.severity == "ERROR" else sys.stdout,
            )
            if f.severity == "ERROR":
                has_errors = True
        return 1 if (has_errors or args.warn_exit) else 0

    if not args.paths:
        parser.error("the following arguments are required: paths (or --profile, --check-surfaces)")

    override = None
    if args.active_layers is not None:
        override = frozenset(x.strip().lower() for x in args.active_layers.split(",") if x.strip())

    findings = []
    try:
        for arg in args.paths:
            path = Path(arg)
            if override is not None:
                active_layers = override
            else:
                profile = find_profile(path)
                active_layers = load_active_layers(profile) if profile else None
            findings.extend(
                lint_path(
                    path,
                    registry=args.registry,
                    mode=args.mode,
                    skip_coverage=args.skip_coverage_gate,
                    disabled_skippable=compute_disabled_skippable(active_layers),
                )
            )
    except OSError as exc:
        print(f"sdd-doc-lint: registry unavailable ({exc}); skipping.", file=sys.stderr)
        return 2

    if args.format == "json":
        import json

        payload = [
            {
                "code": f.code,
                "severity": f.severity,
                "file": str(f.path),
                "line": f.line,
                "section": getattr(f, "section", None),
                "message": f.message,
            }
            for f in sorted(findings, key=lambda x: (x.path, x.line, x.code))
        ]
        print(json.dumps(payload))
    else:
        errors = [f for f in findings if f.severity == "error"]
        for f in sorted(findings, key=lambda x: (x.path, x.line, x.code)):
            stream = sys.stderr if f.severity == "error" else sys.stdout
            print(str(f), file=stream)
        if errors:
            print(
                f"\nsdd-doc-lint: {len(errors)} error(s) across "
                f"{len({f.path for f in errors})} file(s).",
                file=sys.stderr,
            )
        elif not findings:
            # §3.6c: a file without an NN_LAYER segment or ARTIFACT-NN prefix
            # is SKIPPED by layer detection, not linted — so "no findings" may
            # mean "nothing was checked". Say so, so a clean-looking run over
            # non-layer paths is never mistaken for a clean baseline.
            print(
                "sdd-doc-lint: no structural findings "
                "(paths without a layer pattern were skipped, not checked — "
                "pass layer-pattern paths to lint real documents)."
            )

    if any(f.severity == "error" for f in findings):
        return 1
    # Without this, a warning is emitted and then reported as success, so a
    # caller that speaks only on a non-zero exit can never surface one.
    return 1 if (args.warn_exit and findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
