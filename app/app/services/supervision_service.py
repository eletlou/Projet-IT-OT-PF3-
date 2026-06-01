from flask import current_app

from app.repositories.supervision_repository import (
    fetch_alerts,
    fetch_automation_history,
    fetch_defaults,
    fetch_line_status,
    fetch_logs,
    fetch_thresholds,
    update_threshold_value,
)
from app.services.opcua_test_service import (
    load_opcua_test_nodes,
    read_configured_opcua_variables,
)


def get_supervision_view_model():
    line_status = fetch_line_status()
    autom_history = fetch_automation_history()
    alerts = fetch_alerts()
    thresholds = fetch_thresholds()
    defaults = fetch_defaults()
    opcua_variables = _read_live_opcua_variables(current_app.config)
    logs = fetch_logs()

    return {
        "line_status": line_status,
        "autom_history": list(reversed(autom_history)),
        "latest_autom": autom_history[0] if autom_history else None,
        "alerts": alerts,
        "thresholds": thresholds,
        "defaults": defaults,
        "opcua_variables": opcua_variables,
        "logs": logs,
    }


def update_threshold(threshold_id, threshold_value):
    update_threshold_value(threshold_id, threshold_value)


def _read_live_opcua_variables(config):
    try:
        configured_nodes = load_opcua_test_nodes(config.get("OPCUA_TEST_NODE_FILE", ""))
    except (FileNotFoundError, ValueError) as exc:
        current_app.logger.warning("Liste des Node IDs OPC UA indisponible: %s", exc)
        return []

    variable_results = read_configured_opcua_variables(
        config,
        configured_nodes,
        timeout=config.get("OPCUA_LIVE_TIMEOUT", 3),
        attempts=config.get("OPCUA_LIVE_ATTEMPTS", 1),
        precheck_timeout=config.get("OPCUA_LIVE_PRECHECK_TIMEOUT", 0.5),
    )

    return [
        {
            "nom_variable": variable_result["display_name"],
            "valeur_actuelle": variable_result["value_display"],
            "unite": None,
            "qualite": variable_result["status_slug"],
            "qualite_label": variable_result["status_label"],
            "noeud_opcua": variable_result["node_id"],
            "date_mesure": variable_result.get("source_timestamp"),
        }
        for variable_result in variable_results
    ]
