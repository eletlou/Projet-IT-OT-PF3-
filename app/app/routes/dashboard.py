from flask import Blueprint, render_template

from app.permissions import login_required, permission_required
from app.services.dashboard_service import get_dashboard_view_model


dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
@permission_required("dashboard")
def index():
    return render_template("dashboard/index.html", page_data=get_dashboard_view_model())
