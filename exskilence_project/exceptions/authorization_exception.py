from typing import Any, List, Optional

from exceptions.base_exception import ApplicationBaseException


class AuthorizationException(ApplicationBaseException):
    def __init__(
        self,
        message: str = "Forbidden",
        details: Optional[List[Any]] = None,
        status_code: int = 403,
    ):
        super().__init__(message, status_code=status_code, details=details or [])
