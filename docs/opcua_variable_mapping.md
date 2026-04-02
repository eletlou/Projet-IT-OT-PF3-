# Mapping Variables OPC UA

Analyse realisee le 2 avril 2026 sur la branche `restore-test-opcua` (commit `44ce676`).

Sources lues :
- `db/01-schema.sql`
- `db/02-seed.sql`
- `/home/user/Téléchargements/ExportDB.sql`
- `app/app/routes/`
- `app/app/services/`
- `app/app/repositories/`
- `app/app/templates/`
- `app/app/config.py`
- `app/app/data/opcua_test_nodes.txt`
- `app/app/opcua_test_app.py`
- `app/run_opcua_test.py`

Point bloquant signale tout de suite :
- Aucun `document.txt` n'a ete trouve dans le workspace ni sous `/home/user` pendant cette analyse.

## 1. Resume executif

### Ce qui est deja vrai dans le code

- Il existe deja 2 chemins OPC UA distincts dans le projet.
- Chemin 1 : `/commandes/` lit en direct un seul NodeId WAGO configure dans `app/app/config.py`.
- Chemin 2 : `/supervision/opcua-test` lit la liste des NodeIds de `app/app/data/opcua_test_nodes.txt` sans toucher aux ecrans metier.
- La page `/supervision/` ne lit pas le WAGO en direct : elle affiche uniquement la table SQL `VariableOPCUA`.

### Variables pretes a etre connectees immediatement

- `num_caisse_courante` -> `ns=4;s=|var|EAG2.Application.GVL_IHM.IHM_NB_Caisse`
- `quantite_caisses_demandee_commande_courante` -> `ns=4;s=|var|EAG2.Application.G7_PROD.stCurrentOrder.iCaisseDemande`
- `defaut_actif` -> `ns=4;s=|var|EAG2.Application.GVL_OPCUA.OPCUA.xDefautActif`
- `message_defaut_actif` -> `ns=4;s=|var|EAG2.Application.GVL_OPCUA.OPCUA.sDefautMessage`
- `heartbeat_opcua` -> `ns=4;s=|var|EAG2.Application.GVL_OPCUA.OPCUA.xHeartbeat`

### Variables a confirmer avec l'automaticien

- `quantite_caisses_produite_commande_courante` : conflit entre `iCaisseProduite`, `uiBoxesCompleted` et le node de demo `ns=2;s=Production.BoxesDone`
- `mode_fonctionnement_ligne` : `eMode` semble le meilleur candidat, mais la traduction enum OPC UA -> libelle IHM n'est pas definie
- `etat_ligne` : ne pas melanger `eMode`, `eStep` et l'etat metier stocke en BDD sans convention de normalisation
- `etat_robot`, `recette_courante`, `temperature_armoire_c`, `connexion_opcua` : presents en base via des NodeIds `ns=2` de demo, absents de la liste WAGO confirmee

### Variables manquantes dans l'IHM actuelle

- `stock_caisses`
- `stock_huitres`
- `etape_processus`
- `robot_go_echo_code`
- `voyant_caisse_1_a_5`

### Variables manquantes dans la BDD actuelle

- `heartbeat_opcua`
- `mode_processus`
- `etape_processus`
- `defaut_actif`
- `message_defaut_actif`
- une notion canonique unique pour le compteur de boites / numero de caisse

### Variables manquantes dans les NodeIds fournis

- `charge_cpu_pct`
- `ram_utilisee_pct`
- `temperature_cpu_c`
- `cadence_caisses_h`
- `sacs_huitres_consommes`
- `sacs_st_jacques_consommes`
- `code_defaut_actif`
- des compteurs par equipement pour la maintenance

### Observations structurantes

