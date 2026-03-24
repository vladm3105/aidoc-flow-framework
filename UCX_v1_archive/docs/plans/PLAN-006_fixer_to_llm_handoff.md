# UCX v1.17.0 - Fixer-to-LLM Hand-off System

## Overview

Implement explicit hand-off between script-based fixers and LLM remediation by extending the existing validation report. When a fixer cannot fully fix an issue or provides a partial fix, it records this in the validation report for remediation personas to consume.

**Key Design Decisions**:
1. **Always Fix**: `ucx validate` always runs fixer (no `--fix` flag needed)
2. **Single Source**: Use validation report as single source of truth (no separate manifest)
3. **Opt-out**: Use `--no-fix` flag to skip fixing if needed

| Component | Purpose | Files |
|-----------|---------|-------|
| **Always-Fix Validation** | Validation always includes fixing | `main.py` |
| **Extended Validation Report** | Add fixer session section with LLM context | `result.py`, `fixer.py` |
| **LLM_COMPLETION Markers** | Mark partial fixes in documents | `fixer.py` |
| **Remediation Integration** | Parse fixer context from validation report | `remediation.py` |
| **Persona Guidelines** | Instruct all 6 fixer personas | `skills/*.md` |

---

## Gaps Addressed

| ID | Gap | Resolution |
|----|-----|------------|
| GAP-002 | Report regeneration loses Section 7 | **ELIMINATED** - validation always fixes, context always fresh |
| GAP-004 | FixerContext data flow missing | Explicit attachment in main.py after fix_all() |
| GAP-010 | result.py has no fixer awareness | Add FixerContext field and _format_fixer_section() |
| GAP-011 | fix_all() return not used | Convert FixSummary to FixerContext in CLI |
| GAP-012 | FixResult missing fields | Add partial_fix, llm_task fields |
| GAP-013 | LLM codes not defined | Add LLM_COMPLETION_CODES, LLM_ONLY_CODES |
| GAP-001 | JSON parsing robustness | Add schema validation |
| GAP-005 | Missing imports | Complete import statements |
| GAP-007 | Multiple runs | Each run fixes and updates context |
| GAP-009 | Marker accumulation | Add deduplication check |
| GAP-014 | JSON error handling | Add logging |
| GAP-016 | Report path for file input | Handle file vs directory |
| GAP-017/18 | Test coverage | Complete test specification |

---

## Phase 1: Extend Validation Report Format

### Goal
Add "Fixer Session Summary" section to the validation report with embedded JSON for machine parsing. Since validation always runs the fixer, Section 7 is always fresh.

### Changes

**File: `/opt/data/docs_flow_framework/UCX/ucx/validators/common/result.py`**

1. Add imports at top of file:
```python
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
```

2. Add `FixerContext` dataclass (~line 50, before ValidationResult):
```python
@dataclass
class FixerContext:
    """Fixer session context for LLM hand-off."""
    schema_version: str = "1.0"
    session_id: str = ""
    timestamp: str = ""
    fixed_count: int = 0
    partial_fix_count: int = 0
    skipped_count: int = 0
    llm_completion: List[dict] = field(default_factory=list)
    llm_only: List[dict] = field(default_factory=list)
    fixer_applied: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> Optional["FixerContext"]:
        """Parse FixerContext from JSON with validation."""
        try:
            data = json.loads(json_str)
            # Schema validation
            required_fields = ["session_id", "timestamp"]
            if not all(f in data for f in required_fields):
                logger.warning("FixerContext JSON missing required fields")
                return None
            return cls(
                schema_version=data.get("schema_version", "1.0"),
                session_id=data.get("session_id", ""),
                timestamp=data.get("timestamp", ""),
                fixed_count=data.get("fixed_count", 0),
                partial_fix_count=data.get("partial_fix_count", 0),
                skipped_count=data.get("skipped_count", 0),
                llm_completion=data.get("llm_completion", []),
                llm_only=data.get("llm_only", []),
                fixer_applied=data.get("fixer_applied", []),
            )
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse FixerContext JSON: {e}")
            return None
```

3. Update `UnifiedValidationResult` dataclass (~line 121):
```python
@dataclass
class UnifiedValidationResult:
    """Unified validation result with optional fixer context."""
    # ... existing fields ...
    tier1_issues: List[ValidationIssue] = field(default_factory=list)
    tier2_issues: List[ValidationIssue] = field(default_factory=list)
    # ... other existing fields ...

    # NEW: Fixer hand-off context
    fixer_context: Optional[FixerContext] = None
```

4. Add `_format_fixer_section()` method (~line 360):
```python
def _format_fixer_section(self) -> str:
    """Format fixer session summary with embedded JSON."""
    ctx = self.fixer_context
    if not ctx:
        return ""

    lines = [
        "---",
        "",
        "## 7. Fixer Session Summary",
        "",
        f"**Session ID**: `{ctx.session_id}`",
        f"**Timestamp**: {ctx.timestamp}",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Fixed (Complete) | {ctx.fixed_count} |",
        f"| Partial (LLM Completion) | {ctx.partial_fix_count} |",
        f"| Skipped | {ctx.skipped_count} |",
        "",
    ]

    # 7.1 LLM Completion items
    if ctx.llm_completion:
        lines.extend([
            "### 7.1 LLM Completion Required",
            "",
            "Script applied partial fixes. LLM should complete these:",
            "",
            "| Code | File | Script Action | LLM Task |",
            "|------|------|---------------|----------|",
        ])
        for item in ctx.llm_completion:
            lines.append(
                f"| `{item['code']}` | `{item['file']}` | "
                f"{item['script_action']} | {item['llm_task']} |"
            )
        lines.append("")

    # 7.2 LLM-only items
    if ctx.llm_only:
        lines.extend([
            "### 7.2 LLM-Only Issues",
            "",
            "These require semantic understanding (no script fix possible):",
            "",
            "| Code | File | Reason |",
            "|------|------|--------|",
        ])
        for item in ctx.llm_only:
            lines.append(f"| `{item['code']}` | `{item['file']}` | {item['reason']} |")
        lines.append("")

    # 7.3 Protected changes
    if ctx.fixer_applied:
        lines.extend([
            "### 7.3 Protected Changes (Do Not Undo)",
            "",
            "Script successfully fixed these. Remediation should NOT modify:",
            "",
        ])
        for item in ctx.fixer_applied[:10]:  # Limit to 10
            changes_preview = ", ".join(item.get('changes', [])[:2])
            lines.append(f"- `{item['code']}` in `{item['file']}`: {changes_preview}")
        if len(ctx.fixer_applied) > 10:
            lines.append(f"- ... and {len(ctx.fixer_applied) - 10} more")
        lines.append("")

    # 7.4 Embedded JSON for machine parsing
    lines.extend([
        "### 7.4 Machine-Readable Context",
        "",
        "<!-- FIXER_CONTEXT_START",
        ctx.to_json(),
        "FIXER_CONTEXT_END -->",
        "",
    ])

    return "\n".join(lines)
```

5. Update `format_report()` to include Section 7 (~line 500):
```python
def format_report(
    self,
    doc_id: str = "",
    doc_type: str = "BRD",
    version: str = "v001",
) -> str:
    """Format validation report with fixer section."""
    # ... existing sections 1-6 generation ...

    report_lines = []
    report_lines.extend(self._format_header(doc_id, doc_type, version))
    report_lines.extend(self._format_sections_1_to_6())

    # Section 7: Fixer Session Summary (always present since we always fix)
    if self.fixer_context:
        report_lines.append(self._format_fixer_section())

    # Footer
    report_lines.append("---")
    report_lines.append("")
    report_lines.append(f"*Generated by UCX Framework v{get_version()}*")

    return "\n".join(report_lines)
```

---

## Phase 2: Fixer Code Classification and Context Building

### Goal
Define which codes get partial fixes (LLM completion) vs full fixes vs LLM-only, and build FixerContext.

### Changes

**File: `/opt/data/docs_flow_framework/UCX/ucx/validators/brd/fixer.py`**

1. Add imports at top:
```python
import json
import uuid
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Set, Optional
from pathlib import Path

from ucx.validators.common.result import ValidationIssue, FixerContext

logger = logging.getLogger(__name__)
```

