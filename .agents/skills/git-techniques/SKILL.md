---
name: git-techniques
description: Advanced Git history, recovery, and debugging techniques with guardrails for destructive, remote, and config-changing operations.
---

# Git Techniques

Use for advanced Git investigation, recovery, and debugging: reflog recovery, history search, line history, blame follow-up, bisect, fixup/autosquash, worktrees, stash inspection, and large-repo checkout options. Routine commits, pushes, branches, and PRs follow the bundled `git` safety skill and the repository's `AGENTS.md`; repository worktree, branch, and merge rules win over anything below.

## Safety contract

- Default to read-only commands: `status`, `log`, `show`, `diff`, `blame`, `reflog`, `log -S`, `log -G`, `log -L`, and `worktree list`.
- Do not run a mutating operation unless the user explicitly requested that exact operation. This includes `reset`, `rebase`, `commit --amend`, `push` in any force form, `worktree add/remove`, sparse-checkout or clone-filter changes, broad stash operations, global/system config changes, `maintenance`, and blame-ignore-revs changes.
- Do not run interactive commands such as `add -p`, `checkout -p`, `stash -p`, or `rebase -i` in automation unless the user explicitly asks and provides an interactive context. Prefer named paths and explicit non-interactive commands.
- Preserve unrelated working-tree changes. Name the files being staged, inspected, or recovered. Never commit or push changes the session did not make or cannot explain.
- Before an explicitly authorized discard, use the bundled `git` recovery-save path where applicable.
- Never rewrite pushed or shared history by default. If a remote rewrite is explicitly authorized and repository policy permits it, prefer `--force-with-lease` over `--force`.

## Techniques

- Recovery: use `git reflog` to find the prior `HEAD@{n}`, inspect it with `git show HEAD@{n}`, and only then perform an explicitly approved reset. Reflog entries are normally retained about 90 days, not guaranteed.
- History search: use `git log -S "<string>" --oneline` for added/removed occurrences, `git log -G "<regex>"` for pattern matches, and `--pickaxe-regex` when needed. Use `git log --grep` only for commit-message search.
- Line history: use `git log -L <start>,<end>:<file>` or `git log -L :<function>:<file>` to review diffs for specific lines or functions.
- Blame follow-up: use `git blame -w -C -M <file>` to look past whitespace, moves, and copies. Changing blame-ignore configuration or committing an ignore-revs file needs explicit approval.
- Stash inspection: prefer named stashes, inspect with `git stash list` and `git stash show -p stash@{n}`, and apply rather than drop when uncertain. Include untracked files or broad paths only on explicit request.
- Fixup/autosquash: use `git commit --fixup=<commit>` plus autosquash rebase only for explicitly requested local history rewrites. Do not reorder or squash shared history without explicit approval.
- Bisect: require a clean tree, an explicitly approved test command with trustworthy exit codes, and always finish with `git bisect reset`. Report the culprit commit and the verification evidence.
- Worktrees: defer to the repository's worktree flow. Do not create second clones or stray worktrees to avoid stashing; remove only worktrees the task created, after confirming no needed work remains.
- Partial staging: split commits by explicit paths rather than interactive hunk editing in automation.
- Large repositories: use shallow, blob-filter, or sparse-checkout clones only for new checkouts the user explicitly requested. Never initialize or restructure cloning inside an existing source-controlled tree.
- Performance and display settings: propose aliases and config changes for the user to approve; do not write global config without an explicit request.

## Report

State the commands run, the evidence found, the exact recovery or culprit target when applicable, what was left unchanged, and the next safe step. For any proposed mutation, give the exact command, its blast radius, and its rollback path, then wait for approval.
