from app.db import fetch_all, fetch_one


def get_dashboard_view_model():
    summary = fetch_one(
        """
        SELECT
            COUNT(*) AS total_commandes,
            SUM(CASE WHEN statut = 'en_cours' THEN 1 ELSE 0 END) AS commandes_en_cours,
            SUM(CASE WHEN statut = 'terminee' THEN 1 ELSE 0 END) AS commandes_terminees
        FROM Commande
        """
    )

    alert_summary = fetch_one(
        """
        SELECT
            SUM(CASE WHEN statut_alerte = 'ouverte' THEN 1 ELSE 0 END) AS alertes_ouvertes,
            SUM(CASE WHEN niveau_alerte = 'critique' AND statut_alerte <> 'fermee' THEN 1 ELSE 0 END) AS alertes_critiques
        FROM Alerte
        """
    )

    maintenance_summary = fetch_one(
        """
        SELECT COUNT(*) AS maintenances_a_planifier
        FROM PlanMaint p
        JOIN Equipement e ON e.id_equipement = p.id_equipement
        WHERE p.actif = 1 AND e.nb_cycles >= (p.seuil_cycles * 0.9)
        """
    )

    users_summary = fetch_one(
        """
        SELECT COUNT(*) AS utilisateurs_actifs
        FROM Utilisateur
        WHERE actif = 1
        """
    )

    line_status = fetch_one(
        """
        SELECT *
        FROM LigneProd
        ORDER BY id_ligne DESC
        LIMIT 1
        """
    )

    latest_automation = fetch_one(
        """
        SELECT *
        FROM DataAutom
        ORDER BY date_mesure DESC
        LIMIT 1
        """
    )

    latest_production = fetch_one(
        """
        SELECT *
        FROM DataProd
        ORDER BY date_mesure DESC
        LIMIT 1
        """
    )

    recent_commands = fetch_all(
        """
        SELECT *
        FROM vue_generale_commandes
        ORDER BY date_debut DESC
        LIMIT 5
        """
    )

    recent_alerts = fetch_all(
        """
        SELECT niveau_alerte, message_alerte, statut_alerte, date_creation, source_alerte
        FROM Alerte
        ORDER BY date_creation DESC
        LIMIT 5
        """
    )

    maintenance_focus = fetch_all(
        """
        SELECT
            e.nom_equipement,
            p.libelle_plan,
            e.nb_cycles,
            p.seuil_cycles,
            CASE
                WHEN e.nb_cycles >= p.seuil_cycles THEN 'a_planifier'
                WHEN e.nb_cycles >= (p.seuil_cycles * 0.9) THEN 'proche'
                ELSE 'ok'
            END AS statut_plan
        FROM PlanMaint p
        JOIN Equipement e ON e.id_equipement = p.id_equipement
        WHERE p.actif = 1
        ORDER BY e.nb_cycles DESC
        LIMIT 4
        """
    )

    recent_logs = fetch_all(
        """
        SELECT niveau_log, message_log, date_log
        FROM ConsolLigne
        ORDER BY date_log DESC
        LIMIT 5
        """
    )

    return {
        "summary": {
            "total_commandes": summary["total_commandes"] or 0,
            "commandes_en_cours": summary["commandes_en_cours"] or 0,
            "commandes_terminees": summary["commandes_terminees"] or 0,
            "alertes_ouvertes": alert_summary["alertes_ouvertes"] or 0,
            "alertes_critiques": alert_summary["alertes_critiques"] or 0,
            "maintenances_a_planifier": maintenance_summary["maintenances_a_planifier"] or 0,
            "utilisateurs_actifs": users_summary["utilisateurs_actifs"] or 0,
        },
        "line_status": line_status,
        "latest_automation": latest_automation,
        "latest_production": latest_production,
        "recent_commands": recent_commands,
        "recent_alerts": recent_alerts,
        "maintenance_focus": maintenance_focus,
        "recent_logs": recent_logs,
    }
