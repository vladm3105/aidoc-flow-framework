"""UCX Scanner - Unified Report Analysis for Remediation.

Renamed from Pre-Screening (v1.10.3) to UCX Scanner (v1.11.0).

Analyzes UCR review reports using two extraction methods:
1. **Manifest Extraction**: Parses Chairperson's Remediation Findings Manifest (authoritative)
2. **Persona Extraction**: Extracts findings from individual persona sections (fixer routing)

The Chairperson manifest is the authoritative source for:
- Unique finding counts (P0/P1/P2)
- PRD-Ready Score
- Fixer assignments

Persona extraction is used for:
- Backward compatibility with pre-manifest reports
- Fixer routing when manifest not present
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


# Mapping: UCR review personas → Fixer personas
PERSONA_TO_FIXER: dict[str, Optional[str]] = {
    # Direct mappings
    "architect": "architect",
    "auditor": "auditor",
    "qa_lead": "qa_lead",
    "qa lead": "qa_lead",
    "devils_advocate": "devils_advocate",
    "devil's advocate": "devils_advocate",
    "devils advocate": "devils_advocate",
    "integration_expert": "integration_lead",
    "integration expert": "integration_lead",
    "integration_lead": "integration_lead",  # Direct mapping
    "integration lead": "integration_lead",
    # Indirect mappings
    "tech_lead": "qa_lead",
    "tech lead": "qa_lead",
    "operator": "integration_lead",
    # Business-level personas (no fixer mapping - handled at BRD/PRD level)
    "strategist": None,
    "product_owner": None,
    "product owner": None,
    "business_analyst": None,
    "business analyst": None,
    "ux_strategist": None,
    "ux strategist": None,
    "fact_checker": None,
    "fact checker": None,
    "chairperson": None,  # Chairperson is always loaded as mandatory
    "requirements_specialist": None,
    "requirements specialist": None,
}

# Domain-specific fixers (adaptive loading based on findings)
DOMAIN_FIXER_SKILLS: list[str] = [
    "architect",
    "auditor",
    "qa_lead",
    "integration_lead",
]

# Mandatory fixers (always loaded regardless of findings)
MANDATORY_FIXER_SKILLS: list[str] = [
    "devils_advocate",  # Safety: root cause vs symptom validation
    "chairperson",      # Synthesis: de-dupe, conflict resolution, final conclusion
]


@dataclass
class Finding:
    """Single UCR finding."""
    id: str
    priority: str  # P0, P1, P2
    status: str    # OPEN, RESOLVED, DEFERRED
    persona: str
    description: str

    @property
    def is_actionable(self) -> bool:
        """Check if finding requires remediation action.

        DEFERRED findings are NOT actionable - they're explicitly being
        deferred to another document (e.g., "Defer to SPEC", "Defer to BRD-02").
        """
        return (
            self.priority in ("P0", "P1")
            and self.status not in ("RESOLVED", "VERIFIED", "CLOSED", "DEFERRED")
        )


@dataclass
class ScreeningResult:
    """Pre-screening analysis result."""
    required_fixers: list[str] = field(default_factory=list)
    findings_by_fixer: dict[str, list[str]] = field(default_factory=dict)
    excluded_fixers: list[str] = field(default_factory=list)
    total_findings: int = 0
    actionable_findings: int = 0
    all_findings: list[Finding] = field(default_factory=list)

    @property
    def has_actionable_findings(self) -> bool:
        """Check if there are any findings requiring remediation."""
        return self.actionable_findings > 0

    @property
    def domain_fixers_needed(self) -> list[str]:
        """Get only domain fixers (excluding mandatory)."""
        return [f for f in self.required_fixers if f in DOMAIN_FIXER_SKILLS]

    @property
    def unique_findings(self) -> int:
        """Count of unique finding IDs (deduplicated across personas)."""
        return len(set(f.id for f in self.all_findings))

    @property
    def resolved_findings(self) -> int:
        """Count of unique resolved findings."""
        seen = set()
        count = 0
        for f in self.all_findings:
            if f.id not in seen and f.status == "RESOLVED":
                seen.add(f.id)
                count += 1
        return count

    @property
    def deferred_findings(self) -> int:
        """Count of unique deferred findings."""
        seen = set()
        count = 0
        for f in self.all_findings:
            if f.id not in seen and f.status == "DEFERRED":
                seen.add(f.id)
                count += 1
        return count

    @property
    def open_findings(self) -> int:
        """Count of unique open findings."""
        seen = set()
        count = 0
        for f in self.all_findings:
            if f.id not in seen and f.status == "OPEN":
                seen.add(f.id)
                count += 1
        return count

    def get_findings_by_priority(self) -> dict[str, dict[str, int]]:
        """Get finding counts by priority and status."""
        from collections import defaultdict
        result: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for f in self.all_findings:
            result[f.priority][f.status] += 1
        return dict(result)

    def get_unique_actionable_ids(self) -> list[str]:
        """Get unique actionable finding IDs (deduplicated across personas)."""
        seen = set()
        unique = []
        for f in self.all_findings:
            if f.is_actionable and f.id not in seen:
                seen.add(f.id)
                unique.append(f.id)
        return unique

    def get_unique_findings_by_priority(self) -> dict[str, dict[str, int]]:
        """Get unique finding counts by priority and status (deduplicated)."""
        from collections import defaultdict
        seen = set()
        result: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for f in self.all_findings:
            if f.id not in seen:
                seen.add(f.id)
                result[f.priority][f.status] += 1
        return dict(result)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "required_fixers": self.required_fixers,
            "findings_by_fixer": self.findings_by_fixer,
            "excluded_fixers": self.excluded_fixers,
            "unique_findings": self.unique_findings,
            "open_findings": self.open_findings,
            "resolved_findings": self.resolved_findings,
            "deferred_findings": self.deferred_findings,
            "actionable_findings": len(self.get_unique_actionable_ids()),
            "unique_actionable_ids": self.get_unique_actionable_ids(),
            "findings_by_priority": self.get_unique_findings_by_priority(),
            "domain_fixers_needed": self.domain_fixers_needed,
        }


def analyze_ucr_report(report_path: Path) -> ScreeningResult:
    """
    Analyze UCR report and determine required fixer personas.

    Pre-screens the review report to identify which domain-specific fixers
    are needed based on actual P0/P1 findings. Mandatory fixers (devils_advocate,
    chairperson) are always included.

    Args:
        report_path: Path to UCR review report

    Returns:
        ScreeningResult with required fixers and findings mapping

    Example:
        >>> result = analyze_ucr_report(Path("BRD-01.UCR_review_report_v003.md"))
        >>> print(result.required_fixers)
        ['auditor', 'devils_advocate', 'chairperson']
        >>> print(result.excluded_fixers)
        ['architect', 'integration_lead', 'qa_lead']
    """
    content = report_path.read_text(encoding="utf-8")
    result = ScreeningResult()

    # Extract persona sections
    persona_sections = _extract_persona_sections(content)

    # Analyze each section for actionable findings
    fixer_findings: dict[str, list[str]] = {}

    for persona, section_content in persona_sections.items():
        findings = _extract_findings(section_content, persona)
        result.all_findings.extend(findings)

        # Filter actionable: P0/P1 that are NOT resolved
        actionable = [f for f in findings if f.is_actionable]

        result.total_findings += len(findings)
        result.actionable_findings += len(actionable)

        if actionable:
            fixer = PERSONA_TO_FIXER.get(persona.lower())
            if fixer and fixer in DOMAIN_FIXER_SKILLS:
                if fixer not in fixer_findings:
                    fixer_findings[fixer] = []
                fixer_findings[fixer].extend([f.id for f in actionable])

    # Build required fixers list
    required = list(fixer_findings.keys())

    # Always include mandatory fixers if there are any actionable findings
    if result.actionable_findings > 0:
        for mandatory in MANDATORY_FIXER_SKILLS:
            if mandatory not in required:
                required.append(mandatory)

    # Sort fixers in proper order
    result.required_fixers = _sort_fixers(required)
    result.findings_by_fixer = fixer_findings
    result.excluded_fixers = sorted(
        set(DOMAIN_FIXER_SKILLS) - set(fixer_findings.keys())
    )

    return result


def _extract_persona_sections(content: str) -> dict[str, str]:
    """
    Extract content by MAIN persona section from UCR report.

    Only matches top-level persona sections like:
    - "## 1. Architect Review"
    - "## 2. Auditor Review"

    Does NOT match sub-sections like "## P1 Compliance Gaps".
    All content under a main persona section is grouped together.
    """
    sections = {}

    # Pattern: ## N. Persona Review (must have number prefix)
    # This ensures we only capture main persona sections, not sub-sections
    main_section_pattern = r"##\s+(\d+)\.\s+([\w\s']+?)\s+Review\s*\n"

    # Find all main section positions
    main_sections = list(re.finditer(main_section_pattern, content, re.IGNORECASE))

    for i, match in enumerate(main_sections):
        section_num = match.group(1)
        persona_raw = match.group(2).strip()

        # Get content from this section to the next main section (or end)
        start_pos = match.end()
        if i + 1 < len(main_sections):
            end_pos = main_sections[i + 1].start()
        else:
            end_pos = len(content)

        section_content = content[start_pos:end_pos]

        # Normalize persona name
        persona = _normalize_persona_name(persona_raw)
        if persona:
            # If persona already exists (shouldn't happen), append content
            if persona in sections:
                sections[persona] += "\n" + section_content
            else:
                sections[persona] = section_content

    return sections


def _normalize_persona_name(raw_name: str) -> Optional[str]:
    """Normalize persona name to standard format."""
    # Remove common prefixes/suffixes
    name = raw_name.lower().strip()
    name = re.sub(r"^the\s+", "", name)
    name = re.sub(r"\s+(review|assessment|analysis|findings)$", "", name)

    # Replace spaces with underscores
    name = name.replace(" ", "_").replace("'", "")

    # Map to known personas
    known_personas = set(PERSONA_TO_FIXER.keys())
    if name in known_personas:
        return name

    # Try partial matches
    for known in known_personas:
        if name in known or known in name:
            return known

    return name if name else None


def _extract_findings(section_content: str, persona: str) -> list[Finding]:
    """
    Extract findings from a persona section.

    Handles multiple formats:
    - Table rows: | ID | Finding | Section | ... |
    - Inline: P0-1: Description
    - Prefixed: AUD-P1-001, DA-P0-NEW-006

    Excludes:
    - Summary rows (e.g., "DA-P1-NEW-008 through DA-P1-NEW-012")
    - Range expressions (e.g., "PO-P1-001 through PO-P1-005")
    """
    findings = []
    seen_ids = set()

    # Pattern 1: Table rows with finding IDs at START of cell
    # Matches: | **P0-1** | Description | or | AUD-P1-001 | Description |
    # The ID must be the first content in the cell (after optional **)
    table_pattern = r"\|\s*(?:\*\*)?([A-Z]{2,}-?P[012]-(?:NEW-)?\d+|P[012]-\d+)(?:\*\*)?\s*\|([^|]+)"

    for match in re.finditer(table_pattern, section_content):
        finding_id = match.group(1).strip().replace("**", "")
        description = match.group(2).strip()

        if finding_id in seen_ids:
            continue

        # Skip if this is a summary/count row (description starts with number or is very short)
        if re.match(r"^\d+$", description.strip()):
            continue

        # Skip if this looks like a header row
        if description.lower() in ("finding", "description", "gap", "status", "count"):
            continue

        seen_ids.add(finding_id)

        priority = _extract_priority(finding_id)
        status = _extract_status(description, section_content, finding_id)

        findings.append(Finding(
            id=finding_id,
            priority=priority,
            status=status,
            persona=persona,
            description=description[:200]
        ))

    # Pattern 2: Standalone finding references in text (NOT in range expressions)
    # Matches: AUD-P1-002: description
    # Does NOT match: "DA-P1-NEW-008 through DA-P1-NEW-012"
    standalone_pattern = r"(?<!\|)\s*(?:\*\*)?([A-Z]{2,}-P[012]-(?:NEW-)?\d+)(?:\*\*)?[:\s]"

    for match in re.finditer(standalone_pattern, section_content):
        finding_id = match.group(1).strip().replace("**", "")

        if finding_id in seen_ids:
            continue

        # Get surrounding context to check for range expressions
        ctx_start = max(0, match.start() - 20)
        ctx_end = min(len(section_content), match.end() + 20)
        context_check = section_content[ctx_start:ctx_end].lower()

        # Skip if this is part of a range expression
        if any(marker in context_check for marker in ["through", " to ", " - "]):
            # Check if "through" or "to" appears right before this ID
            pre_context = section_content[ctx_start:match.start()].lower()
            if "through" in pre_context or pre_context.rstrip().endswith(" to"):
                continue

        seen_ids.add(finding_id)

        # Get surrounding context for description
        start = max(0, match.start() - 10)
        end = min(len(section_content), match.end() + 100)
        context = section_content[start:end]

        priority = _extract_priority(finding_id)
        status = _extract_status(context, section_content, finding_id)

        findings.append(Finding(
            id=finding_id,
            priority=priority,
            status=status,
            persona=persona,
            description=context[:200]
        ))

    return findings


def _extract_priority(finding_id: str) -> str:
    """Extract priority level from finding ID."""
    if "P0" in finding_id.upper():
        return "P0"
    elif "P1" in finding_id.upper():
        return "P1"
    elif "P2" in finding_id.upper():
        return "P2"
    return "P1"  # Default to P1


def _extract_status(description: str, full_content: str, finding_id: str) -> str:
    """
    Determine finding status from context.

    Checks for status markers in description and the same table row.
    IMPORTANT: Only marks as RESOLVED/DEFERRED if the status marker is in the
    SAME row as the finding ID, not elsewhere in the document.

    Status detection order:
    1. Description column: ✅/RESOLVED/VERIFIED → RESOLVED
    2. Row-level: Explicit "**Defer to" pattern (remediation column) → DEFERRED
    3. Full row: ✅/RESOLVED anywhere in row → RESOLVED
    4. Full row: NOT APPLIED/❌ anywhere in row → OPEN
    5. Default: OPEN

    NOTE: "POST-MVP" and "FUTURE" are NOT used for DEFERRED detection at row level
    because they often appear in problem descriptions, not as deferral decisions.
    Only explicit "Defer to X" patterns indicate actual deferral.
    """
    # Check immediate description
    desc_upper = description.upper()

    # Resolved indicators in description - must be clear status markers
    # Note: "CLOSED" is NOT checked here because it can appear in context
    # like "closed bank account" which doesn't mean the finding is closed
    if "✅" in description:
        return "RESOLVED"
    # Check for status words at word boundaries (not part of other words)
    if re.search(r"\b(RESOLVED|VERIFIED|FIXED)\b", desc_upper):
        return "RESOLVED"

    # Check if finding appears in a table row with resolved status
    # Pattern: | FINDING_ID | ... | ✅ ... | (same row, any column)
    # The [^\n]* ensures we only match within the same line (table row)
    resolved_row_pattern = rf"\|\s*(?:\*\*)?{re.escape(finding_id)}(?:\*\*)?\s*\|[^\n]*✅[^\n]*\|"
    if re.search(resolved_row_pattern, full_content, re.IGNORECASE):
        return "RESOLVED"

    # Also check for "RESOLVED" text in same row
    resolved_text_pattern = rf"\|\s*(?:\*\*)?{re.escape(finding_id)}(?:\*\*)?\s*\|[^\n]*RESOLVED[^\n]*\|"
    if re.search(resolved_text_pattern, full_content, re.IGNORECASE):
        return "RESOLVED"

    # Check if finding appears in a table row with EXPLICIT deferral
    # Only match "**Defer to" or "Defer to" patterns (typically in remediation column)
    # This catches "**Defer to SPEC**", "**Defer to BRD-02**", etc.
    # Does NOT match casual mentions of "post-MVP" in problem descriptions
    deferred_row_pattern = rf"\|\s*(?:\*\*)?{re.escape(finding_id)}(?:\*\*)?\s*\|[^\n]*\*?\*?Defer(?:red)?\s+to\b[^\n]*\|"
    if re.search(deferred_row_pattern, full_content, re.IGNORECASE):
        return "DEFERRED"

    # Check for explicit "NOT APPLIED" or "UNRESOLVED" markers (these mean OPEN)
    not_applied_pattern = rf"\|\s*(?:\*\*)?{re.escape(finding_id)}(?:\*\*)?\s*\|[^\n]*(?:NOT APPLIED|UNRESOLVED|❌)[^\n]*\|"
    if re.search(not_applied_pattern, full_content, re.IGNORECASE):
        return "OPEN"

    return "OPEN"


def _sort_fixers(fixers: list[str]) -> list[str]:
    """
    Sort fixers in execution order.

    Order: Domain fixers first (alphabetical), then devils_advocate, then chairperson last.
    """
    order = {
        # Domain fixers (alphabetical)
        "architect": 1,
        "auditor": 2,
        "integration_lead": 3,
        "qa_lead": 4,
        # Mandatory fixers (safety check, then synthesis)
        "devils_advocate": 10,  # Validates all fixes
        "chairperson": 20,       # Final synthesis (must be last)
    }
    return sorted(fixers, key=lambda x: order.get(x, 99))


# =============================================================================
# MANIFEST PARSING (v1.11.0+)
# =============================================================================

@dataclass
class ManifestFinding:
    """Single finding from Chairperson's Remediation Findings Manifest."""
    id: str                    # REM-P0-001, REM-P1-015
    priority: str              # P0, P1, P2
    status: str                # OPEN, RESOLVED, DEFERRED
    fixer: Optional[str]       # architect, auditor, etc. or None for deferred
    target_file: Optional[str] # BRD-01.6_functional_requirements.md
    target_section: Optional[str]  # Section 6.1
    description: str

    @property
    def is_actionable(self) -> bool:
        """Check if finding requires remediation action."""
        return (
            self.priority in ("P0", "P1")
            and self.status not in ("RESOLVED", "DEFERRED")
        )


