from typing import Any, List, Optional, Tuple

from flask import jsonify, Response


def success_response(
    data: Any = None,
    message: Optional[str] = None,
    status_code: int = 200,
) -> Tuple[Response, int]:
    body: dict[str, Any] = {
        "success": True,
        "data": data if data is not None else {},
    }
    if message is not None:
        body["message"] = message
    return jsonify(body), status_code


def error_response(
    message: str,
    status_code: int = 400,
    details: Optional[List[Any]] = None,
) -> Tuple[Response, int]:
    body: dict[str, Any] = {
        "success": False,
        "error": {
            "message": message,
            "details": details if details is not None else [],
        },
    }
    return jsonify(body), status_code
