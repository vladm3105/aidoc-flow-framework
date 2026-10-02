#!/usr/bin/env bash
# upgrade.sh — re-adopt a new canon framework/VERSION on a consumer project.
#
# Automates the mechanical half of framework/governance/aidoc/UPGRADE-RUNBOOK.md:
#   step 1 (inputs): prints the canon CHANGELOG pointer + override pins old
#     enough to conflict — reading them stays the operator's job;
#   step 2 (re-point): symlink consumers retarget .aidoc/framework at the new
#     canon location; pinned-copy consumers stage the docs/PROJECT.md §7.1
#     allowlist copy aside and swap it over the old tree in one rename
#     (never refreshing over it — cp -r never deletes, so upstream-removed
#     files would linger — and never half-copied);
#   stale detector (the runbook's "Minimal automation" follow-up, now
#     shipped): every .aidoc/project/ override's authored-against
#     framework_version pin is compared against the new canon VERSION and
#     drift is reported (DRIFT:/OK:/UNPINNED: lines, W002-measurable).
#
# NOT automated (stays manual per the runbook): resolving override conflicts
# (step 3), re-passing conformance (step 4 — pass --conformance-cmd to run it),
# and recording the upgrade in the consumer changelog (step 5).
#
# Usage:
#   upgrade.sh <project-dir> --to <tag> [--kind pin|symlink] [--shared <path>]
#       [--canon-dir <dir>] [--conformance-cmd CMD] [--dry-run] [--force] [--yes]
#
#   --to <tag>            target canon release, e.g. framework/v0.71.0 or
#                         a bare X.Y.Z (required unless --canon-dir given).
#   --kind pin|symlink    override the detected consumer kind (default:
#                         symlink when .aidoc/framework is a link, else pin).
#   --shared <path>       new canon location (required for --kind symlink).
#   --canon-dir <dir>     use a local canon tree instead of cloning
#                         (pin kind only).
#   --conformance-cmd CMD run CMD (from <project-dir>) after the re-point as
#                         the runbook step-4 suite; exit 1 on conformance
#                         failure (without it step 4 stays manual).
#   --dry-run             print every mutation without performing it (read-only
#                         VERSION/tag checks still run for local canons).
#   --force               skip the "already at target" refusal (re-install
#                         the same version; still never converts kinds).
#   --yes                 confirm the destructive re-point without prompting
#                         (required for non-interactive use; --dry-run never
#                         prompts and never mutates).
# Exit codes: 0 ok · 1 failed (clone/copy/conformance failure) ·
# 2 usage-or-refused.
#
# Reads the copy set from allowlist.txt (same directory as this script).
# Env: AIDOC_CANON_URL overrides the clone URL (default: the canon repo).
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ALLOWLIST="$SCRIPT_DIR/allowlist.txt"
CANON_URL="${AIDOC_CANON_URL:-https://github.com/vladm3105/aidoc-flow-framework.git}"

usage() { awk 'NR>=2 && /^# Reads the copy set/{exit} NR>=2' "$0" | sed 's/^# \{0,1\}//'; }

die() { echo "upgrade.sh: error: $*" >&2; exit 1; }
refuse() { echo "upgrade.sh: refused: $*" >&2; exit 2; }
log() { echo "upgrade.sh: $*"; }
run() { local text="$1"; shift
  if [ "${DRY_RUN:-0}" = 1 ]; then echo "dry-run: $text"; else "$@"; fi; }

PROJECT=""; TO=""; KIND=""; SHARED=""; CANON_DIR=""; CONF_CMD=""; DRY_RUN=0; FORCE=0; YES=0
need_value() { [ $# -ge 2 ] || refuse "$1 needs a value"; }
while [ $# -gt 0 ]; do
  case "$1" in
    --to) need_value "$@"; TO="$2"; shift 2 ;;
    --kind) need_value "$@"; KIND="$2"; shift 2 ;;
    --shared) need_value "$@"; SHARED="$2"; shift 2 ;;
    --canon-dir) need_value "$@"; CANON_DIR="$2"; shift 2 ;;
    --conformance-cmd) need_value "$@"; CONF_CMD="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --force) FORCE=1; shift ;;
    --yes) YES=1; shift ;;
    -h|--help) usage; exit 0 ;;
    --*) refuse "unknown flag $1 (see --help)" ;;
    *) [ -z "$PROJECT" ] || refuse "one <project-dir> only"; PROJECT="$1"; shift ;;
  esac
done
[ -n "$PROJECT" ] || { usage >&2; refuse "missing <project-dir>"; }
[ -f "$ALLOWLIST" ] || die "allowlist not found: $ALLOWLIST"