2. Add `LLM_COMPLETION_CODES` constant after FIXABLE_CODES (~line 100):
```python
# Codes where script provides PARTIAL fix and LLM completes the semantic work
# These are ALSO in FIXABLE_CODES - script does mechanical work, LLM completes
LLM_COMPLETION_CODES: Dict[str, Dict[str, str]] = {
    "GATE-E010": {
        "script_action": "Splits file at section boundaries",
        "llm_task": "Review split points for semantic coherence",
    },
    "BRD-W011": {
        "script_action": "Adds @diagram-request placeholder for C4-L1",
        "llm_task": "Define system context with components and boundaries",
    },
    "BRD-W012": {
        "script_action": "Adds @diagram-request placeholder for sequence",
        "llm_task": "Define interaction flow with participants and messages",
    },
    "DIAG-E001": {
        "script_action": "Adds DIAGRAM-REQUIRED placeholder",
        "llm_task": "Create Mermaid diagram with domain-specific content",
    },
    "FWDREF-E001": {
        "script_action": "Converts to FWDREF-DEFERRED comment",
        "llm_task": "Verify cross-document references when target docs exist",
    },
}

# Codes that are NOT in FIXABLE_CODES - only LLM can handle
LLM_ONLY_CODES: Dict[str, str] = {
    "CONTENT-E001": "Content quality requires semantic review",
    "LOGIC-E001": "Logical consistency requires domain understanding",
    "TRACE-E001": "Traceability gaps require cross-document analysis",
}
```

3. Update `FixResult` dataclass (~line 28):
```python
@dataclass
class FixResult:
    """Result of a fix operation."""
    code: str
    file_path: Path
    fixed: bool
    message: str
    changes: List[str] = field(default_factory=list)
    partial_fix: bool = False  # NEW: Script did partial work
    llm_task: str = ""  # NEW: What LLM should complete

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "file": str(self.file_path),
            "fixed": self.fixed,
            "message": self.message,
            "changes": self.changes,
            "partial_fix": self.partial_fix,
            "llm_task": self.llm_task,
        }
```

4. Update `FixSummary` dataclass (~line 45):
```python
@dataclass
class FixSummary:
    """Summary of all fix operations."""
    total_issues: int = 0
    fixed_count: int = 0
    partial_fix_count: int = 0  # NEW: Partial fixes needing LLM
    skipped_count: int = 0
    failed_count: int = 0
    results: List[FixResult] = field(default_factory=list)

    @property
    def fully_fixed_count(self) -> int:
        """Count of completely fixed issues (no LLM needed)."""
        return self.fixed_count - self.partial_fix_count

    def add(self, result: FixResult) -> None:
        """Add a fix result to the summary."""
        self.results.append(result)
        if result.fixed:
            self.fixed_count += 1
            if result.partial_fix:
                self.partial_fix_count += 1
        else:
            if result.code in FIXABLE_CODES:
                self.failed_count += 1
            else:
                self.skipped_count += 1

    def to_fixer_context(self, doc_path: Path) -> FixerContext:
        """Convert to FixerContext for validation report."""
        ctx = FixerContext(
            session_id=uuid.uuid4().hex[:8],
            timestamp=datetime.now(timezone.utc).isoformat(),
            fixed_count=self.fully_fixed_count,
            partial_fix_count=self.partial_fix_count,
            skipped_count=self.skipped_count,
        )

        for result in self.results:
            item = {
                "code": result.code,
                "file": str(result.file_path.name) if result.file_path else "",
                "message": result.message,
                "changes": result.changes,
            }

            if result.partial_fix and result.code in LLM_COMPLETION_CODES:
                ctx.llm_completion.append({
                    **item,
                    "script_action": LLM_COMPLETION_CODES[result.code]["script_action"],
                    "llm_task": result.llm_task or LLM_COMPLETION_CODES[result.code]["llm_task"],
                })
                # Also track as fixer-applied (protect from undo)
                ctx.fixer_applied.append(item)
            elif result.fixed:
                # Fully fixed - protect from remediation undo
                ctx.fixer_applied.append(item)
            elif result.code in LLM_ONLY_CODES:
                # LLM-only issue
                ctx.llm_only.append({
                    **item,
                    "reason": LLM_ONLY_CODES[result.code],
                })

        return ctx
```

5. Update `fix_issue()` to track partial fixes (~line 240):
```python
def fix_issue(self, issue: ValidationIssue) -> FixResult:
    """Fix a single issue."""
    if issue.code not in FIXABLE_CODES:
        # Check if LLM-only
        if issue.code in LLM_ONLY_CODES:
            return FixResult(
                code=issue.code,
                file_path=issue.file_path or self.doc_path,
                fixed=False,
                message=f"LLM_ONLY: {LLM_ONLY_CODES[issue.code]}"
            )
        return FixResult(
            code=issue.code,
            file_path=issue.file_path or self.doc_path,
            fixed=False,
            message="Not auto-fixable"
        )

    # Apply the fix using existing fix methods
    result = self._apply_fix_for_code(issue)

    # Check if this is a partial fix needing LLM completion
    if result.fixed and issue.code in LLM_COMPLETION_CODES:
        result.partial_fix = True
        result.llm_task = LLM_COMPLETION_CODES[issue.code]["llm_task"]
        # Insert completion marker in document
        if issue.file_path:
            self._insert_llm_marker(issue.file_path, issue)

    return result
```

---

## Phase 3: Document Markers with Safety

### Goal
Insert markers in documents for LLM to find, with YAML protection and deduplication.

### Changes

**File: `/opt/data/docs_flow_framework/UCX/ucx/validators/brd/fixer.py`**

1. Add marker pattern for deduplication (~line 180):
```python
# Pattern to detect existing LLM markers
LLM_MARKER_PATTERN = re.compile(r'<!-- LLM_COMPLETION: (\S+) -->')
```

2. Add YAML frontmatter protection (~line 250):
```python
def _find_safe_insertion_point(self, content: str, target_line: int) -> int:
    """Find safe insertion point avoiding YAML frontmatter.

    Args:
        content: File content
        target_line: Desired line number (1-indexed)

    Returns:
        Safe 0-indexed line position for insertion
    """
    lines = content.split("\n")

    # Detect YAML frontmatter boundaries
    frontmatter_end = 0
    if lines and lines[0].strip() == "---":
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                frontmatter_end = i + 1
                break

    # If target is in frontmatter, insert after it
    if target_line <= frontmatter_end:
        return frontmatter_end

    # Bounds check
    if target_line < 1:
        return frontmatter_end if frontmatter_end > 0 else 0
    if target_line > len(lines):
        return len(lines)

    return target_line - 1
```

3. Add marker insertion with deduplication (~line 280):
```python
def _insert_llm_marker(self, file_path: Path, issue: ValidationIssue) -> None:
    """Insert LLM_COMPLETION marker at safe location with deduplication."""
    if issue.code not in LLM_COMPLETION_CODES:
        return

    content = self._read_file(file_path)

    # Check for existing marker for this code (deduplication)
    existing_markers = LLM_MARKER_PATTERN.findall(content)
    if issue.code in existing_markers:
        logger.debug(f"Marker for {issue.code} already exists in {file_path}")
        return

    lines = content.split("\n")
    info = LLM_COMPLETION_CODES[issue.code]

    marker = f"<!-- LLM_COMPLETION: {issue.code} -->\n"
    marker += f"<!-- Script: {info['script_action']} -->\n"
    marker += f"<!-- Task: {info['llm_task']} -->"

    insert_at = self._find_safe_insertion_point(content, issue.line or 1)
    lines.insert(insert_at, marker)

    self._file_cache[file_path] = "\n".join(lines)
    self._modified_files.add(file_path)
    logger.debug(f"Inserted LLM_COMPLETION marker for {issue.code} at line {insert_at + 1}")
```

---

## Phase 4: CLI Integration (Always Fix)

### Goal
Update CLI to always run fixer during validation. Use `--no-fix` to opt out.

### Changes

**File: `/opt/data/docs_flow_framework/UCX/ucx/cli/main.py`**

1. Update CLI options (~line 750):
```python
@click.option(
    "--no-fix",
    is_flag=True,
    default=False,
    help="Skip auto-fixing (validation always fixes by default)"
)
```

2. Add imports:
```python
from ucx.validators.common.result import FixerContext
```

