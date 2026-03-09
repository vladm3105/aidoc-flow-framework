# IPLAN-001: UCX Python Migration

**Document ID**: IPLAN-001
**Title**: UCX Framework Migration from Shell to Python
**Status**: Draft
**Created**: 2026-03-09
**Updated**: 2026-03-09
**Target Completion**: 2026-05-04 (8 weeks)
**New Location**: `/opt/data/docs_flow_framework/UCX/` (moved from `ai_dev_ssd_flow/UCX/`)

---

## 1. Executive Summary

Migrate the UCX (Unified Context) Framework from Bash shell scripts (2,203 LOC) to a Python package providing:
- **API Mode**: Programmatic access via Python classes
- **CLI Mode**: Command-line interface via Click
- **MCP Server Mode**: Model Context Protocol server for AI tool integration
- **Observability**: OpenTelemetry LLM instrumentation with structlog
- **Cross-platform**: Windows, macOS, Linux support
- **Testable**: pytest with 85%+ coverage target

**Directory Relocation**: UCX will be moved to `/opt/data/docs_flow_framework/UCX/` as a root-level component, consistent with `governance/`, `dev_tools/`, and `automation/`.

---

## 2. Objectives

| Objective | Success Criteria |
|-----------|------------------|
| Cross-platform support | Runs on Windows, macOS, Linux |
| API mode | `from ucx import UCXAutopilot` works |
| CLI mode | `ucx autopilot brd docs/` works |
| MCP Server mode | `ucx serve` exposes tools via MCP |
| Observability | OTEL traces for all LLM calls + structlog |
| Feature parity | All shell script features ported |
| Testing | 85%+ code coverage |
| Documentation | API docs + usage guide |
| Packaging | Available via `pip install` |
| Directory migration | UCX at root level of docs_flow_framework |

---

## 3. Architecture Overview

### 3.1 High-Level Architecture

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                              UCX Framework                                     │
├───────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐         │
│  │   CLI Mode  │  │  API Mode   │  │ MCP Server  │  │  Plugin Host  │         │
│  │   (Click)   │  │  (Classes)  │  │  (FastMCP)  │  │  (Registry)   │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └───────┬───────┘         │
│         │                │                │                  │                 │
│         └────────────────┴────────────────┴──────────────────┘                 │
│                                   │                                            │
│  ┌────────────────────────────────┴───────────────────────────────────────┐   │
│  │                      Core Orchestrator                                  │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────────┐        │   │
│  │  │    UCC    │  │    UCR    │  │   UCRem   │  │     Drift     │        │   │
│  │  │ (Create)  │  │ (Review)  │  │(Remediate)│  │   (Monitor)   │        │   │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────────┘        │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                   │                                            │
│  ┌────────────────────────────────┴───────────────────────────────────────┐   │
│  │                       Support Layer                                     │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐        │   │
│  │  │ Prompts  │ │  Skills  │ │Validators│ │ AI Client│ │ Tokens │        │   │
│  │  │ (Jinja2) │ │ (Loader) │ │ (Schema) │ │ (Claude) │ │(Budget)│        │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘        │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                   │                                            │
│  ┌────────────────────────────────┴───────────────────────────────────────┐   │
│  │                    Observability Layer                                  │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌─────────────────────────┐   │   │
│  │  │   structlog    │  │  OTEL Tracing  │  │   OTEL LLM Semantic     │   │   │
│  │  │ (Structured    │  │  (Spans/Ctx)   │  │   Conventions           │   │   │
│  │  │   Logging)     │  │                │  │   (gen_ai.*)            │   │   │
│  │  └────────────────┘  └────────────────┘  └─────────────────────────┘   │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Package Structure

```
ucx/
├── __init__.py                 # Public API exports
├── __main__.py                 # python -m ucx entry point
├── version.py                  # Version info
├── py.typed                    # PEP 561 marker
│
├── api/                        # API Mode (Public Interface)
│   ├── __init__.py             # UCXAutopilot, UCCPhase, UCRPhase, UCRemPhase
│   ├── autopilot.py            # High-level autopilot API
│   ├── creation.py             # UCC API
│   ├── review.py               # UCR API
│   └── remediation.py          # UCRem API
│
├── cli/                        # CLI Mode (Click)
│   ├── __init__.py
│   ├── main.py                 # Main CLI group + all commands
│   └── formatters.py           # Rich output formatters
│
├── mcp/                        # MCP Server Mode
│   ├── __init__.py
│   ├── server.py               # FastMCP server implementation
│   ├── tools.py                # MCP tool definitions
│   └── resources.py            # MCP resource providers
│
├── core/                       # Core Implementation
│   ├── __init__.py
│   ├── orchestrator.py         # Phase orchestration logic
│   ├── ucc.py                  # UCC implementation
│   ├── ucr.py                  # UCR implementation
│   ├── ucrem.py                # UCRem implementation
│   ├── drift.py                # Drift monitoring
│   └── batch.py                # Batch/parallel processing
│
├── config/                     # Configuration
│   ├── __init__.py
│   ├── settings.py             # Pydantic settings
│   ├── defaults.py             # Default values
│   ├── schema.py               # Config file schema
│   └── layer_skills.py         # Layer-to-skills mapping
│
├── models/                     # Data Models
│   ├── __init__.py
│   ├── document.py             # Document model
│   ├── review.py               # Review result model
│   ├── fix.py                  # Fix proposal model
│   ├── drift_cache.py          # Drift cache model
│   └── enums.py                # DocType, Status, Confidence enums
│
├── validators/                 # Document Validators
│   ├── __init__.py
│   ├── base.py                 # Abstract validator
│   ├── registry.py             # Validator registry
│   ├── brd.py                  # BRD validator
│   ├── prd.py                  # PRD validator
│   └── generic.py              # Generic validator
│
├── prompts/                    # Prompt Management
│   ├── __init__.py
│   ├── loader.py               # Prompt loading logic
│   ├── renderer.py             # Jinja2 rendering
│   ├── schema.py               # Template variable schema
│   └── templates/              # Prompt templates
│       ├── ucc/
│       │   ├── base.md.j2
│       │   ├── brd.md.j2
│       │   ├── prd.md.j2
│       │   └── ...
│       ├── ucr/
│       │   ├── base.md.j2
│       │   ├── review.md.j2
│       │   └── ...
│       └── ucrem/
│           ├── base.md.j2
│           ├── fix.md.j2
│           └── ...
│
├── skills/                     # Skill Management
│   ├── __init__.py
│   ├── loader.py               # Skill loading logic
│   ├── injector.py             # Skill injection into prompts
│   └── personas/               # Persona definitions
│       ├── architect.md
│       ├── auditor.md
│       ├── qa_engineer.md
│       └── ...
│
├── ai/                         # AI Client Abstraction
│   ├── __init__.py
│   ├── base.py                 # Abstract AI client
│   ├── claude.py               # Claude implementation
│   ├── mock.py                 # Mock client for testing
│   ├── retry.py                # Retry policies
│   └── tokens.py               # Token counting/budget
│
├── observability/              # Observability (OTEL + structlog)
│   ├── __init__.py
│   ├── logging.py              # structlog configuration
│   ├── tracing.py              # OpenTelemetry tracing setup
│   ├── llm_instrumentation.py  # LLM-specific OTEL instrumentation
│   ├── metrics.py              # OTEL metrics (counters, histograms)
│   └── context.py              # Trace context propagation
│
├── plugins/                    # Plugin System
│   ├── __init__.py
│   ├── base.py                 # Plugin base class
│   ├── registry.py             # Plugin registry
│   └── hooks.py                # Pre/post processing hooks
│
├── utils/                      # Utilities
│   ├── __init__.py
│   ├── logging.py              # Structured logging
│   ├── hash.py                 # SHA256 hashing
│   ├── file_ops.py             # File operations
│   ├── progress.py             # Progress display (Rich)
│   └── async_utils.py          # Async helpers
│
└── exceptions.py               # Custom exceptions
```

---

## 4. API Mode Design

### 4.1 Public API Surface

```python
# ucx/__init__.py
from ucx.api.autopilot import UCXAutopilot
from ucx.api.creation import UCCPhase
from ucx.api.review import UCRPhase
from ucx.api.remediation import UCRemPhase
from ucx.config.settings import UCXConfig
from ucx.models.enums import DocType, Status, Confidence
from ucx.models.document import Document
from ucx.models.review import ReviewResult
from ucx.models.fix import FixProposal
from ucx.plugins.base import UCXPlugin

__all__ = [
    "UCXAutopilot",
    "UCCPhase",
    "UCRPhase",
    "UCRemPhase",
    "UCXConfig",
    "DocType",
    "Status",
    "Confidence",
    "Document",
    "ReviewResult",
    "FixProposal",
    "UCXPlugin",
]
```

### 4.2 UCXAutopilot API

```python
# ucx/api/autopilot.py
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Union, Callable, Awaitable
from enum import Enum

class Status(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NEEDS_MANUAL = "NEEDS_MANUAL"
    DRIFT_DETECTED = "DRIFT_DETECTED"

@dataclass
class AutopilotResult:
    """Result of autopilot execution."""
    status: Status
    score: int
    iterations: int
    drift_detected: bool
    review_report: Path
    fix_report: Optional[Path]
    findings: dict  # {P0: int, P1: int, P2: int}
    elapsed_time: float
    tokens_used: int  # Total tokens consumed
    checkpoint_path: Optional[Path]  # For resume capability

class UCXAutopilot:
    """
    High-level autopilot for document lifecycle management.

    Orchestrates UCC → UCR → UCRem phases automatically.

    Example:
        >>> from ucx import UCXAutopilot, UCXConfig
        >>>
        >>> config = UCXConfig(model="opus", max_iterations=3)
        >>> autopilot = UCXAutopilot(config)
        >>>
        >>> # Generate new document
        >>> result = autopilot.run(
        ...     doc_type="brd",
        ...     target="docs/01_BRD/BRD-01",
        ...     from_ref="docs/00_REF/"
        ... )
        >>> print(f"Score: {result.score}, Status: {result.status}")

        >>> # Review existing document
        >>> result = autopilot.run(
        ...     doc_type="brd",
        ...     target="docs/01_BRD/BRD-01"  # Auto-detects review mode
        ... )
    """

    def __init__(
        self,
        config: Optional["UCXConfig"] = None,
        *,
        model: str = "opus",
        max_iterations: int = 3,
        min_score: int = 90,
        skip_drift: bool = False,
        skill_dir: Optional[Path] = None,
        prompt_dir: Optional[Path] = None,
        token_budget: Optional[int] = None,
    ):
        """
        Initialize autopilot.

        Args:
            config: UCXConfig instance (takes precedence over kwargs)
            model: AI model to use (opus, sonnet, haiku)
            max_iterations: Maximum review/fix cycles
            min_score: Minimum passing score (0-100)
            skip_drift: Disable drift monitoring
            skill_dir: Custom skill definitions directory
            prompt_dir: Custom prompt templates directory
            token_budget: Maximum tokens to consume (None=unlimited)
        """
        ...

    def run(
        self,
        doc_type: Union[str, "DocType"],
        target: Union[str, Path],
        *,
        from_ref: Optional[Union[str, Path]] = None,
        from_upstream: Optional[Union[str, Path]] = None,
        from_iplan: Optional[Union[str, Path]] = None,
        dry_run: bool = False,
        progress_callback: Optional[Callable[[str, int], None]] = None,
        checkpoint: bool = False,
    ) -> AutopilotResult:
        """
        Execute autopilot workflow.

        Args:
            doc_type: Document type (brd, prd, ears, etc.)
            target: Target document path
            from_ref: Reference documents directory
            from_upstream: Upstream artifact path
            from_iplan: Implementation plan path
            dry_run: Show actions without executing
            progress_callback: Optional callback for progress updates
            checkpoint: Enable checkpoint/resume capability

        Returns:
            AutopilotResult with status, score, and artifacts

        Raises:
            UCXError: On validation or execution failure
            FileNotFoundError: If required files are missing
            TokenBudgetExceeded: If token budget is exhausted
        """
        ...

    async def run_async(
        self,
        doc_type: Union[str, "DocType"],
        target: Union[str, Path],
        **kwargs
    ) -> AutopilotResult:
        """Async version of run()."""
        ...

    def run_batch(
        self,
        doc_type: Union[str, "DocType"],
        targets: List[Union[str, Path]],
        *,
        chunk_size: int = 3,
        parallel: bool = False,
        max_workers: int = 3,
        fail_fast: bool = False,
        **kwargs
    ) -> List[AutopilotResult]:
        """
        Process multiple documents.

        Args:
            doc_type: Document type for all targets
            targets: List of target paths
            chunk_size: Number of documents per chunk
            parallel: Enable parallel processing
            max_workers: Max concurrent workers (when parallel=True)
            fail_fast: Stop on first failure
            **kwargs: Additional arguments passed to run()

        Returns:
            List of AutopilotResult for each target
        """
        ...

    async def run_batch_async(
        self,
        doc_type: Union[str, "DocType"],
        targets: List[Union[str, Path]],
        **kwargs
    ) -> List[AutopilotResult]:
        """Async version of run_batch()."""
        ...

    def resume(self, checkpoint_path: Path) -> AutopilotResult:
        """Resume from a checkpoint."""
        ...

    def detect_action(self, target: Path) -> str:
        """
        Detect whether to create or review.

        Returns:
            "create" if target doesn't exist
            "review" if target exists
        """
        ...
```

