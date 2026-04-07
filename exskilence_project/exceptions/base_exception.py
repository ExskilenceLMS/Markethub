from typing import Any, List, Optional


class ApplicationBaseException(Exception):
    """Base class for application (business-layer) errors with HTTP semantics."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        details: Optional[List[Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details if details is not None else []
