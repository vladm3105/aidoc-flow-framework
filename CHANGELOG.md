# Changelog — FROZEN (tombstone)

This log is no longer maintained per-PR (frozen 2026-10-01 by CHG-40 for
issue #836 by founder decision: hand-maintaining it costs tokens and time
while GitHub issues already track almost every change). Do not add entries here.

> Supersedes the #687 scope note: this file no longer records project
> releases and no longer mirrors `framework/CHANGELOG.md`.

The live records are:

- Spec changes: `framework/CHANGELOG.md` (document-of-record, GATE-SPEC-E008).
- Everything else: the issue tracker (open and closed) plus git history.

Full history of this file is preserved in git (`git log --follow -- CHANGELOG.md`).

## On-the-fly generation (documented query — no generator script)

Closed-issue list with labels (copy-paste; adjust `--limit` and the `jq` filter):

```sh
gh issue list -R vladm3105/aidoc-flow-framework --state closed --limit 100 \
  --json number,title,closedAt,labels \
  --jq '.[] | "\(.closedAt[:10]) #\(.number) \(.title) [\(.labels | map(.name) | join(","))]"' | sort
```

Merged-PR list for a release window (replace the dates):

```sh
gh pr list -R vladm3105/aidoc-flow-framework --state merged --limit 100 \
  --json number,title,mergedAt \
  --jq '.[] | select(.mergedAt >= "2026-10-01" and .mergedAt < "2026-11-01") | "\(.mergedAt[:10]) #\(.number) \(.title)"' | sort
```

## Last maintained state

Final maintained release: `[0.68.4]` — 2026-10-01. Entries up to and
including 0.68.4 are in git history (commit range ending at the CHG-40
tombstone commit). For 0.68.5 onward, see `framework/CHANGELOG.md` for
spec detail and the tracker queries above for project-level changes.