- La liste `opcua_test_nodes.txt` contient 21 NodeIds WAGO confirmes le 2 avril 2026.
- Le fichier de seed `db/02-seed.sql` contient des variables OPC UA de demo en `ns=2`, pas les NodeIds WAGO `ns=4` utilises par la page de test.
- Le rendu local des pages a pu etre verifie via une instance lancee sur `http://127.0.0.1:5006`.
- Au 2 avril 2026, la page `/commandes/` essaie deja de lire le WAGO au chargement et retourne `Indisponible` si `172.30.30.20:4840` ne repond pas. Le log observe etait : `timed out Le port OPC UA ne repond pas a temps.`

## 2. Ecarts de schema SQL

Le seul SQL local additionnel trouve hors repo est `/home/user/Téléchargements/ExportDB.sql`.

| Table locale | Table repo correspondante | Colonnes differentes | Impact potentiel sur le mapping OPC UA | Recommandation non destructive |
|---|---|---|---|---|
| `table_formateur` | aucune | `id`, `name`, `login` uniquement | aucun mapping OPC UA possible si ce dump est pris comme base principale ; il manque toutes les tables metier attendues par Flask | ne pas substituer `ExportDB.sql` a `db/01-schema.sql` |
| `ExportDB.sql` | `VariableOPCUA`, `DataAutom`, `DataProd`, `Alerte`, `Defaut`, `Commande`, `InterMaint`, `vue_generale_commandes` | tables absentes | les ecrans `/dashboard/`, `/commandes/`, `/supervision/` et le mapping OPC UA deviennent incomplets ou inexploitables | conserver `db/01-schema.sql` comme schema de reference ; garder `ExportDB.sql` separe comme source externe sans l'injecter dans la BDD de l'app |
| `ExportDB.sql` | `Role`, `Utilisateur` | structure absente / incompatible | la navigation, les droits et la connexion applicative ne peuvent pas fonctionner avec ce dump seul | ne pas l'utiliser comme schema applicatif |

### Ecart de donnees locales observe a l'execution

Ce n'est pas un ecart de schema, mais c'est important pour la lecture des pages locales :

- le 2 avril 2026, la BDD locale lancee pour verifier les pages ne correspondait pas entierement au contenu attendu de `db/02-seed.sql`
- comptes observes dans le conteneur MySQL local : `Commande=0`, `DataProd=0`, `DataAutom=0`, `VariableOPCUA=0`, `Alerte=0`, `Defaut=0`, `InterMaint=0`
- comptes non nuls observes : `Recette=3`, `Equipement=4`, `PlanMaint=4`, `SeuilAlerte=3`, `Utilisateur=4`, `Role=4`

Impact :

- les libelles IHM ont bien ete confirmes en local
- les valeurs de demonstration affichees dans les pages locales ne peuvent pas, a elles seules, servir de reference fonctionnelle pour le mapping OPC UA
- le mapping ci-dessous s'appuie donc sur le code, le schema, le seed du repo et les NodeIds confirmes

## 3. Normalisation de noms

| Nom metier canonique propose | IHM / libelle visible | Code / SQL actuel | Alias NodeIds ou sources | Decision de normalisation |
|---|---|---|---|---|
| `num_caisse_courante` | `Compteur OPC UA`, `Num caisse` | `OPCUA_COMMAND_COUNTER_LABEL`, carte `/commandes/` | `IHM_NB_Caisse`, `iNbCaisseIHM`, `uiCurrentBoxNumber` | garder `IHM_NB_Caisse` comme source principale car c'est deja le cablage live existant |
| `quantite_caisses_demandee_commande_courante` | `Quantite` cote objectif / progression | `Commande.quantite_caisses_demandee`, `vue_generale_commandes.quantite_caisses_demandee` | `stCurrentOrder.iCaisseDemande` | correspondance claire ; pas de conflit detecte |
| `quantite_caisses_produite_commande_courante` | `Caisses produites`, numerateur de `Quantite` | `Commande.quantite_caisses_produite`, `DataProd.caisses_produites`, `VariableOPCUA.Caisses produites` | `stCurrentOrder.iCaisseProduite`, `uiBoxesCompleted`, `ns=2;s=Production.BoxesDone` | choisir une source maitre unique avec l'automaticien avant tout cablage durable |
| `etat_comm_sante_opcua` | `Connexion OPCUA`, `Derniere communication` | `LigneProd.derniere_communication`, `VariableOPCUA.Connexion OPCUA` | `xHeartbeat`, `ns=2;s=System.OpcuaConnected` | separer le heartbeat brut du timestamp de derniere communication calcule cote serveur |
| `mode_processus` | `Mode automatique`, `Etat ligne` | `LigneProd.mode_fonctionnement`, `LigneProd.etat_ligne` | `eMode`, `eStep` | ne pas fusionner `mode` et `step` dans un seul champ SQL |
| `defaut_actif` / `message_defaut_actif` | `Evenements maintenance`, `Defauts ligne` | `Defaut.*`, `Alerte.*` | `xDefautActif`, `sDefautMessage` | utiliser `xDefautActif` et `sDefautMessage` pour l'etat courant, garder `Defaut`/`Alerte` pour l'historique |

