# RSVP Mariage V0

Une première version légère d'un site RSVP de mariage, avec :

- une page publique pour confirmer sa présence ;
- un petit tableau de bord pour suivre les réponses ;
- une base de données SQLite locale pour centraliser les RSVP.

## Démarrer

```bash
python3 app.py
```

Le site sera disponible sur `http://127.0.0.1:8000`.

## Routes utiles

- `/` : formulaire RSVP
- `/dashboard` : suivi des réponses
- `/api/event` : configuration de l'événement
- `/api/rsvp` : enregistrement d'une réponse
- `/api/rsvps` : liste + statistiques

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
