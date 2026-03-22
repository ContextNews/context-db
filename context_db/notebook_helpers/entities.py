from __future__ import annotations

import json
import urllib.request

import pandas as pd
from IPython.display import display
from sqlalchemy import text

from context_db.connection import get_session

# ---------------------------------------------------------------------------
# Wikidata helpers
# ---------------------------------------------------------------------------

_WIKIDATA_API = "https://www.wikidata.org/w/api.php"

_LOCATION_TYPE_MAP = {
    "Q515":     "city",
    "Q1549591": "city",
    "Q7930989": "city",
    "Q5119":    "capital",
    "Q3957":    "town",
    "Q532":     "village",
    "Q123705":  "neighbourhood",
    "Q6256":    "country",
    "Q3624078": "country",
    "Q10864048": "region",
    "Q35657":   "region",
    "Q82794":   "region",
}


def _fetch_wikidata(qid: str) -> dict:
    url = (
        f"{_WIKIDATA_API}?action=wbgetentities&ids={qid}"
        "&format=json&languages=en&props=labels|descriptions|aliases|claims"
    )
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())
    entity = data.get("entities", {}).get(qid)
    if not entity or "missing" in entity:
        raise ValueError(f"QID {qid!r} not found on Wikidata")
    return entity


def _string_claim(entity: dict, prop: str) -> str | None:
    for claim in entity.get("claims", {}).get(prop, []):
        if claim.get("rank") != "deprecated":
            val = claim.get("mainsnak", {}).get("datavalue", {}).get("value")
            if isinstance(val, str):
                return val
    return None


def _entity_claim(entity: dict, prop: str) -> str | None:
    for claim in entity.get("claims", {}).get(prop, []):
        if claim.get("rank") != "deprecated":
            val = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
            if isinstance(val, dict) and "id" in val:
                return val["id"]
    return None


def _entity_claims(entity: dict, prop: str) -> list[str]:
    result = []
    for claim in entity.get("claims", {}).get(prop, []):
        if claim.get("rank") != "deprecated":
            val = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
            if isinstance(val, dict) and "id" in val:
                result.append(val["id"])
    return result


def _coordinates(entity: dict) -> tuple[float, float] | tuple[None, None]:
    for claim in entity.get("claims", {}).get("P625", []):
        if claim.get("rank") != "deprecated":
            val = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
            if "latitude" in val:
                return val["latitude"], val["longitude"]
    return None, None


def _iso_code(country_qid: str) -> str | None:
    try:
        return _string_claim(_fetch_wikidata(country_qid), "P297")
    except Exception:
        return None


def _nationality_codes(entity: dict) -> list[str]:
    return [c for qid in _entity_claims(entity, "P27") if (c := _iso_code(qid))]


def _location_type(entity: dict) -> str:
    for qid in _entity_claims(entity, "P31"):
        if qid in _LOCATION_TYPE_MAP:
            return _LOCATION_TYPE_MAP[qid]
    return "place"


def _label(entity: dict) -> str:
    """Get English label, falling back to multilingual label."""
    labels = entity.get("labels", {})
    return (
        labels.get("en", {}).get("value")
        or labels.get("mul", {}).get("value")
        or ""
    )


def _en_aliases(entity: dict) -> list[str]:
    return [a["value"] for a in entity.get("aliases", {}).get("en", [])]

# ---------------------------------------------------------------------------
# Public notebook functions
# ---------------------------------------------------------------------------


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


def _check_exists(qid: str) -> bool:
    """Return True and print a message if the entity is already in the KB."""
    with get_session() as session:
        row = session.execute(
            text("SELECT name FROM kb_entities WHERE qid = :qid"), {"qid": qid}
        ).one_or_none()
    if row:
        print(f"{qid} is already in the KB as {row.name!r}")
        return True
    return False


def add_location(qid: str, aliases: list[str] | None = None) -> None:
    """Fetch location data from Wikidata, show for approval, then insert."""
    if _check_exists(qid):
        return

    print(f"Fetching {qid} from Wikidata...")
    entity = _fetch_wikidata(qid)

    name         = _label(entity)
    if not name:
        print(f"No label found for {qid} on Wikidata. Check the QID and try again.")
        return
    description  = entity.get("descriptions", {}).get("en", {}).get("value")
    loc_type     = _location_type(entity)
    lat, lon     = _coordinates(entity)
    country_qid  = _entity_claim(entity, "P17")
    country_code = _iso_code(country_qid) if country_qid else _string_claim(entity, "P297")
    all_aliases  = sorted({name} | set(_en_aliases(entity)) | set(aliases or []))

    print(f"\n  Name:          {name}")
    print(f"  Description:   {description}")
    print(f"  Location type: {loc_type}")
    print(f"  Country code:  {country_code}")
    print(f"  Coordinates:   {f'{lat}, {lon}' if lat is not None else 'none'}")
    print(f"  Aliases ({len(all_aliases)}):   {', '.join(all_aliases)}")

    if input("\nAdd this entry? [y/N]: ").strip().lower() != "y":
        print("Cancelled.")
        return

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
            """), {"qid": qid, "location_type": loc_type,
                   "country_code": country_code, "lat": lat, "lon": lon})
        else:
            session.execute(text("""
                INSERT INTO kb_locations (qid, location_type, country_code, coordinates)
                VALUES (:qid, :location_type, :country_code, NULL)
            """), {"qid": qid, "location_type": loc_type, "country_code": country_code})

        for alias in all_aliases:
            session.execute(text("""
                INSERT INTO kb_entity_aliases (alias, qid) VALUES (:alias, :qid)
                ON CONFLICT DO NOTHING
            """), {"alias": alias, "qid": qid})

        session.commit()

    print(f"Added {name!r} ({qid}) with {len(all_aliases)} aliases.")


def add_person(qid: str, aliases: list[str] | None = None) -> None:
    """Fetch person data from Wikidata, show for approval, then insert."""
    if _check_exists(qid):
        return

    print(f"Fetching {qid} from Wikidata...")
    entity = _fetch_wikidata(qid)

    name          = _label(entity)
    if not name:
        print(f"No label found for {qid} on Wikidata. Check the QID and try again.")
        return
    description   = entity.get("descriptions", {}).get("en", {}).get("value")
    nationalities = _nationality_codes(entity)
    all_aliases   = sorted({name} | set(_en_aliases(entity)) | set(aliases or []))

    print(f"\n  Name:          {name}")
    print(f"  Description:   {description}")
    print(f"  Nationalities: {', '.join(nationalities) or 'none'}")
    print(f"  Aliases ({len(all_aliases)}):   {', '.join(all_aliases)}")

    if input("\nAdd this entry? [y/N]: ").strip().lower() != "y":
        print("Cancelled.")
        return

    with get_session() as session:
        session.execute(text("""
            INSERT INTO kb_entities (qid, entity_type, name, description)
            VALUES (:qid, 'person', :name, :description)
        """), {"qid": qid, "name": name, "description": description})

        session.execute(text("""
            INSERT INTO kb_persons (qid, nationalities)
            VALUES (:qid, :nationalities)
        """), {"qid": qid, "nationalities": nationalities})

        for alias in all_aliases:
            session.execute(text("""
                INSERT INTO kb_entity_aliases (alias, qid) VALUES (:alias, :qid)
                ON CONFLICT DO NOTHING
            """), {"alias": alias, "qid": qid})

        session.commit()

    print(f"Added {name!r} ({qid}) with {len(all_aliases)} aliases.")


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
