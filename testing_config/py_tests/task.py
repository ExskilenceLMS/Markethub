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


def _seed_product(name="TrackItem", price="22.00", quantity=10):
    from repositories.category_repository import CategoryRepository
    from repositories.product_repository import ProductRepository

    seller_id, _, _ = _seed_user("seller", "Track Seller", password="sellerPass1")
    suffix = uuid.uuid4().hex[:8]
    cat = CategoryRepository().create(f"TrackCat_{suffix}", "Order tracking tests")
    product = ProductRepository().create(
        name,
        "Tracking product",
        Decimal(price),
        quantity,
        cat.id,
        seller_id,
        None,
    )
    return product.id


def _create_order_for_customer(client, qty=2):
    customer_id, customer_email, pwd = _seed_user("customer", "Track Customer", password="custPass1")
    product_id = _seed_product(quantity=9)
    _login_web(client, customer_email, pwd)
    client.post("/customer/cart/add", data={"product_id": product_id, "quantity": qty})
    client.post("/customer/orders/place", follow_redirects=False)
    return customer_id, customer_email, pwd


def test_guest_orders_list_redirects_to_login(client):
    """Guest should not access customer order tracking list."""
    try:
        response = client.get("/customer/orders", follow_redirects=False)
        assert response.status_code == 302
        assert "login" in response.headers.get("Location", "").lower()
    except Exception as error:
        pytest.fail(f"Guest order tracking guard check failed: {error}")


def test_customer_orders_list_shows_tracking_columns(client):
    """Order tracking list should show order id, status, and details link."""
    try:
        _, customer_email, pwd = _create_order_for_customer(client, qty=1)
        _login_web(client, customer_email, pwd)
        response = client.get("/customer/orders")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "My orders" in html
        assert "Status" in html
        assert "Details" in html
        assert "Placed" in html
    except Exception as error:
        pytest.fail(f"Customer tracking list columns check failed: {error}")


def test_customer_orders_status_filter_works(client):
    """Status query filter should keep matching orders in customer list."""
    try:
        _, customer_email, pwd = _create_order_for_customer(client, qty=2)
        _login_web(client, customer_email, pwd)
        response = client.get("/customer/orders?status=Placed")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "Filter by status" in html
        assert "Placed" in html
    except Exception as error:
        pytest.fail(f"Customer status filter check failed: {error}")


def test_customer_order_detail_displays_status_and_total(client):
    """Customer order detail should show total, status, and placed timestamp."""
    try:
        customer_id, customer_email, pwd = _create_order_for_customer(client, qty=3)
        from repositories.order_repository import OrderRepository

        with app.app_context():
            order = OrderRepository().list_by_user_id(customer_id)[0]
            oid = order.id

        _login_web(client, customer_email, pwd)
        response = client.get(f"/customer/orders/{oid}")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert f"Order #{oid}" in html
        assert "Status" in html
        assert "Placed" in html
        assert "Total" in html
    except Exception as error:
        pytest.fail(f"Customer order detail tracking check failed: {error}")


def test_customer_cannot_track_other_customers_order(client):
    """Customer must not access another customer's order detail page."""
    try:
        owner_id, _, _ = _create_order_for_customer(client, qty=1)
        from repositories.order_repository import OrderRepository

        with app.app_context():
            oid = OrderRepository().list_by_user_id(owner_id)[0].id

        _, other_email, other_pwd = _seed_user("customer", "Other Track Customer", password="custPass2")
        _login_web(client, other_email, other_pwd)

        response = client.get(f"/customer/orders/{oid}", follow_redirects=False)
        assert response.status_code == 302
        assert urlparse(response.headers.get("Location", "")).path.rstrip("/") == "/customer/orders"
    except Exception as error:
        pytest.fail(f"Cross-customer tracking access check failed: {error}")


def test_admin_and_staff_order_lists_support_status_filter(client):
    """Admin and staff tracking lists should render status filter controls and rows."""
    try:
        _create_order_for_customer(client, qty=2)

        _, admin_email, admin_pwd = _seed_user("admin", "Track Admin", password="adminPass1")
        _login_web(client, admin_email, admin_pwd)
        admin_response = client.get("/admin/orders?status=Placed")
        assert admin_response.status_code == 200
        admin_html = admin_response.get_data(as_text=True)
        assert "Orders" in admin_html
        assert "Filter by status" in admin_html
        assert "Placed" in admin_html

        _, seller_email, seller_pwd = _seed_user("seller", "Track Staff", password="sellerPass2")
        _login_web(client, seller_email, seller_pwd)
        staff_response = client.get("/staff/orders?status=Placed")
        assert staff_response.status_code == 200
        staff_html = staff_response.get_data(as_text=True)
        assert "Orders" in staff_html
        assert "Filter by status" in staff_html
        assert "Placed" in staff_html
    except Exception as error:
        pytest.fail(f"Admin/staff tracking filter check failed: {error}")
