#!/usr/bin/env bash
# install.sh — deploy a fresh `.aidoc/` on a new consumer project.
#
# Automates framework/governance/aidoc/BOOTSTRAP.md steps 1–5:
#   1. copy the scaffold README into <project>/.aidoc/ and fill the
#      YYYY-MM-DD / author / X.Y.Z placeholders;
#   2. copy PROFILE-TEMPLATE.yaml to .aidoc/profile.yaml (knobs stay
#      commented — the project fills only what it overrides);
#   3. attach the framework: pinned allowlist copy (docs/PROJECT.md §7.1,
#      via allowlist.txt) or a symlink to a shared checkout;
#   4. pin metadata.framework_version to the adopted canon VERSION;
#   5. smoke-verify the BOOTSTRAP step-5 checks.
#
# Usage:
#   install.sh <project-dir> --canon <tag> [--kind pin|symlink]
#       [--shared <path>] [--canon-dir <dir>] [--author NAME]
#       [--dry-run] [--force] [--yes]
#
#   --canon <tag>     canon release tag, e.g. framework/v0.70.3 (required
#                     for --kind pin unless --canon-dir is given; verified
#                     against the canon VERSION when given).
#   --kind pin        pinned allowlist copy (default; self-contained).
#   --kind symlink    symlink .aidoc/framework at --shared <path> (persistent
#                     canon checkout; scratch clones are never linked).
#   --canon-dir <dir> use a local canon tree instead of cloning (air-gapped
#                     installs; must contain framework/VERSION; pin kind only).
#   --author NAME     fill the README author placeholder (default: git
#                     user.name, falling back to the current user).
#   --dry-run         print every mutation without performing it (read-only
#                     VERSION/tag checks still run for local canons).
#   --force           replace an existing <project>/.aidoc wholesale
#                     (WITHOUT it the script refuses to overwrite; requires
#                     --yes or a TTY confirm — the wholesale remove deletes
#                     .aidoc/project/ overrides too).
#   --yes             confirm a --force replace without prompting
#                     (required for non-interactive use).
# Exit codes: 0 ok · 1 failed (clone/template/smoke failure) ·
# 2 usage-or-refused.
#
# Reads the copy set from allowlist.txt (same directory as this script).
# Env: AIDOC_CANON_URL overrides the clone URL (default: the canon repo).
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ALLOWLIST="$SCRIPT_DIR/allowlist.txt"
CANON_URL="${AIDOC_CANON_URL:-https://github.com/vladm3105/aidoc-flow-framework.git}"
TODAY="$(date -u +%F)"

usage() { awk 'NR>=2 && /^# Reads the copy set/{exit} NR>=2' "$0" | sed 's/^# \{0,1\}//'; }

die() { echo "install.sh: error: $*" >&2; exit 1; }
refuse() { echo "install.sh: refused: $*" >&2; exit 2; }
log() { echo "install.sh: $*"; }
run() { # run <dry-text> <cmd...>: echo in dry-run, execute otherwise
  local text="$1"; shift
  if [ "${DRY_RUN:-0}" = 1 ]; then echo "dry-run: $text"; else "$@"; fi
}

PROJECT=""; CANON_TAG=""; KIND="pin"; SHARED=""; CANON_DIR=""; AUTHOR=""; DRY_RUN=0; FORCE=0; YES=0
need_value() { [ $# -ge 2 ] || refuse "$1 needs a value"; }
while [ $# -gt 0 ]; do
  case "$1" in
    --canon) need_value "$@"; CANON_TAG="$2"; shift 2 ;;
    --kind) need_value "$@"; KIND="$2"; shift 2 ;;
    --shared) need_value "$@"; SHARED="$2"; shift 2 ;;
    --canon-dir) need_value "$@"; CANON_DIR="$2"; shift 2 ;;
    --author) need_value "$@"; AUTHOR="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --force) FORCE=1; shift ;;
    --yes) YES=1; shift ;;
    -h|--help) usage; exit 0 ;;
    --*) refuse "unknown flag $1 (see --help)" ;;
    *) [ -z "$PROJECT" ] || refuse "one <project-dir> only"; PROJECT="$1"; shift ;;
  esac
done
[ -n "$PROJECT" ] || { usage >&2; refuse "missing <project-dir>"; }
[ "$KIND" = pin ] || [ "$KIND" = symlink ] || refuse "--kind must be pin or symlink"
[ -f "$ALLOWLIST" ] || die "allowlist not found: $ALLOWLIST"

