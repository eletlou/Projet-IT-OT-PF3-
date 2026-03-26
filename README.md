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
- consultation de la base via Adminer

## 2. Architecture simple

Le projet repose sur 3 briques :

- `web` : application Flask qui affiche les pages et execute la logique metier
- `db` : base de donnees MySQL qui stocke les utilisateurs, commandes, alertes et donnees de supervision
- `adminer` : interface web de consultation de la base de donnees

Le fichier `docker-compose.yml` orchestre ces 3 services.

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

- application Flask : `http://localhost:5000`
- Adminer : `http://localhost:8081`

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
APP_PORT=5000
SESSION_SECRET=change_me_session_secret
```

## 7. Arborescence utile

- `docker-compose.yml` : declaration des services `web`, `db` et `adminer`
- `db/01-schema.sql` : creation de la structure de la base
- `db/02-seed.sql` : insertion des donnees de demonstration
- `app/run.py` : point d'entree Flask
- `app/app/__init__.py` : creation et configuration de l'application
- `app/app/routes/` : routes Flask par module fonctionnel
- `app/app/services/` : logique metier et acces aux donnees
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
- organisation du code par routes, services, templates et fichiers statiques
- base de donnees initialisee automatiquement par scripts SQL
- lancement simplifie avec des scripts `start`, `stop` et `reset`

## 10. Competences informatiques mobilisees

Ce projet montre notamment :

- la comprehension d'une architecture web client / serveur
- l'utilisation d'une base relationnelle MySQL
- la mise en place d'une authentification et de roles
- l'organisation modulaire d'une application Python Flask
- l'utilisation de Docker Compose pour le lancement et le deploiement local

## 11. Point important sur les conteneurs

Au quotidien, il n'est pas necessaire de supprimer et recreer les conteneurs Docker.

- `./stop.sh` met simplement le projet en pause
- `./start.sh` relance rapidement le projet
- `./reset.sh` est reserve a une remise a zero complete

En pratique, ce sont surtout les reconstructions et les reinitialisations completes qui consomment le plus de temps et d'operations, pas un simple `start` ou `stop`.
