from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.permissions import login_required, permission_required
from app.services.user_service import create_user, get_roles, get_users_view_model


users_bp = Blueprint("users", __name__, url_prefix="/utilisateurs")


@users_bp.route("/", methods=["GET", "POST"])
@login_required
@permission_required("users")
def index():
    if request.method == "POST":
        login_value = request.form.get("login", "").strip()
        full_name = request.form.get("nom_complet", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role_id = request.form.get("role_id", "").strip()

        if not login_value or not full_name or not email or not password or not role_id:
            flash("Tous les champs sont obligatoires pour creer un utilisateur.", "error")
            return redirect(url_for("users.index"))

        result = create_user(
            login=login_value,
            full_name=full_name,
            email=email,
            password=password,
            role_id=int(role_id),
        )

        flash(result["message"], "success" if result["success"] else "error")
        return redirect(url_for("users.index"))

    return render_template(
        "users/index.html",
        page_data=get_users_view_model(),
        roles=get_roles(),
    )