3. Update validation command to always fix (~line 850):
```python
# Always fix unless --no-fix is specified
fix_summary = None
if not no_fix and fixable_issues:
    console.print(f"\n[cyan]Auto-fixing {len(fixable_issues)} structural issue(s)...[/cyan]")
    fixer = BRDFixer(doc_path, verbose=ctx.obj.get("verbose", False))
    fix_summary = fixer.fix_all(fixable_issues)

    # Display fix results
    for fix_result in fix_summary.results:
        if fix_result.fixed:
            status = "[cyan]◐[/cyan]" if fix_result.partial_fix else "[green]✓[/green]"
            console.print(f"  {status} {fix_result.code}: {fix_result.message}")
            if fix_result.partial_fix:
                console.print(f"    [dim]LLM Task: {fix_result.llm_task}[/dim]")
        else:
            console.print(f"  [yellow]⊘[/yellow] {fix_result.code}: {fix_result.message}")

    # Summary line
    console.print(
        f"\n[green]Fixed: {fix_summary.fully_fixed_count}[/green] | "
        f"[cyan]Partial: {fix_summary.partial_fix_count}[/cyan] | "
        f"[yellow]Skipped: {fix_summary.skipped_count}[/yellow] | "
        f"[red]Failed: {fix_summary.failed_count}[/red]"
    )

    if fix_summary.partial_fix_count > 0:
        console.print(f"\n[cyan]LLM Completion Required: {fix_summary.partial_fix_count}[/cyan]")
        console.print("[dim]Run `ucx remediate` to complete partial fixes with AI.[/dim]")

    # Re-validate after fixing
    result = validator.validate(doc_path)

# Attach fixer context to result
if fix_summary:
    result.fixer_context = fix_summary.to_fixer_context(doc_path)
```

4. Update report generation (~line 890):
```python
# Generate report (always includes Section 7 since we always fix)
if generate_report:
    report_path = doc_path / ".precommit_validation_report.md"
    report_content = result.format_report(
        doc_id=doc_id,
        doc_type="BRD",
        version=version,
    )
    report_path.write_text(report_content)
    console.print(f"\n[dim]Report: {report_path}[/dim]")
```

5. Add clean-markers command (~line 950):
```python
@validate.command("clean-markers")
@click.argument("doc_path", type=click.Path(exists=True))
@click.pass_context
def clean_markers(ctx, doc_path: str):
    """Remove LLM_COMPLETION markers from documents."""
    import re
    doc_path = Path(doc_path)

    # Handle file vs directory
    if doc_path.is_file():
        doc_path = doc_path.parent

    # Pattern to match marker blocks
    marker_pattern = re.compile(
        r'<!-- LLM_COMPLETION:[^>]+-->\n?'
        r'(?:<!-- Script:[^>]+-->\n?)?'
        r'(?:<!-- Task:[^>]+-->\n?)?',
        re.MULTILINE
    )

    cleaned_count = 0
    for md_file in doc_path.glob("**/*.md"):
        # Skip hidden directories
        if any(part.startswith('.') for part in md_file.parts):
            continue

        content = md_file.read_text()
        new_content = marker_pattern.sub('', content)

        if content != new_content:
            md_file.write_text(new_content)
            cleaned_count += 1
            console.print(f"  [green]✓[/green] Cleaned: {md_file.name}")

    if cleaned_count > 0:
        console.print(f"\n[green]Cleaned markers from {cleaned_count} file(s)[/green]")
    else:
        console.print("[yellow]No markers found to clean[/yellow]")
```

6. CLI behavior (always fix by default):
```python
# CLI Flag Matrix:
# --no-fix | --report    | Behavior
# ---------|-------------|------------------------------------------
# No       | No          | Fix + console only (default)
# No       | Yes         | Fix + report with Section 7 (default)
# Yes      | No          | Skip fix, console only
# Yes      | Yes         | Skip fix, report without Section 7
#
# Examples:
#   ucx validate brd BRD-01              # Fix + report (default)
#   ucx validate brd BRD-01 --no-fix     # Skip fixing
#   ucx validate brd BRD-01 --no-report  # Fix but no report file
```

---

## Phase 5: Remediation Integration

### Goal
UCRem reads fixer context from validation report and injects into prompts.

### Changes

**File: `/opt/data/docs_flow_framework/UCX/ucx/api/remediation.py`**

1. Add imports:
```python
import re
import json
import logging
from pathlib import Path
from typing import Optional

from ucx.validators.common.result import FixerContext

logger = logging.getLogger(__name__)
```

2. Add fixer context patterns and loader (~line 140):
```python
# Pattern to extract fixer context JSON from validation report
FIXER_CONTEXT_PATTERN = re.compile(
    r'<!-- FIXER_CONTEXT_START\n(.*?)\nFIXER_CONTEXT_END -->',
    re.DOTALL
)

def _load_fixer_context(self, doc_path: Path) -> Optional[dict]:
    """Load fixer context from validation report.

    Args:
        doc_path: Document path (file or directory)

    Returns:
        Fixer context dict or None if not found/invalid
    """
    # Handle file vs directory
    if doc_path.is_file():
        report_path = doc_path.parent / ".precommit_validation_report.md"
    else:
        report_path = doc_path / ".precommit_validation_report.md"

    if not report_path.exists():
        logger.debug(f"No validation report found at {report_path}")
        return None

    try:
        content = report_path.read_text()
    except IOError as e:
        logger.warning(f"Failed to read validation report: {e}")
        return None

    match = FIXER_CONTEXT_PATTERN.search(content)
    if not match:
        logger.debug("No fixer context found in validation report")
        return None

    try:
        context = json.loads(match.group(1))

        # Schema validation
        if context.get("schema_version", "0") < "1.0":
            logger.warning("Outdated fixer context schema")

        required = ["session_id", "timestamp"]
        if not all(f in context for f in required):
            logger.warning("Fixer context missing required fields")
            return None

        logger.info(
            f"Loaded fixer context: session={context.get('session_id')}, "
            f"partial_fixes={len(context.get('llm_completion', []))}"
        )
        return context

    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse fixer context JSON: {e}")
        return None
```

3. Update `generate_fixes()` to load context (~line 180):
```python
def generate_fixes(self, doc_path, review_report=None, output_path=None):
    """Generate fixes for a document."""
    doc_path = Path(doc_path)

    # ... existing pre-screening code ...
    self.last_screening = analyze_ucr_report(review_report)

    # Load fixer context from validation report
    self.fixer_context = self._load_fixer_context(doc_path)

    # ... rest of method ...
```

4. Add comprehensive prompt injection (~line 390):
```python
def _build_remediation_prompt(self, ...):
    """Build remediation prompt with fixer context."""
    # ... existing context building ...

    # Inject fixer hand-off context
    parts.append(self._format_fixer_handoff_section())

    # ... rest of method ...

def _format_fixer_handoff_section(self) -> str:
    """Format fixer hand-off section for remediation prompt."""
    lines = ["\n## FIXER HAND-OFF CONTEXT\n"]

    if not self.fixer_context:
        lines.extend([
            "No fixer context found in validation report.",
            "",
            "**Recommendation**: Run `ucx validate --fix` before remediation",
            "to apply automatic fixes and identify items needing LLM attention.",
            "",
        ])
        return "\n".join(lines)

    # Session info
    lines.extend([
        f"**Fixer Session**: `{self.fixer_context.get('session_id', 'N/A')}`",
        f"**Timestamp**: {self.fixer_context.get('timestamp', 'N/A')}",
        "",
    ])

    # LLM Completion items (highest priority)
    llm_completion = self.fixer_context.get("llm_completion", [])
    if llm_completion:
        lines.extend([
            "### Partial Fixes - COMPLETE THESE FIRST",
            "",
            "Script applied partial fixes. Your task is to complete them:",
            "",
            "| Code | File | Script Action | Your Task |",
            "|------|------|---------------|-----------|",
        ])
        for item in llm_completion:
            lines.append(
                f"| `{item['code']}` | `{item['file']}` | "
                f"{item['script_action']} | **{item['llm_task']}** |"
            )
        lines.extend([
            "",
            "Look for `<!-- LLM_COMPLETION: CODE -->` markers in documents.",
            "After completing each task, remove the marker.",
            "",
        ])

    # LLM-only items
    llm_only = self.fixer_context.get("llm_only", [])
    if llm_only:
        lines.extend([
            "### LLM-Only Issues",
            "",
            "These require semantic understanding (no script fix possible):",
            "",
            "| Code | File | Reason |",
            "|------|------|--------|",
        ])
        for item in llm_only:
            lines.append(f"| `{item['code']}` | `{item['file']}` | {item['reason']} |")
        lines.append("")

    # Protected changes (DO NOT UNDO)
    fixer_applied = self.fixer_context.get("fixer_applied", [])
    if fixer_applied:
        lines.extend([
            "### PROTECTED - Do Not Undo These Fixes",
            "",
            "Script successfully applied these fixes. **DO NOT modify or undo**:",
            "",
        ])
        for item in fixer_applied[:10]:
            lines.append(f"- `{item['code']}` in `{item['file']}`")
        if len(fixer_applied) > 10:
            lines.append(f"- ... and {len(fixer_applied) - 10} more")
        lines.extend([
            "",
            "If you believe a fix is incorrect, note it but do not change it.",
            "",
        ])

    return "\n".join(lines)
```

