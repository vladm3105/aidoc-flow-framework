# =============================================================================
# ICON-03: State Machine Contract Example
# =============================================================================
# Example Implementation Contract demonstrating enum-based state definitions
# with valid transition mappings and state machine behavior contracts
# =============================================================================
---
title: "ICON-03: Order Lifecycle State Machine"
tags:
  - implementation-contract
  - layer-11-artifact
  - shared-architecture
  - state-machine
  - example
custom_fields:
  document_type: implementation_contract
  artifact_type: ICON
  layer: 11
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  contract_type: state-machine
  provider_tasks: TASKS-020
  consumer_count: 5
  providers: [TASKS-020]
  consumers: [TASKS-021, TASKS-022, TASKS-023, TASKS-024, TASKS-025]
---

# ICON-03: Order Lifecycle State Machine

## Document Control

| Item | Details |
|------|---------|
| **Status** | Active |
| **Version** | 1.0.0 |
| **Date Created** | 2025-12-29 |
| **Last Updated** | 2025-12-29 |
| **Author** | AI Development Team |
| **Contract Type** | State Machine |
| **Providers** | TASKS-020 (Order Service) |
| **Consumers** | TASKS-021, TASKS-022, TASKS-023, TASKS-024, TASKS-025 |

---

## 3. Executive Summary

This contract defines the order lifecycle state machine for the e-commerce platform. It establishes enum-based states, valid transition mappings, transition guards, and event-driven state change protocols. All services interacting with orders must conform to this state machine contract.

### 3.1 Scope

**Purpose**: Ensure consistent order state management across all services
**Boundary**: Order entity state only; excludes payment and shipping states
**Complexity**: 4/5

---

## 1. Contract Definition

### 1.1 Contract Type

**Type**: State Machine

**Rationale**: Order lifecycle requires:
- Well-defined states with clear semantics
- Valid transition paths with guards
- Event-driven state changes
- Audit trail for compliance

### 1.2 Interface Specification

