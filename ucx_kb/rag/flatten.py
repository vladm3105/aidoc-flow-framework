"""YAML-to-text conversion rules for embedding."""

import re
from collections.abc import Callable
from typing import Any


def yaml_to_text(key: str, value: Any, depth: int = 0) -> str:
    """
    Convert YAML structure to readable text for embedding.

    Flattening rules:
    - key: value           → "Key: value"
    - key: [a, b, c]       → "Key: a, b, c"
    - key: [{k1: v1}, ...] → "Key:\\n- k1: v1\\n- ..."
    - nested dict          → "Parent — Child: value"
    - null / empty         → skip entirely
    - numbers              → format with context

    Args:
        key: YAML key
        value: YAML value (any type)
        depth: Nesting depth for formatting

    Returns:
        Flattened text representation
    """
    if value is None or value == "" or value == []:
        return ""

    human_key = humanize_key(key)

    if isinstance(value, str):
        return f"{human_key}: {value}"

    elif isinstance(value, bool):
        return f"{human_key}: {'Yes' if value else 'No'}"

    elif isinstance(value, (int, float)):
        return f"{human_key}: {_format_number(key, value)}"

    elif isinstance(value, list):
        if all(isinstance(item, (str, int, float, bool)) for item in value):
            # Simple list
            items = [str(item) for item in value if item]
            return f"{human_key}: {', '.join(items)}"
        else:
            # List of dicts
            lines = [f"{human_key}:"]
            for item in value:
                if isinstance(item, dict):
                    item_text = flatten_dict(item, depth + 1)
                    if item_text:
                        lines.append(f"  - {item_text}")
                else:
                    lines.append(f"  - {item}")
            return "\n".join(lines)

    elif isinstance(value, dict):
        lines = [f"{human_key}:"]
        for k, v in value.items():
            nested = yaml_to_text(k, v, depth + 1)
            if nested:
                lines.append(f"  {nested}")
        return "\n".join(lines)

    return f"{human_key}: {value}"


def flatten_dict(d: dict, depth: int = 0) -> str:
    """Flatten a dictionary to text."""
    parts = []
    for k, v in d.items():
        text = yaml_to_text(k, v, depth)
        if text:
            parts.append(text)
    return " | ".join(parts) if depth > 0 else "\n".join(parts)


def humanize_key(key: str) -> str:
    """
    Convert YAML key to human-readable label.

    Examples:
    - "revenue_trend_8q" → "Revenue Trend (8Q)"
    - "phase2_fundamentals" → "Phase 2 Fundamentals"
    - "yoy_pct" → "YoY %"
    """
    # Handle common abbreviations
    abbreviations = {
        "yoy": "YoY",
        "qoq": "QoQ",
        "mom": "MoM",
        "pct": "%",
        "eps": "EPS",
        "pe": "P/E",
        "pb": "P/B",
        "ps": "P/S",
        "ev": "EV",
        "ebitda": "EBITDA",
        "rsi": "RSI",
        "macd": "MACD",
        "sma": "SMA",
        "ema": "EMA",
    }

    # Split on underscores and numbers
    parts = re.split(r"[_]", key)
    result = []

    for part in parts:
        # Check for number suffix (e.g., "8q" → "(8Q)")
        num_match = re.match(r"^(\d+)([a-z]+)$", part)
        if num_match:
            result.append(f"({num_match.group(1).upper()}{num_match.group(2).upper()})")
            continue

        # Check for phase prefix
        phase_match = re.match(r"^phase(\d+)$", part.lower())
        if phase_match:
            result.append(f"Phase {phase_match.group(1)}")
            continue

        # Check for abbreviations
        lower = part.lower()
        if lower in abbreviations:
            result.append(abbreviations[lower])
        else:
            result.append(part.capitalize())

    return " ".join(result)


def _format_number(key: str, value: float | int) -> str:
    """Format number with appropriate context."""
    key_lower = key.lower()

    # Percentages
    if "pct" in key_lower or "percent" in key_lower or "rate" in key_lower:
        return f"{value:.1f}%"

    # Currency (millions/billions)
    if "revenue" in key_lower or "income" in key_lower or "price" in key_lower:
        if abs(value) >= 1_000_000_000:
            return f"${value / 1_000_000_000:.1f}B"
        elif abs(value) >= 1_000_000:
            return f"${value / 1_000_000:.1f}M"
        else:
            return f"${value:,.0f}"

    # Default formatting
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def flatten_list(items: list, item_formatter: Callable[[Any], str] | None = None) -> str:
    """Flatten a list to comma-separated or bullet points."""
    if not items:
        return ""

    if item_formatter:
        items = [item_formatter(item) for item in items]
    else:
        items = [str(item) for item in items if item]

    if len(items) <= 3:
        return ", ".join(items)
    else:
        return "\n".join(f"- {item}" for item in items)


def flatten_dict_list(items: list[dict]) -> str:
    """Flatten a list of dicts to formatted lines."""
    if not items:
        return ""

    lines = []
    for item in items:
        parts = []
        for k, v in item.items():
            if v:
                parts.append(f"{humanize_key(k)}: {v}")
        if parts:
            lines.append(" | ".join(parts))

    return "\n".join(lines)


def section_to_text(section_data: Any, section_label: str) -> str:
    """
    Convert a YAML section to embeddable text.

    Args:
        section_data: The section content (dict, list, or scalar)
        section_label: Human-readable section name

    Returns:
        Formatted text suitable for embedding
    """
    if section_data is None:
        return ""

    if isinstance(section_data, dict):
        return flatten_dict(section_data)
    elif isinstance(section_data, list):
        if all(isinstance(item, dict) for item in section_data):
            return flatten_dict_list(section_data)
        return flatten_list(section_data)
    else:
        return str(section_data)
