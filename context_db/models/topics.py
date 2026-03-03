from sqlalchemy import Column, ForeignKey, String

from .base import Base


class Topic(Base):
    __tablename__ = "topics"

    topic = Column(String, primary_key=True)


class ArticleTopic(Base):
    __tablename__ = "article_topics"

    article_id = Column(String, ForeignKey("articles.id"), primary_key=True)
    topic = Column(String, ForeignKey("topics.topic"), primary_key=True)


class StoryTopic(Base):
    __tablename__ = "story_topics"

    story_id = Column(String, ForeignKey("stories.id"), primary_key=True)
    topic = Column(String, ForeignKey("topics.topic"), primary_key=True)
