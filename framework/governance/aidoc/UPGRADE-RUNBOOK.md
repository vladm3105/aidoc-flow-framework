# Consumer upgrade runbook — re-adopting a new `framework/VERSION`

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-29 |
| Author | Framework Maintainer |
| Framework Version | 0.70.2 |

When the canon ships a new `framework/VERSION`, every consumer owes
re-adoption (GATE-SPEC flow diagram: "consumers re-adopt the new
`framework/VERSION` and re-pass the shared conformance suite"). This runbook
is the procedure behind that box (#787). Canon-side records feed into it but
do not substitute for it: per-consumer migration notes (`GATE-SPEC_FRAMEWORK.md`
W001, for breaking changes) are inputs, and adoption drift (W002) is what the
procedure below clears.

## Procedure

### 1. Read the canon-side inputs

- The canon `CHANGELOG.md` entry for the new version (breaking changes,
  migration notes per W001).
- Your overrides' authored-against `framework_version` pins — anything older
  than the new canon is a candidate conflict.

### 2. Re-point `framework_path`

- **Symlink consumers:** retarget `.aidoc/framework` at the new canon
  location and update `framework_version` in `.aidoc/profile.yaml` to the new
  `X.Y.Z`.
- **Pinned-copy consumers:** remove the old copy first
  (`rm -rf .aidoc/framework` — `cp -r` never deletes, so refreshing over
  the existing tree would let upstream-removed files linger), then replace
  it by repeating the `docs/PROJECT.md` §7.1 allowlist copy at the new
  canon tree (`framework/`, `docs/`, `hooks/`, `sdd_doc_lint/`, `tests/`,
  then prune `framework/archive/` inside the copy), then update
  `framework_version`. Never leave a half-copied tree, and never refresh
  by copying the canon tree whole — that reintroduces the canon-dev
  internals §7.1 excludes (#834).

### 3. Diff each `project/` override against its new upstream shadow

For every file under `.aidoc/project/`, diff it against the same path in the
new `.aidoc/framework/`:

```bash
diff .aidoc/project/<path> .aidoc/framework/<path>
```

Resolve each conflict in the override WITHOUT weakening gates: carry the
project's intent forward onto the new upstream text; if the upstream gate got
stricter, the override follows it up, never down. Delete overrides that now
duplicate upstream verbatim.

### 4. Re-run conformance

Re-pass the shared conformance suite against the re-pointed tree. The upgrade
is not done until the suite is green on the new version.

### 5. Record it

- Update the override `framework_version` pins to the new canon version.
- Record the upgrade in the consumer changelog (old version → new version,
  conflicts resolved, suite result).

## Who owes the upgrade

The consumer owns its re-adoption as an ordinary consumer change (GATE-SPEC
table: "Consumer must adapt" rows are ordinary consumer PRs, not canon CHGs).
The canon owes only the inputs: versioned releases, W001 migration notes for
breaking changes, and drift tracking (W002).

## Minimal automation (open follow-up)

No shipped script performs any part of this yet. The smallest useful one is a
`stale` detector: read each override's authored-against `framework_version`
pin, compare against the canon `VERSION`, and report drift — making W002
measurable. Kept out of this batch on purpose (prose-only vehicle, CHG-16).

## See also

- `BOOTSTRAP.md` — the initial-deploy procedure this runbook extends
- `AIDOC.md` — the contract (structure, discovery rule, symlink convention)
- `chg/gates/GATE-SPEC_FRAMEWORK.md` — the spec gate (W001/W002, re-adoption box)
