import os
import sys

import pytest

# Path setup: project root = three levels up from this file (testing_config/py_tests/task.py)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
exskilence_path = os.path.join(project_root, "exskilence_project")
sys.path.insert(0, exskilence_path)
os.chdir(exskilence_path)

os.environ["FLASK_ENV"] = "testing"

from app import app
from models import db

app.config["TESTING"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"


@pytest.fixture
def client():
    """Test client with a fresh in-memory database and users table."""
    with app.test_client() as c:
        with app.app_context():
            db.create_all()
            yield c
            db.drop_all()


def test_register_customer_success(client):
    """POST /api/auth/register creates a customer and returns 201 with public user fields (no password)."""
    try:
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Ada Customer",
                "email": "ada@example.com",
                "password": "hunter2secret",
                "role": "customer",
            },
        )
        assert response.status_code == 201
        payload = response.get_json()
        assert payload is not None
        assert payload.get("success") is True
        data = payload.get("data") or {}
        assert data.get("email") == "ada@example.com"
        assert data.get("role") == "customer"
        assert "password" not in data
        assert "password_hash" not in data
    except Exception as error:
        pytest.fail(f"Customer registration check failed: {error}")


def test_register_rejects_self_register_non_customer_role(client):
    """Self-registration must reject roles other than customer (Task 3)."""
    try:
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Bad Admin",
                "email": "admin-self@example.com",
                "password": "secretpass",
                "role": "admin",
            },
        )
        assert response.status_code == 400
        payload = response.get_json()
        assert payload is not None
        assert payload.get("success") is False
        assert "customer" in (payload.get("error") or {}).get("message", "").lower()
    except Exception as error:
        pytest.fail(f"Non-customer self-registration rejection check failed: {error}")


def test_login_success_sets_session_cookie(client):
    """POST /api/auth/login returns 200; follow-up GET /api/auth/me succeeds (session)."""
    try:
        reg = client.post(
            "/api/auth/register",
            json={
                "name": "Login User",
                "email": "login@example.com",
                "password": "correct-horse-battery",
                "role": "customer",
            },
        )
        assert reg.status_code == 201

        response = client.post(
            "/api/auth/login",
            json={"email": "login@example.com", "password": "correct-horse-battery"},
        )
        assert response.status_code == 200
        body = response.get_json()
        assert body.get("success") is True
        assert (body.get("data") or {}).get("email") == "login@example.com"

        me = client.get("/api/auth/me")
        assert me.status_code == 200
        me_data = (me.get_json() or {}).get("data") or {}
        assert me_data.get("email") == "login@example.com"
    except Exception as error:
        pytest.fail(f"Login and session check failed: {error}")


def test_auth_me_returns_401_when_unauthenticated(client):
    """GET /api/auth/me without a session returns 401 standard error envelope."""
    try:
        response = client.get("/api/auth/me")
        assert response.status_code == 401
        payload = response.get_json()
        assert payload is not None
        assert payload.get("success") is False
        err = payload.get("error") or {}
        assert "Authentication required" in err.get("message", "")
    except Exception as error:
        pytest.fail(f"Unauthenticated /me check failed: {error}")


def test_logout_clears_session(client):
    """POST /api/auth/logout clears the session so /api/auth/me returns 401."""
    try:
        client.post(
            "/api/auth/register",
            json={
                "name": "Logout User",
                "email": "logout@example.com",
                "password": "logout-secret-9",
                "role": "customer",
            },
        )
        client.post(
            "/api/auth/login",
            json={"email": "logout@example.com", "password": "logout-secret-9"},
        )
        assert client.get("/api/auth/me").status_code == 200

        out = client.post("/api/auth/logout")
        assert out.status_code == 200

        me = client.get("/api/auth/me")
        assert me.status_code == 401
    except Exception as error:
        pytest.fail(f"Logout session clear check failed: {error}")


def test_login_invalid_credentials_returns_generic_error(client):
    """Login with wrong password returns 400 and generic message (no user enumeration)."""
    try:
        client.post(
            "/api/auth/register",
            json={
                "name": "Bob",
                "email": "bob@example.com",
                "password": "right-password",
                "role": "customer",
            },
        )
        response = client.post(
            "/api/auth/login",
            json={"email": "bob@example.com", "password": "wrong-password"},
        )
        assert response.status_code == 400
        payload = response.get_json()
        assert payload.get("success") is False
        assert (payload.get("error") or {}).get("message") == "Invalid email or password"
    except Exception as error:
        pytest.fail(f"Invalid login error message check failed: {error}")
