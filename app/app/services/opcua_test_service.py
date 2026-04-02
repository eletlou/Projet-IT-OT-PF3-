import os
import re
import socket
import time
from contextlib import contextmanager
from datetime import datetime
from urllib.parse import urlsplit


_CONNECTION_SETTINGS = {}
_CONNECTION_TTL_SECONDS = 8 * 60 * 60
_CONFIGURED_VARIABLE_CACHE = {}
_TRUE_VALUES = {"1", "true", "vrai", "on", "oui", "yes"}
_FALSE_VALUES = {"0", "false", "faux", "off", "non", "no"}


class OpcuaTestError(RuntimeError):
    def __init__(self, user_message, technical_message=None):
        technical_message = technical_message or user_message
        super().__init__(technical_message)
        self.user_message = user_message
        self.technical_message = technical_message


def get_opcua_test_page_model(
    config,
    session_key,
    read_state=None,
    form_overrides=None,
    read_error=None,
    read_error_detail=None,
):
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
        "read_error_detail": read_error_detail,
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
        "has_credentials": bool(username),
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

    if not username:
        password_to_store = ""
    elif password:
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
        "password": password if connection_state["username"] else "",
    }


def resolve_default_connection_settings(config):
    endpoint = (config.get("OPCUA_TEST_ENDPOINT", "") or "").strip()
    username = (config.get("OPCUA_TEST_USERNAME", "") or "").strip()
    password = config.get("OPCUA_TEST_PASSWORD", "") or ""

    if not endpoint:
        raise ValueError("Aucun endpoint OPC UA par defaut n'est configure pour l'application.")

    return {
        "endpoint": endpoint,
        "username": username,
        "password": password if username else "",
    }


def read_configured_opcua_variable(
    config,
    node_id,
    display_name=None,
    timeout=None,
    attempts=1,
    precheck_timeout=None,
):
    variable_results = read_configured_opcua_variables(
        config,
        [
            {
                "display_name": display_name,
                "node_id": node_id,
            }
        ],
        timeout=timeout,
        attempts=attempts,
        precheck_timeout=precheck_timeout,
    )
    if not variable_results:
        clean_node_id = (node_id or "").strip()
        resolved_display_name = display_name or _derive_display_name(clean_node_id)
        return _build_variable_error_result(
            resolved_display_name,
            clean_node_id,
            "Aucune variable OPC UA n'a ete fournie.",
        )
    return variable_results[0]


def read_configured_opcua_variables(
    config,
    node_definitions,
    timeout=None,
    attempts=1,
    precheck_timeout=None,
):
    resolved_timeout = float(timeout if timeout is not None else config.get("OPCUA_TEST_TIMEOUT", 3.0))
    resolved_attempts = max(1, int(attempts))
    success_cache_ttl = max(0.0, float(config.get("OPCUA_CONFIGURED_VARIABLE_CACHE_TTL", 0)))
    error_cache_ttl = max(0.0, float(config.get("OPCUA_CONFIGURED_VARIABLE_ERROR_CACHE_TTL", 0)))
    variable_results = []
    pending_reads = []

    for index, node_definition in enumerate(node_definitions or []):
        clean_node_id = ((node_definition or {}).get("node_id") or "").strip()
        resolved_display_name = (node_definition or {}).get("display_name") or _derive_display_name(clean_node_id)
        normalized_node_definition = {
            "display_name": resolved_display_name,
            "node_id": clean_node_id,
        }

        if not clean_node_id:
            error_result = _build_variable_error_result(
                resolved_display_name,
                clean_node_id,
                "Node ID OPC UA non configure.",
            )
            error_result["cache_hit"] = False
            variable_results.append(error_result)
            continue

        variable_results.append(None)
        pending_reads.append((index, normalized_node_definition))

    if not pending_reads:
        return variable_results

    try:
        settings = resolve_default_connection_settings(config)
    except Exception as exc:
        for index, node_definition in pending_reads:
            error_result = _build_variable_error_result(
                node_definition["display_name"],
                node_definition["node_id"],
                get_error_detail(exc),
            )
            error_result["cache_hit"] = False
            variable_results[index] = error_result
        return variable_results

    unresolved_reads = []
    for index, node_definition in pending_reads:
        cache_key = _build_configured_variable_cache_key(settings, node_definition["node_id"])
        cached_result = _get_cached_configured_variable_result(cache_key)
        if cached_result is not None:
            cached_result["cache_hit"] = True
            variable_results[index] = cached_result
            continue
        unresolved_reads.append((index, node_definition, cache_key))

    if not unresolved_reads:
        return variable_results

    if precheck_timeout is not None and float(precheck_timeout) > 0:
        try:
            _precheck_opcua_endpoint(settings, float(precheck_timeout))
        except Exception as exc:
            for index, node_definition, cache_key in unresolved_reads:
                error_result = _build_variable_error_result(
                    node_definition["display_name"],
                    node_definition["node_id"],
                    get_error_detail(exc),
                )
                error_result["cache_hit"] = False
                _cache_configured_variable_result(cache_key, error_result, error_cache_ttl)
                variable_results[index] = error_result
            return variable_results

    last_error_detail = ""

    for attempt_index in range(resolved_attempts):
        try:
            with opcua_client(settings, resolved_timeout) as (client, _ua):
                for index, node_definition, cache_key in unresolved_reads:
                    variable_result = _read_variable(client, node_definition)
                    variable_result["cache_hit"] = False
                    _cache_configured_variable_result(
                        cache_key,
                        variable_result,
                        success_cache_ttl if variable_result.get("read_ok") else error_cache_ttl,
                    )
                    variable_results[index] = variable_result
                return variable_results
        except Exception as exc:
            last_error_detail = get_error_detail(exc)

            if attempt_index < resolved_attempts - 1:
                time.sleep(0.4)

    for index, node_definition, cache_key in unresolved_reads:
        error_result = _build_variable_error_result(
            node_definition["display_name"],
            node_definition["node_id"],
            last_error_detail,
        )
        error_result["cache_hit"] = False
        _cache_configured_variable_result(cache_key, error_result, error_cache_ttl)
        variable_results[index] = error_result

    return variable_results


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


