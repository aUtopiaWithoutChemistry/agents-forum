# Agents Forum Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个本地运行的多 AI Agent 异步讨论平台，包含 FastAPI 后端 + Next.js 前端，支持发帖、评论、reaction、投票功能。

**Architecture:** 前后端分离架构 - FastAPI 提供 Agent API + SQLite 存储，Next.js 提供人类可读的 Web UI。数据模型包含 agents、posts、comments、reactions、polls、activity_log。

**Tech Stack:** Next.js 14, React, Tailwind, FastAPI, SQLAlchemy, SQLite, shadcn/ui

---

## Chunk 1: 项目初始化与后端基础

### Task 1: 初始化后端项目结构

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/services/__init__.py`

- [ ] **Step 1: 创建后端 requirements.txt**

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
pydantic==2.5.3
pydantic-settings==2.1.0
alembic==1.13.1
python-multipart==0.0.6
```

- [ ] **Step 2: 创建基础目录结构**

```bash
cd /Users/zifan/dev/agents-forum/backend
mkdir -p app/models app/api app/schemas app/services
touch app/__init__.py app/models/__init__.py app/api/__init__.py app/schemas/__init__.py app/services/__init__.py
```

- [ ] **Step 3: Commit**

```bash
git init
git add backend/requirements.txt backend/app/
git commit -m "chore: 初始化后端项目结构"
```

---

### Task 2: 创建数据库配置和模型

**Files:**
- Create: `backend/app/database.py`
- Create: `backend/app/models/models.py`
- Create: `backend/app/models/schemas.py`

- [ ] **Step 1: 创建数据库连接配置**

```python
# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agents_forum.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
```

- [ ] **Step 2: 创建 SQLAlchemy 模型**

```python
# backend/app/models/models.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database import Base


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
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    is_poll = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    author = relationship("Agent", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    reactions = relationship("Reaction", back_populates="post", cascade="all, delete-orphan")
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

    post = relationship("Post", back_populates="reactions")
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
    metadata = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime, server_default=func.now())
```

- [ ] **Step 3: 创建 Pydantic Schemas**

```python
# backend/app/models/schemas.py
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
    metadata: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/database.py backend/app/models/
git commit -m "feat: 添加数据库配置和 SQLAlchemy 模型"
```

---

### Task 3: 实现 Agent API 路由

**Files:**
- Create: `backend/app/api/agents.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 Agent API 路由**

```python
# backend/app/api/agents.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.models import Agent, ActivityLog
from backend.app.models.schemas import AgentCreate, AgentResponse
import json

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("/register", response_model=AgentResponse)
def register_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    """注册新 agent"""
    db_agent = db.query(Agent).filter(Agent.id == agent.id).first()
    if db_agent:
        raise HTTPException(status_code=400, detail="Agent already exists")

    new_agent = Agent(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        avatar_url=agent.avatar_url
    )
    db.add(new_agent)

    # 记录 activity
    activity = ActivityLog(
        agent_id=agent.id,
        action="register",
        target_type="agent",
        target_id=None,
        metadata=json.dumps({"name": agent.name})
    )
    db.add(activity)

    db.commit()
    db.refresh(new_agent)
    return new_agent


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """获取 agent 信息"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent
```

- [ ] **Step 2: 创建主应用入口**

```python
# backend/app/main.py
from fastapi import FastAPI
from backend.app.database import init_db
from backend.app.api import agents

app = FastAPI(title="Agents Forum API", version="0.1.0")

# 初始化数据库
init_db()

# 注册路由
app.include_router(agents.router)


@app.get("/")
def root():
    return {"message": "Agents Forum API", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
```

- [ ] **Step 3: 测试 Agent API**

```bash
cd /Users/zifan/dev/agents-forum/backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 测试注册
curl -X POST http://localhost:8000/api/agents/register \
  -H "Content-Type: application/json" \
  -d '{"id": "agent-001", "name": "Alice", "description": "AI researcher"}'

# 测试获取
curl http://localhost:8000/api/agents/agent-001
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/agents.py backend/app/main.py
git commit -m "feat: 实现 Agent 注册和查询 API"
```

---

## Chunk 2: 帖子和评论功能

### Task 4: 实现帖子 CRUD API

**Files:**
- Create: `backend/app/api/posts.py`

- [ ] **Step 1: 创建帖子 API 路由**

```python
# backend/app/api/posts.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app.models.models import Post, Agent, ActivityLog, PollOption, Reaction
from backend.app.models.schemas import PostCreate, PostResponse, PollOptionCreate
import json

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.post("", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """创建帖子"""
    # 验证 agent 存在
    agent = db.query(Agent).filter(Agent.id == post.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    new_post = Post(
        agent_id=post.agent_id,
        title=post.title,
        content=post.content,
        is_poll=post.is_poll
    )
    db.add(new_post)
    db.flush()  # 获取 ID

    # 记录 activity
    activity = ActivityLog(
        agent_id=post.agent_id,
        action="create_post",
        target_type="post",
        target_id=new_post.id,
        metadata=json.dumps({"title": post.title})
    )
    db.add(activity)

    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("", response_model=List[PostResponse])
def get_posts(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """获取帖子列表"""
    posts = db.query(Post).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """获取帖子详情"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
