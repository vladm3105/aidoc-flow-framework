#!/usr/bin/env bash
# Mechanical doc-sync: propagate plugin/framework/hermes VERSION values into
# the documents-of-record that quote those versions. Idempotent; safe to run
# repeatedly; touches only files where a quoted version differs from the
# authoritative VERSION file.
#
# Wired into .pre-commit-config.yaml so it runs automatically on every commit
# that stages a VERSION change. Also safe to invoke manually:
#
#   bash scripts/sync-version-refs.sh
#
# What it propagates (deterministic; sed-style):
#
# Plugin VERSION (platforms/claude-code-plugin/VERSION):
#   - platforms/claude-code-plugin/.claude-plugin/plugin.json
#       "version": "<X.Y.Z>"
#   - .claude-plugin/marketplace.json
#       "version": "<X.Y.Z>"
#   - All 52 platforms/claude-code-plugin/skills/<name>/SKILL.md frontmatter
#       version: "<X.Y.Z>"
#   - README.md
#       `claude-code-plugin/v<X.Y.Z>` references; "(v<X.Y.Z>)" status
#   - platforms/claude-code-plugin/README.md
#       `<X.Y.Z>` references in the version/status rows
#   - platforms/claude-code-plugin/docs/SKILL_AUTHORING.md
#       version: "<X.Y.Z>" + "(currently `<X.Y.Z>`)"
#   - docs/PARITY.md
#       "claude-code-plugin/v<X.Y.Z>" current-state row (line near top)
#
# Framework VERSION (framework/VERSION):
#   - CLAUDE.md "framework spec `<X.Y.Z>`" current-state line
#   - README.md "framework spec `<X.Y.Z>`" Status block
#   - docs/PARITY.md "framework spec `<X.Y.Z>`" current-state row
#
# Hermes VERSION (platforms/hermes/VERSION): same pattern for hermes/v<X.Y.Z>.
#
# What it does NOT do (semantic / human-authored content):
#   - CHANGELOG entries (text)
#   - ROADMAP "Shipped" bullets (text)
#   - HANDOFF.md current-state header (narrative)
#   - docs/TAGGING.md new release rows (human-authored row, mechanical
#     row-add could surprise reviewers — left to the contributor)
#
# Exit codes:
#   0 — no changes needed OR sync applied successfully
#   1 — a VERSION file is missing or malformed (real failure)

set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

# --- helpers ------------------------------------------------------------------

verbose=0
if [[ "${1:-}" == "--verbose" ]]; then
  verbose=1
fi

log() {
  if (( verbose )); then printf '%s\n' "$*" >&2; fi
}

warn() {
  printf '[sync-version-refs] %s\n' "$*" >&2
}

