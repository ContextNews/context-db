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
from context_db.models import Article, Story, ...
from context_db.connection import get_session
```

## Migrations

All migration commands require `DATABASE_URL` to be set (picked up from `.env` or environment).

```bash
# Generate a new migration after editing model files
poetry run alembic revision --autogenerate -m "description of changes"

# Apply all pending migrations
poetry run alembic upgrade head

# Downgrade one step
poetry run alembic downgrade -1
```

Always review the auto-generated file in `context_db/alembic/versions/` before applying — autogenerate may miss custom types or index details.

## ERD generation

The dev dependency `eralchemy2` can regenerate the entity-relationship diagram from the ORM metadata (no live DB needed):

```bash
poetry run python scripts/generate_erd.py
```

## Architecture

### Package layout

- `context_db/models/` — domain-split SQLAlchemy ORM models (source of truth for the schema):
  - `base.py` — `Base = declarative_base()`
  - `core_article.py` — `Article`, `ArticleCluster`, `ArticleClusterArticle`
  - `nlp_mentions.py` — `ArticleEmbedding`, `ArticleEntityMention`
  - `topics.py` — `Topic`, `ArticleTopic`, `StoryTopic`
  - `kb_entities.py` — `KBEntity`, `KBEntityAlias`, `KBLocation`, `KBPerson`
  - `story.py` — `Story`, `ArticleStory`, `ArticleEntityResolved`, `StoryEntity`, `StoryEdge`
  - `__init__.py` — re-exports all public model classes
- `context_db/connection.py` — engine and `get_session()` context manager used by consumers
- `context_db/alembic/` — Alembic migration environment; `env.py` wires `Base.metadata` into Alembic and filters out PostGIS/extension objects from autogenerate
- `common/article_contract.json` — JSON Schema contract for the article message format exchanged between services

### Key design points

- **pgvector**: `ArticleEmbedding.embedding` uses `Vector(None)` (dimensionless) so the same column works for any embedding model dimension. The `render_item` hook in `alembic/env.py` injects the `import pgvector` statement and returns `False` to defer to default rendering; without this hook, autogenerate drops pgvector columns.
- **PostGIS**: `KBLocation.coordinates` uses `Geography(geometry_type="POINT", srid=4326)`. The `include_object` hook in `alembic/env.py` suppresses PostGIS system tables from autogenerate.
- **SSL**: `connection.py` enforces `sslmode=require` on the engine — local tunnels must present a valid SSL certificate.
- **Composite PKs**: junction/association tables use composite primary keys rather than surrogate IDs (e.g. `ArticleEntityResolved`, `StoryEntity`, `KBEntityAlias`).
- **Self-referencing**: `Story.parent_story_id` is a self-FK for story hierarchy. `StoryEdge` is a separate directional table for typed peer relationships between stories (`from_story_id` → `to_story_id`).
- **KB entity hierarchy**: `KBEntity` is the base table (Wikidata QID as PK); `KBLocation` and `KBPerson` are specialisation tables joined on `qid`. Filter on `entity_type` to distinguish `location`, `person`, etc. Do not query `kb_locations` / `kb_persons` directly for entity metadata — always join to `kb_entities`.
- **NLP mentions vs resolved entities**: `ArticleEntityMention` stores raw NLP surface forms (not KB-resolved). `ArticleEntityResolved` and `StoryEntity` store canonical KB links (via `qid`). These are distinct pipeline stages.
- **Rename safety**: Alembic autogenerate cannot detect renames — it emits drop + recreate and loses data. Always hand-write migrations for column or table renames (see `plans/v2_schema_rework.md` for the pattern).

### Article contract (`common/article_contract.json`)

Required fields: `id`, `title`, `url`, `ingested_at`. Optional: `headline`, `text`, `embedding` (array of numbers), `embedding_model`. `additionalProperties` is false — add new fields to the JSON Schema before using them.

### Domain model summary

| Table | Purpose |
|---|---|
| `articles` | Raw ingested news articles |
| `article_embeddings` | Vector embeddings per article × model (`article_id`, `embedding_model` composite PK) |
| `article_clusters` / `article_cluster_articles` | Grouping articles into clusters by period |
| `article_topics` / `topics` | Topic tags on articles (FK to `topics.topic`) |
| `story_topics` | Topic tags on stories (FK to `topics.topic`) |
| `article_entity_mentions` | Raw NLP surface-form entity mentions per article (pre-resolution) |
| `article_entities_resolved` | Canonical KB entities linked to articles (post-resolution, via `qid`) |
| `stories` | AI-generated story summaries (hierarchical via `parent_story_id`) |
| `story_articles` | Many-to-many: articles ↔ stories (with `assigned_at`) |
| `story_entities` | Canonical KB entities linked to stories (via `qid`, with optional `role`) |
| `story_edges` | Directional typed relationships between stories (`from_story_id` → `to_story_id`) |
| `kb_entities` | Canonical Wikidata-backed entities (QID PK, `entity_type` discriminator) |
| `kb_entity_aliases` | Name aliases for KB entities |
| `kb_locations` | Geo-specific fields for `entity_type='location'` entities |
| `kb_persons` | Person-specific fields for `entity_type='person'` entities |