---

## Phase 6: Persona Skill Updates

### Goal
Update all 6 fixer personas with hand-off protocol.

### Files to Update
- `skills/architect.md`
- `skills/auditor.md`
- `skills/qa_lead.md`
- `skills/integration_lead.md`
- `skills/chaos_engineer.md`
- `skills/chairperson.md`

### Section to Add (same for all)

```markdown
## Fixer Hand-off Protocol

The script-based fixer (`ucx validate --fix`) runs before LLM remediation.

### 1. Check Prompt for "FIXER HAND-OFF CONTEXT"

If present, you will see:
- **Partial Fixes - COMPLETE THESE FIRST**: Items where script did mechanical work, you provide semantic completion
- **LLM-Only Issues**: Items requiring your domain expertise
- **PROTECTED - Do Not Undo**: Script fixes you must NOT modify

### 2. Document Markers

Look for these markers in documents:

```html
<!-- LLM_COMPLETION: CODE -->
<!-- Script: What the script did -->
<!-- Task: What you should complete -->
```

**Your task**: Provide the semantic completion described in "Task".

### 3. Priority Order

1. Complete `llm_completion` items FIRST (partial fixes)
2. Address `llm_only` items
3. Handle other findings
4. Verify `fixer_applied` items are correct (but don't modify)

### 4. After Completion

Remove the `<!-- LLM_COMPLETION: ... -->` marker block after completing each task.

### 5. If No Fixer Context

If prompt shows "No fixer context found", recommend running:
```bash
ucx validate --fix <doc_path>
```
before remediation for better results.
```

---

## Implementation Order

| Step | Phase | Task | File |
|------|-------|------|------|
| 1 | 1 | Add imports to result.py | result.py |
| 2 | 1 | Add `FixerContext` dataclass | result.py |
| 3 | 1 | Add `fixer_context` field to UnifiedValidationResult | result.py |
| 4 | 1 | Add `_format_fixer_section()` | result.py |
| 5 | 1 | Update `format_report()` | result.py |
| 6 | 2 | Add imports to fixer.py | fixer.py |
| 7 | 2 | Add `LLM_COMPLETION_CODES`, `LLM_ONLY_CODES` | fixer.py |
| 8 | 2 | Update `FixResult` with new fields | fixer.py |
| 9 | 2 | Update `FixSummary` with `to_fixer_context()` | fixer.py |
| 10 | 2 | Update `fix_issue()` for partial tracking | fixer.py |
| 11 | 3 | Add `LLM_MARKER_PATTERN` | fixer.py |
| 12 | 3 | Add `_find_safe_insertion_point()` | fixer.py |
| 13 | 3 | Add `_insert_llm_marker()` with deduplication | fixer.py |
| 14 | 4 | Change CLI to always fix (add `--no-fix` opt-out) | main.py |
| 15 | 4 | Update CLI fix handling and output | main.py |
| 16 | 4 | Add `clean-markers` command | main.py |
| 17 | 5 | Add imports to remediation.py | remediation.py |
| 18 | 5 | Add `_load_fixer_context()` | remediation.py |
| 19 | 5 | Add `_format_fixer_handoff_section()` | remediation.py |
| 20 | 5 | Update `_build_remediation_prompt()` | remediation.py |
| 21 | 6 | Update architect.md | skills/ |
| 22 | 6 | Update auditor.md | skills/ |
| 23 | 6 | Update qa_lead.md | skills/ |
| 24 | 6 | Update integration_lead.md | skills/ |
| 25 | 6 | Update chaos_engineer.md | skills/ |
| 26 | 6 | Update chairperson.md | skills/ |
| 27 | - | Add unit tests | tests/ |
| 28 | - | Add integration tests | tests/ |
| 29 | - | Update version.py | version.py |
| 30 | - | Create CHANGELOG_v1.17.0.md | docs/ |

---

## Files to Modify

| File | Changes |
|------|---------|
| `ucx/validators/common/result.py` | +80 lines: FixerContext, _format_fixer_section() |
| `ucx/validators/brd/fixer.py` | +90 lines: LLM codes, partial tracking, markers |
| `ucx/api/remediation.py` | +80 lines: context loading, prompt injection |
| `ucx/cli/main.py` | +50 lines: always-fix default, clean-markers |
| `skills/architect.md` | +30 lines: hand-off protocol |
| `skills/auditor.md` | +30 lines: hand-off protocol |
| `skills/qa_lead.md` | +30 lines: hand-off protocol |
| `skills/integration_lead.md` | +30 lines: hand-off protocol |
| `skills/chaos_engineer.md` | +30 lines: hand-off protocol |
| `skills/chairperson.md` | +30 lines: hand-off protocol |
| `tests/unit/test_fixer_context.py` | +120 lines: new test file |
| `tests/integration/test_fixer_handoff.py` | +100 lines: new test file |
| `ucx/version.py` | Version bump to 1.17.0 |
| `docs/CHANGELOG_v1.17.0.md` | New changelog |

**Total**: ~300 lines of production code + ~220 lines of tests

---

## Unit Tests

**File: `tests/unit/test_fixer_context.py`**

