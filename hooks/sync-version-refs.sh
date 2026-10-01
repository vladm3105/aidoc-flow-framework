#!/usr/bin/env bash
# Mechanical doc-sync: propagate framework/VERSION into framework/ version pins.
# Idempotent; safe to run repeatedly.
#
# Wired into .pre-commit-config.yaml so it runs automatically when
# framework/VERSION changes. Also safe to invoke manually:
#   bash hooks/sync-version-refs.sh
#
# Single source: framework/VERSION. There are no platform VERSION files in the
# framework-only repo (CLEANUP-001 retired the three-source sweep; see
# tests/conformance/test_sync_version_refs_counts.py, also retired).
#
# What it propagates (mechanical only — semantic content like changelog entries
# and decision rationale is authored by the contributor):
#   - `framework_spec_version: "X.Y.Z"` frontmatter in framework/playbooks/**.md
#   - `framework_version: "X.Y.Z"` metadata in framework/**/*.yaml
#   - `| Framework Version | X.Y.Z |` document-control rows in framework/**/*.md
#
# Guard against vacuity (#405): every substitution is counted and the script
# fails if a file holds MORE occurrences of the old literal than expected — a
# surplus is a historical mention that must be reworded out of the swept form,
# not silently skipped. Expected counts live beside each call site below.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRAMEWORK_VERSION="$(cat "$REPO_ROOT/framework/VERSION" 2>/dev/null | tr -d '[:space:]')"

if [ -z "$FRAMEWORK_VERSION" ]; then
  echo "sync-version-refs: could not read framework/VERSION" >&2
  exit 1
fi

