# Context Data Schemas

This repo contains shared data contracts and database migrations.

## Schema

![ERD](erd.png)

## Notebooks

Exploratory notebooks for querying and managing the database, runnable on Google Colab.

| Notebook | Description |
|---|---|
| [Entities](https://colab.research.google.com/github/ContextNews/context-db/blob/main/notebooks/entities.ipynb) | Browse unresolved entities, look up by alias, add locations/persons/aliases |

> **Before running:** add `DATABASE_URL` to your Colab secrets (key icon in the left sidebar).

## Setup

1. Copy environment file and update values:
   ```bash
   cp .env.example .env
   ```
2. Install dependencies:
   ```bash
   poetry install
   ```

## Migrations

Ensure `DATABASE_URL` is set (local `.env` or environment).

### Generate a migration

After modifying models in `context_db/models/`, generate a migration:

```bash
poetry run alembic revision --autogenerate -m "description of changes"
```

Review the generated file in `context_db/alembic/versions/` to ensure the changes are correct.

### Apply migrations

```bash
poetry run alembic upgrade head
```

## Local tunnel (example)

If your database is only reachable via a tunnel, establish it first, then run migrations.