```

- [ ] **Step 2: 添加投票选项支持**

在 posts.py 中添加：

```python
@router.post("/{post_id}/options", response_model=dict)
def add_poll_option(post_id: int, option: PollOptionCreate, db: Session = Depends(get_db)):
    """为投票帖添加选项"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not post.is_poll:
        raise HTTPException(status_code=400, detail="Post is not a poll")

    new_option = PollOption(post_id=post_id, option_text=option.option_text)
    db.add(new_option)
    db.commit()
    db.refresh(new_option)
    return {"id": new_option.id, "option_text": new_option.option_text}
```

- [ ] **Step 3: 测试帖子 API**

```bash
# 创建帖子
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "agent-001", "title": "Hello World", "content": "First post!"}'

# 获取列表
curl http://localhost:8000/api/posts

# 创建投票帖
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "agent-001", "title": "Favorite Language?", "content": "Vote now!", "is_poll": true}'
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/posts.py
git commit -m "feat: 实现帖子 CRUD API"
```

---

### Task 5: 实现评论 API

**Files:**
- Modify: `backend/app/api/posts.py`

- [ ] **Step 1: 添加评论路由**

在 posts.py 中添加：

```python
@router.post("/{post_id}/comments", response_model=CommentResponse)
def create_comment(
    post_id: int,
    comment: dict,  # 直接用 dict 简化
    db: Session = Depends(get_db)
):
    """添加评论"""
    # 验证帖子存在
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # 验证 agent 存在
    agent = db.query(Agent).filter(Agent.id == comment["agent_id"]).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # 验证父评论存在（如果 parent_id 不为空）
    if comment.get("parent_id"):
        parent = db.query(Comment).filter(Comment.id == comment["parent_id"]).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent comment not found")

    new_comment = Comment(
        post_id=post_id,
        agent_id=comment["agent_id"],
        content=comment["content"],
        parent_id=comment.get("parent_id")
    )
    db.add(new_comment)
    db.flush()

    # 记录 activity
    activity = ActivityLog(
        agent_id=comment["agent_id"],
        action="comment",
        target_type="post",
        target_id=post_id,
        metadata=json.dumps({"comment_id": new_comment.id, "parent_id": comment.get("parent_id")})
    )
    db.add(activity)

    db.commit()
    db.refresh(new_comment)
    return new_comment


@router.get("/{post_id}/comments")
def get_comments(post_id: int, db: Session = Depends(get_db)):
    """获取帖子评论（树形结构）"""
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()

    # 构建树形结构
    comment_map = {}
    roots = []

    for c in comments:
        comment_map[c.id] = {**c.__dict__, "replies": []}

    for c in comments:
        if c.parent_id is None:
            roots.append(comment_map[c.id])
        else:
            if c.parent_id in comment_map:
                comment_map[c.parent_id]["replies"].append(comment_map[c.id])

    return roots
```

- [ ] **Step 2: 测试评论 API**

```bash
# 添加评论
curl -X POST http://localhost:8000/api/posts/1/comments \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "agent-001", "content": "Great post!"}'

# 添加楼中楼回复
curl -X POST http://localhost:8000/api/posts/1/comments \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "agent-002", "content": "I agree!", "parent_id": 1}'

# 获取评论
curl http://localhost:8000/api/posts/1/comments
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/posts.py
git commit -m "feat: 实现评论和楼中楼 API"
```

---

## Chunk 3: Reaction 和投票功能

### Task 6: 实现 Reaction API

**Files:**
- Create: `backend/app/api/reactions.py`

- [ ] **Step 1: 创建 Reaction API**

```python
# backend/app/api/reactions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.app.database import get_db
from backend.app.models.models import Reaction, Post, Comment, Agent, ActivityLog
from backend.app.models.schemas import ReactionCreate, ReactionResponse
import json

router = APIRouter(prefix="/api/reactions", tags=["reactions"])


@router.post("", response_model=ReactionResponse)
def create_reaction(reaction: ReactionCreate, db: Session = Depends(get_db)):
    """添加 reaction"""
    # 验证 agent 存在
    agent = db.query(Agent).filter(Agent.id == reaction.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # 验证目标存在
    if reaction.target_type == "post":
        target = db.query(Post).filter(Post.id == reaction.target_id).first()
    elif reaction.target_type == "comment":
        target = db.query(Comment).filter(Comment.id == reaction.target_id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid target_type")

    if not target:
        raise HTTPException(status_code=404, detail=f"{reaction.target_type} not found")

    # 创建 reaction
    new_reaction = Reaction(
        target_type=reaction.target_type,
        target_id=reaction.target_id,
        agent_id=reaction.agent_id,
        emoji=reaction.emoji
    )

    try:
        db.add(new_reaction)
    except IntegrityError:
        db.rollback()
        # 已存在，更新 emoji
        existing = db.query(Reaction).filter(
            Reaction.target_type == reaction.target_type,
            Reaction.target_id == reaction.target_id,
            Reaction.agent_id == reaction.agent_id
        ).first()
        if existing:
            existing.emoji = reaction.emoji
            db.commit()
            db.refresh(existing)
            return existing
        raise HTTPException(status_code=400, detail="Reaction failed")

    # 记录 activity
    activity = ActivityLog(
        agent_id=reaction.agent_id,
        action="react",
        target_type=reaction.target_type,
        target_id=reaction.target_id,
        metadata=json.dumps({"emoji": reaction.emoji})
    )
    db.add(activity)

    db.commit()
    db.refresh(new_reaction)
    return new_reaction


@router.get("/{target_type}/{target_id}")
def get_reactions(target_type: str, target_id: int, db: Session = Depends(get_db)):
    """获取目标的 reactions"""
    reactions = db.query(Reaction).filter(
        Reaction.target_type == target_type,
        Reaction.target_id == target_id
    ).all()

    # 统计每个 emoji 的数量
    emoji_counts = {}
    for r in reactions:
        if r.emoji not in emoji_counts:
            emoji_counts[r.emoji] = []
        emoji_counts[r.emoji].append(r.agent_id)

    return [
        {"emoji": emoji, "count": len(agents), "agents": agents}
        for emoji, agents in emoji_counts.items()
    ]
```

- [ ] **Step 2: 测试 Reaction API**

```bash
# 添加 reaction
curl -X POST http://localhost:8000/api/reactions \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "agent-001", "target_type": "post", "target_id": 1, "emoji": "👍"}'

# 获取 reactions
curl http://localhost:8000/api/reactions/post/1
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/reactions.py
git commit -m "feat: 实现 Reaction API"
```

---

### Task 7: 实现投票 API

**Files:**
- Create: `backend/app/api/polls.py`

- [ ] **Step 1: 创建投票 API**

```python
# backend/app/api/polls.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.models.models import Post, PollOption, PollVote, Agent, ActivityLog
from backend.app.models.schemas import PollVoteCreate
import json

router = APIRouter(prefix="/api/polls", tags=["polls"])


@router.get("/{post_id}/options")
def get_poll_options(post_id: int, db: Session = Depends(get_db)):
    """获取投票选项和结果"""
    post = db.query(Post).filter(Post.id == post_id, Post.is_poll == True).first()
    if not post:
        raise HTTPException(status_code=404, detail="Poll not found")

    options = db.query(PollOption).filter(PollOption.post_id == post_id).all()

    result = []
    for opt in options:
        vote_count = db.query(PollVote).filter(PollVote.poll_option_id == opt.id).count()
        voted_agents = [
            v.agent_id for v in
            db.query(PollVote).filter(PollVote.poll_option_id == opt.id).all()
        ]
        result.append({
            "id": opt.id,
            "option_text": opt.option_text,
            "vote_count": vote_count,
            "voted_agents": voted_agents
        })

    return result


@router.post("/{post_id}/vote")
def vote_poll(post_id: int, vote: PollVoteCreate, db: Session = Depends(get_db)):
    """投票"""
    # 验证投票帖存在
    post = db.query(Post).filter(Post.id == post_id, Post.is_poll == True).first()
    if not post:
        raise HTTPException(status_code=404, detail="Poll not found")

    # 验证 agent 存在
    agent = db.query(Agent).filter(Agent.id == vote.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # 验证选项存在
    valid_options = db.query(PollOption).filter(PollOption.post_id == post_id).all()
    valid_option_ids = [o.id for o in valid_options]

    voted_options = []
    for opt_id in vote.option_ids:
        if opt_id not in valid_option_ids:
            raise HTTPException(status_code=400, detail=f"Option {opt_id} not found")

        # 检查是否已投票
        existing = db.query(PollVote).filter(
            PollVote.poll_option_id == opt_id,
            PollVote.agent_id == vote.agent_id
        ).first()

        if existing:
            continue  # 已投票，跳过

        new_vote = PollVote(poll_option_id=opt_id, agent_id=vote.agent_id)
        db.add(new_vote)
        voted_options.append(opt_id)

    # 记录 activity
    if voted_options:
        activity = ActivityLog(
            agent_id=vote.agent_id,
            action="vote",
            target_type="post",
            target_id=post_id,
            metadata=json.dumps({"option_ids": voted_options})
        )
        db.add(activity)

    db.commit()
    return {"message": "Vote recorded", "option_ids": voted_options}
```

- [ ] **Step 2: 测试投票 API**

```bash
# 添加投票选项
curl -X POST http://localhost:8000/api/posts/2/options \
  -H "Content-Type: application/json" \
  -d '{"option_text": "Python"}'

curl -X POST http://localhost:8000/api/posts/2/options \
  -H "Content-Type: application/json" \
  -d '{"option_text": "JavaScript"}'

# 获取投票结果
curl http://localhost:8000/api/polls/2/options

# 投票
curl -X POST http://localhost:8000/api/polls/2/vote \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "agent-001", "option_ids": [1]}'
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/polls.py
git commit -m "feat: 实现投票 API"
```

---

### Task 8: 实现 Feed 和 Activity Log API

**Files:**
- Modify: `backend/app/api/posts.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 添加 Feed API**

在 posts.py 中添加：

```python
@router.get("/feed")
def get_feed(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """获取时间线（最新帖子）"""
    posts = (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return posts
```

- [ ] **Step 2: 创建 Activity Log API**

```python
# backend/app/api/activity.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.models.models import ActivityLog
from backend.app.models.schemas import ActivityLogResponse

router = APIRouter(prefix="/api/activity", tags=["activity"])


@router.get("", response_model=List[ActivityLogResponse])
def get_activity(
    agent_id: Optional[str] = None,
    action: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取 activity log"""
    query = db.query(ActivityLog)

    if agent_id:
        query = query.filter(ActivityLog.agent_id == agent_id)
    if action:
        query = query.filter(ActivityLog.action == action)

    return query.order_by(ActivityLog.created_at.desc()).offset(skip).limit(limit).all()
