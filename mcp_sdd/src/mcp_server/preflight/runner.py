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
        checks["review_templates_exists"] = review_templates.exists()
        checks["personas_exists"] = personas.exists()
        if not review_templates.exists():
            errors.append("missing_review_templates")
        if not personas.exists():
            errors.append("missing_personas")

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

    # Token signals optional provider configuration readiness.
    checks["provider_token_present"] = bool(project_root.joinpath(".env").exists())
    if not checks["provider_token_present"]:
        warnings.append("provider_token_not_detected")

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
