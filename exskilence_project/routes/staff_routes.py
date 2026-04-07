from flask import Blueprint, flash, redirect, render_template, session, url_for

from exceptions import AuthorizationException
from services.category_service import CategoryService
from services.store_service import StoreService
from services.user_service import UserService

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
