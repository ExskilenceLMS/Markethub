from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from exceptions import AuthorizationException, NotFoundException, ValidationException
from services.cart_service import CartService
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


@customer_bp.get("/cart")
def cart():
    uid = int(session["user_id"])
    items, total = CartService().get_cart_summary(uid)
    return render_template(
        "customer/cart.html",
        cart_items=items,
        total_amount=float(total),
    )


@customer_bp.post("/cart/add")
def cart_add():
    uid = int(session["user_id"])
    try:
        CartService().add(uid, request.form.to_dict())
        flash("Added to cart.", "success")
    except ValidationException as exc:
        flash(getattr(exc, "message", str(exc)), "danger")
    cid = request.form.get("redirect_category_id", type=int)
    if cid:
        return redirect(url_for("customer.products", category_id=cid))
    return redirect(url_for("customer.products"))


@customer_bp.post("/cart/<int:line_id>/update")
def cart_update_line(line_id):
    uid = int(session["user_id"])
    try:
        CartService().update_line(uid, line_id, request.form.to_dict())
        flash("Cart updated.", "success")
    except ValidationException as exc:
        flash(getattr(exc, "message", str(exc)), "danger")
    except NotFoundException:
        flash("Cart item not found.", "danger")
    return redirect(url_for("customer.cart"))


@customer_bp.post("/cart/<int:line_id>/remove")
def cart_remove_line(line_id):
    uid = int(session["user_id"])
    try:
        CartService().remove_line(uid, line_id)
        flash("Item removed.", "success")
    except NotFoundException:
        flash("Cart item not found.", "danger")
    return redirect(url_for("customer.cart"))


@customer_bp.post("/cart/clear")
def cart_clear():
    uid = int(session["user_id"])
    CartService().clear(uid)
    flash("Cart cleared.", "success")
    return redirect(url_for("customer.cart"))
