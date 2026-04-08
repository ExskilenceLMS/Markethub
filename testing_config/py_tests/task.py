import os
import sys
import uuid
from decimal import Decimal
from urllib.parse import urlparse

import pytest

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


def _seed_customer(email="t10cust@example.com", password="T10!cart"):
    from repositories.user_repository import UserRepository
    from utils.passwords import hash_password

    UserRepository().create_user("T10 Customer", email, hash_password(password), "customer")
    return email, password


def _seed_product(name="CartWidget", price="12.50", qty=20):
    from repositories.category_repository import CategoryRepository
    from repositories.product_repository import ProductRepository
    from repositories.user_repository import UserRepository
    from utils.passwords import hash_password

    sid = uuid.uuid4().hex[:10]
    seller = UserRepository().create_user(
        "T10Sell", f"t10sell_{sid}@e.com", hash_password("x"), "seller"
    )
    cat = CategoryRepository().create(f"T10Cat_{sid}", None)
    p = ProductRepository().create(
        name,
        "For cart tests",
        Decimal(price),
        qty,
        cat.id,
        seller.id,
        None,
    )
    return p.id


def test_guest_cart_redirects_to_login(client):
    """Unauthenticated GET /customer/cart sends the user to web login."""
    try:
        response = client.get("/customer/cart", follow_redirects=False)
        assert response.status_code == 302
        assert "login" in response.headers.get("Location", "").lower()
    except Exception as error:
        pytest.fail(f"Guest cart redirect check failed: {error}")


def test_customer_cart_page_renders_when_empty(client):
    """Logged-in customer sees the cart hub and empty-state copy with no lines."""
    try:
        email, pwd = _seed_customer()
        _login_web(client, email, pwd)
        response = client.get("/customer/cart")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "customer-hub" in html
        assert "Cart" in html
        assert "Your cart is empty" in html
    except Exception as error:
        pytest.fail(f"Empty cart page check failed: {error}")


def test_cart_add_post_redirects_to_products(client):
    """POST /customer/cart/add redirects back to the products catalog."""
    try:
        email, pwd = _seed_customer()
        pid = _seed_product()
        _login_web(client, email, pwd)
        response = client.post(
            "/customer/cart/add",
            data={"product_id": pid, "quantity": 2},
            follow_redirects=False,
        )
        assert response.status_code == 302
        path = urlparse(response.headers.get("Location", "")).path
        assert path.rstrip("/") == "/customer/products"
    except Exception as error:
        pytest.fail(f"Add-to-cart redirect check failed: {error}")


def test_cart_add_merges_quantity_same_product(client):
    """Two adds for the same product accumulate on one cart line."""
    try:
        email, pwd = _seed_customer()
        pid = _seed_product()
        _login_web(client, email, pwd)
        client.post("/customer/cart/add", data={"product_id": pid, "quantity": 2})
        client.post("/customer/cart/add", data={"product_id": pid, "quantity": 3})
        response = client.get("/customer/cart")
        html = response.get_data(as_text=True)
        assert "CartWidget" in html
        from repositories.cart_repository import CartRepository
        from repositories.user_repository import UserRepository

        with app.app_context():
            user = UserRepository().get_by_email(email)
            lines = CartRepository().list_by_user_id(user.id)
            assert len(lines) == 1
            assert lines[0].quantity == 5
        assert "₹62.50" in html or "62.50" in html
    except Exception as error:
        pytest.fail(f"Cart merge quantity check failed: {error}")


def test_cart_update_line_reflects_in_total(client):
    """Updating a line quantity recalculates the cart total on the page."""
    try:
        email, pwd = _seed_customer()
        pid = _seed_product(price="10.00")
        _login_web(client, email, pwd)
        client.post("/customer/cart/add", data={"product_id": pid, "quantity": 2})
        from repositories.cart_repository import CartRepository
        from repositories.user_repository import UserRepository

        with app.app_context():
            user = UserRepository().get_by_email(email)
            lines = CartRepository().list_by_user_id(user.id)
            line_id = lines[0].id
        response = client.post(
            f"/customer/cart/{line_id}/update",
            data={"quantity": 5},
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "₹50.00" in html or "50.00" in html
    except Exception as error:
        pytest.fail(f"Cart line update total check failed: {error}")


def test_cart_clear_empties_cart(client):
    """POST /customer/cart/clear removes all lines."""
    try:
        email, pwd = _seed_customer()
        pid1 = _seed_product("P1", "5.00")
        pid2 = _seed_product("P2", "7.00")
        _login_web(client, email, pwd)
        client.post("/customer/cart/add", data={"product_id": pid1, "quantity": 1})
        client.post("/customer/cart/add", data={"product_id": pid2, "quantity": 1})
        response = client.post("/customer/cart/clear", follow_redirects=True)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "Your cart is empty" in html
    except Exception as error:
        pytest.fail(f"Cart clear check failed: {error}")