## 4. Tableau complet de mapping OPC UA

| Classification | Zone de l'application | Page / ecran | Libelle visible dans l'IHM | Nom variable metier propose | Table SQL | Colonne SQL | Fichier source / emplacement code | NodeId OPC UA | Type de donnee | Sens d'echange | Frequence / mode de mise a jour | Statut | Commentaire technique |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deja_cablee | Production | `/commandes/` | `Compteur OPC UA / Num caisse` | `num_caisse_courante` | — | — | `app/app/config.py:30-42`, `app/app/services/command_service.py:12-38`, `app/app/templates/commands/index.html:31-40`, `app/app/data/opcua_test_nodes.txt:3` | `ns=4;s=|var|EAG2.Application.GVL_IHM.IHM_NB_Caisse` | hypothese `Int/UInt` | lecture | chargement de page + auto-refresh 5 s ; 3 tentatives de 8 s | trouve | seul cablage live deja present dans l'ecran metier ; a ne pas casser |
| nodeid_confirme_non_rattache | Validation OPC UA | `/supervision/opcua-test` | `Voyants caisse 1 a 5` | `voyant_caisse_1_a_5` | — | — | `app/app/data/opcua_test_nodes.txt:4-8`, `app/app/templates/supervision/opcua_test.html:134-205` | `ns=4;s=|var|EAG2.Application.GVL_IHM.IHM_Voy_Caisse_[1..5]` | hypothese `Bool` | lecture-ecriture potentielle | manuel via page de test | trouve | 5 NodeIds confirmes, aucune page metier ne les consomme aujourd'hui |
| nodeid_confirme_non_rattache | Validation OPC UA / Production | `/supervision/opcua-test` | `iNbCaisseIHM` | `num_caisse_ihm_alias` | — | — | `app/app/data/opcua_test_nodes.txt:9`, `app/app/templates/supervision/opcua_test.html:134-205` | `ns=4;s=|var|EAG2.Application.G7_PROD.iNbCaisseIHM` | hypothese `Int` | lecture-ecriture potentielle | manuel via page de test | trouve | alias probable du compteur de caisse ; a departager avec `IHM_NB_Caisse` et `uiCurrentBoxNumber` |
| visible_ihm_plus_nodeid | Production | `/commandes/`, `/dashboard/` | `Quantite` cote objectif / progression | `quantite_caisses_demandee_commande_courante` | `Commande`, `vue_generale_commandes` | `quantite_caisses_demandee` | `db/01-schema.sql:32-46,177-205`, `app/app/templates/dashboard/index.html:84-99`, `app/app/templates/commands/index.html:95-120`, `app/app/data/opcua_test_nodes.txt:10` | `ns=4;s=|var|EAG2.Application.G7_PROD.stCurrentOrder.iCaisseDemande` | hypothese `Int` | lecture | aujourd'hui par BDD ; candidat direct pour lecture live | trouve | meilleur match fonctionnel 1:1 entre l'IHM et le WAGO |
| visible_ihm_plus_nodeid | Production | `/dashboard/`, `/commandes/`, `/supervision/` | `Caisses produites` | `quantite_caisses_produite_commande_courante` | `Commande`, `DataProd`, `VariableOPCUA` | `quantite_caisses_produite`, `caisses_produites`, `valeur_actuelle` | `db/01-schema.sql:32-46,136-156`, `app/app/templates/dashboard/index.html:149-156`, `app/app/templates/commands/index.html:104-118`, `db/02-seed.sql:108-114` | candidat `ns=4;s=|var|EAG2.Application.G7_PROD.stCurrentOrder.iCaisseProduite` | hypothese `Int` | lecture | aujourd'hui par BDD ; candidat live a confirmer | a_confirmer | conflit avec `uiBoxesCompleted` et avec le node de demo `ns=2;s=Production.BoxesDone` |
| nodeid_confirme_non_rattache | Production | `/supervision/opcua-test` | `uiBoxCount` | `compteur_boites_global` | — | — | `app/app/data/opcua_test_nodes.txt:17`, `app/app/templates/supervision/opcua_test.html:134-205` | `ns=4;s=|var|EAG2.Application.GVL_OPCUA.OPCUA.uiBoxCount` | hypothese `UInt` | lecture-ecriture potentielle | manuel via page de test | trouve | semantique exacte a valider : cumul global ou compteur de lot |
| nodeid_confirme_non_rattache | Production | `/supervision/opcua-test` | `uiBoxesCompleted` | `boites_terminees` | — | — | `app/app/data/opcua_test_nodes.txt:18`, `app/app/templates/supervision/opcua_test.html:134-205` | `ns=4;s=|var|EAG2.Application.GVL_OPCUA.OPCUA.uiBoxesCompleted` | hypothese `UInt` | lecture-ecriture potentielle | manuel via page de test | trouve | candidat naturel pour `quantite_caisses_produite_commande_courante` |
| nodeid_confirme_non_rattache | Production | `/supervision/opcua-test` | `uiCurrentBoxNumber` | `numero_boite_courante` | — | — | `app/app/data/opcua_test_nodes.txt:19`, `app/app/templates/supervision/opcua_test.html:134-205` | `ns=4;s=|var|EAG2.Application.GVL_OPCUA.OPCUA.uiCurrentBoxNumber` | hypothese `UInt` | lecture-ecriture potentielle | manuel via page de test | trouve | recouvre probablement la notion IHM `Num caisse` |
| visible_sans_nodeid | Production | `/dashboard/`, `/commandes/` | `Cadence actuelle`, `Dernieres mesures de production` | `cadence_caisses_h` | `DataProd` | `cadence_caisses_h` | `app/app/repositories/command_repository.py:27-38`, `app/app/templates/dashboard/index.html:149-153`, `app/app/templates/commands/index.html:44-62` | — | `Decimal` | lecture | dashboard et commandes auto-refresh 5 s via BDD | manquant | aucun NodeId direct fourni ; une derivation depuis `rCurrentBoxCycle_s` est possible mais non specifiee |
| nodeid_confirme_non_rattache | Production | `/supervision/opcua-test` | `rCurrentBoxCycle_s` | `temps_cycle_caisse_courant_s` | — | — | `app/app/data/opcua_test_nodes.txt:20`, `app/app/templates/supervision/opcua_test.html:134-205` | `ns=4;s=|var|EAG2.Application.GVL_OPCUA.OPCUA.rCurrentBoxCycle_s` | hypothese `Real` | lecture-ecriture potentielle | manuel via page de test | trouve | valeur instantanee ; ne correspond pas directement au KPI moyen ou max affiche dans l'IHM |
| visible_sans_nodeid | Production | `/commandes/` | `Focus recent`, `Cycle max` | `temps_cycle_moyen_et_max_sec` | `TempsCycle`, `vue_generale_commandes` | `duree_cycle_sec`, `temps_cycle_moyen_sec` | `app/app/repositories/command_repository.py:41-54`, `app/app/templates/commands/index.html:65-83` | — | `Decimal` | lecture | page load + auto-refresh 5 s | manquant | KPI historises ; aucun NodeId WAGO confirme pour le max |
| visible_sans_nodeid | Production | `/dashboard/` | `Sacs huitres` | `sacs_huitres_consommes` | `DataProd` | `sacs_huitres_consommes` | `db/01-schema.sql:146-156`, `app/app/templates/dashboard/index.html:158-161` | — | `Int` | lecture | dashboard auto-refresh 5 s via BDD | manquant | ne pas confondre la consommation affichee avec le stock `diStockHuitres` |
| visible_sans_nodeid | Production | `/dashboard/` | `Sacs saint jacques` | `sacs_st_jacques_consommes` | `DataProd` | `sacs_st_jacques_consommes` | `db/01-schema.sql:146-156`, `app/app/templates/dashboard/index.html:162-165` | — | `Int` | lecture | dashboard auto-refresh 5 s via BDD | manquant | aucun NodeId fourni dans la liste confirmee |
| nodeid_confirme_non_rattache | Logistique | `/supervision/opcua-test` | `diStockCaisses` | `stock_caisses` | — | — | `app/app/data/opcua_test_nodes.txt:21`, `app/app/templates/supervision/opcua_test.html:134-205` | `ns=4;s=|var|EAG2.Application.GVL_OPCUA.OPCUA.diStockCaisses` | hypothese `DInt` | lecture-ecriture potentielle | manuel via page de test | trouve | NodeId connu sans ecran metier actuel |
| nodeid_confirme_non_rattache | Matiere | `/supervision/opcua-test` | `diStockHuitres` | `stock_huitres` | — | — | `app/app/data/opcua_test_nodes.txt:22`, `app/app/templates/supervision/opcua_test.html:134-205` | `ns=4;s=|var|EAG2.Application.GVL_OPCUA.OPCUA.diStockHuitres` | hypothese `DInt` | lecture-ecriture potentielle | manuel via page de test | trouve | utile seulement si un besoin stock apparait dans l'IHM |
| present_en_base_non_reliee | Production / Recette | `/supervision/` | `Recette courante` | `recette_courante` | `VariableOPCUA` | `nom_variable`, `valeur_actuelle`, `noeud_opcua` | `app/app/repositories/supervision_repository.py:74-80`, `app/app/templates/supervision/index.html:118-147`, `db/02-seed.sql:108-114` | `ns=2;s=Recipe.Current` | `String` | lecture | page load via BDD uniquement | a_confirmer | variable de demo `ns=2`, absente du fichier WAGO confirme |
| visible_ihm_plus_nodeid | Supervision | `/dashboard/`, `/supervision/` | `Etat ligne` | `etat_ligne` | `LigneProd` | `etat_ligne` | `app/app/repositories/dashboard_repository.py:48-56`, `app/app/repositories/supervision_repository.py:4-12`, `app/app/templates/dashboard/index.html:10-17`, `app/app/templates/supervision/index.html:9-15` | candidat `ns=4;s=|var|EAG2.Application.GVL_OPCUA.OPCUA.eMode` | hypothese `Enum/String` | lecture | dashboard 5 s ; supervision page load | a_confirmer | `etat_ligne` et `mode_fonctionnement` sont deux notions SQL distinctes ; ne pas les ecraser avec une seule enum brute |
| visible_ihm_plus_nodeid | Supervision | `/dashboard/` | `Mode automatique / manuel` | `mode_fonctionnement_ligne` | `LigneProd` | `mode_fonctionnement` | `db/01-schema.sql:48-56`, `app/app/templates/dashboard/index.html:12-17`, `app/app/data/opcua_test_nodes.txt:13` | `ns=4;s=|var|EAG2.Application.GVL_OPCUA.OPCUA.eMode` | hypothese `Enum` | lecture | dashboard auto-refresh 5 s | a_confirmer | probable meilleur candidat, mais la table de traduction enum OPC UA -> libelle IHM n'existe pas |
| visible_ihm_plus_nodeid | Supervision | `/dashboard/`, `/supervision/` | `Derniere communication`, `Connexion OPCUA` | `derniere_communication_automate` | `LigneProd`, `VariableOPCUA` | `derniere_communication`, `valeur_actuelle` | `db/01-schema.sql:48-56,136-144`, `app/app/templates/dashboard/index.html:19-27`, `app/app/templates/supervision/index.html:9-15`, `db/02-seed.sql:113` | candidat `ns=4;s=|var|EAG2.Application.GVL_OPCUA.OPCUA.xHeartbeat` | hypothese `Bool` + timestamp serveur | lecture | dashboard 5 s ; supervision page load | a_confirmer | le node WAGO donne un heartbeat ; la date affichee doit etre reconstruite cote serveur |
| nodeid_confirme_non_rattache | Supervision | `/supervision/opcua-test` | `eStep` | `etape_processus` | — | — | `app/app/data/opcua_test_nodes.txt:14`, `app/app/templates/supervision/opcua_test.html:134-205` | `ns=4;s=|var|EAG2.Application.GVL_OPCUA.OPCUA.eStep` | hypothese `Enum` | lecture-ecriture potentielle | manuel via page de test | trouve | aucun champ SQL actuel ne porte explicitement cette etape |
| visible_ihm_plus_nodeid | Supervision | `/supervision/`, `/supervision/opcua-test` | `Defaut actif` | `defaut_actif` | projection future `Defaut` / `Alerte` | — | `app/app/templates/supervision/index.html:62-80`, `app/app/data/opcua_test_nodes.txt:15` | `ns=4;s=|var|EAG2.Application.GVL_OPCUA.OPCUA.xDefautActif` | hypothese `Bool` | lecture | aujourd'hui manuel ; cible page load ou event-driven | trouve | bon candidat pour l'etat courant ; l'historique doit rester dans les tables SQL existantes |
| visible_ihm_plus_nodeid | Supervision | `/supervision/`, `/supervision/opcua-test` | `Message defaut actif` | `message_defaut_actif` | projection future `Defaut` / `Alerte` | `description_defaut`, `message_alerte` | `app/app/templates/supervision/index.html:62-80`, `app/app/data/opcua_test_nodes.txt:16` | `ns=4;s=|var|EAG2.Application.GVL_OPCUA.OPCUA.sDefautMessage` | hypothese `String` | lecture | aujourd'hui manuel ; cible page load ou event-driven | trouve | a historiser si tu veux conserver les evenements passes |
| present_en_base_non_reliee | Supervision | `/supervision/` | `Etat robot` | `etat_robot` | `VariableOPCUA` | `valeur_actuelle`, `noeud_opcua` | `app/app/repositories/supervision_repository.py:74-80`, `app/app/templates/supervision/index.html:118-147`, `db/02-seed.sql:110` | `ns=2;s=Robot.Status` | `String/Enum` | lecture | page load via BDD uniquement | a_confirmer | aucun NodeId WAGO confirme pour remplacer cette variable de demo |
| nodeid_confirme_non_rattache | Robot | `/supervision/opcua-test` | `uiGoEchoCode` | `robot_go_echo_code` | — | — | `app/app/data/opcua_test_nodes.txt:23`, `app/app/templates/supervision/opcua_test.html:134-205` | `ns=4;s=|var|EAG2.Application.GVL_Robot.Robot.uiGoEchoCode` | hypothese `UInt` | lecture-ecriture potentielle | manuel via page de test | trouve | signification a confirmer avec l'automaticien avant toute integration metier |
| visible_sans_nodeid | Supervision technique | `/supervision/` | `CPU` | `charge_cpu_pct` | `DataAutom`, `SeuilAlerte` | `charge_cpu`, `valeur_seuil` | `db/01-schema.sql:107-134`, `app/app/repositories/supervision_repository.py:15-23,47-53`, `app/app/templates/supervision/index.html:17-29,85-115,151-177` | — | `Decimal` | lecture | page load ; seuil modifiable via POST | manquant | aucune variable WAGO confirmee dans les sources fournies |
| visible_sans_nodeid | Supervision technique | `/supervision/` | `RAM` | `ram_utilisee_pct` | `DataAutom`, `SeuilAlerte` | `ram_utilisee`, `valeur_seuil` | `db/01-schema.sql:107-134`, `app/app/repositories/supervision_repository.py:15-23,47-53`, `app/app/templates/supervision/index.html:17-29,85-115,151-177` | — | `Decimal` | lecture | page load ; seuil modifiable via POST | manquant | aucune variable WAGO confirmee dans les sources fournies |
| visible_sans_nodeid | Supervision technique | `/supervision/` | `Temperature CPU` | `temperature_cpu_c` | `DataAutom`, `SeuilAlerte` | `temperature_cpu`, `valeur_seuil` | `db/01-schema.sql:107-134`, `app/app/repositories/supervision_repository.py:15-23,47-53`, `app/app/templates/supervision/index.html:17-29,85-115,151-177` | — | `Decimal` | lecture | page load ; seuil modifiable via POST | manquant | ne pas substituer `Cabinet.Temp` sans validation fonctionnelle |
| present_en_base_non_reliee | Environnement | `/supervision/` | `Temperature armoire` | `temperature_armoire_c` | `VariableOPCUA` | `valeur_actuelle`, `noeud_opcua` | `app/app/repositories/supervision_repository.py:74-80`, `app/app/templates/supervision/index.html:118-147`, `db/02-seed.sql:114` | `ns=2;s=Cabinet.Temp` | `Decimal` | lecture | page load via BDD uniquement | a_confirmer | variable de demo `ns=2`, absente des NodeIds WAGO confirmes |
| visible_sans_nodeid | Maintenance | `/maintenance/` | `Cycles`, `Seuil`, `Derniere maintenance` | `etat_cycles_maintenance` | `Equipement`, `PlanMaint` | `nb_cycles`, `seuil_cycles`, `date_derniere_maintenance` | `app/app/repositories/maintenance_repository.py:16-62`, `app/app/templates/maintenance/index.html:32-64` | — | `Int / Date` | lecture | page load | manquant | la liste WAGO fournie ne contient aucun compteur par equipement ; impossible de cabler proprement la maintenance sans nouveaux NodeIds |
| bdd_seulement | Supervision | `/supervision/` | `Seuils techniques` | `seuils_techniques` | `SeuilAlerte` | `indicateur`, `valeur_seuil`, `unite`, `niveau` | `app/app/repositories/supervision_repository.py:47-53,95-103`, `app/app/templates/supervision/index.html:151-177` | — | `Decimal / Enum` | lecture-ecriture BDD | page load + formulaire POST | trouve | parametrage purement BDD ; pas de cablage OPC UA direct dans le repo actuel |
| bdd_seulement | Maintenance | `/maintenance/` | `Nouvelle intervention`, `Interventions` | `interventions_maintenance` | `InterMaint` | `type_intervention`, `statut`, `date_planifiee`, `date_realisation`, `commentaire` | `app/app/repositories/maintenance_repository.py:66-110`, `app/app/templates/maintenance/index.html:67-141` | — | `String / Date` | lecture-ecriture BDD | page load + formulaire POST | trouve | hors perimetre OPC UA direct |
| hors_perimetre | Administration | `/utilisateurs/` | `Gestion des utilisateurs` | `utilisateurs_et_roles` | `Utilisateur`, `Role` | `login`, `nom_complet`, `email`, `id_role`, `actif` | `app/app/repositories/user_repository.py`, `app/app/templates/users/index.html` | — | `String / Bool` | lecture-ecriture BDD | page load + formulaire POST | trouve | aucune variable OPC UA candidate detectee sur cette page |