### 4.3 Phase APIs

```python
# ucx/api/creation.py
class UCCPhase:
    """
    UCC (Unified Context Creation) phase.

    Example:
        >>> from ucx import UCCPhase, UCXConfig
        >>>
        >>> ucc = UCCPhase(UCXConfig())
        >>> doc = ucc.create(
        ...     doc_type="brd",
        ...     output_path="docs/01_BRD/BRD-01",
        ...     from_ref="docs/00_REF/"
        ... )
        >>> print(f"Created: {doc.path}")
    """

    def create(
        self,
        doc_type: Union[str, DocType],
        output_path: Union[str, Path],
        *,
        from_ref: Optional[Path] = None,
        from_upstream: Optional[Path] = None,
        from_iplan: Optional[Path] = None,
        template: Optional[Path] = None,
        multi_file: bool = False,
    ) -> Document:
        """Create a new document."""
        ...

    async def create_async(self, *args, **kwargs) -> Document:
        """Async version of create()."""
        ...

    def get_prompt(
        self,
        doc_type: Union[str, DocType],
        *,
        include_skills: bool = True,
        include_template: bool = True,
    ) -> str:
        """Get the assembled prompt without execution."""
        ...


# ucx/api/review.py
class UCRPhase:
    """
    UCR (Unified Context Review) phase.

    Example:
        >>> from ucx import UCRPhase
        >>>
        >>> ucr = UCRPhase()
        >>> result = ucr.review("brd", "docs/01_BRD/BRD-01")
        >>> print(f"Score: {result.score}, Findings: {result.findings}")
    """

    def review(
        self,
        doc_type: Union[str, DocType],
        doc_path: Union[str, Path],
        *,
        output_path: Optional[Path] = None,
        skip_validation: bool = False,
    ) -> ReviewResult:
        """Review a document."""
        ...

    async def review_async(self, *args, **kwargs) -> ReviewResult:
        """Async version of review()."""
        ...

    def validate(
        self,
        doc_type: Union[str, DocType],
        doc_path: Union[str, Path],
    ) -> ValidationResult:
        """Run validation only (no AI review)."""
        ...


# ucx/api/remediation.py
class UCRemPhase:
    """
    UCRem (Unified Context Remediation) phase.

    Example:
        >>> from ucx import UCRemPhase
        >>>
        >>> ucrem = UCRemPhase()
        >>> fixes = ucrem.generate_fixes(
        ...     review_report="docs/BRD_UCR_REVIEW.md",
        ...     doc_path="docs/01_BRD/BRD-01"
        ... )
        >>> for fix in fixes:
        ...     if fix.confidence == Confidence.AUTO_SAFE:
        ...         fix.apply()
    """

    def generate_fixes(
        self,
        review_report: Union[str, Path],
        doc_path: Union[str, Path],
        *,
        output_path: Optional[Path] = None,
    ) -> List[FixProposal]:
        """Generate fix proposals from review report."""
        ...

    async def generate_fixes_async(self, *args, **kwargs) -> List[FixProposal]:
        """Async version of generate_fixes()."""
        ...

    def apply_fix(
        self,
        fix: FixProposal,
        *,
        dry_run: bool = False,
    ) -> bool:
        """Apply a single fix."""
        ...

    def apply_auto_safe(
        self,
        fixes: List[FixProposal],
        *,
        dry_run: bool = False,
    ) -> List[FixProposal]:
        """Apply all auto-safe fixes, return applied list."""
        ...
```

### 4.4 Data Models

```python
# ucx/models/document.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class Document:
    """Represents a UCX document."""
    path: Path
    doc_type: "DocType"
    doc_id: str
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def exists(self) -> bool:
        """Check if document file exists."""
        return self.path.exists()

    @classmethod
    def from_path(cls, path: Path) -> "Document":
        """Load document from file path."""
        ...

    def read_content(self) -> str:
        """Read document content."""
        ...

    def write_content(self, content: str) -> None:
        """Write document content."""
        ...


# ucx/models/review.py
@dataclass
class ReviewResult:
    """Result of UCR review."""
    doc_path: Path
    report_path: Path
    score: int
    status: Status
    validation_status: str  # PASSED, FAILED, SKIPPED
    findings: Dict[str, int]  # {P0: 2, P1: 5, P2: 3}
    finding_details: Dict[str, List[str]]  # {P0: ["P0-1: desc"], ...}
    raw_content: str
    tokens_used: int

    @property
    def has_critical(self) -> bool:
        """Check if P0 findings exist."""
        return self.findings.get("P0", 0) > 0

    @property
    def total_findings(self) -> int:
        """Total number of findings."""
        return sum(self.findings.values())

    @classmethod
    def from_report(cls, report_path: Path, doc_path: Path) -> "ReviewResult":
        """Parse review result from report file."""
        ...

    def get_findings_by_priority(self, priority: "Priority") -> List[str]:
        """Extract finding IDs for a priority level."""
        ...


# ucx/models/fix.py
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
    fix_action: "FixAction"
    rationale: str
    validated_by: List[str]
    verification: Optional[str] = None

    @property
    def can_auto_apply(self) -> bool:
        """Check if fix can be auto-applied."""
        return self.confidence == Confidence.AUTO_SAFE

    @property
    def needs_review(self) -> bool:
        """Check if fix needs manual review."""
        return self.confidence == Confidence.MANUAL_REQUIRED

    def apply(self, dry_run: bool = False) -> bool:
        """Apply this fix to the target file."""
        ...

    def to_yaml(self) -> str:
        """Serialize to YAML format."""
        ...

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "FixProposal":
        """Deserialize from YAML format."""
        ...


# ucx/models/drift_cache.py
@dataclass
class UpstreamDoc:
    """Tracked upstream document."""
    path: str
    hash: str
    last_modified: datetime
    size: int

@dataclass
class DriftCache:
    """Drift detection cache."""
    schema_version: str = "1.1"
    document_id: str = ""
    document_version: str = "1.0"
    upstream_mode: str = "none"
    drift_detection_skipped: bool = False
    last_reviewed: datetime = field(default_factory=datetime.now)
    reviewer_version: str = "UCX-2.0"
    upstream_documents: Dict[str, UpstreamDoc] = field(default_factory=dict)
    review_history: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def latest_score(self) -> Optional[int]:
        """Get most recent review score."""
        if self.review_history:
            return self.review_history[-1].get("score")
        return None

    @classmethod
    def load(cls, path: Path) -> "DriftCache":
        """Load from JSON file."""
        ...

    def save(self, path: Path) -> None:
        """Save to JSON file."""
        ...

    def add_review(self, score: int, status: str, drift_detected: bool) -> None:
        """Add review entry to history."""
        ...

    def track_upstream(self, upstream_path: Path) -> None:
        """Track an upstream document for drift detection."""
        ...

    def check_drift(self, upstream_path: Path) -> Tuple[bool, List[str]]:
        """
        Check if upstream has changed.

        Returns:
            Tuple of (has_drift, list_of_changed_files)
        """
        ...
```

### 4.5 Configuration

```python
# ucx/config/settings.py
from pydantic import Field
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

class RetryConfig(BaseSettings):
    """Retry policy configuration."""
    max_attempts: int = Field(3, description="Maximum retry attempts")
    base_delay: float = Field(1.0, description="Base delay in seconds")
    max_delay: float = Field(60.0, description="Maximum delay in seconds")
    exponential_base: float = Field(2.0, description="Exponential backoff base")

class TokenConfig(BaseSettings):
    """Token budget configuration."""
    max_input_tokens: int = Field(100000, description="Max input tokens per request")
    max_output_tokens: int = Field(8000, description="Max output tokens per request")
    budget_per_session: Optional[int] = Field(None, description="Total token budget")
    truncation_strategy: str = Field("smart", description="smart|head|tail")

class UCXConfig(BaseSettings):
    """UCX configuration with environment variable support."""

    # AI Model
    model: str = Field("opus", env="UCX_MODEL")

    # Autopilot
    max_iterations: int = Field(3, env="UCX_MAX_ITER")
    min_score: int = Field(90, env="UCX_MIN_SCORE")
    batch_size: int = Field(3, env="UCX_BATCH_SIZE")

    # Drift Monitoring
    skip_drift: bool = Field(False, env="UCX_SKIP_DRIFT")
    hash_algorithm: str = Field("sha256", env="UCX_HASH_ALG")

    # Skill Loading
    load_skills: bool = Field(True, env="UCX_LOAD_SKILLS")
    skill_dir: Optional[Path] = Field(None, env="UCX_SKILL_DIR")

    # Prompts
    prompt_dir: Optional[Path] = Field(None, env="UCX_PROMPT_DIR")
    template_dir: Optional[Path] = Field(None, env="UCX_TEMPLATE_DIR")

    # Logging (structlog)
    log_level: str = Field("INFO", env="UCX_LOG_LEVEL")
    log_format: str = Field("json", env="UCX_LOG_FORMAT")  # json | console
    log_file: Optional[Path] = Field(None, env="UCX_LOG_FILE")

    # OpenTelemetry
    otel_enabled: bool = Field(True, env="UCX_OTEL_ENABLED")
    otel_endpoint: Optional[str] = Field(None, env="OTEL_EXPORTER_OTLP_ENDPOINT")
    otel_service_name: str = Field("ucx", env="OTEL_SERVICE_NAME")
    otel_llm_capture_content: bool = Field(False, env="UCX_OTEL_CAPTURE_CONTENT")

    # Output
    output_dir: Optional[Path] = Field(None, env="UCX_OUTPUT_DIR")

    # Retry Policy
    retry: RetryConfig = Field(default_factory=RetryConfig)

    # Token Budget
    tokens: TokenConfig = Field(default_factory=TokenConfig)

    # Parallel Processing
    max_workers: int = Field(3, env="UCX_MAX_WORKERS")

    # Checkpointing
    enable_checkpoints: bool = Field(False, env="UCX_CHECKPOINTS")
    checkpoint_dir: Optional[Path] = Field(None, env="UCX_CHECKPOINT_DIR")

    class Config:
        env_file = ".env"
        env_prefix = ""
        extra = "ignore"

    @classmethod
    def from_yaml(cls, path: Path) -> "UCXConfig":
        """Load configuration from YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def to_yaml(self, path: Path) -> None:
        """Save configuration to YAML file."""
        with open(path, "w") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)
```

### 4.6 Configuration File Schema

**Project configuration file: `ucx.yaml` or `.ucxrc`**

```yaml
# ucx.yaml - Project-level UCX configuration
# Location: project root

# AI Model Settings
model: opus                    # opus | sonnet | haiku
max_iterations: 3              # Max review/fix cycles
min_score: 90                  # Minimum passing score (0-100)

# Drift Monitoring
skip_drift: false              # Disable drift detection
hash_algorithm: sha256         # sha256 | md5

# Skill Loading
load_skills: true              # Enable skill injection
skill_dir: null                # Custom skills directory (null = built-in)

# Prompts
prompt_dir: null               # Custom prompts directory
template_dir: null             # Custom templates directory

# Output
output_dir: null               # Output directory (null = alongside source)

# Logging
log_level: INFO                # DEBUG | INFO | WARNING | ERROR
log_format: console            # console | json

# Retry Policy
retry:
  max_attempts: 3
  base_delay: 1.0
  max_delay: 60.0
  exponential_base: 2.0

# Token Budget
tokens:
  max_input_tokens: 100000
  max_output_tokens: 8000
  budget_per_session: null     # null = unlimited
  truncation_strategy: smart   # smart | head | tail

# Parallel Processing
max_workers: 3                 # Max concurrent workers
batch_size: 3                  # Documents per batch

# Checkpointing
enable_checkpoints: false
checkpoint_dir: .ucx_checkpoints
```

---

## 5. CLI Mode Design

### 5.1 Command Structure