if [[ ! "$FRAMEWORK_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "sync-version-refs: malformed version '$FRAMEWORK_VERSION'" >&2
  exit 1
fi

echo "sync-version-refs: framework/VERSION = $FRAMEWORK_VERSION"

replace_in_file_counted() {
  # $1 = repo-relative path, $2 = old literal, $3 = new literal, $4 = expected count
  local rel="$1" old="$2" new="$3" expected="$4"
  local path="$REPO_ROOT/$rel"
  if [ ! -f "$path" ]; then
    echo "sync-version-refs: skip (absent): $rel" >&2
    return 0
  fi
  local actual
  actual="$(grep -cF -- "$old" "$path" || true)"
  if [ "$actual" -gt "$expected" ]; then
    echo "sync-version-refs: REFUSING $rel — holds $actual occurrence(s) of '$old', expected $expected." >&2
    echo "sync-version-refs: reword the historical mention out of the swept literal form, then re-run." >&2
    return 1
  fi
  if [ "$actual" -eq 0 ]; then
    return 0
  fi
  # Fail closed (#821): every fallible stage is guarded explicitly because
  # `set -e` stays disabled inside functions invoked from an OR-list
  # (`sweep … || true` call sites). The pre-fix code ran an unconditional
  # `cat tmp > path` after the converter, truncating the target on
  # converter failure while the hook reported success.
  #
  # Atomic write: same-dir temp + rename, so a mid-copy failure (ENOSPC,
  # signal) can never leave a partial target — rename either installs the
  # complete file or nothing. The temp inherits the target's mode first
  # (mktemp is 600; a bare rename would propagate that); `stat` tries GNU
  # then BSD flags, and a failed chmod aborts loud before the rename.
  local tmp
  tmp="$(mktemp "$(dirname "$path")/.sync-XXXXXX")"
  # Track every same-dir temp for the EXIT trap below (kill-safe cleanup).
  _sync_tmps+=("$tmp")
  if ! python3 - "$path" "$old" "$new" "$tmp" <<'EOF'
import sys
path, old, new, tmp = sys.argv[1:5]
text = open(path, encoding="utf-8").read()
open(tmp, "w", encoding="utf-8").write(text.replace(old, new))
EOF
  then
    echo "sync-version-refs: FAILED converter for $rel — target untouched" >&2
    rm -f "$tmp"
    return 1
  fi
  if ! chmod "$(stat -c %a "$path" 2>/dev/null || stat -f %Lp "$path")" "$tmp" \
    || ! mv "$tmp" "$path"; then
    echo "sync-version-refs: FAILED write for $rel — target untouched" >&2
    rm -f "$tmp"
    return 1
  fi
  rm -f "$tmp"
  # Record the rewrite for the scoped re-stage below (#830-1): only paths
  # reaching this line were byte-changed by this run.
  touched+=("$rel")
  echo "sync-version-refs: $rel — replaced $actual occurrence(s)"
}

rc=0

# Same-dir temps must never litter the tree on a killed run (#830-4): a
# function-scoped `rm -f` covers every coded return, and this EXIT trap
# covers death by signal (TERM/INT) mid-conversion. `rm -f` tolerates temps
# the success path already removed or renamed away; the guard preserves the
# script exit status.
_sync_tmps=()
_sync_cleanup() {
  [ "${#_sync_tmps[@]}" -gt 0 ] && rm -f -- "${_sync_tmps[@]}" || true
}
trap _sync_cleanup EXIT

# Repo-relative paths this run actually rewrote — the re-stage below is
# scoped to exactly these (#830-1), never `git add -u`.
touched=()
sweep() {
  replace_in_file_counted "$@" || rc=1
}

# Frozen records must never be rewritten: framework/archive/ holds the
# pre-change originals each CHG cites in `supersedes`. Sweeping them would
# destroy the audit trail (measured 2026-09-21: the 0.54.0 pass rewrote
# framework/archive/CHG-04/ originals before this exclusion landed).
ARCHIVE_EXCL="archive/CHG-"

# Old version literals swept to $FRAMEWORK_VERSION. Extend with the previous
# release on every MINOR bump (#663) — the conformance pin
# (tests/conformance/test_sync_version_refs.py) fails if a swept-form
# literal in the tree is missing from this list.
OLD_VERSIONS="0.50.0 0.51.0 0.52.0 0.53.0 0.53.1 0.53.2 0.53.3 0.54.0 0.55.0 0.56.0 0.57.0 0.57.1 0.58.0 0.59.0 0.59.1 0.59.2 0.60.0 0.61.0 0.61.1 0.61.2 0.61.3 0.61.4 0.61.5 0.61.6 0.61.7 0.61.8 0.62.0 0.62.1 0.62.2 0.62.3 0.62.4 0.62.5 0.62.6 0.62.7 0.63.0 0.64.0 0.65.0 0.65.1 0.65.2 0.67.0 0.67.1 0.68.0 0.68.1 0.68.2 0.68.3 0.68.4 0.68.5 0.68.6 0.69.0 0.70.0"

# --- playbook frontmatter pins (Step 6 of CLEANUP-001 pins these at 0.53.3) ---
# NUL-delimited throughout (#830-3): a newline in a filename must not split
# one path into two bogus `$rel` values hitting the `skip (absent)` branch.
while IFS= read -r -d '' f; do
  rel="${f#"$REPO_ROOT"/}"
  for old in $OLD_VERSIONS; do
    sweep "$rel" "framework_spec_version: \"$old\"" "framework_spec_version: \"$FRAMEWORK_VERSION\"" 1 || true
  done
done < <(grep -rlZ 'framework_spec_version: "0\.' "$REPO_ROOT/framework/playbooks/" 2>/dev/null || true)

# --- framework metadata + document-control rows (archive excluded — see above) ---
# Portable ERE alternation (#830-2): the old BRE `\|` join matched nothing
# under BSD grep (no `-E` on the call), a silent local no-op on macOS.
# `grep -rlE` with `|` matches the same language on GNU and BSD.
_meta_pat=""
for old in $OLD_VERSIONS; do
  [ -n "$_meta_pat" ] && _meta_pat="${_meta_pat}|"
  _meta_pat="${_meta_pat}framework_version: \"${old}\"|| Framework Version | ${old} |"
done
while IFS= read -r -d '' f; do
  rel="${f#"$REPO_ROOT"/}"
  # Archive exclusion lives here rather than in a `grep -v` stage: a
  # line-oriented filter cannot sift NUL-delimited bytes (one match would
  # drop the whole stream). Same semantics — archive/ paths are skipped.
  case "$rel" in *"$ARCHIVE_EXCL"*) continue;; esac
  for old in $OLD_VERSIONS; do
    sweep "$rel" "framework_version: \"$old\"" "framework_version: \"$FRAMEWORK_VERSION\"" 5 || true
    sweep "$rel" "| Framework Version | $old |" "| Framework Version | $FRAMEWORK_VERSION |" 5 || true
  done
done < <(grep -rlZE "$_meta_pat" "$REPO_ROOT/framework/" 2>/dev/null || true)

if [ "$rc" -ne 0 ]; then
  echo "sync-version-refs: one or more files refused (see above)" >&2
  exit 1
fi

# Re-stage exactly what the bump touched when run as a pre-commit hook
# (#830-1): `git add -u` staged every unstaged tracked modification
# repo-wide, silently folding unauthorized hunks into the VERSION commit.
if git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if [ "${#touched[@]}" -gt 0 ]; then
    git -C "$REPO_ROOT" add -- "${touched[@]}" 2>/dev/null || true
  fi
fi

echo "sync-version-refs: done (framework version propagated)"
