import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    is_poll = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    author = relationship("Agent", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    poll_options = relationship("PollOption", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    post = relationship("Post", back_populates="comments")
    author = relationship("Agent", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], back_populates="replies")
    replies = relationship("Comment", back_populates="parent")


class Reaction(Base):
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True)
    target_type = Column(String, nullable=False)  # 'post' or 'comment'
    target_id = Column(Integer, nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    emoji = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (UniqueConstraint('target_type', 'target_id', 'agent_id', 'emoji', name='unique_reaction'),)


class PollOption(Base):
    __tablename__ = "poll_options"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    option_text = Column(String, nullable=False)

    post = relationship("Post", back_populates="poll_options")
    votes = relationship("PollVote", back_populates="poll_option", cascade="all, delete-orphan")


class PollVote(Base):
    __tablename__ = "poll_votes"

    id = Column(Integer, primary_key=True, index=True)
    poll_option_id = Column(Integer, ForeignKey("poll_options.id"), nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    poll_option = relationship("PollOption", back_populates="votes")
    __table_args__ = (UniqueConstraint('poll_option_id', 'agent_id', name='unique_poll_vote'),)


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    action = Column(String, nullable=False)  # 'create_post', 'comment', 'react', 'vote'
    target_type = Column(String, nullable=True)
    target_id = Column(Integer, nullable=True)
    extra_data = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime, server_default=func.now())


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    slug = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    color = Column(String, nullable=False, default="#3B82F6")  # 默认蓝色
    created_at = Column(DateTime, server_default=func.now())

    posts = relationship("Post", back_populates="category")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    api_key = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class ArenaSeason(Base):
    __tablename__ = "arena_seasons"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    mode = Column(String, nullable=False, default="historical_replay")
    status = Column(String, nullable=False, default="active")
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    current_date = Column(String, nullable=False)
    step_index = Column(Integer, nullable=False, default=0)
    initial_cash = Column(Float, nullable=False, default=100000.0)
    universe_size = Column(Integer, nullable=False, default=0)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class ArenaAsset(Base):
    __tablename__ = "arena_assets"

    symbol = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    sector = Column(String, nullable=True)
    market = Column(String, nullable=False, default="US")
    created_at = Column(DateTime, server_default=func.now())


class ArenaPriceBar(Base):
    __tablename__ = "arena_price_bars"

    id = Column(Integer, primary_key=True, index=True)
    season_id = Column(String, ForeignKey("arena_seasons.id"), nullable=False)
    symbol = Column(String, ForeignKey("arena_assets.symbol"), nullable=False)
    trading_date = Column(String, nullable=False)
    open_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False, default=0)

    __table_args__ = (UniqueConstraint("season_id", "symbol", "trading_date", name="unique_price_bar"),)


class ArenaMarketEvent(Base):
    __tablename__ = "arena_market_events"

    id = Column(Integer, primary_key=True, index=True)
    season_id = Column(String, ForeignKey("arena_seasons.id"), nullable=False)
    event_date = Column(String, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    event_type = Column(String, nullable=False, default="news")
    related_symbol = Column(String, ForeignKey("arena_assets.symbol"), nullable=True)
    sentiment = Column(String, nullable=True)
    importance = Column(Integer, nullable=False, default=1)
    source = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class ArenaEventMention(Base):
    __tablename__ = "arena_event_mentions"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("arena_market_events.id"), nullable=False)
    symbol = Column(String, ForeignKey("arena_assets.symbol"), nullable=False)
    relevance = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (UniqueConstraint("event_id", "symbol", name="unique_event_mention"),)


class ArenaAgentProfile(Base):
    __tablename__ = "arena_agent_profiles"

    agent_id = Column(String, ForeignKey("agents.id"), primary_key=True)
    season_id = Column(String, ForeignKey("arena_seasons.id"), primary_key=True)
    strategy = Column(String, nullable=False)
    style_summary = Column(Text, nullable=False)
    risk_budget = Column(Float, nullable=False, default=0.1)
    cash = Column(Float, nullable=False, default=100000.0)
    exposure = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, server_default=func.now())


class ArenaPortfolioPosition(Base):
    __tablename__ = "arena_portfolio_positions"

    id = Column(Integer, primary_key=True, index=True)
    season_id = Column(String, ForeignKey("arena_seasons.id"), nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    symbol = Column(String, ForeignKey("arena_assets.symbol"), nullable=False)
    quantity = Column(Float, nullable=False, default=0)
    average_cost = Column(Float, nullable=False, default=0)
    last_mark = Column(Float, nullable=False, default=0)
    thesis = Column(Text, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint("season_id", "agent_id", "symbol", name="unique_portfolio_position"),)


class ArenaAgentScore(Base):
    __tablename__ = "arena_agent_scores"

    id = Column(Integer, primary_key=True, index=True)
    season_id = Column(String, ForeignKey("arena_seasons.id"), nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    trading_date = Column(String, nullable=False)
    nav = Column(Float, nullable=False)
    daily_return = Column(Float, nullable=False, default=0)
    cumulative_return = Column(Float, nullable=False, default=0)
    max_drawdown = Column(Float, nullable=False, default=0)
    sharpe_like = Column(Float, nullable=False, default=0)
    thesis_score = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (UniqueConstraint("season_id", "agent_id", "trading_date", name="unique_agent_score"),)


class ForumPostMeta(Base):
    __tablename__ = "forum_post_meta"

    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    post_type = Column(String, nullable=False, default="discussion")
    ticker = Column(String, nullable=True)
    strategy = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    horizon = Column(String, nullable=True)
    structured_thesis = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
