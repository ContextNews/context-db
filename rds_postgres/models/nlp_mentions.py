from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text

from .base import Base


class ArticleEmbedding(Base):
    __tablename__ = "article_embeddings"

    article_id = Column(String, ForeignKey("articles.id"), primary_key=True)
    embedding_model = Column(String, primary_key=True)
    embedding = Column(Vector(None), nullable=False)
    embedded_text = Column(Text)
    created_at = Column(DateTime, nullable=True)


class ArticleEntityMention(Base):
    __tablename__ = "article_entity_mentions"

    article_id = Column(String, ForeignKey("articles.id"), primary_key=True)
    ner_type = Column(String, primary_key=True)
    mention_text = Column(String, primary_key=True)
    mention_count = Column(Integer, nullable=False)
    in_title = Column(Boolean, nullable=False)
