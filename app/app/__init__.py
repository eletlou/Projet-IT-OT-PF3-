import logging
from datetime import date, datetime

from flask import Flask, session

from app.config import Config
from app.permissions import get_navigation, has_permission
from app.routes.auth import auth_bp
from app.routes.commands import commands_bp
from app.routes.dashboard import dashboard_bp
from app.routes.maintenance import maintenance_bp
from app.routes.supervision import supervision_bp
from app.routes.users import users_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    _configure_logging()

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(commands_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(supervision_bp)
    app.register_blueprint(users_bp)

    @app.context_processor
    def inject_layout_context():
        user_role = session.get("user_role")
        return {
            "navigation_items": get_navigation(user_role),
            "can": lambda permission: has_permission(user_role, permission),
        }

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
