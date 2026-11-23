# MS5 — Exécution

Service FastAPI qui exécute le code soumis (Python ou Java) contre les tests d'un problème et calcule le pourcentage de réussite. Port **8085**, base MySQL `execution_db`, enregistré dans Eureka. Sans Docker : tout se lance en local.

## Flux

1. MS4 appelle `POST /api/executions` avec `{"soumissionId": "..."}` → réponse **202** immédiate.
2. En arrière-plan : lecture de la soumission (MS4) et des tests (MS3), exécution, enregistrement du résultat.
3. MS4 reçoit le statut `EXÉCUTÉE` (ou `ERREUR`), MS6 reçoit le score. Si MS6 est injoignable, `score_transmis` reste à `false` et une tâche planifiée renvoie le score.
4. Le participant lit le résultat avec `GET /api/executions/{soumissionId}`.

## Installation

Prérequis : Python 3.11, MySQL 8.

```bash
cd backend/ms5-execution
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # puis adapter DATABASE_URL, MS3_URL, MS4_URL, MS6_URL
```

## Base de données

```bash
mysql -u root -p -e "CREATE DATABASE execution_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
alembic upgrade head
```

## Démarrage

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8085 --reload
```

- Swagger : http://localhost:8085/docs
- Santé : http://localhost:8085/health

## Configuration

Variables d'environnement (voir `.env.example`). Priorité : environnement > `.env` > Config Server (`CONFIG_SERVER_URL`, optionnel) > valeurs par défaut. Eureka se désactive avec `EUREKA_ENABLED=false`.

## Tests

```bash
pytest
```

Les tests utilisent SQLite en mémoire et de faux clients MS3/MS4/MS6 : ni MySQL ni les autres services ne sont nécessaires.

## État

- Fait : API, modèle de données, migration, clients résilients, Eureka, renvoi des scores.
- À faire : l'exécuteur de code (`app/executor/`). Tant qu'il n'est pas implémenté, toute exécution passe en `ERREUR`.
- À faire : `GET /api/executions/meilleures?problemeId=` et le contrôle d'accès 403 (propriétaire de la soumission).
