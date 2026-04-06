from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys

from mcp_server.skills.project_ucx_loader import resolve_ucx_root


_ALLOWED_CONTEXTS = {"create", "review", "remediate", "any"}
_STATUS_TOKEN_PATTERN = re.compile(r"\b(READY|DEGRADED|BLOCKED)\b", re.IGNORECASE)
_ISO_DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


@dataclass(frozen=True)
class PreflightRunResult:
    payload: dict[str, object]
    report_json: str
    report_text: str
    status: str
    report_path: Path | None
    summary_path: Path | None

    @property
    def report(self) -> dict[str, object]:
        """Alias for payload (API consistency)."""
        return self.payload

    @property
    def is_ready(self) -> bool:
        """Alias for status == 'ready' (API consistency)."""
        return self.status == "ready"


def _render_text(payload: dict[str, object]) -> str:
    lines = [
        "MCP Preflight Report",
        f"Project: {payload.get('project_root')}",
        f"Context: {payload.get('context')}",
        f"Status: {str(payload.get('status', 'blocked')).upper()}",
        "",
    ]

    checks = payload.get("checks", {})
    if isinstance(checks, dict):
        lines.append("Checks:")
        for key in sorted(checks):
            lines.append(f"- {key}: {checks[key]}")
        lines.append("")

    warnings = payload.get("warnings", [])
    if isinstance(warnings, list) and warnings:
        lines.append("Warnings:")
        lines.extend(f"- {item}" for item in warnings if isinstance(item, str))
        lines.append("")

    errors = payload.get("errors", [])
    if isinstance(errors, list) and errors:
        lines.append("Errors:")
        lines.extend(f"- {item}" for item in errors if isinstance(item, str))

    return "\n".join(lines).rstrip() + "\n"


def _parse_probe_payload(text: str) -> dict[str, object]:
    """Best-effort parse for provider probe output with fallback token extraction."""
    stripped = text.strip()
    if not stripped:
        return {
            "status": "degraded",
            "fallback_used": True,
            "reason": "empty_probe_payload",
            "iso_dates": [],
        }

    # Primary path: JSON payload with status key.
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, dict):
            raw_status = str(parsed.get("status", "")).strip().lower()
            if raw_status in {"ready", "degraded", "blocked"}:
                return {
                    "status": raw_status,
                    "fallback_used": False,
                    "reason": "json_status",
                    "iso_dates": sorted(set(_ISO_DATE_PATTERN.findall(stripped))),
                }
    except json.JSONDecodeError:
        pass

    # Fallback: status token scan from free-form text.
    token_match = _STATUS_TOKEN_PATTERN.search(stripped)
    iso_dates = sorted(set(_ISO_DATE_PATTERN.findall(stripped)))
    if token_match:
        return {
            "status": token_match.group(1).lower(),
            "fallback_used": True,
            "reason": "token_scan",
            "iso_dates": iso_dates,
        }

    # Secondary fallback: infer degraded when only temporal proof exists.
    if iso_dates:
        return {
            "status": "degraded",
            "fallback_used": True,
            "reason": "iso_date_fallback",
            "iso_dates": iso_dates,
        }

    return {
        "status": "blocked",
        "fallback_used": True,
        "reason": "no_status_signal",
        "iso_dates": [],
    }