def _derive_display_name(node_id):
    if not node_id:
        return "Variable OPC UA"

    node_tail = node_id.split(".")[-1]
    if node_tail and node_tail != node_id:
        return node_tail

    return node_id


def _build_variable_error_result(display_name, node_id, error_message):
    return {
        "display_name": display_name,
        "node_id": node_id,
        "value_display": "Indisponible",
        "write_value": "",
        "data_type": "Inconnu",
        "status_label": "Erreur",
        "status_slug": "error",
        "read_ok": False,
        "write_supported": False,
        "editor_type": "unsupported",
        "source_timestamp": None,
        "server_timestamp": None,
        "error_message": error_message,
    }


def _build_configured_variable_cache_key(settings, node_id):
    return (
        (settings.get("endpoint") or "").strip(),
        (settings.get("username") or "").strip(),
        node_id,
    )


def _get_cached_configured_variable_result(cache_key):
    _cleanup_configured_variable_cache()
    cached_entry = _CONFIGURED_VARIABLE_CACHE.get(cache_key)

    if not cached_entry:
        return None

    return dict(cached_entry["result"])


def _cache_configured_variable_result(cache_key, result, ttl_seconds):
    _cleanup_configured_variable_cache()

    if ttl_seconds <= 0:
        _CONFIGURED_VARIABLE_CACHE.pop(cache_key, None)
        return

    _CONFIGURED_VARIABLE_CACHE[cache_key] = {
        "expires_at": time.time() + ttl_seconds,
        "result": dict(result),
    }


def _cleanup_configured_variable_cache():
    now = time.time()
    expired_keys = [
        cache_key
        for cache_key, cache_entry in _CONFIGURED_VARIABLE_CACHE.items()
        if cache_entry.get("expires_at", 0) <= now
    ]

    for cache_key in expired_keys:
        _CONFIGURED_VARIABLE_CACHE.pop(cache_key, None)


def _precheck_opcua_endpoint(settings, timeout):
    endpoint = (settings.get("endpoint") or "").strip()
    parsed_endpoint = urlsplit(endpoint)
    host = parsed_endpoint.hostname
    port = parsed_endpoint.port

    if not host or port is None:
        raise ValueError("L'endpoint OPC UA configure est invalide ou incomplet.")

    try:
        with socket.create_connection((host, port), timeout=timeout):
            return
    except OSError as exc:
        raise OpcuaTestError(
            "Endpoint OPC UA injoignable",
            _format_connection_error(exc, settings),
        ) from exc


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

    discovered_endpoint = _discover_matching_endpoint(settings["endpoint"], timeout)

    try:
        _validate_discovered_endpoint(settings, discovered_endpoint)
        _connect_client(client, settings, discovered_endpoint)
    except Exception as exc:
        raise OpcuaTestError("Erreur de connexion", _format_connection_error(exc, settings, discovered_endpoint)) from exc
    try:
        yield client, ua
    finally:
        try:
            client.disconnect()
        except Exception:
            pass


def get_user_facing_error(exc, default_message):
    if isinstance(exc, OpcuaTestError):
        return exc.user_message
    return default_message


def get_error_detail(exc):
    if isinstance(exc, OpcuaTestError):
        return exc.technical_message
    return str(exc).strip() or exc.__class__.__name__


