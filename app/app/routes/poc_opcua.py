from flask import Blueprint, current_app, jsonify, render_template, request

from app.permissions import login_required, permission_required
from app.services.poc_opcua_service import run_poc_opcua_test


poc_opcua_bp = Blueprint("poc_opcua", __name__)


@poc_opcua_bp.route("/poc-opcua")
@login_required
@permission_required("opcua_test")
def index():
    return render_template(
        "poc_opcua/index.html",
        page_data={
            "opcua_endpoint": (current_app.config.get("OPCUA_TEST_ENDPOINT", "") or "").strip(),
            "opcua_username": (current_app.config.get("OPCUA_TEST_USERNAME", "") or "").strip(),
        },
    )


@poc_opcua_bp.route("/api/poc-opcua/test", methods=["GET", "POST"])
@login_required
@permission_required("opcua_test")
def test_api():
    request_payload = request.get_json(silent=True) or request.form

    return jsonify(
        run_poc_opcua_test(
            current_app.config,
            endpoint=request_payload.get("endpoint"),
            username=request_payload.get("username"),
            password=request_payload.get("password"),
        )
    )
