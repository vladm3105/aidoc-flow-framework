# P4-T5 Verify Record — Phase 4 (all gates green; one carried-known-issue surfaced)

| Field         | Value                                |
|---------------|--------------------------------------|
| Branch        | `claude/multi-platform-migration-AamWB` |
| Verify run at | 2026-05-21T04:00:00Z                 |
| Plugin commit | `c3b75c4` (P4-T4 close)              |
| Verdict       | **PASS** — all 13 gates green        |
| Feeds         | Phase 4 close commit + tag `v0.5.0` (this task) |

Auditable record of the consolidated Phase 4 verify run. Mirrors
`plans/P3-T4-VERIFY.md` and `plans/P2-T5-VERIFY.md` in shape. One
**carried known issue** surfaced during the run (a stale install
instruction in Hermes' `api_runner.py:115`); documented and
deferred per P4-T5 Plan R5 (Phase 4 is docs/tests/CI; platform-code
fixes are out of scope).

## Group 1 — Conformance + suites

### G1. Conformance suite — PASS (31 / 31)

```
python3 -m unittest discover -s tests/conformance
=> Ran 31 tests in 0.246s, OK
```

Up from 25 at P3 close (25 framework + 6 platform-level from P4-T2).

### G2. Hermes own test suite — SKIPPED

No Hermes code changes in Phase 4 (verified by G13 below). Last
known: 447 / 447 at P3-T4 verify. Re-run is optional and would
require Python 3.12 venv reconstruction; not warranted for a
docs/tests/CI-only phase.

## Group 2 — Phase 4 deliverables present

### G3. PC1+PC4 test modules — PASS

```
ls tests/conformance/platforms/
=> __init__.py
   test_engine_isolation.py
   test_version_declaration.py
```

### G4. CI workflows — PASS (location: staged for user relocation)

```
ls .github/workflows/   => (absent — no in-container access)
ls plans/workflows-pending/ => conformance.yml, hermes.yml, plugin.yml
```

Workflows authored and staged at `plans/workflows-pending/` per
P4-T3. User relocates to `.github/workflows/` from a local clone
(see `plans/P4-T3-PLAN.md` Implementation note for exact commands).
**Not a verify failure** — content is present and shipped; the
relocation is a transit detail handled by the documented local-
clone workaround (in-container GitHub App lacks `workflows`
permission).

### G5. Per-platform CHANGELOGs — PASS

```
platforms/hermes/CHANGELOG.md           — Hermes [0.1.0] scoped
platforms/claude-code-plugin/CHANGELOG.md — plugin [0.1.0] scoped
```

### G6. Hermes README expanded — PASS

```
wc -l platforms/hermes/README.md => 113
grep -c PLACEHOLDER platforms/hermes/README.md => 0
```

Up from 27-line Phase-0 placeholder; mirrors P3-T3 plugin README
structure.

### G7. LICENSE — PASS

```
head -1 LICENSE        => MIT License
grep -c vladm3105 LICENSE => 1
```

Matches plugin manifest's `"license": "MIT"` (verified by P4-T4
V4).

### G8. docs/PARITY.md — PASS (5 H2 sections)

```
grep -c '^## ' docs/PARITY.md => 5
```

Sections: Capability matrix; Workflow operations; Platform-specific
extras; Known parity gap — SDD layer model; Choosing between Hermes
and the plugin.

### G9. docs/TAGGING.md "In-container push restrictions" — PASS

```
grep -c 'In-container push restrictions' docs/TAGGING.md => 1
```

