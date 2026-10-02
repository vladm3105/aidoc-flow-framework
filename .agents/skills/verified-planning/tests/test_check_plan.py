import contextlib
import importlib.util
import io
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "check_plan.py"

# Load the gate in-process (no subprocess: faster, and avoids a security-linter
# flag for shelling out from a test).
_spec = importlib.util.spec_from_file_location("check_plan_under_test", SCRIPT)
_cp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cp)


class _Result:
    def __init__(self, returncode, stdout, stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _run(*args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = _cp.main([str(a) for a in args])
    return _Result(rc, buf.getvalue())


def _repo(tmp_path: Path) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / ".git").mkdir()
    src = tmp_path / "src"
    src.mkdir()
    (src / "loop.py").write_text(
        "\n".join(f"line{n}" for n in range(1, 11)) + "\nappend_event(task_completed)\n"
    )  # line 11
    return tmp_path


LEDGER_HEADER = (
    "## Claim ledger\n\n| # | Claim | Symbol | Citation |\n|---|---|---|---|\n"
)
REVIEW_OK = (
    "## Review log\n\n"
    "### Pass 1 - 2026-06-07\n- self review.\n\n"
    "### Pass 2 - 2026-06-07 - independent\n- no new findings.\n"
)
GOOD_ROW = "| 1 | completion is logged | `task_completed` | src/loop.py:11 |\n"


def _plan(repo, ledger_rows, review=REVIEW_OK, name="PLAN-001_x.md"):
    p = repo / name
    p.write_text(LEDGER_HEADER + ledger_rows + "\n" + review)
    return p


def test_resolved_citation_passes(tmp_path):
    repo = _repo(tmp_path)
    plan = _plan(repo, GOOD_ROW)
    r = _run(plan)
    assert r.returncode == 0, r.stdout + r.stderr


def test_missing_file_fails(tmp_path):
    repo = _repo(tmp_path)
    plan = _plan(repo, "| 1 | x | `foo` | src/nope.py:3 |\n")
    r = _run(plan)
    assert r.returncode == 1
    assert "does not exist" in r.stdout


def test_directory_citation_fails_gracefully(tmp_path):
    repo = _repo(tmp_path)
    plan = _plan(repo, "| 1 | x | `src` | src:1 |\n")
    r = _run(plan)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "is not a file" in r.stdout
    assert "Traceback" not in r.stderr


def test_line_out_of_range_with_symbol_warns(tmp_path):
    # PLAN-051: out-of-range line + symbol present elsewhere → warn (rc 0), the symbol is authoritative.
    repo = _repo(tmp_path)
    plan = _plan(repo, "| 1 | x | `task_completed` | src/loop.py:999 |\n")
    r = _run(plan)
    assert r.returncode == 0, r.stdout
    assert "drifted" in r.stdout and "warn" in r.stdout


def test_drifted_symbol_warns(tmp_path):
    # PLAN-051: symbol present but not at the cited line → warn (rc 0), not a failure.
    repo = _repo(tmp_path)
    plan = _plan(repo, "| 1 | x | `task_completed` | src/loop.py:1 |\n")
    r = _run(plan)
    assert r.returncode == 0, r.stdout
    assert "drifted" in r.stdout and "warn" in r.stdout  # the warn line is emitted


def test_symbol_genuinely_absent_fails(tmp_path):
    # A symbol that appears nowhere in the file is a real, still-failing error.
    repo = _repo(tmp_path)
    plan = _plan(repo, "| 1 | x | `never_appears_anywhere` | src/loop.py:1 |\n")
    r = _run(plan)
    assert r.returncode == 1 and "not found in" in r.stdout


def test_no_symbol_out_of_range_fails(tmp_path):
    # No symbol to anchor on + out-of-range line → still an error (nothing to resolve against).
    repo = _repo(tmp_path)
    plan = _plan(repo, "| 1 | x |  | src/loop.py:999 |\n")
    r = _run(plan)
    assert r.returncode == 1 and "out of range" in r.stdout


def test_no_symbol_in_range_passes(tmp_path):
    # No symbol + in-range line passes unchanged (the line is the only check).
    repo = _repo(tmp_path)
    plan = _plan(repo, "| 1 | x |  | src/loop.py:5 |\n")
    r = _run(plan)
    assert r.returncode == 0, r.stdout


def test_fix_repoints_unambiguous_drift(tmp_path):
    # --fix re-points a drifted, single-occurrence citation, in place, per-row.
    repo = _repo(tmp_path)
    plan = _plan(repo, "| 1 | x | `task_completed` | src/loop.py:1 |\n")
    r = _run("--fix", plan)
    assert r.returncode == 0, r.stdout
    assert "re-pointed 1" in r.stdout
    assert "src/loop.py:11" in plan.read_text()  # 1 → 11, the real line
    r2 = _run(plan)  # now precise — no drift
    assert r2.returncode == 0 and "drifted" not in r2.stdout


def test_ambiguous_drift_warns_and_fix_leaves_it(tmp_path):
    # A symbol with multiple occurrences is ambiguous → warns, and --fix does NOT rewrite it.
    repo = _repo(tmp_path)
    (repo / "src" / "dup.py").write_text(
        "\n".join(["x"] * 4 + ["dup_sym"] + ["x"] * 10 + ["dup_sym"]) + "\n"
    )
    plan = _plan(repo, "| 1 | x | `dup_sym` | src/dup.py:1 |\n")
    before = plan.read_text()
    r = _run("--fix", plan)
    assert r.returncode == 0 and "re-pointed" not in r.stdout
    assert plan.read_text() == before  # unchanged
    r2 = _run(plan)
    assert r2.returncode == 0 and "drifted" in r2.stdout


def test_unverified_row_fails(tmp_path):
    repo = _repo(tmp_path)
    plan = _plan(repo, "| 1 | x | `foo` | UNVERIFIED |\n")
    r = _run(plan)
    assert r.returncode == 1 and "UNVERIFIED" in r.stdout


def test_empty_ledger_fails(tmp_path):
    repo = _repo(tmp_path)
    plan = _plan(repo, "")
    r = _run(plan)
    assert r.returncode == 1 and "no rows" in r.stdout


REVIEW_SINGLE_ENTRY = "## Review log\n\n### Pass 1 - 2026-06-07\n- only one pass.\n"
REVIEW_NO_INDEP = "## Review log\n\n### Pass 1 - 2026-06-07\n- self.\n\n### Pass 2 - 2026-06-07\n- self again, no new findings.\n"
REVIEW_NOT_GREEN = (
    "## Review log\n\n### Pass 1 - 2026-06-07\n- self.\n\n"
    "### Pass 2 - 2026-06-07 - independent\n- found a bug, unfixed.\n"
)


def test_fewer_than_two_passes_fails(tmp_path):
    repo = _repo(tmp_path)
    plan = _plan(repo, GOOD_ROW, review=REVIEW_SINGLE_ENTRY)
    r = _run(plan)
    assert r.returncode == 1 and "at least two" in r.stdout


def test_no_independent_pass_fails(tmp_path):
    repo = _repo(tmp_path)
    plan = _plan(repo, GOOD_ROW, review=REVIEW_NO_INDEP)
    r = _run(plan)
    assert r.returncode == 1 and "independent" in r.stdout


def test_final_pass_not_green_fails(tmp_path):
    repo = _repo(tmp_path)
    plan = _plan(repo, GOOD_ROW, review=REVIEW_NOT_GREEN)
    r = _run(plan)
    assert r.returncode == 1 and "zero-findings" in r.stdout


def test_full_valid_plan_passes(tmp_path):
    repo = _repo(tmp_path)
    plan = _plan(repo, GOOD_ROW)
    r = _run(plan)
    assert r.returncode == 0, r.stdout


def test_non_plan_markdown_skipped(tmp_path):
    repo = _repo(tmp_path)
    p = repo / "PLAN-README.md"
    p.write_text("# just notes\n\nNo ledger, no review log here.\n")
    r = _run(p)
    assert r.returncode == 0 and "ok" in r.stdout


def test_missing_review_when_ledger_present_fails(tmp_path):
    repo = _repo(tmp_path)
    p = repo / "PLAN-002.md"
    p.write_text(LEDGER_HEADER + GOOD_ROW)
    r = _run(p)
    assert r.returncode == 1 and "Review log" in r.stdout


# --- Improvement 1: robust green-final detection ---


def _review(final_line: str) -> str:
    return f"## Review log\n\n### Pass 1 - 2026-06-07\n- self.\n\n### Pass 2 - 2026-06-07 - independent\n- {final_line}\n"


def test_green_accepts_load_bearing_phrase(tmp_path):
    # the exact false-negative we hit: "no load-bearing findings" must pass
    repo = _repo(tmp_path)
    plan = _plan(repo, GOOD_ROW, review=_review("No load-bearing findings. Ready."))
    r = _run(plan)
    assert r.returncode == 0, r.stdout


def test_green_accepts_explicit_result_marker(tmp_path):
    # an explicit Result: ready marker passes even without a "findings" phrase
    repo = _repo(tmp_path)
    plan = _plan(repo, GOOD_ROW, review=_review("**Result:** ready"))
    r = _run(plan)
    assert r.returncode == 0, r.stdout


def test_green_still_rejects_open_finding(tmp_path):
    repo = _repo(tmp_path)
    plan = _plan(repo, GOOD_ROW, review=_review("found an unfixed bug; not ready"))
    r = _run(plan)
    assert r.returncode == 1 and "zero-findings" in r.stdout


def test_green_does_not_falsematch_no_fix_for_findings(tmp_path):
    # the broadened matcher must NOT mark a pass with open findings green
    repo = _repo(tmp_path)
    plan = _plan(repo, GOOD_ROW, review=_review("no fix for these findings yet"))
    r = _run(plan)
    assert r.returncode == 1 and "zero-findings" in r.stdout


# --- Improvement 2: cross-repo citation support (--root) ---


def _cross_repo(tmp_path):
    # parent/repo (the plan's repo, has .git) + parent/sib (a sibling repo)
    repo = _repo(tmp_path / "repo")
    sib = tmp_path / "sib"
    sib.mkdir()
    (sib / "contract.yaml").write_text("kind: contract\n")
    plan = _plan(repo, "| 1 | sibling contract | `contract` | sib/contract.yaml:1 |\n")
    return plan


def test_cross_repo_citation_fails_without_root(tmp_path):
    plan = _cross_repo(tmp_path)  # repo_root=parent/repo; repo/sib does not exist
    r = _run(plan)
    assert r.returncode == 1 and "does not exist" in r.stdout


def test_cross_repo_citation_resolves_with_root(tmp_path):
    plan = _cross_repo(tmp_path)
    r = _run("--root", tmp_path, plan)  # parent/sib/contract.yaml resolves
    assert r.returncode == 0, r.stdout + r.stderr


# --- Improvement 3: positive output + --init ---


def test_success_prints_verified_count(tmp_path):
    repo = _repo(tmp_path)
    plan = _plan(repo, GOOD_ROW)
    r = _run(plan)
    assert r.returncode == 0
    assert "verified 1" in r.stdout and "pass" in r.stdout


def test_init_scaffolds_sections(tmp_path):
    repo = _repo(tmp_path)
    p = repo / "PLAN-007_new.md"
    p.write_text("# New plan\n\nSome body.\n")
    r = _run("--init", p)
    assert r.returncode == 0
    text = p.read_text()
    assert "## Claim ledger" in text and "## Review log" in text


def test_init_is_idempotent(tmp_path):
    repo = _repo(tmp_path)
    plan = _plan(repo, GOOD_ROW)  # already has both sections
    before = plan.read_text()
    r = _run("--init", plan)
    assert r.returncode == 0
    assert plan.read_text() == before  # unchanged


def test_init_adds_ledger_without_duplicating_review(tmp_path):
    # plan has a Review log (with real passes) but no ledger → add ledger only,
    # keep the single existing Review log and its content
    repo = _repo(tmp_path)
    p = repo / "PLAN-008_x.md"
    p.write_text("# Plan\n\n" + REVIEW_OK)
    r = _run("--init", p)
    assert r.returncode == 0
    text = p.read_text()
    assert "## Claim ledger" in text
    assert text.count("## Review log") == 1  # not duplicated
    assert "no new findings" in text  # author's existing pass preserved


def test_init_adds_review_when_only_ledger(tmp_path):
    repo = _repo(tmp_path)
    p = repo / "PLAN-009_x.md"
    p.write_text(LEDGER_HEADER + GOOD_ROW)  # ledger, no review log
    r = _run("--init", p)
    assert r.returncode == 0
    text = p.read_text()
    assert "## Review log" in text
    assert text.count("## Claim ledger") == 1  # not duplicated


def test_ledger_row_is_reported_by_its_hash_column_not_its_position(tmp_path):
    """A split ledger is not contiguous 1..N, and the `#` column is what authors cite.

    Reporting the position is a second numbering system for one table: a warning reading
    `ledger row 2` would name the row whose `#` column says 52, and every in-text
    "ledger row N" reference in a plan uses the `#` column.
    """
    repo = _repo(tmp_path)
    plan = _plan(
        repo,
        "| 51 | first | `task_completed` | src/loop.py:11 |\n"
        "| 52 | second | `absent_symbol` | src/loop.py:3 |\n",
    )
    r = _run(plan)
    assert r.returncode == 1
    assert "ledger row 52:" in r.stdout, r.stdout
    # POSITIVE CONTROL. Without it this passes against a gate that labels every row 52,
    # and against one that happens to print the string anywhere for any reason.
    assert "ledger row 2:" not in r.stdout, r.stdout


def test_a_table_without_a_hash_column_still_reports_by_position(tmp_path):
    """The fallback, asserted rather than assumed.

    A table declaring no `#` column has no author-visible numbering to honour, so position is
    the only label available — and that path must not regress while the other one changes.
    """
    repo = _repo(tmp_path)
    plan = repo / "PLAN-002_x.md"
    plan.write_text(
        "## Claim ledger\n\n| Claim | Symbol | Citation |\n|---|---|---|\n"
        "| only row | `absent_symbol` | src/loop.py:3 |\n\n" + REVIEW_OK
    )
    r = _run(plan)
    assert r.returncode == 1
    # ROW **2**, NOT ROW 1, AND THE DIFFERENCE IS THE POINT. Header detection keys on the first
    # cell being `#`/`no`/`no.`, so a table with no `#` column has its header parsed as a DATA
    # row — pre-existing behaviour, unrelated to the `#`-column label, and the reason an
    # assertion on "ledger row 1" here would pass against the HEADER's own error rather than
    # against the fallback under test.
    assert "ledger row 2: symbol 'absent_symbol' not found" in r.stdout, r.stdout


# --- PROBE: the claim state for something that cannot be settled from source ---
#
# WHY THIS EXISTS. Before it, a ledger row had two options: a real citation, or
# UNVERIFIED (fatal). A claim whose answer is a LIVE fact — a server-side
# setting, an API behaviour, a runtime observation — fits neither, so authors
# wrote prose instead. Measured consequence: one plan answered the same
# unmeasurable question three different ways across three review passes, each
# fold retracting the last. PROBE gives that claim somewhere legitimate to sit.
#
# It is deliberately NOT a free pass, and these tests are the teeth.


PHASES = "\n## Phases\n\n### Phase A\n### Phase B\n"


def test_probe_with_command_and_blocks_passes(tmp_path):
    repo = _repo(tmp_path)
    row = "| 1 | the bypass mechanism — blocks Phase B | `n/a` | PROBE: gh api repos/o/r/rulesets |\n"
    r = _run(_plan(repo, row, review=REVIEW_OK + PHASES))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "1 probe(s)" in r.stdout, r.stdout


def test_probe_without_command_fails(tmp_path):
    # Otherwise "PROBE" is a way to dodge a citation you simply did not look up.
    repo = _repo(tmp_path)
    row = "| 1 | the bypass mechanism — blocks Phase B | `n/a` | PROBE |\n"
    r = _run(_plan(repo, row))
    assert r.returncode == 1
    assert "PROBE without a command" in r.stdout, r.stdout


def test_probe_that_does_not_say_what_it_blocks_fails(tmp_path):
    # An unmeasured claim that names no gated phase reads as merely unfinished,
    # which is how it gets folded into prose and guessed at.
    repo = _repo(tmp_path)
    row = "| 1 | the bypass mechanism is unclear | `n/a` | PROBE: gh api repos/o/r/rulesets |\n"
    r = _run(_plan(repo, row))
    assert r.returncode == 1
    assert "does not say what it BLOCKS" in r.stdout, r.stdout


def test_probe_is_not_treated_as_unverified(tmp_path):
    # The distinction is the whole point: UNVERIFIED means "you did not look";
    # PROBE means "looking at source cannot answer this".
    repo = _repo(tmp_path)
    row = "| 1 | live protection state — blocks Phase C | `n/a` | PROBE: gh api repos/o/r/branches/main/protection |\n"
    r = _run(_plan(repo, row))
    assert "UNVERIFIED" not in r.stdout, r.stdout


def test_probe_count_is_reported_so_growth_is_visible(tmp_path):
    repo = _repo(tmp_path)
    rows = (
        GOOD_ROW
        + "| 2 | a — blocks Phase A | `n/a` | PROBE: cmd one |\n"
        + "| 3 | b — blocks Phase B | `n/a` | PROBE: cmd two |\n"
    )
    r = _run(_plan(repo, rows, review=REVIEW_OK + PHASES))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "3 citation(s)" in r.stdout and "2 probe(s)" in r.stdout, r.stdout


def test_probe_blocking_a_phase_that_does_not_exist_fails(tmp_path):
    # THE AMENDMENT. A probe is admissible because it blocks a NAMED phase
    # rather than the plan — which only holds while that phase exists. Measured
    # on this rule's own first use: a scope cut deleted the named phase and left
    # the probe pointing at empty space, reading as instrumented while blocking
    # no work. Requiring a phase NAME was not enough; it must RESOLVE.
    repo = _repo(tmp_path)
    row = "| 1 | the bypass — blocks Phase Q | `n/a` | PROBE: gh api repos/o/r/rulesets |\n"
    r = _run(_plan(repo, row, review=REVIEW_OK + PHASES))
    assert r.returncode == 1
    assert "no such phase exists" in r.stdout.lower(), r.stdout


def test_probe_blocking_a_phase_id_resolves(tmp_path):
    # Phase IDs (B1, B2b) are as valid as "Phase C" and are the commoner form.
    repo = _repo(tmp_path)
    row = "| 1 | the bypass — blocks B1 | `n/a` | PROBE: gh api repos/o/r/rulesets |\n"
    body = REVIEW_OK + "\n## Phases\n\n- **B1. probe, then write**\n"
    r = _run(_plan(repo, row, review=body))
    assert r.returncode == 0, r.stdout + r.stderr


def test_absolute_citation_is_rejected_not_resolved(tmp_path):
    # An absolute citation would otherwise open files outside every root,
    # turning the gate into a file-existence oracle over PR-controlled text.
    repo = _repo(tmp_path)
    outside = tmp_path / "outside.txt"
    outside.write_text("secret\n")
    row = f"| 1 | outside file | `secret` | {outside}:1 |\n"
    r = _run(_plan(repo, row))
    assert r.returncode == 1
    assert "is absolute" in r.stdout, r.stdout


def test_dotdot_escape_is_rejected(tmp_path):
    # `..` that lands outside every root resolves to nothing — same oracle,
    # spelled relatively. The outside file EXISTS, so only containment (not
    # absence) can produce this error: pre-fix this test fails with rc 0.
    repo = _repo(tmp_path / "repo")
    (tmp_path / "outside.txt").write_text("secret\n")
    row = "| 1 | outside file | `secret` | ../outside.txt:1 |\n"
    r = _run(_plan(repo, row))
    assert r.returncode == 1
    assert "does not exist under any root" in r.stdout, r.stdout


def test_dotdot_contained_in_root_still_resolves(tmp_path):
    # Containment is judged by landing spot, not spelling: `sub/../x` inside
    # the root is a real citation and must keep working.
    repo = _repo(tmp_path)
    (repo / "sub").mkdir()
    row = "| 1 | completion is logged | `task_completed` | sub/../src/loop.py:11 |\n"
    r = _run(_plan(repo, row))
    assert r.returncode == 0, r.stdout + r.stderr


def test_single_cell_probe_row_errors_instead_of_crashing(tmp_path):
    # A one-cell PROBE row has no claim cell; the gate must report it, not
    # raise IndexError (which exits 1 by accident with a traceback).
    repo = _repo(tmp_path)
    plan = repo / "PLAN-002_probe.md"
    plan.write_text(
        "## Claim ledger\n\n| Citation |\n|----------|\n"
        "| PROBE: curl example.com |\n\n" + REVIEW_OK
    )
    r = _run(plan)
    assert r.returncode == 1
    assert "needs claim + citation cells" in r.stdout, r.stdout
    assert "Traceback" not in r.stdout + r.stderr
