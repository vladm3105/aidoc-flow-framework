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
#   - All platforms/claude-code-plugin/skills/<name>/SKILL.md frontmatter
#       version: "<X.Y.Z>"
#   - README.md
#       `claude-code-plugin/v<X.Y.Z>` references
#   - platforms/claude-code-plugin/docs/SKILL_AUTHORING.md
#       version: "<X.Y.Z>"
#   - platforms/claude-code-plugin/README.md
#       `claude-code-plugin/v<X.Y.Z>` references in the Platform info table
#       (added 2026-06-14 to close the v0.6.3 → v0.20.0 drift bug — the
#       prior awk pass only handled bare X.Y.Z lines in the `$ cat VERSION`
#       example block, missing the table cell)
#   - ../web-site/src/pages/index.astro
#       `Pre-release v<X.Y.Z>` badge in the home page (cross-submodule write
#       at the umbrella layer; added 2026-06-14 per IPLAN-0008 step 6 to
#       close the v0.18.0 stale-badge drift bug). The sibling web-site/ is
#       a separate git repo, so writes here land as unstaged changes in
#       web-site's working tree — the developer commits them in web-site's
#       own PR. Skipped silently if web-site/ is not present alongside.
#   - docs/PARITY.md
#       claude-code-plugin/v<X.Y.Z> current-state row
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
#   - docs/TAGGING.md new release rows (human-authored)
#
# Exit code: always 0 (this is a sync hook; never blocks the commit).
# Genuine failures (missing/malformed VERSION) print a warning to stderr but
# still exit 0 so the commit proceeds.

# Note: do NOT enable `set -e` here. The script does a lot of best-effort
# detection (greps that may return no matches, files that may not exist).
# Each step is individually defensive.

set -u  # catch unset-variable bugs only

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

verbose=0
if [[ "${1:-}" == "--verbose" ]]; then
  verbose=1
fi

log() {
  [[ "$verbose" == "1" ]] && printf '%s\n' "$*" >&2
  return 0
}

warn() {
  printf '[sync-version-refs] %s\n' "$*" >&2
  return 0
}

