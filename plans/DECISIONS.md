# Decisions — repo working log (per CLAUDE.md)

Non-obvious choices made during implementation work. ISO-stamped, newest first.
Spec-governance decisions live in `framework/governance/DECISIONS.md` (GD series);
this file records repo-process choices that do not belong in the spec.

## 2026-09-22 — CHG-05 implementation (bugfix vehicle, #656/#657)

- **Vehicle choice A (new `bugfix` subtype, not extended `audit_fix`).**
  `audit_fix` guidance is audit-shaped (severity-ordered findings, no TDD); contorting
  it to cover field defects would blur both contracts. New subtype keeps each
  contract readable; `combined` default untouched.
- **Greenfield `sdd_doc_lint/bugfix_lint.py` over extending `chg_lint.py`.**
  BGF checks validate IPLAN docs, not CHG docs; folding them into the CHG linter
  would couple two lifecycles. `chg_lint.py` untouched by design.
- **Linter wiring: CI-only, no pre-commit entry.**
  A pre-commit hook scoped to `IPLAN-*_bugfix_*` filenames would match zero tracked
  files, tripping `test_precommit_trigger_reachability.py` unless exempted in
  `KNOWN_UNREACHABLE` — an exemption that weakens the guard for a hook with no
  current consumers. Enforcement runs in CI instead: `sdd_doc_lint/tests` (BGF unit)
  via `doc-review.yml`, and the BGF catalog-agreement guard inside
  `tests/conformance` (runs on every PR via `chg-gate.yml`/`conformance.yml`).
  Authors run `bugfix_lint.py` manually. Revisit when the first real bugfix IPLAN
  lands in-tree.
- **TMP promise removed, not built.**
  Building a real `layers/08_IPLAN/tmp/` contract alongside the bugfix subtype would
  leave two competing lightweight vehicles. `tmp/` references now point at the
  bugfix vehicle with a retirement note.
- **Version confirm: MINOR `0.55.0 → 0.56.0`.**
  Additive template fields + governance prose + new lint checks; no removals, no
  registry shape change. Fanout via `hooks/sync-version-refs.sh` (+0.55.0 sweep
  lines); 116 files, pins only (verified: every changed version literal is a pin
  form; `framework/VERSION` itself is the one exception).
- **Corpus cross-check vacuous.**
  `examples/` was deleted by CLEANUP-001, so the `sdd_doc_lint examples/` check has
  no corpus. Coverage comes from `tests/acceptance/deterministic` (64 green, no
  golden churn) instead. Recorded so a future reader does not file it as a miss.
