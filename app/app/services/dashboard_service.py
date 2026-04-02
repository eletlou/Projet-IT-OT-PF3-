from flask import current_app

from app.repositories.dashboard_repository import (
    fetch_alert_summary,
    fetch_dashboard_summary,
    fetch_latest_automation,
    fetch_latest_production,
    fetch_line_status,
    fetch_maintenance_focus,
    fetch_maintenance_summary,
    fetch_recent_alerts,
    fetch_recent_commands,
    fetch_recent_logs,
    fetch_user_summary,
)
from app.services.opcua_test_service import read_configured_opcua_variable


def get_dashboard_view_model():
    summary = fetch_dashboard_summary()
    alert_summary = fetch_alert_summary()
    maintenance_summary = fetch_maintenance_summary()
    users_summary = fetch_user_summary()
    line_status = _build_line_status(fetch_line_status())
    latest_automation = _build_latest_automation(fetch_latest_automation())
    latest_production = _build_latest_production(fetch_latest_production())
    recent_commands = fetch_recent_commands()
    recent_alerts = fetch_recent_alerts()
    maintenance_focus = fetch_maintenance_focus()
    recent_logs = fetch_recent_logs()
    opcua_line_status = read_configured_opcua_variable(
        current_app.config,
        current_app.config.get("OPCUA_DASHBOARD_LINE_STATUS_NODE_ID"),
        current_app.config.get("OPCUA_DASHBOARD_LINE_STATUS_LABEL"),
        timeout=current_app.config.get("OPCUA_DASHBOARD_LINE_STATUS_TIMEOUT"),
        attempts=current_app.config.get("OPCUA_DASHBOARD_LINE_STATUS_ATTEMPTS", 1),
        precheck_timeout=current_app.config.get("OPCUA_DASHBOARD_LINE_STATUS_PRECHECK_TIMEOUT"),
    )

    if opcua_line_status["read_ok"]:
        line_status = _merge_opcua_line_status(line_status, opcua_line_status)
    elif not opcua_line_status.get("cache_hit"):
        current_app.logger.warning(
            "Lecture OPC UA impossible pour le statut ligne %s: %s",
            opcua_line_status["display_name"],
            opcua_line_status["error_message"],
        )

    return {
        "summary": {
            "total_commandes": summary["total_commandes"] or 0,
            "commandes_en_cours": summary["commandes_en_cours"] or 0,
            "commandes_terminees": summary["commandes_terminees"] or 0,
            "alertes_ouvertes": alert_summary["alertes_ouvertes"] or 0,
            "alertes_critiques": alert_summary["alertes_critiques"] or 0,
            "maintenances_a_planifier": maintenance_summary["maintenances_a_planifier"] or 0,
            "utilisateurs_actifs": users_summary["utilisateurs_actifs"] or 0,
        },
        "line_status": line_status,
        "opcua_line_status": opcua_line_status,
        "latest_automation": latest_automation,
        "latest_production": latest_production,
        "recent_commands": recent_commands,
        "recent_alerts": recent_alerts,
        "maintenance_focus": maintenance_focus,
        "recent_logs": recent_logs,
    }


def _build_line_status(line_status):
    line_status = line_status or {}
    return {
        "nom_ligne": line_status.get("nom_ligne") or "Ligne de palettisation PF3",
        "etat_ligne": line_status.get("etat_ligne") or "Indisponible",
        "mode_fonctionnement": line_status.get("mode_fonctionnement") or "non renseigne",
        "disponibilite": line_status.get("disponibilite") or 0,
        "cadence_cible_caisses_h": line_status.get("cadence_cible_caisses_h") or 0,
        "derniere_communication": line_status.get("derniere_communication"),
    }


def _build_latest_automation(latest_automation):
    latest_automation = latest_automation or {}
    return {
        "charge_cpu": latest_automation.get("charge_cpu") or 0,
        "ram_utilisee": latest_automation.get("ram_utilisee") or 0,
    }


def _build_latest_production(latest_production):
    latest_production = latest_production or {}
    return {
        "cadence_caisses_h": latest_production.get("cadence_caisses_h") or 0,
        "caisses_produites": latest_production.get("caisses_produites") or 0,
        "sacs_huitres_consommes": latest_production.get("sacs_huitres_consommes") or 0,
        "sacs_st_jacques_consommes": latest_production.get("sacs_st_jacques_consommes") or 0,
    }


def _merge_opcua_line_status(line_status, opcua_line_status):
    value_display = (opcua_line_status.get("value_display") or "").strip().upper()
    is_line_running = value_display in {"1", "TRUE", "VRAI", "ON", "YES", "OUI"}

    line_status["etat_ligne"] = "En cours production" if is_line_running else "Ligne arretee"
    line_status["derniere_communication"] = (
        opcua_line_status.get("source_timestamp") or line_status.get("derniere_communication")
    )

    return line_status
