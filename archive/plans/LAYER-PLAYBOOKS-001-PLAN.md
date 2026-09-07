# LAYER-PLAYBOOKS-001 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add per-layer per-lens playbooks (45 files) to calibrate the review-team's content-quality findings against each layer's specific failure modes, with a deterministic checklist floor and a beyond-checklist escape hatch.

**Architecture:** Engine-agnostic. Framework contract in `framework/governance/REVIEW_TEAM.md` (new §Playbooks); playbook files at `framework/playbooks/<NN>_<LAYER>/<lens>.md`. Plugin's 8 audit SKILLs load the layer-and-lens-matched playbook at fan-out time and inline its content into each lens subagent's Task brief. Synthesizer enforces a new required `findings[].check` field; missing/fabricated citations are discarded. New `verdict.playbook_coverage` surfaces which checks fired.

**Tech Stack:** YAML frontmatter, Python stdlib for tests/loader, Markdown for playbooks, existing audit SKILLs' team-mode dispatcher (already in place from BRD-RT-001 / PRD-RT-001).

**Design authority:** `plans/LAYER-PLAYBOOKS-001-DESIGN.md` (committed in ae3dd8bd).

---

## Plan structure

The plan has 12 tasks across 6 phases. Phases A–D are TDD-disciplined (test first, then implementation). Phase E is content-authoring (8 layer-tasks, each authoring 5-6 playbooks for that layer; ~45 playbooks total). Phase F is doc-of-record + live verification + landing.

| Phase | Tasks | Description |
|---|---|---|
| A. Spec | 1 | REVIEW_TEAM.md §Playbooks + `framework/VERSION` 0.13.1 → 0.14.0 |
| B. Tests-first (conformance) | 2 | Coverage + frontmatter conformance tests (FAIL until playbooks land) |
| C. Tests-first (unit) | 3 | Loader unit test + finding-check schema test |
| D. Mechanism | 4–5 | Loader helper + brief composition (8 SKILLs); synthesizer schema extension |
| E. Playbook content | 6.1–6.8 | 45 playbooks across 8 layers (one task per layer) |
| F. Lint + verify + land | 7–12 | Sync-hook extension; smoke + live acceptance; doc-of-record; two-cycle plan review; PR |

## File structure

### Created

| Path | Purpose |
|---|---|
| `framework/playbooks/01_BRD/<lens>.md` × 5 | BRD-layer playbooks (architect, business_analyst, auditor, chaos_engineer, security_engineer) |
| `framework/playbooks/02_PRD/<lens>.md` × 6 | PRD playbooks (product_owner, architect, tech_lead, chaos_engineer, security_engineer, auditor) |
| `framework/playbooks/03_EARS/<lens>.md` × 5 | EARS playbooks (requirements_specialist, tech_lead, qa_lead, chaos_engineer, security_engineer) |
| `framework/playbooks/04_BDD/<lens>.md` × 6 | BDD playbooks (qa_lead, tech_lead, chaos_engineer, security_engineer, operator, auditor) |
| `framework/playbooks/05_ADR/<lens>.md` × 6 | ADR playbooks (architect, tech_lead, chaos_engineer, security_engineer, operator, auditor) |
| `framework/playbooks/06_SPEC/<lens>.md` × 5 | SPEC playbooks (architect, tech_lead, integration_lead, chaos_engineer, security_engineer) |
| `framework/playbooks/07_TDD/<lens>.md` × 6 | TDD playbooks (qa_lead, tech_lead, chaos_engineer, security_engineer, operator, auditor) |
| `framework/playbooks/08_IPLAN/<lens>.md` × 6 | IPLAN playbooks (tech_lead, architect, operator, integration_lead, auditor, chaos_engineer) |
| `tests/conformance/test_playbook_coverage.py` | Conformance: every (layer, lens) in REVIEW_CREWS.yaml has a playbook |
| `tests/conformance/test_playbook_frontmatter.py` | Conformance: every playbook's frontmatter parses + matches REVIEW_CREWS.yaml weight |
| `tests/unit/test_playbook_loader.py` | Unit: audit SKILL helper resolves path; missing-file behavior |
| `tests/unit/test_finding_check_field.py` | Unit: synthesizer enforces `findings[].check`; discards missing/fabricated |

### Modified

| Path | What changes |
|---|---|
| `framework/governance/REVIEW_TEAM.md` | New §Playbooks section: file location, frontmatter schema, content sections, finding-citation rule |
| `framework/VERSION` | 0.13.1 → 0.14.0 (new artifact class added to framework spec) |
| `platforms/claude-code-plugin/VERSION` | Minor bump (consumes new spec) |
| `platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION` | 0.13.1 → 0.14.0 (sync hook handles, listed here for visibility) |
| `platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md` | Add `## Playbook injection` subsection in team-mode flow |
| `platforms/claude-code-plugin/skills/doc-prd-audit/SKILL.md` | Same |
| `platforms/claude-code-plugin/skills/doc-ears-audit/SKILL.md` | Same |
| `platforms/claude-code-plugin/skills/doc-bdd-audit/SKILL.md` | Same |
| `platforms/claude-code-plugin/skills/doc-adr-audit/SKILL.md` | Same |
| `platforms/claude-code-plugin/skills/doc-spec-audit/SKILL.md` | Same |
| `platforms/claude-code-plugin/skills/doc-tdd-audit/SKILL.md` | Same |
| `platforms/claude-code-plugin/skills/doc-iplan-audit/SKILL.md` | Same |
| `platforms/claude-code-plugin/agents/synthesizer.md` | `findings[].check` required-field enforcement; `verdict.playbook_coverage` emission |
| `tests/conformance/test_framework_spec_version.py` | Extend to assert every playbook's `framework_spec_version` matches `framework/VERSION` |
| `scripts/sync-version-refs.sh` | Add propagation of `framework_spec_version: "X.Y.Z"` into all 45 playbook frontmatters when `framework/VERSION` bumps |
| `CHANGELOG.md` (root) | New `[Unreleased]` entry: framework 0.13.1 → 0.14.0 (playbooks) + plugin minor (consumes) |
| `platforms/claude-code-plugin/CHANGELOG.md` | New entry for plugin version bump (playbook injection in audit SKILLs + synthesizer schema) |
| `ROADMAP.md` | Mark playbook calibration as shipped under the current phase |
| `plans/HANDOFF.md` | Update current-state narrative + next-step pointer |
| `CLAUDE.md` | Update `Current state (as of YYYY-MM-DD)` line to reference framework 0.14.0 + plugin new version |
| `docs/PARITY.md` | Update current-state row + add playbook-injection row (plugin yes / Hermes deferred) |
| `plans/HERMES-BACKLOG.md` | Add H-4 entry: Hermes playbook-injection parity (consumes framework 0.14.0+) |

---

## Phase A — Framework spec extension

### Task 1: Extend REVIEW_TEAM.md with §Playbooks; bump framework/VERSION

**Files:**

- Modify: `framework/governance/REVIEW_TEAM.md`
- Modify: `framework/VERSION` (0.13.1 → 0.14.0)
- Modify: `platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION` (sync hook handles, but verify)

- [ ] **Step 1: Read the existing REVIEW_TEAM.md to locate insertion point**

```bash
grep -n '^## ' framework/governance/REVIEW_TEAM.md
```

The new §Playbooks section goes after §"Scoring, conflicts & the gate" and before §"Resilience".

- [ ] **Step 2: Add the §Playbooks section**

Insert the following content into `framework/governance/REVIEW_TEAM.md` at the located position:

````markdown
## Playbooks

Each (layer, lens) pair has a **playbook** — a layer-specific reasoning frame plus a deterministic checklist of evidence checks. Playbooks live at `framework/playbooks/<NN>_<LAYER>/<lens>.md` (one file per lens per layer; ~45 files total across the 8 layers).

### Why

The lens names in `REVIEW_CREWS.yaml` are layer-specialized by intent (e.g., `business_analyst` at BRD vs `product_owner` at PRD vs `requirements_specialist` at EARS are three distinct reasoning modes). Without a per-layer failure-mode catalog, a generic lens agent reasons about all layers identically and misses layer-specific gaps. Playbooks supply the catalog without forking the agent.

### File location

```
framework/playbooks/
  01_BRD/architect.md
  01_BRD/business_analyst.md
  ...
  02_PRD/product_owner.md
  02_PRD/architect.md
  02_PRD/tech_lead.md
  ...
```

Layer directory is `<NN>_<LAYER>` matching the `framework/layers/` convention. Lens filename matches the persona name in `REVIEW_CREWS.yaml` (snake_case, `.md` suffix).

### Required frontmatter

```yaml
---
layer: 02_PRD                          # matches directory name exactly
lens: chaos_engineer                   # matches filename stem + REVIEW_CREWS.yaml persona name
weight: 8                              # must match REVIEW_CREWS.yaml weight for this (layer, lens)
agent: chaos-engineer                  # plugin agent name; documented per-platform binding
framework_spec_version: "0.14.0"       # must match framework/VERSION; auto-propagated by sync hook
---
```

### Required content sections

1. **Reasoning frame** — 2-3 paragraphs: what this lens uniquely sees at this layer altitude; how it differs from the same lens at adjacent layers; what this lens does NOT do (covered by other lenses).
2. **Required evidence checks** — finite list `C1`..`Cn` of deterministic checks. Each check states what to look for and the priority of a finding if the check fires.
3. **Beyond-checklist** — escape hatch for layer-specific failure modes the checklist does not cover. Finding must cite `beyond-checklist:<principle-tag>` and reference the reasoning frame.
4. **Scoring** — 0-100 rubric tied to checklist coverage and beyond-checklist density.

### Finding citation rule (binding contract)

Every finding produced by a lens MUST cite either a checklist check (`check: "C1"`) or a beyond-checklist principle (`check: "beyond-checklist:<tag>"`). The synthesizer **discards** findings without a citation or with a fabricated check id, logging the discard in `report.md`. This is the deterministic floor of the playbook contract.

### Coverage emission

The synthesizer emits `verdict.playbook_coverage` summarizing how many findings cited each check id plus a `beyond_checklist` count. A drift signal: if > 30% of findings are beyond-checklist, the playbook needs revision.
````

- [ ] **Step 3: Bump framework/VERSION**

```bash
echo "0.14.0" > framework/VERSION
cat framework/VERSION
```

Expected: `0.14.0`

- [ ] **Step 4: Verify FRAMEWORK_SPEC_VERSION will be synced by hook**

```bash
cat platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION
```

Currently `0.13.1`. The pre-commit `sync-version-refs.sh` hook propagates it automatically when we commit. Verify after commit — see post-commit `grep -c` in Step 5. The hook ALSO propagates `framework_spec_version: "0.14.0"` into 52 SKILL.md frontmatters. Playbook frontmatters are NOT yet handled by the hook — Task 11 extends the hook to cover them; until Task 11 lands, playbook authoring in Phase E must hardcode `framework_spec_version: "0.14.0"` (which is the post-bump value, so this is consistent).

- [ ] **Step 5: Commit**

