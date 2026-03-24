"""Fix proposal models."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
import yaml

from ucx.models.enums import Confidence, Priority, FixType


@dataclass
class FixAction:
    """Details of a fix action."""

    position: str = ""  # after, before, replace
    anchor: str = ""    # text to find
    text: str = ""      # text to add/modify
    parent_section: str = ""
    section_number: str = ""
    heading: str = ""
    content: str = ""
    table_anchor: str = ""
    row_data: list[str] = field(default_factory=list)
    old_text: str = ""
    new_text: str = ""
    field_path: str = ""
    value: str = ""
    tag_type: str = ""
    tag_value: str = ""
    location: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding empty fields."""
        return {k: v for k, v in self.__dict__.items() if v}


@dataclass
class FixProposal:
    """A proposed fix from UCRem."""

    fix_id: str
    source_finding: str
    priority: Priority
    confidence: Confidence
    target_file: Path
    target_section: str
    fix_type: FixType
    fix_action: FixAction
    rationale: str = ""
    validated_by: list[str] = field(default_factory=list)
    verification: str = ""

    @property
    def can_auto_apply(self) -> bool:
        """Check if this fix can be auto-applied."""
        return self.confidence == Confidence.AUTO_SAFE

    @property
    def needs_review(self) -> bool:
        """Check if this fix needs manual review."""
        return self.confidence == Confidence.MANUAL_REQUIRED

    def apply(self, dry_run: bool = False) -> bool:
        """
        Apply this fix to the target file.

        Args:
            dry_run: If True, show what would be done without applying

        Returns:
            True if fix was applied successfully
        """
        if not self.target_file.exists():
            return False

        content = self.target_file.read_text(encoding="utf-8")
        new_content = self._apply_fix(content)

        if new_content == content:
            return False  # No change

        if not dry_run:
            self.target_file.write_text(new_content, encoding="utf-8")

        return True

    def _apply_fix(self, content: str) -> str:
        """Apply fix transformation to content."""
        if self.fix_type == FixType.ADD_TEXT:
            return self._apply_add_text(content)
        elif self.fix_type == FixType.MODIFY_TEXT:
            return self._apply_modify_text(content)
        elif self.fix_type == FixType.ADD_SECTION:
            return self._apply_add_section(content)
        # Add more fix types as needed
        return content

    def _apply_add_text(self, content: str) -> str:
        """Apply add_text fix."""
        anchor = self.fix_action.anchor
        text = self.fix_action.text
        position = self.fix_action.position

        if anchor not in content:
            return content

        if position == "after":
            return content.replace(anchor, f"{anchor}\n{text}")
        elif position == "before":
            return content.replace(anchor, f"{text}\n{anchor}")
        elif position == "replace":
            return content.replace(anchor, text)

        return content

    def _apply_modify_text(self, content: str) -> str:
        """Apply modify_text fix."""
        old_text = self.fix_action.old_text
        new_text = self.fix_action.new_text

        if old_text in content:
            return content.replace(old_text, new_text)
        return content

    def _apply_add_section(self, content: str) -> str:
        """Apply add_section fix."""
        # Find parent section and add new section after it
        parent = self.fix_action.parent_section
        heading = self.fix_action.heading
        section_content = self.fix_action.content

        new_section = f"\n### {self.fix_action.section_number} {heading}\n\n{section_content}\n"

        if parent in content:
            # Find end of parent section (next ## or end of file)
            import re
            pattern = rf"(## {re.escape(parent)}.*?)(\n## |\Z)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                insert_pos = match.end(1)
                return content[:insert_pos] + new_section + content[insert_pos:]

        return content

    def to_yaml(self) -> str:
        """Serialize to YAML format."""
        data = {
            "fix_id": self.fix_id,
            "source_finding": self.source_finding,
            "priority": self.priority.value,
            "confidence": self.confidence.value,
            "target_file": str(self.target_file),
            "target_section": self.target_section,
            "fix_type": self.fix_type.value,
            "fix_action": self.fix_action.to_dict(),
            "rationale": self.rationale,
            "validated_by": self.validated_by,
            "verification": self.verification,
        }
        return yaml.dump(data, default_flow_style=False, sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "FixProposal":
        """Parse from YAML string."""
        data = yaml.safe_load(yaml_str)
        return cls(
            fix_id=data["fix_id"],
            source_finding=data["source_finding"],
            priority=Priority(data["priority"]),
            confidence=Confidence(data["confidence"]),
            target_file=Path(data["target_file"]),
            target_section=data["target_section"],
            fix_type=FixType(data["fix_type"]),
            fix_action=FixAction(**data.get("fix_action", {})),
            rationale=data.get("rationale", ""),
            validated_by=data.get("validated_by", []),
            verification=data.get("verification", ""),
        )
