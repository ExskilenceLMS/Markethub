from typing import Any, List, Optional

from exceptions.base_exception import ApplicationBaseException


class NotFoundException(ApplicationBaseException):
    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[List[Any]] = None,
    ):
        super().__init__(message, status_code=404, details=details or [])
