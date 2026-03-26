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


def get_dashboard_view_model():
    summary = fetch_dashboard_summary()
    alert_summary = fetch_alert_summary()
    maintenance_summary = fetch_maintenance_summary()
    users_summary = fetch_user_summary()
    line_status = fetch_line_status()
    latest_automation = fetch_latest_automation()
    latest_production = fetch_latest_production()
    recent_commands = fetch_recent_commands()
    recent_alerts = fetch_recent_alerts()
    maintenance_focus = fetch_maintenance_focus()
    recent_logs = fetch_recent_logs()

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
        "latest_automation": latest_automation,
        "latest_production": latest_production,
        "recent_commands": recent_commands,
        "recent_alerts": recent_alerts,
        "maintenance_focus": maintenance_focus,
        "recent_logs": recent_logs,
    }
