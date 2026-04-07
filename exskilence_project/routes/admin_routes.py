from flask import Blueprint, flash, redirect, render_template, session, url_for

from exceptions import AuthorizationException
from services.admin_service import AdminService
from services.user_service import UserService

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


@admin_bp.get("/categories")
def categories():
    return render_template("admin/categories.html")
