CREATE TABLE IF NOT EXISTS Role (
    id_role INT AUTO_INCREMENT PRIMARY KEY,
    code_role VARCHAR(30) NOT NULL UNIQUE,
    libelle_role VARCHAR(50) NOT NULL,
    description_role VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Utilisateur (
    id_utilisateur INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    mot_de_passe_hash VARCHAR(255) NOT NULL,
    nom_complet VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    id_role INT NOT NULL,
    actif TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_utilisateur_role
        FOREIGN KEY (id_role) REFERENCES Role (id_role)
);

CREATE TABLE IF NOT EXISTS Recette (
    id_recette INT AUTO_INCREMENT PRIMARY KEY,
    code_recette VARCHAR(30) NOT NULL UNIQUE,
    libelle_recette VARCHAR(100) NOT NULL,
    nb_sacs_huitres INT NOT NULL DEFAULT 0,
    nb_sacs_st_jacques INT NOT NULL DEFAULT 0,
    nb_caisses_palette INT NOT NULL DEFAULT 5,
    description_recette VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS Commande (
    id_commande INT AUTO_INCREMENT PRIMARY KEY,
    reference_commande VARCHAR(50) NOT NULL UNIQUE,
    id_recette INT NOT NULL,
    quantite_caisses_demandee INT NOT NULL,
    quantite_caisses_produite INT NOT NULL DEFAULT 0,
    statut VARCHAR(30) NOT NULL,
    date_debut DATETIME NOT NULL,
    date_fin DATETIME NULL,
    duree_production_min INT NULL,
    energie_kwh DECIMAL(8, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_commande_recette
        FOREIGN KEY (id_recette) REFERENCES Recette (id_recette)
);

CREATE TABLE IF NOT EXISTS LigneProd (
    id_ligne INT AUTO_INCREMENT PRIMARY KEY,
    nom_ligne VARCHAR(100) NOT NULL,
    etat_ligne VARCHAR(30) NOT NULL,
    mode_fonctionnement VARCHAR(30) NOT NULL,
    disponibilite DECIMAL(5, 2) NOT NULL DEFAULT 0,
    cadence_cible_caisses_h DECIMAL(6, 2) NOT NULL DEFAULT 0,
    derniere_communication DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS Equipement (
    id_equipement INT AUTO_INCREMENT PRIMARY KEY,
    nom_equipement VARCHAR(100) NOT NULL,
    type_equipement VARCHAR(50) NOT NULL,
    etat_equipement VARCHAR(30) NOT NULL,
    nb_cycles INT NOT NULL DEFAULT 0,
    date_derniere_maintenance DATE NULL,
    criticite VARCHAR(20) NOT NULL DEFAULT 'moyenne'
);

CREATE TABLE IF NOT EXISTS PlanMaint (
    id_plan_maint INT AUTO_INCREMENT PRIMARY KEY,
    id_equipement INT NOT NULL,
    libelle_plan VARCHAR(100) NOT NULL,
    seuil_cycles INT NOT NULL,
    periodicite_jours INT NOT NULL,
    actif TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT fk_planmaint_equipement
        FOREIGN KEY (id_equipement) REFERENCES Equipement (id_equipement)
);

CREATE TABLE IF NOT EXISTS InterMaint (
    id_inter_maint INT AUTO_INCREMENT PRIMARY KEY,
    id_plan_maint INT NULL,
    id_equipement INT NOT NULL,
    type_intervention VARCHAR(50) NOT NULL,
    statut VARCHAR(30) NOT NULL,
    date_planifiee DATE NOT NULL,
    date_realisation DATE NULL,
    commentaire VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_intermaint_plan
        FOREIGN KEY (id_plan_maint) REFERENCES PlanMaint (id_plan_maint),
    CONSTRAINT fk_intermaint_equipement
        FOREIGN KEY (id_equipement) REFERENCES Equipement (id_equipement)
);

CREATE TABLE IF NOT EXISTS Defaut (
    id_defaut INT AUTO_INCREMENT PRIMARY KEY,
    id_equipement INT NULL,
    code_defaut VARCHAR(50) NOT NULL,
    criticite VARCHAR(20) NOT NULL,
    description_defaut VARCHAR(255) NOT NULL,
    date_defaut DATETIME NOT NULL,
    acquitte TINYINT(1) NOT NULL DEFAULT 0,
    CONSTRAINT fk_defaut_equipement
        FOREIGN KEY (id_equipement) REFERENCES Equipement (id_equipement)
);

CREATE TABLE IF NOT EXISTS SeuilAlerte (
    id_seuil_alerte INT AUTO_INCREMENT PRIMARY KEY,
    indicateur VARCHAR(50) NOT NULL,
    valeur_seuil DECIMAL(10, 2) NOT NULL,
    unite VARCHAR(20) NOT NULL,
    niveau VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS Alerte (
    id_alerte INT AUTO_INCREMENT PRIMARY KEY,
    id_seuil_alerte INT NULL,
    source_alerte VARCHAR(100) NOT NULL,
    niveau_alerte VARCHAR(20) NOT NULL,
    message_alerte VARCHAR(255) NOT NULL,
    valeur_mesuree DECIMAL(10, 2) NULL,
    statut_alerte VARCHAR(20) NOT NULL DEFAULT 'ouverte',
    date_creation DATETIME NOT NULL,
    CONSTRAINT fk_alerte_seuil
        FOREIGN KEY (id_seuil_alerte) REFERENCES SeuilAlerte (id_seuil_alerte)
);

CREATE TABLE IF NOT EXISTS DataAutom (
    id_data_autom INT AUTO_INCREMENT PRIMARY KEY,
    charge_cpu DECIMAL(5, 2) NOT NULL,
    ram_utilisee DECIMAL(5, 2) NOT NULL,
    temperature_cpu DECIMAL(5, 2) NOT NULL,
    date_mesure DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS VariableOPCUA (
    id_variable_opcua INT AUTO_INCREMENT PRIMARY KEY,
    nom_variable VARCHAR(100) NOT NULL,
    noeud_opcua VARCHAR(150) NOT NULL,
    valeur_actuelle VARCHAR(100) NOT NULL,
    unite VARCHAR(20),
    qualite VARCHAR(30) NOT NULL,
    date_mesure DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS DataProd (
    id_data_prod INT AUTO_INCREMENT PRIMARY KEY,
    id_commande INT NOT NULL,
    cadence_caisses_h DECIMAL(6, 2) NOT NULL,
    caisses_produites INT NOT NULL,
    sacs_huitres_consommes INT NOT NULL,
    sacs_st_jacques_consommes INT NOT NULL,
    date_mesure DATETIME NOT NULL,
    CONSTRAINT fk_dataprod_commande
        FOREIGN KEY (id_commande) REFERENCES Commande (id_commande)
);

CREATE TABLE IF NOT EXISTS TempsCycle (
    id_temps_cycle INT AUTO_INCREMENT PRIMARY KEY,
    id_commande INT NOT NULL,
    numero_caisse INT NOT NULL,
    duree_cycle_sec DECIMAL(6, 2) NOT NULL,
    date_mesure DATETIME NOT NULL,
    CONSTRAINT fk_tempscycle_commande
        FOREIGN KEY (id_commande) REFERENCES Commande (id_commande)
);

CREATE TABLE IF NOT EXISTS ConsolLigne (
    id_consol_ligne INT AUTO_INCREMENT PRIMARY KEY,
    niveau_log VARCHAR(20) NOT NULL,
    message_log VARCHAR(255) NOT NULL,
    date_log DATETIME NOT NULL
);

DROP VIEW IF EXISTS vue_generale_commandes;

CREATE VIEW vue_generale_commandes AS
SELECT
    c.id_commande,
    c.reference_commande,
    r.code_recette,
    r.libelle_recette,
    c.quantite_caisses_demandee,
    c.quantite_caisses_produite,
    c.statut,
    c.date_debut,
    c.date_fin,
    c.duree_production_min,
    c.energie_kwh,
    ROUND(AVG(tc.duree_cycle_sec), 2) AS temps_cycle_moyen_sec
FROM Commande c
JOIN Recette r ON r.id_recette = c.id_recette
LEFT JOIN TempsCycle tc ON tc.id_commande = c.id_commande
GROUP BY
    c.id_commande,
    c.reference_commande,
    r.code_recette,
    r.libelle_recette,
    c.quantite_caisses_demandee,
    c.quantite_caisses_produite,
    c.statut,
    c.date_debut,
    c.date_fin,
    c.duree_production_min,
    c.energie_kwh;
