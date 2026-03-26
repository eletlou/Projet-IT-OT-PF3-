from app.repositories.command_repository import (
    fetch_command_summary,
    fetch_cycle_focus,
    fetch_recent_commands,
    fetch_recent_production_points,
)


def get_commands_view_model():
    summary = fetch_command_summary()
    commands = fetch_recent_commands()
    production_points = fetch_recent_production_points()
    cycle_focus = fetch_cycle_focus()

    return {
        "summary": summary,
        "commands": commands,
        "production_points": list(reversed(production_points)),
        "cycle_focus": cycle_focus,
    }
