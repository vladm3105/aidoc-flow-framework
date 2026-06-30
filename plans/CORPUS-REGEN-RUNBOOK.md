# Corpus Regeneration Runbook — regenerate the example corpus after framework changes

> **Why this exists.** The example corpus (`examples/url-shortener/docs/` +
> `.aidoc/`) is a **framework output**, not a hand-maintained artifact. After a
> run of framework-spec changes that alter templates, lint rules, playbooks, or
> the trace contract, the committed corpus drifts from what the current framework
> would produce — so a set of corpus-remediation findings are deliberately
> **deferred to a wholesale regen** rather than hand-patched (hand-editing example
> artifacts is forbidden — see `CLAUDE.md` "Never hand-edit example artifacts").
> This runbook is the procedure for that regen. It **must run in a live Claude
> Code plugin session** (the cascade dispatches the `doc-*-autopilot` skills); it
> cannot run in a framework-dev container.

## When to run

Run a wholesale regen when framework-spec changes since the corpus was last
produced have changed any of: layer
**templates**, **lint rules** (`sdd_doc_lint`), **playbooks**, the **trace
contract**, or **`@`-tag semantics**. As of this writing the corpus lags the spec
by the `0.29.x → 0.32.5` arc (YAML-BDD, element-level coverage, provisional IDs,
reuse, advisory scores, the sketch roadmap), so a regen is due.

## What a regen clears (the deferred backlog)

These `FRAMEWORK-TODO.md` items are **closed by the regen**, not by hand:

- **16 COV02 orphans** — BDD scenarios with no downstream SPEC/TDD at element
  level (surfaced by ELEMENT-COVERAGE-001; a fresh cascade authors the coverage).
- **`CORPUS-REFGRAN-RECASCADE`** — the 5 remaining SPEC/TDD/IPLAN doc-level
  `@adr`/`@tdd` tags re-cascaded to element granularity (GD-03/REFGRAN01).
- **`CORPUS-PRD-TH-RES`** — PRD-01's missing `component_decomposition` thresholds
  (11 unresolvable `@threshold:` citations).
- **`INDEX-UPSTREAM-RESIDUE`** (corpus side) — stale cumulative `Upstream:`
  enumerations in the corpus's layer index docs.

After a clean regen these drop out of the corpus baseline; close each TODO entry
with the regen commit ref.

## Procedure

All commands run from the framework repo root, in a live plugin session with the
`aidoc-flow` plugin installed (see `plans/PLUGIN-P2-DEPLOY-RUNBOOK.md` for install).
The driver and all its modes are documented in
[`tests/ACCEPTANCE.md`](../tests/ACCEPTANCE.md) §3 — this runbook sequences them for
a regen.

1. **Record the starting baseline** (for the diff at the end):

   ```bash
   PYTHONPATH=tools python -m sdd_doc_lint examples/url-shortener/docs/ \
     | grep -oE 'COV0[12]|REFGRAN01|STY02|TH-RES-001|STRUCT01|ID02|PROV01|REUSE0[12]' \
     | sort | uniq -c | tee /tmp/corpus-baseline-before.txt
   ```

2. **Cleanup-then-cascade** (the deterministic-start pattern — `ACCEPTANCE.md`
   §4 "Cleanup-then-cascade"): remove the layers being regenerated + their
   per-layer saga/audit state, then run the cascade with `--force`. For a
   *wholesale* regen, clear the whole produced chain:

   ```bash
   rm -rf examples/url-shortener/docs examples/url-shortener/.aidoc
   bash tests/scripts/test-acceptance.sh url-shortener --live --force
   ```

   (To regenerate only some layers, use `--from <LAYER>` / single-layer mode per
   `ACCEPTANCE.md` §3 Usage instead of the full `rm -rf`.)

3. **Verify — the gate.** A regen is accepted only when ALL hold:

   | # | Check | Expected |
   |---|-------|----------|
   | G1 | `bash tests/scripts/test-acceptance.sh url-shortener --dry-run` | green deterministic smoke (Phase 0, negative fixtures, hook) |
   | G2 | `python -m pytest tests/conformance -q` | green |
   | G3 | `PYTHONPATH=tools python -m sdd_doc_lint examples/url-shortener/docs/` | **no `STRUCT01`/`ID02`/`TRACE-RES-001` errors**; COV02 orphans resolved (or each explicitly `deferred:`); REFGRAN01 at element granularity; compare to `/tmp/corpus-baseline-before.txt` and account for every delta |
   | G4 | the chain's recorded version (`docs/.version`, per `ACCEPTANCE.md` §3 layout — established/updated by `--promote`) | matches the current plugin version |
   | G5 | the produced chain's `@`-tag chain resolves end-to-end (no dangling refs) | `python tools/trace_walk.py examples/url-shortener/docs/` clean |

4. **Promote** (commit the regenerated corpus):

   ```bash
   bash tests/scripts/test-acceptance.sh url-shortener --live --promote
   ```

   This stages + commits `docs/` + `.aidoc/` (see `ACCEPTANCE.md` §3.2 `--promote`).

5. **Close the backlog.** In `plans/FRAMEWORK-TODO.md`, move the four
   corpus-remediation items above to Closed with the regen commit ref; update
   `plans/HANDOFF.md`.

## Notes

- **Determinism:** element IDs are LLM-generated stable strings, **not** content
  hashes (see auto-memory `project-element-ids-not-deterministic`), so a regen will
  not reproduce byte-identical IDs — that is expected. The gate is *structural*
  (G2/G3/G5), not a byte-diff.
- **Cost:** a full live cascade exercises all active plugin elements; see
  `ACCEPTANCE.md` §3 for the cost ballpark.
- **Never hand-edit** a corpus artifact to "fix" a G3 finding — if a class of
  finding survives a clean cascade, that is a **framework/playbook gap**: fix the
  skill or template and re-cascade (`CLAUDE.md` "Never hand-edit example
  artifacts").
