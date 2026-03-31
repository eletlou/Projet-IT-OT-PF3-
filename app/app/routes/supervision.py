from uuid import uuid4

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from app.permissions import has_permission, login_required, permission_required
from app.services.opcua_test_service import (
    clear_connection_settings,
    get_error_detail,
    get_opcua_test_page_model,
    get_user_facing_error,
    read_opcua_test_variables,
    save_connection_settings,
    write_opcua_test_value,
)
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


@supervision_bp.route("/opcua-test")
@login_required
@permission_required("opcua_test")
def opcua_test():
    return render_template(
        "supervision/opcua_test.html",
        page_data=get_opcua_test_page_model(current_app.config, _get_opcua_test_session_key()),
    )


@supervision_bp.route("/opcua-test/connect", methods=["POST"])
@login_required
@permission_required("opcua_test")
def connect_opcua_test_route():
    endpoint = request.form.get("endpoint", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    session_key = _get_opcua_test_session_key()

    try:
        save_connection_settings(current_app.config, session_key, endpoint, username, password)
        read_state = read_opcua_test_variables(current_app.config, session_key)
        page_data = get_opcua_test_page_model(
            current_app.config,
            session_key,
            read_state=read_state,
            form_overrides={"endpoint": endpoint, "username": username},
        )
        flash("Connexion OK", "success")
    except Exception as exc:
        error_detail = get_error_detail(exc)
        current_app.logger.warning("Echec du test OPC UA initial: %s", error_detail)
        page_data = get_opcua_test_page_model(
            current_app.config,
            session_key,
            form_overrides={"endpoint": endpoint, "username": username},
            read_error=get_user_facing_error(exc, "Erreur de connexion"),
            read_error_detail=error_detail,
        )
        flash("Erreur de connexion", "error")

    return render_template("supervision/opcua_test.html", page_data=page_data)


@supervision_bp.route("/opcua-test/refresh", methods=["POST"])
@login_required
@permission_required("opcua_test")
def refresh_opcua_test_route():
    session_key = _get_opcua_test_session_key()

    try:
        read_state = read_opcua_test_variables(current_app.config, session_key)
        page_data = get_opcua_test_page_model(current_app.config, session_key, read_state=read_state)
        flash("Connexion OK", "success")
    except Exception as exc:
        error_detail = get_error_detail(exc)
        current_app.logger.warning("Echec du rafraichissement OPC UA: %s", error_detail)
        page_data = get_opcua_test_page_model(
            current_app.config,
            session_key,
            read_error=get_user_facing_error(exc, "Erreur de connexion"),
            read_error_detail=error_detail,
        )
        flash("Erreur de connexion", "error")

    return render_template("supervision/opcua_test.html", page_data=page_data)


@supervision_bp.route("/opcua-test/write", methods=["POST"])
@login_required
@permission_required("opcua_test")
def write_opcua_test_value_route():
    session_key = _get_opcua_test_session_key()
    node_id = request.form.get("node_id", "").strip()
    value_to_write = request.form.get("value_to_write", "")

    try:
        write_result = write_opcua_test_value(current_app.config, session_key, node_id, value_to_write)
        flash(
            f"Variable {write_result['display_name']} mise a jour avec la valeur {write_result['written_value']}.",
            "success",
        )
    except Exception as exc:
        error_detail = get_error_detail(exc)
        current_app.logger.warning("Echec ecriture OPC UA sur %s: %s", node_id or "node_inconnu", error_detail)
        flash("Erreur d'ecriture", "error")

    try:
        read_state = read_opcua_test_variables(current_app.config, session_key)
        page_data = get_opcua_test_page_model(current_app.config, session_key, read_state=read_state)
    except Exception as exc:
        error_detail = get_error_detail(exc)
        current_app.logger.warning("Impossible de relire les variables apres ecriture OPC UA: %s", error_detail)
        page_data = get_opcua_test_page_model(
            current_app.config,
            session_key,
            read_error=get_user_facing_error(exc, "Erreur de connexion"),
            read_error_detail=error_detail,
        )

    return render_template("supervision/opcua_test.html", page_data=page_data)


@supervision_bp.route("/opcua-test/disconnect", methods=["POST"])
@login_required
@permission_required("opcua_test")
def disconnect_opcua_test_route():
    clear_connection_settings(_get_opcua_test_session_key())
    flash("Connexion OPC UA temporaire effacee pour cette session.", "success")
    return redirect(url_for("supervision.opcua_test"))


def _get_opcua_test_session_key():
    if "opcua_test_session_key" not in session:
        session["opcua_test_session_key"] = uuid4().hex
    return session["opcua_test_session_key"]
