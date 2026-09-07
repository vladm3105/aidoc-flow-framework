# P1-T6 Plan — `framework/VERSION` + Tag Convention

| Field      | Value                                      |
|------------|--------------------------------------------|
| Task       | P1-T6                                      |
| Depends on | P1-T2/T3/T4/T5 (`framework/` populated, suite green) |
| Status     | DONE — 2026-05-19T09:20:00Z                |
| Feeds      | Phase 1 close (`framework/v0.1.0` + `v0.2.0` tags) |

## Objective

Establish the framework spec's independent version stream: create
`framework/VERSION`, define the namespaced tag convention, and have the
conformance suite cover the new file. The git tag itself is deferred to
Phase 1 close (see D-0009).

## Decisions — D-0009

- **Tag namespace.** The framework spec versions in its own stream. Its
  release tag is `framework/v<semver>` (slash-namespaced git ref). Platforms,
  once scaffolded, use `<platform>/v<semver>` (`hermes/v…`,
  `claude-code-plugin/v…`). Project *milestone* tags remain bare `v<semver>`
  (`v0.1.0`…`v1.0.0`). Slash refs let `git tag -l 'framework/*'` filter a
  stream and stay visually distinct from milestone tags.
- **Tag timing.** `framework/VERSION` is created now (this task); the
  `framework/v0.1.0` git tag is deferred until P1-T7 lands, so the tag marks a
  complete spec. It is created at Phase 1 close together with the project
  `v0.2.0` milestone tag.

## Scope

**In:** create `framework/VERSION`; extend `docs/PROJECT.md` §3 with the
namespaced tag convention; add a conformance test for `VERSION`.
**Out:** creating/pushing any git tag (Phase 1 close); P1-T7 methodology docs.

## Approach

### `framework/VERSION`

Single line, bare SemVer, trailing newline:

```
0.1.0
```

No `v` prefix in the file — the `v` belongs to the tag name only. Matches the
per-platform `VERSION` convention in `docs/PROJECT.md` §2.

### `docs/PROJECT.md` §3 — tag convention

Add a subsection defining three tag namespaces: project milestones (`vX.Y.Z`),
framework spec (`framework/vX.Y.Z`), platforms (`<platform>/vX.Y.Z`). State
that `framework/VERSION` holds the bare SemVer and the tag adds the `v`.

### Conformance — `tests/conformance/test_version.py`

New test module: `framework/VERSION` exists, is a single line, and matches
`^\d+\.\d+\.\d+$`. Keeps the suite covering every part of `framework/`.

## Step sequence

1. Create `framework/VERSION`.
2. Extend `docs/PROJECT.md` §3.
3. Add `tests/conformance/test_version.py`.
4. **Verify** (below).
5. **Land:** record D-0009; commit; update `CHANGELOG.md`, `HANDOFF.md`,
   `MIGRATION_TODO.md` (P1-T6 scope = VERSION + convention; the tag is tracked
   as a Phase-1-close action so it is not lost).

## Verification

- `python3 -m unittest discover -s tests/conformance` → all tests pass,
  including the new `VERSION` checks.
- `cat framework/VERSION` → exactly `0.1.0`.
- No git tag is created by this task.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Tagging an incomplete spec | tag deferred to Phase 1 close (D-0009) |
| R2 | Deferred tag forgotten | tracked as an explicit Phase-1-close action in `MIGRATION_TODO.md` |
| R3 | `framework/v0.1.0` slash ref confuses tooling | modern git/GitHub support it; `-l 'framework/*'` is the payoff; hyphen form was the considered alternative |

## Implementation (2026-05-19T09:20:00Z)

Created `framework/VERSION` (`0.1.0`); extended `docs/PROJECT.md` §3 with the
tag-namespace convention; added `tests/conformance/test_version.py`. Suite is
green at **24 tests** (22 + 2). No git tag created — deferred to Phase 1 close
per D-0009, tracked as P1-T8 in `MIGRATION_TODO.md`. No deviations from plan.

## Review log

### Pass 1 — 2026-05-19T09:05:00Z

- **G1.** Tagging now would mark an incomplete spec (P1-T7 pending). → Tag
  deferred to Phase 1 close; only `framework/VERSION` is created now. D-0009,
  R1.
- **G2.** `docs/PROJECT.md` §3 defines only bare milestone tags — no namespace
  for the framework/platform streams. → Extend §3 with the convention rather
  than spawn a separate doc (keeps the tagging authority in one place).
- **G3.** A new `framework/` file the conformance suite does not check is a
  blind spot. → Add `test_version.py`.
- **G4.** `VERSION` file format must be unambiguous. → Bare `X.Y.Z` + newline,
  no `v` prefix; the `v` is tag-only. Consistent with platform `VERSION` files.

### Pass 2 — 2026-05-19T09:10:00Z

Cross-checked Verification and scope against the approach:

- **G5.** Deferring the tag means the tracker line "P1-T6 — … tag first spec
  release" is only partly satisfied here. → `MIGRATION_TODO.md` update will
  re-scope P1-T6 to VERSION + convention and add the `framework/v0.1.0` tag as
  a named Phase-1-close action alongside `v0.2.0`, so it cannot be lost (R2).
- **G6.** Verification is sound: it runs the suite (covering the new file) and
  asserts no tag is created — no false positive/negative. The `VERSION` content
  is also scanned by `test_spec_hygiene` (already in the suite); `0.1.0` trips
  none of the engine/version patterns — confirmed safe.
- **G7.** The eventual `framework/v0.1.0` / `v0.2.0` tags are remote,
  hard-to-reverse actions — they require explicit user confirmation when
  Phase 1 closes. Noted for the closeout step.
- No new blockers. Ready to implement.