```bash
git add framework/governance/REVIEW_TEAM.md framework/VERSION
env -u LD_LIBRARY_PATH git commit -m "feat(framework): add §Playbooks spec; bump 0.13.1 -> 0.14.0

Per LAYER-PLAYBOOKS-001 design: layer-specific lens playbooks at
framework/playbooks/<NN>_<LAYER>/<lens>.md with frontmatter contract,
required content sections, and finding-citation rule (every finding
cites Cn or beyond-checklist:<tag>). Synthesizer discards uncited
findings."
```

After commit, verify the sync hook updated `FRAMEWORK_SPEC_VERSION`, the 52 SKILL.md frontmatters, and other propagation targets:

```bash
git log -1 --stat | head -30
grep -c 'framework_spec_version: "0.14.0"' platforms/claude-code-plugin/skills/*/SKILL.md
```

Expected: `52` (the auto-sync did its job; this is the existing PR #99 mechanism).

---

## Phase B — Conformance tests (TDD: write first, must fail)

### Task 2: Conformance test for playbook coverage

**Files:**

- Create: `tests/conformance/test_playbook_coverage.py`

- [ ] **Step 1: Write the failing test**

Create `tests/conformance/test_playbook_coverage.py` with:

```python
"""Every (layer, lens) in REVIEW_CREWS.yaml has a playbook file."""
from __future__ import annotations
import unittest
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CREWS = REPO_ROOT / "framework" / "governance" / "REVIEW_CREWS.yaml"
PLAYBOOKS = REPO_ROOT / "framework" / "playbooks"

# Layer numbering matches framework/layers/ directory convention.
LAYER_PREFIX = {
    "BRD": "01_BRD",
    "PRD": "02_PRD",
    "EARS": "03_EARS",
    "BDD": "04_BDD",
    "ADR": "05_ADR",
    "SPEC": "06_SPEC",
    "TDD": "07_TDD",
    "IPLAN": "08_IPLAN",
}


class PlaybookCoverageTests(unittest.TestCase):
    def setUp(self):
        with CREWS.open() as f:
            self.crews = yaml.safe_load(f)

    def test_every_crew_lens_has_a_playbook_file(self):
        missing = []
        for layer_name, crew in self.crews["crews"].items():
            prefix = LAYER_PREFIX[layer_name]
            for lens in crew["review"]:
                expected = PLAYBOOKS / prefix / f"{lens}.md"
                if not expected.is_file():
                    missing.append(str(expected.relative_to(REPO_ROOT)))
        self.assertEqual(
            missing, [],
            f"Playbook coverage gap: {len(missing)} missing files.\n"
            + "\n".join(f"  - {p}" for p in missing),
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test — confirm it fails with all 45 playbooks missing**

```bash
env -u LD_LIBRARY_PATH python3 -m unittest tests.conformance.test_playbook_coverage -v 2>&1 | tail -20
```

Expected: FAIL with `Playbook coverage gap: 45 missing files.` followed by 45 paths.

- [ ] **Step 3: Commit the failing test**

```bash
git add tests/conformance/test_playbook_coverage.py
env -u LD_LIBRARY_PATH git commit -m "test(conformance): assert every (layer, lens) crew member has a playbook

Test fails with 45 missing files until Phase E authors the playbook
content. Coverage assertion is the gate against crew-vs-playbook drift."
```

### Task 3: Conformance test for playbook frontmatter

**Files:**

- Create: `tests/conformance/test_playbook_frontmatter.py`

- [ ] **Step 1: Write the failing test**

Create `tests/conformance/test_playbook_frontmatter.py`:

```python
"""Every playbook's YAML frontmatter parses + matches REVIEW_CREWS.yaml."""
from __future__ import annotations
import re
import unittest
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CREWS_PATH = REPO_ROOT / "framework" / "governance" / "REVIEW_CREWS.yaml"
VERSION_PATH = REPO_ROOT / "framework" / "VERSION"
PLAYBOOKS_DIR = REPO_ROOT / "framework" / "playbooks"

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
REQUIRED_FIELDS = {"layer", "lens", "weight", "agent", "framework_spec_version"}


def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text()
    m = FM_RE.match(text)
    if not m:
        return None
    return yaml.safe_load(m.group(1))


class PlaybookFrontmatterTests(unittest.TestCase):
    def setUp(self):
        with CREWS_PATH.open() as f:
            self.crews = yaml.safe_load(f)
        self.framework_version = VERSION_PATH.read_text().strip()
        self.playbooks = list(PLAYBOOKS_DIR.rglob("*.md")) if PLAYBOOKS_DIR.exists() else []

    def test_every_playbook_has_required_frontmatter_fields(self):
        for pb in self.playbooks:
            with self.subTest(playbook=str(pb.relative_to(REPO_ROOT))):
                fm = parse_frontmatter(pb)
                self.assertIsNotNone(fm, f"frontmatter missing/malformed in {pb}")
                missing = REQUIRED_FIELDS - set(fm.keys())
                self.assertEqual(missing, set(), f"missing fields: {missing}")

    def test_every_playbook_lens_weight_matches_review_crews(self):
        # crew_lookup[(layer_name, lens)] -> weight
        crew_lookup = {}
        for layer_name, crew in self.crews["crews"].items():
            for lens, weight in crew["review"].items():
                crew_lookup[(layer_name, lens)] = weight

        for pb in self.playbooks:
            fm = parse_frontmatter(pb)
            if fm is None:
                continue
            layer_dir = pb.parent.name  # "02_PRD"
            layer_short = layer_dir.split("_", 1)[1] if "_" in layer_dir else layer_dir
            key = (layer_short, fm["lens"])
            with self.subTest(playbook=str(pb.relative_to(REPO_ROOT))):
                self.assertIn(key, crew_lookup, f"unknown (layer, lens): {key}")
                self.assertEqual(
                    fm["weight"], crew_lookup[key],
                    f"weight mismatch for {key}: playbook={fm['weight']} crews={crew_lookup[key]}",
                )

    def test_every_playbook_framework_spec_version_matches(self):
        for pb in self.playbooks:
            fm = parse_frontmatter(pb)
            if fm is None:
                continue
            with self.subTest(playbook=str(pb.relative_to(REPO_ROOT))):
                self.assertEqual(fm["framework_spec_version"], self.framework_version)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test — passes vacuously (no playbooks yet) but framework is in place**

```bash
env -u LD_LIBRARY_PATH python3 -m unittest tests.conformance.test_playbook_frontmatter -v 2>&1 | tail -10
```

Expected: PASS (because `self.playbooks` is empty until Phase E authors content; each subTest runs over an empty list).

- [ ] **Step 3: Extend test_framework_spec_version.py for playbook coverage**

```bash
grep -l 'framework_spec_version' tests/conformance/test_framework_spec_version.py
```

Add an assertion verifying every `framework/playbooks/*/*.md` frontmatter's `framework_spec_version` matches `framework/VERSION`. (The new test in Task 3 already does this; this step is purely to centralize the assertion in the existing test if the project's pattern is one-version-test-file.) **Decision rule:** if `test_framework_spec_version.py` already iterates over multiple file globs, add `framework/playbooks/*/*.md` as another glob. Otherwise leave `test_playbook_frontmatter.py` as the single source of truth and skip this step. Inspect first:

```bash
cat tests/conformance/test_framework_spec_version.py 2>/dev/null | head -50 || echo "(file does not exist; skip this step)"
```

If file exists and globs over multiple file kinds, extend it. If file does not exist or is single-purpose, skip.

- [ ] **Step 4: Commit**

```bash
git add tests/conformance/test_playbook_frontmatter.py
# only add test_framework_spec_version.py if you modified it in Step 3
env -u LD_LIBRARY_PATH git commit -m "test(conformance): playbook frontmatter contract assertion

Validates required fields, lens-weight matches REVIEW_CREWS.yaml, and
framework_spec_version matches framework/VERSION. Passes vacuously until
playbook content lands in Phase E."
```

---

## Phase C — Unit tests (TDD: write first, must fail)

### Task 4: Unit test for playbook loader

**Files:**

- Create: `tests/unit/test_playbook_loader.py`

The loader is a small Python helper that the audit SKILLs can invoke (or whose logic they replicate inline). Test-first to lock the contract; implementation lands in Phase D.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_playbook_loader.py`:

```python
"""Loader helper for layer-and-lens playbook resolution."""
from __future__ import annotations
import unittest
from pathlib import Path
import tempfile

# Loader lives at platforms/claude-code-plugin/tools/playbook_loader.py
import sys
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "platforms" / "claude-code-plugin" / "tools"))


class PlaybookLoaderTests(unittest.TestCase):
    def test_resolves_known_playbook_path(self):
        from playbook_loader import resolve_playbook_path
        path = resolve_playbook_path(
            repo_root=REPO_ROOT,
            layer="02_PRD",
            lens="chaos_engineer",
        )
        self.assertEqual(
            path,
            REPO_ROOT / "framework" / "playbooks" / "02_PRD" / "chaos_engineer.md",
        )

    def test_missing_playbook_raises_with_documented_reason(self):
        from playbook_loader import load_playbook, PlaybookMissingError
        with self.assertRaises(PlaybookMissingError) as cm:
            load_playbook(
                repo_root=REPO_ROOT,
                layer="02_PRD",
                lens="nonexistent_lens",
            )
        self.assertIn("playbook missing:", str(cm.exception))
        self.assertIn("framework/playbooks/02_PRD/nonexistent_lens.md", str(cm.exception))

    def test_load_returns_content_when_file_exists(self):
        from playbook_loader import load_playbook
        # Use a temp playbook file to keep test hermetic.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "framework" / "playbooks" / "02_PRD").mkdir(parents=True)
            pb = tmp / "framework" / "playbooks" / "02_PRD" / "chaos_engineer.md"
            pb.write_text("---\nlens: chaos_engineer\n---\n# content\n")
            content = load_playbook(
                repo_root=tmp,
                layer="02_PRD",
                lens="chaos_engineer",
            )
            self.assertIn("# content", content)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test — confirm it fails with ImportError**

```bash
env -u LD_LIBRARY_PATH python3 -m unittest tests.unit.test_playbook_loader -v 2>&1 | tail -10
```

Expected: FAIL with `ModuleNotFoundError: No module named 'playbook_loader'`. Phase D Task 7 implements it.

- [ ] **Step 3: Commit the failing test**

```bash
git add tests/unit/test_playbook_loader.py
env -u LD_LIBRARY_PATH git commit -m "test(unit): playbook loader contract (failing; impl follows)

Locks the loader's three guarantees: known-path resolution, documented
missing-file error, content return on success. Implementation lands in
Phase D."
```

### Task 5: Unit test for finding-check schema enforcement

**Files:**

- Create: `tests/unit/test_finding_check_field.py`

This test asserts the synthesizer's discard behavior for uncited / fabricated check ids. The synthesizer is a plugin agent (`platforms/claude-code-plugin/agents/synthesizer.md`); the test exercises its **schema-enforcement helper** which we'll factor out as `platforms/claude-code-plugin/tools/finding_filter.py` for testability.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_finding_check_field.py`:

```python
"""Synthesizer discards findings without a check citation or with fabricated check ids."""
from __future__ import annotations
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "platforms" / "claude-code-plugin" / "tools"))


