from app.db import fetch_all, fetch_one


def fetch_dashboard_summary():
    return fetch_one(
        """
        SELECT
            COUNT(*) AS total_commandes,
            SUM(CASE WHEN statut = 'en_cours' THEN 1 ELSE 0 END) AS commandes_en_cours,
            SUM(CASE WHEN statut = 'terminee' THEN 1 ELSE 0 END) AS commandes_terminees
        FROM Commande
        """
    )


def fetch_alert_summary():
    return fetch_one(
        """
        SELECT
            SUM(CASE WHEN statut_alerte = 'ouverte' THEN 1 ELSE 0 END) AS alertes_ouvertes,
            SUM(CASE WHEN niveau_alerte = 'critique' AND statut_alerte <> 'fermee' THEN 1 ELSE 0 END) AS alertes_critiques
        FROM Alerte
        """
    )


def fetch_maintenance_summary():
    return fetch_one(
        """
        SELECT COUNT(*) AS maintenances_a_planifier
        FROM PlanMaint p
        JOIN Equipement e ON e.id_equipement = p.id_equipement
        WHERE p.actif = 1 AND e.nb_cycles >= (p.seuil_cycles * 0.9)
        """
    )


def fetch_user_summary():
    return fetch_one(
        """
        SELECT COUNT(*) AS utilisateurs_actifs
        FROM Utilisateur
        WHERE actif = 1
        """
    )


def fetch_line_status():
    return fetch_one(
        """
        SELECT *
        FROM LigneProd
        ORDER BY id_ligne DESC
        LIMIT 1
        """
    )


def fetch_latest_automation():
    return fetch_one(
        """
        SELECT *
        FROM DataAutom
        ORDER BY date_mesure DESC
        LIMIT 1
        """
    )


def fetch_latest_production():
    return fetch_one(
        """
        SELECT *
        FROM DataProd
        ORDER BY date_mesure DESC
        LIMIT 1
        """
    )


def fetch_recent_commands():
    return fetch_all(
        """
        SELECT *
        FROM vue_generale_commandes
        ORDER BY date_debut DESC
        LIMIT 5
        """
    )


def fetch_recent_alerts():
    return fetch_all(
        """
        SELECT niveau_alerte, message_alerte, statut_alerte, date_creation, source_alerte
        FROM Alerte
        ORDER BY date_creation DESC
        LIMIT 5
        """
    )


def fetch_maintenance_focus():
    return fetch_all(
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


def fetch_recent_logs():
    return fetch_all(
        """
        SELECT niveau_log, message_log, date_log
        FROM ConsolLigne
        ORDER BY date_log DESC
        LIMIT 5
        """
    )

