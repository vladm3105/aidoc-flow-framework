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
  local tmp
  tmp="$(mktemp)"
  python3 - "$path" "$old" "$new" "$tmp" <<'EOF'
import sys
path, old, new, tmp = sys.argv[1:5]
text = open(path, encoding="utf-8").read()
open(tmp, "w", encoding="utf-8").write(text.replace(old, new))
EOF
  cat "$tmp" > "$path"
  rm -f "$tmp"
  echo "sync-version-refs: $rel — replaced $actual occurrence(s)"
}

rc=0
sweep() {
  replace_in_file_counted "$@" || rc=1
}

# --- playbook frontmatter pins (Step 6 of CLEANUP-001 pins these at 0.53.3) ---
while IFS= read -r f; do
  rel="${f#"$REPO_ROOT"/}"
  sweep "$rel" 'framework_spec_version: "0.50.0"' "framework_spec_version: \"$FRAMEWORK_VERSION\"" 1 || true
  sweep "$rel" 'framework_spec_version: "0.53.0"' "framework_spec_version: \"$FRAMEWORK_VERSION\"" 1 || true
  sweep "$rel" 'framework_spec_version: "0.53.2"' "framework_spec_version: \"$FRAMEWORK_VERSION\"" 1 || true
done < <(grep -rl 'framework_spec_version: "0\.' "$REPO_ROOT/framework/playbooks/" 2>/dev/null || true)

# --- framework metadata + document-control rows ---
while IFS= read -r f; do
  rel="${f#"$REPO_ROOT"/}"
  sweep "$rel" 'framework_version: "0.53.0"' "framework_version: \"$FRAMEWORK_VERSION\"" 5 || true
  sweep "$rel" '| Framework Version | 0.53.0 |' "| Framework Version | $FRAMEWORK_VERSION |" 5 || true
done < <(grep -rl 'framework_version: "0.53.0"\|| Framework Version | 0.53.0 |' "$REPO_ROOT/framework/" 2>/dev/null || true)

if [ "$rc" -ne 0 ]; then
  echo "sync-version-refs: one or more files refused (see above)" >&2
  exit 1
fi

# Re-stage what the bump touched when run as a pre-commit hook.
if git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$REPO_ROOT" add -u 2>/dev/null || true
fi

echo "sync-version-refs: done (framework version propagated)"
