"""Project .env file loader with mtime-based caching and security protections."""

from __future__ import annotations

import logging
import os
import stat
from pathlib import Path
from typing import Any

from dotenv import dotenv_values

logger = logging.getLogger(__name__)

BLOCKED_ENV_VARS: frozenset[str] = frozenset({
    "PATH", "HOME", "PYTHONPATH", "LD_LIBRARY_PATH",
    "LD_PRELOAD", "SHELL", "USER", "IFS",
})

# mtime-based cache: {str(project_root): (mtime, env_dict)}
_env_cache: dict[str, tuple[float, dict[str, str]]] = {}


def _strip_bom_key(env: dict[str, str]) -> dict[str, str]:
    """Strip UTF-8 BOM prefix from the first key if present."""
    if not env:
        return env
    first_key = next(iter(env))
    if first_key.startswith("\ufeff"):
        cleaned_key = first_key.lstrip("\ufeff")
        val = env.pop(first_key)
        env[cleaned_key] = val
    return env


def _check_permissions(env_path: Path) -> None:
    """Warn if .env file is group/world-readable."""
    try:
        mode = env_path.stat().st_mode
        if mode & (stat.S_IRGRP | stat.S_IROTH | stat.S_IWGRP | stat.S_IWOTH):
            logger.warning(
                "Insecure permissions on %s (mode %o). "
                "Consider restricting to owner-only (chmod 600).",
                env_path, stat.S_IMODE(mode),
            )
    except OSError:
        pass


def load_project_env(project_root: Path) -> dict[str, str]:
    """Load .env from project root with mtime-based caching.

    Returns filtered env dict. Missing .env returns empty dict.
    System variables in BLOCKED_ENV_VARS are excluded with a warning.
    """
    env_path = project_root / ".env"
    cache_key = str(project_root)

    if not env_path.exists():
        _env_cache.pop(cache_key, None)
        return {}

    try:
        current_mtime = env_path.stat().st_mtime
    except OSError:
        return {}

    cached = _env_cache.get(cache_key)
    if cached is not None and cached[0] == current_mtime:
        return cached[1]

    _check_permissions(env_path)

    try:
        raw = dotenv_values(env_path, encoding="utf-8")
    except Exception:
        logger.warning("Failed to parse .env at %s — returning empty env", env_path)
        _env_cache[cache_key] = (current_mtime, {})
        return {}

    # Filter None values (bare KEY lines without =value)
    env: dict[str, str] = {k: v for k, v in raw.items() if v is not None}

    # Strip UTF-8 BOM from first key
    env = _strip_bom_key(env)

    # Block system variables
    blocked_found = BLOCKED_ENV_VARS & env.keys()
    if blocked_found:
        logger.warning(
            "Blocked system variables in %s: %s — these will not be passed to executors",
            env_path, ", ".join(sorted(blocked_found)),
        )
        for key in blocked_found:
            del env[key]

    _env_cache[cache_key] = (current_mtime, env)
    logger.info("Loaded %d env vars from %s", len(env), env_path)
    return env


def show_project_env(project_root: Path) -> dict[str, Any]:
    """Inspect project .env without exposing values. Returns keys only."""
    env_path = project_root / ".env"
    if not env_path.exists():
        return {
            "project_root": str(project_root),
            "env_file_exists": False,
            "env_keys": [],
            "env_key_count": 0,
            "blocked_vars": [],
        }

    try:
        raw = dotenv_values(env_path, encoding="utf-8")
    except Exception:
        return {
            "project_root": str(project_root),
            "env_file_exists": True,
            "env_keys": [],
            "env_key_count": 0,
            "blocked_vars": [],
            "parse_error": True,
        }

    all_keys = [k for k, v in raw.items() if v is not None]
    # Strip BOM from first key for display
    if all_keys and all_keys[0].startswith("\ufeff"):
        all_keys[0] = all_keys[0].lstrip("\ufeff")

    blocked = sorted(BLOCKED_ENV_VARS & set(all_keys))
    safe_keys = [k for k in all_keys if k not in BLOCKED_ENV_VARS]

    # API executor readiness: check if expected API key vars are present
    api_key_vars = {
        "LITELLM_MASTER_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "OPENROUTER_API_KEY",
    }
    api_keys_present = sorted(api_key_vars & set(safe_keys))
    ucx_overrides = {k: "(set)" for k in safe_keys if k.startswith("UCX_EXECUTOR_")}

    return {
        "project_root": str(project_root),
        "env_file_exists": True,
        "env_keys": safe_keys,
        "env_key_count": len(safe_keys),
        "blocked_vars": blocked,
        "api_keys_present": api_keys_present,
        "ucx_executor_overrides": ucx_overrides,
    }


def _invalidate_env_cache(project_root: Path) -> None:
    """Remove cached entry for a project (used in tests)."""
    _env_cache.pop(str(project_root), None)
