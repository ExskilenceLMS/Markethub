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


def _seed_product(name="FlowItem", price="25.00", quantity=12):
    from repositories.category_repository import CategoryRepository
    from repositories.product_repository import ProductRepository

    seller_id, _, _ = _seed_user("seller", "Flow Seller", password="sellerPass1")
    suffix = uuid.uuid4().hex[:8]
    cat = CategoryRepository().create(f"FlowCat_{suffix}", "Order UI workflow")
    product = ProductRepository().create(
        name,
        "Order flow product",
        Decimal(price),
        quantity,
        cat.id,
        seller_id,
        None,
    )
    return product.id


def _create_order(client, qty=2):
    customer_id, customer_email, customer_pwd = _seed_user("customer", "Flow Customer", password="custPass1")
    product_id = _seed_product(quantity=10)
    _login_web(client, customer_email, customer_pwd)
    client.post("/customer/cart/add", data={"product_id": product_id, "quantity": qty})
    client.post("/customer/orders/place", follow_redirects=False)

    from repositories.order_repository import OrderRepository

    with app.app_context():
        order = OrderRepository().list_by_user_id(customer_id)[0]
    return customer_id, customer_email, customer_pwd, order.id


def test_guest_cannot_open_admin_order_detail(client):
    """Guests should be redirected from admin order workflow pages."""
    try:
        response = client.get("/admin/orders/1", follow_redirects=False)
        assert response.status_code == 302
        assert "login" in response.headers.get("Location", "").lower()
    except Exception as error:
        pytest.fail(f"Guest admin-order access guard check failed: {error}")


def test_admin_order_detail_shows_status_control_ui(client):
    """Admin detail page should render status select and save button for workflow control."""
    try:
        _, _, _, oid = _create_order(client)
        _, admin_email, admin_pwd = _seed_user("admin", "Flow Admin", password="adminPass1")
        _login_web(client, admin_email, admin_pwd)

        response = client.get(f"/admin/orders/{oid}")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "Update status" in html
        assert 'select id="status" name="status"' in html
        assert "Save" in html
    except Exception as error:
        pytest.fail(f"Admin order-detail status UI check failed: {error}")


def test_admin_can_transition_order_placed_to_shipped(client):
    """Admin can execute valid status transition Placed -> Shipped."""
    try:
        _, _, _, oid = _create_order(client)
        _, admin_email, admin_pwd = _seed_user("admin", "Flow Admin2", password="adminPass2")
        _login_web(client, admin_email, admin_pwd)

        response = client.post(f"/admin/orders/{oid}", data={"status": "Shipped"}, follow_redirects=False)
        assert response.status_code == 302
        assert urlparse(response.headers.get("Location", "")).path.rstrip("/") == f"/admin/orders/{oid}"

        from repositories.order_repository import OrderRepository

        with app.app_context():
            refreshed = OrderRepository().get_by_id(oid)
            assert refreshed is not None
            assert refreshed.status == "Shipped"
    except Exception as error:
        pytest.fail(f"Admin valid status transition check failed: {error}")


def test_staff_invalid_transition_is_blocked(client):
    """Staff cannot perform invalid transition Placed -> Delivered directly."""
    try:
        _, _, _, oid = _create_order(client)
        _, staff_email, staff_pwd = _seed_user("seller", "Flow Staff", password="staffPass1")
        _login_web(client, staff_email, staff_pwd)

        response = client.post(f"/staff/orders/{oid}", data={"status": "Delivered"}, follow_redirects=False)
        assert response.status_code == 302
        assert urlparse(response.headers.get("Location", "")).path.rstrip("/") == f"/staff/orders/{oid}"

        from repositories.order_repository import OrderRepository

        with app.app_context():
            refreshed = OrderRepository().get_by_id(oid)
            assert refreshed is not None
            assert refreshed.status == "Placed"
    except Exception as error:
        pytest.fail(f"Staff invalid transition block check failed: {error}")


def test_customer_cannot_post_status_update_to_order_routes(client):
    """Customer role cannot post order status updates on staff/admin workflow routes."""
    try:
        _, customer_email, customer_pwd, oid = _create_order(client)
        _login_web(client, customer_email, customer_pwd)

        admin_post = client.post(f"/admin/orders/{oid}", data={"status": "Shipped"}, follow_redirects=False)
        staff_post = client.post(f"/staff/orders/{oid}", data={"status": "Shipped"}, follow_redirects=False)

        assert admin_post.status_code == 302
        assert staff_post.status_code == 302
        assert "login" in admin_post.headers.get("Location", "").lower()
        assert "login" in staff_post.headers.get("Location", "").lower()
    except Exception as error:
        pytest.fail(f"Customer status-update access control check failed: {error}")


def test_status_filter_controls_exist_on_admin_and_staff_lists(client):
    """Order list UIs for admin and staff include status filter controls."""
    try:
        _create_order(client)

        _, admin_email, admin_pwd = _seed_user("admin", "Flow Admin3", password="adminPass3")
        _login_web(client, admin_email, admin_pwd)
        admin_page = client.get("/admin/orders?status=Placed")
        assert admin_page.status_code == 200
        admin_html = admin_page.get_data(as_text=True)
        assert "Filter by status" in admin_html
        assert "customer-filter-form" in admin_html

        _, staff_email, staff_pwd = _seed_user("seller", "Flow Staff2", password="staffPass2")
        _login_web(client, staff_email, staff_pwd)
        staff_page = client.get("/staff/orders?status=Placed")
        assert staff_page.status_code == 200
        staff_html = staff_page.get_data(as_text=True)
        assert "Filter by status" in staff_html
        assert "customer-filter-form" in staff_html
    except Exception as error:
        pytest.fail(f"Order list filter-control UI check failed: {error}")
