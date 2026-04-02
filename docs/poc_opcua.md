# POC OPC UA

## Objectif

Valider de maniere simple la faisabilite d'une communication OPC UA entre l'application web et l'automate WAGO.

Le POC doit montrer deux choses :

- le serveur web sait se connecter a l'automate en OPC UA et lire quelques variables
- le navigateur peut declencher ce test et recuperer un resultat lisible depuis la page web

## Perimetre

- nouvelle page dediee : `/poc-opcua`
- nouvel endpoint API lecture seule : `/api/poc-opcua/test`
- reutilisation de la logique existante dans `app/app/services/opcua_test_service.py`
- lecture de 4 variables maximum choisies a partir du fichier local `app/app/data/opcua_test_nodes.txt`
- saisie manuelle simple de l'endpoint, de l'utilisateur et du mot de passe sur la page
- aucun ecriture OPC UA
- aucune ecriture en base de donnees
- aucun WebSocket
- aucun polling automatique

## Procedure de test

1. Demarrer l'application avec `./start.sh`
2. Ouvrir `http://localhost:5005`
3. Se connecter avec un compte ayant le droit `opcua_test`, par exemple `admin / admin1234`
4. Ouvrir la page `/poc-opcua`
5. Verifier ou ajuster l'endpoint, l'utilisateur et le mot de passe
6. Cliquer sur `Lancer le test OPC UA`
7. Lire le JSON retourne a l'ecran

## Resultat attendu

- un statut global `SUCCES` ou `ECHEC`
- un horodatage
- un temps de reponse en millisecondes
- l'endpoint OPC UA utilise
- l'etat de session ouverte
- le nombre de variables lues
- la valeur de quelques variables OPC UA
- un message d'erreur brut si la connexion ou la lecture echoue
- un JSON brut et lisible affiche directement dans la page

## Limites du POC

- le POC est volontairement manuel et minimal
- il ne remplace pas la page de test plus complete `/supervision/opcua-test`
- il ne gere pas l'ecriture, la surveillance continue ni la reconnexion automatique
- il depend des NodeIds presents dans `app/app/data/opcua_test_nodes.txt`
- si le reseau industriel ou le serveur OPC UA n'est pas accessible, le test remonte simplement l'erreur