[ -d "$PROJECT" ] || refuse "project dir must exist: $PROJECT"
PROJECT="$(cd -- "$PROJECT" && pwd)" # resolve symlinks/traversal; all writes stay under it
AIDOC="$PROJECT/.aidoc"
if [ -e "$AIDOC" ] && [ "$FORCE" != 1 ]; then
  refuse "$AIDOC already exists (pass --force to replace it wholesale)"
fi
if [ "$KIND" = symlink ] && [ -z "$SHARED" ]; then
  refuse "--kind symlink requires --shared <path> to a persistent canon checkout"
fi
if [ "$KIND" = symlink ] && [ -n "$CANON_DIR" ]; then
  refuse "--canon-dir is for --kind pin; the symlink kind reads --shared"
fi
if [ "$KIND" = pin ] && [ -z "$CANON_DIR" ] && [ -z "$CANON_TAG" ]; then
  refuse "--kind pin requires --canon <tag> (or --canon-dir <dir>)"
fi
if [ -n "$AUTHOR" ]; then :;
elif AUTHOR="$(git config user.name 2>/dev/null)" && [ -n "$AUTHOR" ]; then :;
else AUTHOR="$(id -un 2>/dev/null || echo engineer)"; fi

# Resolve the canon tree (clone to scratch, or use a given directory).
SCRATCH=""
cleanup() { [ -z "$SCRATCH" ] || rm -rf "$SCRATCH"; }
trap cleanup EXIT
CANON=""
if [ "$KIND" = symlink ]; then
  [ -d "$SHARED" ] || refuse "shared canon not a directory: $SHARED"
  CANON="$(cd -- "$SHARED" && pwd)" || refuse "cannot resolve --shared: $SHARED"
else
  if [ -n "$CANON_DIR" ]; then
    [ -d "$CANON_DIR" ] || refuse "canon dir not found: $CANON_DIR"
    CANON="$(cd -- "$CANON_DIR" && pwd)" || refuse "cannot resolve --canon-dir: $CANON_DIR"
  else
    SCRATCH="$(mktemp -d)"
    log "cloning $CANON_TAG to scratch"
    run "git clone --depth 1 --branch $CANON_TAG $CANON_URL <scratch>" \
      git clone --depth 1 --branch "$CANON_TAG" "$CANON_URL" "$SCRATCH"
    CANON="$SCRATCH"
  fi
fi
NEEDS_CLONE=0
if [ "$KIND" = pin ] && [ -z "$CANON_DIR" ]; then NEEDS_CLONE=1; fi
VERSION=""
if [ "$DRY_RUN" = 1 ] && [ "$NEEDS_CLONE" = 1 ]; then
  log "(dry-run: VERSION checks skipped — no clone performed)"
else
  [ -f "$CANON/framework/VERSION" ] || die "no framework/VERSION under canon tree: $CANON"
  VERSION="$(tr -d '[:space:]' < "$CANON/framework/VERSION")"
  case "$VERSION" in ''|*[!A-Za-z0-9._+-]*) die "bad canon VERSION: $VERSION" ;; esac
  if [ -n "$CANON_TAG" ]; then
    EXPECTED="${CANON_TAG#framework/v}"
    [ "$VERSION" = "$EXPECTED" ] || die "canon VERSION $VERSION != tag $CANON_TAG"
  fi
  log "canon framework/VERSION: $VERSION"
fi

# BOOTSTRAP step 1–2: scaffold README + profile template.
if [ -e "$AIDOC" ] && [ "$FORCE" = 1 ]; then
  if [ "$DRY_RUN" != 1 ] && [ "$YES" != 1 ]; then
    if [ ! -t 0 ]; then
      refuse "not a TTY — pass --yes to confirm replacing $AIDOC non-interactively (or --dry-run to preview)"
    fi
    printf '%s\n' "install.sh: WARNING: --force removes the existing $AIDOC wholesale (including .aidoc/project/ overrides)."
    read -r -p "install.sh: proceed? [y/N] " ans || ans=""
    case "$ans" in [Yy]|[Yy][Ee][Ss]) ;; *) refuse "aborted by operator" ;; esac
  fi
  run "rm -rf $AIDOC" rm -rf "$AIDOC"
fi
run "mkdir -p $AIDOC" mkdir -p "$AIDOC"
for src in "framework/governance/aidoc/AIDOC-SCAFFOLD-TEMPLATE.md:$AIDOC/README.md" \
           "framework/governance/PROFILE-TEMPLATE.yaml:$AIDOC/profile.yaml"; do
  from="$CANON/${src%%:*}"; to="${src##*:}"
  [ "$DRY_RUN" = 1 ] || [ -f "$from" ] || die "canon template missing: $from"
  run "cp $from $to" cp "$from" "$to"
