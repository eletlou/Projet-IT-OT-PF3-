import time
from datetime import datetime

from app.services.opcua_test_service import (
    get_error_detail,
    load_opcua_test_nodes,
    opcua_client,
    resolve_default_connection_settings,
)


POC_OPCUA_MAX_VARIABLES = 4
POC_OPCUA_PREFERRED_VARIABLES = (
    "IHM_NB_Caisse",
    "iCaisseDemande",
    "iCaisseProduite",
    "xHeartbeat",
)


def run_poc_opcua_test(config, endpoint=None, username=None, password=None):
    start_time = time.perf_counter()
    default_endpoint = (config.get("OPCUA_TEST_ENDPOINT", "") or "").strip()
    result = {
        "success": False,
        "test_timestamp": datetime.now().isoformat(timespec="seconds"),
        "response_time_ms": 0,
        "opcua_endpoint": default_endpoint,
        "server_to_automate_ok": False,
        "browser_to_server_ok": True,
        "session_open": False,
        "variables_count": 0,
        "variables": [],
        "error": None,
    }

    try:
        settings = _resolve_poc_connection_settings(config, endpoint=endpoint, username=username, password=password)
        selected_nodes = _select_poc_nodes(config)
        timeout = float(config.get("OPCUA_TEST_TIMEOUT", 3.0))
        variables = []
        read_errors = []

        # Le POC ouvre une seule session, lit quelques variables, puis renvoie un resume simple.
        with opcua_client(settings, timeout) as (client, _ua):
            result["session_open"] = True

            for node_definition in selected_nodes:
                try:
                    variables.append(_read_poc_variable(client, node_definition))
                except Exception as exc:
                    read_errors.append(f"{node_definition['display_name']} : {get_error_detail(exc)}")

        result["opcua_endpoint"] = settings["endpoint"]
        result["variables"] = variables
        result["variables_count"] = len(variables)
        result["success"] = bool(variables)
        result["server_to_automate_ok"] = result["success"]

        if not variables:
            result["error"] = "Aucune variable OPC UA n'a pu etre lue."
            if read_errors:
                result["error"] = " | ".join(read_errors[:2])
    except Exception as exc:
        result["error"] = get_error_detail(exc)
    finally:
        result["response_time_ms"] = round((time.perf_counter() - start_time) * 1000)

    return result


def _resolve_poc_connection_settings(config, endpoint=None, username=None, password=None):
    default_settings = resolve_default_connection_settings(config)
    clean_endpoint = ((endpoint if endpoint is not None else default_settings["endpoint"]) or "").strip()
    clean_username = ((username if username is not None else default_settings["username"]) or "").strip()
    resolved_password = default_settings["password"] if password is None else password

    if clean_username == default_settings["username"] and not resolved_password:
        resolved_password = default_settings["password"]

    if not clean_endpoint:
        raise ValueError("Aucun endpoint OPC UA n'est configure.")

    return {
        "endpoint": clean_endpoint,
        "username": clean_username,
        "password": resolved_password if clean_username else "",
    }


def _select_poc_nodes(config):
    configured_nodes = load_opcua_test_nodes(config.get("OPCUA_TEST_NODE_FILE", ""))
    selected_nodes = []
    seen_node_ids = set()

    for variable_name in POC_OPCUA_PREFERRED_VARIABLES:
        matching_node = next(
            (node_definition for node_definition in configured_nodes if node_definition["display_name"] == variable_name),
            None,
        )
        if not matching_node:
            continue

        selected_nodes.append(matching_node)
        seen_node_ids.add(matching_node["node_id"])

    if len(selected_nodes) < POC_OPCUA_MAX_VARIABLES:
        for node_definition in configured_nodes:
            if node_definition["node_id"] in seen_node_ids:
                continue

            selected_nodes.append(node_definition)
            seen_node_ids.add(node_definition["node_id"])

            if len(selected_nodes) >= POC_OPCUA_MAX_VARIABLES:
                break

    return selected_nodes[:POC_OPCUA_MAX_VARIABLES]


def _read_poc_variable(client, node_definition):
    node = client.get_node(node_definition["node_id"])
    data_value = node.get_data_value()
    variant = getattr(data_value, "Value", None)
    current_value = getattr(variant, "Value", None)
    status_code = getattr(data_value, "StatusCode", None)

    return {
        "name": node_definition["display_name"],
        "value": _format_value(current_value),
        "quality": getattr(status_code, "name", None) or str(status_code or "Inconnu"),
    }


def _format_value(value):
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %H:%M:%S")
    if isinstance(value, (list, tuple, set)):
        return ", ".join(_format_value(item) for item in value)
    if isinstance(value, dict):
        return str(value)
    return str(value)