```
ucx
├── autopilot     # Full UCC → UCR → UCRem cycle
├── create        # UCC phase only
├── review        # UCR phase only
├── remediate     # UCRem phase only
├── validate      # Validation only (no AI)
├── drift         # Drift monitoring commands
│   ├── check     # Check for drift
│   ├── update    # Update drift cache
│   └── status    # Show drift status
├── serve         # Start MCP server
├── init          # Initialize UCX in project
├── config        # Show/edit configuration
│   ├── show      # Display current config
│   ├── set       # Set config value
│   └── init      # Create config file
└── version       # Show version info
```

### 5.2 CLI Implementation

```python
# ucx/cli/main.py
import click
from rich.console import Console
from pathlib import Path

console = Console()

@click.group()
@click.version_option()
@click.option("--config", "-c", type=click.Path(exists=True), help="Config file")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Minimal output")
@click.pass_context
def cli(ctx, config, verbose, quiet):
    """UCX - Unified Context Framework for document lifecycle management."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    if config:
        ctx.obj["config"] = UCXConfig.from_yaml(Path(config))
    else:
        ctx.obj["config"] = UCXConfig()


@cli.command()
@click.argument("doc_type")
@click.argument("target", type=click.Path())
@click.option("--from-ref", type=click.Path(exists=True), help="Reference docs")
@click.option("--from-upstream", type=click.Path(exists=True), help="Upstream artifact")
@click.option("--from-iplan", type=click.Path(), help="Implementation plan")
@click.option("--max-iterations", default=3, help="Max review/fix cycles")
@click.option("--min-score", default=90, help="Minimum passing score")
@click.option("--skip-drift", is_flag=True, help="Skip drift monitoring")
@click.option("--dry-run", is_flag=True, help="Show actions without executing")
@click.option("--checkpoint", is_flag=True, help="Enable checkpoint/resume")
@click.option("--resume", type=click.Path(exists=True), help="Resume from checkpoint")
@click.pass_context
def autopilot(ctx, doc_type, target, resume, **kwargs):
    """
    Run full autopilot cycle (UCC → UCR → UCRem).

    \b
    Examples:
      ucx autopilot brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/
      ucx autopilot prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01
      ucx autopilot brd docs/01_BRD/ --batch  # Process all BRDs in directory
    """
    from ucx import UCXAutopilot
    from ucx.cli.formatters import display_autopilot_result

    config = ctx.obj["config"]
    pilot = UCXAutopilot(config)

    if resume:
        result = pilot.resume(Path(resume))
    else:
        result = pilot.run(doc_type=doc_type, target=Path(target), **kwargs)

    display_autopilot_result(result, console)


@cli.command()
@click.option("--host", default="localhost", help="Server host")
@click.option("--port", default=8765, help="Server port")
@click.option("--transport", type=click.Choice(["stdio", "http"]), default="stdio")
@click.pass_context
def serve(ctx, host, port, transport):
    """
    Start UCX MCP server.

    \b
    Examples:
      ucx serve                          # stdio transport (default)
      ucx serve --transport http --port 8765
    """
    from ucx.mcp.server import UCXMCPServer

    server = UCXMCPServer(ctx.obj["config"])
    server.run(host=host, port=port, transport=transport)


@cli.group()
def drift():
    """Drift monitoring commands."""
    pass


@drift.command("check")
@click.argument("doc_path", type=click.Path(exists=True))
@click.pass_context
def drift_check(ctx, doc_path):
    """Check document for upstream drift."""
    from ucx.core.drift import DriftMonitor

    monitor = DriftMonitor()
    has_drift, changed = monitor.check(Path(doc_path))

    if has_drift:
        console.print(f"[yellow]⚠ Drift detected[/yellow]")
        for f in changed:
            console.print(f"  Changed: {f}")
    else:
        console.print(f"[green]✓ No drift[/green]")


@cli.group()
def config():
    """Configuration commands."""
    pass


@config.command("show")
@click.pass_context
def config_show(ctx):
    """Display current configuration."""
    from rich.table import Table

    table = Table(title="UCX Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    cfg = ctx.obj["config"]
    for key, value in cfg.model_dump().items():
        table.add_row(key, str(value))

    console.print(table)


@config.command("init")
@click.option("--force", is_flag=True, help="Overwrite existing config")
@click.pass_context
def config_init(ctx, force):
    """Create ucx.yaml configuration file."""
    config_path = Path("ucx.yaml")

    if config_path.exists() and not force:
        console.print("[red]Config file exists. Use --force to overwrite.[/red]")
        return

    UCXConfig().to_yaml(config_path)
    console.print(f"[green]Created {config_path}[/green]")
```

### 5.3 CLI Output Formatters

```python
# ucx/cli/formatters.py
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

def display_autopilot_result(result: "AutopilotResult", console: Console):
    """Display autopilot result with rich formatting."""
    table = Table(title="Autopilot Result")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green" if result.status.value == "PASS" else "red")

    table.add_row("Status", result.status.value)
    table.add_row("Score", f"{result.score}/100")
    table.add_row("Iterations", str(result.iterations))
    table.add_row("Drift Detected", "Yes" if result.drift_detected else "No")
    table.add_row("P0 Findings", str(result.findings.get("P0", 0)))
    table.add_row("P1 Findings", str(result.findings.get("P1", 0)))
    table.add_row("P2 Findings", str(result.findings.get("P2", 0)))
    table.add_row("Tokens Used", f"{result.tokens_used:,}")
    table.add_row("Elapsed Time", f"{result.elapsed_time:.2f}s")

    console.print(table)
    console.print(f"\nReview Report: {result.review_report}")
    if result.fix_report:
        console.print(f"Fix Report: {result.fix_report}")


def create_progress_bar(console: Console) -> Progress:
    """Create a rich progress bar for autopilot phases."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    )
```

---

## 6. MCP Server Mode Design

### 6.1 Overview

The MCP (Model Context Protocol) server exposes UCX functionality as tools that can be invoked by AI models like Claude.

### 6.2 MCP Server Implementation

```python
# ucx/mcp/server.py
from mcp.server.fastmcp import FastMCP
from pathlib import Path
from typing import Optional

class UCXMCPServer:
    """MCP Server for UCX Framework."""

    def __init__(self, config: "UCXConfig"):
        self.config = config
        self.mcp = FastMCP("UCX Framework")
        self._register_tools()
        self._register_resources()

    def _register_tools(self):
        """Register MCP tools."""

        @self.mcp.tool()
        def ucx_autopilot(
            doc_type: str,
            target: str,
            from_ref: Optional[str] = None,
            from_upstream: Optional[str] = None,
            max_iterations: int = 3,
            min_score: int = 90,
        ) -> dict:
            """
            Run UCX autopilot workflow for document creation/review/remediation.

            Args:
                doc_type: Document type (brd, prd, ears, bdd, adr, sys, req, ctr, spec, tspec)
                target: Target document path
                from_ref: Reference documents directory
                from_upstream: Upstream artifact path
                max_iterations: Maximum review/fix cycles
                min_score: Minimum passing score

            Returns:
                AutopilotResult with status, score, and artifacts
            """
            from ucx import UCXAutopilot

            pilot = UCXAutopilot(
                self.config,
                max_iterations=max_iterations,
                min_score=min_score,
            )

            result = pilot.run(
                doc_type=doc_type,
                target=Path(target),
                from_ref=Path(from_ref) if from_ref else None,
                from_upstream=Path(from_upstream) if from_upstream else None,
            )

            return {
                "status": result.status.value,
                "score": result.score,
                "iterations": result.iterations,
                "drift_detected": result.drift_detected,
                "review_report": str(result.review_report),
                "fix_report": str(result.fix_report) if result.fix_report else None,
                "findings": result.findings,
            }

        @self.mcp.tool()
        def ucx_create(
            doc_type: str,
            output_path: str,
            from_ref: Optional[str] = None,
            from_upstream: Optional[str] = None,
        ) -> dict:
            """
            Create a new document using UCX UCC phase.

            Args:
                doc_type: Document type
                output_path: Output document path
                from_ref: Reference documents directory
                from_upstream: Upstream artifact path

            Returns:
                Created document information
            """
            from ucx import UCCPhase

            ucc = UCCPhase(self.config)
            doc = ucc.create(
                doc_type=doc_type,
                output_path=Path(output_path),
                from_ref=Path(from_ref) if from_ref else None,
                from_upstream=Path(from_upstream) if from_upstream else None,
            )

            return {
                "path": str(doc.path),
                "doc_id": doc.doc_id,
                "doc_type": doc.doc_type.value,
            }

        @self.mcp.tool()
        def ucx_review(
            doc_type: str,
            doc_path: str,
        ) -> dict:
            """
            Review a document using UCX UCR phase.

            Args:
                doc_type: Document type
                doc_path: Document path to review

            Returns:
                Review result with score and findings
            """
            from ucx import UCRPhase

            ucr = UCRPhase(self.config)
            result = ucr.review(doc_type=doc_type, doc_path=Path(doc_path))

            return {
                "score": result.score,
                "status": result.status.value,
                "findings": result.findings,
                "has_critical": result.has_critical,
                "report_path": str(result.report_path),
            }

        @self.mcp.tool()
        def ucx_check_drift(doc_path: str) -> dict:
            """
            Check document for upstream drift.

            Args:
                doc_path: Document path to check

            Returns:
                Drift detection result
            """
            from ucx.core.drift import DriftMonitor

            monitor = DriftMonitor()
            has_drift, changed = monitor.check(Path(doc_path))

            return {
                "has_drift": has_drift,
                "changed_files": changed,
            }

    def _register_resources(self):
        """Register MCP resources."""

        @self.mcp.resource("ucx://config")
        def get_config() -> str:
            """Get current UCX configuration."""
            import yaml
            return yaml.dump(self.config.model_dump())

        @self.mcp.resource("ucx://doc-types")
        def get_doc_types() -> str:
            """Get supported document types."""
            from ucx.models.enums import DocType
            return "\n".join([f"{dt.value}: {dt.display_name}" for dt in DocType])

    def run(self, host: str = "localhost", port: int = 8765, transport: str = "stdio"):
        """Run the MCP server."""
        if transport == "stdio":
            self.mcp.run()
        else:
            self.mcp.run(transport="streamable-http", host=host, port=port)
```

### 6.3 MCP Tool Definitions

| Tool | Description | Parameters |
|------|-------------|------------|
| `ucx_autopilot` | Full UCC→UCR→UCRem cycle | doc_type, target, from_ref, from_upstream, max_iterations, min_score |
| `ucx_create` | Create document (UCC) | doc_type, output_path, from_ref, from_upstream |
| `ucx_review` | Review document (UCR) | doc_type, doc_path |
| `ucx_remediate` | Generate fixes (UCRem) | review_report, doc_path |
| `ucx_check_drift` | Check for upstream drift | doc_path |
| `ucx_validate` | Validate document structure | doc_type, doc_path |

---

## 7. Prompt Migration Strategy

### 7.1 Overview

Migrate existing `.md` prompts to Jinja2 templates for dynamic rendering.

### 7.2 Template Variable Schema

```python
# ucx/prompts/schema.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class UCCContext(BaseModel):
    """Context variables for UCC prompts."""
    doc_type: str
    doc_type_full: str  # Full name (e.g., "Business Requirements Document")
    layer: int
    target_path: str
    ref_content: Optional[str] = None
    upstream_content: Optional[str] = None
    iplan_content: Optional[str] = None
    template_content: Optional[str] = None
    skills: List[str] = []
    custom_instructions: Optional[str] = None

class UCRContext(BaseModel):
    """Context variables for UCR prompts."""
    doc_type: str
    doc_type_full: str
    layer: int
    doc_path: str
    doc_content: str
    validation_results: Optional[str] = None
    skills: List[str] = []
    previous_score: Optional[int] = None
    iteration: int = 1

class UCRemContext(BaseModel):
    """Context variables for UCRem prompts."""
    doc_type: str
    doc_path: str
    doc_content: str
    review_content: str
    findings: Dict[str, List[str]]  # {P0: [...], P1: [...], P2: [...]}
    skills: List[str] = []
    iteration: int = 1
```

### 7.3 Template Structure

```jinja2
{# ucx/prompts/templates/ucc/base.md.j2 #}
# UCC: Create {{ doc_type_full }}

You are creating a **{{ doc_type_full }}** (Layer {{ layer }}) document.

## Target
- Output Path: `{{ target_path }}`
- Document ID: `{{ doc_id }}`

{% if skills %}
## Expert Personas
{% for skill in skills %}
{{ skill }}
{% endfor %}
{% endif %}

{% if ref_content %}
## Reference Documents
{{ ref_content }}
{% endif %}

{% if upstream_content %}
## Upstream Artifact
{{ upstream_content }}
{% endif %}

{% if template_content %}
## Template
{{ template_content }}
{% endif %}

## Instructions
{{ instructions }}

{% block doc_specific %}{% endblock %}
```

