from __future__ import annotations

import pandas as pd
from IPython.display import display
from sqlalchemy import text

from context_db.connection import get_session


def unresolved_entities(ner_type: str = "ALL") -> pd.DataFrame:
    """Return extracted entities with no KB match, ordered by frequency."""
    ner_filter = "AND aem.ner_type = :ner_type" if ner_type != "ALL" else ""
    params = {"ner_type": ner_type} if ner_type != "ALL" else {}

    with get_session() as session:
        rows = session.execute(text(f"""
            SELECT
                aem.mention_text,
                aem.ner_type,
                SUM(aem.mention_count) AS total_count
            FROM article_entity_mentions aem
            LEFT JOIN kb_entity_aliases kea
                ON UPPER(aem.mention_text) = UPPER(kea.alias)
            WHERE kea.alias IS NULL
            {ner_filter}
            GROUP BY aem.mention_text, aem.ner_type
            ORDER BY total_count DESC
        """), params).all()

    return pd.DataFrame(rows, columns=["mention_text", "ner_type", "total_count"])


def lookup_entity(alias: str) -> None:
    """Look up an entity by alias. Falls back to partial match if no exact match."""
    with get_session() as session:
        row = session.execute(text("""
            SELECT ke.qid, ke.entity_type, ke.name, ke.description
            FROM kb_entity_aliases kea
            JOIN kb_entities ke ON ke.qid = kea.qid
            WHERE UPPER(kea.alias) = UPPER(:name)
            LIMIT 1
        """), {"name": alias}).one_or_none()

        if not row:
            matches = session.execute(text("""
                SELECT DISTINCT ke.qid, ke.entity_type, ke.name, ke.description
                FROM kb_entity_aliases kea
                JOIN kb_entities ke ON ke.qid = kea.qid
                WHERE kea.alias ILIKE :pattern
                ORDER BY ke.name
                LIMIT 20
            """), {"pattern": f"%{alias}%"}).all()

            if not matches:
                print(f"No entity found for: {alias!r}")
                return

            if len(matches) == 1:
                row = matches[0]
            else:
                print(f"No exact match. Partial matches for {alias!r}:")
                display(pd.DataFrame(matches, columns=["qid", "entity_type", "name", "description"]))
                return

        aliases = session.execute(text("""
            SELECT alias FROM kb_entity_aliases
            WHERE qid = :qid
            ORDER BY alias
        """), {"qid": row.qid}).scalars().all()

    print(f"QID:         {row.qid}")
    print(f"Type:        {row.entity_type}")
    print(f"Name:        {row.name}")
    if row.description:
        print(f"Description: {row.description}")
    print(f"\nAliases ({len(aliases)}):")
    for a in aliases:
        print(f"  {a}")


def add_location(
    qid: str,
    name: str,
    description: str | None = None,
    location_type: str = "city",
    country_code: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    aliases: list[str] | None = None,
) -> None:
    """Insert a location entity into kb_entities, kb_locations, and kb_entity_aliases."""
    all_aliases = [name] + [a for a in (aliases or []) if a != name]

    with get_session() as session:
        session.execute(text("""
            INSERT INTO kb_entities (qid, entity_type, name, description)
            VALUES (:qid, 'location', :name, :description)
        """), {"qid": qid, "name": name, "description": description})

        if lat is not None and lon is not None:
            session.execute(text("""
                INSERT INTO kb_locations (qid, location_type, country_code, coordinates)
                VALUES (:qid, :location_type, :country_code,
                        ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography)
            """), {"qid": qid, "location_type": location_type,
                   "country_code": country_code, "lat": lat, "lon": lon})
        else:
            session.execute(text("""
                INSERT INTO kb_locations (qid, location_type, country_code, coordinates)
                VALUES (:qid, :location_type, :country_code, NULL)
            """), {"qid": qid, "location_type": location_type, "country_code": country_code})

        for alias in all_aliases:
            session.execute(text("""
                INSERT INTO kb_entity_aliases (alias, qid) VALUES (:alias, :qid)
                ON CONFLICT DO NOTHING
            """), {"alias": alias, "qid": qid})

        session.commit()

    print(f"Added location {name!r} ({qid}) with {len(all_aliases)} aliases.")


def add_person(
    qid: str,
    name: str,
    description: str | None = None,
    nationalities: list[str] | None = None,
    aliases: list[str] | None = None,
) -> None:
    """Insert a person entity into kb_entities, kb_persons, and kb_entity_aliases."""
    all_aliases = [name] + [a for a in (aliases or []) if a != name]

    with get_session() as session:
        session.execute(text("""
            INSERT INTO kb_entities (qid, entity_type, name, description)
            VALUES (:qid, 'person', :name, :description)
        """), {"qid": qid, "name": name, "description": description})

        session.execute(text("""
            INSERT INTO kb_persons (qid, nationalities)
            VALUES (:qid, :nationalities)
        """), {"qid": qid, "nationalities": nationalities or []})

        for alias in all_aliases:
            session.execute(text("""
                INSERT INTO kb_entity_aliases (alias, qid) VALUES (:alias, :qid)
                ON CONFLICT DO NOTHING
            """), {"alias": alias, "qid": qid})

        session.commit()

    print(f"Added person {name!r} ({qid}) with {len(all_aliases)} aliases.")


def add_alias(qid: str, alias: str) -> None:
    """Add an alias to an existing entity."""
    with get_session() as session:
        entity = session.execute(text("""
            SELECT name FROM kb_entities WHERE qid = :qid
        """), {"qid": qid}).one_or_none()

        if not entity:
            print(f"No entity found with QID {qid!r}")
            return

        existing = session.execute(text("""
            SELECT 1 FROM kb_entity_aliases WHERE alias = :alias AND qid = :qid
        """), {"alias": alias, "qid": qid}).one_or_none()

        if existing:
            print(f"Alias {alias!r} already exists for {entity.name} ({qid})")
            return

        session.execute(text("""
            INSERT INTO kb_entity_aliases (alias, qid) VALUES (:alias, :qid)
        """), {"alias": alias, "qid": qid})
        session.commit()

    print(f"Added alias {alias!r} to {entity.name} ({qid})")
