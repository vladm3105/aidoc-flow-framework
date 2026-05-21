# P5-T5 Verify Record — Phase 5 cutover (consolidated final gate)

| Field         | Value                                |
|---------------|--------------------------------------|
| Branch        | `claude/multi-platform-migration-AamWB` |
| Verify run at | 2026-05-21T09:10:00Z                 |
| HEAD          | `cae9ee0` (P5-T3 close)              |
| Baseline      | `954d8da` (`v0.5.0`, Phase-4 close) for scope gates |
| Verdict       | **PASS** — all 17 gates green        |
| Feeds         | P5-T6 close + cutover (`CHANGELOG [1.0.0]`, tag `v1.0.0`, user `main` force-replace) |

Final consolidated verify for the cutover phase. Mirrors
`plans/P4-T5-VERIFY.md` / `plans/P3-T4-VERIFY.md` /
`plans/P2-T5-VERIFY.md` in shape. Confirms the two destructive
removals (P5-T2 `legacy/`, P5-T3 root `.claude/`) landed cleanly,
docs are finalized (P5-T4), and the shipped tree is the intended
v1.0.0 state. **No new issues; one carried known issue was
resolved** this phase (the api_runner install string).

## Group 1 — Conformance + suites

### G1. Conformance suite — PASS (31 / 31)

```
python3 -m unittest discover -s tests/conformance
=> Ran 31 tests, OK
```

Unchanged from P4 close — Phase 5 touched neither `framework/` nor
the suite. The `\.claude/` forbidden-token check in
`test_spec_hygiene.py` scans `framework/` content (not the removed
root loader), so the `.claude/` removal does not affect it.

### G2. Hermes own suite — SKIPPED (justified)

The only Phase-5 platform-code change is the **documented 1-line
api_runner fix** (G8); the full 447-test suite re-run requires a
Python-3.12 venv rebuild and is not warranted for a one-line error-
string correction. Last known green: 447 / 447 at P3-T4 verify.

## Group 2 — Both destructive removals landed

### G3. In-tree `legacy/` removed — PASS

```
git ls-files legacy/  => 0 (tracked)
```

