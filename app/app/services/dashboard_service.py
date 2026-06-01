from flask import current_app

from app.repositories.dashboard_repository import (
    fetch_alert_summary,
    fetch_dashboard_summary,
    fetch_latest_automation,
    fetch_line_status,
    fetch_maintenance_focus,
    fetch_maintenance_summary,
    fetch_recent_alerts,
    fetch_recent_commands,
    fetch_recent_logs,
    fetch_user_summary,
)
from app.services.opcua_test_service import read_configured_opcua_variables


def get_dashboard_view_model():
    summary = fetch_dashboard_summary()
    alert_summary = fetch_alert_summary()
    maintenance_summary = fetch_maintenance_summary()
    users_summary = fetch_user_summary()
    line_status = _build_line_status(fetch_line_status())
    latest_automation = _build_latest_automation(fetch_latest_automation())
    recent_commands = fetch_recent_commands()
    recent_alerts = fetch_recent_alerts()
    maintenance_focus = fetch_maintenance_focus()
    recent_logs = fetch_recent_logs()
    opcua_snapshot = _read_dashboard_opcua_snapshot(current_app.config)
    opcua_line_status = opcua_snapshot["line_status"]
    latest_production = _build_live_production(opcua_snapshot)

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
        "opcua_production_snapshot": opcua_snapshot,
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


def _build_live_production(opcua_snapshot):
    return {
        "numero_caisse": _read_live_value(opcua_snapshot["current_box"]),
        "caisses_demandees": _read_live_value(opcua_snapshot["requested_boxes"]),
        "caisses_produites": _read_live_value(opcua_snapshot["produced_boxes"]),
        "sacs_huitres_consommes": _read_live_value(opcua_snapshot["oyster_bags"]),
        "sacs_st_jacques_consommes": _read_live_value(opcua_snapshot["scallop_bags"]),
    }


def _read_dashboard_opcua_snapshot(config):
    variable_definitions = [
        {
            "key": "line_status",
            "display_name": config.get("OPCUA_DASHBOARD_LINE_STATUS_LABEL"),
            "node_id": config.get("OPCUA_DASHBOARD_LINE_STATUS_NODE_ID"),
        },
        {
            "key": "current_box",
            "display_name": "Numero caisse courant",
            "node_id": config.get("OPCUA_DASHBOARD_CURRENT_BOX_NODE_ID"),
        },
        {
            "key": "requested_boxes",
            "display_name": "Caisses demandees",
            "node_id": config.get("OPCUA_CURRENT_ORDER_REQUESTED_BOXES_NODE_ID"),
        },
        {
            "key": "produced_boxes",
            "display_name": "Caisses produites",
            "node_id": config.get("OPCUA_CURRENT_ORDER_PRODUCED_BOXES_NODE_ID"),
        },
        {
            "key": "oyster_bags",
            "display_name": "Sacs huitres",
            "node_id": config.get("OPCUA_DASHBOARD_OYSTER_BAGS_NODE_ID"),
        },
        {
            "key": "scallop_bags",
            "display_name": "Sacs saint jacques",
            "node_id": config.get("OPCUA_DASHBOARD_SCALLOP_BAGS_NODE_ID"),
        },
    ]
    variable_results = read_configured_opcua_variables(
        config,
        variable_definitions,
        timeout=max(
            float(config.get("OPCUA_DASHBOARD_LINE_STATUS_TIMEOUT", 3)),
            float(config.get("OPCUA_DASHBOARD_PRODUCTION_TIMEOUT", 3)),
        ),
        attempts=max(
            int(config.get("OPCUA_DASHBOARD_LINE_STATUS_ATTEMPTS", 1)),
            int(config.get("OPCUA_DASHBOARD_PRODUCTION_ATTEMPTS", 1)),
        ),
        precheck_timeout=max(
            float(config.get("OPCUA_DASHBOARD_LINE_STATUS_PRECHECK_TIMEOUT", 0)),
            float(config.get("OPCUA_DASHBOARD_PRODUCTION_PRECHECK_TIMEOUT", 0)),
        ),
    )
    results_by_key = {
        variable_definition["key"]: variable_result
        for variable_definition, variable_result in zip(variable_definitions, variable_results)
    }
    production_results = [
        results_by_key[key]
        for key in ("current_box", "requested_boxes", "produced_boxes", "oyster_bags", "scallop_bags")
    ]
    successful_reads = sum(1 for variable_result in production_results if variable_result.get("read_ok"))

    if successful_reads == len(production_results):
        status_label = "Synchronise"
        status_slug = "good"
    elif successful_reads:
        status_label = "Partiel"
        status_slug = "warning"
    else:
        status_label = "Indisponible"
        status_slug = "error"

    return {
        **results_by_key,
        "status_label": status_label,
        "status_slug": status_slug,
        "source_timestamp": _resolve_latest_source_timestamp(production_results),
    }


def _read_live_value(variable_result):
    if not variable_result.get("read_ok"):
        return "-"
    return variable_result.get("value_display") or "-"


def _resolve_latest_source_timestamp(variable_results):
    timestamps = [
        variable_result.get("source_timestamp")
        for variable_result in variable_results
        if variable_result.get("source_timestamp")
    ]
    return max(timestamps) if timestamps else None


def _merge_opcua_line_status(line_status, opcua_line_status):
    value_display = (opcua_line_status.get("value_display") or "").strip().upper()
    is_line_running = value_display in {"1", "TRUE", "VRAI", "ON", "YES", "OUI"}

    line_status["etat_ligne"] = "En cours production" if is_line_running else "Ligne arretee"
    line_status["derniere_communication"] = (
        opcua_line_status.get("source_timestamp") or line_status.get("derniere_communication")
    )

    return line_status
