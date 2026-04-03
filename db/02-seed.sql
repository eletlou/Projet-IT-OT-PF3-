INSERT INTO Role (id_role, code_role, libelle_role, description_role)
VALUES
    (1, 'administrateur', 'Administrateur', 'Gere les utilisateurs et l acces global a l application.'),
    (2, 'operateur', 'Operateur', 'Consulte les commandes et les alertes utiles a la production.'),
    (3, 'responsable', 'Responsable', 'Suit la production et planifie la maintenance preventive.'),
    (4, 'integrateur', 'Integrateur', 'Supervise la maintenance detaillee et les seuils techniques.');

INSERT INTO Utilisateur (login, mot_de_passe_hash, nom_complet, email, id_role, actif)
VALUES
    (
        'admin',
        'scrypt:32768:8:1$XZfwI7rSOYQm3Xmm$95987ac35e2c27ce28052dd86a8670ac907f425482881983502eeed7909ff0e91430111ffba3e0012bb2fcd194ea2fd7ef3de9c6cca8f83dbea355922fde40df',
        'Claire Martin',
        'admin@viviers.local',
        1,
        1
    ),
    (
        'operateur',
        'scrypt:32768:8:1$X6YkT009yLwxmh1Q$d788a881c43e9b0ea7f7aca639c2a9937ed9a4da512e0c9b4f43d6d101be95c99f93922f792a6a020fff47956ee47f4dd1d6f1d336cadacb00fb1176eeb53049',
        'Lucas Robin',
        'operateur@viviers.local',
        2,
        1
    ),
    (
        'responsable',
        'scrypt:32768:8:1$sSSpBlM83so0Hcpi$63d60cdd666a71cbd965a930430fe635a39f15f618268d81b01191e18aa2b5a24980855dc21c937bcbb1306645fed2c04d013e9063a721b438d5ff26cf22f1b2',
        'Mathilde Breton',
        'responsable@viviers.local',
        3,
        1
    ),
    (
        'integrateur',
        'scrypt:32768:8:1$cALm6NsB7eOmfgJx$647064729557f2207d5a9ab0392defb6953bca45b6759e7e5c0ecf3a6c34ee43c6ab8e52a7e2a02609b62ad7c2cd525be1686ec5f639d37f1081210b7c51e34e',
        'Pierre Garnier',
        'integrateur@uimm.local',
        4,
        1
    );

INSERT INTO Recette (id_recette, code_recette, libelle_recette, nb_sacs_huitres, nb_sacs_st_jacques, nb_caisses_palette, description_recette)
VALUES
    (1, 'REC-H', '2 sacs Huitres', 2, 0, 5, 'Conditionnement 100 pourcent huitres'),
    (2, 'REC-STJ', '2 sacs Saint Jacques', 0, 2, 5, 'Conditionnement 100 pourcent saint jacques'),
    (3, 'REC-MIX', '1 sac Huitre + 1 sac Saint Jacques', 1, 1, 5, 'Conditionnement mixte');

-- Les donnees ci-dessous sont volontairement laissees vides au demarrage.
-- Elles doivent desormais venir du terrain, de synchronisations applicatives,
-- ou d'import SQL explicite, mais plus d'un seed de demonstration.

INSERT INTO SeuilAlerte (id_seuil_alerte, indicateur, valeur_seuil, unite, niveau)
VALUES
    (1, 'charge_cpu', 75.00, '%', 'moyen'),
    (2, 'ram_utilisee', 80.00, '%', 'moyen'),
    (3, 'temperature_cpu', 65.00, 'C', 'critique');

-- Les alertes, defauts, historiques et interventions ne sont plus seeded
-- pour eviter toute confusion avec des donnees reelles de production.
