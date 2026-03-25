from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from app.services.user_service import get_user_by_login


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        login_value = request.form.get("login", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_login(login_value)

        if user and user["actif"] and check_password_hash(user["mot_de_passe_hash"], password):
            session.clear()
            session["user_id"] = user["id_utilisateur"]
            session["user_login"] = user["login"]
            session["user_name"] = user["nom_complet"]
            session["user_role"] = user["code_role"]
            session["user_role_label"] = user["libelle_role"]

            current_app.logger.info("Connexion reussie pour %s", user["login"])
            return redirect(url_for("dashboard.index"))

        current_app.logger.warning("Echec de connexion pour %s", login_value or "login_vide")
        flash("Identifiants invalides ou utilisateur inactif.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    user_login = session.get("user_login", "inconnu")
    session.clear()
    current_app.logger.info("Deconnexion utilisateur %s", user_login)
    return redirect(url_for("auth.login"))
