from typing import Any, Dict, Optional, Tuple

from exceptions import ValidationException


def parse_cart_product_quantity(data: Optional[Dict[str, Any]]) -> Tuple[int, int]:
    """Parse product_id and quantity for add-to-cart; quantity must be > 0."""
    if not data or not isinstance(data, dict):
        raise ValidationException("Invalid form data")

    pid_raw = data.get("product_id")
    try:
        product_id = int(pid_raw)
    except (TypeError, ValueError):
        raise ValidationException("Product is required", details=["product_id"])
    if product_id <= 0:
        raise ValidationException("Product is required", details=["product_id"])

    qty_raw = data.get("quantity")
    try:
        quantity = int(qty_raw)
    except (TypeError, ValueError):
        raise ValidationException("Quantity is required", details=["quantity"])
    if quantity <= 0:
        raise ValidationException("Quantity must be greater than zero", details=["quantity"])

    return product_id, quantity


def parse_cart_line_quantity(data: Optional[Dict[str, Any]]) -> int:
    """Parse quantity for updating a cart line; must be > 0."""
    if not data or not isinstance(data, dict):
        raise ValidationException("Invalid form data")

    qty_raw = data.get("quantity")
    try:
        quantity = int(qty_raw)
    except (TypeError, ValueError):
        raise ValidationException("Quantity is required", details=["quantity"])
    if quantity <= 0:
        raise ValidationException("Quantity must be greater than zero", details=["quantity"])

    return quantity
