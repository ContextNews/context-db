from geoalchemy2 import Geography
from sqlalchemy import ARRAY, Boolean, Column, DateTime, ForeignKey, String, Text, func

from .base import Base


class KBEntity(Base):
    __tablename__ = "kb_entities"

    qid = Column(String, primary_key=True)
    entity_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    date_added = Column(DateTime, nullable=False, server_default=func.now())
    validated = Column(Boolean, nullable=False, server_default="false")


class KBEntityAlias(Base):
    __tablename__ = "kb_entity_aliases"

    alias = Column(String, primary_key=True)
    qid = Column(String, ForeignKey("kb_entities.qid"), primary_key=True)


class KBLocation(Base):
    __tablename__ = "kb_locations"

    qid = Column(String, ForeignKey("kb_entities.qid"), primary_key=True)
    location_type = Column(String, nullable=False)
    country_code = Column(String, nullable=True)
    coordinates = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)


class KBPerson(Base):
    __tablename__ = "kb_persons"

    qid = Column(String, ForeignKey("kb_entities.qid"), primary_key=True)
    nationalities = Column(ARRAY(String), nullable=True)
