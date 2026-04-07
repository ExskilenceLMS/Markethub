from typing import Any, Dict, List

from exceptions import ValidationException


def validation_exception_to_field_errors(exc: ValidationException) -> Dict[str, List[str]]:
    """
    Map ValidationException to template-friendly { field_name: [messages], '_form': [...] }.
    """
    out: Dict[str, List[str]] = {}
    details = exc.details or []

    if not details:
        out.setdefault("_form", []).append(exc.message)
        return out

    for item in details:
        if isinstance(item, str):
            out.setdefault(item, []).append(exc.message)
        elif isinstance(item, dict):
            field = item.get("field")
            if field:
                out.setdefault(str(field), []).append(exc.message)
            else:
                out.setdefault("_form", []).append(exc.message)
        else:
            out.setdefault("_form", []).append(exc.message)

    if not out:
        out.setdefault("_form", []).append(exc.message)
    return out
