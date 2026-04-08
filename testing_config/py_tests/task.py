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


def _seed_product(name="WorkflowItem", price="30.00", quantity=8):
    from repositories.category_repository import CategoryRepository
    from repositories.product_repository import ProductRepository

    seller_id, _, _ = _seed_user("seller", "Workflow Seller", password="sellerPass1")
    suffix = uuid.uuid4().hex[:8]
    cat = CategoryRepository().create(f"WorkflowCat_{suffix}", "Workflow tests")
    product = ProductRepository().create(
        name,
        "Order workflow test product",
        Decimal(price),
        quantity,
        cat.id,
        seller_id,
        None,
    )
    return product.id


def test_guest_order_place_redirects_to_login(client):
    """Guest posting place-order is redirected to login."""
    try:
        response = client.post("/customer/orders/place", follow_redirects=False)
        assert response.status_code == 302
        assert "login" in response.headers.get("Location", "").lower()
    except Exception as error:
        pytest.fail(f"Guest order place guard check failed: {error}")


def test_order_workflow_places_order_and_redirects(client):
    """Cart to order workflow redirects to /customer/orders and creates order."""
    try:
        customer_id, customer_email, pwd = _seed_user("customer", "Workflow Customer", password="custPass1")
        product_id = _seed_product(quantity=9)
        _login_web(client, customer_email, pwd)

        client.post("/customer/cart/add", data={"product_id": product_id, "quantity": 3})
        response = client.post("/customer/orders/place", follow_redirects=False)

        assert response.status_code == 302
        assert urlparse(response.headers.get("Location", "")).path.rstrip("/") == "/customer/orders"

        from repositories.order_repository import OrderRepository

        with app.app_context():
            orders = OrderRepository().list_by_user_id(customer_id)
            assert len(orders) == 1
            assert orders[0].status == "Placed"
    except Exception as error:
        pytest.fail(f"Order placement workflow redirect check failed: {error}")


def test_order_workflow_deducts_stock_and_clears_cart(client):
    """Successful workflow deducts stock and clears all cart lines."""
    try:
        customer_id, customer_email, pwd = _seed_user("customer", "Workflow Customer2", password="custPass2")
        product_id = _seed_product(name="WItem2", quantity=7)
        _login_web(client, customer_email, pwd)

        client.post("/customer/cart/add", data={"product_id": product_id, "quantity": 4})
        client.post("/customer/orders/place", follow_redirects=False)

        from repositories.cart_repository import CartRepository
        from repositories.product_repository import ProductRepository

        with app.app_context():
            refreshed = ProductRepository().get_by_id(product_id)
            assert refreshed is not None
            assert refreshed.quantity == 3
            assert CartRepository().list_by_user_id(customer_id) == []
    except Exception as error:
        pytest.fail(f"Workflow stock deduction and cart clear check failed: {error}")


def test_order_workflow_prevents_oversell_and_keeps_cart(client):
    """If requested qty exceeds stock, workflow must not create order and cart remains."""
    try:
        customer_id, customer_email, pwd = _seed_user("customer", "Workflow Customer3", password="custPass3")
        product_id = _seed_product(name="WItem3", quantity=2)
        _login_web(client, customer_email, pwd)

        client.post("/customer/cart/add", data={"product_id": product_id, "quantity": 5})
        response = client.post("/customer/orders/place", follow_redirects=False)

        assert response.status_code == 302
        assert urlparse(response.headers.get("Location", "")).path.rstrip("/") == "/customer/cart"

        from repositories.cart_repository import CartRepository
        from repositories.order_repository import OrderRepository

        with app.app_context():
            assert len(OrderRepository().list_by_user_id(customer_id)) == 0
            assert len(CartRepository().list_by_user_id(customer_id)) == 1
    except Exception as error:
        pytest.fail(f"Workflow oversell prevention check failed: {error}")


def test_order_workflow_blocks_empty_cart(client):
    """Empty cart placement redirects back to cart and creates no order."""
    try:
        customer_id, customer_email, pwd = _seed_user("customer", "Workflow EmptyCart", password="custPass4")
        _login_web(client, customer_email, pwd)
        response = client.post("/customer/orders/place", follow_redirects=False)

        assert response.status_code == 302
        assert urlparse(response.headers.get("Location", "")).path.rstrip("/") == "/customer/cart"

        from repositories.order_repository import OrderRepository

        with app.app_context():
            assert OrderRepository().list_by_user_id(customer_id) == []
    except Exception as error:
        pytest.fail(f"Workflow empty-cart guard check failed: {error}")


def test_customer_orders_list_shows_placed_order_after_workflow(client):
    """After workflow success, /customer/orders renders order id and status."""
    try:
        _, customer_email, pwd = _seed_user("customer", "Workflow OrdersList", password="custPass5")
        product_id = _seed_product(name="WItem4", quantity=6)
        _login_web(client, customer_email, pwd)

        client.post("/customer/cart/add", data={"product_id": product_id, "quantity": 2})
        client.post("/customer/orders/place", follow_redirects=False)
        response = client.get("/customer/orders")

        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "My orders" in html
        assert "Placed" in html
        assert "#" in html
    except Exception as error:
        pytest.fail(f"Orders list post-workflow check failed: {error}")
