from flask import current_app

from app.repositories.command_repository import (
    fetch_command_summary,
    fetch_cycle_focus,
    fetch_recent_commands,
    fetch_recent_production_points,
)
from app.services.opcua_test_service import read_configured_opcua_variable


def get_commands_view_model():
    summary = fetch_command_summary()
    commands = fetch_recent_commands()
    production_points = fetch_recent_production_points()
    cycle_focus = fetch_cycle_focus()
    opcua_box_counter = read_configured_opcua_variable(
        current_app.config,
        current_app.config.get("OPCUA_COMMAND_COUNTER_NODE_ID"),
        current_app.config.get("OPCUA_COMMAND_COUNTER_LABEL"),
        timeout=current_app.config.get("OPCUA_COMMAND_COUNTER_TIMEOUT"),
        attempts=current_app.config.get("OPCUA_COMMAND_COUNTER_ATTEMPTS", 1),
        precheck_timeout=current_app.config.get("OPCUA_COMMAND_COUNTER_PRECHECK_TIMEOUT"),
    )

    if not opcua_box_counter["read_ok"]:
        current_app.logger.warning(
            "Lecture OPC UA impossible pour %s: %s",
            opcua_box_counter["display_name"],
            opcua_box_counter["error_message"],
        )

    return {
        "summary": summary,
        "commands": commands,
        "production_points": list(reversed(production_points)),
        "cycle_focus": cycle_focus,
        "opcua_box_counter": opcua_box_counter,
    }
