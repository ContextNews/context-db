# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repo contains shared data contracts and database migrations for a news/article processing pipeline. It is intended to be installed as a Python package by other services.

## Setup

```bash
cp .env.example .env   # then set DATABASE_URL
poetry install
```

## Migrations

All migration commands require `DATABASE_URL` to be set (picked up from `.env` or environment).

```bash
# Generate a new migration after editing rds_postgres/models.py
poetry run alembic revision --autogenerate -m "description of changes"

# Apply all pending migrations
poetry run alembic upgrade head

# Downgrade one step
poetry run alembic downgrade -1
```

Always review the auto-generated file in `rds_postgres/alembic/versions/` before applying — autogenerate may miss custom types or index details.

## Architecture

### Package layout

- `rds_postgres/models.py` — single file containing all SQLAlchemy ORM models (the source of truth for the schema)
- `rds_postgres/connection.py` — engine and `get_session()` context manager used by consumers
- `rds_postgres/alembic/` — Alembic migration environment; `env.py` wires `Base.metadata` into Alembic and filters out PostGIS/extension objects from autogenerate
- `common/article_contract.json` — JSON Schema contract for the article message format exchanged between services

### Key design points

- **pgvector**: `ArticleEmbedding.embedding` uses `Vector(None)` (dimensionless) so the same column works for any embedding model dimension. The `render_item` hook in `alembic/env.py` ensures pgvector types survive autogenerate.
- **PostGIS**: `Location.coordinates` uses `Geography(geometry_type="POINT", srid=4326)`. The `include_object` hook in `alembic/env.py` suppresses PostGIS system tables from autogenerate.
- **SSL**: `connection.py` enforces `sslmode=require` on the engine — local tunnels must present a valid SSL certificate.
- **Composite PKs**: many junction/association tables use composite primary keys rather than surrogate IDs (e.g. `ArticleEntity`, `ArticleLocation`, `StoryLocation`, `PersonAlias`).
- **Self-referencing**: `Story.parent_story_id` is a self-FK; `StoryStory` is a separate many-to-many table for peer relationships between stories.

### Domain model summary

| Table | Purpose |
|---|---|
| `articles` | Raw ingested news articles |
| `article_embeddings` | Vector embeddings per article × model |
| `article_clusters` / `article_cluster_articles` | Grouping articles into clusters by period |
| `article_topics` / `topics` | Topic tags on articles |
| `article_entities` / `entities` | Named entities extracted from articles |
| `stories` | AI-generated story summaries (hierarchical via `parent_story_id`) |
| `story_stories` | Peer relationships between stories |
| `story_topics` | Topic tags on stories |
| `article_stories` | Many-to-many: articles ↔ stories |
| `locations` / `location_aliases` | Wikidata-backed geo locations with aliases |
| `article_locations` / `story_locations` | Geo tags on articles and stories |
| `persons` / `person_aliases` | Wikidata-backed persons with aliases |
| `article_persons` / `story_persons` | Person tags on articles and stories |
