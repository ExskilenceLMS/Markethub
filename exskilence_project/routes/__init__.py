from flask import Flask


def register_blueprints(app: Flask) -> None:
    from routes.auth_routes import auth_bp
    from routes.health import health_bp
    from routes.web_routes import web_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