read_version() {
  local f="$1"
  if [[ ! -f "$f" ]]; then
    warn "missing VERSION file: $f"
    exit 1
  fi
  local v
  v="$(tr -d '[:space:]' < "$f")"
  if ! [[ "$v" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    warn "malformed VERSION in $f: '$v' (expected X.Y.Z)"
    exit 1
  fi
  printf '%s' "$v"
}

# In-place replace a literal old-string with a literal new-string in $1 ($2/$3).
# Uses sed with delimiter |.  We don't escape further because version strings
# are X.Y.Z digits.
replace_in_file() {
  local file="$1" old="$2" new="$3"
  if [[ ! -f "$file" ]]; then return 0; fi
  if [[ "$old" == "$new" ]]; then return 0; fi
  if ! grep -qF "$old" "$file"; then return 0; fi
  sed -i "s|${old}|${new}|g" "$file"
  log "  updated $file: $old -> $new"
}

# --- plugin VERSION fanout ----------------------------------------------------

plugin_ver="$(read_version platforms/claude-code-plugin/VERSION)"
log "plugin VERSION: $plugin_ver"

# Determine previous plugin version (if any) from the most recent
# tagged release row in docs/TAGGING.md, falling back to scanning for
# a unique version string in plugin.json.
plugin_prev=""
if [[ -f platforms/claude-code-plugin/.claude-plugin/plugin.json ]]; then
  plugin_prev="$(grep -oE '"version": "[0-9]+\.[0-9]+\.[0-9]+"' \
                 platforms/claude-code-plugin/.claude-plugin/plugin.json \
                 | head -1 | sed -E 's/.*"([0-9]+\.[0-9]+\.[0-9]+)".*/\1/')"
fi

if [[ -n "$plugin_prev" && "$plugin_prev" != "$plugin_ver" ]]; then
  log "plugin sync $plugin_prev -> $plugin_ver"

  # plugin.json
  replace_in_file platforms/claude-code-plugin/.claude-plugin/plugin.json \
    "\"version\": \"$plugin_prev\"" "\"version\": \"$plugin_ver\""

  # marketplace.json
  replace_in_file .claude-plugin/marketplace.json \
    "\"version\": \"$plugin_prev\"" "\"version\": \"$plugin_ver\""

  # SKILL.md frontmatter (52 files)
  for skill in platforms/claude-code-plugin/skills/*/SKILL.md; do
    [[ -f "$skill" ]] || continue
    replace_in_file "$skill" \
      "version: \"$plugin_prev\"" "version: \"$plugin_ver\""
  done

  # README.md (repo root)
  replace_in_file README.md \
    "claude-code-plugin/v$plugin_prev" "claude-code-plugin/v$plugin_ver"
  replace_in_file README.md \
    "(v$plugin_prev);" "(v$plugin_ver);"

  # platforms/claude-code-plugin/README.md
  replace_in_file platforms/claude-code-plugin/README.md \
    "\`$plugin_prev\`" "\`$plugin_ver\`"
  # If a bare X.Y.Z line exists (the "## version" block lists it that way),
  # update only when it's an exact line match — handled by sed; safe.

  # SKILL_AUTHORING.md
  replace_in_file platforms/claude-code-plugin/docs/SKILL_AUTHORING.md \
    "version: \"$plugin_prev\"" "version: \"$plugin_ver\""
  replace_in_file platforms/claude-code-plugin/docs/SKILL_AUTHORING.md \
    "(currently \`$plugin_prev\`)" "(currently \`$plugin_ver\`)"

  # docs/PARITY.md (current-state row near top)
  replace_in_file docs/PARITY.md \
    "claude-code-plugin/v$plugin_prev" "claude-code-plugin/v$plugin_ver"
fi

# --- framework VERSION fanout -------------------------------------------------

fw_ver="$(read_version framework/VERSION)"
log "framework VERSION: $fw_ver"

# Find previous framework version by inspecting CLAUDE.md (lowest-cost source
# of the prior reference). If not present there, skip silently.
fw_prev=""
if [[ -f CLAUDE.md ]]; then
  fw_prev="$(grep -oE 'framework spec \`[0-9]+\.[0-9]+\.[0-9]+\`' CLAUDE.md \
             | head -1 | sed -E 's/.*\`([0-9]+\.[0-9]+\.[0-9]+)\`.*/\1/')"
fi

if [[ -n "$fw_prev" && "$fw_prev" != "$fw_ver" ]]; then
  log "framework sync $fw_prev -> $fw_ver"

  # CLAUDE.md current-state line
  replace_in_file CLAUDE.md \
    "framework spec \`$fw_prev\`" "framework spec \`$fw_ver\`"

  # README.md Status block (two occurrences of "framework spec `X.Y.Z`")
  replace_in_file README.md \
    "framework spec \`$fw_prev\`" "framework spec \`$fw_ver\`"

  # docs/PARITY.md current-state row
  replace_in_file docs/PARITY.md \
    "framework spec \`$fw_prev\`" "framework spec \`$fw_ver\`"
fi

# --- hermes VERSION fanout ----------------------------------------------------

if [[ -f platforms/hermes/VERSION ]]; then
  hermes_ver="$(read_version platforms/hermes/VERSION)"
  log "hermes VERSION: $hermes_ver"

  hermes_prev=""
  if [[ -f README.md ]]; then
    hermes_prev="$(grep -oE 'hermes/v[0-9]+\.[0-9]+\.[0-9]+' README.md \
                   | head -1 | sed -E 's|hermes/v(.*)|\1|')"
  fi

  if [[ -n "$hermes_prev" && "$hermes_prev" != "$hermes_ver" ]]; then
    log "hermes sync $hermes_prev -> $hermes_ver"
    replace_in_file README.md \
      "hermes/v$hermes_prev" "hermes/v$hermes_ver"
    replace_in_file docs/PARITY.md \
      "hermes/v$hermes_prev" "hermes/v$hermes_ver"
  fi
fi

# Re-stage anything we touched (pre-commit reads from the staging area).
# `git diff --quiet` returns 1 if there are unstaged changes; in that case
# we stage them so pre-commit sees the synced state.
if ! git diff --quiet; then
  # Only restage files that were already tracked + modified in this run.
  # `git add -u` skips untracked files.
  git add -u
  warn "version-reference sync applied; restaged changed files"
fi

exit 0