## 5. Variables pretes a cabler

- `num_caisse_courante` : deja cablee sur `/commandes/`, source WAGO confirmee, a conserver telle quelle
- `quantite_caisses_demandee_commande_courante` : NodeId confirme et correspondance metier claire
- `defaut_actif` : NodeId confirme et usage supervision evident
- `message_defaut_actif` : NodeId confirme et usage supervision evident
- `heartbeat_opcua` : NodeId confirme, utile pour reconstruire `Derniere communication`

## 6. Variables a confirmer

- choisir la source maitre de `quantite_caisses_produite_commande_courante`
- valider la traduction des enums `eMode` et `eStep`
- confirmer si `etat_robot`, `recette_courante`, `temperature_armoire_c` existent vraiment cote WAGO ou s'ils sont seulement des variables de demo SQL
- confirmer si la cadence doit etre exposee directement par automate ou derivee du temps de cycle
- demander des NodeIds specifiques pour CPU, RAM, temperature CPU et pour les compteurs de maintenance par equipement si ces donnees doivent venir de l'automate

## 7. Recommandations minimales sans casser l'existant

1. Conserver tel quel le cablage actuel de `/commandes/` vers `IHM_NB_Caisse`.
2. Ne pas ecraser la table `VariableOPCUA` avec des NodeIds WAGO `ns=4` tant qu'une table de correspondance n'existe pas.
3. Utiliser les libelles IHM comme reference fonctionnelle et documenter, pour chaque variable, une seule source OPC UA maitre.
4. Garder `/supervision/opcua-test` comme sas de validation terrain et ne faire entrer dans les ecrans metier que les NodeIds stabilises avec l'automaticien.
5. Ajouter si besoin une table de correspondance dediee, sans refonte brutale du modele existant.

