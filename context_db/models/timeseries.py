from sqlalchemy import Column, Date, Float, ForeignKey, Index, Integer, String

from .base import Base


class TSEntity(Base):
    __tablename__ = "ts_entities"

    id = Column(String, primary_key=True)        # Wikidata QID or custom identifier
    name = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)  # "country", "region", "union", "bloc"


class TSSource(Base):
    __tablename__ = "ts_sources"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)  # "World Bank", "IMF"
    url = Column(String, nullable=True)


class TSIndicator(Base):
    __tablename__ = "ts_indicators"

    id = Column(String, primary_key=True)         # e.g. "NY.GDP.MKTP.CD"
    name = Column(String, nullable=False)          # "GDP (current US$)"
    unit = Column(String, nullable=True)           # "USD", "tonnes CO2"
    frequency = Column(String, nullable=True)      # "annual", "quarterly", "monthly"
    source_id = Column(Integer, ForeignKey("ts_sources.id"), nullable=False)


class TSDatapoint(Base):
    __tablename__ = "ts_datapoints"

    indicator_id = Column(String, ForeignKey("ts_indicators.id"), primary_key=True)
    entity_id = Column(String, ForeignKey("ts_entities.id"), primary_key=True)
    date = Column(Date, primary_key=True)
    value = Column(Float, nullable=True)

    __table_args__ = (
        Index("ix_ts_datapoints_indicator_entity", "indicator_id", "entity_id"),
        Index("ix_ts_datapoints_date", "date"),
    )