```python
"""
Order Lifecycle State Machine Contract
======================================
Defines order states, transitions, guards, and state machine behavior
for consistent order management across all services.

State Diagram:
                                    ┌─────────────────────────────────┐
                                    │                                 ▼
    DRAFT ──> PENDING_PAYMENT ──> PAID ──> PROCESSING ──> SHIPPED ──> DELIVERED
      │              │              │          │             │
      │              │              │          │             └──> RETURNED
      │              │              │          │
      ▼              ▼              ▼          ▼
   CANCELLED    CANCELLED      REFUNDED   CANCELLED
                EXPIRED
"""

from enum import Enum, auto
from typing import Set, Dict, Optional, Callable, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod


class OrderState(str, Enum):
    """
    Order lifecycle states.

    Terminal states: DELIVERED, CANCELLED, REFUNDED, RETURNED
    """
    # Initial state
    DRAFT = "draft"

    # Payment flow
    PENDING_PAYMENT = "pending_payment"
    PAYMENT_EXPIRED = "payment_expired"
    PAID = "paid"

    # Fulfillment flow
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

    # Exception states
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    RETURNED = "returned"

    @property
    def is_terminal(self) -> bool:
        """Check if state is a terminal (final) state."""
        return self in {
            OrderState.DELIVERED,
            OrderState.CANCELLED,
            OrderState.REFUNDED,
            OrderState.RETURNED,
            OrderState.PAYMENT_EXPIRED,
        }

    @property
    def is_cancellable(self) -> bool:
        """Check if order can be cancelled from this state."""
        return self in {
            OrderState.DRAFT,
            OrderState.PENDING_PAYMENT,
            OrderState.PAID,
            OrderState.PROCESSING,
        }

    @property
    def is_refundable(self) -> bool:
        """Check if order can be refunded from this state."""
        return self in {
            OrderState.PAID,
            OrderState.PROCESSING,
            OrderState.SHIPPED,
            OrderState.DELIVERED,
        }


class OrderEvent(str, Enum):
    """Events that trigger state transitions."""
    # Customer actions
    SUBMIT = "submit"
    CANCEL = "cancel"

    # Payment events
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_EXPIRED = "payment_expired"
    REFUND_INITIATED = "refund_initiated"

    # Fulfillment events
    START_PROCESSING = "start_processing"
    SHIP = "ship"
    DELIVER = "deliver"

    # Returns
    RETURN_INITIATED = "return_initiated"
    RETURN_RECEIVED = "return_received"


@dataclass(frozen=True)
class Transition:
    """
    State transition definition with guards.

    Attributes:
        from_state: Source state
        to_state: Target state
        event: Triggering event
        guards: List of guard function names
        side_effects: List of side effect function names
    """
    from_state: OrderState
    to_state: OrderState
    event: OrderEvent
    guards: tuple = field(default_factory=tuple)
    side_effects: tuple = field(default_factory=tuple)


# =============================================================================
# Transition Table (Single Source of Truth)
# =============================================================================

VALID_TRANSITIONS: Set[Transition] = {
    # Draft -> Pending Payment (submit order)
    Transition(
        from_state=OrderState.DRAFT,
        to_state=OrderState.PENDING_PAYMENT,
        event=OrderEvent.SUBMIT,
        guards=("has_items", "has_shipping_address"),
        side_effects=("create_payment_intent", "set_payment_deadline")
    ),

    # Draft -> Cancelled
    Transition(
        from_state=OrderState.DRAFT,
        to_state=OrderState.CANCELLED,
        event=OrderEvent.CANCEL,
        guards=(),
        side_effects=("release_inventory",)
    ),

    # Pending Payment -> Paid
    Transition(
        from_state=OrderState.PENDING_PAYMENT,
        to_state=OrderState.PAID,
        event=OrderEvent.PAYMENT_RECEIVED,
        guards=("payment_amount_matches",),
        side_effects=("confirm_inventory", "send_confirmation_email")
    ),

    # Pending Payment -> Expired
    Transition(
        from_state=OrderState.PENDING_PAYMENT,
        to_state=OrderState.PAYMENT_EXPIRED,
        event=OrderEvent.PAYMENT_EXPIRED,
        guards=("payment_deadline_passed",),
        side_effects=("release_inventory", "send_expiry_notification")
    ),

    # Pending Payment -> Cancelled
    Transition(
        from_state=OrderState.PENDING_PAYMENT,
        to_state=OrderState.CANCELLED,
        event=OrderEvent.CANCEL,
        guards=(),
        side_effects=("cancel_payment_intent", "release_inventory")
    ),

    # Paid -> Processing
    Transition(
        from_state=OrderState.PAID,
        to_state=OrderState.PROCESSING,
        event=OrderEvent.START_PROCESSING,
        guards=("inventory_available",),
        side_effects=("create_fulfillment_task",)
    ),

    # Paid -> Refunded (before processing)
    Transition(
        from_state=OrderState.PAID,
        to_state=OrderState.REFUNDED,
        event=OrderEvent.REFUND_INITIATED,
        guards=("within_refund_window",),
        side_effects=("process_refund", "release_inventory")
    ),

    # Paid -> Cancelled
    Transition(
        from_state=OrderState.PAID,
        to_state=OrderState.CANCELLED,
        event=OrderEvent.CANCEL,
        guards=("not_processing_started",),
        side_effects=("process_refund", "release_inventory")
    ),

    # Processing -> Shipped
    Transition(
        from_state=OrderState.PROCESSING,
        to_state=OrderState.SHIPPED,
        event=OrderEvent.SHIP,
        guards=("has_tracking_number",),
        side_effects=("send_shipping_notification",)
    ),

    # Processing -> Cancelled
    Transition(
        from_state=OrderState.PROCESSING,
        to_state=OrderState.CANCELLED,
        event=OrderEvent.CANCEL,
        guards=("not_shipped",),
        side_effects=("process_refund", "cancel_fulfillment")
    ),

    # Shipped -> Delivered
    Transition(
        from_state=OrderState.SHIPPED,
        to_state=OrderState.DELIVERED,
        event=OrderEvent.DELIVER,
        guards=(),
        side_effects=("send_delivery_confirmation", "start_return_window")
    ),

    # Shipped -> Returned (return before delivery)
    Transition(
        from_state=OrderState.SHIPPED,
        to_state=OrderState.RETURNED,
        event=OrderEvent.RETURN_RECEIVED,
        guards=(),
        side_effects=("process_refund", "restock_inventory")
    ),

    # Delivered -> Returned
    Transition(
        from_state=OrderState.DELIVERED,
        to_state=OrderState.RETURNED,
        event=OrderEvent.RETURN_RECEIVED,
        guards=("within_return_window",),
        side_effects=("process_refund", "restock_inventory")
    ),
}


# =============================================================================
# State Machine Protocol
# =============================================================================

class TransitionGuard(ABC):
    """Protocol for transition guard implementations."""

    @abstractmethod
    def check(self, order: "Order", context: Dict[str, Any]) -> bool:
        """
        Evaluate guard condition.

        Args:
            order: Order entity being transitioned
            context: Additional context for evaluation

        Returns:
            True if guard passes, False otherwise
        """
        ...

    @property
    @abstractmethod
    def error_message(self) -> str:
        """Human-readable error when guard fails."""
        ...


class SideEffect(ABC):
    """Protocol for transition side effect implementations."""

    @abstractmethod
    async def execute(self, order: "Order", context: Dict[str, Any]) -> None:
        """
        Execute side effect.

        Args:
            order: Order entity after transition
            context: Additional context

        Raises:
            SideEffectError: If side effect fails
        """
        ...

    @property
    @abstractmethod
    def is_reversible(self) -> bool:
        """Whether this side effect can be rolled back."""
        ...


@dataclass
class TransitionResult:
    """Result of a state transition attempt."""
    success: bool
    from_state: OrderState
    to_state: Optional[OrderState]
    event: OrderEvent
    failed_guard: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class OrderStateMachine:
    """
    Order state machine implementation.

    This class enforces valid state transitions and executes
    associated guards and side effects.
    """

    def __init__(
        self,
        guards: Dict[str, TransitionGuard],
        side_effects: Dict[str, SideEffect]
    ):
        self._guards = guards
        self._side_effects = side_effects
        self._transition_map = self._build_transition_map()

    def _build_transition_map(self) -> Dict[tuple, Transition]:
        """Build lookup map from (state, event) to transition."""
        return {
            (t.from_state, t.event): t
            for t in VALID_TRANSITIONS
        }

    def can_transition(
        self,
        order: "Order",
        event: OrderEvent,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if transition is possible without executing it.

        Args:
            order: Order entity
            event: Event to apply
            context: Additional context for guards

        Returns:
            True if transition would succeed
        """
        context = context or {}
        transition = self._transition_map.get((order.state, event))

        if transition is None:
            return False

        return all(
            self._guards[guard].check(order, context)
            for guard in transition.guards
            if guard in self._guards
        )

    def get_available_events(self, order: "Order") -> List[OrderEvent]:
        """
        Get list of events that can be applied to order's current state.

        Args:
            order: Order entity

        Returns:
            List of valid events
        """
        return [
            event
            for (state, event), _ in self._transition_map.items()
            if state == order.state
        ]

    async def transition(
        self,
        order: "Order",
        event: OrderEvent,
        context: Optional[Dict[str, Any]] = None
    ) -> TransitionResult:
        """
        Attempt to transition order to new state.

        Args:
            order: Order entity to transition
            event: Event triggering transition
            context: Additional context for guards/effects

        Returns:
            TransitionResult with success/failure details
        """
        context = context or {}
        from_state = order.state

        # Find valid transition
        transition = self._transition_map.get((from_state, event))
        if transition is None:
            return TransitionResult(
                success=False,
                from_state=from_state,
                to_state=None,
                event=event,
                error_message=f"No valid transition from {from_state} on event {event}"
            )

        # Check guards
        for guard_name in transition.guards:
            guard = self._guards.get(guard_name)
            if guard and not guard.check(order, context):
                return TransitionResult(
                    success=False,
                    from_state=from_state,
                    to_state=None,
                    event=event,
                    failed_guard=guard_name,
                    error_message=guard.error_message
                )

        # Execute transition
        order.state = transition.to_state

        # Execute side effects
        executed_effects = []
        try:
            for effect_name in transition.side_effects:
                effect = self._side_effects.get(effect_name)
                if effect:
                    await effect.execute(order, context)
                    executed_effects.append(effect_name)
        except Exception as e:
            # Rollback reversible effects
            for effect_name in reversed(executed_effects):
                effect = self._side_effects.get(effect_name)
                if effect and effect.is_reversible:
                    # ... rollback logic
                    pass
            order.state = from_state
            return TransitionResult(
                success=False,
                from_state=from_state,
                to_state=None,
                event=event,
                error_message=f"Side effect {effect_name} failed: {str(e)}"
            )

        return TransitionResult(
            success=True,
            from_state=from_state,
            to_state=transition.to_state,
            event=event
        )


# =============================================================================
# Order Entity Interface
# =============================================================================

@dataclass
class Order:
    """Order entity with state machine integration."""
    id: str
    state: OrderState = OrderState.DRAFT
    items: List[Any] = field(default_factory=list)
    shipping_address: Optional[str] = None
    tracking_number: Optional[str] = None
    payment_deadline: Optional[datetime] = None
    return_window_end: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    state_history: List[Dict[str, Any]] = field(default_factory=list)

    def record_transition(self, from_state: OrderState, to_state: OrderState, event: OrderEvent) -> None:
        """Record state transition in history for audit."""
        self.state_history.append({
            "from_state": from_state.value,
            "to_state": to_state.value,
            "event": event.value,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.utcnow()
```

