import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

from exceptions import ValidationException

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

SELF_REGISTER_ROLES = {"customer"}


def validate_email_format(email: str) -> None:
    if not email or not isinstance(email, str):
        raise ValidationException("Email is required", details=["email"])
    e = email.strip()
    if not e or not _EMAIL_RE.match(e):
        raise ValidationException("Invalid email format", details=["email"])


def validate_password_present(password: Optional[str]) -> None:
    if password is None or not isinstance(password, str) or not password.strip():
        raise ValidationException("Password is required", details=["password"])


def validate_register_payload(data: Optional[Dict[str, Any]]) -> Tuple[str, str, str, str]:
    if not data or not isinstance(data, dict):
        raise ValidationException("JSON body is required")

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role_raw = data.get("role", "customer")

    if name is None or not isinstance(name, str) or not name.strip():
        raise ValidationException("Name is required", details=["name"])

    validate_email_format(email)
    validate_password_present(password)

    if role_raw is None or not isinstance(role_raw, str) or not role_raw.strip():
        raise ValidationException("Role is required", details=["role"])

    role = role_raw.strip().lower()
    if role not in SELF_REGISTER_ROLES:
        raise ValidationException(
            "Self-registration is only allowed for the customer role",
            details=["role"],
        )

    return name.strip(), email.strip().lower(), password, role


def validate_login_payload(data: Optional[Dict[str, Any]]) -> Tuple[str, str]:
    if not data or not isinstance(data, dict):
        raise ValidationException("JSON body is required")

    email = data.get("email")
    password = data.get("password")

    validate_email_format(email)
    validate_password_present(password)

    return email.strip().lower(), password


def validate_role_value(role: str, allowed: Sequence[str]) -> None:
    allowed_list = list(allowed)
    if role not in allowed_list:
        raise ValidationException(
            "Invalid role",
            details=[{"field": "role", "allowed": allowed_list}],
        )
