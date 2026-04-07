from typing import Any, Dict

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from exceptions import AuthorizationException, ValidationException
from services.user_service import UserService
from utils.form_errors import validation_exception_to_field_errors
from utils.session_util import set_user_session

web_bp = Blueprint("web", __name__)


def _redirect_after_login(user: Dict[str, Any]):
    role = user.get("role")
    if role == "admin":
        return redirect(url_for("admin.dashboard"))
    if role == "seller":
        return redirect(url_for("web.staff_dashboard"))
    if role == "customer":
        return redirect(url_for("web.customer_home"))
    return redirect(url_for("web.home"))


@web_bp.route("/")
def home():
    return render_template("home.html")


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = {
            "email": request.form.get("email"),
            "password": request.form.get("password"),
        }
        try:
            user = UserService().login(data)
            set_user_session(session, user)
            flash("Logged in successfully.", "success")
            return _redirect_after_login(user)
        except ValidationException as exc:
            return render_template(
                "auth/login.html",
                form_errors=validation_exception_to_field_errors(exc),
            )
    return render_template("auth/login.html", form_errors=None)


@web_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
            "confirm_password": request.form.get("confirm_password"),
            "role": request.form.get("role") or "customer",
        }
        try:
            user = UserService().register(data)
            set_user_session(session, user)
            flash("Registration successful. You are logged in.", "success")
            return _redirect_after_login(user)
        except ValidationException as exc:
            return render_template(
                "auth/register.html",
                form_errors=validation_exception_to_field_errors(exc),
            )
    return render_template("auth/register.html", form_errors=None)


@web_bp.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("web.home"))


@web_bp.route("/staff")
def staff_dashboard():
    try:
        UserService.require_roles(session, ["seller"])
    except AuthorizationException:
        flash("Staff access only.", "warning")
        return redirect(url_for("web.login"))
    return render_template("staff/dashboard.html")


@web_bp.route("/customer")
def customer_home():
    try:
        UserService.require_roles(session, ["customer"])
    except AuthorizationException:
        flash("Please log in as a customer.", "warning")
        return redirect(url_for("web.login"))
    return render_template("customer/home.html")
