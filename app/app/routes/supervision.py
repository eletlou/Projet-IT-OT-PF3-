from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.permissions import has_permission, login_required, permission_required
from app.services.supervision_service import get_supervision_view_model, update_threshold


supervision_bp = Blueprint("supervision", __name__, url_prefix="/supervision")


@supervision_bp.route("/")
@login_required
@permission_required("supervision")
def index():
    return render_template("supervision/index.html", page_data=get_supervision_view_model())


@supervision_bp.route("/seuils/<int:threshold_id>", methods=["POST"])
@login_required
@permission_required("supervision")
def update_threshold_route(threshold_id):
    if not has_permission(session.get("user_role"), "thresholds_write"):
        flash("Ton profil ne peut pas modifier les seuils.", "error")
        return redirect(url_for("supervision.index"))

    threshold_value = request.form.get("valeur_seuil", "0").replace(",", ".").strip()

    try:
        update_threshold(threshold_id, float(threshold_value))
        flash("Seuil mis a jour.", "success")
    except ValueError:
        flash("Valeur de seuil invalide.", "error")

    return redirect(url_for("supervision.index"))
