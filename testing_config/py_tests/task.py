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
os.environ["DATABASE_URI"] = "sqlite:///:memory:"

from app import app
from models import db

app.config["TESTING"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"


@pytest.fixture
def client():
    """Flask client with isolated in-memory schema per test."""
    with app.test_client() as c:
        with app.app_context():
            db.create_all()
            yield c
            db.session.remove()
            db.drop_all()


def _login_web(client, email, password):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )


def _seed_user(role, name, password="pass123!", email=None):
    from repositories.user_repository import UserRepository
    from utils.passwords import hash_password

    user_email = email or f"{role}_{uuid.uuid4().hex[:10]}@example.com"
    user = UserRepository().create_user(name, user_email, hash_password(password), role)
    return user.id, user.email, password


def _seed_product(name="InvItem", price="25.00", quantity=10):
    from repositories.category_repository import CategoryRepository
    from repositories.product_repository import ProductRepository

    seller_id, _, _ = _seed_user("seller", "Inventory Seller", password="sellerPass1")
    suffix = uuid.uuid4().hex[:8]
    cat = CategoryRepository().create(f"InvCat_{suffix}", "Inventory tests")
    product = ProductRepository().create(
        name,
        "Inventory test product",
        Decimal(price),
        quantity,
        cat.id,
        seller_id,
        None,
    )
    return product.id


def test_guest_cannot_access_cart(client):
    """Guests should be redirected from customer cart."""
    try:
        response = client.get("/customer/cart", follow_redirects=False)
        assert response.status_code == 302
        assert "login" in response.headers.get("Location", "").lower()
    except Exception as error:
        pytest.fail(f"Guest cart access guard check failed: {error}")


def test_place_order_reduces_stock_and_clears_cart(client):
    """Placing order from cart deducts product stock and empties the cart."""
    try:
        customer_id, customer_email, pwd = _seed_user("customer", "Inventory Customer", password="custPass1")
        product_id = _seed_product(quantity=9)
        _login_web(client, customer_email, pwd)

        client.post("/customer/cart/add", data={"product_id": product_id, "quantity": 4})
        response = client.post("/customer/orders/place", follow_redirects=False)

        assert response.status_code == 302
        assert urlparse(response.headers.get("Location", "")).path.rstrip("/") == "/customer/orders"

        from repositories.cart_repository import CartRepository
        from repositories.order_repository import OrderRepository
        from repositories.product_repository import ProductRepository

        with app.app_context():
            refreshed = ProductRepository().get_by_id(product_id)
            assert refreshed is not None
            assert refreshed.quantity == 5
            assert len(OrderRepository().list_by_user_id(customer_id)) == 1
            assert CartRepository().list_by_user_id(customer_id) == []
    except Exception as error:
        pytest.fail(f"Stock deduction and cart clear check failed: {error}")


def test_place_order_blocks_when_quantity_exceeds_stock(client):
    """Overselling is blocked when cart quantity is greater than available stock."""
    try:
        customer_id, customer_email, pwd = _seed_user("customer", "LowStock Customer", password="custPass2")
        product_id = _seed_product(name="LowStockItem", quantity=2)
        _login_web(client, customer_email, pwd)

        client.post("/customer/cart/add", data={"product_id": product_id, "quantity": 3})
        response = client.post("/customer/orders/place", follow_redirects=False)

        assert response.status_code == 302
        assert urlparse(response.headers.get("Location", "")).path.rstrip("/") == "/customer/cart"

        from repositories.cart_repository import CartRepository
        from repositories.order_repository import OrderRepository
        from repositories.product_repository import ProductRepository

        with app.app_context():
            refreshed = ProductRepository().get_by_id(product_id)
            assert refreshed is not None
            assert refreshed.quantity == 2
            assert len(OrderRepository().list_by_user_id(customer_id)) == 0
            assert len(CartRepository().list_by_user_id(customer_id)) == 1
    except Exception as error:
        pytest.fail(f"Oversell prevention check failed: {error}")


def test_product_service_rejects_negative_stock_quantity(client):
    """Product service must reject negative inventory during product creation."""
    try:
        from exceptions import ValidationException
        from services.product_service import ProductService

        admin_id, _, _ = _seed_user("admin", "Inventory Admin", password="adminPass1")
        seller_id, _, _ = _seed_user("seller", "Inventory Seller2", password="sellerPass2")
        from repositories.category_repository import CategoryRepository

        category = CategoryRepository().create(f"NegQtyCat_{uuid.uuid4().hex[:8]}", None)

        with pytest.raises(ValidationException):
            ProductService().create(
                {
                    "name": "BadQty",
                    "description": "bad",
                    "price": "10.00",
                    "quantity": "-1",
                    "category_id": str(category.id),
                    "seller_id": str(seller_id),
                },
                admin_id,
                "admin",
            )
    except Exception as error:
        pytest.fail(f"Negative quantity validation check failed: {error}")


def test_customer_products_page_shows_stock_and_qty_input(client):
    """Customer products page renders stock label and quantity input for cart actions."""
    try:
        _, customer_email, pwd = _seed_user("customer", "View Stock Customer", password="custPass3")
        _seed_product(name="VisibleStock", quantity=6)
        _login_web(client, customer_email, pwd)

        response = client.get("/customer/products")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "Stock:" in html
        assert "customer-cart__qty-input" in html
        assert "Add to cart" in html
    except Exception as error:
        pytest.fail(f"Products stock display check failed: {error}")


def test_cart_update_quantity_rejects_zero(client):
    """Updating cart line with zero quantity is rejected and line remains unchanged."""
    try:
        customer_id, customer_email, pwd = _seed_user("customer", "Cart Update Customer", password="custPass4")
        product_id = _seed_product(name="UpdateQty", quantity=7)
        _login_web(client, customer_email, pwd)

        client.post("/customer/cart/add", data={"product_id": product_id, "quantity": 2})
        from repositories.cart_repository import CartRepository

        with app.app_context():
            line = CartRepository().list_by_user_id(customer_id)[0]
            line_id = line.id

        response = client.post(
            f"/customer/cart/{line_id}/update",
            data={"quantity": 0},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert urlparse(response.headers.get("Location", "")).path.rstrip("/") == "/customer/cart"

        with app.app_context():
            line = CartRepository().list_by_user_id(customer_id)[0]
            assert line.quantity == 2
    except Exception as error:
        pytest.fail(f"Cart zero-quantity update guard check failed: {error}")
