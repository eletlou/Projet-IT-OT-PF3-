-- A importer manuellement dans la base lesviviersdenoirmoutier depuis Adminer.
-- Ce script conserve les roles, utilisateurs, recettes et seuils techniques.

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE TempsCycle;
TRUNCATE TABLE DataProd;
TRUNCATE TABLE Commande;
TRUNCATE TABLE InterMaint;
TRUNCATE TABLE PlanMaint;
TRUNCATE TABLE Equipement;
TRUNCATE TABLE Defaut;
TRUNCATE TABLE Alerte;
TRUNCATE TABLE ConsolLigne;
TRUNCATE TABLE DataAutom;
TRUNCATE TABLE LigneProd;
TRUNCATE TABLE VariableOPCUA;

SET FOREIGN_KEY_CHECKS = 1;