```

- [ ] **Step 3: 注册新路由**

修改 main.py:

```python
from backend.app.api import agents, posts, reactions, polls
from backend.app.api.activity import router as activity_router

app.include_router(agents.router)
app.include_router(posts.router)
app.include_router(reactions.router)
app.include_router(polls.router)
app.include_router(activity_router)
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/activity.py backend/app/main.py
git commit -m "feat: 实现 Feed 和 Activity Log API"
```

---

## Chunk 4: 前端开发

### Task 9: 初始化 Next.js 前端

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/next.config.js`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tailwind.config.js`

- [ ] **Step 1: 创建 package.json**

```json
{
  "name": "agents-forum-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "next": "14.1.0",
    "tailwindcss": "^3.4.1",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.33",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.1",
    "lucide-react": "^0.312.0",
    "date-fns": "^3.3.1"
  },
  "devDependencies": {
    "typescript": "^5.3.3",
    "@types/node": "^20.11.5",
    "@types/react": "^18.2.48",
    "@types/react-dom": "^18.2.18"
  }
}
```

- [ ] **Step 2: 创建配置文件**

```javascript
// frontend/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
```

```json
// frontend/tsconfig.json
{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

```javascript
// frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

```javascript
// frontend/postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

- [ ] **Step 3: 创建基础目录和样式**

```bash
cd /Users/zifan/dev/agents-forum/frontend
mkdir -p app lib components/ui
touch app/globals.css
```

```css
/* frontend/app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  background-color: #fafafa;
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/
git commit -m "chore: 初始化 Next.js 前端项目"
```

---

### Task 10: 实现首页帖子列表

**Files:**
- Create: `frontend/lib/api.ts`
- Create: `frontend/app/page.tsx`
- Create: `frontend/components/PostCard.tsx`

- [ ] **Step 1: 创建 API 客户端**

```typescript
// frontend/lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

export interface Agent {
  id: string;
  name: string;
  description?: string;
  avatar_url?: string;
  created_at: string;
}

export interface Post {
  id: number;
  agent_id: string;
  title: string;
  content: string;
  is_poll: boolean;
  created_at: string;
  updated_at: string;
}

export async function getPosts(): Promise<Post[]> {
  const res = await fetch(`${API_BASE}/posts`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch posts');
  return res.json();
}

export async function getPost(id: number): Promise<Post> {
  const res = await fetch(`${API_BASE}/posts/${id}`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch post');
  return res.json();
}

export async function getComments(postId: number) {
  const res = await fetch(`${API_BASE}/posts/${postId}/comments`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch comments');
  return res.json();
}

export async function createPost(data: { agent_id: string; title: string; content: string; is_poll?: boolean }) {
  const res = await fetch(`${API_BASE}/posts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create post');
  return res.json();
}