```python
import pytest
import json
from pathlib import Path
from datetime import datetime, timezone

from ucx.validators.common.result import FixerContext, UnifiedValidationResult
from ucx.validators.brd.fixer import (
    FixResult, FixSummary, LLM_COMPLETION_CODES, LLM_ONLY_CODES
)


class TestFixerContext:
    """Tests for FixerContext dataclass."""

    def test_creation_with_defaults(self):
        """Test FixerContext creation with default values."""
        ctx = FixerContext()
        assert ctx.schema_version == "1.0"
        assert ctx.session_id == ""
        assert ctx.llm_completion == []

    def test_to_dict(self):
        """Test conversion to dictionary."""
        ctx = FixerContext(session_id="abc123", fixed_count=5)
        d = ctx.to_dict()
        assert d["session_id"] == "abc123"
        assert d["fixed_count"] == 5

    def test_to_json(self):
        """Test JSON serialization."""
        ctx = FixerContext(session_id="abc123")
        json_str = ctx.to_json()
        parsed = json.loads(json_str)
        assert parsed["session_id"] == "abc123"

    def test_from_json_valid(self):
        """Test parsing valid JSON."""
        json_str = '{"session_id": "abc", "timestamp": "2026-01-01T00:00:00Z"}'
        ctx = FixerContext.from_json(json_str)
        assert ctx is not None
        assert ctx.session_id == "abc"

    def test_from_json_missing_required(self):
        """Test parsing JSON missing required fields."""
        json_str = '{"fixed_count": 5}'
        ctx = FixerContext.from_json(json_str)
        assert ctx is None

    def test_from_json_invalid(self):
        """Test parsing invalid JSON."""
        ctx = FixerContext.from_json("not valid json")
        assert ctx is None


class TestFixResult:
    """Tests for FixResult dataclass."""

    def test_partial_fix_fields(self):
        """Test partial_fix and llm_task fields."""
        result = FixResult(
            code="GATE-E010",
            file_path=Path("test.md"),
            fixed=True,
            message="Split file",
            partial_fix=True,
            llm_task="Review splits"
        )
        assert result.partial_fix is True
        assert result.llm_task == "Review splits"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = FixResult(
            code="BRD-E002",
            file_path=Path("test.md"),
            fixed=True,
            message="Added field",
            changes=["Added document_type"]
        )
        d = result.to_dict()
        assert d["code"] == "BRD-E002"
        assert d["partial_fix"] is False


class TestFixSummary:
    """Tests for FixSummary with to_fixer_context()."""

    def test_fully_fixed_count(self):
        """Test fully_fixed_count property."""
        summary = FixSummary(fixed_count=10, partial_fix_count=3)
        assert summary.fully_fixed_count == 7

    def test_add_partial_fix(self):
        """Test adding partial fix result."""
        summary = FixSummary()
        result = FixResult(
            code="GATE-E010",
            file_path=Path("test.md"),
            fixed=True,
            message="Split",
            partial_fix=True
        )
        summary.add(result)
        assert summary.fixed_count == 1
        assert summary.partial_fix_count == 1

    def test_to_fixer_context(self):
        """Test conversion to FixerContext."""
        summary = FixSummary()
        summary.add(FixResult(
            code="GATE-E010",
            file_path=Path("test.md"),
            fixed=True,
            message="Split",
            partial_fix=True,
            llm_task="Review"
        ))
        summary.add(FixResult(
            code="BRD-E002",
            file_path=Path("index.md"),
            fixed=True,
            message="Added field"
        ))

        ctx = summary.to_fixer_context(Path("/test"))
        assert ctx.partial_fix_count == 1
        assert ctx.fixed_count == 1  # Fully fixed only
        assert len(ctx.llm_completion) == 1
        assert len(ctx.fixer_applied) == 2  # Both partial and full


class TestLLMCodes:
    """Tests for LLM code constants."""

    def test_llm_completion_codes_structure(self):
        """Test LLM_COMPLETION_CODES has required keys."""
        for code, info in LLM_COMPLETION_CODES.items():
            assert "script_action" in info
            assert "llm_task" in info

    def test_llm_only_codes_structure(self):
        """Test LLM_ONLY_CODES are strings."""
        for code, reason in LLM_ONLY_CODES.items():
            assert isinstance(reason, str)


class TestMarkerInsertion:
    """Tests for marker insertion."""

    def test_yaml_frontmatter_detection(self, tmp_path):
        """Test markers not inserted in YAML frontmatter."""
        from ucx.validators.brd.fixer import BRDFixer

        content = """---
doc_id: TEST-01
title: Test
---

# Content here
"""
        test_file = tmp_path / "test.md"
        test_file.write_text(content)

        fixer = BRDFixer(tmp_path)
        safe_line = fixer._find_safe_insertion_point(content, 2)
        assert safe_line >= 4  # After frontmatter

    def test_marker_deduplication(self, tmp_path):
        """Test same marker not inserted twice."""
        from ucx.validators.brd.fixer import BRDFixer
        from ucx.validators.common.result import ValidationIssue

        content = """---
doc_id: TEST-01
---

<!-- LLM_COMPLETION: GATE-E010 -->
<!-- Script: Existing -->
<!-- Task: Existing -->

# Content
"""
        test_file = tmp_path / "test.md"
        test_file.write_text(content)

        fixer = BRDFixer(tmp_path)
        fixer._file_cache[test_file] = content

        issue = ValidationIssue(
            code="GATE-E010",
            message="Test",
            file_path=test_file,
            line=8
        )
        fixer._insert_llm_marker(test_file, issue)

        # Should not add duplicate
        result = fixer._file_cache[test_file]
        assert result.count("LLM_COMPLETION: GATE-E010") == 1


class TestValidationReportGeneration:
    """Tests for Section 7 generation."""

    def test_format_fixer_section(self):
        """Test _format_fixer_section() output."""
        result = UnifiedValidationResult()
        result.fixer_context = FixerContext(
            session_id="abc123",
            timestamp="2026-01-01T00:00:00Z",
            fixed_count=5,
            partial_fix_count=2,
            llm_completion=[
                {"code": "GATE-E010", "file": "test.md",
                 "script_action": "Split", "llm_task": "Review"}
            ]
        )
        section = result._format_fixer_section()
        assert "abc123" in section
        assert "GATE-E010" in section
        assert "FIXER_CONTEXT_START" in section

    def test_format_report_includes_section7(self):
        """Test report includes Section 7 when fixer_context present."""
        result = UnifiedValidationResult()
        result.fixer_context = FixerContext(session_id="test")
        report = result.format_report(doc_id="TEST-01")
        assert "## 7. Fixer Session Summary" in report


class TestRemediationContextLoading:
    """Tests for remediation fixer context loading."""

    def test_load_from_validation_report(self, tmp_path):
        """Test loading fixer context from validation report."""
        from ucx.api.remediation import UCRemPhase

        report = """
# Validation Report

<!-- FIXER_CONTEXT_START
{
  "schema_version": "1.0",
  "session_id": "test123",
  "timestamp": "2026-01-01T00:00:00Z",
  "fixed_count": 5,
  "partial_fix_count": 2,
  "llm_completion": [
    {"code": "GATE-E010", "file": "test.md", "script_action": "Split", "llm_task": "Review"}
  ],
  "fixer_applied": []
}
FIXER_CONTEXT_END -->
"""
        report_path = tmp_path / ".precommit_validation_report.md"
        report_path.write_text(report)

        rem = UCRemPhase()
        ctx = rem._load_fixer_context(tmp_path)

        assert ctx is not None
        assert ctx["session_id"] == "test123"
        assert len(ctx["llm_completion"]) == 1

    def test_missing_report_returns_none(self, tmp_path):
        """Test None returned when report doesn't exist."""
        from ucx.api.remediation import UCRemPhase

        rem = UCRemPhase()
        ctx = rem._load_fixer_context(tmp_path)
        assert ctx is None

    def test_corrupt_json_returns_none(self, tmp_path):
        """Test None returned for corrupt JSON."""
        from ucx.api.remediation import UCRemPhase

        report = """
<!-- FIXER_CONTEXT_START
{invalid json here
FIXER_CONTEXT_END -->
"""
        report_path = tmp_path / ".precommit_validation_report.md"
        report_path.write_text(report)

        rem = UCRemPhase()
        ctx = rem._load_fixer_context(tmp_path)
        assert ctx is None

    def test_handles_file_path_input(self, tmp_path):
        """Test loading when doc_path is a file, not directory."""
        from ucx.api.remediation import UCRemPhase

        report = """
<!-- FIXER_CONTEXT_START
{"session_id": "test", "timestamp": "2026-01-01"}
FIXER_CONTEXT_END -->
"""
        report_path = tmp_path / ".precommit_validation_report.md"
        report_path.write_text(report)

        # Pass a file path instead of directory
        file_path = tmp_path / "some_file.md"
        file_path.write_text("content")

        rem = UCRemPhase()
        ctx = rem._load_fixer_context(file_path)
        assert ctx is not None
```

**File: `tests/integration/test_fixer_handoff.py`**

