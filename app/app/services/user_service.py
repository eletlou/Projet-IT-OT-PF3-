from werkzeug.security import generate_password_hash

from app.db import execute_query, fetch_all, fetch_one


def get_user_by_login(login):
    return fetch_one(
        """
        SELECT
            u.id_utilisateur,
            u.login,
            u.mot_de_passe_hash,
            u.nom_complet,
            u.email,
            u.actif,
            r.code_role,
            r.libelle_role
        FROM Utilisateur u
        JOIN Role r ON r.id_role = u.id_role
        WHERE u.login = %s
        """,
        (login,),
    )


def get_roles():
    return fetch_all(
        """
        SELECT id_role, code_role, libelle_role
        FROM Role
        ORDER BY id_role
        """
    )


def get_users_view_model():
    users = fetch_all(
        """
        SELECT
            u.login,
            u.nom_complet,
            u.email,
            u.actif,
            u.created_at,
            r.libelle_role,
            r.code_role
        FROM Utilisateur u
        JOIN Role r ON r.id_role = u.id_role
        ORDER BY u.created_at DESC
        """
    )

    summary = fetch_one(
        """
        SELECT
            COUNT(*) AS total_utilisateurs,
            SUM(CASE WHEN actif = 1 THEN 1 ELSE 0 END) AS utilisateurs_actifs
        FROM Utilisateur
        """
    )

    role_distribution = fetch_all(
        """
        SELECT r.libelle_role, COUNT(*) AS total
        FROM Utilisateur u
        JOIN Role r ON r.id_role = u.id_role
        GROUP BY r.libelle_role
        ORDER BY total DESC, r.libelle_role ASC
        """
    )

    return {
        "users": users,
        "summary": summary,
        "role_distribution": role_distribution,
    }


def create_user(login, full_name, email, password, role_id):
    existing_user = fetch_one(
        """
        SELECT id_utilisateur
        FROM Utilisateur
        WHERE login = %s
        """,
        (login,),
    )

    if existing_user:
        return {
            "success": False,
            "message": "Ce login existe deja.",
        }

    execute_query(
        """
        INSERT INTO Utilisateur (login, mot_de_passe_hash, nom_complet, email, id_role, actif)
        VALUES (%s, %s, %s, %s, %s, 1)
        """,
        (
            login,
            generate_password_hash(password),
            full_name,
            email,
            role_id,
        ),
    )

    return {
        "success": True,
        "message": "Utilisateur cree avec succes.",
    }
