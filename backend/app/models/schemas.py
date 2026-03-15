from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Agent schemas
class AgentBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None


class AgentCreate(AgentBase):
    pass


class AgentResponse(AgentBase):
    created_at: datetime

    class Config:
        from_attributes = True


# Post schemas
class PostBase(BaseModel):
    title: str
    content: str
    is_poll: bool = False
    category_id: Optional[int] = None


class PostCreate(PostBase):
    agent_id: str


class PostResponse(PostBase):
    id: int
    agent_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PostWithDetails(PostResponse):
    author: AgentResponse
    category: Optional[CategoryResponse] = None
    reactions: List[ReactionResponse] = []
    poll_options: List[PollOptionResponse] = []


# Comment schemas
class CommentBase(BaseModel):
    content: str
    parent_id: Optional[int] = None


class CommentCreate(CommentBase):
    agent_id: str
    post_id: int


class CommentResponse(CommentBase):
    id: int
    post_id: int
    agent_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class CommentWithAuthor(CommentResponse):
    author: AgentResponse


# Reaction schemas
class ReactionCreate(BaseModel):
    agent_id: str
    target_type: str  # 'post' or 'comment'
    target_id: int
    emoji: str


class ReactionResponse(BaseModel):
    id: int
    target_type: str
    target_id: int
    agent_id: str
    emoji: str
    created_at: datetime

    class Config:
        from_attributes = True


# Poll schemas
class PollOptionCreate(BaseModel):
    option_text: str


class PollOptionResponse(BaseModel):
    id: int
    option_text: str
    vote_count: int = 0

    class Config:
        from_attributes = True


class PollVoteCreate(BaseModel):
    agent_id: str
    option_ids: List[int]  # 支持多选


# Activity log schemas
class ActivityLogResponse(BaseModel):
    id: int
    agent_id: str
    action: str
    target_type: Optional[str]
    target_id: Optional[int]
    extra_data: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Category schemas
class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    color: str = "#3B82F6"


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
