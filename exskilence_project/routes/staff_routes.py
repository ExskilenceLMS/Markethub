from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from exceptions import AuthorizationException, NotFoundException, ValidationException
from services.category_service import CategoryService
from services.order_service import OrderService
from services.product_service import ProductService
from services.store_service import StoreService
from services.user_service import UserService
from utils.form_errors import validation_exception_to_field_errors

staff_bp = Blueprint("staff", __name__, url_prefix="/staff")


@staff_bp.before_request
def _require_seller_role():
    try:
        UserService.require_roles(session, ["seller"])
    except AuthorizationException:
        flash("Staff access only. Please log in with a seller account.", "warning")
        return redirect(url_for("web.login"))
    return None


@staff_bp.get("/")
def dashboard():
    return render_template("staff/dashboard.html")


@staff_bp.get("/orders")
def order_list():
    uid = int(session["user_id"])
    orders = OrderService().list_dicts_for_role("seller", uid)
    return render_template("staff/order_list.html", orders=orders)


@staff_bp.route("/orders/<int:oid>", methods=["GET", "POST"])
def order_detail(oid):
    uid = int(session["user_id"])
    if request.method == "POST":
        try:
            OrderService().update_status(oid, request.form.to_dict(), "seller")
            flash("Order status updated.", "success")
        except ValidationException as exc:
            flash(getattr(exc, "message", str(exc)), "danger")
        except NotFoundException:
            flash("Order not found.", "danger")
        return redirect(url_for("staff.order_detail", oid=oid))
    try:
        order, next_statuses = OrderService().get_dict_with_next_statuses(oid, uid, "seller")
    except NotFoundException:
        flash("Order not found.", "danger")
        return redirect(url_for("staff.order_list"))
    return render_template(
        "staff/order_detail.html",
        order=order,
        next_statuses=next_statuses,
    )


@staff_bp.get("/categories")
def category_readonly():
    uid = int(session["user_id"])
    categories = CategoryService().list_for_seller(uid)
    return render_template("staff/category_readonly.html", categories=categories)


@staff_bp.get("/stores")
def store_readonly():
    uid = int(session["user_id"])
    stores = StoreService().list_for_seller(uid)
    return render_template("staff/store_readonly.html", stores=stores)


@staff_bp.get("/products")
def product_list():
    uid = int(session["user_id"])
    products = ProductService().list_for_role("seller", uid)
    return render_template("staff/product_list.html", products=products)


@staff_bp.route("/products/new", methods=["GET", "POST"])
def product_new():
    categories = CategoryService().list_for_seller(int(session["user_id"]))
    uid = int(session["user_id"])
    if request.method == "POST":
        form = request.form.to_dict()
        try:
            ProductService().create(form, uid, "seller")
            flash("Product created.", "success")
            return redirect(url_for("staff.product_list"))
        except ValidationException as exc:
            return render_template(
                "staff/product_form.html",
                product=None,
                categories=categories,
                form_errors=validation_exception_to_field_errors(exc),
            )
    return render_template(
        "staff/product_form.html",
        product=None,
        categories=categories,
        form_errors=None,
    )


@staff_bp.route("/products/<int:pid>/edit", methods=["GET", "POST"])
def product_edit(pid):
    categories = CategoryService().list_for_seller(int(session["user_id"]))
    uid = int(session["user_id"])
    if request.method == "POST":
        form = request.form.to_dict()
        try:
            ProductService().update(pid, form, uid, "seller")
            flash("Product updated.", "success")
            return redirect(url_for("staff.product_list"))
        except ValidationException as exc:
            try:
                product = ProductService().get_dict(pid)
            except NotFoundException:
                flash("Product not found.", "danger")
                return redirect(url_for("staff.product_list"))
            return render_template(
                "staff/product_form.html",
                product=product,
                categories=categories,
                form_errors=validation_exception_to_field_errors(exc),
            )
        except (NotFoundException, AuthorizationException) as exc:
            flash(getattr(exc, "message", str(exc)), "danger")
            return redirect(url_for("staff.product_list"))
    try:
        product = ProductService().get_dict(pid)
    except NotFoundException:
        flash("Product not found.", "danger")
        return redirect(url_for("staff.product_list"))
    if product["seller_id"] != uid:
        flash("You can only edit your own products.", "danger")
        return redirect(url_for("staff.product_list"))
    return render_template(
        "staff/product_form.html",
        product=product,
        categories=categories,
        form_errors=None,
    )


@staff_bp.post("/products/<int:pid>/delete")
def product_delete(pid):
    uid = int(session["user_id"])
    try:
        ProductService().delete(pid, uid, "seller")
        flash("Product deleted.", "success")
    except NotFoundException:
        flash("Product not found.", "danger")
    except AuthorizationException as exc:
        flash(exc.message, "danger")
    return redirect(url_for("staff.product_list"))