@dataclass
class ManifestResult:
    """Chairperson manifest extraction result (authoritative)."""
    has_manifest: bool = False

    # Summary counts from manifest
    total_findings: int = 0
    p0_count: int = 0
    p1_count: int = 0
    p2_count: int = 0
    resolved_count: int = 0
    deferred_count: int = 0
    actionable_count: int = 0

    # Score from Chairperson
    prd_ready_score: Optional[int] = None
    recommendation: Optional[str] = None  # PROCEED, REMEDIATION REQUIRED, FUNDAMENTAL REDESIGN

    # Fixer assignments from manifest
    findings_by_fixer: dict[str, list[str]] = field(default_factory=dict)

    # All findings
    findings: list[ManifestFinding] = field(default_factory=list)

    # Raw extraction metadata
    manifest_version: Optional[str] = None

    def get_required_fixers(self) -> list[str]:
        """Get list of fixers with actionable findings."""
        fixers = list(self.findings_by_fixer.keys())

        # Always add mandatory fixers if there are actionable findings
        if self.actionable_count > 0:
            for mandatory in MANDATORY_FIXER_SKILLS:
                if mandatory not in fixers:
                    fixers.append(mandatory)

        return _sort_fixers(fixers)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "has_manifest": self.has_manifest,
            "total_findings": self.total_findings,
            "p0_count": self.p0_count,
            "p1_count": self.p1_count,
            "p2_count": self.p2_count,
            "resolved_count": self.resolved_count,
            "deferred_count": self.deferred_count,
            "actionable_count": self.actionable_count,
            "prd_ready_score": self.prd_ready_score,
            "recommendation": self.recommendation,
            "required_fixers": self.get_required_fixers(),
            "findings_by_fixer": self.findings_by_fixer,
            "findings": [
                {
                    "id": f.id,
                    "priority": f.priority,
                    "status": f.status,
                    "fixer": f.fixer,
                    "target_file": f.target_file,
                    "target_section": f.target_section,
                    "description": f.description[:200],
                }
                for f in self.findings
            ],
        }


