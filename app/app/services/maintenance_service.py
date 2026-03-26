from app.repositories.maintenance_repository import (
    fetch_active_plans,
    fetch_equipments,
    fetch_interventions,
    fetch_maintenance_summary,
    fetch_plan_by_id,
    insert_intervention,
)


def get_maintenance_view_model():
    summary = fetch_maintenance_summary()
    equipments = fetch_equipments()
    plans = fetch_active_plans()
    interventions = fetch_interventions()

    return {
        "summary": {
            "planifiees": summary["planifiees"] or 0,
            "en_retard": summary["en_retard"] or 0,
            "terminees": summary["terminees"] or 0,
            "a_planifier": sum(
                1 for equipment in equipments if equipment["statut_plan"] in {"a_planifier", "proche"}
            ),
        },
        "equipments": equipments,
        "plans": plans,
        "interventions": interventions,
    }


def create_intervention(plan_id, intervention_type, date_planifiee, commentaire):
    plan = fetch_plan_by_id(plan_id)

    insert_intervention(
        plan_id=plan["id_plan_maint"],
        equipment_id=plan["id_equipement"],
        intervention_type=intervention_type,
        date_planifiee=date_planifiee,
        commentaire=commentaire or None,
    )
