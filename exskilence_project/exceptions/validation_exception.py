from typing import Any, List, Optional

from exceptions.base_exception import ApplicationBaseException


class ValidationException(ApplicationBaseException):
    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[List[Any]] = None,
    ):
        super().__init__(message, status_code=400, details=details or [])