```python
import pytest
from pathlib import Path


class TestFullWorkflow:
    """Integration tests for complete fixer-to-remediation workflow."""

    @pytest.fixture
    def sample_brd(self, tmp_path):
        """Create a sample BRD with fixable issues."""
        brd_dir = tmp_path / "BRD-TEST"
        brd_dir.mkdir()

        # Index file missing required fields
        index = brd_dir / "BRD-TEST.0_index.md"
        index.write_text("""---
doc_id: BRD-TEST
title: Test Document
---

# BRD-TEST Index

## Contents
- Section 1
""")

        # Section with diagram placeholder issue
        section = brd_dir / "BRD-TEST.1_intro.md"
        section.write_text("""---
doc_id: BRD-TEST.1
title: Introduction
---

# Introduction

[TBD: Add C4-L1 system context diagram]

## Overview

This is the overview.
""")

        return brd_dir

    def test_validate_always_creates_section7(self, sample_brd):
        """Test that validation (always fixes) creates Section 7."""
        from ucx.validators.brd.validator import UnifiedBRDValidator
        from ucx.validators.brd.fixer import BRDFixer

        # Validate (always fixes by default)
        validator = UnifiedBRDValidator()
        result = validator.validate(sample_brd)

        # Fix (always runs)
        fixer = BRDFixer(sample_brd)
        fix_summary = fixer.fix_all(result.issues)

        # Attach context
        result.fixer_context = fix_summary.to_fixer_context(sample_brd)

        # Generate report
        report = result.format_report(doc_id="BRD-TEST")

        assert "## 7. Fixer Session Summary" in report
        assert "FIXER_CONTEXT_START" in report

    def test_no_fix_flag_skips_section7(self, sample_brd):
        """Test that --no-fix skips Section 7."""
        from ucx.validators.brd.validator import UnifiedBRDValidator

        # Validate without fixing
        validator = UnifiedBRDValidator()
        result = validator.validate(sample_brd)
        result.fixer_context = None  # No fixing

        report = result.format_report(doc_id="BRD-TEST")

        # Section 7 should NOT be present
        assert "## 7. Fixer Session Summary" not in report

    def test_remediation_loads_fixer_context(self, sample_brd):
        """Test that remediation loads fixer context from report."""
        from ucx.validators.brd.validator import UnifiedBRDValidator
        from ucx.validators.brd.fixer import BRDFixer
        from ucx.api.remediation import UCRemPhase

        # Validate + fix
        validator = UnifiedBRDValidator()
        result = validator.validate(sample_brd)
        fixer = BRDFixer(sample_brd)
        fix_summary = fixer.fix_all(result.issues)
        result.fixer_context = fix_summary.to_fixer_context(sample_brd)

        # Write report
        report_path = sample_brd / ".precommit_validation_report.md"
        report_path.write_text(result.format_report(doc_id="BRD-TEST"))

        # Load in remediation
        rem = UCRemPhase()
        ctx = rem._load_fixer_context(sample_brd)

        assert ctx is not None
        assert "session_id" in ctx

    def test_clean_markers_removes_all(self, sample_brd):
        """Test that clean-markers removes all LLM markers."""
        # Add markers to file
        section = sample_brd / "BRD-TEST.1_intro.md"
        content = section.read_text()
        content = content.replace(
            "# Introduction",
            "<!-- LLM_COMPLETION: GATE-E010 -->\n"
            "<!-- Script: Test -->\n"
            "<!-- Task: Review -->\n"
            "# Introduction"
        )
        section.write_text(content)

        # Verify marker exists
        assert "LLM_COMPLETION" in section.read_text()

        # Clean markers (simulate CLI command)
        import re
        marker_pattern = re.compile(
            r'<!-- LLM_COMPLETION:[^>]+-->\n?'
            r'(?:<!-- Script:[^>]+-->\n?)?'
            r'(?:<!-- Task:[^>]+-->\n?)?'
        )

        for md_file in sample_brd.glob("**/*.md"):
            content = md_file.read_text()
            new_content = marker_pattern.sub('', content)
            if content != new_content:
                md_file.write_text(new_content)

        # Verify marker removed
        assert "LLM_COMPLETION" not in section.read_text()

    def test_prompt_injection_format(self, sample_brd):
        """Test that fixer context is properly formatted in prompt."""
        from ucx.api.remediation import UCRemPhase

        # Create mock fixer context
        rem = UCRemPhase()
        rem.fixer_context = {
            "session_id": "test123",
            "timestamp": "2026-01-01T00:00:00Z",
            "llm_completion": [
                {
                    "code": "GATE-E010",
                    "file": "test.md",
                    "script_action": "Split file",
                    "llm_task": "Review splits"
                }
            ],
            "fixer_applied": [
                {"code": "BRD-E002", "file": "index.md"}
            ]
        }

        section = rem._format_fixer_handoff_section()

        assert "FIXER HAND-OFF CONTEXT" in section
        assert "test123" in section
        assert "COMPLETE THESE FIRST" in section
        assert "GATE-E010" in section
        assert "PROTECTED" in section
        assert "BRD-E002" in section
```

---

## Verification

1. **Test Section 7 Generation (always fix)**:
```bash
cd /opt/data/docs_flow_framework/UCX
PYTHONPATH=. python -c "
from pathlib import Path
from ucx.validators.brd.validator import UnifiedBRDValidator
from ucx.validators.brd.fixer import BRDFixer

doc_path = Path('test_doc')
validator = UnifiedBRDValidator()
result = validator.validate(doc_path)

fixer = BRDFixer(doc_path)
summary = fixer.fix_all(result.issues)
result.fixer_context = summary.to_fixer_context(doc_path)

report = result.format_report(doc_id='TEST-01')
print('Section 7 present:', '## 7. Fixer Session Summary' in report)
print('JSON present:', 'FIXER_CONTEXT_START' in report)
"
```

2. **Test Default Behavior (always fixes)**:
```bash
# Default: validation always fixes
ucx validate brd docs/01_BRD/BRD-01

# Check Section 7 exists
grep "## 7. Fixer Session" docs/01_BRD/BRD-01/.precommit_validation_report.md

# Opt-out: skip fixing
ucx validate brd docs/01_BRD/BRD-01 --no-fix

# Section 7 should NOT exist (no fixing was done)
grep "## 7. Fixer Session" docs/01_BRD/BRD-01/.precommit_validation_report.md || echo "No Section 7 (expected)"
```

3. **Test Remediation Context Loading**:
```bash
PYTHONPATH=. python -c "
from pathlib import Path
from ucx.api.remediation import UCRemPhase

rem = UCRemPhase()
ctx = rem._load_fixer_context(Path('docs/01_BRD/BRD-01'))
print(f'Context loaded: {ctx is not None}')
if ctx:
    print(f'Session: {ctx.get(\"session_id\")}')
    print(f'Partial fixes: {len(ctx.get(\"llm_completion\", []))}')
"
```

4. **Test Clean Markers**:
```bash
ucx validate clean-markers docs/01_BRD/BRD-01
```

5. **Run Unit Tests**:
```bash
pytest tests/unit/test_fixer_context.py -v
pytest tests/integration/test_fixer_handoff.py -v
```

---

## Flow Diagram

```
┌────────────────────────────────────────────┐
│     ucx validate brd BRD-01                │
│     (ALWAYS fixes by default)              │
└────────┬───────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│          1. Validation                   │
│  └─ Identifies all issues                │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│          2. BRD Fixer (automatic)        │
│  ├─ Fix issues (full or partial)         │
│  ├─ Track partial fixes (LLM_COMPLETION) │
│  ├─ Insert markers in documents          │
│  └─ Build FixerContext                   │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│          3. Re-validation                │
│  └─ Verify fixes, find remaining issues  │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│     4. Report Generation                 │
│  ├─ Sections 1-6: Standard content       │
│  └─ Section 7: Fixer Session Summary     │
│       ├─ LLM Completion table            │
│       ├─ Protected changes list          │
│       └─ Embedded JSON (machine-readable)│
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│     .precommit_validation_report.md      │
│  (Single source: validation + fixer)     │
│  (Section 7 always fresh)                │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│          UCRem Remediation               │
│  ├─ Parse FIXER_CONTEXT_START block      │
│  ├─ Validate JSON schema                 │
│  ├─ Inject "FIXER HAND-OFF CONTEXT"      │
│  │   - Partial fixes (highest priority)  │
│  │   - LLM-only issues                   │
│  │   - Protected changes (DO NOT UNDO)   │
│  └─ Personas complete tasks              │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│     ucx validate clean-markers           │
│  - Remove LLM_COMPLETION markers         │
│  - Run after remediation complete        │
└──────────────────────────────────────────┘
```

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Report parsing failures | Regex with schema validation; graceful None return |
| YAML frontmatter corruption | Safe insertion point detection |
| Marker accumulation | Deduplication check + clean-markers command |
| Large fixer context | Limit fixer_applied to 10 items in display |
| JSON in HTML comment | Escape `-->` if present in paths (rare) |
| Backwards compatibility | `--no-fix` flag for opt-out |
| Always-fix breaks workflow | Clear messaging; opt-out available |
| Multiple runs | Each run creates fresh context; markers deduplicated |

---

## Benefits of Always-Fix Approach

| Aspect | Before (--fix flag) | After (always fix) |
|--------|---------------------|-------------------|
| User workflow | Must remember `--fix` | Just run `ucx validate` |
| Section 7 freshness | Could be stale | Always current |
| Code complexity | Preservation logic needed | Simple - always generate |
| Remediation context | May be missing | Always available |
| Lines of code | ~330 | ~300 (removed preservation) |

---

## Gap Resolutions (Final Review)

Addresses 15 gaps identified in final review:

### GAP-CLI-001: `--fix` Flag Deprecation

**Problem**: Existing scripts may use `--fix` flag which is now default behavior.

**Resolution**: Add deprecation warning (not error) for backwards compatibility.

**File: `ucx/cli/main.py`** (~line 745):
```python
@click.option(
    "--fix",
    is_flag=True,
    default=False,
    hidden=True,  # Hide from help text
    help="DEPRECATED: Validation now always fixes. Use --no-fix to skip."
)
@click.option(
    "--no-fix",
    is_flag=True,
    default=False,
    help="Skip auto-fixing (validation always fixes by default)"
)
def validate_brd(ctx, doc_path: str, fix: bool, no_fix: bool, ...):
    # Deprecation warning
    if fix:
        console.print(
            "[yellow]⚠ --fix is deprecated. Validation now always fixes by default. "
            "Use --no-fix to skip fixing.[/yellow]"
        )
```

---

### GAP-BC-001: Breaking Change Documentation

**Problem**: CHANGELOG needs clear breaking change section.

**Resolution**: Add to `docs/CHANGELOG_v1.17.0.md`:

