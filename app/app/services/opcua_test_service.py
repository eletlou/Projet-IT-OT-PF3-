import os
import re
import time
from contextlib import contextmanager
from datetime import datetime


_CONNECTION_SETTINGS = {}
_CONNECTION_TTL_SECONDS = 8 * 60 * 60
_TRUE_VALUES = {"1", "true", "vrai", "on", "oui", "yes"}
_FALSE_VALUES = {"0", "false", "faux", "off", "non", "no"}


def get_opcua_test_page_model(config, session_key, read_state=None, form_overrides=None, read_error=None):
    connection_state = get_connection_state(config, session_key)
    form_overrides = form_overrides or {}

    node_error = None
    configured_nodes = []

    try:
        configured_nodes = load_opcua_test_nodes(config.get("OPCUA_TEST_NODE_FILE", ""))
    except (FileNotFoundError, ValueError) as exc:
        node_error = str(exc)

    variables = []
    last_read_at = None
    successful_reads = 0
    failed_reads = 0
    writable_nodes = 0

    if read_state:
        variables = read_state.get("variables", [])
        last_read_at = read_state.get("last_read_at")
        successful_reads = sum(1 for item in variables if item.get("read_ok"))
        failed_reads = sum(1 for item in variables if not item.get("read_ok"))
        writable_nodes = sum(1 for item in variables if item.get("write_supported"))

    return {
        "connection": connection_state,
        "form_state": {
            "endpoint": form_overrides.get("endpoint", connection_state["endpoint"]),
            "username": form_overrides.get("username", connection_state["username"]),
        },
        "node_file_path": config.get("OPCUA_TEST_NODE_FILE", ""),
        "node_file_error": node_error,
        "configured_nodes": configured_nodes,
        "variables": variables,
        "summary": {
            "configured_nodes": len(configured_nodes),
            "successful_reads": successful_reads,
            "failed_reads": failed_reads,
            "writable_nodes": writable_nodes,
            "last_read_at": last_read_at,
        },
        "read_error": read_error,
    }


def get_connection_state(config, session_key):
    _cleanup_connection_settings()

    saved_settings = _CONNECTION_SETTINGS.get(session_key, {})
    endpoint = saved_settings.get("endpoint") or config.get("OPCUA_TEST_ENDPOINT", "").strip()
    username = saved_settings.get("username") or config.get("OPCUA_TEST_USERNAME", "").strip()
    password = saved_settings.get("password")

    if not password:
        password = config.get("OPCUA_TEST_PASSWORD", "")

    source_label = "non configure"
    if saved_settings.get("endpoint"):
        source_label = "memorisee pour cette session"
    elif endpoint:
        source_label = "chargee depuis la configuration"

    return {
        "endpoint": endpoint,
        "username": username,
        "has_active_settings": bool(endpoint),
        "has_password": bool(password),
        "source_label": source_label,
    }


def save_connection_settings(config, session_key, endpoint, username, password):
    endpoint = endpoint.strip()
    username = username.strip()

    if not endpoint:
        raise ValueError("Renseigne l'URL OPC UA du WAGO avant de lancer le test.")

    _cleanup_connection_settings()
    previous_settings = _CONNECTION_SETTINGS.get(session_key, {})

    if password:
        password_to_store = password
    elif previous_settings.get("endpoint") == endpoint and previous_settings.get("username") == username:
        password_to_store = previous_settings.get("password", "")
    else:
        password_to_store = config.get("OPCUA_TEST_PASSWORD", "")

    _CONNECTION_SETTINGS[session_key] = {
        "endpoint": endpoint,
        "username": username,
        "password": password_to_store,
        "updated_at": time.time(),
    }


def clear_connection_settings(session_key):
    _CONNECTION_SETTINGS.pop(session_key, None)


def read_opcua_test_variables(config, session_key):
    settings = resolve_connection_settings(config, session_key)
    nodes = load_opcua_test_nodes(config.get("OPCUA_TEST_NODE_FILE", ""))
    timeout = float(config.get("OPCUA_TEST_TIMEOUT", 3.0))
    variables = []

    with opcua_client(settings, timeout) as (client, _ua):
        for node_definition in nodes:
            variables.append(_read_variable(client, node_definition))

    return {
        "variables": variables,
        "last_read_at": datetime.now(),
    }