```jinja2
{# ucx/prompts/templates/ucc/brd.md.j2 #}
{% extends "ucc/base.md.j2" %}

{% block doc_specific %}
## BRD-Specific Requirements

1. Include Executive Summary with business justification
2. Define stakeholders and their concerns
3. Include all BRD.XX.XX.XX requirement IDs
4. Add Constraints and Assumptions section
5. Include Compliance and Regulatory requirements
{% endblock %}
```

### 7.4 Migration Script

```python
# scripts/migrate_prompts.py
"""
Migrate shell script prompts to Jinja2 templates.

Usage:
    python scripts/migrate_prompts.py --source creation/ --output ucx/prompts/templates/
"""

import re
from pathlib import Path
from typing import Dict, List

VARIABLE_PATTERNS = {
    r'\$\{DOC_TYPE\}': '{{ doc_type }}',
    r'\$\{DOC_TYPE_FULL\}': '{{ doc_type_full }}',
    r'\$\{LAYER\}': '{{ layer }}',
    r'\$\{TARGET_PATH\}': '{{ target_path }}',
    r'\$\{REF_CONTENT\}': '{{ ref_content }}',
    r'\$\{UPSTREAM_CONTENT\}': '{{ upstream_content }}',
    r'\$DOC_TYPE': '{{ doc_type }}',
    r'\$LAYER': '{{ layer }}',
}

def migrate_prompt(source: Path, output: Path) -> None:
    """Migrate a single prompt file."""
    content = source.read_text()

    # Replace shell variables with Jinja2
    for pattern, replacement in VARIABLE_PATTERNS.items():
        content = re.sub(pattern, replacement, content)

    # Add Jinja2 conditionals for optional sections
    content = add_conditionals(content)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content)
    print(f"Migrated: {source} -> {output}")

def add_conditionals(content: str) -> str:
    """Add Jinja2 conditionals for optional sections."""
    # Example: wrap skill injection
    if "## Expert Personas" in content:
        content = content.replace(
            "## Expert Personas",
            "{% if skills %}\n## Expert Personas\n{% for skill in skills %}\n{{ skill }}\n{% endfor %}\n{% endif %}"
        )
    return content

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    for prompt_file in args.source.glob("**/*.md"):
        relative = prompt_file.relative_to(args.source)
        output_file = args.output / relative.with_suffix(".md.j2")
        migrate_prompt(prompt_file, output_file)

if __name__ == "__main__":
    main()
```

---

## 8. Skill Migration Strategy

### 8.1 Persona File Format

```markdown
<!-- ucx/skills/personas/architect.md -->
# Architect Persona

## Role
You are a Senior Software Architect with expertise in:
- System design and architecture patterns
- Technical decision-making
- Scalability and performance
- Security best practices

## Review Focus
- Architectural consistency
- Design pattern adherence
- Scalability concerns
- Technical feasibility

## Quality Criteria
- Clear separation of concerns
- Appropriate abstraction levels
- Consistent naming conventions
- Documented trade-offs
```

### 8.2 Skill Loader

```python
# ucx/skills/loader.py
from pathlib import Path
from typing import List, Dict, Optional
import re

class SkillLoader:
    """Load and manage persona skills."""

    def __init__(self, skill_dir: Optional[Path] = None):
        self.skill_dir = skill_dir or Path(__file__).parent / "personas"
        self._cache: Dict[str, str] = {}

    def load(self, skill_name: str) -> str:
        """Load a skill by name."""
        if skill_name in self._cache:
            return self._cache[skill_name]

        skill_path = self.skill_dir / f"{skill_name}.md"
        if not skill_path.exists():
            raise FileNotFoundError(f"Skill not found: {skill_name}")

        content = skill_path.read_text()
        self._cache[skill_name] = content
        return content

    def load_for_layer(self, layer: int) -> List[str]:
        """Load all skills for a document layer."""
        from ucx.config.layer_skills import LAYER_SKILLS

        skill_names = LAYER_SKILLS.get(layer, [])
        return [self.load(name) for name in skill_names]

    def list_available(self) -> List[str]:
        """List all available skills."""
        return [p.stem for p in self.skill_dir.glob("*.md")]
```

### 8.3 Skill Injector

```python
# ucx/skills/injector.py
from typing import List, Optional

class SkillInjector:
    """Inject skills into prompts."""

    def __init__(self, loader: "SkillLoader"):
        self.loader = loader

    def inject(
        self,
        prompt: str,
        skills: List[str],
        position: str = "after_header"
    ) -> str:
        """
        Inject skills into a prompt.

        Args:
            prompt: Base prompt content
            skills: Skill content strings
            position: Where to inject (after_header, before_instructions, end)

        Returns:
            Prompt with injected skills
        """
        if not skills:
            return prompt

        skill_section = "\n## Expert Personas\n\n"
        for skill in skills:
            skill_section += f"{skill}\n\n---\n\n"

        if position == "after_header":
            # Insert after first heading
            lines = prompt.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("# "):
                    lines.insert(i + 1, skill_section)
                    break
            return "\n".join(lines)

        elif position == "end":
            return prompt + "\n" + skill_section

        return prompt
```

### 8.4 Layer-to-Skill Mapping

```python
# ucx/config/layer_skills.py
"""Mapping of document layers to required skills."""

LAYER_SKILLS = {
    1: ["architect", "business_analyst"],           # BRD
    2: ["architect", "product_owner", "qa_engineer"],  # PRD
    3: ["requirements_engineer", "qa_engineer"],    # EARS
    4: ["qa_engineer", "test_architect"],           # BDD
    5: ["architect", "technical_lead"],             # ADR
    6: ["systems_engineer", "architect"],           # SYS
    7: ["requirements_engineer", "systems_engineer"],  # REQ
    8: ["data_architect", "api_designer"],          # CTR
    9: ["technical_lead", "developer"],             # SPEC
    10: ["qa_engineer", "test_architect"],          # TSPEC
}

SKILL_DESCRIPTIONS = {
    "architect": "Senior Software Architect",
    "business_analyst": "Business Analyst",
    "product_owner": "Product Owner",
    "qa_engineer": "QA Engineer",
    "requirements_engineer": "Requirements Engineer",
    "test_architect": "Test Architect",
    "technical_lead": "Technical Lead",
    "systems_engineer": "Systems Engineer",
    "data_architect": "Data Architect",
    "api_designer": "API Designer",
    "developer": "Senior Developer",
}
```

---

## 9. Token Budget Management

### 9.1 Token Counter

```python
# ucx/ai/tokens.py
from typing import Optional, Tuple
import tiktoken

class TokenCounter:
    """Count and manage tokens."""

    def __init__(self, model: str = "claude-3-opus"):
        # Use cl100k_base as approximation for Claude
        self._encoding = tiktoken.get_encoding("cl100k_base")
        self._model = model

    def count(self, text: str) -> int:
        """Count tokens in text."""
        return len(self._encoding.encode(text))

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate API cost in USD."""
        # Approximate pricing (update as needed)
        PRICING = {
            "claude-3-opus": (15.0, 75.0),      # per 1M tokens (input, output)
            "claude-3-sonnet": (3.0, 15.0),
            "claude-3-haiku": (0.25, 1.25),
        }

        input_price, output_price = PRICING.get(self._model, (15.0, 75.0))
        return (input_tokens * input_price + output_tokens * output_price) / 1_000_000


class TokenBudget:
    """Manage token budget for a session."""

    def __init__(self, budget: Optional[int] = None):
        self.budget = budget
        self.used = 0
        self.history: list = []

    def consume(self, tokens: int, operation: str) -> None:
        """Record token consumption."""
        self.used += tokens
        self.history.append({"operation": operation, "tokens": tokens})

        if self.budget and self.used > self.budget:
            raise TokenBudgetExceeded(
                f"Token budget exceeded: {self.used}/{self.budget}"
            )

    @property
    def remaining(self) -> Optional[int]:
        """Get remaining tokens."""
        if self.budget is None:
            return None
        return max(0, self.budget - self.used)

    def can_proceed(self, estimated_tokens: int) -> bool:
        """Check if operation can proceed within budget."""
        if self.budget is None:
            return True
        return self.used + estimated_tokens <= self.budget
```

### 9.2 Content Truncation

```python
# ucx/ai/tokens.py (continued)

class ContentTruncator:
    """Truncate content to fit token limits."""

    def __init__(self, counter: TokenCounter):
        self.counter = counter

    def truncate(
        self,
        content: str,
        max_tokens: int,
        strategy: str = "smart"
    ) -> Tuple[str, bool]:
        """
        Truncate content to fit within token limit.

        Args:
            content: Content to truncate
            max_tokens: Maximum tokens allowed
            strategy: Truncation strategy (smart|head|tail|middle)

        Returns:
            Tuple of (truncated_content, was_truncated)
        """
        current_tokens = self.counter.count(content)

        if current_tokens <= max_tokens:
            return content, False

        if strategy == "head":
            return self._truncate_head(content, max_tokens), True
        elif strategy == "tail":
            return self._truncate_tail(content, max_tokens), True
        elif strategy == "middle":
            return self._truncate_middle(content, max_tokens), True
        else:  # smart
            return self._truncate_smart(content, max_tokens), True

    def _truncate_smart(self, content: str, max_tokens: int) -> str:
        """Smart truncation preserving structure."""
        lines = content.split("\n")

        # Keep headers and first/last paragraphs
        important_lines = []
        regular_lines = []

        for line in lines:
            if line.startswith("#") or line.startswith("---"):
                important_lines.append(line)
            else:
                regular_lines.append(line)

        # Build result keeping important content
        result = "\n".join(important_lines)
        remaining_tokens = max_tokens - self.counter.count(result) - 50  # buffer

        # Add regular lines until limit
        for line in regular_lines:
            line_tokens = self.counter.count(line)
            if remaining_tokens >= line_tokens:
                result += "\n" + line
                remaining_tokens -= line_tokens
            else:
                break

        result += "\n\n[... content truncated ...]"
        return result

    def _truncate_head(self, content: str, max_tokens: int) -> str:
        """Keep beginning of content."""
        words = content.split()
        result = []
        tokens = 0

        for word in words:
            word_tokens = self.counter.count(word + " ")
            if tokens + word_tokens > max_tokens - 20:
                break
            result.append(word)
            tokens += word_tokens

        return " ".join(result) + "\n[... truncated ...]"

    def _truncate_tail(self, content: str, max_tokens: int) -> str:
        """Keep end of content."""
        words = content.split()
        result = []
        tokens = 0

        for word in reversed(words):
            word_tokens = self.counter.count(word + " ")
            if tokens + word_tokens > max_tokens - 20:
                break
            result.insert(0, word)
            tokens += word_tokens

        return "[... truncated ...]\n" + " ".join(result)
```

---

## 10. Observability: OTEL LLM & Structlog

### 10.1 Overview

UCX implements comprehensive observability using:
- **OpenTelemetry (OTEL)**: Distributed tracing with LLM semantic conventions
- **structlog**: Structured logging with context propagation
- **Metrics**: Token usage, latency, and error rate tracking

### 10.2 Structlog Configuration

```python
# ucx/observability/logging.py
import structlog
import logging
import sys
from typing import Optional
from pathlib import Path

def configure_structlog(
    level: str = "INFO",
    format: str = "json",
    log_file: Optional[Path] = None,
    add_trace_context: bool = True,
) -> None:
    """
    Configure structlog for UCX.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        format: Output format (json, console)
        log_file: Optional file path for log output
        add_trace_context: Include OTEL trace/span IDs in logs
    """
    # Shared processors for all outputs
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    # Add OTEL trace context if enabled
    if add_trace_context:
        shared_processors.insert(0, add_otel_context)

    # Format-specific processors
    if format == "json":
        final_processors = [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:  # console
        final_processors = [
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=shared_processors + final_processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=log_level,
    )

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        logging.getLogger().addHandler(file_handler)


def add_otel_context(logger, method_name, event_dict):
    """Add OpenTelemetry trace context to log records."""
    from opentelemetry import trace

    span = trace.get_current_span()
    if span.is_recording():
        ctx = span.get_span_context()
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")

    return event_dict


def get_logger(name: str = "ucx") -> structlog.stdlib.BoundLogger:
    """Get a structlog logger instance."""
    return structlog.get_logger(name)


# Context managers for structured logging
class LogContext:
    """Context manager for adding context to logs."""

    def __init__(self, **context):
        self.context = context
        self.token = None

    def __enter__(self):
        self.token = structlog.contextvars.bind_contextvars(**self.context)
        return self

    def __exit__(self, *args):
        structlog.contextvars.unbind_contextvars(*self.context.keys())
```