class FindingFilterTests(unittest.TestCase):
    def _filter(self, findings, valid_checks):
        from finding_filter import filter_findings
        return filter_findings(findings, valid_check_ids=valid_checks)

    def test_finding_with_valid_check_id_is_kept(self):
        kept, discarded = self._filter(
            findings=[{"id": "CE-1", "priority": "P2", "check": "C1"}],
            valid_checks={"C1", "C2"},
        )
        self.assertEqual(len(kept), 1)
        self.assertEqual(len(discarded), 0)

    def test_finding_without_check_field_is_discarded(self):
        kept, discarded = self._filter(
            findings=[{"id": "CE-1", "priority": "P2"}],  # no 'check' field
            valid_checks={"C1", "C2"},
        )
        self.assertEqual(len(kept), 0)
        self.assertEqual(len(discarded), 1)
        self.assertEqual(discarded[0]["reason"], "no_check_citation")

    def test_finding_with_fabricated_check_id_is_discarded(self):
        kept, discarded = self._filter(
            findings=[{"id": "CE-1", "priority": "P2", "check": "C99"}],
            valid_checks={"C1", "C2"},
        )
        self.assertEqual(len(kept), 0)
        self.assertEqual(len(discarded), 1)
        self.assertEqual(discarded[0]["reason"], "unknown_check")
        self.assertEqual(discarded[0]["check"], "C99")

    def test_beyond_checklist_finding_is_kept(self):
        kept, discarded = self._filter(
            findings=[{
                "id": "CE-2",
                "priority": "P2",
                "check": "beyond-checklist:degraded-mode-asymmetry",
            }],
            valid_checks={"C1", "C2"},
        )
        self.assertEqual(len(kept), 1)
        self.assertEqual(len(discarded), 0)


class CoverageEmissionTests(unittest.TestCase):
    def test_coverage_groups_findings_by_check(self):
        from finding_filter import emit_coverage
        findings = [
            {"check": "C1"},
            {"check": "C1"},
            {"check": "C2"},
            {"check": "beyond-checklist:foo"},
            {"check": "beyond-checklist:bar"},
        ]
        coverage = emit_coverage(findings)
        self.assertEqual(coverage["C1"], 2)
        self.assertEqual(coverage["C2"], 1)
        self.assertEqual(coverage["beyond_checklist"], 2)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test — confirm it fails with ImportError**

```bash
env -u LD_LIBRARY_PATH python3 -m unittest tests.unit.test_finding_check_field -v 2>&1 | tail -10
```

Expected: FAIL with `ModuleNotFoundError: No module named 'finding_filter'`.

- [ ] **Step 3: Commit the failing test**

```bash
git add tests/unit/test_finding_check_field.py
env -u LD_LIBRARY_PATH git commit -m "test(unit): finding-check schema enforcement contract (failing)

Locks synthesizer's filter behavior: keep checklist-cited and
beyond-checklist findings; discard uncited and fabricated. Coverage
emission groups by check id. Implementation follows in Phase D."
```

---

## Phase D — Mechanism implementation

### Task 6: Implement finding_filter.py (synthesizer's schema helper)

**Files:**

- Create: `platforms/claude-code-plugin/tools/finding_filter.py`

- [ ] **Step 1: Implement the module**

Create `platforms/claude-code-plugin/tools/finding_filter.py`:

```python
"""Finding-check schema enforcement for the synthesizer agent.

Per LAYER-PLAYBOOKS-001 design: every finding produced by a lens MUST cite
either a playbook checklist check (e.g. "C1") or a beyond-checklist
principle ("beyond-checklist:<tag>"). Findings without a valid citation
are discarded.

Stdlib-only; no external dependencies.
"""
from __future__ import annotations
from collections import Counter
from typing import Iterable

BEYOND_PREFIX = "beyond-checklist:"


def filter_findings(
    findings: Iterable[dict],
    valid_check_ids: set[str],
) -> tuple[list[dict], list[dict]]:
    """Split findings into (kept, discarded).

    Kept: finding has 'check' field that is either in `valid_check_ids` or
    begins with the beyond-checklist prefix.
    Discarded: every other finding, with a 'reason' field added:
      - 'no_check_citation': finding has no 'check' field
      - 'unknown_check': finding's check id is not in `valid_check_ids`
        and is not a beyond-checklist citation
    """
    kept: list[dict] = []
    discarded: list[dict] = []
    for finding in findings:
        check = finding.get("check")
        if check is None:
            discarded.append({**finding, "reason": "no_check_citation"})
            continue
        if check.startswith(BEYOND_PREFIX):
            kept.append(finding)
            continue
        if check in valid_check_ids:
            kept.append(finding)
            continue
        discarded.append({**finding, "reason": "unknown_check"})
    return kept, discarded


def emit_coverage(findings: Iterable[dict]) -> dict:
    """Return verdict.playbook_coverage shape: {<check_id>: <count>, ..., 'beyond_checklist': <n>}."""
    counts: Counter[str] = Counter()
    for finding in findings:
        check = finding.get("check")
        if check is None:
            continue
        if check.startswith(BEYOND_PREFIX):
            counts["beyond_checklist"] += 1
        else:
            counts[check] += 1
    return dict(counts)
```

- [ ] **Step 2: Run the unit test — confirm it passes**

```bash
env -u LD_LIBRARY_PATH python3 -m unittest tests.unit.test_finding_check_field -v 2>&1 | tail -15
```

Expected: all 5 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add platforms/claude-code-plugin/tools/finding_filter.py
env -u LD_LIBRARY_PATH git commit -m "feat(plugin): synthesizer's finding-filter helper (stdlib-only)

Splits findings into kept/discarded by check-field citation. Emits
verdict.playbook_coverage. Resolves test_finding_check_field unit tests."
```

### Task 7: Implement playbook_loader.py

**Files:**

- Create: `platforms/claude-code-plugin/tools/playbook_loader.py`

- [ ] **Step 1: Implement the loader**

Create `platforms/claude-code-plugin/tools/playbook_loader.py`:

```python
"""Layer-and-lens playbook resolver for plugin audit SKILLs.

Resolves framework/playbooks/<layer>/<lens>.md, reads the content, and
raises a documented error if the file is missing.

Stdlib-only.
"""
from __future__ import annotations
from pathlib import Path


class PlaybookMissingError(FileNotFoundError):
    """Raised when a (layer, lens) pair has no playbook on disk."""


def resolve_playbook_path(repo_root: Path | str, layer: str, lens: str) -> Path:
    """Return the absolute path where the (layer, lens) playbook should live.

    No I/O. Pure path resolution. Use load_playbook() to actually read.
    """
    return Path(repo_root) / "framework" / "playbooks" / layer / f"{lens}.md"


def load_playbook(repo_root: Path | str, layer: str, lens: str) -> str:
    """Read and return the playbook content for (layer, lens).

    Raises PlaybookMissingError with a message naming the expected path
    if the file does not exist.
    """
    path = resolve_playbook_path(repo_root, layer, lens)
    if not path.is_file():
        rel = path.relative_to(repo_root) if path.is_absolute() else path
        raise PlaybookMissingError(f"playbook missing: {rel}")
    return path.read_text()
```

- [ ] **Step 2: Run the unit test — confirm it passes**

```bash
env -u LD_LIBRARY_PATH python3 -m unittest tests.unit.test_playbook_loader -v 2>&1 | tail -15
```

Expected: all 3 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add platforms/claude-code-plugin/tools/playbook_loader.py
env -u LD_LIBRARY_PATH git commit -m "feat(plugin): playbook loader helper (stdlib-only)

Resolves framework/playbooks/<layer>/<lens>.md. Raises
PlaybookMissingError with the expected-path message on miss. Resolves
test_playbook_loader unit tests."
```

### Task 8: Wire playbook injection into all 8 audit SKILLs

**Files:**

- Modify: `platforms/claude-code-plugin/skills/doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}-audit/SKILL.md`

Each audit SKILL already has a §"Review Mode" / §"team mode" subsection (from BRD-RT-001 / PRD-RT-001 implementations). The new edit adds a `## Playbook injection` paragraph between step 3 ("Map each lens to its plugin agent") and step 4 ("Fan out") of the team-mode procedure.

**Insertion locator (consistent across all 8 SKILLs)**: each SKILL's team-mode section already contains a line matching `3\. \*\*Map each lens to its plugin agent\*\* via the table in` (verified by grep in BRD/PRD SKILLs; the others were derived from the same template). Insert the new step `3a` immediately after the bullet block for step 3. Replace the existing step 4 entirely with the augmented version below. If the locator does NOT match in any SKILL, halt and inspect — the SKILL may have drifted from the template, requiring manual reconciliation.

**Pre-check** before applying:

```bash
grep -lE '^3\. \*\*Map each lens to its plugin agent' \
  platforms/claude-code-plugin/skills/doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}-audit/SKILL.md \
  | wc -l
```

Expected: `8`. If less, list the missing files and reconcile before proceeding.

- [ ] **Step 1: Define the canonical insertion text**

The text to insert (used verbatim in all 8 SKILLs, with `<layer>` and `<NN>_<LAYER>` substituted):

```markdown
3a. **Load the layer-and-lens playbook.** For each lens in the crew,
   resolve and read the playbook content from
   `${CLAUDE_PLUGIN_ROOT}/../../framework/playbooks/<NN>_<LAYER>/<lens>.md`.
   If the playbook file is missing, mark `branches[<lens>].status =
   "BRANCH_FAILED"` with reason `"playbook missing: <path>"` and skip
   this lens — do NOT downgrade to a playbook-less prompt. Other lenses
   continue. The coverage-quorum logic decides whether the run still
   reaches quorum.
```

And the brief-composition step (modify step 4 of the team-mode procedure):

```markdown
4. **Fan out.** Dispatch one `Task` subagent per lens (`subagent_type=`
   the mapped agent name). Each subagent's brief contains:
   - The absolute artifact path (untrusted content)
   - The lens name and its weight
   - The slot path `.aidoc/review/<NN>_<LAYER>/<artifact-id>/<lens>.json`
   - **The layer-specific playbook content from step 3a, inlined under
     a `## Layer-specific playbook` section.** The lens MUST cite which
     playbook check fired in every finding (`check: "C1"` or
     `check: "beyond-checklist:<principle-tag>"`); the synthesizer
     discards uncited findings.
   - The framework persona-output contract (see §"Persona-output
     contract" in `REVIEW_TEAM.md`)
   - The structural checklist below as untrusted context (for awareness;
     the lens does **not** re-run the structural checks — those are this
     skill's job)
```

- [ ] **Step 2: Apply to doc-brd-audit/SKILL.md**

Open `platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md`. Locate the team-mode section. Insert the `3a` step after the existing step 3 ("Map each lens to its plugin agent"). Replace the existing step 4 with the augmented version above (substituting `<NN>_<LAYER>` → `01_BRD`).

- [ ] **Step 3: Apply to doc-prd-audit/SKILL.md**

Same pattern with `02_PRD`.

- [ ] **Step 4: Apply to doc-ears-audit/SKILL.md**

Same pattern with `03_EARS`.

- [ ] **Step 5: Apply to doc-bdd-audit/SKILL.md**

Same pattern with `04_BDD`.

- [ ] **Step 6: Apply to doc-adr-audit/SKILL.md**

Same pattern with `05_ADR`.

- [ ] **Step 7: Apply to doc-spec-audit/SKILL.md**

Same pattern with `06_SPEC`.

- [ ] **Step 8: Apply to doc-tdd-audit/SKILL.md**

Same pattern with `07_TDD`.

- [ ] **Step 9: Apply to doc-iplan-audit/SKILL.md**

Same pattern with `08_IPLAN`.

- [ ] **Step 10: Verify each edit landed**

```bash
grep -l 'Playbook injection\|Layer-specific playbook' platforms/claude-code-plugin/skills/doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}-audit/SKILL.md
```

Expected: 8 paths printed.

```bash
grep -c '3a\. \*\*Load the layer-and-lens playbook' platforms/claude-code-plugin/skills/doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}-audit/SKILL.md
```

Expected: each path reports `1`.

- [ ] **Step 11: Commit**

```bash
git add platforms/claude-code-plugin/skills/doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}-audit/SKILL.md
env -u LD_LIBRARY_PATH git commit -m "feat(plugin): wire playbook injection into all 8 audit SKILLs

