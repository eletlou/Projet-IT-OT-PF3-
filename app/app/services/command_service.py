from datetime import datetime

from flask import current_app

from app.repositories.command_repository import (
    fetch_command_summary,
    fetch_cycle_focus,
    fetch_recent_commands,
    fetch_recent_production_points,
)
from app.services.opcua_test_service import read_configured_opcua_variables


def get_commands_view_model():
    summary = fetch_command_summary()
    commands = fetch_recent_commands()
    production_points = fetch_recent_production_points()
    cycle_focus = fetch_cycle_focus()
    opcua_snapshot = _build_commands_opcua_snapshot(current_app.config)
    opcua_box_counter = opcua_snapshot["opcua_box_counter"]
    opcua_current_order = opcua_snapshot["opcua_current_order"]

    if not opcua_box_counter["read_ok"] and not opcua_box_counter.get("cache_hit"):
        current_app.logger.warning(
            "Lecture OPC UA impossible pour %s: %s",
            opcua_box_counter["display_name"],
            opcua_box_counter["error_message"],
        )

    if opcua_current_order["failed_reads"] and not opcua_current_order["cache_hit_only"]:
        current_app.logger.warning(
            "Lecture OPC UA partielle pour la commande active: %s",
            ", ".join(opcua_current_order["failed_reads"]),
        )

    return {
        "summary": summary,
        "commands": commands,
        "production_points": list(reversed(production_points)),
        "cycle_focus": cycle_focus,
        "opcua_box_counter": opcua_box_counter,
        "opcua_current_order": opcua_current_order,
    }


def _build_commands_opcua_snapshot(config):
    batch_timeout = max(
        float(config.get("OPCUA_COMMAND_COUNTER_TIMEOUT", 3)),
        float(config.get("OPCUA_CURRENT_ORDER_TIMEOUT", 3)),
    )
    batch_attempts = max(
        int(config.get("OPCUA_COMMAND_COUNTER_ATTEMPTS", 1)),
        int(config.get("OPCUA_CURRENT_ORDER_ATTEMPTS", 1)),
    )
    batch_precheck_timeout = max(
        float(config.get("OPCUA_COMMAND_COUNTER_PRECHECK_TIMEOUT", 0)),
        float(config.get("OPCUA_CURRENT_ORDER_PRECHECK_TIMEOUT", 0)),
    )
    variable_definitions = [
        {
            "key": "opcua_box_counter",
            "display_name": config.get("OPCUA_COMMAND_COUNTER_LABEL"),
            "node_id": config.get("OPCUA_COMMAND_COUNTER_NODE_ID"),
        },
        {
            "key": "date_debut",
            "display_name": "Date debut commande",
            "node_id": config.get("OPCUA_CURRENT_ORDER_START_NODE_ID"),
        },
        {
            "key": "date_fin",
            "display_name": "Date fin commande",
            "node_id": config.get("OPCUA_CURRENT_ORDER_END_NODE_ID"),
        },
        {
            "key": "duree_production",
            "display_name": "Temps total production",
            "node_id": config.get("OPCUA_CURRENT_ORDER_DURATION_NODE_ID"),
        },
        {
            "key": "quantite_caisses_demandee",
            "display_name": "Caisses demandees",
            "node_id": config.get("OPCUA_CURRENT_ORDER_REQUESTED_BOXES_NODE_ID"),
        },
        {
            "key": "quantite_caisses_produite",
            "display_name": "Caisses produites",
            "node_id": config.get("OPCUA_CURRENT_ORDER_PRODUCED_BOXES_NODE_ID"),
        },
    ]

    variable_results = read_configured_opcua_variables(
        config,
        variable_definitions,
        timeout=batch_timeout,
        attempts=batch_attempts,
        precheck_timeout=batch_precheck_timeout,
    )
    results_by_key = {
        variable_definition["key"]: variable_result
        for variable_definition, variable_result in zip(variable_definitions, variable_results)
    }

    start_datetime = _parse_opcua_datetime(results_by_key["date_debut"])
    end_datetime = _parse_opcua_datetime(results_by_key["date_fin"])
    duration_raw = _parse_opcua_int(results_by_key["duree_production"])
    requested_boxes = _parse_opcua_int(results_by_key["quantite_caisses_demandee"])
    produced_boxes = _parse_opcua_int(results_by_key["quantite_caisses_produite"])
    failed_reads = [
        f"{variable_result['display_name']}: {variable_result['error_message']}"
        for key, variable_result in results_by_key.items()
        if key != "opcua_box_counter" and not variable_result.get("read_ok")
    ]

    return {
        "opcua_box_counter": results_by_key["opcua_box_counter"],
        "opcua_current_order": {
            "date_debut": start_datetime.date() if start_datetime else None,
            "date_fin": end_datetime.date() if end_datetime else None,
            "heure_debut": start_datetime.strftime("%H:%M:%S") if start_datetime else "-",
            "heure_fin": end_datetime.strftime("%H:%M:%S") if end_datetime else "-",
            "quantite_caisses_demandee": requested_boxes if requested_boxes is not None else "-",
            "quantite_caisses_produite": produced_boxes if produced_boxes is not None else "-",
            "duree_production_min": _convert_duration_to_minutes(duration_raw),
            "duree_production_brute": duration_raw,
            "source_timestamp": _resolve_latest_source_timestamp(results_by_key.values()),
            "status_label": _resolve_current_order_status_label(results_by_key),
            "status_slug": _resolve_current_order_status_slug(results_by_key),
            "failed_reads": failed_reads,
            "cache_hit_only": all(
                variable_result.get("cache_hit")
                for key, variable_result in results_by_key.items()
                if key != "opcua_box_counter"
            ),
        },
    }


