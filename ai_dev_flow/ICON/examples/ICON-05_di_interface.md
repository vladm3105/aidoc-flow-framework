# =============================================================================
# ICON-05: Dependency Injection Interface Example
# =============================================================================
# Example Implementation Contract demonstrating ABC-based dependency injection
# interfaces with provider/consumer patterns for testable architecture
# =============================================================================
---
title: "ICON-05: Notification Service DI Interface"
tags:
  - implementation-contract
  - layer-11-artifact
  - shared-architecture
  - di-interface
  - example
custom_fields:
  document_type: implementation_contract
  artifact_type: ICON
  layer: 11
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  contract_type: di-interface
  provider_tasks: TASKS-040
  consumer_count: 8
  providers: [TASKS-040, TASKS-041, TASKS-042]
  consumers: [TASKS-043, TASKS-044, TASKS-045, TASKS-046, TASKS-047, TASKS-048, TASKS-049, TASKS-050]
---

# ICON-05: Notification Service DI Interface

## Document Control

| Item | Details |
|------|---------|
| **Status** | Active |
| **Version** | 1.0.0 |
| **Date Created** | 2025-12-29 |
| **Last Updated** | 2025-12-29 |
| **Author** | AI Development Team |
| **Contract Type** | DI Interface |
| **Providers** | TASKS-040, TASKS-041, TASKS-042 |
| **Consumers** | TASKS-043 through TASKS-050 |

---

## 3. Executive Summary

This contract defines ABC-based dependency injection interfaces for the notification service. It establishes abstract base classes, provider patterns, and testable interfaces that enable loose coupling between services, easy mocking for tests, and pluggable notification channel implementations.

### 3.1 Scope

**Purpose**: Enable pluggable notification backends with consistent interfaces
**Boundary**: Notification sending abstractions only
**Complexity**: 4/5

---

## 1. Contract Definition

### 1.1 Contract Type

**Type**: DI Interface

**Rationale**: Notification services require:
- Multiple backend implementations (email, SMS, push)
- Easy testing with mock implementations
- Runtime provider switching
- Consistent interface across channels

### 1.2 Interface Specification