---

## 2. Provider Requirements

### 2.1 Implementation Obligations

**Provider TASKS**: TASKS-020 (Order Service)

**Requirements**:
- [ ] Implement all state enums as defined
- [ ] Implement all guard functions
- [ ] Implement all side effect handlers
- [ ] Enforce transition table in all state changes
- [ ] Record all transitions in audit history

### 2.2 Validation Criteria

**State Transition Validation**:
```python
def test_no_invalid_transitions():
    """Verify only valid transitions are allowed."""
    machine = OrderStateMachine(guards={}, side_effects={})
    order = Order(id="test-001", state=OrderState.DRAFT)

    # Invalid: DRAFT cannot go directly to SHIPPED
    result = await machine.transition(order, OrderEvent.SHIP)
    assert result.success is False
    assert order.state == OrderState.DRAFT
```

---

## 3. Consumer Requirements

### 3.1 Usage Obligations

**Consumer TASKS**: TASKS-021 through TASKS-025

**Requirements**:
- [ ] Check `can_transition()` before attempting transitions
- [ ] Handle `TransitionResult` failures appropriately
- [ ] Never modify `order.state` directly
- [ ] Use `get_available_events()` for UI state management

### 3.2 Dependency Management

**Import Pattern**:
```python
from contracts.order.state_machine import (
    OrderState,
    OrderEvent,
    OrderStateMachine,
    TransitionResult,
)

class CheckoutService:
    """Checkout service consuming order state machine."""

    def __init__(self, state_machine: OrderStateMachine):
        self._state_machine = state_machine

    async def submit_order(self, order: Order) -> TransitionResult:
        """Submit order for payment."""
        if not self._state_machine.can_transition(order, OrderEvent.SUBMIT):
            raise ValueError("Order cannot be submitted in current state")

        return await self._state_machine.transition(
            order,
            OrderEvent.SUBMIT,
            context={"user_id": order.customer_id}
        )
```

