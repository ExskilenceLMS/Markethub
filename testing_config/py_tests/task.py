import os
import sys
from pathlib import Path
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


def test_home_page_includes_header_main_footer_layout(client):
    """GET / returns 200 and HTML that includes base layout regions (navbar, main, footer)."""
    try:
        response = client.get("/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "site-header" in html
        assert "<main>" in html
        assert "site-footer" in html
        assert "base.css" in html
    except Exception as error:
        pytest.fail(f"Home base layout check failed: {error}")


def test_login_page_has_post_form_email_password(client):
    """GET /login returns 200 with POST form fields email/password and layout chrome."""
    try:
        response = client.get("/login")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'method="post"' in html.lower()
        assert 'name="email"' in html
        assert 'name="password"' in html
        assert 'type="submit"' in html
        assert "site-header" in html
        assert "Register" in html
    except Exception as error:
        pytest.fail(f"Login page structure check failed: {error}")


def test_register_page_inherits_layout_and_flash_slot(client):
    """GET /register returns 200 with card form; base template wires flash_messages (see templates/base.html)."""
    try:
        response = client.get("/register")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "Create account" in html
        assert 'name="name"' in html
        assert "site-header" in html
        assert 'name="role"' in html and "customer" in html
        assert "site-footer" in html
        base_tpl = Path(exskilence_path) / "templates" / "base.html"
        assert base_tpl.is_file()
        assert "flash_messages.html" in base_tpl.read_text(encoding="utf-8")
    except Exception as error:
        pytest.fail(f"Register page layout check failed: {error}")


def test_web_login_success_redirects_to_home(client):
    """After register, logout, and valid web form login, response redirects to home (/)."""
    try:
        client.post(
            "/register",
            data={
                "name": "Task Four User",
                "email": "task4user@example.com",
                "password": "Task4Test!pass",
                "role": "customer",
            },
            follow_redirects=True,
        )
        client.post("/logout", follow_redirects=True)

        response = client.post(
            "/login",
            data={
                "email": "task4user@example.com",
                "password": "Task4Test!pass",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        loc = response.headers.get("Location", "")
        path = urlparse(loc).path or "/"
        assert path == "/" or path == ""
        assert "login" not in loc.lower()
    except Exception as error:
        pytest.fail(f"Web login redirect to home check failed: {error}")