```python
"""
Notification Service DI Interface Contract
==========================================
ABC-based dependency injection interfaces for notification services.
Enables pluggable backends, easy testing, and consistent API.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    Optional,
    List,
    Dict,
    Any,
    Protocol,
    TypeVar,
    Generic,
    runtime_checkable,
)
from contextlib import asynccontextmanager


# =============================================================================
# Value Types
# =============================================================================

class NotificationChannel(str, Enum):
    """Available notification channels."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"
    WEBHOOK = "webhook"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class DeliveryStatus(str, Enum):
    """Notification delivery status."""
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"


@dataclass(frozen=True)
class Recipient:
    """Notification recipient."""
    id: str
    channel: NotificationChannel
    address: str  # email, phone, device_token, etc.
    name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationContent:
    """Notification content payload."""
    subject: Optional[str] = None
    body: str = ""
    html_body: Optional[str] = None
    template_id: Optional[str] = None
    template_vars: Dict[str, Any] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class NotificationRequest:
    """Request to send a notification."""
    id: str
    recipient: Recipient
    content: NotificationContent
    channel: NotificationChannel
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_at: Optional[datetime] = None
    idempotency_key: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None


@dataclass
class NotificationResult:
    """Result of notification send attempt."""
    request_id: str
    status: DeliveryStatus
    channel: NotificationChannel
    provider_message_id: Optional[str] = None
    sent_at: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    retryable: bool = False
    retry_after_seconds: Optional[int] = None


# =============================================================================
# Core Interfaces (ABC-based)
# =============================================================================

class NotificationSender(ABC):
    """
    Abstract base class for notification sending.

    Each channel (email, SMS, push) implements this interface.
    Implementations are injected at runtime based on configuration.

    Example:
        class EmailSender(NotificationSender):
            def __init__(self, smtp_client: SMTPClient):
                self._smtp = smtp_client

            async def send(self, request: NotificationRequest) -> NotificationResult:
                # Implementation details
                pass
    """

    @property
    @abstractmethod
    def channel(self) -> NotificationChannel:
        """Channel this sender handles."""
        ...

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if sender is currently available."""
        ...

    @abstractmethod
    async def send(self, request: NotificationRequest) -> NotificationResult:
        """
        Send a single notification.

        Args:
            request: Notification request with recipient and content

        Returns:
            NotificationResult with delivery status

        Raises:
            NotificationError: If sending fails with non-retryable error
        """
        ...

    @abstractmethod
    async def send_batch(
        self,
        requests: List[NotificationRequest]
    ) -> List[NotificationResult]:
        """
        Send multiple notifications in batch.

        Args:
            requests: List of notification requests

        Returns:
            List of results (same order as requests)
        """
        ...

    @abstractmethod
    async def get_status(self, message_id: str) -> DeliveryStatus:
        """
        Check delivery status of sent notification.

        Args:
            message_id: Provider message ID from NotificationResult

        Returns:
            Current delivery status
        """
        ...


class TemplateRenderer(ABC):
    """
    Abstract base class for notification template rendering.

    Separates template rendering from sending for flexibility.
    Supports multiple template engines (Jinja2, Handlebars, etc.)
    """

    @abstractmethod
    async def render(
        self,
        template_id: str,
        variables: Dict[str, Any],
        locale: str = "en"
    ) -> NotificationContent:
        """
        Render template to notification content.

        Args:
            template_id: Template identifier
            variables: Template variables
            locale: Localization locale

        Returns:
            Rendered NotificationContent

        Raises:
            TemplateNotFoundError: Template doesn't exist
            TemplateRenderError: Rendering failed
        """
        ...

    @abstractmethod
    async def validate_template(
        self,
        template_id: str,
        variables: Dict[str, Any]
    ) -> List[str]:
        """
        Validate template with given variables.

        Returns list of missing or invalid variables.
        """
        ...

    @abstractmethod
    def list_templates(self, channel: NotificationChannel) -> List[str]:
        """List available templates for channel."""
        ...


class NotificationQueue(ABC):
    """
    Abstract base class for notification queueing.

    Enables async processing, rate limiting, and retry handling.
    """

    @abstractmethod
    async def enqueue(
        self,
        request: NotificationRequest,
        delay_seconds: int = 0
    ) -> str:
        """
        Add notification to queue for async processing.

        Args:
            request: Notification request
            delay_seconds: Delay before processing

        Returns:
            Queue job ID
        """
        ...

    @abstractmethod
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of queued job."""
        ...

    @abstractmethod
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel queued job if not yet processed."""
        ...

    @abstractmethod
    async def retry_job(self, job_id: str) -> str:
        """Retry failed job, returns new job ID."""
        ...


class DeliveryTracker(ABC):
    """
    Abstract base class for delivery tracking and analytics.

    Tracks delivery status, open rates, click rates, etc.
    """

    @abstractmethod
    async def track_sent(self, result: NotificationResult) -> None:
        """Record notification sent."""
        ...

    @abstractmethod
    async def track_delivered(
        self,
        message_id: str,
        delivered_at: datetime
    ) -> None:
        """Record successful delivery."""
        ...

    @abstractmethod
    async def track_failed(
        self,
        message_id: str,
        error_code: str,
        error_message: str
    ) -> None:
        """Record delivery failure."""
        ...

    @abstractmethod
    async def track_opened(
        self,
        message_id: str,
        opened_at: datetime
    ) -> None:
        """Record notification opened (email/push)."""
        ...

    @abstractmethod
    async def track_clicked(
        self,
        message_id: str,
        link_id: str,
        clicked_at: datetime
    ) -> None:
        """Record link click."""
        ...

    @abstractmethod
    async def get_delivery_stats(
        self,
        start_date: datetime,
        end_date: datetime,
        channel: Optional[NotificationChannel] = None
    ) -> Dict[str, Any]:
        """Get delivery statistics for period."""
        ...


# =============================================================================
# Protocol Interface (for structural typing)
# =============================================================================

@runtime_checkable
class NotificationProvider(Protocol):
    """
    Protocol for notification providers.

    Use this for duck-typed dependency injection where
    ABC inheritance isn't required.
    """

    @property
    def channel(self) -> NotificationChannel: ...

    async def send(self, request: NotificationRequest) -> NotificationResult: ...


# =============================================================================
# Factory Interface
# =============================================================================

class NotificationSenderFactory(ABC):
    """
    Factory for creating channel-specific senders.

    Enables runtime configuration of notification backends.
    """

    @abstractmethod
    def create_sender(self, channel: NotificationChannel) -> NotificationSender:
        """
        Create sender for specified channel.

        Args:
            channel: Notification channel

        Returns:
            Configured NotificationSender

        Raises:
            UnsupportedChannelError: Channel not configured
        """
        ...

    @abstractmethod
    def get_available_channels(self) -> List[NotificationChannel]:
        """Get list of configured channels."""
        ...

    @abstractmethod
    def register_sender(
        self,
        channel: NotificationChannel,
        sender: NotificationSender
    ) -> None:
        """Register sender for channel."""
        ...


# =============================================================================
# Service Aggregator Interface
# =============================================================================

class NotificationService(ABC):
    """
    High-level notification service interface.

    Aggregates senders, templates, queue, and tracking.
    This is the main interface consumers should depend on.
    """

    @abstractmethod
    async def send(
        self,
        recipient_id: str,
        template_id: str,
        variables: Dict[str, Any],
        channel: Optional[NotificationChannel] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        **kwargs
    ) -> NotificationResult:
        """
        Send notification using template.

        Args:
            recipient_id: User ID to notify
            template_id: Template to render
            variables: Template variables
            channel: Override channel (default from user preferences)
            priority: Delivery priority
            **kwargs: Additional options

        Returns:
            NotificationResult
        """
        ...

    @abstractmethod
    async def send_immediate(
        self,
        request: NotificationRequest
    ) -> NotificationResult:
        """Send notification immediately (bypass queue)."""
        ...

    @abstractmethod
    async def schedule(
        self,
        recipient_id: str,
        template_id: str,
        variables: Dict[str, Any],
        send_at: datetime,
        **kwargs
    ) -> str:
        """Schedule notification for future delivery."""
        ...

    @abstractmethod
    async def cancel_scheduled(self, job_id: str) -> bool:
        """Cancel scheduled notification."""
        ...

    @abstractmethod
    async def get_user_preferences(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Get user notification preferences."""
        ...

    @abstractmethod
    async def update_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> None:
        """Update user notification preferences."""
        ...


# =============================================================================
# Configuration Interface
# =============================================================================

@dataclass
class ChannelConfig:
    """Configuration for a notification channel."""
    enabled: bool = True
    rate_limit_per_second: int = 10
    retry_max_attempts: int = 3
    retry_backoff_seconds: int = 60
    timeout_seconds: int = 30
    batch_size: int = 100
    provider_settings: Dict[str, Any] = field(default_factory=dict)


class NotificationConfigProvider(ABC):
    """
    Abstract interface for notification configuration.

    Enables configuration from various sources (env, files, services).
    """

    @abstractmethod
    def get_channel_config(
        self,
        channel: NotificationChannel
    ) -> ChannelConfig:
        """Get configuration for channel."""
        ...

    @abstractmethod
    def is_channel_enabled(self, channel: NotificationChannel) -> bool:
        """Check if channel is enabled."""
        ...

    @abstractmethod
    def get_default_channel(self) -> NotificationChannel:
        """Get default notification channel."""
        ...


# =============================================================================
# Context Manager for Transactions
# =============================================================================

class NotificationContext(ABC):
    """
    Context manager for notification transactions.

    Enables atomic notification sending with rollback on failure.
    """

    @abstractmethod
    @asynccontextmanager
    async def transaction(self):
        """
        Begin notification transaction.

        Usage:
            async with notification_ctx.transaction():
                await service.send(...)
                await service.send(...)
                # All or nothing - rolls back on exception
        """
        ...


# =============================================================================
# Mock Implementation for Testing
# =============================================================================

class MockNotificationSender(NotificationSender):
    """
    Mock sender for testing.

    Records all sent notifications for assertion.
    """

    def __init__(self, channel: NotificationChannel):
        self._channel = channel
        self._sent: List[NotificationRequest] = []
        self._should_fail = False
        self._is_available = True

    @property
    def channel(self) -> NotificationChannel:
        return self._channel

    @property
    def is_available(self) -> bool:
        return self._is_available

    @property
    def sent_notifications(self) -> List[NotificationRequest]:
        """Get list of sent notifications for assertions."""
        return self._sent.copy()

    def configure_failure(self, should_fail: bool = True) -> None:
        """Configure mock to fail sends."""
        self._should_fail = should_fail

    def configure_availability(self, available: bool = True) -> None:
        """Configure mock availability."""
        self._is_available = available

    async def send(self, request: NotificationRequest) -> NotificationResult:
        self._sent.append(request)

        if self._should_fail:
            return NotificationResult(
                request_id=request.id,
                status=DeliveryStatus.FAILED,
                channel=self._channel,
                error_code="MOCK_FAILURE",
                error_message="Configured to fail",
                retryable=True
            )

        return NotificationResult(
            request_id=request.id,
            status=DeliveryStatus.SENT,
            channel=self._channel,
            provider_message_id=f"mock_{request.id}",
            sent_at=datetime.utcnow()
        )

    async def send_batch(
        self,
        requests: List[NotificationRequest]
    ) -> List[NotificationResult]:
        return [await self.send(r) for r in requests]

    async def get_status(self, message_id: str) -> DeliveryStatus:
        return DeliveryStatus.DELIVERED

    def reset(self) -> None:
        """Reset mock state."""
        self._sent.clear()
        self._should_fail = False
        self._is_available = True
```

