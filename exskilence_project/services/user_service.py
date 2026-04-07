from typing import Any, Dict, List, Mapping, Optional, Union

from exceptions import AuthorizationException, NotFoundException, ValidationException
from repositories.user_repository import UserRepository
from utils.passwords import hash_password, verify_password
from validators.user_validator import validate_login_payload, validate_register_payload


class UserService:
    def __init__(self, user_repository: Optional[UserRepository] = None):
        self._repo = user_repository or UserRepository()

    def register(self, data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        name, email, password, role = validate_register_payload(data)
        if self._repo.get_by_email(email):
            raise ValidationException(
                "Email is already registered",
                details=["email"],
            )
        password_hash = hash_password(password)
        user = self._repo.create_user(name, email, password_hash, role)
        return user.to_public_dict()

    def login(self, data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        email, password = validate_login_payload(data)
        user = self._repo.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise ValidationException("Invalid email or password")
        return user.to_public_dict()

    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found")
        return user.to_public_dict()

    @staticmethod
    def require_authenticated(session: Union[Mapping[str, Any], Any]) -> int:
        uid = session.get("user_id")
        if uid is None:
            raise AuthorizationException(
                "Authentication required",
                status_code=401,
            )
        return int(uid)

    @staticmethod
    def require_roles(
        session: Union[Mapping[str, Any], Any],
        allowed_roles: List[str],
    ) -> None:
        UserService.require_authenticated(session)
        role = session.get("role")
        if not isinstance(role, str) or role not in allowed_roles:
            raise AuthorizationException(
                "You do not have permission to perform this action",
            )
