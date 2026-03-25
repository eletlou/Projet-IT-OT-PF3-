from app.db import fetch_all, fetch_one


def get_commands_view_model():
    summary = fetch_one(
        """
        SELECT
            COUNT(*) AS total_commandes,
            SUM(CASE WHEN statut = 'terminee' THEN 1 ELSE 0 END) AS commandes_terminees,
            SUM(CASE WHEN statut = 'en_cours' THEN 1 ELSE 0 END) AS commandes_en_cours,
            ROUND(AVG(energie_kwh), 2) AS energie_moyenne
        FROM Commande
        """
    )

    commands = fetch_all(
        """
        SELECT *
        FROM vue_generale_commandes
        ORDER BY date_debut DESC
        """
    )

    production_points = fetch_all(
        """
        SELECT
            DATE_FORMAT(date_mesure, '%H:%i') AS heure,
            cadence_caisses_h,
            caisses_produites
        FROM DataProd
        ORDER BY date_mesure DESC
        LIMIT 6
        """
    )

    cycle_focus = fetch_all(
        """
        SELECT
            c.reference_commande,
            ROUND(AVG(tc.duree_cycle_sec), 2) AS temps_cycle_moyen_sec,
            MAX(tc.duree_cycle_sec) AS temps_cycle_max_sec
        FROM TempsCycle tc
        JOIN Commande c ON c.id_commande = tc.id_commande
        GROUP BY c.reference_commande
        ORDER BY MAX(tc.date_mesure) DESC
        LIMIT 5
        """
    )

    return {
        "summary": summary,
        "commands": commands,
        "production_points": list(reversed(production_points)),
        "cycle_focus": cycle_focus,
    }
