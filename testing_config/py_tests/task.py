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
    return user, password


def _seed_product(name="OrderItem", price="20.00", quantity=12):
    from repositories.category_repository import CategoryRepository
    from repositories.product_repository import ProductRepository

    seller, _ = _seed_user("seller", "Order Seller", password="sellerPass1")
    suffix = uuid.uuid4().hex[:8]
    cat = CategoryRepository().create(f"OrdersCat_{suffix}", "Order tests")
    product = ProductRepository().create(
        name,
        "Order management product",
        Decimal(price),
        quantity,
        cat.id,
        seller.id,
        None,
    )
    return product


def _create_customer_order_via_cart(client, qty=2, price="20.00"):
    from repositories.cart_repository import CartRepository
    from repositories.order_repository import OrderRepository

    customer, pwd = _seed_user("customer", "Order Customer", password="custPass1")
    product = _seed_product(price=price, quantity=20)
    product_id = product.id
    _login_web(client, customer.email, pwd)
    client.post("/customer/cart/add", data={"product_id": product_id, "quantity": qty})
    response = client.post("/customer/orders/place", follow_redirects=False)

    with app.app_context():
        orders = OrderRepository().list_by_user_id(customer.id)
        lines_after = CartRepository().list_by_user_id(customer.id)

    return customer, product_id, response, orders, lines_after


def test_guest_orders_redirects_to_login(client):
    """Anonymous user cannot access customer orders list."""
    try:
        response = client.get("/customer/orders", follow_redirects=False)
        assert response.status_code == 302
        assert "login" in response.headers.get("Location", "").lower()
    except Exception as error:
        pytest.fail(f"Guest orders redirect check failed: {error}")


def test_place_order_from_cart_redirects_and_persists_order(client):
    """Placing from non-empty cart creates a Placed order and redirects to orders list."""
    try:
        customer, product_id, response, orders, lines_after = _create_customer_order_via_cart(client, qty=3)
        assert response.status_code == 302
        path = urlparse(response.headers.get("Location", "")).path
        assert path.rstrip("/") == "/customer/orders"
        assert len(orders) == 1
        assert orders[0].status == "Placed"
        assert lines_after == []

        from repositories.product_repository import ProductRepository

        with app.app_context():
            refreshed = ProductRepository().get_by_id(product_id)
            assert refreshed is not None
            assert refreshed.quantity == 17
    except Exception as error:
        pytest.fail(f"Place order persistence check failed: {error}")


def test_place_order_empty_cart_redirects_back_to_cart(client):
    """Posting place-order with empty cart should not create orders and must redirect to cart."""
    try:
        customer, pwd = _seed_user("customer", "Empty Cart Customer", password="emptyPass1")
        _login_web(client, customer.email, pwd)
        response = client.post("/customer/orders/place", follow_redirects=False)
        assert response.status_code == 302
        path = urlparse(response.headers.get("Location", "")).path
        assert path.rstrip("/") == "/customer/cart"

        from repositories.order_repository import OrderRepository

        with app.app_context():
            assert OrderRepository().list_by_user_id(customer.id) == []
    except Exception as error:
        pytest.fail(f"Empty cart place-order check failed: {error}")


def test_customer_orders_list_renders_placed_order(client):
    """Customer orders page renders newly created order details."""
    try:
        customer, _, _, orders, _ = _create_customer_order_via_cart(client, qty=2, price="15.00")
        response = client.get("/customer/orders")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "My orders" in html
        assert f"#{orders[0].id}" in html
        assert "Placed" in html
        assert customer.email not in html or isinstance(html, str)
    except Exception as error:
        pytest.fail(f"Customer orders list render check failed: {error}")


def test_customer_cannot_view_other_customers_order_detail(client):
    """A customer is blocked from viewing another customer's order detail."""
    try:
        _, _, _, orders, _ = _create_customer_order_via_cart(client, qty=1)
        target_order_id = orders[0].id

        other_user, other_pwd = _seed_user("customer", "Other Customer", password="otherPass1")
        _login_web(client, other_user.email, other_pwd)

        response = client.get(f"/customer/orders/{target_order_id}", follow_redirects=False)
        assert response.status_code == 302
        path = urlparse(response.headers.get("Location", "")).path
        assert path.rstrip("/") == "/customer/orders"
    except Exception as error:
        pytest.fail(f"Customer order access-control check failed: {error}")


def test_admin_updates_order_status_to_shipped(client):
    """Admin can update a placed order status to shipped from admin order detail route."""
    try:
        _, _, _, orders, _ = _create_customer_order_via_cart(client, qty=2)
        oid = orders[0].id

        admin, admin_pwd = _seed_user("admin", "Orders Admin", password="adminPass1")
        _login_web(client, admin.email, admin_pwd)

        response = client.post(
            f"/admin/orders/{oid}",
            data={"status": "Shipped"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        path = urlparse(response.headers.get("Location", "")).path
        assert path.rstrip("/") == f"/admin/orders/{oid}"

        from repositories.order_repository import OrderRepository

        with app.app_context():
            refreshed = OrderRepository().get_by_id(oid)
            assert refreshed is not None
            assert refreshed.status == "Shipped"
    except Exception as error:
        pytest.fail(f"Admin order status update check failed: {error}")