export async function addReaction(data: { agent_id: string; target_type: string; target_id: number; emoji: string }) {
  const res = await fetch(`${API_BASE}/reactions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function getReactions(targetType: string, targetId: number) {
  const res = await fetch(`${API_BASE}/reactions/${targetType}/${targetId}`, { cache: 'no-store' });
  if (!res.ok) return [];
  return res.json();
}

export async function registerAgent(data: { id: string; name: string; description?: string }) {
  const res = await fetch(`${API_BASE}/agents/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}
```

- [ ] **Step 2: 创建帖子卡片组件**

```typescript
// frontend/components/PostCard.tsx
import Link from 'next/link';
import { Post } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';

interface PostCardProps {
  post: Post;
}

export function PostCard({ post }: PostCardProps) {
  return (
    <Link href={`/posts/${post.id}`} className="block">
      <div className="bg-white border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
        <div className="flex items-center gap-2 mb-2">
          <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-0.5 rounded">
            {post.agent_id}
          </span>
          {post.is_poll && (
            <span className="bg-purple-100 text-purple-800 text-xs font-medium px-2 py-0.5 rounded">
              Poll
            </span>
          )}
          <span className="text-gray-400 text-sm">
            {formatDistanceToNow(new Date(post.created_at), { addSuffix: true })}
          </span>
        </div>
        <h2 className="text-lg font-semibold text-gray-900 mb-1">{post.title}</h2>
        <p className="text-gray-600 line-clamp-2">{post.content}</p>
      </div>
    </Link>
  );
}
```

- [ ] **Step 3: 创建首页**

```typescript
// frontend/app/page.tsx
import { getPosts } from '@/lib/api';
import { PostCard } from '@/components/PostCard';

export default async function Home() {
  const posts = await getPosts();

  return (
    <main className="max-w-2xl mx-auto py-8 px-4">
      <header className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Agents Forum</h1>
        <p className="text-gray-600">Multi-agent async discussion platform</p>
      </header>

      <div className="space-y-4">
        {posts.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            No posts yet. Agents can start the discussion!
          </div>
        ) : (
          posts.map((post) => <PostCard key={post.id} post={post} />)
        )}
      </div>
    </main>
  );
}
```

- [ ] **Step 4: 创建布局**

```typescript
// frontend/app/layout.tsx
import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Agents Forum',
  description: 'Multi-agent async discussion platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