---

## 4. Change Management

### 4.1 Versioning Strategy

**Semantic Versioning**:
- **Major**: New states, removed transitions
- **Minor**: New events, additional guards
- **Patch**: Side effect optimizations

### 4.3 Change History

| Version | Date | Changes | Impact |
|---------|------|---------|--------|
| 1.0.0 | 2025-12-29 | Initial state machine definition | N/A |

---

## 5. Testing Requirements

### 5.1 Provider Tests

**State Machine Tests**:
```python
import pytest
from contracts.order.state_machine import (
    Order, OrderState, OrderEvent, VALID_TRANSITIONS
)

class TestStateTransitions:
    """Verify state transition correctness."""

    def test_valid_happy_path(self):
        """Test complete order lifecycle."""
        states = [
            (OrderState.DRAFT, OrderEvent.SUBMIT, OrderState.PENDING_PAYMENT),
            (OrderState.PENDING_PAYMENT, OrderEvent.PAYMENT_RECEIVED, OrderState.PAID),
            (OrderState.PAID, OrderEvent.START_PROCESSING, OrderState.PROCESSING),
            (OrderState.PROCESSING, OrderEvent.SHIP, OrderState.SHIPPED),
            (OrderState.SHIPPED, OrderEvent.DELIVER, OrderState.DELIVERED),
        ]

        for from_state, event, to_state in states:
            transition = next(
                (t for t in VALID_TRANSITIONS
                 if t.from_state == from_state and t.event == event),
                None
            )
            assert transition is not None
            assert transition.to_state == to_state

    def test_terminal_states_have_no_outgoing_transitions(self):
        """Terminal states should not have outgoing transitions."""
        terminal_states = {s for s in OrderState if s.is_terminal}

        for transition in VALID_TRANSITIONS:
            assert transition.from_state not in terminal_states
```

---

## 6. Documentation

### 6.1 Usage Examples

**Complete Workflow**:
```python
# Create order
order = Order(id="ord-123", items=[item1, item2], shipping_address="123 Main St")

# Submit for payment
result = await machine.transition(order, OrderEvent.SUBMIT)
assert result.success
assert order.state == OrderState.PENDING_PAYMENT

# Payment received
result = await machine.transition(order, OrderEvent.PAYMENT_RECEIVED)
assert order.state == OrderState.PAID
```

### 6.2 Common Patterns

**State-based UI rendering**:
```python
def get_order_actions(order: Order) -> List[str]:
    """Get available actions for order based on state."""
    events = machine.get_available_events(order)
    return [event.value for event in events]
```

### 6.3 Anti-Patterns

**Avoid**:
- Directly modifying `order.state` without state machine
- Ignoring `TransitionResult.success` flag
- Hardcoding state transition logic outside state machine

---

## 7. Traceability

### 7.1 Upstream Artifacts

```markdown
@spec: SPEC-06         # Order Management Specification
@req: REQ.06.01.01     # Order State Requirements
@adr: ADR-04           # State Machine Architecture Decision
```

### 7.2 Provider/Consumer Tags

**This Contract**:
```markdown
@icon: ICON-03:OrderStateMachine
```

---

## 10. Document Metadata

**Version**: 1.0.0
**Created**: 2025-12-29
**Last Updated**: 2025-12-29
**Contract Type**: State Machine
**Providers**: 1
**Consumers**: 5
**Complexity**: 4/5
**Token Count**: ~4000

# =============================================================================
# END OF ICON-03: Order Lifecycle State Machine
# =============================================================================