@dataclass
class ScanResult:
    """Unified scan result combining manifest and persona extraction."""
    # Manifest data (authoritative when present)
    manifest: ManifestResult = field(default_factory=ManifestResult)

    # Persona-based extraction (for backward compatibility / fixer routing)
    persona_extraction: ScreeningResult = field(default_factory=ScreeningResult)

    @property
    def has_manifest(self) -> bool:
        """Check if Chairperson manifest was found."""
        return self.manifest.has_manifest

    @property
    def authoritative_counts(self) -> dict[str, int]:
        """Get authoritative finding counts (manifest if present, else persona)."""
        if self.has_manifest:
            return {
                "total": self.manifest.total_findings,
                "p0": self.manifest.p0_count,
                "p1": self.manifest.p1_count,
                "p2": self.manifest.p2_count,
                "resolved": self.manifest.resolved_count,
                "deferred": self.manifest.deferred_count,
                "actionable": self.manifest.actionable_count,
            }
        else:
            by_priority = self.persona_extraction.get_unique_findings_by_priority()
            return {
                "total": self.persona_extraction.unique_findings,
                "p0": sum(by_priority.get("P0", {}).values()),
                "p1": sum(by_priority.get("P1", {}).values()),
                "p2": sum(by_priority.get("P2", {}).values()),
                "resolved": self.persona_extraction.resolved_findings,
                "deferred": self.persona_extraction.deferred_findings,
                "actionable": len(self.persona_extraction.get_unique_actionable_ids()),
            }

    @property
    def prd_ready_score(self) -> Optional[int]:
        """Get PRD-Ready score from manifest."""
        return self.manifest.prd_ready_score if self.has_manifest else None

    @property
    def required_fixers(self) -> list[str]:
        """Get required fixers (from manifest if present, else persona extraction)."""
        if self.has_manifest:
            return self.manifest.get_required_fixers()
        return self.persona_extraction.required_fixers

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "has_manifest": self.has_manifest,
            "authoritative_counts": self.authoritative_counts,
            "prd_ready_score": self.prd_ready_score,
            "required_fixers": self.required_fixers,
            "manifest": self.manifest.to_dict() if self.has_manifest else None,
            "persona_extraction": self.persona_extraction.to_dict(),
        }


