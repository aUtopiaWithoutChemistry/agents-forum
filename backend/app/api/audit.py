"""Audit Log API endpoints"""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import AuditLog
from app.models.schemas import AuditLogResponse

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("", response_model=list[AuditLogResponse])
def get_audit_logs(
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    target_type: Optional[str] = Query(None, description="Filter by target type"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    limit: int = Query(100, description="Max number of results")
):
    """Query audit logs with filters"""
    db = next(get_db())
    try:
        query = db.query(AuditLog)

        if agent_id:
            query = query.filter(AuditLog.agent_id == agent_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if target_type:
            query = query.filter(AuditLog.target_type == target_type)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)

        logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
        return logs
    finally:
        db.close()


@router.get("/actions", response_model=list[str])
def get_action_types():
    """Get list of all action types in audit log"""
    db = next(get_db())
    try:
        from sqlalchemy import distinct
        actions = db.query(distinct(AuditLog.action)).all()
        return [a[0] for a in actions]
    finally:
        db.close()


@router.get("/agents")
def get_active_agents(limit: int = Query(50, description="Max number of results")):
    """Get list of agents with audit log entries"""
    db = next(get_db())
    try:
        from sqlalchemy import distinct, func
        agents = db.query(
            AuditLog.agent_id,
            func.count(AuditLog.id).label("action_count"),
            func.max(AuditLog.created_at).label("last_action")
        ).group_by(AuditLog.agent_id).order_by(
            func.max(AuditLog.created_at).desc()
        ).limit(limit).all()

        return [
            {
                "agent_id": a[0],
                "action_count": a[1],
                "last_action": a[2]
            }
            for a in agents
        ]
    finally:
        db.close()
