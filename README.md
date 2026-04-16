# RSVP Mariage V0

Une première version légère d'un site RSVP de mariage, avec :

- une page publique pour confirmer sa présence ;
- une page de remerciement après validation du RSVP ;
- un tableau de bord privé protégé par mot de passe ;
- une base de données SQLite locale pour centraliser les RSVP.

## Démarrer

```bash
python3 app.py
```

Le site sera disponible sur `http://127.0.0.1:8000`.

## Routes utiles

- `/` : formulaire RSVP
- `/admin/login` : accès admin
- `/dashboard` : suivi des réponses
- `/api/event` : configuration de l'événement
- `/api/rsvp` : enregistrement d'une réponse
- `/api/rsvps` : liste + statistiques

## Accès privé au suivi

Le suivi n'est plus accessible depuis la page publique.

Au premier démarrage, l'application crée automatiquement un mot de passe admin local dans :

```text
data/admin_password.txt
```

Ce fichier est ignoré par Git. Vous pouvez aussi définir votre propre mot de passe avec la variable d'environnement :

```bash
RSVP_ADMIN_PASSWORD="votre-mot-de-passe" python3 app.py
```

## Personnalisation rapide

Dans `app.py`, modifiez la constante `EVENT_CONFIG` pour remplacer :

- les prénoms des mariés ;
- la date ;
- le lieu ;
- la date limite de réponse ;
- le message d'introduction.

## Base de données

Les réponses sont enregistrées dans :

```text
data/rsvp.sqlite3
```

La V0 repose sur un identifiant unique par e-mail. C'est pratique pour démarrer, puis on pourra ensuite passer à un modèle plus précis :

- code d'invitation par foyer ;
- table `guests` séparée ;
- espace admin protégé ;
- export CSV ;
- relances automatiques.