---

## 2. Provider Requirements

### 2.1 Implementation Obligations

**Provider TASKS**: TASKS-040 (Email), TASKS-041 (SMS), TASKS-042 (Push)

**Requirements**:
- [ ] Implement all abstract methods
- [ ] Honor rate limiting configuration
- [ ] Implement proper retry logic
- [ ] Track all deliveries via DeliveryTracker

### 2.2 Validation Criteria

```bash
# Type check implementations
mypy --strict src/services/notifications/

# Verify interface compliance
python -c "
from services.notifications.email import EmailSender
from contracts.notifications import NotificationSender
assert issubclass(EmailSender, NotificationSender)
"
```

---

## 3. Consumer Requirements

### 3.1 Usage Obligations

**Consumer TASKS**: TASKS-043 through TASKS-050

**Requirements**:
- [ ] Depend on interfaces, not implementations
- [ ] Use factory for sender creation
- [ ] Use MockNotificationSender in tests
- [ ] Handle all possible DeliveryStatus values

### 3.2 Dependency Management

```python
from contracts.notifications import (
    NotificationService,
    NotificationChannel,
    NotificationPriority,
)

class OrderService:
    """Order service with notification dependency."""

    def __init__(self, notifications: NotificationService):
        # Depend on interface, not implementation
        self._notifications = notifications

    async def complete_order(self, order: Order) -> None:
        """Complete order and notify customer."""
        # Business logic...

        await self._notifications.send(
            recipient_id=order.customer_id,
            template_id="order_complete",
            variables={
                "order_id": order.id,
                "total": order.total,
                "items": order.items,
            },
            priority=NotificationPriority.HIGH
        )
```