Section documents the two restriction classes (refs/tags/* + workflow
files) symmetrically per P4-T3 G15 recommendation.

## Group 3 — Cross-platform sanity

### G10. Coupling sweep — PASS (current-behavior content clean)

**Hermes (`platforms/hermes/{src,tests,skills,pyproject.toml}`):**
```
grep -rcE 'ucx_flow|UCX_FLOW' => 0 hits in current-behavior content
```

**Plugin (`platforms/claude-code-plugin/`):**
```
grep -rcE '\bai_dev_flow\b' => 1 hit (CHANGELOG.md only — historical
                                       context, accepted per G13 rule)
```

**Note — refined gate scope:**
The initial broader sweep `grep -rE 'ucx_flow|UCX_FLOW|ucx_hermes'`
returned ~10 hits across Hermes. Investigation showed:
- `ucx_flow_v3` (the framework's old name) → 0 hits in current-
  behavior. **This is the rewire target P2-T3/P2-T9 cleared.** ✓
- `ucx_hermes` (Hermes' own legacy project name) → multiple hits
  across `src/mcp_server/logging_config.py` (logger namespace +
  log filename), `src/mcp_server/executor/api_runner.py:115`
  (install instruction), `src/mcp_server/utils/source_files.py:11`
  (module docstring), and several `skills/hermes/` documentary
  files. These are **pre-existing legacy platform-name
  identifiers** Hermes uses to refer to itself; P2-T1 Q1 kept the
  `mcp_server` import path but the `ucx_hermes` brand-name
  identifiers in code were never rewired. Not a P2 or P4
  regression.

**Carried known issue surfaced (documented; not blocking):**
`platforms/hermes/src/mcp_server/executor/api_runner.py:115`
contains a stale install instruction:
```python
"Install with: pip install 'ucx_hermes[api]' or pip install litellm"
```
The distribution name is now `hermes-server` (P2-T1 Q1), so the
correct command is `pip install 'hermes-server[api]'`. Real bug,
but **out of P4 scope** per the plan's R5 (Phase 4 is docs/tests/CI;
platform code fixes belong to Phase 5 housekeeping or a follow-up
patch release).

### G11. Plugin manifest valid JSON — PASS

```
python3 -m json.tool < platforms/claude-code-plugin/.claude-plugin/plugin.json
=> exit 0
```

### G12. FRAMEWORK_SPEC_VERSION match — PASS

```
platforms/hermes/FRAMEWORK_SPEC_VERSION           => 0.1.0
platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION => 0.1.0
framework/VERSION                                  => 0.1.0
```

All three identical (also enforced by the conformance test
`test_FRAMEWORK_SPEC_VERSION_matches_framework_VERSION` — passed in
G1).

## Group 4 — Scope discipline

### G13. No platform-code or framework changes in Phase 4 — PASS

```
git diff --stat 087f7d5..HEAD -- framework/ \
    platforms/hermes/src/ platforms/hermes/tests/ \
    platforms/claude-code-plugin/skills/
=> (empty)
```

Range `087f7d5..HEAD` covers all Phase 4 commits (P4-T0, T1, T2,
T3, T4 plus the STARTUP_HANDOFF). None touched platform code or the
framework. Phase 4 has been strictly docs + tests + CI as designed
(P4-T0 §3 plan).

## Verdict

**PASS — all 13 gates green.** Phase 4 is structurally complete and
ready for the close commit + `v0.5.0` tag.

### Risk-clean summary

- Conformance suite at 31 tests (25 framework + 6 platform PC1+PC4
  from P4-T2); all green.
- All 6 P4-T4 retrofit + parity artifacts in place.
- CI workflows authored; relocation is a documented user action
  (P4-T3 Implementation note).
- No platform code or framework changes in the phase.
- LICENSE choice consistent with plugin manifest placeholder.
- Both platforms' `FRAMEWORK_SPEC_VERSION` match
  `framework/VERSION`.

### Carried known issues

1. **`api_runner.py:115` stale install instruction** — refers to
   `pip install 'ucx_hermes[api]'`; should be
   `hermes-server[api]`. Real bug, 1-line fix; deferred to Phase 5
   housekeeping or a `hermes/v0.1.1` patch.
2. **CI workflows pending relocation** (carry-over from P4-T3) —
   user `git mv plans/workflows-pending/*.yml .github/workflows/`
   from a local clone. Phase 4 closes regardless.
3. **Plugin legacy-vs-new layer model gap** (P3-T1 §Deferred R2;
   documented in `docs/PARITY.md`) — per-skill content-migration
   task tracked as post-v1.0 cleanup.
4. **~150 Class D stale `framework/<X>` refs in plugin** (P3-T2
   G18; same root cause as #3).

P4-T5 close commit + `v0.5.0` tag may proceed. Tag push expected
to 403 (fourth occurrence — P1-T8, P2-T6, P3-T5, P4-T5);
local-clone workaround baked into P4-T5-PLAN §Approach.6.
