from typing import Any, Mapping


def set_user_session(session: Any, user: Mapping[str, Any]) -> None:
    session.clear()
    session.permanent = True
    session["user_id"] = user["id"]
    session["role"] = user["role"]
    session["name"] = user["name"]
    session["email"] = user["email"]
