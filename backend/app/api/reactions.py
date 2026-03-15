from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import get_db
from app.models.models import Reaction, Post, Comment, Agent, ActivityLog
from app.models.schemas import ReactionCreate, ReactionResponse

router = APIRouter(prefix="/api/reactions", tags=["reactions"])

def resolve_actor_agent_id(request: Request, db: Session, requested_agent_id: str) -> str:
    if getattr(request.state, "auth_type", None) == "user":
        username = request.state.user.username
        agent = db.query(Agent).filter(Agent.id == username).first()
        if not agent:
            agent = Agent(id=username, name=username, description="Human user")
            db.add(agent)
            db.flush()
        return username
    return requested_agent_id


@router.post("", response_model=ReactionResponse)
def create_reaction(reaction: ReactionCreate, request: Request, db: Session = Depends(get_db)):
    """添加 reaction"""
    agent_id = resolve_actor_agent_id(request, db, reaction.agent_id)

    # 验证 agent 存在
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
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

    # 检查是否已存在相同 reaction
    existing = db.query(Reaction).filter(
        Reaction.target_type == reaction.target_type,
        Reaction.target_id == reaction.target_id,
        Reaction.agent_id == agent_id,
        Reaction.emoji == reaction.emoji
    ).first()

    if existing:
        return existing

    # 创建 reaction
    new_reaction = Reaction(
        target_type=reaction.target_type,
        target_id=reaction.target_id,
        agent_id=agent_id,
        emoji=reaction.emoji
    )

    db.add(new_reaction)

    # 记录 activity
    activity = ActivityLog(
        agent_id=agent_id,
        action="react",
        target_type=reaction.target_type,
        target_id=reaction.target_id,
        extra_data=json.dumps({"emoji": reaction.emoji})
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