def _discover_matching_endpoint(endpoint, timeout):
    try:
        from opcua import Client
    except ImportError:
        return None

    probe_client = Client(endpoint, timeout=timeout)

    try:
        endpoints = probe_client.connect_and_get_server_endpoints()
        return probe_client.find_endpoint(
            endpoints,
            probe_client.security_policy.Mode,
            probe_client.security_policy.URI,
        )
    except Exception:
        return None


def _validate_discovered_endpoint(settings, endpoint_description):
    if endpoint_description is None:
        return

    token_types = _get_user_token_types(endpoint_description)

    if not settings.get("username") and "Anonymous" not in token_types:
        raise RuntimeError("Le serveur OPC UA n'autorise pas l'acces anonyme pour cet endpoint.")

    if settings.get("username") and "UserName" not in token_types:
        raise RuntimeError("Le serveur OPC UA n'autorise pas l'authentification par utilisateur pour cet endpoint.")

    if settings.get("username") and _username_token_requires_encryption(endpoint_description) and not _has_cryptography_support():
        raise RuntimeError(
            "Le mot de passe OPC UA doit etre chiffre pour cet endpoint, mais la dependance Python 'cryptography' n'est pas disponible."
        )


def _connect_client(client, settings, discovered_endpoint):
    client.connect_socket()
    try:
        client.send_hello()
        client.open_secure_channel()
        try:
            client.create_session()

            if discovered_endpoint is not None and getattr(discovered_endpoint, "UserIdentityTokens", None):
                client._policy_ids = discovered_endpoint.UserIdentityTokens

            try:
                client.activate_session(
                    username=settings.get("username") or None,
                    password=settings.get("password") or None,
                    certificate=client.user_certificate,
                )
            except Exception:
                client.close_session()
                raise
        except Exception:
            client.close_secure_channel()
            raise
    except Exception:
        client.disconnect_socket()
        raise


def _format_connection_error(exc, settings, endpoint_description=None):
    message = str(exc).strip() or exc.__class__.__name__
    message_lower = message.lower()
    token_types = _get_user_token_types(endpoint_description)

    if not settings.get("username") and token_types and "Anonymous" not in token_types:
        return (
            f"{message} L'endpoint detecte n'accepte pas l'acces anonyme. "
            "Configure un utilisateur OPC UA sur le WAGO ou active l'acces anonyme cote automate."
        )

    if settings.get("username") and token_types and "UserName" not in token_types:
        return (
            f"{message} L'endpoint detecte n'accepte pas l'authentification Username/Password. "
            "Verifie la configuration OPC UA du WAGO et le type d'identite autorise."
        )

    if settings.get("username") and _username_token_requires_encryption(endpoint_description) and not _has_cryptography_support():
        return (
            f"{message} Le serveur demande un chiffrement du mot de passe OPC UA pour cet endpoint. "
            "Reconstruis l'image web avec la dependance Python 'cryptography'."
        )

    if "badsessionnotactivated" in message_lower or "activatesession has not been called" in message_lower:
        hints = [
            "Le serveur OPC UA a refuse l'activation de la session.",
        ]
        if not settings.get("username"):
            hints.append(
                "L'acces anonyme est probablement desactive sur le WAGO : essaye avec un utilisateur OPC UA configure sur l'automate."
            )
        hints.append(
            "Si le CC100 n'accepte pas l'endpoint non securise, il faut autoriser `Security Policy None` cote automate ou passer a une liaison OPC UA securisee avec certificats."
        )
        return f"{message} {' '.join(hints)}"

    if "connection refused" in message_lower or "[errno 111]" in message_lower:
        return (
            f"{message} Le port OPC UA a refuse la connexion. Verifie que le serveur OPC UA du WAGO est demarre et ecoute bien sur l'adresse cible."
        )

    if "timed out" in message_lower or "timeout" in message_lower:
        return (
            f"{message} Le port OPC UA ne repond pas a temps. Verifie le flux TCP 4840 entre le conteneur Docker, la VM et le reseau industriel."
        )

    return message


def _get_user_token_types(endpoint_description):
    if endpoint_description is None:
        return set()

    token_types = set()
    for token in getattr(endpoint_description, "UserIdentityTokens", []):
        token_type = getattr(getattr(token, "TokenType", None), "name", None)
        if token_type:
            token_types.add(token_type)
    return token_types


def _username_token_requires_encryption(endpoint_description):
    if endpoint_description is None:
        return False

    security_policy_uri = getattr(endpoint_description, "SecurityPolicyUri", "") or ""

    for token in getattr(endpoint_description, "UserIdentityTokens", []):
        token_type = getattr(getattr(token, "TokenType", None), "name", None)
        if token_type != "UserName":
            continue

        token_policy_uri = getattr(token, "SecurityPolicyUri", "") or security_policy_uri
        return bool(token_policy_uri and not token_policy_uri.lower().endswith("#none"))

    return False


def _has_cryptography_support():
    try:
        import cryptography  # noqa: F401
    except ImportError:
        return False
    return True


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