[ -d "$PROJECT" ] || refuse "project dir must exist: $PROJECT"
PROJECT="$(cd -- "$PROJECT" && pwd)" # resolve symlinks/traversal; all writes stay under it
AIDOC="$PROJECT/.aidoc"
[ -f "$AIDOC/profile.yaml" ] || refuse "no consumer .aidoc here: $AIDOC/profile.yaml missing"
FW="$AIDOC/framework"
[ -e "$FW" ] || [ -L "$FW" ] || refuse ".aidoc/framework missing — run install.sh first"
if [ -z "$KIND" ]; then
  if [ -L "$FW" ]; then KIND=symlink; else KIND=pin; fi
  log "detected kind: $KIND"
else
  [ "$KIND" = pin ] || [ "$KIND" = symlink ] || refuse "--kind must be pin or symlink"
  if [ "$KIND" = symlink ] && [ ! -L "$FW" ]; then
    refuse "--kind symlink but .aidoc/framework is not a link (kind conversion is out of scope — reinstall)"
  fi
  if [ "$KIND" = pin ] && [ -L "$FW" ]; then
    refuse "--kind pin but .aidoc/framework is a link (kind conversion is out of scope — reinstall)"
  fi
fi
if [ "$KIND" = symlink ] && [ -z "$SHARED" ]; then
  refuse "--kind symlink requires --shared <path> to the new canon location"
fi
if [ "$KIND" = symlink ] && [ -n "$CANON_DIR" ]; then
  refuse "--canon-dir is for --kind pin; the symlink kind reads --shared"
fi
if [ -z "$TO" ] && [ -z "$CANON_DIR" ]; then
  refuse "need --to <tag> (or --canon-dir <dir>)"
fi

