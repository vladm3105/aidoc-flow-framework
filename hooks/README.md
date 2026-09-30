# Hooks — event contract

This directory holds the repo's executable hooks plus `hooks.json`, the
engine-facing hook manifest. Two events are registered; both are
**advisory/warn-only** (always exit 0, never block).

| Event | Hook | Matcher | Timeout | Fires when |
|-------|------|---------|---------|------------|
| `PostToolUse` | `sdd-doc-review.sh` | `Write\|Edit` | 15 | An SDD instance document is written/edited — nudges the matching review skill |
| `PreCommit` | `ch-gate-check.sh` | `.*` | 10 | Before a commit lands — warns when code files ship with no active CHG |

## Honored-by whom

`PostToolUse` is the retained platform hook event (see `AGENTS.md`). `PreCommit`
has no retained engine consumer in this repo since the platforms were archived —
no live engine is proven to honor the `hooks.json` `PreCommit` registration.
The guaranteed execution path for the CHG gate is the
`.pre-commit-config.yaml` `chg-gate-check` hook (default `pre-commit` stage),
which invokes the same script. Adopters who only install `hooks.json`
`PreCommit` must verify their engine fires it, or wire the pre-commit hook
instead. (`ADAPTATION.md` §4 instructs adopters to install the script via
`hooks.json` `PreCommit`; treat the pre-commit hook as the fallback.)

## Other scripts (no engine event — CI/pre-commit wiring only)

- `check-docs-updated.sh` — document-of-record reminder (pre-commit).
- `pre_push_check.sh` — canon pre-push validation (`pre-push` stage):
  linters + audit-trail phrase + the three unittest suites
  (`tests/conformance`, `tests/unit`, `sdd_doc_lint/tests` — Invariant 1
  parity with CI; skipped-with-notice when python3 or suite deps are absent).
- `read-pin-currency-log.sh` / `reconcile-pin-currency-issue.sh` — pin-currency reader.
- `sync-version-refs.sh` — mechanical version-pin fanout (runs on
  `framework/VERSION` changes; see its header).

All scripts pass `bash -n`; hook commands resolve via `${AIDOC_ROOT:-.}`.