Each audit SKILL team-mode flow now loads the (layer, lens) playbook
before fan-out and inlines its content into the per-lens Task brief
under '## Layer-specific playbook'. Missing playbook -> BRANCH_FAILED
for that lens (never silent downgrade). Each lens's findings must
cite a check id; the synthesizer (Task 9) enforces the citation."
```

### Task 9: Update synthesizer to honor finding-check schema + emit playbook_coverage

**Files:**

- Modify: `platforms/claude-code-plugin/agents/synthesizer.md`

- [ ] **Step 1: Open synthesizer.md and locate the reduce section**

```bash
grep -n '^## \|^### ' platforms/claude-code-plugin/agents/synthesizer.md
```

Confirmed section structure (from pre-plan inspection 2026-06-07):

```
## Inputs                                            (line ~33)
## Reduce — deterministic, gating                    (line ~40)
## Narrative — advisory (non-gating)                 (line ~56)
## The gate (state it explicitly in the report)      (line ~61)
## Output — two companion artifacts                  (line ~68)
### 1. `verdict.json` — the machine-readable verdict (line ~74)
### 2. `report.md` — the human narrative             (line ~152)
## Hard Constraints                                  (line ~169)
## Related Resources                                 (line ~175)
```

The new behavior:

1. Per-lens slot's findings pass through `finding_filter.filter_findings()` — inserted as a new `### Playbook check-citation enforcement (LAYER-PLAYBOOKS-001)` subsection at the END of `## Reduce` (after the existing deterministic reduce rules, before `## Narrative`).
2. `verdict.playbook_coverage` field added to the `verdict.json` schema in `### 1. verdict.json` subsection (after existing fields).
3. Discarded findings are tabulated in `report.md` under a new `## Discarded findings` subsection (added to `### 2. report.md`).

- [ ] **Step 2: Add the schema-enforcement instruction**

In the synthesizer's reduce algorithm (the existing instruction set telling it how to merge slot files), insert this paragraph:

```markdown
### Playbook check-citation enforcement (LAYER-PLAYBOOKS-001)

After loading each lens slot's `findings[]`, run them through the
finding-filter helper at `${CLAUDE_PLUGIN_ROOT}/tools/finding_filter.py`.
Two-step filter:

1. **Citation gate.** Each finding must have a `check` field that is
   either (a) one of the playbook's `C1..Cn` ids for this lens, or
   (b) prefixed `beyond-checklist:`. Findings without a check or with
   a fabricated id are **discarded**.
2. **Coverage emission.** Group surviving findings by `check` value;
   emit `verdict.playbook_coverage` as `{<check_id>: <count>, ...,
   beyond_checklist: <n>}`.

The set of valid `Cn` ids for a (layer, lens) is derived from the
playbook itself — parse `## Required evidence checks` headings and
extract identifiers matching `^\*\*C\d+ ` (the canonical check-row
shape; see REVIEW_TEAM.md §Playbooks §"Required content sections").

Discarded findings are reported in `report.md` under a `## Discarded
findings` subsection: count by reason (`no_check_citation` /
`unknown_check`), three example finding ids per reason. The
synthesizer's narrative MUST surface the discard count if non-zero —
this is a quality signal for the calibration loop.
```

- [ ] **Step 3: Update the verdict.json output schema in synthesizer.md**

Locate the verdict.json schema section (it documents fields like `combined_status`, `content_score`, `coverage`, etc.). Add the new field:

```yaml
playbook_coverage:                    # NEW per LAYER-PLAYBOOKS-001
  type: object
  description: |
    Count of surviving findings per playbook check id, plus a
    'beyond_checklist' aggregate. Drift signal: if
    beyond_checklist / total > 0.30, the playbook may need revision.
  example:
    C1: 2
    C2: 1
    beyond_checklist: 1
```

- [ ] **Step 4: Verify the synthesizer.md changes**

```bash
grep -n 'finding_filter\|playbook_coverage\|Discarded findings' platforms/claude-code-plugin/agents/synthesizer.md
```

Expected: ≥ 5 matches.

- [ ] **Step 5: Commit**

```bash
git add platforms/claude-code-plugin/agents/synthesizer.md
env -u LD_LIBRARY_PATH git commit -m "feat(plugin): synthesizer enforces finding-check citation + emits coverage

Per LAYER-PLAYBOOKS-001: filter via finding_filter.filter_findings;
emit verdict.playbook_coverage; surface discarded-finding count in
report.md narrative. Discarded reasons tabulated under a new
'## Discarded findings' section."
```

---

## Phase E — Author the 45 playbooks

Each layer-task authors that layer's playbooks (5 or 6 files). All playbooks follow the content shape from REVIEW_TEAM.md §Playbooks. Each file is target ~120-180 lines.

**Note on TDD exception**: Tasks 10.1–10.8 are content-authoring tasks, NOT test-driven. The "test" for these files is the conformance test from Task 2 (file existence per crew) + the frontmatter test from Task 3 (parses + matches REVIEW_CREWS.yaml). Both tests are already in place by Phase E. No per-playbook unit test exists or is needed — playbook *content* quality is validated by the live acceptance run in Phase F. This is a deliberate deviation from the writing-plans skill's TDD default; content artifacts have no per-instance code-level test surface.

**Note on calibration**: BRD + PRD playbooks (Tasks 10.1, 10.2) are calibrated against the live cascade findings already produced (BRD score 96, PRD score 93 + 15-finding verdict). EARS + later layers (Tasks 10.3–10.8) are authored a-priori without live calibration data. This is a known design risk; if a later layer's first live cascade shows < 60% checklist-cited findings, that layer's playbooks need revision before merge.

**Common authoring template for every playbook** (use this as the starting frame, then customize the layer/lens-specific content):

```markdown
---
layer: <NN>_<LAYER>
lens: <lens_snake_case>
weight: <weight from REVIEW_CREWS.yaml>
agent: <plugin agent name from review-team/SKILL.md mapping>
framework_spec_version: "0.14.0"
---
# <lens> lens — <LAYER> layer

## Reasoning frame

[2-3 paragraphs:
 (a) What this lens uniquely sees at this layer's altitude.
 (b) How it differs from the same lens at adjacent layers
     (e.g., chaos_engineer at PRD vs at SPEC vs at TDD).
 (c) What this lens does NOT do (covered by other lenses in the
     same crew).]

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check
citation are out-of-scope and discarded by the synthesizer.

**C1 — <check name>.** <imperative statement of what to verify>.
Missing → P<N> finding citing C1.

**C2 — <check name>.** <...>. Missing → P<N> citing C2.

**C3 — <check name>.** <...>. Missing → P<N> citing C3.

