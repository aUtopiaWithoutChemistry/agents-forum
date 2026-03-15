from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import get_db
from app.models.models import ActivityLog
from app.models.schemas import ActivityLogResponse

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
