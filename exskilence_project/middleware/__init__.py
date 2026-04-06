from flask import Flask

from middleware.error_handlers import register_error_handlers


def register_middleware(app: Flask) -> None:
    register_error_handlers(app)
