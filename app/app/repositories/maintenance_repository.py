from app.db import execute_query, fetch_all, fetch_one


def fetch_maintenance_summary():
    return fetch_one(
        """
        SELECT
            SUM(CASE WHEN statut = 'planifiee' THEN 1 ELSE 0 END) AS planifiees,
            SUM(CASE WHEN statut = 'en_retard' THEN 1 ELSE 0 END) AS en_retard,
            SUM(CASE WHEN statut = 'terminee' THEN 1 ELSE 0 END) AS terminees
        FROM InterMaint
        """
    )


def fetch_equipments():
    return fetch_all(
        """
        SELECT
            e.id_equipement,
            e.nom_equipement,
            e.type_equipement,
            e.etat_equipement,
            e.nb_cycles,
            e.date_derniere_maintenance,
            e.criticite,
            MAX(p.seuil_cycles) AS seuil_cycles,
            CASE
                WHEN MAX(p.seuil_cycles) IS NULL THEN 'sans_plan'
                WHEN e.nb_cycles >= MAX(p.seuil_cycles) THEN 'a_planifier'
                WHEN e.nb_cycles >= (MAX(p.seuil_cycles) * 0.9) THEN 'proche'
                ELSE 'ok'
            END AS statut_plan
        FROM Equipement e
        LEFT JOIN PlanMaint p ON p.id_equipement = e.id_equipement AND p.actif = 1
        GROUP BY
            e.id_equipement,
            e.nom_equipement,
            e.type_equipement,
            e.etat_equipement,
            e.nb_cycles,
            e.date_derniere_maintenance,
            e.criticite
        ORDER BY e.criticite DESC, e.nb_cycles DESC
        """
    )


def fetch_active_plans():
    return fetch_all(
        """
        SELECT
            p.id_plan_maint,
            p.libelle_plan,
            p.seuil_cycles,
            p.periodicite_jours,
            e.nom_equipement
        FROM PlanMaint p
        JOIN Equipement e ON e.id_equipement = p.id_equipement
        WHERE p.actif = 1
        ORDER BY e.nom_equipement
        """
    )


def fetch_interventions():
    return fetch_all(
        """
        SELECT
            i.id_inter_maint,
            i.type_intervention,
            i.statut,
            i.date_planifiee,
            i.date_realisation,
            i.commentaire,
            e.nom_equipement,
            p.libelle_plan
        FROM InterMaint i
        JOIN Equipement e ON e.id_equipement = i.id_equipement
        LEFT JOIN PlanMaint p ON p.id_plan_maint = i.id_plan_maint
        ORDER BY i.date_planifiee DESC, i.id_inter_maint DESC
        """
    )


def fetch_plan_by_id(plan_id):
    return fetch_one(
        """
        SELECT id_plan_maint, id_equipement
        FROM PlanMaint
        WHERE id_plan_maint = %s
        """,
        (plan_id,),
    )


def insert_intervention(plan_id, equipment_id, intervention_type, date_planifiee, commentaire):
    execute_query(
        """
        INSERT INTO InterMaint (id_plan_maint, id_equipement, type_intervention, statut, date_planifiee, commentaire)
        VALUES (%s, %s, %s, 'planifiee', %s, %s)
        """,
        (
            plan_id,
            equipment_id,
            intervention_type,
            date_planifiee,
            commentaire,
        ),
    )

