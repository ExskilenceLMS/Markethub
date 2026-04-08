from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional, Tuple

from exceptions import ValidationException


def parse_product_payload(
    data: Optional[Dict[str, Any]],
    *,
    require_seller_id: bool,
) -> Tuple[str, Optional[str], Decimal, int, int, Optional[int], Optional[str]]:
    if not data or not isinstance(data, dict):
        raise ValidationException("Invalid form data")

    name = data.get("name")
    if name is None or not isinstance(name, str) or not name.strip():
        raise ValidationException("Product name is required", details=["name"])

    desc_raw = data.get("description")
    if desc_raw is not None and isinstance(desc_raw, str):
        description = desc_raw.strip() or None
    else:
        description = None

    price_raw = data.get("price")
    try:
        price = Decimal(str(price_raw).strip())
    except (InvalidOperation, AttributeError, TypeError, ValueError):
        raise ValidationException("Valid price is required", details=["price"])
    if price <= 0:
        raise ValidationException("Price must be greater than zero", details=["price"])

    qty_raw = data.get("quantity")
    try:
        quantity = int(qty_raw)
    except (TypeError, ValueError):
        raise ValidationException("Quantity is required", details=["quantity"])
    if quantity < 0:
        raise ValidationException("Quantity cannot be negative", details=["quantity"])

    try:
        category_id = int(data.get("category_id"))
    except (TypeError, ValueError):
        raise ValidationException("Category is required", details=["category_id"])

    seller_id: Optional[int] = None
    if require_seller_id:
        try:
            seller_id = int(data.get("seller_id"))
        except (TypeError, ValueError):
            raise ValidationException("Seller is required", details=["seller_id"])

    img = data.get("image_url")
    if img is not None and isinstance(img, str):
        image_url = img.strip() or None
    else:
        image_url = None

    return name.strip(), description, price, quantity, category_id, seller_id, image_url
