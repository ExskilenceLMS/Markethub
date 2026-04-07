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


def _login_web(client, email, password):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )


def test_unauthenticated_get_admin_redirects_to_login(client):
    """Guests hitting /admin are redirected to the web login page."""
    try:
        response = client.get("/admin/", follow_redirects=False)
        assert response.status_code == 302
        loc = response.headers.get("Location", "")
        assert "login" in loc.lower()
    except Exception as error:
        pytest.fail(f"Guest admin redirect check failed: {error}")


def test_customer_session_get_admin_redirects_to_login(client):
    """Non-admin roles cannot access the admin blueprint (controlled UI access)."""
    try:
        from repositories.user_repository import UserRepository
        from utils.passwords import hash_password

        UserRepository().create_user(
            "Cust",
            "custonly@example.com",
            hash_password("cust-pass-9"),
            "customer",
        )
        _login_web(client, "custonly@example.com", "cust-pass-9")
        response = client.get("/admin/", follow_redirects=False)
        assert response.status_code == 302
        loc = response.headers.get("Location", "")
        assert "login" in loc.lower()
    except Exception as error:
        pytest.fail(f"Customer blocked from admin check failed: {error}")


def test_admin_get_dashboard_returns_200_with_layout(client):
    """Admin session can load the dashboard with layout chrome from base_admin."""
    try:
        from repositories.user_repository import UserRepository
        from utils.passwords import hash_password

        UserRepository().create_user(
            "Admin User",
            "adminuser@example.com",
            hash_password("Adm1n!task6"),
            "admin",
        )
        _login_web(client, "adminuser@example.com", "Adm1n!task6")
        response = client.get("/admin/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "admin-layout" in html
        assert "admin-sidebar" in html
        assert "Admin dashboard" in html
    except Exception as error:
        pytest.fail(f"Admin dashboard load check failed: {error}")


def test_admin_dashboard_renders_stat_grid_with_user_counts(client):
    """Dashboard shows stat cards populated from AdminService counts."""
    try:
        from repositories.user_repository import UserRepository
        from utils.passwords import hash_password

        repo = UserRepository()
        repo.create_user("A", "a1@example.com", hash_password("x"), "admin")
        repo.create_user("S", "s1@example.com", hash_password("x"), "seller")
        repo.create_user("C", "c1@example.com", hash_password("x"), "customer")

        _login_web(client, "a1@example.com", "x")
        response = client.get("/admin/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "stat-grid" in html
        assert html.count("stat-card") >= 6
        assert "Total users" in html
        assert "Admins" in html and "Customers" in html
    except Exception as error:
        pytest.fail(f"Admin stat grid check failed: {error}")


def test_admin_users_page_accessible_for_admin_session(client):
    """Sidebar route /admin/users renders for an authenticated admin."""
    try:
        from repositories.user_repository import UserRepository
        from utils.passwords import hash_password

        UserRepository().create_user(
            "Admin Two",
            "admintwo@example.com",
            hash_password("pass-two-8"),
            "admin",
        )
        _login_web(client, "admintwo@example.com", "pass-two-8")
        response = client.get("/admin/users")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "admin-layout" in html
        assert "Users" in html
    except Exception as error:
        pytest.fail(f"Admin users page check failed: {error}")


def test_admin_login_redirects_to_admin_dashboard(client):
    """Web login as admin redirects to /admin/ (role-based landing)."""
    try:
        from repositories.user_repository import UserRepository
        from utils.passwords import hash_password

        UserRepository().create_user(
            "Redirect Admin",
            "rediradmin@example.com",
            hash_password("Redir!99"),
            "admin",
        )
        response = _login_web(client, "rediradmin@example.com", "Redir!99")
        assert response.status_code == 302
        path = urlparse(response.headers.get("Location", "")).path
        assert path.rstrip("/") == "/admin"
    except Exception as error:
        pytest.fail(f"Admin login redirect check failed: {error}")
