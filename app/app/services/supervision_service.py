from app.db import execute_query, fetch_all, fetch_one


def get_supervision_view_model():
    line_status = fetch_one(
        """
        SELECT *
        FROM LigneProd
        ORDER BY id_ligne DESC
        LIMIT 1
        """
    )

    autom_history = fetch_all(
        """
        SELECT *
        FROM DataAutom
        ORDER BY date_mesure DESC
        LIMIT 6
        """
    )

    alerts = fetch_all(
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

    thresholds = fetch_all(
        """
        SELECT *
        FROM SeuilAlerte
        ORDER BY indicateur
        """
    )

    defaults = fetch_all(
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

    opcua_variables = fetch_all(
        """
        SELECT *
        FROM VariableOPCUA
        ORDER BY nom_variable
        """
    )

    logs = fetch_all(
        """
        SELECT *
        FROM ConsolLigne
        ORDER BY date_log DESC
        LIMIT 8
        """
    )

    return {
        "line_status": line_status,
        "autom_history": list(reversed(autom_history)),
        "latest_autom": autom_history[0] if autom_history else None,
        "alerts": alerts,
        "thresholds": thresholds,
        "defaults": defaults,
        "opcua_variables": opcua_variables,
        "logs": logs,
    }


def update_threshold(threshold_id, threshold_value):
    execute_query(
        """
        UPDATE SeuilAlerte
        SET valeur_seuil = %s
        WHERE id_seuil_alerte = %s
        """,
        (threshold_value, threshold_id),
    )
