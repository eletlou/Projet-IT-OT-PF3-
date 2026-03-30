import logging
from datetime import datetime
from uuid import uuid4

from flask import Flask, flash, redirect, render_template, request, session, url_for

from app.config import Config
from app.services.opcua_test_service import (
    clear_connection_settings,
    get_opcua_test_page_model,
    read_opcua_test_variables,
    save_connection_settings,
    write_opcua_test_value,
)


def create_opcua_test_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["SESSION_COOKIE_NAME"] = "opcua_test_session"

    _configure_logging()

    @app.template_filter("datetimefr")
    def datetimefr(value):
        if not value:
            return "-"
        if isinstance(value, datetime):
            return value.strftime("%d/%m/%Y %H:%M")
        return str(value)

    @app.get("/")
    def index():
        return render_template(
            "opcua_test/standalone.html",
            page_data=get_opcua_test_page_model(app.config, _get_opcua_test_session_key()),
        )

    @app.post("/connect")
    def connect():
        endpoint = request.form.get("endpoint", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        session_key = _get_opcua_test_session_key()

        try:
            save_connection_settings(app.config, session_key, endpoint, username, password)
            read_state = read_opcua_test_variables(app.config, session_key)
            page_data = get_opcua_test_page_model(
                app.config,
                session_key,
                read_state=read_state,
                form_overrides={"endpoint": endpoint, "username": username},
            )
            flash("Connexion OPC UA validee. Les variables ont ete lues avec succes.", "success")
        except Exception as exc:
            app.logger.warning("Echec du test OPC UA initial: %s", exc)
            page_data = get_opcua_test_page_model(
                app.config,
                session_key,
                form_overrides={"endpoint": endpoint, "username": username},
                read_error=str(exc),
            )
            flash(f"Connexion OPC UA impossible : {exc}", "error")

        return render_template("opcua_test/standalone.html", page_data=page_data)

    @app.post("/refresh")
    def refresh():
        session_key = _get_opcua_test_session_key()

        try:
            read_state = read_opcua_test_variables(app.config, session_key)
            page_data = get_opcua_test_page_model(app.config, session_key, read_state=read_state)
            flash("Lecture OPC UA actualisee.", "success")
        except Exception as exc:
            app.logger.warning("Echec du rafraichissement OPC UA: %s", exc)
            page_data = get_opcua_test_page_model(app.config, session_key, read_error=str(exc))
            flash(f"Lecture OPC UA impossible : {exc}", "error")

        return render_template("opcua_test/standalone.html", page_data=page_data)

    @app.post("/write")
    def write():
        session_key = _get_opcua_test_session_key()
        node_id = request.form.get("node_id", "").strip()
        value_to_write = request.form.get("value_to_write", "")

        try:
            write_result = write_opcua_test_value(app.config, session_key, node_id, value_to_write)
            flash(
                f"Variable {write_result['display_name']} mise a jour avec la valeur {write_result['written_value']}.",
                "success",
            )
        except Exception as exc:
            app.logger.warning("Echec ecriture OPC UA sur %s: %s", node_id or "node_inconnu", exc)
            flash(f"Ecriture OPC UA impossible : {exc}", "error")

        try:
            read_state = read_opcua_test_variables(app.config, session_key)
            page_data = get_opcua_test_page_model(app.config, session_key, read_state=read_state)
        except Exception as exc:
            app.logger.warning("Impossible de relire les variables apres ecriture OPC UA: %s", exc)
            page_data = get_opcua_test_page_model(app.config, session_key, read_error=str(exc))

        return render_template("opcua_test/standalone.html", page_data=page_data)

    @app.post("/disconnect")
    def disconnect():
        clear_connection_settings(_get_opcua_test_session_key())
        flash("Connexion OPC UA temporaire effacee pour cette session.", "success")
        return redirect(url_for("index"))

    app.logger.info("Application Flask OPC UA de test initialisee")
    return app


def _get_opcua_test_session_key():
    if "opcua_test_session_key" not in session:
        session["opcua_test_session_key"] = uuid4().hex
    return session["opcua_test_session_key"]


def _configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
