"""Review memory management for persona prompts mode (per-persona reviews)."""

import hashlib
import json
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from ucx.utils.logging import get_logger
from ucx.version import __version__

# Scoring imports (Phase 8 integration)
from ucx.scoring.calculator import Finding, ScoringCalculator, ScoringResult
from ucx.scoring.categories import get_category_by_name
from ucx.scoring.conflicts import CategoryConflictResolver


# Finding similarity threshold (0.0-1.0)
FINDING_SIMILARITY_THRESHOLD = 0.6


# Canonical Finding ID pattern: PREFIX-P0-NNN (e.g., ARCH-P0-001, TL-P1-002)
# This is the ONLY supported format - no legacy patterns needed
FINDING_ID_PATTERN = re.compile(
    r'(?:'
    r'\|\s*\*?\*?([A-Z]{2,4}-P[012]-\d{1,3})\*?\*?\s*\|'  # Table: | ARCH-P0-001 |
    r'|'
    r'\*\*([A-Z]{2,4}-P[012]-\d{1,3})\*\*'  # Bold: **TL-P0-001**
    r'|'
    r'(?:^|\n)\s*([A-Z]{2,4}-P[012]-\d{1,3})[:\s]'  # Line start: AUD-P0-001:
    r')',
    re.MULTILINE
)


def _parse_finding_id(raw_id: str) -> tuple[str, str, str]:
    """Parse finding ID into (prefix, priority, number).

    Args:
        raw_id: Finding ID string like "ARCH-P0-001"

    Returns:
        Tuple of (prefix, priority, number) e.g. ("ARCH", "P0", "001")
    """
    parts = raw_id.split('-')
    if len(parts) >= 3:
        return (parts[0], parts[1], parts[2])
    return (raw_id, "P0", "000")  # Fallback for malformed IDs


# Phase 6.9: VERIFY tag pattern for appendix on-demand verification
VERIFY_TAG_PATTERN = re.compile(r'\[VERIFY:\s*([A-Za-z0-9\-_.]+)\]')

# Patterns indicating claim of missing content (for VERIFY tag enforcement)
MISSING_CLAIM_PATTERNS = re.compile(
    r'(missing|absent|not specified|not defined|lacks|no .* specified|undefined)',
    re.IGNORECASE
)


# Default session TTL in hours
DEFAULT_SESSION_TTL_HOURS = 24


@dataclass
class PersonaResult:
    """Result from a single persona review."""

    persona: str
    prompt_file: Path
    response_file: Path
    prompt_tokens: int = 0
    response_tokens: int = 0
    duration_ms: float = 0
    completed_at: Optional[str] = None

    @property
    def is_complete(self) -> bool:
        return self.response_file.exists() and self.response_file.stat().st_size > 0


@dataclass
class ReviewSession:
    """Metadata for a review session."""

    doc_path: str
    doc_type: str
    started_at: str
    content_hash: str
    personas: list[str] = field(default_factory=list)
    completed_personas: list[str] = field(default_factory=list)
    status: str = "in_progress"  # in_progress, completed, failed
    last_updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "doc_path": self.doc_path,
            "doc_type": self.doc_type,
            "started_at": self.started_at,
            "content_hash": self.content_hash,
            "personas": self.personas,
            "completed_personas": self.completed_personas,
            "status": self.status,
            "last_updated_at": self.last_updated_at or self.started_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReviewSession":
        # Handle missing last_updated_at for older sessions
        if "last_updated_at" not in data:
            data["last_updated_at"] = data.get("started_at")
        return cls(**data)

    def is_expired(self, ttl_hours: int = DEFAULT_SESSION_TTL_HOURS) -> bool:
        """Check if session has expired based on TTL."""
        try:
            last_update = datetime.fromisoformat(self.last_updated_at or self.started_at)
            age = datetime.now() - last_update
            return age > timedelta(hours=ttl_hours)
        except (ValueError, TypeError):
            return True  # Invalid timestamp = expired

    def get_age_str(self) -> str:
        """Get human-readable session age."""
        try:
            started = datetime.fromisoformat(self.started_at)
            age = datetime.now() - started
            if age.days > 0:
                return f"{age.days}d {age.seconds // 3600}h ago"
            elif age.seconds >= 3600:
                return f"{age.seconds // 3600}h {(age.seconds % 3600) // 60}m ago"
            else:
                return f"{age.seconds // 60}m ago"
        except (ValueError, TypeError):
            return "unknown"