def write_opcua_test_value(config, session_key, node_id, raw_value):
    settings = resolve_connection_settings(config, session_key)
    timeout = float(config.get("OPCUA_TEST_TIMEOUT", 3.0))

    if not node_id:
        raise ValueError("Le Node ID cible est manquant pour l'ecriture OPC UA.")

    with opcua_client(settings, timeout) as (client, ua):
        node = client.get_node(node_id)
        data_value = node.get_data_value()
        variant = getattr(data_value, "Value", None)
        current_value = getattr(variant, "Value", None)
        variant_type = getattr(variant, "VariantType", None)

        if isinstance(current_value, (list, tuple, dict, set)):
            raise ValueError("La page de test ne gere pas l'ecriture des tableaux OPC UA.")

        parsed_value = _parse_write_value(raw_value, current_value, variant_type)

        if variant_type is not None:
            node.set_value(ua.Variant(parsed_value, variant_type))
        else:
            node.set_value(parsed_value)

    return {
        "node_id": node_id,
        "display_name": node_id.split(".")[-1],
        "written_value": _format_value(parsed_value),
    }


def resolve_connection_settings(config, session_key):
    connection_state = get_connection_state(config, session_key)

    if not connection_state["endpoint"]:
        raise ValueError("Aucune connexion OPC UA n'est configuree pour cette session de test.")

    saved_settings = _CONNECTION_SETTINGS.get(session_key, {})
    password = saved_settings.get("password")
    if not password:
        password = config.get("OPCUA_TEST_PASSWORD", "")

    return {
        "endpoint": connection_state["endpoint"],
        "username": connection_state["username"],
        "password": password,
    }


def load_opcua_test_nodes(node_file_path):
    if not node_file_path:
        raise FileNotFoundError("Le chemin vers la liste des Node IDs OPC UA est vide.")

    if not os.path.exists(node_file_path):
        raise FileNotFoundError(f"Le fichier Node IDs OPC UA est introuvable : {node_file_path}")

    nodes = []

    with open(node_file_path, "r", encoding="utf-8") as node_file:
        for line_number, raw_line in enumerate(node_file, start=1):
            parsed_line = parse_node_definition(raw_line)
            if parsed_line is None:
                continue
            parsed_line["line_number"] = line_number
            nodes.append(parsed_line)

    if not nodes:
        raise ValueError("La liste des Node IDs OPC UA est vide.")

    return nodes


def parse_node_definition(raw_line):
    clean_line = raw_line.strip()
    if not clean_line or clean_line.startswith("#"):
        return None

    parts = clean_line.split("|", 4)
    if len(parts) != 5:
        raise ValueError(f"Format Node ID OPC UA invalide : {clean_line}")

    namespace_match = re.fullmatch(r"NS(\d+)", parts[0].strip(), re.IGNORECASE)
    if not namespace_match:
        raise ValueError(f"Namespace OPC UA invalide : {parts[0]}")

    namespace_index = int(namespace_match.group(1))
    identifier_type = parts[1].strip().lower()
    identifier_prefix = parts[3].strip()
    identifier_value = parts[4].strip()

    if identifier_type == "string":
        node_identifier = identifier_value
        if identifier_prefix and not node_identifier.startswith("|"):
            node_identifier = f"|{identifier_prefix}|{node_identifier}"
        node_id = f"ns={namespace_index};s={node_identifier}"
    elif identifier_type == "numeric":
        node_id = f"ns={namespace_index};i={int(identifier_value)}"
    elif identifier_type == "guid":
        node_id = f"ns={namespace_index};g={identifier_value}"
    elif identifier_type == "bytestring":
        node_id = f"ns={namespace_index};b={identifier_value}"
    else:
        raise ValueError(f"Type d'identifiant OPC UA non gere : {parts[1]}")

    return {
        "display_name": identifier_value.split(".")[-1],
        "node_id": node_id,
        "raw_line": clean_line,
    }