def parse_chairperson_manifest(content: str) -> ManifestResult:
    """
    Parse Chairperson's Remediation Findings Manifest from UCR report.

    Looks for content between <!-- UCX-MANIFEST-START --> and <!-- UCX-MANIFEST-END -->
    markers and extracts:
    - Summary counts table
    - Fixer assignment table
    - Findings table
    - PRD-Ready score

    Args:
        content: Full UCR report content

    Returns:
        ManifestResult with extracted data, or empty result if no manifest found
    """
    result = ManifestResult()

    # Look for manifest markers
    manifest_match = re.search(
        r"<!--\s*UCX-MANIFEST-START\s*-->(.*?)<!--\s*UCX-MANIFEST-END\s*-->",
        content,
        re.DOTALL | re.IGNORECASE
    )

    if not manifest_match:
        return result

    result.has_manifest = True
    manifest_content = manifest_match.group(1)

    # Extract summary counts table
    # | Total Unique Findings | [N] |
    summary_patterns = {
        "total_findings": r"Total Unique Findings\s*\|\s*(\d+)",
        "p0_count": r"P0.*?Critical.*?\|\s*(\d+)",
        "p1_count": r"P1.*?High.*?\|\s*(\d+)",
        "p2_count": r"P2.*?Medium.*?\|\s*(\d+)",
        "resolved_count": r"Resolved\s*\|\s*(\d+)",
        "deferred_count": r"Deferred\s*\|\s*(\d+)",
        "actionable_count": r"Actionable\s*\|\s*(\d+)",
    }

    for attr, pattern in summary_patterns.items():
        match = re.search(pattern, manifest_content, re.IGNORECASE)
        if match:
            setattr(result, attr, int(match.group(1)))

    # Extract fixer assignments table
    # | architect | [N] | REM-xxx, ... |
    fixer_pattern = r"\|\s*(architect|auditor|integration_lead|qa_lead|operator)\s*\|\s*(\d+)\s*\|\s*([^|]+)\|"
    for match in re.finditer(fixer_pattern, manifest_content, re.IGNORECASE):
        fixer = match.group(1).lower()
        finding_ids_str = match.group(3).strip()
        finding_ids = [f.strip() for f in finding_ids_str.split(",") if f.strip()]
        if finding_ids:
            result.findings_by_fixer[fixer] = finding_ids

    # Extract findings table
    # | REM-P0-001 | P0 | OPEN | architect | file.md | Section 6.1 | Description |
    findings_pattern = r"\|\s*(REM-P[012]-\d+)\s*\|\s*(P[012])\s*\|\s*(OPEN|RESOLVED|DEFERRED)\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]+)\|"
    for match in re.finditer(findings_pattern, manifest_content, re.IGNORECASE):
        fixer = match.group(4).strip() or None
        if fixer == "-":
            fixer = None

        target_file = match.group(5).strip() or None
        if target_file == "-":
            target_file = None

        target_section = match.group(6).strip() or None
        if target_section == "-":
            target_section = None

        result.findings.append(ManifestFinding(
            id=match.group(1).strip(),
            priority=match.group(2).strip().upper(),
            status=match.group(3).strip().upper(),
            fixer=fixer.lower() if fixer else None,
            target_file=target_file,
            target_section=target_section,
            description=match.group(7).strip(),
        ))

    # Extract PRD-Ready score from Chairperson section
    # **Final Score**: 82/100
    score_match = re.search(r"Final Score[:\s*]*(\d+)/100", content, re.IGNORECASE)
    if score_match:
        result.prd_ready_score = int(score_match.group(1))

    # Extract recommendation
    rec_match = re.search(
        r"Final Recommendation[:\s*]*(PROCEED|REMEDIATION REQUIRED|FUNDAMENTAL REDESIGN)",
        content,
        re.IGNORECASE
    )
    if rec_match:
        result.recommendation = rec_match.group(1).upper()

    return result


def scan_ucr_report(report_path: Path) -> ScanResult:
    """
    Unified UCR report scanner.

    Performs both manifest extraction (authoritative) and persona extraction
    (for fixer routing / backward compatibility).

    Args:
        report_path: Path to UCR review report

    Returns:
        ScanResult with both manifest and persona extraction data
    """
    content = report_path.read_text(encoding="utf-8")

    result = ScanResult()

    # Try manifest extraction first (authoritative)
    result.manifest = parse_chairperson_manifest(content)

    # Always do persona extraction for fixer routing
    result.persona_extraction = analyze_ucr_report(report_path)

    return result
