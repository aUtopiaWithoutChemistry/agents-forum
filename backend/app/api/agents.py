from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import get_db
from app.models.models import Agent, ActivityLog
from app.models.schemas import AgentCreate, AgentResponse

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
