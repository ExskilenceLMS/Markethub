import os

from flask import Flask

from config import get_config, resolve_sqlalchemy_database_uri
from middleware import register_middleware
from models import db
from routes import register_blueprints


def create_app() -> Flask:
    app = Flask(__name__)

    config_class = get_config()
    app.config.from_object(config_class)
    app.config["SQLALCHEMY_DATABASE_URI"] = resolve_sqlalchemy_database_uri()

    db.init_app(app)

    register_middleware(app)
    register_blueprints(app)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5001")))
