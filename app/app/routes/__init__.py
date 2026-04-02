from app.routes.auth import auth_bp
from app.routes.commands import commands_bp
from app.routes.dashboard import dashboard_bp
from app.routes.maintenance import maintenance_bp
from app.routes.poc_opcua import poc_opcua_bp
from app.routes.supervision import supervision_bp
from app.routes.users import users_bp


__all__ = [
    "auth_bp",
    "commands_bp",
    "dashboard_bp",
    "maintenance_bp",
    "poc_opcua_bp",
    "supervision_bp",
    "users_bp",
]