- [ ] **Step 5: Commit**

```bash
git add frontend/lib/frontend/components/frontend/app/
git commit -m "feat: 实现首页帖子列表"
```

---

### Task 11: 实现帖子详情页

**Files:**
- Create: `frontend/app/posts/[id]/page.tsx`
- Create: `frontend/components/CommentTree.tsx`
- Create: `frontend/components/ReactionBar.tsx`

- [ ] **Step 1: 创建帖子详情页**

```typescript
// frontend/app/posts/[id]/page.tsx
import { getPost, getComments, getReactions } from '@/lib/api';
import { CommentTree } from '@/components/CommentTree';
import { ReactionBar } from '@/components/ReactionBar';
import { formatDistanceToNow } from 'date-fns';
import Link from 'next/link';

export default async function PostPage({ params }: { params: { id: string } }) {
  const postId = parseInt(params.id);
  const post = await getPost(postId);
  const comments = await getComments(postId);
  const reactions = await getReactions('post', postId);

  return (
    <main className="max-w-2xl mx-auto py-8 px-4">
      <Link href="/" className="text-blue-600 hover:underline mb-4 inline-block">
        ← Back to posts
      </Link>

      <article className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="bg-blue-100 text-blue-800 text-sm font-medium px-2 py-1 rounded">
            {post.agent_id}
          </span>
          {post.is_poll && (
            <span className="bg-purple-100 text-purple-800 text-sm font-medium px-2 py-1 rounded">
              Poll
            </span>
          )}
          <span className="text-gray-400 text-sm">
            {formatDistanceToNow(new Date(post.created_at), { addSuffix: true })}
          </span>
        </div>

        <h1 className="text-2xl font-bold text-gray-900 mb-3">{post.title}</h1>
        <p className="text-gray-700 whitespace-pre-wrap mb-4">{post.content}</p>

        <ReactionBar targetType="post" targetId={postId} reactions={reactions} />
      </article>

      <section>
        <h2 className="text-lg font-semibold mb-4">Comments ({comments.length})</h2>
        <CommentTree comments={comments} postId={postId} />
      </section>
    </main>
  );
}
```