```markdown
## ⚠️ Breaking Changes

### Validation Now Always Fixes

**Before (v1.16.x)**: `ucx validate brd BRD-01` validated only; `--fix` required for fixes.

**After (v1.17.0)**: `ucx validate brd BRD-01` validates AND fixes automatically.

**Migration**:
- Remove `--fix` from all scripts and CI/CD pipelines (now default)
- Add `--no-fix` where validation-only behavior is needed
- Update pre-commit hooks to use `--no-fix` (see GAP-BC-002)

**Why**: Reduces friction, ensures Section 7 (fixer context) is always fresh for remediation.
```

---

### GAP-BC-002: Pre-commit Hook Behavior

**Problem**: Pre-commit hooks should NOT auto-fix (staging area issues).

**Resolution**: Update `.pre-commit-config.yaml` template and documentation.

**File: `docs/CHANGELOG_v1.17.0.md`** (add section):
```markdown
### Pre-commit Hook Update

Pre-commit hooks should use `--no-fix` to prevent staging area conflicts:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ucx-validate
        name: UCX BRD Validation
        entry: ucx validate brd --no-fix  # <-- ADD --no-fix
        language: system
        files: ^docs/01_BRD/
        types: [markdown]
```

**Rationale**: Pre-commit runs on staged files. Auto-fixing would modify files outside staging, causing confusion.
```

---

### GAP-FLOW-001: FixerContext Import in main.py

**Problem**: Import statement needs explicit verification.

**Resolution**: Confirm import at top of `ucx/cli/main.py`:

```python
# Existing imports section (~line 25)
from ucx.validators.common.result import (
    ValidationIssue,
    UnifiedValidationResult,
    FixerContext,  # NEW: For fixer hand-off
)
from ucx.validators.brd.fixer import BRDFixer, FixSummary
```

---

### GAP-FLOW-002: Circular Import Prevention

**Problem**: Need to verify no circular imports between modules.

**Resolution**: Import structure is safe because:

1. `result.py` → `FixerContext` (no fixer imports)
2. `fixer.py` → imports from `result.py` (one direction)
3. `main.py` → imports from both (top level)
4. `remediation.py` → imports `FixerContext` from `result.py`

**Verification test**:
```bash
PYTHONPATH=. python -c "
from ucx.validators.common.result import FixerContext
from ucx.validators.brd.fixer import BRDFixer, FixSummary
from ucx.api.remediation import UCRemPhase
print('All imports successful - no circular dependencies')
"
```

---

### GAP-TEST-002: CLI Option Tests

**Problem**: Need tests for `--fix` deprecation and `--no-fix` flag.

**Add to `tests/unit/test_fixer_context.py`**:
```python
class TestCLIOptions:
    """Tests for CLI flag behavior."""

    def test_fix_flag_shows_deprecation(self, cli_runner, sample_brd):
        """Test --fix shows deprecation warning."""
        from ucx.cli.main import cli

        result = cli_runner.invoke(cli, [
            "validate", "brd", str(sample_brd), "--fix"
        ])
        assert "--fix is deprecated" in result.output

    def test_no_fix_skips_fixing(self, cli_runner, sample_brd):
        """Test --no-fix skips auto-fixing."""
        from ucx.cli.main import cli

        result = cli_runner.invoke(cli, [
            "validate", "brd", str(sample_brd), "--no-fix"
        ])
        # Should NOT show fix results
        assert "Fixed:" not in result.output or "Fixed: 0" in result.output

    def test_default_runs_fixer(self, cli_runner, sample_brd):
        """Test default behavior runs fixer."""
        from ucx.cli.main import cli

        result = cli_runner.invoke(cli, [
            "validate", "brd", str(sample_brd)
        ])
        # Should show fix activity
        assert "Auto-fixing" in result.output or "Fixed:" in result.output
```

---

### GAP-CLI-002: Help Text Updates

**Problem**: Help text needs to reflect always-fix behavior.

**Resolution**: Update command help strings.

**File: `ucx/cli/main.py`** (~line 740):
```python
@click.command()
@click.argument("doc_path", type=click.Path(exists=True))
@click.option(
    "--no-fix",
    is_flag=True,
    default=False,
    help="Skip auto-fixing (validation always fixes by default)"
)
@click.option(
    "--report/--no-report",
    default=True,
    help="Generate validation report (default: yes)"
)
@click.pass_context
def validate_brd(ctx, doc_path, no_fix, report):
    """
    Validate a BRD document.

    Validation automatically fixes structural issues. Use --no-fix to skip fixing.

    Examples:

        ucx validate brd docs/01_BRD/BRD-01     # Validate + fix (default)

        ucx validate brd BRD-01 --no-fix        # Validate only

        ucx validate brd BRD-01 --no-report     # Fix but no report file
    """
```

---

### GAP-FLOW-003: Prompt Injection Location

**Problem**: Specify where fixer context is injected in remediation prompt.

**Resolution**: Inject after pre-screening results, before persona instructions.

**File: `ucx/api/remediation.py`** (~line 390):
```python
def _build_remediation_prompt(self, persona: str, findings: List[dict]) -> str:
    """Build complete remediation prompt."""
    parts = []

    # 1. System context (role, capabilities)
    parts.append(self._get_persona_system_prompt(persona))

    # 2. Document context (from review report)
    parts.append(self._format_document_context())

    # 3. Pre-screening results (UCR findings)
    parts.append(self._format_prescreening_results())

    # 4. FIXER HAND-OFF CONTEXT (NEW - injected here)
    parts.append(self._format_fixer_handoff_section())

    # 5. Specific findings to address
    parts.append(self._format_findings(findings))

    # 6. Persona-specific instructions
    parts.append(self._get_persona_instructions(persona))

    # 7. Output format requirements
    parts.append(self._format_output_requirements())

    return "\n\n".join(filter(None, parts))
```

---

### GAP-EDGE-001: Empty FixerContext Handling

**Problem**: Handle case where fixer ran but produced no results.

**Resolution**: Check for meaningful content before displaying.

**File: `ucx/validators/common/result.py`** (update `_format_fixer_section()`):
```python
def _format_fixer_section(self) -> str:
    """Format fixer session summary with embedded JSON."""
    ctx = self.fixer_context
    if not ctx:
        return ""

    # Check if context has any meaningful content
    has_content = (
        ctx.fixed_count > 0 or
        ctx.partial_fix_count > 0 or
        ctx.skipped_count > 0 or
        ctx.llm_completion or
        ctx.llm_only or
        ctx.fixer_applied
    )

    if not has_content:
        # Minimal section for empty fixer run
        return """
---

## 7. Fixer Session Summary

**Session ID**: `{session_id}`
**Result**: No issues required fixing.

<!-- FIXER_CONTEXT_START
{json_context}
FIXER_CONTEXT_END -->
""".format(session_id=ctx.session_id, json_context=ctx.to_json())

    # ... rest of full formatting ...
```

---

### GAP-EDGE-002: Fixer Error Recovery

**Problem**: Handle fixer exceptions gracefully.

**Resolution**: Wrap fixer call in try-catch, continue with validation report.

**File: `ucx/cli/main.py`** (~line 850):
```python
# Always fix unless --no-fix is specified
fix_summary = None
fixer_error = None

if not no_fix and fixable_issues:
    console.print(f"\n[cyan]Auto-fixing {len(fixable_issues)} structural issue(s)...[/cyan]")
    try:
        fixer = BRDFixer(doc_path, verbose=ctx.obj.get("verbose", False))
        fix_summary = fixer.fix_all(fixable_issues)
    except Exception as e:
        fixer_error = str(e)
        console.print(f"[red]Fixer error: {e}[/red]")
        logger.exception("Fixer failed")
        # Continue with validation - don't block on fixer failure

# Attach fixer context (or error context)
if fix_summary:
    result.fixer_context = fix_summary.to_fixer_context(doc_path)
elif fixer_error:
    # Create error context so remediation knows fixer attempted but failed
    from datetime import datetime, timezone
    result.fixer_context = FixerContext(
        session_id="error",
        timestamp=datetime.now(timezone.utc).isoformat(),
        llm_only=[{
            "code": "FIXER-ERROR",
            "file": str(doc_path),
            "reason": f"Fixer failed: {fixer_error}. Manual fixes required."
        }]
    )
