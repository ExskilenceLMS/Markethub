from typing import Any, Dict, List, Optional, Tuple

from exceptions import ValidationException


def parse_store_form(data: Optional[Dict[str, Any]]) -> Tuple[str, int, bool, List[int]]:
    if not data or not isinstance(data, dict):
        raise ValidationException("Invalid form data")

    name = data.get("name")
    if name is None or not isinstance(name, str) or not name.strip():
        raise ValidationException("Store name is required", details=["name"])

    seller_raw = data.get("seller_id")
    try:
        seller_id = int(seller_raw)
    except (TypeError, ValueError):
        raise ValidationException("Seller is required", details=["seller_id"])

    raw_active = data.get("is_active")
    is_active = raw_active in (True, "true", "1", "on", 1)

    raw_ids = data.get("category_ids")
    if raw_ids is None:
        category_ids = []
    elif isinstance(raw_ids, list):
        category_ids = []
        for x in raw_ids:
            try:
                category_ids.append(int(x))
            except (TypeError, ValueError):
                pass
    else:
        try:
            category_ids = [int(raw_ids)]
        except (TypeError, ValueError):
            category_ids = []

    return name.strip(), seller_id, is_active, category_ids
