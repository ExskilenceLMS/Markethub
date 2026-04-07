from typing import Any, Dict, Optional, Tuple

from exceptions import ValidationException


def parse_category_form(data: Optional[Dict[str, Any]]) -> Tuple[str, Optional[str]]:
    if not data or not isinstance(data, dict):
        raise ValidationException("Invalid form data")

    name = data.get("name")
    if name is None or not isinstance(name, str) or not name.strip():
        raise ValidationException("Category name is required", details=["name"])

    desc = data.get("description")
    if desc is not None and isinstance(desc, str):
        d = desc.strip() or None
    else:
        d = None

    return name.strip(), d
