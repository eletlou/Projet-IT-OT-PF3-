import logging
from datetime import date, datetime

from flask import Flask, redirect, request, session, url_for

from app.config import Config
from app.permissions import get_navigation, has_permission, is_navigation_item_active
from app.routes import auth_bp, commands_bp, dashboard_bp, maintenance_bp, poc_opcua_bp, supervision_bp, users_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    _configure_logging()

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(commands_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(poc_opcua_bp)
    app.register_blueprint(supervision_bp)
    app.register_blueprint(users_bp)

    @app.context_processor
    def inject_layout_context():
        user_role = session.get("user_role")
        return {
            "navigation_items": get_navigation(user_role),
            "can": lambda permission: has_permission(user_role, permission),
            "is_nav_active": lambda item: is_navigation_item_active(item, request.path),
        }

    @app.before_request
    def protect_application_routes():
        endpoint = request.endpoint

        if not endpoint:
            return None

        if endpoint == "static" or endpoint.startswith("static"):
            return None

        if endpoint.startswith("auth."):
            return None

        if "user_id" not in session:
            return redirect(url_for("auth.login"))

    @app.template_filter("datetimefr")
    def datetimefr(value):
        if not value:
            return "-"
        if isinstance(value, datetime):
            return value.strftime("%d/%m/%Y %H:%M")
        return str(value)

    @app.template_filter("datefr")
    def datefr(value):
        if not value:
            return "-"
        if isinstance(value, (datetime, date)):
            return value.strftime("%d/%m/%Y")
        return str(value)

    app.logger.info("Application Flask initialisee pour la supervision Les Viviers")
    return app


def _configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