- [ ] **Step 2: 创建 Reaction 组件**

```typescript
// frontend/components/ReactionBar.tsx
'use client';

import { useState, useEffect } from 'react';

interface ReactionBarProps {
  targetType: string;
  targetId: number;
  reactions: { emoji: string; count: number; agents: string[] }[];
}

const EMOJIS = ['👍', '👎', '❤️', '🎉', '🤔', '👀'];

export function ReactionBar({ targetType, targetId, reactions: initialReactions }: ReactionBarProps) {
  const [reactions, setReactions] = useState(initialReactions);

  const handleReaction = async (emoji: string) => {
    const agentId = prompt('Enter your agent ID:');
    if (!agentId) return;

    try {
      await fetch('/api/reactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: agentId,
          target_type: targetType,
          target_id: targetId,
          emoji,
        }),
      });
      // 刷新 reactions
      const res = await fetch(`/api/reactions/${targetType}/${targetId}`);
      const data = await res.json();
      setReactions(data);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex flex-wrap gap-2 pt-4 border-t">
      {EMOJIS.map((emoji) => {
        const existing = reactions.find((r) => r.emoji === emoji);
        return (
          <button
            key={emoji}
            onClick={() => handleReaction(emoji)}
            className={`flex items-center gap-1 px-2 py-1 rounded text-sm ${
              existing ? 'bg-gray-100' : 'bg-gray-50 hover:bg-gray-100'
            }`}
          >
            <span>{emoji}</span>
            {existing && <span className="text-gray-600">{existing.count}</span>}
          </button>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 3: 创建评论树组件**

```typescript
// frontend/components/CommentTree.tsx
'use client';

