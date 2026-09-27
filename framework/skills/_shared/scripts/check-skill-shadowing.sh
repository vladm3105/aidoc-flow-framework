#!/usr/bin/env bash
# Detect name collisions between user-level and project-level skill components.
# Framework adaptation: project skills live at framework/skills/; user dirs via env.
#
# On engines with asymmetric precedence (e.g. project agents override user agents,
#   - project agents override user agents;
#   - user skills override project skills.
#
# A declared project-agent override is allowed. A same-name project skill is
# always a defect because it is masked by the user skill; a marker cannot make
# it an override. The scan follows initialized submodules recursively.
#
# Usage: check-skill-shadowing.sh [--no-recurse] [--check-remote] [repo-path]  (default: cwd)
# Exit: 0 = clean, 1 = collision defect, 2 = incomplete scan or usage error
#
# --check-remote is opt-in: for each hit, classify it against origin/main as
# COMMITTED (needs a PR) or LOCAL ONLY (already fixed upstream or never
# committed — sync the checkout instead). Uses the local origin/main ref as-is;
# run git fetch first when it may be stale.

set -uo pipefail

GLOBAL="${USER_CONFIG_ROOT:?set USER_CONFIG_ROOT to your engine user-config dir}"
USER_SKILLS_DIR="${USER_SKILLS_DIR:-$GLOBAL/skills}"
USER_AGENTS_DIR="${USER_AGENTS_DIR:-$GLOBAL/agents}"
RECURSE=1
CHECK_REMOTE=0
REPO=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --no-recurse) RECURSE=0 ;;
    --check-remote) CHECK_REMOTE=1 ;;
    -h|--help)
      printf 'usage: check-skill-shadowing.sh [--no-recurse] [--check-remote] [repo-path]\n'
      printf '  scans repo-path and, by default, initialized submodules recursively\n'
      printf '  --check-remote classifies each hit against origin/main (COMMITTED vs LOCAL ONLY)\n'
      printf '  exit 0 clean, 1 collision defect, 2 incomplete scan/usage error\n'
      exit 0 ;;
    -*) printf 'unknown option: %s\n' "$1" >&2; exit 2 ;;
    *)
      [ -z "$REPO" ] || { printf 'only one repo-path is accepted\n' >&2; exit 2; }
      REPO="$1" ;;
  esac
  shift
done

REPO="${REPO:-$PWD}"
if [ ! -d "$REPO" ]; then
  printf 'not a directory: %s\n' "$REPO" >&2
  exit 2
fi
if [ ! -d "$USER_SKILLS_DIR" ] || [ ! -d "$USER_AGENTS_DIR" ]; then
  printf 'invalid user config root (need skills/ and agents/): %s\n' "$GLOBAL" >&2
  exit 2
fi

REPO=$(realpath -m -- "$REPO")
GLOBAL=$(realpath -m -- "$GLOBAL")
TOP="$REPO"

total_defects=0
declared_agents=0
masked_skills=0
undeclared_agents=0
scan_errors=0
scanned=0
declare -A visited=()
declare -A global_agent_names=()

frontmatter_name() { # $1 = agent file
  awk '
    /^---$/ { marks++; next }
    marks == 1 && /^name:[[:space:]]*/ {
      sub(/^name:[[:space:]]*/, "")
      gsub(/^['"'"']|['"'"']$/, "")
      print
      exit
    }
  ' "$1"
}

has_override_marker() { # $1 = agent file
  grep -Eq '^> \*\*OVERRIDES GLOBAL\*\*([[:space:]]|—)' "$1"
}

remote_classify() { # $1 = repo dir, $2 = absolute file path -> classification string
  local repo="$1" file="$2" rel behind
  [ "$CHECK_REMOTE" -eq 1 ] || return 0
  rel="${file#$repo/}"
  if ! git -C "$repo" rev-parse --verify --quiet 'origin/main' >/dev/null 2>&1; then
    printf ' [remote: unknown — no origin/main ref; git fetch first]'
    return 0
  fi
  behind=$(git -C "$repo" rev-list --count 'HEAD..origin/main' 2>/dev/null || echo '?')
  if git -C "$repo" cat-file -e "origin/main:$rel" 2>/dev/null; then
    printf ' [COMMITTED on origin/main — needs a PR; checkout %s behind]' "$behind"
  else
    printf ' [LOCAL ONLY — absent on origin/main; sync checkout (behind %s) before filing]' "$behind"
  fi
}

