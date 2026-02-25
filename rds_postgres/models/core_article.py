from sqlalchemy import Column, DateTime, ForeignKey, String, Text

from .base import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(String, primary_key=True)
    source = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    url = Column(String, nullable=False, unique=True, index=True)
    published_at = Column(DateTime, nullable=False, index=True)
    ingested_at = Column(DateTime, nullable=False, index=True)
    text = Column(Text)


class ArticleCluster(Base):
    __tablename__ = "article_clusters"

    article_cluster_id = Column(String, primary_key=True)
    cluster_period = Column(DateTime, nullable=False, index=True)


class ArticleClusterArticle(Base):
    __tablename__ = "article_cluster_articles"

    article_cluster_id = Column(
        String, ForeignKey("article_clusters.article_cluster_id"), primary_key=True
    )
    article_id = Column(String, ForeignKey("articles.id"), primary_key=True)
