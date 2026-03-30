# LES VIVIERS DE NOIRMOUTIER

Application web de supervision industrielle realisee avec `Flask`, `Jinja2`, `MySQL` et `Docker Compose`.

## 1. Objectif du projet

Ce projet permet de superviser une ligne de production a travers une interface web simple.

Fonctions principales :

- connexion des utilisateurs avec session Flask
- gestion des roles : `Administrateur`, `Operateur`, `Responsable`, `Integrateur`
- vue d'ensemble de la ligne de production
- suivi des commandes et des recettes
- maintenance curative et preventive
- supervision technique : alertes, variables automate, seuils, OPCUA
- gestion des utilisateurs

## 2. Architecture simple

Le projet repose sur 2 briques principales :

- `web` : application Flask qui affiche les pages et execute la logique metier
- `db` : base de donnees MySQL qui stocke les utilisateurs, commandes, alertes et donnees de supervision

Le fichier `docker-compose.yml` orchestre ces 2 services.

## 3. Demarrage du projet

### Commande la plus simple

```bash
./start.sh
```

Ce script :

- demarre le projet la premiere fois
- relance rapidement les conteneurs si le projet a deja ete lance
- evite de supprimer et recreer les conteneurs a chaque usage

### Mettre l'application en pause

```bash
./stop.sh
```

Cette commande arrete les services sans supprimer les conteneurs. C'est la bonne commande au quotidien si on veut liberer des ressources puis redemarrer plus tard.

### Reinitialiser completement le projet

```bash
./reset.sh
```

Cette commande est plus lourde. Elle supprime les conteneurs et le volume MySQL, puis reconstruit le projet avec une base propre. A utiliser seulement si on veut vraiment repartir de zero.

### Commandes Docker equivalentes

```bash
docker compose up --build -d
docker compose stop
docker compose down -v
```

## 4. Acces navigateur

- application Flask : `http://localhost:5005`

## 5. Comptes de demonstration

- `admin / admin1234`
- `operateur / operateur1234`
- `responsable / responsable1234`
- `integrateur / integrateur1234`

## 6. Variables d'environnement

Le projet contient deja un fichier `.env` local pour le developpement.

Modele de reference :

```env
MYSQL_ROOT_PASSWORD=uimm
MYSQL_DATABASE=les_viviers_de_noirmoutier
APP_PORT=5005
SESSION_SECRET=change_me_session_secret
```

Valeur conseillee pour eviter les conflits entre equipes en local :

```env
APP_PORT=5005
```

## 7. Arborescence utile

- `docker-compose.yml` : declaration de la stack client `web` + `db`
- `db/01-schema.sql` : creation de la structure de la base
- `db/02-seed.sql` : insertion des donnees de demonstration
- `app/run.py` : point d'entree Flask
- `app/app/__init__.py` : creation et configuration de l'application
- `app/app/routes/` : routes Flask par module fonctionnel
- `app/app/services/` : logique metier et orchestration
- `app/app/repositories/` : requetes SQL et acces aux donnees
- `app/app/templates/` : pages HTML Jinja2
- `app/app/static/css/style.css` : styles CSS
- `app/app/static/js/app.js` : scripts JavaScript

## 8. Pages disponibles

- `/login` : connexion
- `/dashboard/` : vue d'ensemble
- `/commandes/` : suivi production
- `/maintenance/` : interventions et plans preventifs
- `/supervision/` : alertes, automate, OPCUA et seuils
- `/utilisateurs/` : gestion des acces

## 9. Comment l'expliquer a l'oral

Version simple que tu peux reprendre :

"J'ai realise une application web de supervision pour une ligne de production. L'utilisateur se connecte avec un role, puis accede a des ecrans de production, maintenance, supervision et gestion des utilisateurs. L'application est developpee en Flask avec des templates Jinja2, et les donnees sont stockees dans MySQL. Le tout est lance avec Docker Compose pour avoir un environnement stable et reproductible."

Points a mettre en avant :

- architecture separee entre application web, base de donnees et outil d'administration
- securisation minimale par authentification et gestion des droits
- organisation du code par routes, services, repositories, templates et fichiers statiques
- base de donnees initialisee automatiquement par scripts SQL
- lancement simplifie avec des scripts `start`, `stop` et `reset`

## 10. Competences informatiques mobilisees

Ce projet montre notamment :

- la comprehension d'une architecture web client / serveur
- l'utilisation d'une base relationnelle MySQL
- la mise en place d'une authentification et de roles
- l'organisation modulaire d'une application Python Flask avec separation routes / services / repositories
- l'utilisation de Docker Compose pour le lancement et le deploiement local

## 11. Point important sur les conteneurs

Au quotidien, il n'est pas necessaire de supprimer et recreer les conteneurs Docker.

- `./stop.sh` met simplement le projet en pause
- `./start.sh` relance rapidement le projet
- `./reset.sh` est reserve a une remise a zero complete

En pratique, ce sont surtout les reconstructions et les reinitialisations completes qui consomment le plus de temps et d'operations, pas un simple `start` ou `stop`.

## 12. Deploiement client via Portainer

Pour le deploiement client, s'appuyer sur les exigences reseau et hebergement de [Projet IT-OT - Doc Technique SACom.pdf](/home/user/Bureau/Projet%20IT-OT%20-%20Doc%20Technique%20SACom.pdf) et sur les attentes fonctionnelles de [LesViviers202601-1-Offre.pdf](/home/user/Bureau/LesViviers202601-1-Offre.pdf).

Synthese utile :

- equipe C : VM Debian 12 en `10.0.1.30`
- acces deploiement : Portainer en `https` sur le port `9443`
- pas d'acces SSH pour le deploiement
- reseau industriel : `172.30.30.X/24`
- flux autorise entre reseau entreprise et industriel : `TCP 4840` pour OPC UA
- le logiciel final doit etre un serveur web en conteneur Docker avec base SQL associee

Etapes conseillees :

1. pousser le code a jour sur GitHub
2. depuis Portainer, creer une stack a partir du fichier `docker-compose.yml`
3. definir au minimum les variables d'environnement suivantes :
   - `MYSQL_ROOT_PASSWORD`
   - `MYSQL_DATABASE`
   - `SESSION_SECRET`
   - `APP_PORT=5005`
4. deployer uniquement `web` et `db`, qui sont les seuls services presents dans la stack finale
5. verifier l'acces web sur `http://10.0.1.30:5005`
6. verifier le dialogue OPC UA vers le WAGO `172.30.30.20` sur le port `4840`
7. verifier la persistance MySQL apres redemarrage des conteneurs

Point de vigilance :

- le test OPC UA actuel valide une connexion anonyme de recette, mais le cahier client final demande une liaison OPC UA securisee avec certificats et une gestion de reconnexion
- avant livraison client, il faut donc distinguer clairement le conteneur de test temporaire du comportement final attendu sur la supervision metier