def _parse_opcua_datetime(variable_result):
    if not variable_result.get("read_ok"):
        return None

    raw_value = (variable_result.get("value_display") or "").strip()
    if not raw_value or raw_value == "-":
        return None

    normalized_value = raw_value.replace("T", " ")
    if normalized_value.endswith("Z"):
        normalized_value = normalized_value[:-1]

    datetime_formats = (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y",
    )

    for datetime_format in datetime_formats:
        try:
            return datetime.strptime(normalized_value, datetime_format)
        except ValueError:
            continue

    return None


def _parse_opcua_int(variable_result):
    if not variable_result.get("read_ok"):
        return None

    raw_value = (variable_result.get("value_display") or "").strip()
    if not raw_value or raw_value == "-":
        return None

    try:
        return int(float(raw_value))
    except ValueError:
        return None


def _convert_duration_to_minutes(duration_raw):
    if duration_raw is None:
        return "-"
    if duration_raw <= 0:
        return 0

    # Hypothese minimale: les temps IEC/CODESYS remontent generalement en millisecondes.
    return round(duration_raw / 60000, 1)


def _resolve_latest_source_timestamp(variable_results):
    timestamps = [
        variable_result.get("source_timestamp")
        for variable_result in variable_results
        if variable_result.get("source_timestamp")
    ]
    return max(timestamps) if timestamps else None


def _resolve_current_order_status_label(results_by_key):
    relevant_results = [
        variable_result
        for key, variable_result in results_by_key.items()
        if key != "opcua_box_counter"
    ]
    successful_reads = sum(1 for variable_result in relevant_results if variable_result.get("read_ok"))

    if successful_reads == len(relevant_results):
        return "Synchronise"
    if successful_reads:
        return "Partiel"
    return "Indisponible"


def _resolve_current_order_status_slug(results_by_key):
    status_label = _resolve_current_order_status_label(results_by_key)
    return {
        "Synchronise": "good",
        "Partiel": "warning",
        "Indisponible": "error",
    }.get(status_label, "neutral")
