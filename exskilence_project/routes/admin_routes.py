from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from exceptions import AuthorizationException, NotFoundException, ValidationException
from services.admin_service import AdminService
from services.category_service import CategoryService
from services.order_service import OrderService
from services.product_service import ProductService
from services.store_service import StoreService
from services.user_service import UserService
from utils.form_errors import validation_exception_to_field_errors

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.before_request
def _require_admin_role():
    try:
        UserService.require_roles(session, ["admin"])
    except AuthorizationException:
        flash("Admin access only. Please log in with an admin account.", "warning")
        return redirect(url_for("web.login"))
    return None


@admin_bp.get("/")
def dashboard():
    stats = AdminService().get_dashboard_stats()
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.get("/users")
def users():
    return render_template("admin/users.html")


@admin_bp.get("/sellers")
def sellers():
    return render_template("admin/sellers.html")


# —— Categories ——


@admin_bp.get("/categories")
def category_list():
    categories = CategoryService().list_all_dicts()
    return render_template("admin/category_list.html", categories=categories)


@admin_bp.route("/categories/new", methods=["GET", "POST"])
def category_new():
    if request.method == "POST":
        try:
            CategoryService().create(request.form.to_dict())
            flash("Category created.", "success")
            return redirect(url_for("admin.category_list"))
        except ValidationException as exc:
            return render_template(
                "admin/category_form.html",
                category=None,
                form_errors=validation_exception_to_field_errors(exc),
            )
    return render_template("admin/category_form.html", category=None, form_errors=None)


@admin_bp.route("/categories/<int:cid>/edit", methods=["GET", "POST"])
def category_edit(cid):
    if request.method == "POST":
        try:
            CategoryService().update(cid, request.form.to_dict())
            flash("Category updated.", "success")
            return redirect(url_for("admin.category_list"))
        except ValidationException as exc:
            try:
                category = CategoryService().get_dict(cid)
            except NotFoundException:
                flash("Category not found.", "danger")
                return redirect(url_for("admin.category_list"))
            return render_template(
                "admin/category_form.html",
                category=category,
                form_errors=validation_exception_to_field_errors(exc),
            )
    try:
        category = CategoryService().get_dict(cid)
    except NotFoundException:
        flash("Category not found.", "danger")
        return redirect(url_for("admin.category_list"))
    return render_template("admin/category_form.html", category=category, form_errors=None)


@admin_bp.post("/categories/<int:cid>/delete")
def category_delete(cid):
    try:
        CategoryService().delete(cid)
        flash("Category deleted.", "success")
    except NotFoundException:
        flash("Category not found.", "danger")
    return redirect(url_for("admin.category_list"))


# —— Stores ——


@admin_bp.get("/stores")
def store_list():
    stores = StoreService().list_all_dicts()
    return render_template("admin/store_list.html", stores=stores)


@admin_bp.route("/stores/new", methods=["GET", "POST"])
def store_new():
    sellers = StoreService().list_sellers_for_dropdown()
    categories = CategoryService().list_all_dicts()
    if request.method == "POST":
        form = {
            "name": request.form.get("name"),
            "seller_id": request.form.get("seller_id"),
            "is_active": request.form.get("is_active"),
            "category_ids": request.form.getlist("category_ids"),
        }
        try:
            StoreService().create(form)
            flash("Store created.", "success")
            return redirect(url_for("admin.store_list"))
        except ValidationException as exc:
            return render_template(
                "admin/store_form.html",
                store=None,
                sellers=sellers,
                categories=categories,
                form_errors=validation_exception_to_field_errors(exc),
            )
    return render_template(
        "admin/store_form.html",
        store=None,
        sellers=sellers,
        categories=categories,
        form_errors=None,
    )


@admin_bp.route("/stores/<int:sid>/edit", methods=["GET", "POST"])
def store_edit(sid):
    sellers = StoreService().list_sellers_for_dropdown()
    categories = CategoryService().list_all_dicts()
    if request.method == "POST":
        form = {
            "name": request.form.get("name"),
            "seller_id": request.form.get("seller_id"),
            "is_active": request.form.get("is_active"),
            "category_ids": request.form.getlist("category_ids"),
        }
        try:
            StoreService().update(sid, form)
            flash("Store updated.", "success")
            return redirect(url_for("admin.store_list"))
        except ValidationException as exc:
            try:
                store = StoreService().get_dict(sid)
            except NotFoundException:
                flash("Store not found.", "danger")
                return redirect(url_for("admin.store_list"))
            return render_template(
                "admin/store_form.html",
                store=store,
                sellers=sellers,
                categories=categories,
                form_errors=validation_exception_to_field_errors(exc),
            )
    try:
        store = StoreService().get_dict(sid)
    except NotFoundException:
        flash("Store not found.", "danger")
        return redirect(url_for("admin.store_list"))
    return render_template(
        "admin/store_form.html",
        store=store,
        sellers=sellers,
        categories=categories,
        form_errors=None,
    )