---

## 5. Testing Requirements

### 5.1 Provider Tests

```python
import pytest
from contracts.notifications import (
    MockNotificationSender,
    NotificationChannel,
    NotificationRequest,
    NotificationContent,
    Recipient,
    DeliveryStatus,
)

class TestMockNotificationSender:
    """Verify mock sender works correctly."""

    @pytest.fixture
    def mock_sender(self):
        return MockNotificationSender(NotificationChannel.EMAIL)

    @pytest.fixture
    def sample_request(self):
        return NotificationRequest(
            id="req-123",
            recipient=Recipient(
                id="user-456",
                channel=NotificationChannel.EMAIL,
                address="user@example.com"
            ),
            content=NotificationContent(body="Test message"),
            channel=NotificationChannel.EMAIL
        )

    async def test_send_records_notification(self, mock_sender, sample_request):
        """Sent notifications are recorded for assertions."""
        result = await mock_sender.send(sample_request)

        assert result.status == DeliveryStatus.SENT
        assert len(mock_sender.sent_notifications) == 1
        assert mock_sender.sent_notifications[0].id == "req-123"

    async def test_configured_failure(self, mock_sender, sample_request):
        """Mock can be configured to fail."""
        mock_sender.configure_failure(True)

        result = await mock_sender.send(sample_request)

        assert result.status == DeliveryStatus.FAILED
        assert result.retryable is True
```

