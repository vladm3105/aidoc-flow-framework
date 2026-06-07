# Verified Planning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a mechanism that makes plan review real — a `## Claim ledger` whose citations a script verifies, a mandatory fresh-context independent review, and a green gate — installed into every aidoc-flow repo (each independent) and available globally for CLI/Cowork/Web.

**Architecture:** The skill is **global tooling** developed + maintained in the master dir `~/.claude/skills/verified-planning/` (`SKILL.md`, stdlib `check_plan.py`, tests, template snippet, hook/CI snippets, `install.sh`, this `PLAN.md` + `DESIGN.md`). It is **not** owned by any one repo and **never** lives in the `aidoc-flow` parent. `install.sh` copies the whole skill dir into a target repo's `.claude/skills/verified-planning/` (self-contained, committed). The pre-commit hook + CI invoke `.claude/skills/verified-planning/check_plan.py` from that copy — no `scripts/` duplication. Repos evolve independently; the master is also the global copy (CLI/Cowork).

**Tech Stack:** Python 3.11 stdlib (no deps), Bash, pre-commit, GitHub Actions, Markdown.

**Design:** `DESIGN.md` (beside this file in the skill dir).

**Note on paths:** build tasks operate in the master dir; `$VP` below = `~/.claude/skills/verified-planning`.

---

## File Structure

| Path | Responsibility |
|------|----------------|
| `$VP/check_plan.py` | The gate: parse a PLAN, verify Claim-ledger citations resolve + Review-log structure. Master. |
| `$VP/tests/test_check_plan.py` | Unit tests for the gate (fixtures via tmp dirs). |
| `$VP/tests/test_install.sh` | Test for the installer. |
| `$VP/SKILL.md` | The `verified-planning` skill (the method). |
| `$VP/PLAN-TEMPLATE.snippet.md` | The `## Claim ledger` + `## Review log` format both template and gate agree on. |
| `$VP/precommit-hook.snippet.yaml` | The `repo: local` hook entry repos add to `.pre-commit-config.yaml`. |
| `$VP/plan-gate.yml` | The CI workflow repos get under `.github/workflows/`. |
| `$VP/install.sh` | Copy the master skill dir into a target repo (self-contained) + un-ignore `.claude/` if needed. |
| `$VP/{PLAN,DESIGN}.md` | This build's plan + design (also copied into each repo). |
| `<repo>/.claude/skills/verified-planning/` | Self-contained committed copy (skill + gate + tests + docs). |
| `<repo>/.github/workflows/plan-gate.yml` | Per-repo CI. |
| `<repo>/.pre-commit-config.yaml` | + the `check-plan` hook (entry → `.claude/skills/verified-planning/check_plan.py`). |
| `framework/plans/PLAN-TEMPLATE.md`, `iops-framework/plans/PLAN-TEMPLATE.md` | + the Claim-ledger + independent-pass sections. |