### Proposition non destructive de structure cible

Si tu veux historiser proprement le mapping sans casser `VariableOPCUA`, la structure la plus simple est d'ajouter une table de correspondance dediee :

```sql
CREATE TABLE IF NOT EXISTS CorrespondanceOPCUA (
    id_correspondance INT AUTO_INCREMENT PRIMARY KEY,
    zone_application VARCHAR(50) NOT NULL,
    page_ecran VARCHAR(100) NOT NULL,
    libelle_ihm VARCHAR(150) NOT NULL,
    nom_variable_metier VARCHAR(120) NOT NULL,
    table_sql VARCHAR(80) NULL,
    colonne_sql VARCHAR(120) NULL,
    nodeid_opcua VARCHAR(180) NULL,
    type_donnee VARCHAR(40) NULL,
    sens_echange VARCHAR(30) NOT NULL DEFAULT 'lecture',
    mode_mise_a_jour VARCHAR(80) NULL,
    statut_mapping VARCHAR(30) NOT NULL DEFAULT 'a_confirmer',
    commentaire_technique VARCHAR(255) NULL,
    actif TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

Pourquoi cette option est la moins risquee :

- elle ne casse aucune requete existante
- elle n'oblige pas a remodeler `VariableOPCUA`
- elle permet de conserver separement les variables de demo SQL et les vrais NodeIds WAGO confirmes
- elle sert de referentiel commun entre IHM, Python, BDD et automaticien

## 8. Verification locale realisee

- pages verifiees en local : `/dashboard/`, `/commandes/`, `/maintenance/`, `/supervision/`, `/supervision/opcua-test`, `/utilisateurs/`
- methode : login `admin / admin1234` sur une instance locale lancee temporairement en `http://127.0.0.1:5006`
- resultat notable :
  - les libelles IHM ont ete confirmes par rendu HTML
  - `/commandes/` tente deja une lecture OPC UA reelle au chargement
  - la BDD locale utilisee pour le rendu ne contenait pas toutes les donnees de `db/02-seed.sql`, donc les valeurs affichees localement n'ont pas ete prises comme reference metier
