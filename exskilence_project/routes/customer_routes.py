from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from exceptions import AuthorizationException, ValidationException
from services.category_service import CategoryService
from services.product_service import ProductService
from services.user_service import UserService

customer_bp = Blueprint("customer", __name__, url_prefix="/customer")


@customer_bp.before_request
def _require_customer():
    try:
        UserService.require_roles(session, ["customer"])
    except AuthorizationException:
        flash("Please log in as a customer.", "warning")
        return redirect(url_for("web.login"))
    return None


@customer_bp.get("/")
def dashboard():
    uid = int(session["user_id"])
    profile = UserService().get_user_by_id(uid)
    return render_template("customer/dashboard.html", profile=profile)


@customer_bp.get("/categories")
def categories():
    items = CategoryService().list_all_dicts()
    return render_template("customer/categories.html", categories=items)


@customer_bp.get("/products")
def products():
    cid = request.args.get("category_id", type=int)
    try:
        product_rows = ProductService().list_catalog_dicts(category_id=cid)
    except ValidationException as exc:
        flash(getattr(exc, "message", str(exc)), "danger")
        product_rows = ProductService().list_catalog_dicts(category_id=None)
        cid = None
    category_options = CategoryService().list_all_dicts()
    return render_template(
        "customer/products.html",
        products=product_rows,
        categories=category_options,
        selected_category_id=cid,
    )
