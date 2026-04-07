import logging

from flask import Flask
from werkzeug.exceptions import HTTPException

from exceptions import ApplicationBaseException
from utils.response import error_response

logger = logging.getLogger("markethub")


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ApplicationBaseException)
    def handle_application_exception(exc: ApplicationBaseException):
        log = logger.warning if exc.status_code < 500 else logger.error
        log(
            "Business error: %s | status=%s | details=%s",
            exc.message,
            exc.status_code,
            exc.details,
        )
        return error_response(
            exc.message,
            status_code=exc.status_code,
            details=exc.details,
        )

    @app.errorhandler(HTTPException)
    def handle_http_exception(exc: HTTPException):
        if exc.code and exc.code >= 500:
            logger.error("HTTP %s: %s", exc.code, exc.description)
        else:
            logger.warning("HTTP %s: %s", exc.code, exc.description)
        message = exc.description or exc.name or "Request error"
        return error_response(
            message,
            status_code=exc.code or 500,
            details=[],
        )

    @app.errorhandler(Exception)
    def handle_unexpected_exception(exc: Exception):
        if app.debug:
            raise exc
        logger.exception("Unhandled error: %s", exc)
        return error_response(
            "An unexpected error occurred. Please try again later.",
            status_code=500,
            details=[],
        )
