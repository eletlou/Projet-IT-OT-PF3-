from app.db import execute_query, fetch_all, fetch_one


def fetch_line_status():
    return fetch_one(
        """
        SELECT *
        FROM LigneProd
        ORDER BY id_ligne DESC
        LIMIT 1
        """
    )


def fetch_automation_history():
    return fetch_all(
        """
        SELECT *
        FROM DataAutom
        ORDER BY date_mesure DESC
        LIMIT 6
        """
    )


def fetch_alerts():
    return fetch_all(
        """
        SELECT
            a.id_alerte,
            a.source_alerte,
            a.niveau_alerte,
            a.message_alerte,
            a.valeur_mesuree,
            a.statut_alerte,
            a.date_creation,
            s.indicateur,
            s.valeur_seuil,
            s.unite
        FROM Alerte a
        LEFT JOIN SeuilAlerte s ON s.id_seuil_alerte = a.id_seuil_alerte
        ORDER BY a.date_creation DESC
        """
    )


def fetch_thresholds():
    return fetch_all(
        """
        SELECT *
        FROM SeuilAlerte
        ORDER BY indicateur
        """
    )


def fetch_defaults():
    return fetch_all(
        """
        SELECT
            d.code_defaut,
            d.criticite,
            d.description_defaut,
            d.date_defaut,
            d.acquitte,
            e.nom_equipement
        FROM Defaut d
        LEFT JOIN Equipement e ON e.id_equipement = d.id_equipement
        ORDER BY d.date_defaut DESC
        """
    )


def fetch_opcua_variables():
    return fetch_all(
        """
        SELECT *
        FROM VariableOPCUA
        ORDER BY nom_variable
        """
    )


def fetch_logs():
    return fetch_all(
        """
        SELECT *
        FROM ConsolLigne
        ORDER BY date_log DESC
        LIMIT 8
        """
    )


def update_threshold_value(threshold_id, threshold_value):
    execute_query(
        """
        UPDATE SeuilAlerte
        SET valeur_seuil = %s
        WHERE id_seuil_alerte = %s
        """,
        (threshold_value, threshold_id),
    )