### 10.3 OpenTelemetry Tracing Setup

```python
# ucx/observability/tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as OTLPHttpExporter
from typing import Optional

def configure_tracing(
    service_name: str = "ucx",
    endpoint: Optional[str] = None,
    use_http: bool = False,
) -> trace.Tracer:
    """
    Configure OpenTelemetry tracing.

    Args:
        service_name: Service name for traces
        endpoint: OTLP endpoint (None = no export, just in-memory)
        use_http: Use HTTP exporter instead of gRPC

    Returns:
        Configured tracer instance
    """
    resource = Resource.create({
        SERVICE_NAME: service_name,
        "service.version": "1.0.0",
        "deployment.environment": "development",
    })

    provider = TracerProvider(resource=resource)

    if endpoint:
        if use_http:
            exporter = OTLPHttpExporter(endpoint=endpoint)
        else:
            exporter = OTLPSpanExporter(endpoint=endpoint)

        provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)
    return trace.get_tracer("ucx")


def get_tracer() -> trace.Tracer:
    """Get the UCX tracer instance."""
    return trace.get_tracer("ucx")
```

### 10.4 LLM Instrumentation (OTEL Semantic Conventions)

```python
# ucx/observability/llm_instrumentation.py
"""
OpenTelemetry LLM Semantic Conventions for UCX.

Follows the OTEL GenAI semantic conventions:
https://opentelemetry.io/docs/specs/semconv/gen-ai/
"""

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from functools import wraps
from typing import Optional, Dict, Any, Callable
import time

# OTEL GenAI Semantic Convention attribute names
GEN_AI_SYSTEM = "gen_ai.system"
GEN_AI_REQUEST_MODEL = "gen_ai.request.model"
GEN_AI_REQUEST_MAX_TOKENS = "gen_ai.request.max_tokens"
GEN_AI_REQUEST_TEMPERATURE = "gen_ai.request.temperature"
GEN_AI_REQUEST_TOP_P = "gen_ai.request.top_p"
GEN_AI_RESPONSE_ID = "gen_ai.response.id"
GEN_AI_RESPONSE_MODEL = "gen_ai.response.model"
GEN_AI_RESPONSE_FINISH_REASONS = "gen_ai.response.finish_reasons"
GEN_AI_USAGE_INPUT_TOKENS = "gen_ai.usage.input_tokens"
GEN_AI_USAGE_OUTPUT_TOKENS = "gen_ai.usage.output_tokens"
GEN_AI_OPERATION_NAME = "gen_ai.operation.name"

# UCX-specific attributes
UCX_DOC_TYPE = "ucx.doc_type"
UCX_PHASE = "ucx.phase"
UCX_ITERATION = "ucx.iteration"
UCX_SCORE = "ucx.score"


class LLMInstrumentor:
    """Instrument LLM calls with OpenTelemetry."""

    def __init__(
        self,
        tracer: Optional[trace.Tracer] = None,
        capture_content: bool = False,
    ):
        """
        Initialize LLM instrumentor.

        Args:
            tracer: OTEL tracer (uses default if None)
            capture_content: Whether to capture prompt/response content
                             (disabled by default for privacy)
        """
        self.tracer = tracer or trace.get_tracer("ucx.llm")
        self.capture_content = capture_content

    def instrument_call(
        self,
        func: Callable,
        operation: str = "chat",
        model: str = "claude-3-opus",
    ) -> Callable:
        """
        Decorator to instrument an LLM call.

        Args:
            func: Function making the LLM call
            operation: Operation name (chat, create, review, etc.)
            model: Model name
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.tracer.start_as_current_span(
                f"gen_ai.{operation}",
                kind=trace.SpanKind.CLIENT,
            ) as span:
                # Set request attributes
                span.set_attribute(GEN_AI_SYSTEM, "anthropic")
                span.set_attribute(GEN_AI_REQUEST_MODEL, model)
                span.set_attribute(GEN_AI_OPERATION_NAME, operation)

                if "max_tokens" in kwargs:
                    span.set_attribute(GEN_AI_REQUEST_MAX_TOKENS, kwargs["max_tokens"])
                if "temperature" in kwargs:
                    span.set_attribute(GEN_AI_REQUEST_TEMPERATURE, kwargs["temperature"])

                # Capture prompt content if enabled
                if self.capture_content and "prompt" in kwargs:
                    span.add_event("gen_ai.content.prompt", {
                        "gen_ai.prompt": kwargs["prompt"][:10000]  # Truncate
                    })

                start_time = time.perf_counter()

                try:
                    result = func(*args, **kwargs)

                    # Set response attributes
                    elapsed = time.perf_counter() - start_time
                    span.set_attribute("gen_ai.response.latency_ms", elapsed * 1000)

                    if hasattr(result, "id"):
                        span.set_attribute(GEN_AI_RESPONSE_ID, result.id)
                    if hasattr(result, "model"):
                        span.set_attribute(GEN_AI_RESPONSE_MODEL, result.model)
                    if hasattr(result, "stop_reason"):
                        span.set_attribute(GEN_AI_RESPONSE_FINISH_REASONS, [result.stop_reason])

                    # Token usage
                    if hasattr(result, "usage"):
                        span.set_attribute(GEN_AI_USAGE_INPUT_TOKENS, result.usage.input_tokens)
                        span.set_attribute(GEN_AI_USAGE_OUTPUT_TOKENS, result.usage.output_tokens)

                    # Capture response content if enabled
                    if self.capture_content and hasattr(result, "content"):
                        content = result.content[0].text if result.content else ""
                        span.add_event("gen_ai.content.completion", {
                            "gen_ai.completion": content[:10000]
                        })

                    span.set_status(Status(StatusCode.OK))
                    return result

                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        return wrapper

    def create_ucx_span(
        self,
        name: str,
        phase: str,
        doc_type: str,
        iteration: int = 1,
        **attributes
    ) -> trace.Span:
        """
        Create a UCX-specific span for phase tracking.

        Args:
            name: Span name
            phase: UCX phase (ucc, ucr, ucrem)
            doc_type: Document type
            iteration: Iteration number
            **attributes: Additional attributes
        """
        span = self.tracer.start_span(name)
        span.set_attribute(UCX_PHASE, phase)
        span.set_attribute(UCX_DOC_TYPE, doc_type)
        span.set_attribute(UCX_ITERATION, iteration)

        for key, value in attributes.items():
            span.set_attribute(f"ucx.{key}", value)

        return span


# Decorator for easy instrumentation
def trace_llm_call(
    operation: str = "chat",
    model: str = "claude-3-opus",
    capture_content: bool = False,
):
    """Decorator to trace LLM calls."""
    instrumentor = LLMInstrumentor(capture_content=capture_content)

    def decorator(func):
        return instrumentor.instrument_call(func, operation, model)

    return decorator
```

### 10.5 Metrics Collection

```python
# ucx/observability/metrics.py
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from typing import Optional

def configure_metrics(
    service_name: str = "ucx",
    endpoint: Optional[str] = None,
) -> metrics.Meter:
    """Configure OpenTelemetry metrics."""
    if endpoint:
        exporter = OTLPMetricExporter(endpoint=endpoint)
        reader = PeriodicExportingMetricReader(exporter, export_interval_millis=60000)
        provider = MeterProvider(metric_readers=[reader])
    else:
        provider = MeterProvider()

    metrics.set_meter_provider(provider)
    return metrics.get_meter("ucx")


class UCXMetrics:
    """UCX-specific metrics."""

    def __init__(self, meter: Optional[metrics.Meter] = None):
        self.meter = meter or metrics.get_meter("ucx")

        # Counters
        self.llm_calls = self.meter.create_counter(
            "ucx.llm.calls",
            description="Number of LLM API calls",
            unit="1",
        )

        self.tokens_used = self.meter.create_counter(
            "ucx.llm.tokens",
            description="Total tokens consumed",
            unit="1",
        )

        self.documents_processed = self.meter.create_counter(
            "ucx.documents.processed",
            description="Documents processed",
            unit="1",
        )

        # Histograms
        self.llm_latency = self.meter.create_histogram(
            "ucx.llm.latency",
            description="LLM call latency",
            unit="ms",
        )

        self.review_score = self.meter.create_histogram(
            "ucx.review.score",
            description="Review scores",
            unit="1",
        )

        # Gauges (using UpDownCounter)
        self.active_sessions = self.meter.create_up_down_counter(
            "ucx.sessions.active",
            description="Active UCX sessions",
            unit="1",
        )

    def record_llm_call(
        self,
        model: str,
        phase: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
        success: bool = True,
    ):
        """Record metrics for an LLM call."""
        labels = {
            "model": model,
            "phase": phase,
            "status": "success" if success else "error",
        }

        self.llm_calls.add(1, labels)
        self.tokens_used.add(input_tokens + output_tokens, {"type": "total", **labels})
        self.tokens_used.add(input_tokens, {"type": "input", **labels})
        self.tokens_used.add(output_tokens, {"type": "output", **labels})
        self.llm_latency.record(latency_ms, labels)

    def record_document(self, doc_type: str, phase: str, score: Optional[int] = None):
        """Record document processing metrics."""
        self.documents_processed.add(1, {"doc_type": doc_type, "phase": phase})
        if score is not None:
            self.review_score.record(score, {"doc_type": doc_type})
```

### 10.6 Integration with AI Client

```python
# ucx/ai/claude.py (updated with instrumentation)
from anthropic import Anthropic
from ucx.observability.llm_instrumentation import trace_llm_call, LLMInstrumentor
from ucx.observability.logging import get_logger, LogContext
from ucx.observability.metrics import UCXMetrics
import time

log = get_logger("ucx.ai")

class ClaudeClient:
    """Claude API client with full observability."""

    def __init__(self, config: "UCXConfig"):
        self.client = Anthropic()
        self.config = config
        self.instrumentor = LLMInstrumentor(
            capture_content=config.otel_llm_capture_content
        )
        self.metrics = UCXMetrics()

    @trace_llm_call(operation="chat")
    def chat(
        self,
        prompt: str,
        *,
        model: str = "claude-3-opus-20240229",
        max_tokens: int = 8000,
        temperature: float = 0.0,
        phase: str = "unknown",
        doc_type: str = "unknown",
    ):
        """Send chat request with full instrumentation."""
        start = time.perf_counter()

        with LogContext(phase=phase, doc_type=doc_type, model=model):
            log.info("llm_request_start", prompt_length=len(prompt))

            try:
                response = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}],
                )

                elapsed_ms = (time.perf_counter() - start) * 1000

                # Record metrics
                self.metrics.record_llm_call(
                    model=model,
                    phase=phase,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    latency_ms=elapsed_ms,
                    success=True,
                )

                log.info(
                    "llm_request_complete",
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    latency_ms=elapsed_ms,
                    stop_reason=response.stop_reason,
                )

                return response

            except Exception as e:
                elapsed_ms = (time.perf_counter() - start) * 1000
                log.error("llm_request_failed", error=str(e), latency_ms=elapsed_ms)
                self.metrics.record_llm_call(
                    model=model,
                    phase=phase,
                    input_tokens=0,
                    output_tokens=0,
                    latency_ms=elapsed_ms,
                    success=False,
                )
                raise
```

### 10.7 Configuration Example

```yaml
# ucx.yaml - Observability configuration

# Structured Logging (structlog)
log_level: INFO                    # DEBUG | INFO | WARNING | ERROR
log_format: json                   # json | console
log_file: null                     # Optional file path

# OpenTelemetry
otel_enabled: true                 # Enable/disable OTEL
otel_endpoint: "http://localhost:4317"  # OTLP gRPC endpoint
otel_service_name: ucx             # Service name in traces

# LLM Instrumentation
otel_llm_capture_content: false    # Capture prompt/response (privacy!)
```

### 10.8 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `UCX_LOG_LEVEL` | Log level | INFO |
| `UCX_LOG_FORMAT` | Log format (json/console) | json |
| `UCX_LOG_FILE` | Log file path | None |
| `UCX_OTEL_ENABLED` | Enable OTEL | true |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP endpoint | None |
| `OTEL_SERVICE_NAME` | Service name | ucx |
| `UCX_OTEL_CAPTURE_CONTENT` | Capture LLM content | false |

---

## 11. Error Recovery Strategy

### 10.1 Retry Policies