# Read VERSION file; return empty (and warn) on missing/malformed.
read_version() {
  local f="$1"
  if [[ ! -f "$f" ]]; then return 0; fi
  local v
  v="$(tr -d '[:space:]' < "$f" 2>/dev/null || true)"
  if ! [[ "$v" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    warn "skipping malformed VERSION in $f: '$v'"
    return 0
  fi
  printf '%s' "$v"
}

# In-place replace a literal old-string with a literal new-string in $1 ($2/$3).
# Skip silently if file doesn't exist, old==new, or pattern not present.
replace_in_file() {
  local file="$1" old="$2" new="$3"
  [[ -f "$file" ]] || return 0
  [[ "$old" != "$new" ]] || return 0
  grep -qF "$old" "$file" 2>/dev/null || return 0
  sed -i "s|${old}|${new}|g" "$file" 2>/dev/null || {
    warn "sed failed on $file"
    return 0
  }
  log "  updated $file: $old -> $new"
  return 0
}

# Find current version reference in a file matching a regex; returns the
# captured X.Y.Z group, or empty if not found. Never fails.
detect_version_in() {
  local file="$1" pattern="$2"
  [[ -f "$file" ]] || return 0
  local match
  match="$(grep -oE "$pattern" "$file" 2>/dev/null | head -1 || true)"
  [[ -n "$match" ]] || return 0
  printf '%s' "$match" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || true
}

# --- plugin VERSION fanout ----------------------------------------------------

plugin_ver="$(read_version platforms/claude-code-plugin/VERSION)"
log "plugin VERSION: ${plugin_ver:-(missing)}"

if [[ -n "$plugin_ver" ]]; then
  plugin_prev="$(detect_version_in \
    platforms/claude-code-plugin/.claude-plugin/plugin.json \
    '"version": "[0-9]+\.[0-9]+\.[0-9]+"')"

  if [[ -n "$plugin_prev" && "$plugin_prev" != "$plugin_ver" ]]; then
    log "plugin sync $plugin_prev -> $plugin_ver"

    replace_in_file platforms/claude-code-plugin/.claude-plugin/plugin.json \
      "\"version\": \"$plugin_prev\"" "\"version\": \"$plugin_ver\""
    replace_in_file .claude-plugin/marketplace.json \
      "\"version\": \"$plugin_prev\"" "\"version\": \"$plugin_ver\""
    for skill in platforms/claude-code-plugin/skills/*/SKILL.md; do
      [[ -f "$skill" ]] || continue
      replace_in_file "$skill" \
        "version: \"$plugin_prev\"" "version: \"$plugin_ver\""
    done
    replace_in_file README.md \
      "claude-code-plugin/v$plugin_prev" "claude-code-plugin/v$plugin_ver"
    replace_in_file platforms/claude-code-plugin/README.md \
      "claude-code-plugin/v$plugin_prev" "claude-code-plugin/v$plugin_ver"
    # Cross-submodule write: ../web-site/ is a sibling repo under the umbrella.
    # The sync hook lands changes in its working tree; the developer commits
    # them in the web-site PR. The replace_in_file helper is no-op if the file
    # does not exist (e.g., the framework repo is cloned standalone without
    # the umbrella siblings).
    replace_in_file ../web-site/src/pages/index.astro \
      "Pre-release v$plugin_prev" "Pre-release v$plugin_ver"
    replace_in_file platforms/claude-code-plugin/docs/SKILL_AUTHORING.md \
      "version: \"$plugin_prev\"" "version: \"$plugin_ver\""
    replace_in_file platforms/claude-code-plugin/docs/SKILL_AUTHORING.md \
      "(currently \`$plugin_prev\`)" "(currently \`$plugin_ver\`)"
    replace_in_file docs/PARITY.md \
      "claude-code-plugin/v$plugin_prev" "claude-code-plugin/v$plugin_ver"

    # platforms/claude-code-plugin/README.md has a `$ cat VERSION` example
    # block with the bare version on its own line. The bare X.Y.Z is too
    # generic to grep+sed safely (would match version refs in prose); use
    # awk to update only the literal `^prev$` lines.
    if [[ -f platforms/claude-code-plugin/README.md ]]; then
      awk -v prev="$plugin_prev" -v new="$plugin_ver" \
        '{ if ($0 == prev) print new; else print }' \
        platforms/claude-code-plugin/README.md > platforms/claude-code-plugin/README.md.tmp \
        && mv platforms/claude-code-plugin/README.md.tmp \
              platforms/claude-code-plugin/README.md \
        && log "  updated platforms/claude-code-plugin/README.md: bare \`^$plugin_prev$\` line -> $plugin_ver"
    fi
  fi
fi

# --- framework VERSION fanout -------------------------------------------------

fw_ver="$(read_version framework/VERSION)"
log "framework VERSION: ${fw_ver:-(missing)}"

if [[ -n "$fw_ver" ]]; then
  fw_prev="$(detect_version_in CLAUDE.md \
    'framework spec `[0-9]+\.[0-9]+\.[0-9]+`')"

  if [[ -n "$fw_prev" && "$fw_prev" != "$fw_ver" ]]; then
    log "framework sync $fw_prev -> $fw_ver"
    replace_in_file CLAUDE.md \
      "framework spec \`$fw_prev\`" "framework spec \`$fw_ver\`"
    replace_in_file README.md \
      "framework spec \`$fw_prev\`" "framework spec \`$fw_ver\`"
    replace_in_file docs/PARITY.md \
      "framework spec \`$fw_prev\`" "framework spec \`$fw_ver\`"

    # platforms/claude-code-plugin/README.md quotes the framework spec version
    # in prose ("...framework spec `X`...") AND in a `$ cat FRAMEWORK_SPEC_VERSION`
    # example block (bare X.Y.Z on its own line). Both were previously skipped,
    # forcing a hand-edit every framework bump (a conformance test caught the
    # drift after the fact). Sync prose via replace_in_file; sync the bare line
    # via awk, anchored to the preceding `$ cat FRAMEWORK_SPEC_VERSION` marker so
    # the generic X.Y.Z is only touched inside that block.
    replace_in_file platforms/claude-code-plugin/README.md \
      "framework spec \`$fw_prev\`" "framework spec \`$fw_ver\`"
    if [[ -f platforms/claude-code-plugin/README.md ]]; then
      awk -v prev="$fw_prev" -v new="$fw_ver" '
        marker { if ($0 == prev) $0 = new; marker = 0 }
        /^\$ cat FRAMEWORK_SPEC_VERSION$/ { marker = 1 }
        { print }
      ' platforms/claude-code-plugin/README.md > platforms/claude-code-plugin/README.md.tmp \
        && mv platforms/claude-code-plugin/README.md.tmp \
              platforms/claude-code-plugin/README.md \
        && log "  updated plugin README: \$ cat FRAMEWORK_SPEC_VERSION block -> $fw_ver"
    fi

    # The conformance test pins the expected spec version as a literal release
    # tripwire; it must track framework/VERSION. Correctness is also guarded by
    # the sibling assertEqual(..., framework_version()) and by GATE-SPEC-E008
    # (CHANGELOG required), so syncing this literal removes recurring toil
    # without weakening the gate.
    replace_in_file tests/conformance/platforms/test_plugin_release_metadata.py \
      "_plugin_framework_spec_version(), \"$fw_prev\"" \
      "_plugin_framework_spec_version(), \"$fw_ver\""
  fi

  # Each platform declares its target framework spec via
  # platforms/<name>/FRAMEWORK_SPEC_VERSION; this MUST equal framework/VERSION
  # (asserted by tests/conformance). Sync them automatically.
  for platform_fw_file in platforms/*/FRAMEWORK_SPEC_VERSION; do
    [[ -f "$platform_fw_file" ]] || continue
    local_prev="$(read_version "$platform_fw_file")"
    if [[ -n "$local_prev" && "$local_prev" != "$fw_ver" ]]; then
      echo "$fw_ver" > "$platform_fw_file"
      log "  updated $platform_fw_file: $local_prev -> $fw_ver"
    fi
  done

  # Plugin SKILL.md frontmatter declares framework_spec_version: "X.Y.Z" —
  # fanout to the previous detected value if the SKILLs all agree on it.
  skill_fw_prev="$(detect_version_in \
    platforms/claude-code-plugin/skills/doc-brd-autopilot/SKILL.md \
    'framework_spec_version: "[0-9]+\.[0-9]+\.[0-9]+"')"
  if [[ -n "$skill_fw_prev" && "$skill_fw_prev" != "$fw_ver" ]]; then
    log "  SKILL frontmatter sync $skill_fw_prev -> $fw_ver (52 files + SKILL_AUTHORING.md)"
    for skill in platforms/claude-code-plugin/skills/*/SKILL.md; do
      [[ -f "$skill" ]] || continue
      replace_in_file "$skill" \
        "framework_spec_version: \"$skill_fw_prev\"" \
        "framework_spec_version: \"$fw_ver\""
    done
    replace_in_file platforms/claude-code-plugin/docs/SKILL_AUTHORING.md \
      "framework_spec_version: \"$skill_fw_prev\"" \
      "framework_spec_version: \"$fw_ver\""
  fi

  # Playbook frontmatter declares framework_spec_version: "X.Y.Z" too —
  # propagate via the same detected-prev pattern as SKILLs. Detect from
  # the first BRD playbook (any layer playbook with the field works as
  # the canonical detector).
  pb_fw_prev="$(detect_version_in \
    framework/playbooks/01_BRD/architect.md \
    'framework_spec_version: "[0-9]+\.[0-9]+\.[0-9]+"')"
  if [[ -n "$pb_fw_prev" && "$pb_fw_prev" != "$fw_ver" ]]; then
    log "  playbook frontmatter sync $pb_fw_prev -> $fw_ver"
    for pb in framework/playbooks/*/*.md; do
      [[ -f "$pb" ]] || continue
      replace_in_file "$pb" \
        "framework_spec_version: \"$pb_fw_prev\"" \
        "framework_spec_version: \"$fw_ver\""
    done
  fi
fi

# --- hermes VERSION fanout ----------------------------------------------------

hermes_ver="$(read_version platforms/hermes/VERSION)"
log "hermes VERSION: ${hermes_ver:-(missing)}"

if [[ -n "$hermes_ver" ]]; then
  hermes_prev="$(detect_version_in README.md 'hermes/v[0-9]+\.[0-9]+\.[0-9]+')"
  if [[ -n "$hermes_prev" && "$hermes_prev" != "$hermes_ver" ]]; then
    log "hermes sync $hermes_prev -> $hermes_ver"
    replace_in_file README.md \
      "hermes/v$hermes_prev" "hermes/v$hermes_ver"
    replace_in_file platforms/hermes/README.md \
      "hermes/v$hermes_prev" "hermes/v$hermes_ver"
    replace_in_file docs/PARITY.md \
      "hermes/v$hermes_prev" "hermes/v$hermes_ver"
  fi
fi

# Re-stage anything we touched (pre-commit reads from the staging area).
if ! git diff --quiet 2>/dev/null; then
  git add -u 2>/dev/null || true
  warn "version-reference sync applied; restaged changed files"
fi

exit 0
