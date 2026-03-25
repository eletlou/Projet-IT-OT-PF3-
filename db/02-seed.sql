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

INSERT INTO LigneProd (id_ligne, nom_ligne, etat_ligne, mode_fonctionnement, disponibilite, cadence_cible_caisses_h, derniere_communication)
VALUES
    (1, 'Ligne de palettisation PF3', 'production', 'automatique', 96.40, 120.00, '2026-03-25 10:24:00');

INSERT INTO Equipement (id_equipement, nom_equipement, type_equipement, etat_equipement, nb_cycles, date_derniere_maintenance, criticite)
VALUES
    (1, 'Robot Fanuc', 'robot', 'operationnel', 12450, '2026-03-10', 'haute'),
    (2, 'Automate Wago CC100', 'automate', 'surveille', 12450, '2026-03-02', 'haute'),
    (3, 'Prehenseur double sac', 'outillage', 'maintenance_proche', 11820, '2026-03-05', 'moyenne'),
    (4, 'Convoyeur gravitaire', 'convoyeur', 'operationnel', 9800, '2026-03-01', 'moyenne');

INSERT INTO PlanMaint (id_plan_maint, id_equipement, libelle_plan, seuil_cycles, periodicite_jours, actif)
VALUES
    (1, 1, 'Nettoyage robot', 12500, 14, 1),
    (2, 2, 'Controle sauvegarde automate', 13000, 30, 1),
    (3, 3, 'Controle ventouses prehenseur', 12000, 10, 1),
    (4, 4, 'Inspection convoyeur', 10000, 21, 1);

INSERT INTO Commande (id_commande, reference_commande, id_recette, quantite_caisses_demandee, quantite_caisses_produite, statut, date_debut, date_fin, duree_production_min, energie_kwh)
VALUES
    (1, 'CMD-25032026-001', 1, 5, 5, 'terminee', '2026-03-25 07:30:00', '2026-03-25 08:04:00', 34, 12.80),
    (2, 'CMD-25032026-002', 3, 4, 4, 'terminee', '2026-03-25 08:15:00', '2026-03-25 08:49:00', 34, 11.40),
    (3, 'CMD-25032026-003', 2, 5, 3, 'en_cours', '2026-03-25 09:10:00', NULL, NULL, 9.20),
    (4, 'CMD-24032026-014', 1, 3, 3, 'terminee', '2026-03-24 14:20:00', '2026-03-24 14:39:00', 19, 7.95),
    (5, 'CMD-24032026-013', 3, 5, 5, 'terminee', '2026-03-24 13:15:00', '2026-03-24 13:56:00', 41, 13.65),
    (6, 'CMD-26032026-001', 2, 5, 0, 'planifiee', '2026-03-26 07:30:00', NULL, NULL, 0.00);

INSERT INTO DataProd (id_data_prod, id_commande, cadence_caisses_h, caisses_produites, sacs_huitres_consommes, sacs_st_jacques_consommes, date_mesure)
VALUES
    (1, 3, 102.00, 1, 0, 2, '2026-03-25 09:20:00'),
    (2, 3, 108.00, 2, 0, 4, '2026-03-25 09:35:00'),
    (3, 3, 112.00, 3, 0, 6, '2026-03-25 09:50:00'),
    (4, 2, 118.00, 4, 4, 4, '2026-03-25 08:48:00'),
    (5, 1, 120.00, 5, 10, 0, '2026-03-25 08:03:00');

INSERT INTO TempsCycle (id_temps_cycle, id_commande, numero_caisse, duree_cycle_sec, date_mesure)
VALUES
    (1, 1, 1, 395.00, '2026-03-25 07:37:00'),
    (2, 1, 2, 402.00, '2026-03-25 07:44:00'),
    (3, 1, 3, 398.00, '2026-03-25 07:51:00'),
    (4, 1, 4, 401.00, '2026-03-25 07:57:00'),
    (5, 1, 5, 399.00, '2026-03-25 08:03:00'),
    (6, 2, 1, 501.00, '2026-03-25 08:22:00'),
    (7, 2, 2, 494.00, '2026-03-25 08:30:00'),
    (8, 2, 3, 506.00, '2026-03-25 08:39:00'),
    (9, 2, 4, 498.00, '2026-03-25 08:48:00'),
    (10, 3, 1, 522.00, '2026-03-25 09:20:00'),
    (11, 3, 2, 510.00, '2026-03-25 09:35:00'),
    (12, 3, 3, 505.00, '2026-03-25 09:50:00');