11 git-ignored `legacy/tmp/` scratch files linger on disk locally
(same class as G4's leftover); **untracked, so they do not
propagate** to the force-replaced `main`. Content preserved in the
protected `legacy-ucx-v3.2-read-only` archive branch + git history.

### G4. Root `.claude/` loader removed — PASS

```
git ls-files .claude/  => 0 (tracked)
on disk: only .claude/settings.local.json (git-ignored)
```

The lone leftover is the git-ignored local-settings file — untracked,
won't propagate. Content preserved three ways: productized in
`platforms/claude-code-plugin/`; pre-migration `.claude/` in the
archive branch; migration-era `.claude/` (incl. the 3 hooks) in
working-branch git history.

## Group 3 — Archive + versions + plugin smoke

### G5. Archive branch intact — PASS

```
git ls-remote origin legacy-ucx-v3.2-read-only
=> 491e8db…  refs/heads/legacy-ucx-v3.2-read-only
```

Exactly the old `main` tip — makes the P5-T6 force-replace lossless.

### G6. FRAMEWORK_SPEC_VERSION match — PASS

```
framework/VERSION                                  => 0.1.0
platforms/hermes/FRAMEWORK_SPEC_VERSION             => 0.1.0
platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION => 0.1.0
```

All three identical (also enforced by G1's conformance test).
Framework stays `0.1.0` per P5-T1 Q2.

### G7. Plugin smoke — PASS

```
plugin skill dirs => 142
python3 -m json.tool < .../.claude-plugin/plugin.json => valid JSON
```

## Group 4 — Scope discipline

### G8. Phase-5 footprint is removals + docs + one tracked fix — PASS

`git diff --name-only 954d8da..HEAD`, grouped by top-level:

| Path group | Files | What |
|------------|-------|------|
| `legacy/`  | 2276  | P5-T2 removal |
| `.claude/` | 240   | P5-T3 removal |
| `platforms/` | 1   | **api_runner fix** (`23ae664`, see below) |
| `docs/`    | 2     | P5-T4 finalize (REPO_STRUCTURE, PROJECT) |
| `README.md` `CLAUDE.md` `CHANGELOG.md` | 3 | P5-T4 finalize + fix changelog record |
| `plans/`   | 10    | task plans + trackers |

**`framework/` = 0 changes** — the spec was untouched all phase
(P5-T1 Q2). The single `platforms/` change is the resolution of
**P4-T5 carried known issue #1**: `api_runner.py:115` install string
`ucx_hermes[api]` → `hermes-server[api]` (`23ae664`), recorded in
`CHANGELOG [Unreleased]` (`e8ea865`) and destined for the optional
`hermes/v0.1.1` patch tag (P5-T1 Q4 / P5-T6). Not a scope violation
— a tracked, documented fix.

## Group 5 — No dangling runtime references to the removed dirs

### G9. No root-`legacy/` runtime path refs — PASS

Sweep of `framework/ platforms/*/src platforms/*/skills tests/`:
**1 match, a false positive** —
`platforms/claude-code-plugin/skills/doc-brd-autopilot/SKILL.md:261`
reads "Detect ALL legacy/source ID patterns", i.e. the prose phrase
*legacy-or-source*, not a path into the removed `legacy/` directory.
No runtime dependency on the removed tree.

### G10. No root-`.claude/` runtime path refs — PASS

Sweep of `framework/ platforms/*/src tests/` (excluding the plugin's
own `.claude-plugin/` manifest path + the `test_spec_hygiene.py`
forbidden-token pattern): **0 hits.** Nothing in the shipped runtime
trees reads the removed root loader.

## Group 6 — Docs finalized (P5-T4) + shipped tree

### G11. README finalized — PASS

```
'legacy/' mentions => 0 ; archive-branch pointer => 1
```

Migration framing + `legacy/` dropped from the structure diagram;
archive branch named.

### G12. CLAUDE.md rewritten — PASS

```
'Phase 1 — Framework Spec' migration framing => 0 ; archive pointer => 1
```

Now post-migration project memory (root file; survived the P5-T3
`.claude/` removal per P5-T1 Q6).

### G13. REPO_STRUCTURE as-built — PASS

```
'PLANNED' occurrences => 0
```

### G14. Shipped top-level tree — PASS

```
.github .gitignore .mcp.json .pre-commit-config.yaml .vscode
CHANGELOG.md CLAUDE.md LICENSE README.md ROADMAP.md
docs framework plans platforms tests
```

**No `legacy/`, no `.claude/`** top-level entries — both removals
confirmed at the tree level. The shipped project = `framework/` spec
+ `platforms/{hermes,claude-code-plugin}/` + `tests/` + `docs/` +
`plans/` (audit trail, P5-T1 Q5) + root project files.

### G15. Working tree clean — PASS

```
git status --porcelain => (empty)
```

The git-ignored leftovers (G3/G4) correctly do not appear.

## Group 7 — Release readiness

### G16. CHANGELOG state — PASS (pre-1.0.0, as expected)

```
## [Unreleased]      <- holds the api_runner fix
## [0.5.0] — 2026-05-21
## [0.4.0] … [0.2.0]
```

The `[1.0.0]` entry is authored in **P5-T6** (this verify precedes
the close), so its absence is correct, not a gap.

### G17. Branch synced with remote — PASS

```
HEAD            => cae9ee0
@{u} (origin)   => cae9ee0
```

All Phase-5 work is pushed; nothing local-only at risk.

## Verdict

**PASS — all 17 gates green.** Phase 5's structural work (two
removals + doc finalization + the carried api_runner fix) is
complete and verified. Ready for **P5-T6** — the close commit
(`CHANGELOG [1.0.0]`, ROADMAP Phase-5 marking) + tags (`v1.0.0`
project; optional `hermes/v0.1.1`) + the **user-authorized `main`
force-replace** (tag pushes + force-replace are user-local-clone
actions; the in-container session does not push to `main` or
`refs/tags/*`).

### Carried known issues (net −1 this phase)

1. ~~api_runner.py:115 stale install string~~ — **RESOLVED** this
   phase (`23ae664`); in `CHANGELOG [Unreleased]`, ships under the
   optional `hermes/v0.1.1` tag at P5-T6.
2. **CI workflows pending relocation** (P4-T3 carry-over) — user
   `git mv plans/workflows-pending/*.yml .github/workflows/` from a
   local clone; ideally before the `v1.0.0` tag so CI runs on the
   cutover commit.
3. **Plugin layer-model gap** (missing `doc-tdd` + `doc-iplan`;
   documented in `docs/PARITY.md`) — post-v1.0 per-skill content
   migration; **not a v1.0.0 blocker** (P5-T1 Q3).
4. **~150 Class D stale `framework/<X>` refs in the plugin** (P3-T2
   G18) — same root cause as #3; post-v1.0 cleanup.

### Cutover-mechanics reminder (for P5-T6)

The `main` replacement is a **force-replace** (P5-T1 Q1; histories
diverged, FF impossible, lossless because the old `main` is the
protected archive branch). It is **user-authorized + user-executed**
from a local clone after temporarily lifting `main` branch
protection. The in-container session never pushes to `main`.
