from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
import pgvector.sqlalchemy
from sqlalchemy import engine_from_config, pool

from context_db.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

load_dotenv()


def get_database_url() -> str:
    return os.environ.get(
        "DATABASE_URL", "postgresql://user:pass@localhost:5432/dbname"
    )


def include_object(object_, name, type_, reflected, compare_to):  # noqa: ANN001
    if type_ == "extension":
        return False
    if type_ == "table" and name in {
        "spatial_ref_sys",
        "geometry_columns",
        "geography_columns",
        "raster_columns",
        "raster_overviews",
    }:
        return False
    return True


def render_item(type_, obj, autogen_context):  # noqa: ANN001
    if type_ == "type" and obj.__module__.startswith("pgvector"):
        autogen_context.imports.add("import pgvector")
    return False


def run_migrations_offline() -> None:
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=Base.metadata,
        include_object=include_object,
        render_item=render_item,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
            include_object=include_object,
            render_item=render_item,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