[... target 5-8 checks per playbook; finite, deterministically
applicable, derived from the layer's known failure modes]

## Beyond-checklist

If you find a layer-specific failure mode the checklist does not cover,
raise it as a P2/P3 finding citing `beyond-checklist:<principle-tag>`
and state which paragraph of the reasoning frame above motivates it.
Use sparingly. If more than 30% of your findings are beyond-checklist,
the playbook needs revision (file a follow-up).

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
```

### Task 10.1: Author BRD playbooks (5 files)

**Files:**

- Create: `framework/playbooks/01_BRD/architect.md` (weight 30)
- Create: `framework/playbooks/01_BRD/business_analyst.md` (weight 30)
- Create: `framework/playbooks/01_BRD/auditor.md` (weight 20)
- Create: `framework/playbooks/01_BRD/chaos_engineer.md` (weight 12)
- Create: `framework/playbooks/01_BRD/security_engineer.md` (weight 8)

**Per-playbook content topics** (the checklist content for each):

| Lens | Key checks (derive C1..Cn from these) |
|---|---|
| architect | (a) Capability-vs-implementation altitude (no container/component names at BRD altitude); (b) capability decomposition reconciles across §sections; (c) measurable outcomes attached to each capability; (d) cross-capability boundaries explicit; (e) NFRs declared at capability altitude (not deferred to PRD when BRD-authoritative) |
| business_analyst | (a) Every objective has a baseline and a measurable target; (b) personas tied to capabilities; (c) BRD scope boundary (what's in/out) explicit; (d) success metrics observable post-launch; (e) every requirement traces to an upstream business motivator |
| auditor | (a) Element IDs conform to ID_NAMING_STANDARDS; (b) every §section required by BRD template present; (c) external references (RFC, BRD-XX) resolve; (d) glossary covers every domain term; (e) Document Control filled in |
| chaos_engineer | (a) Reliability NFRs declared (availability, durability) at BRD altitude; (b) capacity bounds named or explicitly ADR-deferred; (c) degraded-mode behaviors named for each critical capability; (d) recovery/restore SLAs declared at the level the business commits to |
| security_engineer | (a) Trust boundaries declared at capability altitude; (b) data-classification of each persona-managed artifact; (c) abuse-case capabilities named (not implementation); (d) external compliance refs (RFC/regulation) cited where applicable |

- [ ] **Step 1: Author all 5 BRD playbooks**

Use the template above for each. Substitute the per-lens checks from the table. Target ~150 lines per file.

- [ ] **Step 2: Run conformance tests for BRD coverage**

```bash
env -u LD_LIBRARY_PATH python3 -m unittest tests.conformance.test_playbook_coverage -v 2>&1 | tail -10
```

Expected: still FAIL (other layers' playbooks missing), but BRD's 5 paths no longer in the missing list. Verify by grepping the output:

```bash
env -u LD_LIBRARY_PATH python3 -m unittest tests.conformance.test_playbook_coverage 2>&1 | grep '01_BRD' || echo "BRD coverage complete"
```

Expected: `BRD coverage complete`.

- [ ] **Step 3: Run frontmatter conformance test on the new files**

```bash
env -u LD_LIBRARY_PATH python3 -m unittest tests.conformance.test_playbook_frontmatter -v 2>&1 | tail -10
```

Expected: PASS (5 new playbooks all have valid frontmatter matching REVIEW_CREWS.yaml weights).

- [ ] **Step 4: Commit BRD playbooks**

```bash
git add framework/playbooks/01_BRD/
env -u LD_LIBRARY_PATH git commit -m "feat(framework): BRD playbooks (5 lenses: architect/BA/auditor/chaos/security)

Layer-specific reasoning frame + 5-8 deterministic checks per lens +
beyond-checklist escape hatch + 0-100 scoring rubric. Crew weights
match REVIEW_CREWS.yaml BRD entry (30/30/20/12/8 sums to 100)."
```

### Task 10.2: Author PRD playbooks (6 files)

**Files:**

- Create: `framework/playbooks/02_PRD/product_owner.md` (weight 30)
- Create: `framework/playbooks/02_PRD/architect.md` (weight 25)
- Create: `framework/playbooks/02_PRD/tech_lead.md` (weight 20)
- Create: `framework/playbooks/02_PRD/chaos_engineer.md` (weight 8)
- Create: `framework/playbooks/02_PRD/security_engineer.md` (weight 7)
- Create: `framework/playbooks/02_PRD/auditor.md` (weight 10)

**Per-playbook content topics** (informed by the just-closed PRD-01 cascade findings — these are calibrated to the real failure modes the team-mode review surfaced):

| Lens | Key checks |
|---|---|
| product_owner | (a) Every §11 launch gate traces to a BRD-authorized requirement (the rate-limit gap PR-RT-001 surfaced); (b) measurable thresholds in §5 have a rationale or baseline; (c) every §9 functional req has nested ACs; (d) priority assignments (P1/P2) consistent across §7/§9/§11; (e) MVP-hypothesis 30-day metrics gate the launch decision |
| architect | (a) c4-l2 + dfd-l2 + sequence-sync reconcile; (b) container-altitude only (no class/method names); (c) every diagram has a `decomposition note` explaining MVP deferrals; (d) ADR deferral pattern consistent (single mode); (e) NFR bounds match §5 measurement boundary |
| tech_lead | (a) Every §11 gate's "Validation" cell is measurable (not "Pass"); (b) every numeric in the PRD is bound to a §5 measurement boundary; (c) implementability called out for novel patterns; (d) over-length / empty-input / type-confused inputs bounded; (e) §13 mitigations have numeric or ADR-deferred bounds |
| chaos_engineer | (a) §13 risk-row symmetry (every risk has §10 surface + §11 AC + §12 anchor — the CE-1 finding from PRD live cascade); (b) bounded degraded mode (no unbounded slowness that escapes the 5xx branch — the CE-3 finding); (c) failure-branch gating (not just happy-path "controls in place" — the CE-2 finding); (d) capacity-exhausted explicit non-retryable; (e) best-effort-vs-synchronous separation at PRD altitude |
| security_engineer | (a) Every PRD-introduced trust-boundary tied to a BRD authorization; (b) §13 abuse mitigations have a takedown SLA or ADR-deferral marker; (c) screen-at-submit TOCTOU window addressed; (d) data classification for visit-count / link-store distinct; (e) enumeration/scraping defense layered (not single-control) |
| auditor | (a) `@brd:` tag resolution rate 100%; (b) element-ID conformance per ID_NAMING_STANDARDS; (c) every §section required by PRD template present; (d) glossary covers PRD-introduced terms; (e) PRD's own self-claimed score in Document Control NOT used as audit verdict |

- [ ] **Step 1: Author all 6 PRD playbooks**

Mirror the BRD task pattern. The chaos_engineer playbook in particular should encode C1/C2/C3 to match the CE-1/CE-2/CE-3 findings the just-closed cascade surfaced — this is the strongest empirical calibration we have.

- [ ] **Step 2: Conformance tests for PRD coverage**

```bash
env -u LD_LIBRARY_PATH python3 -m unittest tests.conformance.test_playbook_coverage 2>&1 | grep '02_PRD' || echo "PRD coverage complete"
```

Expected: `PRD coverage complete`.

```bash
env -u LD_LIBRARY_PATH python3 -m unittest tests.conformance.test_playbook_frontmatter -v 2>&1 | tail -5
```

Expected: PASS.

- [ ] **Step 3: Commit PRD playbooks**

```bash
git add framework/playbooks/02_PRD/
env -u LD_LIBRARY_PATH git commit -m "feat(framework): PRD playbooks (6 lenses)

product_owner/architect/tech_lead/chaos/security/auditor.
chaos_engineer's C1-C3 calibrated against the CE-1/CE-2/CE-3 findings
from the PRD-01 live cascade (risk-row symmetry, bounded degraded mode,
failure-branch gating). Crew weights match REVIEW_CREWS.yaml PRD entry
(30/25/20/8/7/10 sums to 100)."
```

### Task 10.3: Author EARS playbooks (5 files)

**Files:**

- Create: `framework/playbooks/03_EARS/requirements_specialist.md` (weight 35)
- Create: `framework/playbooks/03_EARS/tech_lead.md` (weight 25)
- Create: `framework/playbooks/03_EARS/qa_lead.md` (weight 20)
- Create: `framework/playbooks/03_EARS/chaos_engineer.md` (weight 12)
- Create: `framework/playbooks/03_EARS/security_engineer.md` (weight 8)

| Lens | Key checks |
|---|---|
| requirements_specialist | (a) Every EARS line uses one of the 6 canonical patterns (ubiquitous / event-driven / state-driven / optional / unwanted / complex); (b) atomicity — one rule per line; (c) every line has a measurable response; (d) every `@prd:` tag resolves; (e) no orphan rule (every line traces to a PRD §9 row) |
| tech_lead | (a) Triggers + responses are technically implementable (no hand-waving); (b) overlapping rules flagged (multiple ubiquitous on same state); (c) every numeric bound has units; (d) ADR-deferred placeholders explicitly marked; (e) consistency of terminology with PRD glossary |
| qa_lead | (a) Every EARS line corresponds to ≥1 BDD scenario at next layer; (b) coverage matrix readable (rule → tests); (c) ambiguity-free triggers (no "occasionally", "sometimes"); (d) negative cases enumerated (unwanted patterns); (e) idempotency declared for stateful rules |
| chaos_engineer | (a) Every failure mode named in PRD §13 has an unwanted-behavior EARS line; (b) timeout-vs-deadline coupling explicit; (c) retry budgets bounded; (d) cascading-failure boundary stated; (e) recovery rules paired with detection rules |
| security_engineer | (a) Every abuse case from PRD has an EARS line (event-driven + unwanted); (b) input-validation rules cover all submission paths; (c) rate-limiting rules have explicit bounds (or ADR-deferred); (d) audit-log rules cover authentication + authorization decisions; (e) data-classification matched to access rules |

- [ ] **Step 1: Author 5 EARS playbooks**
- [ ] **Step 2: Conformance check + commit**

```bash
env -u LD_LIBRARY_PATH python3 -m unittest tests.conformance.test_playbook_coverage 2>&1 | grep '03_EARS' || echo "EARS coverage complete"
git add framework/playbooks/03_EARS/
env -u LD_LIBRARY_PATH git commit -m "feat(framework): EARS playbooks (5 lenses: req_spec/tech_lead/qa/chaos/security)

Crew weights 35/25/20/12/8 sums to 100 per REVIEW_CREWS.yaml."
```

### Task 10.4: Author BDD playbooks (6 files)

**Files:**

- Create: `framework/playbooks/04_BDD/qa_lead.md` (weight 35)
- Create: `framework/playbooks/04_BDD/tech_lead.md` (weight 25)
- Create: `framework/playbooks/04_BDD/chaos_engineer.md` (weight 14)
- Create: `framework/playbooks/04_BDD/security_engineer.md` (weight 6)
- Create: `framework/playbooks/04_BDD/operator.md` (weight 10)
- Create: `framework/playbooks/04_BDD/auditor.md` (weight 10)

| Lens | Key checks |
|---|---|
| qa_lead | (a) Every EARS line covered by ≥1 scenario; (b) Given/When/Then atomicity; (c) data tables vs scenario outlines used appropriately; (d) shared steps deduplicated; (e) tag conventions consistent |
| tech_lead | (a) Step definitions implementable (no semantic ambiguity); (b) timeout/wait reasoning explicit; (c) fixture setup teardown idempotent; (d) cross-scenario dependencies absent (each scenario standalone); (e) `@regression` vs `@smoke` tags placed correctly |
| chaos_engineer | (a) Every unwanted EARS pattern has a failure-mode scenario; (b) network-partition + slow-response variants covered; (c) recovery scenarios paired with failure scenarios; (d) resource-exhaustion paths exercised; (e) negative-path coverage matches positive-path |
| security_engineer | (a) Every abuse-case EARS line has a security scenario; (b) authn/authz scenarios cover both happy + denied paths; (c) input-fuzzing scenarios for every accepting endpoint; (d) audit-log assertions present where rules require them; (e) regulatory-compliance scenarios where applicable |
| operator | (a) Observability hooks in scenarios (logs, metrics, traces); (b) runtime-config-change scenarios; (c) deploy-during-traffic scenarios; (d) operator-action scenarios (rollback, drain, freeze); (e) alerting-fire scenarios for SLO breaches |
| auditor | (a) Tags resolve to upstream EARS lines; (b) step-definition catalog conformance; (c) scenario IDs follow naming standards; (d) gherkin-lint clean; (e) feature-file Document Control populated |

- [ ] **Step 1-2: Author + commit**

```bash
git add framework/playbooks/04_BDD/
env -u LD_LIBRARY_PATH git commit -m "feat(framework): BDD playbooks (6 lenses)

Crew weights 35/25/14/6/10/10 sums to 100 per REVIEW_CREWS.yaml.
chaos_engineer/security_engineer split 14/6 reflects BDD's failure-
scenario emphasis over abuse-case scenarios."
```

### Task 10.5: Author ADR playbooks (6 files)

**Files:**

- Create: `framework/playbooks/05_ADR/architect.md` (weight 35)
- Create: `framework/playbooks/05_ADR/tech_lead.md` (weight 25)
- Create: `framework/playbooks/05_ADR/chaos_engineer.md` (weight 8)
- Create: `framework/playbooks/05_ADR/security_engineer.md` (weight 12)
- Create: `framework/playbooks/05_ADR/operator.md` (weight 10)
- Create: `framework/playbooks/05_ADR/auditor.md` (weight 10)

| Lens | Key checks |
|---|---|
| architect | (a) Decision context section explains the forcing function; (b) options compared on the same criteria; (c) selected option's rationale falsifiable; (d) consequences enumerated (positive + negative + neutral); (e) supersedes/superseded-by chains intact |
| tech_lead | (a) Implementation cost named (small/medium/large with justification); (b) reversibility called out; (c) dependencies on other ADRs listed; (d) migration path stated where the decision changes status quo; (e) verification approach declared |
| chaos_engineer | (a) Failure modes of the chosen option enumerated; (b) blast radius bounded; (c) graceful-degradation behavior named; (d) rollback decision-criteria stated; (e) operational risk acknowledged |
| security_engineer | (a) Trust-boundary impact of the decision; (b) authn/authz implications; (c) crypto choices (algorithm, key-management) where applicable; (d) audit-log implications; (e) compliance/regulatory fit |
| operator | (a) Runtime observability impact; (b) deploy-time impact (downtime, rolling-deploy compatibility); (c) on-call runbook impact; (d) capacity / cost impact; (e) telemetry coverage |
| auditor | (a) ADR ID + title format conforms; (b) status transition log (Proposed → Accepted → ...) intact; (c) cross-refs to BRD/PRD/SPEC resolve; (d) glossary covers introduced terms; (e) Document Control populated |

- [ ] **Step 1-2: Author + commit (same pattern as previous layer tasks)**

```bash
git add framework/playbooks/05_ADR/
env -u LD_LIBRARY_PATH git commit -m "feat(framework): ADR playbooks (6 lenses)

Crew weights 35/25/8/12/10/10 sums to 100. security_engineer (12)
> chaos_engineer (8) reflects ADRs' role in encoding trust boundaries,
authn/authz choices, and crypto decisions."
```

### Task 10.6: Author SPEC playbooks (5 files)

**Files:**

- Create: `framework/playbooks/06_SPEC/architect.md` (weight 30)
- Create: `framework/playbooks/06_SPEC/tech_lead.md` (weight 30)
- Create: `framework/playbooks/06_SPEC/integration_lead.md` (weight 20)
- Create: `framework/playbooks/06_SPEC/chaos_engineer.md` (weight 10)
- Create: `framework/playbooks/06_SPEC/security_engineer.md` (weight 10)

| Lens | Key checks |
|---|---|
| architect | (a) Component-altitude (not class — leave to TDD); (b) C4-L3 if applicable; (c) every ADR consumed; (d) deployment topology stated; (e) NFR bounds from PRD/ADR materialized as component properties |
| tech_lead | (a) Concurrency primitives chosen explicitly (lock/lease/CAS/event-sourced); (b) data shapes typed where applicable; (c) algorithmic complexity bounded; (d) error-propagation contract stated; (e) interface contracts (API + storage) stable |
| integration_lead | (a) External-system contracts have versioned schemas; (b) backward-compat policy stated; (c) integration error modes enumerated; (d) timeout/retry budgets per integration; (e) circuit-breaker policy where applicable |
| chaos_engineer | (a) Component-level failure modes (per-component RT0 / RT1); (b) bulkhead/isolation boundaries; (c) fault-injection strategy declared; (d) recovery primitives chosen; (e) cascading-failure firebreaks |
| security_engineer | (a) Component-level trust boundaries; (b) per-component data-classification; (c) secrets-management chosen; (d) authz model per integration; (e) audit-log shape per data-class |

- [ ] **Step 1-2: Author + commit**

```bash
git add framework/playbooks/06_SPEC/
env -u LD_LIBRARY_PATH git commit -m "feat(framework): SPEC playbooks (5 lenses)

Crew weights 30/30/20/10/10 sums to 100. Equal chaos/security split
reflects SPEC's dual responsibility for both reliability and security
controls at component altitude."
```

### Task 10.7: Author TDD playbooks (6 files)

**Files:**

- Create: `framework/playbooks/07_TDD/qa_lead.md` (weight 35)
- Create: `framework/playbooks/07_TDD/tech_lead.md` (weight 25)
- Create: `framework/playbooks/07_TDD/chaos_engineer.md` (weight 10)
- Create: `framework/playbooks/07_TDD/security_engineer.md` (weight 10)
- Create: `framework/playbooks/07_TDD/operator.md` (weight 10)
- Create: `framework/playbooks/07_TDD/auditor.md` (weight 10)

| Lens | Key checks |
|---|---|
| qa_lead | (a) Every SPEC component has unit-test coverage; (b) every BDD scenario has integration-test mapping; (c) coverage thresholds met per ID_NAMING_STANDARDS; (d) test-pyramid balance reasonable (unit > integration > e2e); (e) flaky-test policy declared |
| tech_lead | (a) Test isolation (no shared mutable state); (b) fixture design DRY; (c) parameterized tests for combinatorial cases; (d) timing-sensitive tests deterministic (no sleep-based); (e) mock boundary explicit (don't mock the thing under test) |
| chaos_engineer | (a) Chaos-test catalog defined (network, latency, resource, dep failures); (b) each catalog entry has a SPEC component target; (c) recovery assertions explicit; (d) blast-radius bounded by test design; (e) chaos-tests runnable in CI gated profile |
| security_engineer | (a) SECTEST coverage per per-component trust boundary; (b) fuzz-test strategy declared; (c) authn/authz test matrix; (d) input-validation tests per accepting endpoint; (e) static-analysis (SAST) gate configured |
| operator | (a) Runtime-config-change tests; (b) deploy-during-traffic tests; (c) observability assertion tests (log shape, metric presence); (d) operator-action tests (drain, freeze, rollback); (e) SLO-breach detection tests |
| auditor | (a) Every SPEC component traced to ≥1 test; (b) test IDs conform to naming standards; (c) coverage report generated by CI; (d) test-result format machine-readable; (e) Document Control on TDD doc |

- [ ] **Step 1-2: Author + commit**

```bash
git add framework/playbooks/07_TDD/
env -u LD_LIBRARY_PATH git commit -m "feat(framework): TDD playbooks (6 lenses)

Crew weights 35/25/10/10/10/10 sums to 100. Equal chaos/security split
balances failure-test cases and security-test cases per ADR rationale
in REVIEW_CREWS.yaml."
```

### Task 10.8: Author IPLAN playbooks (6 files)

**Files:**

- Create: `framework/playbooks/08_IPLAN/tech_lead.md` (weight 30)
- Create: `framework/playbooks/08_IPLAN/architect.md` (weight 25)
- Create: `framework/playbooks/08_IPLAN/operator.md` (weight 15)
- Create: `framework/playbooks/08_IPLAN/integration_lead.md` (weight 12)
- Create: `framework/playbooks/08_IPLAN/auditor.md` (weight 10)
- Create: `framework/playbooks/08_IPLAN/chaos_engineer.md` (weight 8)

| Lens | Key checks |
|---|---|
| tech_lead | (a) Each step has exact commands + expected output; (b) prerequisites enumerated; (c) implementation contracts referenced (per IMPL_CONTRACTS_GUIDE); (d) commit boundaries explicit; (e) verification step per task |
| architect | (a) Sequencing respects dependencies; (b) component-level concerns surface at appropriate task; (c) ADR consumption traceable; (d) deployment-environment assumptions explicit; (e) rollback boundaries align with deploy boundaries |
| operator | (a) Deploy procedure stated; (b) health-check criteria post-deploy; (c) runbook delta named; (d) on-call paging path stated; (e) capacity-impact estimated |
| integration_lead | (a) External-system coordination steps explicit; (b) version-pin updates; (c) compat-window noted (deprecation, sunset); (d) feature-flag rollout sequenced; (e) integration-smoke verification |
| auditor | (a) Task IDs conform; (b) cross-refs to TDD/SPEC resolve; (c) commit-message convention enforced; (d) doc-of-record updates listed (CHANGELOG/ROADMAP/HANDOFF/CLAUDE.md); (e) Document Control on IPLAN doc |
| chaos_engineer | (a) Rollback procedure documented per task; (b) failed-deploy recovery stated; (c) data-corruption recovery if applicable; (d) failure-injection-during-deploy strategy; (e) rollback-during-rollback contingency |

- [ ] **Step 1-2: Author + commit**

```bash
git add framework/playbooks/08_IPLAN/
env -u LD_LIBRARY_PATH git commit -m "feat(framework): IPLAN playbooks (6 lenses)

Crew weights 30/25/15/12/10/8 sums to 100. Chaos-only (8) reflects
IPLAN's procedural deploy/rollback focus; threat model lives upstream
in ADR/SPEC."
```

- [ ] **Final coverage check after all 45 playbooks**

```bash
env -u LD_LIBRARY_PATH python3 -m unittest tests.conformance.test_playbook_coverage tests.conformance.test_playbook_frontmatter -v 2>&1 | tail -15
```

Expected: both test classes PASS. 0 missing files.

---

## Phase F — Lint hook + acceptance + landing

### Task 11: Extend sync-version-refs.sh for playbook frontmatter propagation

**Files:**

- Modify: `scripts/sync-version-refs.sh`

- [ ] **Step 1: Read the existing framework-version section**

```bash
sed -n '155,205p' scripts/sync-version-refs.sh
```

The hook already propagates `framework_spec_version: "X.Y.Z"` across 52 SKILL.md files. We add the 45 playbook files.

- [ ] **Step 2: Add playbook propagation**

Add this block right after the existing SKILL frontmatter propagation, inside `if [[ -n "$fw_ver" ]]; then ... fi`:

```bash
  # Playbook frontmatter declares framework_spec_version: "X.Y.Z" too —
  # propagate via the same detected-prev pattern as SKILLs.
  pb_fw_prev="$(detect_version_in \
    framework/playbooks/01_BRD/architect.md \
    'framework_spec_version: "[0-9]+\.[0-9]+\.[0-9]+"')"
  if [[ -n "$pb_fw_prev" && "$pb_fw_prev" != "$fw_ver" ]]; then
    log "  playbook frontmatter sync $pb_fw_prev -> $fw_ver (45 files)"
    for pb in framework/playbooks/*/*.md; do
      [[ -f "$pb" ]] || continue
      replace_in_file "$pb" \
        "framework_spec_version: \"$pb_fw_prev\"" \
        "framework_spec_version: \"$fw_ver\""
    done
  fi
```

- [ ] **Step 3: Smoke test the hook in standalone mode**

```bash
bash scripts/sync-version-refs.sh --verbose 2>&1 | grep -i playbook
```

Expected: nothing (no version mismatch right now; both VERSION and playbooks are at 0.14.0).

- [ ] **Step 4: Commit**

```bash
git add scripts/sync-version-refs.sh
env -u LD_LIBRARY_PATH git commit -m "feat(scripts): extend sync-version-refs.sh for playbook frontmatter

Auto-propagates framework_spec_version into all 45 playbooks when
framework/VERSION bumps. Mirrors the existing 52-SKILL.md fanout."
```

### Task 12: Smoke acceptance (dry-run brief composition)

**Files (read-only check; no edits):**

- Read: `tests/scripts/test-acceptance.sh` (verify dry-run flag)
- Read: `examples/url-shortener/.aidoc/review/01_BRD/BRD-01/<lens>.json` (sample brief)

> **Plan-review note (Pass 1 finding 1):** The CLAUDE.md-mandated two-cycle plan review (Pass 1 + Pass 2) happens against THIS plan file BEFORE the impl PR opens — see `## Review log` at the end of this document. It is NOT a step inside the impl-execution flow. Task 12-15 below are the impl-execution steps only.

**Files:**

- Modify: `CHANGELOG.md` (root)
- Modify: `platforms/claude-code-plugin/CHANGELOG.md`
- Modify: `ROADMAP.md`
- Modify: `plans/HANDOFF.md`
- Modify: `CLAUDE.md` (current-state line)
- Modify: `docs/PARITY.md`
- Modify: `plans/HERMES-BACKLOG.md` (add H-4 entry)
- Modify: `platforms/claude-code-plugin/VERSION` (minor bump)
- Modify: `plans/LAYER-PLAYBOOKS-001-PLAN.md` (add Review log section with Pass 1 + Pass 2)

#### Step 1: Smoke acceptance (dry-run brief composition for BRD)

- [ ] **Step 1.1: Identify the dry-run flag**

```bash
grep -n -- '--dry-run' tests/scripts/test-acceptance.sh | head -5
```

If `--dry-run` is supported in the cascade phase, use it. If not, the brief composition can be exercised by setting `CLAUDE_PLUGIN_ROOT` + running a single audit SKILL invocation with `--print` (no LLM call) — adapt to the harness's actual capabilities.

- [ ] **Step 1.2: Run brief-composition smoke**

```bash
bash tests/scripts/test-acceptance.sh url-shortener --dry-run --phase=cascade --from-layer=brd --to-layer=brd 2>&1 | tee tmp/playbook-smoke.log | tail -20
```

Inspect for the `## Layer-specific playbook` section in the composed brief. Grep:

```bash
grep -c '## Layer-specific playbook' tmp/playbook-smoke.log
```

Expected: at least 1 (one per dispatched lens; ≥4 for BRD).

Pass criteria: brief composition includes playbook content, no missing-playbook errors, no schema errors.

#### Step 2: Live acceptance run (single layer — BRD)

- [ ] **Step 2.1: Run live BRD cascade**

```bash
bash tests/scripts/test-acceptance.sh url-shortener --live --phase=cascade --from-layer=brd --to-layer=brd 2>&1 | tee tmp/playbook-live-brd.log | tail -30
```

Wall-clock budget: ~15-20 min for BRD (single-layer cascade).

- [ ] **Step 2.2: Inspect findings + verdict**

```bash
python3 -c "
import json
v = json.load(open('examples/url-shortener/.aidoc/review/01_BRD/BRD-01/verdict.json'))
print(f'combined={v[\"combined_status\"]} score={v[\"content_score\"]} blocking={v[\"blocking_findings_count\"]}')
print(f'lens_scores={v[\"lens_scores\"]}')
print(f'playbook_coverage={v.get(\"playbook_coverage\",{})}')
print(f'findings (count by check):')
from collections import Counter
c = Counter(f.get('check','<missing>') for f in v.get('findings',[]))
for k, n in c.items(): print(f'  {k}: {n}')
"
```

**Pass criteria** (per design risk-section):

- `combined_status == PASS` (any layer score)
- `coverage.quorum_met == true`
- ≥ 60% of findings cite a checklist check (`C1..Cn`, not `beyond-checklist:`)
- BRD score within ±3 of pre-playbook baseline of 96 (so: 93–100)
- No findings with `check: "<missing>"` — those would be schema-failure

If pass criteria not met, treat as miscalibration. Iterate per the structure below — do NOT proceed to merge until live acceptance passes.

- [ ] **Step 2.3: Iterate-on-failure (if pass criteria not met)**

  For each failed pass criterion:

  **If score regression > 3 (e.g. BRD < 93)**: the playbook checklist is too aggressive — flagging items as P0/P1 that the layer doesn't warrant. Soften priority assignments in the failing lens's playbook (e.g., demote `Missing → P1` to `Missing → P2`). Re-commit the playbook diff. Re-run Step 2.1.

  **If checklist-cited ratio < 60%**: the playbook checklist is too narrow — lenses are escaping to `beyond-checklist:` because the checks don't anticipate the real findings. Add 1-2 new `Cn` checks to the failing lens's playbook based on the beyond-checklist findings' principle tags. Re-commit. Re-run Step 2.1.

  **If coverage.quorum_met == false**: a lens failed with `BRANCH_FAILED` reason "playbook missing" — a playbook file was added to crew without authoring (caught by conformance test) OR a frontmatter is malformed (caught by frontmatter test). Inspect Task 2/3 conformance results; fix the failing playbook file.

  **If a finding has `check: "<missing>"`**: schema enforcement bug. Inspect `finding_filter.filter_findings` (Task 6); the filter should never let a missing-check finding through. File as a Phase D regression and fix the helper before re-running.

  Maximum 3 iteration rounds per layer. If still failing, halt the plan and escalate — the playbook for that layer needs human design review beyond what this PR can resolve.

#### Step 3 [removed: see plan-review note at top of Task 12]

#### Step 4: Doc-of-record updates (all in this same task; per "Update docs of record per PR" rule)

- [ ] **Step 4.1: Bump plugin VERSION (0.6.5 → 0.7.0)**

Current plugin VERSION confirmed at plan-write time: `0.6.5`. Bump to `0.7.0` (semver minor — plugin consumes a new framework artifact class). If current VERSION differs from 0.6.5 at execution time (subsequent PRs may have bumped it), use the next-minor value relative to the actual current.

```bash
cat platforms/claude-code-plugin/VERSION  # expect 0.6.5 at execution time (or later)
echo "0.7.0" > platforms/claude-code-plugin/VERSION
```

The `sync-version-refs.sh` hook will propagate this to `plugin.json`, `marketplace.json`, all 52 `SKILL.md` frontmatters, `README.md`, `platforms/claude-code-plugin/README.md`, `docs/SKILL_AUTHORING.md`, `docs/PARITY.md` on the next commit. NOTE: Task 11's playbook propagation extension is required for the hook to handle the 45 playbook frontmatters; that should already be in place before this step (Phase F sequencing).

- [ ] **Step 4.2: Root CHANGELOG entry**

Add to `CHANGELOG.md` under `## [Unreleased]`:

```markdown
### Added
- **Framework Spec 0.13.1 → 0.14.0** — adds Layer Playbooks
  (`framework/playbooks/<NN>_<LAYER>/<lens>.md`) as a new artifact
  class. Each (layer, lens) pair gets a layer-specific reasoning
  frame + deterministic checklist + beyond-checklist escape hatch.
  Synthesizer enforces a new required `findings[].check` field;
  uncited findings are discarded. New `verdict.playbook_coverage`
  field. See plans/LAYER-PLAYBOOKS-001-{DESIGN,PLAN}.md.
- **Claude Code plugin `<PV>` → `<NEW_PV>`** — consumes 0.14.0 by
  inlining playbook content into per-lens Task briefs across all 8
  audit SKILLs. Synthesizer agent gains finding-filter +
  coverage-emission helpers (stdlib-only).
```

- [ ] **Step 4.3: Plugin CHANGELOG entry**

Add to `platforms/claude-code-plugin/CHANGELOG.md`:

```markdown
## [<NEW_PV>] — YYYY-MM-DD

### Added
- Playbook injection in all 8 audit SKILLs (brd, prd, ears, bdd, adr,
  spec, tdd, iplan). Each loads
  `framework/playbooks/<NN>_<LAYER>/<lens>.md` and inlines the content
  into each lens subagent's Task brief.
- `tools/playbook_loader.py` — stdlib helper for path resolution +
  missing-file handling.
- `tools/finding_filter.py` — synthesizer's check-citation filter +
  coverage-emission helper.
- `agents/synthesizer.md` — schema-enforcement + `playbook_coverage`
  emission per LAYER-PLAYBOOKS-001.

### Changed
- `FRAMEWORK_SPEC_VERSION` 0.13.1 → 0.14.0 (consumes new spec).
```

- [ ] **Step 4.4: ROADMAP update**

In `ROADMAP.md`, find the current phase and add a bullet under "Shipped":

```markdown
- ✅ Layer Playbooks (LAYER-PLAYBOOKS-001) — 45 per-(layer, lens)
  playbooks calibrate review-team findings; deterministic checklist
  floor + beyond-checklist escape hatch.
```

- [ ] **Step 4.5: HANDOFF.md narrative**

Append to `plans/HANDOFF.md`:

```markdown
## YYYY-MM-DD — LAYER-PLAYBOOKS-001 shipped

Framework spec bumped to 0.14.0 (new artifact class: playbooks). 45
playbook files across all 8 layers calibrate the review-team's
content-quality findings. Plugin v<NEW_PV> wires playbook injection
into all 8 audit SKILLs. Synthesizer enforces finding-check citation;
uncited findings are discarded. Live BRD acceptance run posted score
<X>/100 with <Y>% checklist-cited findings.

Next: <next-step pointer — EARS-RT-001? backfill PRD live run?>
```

- [ ] **Step 4.6: CLAUDE.md current-state line**

In `CLAUDE.md`, update the `Current state (as of YYYY-MM-DD):` paragraph to reference framework 0.14.0 + plugin `<NEW_PV>` + mention layer playbooks.

- [ ] **Step 4.7: PARITY.md update**

In `docs/PARITY.md`:

- Update current-state row to framework 0.14.0 + plugin `<NEW_PV>`.
- Add a new feature row: `Layer Playbooks | ✅ all 8 layers | ⏳ deferred (HERMES-BACKLOG H-4)`.

- [ ] **Step 4.8: HERMES-BACKLOG entry**

Add to `plans/HERMES-BACKLOG.md`:

```markdown
### H-4. Layer Playbook Injection in Hermes Team-Mode (LAYER-PLAYBOOKS-001)

**Source:** PR LAYER-PLAYBOOKS-001 (plugin) shipped 45 playbooks at
`framework/playbooks/<NN>_<LAYER>/<lens>.md`. Hermes does not yet
consume them.

**Scope:** When Hermes implements team-mode lens fan-out, the lens
prompts must inline the (layer, lens) playbook content per the
framework spec contract in REVIEW_TEAM.md §Playbooks. Synthesizer
parity: enforce `findings[].check` citation; emit
`verdict.playbook_coverage`.

**Dependency:** Hermes team-mode (currently not implemented).
```

#### Step 5: Final commit + push

- [ ] **Step 5.1: Final commit batching all doc-of-record changes + plugin VERSION**

```bash
git add CHANGELOG.md platforms/claude-code-plugin/CHANGELOG.md \
        ROADMAP.md plans/HANDOFF.md CLAUDE.md docs/PARITY.md \
        plans/HERMES-BACKLOG.md platforms/claude-code-plugin/VERSION \
        plans/LAYER-PLAYBOOKS-001-PLAN.md

env -u LD_LIBRARY_PATH git commit -m "docs(layer-playbooks): doc-of-record updates + plugin minor bump

CHANGELOG (root + plugin), ROADMAP, HANDOFF, CLAUDE.md current-state,
PARITY.md, HERMES-BACKLOG H-4 entry, plugin VERSION bump to <NEW_PV>.
Plan's Review log records two passes of plan review (per CLAUDE.md
Development workflow item 2). Live BRD acceptance: <X>/100 with <Y>%
checklist-cited."
```

The sync-version-refs.sh hook will auto-propagate the plugin VERSION into plugin.json, marketplace.json, the 52 SKILL.md frontmatters, etc.

- [ ] **Step 5.2: Push**

```bash
env -u GH_TOKEN git push 2>&1 | tail -5
```

#### Step 6: Open the PR

- [ ] **Step 6.1: Verify branch state**

```bash
git log --oneline origin/main..HEAD | wc -l
git status --short
```

Expected: many commits ahead of main (one per Phase A-F task), clean working tree.

- [ ] **Step 6.2: Open PR via gh**

```bash
env -u GH_TOKEN gh pr create --title "LAYER-PLAYBOOKS-001: per-layer per-lens review playbooks (45 files)" --body "$(cat <<'EOF'
## Summary

- Adds 45 per-(layer, lens) playbooks calibrating the review-team's
  content-quality findings against each layer's known failure modes
- Framework spec 0.13.1 → 0.14.0 introduces the playbook contract in
  REVIEW_TEAM.md §Playbooks
- Plugin <PV> → <NEW_PV> wires playbook injection into all 8 audit
  SKILLs + synthesizer enforces finding-check citation
- See plans/LAYER-PLAYBOOKS-001-{DESIGN,PLAN}.md for full design +
  implementation history

## Test plan

- [x] Conformance: test_playbook_coverage + test_playbook_frontmatter
- [x] Unit: test_playbook_loader + test_finding_check_field
- [x] Smoke: dry-run brief composition for BRD cascade
- [x] Live: BRD cascade with playbook injection — score <X>/100 with
      <Y>% findings cited via checklist (≥60% target met)
- [x] Plan two-cycle review completed (Pass 1 + Pass 2 logged in plan)
EOF
)"
```

- [ ] **Step 6.3: Record PR number in HANDOFF.md and push if needed**

PR is now live. STOP — wait for user review / merge before any further work in this stream.

---

## Self-review (per writing-plans skill)

This section MUST be completed before the plan is considered "ready". Walk the spec end-to-end against the plan as a final check.

### Spec coverage

- ✅ Framework contract in REVIEW_TEAM.md §Playbooks → Task 1
- ✅ 45 playbooks → Tasks 10.1–10.8 (BRD 5 + PRD 6 + EARS 5 + BDD 6 + ADR 6 + SPEC 5 + TDD 6 + IPLAN 6 = 45)
- ✅ 8 audit SKILL extensions → Task 8 sub-steps 2–9
- ✅ Synthesizer schema extension → Task 9
- ✅ Conformance tests (coverage + frontmatter) → Tasks 2 + 3
- ✅ Unit tests (loader + finding-filter) → Tasks 4 + 5
- ✅ Sync hook extension → Task 11
- ✅ VERSION bumps (framework + plugin + FRAMEWORK_SPEC_VERSION) → Task 1 + Task 12 Step 4.1
- ✅ Doc-of-record (CHANGELOG/ROADMAP/HANDOFF/CLAUDE.md/PARITY/HERMES-BACKLOG) → Task 12 Steps 4.2–4.8
- ✅ Live acceptance with pass criteria → Task 12 Step 2
- ✅ Plan two-cycle review (mandatory) → Task 12 Step 3 + executed in this PR's Review log

### Placeholder scan

The plan contains `<NEW_PV>` and `<X>/100 with <Y>%` as **deliberate** placeholders to be filled with actual values during execution (plugin VERSION not yet computed; live acceptance not yet run). These are NOT "TBD" — they're variables resolved by Phase F. Every other content step has full code/text.

### Type consistency

- `PlaybookMissingError` defined in Task 7, referenced in Task 4 test — identical spelling ✓
- `resolve_playbook_path` + `load_playbook` defined in Task 7, referenced in Task 4 test ✓
- `filter_findings` + `emit_coverage` defined in Task 6, referenced in Task 5 test ✓
- `BEYOND_PREFIX = "beyond-checklist:"` used consistently in Task 6 + Task 5 test ✓
- `findings[].check` field name consistent across schema docs, synthesizer.md edit, and unit tests ✓

### Scope check

Plan covers exactly the design's in-scope items. Out-of-scope items (inheritance, profile overrides, cross-layer findings, generation tooling, Hermes parity, calibration-only iterations) are NOT addressed here — Hermes parity is filed as H-4 in HERMES-BACKLOG.md per the plugin-first policy.

---

## Review log

*Mandatory per CLAUDE.md "Two-cycle plan review is mandatory — BEFORE the plan PR opens." Cycles executed against this draft prior to the initial commit of this plan file. Each cycle = review → patch → re-review.*

### Pass 1 — 2026-06-07

Reviewer: Claude (plan author, fresh-eyes self-review).

Findings:

1. **Confused 2-cycle-review placement (CRITICAL).** Task 12 Step 3 was structured as "execute 2-cycle plan review during impl execution." That conflicts with the worked sequence in CLAUDE.md §"Development workflow" — cycles happen BEFORE the plan PR opens, against the plan draft. Patched: removed Task 12 Step 3; added plan-review note at top of Task 12 pointing to this Review log section; the cycles happen here, pre-commit.

2. **`tests/unit/` existence not verified (CRITICAL).** Tasks 4–5 reference `tests/unit/test_*.py`; I did not pre-verify the directory. Patched: confirmed via `ls -d tests/unit/` → exists. Existing siblings include `test_nonlayer_skills.py`, `test_sdd_doc_lint_struct01.py`, `test_sync_scripts.py`. No change to paths in plan required; finding logged for traceability.

3. **Task 9 synthesizer.md edit too vague (CRITICAL).** Original said "Locate the verdict.json schema section..." without showing existing structure. Patched: Task 9 Step 1 now lists the confirmed section structure (Inputs/Reduce/Narrative/The gate/Output → verdict.json/report.md → Hard Constraints/Related Resources) with line-number anchors and exact insertion targets (new `### Playbook check-citation enforcement` subsection at end of `## Reduce`; new field in `### 1. verdict.json`; new subsection in `### 2. report.md`).

4. **Concrete VERSION values missing (CRITICAL).** Task 12 Step 4.1 used `<PV>` / `<NEW_PV>` placeholders. Patched: Step 4.1 now states PV=0.6.5 → NEW_PV=0.7.0 explicitly. CLAUDE.md's current-state line at 0.6.2 is stale (file confirmed at 0.6.5); plan notes the bump is relative to actual at execution time.

5. **Task 12 oversized (IMPORTANT).** Originally bundled smoke + live + 2-cycle review + doc-of-record + PR-open. After removing 2-cycle review (Pass 1 finding 1), task is more manageable. Patched: kept as Task 12 with substep structure; rejected proposed split into Tasks 12-15 because the substeps are tightly coupled (live acceptance pass → doc-of-record entries reference the actual live-run results) and splitting would require passing state across tasks.

6. **Iterate-on-failure branch missing (IMPORTANT).** Original Task 12 Step 2 said "iterate playbooks if live acceptance fails" without structure. Patched: added Step 2.3 with explicit branch per failure mode (score regression / checklist-cited ratio / quorum / schema-bug), max 3 iteration rounds, escalation path.

7. **SKILL insertion locator hand-wavy (IMPORTANT).** Original Task 8 said "Locate the team-mode section, insert after step 3." Patched: added explicit pre-check grep matching `^3\. \*\*Map each lens to its plugin agent\*\* via the table in` across all 8 SKILLs (expected count: 8) + halt-and-inspect instruction if locator misses.

8. **Content-authoring not-TDD note missing (IMPORTANT).** Tasks 10.1–10.8 don't follow TDD per writing-plans skill default. Patched: added preamble note to Phase E explaining the TDD-exception (the conformance tests from Phase B are the "test" for playbook existence + frontmatter; content quality is validated by live acceptance).

9. **Calibration risk for EARS+ layers (NICE-TO-HAVE).** BRD/PRD playbooks calibrate against live cascade findings; EARS+ are a-priori. Patched: noted as a design risk in Phase E preamble; iterate-on-failure (Pass 1 finding 6) handles per-layer miscalibration at execution time.

10. **Hook propagation note in Task 1 (NICE-TO-HAVE).** Task 1 Step 4 didn't explain that the sync hook doesn't yet propagate to playbooks (Task 11 extends it); playbook authoring in Phase E must hardcode `"0.14.0"` since Task 11 lands in Phase F. Patched: added clarifying note to Task 1 Step 4.

Skipped (deferred): cross-playbook altitude consistency check (manual review during authoring), PR-size acknowledgment (no rule violation), final brief visual inspection (implicitly covered by grep count).

10 findings, 10 patches applied inline. Plan re-read after patches confirms internal consistency.

### Pass 2 — 2026-06-07

Reviewer: Claude (re-review after Pass 1 patches, fresh-eyes pass focused on cycle-N+1 invariant — verifying Pass 1 patches did not introduce new gaps).

Findings:

1. **Pass 1 patch 1 introduced a forward-reference (MINOR).** The plan-review note at top of Task 12 says "see `## Review log` at the end of this document." That's a forward reference within a single file — acceptable. Re-check: the Review log section exists at end of file with Pass 1 + Pass 2 entries. No fix needed.

2. **Pass 1 patch 5 (Task 12 NOT split) creates a long single task — could this cause executor confusion (MINOR)?** Task 12 has 5 substeps (Smoke / Live / [removed] / Doc-of-record / PR-open) with 16 numbered sub-substeps total. Re-read for clarity: each substep has its own header (`#### Step N: ...`); each sub-substep has a checkbox + bash code or text. Structure is navigable. No fix needed. If executor reports confusion mid-execution, a refactor PR splits Task 12 then.

3. **Pass 1 patch 6 (iterate-on-failure) introduces a recursive structure not bounded earlier (MINOR).** Step 2.3 says "Re-run Step 2.1" up to 3 rounds. Cross-check: Step 2.1 is `bash test-acceptance.sh url-shortener --live ...`, idempotent and repeatable. The 3-round cap prevents infinite loops. Step 2.3 final paragraph specifies escalation. No fix needed.

4. **Pass 1 patch 3 (Task 9 exact-text) added confirmed line-number anchors (~33, ~40, ...) — could these drift (MINOR)?** Line numbers were captured at plan-write time (2026-06-07). If subsequent PRs edit synthesizer.md, the anchors drift. Cross-check: Task 9 Step 2 instructs to insert AT END of `## Reduce` (named section, not line-anchored). Step 3 says AT END of `### 1. verdict.json` schema (named, not line-anchored). Line numbers are informational, not load-bearing. No fix needed.

5. **Pass 1 patch 4 noted CLAUDE.md current-state stale at 0.6.2 (MINOR).** Plan doesn't include a step to update CLAUDE.md's current-state from 0.6.2 to 0.6.5 → 0.7.0 + framework 0.14.0. Cross-check: Task 12 Step 4.6 explicitly says "update the `Current state (as of YYYY-MM-DD):` paragraph to reference framework 0.14.0 + plugin `<NEW_PV>`" — this WILL update 0.6.2 to 0.7.0 in one edit. Covered.

6. **Type-consistency re-check.** All four named types/functions from the self-review section (PlaybookMissingError, resolve_playbook_path/load_playbook, filter_findings/emit_coverage, BEYOND_PREFIX) still consistent across pre-patch + post-patch text. No drift.

7. **Pass 2 surfaces no new substantive gaps beyond MINOR consistency-checks above.**

Pass 2 verdict: ZERO substantive gaps remain. Per CLAUDE.md rule "final pass surfaces zero substantive gaps → OPEN plan PR", this draft is ready for plan PR after commit + push.

Total: 2 passes, 10 + 7 findings, all addressed. Plan ready to commit.