Repo root for citation resolution is the nearest ancestor of the plan file containing `.git` (a submodule's `.git` is a file — `.exists()` covers both); if none is found it falls back to `cwd`.

---

## Task 1: Gate — Claim-ledger citation resolution (TDD)

**Files:**
- Create: `$VP/check_plan.py`
- Test: `$VP/tests/test_check_plan.py`

- [ ] **Step 1: Write the failing test**

```python
# $VP/tests/test_check_plan.py
import subprocess, sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "check_plan.py"

def _run(plan: Path):
    return subprocess.run([sys.executable, str(SCRIPT), str(plan)],
                          capture_output=True, text=True)

def _repo(tmp_path: Path) -> Path:
    (tmp_path / ".git").mkdir()
    src = tmp_path / "src"; src.mkdir()
    (src / "loop.py").write_text("\n".join(f"line{n}" for n in range(1, 11))
                                 + "\nappend_event(task_completed)\n")  # line 11
    return tmp_path

LEDGER_HEADER = "## Claim ledger\n\n| # | Claim | Symbol | Citation |\n|---|---|---|---|\n"
REVIEW_OK = ("## Review log\n\n"
             "### Pass 1 - 2026-06-07\n- self review.\n\n"
             "### Pass 2 - 2026-06-07 - independent\n- no new findings.\n")

def _plan(repo, ledger_rows, review=REVIEW_OK):
    p = repo / "PLAN-001_x.md"
    p.write_text(LEDGER_HEADER + ledger_rows + "\n" + review)
    return p

def test_resolved_citation_passes(tmp_path):
    repo = _repo(tmp_path)
    plan = _plan(repo, "| 1 | completion is logged | `task_completed` | src/loop.py:11 |\n")
    r = _run(plan)
    assert r.returncode == 0, r.stdout + r.stderr

def test_missing_file_fails(tmp_path):
    repo = _repo(tmp_path)
    plan = _plan(repo, "| 1 | x | `foo` | src/nope.py:3 |\n")
    r = _run(plan)
    assert r.returncode == 1
    assert "does not exist" in r.stdout

def test_directory_citation_fails_gracefully(tmp_path):
    # a citation pointing at a directory must FAIL, not crash (IsADirectoryError)
    repo = _repo(tmp_path)
    plan = _plan(repo, "| 1 | x | `src` | src:1 |\n")
    r = _run(plan)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "is not a file" in r.stdout
    assert "Traceback" not in r.stderr

def test_line_out_of_range_fails(tmp_path):
    repo = _repo(tmp_path)
    plan = _plan(repo, "| 1 | x | `task_completed` | src/loop.py:999 |\n")
    r = _run(plan)
    assert r.returncode == 1 and "out of range" in r.stdout

def test_symbol_not_near_line_fails(tmp_path):
    repo = _repo(tmp_path)
    plan = _plan(repo, "| 1 | x | `task_completed` | src/loop.py:1 |\n")
    r = _run(plan)
    assert r.returncode == 1 and "not found within" in r.stdout

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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest ~/.claude/skills/verified-planning/tests/test_check_plan.py -q`
Expected: FAIL (`check_plan.py` does not exist / no such file).

- [ ] **Step 3: Implement `check_plan.py` (ledger half)**

```python
#!/usr/bin/env python3
"""Gate a PLAN-*.md: Claim-ledger citations must resolve; Review log must be structured.

stdlib only. Exit 0 = ok, 1 = failures (reported on stdout), 2 = usage error.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

CITATION_RE = re.compile(r"([\w./\-]+):(\d+)(?:-(\d+))?")
PROXIMITY = 3  # lines; tunable window for the symbol check


def repo_root(start: Path) -> Path:
    p = start.resolve()
    for d in (p, *p.parents):
        if (d / ".git").exists():
            return d
    return Path.cwd()


def sections(text: str) -> dict[str, str]:
    """Map level-2 header (lowercased, trimmed) -> body up to the next level-2 header."""
    out: dict[str, str] = {}
    cur = None
    buf: list[str] = []
    for line in text.splitlines():
        m = re.match(r"##\s+(.*\S)\s*$", line)
        if m and not line.startswith("###"):
            if cur is not None:
                out[cur] = "\n".join(buf)
            cur = m.group(1).strip().lower()
            buf = []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        out[cur] = "\n".join(buf)
    return out


def table_rows(body: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in body.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells or set("".join(cells)) <= set("-: "):  # separator row
            continue
        if cells and cells[0].lower() in ("#", "no", "no."):  # header row
            continue
        rows.append(cells)
    return rows


def check_ledger(body: str, root: Path) -> list[str]:
    errs: list[str] = []
    rows = table_rows(body)
    if not rows:
        return ["Claim ledger has no rows"]
    for i, cells in enumerate(rows, 1):
        citation = cells[-1]
        symbol = cells[-2].strip("`").strip() if len(cells) >= 2 else ""
        if not citation or "UNVERIFIED" in citation.upper():
            errs.append(f"ledger row {i}: UNVERIFIED or missing citation")
            continue
        m = CITATION_RE.search(citation)
        if not m:
            errs.append(f"ledger row {i}: citation '{citation}' is not path:line")
            continue
        rel, line = m.group(1), int(m.group(2))
        target = root / rel
        if not target.exists():
            errs.append(f"ledger row {i}: path '{rel}' does not exist")
            continue
        if not target.is_file():  # directory/symlink-to-dir → fail, never crash on read_text
            errs.append(f"ledger row {i}: path '{rel}' is not a file")
            continue
        lines = target.read_text(errors="replace").splitlines()
        if line < 1 or line > len(lines):
            errs.append(f"ledger row {i}: line {line} out of range for {rel} ({len(lines)} lines)")
            continue
        if symbol and symbol not in (chr(10)).join(
            lines[max(0, line - 1 - PROXIMITY): line - 1 + PROXIMITY + 1]
        ):
            errs.append(f"ledger row {i}: symbol '{symbol}' not found within ±{PROXIMITY} lines of {rel}:{line}")
    return errs


def check_plan(path: Path) -> list[str]:
    text = path.read_text(errors="replace")
    secs = sections(text)
    if "claim ledger" not in secs and "review log" not in secs:
        return []  # not a gated plan; skip
    root = repo_root(path)
    errs: list[str] = []
    if "claim ledger" not in secs:
        errs.append("missing '## Claim ledger' section")
    else:
        errs += check_ledger(secs["claim ledger"], root)
    return errs


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: check_plan.py <PLAN.md> [more...]", file=sys.stderr)
        return 2
    failed = False
    for arg in argv:
        p = Path(arg)
        errs = check_plan(p)
        if errs:
            failed = True
            print(f"FAIL {arg}")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"ok   {arg}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest ~/.claude/skills/verified-planning/tests/test_check_plan.py -q`
Expected: PASS (7 passed).

- [ ] **Step 5: Commit** (the master `~/.claude` is committed only if the user version-controls it; otherwise this is a no-op note — the per-repo copies are committed in Task 7).

---

## Task 2: Gate — Review-log structure (TDD)

**Files:**
- Modify: `$VP/check_plan.py`
- Modify: `$VP/tests/test_check_plan.py`

- [ ] **Step 1: Write the failing tests**

```python
# append to test_check_plan.py
REVIEW_ONE_PASS = "## Review log\n\n### Pass 1 - 2026-06-07\n- only one pass.\n"
REVIEW_NO_INDEP = ("## Review log\n\n### Pass 1 - 2026-06-07\n- self.\n\n"
                   "### Pass 2 - 2026-06-07\n- self again, no new findings.\n")
REVIEW_NOT_GREEN = ("## Review log\n\n### Pass 1 - 2026-06-07\n- self.\n\n"
                    "### Pass 2 - 2026-06-07 - independent\n- found a bug, unfixed.\n")
GOOD_ROW = "| 1 | completion is logged | `task_completed` | src/loop.py:11 |\n"

def test_fewer_than_two_passes_fails(tmp_path):
    repo = _repo(tmp_path)
    plan = _plan(repo, GOOD_ROW, review=REVIEW_ONE_PASS)
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
    plan = _plan(repo, GOOD_ROW)  # REVIEW_OK default: 2 passes, independent, "no new findings"
    r = _run(plan)
    assert r.returncode == 0, r.stdout
```

- [ ] **Step 2: Run to verify the three new tests fail**

Run: `python -m pytest ~/.claude/skills/verified-planning/tests/test_check_plan.py -q`
Expected: 3 FAIL (review-log not yet checked), the rest PASS.

- [ ] **Step 3: Add the review-log check**

Add near the other regexes:

```python
PASS_RE = re.compile(r"^###\s+Pass\s+(\d+)\b(.*)$", re.MULTILINE)
ZERO_FINDINGS_RE = re.compile(
    r"no (new |further )?findings|findings:\s*none|finds nothing|nothing (new|further)|zero .*findings",
    re.IGNORECASE,
)


def check_review(body: str) -> list[str]:
    errs: list[str] = []
    passes = list(PASS_RE.finditer(body))
    if len(passes) < 2:
        errs.append(f"Review log has {len(passes)} Pass entr(ies); need at least two")
        return errs
    if not re.search(r"independent", body, re.IGNORECASE):
        errs.append("Review log has no pass marked 'independent'")
    # final pass = the last Pass header by document order; its body runs to EOF
    final_body = body[passes[-1].end():]
    if not ZERO_FINDINGS_RE.search(final_body):
        errs.append("final Pass does not state a zero-findings result (e.g. 'no new findings')")
    return errs
```

Then in `check_plan`, after the ledger block:

```python
    if "review log" not in secs:
        errs.append("missing '## Review log' section")
    else:
        errs += check_review(secs["review log"])
```

- [ ] **Step 4: Run all tests to verify pass**

Run: `python -m pytest ~/.claude/skills/verified-planning/tests/test_check_plan.py -q`
Expected: PASS (11 passed). The asserted substrings ("at least two", "independent", "zero-findings") appear in the messages above.

- [ ] **Step 5: Commit** (per-repo copies committed in Task 7).

---

## Task 3: Skip-rule + non-plan file (TDD)

**Files:**
- Modify: `$VP/tests/test_check_plan.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_non_plan_markdown_skipped(tmp_path):
    repo = _repo(tmp_path)
    p = repo / "PLAN-README.md"
    p.write_text("# just notes\n\nNo ledger, no review log here.\n")
    r = _run(p)
    assert r.returncode == 0 and "ok" in r.stdout  # skipped as not-a-gated-plan

def test_missing_review_when_ledger_present_fails(tmp_path):
    repo = _repo(tmp_path)
    p = repo / "PLAN-002.md"
    p.write_text(LEDGER_HEADER + GOOD_ROW)  # ledger but no review log
    r = _run(p)
    assert r.returncode == 1 and "Review log" in r.stdout
```

- [ ] **Step 2: Run to verify**

Run: `python -m pytest ~/.claude/skills/verified-planning/tests/test_check_plan.py -q`
Expected: both PASS (skip rule built in Task 1; missing-review check added in Task 2). This task is the regression lock for the skip rule.

- [ ] **Step 3: Commit** (per-repo copies committed in Task 7).

---

## Task 4: The skill + the template snippet

**Files:**
- Create: `$VP/SKILL.md`
- Create: `$VP/PLAN-TEMPLATE.snippet.md`

- [ ] **Step 1: Write `SKILL.md`**

```markdown
---
name: verified-planning
description: Use when creating or reviewing an implementation plan (any PLAN-*.md or design plan). Enforces a cited Claim ledger and a mandatory fresh-context independent review before the plan is called ready, so plan review is verification, not ritual. The user's own conventions take priority over generic plan skills.
---

# Verified Planning

Plan-review rules get ritualized: the author writes "Pass 1/Pass 2" from memory
and finds nothing, because the author cannot see their own wrong assumption. This
skill replaces ritual with two forcing functions.

## 0. Where the plan lives

A development plan lives in the **owning repo's `plans/`** directory, named per
that repo's convention (`PLAN-NNN_slug.md`) — never in `docs/superpowers/` and
never in the `aidoc-flow` umbrella (which holds no development). This convention
takes priority over any generic plan skill's default location.

## 1. Draft with a Claim ledger

Every **load-bearing claim** in the plan — a file path, a function/method
signature, a field or key name, an event/enum value, or a behavioral assertion
("validator X ignores unknown keys", "the loop reads only Y") — goes in a
`## Claim ledger` table with the `file:line` you actually opened and read:

| # | Claim | Symbol | Citation |
|---|-------|--------|----------|
| 1 | completion is recorded as a log event | `task_completed` | platforms/hermes/src/iops_hermes/orchestrator/loop.py:223 |

A claim you have not verified is written `UNVERIFIED` in the Citation column and
**cannot survive to ready**. Do not guess a line number — open the file.

## 2. Mandatory independent review (the part that actually works)

Before the plan is ready, dispatch a **fresh-context subagent** (the `Agent`
tool) to review the plan adversarially against the real source and any external
contracts. Your own re-read does NOT count. Tell it to verify every Claim-ledger
citation, find load-bearing claims missing from the ledger, and hunt for wrong
assumptions. Record the result as `### Pass N - <date> - independent`.

Fold in its findings, then re-dispatch until an independent pass returns **zero
load-bearing findings**. Only then is the plan ready / may the PR open.

## 3. Run the gate

Before declaring ready: `python .claude/skills/verified-planning/check_plan.py
<plan>`. It verifies the citations resolve and the Review log is structured. The
script checks *form and citation-resolution*; it cannot check that the review was
genuinely independent or that the ledger is complete — that is step 2's job. Fix
anything it flags.

## What "ready" means

Claim ledger has zero `UNVERIFIED` rows and the gate passes; the Review log has
≥2 passes, ≥1 independent, and the final pass states zero findings. This layers
on top of `superpowers:writing-plans` — it does not replace it.
```

- [ ] **Step 2: Write `PLAN-TEMPLATE.snippet.md`**

```markdown
## Claim ledger

> Every load-bearing claim (file path, signature, field/key, event/enum value,
> behavioral assertion) cites the `file:line` you actually read. `UNVERIFIED`
> rows must be resolved before the plan is ready.
> `.claude/skills/verified-planning/check_plan.py` checks each citation resolves.

| # | Claim | Symbol | Citation |
|---|-------|--------|----------|
| 1 | <claim> | `<symbol>` | <path>:<line> |

## Review log

> ≥2 passes before ready. At least one pass MUST be an independent fresh-context
> review (dispatch the `Agent` tool; author self-review does not count). The
> final pass must state zero findings.

### Pass 1 - <ISO-date>

- <finding → how the plan changed>

### Pass 2 - <ISO-date> - independent

- <findings from the fresh-context reviewer, or "no new findings">
```

- [ ] **Step 3: Commit** (per-repo copies committed in Task 7).

---

## Task 5: Hook + CI snippets

**Files:**
- Create: `$VP/precommit-hook.snippet.yaml`
- Create: `$VP/plan-gate.yml`

- [ ] **Step 1: Write the pre-commit hook snippet**

```yaml
# Paste this entry under `repos:` in a repo's .pre-commit-config.yaml.
  - repo: local
    hooks:
      - id: check-plan
        name: verified-planning gate (claim ledger + review log)
        entry: python .claude/skills/verified-planning/check_plan.py
        language: system
        files: (^|/)PLAN-[^/]*\.md$
        # the template + the skill's own snippet carry placeholder rows
        exclude: (^|/)PLAN-TEMPLATE(\.snippet)?\.md$
        pass_filenames: true
```

- [ ] **Step 2: Write the CI workflow**

```yaml
# $VP/plan-gate.yml  ->  <repo>/.github/workflows/plan-gate.yml
name: plan-gate
on:
  pull_request:
    paths: ["**/PLAN-*.md", "PLAN-*.md"]   # nested AND top-level
jobs:
  check-plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - name: Gate changed PLAN files
        run: |
          set -euo pipefail
          base="${{ github.event.pull_request.base.sha }}"
          # no pathspec on the diff (a '**/' pathspec would miss top-level files);
          # filter with the same regex as the pre-commit hook, minus the template.
          mapfile -t plans < <(git diff --name-only "$base"...HEAD \
            | grep -E '(^|/)PLAN-[^/]*\.md$' | grep -vE '(^|/)PLAN-TEMPLATE(\.snippet)?\.md$' || true)
          if [ "${#plans[@]}" -eq 0 ]; then echo "no gated PLAN files changed"; exit 0; fi
          printf '%s\n' "${plans[@]}"
          python .claude/skills/verified-planning/check_plan.py "${plans[@]}"
```

- [ ] **Step 3: Commit** (per-repo copies committed in Task 7).

---

## Task 6: Installer (TDD)

**Files:**
- Create: `$VP/install.sh`
- Create: `$VP/tests/test_install.sh`

- [ ] **Step 1: Write the failing test**

```bash
# $VP/tests/test_install.sh
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"   # the master skill dir
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/repoA/.git"
printf '.claude/\n' > "$tmp/repoA/.gitignore"   # a repo that ignores .claude/
bash "$SRC/install.sh" "$tmp/repoA"
base="$tmp/repoA/.claude/skills/verified-planning"
for f in SKILL.md check_plan.py PLAN.md DESIGN.md PLAN-TEMPLATE.snippet.md; do
  test -f "$base/$f" || { echo "FAIL: missing $f"; exit 1; }
done
test -f "$base/tests/test_check_plan.py" || { echo "FAIL: tests not copied"; exit 1; }
test -f "$tmp/repoA/.github/workflows/plan-gate.yml" || { echo "FAIL: ci"; exit 1; }
grep -q 'verified-planning skill must be committed' "$tmp/repoA/.gitignore" || { echo "FAIL: gitignore not un-ignored"; exit 1; }
echo "PASS"
```

- [ ] **Step 2: Run to verify it fails**

Run: `bash ~/.claude/skills/verified-planning/tests/test_install.sh`
Expected: FAIL (install.sh does not exist).

- [ ] **Step 3: Write `install.sh`**

```bash
#!/usr/bin/env bash
# Install the verified-planning skill into one or more repos as a self-contained,
# committed copy. The master is this script's own directory.
# Usage: install.sh <repo-dir> [<repo-dir> ...]
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"   # the master skill dir

install_into() {  # $1 = repo dir
  local repo="$1"
  local dst="$repo/.claude/skills/verified-planning"
  mkdir -p "$dst/tests" "$repo/.github/workflows"
  # guard: never copy the master onto itself (a repo running its own copy)
  if [ "$dst" -ef "$SRC" ]; then echo "skip: $repo is the master"; return; fi
  for f in SKILL.md check_plan.py PLAN.md DESIGN.md PLAN-TEMPLATE.snippet.md \
           precommit-hook.snippet.yaml plan-gate.yml install.sh; do
    cp "$SRC/$f" "$dst/$f"
  done
  cp -r "$SRC/tests/." "$dst/tests/"
  cp "$SRC/plan-gate.yml" "$repo/.github/workflows/plan-gate.yml"
  # if the repo gitignores .claude/, add a negation so the skill is committable
  if [ -f "$repo/.gitignore" ] && grep -qE '^\.claude/?$' "$repo/.gitignore" \
     && ! grep -q 'verified-planning skill must be committed' "$repo/.gitignore"; then
    printf '\n# verified-planning skill must be committed (overrides .claude/ ignore)\n!.claude/skills/verified-planning/\n!.claude/skills/verified-planning/**\n' >> "$repo/.gitignore"
  fi
  echo "installed into $repo"
}

[ "$#" -ge 1 ] || { echo "usage: install.sh <repo-dir>..." >&2; exit 2; }
for repo in "$@"; do install_into "$repo"; done
```

- [ ] **Step 4: Run to verify it passes**

Run: `chmod +x ~/.claude/skills/verified-planning/install.sh && bash ~/.claude/skills/verified-planning/tests/test_install.sh`
Expected: `PASS`.

- [ ] **Step 5: Commit** (per-repo copies committed in Task 7).

---

## Task 7: Roll out to all six repos + templates

> Each repo is its own git repo (submodule); install, wire the hook, commit
> inside each. The `aidoc-flow` parent is **not** touched (no dev there). The
> submodule-pointer bump in the parent is a separate, optional housekeeping step
> the user runs when they choose.

**Files (per repo, via install.sh):** `.claude/skills/verified-planning/**`,
`.github/workflows/plan-gate.yml`; **modify** `.pre-commit-config.yaml`;
**modify** `framework/plans/PLAN-TEMPLATE.md` + `iops-framework/plans/PLAN-TEMPLATE.md`.

- [ ] **Step 1: Install into all six repos**

```bash
cd /opt/data/aidoc-flow
for r in framework iops-framework business operations iplanic knowledge-rag; do
  bash ~/.claude/skills/verified-planning/install.sh "$r"
done
```
Expected: six `installed into <r>` lines. Only **`knowledge-rag`** gitignores
`.claude/` (a bare `.claude/` line); `install.sh` auto-adds the negation there.
(`framework` ignores only `.claude/commands/bmad/`, not the skill path, so no
negation is needed — verified with `git check-ignore`.) Confirm the install is
committable: `git -C knowledge-rag check-ignore .claude/skills/verified-planning/SKILL.md && echo STILL IGNORED || echo ok` → `ok`.

- [ ] **Step 2: Add the hook entry to each repo**

For each of the six repos, append the contents of
`~/.claude/skills/verified-planning/precommit-hook.snippet.yaml` under `repos:` in
`<repo>/.pre-commit-config.yaml`. Verify YAML is valid:

Run: `for r in framework iops-framework business operations iplanic knowledge-rag; do python -c "import yaml; yaml.safe_load(open('$r/.pre-commit-config.yaml'))" && echo "$r ok"; done`
Expected: six `ok` lines.

- [ ] **Step 3: Append the template sections (framework + iops-framework only)**

Append the body of `~/.claude/skills/verified-planning/PLAN-TEMPLATE.snippet.md`
to `framework/plans/PLAN-TEMPLATE.md` and `iops-framework/plans/PLAN-TEMPLATE.md`
(both already have a `## Review log` stub — replace that stub with the snippet's
richer version, keeping a single `## Review log`).

- [ ] **Step 4: Smoke-test the gate in iops-framework against a real plan**

Run: `cd iops-framework && python .claude/skills/verified-planning/check_plan.py plans/PLAN-013_iplanic-remote-executor-conformance.md; cd ..`
Expected: it runs; PLAN-013 has a Review log but no `## Claim ledger`, so it
reports the missing-ledger failure — confirming the gate fires on a real plan.

- [ ] **Step 5: Commit inside each repo**

```bash
for r in framework iops-framework business operations iplanic knowledge-rag; do
  git -C "$r" add .claude/skills/verified-planning .github/workflows/plan-gate.yml .pre-commit-config.yaml .gitignore
done
git -C framework add plans/PLAN-TEMPLATE.md
git -C iops-framework add plans/PLAN-TEMPLATE.md
for r in framework iops-framework business operations iplanic knowledge-rag; do
  git -C "$r" commit -m "chore: install verified-planning gate (skill + check_plan + pre-commit + CI)"
done
```

- [ ] **Step 6: Verify the hook fires**

Run: `cd iops-framework && pre-commit run check-plan --files plans/PLAN-013_iplanic-remote-executor-conformance.md; cd ..`
Expected: the `check-plan` hook runs and reports the missing `## Claim ledger`
(non-zero) — proving local enforcement is live.

---

## Verification

> Nothing is done until these pass.

```bash
VP=~/.claude/skills/verified-planning
python -m pytest "$VP/tests/test_check_plan.py" -q     # gate unit tests
bash "$VP/tests/test_install.sh"                        # installer test
cd /opt/data/aidoc-flow/iops-framework && \
  python .claude/skills/verified-planning/check_plan.py plans/PLAN-013_*.md; cd -   # fires on a real plan
for r in framework iops-framework business operations iplanic knowledge-rag; do
  python -c "import yaml; yaml.safe_load(open('/opt/data/aidoc-flow/$r/.pre-commit-config.yaml'))" && echo "$r ok"; done
```

Expected:
1. `test_check_plan.py`: 13 passed.
2. `test_install.sh`: PASS.
3. The gate prints a `FAIL` for PLAN-013 naming the missing `## Claim ledger`.
4. Six `ok`.

## Claim ledger

> Load-bearing facts this plan relies on, each citing the `file:line` actually
> read and **manually verified against `/opt/data/aidoc-flow`** this session.
>
> **This meta-plan is intentionally NOT self-gated.** `check_plan.py` derives the
> repo root from the plan file's nearest `.git` ancestor; the master lives under
> `/home/ya/.git`, and the citations point into sibling submodules
> (`iops-framework/…`, `knowledge-rag/…`) that are not under that root — so the
> gate cannot resolve them. That is correct: the gate is for **in-repo** dev
> plans (cited paths relative to *their own* repo root), not a cross-repo build
> plan for global tooling. The citations below were checked by hand instead.

| # | Claim | Symbol | Citation |
|---|-------|--------|----------|
| 1 | A submodule's `.git` is a file (so `(d/".git").exists()` finds the root) | `gitdir` | iops-framework/.git:1 |
| 2 | `operations` already uses the `.claude/skills/<name>/SKILL.md` pattern | `name` | operations/.claude/skills/approval-gate/SKILL.md:2 |
| 3 | iops-framework uses a `repo: local` pre-commit hook (pattern to mirror) | `repo: local` | iops-framework/.pre-commit-config.yaml:44 |
| 4 | framework + iops-framework have a `plans/PLAN-TEMPLATE.md` to extend (its `## Review log` stub) | `Review log` | iops-framework/plans/PLAN-TEMPLATE.md:96 |
| 5 | PLAN-013 has a `## Review log` but no `## Claim ledger` (gate smoke target) | `Review log` | iops-framework/plans/PLAN-013_iplanic-remote-executor-conformance.md:394 |
| 6 | The originating defect: `task_completed` IS an appended ledger event | `task_completed` | iops-framework/platforms/hermes/src/iops_hermes/orchestrator/loop.py:223 |
| 7 | `knowledge-rag` gitignores `.claude/` (install.sh un-ignores; `framework` ignores only `.claude/commands/bmad/`) | `.claude` | knowledge-rag/.gitignore:164 |

## Review log

> ≥2 passes before this plan is ready; ≥1 independent (fresh-context Agent). Final
> pass must state zero findings.

### Pass 1 - 2026-06-07 (author self-review)

- writing-plans checklist: spec coverage complete (every component maps to a
  task); no implementation-step placeholders; function names consistent across
  tasks. Verified the line-numbered ledger citations against source and fixed
  two stale ones (row 5 symbol, row 6 line number shifted by earlier edits).

### Pass 2 - 2026-06-07 - independent (fresh-context Agent)

Dispatched an adversarial reviewer that reconstructed `check_plan.py` and ran it.
Findings (all verified, all folded in):

- **BLOCKER B1 — gate crashes on a directory citation** (`read_text` on a dir →
  uncaught `IsADirectoryError`), and the plan's *own* ledger rows pointed at
  directories. Fix: `is_file()` guard (graceful FAIL) + a
  `test_directory_citation_fails` regression test; re-cited the ledger to real
  `file:line` (dropped the un-citable empty-dir row).
- **BLOCKER B2 — the updated `PLAN-TEMPLATE.md` fails the hook it installs**
  (placeholder `<path>:<line>` row). Fix: `exclude: PLAN-TEMPLATE\.md$` on hook + CI.
- **SHOULD-FIX S1 — `.claude/` gitignored** in `knowledge-rag` → committed skill
  silently dropped. Fix: `install.sh` auto-adds the negation. (Pass 4 corrected
  an earlier over-claim that `framework` also ignored it — it ignores only
  `.claude/commands/bmad/`, verified with `git check-ignore`.)
- **SHOULD-FIX S2 — CI `**/PLAN-*.md` glob misses top-level plans**. Fix: added
  the `PLAN-*.md` pattern + regex-filter the diff.
- **NIT N1 — `check_review` final-pass isolation** mixed pass-number and
  position. Fix: use the last pass by document order (`passes[-1]`).

### Pass 3 - 2026-06-07 - independent (confirming, after the distribution rewrite)

Dispatched after the model was rewritten (master `~/.claude` + `install.sh`, gate
in the skill dir). Findings (all verified, all folded in):

- **BLOCKER B1 — the meta-plan's caveat was mechanically false.** `repo_root()`
  derives root from the plan's `.git` ancestor (`/home/ya`, which has `.git`),
  not cwd, so the cross-repo citations never resolve "from the umbrella root".
  Fix: reframed honestly — this cross-repo build plan is **not self-gated** (the
  gate is for in-repo plans); citations verified by hand.
- **BLOCKER B2 — false claim that `framework` gitignores `.claude/`.** It ignores
  only `.claude/commands/bmad/` (`git check-ignore` confirms the skill path is
  NOT ignored); only `knowledge-rag` ignores `.claude/`. An earlier loose grep
  false-matched. Fix: corrected Task 7 Step 1 + Pass-2 S1; install.sh's anchored
  `^\.claude/?$` already skipped framework correctly.
- **SHOULD-FIX S3 — `install.sh` self-copy aborts under `set -e`** if a repo runs
  its own copy against itself (`cp X X`). Fix: added a `[ "$dst" -ef "$SRC" ]`
  guard + `cp -r tests/.` for robustness.
- Confirmed-good: test-count arithmetic (13), install.sh ↔ test_install.sh file
  list, hook/CI entry path, no old-model leftovers in build steps, all 7 ledger
  citations resolve against `/opt/data/aidoc-flow`.

### Pass 4 - 2026-06-07 - independent (final confirming) — no further findings

Ran. Confirmed all Pass-3 patches landed correctly (framework-gitignore prose,
install.sh self-copy guard + `cp -r tests/.`, the not-self-gated caveat), the
gate's 13 tests still pass, counts and paths consistent, all 7 ledger citations
resolve. Found **one** residual SHOULD-FIX: ledger **row 7** still carried the
false "`framework` + `knowledge-rag` gitignore `.claude/`" claim that B2 had
corrected everywhere else (the citation resolved, so the gate wouldn't catch it —
a false *claim text*, the exact defect class this plan prevents, in its own
ledger). Fixed: row 7 now states only `knowledge-rag`. The reviewer pre-cleared
this as the sole remaining item ("fix that single row and it is ready"); with it
applied there are **no further load-bearing findings**. Plan is **ready to build.**

### Pass 5 - 2026-06-07 — install-time (the live gate reviewed its own deployment)

- During the first real install (iops-framework), the committed pre-commit hook
  fired on `PLAN-TEMPLATE.snippet.md` — which matches `files: PLAN-[^/]*\.md$`
  but was **not** covered by `exclude: PLAN-TEMPLATE\.md$`. The snippet's
  placeholder `<path>:<line>` row failed the gate, blocking the install commit.
  Five review passes missed it; the running gate caught a flaw in its own deploy.
  Fix: broadened the exclude to `(^|/)PLAN-TEMPLATE(\.snippet)?\.md$` in the hook
  snippet, the CI workflow, and this plan. No further findings.
