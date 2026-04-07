import logging
import os
import sys
from pathlib import Path

import pytest
from flask import Blueprint

# Path setup: project root = three levels up from this file (testing_config/py_tests/task.py)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
exskilence_path = os.path.join(project_root, "exskilence_project")
sys.path.insert(0, exskilence_path)
os.chdir(exskilence_path)

os.environ["FLASK_ENV"] = "testing"

from app import app
from exceptions import (
    AuthorizationException,
    NotFoundException,
    ValidationException,
)
from models import db

app.config["TESTING"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

_TASK2_BP_NAME = "task2_pytest_exceptions"


def _register_task2_pytest_blueprint() -> None:
    if _TASK2_BP_NAME in app.blueprints:
        return

    bp = Blueprint(_TASK2_BP_NAME, __name__, url_prefix="/__task2_pytest")

    @bp.get("/validation")
    def _raise_validation():
        raise ValidationException(
            message="validation pytest",
            details=["invalid_field"],
        )

    @bp.get("/not-found")
    def _raise_not_found():
        raise NotFoundException(
            message="resource pytest not found",
            details=[],
        )

    @bp.get("/auth")
    def _raise_auth():
        raise AuthorizationException(
            message="authorization pytest denied",
            details=[],
        )

    app.register_blueprint(bp)


_register_task2_pytest_blueprint()


@pytest.fixture
def client():
    """Test client with a fresh in-memory database."""
    with app.test_client() as c:
        with app.app_context():
            db.create_all()
            yield c
            db.drop_all()


def _assert_standard_error_envelope(payload: dict, *, expected_message: str) -> None:
    assert payload is not None
    assert payload.get("success") is False
    err = payload.get("error")
    assert isinstance(err, dict)
    assert err.get("message") == expected_message
    assert "details" in err
    assert isinstance(err.get("details"), list)


def test_unknown_route_returns_standard_error_envelope(client):
    """Unregistered URL is handled as HTTP error and returns the standard error JSON envelope."""
    try:
        response = client.get("/api/__no_such_route_task2__")
        assert response.status_code == 404
        payload = response.get_json()
        _assert_standard_error_envelope(
            payload,
            expected_message=(
                "The requested URL was not found on the server. "
                "If you entered the URL manually please check your spelling and try again."
            ),
        )
    except Exception as error:
        pytest.fail(f"Unknown route error envelope check failed: {error}")


def test_validation_exception_returns_400_standard_error_envelope(client):
    """ValidationException is handled globally and returns 400 with the standard error envelope."""
    try:
        response = client.get("/__task2_pytest/validation")
        assert response.status_code == 400
        payload = response.get_json()
        _assert_standard_error_envelope(
            payload,
            expected_message="validation pytest",
        )
        assert payload["error"]["details"] == ["invalid_field"]
    except Exception as error:
        pytest.fail(f"ValidationException error envelope check failed: {error}")


def test_not_found_exception_returns_404_standard_error_envelope(client):
    """NotFoundException is handled globally and returns 404 with the standard error envelope."""
    try:
        response = client.get("/__task2_pytest/not-found")
        assert response.status_code == 404
        payload = response.get_json()
        _assert_standard_error_envelope(
            payload,
            expected_message="resource pytest not found",
        )
    except Exception as error:
        pytest.fail(f"NotFoundException error envelope check failed: {error}")


def test_authorization_exception_returns_403_standard_error_envelope(client):
    """AuthorizationException is handled globally and returns 403 with the standard error envelope."""
    try:
        response = client.get("/__task2_pytest/auth")
        assert response.status_code == 403
        payload = response.get_json()
        _assert_standard_error_envelope(
            payload,
            expected_message="authorization pytest denied",
        )
    except Exception as error:
        pytest.fail(f"AuthorizationException error envelope check failed: {error}")


def test_validation_exception_logs_business_error(client, caplog):
    """Application exception handler logs business errors at WARNING for 4xx."""
    try:
        with caplog.at_level(logging.WARNING, logger="markethub"):
            client.get("/__task2_pytest/validation")
        messages = [r.getMessage() for r in caplog.records]
        matched = any(
            "Business error" in m and "validation pytest" in m for m in messages
        )
        assert matched, "Expected markethub WARNING log line for business error"
    except Exception as error:
        pytest.fail(f"Business error logging check failed: {error}")


def test_task_two_exception_logging_files_present():
    """Task 2: exception hierarchy, error handlers, and logging config exist on disk."""
    try:
        root = Path(project_root) / "exskilence_project"
        assert (root / "exceptions" / "base_exception.py").is_file()
        assert (root / "exceptions" / "validation_exception.py").is_file()
        assert (root / "exceptions" / "not_found_exception.py").is_file()
        assert (root / "exceptions" / "authorization_exception.py").is_file()
        assert (root / "middleware" / "error_handlers.py").is_file()
        assert (root / "config" / "logging_config.py").is_file()
    except Exception as error:
        pytest.fail(f"Task 2 file layout check failed: {error}")
