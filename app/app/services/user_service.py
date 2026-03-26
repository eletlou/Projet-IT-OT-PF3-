from werkzeug.security import generate_password_hash

from app.repositories.user_repository import (
    fetch_existing_user,
    fetch_role_distribution,
    fetch_roles,
    fetch_user_by_login,
    fetch_user_summary,
    fetch_users,
    insert_user,
)


def get_user_by_login(login):
    return fetch_user_by_login(login)


def get_roles():
    return fetch_roles()


def get_users_view_model():
    users = fetch_users()
    summary = fetch_user_summary()
    role_distribution = fetch_role_distribution()

    return {
        "users": users,
        "summary": summary,
        "role_distribution": role_distribution,
    }


def create_user(login, full_name, email, password, role_id):
    existing_user = fetch_existing_user(login)

    if existing_user:
        return {
            "success": False,
            "message": "Ce login existe deja.",
        }

    insert_user(
        login=login,
        password_hash=generate_password_hash(password),
        full_name=full_name,
        email=email,
        role_id=role_id,
    )

    return {
        "success": True,
        "message": "Utilisateur cree avec succes.",
    }
