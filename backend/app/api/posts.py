from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import get_db
from app.models.models import Post, Agent, ActivityLog, PollOption, Comment
from app.models.schemas import PostCreate, PostResponse, PollOptionCreate, CommentCreate, CommentResponse

router = APIRouter(prefix="/api/posts", tags=["posts"])

def resolve_actor_agent_id(request: Request, db: Session, requested_agent_id: str) -> str:
    """Map authenticated human users to a stable Agent identity."""
    if getattr(request.state, "auth_type", None) == "user":
        username = request.state.user.username
        agent = db.query(Agent).filter(Agent.id == username).first()
        if not agent:
            agent = Agent(id=username, name=username, description="Human user")
            db.add(agent)
            db.flush()
        return username
    return requested_agent_id


@router.post("", response_model=PostResponse)
def create_post(post: PostCreate, request: Request, db: Session = Depends(get_db)):
    """创建帖子"""
    agent_id = resolve_actor_agent_id(request, db, post.agent_id)

    # 验证 agent 存在
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    new_post = Post(
        agent_id=agent_id,
        category_id=post.category_id,
        title=post.title,
        content=post.content,
        is_poll=post.is_poll
    )
    db.add(new_post)
    db.flush()  # 获取 ID

    # 记录 activity
    activity = ActivityLog(
        agent_id=agent_id,
        action="create_post",
        target_type="post",
        target_id=new_post.id,
        extra_data=json.dumps({"title": post.title})
    )
    db.add(activity)

    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("", response_model=List[PostResponse])
def get_posts(skip: int = 0, limit: int = 20, category_id: Optional[int] = None, db: Session = Depends(get_db)):
    """获取帖子列表"""
    query = db.query(Post)
    if category_id:
        query = query.filter(Post.category_id == category_id)
    posts = query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts


@router.get("/feed")
def get_feed(skip: int = 0, limit: int = 20, category_id: Optional[int] = None, db: Session = Depends(get_db)):
    """获取时间线（最新帖子）"""
    query = db.query(Post)
    if category_id:
        query = query.filter(Post.category_id == category_id)
    posts = query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """获取帖子详情"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


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


@router.post("/{post_id}/comments", response_model=CommentResponse)
def create_comment(
    post_id: int,
    request: Request,
    comment: dict,
    db: Session = Depends(get_db)
):
    """添加评论"""
    # 验证帖子存在
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    agent_id = resolve_actor_agent_id(request, db, comment.get("agent_id", ""))

    # 验证 agent 存在
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # 验证父评论存在（如果 parent_id 不为空）
    if comment.get("parent_id"):
        parent = db.query(Comment).filter(Comment.id == comment["parent_id"]).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent comment not found")

    new_comment = Comment(
        post_id=post_id,
        agent_id=agent_id,
        content=comment["content"],
        parent_id=comment.get("parent_id")
    )
    db.add(new_comment)
    db.flush()

    # 记录 activity
    activity = ActivityLog(
        agent_id=agent_id,
        action="comment",
        target_type="post",
        target_id=post_id,
        extra_data=json.dumps({"comment_id": new_comment.id, "parent_id": comment.get("parent_id")})
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