```

---

### GAP-TEST-001: Integration Test Specification

**Problem**: Need end-to-end test for full workflow.

**Resolution**: Already covered in `tests/integration/test_fixer_handoff.py`:
- `test_validate_always_creates_section7()` - validates Section 7 creation
- `test_no_fix_flag_skips_section7()` - validates `--no-fix` behavior
- `test_remediation_loads_fixer_context()` - validates context flow
- `test_clean_markers_removes_all()` - validates cleanup
- `test_prompt_injection_format()` - validates prompt formatting

**Add end-to-end CLI test**:
```python
def test_full_cli_workflow(self, tmp_path, cli_runner):
    """Test complete CLI workflow: validate → remediate."""
    from ucx.cli.main import cli

    # Create sample BRD
    brd_dir = tmp_path / "BRD-TEST"
    brd_dir.mkdir()
    # ... setup files ...

    # Step 1: Validate (auto-fixes)
    result = cli_runner.invoke(cli, [
        "validate", "brd", str(brd_dir)
    ])
    assert result.exit_code == 0
    assert "Fixed:" in result.output

    # Step 2: Verify report has Section 7
    report = (brd_dir / ".precommit_validation_report.md").read_text()
    assert "## 7. Fixer Session Summary" in report
    assert "FIXER_CONTEXT_START" in report

    # Step 3: Verify context can be loaded
    from ucx.api.remediation import UCRemPhase
    rem = UCRemPhase()
    ctx = rem._load_fixer_context(brd_dir)
    assert ctx is not None
```

---

### GAP-DOC-001: README Update Specification

**Problem**: README needs update for always-fix behavior.

**Resolution**: Add to `docs/CHANGELOG_v1.17.0.md` README update instructions:

```markdown
## README Updates

Update `/opt/data/docs_flow_framework/UCX/README.md`:

### Quick Start Section
```markdown
## Quick Start

# Validate and auto-fix a BRD (default behavior)
ucx validate brd docs/01_BRD/BRD-01

# Validate only (no fixes)
ucx validate brd docs/01_BRD/BRD-01 --no-fix

# Run AI review after validation
ucx review brd docs/01_BRD/BRD-01

# Run remediation (uses fixer context from validation)
ucx remediate docs/01_BRD/BRD-01
```

### Workflow Section
```markdown
## Workflow

1. **Validate + Fix**: `ucx validate brd BRD-01` (fixes structural issues automatically)
2. **Review**: `ucx review brd BRD-01` (AI-powered content review)
3. **Remediate**: `ucx remediate BRD-01` (AI applies fixes using fixer hand-off context)
4. **Clean up**: `ucx validate clean-markers BRD-01` (removes LLM markers)
```

### Version History Section
```markdown
## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.17.0 | 2026-03-XX | Fixer-to-LLM hand-off, always-fix validation |
| v1.16.2 | 2026-03-15 | Duplicate fixer guardrails |
```
```

---

### GAP-DOC-002: Skills Hand-off Section Location

**Problem**: Specify where to add hand-off protocol in skill files.

**Resolution**: Add after "Role" section, before "Process" section.

**File structure for each skill** (`skills/*.md`):
```markdown
## Role
[Existing role description]

## Fixer Hand-off Protocol  ← INSERT HERE

The script-based fixer (`ucx validate --fix`) runs before LLM remediation.
[... hand-off protocol content ...]

## Process
[Existing process description]
```

**Implementation**: Use grep to find "## Process" in each file and insert before it:
```bash
for skill in architect auditor qa_lead integration_lead chaos_engineer chairperson; do
    FILE="skills/${skill}.md"
    # Find line number of "## Process"
    LINE=$(grep -n "^## Process" "$FILE" | cut -d: -f1)
    # Insert hand-off section before Process
    # ... sed or python script ...
done
```

---

### GAP-CLI-003: clean-markers Command Placement

**Problem**: Clarify `clean-markers` subcommand structure.

**Resolution**: `clean-markers` is a subcommand of `validate`:

```
ucx validate clean-markers <doc_path>
```

**CLI tree**:
```
ucx
├── validate
│   ├── brd <doc_path> [--no-fix] [--no-report]
│   ├── prd <doc_path> [--no-fix] [--no-report]
│   └── clean-markers <doc_path>  ← NEW
├── review
│   └── ...
└── remediate
    └── ...
```

**File: `ucx/cli/main.py`** - Command registration:
```python
@validate.command("clean-markers")
@click.argument("doc_path", type=click.Path(exists=True))
@click.pass_context
def clean_markers(ctx, doc_path: str):
    """Remove LLM_COMPLETION markers from documents.

    After remediation completes semantic fixes, run this command
    to clean up the temporary markers.

    Example:
        ucx validate clean-markers docs/01_BRD/BRD-01
    """
    # ... implementation ...
```

---

### GAP-EDGE-003: File Path Edge Cases

**Problem**: Handle file vs directory paths consistently.

**Resolution**: Add path normalization helper.

**File: `ucx/validators/brd/fixer.py`** (~line 200):
```python
def _normalize_doc_path(self, path: Path) -> Path:
    """Normalize path to always be a directory.

    Args:
        path: File or directory path

    Returns:
        Directory path (parent if file was passed)
    """
    path = Path(path)
    if path.is_file():
        # If a file was passed, use its parent directory
        return path.parent
    return path
```

**Update `__init__`**:
```python
def __init__(self, doc_path: Path, verbose: bool = False):
    self.doc_path = self._normalize_doc_path(Path(doc_path))
    # ... rest of init ...
```

**File: `ucx/api/remediation.py`** (update `_load_fixer_context`):
```python
def _load_fixer_context(self, doc_path: Path) -> Optional[dict]:
    """Load fixer context from validation report.

    Args:
        doc_path: Document path (file or directory)
    """
    doc_path = Path(doc_path)

    # Normalize: if file, look for report in parent
    if doc_path.is_file():
        report_path = doc_path.parent / ".precommit_validation_report.md"
    else:
        report_path = doc_path / ".precommit_validation_report.md"

    # ... rest of method ...
```

---

## Final Gap Summary

| Gap ID | Category | Status |
|--------|----------|--------|
| GAP-CLI-001 | CLI | ✅ Deprecation warning for `--fix` |
| GAP-BC-001 | Docs | ✅ Breaking change in CHANGELOG |
| GAP-BC-002 | Docs | ✅ Pre-commit hook guidance |
| GAP-FLOW-001 | Code | ✅ Import statement specified |
| GAP-FLOW-002 | Code | ✅ Circular import verification |
| GAP-TEST-002 | Test | ✅ CLI option tests added |
| GAP-CLI-002 | CLI | ✅ Help text updated |
| GAP-FLOW-003 | Code | ✅ Prompt injection location specified |
| GAP-EDGE-001 | Code | ✅ Empty FixerContext handling |
| GAP-EDGE-002 | Code | ✅ Fixer error recovery |
| GAP-TEST-001 | Test | ✅ Integration test confirmed |
| GAP-DOC-001 | Docs | ✅ README update specification |
| GAP-DOC-002 | Docs | ✅ Skills section location |
| GAP-CLI-003 | CLI | ✅ clean-markers placement |
| GAP-EDGE-003 | Code | ✅ File path normalization |

---

## Updated Implementation Order

Add to existing implementation steps:

| Step | Phase | Task | File |
|------|-------|------|------|
| 31 | CLI | Add `--fix` deprecation warning | main.py |
| 32 | CLI | Update help text for always-fix | main.py |
| 33 | Code | Add path normalization helper | fixer.py |
| 34 | Code | Add empty FixerContext handling | result.py |
| 35 | Code | Add fixer error recovery | main.py |
| 36 | Test | Add CLI option tests | test_fixer_context.py |
| 37 | Test | Add end-to-end CLI test | test_fixer_handoff.py |
| 38 | Docs | Update README | README.md |
| 39 | Docs | Add breaking change section | CHANGELOG_v1.17.0.md |
| 40 | Docs | Add pre-commit hook guidance | CHANGELOG_v1.17.0.md |

---

## Updated Files to Modify

| File | Additional Changes |
|------|-------------------|
| `ucx/cli/main.py` | +25 lines: deprecation warning, help text, error recovery |
| `ucx/validators/common/result.py` | +15 lines: empty context handling |
| `ucx/validators/brd/fixer.py` | +10 lines: path normalization |
| `tests/unit/test_fixer_context.py` | +30 lines: CLI option tests |
| `tests/integration/test_fixer_handoff.py` | +25 lines: end-to-end CLI test |
| `docs/CHANGELOG_v1.17.0.md` | +40 lines: breaking changes, pre-commit |
| `README.md` | +20 lines: workflow updates |

**Updated Total**: ~360 lines production code + ~275 lines tests
