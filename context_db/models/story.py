from sqlalchemy import ARRAY, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text

from .base import Base


class Story(Base):
    __tablename__ = "stories"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    key_points = Column(ARRAY(Text), nullable=False)
    story_period = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, index=True)
    updated_at = Column(DateTime, nullable=False, index=True)
    parent_story_id = Column(String, ForeignKey("stories.id"))


class ArticleStory(Base):
    __tablename__ = "story_articles"

    article_id = Column(String, ForeignKey("articles.id"), primary_key=True)
    story_id = Column(String, ForeignKey("stories.id"), primary_key=True)
    assigned_at = Column(DateTime, nullable=True)


class ArticleEntityResolved(Base):
    __tablename__ = "article_entities_resolved"

    article_id = Column(String, ForeignKey("articles.id"), primary_key=True)
    qid = Column(String, ForeignKey("kb_entities.qid"), primary_key=True)
    score = Column(Float, nullable=True)


class StoryEntity(Base):
    __tablename__ = "story_entities"

    story_id = Column(String, ForeignKey("stories.id"), primary_key=True)
    qid = Column(String, ForeignKey("kb_entities.qid"), primary_key=True)
    score = Column(Float, nullable=True)
    role = Column(String, nullable=True)
    validated = Column(Boolean, nullable=False, server_default="false")


class StoryEdge(Base):
    __tablename__ = "story_edges"

    from_story_id = Column(String, ForeignKey("stories.id"), primary_key=True)
    to_story_id = Column(String, ForeignKey("stories.id"), primary_key=True)
    relation_type = Column(String, nullable=True)
    score = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=True)


class StoryIndicator(Base):
    __tablename__ = "story_indicators"

    story_id = Column(String, ForeignKey("stories.id"), primary_key=True)
    indicator_id = Column(String, ForeignKey("ts_indicators.id"), primary_key=True)
