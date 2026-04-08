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


def _seed_admin(client, email="task8admin@example.com", password="Task8!adm"):
    from repositories.user_repository import UserRepository
    from utils.passwords import hash_password

    UserRepository().create_user("Task8 Admin", email, hash_password(password), "admin")
    _login_web(client, email, password)
    return email, password


def _seller_with_store_category():
    from repositories.category_repository import CategoryRepository
    from repositories.store_repository import StoreRepository
    from repositories.user_repository import UserRepository
    from utils.passwords import hash_password

    seller = UserRepository().create_user(
        "Task8 Seller",
        "task8seller@example.com",
        hash_password("Task8!sel"),
        "seller",
    )
    cat = CategoryRepository().create("Task8 Cat", "for products")
    StoreRepository().create("Task8 Store", seller.id, True, [cat.id])
    return seller, cat


def test_admin_product_new_get_renders_crud_form(client):
    """Admin GET /admin/products/new shows structured product form including seller select."""
    try:
        _seed_admin(client)
        from repositories.user_repository import UserRepository
        from utils.passwords import hash_password

        UserRepository().create_user("S", "s@e.com", hash_password("x"), "seller")
        from repositories.category_repository import CategoryRepository

        CategoryRepository().create("C1", None)

        response = client.get("/admin/products/new")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "form-card" in html
        assert 'name="name"' in html
        assert 'name="price"' in html
        assert 'name="quantity"' in html
        assert 'name="category_id"' in html
        assert 'name="seller_id"' in html
    except Exception as error:
        pytest.fail(f"Admin product new form check failed: {error}")


def test_admin_product_create_post_redirects_to_list(client):
    """Valid admin product POST redirects to /admin/products and lists the product."""
    try:
        _seed_admin(client)
        from repositories.category_repository import CategoryRepository
        from repositories.user_repository import UserRepository
        from utils.passwords import hash_password

        seller = UserRepository().create_user("Sv", "sv@e.com", hash_password("x"), "seller")
        cat = CategoryRepository().create("CatAdm", None)
        response = client.post(
            "/admin/products/new",
            data={
                "name": "Widget Task8",
                "description": "A widget",
                "price": "19.99",
                "quantity": "5",
                "category_id": str(cat.id),
                "seller_id": str(seller.id),
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert urlparse(response.headers.get("Location", "")).path.rstrip("/") == "/admin/products"
        listed = client.get("/admin/products")
        assert listed.status_code == 200
        assert "Widget Task8" in listed.get_data(as_text=True)
    except Exception as error:
        pytest.fail(f"Admin product create redirect check failed: {error}")


def test_admin_product_post_empty_name_shows_validation(client):
    """Missing product name re-renders the form with validation errors."""
    try:
        _seed_admin(client)
        from repositories.category_repository import CategoryRepository
        from repositories.user_repository import UserRepository
        from utils.passwords import hash_password

        seller = UserRepository().create_user("S2", "s2@e.com", hash_password("x"), "seller")
        CategoryRepository().create("Cx", None)
        response = client.post(
            "/admin/products/new",
            data={
                "name": "",
                "price": "10",
                "quantity": "1",
                "category_id": "1",
                "seller_id": str(seller.id),
            },
        )
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "Product name is required" in html
    except Exception as error:
        pytest.fail(f"Admin product validation UI check failed: {error}")


def test_seller_product_new_get_renders_form_when_store_has_category(client):
    """Seller with a store linked to a category can open the add-product form."""
    try:
        seller, _cat = _seller_with_store_category()
        _login_web(client, "task8seller@example.com", "Task8!sel")
        response = client.get("/staff/products/new")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "form-card" in html
        assert 'name="name"' in html and 'name="price"' in html
        assert 'name="category_id"' in html
        assert 'name="seller_id"' not in html
    except Exception as error:
        pytest.fail(f"Seller product new form check failed: {error}")


def test_seller_product_create_post_redirects_to_list(client):
    """Seller can create a product assigned to an allowed category."""
    try:
        seller, cat = _seller_with_store_category()
        _login_web(client, "task8seller@example.com", "Task8!sel")
        response = client.post(
            "/staff/products/new",
            data={
                "name": "Seller Item 8",
                "description": "From seller",
                "price": "8.50",
                "quantity": "12",
                "category_id": str(cat.id),
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert urlparse(response.headers.get("Location", "")).path.rstrip("/") == "/staff/products"
        listed = client.get("/staff/products")
        assert "Seller Item 8" in listed.get_data(as_text=True)
    except Exception as error:
        pytest.fail(f"Seller product create check failed: {error}")


def test_admin_product_delete_removes_product(client):
    """Admin POST delete removes the product from the catalog list."""
    try:
        _seed_admin(client)
        from repositories.category_repository import CategoryRepository
        from repositories.user_repository import UserRepository
        from utils.passwords import hash_password

        seller = UserRepository().create_user("Sd", "sd@e.com", hash_password("x"), "seller")
        cat = CategoryRepository().create("Cd", None)
        client.post(
            "/admin/products/new",
            data={
                "name": "ToDelete8",
                "price": "1.00",
                "quantity": "1",
                "category_id": str(cat.id),
                "seller_id": str(seller.id),
            },
            follow_redirects=True,
        )
        listed_before = client.get("/admin/products")
        html_b = listed_before.get_data(as_text=True)
        assert "ToDelete8" in html_b
        import re

        m = re.search(r"/admin/products/(\d+)/delete", html_b)
        assert m, "expected delete form with product id"
        pid = m.group(1)
        del_resp = client.post(
            "/admin/products/%s/delete" % pid,
            follow_redirects=False,
        )
        assert del_resp.status_code == 302
        listed_after = client.get("/admin/products")
        assert "ToDelete8" not in listed_after.get_data(as_text=True)
    except Exception as error:
        pytest.fail(f"Admin product delete check failed: {error}")
