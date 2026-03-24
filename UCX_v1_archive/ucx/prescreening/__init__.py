"""UCX Scanner Module (formerly Pre-Screening).

Provides unified report analysis for adaptive remediation:
- scan_ucr_report(): Unified scanner with manifest + persona extraction
- analyze_ucr_report(): Legacy persona-based extraction (backward compat)
- parse_chairperson_manifest(): Extract from Chairperson's manifest
"""

from ucx.prescreening.ucr_analyzer import (
    # Unified scanner (v1.11.0+)
    scan_ucr_report,
    ScanResult,
    ManifestResult,
    ManifestFinding,
    parse_chairperson_manifest,
    # Legacy (backward compat)
    analyze_ucr_report,
    ScreeningResult,
    Finding,
    PERSONA_TO_FIXER,
)

__all__ = [
    # Unified scanner (recommended)
    "scan_ucr_report",
    "ScanResult",
    "ManifestResult",
    "ManifestFinding",
    "parse_chairperson_manifest",
    # Legacy (backward compat)
    "analyze_ucr_report",
    "ScreeningResult",
    "Finding",
    "PERSONA_TO_FIXER",
]
