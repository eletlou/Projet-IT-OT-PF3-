# LES VIVIERS DE NOIRMOUTIER

Application web de supervision en `Flask + Jinja2 + MySQL`, conteneurisee avec `Docker Compose`.

## 1. Ce que fait maintenant l'application

- authentification avec sessions Flask
- gestion des roles : `Administrateur`, `Operateur`, `Responsable`, `Integrateur`
- vue d'ensemble de la ligne
- historique des commandes et des recettes
- suivi maintenance et planification preventive
- supervision technique : alertes, seuils, donnees automate, variables OPCUA
- gestion des utilisateurs par l'administrateur
- interface Adminer pour verifier la base

## 2. Comptes de demonstration

- `admin / admin1234`
- `operateur / operateur1234`
- `responsable / responsable1234`
- `integrateur / integrateur1234`

## 3. Variables d'environnement

Le projet contient deja un fichier `.env` local pour le developpement.

Le modele reste disponible dans `.env.example` :

```env
MYSQL_ROOT_PASSWORD=uimm
MYSQL_DATABASE=les_viviers_de_noirmoutier
APP_PORT=5000
SESSION_SECRET=change_me_session_secret
```

## 4. Commandes terminal

### Lancer le projet simplement

```bash
./start.sh
```

Cette commande suffit pour le lancement courant. Il n'est pas necessaire d'arreter Docker avant de relancer l'application.

### Lancer le projet manuellement

```bash
docker compose up --build -d
```

### Arreter le projet

```bash
./stop.sh
```

### Repartir proprement avec la nouvelle base de supervision

```bash
./reset.sh
```

## 5. Acces navigateur

- Application Flask : `http://localhost:5000`
- Adminer : `http://localhost:8081`

## 6. Connexion Adminer

- Systeme : `MySQL`
- Serveur : `db`
- Utilisateur : `root`
- Mot de passe : `uimm`
- Base : `les_viviers_de_noirmoutier`

## 7. Fichiers principaux

- `docker-compose.yml` : lance Flask, MySQL et Adminer
- `db/01-schema.sql` : cree les tables metier de supervision
- `db/02-seed.sql` : insere les donnees de demonstration
- `app/app/routes/` : pages Flask
- `app/app/services/` : requetes SQL et logique metier
- `app/app/templates/` : pages HTML Jinja2
- `app/app/static/css/style.css` : charte visuelle
- `app/app/static/js/app.js` : menu mobile

## 8. Pages disponibles

- `/login` : connexion
- `/dashboard/` : vue d'ensemble
- `/commandes/` : suivi production
- `/maintenance/` : interventions et plans preventifs
- `/supervision/` : alertes, automate, OPCUA et seuils
- `/utilisateurs/` : gestion des acces

## 9. Point technique important

Si tu avais deja lance une ancienne version du projet, il faut faire `docker compose down -v` pour supprimer l'ancien volume MySQL. Sinon Docker conserve l'ancienne base et les nouveaux scripts SQL ne sont pas reappliques.