while IFS= read -r -d '' agent; do
  name=$(frontmatter_name "$agent")
  if [ -z "$name" ]; then
    printf 'cannot read agent name: %s\n' "$agent" >&2
    scan_errors=$((scan_errors + 1))
    continue
  fi
  global_agent_names["$name"]=1
done < <(find "$USER_AGENTS_DIR" -type f -name '*.md' -print0)

scan_repo() { # $1 = repo dir
  local repo="$1" name file out=""
  [ -z "${visited[$repo]+x}" ] || return 0
  visited["$repo"]=1
  scanned=$((scanned + 1))

  # User skills win. A same-directory-name project skill is therefore masked,
  # not an override, regardless of any declaration marker.
  while IFS= read -r -d '' file; do
    name=$(basename "$(dirname "$file")")
    if [ -f "$USER_SKILLS_DIR/$name/SKILL.md" ]; then
      out+=$(printf '  MASKED skill %-24s %s  <- defect, rename or remove it%s\n' "$name" "$file" "$(remote_classify "$repo" "$file")")$'\n'
      masked_skills=$((masked_skills + 1))
      total_defects=$((total_defects + 1))
    fi
  done < <(find "$repo/framework/skills" -mindepth 2 -maxdepth 2 -type f -name SKILL.md -print0 2>/dev/null)

  # Agent identity comes from frontmatter name, not the filename.
  while IFS= read -r -d '' file; do
    name=$(frontmatter_name "$file")
    if [ -z "$name" ]; then
      out+=$(printf '  INVALID agent frontmatter       %s\n' "$file")$'\n'
      scan_errors=$((scan_errors + 1))
      continue
    fi
    [ -n "${global_agent_names[$name]+x}" ] || continue
    if has_override_marker "$file"; then
      out+=$(printf '  declared agent override: %-15s %s\n' "$name" "$file")$'\n'
      declared_agents=$((declared_agents + 1))
    else
      out+=$(printf '  UNDECLARED agent %-18s %s  <- defect, declare or remove it%s\n' "$name" "$file" "$(remote_classify "$repo" "$file")")$'\n'
      undeclared_agents=$((undeclared_agents + 1))
      total_defects=$((total_defects + 1))
    fi
  done < <(find "$repo/framework/skills/_shared/agents" -type f -name '*.md' -print0 2>/dev/null)

  if [ -n "$out" ]; then
    printf '%s\n%s' "$repo" "$out"
  fi
}

scan_tree() { # $1 = repo dir
  local repo="$1" gm key path resolved keys
  scan_repo "$repo"
  [ "$RECURSE" -eq 1 ] || return 0
  gm="$repo/.gitmodules"
  [ -f "$gm" ] || return 0

  if ! keys=$(git config --file "$gm" --name-only --get-regexp '^submodule\..*\.path$' 2>/dev/null); then
    printf 'cannot enumerate submodules from %s\n' "$gm" >&2
    scan_errors=$((scan_errors + 1))
    return 0
  fi

  while IFS= read -r key; do
    [ -n "$key" ] || continue
    if ! path=$(git config --file "$gm" --get "$key"); then
      printf 'cannot read %s from %s\n' "$key" "$gm" >&2
      scan_errors=$((scan_errors + 1))
      continue
    fi
    path=${path%$'\r'}
    case "$path" in
      /*)
        printf 'absolute submodule path is outside scan contract: %s\n' "$path" >&2
        scan_errors=$((scan_errors + 1))
        continue ;;
    esac
    resolved=$(realpath -m -- "$repo/$path")
    case "$resolved/" in
      "$TOP"/*) ;;
      *)
        printf 'submodule path escapes scan root: %s -> %s\n' "$path" "$resolved" >&2
        scan_errors=$((scan_errors + 1))
        continue ;;
    esac
    if [ ! -d "$resolved" ] || [ ! -e "$resolved/.git" ]; then
      printf 'submodule not initialized; scan incomplete: %s\n' "$resolved" >&2
      scan_errors=$((scan_errors + 1))
      continue
    fi
    scan_tree "$resolved"
  done <<< "$keys"
}

scan_tree "$REPO"

printf '\n%s: %d repo(s), %d declared agent override(s), %d masked skill(s), %d undeclared agent(s), %d scan error(s)\n' \
  "$REPO" "$scanned" "$declared_agents" "$masked_skills" "$undeclared_agents" "$scan_errors"

[ "$scan_errors" -eq 0 ] || exit 2
[ "$total_defects" -eq 0 ] || exit 1
exit 0
