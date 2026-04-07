from flask import Blueprint, request, session

from services.user_service import UserService
from utils.response import success_response
from utils.session_util import set_user_session

# JSON API only. Browser forms use routes/web_routes.py (Jinja templates).
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True)
    user = UserService().register(data)
    return success_response(data=user, message="Registered successfully", status_code=201)


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True)
    user = UserService().login(data)
    set_user_session(session, user)
    return success_response(data=user, message="Logged in successfully")


@auth_bp.post("/logout")
def logout():
    session.clear()
    return success_response(message="Logged out successfully")


@auth_bp.get("/me")
def me():
    uid = UserService.require_authenticated(session)
    user = UserService().get_user_by_id(uid)
    return success_response(data=user)
