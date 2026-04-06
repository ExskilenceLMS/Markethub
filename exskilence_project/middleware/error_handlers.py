from flask import Flask

from exceptions import AppException
from utils.response import error_response


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppException)
    def handle_app_exception(exc: AppException):
        return error_response(exc.message, status_code=exc.status_code)

    @app.errorhandler(404)
    def handle_not_found(_e):
        return error_response("Not found", status_code=404, code="NOT_FOUND")

    @app.errorhandler(500)
    def handle_server_error(_e):
        return error_response(
            "Internal server error",
            status_code=500,
            code="INTERNAL_ERROR",
        )