@contextmanager
def opcua_client(settings, timeout):
    try:
        from opcua import Client, ua
    except ImportError as exc:
        raise RuntimeError(
            "La librairie python-opcua n'est pas installee. Reconstruis le conteneur web pour activer cette page de test."
        ) from exc

    client = Client(settings["endpoint"], timeout=timeout)

    if settings.get("username"):
        client.set_user(settings["username"])
    if settings.get("password"):
        client.set_password(settings["password"])

    client.connect()
    try:
        yield client, ua
    finally:
        try:
            client.disconnect()
        except Exception:
            pass


def _cleanup_connection_settings():
    now = time.time()
    expired_keys = [
        session_key
        for session_key, settings in _CONNECTION_SETTINGS.items()
        if now - settings.get("updated_at", 0) > _CONNECTION_TTL_SECONDS
    ]

    for session_key in expired_keys:
        _CONNECTION_SETTINGS.pop(session_key, None)


def _read_variable(client, node_definition):
    try:
        node = client.get_node(node_definition["node_id"])
        data_value = node.get_data_value()
        variant = getattr(data_value, "Value", None)
        current_value = getattr(variant, "Value", None)
        variant_type = getattr(variant, "VariantType", None)
        variant_type_name = getattr(variant_type, "name", None) or type(current_value).__name__
        status_code = getattr(data_value, "StatusCode", None)
        status_label = _get_status_label(status_code)
        is_good_status = _is_good_status(status_code)
        editor_type = _get_editor_type(current_value)

        return {
            "display_name": node_definition["display_name"],
            "node_id": node_definition["node_id"],
            "value_display": _format_value(current_value),
            "write_value": _format_input_value(current_value),
            "data_type": variant_type_name,
            "status_label": status_label,
            "status_slug": "good" if is_good_status else _slugify(status_label),
            "read_ok": True,
            "write_supported": editor_type != "unsupported",
            "editor_type": editor_type,
            "source_timestamp": getattr(data_value, "SourceTimestamp", None),
            "server_timestamp": getattr(data_value, "ServerTimestamp", None),
            "error_message": "",
        }
    except Exception as exc:
        return {
            "display_name": node_definition["display_name"],
            "node_id": node_definition["node_id"],
            "value_display": "Lecture impossible",
            "write_value": "",
            "data_type": "Inconnu",
            "status_label": "Erreur",
            "status_slug": "error",
            "read_ok": False,
            "write_supported": False,
            "editor_type": "unsupported",
            "source_timestamp": None,
            "server_timestamp": None,
            "error_message": str(exc),
        }


def _get_status_label(status_code):
    if status_code is None:
        return "Inconnu"
    return getattr(status_code, "name", None) or str(status_code)


def _is_good_status(status_code):
    if status_code is None:
        return False

    try:
        return bool(status_code.is_good())
    except Exception:
        return "good" in _get_status_label(status_code).lower()


def _get_editor_type(value):
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "number"
    if isinstance(value, (list, tuple, dict, set)):
        return "unsupported"
    return "text"


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


def _format_input_value(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    return str(value)


def _parse_write_value(raw_value, current_value, variant_type):
    clean_value = (raw_value or "").strip()
    variant_name = getattr(variant_type, "name", "").lower()

    if variant_name == "boolean" or isinstance(current_value, bool):
        lowered_value = clean_value.lower()
        if lowered_value in _TRUE_VALUES:
            return True
        if lowered_value in _FALSE_VALUES:
            return False
        raise ValueError("Valeur booleenne attendue : true/false, 1/0, oui/non.")

    if variant_name in {"sbyte", "byte", "int16", "int32", "int64", "uint16", "uint32", "uint64"} or (
        isinstance(current_value, int) and not isinstance(current_value, bool)
    ):
        return int(clean_value)

    if variant_name in {"float", "double"} or isinstance(current_value, float):
        return float(clean_value.replace(",", "."))

    if variant_name == "datetime" or isinstance(current_value, datetime):
        return datetime.fromisoformat(clean_value)

    return clean_value


def _slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "info"