```python
# ucx/ai/retry.py
import asyncio
import random
from typing import TypeVar, Callable, Optional
from functools import wraps

T = TypeVar("T")

class RetryPolicy:
    """Configurable retry policy with exponential backoff."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: tuple = (Exception,),
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for attempt number."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)

        if self.jitter:
            delay *= (0.5 + random.random())

        return delay

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator for sync functions."""
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(self.max_attempts):
                try:
                    return func(*args, **kwargs)
                except self.retryable_exceptions as e:
                    last_exception = e
                    if attempt < self.max_attempts - 1:
                        delay = self.get_delay(attempt)
                        import time
                        time.sleep(delay)

            raise last_exception

        return wrapper

    def async_retry(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator for async functions."""
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(self.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except self.retryable_exceptions as e:
                    last_exception = e
                    if attempt < self.max_attempts - 1:
                        delay = self.get_delay(attempt)
                        await asyncio.sleep(delay)

            raise last_exception

        return wrapper


# Default retry policy for AI calls
AI_RETRY_POLICY = RetryPolicy(
    max_attempts=3,
    base_delay=2.0,
    max_delay=60.0,
    retryable_exceptions=(
        ConnectionError,
        TimeoutError,
        # Add anthropic-specific exceptions
    ),
)
```

### 10.2 Checkpoint/Resume

```python
# ucx/core/checkpoint.py
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Any, Dict

@dataclass
class Checkpoint:
    """Checkpoint state for resumable operations."""
    checkpoint_id: str
    created_at: str
    doc_type: str
    target: str
    phase: str  # "ucc" | "ucr" | "ucrem"
    iteration: int
    state: Dict[str, Any]
    partial_results: Dict[str, Any]

    @classmethod
    def create(cls, doc_type: str, target: str) -> "Checkpoint":
        """Create new checkpoint."""
        import uuid
        return cls(
            checkpoint_id=str(uuid.uuid4()),
            created_at=datetime.now().isoformat(),
            doc_type=doc_type,
            target=target,
            phase="ucc",
            iteration=0,
            state={},
            partial_results={},
        )

    def save(self, checkpoint_dir: Path) -> Path:
        """Save checkpoint to disk."""
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        path = checkpoint_dir / f"{self.checkpoint_id}.json"

        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)

        return path

    @classmethod
    def load(cls, path: Path) -> "Checkpoint":
        """Load checkpoint from disk."""
        with open(path) as f:
            data = json.load(f)
        return cls(**data)

    def update(
        self,
        phase: Optional[str] = None,
        iteration: Optional[int] = None,
        state: Optional[Dict] = None,
        partial_results: Optional[Dict] = None,
    ) -> None:
        """Update checkpoint state."""
        if phase:
            self.phase = phase
        if iteration is not None:
            self.iteration = iteration
        if state:
            self.state.update(state)
        if partial_results:
            self.partial_results.update(partial_results)


class CheckpointManager:
    """Manage checkpoints for resumable operations."""

    def __init__(self, checkpoint_dir: Path):
        self.checkpoint_dir = checkpoint_dir

    def create(self, doc_type: str, target: str) -> Checkpoint:
        """Create and save a new checkpoint."""
        cp = Checkpoint.create(doc_type, target)
        cp.save(self.checkpoint_dir)
        return cp

    def load(self, checkpoint_id: str) -> Checkpoint:
        """Load checkpoint by ID."""
        path = self.checkpoint_dir / f"{checkpoint_id}.json"
        return Checkpoint.load(path)

    def list_checkpoints(self) -> list:
        """List all checkpoints."""
        return [
            Checkpoint.load(p)
            for p in self.checkpoint_dir.glob("*.json")
        ]

    def cleanup_old(self, max_age_days: int = 7) -> int:
        """Remove checkpoints older than max_age_days."""
        cutoff = datetime.now().timestamp() - (max_age_days * 86400)
        removed = 0

        for path in self.checkpoint_dir.glob("*.json"):
            if path.stat().st_mtime < cutoff:
                path.unlink()
                removed += 1

        return removed
```

### 10.3 Partial Failure Handling

```python
# ucx/core/batch.py
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class BatchResult:
    """Result of batch processing."""
    total: int
    succeeded: int
    failed: int
    results: List["AutopilotResult"]
    failures: List[dict]  # [{target, error, traceback}, ...]

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        return self.succeeded / self.total if self.total > 0 else 0.0


class BatchProcessor:
    """Process multiple documents with failure handling."""

    def __init__(
        self,
        config: "UCXConfig",
        max_workers: int = 3,
        fail_fast: bool = False,
    ):
        self.config = config
        self.max_workers = max_workers
        self.fail_fast = fail_fast

    def process(
        self,
        doc_type: str,
        targets: List[Path],
        **kwargs
    ) -> BatchResult:
        """Process multiple targets with parallel execution."""
        from ucx import UCXAutopilot

        results = []
        failures = []

        pilot = UCXAutopilot(self.config)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_target = {
                executor.submit(pilot.run, doc_type, target, **kwargs): target
                for target in targets
            }

            for future in as_completed(future_to_target):
                target = future_to_target[future]

                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    import traceback
                    failures.append({
                        "target": str(target),
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    })

                    if self.fail_fast:
                        # Cancel remaining futures
                        for f in future_to_target:
                            f.cancel()
                        break

        return BatchResult(
            total=len(targets),
            succeeded=len(results),
            failed=len(failures),
            results=results,
            failures=failures,
        )
```

---

## 11. Plugin System

### 11.1 Plugin Base Class

```python
# ucx/plugins/base.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class UCXPlugin(ABC):
    """Base class for UCX plugins."""

    name: str = "unnamed_plugin"
    version: str = "1.0.0"

    @abstractmethod
    def initialize(self, config: "UCXConfig") -> None:
        """Initialize plugin with configuration."""
        pass

    def pre_create(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Hook before document creation."""
        return context

    def post_create(self, document: "Document", context: Dict[str, Any]) -> None:
        """Hook after document creation."""
        pass

    def pre_review(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Hook before document review."""
        return context

    def post_review(self, result: "ReviewResult", context: Dict[str, Any]) -> None:
        """Hook after document review."""
        pass

    def pre_remediate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Hook before remediation."""
        return context

    def post_remediate(self, fixes: list, context: Dict[str, Any]) -> None:
        """Hook after remediation."""
        pass

    def on_error(self, error: Exception, context: Dict[str, Any]) -> Optional[Exception]:
        """Handle errors. Return None to suppress, or modified exception."""
        return error
```

### 11.2 Plugin Registry

```python
# ucx/plugins/registry.py
from typing import Dict, List, Type, Optional
from pathlib import Path
import importlib.util

class PluginRegistry:
    """Registry for UCX plugins."""

    def __init__(self):
        self._plugins: Dict[str, "UCXPlugin"] = {}

    def register(self, plugin: "UCXPlugin") -> None:
        """Register a plugin instance."""
        self._plugins[plugin.name] = plugin

    def unregister(self, name: str) -> None:
        """Unregister a plugin by name."""
        self._plugins.pop(name, None)

    def get(self, name: str) -> Optional["UCXPlugin"]:
        """Get plugin by name."""
        return self._plugins.get(name)

    def list_plugins(self) -> List[str]:
        """List registered plugin names."""
        return list(self._plugins.keys())

    def load_from_directory(self, plugin_dir: Path) -> int:
        """Load plugins from a directory."""
        loaded = 0

        for path in plugin_dir.glob("*.py"):
            if path.name.startswith("_"):
                continue

            spec = importlib.util.spec_from_file_location(path.stem, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find UCXPlugin subclasses
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, UCXPlugin)
                    and attr is not UCXPlugin
                ):
                    plugin = attr()
                    self.register(plugin)
                    loaded += 1

        return loaded

    def call_hook(self, hook_name: str, *args, **kwargs) -> Any:
        """Call a hook on all plugins."""
        results = []

        for plugin in self._plugins.values():
            hook = getattr(plugin, hook_name, None)
            if hook and callable(hook):
                result = hook(*args, **kwargs)
                results.append(result)

        return results
```

---

## 12. Async/Parallel Execution

### 12.1 Async Utilities

```python
# ucx/utils/async_utils.py
import asyncio
from typing import List, TypeVar, Callable, Awaitable
from concurrent.futures import ThreadPoolExecutor

T = TypeVar("T")

async def run_in_thread(func: Callable[..., T], *args, **kwargs) -> T:
    """Run sync function in thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


async def gather_with_concurrency(
    n: int,
    coros: List[Awaitable[T]],
) -> List[T]:
    """Run coroutines with limited concurrency."""
    semaphore = asyncio.Semaphore(n)

    async def limited_coro(coro: Awaitable[T]) -> T:
        async with semaphore:
            return await coro

    return await asyncio.gather(*[limited_coro(c) for c in coros])


async def process_batch_async(
    items: List[T],
    processor: Callable[[T], Awaitable],
    max_concurrency: int = 3,
    fail_fast: bool = False,
) -> List:
    """Process items in parallel with concurrency limit."""
    results = []
    errors = []
    semaphore = asyncio.Semaphore(max_concurrency)

    async def process_item(item: T, index: int):
        async with semaphore:
            try:
                result = await processor(item)
                return (index, result, None)
            except Exception as e:
                return (index, None, e)

    tasks = [
        asyncio.create_task(process_item(item, i))
        for i, item in enumerate(items)
    ]

    if fail_fast:
        # Return on first error
        for coro in asyncio.as_completed(tasks):
            idx, result, error = await coro
            if error:
                # Cancel remaining tasks
                for task in tasks:
                    task.cancel()
                raise error
            results.append((idx, result))
    else:
        # Collect all results
        completed = await asyncio.gather(*tasks, return_exceptions=True)
        for idx, result, error in completed:
            if error:
                errors.append((idx, error))
            else:
                results.append((idx, result))

    # Sort by original index
    results.sort(key=lambda x: x[0])
    return [r for _, r in results], errors
```

---

## 13. CI/CD Configuration

### 13.1 GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run linting
        run: |
          ruff check ucx tests
          ruff format --check ucx tests

      - name: Run type checking
        run: mypy ucx

      - name: Run tests
        run: pytest --cov=ucx --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  release:
    needs: test
    if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install build tools
        run: pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          generate_release_notes: true
```

### 13.2 Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.2.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies:
          - pydantic>=2.0
          - types-PyYAML

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

---

## 14. Documentation Structure

### 14.1 Documentation Directory

```
docs/
├── index.md                    # Home page
├── getting-started/
│   ├── installation.md
│   ├── quickstart.md
│   └── configuration.md
├── user-guide/
│   ├── cli-reference.md
│   ├── api-usage.md
│   ├── mcp-server.md
│   ├── batch-processing.md
│   └── plugins.md
├── api/
│   ├── autopilot.md
│   ├── creation.md
│   ├── review.md
│   ├── remediation.md
│   ├── models.md
│   └── config.md
├── migration/
│   ├── from-shell-scripts.md
│   └── prompt-migration.md
└── development/
    ├── contributing.md
    ├── architecture.md
    └── testing.md
```

### 14.2 MkDocs Configuration

```yaml
# mkdocs.yml
site_name: UCX Framework
site_description: Unified Context Framework for AI-driven document lifecycle management
repo_url: https://github.com/example/ucx
repo_name: example/ucx

theme:
  name: material
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.tabs
    - search.suggest
    - content.code.copy

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
            show_root_heading: true

nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Quickstart: getting-started/quickstart.md
    - Configuration: getting-started/configuration.md
  - User Guide:
    - CLI Reference: user-guide/cli-reference.md
    - API Usage: user-guide/api-usage.md
    - MCP Server: user-guide/mcp-server.md
    - Batch Processing: user-guide/batch-processing.md
    - Plugins: user-guide/plugins.md
  - API Reference:
    - UCXAutopilot: api/autopilot.md
    - UCCPhase: api/creation.md
    - UCRPhase: api/review.md
    - UCRemPhase: api/remediation.md
    - Models: api/models.md
    - Configuration: api/config.md
  - Migration:
    - From Shell Scripts: migration/from-shell-scripts.md
    - Prompt Migration: migration/prompt-migration.md
  - Development:
    - Contributing: development/contributing.md
    - Architecture: development/architecture.md
    - Testing: development/testing.md

markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
  - pymdownx.tabbed
  - admonition
  - toc:
      permalink: true