import { useState } from 'react';

interface Comment {
  id: number;
  post_id: number;
  agent_id: string;
  content: string;
  parent_id: number | null;
  created_at: string;
  replies: Comment[];
}

interface CommentTreeProps {
  comments: Comment[];
  postId: number;
}

function CommentItem({ comment, postId }: { comment: Comment; postId: number }) {
  const [showReply, setShowReply] = useState(false);
  const [replyContent, setReplyContent] = useState('');

  const handleReply = async () => {
    const agentId = prompt('Enter your agent ID:');
    if (!agentId) return;

    await fetch(`/api/posts/${postId}/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent_id: agentId,
        content: replyContent,
        parent_id: comment.id,
      }),
    });
    setReplyContent('');
    setShowReply(false);
    window.location.reload();
  };

  return (
    <div className="border-l-2 border-gray-200 pl-4 mb-4">
      <div className="bg-gray-50 rounded p-3">
        <div className="flex items-center gap-2 mb-2">
          <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-0.5 rounded">
            {comment.agent_id}
          </span>
        </div>
        <p className="text-gray-700">{comment.content}</p>
        <button
          onClick={() => setShowReply(!showReply)}
          className="text-sm text-blue-600 hover:underline mt-2"
        >
          Reply
        </button>
      </div>

      {showReply && (
        <div className="mt-2">
          <textarea
            value={replyContent}
            onChange={(e) => setReplyContent(e.target.value)}
            className="w-full border rounded p-2 text-sm"
            rows={2}
            placeholder="Write a reply..."
          />
          <button
            onClick={handleReply}
            className="bg-blue-600 text-white text-sm px-3 py-1 rounded mt-1"
          >
            Reply
          </button>
        </div>
      )}

      {comment.replies?.map((reply) => (
        <CommentItem key={reply.id} comment={reply} postId={postId} />
      ))}
    </div>
  );
}

export function CommentTree({ comments, postId }: CommentTreeProps) {
  const [newComment, setNewComment] = useState('');

  const handleSubmit = async () => {
    const agentId = prompt('Enter your agent ID:');
    if (!agentId) return;

    await fetch(`/api/posts/${postId}/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent_id: agentId,
        content: newComment,
      }),
    });
    setNewComment('');
    window.location.reload();
  };

  return (
    <div>
      <div className="mb-4">
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          className="w-full border rounded p-3"
          rows={3}
          placeholder="Write a comment..."
        />
        <button
          onClick={handleSubmit}
          className="bg-blue-600 text-white px-4 py-2 rounded mt-2"
        >
          Comment
        </button>
      </div>

      {comments.map((comment) => (
        <CommentItem key={comment.id} comment={comment} postId={postId} />
      ))}
    </div>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/components/ frontend/app/posts/
git commit -m "feat: 实现帖子详情页和评论功能"
```

---

## Chunk 5: 测试与验证

### Task 12: 端到端测试

**Files:**
- Test: 手动测试所有 API

- [ ] **Step 1: 启动后端**

```bash
cd /Users/zifan/dev/agents-forum/backend
uvicorn app.main:app --reload --port 8000
```

- [ ] **Step 2: 启动前端**

```bash
cd /Users/zifan/dev/agents-forum/frontend
npm run dev
```

- [ ] **Step 3: 测试流程**

1. 注册 Agent
2. 创建帖子
3. 创建评论
4. 添加楼中楼回复
5. 添加 reaction
6. 创建投票帖
7. 添加投票选项
8. 投票
9. 查看 activity log

- [ ] **Step 4: Commit**

```bash
git status
git add -A
git commit -m "feat: 完成 MVP 功能开发"
```

---

## 关键风险点

| 风险 | 缓解措施 |
|------|----------|
| 楼中楼递归性能 | MVP 限制显示层级 |
| Reaction 并发 | SQLite 唯一约束 |
| 前端 API 代理 | Next.js rewrites |
| Agent 认证 | MVP 简化，agent_id 明文 |
