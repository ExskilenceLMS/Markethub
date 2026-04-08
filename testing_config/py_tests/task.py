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


def _seed_customer(email="task9cust@example.com", password="Task9!pwd"):
    from repositories.user_repository import UserRepository
    from utils.passwords import hash_password

    UserRepository().create_user("Task9 Customer", email, hash_password(password), "customer")
    return email, password


def test_guest_customer_dashboard_redirects_to_login(client):
    """Unauthenticated users cannot open the customer dashboard."""
    try:
        response = client.get("/customer/", follow_redirects=False)
        assert response.status_code == 302
        assert "login" in response.headers.get("Location", "").lower()
    except Exception as error:
        pytest.fail(f"Guest customer redirect check failed: {error}")


def test_customer_dashboard_shows_profile_and_shop_nav(client):
    """Customer GET /customer/ shows profile card and shop navigation links."""
    try:
        email, pwd = _seed_customer()
        _login_web(client, email, pwd)
        response = client.get("/customer/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "customer-hub" in html
        assert "My account" in html
        assert "customer-profile-card" in html
        assert "customer-hub__nav" in html
        assert "/customer/categories" in html
        assert "/customer/products" in html
        assert email in html
    except Exception as error:
        pytest.fail(f"Customer dashboard content check failed: {error}")


def test_customer_categories_page_renders_for_customer(client):
    """Customer can load the categories browse page."""
    try:
        email, pwd = _seed_customer()
        _login_web(client, email, pwd)
        response = client.get("/customer/categories")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "customer-hub" in html
        assert "Categories" in html
        assert "customer-category-grid" in html or "No categories yet" in html
    except Exception as error:
        pytest.fail(f"Customer categories page check failed: {error}")


def test_customer_products_page_renders_catalog(client):
    """Customer products page shows filter form and product grid when items exist."""
    try:
        from repositories.category_repository import CategoryRepository
        from repositories.product_repository import ProductRepository
        from repositories.user_repository import UserRepository
        from utils.passwords import hash_password

        email, pwd = _seed_customer()
        seller = UserRepository().create_user("S9", "s9@e.com", hash_password("x"), "seller")
        cat = CategoryRepository().create("Cat9", None)
        ProductRepository().create(
            "Prod9",
            "Nice item",
            __import__("decimal").Decimal("9.99"),
            3,
            cat.id,
            seller.id,
            None,
        )
        _login_web(client, email, pwd)
        response = client.get("/customer/products")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "customer-filter-form" in html
        assert "customer-product-grid" in html
        assert "Prod9" in html
    except Exception as error:
        pytest.fail(f"Customer products catalog check failed: {error}")


def test_customer_login_redirects_to_customer_home(client):
    """Web login as customer redirects to /customer (dashboard)."""
    try:
        email, pwd = _seed_customer("redir9@example.com", "Redir9!x")
        response = _login_web(client, email, pwd)
        assert response.status_code == 302
        path = urlparse(response.headers.get("Location", "")).path
        assert path.rstrip("/") == "/customer"
    except Exception as error:
        pytest.fail(f"Customer login redirect check failed: {error}")


def test_non_customer_blocked_from_customer_routes(client):
    """Seller session is redirected away from customer-only routes."""
    try:
        from repositories.user_repository import UserRepository
        from utils.passwords import hash_password

        UserRepository().create_user("NotCust", "seller9@e.com", hash_password("y"), "seller")
        _login_web(client, "seller9@e.com", "y")
        response = client.get("/customer/", follow_redirects=False)
        assert response.status_code == 302
        assert "login" in response.headers.get("Location", "").lower()
    except Exception as error:
        pytest.fail(f"Non-customer blocked from customer routes check failed: {error}")