CURRENT="$(sed -n -E 's/^  framework_version: "?([^"]+)"?/\1/p' "$AIDOC/profile.yaml" | head -1)"
[ -n "$CURRENT" ] || die "no framework_version pin in $AIDOC/profile.yaml"

SCRATCH=""
cleanup() { [ -z "$SCRATCH" ] || rm -rf "$SCRATCH"; }
trap cleanup EXIT
CANON=""
if [ "$KIND" = symlink ]; then
  [ -d "$SHARED" ] || refuse "shared canon not a directory: $SHARED"
  CANON="$(cd -- "$SHARED" && pwd)" || refuse "cannot resolve --shared: $SHARED"
elif [ -n "$CANON_DIR" ]; then
  [ -d "$CANON_DIR" ] || refuse "canon dir not found: $CANON_DIR"
  CANON="$(cd -- "$CANON_DIR" && pwd)" || refuse "cannot resolve --canon-dir: $CANON_DIR"
else
  SCRATCH="$(mktemp -d)"
  log "cloning $TO to scratch"
  run "git clone --depth 1 --branch $TO $CANON_URL <scratch>" \
    git clone --depth 1 --branch "$TO" "$CANON_URL" "$SCRATCH"
  CANON="$SCRATCH"
fi

NEEDS_CLONE=0
if [ "$KIND" = pin ] && [ -z "$CANON_DIR" ]; then NEEDS_CLONE=1; fi
NEW=""
if [ "$DRY_RUN" = 1 ] && [ "$NEEDS_CLONE" = 1 ]; then
  log "(dry-run: VERSION checks skipped — no clone performed)"
else
  [ -f "$CANON/framework/VERSION" ] || die "no framework/VERSION under canon tree: $CANON"
  NEW="$(tr -d '[:space:]' < "$CANON/framework/VERSION")"
  case "$NEW" in ''|*[!A-Za-z0-9._+-]*) die "bad canon VERSION: $NEW" ;; esac
  if [ -n "$TO" ]; then
    EXPECTED="${TO#framework/v}"
    [ "$NEW" = "$EXPECTED" ] || die "canon VERSION $NEW != --to $TO"
  fi
  log "re-adopting $CURRENT → $NEW"
  if [ "$NEW" = "$CURRENT" ] && [ "$FORCE" != 1 ]; then
    refuse "already at $NEW (pass --force to re-install the same version)"
  fi
fi

# Runbook step 1: surface the canon-side inputs (reading stays manual).
log "step 1: read the canon CHANGELOG entry for the new version (breaking changes, W001 notes)"
if [ "$DRY_RUN" != 1 ] && [ -f "$CANON/framework/CHANGELOG.md" ]; then
  log "canon changelog: $CANON/framework/CHANGELOG.md"
else
  log "canon changelog: <canon>/framework/CHANGELOG.md"
fi

# Stale detector (runbook step-1 input): report BEFORE the confirm gate so
# the operator confirms with the conflict list in hand — never confirm blind.
if [ "$DRY_RUN" = 1 ]; then
  log "(dry-run: stale detector skipped)"
elif [ ! -d "$AIDOC/project" ]; then
  log "no .aidoc/project/ overrides — nothing to diff (runbook step 3 vacuous)"
else
  DRIFT=0
  while IFS= read -r f; do
    pin="$(sed -n -E 's/^[[:space:]]*framework_version: "?([0-9][^"]*)"?/\1/p' "$f" | head -1)"
    rel="${f#"$AIDOC"/}"
    if [ -z "$pin" ]; then echo "UNPINNED: $rel (no authored-against framework_version)";
    elif [ "$pin" = "$NEW" ]; then echo "OK: $rel (at $NEW)";
    else echo "DRIFT: $rel (authored against $pin, canon now $NEW)"; DRIFT=$((DRIFT+1)); fi
  done < <(find "$AIDOC/project" -type f | sort)
  [ "$DRIFT" = 0 ] || log "$DRIFT override(s) older than $NEW — resolve per runbook step 3 (carry intent forward, never weaken gates)"
fi

# Destructive ops are never silent: confirm on a TTY, or require --yes.
if [ "$DRY_RUN" != 1 ] && [ "$YES" != 1 ]; then
  if [ ! -t 0 ]; then
    refuse "not a TTY — pass --yes to confirm the re-point non-interactively (or --dry-run to preview)"
  fi
  if [ "$KIND" = symlink ]; then op="retarget $FW at $CANON"; else op="remove $FW and re-copy the allowlist"; fi
  printf '%s\n' "upgrade.sh: about to $op."
  read -r -p "upgrade.sh: proceed? [y/N] " ans || ans=""
  case "$ans" in [Yy]|[Yy][Ee][Ss]) ;; *) refuse "aborted by operator" ;; esac
fi

# Runbook step 2: re-point framework_path.
if [ "$KIND" = symlink ]; then
  run "ln -sfn $CANON $FW" ln -sfn "$CANON" "$FW"
else
  # Stage-then-rename: the live tree stays old-complete until one rename —
  # never a half-copied tree (a mid-copy failure must not strand the consumer).
  STAGE="$FW.new"
  run "rm -rf $STAGE (clear stale stage)" rm -rf "$STAGE"
  run "mkdir -p $STAGE" mkdir -p "$STAGE"
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in ''|\#*) continue ;; esac
    case "$line" in
      '!'*) entry="${line#!}"
         case "$entry" in ''|/*|*..*) die "bad allowlist entry: $line" ;; esac
         run "rm -rf $STAGE/$entry" rm -rf "$STAGE/$entry" ;;
      *) d="${line%/}"
         case "$d" in ''|/*|*..*) die "bad allowlist entry: $line" ;; esac
         [ "$DRY_RUN" = 1 ] || [ -e "$CANON/$d" ] || die "allowlist entry missing from canon: $d"
         run "cp -r $CANON/$d $STAGE/" cp -r "$CANON/$d" "$STAGE/" ;;
    esac
  done < "$ALLOWLIST"
  if [ "$DRY_RUN" = 1 ]; then
    echo "dry-run: rm -rf $FW && mv $STAGE $FW (atomic replace)"
  else
    rm -rf "$FW" && mv "$STAGE" "$FW"
  fi
fi
if [ "$DRY_RUN" != 1 ]; then
  sed -i -E "s/^(  framework_version: ).*/\\1\"$NEW\"/" "$AIDOC/profile.yaml"
  VERIFY="$(sed -n -E 's/^  framework_version: "?([^"]+)"?/\1/p' "$AIDOC/profile.yaml" | head -1)"
  [ "$VERIFY" = "$NEW" ] || die "re-pin failed: profile reads $VERIFY, expected $NEW"
  log "profile.yaml re-pinned at framework_version $NEW (verified)"
fi

if [ "$DRY_RUN" = 1 ]; then log "done (dry-run)"; exit 0; fi

# Runbook step 4: conformance stays manual unless --conformance-cmd runs it.
if [ -n "$CONF_CMD" ]; then
  log "step 4: running conformance: $CONF_CMD"
  (cd "$PROJECT" && eval "$CONF_CMD") || die "conformance failed — the upgrade is not done until the suite is green"
  log "step 4: conformance green"
else
  log "step 4: STAYS MANUAL — re-pass the shared conformance suite before calling this done"
fi
log "step 5: STAYS MANUAL — record old→new + conflicts + suite result in the consumer changelog"
log "done: kind=$KIND $CURRENT → $NEW"
