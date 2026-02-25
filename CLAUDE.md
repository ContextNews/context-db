# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repo contains shared data contracts and database migrations for a news/article processing pipeline. It is intended to be installed as a Python package by other services.

## Setup

```bash
cp .env.example .env   # then set DATABASE_URL
poetry install
```

## Installing in consumer services

Other services depend on this package. Add it to their `pyproject.toml` as a path or git dependency:

```toml
context-data-schema = { path = "../context-data-schema", develop = true }
# or via git:
context-data-schema = { git = "https://github.com/org/context-data-schema.git" }
```

Then import models and the session helper:

```python
from rds_postgres.models import Article, Story, ...
from rds_postgres.connection import get_session
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

## ERD generation

The dev dependency `eralchemy2` can regenerate the entity-relationship diagram:

```bash
poetry run eralchemy2 -i postgresql://... -o erd.png
```

## Architecture

### Package layout

- `rds_postgres/models.py` — single file containing all SQLAlchemy ORM models (the source of truth for the schema)
- `rds_postgres/connection.py` — engine and `get_session()` context manager used by consumers
- `rds_postgres/alembic/` — Alembic migration environment; `env.py` wires `Base.metadata` into Alembic and filters out PostGIS/extension objects from autogenerate
- `common/article_contract.json` — JSON Schema contract for the article message format exchanged between services
- `plans/v2_schema_rework.md` — planned major schema refactor (not yet implemented); see below

### Key design points

- **pgvector**: `ArticleEmbedding.embedding` uses `Vector(None)` (dimensionless) so the same column works for any embedding model dimension. The `render_item` hook in `alembic/env.py` injects the `import pgvector` statement and returns `False` to defer to default rendering; without this hook, autogenerate drops pgvector columns.
- **PostGIS**: `Location.coordinates` uses `Geography(geometry_type="POINT", srid=4326)`. The `include_object` hook in `alembic/env.py` suppresses PostGIS system tables from autogenerate.
- **SSL**: `connection.py` enforces `sslmode=require` on the engine — local tunnels must present a valid SSL certificate.
- **Composite PKs**: many junction/association tables use composite primary keys rather than surrogate IDs (e.g. `ArticleEntity`, `ArticleLocation`, `StoryLocation`, `PersonAlias`).
- **Self-referencing**: `Story.parent_story_id` is a self-FK; `StoryStory` is a separate many-to-many table for peer relationships between stories.
- **Known schema gap**: `StoryTopic.topic` is a plain `String` column with no FK to `topics.topic`, unlike `ArticleTopic.topic` which does have the FK. This is a known inconsistency in the current schema.

### Article contract (`common/article_contract.json`)

Required fields: `id`, `title`, `url`, `ingested_at`. Optional: `headline`, `text`, `embedding` (array of numbers), `embedding_model`. `additionalProperties` is false — add new fields to the JSON Schema before using them.

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

### Planned v2 schema rework (`plans/v2_schema_rework.md`)

A significant refactor is planned but not yet implemented. Key changes:

- Split `models.py` into domain files under `rds_postgres/models/`
- Unify `locations` + `persons` into a single `kb_entities` / `kb_entity_aliases` hierarchy with `kb_locations` and `kb_persons` as specialisation tables (Wikidata QID as PK throughout)
- Separate raw NLP entity mentions (`article_entity_mentions`) from resolved KB links (`article_entities_resolved`)
- Replace `story_stories` (undirected) with `story_edges` (directional + typed)
- Replace `article_clusters` / `article_cluster_articles` with a `cluster_label` column on `story_articles`
- Add `embedding_kind` and `chunk_index` to `article_embeddings` PK

When implementing v2, follow the incremental migration path in the plan file rather than a big-bang replacement.
