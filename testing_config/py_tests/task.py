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


def _seed_admin(client):
    from repositories.user_repository import UserRepository
    from utils.passwords import hash_password

    UserRepository().create_user(
        "Admin",
        "task7admin@example.com",
        hash_password("Task7!adm"),
        "admin",
    )
    _login_web(client, "task7admin@example.com", "Task7!adm")


def test_admin_category_new_get_renders_form_fields(client):
    """GET /admin/categories/new shows structured category form (name, description, form-card)."""
    try:
        _seed_admin(client)
        response = client.get("/admin/categories/new")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "form-card" in html
        assert 'name="name"' in html
        assert 'name="description"' in html
        assert "<textarea" in html
        assert 'method="post"' in html.lower()
    except Exception as error:
        pytest.fail(f"Category new form structure check failed: {error}")


def test_admin_category_post_creates_and_redirects_to_list(client):
    """Valid category POST redirects to the category list after create."""
    try:
        _seed_admin(client)
        response = client.post(
            "/admin/categories/new",
            data={
                "name": "Electronics Task7",
                "description": "Gadgets and devices",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        path = urlparse(response.headers.get("Location", "")).path
        assert path.rstrip("/") == "/admin/categories"
        listed = client.get("/admin/categories")
        assert listed.status_code == 200
        assert "Electronics Task7" in listed.get_data(as_text=True)
    except Exception as error:
        pytest.fail(f"Category create redirect check failed: {error}")


def test_admin_category_post_empty_name_shows_validation_ui(client):
    """Empty category name re-renders the form with validation messaging."""
    try:
        _seed_admin(client)
        response = client.post(
            "/admin/categories/new",
            data={"name": "", "description": ""},
        )
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "Category name is required" in html
        assert "form-errors" in html or "field-error" in html
    except Exception as error:
        pytest.fail(f"Category validation UI check failed: {error}")


def test_admin_store_new_get_renders_seller_select_and_category_grid(client):
    """Store form exposes seller select, category checkboxes, and active toggle."""
    try:
        from repositories.category_repository import CategoryRepository
        from repositories.user_repository import UserRepository
        from utils.passwords import hash_password

        UserRepository().create_user(
            "Seller One",
            "seller1@example.com",
            hash_password("s"),
            "seller",
        )
        CategoryRepository().create("Cat A", "desc")
        _seed_admin(client)
        response = client.get("/admin/stores/new")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "form-card" in html
        assert 'name="seller_id"' in html
        assert 'name="category_ids"' in html
        assert "checkbox-grid" in html
        assert 'name="is_active"' in html
    except Exception as error:
        pytest.fail(f"Store new form structure check failed: {error}")


def test_admin_store_post_creates_and_redirects_to_store_list(client):
    """Creating a store with seller and optional categories redirects to store list."""
    try:
        from repositories.category_repository import CategoryRepository
        from repositories.user_repository import UserRepository
        from utils.passwords import hash_password

        seller = UserRepository().create_user(
            "Seller Two",
            "seller2@example.com",
            hash_password("s"),
            "seller",
        )
        cat = CategoryRepository().create("Cat B", None)
        _seed_admin(client)
        response = client.post(
            "/admin/stores/new",
            data={
                "name": "Flagship Task7",
                "seller_id": str(seller.id),
                "is_active": "1",
                "category_ids": str(cat.id),
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        path = urlparse(response.headers.get("Location", "")).path
        assert path.rstrip("/") == "/admin/stores"
        listed = client.get("/admin/stores")
        assert listed.status_code == 200
        assert "Flagship Task7" in listed.get_data(as_text=True)
    except Exception as error:
        pytest.fail(f"Store create redirect check failed: {error}")


def test_seller_staff_stores_readonly_page_loads(client):
    """Seller session can open the read-only My stores page under /staff/stores."""
    try:
        from repositories.user_repository import UserRepository
        from utils.passwords import hash_password

        UserRepository().create_user(
            "Seller Three",
            "seller3@example.com",
            hash_password("Staff!77"),
            "seller",
        )
        _login_web(client, "seller3@example.com", "Staff!77")
        response = client.get("/staff/stores")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "Your stores" in html or "stores" in html.lower()
    except Exception as error:
        pytest.fail(f"Seller stores readonly page check failed: {error}")
