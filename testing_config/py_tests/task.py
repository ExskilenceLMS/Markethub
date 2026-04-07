import os
import sys
from urllib.parse import urlparse

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
    """Test client with a fresh in-memory database."""
    with app.test_client() as c:
        with app.app_context():
            db.create_all()
            yield c
            db.drop_all()


def test_login_page_renders_auth_form_and_register_link(client):
    """GET /login returns the auth card with email/password POST form and link to register."""
    try:
        response = client.get("/login")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "auth-page" in html
        assert "auth-card" in html
        assert 'method="post"' in html.lower()
        assert 'name="email"' in html
        assert 'name="password"' in html
        assert "btn-primary-fk" in html
        assert "register" in html.lower()
    except Exception as error:
        pytest.fail(f"Login page UI check failed: {error}")


def test_register_page_renders_confirm_password_and_role_select(client):
    """GET /register returns confirm password, role select, and auth chrome."""
    try:
        response = client.get("/register")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "auth-page" in html and "auth-card" in html
        assert 'name="confirm_password"' in html
        assert 'name="role"' in html
        assert 'name="name"' in html and 'name="email"' in html
        assert "customer" in html
    except Exception as error:
        pytest.fail(f"Register page UI check failed: {error}")


def test_login_post_invalid_password_shows_error_message(client):
    """Invalid web login re-renders login with standard error summary (no user enumeration)."""
    try:
        with app.app_context():
            from repositories.user_repository import UserRepository
            from utils.passwords import hash_password

            UserRepository().create_user(
                "U1",
                "u1@example.com",
                hash_password("realpass"),
                "customer",
            )

        response = client.post(
            "/login",
            data={"email": "u1@example.com", "password": "wrongpass"},
        )
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "Invalid email or password" in html
        assert "form-errors" in html
    except Exception as error:
        pytest.fail(f"Login error display check failed: {error}")


def test_register_post_password_mismatch_shows_validation(client):
    """Mismatched passwords re-render register with field-level error for confirm_password."""
    try:
        response = client.post(
            "/register",
            data={
                "name": "Test User",
                "email": "mismatch@example.com",
                "password": "one-pass",
                "confirm_password": "other-pass",
                "role": "customer",
            },
        )
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "Passwords do not match" in html
        assert "err-confirm_password" in html or "confirm_password" in html
    except Exception as error:
        pytest.fail(f"Password mismatch UI check failed: {error}")


def test_register_non_customer_role_shows_role_error(client):
    """Choosing seller/admin on the register form must show self-register role validation."""
    try:
        response = client.post(
            "/register",
            data={
                "name": "Seller Try",
                "email": "sellertry@example.com",
                "password": "samepass",
                "confirm_password": "samepass",
                "role": "seller",
            },
        )
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "Self-registration is only allowed" in html
        assert "form-errors" in html or "field-error" in html
    except Exception as error:
        pytest.fail(f"Non-customer register rejection UI check failed: {error}")


def test_register_customer_web_post_redirects_to_customer_area(client):
    """Successful customer registration redirects to the customer route (role-based landing)."""
    try:
        response = client.post(
            "/register",
            data={
                "name": "New Customer",
                "email": "newcust@example.com",
                "password": "RegPass!9",
                "confirm_password": "RegPass!9",
                "role": "customer",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        loc = response.headers.get("Location", "")
        path = urlparse(loc).path
        assert path.rstrip("/") == "/customer"
    except Exception as error:
        pytest.fail(f"Customer register redirect check failed: {error}")
