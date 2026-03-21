from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import get_db
from app.models.models import Agent, ActivityLog
from app.models.schemas import AgentCreate, AgentResponse, AgentUpdate

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("", response_model=List[AgentResponse])
def get_agents(db: Session = Depends(get_db)):
    """获取所有 agents"""
    agents = db.query(Agent).all()
    return agents


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
        extra_data=json.dumps({"name": agent.name})
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


@router.patch("/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: str, update: AgentUpdate, request: Request, db: Session = Depends(get_db)):
    """更新 agent 信息（仅允许更新自己的名字）"""
    actor_id = resolve_actor_agent_id(request, db, agent_id)
    if actor_id != agent_id:
        raise HTTPException(status_code=403, detail="Cannot update another agent's name")

    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if update.name is not None:
        agent.name = update.name

    activity = ActivityLog(
        agent_id=agent_id,
        action="update_agent",
        target_type="agent",
        target_id=None,
        extra_data=json.dumps({"name": update.name})
    )
    db.add(activity)

    db.commit()
    db.refresh(agent)
    return agent