### 5.2 Consumer Tests

```python
import pytest
from unittest.mock import AsyncMock
from contracts.notifications import NotificationService, NotificationResult, DeliveryStatus

@pytest.fixture
def mock_notification_service():
    """Create mock notification service for testing."""
    service = AsyncMock(spec=NotificationService)
    service.send.return_value = NotificationResult(
        request_id="req-123",
        status=DeliveryStatus.SENT,
        channel=NotificationChannel.EMAIL,
        provider_message_id="msg-456"
    )
    return service

async def test_order_completion_sends_notification(mock_notification_service):
    """Order completion triggers notification."""
    order_service = OrderService(notifications=mock_notification_service)
    order = Order(id="ord-789", customer_id="cust-123", total=99.99)

    await order_service.complete_order(order)

    mock_notification_service.send.assert_called_once()
    call_kwargs = mock_notification_service.send.call_args.kwargs
    assert call_kwargs["recipient_id"] == "cust-123"
    assert call_kwargs["template_id"] == "order_complete"
```

---

## 6. Documentation

### 6.1 Usage Examples

**DI Container Registration**:
```python
from dependency_injector import containers, providers

class NotificationContainer(containers.DeclarativeContainer):
    """DI container for notification services."""

    config = providers.Configuration()

    # Channel senders
    email_sender = providers.Singleton(
        EmailSender,
        smtp_client=providers.Dependency()
    )

    sms_sender = providers.Singleton(
        TwilioSMSSender,
        account_sid=config.twilio.account_sid,
        auth_token=config.twilio.auth_token
    )

    # Factory
    sender_factory = providers.Singleton(
        DefaultSenderFactory,
        email=email_sender,
        sms=sms_sender
    )

    # Main service
    notification_service = providers.Singleton(
        DefaultNotificationService,
        sender_factory=sender_factory,
        template_renderer=providers.Dependency(),
        queue=providers.Dependency()
    )
```

### 6.2 Common Patterns

**Multi-channel notification**:
```python
async def notify_user(
    user_id: str,
    template_id: str,
    variables: Dict[str, Any],
    service: NotificationService
) -> List[NotificationResult]:
    """Send notification to all user's preferred channels."""
    prefs = await service.get_user_preferences(user_id)

    results = []
    for channel in prefs.get("enabled_channels", [NotificationChannel.EMAIL]):
        result = await service.send(
            recipient_id=user_id,
            template_id=template_id,
            variables=variables,
            channel=channel
        )
        results.append(result)

    return results
```

### 6.3 Anti-Patterns

**Avoid**:
- Directly instantiating concrete senders in services
- Depending on specific notification providers
- Skipping the factory for sender creation
- Using real senders in unit tests

---

## 7. Traceability

### 7.1 Upstream Artifacts

```markdown
@spec: SPEC-08         # Notification System Specification
@req: REQ.08.01.01     # Notification Requirements
@adr: ADR-06           # DI Architecture Decision
```

### 7.2 Provider/Consumer Tags

```markdown
@icon: ICON-05:NotificationDIInterface
```

---

## 10. Document Metadata

**Version**: 1.0.0
**Created**: 2025-12-29
**Last Updated**: 2025-12-29
**Contract Type**: DI Interface
**Providers**: 3
**Consumers**: 8
**Complexity**: 4/5
**Token Count**: ~5000

# =============================================================================
# END OF ICON-05: Notification Service DI Interface
# =============================================================================
