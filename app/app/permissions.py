from functools import wraps

from flask import flash, redirect, session, url_for


ROLE_PERMISSIONS = {
    "administrateur": {
        "dashboard",
        "commandes",
        "maintenance",
        "maintenance_write",
        "opcua_test",
        "supervision",
        "thresholds_write",
        "users",
    },
    "operateur": {
        "dashboard",
        "commandes",
        "maintenance",
    },
    "responsable": {
        "dashboard",
        "commandes",
        "maintenance",
        "maintenance_write",
        "supervision",
    },
    "integrateur": {
        "dashboard",
        "commandes",
        "maintenance",
        "maintenance_write",
        "opcua_test",
        "supervision",
        "thresholds_write",
    },
}

NAV_ITEMS = [
    {
        "endpoint": "dashboard.index",
        "label": "Vue d'ensemble",
        "prefix": "/dashboard",
        "permission": "dashboard",
    },
    {
        "endpoint": "commands.index",
        "label": "Commandes",
        "prefix": "/commandes",
        "permission": "commandes",
    },
    {
        "endpoint": "maintenance.index",
        "label": "Maintenance",
        "prefix": "/maintenance",
        "permission": "maintenance",
    },
    {
        "endpoint": "supervision.index",
        "label": "Supervision",
        "prefix": "/supervision",
        "permission": "supervision",
        "active_exclude_prefixes": ["/supervision/opcua-test"],
    },
    {
        "endpoint": "supervision.opcua_test",
        "label": "OPCUA",
        "prefix": "/supervision/opcua-test",
        "permission": "opcua_test",
    },
    {
        "endpoint": "users.index",
        "label": "Utilisateurs",
        "prefix": "/utilisateurs",
        "permission": "users",
    },
]


def has_permission(role_code, permission):
    if not role_code:
        return False
    return permission in ROLE_PERMISSIONS.get(role_code, set())


def get_navigation(role_code):
    return [item for item in NAV_ITEMS if has_permission(role_code, item["permission"])]


def is_navigation_item_active(item, path):
    for excluded_prefix in item.get("active_exclude_prefixes", []):
        if path.startswith(excluded_prefix):
            return False

    return path.startswith(item["prefix"])


def login_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return view_function(*args, **kwargs)

    return wrapped_view


def permission_required(permission):
    def decorator(view_function):
        @wraps(view_function)
        def wrapped_view(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("auth.login"))
            if not has_permission(session.get("user_role"), permission):
                flash("Acces non autorise pour cette section.", "error")
                return redirect(url_for("dashboard.index"))
            return view_function(*args, **kwargs)

        return wrapped_view

    return decorator
