from app.repositories.supervision_repository import (
    fetch_alerts,
    fetch_automation_history,
    fetch_defaults,
    fetch_line_status,
    fetch_logs,
    fetch_opcua_variables,
    fetch_thresholds,
    update_threshold_value,
)


def get_supervision_view_model():
    line_status = fetch_line_status()
    autom_history = fetch_automation_history()
    alerts = fetch_alerts()
    thresholds = fetch_thresholds()
    defaults = fetch_defaults()
    opcua_variables = fetch_opcua_variables()
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
