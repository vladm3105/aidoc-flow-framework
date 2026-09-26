# Worktree Flow — `feature/*` → `dev`

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-20 |
| Author | Framework Maintainer |
| Framework Version | 0.61.7 |

Task isolation and promotion for framework-consuming projects. Covers `dev`
integration only. `dev` → `staging` → `main` promotions are human-executed
and out of scope.

## 1. Invariants

1. The main checkout stays on `dev`. Feature work never executes in the main
   checkout.
2. One task maps to one worktree and one branch: `feature/<issue-or-chg>-<slug>`
   or `fix/<issue>-<slug>`.
3. Direct pushes to `dev`, `staging`, `main` are forbidden. Promotion is
   PR-only.
4. No CHG/IPLAN-gated code writes without an authorizing IPLAN in
   `In Progress` listing each target file in `file_manifest`. Bootstrap
   exemption: authoring the CHG/SDD/IPLAN chain itself in order.
5. No whole-tree git operations (`stash`, `checkout -- <dirs>`, branch
   switch, blanket `add -A`) in a tree with running subagents. Use
   file-scoped commands.

## 2. Prerequisites

- Dependencies: `git >= 2.38` (worktree support), `gh` CLI (authenticated),
  network access to `origin`.
- Authorized work: active CHG (`Approved` or later) and IPLAN (`In Progress`)
  where applicable.
- Disk: each worktree duplicates working files. Remove worktrees after merge.

## 3. Procedure

### 3.1 Sync `dev` in main checkout

```bash
git fetch origin
git checkout dev
git pull --ff-only origin dev
git worktree list
```

If `pull --ff-only` fails, resolve divergence before creating a worktree. Do
not proceed on a stale base.

### 3.2 Create worktree and branch

```bash
git worktree add ../<project>-<issue> -b feature/<short-name> origin/dev
cd ../<project>-<issue>
git branch --show-current
```

Naming: `feature/<issue-or-chg>-<slug>` for features, `fix/<issue>-<slug>`
for defects. Verify branch output before the first write.

### 3.3 Implement in worktree

1. Execute IPLAN steps in order.
2. Update each `file_manifest` entry from `NOT_STARTED` to `DONE` (or
   `SKIPPED` with `_note`) as the file lands.
3. Stage owned files only. Never stage unrelated changes.

### 3.4 Verify in worktree

Run the project's own verification gates (conformance suite, linter,
acceptance harness — whatever the repo's governance names). If a gate is
skipped, record the command and reason in the PR body.

### 3.5 Push feature branch

```bash
git status --short
git add <owned-files-only>
git commit -m "<scope>: <what> (#N)"
git push -u origin feature/<short-name>
```

Run `git branch --show-current` before commit and before push. If HEAD is not
the feature branch, stop.

### 3.6 Open PR `feature/*` → `dev`

```bash
gh pr create --base dev --head feature/<short-name> --title "<scope>: <what>" --body-file -
```

PR body rules: include `Closes #N` or `Fixes #N` only on full resolution;
partial advances get a progress comment. Never write the phrase negated.

### 3.7 After merge — cleanup (ORDER MATTERS)

```bash
cd <main-checkout>
git worktree remove ../<project>-<issue> --force
git fetch --prune origin
git branch -d feature/<short-name>
git checkout dev
git pull --ff-only origin dev
```

**Order guard:** `worktree remove` runs BEFORE branch delete. Deleting the
branch first orphans the worktree's metadata and the remove then fails.
Delete the remote branch on merge. If `worktree remove` fails due to
uncommitted state, snapshot (copy to a scratch dir or patch export) before
forcing.

## 4. Failure modes

| Condition | Handling |
|---|---|
| `pull --ff-only` fails | Stop. Resolve divergence in main checkout. Do not base a worktree on a diverged `dev`. |
| Wrong branch at commit/push time | Stop. Never commit to `dev`/`staging`/`main`. |
| `worktree remove` reports dirty tree | Snapshot irreplaceable work first, then `--force`. |
| Concurrent subagents active | Use `git diff -- <owned files>` only. No whole-tree stat, stash, or branch switch. |

## 5. Validation

1. `git worktree list` shows one entry per active task, zero after cleanup.
2. `git branch --show-current` in worktree returns the feature branch at
   commit and push time.
3. `git status --short` in main checkout is clean of feature changes
   throughout.
4. Merged PR targets `dev`, carries required CI gates, and references the
   authorizing CHG/IPLAN.

## 6. References

- `DOC_GOVERNANCE_CORE.md` §3.13 (IPLAN Gate), §4.1 (status propagation)
- `NOTICES.md` §Concurrency traps (no whole-tree ops), Rule 5 (archive)
- `SELF_LEARNING.md` (feedback-submit contract for process fixes)