done
if [ "$DRY_RUN" != 1 ]; then
  AUTHOR_ESC="$(printf '%s' "$AUTHOR" | sed 's/[&|\\]/\\&/g')"
  sed -i "s/YYYY-MM-DD/$TODAY/; s|<your name>|$AUTHOR_ESC|; s/X\\.Y\\.Z/$VERSION/g" "$AIDOC/README.md"
  sed -i -E "s/^(  framework_version: ).*/\\1\"$VERSION\"/; s/^(  last_updated: ).*/\\1\"$TODAY\"/" "$AIDOC/profile.yaml"
  log "README placeholders filled (date=$TODAY author=$AUTHOR version=$VERSION)"
  log "profile.yaml pinned at framework_version $VERSION"
else
  log "(dry-run: placeholder fill + version pin skipped)"
fi

# BOOTSTRAP step 3: attach the framework (pin or symlink).
if [ "$KIND" = symlink ]; then
  run "ln -s $CANON $AIDOC/framework" ln -s "$CANON" "$AIDOC/framework"
else
  run "mkdir -p $AIDOC/framework" mkdir -p "$AIDOC/framework"
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in ''|\#*) continue ;; esac
    case "$line" in
      '!'*) entry="${line#!}"
         case "$entry" in ''|/*|*..*) die "bad allowlist entry: $line" ;; esac
         run "rm -rf $AIDOC/framework/$entry" rm -rf "$AIDOC/framework/$entry" ;;
      *) d="${line%/}"
         case "$d" in ''|/*|*..*) die "bad allowlist entry: $line" ;; esac
         [ "$DRY_RUN" = 1 ] || [ -e "$CANON/$d" ] || die "allowlist entry missing from canon: $d"
         run "cp -r $CANON/$d $AIDOC/framework/" cp -r "$CANON/$d" "$AIDOC/framework/" ;;
    esac
  done < "$ALLOWLIST"
fi

# BOOTSTRAP step 4 is folded into the pin above; step 5: smoke-verify.
if [ "$DRY_RUN" = 1 ]; then log "(dry-run: smoke checks skipped)"; log "done (dry-run)"; exit 0; fi
if [ ! -f "$AIDOC/README.md" ] || [ ! -f "$AIDOC/profile.yaml" ]; then
  die "smoke: README/profile missing"
fi
if readlink -f "$AIDOC/framework" >/dev/null 2>&1; then :;
elif [ -e "$AIDOC/framework" ]; then :; # readlink -f missing (macOS): -e follows links too
else die "smoke: .aidoc/framework does not resolve"; fi
PINNED="$(sed -n -E 's/^  framework_version: "?([^"]+)"?/\1/p' "$AIDOC/profile.yaml" | head -1)"
[ "$PINNED" = "$VERSION" ] || die "smoke: profile pins $PINNED, canon is $VERSION"
SURFACE="$AIDOC/framework/framework/governance/ADAPTATION_SURFACE.yaml"
[ -f "$SURFACE" ] || die "smoke: incomplete copy — ADAPTATION_SURFACE.yaml missing"
if command -v python3 >/dev/null; then
  rc=0
  python3 - "$AIDOC/profile.yaml" "$SURFACE" <<'EOF' || rc=$?
import sys
try:
    import yaml
except ImportError:
    print("PyYAML unavailable — closed-key check SKIPPED", file=sys.stderr)
    sys.exit(2)
profile = yaml.safe_load(open(sys.argv[1])) or {}
surface = yaml.safe_load(open(sys.argv[2])) or {}
known = {k.get("name") for k in surface.get("knobs", []) or []} | {"metadata"}
unknown = [k for k in profile if k not in known]
if unknown:
    print(f"unknown profile keys: {unknown}", file=sys.stderr)
    sys.exit(1)
EOF
  if [ "$rc" = 0 ]; then log "smoke: profile keys within the closed surface";
  elif [ "$rc" = 2 ]; then log "WARNING: PyYAML unavailable — profile keys NOT verified (check BOOTSTRAP step 5 manually)";
  else die "smoke: profile.yaml carries unknown keys"; fi
else
  log "WARNING: python3 unavailable — profile keys NOT verified (check BOOTSTRAP step 5 manually)"
fi
log "done: kind=$KIND version=$VERSION aidoc=$AIDOC"
