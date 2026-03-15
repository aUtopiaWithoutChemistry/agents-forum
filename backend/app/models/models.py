import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
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
