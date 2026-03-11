"""Review memory management for multi-turn persona reviews."""

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


# Finding similarity threshold (0.0-1.0)
FINDING_SIMILARITY_THRESHOLD = 0.6


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


class ReviewMemory:
    """
    Manages review memory for multi-turn persona reviews.
    
    Stores prompts, responses, and session state in .doc_review_memory/
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
    
    MEMORY_DIR_NAME = ".doc_review_memory"
    
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
        self.final_body_file = self.memory_dir / "final_body.md"
        
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

        # Update session
        if self._session and persona not in self._session.completed_personas:
            self._session.completed_personas.append(persona)
            self._session.last_updated_at = datetime.now().isoformat()
            self._save_session()
        
        self.logger.debug(
            f"Saved response for {persona}: {len(response)} chars, {duration_ms:.0f}ms"
        )
        return path
    
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

        if include_header and self._session:
            # SDD-compliant YAML frontmatter
            review_date = self._session.started_at[:19]
            doc_type_upper = self.doc_type.upper()
            layer = self._get_layer_for_doc_type()
            downstream = self._get_downstream_for_doc_type()
            persona_count = len(self._session.completed_personas)

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
            parts.append(f"  personas_applied: {persona_count}\n")
            parts.append(f'  {downstream}_ready_score: "[PENDING]"\n')
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
            parts.append(f"| **Personas Applied** | {persona_count} |\n")
            parts.append(f"| **Reviewer** | UCX Framework v{__version__} |\n")
            parts.append("| **Status** | Draft |\n\n")
            parts.append("---\n\n")

        # Add each persona's response
        responses = self.get_all_responses()

        # Extract and deduplicate findings
        findings = self._extract_findings(responses)
        dedup_result = self._deduplicate_findings(findings)

        # Add consolidated findings section first (if we have findings)
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

        # Save to final_body.md
        self.final_body_file.write_text(content, encoding="utf-8")
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

        Returns list of dicts with keys: persona, priority, id, title, text
        """
        findings = []
        # Pattern: **[P0-X]** or **[P1-X]** or similar
        pattern = re.compile(
            r'\*\*\[([Pp][0-2])-(\d+)\]\*\*\s*([^\n]+?)(?:\n|$)(.*?)(?=\*\*\[[Pp][0-2]-|\Z)',
            re.DOTALL
        )

        for persona, response in responses.items():
            for match in pattern.finditer(response):
                priority = match.group(1).upper()
                finding_num = match.group(2)
                title = match.group(3).strip().rstrip(':').strip()
                text = match.group(4).strip()

                findings.append({
                    "persona": persona,
                    "priority": priority,
                    "id": f"{priority}-{finding_num}",
                    "title": title,
                    "text": text[:500],  # Truncate for comparison
                    "full_text": text,
                })

        return findings

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