```

---

## 15. Implementation Phases (Updated)

### Phase 0: Design Completion (Week 0.5)

**Tasks**:
- [ ] Finalize MCP tool specifications
- [ ] Complete prompt template schema
- [ ] Define all exception types
- [ ] Create migration scripts for prompts/skills

**Deliverables**:
- `ucx/mcp/tools.py` (specification only)
- `ucx/prompts/schema.py`
- `scripts/migrate_prompts.py`
- `scripts/migrate_skills.py`

### Phase 1: Foundation & Observability (Week 1)

**Tasks**:
- [ ] Set up Python package structure with pyproject.toml
- [ ] Implement UCXConfig with Pydantic (including retry, token, OTEL config)
- [ ] Implement structlog configuration with OTEL context
- [ ] Implement OpenTelemetry tracing setup
- [ ] Implement OTEL metrics collection
- [ ] Implement file operation utilities
- [ ] Implement hash computation utilities
- [ ] Create base exceptions
- [ ] Create defaults.py with all default values
- [ ] Set up pytest infrastructure

**Deliverables**:
- `pyproject.toml`
- `ucx/__init__.py`, `ucx/__main__.py`, `ucx/version.py`, `ucx/py.typed`
- `ucx/config/settings.py`, `ucx/config/defaults.py`, `ucx/config/schema.py`
- `ucx/observability/__init__.py`, `ucx/observability/logging.py`
- `ucx/observability/tracing.py`, `ucx/observability/metrics.py`
- `ucx/observability/context.py`
- `ucx/utils/hash.py`, `ucx/utils/file_ops.py`
- `ucx/exceptions.py`
- `tests/__init__.py`, `tests/conftest.py`
- `tests/unit/__init__.py`, `tests/unit/test_config.py`, `tests/unit/test_observability.py`

### Phase 2: Models & Validators (Week 2)

**Tasks**:
- [ ] Implement Document model with from_path, read/write
- [ ] Implement ReviewResult model with parsing
- [ ] Implement FixProposal model with YAML serialization
- [ ] Implement DriftCache model with full drift detection
- [ ] Implement all enums (DocType, Status, Confidence, Priority, FixType)
- [ ] Port BRD validator
- [ ] Port PRD validator
- [ ] Implement generic validator
- [ ] Create validator registry

**Deliverables**:
- `ucx/models/__init__.py`, `ucx/models/document.py`, `ucx/models/review.py`
- `ucx/models/fix.py`, `ucx/models/drift_cache.py`, `ucx/models/enums.py`
- `ucx/validators/__init__.py`, `ucx/validators/base.py`, `ucx/validators/registry.py`
- `ucx/validators/brd.py`, `ucx/validators/prd.py`, `ucx/validators/generic.py`
- `tests/unit/test_models.py`, `tests/unit/test_validators.py`

### Phase 3: Prompts & Skills (Week 2-3)

**Tasks**:
- [ ] Implement prompt loader
- [ ] Implement Jinja2 renderer with schema validation
- [ ] Run migration script for all UCC prompts
- [ ] Run migration script for all UCR prompts
- [ ] Run migration script for all UCRem prompts
- [ ] Implement skill loader
- [ ] Implement skill injector
- [ ] Migrate all persona skills
- [ ] Create layer_skills.py mapping

**Deliverables**:
- `ucx/prompts/__init__.py`, `ucx/prompts/loader.py`, `ucx/prompts/renderer.py`
- `ucx/prompts/schema.py`
- `ucx/prompts/templates/ucc/*.md.j2` (all document types)
- `ucx/prompts/templates/ucr/*.md.j2`
- `ucx/prompts/templates/ucrem/*.md.j2`
- `ucx/skills/__init__.py`, `ucx/skills/loader.py`, `ucx/skills/injector.py`
- `ucx/skills/personas/*.md` (all personas)
- `ucx/config/layer_skills.py`
- `tests/unit/test_prompts.py`, `tests/unit/test_skills.py`

### Phase 4: AI Client, Token Management & LLM Instrumentation (Week 3)

**Tasks**:
- [ ] Implement abstract AI client interface
- [ ] Implement Claude client using anthropic SDK
- [ ] Implement mock client for testing
- [ ] Implement retry policies with exponential backoff
- [ ] Implement token counter
- [ ] Implement token budget management
- [ ] Implement content truncation strategies
- [ ] Implement OTEL LLM instrumentation (gen_ai.* semantic conventions)
- [ ] Integrate structlog with AI client

**Deliverables**:
- `ucx/ai/__init__.py`, `ucx/ai/base.py`, `ucx/ai/claude.py`, `ucx/ai/mock.py`
- `ucx/ai/retry.py`, `ucx/ai/tokens.py`
- `ucx/observability/llm_instrumentation.py`
- `tests/unit/test_ai_client.py`, `tests/unit/test_tokens.py`
- `tests/unit/test_llm_instrumentation.py`

### Phase 5: Core Phases (Week 3-4)

**Tasks**:
- [ ] Implement UCC phase with prompt assembly
- [ ] Implement UCR phase with validation integration
- [ ] Implement UCRem phase with fix generation
- [ ] Implement drift monitoring
- [ ] Implement orchestrator logic
- [ ] Implement batch processor
- [ ] Implement checkpoint/resume

**Deliverables**:
- `ucx/core/__init__.py`, `ucx/core/orchestrator.py`
- `ucx/core/ucc.py`, `ucx/core/ucr.py`, `ucx/core/ucrem.py`
- `ucx/core/drift.py`, `ucx/core/batch.py`, `ucx/core/checkpoint.py`
- `tests/unit/test_core_ucc.py`, `tests/unit/test_core_ucr.py`
- `tests/unit/test_core_ucrem.py`, `tests/unit/test_drift.py`

### Phase 6: API Layer (Week 4)

**Tasks**:
- [ ] Implement UCXAutopilot API with all methods
- [ ] Implement UCCPhase API with async support
- [ ] Implement UCRPhase API with async support
- [ ] Implement UCRemPhase API with async support
- [ ] Add progress callbacks
- [ ] Add batch processing with parallel support
- [ ] Implement async utilities

**Deliverables**:
- `ucx/api/__init__.py`, `ucx/api/autopilot.py`
- `ucx/api/creation.py`, `ucx/api/review.py`, `ucx/api/remediation.py`
- `ucx/utils/async_utils.py`, `ucx/utils/progress.py`
- `tests/integration/__init__.py`, `tests/integration/test_api.py`

### Phase 7: CLI & MCP Server (Week 5)

**Tasks**:
- [ ] Implement main CLI group with all global options
- [ ] Implement autopilot command with resume support
- [ ] Implement create, review, remediate commands
- [ ] Implement drift subcommands
- [ ] Implement config subcommands
- [ ] Implement init command
- [ ] Add rich progress display
- [ ] Add shell completion
- [ ] Implement MCP server with FastMCP
- [ ] Register all MCP tools
- [ ] Register MCP resources

**Deliverables**:
- `ucx/cli/__init__.py`, `ucx/cli/main.py`, `ucx/cli/formatters.py`
- `ucx/mcp/__init__.py`, `ucx/mcp/server.py`, `ucx/mcp/tools.py`, `ucx/mcp/resources.py`
- `tests/integration/test_cli.py`, `tests/integration/test_mcp.py`

### Phase 8: Plugin System (Week 5)

**Tasks**:
- [ ] Implement plugin base class
- [ ] Implement plugin registry
- [ ] Implement hook system
- [ ] Add plugin loading from directory
- [ ] Document plugin API

**Deliverables**:
- `ucx/plugins/__init__.py`, `ucx/plugins/base.py`
- `ucx/plugins/registry.py`, `ucx/plugins/hooks.py`
- `tests/unit/test_plugins.py`

### Phase 9: Testing & Documentation (Week 6)

**Tasks**:
- [ ] Achieve 85%+ test coverage
- [ ] Add integration tests with mock AI
- [ ] Add end-to-end tests
- [ ] Write API documentation (mkdocs)
- [ ] Write user guide
- [ ] Write migration guide from shell scripts
- [ ] Add type hints throughout (mypy strict)
- [ ] Create test fixtures

**Deliverables**:
- `docs/` (full documentation structure)
- `mkdocs.yml`
- `tests/integration/test_end_to_end.py`
- `tests/fixtures/` (sample files)
- Coverage report > 85%

### Phase 10: Release (Week 7)

**Tasks**:
- [ ] Create shell script wrappers for backward compatibility
- [ ] Set up GitHub Actions CI/CD
- [ ] Configure pre-commit hooks
- [ ] Publish to PyPI
- [ ] Create release notes
- [ ] Update framework documentation

**Deliverables**:
- `bin/run_ucx_autopilot.sh`, `bin/run_ucc.sh`, `bin/run_ucr.sh`, `bin/run_ucrem.sh`
- `.github/workflows/ci.yml`
- `.pre-commit-config.yaml`
- PyPI package `ucx`
- GitHub release v1.0.0

---

## 16. Dependencies

### Runtime Dependencies

```toml
[project]
dependencies = [
    "click>=8.1",           # CLI framework
    "pydantic>=2.0",        # Data validation
    "pydantic-settings>=2.0", # Settings management
    "rich>=13.0",           # Terminal formatting
    "pyyaml>=6.0",          # YAML parsing
    "jinja2>=3.1",          # Template rendering
    "anthropic>=0.18",      # Claude API client
    "structlog>=24.0",      # Structured logging
    "tiktoken>=0.5",        # Token counting
    "mcp>=1.0",             # Model Context Protocol
    # OpenTelemetry (OTEL) for observability
    "opentelemetry-api>=1.20",
    "opentelemetry-sdk>=1.20",
    "opentelemetry-exporter-otlp>=1.20",
    "opentelemetry-instrumentation>=0.41b0",
]
```

### Development Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=4.1",
    "pytest-mock>=3.12",
    "mypy>=1.8",
    "ruff>=0.2",
    "pre-commit>=3.6",
    "opentelemetry-test-utils>=0.41b0",  # OTEL testing utilities
]
docs = [
    "mkdocs>=1.5",
    "mkdocs-material>=9.5",
    "mkdocstrings[python]>=0.24",
]
```

---

## 17. Testing Strategy

### 17.1 Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_models.py
│   ├── test_validators.py
│   ├── test_prompts.py
│   ├── test_skills.py
│   ├── test_ai_client.py
│   ├── test_tokens.py
│   ├── test_retry.py
│   ├── test_hash.py
│   ├── test_drift.py
│   ├── test_core_ucc.py
│   ├── test_core_ucr.py
│   ├── test_core_ucrem.py
│   ├── test_checkpoint.py
│   ├── test_plugins.py
│   ├── test_structlog.py        # structlog configuration tests
│   ├── test_otel_tracing.py     # OTEL tracing tests
│   ├── test_otel_metrics.py     # OTEL metrics tests
│   └── test_llm_instrumentation.py  # LLM instrumentation tests
├── integration/
│   ├── __init__.py
│   ├── test_api_autopilot.py
│   ├── test_api_phases.py
│   ├── test_cli.py
│   ├── test_mcp.py
│   ├── test_observability.py    # Full observability integration
│   └── test_end_to_end.py
└── fixtures/
    ├── sample_brd.md
    ├── sample_prd.md
    ├── sample_review_report.md
    ├── sample_fix_report.md
    ├── sample_drift_cache.json
    └── sample_config.yaml
```

### 17.2 Coverage Targets

| Module | Target Coverage |
|--------|-----------------|
| `config/` | 95% |
| `models/` | 95% |
| `validators/` | 90% |
| `utils/` | 90% |
| `ai/` | 90% |
| `observability/` | 90% |
| `prompts/` | 85% |
| `skills/` | 85% |
| `core/` | 85% |
| `api/` | 85% |
| `cli/` | 80% |
| `mcp/` | 80% |
| `plugins/` | 85% |
| **Overall** | **85%** |

---

## 18. Backward Compatibility

### 18.1 Shell Script Wrappers

```bash
#!/usr/bin/env bash
# bin/run_ucx_autopilot.sh
# Backward-compatible wrapper for legacy shell script users

exec python -m ucx autopilot "$@"
```

```bash
#!/usr/bin/env bash
# bin/run_ucc.sh
exec python -m ucx create "$@"
```

```bash
#!/usr/bin/env bash
# bin/run_ucr.sh
exec python -m ucx review "$@"
```

```bash
#!/usr/bin/env bash
# bin/run_ucrem.sh
exec python -m ucx remediate "$@"
```

### 18.2 Environment Variable Compatibility

All existing environment variables remain supported:
- `UCX_MODEL`
- `UCX_MAX_ITER`
- `UCX_MIN_SCORE`
- `UCX_SKIP_DRIFT`
- `UCR_LOAD_SKILLS`
- `UCREM_LOAD_SKILLS`

---

## 19. Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Claude API changes | Low | High | Abstract AI client interface |
| Feature parity gaps | Medium | High | Comprehensive test suite |
| Performance regression | Low | Medium | Benchmark critical paths |
| User adoption | Medium | Medium | Backward-compatible wrappers |
| Dependency conflicts | Low | Medium | Pin versions in pyproject.toml |
| Token budget overruns | Medium | Medium | Budget management + truncation |
| MCP protocol changes | Low | Medium | Abstract MCP layer |
| Parallel execution bugs | Medium | High | Thorough async testing |

---

## 20. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test coverage | > 85% | pytest-cov |
| Type coverage | > 90% | mypy --strict |
| Platform support | Windows + macOS + Linux | CI matrix |
| API response time | < 100ms (excl. AI) | Benchmark tests |
| CLI startup time | < 500ms | Benchmark tests |
| Documentation | 100% public API | mkdocs build |
| MCP tool response | < 50ms (excl. AI) | Benchmark tests |

---

## 21. Appendix: API Quick Reference

### Import Patterns

```python
# Full autopilot
from ucx import UCXAutopilot, UCXConfig
autopilot = UCXAutopilot(UCXConfig(model="opus"))
result = autopilot.run("brd", "docs/01_BRD/BRD-01", from_ref="docs/00_REF/")

# Async autopilot
result = await autopilot.run_async("brd", "docs/01_BRD/BRD-01")

# Batch processing
results = autopilot.run_batch("brd", ["BRD-01", "BRD-02"], parallel=True)

# Individual phases
from ucx import UCCPhase, UCRPhase, UCRemPhase
ucc = UCCPhase()
ucr = UCRPhase()
ucrem = UCRemPhase()

# Models
from ucx import Document, ReviewResult, FixProposal, DriftCache

# Enums
from ucx import DocType, Status, Confidence

# Plugins
from ucx import UCXPlugin
```

### CLI Quick Reference

```bash
# Autopilot
ucx autopilot brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/
ucx autopilot prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01 --max-iterations 5
ucx autopilot brd docs/01_BRD/BRD-01 --checkpoint  # Enable resume
ucx autopilot --resume .ucx_checkpoints/abc123.json  # Resume from checkpoint

# Individual phases
ucx create brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/
ucx review brd docs/01_BRD/BRD-01
ucx remediate BRD_UCR_REVIEW.md docs/01_BRD/BRD-01 --apply-auto-safe

# Drift monitoring
ucx drift check docs/01_BRD/BRD-01
ucx drift update docs/01_BRD/BRD-01
ucx drift status

# MCP Server
ucx serve                          # stdio transport
ucx serve --transport http --port 8765

# Utilities
ucx validate brd docs/01_BRD/BRD-01
ucx init --project-name myproject
ucx config show
ucx config init
ucx version
```

---

## 22. Directory Relocation

### 22.1 Rationale

UCX should be moved from `ai_dev_ssd_flow/UCX/` to root level `docs_flow_framework/UCX/`:

| Factor | Current Location | Proposed Location |
|--------|------------------|-------------------|
| Path | `ai_dev_ssd_flow/UCX/` | `UCX/` (root) |
| Consistency | Mixed with SDD artifacts | Alongside `governance/`, `dev_tools/` |
| Discoverability | Nested 2 levels deep | Root-level visibility |
| Independence | Coupled with doc templates | Standalone tool |

### 22.2 Migration Steps

```bash
# Phase 0: Preparation
cd /opt/data/docs_flow_framework

# 1. Move UCX to root level
mv ai_dev_ssd_flow/UCX ./UCX

# 2. Update symlink in ai_dev_ssd_flow
rm ai_dev_ssd_flow/AI_EXPERTS
ln -s ../UCX ai_dev_ssd_flow/AI_EXPERTS

# 3. Update any absolute path references
grep -r "ai_dev_ssd_flow/UCX" --include="*.md" --include="*.py" --include="*.sh" | \
    xargs sed -i 's|ai_dev_ssd_flow/UCX|UCX|g'

# 4. Update pyproject.toml paths if needed
# 5. Run tests to verify
cd UCX && pytest
```

### 22.3 Post-Migration Structure

```
/opt/data/docs_flow_framework/
├── UCX/                        # NEW: Root-level UCX
│   ├── ucx/                    # Python package
│   ├── tests/
│   ├── docs/
│   ├── bin/
│   ├── pyproject.toml
│   └── IPLAN-001_ucx_python_migration.md
├── governance/                 # Governance tools
├── dev_tools/                  # Development tools
├── automation/                 # Automation scripts
├── ai_dev_ssd_flow/           # SDD layer artifacts
│   ├── 01_BRD/
│   ├── 02_PRD/
│   ├── ...
│   └── AI_EXPERTS -> ../UCX   # Symlink for compatibility
└── ...
```

### 22.4 Compatibility

- Existing `AI_EXPERTS` symlink will point to new location
- All relative imports within UCX remain unchanged
- Shell wrappers in `bin/` continue to work
- Environment variables unchanged

### 22.5 Legacy Deprecation

The following directories are **DEPRECATED** and superseded by UCX:

#### 22.5.1 Deprecated Directories

| Directory | Status | Replacement |
|-----------|--------|-------------|
| `ai_dev_ssd_flow/AI_EXPERTS/` | Symlink → UCX | `UCX/ucx/skills/personas/` |
| `ai_dev_ssd_flow/AUTOPILOT/` | DEPRECATED | `UCX/ucx/api/autopilot.py` + CLI |

#### 22.5.2 AUTOPILOT Directory Contents

```
ai_dev_ssd_flow/AUTOPILOT/           # DEPRECATED
├── AUTOPILOT_INTEGRATION_REVIEW.md  # → UCX docs/
├── AUTOPILOT_WORKFLOW_GUIDE.md      # → UCX docs/user_guide.md
├── HOW_TO_USE_AUTOPILOT.md          # → UCX docs/getting-started/
├── IMPROVEMENTS_SUMMARY.md          # Archive only
├── MVP_AUTOPILOT.md                 # → UCX IPLAN-001
├── MVP_GITHUB_CICD_INTEGRATION_PLAN.md  # → UCX .github/workflows/
├── MVP_PIPELINE_END_TO_END_USER_GUIDE.md # → UCX docs/
├── Makefile                         # → UCX pyproject.toml scripts
├── config/                          # → UCX ucx/config/
├── scripts/                         # → UCX ucx/cli/ + bin/
└── tests/                           # → UCX tests/
```

#### 22.5.3 Deprecation Timeline

| Phase | Action | Target Date |
|-------|--------|-------------|
| **Phase 1** | Add deprecation notice to AUTOPILOT/README.md | Week 1 |
| **Phase 2** | Migrate useful documentation to UCX/docs/ | Week 2-3 |
| **Phase 3** | Update all references in other docs | Week 4 |
| **Phase 4** | Remove AUTOPILOT symlink from AI_EXPERTS | Week 6 |
| **Phase 5** | Archive AUTOPILOT to `.deprecated/` | Week 8 |
| **Phase 6** | Delete AUTOPILOT after 30-day notice | Week 12 |

#### 22.5.4 Deprecation Script

```bash
#!/usr/bin/env bash
# scripts/deprecate_legacy.sh
# Run this after UCX Python migration is complete

set -euo pipefail

DOCS_FLOW="/opt/data/docs_flow_framework"
AUTOPILOT="$DOCS_FLOW/ai_dev_ssd_flow/AUTOPILOT"
DEPRECATED="$DOCS_FLOW/.deprecated"
UCX="$DOCS_FLOW/UCX"

echo "=== UCX Legacy Deprecation Script ==="

# Phase 1: Create deprecation notice
cat > "$AUTOPILOT/DEPRECATED.md" << 'EOF'
# ⚠️ DEPRECATED

**This directory is DEPRECATED as of 2026-03-09.**

All functionality has been migrated to the UCX Framework.

## Migration Guide

| Old Location | New Location |
|--------------|--------------|
| `AUTOPILOT/scripts/` | `UCX/bin/` or `ucx` CLI |
| `AUTOPILOT/config/` | `UCX/ucx/config/` |
| `AUTOPILOT/*.md` | `UCX/docs/` |

## New Commands

```bash
# Instead of: ./AUTOPILOT/scripts/run_autopilot.sh
ucx autopilot brd docs/01_BRD/BRD-01

# Instead of: make review
ucx review brd docs/01_BRD/BRD-01

# Instead of: make remediate
ucx remediate report.md docs/01_BRD/BRD-01
```

## Removal Schedule

- **2026-04-06**: Moved to `.deprecated/AUTOPILOT/`
- **2026-05-06**: Permanently deleted

Please update your workflows to use UCX.
EOF

echo "✓ Created deprecation notice"

# Phase 2: Migrate documentation (selective)
mkdir -p "$UCX/docs/legacy"
for doc in AUTOPILOT_WORKFLOW_GUIDE.md HOW_TO_USE_AUTOPILOT.md; do
    if [[ -f "$AUTOPILOT/$doc" ]]; then
        cp "$AUTOPILOT/$doc" "$UCX/docs/legacy/"
        echo "✓ Migrated $doc to UCX/docs/legacy/"
    fi
done

# Phase 3: Update AI_EXPERTS symlink (already points to UCX)
if [[ -L "$DOCS_FLOW/ai_dev_ssd_flow/AI_EXPERTS" ]]; then
    echo "✓ AI_EXPERTS symlink already points to UCX"
else
    rm -f "$DOCS_FLOW/ai_dev_ssd_flow/AI_EXPERTS"
    ln -s ../UCX "$DOCS_FLOW/ai_dev_ssd_flow/AI_EXPERTS"
    echo "✓ Updated AI_EXPERTS symlink"
fi

# Phase 4: Archive (run manually after Week 8)
archive_autopilot() {
    mkdir -p "$DEPRECATED"
    mv "$AUTOPILOT" "$DEPRECATED/AUTOPILOT_$(date +%Y%m%d)"
    echo "✓ Archived AUTOPILOT to .deprecated/"
}

echo ""
echo "=== Deprecation Complete ==="
echo "To archive AUTOPILOT (after Week 8), run:"
echo "  archive_autopilot"
```

#### 22.5.5 Feature Migration Matrix

| AUTOPILOT Feature | UCX Equivalent | Status |
|-------------------|----------------|--------|
| `run_autopilot.sh` | `ucx autopilot` CLI | ✅ Implemented |
| `run_review.sh` | `ucx review` CLI | ✅ Implemented |
| `run_remediate.sh` | `ucx remediate` CLI | ✅ Implemented |
| Makefile targets | `pyproject.toml` scripts | ✅ Implemented |
| config/*.yaml | `ucx/config/` + `ucx.yaml` | ✅ Implemented |
| Persona definitions | `ucx/skills/personas/` | ✅ Implemented |
| Drift monitoring | `ucx/core/drift.py` | ✅ Implemented |
| Batch processing | `ucx autopilot --batch` | ✅ Implemented |
| CI/CD integration | `.github/workflows/ci.yml` | ✅ Implemented |

#### 22.5.6 Breaking Changes

Users of the legacy AUTOPILOT must update:

1. **Script invocations**:
   ```bash
   # Old
   ./AUTOPILOT/scripts/run_autopilot.sh --doc-type brd --target docs/

   # New
   ucx autopilot brd docs/
   ```

2. **Environment variables**:
   ```bash
   # Old (still supported)
   AUTOPILOT_MODEL=opus

   # New (preferred)
   UCX_MODEL=opus
   ```

3. **Configuration files**:
   ```bash
   # Old
   AUTOPILOT/config/settings.yaml

   # New
   ucx.yaml  # or UCX_* environment variables
   ```

4. **Import paths** (for programmatic use):
   ```python
   # Old (removed)
   from autopilot import run_autopilot

   # New
   from ucx import UCXAutopilot
   autopilot = UCXAutopilot()
   result = autopilot.run("brd", "docs/01_BRD/BRD-01")
   ```

---

## 23. Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.3 | 2026-03-09 | Added: Legacy deprecation plan for AI_EXPERTS and AUTOPILOT directories. Added: Deprecation timeline, migration matrix, breaking changes documentation, deprecation script. |
| 1.2 | 2026-03-09 | Added: OTEL LLM instrumentation, structlog configuration, observability module, directory relocation plan. Updated: Dependencies with OTEL packages. Extended timeline from 7 to 8 weeks. |
| 1.1 | 2026-03-09 | Added: MCP Server Mode, Token Management, Error Recovery, Plugin System, Async Support, CI/CD Config, Documentation Structure. Updated: Implementation phases from 9 to 10. Extended timeline from 6 to 7 weeks. |
| 1.0 | 2026-03-09 | Initial plan created |
