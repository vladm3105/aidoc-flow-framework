"""Drift cache model for tracking upstream changes."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from datetime import datetime
import json
import hashlib


@dataclass
class UpstreamDocument:
    """Tracked upstream document."""

    hash: str
    last_checked: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hash": self.hash,
            "last_checked": self.last_checked.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UpstreamDocument":
        """Create from dictionary."""
        return cls(
            hash=data["hash"],
            last_checked=datetime.fromisoformat(data["last_checked"]),
        )


@dataclass
class ReviewEntry:
    """Entry in review history."""

    date: datetime
    score: int
    drift_detected: bool
    status: str
    report_version: str = "v001"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "date": self.date.isoformat(),
            "score": self.score,
            "drift_detected": self.drift_detected,
            "status": self.status,
            "report_version": self.report_version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReviewEntry":
        """Create from dictionary."""
        return cls(
            date=datetime.fromisoformat(data["date"]),
            score=data["score"],
            drift_detected=data["drift_detected"],
            status=data["status"],
            report_version=data.get("report_version", "v001"),
        )


@dataclass
class DriftCache:
    """Drift detection cache for tracking upstream changes."""

    schema_version: str = "1.1"
    document_id: str = ""
    document_version: str = "1.0"
    upstream_mode: str = "none"
    drift_detection_skipped: bool = False
    skip_reason: str = ""
    last_reviewed: datetime = field(default_factory=datetime.now)
    reviewer_version: str = "UCX-2.0"
    upstream_documents: dict[str, UpstreamDocument] = field(default_factory=dict)
    review_history: list[ReviewEntry] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "DriftCache":
        """
        Load drift cache from JSON file.

        Args:
            path: Path to .drift_cache.json file

        Returns:
            DriftCache instance
        """
        if not path.exists():
            return cls()

        data = json.loads(path.read_text(encoding="utf-8"))

        upstream_docs = {}
        for name, doc_data in data.get("upstream_documents", {}).items():
            upstream_docs[name] = UpstreamDocument.from_dict(doc_data)

        review_history = []
        for entry_data in data.get("review_history", []):
            review_history.append(ReviewEntry.from_dict(entry_data))

        return cls(
            schema_version=data.get("schema_version", "1.1"),
            document_id=data.get("document_id", ""),
            document_version=data.get("document_version", "1.0"),
            upstream_mode=data.get("upstream_mode", "none"),
            drift_detection_skipped=data.get("drift_detection_skipped", False),
            skip_reason=data.get("skip_reason", ""),
            last_reviewed=datetime.fromisoformat(data["last_reviewed"]) if "last_reviewed" in data else datetime.now(),
            reviewer_version=data.get("reviewer_version", "UCX-2.0"),
            upstream_documents=upstream_docs,
            review_history=review_history,
        )

    def save(self, path: Path) -> None:
        """
        Save drift cache to JSON file.

        Args:
            path: Path to save .drift_cache.json
        """
        data = {
            "schema_version": self.schema_version,
            "document_id": self.document_id,
            "document_version": self.document_version,
            "upstream_mode": self.upstream_mode,
            "drift_detection_skipped": self.drift_detection_skipped,
            "skip_reason": self.skip_reason,
            "last_reviewed": self.last_reviewed.isoformat(),
            "reviewer_version": self.reviewer_version,
            "upstream_documents": {
                name: doc.to_dict()
                for name, doc in self.upstream_documents.items()
            },
            "review_history": [entry.to_dict() for entry in self.review_history],
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def add_review(
        self,
        score: int,
        status: str,
        drift_detected: bool = False,
        report_version: str = "v001",
    ) -> None:
        """
        Add review entry to history.

        Args:
            score: Review score (0-100)
            status: Review status (PASS, FAIL, etc.)
            drift_detected: Whether drift was detected
            report_version: Version of the report
        """
        self.last_reviewed = datetime.now()
        self.review_history.append(
            ReviewEntry(
                date=self.last_reviewed,
                score=score,
                drift_detected=drift_detected,
                status=status,
                report_version=report_version,
            )
        )

    def track_upstream(self, path: Path) -> None:
        """
        Track an upstream document.

        Args:
            path: Path to upstream document
        """
        if not path.exists():
            return

        content = path.read_bytes()
        hash_value = f"sha256:{hashlib.sha256(content).hexdigest()}"

        self.upstream_documents[path.name] = UpstreamDocument(
            hash=hash_value,
            last_checked=datetime.now(),
        )
        self.upstream_mode = "ref"

    def check_drift(self, upstream_path: Path) -> tuple[bool, list[str]]:
        """
        Check if upstream has changed.

        Args:
            upstream_path: Path to upstream file or directory

        Returns:
            Tuple of (drift_detected, list of changed files)
        """
        if self.upstream_mode == "none" or not upstream_path.exists():
            return False, []

        changed_files = []

        if upstream_path.is_dir():
            for file_path in upstream_path.glob("*"):
                if file_path.is_file():
                    if self._check_file_drift(file_path):
                        changed_files.append(file_path.name)
        else:
            if self._check_file_drift(upstream_path):
                changed_files.append(upstream_path.name)

        return len(changed_files) > 0, changed_files

    def _check_file_drift(self, path: Path) -> bool:
        """Check if a single file has drifted."""
        if path.name not in self.upstream_documents:
            return True  # New file = drift

        content = path.read_bytes()
        current_hash = f"sha256:{hashlib.sha256(content).hexdigest()}"
        cached_hash = self.upstream_documents[path.name].hash

        return current_hash != cached_hash

    @property
    def latest_review(self) -> Optional[ReviewEntry]:
        """Get the most recent review entry."""
        if not self.review_history:
            return None
        return self.review_history[-1]

    @property
    def latest_score(self) -> int:
        """Get the most recent review score."""
        latest = self.latest_review
        return latest.score if latest else 0