INSERT INTO DataAutom (id_data_autom, charge_cpu, ram_utilisee, temperature_cpu, date_mesure)
VALUES
    (1, 38.00, 44.00, 49.00, '2026-03-25 09:40:00'),
    (2, 42.00, 46.00, 50.00, '2026-03-25 09:45:00'),
    (3, 47.00, 48.00, 51.00, '2026-03-25 09:50:00'),
    (4, 51.00, 52.00, 53.00, '2026-03-25 09:55:00'),
    (5, 54.00, 55.00, 55.50, '2026-03-25 10:00:00'),
    (6, 58.00, 57.00, 57.00, '2026-03-25 10:05:00');

INSERT INTO VariableOPCUA (id_variable_opcua, nom_variable, noeud_opcua, valeur_actuelle, unite, qualite, date_mesure)
VALUES
    (1, 'Etat robot', 'ns=2;s=Robot.Status', 'Production', '', 'good', '2026-03-25 10:05:00'),
    (2, 'Recette courante', 'ns=2;s=Recipe.Current', 'REC-STJ', '', 'good', '2026-03-25 10:05:00'),
    (3, 'Caisses produites', 'ns=2;s=Production.BoxesDone', '3', 'u', 'good', '2026-03-25 10:05:00'),
    (4, 'Connexion OPCUA', 'ns=2;s=System.OpcuaConnected', 'True', '', 'good', '2026-03-25 10:05:00'),
    (5, 'Temperature armoire', 'ns=2;s=Cabinet.Temp', '31.4', 'C', 'good', '2026-03-25 10:05:00');

INSERT INTO SeuilAlerte (id_seuil_alerte, indicateur, valeur_seuil, unite, niveau)
VALUES
    (1, 'charge_cpu', 75.00, '%', 'moyen'),
    (2, 'ram_utilisee', 80.00, '%', 'moyen'),
    (3, 'temperature_cpu', 65.00, 'C', 'critique');

INSERT INTO Alerte (id_alerte, id_seuil_alerte, source_alerte, niveau_alerte, message_alerte, valeur_mesuree, statut_alerte, date_creation)
VALUES
    (1, 1, 'Serveur supervision', 'moyen', 'Charge CPU elevee sur la VM de supervision', 58.00, 'surveillee', '2026-03-25 10:05:00'),
    (2, 3, 'Automate Wago CC100', 'critique', 'Temperature CPU proche du seuil critique', 57.00, 'ouverte', '2026-03-25 10:05:00'),
    (3, NULL, 'Ligne de palettisation PF3', 'moyen', 'Maintenance preventive du prehenseur a planifier', NULL, 'ouverte', '2026-03-25 09:58:00'),
    (4, NULL, 'OPCUA', 'faible', 'Reconnexion OPCUA effectuee avec succes', NULL, 'fermee', '2026-03-25 09:12:00');

INSERT INTO Defaut (id_defaut, id_equipement, code_defaut, criticite, description_defaut, date_defaut, acquitte)
VALUES
    (1, 3, 'PREH-021', 'moyenne', 'Depression ventouse inferieure insuffisante', '2026-03-25 09:42:00', 0),
    (2, 2, 'AUTO-007', 'haute', 'Temps de reponse entree capteur caisse anormal', '2026-03-25 09:15:00', 1),
    (3, 1, 'ROBOT-003', 'faible', 'Deviation trajectoire corrigee automatiquement', '2026-03-24 16:02:00', 1);

INSERT INTO InterMaint (id_inter_maint, id_plan_maint, id_equipement, type_intervention, statut, date_planifiee, date_realisation, commentaire)
VALUES
    (1, 3, 3, 'preventive', 'planifiee', '2026-03-26', NULL, 'Controle ventouses avant prise de poste'),
    (2, 1, 1, 'preventive', 'terminee', '2026-03-10', '2026-03-10', 'Nettoyage robot realise pendant arret programme'),
    (3, 2, 2, 'curative', 'terminee', '2026-03-18', '2026-03-18', 'Rechargement sauvegarde automate et test OK'),
    (4, 4, 4, 'preventive', 'en_retard', '2026-03-22', NULL, 'Controle rouleaux convoyeur non encore realise');

INSERT INTO ConsolLigne (id_consol_ligne, niveau_log, message_log, date_log)
VALUES
    (1, 'INFO', 'Serveur web lance avec succes', '2026-03-25 09:00:00'),
    (2, 'INFO', 'Connexion OPCUA etablie avec la ligne', '2026-03-25 09:01:00'),
    (3, 'WARNING', 'Ventouse inferieure en derive de pression', '2026-03-25 09:42:00'),
    (4, 'INFO', 'Commande CMD-25032026-003 demarree', '2026-03-25 09:10:00'),
    (5, 'WARNING', 'Maintenance preventive du prehenseur a planifier', '2026-03-25 09:58:00'),
    (6, 'INFO', 'Derniere communication automate recue', '2026-03-25 10:24:00');
