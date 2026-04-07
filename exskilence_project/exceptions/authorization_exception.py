from typing import Any, List, Optional

from exceptions.base_exception import ApplicationBaseException


class AuthorizationException(ApplicationBaseException):
    def __init__(
        self,
        message: str = "Forbidden",
        details: Optional[List[Any]] = None,
    ):
        super().__init__(message, status_code=403, details=details or [])
