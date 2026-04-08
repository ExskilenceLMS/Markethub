from typing import Any, Dict, Optional

from exceptions import ValidationException

STATUS_PLACED = "Placed"
STATUS_SHIPPED = "Shipped"
STATUS_DELIVERED = "Delivered"
STATUS_CANCELLED = "Cancelled"

ALL_ORDER_STATUSES = frozenset(
    {STATUS_PLACED, STATUS_SHIPPED, STATUS_DELIVERED, STATUS_CANCELLED}
)

_ALLOWED_TRANSITIONS = {
    STATUS_PLACED: {STATUS_SHIPPED, STATUS_CANCELLED},
    STATUS_SHIPPED: {STATUS_DELIVERED, STATUS_CANCELLED},
    STATUS_DELIVERED: set(),
    STATUS_CANCELLED: set(),
}


def parse_order_status_update(data: Optional[Dict[str, Any]]) -> str:
    if not data or not isinstance(data, dict):
        raise ValidationException("Invalid form data")
    raw = data.get("status")
    if raw is None or not isinstance(raw, str) or raw.strip() not in ALL_ORDER_STATUSES:
        raise ValidationException("Invalid status", details=["status"])
    return raw.strip()


def assert_valid_status_transition(current_status: str, new_status: str) -> None:
    allowed = _ALLOWED_TRANSITIONS.get(current_status, set())
    if new_status not in allowed:
        raise ValidationException(
            f"Cannot change order status from {current_status} to {new_status}",
            details=["status"],
        )


def next_status_choices(current_status: str):
    return sorted(_ALLOWED_TRANSITIONS.get(current_status, set()))