@admin_bp.post("/stores/<int:sid>/delete")
def store_delete(sid):
    try:
        StoreService().delete(sid)
        flash("Store deleted.", "success")
    except NotFoundException:
        flash("Store not found.", "danger")
    return redirect(url_for("admin.store_list"))


# —— Products ——


@admin_bp.get("/products")
def product_list():
    uid = int(session["user_id"])
    products = ProductService().list_for_role("admin", uid)
    return render_template("admin/product_list.html", products=products)


@admin_bp.route("/products/new", methods=["GET", "POST"])
def product_new():
    sellers = StoreService().list_sellers_for_dropdown()
    categories = CategoryService().list_all_dicts()
    uid = int(session["user_id"])
    if request.method == "POST":
        form = request.form.to_dict()
        try:
            ProductService().create(form, uid, "admin")
            flash("Product created.", "success")
            return redirect(url_for("admin.product_list"))
        except ValidationException as exc:
            return render_template(
                "admin/product_form.html",
                product=None,
                sellers=sellers,
                categories=categories,
                show_seller_select=True,
                form_errors=validation_exception_to_field_errors(exc),
            )
        except AuthorizationException as exc:
            flash(exc.message, "danger")
            return redirect(url_for("admin.product_list"))
    return render_template(
        "admin/product_form.html",
        product=None,
        sellers=sellers,
        categories=categories,
        show_seller_select=True,
        form_errors=None,
    )


@admin_bp.route("/products/<int:pid>/edit", methods=["GET", "POST"])
def product_edit(pid):
    sellers = StoreService().list_sellers_for_dropdown()
    categories = CategoryService().list_all_dicts()
    uid = int(session["user_id"])
    if request.method == "POST":
        form = request.form.to_dict()
        try:
            ProductService().update(pid, form, uid, "admin")
            flash("Product updated.", "success")
            return redirect(url_for("admin.product_list"))
        except ValidationException as exc:
            try:
                product = ProductService().get_dict(pid)
            except NotFoundException:
                flash("Product not found.", "danger")
                return redirect(url_for("admin.product_list"))
            return render_template(
                "admin/product_form.html",
                product=product,
                sellers=sellers,
                categories=categories,
                show_seller_select=True,
                form_errors=validation_exception_to_field_errors(exc),
            )
        except (NotFoundException, AuthorizationException) as exc:
            flash(getattr(exc, "message", str(exc)), "danger")
            return redirect(url_for("admin.product_list"))
    try:
        product = ProductService().get_dict(pid)
    except NotFoundException:
        flash("Product not found.", "danger")
        return redirect(url_for("admin.product_list"))
    return render_template(
        "admin/product_form.html",
        product=product,
        sellers=sellers,
        categories=categories,
        show_seller_select=True,
        form_errors=None,
    )


@admin_bp.post("/products/<int:pid>/delete")
def product_delete(pid):
    uid = int(session["user_id"])
    try:
        ProductService().delete(pid, uid, "admin")
        flash("Product deleted.", "success")
    except NotFoundException:
        flash("Product not found.", "danger")
    except AuthorizationException as exc:
        flash(exc.message, "danger")
    return redirect(url_for("admin.product_list"))


# —— Orders ——


@admin_bp.get("/orders")
def order_list():
    uid = int(session["user_id"])
    orders = OrderService().list_dicts_for_role("admin", uid)
    return render_template("admin/order_list.html", orders=orders)


@admin_bp.route("/orders/<int:oid>", methods=["GET", "POST"])
def order_detail(oid):
    uid = int(session["user_id"])
    if request.method == "POST":
        try:
            OrderService().update_status(oid, request.form.to_dict(), "admin")
            flash("Order status updated.", "success")
        except ValidationException as exc:
            flash(getattr(exc, "message", str(exc)), "danger")
        except NotFoundException:
            flash("Order not found.", "danger")
        return redirect(url_for("admin.order_detail", oid=oid))
    try:
        order, next_statuses = OrderService().get_dict_with_next_statuses(oid, uid, "admin")
    except NotFoundException:
        flash("Order not found.", "danger")
        return redirect(url_for("admin.order_list"))
    return render_template(
        "admin/order_detail.html",
        order=order,
        next_statuses=next_statuses,
    )


# —— Staff / assignments overview ——


@admin_bp.get("/staff/manage")
def staff_management():
    assignments = StoreService().staff_assignments_overview()
    return render_template("admin/staff_management.html", assignments=assignments)