# ============================================================================
# Phase 6.9: Appendix Verifier
# ============================================================================

@dataclass
class VerificationResult:
    """Result of verifying a finding against appendix content."""
    finding_id: str
    appendix_id: str
    verification_status: str  # "FOUND", "NOT_FOUND", "PARTIAL"
    matched_content: str = ""  # Snippet of matching content
    confidence: float = 0.0


class AppendixVerifier:
    """Verify findings against appendix content (Phase 6.9).

    Post-processing phase that validates findings with [VERIFY: appendix-id] tags
    against actual appendix content.
    """

    def __init__(self, doc_sections: dict[str, str]):
        self._sections = doc_sections
        self._logger = get_logger(__name__)

    def verify_findings(
        self,
        findings: list[dict],
        warn_on_missing_tag: bool = True,
    ) -> list[dict]:
        """Verify findings and update with verification status.

        Args:
            findings: List of finding dicts with 'id', 'description', etc.
            warn_on_missing_tag: Log warning if "missing" claim lacks VERIFY tag

        Returns:
            Findings with added 'verification_status' and 'verification_note' fields
        """
        verified_findings = []

        for finding in findings:
            finding_copy = finding.copy()
            description = finding.get("description", "") + finding.get("gap", "")

            # Check for VERIFY tags
            verify_matches = VERIFY_TAG_PATTERN.findall(description)

            if verify_matches:
                # Verify against appendix
                for appendix_id in verify_matches:
                    result = self._verify_against_appendix(
                        finding_id=finding.get("id", ""),
                        description=description,
                        appendix_id=appendix_id,
                    )
                    finding_copy["verification_status"] = result.verification_status
                    finding_copy["verification_note"] = result.matched_content[:200] if result.matched_content else ""
                    finding_copy["verified_appendix"] = appendix_id

            elif warn_on_missing_tag:
                # Check if finding claims something is "missing" without VERIFY tag
                if MISSING_CLAIM_PATTERNS.search(description):
                    self._logger.warning(
                        f"Finding {finding.get('id', 'N/A')} claims content is missing "
                        f"but lacks [VERIFY: appendix-id] tag. Consider adding verification."
                    )
                    finding_copy["verification_note"] = "WARN: Missing content claim without VERIFY tag"

            verified_findings.append(finding_copy)

        return verified_findings

    def _verify_against_appendix(
        self,
        finding_id: str,
        description: str,
        appendix_id: str,
    ) -> VerificationResult:
        """Verify a finding against specific appendix content."""
        if appendix_id not in self._sections:
            return VerificationResult(
                finding_id=finding_id,
                appendix_id=appendix_id,
                verification_status="NOT_FOUND",
                matched_content=f"Appendix {appendix_id} not found in document",
            )

        appendix_content = self._sections[appendix_id].lower()

        # Extract key terms from finding description
        key_terms = self._extract_key_terms(description)

        # Check how many key terms appear in appendix
        matches = sum(1 for term in key_terms if term in appendix_content)
        match_ratio = matches / len(key_terms) if key_terms else 0

        if match_ratio >= 0.6:
            status = "FOUND"
            # Extract matching snippet
            matched = self._extract_matching_snippet(
                self._sections[appendix_id], key_terms
            )
        elif match_ratio >= 0.3:
            status = "PARTIAL"
            matched = f"Partial match ({matches}/{len(key_terms)} terms found)"
        else:
            status = "NOT_FOUND"
            matched = f"Content not found in {appendix_id}"

        return VerificationResult(
            finding_id=finding_id,
            appendix_id=appendix_id,
            verification_status=status,
            matched_content=matched,
            confidence=match_ratio,
        )

    def _extract_key_terms(self, text: str, max_terms: int = 10) -> list[str]:
        """Extract key terms from finding description for verification."""
        # Remove common words and extract meaningful terms
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "to", "of", "in", "for", "on", "with", "at",
            "by", "from", "or", "and", "not", "no", "but", "if", "then",
            "this", "that", "these", "those", "it", "its", "as", "such",
        }

        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        key_terms = [w for w in words if w not in stop_words]

        # Deduplicate and limit
        seen = set()
        unique = []
        for term in key_terms:
            if term not in seen:
                seen.add(term)
                unique.append(term)

        return unique[:max_terms]

    def _extract_matching_snippet(
        self,
        content: str,
        key_terms: list[str],
        snippet_size: int = 200,
    ) -> str:
        """Extract snippet from content containing key terms."""
        content_lower = content.lower()

        # Find first matching term
        for term in key_terms:
            pos = content_lower.find(term)
            if pos >= 0:
                start = max(0, pos - snippet_size // 2)
                end = min(len(content), pos + snippet_size // 2)
                snippet = content[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet = snippet + "..."
                return snippet

        return ""


class ReviewMemory:
    """
    Manages review memory for multi-turn persona reviews.

    Stores prompts, responses, and session state in .ucx_review_session/
    directory within the document folder.
    
    Features:
    - Per-persona prompt/response storage
    - Resume capability (skip completed personas)
    - Content hash for cache invalidation
    - Session metadata tracking
    
    Example:
        >>> memory = ReviewMemory(doc_path, doc_type="brd")
        >>> memory.save_shared_context(document_content)
        >>> 
        >>> for persona in personas:
        >>>     if memory.is_persona_complete(persona):
        >>>         continue  # Resume - skip completed
        >>>     memory.save_prompt(persona, prompt)
        >>>     response = ai_client.generate(prompt)
        >>>     memory.save_response(persona, response)
        >>> 
        >>> final_report = memory.assemble_report()
    """
    
    MEMORY_DIR_NAME = ".ucx_review_session"
    
    def __init__(self, doc_path: Path, doc_type: str = "brd"):
        """
        Initialize review memory.
        
        Args:
            doc_path: Path to document file or directory
            doc_type: Document type (brd, prd, etc.)
        """
        self.doc_path = Path(doc_path)
        self.doc_type = doc_type
        self.logger = get_logger("ucx.core.review_memory")
        
        # Set memory directory
        if self.doc_path.is_dir():
            self.memory_dir = self.doc_path / self.MEMORY_DIR_NAME
        else:
            self.memory_dir = self.doc_path.parent / self.MEMORY_DIR_NAME
        
        self.session_file = self.memory_dir / "session.json"
        self.shared_context_file = self.memory_dir / "shared_context.txt"
        self.assembled_report_file = self.memory_dir / "assembled_report.md"
        
        self._session: Optional[ReviewSession] = None
        
        self.logger.debug(f"ReviewMemory initialized: {self.memory_dir}")
    
    def initialize(
        self,
        personas: list[str],
        content_hash: str,
        clear: bool = False,
        session_ttl_hours: int = DEFAULT_SESSION_TTL_HOURS,
    ) -> bool:
        """
        Initialize or resume a review session.

        Args:
            personas: List of persona names to review
            content_hash: Hash of document content for cache validation
            clear: If True, clear any existing memory before starting
            session_ttl_hours: Session time-to-live in hours (default: 24)

        Returns:
            True if resuming existing session, False if new session
        """
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Clear memory if requested
        if clear:
            self.logger.info("Clearing existing memory (fresh start)")
            self._clear_memory()

        # Check for existing session
        if self.session_file.exists():
            try:
                existing = self._load_session()

                # Check if session expired
                if existing.is_expired(session_ttl_hours):
                    self.logger.info(
                        f"Session expired (started {existing.get_age_str()}, TTL={session_ttl_hours}h) - starting fresh"
                    )
                    self._clear_memory()
                # Check if content changed
                elif existing.content_hash != content_hash:
                    self.logger.info("Document content changed - starting fresh session")
                    self._clear_memory()
                # Valid session - resume
                else:
                    self._session = existing
                    completed = len(existing.completed_personas)
                    total = len(existing.personas)
                    pending = total - completed
                    self.logger.info(
                        f"Resuming session (started {existing.get_age_str()}): "
                        f"{completed}/{total} complete, {pending} pending"
                    )
                    return True
            except Exception as e:
                self.logger.warning(f"Failed to load session: {e} - starting fresh")
                self._clear_memory()
        
        # Create new session
        self._session = ReviewSession(
            doc_path=str(self.doc_path),
            doc_type=self.doc_type,
            started_at=datetime.now().isoformat(),
            content_hash=content_hash,
            personas=personas,
            completed_personas=[],
            status="in_progress",
        )
        self._save_session()
        self.logger.info(f"Created new session with {len(personas)} personas")
        return False
    
    def save_shared_context(self, content: str) -> Path:
        """
        Save shared document context.
        
        Args:
            content: Document content to share across personas
        
        Returns:
            Path to saved context file
        """
        self.shared_context_file.write_text(content, encoding="utf-8")
        self.logger.debug(f"Saved shared context: {len(content)} chars")
        return self.shared_context_file
    
    def get_shared_context(self) -> Optional[str]:
        """Get shared context if exists."""
        if self.shared_context_file.exists():
            return self.shared_context_file.read_text(encoding="utf-8")
        return None
    
    def get_prompt_path(self, persona: str) -> Path:
        """Get path for persona prompt file."""
        return self.memory_dir / f"prompt_{persona}.txt"
    
    def get_response_path(self, persona: str) -> Path:
        """Get path for persona response file."""
        return self.memory_dir / f"response_{persona}.txt"
    
    def save_prompt(self, persona: str, prompt: str) -> Path:
        """
        Save prompt for a persona.
        
        Args:
            persona: Persona name
            prompt: Full prompt content
        
        Returns:
            Path to saved prompt file
        """
        path = self.get_prompt_path(persona)
        path.write_text(prompt, encoding="utf-8")
        self.logger.debug(f"Saved prompt for {persona}: {len(prompt)} chars")
        return path
    
    def save_response(
        self,
        persona: str,
        response: str,
        duration_ms: float = 0,
        tokens: int = 0,
    ) -> Path:
        """
        Save response for a persona and mark as complete.

        Args:
            persona: Persona name
            response: Response content
            duration_ms: Time taken in milliseconds
            tokens: Response token count

        Returns:
            Path to saved response file
        """
        path = self.get_response_path(persona)
        path.write_text(response, encoding="utf-8")

        # Validate chairperson response format
        self._validate_chairperson_response(persona, response)

        # Update session
        if self._session and persona not in self._session.completed_personas:
            self._session.completed_personas.append(persona)
            self._session.last_updated_at = datetime.now().isoformat()
            self._save_session()

        self.logger.debug(
            f"Saved response for {persona}: {len(response)} chars, {duration_ms:.0f}ms"
        )
        return path

    def _validate_chairperson_response(self, persona: str, response: str) -> None:
        """Validate Chairperson output contains required manifest markers.

        Args:
            persona: Persona name
            response: Response content

        Logs warning if manifest markers are missing.
        """
        if persona != "chairperson":
            return

        if "<!-- UCX-MANIFEST-START -->" not in response:
            self.logger.warning(
                "Chairperson response missing UCX-MANIFEST-START marker. "
                "Automated remediation routing will use persona extraction fallback."
            )

        if "<!-- UCX-MANIFEST-END -->" not in response:
            self.logger.warning(
                "Chairperson response missing UCX-MANIFEST-END marker. "
                "Manifest parsing may be incomplete."
            )
    
    def get_response(self, persona: str) -> Optional[str]:
        """Get cached response for a persona if exists."""
        path = self.get_response_path(persona)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None
    
    def is_persona_complete(self, persona: str) -> bool:
        """Check if persona review is complete."""
        if self._session and persona in self._session.completed_personas:
            return self.get_response_path(persona).exists()
        return False
    
    def get_completed_personas(self) -> list[str]:
        """Get list of completed persona names."""
        if self._session:
            return self._session.completed_personas.copy()
        return []
    
    def get_pending_personas(self) -> list[str]:
        """Get list of pending persona names."""
        if self._session:
            return [p for p in self._session.personas if p not in self._session.completed_personas]
        return []
    
    def get_all_responses(self) -> dict[str, str]:
        """Get all completed persona responses."""
        responses = {}
        if self._session:
            for persona in self._session.completed_personas:
                response = self.get_response(persona)
                if response:
                    responses[persona] = response
        return responses
    
    def assemble_report(
        self,
        include_header: bool = True,
        review_id: str = "",
        version: int = 1,
    ) -> str:
        """
        Assemble final report from all persona responses.

        Args:
            include_header: Include report header with metadata
            review_id: Review ID for tracking (e.g., UCR-BRD-01-v001)
            version: Report version number

        Returns:
            Combined report content with SDD-compliant format
        """
        parts = []

        # Get all responses first
        responses = self.get_all_responses()

        # Extract findings and calculate scoring BEFORE generating frontmatter
        findings = self._extract_findings(responses)
        dedup_result = self._deduplicate_findings(findings)
        scoring_result = self.calculate_weighted_score(findings)

        if include_header and self._session:
            # SDD-compliant YAML frontmatter
            review_date = self._session.started_at[:19]
            doc_type_upper = self.doc_type.upper()
            layer = self._get_layer_for_doc_type()
            downstream = self._get_downstream_for_doc_type()
            persona_count = len(self._session.completed_personas)

            # Use actual weighted score in frontmatter
            weighted_score = scoring_result.weighted_score

            parts.append("---\n")
            parts.append(f'title: "UCR Review Report: {doc_type_upper}"\n')
            parts.append("tags:\n")
            parts.append("  - ucr-review\n")
            parts.append(f"  - {self.doc_type}-review\n")
            parts.append(f"  - layer-{layer}-artifact\n")
            parts.append("  - quality-assurance\n")
            parts.append("custom_fields:\n")
            parts.append("  document_type: ucr-review-report\n")
            parts.append(f"  source_artifact_type: {doc_type_upper}\n")
            parts.append(f'  review_id: "{review_id or f"UCR-{doc_type_upper}-v{version:03d}"}"\n')
            parts.append(f"  layer: {layer}\n")
            parts.append("  review_method: unified-context-review\n")
            parts.append("  scoring_method: category-weighted-v1.12.0\n")
            parts.append(f"  personas_applied: {persona_count}\n")
            parts.append(f"  weighted_score: {weighted_score:.1f}\n")
            parts.append(f"  p0_findings: {scoring_result.total_p0}\n")
            parts.append(f"  p1_findings: {scoring_result.total_p1}\n")
            parts.append(f"  p2_findings: {scoring_result.total_p2}\n")
            parts.append(f'  last_updated: "{review_date}"\n')
            parts.append("---\n\n")

            # Title and Document Control
            parts.append(f"# UCR Review Report: {doc_type_upper}\n\n")
            parts.append("## 0. Document Control\n\n")
            parts.append("| Item | Details |\n")
            parts.append("|------|--------|\n")
            parts.append(f"| **Source Document** | {self._session.doc_path} |\n")
            parts.append(f'| **Review ID** | {review_id or f"UCR-{doc_type_upper}-v{version:03d}"} |\n')
            parts.append(f"| **Review Date** | {review_date} |\n")
            parts.append("| **Review Method** | UCR (Unified Context Review) - Multi-Turn |\n")
            parts.append(f"| **Weighted Score** | {weighted_score:.1f}/100 |\n")
            parts.append(f"| **Personas Applied** | {persona_count} |\n")
            parts.append(f"| **Reviewer** | UCX Framework v{__version__} |\n")
            parts.append("| **Status** | Draft |\n\n")
            parts.append("---\n\n")

        # Add scoring summary section first
        parts.append(self._format_scoring_summary(scoring_result, dedup_result["stats"]))
        parts.append("---\n\n")

        # Add consolidated findings section (if we have findings)
        if dedup_result["stats"].get("total_findings", 0) > 0:
            parts.append(self._format_consolidated_findings(dedup_result))
            parts.append("---\n\n")

        # Add individual persona reviews
        for i, persona in enumerate(self._session.personas if self._session else []):
            if persona in responses:
                title = persona.replace("_", " ").title()
                parts.append(f"## {i + 1}. {title} Review\n\n")
                parts.append(responses[persona])
                parts.append("\n\n---\n\n")

        content = "".join(parts)

        # Save to assembled_report.md
        self.assembled_report_file.write_text(content, encoding="utf-8")
        self.logger.info(f"Assembled report: {len(content)} chars from {len(responses)} personas")

        return content

    def _get_layer_for_doc_type(self) -> int:
        """Get SDD layer number for document type."""
        layers = {
            "brd": 1, "prd": 2, "ears": 3, "bdd": 4, "adr": 5,
            "sys": 6, "req": 7, "ctr": 8, "spec": 9, "tspec": 10,
        }
        return layers.get(self.doc_type.lower(), 0)

    def _get_downstream_for_doc_type(self) -> str:
        """Get downstream artifact ready score name."""
        downstream = {
            "brd": "prd", "prd": "ears", "ears": "bdd", "bdd": "adr",
            "adr": "sys", "sys": "req", "req": "ctr", "ctr": "spec",
            "spec": "tspec", "tspec": "code",
        }
        return downstream.get(self.doc_type.lower(), "downstream")
    
    def mark_complete(self) -> None:
        """Mark the review session as complete."""
        if self._session:
            self._session.status = "completed"
            self._save_session()
            self.logger.info("Review session marked complete")
    
    def mark_failed(self, error: str = "") -> None:
        """Mark the review session as failed."""
        if self._session:
            self._session.status = f"failed: {error}" if error else "failed"
            self._save_session()
            self.logger.warning(f"Review session marked failed: {error}")
    
    def _save_session(self) -> None:
        """Save session metadata to disk."""
        if self._session:
            self.session_file.write_text(
                json.dumps(self._session.to_dict(), indent=2),
                encoding="utf-8",
            )
    
    def _load_session(self) -> ReviewSession:
        """Load session metadata from disk."""
        data = json.loads(self.session_file.read_text(encoding="utf-8"))
        return ReviewSession.from_dict(data)
    
    def _clear_memory(self) -> None:
        """Clear all memory files (for fresh start)."""
        if self.memory_dir.exists():
            for f in self.memory_dir.iterdir():
                if f.is_file():
                    f.unlink()
            self.logger.debug("Cleared memory directory")
    
    @staticmethod
    def compute_content_hash(content: str) -> str:
        """Compute hash of content for cache validation."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    def _extract_findings(self, responses: dict[str, str]) -> list[dict]:
        """
        Extract findings from all persona responses.

        Returns list of dicts with keys: persona, priority, id, prefix, title, text, category
        Category is extracted from [CAT:xxx] tag or assigned via CategoryAssigner fallback.

        Supports canonical Finding ID format: PREFIX-P0-NNN (e.g., ARCH-P0-001)
        """
        findings = []
        seen_ids = set()  # Deduplication

        # Pattern to extract category tag: [CAT:xxx]
        category_pattern = re.compile(r'\[CAT:(\w+)\]', re.IGNORECASE)

        # Initialize category conflict resolver for fallback
        resolver = CategoryConflictResolver()

        for persona, response in responses.items():
            for match in FINDING_ID_PATTERN.finditer(response):
                # Extract finding ID from whichever group matched
                raw_id = match.group(1) or match.group(2) or match.group(3)
                if not raw_id or raw_id in seen_ids:
                    continue

                seen_ids.add(raw_id)
                prefix, priority, num = _parse_finding_id(raw_id)

                # Extract context around the finding (200 chars before, 500 after)
                start = max(0, match.start() - 200)
                end = min(len(response), match.end() + 500)
                context = response[start:end]

                # Try to extract explicit category tag
                cat_match = category_pattern.search(context)
                explicit_tag = cat_match.group(1).lower() if cat_match else None

                # Use CategoryConflictResolver for category assignment
                resolution = resolver.resolve(
                    finding_id=raw_id,
                    finding_text=context,
                    persona=persona,
                    explicit_tag=explicit_tag,
                )
                category = resolution.resolved_category.value

                # Extract title from context
                title = self._extract_title(context, raw_id)

                findings.append({
                    "persona": persona,
                    "priority": priority,
                    "id": raw_id,
                    "prefix": prefix,
                    "title": title,
                    "text": context[:500],  # Truncate for comparison
                    "full_text": context,
                    "category": category,
                })

        return findings

    def _extract_title(self, context: str, finding_id: str) -> str:
        """Extract finding title from context around finding ID.

        Args:
            context: Text around the finding ID
            finding_id: The finding ID (e.g., ARCH-P0-001)

        Returns:
            Extracted title string (max 100 chars)
        """
        # Try table format: | FINDING_ID | Title |
        table_pattern = rf'\|\s*\*?\*?{re.escape(finding_id)}\*?\*?\s*\|\s*([^|]+)'
        match = re.search(table_pattern, context)
        if match:
            return match.group(1).strip()[:100]

        # Try inline format: FINDING_ID: Title or FINDING_ID - Title
        inline_pattern = rf'{re.escape(finding_id)}[:\s-]+([^\n|]+)'
        match = re.search(inline_pattern, context)
        if match:
            return match.group(1).strip()[:100]

        return "Untitled finding"

    def calculate_weighted_score(
        self,
        findings: list[dict],
    ) -> ScoringResult:
        """
        Calculate weighted score from extracted findings.

        Args:
            findings: List of finding dicts from _extract_findings()

        Returns:
            ScoringResult with weighted score and category breakdown
        """
        # Convert finding dicts to Finding objects
        # Category strings are converted to Category enums
        finding_objects = []
        for f in findings:
            cat_str = f.get("category")
            cat_enum = get_category_by_name(cat_str) if cat_str else None
            finding_objects.append(Finding(
                id=f["id"],
                priority=f["priority"],
                text=f["title"],
                persona=f["persona"],
                category=cat_enum,
            ))

        # Calculate weighted score
        calculator = ScoringCalculator(doc_type=self.doc_type)
        return calculator.calculate(finding_objects)

    def _compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute Jaccard similarity between two texts.

        Returns value between 0.0 (no overlap) and 1.0 (identical).
        """
        # Normalize: lowercase, remove punctuation, split into words
        def normalize(text: str) -> set[str]:
            text = re.sub(r'[^\w\s]', ' ', text.lower())
            words = set(text.split())
            # Filter out common stop words
            stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                          'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                          'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                          'can', 'need', 'to', 'of', 'in', 'for', 'on', 'with', 'at',
                          'by', 'from', 'as', 'into', 'through', 'during', 'before',
                          'after', 'above', 'below', 'between', 'under', 'again',
                          'further', 'then', 'once', 'here', 'there', 'when', 'where',
                          'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other',
                          'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
                          'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if',
                          'or', 'because', 'until', 'while', 'this', 'that', 'these',
                          'those', 'it', 'its'}
            return words - stop_words

        words1 = normalize(text1)
        words2 = normalize(text2)

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _deduplicate_findings(self, findings: list[dict]) -> dict:
        """
        Deduplicate findings across personas.

        Returns dict with:
          - unique: list of unique findings
          - duplicates: list of duplicate groups (findings that overlap)
          - stats: deduplication statistics
        """
        if not findings:
            return {"unique": [], "duplicates": [], "stats": {}}

        # Group findings by priority first
        by_priority = defaultdict(list)
        for f in findings:
            by_priority[f["priority"]].append(f)

        unique_findings = []
        duplicate_groups = []
        processed = set()

        for priority in ["P0", "P1", "P2"]:
            priority_findings = by_priority.get(priority, [])

            for i, finding in enumerate(priority_findings):
                key = (finding["persona"], finding["id"])
                if key in processed:
                    continue

                # Find similar findings from OTHER personas
                similar = [finding]
                for j, other in enumerate(priority_findings):
                    if i == j:
                        continue
                    other_key = (other["persona"], other["id"])
                    if other_key in processed:
                        continue

                    # Skip if same persona (they shouldn't duplicate themselves)
                    if other["persona"] == finding["persona"]:
                        continue

                    # Check title + text similarity
                    title_sim = self._compute_similarity(finding["title"], other["title"])
                    text_sim = self._compute_similarity(finding["text"], other["text"])

                    # Weighted average (title matters more)
                    combined_sim = 0.6 * title_sim + 0.4 * text_sim

                    if combined_sim >= FINDING_SIMILARITY_THRESHOLD:
                        similar.append(other)
                        processed.add(other_key)

                processed.add(key)

                if len(similar) > 1:
                    # Multiple personas found same issue - record as duplicate
                    duplicate_groups.append({
                        "primary": finding,
                        "similar": similar[1:],
                        "personas": [f["persona"] for f in similar],
                    })
                else:
                    unique_findings.append(finding)

        # Compute stats
        total = len(findings)
        unique_count = len(unique_findings) + len(duplicate_groups)
        duplicate_count = sum(len(g["similar"]) for g in duplicate_groups)

        stats = {
            "total_findings": total,
            "unique_findings": unique_count,
            "duplicates_removed": duplicate_count,
            "dedup_ratio": (duplicate_count / total * 100) if total > 0 else 0,
        }

        return {
            "unique": unique_findings,
            "duplicates": duplicate_groups,
            "stats": stats,
        }

    def _format_consolidated_findings(self, dedup_result: dict) -> str:
        """Format deduplicated findings into a consolidated section."""
        parts = []
        parts.append("## Consolidated Findings Summary\n\n")

        stats = dedup_result["stats"]
        parts.append(f"**Deduplication Stats**: {stats['total_findings']} total findings → "
                     f"{stats['unique_findings']} unique ({stats['dedup_ratio']:.0f}% duplicates removed)\n\n")

        # P0 Critical first
        p0_findings = [f for f in dedup_result["unique"] if f["priority"] == "P0"]
        p0_dupes = [g for g in dedup_result["duplicates"] if g["primary"]["priority"] == "P0"]

        if p0_findings or p0_dupes:
            parts.append("### P0 Critical Findings\n\n")
            for f in p0_findings:
                parts.append(f"- **[{f['id']}]** {f['title']} *(from {f['persona']})*\n")
            for g in p0_dupes:
                personas = ", ".join(g["personas"])
                parts.append(f"- **[{g['primary']['id']}]** {g['primary']['title']} "
                             f"*(confirmed by {len(g['personas'])} personas: {personas})*\n")
            parts.append("\n")

        # P1 High
        p1_findings = [f for f in dedup_result["unique"] if f["priority"] == "P1"]
        p1_dupes = [g for g in dedup_result["duplicates"] if g["primary"]["priority"] == "P1"]

        if p1_findings or p1_dupes:
            parts.append("### P1 High Priority Findings\n\n")
            for f in p1_findings:
                parts.append(f"- **[{f['id']}]** {f['title']} *(from {f['persona']})*\n")
            for g in p1_dupes:
                personas = ", ".join(g["personas"])
                parts.append(f"- **[{g['primary']['id']}]** {g['primary']['title']} "
                             f"*(confirmed by {len(g['personas'])} personas: {personas})*\n")
            parts.append("\n")

        # P2 Medium (brief summary)
        p2_count = len([f for f in dedup_result["unique"] if f["priority"] == "P2"])
        p2_count += len([g for g in dedup_result["duplicates"] if g["primary"]["priority"] == "P2"])
        if p2_count > 0:
            parts.append(f"### P2 Medium Priority: {p2_count} findings (see individual reviews)\n\n")

        return "".join(parts)

    def _format_scoring_summary(
        self,
        scoring_result: ScoringResult,
        dedup_stats: dict,
    ) -> str:
        """
        Format weighted scoring summary section.

        Args:
            scoring_result: Result from calculate_weighted_score()
            dedup_stats: Deduplication statistics

        Returns:
            Formatted markdown section with scoring breakdown
        """
        parts = []
        parts.append("## Scoring Summary\n\n")

        # Overall score and status
        score = scoring_result.weighted_score
        status = "PASS" if score >= 85 else ("WARN" if score >= 70 else "FAIL")
        status_icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[status]

        parts.append(f"**Weighted Score**: {score:.1f}/100 {status_icon} ({status})\n\n")
        parts.append(f"**Total Findings**: P0={scoring_result.total_p0}, "
                     f"P1={scoring_result.total_p1}, P2={scoring_result.total_p2}\n\n")

        # Category breakdown table
        parts.append("### Category Breakdown\n\n")
        parts.append("| Category | P0 | P1 | P2 | Raw | Capped | Weighted |\n")
        parts.append("|----------|----:|----:|----:|-----:|-------:|--------:|\n")

        for cat_enum, cat_score in sorted(
            scoring_result.category_scores.items(),
            key=lambda x: x[0].value  # Sort by category name
        ):
            cat_name = cat_enum.value
            raw = cat_score.raw_deduction
            capped = cat_score.capped_deduction
            weighted = cat_score.weighted_deduction
            parts.append(
                f"| {cat_name} | {cat_score.p0_count} | {cat_score.p1_count} | "
                f"{cat_score.p2_count} | -{raw} | -{capped} | -{weighted:.2f} |\n"
            )

        # Total row
        total_raw = sum(cs.raw_deduction for cs in scoring_result.category_scores.values())
        total_capped = sum(cs.capped_deduction for cs in scoring_result.category_scores.values())
        total_weighted = 100.0 - score
        parts.append(
            f"| **Total** | **{scoring_result.total_p0}** | **{scoring_result.total_p1}** | "
            f"**{scoring_result.total_p2}** | **-{total_raw}** | **-{total_capped}** | "
            f"**-{total_weighted:.2f}** |\n"
        )
        parts.append("\n")

        # Downstream readiness
        downstream = self._get_downstream_for_doc_type().upper()
        ready_status = "Ready" if score >= 85 and scoring_result.total_p0 == 0 else "Not Ready"
        parts.append(f"**{downstream}-Ready Status**: {ready_status}\n\n")

        # Scoring method note
        parts.append(f"> *Scoring Method*: Category-Weighted v1.12.0 "
                     f"(weights per {self.doc_type.upper()} document type)\n\n")

        return "".join(parts)
