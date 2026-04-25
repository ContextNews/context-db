from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint

from .base import Base


class TgChannel(Base):
    __tablename__ = "tg_channels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    channel_id = Column(BigInteger, unique=True)  # Telegram's internal channel ID
    title = Column(String)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False)


class TgPost(Base):
    __tablename__ = "tg_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(Integer, ForeignKey("tg_channels.id"), nullable=False, index=True)
    message_id = Column(Integer, nullable=False)
    text = Column(Text)
    date = Column(DateTime, nullable=False, index=True)
    edit_date = Column(DateTime)
    has_media = Column(Boolean, nullable=False, default=False)
    media_type = Column(String)
    collected_at = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("channel_id", "message_id", name="uq_tg_channel_message"),
    )


class TgCursor(Base):
    __tablename__ = "tg_cursors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(Integer, ForeignKey("tg_channels.id"), nullable=False, unique=True)
    last_message_id = Column(Integer, nullable=False, default=0)
    backfill_complete = Column(Boolean, nullable=False, default=False)
    updated_at = Column(DateTime)


class TgStructuredPost(Base):
    __tablename__ = "tg_structured_posts"

    post_id       = Column(Integer, ForeignKey("tg_posts.id"), primary_key=True)
    latitude      = Column(Float, nullable=True)
    longitude     = Column(Float, nullable=True)
    location_name = Column(String, nullable=True)
    label         = Column(Text, nullable=False)
    priority      = Column(Integer, nullable=False)
    story_id      = Column(String, ForeignKey("stories.id"), nullable=True)


class TgPostNoise(Base):
    __tablename__ = "tg_post_noise"

    post_id = Column(Integer, ForeignKey("tg_posts.id"), primary_key=True)
