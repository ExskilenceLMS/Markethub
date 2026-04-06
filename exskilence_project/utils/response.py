from typing import Any, Optional

from flask import jsonify, Response


def success_response(
    data: Any = None,
    message: str = "OK",
    status_code: int = 200,
    meta: Optional[dict] = None,
) -> tuple[Response, int]:
    body: dict[str, Any] = {
        "success": True,
        "message": message,
        "data": data,
    }
    if meta is not None:
        body["meta"] = meta
    return jsonify(body), status_code


def error_response(
    message: str,
    status_code: int = 400,
    errors: Optional[list] = None,
    code: Optional[str] = None,
) -> tuple[Response, int]:
    body: dict[str, Any] = {
        "success": False,
        "message": message,
        "errors": errors if errors is not None else [],
    }
    if code:
        body["code"] = code
    return jsonify(body), status_code
