import os

from flask import Flask
from sqlalchemy.exc import OperationalError

from config import get_config, resolve_sqlalchemy_database_uri
from config.logging_config import get_logger, setup_logging
from middleware import register_middleware
from models import db
from routes import register_blueprints


def create_app() -> Flask:
    setup_logging()
    app = Flask(__name__)

    config_class = get_config()
    app.config.from_object(config_class)
    app.config["SQLALCHEMY_DATABASE_URI"] = resolve_sqlalchemy_database_uri()

    db.init_app(app)

    # Werkzeug reloader: parent has WERKZEUG_SERVER_FD; only skip DB init there (not on plain `import app`).
    _reloader_parent = os.environ.get("WERKZEUG_SERVER_FD") is not None and os.environ.get(
        "WERKZEUG_RUN_MAIN"
    ) != "true"

    with app.app_context():
        if _reloader_parent:
            pass
        elif os.environ.get("SKIP_DB_CREATE_ALL", "").lower() in ("1", "true", "yes"):
            get_logger().warning(
                "SKIP_DB_CREATE_ALL is set; skipping db.create_all()."
            )
        else:
            try:
                db.create_all()
            except OperationalError as exc:
                get_logger().error(
                    "Database unavailable or access denied; tables were not created (%s). "
                    "Set DB_USER/DB_PASSWORD/DB_NAME in .env to match MySQL (see README "
                    "“MySQL 1045 access denied”), or set SKIP_DB_CREATE_ALL=1 to skip schema init.",
                    exc.orig if getattr(exc, "orig", None) else exc,
                )

    register_middleware(app)
    register_blueprints(app)

    flask_env = getattr(app, "env", None) or os.environ.get("FLASK_ENV", "development")
    get_logger().info("Application initialized (env=%s)", flask_env)

    return app


app = create_app()


if __name__ == "__main__":
    _port = int(os.environ.get("PORT", "5001"))
    get_logger().info("Open http://127.0.0.1:%s (default PORT=%s)", _port, _port)
    app.run(host="0.0.0.0", port=_port)
