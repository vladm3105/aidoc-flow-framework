# `.aidoc/` Bootstrap — new-project procedure + shape validation

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-29 |
| Author | Framework Maintainer |
| Framework Version | 0.68.3 |

This is the ordered procedure for deploying `.aidoc/` on a new project
(#786). The contract lives in `AIDOC.md`; the profile semantics in
`ADAPTATION.md` + `ADAPTATION_SURFACE.yaml`. Follow the steps in order —
each step's check must pass before moving on.

## Procedure

### 1. Copy the scaffold README

Run from the framework repository root:

```bash
mkdir -p <project>/.aidoc
cp framework/governance/aidoc/AIDOC-SCAFFOLD-TEMPLATE.md <project>/.aidoc/README.md
```

Fill the `YYYY-MM-DD`, author, and `X.Y.Z` placeholders in the copied file.

### 2. Copy the profile template and fill the knobs

```bash
cp framework/governance/PROFILE-TEMPLATE.yaml <project>/.aidoc/profile.yaml
```

Uncomment and fill only the knobs the project overrides. Keys must come from
the closed set in `ADAPTATION_SURFACE.yaml` (`active_layers`,
`section_toggles`, `audit_threshold`, `glossary`, `review_mode`,
`quality_loop_max_iterations`) — engines IGNORE any other key. Per-layer
review crews and persona weights are framework-defined (`REVIEW_CREWS.yaml`)
and are not project-overridable through this surface.

### 3. Create the framework symlink

```bash
ln -s <shared-framework-location> <project>/.aidoc/framework
```

`.aidoc/framework` is the canonical path engines resolve (via
`readlink -f`); `framework_path: .aidoc/framework` in `profile.yaml` declares
it. Pinned-copy checkouts are allowed where symlinks are unavailable, but the
copy MUST be refreshed on every upgrade (see `UPGRADE-RUNBOOK.md`) — a stale
copy is silent drift.

### 4. Pin the framework version

Set `framework_version` in `<project>/.aidoc/profile.yaml` `metadata` to the
canon `framework/VERSION` the project adopts (exact `X.Y.Z`, never a range).
Overrides under `.aidoc/project/` carry the `framework_version` they were
authored against — the signal the upgrade check reads.

### 5. Smoke-verify the shape

The fresh `.aidoc/` passes when ALL of these hold:

- [ ] `.aidoc/README.md`, `.aidoc/profile.yaml` present; `.aidoc/framework`
      resolves (`readlink -f .aidoc/framework` exits 0).
- [ ] Every key in `profile.yaml` is in the `ADAPTATION_SURFACE.yaml` closed
      set (no unknown keys).
- [ ] Behavior-changing project docs live under `.aidoc/project/` (mirroring
      `framework/` paths per the discovery rule) — never loose at `.aidoc/`
      root, where engines do not read them.
- [ ] `framework_version` in `profile.yaml` equals the adopted canon
      `framework/VERSION`.

## What is NOT part of the contract

Extra top-level directories (e.g. a `knowledge/` dir) are not read by engines
and are not a sanctioned tier member — project knowledge the agent must find
belongs under `.aidoc/project/` or the project's own docs, not beside the
contract. Overrides never modify the shared `framework/` directory.

## See also

- `AIDOC.md` — the contract (structure, discovery rule, symlink convention)
- `ADAPTATION.md` §10 — the override contract and constraints
- `UPGRADE-RUNBOOK.md` — moving an adopted project to a new canon version
