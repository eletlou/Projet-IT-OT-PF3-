from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.permissions import has_permission, login_required, permission_required
from app.services.maintenance_service import create_intervention, get_maintenance_view_model


maintenance_bp = Blueprint("maintenance", __name__, url_prefix="/maintenance")


@maintenance_bp.route("/", methods=["GET", "POST"])
@login_required
@permission_required("maintenance")
def index():
    if request.method == "POST":
        if not has_permission(session.get("user_role"), "maintenance_write"):
            flash("Ton profil ne peut pas planifier une intervention.", "error")
            return redirect(url_for("maintenance.index"))

        plan_id = request.form.get("plan_id")
        intervention_type = request.form.get("type_intervention", "").strip()
        date_planifiee = request.form.get("date_planifiee", "").strip()
        commentaire = request.form.get("commentaire", "").strip()

        if not plan_id or not intervention_type or not date_planifiee:
            flash("Merci de remplir le plan, le type et la date.", "error")
            return redirect(url_for("maintenance.index"))

        create_intervention(
            plan_id=int(plan_id),
            intervention_type=intervention_type,
            date_planifiee=date_planifiee,
            commentaire=commentaire,
        )
        flash("Intervention planifiee avec succes.", "success")
        return redirect(url_for("maintenance.index"))

    return render_template("maintenance/index.html", page_data=get_maintenance_view_model())
