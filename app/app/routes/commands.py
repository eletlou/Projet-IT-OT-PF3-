from flask import Blueprint, render_template

from app.permissions import login_required, permission_required
from app.services.command_service import get_commands_view_model


commands_bp = Blueprint("commands", __name__, url_prefix="/commandes")


@commands_bp.route("/")
@login_required
@permission_required("commandes")
def index():
    return render_template("commands/index.html", page_data=get_commands_view_model())