def run_preflight(
    *,
    project_root: Path,
    context: str,
    document_path: Path | None = None,
    output_dir: Path | None = None,
) -> PreflightRunResult:
    normalized_context = context.strip().lower()
    if normalized_context not in _ALLOWED_CONTEXTS:
        raise ValueError(f"Unsupported preflight context: {context}")

    ucx_root = resolve_ucx_root(project_root)
    checks: dict[str, object] = {
        "project_exists": project_root.exists(),
        "ucx_root_exists": ucx_root.exists(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_supported": (sys.version_info.major, sys.version_info.minor) >= (3, 11),
    }

    errors: list[str] = []
    warnings: list[str] = []

    if not project_root.exists():
        errors.append("missing_project_root")
    if not ucx_root.exists():
        errors.append("missing_docs_ucx")

    if normalized_context in {"create", "any"}:
        create_templates = ucx_root / "prompts/templates/creation"
        checks["creation_templates_exists"] = create_templates.exists()
        if not create_templates.exists():
            errors.append("missing_creation_templates")

    if normalized_context in {"review", "remediate", "any"}:
        review_templates = ucx_root / "prompts/templates/review"
        personas = ucx_root / "skills/personas"
        persona_mappings = ucx_root / "skills/persona_mappings.yaml"
        checks["review_templates_exists"] = review_templates.exists()
        checks["personas_exists"] = personas.exists()
        checks["persona_mappings_exists"] = persona_mappings.exists()
        if not review_templates.exists():
            errors.append("missing_review_templates")
        if not personas.exists():
            errors.append("missing_personas")
        if not persona_mappings.exists():
            warnings.append("missing_persona_mappings")
        elif persona_mappings.exists():
            try:
                from mcp_server.skills.persona_manager import check_persona_mapping_health
                health = check_persona_mapping_health(project_root=project_root)
                checks["persona_mapping_health"] = health["status"]
                for name in health["missing_persona_files"]:
                    errors.append(f"persona_file_missing:{name}")
                for entry in health["missing_doctypes"]:
                    warnings.append(f"persona_mapping_incomplete:{entry}")
            except Exception:
                warnings.append("persona_mapping_health_check_failed")

    if document_path is not None:
        checks["document_exists"] = document_path.exists()
        if not document_path.exists():
            errors.append("missing_document_path")

    # Optional probe file path for local deterministic diagnostics.
    probe_file = project_root / "tmp" / "preflight_probe_response.txt"
    if probe_file.exists() and probe_file.is_file():
        probe_result = _parse_probe_payload(probe_file.read_text(encoding="utf-8"))
        checks["probe_file"] = str(probe_file)
        checks["probe_status"] = probe_result["status"]
        checks["probe_fallback_used"] = probe_result["fallback_used"]
        checks["probe_fallback_reason"] = probe_result["reason"]
        checks["probe_iso_dates"] = probe_result["iso_dates"]

        probe_status = str(probe_result["status"])
        if probe_status == "blocked":
            errors.append("provider_probe_blocked")
        elif probe_status == "degraded":
            warnings.append("provider_probe_degraded")

    # Project .env loading and inspection.
    env_path = project_root / ".env"
    checks["provider_token_present"] = env_path.exists()
    if not checks["provider_token_present"]:
        warnings.append("provider_token_not_detected")
    else:
        try:
            from mcp_server.env_manager import load_project_env, show_project_env, BLOCKED_ENV_VARS
            env_info = show_project_env(project_root)
            checks["env_key_count"] = env_info["env_key_count"]
            checks["env_keys"] = env_info["env_keys"]
            if env_info.get("blocked_vars"):
                checks["env_blocked_vars"] = env_info["blocked_vars"]
                warnings.append(f"env_blocked_vars:{','.join(env_info['blocked_vars'])}")
            if env_info.get("parse_error"):
                warnings.append("env_parse_error")
        except Exception:
            warnings.append("env_inspection_failed")

    if errors:
        status = "blocked"
    elif warnings:
        status = "degraded"
    else:
        status = "ready"

    payload: dict[str, object] = {
        "project_root": str(project_root),
        "context": normalized_context,
        "status": status,
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
    }

    report_json = json.dumps(payload, sort_keys=True)
    report_text = _render_text(payload)

    report_path: Path | None = None
    summary_path: Path | None = None
    # Default output to the parent document folder per PLAN-017 convention.
    if output_dir is None and document_path is not None:
        output_dir = document_path.parent if document_path.is_file() else document_path
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / "preflight_report.json"
        summary_path = output_dir / "preflight_report.txt"
        report_path.write_text(report_json, encoding="utf-8")
        summary_path.write_text(report_text, encoding="utf-8")

    return PreflightRunResult(
        payload=payload,
        report_json=report_json,
        report_text=report_text,
        status=status,
        report_path=report_path,
        summary_path=summary_path,
    )
